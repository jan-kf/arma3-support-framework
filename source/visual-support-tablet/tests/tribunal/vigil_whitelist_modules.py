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
        _object setDir 0;
        _object setFuel 0;
        _object engineOn false;
        _object setVelocity [0,0,0];
    };
} forEach [_assetA, _assetB, _assetC, _control];
uiSleep 3;
{
    if (!isNull _x) then {
        _x setVelocity [0,0,0];
        _x setAngularVelocity [0,0,0];
    };
} forEach [_assetA, _assetB, _assetC, _control];

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

private _playerDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; (count allPlayers) isEqualTo 1 || {diag_tickTime > _playerDeadline}};
private _curatorPlayer = allPlayers param [0, objNull];
private _curatorGroup = createGroup sideLogic;
private _curator = _curatorGroup createUnit ["ModuleCurator_F", [0,0,0], [], 0, "NONE"];
_curatorGroup setVariable ["isCuratorModuleGroup", true, true];
_curatorPlayer assignCurator _curator;
_curator addCuratorEditableObjects [[_assetC], true];
private _assignedDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator || {diag_tickTime > _assignedDeadline}};
["vigil.whitelist.curatorSetup", !isNull _curatorPlayer && {!isNull _curator} && {(getAssignedCuratorLogic _curatorPlayer) isEqualTo _curator} && {_assetC in curatorEditableObjects _curator}, format ["player=%1|curator=%2|assigned=%3|editable=%4", netId _curatorPlayer, netId _curator, netId (getAssignedCuratorLogic _curatorPlayer), _assetC in curatorEditableObjects _curator]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_SETUP", [_token, netId _assetA, netId _assetB, netId _assetC, netId _control, netId _curator, netId _curatorPlayer], true];
private _acceptedToggles = [];
for "_phase" from 1 to 1 do {
    missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_PHASE", _phase, true];
    private _toggleDeadline = diag_tickTime + 90;
    waitUntil {
        uiSleep 0.05;
        _acceptedToggles = (localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 3) isEqualTo "accepted"};
        (count _acceptedToggles) isEqualTo _phase || {diag_tickTime > _toggleDeadline}
    };
    private _members = +(missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []]);
    private _target = _assetC;
    private _expected = _expectedBase + [_assetC];
    private _transitionOk = (count _acceptedToggles) isEqualTo _phase
        && {[_members, _expected] call _sameObjects}
        && {(_acceptedToggles # (_phase - 1) # 4) isEqualTo netId _target}
        && {(_acceptedToggles # (_phase - 1) # 5) isEqualTo (_phase isEqualTo 1)};
    [format ["vigil.whitelist.zeusTransition%1", _phase], _transitionOk, format ["phase=%1|toggles=%2|members=%3", _phase, _acceptedToggles, _members apply {[vehicleVarName _x, netId _x]}]] call _assert;
};

private _claims = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
private _acceptedClaims = _claims select {_x # 4};
private _logicIds = _acceptedToggles apply {_x # 1};
private _authority = (count _acceptedClaims) isEqualTo 1
    && {(_acceptedClaims findIf {(_x # 2) isNotEqualTo netId _curator || {(_x # 3) <= 2}}) < 0}
    && {(_acceptedToggles apply {_x # 4}) isEqualTo [netId _assetC]};
["vigil.whitelist.zeusAuthority", _authority, format ["claims=%1|toggles=%2", _claims, _acceptedToggles]] call _assert;
private _logicDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_logicIds findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _logicDeadline}};
["vigil.whitelist.zeusCleanup", (count _logicIds) isEqualTo 1 && {(_logicIds findIf {!isNull objectFromNetId _x}) < 0}, format ["ids=%1", _logicIds]] call _assert;

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
    && {(count ((localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 3) isEqualTo "accepted"})) isEqualTo 1}
    && {[_finalMembers, _expectedBase + [_assetC]] call _sameObjects};
["vigil.whitelist.idempotence", _idempotent, format ["claims=%1|toggles=%2|members=%3", _finalClaims, localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []], _finalMembers apply {netId _x}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_RESULT", [_token, (_expectedBase + [_assetC]) apply {netId _x}, [netId _assetC], _logicIds, _acceptedClaims], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
private _all = [_assetA, _assetB, _assetC, _control] + _modules;
{if (!isNull _x) then {deleteVehicle _x;};} forEach _all;
deleteVehicle _curator; deleteGroup _curatorGroup;
localNamespace setVariable ["YSF_WHITELIST_EDEN_RECORDS", createHashMap];
localNamespace setVariable ["YSF_WHITELIST_MEMBERS", createHashMap];
missionNamespace setVariable ["YSF_WHITELIST_CONFIGURED", false, true];
missionNamespace setVariable ["YSF_WHITELISTED_ASSETS", [], true];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_all findIf {!isNull _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
["vigil.whitelist.cleanup", (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", ""]) isEqualTo _token && {(_all findIf {!isNull _x}) < 0} && {isNull _curator}, format ["client=%1|remaining=%2|curator=%3", missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", ""], _all select {!isNull _x}, isNull _curator]] call _assert;
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
private _clientCuratorReady = !isNull _curator && {(getAssignedCuratorLogic player) isEqualTo _curator} && {_assetC in curatorEditableObjects _curator};
["vigil.whitelist.clientAssigned", _clientCuratorReady, format ["player=%1|owner=%2|curator=%3|editable=%4|editableCount=%5", netId player, clientOwner, netId _curator, _assetC in curatorEditableObjects _curator, count curatorEditableObjects _curator]] call _assert;
private _initial = call YOSHI_getAllVehicles;
["vigil.whitelist.clientEdenSource", [_initial, _expectedBase] call _sameObjects && {!(_assetC in _initial)} && {!(_control in _initial)}, format ["source=%1", _initial apply {[vehicleVarName _x, netId _x]}]] call _assert;

diag_log "TRIBUNAL_VIGIL_WHITELIST_ZEUS|ARMED";
private _displayDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; !isNull findDisplay 312 || {diag_tickTime > _displayDeadline}};
private _display = findDisplay 312;
diag_log "TRIBUNAL_VIGIL_WHITELIST_ZEUS|DISPLAY_OPEN";
private _selectModule = {
    params ["_display"];
    ctrlActivate (_display displayCtrl 152); uiSleep 0.25;
    private _tree = _display displayCtrl 280; private _path = [];
    for "_i" from 0 to ((_tree tvCount []) - 1) do {
        if ((_tree tvText [_i]) isEqualTo "Add/Remove from Whitelist") exitWith {_path = [_i];};
        for "_j" from 0 to ((_tree tvCount [_i]) - 1) do {if ((_tree tvText [_i,_j]) isEqualTo "Add/Remove from Whitelist") exitWith {_path = [_i,_j];};};
        if (_path isNotEqualTo []) exitWith {};
    };
    if ((count _path) > 1) then {_tree tvSetCurSel [_path # 0]; uiSleep 0.1;};
    if (_path isNotEqualTo []) then {_tree tvSetCurSel _path;};
    _path
};
private _placements = [];
for "_phase" from 1 to 1 do {
    private _phaseDeadline = diag_tickTime + 120;
    waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_PHASE", 0]) isEqualTo _phase || {diag_tickTime > _phaseDeadline}};
    private _target = _assetC;
    private _path = [_display] call _selectModule;
    diag_log format ["TRIBUNAL_VIGIL_WHITELIST_ZEUS|SELECTION|%1|path=%2|target=%3|editable=%4|asl=%5|velocity=%6|angular=%7|grounded=%8|attached=%9", _phase, _path, netId _target, _target in curatorEditableObjects _curator, getPosASL _target, velocity _target, angularVelocity _target, isTouchingGround _target, attachedObjects _target];
    private _camPos = (getPosASL _target) vectorAdd [0,-30,20];
    private _camDir = vectorNormalized ((getPosASL _target) vectorDiff _camPos);
    private _right = vectorNormalized (_camDir vectorCrossProduct [0,0,1]);
    private _up = vectorNormalized (_right vectorCrossProduct _camDir);
    curatorCamera setPosASL _camPos; curatorCamera setVectorDirAndUp [_camDir, _up]; uiSleep 0.5;
    private _point = worldToScreen (_target modelToWorldVisual [0,0,1.5]);
    diag_log format ["TRIBUNAL_VIGIL_WHITELIST_ZEUS|PLACEMENT_READY|%1|%2", _phase, _point];
    private _hover = []; private _hoverDeadline = diag_tickTime + 15;
    waitUntil {uiSleep 0.02; _hover = curatorMouseOver; (toLowerANSI (_hover param [0, ""]) isEqualTo "object" && {(_hover param [1, objNull]) isEqualTo _target}) || {diag_tickTime > _hoverDeadline}};
    if (toLowerANSI (_hover param [0, ""]) isEqualTo "object" && {(_hover param [1, objNull]) isEqualTo _target}) then {diag_log format ["TRIBUNAL_VIGIL_WHITELIST_ZEUS|HOVER_READY|%1|target=%2|hover=%3", _phase, netId _target, _hover];} else {diag_log format ["TRIBUNAL_VIGIL_WHITELIST_ZEUS|HOVER_FAIL|%1|target=%2|hover=%3", _phase, netId _target, _hover];};
    private _before = count (uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []]);
    private _resultDeadline = diag_tickTime + 60;
    waitUntil {uiSleep 0.05; count (uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []]) > _before || {diag_tickTime > _resultDeadline}};
    private _rows = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []];
    private _row = _rows param [(count _rows) - 1, []];
    private _source = call YOSHI_getAllVehicles;
    private _expected = _expectedBase + [_assetC];
    _placements pushBack [_phase, _path, _point, _row, [_source, _expected] call _sameObjects];
    diag_log format ["TRIBUNAL_VIGIL_WHITELIST_ZEUS|PLACED|%1|%2", _phase, _row];
};
private _placementAudit = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_PLACEMENT_AUDIT", []];
private _native = (count _placements) isEqualTo 1 && {(count _placementAudit) isEqualTo 1}
    && {(_placements findIf {(_x # 1) isEqualTo [] || {(count (_x # 2)) isNotEqualTo 2} || {!((_x # 3) # 2)} || {!(_x # 4)}}) < 0}
    && {(_placements apply {_x # 3 # 4}) isEqualTo [netId _assetC]}
    && {(_placementAudit findIf {(_x # 2) isNotEqualTo "YSF_Toggle_To_Whitelist_Module" || {(_x # 5) isNotEqualTo clientOwner}}) < 0};
["vigil.whitelist.nativePlacements", _native, format ["placements=%1|audit=%2", _placements, _placementAudit]] call _assert;

private _negative = [];
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _negative = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_NEGATIVE", []]; (count _negative) isEqualTo 3 || {diag_tickTime > _negativeDeadline}};
[objNull, objNull, _negative param [1, ""]] remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2];
[player, objectFromNetId (_negative param [2, ""]), format ["%1-forged", _token]] remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2];
private _receiptDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; private _rows = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []]; (_rows findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 3) isEqualTo "duplicate"}}) >= 0 && {(_rows findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0} || {diag_tickTime > _receiptDeadline}};
private _results = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []];
private _acceptedResults = _results select {_x # 2};
private _feedback = (count _acceptedResults) isEqualTo 1
    && {(_acceptedResults apply {_x # 4}) isEqualTo [netId _assetC]}
    && {(_acceptedResults findIf {(_x # 6) isNotEqualTo clientOwner}) < 0}
    && {(_results findIf {(_x # 6) isNotEqualTo clientOwner}) < 0}
    && {(_results findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 3) isEqualTo "duplicate"}}) >= 0}
    && {(_results findIf {(_x # 0) isEqualTo format ["%1-forged", _token] && {(_x # 3) isEqualTo "predicate_logic_class"}}) >= 0};
["vigil.whitelist.feedbackAndNegatives", _feedback, format ["results=%1|owner=%2", _results, clientOwner]] call _assert;

private _result = []; private _resultDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_VIGIL_WHITELIST_RESULT", []]; (count _result) isEqualTo 5 || {diag_tickTime > _resultDeadline}};
private _replicated = (_result param [0, ""]) isEqualTo _token && {(_result param [1, []]) isEqualTo ((_expectedBase + [_assetC]) apply {netId _x})} && {(_result param [2, []]) isEqualTo [netId _assetC]} && {[(call YOSHI_getAllVehicles), _expectedBase + [_assetC]] call _sameObjects};
["vigil.whitelist.clientReplication", _replicated, format ["result=%1|source=%2", _result, (call YOSHI_getAllVehicles) apply {netId _x}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_WHITELIST_CLIENT_DONE", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-whitelist-modules",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.whitelist.edenAggregate", "vigil.whitelist.edenRetained",
        "vigil.whitelist.curatorSetup", "vigil.whitelist.zeusTransition1",
        "vigil.whitelist.zeusAuthority",
        "vigil.whitelist.zeusCleanup", "vigil.whitelist.idempotence",
        "vigil.whitelist.cleanup",
    }),
    client_expected=frozenset({
        "vigil.whitelist.clientAssigned", "vigil.whitelist.clientEdenSource",
        "vigil.whitelist.nativePlacements", "vigil.whitelist.feedbackAndNegatives",
        "vigil.whitelist.clientReplication",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "visual-support-tablet", "feature": "whitelist-modules",
        "visual_driver": "zeus-placement", "visual_armed_marker": "TRIBUNAL_VIGIL_WHITELIST_ZEUS|ARMED",
        "zeus_marker_prefix": "TRIBUNAL_VIGIL_WHITELIST_ZEUS", "zeus_placements": 1,
    },
    mission_entities=(
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_MODULE_A", "YSF_Asset_Whitelist_Module", "YSF_Tablet", "Logic", (3600, 0, 3600)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_MODULE_B", "YSF_Asset_Whitelist_Module", "YSF_Tablet", "Logic", (3620, 0, 3600)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_A", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4550, 16, 2785)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_B", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4575, 16, 2785)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_C", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4600, 16, 2785)),
        MissionEntity("TRIBUNAL_VIGIL_WHITELIST_CONTROL", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4625, 16, 2785)),
    ),
    mission_syncs=(
        MissionSync("TRIBUNAL_VIGIL_WHITELIST_MODULE_A", "TRIBUNAL_VIGIL_WHITELIST_A"),
        MissionSync("TRIBUNAL_VIGIL_WHITELIST_MODULE_B", "TRIBUNAL_VIGIL_WHITELIST_B"),
    ),
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Multiple authentic Eden whitelist modules aggregate exact synchronized assets; one assigned-curator placement adds one exact asset once, returns only to the placer, and rejects replay/forgery without another mutation.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The scenario proves configured dispatch, native Sync identity, retained logic, exact client discovery snapshots, authentic curator add causality, authority, idempotence, feedback, replication, and cleanup. Curator removal remains a separate engine-fixture experiment.",
        dependencies=("typed Eden module fixture", "authenticated curator input adapter", "accepted Vigil mixed-fleet browser", "one authenticated client"),
        evidence_types=frozenset({"configured-dispatch", "native-sync", "native-curator-placement", "exact-identity", "authoritative-state", "replication", "locality", "cleanup"}),
        locality_requirements="Eden registration and whitelist mutation are server-owned; the placing client owns transient curator modules and receives only its correlated result snapshots.",
    ),
)
