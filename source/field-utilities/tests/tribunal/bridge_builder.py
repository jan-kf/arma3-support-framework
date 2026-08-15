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
waitUntil {uiSleep 0.05; !isNull (call YFU_bridge_getDialogDisplay) || {diag_tickTime > _dialogDeadline}};
disableSerialization;
private _display = call YFU_bridge_getDialogDisplay;
private _page = if (isNull _display) then {controlNull} else {_display displayCtrl 98210};
private _buildControl = if (isNull _display) then {controlNull} else {_display displayCtrl 98261};
private _dialogOk = !isNull _display && {(ctrlIDD _display) isEqualTo 98200} && {!isNull _page} && {!isNull _buildControl} && {ctrlEnabled _buildControl};
["bridge.dialog.open", _dialogOk, format ["display=%1|idd=%2|page=%3|build=%4|enabled=%5", !isNull _display, if (isNull _display) then {-1} else {ctrlIDD _display}, !isNull _page, !isNull _buildControl, if (isNull _buildControl) then {false} else {ctrlEnabled _buildControl}]] call _assert;

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
