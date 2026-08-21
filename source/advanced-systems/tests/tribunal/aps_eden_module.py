"""Authentic typed-Eden activation coverage for LORICA APS."""

from tribunal.mission.projectiles import direct_fixture_sqf
from tribunal.runner.model import MissionEntity, MissionSync, Scenario, ScenarioReview


SERVER_SQF = direct_fixture_sqf() + r"""
private _targetA = missionNamespace getVariable ["TRIBUNAL_APS_EDEN_TARGET_A", objNull];
private _targetB = missionNamespace getVariable ["TRIBUNAL_APS_EDEN_TARGET_B", objNull];
private _control = missionNamespace getVariable ["TRIBUNAL_APS_EDEN_CONTROL", objNull];
private _targets = [_targetA, _targetB, _control];
private _modules = [];
{if (!isNull _x) then {_x setFuel 0; _x engineOn false; _x allowDamage true; _x setDamage 0;};} forEach _targets;
uiSleep 3;
{if (!isNull _x) then {_x setVelocity [0, 0, 0];};} forEach _targets;

private _auditDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (count (localNamespace getVariable ["YAS_APS_MODULE_DISPATCH_AUDIT", []])) >= 3 || {diag_tickTime > _auditDeadline}};
private _audit = localNamespace getVariable ["YAS_APS_MODULE_DISPATCH_AUDIT", []];
private _clientStimulus = missionNamespace getVariable ["TRIBUNAL_APS_EDEN_CLIENT_STIMULUS", []];
private _serverRows = _audit select {_x param [9, false]};
private _rejectedRows = _audit select {!(_x param [9, false])};
private _syncSets = _serverRows apply {(_x param [8, []]) apply {_x param [1, ""]}};
private _rowA = _serverRows select {((_x # 8) param [0, []]) param [1, ""] isEqualTo "TRIBUNAL_APS_EDEN_TARGET_A"};
private _rowB = _serverRows select {((_x # 8) param [0, []]) param [1, ""] isEqualTo "TRIBUNAL_APS_EDEN_TARGET_B"};
private _moduleA = if ((count _rowA) isEqualTo 1) then {objectFromNetId ((_rowA # 0) # 2)} else {objNull};
private _moduleB = if ((count _rowB) isEqualTo 1) then {objectFromNetId ((_rowB # 0) # 2)} else {objNull};
_modules = [_moduleA, _moduleB];
private _dispatchOk = (count _serverRows) isEqualTo 2
    && {(_serverRows findIf {(_x # 0) isNotEqualTo "YAS_APS_Module" || {!(_x # 4)} || {!(_x # 5)} || {(_x # 6) isNotEqualTo 2} || {(_x # 7) isNotEqualTo 0} || {(_x # 10) isNotEqualTo "accepted"}}) < 0}
    && ({_x isEqualTo "TRIBUNAL_APS_EDEN_TARGET_A"} count (_syncSets apply {_x param [0, ""]})) isEqualTo 1
    && ({_x isEqualTo "TRIBUNAL_APS_EDEN_TARGET_B"} count (_syncSets apply {_x param [0, ""]})) isEqualTo 1;
["aps.module.dispatch", _dispatchOk, format ["audit=%1|serverRows=%2|sync=%3", _audit, _serverRows, _syncSets]] call _assert;
private _authorityOk = (count _rejectedRows) isEqualTo 1
    && {(count _clientStimulus) isEqualTo 3}
    && {(_clientStimulus # 0) isEqualTo _token}
    && {(_rejectedRows # 0) # 0 isNotEqualTo "YAS_APS_Module"}
    && {((_rejectedRows # 0) # 2) isEqualTo (_clientStimulus # 1)}
    && {((_rejectedRows # 0) # 6) isEqualTo (_clientStimulus # 2)}
    && {((_rejectedRows # 0) # 7) isEqualTo (_clientStimulus # 2)}
    && {((_rejectedRows # 0) # 10) isEqualTo "wrong_class"};
["aps.module.authority", _authorityOk, format ["stimulus=%1|rejected=%2", _clientStimulus, _rejectedRows]] call _assert;
private _retainedOk = (_modules findIf {isNull _x || {typeOf _x isNotEqualTo "YAS_APS_Module"} || {!local _x} || {owner _x isNotEqualTo 2}}) < 0
    && {(synchronizedObjects _moduleA) isEqualTo [_targetA]}
    && {(synchronizedObjects _moduleB) isEqualTo [_targetB]};
["aps.module.retained", _retainedOk, format ["modules=%1|sync=%2", _modules apply {[vehicleVarName _x, typeOf _x, local _x, owner _x]}, _modules apply {(synchronizedObjects _x) apply {vehicleVarName _x}}]] call _assert;

private _targetsOk = (_targets findIf {isNull _x || {!alive _x} || {!local _x} || {(netId _x) isEqualTo ""}}) < 0
    && {_targetA getVariable ["YOSHI_APS_Installed", false]}
    && {_targetB getVariable ["YOSHI_APS_Installed", false]}
    && {!(_control getVariable ["YOSHI_APS_Installed", false])};
["aps.module.targets", _targetsOk, format ["ids=%1|alive=%2|installed=%3|locality=%4", _targets apply {netId _x}, _targets apply {alive _x}, _targets apply {_x getVariable ["YOSHI_APS_Installed", false]}, _targets apply {[local _x, owner _x]}]] call _assert;
["aps.module.multiple", _targetsOk && {([_targetA] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo YOSHI_APS_DEFAULT_HARDKILL_CHARGES} && {([_targetB] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo YOSHI_APS_DEFAULT_HARDKILL_CHARGES}, format ["charges=%1", [_targets apply {[_x] call YOSHI_fnc_apsHardKillChargeCount}]]] call _assert;

missionNamespace setVariable ["YOSHI_APS_EngagementEvents", [], true];
private _fire = {
    params ["_target", "_label", "_expectIntercept"];
    _target setVehiclePosition [[3000, 4200, 0], [], 0, "NONE"];
    _target setDir 0;
    _target setVelocity [0, 0, 0];
    _target setAngularVelocity [0, 0, 0];
    uiSleep 3;
    _target setVelocity [0, 0, 0];
    _target setAngularVelocity [0, 0, 0];
    private _settledASL = getPosASL _target;
    uiSleep 0.1;
    private _targetASL = getPosASL _target;
    private _targetVelocity = velocity _target;
    private _targetAngularVelocity = angularVelocity _target;
    private _grounded = isTouchingGround _target;
    private _stable = _grounded
        && {(_settledASL distance _targetASL) <= 0.25}
        && {(vectorMagnitude _targetVelocity) <= 0.5}
        && {(vectorMagnitude _targetAngularVelocity) <= 0.5};
    private _aimASL = AGLToASL (_target modelToWorldVisual (getCenterOfMass _target));
    private _origin = _aimASL vectorAdd [90, 0, 0];
    private _direction = vectorNormalized (_aimASL vectorDiff _origin);
    private _pathHits = lineIntersectsSurfaces [_origin, _aimASL, objNull, objNull, true, 64, "FIRE", "GEOM"];
    private _pathValid = _pathHits isNotEqualTo [] && {((_pathHits # 0) # 2) isEqualTo _target};
    private _impactKey = format ["TRIBUNAL_APS_EDEN_HIT_%1", _label];
    private _damageKey = format ["TRIBUNAL_APS_EDEN_DAMAGE_%1", _label];
    missionNamespace setVariable [_damageKey, []];
    private _damageHandler = _target addEventHandler ["HandleDamage", compile format ["private _events = missionNamespace getVariable ['%1', []]; _events pushBack [diag_tickTime, _this # 1, _this # 2, _this # 4]; missionNamespace setVariable ['%1', _events]; _this # 2", _damageKey]];
    private _damageBefore = damage _target;
    private _beforeCharges = [_target] call YOSHI_fnc_apsHardKillChargeCount;
    private _launch = ["R_PG32V_F", _origin, _direction, 250, _label, _target, 0] call TRIBUNAL_fnc_directProjectileLaunch;
    private _projectile = _launch # 0;
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
        _event isNotEqualTo [] || {missionNamespace getVariable [_impactKey, false]} || {diag_tickTime > _deadline}
    };
    private _impact = missionNamespace getVariable [_impactKey, false];
    private _terminated = isNull _projectile;
    private _damageEvents = missionNamespace getVariable [_damageKey, []];
    private _damageAfter = damage _target;
    _target removeEventHandler ["HandleDamage", _damageHandler];
    private _afterCharges = [_target] call YOSHI_fnc_apsHardKillChargeCount;
    private _collisionBounds = boundingBoxReal _target;
    private _collisionRadius = (((_collisionBounds # 0) distance (_collisionBounds # 1)) * 0.5) + 0.5;
    private _exactDamage = (_damageEvents findIf {(_x # 3) in ["R_PG32V_F", "ammo_Penetrator_RPG32V"]}) >= 0;
    private _physicalImpact = _terminated && {_closest <= _collisionRadius} && {_exactDamage} && {_damageAfter >= (_damageBefore + 0.05)};
    private _protected = !_impact && {_damageEvents isEqualTo []} && {abs (_damageAfter - _damageBefore) <= 0.01};
    private _ok = !isNull _target && {alive _target} && {_stable} && {_pathValid} && {_uid isNotEqualTo ""} && {_launch # 2} && {_tracked}
        && {if (_expectIntercept) then {_event isNotEqualTo [] && {isNull _projectile} && {_protected} && {_afterCharges isEqualTo (_beforeCharges - 1)}} else {_physicalImpact && {_event isEqualTo []} && {_afterCharges isEqualTo _beforeCharges}}};
    [_ok, _uid, _impact, _event, _beforeCharges, _afterCharges, _launch # 3, _targetASL, getPosASL _target, _targetVelocity, velocity _target, _targetAngularVelocity, _grounded, _stable, _aimASL, _origin, _pathValid, _pathHits apply {[_x # 0, typeOf (_x # 2), netId (_x # 2)]}, _terminated, _closest, _lastProjectileASL, _damageBefore, _damageAfter, _damageEvents, _collisionRadius, _exactDamage, _physicalImpact, _protected]
};
private _positiveA = [_targetA, "eden-a", true] call _fire;
_targetA setPosATL [3300, 4000, 0]; uiSleep 1;
private _positiveB = [_targetB, "eden-b", true] call _fire;
_targetB setPosATL [3300, 4200, 0]; uiSleep 1;
private _controlResult = [_control, "eden-control", false] call _fire;
["aps.module.intercepts", (_positiveA # 0) && {(_positiveB # 0)}, format ["a=%1|b=%2", _positiveA, _positiveB]] call _assert;
["aps.module.unsyncedImpact", _controlResult # 0, format ["control=%1", _controlResult]] call _assert;
["aps.module.locality", (_targets findIf {!local _x || {owner _x isNotEqualTo 2}}) < 0 && {(_serverRows findIf {!(_x # 4) || {!(_x # 5)} || {(_x # 6) isNotEqualTo 2}}) < 0}, format ["targets=%1|dispatch=%2", _targets apply {[netId _x, local _x, owner _x]}, _serverRows]] call _assert;

missionNamespace setVariable ["TRIBUNAL_APS_EDEN_RESULT", [_token, _targets apply {netId _x}, [_positiveA # 1, _positiveB # 1], _serverRows], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_APS_EDEN_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
private _ids = _targets apply {netId _x};
{if (!isNull _x) then {deleteVehicle _x;};} forEach (_targets + _modules);
private _cleanupDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; (_ids findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
["aps.module.cleanup", (missionNamespace getVariable ["TRIBUNAL_APS_EDEN_CLIENT_DONE", ""]) isEqualTo _token && {(_ids findIf {!isNull objectFromNetId _x}) < 0} && {(_modules findIf {!isNull _x}) < 0}, format ["ids=%1|remaining=%2|modulesNull=%3", _ids, _ids select {!isNull objectFromNetId _x}, _modules apply {isNull _x}]] call _assert;
"""

