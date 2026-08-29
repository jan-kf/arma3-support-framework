"""Permanent selective ACE cargo policy coverage for Pontifex boxes."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_EXPECTED = frozenset({
    "field.aceCargo.fixture",
    "field.aceCargo.selectivePolicy",
    "field.aceCargo.exactLoad",
    "field.aceCargo.cleanup",
})

CLIENT_EXPECTED = frozenset({
    "field.aceCargo.clientPolicy",
    "field.aceCargo.clientLoad",
})

SERVER_SQF = r'''
private _scenarioPlayer = objNull;
private _playerDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _playerDeadline}
};

private _origin = [2300, 5700, 0];
private _spawn = {
    params ["_class", "_offset"];
    private _object = createVehicle [_class, _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setVehiclePosition [_origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setDir 0;
    _object setVelocity [0,0,0];
    _object setAngularVelocity [0,0,0];
    _object allowDamage false;
    _object enableSimulationGlobal false;
    _object
};
private _bridge = ["YFU_Bridge_Box", [0,0,0]] call _spawn;
private _ophanim = ["YAS_OPHANIM_box", [4,0,0]] call _spawn;
private _ordinary = ["B_supplyCrate_F", [8,0,0]] call _spawn;
private _aceCarrier = ["B_Truck_01_transport_F", [0,12,0]] call _spawn;
_aceCarrier lock 0;
private _objects = [_bridge, _ophanim, _ordinary, _aceCarrier];
private _ids = _objects apply {netId _x};

private _policyDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    (_bridge call ace_cargo_fnc_getSizeItem) isEqualTo 2
        && {(_ophanim call ace_cargo_fnc_getSizeItem) isEqualTo 2}
        && {(_ordinary call ace_cargo_fnc_getSizeItem) isEqualTo -1}
        && {[_bridge, _aceCarrier, true] call ace_cargo_fnc_canLoadItemIn}
        && {[_ophanim, _aceCarrier, true] call ace_cargo_fnc_canLoadItemIn}
        || {diag_tickTime > _policyDeadline}
};
private _rows = [_bridge, _ophanim] apply {
    [
        typeOf _x,
        _x isKindOf "ReammoBox_F",
        getNumber (configOf _x >> "YFU_preserveAceCargo"),
        getNumber (configOf _x >> "ace_cargo_size"),
        _x getVariable ["ace_cargo_size", 999],
        _x getVariable ["ace_cargo_canLoad", false],
        _x call ace_cargo_fnc_getSizeItem,
        [_x, _aceCarrier, true] call ace_cargo_fnc_canLoadItemIn,
        alive _x
    ]
};
private _ordinaryRow = [
    getNumber (configOf _ordinary >> "YFU_preserveAceCargo"),
    getNumber (configOf _ordinary >> "ace_cargo_size"),
    _ordinary getVariable ["ace_cargo_size", 999],
    _ordinary getVariable ["ace_cargo_canLoad", true],
    _ordinary call ace_cargo_fnc_getSizeItem,
    [_ordinary, _aceCarrier, true] call ace_cargo_fnc_canLoadItemIn
];
private _fixtureOk = !isNull _scenarioPlayer
    && {(_objects findIf {isNull _x || {!local _x} || {(netId _x) isEqualTo ""}}) < 0}
    && {_bridge isKindOf "ReammoBox_F"} && {_ophanim isKindOf "ReammoBox_F"}
    && {(getNumber (configOf _bridge >> "YFU_preserveAceCargo")) isEqualTo 1}
    && {(getNumber (configOf _ophanim >> "YFU_preserveAceCargo")) isEqualTo 1}
    && {(getNumber (configOf _bridge >> "ace_cargo_size")) isEqualTo 2}
    && {(getNumber (configOf _ophanim >> "ace_cargo_size")) isEqualTo 2};
["field.aceCargo.fixture", _fixtureOk, format ["ids=%1|rows=%2|ordinary=%3|carrier=[%4,%5,%6,%7,%8]", _ids, _rows, _ordinaryRow, getNumber (configOf _aceCarrier >> "ace_cargo_hasCargo"), _aceCarrier call ace_cargo_fnc_getCargoSpaceLeft, alive _aceCarrier, locked _aceCarrier, _aceCarrier getVariable ["ace_cargo_hasCargo", "unset"]]] call _assert;

private _policyOk = (_rows findIf {
    !(_x # 1) || {(_x # 2) isNotEqualTo 1} || {(_x # 3) isNotEqualTo 2}
        || {(_x # 4) isNotEqualTo 2} || {!(_x # 5)}
        || {(_x # 6) isNotEqualTo 2} || {!(_x # 7)}
}) < 0
    && {(_ordinaryRow # 0) isEqualTo 0}
    && {(_ordinaryRow # 2) isEqualTo -1}
    && {!(_ordinaryRow # 3)}
    && {(_ordinaryRow # 4) isEqualTo -1}
    && {!(_ordinaryRow # 5)};
["field.aceCargo.selectivePolicy", _policyOk, format ["rows=%1|ordinary=%2", _rows, _ordinaryRow]] call _assert;

private _ordinaryRejected = !([_ordinary, _aceCarrier, true] call ace_cargo_fnc_loadItem);
private _bridgeLoaded = [_bridge, _aceCarrier, true] call ace_cargo_fnc_loadItem;
private _ophanimLoaded = [_ophanim, _aceCarrier, true] call ace_cargo_fnc_loadItem;
private _loadDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    private _loaded = _aceCarrier getVariable ["ace_cargo_loaded", []];
    _bridge in _loaded && {_ophanim in _loaded}
        && {(attachedTo _bridge) isEqualTo _aceCarrier}
        && {(attachedTo _ophanim) isEqualTo _aceCarrier}
        || {diag_tickTime > _loadDeadline}
};
private _loaded = _aceCarrier getVariable ["ace_cargo_loaded", []];
private _loadOk = _ordinaryRejected && {_bridgeLoaded} && {_ophanimLoaded}
    && {_bridge in _loaded} && {_ophanim in _loaded} && {!(_ordinary in _loaded)}
    && {(attachedTo _bridge) isEqualTo _aceCarrier}
    && {(attachedTo _ophanim) isEqualTo _aceCarrier}
    && {isNull attachedTo _ordinary};
["field.aceCargo.exactLoad", _loadOk, format ["returns=%1|loaded=%2|attached=%3|ordinary=%4", [_ordinaryRejected,_bridgeLoaded,_ophanimLoaded], _loaded apply {if (isNull _x) then {""} else {netId _x}}, [_bridge,_ophanim] apply {netId (attachedTo _x)}, netId (attachedTo _ordinary)]] call _assert;

missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_CARGO_SETUP", [_token, _ids], true];
private _clientDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_FIELD_ACE_CARGO_DONE", ""]) isEqualTo _token
        || {diag_tickTime > _clientDeadline}
};
private _clientDone = (missionNamespace getVariable ["TRIBUNAL_FIELD_ACE_CARGO_DONE", ""]) isEqualTo _token;

{deleteVehicle _x;} forEach _objects;
missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_CARGO_SETUP", nil, true];
missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_CARGO_DONE", nil, true];
private _cleanupDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    (_ids findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupDeadline}
};
private _cleanupOk = _clientDone && {(_ids findIf {!isNull objectFromNetId _x}) < 0};
["field.aceCargo.cleanup", _cleanupOk, format ["clientDone=%1|remaining=%2", _clientDone, _ids select {!isNull objectFromNetId _x}]] call _assert;
'''

CLIENT_SQF = r'''
private _setup = [];
private _setupDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    _setup = missionNamespace getVariable ["TRIBUNAL_FIELD_ACE_CARGO_SETUP", []];
    (count _setup) isEqualTo 2 || {diag_tickTime > _setupDeadline}
};
private _ids = _setup param [1, []];
private _objects = [];
private _objectsDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _objects = _ids apply {objectFromNetId _x};
    (count _objects) isEqualTo 4 && {(_objects findIf {isNull _x}) < 0}
        || {diag_tickTime > _objectsDeadline}
};
private _bridge = _objects param [0, objNull];
private _ophanim = _objects param [1, objNull];
private _ordinary = _objects param [2, objNull];
private _aceCarrier = _objects param [3, objNull];
private _loaded = _aceCarrier getVariable ["ace_cargo_loaded", []];
private _policyOk = (_setup param [0, ""]) isEqualTo _token
    && {(_bridge call ace_cargo_fnc_getSizeItem) isEqualTo 2}
    && {(_ophanim call ace_cargo_fnc_getSizeItem) isEqualTo 2}
    && {(_ordinary call ace_cargo_fnc_getSizeItem) isEqualTo -1}
    && {_bridge getVariable ["ace_cargo_canLoad", false]}
    && {_ophanim getVariable ["ace_cargo_canLoad", false]}
    && {!(_ordinary getVariable ["ace_cargo_canLoad", true])}
    && {(_objects findIf {local _x}) < 0};
["field.aceCargo.clientPolicy", _policyOk, format ["ids=%1|sizes=%2|canLoad=%3|locality=%4", _ids, [_bridge,_ophanim,_ordinary] apply {_x call ace_cargo_fnc_getSizeItem}, [_bridge,_ophanim,_ordinary] apply {_x getVariable ["ace_cargo_canLoad","unset"]}, _objects apply {[local _x,owner _x]}]] call _assert;

private _loadOk = _bridge in _loaded && {_ophanim in _loaded} && {!(_ordinary in _loaded)}
    && {(attachedTo _bridge) isEqualTo _aceCarrier}
    && {(attachedTo _ophanim) isEqualTo _aceCarrier}
    && {isNull attachedTo _ordinary};
["field.aceCargo.clientLoad", _loadOk, format ["loaded=%1|attached=%2|ordinary=%3", _loaded apply {if (isNull _x) then {""} else {netId _x}}, [_bridge,_ophanim] apply {netId (attachedTo _x)}, netId (attachedTo _ordinary)]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_CARGO_DONE", _token, true];
'''

BASELINE = ["field.aceCargo.fixture"]
POLICY = ["field.aceCargo.selectivePolicy", "field.aceCargo.clientPolicy"]
LOAD = ["field.aceCargo.exactLoad", "field.aceCargo.clientLoad"]
CLEANUP = ["field.aceCargo.cleanup"]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "fieldutils-ace-cargo-policy",
        "version": 1,
        "feature_family": "pontifex-field-utilities-ace-cargo-policy",
        "name": "Field Utilities selective ACE cargo policy",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "mods/field-utilities/tests/tribunal/ace_cargo_policy.py",
            "applicability": "ACE 3.21.0 on Arma 3 dedicated multiplayer with one authenticated client and server-owned YFU_Bridge_Box, YAS_OPHANIM_box, B_supplyCrate_F and unlocked B_Truck_01_transport_F fixtures",
            "participants": {
                "server": "class/runtime policy, ACE load result, exact membership and cleanup",
                "client-a": "runtime-policy and exact replicated ACE membership observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:ace-cargo-policy",
        "label": "Field Utilities selective ACE cargo policy",
        "kind": "product_behavior",
        "aliases": ["Pontifex ACE cargo opt-in"],
        "biki_context": [],
    },
    "arms": [
        {"key": "fixture", "role": "baseline", "description": "The exact Pontifex boxes, ordinary ammo box and unlocked ACE carrier exist server-local with independent class/config identities", "assertions": BASELINE},
        {"key": "selective-policy", "role": "treatment", "description": "Opted-in Pontifex boxes expose size 2 and ACE eligibility on both peers while ordinary ammo cargo remains ACE-disabled", "assertions": POLICY},
        {"key": "exact-load", "role": "treatment", "description": "Authentic ACE loading accepts both exact opted-in boxes, rejects the ordinary control, and replicates exact membership and attachment", "assertions": LOAD},
        {"key": "cleanup", "role": "treatment", "description": "Every exact fixture identity is deleted after both peers finish observation", "assertions": CLEANUP},
    ],
    "causal_relationships": [],
    "propositions": [
        {
            "id": "pontifex:field-utilities:selective-ace-cargo",
            "text": "Field Utilities preserves the explicit ACE cargo contract for the exact Bridge and OPHANIM boxes while ordinary ammo boxes retain the existing ACE-disabled policy.",
            "intended_use": "primary_result",
            "assertions": BASELINE + POLICY + LOAD + CLEANUP,
            "rationale": "Exact config and runtime values, framework eligibility, literal load returns, membership, attachment, remote replication, an ordinary-box control and cleanup exclude config-only and self-observed false passes.",
        }
    ],
    "unresolved": [
        "Other opted-in classes, ACE versions, carriers, client-owned objects, ownership migration, client-B/JIP, user-driven menus, unload placement, and concurrent ACE/native requests remain outside this proof."
    ],
}

TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-ace-cargo-policy",
    tier="gameplay",
    server_expected=SERVER_EXPECTED,
    client_expected=CLIENT_EXPECTED,
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "field-utilities", "feature": "selective-ace-cargo-policy"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Field Utilities preserves configured ACE cargo for its exact Bridge box and Advanced Systems' exact OPHANIM box; ordinary ammo boxes retain the existing ACE-disabled policy. Authentic ACE loading must accept and replicate both exact opted-in boxes while rejecting the ordinary control, and every fixture is removed after observation.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="The blanket runtime size -1 contradicted both shipped size-2 configs. A per-class opt-in now initializes the declared size through ACE's public API while retaining the existing replacement policy for ordinary ammo boxes; exact server/client runtime state and authentic load results prove behavior rather than config text.",
        dependencies=("ACE 3.21 cargo API", "Field Utilities object-created policy", "Advanced Systems OPHANIM config", "one authenticated client"),
        evidence_types=frozenset({"config-runtime-parity", "ace-cargo-eligibility", "ace-cargo-membership", "exact-identity", "replication", "negative-control", "cleanup"}),
        locality_requirements="The dedicated server creates and owns every fixture and invokes ACE loading; client-a independently observes globally replicated size/can-load state, exact loaded membership and attachments. Other ownership and multi-client domains are unclaimed.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
