"""Project-neutral Tribunal command dispatcher."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from tribunal.discovery import discover


def load_project(path: Path) -> dict:
    project = json.loads(path.read_text(encoding="utf-8"))
    if project.get("schema") != 1 or not isinstance(project.get("entrypoint"), str):
        raise RuntimeError("invalid Tribunal project manifest")
    return project


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a registered Arma mod suite through Tribunal.")
    parser.add_argument("--project", type=Path, required=True, help="path to a Tribunal project manifest")
    parser.add_argument("command", nargs="?", default="scenarios")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    project_path = args.project.resolve()
    project = load_project(project_path)
    if args.command == "scenarios":
        roots = [project_path.parent / value for value in project.get("scenario_roots", [])]
        for scenario in discover(roots).values():
            print(f"{scenario.tier}\t{scenario.identifier}")
        return 0
    entrypoint = project_path.parent / project["entrypoint"]
    return subprocess.run([str(entrypoint), args.command, *args.args], cwd=project_path.parent).returncode


if __name__ == "__main__":
    raise SystemExit(main())
