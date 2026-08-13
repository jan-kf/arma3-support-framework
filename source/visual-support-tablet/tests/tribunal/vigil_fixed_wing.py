"""Physical Tier 3 contract for Vigil fixed-wing strike support."""

from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.mission.combat import combat_observer_sqf
from tribunal.mission.designation import designation_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-fixed-wing",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.fixedWing.registration.snapshot",
        "vigil.fixedWing.registration.originalRemoved",
        "vigil.fixedWing.dispatch.reconstructed",
        "vigil.fixedWing.dispatch.ingress",
        "vigil.fixedWing.locality",
        "vigil.fixedWing.designation.normal",
        "vigil.fixedWing.strike.normal.release",
        "vigil.fixedWing.strike.normal.guidance",
        "vigil.fixedWing.strike.normal.effect",
        "vigil.fixedWing.designation.ir",
        "vigil.fixedWing.strike.ir.release",
        "vigil.fixedWing.strike.ir.guidance",
        "vigil.fixedWing.strike.ir.effect",
        "vigil.fixedWing.strike.repeated",
        "vigil.fixedWing.control.noDesignation",
        "vigil.fixedWing.egress.flight",
        "vigil.fixedWing.egress.cleanup",
        "vigil.fixedWing.cleanup",
    }),
    client_expected=frozenset({
        "vigil.fixedWing.client.registry",
        "vigil.fixedWing.client.deploy",
        "vigil.fixedWing.client.locality",
        "vigil.fixedWing.client.normalDesignation",
        "vigil.fixedWing.client.normalRequest",
        "vigil.fixedWing.client.normalResult",
        "vigil.fixedWing.client.irDesignation",
        "vigil.fixedWing.client.irRequest",
        "vigil.fixedWing.client.irResult",
        "vigil.fixedWing.client.designationCleanup",
        "vigil.fixedWing.client.noDesignation",
        "vigil.fixedWing.client.rtb",
    }),
    server_sqf=designation_observer_sqf() + aviation_observer_sqf() + combat_observer_sqf() + r'''
private _assetId = format ["FW_TRIBUNAL_%1", _token];
private _combatToken = format ["%1-fixed-wing", _token];
private _scenarioPlayer = allPlayers param [0, objNull];
private _operating = if (isNull _scenarioPlayer) then {[3200, 5600, 0]} else {getPosASL _scenarioPlayer};
private _infilDelta = if ((_operating # 0) < (worldSize / 2)) then {2200} else {-2200};
private _infil = [(((_operating # 0) + _infilDelta) max 500) min (worldSize - 500), _operating # 1, 900];
private _exfil = [500, 1000, 900];
private _source = "B_Plane_CAS_01_dynamicLoadout_F" createVehicle [1500, 5400, 0];
_source setDir 125;
_source setFuel 0.73;
_source setDamage 0.04;
createVehicleCrew _source;
{_x setSkill 1} forEach crew _source;
{
    _source setPylonLoadout [_x # 0, "", true, _x # 2];
} forEach (getAllPylonsInfo _source);
{
    _source setPylonLoadout [_x, "PylonMissile_1Rnd_Bomb_04_F", true, [-1]];
    _source setAmmoOnPylon [_x, 1];
} forEach [4, 5, 6];
_source setVariable ["YSF_FW_ID", _assetId, true];
private _sourceId = netId _source;
private _sourceCrewIds = crew _source apply {netId _x};
private _sourceTextures = getObjectTextures _source;
private _sourcePylons = [_source] call YOSHI_GET_PYLON_INFO;
private _registered = [_source, _infil, _exfil, "SABER"] call YSF_fwRegisterAsset;
private _entry = [_assetId] call YSF_fwGetEntry;
private _snapshot = _entry getOrDefault ["snapshot", []];
private _snapshotPylons = _snapshot param [3, []];
private _bombRows = _snapshotPylons select {(_x param [1, ""]) isEqualTo "PylonMissile_1Rnd_Bomb_04_F"};
private _snapshotChecks = [
    _registered,
    typeName _entry isEqualTo "HASHMAP",
    (_snapshot param [0, ""]) isEqualTo "B_Plane_CAS_01_dynamicLoadout_F",
    abs ((_snapshot param [2, -1]) - 0.73) < 0.001,
    abs (((_snapshot param [4, []]) param [0, -1]) - 0.04) < 0.001,
    (_snapshot param [1, []]) isEqualTo _sourceTextures,
    count _bombRows isEqualTo 3,
    (count (_bombRows select {(_x param [3, -1]) isEqualTo 1})) isEqualTo 3,
    (_entry getOrDefault ["callsign", ""]) isEqualTo "SABER",
    abs ((_entry getOrDefault ["heading", -1]) - 125) < 0.01,
    (_entry getOrDefault ["roleMask", 0]) isEqualTo YSF_FW_ROLE_STRIKE
];
private _snapshotOk = (_snapshotChecks findIf {!_x}) < 0;
["vigil.fixedWing.registration.snapshot", _snapshotOk, format ["checks=%1|asset=%2|class=%3|fuel=%4|damage=%5|bombs=%6|textures=%7:%8|callsign=%9|heading=%10|role=%11", _snapshotChecks, _assetId, _snapshot param [0, ""], _snapshot param [2, -1], (_snapshot param [4, []]) param [0, -1], _bombRows, _snapshot param [1, []], _sourceTextures, _entry getOrDefault ["callsign", ""], _entry getOrDefault ["heading", -1], _entry getOrDefault ["roleMask", -1]]] call _assert;
private _deleteDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.01; isNull _source || diag_tickTime > _deleteDeadline};
private _originalRemoved = isNull _source && {(_sourceCrewIds findIf {!isNull (objectFromNetId _x)}) < 0};
["vigil.fixedWing.registration.originalRemoved", _originalRemoved, format ["source=%1|crew=%2|sourceNull=%3", _sourceId, _sourceCrewIds, isNull _source]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_FIXTURE", [_token, _assetId, _infil, _operating, _exfil], true];

private _deployDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    _entry = [_assetId] call YSF_fwGetEntry;
    !isNull (_entry getOrDefault ["spawnedVeh", objNull]) || diag_tickTime > _deployDeadline
};
private _aircraft = _entry getOrDefault ["spawnedVeh", objNull];
private _aircraftId = if (isNull _aircraft) then {""} else {netId _aircraft};
private _pilot = if (isNull _aircraft) then {objNull} else {effectiveCommander _aircraft};
private _spawnPosition = if (isNull _aircraft) then {[]} else {getPosASL _aircraft};
private _spawnHeading = if (isNull _aircraft) then {-1} else {getDir _aircraft};
private _spawnSpeed = if (isNull _aircraft) then {-1} else {vectorMagnitude velocity _aircraft};
private _reconstructedPylons = if (isNull _aircraft) then {[]} else {[_aircraft] call YOSHI_GET_PYLON_INFO};
private _reconstructedBombs = _reconstructedPylons select {(_x param [1, ""]) isEqualTo "PylonMissile_1Rnd_Bomb_04_F"};
private _reconstructed = !isNull _aircraft && {alive _aircraft} && {!isNull _pilot}
    && {typeOf _aircraft isEqualTo "B_Plane_CAS_01_dynamicLoadout_F"}
    && {abs (fuel _aircraft - 0.73) < 0.03} && {abs (damage _aircraft - 0.04) < 0.01}
    && {getObjectTextures _aircraft isEqualTo _sourceTextures}
    && {count _reconstructedBombs isEqualTo 3}
    && {{(_x param [3, -1]) isEqualTo 1} count _reconstructedBombs isEqualTo 3};
["vigil.fixedWing.dispatch.reconstructed", _reconstructed, format ["aircraft=%1|class=%2|crew=%3|fuel=%4|damage=%5|pylons=%6|spawn=%7|heading=%8|speed=%9", _aircraftId, typeOf _aircraft, count crew _aircraft, fuel _aircraft, damage _aircraft, _reconstructedBombs, _spawnPosition, _spawnHeading, _spawnSpeed]] call _assert;
private _localityOk = isServer && {local _aircraft} && {local _pilot} && {local group _pilot};
["vigil.fixedWing.locality", _localityOk, format ["server=%1|aircraft=%2/%3|pilot=%4/%5|groupLocal=%6", isServer, local _aircraft, owner _aircraft, local _pilot, owner _pilot, local group _pilot]] call _assert;

[_combatToken] call TRIBUNAL_fnc_combatObserverStart;
[_combatToken, _aircraft] call TRIBUNAL_fnc_combatObserveSource;
private _ingressSamples = [_aircraft, _operating, {
    false
}, 15, 0.25] call TRIBUNAL_fnc_observeFlight;
private _ingressEvidence = [_ingressSamples, _spawnPosition, _operating] call TRIBUNAL_fnc_flightEvidence;
private _headingError = abs (((_spawnHeading - 90) + 540) mod 360 - 180);
private _loiterCenter = _aircraft getVariable ["YSF_FW_LOITER_CENTER_ASL", []];
private _ingressOk = (_spawnPosition distance2D _infil) < 25
    && {_spawnSpeed > 100}
    && {(_ingressEvidence getOrDefault ["maximumTravel", 0]) > 300}
    && {(_ingressEvidence getOrDefault ["groundSamples", 1]) isEqualTo 0}
    && {(count _loiterCenter) >= 3 && {_loiterCenter distance2D _operating < 1}}
    && {count waypoints (group _aircraft) > 0}
    && {alive _aircraft};
["vigil.fixedWing.dispatch.ingress", _ingressOk, format ["spawn=%1|infil=%2|heading=%3|headingError=%4|speed=%5|samples=%6|minDistance=%7|maxTravel=%8|ground=%9|loiter=%10|waypoints=%11", _spawnPosition, _infil, _spawnHeading, _headingError, _spawnSpeed, _ingressEvidence getOrDefault ["samples", 0], _ingressEvidence getOrDefault ["minimumDistance", -1], _ingressEvidence getOrDefault ["maximumTravel", -1], _ingressEvidence getOrDefault ["groundSamples", -1], _loiterCenter, count waypoints (group _aircraft)]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_DEPLOYED", [_token, _assetId, _aircraftId], true];

private _normalReadyDeadline = diag_tickTime + 90;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_NORMAL_READY"} || diag_tickTime > _normalReadyDeadline};
private _normalReady = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_NORMAL_READY", []];
private _normalLaserId = _normalReady param [1, ""];
private _normalLaser = objNull;
private _normalResolveDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.02;
    _normalLaser = if (_normalLaserId isEqualTo "") then {objNull} else {objectFromNetId _normalLaserId};
    !isNull _normalLaser || diag_tickTime > _normalResolveDeadline
};
private _normalDesignation = [allPlayers param [0, objNull], _normalLaser, "laser-designator"] call TRIBUNAL_fnc_designationRecord;
private _normalPos = _normalDesignation getOrDefault ["positionASL", []];
private _normalTarget = objNull;
if ((count _normalPos) >= 3) then {
    _normalTarget = createVehicle ["O_MRAP_02_F", ASLToATL _normalPos, [], 0, "NONE"];
    _normalTarget setFuel 0;
    _normalTarget setDamage 0;
    [_combatToken, _normalTarget] call TRIBUNAL_fnc_combatObserveTarget;
};
private _normalTargetId = netId _normalTarget;
private _normalDesignationOk = (_normalReady param [0, ""]) isEqualTo _token
    && {_normalLaserId isNotEqualTo ""} && {!isNull _normalLaser}
    && {!local _normalLaser} && {owner _normalLaser isEqualTo owner (allPlayers # 0)}
    && {(_normalDesignation getOrDefault ["designationClass", ""]) isKindOf "LaserTarget"};
["vigil.fixedWing.designation.normal", _normalDesignationOk, format ["ready=%1|snapshot=%2|target=%3|targetPos=%4", _normalReady, _normalDesignation, _normalTargetId, getPosASL _normalTarget]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_NORMAL_TARGET", [_token, _normalTargetId], true];

private _normalFireDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.05;
    count (([_combatToken] call TRIBUNAL_fnc_combatObserverState) getOrDefault ["fires", []]) >= 1
        || diag_tickTime > _normalFireDeadline
};
private _normalImpactDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.05;
    private _state = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
    count ((_state getOrDefault ["hitDetails", []]) select {(_x getOrDefault ["target", ""]) isEqualTo _normalTargetId}) > 0
        || diag_tickTime > _normalImpactDeadline
};
private _normalCombat = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _normalFires = (_normalCombat getOrDefault ["fires", []]) select {(_x getOrDefault ["source", ""]) isEqualTo _aircraftId};
private _normalEvent = _normalFires param [0, createHashMap];
private _normalProjectileId = _normalEvent getOrDefault ["projectile", ""];
private _normalSamples = _normalEvent getOrDefault ["samples", []];
private _normalHits = (_normalCombat getOrDefault ["hitDetails", []]) select {
    (_x getOrDefault ["target", ""]) isEqualTo _normalTargetId
    && {(_x getOrDefault ["projectile", ""]) isEqualTo _normalProjectileId}
};
private _normalMin = 1e9;
private _normalTargetPos = getPosASL _normalTarget;
{_normalMin = _normalMin min ((_x # 1) distance _normalTargetPos)} forEach _normalSamples;
private _normalReleaseOk = _normalProjectileId isNotEqualTo ""
    && {(_normalEvent getOrDefault ["weapon", ""]) isEqualTo "Bomb_04_Plane_CAS_01_F"}
    && {(_normalEvent getOrDefault ["ammo", ""]) isEqualTo "Bomb_04_F"}
    && {_normalEvent getOrDefault ["sourceLocal", false]}
    && {_normalEvent getOrDefault ["projectileLocal", false]};
["vigil.fixedWing.strike.normal.release", _normalReleaseOk, format ["aircraft=%1|designation=%2|event=%3", _aircraftId, _normalLaserId, _normalEvent]] call _assert;
private _normalGuidanceOk = count _normalSamples > 10 && {_normalMin < 20}
    && {getNumber (configFile >> "CfgAmmo" >> "Bomb_04_F" >> "laserLock") > 0};
["vigil.fixedWing.strike.normal.guidance", _normalGuidanceOk, format ["projectile=%1|samples=%2|minDistance=%3|laserLock=%4|designation=%5", _normalProjectileId, count _normalSamples, _normalMin, getNumber (configFile >> "CfgAmmo" >> "Bomb_04_F" >> "laserLock"), _normalLaserId]] call _assert;
private _normalEffectOk = count _normalHits > 0 && {damage _normalTarget > 0};
["vigil.fixedWing.strike.normal.effect", _normalEffectOk, format ["projectile=%1|target=%2|hits=%3|damage=%4", _normalProjectileId, _normalTargetId, _normalHits, damage _normalTarget]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_NORMAL_DONE", [_token, _normalProjectileId, _normalTargetId], true];

private _irReadyDeadline = diag_tickTime + 90;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_IR_READY"} || diag_tickTime > _irReadyDeadline};
private _irReady = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_IR_READY", []];
private _irLaserId = _irReady param [1, ""];
private _irLaser = objNull;
private _irResolveDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.02;
    _irLaser = if (_irLaserId isEqualTo "") then {objNull} else {objectFromNetId _irLaserId};
    !isNull _irLaser || diag_tickTime > _irResolveDeadline
};
private _irDesignation = [allPlayers param [0, objNull], _irLaser, "weapon-ir-helper"] call TRIBUNAL_fnc_designationRecord;
private _irPos = _irDesignation getOrDefault ["positionASL", []];
private _irTarget = objNull;
if ((count _irPos) >= 3) then {
    _irTarget = createVehicle ["O_MRAP_02_F", ASLToATL _irPos, [], 0, "NONE"];
    _irTarget setFuel 0;
    _irTarget setDamage 0;
    [_combatToken, _irTarget] call TRIBUNAL_fnc_combatObserveTarget;
};
private _irTargetId = netId _irTarget;
private _irDesignationOk = (_irReady param [0, ""]) isEqualTo _token
    && {_irLaserId isNotEqualTo ""} && {!isNull _irLaser}
    && {!local _irLaser} && {owner _irLaser isEqualTo owner (allPlayers # 0)}
    && {(_irDesignation getOrDefault ["designationClass", ""]) isKindOf "LaserTarget"};
["vigil.fixedWing.designation.ir", _irDesignationOk, format ["ready=%1|snapshot=%2|target=%3|targetPos=%4", _irReady, _irDesignation, _irTargetId, getPosASL _irTarget]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_IR_TARGET", [_token, _irTargetId], true];

private _irFireDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.05;
    count (([_combatToken] call TRIBUNAL_fnc_combatObserverState) getOrDefault ["fires", []]) >= 2
        || diag_tickTime > _irFireDeadline
};
private _irImpactDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.05;
    private _state = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
    count ((_state getOrDefault ["hitDetails", []]) select {(_x getOrDefault ["target", ""]) isEqualTo _irTargetId}) > 0
        || diag_tickTime > _irImpactDeadline
};
private _irCombat = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _allFires = (_irCombat getOrDefault ["fires", []]) select {(_x getOrDefault ["source", ""]) isEqualTo _aircraftId};
private _irEvent = _allFires param [1, createHashMap];
private _irProjectileId = _irEvent getOrDefault ["projectile", ""];
private _irSamples = _irEvent getOrDefault ["samples", []];
private _irHits = (_irCombat getOrDefault ["hitDetails", []]) select {
    (_x getOrDefault ["target", ""]) isEqualTo _irTargetId
    && {(_x getOrDefault ["projectile", ""]) isEqualTo _irProjectileId}
};
private _irMin = 1e9;
private _irTargetPos = getPosASL _irTarget;
{_irMin = _irMin min ((_x # 1) distance _irTargetPos)} forEach _irSamples;
private _irReleaseOk = _irProjectileId isNotEqualTo ""
    && {(_irEvent getOrDefault ["weapon", ""]) isEqualTo "Bomb_04_Plane_CAS_01_F"}
    && {(_irEvent getOrDefault ["ammo", ""]) isEqualTo "Bomb_04_F"}
    && {_irEvent getOrDefault ["projectileLocal", false]};
["vigil.fixedWing.strike.ir.release", _irReleaseOk, format ["aircraft=%1|designation=%2|event=%3", _aircraftId, _irLaserId, _irEvent]] call _assert;
private _irGuidanceOk = count _irSamples > 10 && {_irMin < 20};
["vigil.fixedWing.strike.ir.guidance", _irGuidanceOk, format ["projectile=%1|samples=%2|minDistance=%3|designation=%4", _irProjectileId, count _irSamples, _irMin, _irLaserId]] call _assert;
private _irEffectOk = count _irHits > 0 && {damage _irTarget > 0};
["vigil.fixedWing.strike.ir.effect", _irEffectOk, format ["projectile=%1|target=%2|hits=%3|damage=%4", _irProjectileId, _irTargetId, _irHits, damage _irTarget]] call _assert;
private _repeatedOk = count _allFires isEqualTo 2 && {_normalProjectileId isNotEqualTo _irProjectileId}
    && {_normalTargetId isNotEqualTo _irTargetId} && {alive _aircraft}
    && {(_entry getOrDefault ["state", ""]) isEqualTo YSF_FW_STATE_ON_STATION};
["vigil.fixedWing.strike.repeated", _repeatedOk, format ["fires=%1|projectiles=%2|targets=%3|state=%4", count _allFires, [_normalProjectileId, _irProjectileId], [_normalTargetId, _irTargetId], _entry getOrDefault ["state", ""]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_IR_DONE", [_token, _irProjectileId, _irTargetId], true];

private _controlDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_NO_DESIGNATION_REQUEST"} || diag_tickTime > _controlDeadline};
private _firesBeforeControl = count ((_irCombat getOrDefault ["fires", []]) select {(_x getOrDefault ["source", ""]) isEqualTo _aircraftId});
uiSleep 6;
private _controlCombat = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _firesAfterControl = count ((_controlCombat getOrDefault ["fires", []]) select {(_x getOrDefault ["source", ""]) isEqualTo _aircraftId});
private _noDesignationOk = _firesBeforeControl isEqualTo 2 && {_firesAfterControl isEqualTo _firesBeforeControl};
["vigil.fixedWing.control.noDesignation", _noDesignationOk, format ["fires=%1:%2|request=%3", _firesBeforeControl, _firesAfterControl, missionNamespace getVariable ["TRIBUNAL_FIXED_WING_NO_DESIGNATION_REQUEST", []]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_CONTROL_DONE", [_token, _firesAfterControl], true];

private _rtbDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    _entry = [_assetId] call YSF_fwGetEntry;
    (_entry getOrDefault ["state", ""]) isEqualTo YSF_FW_STATE_RTB || diag_tickTime > _rtbDeadline
};
private _rtbStart = getPosASL _aircraft;
private _rtbSamples = [_aircraft, _exfil, {
    params ["_observed"];
    isNull _observed
}, 180, 0.25] call TRIBUNAL_fnc_observeFlight;
private _rtbEvidence = [_rtbSamples, _rtbStart, _exfil] call TRIBUNAL_fnc_flightEvidence;
_entry = [_assetId] call YSF_fwGetEntry;
private _rtbFlightOk = (_rtbEvidence getOrDefault ["maximumTravel", 0]) > 300
    && {(_rtbEvidence getOrDefault ["minimumDistance", 1e9]) < 650};
["vigil.fixedWing.egress.flight", _rtbFlightOk, format ["start=%1|exfil=%2|samples=%3|minDistance=%4|maxTravel=%5", _rtbStart, _exfil, _rtbEvidence getOrDefault ["samples", 0], _rtbEvidence getOrDefault ["minimumDistance", -1], _rtbEvidence getOrDefault ["maximumTravel", -1]]] call _assert;
private _egressOk = isNull _aircraft && {isNull (_entry getOrDefault ["spawnedVeh", objNull])}
    && {(_entry getOrDefault ["lastRtbResult", ""]) isEqualTo "success"}
    && {(_entry getOrDefault ["state", ""]) in [YSF_FW_STATE_STOWED, YSF_FW_STATE_COOLDOWN]}
    && {typeName _entry isEqualTo "HASHMAP"};
["vigil.fixedWing.egress.cleanup", _egressOk, format ["aircraftNull=%1|spawnedNull=%2|state=%3|result=%4|cooldown=%5", isNull _aircraft, isNull (_entry getOrDefault ["spawnedVeh", objNull]), _entry getOrDefault ["state", ""], _entry getOrDefault ["lastRtbResult", ""], _entry getOrDefault ["cooldownSeconds", -1]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_EGRESS_DONE", [_token, _assetId, _entry getOrDefault ["state", ""]], true];

[_combatToken] call TRIBUNAL_fnc_combatObserverStop;
{if (!isNull _x) then {deleteVehicleCrew _x; deleteVehicle _x}} forEach [_normalTarget, _irTarget];
private _registry = call YSF_fwEnsureRegistry;
private _cleanupOk = count _registry isEqualTo 1
    && {isNull (_entry getOrDefault ["spawnedVeh", objNull])}
    && {isNull _normalLaser} && {isNull _irLaser};
["vigil.fixedWing.cleanup", _cleanupOk, format ["registry=%1|spawned=%2|normalLaserNull=%3|irLaserNull=%4", keys _registry, _entry getOrDefault ["spawnedVeh", objNull], isNull _normalLaser, isNull _irLaser]] call _assert;
''',
    client_sqf=designation_observer_sqf() + r'''
private _fixtureDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_FIXTURE"} || diag_tickTime > _fixtureDeadline};
private _fixture = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_FIXTURE", []];
private _assetId = _fixture param [1, ""];
private _registry = call YSF_fwGetPublicRegistry;
private _rowIndex = _registry findIf {(_x param [0, ""]) isEqualTo _assetId};
private _registryOk = (_fixture param [0, ""]) isEqualTo _token && {_rowIndex >= 0}
    && {((_registry select _rowIndex) param [1, ""]) isEqualTo YSF_FW_STATE_STOWED}
    && {((_registry select _rowIndex) param [2, ""]) isEqualTo "SABER"};
["vigil.fixedWing.client.registry", _registryOk, format ["fixture=%1|registry=%2", _fixture, _registry]] call _assert;
player linkItem "YSF_VigilTerminal_B";
player allowDamage false;
uiNamespace setVariable ["YSF_current_selected_fw_id", _assetId];
call YOSHI_taskFW_deploy;
private _deployedDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_DEPLOYED"} || diag_tickTime > _deployedDeadline};
private _deployed = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_DEPLOYED", []];
private _aircraftId = _deployed param [2, ""];
private _aircraft = if (_aircraftId isEqualTo "") then {objNull} else {objectFromNetId _aircraftId};
private _deployOk = (_deployed param [0, ""]) isEqualTo _token && {!isNull _aircraft} && {alive _aircraft};
["vigil.fixedWing.client.deploy", _deployOk, format ["signal=%1|aircraft=%2|state=%3", _deployed, _aircraft, if (_rowIndex < 0) then {""} else {(_registry select _rowIndex) param [1, ""]}]] call _assert;
["vigil.fixedWing.client.locality", !isNull _aircraft && {!local _aircraft}, format ["aircraft=%1|local=%2|clientOwnerView=%3|playerOwnerView=%4|serverLocalityProvenSeparately=true", _aircraftId, if (isNull _aircraft) then {false} else {local _aircraft}, if (isNull _aircraft) then {-1} else {owner _aircraft}, owner player]] call _assert;

removeAllWeapons player;
player addMagazine "Laserbatteries";
player addWeapon "Laserdesignator";
diag_log format ["TRIBUNAL_FIXED_WING|HANDHELD_EQUIPPED|weapons=%1", weapons player];
private _handheldSelectedDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; currentWeapon player isEqualTo "Laserdesignator" || diag_tickTime > _handheldSelectedDeadline};
if (currentWeapon player isEqualTo "Laserdesignator") then {
    diag_log format ["TRIBUNAL_FIXED_WING|HANDHELD_ARMED|weapon=%1|weapons=%2", currentWeapon player, weapons player];
};
private _normalLaserDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; !isNull (laserTarget player) || diag_tickTime > _normalLaserDeadline};
private _normalLaser = laserTarget player;
private _normalSnapshot = [player, _normalLaser, "laser-designator"] call TRIBUNAL_fnc_designationRecord;
private _normalClientOk = currentWeapon player isEqualTo "Laserdesignator"
    && {!isNull _normalLaser} && {local _normalLaser}
    && {(_normalSnapshot getOrDefault ["designation", ""]) isNotEqualTo ""}
    && {(_normalSnapshot getOrDefault ["designationClass", ""]) isKindOf "LaserTarget"};
["vigil.fixedWing.client.normalDesignation", _normalClientOk, format ["snapshot=%1|weapon=%2|magazine=%3", _normalSnapshot, currentWeapon player, currentMagazine player]] call _assert;
if (_normalClientOk) then {diag_log "TRIBUNAL_FIXED_WING|HANDHELD_ACTIVE"};
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_NORMAL_READY", [_token, netId _normalLaser], true];
private _normalTargetDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_NORMAL_TARGET"} || diag_tickTime > _normalTargetDeadline};
private _normalTarget = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_NORMAL_TARGET", []];
["bomb", "Bomb_04_Plane_CAS_01_F"] call YSF_fwRequestStrike;
private _busyObserved = false;
private _normalRequestDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    if (missionNamespace getVariable ["YSF_fw_strikeBusy", false]) then {_busyObserved = true};
    _busyObserved || diag_tickTime > _normalRequestDeadline
};
["vigil.fixedWing.client.normalRequest", _busyObserved, format ["target=%1|busy=%2|designation=%3", _normalTarget, missionNamespace getVariable ["YSF_fw_strikeBusy", false], netId _normalLaser]] call _assert;
private _normalDoneDeadline = diag_tickTime + 120;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_NORMAL_DONE"} || diag_tickTime > _normalDoneDeadline};
private _normalDone = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_NORMAL_DONE", []];
private _normalResultOk = (_normalDone param [0, ""]) isEqualTo _token
    && {(_normalDone param [1, ""]) isNotEqualTo ""}
    && {(_normalDone param [2, ""]) isEqualTo (_normalTarget param [1, ""])};
["vigil.fixedWing.client.normalResult", _normalResultOk, format ["done=%1|target=%2", _normalDone, _normalTarget]] call _assert;
diag_log "TRIBUNAL_FIXED_WING|HANDHELD_DONE";
private _normalOffDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; isNull (laserTarget player) || diag_tickTime > _normalOffDeadline};

removeAllWeapons player;
player addWeapon "arifle_MX_F";
player addPrimaryWeaponItem "acc_pointer_IR";
player selectWeapon "arifle_MX_F";
diag_log "TRIBUNAL_FIXED_WING|IR_ARMED";
private _irLaserDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    private _candidate = player getVariable ["YSF_irFakeLaserTarget", objNull];
    (!isNull _candidate && {((getPosASL _candidate) # 2) - (getTerrainHeightASL getPosASL _candidate) < 100})
        || diag_tickTime > _irLaserDeadline
};
private _irLaser = player getVariable ["YSF_irFakeLaserTarget", objNull];
private _irSnapshot = [player, _irLaser, "weapon-ir-helper"] call TRIBUNAL_fnc_designationRecord;
private _irClientOk = [player] call YSF_irLaserViz_isIrPointerActive
    && {!isNull _irLaser} && {local _irLaser}
    && {((getPosASL _irLaser) # 2) - (getTerrainHeightASL getPosASL _irLaser) < 100}
    && {(_irSnapshot getOrDefault ["designation", ""]) isNotEqualTo ""}
    && {[_irLaser] isNotEqualTo [_normalLaser]};
["vigil.fixedWing.client.irDesignation", _irClientOk, format ["snapshot=%1|weapon=%2|accessories=%3|active=%4", _irSnapshot, currentWeapon player, primaryWeaponItems player, [player] call YSF_irLaserViz_isIrPointerActive]] call _assert;
if (_irClientOk) then {diag_log "TRIBUNAL_FIXED_WING|IR_ACTIVE"};
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_IR_READY", [_token, netId _irLaser], true];
private _irTargetDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_IR_TARGET"} || diag_tickTime > _irTargetDeadline};
private _irTarget = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_IR_TARGET", []];
["bomb", "Bomb_04_Plane_CAS_01_F"] call YSF_fwRequestStrike;
private _irBusyObserved = false;
private _irRequestDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    if (missionNamespace getVariable ["YSF_fw_strikeBusy", false]) then {_irBusyObserved = true};
    _irBusyObserved || diag_tickTime > _irRequestDeadline
};
["vigil.fixedWing.client.irRequest", _irBusyObserved, format ["target=%1|busy=%2|designation=%3", _irTarget, missionNamespace getVariable ["YSF_fw_strikeBusy", false], netId _irLaser]] call _assert;
private _irDoneDeadline = diag_tickTime + 120;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_IR_DONE"} || diag_tickTime > _irDoneDeadline};
private _irDone = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_IR_DONE", []];
private _irResultOk = (_irDone param [0, ""]) isEqualTo _token
    && {(_irDone param [1, ""]) isNotEqualTo ""}
    && {(_irDone param [2, ""]) isEqualTo (_irTarget param [1, ""])};
["vigil.fixedWing.client.irResult", _irResultOk, format ["done=%1|target=%2", _irDone, _irTarget]] call _assert;
diag_log "TRIBUNAL_FIXED_WING|IR_DONE";
private _irOffDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    isNull (player getVariable ["YSF_irFakeLaserTarget", objNull]) || diag_tickTime > _irOffDeadline
};
private _designationsClean = isNull (laserTarget player)
    && {isNull (player getVariable ["YSF_irFakeLaserTarget", objNull])}
    && {([player] call YSF_fwGetDesignationDescriptorForUnit) isEqualTo []};
["vigil.fixedWing.client.designationCleanup", _designationsClean, format ["normal=%1|ir=%2|descriptor=%3", laserTarget player, player getVariable ["YSF_irFakeLaserTarget", objNull], [player] call YSF_fwGetDesignationDescriptorForUnit]] call _assert;
diag_log "TRIBUNAL_FIXED_WING|DESIGNATIONS_CLEAN";
missionNamespace setVariable ["TRIBUNAL_FIXED_WING_NO_DESIGNATION_REQUEST", [_token, diag_tickTime], true];
["bomb", "Bomb_04_Plane_CAS_01_F"] call YSF_fwRequestStrike;
private _controlDoneDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_CONTROL_DONE"} || diag_tickTime > _controlDoneDeadline};
private _controlDone = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_CONTROL_DONE", []];
["vigil.fixedWing.client.noDesignation", (_controlDone param [0, ""]) isEqualTo _token && {(_controlDone param [1, -1]) isEqualTo 2}, format ["descriptor=%1|control=%2", [player] call YSF_fwGetDesignationDescriptorForUnit, _controlDone]] call _assert;
uiNamespace setVariable ["YSF_current_selected_fw_id", _assetId];
call YOSHI_taskFW_rtb;
private _egressDeadline = diag_tickTime + 210;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_FIXED_WING_EGRESS_DONE"} || diag_tickTime > _egressDeadline};
private _egress = missionNamespace getVariable ["TRIBUNAL_FIXED_WING_EGRESS_DONE", []];
["vigil.fixedWing.client.rtb", (_egress param [0, ""]) isEqualTo _token && {isNull _aircraft} && {(_egress param [2, ""]) in [YSF_FW_STATE_STOWED, YSF_FW_STATE_COOLDOWN]}, format ["egress=%1|aircraftNull=%2", _egress, isNull _aircraft]] call _assert;
player allowDamage true;
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-fixed-wing-strike",
        "fixture": "registered B_Plane_CAS_01_dynamicLoadout_F with three native Bomb_04_F rounds",
        "visual_driver": "designation-input",
        "visual_armed_marker": "TRIBUNAL_FIXED_WING|HANDHELD_EQUIPPED",
        "munition": "PylonMissile_1Rnd_Bomb_04_F / Bomb_04_F",
        "player_spawn": "2000,5,5600",
        "respawn_on_start": "0",
        "future_client_isolation": "client-b observes shared aircraft/projectiles but never inherits client-a input/helper state",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A registered fixed-wing strike asset preserves gameplay-relevant state, reconstructs once at ingress, accepts real client laser and weapon-IR designations, releases exact physically guided native munitions twice, rejects a designation-free request, then physically egresses and despawns while remaining registered.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Live A/B evidence found fuel and partial ammunition loss plus an unnecessary count-changing laser-bomb rewrite; the scenario protects the corrected user-visible lifecycle without freezing registry schema, coordinates, waypoint details, or helper names.",
        dependencies=("Tribunal aviation/combat/designation observers", "authenticated X11 input", "Vigil fixed-wing registry and strike API"),
        evidence_types=frozenset({"registration", "aircraft-trajectory", "designation", "input", "Fired", "projectile-trajectory", "HitPart", "damage", "locality", "cleanup"}),
        locality_requirements="Client-a owns input and both designation objects; the dedicated server owns registry, aircraft, crew, projectiles, damage observation, RTB, and cleanup.",
    ),
)
