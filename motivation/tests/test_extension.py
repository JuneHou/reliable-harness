"""Offline tests for the AgentDefect extension exp-2026-10-22. No key, no network."""

import json
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from motivation_pilot import extension as ext  # noqa: E402
from motivation_pilot import instrument  # noqa: E402
from motivation_pilot import pilot_run as pr  # noqa: E402

CONFIGS = {case: ext.build_configurations(case) for case in ext.CASE_ORDER}


class _Proc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def test_run_module_defaults_unchanged(monkeypatch):
    calls = []

    def transient(argv, **kwargs):
        calls.append(argv)
        return _Proc(1, "", "openai.RateLimitError: RateLimit")

    monkeypatch.setattr(pr.subprocess, "run", transient)
    legacy = pr._run_module("77178370", "run_buggy", "q", None, 5)
    assert "error" in legacy
    assert len(calls) == 2, "the pilot's own retry loop is kept for default arguments"
    script = calls[0][2]
    assert script.startswith(pr._study_prelude()) and "max_retries" not in script and "_mp_phase" not in script

    calls.clear()
    extension = pr._run_module("77178370", "run_buggy", "q", None, 5, probe=False)
    assert len(calls) == 1, "extension calls make one attempt"
    assert "max_retries" in calls[0][2] and "_mp_phase" in calls[0][2]
    assert extension["returncode"] == 1


def test_audit_source_identical():
    source = ext.archive_text("77178370", "run_buggy.py")
    old = ('    query = "what are cars made of?"\n    result = qa({"question": query})\n'
           '    result= retriever.get_relevant_documents(query)\n    \n    return result')
    new = '    result = qa({"question": user_input})\n    return result["answer"]'
    assert pr._audit_building_source(source) == source.replace(old, new, 1)


def test_decompositions_rebuild_routes():
    for case in ext.CASE_ORDER:
        checks = ext.decomposition_checks(case, CONFIGS[case])
        assert all(row["equal"] for row in checks["reconstruction"]), case
    loader = CONFIGS["79343179"]
    assert ext.same_ast(loader["L1L2"]["source"], loader["published"]["source"], "loader")


def test_comparisons_isolated():
    rows = ext.comparisons()
    assert len(rows) == 32
    for case in ext.CASE_ORDER:
        checks = ext.decomposition_checks(case, CONFIGS[case])["comparisons"]
        for comparison_id, entry in checks.items():
            assert entry["isolated"], comparison_id
            if entry["declared"] is not None:
                assert (entry["removed"], entry["added"]) == tuple(entry["declared"]), comparison_id


def test_static_coherence_labels():
    for case, configs in CONFIGS.items():
        for name, config in configs.items():
            label = ext.coherence(config)["label"]
            expected = "incompatible_fragment" if (case, name) == ("76906469", "B") else "coherent"
            assert label == expected, (case, name, ext.coherence(config))


def test_contract_q1_q4_after_corrections():
    assert ext.ORACLE.name == "frozen_oracles_v2.json"
    for case in ext.CASE_ORDER:
        for row in ext.contract(case):
            if row["required_for_adequacy"]:
                assert row["q1_frozen_accepted"] is True, (case, row["check_id"])
                assert row["q4_expected_matches_assets"] is not False, (case, row["check_id"])
    turn2 = ext.contract("76906469")[0]
    assert "test.py line 14" in turn2["q1_source"] and "limited_endpoint" in turn2["note"]


def test_wrappers_fire_on_resolved_classes(tmp_path):
    for boundary in ("memory", "retrieval", "embeddings", "parsers", "agent_parsers", "tools"):
        result = ext.selftest_boundary(boundary, tmp_path)
        assert result["ok"], result
    parsers = ext.selftest_boundary("parsers", tmp_path)
    assert any("StrOutputParser.invoke from langchain_core.output_parsers.base.BaseOutputParser" in line
               for line in parsers["installed"])
    memory = ext.selftest_boundary("memory", tmp_path)
    assert any("save_context from langchain.memory.chat_memory.BaseChatMemory" in line for line in memory["installed"])