CLIENT_SQF = r"""
private _stimulusOk = !isNull player && {(netId player) isNotEqualTo ""} && {clientOwner > 2};
private _clientStimulus = [_token, netId player, clientOwner];
missionNamespace setVariable ["TRIBUNAL_APS_EDEN_CLIENT_STIMULUS", _clientStimulus, true];
[player] remoteExecCall ["YAS_fnc_apsModuleEnable", 2];
["aps.module.clientAuthorityStimulus", _stimulusOk, format ["player=%1|owner=%2|clientOwner=%3", netId player, owner player, clientOwner]] call _assert;
private _result = [];
private _deadline = diag_tickTime + 180;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_APS_EDEN_RESULT", []]; (count _result) isEqualTo 4 || {diag_tickTime > _deadline}};
private _ids = _result param [1, []];
private _vehicles = _ids apply {objectFromNetId _x};
private _resolveDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (_vehicles findIf {isNull _x}) < 0 || {diag_tickTime > _resolveDeadline}};
private _projectiles = _result param [2, []];
private _events = [];
private _eventDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; _events = missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]; (_projectiles findIf {_uid = _x; (_events findIf {(_x param [1, ""]) isEqualTo _uid && {(_x param [2, ""]) isEqualTo "hardkill"}}) < 0}) < 0 || {diag_tickTime > _eventDeadline}};
private _dispatch = _result param [3, []];
private _rowA = _dispatch select {((_x # 8) param [0, []]) param [1, ""] isEqualTo "TRIBUNAL_APS_EDEN_TARGET_A"};
private _rowB = _dispatch select {((_x # 8) param [0, []]) param [1, ""] isEqualTo "TRIBUNAL_APS_EDEN_TARGET_B"};
private _moduleA = if ((count _rowA) isEqualTo 1) then {objectFromNetId ((_rowA # 0) # 2)} else {objNull};
private _moduleB = if ((count _rowB) isEqualTo 1) then {objectFromNetId ((_rowB # 0) # 2)} else {objNull};
private _moduleSync = [synchronizedObjects _moduleA, synchronizedObjects _moduleB];
private _replicated = (_result param [0, ""]) isEqualTo _token
    && {(count _vehicles) isEqualTo 3}
    && {(_vehicles findIf {isNull _x}) < 0}
    && {(_vehicles # 0) getVariable ["YOSHI_APS_Installed", false]}
    && {(_vehicles # 1) getVariable ["YOSHI_APS_Installed", false]}
    && {!((_vehicles # 2) getVariable ["YOSHI_APS_Installed", false])}
    && {!isNull _moduleA} && {!isNull _moduleB}
    && {(_moduleSync # 0) isEqualTo [(_vehicles # 0)]} && {(_moduleSync # 1) isEqualTo [(_vehicles # 1)]}
    && {(_projectiles findIf {_uid = _x; (_events findIf {(_x param [1, ""]) isEqualTo _uid && {(_x param [2, ""]) isEqualTo "hardkill"}}) < 0}) < 0};
["aps.module.clientReplication", _replicated, format ["ids=%1|resolved=%2|installed=%3|projectiles=%4|events=%5", _ids, _vehicles apply {!isNull _x}, _vehicles apply {_x getVariable ["YOSHI_APS_Installed", false]}, _projectiles, _events]] call _assert;
missionNamespace setVariable ["TRIBUNAL_APS_EDEN_CLIENT_DONE", _token, true];
"""


