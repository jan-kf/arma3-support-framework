"""Bounded physical characterization of Vigil's hidden-pad landing mechanism."""

from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.runner.model import CharacterizedBehavior, Scenario, ScenarioReview


CONTROL_ASSERTIONS = ["vigil.transport.padAB.fixture", "vigil.transport.padAB.control"]
TREATMENT_ASSERTIONS = ["vigil.transport.padAB.treatment"]
CLOSEOUT_ASSERTIONS = [
    "vigil.transport.padAB.comparison",
    "vigil.transport.padAB.cleanup",
    "vigil.transport.padAB.clientComplete",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-transport-pad-ab",
        "version": 1,
        "feature_family": "pontifex-vigil-helicopter-transport",
        "name": "Vigil hidden-pad landing characterization",
        "definition": {
            "kind": "controlled dedicated-multiplayer landing characterization",
            "reference": "mods/visual-support-tablet/tests/tribunal/vigil_transport_pad_ab.py",
            "applicability": "Arma 3 2.22 dedicated multiplayer; server-local B_Heli_Light_01_F; clear Stratis corridor",
            "participants": {
                "server": "aircraft/group authority, matched landing arms, physical observation, and cleanup",
                "client-a": "replicated bounded-completion observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:hidden-pad-landing",
        "label": "Vigil hidden-pad helicopter landing",
        "kind": "product_behavior",
        "aliases": ["Vigil transport landing pad"],
        "biki_context": ["arma:createvehicle"],
    },
    "arms": [
        {
            "key": "landing_without_pad",
            "role": "negative_control",
            "description": "An airborne server-local helicopter uses doMove then LAND with no destination pad within 100 m",
            "assertions": CONTROL_ASSERTIONS,
        },
        {
            "key": "landing_with_hidden_pad",
            "role": "treatment",
            "description": "The matched helicopter uses the same sequence with one exact Land_HelipadEmpty_F at destination",
            "assertions": TREATMENT_ASSERTIONS,
        },
        {
            "key": "closeout",
            "role": "treatment",
            "description": "The causal contrast, exact cleanup, and replicated completion close",
            "assertions": CLOSEOUT_ASSERTIONS,
        },
    ],
    "causal_relationships": [
        {
            "key": "hidden-pad-v-no-pad",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "landing_with_hidden_pad",
            "target": "landing_without_pad",
            "controlled_dimensions": [
                "aircraft class", "server locality", "airborne start pose",
                "pilot creation", "doMove destination", "LAND command",
                "terrain", "weather", "landing deadline",
            ],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:hidden-pad-landing-requirement",
            "text": "For the tested server-local B_Heli_Light_01_F airborne approach on clear Stratis terrain, doMove followed by LAND settles within 25 m only with one exact Land_HelipadEmpty_F at destination; the matched no-pad control remains airborne beyond 50 m at the bounded deadline.",
            "intended_use": "characterization",
            "assertions": CONTROL_ASSERTIONS + TREATMENT_ASSERTIONS + CLOSEOUT_ASSERTIONS,
            "rationale": "The arms share class, locality, start pose, pilot setup, destination, commands, terrain, weather and deadlines. Pad census, sampled flight, continuous settling, spatial bounds and exact cleanup isolate pad presence.",
        },
    ],
    "unresolved": [
        "Other helicopter classes, terrain/slope/obstacles, approach geometries, landing modes, waypoint-only approaches, ownership migration, client-B and JIP remain outside this characterization."
    ],
}

SERVER_SQF = aviation_observer_sqf() + r'''
private _padABStart = [2000, 5200, 50];
private _padABDestination = [2350, 5200, 0];
private _runPadArm = {
    params ["_withDestinationPad"];
    private _destinationPad = objNull;
    if (_withDestinationPad) then {
        _destinationPad = "Land_HelipadEmpty_F" createVehicle _padABDestination;
    };
    private _padsBefore = nearestObjects [_padABDestination, ["Land_HelipadEmpty_F"], 100];
    private _aircraft = createVehicle ["B_Heli_Light_01_F", _padABStart, [], 0, "FLY"];
    _aircraft setDir 90;
    _aircraft setFuel 1;
    _aircraft setDamage 0;
    _aircraft setPosATL _padABStart;
    createVehicleCrew _aircraft;
    _aircraft engineOn true;
    private _setupDeadline = diag_tickTime + 15;
    waitUntil {
        uiSleep 0.1;
        (!isNull driver _aircraft && {alive driver _aircraft} && {(getPosATL _aircraft # 2) > 10} && {isEngineOn _aircraft})
            || diag_tickTime > _setupDeadline
    };
    private _pilot = driver _aircraft;
    private _group = if (isNull _pilot) then {grpNull} else {group _pilot};
    private _aircraftId = netId _aircraft;
    private _pilotId = if (isNull _pilot) then {""} else {netId _pilot};
    private _fixtureOk = !isNull _aircraft && {alive _aircraft} && {!isNull _pilot}
        && {alive _pilot} && {local _aircraft} && {local _pilot} && {local _group}
        && {(getPosATL _aircraft # 2) > 10} && {isEngineOn _aircraft} && {canMove _aircraft};
    private _start = getPosATL _aircraft;
    [_aircraft, true] call YSF_fnc_setVehicleEngineState;
    _aircraft flyInHeight 20;
    [_aircraft] call YSF_fnc_setVehicleTransitAI;
    [_aircraft, "NONE"] call YSF_fnc_setVehicleLandMode;
    (driver _aircraft) doMove _padABDestination;
    private _approachSamples = [_aircraft, _padABDestination, {
        params ["_observed"];
        (_observed distance2D _padABDestination) <= YSF_TRX_ARRIVAL_RADIUS
    }, 90, 0.5] call TRIBUNAL_fnc_observeFlight;
    [_aircraft, "LAND"] call YSF_fnc_setVehicleLandMode;
    private _landingSamples = [];
    private _landingDeadline = diag_tickTime + 90;
    private _groundSince = -1;
    waitUntil {
        _landingSamples pushBack ([_aircraft, _padABDestination] call TRIBUNAL_fnc_aviationSample);
        private _landedNow = isTouchingGround _aircraft && {unitReady _aircraft}
            && {(vectorMagnitude velocity _aircraft) < 2};
        if (_landedNow) then {
            if (_groundSince < 0) then {_groundSince = diag_tickTime;};
        } else {
            _groundSince = -1;
        };
        uiSleep 0.5;
        (_groundSince >= 0 && {(diag_tickTime - _groundSince) >= 3})
            || {diag_tickTime > _landingDeadline}
    };
    _approachSamples append _landingSamples;
    private _evidence = [_approachSamples, _start, _padABDestination] call TRIBUNAL_fnc_flightEvidence;
    private _settledPosition = getPosATL _aircraft;
    uiSleep 1;
    private _distance = _aircraft distance2D _padABDestination;
    private _stable = _groundSince >= 0 && {(diag_tickTime - _groundSince) >= 3}
        && {alive _aircraft} && {damage _aircraft < 0.5}
        && {isTouchingGround _aircraft} && {unitReady _aircraft}
        && {(vectorMagnitude velocity _aircraft) < 2}
        && {_aircraft distance2D _settledPosition < 3};
    private _success = _fixtureOk
        && {_evidence getOrDefault ["moved", false]}
        && {_evidence getOrDefault ["approached", false]}
        && {_evidence getOrDefault ["maximumAltitudeATL", 0] > 5}
        && {_distance < 25} && {_stable};
    private _result = createHashMapFromArray [
        ["withPad", _withDestinationPad], ["fixture", _fixtureOk],
        ["aircraft", _aircraftId], ["pilot", _pilotId],
        ["padsBefore", count _padsBefore], ["padExact", _destinationPad in _padsBefore],
        ["samples", _evidence getOrDefault ["samples", 0]],
        ["minimumDistance", _evidence getOrDefault ["minimumDistance", -1]],
        ["maximumTravel", _evidence getOrDefault ["maximumTravel", -1]],
        ["maximumAltitude", _evidence getOrDefault ["maximumAltitudeATL", -1]],
        ["moved", _evidence getOrDefault ["moved", false]],
        ["approached", _evidence getOrDefault ["approached", false]],
        ["landedSample", _evidence getOrDefault ["landed", false]],
        ["distance", _distance], ["drift", _aircraft distance2D _settledPosition],
        ["touching", isTouchingGround _aircraft], ["ready", unitReady _aircraft],
        ["speed", vectorMagnitude velocity _aircraft], ["damage", damage _aircraft],
        ["stable", _stable], ["engineOn", isEngineOn _aircraft], ["canMove", canMove _aircraft], ["success", _success]
    ];
    deleteVehicleCrew _aircraft;
    deleteVehicle _aircraft;
    if (!isNull _destinationPad) then {deleteVehicle _destinationPad;};
    if (!isNull _group) then {deleteGroup _group;};
    uiSleep 2;
    _result set ["cleanup", isNull _aircraft && {isNull _destinationPad}];
    _result
};

private _padABFixture = (nearestObjects [_padABDestination, ["Land_HelipadEmpty_F"], 100]) isEqualTo [];
["vigil.transport.padAB.fixture", _padABFixture, format ["start=%1|destination=%2|destinationPads=%3", _padABStart, _padABDestination, nearestObjects [_padABDestination, ["Land_HelipadEmpty_F"], 100]]] call _assert;
private _padABControl = [false] call _runPadArm;
private _controlOk = !(_padABControl getOrDefault ["success", true])
    && {_padABControl getOrDefault ["fixture", false]}
    && {_padABControl getOrDefault ["moved", false]}
    && {(_padABControl getOrDefault ["minimumDistance", 1e9]) < YSF_TRX_ARRIVAL_RADIUS}
    && {!(_padABControl getOrDefault ["stable", true])}
    && {(_padABControl getOrDefault ["distance", 0]) > 50}
    && {(_padABControl getOrDefault ["padsBefore", -1]) isEqualTo 0}
    && {!(_padABControl getOrDefault ["padExact", true])};
["vigil.transport.padAB.control", _controlOk, str _padABControl] call _assert;
private _padABTreatment = [true] call _runPadArm;
private _treatmentOk = (_padABTreatment getOrDefault ["success", false])
    && {(_padABTreatment getOrDefault ["padsBefore", -1]) isEqualTo 1}
    && {_padABTreatment getOrDefault ["padExact", false]};
["vigil.transport.padAB.treatment", _treatmentOk, str _padABTreatment] call _assert;
private _comparisonOk = _controlOk && {_treatmentOk}
    && {(_padABControl getOrDefault ["distance", 0]) > 50}
    && {(_padABTreatment getOrDefault ["distance", 1e9]) < 25};
["vigil.transport.padAB.comparison", _comparisonOk, format ["control=%1|treatment=%2", _padABControl, _padABTreatment]] call _assert;
private _padABCleanup = (_padABControl getOrDefault ["cleanup", false])
    && {_padABTreatment getOrDefault ["cleanup", false]}
    && {(nearestObjects [_padABDestination, ["Land_HelipadEmpty_F"], 100]) isEqualTo []};
["vigil.transport.padAB.cleanup", _padABCleanup, format ["control=%1|treatment=%2|remainingPads=%3", _padABControl getOrDefault ["cleanup", false], _padABTreatment getOrDefault ["cleanup", false], nearestObjects [_padABDestination, ["Land_HelipadEmpty_F"], 100]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_TRANSPORT_PAD_AB_DONE", _token, true];
'''

CLIENT_SQF = r'''
private _deadline = diag_tickTime + 240;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_PAD_AB_DONE", ""]) isEqualTo _token
        || diag_tickTime > _deadline
};
private _done = (missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_PAD_AB_DONE", ""]) isEqualTo _token;
["vigil.transport.padAB.clientComplete", _done, format ["token=%1|done=%2", _token, missionNamespace getVariable ["TRIBUNAL_VIGIL_TRANSPORT_PAD_AB_DONE", ""]]] call _assert;
'''

TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-transport-pad-ab",
    tier="gameplay",
    server_expected=frozenset(CONTROL_ASSERTIONS + TREATMENT_ASSERTIONS + CLOSEOUT_ASSERTIONS[:-1]),
    client_expected=frozenset({CLOSEOUT_ASSERTIONS[-1]}),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-transport-hidden-pad-landing",
        "fixture": "server-local-airborne-B_Heli_Light_01_F",
        "flight_corridor": "Stratis [2000,5200,50] to [2350,5200,0]",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="For the bounded airborne doMove plus LAND sequence, one exact hidden destination pad causally distinguishes a continuously settled landing from a matched no-pad control.",
        outcome="KEEP + CHARACTERIZE ENGINE REQUIREMENT",
        rationale="A controlled server-local A/B freezes only the exact hidden-pad requirement proven for one airborne class, corridor, command sequence and deadline.",
        dependencies=("Arma helicopter AI", "Tribunal aviation observer", "one authenticated client"),
        evidence_types=frozenset({"locality", "trajectory", "ground-contact", "continuous-settling", "causal-pair", "negative-control", "cleanup"}),
        locality_requirements="The dedicated server owns both aircraft, pilot groups, destination pad, commands, observations, and cleanup; client-a observes only replicated bounded completion.",
        characterized_behaviors=(CharacterizedBehavior(
            description="Provide one exact Land_HelipadEmpty_F at destination before LAND for the tested airborne doMove approach.",
            reason="The matched no-pad helicopter reaches the arrival radius but does not descend or settle by the bounded deadline; the hidden-pad treatment does.",
            evidence="Calibration 20260824T164032Z-93edbd8c on Arma 3 2.22 dedicated: control remained airborne 105.075 m away; treatment reached 0.213 m and stayed settled 23.224 m away.",
            alternative_tested="The same server-local B_Heli_Light_01_F, airborne start, pilot, doMove destination, LAND command, terrain, weather and deadlines with no helipad within 100 m.",
            outcome="The hidden-pad arm landed and stabilized; the no-pad control remained airborne. Scope is one class, corridor, approach sequence and 90-second landing deadline.",
        ),),
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
