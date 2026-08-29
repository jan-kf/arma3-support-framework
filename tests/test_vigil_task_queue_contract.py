"""Static guards for Vigil's per-asset task queue and compact operational UI."""

from pathlib import Path
import unittest

from tribunal.discovery import discover
from tribunal.evidence.contract import ARM_ROLES


ROOT = Path(__file__).resolve().parents[1]
VIGIL = ROOT / "source/visual-support-tablet/addons/VIGIL"


class VigilTaskQueueContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.governor = (VIGIL / "functions/governor/fn_governor.sqf").read_text(encoding="utf-8")
        self.request_server = (VIGIL / "functions/governor/fn_taskRequestServer.sqf").read_text(encoding="utf-8")
        self.assets = (VIGIL / "functions/tablet/fn_assets.sqf").read_text(encoding="utf-8")
        self.page = (VIGIL / "ui/pages/page_assets.hpp").read_text(encoding="utf-8")
        self.config = (VIGIL / "config.cpp").read_text(encoding="utf-8")

    def test_server_queue_and_history_are_bounded_and_generation_owned(self) -> None:
        for fragment in (
            "#define YSF_TASK_QUEUE_LIMIT 4",
            "#define YSF_TASK_HISTORY_LIMIT 8",
            'YSF_taskActivateNext = {',
            '_queue pushBack _task;',
            '_history deleteRange',
            '[_rec, _task] call YSF_taskHistoryAppend;',
            '[_rec] call YSF_taskActivateNext;',
            '"started", true, "activated"',
            '"terminal", true, "terminal"',
        ):
            self.assertIn(fragment, self.governor)
        for fragment in (
            'localNamespace getVariable ["YSF_task_ingress_queue", []]',
            '_queue pushBack',
            'private _next = _pending deleteAt 0;',
            'call YSF_taskRequestProcess;',
            '"ingress_full"',
        ):
            self.assertIn(fragment, self.request_server)

    def test_duplicate_policy_is_task_specific(self) -> None:
        equivalent = self.governor.split("YSF_taskEquivalent = {", 1)[1].split("YSF_taskHistoryAppend = {", 1)[0]
        self.assertIn('case "artillery"', equivalent)
        self.assertIn('case "transport"', equivalent)
        self.assertIn('case "cas"', equivalent)
        self.assertIn("distance2D", equivalent)
        self.assertIn('"equivalent_duplicate"', self.governor)
        self.assertNotIn("YSF_TASK_DUPLICATE_DISTANCE", self.governor)

    def test_replacement_is_explicit_confirmed_and_separate_from_fifo(self) -> None:
        self.assertIn('localNamespace getVariable ["YSF_task_authority_token"', self.governor)
        self.assertIn('_existing set ["replacement", _task];', self.governor)
        self.assertIn('"replacement_pending"', self.governor)
        self.assertIn('call BIS_fnc_guiMessage;', self.governor)
        self.assertIn('"VIGIL Replace Active Task"', self.governor)
        self.assertEqual(self.page.count("class BtnReplace: YSF_BtnReplace"), 3)

    def test_operational_overlay_uses_real_theme_cross_tab_lines_and_refresh(self) -> None:
        for fragment in (
            'missionNamespace getVariable ["YSF_monochromeBaseColor"',
            '_map drawLine',
            '_map drawIcon',
            'then {_base # 3} else {(_base # 3) * 0.3}',
            'uiSleep 3;',
            'YSF_taskOperationalRefresh = {',
            'YSF_taskOperationalDraw = {',
        ):
            self.assertIn(fragment, self.assets)
        self.assertIn('onDraw = "_this call YSF_taskOperationalDraw;"', self.page)
        self.assertIn("IDC_ASSETS_TASK_STATUS", self.page)
        self.assertIn("IDC_ASSETS_TASK_RECENT", self.page)
        self.assertIn("YSF_task_operational_draw_rows", self.config)

    def test_old_task_management_homepage_remains_unregistered(self) -> None:
        init = (VIGIL / "functions/global/fn_init.sqf").read_text(encoding="utf-8")
        self.assertIn('// ["home", IDC_PAGE_HOME] call YSF_UI_RegisterPage;', init)
        active_lines = [line.strip() for line in init.splitlines() if not line.lstrip().startswith("//")]
        self.assertNotIn('["home", IDC_PAGE_HOME] call YSF_UI_RegisterPage;', active_lines)
        self.assertNotIn('#include "ui\\pages\\page_home.hpp"', self.config)

    def test_permanent_scenario_contract_is_complete(self) -> None:
        scenario = discover([ROOT / "source/visual-support-tablet/tests/tribunal"])["vigil-task-queue"]
        self.assertEqual(len(scenario.server_expected), 9)
        self.assertEqual(len(scenario.client_expected), 7)
        self.assertEqual(scenario.evidence_contract["scenario"]["version"], 2)
        self.assertTrue(all(arm["role"] in ARM_ROLES for arm in scenario.evidence_contract["arms"]))
        covered = {
            assertion
            for proposition in scenario.evidence_contract["propositions"]
            for assertion in proposition["assertions"]
        }
        self.assertEqual(covered, set(scenario.server_expected | scenario.client_expected))


if __name__ == "__main__":
    unittest.main()
