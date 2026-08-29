"""Static guards for resolved Vigil product decisions."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VIGIL = ROOT / "source/visual-support-tablet/addons/VIGIL"
FIELD = ROOT / "source/field-utilities/addons/FieldUtils"


class VigilResolvedDecisionContractTests(unittest.TestCase):
    def test_airdrop_estimates_real_flight_time_to_release_not_fall_time(self) -> None:
        assets = (FIELD / "functions/fabricator/fn_assets.sqf").read_text(encoding="utf-8")
        announce = assets.split("YFU_assetsAirdropAnnounce = {", 1)[1].split(
            "YFU_airdropResultVariable = {", 1
        )[0]
        self.assertIn("velocity _airAsset", announce)
        self.assertIn("_distance - _releaseRadius", announce)
        self.assertIn("_remaining / _closingSpeed", announce)
        self.assertIn("_predictedReleaseATL", announce)
        self.assertIn("approximately %3 seconds", announce)
        self.assertIn("release %2 of target", announce)
        self.assertNotIn("YOSHI_GET_FALL_TIME", announce)
        self.assertNotIn("ground", announce.split("private _msg = format", 1)[1])

    def test_artillery_workspace_is_cleared_on_tab_transition_and_close(self) -> None:
        arty = (VIGIL / "functions/task_artillery/fn_ui_arty.sqf").read_text(encoding="utf-8")
        assets = (VIGIL / "functions/tablet/fn_assets.sqf").read_text(encoding="utf-8")
        utils = (VIGIL / "functions/global/fn_utils.sqf").read_text(encoding="utf-8")
        config = (VIGIL / "config.cpp").read_text(encoding="utf-8")
        for fragment in (
            "YSF_taskArtyClearWorkspace = {",
            'deleteMarkerLocal _coordinateMarker',
            'uiNamespace setVariable ["YSF_arty_coord_preview_var", ""]',
            'uiNamespace setVariable ["YOSHI_taskArty_state", nil]',
            'uiNamespace setVariable ["YOSHI_taskArty_strikePattern", []]',
        ):
            self.assertIn(fragment, arty)
        self.assertEqual(assets.count("call YSF_taskArtyClearWorkspace;"), 2)
        self.assertIn("call YSF_taskArtyClearWorkspace;", utils)
        self.assertIn("call YSF_clearAllMarkers", config)
        self.assertNotIn("YSF_TASK_RECORDS", arty)
        self.assertNotIn("YSF_TASK_OPERATIONAL_ROWS", arty)

    def test_dead_recon_surface_is_retired_but_future_role_seam_remains(self) -> None:
        config = (VIGIL / "config.cpp").read_text(encoding="utf-8")
        assets = (VIGIL / "functions/tablet/fn_assets.sqf").read_text(encoding="utf-8")
        page = (VIGIL / "ui/pages/page_assets.hpp").read_text(encoding="utf-8")
        fixed_wing = (VIGIL / "functions/task_fixedWing/fn_initFixedWingFunctions.sqf").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("class TaskRecon", config)
        self.assertNotIn("YOSHI_taskRecon", assets)
        self.assertNotIn("TaskG_Recon", page)
        self.assertFalse((VIGIL / "functions/task_recon/fn_recon_task.sqf").exists())
        self.assertIn("YSF_FW_ROLE_RECON = 2", fixed_wing)
        self.assertIn("if (unitIsUAV _vehicle)", fixed_wing)


if __name__ == "__main__":
    unittest.main()
