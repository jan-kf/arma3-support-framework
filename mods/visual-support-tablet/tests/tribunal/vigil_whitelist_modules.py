"""Authentic Eden and Zeus activation coverage for the Vigil asset whitelist."""

from tribunal.runner.model import MissionEntity, MissionSync, Scenario, ScenarioReview


SERVER_SQF = r'''
private _assetA = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_A", objNull];
private _assetB = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_B", objNull];
private _assetC = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_C", objNull];
private _control = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_CONTROL", objNull];
private _expectedBase = [_assetA, _assetB];
private _sameObjects = {params ["_actual", "_expected"]; (count _actual) isEqualTo count _expected && {(_expected findIf {!(_x in _actual)}) < 0}};
{
    private _object = _x;
    if (!isNull _object) then {
        _object setVehiclePosition [[2000 + (_forEachIndex * 50), 5600, 0], [], 0, "NONE"];
        _object setDir 0;
        _object setFuel 0;
        _object engineOn false;
        _object setVelocity [0,0,0];
        _object setAngularVelocity [0,0,0];
    };
} forEach [_assetA, _assetB, _assetC, _control];
private _fixtures = [_assetA, _assetB, _assetC, _control];
private _stableSince = -1;
private _settleDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _stable = (_fixtures findIf {
        isNull _x
            || {!isTouchingGround _x}
            || {vectorMagnitude velocity _x > 0.05}
            || {vectorMagnitude angularVelocity _x > 0.05}
    }) < 0;
    if (_stable) then {
        if (_stableSince < 0) then {_stableSince = diag_tickTime;};
    } else {
        _stableSince = -1;
    };
    (_stableSince >= 0 && {diag_tickTime - _stableSince >= 1}) || {diag_tickTime > _settleDeadline}
};
private _fixtureState = _fixtures apply {
    [netId _x, getPosASL _x, velocity _x, angularVelocity _x, isTouchingGround _x]
};
private _fixturesStable = _stableSince >= 0
    && {diag_tickTime - _stableSince >= 1}
    && {(_fixtures findIf {
        isNull _x
            || {!isTouchingGround _x}
            || {vectorMagnitude velocity _x > 0.05}
            || {vectorMagnitude angularVelocity _x > 0.05}
    }) < 0};
["vigil.whitelist.fixtureStable", _fixturesStable, format ["state=%1|stableFor=%2", _fixtureState, if (_stableSince < 0) then {-1} else {diag_tickTime - _stableSince}]] call _assert;

private _auditDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (count (localNamespace getVariable ["YSF_WHITELIST_EDEN_AUDIT", []])) >= 2 || {diag_tickTime > _auditDeadline}};
private _audit = localNamespace getVariable ["YSF_WHITELIST_EDEN_AUDIT", []];
private _accepted = _audit select {_x # 6 && {(_x # 7) isEqualTo "accepted_native"}};
private _moduleIds = _accepted apply {_x # 1};
private _modules = _moduleIds apply {objectFromNetId _x};
private _initial = +(missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []]);
private _edenOk = (count _accepted) isEqualTo 2
    && {(_accepted findIf {(_x # 0) isNotEqualTo "YSF_Asset_Whitelist_Module" || {!(_x # 2)} || {!(_x # 3)} || {(_x # 4) isNotEqualTo 2} || {(_x # 5) > 2} || {(count (_x # 8)) isNotEqualTo 1}}) < 0}
    && {[_initial, _expectedBase] call _sameObjects}
    && {!(_assetC in _initial)} && {!(_control in _initial)};
["vigil.whitelist.edenAggregate", _edenOk, format ["audit=%1|initial=%2|modules=%3", _audit, _initial apply {[vehicleVarName _x, netId _x]}, _modules apply {[typeOf _x, netId _x, local _x, owner _x]}]] call _assert;
private _retained = (_modules findIf {isNull _x || {!local _x} || {owner _x isNotEqualTo 2} || {(count synchronizedObjects _x) isNotEqualTo 1}}) < 0;
["vigil.whitelist.edenRetained", _retained, format ["modules=%1|sync=%2", _modules apply {[typeOf _x, netId _x]}, _modules apply {(synchronizedObjects _x) apply {[vehicleVarName _x, netId _x]}}]] call _assert;
private _moduleA = (_modules select {_assetA in synchronizedObjects _x}) param [0, objNull];
private _moduleAId = netId _moduleA;

private _playerDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; (count allPlayers) isEqualTo 1 || {diag_tickTime > _playerDeadline}};
private _curatorPlayer = allPlayers param [0, objNull];
private _curatorGroup = createGroup sideLogic;
private _curator = _curatorGroup createUnit ["ModuleCurator_F", [0,0,0], [], 0, "NONE"];
_curatorGroup setVariable ["isCuratorModuleGroup", true, true];
_curatorPlayer assignCurator _curator;
_curator addCuratorEditableObjects [[_assetA, _assetC], true];
private _assignedDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator || {diag_tickTime > _assignedDeadline}};
["vigil.whitelist.curatorSetup", !isNull _curatorPlayer && {!isNull _curator} && {(getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator} && {_assetA in curatorEditableObjects _curator} && {_assetC in curatorEditableObjects _curator}, format ["player=%1|curator=%2|assigned=%3|editable=%4", netId _curatorPlayer, netId _curator, netId (getAssignedCuratorLogic _curatorPlayer), [_assetA, _assetC] apply {_x in curatorEditableObjects _curator}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS", []];
TRIBUNAL_VIGIL_WHITELIST_fnc_requestEntrypoint = {
    params ["_logic"];
    private _requests = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS", []];
    _requests pushBack [_logic, remoteExecutedOwner];
    missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS", _requests];
};
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_SETUP", [_token, netId _assetA, netId _assetB, netId _assetC, netId _control, netId _curator, netId _curatorPlayer], true];
private _edenObservedDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_EDEN_OBSERVED", ""]) isEqualTo _token || {diag_tickTime > _edenObservedDeadline}};
deleteVehicle _moduleA;
private _retireDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _members = missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []];
    (count _members) isEqualTo 1 && {_assetB in _members} && {!(_assetA in _members)}
        || {diag_tickTime > _retireDeadline}
};
private _retiredMembers = +(missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []]);
private _records = localNamespace getVariable ["YSF_WHITELIST_EDEN_RECORDS", createHashMap];
private _reconcileAudit = localNamespace getVariable ["YSF_WHITELIST_RECONCILE_AUDIT", []];
private _retiredOk = isNull _moduleA
    && {(count _records) isEqualTo 1}
    && {[_retiredMembers, [_assetB]] call _sameObjects}
    && {(_reconcileAudit findIf {_moduleAId in (_x # 0)}) >= 0};
["vigil.whitelist.edenDeletionRetires", _retiredOk, format ["module=%1|records=%2|members=%3|audit=%4", _moduleAId, keys _records, _retiredMembers apply {netId _x}, _reconcileAudit]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_EDEN_RETIRED", [_token, _moduleAId], true];
private _retiredClientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_EDEN_RETIRED_CLIENT", ""]) isEqualTo _token || {diag_tickTime > _retiredClientDeadline}};
private _acceptedToggles = [];
for "_phase" from 1 to 3 do {
    missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_PHASE", _phase, true];
    private _entrypointRequestDeadline = diag_tickTime + 30;
    waitUntil {uiSleep 0.01; (count (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS", []])) >= _phase || {diag_tickTime > _entrypointRequestDeadline}};
    private _entrypointRequest = (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS", []]) param [_phase - 1, []];
    private _entrypointLogic = _entrypointRequest param [0, objNull];
    if ((_entrypointRequest param [1, -1]) > 2 && {!isNull _entrypointLogic}) then {[_entrypointLogic] call YSF_fnc_toggleObjectInWhitelist;};
    private _toggleDeadline = diag_tickTime + 90;
    waitUntil {
        uiSleep 0.05;
        _acceptedToggles = (localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 3) isEqualTo "accepted"};
        (count _acceptedToggles) isEqualTo _phase || {diag_tickTime > _toggleDeadline}
    };
    private _members = +(missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []]);
    private _target = _assetC;
    private _expected = [[_assetB, _assetC], [_assetB], [_assetB, _assetC]] select (_phase - 1);
    private _transitionOk = (count _acceptedToggles) isEqualTo _phase
        && {[_members, _expected] call _sameObjects}
        && {(_acceptedToggles # (_phase - 1) # 4) isEqualTo netId _target}
        && {(_acceptedToggles # (_phase - 1) # 5) isEqualTo ([true, false, true] # (_phase - 1))};
    [format ["vigil.whitelist.zeusTransition%1", _phase], _transitionOk, format ["phase=%1|toggles=%2|members=%3", _phase, _acceptedToggles, _members apply {[vehicleVarName _x, netId _x]}]] call _assert;
};

private _claims = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
private _acceptedClaims = _claims select {_x # 4};
private _logicIds = _acceptedToggles apply {_x # 1};
private _authority = (count _acceptedClaims) isEqualTo 3
    && {(_acceptedClaims findIf {(_x # 2) isNotEqualTo netId _curator || {(_x # 3) <= 2}}) < 0}
    && {(_acceptedClaims apply {_x # 0}) isEqualTo (_acceptedToggles apply {_x # 0})}
    && {(_acceptedClaims apply {_x # 1}) isEqualTo (_acceptedToggles apply {_x # 1})}
    && {(_acceptedToggles apply {_x # 4}) isEqualTo [netId _assetC, netId _assetC, netId _assetC]}
    && {(_acceptedToggles apply {_x # 5}) isEqualTo [true, false, true]};
["vigil.whitelist.zeusAuthority", _authority, format ["claims=%1|toggles=%2", _claims, _acceptedToggles]] call _assert;
private _logicDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_logicIds findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _logicDeadline}};
["vigil.whitelist.zeusCleanup", (count _logicIds) isEqualTo 3 && {(count (_logicIds arrayIntersect _logicIds)) isEqualTo 3} && {(_logicIds findIf {!isNull objectFromNetId _x}) < 0}, format ["ids=%1", _logicIds]] call _assert;

private _replayOperation = (_acceptedClaims # 0) # 0;
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_NEGATIVE", [_token, _replayOperation, netId _curator], true];
unassignCurator _curator;
private _negativeDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _rows = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
    (_rows findIf {(_x # 0) isEqualTo _replayOperation && {(_x # 5) isEqualTo "duplicate"}}) >= 0
        && {(_rows findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 5) isEqualTo "predicate_logic_class"}}) >= 0}
        || {diag_tickTime > _negativeDeadline}
};
private _finalClaims = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
private _finalMembers = missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []];
private _idempotent = (_finalClaims findIf {(_x # 0) isEqualTo _replayOperation && {(_x # 5) isEqualTo "duplicate"}}) >= 0
    && {(_finalClaims findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 5) isEqualTo "predicate_logic_class"}}) >= 0}
    && {(count ((localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 3) isEqualTo "accepted"})) isEqualTo 3}
    && {[_finalMembers, [_assetB, _assetC]] call _sameObjects};
["vigil.whitelist.idempotence", _idempotent, format ["claims=%1|toggles=%2|members=%3", _finalClaims, localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []], _finalMembers apply {netId _x}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_RESULT", [_token, [_assetB, _assetC] apply {netId _x}, [netId _assetC, netId _assetC, netId _assetC], _logicIds, _acceptedClaims], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
private _clientDone = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", ""];
private _all = [_assetA, _assetB, _assetC, _control] + _modules;
{if (!isNull _x) then {deleteVehicle _x;};} forEach _all;
deleteVehicle _curator;
private _curatorDeleteDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _curator || {diag_tickTime > _curatorDeleteDeadline}};
deleteGroup _curatorGroup;
private _edenMonitor = localNamespace getVariable ["YSF_WHITELIST_EDEN_MONITOR", scriptNull];
if (!scriptDone _edenMonitor) then {terminate _edenMonitor;};
localNamespace setVariable ["YSF_WHITELIST_EDEN_MONITOR", scriptNull];
localNamespace setVariable ["YSF_WHITELIST_EDEN_RECORDS", createHashMap];
localNamespace setVariable ["YSF_WHITELIST_EDEN_AUDIT", []];
localNamespace setVariable ["YSF_WHITELIST_RECONCILE_AUDIT", []];
localNamespace setVariable ["YSF_WHITELIST_MEMBERS", createHashMap];
localNamespace setVariable ["YSF_WHITELIST_OVERRIDES", createHashMap];
localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIMS", createHashMap];
localNamespace setVariable ["YSF_WHITELIST_ZEUS_OPERATIONS", createHashMap];
localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
localNamespace setVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []];
missionNamespace setVariable ["YSF_WHITELIST_CONFIGURED", false, true];
missionNamespace setVariable ["YSF_WHITELISTED_ASSETS", [], true];
{
    missionNamespace setVariable [_x, nil, true];
} forEach [
    "TRIBUNAL_VIGIL_WHITELIST_SETUP",
    "TRIBUNAL_VIGIL_WHITELIST_EDEN_OBSERVED",
    "TRIBUNAL_VIGIL_WHITELIST_EDEN_RETIRED",
    "TRIBUNAL_VIGIL_WHITELIST_EDEN_RETIRED_CLIENT",
    "TRIBUNAL_VIGIL_WHITELIST_PHASE",
    "TRIBUNAL_VIGIL_WHITELIST_NEGATIVE",
    "TRIBUNAL_VIGIL_WHITELIST_RESULT",
    "TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE",
    "TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS"
];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_all findIf {!isNull _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
private _auditClean = (localNamespace getVariable ["YSF_WHITELIST_EDEN_AUDIT", []]) isEqualTo []
    && {(localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []]) isEqualTo []}
    && {(localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []]) isEqualTo []}
    && {(count (localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIMS", createHashMap])) isEqualTo 0}
    && {(count (localNamespace getVariable ["YSF_WHITELIST_ZEUS_OPERATIONS", createHashMap])) isEqualTo 0};
["vigil.whitelist.cleanup", _clientDone isEqualTo _token && {(_all findIf {!isNull _x}) < 0} && {isNull _curator} && {_auditClean}, format ["client=%1|remaining=%2|curator=%3|auditClean=%4", _clientDone, _all select {!isNull _x}, isNull _curator, _auditClean]] call _assert;
'''


