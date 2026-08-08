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
        diag_log format ["PONTIFEX_TEST|%1|server|%2|%3", _status, _name, _detail];
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

    private _requireClient = (paramsArray param [1, 0]) isEqualTo 1;
    if (_requireClient) then {
        missionNamespace setVariable ["PONTIFEX_clientHello", []];
        missionNamespace setVariable ["PONTIFEX_clientConfirmed", ""];

        PONTIFEX_fnc_serverNonce = {
            params ["_nonce", "_playerOwner"];
            private _sender = remoteExecutedOwner;
            private _matchingPlayer = allPlayers select {owner _x isEqualTo _sender};
            missionNamespace setVariable [
                "PONTIFEX_clientHello",
                [_nonce, _sender, _playerOwner, _matchingPlayer]
            ];
            [_nonce] remoteExecCall ["PONTIFEX_fnc_clientNonceAck", _sender];
        };
        PONTIFEX_fnc_serverConfirm = {
            params ["_nonce"];
            missionNamespace setVariable ["PONTIFEX_clientConfirmed", _nonce];
        };

        private _clientDeadline = diag_tickTime + 90;
        waitUntil {
            uiSleep 0.25;
            (diag_tickTime > _clientDeadline) ||
            {!(missionNamespace getVariable ["PONTIFEX_clientHello", []] isEqualTo [])}
        };

        private _hello = missionNamespace getVariable ["PONTIFEX_clientHello", []];
        private _nonce = _hello param [0, ""];
        private _sender = _hello param [1, -1];
        private _reportedOwner = _hello param [2, -2];
        private _matching = _hello param [3, []];
        private _playerUnit = _matching param [0, objNull];

        ["server.clientCount", (count allPlayers) isEqualTo 1, format ["actual=%1", count allPlayers]] call _assert;
        [
            "server.playerIdentity",
            !isNull _playerUnit && {_sender > 2} && {_sender isEqualTo _reportedOwner} && {name _playerUnit isNotEqualTo ""},
            format ["owner=%1|reportedOwner=%2|name=%3|uidPresent=%4", _sender, _reportedOwner, name _playerUnit, getPlayerUID _playerUnit isNotEqualTo ""]
        ] call _assert;
        [
            "server.clientNotHeadless",
            !isNull _playerUnit && {!(_playerUnit isKindOf "HeadlessClient_F")},
            format ["type=%1", typeOf _playerUnit]
        ] call _assert;

        private _confirmDeadline = diag_tickTime + 30;
        waitUntil {
            uiSleep 0.25;
            (diag_tickTime > _confirmDeadline) ||
            {(missionNamespace getVariable ["PONTIFEX_clientConfirmed", ""]) isEqualTo _nonce}
        };
        [
            "server.roundTrip",
            _nonce isNotEqualTo "" && {(missionNamespace getVariable ["PONTIFEX_clientConfirmed", ""]) isEqualTo _nonce},
            format ["nonce=%1", _nonce]
        ] call _assert;
    };

    private _overall = ["PASS", "FAIL"] select (_failures > 0);
    diag_log format ["PONTIFEX_TEST|COMPLETE|server|status=%1|assertions=%2|failures=%3", _overall, _assertions, _failures];
};
