"""Authentic curator activation coverage for LORICA APS."""

from tribunal.mission.projectiles import direct_fixture_sqf
from tribunal.runner.model import MissionEntity, Scenario, ScenarioReview


SERVER_SQF = direct_fixture_sqf() + r'''
private _targetControl = missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_CONTROL", objNull];
private _targetOn = missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_TARGET_ON", objNull];
private _targets = [_targetControl, _targetOn];
{
    if (!isNull _x) then {
        _x setFuel 0;
        _x engineOn false;
        _x allowDamage true;
        _x setDamage 0;
    };
} forEach _targets;
uiSleep 3;
{if (!isNull _x) then {_x setVelocity [0,0,0]; _x setAngularVelocity [0,0,0];};} forEach _targets;
private _playerDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; (count allPlayers) isEqualTo 1 || {diag_tickTime > _playerDeadline}};
private _curatorPlayer = allPlayers param [0, objNull];
private _curatorGroup = createGroup sideLogic;
private _curator = _curatorGroup createUnit ["ModuleCurator_F", [0,0,0], [], 0, "NONE"];
_curatorGroup setVariable ["isCuratorModuleGroup", true, true];
_curatorPlayer assignCurator _curator;
_curator addCuratorEditableObjects [[_targetOn], true];
private _installOn = [_targetOn] call YOSHI_fnc_apsEnableVehicle;
private _suspendOn = [_targetOn] call YOSHI_fnc_apsDisableVehicle;
private _setupOk = (_targets findIf {isNull _x}) < 0 && {!isNull _curatorPlayer} && {!isNull _curator}
    && {_installOn} && {_suspendOn}
    && {!(_targetControl getVariable ["YOSHI_APS_Installed", false])}
    && {!(_targetOn getVariable ["YOSHI_APS_Enabled", true])}
    && {_targetOn in (curatorEditableObjects _curator)};
["aps.zeus.setup", _setupOk, format ["control=%1|target=%2|player=%3|curator=%4|editable=%5|installed=%6|enabled=%7|locality=%8", netId _targetControl, netId _targetOn, netId _curatorPlayer, netId _curator, _targetOn in (curatorEditableObjects _curator), _targets apply {_x getVariable ["YOSHI_APS_Installed", false]}, _targets apply {_x getVariable ["YOSHI_APS_Enabled", false]}, _targets apply {[local _x, owner _x]}]] call _assert;

private _fire = {
    params ["_target", "_label", "_expectIntercept"];
    _target setVehiclePosition [[3000, 4200, 0], [], 0, "NONE"];
    _target setDir 0;
    _target setVelocity [0,0,0];
    _target setAngularVelocity [0,0,0];
    uiSleep 3;
    private _settledASL = getPosASL _target;
    private _targetVelocity = velocity _target;
    private _targetAngularVelocity = angularVelocity _target;
    private _grounded = isTouchingGround _target;
    private _stable = _grounded && {(vectorMagnitude _targetVelocity) <= 0.5} && {(vectorMagnitude _targetAngularVelocity) <= 0.5};
    private _aimASL = AGLToASL (_target modelToWorldVisual (getCenterOfMass _target));
    private _origin = _aimASL vectorAdd [90,0,0];
    private _direction = vectorNormalized (_aimASL vectorDiff _origin);
    private _pathHits = lineIntersectsSurfaces [_origin, _aimASL, objNull, objNull, true, 64, "FIRE", "GEOM"];
    private _pathValid = _pathHits isNotEqualTo [] && {((_pathHits # 0) # 2) isEqualTo _target};
    private _damageKey = format ["TRIBUNAL_APS_ZEUS_DAMAGE_%1", _label];
    missionNamespace setVariable [_damageKey, []];
    private _damageHandler = _target addEventHandler ["HandleDamage", compile format ["private _events = missionNamespace getVariable ['%1', []]; _events pushBack [diag_tickTime, _this # 1, _this # 2, _this # 4]; missionNamespace setVariable ['%1', _events]; _this # 2", _damageKey]];
    private _damageBefore = damage _target;
    private _beforeCharges = [_target] call YOSHI_fnc_apsHardKillChargeCount;
    private _eventsBefore = +(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]);
    private _launch = ["R_PG32V_F", _origin, _direction, 250, _label, _target, 0] call TRIBUNAL_fnc_directProjectileLaunch;
    private _projectile = _launch # 0;
    private _hitKey = _launch # 1;
    private _uid = if (isNull _projectile) then {""} else {[_projectile] call YOSHI_fnc_apsProjectileUid};
    private _tracked = !isNull _projectile && {[_projectile] call YOSHI_fnc_apsTrackProjectileLocal};
    private _event = [];
    private _closest = 1e9;
    private _lastProjectileASL = [];
    private _deadline = diag_tickTime + 4;
    waitUntil {
        uiSleep 0.005;
        if (!isNull _projectile) then {_lastProjectileASL = getPosASL _projectile; _closest = _closest min (_projectile distance _target);};
        private _matches = (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) select {
            (_x param [0, ""]) isEqualTo netId _target && {(_x param [1, ""]) isEqualTo _uid} && {(_x param [2, ""]) isEqualTo "hardkill"}
        };
        if ((count _matches) isEqualTo 1) then {_event = _matches # 0;};
        _event isNotEqualTo [] || {missionNamespace getVariable [_hitKey, false]} || {diag_tickTime > _deadline}
    };
    private _hitPart = missionNamespace getVariable [_hitKey, false];
    private _terminated = isNull _projectile;
    private _damageEvents = missionNamespace getVariable [_damageKey, []];
    private _damageAfter = damage _target;
    _target removeEventHandler ["HandleDamage", _damageHandler];
    private _afterCharges = [_target] call YOSHI_fnc_apsHardKillChargeCount;
    private _collisionBounds = boundingBoxReal _target;
    private _collisionRadius = (((_collisionBounds # 0) distance (_collisionBounds # 1)) * 0.5) + 0.5;
    private _exactDamage = (_damageEvents findIf {(_x # 3) in ["R_PG32V_F", "ammo_Penetrator_RPG32V"]}) >= 0;
    private _physicalImpact = _terminated && {_hitPart} && {_closest <= _collisionRadius} && {_exactDamage} && {_damageAfter >= (_damageBefore + 0.05)};
    private _protected = !_hitPart && {_damageEvents isEqualTo []} && {abs (_damageAfter - _damageBefore) <= 0.01};
    private _ok = _stable && {_pathValid} && {_uid isNotEqualTo ""} && {_launch # 2} && {_tracked}
        && {if (_expectIntercept) then {_event isNotEqualTo [] && {_terminated} && {_protected} && {_afterCharges isEqualTo (_beforeCharges - 1)}} else {_physicalImpact && {_event isEqualTo []} && {_afterCharges isEqualTo _beforeCharges}}};
    [_ok, _uid, _hitPart, _event, _beforeCharges, _afterCharges, _launch # 3, _settledASL, _targetVelocity, _targetAngularVelocity, _grounded, _pathValid, _terminated, _closest, _lastProjectileASL, _damageBefore, _damageAfter, _damageEvents, _collisionRadius, _exactDamage, _physicalImpact, _protected, (count _eventsBefore), count (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []])]
};

private _off = [_targetControl, "zeus-disabled-control", false] call _fire;
["aps.zeus.offImpact", _off # 0, format ["result=%1", _off]] call _assert;
deleteVehicle _targetControl;
uiSleep 0.25;
missionNamespace setVariable ["TRIBUNAL_APS_ZEUS_SETUP", [_token, netId _targetOn, netId _curator, netId _curatorPlayer], true];
missionNamespace setVariable ["TRIBUNAL_APS_ZEUS_PHASE", 1, true];

private _onDeadline = diag_tickTime + 90;
private _onAudit = [];
waitUntil {
    uiSleep 0.05;
    _onAudit = (localNamespace getVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", []]) select {(_x # 4) isEqualTo "accepted" && {_x # 5}};
    (count _onAudit) isEqualTo 1 || {diag_tickTime > _onDeadline}
};
private _onState = _targetOn getVariable ["YOSHI_APS_Enabled", false];
["aps.zeus.onTransition", (count _onAudit) isEqualTo 1 && {_onState}, format ["audit=%1|enabled=%2", _onAudit, _onState]] call _assert;
private _on = [_targetOn, "zeus-on", true] call _fire;
["aps.zeus.onIntercept", _on # 0, format ["result=%1", _on]] call _assert;

private _claims = localNamespace getVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", []];
private _toggles = localNamespace getVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", []];
private _acceptedClaims = _claims select {_x # 5};
private _logicIds = _toggles select {(_x # 4) isEqualTo "accepted"} apply {_x # 1};
private _acceptedOwner = (_acceptedClaims param [0, []]) param [4, -1];
private _expectedTargetIds = [netId _targetOn];
private _claimTargetIds = _acceptedClaims apply {_x # 2};
private _authorityOk = (count _acceptedClaims) isEqualTo 1
    && {_acceptedOwner > 2}
    && {(_acceptedClaims findIf {(_x # 4) isNotEqualTo _acceptedOwner}) < 0}
    && {(_acceptedClaims findIf {(_x # 3) isNotEqualTo netId _curator}) < 0}
    && {(count (_claimTargetIds arrayIntersect _expectedTargetIds)) isEqualTo 1};
["aps.zeus.authority", _authorityOk, format ["claims=%1|toggles=%2", _claims, _toggles]] call _assert;
private _cleanupLogicDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_logicIds findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupLogicDeadline}};
["aps.zeus.logicCleanup", (count _logicIds) isEqualTo 1 && {(_logicIds findIf {!isNull objectFromNetId _x}) < 0}, format ["ids=%1|live=%2", _logicIds, _logicIds select {!isNull objectFromNetId _x}]] call _assert;

private _acceptedClaim = _acceptedClaims param [0, []];
private _replayOperation = _acceptedClaim param [0, ""];
missionNamespace setVariable ["TRIBUNAL_APS_ZEUS_NEGATIVE", [_token, _replayOperation, netId _targetOn, netId _curator], true];
unassignCurator _curator;
private _negativeDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _rows = localNamespace getVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", []];
    (_rows findIf {(_x # 0) isEqualTo _replayOperation && {(_x # 6) isEqualTo "duplicate"}}) >= 0
        && {(_rows findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 6) isEqualTo "predicate_logic_class"}}) >= 0}
        || {diag_tickTime > _negativeDeadline}
};
private _finalClaims = localNamespace getVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", []];
private _duplicateRows = _finalClaims select {(_x # 0) isEqualTo _replayOperation && {(_x # 6) isEqualTo "duplicate"}};
private _unauthorizedRows = _finalClaims select {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 6) isEqualTo "predicate_logic_class"}};
private _finalToggles = localNamespace getVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", []];
private _idempotent = (count _duplicateRows) isEqualTo 1 && {(count _unauthorizedRows) isEqualTo 1}
    && {(count (_finalToggles select {(_x # 4) isEqualTo "accepted"})) isEqualTo 1}
    && {_targetOn getVariable ["YOSHI_APS_Enabled", false]}
    && {([_targetOn] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo (_on # 5)};
["aps.zeus.idempotence", _idempotent, format ["replay=%1|unauthorized=%2|toggles=%3|state=%4|charges=%5", _duplicateRows, _unauthorizedRows, _finalToggles, [_targetOn] call YOSHI_fnc_apsStateSnapshot, [_targetOn] call YOSHI_fnc_apsHardKillChargeCount]] call _assert;

missionNamespace setVariable ["TRIBUNAL_APS_ZEUS_RESULT", [_token, _expectedTargetIds, netId _curator, _off # 1, _on # 1, _acceptedClaims, _logicIds, _on # 3], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
private _targetIds = _targets apply {netId _x};
{deleteVehicle _x;} forEach _targets;
deleteVehicle _curator;
deleteGroup _curatorGroup;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_targetIds findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
["aps.zeus.cleanup", (missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_CLIENT_DONE", ""]) isEqualTo _token && {(_targetIds findIf {!isNull objectFromNetId _x}) < 0}, format ["clientDone=%1|targets=%2", missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_CLIENT_DONE", ""], _targetIds apply {objectFromNetId _x}]] call _assert;
'''


