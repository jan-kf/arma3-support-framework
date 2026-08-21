"""Authentic Eden and Zeus activation coverage for Counter Battery Radar."""

from tribunal.mission.artillery import artillery_observer_sqf
from tribunal.mission.markers import marker_observer_sqf
from tribunal.runner.model import MissionEntity, Scenario, ScenarioReview


SERVER_SQF = artillery_observer_sqf() + marker_observer_sqf() + r'''
private _module = objNull;
private _auditDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (count (localNamespace getVariable ["YAS_CBR_MODULE_DISPATCH_AUDIT", []])) >= 1 || {diag_tickTime > _auditDeadline}};
private _dispatch = localNamespace getVariable ["YAS_CBR_MODULE_DISPATCH_AUDIT", []];
private _acceptedDispatch = _dispatch select {_x # 8};
if ((count _acceptedDispatch) isEqualTo 1) then {_module = objectFromNetId ((_acceptedDispatch # 0) # 2);};
private _edenOk = (count _acceptedDispatch) isEqualTo 1
    && {!isNull _module} && {typeOf _module isEqualTo "YAS_CBR_Module"}
    && {local _module} && {owner _module isEqualTo 2}
    && {(_acceptedDispatch # 0) # 2 isEqualTo netId _module}
    && {(_acceptedDispatch # 0) # 9 isEqualTo "accepted"}
    && {missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]};
["cbr.module.edenDispatch", _edenOk, format ["module=%1|local=%2|owner=%3|audit=%4|enabled=%5", netId _module, local _module, owner _module, _dispatch, missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]]] call _assert;
["cbr.module.edenRetained", !isNull _module && {typeOf _module isEqualTo "YAS_CBR_Module"}, format ["module=%1|class=%2", netId _module, typeOf _module]] call _assert;

private _playerDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; (count allPlayers) isEqualTo 1 || {diag_tickTime > _playerDeadline}};
private _curatorPlayer = allPlayers param [0, objNull];
private _curatorGroup = createGroup sideLogic;
private _curator = _curatorGroup createUnit ["ModuleCurator_F", [0,0,0], [], 0, "NONE"];
_curatorGroup setVariable ["isCuratorModuleGroup", true, true];
_curatorPlayer assignCurator _curator;
private _assignedDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator || {diag_tickTime > _assignedDeadline}};
private _setupOk = !isNull _curatorPlayer && {!isNull _curator} && {(getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator};
["cbr.module.curatorSetup", _setupOk, format ["player=%1|curator=%2|assigned=%3", netId _curatorPlayer, netId _curator, netId (getAssignedCuratorLogic _curatorPlayer)]] call _assert;

private _target = [4000,3500,0];
private _gunPos = [3500,4000,0];
private _gun = "O_Mortar_01_F" createVehicle _gunPos;
_gun setVectorUp (surfaceNormal (getPosATL _gun));
createVehicleCrew _gun;
_gun setVehicleAmmo 1;
private _crewDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; !isNull gunner _gun || {diag_tickTime > _crewDeadline}};

private _fire = {
    params ["_label", "_expectDetection"];
    private _shotToken = format ["%1-%2", _token, _label];
    [_shotToken] call TRIBUNAL_fnc_artilleryObserverStart;
    private _sourceObserved = [_shotToken, _gun, [_target]] call TRIBUNAL_fnc_artilleryObserveSource;
    _gun setVehicleAmmo 1;
    _gun doArtilleryFire [_target, "8Rnd_82mm_Mo_shells", 1];
    private _peakClusters = 0;
    private _peakMarkers = [];
    private _deadline = diag_tickTime + 150;
    waitUntil {
        uiSleep 0.05;
        _peakClusters = _peakClusters max (count YOSHI_CB_clusters);
        private _names = ["YOSHI_cb_"] call TRIBUNAL_fnc_markerNames;
        {_peakMarkers pushBackUnique _x;} forEach _names;
        private _events = ([_shotToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
        ((count _events) isEqualTo 1 && {(_events # 0) getOrDefault ["terminated", false]}) || {diag_tickTime > _deadline}
    };
    private _events = ([_shotToken] call TRIBUNAL_fnc_artilleryObserverStop) getOrDefault ["events", []];
    private _event = _events param [0, createHashMap];
    private _last = _event getOrDefault ["lastPosition", []];
    private _physical = _sourceObserved && {(count _events) isEqualTo 1}
        && {_event getOrDefault ["artilleryEvent", false]}
        && {_event getOrDefault ["terminated", false]}
        && {(count (_event getOrDefault ["samples", []])) > 10}
        && {(count _last) >= 2} && {_last distance2D _target < 250};
    private _causal = if (_expectDetection) then {_peakClusters > 0 && {(count _peakMarkers) >= 2}} else {_peakClusters isEqualTo 0 && {_peakMarkers isEqualTo []}};
    [_physical && {_causal}, _physical, _peakClusters, _peakMarkers, _last, count (_event getOrDefault ["samples", []]), _event getOrDefault ["artilleryEvent", false]]
};

private _positive = ["eden-on", true] call _fire;
["cbr.module.edenCausalDetection", _positive # 0, format ["result=%1", _positive]] call _assert;
private _clearDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; YOSHI_CB_clusters isEqualTo [] && {(["YOSHI_cb_"] call TRIBUNAL_fnc_markerNames) isEqualTo []} || {diag_tickTime > _clearDeadline}};

missionNamespace setVariable ["TRIBUNAL_CBR_ZEUS_SETUP", [_token, netId _curator, netId _curatorPlayer], true];
missionNamespace setVariable ["TRIBUNAL_CBR_ZEUS_PHASE", 1, true];
private _toggleDeadline = diag_tickTime + 90;
private _toggleAudit = [];
waitUntil {
    uiSleep 0.05;
    _toggleAudit = (localNamespace getVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 3) isEqualTo "accepted"};
    (count _toggleAudit) isEqualTo 1 || {diag_tickTime > _toggleDeadline}
};
private _offState = !(missionNamespace getVariable ["YOSHI_CBR_ENABLED", true]);
["cbr.module.zeusOffTransition", (count _toggleAudit) isEqualTo 1 && {_offState} && {!((_toggleAudit # 0) # 4)}, format ["audit=%1|enabled=%2", _toggleAudit, missionNamespace getVariable ["YOSHI_CBR_ENABLED", true]]] call _assert;
private _negative = ["zeus-off", false] call _fire;
["cbr.module.zeusOffPhysicalControl", _negative # 0, format ["result=%1", _negative]] call _assert;

private _claims = localNamespace getVariable ["YAS_CBR_ZEUS_CLAIM_AUDIT", []];
private _acceptedClaims = _claims select {_x # 4};
private _logicIds = _toggleAudit apply {_x # 1};
private _authorityOk = (count _acceptedClaims) isEqualTo 1
    && {(_acceptedClaims # 0) # 2 isEqualTo netId _curator}
    && {(_acceptedClaims # 0) # 3 > 2};
["cbr.module.zeusAuthority", _authorityOk, format ["claims=%1|toggles=%2", _claims, _toggleAudit]] call _assert;
private _logicDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_logicIds findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _logicDeadline}};
["cbr.module.zeusLogicCleanup", (count _logicIds) isEqualTo 1 && {(_logicIds findIf {!isNull objectFromNetId _x}) < 0}, format ["ids=%1", _logicIds]] call _assert;

private _acceptedClaim = _acceptedClaims param [0, []];
private _operation = _acceptedClaim param [0, ""];
missionNamespace setVariable ["TRIBUNAL_CBR_ZEUS_NEGATIVE", [_token, _operation, netId _curator], true];
unassignCurator _curator;
private _negativeDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _rows = localNamespace getVariable ["YAS_CBR_ZEUS_CLAIM_AUDIT", []];
    (_rows findIf {(_x # 0) isEqualTo _operation && {(_x # 5) isEqualTo "duplicate"}}) >= 0
        && {(_rows findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 5) isEqualTo "predicate_logic_class"}}) >= 0}
        || {diag_tickTime > _negativeDeadline}
};
private _finalClaims = localNamespace getVariable ["YAS_CBR_ZEUS_CLAIM_AUDIT", []];
private _idempotent = (_finalClaims findIf {(_x # 0) isEqualTo _operation && {(_x # 5) isEqualTo "duplicate"}}) >= 0
    && {(_finalClaims findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 5) isEqualTo "predicate_logic_class"}}) >= 0}
    && {(count ((localNamespace getVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 3) isEqualTo "accepted"})) isEqualTo 1}
    && {!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", true])};
["cbr.module.zeusIdempotence", _idempotent, format ["claims=%1|toggles=%2|enabled=%3", _finalClaims, localNamespace getVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", []], missionNamespace getVariable ["YOSHI_CBR_ENABLED", true]]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CBR_MODULE_RESULT", [_token, netId _module, netId _curator, _positive, _negative, _acceptedClaims, _logicIds], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_CBR_MODULE_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
deleteVehicleCrew _gun;
deleteVehicle _gun;
deleteVehicle _module;
deleteVehicle _curator;
deleteGroup _curatorGroup;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _gun && {isNull _module} && {isNull _curator} || {diag_tickTime > _cleanupDeadline}};
["cbr.module.cleanup", (missionNamespace getVariable ["TRIBUNAL_CBR_MODULE_CLIENT_DONE", ""]) isEqualTo _token && {isNull _gun} && {isNull _module} && {isNull _curator}, format ["clientDone=%1|gun=%2|module=%3|curator=%4", missionNamespace getVariable ["TRIBUNAL_CBR_MODULE_CLIENT_DONE", ""], isNull _gun, isNull _module, isNull _curator]] call _assert;
'''


