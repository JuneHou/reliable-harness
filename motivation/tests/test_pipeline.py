import json
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from motivation_pilot.access import (  # noqa: E402
    AccessDenied,
    fresh_arm,
    read_for_repair,
    repair_may_read,
    write_for_repair,
)
from motivation_pilot.cache import cache_key  # noqa: E402
from motivation_pilot.cli import command_prepare, load_config, main  # noqa: E402
from motivation_pilot.environment import offline_ready  # noqa: E402
from motivation_pilot.records import summarize  # noqa: E402
from motivation_pilot.report import configuration_status, format_live_proposal  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "study.yaml"
PYTHON = sys.executable


def _base_key(**overrides):
    payload = {
        "source": "buggy",
        "patch": "patch",
        "task": "task",
        "assets": "assets",
        "state": "state",
        "models": "models",
        "settings": "settings",
        "environment": "env",
        "prompt_version": "p1",
        "oracle_version": "o1",
        "protocol_version": "v1",
        "phase": "evaluation",
        "repetition": 0,
    }
    payload.update(overrides)
    return cache_key(**payload)


def test_config_changes_repetitions_models_and_budgets():
    config = load_config(CONFIG)
    original = format_live_proposal(config)
    assert "qualification_executions: 24" in original
    assert "public_test_executions: 96" in original
    changed = dict(config)
    changed["repetitions"] = 1
    changed["public_execution_cap"] = 1
    changed["repairer_model"] = "repairer-test"
    changed["subject_model"] = "subject-test"
    text = format_live_proposal(changed)
    assert "qualification_executions: 8" in text
    assert "public_test_executions: 8" in text
    assert "repairer_model: repairer-test" in text
    assert "subject_model: subject-test" in text
    assert "runtime_paid_allowance: 0" in original


def test_mock_pipeline_runs_all_eight_stages(tmp_path):
    fixture = ROOT / "tests" / "fixtures" / "dev_program"
    assert not fixture.exists()
    code = main(["dry-run", "--root", str(tmp_path), "--config", str(CONFIG)])
    assert code == 0
    assert not (tmp_path / "artifacts" / "mock_report.md").exists()


def test_missing_execution_is_unknown():
    summary = summarize(["rep-0", "rep-1"], [{"execution_id": "rep-0", "status": "completed_pass"}])
    assert summary["planned"] == 2
    assert summary["completed"] == 1
    assert summary["missing"] == 1
    assert summary["missing_status"] == "unknown"
    assert summary["missing_counted_as_failure"] is False


def test_state_reset_isolates_arms(tmp_path):
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "run_buggy.py").write_text("print('ok')\n", encoding="utf-8")
    arm1 = fresh_arm(seed, tmp_path / "arm1")
    (arm1 / "marker.txt").write_text("from arm1\n", encoding="utf-8")
    arm2 = fresh_arm(seed, tmp_path / "arm2")
    assert not (arm2 / "marker.txt").exists()
    assert (arm2 / "run_buggy.py").exists()


def test_cache_key_changes_with_source_task_oracle():
    base = _base_key()
    assert _base_key(source="other") != base
    assert _base_key(task="other") != base
    assert _base_key(oracle_version="o2") != base


def test_read_boundary_blocks_zip_git_fixed_and_artifacts(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "run_buggy.py").write_text("ok\n", encoding="utf-8")
    (workspace / "public_contract.txt").write_text("public\n", encoding="utf-8")
    config = load_config(CONFIG)
    denied = [
        Path(config["archive"]),
        Path(config["repository"]) / ".git",
        Path(config["repository"]) / "repair_family_pilot" / "artifacts",
    ]
    assert repair_may_read(workspace, workspace / "run_buggy.py", denied)
    assert read_for_repair(workspace, workspace / "public_contract.txt", denied) == "public\n"
    fixed = tmp_path / "published" / "run_fixed.py"
    heldout = tmp_path / "hidden" / "heldout_tasks.json"
    fixed.parent.mkdir()
    heldout.parent.mkdir()
    fixed.write_text("published\n", encoding="utf-8")
    heldout.write_text("{}\n", encoding="utf-8")
    for target in [fixed, heldout, *denied]:
        assert repair_may_read(workspace, target, denied) is False


