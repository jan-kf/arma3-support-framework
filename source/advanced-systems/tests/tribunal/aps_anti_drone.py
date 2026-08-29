"""Permanent threat-policy, authority, payload-lifecycle, and compatibility proof for APS anti-drone."""

from tribunal.runner.model import Scenario, ScenarioReview

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "pontifex.advanced-systems.aps-anti-drone",
        "version": 2,
        "feature_family": "pontifex-advanced-systems-aps",
        "name": "APS anti-drone threat transaction",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "source/advanced-systems/tests/tribunal/aps_anti_drone.py",
            "applicability": "Arma 3 dedicated multiplayer with one authenticated client; representative small west/east UAV threats and Pontifex payloads",
            "participants": {
                "server": "threat decision, resource transaction, payload crash disposition and evidence authority",
                "client-a": "owner of both qualifying UAVs and owner-local neutralization effects",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:advanced-systems:aps-anti-drone",
        "label": "APS anti-drone threat transaction",
        "kind": "product_behavior",
        "aliases": ["APS drone defense", "Payload suppression on defensive kill"],
        "biki_context": ["biki-page:12572", "biki-page:1397", "biki-page:15365", "biki-page:8369", "biki-page:1644", "biki-page:1766"],
    },
    "arms": [
        {"key": "motion-controls", "role": "negative_control", "description": "Fast departing, transverse, and slow UAVs remain alive", "assertions": ["apsDrone.motionPolicy", "apsDrone.neutralization"]},
        {"key": "qualifying-threats", "role": "treatment", "description": "West and east client-owned UAVs close above threshold and are neutralized", "assertions": ["apsDrone.fixture", "apsDrone.clientOwnership", "apsDrone.authority", "apsDrone.neutralization"]},
        {"key": "aps-payload-suppression", "role": "treatment", "description": "APS consumes the Pontifex manifest without creating its crash payload effect", "assertions": ["apsDrone.payloadSuppression"]},
        {"key": "ordinary-impact", "role": "positive_control", "description": "Ordinary UAV destruction releases and detonates its installed satchel", "assertions": ["apsDrone.ordinaryCrashPayload"]},
        {"key": "handler-compatibility", "role": "positive_control", "description": "An unrelated Killed handler remains installed and fires on APS neutralization", "assertions": ["apsDrone.handlerCompatibility", "apsDrone.cleanup"]},
    ],
    "causal_relationships": [
        {"key": "motion-discriminates-threat", "relation": "COMPARES_WITH", "source": "qualifying-threats", "target": "motion-controls", "controlled_dimensions": ["UAV family", "range", "APS state", "speed threshold"]},
        {"key": "aps-disposition-differs", "relation": "COMPARES_WITH", "source": "aps-payload-suppression", "target": "ordinary-impact", "controlled_dimensions": ["Payload Manager state", "installed payload ownership", "UAV death"]},
    ],
    "propositions": [{
        "id": "pontifex:advanced-systems:aps-anti-drone-threat-contract",
        "text": "APS neutralizes side-agnostic small UAVs only when they are inside range and meaningfully closing above the configured relative-speed threshold, commits fuel and owner-local destruction together, suppresses only Pontifex-owned defensive-kill payload effects, and does not remove unrelated handlers.",
        "intended_use": "primary_result",
        "assertions": ["apsDrone.fixture", "apsDrone.motionPolicy", "apsDrone.authority", "apsDrone.neutralization", "apsDrone.payloadSuppression", "apsDrone.ordinaryCrashPayload", "apsDrone.handlerCompatibility", "apsDrone.cleanup", "apsDrone.clientOwnership"],
        "rationale": "Matched motion controls, two opposing-side treatments, exact fuel delta, owner IDs, physical death/survival, deployment/audit ledgers, and an independent sentinel handler jointly exclude proximity-only, side-filtered, server-local-only, partial-commit, blanket-handler-removal, and no-stimulus false passes.",
    }],
    "unresolved": ["Client-B/JIP, ownership migration during an active transaction, non-Pontifex payload semantics, and the broader eligible-UAV catalogue remain outside this representative proof."],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="aps-anti-drone",
    tier="gameplay",
    server_expected=frozenset({
        "apsDrone.fixture",
        "apsDrone.motionPolicy",
        "apsDrone.authority",
        "apsDrone.neutralization",
        "apsDrone.payloadSuppression",
        "apsDrone.ordinaryCrashPayload",
        "apsDrone.handlerCompatibility",
        "apsDrone.cleanup",
    }),
    client_expected=frozenset({"apsDrone.clientOwnership"}),
    server_sqf=r'''
private _player = objNull;
private _playerDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _player = allPlayers param [0, objNull];
    !isNull _player || {diag_tickTime > _playerDeadline}
};
private _client = if (isNull _player) then {-1} else {owner _player};
private _origin = if (isNull _player) then {[4700, 2900, 0]} else {(getPosATL _player) vectorAdd [0, 0, 0]};
private _carrier = createVehicle ["B_APC_Tracked_01_AA_F", _origin, [], 0, "CAN_COLLIDE"];
_carrier setPosATL _origin;
_carrier allowDamage false;
_carrier setFuel 0.8;
_carrier setVariable ["YOSHI_APS_Enabled", true, true];
_carrier setVariable ["YOSHI_APS_AntiDrone_Enabled", true, true];
missionNamespace setVariable ["YAS_apsAntiDroneEngagementRadius", 30, true];
missionNamespace setVariable ["YAS_apsAntiDroneMinimumSpeed", 40, true];

private _spawnUav = {
    params ["_class", "_offset", "_velocity", "_owner"];
    private _uav = createVehicle [_class, _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _uav setPosATL (_origin vectorAdd _offset);
    createVehicleCrew _uav;
    _uav allowDamage false;
    _uav enableSimulationGlobal false;
    _uav setVelocity _velocity;
    if (_owner > 2) then {_uav setOwner _owner;};
    _uav
};
private _westInbound = ["B_UAV_01_F", [22, 0, 6], [-18, 0, 0], _client] call _spawnUav;
private _eastInbound = ["O_UAV_01_F", [-22, 0, 6], [18, 0, 0], _client] call _spawnUav;
private _departing = ["O_UAV_01_F", [18, 7, 6], [18, 0, 0], 2] call _spawnUav;
private _transverse = ["O_UAV_01_F", [0, 20, 6], [18, 0, 0], 2] call _spawnUav;
private _slow = ["O_UAV_01_F", [16, -7, 6], [-5, 0, 0], 2] call _spawnUav;
private _ordinaryCrash = ["B_UAV_01_F", [45, 0, 2], [0, 0, 0], 2] call _spawnUav;

private _grenadePayload = [["c5-grenade", "HandGrenade", "M67 fragmentation grenade", 1, "drop", "GrenadeHand"]];
private _satchelPayload = [["c5-satchel", "SatchelCharge_Remote_Mag", "Satchel charge", 8, "satchel", "ModuleExplosive_SatchelCharge_F"]];
_westInbound setVariable ["YFU_PAYLOAD_STATE", [10, _grenadePayload, 0], true];
_ordinaryCrash setVariable ["YFU_PAYLOAD_STATE", [20, _satchelPayload, 0], true];
private _uavs = [_westInbound, _eastInbound, _departing, _transverse, _slow, _ordinaryCrash];
private _ids = _uavs apply {netId _x};
missionNamespace setVariable ["TRIBUNAL_APS_DRONE_FIXTURE", [_token, netId _carrier, _ids, _client], true];
private _fixtureOk = !isNull _player && {_client > 2} && {!isNull _carrier} && {(_ids findIf {_x isEqualTo ""}) < 0};
["apsDrone.fixture", _fixtureOk, format ["client=%1|carrier=%2|uavs=%3|owners=%4", _client, netId _carrier, _ids, _uavs apply {owner _x}]] call _assert;

private _readyDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_APS_DRONE_CLIENT_READY", ""]) isEqualTo _token || {diag_tickTime > _readyDeadline}};
private _motion = [
    [_westInbound, [22, 0, 6], [-18, 0, 0]],
    [_eastInbound, [-22, 0, 6], [18, 0, 0]],
    [_departing, [18, 7, 6], [18, 0, 0]],
    [_transverse, [0, 20, 6], [18, 0, 0]],
    [_slow, [16, -7, 6], [-5, 0, 0]],
    [_ordinaryCrash, [45, 0, 2], [0, 0, 0]]
];
{
    _x params ["_uav", "_offset", "_velocity"];
    _uav setPosATL (_origin vectorAdd _offset);
    _uav enableSimulationGlobal true;
    _uav setVelocity _velocity;
} forEach _motion;
_westInbound allowDamage true;
private _metrics = _uavs apply {[_carrier, _x] call YOSHI_fnc_apsEvaluateDroneThreat};
private _motionOk = !((_metrics # 0) isEqualTo []) && {!((_metrics # 1) isEqualTo [])}
    && {(_metrics # 2) isEqualTo []} && {(_metrics # 3) isEqualTo []} && {(_metrics # 4) isEqualTo []};
["apsDrone.motionPolicy", _motionOk, format ["metrics=%1", _metrics]] call _assert;

private _fuelBefore = fuel _carrier;
[_carrier, -1, 0.05] spawn YOSHI_detectDrones;
_eastInbound enableSimulationGlobal false;
_eastInbound setPosATL (_origin vectorAdd [-22, 0, 6]);
private _firstDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    private _events = missionNamespace getVariable ["YOSHI_APS_DRONE_ENGAGEMENT_EVENTS", []];
    (count _events) >= 1 || {diag_tickTime > _firstDeadline}
};
_eastInbound setPosATL (_origin vectorAdd [-22, 0, 6]);
_eastInbound enableSimulationGlobal true;
_eastInbound setVelocity [18, 0, 0];
_eastInbound allowDamage true;
private _secondDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    private _events = missionNamespace getVariable ["YOSHI_APS_DRONE_ENGAGEMENT_EVENTS", []];
    (count _events) >= 2 || {diag_tickTime > _secondDeadline}
};
_carrier setVariable ["YOSHI_APS_Enabled", false, true];
private _events = missionNamespace getVariable ["YOSHI_APS_DRONE_ENGAGEMENT_EVENTS", []];
private _fuelAfter = fuel _carrier;
private _authorityOk = (count _events) isEqualTo 2
    && {abs ((_fuelBefore - _fuelAfter) - (2 * YOSHI_APS_SOFTKILL_FUEL_COST)) < 0.002}
    && {(_events findIf {(_x # 4) isNotEqualTo 2 || {(_x # 5) isNotEqualTo _client}}) < 0};
["apsDrone.authority", _authorityOk, format ["events=%1|fuel=%2>%3", _events, _fuelBefore, _fuelAfter]] call _assert;
["apsDrone.neutralization", !alive _westInbound && {!alive _eastInbound} && {alive _departing} && {alive _transverse} && {alive _slow}, format ["alive=%1|damage=%2", _uavs apply {alive _x}, _uavs apply {damage _x}]] call _assert;

private _deployBeforeCrash = count (localNamespace getVariable ["YFU_PAYLOAD_DEPLOYMENTS", []]);
_ordinaryCrash allowDamage true;
_ordinaryCrash setDamage 1;
private _crashDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; count (localNamespace getVariable ["YFU_PAYLOAD_DEPLOYMENTS", []]) > _deployBeforeCrash || {diag_tickTime > _crashDeadline}};
private _payloadAudit = localNamespace getVariable ["YFU_PAYLOAD_AUDIT", []];
private _deployments = localNamespace getVariable ["YFU_PAYLOAD_DEPLOYMENTS", []];
private _suppressed = _payloadAudit select {(_x # 1) isEqualTo "crash" && {(_x # 3) isEqualTo "aps-suppressed"}};
private _crashReleases = _deployments select {(_x # 1) isEqualTo "crash-release"};
["apsDrone.payloadSuppression", (count _suppressed) isEqualTo 1 && {([_westInbound] call YFU_fnc_payloadState) # 1 isEqualTo []}, format ["suppressed=%1|state=%2", _suppressed, [_westInbound] call YFU_fnc_payloadState]] call _assert;
["apsDrone.ordinaryCrashPayload", (count _crashReleases) isEqualTo 1 && {(_crashReleases # 0) # 5 isEqualTo "SatchelCharge_Remote_Mag"} && {([_ordinaryCrash] call YFU_fnc_payloadState) # 1 isEqualTo []}, format ["releases=%1|state=%2", _crashReleases, [_ordinaryCrash] call YFU_fnc_payloadState]] call _assert;
["apsDrone.handlerCompatibility", _westInbound getVariable ["TRIBUNAL_APS_DRONE_SENTINEL_FIRED", false], format ["sentinel=%1|suppressionMarker=%2", _westInbound getVariable ["TRIBUNAL_APS_DRONE_SENTINEL_FIRED", false], _westInbound getVariable ["YOSHI_APS_AntiDroneNeutralized", ""]]] call _assert;

private _crew = [];
{_crew append crew _x;} forEach _uavs;
{if (!isNull _x) then {deleteVehicle _x;};} forEach _crew;
{if (!isNull _x) then {deleteVehicle _x;};} forEach _uavs;
deleteVehicle _carrier;
{private _effect = objectFromNetId (_x # 7); if (!isNull _effect) then {deleteVehicle _effect;};} forEach _crashReleases;
missionNamespace setVariable ["TRIBUNAL_APS_DRONE_FIXTURE", nil, true];
["apsDrone.cleanup", true, format ["uavs=%1|effects=%2", _ids, _crashReleases apply {_x # 7}]] call _assert;
''',
    client_sqf=r'''
private _fixture = [];
private _deadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _fixture = missionNamespace getVariable ["TRIBUNAL_APS_DRONE_FIXTURE", []];
    (count _fixture) isEqualTo 4 || {diag_tickTime > _deadline}
};
private _ids = _fixture param [2, []];
private _uavs = _ids apply {objectFromNetId _x};
private _sentinelId = if ((count _uavs) >= 1 && {local (_uavs # 0)}) then {
    (_uavs # 0) addEventHandler ["Killed", {params ["_unit"]; _unit setVariable ["TRIBUNAL_APS_DRONE_SENTINEL_FIRED", true, true];}]
} else {-1};
private _owned = (count _uavs) isEqualTo 6 && {local (_uavs # 0)} && {local (_uavs # 1)} && {!local (_uavs # 5)} && {_sentinelId >= 0};
["apsDrone.clientOwnership", _owned, format ["ids=%1|local=%2|owners=%3|client=%4", _ids, _uavs apply {local _x}, _uavs apply {owner _x}, clientOwner]] call _assert;
missionNamespace setVariable ["TRIBUNAL_APS_DRONE_CLIENT_READY", _token, true];
''',
    metadata={"product": "advanced-systems", "feature": "aps-anti-drone"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="APS engages any small UAV inside the configured envelope only when relative speed and radial closing speed exceed the threshold; it commits fuel and owner-local neutralization atomically, suppresses only Pontifex-owned crash payload effects, and preserves unrelated Killed handlers.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The scenario proves threat semantics, side independence, client ownership, exact resources, causal destruction, ordinary kinetic-impact payload behavior, APS suppression, and handler compatibility without a combinatorial matrix.",
        dependencies=("dedicated server", "one authenticated client", "Payload Manager"),
        evidence_types=frozenset({"trajectory", "authoritative-state", "resource", "locality", "physical-outcome", "negative-control", "composition", "cleanup"}),
        locality_requirements="Detection and transaction authority execute on the server; UAV neutralization executes on each UAV owner; Payload Manager crash disposition executes on the server.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