def test_request_prepared_and_backend_attempt(tmp_path):
    trace = tmp_path / "both.jsonl"
    script = (pr._study_prelude() + instrument.NO_RETRY_PRELUDE
              + instrument.trace_prelude(trace, ["chat_request", "network_attempt"]) + ext.SELFTEST_BODIES["chat_request"])
    proc = subprocess.run([sys.executable, "-c", script], cwd=tmp_path, capture_output=True, text=True, timeout=300,
                          env={**__import__("os").environ, "OPENAI_API_KEY": "sk-test"})
    assert proc.returncode == 0, proc.stderr[-800:]
    events = instrument.read_trace(trace)
    assert sum(e["kind"] == "request_prepared" for e in events) == 1
    assert sum(e["kind"] == "backend_attempt" for e in events) == 1
    failing = ext.selftest_boundary("network_attempt", tmp_path)
    assert failing["failing_calls"] == 1 and failing["backend_attempt_events"] == 1


def _raw(info, returncode=1, timeout=False):
    return {"timeout": timeout, "returncode": returncode, "result": info}


def test_status_classification():
    config = {"source": "import added_pkg\nimport os\n", "actions": []}
    original = "import os\n"
    sha = ext.sha256_text(config["source"])
    base = {"ok": False, "loaded_sha256": sha, "mp_failed_phase": "turn_1", "error_mro": ["ValueError", "Exception"],
            "last_boundary": "memory"}
    assert ext.classify(_raw(None, timeout=True), [], config, original)[0] == "unresolved_timeout"
    assert ext.classify(_raw(None), [], config, original)[0] == "evaluator_failure"
    assert ext.classify(_raw({**base, "loaded_sha256": "other"}), [], config, original)[0] == "application_failure"
    assert ext.classify(_raw({"ok": True, "loaded_sha256": sha}, returncode=0), [], config, original)[0] == "completed"
    assert ext.classify(_raw({**base, "mp_failed_phase": "prelude"}), [], config, original)[0] == "instrumentation_failure"
    probe_first = [{"seq": 1, "kind": "probe_error"}, {"seq": 2, "kind": "exception"}]
    assert ext.classify(_raw(base), probe_first, config, original)[0] == "instrumentation_failure"
    assert ext.classify(_raw({**base, "mp_failed_phase": "flatten"}), [], config, original)[0] == "evaluator_failure"
    added = {**base, "error_mro": ["ModuleNotFoundError", "ImportError", "Exception"], "missing_module": "added_pkg"}
    assert ext.classify(_raw(added), [], config, original) == ("interface_runtime_failure", "candidate_import")
    env = {**added, "missing_module": "os"}
    assert ext.classify(_raw(env), [], config, original)[0] == "environment_blocked"
    infra = {**base, "error_mro": ["RateLimitError", "APIStatusError", "APIError", "OpenAIError", "Exception"]}
    assert ext.classify(_raw(infra), [], config, original)[0] == "infrastructure_failure"
    network = {**base, "error_mro": ["ConnectionError", "RequestException", "OSError", "Exception"]}
    assert ext.classify(_raw(network), [], config, original)[0] == "environment_blocked"
    assert ext.classify(_raw(base), [], config, original) == ("interface_runtime_failure", "memory")


def _run(config, rep, status, passed=None, input_id="buildings", case="77178370"):
    checks = {input_id: {"passed": passed}} if passed is not None else {}
    return {"case": case, "configuration": config, "input_id": input_id, "repetition": rep, "probe": True,
            "status": status, "checks": checks}


