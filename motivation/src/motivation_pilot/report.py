"""Case flow, repair evidence, live execution counts, and the decision template."""

from __future__ import annotations

import csv
import json
from pathlib import Path

DECISION_ROWS = (
    ("Baseline usually recovers adequately; little consequential scope variation",
     "Do not claim a demonstrated need for a scope-selection method"),
    ("Failures are mainly bad implementations at sensible targets",
     "Improve repair generation or validation"),
    ("Extra changes cause measurable problems",
     "Investigate sufficient-scope selection and regression-aware repair"),
    ("Module dependencies repeatedly explain consequential targeting mistakes",
     "Investigate module-level dependency reasoning"),
    ("Coherent repairs show complementarity or multiple sufficient routes with different consequences",
     "Pursue the ultimate RQ using structured repair interventions"),
    ("Too few reproducible cases or weak oracles",
     "Improve the empirical setting before comparing methods"),
)


def configuration_status(config: dict) -> str:
    repairer = str(config.get("repairer_model", "")).strip()
    subject = str(config.get("subject_model", "")).strip()
    if not repairer or not subject:
        return "configuration_incomplete"
    return "configured"


def stage_counts(config: dict) -> dict:
    cases = int(config["review_cases"])
    repetitions = int(config["repetitions"])
    public_cap = int(config["public_execution_cap"])
    revisions = int(config["revision_cap"])
    tasks = int(config["tasks_per_case_maximum"])
    arms = int(config["evaluation_arms"])
    subsets = int(config["audit_subsets_maximum"])
    retry_cap = int(config["max_retries_per_execution"])
    qualification = cases * 1 * repetitions
    repair = cases * (1 + revisions)
    public = cases * public_cap
    evaluation = cases * arms * tasks * repetitions
    audit = cases * subsets * tasks * repetitions
    model_using = qualification + repair + public + evaluation + audit
    return {
        "qualification_executions": qualification,
        "repair_generations": repair,
        "public_test_executions": public,
        "evaluation_executions": evaluation,
        "audit_executions": audit,
        "embeddings": "included inside subject executions",
        "retries": model_using * retry_cap,
        "cost": "unresolved",
        "configuration_status": configuration_status(config),
        "repairer_model": config.get("repairer_model", ""),
        "subject_model": config.get("subject_model", ""),
        "runtime_paid_allowance": int(config["runtime_paid_allowance"]),
    }


def format_live_proposal(config: dict) -> str:
    counts = stage_counts(config)
    lines = [
        "configuration_status: " + counts["configuration_status"],
        "repairer_model: " + str(counts["repairer_model"]),
        "subject_model: " + str(counts["subject_model"]),
        "runtime_paid_allowance: " + str(counts["runtime_paid_allowance"]),
        "qualification_executions: " + str(counts["qualification_executions"]),
        "repair_generations: " + str(counts["repair_generations"]),
        "public_test_executions: " + str(counts["public_test_executions"]),
        "evaluation_executions: " + str(counts["evaluation_executions"]),
        "audit_executions: " + str(counts["audit_executions"]),
        "embeddings: " + counts["embeddings"],
        "retries: " + str(counts["retries"]),
        "cost: " + counts["cost"],
        "",
    ]
    return "\n".join(lines)


def format_decision_template() -> str:
    lines = ["finding | next direction | observation", "---|---|---"]
    for finding, direction in DECISION_ROWS:
        lines.append(f"{finding} | {direction} | ")
    return "\n".join(lines) + "\n"


def write_inventory_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "archive_folder", "name", "component_category_count", "physical_module_count",
        "repair_mechanism_count", "role", "requires_controlled_configuration",
        "static_candidate", "oracle_reviewed", "oracle_review_status", "offline_ready",
        "reproduction_qualified", "study_ready", "assertion_names", "missing_imports",
        "has_buggy", "has_fixed", "evidential_role",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_case_flow(rows: list[dict]) -> str:
    header = "archive_folder | role | static_candidate | oracle_reviewed | offline_ready | reproduction_qualified | study_ready | limitation"
    body = [header]
    for row in rows:
        limitation = row.get("missing_imports") or row.get("evidential_role") or ""
        body.append(
            " | ".join([
                str(row["archive_folder"]),
                str(row["role"]),
                str(row["static_candidate"]),
                str(row["oracle_reviewed"]),
                str(row["offline_ready"]),
                str(row["reproduction_qualified"]),
                str(row["study_ready"]),
                str(limitation),
            ])
        )
    return "\n".join(body) + "\n"


def denominator_text(summary: dict) -> str:
    return (
        f"planned: {summary['planned']}\n"
        f"completed: {summary['completed']}\n"
        f"missing: {summary['missing']}\n"
        f"missing_status: {summary['missing_status']}\n"
        f"missing_counted_as_failure: {summary['missing_counted_as_failure']}\n"
    )


def attach_roles(rows: list[dict], drafts: list[dict]) -> None:
    by_id = {item["archive_folder"]: item["evidential_role"] for item in drafts}
    for row in rows:
        if row["archive_folder"] in by_id:
            row["evidential_role"] = by_id[row["archive_folder"]]
