"""exp-2026-10-23-v, reanalysis of every recorded AgentDefect comparison with enactment rates and pass probability intervals.

No model call. Reads the runs, traces and comparisons of exp-2026-10-22, exp-2026-10-22-r and exp-2026-10-23-e.

    PYTHONPATH=src python -m motivation_pilot.verdict_reanalysis run [--delta 0.2]
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from motivation_pilot import extension as ext
from motivation_pilot import verdict_stats as vs

EXP_ID = "exp-2026-10-23-v"
OUT = ext.ROOT / "artifacts" / "agentdefect_extension" / EXP_ID
BATCHES = ["exp-2026-10-22", "exp-2026-10-22-r", "exp-2026-10-23-e"]
DEFAULT_DELTA = 0.2

# Module to the trace event kind that shows the module ran. Modules absent here have no probe.
MODULE_EVENT = {
    "memory_representation": ["memory_before"], "memory": ["memory_before"],
    "agent_control": ["request_prepared"], "prompt": ["request_prepared"], "chain_control": ["request_prepared"],
    "execution_control": ["request_prepared"],
    "loader": ["loader_output"], "vector_store": ["embedding", "retrieval"], "retrieval": ["retrieval"],
    "tools": ["tool_call"], "output_parsing": ["parser"],
}
NOT_OBSERVABLE = {"document_splitting", "model_client", "data_loading"}
EXTRA_COMPONENTS = {"78383658": {"R": ["retrieval"]}}
PROBE_KINDS = {"probe_installed", "probe_unresolved", "probe_error"}


def edits_of(case: str, change: str) -> list[str]:
    """The edits a comparison's change names. 'bundle U1+U2' names two."""
    if change.startswith("bundle"):
        return change.split(" ", 1)[1].split("+")
    return [change]


def modules_of(case: str, edits: list[str]) -> list[str]:
    components = {**ext.COMPONENTS.get(case, {}), **EXTRA_COMPONENTS.get(case, {})}
    return sorted({m for e in edits for m in components[e]})


def trace_kinds(directory: Path, run: dict) -> Counter:
    path = directory / run["trace"]
    if not path.exists():
        return Counter()
    return Counter(json.loads(line)["kind"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def enacted(case: str, edits: list[str], kinds: Counter) -> tuple:
    """(enacted or None, evidence). None when a module of the edit has no probe."""
    modules = modules_of(case, edits)
    if any(m in NOT_OBSERVABLE or m not in MODULE_EVENT for m in modules):
        return None, {m: "not_observable" for m in modules if m in NOT_OBSERVABLE or m not in MODULE_EVENT}
    evidence = {m: {k: kinds.get(k, 0) for k in MODULE_EVENT[m]} for m in modules}
    return all(any(kinds.get(k, 0) > 0 for k in MODULE_EVENT[m]) for m in modules), evidence


def sides(comp: dict, runs_by_id: dict) -> tuple[list[dict], list[dict]]:
    cited = [runs_by_id[i] for i in comp["run_ids"] if i in runs_by_id]
    with_runs = [r for r in cited if r["configuration"] == comp["with"] and r.get("probe", True)]
    without_runs = [r for r in cited if r["configuration"] == comp["without"] and r.get("probe", True)]
    return with_runs, without_runs


def analyse_batch(batch: str, delta: float) -> tuple[list[dict], list[dict], list[dict]]:
    directory = ext.ROOT / "artifacts" / "agentdefect_extension" / batch
    runs = ext.load_runs(directory)
    runs_by_id = {r["run_id"]: r for r in runs}
    comps = ext.read_jsonl(directory / "comparisons.jsonl")
    rows, enact_rows, cell_rows = [], [], []
    for comp in comps:
        case = comp.get("case", "78383658")
        edits = edits_of(case, comp["change"])
        with_runs, without_runs = sides(comp, runs_by_id)
        row_id = comp["comparison_id"] + (f"@{comp['environment']}" if comp.get("environment") else "")
        with_side, without_side = [], []
        for r in with_runs:
            e, evidence = enacted(case, edits, trace_kinds(directory, r))
            with_side.append((r["input_id"], r["status"] == "completed_pass", e))
            enact_rows.append({"batch": batch, "comparison_id": row_id, "run_id": r["run_id"], "configuration": r["configuration"],
                               "input_id": r["input_id"], "status": r["status"], "enacted": e, "evidence": evidence})
        for r in without_runs:
            without_side.append((r["input_id"], r["status"] == "completed_pass", None))
        verdict = comp["verdict"] if comp["verdict"] is not None else "not_admissible"
        summary = vs.summarise_comparison(with_side, without_side, verdict, delta)
        summary["enactment"]["modules"] = modules_of(case, edits)
        errors = {"with": sum(1 for r in with_runs if r["status"] not in ("completed_pass", "behavioral_failure")),
                  "without": sum(1 for r in without_runs if r["status"] not in ("completed_pass", "behavioral_failure"))}
        rows.append({"batch": batch, "comparison_id": row_id, "case": case, "change": comp["change"], "context": comp["context"],
                     "with_configuration": comp["with"], "without_configuration": comp["without"],
                     "environment": comp.get("environment"), "recorded_class": comp["class"], "errors": errors, **summary})
        for name, side in (("with", with_side), ("without", without_side)):
            for cell, c in vs.cells_of(side).items():
                cell_rows.append({"batch": batch, "comparison_id": row_id, "side": name, "cell": cell, **c})
    return rows, enact_rows, cell_rows


def summarise(rows: list[dict], delta: float) -> dict:
    by_verdict = {}
    for v in sorted({r["recorded_verdict"] for r in rows}):
        sub = [r for r in rows if r["recorded_verdict"] == v]
        by_verdict[v] = {"rows": len(sub), "survives": sum(1 for r in sub if r["survives"] is True),
                         "fails": sum(1 for r in sub if r["survives"] is False),
                         "no_label": sum(1 for r in sub if r["survives"] is None),
                         "never_enacted": sum(1 for r in sub if r["enactment"]["state"] == "never_enacted"),
                         "not_observable": sum(1 for r in sub if r["enactment"]["state"] == "not_observable"),
                         "partially_enacted": sum(1 for r in sub if r["enactment"]["rate"] not in (None, 0, 1))}
    return {"experiment": EXP_ID, "delta": delta, "level": vs.LEVEL, "batches": BATCHES, "rows": len(rows),
            "by_batch": dict(Counter(r["batch"] for r in rows)), "by_verdict": by_verdict,
            "survives_total": sum(1 for r in rows if r["survives"] is True),
            "labelled_total": sum(1 for r in rows if r["survives"] is not None),
            "required_fail_fisher": sum(1 for r in rows if r["recorded_verdict"] == "required_in_context" and (r["fisher_p"] or 1) >= 0.05),
            "min_fisher_p": min((r["fisher_p"] for r in rows if r["fisher_p"] is not None), default=None)}


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def cmd_run(delta: float) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, enact_rows, cell_rows = [], [], []
    for batch in BATCHES:
        r, e, c = analyse_batch(batch, delta)
        rows += r
        enact_rows += e
        cell_rows += c
    write_jsonl(OUT / "reanalysis.jsonl", rows)
    write_jsonl(OUT / "enactment.jsonl", enact_rows)
    write_jsonl(OUT / "cells.jsonl", cell_rows)
    summary = summarise(rows, delta)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--delta", type=float, default=DEFAULT_DELTA)
    a = parser.parse_args(argv)
    return cmd_run(a.delta)


if __name__ == "__main__":
    sys.exit(main())
