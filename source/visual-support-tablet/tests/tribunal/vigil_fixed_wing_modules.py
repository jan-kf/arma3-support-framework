"""Authentic Eden and curator activation coverage for Vigil fixed-wing assets."""

from tribunal.runner.model import MissionEntity, MissionSync, Scenario, ScenarioReview


SERVER_SQF = r'''
private _assetA = missionNamespace getVariable ["TRIBUNAL_FW_EDEN_A", objNull];
private _assetB = missionNamespace getVariable ["TRIBUNAL_FW_EDEN_B", objNull];
private _zeusTarget = missionNamespace getVariable ["TRIBUNAL_FW_ZEUS_TARGET", objNull];
private _control = missionNamespace getVariable ["TRIBUNAL_FW_CONTROL", objNull];
private _deadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (count (localNamespace getVariable ["YSF_FW_MODULE_DISPATCH_AUDIT", []])) >= 6 || {diag_tickTime > _deadline}};
private _audit = localNamespace getVariable ["YSF_FW_MODULE_DISPATCH_AUDIT", []];
private _accepted = _audit select {_x # 7 && {(_x # 8) isEqualTo "accepted_native"}};
private _assetRows = _accepted select {(_x # 0) isEqualTo "asset"};
private _infilRows = _accepted select {(_x # 0) isEqualTo "infil"};
private _exfilRows = _accepted select {(_x # 0) isEqualTo "exfil"};
private _native = (count _accepted) isEqualTo 6
    && {(_accepted findIf {!(_x # 3) || {!(_x # 4)} || {(_x # 5) isNotEqualTo 2} || {(_x # 6) > 2}}) < 0};
["vigil.fwModules.nativeDispatch", _native, format ["audit=%1", _audit]] call _assert;
private _reg = call YSF_fwEnsureRegistry;
private _sourceRows = [];
{_sourceRows append (_x # 9 # 0);} forEach _assetRows;
private _sourceIds = _sourceRows apply {_x # 2};
private _expectedEdenIds = _sourceIds apply {format ["FW_%1", _x]};
private _edenIds = [];
{_edenIds append (_x # 9 # 1);} forEach _assetRows;
private _edenOk = (count _assetRows) isEqualTo 2 && {(count _reg) isEqualTo 2}
    && {(count (_sourceIds arrayIntersect _sourceIds)) isEqualTo 2} && {(_sourceIds findIf {_x isEqualTo ""}) < 0}
    && {(count (_edenIds arrayIntersect _expectedEdenIds)) isEqualTo 2}
    && {(_expectedEdenIds findIf {isNil {_reg get _x}}) < 0}
    && {(_sourceIds findIf {!isNull objectFromNetId _x}) < 0}
    && {!isNull _control} && {!isNull _zeusTarget};
["vigil.fwModules.edenAssets", _edenOk, format ["sourceRows=%1|source=%2|expected=%3|reported=%4|registry=%5|control=%6", _sourceRows, _sourceIds, _expectedEdenIds, _edenIds, keys _reg, [netId _control, typeOf _control]]] call _assert;

private _infilA = (_infilRows # 0 # 9 # 0);
private _infilB = (_infilRows # 1 # 9 # 0);
private _exfilA = (_exfilRows # 0 # 9 # 0);
private _exfilB = (_exfilRows # 1 # 9 # 0);
private _nearInfil = ["infil", [4683,2780,0]] call YSF_fnc_fwSelectMissionPoint;
private _farInfil = ["infil", [2500,5000,0]] call YSF_fnc_fwSelectMissionPoint;
private _nearExfil = ["exfil", [4683,2780,1200]] call YSF_fnc_fwSelectMissionPoint;
private _pointSet = {params ["_actual", "_a", "_b"]; (_actual distance2D _a) < 1 || {(_actual distance2D _b) < 1}};
private _pointPolicy = [_nearInfil, _infilA, _infilB] call _pointSet
    && {[_farInfil, _infilA, _infilB] call _pointSet}
    && {_nearInfil distance2D _farInfil > 1000}
    && {[_nearExfil, _exfilA, _exfilB] call _pointSet};
["vigil.fwModules.pointAggregation", _pointPolicy, format ["infilRows=%1|exfilRows=%2|selected=%3", _infilRows, _exfilRows, [_nearInfil, _farInfil, _nearExfil]]] call _assert;

private _requesterOwner = missionNamespace getVariable ["PONTIFEX_LIVE_clientOwner", -1];
createVehicleCrew _zeusTarget;
createVehicleCrew _control;
{
    _x setVehiclePosition [[2000 + (_forEachIndex * 50), 5600, 0], [], 0, "NONE"];
    _x setDir 120; _x setFuel 0; _x engineOn false; _x setVelocity [0,0,0]; _x setAngularVelocity [0,0,0];
    {doStop _x;} forEach crew _x;
} forEach [_zeusTarget, _control];
uiSleep 3;
{_x setVelocity [0,0,0]; _x setAngularVelocity [0,0,0];} forEach [_zeusTarget, _control];
private _curatorPlayer = objNull;
private _playerDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _matches = allPlayers select {owner _x isEqualTo _requesterOwner};
    _curatorPlayer = _matches param [0, objNull];
    !isNull _curatorPlayer || {diag_tickTime > _playerDeadline}
};
private _identity = [_token, netId _curatorPlayer, _requesterOwner];
private _curatorGroup = createGroup sideLogic;
private _curator = _curatorGroup createUnit ["ModuleCurator_F", [0,0,0], [], 0, "NONE"];
_curatorGroup setVariable ["isCuratorModuleGroup", true, true];
_curatorPlayer assignCurator _curator;
_curator addCuratorEditableObjects [[_zeusTarget], true];
private _curatorDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator || {diag_tickTime > _curatorDeadline}};
["vigil.fwModules.curatorSetup", !isNull _curatorPlayer && {owner _curatorPlayer isEqualTo (_identity param [2, -1])} && {(getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator} && {_zeusTarget in curatorEditableObjects _curator}, format ["identity=%1|player=%2|owner=%3|curator=%4|editable=%5", _identity, netId _curatorPlayer, owner _curatorPlayer, netId _curator, _zeusTarget in curatorEditableObjects _curator]] call _assert;

private _deployId = _edenIds param [0, ""];
private _deployRequest = format ["%1-fw-deploy", _token];
missionNamespace setVariable ["TRIBUNAL_FW_MODULE_SETUP", [_token, _deployId, _deployRequest, netId _zeusTarget, netId _control, netId _curator], true];
private _deployDeadline = diag_tickTime + 60;
private _entry = objNull;
waitUntil {uiSleep 0.05; _entry = [_deployId] call YSF_fwGetEntry; typeName _entry isEqualTo "HASHMAP" && {(_entry getOrDefault ["state", ""]) isEqualTo YSF_FW_STATE_ON_STATION} || {diag_tickTime > _deployDeadline}};
private _spawned = if (typeName _entry isEqualTo "HASHMAP") then {_entry getOrDefault ["spawnedVeh", objNull]} else {objNull};
private _actualInfil = if (typeName _entry isEqualTo "HASHMAP") then {_entry getOrDefault ["lastInfilPosASL", []]} else {[]};
private _expectedInfil = ["infil", getPosASL _curatorPlayer] call YSF_fnc_fwSelectMissionPoint;
private _deployOk = !isNull _spawned && {(count _actualInfil) isEqualTo 3} && {_actualInfil distance2D _expectedInfil < 1}
    && {(_entry getOrDefault ["infilUsesMissionPoints", false])};
["vigil.fwModules.nearestIngress", _deployOk, format ["id=%1|actual=%2|expected=%3|vehicle=%4|player=%5", _deployId, _actualInfil, _expectedInfil, [netId _spawned, typeOf _spawned], getPosASL _curatorPlayer]] call _assert;
private _expectedExfil = ["exfil", getPosASL _spawned] call YSF_fnc_fwSelectMissionPoint;
private _rtb = [_deployId] call YSF_fwRtbAsset;
_entry = [_deployId] call YSF_fwGetEntry;
private _actualExfil = _entry getOrDefault ["lastExfilPosASL", []];
["vigil.fwModules.nearestEgress", _rtb && {(count _actualExfil) isEqualTo 3} && {_actualExfil distance2D _expectedExfil < 1} && {_entry getOrDefault ["exfilUsesMissionPoints", false]}, format ["actual=%1|expected=%2|state=%3", _actualExfil, _expectedExfil, _entry getOrDefault ["state", ""]]] call _assert;

private _zeusDeadline = diag_tickTime + 90;
private _zeusRows = [];
waitUntil {uiSleep 0.05; _zeusRows = (localNamespace getVariable ["YSF_FW_ZEUS_ADD_AUDIT", []]) select {_x # 3}; (count _zeusRows) isEqualTo 1 || {diag_tickTime > _zeusDeadline}};
private _claims = localNamespace getVariable ["YSF_FW_ZEUS_CLAIM_AUDIT", []];
private _acceptedClaims = _claims select {_x # 4};
private _zeusId = (_zeusRows param [0, []]) param [5, ""];
_reg = call YSF_fwEnsureRegistry;
private _zeusOk = (count _zeusRows) isEqualTo 1 && {(count _acceptedClaims) isEqualTo 1}
    && {_zeusId isNotEqualTo ""} && {!isNil {_reg get _zeusId}} && {isNull _zeusTarget}
    && {(_acceptedClaims # 0 # 2) isEqualTo netId _curator} && {(_acceptedClaims # 0 # 3) > 2};
["vigil.fwModules.zeusAuthority", _zeusOk, format ["adds=%1|claims=%2|registry=%3", _zeusRows, _claims, keys _reg]] call _assert;
private _operation = (_acceptedClaims param [0, []]) param [0, ""];
missionNamespace setVariable ["TRIBUNAL_FW_MODULE_NEGATIVE", [_token, _operation, netId _curator], true];
unassignCurator _curator;
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; private _rows = localNamespace getVariable ["YSF_FW_ZEUS_CLAIM_AUDIT", []]; (_rows findIf {(_x # 0) isEqualTo _operation && {(_x # 5) isEqualTo "duplicate"}}) >= 0 && {(_rows findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 5) isEqualTo "predicate_logic_class"}}) >= 0} || {diag_tickTime > _negativeDeadline}};
private _finalClaims = localNamespace getVariable ["YSF_FW_ZEUS_CLAIM_AUDIT", []];
private _finalAdds = localNamespace getVariable ["YSF_FW_ZEUS_ADD_AUDIT", []];
_reg = call YSF_fwEnsureRegistry;
private _negativeOk = (_finalClaims findIf {(_x # 0) isEqualTo _operation && {(_x # 5) isEqualTo "duplicate"}}) >= 0
    && {(_finalClaims findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 5) isEqualTo "predicate_logic_class"}}) >= 0}
    && {(count (_finalAdds select {_x # 3})) isEqualTo 1} && {(count _reg) isEqualTo 3} && {!isNull _control};
["vigil.fwModules.negativesIdempotent", _negativeOk, format ["claims=%1|adds=%2|registry=%3|control=%4", _finalClaims, _finalAdds, keys _reg, netId _control]] call _assert;

missionNamespace setVariable ["TRIBUNAL_FW_MODULE_RESULT", [_token, _edenIds, _zeusId, _actualInfil, _actualExfil, netId _control], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_FW_MODULE_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
if (!isNull _spawned) then {deleteVehicleCrew _spawned; deleteVehicle _spawned;};
deleteVehicleCrew _control; deleteVehicle _control; deleteVehicle _curator; deleteGroup _curatorGroup;
private _logics = [];
{private _id = _x # 2; private _logic = objectFromNetId _id; if (!isNull _logic) then {_logics pushBack _logic; deleteVehicle _logic;};} forEach _accepted;
localNamespace setVariable ["YSF_FW_MODULE_INFIL_POINTS", createHashMap];
localNamespace setVariable ["YSF_FW_MODULE_EXFIL_POINTS", createHashMap];
missionNamespace setVariable ["YSF_FW_MISSION_INFIL_POINTS", [], true];
missionNamespace setVariable ["YSF_FW_MISSION_EXFIL_POINTS", [], true];
private _emptyRegistry = createHashMap;
[YSF_FW_REGISTRY_TOKEN, _emptyRegistry] call YSF_fwCommitRegistry;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _control && {isNull _curator} && {(_logics findIf {!isNull _x}) < 0} || {diag_tickTime > _cleanupDeadline}};
["vigil.fwModules.cleanup", (missionNamespace getVariable ["TRIBUNAL_FW_MODULE_CLIENT_DONE", ""]) isEqualTo _token && {isNull _control} && {isNull _curator} && {(_logics findIf {!isNull _x}) < 0} && {(count (call YSF_fwEnsureRegistry)) isEqualTo 0} && {(call YSF_fwGetPublicRegistry) isEqualTo []}, format ["client=%1|logics=%2|private=%3|public=%4", missionNamespace getVariable ["TRIBUNAL_FW_MODULE_CLIENT_DONE", ""], _logics, keys (call YSF_fwEnsureRegistry), call YSF_fwGetPublicRegistry]] call _assert;
'''


