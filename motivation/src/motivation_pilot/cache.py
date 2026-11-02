"""Cache keys include every input that would change an execution."""

from __future__ import annotations

import hashlib
import json

FIELDS = (
    "source",
    "patch",
    "task",
    "assets",
    "state",
    "models",
    "settings",
    "environment",
    "prompt_version",
    "oracle_version",
    "protocol_version",
    "phase",
    "repetition",
)


def cache_key(**kwargs) -> str:
    payload = {field: kwargs[field] for field in FIELDS}
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
