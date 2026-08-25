"""Permanent coverage for Vigil's server-owned governor terminal lifecycle."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_ASSERTIONS = [
    "vigil.governor.fixture",
    "vigil.governor.normal",
    "vigil.governor.earlyComplete",
    "vigil.governor.failure",
    "vigil.governor.cancellation",
    "vigil.governor.vehicleLoss",
    "vigil.governor.duplicate",
    "vigil.governor.successor",
    "vigil.governor.cleanup",
]

CLIENT_ASSERTIONS = ["vigil.governor.clientReceipt"]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-governor-lifecycle",
        "version": 1,
        "feature_family": "pontifex-vigil-task-governor-lifecycle",
        "name": "Vigil task-governor terminal lifecycle",
        "definition": {
            "kind": "controlled dedicated-server lifecycle specification",
            "reference": "source/visual-support-tablet/tests/tribunal/vigil_governor_lifecycle.py",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA and Vigil; harmless scenario-owned server tasks and server-local vehicles",
            "participants": {
                "server": "constructs harmless task handlers locally, drives exact governor ticks, records ordered callbacks, terminal causes, finalizer counts, generation identity, manager disposition, and cleanup",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:task-governor-lifecycle",
        "label": "Vigil task governor lifecycle",
        "kind": "product_behavior",
        "aliases": ["Vigil governor terminal policy"],
        "biki_context": [],
    },
    "arms": [
        {"key": "fixture", "role": "baseline", "description": "The server owns the isolated manager and exact governor functions", "assertions": [SERVER_ASSERTIONS[0]]},
        {"key": "normal", "role": "positive_control", "description": "Ordered stages include a repeated wait and exact-once finalization before disablement", "assertions": [SERVER_ASSERTIONS[1]]},
        {"key": "early-complete", "role": "treatment", "description": "An early complete return still enters exact-once finalization", "assertions": [SERVER_ASSERTIONS[2]]},
        {"key": "failure", "role": "treatment", "description": "A handler failure retains its cause, finalizes once, and disables the exact generation", "assertions": [SERVER_ASSERTIONS[3]]},
        {"key": "cancellation", "role": "treatment", "description": "Accepted server cancellation enters the same exact-once terminal path", "assertions": [SERVER_ASSERTIONS[4]]},
        {"key": "vehicle-loss", "role": "treatment", "description": "Vehicle death is processed through failure finalization rather than pre-disabled", "assertions": [SERVER_ASSERTIONS[5]]},
        {"key": "duplicate", "role": "negative_control", "description": "A second active generation is rejected and its sentinel handler never runs", "assertions": [SERVER_ASSERTIONS[6]]},
        {"key": "successor", "role": "treatment", "description": "A finalizer-installed successor survives retirement of the exact finishing generation and then finalizes independently", "assertions": [SERVER_ASSERTIONS[7]]},
        {"key": "cleanup", "role": "treatment", "description": "Client-a acknowledges the completed server matrix; scenario objects, manager state, helper symbols, and governor running state are restored", "assertions": [SERVER_ASSERTIONS[8], CLIENT_ASSERTIONS[0]]},
    ],
    "causal_relationships": [
        {
            "key": "terminal-causes-v-normal",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "early-complete",
            "target": "normal",
            "controlled_dimensions": ["same server constructor", "same handler map", "same manual tick driver", "same resource/finalizer observer"],
        },
        {
            "key": "duplicate-v-successor",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "successor",
            "target": "duplicate",
            "controlled_dimensions": ["same vehicle-keyed manager", "same generation identity", "same assignment function", "only finishing-generation state differs"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:governor-terminal-finalization",
            "text": "For server-owned Vigil tasks, normal completion, early completion, failure, accepted cancellation, and vehicle loss converge on exact-once finalization and disable the exact terminal generation without later callbacks.",
            "intended_use": "primary_result",
            "assertions": SERVER_ASSERTIONS + CLIENT_ASSERTIONS,
            "rationale": "Matched harmless handlers record exact ordered callbacks and owned-resource cleanup for every terminal cause; manager generation and enabled state are inspected after bounded manual ticks.",
        },
        {
            "id": "pontifex:vigil:governor-generation-preservation",
            "text": "Vigil rejects replacement of an active task generation while allowing a finishing generation's finalizer to install a successor that is not disabled by retirement of its predecessor.",
            "intended_use": "primary_result",
            "assertions": [SERVER_ASSERTIONS[6], SERVER_ASSERTIONS[7], SERVER_ASSERTIONS[8]],
            "rationale": "The rejected generation carries an executable sentinel that remains absent, while the permitted successor is compared by id and generation before and after predecessor finalization.",
        },
    ],
    "unresolved": [
        "Client request authentication, declarative schemas, forged code-bearing payloads, cancellation eligibility, retry/invalid-return policy, durable terminal history, headless/client-owned vehicles, client-N, and JIP remain outside this server-owned lifecycle proof."
    ],
}


SERVER_SQF = r'''
private _initialManagers = missionNamespace getVariable ["YSF_task_managers", createHashMap];
private _initialPFH = missionNamespace getVariable ["YSF_governorPFH", -1];
if (_initialPFH >= 0) then {call YSF_governorStop;};
missionNamespace setVariable ["YSF_task_managers", createHashMap];
missionNamespace setVariable ["TRIBUNAL_GOV_SENTINEL", false];
missionNamespace setVariable ["TRIBUNAL_GOV_OBJECTS", []];

TRIBUNAL_GOV_record = {
    params ["_task", "_label"];
    private _rows = _task getOrDefault ["tribunalRows", []];
    _rows pushBack _label;
    _task set ["tribunalRows", _rows];
};

TRIBUNAL_GOV_handlers = {
    createHashMapFromArray [
        ["init", {
            params ["_veh", "_task", "_data"];
            _data params ["_arm", "_mode"];
            [_task, "init"] call TRIBUNAL_GOV_record;
            if (_mode isEqualTo "sentinel") then {missionNamespace setVariable ["TRIBUNAL_GOV_SENTINEL", true];};
            private _resource = "Land_HelipadEmpty_F" createVehicle [0, 0, 0];
            _resource setPosATL ((getPosATL _veh) vectorAdd [0, 3, 0]);
            _task set ["tribunalResource", _resource];
            private _objects = missionNamespace getVariable ["TRIBUNAL_GOV_OBJECTS", []];
            _objects pushBack _resource;
            missionNamespace setVariable ["TRIBUNAL_GOV_OBJECTS", _objects];
            if (_mode isEqualTo "early" || {_mode isEqualTo "successor-parent"}) exitWith {"complete"};
            "advance"
        }],
        ["start", {
            params ["_veh", "_task", "_data"];
            _data params ["_arm", "_mode"];
            [_task, "start"] call TRIBUNAL_GOV_record;
            if (_mode isEqualTo "normal" && {(_task getOrDefault ["tribunalStartCount", 0]) isEqualTo 0}) exitWith {
                _task set ["tribunalStartCount", 1];
                "wait"
            };
            if (_mode isEqualTo "failure") exitWith {"fail"};
            "advance"
        }],
        ["mission", {
            params ["_veh", "_task", "_data"];
            _data params ["_arm", "_mode"];
            [_task, "mission"] call TRIBUNAL_GOV_record;
            if (_mode in ["cancellation", "vehicle-loss", "duplicate"]) exitWith {"wait"};
            "advance"
        }],
        ["end", {
            params ["_veh", "_task", "_data"];
            [_task, "end"] call TRIBUNAL_GOV_record;
            "advance"
        }],
        ["finally", {
            params ["_veh", "_task", "_data"];
            _data params ["_arm", "_mode"];
            [_task, "finally"] call TRIBUNAL_GOV_record;
            _task set ["tribunalFinalizers", (_task getOrDefault ["tribunalFinalizers", 0]) + 1];
            private _resource = _task getOrDefault ["tribunalResource", objNull];
            if (!isNull _resource) then {deleteVehicle _resource;};
            _task set ["tribunalResource", objNull];
            if (_mode isEqualTo "successor-parent") then {
                private _child = ["tribunal-successor", _veh, call TRIBUNAL_GOV_handlers, [_arm, "early"], 10, 3] call YSF_taskNew;
                _task set ["tribunalSuccessor", _child];
                [_veh, _child] call YSF_taskAssign;
            };
            "complete"
        }]
    ]
};

TRIBUNAL_GOV_tick = {
    params ["_veh", "_task", ["_limit", 16]];
    for "_i" from 1 to _limit do {
        [_veh] call YSF_taskTick;
        if ((_task getOrDefault ["stage", -1]) >= 5) exitWith {};
        uiSleep 0.02;
    };
};

TRIBUNAL_GOV_vehicle = {
    params ["_offset"];
    private _veh = "C_Offroad_01_F" createVehicle [0, 0, 0];
    _veh setPosATL ([1000 + _offset, 1000, 0]);
    private _objects = missionNamespace getVariable ["TRIBUNAL_GOV_OBJECTS", []];
    _objects pushBack _veh;
    missionNamespace setVariable ["TRIBUNAL_GOV_OBJECTS", _objects];
    _veh
};

private _fixtureOk = isServer
    && {!isNil "YSF_taskNew"}
    && {!isNil "YSF_taskAssign"}
    && {!isNil "YSF_taskTick"}
    && {!isNil "YSF_taskCancel"}
    && {!isNil "YSF_governorHandle"}
    && {(count (call YSF__mgr)) isEqualTo 0};
["vigil.governor.fixture", _fixtureOk, format ["server=%1|pfh=%2|managerCount=%3", isServer, _initialPFH, count (call YSF__mgr)]] call _assert;

private _normalVeh = [0] call TRIBUNAL_GOV_vehicle;
private _normal = ["tribunal-normal", _normalVeh, call TRIBUNAL_GOV_handlers, ["normal", "normal"], 10, 3] call YSF_taskNew;
[_normalVeh, _normal] call YSF_taskAssign;
[_normalVeh, _normal] call TRIBUNAL_GOV_tick;
private _normalRec = (call YSF__mgr) getOrDefault [str _normalVeh, objNull];
private _normalOk = (_normal getOrDefault ["tribunalRows", []]) isEqualTo ["init", "start", "start", "mission", "end", "finally"]
    && {(_normal getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {isNull (_normal getOrDefault ["tribunalResource", objNull])}
    && {(_normal getOrDefault ["state", ""]) isEqualTo "complete"}
    && {typeName _normalRec isEqualTo "HASHMAP"}
    && {!(_normalRec getOrDefault ["enabled", true])};
["vigil.governor.normal", _normalOk, format ["rows=%1|finalizers=%2|state=%3|enabled=%4", _normal getOrDefault ["tribunalRows", []], _normal getOrDefault ["tribunalFinalizers", 0], _normal getOrDefault ["state", ""], if (typeName _normalRec isEqualTo "HASHMAP") then {_normalRec getOrDefault ["enabled", "missing"]} else {"missing"}]] call _assert;

private _earlyVeh = [20] call TRIBUNAL_GOV_vehicle;
private _early = ["tribunal-early", _earlyVeh, call TRIBUNAL_GOV_handlers, ["early", "early"], 10, 3] call YSF_taskNew;
[_earlyVeh, _early] call YSF_taskAssign;
[_earlyVeh, _early] call TRIBUNAL_GOV_tick;
private _earlyRec = (call YSF__mgr) getOrDefault [str _earlyVeh, objNull];
private _earlyOk = (_early getOrDefault ["tribunalRows", []]) isEqualTo ["init", "finally"]
    && {(_early getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {isNull (_early getOrDefault ["tribunalResource", objNull])}
    && {typeName _earlyRec isEqualTo "HASHMAP" && {!(_earlyRec getOrDefault ["enabled", true])}};
["vigil.governor.earlyComplete", _earlyOk, format ["rows=%1|finalizers=%2|enabled=%3", _early getOrDefault ["tribunalRows", []], _early getOrDefault ["tribunalFinalizers", 0], if (typeName _earlyRec isEqualTo "HASHMAP") then {_earlyRec getOrDefault ["enabled", "missing"]} else {"missing"}]] call _assert;

private _failVeh = [40] call TRIBUNAL_GOV_vehicle;
private _failed = ["tribunal-failure", _failVeh, call TRIBUNAL_GOV_handlers, ["failure", "failure"], 10, 3] call YSF_taskNew;
[_failVeh, _failed] call YSF_taskAssign;
[_failVeh, _failed] call TRIBUNAL_GOV_tick;
private _failRec = (call YSF__mgr) getOrDefault [str _failVeh, objNull];
private _failOk = (_failed getOrDefault ["tribunalRows", []]) isEqualTo ["init", "start", "finally"]
    && {(_failed getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {(_failed getOrDefault ["state", ""]) isEqualTo "failed"}
    && {typeName _failRec isEqualTo "HASHMAP" && {!(_failRec getOrDefault ["enabled", true])}};
["vigil.governor.failure", _failOk, format ["rows=%1|finalizers=%2|state=%3|enabled=%4", _failed getOrDefault ["tribunalRows", []], _failed getOrDefault ["tribunalFinalizers", 0], _failed getOrDefault ["state", ""], if (typeName _failRec isEqualTo "HASHMAP") then {_failRec getOrDefault ["enabled", "missing"]} else {"missing"}]] call _assert;

private _cancelVeh = [60] call TRIBUNAL_GOV_vehicle;
private _cancelled = ["tribunal-cancel", _cancelVeh, call TRIBUNAL_GOV_handlers, ["cancellation", "cancellation"], 10, 3] call YSF_taskNew;
[_cancelVeh, _cancelled] call YSF_taskAssign;
for "_i" from 1 to 3 do {[_cancelVeh] call YSF_taskTick;};
private _cancelAccepted = ([_cancelVeh] call YSF_taskCancel) isEqualTo true;
[_cancelVeh, _cancelled] call TRIBUNAL_GOV_tick;
private _cancelRec = (call YSF__mgr) getOrDefault [str _cancelVeh, objNull];
private _cancelOk = _cancelAccepted
    && {(_cancelled getOrDefault ["tribunalRows", []]) isEqualTo ["init", "start", "mission", "finally"]}
    && {(_cancelled getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {(_cancelled getOrDefault ["state", ""]) isEqualTo "cancelled"}
    && {typeName _cancelRec isEqualTo "HASHMAP" && {!(_cancelRec getOrDefault ["enabled", true])}};
["vigil.governor.cancellation", _cancelOk, format ["accepted=%1|rows=%2|finalizers=%3|state=%4", _cancelAccepted, _cancelled getOrDefault ["tribunalRows", []], _cancelled getOrDefault ["tribunalFinalizers", 0], _cancelled getOrDefault ["state", ""]]] call _assert;

private _lostVeh = [80] call TRIBUNAL_GOV_vehicle;
private _lost = ["tribunal-lost", _lostVeh, call TRIBUNAL_GOV_handlers, ["vehicle-loss", "vehicle-loss"], 10, 3] call YSF_taskNew;
[_lostVeh, _lost] call YSF_taskAssign;
for "_i" from 1 to 3 do {[_lostVeh] call YSF_taskTick;};
_lostVeh setDamage 1;
call YSF_governorHandle;
[_lostVeh, _lost] call TRIBUNAL_GOV_tick;
private _lostRec = (call YSF__mgr) getOrDefault [str _lostVeh, objNull];
private _lostOk = (_lost getOrDefault ["tribunalRows", []]) isEqualTo ["init", "start", "mission", "finally"]
    && {(_lost getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {(_lost getOrDefault ["state", ""]) isEqualTo "failed"}
    && {typeName _lostRec isEqualTo "HASHMAP" && {!(_lostRec getOrDefault ["enabled", true])}};
["vigil.governor.vehicleLoss", _lostOk, format ["alive=%1|rows=%2|finalizers=%3|state=%4", alive _lostVeh, _lost getOrDefault ["tribunalRows", []], _lost getOrDefault ["tribunalFinalizers", 0], _lost getOrDefault ["state", ""]]] call _assert;

private _dupVeh = [100] call TRIBUNAL_GOV_vehicle;
private _original = ["tribunal-original", _dupVeh, call TRIBUNAL_GOV_handlers, ["duplicate", "duplicate"], 10, 3] call YSF_taskNew;
[_dupVeh, _original] call YSF_taskAssign;
for "_i" from 1 to 3 do {[_dupVeh] call YSF_taskTick;};
private _duplicate = ["tribunal-sentinel", _dupVeh, call TRIBUNAL_GOV_handlers, ["duplicate", "sentinel"], 10, 3] call YSF_taskNew;
private _duplicateResult = [_dupVeh, _duplicate] call YSF_taskAssign;
private _dupRec = (call YSF__mgr) getOrDefault [str _dupVeh, objNull];
private _preserved = typeName _dupRec isEqualTo "HASHMAP" && {((_dupRec get "task") get "id") isEqualTo (_original get "id")} && {((_dupRec get "task") get "gen") isEqualTo (_original get "gen")};
private _cancelOriginal = ([_dupVeh] call YSF_taskCancel) isEqualTo true;
[_dupVeh, _original] call TRIBUNAL_GOV_tick;
private _duplicateOk = (_duplicateResult isEqualTo false) && {_preserved} && {!(missionNamespace getVariable ["TRIBUNAL_GOV_SENTINEL", false])} && {_cancelOriginal};
["vigil.governor.duplicate", _duplicateOk, format ["result=%1|preserved=%2|sentinel=%3|cancel=%4", _duplicateResult, _preserved, missionNamespace getVariable ["TRIBUNAL_GOV_SENTINEL", false], _cancelOriginal]] call _assert;

private _successorVeh = [120] call TRIBUNAL_GOV_vehicle;
private _parent = ["tribunal-parent", _successorVeh, call TRIBUNAL_GOV_handlers, ["successor", "successor-parent"], 10, 3] call YSF_taskNew;
[_successorVeh, _parent] call YSF_taskAssign;
[_successorVeh, _parent] call TRIBUNAL_GOV_tick;
private _child = _parent getOrDefault ["tribunalSuccessor", objNull];
private _successorRec = (call YSF__mgr) getOrDefault [str _successorVeh, objNull];
private _childInstalled = typeName _child isEqualTo "HASHMAP"
    && {typeName _successorRec isEqualTo "HASHMAP"}
    && {_successorRec getOrDefault ["enabled", false]}
    && {((_successorRec get "task") get "id") isEqualTo (_child get "id")}
    && {((_successorRec get "task") get "gen") isEqualTo (_child get "gen")};
if (typeName _child isEqualTo "HASHMAP") then {[_successorVeh, _child] call TRIBUNAL_GOV_tick;};
private _childRec = (call YSF__mgr) getOrDefault [str _successorVeh, objNull];
private _successorOk = (_parent getOrDefault ["tribunalRows", []]) isEqualTo ["init", "finally"]
    && {(_parent getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {_childInstalled}
    && {(_child getOrDefault ["tribunalRows", []]) isEqualTo ["init", "finally"]}
    && {(_child getOrDefault ["tribunalFinalizers", 0]) isEqualTo 1}
    && {typeName _childRec isEqualTo "HASHMAP" && {!(_childRec getOrDefault ["enabled", true])}};
["vigil.governor.successor", _successorOk, format ["parentRows=%1|parentFinalizers=%2|installed=%3|childRows=%4|childFinalizers=%5|childEnabled=%6", _parent getOrDefault ["tribunalRows", []], _parent getOrDefault ["tribunalFinalizers", 0], _childInstalled, if (typeName _child isEqualTo "HASHMAP") then {_child getOrDefault ["tribunalRows", []]} else {[]}, if (typeName _child isEqualTo "HASHMAP") then {_child getOrDefault ["tribunalFinalizers", 0]} else {-1}, if (typeName _childRec isEqualTo "HASHMAP") then {_childRec getOrDefault ["enabled", "missing"]} else {"missing"}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_GOVERNOR_READY", _token, true];
private _clientDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_GOVERNOR_ACK", ""]) isEqualTo _token
        || {diag_tickTime > _clientDeadline}
};
private _clientAck = (missionNamespace getVariable ["TRIBUNAL_VIGIL_GOVERNOR_ACK", ""]) isEqualTo _token;

{
    if (!isNull _x) then {deleteVehicle _x;};
} forEach (missionNamespace getVariable ["TRIBUNAL_GOV_OBJECTS", []]);
missionNamespace setVariable ["YSF_task_managers", _initialManagers];
missionNamespace setVariable ["TRIBUNAL_GOV_SENTINEL", nil];
missionNamespace setVariable ["TRIBUNAL_GOV_OBJECTS", nil];
TRIBUNAL_GOV_record = nil;
TRIBUNAL_GOV_handlers = nil;
TRIBUNAL_GOV_tick = nil;
TRIBUNAL_GOV_vehicle = nil;
if (_initialPFH >= 0) then {[1] call YSF_governorStart;};
private _cleanupOk = (missionNamespace getVariable ["YSF_task_managers", createHashMap]) isEqualTo _initialManagers
    && {isNil "TRIBUNAL_GOV_record"}
    && {isNil "TRIBUNAL_GOV_handlers"}
    && {isNil "TRIBUNAL_GOV_tick"}
    && {isNil "TRIBUNAL_GOV_vehicle"}
    && {isNil {missionNamespace getVariable "TRIBUNAL_GOV_OBJECTS"}}
    && {_clientAck}
    && {(_initialPFH < 0) || {(missionNamespace getVariable ["YSF_governorPFH", -1]) >= 0}};
["vigil.governor.cleanup", _cleanupOk, format ["managerRestored=%1|clientAck=%2|pfh=%3", (missionNamespace getVariable ["YSF_task_managers", createHashMap]) isEqualTo _initialManagers, _clientAck, missionNamespace getVariable ["YSF_governorPFH", -1]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_GOVERNOR_READY", nil, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_GOVERNOR_ACK", nil, true];
'''


CLIENT_SQF = r'''
private _deadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_GOVERNOR_READY", ""]) isEqualTo _token
        || {diag_tickTime > _deadline}
};
private _received = (missionNamespace getVariable ["TRIBUNAL_VIGIL_GOVERNOR_READY", ""]) isEqualTo _token;
["vigil.governor.clientReceipt", _received, format ["received=%1|token=%2", _received, _token]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_GOVERNOR_ACK", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-governor-lifecycle",
    tier="gameplay",
    server_expected=frozenset(SERVER_ASSERTIONS),
    client_expected=frozenset(CLIENT_ASSERTIONS),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "visual-support-tablet", "feature": "task-governor-lifecycle"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Server-owned Vigil tasks converge on exact-once terminal finalization, reject active replacement, and preserve a finalizer-installed successor generation.",
        outcome="REWRITE BEFORE PERMANENT COVERAGE",
        rationale="Canonical review found divergent terminal paths that skipped finalizers or disabled the wrong generation. Harmless matched tasks now make callback order, terminal cause, resource cleanup, duplicate rejection, and successor identity direct oracles.",
        dependencies=("Vigil server governor", "CBA scheduler", "server-local harmless vehicles"),
        evidence_types=frozenset({"callback-order", "terminal-cause", "generation-identity", "negative-control", "cleanup", "replication"}),
        locality_requirements="All executable handlers are constructed and invoked on the dedicated server. No client-authored code or request-authority claim is admitted; client-N and ownership migration are excluded.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
