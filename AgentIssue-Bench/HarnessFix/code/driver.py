#!/usr/bin/env python3
"""Run HarnessFix on AgentIssue-Bench issues (plan steps 3 and 4).

For each selected issue and rerun, one rerun at a time on the machine:
  1. a fresh copy of methods/HarnessFix (with the two modes) in <rerun>/harnessfix, its .venv linked,
     the issue's buggy tree (AgentIssue-Bench/SelfHeal/inputs/issues/<tag>/repo, never the developer
     patch or metadata) as task_agent/agentissue_program, and the issue's one test as the training,
     validation and test split (departure 1), with the code intent SelfHeal received as the task text
     (run_agent_adapted.py:360 uses row['intent']);
  2. HarnessFix's own pipeline, run_pipeline_agentissue.py (the AgentIssue-Bench mode, built on HarnessFix's
     SWE-Bench mode), with its default settings, its agents calling the run's ARC model through one relay;
  3. the final repair: the version the pipeline's best_version_by_val picks among the promoted
     versions, as a patch against the buggy tree, or no repair with its cause;
  4. the leakage audit, the check that the original program folder equals the input tree, and the final
     repair executed once through run_test's shipped evaluator path.
Every patch is taken against the input tree. The repository copies are deleted after the rerun; the patch
of every version is kept.

The issue's image is pulled once per issue and tagged stochastic-harness/hf-agentissue:<tag>, so
SelfHeal's queue removing its own tag never removes the image a HarnessFix rerun is using.
"""
import argparse
import csv
import importlib.util
import json
import re
import os
import shutil
import subprocess
import sys
import time

H = "/data/wang/junh/githubs/stochastic-harness"
AIC = os.path.join(H, "AgentIssue-Bench", "SelfHeal", "code")
ADC = os.path.join(H, "AgentDefect", "SelfHeal", "code")
sys.path.insert(0, ADC)
import driver as sh  # noqa: E402  (start_relay, child_env)

ROOT = os.path.join(H, "AgentIssue-Bench", "HarnessFix")
CODE = os.path.join(ROOT, "code")
ISSUES = os.path.join(H, "AgentIssue-Bench", "SelfHeal", "inputs", "issues")
HF_SRC = os.path.join(H, "methods", "HarnessFix")
MODE = "agentissue"
CASE_PY = "/data/wang/junh/python/cpython-3.10.19/bin/python3.10"
EMBED_STORE = os.path.join(ROOT, "embedding_store.jsonl")
AUDIT = os.path.join(H, "AgentDefect", "HarnessFix", "code", "audit_leakage.py")
RERUNS = 5


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ex = load("hf_agentissue_exec", os.path.join(CODE, "exec_case.py"))
tr = load("aic_test_repairs", os.path.join(AIC, "test_repairs.py"))
tr.adt.EMBED_STORE = EMBED_STORE


def tmp_files(tag):
    return ["/tmp/aggregate_plan.md", "/tmp/changes_summary.md", f"/tmp/result_{tag}.json"]


def intents(model):
    path = os.path.join(H, "AgentIssue-Bench", "SelfHeal", model, "rules", "test_descriptions_with_intent.csv")
    return {r["id"]: r["intent"] for r in csv.DictReader(open(path, encoding="utf-8"))}