CLIENT_SQF = r'''
private _setup = [];
private _setupDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; _setup = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_SETUP", []]; (count _setup) isEqualTo 7 || {diag_tickTime > _setupDeadline}};
private _assetA = objectFromNetId (_setup param [1, ""]);
private _assetB = objectFromNetId (_setup param [2, ""]);
private _assetC = objectFromNetId (_setup param [3, ""]);
private _control = objectFromNetId (_setup param [4, ""]);
private _curator = objectFromNetId (_setup param [5, ""]);
private _expectedBase = [_assetA, _assetB];
private _sameObjects = {params ["_actual", "_expected"]; (count _actual) isEqualTo count _expected && {(_expected findIf {!(_x in _actual)}) < 0}};
private _assignedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic player) isEqualTo _curator && {_assetC in curatorEditableObjects _curator} || {diag_tickTime > _assignedDeadline}};
private _clientCuratorReady = !isNull _curator && {(getAssignedCuratorLogic player) isEqualTo _curator} && {_assetA in curatorEditableObjects _curator} && {_assetC in curatorEditableObjects _curator};
["vigil.whitelist.clientAssigned", _clientCuratorReady, format ["player=%1|owner=%2|curator=%3|editable=%4|editableCount=%5", netId player, clientOwner, netId _curator, [_assetA, _assetC] apply {_x in curatorEditableObjects _curator}, count curatorEditableObjects _curator]] call _assert;
private _initial = call YOSHI_getAllVehicles;
["vigil.whitelist.clientEdenSource", [_initial, _expectedBase] call _sameObjects && {!(_assetC in _initial)} && {!(_control in _initial)}, format ["source=%1", _initial apply {[vehicleVarName _x, netId _x]}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_EDEN_OBSERVED", _token, true];
private _retired = [];
private _retiredDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _retired = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_EDEN_RETIRED", []]; (count _retired) isEqualTo 2 || {diag_tickTime > _retiredDeadline}};
private _retiredSource = call YOSHI_getAllVehicles;
private _retiredReplicaOk = (_retired param [0, ""]) isEqualTo _token
    && {[_retiredSource, [_assetB]] call _sameObjects}
    && {!(_assetA in _retiredSource)};
["vigil.whitelist.clientEdenRetirement", _retiredReplicaOk, format ["retired=%1|source=%2", _retired, _retiredSource apply {netId _x}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_EDEN_RETIRED_CLIENT", _token, true];

private _replicaFixtures = [_assetA, _assetC];
private _replicaStableSince = -1;
private _replicaAnchor = [];
private _replicaSettleDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    private _positions = _replicaFixtures apply {getPosASL _x};
    private _valid = (_replicaFixtures findIf {isNull _x}) < 0;
    if (!_valid) then {
        _replicaStableSince = -1;
        _replicaAnchor = [];
    } else {
        if (_replicaAnchor isEqualTo [] || {(_positions findIf {(_x distance (_replicaAnchor # _forEachIndex)) > 0.05}) >= 0}) then {
            _replicaAnchor = _positions;
            _replicaStableSince = diag_tickTime;
        };
    };
    (_replicaStableSince >= 0 && {diag_tickTime - _replicaStableSince >= 1}) || {diag_tickTime > _replicaSettleDeadline}
};
private _replicaState = _replicaFixtures apply {
    [netId _x, getPosASL _x, velocity _x, angularVelocity _x, isTouchingGround _x]
};
private _replicaPositions = _replicaFixtures apply {getPosASL _x};
private _replicaStable = _replicaStableSince >= 0
    && {diag_tickTime - _replicaStableSince >= 1}
    && {(_replicaFixtures findIf {isNull _x}) < 0}
    && {(_replicaPositions findIf {(_x distance (_replicaAnchor # _forEachIndex)) > 0.05}) < 0};
["vigil.whitelist.clientFixtureStable", _replicaStable, format ["state=%1|stableFor=%2", _replicaState, if (_replicaStableSince < 0) then {-1} else {diag_tickTime - _replicaStableSince}]] call _assert;

private _activations = [];
for "_phase" from 1 to 3 do {
    private _phaseDeadline = diag_tickTime + 120;
    waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_PHASE", 0]) isEqualTo _phase || {diag_tickTime > _phaseDeadline}};
    private _resultsBefore = +(uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []]);
    private _moduleGroup = createGroup [sideLogic, true];
    private _logic = _moduleGroup createUnit ["YSF_Toggle_To_Whitelist_Module", getPosATL _assetC, [], 0, "CAN_COLLIDE"];
    _logic attachTo [_assetC, [0,0,0]];
    private _logicOwnerDeadline = diag_tickTime + 10;
    waitUntil {uiSleep 0.01; owner _logic isEqualTo clientOwner || {diag_tickTime > _logicOwnerDeadline}};
    private _operationId = format ["whitelist-%1-%2-%3-%4", _phase, clientOwner, netId _logic, diag_tickTime];
    private _activation = [_phase, _operationId, netId _logic, netId _assetC, netId _curator, clientOwner, local _logic, owner _logic];
    [_logic, _curator, _operationId, _assetC] remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2];
    [_logic] remoteExecCall ["TRIBUNAL_VIGIL_WHITELIST_fnc_requestEntrypoint", 2];
    private _resultDeadline = diag_tickTime + 60;
    waitUntil {uiSleep 0.05; (count (uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []])) > count _resultsBefore || {diag_tickTime > _resultDeadline}};
    private _rows = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []];
    private _row = _rows param [(count _rows) - 1, []];
    private _source = call YOSHI_getAllVehicles;
    private _expected = [[_assetB, _assetC], [_assetB], [_assetB, _assetC]] select (_phase - 1);
    _activations pushBack [_activation, _row, [_source, _expected] call _sameObjects];
    deleteGroup _moduleGroup;
};
private _activationLogicIds = _activations apply {_x # 0 # 2};
private _activationOk = (count _activations) isEqualTo 3
    && {(_activations findIf {
        private _activation = _x # 0; private _row = _x # 1;
        (_activation # 2) isEqualTo ""
            || {(_activation # 3) isNotEqualTo netId _assetC}
            || {(_activation # 4) isNotEqualTo netId _curator}
            || {(_activation # 5) isNotEqualTo clientOwner}
            || {!(_activation # 6)}
            || {!(_row # 2)}
            || {(_row # 0) isNotEqualTo (_activation # 1)}
            || {(_row # 1) isNotEqualTo (_activation # 2)}
            || {(_row # 4) isNotEqualTo netId _assetC}
            || {!(_x # 2)}
    }) < 0}
    && {count (_activationLogicIds arrayIntersect _activationLogicIds) isEqualTo 3}
    && {(_activations apply {_x # 1 # 5}) isEqualTo [true, false, true]};
["vigil.whitelist.entrypointActivations", _activationOk, format ["activations=%1", _activations]] call _assert;

private _negative = [];
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _negative = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_NEGATIVE", []]; (count _negative) isEqualTo 3 || {diag_tickTime > _negativeDeadline}};
[objNull, objNull, _negative param [1, ""]] remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2];
[player, objectFromNetId (_negative param [2, ""]), format ["%1-forged", _token]] remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2];
private _receiptDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; private _rows = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []]; (_rows findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 3) isEqualTo "duplicate"}}) >= 0 && {(_rows findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0} || {diag_tickTime > _receiptDeadline}};
private _results = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []];
private _acceptedResults = _results select {_x # 2};
private _feedback = (count _acceptedResults) isEqualTo 3
    && {(_acceptedResults apply {_x # 4}) isEqualTo [netId _assetC, netId _assetC, netId _assetC]}
    && {(_acceptedResults apply {_x # 5}) isEqualTo [true, false, true]}
    && {(_acceptedResults findIf {(_x # 6) isNotEqualTo clientOwner}) < 0}
    && {(_results findIf {(_x # 6) isNotEqualTo clientOwner}) < 0}
    && {(_results findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 3) isEqualTo "duplicate"}}) >= 0}
    && {(_results findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0};
["vigil.whitelist.feedbackAndNegatives", _feedback, format ["results=%1|owner=%2", _results, clientOwner]] call _assert;

private _result = []; private _resultDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_RESULT", []]; (count _result) isEqualTo 5 || {diag_tickTime > _resultDeadline}};
private _replicated = (_result param [0, ""]) isEqualTo _token && {(_result param [1, []]) isEqualTo ([_assetB, _assetC] apply {netId _x})} && {(_result param [2, []]) isEqualTo [netId _assetC, netId _assetC, netId _assetC]} && {[(call YOSHI_getAllVehicles), [_assetB, _assetC]] call _sameObjects};
["vigil.whitelist.clientReplication", _replicated, format ["result=%1|source=%2", _result, (call YOSHI_getAllVehicles) apply {netId _x}]] call _assert;
uiNamespace setVariable ["YSF_WHITELIST_ZEUS_RESULTS", []];
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", _token, true];
'''


