"""Tribunal Evidence Contract v1 producer and migration contracts."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

from tribunal.evidence import (
    EvidenceContractError,
    build_execution_package,
    load_and_validate,
    validate_package,
    write_immutable_package,
)


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pontifex_paths import PATHS  # noqa: E402

PACKAGES = ROOT / "evidence" / "accepted"
RUN = PATHS.runs / "20260821T153013Z-0a8b2c91"


class EvidenceContractV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = load_and_validate(PACKAGES / "20260821T153013Z-0a8b2c91.json")

    def test_converted_packages_are_valid_human_readable_and_scoped(self) -> None:
        for path in sorted(PACKAGES.glob("*.json")):
            package = load_and_validate(path)
            self.assertEqual(package["schema"], "tribunal.evidence/v1")
            self.assertEqual(package["run"]["execution_state"], "completed")
            self.assertEqual(package["context"]["version"], "2.22.153995")
            self.assertEqual(package["participants"][0]["role"], "dedicated_server")
            self.assertTrue(package["artifacts"])
            self.assertTrue(package["source_snapshots"][0]["files"])
            self.assertFalse(package["publication"]["synthetic"])

        cbr = self.package
        self.assertIn("CBR", cbr["scenarios"][0]["name"])
        control = next(arm for arm in cbr["experimental_arms"] if arm["role"] == "negative_control")
        self.assertIn("same artillery", control["description"])
        self.assertEqual(cbr["causal_relationships"][0]["relation"], "CAUSAL_PAIR_WITH")
        self.assertIn(control["id"], {
            cbr["causal_relationships"][0]["source_arm_id"],
            cbr["causal_relationships"][0]["target_arm_id"],
        })

    def test_unknown_optional_fields_are_tolerated_but_required_fields_fail(self) -> None:
        extended = copy.deepcopy(self.package)
        extended["future_optional"] = {"new": True}
        extended["scenarios"][0]["future_optional"] = "preserved"
        validate_package(extended, verify_integrity=False)
        broken = copy.deepcopy(self.package)
        del broken["run"]["execution_state"]
        with self.assertRaisesRegex(EvidenceContractError, "execution_state"):
            validate_package(broken, verify_integrity=False)

    def test_assertions_reference_observations_and_artifacts(self) -> None:
        observation_ids = {item["id"] for item in self.package["observations"]}
        artifact_ids = {item["id"] for item in self.package["artifacts"]}
        self.assertTrue(self.package["assertions"])
        for assertion in self.package["assertions"]:
            self.assertTrue(set(assertion["observation_ids"]) <= observation_ids)
            self.assertTrue(set(assertion["artifact_ids"]) <= artifact_ids)
            self.assertIn(assertion["participant_id"], {"server", "client-a"})
            self.assertEqual(assertion["result"], "pass")

    def test_completed_negative_result_is_not_failed_execution(self) -> None:
        manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
        result = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
        negative = {**result, "status": "FAIL", "reason": "assertion_failure"}
        package = build_execution_package(RUN, manifest, negative)
        self.assertEqual(package["run"]["execution_state"], "completed")
        self.assertEqual(package["run"]["outcome"], "negative")
        failed = {**result, "status": "FAIL", "reason": "runner_error"}
        package = build_execution_package(RUN, manifest, failed)
        self.assertEqual(package["run"]["execution_state"], "failed_to_execute")
        self.assertEqual(package["run"]["outcome"], "inconclusive")

    def test_scenario_declared_scientific_semantics_publish_only_on_literal_pass(self) -> None:
        manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
        result = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
        names = [row["name"] for row in result["assertions"][:2]]
        semantics = {
            "scenario": {"id": "tribunal.contract-probe.semantic", "version": 1, "feature_family": "tribunal", "name": "Contract probe", "definition": {"kind": "test", "reference": "tests/test_evidence_contract_v1.py"}},
            "knowledge_subject": {"key": "tribunal:contract-probe", "label": "Contract probe", "kind": "tooling", "biki_context": []},
            "arms": [
                {"key": "treatment", "role": "treatment", "description": "Explicit treatment", "assertions": [names[0]]},
                {"key": "control", "role": "negative_control", "description": "Explicit control", "assertions": [names[1]]},
            ],
            "causal_relationships": [{"key": "pair", "relation": "CAUSAL_PAIR_WITH", "source": "treatment", "target": "control", "controlled_dimensions": ["fixture"]}],
            "propositions": [{"id": "tribunal:contract-probe:claim", "text": "Explicit semantics survive automatic emission.", "intended_use": "producer regression", "assertions": names, "rationale": "Both declared observations passed."}],
        }
        manifest["test_plan"] = {"scenarios": ["contract-probe"], "evidence_contracts": {"contract-probe": semantics}}
        package = build_execution_package(RUN, manifest, result)
        validate_package(package, verify_integrity=False)
        self.assertEqual(len(package["experimental_arms"]), 2)
        self.assertEqual(package["causal_relationships"][0]["relation"], "CAUSAL_PAIR_WITH")
        self.assertEqual(package["proposition_evaluations"][0]["outcome"], "demonstrated")
        self.assertEqual(package["knowledge_subject"]["key"], "tribunal:contract-probe")
        self.assertEqual(package["scenarios"][0]["id"], "tribunal.contract-probe.semantic")
        self.assertEqual(package["experimental_arms"][0]["scenario_id"], "tribunal.contract-probe.semantic")

        failed = build_execution_package(RUN, manifest, {**result, "status": "FAIL", "reason": "assertion_failure"})
        self.assertEqual(failed["experimental_arms"], [])
        self.assertEqual(failed["proposition_evaluations"], [])
        self.assertNotIn("knowledge_subject", failed)

    def test_stable_identity_survives_path_movement(self) -> None:
        manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
        result = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
        original = build_execution_package(RUN, manifest, result)
        with tempfile.TemporaryDirectory() as temporary:
            moved = Path(temporary) / "moved-run"
            shutil.copytree(RUN, moved)
            relocated = build_execution_package(moved, manifest, result)
        self.assertEqual(original["package_id"], relocated["package_id"])
        self.assertEqual(
            [item["id"] for item in original["assertions"]],
            [item["id"] for item in relocated["assertions"]],
        )
        self.assertEqual(
            [item["id"] for item in original["artifacts"]],
            [item["id"] for item in relocated["artifacts"]],
        )

    def test_published_package_is_immutable_and_correction_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "evidence.json"
            raw = copy.deepcopy(self.package)
            raw.pop("integrity")
            write_immutable_package(output, raw)
            changed = copy.deepcopy(raw)
            changed["run"]["outcome"] = "mixed"
            with self.assertRaisesRegex(EvidenceContractError, "immutable"):
                write_immutable_package(output, changed)
            replacement = copy.deepcopy(changed)
            replacement["package_revision"] = 2
            replacement["package_id"] += ":correction-2"
            replacement["supersedes_package_id"] = raw["package_id"]
            write_immutable_package(Path(temporary) / "evidence-correction-2.json", replacement)

    def test_vigil_removal_remains_not_established(self) -> None:
        vigil = load_and_validate(PACKAGES / "20260821T165814Z-d0a72396.json")
        removal = next(
            item for item in vigil["proposition_evaluations"]
            if item["proposition_id"] == "pontifex:vigil:whitelist-authentic-removal"
        )
        self.assertEqual(removal["outcome"], "not_established")
        self.assertEqual(removal["observation_ids"], [])
        self.assertEqual(removal["assertion_ids"], [])


if __name__ == "__main__":
    unittest.main()
