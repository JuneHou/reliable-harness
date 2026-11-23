#!/usr/bin/env python3
"""HarnessFix's task runner for AgentIssue-Bench, called by task_agent/run_agentissue.sh.

Same arguments as HarnessFix's Terminal-Bench runner (--subset, --model, --workers, --output) plus
--agent-src, the repository tree to run. The tree's difference from the issue's buggy tree becomes a
patch, which goes through SelfHeal's AgentIssue-Bench test path unchanged (run_eval of
AgentIssue-Bench/SelfHeal/code/test_repairs.py, shipped evaluator: apply_patch then test_patched in a
fresh container of the issue's image). An unchanged tree uses calibrate.py's null patch, as the
original program's runs did. The test folder stays outside HarnessFix's working copy.

It then writes HarnessFix's Terminal-Bench trace layout in <output>/<tag>/, as exec_case.py of the
AgentDefect side does. Settings come from the driver: HF_CASE (the tag), HF_IMAGE, HF_RUNS_DIR and
HF_BASE_TREE.
"""
import argparse
import filecmp
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

AIC = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code"
sys.path.insert(0, AIC)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def files_of(root):
    out = set()
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "__pycache__")]
        for f in fs:
            if f.endswith(".pyc"):
                continue
            out.add(os.path.relpath(os.path.join(d, f), root))
    return out


def tree_patch(base, cand):
    """git diff of every file that differs between the two trees, new and deleted files included."""
    a, b = files_of(base), files_of(cand)
    changed = sorted(p for p in a | b if p not in a or p not in b
                     or not filecmp.cmp(os.path.join(base, p), os.path.join(cand, p), shallow=False))
    if not changed:
        return "", []
    with tempfile.TemporaryDirectory() as tmp:
        g = ["git", "-C", tmp, "-c", "user.email=x@x", "-c", "user.name=x"]
        subprocess.run(["git", "init", "-q", tmp], check=True)
        for p in changed:
            if p in a:
                os.makedirs(os.path.dirname(os.path.join(tmp, p)), exist_ok=True)
                shutil.copy2(os.path.join(base, p), os.path.join(tmp, p))
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "base"], check=True)
        for p in changed:
            dst = os.path.join(tmp, p)
            if p in b:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(cand, p), dst)
            elif os.path.exists(dst):
                os.remove(dst)
        subprocess.run(g + ["add", "-A"], check=True)
        r = subprocess.run(g + ["diff", "--cached", "--no-renames", "--src-prefix=a/", "--dst-prefix=b/"],
                           check=True, capture_output=True)
    return r.stdout.decode("utf-8", "surrogateescape"), changed


def chat_calls(relay_log):
    calls = []
    if not os.path.exists(relay_log):
        return calls
    for line in open(relay_log, encoding="utf-8"):
        r = json.loads(line)
        if "request" not in r or "messages" not in (r.get("request") or {}):
            continue
        resp = r.get("response") or {}
        msg = {}
        if isinstance(resp, dict) and resp.get("choices"):
            msg = resp["choices"][0].get("message") or {}
        elif r.get("response_text") is not None:
            msg = {"role": "assistant", "content": r["response_text"]}
        calls.append({"call_index": len(calls) + 1, "request_messages": r["request"]["messages"],
                      "response_message": msg, "status": r.get("status"), "usage": r.get("usage_returned")})
    return calls


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-src", required=True)
    ap.add_argument("--subset", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    tag = os.environ["HF_CASE"]
    ids = [l.strip() for l in open(os.path.join(a.subset, "instance_ids.txt")) if l.strip()]
    if ids != [tag]:
        sys.exit(f"subset {a.subset} holds {ids}, expected [{tag}]")
    model = a.model.split("/", 1)[1] if a.model.startswith("openai/") else a.model
    tr = load("aic_test_repairs", os.path.join(AIC, "test_repairs.py"))
    tr.adt.EMBED_STORE = os.environ["HF_EMBED_STORE"]   # HarnessFix's own store, never the file SelfHeal's queue appends to
    cal = load("aic_calibrate", os.path.join(AIC, "calibrate.py"))
    patch, changed = tree_patch(os.environ["HF_BASE_TREE"], a.agent_src)
    label = os.path.basename(os.path.normpath(a.output))
    out = os.path.join(os.environ["HF_RUNS_DIR"], label, tag)
    rec = tr.run_eval(tag, os.environ["HF_IMAGE"], model, out, "shipped", patch or cal.NULL_PATCH,
                      extra={"kind": "harnessfix_internal", "run": label, "changed": changed,
                             "null_patch": not patch})
    stdout = open(os.path.join(out, "test.log"), encoding="utf-8", errors="replace").read()
    stderr = open(os.path.join(out, "test_stderr.log"), encoding="utf-8", errors="replace").read()
    calls = chat_calls(os.path.join(out, "relay_log_test.jsonl"))
    reward = 1.0 if rec["passed"] else 0.0
    exit_status = "solved" if rec["passed"] else "unsolved"
    task_out = os.path.join(a.output, tag)
    write_json(os.path.join(task_out, "result.json"), {"task_name": tag, "trial_name": label,
               "verifier_result": {"rewards": {"reward": reward}}, "exception_info": None, "test_record": rec})
    open(os.path.join(task_out, "test-stdout.txt"), "w", encoding="utf-8").write(stdout)
    open(os.path.join(task_out, "test-stderr.txt"), "w", encoding="utf-8").write(stderr)
    steps = [{"step_id": c["call_index"], "source": "agent",
              "message": (c["response_message"] or {}).get("content") or "",
              "tool_calls": (c["response_message"] or {}).get("tool_calls") or [], "observation": {}} for c in calls]
    steps.append({"step_id": len(steps) + 1, "source": "system",
                  "message": f"issue test run, exit {rec['exit']}, timed out {rec['timed_out']}",
                  "observation": {"results": [{"content": (stdout + "\n" + stderr)[-6000:]}]}})
    write_json(os.path.join(task_out, f"{tag}.atif.json"),
               {"schema_version": "ATIF-v1.2", "agent": {"name": f"AgentIssue-Bench {tag} system", "model": model},
                "steps": steps})
    messages = (calls[-1]["request_messages"] + [calls[-1]["response_message"]]) if calls else []
    write_json(os.path.join(task_out, f"{tag}.traj.json"), {
        "trajectory_format": "stochastic-harness-agentissue-relay-adapter", "instance_id": tag,
        "messages": messages, "model_calls": calls,
        "info": {"exit_status": exit_status, "prediction": str(reward), "reward": reward, "model": model,
                 "task_name": tag, "trial_name": label, "exception": None,
                 "trajectory_atif_path": os.path.join(task_out, f"{tag}.atif.json"),
                 "chat_trace": {"source": "relay_log_test.jsonl", "model_call_count": len(calls),
                                "request_response_granularity": "relay_request_reply",
                                "raw_provider_payload_available": True},
                 "model_stats": {"api_calls": len(calls), "instance_cost": 0.0}}})
    write_json(os.path.join(a.output, "preds.json"), {tag: str(reward)})
    write_json(os.path.join(a.output, "run_info.json"), {"benchmark": "agentissue", "model": model, "n_predictions": 1,
               "tasks": [{"task_id": tag, "trial_name": label, "exit_status": exit_status, "reward": reward}],
               "test_folder": out})
    print(f"[agentissue] {tag} {label}: passed {rec['passed']}, {len(changed)} changed files, {len(calls)} model calls", flush=True)


if __name__ == "__main__":
    main()
