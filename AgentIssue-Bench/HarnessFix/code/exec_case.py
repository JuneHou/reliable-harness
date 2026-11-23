#!/usr/bin/env python3
"""HarnessFix's task runner for AgentIssue-Bench, called by task_agent/run_agentissue.sh.

HarnessFix's AgentIssue-Bench mode is built on its SWE-Bench mode. This script takes the place of the
task agent run (run_swebench.sh) with --subset, --model, --workers and --output, plus --agent-src, the
repository tree to run. The tree's difference from the issue's buggy tree becomes a
patch, which goes through SelfHeal's AgentIssue-Bench test path unchanged (run_eval of
AgentIssue-Bench/SelfHeal/code/test_repairs.py, shipped evaluator: apply_patch then test_patched in a
fresh container of the issue's image). An unchanged tree uses calibrate.py's null patch, as the
original program's runs did. The test folder stays outside HarnessFix's working copy.

It then writes HarnessFix's SWE-Bench layout: <output>/preds.json with the tree's patch, and in
<output>/<tag>/ the trace <tag>.traj.json and the test's report.json and test_output.txt, which
eval/eval_agentissue.py places where the SWE-Bench harness writes its own. The trace's messages are the
issue text as the task (messages[1], inside <pr_description> as SWE-Bench's run_analysis reads it), each
model call the repository made during the test as the request's last message and the reply, and the
test's exit status and output as the last observation. Settings come from the driver: HF_CASE (the tag), HF_IMAGE, HF_RUNS_DIR and
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


def dangling(p):
    return os.path.islink(p) and not os.path.exists(p)


def same_file(x, y):
    """A link whose target is missing (ai_5628 and ai_6510 hold README.md -> packages/ai/README.md, and
    packages/ai/README.md is not in the tree) is compared as a link, by its target text, as git compares a
    link. Every other file is compared by content, as before."""
    if dangling(x) or dangling(y):
        return os.path.islink(x) and os.path.islink(y) and os.readlink(x) == os.readlink(y)
    return filecmp.cmp(x, y, shallow=False)


def copy_entry(src, dst):
    """A link whose target is missing is copied as a link; every other file as before."""
    if os.path.islink(dst):
        os.remove(dst)
    if dangling(src):
        os.symlink(os.readlink(src), dst)
    else:
        shutil.copy2(src, dst)


def tree_patch(base, cand):
    """git diff of every file that differs between the two trees, new and deleted files included."""
    a, b = files_of(base), files_of(cand)
    changed = sorted(p for p in a | b if p not in a or p not in b
                     or not same_file(os.path.join(base, p), os.path.join(cand, p)))
    if not changed:
        return "", []
    with tempfile.TemporaryDirectory() as tmp:
        g = ["git", "-C", tmp, "-c", "user.email=x@x", "-c", "user.name=x"]
        subprocess.run(["git", "init", "-q", tmp], check=True)
        for p in changed:
            if p in a:
                os.makedirs(os.path.dirname(os.path.join(tmp, p)), exist_ok=True)
                copy_entry(os.path.join(base, p), os.path.join(tmp, p))
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "base"], check=True)
        for p in changed:
            dst = os.path.join(tmp, p)
            if p in b:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                copy_entry(os.path.join(cand, p), dst)
            elif os.path.lexists(dst):
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


def other_relay_calls(relay_log):
    """Each logged call that is not a chat call, with what the relay logged for it."""
    if not os.path.exists(relay_log):
        return []
    out = []
    for n, line in enumerate(open(relay_log, encoding="utf-8"), start=1):
        r = json.loads(line)
        if "messages" not in (r.get("request") or {}):
            out.append({"line": n, **{k: r[k] for k in ("path", "embed_model", "embed_inputs", "embed_reused", "status")
                                      if k in r}})
    return out


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
    task = json.loads(open(os.path.join(a.subset, "data.jsonl"), encoding="utf-8").readline())
    intent = task.get("instruction") or task.get("question") or ""
    exit_status = "solved" if rec["passed"] else ("error" if rec["timed_out"] else "unsolved")
    task_out = os.path.join(a.output, tag)
    os.makedirs(task_out, exist_ok=True)
    write_json(os.path.join(task_out, "report.json"), {
        "instance_id": tag, "resolved": bool(rec["passed"]), "exit": rec["exit"], "timed_out": rec["timed_out"],
        "failed_in_stdout": rec["failed_in_stdout"], "success_message": rec["success_message"],
        "evaluator": "shipped", "null_patch": not patch, "changed_files": changed})
    open(os.path.join(task_out, "test_output.txt"), "w", encoding="utf-8").write(
        stdout + ("\n--- stderr ---\n" + stderr if stderr else ""))
    messages = [
        {"role": "system", "content": f"AgentIssue-Bench issue {tag}: the repository at the issue's commit runs with "
                                      "the issue's test in the issue's Docker image."},
        {"role": "user", "content": f"<pr_description>\n{intent}\n</pr_description>"},
    ]
    for c in calls:
        last = (c["request_messages"] or [{}])[-1]
        messages.append({"role": "user", "content": last.get("content") if isinstance(last.get("content"), str)
                         else json.dumps(last.get("content"), ensure_ascii=False)})
        messages.append({"role": "assistant", "content": (c["response_message"] or {}).get("content") or ""})
    messages.append({"role": "user", "content": f"<returncode>{rec['exit']}</returncode>\n<output>\n"
                                                f"{(stdout + chr(10) + stderr)[-6000:]}\n</output>"})
    write_json(os.path.join(task_out, f"{tag}.traj.json"), {
        "trajectory_format": "stochastic-harness-agentissue-swe-layout", "instance_id": tag,
        "messages": messages, "model_calls": calls,
        "info": {"exit_status": exit_status, "submission": patch, "model": model, "test_record": rec,
                 "chat_trace": {"source": "relay_log_test.jsonl", "model_call_count": len(calls),
                                # plan, run record item: calls the relay logged that are not chat calls
                                # (embedding lookups); none of the 50 issues' original runs made one
                                "other_relay_calls": other_relay_calls(os.path.join(out, "relay_log_test.jsonl")),
                                "request_response_granularity": "relay_request_reply",
                                "raw_provider_payload_available": True},
                 "model_stats": {"api_calls": len(calls), "instance_cost": 0.0}}})
    write_json(os.path.join(a.output, "preds.json"),
               {tag: {"instance_id": tag, "model_name_or_path": model, "model_patch": patch}})
    write_json(os.path.join(a.output, "run_info.json"), {"benchmark": "agentissue", "model": model, "n_predictions": 1,
               "tasks": [{"task_id": tag, "trial_name": label, "exit_status": exit_status, "passed": rec["passed"]}],
               "test_folder": out})
    print(f"[agentissue] {tag} {label}: passed {rec['passed']}, {len(changed)} changed files, {len(calls)} model calls", flush=True)


if __name__ == "__main__":
    main()
