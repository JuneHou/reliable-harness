#!/usr/bin/env python3
"""Run HarnessFix on AgentDefect cases (plan steps 3 and 4).

For each requirement-list environment of SelfHeal's AgentDefect test path (built once, as
test_repairs.main does, into HarnessFix's own test_envs folder), and for each selected case and
rerun, one rerun at a time on the machine:
  1. a fresh copy of methods/HarnessFix (with the two modes) in <rerun>/harnessfix, its .venv linked,
     the case's program as task_agent/agentdefect_program, and the case's one test as the training,
     validation and test split (departure 1), with the code intent as the task text;
  2. HarnessFix's own pipeline, run_pipeline_agentdefect.py, with its default settings, its agents
     calling the run's ARC model through one relay (relay_log_harnessfix.jsonl);
  3. the final repair: the version the pipeline's own best_version_by_val picks among the promoted
     versions, or no repair with its cause;
  4. the leakage audit, and the final repair executed once through run_test (<rerun>/test/).

Existing scripts are imported, never edited.
"""
import argparse
import filecmp
import importlib.util
import json
import re
import os
import shutil
import subprocess
import sys
import time

H = "/data/wang/junh/githubs/stochastic-harness"
SH_CODE = os.path.join(H, "AgentDefect", "SelfHeal", "code")
sys.path.insert(0, SH_CODE)
import test_repairs as tr  # noqa: E402
import driver as sh  # noqa: E402  (start_relay, child_env)

ROOT = os.path.join(H, "AgentDefect", "HarnessFix")
CODE = os.path.join(ROOT, "code")
INPUTS = os.path.join(ROOT, "inputs")
HF_SRC = os.path.join(H, "methods", "HarnessFix")
MODE = "agentdefect"
CASE_PY = "/data/wang/junh/python/cpython-3.10.19/bin/python3.10"
RERUNS = 5
tr.TEST_ENVS = os.path.join(ROOT, "test_envs")
tr.ENV_LOGS = os.path.join(ROOT, "test_env_logs")
# HarnessFix's tests keep their own copy of the shared embedding store, so they never append to the
# file SelfHeal's queued AgentDefect runs append to. Identical requests still reuse the saved replies.
EMBED_STORE = os.path.join(ROOT, "embedding_store.jsonl")
tr.EMBED_STORE = EMBED_STORE
# Fixed files HarnessFix's agents write in /tmp (aggregate_results.py:1018 and :1033, the analysis
# prompt's /tmp/result_<id>.json, the modify prompt's /tmp/changes_summary.md). They are removed
# before and after each rerun so no rerun reads another's.
def tmp_files(case):
    return ["/tmp/aggregate_plan.md", "/tmp/changes_summary.md", f"/tmp/result_{case}.json"]


def write_key_files(copy, program_dir):
    """The "Key Files" list of the diagnosis prompt for this case, as GAIA's analysis prompt lists its
    agent's key files (plan, "Resolved by a reference", run record and diagnosis file list item): every
    file of the case's program folder, written into this rerun's copy of the prompt."""
    files = sorted(os.path.relpath(os.path.join(d, f), program_dir)
                   for d, _, fs in os.walk(program_dir) for f in fs)
    role = {"run_buggy.py": "the program. The test imports `run_agent` from it",
            "requirements.txt": "the Python packages the program needs"}
    lines = [f"    - `{f}`: {role.get(f, 'a file in the program folder')}" for f in files]
    cfg = os.path.join(copy, "failure_analysis", f"analysis_config_{MODE}.yaml")
    text = open(cfg, encoding="utf-8").read()
    if text.count("    __KEY_FILES__\n") != 1:
        raise SystemExit(f"{cfg}: the Key Files marker is missing")
    open(cfg, "w", encoding="utf-8").write(text.replace("    __KEY_FILES__\n", "\n".join(lines) + "\n"))


