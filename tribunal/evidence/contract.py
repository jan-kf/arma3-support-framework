"""Validation, stable identity, and emission for tribunal.evidence/v1.

The interchange is plain JSON and deliberately has no dependency on Tribunal's
runtime. This module is the producer-side reference implementation; consumers
must validate the published JSON contract rather than import this code.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from tribunal.reporting.artifacts import atomic_json


CONTRACT_SCHEMA = "tribunal.evidence/v1"
PACKAGE_NAME = "evidence-package.v1.json"
EXECUTION_STATES = {"completed", "failed_to_execute", "cancelled"}
OUTCOMES = {"positive", "negative", "mixed", "inconclusive", "not_applicable"}
PUBLICATION_STATES = {"accepted", "candidate", "superseded", "corrected"}
ARM_ROLES = {"treatment", "negative_control", "positive_control", "baseline", "counterfactual", "replicate"}
PAIR_RELATIONS = {"COMPARES_WITH", "CONTROLS_FOR", "CAUSAL_PAIR_WITH", "REPLICATES"}
VALUE_TYPES = {
    "boolean", "integer", "float", "string", "enum", "quantity", "vector",
    "position", "collection", "object_identity", "event", "state_transition",
    "record", "custom",
}
ASSERTION_TYPES = {
    "equality", "inequality", "within_tolerance", "contains", "not_contains",
    "event_occurred", "event_absent", "state_equals", "count_equals",
    "object_exists", "object_absent", "custom",
}
EVALUATION_OUTCOMES = {"demonstrated", "counterexample_observed", "not_established", "inconclusive"}


class EvidenceContractError(ValueError):
    """The package is structurally or semantically unsafe to publish/ingest."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def content_id(namespace: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_bytes(value)).hexdigest()
    return f"urn:tribunal:{namespace}:sha256:{digest}"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(record: dict[str, Any], fields: tuple[str, ...], where: str) -> None:
    missing = [field for field in fields if field not in record or record[field] in (None, "")]
    if missing:
        raise EvidenceContractError(f"{where} missing required fields: {', '.join(missing)}")


def _unique(records: list[dict[str, Any]], where: str) -> set[str]:
    ids = [record.get("id") for record in records]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise EvidenceContractError(f"{where} IDs must be present and unique")
    return set(ids)


def integrity_payload(package: dict[str, Any]) -> dict[str, Any]:
    payload = dict(package)
    payload.pop("integrity", None)
    return payload


