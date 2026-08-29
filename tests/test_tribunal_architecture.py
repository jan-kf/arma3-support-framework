"""Boundary contracts for the generic Tribunal framework migration."""

from __future__ import annotations

import inspect
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from tribunal.discovery import discover  # noqa: E402
from tribunal.mission.entities import render_typed_entities
from tribunal.runner.model import MissionEntity, MissionSync, Scenario  # noqa: E402
import pontifex_multiplayer as multiplayer  # noqa: E402
import pontifex_server as dedicated  # noqa: E402
from pontifex_paths import TRIBUNAL_ROOT  # noqa: E402


class TribunalArchitectureTests(unittest.TestCase):
    def test_pontifex_adapters_use_generic_pbo_and_protocol_boundaries(self) -> None:
        self.assertEqual(dedicated.build_mission_pbo.__module__, "tribunal.mission.pbo")
        self.assertEqual(multiplayer.TestPlan.__module__, "tribunal.runner.model")

    def test_feature_scenarios_are_discovered_outside_tribunal(self) -> None:
        scenarios = discover([
            ROOT / "mods" / "advanced-systems" / "tests" / "tribunal",
            ROOT / "mods" / "field-utilities" / "tests" / "tribunal",
            ROOT / "mods" / "visual-support-tablet" / "tests" / "tribunal",
        ])
        aps = scenarios["aps-intercept"]
        self.assertIsInstance(aps, Scenario)
        self.assertEqual(aps.tier, "gameplay")
        self.assertIn("aps.positive.engaged", aps.server_expected)
        self.assertIn("aps.replication", aps.client_expected)
        self.assertEqual(multiplayer.APS_SCENARIO, aps)
        vigil = scenarios["vigil-ui"]
        self.assertEqual(vigil.metadata["visual_driver"], "tabbed-control")
        self.assertIn("vigil.input.artilleryTab", vigil.client_expected)
        self.assertIn("vigil.fixture.inputReady", vigil.client_expected)
        self.assertNotIn("ctrlShown _page", vigil.client_sqf)
        self.assertIn("ctrlEnabled _tabs", vigil.client_sqf)
        self.assertIn("lbCurSel _tabs", vigil.client_sqf)
        self.assertLess(vigil.client_sqf.index("private _inputReadyAt"), vigil.client_sqf.index('player linkItem "YSF_VigilTerminal_B"'))
        self.assertIn("vigil.access.requiredRejects", vigil.client_expected)
        self.assertIn("vigil.access.overrideOpens", vigil.client_expected)
        self.assertIn("vigil.access.bluOpens", vigil.client_expected)
        self.assertIn("vigil.access.independentOpens", vigil.client_expected)
        self.assertIn("vigil.access.opforOpens", vigil.client_expected)
        self.assertIn("vigil.access.matrixCleanup", vigil.client_expected)
        self.assertTrue({
            "vigil.browser.fixtureReplicated",
            "vigil.browser.transportExact",
            "vigil.browser.artilleryExact",
            "vigil.browser.casExact",
        }.issubset(vigil.client_expected))
        self.assertTrue({
            "vigil.browser.serverFixture",
            "vigil.browser.serverLocality",
            "vigil.browser.cleanup",
        }.issubset(vigil.server_expected))
        self.assertIn("TRIBUNAL_VIGIL_BROWSER_FIXTURE", vigil.server_sqf)
        self.assertIn("TRIBUNAL_VIGIL_BROWSER_DONE", vigil.client_sqf)
        self.assertIn("objectFromNetId", vigil.client_sqf)
        self.assertIn("_tree tvData", vigil.client_sqf)
        self.assertIn('["transport", [_browserFixture # 0]', vigil.client_sqf)
        self.assertIn('["arty", [_browserFixture # 1]', vigil.client_sqf)
        self.assertIn('["cas", [_browserFixture # 2]', vigil.client_sqf)
        self.assertNotIn('["recon",', vigil.client_sqf)
        self.assertIn('missionNamespace setVariable ["YSF_enableTablet", false]', vigil.client_sqf)
        self.assertIn("TRIBUNAL_VIGIL_REQUIRED_CALL_AT", vigil.client_sqf)
        self.assertIn('"YSF_VigilTerminal_I"', vigil.client_sqf)
        self.assertIn('"YSF_VigilTerminal_O"', vigil.client_sqf)
        self.assertLess(vigil.client_sqf.index("vigil.fixture.inputReady"), vigil.client_sqf.index('diag_log "TRIBUNAL_VIGIL|ARMED"'))
        self.assertIn("private _reopenWorker = [] spawn", vigil.client_sqf)
        self.assertIn("[] call YSF_UI_OpenTablet", vigil.client_sqf)
        self.assertIn('"exec", "-e", "DISPLAY=:0", client_name', inspect.getsource(multiplayer))
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["vigil-ui"], vigil)
        markers = scenarios["vigil-markers"]
        self.assertEqual(markers.metadata["visual_driver"], "map-markers")
        self.assertEqual(markers.metadata["map_expected_anchor"], {"x": 0.5, "y": 0.5})
        self.assertIn("vigil.marker.firstBacking", markers.client_expected)
        self.assertIn("vigil.marker.dynamicReplacement", markers.client_expected)
        self.assertIn("vigil.marker.closeArmed", markers.client_expected)
        self.assertIn("vigil.marker.closeCleanup", markers.client_expected)
        self.assertTrue({
            "vigil.marker.serverFixture",
            "vigil.marker.serverCleanup",
        }.issubset(markers.server_expected))
        marker_contract_assertions = {
            assertion
            for arm in markers.evidence_contract["arms"]
            for assertion in arm["assertions"]
        }
        self.assertEqual(
            marker_contract_assertions,
            set(markers.server_expected) | set(markers.client_expected),
        )
        self.assertIn('["pattern", "circle"] call YOSHI_taskArty_Set', markers.client_sqf)
        self.assertIn('["spread", 50] call YOSHI_taskArty_Set', markers.client_sqf)
        self.assertIn('["dir", 0] call YOSHI_taskArty_Set', markers.client_sqf)
        self.assertIn('["count", _countControl] call YOSHI_setCount', markers.client_sqf)
        self.assertIn("_x in allMapMarkers", markers.client_sqf)
        self.assertIn("call YOSHI_assetSelected", markers.client_sqf)
        self.assertIn("getArtilleryETA [[4680, 2770, 0], _ordnance]", markers.server_sqf)
        self.assertIn('displayAddEventHandler ["KeyDown"', markers.client_sqf)
        self.assertIn('markerText _x) find "1st Round ETA:"', markers.client_sqf)
        self.assertIn('uiNamespace getVariable ["YSF_map_overlay_markers", []]', markers.client_sqf)
        self.assertIn("private _remainingAfterClose = _captured select {_x in allMapMarkers};", markers.client_sqf)
        self.assertLess(
            markers.client_sqf.index('displayAddEventHandler ["KeyDown"'),
            markers.client_sqf.index("private _closeDeadline"),
        )
        self.assertIn("YSF_arty_coord_preview_var", markers.client_sqf)
        self.assertIn("vigil.marker.tabLeaveCleanup", markers.client_expected)
        self.assertIn("vigil.marker.tabReturnClean", markers.client_expected)
        self.assertIn("[controlNull, 0] call YOSHI_assetsTabChanged", markers.client_sqf)
        self.assertIn("[controlNull, 1] call YOSHI_assetsTabChanged", markers.client_sqf)
        self.assertNotIn("YOSHI_taskArty_submit", markers.client_sqf)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["vigil-markers"], markers)
        runner_source = inspect.getsource(multiplayer)
        self.assertIn('visual_driver == "map-markers"', runner_source)
        self.assertIn("/pontifex/tools/tribunal_map_probe.py", runner_source)
        self.assertIn("ui_probes_attempted: set[str]", runner_source)
        self.assertNotIn("only one interactive visual scenario", runner_source)
        gameplay = multiplayer.select_plan("gameplay")
        self.assertTrue({"vigil-ui", "vigil-markers", "vigil-artillery"}.issubset(gameplay.selected))

        artillery = scenarios["vigil-artillery"]
        self.assertEqual(artillery.metadata["targeting_modes"], "grid-only")
        self.assertEqual(artillery.metadata["patterns"], "circle,line")
        self.assertIn("vigil.artillery.vls.arrival", artillery.server_expected)
        self.assertIn("vigil.artillery.grid.invalid", artillery.client_expected)
        self.assertIn("TRIBUNAL_fnc_artilleryObserverStart", artillery.server_sqf)
        self.assertIn("call YOSHI_taskArty_submit", artillery.client_sqf)
        self.assertIn('["done", "ready_for_next"]', artillery.server_sqf)
        self.assertNotIn("laserTarget", artillery.client_sqf)

        transport = scenarios["vigil-transport"]
        self.assertEqual(transport.metadata["ui_path"], "YOSHI_taskTRN_submit/YOSHI_taskTRN_rtb")
        self.assertIn("vigil.transport.dispatch.flight", transport.server_expected)
        self.assertIn("vigil.transport.home", transport.server_expected)
        self.assertIn("vigil.transport.client.eligible", transport.client_expected)
        self.assertIn("TRIBUNAL_fnc_observeFlight", transport.server_sqf)
        self.assertIn("call YOSHI_taskTRN_submit", transport.client_sqf)
        self.assertIn("call YOSHI_taskTRN_rtb", transport.client_sqf)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["vigil-transport"], transport)
        self.assertIn("vigil-transport", gameplay.selected)

        radar = scenarios["advsys-counter-battery-radar"]
        self.assertNotIn("visual_driver", radar.metadata)
        self.assertIn("cbr.prediction.impactAccuracy", radar.server_expected)
        self.assertIn("cbr.control.disabledNoDetection", radar.server_expected)
        self.assertIn("cbr.client.warningDelivered", radar.client_expected)
        self.assertIn("cbr.warning.launchPipeline", radar.server_expected)
        self.assertIn("TRIBUNAL_fnc_markerCensus", radar.server_sqf)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["advsys-counter-battery-radar"], radar)
        self.assertIn("advsys-counter-battery-radar", gameplay.selected)

        bridge = scenarios["fieldutils-bridge-builder"]
        self.assertNotIn("visual_driver", bridge.metadata)
        self.assertIn("bridge.traversal.authoritative", bridge.server_expected)
        self.assertIn("bridge.interaction.registration", bridge.client_expected)
        self.assertIn("bridge.interaction.conditions", bridge.client_expected)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["fieldutils-bridge-builder"], bridge)
        self.assertIn("fieldutils-bridge-builder", gameplay.selected)

    def test_typed_mission_fixture_is_validated_and_renders_native_sync(self) -> None:
        entities = (
            MissionEntity("MODULE_A", "Example_Module", "Example_Addon", "Logic", (100, 5, 200)),
            MissionEntity("TARGET_A", "Example_Target", "Example_Targets", "Object", (110, 5, 200)),
        )
        source, connections = render_typed_entities(
            entities, (MissionSync("MODULE_A", "TARGET_A"),), first_item=2
        )
        self.assertIn('class Item2 { dataType="Logic";', source)
        self.assertIn('name="MODULE_A"', source)
        self.assertIn('class Item3 { dataType="Object";', source)
        self.assertIn('side="Empty"; flags=7;', source)
        self.assertIn('item0=100; item1=101;', connections)
        self.assertIn('type="Sync";', connections)
        self.assertIn('class LinkIDProvider { nextID=1; };', connections)
        self.assertIn('linkID=0;', connections)
        self.assertNotIn('id=102;', connections)
        with self.assertRaisesRegex(ValueError, "overlap fixture footprints"):
            render_typed_entities(
                (
                    MissionEntity("TARGET_A", "Example_Target", "Example_Targets", "Object", (110, 5, 200)),
                    MissionEntity("TARGET_B", "Example_Target", "Example_Targets", "Object", (115, 5, 200)),
                ),
                (),
                first_item=0,
            )
        with self.assertRaises(ValueError):
            Scenario("bad", "gameplay", frozenset(), frozenset(), "", "", mission_entities=entities, mission_syncs=(MissionSync("MODULE_A", "MISSING"),))

    def test_project_manifest_discovers_the_runtime_feature_scenario_set(self) -> None:
        manifest = json.loads((ROOT / "tribunal.project.json").read_text(encoding="utf-8"))
        roots = [ROOT / value for value in manifest["scenario_roots"]]
        manifest_scenarios = discover(roots)
        self.assertEqual(set(manifest_scenarios), set(multiplayer.FEATURE_SCENARIOS))
        self.assertTrue(all(root.is_dir() for root in roots))

    def test_client_probes_consume_the_external_tribunal_package(self) -> None:
        runner = (ROOT / "tools/pontifex_multiplayer.py").read_text(encoding="utf-8")
        self.assertIn('f"{TRIBUNAL_ROOT}:/tribunal:ro"', runner)
        self.assertIn('"PYTHONPATH=/tribunal"', runner)

    def test_generic_tribunal_sources_do_not_encode_pontifex_features(self) -> None:
        prohibited = (r"\baps\b", r"iron dome", r"\bvigil\b", r"field utilities", r"\bpontifex\b")
        for path in (TRIBUNAL_ROOT / "tribunal").rglob("*.py"):
            text = path.read_text(encoding="utf-8").casefold()
            self.assertFalse(any(re.search(pattern, text) for pattern in prohibited), path)


if __name__ == "__main__":
    unittest.main()
