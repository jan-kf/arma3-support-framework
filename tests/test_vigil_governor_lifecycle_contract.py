from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class VigilGovernorLifecycleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.governor = (
            ROOT / "source/visual-support-tablet/addons/VIGIL/functions/governor/fn_governor.sqf"
        ).read_text()
        self.scenario = discover(
            [ROOT / "source/visual-support-tablet/tests/tribunal"]
        )["vigil-governor-lifecycle"]

    def test_terminal_causes_share_finalization_path(self) -> None:
        self.assertIn("YSF__finalize = {", self.governor)
        self.assertIn('[_task,"complete"] call YSF__terminate;', self.governor)
        self.assertIn('_task set ["finalizing",true];', self.governor)
        self.assertIn('_task set ["finalized",true];', self.governor)

    def test_active_replacement_and_successor_are_generation_aware(self) -> None:
        self.assertIn('if (_existingEnabled && {!_existingFinalizing}) exitWith {false};', self.governor)
        self.assertIn('private _sameGeneration =', self.governor)
        self.assertIn('&& {(_currentTask get "gen") isEqualTo (_task get "gen")};', self.governor)

    def test_vehicle_loss_reaches_task_tick(self) -> None:
        handle = self.governor.split("YSF_governorHandle = {", 1)[1].split("YSF_governorStart = {", 1)[0]
        self.assertNotIn('_rec set ["enabled", false]', handle)
        self.assertIn('[_veh] call YSF_taskTick;', handle)

    def test_evidence_contract_covers_every_assertion(self) -> None:
        declared = {
            assertion
            for arm in self.scenario.evidence_contract["arms"]
            for assertion in arm["assertions"]
        }
        self.assertEqual(declared, set(self.scenario.server_expected) | set(self.scenario.client_expected))

    def test_scenario_has_every_terminal_and_generation_oracle(self) -> None:
        for fragment in (
            '"vigil.governor.normal"',
            '"vigil.governor.earlyComplete"',
            '"vigil.governor.failure"',
            '"vigil.governor.cancellation"',
            '"vigil.governor.vehicleLoss"',
            '"vigil.governor.duplicate"',
            '"vigil.governor.successor"',
            '"TRIBUNAL_GOV_SENTINEL"',
            '"tribunalFinalizers"',
        ):
            self.assertIn(fragment, self.scenario.server_sqf)


if __name__ == "__main__":
    unittest.main()