ASSERT_EDEN = [
    "vigil.whitelist.fixtureStable",
    "vigil.whitelist.edenAggregate",
    "vigil.whitelist.edenRetained",
    "vigil.whitelist.edenDeletionRetires",
    "vigil.whitelist.clientEdenSource",
    "vigil.whitelist.clientEdenRetirement",
    "vigil.whitelist.clientFixtureStable",
]
ASSERT_TOGGLE = [
    "vigil.whitelist.curatorSetup",
    "vigil.whitelist.zeusTransition1",
    "vigil.whitelist.zeusTransition2",
    "vigil.whitelist.zeusTransition3",
    "vigil.whitelist.zeusAuthority",
    "vigil.whitelist.zeusCleanup",
    "vigil.whitelist.clientAssigned",
    "vigil.whitelist.entrypointActivations",
]
ASSERT_NEGATIVE = [
    "vigil.whitelist.idempotence",
    "vigil.whitelist.feedbackAndNegatives",
]
ASSERT_REPLICATION = [
    "vigil.whitelist.clientReplication",
    "vigil.whitelist.cleanup",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-whitelist-modules",
        "version": 1,
        "feature_family": "pontifex-vigil-whitelist",
        "name": "Vigil authentic Eden whitelist and curator toggle",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "mods/visual-support-tablet/tests/tribunal/vigil_whitelist_modules.py",
            "applicability": "Arma 3 dedicated multiplayer with one independently authenticated assigned-curator client",
            "participants": {
                "server": "authoritative whitelist and module owner",
                "client-a": "assigned curator, product-entrypoint actor, and replication observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:asset-whitelist-modules",
        "label": "Vigil asset whitelist Eden and Zeus activation",
        "kind": "product_behavior",
        "aliases": ["Vigil whitelist modules", "Add/Remove from Whitelist"],
        "biki_context": ["biki-page:8458", "biki-page:14844", "biki-page:14896", "biki-page:14822", "biki-page:17356", "biki-page:14941"],
    },
    "arms": [
        {
            "key": "eden_aggregate",
            "role": "treatment",
            "description": "Two authentic retained Eden modules contribute exact assets and deleting one retires only its contribution",
            "assertions": ASSERT_EDEN,
        },
        {
            "key": "authorized_toggle",
            "role": "treatment",
            "description": "Three configured Pontifex entrypoint activations add, remove, and re-add the same exact asset",
            "assertions": ASSERT_TOGGLE,
        },
        {
            "key": "invalid_replay",
            "role": "negative_control",
            "description": "Delivered replay and wrong-class claims cannot cause another whitelist mutation",
            "assertions": ASSERT_NEGATIVE,
        },
        {
            "key": "replication",
            "role": "replicate",
            "description": "Client independently resolves the final authoritative membership and exact operation identities",
            "assertions": ASSERT_REPLICATION,
        },
    ],
    "causal_relationships": [
        {
            "key": "native-toggle-v-invalid",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "authorized_toggle",
            "target": "invalid_replay",
            "controlled_dimensions": ["mission", "authoritative whitelist", "requesting client", "target class family"],
        },
        {
            "key": "authority-v-replica",
            "relation": "REPLICATES",
            "source": "authorized_toggle",
            "target": "replication",
            "controlled_dimensions": ["operation identities", "asset identities", "run token"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:whitelist-eden-aggregate",
            "text": "Multiple authentic retained Eden whitelist modules aggregate the exact synchronized asset union, and deleting one module retires only its contribution on server and client.",
            "intended_use": "primary_result",
            "assertions": ASSERT_EDEN,
            "rationale": "Configured dispatch receipts, native Sync identities, authoritative membership, and an equal unsynchronized control establish the mission-maker path.",
        },
        {
            "id": "pontifex:vigil:whitelist-zeus-toggle",
            "text": "An assigned curator can add, remove, and re-add the same asset through the configured Pontifex entrypoint, with exact private results, idempotent replay rejection, replication, and cleanup.",
            "intended_use": "primary_result",
            "assertions": ASSERT_TOGGLE + ASSERT_NEGATIVE + ASSERT_REPLICATION,
            "rationale": "Three product-entrypoint activations with engine-realistic inputs are correlated to distinct client-owned logics, exact same-target server claims, alternating authoritative transitions, requester-owned results, final client membership, and delivered negative controls.",
        },
    ],
    "unresolved": [
        "Client-B/JIP isolation, curator reassignment, ownership migration, and live synchronization mutation on a retained Eden module remain outside this one-client proof."
    ],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-whitelist-modules",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.whitelist.fixtureStable", "vigil.whitelist.edenAggregate", "vigil.whitelist.edenRetained",
        "vigil.whitelist.curatorSetup", "vigil.whitelist.zeusTransition1",
        "vigil.whitelist.zeusTransition2", "vigil.whitelist.zeusTransition3",
        "vigil.whitelist.edenDeletionRetires", "vigil.whitelist.zeusAuthority",
        "vigil.whitelist.zeusCleanup", "vigil.whitelist.idempotence",
        "vigil.whitelist.cleanup",
    }),
    client_expected=frozenset({
        "vigil.whitelist.clientAssigned", "vigil.whitelist.clientEdenSource",
        "vigil.whitelist.clientEdenRetirement", "vigil.whitelist.clientFixtureStable",
        "vigil.whitelist.entrypointActivations", "vigil.whitelist.feedbackAndNegatives",
        "vigil.whitelist.clientReplication",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "visual-support-tablet", "feature": "whitelist-modules",
    },
    mission_entities=(
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_MODULE_A", "YSF_Asset_Whitelist_Module", "YSF_Tablet", "Logic", (3600, 0, 3600)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_MODULE_B", "YSF_Asset_Whitelist_Module", "YSF_Tablet", "Logic", (3620, 0, 3600)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_A", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4550, 16, 2900)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_B", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4575, 16, 2900)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_C", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4600, 16, 2900)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_CONTROL", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4625, 16, 2900)),
    ),
    mission_syncs=(
        MissionSync("TRIBUNAL_VIGIL_WHITELIST_MODULE_A", "TRIBUNAL_VIGIL_WHITELIST_A"),
        MissionSync("TRIBUNAL_VIGIL_WHITELIST_MODULE_B", "TRIBUNAL_VIGIL_WHITELIST_B"),
    ),
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Multiple authentic Eden whitelist modules aggregate exact synchronized assets and retire a deleted source; one assigned curator invokes the configured Pontifex entrypoint with engine-realistic inputs to add, remove, and re-add the same asset, receives exact private results, and cannot replay or forge another mutation.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The scenario proves configured dispatch, native Sync identity, deleted-source retirement, exact client discovery snapshots, three same-target configured curator entrypoint activations, alternating transitions, authority, idempotence, feedback, replication, and cleanup.",
        dependencies=("typed Eden module fixture", "Pontifex curator input adapter", "real module, target, and curator objects", "accepted Vigil mixed-fleet browser", "one authenticated client"),
        evidence_types=frozenset({"configured-dispatch", "native-sync", "product-entrypoint-activation", "exact-identity", "negative-control", "authoritative-state", "replication", "locality", "cleanup"}),
        locality_requirements="Eden registration and whitelist mutation are server-owned; the authenticated client supplies real module, target, curator, and operation values that Arma placement provides; the server invokes the configured Pontifex entrypoint in its engine authority context; the client receives only its correlated result snapshots.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
