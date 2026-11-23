#!/usr/bin/env python3
"""HarnessFix's task runner for AgentDefect, called by task_agent/run_agentdefect.sh.

It takes the same arguments as HarnessFix's GAIA runner, run_gaia.sh (--subset, --model, --workers,
--concurrency, --output), plus --agent-src, the harness folder to run. For the case in the subset it
executes the folder's run_buggy.py through SelfHeal's AgentDefect test path, unchanged (run_test of
AgentDefect/SelfHeal/code/test_repairs.py): the program is written as run_fixed.py into a copy of the
case and the case's test.py runs it, with the program's model calls going through the relay to the
run's ARC model. The test folder stays outside HarnessFix's working copy.

It then writes GAIA's trace layout in <output>/<case>/ (as run_gaia_entry.py does): <case>.traj.json
with info (exit_status, prediction, elapsed_seconds), a trajectory with one step per call the relay
logged (chat calls and the program's embedding lookups, in order) and model_calls with the chat calls,
plus test-stdout.txt with the program and test output, and <output>/preds.json. The
prediction is the end of the program and test output, since the case's test, not an answer string,
decides.

Settings come from the driver through the environment: HF_CASE, HF_RUNS_DIR, HF_ENV_PY, HF_ENV_REC
and HF_EMBED_STORE.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code")
import test_repairs as tr  # noqa: E402
tr.EMBED_STORE = os.environ["HF_EMBED_STORE"]


def relay_record(relay_log):
    """Every call the relay logged during the run, in the logged order (plan, "Resolved by a reference",
    run record item). Each call is one step of the trajectory in the step layout of GAIA's runner
    (run_gaia_entry.py _step_to_dict: model_input_messages, model_output_message, tool_calls with name,
    arguments and id, observations). A chat call keeps its messages, and is also in model_calls with
    call_index equal to its step number, so compile_gaia_htir reads it once. An embedding call, the
    program's lookup of matching text, is a tool call with what the relay logged for it."""
    trajectory, calls = [], []
    if not os.path.exists(relay_log):
        return trajectory, calls
    for n, line in enumerate(open(relay_log, encoding="utf-8"), start=1):
        r = json.loads(line)
        k = len(trajectory) + 1
        source = f"relay_log_test.jsonl line {n}"
        if "messages" in (r.get("request") or {}):
            resp = r.get("response") or {}
            msg = {}
            if isinstance(resp, dict) and resp.get("choices"):
                msg = resp["choices"][0].get("message") or {}
            elif r.get("response_text") is not None:
                msg = {"role": "assistant", "content": r["response_text"]}
            calls.append({"call_index": k, "request_messages": r["request"]["messages"],
                          "response_message": msg, "status": r.get("status"),
                          "usage": r.get("usage_returned")})
            trajectory.append({"_type": "ActionStep", "step_number": k, "source": source,
                               "model_input_messages": r["request"]["messages"], "model_output_message": msg})
        else:
            args = {key: r[key] for key in ("path", "embed_model", "embed_inputs", "embed_reused") if key in r}
            obs = f"status {r.get('status')}"
            if "embed_inputs" in r:
                obs += f", {r['embed_inputs']} input(s) embedded"
            if r.get("embed_reused"):
                obs += ", reply reused from the embedding store"
            if r.get("response_text"):
                obs += f", reply: {r['response_text'][:2000]}"
            name = "embeddings" if str(r.get("path", "")).endswith("/embeddings") else str(r.get("path"))
            trajectory.append({"_type": "ActionStep", "step_number": k, "source": source,
                               "tool_calls": [{"name": name, "arguments": args, "id": f"relay_call_{k}"}],
                               "observations": obs})
    return trajectory, calls


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
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    case = os.environ["HF_CASE"]
    ids = [l.strip() for l in open(os.path.join(a.subset, "instance_ids.txt")) if l.strip()]
    if ids != [case]:
        sys.exit(f"subset {a.subset} holds {ids}, expected [{case}]")
    model = a.model.split("/", 1)[1] if a.model.startswith("openai/") else a.model
    py = os.environ["HF_ENV_PY"]
    env_rec = json.load(open(os.environ["HF_ENV_REC"]))
    code = open(os.path.join(a.agent_src, "run_buggy.py"), encoding="utf-8").read()
    label = os.path.basename(os.path.normpath(a.output))
    t = os.path.join(os.environ["HF_RUNS_DIR"], label, case)
    outcome = tr.run_test(t, model, case, code, py, env_rec,
                          {"kind": "harnessfix_internal", "run": label,
                           "agent_src": os.path.relpath(a.agent_src, os.path.dirname(os.path.dirname(a.agent_src)))})
    # plan departure 4: run_test copies the case folder, test.py and readme.md included, into the test folder,
    # whose path the test output prints; the two copies are deleted once the test has run, so no file the
    # HarnessFix agents can reach holds the test or the readme (test.log and test_record.json stay)
    for name in ("test.py", "readme.md"):
        if os.path.exists(os.path.join(t, name)):
            os.remove(os.path.join(t, name))
    rec = json.load(open(os.path.join(t, "test_record.json")))
    log = open(os.path.join(t, "test.log"), encoding="utf-8", errors="replace").read()
    trajectory, calls = relay_record(os.path.join(t, "relay_log_test.jsonl"))
    exit_status = "solved" if rec["passed"] else "unsolved"
    prediction = log[-3000:] if log.strip() else ""
    task_out = os.path.join(a.output, case)
    os.makedirs(task_out, exist_ok=True)
    with open(os.path.join(task_out, "test-stdout.txt"), "w", encoding="utf-8") as f:
        f.write(log)
    write_json(os.path.join(task_out, f"{case}.traj.json"), {
        "trajectory_format": "stochastic-harness-agentdefect-relay-adapter",
        "instance_id": case,
        "trajectory": trajectory,
        "model_calls": calls,
        "info": {"exit_status": exit_status, "prediction": prediction, "iteration_limit_exceeded": False,
                 "elapsed_seconds": rec["seconds"], "test_passed": rec["passed"], "test_exit": rec["exit"],
                 "model": model, "task_name": case, "run": label,
                 "test_output_path": os.path.join(task_out, "test-stdout.txt"),
                 "model_stats": {"api_calls": len(calls), "instance_cost": 0.0}},
    })
    preds_path = os.path.join(a.output, "preds.json")
    preds = json.load(open(preds_path)) if os.path.exists(preds_path) else {}
    preds[case] = prediction
    write_json(preds_path, preds)
    write_json(os.path.join(a.output, "run_info.json"), {
        "benchmark": "agentdefect", "model": model, "n_predictions": len(preds),
        "tasks": [{"task_id": case, "run": label, "exit_status": exit_status}], "test_folder": t})
    print(f"[agentdefect] {case} {label}: {outcome}, {len(calls)} model calls", flush=True)


if __name__ == "__main__":
    main()
