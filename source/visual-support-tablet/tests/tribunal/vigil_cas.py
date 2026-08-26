"""Physical Tier 3 contract for Vigil rotary-wing close air support."""

from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.mission.combat import combat_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-cas",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.cas.fixture",
        "vigil.cas.locality",
        "vigil.cas.dispatch.accepted",
        "vigil.cas.dispatch.duplicateRejected",
        "vigil.cas.transit",
        "vigil.cas.onStation",
        "vigil.cas.target.controls",
        "vigil.cas.attack.fired",
        "vigil.cas.attack.correlated",
        "vigil.cas.attack.effect",
        "vigil.cas.timer",
        "vigil.cas.disengaged",
        "vigil.cas.rtb",
        "vigil.cas.home",
        "vigil.cas.noTarget",
        "vigil.cas.noAmmo",
        "vigil.cas.cleanup",
    }),
    client_expected=frozenset({
        "vigil.cas.client.locality",
        "vigil.cas.client.eligible",
        "vigil.cas.client.dispatch",
        "vigil.cas.client.onStation",
        "vigil.cas.client.home",
        "vigil.cas.client.noTarget",
    }),
    server_sqf=aviation_observer_sqf() + combat_observer_sqf() + r'''
private _home = [1800, 5600, 0];
private _area = [3200, 5600, 0];
private _combatToken = format ["%1-vigil-cas", _token];
private _homePad = "Land_HelipadEmpty_F" createVehicle _home;
private _aircraft = "B_Heli_Attack_01_F" createVehicle _home;
_aircraft setDir 90;
_aircraft setFuel 1;
_aircraft setDamage 0;
createVehicleCrew _aircraft;
{_x setSkill 1} forEach crew _aircraft;

private _hostile = "O_MBT_02_cannon_F" createVehicle _area;
createVehicleCrew _hostile;
_hostile setFuel 0;
{_x disableAI "ALL"} forEach crew _hostile;
private _friendly = "B_MRAP_01_F" createVehicle [3200, 5900, 0];
createVehicleCrew _friendly;
_friendly setFuel 0;
{doStop _x} forEach crew _friendly;
private _neutral = "C_Offroad_01_F" createVehicle [3200, 5300, 0];
_neutral setFuel 0;
private _outside = "O_MRAP_02_F" createVehicle [3200, 7000, 0];
_outside setFuel 0;

private _setupDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.1;
    (!isNull driver _aircraft && {alive driver _aircraft}) || diag_tickTime > _setupDeadline
};
private _pilot = driver _aircraft;
private _aircraftId = netId _aircraft;
private _hostileId = netId _hostile;
private _friendlyId = netId _friendly;
private _neutralId = netId _neutral;
private _outsideId = netId _outside;
private _fixtureOk = !isNull _aircraft && {alive _aircraft} && {!isNull _pilot}
    && {_aircraftId isNotEqualTo ""} && {_hostileId isNotEqualTo ""}
    && {_friendlyId isNotEqualTo ""} && {_neutralId isNotEqualTo ""}
    && {_outsideId isNotEqualTo ""};
["vigil.cas.fixture", _fixtureOk, format ["aircraft=%1|pilot=%2|hostile=%3|friendly=%4|neutral=%5|outside=%6|home=%7|area=%8", _aircraftId, if (isNull _pilot) then {""} else {netId _pilot}, _hostileId, _friendlyId, _neutralId, _outsideId, _home, _area]] call _assert;
private _localityOk = isServer && {local _aircraft} && {local _pilot}
    && {local (group _pilot)} && {local _hostile} && {local _friendly}
    && {local _neutral} && {local _outside};
["vigil.cas.locality", _localityOk, format ["server=%1|aircraft=%2/%3|pilot=%4/%5|group=%6|targets=%7", isServer, local _aircraft, owner _aircraft, local _pilot, owner _pilot, local (group _pilot), [local _hostile, local _friendly, local _neutral, local _outside]]] call _assert;

[_combatToken] call TRIBUNAL_fnc_combatObserverStart;
[_combatToken, _aircraft] call TRIBUNAL_fnc_combatObserveSource;
{[_combatToken, _x] call TRIBUNAL_fnc_combatObserveTarget} forEach [_hostile, _friendly, _neutral, _outside];
private _initialAmmo = [_aircraft, "ACE_gatling_20mm_Comanche"] call YSF_AAE_weaponAmmoCount;
missionNamespace setVariable ["TRIBUNAL_VIGIL_CAS_FIXTURE", [_token, _aircraftId, _hostileId, _friendlyId, _neutralId, _outsideId, _home, _area], true];

private _dispatchDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.1;
    (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "dispatching"
        || diag_tickTime > _dispatchDeadline
};
private _dispatchTask = _aircraft getVariable ["YSF_cas_taskId", ""];
private _dispatchOk = (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "dispatching"
    && {_dispatchTask isNotEqualTo ""}
    && {(_aircraft getVariable ["YSF_cas_lastRequest", ""]) in ["accepted", "duplicate_rejected"]};
["vigil.cas.dispatch.accepted", _dispatchOk, format ["state=%1|task=%2|request=%3|area=%4", _aircraft getVariable ["YSF_cas_state", ""], _dispatchTask, _aircraft getVariable ["YSF_cas_lastRequest", ""], _aircraft getVariable ["YSF_cas_areaATL", []]]] call _assert;
private _duplicateDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (_aircraft getVariable ["YSF_cas_lastRequest", ""]) isEqualTo "duplicate_rejected"
        || diag_tickTime > _duplicateDeadline
};
private _duplicateOk = (_aircraft getVariable ["YSF_cas_lastRequest", ""]) isEqualTo "duplicate_rejected"
    && {(_aircraft getVariable ["YSF_cas_taskId", ""]) isEqualTo _dispatchTask};
["vigil.cas.dispatch.duplicateRejected", _duplicateOk, format ["request=%1|task=%2|activeTask=%3", _aircraft getVariable ["YSF_cas_lastRequest", ""], _dispatchTask, _aircraft getVariable ["YSF_cas_taskId", ""]]] call _assert;

private _dispatchStart = getPosATL _aircraft;
private _dispatchSamples = [_aircraft, _area, {
    params ["_observed"];
    (_observed getVariable ["YSF_cas_state", ""]) in ["on_station", "failed", "cancelled"]
}, 190, 0.5] call TRIBUNAL_fnc_observeFlight;
private _dispatchEvidence = [_dispatchSamples, _dispatchStart, _area] call TRIBUNAL_fnc_flightEvidence;
private _areaDistance = _aircraft distance2D _area;
private _transitOk = (_dispatchEvidence getOrDefault ["moved", false])
    && {(_dispatchEvidence getOrDefault ["maximumAltitudeATL", 0]) > 5}
    && {_areaDistance <= YSF_CAS_ARRIVAL_RADIUS};
["vigil.cas.transit", _transitOk, format ["samples=%1|minDistance=%2|maxTravel=%3|maxAltitude=%4|areaDistance=%5", _dispatchEvidence getOrDefault ["samples", 0], _dispatchEvidence getOrDefault ["minimumDistance", -1], _dispatchEvidence getOrDefault ["maximumTravel", -1], _dispatchEvidence getOrDefault ["maximumAltitudeATL", -1], _areaDistance]] call _assert;
private _onStationAt = serverTime;
private _onStationOk = (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "on_station"
    && {_aircraft getVariable ["YSF_cas_active", false]}
    && {(_aircraft getVariable ["YSF_cas_areaATL", []]) isEqualTo _area};
["vigil.cas.onStation", _onStationOk, format ["state=%1|active=%2|distance=%3|area=%4", _aircraft getVariable ["YSF_cas_state", ""], _aircraft getVariable ["YSF_cas_active", false], _areaDistance, _aircraft getVariable ["YSF_cas_areaATL", []]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_CAS_ON_STATION", [_token, _aircraftId], true];

private _attackDeadline = diag_tickTime + 40;
waitUntil {
    uiSleep 0.1;
    private _combat = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
    private _events = missionNamespace getVariable ["YSF_CAS_EngagementEvents", []];
    (count (_combat getOrDefault ["hits", []]) > 0 && {count _events > 0})
        || diag_tickTime > _attackDeadline
};
private _combat = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _fires = _combat getOrDefault ["fires", []];
private _hits = _combat getOrDefault ["hits", []];
private _damageEvents = _combat getOrDefault ["damage", []];
private _ledger = missionNamespace getVariable ["YSF_CAS_EngagementEvents", []];
private _hostileFires = _fires select {(_x getOrDefault ["source", ""]) isEqualTo _aircraftId};
private _hostileLedger = _ledger select {(_x param [1, ""]) isEqualTo _aircraftId && {(_x param [2, ""]) isEqualTo _hostileId}};
private _hostileHits = _hits select {(_x param [1, ""]) isEqualTo _hostileId};
private _controlHits = _hits select {(_x param [1, ""]) in [_friendlyId, _neutralId, _outsideId]};
private _controlLedger = _ledger select {(_x param [2, ""]) in [_friendlyId, _neutralId, _outsideId]};
private _ammoAfter = [_aircraft, "ACE_gatling_20mm_Comanche"] call YSF_AAE_weaponAmmoCount;
private _weaponOk = _hostileFires findIf {
    private _weapon = _x getOrDefault ["weapon", ""];
    private _ammo = _x getOrDefault ["ammo", ""];
    private _simulation = toLower getText (configFile >> "CfgAmmo" >> _ammo >> "simulation");
    _weapon isEqualTo "ACE_gatling_20mm_Comanche" && {"shotbullet" in _simulation}
} >= 0;
["vigil.cas.target.controls", count _controlLedger isEqualTo 0 && {count _controlHits isEqualTo 0} && {damage _friendly isEqualTo 0} && {damage _neutral isEqualTo 0} && {damage _outside isEqualTo 0}, format ["hostile=%1|controlLedger=%2|controlHits=%3|damage=%4", _hostileId, _controlLedger, _controlHits, [damage _friendly, damage _neutral, damage _outside]]] call _assert;
["vigil.cas.attack.fired", count _hostileFires > 0 && {_weaponOk} && {_ammoAfter < _initialAmmo}, format ["aircraft=%1|fires=%2|ammo=%3:%4", _aircraftId, _hostileFires, _initialAmmo, _ammoAfter]] call _assert;
["vigil.cas.attack.correlated", count _hostileLedger > 0, format ["aircraft=%1|hostile=%2|ledger=%3", _aircraftId, _hostileId, _hostileLedger]] call _assert;
["vigil.cas.attack.effect", count _hostileHits > 0, format ["hostile=%1|hits=%2|damageEvents=%3|damage=%4", _hostileId, _hostileHits, _damageEvents, damage _hostile]] call _assert;

private _returnDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (_aircraft getVariable ["YSF_cas_state", ""]) in ["returning", "failed", "cancelled"]
        || diag_tickTime > _returnDeadline
};
private _stationDuration = serverTime - _onStationAt;
private _timerOk = _stationDuration >= 25 && {_stationDuration < 50};
["vigil.cas.timer", _timerOk, format ["duration=%1|state=%2", _stationDuration, _aircraft getVariable ["YSF_cas_state", ""]]] call _assert;
private _fireCountAtReturn = count _fires;
uiSleep 6;
private _combatAfterDisengage = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _disengaged = !(_aircraft getVariable ["YSF_cas_active", true])
    && {(_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "returning"}
    && {count (_combatAfterDisengage getOrDefault ["fires", []]) isEqualTo _fireCountAtReturn};
["vigil.cas.disengaged", _disengaged, format ["state=%1|active=%2|fires=%3:%4", _aircraft getVariable ["YSF_cas_state", ""], _aircraft getVariable ["YSF_cas_active", true], _fireCountAtReturn, count (_combatAfterDisengage getOrDefault ["fires", []])]] call _assert;

private _returnStart = getPosATL _aircraft;
private _returnSamples = [_aircraft, _home, {
    params ["_observed"];
    (_observed getVariable ["YSF_cas_state", ""]) in ["home", "failed", "cancelled"]
}, 190, 0.5] call TRIBUNAL_fnc_observeFlight;
private _returnEvidence = [_returnSamples, _returnStart, _home] call TRIBUNAL_fnc_flightEvidence;
private _rtbOk = (_returnEvidence getOrDefault ["moved", false])
    && {(_returnEvidence getOrDefault ["approached", false])}
    && {(_returnEvidence getOrDefault ["maximumAltitudeATL", 0]) > 5};
["vigil.cas.rtb", _rtbOk, format ["samples=%1|minDistance=%2|maxTravel=%3|maxAltitude=%4", _returnEvidence getOrDefault ["samples", 0], _returnEvidence getOrDefault ["minimumDistance", -1], _returnEvidence getOrDefault ["maximumTravel", -1], _returnEvidence getOrDefault ["maximumAltitudeATL", -1]]] call _assert;
private _homeDistance = _aircraft distance2D _home;
private _homeOk = (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "home"
    && {_homeDistance < 25} && {_returnEvidence getOrDefault ["landed", false]}
    && {alive _aircraft} && {damage _aircraft < 0.5};
["vigil.cas.home", _homeOk, format ["state=%1|distance=%2|touching=%3|speed=%4|damage=%5", _aircraft getVariable ["YSF_cas_state", ""], _homeDistance, isTouchingGround _aircraft, vectorMagnitude velocity _aircraft, damage _aircraft]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_CAS_HOME", [_token, _aircraftId], true];

deleteVehicleCrew _hostile;
deleteVehicle _hostile;
deleteVehicleCrew _outside;
deleteVehicle _outside;
private _beforeNoTarget = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _beforeNoTargetFires = count (_beforeNoTarget getOrDefault ["fires", []]);
private _beforeNoTargetLedger = count (missionNamespace getVariable ["YSF_CAS_EngagementEvents", []]);
missionNamespace setVariable ["TRIBUNAL_VIGIL_CAS_NO_TARGET_READY", [_token, _aircraftId], true];
private _noTargetDeadline = diag_tickTime + 260;
waitUntil {
    uiSleep 0.2;
    (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "home"
        && {(_aircraft getVariable ["YSF_cas_taskId", ""]) isNotEqualTo _dispatchTask}
        || diag_tickTime > _noTargetDeadline
};
private _afterNoTarget = [_combatToken] call TRIBUNAL_fnc_combatObserverState;
private _noTargetOk = (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "home"
    && {count (_afterNoTarget getOrDefault ["fires", []]) isEqualTo _beforeNoTargetFires}
    && {count (missionNamespace getVariable ["YSF_CAS_EngagementEvents", []]) isEqualTo _beforeNoTargetLedger};
["vigil.cas.noTarget", _noTargetOk, format ["state=%1|fires=%2:%3|ledger=%4:%5", _aircraft getVariable ["YSF_cas_state", ""], _beforeNoTargetFires, count (_afterNoTarget getOrDefault ["fires", []]), _beforeNoTargetLedger, count (missionNamespace getVariable ["YSF_CAS_EngagementEvents", []])]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_CAS_NO_TARGET_DONE", [_token, _aircraftId], true];

private _unavailable = "B_Heli_Attack_01_F" createVehicle [1700, 5500, 0];
createVehicleCrew _unavailable;
_unavailable setVehicleAmmo 0;
private _handlers = call YSF_handlers_cas;
private _invalidTask = ["cas", _unavailable, _handlers, [_area, 60, 0.1], 10, 3] call YSF_taskNew;
[_unavailable, _invalidTask] call YSF_taskCASAssign;
private _invalidDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.1; (_unavailable getVariable ["YSF_cas_state", ""]) isEqualTo "failed" || diag_tickTime > _invalidDeadline};
private _noAmmoOk = !([_unavailable] call YSF_CAS_hasLethalAmmo)
    && {(_unavailable getVariable ["YSF_cas_state", ""]) isEqualTo "failed"}
    && {!(_unavailable getVariable ["YSF_cas_active", true])};
["vigil.cas.noAmmo", _noAmmoOk, format ["state=%1|active=%2|ammo=%3", _unavailable getVariable ["YSF_cas_state", ""], _unavailable getVariable ["YSF_cas_active", true], magazinesAmmoFull _unavailable]] call _assert;

[_combatToken] call TRIBUNAL_fnc_combatObserverStop;
private _manager = (call YSF__mgr) getOrDefault [[_aircraft] call YSF_taskKey, objNull];
private _managerIdle = typeName _manager isEqualTo "HASHMAP" && {!(_manager getOrDefault ["enabled", true])};
{deleteVehicleCrew _x; deleteVehicle _x} forEach [_aircraft, _friendly, _unavailable];
deleteVehicle _neutral;
deleteVehicle _homePad;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _aircraft && {isNull _unavailable} || diag_tickTime > _cleanupDeadline};
private _cleanupOk = isNull _aircraft && {isNull _unavailable} && {_managerIdle};
["vigil.cas.cleanup", _cleanupOk, format ["aircraftNull=%1|invalidNull=%2|managerIdle=%3", isNull _aircraft, isNull _unavailable, _managerIdle]] call _assert;
''',
    client_sqf=r'''
private _fixtureDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_CAS_FIXTURE"} || diag_tickTime > _fixtureDeadline};
private _fixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_CAS_FIXTURE", []];
private _aircraftId = _fixture param [1, ""];
private _aircraft = if (_aircraftId isEqualTo "") then {objNull} else {objectFromNetId _aircraftId};
private _area = _fixture param [7, []];
private _crewDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (!isNull _aircraft && {!isNull effectiveCommander _aircraft}) || diag_tickTime > _crewDeadline};
["vigil.cas.client.locality", hasInterface && {!isServer} && {!isNull _aircraft} && {!local _aircraft}, format ["interface=%1|server=%2|aircraft=%3|local=%4|owner=%5", hasInterface, isServer, _aircraftId, if (isNull _aircraft) then {false} else {local _aircraft}, if (isNull _aircraft) then {-1} else {owner _aircraft}]] call _assert;
private _eligible = !isNull _aircraft && {[_aircraft] call YOSHI_isArmedHelicopter};
["vigil.cas.client.eligible", _eligible, format ["class=%1|crew=%2|weapons=%3", typeOf _aircraft, crew _aircraft, weapons _aircraft]] call _assert;
uiNamespace setVariable ["YSF_current_selected_asset", _aircraft];
private _state = call YOSHI_taskCAS_GetState;
_state set ["grid", _area];
_state set ["alt", 60];
_state set ["time_limit", 0.5];
uiNamespace setVariable ["YOSHI_taskCAS_state", _state];
call YOSHI_taskCAS_submit;
private _dispatchDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "dispatching" || diag_tickTime > _dispatchDeadline};
private _dispatchOk = (_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "dispatching"
    && {(_aircraft getVariable ["YSF_cas_taskId", ""]) isNotEqualTo ""};
["vigil.cas.client.dispatch", _dispatchOk, format ["state=%1|task=%2|area=%3", _aircraft getVariable ["YSF_cas_state", ""], _aircraft getVariable ["YSF_cas_taskId", ""], _area]] call _assert;
uiSleep 2;
call YOSHI_taskCAS_submit;

private _stationDeadline = diag_tickTime + 210;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_CAS_ON_STATION"} || diag_tickTime > _stationDeadline};
private _station = missionNamespace getVariable ["TRIBUNAL_VIGIL_CAS_ON_STATION", []];
private _stationOk = (_station param [0, ""]) isEqualTo _token
    && {(_station param [1, ""]) isEqualTo _aircraftId}
    && {(_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "on_station"};
["vigil.cas.client.onStation", _stationOk, format ["signal=%1|state=%2|active=%3", _station, _aircraft getVariable ["YSF_cas_state", ""], _aircraft getVariable ["YSF_cas_active", false]]] call _assert;

private _homeDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_CAS_HOME"} || diag_tickTime > _homeDeadline};
private _homeSignal = missionNamespace getVariable ["TRIBUNAL_VIGIL_CAS_HOME", []];
private _homeOk = (_homeSignal param [0, ""]) isEqualTo _token
    && {(_homeSignal param [1, ""]) isEqualTo _aircraftId}
    && {(_aircraft getVariable ["YSF_cas_state", ""]) isEqualTo "home"};
["vigil.cas.client.home", _homeOk, format ["signal=%1|state=%2", _homeSignal, _aircraft getVariable ["YSF_cas_state", ""]]] call _assert;

private _readyDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_CAS_NO_TARGET_READY"} || diag_tickTime > _readyDeadline};
private _ready = missionNamespace getVariable ["TRIBUNAL_VIGIL_CAS_NO_TARGET_READY", []];
if ((_ready param [0, ""]) isEqualTo _token) then {
    uiNamespace setVariable ["YSF_current_selected_asset", _aircraft];
    private _second = call YOSHI_taskCAS_GetState;
    _second set ["grid", _area];
    _second set ["alt", 60];
    _second set ["time_limit", 0.1];
    uiNamespace setVariable ["YOSHI_taskCAS_state", _second];
    call YOSHI_taskCAS_submit;
};
private _noTargetDeadline = diag_tickTime + 280;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_CAS_NO_TARGET_DONE"} || diag_tickTime > _noTargetDeadline};
private _noTargetSignal = missionNamespace getVariable ["TRIBUNAL_VIGIL_CAS_NO_TARGET_DONE", []];
private _noTargetOk = (_noTargetSignal param [0, ""]) isEqualTo _token
    && {(_noTargetSignal param [1, ""]) isEqualTo _aircraftId};
["vigil.cas.client.noTarget", _noTargetOk, format ["ready=%1|done=%2", _ready, _noTargetSignal]] call _assert;
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-rotary-cas",
        "fixture": "server-local-crewed-B_Heli_Attack_01_F versus stationary O_MBT_02_cannon_F",
        "flight_corridor": "Stratis [1800,5600] to [3200,5600]",
        "ui_path": "YOSHI_taskCAS_submit",
        "representative_weapon": "ACE_gatling_20mm_Comanche / ACE_20mm_HE",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A valid selected rotary CAS helicopter accepts one area task, physically reaches the operating region, attacks only a valid hostile ground target with a real appropriate weapon and attributable impact, remains active for the requested bounded duration, disengages, physically returns and settles at home, and can repeat the lifecycle without fabricating attacks when no target exists.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Review found globally-scoped engagement, incorrect side resolution, absent area filtering, fragile guided-only selection, unbounded duplicate/invalid requests, and no reliable RTB. The refined implementation and scenario assert the user path plus independent trajectory, fire, impact, control-target, timer, locality, and cleanup evidence.",
        dependencies=("Vigil task governor", "Arma helicopter AI", "CBA", "Tribunal aviation observer", "Tribunal combat observer"),
        evidence_types=frozenset({"client-request", "locality", "trajectory", "target-identity", "weapon-fire", "impact", "control-target", "task-state", "timer", "landing", "cleanup"}),
        locality_requirements="Client-a owns Vigil UI/request state; the dedicated server owns aircraft, pilot group, target selection, fire observation, authoritative combat/task state, and world effects.",
    ),
)
