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
    "cbr.client.observationsReplicated",
    "cbr.client.visualEnvelope",
    "cbr.client.zoomClustering",
    "cbr.client.shapeEnvelope",
    "cbr.client.warningOutOfRadius",
    "cbr.client.warningDelivered",
    "cbr.client.warningSameSide",
})

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "pontifex.advanced-systems.counter-battery-radar",
        "version": 1,
        "feature_family": "pontifex-advanced-systems-cbr",
        "name": "Counter Battery Radar strike observations and scale-aware map presentation",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "mods/advanced-systems/tests/tribunal/counter_battery_radar.py",
            "applicability": "Arma 3 dedicated multiplayer with one authenticated client, native server-owned mortar shells, and the main client map control",
            "participants": {
                "server": "native artillery, prediction, durable observation, origin, warning and evidence authority",
                "client-a": "replicated-observation, local map-renderer and side-radio observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:advanced-systems:counter-battery-radar",
        "label": "Counter Battery Radar strike observations and map presentation",
        "kind": "product_behavior",
        "aliases": ["CBR", "counter-battery radar"],
        "biki_context": ["biki-page:8369", "biki-page:1644"],
    },
    "arms": [
        {"key": "disabled-real-shot", "role": "negative_control", "description": "A proven native artillery shot produces no observation, origin, warning-zone display, or retained state while CBR is disabled", "assertions": ["cbr.control.disabledShotProven", "cbr.control.disabledNoDetection"]},
        {"key": "tracked-native-salvo", "role": "treatment", "description": "Eight exact native shells produce eight independent timed uncertainty observations with provenance and terrain-accurate predictions", "assertions": ["cbr.detection.observations", "cbr.detection.provenance", "cbr.detection.timing", "cbr.prediction.impactAccuracy", "cbr.detection.zoneCentre"]},
        {"key": "scale-aware-map", "role": "treatment", "description": "Replicated real-shell rows render on the real client map and expire visually without becoming authoritative client state", "assertions": ["cbr.client.observationsReplicated", "cbr.client.visualEnvelope"]},
        {"key": "walking-close-map", "role": "positive_control", "description": "Four separated linear observations remain distinct at close map zoom", "assertions": ["cbr.client.zoomClustering"]},
        {"key": "walking-overview-map", "role": "treatment", "description": "The same four rows merge at overview zoom into a bounded elongated capsule without losing underlying identities", "assertions": ["cbr.client.zoomClustering", "cbr.client.shapeEnvelope"]},
        {"key": "warning-controls", "role": "treatment", "description": "A real hostile near salvo warns once while hostile-far and friendly-near launches do not", "assertions": ["cbr.warning.launchPipeline", "cbr.client.warningOutOfRadius", "cbr.client.warningDelivered", "cbr.client.warningSameSide"]},
        {"key": "origin-and-lifecycle", "role": "treatment", "description": "Origin uncertainty narrows to a confirmed launcher fix, observations expire independently, and stop/cleanup remove retained state", "assertions": ["cbr.origin.narrows", "cbr.origin.confirmed", "cbr.expiry.cleared", "cbr.lifecycle.start", "cbr.lifecycle.stop", "cbr.cleanup"]},
    ],
    "causal_relationships": [
        {"key": "enable-causes-observation", "relation": "COMPARES_WITH", "source": "tracked-native-salvo", "target": "disabled-real-shot", "controlled_dimensions": ["native mortar", "ammunition", "elevated target", "physical flight"]},
        {"key": "zoom-changes-presentation-only", "relation": "COMPARES_WITH", "source": "walking-overview-map", "target": "walking-close-map", "controlled_dimensions": ["four observation identities", "positions", "uncertainty geometry", "timing", "map control"]},
    ],
    "propositions": [{
        "id": "pontifex:advanced-systems:cbr-observation-presentation-contract",
        "text": "CBR retains one timed, provenance-bearing uncertainty observation per physical strike and derives non-destructive client-local visual clusters from current map scale; zooming changes only presentation, and linear barrages use a bounded elongated envelope instead of an enclosing circle.",
        "intended_use": "primary_result",
        "assertions": ["cbr.control.disabledShotProven", "cbr.control.disabledNoDetection", "cbr.detection.observations", "cbr.detection.provenance", "cbr.detection.timing", "cbr.prediction.impactAccuracy", "cbr.detection.zoneCentre", "cbr.client.observationsReplicated", "cbr.client.visualEnvelope", "cbr.client.zoomClustering", "cbr.client.shapeEnvelope", "cbr.expiry.cleared", "cbr.lifecycle.start", "cbr.lifecycle.stop", "cbr.cleanup"],
        "rationale": "Exact native shell identities and trajectories, unique stored UIDs, retained uncertainty/timing/provenance fields, client replication, two real map scales, unchanged underlying IDs, explicit capsule dimensions, disabled stimulus and full expiry/stop controls jointly exclude fixed-zone assignment, destructive aggregation, circle inflation, no-stimulus and ledger-only false passes.",
    }],
    "unresolved": ["Warning cadence, independent confirmed-origin expiry, authenticated owner-bound telemetry, marker audience, client-B/JIP and cross-owner artillery remain outside this resolved observation-and-presentation decision. No active-observation cap is introduced; future performance evidence may justify a separate bounded policy."],
}

