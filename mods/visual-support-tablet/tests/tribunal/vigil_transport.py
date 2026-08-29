"""Physical Tier 3 contract for Vigil helicopter dispatch and RTB."""

from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


TRANSPORT_FIXTURE = [
    "vigil.transport.fixture",
    "vigil.transport.locality",
    "vigil.transport.client.locality",
    "vigil.transport.client.eligible",
]
TRANSPORT_DISPATCH = [
    "vigil.transport.dispatch.accepted",
    "vigil.transport.dispatch.duplicateRejected",
    "vigil.transport.dispatch.flight",
    "vigil.transport.client.dispatch",
]
TRANSPORT_ARRIVAL = [
    "vigil.transport.arrival",
    "vigil.transport.waiting",
    "vigil.transport.client.waiting",
]
TRANSPORT_RTB = [
    "vigil.transport.rtb.accepted",
    "vigil.transport.rtb.flight",
    "vigil.transport.home",
    "vigil.transport.client.rtb",
    "vigil.transport.client.home",
]
TRANSPORT_NORMAL_CLOSEOUT = [
    "vigil.transport.stabilizer.deferred",
    "vigil.transport.cleanup",
]
TRANSPORT_ABNORMAL_FIXTURE = [
    "vigil.transport.abnormal.fixture",
]
TRANSPORT_ABNORMAL_STIMULUS = [
    "vigil.transport.abnormal.destruction",
    "vigil.transport.client.abnormalDispatch",
]
TRANSPORT_ABNORMAL_TERMINAL = [
    "vigil.transport.abnormal.terminal",
    "vigil.transport.abnormal.padCleanup",
    "vigil.transport.client.abnormalFailure",
]
TRANSPORT_ABNORMAL_CLOSEOUT = [
    "vigil.transport.abnormal.cleanup",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-transport",
        "version": 1,
        "feature_family": "pontifex-vigil-transport",
        "name": "Vigil bounded helicopter transport lifecycle",
        "definition": {
            "kind": "controlled dedicated-multiplayer product specification",
            "reference": "mods/visual-support-tablet/tests/tribunal/vigil_transport.py",
            "applicability": "Arma 3 dedicated multiplayer with one authenticated client, server-local B_Heli_Light_01_F fixtures, and bounded clear Stratis corridors",
            "participants": {
                "server": "owns aircraft, crews, task governor, physical flight, product landing pads, destruction stimulus, and cleanup",
                "client-a": "owns the real Vigil request path and observes nonlocal task, aircraft, failure, and pad identity replication",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:helicopter-transport",
        "label": "Vigil helicopter transport lifecycle",
        "kind": "product_behavior",
        "aliases": ["Vigil transport", "Vigil reinsertion"],
        "biki_context": ["biki-page:1766", "biki-page:1378", "biki-page:1601"],
    },
    "arms": [
        {"key": "normal-fixture", "role": "baseline", "description": "A server-local crewed representative transport is eligible and resolves nonlocally on client-a", "assertions": TRANSPORT_FIXTURE},
        {"key": "normal-dispatch", "role": "treatment", "description": "The real client request accepts one outbound task, rejects a duplicate, and produces attributable physical flight", "assertions": TRANSPORT_DISPATCH},
        {"key": "normal-arrival", "role": "treatment", "description": "The exact transport settles at the LZ and remains available", "assertions": TRANSPORT_ARRIVAL},
        {"key": "normal-rtb", "role": "treatment", "description": "The real RTB request produces a distinct task and physical return to the recorded home", "assertions": TRANSPORT_RTB},
        {"key": "normal-closeout", "role": "treatment", "description": "The disabled stabilizer remains absent and normal fixtures and governor activity retire", "assertions": TRANSPORT_NORMAL_CLOSEOUT},
        {"key": "abnormal-fixture", "role": "baseline", "description": "A second exact server-local transport begins alive with no destination pad and is submitted through the same client path", "assertions": TRANSPORT_ABNORMAL_FIXTURE},
        {"key": "abnormal-destruction", "role": "treatment", "description": "After the exact task reaches its landing stage and creates its sole product pad while still airborne, server-local setDamage destroys the exact aircraft", "assertions": TRANSPORT_ABNORMAL_STIMULUS},
        {"key": "abnormal-terminal", "role": "treatment", "description": "The same generation finalizes failed, disables its governor record, deletes its exact product-created pad, and replicates failure to client-a", "assertions": TRANSPORT_ABNORMAL_TERMINAL},
        {"key": "abnormal-closeout", "role": "treatment", "description": "Controlled teardown removes the wreck, crew group, home pad, signals, and remaining exact fixture identities", "assertions": TRANSPORT_ABNORMAL_CLOSEOUT},
    ],
    "causal_relationships": [
        {"key": "normal-v-destroyed-terminal", "relation": "CAUSAL_PAIR_WITH", "source": "normal-arrival", "target": "abnormal-destruction", "controlled_dimensions": ["aircraft class", "server locality", "authenticated client request", "clear corridor", "product task governor", "destruction is the varied dimension"]},
        {"key": "destruction-v-finalizer", "relation": "CAUSAL_PAIR_WITH", "source": "abnormal-destruction", "target": "abnormal-terminal", "controlled_dimensions": ["exact aircraft", "exact task id and generation", "exact product-created pad", "mission"]},
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:transport-bounded-round-trip",
            "text": "Under the tested dedicated-multiplayer conditions, Vigil accepts one authenticated dispatch for an eligible server-local helicopter, rejects an active duplicate, physically reaches and settles at the LZ, waits, accepts RTB, and physically returns and settles at its recorded home with no active task or fixture resources.",
            "intended_use": "primary_result",
            "assertions": TRANSPORT_FIXTURE + TRANSPORT_DISPATCH + TRANSPORT_ARRIVAL + TRANSPORT_RTB + TRANSPORT_NORMAL_CLOSEOUT,
            "rationale": "Exact request, aircraft, task, trajectory, landing, waiting, return, locality, and cleanup observations exclude state-only completion, unrelated flight, duplicate replacement, and leaked-fixture false passes.",
        },
        {
            "id": "pontifex:vigil:transport-in-flight-destruction-cleanup",
            "text": "Under the tested server-local conditions, destroying the exact active transport after its task creates a landing pad but before landing causes the same task generation to finalize failed, disables its governor record, deletes its exact product-created pad, and replicates the failed terminal state to client-a.",
            "intended_use": "primary_result",
            "assertions": TRANSPORT_ABNORMAL_FIXTURE + TRANSPORT_ABNORMAL_STIMULUS + TRANSPORT_ABNORMAL_TERMINAL + TRANSPORT_ABNORMAL_CLOSEOUT,
            "rationale": "The client submits through the real request path; exact pre-destruction aircraft/task/pad identities are acknowledged while live and airborne; server-local damage is the causal stimulus; exact generation, finalization, manager disablement, pad null transition, client replication, and cleanup exclude timeout, controlled pad deletion, and unrelated-task false passes.",
        },
    ],
    "unresolved": [
        "Remote cancellation policy, destruction before pad creation, crew-only death, RTB destruction, retry exhaustion, client-owned/headless aircraft, ownership migration, client-B/JIP, and disconnect remain outside this one abnormal terminal proof.",
        "Other helicopter classes, terrain, landing commands, destination-pad reuse, and presentation remain reviewed optional or decision-bound combinations.",
    ],
}


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
        "vigil.transport.stabilizer.deferred",
        "vigil.transport.abnormal.fixture",
        "vigil.transport.abnormal.destruction",
        "vigil.transport.abnormal.terminal",
        "vigil.transport.abnormal.padCleanup",
        "vigil.transport.abnormal.cleanup",
    }),
    client_expected=frozenset({
        "vigil.transport.client.locality",
        "vigil.transport.client.eligible",
        "vigil.transport.client.dispatch",
        "vigil.transport.client.waiting",
        "vigil.transport.client.rtb",
        "vigil.transport.client.home",
        "vigil.transport.client.abnormalDispatch",
        "vigil.transport.client.abnormalFailure",
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
private _stabilizerSeen = false;
missionNamespace setVariable ["TRIBUNAL_VIGIL_STABILIZER_SEEN", false];
private _stabilizerMonitor = [{
    params ["_args"];
    _args params ["_observed", "_seenRef"];
    if (_observed in YSF_STABILIZE_HELICOPTERS || {YSF_helicopterStab_helicopterDecel findIf {(_x # 0) isEqualTo _observed} > -1}) then {
        missionNamespace setVariable [_seenRef, true];
    };
}, 0.05, [_aircraft, "TRIBUNAL_VIGIL_STABILIZER_SEEN"]] call CBA_fnc_addPerFrameHandler;

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

[_stabilizerMonitor] call CBA_fnc_removePerFrameHandler;
_stabilizerSeen = missionNamespace getVariable ["TRIBUNAL_VIGIL_STABILIZER_SEEN", false];
private _stabilizerClean = !_stabilizerSeen && {!(_aircraft in YSF_STABILIZE_HELICOPTERS)}
    && {YSF_helicopterStab_helicopterDecel findIf {(_x # 0) isEqualTo _aircraft} < 0}
    && {isNil {_aircraft getVariable "YSF_helicopterStab_speedAlt"}};
["vigil.transport.stabilizer.deferred", _stabilizerClean, format ["seen=%1|registered=%2|active=%3|sample=%4", _stabilizerSeen, _aircraft in YSF_STABILIZE_HELICOPTERS, YSF_helicopterStab_helicopterDecel findIf {(_x # 0) isEqualTo _aircraft}, _aircraft getVariable ["YSF_helicopterStab_speedAlt", []]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_STABILIZER_SEEN", nil];
private _manager = (call YSF__mgr) getOrDefault [[_aircraft] call YSF_taskKey, objNull];
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

private _abnormalHome = [1900, 5600, 0];
private _abnormalDestination = [2350, 5600, 0];
private _abnormalPadsBefore = allMissionObjects "Land_HelipadEmpty_F";
private _abnormalHomePad = "Land_HelipadEmpty_F" createVehicle _abnormalHome;
private _abnormalAircraft = "B_Heli_Light_01_F" createVehicle _abnormalHome;
_abnormalAircraft setDir 90;
_abnormalAircraft setFuel 1;
_abnormalAircraft setDamage 0;
createVehicleCrew _abnormalAircraft;
private _abnormalSetupDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.1;
    (!isNull driver _abnormalAircraft && {alive driver _abnormalAircraft} && {isTouchingGround _abnormalAircraft})
        || diag_tickTime > _abnormalSetupDeadline
};
private _abnormalPilot = driver _abnormalAircraft;
private _abnormalGroup = group _abnormalPilot;
private _abnormalAircraftId = netId _abnormalAircraft;
private _abnormalFixtureOk = !isNull _abnormalAircraft && {alive _abnormalAircraft}
    && {!isNull _abnormalPilot} && {alive _abnormalPilot}
    && {local _abnormalAircraft} && {local _abnormalPilot} && {local _abnormalGroup}
    && {_abnormalAircraftId isNotEqualTo ""}
    && {_abnormalPadsBefore findIf {_x distance2D _abnormalDestination < 100} < 0};
["vigil.transport.abnormal.fixture", _abnormalFixtureOk, format ["aircraft=%1|pilot=%2|local=%3|home=%4|destination=%5|nearbyPadsBefore=%6", _abnormalAircraftId, netId _abnormalPilot, local _abnormalAircraft, _abnormalHome, _abnormalDestination, _abnormalPadsBefore select {_x distance2D _abnormalDestination < 100}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FIXTURE", [_token, _abnormalAircraftId, _abnormalHome, _abnormalDestination], true];

private _abnormalTask = objNull;
private _abnormalManager = objNull;
private _abnormalPad = objNull;
private _abnormalArmedDeadline = diag_tickTime + 210;
waitUntil {
    uiSleep 0.1;
    _abnormalManager = (call YSF__mgr) getOrDefault [[_abnormalAircraft] call YSF_taskKey, objNull];
    if (typeName _abnormalManager isEqualTo "HASHMAP") then {
        _abnormalTask = _abnormalManager getOrDefault ["task", objNull];
        if (typeName _abnormalTask isEqualTo "HASHMAP") then {
            _abnormalPad = _abnormalTask getOrDefault ["lzPad", objNull];
        };
    };
    (typeName _abnormalTask isEqualTo "HASHMAP"
        && {(_abnormalTask getOrDefault ["stage", -1]) isEqualTo 3}
        && {!isNull _abnormalPad})
        || diag_tickTime > _abnormalArmedDeadline
};
private _abnormalTaskId = if (typeName _abnormalTask isEqualTo "HASHMAP") then {_abnormalTask getOrDefault ["id", ""]} else {""};
private _abnormalTaskGen = if (typeName _abnormalTask isEqualTo "HASHMAP") then {_abnormalTask getOrDefault ["gen", -1]} else {-1};
private _abnormalPadId = if (isNull _abnormalPad) then {""} else {netId _abnormalPad};
private _abnormalAirborne = alive _abnormalAircraft && {!isTouchingGround _abnormalAircraft}
    && {((getPosATL _abnormalAircraft) # 2) > 3};
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_ARMED", [_token, _abnormalAircraftId, _abnormalTaskId, _abnormalTaskGen, _abnormalPadId], true];
private _abnormalAckDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED", ""]) isEqualTo _token
        || diag_tickTime > _abnormalAckDeadline
};
private _abnormalPreconditions = typeName _abnormalTask isEqualTo "HASHMAP"
    && {_abnormalTaskId isNotEqualTo ""} && {_abnormalTaskGen >= 0}
    && {(_abnormalTask getOrDefault ["stage", -1]) isEqualTo 3}
    && {!isNull _abnormalPad} && {_abnormalPadId isNotEqualTo ""}
    && {!(_abnormalPad in _abnormalPadsBefore)}
    && {_abnormalTask getOrDefault ["deletePadOnFinish", false]}
    && {_abnormalAirborne}
    && {(missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED", ""]) isEqualTo _token};
_abnormalAircraft setDamage 1;
private _destroyDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; !alive _abnormalAircraft || diag_tickTime > _destroyDeadline};
private _destroyed = !alive _abnormalAircraft && {damage _abnormalAircraft >= 1};
["vigil.transport.abnormal.destruction", _abnormalPreconditions && {_destroyed}, format ["aircraft=%1|task=%2|gen=%3|stage=%4|pad=%5|productPad=%6|airborne=%7|alt=%8|touching=%9|clientArmed=%10|alive=%11|damage=%12", _abnormalAircraftId, _abnormalTaskId, _abnormalTaskGen, if (typeName _abnormalTask isEqualTo "HASHMAP") then {_abnormalTask getOrDefault ["stage", -1]} else {-1}, _abnormalPadId, !(_abnormalPad in _abnormalPadsBefore), _abnormalAirborne, (getPosATL _abnormalAircraft) # 2, isTouchingGround _abnormalAircraft, missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED", ""], alive _abnormalAircraft, damage _abnormalAircraft]] call _assert;

private _abnormalTerminalDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (typeName _abnormalTask isEqualTo "HASHMAP"
        && {_abnormalTask getOrDefault ["finalized", false]}
        && {!(_abnormalManager getOrDefault ["enabled", true])})
        || diag_tickTime > _abnormalTerminalDeadline
};
private _abnormalTerminalOk = typeName _abnormalTask isEqualTo "HASHMAP"
    && {(_abnormalTask getOrDefault ["id", ""]) isEqualTo _abnormalTaskId}
    && {(_abnormalTask getOrDefault ["gen", -1]) isEqualTo _abnormalTaskGen}
    && {(_abnormalTask getOrDefault ["state", ""]) isEqualTo "failed"}
    && {(_abnormalTask getOrDefault ["status", ""]) isEqualTo "failed"}
    && {_abnormalTask getOrDefault ["finalized", false]}
    && {(_abnormalTask getOrDefault ["stage", -1]) isEqualTo 5}
    && {!(_abnormalManager getOrDefault ["enabled", true])}
    && {(_abnormalAircraft getVariable ["YSF_transport_state", ""]) isEqualTo "failed"};
["vigil.transport.abnormal.terminal", _abnormalTerminalOk, format ["aircraft=%1|task=%2|gen=%3|state=%4|status=%5|stage=%6|finalized=%7|managerEnabled=%8|vehicleState=%9", _abnormalAircraftId, _abnormalTask getOrDefault ["id", ""], _abnormalTask getOrDefault ["gen", -1], _abnormalTask getOrDefault ["state", ""], _abnormalTask getOrDefault ["status", ""], _abnormalTask getOrDefault ["stage", -1], _abnormalTask getOrDefault ["finalized", false], _abnormalManager getOrDefault ["enabled", true], _abnormalAircraft getVariable ["YSF_transport_state", ""]]] call _assert;
private _padCleanupOk = isNull _abnormalPad
    && {objectFromNetId _abnormalPadId isEqualTo objNull}
    && {isNull (_abnormalTask getOrDefault ["lzPad", objNull])}
    && {(allMissionObjects "Land_HelipadEmpty_F") findIf {netId _x isEqualTo _abnormalPadId} < 0};
["vigil.transport.abnormal.padCleanup", _padCleanupOk, format ["pad=%1|null=%2|resolvedNull=%3|taskPadNull=%4|matching=%5", _abnormalPadId, isNull _abnormalPad, objectFromNetId _abnormalPadId isEqualTo objNull, isNull (_abnormalTask getOrDefault ["lzPad", objNull]), (allMissionObjects "Land_HelipadEmpty_F") findIf {netId _x isEqualTo _abnormalPadId}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FAILED", [_token, _abnormalAircraftId, _abnormalTaskId, _abnormalTaskGen, _abnormalPadId], true];
private _abnormalClientTerminalDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_TERMINAL", ""]) isEqualTo _token
        || diag_tickTime > _abnormalClientTerminalDeadline
};

private _abnormalCrewIds = (crew _abnormalAircraft) apply {netId _x};
deleteVehicleCrew _abnormalAircraft;
deleteVehicle _abnormalAircraft;
deleteVehicle _abnormalHomePad;
if (!isNull _abnormalGroup) then {deleteGroup _abnormalGroup;};
private _abnormalCleanupDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    isNull _abnormalAircraft && {isNull _abnormalHomePad}
        && {_abnormalCrewIds findIf {!isNull objectFromNetId _x} < 0}
        || diag_tickTime > _abnormalCleanupDeadline
};
private _abnormalCleanupOk = isNull _abnormalAircraft && {isNull _abnormalHomePad}
    && {isNull _abnormalPad}
    && {_abnormalCrewIds findIf {!isNull objectFromNetId _x} < 0}
    && {(allMissionObjects "B_Heli_Light_01_F") findIf {netId _x isEqualTo _abnormalAircraftId} < 0};
["vigil.transport.abnormal.cleanup", _abnormalCleanupOk, format ["aircraft=%1|null=%2|homePadNull=%3|productPadNull=%4|crewRemaining=%5|matchingAircraft=%6", _abnormalAircraftId, isNull _abnormalAircraft, isNull _abnormalHomePad, isNull _abnormalPad, _abnormalCrewIds select {!isNull objectFromNetId _x}, (allMissionObjects "B_Heli_Light_01_F") findIf {netId _x isEqualTo _abnormalAircraftId}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLEANED", [_token, _abnormalAircraftId, _abnormalTaskId, _abnormalTaskGen, _abnormalPadId], true];
private _abnormalClientCleanedDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_CLEANED", ""]) isEqualTo _token
        || diag_tickTime > _abnormalClientCleanedDeadline
};
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FIXTURE", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_ARMED", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FAILED", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLEANED", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_TERMINAL", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_CLEANED", nil, true];
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
_state set ["do_not_climb", false];
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

private _abnormalFixtureDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FIXTURE"} || diag_tickTime > _abnormalFixtureDeadline};
private _abnormalFixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FIXTURE", []];
private _abnormalAircraftId = _abnormalFixture param [1, ""];
private _abnormalAircraft = if (_abnormalAircraftId isEqualTo "") then {objNull} else {objectFromNetId _abnormalAircraftId};
private _abnormalDestination = _abnormalFixture param [3, []];
uiNamespace setVariable ["YSF_current_selected_asset", _abnormalAircraft];
private _abnormalState = call YOSHI_taskTransport_GetState;
_abnormalState set ["grid", _abnormalDestination];
_abnormalState set ["alt", 20];
_abnormalState set ["do_not_climb", false];
_abnormalState set ["ignore_en", false];
uiNamespace setVariable ["YOSHI_taskTransport_state", _abnormalState];
call YOSHI_taskTRN_submit;
private _abnormalArmedDeadline = diag_tickTime + 210;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_ARMED"} || diag_tickTime > _abnormalArmedDeadline};
private _abnormalArmed = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_ARMED", []];
private _abnormalTaskId = _abnormalArmed param [2, ""];
private _abnormalTaskGen = _abnormalArmed param [3, -1];
private _abnormalPadId = _abnormalArmed param [4, ""];
private _abnormalPad = if (_abnormalPadId isEqualTo "") then {objNull} else {objectFromNetId _abnormalPadId};
private _abnormalReplicaDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    _abnormalAircraft = objectFromNetId _abnormalAircraftId;
    _abnormalPad = objectFromNetId _abnormalPadId;
    (!isNull _abnormalAircraft && {!isNull _abnormalPad} && {alive _abnormalAircraft}
        && {!isTouchingGround _abnormalAircraft} && {((getPosATL _abnormalAircraft) # 2) > 3})
        || diag_tickTime > _abnormalReplicaDeadline
};
private _abnormalDispatchOk = (_abnormalArmed param [0, ""]) isEqualTo _token
    && {(_abnormalArmed param [1, ""]) isEqualTo _abnormalAircraftId}
    && {!isNull _abnormalAircraft} && {!local _abnormalAircraft} && {alive _abnormalAircraft}
    && {!isTouchingGround _abnormalAircraft} && {((getPosATL _abnormalAircraft) # 2) > 3}
    && {_abnormalTaskId isNotEqualTo ""} && {_abnormalTaskGen >= 0}
    && {!isNull _abnormalPad};
["vigil.transport.client.abnormalDispatch", _abnormalDispatchOk, format ["aircraft=%1|local=%2|alive=%3|touching=%4|alt=%5|task=%6|gen=%7|pad=%8|padNull=%9", _abnormalAircraftId, if (isNull _abnormalAircraft) then {false} else {local _abnormalAircraft}, if (isNull _abnormalAircraft) then {false} else {alive _abnormalAircraft}, if (isNull _abnormalAircraft) then {true} else {isTouchingGround _abnormalAircraft}, if (isNull _abnormalAircraft) then {-1} else {(getPosATL _abnormalAircraft) # 2}, _abnormalTaskId, _abnormalTaskGen, _abnormalPadId, isNull _abnormalPad]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED", _token, true];

private _abnormalFailedDeadline = diag_tickTime + 45;
private _abnormalResultRows = [];
waitUntil {
    uiSleep 0.05;
    _abnormalResultRows = uiNamespace getVariable ["YSF_task_request_results", []];
    (!isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FAILED"}
        && {_abnormalResultRows findIf {(_x # 1) isEqualTo "terminal" && {(_x # 4) isEqualTo _abnormalTaskId} && {(_x # 5) isEqualTo "failed"}} >= 0})
        || diag_tickTime > _abnormalFailedDeadline
};
private _abnormalFailed = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_FAILED", []];
private _abnormalTerminalRows = _abnormalResultRows select {(_x # 1) isEqualTo "terminal" && {(_x # 4) isEqualTo _abnormalTaskId} && {(_x # 5) isEqualTo "failed"}};
private _abnormalReceiptOk = (_abnormalFailed param [0, ""]) isEqualTo _token
    && {(_abnormalFailed param [1, ""]) isEqualTo _abnormalAircraftId}
    && {(_abnormalFailed param [2, ""]) isEqualTo _abnormalTaskId}
    && {(_abnormalFailed param [3, -1]) isEqualTo _abnormalTaskGen}
    && {(_abnormalFailed param [4, ""]) isEqualTo _abnormalPadId}
    && {(count _abnormalTerminalRows) isEqualTo 1};
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_TERMINAL", _token, true];
private _abnormalCleanedDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLEANED"} || diag_tickTime > _abnormalCleanedDeadline};
private _abnormalCleaned = missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLEANED", []];
private _abnormalFailureOk = _abnormalReceiptOk
    && {(_abnormalCleaned param [0, ""]) isEqualTo _token}
    && {(_abnormalCleaned param [1, ""]) isEqualTo _abnormalAircraftId}
    && {(_abnormalCleaned param [2, ""]) isEqualTo _abnormalTaskId}
    && {(_abnormalCleaned param [3, -1]) isEqualTo _abnormalTaskGen}
    && {(_abnormalCleaned param [4, ""]) isEqualTo _abnormalPadId}
    && {isNull objectFromNetId _abnormalAircraftId}
    && {isNull objectFromNetId _abnormalPadId};
["vigil.transport.client.abnormalFailure", _abnormalFailureOk, format ["signal=%1|cleaned=%2|aircraft=%3|aircraftNull=%4|task=%5|gen=%6|terminalRows=%7|pad=%8|padNull=%9", _abnormalFailed, _abnormalCleaned, _abnormalAircraftId, isNull objectFromNetId _abnormalAircraftId, _abnormalTaskId, _abnormalTaskGen, _abnormalTerminalRows, _abnormalPadId, isNull objectFromNetId _abnormalPadId]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_CLEANED", _token, true];
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
        behavior_contract="A valid selected transport accepts one dispatch, physically flies to and settles at the selected LZ, waits, accepts RTB, physically returns and settles at its recorded home, then leaves no active task or fixture resources. If the exact transport is destroyed after its task creates a landing pad but before landing, the same task generation finalizes failed, disables its governor record, deletes that exact product pad, and replicates failure.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The accepted normal round trip is retained. A second causal arm uses the same real client request and server-local class/corridor, acknowledges the exact active task and product pad while airborne, then varies only exact-aircraft destruction and proves terminal generation, governor, pad, replication, and fixture cleanup.",
        dependencies=("Vigil task governor", "Arma helicopter AI", "CBA", "Tribunal aviation observer"),
        evidence_types=frozenset({"client-request", "locality", "trajectory", "ground-contact", "settling", "exact-identity", "destruction-stimulus", "task-state", "replication", "cleanup"}),
        locality_requirements="Client-a owns Vigil UI/request state; the dedicated server owns aircraft, pilot group, waypoints, task execution, and authoritative world state.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
