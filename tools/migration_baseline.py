#!/usr/bin/env python3
"""Record or compare Pontifex's migration-safe Tribunal contract inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pontifex_paths import TRIBUNAL_ROOT  # noqa: E402

if str(TRIBUNAL_ROOT) in sys.path:
    sys.path.remove(str(TRIBUNAL_ROOT))
sys.path.insert(0, str(TRIBUNAL_ROOT))

from tribunal.discovery import discover  # noqa: E402
import tribunal.scenarios  # noqa: E402


def inventory(project_path: Path) -> dict:
    project_path = project_path.resolve()
    project = json.loads(project_path.read_text(encoding="utf-8"))
    roots = [project_path.parent / value for value in project["scenario_roots"]]
    framework_root = Path(next(iter(tribunal.scenarios.__path__)))
    scenarios = {**discover([framework_root]), **discover(roots)}
    return {
        "schema": 1,
        "project": project["project"],
        "assertion_prefix": project["assertion_prefix"],
        "scenarios": [
            {
                "id": scenario.identifier,
                "tier": scenario.tier,
                "requires_project_mods": scenario.requires_project_mods,
                "server_assertions": sorted(scenario.server_expected),
                "client_assertions": {
                    "client-a": sorted(scenario.expected_for("client-a")),
                    **{
                        identity: sorted(expected)
                        for identity, expected in sorted(scenario.client_expected_by_identity.items())
                        if identity != "client-a"
                    },
                },
            }
            for scenario in sorted(scenarios.values(), key=lambda item: item.identifier)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("snapshot", "compare"))
    parser.add_argument("--project", type=Path, default=ROOT / "tribunal.project.json")
    parser.add_argument("--baseline", type=Path, default=ROOT / "docs" / "migration-baseline.v1.json")
    args = parser.parse_args()
    current = inventory(args.project)
    if args.command == "snapshot":
        args.baseline.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"recorded {len(current['scenarios'])} scenarios in {args.baseline}")
        return 0
    expected = json.loads(args.baseline.read_text(encoding="utf-8"))
    if current != expected:
        print("migration baseline differs", file=sys.stderr)
        return 1
    print(f"migration baseline equivalent: {len(current['scenarios'])} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