CLIENT_SQF = r'''
private _setup = [];
private _deadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; _setup = missionNamespace getVariable ["TRIBUNAL_FW_MODULE_SETUP", []]; (count _setup) isEqualTo 6 || {diag_tickTime > _deadline}};
private _deployId = _setup param [1, ""];
private _request = _setup param [2, ""];
private _target = objectFromNetId (_setup param [3, ""]);
private _control = objectFromNetId (_setup param [4, ""]);
private _curator = objectFromNetId (_setup param [5, ""]);
private _assignedDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic player) isEqualTo _curator || {diag_tickTime > _assignedDeadline}};
_curator addCuratorEditableObjects [[_target], true];
private _editableDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; _target in curatorEditableObjects _curator || {diag_tickTime > _editableDeadline}};
["vigil.fwModules.clientAssigned", !isNull _target && {!isNull _control} && {(getAssignedCuratorLogic player) isEqualTo _curator} && {_target in curatorEditableObjects _curator}, format ["player=%1|target=%2|control=%3|curator=%4|assigned=%5|owner=%6|editableMirror=%7", netId player, netId _target, netId _control, netId _curator, netId (getAssignedCuratorLogic player), clientOwner, _target in curatorEditableObjects _curator]] call _assert;
[_deployId, player, _request] call YSF_fwDeployAsset;
private _ack = [];
private _ackDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _ack = missionNamespace getVariable [format ["YSF_FW_DEPLOY_ACK_%1", _request], []]; (count _ack) >= 3 || {diag_tickTime > _ackDeadline}};
["vigil.fwModules.clientDeployEndpoint", (_ack param [0, false]) && {(_ack param [1, ""]) isEqualTo "accepted"} && {(_ack param [2, ""]) isEqualTo _deployId}, format ["request=%1|ack=%2", _request, _ack]] call _assert;

diag_log "TRIBUNAL_VIGIL_FW_ZEUS|ARMED";
private _displayDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; !isNull findDisplay 312 || {diag_tickTime > _displayDeadline}};
private _display = findDisplay 312;
diag_log "TRIBUNAL_VIGIL_FW_ZEUS|DISPLAY_OPEN";
ctrlActivate (_display displayCtrl 152); uiSleep 0.25;
private _tree = _display displayCtrl 280; private _path = [];
for "_i" from 0 to ((_tree tvCount []) - 1) do {
    if ((_tree tvText [_i]) isEqualTo "Add Fixed Wing Asset") exitWith {_path = [_i];};
    for "_j" from 0 to ((_tree tvCount [_i]) - 1) do {if ((_tree tvText [_i,_j]) isEqualTo "Add Fixed Wing Asset") exitWith {_path = [_i,_j];};};
    if (_path isNotEqualTo []) exitWith {};
};
if ((count _path) > 1) then {_tree tvSetCurSel [_path # 0]; uiSleep 0.1;};
if (_path isNotEqualTo []) then {_tree tvSetCurSel _path;};
private _centerASL = AGLToASL (_target modelToWorldVisual (getCenterOfMass _target));
private _aimASL = _centerASL;
private _camPos = _aimASL vectorAdd [0,-40,15];
private _camDir = vectorNormalized (_aimASL vectorDiff _camPos);
private _right = vectorNormalized (_camDir vectorCrossProduct [0,0,1]);
private _up = vectorNormalized (_right vectorCrossProduct _camDir);
private _surfaceHits = lineIntersectsSurfaces [_camPos, _centerASL, objNull, objNull, true, 32, "VIEW", "FIRE"];
private _targetHit = _surfaceHits select {(_x # 2) isEqualTo _target};
if (_targetHit isNotEqualTo []) then {_aimASL = (_targetHit # 0) # 0;};
private _aimATL = ASLToAGL _aimASL;
private _points = [];
private _projectionDeadline = diag_tickTime + 5;
waitUntil {
    curatorCamera setPosASL _camPos;
    curatorCamera setVectorDirAndUp [_camDir, _up];
    uiSleep 0.05;
    private _originPoint = worldToScreen (ASLToAGL (getPosASL _target));
    private _surfacePoint = worldToScreen _aimATL;
    _points = [];
    if ((count _originPoint) isEqualTo 2) then {
        {
            private _candidate = [(_originPoint # 0) + (_x # 0), (_originPoint # 1) + (_x # 1)];
            if ((_candidate # 0) >= 0 && {(_candidate # 0) <= 1} && {(_candidate # 1) >= 0} && {(_candidate # 1) <= 1}) then {_points pushBack _candidate;};
        } forEach [[0,0],[0,0.075],[0,-0.075],[0.025,0],[0.025,0.075],[0.025,-0.075],[-0.025,0],[-0.025,0.075],[-0.025,-0.075],[0.075,0],[0.075,0.075],[0.075,-0.075],[-0.075,0],[-0.075,0.075],[-0.075,-0.075]];
    };
    if ((count _surfacePoint) isEqualTo 2 && {(_surfacePoint # 0) >= 0} && {(_surfacePoint # 0) <= 1} && {(_surfacePoint # 1) >= 0} && {(_surfacePoint # 1) <= 1}) then {_points pushBack _surfacePoint;};
    _points = _points arrayIntersect _points;
    _points isNotEqualTo [] || {diag_tickTime > _projectionDeadline}
};
diag_log format ["TRIBUNAL_VIGIL_FW_ZEUS|PLACEMENT_READY|1|%1", _points];
private _hover = []; private _hoverDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.02; _hover = curatorMouseOver; (toLowerANSI (_hover param [0, ""]) isEqualTo "object" && {(_hover param [1, objNull]) isEqualTo _target}) || {diag_tickTime > _hoverDeadline}};
if (toLowerANSI (_hover param [0, ""]) isEqualTo "object" && {(_hover param [1, objNull]) isEqualTo _target}) then {diag_log format ["TRIBUNAL_VIGIL_FW_ZEUS|HOVER_READY|1|target=%1|surface=%2", netId _target, _aimASL];} else {diag_log format ["TRIBUNAL_VIGIL_FW_ZEUS|HOVER_FAIL|1|target=%1|hover=%2|asl=%3|velocity=%4|surfaceHits=%5|aim=%6", netId _target, _hover, getPosASL _target, velocity _target, _surfaceHits apply {[netId (_x # 2), _x # 0]}, _aimASL];};
private _resultDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; (count (uiNamespace getVariable ["YSF_FW_ZEUS_RESULTS", []])) >= 1 || {diag_tickTime > _resultDeadline}};
private _results = uiNamespace getVariable ["YSF_FW_ZEUS_RESULTS", []];
private _accepted = _results select {_x # 2};
private _placement = uiNamespace getVariable ["YSF_FW_ZEUS_PLACEMENT_AUDIT", []];
private _native = (count _accepted) isEqualTo 1 && {(count _placement) isEqualTo 1} && {_path isNotEqualTo []} && {_points isNotEqualTo []}
    && {(_accepted # 0 # 4) isNotEqualTo ""} && {(_accepted # 0 # 5) isEqualTo clientOwner}
    && {(_placement # 0 # 2) isEqualTo "YSF_FixedWing_Zeus_Add_Module"} && {(_placement # 0 # 5) isEqualTo clientOwner};
diag_log format ["TRIBUNAL_VIGIL_FW_ZEUS|PLACED|1|%1", _accepted];
["vigil.fwModules.nativeZeusPlacement", _native, format ["path=%1|points=%2|placement=%3|results=%4", _path, _points, _placement, _results]] call _assert;

private _negative = [];
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _negative = missionNamespace getVariable ["TRIBUNAL_FW_MODULE_NEGATIVE", []]; (count _negative) isEqualTo 3 || {diag_tickTime > _negativeDeadline}};
[objNull, objNull, _negative # 1] remoteExecCall ["YSF_fnc_fwModuleZeusClaimServer", 2];
[player, objectFromNetId (_negative # 2), format ["%1-forged", _token]] remoteExecCall ["YSF_fnc_fwModuleZeusClaimServer", 2];
private _receiptDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; private _rows = uiNamespace getVariable ["YSF_FW_ZEUS_RESULTS", []]; (_rows findIf {(_x # 0) isEqualTo (_negative # 1) && {(_x # 3) isEqualTo "duplicate"}}) >= 0 && {(_rows findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0} || {diag_tickTime > _receiptDeadline}};
_results = uiNamespace getVariable ["YSF_FW_ZEUS_RESULTS", []];
private _feedback = (_results findIf {(_x # 5) isNotEqualTo clientOwner}) < 0
    && {(_results findIf {(_x # 0) isEqualTo (_negative # 1) && {(_x # 3) isEqualTo "duplicate"}}) >= 0}
    && {(_results findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0};
["vigil.fwModules.feedbackAndNegatives", _feedback, format ["owner=%1|results=%2", clientOwner, _results]] call _assert;
private _result = []; private _replicationDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_FW_MODULE_RESULT", []]; (count _result) isEqualTo 6 || {diag_tickTime > _replicationDeadline}};
private _publicIds = (call YSF_fwGetPublicRegistry) apply {_x # 0};
private _replicated = (_result # 0) isEqualTo _token && {(_result # 2) in _publicIds} && {(_result # 1 findIf {!(_x in _publicIds)}) < 0} && {!isNull objectFromNetId (_result # 5)};
["vigil.fwModules.clientReplication", _replicated, format ["result=%1|public=%2", _result, call YSF_fwGetPublicRegistry]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FW_MODULE_CLIENT_DONE", _token, true];
'''