CLIENT_SQF = marker_observer_sqf() + r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];

// Published first: the server places its artillery relative to a declared
// observer rather than whichever player happens to be first in allPlayers, and
// it needs that position before the fixture exists.
missionNamespace setVariable [format ["TRIBUNAL_CBR_OBSERVER_%1", _identity], netId player, true];

private _enabledDeadline = diag_tickTime + 240;
waitUntil {uiSleep 0.25; (missionNamespace getVariable ["TRIBUNAL_CBR_ENABLED_AT", ""]) isEqualTo _token || diag_tickTime > _enabledDeadline};
["cbr.client.enabledReplicated", (missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]) && {hasInterface} && {!isServer} && {_identity isNotEqualTo ""}, format ["enabled=%1|hasInterface=%2|server=%3|identity=%4", missionNamespace getVariable ["YOSHI_CBR_ENABLED", "missing"], hasInterface, isServer, _identity]] call _assert;

["cbr.client.noLocalState", (YOSHI_CB_observations isEqualTo []) && {(count YOSHI_originTrack) isEqualTo 0}, format ["identity=%1|serverObservations=%2|tracks=%3", _identity, count YOSHI_CB_observations, count YOSHI_originTrack]] call _assert;

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

// The map renderer is client-owned. Open the real map before the salvo and
// retain its local-marker lifecycle independently of the radio gates.
openMap true;
private _mapDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; visibleMap && {!isNull findDisplay 12} || {diag_tickTime > _mapDeadline}};
TRIBUNAL_CBR_ZONE_SAMPLES = nil;
TRIBUNAL_CBR_REPLICATED_PEAK = [];
private _zoneWorker = [] spawn {
    private _saw = false;
    TRIBUNAL_CBR_ZONE_SAMPLES = [
        "YOSHI_cb_",
        {
            params ["_census"];
            private _rows = missionNamespace getVariable ["YOSHI_CBR_OBSERVATIONS", []];
            if ((count _rows) > count TRIBUNAL_CBR_REPLICATED_PEAK) then {TRIBUNAL_CBR_REPLICATED_PEAK = +_rows};
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

// Replication is the durable observation ledger, not server-authored display
// clusters. The client derives a local capsule/ellipse and label from it.
private _zoneDeadline = diag_tickTime + 280;
waitUntil {uiSleep 0.5; (scriptDone _zoneWorker) || diag_tickTime > _zoneDeadline};
private _samples = if (isNil "TRIBUNAL_CBR_ZONE_SAMPLES") then {[]} else {TRIBUNAL_CBR_ZONE_SAMPLES};
private _zoneEvidence = [_samples] call TRIBUNAL_fnc_markerLifecycleEvidence;
private _authoritative = missionNamespace getVariable ["TRIBUNAL_CBR_ZONE_RECORD", []];
private _expectedCentre = _authoritative param [0, []];
private _expectedCount = _authoritative param [1, -1];
private _seen = _zoneEvidence getOrDefault ["everSeen", []];
private _iconTexts = [];
private _areaSeen = false;
{
    private _records = _x getOrDefault ["records", createHashMap];
    {
        private _record = _y;
        if ((_record getOrDefault ["color", ""]) isEqualTo "ColorRed"
            && {(_record getOrDefault ["shape", ""]) in ["ELLIPSE", "RECTANGLE"]}
            && {((_record getOrDefault ["position", [1e9,1e9,0]]) distance2D _expectedCentre) < 250}) then {_areaSeen = true};
        if ((_record getOrDefault ["type", ""]) isEqualTo "mil_warning") then {
            private _text = _record getOrDefault ["text", ""];
            if (_text isNotEqualTo "") then {_iconTexts pushBackUnique _text};
        };
    } forEach _records;
} forEach _samples;
// The label itself must replicate, not merely a marker of the right type. The
// count field is asserted exactly against the authoritative peak; the countdown
// digits are not, because they change every product tick and this client samples
// at a fixed interval.
private _countPrefix = format ["%1 shells | ETA ", _expectedCount];
private _labelSeen = _expectedCount > 0
    && {(_iconTexts findIf {(_x find _countPrefix) isEqualTo 0 && {(_x select [(count _x) - 1]) isEqualTo "s"}}) >= 0};
private _originDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.25; (scriptDone _originWorker) || diag_tickTime > _originDeadline};
private _originSeen = TRIBUNAL_CBR_ORIGIN_SEEN;
private _replicated = +TRIBUNAL_CBR_REPLICATED_PEAK;
private _replicatedOk = _expectedCount > 0
    && {(count _replicated) >= _expectedCount}
    && {((count (_replicated apply {_x # 0})) isEqualTo count ((_replicated apply {_x # 0}) arrayIntersect (_replicated apply {_x # 0})))}
    && {(_replicated findIf {(count _x) >= 8 && {(_x # 2) isEqualTo ["ellipse", [100,100], 0]} && {(count (_x # 7)) >= 5}}) >= 0};
["cbr.client.observationsReplicated", _replicatedOk, format ["identity=%1|expected=%2|replicated=%3|rows=%4", _identity, _expectedCount, count _replicated, _replicated]] call _assert;
private _visualOk = _areaSeen
    && {(_seen findIf {(_x find "YOSHI_cb_view_") isEqualTo 0}) >= 0}
    && {_zoneEvidence getOrDefault ["cleared", false]}
    && {(_originSeen findIf {(_x find "YOSHI_origin") isEqualTo 0}) >= 0}
    && {_labelSeen};
["cbr.client.visualEnvelope", _visualOk, format ["identity=%1|centre=%2|everSeen=%3|area=%4|cleared=%5|origin=%6|expectedCount=%7|label=%8|texts=%9", _identity, _expectedCentre, _seen, _areaSeen, _zoneEvidence getOrDefault ["cleared", false], _originSeen, _expectedCount, _labelSeen, _iconTexts]] call _assert;

// Controlled presentation arm: four durable observations form a straight
// walking barrage. The real map control must split them when zoomed in and
// merge them when zoomed out, without altering the four underlying rows.
private _map = (findDisplay 12) displayCtrl 51;
private _base = getPosASL player;
private _synthetic = [];
for "_i" from 0 to 3 do {
    _synthetic pushBack [
        format ["%1-walk-%2", _token, _i],
        [(_base # 0) + ((_i - 1.5) * 300), _base # 1, 0],
        ["ellipse", [100,100], 0], time, time, 30 - _i, time + 40,
        [clientOwner, "synthetic-walking-barrage", "mortar", "mortar", "EAST", clientOwner]
    ];
};
missionNamespace setVariable ["YOSHI_CBR_OBSERVATIONS", +_synthetic];
private _centre = [(_base # 0), _base # 1, 0];
_map ctrlMapAnimAdd [0, 0.01, _centre];
ctrlMapAnimCommit _map;
uiSleep 0.5;
[_map] call YOSHI_CB_renderMap;
private _zoomInScale = ctrlMapScale _map;
private _zoomInCount = count YOSHI_CB_visualClusters;
_map ctrlMapAnimAdd [0, 1.0, _centre];
ctrlMapAnimCommit _map;
uiSleep 0.5;
[_map] call YOSHI_CB_renderMap;
private _zoomOutScale = ctrlMapScale _map;
private _zoomOut = +YOSHI_CB_visualClusters;
private _zoomOutCount = count _zoomOut;
private _underlyingAfter = missionNamespace getVariable ["YOSHI_CBR_OBSERVATIONS", []];
private _zoomOk = _zoomInScale < _zoomOutScale
    && {_zoomInCount > _zoomOutCount} && {_zoomOutCount isEqualTo 1}
    && {(count _underlyingAfter) isEqualTo count _synthetic}
    && {((_underlyingAfter apply {_x # 0}) isEqualTo (_synthetic apply {_x # 0}))};
["cbr.client.zoomClustering", _zoomOk, format ["scales=%1/%2|clusters=%3/%4|underlying=%5|ids=%6", _zoomInScale, _zoomOutScale, _zoomInCount, _zoomOutCount, count _underlyingAfter, _underlyingAfter apply {_x # 0}]] call _assert;
private _envelope = _zoomOut param [0, []];
private _halfLength = _envelope param [3, 0];
private _radius = _envelope param [4, 1e9];
private _shapeOk = (_envelope param [8, 0]) isEqualTo 4
    && {_halfLength > (3 * _radius)}
    && {_radius <= 110}
    && {(count (_envelope param [9, []])) isEqualTo 4}
    && {(markerShape (YOSHI_CB_renderMarkers param [0, ""])) isEqualTo "RECTANGLE"};
["cbr.client.shapeEnvelope", _shapeOk, format ["envelope=%1|halfLength=%2|radius=%3|markers=%4", _envelope, _halfLength, _radius, YOSHI_CB_renderMarkers apply {[_x, markerShape _x, markerSize _x]}]] call _assert;
missionNamespace setVariable ["YOSHI_CBR_OBSERVATIONS", []];
call YOSHI_CB_clearRenderMarkers;
openMap false;

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
        "cbr.detection.observations",
        "cbr.detection.provenance",
        "cbr.detection.timing",
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
    && {YOSHI_CB_observations isEqualTo []}
    && {_disabledZones isEqualTo []}
    && {_disabledOrigins isEqualTo []}
    && {(count YOSHI_originTrack) isEqualTo 0};
["cbr.control.disabledNoDetection", _disabledOk, format ["shotProven=%1|enabled=%2|observations=%3|zones=%4|origins=%5|tracks=%6", _controlShotOk, _disabledEnabled, count YOSHI_CB_observations, _disabledZones, _disabledOrigins, count YOSHI_originTrack]] call _assert;

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
private _peakObservations = [];
private _peakEtaMin = -1;
private _peakEtaMax = -1;
private _peakAt = -1;
private _originRadii = [];
private _confirmedSeen = false;

[_gun] call TRIBUNAL_CBR_fnc_firingPlatform;
_gun doArtilleryFire [_target, _ordnance, _rounds];

private _flightDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.25;
    private _current = +YOSHI_CB_observations;
    if ((count _current) > _peakMembers) then {
        _peakMembers = count _current;
        _peakObservations = _current;
        private _sumX = 0;
        private _sumY = 0;
        {_sumX = _sumX + ((_x # 1) # 0); _sumY = _sumY + ((_x # 1) # 1)} forEach _current;
        _peakCentre = [_sumX / _peakMembers, _sumY / _peakMembers, 0];
        private _etas = _current apply {_x # 5};
        _peakEtaMin = selectMin _etas;
        _peakEtaMax = selectMax _etas;
        // The instant the ledger was read, so the shells that were really in
        // the air at that moment can be recovered from their own timings.
        _peakAt = diag_tickTime;
    };
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
missionNamespace setVariable ["TRIBUNAL_CBR_ZONE_RECORD", [_peakCentre, _peakMembers], true];

private _uids = _peakObservations apply {_x # 0};
private _observationsOk = _observed && {(count _events) isEqualTo _rounds} && {_peakMembers >= 2}
    && {(count _uids) isEqualTo count (_uids arrayIntersect _uids)}
    && {(_peakObservations findIf {(count _x) < 8 || {!((_x # 2) isEqualTo ["ellipse", [100,100], 0])} || {(_x # 3) > (_x # 4)} || {(_x # 6) <= (_x # 4)}}) < 0};
["cbr.detection.observations", _observationsOk, format ["observed=%1|events=%2|peak=%3|uids=%4|rows=%5", _observed, count _events, _peakMembers, _uids, _peakObservations]] call _assert;
private _provenanceOk = _peakMembers > 0
    && {(_peakObservations findIf {(count (_x # 7)) < 6 || {((_x # 7) # 1) isNotEqualTo netId _gun} || {((_x # 7) # 2) isEqualTo ""} || {((_x # 7) # 3) isEqualTo ""}}) < 0};
["cbr.detection.provenance", _provenanceOk, format ["gun=%1|rows=%2", netId _gun, _peakObservations apply {_x # 7}]] call _assert;

// The ledger is captured while the threat is live: it expires shortly after
// each shell lands. Its aggregate label inputs must state count and remaining time,
// and that time must be consistent with the flights Tribunal measured.
private _flights = _predictions apply {_x # 4};
private _maximumFlight = if (_flights isEqualTo []) then {0} else {selectMax _flights};
// Independent physical oracle for the label. Comparing the drawn text with the
// cluster fields that generated it only proves the product formats its own state
// consistently, so the count and remaining time are instead recovered from the
// projectiles Tribunal observed: which ones were genuinely in the air when the
// label was read, and how much flight each of them actually had left, measured
// from its own terminal timestamp.
//
// Boundary band: a shell can be counted slightly before its first track update
// reaches the server, and a landed shell lingers about a second until its
// member entry expires, so membership is asserted as a range between the shells
// that were definitely airborne and those that could still have been.
private _band = 1.5;
private _strictLive = [];
private _looseLive = [];
private _remaining = [];
{
    // A shell is not a network object, so netId reports "0:0" for all of them.
    // The observer's own event index is the stable identity of one physically
    // observed projectile, carried with its class and real launch/impact times.
    private _identity = [_x getOrDefault ["index", -1], _x getOrDefault ["projectileClass", ""]];
    private _firedAt = _x getOrDefault ["firedAt", -1];
    private _endedAt = _x getOrDefault ["terminatedAt", -1];
    if (_firedAt >= 0 && {_endedAt > 0} && {_x getOrDefault ["terminated", false]}) then {
        if (_firedAt <= (_peakAt - _band) && {_endedAt >= (_peakAt + _band)}) then {
            _strictLive pushBack [_identity, _firedAt, _endedAt, _endedAt - _peakAt];
            _remaining pushBack (_endedAt - _peakAt);
        };
        if (_firedAt <= (_peakAt + _band) && {_endedAt >= (_peakAt - _band)}) then {
            _looseLive pushBack _identity;
        };
    };
} forEach _events;
private _derivedMin = if (_remaining isEqualTo []) then {-1} else {selectMin _remaining};
private _derivedMax = if (_remaining isEqualTo []) then {-1} else {selectMax _remaining};
// The tolerance is deliberately asymmetric, because the error has a direction.
// A displayed ETA is computed from a track update up to 0.5 s old, is rounded up
// to whole seconds, and is read by a 0.25 s poll, so it legitimately runs *ahead*
// of the truth; under load the product's per-shell update spawns lag further
// still, and a measured run showed +2.17 s. Over-reporting is therefore allowed
// 4 s. Nothing makes a displayed ETA legitimately *shorter* than the real
// remaining flight except rounding and the ~0.13 s prediction error, so
// under-reporting is held to 1.5 s. Both bounds sit far below the ~27 s flight
// they describe, and the prediction defect itself is guarded by the 20 m
// position bound in cbr.prediction.impactAccuracy rather than by this label check.
private _etaOverTolerance = 4;
private _etaUnderTolerance = 1.5;
private _countOk = (count _strictLive) >= 4
    && {_peakMembers >= (count _strictLive)}
    && {_peakMembers <= (count _looseLive)};
private _minDelta = _peakEtaMin - _derivedMin;
private _maxDelta = _peakEtaMax - _derivedMax;
private _etaOk = (count _remaining) >= 4
    && {_minDelta <= _etaOverTolerance} && {_minDelta >= -_etaUnderTolerance}
    && {_maxDelta <= _etaOverTolerance} && {_maxDelta >= -_etaUnderTolerance};
private _timingOk = _peakEtaMin >= 0 && {_peakEtaMin <= _peakEtaMax}
    && {_countOk} && {_etaOk};
["cbr.detection.timing", _timingOk, format ["peakAt=%1|storedCount=%2|liveDefinite=%3|livePossible=%4|storedEta=%5-%6|derivedEta=%7-%8|delta=%9/%10|tolerance=+%11/-%12|liveDetail=%13", _peakAt, _peakMembers, count _strictLive, count _looseLive, _peakEtaMin, _peakEtaMax, _derivedMin, _derivedMax, _minDelta, _maxDelta, _etaOverTolerance, _etaUnderTolerance, _strictLive]] call _assert;

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

private _expiryDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.25; YOSHI_CB_observations isEqualTo [] || {diag_tickTime > _expiryDeadline}};
private _expiryOk = _peakMembers > 0 && {YOSHI_CB_observations isEqualTo []}
    && {(missionNamespace getVariable ["YOSHI_CBR_OBSERVATIONS", [["stale"]]]) isEqualTo []};
["cbr.expiry.cleared", _expiryOk, format ["peakMembers=%1|serverRows=%2|publishedRows=%3", _peakMembers, count YOSHI_CB_observations, count (missionNamespace getVariable ["YOSHI_CBR_OBSERVATIONS", []])]] call _assert;

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
    && {YOSHI_CB_observations isEqualTo []}
    && {(count YOSHI_originTrack) isEqualTo 0}
    && {scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull])}
    && {scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])};
["cbr.lifecycle.stop", _stopOk, format ["stopped=%1|enabled=%2|zones=%3|origins=%4|observations=%5|tracks=%6|manager=%7|origin=%8", _stopped, missionNamespace getVariable ["YOSHI_CBR_ENABLED", true], _stopZones, _stopOrigins, count YOSHI_CB_observations, count YOSHI_originTrack, scriptDone (missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull]), scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])]] call _assert;

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
        "evidence": "predicted-impact,strike-observations,zoom-aware-local-map,side-radio",
        # Without this the player respawns at the map origin, which on Stratis is
        # open water, leaving nowhere to place the artillery that must land
        # inside the observer's warning radius. Matches the fixed-wing scenarios.
        "respawn_on_start": "0",
        "observer_identities": ",".join(OBSERVER_IDENTITIES),
        "future_client_isolation": "client-b must receive the same authoritative observations, derive its own map presentation, and receive its own side-filtered warning",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract=(
            "While the system is enabled, each hostile artillery shell produces an independent authoritative "
            "predicted-impact observation retaining uncertainty, timing and provenance. Each client dynamically "
            "clusters those observations for its current map scale without destroying them and renders a bounded "
            "shape-preserving envelope and count/ETA label. A launch-origin estimate narrows with repeated fire until it is "
            "confirmed at the firing position, and one launch warning per airborne cycle delivered only to "
            "opposing-side players within the warning radius; all of it disappears when the threat expires and "
            "when the system is stopped, and a real shot produces nothing while it is disabled."
        ),
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale=(
            "The terrain prediction defect was corrected, and fixed 100-metre server clusters were replaced by "
            "durable per-strike observations plus client-local screen-space clustering. The scenario asserts "
            "exact real-shell storage, timing and provenance, real-map zoom split/merge, a shape-preserving "
            "walking-barrage capsule, prediction versus real impact, and every warning claim through native launches."
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
            "The dedicated server owns detection, observations, prediction and origin estimation. Each observing "
            "client receives the authoritative observation rows, derives disposable visual clusters on its own "
            "map control, receives its side-filtered radio warning, and owns no authoritative observation state."
        ),
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
