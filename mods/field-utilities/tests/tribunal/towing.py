"""Server-authoritative physical towing and lifecycle coverage for Field Utilities."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_SQF = r'''
localNamespace setVariable ["YFU_TOW_OPERATIONS", createHashMap];
localNamespace setVariable ["YFU_TOW_OBJECT_CLAIMS", createHashMap];
localNamespace setVariable ["YFU_TOW_REQUESTS", createHashMap];
localNamespace setVariable ["YFU_TOW_AUDIT", []];

private _scenarioPlayer = objNull;
private _playerDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _playerDeadline}
};
private _origin = [2000,5600,0];
private _spawn = {
    params ["_class", "_offset"];
    private _object = createVehicle [_class, _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setVehiclePosition [_origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setDir 0;
    _object setFuel 0;
    _object engineOn false;
    _object setVelocity [0,0,0];
    _object setAngularVelocity [0,0,0];
    _object
};
private _tow = ["B_MRAP_01_F", [0,6,0]] call _spawn;
private _cargo = ["C_Offroad_01_F", [0,-2,0]] call _spawn;
private _otherTow = ["B_MRAP_01_F", [6,-2,0]] call _spawn;
private _unrelatedCargo = ["B_Quadbike_01_F", [0,-10,0]] call _spawn;
private _wrongCargo = ["B_supplyCrate_F", [-5,-2,0]] call _spawn;
private _objects = [_tow, _cargo, _otherTow, _unrelatedCargo, _wrongCargo];
private _ids = _objects apply {netId _x};
private _baseTow = _origin vectorAdd [0,6,0];
private _baseCargo = _origin vectorAdd [0,-2,0];
private _resetPair = {
    params ["_tow", "_cargo"];
    doStop driver _tow;
    _tow setVehiclePosition [_baseTow, [], 0, "CAN_COLLIDE"];
    _cargo setVehiclePosition [_baseCargo, [], 0, "CAN_COLLIDE"];
    {
        _x setDir 0;
        _x setVelocity [0,0,0];
        _x setAngularVelocity [0,0,0];
        _x setDamage 0;
    } forEach [_tow, _cargo];
    _tow setFuel 0;
    _cargo setFuel 0;
};
private _stableSince = -1;
private _settleDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _stable = (_objects findIf {
        isNull _x || {!local _x} || {(netId _x) isEqualTo ""}
            || {vectorMagnitude velocity _x > 0.1}
            || {vectorMagnitude angularVelocity _x > 0.1}
    }) < 0;
    if (_stable) then {
        if (_stableSince < 0) then {_stableSince = diag_tickTime;};
    } else {
        _stableSince = -1;
    };
    (_stableSince >= 0 && {diag_tickTime - _stableSince >= 1}) || {diag_tickTime > _settleDeadline}
};
private _fixtureOk = !isNull _scenarioPlayer
    && {(_objects findIf {isNull _x || {!local _x} || {(netId _x) isEqualTo ""}}) < 0}
    && {_tow isKindOf "LandVehicle"} && {_cargo isKindOf "LandVehicle"}
    && {!(_wrongCargo isKindOf "LandVehicle")}
    && {_tow distance _cargo < YFU_TOW_PAIR_RANGE};
["field.towing.fixture", _fixtureOk, format ["player=%1|owner=%2|objects=%3|distance=%4|stable=%5", netId _scenarioPlayer, owner _scenarioPlayer, _objects apply {[netId _x,typeOf _x,local _x,owner _x,getPosASL _x]}, _tow distance _cargo, _stableSince]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_SETUP", [_token, _ids], true];

private _clientReadyDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_CLIENT_READY", ""]) isEqualTo _token || {diag_tickTime > _clientReadyDeadline}};

private _placeRequesterNear = {
    params ["_object"];
    [_object] remoteExecCall ["TRIBUNAL_fnc_fieldTowPlaceRequester", owner _scenarioPlayer];
    private _deadline = diag_tickTime + 10;
    waitUntil {uiSleep 0.05; (_scenarioPlayer distance _object) < 8 || {diag_tickTime > _deadline}};
    (_scenarioPlayer distance _object) < 8
};

createVehicleCrew _tow;
private _driver = driver _tow;
private _driverGroup = group _driver;
private _drive = {
    params ["_tow", "_cargo", "_destination"];
    private _startTow = getPosASL _tow;
    private _startCargo = getPosASL _cargo;
    private _samples = [];
    _tow setFuel 1;
    (driver _tow) doMove _destination;
    private _deadline = diag_tickTime + 35;
    waitUntil {
        uiSleep 0.5;
        _samples pushBack [
            diag_tickTime, getPosASL _tow, getPosASL _cargo,
            velocity _tow, velocity _cargo, netId (getTowParent _cargo),
            (ropes _tow) apply {netId _x}
        ];
        (_tow distance2D _startTow) > 25 || {diag_tickTime > _deadline}
    };
    doStop driver _tow;
    _tow setFuel 0;
    [
        _startTow, _startCargo, getPosASL _tow, getPosASL _cargo,
        _tow distance2D _startTow, _cargo distance2D _startCargo,
        _tow distance2D _cargo, damage _tow, damage _cargo, _samples
    ]
};

private _control = [_tow, _cargo, _origin vectorAdd [0,55,0]] call _drive;
private _controlOk = (_control # 4) > 20
    && {(_control # 5) < 1}
    && {(count ropes _tow) isEqualTo 0}
    && {(ropeAttachedObjects _tow) isEqualTo []}
    && {isNull getTowParent _cargo};
["field.towing.noTowControl", _controlOk, format ["control=%1", _control]] call _assert;

[_tow, _cargo] call _resetPair;
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "attach", true];
private _activeDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (_tow getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo []
        || {diag_tickTime > _activeDeadline}
};
private _active = _tow getVariable ["YFU_TOW_ACTIVE", []];
private _attachOp = _active param [0, ""];
private _all = call YFU_fnc_towOperations;
private _tx = _all getOrDefault [_attachOp, createHashMap];
private _featureRopes = _tx getOrDefault ["ropes", []];
private _authorityOk = _attachOp isNotEqualTo ""
    && {(_tx getOrDefault ["state", ""]) isEqualTo "active"}
    && {(_tx getOrDefault ["tow", objNull]) isEqualTo _tow}
    && {(_tx getOrDefault ["cargo", objNull]) isEqualTo _cargo}
    && {_featureRopes isNotEqualTo []}
    && {(_featureRopes findIf {isNull _x || {!local _x}}) < 0}
    && {(getTowParent _cargo) isEqualTo _tow}
    && {_cargo in ropeAttachedObjects _tow}
    && {((call YFU_fnc_towObjectClaims) getOrDefault [netId _tow, ""]) isEqualTo _attachOp}
    && {((call YFU_fnc_towObjectClaims) getOrDefault [netId _cargo, ""]) isEqualTo _attachOp};
["field.towing.authority", _authorityOk, format ["active=%1|tx=%2|ropes=%3|parent=%4|locality=%5|audit=%6", _active, _tx, _featureRopes apply {netId _x}, netId (getTowParent _cargo), [_tow,_cargo] apply {[netId _x,local _x,owner _x]}, localNamespace getVariable ["YFU_TOW_AUDIT", []]]] call _assert;

private _treatment = [_tow, _cargo, _origin vectorAdd [0,55,0]] call _drive;
private _treatmentOk = (_treatment # 4) > 20
    && {(_treatment # 5) > 15}
    && {(_treatment # 5) > ((_control # 5) + 10)}
    && {(_treatment # 6) < 18}
    && {(_treatment # 8) < 0.2}
    && {(getTowParent _cargo) isEqualTo _tow}
    && {_cargo in ropeAttachedObjects _tow}
    && {(_featureRopes findIf {isNull _x}) < 0};
["field.towing.physicalTreatment", _treatmentOk, format ["controlCargo=%1|treatment=%2|featureRopes=%3", _control # 5, _treatment, _featureRopes apply {netId _x}]] call _assert;

[_tow, _cargo] call _resetPair;
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "conflict", true];
private _conflictDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _audit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
    (_audit findIf {(_x # 1) isEqualTo "active-conflict"}) >= 0
        || {diag_tickTime > _conflictDeadline}
};
private _conflictAudit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
private _conflictOk = (_conflictAudit findIf {(_x # 1) isEqualTo "active-conflict"}) >= 0
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo _active}
    && {(_featureRopes findIf {isNull _x}) < 0}
    && {(getTowParent _cargo) isEqualTo _tow};
["field.towing.conflict", _conflictOk, format ["active=%1|audit=%2", _tow getVariable ["YFU_TOW_ACTIVE", []], _conflictAudit]] call _assert;

doStop driver _tow;
_tow setFuel 0;
_unrelatedCargo setVehiclePosition [(getPosATL _tow) vectorAdd [0,-3,0], [], 0, "CAN_COLLIDE"];
_unrelatedCargo setDir getDir _tow;
private _unrelated = ropeCreate [_tow, [0,0,0], _unrelatedCargo, [0,0,0], 5];
private _unrelatedId = netId _unrelated;
private _unrelatedValid = !isNull _unrelated && {_unrelatedId isNotEqualTo ""} && {local _unrelated} && {_unrelated in ropes _tow};
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "stow", true];
private _stowDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []
        || {diag_tickTime > _stowDeadline}
};
private _scopedOk = (_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []
    && {(_featureRopes findIf {!isNull _x}) < 0}
    && {_unrelatedValid}
    && {!isNull _unrelated}
    && {(netId _unrelated) isEqualTo _unrelatedId}
    && {_unrelated in ropes _tow}
    && {isNull getTowParent _cargo}
    && {(count call YFU_fnc_towOperations) isEqualTo 0}
    && {(count call YFU_fnc_towObjectClaims) isEqualTo 0};
["field.towing.scopedStow", _scopedOk, format ["feature=%1|unrelated=%2|ropes=%3|attached=%4|parent=%5|audit=%6", _featureRopes apply {isNull _x}, [_unrelatedId,isNull _unrelated], (ropes _tow) apply {netId _x}, (ropeAttachedObjects _tow) apply {netId _x}, netId (getTowParent _cargo), localNamespace getVariable ["YFU_TOW_AUDIT", []]]] call _assert;
if (!isNull _unrelated) then {ropeDestroy _unrelated;};

[_tow, _cargo] call _resetPair;
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "break-attach", true];
private _breakAttachDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (_tow getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo [] || {diag_tickTime > _breakAttachDeadline}};
private _breakActive = _tow getVariable ["YFU_TOW_ACTIVE", []];
private _breakOp = _breakActive param [0, ""];
private _breakTx = (call YFU_fnc_towOperations) getOrDefault [_breakOp, createHashMap];
private _breakRopes = _breakTx getOrDefault ["ropes", []];
if (_breakRopes isNotEqualTo []) then {ropeDestroy (_breakRopes # 0);};
private _breakDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []
        && {(count call YFU_fnc_towOperations) isEqualTo 0}
        || {diag_tickTime > _breakDeadline}
};
private _breakAudit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
private _breakOk = _breakOp isNotEqualTo ""
    && {_breakRopes isNotEqualTo []}
    && {(_breakRopes findIf {!isNull _x}) < 0}
    && {isNull getTowParent _cargo}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {(count call YFU_fnc_towOperations) isEqualTo 0}
    && {(_breakAudit findIf {(_x # 0) isEqualTo "finalize" && {(_x # 1) isEqualTo "rope-lost"} && {(_x # 3) isEqualTo _breakOp}}) >= 0};
["field.towing.breakCleanup", _breakOk, format ["operation=%1|ropes=%2|parent=%3|audit=%4", _breakOp, _breakRopes apply {isNull _x}, netId (getTowParent _cargo), _breakAudit]] call _assert;

[_tow, _cargo] call _resetPair;
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "reuse", true];
private _reuseDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (_tow getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo [] || {diag_tickTime > _reuseDeadline}};
private _reuseActive = _tow getVariable ["YFU_TOW_ACTIVE", []];
private _reuseOp = _reuseActive param [0, ""];
private _reuseTx = (call YFU_fnc_towOperations) getOrDefault [_reuseOp, createHashMap];
private _reuseRopes = _reuseTx getOrDefault ["ropes", []];
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "reuse-stow", true];
private _reuseStowDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo [] || {diag_tickTime > _reuseStowDeadline}};
private _reuseOk = _reuseOp isNotEqualTo ""
    && {_reuseOp isNotEqualTo _breakOp}
    && {_reuseRopes isNotEqualTo []}
    && {(_reuseRopes findIf {!isNull _x}) < 0}
    && {isNull getTowParent _cargo}
    && {(count call YFU_fnc_towOperations) isEqualTo 0}
    && {(count call YFU_fnc_towObjectClaims) isEqualTo 0};
["field.towing.reuse", _reuseOk, format ["break=%1|reuse=%2|ropes=%3|audit=%4", _breakOp, _reuseOp, _reuseRopes apply {isNull _x}, localNamespace getVariable ["YFU_TOW_AUDIT", []]]] call _assert;

[_tow, _cargo] call _resetPair;
[_tow] call _placeRequesterNear;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_PHASE", "negatives", true];
private _negativeDeadline = diag_tickTime + 25;
waitUntil {
    uiSleep 0.05;
    private _audit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
    (_audit findIf {(_x # 1) isEqualTo "requester-range"}) >= 0
        && {(_audit findIf {(_x # 1) isEqualTo "cargo-vehicle"}) >= 0}
        || {diag_tickTime > _negativeDeadline}
};
private _negativeAudit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
private _negativeOk = (_negativeAudit findIf {(_x # 1) isEqualTo "requester-range"}) >= 0
    && {(_negativeAudit findIf {(_x # 1) isEqualTo "cargo-vehicle"}) >= 0}
    && {(count ropes _tow) isEqualTo 0}
    && {isNull getTowParent _cargo}
    && {(count call YFU_fnc_towOperations) isEqualTo 0}
    && {(count call YFU_fnc_towObjectClaims) isEqualTo 0};
["field.towing.negatives", _negativeOk, format ["audit=%1|ropes=%2|parent=%3", _negativeAudit, ropes _tow, netId (getTowParent _cargo)]] call _assert;

missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_RESULT", [_token, _ids, _control, _treatment, _attachOp, _breakOp, _reuseOp, localNamespace getVariable ["YFU_TOW_AUDIT", []]], true];
private _clientDoneDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDoneDeadline}};
private _clientDone = (missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_CLIENT_DONE", ""]) isEqualTo _token;

if (!isNull _driver) then {deleteVehicle _driver;};
if (!isNull _driverGroup) then {deleteGroup _driverGroup;};
{if (!isNull _x) then {deleteVehicle _x;};} forEach _objects;
localNamespace setVariable ["YFU_TOW_OPERATIONS", createHashMap];
localNamespace setVariable ["YFU_TOW_OBJECT_CLAIMS", createHashMap];
localNamespace setVariable ["YFU_TOW_REQUESTS", createHashMap];
localNamespace setVariable ["YFU_TOW_AUDIT", []];
{
    missionNamespace setVariable [_x, nil, true];
} forEach [
    "TRIBUNAL_FIELD_TOW_SETUP", "TRIBUNAL_FIELD_TOW_CLIENT_READY",
    "TRIBUNAL_FIELD_TOW_PHASE", "TRIBUNAL_FIELD_TOW_RESULT",
    "TRIBUNAL_FIELD_TOW_CLIENT_DONE"
];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_ids findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
private _cleanupOk = _clientDone
    && {(_ids findIf {!isNull objectFromNetId _x}) < 0}
    && {(count call YFU_fnc_towOperations) isEqualTo 0}
    && {(count call YFU_fnc_towObjectClaims) isEqualTo 0}
    && {(localNamespace getVariable ["YFU_TOW_AUDIT", []]) isEqualTo []};
["field.towing.cleanup", _cleanupOk, format ["clientDone=%1|remaining=%2|operations=%3|claims=%4", _clientDone, _ids select {!isNull objectFromNetId _x}, count call YFU_fnc_towOperations, count call YFU_fnc_towObjectClaims]] call _assert;
'''


CLIENT_SQF = r'''
uiNamespace setVariable ["YFU_TOW_RESULTS", []];
private _setup = [];
private _setupDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    _setup = missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_SETUP", []];
    (count _setup) isEqualTo 2 || {diag_tickTime > _setupDeadline}
};
private _ids = _setup param [1, []];
private _objects = _ids apply {objectFromNetId _x};
private _objectsDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _objects = _ids apply {objectFromNetId _x};
    (count _objects) isEqualTo 5 && {(_objects findIf {isNull _x}) < 0}
        || {diag_tickTime > _objectsDeadline}
};
private _tow = _objects param [0, objNull];
private _cargo = _objects param [1, objNull];
private _otherTow = _objects param [2, objNull];
private _unrelatedCargo = _objects param [3, objNull];
private _wrongCargo = _objects param [4, objNull];
TRIBUNAL_fnc_fieldTowPlaceRequester = {
    params ["_object"];
    if (hasInterface && {!isNull _object}) then {
        player setPosATL ((getPosATL _object) vectorAdd [5,0,0]);
        player setVelocity [0,0,0];
    };
};
if (!isNull _tow) then {
    player setPosATL ((getPosATL _tow) vectorAdd [2,0,0]);
    player setVelocity [0,0,0];
    uiSleep 1;
};

private _findAction = {
    params ["_nodes", "_wanted"];
    private _found = [];
    {
        _x params ["_data", "_children"];
        if ((_data param [0, ""]) isEqualTo _wanted) exitWith {_found = _data};
        private _child = [_children, _wanted] call _findAction;
        if (_child isNotEqualTo []) exitWith {_found = _child};
    } forEach _nodes;
    _found
};
[_tow] call ace_interact_menu_fnc_compileMenu;
private _class = typeOf _tow call ace_common_fnc_getConfigName;
private _root = [ace_interact_menu_ActNamespace getOrDefault [_class, []], "TowActions"] call _findAction;
private _children = [_tow, player, []] call YOSHI_towRopeActions;
private _attachRows = _children select {
    private _data = _x param [0, []];
    private _args = _data param [6, []];
    (count _args) isEqualTo 2 && {(_args # 0) isEqualTo _tow} && {(_args # 1) isEqualTo _cargo}
};
private _attach = if (_attachRows isEqualTo []) then {[]} else {(_attachRows # 0) # 0};
private _args = _attach param [6, []];
private _condition = _attach param [4, {false}];
private _relevant = if (_attach isEqualTo []) then {false} else {[_tow, player, _args] call _condition};
private _actionOk = !isNull _tow && {!isNull _cargo}
    && {!local _tow} && {!local _cargo}
    && {_root isNotEqualTo []}
    && {(count _attachRows) isEqualTo 1}
    && {_args isEqualTo [_tow, _cargo]}
    && {_relevant};
["field.towing.clientAction", _actionOk, format ["root=%1|children=%2|attach=%3|args=%4|relevant=%5|objects=%6", _root param [0,""], _children apply {(_x # 0) param [0,""]}, _attach param [0,""], _args apply {netId _x}, _relevant, _objects apply {[netId _x,local _x,owner _x]}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_CLIENT_READY", _token, true];

private _waitPhase = {
    params ["_phase", ["_timeout", 60]];
    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.05;
        (missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_PHASE", ""]) isEqualTo _phase
            || {diag_tickTime > _deadline}
    };
    (missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_PHASE", ""]) isEqualTo _phase
};
private _moveRequesterNear = {
    params ["_object"];
    player setPosATL ((getPosATL _object) vectorAdd [5,0,0]);
    player setVelocity [0,0,0];
    uiSleep 1.5;
};
private _waitResult = {
    params ["_operationId", ["_timeout", 20]];
    private _row = [];
    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.05;
        private _rows = uiNamespace getVariable ["YFU_TOW_RESULTS", []];
        private _matches = _rows select {(_x # 0) isEqualTo _operationId};
        if (_matches isNotEqualTo []) then {_row = _matches # ((count _matches) - 1);};
        _row isNotEqualTo [] || {diag_tickTime > _deadline}
    };
    _row
};

["attach"] call _waitPhase;
[_tow] call _moveRequesterNear;
private _attachOp = format ["%1-attach", _token];
[_tow, _cargo, _attachOp] call YOSHI_deployTowRopes;
private _attachResult = [_attachOp] call _waitResult;
private _attachOk = (_attachResult param [1, false])
    && {(_attachResult param [2, ""]) isEqualTo "accepted"}
    && {(_attachResult param [3, ""]) isEqualTo netId _tow}
    && {(_attachResult param [4, ""]) isEqualTo netId _cargo}
    && {(_attachResult param [5, []]) isNotEqualTo []}
    && {(_attachResult param [6, ""]) isEqualTo "active"}
    && {(_attachResult param [7, -1]) isEqualTo clientOwner};
["field.towing.clientAttachResult", _attachOk, format ["result=%1|owner=%2", _attachResult, clientOwner]] call _assert;

private _replicaDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (_tow getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo []
        && {_cargo in ropeAttachedObjects _tow}
        && {(ropes _tow apply {netId _x}) isNotEqualTo []}
        || {diag_tickTime > _replicaDeadline}
};
private _active = _tow getVariable ["YFU_TOW_ACTIVE", []];
private _replicaOk = (_active param [0, ""]) isEqualTo _attachOp
    && {(_active param [1, ""]) isEqualTo netId _tow}
    && {(_active param [2, ""]) isEqualTo netId _cargo}
    && {(_active param [3, []]) isEqualTo (_attachResult param [5, []])}
    && {!local _cargo}
    && {isNull getTowParent _cargo}
    && {_cargo in ropeAttachedObjects _tow}
    && {(ropes _tow apply {netId _x}) isEqualTo (_attachResult param [5, []])};
["field.towing.clientReplica", _replicaOk, format ["active=%1|result=%2|ropes=%3|parent=%4|locality=%5", _active, _attachResult, ropes _tow apply {netId _x}, netId (getTowParent _cargo), [_tow,_cargo] apply {[local _x,owner _x]}]] call _assert;

["conflict"] call _waitPhase;
[_tow] call _moveRequesterNear;
private _conflictOp = format ["%1-conflict", _token];
[_tow, _unrelatedCargo, _conflictOp] call YFU_fnc_towRequestAttach;
private _conflictResult = [_conflictOp] call _waitResult;
private _conflictOk = !(_conflictResult param [1, true])
    && {(_conflictResult param [2, ""]) isEqualTo "active-conflict"}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo _active}
    && {(_cargo getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo _active};
["field.towing.clientConflict", _conflictOk, format ["result=%1|active=%2", _conflictResult, _tow getVariable ["YFU_TOW_ACTIVE", []]]] call _assert;

["stow"] call _waitPhase;
[_tow] call _moveRequesterNear;
private _stowOp = format ["%1-stow", _token];
[_tow, _stowOp] call YFU_fnc_towRequestStow;
private _stowResult = [_stowOp] call _waitResult;
private _stowOk = (_stowResult param [1, false])
    && {(_stowResult param [2, ""]) isEqualTo "stowed"}
    && {(_stowResult param [3, ""]) isEqualTo netId _tow}
    && {(_stowResult param [4, ""]) isEqualTo netId _cargo}
    && {(_stowResult param [6, ""]) isEqualTo "detached"};
["field.towing.clientScopedStow", _stowOk, format ["result=%1|ropes=%2|attached=%3|parent=%4", _stowResult, ropes _tow apply {netId _x}, ropeAttachedObjects _tow apply {netId _x}, netId (getTowParent _cargo)]] call _assert;

["break-attach"] call _waitPhase;
[_tow] call _moveRequesterNear;
private _breakOp = format ["%1-break", _token];
[_tow, _cargo, _breakOp] call YFU_fnc_towRequestAttach;
private _breakAttach = [_breakOp] call _waitResult;
private _breakRows = [];
private _breakDeadline = diag_tickTime + 25;
waitUntil {
    uiSleep 0.05;
    _breakRows = (uiNamespace getVariable ["YFU_TOW_RESULTS", []]) select {(_x # 0) isEqualTo _breakOp};
    (count _breakRows) >= 2 || {diag_tickTime > _breakDeadline}
};
private _breakOk = (_breakAttach param [1, false])
    && {(_breakAttach param [2, ""]) isEqualTo "accepted"}
    && {(count _breakRows) >= 2}
    && {((_breakRows # ((count _breakRows)-1)) # 2) isEqualTo "rope-lost"}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {isNull getTowParent _cargo};
["field.towing.clientBreak", _breakOk, format ["rows=%1|active=%2|parent=%3", _breakRows, _tow getVariable ["YFU_TOW_ACTIVE", []], netId (getTowParent _cargo)]] call _assert;

["reuse"] call _waitPhase;
[_tow] call _moveRequesterNear;
private _reuseOp = format ["%1-reuse", _token];
[_tow, _cargo, _reuseOp] call YFU_fnc_towRequestAttach;
private _reuseResult = [_reuseOp] call _waitResult;
["reuse-stow"] call _waitPhase;
[_tow] call _moveRequesterNear;
private _reuseStowOp = format ["%1-reuse-stow", _token];
[_tow, _reuseStowOp] call YFU_fnc_towRequestStow;
private _reuseStow = [_reuseStowOp] call _waitResult;
private _reuseOk = (_reuseResult param [1, false])
    && {(_reuseResult param [2, ""]) isEqualTo "accepted"}
    && {(_reuseStow param [1, false])}
    && {(_reuseStow param [2, ""]) isEqualTo "stowed"}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {isNull getTowParent _cargo};
["field.towing.clientReuse", _reuseOk, format ["attach=%1|stow=%2|active=%3", _reuseResult, _reuseStow, _tow getVariable ["YFU_TOW_ACTIVE", []]]] call _assert;

["negatives"] call _waitPhase;
private _playerASL = getPosASL player;
player setPosASL (_playerASL vectorAdd [40,0,0]);
uiSleep 0.5;
private _farOp = format ["%1-far", _token];
[_tow, _cargo, _farOp] call YFU_fnc_towRequestAttach;
private _farResult = [_farOp] call _waitResult;
player setPosASL _playerASL;
uiSleep 0.2;
private _wrongOp = format ["%1-wrong", _token];
[_tow, _wrongCargo, _wrongOp] call YFU_fnc_towRequestAttach;
private _wrongResult = [_wrongOp] call _waitResult;
private _negativeOk = !(_farResult param [1, true])
    && {(_farResult param [2, ""]) isEqualTo "requester-range"}
    && {!(_wrongResult param [1, true])}
    && {(_wrongResult param [2, ""]) isEqualTo "cargo-vehicle"}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {(count ropes _tow) isEqualTo 0}
    && {isNull getTowParent _cargo};
["field.towing.clientNegatives", _negativeOk, format ["far=%1|wrong=%2|active=%3|ropes=%4", _farResult, _wrongResult, _tow getVariable ["YFU_TOW_ACTIVE", []], ropes _tow]] call _assert;

private _serverResult = [];
private _serverDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _serverResult = missionNamespace getVariable ["TRIBUNAL_FIELD_TOW_RESULT", []];
    (count _serverResult) isEqualTo 8 || {diag_tickTime > _serverDeadline}
};
private _identityOk = (_serverResult param [0, ""]) isEqualTo _token
    && {(_serverResult param [1, []]) isEqualTo _ids}
    && {(_serverResult param [4, ""]) isEqualTo _attachOp}
    && {(_serverResult param [5, ""]) isEqualTo _breakOp}
    && {(_serverResult param [6, ""]) isEqualTo _reuseOp};
["field.towing.clientIdentity", _identityOk, format ["server=%1|clientOps=%2", _serverResult, [_attachOp,_breakOp,_reuseOp]]] call _assert;
uiNamespace setVariable ["YFU_TOW_RESULTS", []];
missionNamespace setVariable ["TRIBUNAL_FIELD_TOW_CLIENT_DONE", _token, true];
'''


CONTROL_ASSERTIONS = ["field.towing.fixture", "field.towing.noTowControl"]
TREATMENT_ASSERTIONS = [
    "field.towing.authority", "field.towing.physicalTreatment",
    "field.towing.clientAction", "field.towing.clientAttachResult",
    "field.towing.clientReplica",
]
LIFECYCLE_ASSERTIONS = [
    "field.towing.conflict", "field.towing.scopedStow",
    "field.towing.breakCleanup", "field.towing.reuse",
    "field.towing.clientConflict", "field.towing.clientScopedStow",
    "field.towing.clientBreak", "field.towing.clientReuse",
]
NEGATIVE_ASSERTIONS = [
    "field.towing.negatives", "field.towing.clientNegatives",
    "field.towing.clientIdentity", "field.towing.cleanup",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "fieldutils-towing",
        "version": 1,
        "feature_family": "pontifex-field-utilities-towing",
        "name": "Field Utilities authoritative physical towing",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "mods/field-utilities/tests/tribunal/towing.py",
            "applicability": "Arma 3 dedicated multiplayer with one authenticated client and server-owned land-vehicle fixture",
            "participants": {
                "server": "authoritative towing transaction, rope owner, AI movement owner, and lifecycle finalizer",
                "client-a": "registered-action observer, authenticated requester, result and replication observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:towing",
        "label": "Field Utilities land-vehicle towing",
        "kind": "product_behavior",
        "aliases": ["Field towing", "TowActions"],
        "biki_context": ["biki-page:11222", "biki-page:11227", "biki-page:16747", "biki-page:16751", "biki-page:32302", "biki-page:29427", "biki-page:34337"],
    },
    "arms": [
        {
            "key": "no_tow_control",
            "role": "baseline",
            "description": "The exact AI-driven tower moves while the nearby unconnected cargo remains stationary",
            "assertions": CONTROL_ASSERTIONS,
        },
        {
            "key": "authoritative_tow",
            "role": "treatment",
            "description": "The same AI movement with one authenticated exact-pair transaction physically tows the cargo",
            "assertions": TREATMENT_ASSERTIONS,
        },
        {
            "key": "lifecycle",
            "role": "treatment",
            "description": "Conflict rejection, exact scoped stow, rope-loss finalization, and reuse retire only feature-owned state",
            "assertions": LIFECYCLE_ASSERTIONS,
        },
        {
            "key": "invalid_requests",
            "role": "negative_control",
            "description": "Delivered distant-requester and wrong-class requests cannot create rope, parent, or transaction state",
            "assertions": NEGATIVE_ASSERTIONS,
        },
    ],
    "causal_relationships": [
        {
            "key": "tow-v-no-tow",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "authoritative_tow",
            "target": "no_tow_control",
            "controlled_dimensions": ["exact vehicles", "start pose", "AI driver", "destination", "terrain", "movement bound"],
        },
        {
            "key": "accepted-v-invalid",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "authoritative_tow",
            "target": "invalid_requests",
            "controlled_dimensions": ["request endpoint", "requesting client", "tower identity", "mission"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:field-utilities:towing-physical",
            "text": "An authenticated nearby player can establish one exact server-authoritative land-vehicle tow whose cargo physically follows the moving tower, unlike the same no-tow control.",
            "intended_use": "primary_result",
            "assertions": CONTROL_ASSERTIONS + TREATMENT_ASSERTIONS,
            "rationale": "Exact paired trajectories, retained rope identities, native tow-parent state, authority telemetry, client replication, and a matched no-tow control establish the physical effect.",
        },
        {
            "id": "pontifex:field-utilities:towing-lifecycle",
            "text": "Active conflicts are rejected; stow and rope loss retire exactly feature-owned rope/parent/claim state; the same pair can then tow again; invalid requests cause no mutation.",
            "intended_use": "primary_result",
            "assertions": LIFECYCLE_ASSERTIONS + NEGATIVE_ASSERTIONS,
            "rationale": "Delivered negative receipts, an independently injected unrelated rope, exact handle destruction, monitor evidence, reuse, and final cleanup close stale-state and broad-destruction false-PASS paths.",
        },
    ],
    "unresolved": [
        "Player-owned vehicle topology, ownership migration, client-B/JIP, natural projectile-cut rope loss, unconfigured-class geometry breadth, and deletion/disconnect during an active tow remain outside this proof."
    ],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-towing",
    tier="gameplay",
    server_expected=frozenset(CONTROL_ASSERTIONS + [
        "field.towing.authority", "field.towing.physicalTreatment",
        "field.towing.conflict", "field.towing.scopedStow",
        "field.towing.breakCleanup", "field.towing.reuse",
        "field.towing.negatives", "field.towing.cleanup",
    ]),
    client_expected=frozenset([
        "field.towing.clientAction", "field.towing.clientAttachResult",
        "field.towing.clientReplica", "field.towing.clientConflict",
        "field.towing.clientScopedStow", "field.towing.clientBreak",
        "field.towing.clientReuse", "field.towing.clientNegatives",
        "field.towing.clientIdentity",
    ]),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "field-utilities", "feature": "towing"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A nearby authenticated player can establish one exact land-vehicle tow; the same physical movement tows cargo only in the treatment, conflicts and invalid requests fail closed, and stow or rope loss removes exactly feature-owned state before reuse.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="The prior client-side helper discarded rope identity and broadly destroyed ropes. The refined scenario proves server authority, exact transaction/rope identity, matched physical causality, scoped cleanup, break finalization, reuse, negative stimuli, replication, and bounded completion.",
        dependencies=("ACE 3.21 registered action tree", "native rope and tow-parent commands", "one authenticated client"),
        evidence_types=frozenset({"ace-action-data", "exact-identity", "locality", "paired-trajectory", "physical-effect", "authoritative-state", "negative-control", "replication", "cleanup"}),
        locality_requirements="The server owns fixture vehicles, ropes, AI movement, transaction and finalizer; client-a owns action resolution and authenticated requests. Player-owned vehicles and ownership migration are not claimed.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