def seal_package(package: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(package)
    payload_hash = hashlib.sha256(canonical_bytes(integrity_payload(sealed))).hexdigest()
    sealed["integrity"] = {
        "algorithm": "sha256",
        "payload_sha256": payload_hash,
        "canonicalization": "tribunal-canonical-json/v1",
    }
    return sealed


def validate_package(package: dict[str, Any], *, verify_integrity: bool = True) -> None:
    """Validate required v1 semantics while tolerating unknown optional fields."""
    _require(package, ("schema", "package_id", "package_revision", "run", "scenarios", "participants", "context", "source_snapshots", "artifacts", "observations", "assertions", "experimental_arms", "causal_relationships", "proposition_evaluations", "publication"), "package")
    if package["schema"] != CONTRACT_SCHEMA:
        raise EvidenceContractError(f"unsupported schema: {package['schema']!r}")
    if not isinstance(package["package_revision"], int) or package["package_revision"] < 1:
        raise EvidenceContractError("package_revision must be a positive integer")

    run = package["run"]
    _require(run, ("id", "started_at", "finished_at", "execution_state", "outcome", "runner_status", "mode"), "run")
    if run["execution_state"] not in EXECUTION_STATES or run["outcome"] not in OUTCOMES:
        raise EvidenceContractError("invalid run execution_state/outcome")
    if run["execution_state"] != "completed" and run["outcome"] not in {"inconclusive", "not_applicable"}:
        raise EvidenceContractError("failed/cancelled execution cannot claim a scientific result")

    if not package["scenarios"] or not package["participants"] or not package["source_snapshots"]:
        raise EvidenceContractError("package requires scenarios, participants, and source snapshots")
    scenario_ids = _unique(package["scenarios"], "scenario")
    for scenario in package["scenarios"]:
        _require(scenario, ("id", "version", "feature_family", "name", "definition"), f"scenario {scenario.get('id')}")
    participant_ids = _unique(package["participants"], "participant")
    for participant in package["participants"]:
        _require(participant, ("id", "role", "runtime"), f"participant {participant.get('id')}")
    artifact_ids = _unique(package["artifacts"], "artifact")
    for artifact in package["artifacts"]:
        _require(artifact, ("id", "type", "sha256", "reference", "description"), f"artifact {artifact.get('id')}")
        if len(artifact["sha256"]) != 64:
            raise EvidenceContractError(f"artifact {artifact['id']} has invalid sha256")
        if artifact.get("participant_id") and artifact["participant_id"] not in participant_ids:
            raise EvidenceContractError(f"artifact {artifact['id']} references unknown participant")
    snapshot_ids = _unique(package["source_snapshots"], "source snapshot")
    for snapshot in package["source_snapshots"]:
        _require(snapshot, ("id", "repository", "commit", "tree_state", "files"), f"source snapshot {snapshot.get('id')}")
        for source_file in snapshot["files"]:
            _require(source_file, ("path", "sha256"), f"source file in {snapshot['id']}")

    arm_ids = _unique(package["experimental_arms"], "experimental arm")
    for arm in package["experimental_arms"]:
        _require(arm, ("id", "scenario_id", "role", "description"), f"arm {arm.get('id')}")
        if arm["scenario_id"] not in scenario_ids or arm["role"] not in ARM_ROLES:
            raise EvidenceContractError(f"invalid arm {arm['id']}")
    observation_ids = _unique(package["observations"], "observation")
    for observation in package["observations"]:
        _require(observation, ("id", "scenario_id", "type", "value", "observed_at", "participant_id", "artifact_ids"), f"observation {observation.get('id')}")
        if observation["scenario_id"] not in scenario_ids or observation["participant_id"] not in participant_ids:
            raise EvidenceContractError(f"observation {observation['id']} has unknown scenario/participant")
        if observation["type"] not in VALUE_TYPES:
            raise EvidenceContractError(f"observation {observation['id']} has invalid type")
        if observation.get("arm_id") and observation["arm_id"] not in arm_ids:
            raise EvidenceContractError(f"observation {observation['id']} has unknown arm")
        if not set(observation["artifact_ids"]) <= artifact_ids:
            raise EvidenceContractError(f"observation {observation['id']} has unknown artifact")
    assertion_ids = _unique(package["assertions"], "assertion")
    for assertion in package["assertions"]:
        _require(assertion, ("id", "definition_id", "scenario_id", "type", "expected", "observed", "result", "observation_ids", "artifact_ids"), f"assertion {assertion.get('id')}")
        if assertion["scenario_id"] not in scenario_ids or assertion["type"] not in ASSERTION_TYPES:
            raise EvidenceContractError(f"invalid assertion {assertion['id']}")
        if assertion["result"] not in {"pass", "fail", "error", "not_evaluated"}:
            raise EvidenceContractError(f"invalid assertion result {assertion['id']}")
        if not set(assertion["observation_ids"]) <= observation_ids or not set(assertion["artifact_ids"]) <= artifact_ids:
            raise EvidenceContractError(f"assertion {assertion['id']} has dangling evidence references")
    _unique(package["causal_relationships"], "causal relationship")
    for relation in package["causal_relationships"]:
        _require(relation, ("id", "relation", "source_arm_id", "target_arm_id", "controlled_dimensions"), f"causal relationship {relation.get('id')}")
        if relation["relation"] not in PAIR_RELATIONS or relation["source_arm_id"] not in arm_ids or relation["target_arm_id"] not in arm_ids:
            raise EvidenceContractError(f"invalid causal relationship {relation['id']}")
    if package["proposition_evaluations"]:
        _require(package, ("knowledge_subject",), "package with proposition evaluations")
        _require(package["knowledge_subject"], ("key", "label", "kind", "biki_context"), "knowledge_subject")
    _unique(package["proposition_evaluations"], "proposition evaluation")
    for evaluation in package["proposition_evaluations"]:
        _require(evaluation, ("id", "proposition_id", "text", "outcome", "intended_use", "observation_ids", "assertion_ids", "rationale"), f"evaluation {evaluation.get('id')}")
        if evaluation["outcome"] not in EVALUATION_OUTCOMES:
            raise EvidenceContractError(f"invalid evaluation outcome {evaluation['id']}")
        if not set(evaluation["observation_ids"]) <= observation_ids or not set(evaluation["assertion_ids"]) <= assertion_ids:
            raise EvidenceContractError(f"evaluation {evaluation['id']} has dangling evidence references")

    publication = package["publication"]
    _require(publication, ("status", "published_at", "publisher", "synthetic"), "publication")
    if publication["status"] not in PUBLICATION_STATES:
        raise EvidenceContractError("invalid publication status")
    if package["package_revision"] > 1 and not package.get("supersedes_package_id"):
        raise EvidenceContractError("replacement package must identify superseded package")
    if verify_integrity:
        integrity = package.get("integrity")
        _require(integrity or {}, ("algorithm", "payload_sha256", "canonicalization"), "integrity")
        expected = hashlib.sha256(canonical_bytes(integrity_payload(package))).hexdigest()
        if integrity["algorithm"] != "sha256" or integrity["payload_sha256"] != expected:
            raise EvidenceContractError("package integrity mismatch")


def load_and_validate(path: Path) -> dict[str, Any]:
    package = json.loads(path.read_text(encoding="utf-8"))
    validate_package(package)
    return package


def write_immutable_package(path: Path, package: dict[str, Any]) -> Path:
    sealed = seal_package(package)
    validate_package(sealed)
    if path.exists():
        existing = path.read_bytes()
        proposed = json.dumps(sealed, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        if existing != proposed:
            raise EvidenceContractError(f"published evidence package is immutable: {path}")
        return path
    atomic_json(path, sealed)
    return path


def _artifact(run_dir: Path, relative: str, artifact_type: str, description: str, participant_id: str | None = None) -> dict[str, Any] | None:
    path = run_dir / relative
    if not path.is_file():
        return None
    digest = file_sha256(path)
    record: dict[str, Any] = {
        "id": f"urn:tribunal:artifact:sha256:{digest}",
        "type": artifact_type,
        "sha256": digest,
        "reference": relative,
        "description": description,
    }
    if participant_id:
        record["participant_id"] = participant_id
    return record


def build_execution_package(run_dir: Path, manifest: dict[str, Any], result: dict[str, Any]) -> Path:
    """Emit a generic v1 package from the normal completed-run path.

    Legacy line assertions are represented as explicit custom boolean
    observations. Scenarios may later enrich/replace these with typed evidence;
    no proposition evaluation is invented here.
    """
    run_id = result["run_id"]
    test_plan = manifest.get("test_plan") or {}
    scenario_names = test_plan.get("scenarios") or [f"run-family:{manifest.get('mode', 'unknown')}"]
    evidence_contracts = test_plan.get("evidence_contracts") or {}
    scenarios = [
        evidence_contracts.get(name, {}).get("scenario", {
            "id": name,
            "version": 1,
            "feature_family": name.split(".")[0].split("-")[0],
            "name": name,
            "definition": {"kind": "runner-selection", "reference": "manifest.json#test_plan"},
        })
        for name in scenario_names
    ]
    default_runner_scenario = scenario_names[0]
    default_scenario = scenarios[0]["id"]
    participants = [
        {"id": "server", "role": "dedicated_server", "runtime": manifest.get("arma_server", {})},
        *[
            {"id": client_id, "role": "player_client", "runtime": {**details, **manifest.get("arma_client", {})}}
            for client_id, details in sorted((manifest.get("clients") or {"client-a": {}}).items())
        ],
    ]
    artifacts = [
        item for item in (
            _artifact(run_dir, "manifest.json", "run_manifest", "Original Tribunal run manifest"),
            _artifact(run_dir, "results.json", "assertion_report", "Original Tribunal terminal result"),
            _artifact(run_dir, "server/server.rpt", "server_log", "Dedicated-server RPT", "server"),
            _artifact(run_dir, "client-a/client.rpt", "client_log", "Player-client RPT", "client-a"),
        ) if item
    ]
    result_artifact = next((item["id"] for item in artifacts if item["type"] == "assertion_report"), artifacts[0]["id"] if artifacts else None)
    observations = []
    assertions = []
    for index, record in enumerate(result.get("assertions", [])):
        observation_id = f"urn:tribunal:observation:{run_id}:{index}:{record['name']}"
        observations.append({
            "id": observation_id,
            "scenario_id": default_scenario,
            "type": "record",
            "schema_id": "tribunal.legacy-assertion-detail/v1",
            "value": {"predicate_result": record["status"] == "PASS", "detail": record.get("detail", "")},
            "observed_at": result["finished_at"],
            "participant_id": record["origin"],
            "artifact_ids": [result_artifact] if result_artifact else [],
        })
        assertions.append({
            "id": f"urn:tribunal:assertion-result:{run_id}:{index}:{record['name']}",
            "definition_id": f"urn:tribunal:assertion-definition:{record['name']}",
            "scenario_id": default_scenario,
            "type": "custom",
            "expected": True,
            "observed": record["status"] == "PASS",
            "result": record["status"].lower(),
            "observation_ids": [observation_id],
            "artifact_ids": [result_artifact] if result_artifact else [],
        })
    completed = result.get("reason") in {"complete", "assertion_failure"} and result.get("status") in {"PASS", "FAIL"}
    experimental_arms: list[dict[str, Any]] = []
    causal_relationships: list[dict[str, Any]] = []
    proposition_evaluations: list[dict[str, Any]] = []
    knowledge_subject = None
    # Scientific meaning is published only for a literal successful execution
    # of one scenario that supplied an explicit evidence contract. Failed and
    # aggregate runs retain the generic assertion record and cannot overclaim.
    if completed and result.get("status") == "PASS" and len(scenario_names) == 1:
        semantics = evidence_contracts.get(default_runner_scenario)
        if semantics:
            knowledge_subject = semantics["knowledge_subject"]
            assertion_by_name = {
                record["name"]: assertions[index]
                for index, record in enumerate(result.get("assertions", []))
            }
            arm_ids: dict[str, str] = {}
            for arm in semantics["arms"]:
                arm_id = f"urn:tribunal:arm:{run_id}:{arm['key']}"
                arm_ids[arm["key"]] = arm_id
                names = arm.get("assertions", [])
                observation_ids = [assertion_by_name[name]["observation_ids"][0] for name in names]
                for name in names:
                    observations[assertions.index(assertion_by_name[name])]["arm_id"] = arm_id
                experimental_arms.append({
                    "id": arm_id, "scenario_id": default_scenario,
                    "role": arm["role"], "description": arm["description"],
                    "observation_ids": observation_ids,
                })
            for relation in semantics["causal_relationships"]:
                causal_relationships.append({
                    "id": f"urn:tribunal:causal-relationship:{run_id}:{relation['key']}",
                    "relation": relation["relation"],
                    "source_arm_id": arm_ids[relation["source"]],
                    "target_arm_id": arm_ids[relation["target"]],
                    "controlled_dimensions": relation["controlled_dimensions"],
                })
            for proposition in semantics["propositions"]:
                names = proposition["assertions"]
                selected = [assertion_by_name[name] for name in names]
                proposition_evaluations.append({
                    "id": f"urn:tribunal:proposition-evaluation:{run_id}:{proposition['id']}",
                    "proposition_id": proposition["id"], "text": proposition["text"],
                    "outcome": proposition.get("outcome", "demonstrated"),
                    "intended_use": proposition["intended_use"],
                    "observation_ids": [item["observation_ids"][0] for item in selected],
                    "assertion_ids": [item["id"] for item in selected],
                    "rationale": proposition["rationale"],
                })
    package = {
        "schema": CONTRACT_SCHEMA,
        "package_id": f"urn:tribunal:evidence-package:{run_id}:1",
        "package_revision": 1,
        "run": {
            "id": run_id,
            "started_at": manifest["started_at"],
            "finished_at": result["finished_at"],
            "execution_state": "completed" if completed else "failed_to_execute",
            "outcome": ("positive" if result["status"] == "PASS" else "negative") if completed else "inconclusive",
            "runner_status": result["status"],
            "reason": result.get("reason"),
            "mode": manifest.get("mode", "unknown"),
        },
        "scenarios": scenarios,
        "participants": participants,
        "context": {
            "product": "Arma 3",
            "branch": "stable",
            "version": (manifest.get("arma_server") or {}).get("version"),
            "server_build": (manifest.get("arma_server") or {}).get("steam_build_id"),
            "client_build": (manifest.get("arma_client") or {}).get("steam_build_id"),
            "session": "multiplayer",
            "server_kind": "dedicated",
            "mods": manifest.get("dependencies", []),
            "mission": manifest.get("fresh_mission"),
        },
        "source_snapshots": [{
            "id": content_id("source-snapshot", {"repository": manifest.get("source_repository", "project"), "commit": manifest["git"]["commit"], "tree_state": "dirty" if manifest["git"].get("dirty") else "clean", "changed_paths": manifest["git"].get("changes", []), "files": [], "builds": manifest.get("builds", [])}),
            "repository": manifest.get("source_repository", "project"),
            "commit": manifest["git"]["commit"],
            "tree_state": "dirty" if manifest["git"].get("dirty") else "clean",
            "changed_paths": manifest["git"].get("changes", []),
            "files": [],
            "builds": manifest.get("builds", []),
        }],
        "artifacts": artifacts,
        "observations": observations,
        "assertions": assertions,
        "experimental_arms": experimental_arms,
        "causal_relationships": causal_relationships,
        "proposition_evaluations": proposition_evaluations,
        "publication": {
            "status": "accepted" if completed else "candidate",
            "published_at": result["finished_at"],
            "publisher": "Tribunal automatic terminal reporter",
            "synthetic": False,
        },
    }
    if knowledge_subject:
        package["knowledge_subject"] = knowledge_subject
    if completed and result.get("status") == "PASS" and len(scenario_names) == 1 and evidence_contracts.get(default_runner_scenario):
        package["unresolved"] = evidence_contracts[default_runner_scenario].get("unresolved", [])
    return package


def emit_execution_package(run_dir: Path, manifest: dict[str, Any], result: dict[str, Any]) -> Path:
    """Build and immutably publish the normal terminal-run package."""
    package = build_execution_package(run_dir, manifest, result)
    return write_immutable_package(run_dir / PACKAGE_NAME, package)
