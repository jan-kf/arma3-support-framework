"""Causal Tier 3 coverage for Advanced Systems Counter Battery Radar.

The scenario proves the product contract reviewed in
`tribunal/docs/advanced-systems-counter-battery-radar-review.md`: while the
system is enabled, real hostile artillery fire produces an authoritative
predicted-impact zone, a narrowing then confirmed launch-origin estimate, and a
side-filtered launch warning, all of which are removed again when the threat
expires or the system is stopped.

Impact prediction is asserted against Tribunal's independent trajectory
observer rather than against the product's own internal state.
"""

from tribunal.mission.artillery import artillery_observer_sqf
from tribunal.mission.markers import marker_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


# Stratis high ground. Elevated impact is required: a sea-level target cannot
# distinguish a terrain-aware impact solution from one that integrates to the
# waterline.
ELEVATED_TARGET = "[4000, 3500, 0]"
ELEVATED_GUN = "[3500, 4000, 0]"


TRIBUNAL_SCENARIO = Scenario(
    identifier="advsys-counter-battery-radar",
    tier="gameplay",
    server_expected=frozenset({
        "cbr.control.disabledNoDetection",
        "cbr.lifecycle.start",
        "cbr.detection.cluster",
        "cbr.detection.zoneMarker",
        "cbr.detection.iconMarker",
        "cbr.prediction.impactAccuracy",
        "cbr.detection.zoneCentre",
        "cbr.origin.narrows",
        "cbr.origin.confirmed",
        "cbr.expiry.cleared",
        "cbr.locality",
        "cbr.lifecycle.stop",
    }),
    client_expected=frozenset({
        "cbr.client.enabledReplicated",
        "cbr.client.markersReplicated",
        "cbr.client.warningDelivered",
        "cbr.client.warningControls",
        "cbr.client.noLocalState",
    }),
    server_sqf=artillery_observer_sqf() + marker_observer_sqf() + r'''
private _zonePrefix = "YOSHI_cb_";
private _originPrefix = "YOSHI_origin";
private _target = ''' + ELEVATED_TARGET + r''';
private _targetHeight = getTerrainHeightASL _target;

private _gun = "O_Mortar_01_F" createVehicle ''' + ELEVATED_GUN + r''';
_gun setVectorUp (surfaceNormal (getPosATL _gun));
createVehicleCrew _gun;
private _crewDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.1; !isNull (gunner _gun) || diag_tickTime > _crewDeadline};
private _ordnance = "8Rnd_82mm_Mo_shells";
_gun setVehicleAmmo 1;

// ---------------------------------------------------------------- control --
// Disabled is the shipped default. The same real fire must produce no zone,
// no origin estimate and no markers at all.
private _disabledEnabled = missionNamespace getVariable ["YOSHI_CBR_ENABLED", true];
_gun doArtilleryFire [_target, _ordnance, 1];
private _disabledDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.5; diag_tickTime > _disabledDeadline};
private _disabledZones = [_zonePrefix] call TRIBUNAL_fnc_markerNames;
private _disabledOrigins = [_originPrefix] call TRIBUNAL_fnc_markerNames;
private _disabledOk = !_disabledEnabled
    && {YOSHI_CB_clusters isEqualTo []}
    && {_disabledZones isEqualTo []}
    && {_disabledOrigins isEqualTo []}
    && {(count YOSHI_originTrack) isEqualTo 0};
["cbr.control.disabledNoDetection", _disabledOk, format ["enabled=%1|clusters=%2|zones=%3|origins=%4|tracks=%5", _disabledEnabled, count YOSHI_CB_clusters, _disabledZones, _disabledOrigins, count YOSHI_originTrack]] call _assert;

// ---------------------------------------------------------------- start ----
private _started = [] call YOSHI_fnc_cbrStart;
private _startOk = _started && {missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]}
    && {!scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull])}
    && {!scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])};
["cbr.lifecycle.start", _startOk, format ["started=%1|enabled=%2", _started, missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_CBR_ENABLED_AT", _token, true];

// ------------------------------------------------- detection and prediction -
// One full magazine: enough repeat launches to drive the origin estimate from
// its initial radius down to a confirmed fix.
private _rounds = 8;
private _requested = [];
for "_i" from 1 to _rounds do {_requested pushBack _target};
private _fireToken = format ["%1-cbr", _token];
[_fireToken] call TRIBUNAL_fnc_artilleryObserverStart;
private _observed = [_fireToken, _gun, _requested] call TRIBUNAL_fnc_artilleryObserveSource;

// Product prediction sampled once per shell at launch, paired with that same
// shell's real terminal position. This is dispersion-free: each shell is its
// own control.
missionNamespace setVariable ["TRIBUNAL_CBR_PREDICTIONS", []];
private _predictEh = _gun addEventHandler ["Fired", {
    params ["_source", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];
    if (isNull _projectile) exitWith {};
    private _prediction = _projectile call YOSHI_predictFallTimeAndPos;
    [_projectile, netId _projectile, _prediction, diag_tickTime] spawn {
        params ["_projectile", "_uid", "_prediction", "_firedAt"];
        private _last = getPosASL _projectile;
        private _deadline = diag_tickTime + 180;
        while {!isNull _projectile && {diag_tickTime < _deadline}} do {
            _last = getPosASL _projectile;
            uiSleep 0.02;
        };
        private _records = missionNamespace getVariable ["TRIBUNAL_CBR_PREDICTIONS", []];
        _records pushBack [_uid, _prediction # 1, _prediction # 0, _last, diag_tickTime - _firedAt, isNull _projectile];
        missionNamespace setVariable ["TRIBUNAL_CBR_PREDICTIONS", _records];
    };
}];

private _peakMembers = 0;
private _peakCentre = [];
private _peakZone = "";
private _peakIcon = "";
private _peakText = "";
private _peakType = "";
private _peakShape = "";
private _peakColour = "";
private _peakSize = [];
private _originRadii = [];
private _confirmedSeen = false;

// The disabled-path control above consumed a round; restore a full magazine so
// the tracked salvo is exactly _rounds shells.
_gun setVehicleAmmo 1;
_gun doArtilleryFire [_target, _ordnance, _rounds];

private _flightDeadline = diag_tickTime + 150;
waitUntil {
    uiSleep 0.25;
    {
        private _members = count (_x select 0);
        if (_members > _peakMembers) then {
            _peakMembers = _members;
            _peakCentre = +(_x select 1);
            _peakZone = _x select 5;
            _peakIcon = _x select 6;
            _peakText = markerText (_x select 6);
            _peakType = markerType (_x select 6);
            _peakShape = markerShape (_x select 5);
            _peakColour = markerColor (_x select 5);
            _peakSize = markerSize (_x select 5);
        };
    } forEach YOSHI_CB_clusters;
    {
        private _radius = _y getOrDefault ["radius", -1];
        if (_radius >= 0) then {_originRadii pushBackUnique _radius};
        if (_y getOrDefault ["confirmed", false]) then {_confirmedSeen = true};
    } forEach YOSHI_originTrack;
    private _records = missionNamespace getVariable ["TRIBUNAL_CBR_PREDICTIONS", []];
    ((count _records) isEqualTo _rounds) || {diag_tickTime > _flightDeadline}
};
_gun removeEventHandler ["Fired", _predictEh];
private _fireState = [_fireToken] call TRIBUNAL_fnc_artilleryObserverStop;
private _events = _fireState getOrDefault ["events", []];
private _predictions = missionNamespace getVariable ["TRIBUNAL_CBR_PREDICTIONS", []];

private _clusterOk = _observed && {(count _events) isEqualTo _rounds} && {_peakMembers >= 2};
["cbr.detection.cluster", _clusterOk, format ["observed=%1|firedEvents=%2|peakMembers=%3|rounds=%4", _observed, count _events, _peakMembers, _rounds]] call _assert;

private _zoneOk = _peakZone isNotEqualTo "" && {_peakShape isEqualTo "ELLIPSE"} && {_peakColour isEqualTo "ColorRed"}
    && {(count _peakSize) isEqualTo 2} && {(_peakSize # 0) > 0};
["cbr.detection.zoneMarker", _zoneOk, format ["marker=%1|shape=%2|colour=%3|size=%4|centre=%5", _peakZone, _peakShape, _peakColour, _peakSize, _peakCentre]] call _assert;

// Marker properties are captured while the zone is live: it is deleted as soon
// as the last tracked shell expires, so reading them here would race cleanup.
private _iconOk = _peakIcon isNotEqualTo "" && {_peakType isEqualTo "mil_warning"}
    && {(_peakText find "shells") > 0} && {(_peakText find "ETA") > 0};
["cbr.detection.iconMarker", _iconOk, format ["icon=%1|type=%2|text=%3", _peakIcon, _peakType, _peakText]] call _assert;

// Per-shell predicted impact against the engine's real terminal position.
private _errors = [];
private _etaErrors = [];
{
    _x params ["_uid", "_predictedPos", "_predictedEta", "_actualPos", "_flight", "_terminated"];
    if (_terminated && {(count _predictedPos) >= 2} && {(count _actualPos) >= 2}) then {
        _errors pushBack (_predictedPos distance2D _actualPos);
        _etaErrors pushBack (_predictedEta - _flight);
    };
} forEach _predictions;
private _worstError = if (_errors isEqualTo []) then {1e9} else {selectMax _errors};
private _worstEta = if (_etaErrors isEqualTo []) then {1e9} else {selectMax (_etaErrors apply {abs _x})};
private _accuracyOk = (count _errors) >= 4 && {_worstError < 20} && {_worstEta < 3} && {_targetHeight > 100};
["cbr.prediction.impactAccuracy", _accuracyOk, format ["samples=%1|worstMetres=%2|worstEtaSeconds=%3|targetHeightASL=%4|errors=%5", count _errors, _worstError, _worstEta, _targetHeight, _errors]] call _assert;

// Aggregate: the drawn zone centre must sit on the real impact centroid.
private _impacts = [];
{
    private _last = _x getOrDefault ["lastPosition", []];
    if ((count _last) >= 2 && {_x getOrDefault ["terminated", false]}) then {_impacts pushBack _last};
} forEach _events;
private _centroid = [0, 0, 0];
if !(_impacts isEqualTo []) then {
    private _sx = 0; private _sy = 0;
    {_sx = _sx + (_x # 0); _sy = _sy + (_x # 1);} forEach _impacts;
    _centroid = [_sx / (count _impacts), _sy / (count _impacts), 0];
};
private _centreError = if ((count _peakCentre) >= 2 && {!(_impacts isEqualTo [])}) then {_peakCentre distance2D _centroid} else {1e9};
["cbr.detection.zoneCentre", (count _impacts) >= 4 && {_centreError < 30}, format ["zoneCentre=%1|impactCentroid=%2|metres=%3|impacts=%4", _peakCentre, _centroid, _centreError, count _impacts]] call _assert;

// The zone is removed as soon as its last member expires, so the removal must
// be observed here rather than after the later phases have burned that window.
private _expirySamples = [_zonePrefix, {params ["_census"]; (_census getOrDefault ["count", 0]) isEqualTo 0}, 60, 0.5] call TRIBUNAL_fnc_markerObserve;
private _expiry = [_expirySamples] call TRIBUNAL_fnc_markerLifecycleEvidence;
private _expiryOk = _peakMembers > 0 && {_expiry getOrDefault ["cleared", false]} && {YOSHI_CB_clusters isEqualTo []};
["cbr.expiry.cleared", _expiryOk, format ["peakMembers=%1|samples=%2|maximum=%3|final=%4|removed=%5|clusters=%6", _peakMembers, _expiry getOrDefault ["samples", 0], _expiry getOrDefault ["maximumCount", -1], _expiry getOrDefault ["finalCount", -1], _expiry getOrDefault ["removed", []], count YOSHI_CB_clusters]] call _assert;

// ---------------------------------------------------------------- origin ---
private _minRadius = if (_originRadii isEqualTo []) then {1e9} else {selectMin _originRadii};
private _maxRadius = if (_originRadii isEqualTo []) then {-1} else {selectMax _originRadii};
["cbr.origin.narrows", (count _originRadii) >= 3 && {_maxRadius >= YOSHI_ORIGIN_INITIAL_R} && {_minRadius < _maxRadius}, format ["radii=%1|min=%2|max=%3", _originRadii, _minRadius, _maxRadius]] call _assert;

// One magazine halves the estimate to just above the confirmation threshold.
// A second, shorter volley from the same gun carries it past that threshold,
// which is what promotes the estimate to a confirmed fix.
_gun setVehicleAmmo 1;
_gun doArtilleryFire [_target, _ordnance, 4];
private _confirmDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.25;
    {
        private _radius = _y getOrDefault ["radius", -1];
        if (_radius >= 0) then {_originRadii pushBackUnique _radius};
        if (_y getOrDefault ["confirmed", false]) then {_confirmedSeen = true};
    } forEach YOSHI_originTrack;
    _confirmedSeen || {diag_tickTime > _confirmDeadline}
};
private _confirmedMarkers = ([_originPrefix] call TRIBUNAL_fnc_markerNames) select {(_x find "confirm") > 0};
private _confirmedTracks = [];
{if (_y getOrDefault ["confirmed", false]) then {_confirmedTracks pushBack _x}} forEach YOSHI_originTrack;
private _confirmedOk = (_confirmedSeen || {!(_confirmedTracks isEqualTo [])})
    && {!(_confirmedMarkers isEqualTo [])}
    && {(markerType (_confirmedMarkers # 0)) isEqualTo "mil_triangle"}
    && {((markerPos (_confirmedMarkers # 0)) distance2D _gun) < 5};
["cbr.origin.confirmed", _confirmedOk, format ["markers=%1|tracks=%2|type=%3|gun=%4|markerPos=%5", _confirmedMarkers, _confirmedTracks, if (_confirmedMarkers isEqualTo []) then {""} else {markerType (_confirmedMarkers # 0)}, getPosASL _gun, if (_confirmedMarkers isEqualTo []) then {[]} else {markerPos (_confirmedMarkers # 0)}]] call _assert;

// ------------------------------------------------------------ warning gate --
missionNamespace setVariable ["TRIBUNAL_CBR_WARN_READY", _token, true];
private _warnDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_CBR_WARN_ARMED", ""]) isEqualTo _token || diag_tickTime > _warnDeadline};
private _players = allPlayers select {isPlayer _x && {alive _x}};
private _observer = if (_players isEqualTo []) then {objNull} else {_players # 0};
private _observerPos = if (isNull _observer) then {[0,0,0]} else {getPosASL _observer};
// Positive, then a same-side control and an out-of-radius control.
[east, [(_observerPos # 0) + 300, _observerPos # 1, 0], 1000] call YOSHI_fnc_cbrWarnSidePlayers;
uiSleep 6;
missionNamespace setVariable ["TRIBUNAL_CBR_WARN_POSITIVE", _token, true];
uiSleep 4;
[west, [(_observerPos # 0) + 300, _observerPos # 1, 0], 1000] call YOSHI_fnc_cbrWarnSidePlayers;
uiSleep 4;
[east, [(_observerPos # 0) + 6000, _observerPos # 1, 0], 1000] call YOSHI_fnc_cbrWarnSidePlayers;
uiSleep 6;
missionNamespace setVariable ["TRIBUNAL_CBR_WARN_CONTROLS", _token, true];

private _localityOk = isServer && {isDedicated} && {!hasInterface} && {local _gun}
    && {({(_x getOrDefault ["executionMachine", ""]) isEqualTo "server"} count _events) isEqualTo (count _events)};
["cbr.locality", _localityOk, format ["server=%1|dedicated=%2|gunLocal=%3|events=%4", isServer, isDedicated, local _gun, count _events]] call _assert;

// ---------------------------------------------------------------- stop -----
private _stopped = [] call YOSHI_fnc_cbrStop;
uiSleep 2;
private _stopZones = [_zonePrefix] call TRIBUNAL_fnc_markerNames;
private _stopOrigins = [_originPrefix] call TRIBUNAL_fnc_markerNames;
private _stopOk = !_stopped
    && {!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", true])}
    && {_stopZones isEqualTo []}
    && {_stopOrigins isEqualTo []}
    && {YOSHI_CB_clusters isEqualTo []}
    && {(count YOSHI_originTrack) isEqualTo 0}
    && {scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull])};
["cbr.lifecycle.stop", _stopOk, format ["stopped=%1|enabled=%2|zones=%3|origins=%4|clusters=%5|tracks=%6", _stopped, missionNamespace getVariable ["YOSHI_CBR_ENABLED", true], _stopZones, _stopOrigins, count YOSHI_CB_clusters, count YOSHI_originTrack]] call _assert;

deleteVehicleCrew _gun;
deleteVehicle _gun;
missionNamespace setVariable ["TRIBUNAL_CBR_COMPLETE", _token, true];
''',
    client_sqf=marker_observer_sqf() + r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];
