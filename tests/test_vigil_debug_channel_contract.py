from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class VigilDebugChannelContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engage = (
            ROOT / "source/visual-support-tablet/addons/VIGIL/functions/task_cas/fn_airAutoEngage.sqf"
        ).read_text()
        self.settings = (
            ROOT / "source/visual-support-tablet/addons/VIGIL/functions/global/fn_initSettings.sqf"
        ).read_text()
        self.utils = (
            ROOT / "source/visual-support-tablet/addons/VIGIL/functions/global/fn_utils.sqf"
        ).read_text()
        self.harness = (
            ROOT / "source/visual-support-tablet/addons/VIGIL/functions/global/fn_fwLaserTest.sqf"
        ).read_text()
        self.scenario = discover(
            [ROOT / "source/visual-support-tablet/tests/tribunal"]
        )["vigil-debug-channel"]

    def test_aae_debug_uses_only_the_registered_vigil_gate(self) -> None:
        self.assertNotIn("YSF_AAE_DEBUG =", self.engage)
        self.assertNotIn('getVariable ["YSF_AAE_DEBUG"', self.engage)
        self.assertIn('["YSF_showDebugMessages", "CHECKBOX"', self.settings)
        self.assertIn('[_msg, "YSF_AAE", "YSF_showDebugMessages"] call YCD_fnc_debugMsg;', self.engage)

    def test_shared_debug_wrapper_has_one_production_owner(self) -> None:
        self.assertEqual(self.utils.count("YSF_fnc_debugMsg = {"), 1)
        self.assertIn('[_msg, "YSF", "YSF_showDebugMessages"] call YCD_fnc_debugMsg;', self.utils)
        self.assertNotIn("YSF_fnc_debugMsg = {", self.harness)

    def test_scenario_observes_exact_off_on_route_and_cleanup(self) -> None:
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        for fragment in (
            "YSF_AAE_dbg",
            "YCD_fnc_showDebugLine",
            "TRIBUNAL_AAE_DISABLED_",
            "TRIBUNAL_AAE_ENABLED_",
            "TRIBUNAL_SHARED_DISABLED_",
            "TRIBUNAL_SHARED_ENABLED_",
            '"YSF_showDebugMessages"',
            "vigil.aaeDebug.clientDisabled",
            "vigil.aaeDebug.clientEnabled",
            "vigil.aaeDebug.cleanup",
            "TRIBUNAL_VIGIL_AAE_DEBUG_ORIGINAL",
        ):
            self.assertIn(fragment, combined)

    def test_evidence_contract_covers_every_assertion(self) -> None:
        declared = {
            assertion
            for arm in self.scenario.evidence_contract["arms"]
            for assertion in arm["assertions"]
        }
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(declared, expected)


if __name__ == "__main__":
    unittest.main()