def test_check_outcomes_and_qualification(monkeypatch):
    runs = [_run("p", r, "completed_pass", True) for r in (1, 2, 3)]
    runs += [_run("f", r, "behavioral_failure", False) for r in (1, 2, 3)]
    runs += [_run("u", 1, "completed_pass", True), _run("u", 2, "behavioral_failure", False), _run("u", 3, "completed_pass", True)]
    runs += [_run("m", 1, "completed_pass", True), _run("m", 2, "infrastructure_failure"), _run("m", 3, "completed_pass", True)]
    runs += [_run("i", r, "interface_runtime_failure", False) for r in (1, 2, 3)]
    labels = {c: ext.outcome(runs, "77178370", c, "buildings")["label"] for c in ("p", "f", "u", "m", "i")}
    assert labels == {"p": "pass", "f": "fail", "u": "unstable", "m": "unresolved", "i": "fail"}

    def contract(rows):
        monkeypatch.setattr(ext, "contract_cache", lambda case: rows)

    row = {"check_id": "buildings", "category": "original", "q1_frozen_accepted": True, "q4_expected_matches_assets": True}
    original_fails = [_run("original", r, "behavioral_failure", False) for r in (1, 2, 3)]
    contract([row])
    assert ext.qualification("77178370", original_fails)["buildings"]["status"] == "qualified"
    original_passes = [_run("original", r, "completed_pass", True) for r in (1, 2, 3)]
    assert ext.qualification("77178370", original_passes)["buildings"]["status"] == "not_reproducing"
    contract([{**row, "q1_frozen_accepted": False}])
    assert ext.qualification("77178370", original_fails)["buildings"]["status"] == "oracle_invalid"
    contract([{**row, "q4_expected_matches_assets": False}])
    assert ext.qualification("77178370", original_fails)["buildings"]["status"] == "oracle_invalid"
    contract([row])
    mixed = [_run("original", 1, "behavioral_failure", False), _run("original", 2, "completed_pass", True),
             _run("original", 3, "behavioral_failure", False)]
    assert ext.qualification("77178370", mixed)["buildings"]["status"] == "unresolved"


def test_admissibility_then_verdicts():
    comp = {"without": "a", "with": "b"}
    coherent = {"a": "coherent", "b": "coherent"}
    quals = {"c": {"status": "qualified"}}
    isolated = {"isolated": True}
    assert ext.admissibility(comp, coherent, isolated, quals, [], False) == ("admissible", [])
    assert ext.admissibility(comp, {**coherent, "a": "incompatible_fragment"}, isolated, quals, [], False)[0] == "interface_dependency_diagnostic"
    assert ext.admissibility(comp, coherent, isolated, quals, [], True)[0] == "interface_dependency_diagnostic"
    assert ext.admissibility(comp, coherent, {"isolated": False}, quals, [], False)[0] == "inadmissible_not_isolated"
    assert ext.admissibility(comp, coherent, isolated, {"c": {"status": "oracle_invalid"}}, [], False)[0] \
        == "inadmissible_unqualified_required_check"
    mismatched = [{"input_id": "x", "repetition": 1, "status": "completed_pass", "fingerprint_parts": {"oracle_version": "1"}},
                  {"input_id": "x", "repetition": 1, "status": "completed_pass", "fingerprint_parts": {"oracle_version": "2"}}]
    assert ext.admissibility(comp, coherent, isolated, quals, mismatched, False)[0] == "inadmissible_conditions_not_matched"
    assert ext.contribution_verdict("adequate", "inadequate") == "required_in_context"
    assert ext.contribution_verdict("adequate", "adequate") == "removable_in_context"
    assert ext.contribution_verdict("adequate", "unresolved") == "unresolved_in_context"
    assert ext.contribution_verdict("inadequate", "adequate") == "not_assessed_parent_not_adequate"


def _adeq(values):
    return {name: {"adequacy": value, "checks": {}} for name, value in values.items()}


def test_decision_record():
    configs = CONFIGS["79343179"]
    coh = {name: "coherent" for name in configs}
    values = {name: "inadequate" for name in configs}
    values.update({"baseline": "adequate", "L1L2L3": "adequate", "L1": "unresolved"})
    decision = ext._decision("79343179", configs, coh, _adeq(values), {}, [])
    assert decision["retained_candidate"] == "L1L2L3"
    assert decision["wording"] == "smaller action set, same module scope"
    assert decision["modules_before"] == decision["modules_after"] == 1
    assert (decision["actions_before"], decision["actions_after"]) == (4, 3), "DV counts as an action"
    assert decision["unresolved_candidates"] == ["L1"]

    none = ext._decision("79343179", configs, coh, _adeq({name: "inadequate" for name in configs}), {}, [])
    assert none["decision"] == "no_adequate_candidate" and none["retained_candidate"] is None

    pdf = CONFIGS["78366661"]
    tie = {name: "inadequate" for name in pdf}
    tie.update({"baseline": "adequate", "N+P1": "adequate"})
    kept = ext._decision("78366661", pdf, {n: "coherent" for n in pdf}, _adeq(tie), {}, [])
    assert kept["decision"] == "retained" and kept["retained_candidate"] == "baseline", "N counts, so N+P1 is larger"

    synthetic = {"original": pdf["original"], "baseline": pdf["baseline"],
                 "x": {"source": "", "actions": ["P1"]}, "y": {"source": "", "actions": ["R"]}}
    split = ext._decision("78366661", synthetic, {n: "coherent" for n in synthetic},
                          _adeq({"original": "inadequate", "baseline": "inadequate", "x": "adequate", "y": "adequate"}), {}, [])
    assert split["decision"] == "unresolved_choice" and split["tied_candidates"] == ["x", "y"]


