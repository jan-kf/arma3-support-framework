"""Static and generated-mission contracts for authenticated APS controls."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class ApsControlsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (ROOT / "source" / "advanced-systems" / "addons" / "AdvSys" / "functions" / "aps" / "fn_aps.sqf").read_text(encoding="utf-8")

    def test_actions_use_one_authenticated_request_boundary(self) -> None:
        self.assertIn("YOSHI_fnc_apsRequestOperation", self.source)
        self.assertIn("private _owner = remoteExecutedOwner", self.source)
        self.assertIn("allPlayers select {isPlayer _x && {owner _x isEqualTo _owner}}", self.source)
        self.assertIn("YOSHI_fnc_apsCanOperate", self.source)
        self.assertIn("(driver _vehicle) isEqualTo _requester", self.source)
        self.assertIn("(gunner _vehicle) isEqualTo _requester", self.source)
        self.assertIn("(commander _vehicle) isEqualTo _requester", self.source)
        self.assertIn("private _nearby = !_inside", self.source)
        self.assertIn('"operator_ineligible"', self.source)
        self.assertIn('"replay"', self.source)
        self.assertNotIn('remoteExecCall ["YOSHI_fnc_apsHandleHardKillTurnOff", 2]', self.source)
        self.assertNotIn('remoteExecCall ["YOSHI_fnc_apsHandleVoiceTurnOff", 2]', self.source)
        self.assertIn('[_vehicle, _requester, _token] call YOSHI_fnc_apsHandleStatusAction', self.source)
        self.assertIn('[_vehicle, _requester, _token] call YOSHI_fnc_apsHandleVoiceTurnOff', self.source)
        self.assertIn('[_vehicle, _requester, _token] call YOSHI_fnc_apsHandleAntiDroneStatusAction', self.source)
        self.assertIn('remoteExecutedOwner > 2 && {_token isNotEqualTo', self.source)

    def test_suspend_resume_preserve_modes_preferences_and_resources(self) -> None:
        self.assertIn('YOSHI_APS_Installed', self.source)
        self.assertIn('"YOSHI_APS_Suspend"', self.source)
        self.assertIn('"YOSHI_APS_Resume"', self.source)
        disable = self.source[self.source.index("YOSHI_fnc_apsDisableVehicle = {"):self.source.index("YOSHI_fnc_apsToggleVehicle = {")]
        self.assertIn('YOSHI_APS_Enabled", false', disable)
        self.assertNotIn("YOSHI_fnc_apsTopUpHardKillCharges", disable)
        self.assertNotIn('YOSHI_APS_VoiceEnabled", false', disable)
        self.assertNotIn('YOSHI_APS_AntiDrone_Enabled", false', disable)
        self.assertNotIn("YOSHI_fnc_apsSetHardKillState", disable)
        self.assertNotIn("YOSHI_fnc_apsSetSoftKillState", disable)
        enable = self.source[self.source.index("YOSHI_fnc_apsEnableVehicle = {"):self.source.index("YOSHI_fnc_apsDisableVehicle = {")]
        self.assertLess(enable.index("if (_firstInstall) then"), enable.index("YOSHI_fnc_apsTopUpHardKillCharges"))

    def test_permanent_scenario_requires_menu_authority_and_physical_ab(self) -> None:
        plan = multiplayer.select_plan("gameplay", "aps-intercept")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "aps-controls-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        for name in ("aps.controls.hardOffImpact", "aps.controls.rebootIntercept", "aps.controls.authoritativeAudit"):
            self.assertIn(name, server)
        for name in ("aps.controls.menu", "aps.controls.transitions", "aps.controls.lifecycle", "aps.controls.composition", "aps.controls.authority", "aps.controls.resultReplication"):
            self.assertIn(name, client)
        self.assertIn("ace_interact_menu_fnc_collectActiveActionTree", client)
        self.assertIn("ace_interact_menu_fnc_compileMenu", client)
        self.assertIn("YOSHI_APS_ActionData_Local", client)
        self.assertIn("_fieldInitial isEqualTo _fieldSuspended", client)
        self.assertIn("_apsSuspendedLeaves isEqualTo [\"YOSHI_APS_Resume\"]", client)
        self.assertIn("call (_data # 3)", client)
        self.assertIn('"operator_ineligible"', client)
        self.assertIn('"replay"', client)
        self.assertIn('"stale_transition"', client)
        self.assertIn('"no_hardkill_charges"', client)
        self.assertIn('"YOSHI_APS_SoftKill_TurnOff"', client)
        self.assertIn('"YOSHI_APS_SoftKill_TurnOn"', client)
        self.assertIn('"YOSHI_APS_AntiDrone_TurnOff"', client)
        self.assertIn('[_apsVehicle, "controls-off"] call _injectThreat', server)
        self.assertIn('[_apsVehicle, "controls-reboot"] call _injectThreat', server)


if __name__ == "__main__":
    unittest.main()
