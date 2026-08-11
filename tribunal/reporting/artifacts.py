"""Atomic machine-readable Tribunal artifact writing."""

from __future__ import annotations

import json
import os
from pathlib import Path


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_result(run_dir: Path, result: dict) -> Path:
    path = run_dir / "result.json"
    atomic_json(path, result)
    return path
