"""Causal Tier 3 coverage for Advanced Systems OPHANIM / Iron Dome."""

from tribunal.mission.artillery import artillery_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


SERVER_EXPECTED = frozenset({
    "iron.fixture.nativeArtillery",
    "iron.control.disabledImpact",
    "iron.control.disabledNoEngagement",
    "iron.launcher.registered",
    "iron.positive.exactIntercept",
    "iron.positive.physicalInterceptor",
    "iron.positive.protected",
    "iron.concurrent.distinctThreats",
    "iron.concurrent.protected",
    "iron.control.outOfRangeImpact",
    "iron.control.outOfRangeNoEngagement",
    "iron.authority.rejected",
    "iron.locality",
    "iron.cleanup",
})

CLIENT_EXPECTED = frozenset({
    "iron.client.authorityStimulus",
    "iron.client.eventReplicated",
})

CLIENT_SQF = r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];

private _authDeadline = diag_tickTime + 240;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_IRON_AUTH_BOX", ""]) isNotEqualTo ""
        || {diag_tickTime > _authDeadline}
};
private _authId = missionNamespace getVariable ["TRIBUNAL_IRON_AUTH_BOX", ""];
private _authBox = if (_authId isEqualTo "") then {objNull} else {objectFromNetId _authId};
private _sent = !isNull _authBox;
if (_sent) then {
    [_authBox, format ["untrusted-%1", _token]] remoteExecCall ["YAS_fnc_ironDomeRegisterBox", 2];
};
missionNamespace setVariable ["TRIBUNAL_IRON_AUTH_SENT", [_token, _identity, _authId], true];
["iron.client.authorityStimulus", _sent && {_identity isEqualTo "client-a"}, format ["identity=%1|box=%2|null=%3", _identity, _authId, isNull _authBox]] call _assert;