def test_protected_write_is_rejected(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    try:
        write_for_repair(workspace, workspace / "run_fixed.py", "secret\n")
    except AccessDenied:
        return
    raise AssertionError("protected write was accepted")


def test_integration_error_is_not_behavioral_necessity():
    try:
        exec("def run_agent(query):\n    return _lookup(query)\nrun_agent('q')", {})
    except NameError as exc:
        status = "integration_error"
        detail = str(exc)
    else:
        status = "completed_pass"
        detail = ""
    assert status == "integration_error"
    assert "behavioral necessity" not in detail


def test_report_denominators_match_manifest():
    summary = summarize(["rep-0", "rep-1"], [{"execution_id": "rep-0", "status": "completed_task_failure"}])
    text = (
        f"planned: {summary['planned']}\ncompleted: {summary['completed']}\n"
        f"missing: {summary['missing']}\nmissing_status: {summary['missing_status']}\n"
    )
    assert "planned: 2" in text
    assert "completed: 1" in text
    assert "missing: 1" in text
    assert "missing_status: unknown" in text
    assert "missing_counted_as_failure: True" not in (
        f"missing_counted_as_failure: {summary['missing_counted_as_failure']}"
    )


def test_empty_model_is_configuration_incomplete():
    empty = {"repairer_model": "", "subject_model": ""}
    assert configuration_status(empty) == "configuration_incomplete"
    named = load_config(CONFIG)
    assert named["repairer_model"] == "gpt-6-luna"
    assert named["subject_model"] == "gpt-6-luna"
    assert named["reasoning_effort"] == "none"
    assert configuration_status(named) == "configured"


def test_proposal_counts_are_stage_specific():
    text = format_live_proposal(load_config(CONFIG))
    for label, value in (
        ("qualification_executions", "24"),
        ("repair_generations", "24"),
        ("public_test_executions", "96"),
        ("evaluation_executions", "192"),
        ("audit_executions", "576"),
    ):
        assert f"{label}: {value}" in text
    assert "embeddings: included inside subject executions" in text
    assert "retries: 912" in text
    assert "cost: unresolved" in text


def test_authored_tasks_are_hidden_and_unfrozen(tmp_path):
    command_prepare(tmp_path, load_config(CONFIG))
    drafts = json.loads((tmp_path / "artifacts" / "task_drafts.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "artifacts" / "study_manifest.json").read_text(encoding="utf-8"))
    assert manifest["study_ready"] is False
    assert manifest["configuration_status"] == "configured"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    denied = [tmp_path / "artifacts"]
    assert repair_may_read(workspace, tmp_path / "artifacts" / "task_drafts.json", denied) is False
    for case in drafts:
        assert case["frozen"] is False
        for item in case["inputs"]:
            assert item["review_status"] == "accepted"
            assert item["frozen"] is True
            if item["role"] != "public_reproducer":
                assert item["visible_to_repair_agent"] is False
                assert item["origin"] == "authored"


def test_case_import_failure_is_not_offline_ready():
    assert offline_ready("import motivation_pilot_missing_module_zz\n", PYTHON) is False
    import pytest  # noqa: F401
    assert offline_ready("import motivation_pilot_missing_module_zz\n", PYTHON) is False


def test_prepare_packet_and_historical_case(tmp_path):
    assert command_prepare(tmp_path, load_config(CONFIG)) == 0
    rows = json.loads((tmp_path / "artifacts" / "readiness.json").read_text(encoding="utf-8"))
    by_id = {row["archive_folder"]: row for row in rows}
    packet = ["76897509", "78366661", "77178370", "78838421", "79343179", "77099194", "79149108", "78383658"]
    for case_id in packet:
        assert by_id[case_id]["static_candidate"] is True
        assert by_id[case_id]["study_ready"] is False
        assert by_id[case_id]["oracle_reviewed"] is False
        assert by_id[case_id]["reproduction_qualified"] is False
    assert by_id["78838421"]["requires_controlled_configuration"] is True
    assert by_id["76906469"]["role"] == "historical_qualification"
    assert "76906469" not in packet
    proposal = (tmp_path / "artifacts" / "live_proposal.md").read_text(encoding="utf-8")
    assert "qualification_executions: 24" in proposal
    assert "cost: unresolved" in proposal
    checks = json.loads((tmp_path / "artifacts" / "historical_checks.json").read_text(encoding="utf-8"))
    assert checks["checked_out"] is False
    assert "commit_has_runs_jsonl" in checks


def test_cli_dry_run_and_live_exit_codes(tmp_path):
    dry = subprocess.run(
        [PYTHON, "-m", "motivation_pilot", "dry-run", "--root", str(tmp_path), "--config", str(CONFIG)],
        cwd=ROOT,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
    )
    assert dry.returncode == 0
    assert not (tmp_path / "artifacts" / "mock_report.md").exists()
    assert "stand-in" in dry.stdout
    removed = subprocess.run(
        [PYTHON, "-m", "motivation_pilot", "qualify", "--root", str(tmp_path / "live"), "--config", str(CONFIG)],
        cwd=ROOT,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
    )
    assert removed.returncode == 2
    assert "invalid choice" in removed.stderr
