"""Repair reads are limited to the workspace. Writes cannot create the published fix."""

from __future__ import annotations

import shutil
from pathlib import Path


class AccessDenied(PermissionError):
    pass


def repair_may_read(workspace: Path, target: Path, denied_roots: list[Path] | None = None) -> bool:
    workspace = workspace.resolve()
    target = target.resolve()
    if target.name == "run_fixed.py":
        return False
    for root in denied_roots or []:
        root = root.resolve()
        if target == root or root in target.parents:
            return False
    if target != workspace and workspace not in target.parents:
        return False
    return True


def repair_may_write(workspace: Path, target: Path) -> bool:
    workspace = workspace.resolve()
    target = target.resolve()
    if target.name == "run_fixed.py":
        return False
    if target != workspace and workspace not in target.parents:
        return False
    return True


def read_for_repair(workspace: Path, target: Path, denied_roots: list[Path] | None = None) -> str:
    if not repair_may_read(workspace, target, denied_roots):
        raise AccessDenied(str(target))
    return target.read_text(encoding="utf-8")


def write_for_repair(workspace: Path, target: Path, text: str) -> None:
    if not repair_may_write(workspace, target):
        raise AccessDenied(str(target))
    target.write_text(text, encoding="utf-8")


def fresh_arm(seed: Path, dest: Path) -> Path:
    """Copy the seed into a new arm directory so one arm cannot leave files for the next."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(seed, dest)
    return dest
