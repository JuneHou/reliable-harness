"""Case import checks. A successful pytest run does not make a case offline ready."""

from __future__ import annotations

import ast
import subprocess
import sys


def imported_top_levels(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module.split(".")[0])
    return sorted(set(names))


def imports_succeed(source: str, python: str | None = None) -> tuple[bool, list[str]]:
    executable = python or sys.executable
    missing = []
    for name in imported_top_levels(source):
        result = subprocess.run(
            [executable, "-c", f"import {name}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            missing.append(name)
    return (not missing, missing)


def offline_ready(source: str, python: str | None = None) -> bool:
    """True only when this source's imports load. Pytest being installed is irrelevant."""
    ok, _missing = imports_succeed(source, python)
    return ok
