"""Generic tier/scenario metadata; no mod feature names live here."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TierPlan:
    name: str
    server_expected: frozenset[str]
    client_expected: frozenset[str]
    gameplay: bool = False
    selected: frozenset[str] = frozenset()
    project_mods: bool = False


@dataclass(frozen=True)
class Scenario:
    """A mod-provided, in-mission scenario consumed by a Tribunal runner."""
    identifier: str
    tier: str
    server_expected: frozenset[str]
    client_expected: frozenset[str]
    server_sqf: str
    client_sqf: str
    requires_project_mods: bool = True
    metadata: dict[str, str] = field(default_factory=dict)