private _enabledDeadline = diag_tickTime + 180;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_ENABLED_AT", ""]) isEqualTo _token || diag_tickTime > _enabledDeadline};
["cbr.client.enabledReplicated", (missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]) && {hasInterface} && {!isServer} && {_identity isEqualTo "client-a"}, format ["enabled=%1|hasInterface=%2|server=%3|identity=%4", missionNamespace getVariable ["YOSHI_CBR_ENABLED", "missing"], hasInterface, isServer, _identity]] call _assert;

["cbr.client.noLocalState", (YOSHI_CB_clusters isEqualTo []) && {(count YOSHI_originTrack) isEqualTo 0}, format ["clusters=%1|tracks=%2", count YOSHI_CB_clusters, count YOSHI_originTrack]] call _assert;

// The authoritative zone must become visible on this client while the threat
// is airborne, then disappear with it. Observed on its own worker so the radio
// gates below are not blocked by the zone lifecycle.
TRIBUNAL_CBR_ZONE_EVIDENCE = nil;
private _zoneWorker = [] spawn {
    private _saw = false;
    private _samples = [
        "YOSHI_cb_",
        {
            params ["_census"];
            if ((_census getOrDefault ["count", 0]) > 0) then {_saw = true};
            _saw && {(_census getOrDefault ["count", 0]) isEqualTo 0}
        },
        240,
        1
    ] call TRIBUNAL_fnc_markerObserve;
    TRIBUNAL_CBR_ZONE_EVIDENCE = [_samples] call TRIBUNAL_fnc_markerLifecycleEvidence;
};

