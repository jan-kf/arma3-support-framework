[] spawn {
    waitUntil {time > 0};
    uiSleep 1;

    private _assertions = 0;
    private _failures = 0;
    private _assert = {
        params ["_name", "_condition", ["_detail", ""]];
        _assertions = _assertions + 1;
        private _status = "PASS";
        if (!_condition) then {
            _status = "FAIL";
            _failures = _failures + 1;
        };
        diag_log format ["PONTIFEX_TEST|%1|%2|%3", _status, _name, _detail];
    };

    ["sqf.executed", true, "initServer.sqf"] call _assert;
    ["server.isDedicated", isDedicated, format ["actual=%1", isDedicated]] call _assert;
    ["server.isServer", isServer, format ["actual=%1", isServer]] call _assert;
    ["core.config", isClass (configFile >> "CfgPatches" >> "YCD_CORDIS")] call _assert;
    ["field_utilities.config", isClass (configFile >> "CfgPatches" >> "YFU_FieldUtils")] call _assert;
    ["advanced_systems.config", isClass (configFile >> "CfgPatches" >> "YAS_AdvSys")] call _assert;
    ["visual_support_tablet.config", isClass (configFile >> "CfgPatches" >> "YSF_Tablet")] call _assert;
    ["core.function", !isNil "YCD_fnc_initServer"] call _assert;
    ["field_utilities.function", !isNil "YFU_fnc_initServer"] call _assert;
    ["advanced_systems.function", !isNil "YAS_fnc_initServer"] call _assert;
    ["visual_support_tablet.function", !isNil "YSF_fnc_initServer"] call _assert;
    ["core.postInit", !isNil {missionNamespace getVariable "YCD_onceCache"}] call _assert;

    private _forceFailure = (paramsArray param [0, 0]) isEqualTo 1;
    ["harness.forcedFailure", !_forceFailure, format ["enabled=%1", _forceFailure]] call _assert;

    private _overall = ["PASS", "FAIL"] select (_failures > 0);
    diag_log format ["PONTIFEX_TEST|COMPLETE|status=%1|assertions=%2|failures=%3", _overall, _assertions, _failures];
};
