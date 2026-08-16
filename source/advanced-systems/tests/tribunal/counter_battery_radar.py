"""Causal Tier 3 coverage for Advanced Systems Counter Battery Radar.

The scenario proves the product contract reviewed in
`tribunal/docs/advanced-systems-counter-battery-radar-review.md`: while the
system is enabled, real hostile artillery fire produces an authoritative
predicted-impact zone, a narrowing then confirmed launch-origin estimate, and a
side-filtered launch warning, all of which are removed again when the threat
expires or the system is stopped.

Every warning claim travels the real pipeline — native artillery launch,
`ArtilleryShellFired`, the product handler, emission, client receipt — rather
than invoking the warning helper directly, and both negative controls are real
launches too. Impact prediction is asserted against Tribunal's independent
artillery/trajectory observer.
"""

from tribunal.mission.artillery import artillery_observer_sqf
from tribunal.mission.markers import marker_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


# Stratis high ground. Elevated impact is required: a sea-level target cannot
# distinguish a terrain-aware impact solution from one that integrates to the
# waterline. It is also far from the player, so it doubles as the real
# out-of-radius warning control.
ELEVATED_TARGET = "[4000, 3500, 0]"
ELEVATED_GUN = "[3500, 4000, 0]"

# Logical client identities this scenario observes. Adding a second identity is
# additive: extend this tuple and the per-identity maps below.
OBSERVER_IDENTITIES = ("client-a",)

CLIENT_EXPECTED = frozenset({
    "cbr.client.enabledReplicated",
    "cbr.client.noLocalState",
    "cbr.client.markersReplicated",
    "cbr.client.warningOutOfRadius",
    "cbr.client.warningDelivered",
    "cbr.client.warningSameSide",
})

CLIENT_SQF = marker_observer_sqf() + r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];

// Published first: the server places its artillery relative to a declared
// observer rather than whichever player happens to be first in allPlayers, and
// it needs that position before the fixture exists.
missionNamespace setVariable [format ["TRIBUNAL_CBR_OBSERVER_%1", _identity], netId player, true];

private _enabledDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_ENABLED_AT", ""]) isEqualTo _token || diag_tickTime > _enabledDeadline};
["cbr.client.enabledReplicated", (missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]) && {hasInterface} && {!isServer} && {_identity isNotEqualTo ""}, format ["enabled=%1|hasInterface=%2|server=%3|identity=%4", missionNamespace getVariable ["YOSHI_CBR_ENABLED", "missing"], hasInterface, isServer, _identity]] call _assert;

["cbr.client.noLocalState", (YOSHI_CB_clusters isEqualTo []) && {(count YOSHI_originTrack) isEqualTo 0}, format ["identity=%1|clusters=%2|tracks=%3", _identity, count YOSHI_CB_clusters, count YOSHI_originTrack]] call _assert;

