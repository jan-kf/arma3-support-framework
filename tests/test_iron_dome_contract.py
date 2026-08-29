from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "source/advanced-systems/addons/AdvSys/functions/iron_dome/fn_ironDome.sqf"
SCENARIO = ROOT / "source/advanced-systems/tests/tribunal/iron_dome.py"


def load_scenario():
    spec = importlib.util.spec_from_file_location("iron_dome_scenario", SCENARIO)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TRIBUNAL_SCENARIO


class IronDomeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.product = PRODUCT.read_text(encoding="utf-8")
        cls.scenario_source = SCENARIO.read_text(encoding="utf-8")
        cls.scenario = load_scenario()

    def test_consequential_pipeline_uses_unpublished_server_capability(self) -> None:
        self.assertIn('localNamespace setVariable ["YAS_IRONDOME_TOKEN", format ["yas-iron-', self.product)
        self.assertNotIn('YAS_IRONDOME_TOKEN =', self.product)
        for operation in (
            "register-box",
            "create-task",
            "assign-tasks",
            "execute-tasks",
            "spawn-missile",
            "monitor-intercept",
            "handle-shell-fired",
        ):
            self.assertIn(f'[_token, "{operation}"] call YAS_fnc_ironDomeAuthorized', self.product)
        self.assertIn('"token-rejected", remoteExecutedOwner', self.product)
        self.assertIn('[_entity, localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""]] call YAS_fnc_ironDomeRegisterBox', self.product)
        self.assertIn('remoteExecCall ["YAS_fnc_ironDomeSubmitShellTelemetry", 2]', self.product)
        self.assertIn('_sourceOwner isNotEqualTo owner _shell', self.product)
        self.assertIn('if (isNull _shell || {!local _shell}) exitWith {}', self.product)
        self.assertIn('(_shell call YOSHI_predictFallTimeAndPos) # 1', self.product)
        self.assertIn('private _impactDistance = _launcher distance2D _impactPos', self.product)
        self.assertNotIn('private _shellDistance = _launcher distance2D _shell', self.product)
        self.assertIn('remoteExecCall ["YAS_fnc_ironDomeNeutralizeShellLocal", _effectOwner]', self.product)
        self.assertIn('remoteExecutedOwner isEqualTo _expectedOwner', self.product)

    def test_terminal_events_are_exact_bounded_and_exhausted_tasks_retire(self) -> None:
        self.assertIn('YAS_IRONDOME_EVENT_LIMIT = 64', self.product)
        self.assertIn('missionNamespace setVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", _events, true]', self.product)
        self.assertIn('[_launcher, "launcher", _token] call YAS_fnc_ironDomeObjectUid', self.product)
        self.assertIn('[_token, "object-uid"] call YAS_fnc_ironDomeAuthorized', self.product)
        self.assertIn('[_missile, "interceptor", _token] call YAS_fnc_ironDomeObjectUid', self.product)
        self.assertIn('_task getOrDefault ["shellUid", ""]', self.product)
        self.assertIn('"intercepted", _attemptIndex', self.product)
        self.assertIn('["activeAttempts", 0]', self.product)
        self.assertIn('private _exhausted = (_task getOrDefault ["attempts", 0]) >= YAS_IRONDOME_MAX_SHOTS', self.product)
        self.assertIn('&& {(_task getOrDefault ["activeAttempts", 0]) <= 0}', self.product)
        self.assertIn('_shell setVariable ["YAS_ironDome_controllerActive", false]', self.product)

    def test_scenario_uses_native_pipeline_and_independent_physical_oracles(self) -> None:
        source = self.scenario_source
        self.assertIn('addMissionEventHandler ["ArtilleryShellFired"', source)
        self.assertIn('_gun doArtilleryFire', source)
        self.assertIn('TRIBUNAL_fnc_artilleryObserveSource', source)
        self.assertIn('_target addEventHandler ["HitPart"', source)
        self.assertIn('(damage _target) > (_damageBeforeDisabled + 0.001)', source)
        self.assertIn('count (_disabledRecord getOrDefault ["samples", []])', source)
        self.assertIn('TRIBUNAL_IRON_INTERCEPTORS', source)
        self.assertIn('allMissionObjects "M_Jian_AT"', source)
        self.assertIn('uiSleep 0.001', source)
        self.assertIn('TRIBUNAL_IRON_OBSERVER_ACTIVE', source)
        self.assertIn('scriptDone _interceptorObserver', source)
        self.assertIn('_travel > 20', source)
        self.assertIn('closestShell', source)
        self.assertNotIn('call YAS_fnc_ironDomeHandleShellFired', source)
        self.assertNotIn('call YAS_fnc_ironDomeSpawnMissile', source)

    def test_generated_sqf_delimiters_are_balanced(self) -> None:
        for name, source in (("server", self.scenario.server_sqf), ("client", self.scenario.client_sqf)):
            stack: list[str] = []
            pairs = {"}": "{", "]": "[", ")": "("}
            in_string = False
            index = 0
            while index < len(source):
                char = source[index]
                if char == '"':
                    if in_string and index + 1 < len(source) and source[index + 1] == '"':
                        index += 2
                        continue
                    in_string = not in_string
                elif not in_string and char in "{[(":
                    stack.append(char)
                elif not in_string and char in "}])":
                    self.assertTrue(stack, f"{name} SQF closes {char} without opener at {index}")
                    self.assertEqual(stack.pop(), pairs[char], f"{name} SQF mismatched {char} at {index}")
                index += 1
            self.assertFalse(in_string, f"{name} SQF has an unterminated string")
            self.assertEqual(stack, [], f"{name} SQF has unclosed delimiters: {stack}")

    def test_negative_controls_prove_stimulus_and_authority_receipt(self) -> None:
        source = self.scenario_source
        self.assertIn('"iron.control.disabledImpact"', source)
        self.assertIn('"iron.control.disabledNoEngagement"', source)
        self.assertIn('"iron.control.outOfRangeImpact"', source)
        self.assertIn('"iron.control.outOfRangeNoEngagement"', source)
        self.assertIn('private _farStimulus = (count _far) isEqualTo 1', source)
        self.assertIn('YAS_IRONDOME_AUDIT', source)
        self.assertIn('(_x param [3, 0]) > 2', source)
        self.assertIn('!(_authBox getVariable ["YAS_ironDome_enabled", false])', source)
        self.assertIn('!(_authBox in YAS_IRONDOME_REGISTRY)', source)

    def test_scenario_requires_concurrency_locality_replication_and_cleanup(self) -> None:
        self.assertEqual(self.scenario.identifier, "advsys-iron-dome")
        self.assertIn("iron.concurrent.distinctThreats", self.scenario.server_expected)
        self.assertIn("iron.concurrent.protected", self.scenario.server_expected)
        self.assertIn("iron.locality", self.scenario.server_expected)
        self.assertIn("iron.cleanup", self.scenario.server_expected)
        self.assertIn("iron.client.eventReplicated", self.scenario.client_expected)
        source = self.scenario_source
        self.assertGreaterEqual(source.count('_gun = createVehicle ["B_Mortar_01_F"'), 3)
        self.assertIn('stale AI command state to suppress the stimulus', source)
        self.assertIn('(count (_concurrentProductUids arrayIntersect _concurrentProductUids)) isEqualTo 2', source)
        self.assertIn('(count (_concurrentMissiles arrayIntersect _concurrentMissiles)) isEqualTo 2', source)
        self.assertIn('(count YAS_IRONDOME_TASKS) isEqualTo 0', source)
        self.assertIn('client_expected_by_identity={"client-a": CLIENT_EXPECTED}', source)


if __name__ == "__main__":
    unittest.main()
