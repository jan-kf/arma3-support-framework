"""Permanent Tier 3 contract for Field Utilities Bridge Builder."""

from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-bridge-builder",
    tier="gameplay",
    server_expected=frozenset({
        "bridge.fixture",
        "bridge.build.authority",
        "bridge.build.geometry",
        "bridge.build.locality",
        "bridge.traversal.authoritative",
        "bridge.remove.scope",
        "bridge.result.lifecycle",
        "bridge.advanced.plan",
        "bridge.auto.support",
        "bridge.wide.vehicle",
        "bridge.ramp.physical",
        "bridge.advanced.cleanup",
        "bridge.cleanup",
    }),
    client_expected=frozenset({
        "bridge.interaction.registration",
        "bridge.interaction.conditions",
        "bridge.dialog.open",
        "bridge.preview.plan",
        "bridge.build.replication",
        "bridge.traversal.physical",
        "bridge.remove.replication",
        "bridge.advanced.replication",
        "bridge.ramp.traversal",
        "bridge.cleanup.client",
    }),
    server_sqf=r'''
private _scenarioPlayer = allPlayers param [0, objNull];
private _playerDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.1;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _playerDeadline}
};
private _originASL = [10, 10, 0];
private _forward = [0, 1, 0];
private _right = [_forward # 1, -(_forward # 0), 0];
private _boxASL = (_originASL vectorAdd (_forward vectorMultiply 3)) vectorAdd [0, 0, 1.2];
private _box = createVehicle ["YFU_Bridge_Box", ASLToAGL _boxASL, [], 0, "CAN_COLLIDE"];
_box setPosASL _boxASL;
_box setVectorDirAndUp [_forward, [0, 0, 1]];
_box enableSimulationGlobal false;
[_box] call YFU_bridge_ensureBoxDefaults;
_box setVariable ["YFU_bridge_manual_plank_count", 4, true];
_box setVariable ["YFU_bridge_plan_max_distance", 30, true];
missionNamespace setVariable ["YFU_bridge_perPlankBuildDelay", 0.05, true];

private _foreignASL = (_boxASL vectorAdd (_right vectorMultiply 3)) vectorAdd [0, 0, -0.2];
private _foreign = createVehicle ["Land_Plank_01_4m_F", ASLToAGL _foreignASL, [], 0, "CAN_COLLIDE"];
_foreign setPosASL _foreignASL;
_foreign setVectorDirAndUp [_forward, [0, 0, 1]];
_foreign enableSimulationGlobal false;
_foreign setVariable ["TRIBUNAL_bridge_foreign", _token, true];

private _fixture = [_token, netId _box, netId _foreign, _originASL, _boxASL, _forward];
missionNamespace setVariable ["TRIBUNAL_BRIDGE_FIXTURE", _fixture, true];
private _fixtureOk = !isNull _scenarioPlayer && {!isNull _box} && {!isNull _foreign}
    && {isClass (configFile >> "CfgVehicles" >> "Land_Plank_01_4m_F")}
    && {local _box};
["bridge.fixture", _fixtureOk, format ["fixture=%1|boxLocal=%2|boxOwner=%3|classAddon=%4", _fixture, local _box, owner _box, configSourceAddonList (configFile >> "CfgVehicles" >> "Land_Plank_01_4m_F")]] call _assert;

private _buildDeadline = diag_tickTime + 90;
private _buildResult = [];
waitUntil {
    uiSleep 0.1;
    _buildResult = _box getVariable ["YFU_bridge_last_result", []];
    ((_buildResult param [1, ""]) isEqualTo "build" && {(_buildResult param [2, ""]) in ["complete", "failed"]})
        || {diag_tickTime > _buildDeadline}
};
private _segmentIds = _buildResult param [4, []];
private _segments = _segmentIds apply {objectFromNetId _x};
private _buildAuthority = ((_buildResult param [0, ""]) find "bridge-build-") isEqualTo 0
    && {(_buildResult param [2, ""]) isEqualTo "complete"}
    && {(_buildResult param [3, ""]) isEqualTo "complete"}
    && {(_buildResult param [6, -1]) isEqualTo owner _scenarioPlayer}
    && {count _segments isEqualTo 4}
    && {(_segments findIf {isNull _x || {typeOf _x isNotEqualTo "Land_Plank_01_4m_F"} || {(_x getVariable ["YFU_bridge_builder_box", ""]) isNotEqualTo netId _box}}) < 0};
["bridge.build.authority", _buildAuthority, format ["result=%1|box=%2|segments=%3|requester=%4", _buildResult, netId _box, _segmentIds, owner _scenarioPlayer]] call _assert;

private _spacing = [];
for "_index" from 1 to ((count _segments) - 1) do {
    _spacing pushBack ((getPosASL (_segments # _index)) distance (getPosASL (_segments # (_index - 1))));
};
private _directions = _segments apply {(vectorDirVisual _x) vectorDotProduct _forward};
private _heights = _segments apply {(getPosASL _x) # 2};
private _geometryOk = count _segments isEqualTo 4
    && {(_spacing findIf {abs (_x - 4.1792) > 0.08}) < 0}
    && {(_directions findIf {_x < 0.995}) < 0}
    && {((selectMax _heights) - (selectMin _heights)) < 0.05};
["bridge.build.geometry", _geometryOk, format ["positions=%1|spacing=%2|directions=%3|heights=%4", _segments apply {getPosASL _x}, _spacing, _directions, _heights]] call _assert;
private _localityRows = _segments apply {[netId _x, local _x, owner _x]};
private _localityOk = count _segments isEqualTo 4 && {(_segments findIf {!local _x}) < 0};
["bridge.build.locality", _localityOk, format ["serverLocal=true|segments=%1", _localityRows]] call _assert;

private _traverseDeadline = diag_tickTime + 35;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_TRAVERSE"} || {diag_tickTime > _traverseDeadline}};
private _traverse = missionNamespace getVariable ["TRIBUNAL_BRIDGE_TRAVERSE", []];
private _traverseOk = (_traverse param [0, ""]) isEqualTo _token
    && {(_traverse param [1, false]) isEqualTo true}
    && {(_traverse param [5, 0]) >= 3};
["bridge.traversal.authoritative", _traverseOk, format ["clientEvidence=%1|serverPlayerASL=%2|vehicle=%3", _traverse, if (isNull _scenarioPlayer) then {[]} else {getPosASL _scenarioPlayer}, vehicle _scenarioPlayer]] call _assert;

private _removeDeadline = diag_tickTime + 45;
private _removeResult = [];
waitUntil {
    uiSleep 0.1;
    _removeResult = _box getVariable ["YFU_bridge_last_result", []];
    ((_removeResult param [1, ""]) isEqualTo "remove" && {(_removeResult param [2, ""]) in ["complete", "failed"]})
        || {diag_tickTime > _removeDeadline}
};
private _ownedGone = (_segmentIds findIf {!isNull (objectFromNetId _x)}) < 0;
private _scopeOk = (_removeResult param [0, ""]) isEqualTo format ["tribunal-bridge-remove-%1", _token]
    && {(_removeResult param [2, ""]) isEqualTo "complete"}
    && {_ownedGone} && {!isNull _foreign}
    && {(_foreign getVariable ["YFU_bridge_builder_box", ""]) isEqualTo ""};
["bridge.remove.scope", _scopeOk, format ["result=%1|ownedGone=%2|foreign=%3|foreignAlive=%4|foreignTag=%5", _removeResult, _ownedGone, netId _foreign, !isNull _foreign, _foreign getVariable ["YFU_bridge_builder_box", ""]]] call _assert;
private _lifecycleOk = !(_box getVariable ["YFU_bridge_building", true])
    && {!(_box getVariable ["YFU_bridge_removing", true])}
    && {(_box getVariable ["YFU_bridge_operation_id", "bad"]) isEqualTo ""};
["bridge.result.lifecycle", _lifecycleOk, format ["build=%1|remove=%2|operation=%3", _box getVariable ["YFU_bridge_building", nil], _box getVariable ["YFU_bridge_removing", nil], _box getVariable ["YFU_bridge_operation_id", nil]]] call _assert;

private _clientRemoveDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_REMOVE_OBSERVED"} || {diag_tickTime > _clientRemoveDeadline}};
private _clientRemove = missionNamespace getVariable ["TRIBUNAL_BRIDGE_REMOVE_OBSERVED", []];
private _clientRemoveOk = (_clientRemove param [0, ""]) isEqualTo _token && {(_clientRemove param [1, false]) isEqualTo true};

private _advancedBoxASL = [50, 10, 1.2];
private _advancedBox = createVehicle ["YFU_Bridge_Box", ASLToAGL _advancedBoxASL, [], 0, "CAN_COLLIDE"];
_advancedBox setPosASL _advancedBoxASL;
_advancedBox setVectorDirAndUp [[0, 1, 0], [0, 0, 1]];
_advancedBox enableSimulationGlobal false;
private _widePlan = ["bridge-plan-v1", true, false, false, 2, 16, 0];
private _wideQueue = [_advancedBox, 16, "Land_Plank_01_4m_F", true, false, _widePlan] call YFU_bridge_buildQueueFromObject;
private _rampPlan = ["bridge-plan-v1", false, false, true, 2, 9, 0];
private _rampQueue = [_advancedBox, 9, "Land_Plank_01_4m_F", false, true, _rampPlan] call YFU_bridge_buildQueueFromObject;
_advancedBox setVectorDirAndUp [[0, 0.979796, 0.2], [0, -0.2, 0.979796]];
private _matchOrientation = [_advancedBox, false, ["bridge-plan-v1", false, true, false, 2, 4, 0]] call YFU_bridge_getBuildOrientation;
private _levelOrientation = [_advancedBox, false, ["bridge-plan-v1", false, false, false, 2, 4, 0]] call YFU_bridge_getBuildOrientation;
_advancedBox setVectorDirAndUp [[0, 1, 0], [0, 0, 1]];
private _wideSteps = _wideQueue apply {_x # 6};
private _rampTypes = _rampQueue apply {_x # 7};
private _planOk = count _wideQueue isEqualTo 16
    && {(_wideSteps findIf {abs (_x - 0.8982) > 0.01}) < 0}
    && {_rampTypes isEqualTo ["ramp_up", "ramp_up", "flat", "flat", "flat", "flat", "ramp_down", "ramp_down", "clip"]}
    && {abs (((_matchOrientation # 0) # 2) - 0.2) < 0.01}
    && {abs (((_levelOrientation # 0) # 2)) < 0.001}
    && {((_levelOrientation # 2) vectorDistance [0, 0, 1]) < 0.001};
["bridge.advanced.plan", _planOk, format ["wideCount=%1|wideSteps=%2|rampTypes=%3|match=%4|level=%5", count _wideQueue, _wideSteps, _rampTypes, _matchOrientation, _levelOrientation]] call _assert;

private _supportATL = [260, 10, 2];
private _supportBox = createVehicle ["YFU_Bridge_Box", _supportATL, [], 0, "CAN_COLLIDE"];
_supportBox setPosATL _supportATL;
_supportBox setVectorDirAndUp [[0, 1, 0], [0, 0, 1]];
_supportBox enableSimulationGlobal false;
private _vehicleControl = createVehicle ["B_MRAP_01_F", _supportATL vectorAdd [0, 12, -2], [], 0, "CAN_COLLIDE"];
_vehicleControl setPosATL (_supportATL vectorAdd [0, 12, -2]);
_vehicleControl enableSimulationGlobal false;
private _buildingSupport = createVehicle ["Land_Cargo_House_V1_F", _supportATL vectorAdd [0, 24, -2], [], 0, "CAN_COLLIDE"];
_buildingSupport setPosATL (_supportATL vectorAdd [0, 24, -2]);
_buildingSupport setDir 180;
_buildingSupport enableSimulationGlobal false;
uiSleep 1;
private _supportStart = getPosASL _supportBox;
private _rawSupportHits = lineIntersectsSurfaces [_supportStart, _supportStart vectorAdd [0, 50, 0], _supportBox, objNull, true, 16, "FIRE", "GEOM"];
private _vehicleHit = _rawSupportHits findIf {(_x # 2) isEqualTo _vehicleControl || {(_x # 3) isEqualTo _vehicleControl}};
private _buildingHit = _rawSupportHits findIf {(_x # 2) isEqualTo _buildingSupport || {(_x # 3) isEqualTo _buildingSupport}};
private _autoPlan = [_supportBox, "Land_Plank_01_4m_F", false, 50, ["bridge-plan-v1", false, false, false, 2, 0, 0]] call YFU_bridge_computePlan;
private _autoDistance = _supportStart distance (_autoPlan # 1);
private _vehicleDistance = if (_vehicleHit < 0) then {-1} else {_supportStart distance ((_rawSupportHits # _vehicleHit) # 0)};
private _buildingDistance = if (_buildingHit < 0) then {-1} else {_supportStart distance ((_rawSupportHits # _buildingHit) # 0)};
private _supportOk = _vehicleHit >= 0 && {_buildingHit >= 0}
    && {_vehicleDistance + 5 < _buildingDistance}
    && {_autoPlan # 12}
    && {abs (_autoDistance - _buildingDistance) < 0.5};
["bridge.auto.support", _supportOk, format ["raw=%1|vehicleDistance=%2|buildingDistance=%3|autoDistance=%4|planEnd=%5", _rawSupportHits apply {[(_x # 0), typeOf (_x # 2), typeOf (_x # 3)]}, _vehicleDistance, _buildingDistance, _autoDistance, _autoPlan # 1]] call _assert;
deleteVehicle _vehicleControl;
deleteVehicle _buildingSupport;
deleteVehicle _supportBox;

private _wideSegments = [];
{
    _x params ["_positionASL", "_className", "_segmentDir", "_up", "_dedupeRadius"];
    _wideSegments pushBack ([_positionASL, _className, _segmentDir, _up, _dedupeRadius, _advancedBox, "tribunal-wide"] call YFU_bridge_spawnPlacedSegment);
} forEach _wideQueue;
private _rampBoxASL = [100, 10, 1.2];
private _rampBox = createVehicle ["YFU_Bridge_Box", ASLToAGL _rampBoxASL, [], 0, "CAN_COLLIDE"];
_rampBox setPosASL _rampBoxASL;
_rampBox setVectorDirAndUp [[0, 1, 0], [0, 0, 1]];
_rampBox enableSimulationGlobal false;
private _physicalRampQueue = [_rampBox, 9, "Land_Plank_01_4m_F", false, true, _rampPlan] call YFU_bridge_buildQueueFromObject;
private _rampSegments = [];
{
    _x params ["_positionASL", "_className", "_segmentDir", "_up", "_dedupeRadius"];
    _rampSegments pushBack ([_positionASL, _className, _segmentDir, _up, _dedupeRadius, _rampBox, "tribunal-ramp"] call YFU_bridge_spawnPlacedSegment);
} forEach _physicalRampQueue;
private _wideVehicle = createVehicle ["B_Quadbike_01_F", ASLToAGL ((getPosASL (_wideSegments # 0)) vectorAdd [0, 0, 0.8]), [], 0, "CAN_COLLIDE"];
_wideVehicle setPosASL ((getPosASL (_wideSegments # 0)) vectorAdd [0, 0, 0.8]);
_wideVehicle setDir 0;
private _fallControl = createVehicle ["B_Quadbike_01_F", ASLToAGL ((getPosASL (_wideSegments # 0)) vectorAdd [8, 0, 0.8]), [], 0, "CAN_COLLIDE"];
_fallControl setPosASL ((getPosASL (_wideSegments # 0)) vectorAdd [8, 0, 0.8]);
_fallControl setDir 0;
private _wideStart = getPosASL _wideVehicle;
private _fallStart = getPosASL _fallControl;
missionNamespace setVariable ["TRIBUNAL_BRIDGE_ADVANCED_FIXTURE", [_token, netId _advancedBox, _wideSegments apply {netId _x}, netId _wideVehicle, netId _fallControl, _rampSegments apply {netId _x}], true];
private _advancedAckDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_ADVANCED_ACK"} || {diag_tickTime > _advancedAckDeadline}};
private _advancedAck = missionNamespace getVariable ["TRIBUNAL_BRIDGE_ADVANCED_ACK", []];
private _wideContacts = 0;
private _wideDeadline = diag_tickTime + 6;
waitUntil {
    _wideVehicle setVelocity [0, 3, (velocity _wideVehicle) # 2];
    private _position = getPosASL _wideVehicle;
    private _hits = lineIntersectsSurfaces [_position vectorAdd [0, 0, 0.2], _position vectorAdd [0, 0, -1.5], _wideVehicle, objNull, true, 8, "GEOM", "NONE"];
    if ((_hits findIf {(_x # 2) in _wideSegments}) >= 0) then {_wideContacts = _wideContacts + 1};
    uiSleep 0.05;
    diag_tickTime > _wideDeadline
};
private _wideEnd = getPosASL _wideVehicle;
private _fallEnd = getPosASL _fallControl;
private _wideOk = (_advancedAck param [0, ""]) isEqualTo _token
    && {(_advancedAck param [1, false])}
    && {((_wideEnd # 1) - (_wideStart # 1)) > 9}
    && {_wideContacts >= 20}
    && {((_fallStart # 2) - (_fallEnd # 2)) > 5}
    && {((_wideStart # 2) - (_wideEnd # 2)) < 2};
["bridge.wide.vehicle", _wideOk, format ["start=%1|end=%2|controlStart=%3|controlEnd=%4|contacts=%5|ack=%6", _wideStart, _wideEnd, _fallStart, _fallEnd, _wideContacts, _advancedAck]] call _assert;
missionNamespace setVariable ["TRIBUNAL_BRIDGE_ADVANCED_RESULT", [_token, _wideOk, _wideStart, _wideEnd, _fallStart, _fallEnd, _wideContacts], true];
private _rampDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_RAMP_RESULT"} || {diag_tickTime > _rampDeadline}};
private _rampResult = missionNamespace getVariable ["TRIBUNAL_BRIDGE_RAMP_RESULT", []];
private _rampOk = (_rampResult param [0, ""]) isEqualTo _token && {(_rampResult param [1, false])};
["bridge.ramp.physical", _rampOk, format ["result=%1|segments=%2", _rampResult, _rampSegments apply {[netId _x, getPosASL _x, vectorDirVisual _x, vectorUpVisual _x]}]] call _assert;
deleteVehicle _wideVehicle;
deleteVehicle _fallControl;
{deleteVehicle _x} forEach _wideSegments;
{deleteVehicle _x} forEach _rampSegments;
deleteVehicle _rampBox;
deleteVehicle _advancedBox;
private _advancedDeleteDeadline = diag_tickTime + 2;
waitUntil {
    uiSleep 0.01;
    (isNull _wideVehicle && {isNull _fallControl} && {isNull _advancedBox} && {isNull _rampBox} && {(_wideSegments findIf {!isNull _x}) < 0} && {(_rampSegments findIf {!isNull _x}) < 0})
        || {diag_tickTime >= _advancedDeleteDeadline}
};
private _advancedCleanup = isNull _wideVehicle && {isNull _fallControl} && {isNull _advancedBox} && {isNull _rampBox} && {(_wideSegments findIf {!isNull _x}) < 0} && {(_rampSegments findIf {!isNull _x}) < 0};
["bridge.advanced.cleanup", _advancedCleanup, format ["vehicle=%1|control=%2|box=%3|wide=%4|rampBox=%5|ramps=%6", isNull _wideVehicle, isNull _fallControl, isNull _advancedBox, _wideSegments apply {isNull _x}, isNull _rampBox, _rampSegments apply {isNull _x}]] call _assert;

deleteVehicle _foreign;
deleteVehicle _box;
private _cleanupDeadline = diag_tickTime + 2;
waitUntil {uiSleep 0.01; (isNull _box && {isNull _foreign}) || {diag_tickTime >= _cleanupDeadline}};
private _cleanupOk = isNull _box && {isNull _foreign} && {_ownedGone} && {_clientRemoveOk};
missionNamespace setVariable ["TRIBUNAL_BRIDGE_CLEANUP", [_token, _cleanupOk], true];
["bridge.cleanup", _cleanupOk, format ["boxNull=%1|foreignNull=%2|ownedGone=%3|clientRemove=%4", isNull _box, isNull _foreign, _ownedGone, _clientRemove]] call _assert;
''',
    client_sqf=r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];