TRIBUNAL_SCENARIO = Scenario(
    identifier="advsys-aps-eden-module",
    tier="gameplay",
    server_expected=frozenset({
        "aps.module.dispatch", "aps.module.authority", "aps.module.retained",
        "aps.module.targets", "aps.module.multiple",
        "aps.module.intercepts", "aps.module.unsyncedImpact", "aps.module.locality",
        "aps.module.cleanup",
    }),
    client_expected=frozenset({"aps.module.clientAuthorityStimulus", "aps.module.clientReplication"}),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "advanced-systems", "feature": "aps-eden-module"},
    mission_entities=(
        MissionEntity("TRIBUNAL_APS_EDEN_MODULE_A", "YAS_APS_Module", "YAS_AdvSys", "Logic", (2980, 0, 4000)),
        MissionEntity("TRIBUNAL_APS_EDEN_MODULE_B", "YAS_APS_Module", "YAS_AdvSys", "Logic", (2980, 0, 4200)),
        MissionEntity("TRIBUNAL_APS_EDEN_TARGET_A", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4600, 16, 2778)),
        MissionEntity("TRIBUNAL_APS_EDEN_TARGET_B", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4600, 16, 2800)),
        MissionEntity("TRIBUNAL_APS_EDEN_CONTROL", "O_MBT_02_cannon_F", "A3_Armor_F_Beta", "Object", (4600, 16, 2822)),
    ),
    mission_syncs=(
        MissionSync("TRIBUNAL_APS_EDEN_MODULE_A", "TRIBUNAL_APS_EDEN_TARGET_A"),
        MissionSync("TRIBUNAL_APS_EDEN_MODULE_B", "TRIBUNAL_APS_EDEN_TARGET_B"),
    ),
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Authentic typed Eden APS modules aggregate idempotently over exact synchronized vehicles; each becomes physically protected while an unsynchronized same-class control remains unprotected.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="Fresh autonomous proof validates authentic native Eden dispatch, aggregate Sync behavior, forged-client rejection, exact physical interception/impact causality, replication, and cleanup.",
        dependencies=("typed Eden module fixture", "Tribunal direct-projectile fixture", "one authenticated client"),
        evidence_types=frozenset({"configured-dispatch", "native-sync", "trajectory", "impact", "authoritative-state", "replication", "locality", "cleanup"}),
        locality_requirements="Native module dispatch and APS mutation must be server-local; client-a observes exact target and engagement replication.",
    ),
)