CLIENT_SQF = r'''
private _setup = [];
private _setupDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; _setup = missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_SETUP", []]; (count _setup) isEqualTo 4 || {diag_tickTime > _setupDeadline}};
private _targets = [objectFromNetId (_setup param [1, ""])];
private _targetId = _setup param [1, ""];
private _curator = objectFromNetId (_setup param [2, ""]);
private _assignedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (getAssignedCuratorLogic player) isEqualTo _curator || {diag_tickTime > _assignedDeadline}};
private _assigned = !isNull _curator && {(getAssignedCuratorLogic player) isEqualTo _curator};
["aps.zeus.clientAssigned", _assigned && {!isNull (_targets # 0)}, format ["player=%1|owner=%2|curator=%3|assigned=%4|target=%5|clientEditableMirror=%6", netId player, clientOwner, netId _curator, netId (getAssignedCuratorLogic player), netId (_targets # 0), (_targets # 0) in (curatorEditableObjects _curator)]] call _assert;

diag_log "TRIBUNAL_APS_ZEUS|ARMED";
private _displayDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; !isNull findDisplay 312 || {diag_tickTime > _displayDeadline}};
private _display = findDisplay 312;
diag_log "TRIBUNAL_APS_ZEUS|DISPLAY_OPEN";
private _selectModule = {
    params ["_display"];
    ctrlActivate (_display displayCtrl 152);
    uiSleep 0.25;
    private _tree = _display displayCtrl 280;
    private _path = [];
    for "_i" from 0 to ((_tree tvCount []) - 1) do {
        if ((_tree tvText [_i]) isEqualTo "Toggle Active Protection System (APS)") exitWith {_path = [_i];};
        for "_j" from 0 to ((_tree tvCount [_i]) - 1) do {
            if ((_tree tvText [_i, _j]) isEqualTo "Toggle Active Protection System (APS)") exitWith {_path = [_i, _j];};
        };
        if (_path isNotEqualTo []) exitWith {};
    };
    if (_path isNotEqualTo []) then {
        if ((count _path) > 1) then {
            _tree tvSetCurSel [_path # 0];
            uiSleep 0.1;
        };
        _tree tvSetCurSel _path;
    };
    [_path, ctrlShown _tree]
};
private _placements = [];
for "_phase" from 1 to 1 do {
    private _phaseDeadline = diag_tickTime + 120;
    waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_PHASE", 0]) isEqualTo _phase || {diag_tickTime > _phaseDeadline}};
    private _target = _targets # (_phase - 1);
    private _selection = [_display] call _selectModule;
    private _camPos = (getPosASL _target) vectorAdd [0,-30,20];
    private _camDir = vectorNormalized ((getPosASL _target) vectorDiff _camPos);
    private _right = vectorNormalized (_camDir vectorCrossProduct [0,0,1]);
    private _up = vectorNormalized (_right vectorCrossProduct _camDir);
    curatorCamera setPosASL _camPos;
    curatorCamera setVectorDirAndUp [_camDir, _up];
    uiSleep 0.5;
    private _point = worldToScreen (_target modelToWorldVisual [0,0,1.5]);
    diag_log format ["TRIBUNAL_APS_ZEUS|PLACEMENT_READY|%1|%2", _phase, _point];
    private _hoverDeadline = diag_tickTime + 15;
    private _hover = [];
    waitUntil {
        uiSleep 0.02;
        _hover = curatorMouseOver;
        (toLowerANSI (_hover param [0, ""]) isEqualTo "object" && {(_hover param [1, objNull]) isEqualTo _target}) || {diag_tickTime > _hoverDeadline}
    };
    private _hoverOk = toLowerANSI (_hover param [0, ""]) isEqualTo "object" && {(_hover param [1, objNull]) isEqualTo _target};
    if (_hoverOk) then {
        diag_log format ["TRIBUNAL_APS_ZEUS|HOVER_READY|%1|target=%2|hover=%3", _phase, netId _target, _hover];
    } else {
        diag_log format ["TRIBUNAL_APS_ZEUS|HOVER_FAIL|%1|target=%2|hover=%3", _phase, netId _target, _hover];
    };
    private _resultDeadline = diag_tickTime + 60;
    private _resultsBefore = +(uiNamespace getVariable ["YAS_APS_ZEUS_RESULTS", []]);
    waitUntil {
        uiSleep 0.05;
        (count (uiNamespace getVariable ["YAS_APS_ZEUS_RESULTS", []])) > (count _resultsBefore)
            || {diag_tickTime > _resultDeadline}
    };
    private _results = uiNamespace getVariable ["YAS_APS_ZEUS_RESULTS", []];
    private _row = _results param [(count _results) - 1, []];
    private _placementAudit = uiNamespace getVariable ["YAS_APS_ZEUS_CLIENT_PLACEMENT_AUDIT", []];
    _placements pushBack [_phase, _selection, _point, _row, _placementAudit param [(count _placementAudit) - 1, []]];
    diag_log format ["TRIBUNAL_APS_ZEUS|PLACED|%1|%2", _phase, _row];
};
private _placementOk = (count _placements) isEqualTo 1
    && {(_placements findIf {(_x # 1 # 0) isEqualTo [] || {!(_x # 1 # 1)} || {(count (_x # 2)) isNotEqualTo 2} || {!((_x # 3) param [3, false])} || {((_x # 3) param [6, -1]) isNotEqualTo clientOwner} || {!((_x # 4) param [5, false])}}) < 0}
    && {(_placements # 0 # 3) # 5}
    && {((_placements # 0 # 3) param [2, ""]) isEqualTo netId (_targets # 0)};
["aps.zeus.nativePlacement", _placementOk, format ["placements=%1", _placements]] call _assert;

private _negative = [];
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _negative = missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_NEGATIVE", []]; (count _negative) isEqualTo 4 || {diag_tickTime > _negativeDeadline}};
[objNull, objNull, objNull, _negative param [1, ""]] remoteExecCall ["YAS_fnc_apsZeusClaimServer", 2];
[player, objectFromNetId (_negative param [2, ""]), objectFromNetId (_negative param [3, ""]), format ["%1-unauthorized", _token]] remoteExecCall ["YAS_fnc_apsZeusClaimServer", 2];
private _negativeResultDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _rows = uiNamespace getVariable ["YAS_APS_ZEUS_RESULTS", []];
    (_rows findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 4) isEqualTo "duplicate"}}) >= 0
        && {(_rows findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 4) isEqualTo "predicate_logic_class"}}) >= 0}
        || {diag_tickTime > _negativeResultDeadline}
};
private _resultRows = uiNamespace getVariable ["YAS_APS_ZEUS_RESULTS", []];
private _acceptedResults = _resultRows select {_x # 3};
private _rejectedResults = _resultRows select {!(_x # 3)};
private _feedbackOk = (count _acceptedResults) isEqualTo 1
    && {(count _rejectedResults) isEqualTo 2}
    && {(count (((_acceptedResults apply {_x # 2}) arrayIntersect [_targetId]))) isEqualTo 1}
    && {(_acceptedResults findIf {(_x # 6) isNotEqualTo clientOwner}) < 0}
    && {(_rejectedResults findIf {(_x # 6) isNotEqualTo clientOwner}) < 0};
["aps.zeus.feedback", _feedbackOk, format ["targetedResults=%1|clientOwner=%2", _resultRows, clientOwner]] call _assert;
private _negativeOk = (_resultRows findIf {(_x # 0) isEqualTo (_negative param [1, ""]) && {(_x # 4) isEqualTo "duplicate"}}) >= 0
    && {(_resultRows findIf {(_x # 0) isEqualTo format ["%1-unauthorized", _token] && {(_x # 4) isEqualTo "predicate_logic_class"}}) >= 0};
["aps.zeus.clientNegativeReceipts", _negativeOk, format ["results=%1", _resultRows]] call _assert;

private _result = [];
private _resultDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_APS_ZEUS_RESULT", []]; (count _result) isEqualTo 8 || {diag_tickTime > _resultDeadline}};
private _events = missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []];
private _onUid = _result param [4, ""];
private _replicated = (_result param [0, ""]) isEqualTo _token
    && {(_result param [1, []]) isEqualTo [_targetId]}
    && {_onUid isNotEqualTo ""}
    && {(_events findIf {(_x param [0, ""]) isEqualTo _targetId && {(_x param [1, ""]) isEqualTo _onUid} && {(_x param [2, ""]) isEqualTo "hardkill"}}) >= 0};
["aps.zeus.clientReplication", _replicated, format ["result=%1|events=%2|target=%3", _result, _events, _targetId]] call _assert;

missionNamespace setVariable ["TRIBUNAL_APS_ZEUS_CLIENT_DONE", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="advsys-aps-zeus-module",
    tier="gameplay",
    server_expected=frozenset({
        "aps.zeus.setup", "aps.zeus.offImpact",
        "aps.zeus.onTransition", "aps.zeus.onIntercept", "aps.zeus.authority",
        "aps.zeus.logicCleanup", "aps.zeus.idempotence", "aps.zeus.cleanup",
    }),
    client_expected=frozenset({
        "aps.zeus.clientAssigned", "aps.zeus.nativePlacement", "aps.zeus.feedback",
        "aps.zeus.clientNegativeReceipts", "aps.zeus.clientReplication",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "advanced-systems",
        "feature": "aps-zeus-module",
        "visual_driver": "zeus-placement",
        "visual_armed_marker": "TRIBUNAL_APS_ZEUS|ARMED",
        "zeus_placements": 1,
    },
    mission_entities=(
        MissionEntity("TRIBUNAL_APS_ZEUS_CONTROL", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4615, 16, 2785)),
        MissionEntity("TRIBUNAL_APS_ZEUS_TARGET_ON", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4600, 16, 2785)),
    ),
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="An assigned curator's authentic Zeus module placement toggles exactly its selected APS vehicle once, returns feedback only to that curator, and rejects replay or unauthenticated stimuli without state drift.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The narrow scenario causally proves a disabled same-threat impact, native curator activation and exact interception, authenticated one-time claim consumption, targeted feedback, negative receipts, replication, and cleanup.",
        dependencies=("authenticated curator input adapter", "Tribunal direct-projectile fixture", "one authenticated client"),
        evidence_types=frozenset({"native-curator-placement", "trajectory", "impact", "authoritative-state", "replication", "locality", "cleanup"}),
        locality_requirements="The placing client owns the native curator module; the server authenticates its assigned curator claim and owns the APS mutation; client-a observes the exact result and event.",
    ),
)
