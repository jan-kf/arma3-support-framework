"""Discovery of mod-provided Tribunal scenarios without product coupling."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from tribunal.runner.model import Scenario


def load_scenario(path: Path) -> Scenario:
    spec = importlib.util.spec_from_file_location(f"tribunal_scenario_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load Tribunal scenario: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    scenario = getattr(module, "TRIBUNAL_SCENARIO", None)
    if not isinstance(scenario, Scenario):
        raise RuntimeError(f"{path} does not export a Tribunal Scenario")
    return scenario


def discover(paths: list[Path]) -> dict[str, Scenario]:
    scenarios: dict[str, Scenario] = {}
    for root in paths:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.py")):
            if path.name.startswith("_"):
                continue
            scenario = load_scenario(path)
            if scenario.identifier in scenarios:
                raise RuntimeError(f"duplicate Tribunal scenario: {scenario.identifier}")
            scenarios[scenario.identifier] = scenario
    return scenarios