// Radio delivery evidence. This proves the warning reached this client's radio
// playback path; automated clients run -noSound, so audible output is not claimed.
TRIBUNAL_CBR_RADIO = [];
TRIBUNAL_CBR_ORIGINAL_RADIO = YCD_fnc_playSideRadioLocal;
YCD_fnc_playSideRadioLocal = {
    TRIBUNAL_CBR_RADIO pushBack [round diag_tickTime, _this select 1];
    _this call TRIBUNAL_CBR_ORIGINAL_RADIO
};
TRIBUNAL_CBR_fnc_warnCount = {
    (+TRIBUNAL_CBR_RADIO) select {(_x # 1) isEqualTo "YAS_CBR_WarningLaunchDetected"}
};

// The authoritative zone must become visible on this client while the threat is
// airborne, then disappear with it. Observed on its own worker so the warning
// gates below are never blocked by the zone lifecycle.
TRIBUNAL_CBR_ZONE_SAMPLES = nil;
private _zoneWorker = [] spawn {
    private _saw = false;
    TRIBUNAL_CBR_ZONE_SAMPLES = [
        "YOSHI_cb_",
        {
            params ["_census"];
            if ((_census getOrDefault ["count", 0]) > 0) then {_saw = true};
            _saw && {(_census getOrDefault ["count", 0]) isEqualTo 0}
        },
        260,
        0.5
    ] call TRIBUNAL_fnc_markerObserve;
};

// The origin estimate is authored on the server and must reach this client too.
// Captured on its own worker while CBR is still running, because a confirmed
// origin marker only disappears when the system is stopped.
TRIBUNAL_CBR_ORIGIN_SEEN = [];
private _originWorker = [] spawn {
    private _samples = [
        "YOSHI_origin",
        {params ["_census"]; (_census getOrDefault ["count", 0]) > 0},
        260,
        0.5
    ] call TRIBUNAL_fnc_markerObserve;
    private _last = _samples select -1;
    TRIBUNAL_CBR_ORIGIN_SEEN = _last getOrDefault ["names", []];
};

missionNamespace setVariable ["TRIBUNAL_CBR_SPY_ARMED", _token, true];

// Real out-of-radius control: the elevated salvo is hostile artillery, but it
// lands kilometres away, so this client must receive nothing from it.
private _farDeadline = diag_tickTime + 300;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_FAR_DONE", ""]) isEqualTo _token || diag_tickTime > _farDeadline};
private _afterFar = call TRIBUNAL_CBR_fnc_warnCount;
["cbr.client.warningOutOfRadius", (count _afterFar) isEqualTo 0, format ["identity=%1|warnings=%2|records=%3", _identity, count _afterFar, _afterFar]] call _assert;

// Positive: a real hostile salvo inside the warning radius warns exactly once,
// however many shells are in that airborne cycle.
private _warnDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_CBR_WARN_DONE", ""]) isEqualTo _token || diag_tickTime > _warnDeadline};
private _afterWarn = call TRIBUNAL_CBR_fnc_warnCount;
private _warnShells = missionNamespace getVariable ["TRIBUNAL_CBR_WARN_SHELLS", 0];
["cbr.client.warningDelivered", (count _afterWarn) isEqualTo 1 && {_warnShells > 1} && {side player isEqualTo west}, format ["identity=%1|warnings=%2|shellsInCycle=%3|side=%4|records=%5", _identity, count _afterWarn, _warnShells, side player, _afterWarn]] call _assert;

// Real same-side control: friendly artillery landing just as close must not warn.
private _sameDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_CBR_SAMESIDE_DONE", ""]) isEqualTo _token || diag_tickTime > _sameDeadline};
private _afterSame = call TRIBUNAL_CBR_fnc_warnCount;
["cbr.client.warningSameSide", (count _afterSame) isEqualTo (count _afterWarn), format ["identity=%1|beforeControl=%2|afterControl=%3|records=%4", _identity, count _afterWarn, count _afterSame, _afterSame]] call _assert;
YCD_fnc_playSideRadioLocal = TRIBUNAL_CBR_ORIGINAL_RADIO;

// Replication must be of the exact authoritative markers, not merely of two
// markers that happen to share the product prefix.
private _zoneDeadline = diag_tickTime + 280;
waitUntil {uiSleep 0.5; (scriptDone _zoneWorker) || diag_tickTime > _zoneDeadline};
private _samples = if (isNil "TRIBUNAL_CBR_ZONE_SAMPLES") then {[]} else {TRIBUNAL_CBR_ZONE_SAMPLES};
private _zoneEvidence = [_samples] call TRIBUNAL_fnc_markerLifecycleEvidence;
private _authoritative = missionNamespace getVariable ["TRIBUNAL_CBR_ZONE_RECORD", []];
private _expectedZone = _authoritative param [0, ""];
private _expectedIcon = _authoritative param [1, ""];
private _expectedCentre = _authoritative param [2, []];
private _expectedSize = _authoritative param [3, []];
private _seen = _zoneEvidence getOrDefault ["everSeen", []];
private _matched = createHashMap;
{
    private _records = _x getOrDefault ["records", createHashMap];
    private _zoneRecord = _records getOrDefault [_expectedZone, createHashMap];
    if ((count _zoneRecord) > 0
        && {((_zoneRecord getOrDefault ["position", [1e9,1e9,0]]) distance2D _expectedCentre) < 1}
        && {(_zoneRecord getOrDefault ["shape", ""]) isEqualTo "ELLIPSE"}
        && {(_zoneRecord getOrDefault ["color", ""]) isEqualTo "ColorRed"}
        && {abs (((_zoneRecord getOrDefault ["size", [0,0]]) # 0) - (_expectedSize param [0, -1])) < 1}) then {
        _matched set ["zone", true];
    };
    private _iconRecord = _records getOrDefault [_expectedIcon, createHashMap];
    if ((count _iconRecord) > 0 && {(_iconRecord getOrDefault ["type", ""]) isEqualTo "mil_warning"}) then {
        _matched set ["icon", true];
    };
} forEach _samples;
private _originDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.25; (scriptDone _originWorker) || diag_tickTime > _originDeadline};
private _originSeen = TRIBUNAL_CBR_ORIGIN_SEEN;
private _replicatedOk = (_expectedZone isNotEqualTo "")
    && {_expectedZone in _seen}
    && {_expectedIcon in _seen}
    && {_matched getOrDefault ["zone", false]}
    && {_matched getOrDefault ["icon", false]}
    && {_zoneEvidence getOrDefault ["cleared", false]}
    && {(_originSeen findIf {(_x find "YOSHI_origin") isEqualTo 0}) >= 0};
["cbr.client.markersReplicated", _replicatedOk, format ["identity=%1|expectedZone=%2|expectedIcon=%3|everSeen=%4|zoneMatched=%5|iconMatched=%6|cleared=%7|originReplicated=%8|samples=%9", _identity, _expectedZone, _expectedIcon, _seen, _matched getOrDefault ["zone", false], _matched getOrDefault ["icon", false], _zoneEvidence getOrDefault ["cleared", false], _originSeen, count _samples]] call _assert;

private _completionDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_COMPLETE", ""]) isEqualTo _token || diag_tickTime > _completionDeadline};
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="advsys-counter-battery-radar",
    tier="gameplay",
    server_expected=frozenset({
        "cbr.control.disabledShotProven",
        "cbr.control.disabledNoDetection",
        "cbr.lifecycle.start",
        "cbr.detection.cluster",
        "cbr.detection.zoneMarker",
        "cbr.detection.iconMarker",
        "cbr.prediction.impactAccuracy",
        "cbr.detection.zoneCentre",
        "cbr.expiry.cleared",
        "cbr.origin.narrows",
        "cbr.origin.confirmed",
        "cbr.warning.launchPipeline",
        "cbr.locality",
        "cbr.lifecycle.stop",
        "cbr.cleanup",
    }),
    client_expected=CLIENT_EXPECTED,
    client_expected_by_identity={identity: CLIENT_EXPECTED for identity in OBSERVER_IDENTITIES},
    client_sqf_by_identity={identity: CLIENT_SQF for identity in OBSERVER_IDENTITIES},
    server_sqf=artillery_observer_sqf() + marker_observer_sqf() + r'''
// Search bearings and then nearby radii, so a fixture position is found even
// when the observer sits near a coastline. Returns [] rather than a bad
// position, letting the caller fail closed.
TRIBUNAL_CBR_fnc_terrainSpread = {
    params ["_candidate"];
    private _heights = [[0,0], [12,0], [-12,0], [0,12], [0,-12]] apply {
        getTerrainHeightASL [(_candidate # 0) + (_x # 0), (_candidate # 1) + (_x # 1), 0]
    };
    (selectMax _heights) - (selectMin _heights)
};

// Flat ground matters: a mortar seated on a slope by surfaceNormal can end up
// unable to elevate onto its target, firing zero rounds with no error. Flatness
// is preferred but progressively relaxed, because insisting on it outright left
// whole phases unplaced and silently skipped.
TRIBUNAL_CBR_fnc_landNear = {
    params ["_origin", "_distance"];
    private _found = [];
    {
        private _maximumSpread = _x;
        {
            private _radius = _x;
            {
                private _candidate = [(_origin # 0) + (_radius * (sin _x)), (_origin # 1) + (_radius * (cos _x)), 0];
                if (_found isEqualTo []
                    && {!(surfaceIsWater _candidate)}
                    && {(_candidate # 0) > 300} && {(_candidate # 1) > 300}
                    && {(_candidate # 0) < 7800} && {(_candidate # 1) < 7800}
                    && {([_candidate] call TRIBUNAL_CBR_fnc_terrainSpread) <= _maximumSpread}) then {_found = _candidate};
            } forEach [0, 45, 90, 135, 180, 225, 270, 315, 22, 67, 112, 157, 202, 247, 292, 337];
        } forEach [_distance, _distance * 0.8, _distance * 1.2, _distance * 0.6];
    } forEach [4, 10, 25, 1e9];
    _found
};

private _zonePrefix = "YOSHI_cb_";
private _originPrefix = "YOSHI_origin";
private _ordnance = "8Rnd_82mm_Mo_shells";
private _created = [];

// The observer must be known before the fixture is placed: the accuracy salvo
// doubles as the out-of-radius warning control, so its impact has to be
// unambiguously outside the warning radius for whichever spawn this tier used.
private _observerDeadline = diag_tickTime + 180;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_OBSERVER_client-a", ""]) isNotEqualTo "" || diag_tickTime > _observerDeadline};
private _observerId = missionNamespace getVariable ["TRIBUNAL_CBR_OBSERVER_client-a", ""];
private _observer = if (_observerId isEqualTo "") then {objNull} else {objectFromNetId _observerId};
private _observerPos = if (isNull _observer) then {[]} else {getPosASL _observer};

// Elevated ground is required to distinguish a terrain-aware impact solution
// from one that integrates to the waterline; the candidate furthest from the
// observer is chosen so the same salvo is also a sound out-of-radius control.
private _candidates = [[4000, 3500, 0], [3000, 2000, 0]];
private _target = _candidates # 0;
private _targetSeparation = -1;
{
    private _separation = if ((count _observerPos) >= 2) then {_observerPos distance2D _x} else {1e9};
    if (_separation > _targetSeparation) then {_targetSeparation = _separation; _target = _x};
} forEach _candidates;
private _targetHeight = getTerrainHeightASL _target;
private _gunOrigin = [_target, 700] call TRIBUNAL_CBR_fnc_landNear;
if (_gunOrigin isEqualTo []) then {_gunOrigin = ''' + ELEVATED_GUN + r'''};

// A fixture gun must be a firing platform, not a combatant. The warning gun is
// deliberately placed near the opposing observer, so its AI can otherwise
// acquire that player, switch behaviour and abandon the fire mission, which
// made the salvo fire zero rounds on some runs while an identical gun far from
// any enemy always fired. Disabling that AI keeps this a detection test rather
// than an AI-engagement test; it does not touch any CBR code path.
// Fixture guns are loaded, nothing more. Suppressing their combat AI was tried
// and reverted: disabling TARGET/AUTOTARGET/FSM stops an AI gunner accepting
// doArtilleryFire, and even the milder CARELESS/BLUE/captive variant broke the
// tracked salvo. The fixture stays minimal until there is evidence for more.
TRIBUNAL_CBR_fnc_firingPlatform = {
    params ["_gun"];
    _gun setVehicleAmmo 1;
    _gun
};

// A warning is emitted only for the first shell of an airborne cycle, so each
// warning phase must start from a genuinely idle tracker or its control is
// vacuous rather than causal.
// Emptiness must be *stable*: doArtilleryFire spaces its rounds out, so the
// tracker is transiently empty between rounds of a salvo that is still firing.
// Accepting that transient would let a later salvo start mid-cycle, silently
// making it a non-first launch and suppressing the warning under test.
TRIBUNAL_CBR_fnc_waitIdle = {
    params [["_timeout", 120], ["_stableFor", 8]];
    private _deadline = diag_tickTime + _timeout;
    private _stableSince = -1;
    waitUntil {
        uiSleep 0.25;
        if (YOSHI_CB_airborneShells isEqualTo []) then {
            if (_stableSince < 0) then {_stableSince = diag_tickTime};
        } else {
            _stableSince = -1;
        };
        (_stableSince >= 0 && {(diag_tickTime - _stableSince) >= _stableFor}) || diag_tickTime > _deadline
    };
    (YOSHI_CB_airborneShells isEqualTo []) && {_stableSince >= 0} && {(diag_tickTime - _stableSince) >= _stableFor}
};

private _gun = "O_Mortar_01_F" createVehicle _gunOrigin;
_gun setVectorUp (surfaceNormal (getPosATL _gun));
createVehicleCrew _gun;
_created pushBack _gun;
private _crewDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.1; !isNull (gunner _gun) || diag_tickTime > _crewDeadline};
[_gun] call TRIBUNAL_CBR_fnc_firingPlatform;

// ---------------------------------------------------------------- control --
// Disabled is the shipped default. The control only means anything if the same
// real shot genuinely happened, so the shell is independently observed through
// launch, flight and impact before CBR's silence is asserted.
private _disabledEnabled = missionNamespace getVariable ["YOSHI_CBR_ENABLED", true];
private _controlToken = format ["%1-cbr-control", _token];
[_controlToken] call TRIBUNAL_fnc_artilleryObserverStart;
private _controlObserved = [_controlToken, _gun, [_target]] call TRIBUNAL_fnc_artilleryObserveSource;
_gun doArtilleryFire [_target, _ordnance, 1];
private _disabledDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.25;
    private _events = ([_controlToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
    ((count _events) >= 1 && {(_events # 0) getOrDefault ["terminated", false]}) || diag_tickTime > _disabledDeadline
};
private _controlEvents = ([_controlToken] call TRIBUNAL_fnc_artilleryObserverStop) getOrDefault ["events", []];
private _controlEvent = _controlEvents param [0, createHashMap];
private _controlLast = _controlEvent getOrDefault ["lastPosition", []];
private _controlShotOk = _controlObserved
    && {(count _controlEvents) isEqualTo 1}
    && {(_controlEvent getOrDefault ["source", ""]) isEqualTo netId _gun}
    && {(_controlEvent getOrDefault ["magazine", ""]) isEqualTo _ordnance}
    && {_controlEvent getOrDefault ["artilleryEvent", false]}
    && {_controlEvent getOrDefault ["terminated", false]}
    && {(count (_controlEvent getOrDefault ["samples", []])) > 10}
    && {(count _controlLast) >= 2}
    && {(_controlLast distance2D _target) < 250};
["cbr.control.disabledShotProven", _controlShotOk, format ["observed=%1|events=%2|artilleryEvent=%3|terminated=%4|samples=%5|impact=%6|target=%7", _controlObserved, count _controlEvents, _controlEvent getOrDefault ["artilleryEvent", false], _controlEvent getOrDefault ["terminated", false], count (_controlEvent getOrDefault ["samples", []]), _controlLast, _target]] call _assert;

private _disabledZones = [_zonePrefix] call TRIBUNAL_fnc_markerNames;
private _disabledOrigins = [_originPrefix] call TRIBUNAL_fnc_markerNames;
private _disabledOk = _controlShotOk
    && {!_disabledEnabled}
    && {YOSHI_CB_clusters isEqualTo []}
    && {_disabledZones isEqualTo []}
    && {_disabledOrigins isEqualTo []}
    && {(count YOSHI_originTrack) isEqualTo 0};
["cbr.control.disabledNoDetection", _disabledOk, format ["shotProven=%1|enabled=%2|clusters=%3|zones=%4|origins=%5|tracks=%6", _controlShotOk, _disabledEnabled, count YOSHI_CB_clusters, _disabledZones, _disabledOrigins, count YOSHI_originTrack]] call _assert;

// ---------------------------------------------------------------- start ----
private _started = [] call YOSHI_fnc_cbrStart;
private _startOk = _started && {missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]}
    && {!scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull])}
    && {!scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])};
["cbr.lifecycle.start", _startOk, format ["started=%1|enabled=%2", _started, missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]]] call _assert;

// Transparent emission recorder: records what the product decided to warn about
// and who qualified, then runs the real helper unchanged. Paired with the
// client's receipt evidence this separates "never emitted" from "not received".
TRIBUNAL_CBR_HANDLE_CALLS = [];
TRIBUNAL_CBR_HANDLE_ORIGINAL = YOSHI_fnc_cbrHandleLocalArtilleryFire;
YOSHI_fnc_cbrHandleLocalArtilleryFire = {
    TRIBUNAL_CBR_HANDLE_CALLS pushBack [
        if (isNull (_this select 0)) then {""} else {netId (_this select 0)},
        str (_this select 1), _this param [3, false], count YOSHI_CB_airborneShells
    ];
    _this call TRIBUNAL_CBR_HANDLE_ORIGINAL
};

TRIBUNAL_CBR_WARN_CALLS = [];
TRIBUNAL_CBR_WARN_ORIGINAL = YOSHI_fnc_cbrWarnSidePlayers;
YOSHI_fnc_cbrWarnSidePlayers = {
    private _artySide = _this select 0;
    private _impact = _this select 1;
    private _radius = _this param [2, 1000];
    private _qualifying = allPlayers select {
        isPlayer _x && {alive _x} && {(side _x) in [west, east, resistance]}
        && {(side _x) isNotEqualTo _artySide} && {(_x distance2D _impact) <= _radius}
    };
    TRIBUNAL_CBR_WARN_CALLS pushBack [_artySide, +_impact, _qualifying apply {netId _x}, allPlayers apply {[netId _x, str side _x, isPlayer _x, alive _x, round (_x distance2D _impact)]}];
    _this call TRIBUNAL_CBR_WARN_ORIGINAL
};

missionNamespace setVariable ["TRIBUNAL_CBR_ENABLED_AT", _token, true];

// The observing clients must arm their radio evidence before any hostile round
// is in the air, or the out-of-radius control could pass by simply missing it.
private _armedDeadline = diag_tickTime + 120;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_SPY_ARMED", ""]) isEqualTo _token || diag_tickTime > _armedDeadline};

// ------------------------------------------------- detection and prediction -
private _rounds = 8;
private _requested = [];
for "_i" from 1 to _rounds do {_requested pushBack _target};
private _fireToken = format ["%1-cbr", _token];
[_fireToken] call TRIBUNAL_fnc_artilleryObserverStart;
private _observed = [_fireToken, _gun, _requested] call TRIBUNAL_fnc_artilleryObserveSource;

// Product prediction sampled once per shell at launch, paired with that same
// shell's real terminal position. Dispersion-free: each shell is its own
// control. The pairing poll is scenario-local; the launch/trajectory oracle it
// is compared against is Tribunal's.
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
private _peakEtaMin = -1;
private _peakEtaMax = -1;
private _originRadii = [];
private _confirmedSeen = false;

[_gun] call TRIBUNAL_CBR_fnc_firingPlatform;
_gun doArtilleryFire [_target, _ordnance, _rounds];

private _flightDeadline = diag_tickTime + 180;
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
            _peakEtaMin = _x select 3;
            _peakEtaMax = _x select 4;
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
missionNamespace setVariable ["TRIBUNAL_CBR_ZONE_RECORD", [_peakZone, _peakIcon, _peakCentre, _peakSize], true];

private _clusterOk = _observed && {(count _events) isEqualTo _rounds} && {_peakMembers >= 2};
["cbr.detection.cluster", _clusterOk, format ["observed=%1|firedEvents=%2|peakMembers=%3|rounds=%4", _observed, count _events, _peakMembers, _rounds]] call _assert;

private _zoneOk = _peakZone isNotEqualTo "" && {_peakShape isEqualTo "ELLIPSE"} && {_peakColour isEqualTo "ColorRed"}
    && {(count _peakSize) isEqualTo 2} && {(_peakSize # 0) > 0};
["cbr.detection.zoneMarker", _zoneOk, format ["marker=%1|shape=%2|colour=%3|size=%4|centre=%5", _peakZone, _peakShape, _peakColour, _peakSize, _peakCentre]] call _assert;

// Marker properties are captured while the zone is live: it is deleted as soon
// as the last tracked shell expires, so reading them here would race cleanup.
// The label must state the count and remaining time the product actually holds,
// and that time must be consistent with the flights Tribunal measured.
private _flights = _predictions apply {_x # 4};
private _maximumFlight = if (_flights isEqualTo []) then {0} else {selectMax _flights};
private _expectedText = format ["%1 shells | ETA %2-%3s", _peakMembers, _peakEtaMin, _peakEtaMax];
private _iconOk = _peakIcon isNotEqualTo "" && {_peakType isEqualTo "mil_warning"}
    && {_peakText isEqualTo _expectedText}
    && {_peakEtaMin >= 0} && {_peakEtaMin <= _peakEtaMax}
    && {_peakEtaMax <= (_maximumFlight + 2)};
["cbr.detection.iconMarker", _iconOk, format ["icon=%1|type=%2|text=%3|expectedText=%4|etaMin=%5|etaMax=%6|maxObservedFlight=%7", _peakIcon, _peakType, _peakText, _expectedText, _peakEtaMin, _peakEtaMax, _maximumFlight]] call _assert;

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

private _expirySamples = [_zonePrefix, {params ["_census"]; (_census getOrDefault ["count", 0]) isEqualTo 0}, 60, 0.5] call TRIBUNAL_fnc_markerObserve;
private _expiry = [_expirySamples] call TRIBUNAL_fnc_markerLifecycleEvidence;
private _expiryOk = _peakMembers > 0 && {_expiry getOrDefault ["cleared", false]} && {YOSHI_CB_clusters isEqualTo []};
["cbr.expiry.cleared", _expiryOk, format ["peakMembers=%1|samples=%2|maximum=%3|final=%4|removed=%5|clusters=%6", _peakMembers, _expiry getOrDefault ["samples", 0], _expiry getOrDefault ["maximumCount", -1], _expiry getOrDefault ["finalCount", -1], _expiry getOrDefault ["removed", []], count YOSHI_CB_clusters]] call _assert;

// ---------------------------------------------------------------- origin ---
private _minRadius = if (_originRadii isEqualTo []) then {1e9} else {selectMin _originRadii};
private _maxRadius = if (_originRadii isEqualTo []) then {-1} else {selectMax _originRadii};
["cbr.origin.narrows", (count _originRadii) >= 3 && {_maxRadius >= YOSHI_ORIGIN_INITIAL_R} && {_minRadius < _maxRadius}, format ["radii=%1|min=%2|max=%3", _originRadii, _minRadius, _maxRadius]] call _assert;

[_gun] call TRIBUNAL_CBR_fnc_firingPlatform;
private _confirmToken = format ["%1-cbr-confirm", _token];
[_confirmToken] call TRIBUNAL_fnc_artilleryObserverStart;
[_confirmToken, _gun, []] call TRIBUNAL_fnc_artilleryObserveSource;
_gun doArtilleryFire [_target, _ordnance, 4];
private _confirmDeadline = diag_tickTime + 120;
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

// Drain the confirm volley to completion before any warning phase begins.
private _drainDeadline = diag_tickTime + 150;
waitUntil {
    uiSleep 0.25;
    private _ev = ([_confirmToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
    ((count _ev) >= 4 && {({_x getOrDefault ["terminated", false]} count _ev) >= 4}) || diag_tickTime > _drainDeadline
};
private _confirmEvents = ([_confirmToken] call TRIBUNAL_fnc_artilleryObserverStop) getOrDefault ["events", []];
private _farIdle = [120] call TRIBUNAL_CBR_fnc_waitIdle;
missionNamespace setVariable ["TRIBUNAL_CBR_FAR_DONE", _token, true];

// ------------------------------------------------------------ warning ------
// Everything below travels the real pipeline: native launch, the engine's
// ArtilleryShellFired, the product's own handler, emission and client receipt.
_observerPos = if (isNull _observer) then {[]} else {getPosASL _observer};
private _warnTarget = if ((count _observerPos) >= 2) then {[_observerPos, 350] call TRIBUNAL_CBR_fnc_landNear} else {[]};
if (_warnTarget isEqualTo [] && {(count _observerPos) >= 2}) then {_warnTarget = [(_observerPos # 0) + 350, _observerPos # 1, 0]};
private _warnGunPos = if (_warnTarget isEqualTo []) then {[]} else {[_warnTarget, 1200] call TRIBUNAL_CBR_fnc_landNear};

private _warnShells = 3;
private _warnEvents = [];
private _warnGun = objNull;
private _sameGun = objNull;
private _sameEvents = [];
private _warnIdle = false;
private _sameIdle = false;
private _warnState = createHashMap;
if !(_warnGunPos isEqualTo []) then {
    _warnGun = "O_Mortar_01_F" createVehicle _warnGunPos;
    _warnGun setVectorUp (surfaceNormal (getPosATL _warnGun));
    createVehicleCrew _warnGun;
    _created pushBack _warnGun;
    private _wc = diag_tickTime + 10;
    waitUntil {uiSleep 0.1; !isNull (gunner _warnGun) || diag_tickTime > _wc};
    [_warnGun] call TRIBUNAL_CBR_fnc_firingPlatform;
    _warnIdle = [120] call TRIBUNAL_CBR_fnc_waitIdle;
    // Re-arm after the idle wait, not before it: the fixture must be loaded at
    // the moment it fires, and this records why if it is not.
    [_warnGun] call TRIBUNAL_CBR_fnc_firingPlatform;
    _warnState = createHashMapFromArray [
        ["gun", netId _warnGun], ["gunner", !isNull (gunner _warnGun)],
        ["ammo", getArtilleryAmmo [_warnGun]], ["damage", damage _warnGun],
        ["position", getPosASL _warnGun], ["range", _warnGunPos distance2D _warnTarget],
        ["inRange", _warnTarget inRangeOfArtillery [[_warnGun], _ordnance]]
    ];
    private _warnToken = format ["%1-cbr-warn", _token];
    [_warnToken] call TRIBUNAL_fnc_artilleryObserverStart;
    [_warnToken, _warnGun, []] call TRIBUNAL_fnc_artilleryObserveSource;
    _warnGun doArtilleryFire [_warnTarget, _ordnance, _warnShells];
    private _wd = diag_tickTime + 150;
    waitUntil {
        uiSleep 0.25;
        private _ev = ([_warnToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
        ((count _ev) >= _warnShells && {({_x getOrDefault ["terminated", false]} count _ev) >= _warnShells}) || diag_tickTime > _wd
    };
    _warnEvents = ([_warnToken] call TRIBUNAL_fnc_artilleryObserverStop) getOrDefault ["events", []];
};
missionNamespace setVariable ["TRIBUNAL_CBR_WARN_SHELLS", count _warnEvents, true];
missionNamespace setVariable ["TRIBUNAL_CBR_WARN_DONE", _token, true];

// Same-side control: friendly artillery landing just as close to the observer.
if !(_warnGunPos isEqualTo []) then {
    _sameIdle = [120] call TRIBUNAL_CBR_fnc_waitIdle;
    _sameGun = "B_Mortar_01_F" createVehicle _warnGunPos;
    _sameGun setVectorUp (surfaceNormal (getPosATL _sameGun));
    createVehicleCrew _sameGun;
    _created pushBack _sameGun;
    private _sc = diag_tickTime + 10;
    waitUntil {uiSleep 0.1; !isNull (gunner _sameGun) || diag_tickTime > _sc};
    [_sameGun] call TRIBUNAL_CBR_fnc_firingPlatform;
    private _sameToken = format ["%1-cbr-same", _token];
    [_sameToken] call TRIBUNAL_fnc_artilleryObserverStart;
    [_sameToken, _sameGun, []] call TRIBUNAL_fnc_artilleryObserveSource;
    _sameGun doArtilleryFire [_warnTarget, _ordnance, 1];
    private _sd = diag_tickTime + 150;
    waitUntil {
        uiSleep 0.25;
        private _ev = ([_sameToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
        ((count _ev) >= 1 && {(_ev # 0) getOrDefault ["terminated", false]}) || diag_tickTime > _sd
    };
    _sameEvents = ([_sameToken] call TRIBUNAL_fnc_artilleryObserverStop) getOrDefault ["events", []];
};
missionNamespace setVariable ["TRIBUNAL_CBR_SAMESIDE_DONE", _token, true];

YOSHI_fnc_cbrWarnSidePlayers = TRIBUNAL_CBR_WARN_ORIGINAL;
YOSHI_fnc_cbrHandleLocalArtilleryFire = TRIBUNAL_CBR_HANDLE_ORIGINAL;
private _warnDistance = if ((count _observerPos) >= 2 && {!(_warnTarget isEqualTo [])}) then {_observerPos distance2D _warnTarget} else {-1};
// Exactly one emission may name the observer, and it must be the hostile salvo
// that landed inside the radius: not the distant salvo, not the friendly one.
private _naming = TRIBUNAL_CBR_WARN_CALLS select {_observerId in (_x # 2)};
private _emissionOk = (count _naming) isEqualTo 1
    && {((_naming # 0) # 0) isEqualTo east}
    && {(((_naming # 0) # 1) distance2D _warnTarget) < 50};
private _pipelineOk = !isNull _observer
    && {_farIdle} && {_warnIdle} && {_sameIdle}
    && {_warnDistance > 100} && {_warnDistance < 1000}
    && {(count _warnEvents) isEqualTo _warnShells}
    && {({_x getOrDefault ["artilleryEvent", false]} count _warnEvents) isEqualTo _warnShells}
    && {(count _sameEvents) isEqualTo 1}
    && {(_sameEvents # 0) getOrDefault ["artilleryEvent", false]}
    && {(side (group (gunner _warnGun))) isEqualTo east}
    && {(side (group (gunner _sameGun))) isEqualTo west}
    && {(side _observer) isEqualTo west}
    && {_emissionOk};
["cbr.warning.launchPipeline", _pipelineOk, format ["observer=%1|observerSide=%2|warnTarget=%3|distance=%4|hostileShells=%5|hostileArtilleryEvents=%6|friendlyShells=%7|idle=[%8,%9,%10]|emissionsNamingObserver=%11|allEmissions=%12|handlerCalls=%13|warnGunState=%14", _observerId, if (isNull _observer) then {"none"} else {str side _observer}, _warnTarget, _warnDistance, count _warnEvents, {_x getOrDefault ["artilleryEvent", false]} count _warnEvents, count _sameEvents, _farIdle, _warnIdle, _sameIdle, count _naming, TRIBUNAL_CBR_WARN_CALLS, TRIBUNAL_CBR_HANDLE_CALLS, _warnState]] call _assert;

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
    && {scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull])}
    && {scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])};
["cbr.lifecycle.stop", _stopOk, format ["stopped=%1|enabled=%2|zones=%3|origins=%4|clusters=%5|tracks=%6|manager=%7|origin=%8", _stopped, missionNamespace getVariable ["YOSHI_CBR_ENABLED", true], _stopZones, _stopOrigins, count YOSHI_CB_clusters, count YOSHI_originTrack, scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull]), scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])]] call _assert;

// ---------------------------------------------------------------- cleanup --
{
    if (!isNull _x) then {deleteVehicleCrew _x; deleteVehicle _x};
} forEach _created;
private _cleanupDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.1; ({!isNull _x} count _created) isEqualTo 0 || diag_tickTime > _cleanupDeadline};
{
    missionNamespace setVariable [_x, nil, true];
} forEach [
    "TRIBUNAL_CBR_PREDICTIONS", "TRIBUNAL_CBR_ZONE_RECORD", "TRIBUNAL_CBR_WARN_SHELLS",
    "TRIBUNAL_CBR_WARN_CALLS", "TRIBUNAL_CBR_WARN_ORIGINAL",
    "TRIBUNAL_CBR_HANDLE_CALLS", "TRIBUNAL_CBR_HANDLE_ORIGINAL",
    "TRIBUNAL_CBR_OBSERVER_client-a", "TRIBUNAL_CBR_SPY_ARMED", "TRIBUNAL_CBR_ENABLED_AT",
    "TRIBUNAL_CBR_FAR_DONE", "TRIBUNAL_CBR_WARN_DONE", "TRIBUNAL_CBR_SAMESIDE_DONE"
];
private _residual = ([_zonePrefix] call TRIBUNAL_fnc_markerNames) + ([_originPrefix] call TRIBUNAL_fnc_markerNames);
private _leftovers = [
    "TRIBUNAL_CBR_PREDICTIONS", "TRIBUNAL_CBR_ZONE_RECORD", "TRIBUNAL_CBR_WARN_SHELLS"
] select {!isNil {missionNamespace getVariable _x}};
private _cleanupOk = ({!isNull _x} count _created) isEqualTo 0
    && {_residual isEqualTo []}
    && {_leftovers isEqualTo []}
    && {(missionNamespace getVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""]) isEqualTo ""};
["cbr.cleanup", _cleanupOk, format ["fixturesAlive=%1|residualMarkers=%2|leftoverState=%3|artilleryActive=%4", {!isNull _x} count _created, _residual, _leftovers, missionNamespace getVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""]]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CBR_COMPLETE", _token, true];
''',
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "advanced-systems",
        "feature": "counter-battery-radar",
        "detection_source": "native-artillery",
        "evidence": "predicted-impact,map-markers,side-radio",
        # Without this the player respawns at the map origin, which on Stratis is
        # open water, leaving nowhere to place the artillery that must land
        # inside the observer's warning radius. Matches the fixed-wing scenarios.
        "respawn_on_start": "0",
        "observer_identities": ",".join(OBSERVER_IDENTITIES),
        "future_client_isolation": "client-b must observe the same authoritative markers and receive its own side-filtered warning",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract=(
            "While the system is enabled, hostile artillery fire produces an authoritative predicted-impact "
            "zone whose drawn centre matches the real impact area and whose label states the tracked shell "
            "count and remaining time, a launch-origin estimate that narrows with repeated fire until it is "
            "confirmed at the firing position, and one launch warning per airborne cycle delivered only to "
            "opposing-side players within the warning radius; all of it disappears when the threat expires and "
            "when the system is stopped, and a real shot produces nothing while it is disabled."
        ),
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale=(
            "Impact prediction integrated to sea level rather than to the ground under the projected point, "
            "placing the drawn zone tens of metres downrange of the real impact whenever the target was above "
            "the waterline. The scenario asserts predicted-versus-real impact per shell against Tribunal's "
            "independent launch and trajectory observer, and drives every warning claim — positive, "
            "out-of-radius and same-side — through real artillery launches rather than the warning helper. "
            "Cluster layout, marker names, uid format and polling cadence remain evidence adapters."
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
            "each observing client identity observes the same authoritative markers, receives its own "
            "side-filtered radio warning, and holds no cluster or origin state of its own."
        ),
    ),
)