// Radio delivery evidence. This proves the warning reached this client's radio
// playback path; automated clients run -noSound, so audible output is not claimed.
TRIBUNAL_CBR_RADIO = [];
TRIBUNAL_CBR_ORIGINAL_RADIO = YCD_fnc_playSideRadioLocal;
YCD_fnc_playSideRadioLocal = {
    TRIBUNAL_CBR_RADIO pushBack [round diag_tickTime, _this select 1];
    _this call TRIBUNAL_CBR_ORIGINAL_RADIO
};
private _readyDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_WARN_READY", ""]) isEqualTo _token || diag_tickTime > _readyDeadline};
missionNamespace setVariable ["TRIBUNAL_CBR_WARN_ARMED", _token, true];

private _positiveDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_CBR_WARN_POSITIVE", ""]) isEqualTo _token || diag_tickTime > _positiveDeadline};
private _afterPositive = +TRIBUNAL_CBR_RADIO;
private _warnings = _afterPositive select {(_x # 1) isEqualTo "YAS_CBR_WarningLaunchDetected"};
["cbr.client.warningDelivered", (count _warnings) isEqualTo 1 && {side player isEqualTo west}, format ["warnings=%1|all=%2|side=%3", count _warnings, _afterPositive, side player]] call _assert;

private _controlsDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_CBR_WARN_CONTROLS", ""]) isEqualTo _token || diag_tickTime > _controlsDeadline};
private _afterControls = (+TRIBUNAL_CBR_RADIO) select {(_x # 1) isEqualTo "YAS_CBR_WarningLaunchDetected"};
["cbr.client.warningControls", (count _afterControls) isEqualTo (count _warnings), format ["beforeControls=%1|afterControls=%2|records=%3", count _warnings, count _afterControls, _afterControls]] call _assert;
YCD_fnc_playSideRadioLocal = TRIBUNAL_CBR_ORIGINAL_RADIO;

private _zoneDeadline = diag_tickTime + 260;
waitUntil {uiSleep 0.5; (scriptDone _zoneWorker) || diag_tickTime > _zoneDeadline};
private _zoneEvidence = if (isNil "TRIBUNAL_CBR_ZONE_EVIDENCE") then {createHashMap} else {TRIBUNAL_CBR_ZONE_EVIDENCE};
private _replicatedOk = (_zoneEvidence getOrDefault ["appeared", false])
    && {(_zoneEvidence getOrDefault ["maximumCount", 0]) >= 2}
    && {_zoneEvidence getOrDefault ["cleared", false]};
["cbr.client.markersReplicated", _replicatedOk, format ["samples=%1|maximum=%2|everSeen=%3|final=%4|cleared=%5", _zoneEvidence getOrDefault ["samples", 0], _zoneEvidence getOrDefault ["maximumCount", -1], _zoneEvidence getOrDefault ["everSeen", []], _zoneEvidence getOrDefault ["finalCount", -1], _zoneEvidence getOrDefault ["cleared", false]]] call _assert;

private _completionDeadline = diag_tickTime + 180;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_COMPLETE", ""]) isEqualTo _token || diag_tickTime > _completionDeadline};
''',
    metadata={
        "product": "advanced-systems",
        "feature": "counter-battery-radar",
        "detection_source": "native-artillery",
        "evidence": "predicted-impact,map-markers,side-radio",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract=(
            "While the system is enabled, hostile artillery fire produces an authoritative predicted-impact "
            "zone whose drawn centre matches the real impact area, a launch-origin estimate that narrows with "
            "repeated fire until it is confirmed at the firing position, and a launch warning delivered only to "
            "opposing-side players within the warning radius; all of it disappears when the threat expires and "
            "when the system is stopped, and nothing is produced while it is disabled."
        ),
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale=(
            "Impact prediction integrated to sea level rather than to the ground under the projected point, "
            "placing the drawn zone tens of metres downrange of the real impact whenever the target was above "
            "the waterline. The scenario now asserts predicted-versus-real impact per shell against Tribunal's "
            "independent trajectory observer, so the corrected solution cannot regress unnoticed. Cluster "
            "layout, marker names, uid format and polling cadence remain evidence adapters."
        ),
        dependencies=(
            "Tribunal artillery observer",
            "Tribunal marker observer",
            "Arma native artillery and ArtilleryShellFired",
            "CORDIS side-radio emission",
            "one authenticated client",
        ),
        evidence_types=frozenset({
            "fire-event", "trajectory", "impact", "map-marker", "replication", "negative-control", "locality", "cleanup",
        }),
        locality_requirements=(
            "The dedicated server owns detection, clustering, prediction, origin estimation and every marker; "
            "client-a observes replicated markers and receives the side-filtered radio warning, and holds no "
            "cluster or origin state of its own."
        ),
    ),
)
