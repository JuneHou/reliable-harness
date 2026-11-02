"""Archive inventory and the five readiness stages.

Assertion names from the test AST populate the static-candidate note only.
They do not set oracle_reviewed, offline_ready, reproduction_qualified, or study_ready.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import subprocess
import zipfile
from pathlib import Path

from motivation_pilot.environment import imported_top_levels

REVIEW_PACKET = (
    "76897509",
    "78366661",
    "77178370",
    "78838421",
    "79343179",
    "77099194",
    "79149108",
    "78383658",
)
CONTROLLED_CONFIGURATION = "78838421"
HISTORICAL_CASE = "76906469"
HISTORICAL_COMMIT = "cb39baa2f8793cf9573dc301c5e74a376b7eeb26"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assertion_names(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr.startswith("assert"):
                found.add(node.func.attr)
    return sorted(found)


def case_files(archive: zipfile.ZipFile) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for name in archive.namelist():
        parts = name.split("/")
        if len(parts) < 3 or parts[0] != "AgentDefect" or not parts[1] or name.endswith("/"):
            continue
        grouped.setdefault(parts[1], []).append("/".join(parts[2:]))
    return grouped


def load_component_table(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["archive_folder"]: row for row in csv.DictReader(handle)}


def historical_runs(repository: Path) -> dict:
    working = repository / "repair_family_pilot" / "artifacts" / "donor_tables" / "runs.jsonl"
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{HISTORICAL_COMMIT}:repair_family_pilot/artifacts/donor_tables/runs.jsonl"],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    return {
        "commit": HISTORICAL_COMMIT,
        "working_tree_has_runs_jsonl": working.exists(),
        "commit_has_runs_jsonl": probe.returncode == 0,
        "checked_out": False,
    }


def build_inventory(config: dict) -> tuple[list[dict], dict]:
    archive_path = Path(config["archive"])
    digest = file_sha256(archive_path)
    if digest != config["expected_sha256"]:
        raise SystemExit(f"archive sha256 {digest} does not match the pinned hash")
    table = load_component_table(Path(config["component_table"]))
    python = config.get("python") or None
    import_cache: dict[str, bool] = {}
    rows = []
    with zipfile.ZipFile(archive_path) as archive:
        grouped = case_files(archive)
        for case_id in sorted(grouped):
            names = grouped[case_id]
            base = {Path(item).name for item in names}
            buggy = _read(archive, case_id, "run_buggy.py")
            test = _read(archive, case_id, "test.py")
            coded = table.get(case_id, {})
            has_pair = "run_buggy.py" in base and "run_fixed.py" in base
            imports_ok = False
            missing_imports: list[str] = []
            if buggy is not None:
                imports_ok, missing_imports = _cached_imports(buggy, python, import_cache)
            role = "inventory"
            if case_id == HISTORICAL_CASE:
                role = "historical_qualification"
            elif case_id in REVIEW_PACKET:
                role = "review_packet"
            rows.append({
                "archive_folder": case_id,
                "name": coded.get("name", ""),
                "component_category_count": coded.get("counted_n", ""),
                "physical_module_count": "",
                "repair_mechanism_count": "",
                "role": role,
                "requires_controlled_configuration": case_id == CONTROLLED_CONFIGURATION,
                "static_candidate": has_pair,
                "oracle_reviewed": False,
                "oracle_review_status": "pending_review",
                "offline_ready": bool(has_pair and imports_ok),
                "reproduction_qualified": False,
                "study_ready": False,
                "assertion_names": ",".join(assertion_names(test or "")),
                "missing_imports": ",".join(missing_imports),
                "has_buggy": "run_buggy.py" in base,
                "has_fixed": "run_fixed.py" in base,
                "evidential_role": "",
            })
    checks = historical_runs(Path(config["repository"]))
    checks["archive_sha256"] = digest
    checks["pair_count"] = sum(1 for row in rows if row["has_buggy"] and row["has_fixed"])
    checks["folder_count"] = len(rows)
    return rows, checks


def _cached_imports(source: str, python: str | None, cache: dict[str, bool]) -> tuple[bool, list[str]]:
    import subprocess
    import sys
    executable = python or sys.executable
    missing = []
    for name in imported_top_levels(source):
        if name not in cache:
            result = subprocess.run([executable, "-c", f"import {name}"], capture_output=True, text=True)
            cache[name] = result.returncode == 0
        if not cache[name]:
            missing.append(name)
    return (not missing, missing)


def _read(archive: zipfile.ZipFile, case_id: str, filename: str) -> str | None:
    key = f"AgentDefect/{case_id}/{filename}"
    if key not in archive.namelist():
        return None
    return archive.read(key).decode("utf-8", errors="replace")