private _eventDeadline = diag_tickTime + 300;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_IRON_EXPECTED_EVENT_TOKEN", ""]) isEqualTo _token
        || {diag_tickTime > _eventDeadline}
};
private _expected = missionNamespace getVariable ["TRIBUNAL_IRON_EXPECTED_EVENT", []];
private _events = missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []];
private _matched = _events select {
    (_x param [0, ""]) isEqualTo (_expected param [0, "missing-shell"])
        && {(_x param [1, ""]) isEqualTo (_expected param [1, "missing-launcher"])}
        && {(_x param [2, ""]) isEqualTo (_expected param [2, "missing-interceptor"])}
        && {(_x param [3, ""]) isEqualTo "intercepted"}
};
private _replicated = (count _expected) >= 3
    && {(count _matched) isEqualTo 1}
    && {_matched # 0 param [8, false]}
    && {_matched # 0 param [9, false]};
["iron.client.eventReplicated", _replicated, format ["identity=%1|expected=%2|matches=%3|events=%4", _identity, _expected, count _matched, count _events]] call _assert;
'''


SERVER_SQF = artillery_observer_sqf() + r'''
private _created = [];
private _targetPos = [4500, 3500, 0];
private _gunPos = [4000, 3500, 0];
private _radius = 1000;
YAS_ironDomeEngagementRadius = _radius;
missionNamespace setVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", [], true];
missionNamespace setVariable ["YAS_IRONDOME_AUDIT", [], false];
missionNamespace setVariable ["TRIBUNAL_IRON_SHOTS", []];
missionNamespace setVariable ["TRIBUNAL_IRON_HITS", []];
missionNamespace setVariable ["TRIBUNAL_IRON_INTERCEPTORS", []];
missionNamespace setVariable ["TRIBUNAL_IRON_ACTIVE_LABEL", ""];

// Product-neutral exact shell evidence.  The product handler was installed at
// postInit, before this observer, so its stable uid is available here whenever
// a launcher made the shell eligible.
private _shellEh = addMissionEventHandler ["ArtilleryShellFired", {
    params ["_vehicle", "_weapon", "_ammo", "_gunner", "_instigator", "_artilleryTarget", "_targetPosition", "_shell"];
    private _label = missionNamespace getVariable ["TRIBUNAL_IRON_ACTIVE_LABEL", "unlabelled"];
    private _shots = missionNamespace getVariable ["TRIBUNAL_IRON_SHOTS", []];
    private _testUid = format ["tribunal-iron-%1-%2-%3", _label, count _shots, round (diag_tickTime * 1000)];
    _shell setVariable ["TRIBUNAL_IRON_UID", _testUid, true];
    private _record = createHashMapFromArray [
        ["label", _label], ["testUid", _testUid],
        ["productUid", _shell getVariable ["YAS_ironDome_uid", ""]],
        ["object", _shell], ["class", typeOf _shell], ["local", local _shell],
        ["initialPosition", getPosASL _shell], ["initialVelocity", velocity _shell],
        ["samples", []], ["lastPosition", []], ["closestTarget", 1e9],
        ["terminated", false], ["artilleryEvent", true]
    ];
    _shots pushBack _record;
    missionNamespace setVariable ["TRIBUNAL_IRON_SHOTS", _shots];
    [_record, _shell, missionNamespace getVariable ["TRIBUNAL_IRON_TARGET", objNull]] spawn {
        params ["_record", "_shell", "_target"];
        private _deadline = diag_tickTime + 60;
        while {!isNull _shell && {diag_tickTime < _deadline}} do {
            private _position = getPosASL _shell;
            private _samples = _record getOrDefault ["samples", []];
            _samples pushBack [diag_tickTime, _position, velocity _shell, local _shell];
            _record set ["samples", _samples];
            _record set ["lastPosition", _position];
            if (!isNull _target) then {
                _record set ["closestTarget", (_record getOrDefault ["closestTarget", 1e9]) min (_shell distance _target)];
            };
            uiSleep 0.01;
        };
        _record set ["terminated", isNull _shell];
    };
}];

// Ammo-class objects did not emit the mission EntityCreated event on this
// dedicated build.  Observe every physical interceptor independently of the
// product ledger with a bounded frame-level object scan instead.
missionNamespace setVariable ["TRIBUNAL_IRON_OBSERVER_ACTIVE", true];
private _interceptorObserver = [] spawn {
    private _seen = [];
    while {missionNamespace getVariable ["TRIBUNAL_IRON_OBSERVER_ACTIVE", false]} do {
        {
            private _entity = _x;
            if !(_entity in _seen) then {
                _seen pushBack _entity;
                private _record = createHashMapFromArray [
                    ["object", _entity], ["uid", _entity getVariable ["YAS_ironDome_uid", ""]], ["samples", []],
                    ["initialPosition", getPosASL _entity], ["lastPosition", getPosASL _entity],
                    ["closestShell", 1e9], ["local", local _entity], ["terminated", false]
                ];
                private _all = missionNamespace getVariable ["TRIBUNAL_IRON_INTERCEPTORS", []];
                _all pushBack _record;
                missionNamespace setVariable ["TRIBUNAL_IRON_INTERCEPTORS", _all];
                [_record, _entity] spawn {
                    params ["_record", "_entity"];
                    private _deadline = diag_tickTime + 15;
                    while {!isNull _entity && {diag_tickTime < _deadline}} do {
                        private _uid = _entity getVariable ["YAS_ironDome_uid", ""];
                        if (_uid isNotEqualTo "") then {_record set ["uid", _uid]};
                        private _position = getPosASL _entity;
                        private _samples = _record getOrDefault ["samples", []];
                        _samples pushBack [diag_tickTime, _position, velocity _entity, local _entity];
                        _record set ["samples", _samples];
                        _record set ["lastPosition", _position];
                        {
                            private _shell = _x getOrDefault ["object", objNull];
                            if (!isNull _shell) then {
                                _record set ["closestShell", (_record getOrDefault ["closestShell", 1e9]) min (_entity distance _shell)];
                            };
                        } forEach (missionNamespace getVariable ["TRIBUNAL_IRON_SHOTS", []]);
                        uiSleep 0.01;
                    };
                    _record set ["terminated", isNull _entity];
                };
            };
        } forEach (allMissionObjects "M_Jian_AT");
        uiSleep 0.001;
    };
};

private _target = createVehicle ["O_MBT_02_cannon_F", _targetPos, [], 0, "NONE"];
_created pushBack _target;
_target setFuel 0;
_target engineOn false;
_target allowDamage true;
missionNamespace setVariable ["TRIBUNAL_IRON_TARGET", _target];
_target addEventHandler ["HitPart", {
    {
        private _projectile = _x param [2, objNull];
        if (!isNull _projectile) then {
            private _uid = _projectile getVariable ["TRIBUNAL_IRON_UID", ""];
            if (_uid isNotEqualTo "") then {
                private _hits = missionNamespace getVariable ["TRIBUNAL_IRON_HITS", []];
                _hits pushBackUnique _uid;
                missionNamespace setVariable ["TRIBUNAL_IRON_HITS", _hits];
            };
        };
    } forEach _this;
}];

private _gun = createVehicle ["B_Mortar_01_F", _gunPos, [], 0, "NONE"];
_created pushBack _gun;
createVehicleCrew _gun;
{_created pushBack _x} forEach crew _gun;
private _ammo = (getArtilleryAmmo [_gun]) param [0, ""];
private _nativeReady = _ammo isNotEqualTo ""
    && {_targetPos inRangeOfArtillery [[_gun], _ammo]}
    && {local _gun}
    && {!isNull gunner _gun};
["iron.fixture.nativeArtillery", _nativeReady, format ["gun=%1|ammo=%2|inRange=%3|local=%4|gunner=%5", netId _gun, _ammo, _targetPos inRangeOfArtillery [[_gun], _ammo], local _gun, netId gunner _gun]] call _assert;
[_token] call TRIBUNAL_fnc_artilleryObserverStart;
[_token, _gun, [_targetPos, _targetPos, _targetPos, _targetPos, _targetPos]] call TRIBUNAL_fnc_artilleryObserveSource;
uiSleep 3;

TRIBUNAL_IRON_fnc_fire = {
    params ["_label", "_rounds", "_gun", "_ammo", "_targetPos"];
    private _before = count (missionNamespace getVariable ["TRIBUNAL_IRON_SHOTS", []]);
    missionNamespace setVariable ["TRIBUNAL_IRON_ACTIVE_LABEL", _label];
    _gun doArtilleryFire [_targetPos, _ammo, _rounds];
    private _launchDeadline = diag_tickTime + 30;
    waitUntil {
        uiSleep 0.05;
        (count (missionNamespace getVariable ["TRIBUNAL_IRON_SHOTS", []])) >= (_before + _rounds)
            || {diag_tickTime > _launchDeadline}
    };
    private _records = (missionNamespace getVariable ["TRIBUNAL_IRON_SHOTS", []]) select {
        (_x getOrDefault ["label", ""]) isEqualTo _label
    };
    private _terminalDeadline = diag_tickTime + 60;
    waitUntil {
        uiSleep 0.05;
        ((count _records) isEqualTo _rounds && {{_x getOrDefault ["terminated", false]} count _records isEqualTo _rounds})
            || {diag_tickTime > _terminalDeadline}
    };
    uiSleep 2;
    _records
};

// Disabled/no-launcher causal control: prove the real native shell exists,
// travels, hits this exact target and damages it before absence of engagement
// is allowed to mean anything.
private _eventsBeforeDisabled = count (missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []]);
private _damageBeforeDisabled = damage _target;
private _disabled = ["disabled", 1, _gun, _ammo, _targetPos] call TRIBUNAL_IRON_fnc_fire;
private _disabledRecord = _disabled param [0, createHashMap];
private _disabledUid = _disabledRecord getOrDefault ["testUid", ""];
private _disabledHit = _disabledUid isNotEqualTo "" && {_disabledUid in (missionNamespace getVariable ["TRIBUNAL_IRON_HITS", []])};
private _disabledPhysical = (count _disabled) isEqualTo 1
    && {_disabledRecord getOrDefault ["artilleryEvent", false]}
    && {_disabledRecord getOrDefault ["local", false]}
    && {(count (_disabledRecord getOrDefault ["samples", []])) > 20}
    && {_disabledRecord getOrDefault ["terminated", false]}
    && {_disabledHit}
    && {(damage _target) > (_damageBeforeDisabled + 0.001)};
["iron.control.disabledImpact", _disabledPhysical, format ["uid=%1|class=%2|samples=%3|closest=%4|hit=%5|damage=%6>%7", _disabledUid, _disabledRecord getOrDefault ["class", ""], count (_disabledRecord getOrDefault ["samples", []]), _disabledRecord getOrDefault ["closestTarget", -1], _disabledHit, damage _target, _damageBeforeDisabled]] call _assert;
private _eventsAfterDisabled = missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []];
["iron.control.disabledNoEngagement", (count _eventsAfterDisabled) isEqualTo _eventsBeforeDisabled, format ["before=%1|after=%2|stimulus=%3", _eventsBeforeDisabled, count _eventsAfterDisabled, _disabledPhysical]] call _assert;

