#!/usr/bin/env python3
"""One-time migration of the four accepted knowledge exemplars to v1.

The historical semantic selections come from the accepted arma-knowledge
curation file. Future Tribunal runs use the normal terminal emitter and should
declare structured evidence during scenario authoring instead of using this
migration utility.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tribunal.evidence.contract import (  # noqa: E402
    build_execution_package,
    content_id,
    file_sha256,
    write_immutable_package,
)


SCENARIOS = {
    "aps-eden-activation": (
        "pontifex.advanced-systems.aps.eden_activation",
        "APS typed Eden activation",
        "advanced-systems/aps",
        "source/advanced-systems/tests/tribunal/aps_eden_module.py",
    ),
    "cbr-module-activation": (
        "pontifex.advanced-systems.cbr.module_activation",
        "CBR Eden and Zeus activation",
        "advanced-systems/cbr",
        "source/advanced-systems/tests/tribunal/counter_battery_radar_modules.py",
    ),
    "fabricator-transaction": (
        "pontifex.field-utilities.fabricator.transaction",
        "Fabricator authenticated transaction",
        "field-utilities/fabricator",
        "source/field-utilities/tests/tribunal/fabricator.py",
    ),
    "vigil-whitelist-activation": (
        "pontifex.vigil.asset-whitelist.activation",
        "Vigil whitelist Eden and Zeus activation",
        "vigil/asset-whitelist",
        "source/visual-support-tablet/tests/tribunal/vigil_whitelist_modules.py",
    ),
}


def artifact(root: Path, relative: str, kind: str, description: str) -> dict:
    digest = file_sha256(root / relative)
    return {
        "id": f"urn:tribunal:artifact:sha256:{digest}",
        "type": kind,
        "sha256": digest,
        "reference": relative,
        "description": description,
    }


def arm_role(observation: dict) -> str:
    if observation["role"] == "NEGATIVE_CONTROL" or "control" in observation["key"]:
        return "negative_control"
    return "treatment"


def convert(root: Path, exemplar: dict) -> dict:
    run_id = exemplar["run_id"]
    run_dir = root / "runs" / run_id
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    result = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    package = build_execution_package(run_dir, manifest, result)
    scenario_id, scenario_name, family, scenario_path = SCENARIOS[exemplar["key"]]
    package["scenarios"] = [{
        "id": scenario_id,
        "version": 1,
        "feature_family": family,
        "name": scenario_name,
        "definition": {
            "kind": "source_snapshot",
            "reference": scenario_path,
            "protocol_revision": exemplar["experiment"]["protocol_revision"],
            "legacy_experiment_key": exemplar["experiment"]["key"],
        },
    }]

    review_record = artifact(root, exemplar["review"], "accepted_review", "Accepted semantic review and false-PASS boundary")
    scenario_record = artifact(root, scenario_path, "scenario_definition", "Exact Tribunal scenario definition")
    package["artifacts"].extend([review_record, scenario_record])
    snapshot = package["source_snapshots"][0]
    snapshot["repository"] = "pontifex"
    snapshot["files"] = [
        {"path": scenario_path, "sha256": scenario_record["sha256"]},
        {"path": exemplar["review"], "sha256": review_record["sha256"]},
    ]
    snapshot["id"] = content_id("source-snapshot", {key: value for key, value in snapshot.items() if key != "id"})

    result_artifact = next(item["id"] for item in package["artifacts"] if item["type"] == "assertion_report")
    assertion_rows = {item["name"]: item for item in result["assertions"] if item["name"] in {
        name for observation in exemplar["observations"] for name in observation["assertions"]
    }}
    observations = []
    assertions = []
    observation_assertions: dict[str, list[str]] = {}
    arms = []
    for observation in exemplar["observations"]:
        observation_id = f"urn:tribunal:observation:{run_id}:{observation['key']}"
        arm_id = f"urn:tribunal:experimental-arm:{run_id}:{observation['key']}"
        rows = [assertion_rows[name] for name in observation["assertions"]]
        participant_ids = sorted({row["origin"] for row in rows})
        arms.append({
            "id": arm_id,
            "scenario_id": scenario_id,
            "role": arm_role(observation),
            "description": observation["text"],
        })
        observations.append({
            "id": observation_id,
            "scenario_id": scenario_id,
            "type": "record",
            "schema_id": "tribunal.assertion-group/v1",
            "value": {
                "summary": observation["text"],
                "role": observation["role"],
                "assertions": [
                    {"definition_id": row["name"], "result": row["status"].lower(), "detail": row.get("detail", "")}
                    for row in rows
                ],
            },
            "observed_at": result["finished_at"],
            "participant_id": participant_ids[0],
            "corroborating_participant_ids": participant_ids[1:],
            "arm_id": arm_id,
            "artifact_ids": [result_artifact],
        })
        ids = []
        for row in rows:
            assertion_id = f"urn:tribunal:assertion-result:{run_id}:{row['name']}"
            ids.append(assertion_id)
            assertions.append({
                "id": assertion_id,
                "definition_id": f"urn:tribunal:assertion-definition:{row['name']}",
                "scenario_id": scenario_id,
                "type": "custom",
                "expected": True,
                "observed": row["status"] == "PASS",
                "result": row["status"].lower(),
                "participant_id": row["origin"],
                "observation_ids": [observation_id],
                "artifact_ids": [result_artifact],
            })
        observation_assertions[observation["key"]] = ids
    package["observations"] = observations
    package["assertions"] = assertions
    package["experimental_arms"] = arms

    treatments = [arm for arm in arms if arm["role"] == "treatment"]
    controls = [arm for arm in arms if arm["role"] != "treatment"]
    package["causal_relationships"] = [
        {
            "id": f"urn:tribunal:causal-pair:{run_id}:{index}",
            "relation": "CAUSAL_PAIR_WITH",
            "source_arm_id": treatments[-1]["id"],
            "target_arm_id": control["id"],
            "controlled_dimensions": [
                "run", "scenario", "Arma build", "dedicated server", "single authenticated client"
            ],
        }
        for index, control in enumerate(controls)
    ]

    evaluations = []
    for claim in exemplar["claims"]:
        evidence_keys = claim.get("evidence", [])
        if claim["role"] in {"THEOREM", "LEMMA"}:
            outcome = "demonstrated"
            intended_use = "primary_result" if claim["role"] == "THEOREM" else "supporting_result"
        elif claim["role"] == "REFUTED":
            outcome = "counterexample_observed"
            intended_use = "counterexample"
        else:
            outcome = "not_established"
            intended_use = "open_question"
        evaluations.append({
            "id": f"urn:tribunal:proposition-evaluation:{run_id}:{claim['key']}:{outcome}",
            "proposition_id": claim["key"],
            "text": claim.get("text") or next(
                prior["text"] for prior in exemplar["claims"]
                if prior["key"] == claim["key"] and prior.get("text")
            ),
            "outcome": outcome,
            "intended_use": intended_use,
            "observation_ids": [f"urn:tribunal:observation:{run_id}:{key}" for key in evidence_keys],
            "assertion_ids": [item for key in evidence_keys for item in observation_assertions[key]],
            "rationale": claim["reason"],
            **({"specializes_proposition_id": claim["specializes"]} if claim.get("specializes") else {}),
            **({"supersedes_outcome": claim["supersedes"]} if claim.get("supersedes") else {}),
        })
    package["proposition_evaluations"] = evaluations
    package["knowledge_subject"] = {
        "key": exemplar["subject"]["key"],
        "label": exemplar["subject"]["label"],
        "kind": exemplar["subject"]["kind"],
        "aliases": exemplar["subject"].get("aliases", []),
        "biki_context": exemplar.get("biki_context", []),
    }
    package["publication"] = {
        "status": "accepted",
        "published_at": "2026-08-22T12:00:00Z",
        "publisher": "accepted arma-knowledge Tribunal migration f35fa0c",
        "synthetic": False,
        "acceptance_basis": exemplar["review"],
        "unresolved": exemplar["unresolved"],
    }
    package["migration"] = {
        "source_contract": "arma-knowledge.tribunal-curation/v1",
        "selection_reason": exemplar["selection_reason"],
    }
    return package


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--curation",
        type=Path,
        default=Path("/mnt/services/arma-knowledge/src/arma_knowledge/tribunal_exemplars.json"),
    )
    parser.add_argument("--output", type=Path, default=ROOT / "evidence" / "accepted")
    args = parser.parse_args()
    curation = json.loads(args.curation.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for exemplar in curation["exemplars"]:
        package = convert(args.root, exemplar)
        output = args.output / f"{exemplar['run_id']}.json"
        write_immutable_package(output, package)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
