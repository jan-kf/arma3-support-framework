"""Physical Tier 3 contract for Vigil helicopter dispatch and RTB."""

from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-transport",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.transport.fixture",
        "vigil.transport.locality",
        "vigil.transport.dispatch.accepted",
        "vigil.transport.dispatch.duplicateRejected",
        "vigil.transport.dispatch.flight",
        "vigil.transport.arrival",
        "vigil.transport.waiting",
        "vigil.transport.rtb.accepted",
        "vigil.transport.rtb.flight",
        "vigil.transport.home",
        "vigil.transport.cleanup",
    }),
    client_expected=frozenset({
        "vigil.transport.client.locality",
        "vigil.transport.client.eligible",
        "vigil.transport.client.dispatch",
        "vigil.transport.client.waiting",
        "vigil.transport.client.rtb",
        "vigil.transport.client.home",
    }),
    server_sqf=aviation_observer_sqf() + r'''
private _home = [1900, 5600, 0];
private _destination = [2350, 5600, 0];
private _homePad = "Land_HelipadEmpty_F" createVehicle _home;
private _destinationPad = "Land_HelipadEmpty_F" createVehicle _destination;
private _aircraft = "B_Heli_Light_01_F" createVehicle _home;
_aircraft setDir 90;
_aircraft setFuel 1;
_aircraft setDamage 0;
createVehicleCrew _aircraft;
private _setupDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.1;
    (!isNull driver _aircraft && {alive driver _aircraft} && {isTouchingGround _aircraft})
        || diag_tickTime > _setupDeadline
};
private _pilot = driver _aircraft;
private _aircraftId = netId _aircraft;
private _pilotId = if (isNull _pilot) then {""} else {netId _pilot};
private _fixtureOk = !isNull _aircraft && {alive _aircraft} && {!isNull _pilot}
    && {alive _pilot} && {_aircraftId isNotEqualTo ""};
["vigil.transport.fixture", _fixtureOk, format ["aircraft=%1|pilot=%2|home=%3|destination=%4", _aircraftId, _pilotId, getPosATL _aircraft, _destination]] call _assert;
private _localityOk = local _aircraft && {!isNull _pilot} && {local _pilot}
    && {local (group _pilot)} && {isServer};
["vigil.transport.locality", _localityOk, format ["aircraftLocal=%1|pilotLocal=%2|groupLocal=%3|aircraftOwner=%4|pilotOwner=%5", local _aircraft, if (isNull _pilot) then {false} else {local _pilot}, if (isNull _pilot) then {false} else {local (group _pilot)}, owner _aircraft, if (isNull _pilot) then {-1} else {owner _pilot}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_FIXTURE", [_token, _aircraftId, _home, _destination], true];

private _dispatchDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.1;
    (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "dispatching"
        || diag_tickTime > _dispatchDeadline
};
private _dispatchTaskId = _aircraft getVariable ["YSF_transport_taskId", ""];
private _dispatchAccepted = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "dispatching"
    && {_dispatchTaskId isNotEqualTo ""}
    && {(_aircraft getVariable ["YSF_transport_lastRequest", ""]) in ["accepted", "duplicate_rejected"]};
["vigil.transport.dispatch.accepted", _dispatchAccepted, format ["state=%1|task=%2|request=%3", _aircraft getVariable ["YSF_transport_state", ""], _dispatchTaskId, _aircraft getVariable ["YSF_transport_lastRequest", ""]]] call _assert;
private _duplicateDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (_aircraft getVariable ["YSF_transport_lastRequest", ""]) isEqualTo "duplicate_rejected"
        || diag_tickTime > _duplicateDeadline
};
private _duplicateOk = (_aircraft getVariable ["YSF_transport_lastRequest", ""]) isEqualTo "duplicate_rejected"
    && {(_aircraft getVariable ["YSF_transport_taskId", ""]) isEqualTo _dispatchTaskId};
["vigil.transport.dispatch.duplicateRejected", _duplicateOk, format ["request=%1|initialTask=%2|activeTask=%3", _aircraft getVariable ["YSF_transport_lastRequest", ""], _dispatchTaskId, _aircraft getVariable ["YSF_transport_taskId", ""]]] call _assert;

private _dispatchStart = getPosATL _aircraft;
private _dispatchSamples = [_aircraft, _destination, {
    params ["_observed"];
    (_observed getVariable ["YSF_transport_state", ""]) in ["waiting", "failed", "cancelled"]
}, 190, 0.5] call TRIBUNAL_fnc_observeFlight;
private _dispatchEvidence = [_dispatchSamples, _dispatchStart, _destination] call TRIBUNAL_fnc_flightEvidence;
private _dispatchFlightOk = (_dispatchEvidence getOrDefault ["moved", false])
    && {(_dispatchEvidence getOrDefault ["approached", false])}
    && {(_dispatchEvidence getOrDefault ["maximumAltitudeATL", 0]) > 5};
["vigil.transport.dispatch.flight", _dispatchFlightOk, format ["aircraft=%1|samples=%2|minDistance=%3|maxTravel=%4|maxAltitude=%5", _aircraftId, _dispatchEvidence getOrDefault ["samples", 0], _dispatchEvidence getOrDefault ["minimumDistance", -1], _dispatchEvidence getOrDefault ["maximumTravel", -1], _dispatchEvidence getOrDefault ["maximumAltitudeATL", -1]]] call _assert;
private _arrivalDistance = _aircraft distance2D _destination;
private _arrivalOk = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "waiting"
    && {_arrivalDistance < 25}
    && {_dispatchEvidence getOrDefault ["landed", false]}
    && {alive _aircraft} && {damage _aircraft < 0.5};
["vigil.transport.arrival", _arrivalOk, format ["state=%1|distance=%2|touching=%3|ready=%4|speed=%5|damage=%6", _aircraft getVariable ["YSF_transport_state", ""], _arrivalDistance, isTouchingGround _aircraft, unitReady _aircraft, vectorMagnitude velocity _aircraft, damage _aircraft]] call _assert;
private _waitPosition = getPosATL _aircraft;
uiSleep 5;
private _waitOk = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "waiting"
    && {_aircraft distance2D _waitPosition < 3}
    && {isTouchingGround _aircraft} && {(vectorMagnitude velocity _aircraft) < 2}
    && {alive _aircraft} && {!isNull driver _aircraft};
["vigil.transport.waiting", _waitOk, format ["state=%1|drift=%2|touching=%3|speed=%4|pilot=%5", _aircraft getVariable ["YSF_transport_state", ""], _aircraft distance2D _waitPosition, isTouchingGround _aircraft, vectorMagnitude velocity _aircraft, netId driver _aircraft]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_WAITING", [_token, _aircraftId], true];

private _rtbDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.1;
    (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "returning"
        || diag_tickTime > _rtbDeadline
};
private _rtbTaskId = _aircraft getVariable ["YSF_transport_taskId", ""];
private _rtbAccepted = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "returning"
    && {_rtbTaskId isNotEqualTo ""} && {_rtbTaskId isNotEqualTo _dispatchTaskId};
["vigil.transport.rtb.accepted", _rtbAccepted, format ["state=%1|dispatchTask=%2|rtbTask=%3", _aircraft getVariable ["YSF_transport_state", ""], _dispatchTaskId, _rtbTaskId]] call _assert;
private _returnStart = getPosATL _aircraft;
private _returnSamples = [_aircraft, _home, {
    params ["_observed"];
    (_observed getVariable ["YSF_transport_state", ""]) in ["home", "failed", "cancelled"]
}, 190, 0.5] call TRIBUNAL_fnc_observeFlight;
private _returnEvidence = [_returnSamples, _returnStart, _home] call TRIBUNAL_fnc_flightEvidence;
private _returnFlightOk = (_returnEvidence getOrDefault ["moved", false])
    && {(_returnEvidence getOrDefault ["approached", false])}
    && {(_returnEvidence getOrDefault ["maximumAltitudeATL", 0]) > 5};
["vigil.transport.rtb.flight", _returnFlightOk, format ["aircraft=%1|samples=%2|minDistance=%3|maxTravel=%4|maxAltitude=%5", _aircraftId, _returnEvidence getOrDefault ["samples", 0], _returnEvidence getOrDefault ["minimumDistance", -1], _returnEvidence getOrDefault ["maximumTravel", -1], _returnEvidence getOrDefault ["maximumAltitudeATL", -1]]] call _assert;
private _homeDistance = _aircraft distance2D _home;
private _homeOk = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "home"
    && {_homeDistance < 25} && {_returnEvidence getOrDefault ["landed", false]}
    && {alive _aircraft} && {damage _aircraft < 0.5};
["vigil.transport.home", _homeOk, format ["state=%1|distance=%2|touching=%3|ready=%4|speed=%5|damage=%6", _aircraft getVariable ["YSF_transport_state", ""], _homeDistance, isTouchingGround _aircraft, unitReady _aircraft, vectorMagnitude velocity _aircraft, damage _aircraft]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_HOME", [_token, _aircraftId], true];
uiSleep 2;

private _manager = (call YSF__mgr) getOrDefault [str _aircraft, objNull];
private _managerIdle = typeName _manager isEqualTo "HASHMAP" && {!(_manager getOrDefault ["enabled", true])};
deleteVehicleCrew _aircraft;
deleteVehicle _aircraft;
deleteVehicle _homePad;
deleteVehicle _destinationPad;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _aircraft || diag_tickTime > _cleanupDeadline};
private _cleanupOk = isNull _aircraft && {_managerIdle}
    && {(allMissionObjects "B_Heli_Light_01_F") findIf {netId _x isEqualTo _aircraftId} < 0};
["vigil.transport.cleanup", _cleanupOk, format ["aircraftNull=%1|managerIdle=%2|matchingAircraft=%3", isNull _aircraft, _managerIdle, (allMissionObjects "B_Heli_Light_01_F") findIf {netId _x isEqualTo _aircraftId}]] call _assert;
''',
    client_sqf=r'''
private _fixtureDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_FIXTURE"} || diag_tickTime > _fixtureDeadline};
private _fixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_FIXTURE", []];
private _aircraftId = _fixture param [1, ""];
private _aircraft = if (_aircraftId isEqualTo "") then {objNull} else {objectFromNetId _aircraftId};
private _destination = _fixture param [3, []];
private _crewDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (!isNull _aircraft && {!isNull effectiveCommander _aircraft}) || diag_tickTime > _crewDeadline};
["vigil.transport.client.locality", hasInterface && {!isServer} && {!isNull _aircraft} && {!local _aircraft}, format ["hasInterface=%1|server=%2|aircraft=%3|local=%4", hasInterface, isServer, _aircraftId, if (isNull _aircraft) then {false} else {local _aircraft}]] call _assert;
private _eligible = !isNull _aircraft && {[_aircraft] call YOSHI_isTransportHelicopter};
["vigil.transport.client.eligible", _eligible, format ["class=%1|side=%2|commanderSide=%3|cargo=%4", typeOf _aircraft, side _aircraft, if (isNull effectiveCommander _aircraft) then {sideUnknown} else {side group effectiveCommander _aircraft}, _aircraft emptyPositions "cargo"]] call _assert;
uiNamespace setVariable ["YSF_current_selected_asset", _aircraft];
private _state = call YOSHI_taskTransport_GetState;
_state set ["grid", _destination];
_state set ["alt", 20];
_state set ["do_not_climb", true];
_state set ["ignore_en", false];
uiNamespace setVariable ["YOSHI_taskTransport_state", _state];
call YOSHI_taskTRN_submit;
private _dispatchDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "dispatching" || diag_tickTime > _dispatchDeadline};
private _dispatchOk = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "dispatching"
    && {(_aircraft getVariable ["YSF_transport_taskId", ""]) isNotEqualTo ""};
["vigil.transport.client.dispatch", _dispatchOk, format ["state=%1|task=%2|destination=%3", _aircraft getVariable ["YSF_transport_state", ""], _aircraft getVariable ["YSF_transport_taskId", ""], _state get "grid"]] call _assert;
call YOSHI_taskTRN_submit;

private _waitingDeadline = diag_tickTime + 210;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_WAITING"} || diag_tickTime > _waitingDeadline};
private _waiting = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_WAITING", []];
private _waitingOk = (_waiting param [0, ""]) isEqualTo _token
    && {(_waiting param [1, ""]) isEqualTo _aircraftId}
    && {(_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "waiting"};
["vigil.transport.client.waiting", _waitingOk, format ["signal=%1|state=%2", _waiting, _aircraft getVariable ["YSF_transport_state", ""]]] call _assert;
call YOSHI_taskTRN_rtb;
private _rtbDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "returning" || diag_tickTime > _rtbDeadline};
private _rtbOk = (_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "returning"
    && {count (_aircraft getVariable ["YSF_transport_homeATL", []]) >= 2};
["vigil.transport.client.rtb", _rtbOk, format ["state=%1|home=%2", _aircraft getVariable ["YSF_transport_state", ""], _aircraft getVariable ["YSF_transport_homeATL", []]]] call _assert;

private _homeDeadline = diag_tickTime + 210;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_HOME"} || diag_tickTime > _homeDeadline};
private _homeSignal = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_HOME", []];
private _homeSeen = (_homeSignal param [0, ""]) isEqualTo _token
    && {(_homeSignal param [1, ""]) isEqualTo _aircraftId}
    && {(_aircraft getVariable ["YSF_transport_state", ""]) isEqualTo "home"};
["vigil.transport.client.home", _homeSeen, format ["signal=%1|state=%2|aircraft=%3", _homeSignal, _aircraft getVariable ["YSF_transport_state", ""], _aircraftId]] call _assert;
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-helicopter-transport",
        "fixture": "server-local-crewed-B_Heli_Light_01_F",
        "flight_corridor": "Stratis [1900,5600] to [2350,5600]",
        "ui_path": "YOSHI_taskTRN_submit/YOSHI_taskTRN_rtb",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A valid selected transport accepts one dispatch, physically flies to and settles at the selected LZ, waits, accepts RTB, physically returns and settles at its recorded home, then leaves no active task or fixture resources.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Review found missing RTB/state/timeout semantics and false-positive landing checks; the refined contract asserts the user path plus independent physical evidence without freezing private waypoint mechanics.",
        dependencies=("Vigil task governor", "Arma helicopter AI", "CBA", "Tribunal aviation observer"),
        evidence_types=frozenset({"client-request", "locality", "trajectory", "ground-contact", "settling", "task-state", "cleanup"}),
        locality_requirements="Client-a owns Vigil UI/request state; the dedicated server owns aircraft, pilot group, waypoints, task execution, and authoritative world state.",
    ),
)
