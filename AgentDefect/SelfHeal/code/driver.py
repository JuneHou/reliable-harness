"""Run SelfHeal's own steps on AgentDefect, one ARC model at a time.

  python driver.py rules  --model gpt-oss-120b
      Fix rules (SelfHeal paper 3.1) and the rebuilt code intents (4.2), in
      AgentDefect/SelfHeal/<model>/rules/. SelfHeal's scripts run unchanged.
  python driver.py repair --model gpt-oss-120b --reruns 5 --parallel 5 [--cases ID ...]
      The fix agent and critic loop (3.2) for every case and rerun, each in
      AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/. No AgentDefect program is run.

Every model call goes through relay.py to the ARC model named by --model, and every
request with its real reply is saved in the step's relay log.
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal"
CODE = os.path.join(ROOT, "code")
INPUTS = os.path.join(ROOT, "inputs")
SELFHEAL = "/data/wang/junh/githubs/SelfHeal"
ZIP = os.path.join(SELFHEAL, "AgentDefect.zip")
PY_NEW = "/data/wang/junh/envs/selfheal/bin/python"           # SelfHeal pins, openai 2.14.0
PY_OLD = "/data/wang/junh/envs/selfheal-openai028/bin/python"  # openai 0.28.1 for the two rule scripts
KEY_FILE = "/data/wang/junh/.cache/keys/arc_llm_api.sh"
csv.field_size_limit(10**9)


def arc_key():
    txt = open(KEY_FILE).read()
    m = re.search(r'API_KEY\s*=\s*["\']?([^"\'\s]+)', txt)
    if not m:
        raise SystemExit("API_KEY not found in key file")
    return m.group(1)


def start_relay(model, log_path):
    port_file = log_path + ".port"
    if os.path.exists(port_file):
        os.remove(port_file)
    proc = subprocess.Popen([PY_NEW, os.path.join(CODE, "relay.py"), "--model", model,
                             "--log", log_path, "--port-file", port_file])
    for _ in range(100):
        if os.path.exists(port_file) and open(port_file).read().strip():
            return proc, int(open(port_file).read())
        time.sleep(0.1)
    proc.kill()
    raise RuntimeError("relay did not start")


def child_env(port):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("OPENAI_", "OPENROUTER_", "SERPAPI_"))}
    env["OPENAI_API_KEY"] = arc_key()
    env["OPENAI_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    env["OPENAI_API_BASE"] = f"http://127.0.0.1:{port}/v1"
    return env


def run_step(model, workdir, python, script, name):
    """Run one SelfHeal script in workdir behind its own relay."""
    log = os.path.join(workdir, f"relay_log_{name}.jsonl")
    proc, port = start_relay(model, log)
    t0 = time.time()
    try:
        with open(os.path.join(workdir, f"{name}.log"), "a") as out:
            r = subprocess.run([python, script], cwd=workdir, env=child_env(port),
                               stdout=out, stderr=subprocess.STDOUT)
    finally:
        proc.terminate()
        proc.wait()
    return {"step": name, "script": script, "python": python, "exit": r.returncode,
            "seconds": round(time.time() - t0, 1), "relay_log": os.path.basename(log)}


def save_record(path, rec):
    """Add this attempt to the record file. Earlier attempts in the same folder are kept."""
    attempts = []
    if os.path.exists(path):
        old = json.load(open(path))
        attempts = old["attempts"] if isinstance(old, dict) and "attempts" in old else [old]
    attempts.append(rec)
    json.dump({"attempts": attempts}, open(path, "w"), indent=1)


def rules(model):
    d = os.path.join(ROOT, model, "rules")
    os.makedirs(d, exist_ok=True)
    for f in ["fix-pattern.csv", "train_descriptions.csv", "test_descriptions.csv"]:
        shutil.copy(os.path.join(INPUTS, f), d)
    for f in ["clean_data.py", "extract_summary.py", "make_rules.py", "create_intent.py"]:
        shutil.copy(os.path.join(SELFHEAL, "preproceesing", f), d)
    # SelfHeal's readme runs clean_data.py once on the training file and once on the test
    # file by switching its file names. clean_data_test.py is that second version.
    src = open(os.path.join(d, "clean_data.py")).read()
    open(os.path.join(d, "clean_data_test.py"), "w").write(
        src.replace("train_descriptions_cleaned.csv", "test_descriptions_cleaned.csv")
           .replace('"train_descriptions.csv"', '"test_descriptions.csv"'))
    steps = []

    def stop_if_failed():
        # A step that exits non-zero stops the rules step, so no later step runs on its partial output.
        if steps[-1]["exit"] != 0:
            save_record(os.path.join(d, "run_record.json"),
                        {"model": model, "steps": steps, "stopped_at": steps[-1]["step"]})
            raise SystemExit(f"{steps[-1]['step']} exited {steps[-1]['exit']}")

    for script, name in [("clean_data.py", "clean_train"), ("clean_data_test.py", "clean_test")]:
        r = subprocess.run([PY_OLD, script], cwd=d, capture_output=True, text=True)
        steps.append({"step": name, "exit": r.returncode})
        stop_if_failed()
    steps.append(run_step(model, d, PY_OLD, "extract_summary.py", "extract_summary"))
    stop_if_failed()
    steps.append(run_step(model, d, PY_OLD, "make_rules.py", "make_rules"))
    stop_if_failed()
    # create_intent.py rewrites its whole output, so a finished intent file is never redone.
    out = os.path.join(d, "test_descriptions_with_intent.csv")
    want = {r["id"] for r in csv.DictReader(open(os.path.join(d, "test_descriptions.csv"), encoding="utf-8"))}
    have = ({r["id"] for r in csv.DictReader(open(out, encoding="utf-8")) if r.get("intent", "").strip()}
            if os.path.exists(out) else set())
    if want <= have:
        steps.append({"step": "create_intent", "exit": 0, "note": "kept the finished intent file"})
    else:
        steps.append(run_step(model, d, PY_NEW, "create_intent.py", "create_intent"))
    rec = {"model": model, "steps": steps}
    save_record(os.path.join(d, "run_record.json"), rec)
    print(json.dumps(rec, indent=1))


def case_ids():
    z = zipfile.ZipFile(ZIP)
    return sorted({p.split("/")[1] for p in z.namelist()
                   if p.count("/") >= 2 and not p.startswith("__MACOSX") and p.split("/")[1]})


def build_rerun(model, case, k):
    r = os.path.join(ROOT, model, case, f"rerun_{k}")
    fa = os.path.join(r, "Fix-Agent")
    dest = os.path.join(fa, "Dataset-Benchmark", case)
    os.makedirs(dest, exist_ok=True)
    os.makedirs(os.path.join(fa, "results"), exist_ok=True)
    z = zipfile.ZipFile(ZIP)
    for p in z.namelist():
        parts = p.split("/")
        if len(parts) == 3 and parts[1] == case and parts[2] and not parts[2].startswith("._") \
                and not p.startswith("__MACOSX"):
            with open(os.path.join(dest, parts[2]), "wb") as f:
                f.write(z.read(p))
    if case == "hf-26":
        shutil.copy(os.path.join(INPUTS, "hf-26_run_buggy.py"), os.path.join(dest, "run_buggy.py"))
    rules_dir = os.path.join(ROOT, model, "rules")
    shutil.copy(os.path.join(rules_dir, "fix_pattern_rules.csv"),
                os.path.join(fa, "fix_pattern_summaries.csv"))
    rows = [row for row in csv.DictReader(open(os.path.join(rules_dir, "test_descriptions_with_intent.csv"),
                                               encoding="utf-8")) if row["id"] == case]
    if len(rows) != 1:
        raise RuntimeError(f"{case}: {len(rows)} intent rows")
    with open(os.path.join(fa, "test_descriptions_with_intent.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "intent"])
        w.writeheader()
        w.writerow({"id": case, "intent": rows[0]["intent"]})
    shutil.copy(os.path.join(CODE, "run_agent.py"), os.path.join(r, "run_agent.py"))
    return r


def run_rerun(model, case, k):
    r = os.path.join(ROOT, model, case, f"rerun_{k}")
    if os.path.exists(os.path.join(r, "Fix-Agent", "results", f"{case}_result.txt")):
        return case, k, "done before"
    r = build_rerun(model, case, k)
    rec = run_step(model, r, PY_NEW, "run_agent.py", "run_agent")
    save_record(os.path.join(r, "run_record.json"), rec)
    return case, k, rec["exit"]


def repair(model, reruns, parallel, cases):
    cases = cases or case_ids()
    jobs = [(c, k) for k in range(1, reruns + 1) for c in cases]
    with ThreadPoolExecutor(parallel) as ex:
        for case, k, status in ex.map(lambda j: run_rerun(model, *j), jobs):
            print(case, k, status, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["rules", "repair"])
    ap.add_argument("--model", required=True, choices=["gpt-oss-120b", "GLM-5.3", "DeepSeek-V4.1-Flash"])
    ap.add_argument("--reruns", type=int, default=5)
    ap.add_argument("--parallel", type=int, default=5)
    ap.add_argument("--cases", nargs="*")
    a = ap.parse_args()
    if a.what == "rules":
        rules(a.model)
    else:
        repair(a.model, a.reruns, a.parallel, a.cases)


if __name__ == "__main__":
    main()