def prepare(rdir, model, case):
    shutil.rmtree(rdir, ignore_errors=True)
    os.makedirs(rdir)
    copy = os.path.join(rdir, "harnessfix")
    shutil.copytree(HF_SRC, copy, ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", "*.pyc"))
    os.symlink(os.path.join(HF_SRC, ".venv"), os.path.join(copy, ".venv"))
    shutil.copytree(os.path.join(INPUTS, "programs", case), os.path.join(copy, "task_agent", f"{MODE}_program"))
    write_key_files(copy, os.path.join(INPUTS, "programs", case))
    task = [json.loads(l) for l in open(os.path.join(INPUTS, model, "tasks.jsonl"), encoding="utf-8")
            if json.loads(l)["task_id"] == case]
    if len(task) != 1:
        raise SystemExit(f"{case}: {len(task)} task rows for {model}")
    for split in ("train", "val", "test"):
        d = os.path.join(copy, "data", f"{MODE}_{split}")
        os.makedirs(d)
        open(os.path.join(d, "instance_ids.txt"), "w").write(case + "\n")
        # GAIA's data.jsonl fields (run_analysis.py _load_gaia_data): the intent is the question, and
        # there is no expected answer string, since the case's test decides
        row = {"task_id": case, "question": task[0]["instruction"], "true_answer": "", "level": "n/a",
               "file_name": "", "instruction": task[0]["instruction"]}
        open(os.path.join(d, "data.jsonl"), "w", encoding="utf-8").write(json.dumps(row, ensure_ascii=False) + "\n")
    return copy


def best_version(copy, model, promoted):
    """The pipeline's own best_version_by_val, run in HarnessFix's venv (its module needs dotenv)."""
    code = (f"import json; import run_pipeline_{MODE} as p; "
            f"print(json.dumps(p.best_version_by_val('openai/{model}', {promoted!r})))")
    r = subprocess.run([os.path.join(copy, ".venv", "bin", "python3"), "-c", code], cwd=copy,
                       capture_output=True, text=True, check=True)
    return int(r.stdout.strip().splitlines()[-1])


def final_repair(copy, model):
    results = os.path.join(copy, "failure_analysis", "results")
    promoted = []
    for v in range(1, 10):
        g = os.path.join(results, f"{MODE}_gate_v{v}.json")
        if os.path.exists(g) and json.load(open(g)).get("passed"):
            promoted.append(v)
    return promoted, best_version(copy, model, promoted)


def model_slug(model):
    return model.split("/")[-1].replace("-", "_").lower()   # run_pipeline_agentdefect.py model_slug


def no_repair_cause(copy, exit_code, log_text):
    evals = [d for d in os.listdir(os.path.join(copy, "eval")) if d.startswith(f"{MODE}_results_{MODE}_train_")
             and d.endswith("_original")] if os.path.isdir(os.path.join(copy, "eval")) else []
    for d in evals:
        r = json.load(open(os.path.join(copy, "eval", d, "results.json")))
        if r.get("resolved_ids") and not (r.get("unresolved_ids") or r.get("error_ids") or r.get("empty_patch_ids")):
            return "no failure: the original program passed the training run, so HarnessFix had nothing to repair"
    gates = [f for f in os.listdir(os.path.join(copy, "failure_analysis", "results"))
             if f.startswith(f"{MODE}_gate_v")] if os.path.isdir(os.path.join(copy, "failure_analysis", "results")) else []
    if exit_code != 0:
        # the last Python error line names the cause; CalledProcessError lines only name the failed step
        errors = [l.strip() for l in log_text.splitlines()
                  if re.match(r"^\w+(Error|Exception): ", l.strip()) and not l.strip().startswith("subprocess.CalledProcessError")]
        steps = [l.strip() for l in log_text.splitlines() if re.match(r"^\[pipeline_\w+\] Step", l.strip())]
        where = steps[-1].split("] ", 1)[-1] if steps else "unknown step"
        what = errors[-1][:300] if errors else ([l for l in log_text.splitlines() if l.strip()][-1:] or [""])[0][:300]
        return f"pipeline exit {exit_code} at {where}: {what}"
    if gates:
        return f"no candidate promoted in {len(gates)} gate check(s)"
    return "no candidate reached the validation gate"


def changed_files(base, cand):
    """Files that differ between two folders, new and deleted ones included (caches left out)."""
    def files_of(root):
        out = set()
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in (".git", "__pycache__")]
            out.update(os.path.relpath(os.path.join(d, f), root) for f in fs if not f.endswith(".pyc"))
        return out
    a, b = files_of(base), files_of(cand)
    return sorted(x for x in a | b if x not in a or x not in b
                  or not filecmp.cmp(os.path.join(base, x), os.path.join(cand, x), shallow=False))