private _fixtureDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_FIXTURE"} || {diag_tickTime > _fixtureDeadline}};
private _fixture = missionNamespace getVariable ["TRIBUNAL_BRIDGE_FIXTURE", []];
private _boxId = _fixture param [1, ""];
private _box = if (_boxId isEqualTo "") then {objNull} else {objectFromNetId _boxId};
private _boxDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; !isNull _box || {diag_tickTime > _boxDeadline}};
private _originalASL = getPosASL player;
private _originalDir = getDir player;
player enableSimulation false;

private _className = if (isNull _box) then {""} else {typeOf _box call ace_common_fnc_getConfigName};
private _trees = ace_interact_menu_ActNamespace getOrDefault [_className, []];
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
private _action = [_trees, "YFU_BoxBridgeOpenUI_Class"] call _findAction;
private _pathFound = _action isNotEqualTo [] && {(_action param [1, ""]) isEqualTo "Open Bridge Builder"};
private _collectActive = {
    params ["_target", "_data"];
    if (isNull _target || {_data isEqualTo []}) exitWith {[]};
    ace_interact_menu_objectActionList = [];
    [_target, [_data, []], [], player distance _target] call ace_interact_menu_fnc_collectActiveActionTree
};
private _boxASL = if (isNull _box) then {getPosASL player} else {getPosASL _box};
private _boxForward = if (isNull _box) then {vectorDir player} else {vectorNormalized (vectorDirVisual _box)};
player setPosASL ((_boxASL vectorAdd (_boxForward vectorMultiply -10)) vectorAdd [0, 0, -1.2]);
private _outOfRange = ([_box, _action] call _collectActive) isEqualTo [];
player setPosASL ((_boxASL vectorAdd (_boxForward vectorMultiply -5)) vectorAdd [0, 0, -1.2]);
_box setVariable ["YFU_bridge_building", true, true];
private _busy = ([_box, _action] call _collectActive) isEqualTo [];
_box setVariable ["YFU_bridge_building", false, true];
private _idleTree = [_box, _action] call _collectActive;
private _idle = _idleTree isNotEqualTo [];
private _registrationOk = _identity isEqualTo "client-a" && {_pathFound} && {!isNil "ace_interact_menu_fnc_collectActiveActionTree"};
["bridge.interaction.registration", _registrationOk, format ["identity=%1|class=%2|path=%3|display=%4|aceVersion=%5", _identity, _className, _action param [0, ""], _action param [1, ""], getText (configFile >> "CfgPatches" >> "ace_interact_menu" >> "versionStr")]] call _assert;
["bridge.interaction.conditions", _outOfRange && {_busy} && {_idle}, format ["outOfRangeAbsent=%1|busyAbsent=%2|idlePresent=%3|distance=%4|activeTree=%5", _outOfRange, _busy, _idle, player distance _box, _idleTree]] call _assert;
if (_registrationOk && {_idle}) then {
    [_box, player, _action param [6, []]] call (_action # 3);
};
private _dialogDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    private _waitLease = uiNamespace getVariable ["YFU_bridge_planner_lease_id", ""];
    private _waitResult = if (isNull _box) then {[]} else {_box getVariable ["YFU_bridge_planner_last_result", []]};
    (!isNull (call YFU_bridge_getDialogDisplay)
        && {_waitLease isNotEqualTo ""}
        && {(_waitResult param [0, ""]) isEqualTo _waitLease}
        && {(_waitResult param [1, ""]) isEqualTo "granted"})
        || {diag_tickTime > _dialogDeadline}
};
disableSerialization;
private _display = call YFU_bridge_getDialogDisplay;
private _page = if (isNull _display) then {controlNull} else {_display displayCtrl 98210};
private _buildControl = if (isNull _display) then {controlNull} else {_display displayCtrl 98261};
private _plannerResult = if (isNull _box) then {[]} else {_box getVariable ["YFU_bridge_planner_last_result", []]};
private _localLeaseId = uiNamespace getVariable ["YFU_bridge_planner_lease_id", ""];
private _dialogOk = !isNull _display && {(ctrlIDD _display) isEqualTo 98200} && {!isNull _page} && {!isNull _buildControl} && {ctrlEnabled _buildControl}
    && {(_plannerResult param [0, ""]) isEqualTo _localLeaseId}
    && {(_plannerResult param [1, ""]) isEqualTo "granted"}
    && {(_plannerResult param [2, ""]) isEqualTo "accepted"}
    && {(_plannerResult param [3, -1]) isEqualTo clientOwner};
