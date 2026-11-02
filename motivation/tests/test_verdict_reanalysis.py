"""Offline tests for the verdict reanalysis exp-2026-10-23-v. No key, no network, no model call."""

import json
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from motivation_pilot import extension as ext  # noqa: E402
from motivation_pilot import verdict_reanalysis as vr  # noqa: E402
from motivation_pilot import verdict_stats as vs  # noqa: E402

EXT = ext.ROOT / "artifacts" / "agentdefect_extension"


def test_jeffreys_three_of_three():
    lo, hi = vs.jeffreys(3, 3)
    assert round(lo, 3) == 0.464 and round(hi, 3) == 1.000
    assert round(vs.jeffreys(0, 3)[1], 3) == 0.536


def test_fisher_three_against_zero():
    assert round(vs.fisher_p(3, 3, 0, 3), 3) == 0.1


def test_contrast_probabilities():
    c = vs.contrast(3, 3, 0, 3)
    assert abs(c["p_delta_positive"] + c["p_delta_negative"] - 1) < 1e-6
    assert round(c["p_delta_positive"], 3) == 0.996, "the posterior rule accepts three against zero where Fisher gives 0.1"
    assert c["delta_interval"][0] > 0
    close = vs.contrast(3, 3, 3, 3)["p_delta_close"]
    assert round(close["0.2"], 2) == 0.72 and round(close["0.1"], 2) == 0.50


def test_survival_rules():
    c = vs.contrast(3, 3, 0, 3)
    assert vs.survives("required_in_context", c, 0.2) is True
    assert vs.survives("removable_in_context", vs.contrast(3, 3, 3, 3), 0.2) is False
    assert vs.survives("removable_in_context", vs.contrast(12, 12, 12, 12), 0.2) is True
    for v in ("harmful_edit_table", "not_assessed_parent_not_adequate", "unresolved_in_context", "not_admissible"):
        assert vs.survives(v, c, 0.2) is None


def test_required_cells_restrict_the_pool():
    with_side = [("target", 1, True)] * 3 + [("extra", 0, True)] * 3
    without_side = [("target", 0, None)] * 3 + [("extra", 1, None)] * 3
    pooled = vs.summarise_comparison(with_side, without_side, "required_in_context")
    required = vs.summarise_comparison(with_side, without_side, "required_in_context", required_cells=["target"])
    assert pooled["with"]["k"] == 3 and pooled["with"]["n"] == 6 and pooled["survives"] is False
    assert required["with"]["k"] == 3 and required["with"]["n"] == 3 and required["survives"] is True


def _rows(batch):
    directory = EXT / batch
    runs = {r["run_id"]: r for r in ext.load_runs(directory)}
    return directory, runs, {c["comparison_id"] + (f"@{c['environment']}" if c.get("environment") else ""): c
                             for c in ext.read_jsonl(directory / "comparisons.jsonl")}


def _enactment(batch, comparison_id):
    directory, runs, comps = _rows(batch)
    comp = comps[comparison_id]
    case = comp.get("case", "78383658")
    with_runs, _ = vr.sides(comp, runs)
    return [vr.enacted(case, vr.edits_of(case, comp["change"]), vr.trace_kinds(directory, r))[0] for r in with_runs]


def test_enactment_rule_on_recorded_traces():
    assert _enactment("exp-2026-10-22", "76906469:B|empty") == [False, False, False], "B alone never reaches a request"
    assert _enactment("exp-2026-10-22", "79343179:L1|L2+L3") == [True, True, True]
    p_core = _enactment("exp-2026-10-22", "77178370:P_core|empty")
    assert len(p_core) == 9 and 0 < sum(p_core) < 9, "the published agent called its tool in some runs only"


def test_not_observable():
    for batch, cid in (("exp-2026-10-22", "78366661:P2|N+P1"), ("exp-2026-10-22", "77099194:W1|empty"), ("exp-2026-10-22", "78366661:N|empty")):
        assert set(_enactment(batch, cid)) == {None}


def test_sides_match_recorded_counts():
    for batch in vr.BATCHES:
        directory, runs, comps = _rows(batch)
        for comp in comps.values():
            with_runs, without_runs = vr.sides(comp, runs)
            cited = [runs[i] for i in comp["run_ids"]]
            assert len(with_runs) == sum(1 for r in cited if r["configuration"] == comp["with"])
            assert len(without_runs) == sum(1 for r in cited if r["configuration"] == comp["without"])
            assert len(with_runs) + len(without_runs) == len(comp["run_ids"])


def test_outputs_when_present():
    out = vr.OUT / "reanalysis.jsonl"
    if not out.exists():
        return
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    summary = json.loads((vr.OUT / "summary.json").read_text())
    assert len(rows) == 88 and summary["rows"] == 88
    assert sum(summary["by_batch"].values()) == 88