def pipeline_end(rdir, case, model, exit_code, promoted, log_text):
    """How the pipeline ended, for the final record (plan step 3c, record only). With one test per case
    (departure 1), an accepted version that passes the training run leaves no failure to analyze in the
    next round, and the released loop then stops on the missing analysis file (run_pipeline_gaia.py has
    the same step_train_failure_analysis and step_aggregate)."""
    if exit_code == 0:
        return "completed"
    v = promoted[-1] if promoted else 0
    run = f"{MODE}_train_{model_slug(model)}_" + (f"program_enhanced_v{v}" if v else "original")
    rec = os.path.join(rdir, "test_runs", run, case, "test_record.json")
    passed = os.path.exists(rec) and json.load(open(rec)).get("passed") is True
    if passed and "FileNotFoundError" in log_text and f"{run}_analysis.jsonl" in log_text:
        which = f"after acceptance: version {v}" if v else "in round one: the original program"
        return (f"stopped {which} passed the training run, so no failure was left to analyze, and the released "
                "pipeline has no exit for that case")
    return "stopped with an error, see pipeline.log"


# Jun "only one env at a time keep. all finish, all deleted": what a case program downloads while it runs is
# deleted when the case's reruns end. ~/.cache/llama_models, where 78564699's program stores its 6.9 GB model,
# points to /data/wang/junh/caches/llama_models, so the download never lands in the home folder.
CASE_CACHES = ["/data/wang/junh/caches/llama_models"]


def clean_case_caches(case):
    for d in CASE_CACHES:
        if os.path.isdir(d) and os.listdir(d):
            for name in os.listdir(d):
                path = os.path.join(d, name)
                shutil.rmtree(path) if os.path.isdir(path) and not os.path.islink(path) else os.remove(path)
            print("case", case, "downloads deleted from", d, flush=True)


