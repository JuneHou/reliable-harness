"""Commands for the motivation pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from motivation_pilot.inventory import build_inventory
from motivation_pilot.report import (
    attach_roles,
    configuration_status,
    format_decision_template,
    format_live_proposal,
    write_case_flow,
    write_inventory_csv,
)
from motivation_pilot.tasks import draft_tasks


def find_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "configs" / "study.yaml").exists() and (candidate / "pyproject.toml").exists():
            return candidate
    raise SystemExit("run this command from motivation_pilot")


def load_config(path: Path) -> dict:
    data = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = _scalar(value.strip())
    return data


def _scalar(value: str):
    if value in {"", '""', "''"}:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def command_prepare(root: Path, config: dict) -> int:
    rows, checks = build_inventory(config)
    drafts = draft_tasks(config)
    attach_roles(rows, drafts)
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    write_inventory_csv(artifacts / "inventory.csv", rows)
    (artifacts / "readiness.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    (artifacts / "task_drafts.json").write_text(json.dumps(drafts, indent=2) + "\n", encoding="utf-8")
    (artifacts / "frozen_oracles.json").write_text(json.dumps(drafts, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "study_ready": False,
        "configuration_status": configuration_status(config),
        "live_authorized": False,
        "repairer_model": config.get("repairer_model", ""),
        "subject_model": config.get("subject_model", ""),
        "review_packet": [row["archive_folder"] for row in rows if row["role"] == "review_packet"],
    }
    (artifacts / "study_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (artifacts / "historical_checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    (artifacts / "live_proposal.md").write_text(format_live_proposal(config), encoding="utf-8")
    (artifacts / "decision_template.md").write_text(format_decision_template(), encoding="utf-8")
    (artifacts / "case_flow.md").write_text(write_case_flow(rows), encoding="utf-8")
    review_lines = ["# Review of the drafted questions\n"]
    for case in drafts:
        review_lines.append(f"## {case['archive_folder']}\n")
        review_lines.append(case["review_reason"] + "\n")
        review_lines.append(f"What this case can support so far: {case['evidential_role']}.\n")
        for task in case["inputs"]:
            review_lines.append(f"- {task['role']}: {task['text']}\n")
    (artifacts / "task_review.md").write_text("\n".join(review_lines), encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="motivation_pilot")
    parser.add_argument("command", choices=["prepare", "dry-run", "report"])
    parser.add_argument("--config", default="")
    parser.add_argument("--manifest", default="")
    parser.add_argument("--root", default="")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else find_root()
    config_path = Path(args.config) if args.config else root / "configs" / "study.yaml"
    config = load_config(config_path)
    if args.command == "prepare":
        return command_prepare(root, config)
    if args.command == "dry-run":
        print("No stand-in program. The pilot runs through pilot_run.py and the extension.")
        return 0
    if args.command == "report":
        report = root / "artifacts" / "baseline_repairs.json"
        if not report.exists():
            print("No real repair record yet.")
            return 4
        print(report.read_text(encoding="utf-8"), end="")
        return 0
    return 2