_target setDamage 0;
uiSleep 3;
private _launcher = createVehicle ["YAS_OPHANIM_box", [4515, 3500, 0], [], 0, "NONE"];
_created pushBack _launcher;
private _registryDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; _launcher in YAS_IRONDOME_REGISTRY || {diag_tickTime > _registryDeadline}};
private _launcherUid = _launcher getVariable ["YAS_ironDome_uid", ""];
private _registered = _launcher in YAS_IRONDOME_REGISTRY
    && {_launcher getVariable ["YAS_ironDome_enabled", false]};
["iron.launcher.registered", _registered, format ["launcher=%1|uid=%2|enabled=%3|registry=%4", netId _launcher, _launcherUid, _launcher getVariable ["YAS_ironDome_enabled", false], count YAS_IRONDOME_REGISTRY]] call _assert;

// Positive case: same real mortar, ammunition, target and aim point.
private _damageBeforePositive = damage _target;
private _positive = ["positive", 1, _gun, _ammo, _targetPos] call TRIBUNAL_IRON_fnc_fire;
private _positiveRecord = _positive param [0, createHashMap];
private _positiveTestUid = _positiveRecord getOrDefault ["testUid", ""];
private _positiveProductUid = _positiveRecord getOrDefault ["productUid", ""];
private _productEvents = missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []];
private _successes = _productEvents select {(_x param [0, ""]) isEqualTo _positiveProductUid && {(_x param [3, ""]) isEqualTo "intercepted"}};
private _launches = _productEvents select {(_x param [0, ""]) isEqualTo _positiveProductUid && {(_x param [3, ""]) isEqualTo "launched"}};
private _success = _successes param [0, []];
private _exact = _positiveProductUid isNotEqualTo ""
    && {(count _successes) isEqualTo 1}
    && {(count _launches) isEqualTo 1}
    && {(_success param [1, ""]) isEqualTo (_launcher getVariable ["YAS_ironDome_uid", ""])}
    && {(_success param [2, ""]) isNotEqualTo ""}
    && {(_success param [4, 0]) isEqualTo 1};
