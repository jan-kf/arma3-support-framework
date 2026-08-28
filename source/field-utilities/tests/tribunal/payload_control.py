"""Permanent live-control, HUD, cycling, and deployment contract for Payload Manager."""

from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-payload-control",
    tier="gameplay",
    server_expected=frozenset({
        "payloadControl.fixture",
        "payloadControl.authority",
        "payloadControl.effects",
        "payloadControl.cleanup",
    }),
    client_expected=frozenset({
        "payloadControl.contextGate",
        "payloadControl.control",
        "payloadControl.hud",
        "payloadControl.cycle",
        "payloadControl.grenades",
        "payloadControl.empty",
        "payloadControl.satchel",
    }),
    server_sqf=r'''
private _scenarioPlayer = objNull;
private _playerDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _playerDeadline}
};
private _origin = if (isNull _scenarioPlayer) then {[4740, 2840, 0]} else {getPosATL _scenarioPlayer};
private _spawnUav = {
    params ["_offset", "_allowDamage"];
    private _uav = createVehicle ["B_UAV_01_F", _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _uav setPosATL (_origin vectorAdd _offset);
    createVehicleCrew _uav;
    _uav setFuel 0;
    _uav engineOn false;
    _uav allowDamage _allowDamage;
    _uav
};
private _grenadeUav = [[4, 0, 0], false] call _spawnUav;
private _satchelUav = [[12, 0, 0], true] call _spawnUav;
private _grenadeRecords = [
    ["b8-hand", "HandGrenade", "M67 fragmentation grenade", 1, "drop", "GrenadeHand"],
    ["b8-mini", "MiniGrenade", "RGO fragmentation grenade", 1, "drop", "GrenadeHand"]
];
private _satchelRecords = [
    ["b8-satchel", "SatchelCharge_Remote_Mag", "Satchel charge", 8, "satchel", "ModuleExplosive_SatchelCharge_F"]
];
_grenadeUav setVariable ["YFU_PAYLOAD_STATE", [40, _grenadeRecords, 0], true];
_satchelUav setVariable ["YFU_PAYLOAD_STATE", [70, _satchelRecords, 0], true];
private _ids = [netId _grenadeUav, netId _satchelUav];
missionNamespace setVariable ["TRIBUNAL_PAYLOAD_CONTROL_FIXTURE", [_token, _ids], true];
private _fixtureOk = !isNull _scenarioPlayer
    && {!isNull _grenadeUav && {!isNull driver _grenadeUav}}
    && {!isNull _satchelUav && {!isNull driver _satchelUav}}
    && {(_ids findIf {_x isEqualTo ""}) < 0}
    && {local _grenadeUav && {local _satchelUav}}
    && {[_grenadeUav] call YFU_fnc_payloadEligible}
    && {[_satchelUav] call YFU_fnc_payloadEligible};
["payloadControl.fixture", _fixtureOk, format ["player=%1|ids=%2|drivers=%3|locality=%4|states=%5", netId _scenarioPlayer, _ids, [netId driver _grenadeUav, netId driver _satchelUav], [local _grenadeUav, owner _grenadeUav, local _satchelUav, owner _satchelUav], [[_grenadeUav] call YFU_fnc_payloadState, [_satchelUav] call YFU_fnc_payloadState]]] call _assert;

private _doneDeadline = diag_tickTime + 75;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_PAYLOAD_CONTROL_DONE", ""]) isEqualTo _token
        || {diag_tickTime > _doneDeadline}
};
private _audit = localNamespace getVariable ["YFU_PAYLOAD_AUDIT", []];
private _ours = _audit select {
    private _operation = _x param [1, ""];
    _operation isEqualTo "tribunal-b8-no-control" || {_operation find "payload-" isEqualTo 0}
};
private _accepted = _ours select {_x param [2, false]};
private _rejected = _ours select {!(_x param [2, false])};
private _stateGrenade = [_grenadeUav] call YFU_fnc_payloadState;
private _stateSatchel = [_satchelUav] call YFU_fnc_payloadState;
private _authorityOk = (count _accepted) isEqualTo 5
    && {(count _rejected) isEqualTo 2}
    && {{(_x # 3) isEqualTo "controller"} count _rejected isEqualTo 1}
    && {{(_x # 3) isEqualTo "empty"} count _rejected isEqualTo 1}
    && {{(_x # 3) isEqualTo "selected"} count _accepted isEqualTo 2}
    && {{(_x # 3) isEqualTo "deployed"} count _accepted isEqualTo 3}
    && {_stateGrenade isEqualTo [44, [], 0]}
    && {_stateSatchel isEqualTo [71, [], 0]};
["payloadControl.authority", _authorityOk, format ["audit=%1|grenadeState=%2|satchelState=%3", _ours, _stateGrenade, _stateSatchel]] call _assert;

private _deployments = (localNamespace getVariable ["YFU_PAYLOAD_DEPLOYMENTS", []]) select {
    (_x param [1, ""]) find "payload-" isEqualTo 0
};
private _payloadClasses = _deployments apply {_x # 5};
private _effectClasses = _deployments apply {_x # 6};
private _effectIds = _deployments apply {_x # 7};
private _effectPositions = _deployments apply {_x # 8};
private _nearExactUav = true;
{
    private _uavAtDeployment = _x # 10;
    private _expectedOffset = if ((_x # 5) isEqualTo "SatchelCharge_Remote_Mag") then {0} else {0.15};
    if (((( _x # 8) distance _uavAtDeployment) - _expectedOffset) > 0.35) then {_nearExactUav = false;};
} forEach _deployments;
private _effectsOk = (count _deployments) isEqualTo 3
    && {_payloadClasses isEqualTo ["MiniGrenade", "HandGrenade", "SatchelCharge_Remote_Mag"]}
    && {_effectClasses isEqualTo ["GrenadeHand", "GrenadeHand", "ModuleExplosive_SatchelCharge_F"]}
    && {(_effectIds findIf {_x isEqualTo ""}) < 0}
    && {_nearExactUav}
    && {!alive _satchelUav};
["payloadControl.effects", _effectsOk, format ["deployments=%1|satchelAlive=%2", _deployments, alive _satchelUav]] call _assert;

private _crew = (crew _grenadeUav) + (crew _satchelUav);
{if (!isNull _x) then {deleteVehicle _x;};} forEach _crew;
{private _effect = objectFromNetId _x; if (!isNull _effect) then {deleteVehicle _effect;};} forEach _effectIds;
{if (!isNull _x) then {deleteVehicle _x;};} forEach [_grenadeUav, _satchelUav];
missionNamespace setVariable ["TRIBUNAL_PAYLOAD_CONTROL_FIXTURE", nil, true];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_ids findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
["payloadControl.cleanup", (missionNamespace getVariable ["TRIBUNAL_PAYLOAD_CONTROL_DONE", ""]) isEqualTo _token && {(_ids findIf {!isNull objectFromNetId _x}) < 0} && {(_effectIds findIf {!isNull objectFromNetId _x}) < 0}, format ["done=%1|uavs=%2|effects=%3", missionNamespace getVariable ["TRIBUNAL_PAYLOAD_CONTROL_DONE", ""], _ids select {!isNull objectFromNetId _x}, _effectIds select {!isNull objectFromNetId _x}]] call _assert;
''',
    client_sqf=r'''
disableSerialization;
private _fixture = [];
private _fixtureDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _fixture = missionNamespace getVariable ["TRIBUNAL_PAYLOAD_CONTROL_FIXTURE", []];
    (count _fixture) isEqualTo 2 || {diag_tickTime > _fixtureDeadline}
};
private _ids = _fixture param [1, []];
private _grenadeUav = objNull;
private _satchelUav = objNull;
private _objectsDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    _grenadeUav = objectFromNetId (_ids param [0, ""]);
    _satchelUav = objectFromNetId (_ids param [1, ""]);
    (!isNull _grenadeUav && {!isNull _satchelUav} && {!isNull driver _grenadeUav} && {!isNull driver _satchelUav}) || {diag_tickTime > _objectsDeadline}
};
uiNamespace setVariable ["YFU_PAYLOAD_RESULTS", []];
private _originalLoadout = getUnitLoadout player;
player linkItem "B_UavTerminal";
private _terminalLinked = "B_UavTerminal" in assignedItems player;
private _originalColor = missionNamespace getVariable ["YFU_monochromeBaseColor", [0.15, 0.95, 0.15, 1]];
missionNamespace setVariable ["YFU_monochromeBaseColor", [0.2, 0.6, 0.9, 1]];

private _localGate = isNull (call YFU_fnc_payloadControlledUAV) && {!(["next"] call YFU_fnc_payloadControlRequest)};
["tribunal-b8-no-control", "next", _grenadeUav] remoteExecCall ["YFU_fnc_payloadControlServer", 2];
private _noControl = [];
private _noControlDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
    private _at = _rows findIf {(_x # 0) isEqualTo "tribunal-b8-no-control"};
    if (_at >= 0) then {_noControl = _rows # _at;};
    _noControl isNotEqualTo [] || {diag_tickTime > _noControlDeadline}
};
["payloadControl.contextGate", _localGate && {!(_noControl param [1, true])} && {(_noControl param [2, ""]) isEqualTo "controller"}, format ["localGate=%1|server=%2|connected=%3", _localGate, _noControl, getConnectedUAV player]] call _assert;

private _request = {
    params ["_action"];
    private _before = count (uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []]);
    private _sent = [_action] call YFU_fnc_payloadControlRequest;
    private _row = [];
    private _deadline = diag_tickTime + 8;
    waitUntil {
        uiSleep 0.05;
        private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
        if ((count _rows) > _before) then {_row = _rows # ((count _rows) - 1);};
        _row isNotEqualTo [] || {diag_tickTime > _deadline}
    };
    [_sent, _row]
};

private _terminalConnected = player connectTerminalToUAV _grenadeUav;
player remoteControl (driver _grenadeUav);
private _controlDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    private _control = UAVControl _grenadeUav;
    ((_control param [0, objNull]) isEqualTo player && {(_control param [1, ""]) in ["DRIVER", "GUNNER"]}) || {diag_tickTime > _controlDeadline}
};
private _control = UAVControl _grenadeUav;
private _controlled = call YFU_fnc_payloadControlledUAV;
["payloadControl.control", _terminalLinked && {_terminalConnected} && {_controlled isEqualTo _grenadeUav} && {(_control # 0) isEqualTo player} && {(_control # 1) in ["DRIVER", "GUNNER"]}, format ["terminal=%1|connected=%2|control=%3|resolved=%4|driver=%5", _terminalLinked, netId getConnectedUAV player, _control, netId _controlled, netId driver _grenadeUav]] call _assert;

private _hud = displayNull;
private _hudControl = controlNull;
private _hudText = "";
private _hudColor = [];
private _hudDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    _hud = uiNamespace getVariable ["YFU_Payload_HUD_Display", displayNull];
    _hudControl = if (isNull _hud) then {controlNull} else {_hud displayCtrl 98351};
    _hudText = if (isNull _hudControl) then {""} else {ctrlText _hudControl};
    _hudColor = if (isNull _hudControl) then {[]} else {ctrlTextColor _hudControl};
    (!isNull _hudControl
        && {"M67 fragmentation grenade" in _hudText}
        && {(count _hudColor) isEqualTo 4}
        && {abs ((_hudColor # 0) - 0.2) < 0.01}
        && {abs ((_hudColor # 1) - 0.6) < 0.01}
        && {abs ((_hudColor # 2) - 0.9) < 0.01})
        || {diag_tickTime > _hudDeadline}
};
private _nextText = ["nextPayload"] call YFU_fnc_payloadBindingText;
private _deployText = ["deployPayload"] call YFU_fnc_payloadBindingText;
private _hudOk = !isNull _hud
    && {"M67 fragmentation grenade" in _hudText}
    && {_nextText in _hudText}
    && {_deployText in _hudText}
    && {(count _hudColor) isEqualTo 4}
    && {abs ((_hudColor # 0) - 0.2) < 0.01}
    && {abs ((_hudColor # 1) - 0.6) < 0.01}
    && {abs ((_hudColor # 2) - 0.9) < 0.01};
["payloadControl.hud", _hudOk, format ["text=%1|color=%2|next=%3|deploy=%4", _hudText, _hudColor, _nextText, _deployText]] call _assert;

private _nextResult = ["next"] call _request;
private _stateAfterNext = [_grenadeUav] call YFU_fnc_payloadState;
private _nextHudDeadline = diag_tickTime + 3;
waitUntil {
    uiSleep 0.05;
    _hudText = if (isNull _hudControl) then {""} else {ctrlText _hudControl};
    "RGO fragmentation grenade" in _hudText || {diag_tickTime > _nextHudDeadline}
};
["payloadControl.cycle", (_nextResult # 0) && {((_nextResult # 1) param [1, false])} && {((_nextResult # 1) param [2, ""]) isEqualTo "selected"} && {_stateAfterNext # 0 isEqualTo 41} && {_stateAfterNext # 2 isEqualTo 1} && {"RGO fragmentation grenade" in _hudText}, format ["result=%1|state=%2|hud=%3", _nextResult, _stateAfterNext, _hudText]] call _assert;

private _deployMini = ["deploy"] call _request;
private _stateAfterMini = [_grenadeUav] call YFU_fnc_payloadState;
private _nextSingle = ["next"] call _request;
private _stateAfterSingle = [_grenadeUav] call YFU_fnc_payloadState;
private _deployHand = ["deploy"] call _request;
private _stateAfterHand = [_grenadeUav] call YFU_fnc_payloadState;
private _emptyHudDeadline = diag_tickTime + 3;
waitUntil {
    uiSleep 0.05;
    _hudText = if (isNull _hudControl) then {""} else {ctrlText _hudControl};
    "EMPTY" in _hudText || {diag_tickTime > _emptyHudDeadline}
};
private _grenadesOk = ((_deployMini # 1) param [1, false])
    && {((_deployMini # 1) param [2, ""]) isEqualTo "deployed"}
    && {_stateAfterMini # 0 isEqualTo 42}
    && {(count (_stateAfterMini # 1)) isEqualTo 1}
    && {((_stateAfterMini # 1) # 0 # 1) isEqualTo "HandGrenade"}
    && {((_nextSingle # 1) param [1, false])}
    && {_stateAfterSingle isEqualTo [43, _stateAfterMini # 1, 0]}
    && {((_deployHand # 1) param [1, false])}
    && {_stateAfterHand isEqualTo [44, [], 0]}
    && {"EMPTY" in _hudText};
["payloadControl.grenades", _grenadesOk, format ["mini=%1|afterMini=%2|single=%3|afterSingle=%4|hand=%5|afterHand=%6|hud=%7", _deployMini, _stateAfterMini, _nextSingle, _stateAfterSingle, _deployHand, _stateAfterHand, _hudText]] call _assert;

private _emptyResult = ["deploy"] call _request;
private _stateAfterEmpty = [_grenadeUav] call YFU_fnc_payloadState;
["payloadControl.empty", (_emptyResult # 0) && {!((_emptyResult # 1) param [1, true])} && {((_emptyResult # 1) param [2, ""]) isEqualTo "empty"} && {_stateAfterEmpty isEqualTo [44, [], 0]}, format ["result=%1|state=%2", _emptyResult, _stateAfterEmpty]] call _assert;

player remoteControl objNull;
player connectTerminalToUAV objNull;
uiSleep 0.5;
player connectTerminalToUAV _satchelUav;
player remoteControl (driver _satchelUav);
private _satchelControlDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (call YFU_fnc_payloadControlledUAV) isEqualTo _satchelUav || {diag_tickTime > _satchelControlDeadline}
};
private _satchelBefore = alive _satchelUav && {([_satchelUav] call YFU_fnc_payloadState) isEqualTo [70, [["b8-satchel", "SatchelCharge_Remote_Mag", "Satchel charge", 8, "satchel", "ModuleExplosive_SatchelCharge_F"]], 0]};
private _satchelResult = ["deploy"] call _request;
private _satchelDeathDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; !alive _satchelUav || {diag_tickTime > _satchelDeathDeadline}};
private _satchelState = [_satchelUav] call YFU_fnc_payloadState;
["payloadControl.satchel", _satchelBefore && {((_satchelResult # 1) param [1, false])} && {((_satchelResult # 1) param [2, ""]) isEqualTo "deployed"} && {_satchelState isEqualTo [71, [], 0]} && {!alive _satchelUav}, format ["before=%1|result=%2|state=%3|alive=%4|damage=%5", _satchelBefore, _satchelResult, _satchelState, alive _satchelUav, damage _satchelUav]] call _assert;

player remoteControl objNull;
player connectTerminalToUAV objNull;
missionNamespace setVariable ["YFU_monochromeBaseColor", _originalColor];
player setUnitLoadout _originalLoadout;
missionNamespace setVariable ["TRIBUNAL_PAYLOAD_CONTROL_DONE", _token, true];
''',
    metadata={
        "product": "field-utilities",
        "feature": "payload-manager-live-control-deployment",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="An authenticated player must actually control an eligible small UAV before configured payload controls work; the persistent themed HUD shows the selected occupied UAV-owned payload and live bindings, cycling traverses only occupied entries, grenade and full-capacity satchel deployments consume exactly one selected record and create the specified causal effect, and empty deployment refuses without mutation.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="This closes the final supported Payload Manager slice with exact UAV/payload/effect identities, replicated revision transitions, real configured control callbacks, controller and empty negatives, HUD state, server receipts, satchel UAV death, and cleanup.",
        dependencies=("one independently authenticated client", "two server-local B_UAV_01_F fixtures with autonomous crew", "CBA keybindings and themed RscTitles HUD"),
        evidence_types=frozenset({"exact-netid", "uav-control", "server-audit", "deployment-receipt", "state-transition", "negative-control", "hud-control-state", "cleanup"}),
        locality_requirements="The dedicated server owns UAV manifests and spawned effects; client-a owns authentic terminal/remote control and HUD observation. Client-B/JIP, mortars, arbitrary UAV classes, broader ACE removal, and sound/pixel matrices are excluded.",
    ),
)