ASSERT_EDEN = ["vigil.fwModules.nativeDispatch", "vigil.fwModules.edenAssets", "vigil.fwModules.pointAggregation"]
ASSERT_POLICY = ["vigil.fwModules.nearestIngress", "vigil.fwModules.nearestEgress", "vigil.fwModules.clientDeployEndpoint"]
ASSERT_ZEUS = ["vigil.fwModules.curatorSetup", "vigil.fwModules.zeusAuthority", "vigil.fwModules.nativeZeusPlacement"]
ASSERT_NEGATIVE = ["vigil.fwModules.negativesIdempotent", "vigil.fwModules.feedbackAndNegatives"]
ASSERT_REPLICATION = ["vigil.fwModules.clientAssigned", "vigil.fwModules.clientReplication", "vigil.fwModules.cleanup"]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-fixed-wing-modules", "version": 1,
        "feature_family": "pontifex-vigil-fixed-wing",
        "name": "Vigil fixed-wing authentic Eden and curator activation",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "source/visual-support-tablet/tests/tribunal/vigil_fixed_wing_modules.py",
            "applicability": "Arma 3 dedicated multiplayer with one independently authenticated assigned-curator client",
            "participants": {"server": "authoritative module and registry owner", "client-a": "requester, assigned curator, and replication observer"},
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:fixed-wing-module-activation",
        "label": "Vigil fixed-wing Eden and Zeus activation",
        "kind": "product_behavior",
        "aliases": ["Vigil fixed-wing modules", "Add Fixed Wing Asset"],
        "biki_context": ["biki-page:8458", "biki-page:14844", "biki-page:14896", "biki-page:14822", "biki-page:17356", "biki-page:14941"],
    },
    "arms": [
        {"key": "eden_typed", "role": "treatment", "description": "Authentic typed asset and point modules with native Sync links", "assertions": ASSERT_EDEN},
        {"key": "nearest_policy", "role": "treatment", "description": "Accepted deploy/RTB lifecycle consumes nearest aggregated mission points", "assertions": ASSERT_POLICY},
        {"key": "zeus_authorized", "role": "treatment", "description": "One genuine placement by the assigned curator on one exact plane", "assertions": ASSERT_ZEUS},
        {"key": "invalid_replay", "role": "negative_control", "description": "Delivered replay and wrong-class requests cannot add another asset", "assertions": ASSERT_NEGATIVE},
        {"key": "replication", "role": "replicate", "description": "Client independently resolves authoritative registry identities and correlated results", "assertions": ASSERT_REPLICATION},
    ],
    "causal_relationships": [
        {"key": "authorized-v-invalid", "relation": "CAUSAL_PAIR_WITH", "source": "zeus_authorized", "target": "invalid_replay", "controlled_dimensions": ["mission", "server registry", "requesting client", "target class family"]},
        {"key": "authority-v-replica", "relation": "REPLICATES", "source": "zeus_authorized", "target": "replication", "controlled_dimensions": ["operation identity", "asset identity", "run token"]},
    ],
    "propositions": [
        {"id": "pontifex:vigil:fw-eden-aggregate", "text": "Authentic retained Eden modules aggregate exact synchronized planes and mission points without adding an unsynchronized control.", "intended_use": "primary_result", "assertions": ASSERT_EDEN, "rationale": "Configured dispatch receipts, pre-deletion source identities, registry identities, point positions, and an equal unsynchronized control jointly establish the module path."},
        {"id": "pontifex:vigil:fw-nearest-points", "text": "Multiple ingress and egress modules select the nearest point at the consequential deploy and RTB boundaries.", "intended_use": "primary_result", "assertions": ASSERT_POLICY, "rationale": "Comfortably separated points are independently selected from requester and aircraft positions and then observed in authoritative lifecycle state."},
        {"id": "pontifex:vigil:fw-zeus-authority", "text": "An assigned curator can add one exact plane once, receives its correlated result privately, and delivered replay or wrong-class requests do not mutate the registry.", "intended_use": "primary_result", "assertions": ASSERT_ZEUS + ASSERT_NEGATIVE + ASSERT_REPLICATION, "rationale": "A genuine UI placement is paired with delivered negative requests, exact audit/registry identities, placer-owned receipts, and client replication."},
    ],
    "unresolved": ["Multiple-client audience isolation remains a client-N follow-up; the server target is owner-specific and this run proves the one-client instance."],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-fixed-wing-modules", tier="gameplay",
    server_expected=frozenset(ASSERT_EDEN + ["vigil.fwModules.curatorSetup"] + ASSERT_POLICY[:2] + ["vigil.fwModules.zeusAuthority", "vigil.fwModules.negativesIdempotent", "vigil.fwModules.cleanup"]),
    client_expected=frozenset(["vigil.fwModules.clientAssigned", "vigil.fwModules.clientDeployEndpoint", "vigil.fwModules.nativeZeusPlacement", "vigil.fwModules.feedbackAndNegatives", "vigil.fwModules.clientReplication"]),
    server_sqf=SERVER_SQF, client_sqf=CLIENT_SQF,
    metadata={"product": "visual-support-tablet", "feature": "fixed-wing-modules", "visual_driver": "zeus-placement", "visual_armed_marker": "TRIBUNAL_VIGIL_FW_ZEUS|ARMED", "zeus_marker_prefix": "TRIBUNAL_VIGIL_FW_ZEUS", "zeus_placements": 1},
    mission_entities=(
        MissionEntity("TRIBUNAL_FW_ASSET_MODULE_A", "YSF_FixedWing_Asset_Module", "YSF_Tablet", "Logic", (3600,0,3600)),
        MissionEntity("TRIBUNAL_FW_ASSET_MODULE_B", "YSF_FixedWing_Asset_Module", "YSF_Tablet", "Logic", (3620,0,3600)),
        MissionEntity("TRIBUNAL_FW_INFIL_MODULE_A", "YSF_FixedWing_Infil_Module", "YSF_Tablet", "Logic", (4650,1200,2800)),
        MissionEntity("TRIBUNAL_FW_INFIL_MODULE_B", "YSF_FixedWing_Infil_Module", "YSF_Tablet", "Logic", (2500,1200,5000)),
        MissionEntity("TRIBUNAL_FW_EXFIL_MODULE_A", "YSF_FixedWing_Exfil_Module", "YSF_Tablet", "Logic", (4750,1200,3000)),
        MissionEntity("TRIBUNAL_FW_EXFIL_MODULE_B", "YSF_FixedWing_Exfil_Module", "YSF_Tablet", "Logic", (2200,1200,5200)),
        MissionEntity("TRIBUNAL_FW_EDEN_A", "B_Plane_CAS_01_F", "A3_Air_F_EPC_Plane_CAS_01", "Object", (4300,16,2800)),
        MissionEntity("TRIBUNAL_FW_EDEN_B", "B_Plane_CAS_01_F", "A3_Air_F_EPC_Plane_CAS_01", "Object", (4350,16,2800)),
        MissionEntity("TRIBUNAL_FW_ZEUS_TARGET", "C_Plane_Civil_01_F", "A3_Air_F_Exp_Plane_Civil_01", "Object", (2000,6,5700)),
        MissionEntity("TRIBUNAL_FW_CONTROL", "C_Plane_Civil_01_F", "A3_Air_F_Exp_Plane_Civil_01", "Object", (2050,6,5700)),
    ),
    mission_syncs=(MissionSync("TRIBUNAL_FW_ASSET_MODULE_A", "TRIBUNAL_FW_EDEN_A"), MissionSync("TRIBUNAL_FW_ASSET_MODULE_B", "TRIBUNAL_FW_EDEN_B")),
    review=ScenarioReview(test_type="specification", behavior_contract="Authentic retained Eden fixed-wing modules aggregate exact synchronized assets and nearest mission points; an assigned curator adds one exact plane once with placer-only correlated feedback while delivered replay/forgery controls preserve state.", outcome="KEEP AS-IS AND SPEC-TEST", rationale="The accepted downstream fixed-wing lifecycle remains intact; this scenario closes only authentic Eden/curator dispatch, authority, aggregation, nearest-point policy, idempotence, locality, replication, and cleanup.", dependencies=("typed Eden module fixture", "authenticated curator input adapter", "accepted fixed-wing registry/deploy/RTB lifecycle", "one authenticated client"), evidence_types=frozenset({"configured-dispatch", "native-sync", "native-curator-placement", "exact-identity", "negative-control", "authoritative-state", "replication", "cleanup"}), locality_requirements="Eden dispatch and registry mutation are server-owned; the curator module is client-owned at placement, claimed by the server for the assigned curator, and its correlated result targets only that requester owner."),
    evidence_contract=EVIDENCE_CONTRACT,
)