["bridge.dialog.open", _dialogOk, format ["display=%1|idd=%2|page=%3|build=%4|enabled=%5|planner=%6|localLease=%7", !isNull _display, if (isNull _display) then {-1} else {ctrlIDD _display}, !isNull _page, !isNull _buildControl, if (isNull _buildControl) then {false} else {ctrlEnabled _buildControl}, _plannerResult, _localLeaseId]] call _assert;

if (!isNull _box) then {
    _box setVariable ["YFU_bridge_manual_plank_count", 4, true];
    _box setVariable ["YFU_bridge_plan_widthwise", false, true];
    _box setVariable ["YFU_bridge_ramp_mode", false, true];
    _box setVariable ["YFU_bridge_pitch_offset_degrees", 0, true];
    [_box, false] call YFU_bridge_beginPlanPreview;
    call YFU_bridge_dialogRefresh;
};
private _queue = if (isNull _box) then {[]} else {[_box] call YFU_bridge_getPlannedQueue};
private _previewOk = count _queue isEqualTo 4
    && {(missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull]) isEqualTo _box}
    && {(_queue findIf {(_x param [1, ""]) isNotEqualTo "Land_Plank_01_4m_F"}) < 0};
["bridge.preview.plan", _previewOk, format ["queue=%1|active=%2|first=%3", count _queue, (missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull]) isEqualTo _box, _queue param [0, []]]] call _assert;
if (_dialogOk && {_previewOk}) then {call YFU_bridge_dialogSubmit;};

