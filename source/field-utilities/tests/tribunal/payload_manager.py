"""Permanent server-authoritative Pontifex Payload Manager contract."""

from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-payload-manager",
    tier="gameplay",
    server_expected=frozenset({
        "payload.fixture",
        "payload.authority",
        "payload.cleanup",
    }),
    client_expected=frozenset({
        "payload.worldUi",
        "payload.themeBindings",
        "payload.apply",
        "payload.atomicRefusal",
        "payload.reorderOwnership",
    }),
    server_sqf=r'''
private _scenarioPlayer = objNull;
private _deadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _deadline}
};
private _origin = if (isNull _scenarioPlayer) then {[4720, 2820, 0]} else {getPosATL _scenarioPlayer};
private _uav = createVehicle ["B_UAV_01_F", _origin vectorAdd [2, 0, 0], [], 0, "CAN_COLLIDE"];
_uav setPosATL (_origin vectorAdd [2, 0, 0]);
_uav setFuel 0;
_uav engineOn false;
_uav allowDamage false;
_uav enableSimulationGlobal false;
private _uavId = netId _uav;
missionNamespace setVariable ["TRIBUNAL_PAYLOAD_FIXTURE", [_token, _uavId], true];
["payload.fixture", !isNull _scenarioPlayer && {!isNull _uav} && {local _uav} && {_uavId isNotEqualTo ""} && {[_uav] call YFU_fnc_payloadEligible}, format ["player=%1|uav=%2|local=%3|owner=%4|class=%5", netId _scenarioPlayer, _uavId, local _uav, owner _uav, typeOf _uav]] call _assert;

private _doneDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_PAYLOAD_DONE", ""]) isEqualTo _token
        || {diag_tickTime > _doneDeadline}
};
private _audit = localNamespace getVariable ["YFU_PAYLOAD_AUDIT", []];
private _ours = _audit select {(_x param [1, ""]) find "tribunal-payload-" isEqualTo 0};
private _accepted = _ours select {_x param [2, false]};
private _rejected = _ours select {!(_x param [2, false])};
private _state = [_uav] call YFU_fnc_payloadState;
private _classes = (_state # 1) apply {_x # 1};
private _authorityOk = (count _accepted) isEqualTo 2
    && {(count _rejected) isEqualTo 2}
    && {{(_x # 3) isEqualTo "capacity"} count _rejected isEqualTo 1}
    && {{(_x # 3) isEqualTo "stale"} count _rejected isEqualTo 1}
    && {(_state # 0) isEqualTo 2}
    && {_classes isEqualTo ["HandGrenade", "MiniGrenade", "HandGrenade"]};
["payload.authority", _authorityOk, format ["audit=%1|state=%2", _ours, _state]] call _assert;

deleteVehicle _uav;
missionNamespace setVariable ["TRIBUNAL_PAYLOAD_FIXTURE", nil, true];
private _cleanupDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; isNull (objectFromNetId _uavId) || {diag_tickTime > _cleanupDeadline}};
["payload.cleanup", (missionNamespace getVariable ["TRIBUNAL_PAYLOAD_DONE", ""]) isEqualTo _token && {isNull (objectFromNetId _uavId)}, format ["done=%1|remaining=%2", missionNamespace getVariable ["TRIBUNAL_PAYLOAD_DONE", ""], objectFromNetId _uavId]] call _assert;
''',
    client_sqf=r'''
disableSerialization;
private _fixture = [];
private _fixtureDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _fixture = missionNamespace getVariable ["TRIBUNAL_PAYLOAD_FIXTURE", []];
    (count _fixture) isEqualTo 2 || {diag_tickTime > _fixtureDeadline}
};
private _uavId = _fixture param [1, ""];
private _uav = objNull;
private _uavDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    _uav = objectFromNetId _uavId;
    !isNull _uav || {diag_tickTime > _uavDeadline}
};
private _originalLoadout = getUnitLoadout player;
private _originalColor = missionNamespace getVariable ["YFU_monochromeBaseColor", [0.15, 0.95, 0.15, 1]];
private _uniformBefore = { _x isEqualTo "HandGrenade" } count uniformItems player;
private _vestBefore = { _x isEqualTo "HandGrenade" } count vestItems player;
private _backpackBefore = { _x isEqualTo "MiniGrenade" } count backpackItems player;
private _satchelBefore = { _x isEqualTo "SatchelCharge_Remote_Mag" } count backpackItems player;
player addItemToUniform "HandGrenade";
uiSleep 2;
private _inventoryReady = ({_x isEqualTo "HandGrenade"} count uniformItems player) isEqualTo (_uniformBefore + 1)
    && {_vestBefore > 0}
    && {_backpackBefore > 0};
player setPosATL ((getPosATL _uav) vectorAdd [-2, 0, 0]);
missionNamespace setVariable ["YFU_monochromeBaseColor", [0.3, 0.4, 0.8, 1]];
[_uav] call YFU_fnc_payloadEnsureActionLocal;
private _actionLabels = (actionIDs _uav) apply {(_uav actionParams _x) param [0, ""]};
private _opened = [_uav] call YFU_fnc_payloadOpen;
private _display = displayNull;
private _displayDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    !isNull _display || {diag_tickTime > _displayDeadline}
};
private _uniformRows = 0;
private _vestRows = 0;
private _backpackRows = 0;
private _rowsDeadline = diag_tickTime + 3;
waitUntil {
    call YFU_fnc_payloadRefreshDialog;
    uiSleep 0.05;
    _uniformRows = if (isNull _display) then {0} else {lbSize (_display displayCtrl 98310)};
    _vestRows = if (isNull _display) then {0} else {lbSize (_display displayCtrl 98311)};
    _backpackRows = if (isNull _display) then {0} else {lbSize (_display displayCtrl 98312)};
    (_uniformRows > 0 && {_vestRows > 0} && {_backpackRows > 0}) || {diag_tickTime > _rowsDeadline}
};
["payload.worldUi", _inventoryReady && {_opened} && {!isNull _display} && {"Pontifex Payload Manager" in _actionLabels} && {_uniformRows > 0} && {_vestRows > 0} && {_backpackRows > 0}, format ["inventory=%1|opened=%2|actions=%3|rows=%4", _inventoryReady, _opened, _actionLabels, [_uniformRows, _vestRows, _backpackRows]]] call _assert;
private _actualTheme = if (isNull _display) then {[]} else {ctrlTextColor (_display displayCtrl 98310)};
private _nextEntry = ["Pontifex: Field Utilities", "nextPayload"] call CBA_fnc_getKeybind;
private _deployEntry = ["Pontifex: Field Utilities", "deployPayload"] call CBA_fnc_getKeybind;
private _nextText = ["nextPayload"] call YFU_fnc_payloadBindingText;
private _deployText = ["deployPayload"] call YFU_fnc_payloadBindingText;
private _bindingsOk = !isNil "_nextEntry" && {!isNil "_deployEntry"} && {_nextText isNotEqualTo ""} && {_deployText isNotEqualTo ""};
private _themeOk = (count _actualTheme) isEqualTo 4 && {abs ((_actualTheme # 0) - 0.3) < 0.01} && {abs ((_actualTheme # 1) - 0.4) < 0.01} && {abs ((_actualTheme # 2) - 0.8) < 0.01};
["payload.themeBindings", _themeOk && {_bindingsOk}, format ["theme=%1|next=%2|deploy=%3", _actualTheme, _nextText, _deployText]] call _assert;
if (!isNull _display) then {closeDialog 2;};

private _apply = "tribunal-payload-apply";
private _claims = [
    ["inventory", "uniform", "HandGrenade", _uniformBefore],
    ["inventory", "backpack", "MiniGrenade", 0],
    ["inventory", "vest", "HandGrenade", 0]
];
[_apply, _uav, 0, _claims] remoteExecCall ["YFU_fnc_payloadApplyServer", 2];
private _applyResult = [];
private _applyDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
    private _at = _rows findIf {(_x # 0) isEqualTo _apply};
    if (_at >= 0) then {_applyResult = _rows # _at;};
    _applyResult isNotEqualTo [] || {diag_tickTime > _applyDeadline}
};
private _state1 = [_uav] call YFU_fnc_payloadState;
private _state1Deadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; _state1 = [_uav] call YFU_fnc_payloadState; (_state1 # 0) >= 1 || {diag_tickTime > _state1Deadline}};
private _classes1 = (_state1 # 1) apply {_x # 1};
private _inventoryDebited = ({ _x isEqualTo "HandGrenade" } count uniformItems player) isEqualTo _uniformBefore
    && {({_x isEqualTo "HandGrenade"} count vestItems player) isEqualTo (_vestBefore - 1)}
    && {({_x isEqualTo "MiniGrenade"} count backpackItems player) isEqualTo (_backpackBefore - 1)};
["payload.apply", (_applyResult param [1, false]) && {(_applyResult param [2, ""]) isEqualTo "applied"} && {_inventoryDebited} && {(_state1 # 0) isEqualTo 1} && {_classes1 isEqualTo ["HandGrenade", "MiniGrenade", "HandGrenade"]}, format ["result=%1|state=%2|inventory=%3", _applyResult, _state1, [_uniformBefore, _vestBefore, _backpackBefore, uniformItems player, vestItems player, backpackItems player]]] call _assert;

private _inventoryBeforeRefusal = getUnitLoadout player;
private _installedClaims = (_state1 # 1) apply {["installed", _x # 0]};
private _over = "tribunal-payload-over-capacity";
private _overClaims = +_installedClaims;
_overClaims pushBack ["inventory", "backpack", "SatchelCharge_Remote_Mag", _satchelBefore];
[_over, _uav, 1, _overClaims] remoteExecCall ["YFU_fnc_payloadApplyServer", 2];
private _overResult = [];
private _overDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
    private _at = _rows findIf {(_x # 0) isEqualTo _over};
    if (_at >= 0) then {_overResult = _rows # _at;};
    _overResult isNotEqualTo [] || {diag_tickTime > _overDeadline}
};
private _stale = "tribunal-payload-stale";
[_stale, _uav, 0, _installedClaims] remoteExecCall ["YFU_fnc_payloadApplyServer", 2];
private _staleResult = [];
private _staleDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
    private _at = _rows findIf {(_x # 0) isEqualTo _stale};
    if (_at >= 0) then {_staleResult = _rows # _at;};
    _staleResult isNotEqualTo [] || {diag_tickTime > _staleDeadline}
};
private _stateAfterRejects = [_uav] call YFU_fnc_payloadState;
private _inventoryUnchanged = (getUnitLoadout player) isEqualTo _inventoryBeforeRefusal;
["payload.atomicRefusal", _inventoryUnchanged && {!(_overResult param [1, true])} && {(_overResult param [2, ""]) isEqualTo "capacity"} && {!(_staleResult param [1, true])} && {(_staleResult param [2, ""]) isEqualTo "stale"} && {_stateAfterRejects isEqualTo _state1}, format ["over=%1|stale=%2|stateBefore=%3|stateAfter=%4|inventoryUnchanged=%5", _overResult, _staleResult, _state1, _stateAfterRejects, _inventoryUnchanged]] call _assert;

private _reorder = "tribunal-payload-reorder";
private _reverseClaims = +_installedClaims;
reverse _reverseClaims;
[_reorder, _uav, 1, _reverseClaims] remoteExecCall ["YFU_fnc_payloadApplyServer", 2];
private _reorderResult = [];
private _reorderDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
    private _at = _rows findIf {(_x # 0) isEqualTo _reorder};
    if (_at >= 0) then {_reorderResult = _rows # _at;};
    _reorderResult isNotEqualTo [] || {diag_tickTime > _reorderDeadline}
};
private _state2 = [_uav] call YFU_fnc_payloadState;
private _state2Deadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; _state2 = [_uav] call YFU_fnc_payloadState; (_state2 # 0) >= 2 || {diag_tickTime > _state2Deadline}};
private _ids1 = (_state1 # 1) apply {_x # 0};
private _ids2 = (_state2 # 1) apply {_x # 0};
private _expectedIds = +_ids1;
reverse _expectedIds;
["payload.reorderOwnership", (_reorderResult param [1, false]) && {(_state2 # 0) isEqualTo 2} && {_ids2 isEqualTo _expectedIds} && {_inventoryUnchanged} && {_inventoryDebited}, format ["result=%1|before=%2|after=%3|inventoryUnchanged=%4", _reorderResult, _ids1, _ids2, _inventoryUnchanged]] call _assert;

player setUnitLoadout _originalLoadout;
missionNamespace setVariable ["YFU_monochromeBaseColor", _originalColor];
missionNamespace setVariable ["TRIBUNAL_PAYLOAD_DONE", _token, true];
''',
    metadata={
        "product": "field-utilities",
        "feature": "payload-manager-authoritative-loadout",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A nearby authenticated client opens the native themed Payload Manager on an eligible small UAV, observes separate real inventory sources, atomically transfers an ordered loadout within eight capacity units, receives explicit over-capacity and stale refusals without inventory or UAV mutation, and may reorder but not reclaim installed UAV-owned entries.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The transaction and ownership boundaries are deliberate product semantics; the scenario uses exact inventory counts, payload IDs/revisions, requester receipts, server audit and cleanup rather than treating UI presence as effect proof.",
        dependencies=("one independently authenticated client", "server-local B_UAV_01_F fixture", "CBA keybinding and Field Utilities theme settings"),
        evidence_types=frozenset({"exact-netid", "server-audit", "requester-receipt", "inventory-delta", "atomic-negative-control", "ui-control-state", "cleanup"}),
        locality_requirements="The dedicated server owns the UAV and authority boundary; client-a owns its inventory/UI and independently observes replicated UAV state. Positive in-control deployment and client-B/JIP are excluded.",
    ),
)