def prepare(rdir, model, tag):
    shutil.rmtree(rdir, ignore_errors=True)
    os.makedirs(rdir)
    copy = os.path.join(rdir, "harnessfix")
    shutil.copytree(HF_SRC, copy, ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", "*.pyc"))
    os.symlink(os.path.join(HF_SRC, ".venv"), os.path.join(copy, ".venv"))
    shutil.copytree(os.path.join(ISSUES, tag, "repo"), os.path.join(copy, "task_agent", f"{MODE}_program"), symlinks=True)
    task = {"task_id": tag, "instruction": intents(model)[tag]}
    for split in ("train", "val", "test"):
        d = os.path.join(copy, "data", f"{MODE}_{split}")
        os.makedirs(d)
        open(os.path.join(d, "instance_ids.txt"), "w").write(tag + "\n")
        open(os.path.join(d, "data.jsonl"), "w", encoding="utf-8").write(json.dumps(task, ensure_ascii=False) + "\n")
    return copy


def final_repair(copy, model):
    results = os.path.join(copy, "failure_analysis", "results")
    promoted = [v for v in range(1, 10) if os.path.exists(os.path.join(results, f"promotion_{MODE}_v{v}.json"))
                and json.load(open(os.path.join(results, f"promotion_{MODE}_v{v}.json"))).get("promoted")]
    code = (f"import json; import run_pipeline_{MODE} as p; "
            f"print(json.dumps(p.best_version_by_val('openai/{model}', {promoted!r})))")
    r = subprocess.run([os.path.join(copy, ".venv", "bin", "python3"), "-c", code], cwd=copy,
                       capture_output=True, text=True, check=True)
    return promoted, int(r.stdout.strip().splitlines()[-1])


def no_repair_cause(copy, exit_code, log_text):
    ev = os.path.join(copy, "eval")
    for d in (os.listdir(ev) if os.path.isdir(ev) else []):
        if d.startswith(f"results_{MODE}_train_") and d.endswith("_original"):
            r = json.load(open(os.path.join(ev, d, "results.json")))
            if r.get("resolved_ids") and not (r.get("unresolved_ids") or r.get("error_ids") or r.get("empty_patch_ids")):
                return "no failure: the original code passed the training run, so HarnessFix had nothing to repair"
    res = os.path.join(copy, "failure_analysis", "results")
    gates = [f for f in os.listdir(res) if f.startswith(f"promotion_{MODE}_v")] if os.path.isdir(res) else []
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


def pipeline_end(copy, exit_code, promoted, log_text):
    """How the pipeline ended, for the final record (plan step 3c, record only), read from the lines the
    released SWE-Bench pipeline prints (run_pipeline_swe.py: "Stopping: N consecutive candidates were not
    promoted.", "Finished iterations.") or, on a non-zero exit, from the last error and step in its log."""
    if exit_code == 0:
        m = re.findall(r"Stopping: (\d+) consecutive candidates were not promoted", log_text)
        if m:
            return f"stopped after {m[-1]} rejections in a row (released rule, --max-promotion-failures)"
        return "completed" + ("" if promoted else ", no version accepted")
    cause = no_repair_cause(copy, exit_code, log_text)
    if cause.startswith("no failure"):
        return ("stopped in round one: the original code passed the training run, so no failure was left to "
                "analyze, and the released pipeline has no exit for that case")
    if promoted and "FileNotFoundError" in log_text and "_analysis.jsonl" in log_text:
        return (f"stopped after acceptance: version {promoted[-1]} passed the training run, so no failure was "
                "left to analyze, and the released pipeline has no exit for that case")
    return "stopped with an error, " + cause


def run_one(model, tag, k, image):
    rdir = os.path.join(ROOT, model, tag, f"rerun_{k}")
    if os.path.exists(os.path.join(rdir, "final_record.json")):
        return "done before"
    copy = prepare(rdir, model, tag)
    # every patch is taken against the input tree, which no agent of the rerun can reach
    base_tree = os.path.join(ISSUES, tag, "repo")
    for f in tmp_files(tag):
        if os.path.exists(f):
            os.remove(f)
    log = os.path.join(rdir, "relay_log_harnessfix.jsonl")
    proc, port = sh.start_relay(model, log)
    env = sh.child_env(port)
    env.update({"HF_CASE": tag, "HF_IMAGE": image, "HF_RUNS_DIR": os.path.join(rdir, "test_runs"),
                "HF_BASE_TREE": base_tree, "HF_CASE_PYTHON": CASE_PY, "HF_EMBED_STORE": EMBED_STORE,
                "HF_EXEC_CASE": os.path.join(CODE, "exec_case.py"),
                # plan departure 4 (e): every agent command runs in a sandbox that shows only this copy and a
                # private /tmp (minisweagent/environments/local.py _sandboxed)
                "HF_SANDBOX_DIR": copy, "HF_SANDBOX_TMP": os.path.join(rdir, "agent_tmp"),
                # the repository's top-level folders and files are the editable paths (operator_registry.py)
                "HF_AGENTISSUE_TREE": os.path.join(copy, "task_agent", f"{MODE}_program")})
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
    for f in tmp_files(tag):
        if os.path.exists(f):
            shutil.copy(f, os.path.join(rdir, "tmp_" + os.path.basename(f)))
            os.remove(f)
    log_text = open(os.path.join(rdir, "pipeline.log"), errors="replace").read()
    promoted, best = final_repair(copy, model)
    versions = {}
    for d in sorted(os.listdir(os.path.join(copy, "task_agent"))):
        if d.startswith(f"enhanced_{MODE}_v"):
            patch, changed = ex.tree_patch(base_tree, os.path.join(copy, "task_agent", d))
            open(os.path.join(rdir, f"{d}.patch"), "w", encoding="utf-8", errors="surrogateescape").write(patch)
            versions[d] = changed
    # the original program folder must still equal the input tree (plan step 3b)
    orig_patch, orig_changed = ex.tree_patch(base_tree, os.path.join(copy, "task_agent", f"{MODE}_program"))
    if orig_changed:
        open(os.path.join(rdir, "original_folder_changed.diff"), "w", encoding="utf-8", errors="surrogateescape").write(orig_patch)
    rec = {"method": "HarnessFix", "tag": tag, "model": model, "rerun": k, "image": image,
           "original_folder_unchanged": not orig_changed, "original_folder_changed_files": orig_changed,
           "pipeline_exit": r.returncode, "pipeline_seconds": seconds, "promoted_versions": promoted,
           "best_version": best, "pipeline_end": pipeline_end(copy, r.returncode, promoted, log_text),
           "version_changed_files": versions, "relay_log": os.path.basename(log)}
    if best > 0:
        patch = open(os.path.join(rdir, f"enhanced_{MODE}_v{best}.patch"), encoding="utf-8", errors="surrogateescape").read()
        open(os.path.join(rdir, "final_repair.patch"), "w", encoding="utf-8", errors="surrogateescape").write(patch)
        rec.update({"repair": True, "cause": None})
    else:
        rec.update({"repair": False, "cause": no_repair_cause(copy, r.returncode, log_text)})
    subprocess.run([sys.executable, AUDIT, rdir], check=True)
    rec["leakage_clean"] = json.load(open(os.path.join(rdir, "leakage_audit.json")))["clean"]
    if rec["repair"]:
        t = tr.run_eval(tag, image, model, os.path.join(rdir, "test"), "shipped", patch,
                        extra={"kind": "repair", "rerun": k, "method": "HarnessFix"})
        rec["test"] = "passed" if t["passed"] else "failed"
    # the repository copies are large; every version's patch is kept above
    for d in os.listdir(os.path.join(copy, "task_agent")):
        if d == f"{MODE}_program" or d.startswith(f"enhanced_{MODE}_v"):
            shutil.rmtree(os.path.join(copy, "task_agent", d), ignore_errors=True)
    json.dump(rec, open(os.path.join(rdir, "final_record.json"), "w"), indent=1)
    return (f"{'repair ' + rec['test'] if rec['repair'] else 'no repair: ' + rec['cause']} | leakage clean {rec['leakage_clean']}"
            f" | original folder unchanged {rec['original_folder_unchanged']} | {seconds} s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--reruns", nargs="*", type=int, default=list(range(1, RERUNS + 1)))
    a = ap.parse_args()
    if not os.path.exists(EMBED_STORE):
        open(EMBED_STORE, "a").close()
    tags = a.tags or sorted(os.listdir(ISSUES))
    for tag in tags:
        todo = [k for k in a.reruns if not os.path.exists(os.path.join(ROOT, a.model, tag, f"rerun_{k}", "final_record.json"))]
        if not todo:
            continue
        src = tr.image_of(tag)
        image = f"stochastic-harness/hf-agentissue:{tag}"
        # Jun "only one env at a time keep. all finish, all deleted": an image this driver pulls is deleted when
        # the issue's reruns end; an image already on the machine (a locally rebuilt amd64 image, or one another
        # run is using) is left as it was
        pulled = False
        if src.startswith("alfin06/"):
            had = subprocess.run(["docker", "image", "inspect", src], capture_output=True).returncode == 0
            subprocess.run(["docker", "pull", "-q", src], check=True, capture_output=True)
            pulled = not had
        subprocess.run(["docker", "tag", src, image], check=True)
        try:
            for k in todo:
                print(tag, a.model, k, run_one(a.model, tag, k, image), time.strftime("%H:%M:%S"), flush=True)
        finally:
            subprocess.run(["docker", "rmi", image], capture_output=True)
            print(tag, "image tag removed", flush=True)
            if pulled:
                users = subprocess.run(["docker", "ps", "-a", "-q", "--filter", f"ancestor={src}"],
                                       capture_output=True, text=True).stdout.split()
                if users:
                    print(tag, f"pulled image kept, {len(users)} container(s) use it", flush=True)
                else:
                    r = subprocess.run(["docker", "rmi", src], capture_output=True, text=True)
                    print(tag, "pulled image deleted" if r.returncode == 0 else f"pulled image not deleted: {r.stderr.strip()[:200]}", flush=True)


if __name__ == "__main__":
    main()
