"""Static safety and UI contract for the Pontifex Payload Manager."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FPV = ROOT / "mods/field-utilities/addons/FieldUtils/functions/drone/fn_fpv.sqf"
UI = ROOT / "mods/field-utilities/addons/FieldUtils/ui/payload_manager.hpp"
CONFIG = ROOT / "mods/field-utilities/addons/FieldUtils/config.cpp"
SETTINGS = ROOT / "mods/field-utilities/addons/FieldUtils/functions/global/fn_initSettings.sqf"


class PayloadManagerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fpv = FPV.read_text(encoding="utf-8")
        cls.ui = UI.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.settings = SETTINGS.read_text(encoding="utf-8")

    def test_catalogue_is_eight_unit_inventory_backed_and_mortars_are_deferred(self) -> None:
        self.assertIn("YFU_PAYLOAD_CAPACITY = 8", self.fpv)
        self.assertIn('["HandGrenade", ["M67 fragmentation grenade", 1', self.fpv)
        self.assertIn('["MiniGrenade", ["RGO fragmentation grenade", 1', self.fpv)
        self.assertIn('["SatchelCharge_Remote_Mag", ["Satchel charge", 8', self.fpv)
        for legacy in ("Sh_82mm_AMOS", "YOSHI_UavOrdinanceCount", "uavMortar"):
            self.assertNotIn(legacy, self.fpv)

    def test_world_entry_and_ui_do_not_depend_on_ace_interaction(self) -> None:
        self.assertIn('addAction [', self.fpv)
        self.assertIn('"Pontifex Payload Manager"', self.fpv)
        self.assertIn('createDialog "YFU_PayloadManager_Dialog"', self.fpv)
        self.assertNotIn("ace_interact_menu", self.fpv)
        self.assertIn('#include "ui\\payload_manager.hpp"', self.config)

    def test_drag_drop_sources_stay_separate_and_proposal_is_ordered(self) -> None:
        for idc in ("YFU_IDC_PAYLOAD_UNIFORM", "YFU_IDC_PAYLOAD_VEST", "YFU_IDC_PAYLOAD_BACKPACK"):
            self.assertIn(idc, self.ui)
            self.assertIn(idc, self.fpv)
        self.assertEqual(self.ui.count("canDrag = 1;"), 2)
        self.assertIn("class Vest: Uniform", self.ui)
        self.assertIn("class Backpack: Uniform", self.ui)
        self.assertIn("onLBDrop", self.ui)
        self.assertIn("YFU_fnc_payloadHandleDrop", self.ui)
        self.assertIn("_proposal insert", self.fpv)
        self.assertIn('"installed-missing"', self.fpv)
        self.assertIn("cannot be reclaimed", self.fpv)

    def test_apply_is_authenticated_atomic_and_uav_owned(self) -> None:
        for marker in (
            "remoteExecutedOwner", "YFU_fnc_payloadPlayerForOwner", "YFU_PAYLOAD_PENDING",
            "YFU_fnc_payloadInventoryPrepareLocal", "YFU_fnc_payloadInventoryPreparedServer",
            "YFU_fnc_payloadInventoryFinalizeLocal", "getUnitLoadout player",
            "player setUnitLoadout _snapshot", '"inventory-rollback"',
            'setVariable ["YFU_PAYLOAD_STATE"', 'remoteExecCall ["YFU_fnc_payloadResult", _owner]',
        ):
            self.assertIn(marker, self.fpv)
        prepare = self.fpv.index("YFU_fnc_payloadInventoryPrepareLocal")
        prepared = self.fpv.index("YFU_fnc_payloadInventoryPreparedServer")
        self.assertLess(self.fpv.index("getUnitLoadout player", prepare), self.fpv.index("YFU_fnc_payloadRemoveSourceItem", prepare))
        self.assertLess(self.fpv.index("private _canCommit", prepared), self.fpv.index('setVariable ["YFU_PAYLOAD_STATE"', prepared))
        apply_server = self.fpv[self.fpv.index("YFU_fnc_payloadApplyServer"):self.fpv.index("YFU_fnc_payloadController")]
        self.assertNotIn("removeItemFrom", apply_server)
        self.assertIn('remoteExecCall ["YFU_fnc_payloadInventoryPrepareLocal", _owner]', apply_server)

    def test_controls_are_context_gated_and_hud_uses_live_bindings(self) -> None:
        for action in ("nextPayload", "deployPayload"):
            self.assertEqual(self.settings.count(f'"{action}"'), 1)
            self.assertIn(f'"{action}"', self.fpv)
        self.assertIn("CBA_fnc_localizeKey", self.fpv)
        self.assertIn("getConnectedUAV player", self.fpv)
        self.assertIn("UAVControl _uav", self.fpv)
        self.assertIn('if (_payloads isEqualTo []) exitWith {["empty"] call _reject}', self.fpv)
        self.assertIn("mod (count _payloads)", self.fpv)

    def test_manager_and_hud_validate_the_existing_theme_setting(self) -> None:
        self.assertIn('missionNamespace getVariable ["YFU_monochromeBaseColor"', self.fpv)
        self.assertIn("_candidate findIf", self.fpv)
        self.assertIn("ctrlSetTextColor", self.fpv)
        self.assertIn("ctrlSetBackgroundColor", self.fpv)
        self.assertIn("YFU_DARK_COLOR", self.ui)
        self.assertIn("YFU_V_DARK_COLOR", self.ui)

    def test_uav_death_releases_payloads_except_feature_owned_aps_suppression(self) -> None:
        self.assertIn('addMissionEventHandler ["EntityKilled"', self.fpv)
        self.assertIn("YFU_fnc_payloadCrashServer", self.fpv)
        for marker in (
            "YFU_PAYLOAD_CRASH_HANDLED",
            'setVariable ["YFU_PAYLOAD_STATE", [_revision + 1, [], 0], true]',
            'getVariable ["YOSHI_APS_AntiDroneNeutralized", ""]',
            '"aps-suppressed"',
            '"crash-release"',
            'if (_deployKind isEqualTo "satchel") then {_effect setDamage 1;}',
            "unrelated mod event handlers are never removed or rewritten",
        ):
            self.assertIn(marker, self.fpv)
        self.assertNotIn("removeAllEventHandlers", self.fpv)


if __name__ == "__main__":
    unittest.main()
