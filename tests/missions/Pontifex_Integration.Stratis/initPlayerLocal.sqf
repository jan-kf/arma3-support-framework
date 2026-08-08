[] spawn {
    private _startupDeadline = diag_tickTime + 60;
    waitUntil {
        uiSleep 0.25;
        (diag_tickTime > _startupDeadline) ||
        {!isNull player && {!isNil "YCD_clientInitialized"}}
    };

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
        diag_log format ["PONTIFEX_TEST|%1|client-a|%2|%3", _status, _name, _detail];
    };

    ["client.hasInterface", hasInterface, format ["actual=%1", hasInterface]] call _assert;
    ["client.notServer", !isServer, format ["isServer=%1", isServer]] call _assert;
    ["client.notDedicated", !isDedicated, format ["isDedicated=%1", isDedicated]] call _assert;
    ["client.coreInitialized", !isNil "YCD_clientInitialized", "YCD initPlayerLocal postInit"] call _assert;
    ["client.configs", (
        isClass (configFile >> "CfgPatches" >> "YCD_CORDIS") &&
        {isClass (configFile >> "CfgPatches" >> "YFU_FieldUtils")} &&
        {isClass (configFile >> "CfgPatches" >> "YAS_AdvSys")} &&
        {isClass (configFile >> "CfgPatches" >> "YSF_Tablet")}
    )] call _assert;
    ["client.functions", (
        !isNil "YCD_fnc_initPlayerLocal" &&
        {!isNil "YFU_fnc_initPlayerLocal"} &&
        {!isNil "YAS_fnc_initPlayerLocal"} &&
        {!isNil "YSF_fnc_initPlayerLocal"}
    )] call _assert;
    ["client.playerExists", !isNull player, format ["name=%1|owner=%2", name player, clientOwner]] call _assert;
    ["client.playerLocal", !isNull player && {local player}, format ["local=%1", local player]] call _assert;

    private _nonce = format ["%1-%2-%3", clientOwner, diag_tickTime, floor random 1000000];
    missionNamespace setVariable ["PONTIFEX_nonceReply", ""];
    PONTIFEX_fnc_clientNonceAck = {
        params ["_reply"];
        missionNamespace setVariable ["PONTIFEX_nonceReply", _reply];
    };
    [_nonce, clientOwner] remoteExecCall ["PONTIFEX_fnc_serverNonce", 2];

    private _nonceDeadline = diag_tickTime + 30;
    waitUntil {
        uiSleep 0.25;
        (diag_tickTime > _nonceDeadline) ||
        {(missionNamespace getVariable ["PONTIFEX_nonceReply", ""]) isEqualTo _nonce}
    };
    private _roundTrip = (missionNamespace getVariable ["PONTIFEX_nonceReply", ""]) isEqualTo _nonce;
    ["client.roundTrip", _roundTrip, format ["nonce=%1", _nonce]] call _assert;
    if (_roundTrip) then {
        [_nonce] remoteExecCall ["PONTIFEX_fnc_serverConfirm", 2];
    };

    private _overall = ["PASS", "FAIL"] select (_failures > 0);
    diag_log format ["PONTIFEX_TEST|COMPLETE|client-a|status=%1|assertions=%2|failures=%3", _overall, _assertions, _failures];
};
