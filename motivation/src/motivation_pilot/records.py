"""Append-only execution records. A missing row is never a failure."""

from __future__ import annotations

import json
from pathlib import Path

STATUSES = (
    "completed_pass",
    "completed_task_failure",
    "integration_error",
    "infrastructure_error",
    "budget_stopped",
    "not_run",
    "unknown",
)


def append_record(path: Path, record: dict) -> None:
    if record.get("status") not in STATUSES:
        raise ValueError(f"unknown status {record.get('status')}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def summarize(planned_ids: list[str], records: list[dict]) -> dict:
    """Missing executions stay unknown. They are not counted as task failures."""
    done = {row["execution_id"] for row in records if row.get("execution_id")}
    missing = [item for item in planned_ids if item not in done]
    return {
        "planned": len(planned_ids),
        "completed": len([item for item in planned_ids if item in done]),
        "missing": len(missing),
        "missing_status": "unknown",
        "missing_counted_as_failure": False,
    }
