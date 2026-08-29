"""Contracts for Tribunal's durable test-review methodology."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from pontifex_paths import TRIBUNAL_ROOT  # noqa: E402

from tribunal.discovery import discover  # noqa: E402
from tribunal.interactions.ace import AceInteractionRequest  # noqa: E402
from tribunal.runner.model import CharacterizedBehavior, ScenarioReview  # noqa: E402


class TestingMethodologyTests(unittest.TestCase):
    def test_all_permanent_scenarios_declare_review_metadata(self) -> None:
        scenarios = discover([
            TRIBUNAL_ROOT / "tribunal" / "scenarios",
            ROOT / "source" / "advanced-systems" / "tests" / "tribunal",
            ROOT / "source" / "field-utilities" / "tests" / "tribunal",
            ROOT / "source" / "visual-support-tablet" / "tests" / "tribunal",
        ])
        self.assertTrue(scenarios)
        for scenario in scenarios.values():
            self.assertIsNotNone(scenario.review, scenario.identifier)
            self.assertNotIn("YOSHI_", scenario.review.behavior_contract, scenario.identifier)
            self.assertTrue(scenario.review.evidence_types, scenario.identifier)
            self.assertTrue(scenario.review.locality_requirements, scenario.identifier)

    def test_scenario_sqf_is_ascii_encodable(self) -> None:
        """Mission .sqf files are written as ASCII; a stray dash breaks the tier."""

        scenarios = discover([
            TRIBUNAL_ROOT / "tribunal" / "scenarios",
            ROOT / "source" / "advanced-systems" / "tests" / "tribunal",
            ROOT / "source" / "field-utilities" / "tests" / "tribunal",
            ROOT / "source" / "visual-support-tablet" / "tests" / "tribunal",
        ])
        for scenario in scenarios.values():
            fragments = {"server": scenario.server_sqf, "client": scenario.client_sqf}
            fragments.update(
                {f"client:{identity}": text for identity, text in scenario.client_sqf_by_identity.items()}
            )
            for origin, text in fragments.items():
                offending = sorted({character for character in text if ord(character) > 127})
                self.assertFalse(offending, f"{scenario.identifier} {origin}: {offending}")

    def test_characterization_requires_complete_evidence_record(self) -> None:
        with self.assertRaises(ValueError):
            CharacterizedBehavior("mechanism", "", "evidence", "alternative", "outcome")
        with self.assertRaises(ValueError):
            ScenarioReview(
                test_type="characterization",
                behavior_contract="preserve a proven engine requirement",
                outcome="KEEP + CHARACTERIZE ENGINE REQUIREMENT",
                rationale="engine evidence",
            )

    def test_ace_interaction_request_is_product_neutral_and_fail_closed(self) -> None:
        request = AceInteractionRequest(
            actor="client-a:player",
            target="fixture:vehicle",
            action_path=("ACE_MainActions", "FeatureAction"),
        )
        self.assertEqual(request.interaction_type, "external")
        self.assertTrue(request.activate)
        with self.assertRaises(ValueError):
            AceInteractionRequest("client-a:player", "fixture:vehicle", (), activate=True)
        with self.assertRaises(ValueError):
            AceInteractionRequest("client-a:player", "fixture:vehicle", ("Action",), expect_available=False, activate=True)


if __name__ == "__main__":
    unittest.main()