private _requestDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["YFU_bridge_last_request", []]) isNotEqualTo [] || {diag_tickTime > _requestDeadline}};
private _lastRequest = missionNamespace getVariable ["YFU_bridge_last_request", []];
private _buildDeadline = diag_tickTime + 45;
private _buildResult = [];
waitUntil {
    uiSleep 0.1;
    _buildResult = if (isNull _box) then {[]} else {_box getVariable ["YFU_bridge_last_result", []]};
    ((_buildResult param [1, ""]) isEqualTo "build" && {(_buildResult param [2, ""]) in ["complete", "failed"]}) || {diag_tickTime > _buildDeadline}
};
private _segmentIds = _buildResult param [4, []];
private _segments = _segmentIds apply {objectFromNetId _x};
private _replicationOk = (_lastRequest param [1, ""]) isEqualTo "build"
    && {(_lastRequest param [0, ""]) isEqualTo (_buildResult param [0, "bad"])}
    && {(_buildResult param [2, ""]) isEqualTo "complete"} && {count _segments isEqualTo 4}
    && {(_segments findIf {isNull _x || {!alive _x} || {(_x getVariable ["YFU_bridge_builder_box", ""]) isNotEqualTo _boxId}}) < 0};
["bridge.build.replication", _replicationOk, format ["result=%1|segments=%2|locality=%3", _buildResult, _segmentIds, _segments apply {[netId _x, local _x, owner _x]}]] call _assert;