CLIENT_SQF = r'''
private _setup = [];
private _setupDeadline = diag_tickTime + 90;
waitUntil {uiSleep 0.05; _setup = missionNamespace getVariable ["TRIBUNAL_CBR_ZEUS_SETUP", []]; (count _setup) isEqualTo 3 || {diag_tickTime > _setupDeadline}};
private _curator = objectFromNetId (_setup param [1, ""]);
private _assignedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic player) isEqualTo _curator || {diag_tickTime > _assignedDeadline}};
["cbr.module.clientAssigned", !isNull _curator && {(getAssignedCuratorLogic player) isEqualTo _curator}, format ["player=%1|owner=%2|curator=%3", netId player, clientOwner, netId _curator]] call _assert;

diag_log "TRIBUNAL_CBR_ZEUS|ARMED";
private _displayDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; !isNull findDisplay 312 || {diag_tickTime > _displayDeadline}};
private _display = findDisplay 312;
diag_log "TRIBUNAL_CBR_ZEUS|DISPLAY_OPEN";
private _phaseDeadline = diag_tickTime + 120;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_CBR_ZEUS_PHASE", 0]) isEqualTo 1 || {diag_tickTime > _phaseDeadline}};
ctrlActivate (_display displayCtrl 152);
uiSleep 0.25;
private _tree = _display displayCtrl 280;
private _path = [];
for "_i" from 0 to ((_tree tvCount []) - 1) do {
    if ((_tree tvText [_i]) isEqualTo "Toggle Counter Batter Radar (CBR)") exitWith {_path = [_i];};
    for "_j" from 0 to ((_tree tvCount [_i]) - 1) do {
        if ((_tree tvText [_i,_j]) isEqualTo "Toggle Counter Batter Radar (CBR)") exitWith {_path = [_i,_j];};
    };
    if (_path isNotEqualTo []) exitWith {};
};
if ((count _path) > 1) then {_tree tvSetCurSel [_path # 0]; uiSleep 0.1;};
if (_path isNotEqualTo []) then {_tree tvSetCurSel _path;};
private _ground = [3700,3700,0];
private _groundASL = AGLToASL _ground;
private _camPos = _groundASL vectorAdd [0,-30,25];
private _camDir = vectorNormalized (_groundASL vectorDiff _camPos);
private _right = vectorNormalized (_camDir vectorCrossProduct [0,0,1]);
private _up = vectorNormalized (_right vectorCrossProduct _camDir);
curatorCamera setPosASL _camPos;
curatorCamera setVectorDirAndUp [_camDir, _up];
uiSleep 0.5;
private _point = worldToScreen _ground;
diag_log format ["TRIBUNAL_CBR_ZEUS|PLACEMENT_READY|1|%1", _point];
// Unlike attachable modules, native ground placement does not expose a stable
// object through curatorMouseOver. Give the external driver time to move the
// cursor to the declared point, record the engine value, then let the exact
// CuratorObjectPlaced claim/result be the fail-closed outcome oracle.
uiSleep 1;
private _hover = curatorMouseOver;
diag_log format ["TRIBUNAL_CBR_ZEUS|HOVER_READY|1|hover=%1", _hover];
private _resultsBefore = count (uiNamespace getVariable ["YAS_CBR_ZEUS_RESULTS", []]);
private _resultDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; count (uiNamespace getVariable ["YAS_CBR_ZEUS_RESULTS", []]) > _resultsBefore || {diag_tickTime > _resultDeadline}};
private _rows = uiNamespace getVariable ["YAS_CBR_ZEUS_RESULTS", []];
private _accepted = _rows select {_x # 2};
private _placements = uiNamespace getVariable ["YAS_CBR_ZEUS_CLIENT_PLACEMENT_AUDIT", []];
private _native = _path isNotEqualTo [] && {(count _point) isEqualTo 2} && {(count _accepted) isEqualTo 1}
    && {(count _placements) isEqualTo 1} && {(_placements # 0) # 4}
    // owner can transiently report 0 on the placing client. The server claim
    // independently requires owner(logic)==remoteExecutedOwner before accept.
    && {(_accepted # 0) # 5 isEqualTo clientOwner};
diag_log format ["TRIBUNAL_CBR_ZEUS|PLACED|1|%1", _accepted param [0, []]];
["cbr.module.nativePlacement", _native, format ["path=%1|point=%2|hover=%3|placements=%4|results=%5", _path, _point, _hover, _placements, _rows]] call _assert;

private _negative = [];
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _negative = missionNamespace getVariable ["TRIBUNAL_CBR_ZEUS_NEGATIVE", []]; (count _negative) isEqualTo 3 || {diag_tickTime > _negativeDeadline}};
[objNull, objNull, _negative param [1, ""]] remoteExecCall ["YAS_fnc_cbrZeusClaimServer", 2];
[player, objectFromNetId (_negative param [2, ""]), format ["%1-unauthorized", _token]] remoteExecCall ["YAS_fnc_cbrZeusClaimServer", 2];
private _receiptDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _current = uiNamespace getVariable ["YAS_CBR_ZEUS_RESULTS", []];
    (_current findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 3) isEqualTo "duplicate"}}) >= 0
        && {(_current findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0}
        || {diag_tickTime > _receiptDeadline}
};
_rows = uiNamespace getVariable ["YAS_CBR_ZEUS_RESULTS", []];
private _feedback = (count (_rows select {_x # 2})) isEqualTo 1
    && {(_rows findIf {(_x # 5) isNotEqualTo clientOwner}) < 0}
    && {(_rows findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 3) isEqualTo "duplicate"}}) >= 0}
    && {(_rows findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0};
["cbr.module.feedbackAndNegativeReceipts", _feedback, format ["results=%1|owner=%2", _rows, clientOwner]] call _assert;

private _result = [];
private _finalDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_CBR_MODULE_RESULT", []]; (count _result) isEqualTo 7 || {diag_tickTime > _finalDeadline}};
private _replicated = (_result param [0, ""]) isEqualTo _token
    && {!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", true])}
    && {(_result param [3, []]) param [0, false]}
    && {(_result param [4, []]) param [0, false]};
["cbr.module.clientReplication", _replicated, format ["result=%1|enabled=%2", _result, missionNamespace getVariable ["YOSHI_CBR_ENABLED", true]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_CBR_MODULE_CLIENT_DONE", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="advsys-cbr-modules",
    tier="gameplay",
    server_expected=frozenset({
        "cbr.module.edenDispatch", "cbr.module.edenRetained",
        "cbr.module.curatorSetup", "cbr.module.edenCausalDetection",
        "cbr.module.zeusOffTransition", "cbr.module.zeusOffPhysicalControl",
        "cbr.module.zeusAuthority", "cbr.module.zeusLogicCleanup",
        "cbr.module.zeusIdempotence", "cbr.module.cleanup",
    }),
    client_expected=frozenset({
        "cbr.module.clientAssigned", "cbr.module.nativePlacement",
        "cbr.module.feedbackAndNegativeReceipts", "cbr.module.clientReplication",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "advanced-systems",
        "feature": "cbr-modules",
        "visual_driver": "zeus-placement",
        "visual_armed_marker": "TRIBUNAL_CBR_ZEUS|ARMED",
        "zeus_marker_prefix": "TRIBUNAL_CBR_ZEUS",
        "zeus_placements": 1,
    },
    mission_entities=(
        MissionEntity("TRIBUNAL_CBR_MODULE_EDEN", "YAS_CBR_Module", "YAS_AdvSys", "Logic", (3700, 0, 3700)),
    ),
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="An authentic retained Eden module enables global CBR; an assigned curator's authentic Zeus placement toggles it once, returns placing-curator-only feedback, and replay or forged requests do not change state.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The narrow scenario correlates native module receipts with one real detected artillery shell and one same-fixture disabled physical control, then proves authority, feedback, idempotence, replication, and cleanup.",
        dependencies=("typed Eden module fixture", "authenticated curator input adapter", "Tribunal artillery and marker observers", "one authenticated client"),
        evidence_types=frozenset({"configured-dispatch", "native-curator-placement", "artillery-trajectory", "marker", "authoritative-state", "replication", "locality", "cleanup"}),
        locality_requirements="Eden dispatch and CBR lifecycle are server-owned; the placing client owns the transient Zeus module and sends an assigned-curator claim; client-a receives only its correlated results.",
    ),
)