def test_installed_probes_are_not_observations():
    run = {"case": "76906469", "configuration": "original"}
    events = [{"seq": 1, "kind": "probe_installed", "boundary": "tools"},
              {"seq": 2, "kind": "probe_installed", "boundary": "memory"},
              {"seq": 3, "kind": "memory_before", "boundary": "memory"},
              {"seq": 4, "kind": "request_prepared", "boundary": "chat_request"},
              {"seq": 5, "kind": "backend_attempt", "boundary": "network_attempt"},
              {"seq": 6, "kind": "parser", "boundary": "agent_parsers"}]
    states = ext.observed_boundary_states(run, events)
    assert states == {"memory": "observed", "chat_request": "observed", "network_attempt": "observed", "agent_parsers": "observed"}
    assert "tools" not in states


def test_resume():
    cells = [{"case": "c", "configuration": "k", "input_id": "i", "repetition": rep, "probe": True} for rep in (1, 2, 3)]

    def prepare(cell):
        parts = {"repetition": cell["repetition"], "v": 1}
        return {}, {}, parts

    def record(cell, version):
        parts = {"repetition": cell["repetition"], "v": version}
        return {**cell, "fingerprint": ext.sha256_text(json.dumps(parts, sort_keys=True))}

    complete = [record(c, 1) for c in cells]
    assert [p[0] for p in ext.plan_cells(cells, complete, prepare)] == ["skip", "skip", "skip"]
    changed = [record(cells[0], 2)] + complete[1:]
    assert [p[0] for p in ext.plan_cells(cells, changed, prepare)][0] == "mismatch"
    partial = complete[:1]
    assert [p[0] for p in ext.plan_cells(cells, partial, prepare)] == ["skip", "run", "run"]


def test_title_scorer_v2_normalizes_typography():
    expected, catalog = ["Pirates of the Caribbean: At World's End", "Spider-Man 3"], ["Pirates of the Caribbean: At World's End",
                                                                                    "Spider-Man 3", "Tangled"]
    answer = "Pirates of the Caribbean: At World\u2019s End, Spider\u2011Man 3"
    assert pr._score_titles(answer, expected, catalog)["passed"] is False
    assert ext.score_titles_v2(answer, expected, catalog) == {"missing": [], "added": [], "passed": True}
    assert ext.score_titles_v2(answer + ", Tangled", expected, catalog)["added"] == ["Tangled"]


def test_load_runs_reads_rescored_checks(tmp_path):
    run = {"run_id": "x", "case": "78383658", "status": "behavioral_failure", "checks": {"action": {"passed": False}}}
    (tmp_path / "runs.jsonl").write_text(json.dumps(run) + "\n")
    assert ext.load_runs(tmp_path)[0]["status"] == "behavioral_failure"
    rescored = {"run_id": "x", "scorer": "titles_v2", "checks": {"action": {"passed": True}}, "status": "completed_pass"}
    (tmp_path / "rescored_checks.jsonl").write_text(json.dumps(rescored) + "\n")
    loaded = ext.load_runs(tmp_path)[0]
    assert loaded["status"] == "completed_pass" and loaded["status_v1"] == "behavioral_failure"
    assert loaded["checks_v1"] == {"action": {"passed": False}}
    assert json.loads((tmp_path / "runs.jsonl").read_text())["status"] == "behavioral_failure", "runs.jsonl stays as recorded"


def test_boundary_states_ignore_installed_probes():
    events = [{"seq": 1, "kind": "probe_installed", "boundary": "tools"}, {"seq": 2, "kind": "memory_before", "boundary": "memory"}]
    states = instrument.boundary_states(events, {"expected": ["memory"], "optional": ["tools"], "removed": [], "order": ["memory", "tools"]})
    assert states == {"memory": "observed"}