["iron.positive.exactIntercept", _exact, format ["testUid=%1|productUid=%2|successes=%3|launches=%4|event=%5", _positiveTestUid, _positiveProductUid, count _successes, count _launches, _success]] call _assert;

private _interceptorUid = _success param [2, ""];
private _interceptorRecords = (missionNamespace getVariable ["TRIBUNAL_IRON_INTERCEPTORS", []]) select {(_x getOrDefault ["uid", ""]) isEqualTo _interceptorUid};
private _interceptor = _interceptorRecords param [0, createHashMap];
private _interceptorSamples = _interceptor getOrDefault ["samples", []];
private _travel = if ((count _interceptorSamples) >= 2) then {((_interceptorSamples # 0) # 1) distance ((_interceptorSamples select ((count _interceptorSamples) - 1)) # 1)} else {0};
private _physicalInterceptor = (count _interceptorRecords) isEqualTo 1
    && {_interceptor getOrDefault ["local", false]}
    && {(count _interceptorSamples) > 5}
    && {_travel > 20}
    && {(_interceptor getOrDefault ["closestShell", 1e9]) <= YAS_IRONDOME_FUSE_DISTANCE};
["iron.positive.physicalInterceptor", _physicalInterceptor, format ["uid=%1|records=%2|samples=%3|travel=%4|closestShell=%5|local=%6", _interceptorUid, count _interceptorRecords, count _interceptorSamples, _travel, _interceptor getOrDefault ["closestShell", -1], _interceptor getOrDefault ["local", false]]] call _assert;
private _positiveHit = _positiveTestUid in (missionNamespace getVariable ["TRIBUNAL_IRON_HITS", []]);
private _protected = _positiveRecord getOrDefault ["terminated", false]
    && {!_positiveHit}
    && {(damage _target) <= (_damageBeforePositive + 0.001)}
    && {_disabledPhysical};
["iron.positive.protected", _protected, format ["uid=%1|hit=%2|damage=%3>%4|disabledImpact=%5", _positiveTestUid, _positiveHit, damage _target, _damageBeforePositive, _disabledPhysical]] call _assert;
missionNamespace setVariable ["TRIBUNAL_IRON_EXPECTED_EVENT", [_success param [0, ""], _success param [1, ""], _success param [2, ""]], true];
missionNamespace setVariable ["TRIBUNAL_IRON_EXPECTED_EVENT_TOKEN", _token, true];

// Two live shells exercise dedupe/assignment without asserting private queue
// layout or the exact configured spacing interval.  A shell deleted by an
// interceptor can leave the AI artillery command occupied until its original
// impact time, so each later phase uses a fresh identically configured mortar
// rather than allowing stale AI command state to suppress the stimulus.
{deleteVehicle _x} forEach crew _gun;
deleteVehicle _gun;
_gun = createVehicle ["B_Mortar_01_F", _gunPos, [], 0, "NONE"];
_created pushBack _gun;
createVehicleCrew _gun;
{_created pushBack _x} forEach crew _gun;
_ammo = (getArtilleryAmmo [_gun]) param [0, ""];
[_token, _gun, [_targetPos, _targetPos]] call TRIBUNAL_fnc_artilleryObserveSource;
_target setDamage 0;
uiSleep 3;
private _concurrent = ["concurrent", 2, _gun, _ammo, _targetPos] call TRIBUNAL_IRON_fnc_fire;
private _concurrentProductUids = _concurrent apply {_x getOrDefault ["productUid", ""]};
private _concurrentTestUids = _concurrent apply {_x getOrDefault ["testUid", ""]};
private _concurrentSuccess = (missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []]) select {
    (_x param [0, ""]) in _concurrentProductUids && {(_x param [3, ""]) isEqualTo "intercepted"}
};
private _concurrentMissiles = _concurrentSuccess apply {_x param [2, ""]};
private _distinct = (count _concurrent) isEqualTo 2
    && {(count (_concurrentProductUids arrayIntersect _concurrentProductUids)) isEqualTo 2}
    && {(count _concurrentSuccess) isEqualTo 2}
    && {(count (_concurrentMissiles arrayIntersect _concurrentMissiles)) isEqualTo 2};
["iron.concurrent.distinctThreats", _distinct, format ["shells=%1|successes=%2|missiles=%3", _concurrentProductUids, count _concurrentSuccess, _concurrentMissiles]] call _assert;
private _concurrentHits = _concurrentTestUids select {_x in (missionNamespace getVariable ["TRIBUNAL_IRON_HITS", []])};
["iron.concurrent.protected", _distinct && {_concurrentHits isEqualTo []} && {damage _target <= 0.001}, format ["hits=%1|damage=%2|shells=%3", _concurrentHits, damage _target, _concurrentTestUids]] call _assert;

// Out-of-range control: a registered, enabled launcher remains present but is
// unambiguously farther away than the configured threshold.  The same real
// shell must again hit before no engagement can pass.
deleteVehicle _launcher;
uiSleep 1;
private _farLauncher = createVehicle ["YAS_OPHANIM_box", [6500, 6500, 0], [], 0, "NONE"];
_created pushBack _farLauncher;
{deleteVehicle _x} forEach crew _gun;
deleteVehicle _gun;
_gun = createVehicle ["B_Mortar_01_F", _gunPos, [], 0, "NONE"];
_created pushBack _gun;
createVehicleCrew _gun;
{_created pushBack _x} forEach crew _gun;
_ammo = (getArtilleryAmmo [_gun]) param [0, ""];
[_token, _gun, [_targetPos]] call TRIBUNAL_fnc_artilleryObserveSource;
YAS_ironDomeEngagementRadius = 300;
_target setDamage 0;
uiSleep 3;
private _eventsBeforeFar = count (missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []]);
private _far = ["far", 1, _gun, _ammo, _targetPos] call TRIBUNAL_IRON_fnc_fire;
private _farRecord = _far param [0, createHashMap];
private _farUid = _farRecord getOrDefault ["testUid", ""];
private _farHit = _farUid isNotEqualTo "" && {_farUid in (missionNamespace getVariable ["TRIBUNAL_IRON_HITS", []])};
private _farStimulus = (count _far) isEqualTo 1
    && {_farRecord getOrDefault ["local", false]}
    && {(count (_farRecord getOrDefault ["samples", []])) > 20}
    && {_farHit}
    && {damage _target > 0.001};
private _farSeparation = _farLauncher distance2D _target;
["iron.control.outOfRangeImpact", _farStimulus, format ["uid=%1|hit=%2|samples=%3|damage=%4|launcherTargetDistance=%5|radius=%6", _farUid, _farHit, count (_farRecord getOrDefault ["samples", []]), damage _target, _farSeparation, YAS_ironDomeEngagementRadius]] call _assert;
private _eventsAfterFar = count (missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []]);
["iron.control.outOfRangeNoEngagement", _farStimulus && {_eventsAfterFar isEqualTo _eventsBeforeFar}, format ["before=%1|after=%2|stimulus=%3", _eventsBeforeFar, _eventsAfterFar, _farStimulus]] call _assert;

