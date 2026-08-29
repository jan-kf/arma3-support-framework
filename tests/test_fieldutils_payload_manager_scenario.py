"""Static contract for the permanent Payload Manager gameplay scenario."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class PayloadManagerScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover([ROOT / "mods/field-utilities/tests/tribunal"])["fieldutils-payload-manager"]

    def test_authority_inventory_ui_and_cleanup_are_exact(self) -> None:
        self.assertEqual(self.scenario.review.outcome, "KEEP AS-IS AND SPEC-TEST")
        self.assertTrue({"payload.fixture", "payload.authority", "payload.cleanup"}.issubset(self.scenario.server_expected))
        self.assertTrue({"payload.worldUi", "payload.themeBindings", "payload.apply", "payload.atomicRefusal", "payload.reorderOwnership"}.issubset(self.scenario.client_expected))
        for needle in ("YFU_PAYLOAD_AUDIT", "remoteExecCall", "uniformItems", "vestItems", "backpackItems", "setUnitLoadout _originalLoadout"):
            self.assertIn(needle, self.scenario.server_sqf + self.scenario.client_sqf)
        self.assertIn('"capacity"', self.scenario.client_sqf)
        self.assertIn('"stale"', self.scenario.client_sqf)
        self.assertIn("actionIDs _uav", self.scenario.client_sqf)
        self.assertIn("ctrlTextColor", self.scenario.client_sqf)
        self.assertNotIn("visual_driver", self.scenario.metadata)

    def test_scope_excludes_mortars_and_unproven_positive_deployment(self) -> None:
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        self.assertNotIn("Sh_82mm_AMOS", combined)
        self.assertNotIn('"deploy" remoteExecCall', combined)
        self.assertIn("Positive in-control deployment", self.scenario.review.locality_requirements)


if __name__ == "__main__":
    unittest.main()
