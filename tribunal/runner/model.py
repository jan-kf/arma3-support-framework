"""Generic tier/scenario metadata; no mod feature names live here."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


TEST_TYPES = frozenset({"specification", "characterization", "tooling"})
REVIEW_OUTCOMES = frozenset({
    "KEEP AS-IS AND SPEC-TEST",
    "KEEP + CHARACTERIZE ENGINE REQUIREMENT",
    "REFINE BEFORE PERMANENT COVERAGE",
    "REWRITE BEFORE PERMANENT COVERAGE",
    "NEEDS EXPERIMENTATION",
    "DEFER / insufficient value",
})


@dataclass(frozen=True)
class CharacterizedBehavior:
    """A mechanism frozen only because evidence proves it is necessary."""

    description: str
    reason: str
    evidence: str
    alternative_tested: str
    outcome: str

    def __post_init__(self) -> None:
        if not all((self.description, self.reason, self.evidence, self.alternative_tested, self.outcome)):
            raise ValueError("characterized behavior requires description, reason, evidence, alternative, and outcome")


@dataclass(frozen=True)
class ScenarioReview:
    """Small, durable record of why a permanent scenario exists."""

    test_type: str
    behavior_contract: str
    outcome: str
    rationale: str
    dependencies: tuple[str, ...] = ()
    evidence_types: frozenset[str] = frozenset()
    locality_requirements: str = ""
    characterized_behaviors: tuple[CharacterizedBehavior, ...] = ()

    def __post_init__(self) -> None:
        if self.test_type not in TEST_TYPES:
            raise ValueError(f"invalid Tribunal test type: {self.test_type}")
        if self.outcome not in REVIEW_OUTCOMES:
            raise ValueError(f"invalid Tribunal review outcome: {self.outcome}")
        if not self.behavior_contract or not self.rationale:
            raise ValueError("scenario review requires a behavior contract and rationale")
        if self.test_type == "characterization" and not self.characterized_behaviors:
            raise ValueError("characterization scenarios require evidence-backed characterized behavior")


@dataclass(frozen=True)
class ClientIdentity:
    """Stable logical identity for one independently authenticated client."""

    name: str
    profile_name: str
    steam_home: Path
    address_offset: int
    diagnostic_vnc_port: int | None = None

    def __post_init__(self) -> None:
        if not self.name.startswith("client-") or not self.name[7:].replace("-", "").isalnum():
            raise ValueError(f"invalid Tribunal client identity: {self.name}")
        if self.address_offset < 2 or self.address_offset > 253:
            raise ValueError("client address offset must be between 2 and 253")


def client_identity_map(clients: tuple[ClientIdentity, ...]) -> Mapping[str, ClientIdentity]:
    """Validate and key client resources without assuming a fixed client count."""

    keyed = {client.name: client for client in clients}
    if len(keyed) != len(clients):
        raise ValueError("duplicate Tribunal client identity")
    offsets = {client.address_offset for client in clients}
    homes = {client.steam_home for client in clients}
    if len(offsets) != len(clients):
        raise ValueError("duplicate Tribunal client address offset")
    if len(homes) != len(clients):
        raise ValueError("each runnable Steam client requires an independent home")
    return MappingProxyType(keyed)


@dataclass(frozen=True)
class TierPlan:
    name: str
    server_expected: frozenset[str]
    client_expected: frozenset[str]
    gameplay: bool = False
    selected: frozenset[str] = frozenset()
    project_mods: bool = False


@dataclass(frozen=True)
class MissionEntity:
    """Validated typed Eden entity with mission.sqm X/ASL-altitude/world-Y position."""

    name: str
    class_name: str
    addon: str
    data_type: str
    position: tuple[float, float, float]

    def __post_init__(self) -> None:
        for label, value in (("name", self.name), ("class_name", self.class_name), ("addon", self.addon)):
            if not value or not value.replace("_", "").isalnum():
                raise ValueError(f"mission entity {label} must contain only letters, numbers, or underscores")
        if self.data_type not in {"Logic", "Object"}:
            raise ValueError("mission entity data_type must be Logic or Object")
        if len(self.position) != 3 or any(not isinstance(value, (int, float)) or value != value or abs(value) > 1e7 for value in self.position):
            raise ValueError("mission entity position must contain three finite scalars")


@dataclass(frozen=True)
class MissionSync:
    """A typed Eden Sync connection between two named mission entities."""

    source: str
    target: str

    def __post_init__(self) -> None:
        if not self.source or not self.target or self.source == self.target:
            raise ValueError("mission sync requires two distinct named entities")


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
    client_expected_by_identity: Mapping[str, frozenset[str]] = field(default_factory=dict)
    client_sqf_by_identity: Mapping[str, str] = field(default_factory=dict)
    review: ScenarioReview | None = None
    mission_entities: tuple[MissionEntity, ...] = ()
    mission_syncs: tuple[MissionSync, ...] = ()
    evidence_contract: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        names = [entity.name for entity in self.mission_entities]
        if len(set(names)) != len(names):
            raise ValueError("scenario mission entity names must be unique")
        known = set(names)
        links = set()
        for sync in self.mission_syncs:
            if sync.source not in known or sync.target not in known:
                raise ValueError("mission sync must reference named scenario entities")
            key = (sync.source, sync.target)
            if key in links:
                raise ValueError("duplicate mission sync")
            links.add(key)
        if self.evidence_contract:
            required = {"scenario", "knowledge_subject", "arms", "causal_relationships", "propositions"}
            missing = required - set(self.evidence_contract)
            if missing:
                raise ValueError(f"scenario evidence contract missing: {', '.join(sorted(missing))}")
            arm_keys = [arm.get("key") for arm in self.evidence_contract["arms"]]
            if any(not key for key in arm_keys) or len(arm_keys) != len(set(arm_keys)):
                raise ValueError("scenario evidence arms require unique keys")

    def expected_for(self, identity: str) -> frozenset[str]:
        """Return identity-specific assertions, retaining client-a compatibility."""

        return self.client_expected_by_identity.get(identity, self.client_expected if identity == "client-a" else frozenset())

    def sqf_for(self, identity: str) -> str:
        """Return identity-specific SQF, retaining client-a compatibility."""

        return self.client_sqf_by_identity.get(identity, self.client_sqf if identity == "client-a" else "")
