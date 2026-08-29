"""Permanent APS anti-drone scenario contract."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402

SCENARIO = ROOT / "mods/advanced-systems/tests/tribunal/aps_anti_drone.py"
APS_SOURCE = ROOT / "mods/advanced-systems/addons/AdvSys/functions/aps/fn_aps.sqf"


class ApsAntiDroneScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SCENARIO.read_text(encoding="utf-8")
        self.aps_source = APS_SOURCE.read_text(encoding="utf-8")
        self.scenario = discover([SCENARIO.parent])["aps-anti-drone"]

    def test_contract_covers_threat_authority_payload_and_handler_boundaries(self) -> None:
        self.assertTrue({
            "apsDrone.motionPolicy", "apsDrone.authority", "apsDrone.neutralization",
            "apsDrone.payloadSuppression", "apsDrone.ordinaryCrashPayload",
            "apsDrone.handlerCompatibility",
        }.issubset(self.scenario.server_expected))
        self.assertEqual(self.scenario.client_expected, frozenset({"apsDrone.clientOwnership"}))
        for marker in (
            "YOSHI_fnc_apsEvaluateDroneThreat", "YOSHI_detectDrones",
            "YOSHI_APS_DRONE_ENGAGEMENT_EVENTS", "YFU_PAYLOAD_DEPLOYMENTS",
            "YFU_PAYLOAD_AUDIT", "addEventHandler [\"Killed\"",
            "YOSHI_APS_AntiDroneNeutralized", "setOwner",
        ):
            self.assertIn(marker, self.source)

    def test_aps_never_removes_handlers_owned_by_other_features_or_mods(self) -> None:
        self.assertNotIn("removeAllEventHandlers", self.aps_source)
        self.assertIn("Third-party", self.aps_source)

    def test_generated_sqf_delimiters_are_balanced(self) -> None:
        for sqf in (self.scenario.server_sqf, self.scenario.client_sqf):
            self.assertEqual(sqf.count("{"), sqf.count("}"))
            self.assertEqual(sqf.count("["), sqf.count("]"))
            self.assertEqual(sqf.count("("), sqf.count(")"))


if __name__ == "__main__":
    unittest.main()