// Adversarial client call: prove receipt at the authority boundary and refusal,
// not merely the absence of an effect.
private _authBox = createVehicle ["YAS_OPHANIM_box", [6550, 6500, 0], [], 0, "NONE"];
_created pushBack _authBox;
uiSleep 0.2;
_authBox setVariable ["YAS_ironDome_enabled", false, true];
missionNamespace setVariable ["TRIBUNAL_IRON_AUTH_BOX", netId _authBox, true];
private _authDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    private _sent = missionNamespace getVariable ["TRIBUNAL_IRON_AUTH_SENT", []];
    ((count _sent) >= 3 && {(_sent # 0) isEqualTo _token}) || {diag_tickTime > _authDeadline}
};
private _receiptDeadline = diag_tickTime + 10;
private _rejections = [];
waitUntil {
    uiSleep 0.05;
    _rejections = (missionNamespace getVariable ["YAS_IRONDOME_AUDIT", []]) select {
        (_x param [1, ""]) isEqualTo "register-box"
            && {(_x param [2, ""]) isEqualTo "token-rejected"}
            && {(_x param [3, 0]) > 2}
    };
    (count _rejections) > 0 || {diag_tickTime > _receiptDeadline}
};
private _authorityRejected = (count _rejections) isEqualTo 1
    && {!(_authBox getVariable ["YAS_ironDome_enabled", false])}
    && {!(_authBox in YAS_IRONDOME_REGISTRY)};
["iron.authority.rejected", _authorityRejected, format ["receipts=%1|enabled=%2|registered=%3|sent=%4", _rejections, _authBox getVariable ["YAS_ironDome_enabled", false], _authBox in YAS_IRONDOME_REGISTRY, missionNamespace getVariable ["TRIBUNAL_IRON_AUTH_SENT", []]]] call _assert;

private _locality = (_success param [8, false])
    && {(_success param [9, false])}
    && {_positiveRecord getOrDefault ["local", false]}
    && {_interceptor getOrDefault ["local", false]}
    && {isServer}
    && {!hasInterface};
["iron.locality", _locality, format ["shell=%1|missile=%2|observerShell=%3|observerMissile=%4|server=%5|interface=%6", _success param [8, false], _success param [9, false], _positiveRecord getOrDefault ["local", false], _interceptor getOrDefault ["local", false], isServer, hasInterface]] call _assert;

[_token] call TRIBUNAL_fnc_artilleryObserverStop;
removeMissionEventHandler ["ArtilleryShellFired", _shellEh];
missionNamespace setVariable ["TRIBUNAL_IRON_OBSERVER_ACTIVE", false];
private _observerDeadline = diag_tickTime + 2;
waitUntil {uiSleep 0.01; scriptDone _interceptorObserver || {diag_tickTime > _observerDeadline}};
YAS_ironDomeEngagementRadius = _radius;
{
    if (!isNull _x) then {deleteVehicle _x};
} forEach _created;
private _cleanupDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.1; (count YAS_IRONDOME_TASKS) isEqualTo 0 || {diag_tickTime > _cleanupDeadline}};
private _cleanup = (count YAS_IRONDOME_TASKS) isEqualTo 0
    && {({!isNull _x && {_x in YAS_IRONDOME_REGISTRY}} count _created) isEqualTo 0}
    && {isNull _target}
    && {isNull _gun};
["iron.cleanup", _cleanup, format ["tasks=%1|registry=%2|targetNull=%3|gunNull=%4", count YAS_IRONDOME_TASKS, count YAS_IRONDOME_REGISTRY, isNull _target, isNull _gun]] call _assert;
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="advsys-iron-dome",
    tier="gameplay",
    server_expected=SERVER_EXPECTED,
    client_expected=CLIENT_EXPECTED,
    client_expected_by_identity={"client-a": CLIENT_EXPECTED},
    client_sqf_by_identity={"client-a": CLIENT_SQF},
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "advanced-systems", "feature": "ophanim-iron-dome"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="An enabled Ophanim automatically launches a physical interceptor against each eligible native artillery shell within range, neutralizes the exact shell before its otherwise-proven impact, handles concurrent threats independently, rejects untrusted mutation, replicates the authoritative result, and leaves disabled/out-of-range stimuli untouched.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Controlled Live A/B proved the physical pipeline and exposed a client-callable authority defect plus non-retiring exhausted tasks; those bounded defects are refined before this causal specification is accepted.",
        dependencies=("Tribunal native-artillery observer", "server-authoritative Iron Dome", "one authenticated client"),
        evidence_types=frozenset({"native-artillery", "trajectory", "impact", "damage", "authoritative-state", "replication", "locality", "adversarial-receipt"}),
        locality_requirements="The native shell, physical interceptor, assignment, terminal decision, and engagement record are server-local/authoritative; client-a observes the exact replicated terminal event and supplies only the rejected authority probe.",
    ),
)