private _traverseOk = false;
private _startASL = [];
private _endASL = [];
private _minimumClearance = 1e9;
private _contactSamples = 0;
if (count _segments isEqualTo 4 && {(_segments findIf {isNull _x}) < 0}) then {
    private _first = _segments # 0;
    private _last = _segments # 3;
    private _dir = vectorNormalized ((getPosASL _last) vectorDiff (getPosASL _first));
    private _right = vectorNormalized ([0, 0, 1] vectorCrossProduct _dir);
    player setPosASL ((getPosASL _first) vectorAdd [0, 0, 0.75]);
    player setVectorDirAndUp [_dir, [0, 0, 1]];
    player enableSimulation true;
    _startASL = getPosASL player;
    private _startedAt = diag_tickTime;
    waitUntil {
        private _velocity = velocity player;
        player setVelocity [(_dir # 0) * 4, (_dir # 1) * 4, _velocity # 2];
        private _position = getPosASL player;
        _minimumClearance = _minimumClearance min ((_position # 2) - getTerrainHeightASL _position);
        private _hits = lineIntersectsSurfaces [_position vectorAdd [0, 0, 0.2], _position vectorAdd [0, 0, -1.4], player, objNull, true, 4, "GEOM", "NONE"];
        if ((_hits findIf {(_x # 2) in _segments}) >= 0) then {_contactSamples = _contactSamples + 1};
        uiSleep 0.05;
        diag_tickTime > (_startedAt + 7) || {!alive player}
    };
    _endASL = getPosASL player;
    private _delta = _endASL vectorDiff _startASL;
    private _forward = _delta vectorDotProduct _dir;
    private _lateral = abs (_delta vectorDotProduct _right);
    _traverseOk = alive player && {_forward > 7} && {_lateral < 0.7} && {_minimumClearance > 0.65} && {_contactSamples >= 3};
};
["bridge.traversal.physical", _traverseOk, format ["start=%1|end=%2|minClearance=%3|contactSamples=%4", _startASL, _endASL, _minimumClearance, _contactSamples]] call _assert;
missionNamespace setVariable ["TRIBUNAL_BRIDGE_TRAVERSE", [_token, _traverseOk, _startASL, _endASL, _minimumClearance, _contactSamples], true];

if (!isNull _box) then {
    player enableSimulation false;
    player setPosASL (((getPosASL _box) vectorAdd (_boxForward vectorMultiply -3)) vectorAdd [0, 0, -1.2]);
    // Let the client-owned player's reposition replicate before the server
    // validates the removal request's eight-metre interaction boundary.
    uiSleep 1;
    [_box, player, format ["tribunal-bridge-remove-%1", _token]] remoteExecCall ["YFU_bridge_startRemoveFromBox", 2];
};
private _removeDeadline = diag_tickTime + 45;
private _removeResult = [];
waitUntil {
    uiSleep 0.1;
    _removeResult = if (isNull _box) then {[]} else {_box getVariable ["YFU_bridge_last_result", []]};
    ((_removeResult param [1, ""]) isEqualTo "remove" && {(_removeResult param [2, ""]) in ["complete", "failed"]}) || {diag_tickTime > _removeDeadline}
};
private _removed = (_segmentIds findIf {!isNull (objectFromNetId _x)}) < 0;
["bridge.remove.replication", (_removeResult param [2, ""]) isEqualTo "complete" && {_removed}, format ["result=%1|removed=%2", _removeResult, _removed]] call _assert;
missionNamespace setVariable ["TRIBUNAL_BRIDGE_REMOVE_OBSERVED", [_token, (_removeResult param [2, ""]) isEqualTo "complete" && {_removed}], true];
private _advancedFixtureDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_ADVANCED_FIXTURE"} || {diag_tickTime > _advancedFixtureDeadline}};
private _advancedFixture = missionNamespace getVariable ["TRIBUNAL_BRIDGE_ADVANCED_FIXTURE", []];
private _advancedIds = _advancedFixture param [2, []];
private _advancedSegments = _advancedIds apply {objectFromNetId _x};
private _rampIds = _advancedFixture param [5, []];
private _rampSegments = _rampIds apply {objectFromNetId _x};
private _advancedReplication = (_advancedFixture param [0, ""]) isEqualTo _token
    && {count _advancedSegments isEqualTo 16}
    && {(_advancedSegments findIf {isNull _x || {local _x} || {typeOf _x isNotEqualTo "Land_Plank_01_4m_F"}}) < 0}
    && {count _rampSegments isEqualTo 9}
    && {(_rampSegments findIf {isNull _x || {local _x} || {typeOf _x isNotEqualTo "Land_Plank_01_4m_F"}}) < 0}
    && {!isNull (objectFromNetId (_advancedFixture param [3, ""]))}
    && {!isNull (objectFromNetId (_advancedFixture param [4, ""]))};
missionNamespace setVariable ["TRIBUNAL_BRIDGE_ADVANCED_ACK", [_token, _advancedReplication], true];
private _advancedResultDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_ADVANCED_RESULT"} || {diag_tickTime > _advancedResultDeadline}};
private _advancedResult = missionNamespace getVariable ["TRIBUNAL_BRIDGE_ADVANCED_RESULT", []];
["bridge.advanced.replication", _advancedReplication && {(_advancedResult param [0, ""]) isEqualTo _token} && {(_advancedResult param [1, false])}, format ["fixture=%1|segments=%2|result=%3", _advancedFixture, _advancedSegments apply {[netId _x, local _x, owner _x]}, _advancedResult]] call _assert;
private _rampTraversalOk = false;
private _rampStart = [];
private _rampEnd = [];
private _rampPeak = -1e9;
private _rampContacts = 0;
private _rampMaxLateral = 0;
private _rampTrajectory = [];
if (_advancedReplication && {count _rampSegments isEqualTo 9}) then {
    private _firstRamp = _rampSegments # 0;
    private _lastRamp = _rampSegments # 8;
    private _rampDir = vectorNormalized ([((getPosASL _lastRamp) # 0) - ((getPosASL _firstRamp) # 0), ((getPosASL _lastRamp) # 1) - ((getPosASL _firstRamp) # 1), 0]);
    private _rampRight = vectorNormalized ([0, 0, 1] vectorCrossProduct _rampDir);
    player setPosASL ((getPosASL _firstRamp) vectorAdd [0, 0, 0.75]);
    player setVectorDirAndUp [_rampDir, [0, 0, 1]];
    player enableSimulation true;
    _rampStart = getPosASL player;
    _rampPeak = _rampStart # 2;
    private _rampStartedAt = diag_tickTime;
    private _nextRampSample = diag_tickTime;
    private _rampForward = 0;
    waitUntil {
        private _velocity = velocity player;
        player setVelocity [(_rampDir # 0) * 3, (_rampDir # 1) * 3, _velocity # 2];
        private _position = getPosASL player;
        _rampPeak = _rampPeak max (_position # 2);
        private _delta = _position vectorDiff _rampStart;
        _rampForward = _delta vectorDotProduct _rampDir;
        _rampMaxLateral = _rampMaxLateral max abs (_delta vectorDotProduct _rampRight);
        private _hits = lineIntersectsSurfaces [_position vectorAdd [0, 0, 0.2], _position vectorAdd [0, 0, -1.5], player, objNull, true, 8, "GEOM", "NONE"];
        if ((_hits findIf {(_x # 2) in _rampSegments}) >= 0) then {_rampContacts = _rampContacts + 1};
        if (diag_tickTime >= _nextRampSample) then {
            _rampTrajectory pushBack [diag_tickTime - _rampStartedAt, _position, velocity player, _rampForward, count _hits];
            _nextRampSample = diag_tickTime + 0.5;
        };
        uiSleep 0.05;
        _rampForward > 29 || {diag_tickTime > (_rampStartedAt + 50)} || {!alive player}
    };
    _rampEnd = getPosASL player;
    private _rampDelta = _rampEnd vectorDiff _rampStart;
    private _rampForward = _rampDelta vectorDotProduct _rampDir;
    private _finalLateral = abs (_rampDelta vectorDotProduct _rampRight);
    _rampTraversalOk = alive player && {_rampForward > 28} && {_finalLateral < 0.7} && {_rampMaxLateral < 0.7} && {_rampContacts >= 100} && {(_rampPeak - (_rampStart # 2)) > 2.2} && {(_rampPeak - (_rampEnd # 2)) > 1.5};
};
missionNamespace setVariable ["TRIBUNAL_BRIDGE_RAMP_RESULT", [_token, _rampTraversalOk, _rampStart, _rampEnd, _rampPeak, _rampContacts, _rampMaxLateral, _rampTrajectory], true];
["bridge.ramp.traversal", _rampTraversalOk, format ["start=%1|end=%2|peak=%3|contacts=%4|maxLateral=%5|trajectory=%6", _rampStart, _rampEnd, _rampPeak, _rampContacts, _rampMaxLateral, _rampTrajectory]] call _assert;
private _cleanupDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_BRIDGE_CLEANUP"} || {diag_tickTime > _cleanupDeadline}};
private _cleanup = missionNamespace getVariable ["TRIBUNAL_BRIDGE_CLEANUP", []];
player enableSimulation true;
player setPosASL _originalASL;
player setDir _originalDir;
["bridge.cleanup.client", (_cleanup param [0, ""]) isEqualTo _token && {(_cleanup param [1, false]) isEqualTo true} && {isNull _box}, format ["cleanup=%1|boxNull=%2|restored=%3", _cleanup, isNull _box, getPosASL player]] call _assert;
''',
    metadata={
        "product": "field-utilities",
        "feature": "bridge-builder",
        "future_client_isolation": "client-b/JIP must observe server-owned segments and results without receiving client-a UI state",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="An eligible nearby player resolves the registered Bridge Builder ACE action; invoking that exact statement opens the dialog, whose handler builds a traversable replicated server-owned bridge and removes only that box's segments with bounded results and cleanup.",
        outcome="REWRITE BEFORE PERMANENT COVERAGE",
        rationale="Baseline construction referenced an absent class and mutated global objects on the requesting client; the scenario is permanent only after replacing that unusable path with a supported component and server-authoritative, box-scoped lifecycle.",
        dependencies=(
            "ACE 3.21 external interaction adapter",
            "Arma Apex plank component",
            "one independently authenticated client",
        ),
        evidence_types=frozenset({
            "ace-active-action-tree", "registered-action-statement", "client-ui-state", "server-authority",
            "exact-netid", "geometry", "physical-traversal", "replication", "cleanup",
        }),
        locality_requirements="Client-a owns ACE action resolution, UI state, and requests; the dedicated server exclusively creates/removes and tags segments. This proves one-client replication only, not client-b or JIP.",
    ),
)