def run_one(model, case, k, py, env_rec_path, env_rec):
    rdir = os.path.join(ROOT, model, case, f"rerun_{k}")
    if os.path.exists(os.path.join(rdir, "final_record.json")):
        return "done before"
    copy = prepare(rdir, model, case)
    for f in tmp_files(case):
        if os.path.exists(f):
            os.remove(f)
    log = os.path.join(rdir, "relay_log_harnessfix.jsonl")
    proc, port = sh.start_relay(model, log)
    env = sh.child_env(port)
    env.update({"HF_CASE": case, "HF_RUNS_DIR": os.path.join(rdir, "test_runs"), "HF_ENV_PY": py,
                "HF_ENV_REC": env_rec_path, "HF_CASE_PYTHON": CASE_PY,
                "HF_EXEC_CASE": os.path.join(CODE, "exec_case.py"), "HF_EMBED_STORE": EMBED_STORE,
                # plan departure 4 (e): every agent command runs in a sandbox that shows only this copy and a
                # private /tmp (minisweagent/environments/local.py _sandboxed)
                "HF_SANDBOX_DIR": copy, "HF_SANDBOX_TMP": os.path.join(rdir, "agent_tmp")})
    t0 = time.time()
    try:
        with open(os.path.join(rdir, "pipeline.log"), "w") as out:
            r = subprocess.run([os.path.join(copy, ".venv", "bin", "python3"), f"run_pipeline_{MODE}.py",
                                "--model", f"openai/{model}", "--analysis-model", f"openai/{model}", "--workers", "1"],
                               cwd=copy, env=env, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    finally:
        proc.terminate()
        proc.wait()
    seconds = round(time.time() - t0, 1)
    for f in tmp_files(case):
        if os.path.exists(f):
            shutil.copy(f, os.path.join(rdir, "tmp_" + os.path.basename(f)))
            os.remove(f)
    log_text = open(os.path.join(rdir, "pipeline.log"), errors="replace").read()
    promoted, best = final_repair(copy, model)
    rec = {"method": "HarnessFix", "case": case, "model": model, "rerun": k, "pipeline_exit": r.returncode,
           "pipeline_seconds": seconds, "promoted_versions": promoted, "best_version": best,
           "pipeline_end": pipeline_end(rdir, case, model, r.returncode, promoted, log_text),
           "relay_log": os.path.basename(log)}
    if best > 0:
        code = open(os.path.join(copy, "task_agent", f"enhanced_{MODE}_{model_slug(model)}_v{best}", "run_buggy.py"),
                    encoding="utf-8").read()
        open(os.path.join(rdir, "final_repair.py"), "w", encoding="utf-8").write(code)
        rec.update({"repair": True, "cause": None})
    else:
        rec.update({"repair": False, "cause": no_repair_cause(copy, r.returncode, log_text)})
    subprocess.run([sys.executable, os.path.join(CODE, "audit_leakage.py"), rdir], check=True)
    rec["leakage_clean"] = json.load(open(os.path.join(rdir, "leakage_audit.json")))["clean"]
    # the original program folder must still equal the input program (plan step 3b)
    orig_changed = changed_files(os.path.join(INPUTS, "programs", case), os.path.join(copy, "task_agent", f"{MODE}_program"))
    rec.update({"original_folder_unchanged": not orig_changed, "original_folder_changed_files": orig_changed})
    if rec["repair"]:
        rec["test"] = tr.run_test(os.path.join(rdir, "test"), model, case, code, py, env_rec,
                                  {"kind": "repair", "rerun": k, "method": "HarnessFix"})
    json.dump(rec, open(os.path.join(rdir, "final_record.json"), "w"), indent=1)
    return (f"{'repair ' + rec['test'] if rec['repair'] else 'no repair: ' + rec['cause']} | leakage clean {rec['leakage_clean']}"
            f" | original folder unchanged {rec['original_folder_unchanged']} | {seconds} s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--reruns", nargs="*", type=int, default=list(range(1, RERUNS + 1)))
    a = ap.parse_args()
    os.makedirs(tr.TEST_ENVS, exist_ok=True)
    os.makedirs(tr.ENV_LOGS, exist_ok=True)
    if not os.path.exists(EMBED_STORE):
        shutil.copy(os.path.join(H, "AgentDefect", "embedding_store.jsonl"), EMBED_STORE)
    for env_name, n, cases, pins in tr.environments():
        todo = [(c, k) for c in sorted(cases) if not a.cases or c in a.cases for k in a.reruns
                if not os.path.exists(os.path.join(ROOT, a.model, c, f"rerun_{k}", "final_record.json"))]
        if not todo:
            continue
        print("env", env_name, "building", time.strftime("%H:%M:%S"), flush=True)
        try:
            env_rec, py = tr.build_env(env_name, n, cases, pins)
            env_rec_path = os.path.join(tr.ENV_LOGS, f"list_{env_name}_record.json")
            json.dump(env_rec, open(env_rec_path, "w"), indent=1, default=str)
            for i, (c, k) in enumerate(todo):
                print("env", env_name, c, a.model, k, run_one(a.model, c, k, py, env_rec_path, env_rec),
                      time.strftime("%H:%M:%S"), flush=True)
                if i == len(todo) - 1 or todo[i + 1][0] != c:
                    clean_case_caches(c)
        finally:
            shutil.rmtree(os.path.join(tr.TEST_ENVS, f"list_{env_name}"), ignore_errors=True)
            print("env", env_name, "environment deleted", flush=True)


if __name__ == "__main__":
    main()
