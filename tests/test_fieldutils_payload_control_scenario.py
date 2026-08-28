"""Static contract for the permanent Payload Manager live-control scenario."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class PayloadControlScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover([ROOT / "source/field-utilities/tests/tribunal"])["fieldutils-payload-control"]

    def test_control_hud_effects_negatives_and_cleanup_are_exact(self) -> None:
        self.assertEqual(self.scenario.review.outcome, "KEEP AS-IS AND SPEC-TEST")
        self.assertTrue({"payloadControl.fixture", "payloadControl.authority", "payloadControl.effects", "payloadControl.cleanup"}.issubset(self.scenario.server_expected))
        self.assertTrue({"payloadControl.contextGate", "payloadControl.control", "payloadControl.hud", "payloadControl.cycle", "payloadControl.grenades", "payloadControl.empty", "payloadControl.satchel"}.issubset(self.scenario.client_expected))
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        for marker in ("connectTerminalToUAV", "remoteControl", "UAVControl", "YFU_fnc_payloadControlRequest", "YFU_PAYLOAD_DEPLOYMENTS", "ctrlTextColor", "CBA", "controller", "empty", "deleteVehicle"):
            self.assertIn(marker, combined + " ".join(self.scenario.review.dependencies))
        self.assertIn('[40, _grenadeRecords, 0]', self.scenario.server_sqf)
        self.assertIn('[70, _satchelRecords, 0]', self.scenario.server_sqf)
        self.assertIn('MiniGrenade", "HandGrenade", "SatchelCharge_Remote_Mag', self.scenario.server_sqf)

    def test_scope_stays_bounded(self) -> None:
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        self.assertNotIn("Sh_82mm_AMOS", combined)
        self.assertNotIn("ace_interact_menu", combined)
        self.assertNotIn("client-b", combined.casefold())
        self.assertIn("Client-B/JIP", self.scenario.review.locality_requirements)


if __name__ == "__main__":
    unittest.main()
