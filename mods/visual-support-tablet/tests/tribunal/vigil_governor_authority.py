"""Permanent coverage for Vigil's declarative task-request authority boundary."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_ASSERTIONS = [
    "vigil.governorAuthority.fixture",
    "vigil.governorAuthority.validSchemas",
    "vigil.governorAuthority.serverBuilt",
    "vigil.governorAuthority.requesterAndAsset",
    "vigil.governorAuthority.malformedAndUnsupported",
    "vigil.governorAuthority.duplicateAndBusy",
    "vigil.governorAuthority.legacyCodeRejected",
    "vigil.governorAuthority.terminalResults",
    "vigil.governorAuthority.cleanup",
]

CLIENT_ASSERTIONS = [
    "vigil.governorAuthority.clientReceipts",
    "vigil.governorAuthority.clientAudience",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-governor-authority",
        "version": 2,
        "feature_family": "pontifex-vigil-task-governor-authority",
        "name": "Vigil declarative task-request authority",
        "definition": {
            "kind": "controlled dedicated-server authority specification",
            "reference": "mods/visual-support-tablet/tests/tribunal/vigil_governor_authority.py",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA and Vigil; one independently authenticated WEST client and server-local WEST/EAST assets",
            "participants": {
                "server": "validates identity, request schema, asset eligibility, replay and active-task state; constructs registered handlers and records terminal results",
                "client-a": "submits declarative positive and negative requests and observes requester-scoped correlated receipts",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:task-governor-authority",
        "label": "Vigil task governor request authority",
        "kind": "product_behavior",
        "aliases": ["Vigil declarative task requests"],
        "biki_context": ["biki-page:17234", "arma:arma-3-cfgremoteexec"],
    },
    "arms": [
        {"key": "fixture", "role": "baseline", "description": "A real client and exact server-local task assets establish identity, side, locality, and registered task factories", "assertions": [SERVER_ASSERTIONS[0]]},
        {"key": "valid", "role": "positive_control", "description": "Declarative artillery, transport, and CAS schemas create server-built task generations", "assertions": SERVER_ASSERTIONS[1:3]},
        {"key": "authority-negatives", "role": "negative_control", "description": "Forged requester and wrong-side asset requests reach exact rejection receipts", "assertions": [SERVER_ASSERTIONS[3]]},
        {"key": "schema-negatives", "role": "negative_control", "description": "Code-bearing malformed and unsupported-type requests reach exact rejection receipts without executing caller code", "assertions": [SERVER_ASSERTIONS[4], SERVER_ASSERTIONS[6]]},
        {"key": "concurrency", "role": "negative_control", "description": "Replay and task-equivalent active requests are rejected without replacing the accepted generation", "assertions": [SERVER_ASSERTIONS[5]]},
        {"key": "results", "role": "treatment", "description": "Requester-only correlated acceptance/rejection and terminal results are observed before complete cleanup", "assertions": [SERVER_ASSERTIONS[7], SERVER_ASSERTIONS[8]] + CLIENT_ASSERTIONS},
    ],
    "causal_relationships": [
        {
            "key": "valid-v-code-bearing",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "schema-negatives",
            "target": "valid",
            "controlled_dimensions": ["same real requester", "same server endpoint", "same WEST asset family", "only declarative schema versus code-bearing payload differs"],
        },
        {
            "key": "same-side-v-wrong-side",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "authority-negatives",
            "target": "valid",
            "controlled_dimensions": ["same requester owner", "same artillery schema", "same vehicle class", "only authoritative asset side differs"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:governor-declarative-authority",
            "text": "Vigil accepts bounded declarative artillery, transport, and CAS requests only from the authenticated owning player for an eligible same-side asset, builds registered handlers on the server, and rejects malformed, code-bearing, unsupported, forged-requester, and wrong-side requests without executing caller code.",
            "intended_use": "primary_result",
            "assertions": SERVER_ASSERTIONS[:5] + [SERVER_ASSERTIONS[6]] + CLIENT_ASSERTIONS,
            "rationale": "A real client submits matched positive and negative requests. Server audit rows, task provenance, exact rejection reasons, and an executable legacy sentinel distinguish boundary arrival from silent absence.",
        },
        {
            "id": "pontifex:vigil:governor-request-correlation",
            "text": "Vigil correlates requester-scoped acceptance, rejection, and terminal results by request ID while rejecting replay and task-equivalent active requests without changing the accepted generation.",
            "intended_use": "primary_result",
            "assertions": [SERVER_ASSERTIONS[5], SERVER_ASSERTIONS[7], SERVER_ASSERTIONS[8]] + CLIENT_ASSERTIONS,
            "rationale": "The accepted generation identity is compared before and after replay/busy stimuli, then all accepted tasks are terminated through the shared finalizer and matched to client receipts.",
        },
    ],
    "unresolved": [
        "Queue ordering, confirmed replacement, bounded terminal history, operational map presentation, remote cancellation eligibility, retry/invalid-return policy, headless/client-owned vehicles, client-N, JIP, and network interruption remain outside this request-authority proof."
    ],
}


SERVER_SQF = r'''
private _initialManagers = missionNamespace getVariable ["YSF_task_managers", createHashMap];
private _initialPFH = missionNamespace getVariable ["YSF_governorPFH", -1];
private _initialAudit = missionNamespace getVariable ["YSF_task_request_audit", []];
private _initialCache = missionNamespace getVariable ["YSF_task_request_cache", createHashMap];
if (_initialPFH >= 0) then {call YSF_governorStop;};
missionNamespace setVariable ["YSF_task_managers", createHashMap];
missionNamespace setVariable ["YSF_task_request_audit", []];
missionNamespace setVariable ["YSF_task_request_cache", createHashMap];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", false];

private _objects = [];
private _groups = [];
private _makeCrewed = {
    params ["_class", "_side", "_pos"];
    private _veh = createVehicle [_class, _pos, [], 0, "NONE"];
    private _group = createGroup [_side, true];
    private _crewClass = ["O_crew_F", "B_crew_F"] select (_side isEqualTo west);
    private _driver = _group createUnit [_crewClass, _pos, [], 0, "NONE"];
    _driver moveInDriver _veh;
    _objects pushBack _driver;
    _objects pushBack _veh;
    _groups pushBack _group;
    _veh
};

private _arty = ["B_MBT_01_arty_F", west, [1600, 1600, 0]] call _makeCrewed;
private _transport = ["B_Heli_Transport_01_F", west, [1640, 1600, 0]] call _makeCrewed;
private _cas = ["B_Heli_Attack_01_dynamicLoadout_F", west, [1680, 1600, 0]] call _makeCrewed;
private _wrongSide = ["O_MBT_02_arty_F", east, [1720, 1600, 0]] call _makeCrewed;
private _legacy = ["C_Offroad_01_F", civilian, [1760, 1600, 0]] call _makeCrewed;
private _ordnance = (getArtilleryAmmo [_arty]) param [0, ""];

private _playerDeadline = diag_tickTime + 45;
private _authorityPlayers = [];
waitUntil {
    uiSleep 0.05;
    _authorityPlayers = allPlayers select {isPlayer _x && {owner _x > 2}};
    (count _authorityPlayers) isEqualTo 1 || {diag_tickTime > _playerDeadline}
};

private _fixtureOk = isServer
    && {!isNil "YSF_taskNew"}
    && {!isNil "YSF_handlers_artillery"}
    && {!isNil "YSF_handlers_transport"}
    && {!isNil "YSF_handlers_cas"}
    && {!isNull driver _arty}
    && {!isNull driver _transport}
    && {!isNull driver _cas}
    && {(count _authorityPlayers) isEqualTo 1}
    && {_ordnance isNotEqualTo ""};
["vigil.governorAuthority.fixture", _fixtureOk, format ["server=%1|players=%2|owners=%3|ordnance=%4|sides=%5", isServer, _authorityPlayers apply {[netId _x, owner _x]}, [_arty, _transport, _cas, _wrongSide] apply {owner _x}, _ordnance, [_arty, _transport, _cas, _wrongSide] apply {side group effectiveCommander _x}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_FIXTURE", [_token, _arty, _transport, _cas, _wrongSide, _legacy, _ordnance], true];
private _sentDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_SENT", ""]) isEqualTo _token || {diag_tickTime > _sentDeadline}};
uiSleep 5;

private _audit = missionNamespace getVariable ["YSF_task_request_audit", []];
private _find = {
    params ["_id", "_accepted", "_reason"];
    _audit findIf {(_x # 0) isEqualTo _id && {(_x # 3) isEqualTo _accepted} && {(_x # 4) isEqualTo _reason}}
};
private _validIds = [format ["%1-arty", _token], format ["%1-transport", _token], format ["%1-cas", _token]];
private _validRows = _audit select {(_x # 0) in _validIds && {_x # 3} && {(_x # 4) isEqualTo "accepted"}};
private _validOk = (count _validRows) isEqualTo 3;
["vigil.governorAuthority.validSchemas", _validOk, format ["validRows=%1|audit=%2", _validRows, _audit]] call _assert;

private _tasks = [_arty, _transport, _cas] apply {
    private _rec = (call YSF__mgr) getOrDefault [[_x] call YSF_taskKey, objNull];
    if (typeName _rec isEqualTo "HASHMAP") then {_rec getOrDefault ["task", objNull]} else {objNull}
};
private _serverBuiltOk = (count (_tasks select {typeName _x isEqualTo "HASHMAP"})) isEqualTo 3
    && {(_tasks # 0) getOrDefault ["type", ""] isEqualTo "artillery"}
    && {(_tasks # 1) getOrDefault ["type", ""] isEqualTo "transport"}
    && {(_tasks # 2) getOrDefault ["type", ""] isEqualTo "cas"}
    && {(_tasks findIf {!(_x getOrDefault ["serverBuilt", false])}) < 0}
    && {(_tasks findIf {(_x getOrDefault ["requestOwner", 0]) <= 2}) < 0}
    && {(_tasks findIf {(_x getOrDefault ["requestId", ""]) isEqualTo ""}) < 0};
["vigil.governorAuthority.serverBuilt", _serverBuiltOk, format ["tasks=%1", _tasks apply {if (typeName _x isEqualTo "HASHMAP") then {[_x getOrDefault ["type", ""], _x getOrDefault ["requestId", ""], _x getOrDefault ["requestOwner", 0], _x getOrDefault ["serverBuilt", false]]} else {["missing"]}}]] call _assert;

private _authorityOk = ([format ["%1-forged-requester", _token], false, "invalid_requester"] call _find) >= 0
    && {([format ["%1-wrong-side", _token], false, "wrong_side"] call _find) >= 0};
["vigil.governorAuthority.requesterAndAsset", _authorityOk, format ["audit=%1", _audit]] call _assert;

private _schemaOk = ([format ["%1-code-payload", _token], false, "malformed_payload"] call _find) >= 0
    && {([format ["%1-unsupported", _token], false, "unsupported_task_type"] call _find) >= 0}
    && {!(missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", false])};
["vigil.governorAuthority.malformedAndUnsupported", _schemaOk, format ["sentinel=%1|audit=%2", missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", false], _audit]] call _assert;

private _casTask = _tasks param [2, objNull];
private _casRec = (call YSF__mgr) getOrDefault [[_cas] call YSF_taskKey, objNull];
private _duplicateOk = ([format ["%1-cas", _token], false, "duplicate"] call _find) >= 0
    && {([format ["%1-cas-busy", _token], false, "equivalent_duplicate"] call _find) >= 0}
    && {typeName _casTask isEqualTo "HASHMAP"}
    && {typeName _casRec isEqualTo "HASHMAP"}
    && {((_casRec get "task") get "id") isEqualTo (_casTask get "id")}
    && {((_casRec get "task") get "gen") isEqualTo (_casTask get "gen")};
["vigil.governorAuthority.duplicateAndBusy", _duplicateOk, format ["task=%1|audit=%2", if (typeName _casTask isEqualTo "HASHMAP") then {[_casTask get "id", _casTask get "gen"]} else {[]}, _audit]] call _assert;

private _legacyResult = missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_LEGACY_RESULT", "missing"];
private _legacyRec = (call YSF__mgr) getOrDefault [[_legacy] call YSF_taskKey, objNull];
if (typeName _legacyRec isEqualTo "HASHMAP" && {_legacyRec getOrDefault ["enabled", false]}) then {[_legacy] call YSF_taskTick;};
private _legacyOk = (_legacyResult isEqualTo false)
    && {typeName ((call YSF__mgr) getOrDefault [[_legacy] call YSF_taskKey, objNull]) isNotEqualTo "HASHMAP"}
    && {!(missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", false])};
["vigil.governorAuthority.legacyCodeRejected", _legacyOk, format ["clientResult=%1|recordType=%2|sentinel=%3", _legacyResult, typeName _legacyRec, missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", false]]] call _assert;

{
    if (typeName _x isEqualTo "HASHMAP") then {
        [_x, "cancelled"] call YSF__terminate;
        [_x get "veh"] call YSF_taskTick;
    };
} forEach _tasks;
private _terminalDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _terminalDeadline}};
private _terminalOk = (count (_tasks select {typeName _x isEqualTo "HASHMAP" && {_x getOrDefault ["finalized", false]} && {(_x getOrDefault ["state", ""]) isEqualTo "cancelled"}})) isEqualTo 3
    && {(missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_CLIENT_DONE", ""]) isEqualTo _token};
["vigil.governorAuthority.terminalResults", _terminalOk, format ["states=%1|clientDone=%2", _tasks apply {if (typeName _x isEqualTo "HASHMAP") then {[_x getOrDefault ["state", ""], _x getOrDefault ["finalized", false]]} else {["missing"]}}, missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_CLIENT_DONE", ""]]] call _assert;

{if (!isNull _x) then {deleteVehicle _x;};} forEach _objects;
{if (!isNull _x) then {deleteGroup _x;};} forEach _groups;
private _deletionDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_objects findIf {!isNull _x}) < 0 || {diag_tickTime > _deletionDeadline}};
missionNamespace setVariable ["YSF_task_managers", _initialManagers];
missionNamespace setVariable ["YSF_task_request_audit", _initialAudit];
missionNamespace setVariable ["YSF_task_request_cache", _initialCache];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", nil];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_FIXTURE", nil, true];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_SENT", nil, true];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_LEGACY_RESULT", nil, true];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_CLIENT_DONE", nil, true];
if (_initialPFH >= 0) then {[1] call YSF_governorStart;};
private _cleanupOk = (missionNamespace getVariable ["YSF_task_managers", createHashMap]) isEqualTo _initialManagers
    && {(missionNamespace getVariable ["YSF_task_request_audit", []]) isEqualTo _initialAudit}
    && {(missionNamespace getVariable ["YSF_task_request_cache", createHashMap]) isEqualTo _initialCache}
    && {isNil {missionNamespace getVariable "TRIBUNAL_GOV_AUTH_SENTINEL"}}
    && {_objects findIf {!isNull _x} < 0}
    && {(_initialPFH < 0) || {(missionNamespace getVariable ["YSF_governorPFH", -1]) >= 0}};
["vigil.governorAuthority.cleanup", _cleanupOk, format ["objects=%1|managerRestored=%2|auditRestored=%3|pfh=%4", _objects apply {isNull _x}, (missionNamespace getVariable ["YSF_task_managers", createHashMap]) isEqualTo _initialManagers, (missionNamespace getVariable ["YSF_task_request_audit", []]) isEqualTo _initialAudit, missionNamespace getVariable ["YSF_governorPFH", -1]]] call _assert;
'''


CLIENT_SQF = r'''
uiNamespace setVariable ["YSF_task_request_results", []];
private _deadline = diag_tickTime + 90;
private _fixture = [];
waitUntil {uiSleep 0.05; _fixture = missionNamespace getVariable ["TRIBUNAL_GOV_AUTH_FIXTURE", []]; (count _fixture) isEqualTo 7 || {diag_tickTime > _deadline}};
_fixture params ["_fixtureToken", "_arty", "_transport", "_cas", "_wrongSide", "_legacy", "_ordnance"];

private _submit = {
    params ["_id", "_requester", "_vehicle", "_type", "_payload"];
    [_id, _requester, _vehicle, _type, _payload] remoteExecCall ["YSF_fnc_taskRequestServer", 2];
};

[format ["%1-arty", _token], clientOwner, _arty, "artillery", [[[1600, 1850, 0]], _ordnance]] call _submit;
[format ["%1-transport", _token], clientOwner, _transport, "transport", [[1640, 1850, 0], 40, false, false, "dispatch"]] call _submit;
[format ["%1-cas", _token], clientOwner, _cas, "cas", [[1680, 1850, 0], 80, 1]] call _submit;
[format ["%1-cas", _token], clientOwner, _cas, "cas", [[1680, 1850, 0], 80, 1]] call _submit;
[format ["%1-cas-busy", _token], clientOwner, _cas, "cas", [[1680, 1850, 0], 80, 1]] call _submit;
[format ["%1-forged-requester", _token], -1, _arty, "artillery", [[[1600, 1850, 0]], _ordnance]] call _submit;
[format ["%1-wrong-side", _token], clientOwner, _wrongSide, "artillery", [[[1720, 1850, 0]], (getArtilleryAmmo [_wrongSide]) param [0, ""]]] call _submit;
private _codePayload = createHashMapFromArray [["handler", {missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", true, true];}]];
[format ["%1-code-payload", _token], clientOwner, _arty, "artillery", _codePayload] call _submit;
[format ["%1-unsupported", _token], clientOwner, _arty, "recon", []] call _submit;

private _legacyHandlers = createHashMapFromArray [
    ["init", {missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_SENTINEL", true, true]; "complete"}],
    ["finally", {"complete"}]
];
private _legacyTask = ["forged", _legacy, _legacyHandlers, [], 10, 3] call YSF_taskNew;
private _legacyResult = [_legacy, _legacyTask] call YSF_taskAssignRemote;
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_LEGACY_RESULT", _legacyResult, true];
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_SENT", _token, true];

private _receiptDeadline = diag_tickTime + 30;
private _rows = [];
waitUntil {
    uiSleep 0.05;
    _rows = uiNamespace getVariable ["YSF_task_request_results", []];
    private _accepted = _rows select {(_x # 1) isEqualTo "accepted" && {_x # 2}};
    private _rejected = _rows select {(_x # 1) isEqualTo "rejected" && {!(_x # 2)}};
    (count _accepted) isEqualTo 3 && {(count _rejected) isEqualTo 6} || {diag_tickTime > _receiptDeadline}
};
private _accepted = _rows select {(_x # 1) isEqualTo "accepted" && {_x # 2}};
private _rejected = _rows select {(_x # 1) isEqualTo "rejected" && {!(_x # 2)}};
private _reasons = _rejected apply {_x # 3};
private _expectedReasons = ["duplicate", "equivalent_duplicate", "invalid_requester", "wrong_side", "malformed_payload", "unsupported_task_type"];
private _receiptOk = (count _accepted) isEqualTo 3 && {(count _rejected) isEqualTo 6}
    && {_expectedReasons findIf {!(_x in _reasons)} < 0};
["vigil.governorAuthority.clientReceipts", _receiptOk, format ["owner=%1|rows=%2", clientOwner, _rows]] call _assert;
private _audienceOk = (_rows findIf {(_x # 6) isNotEqualTo clientOwner}) < 0 && {(_rows findIf {(_x # 0) find _token isNotEqualTo 0}) < 0};
["vigil.governorAuthority.clientAudience", _audienceOk, format ["owner=%1|rows=%2", clientOwner, _rows]] call _assert;

private _terminalDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _rows = uiNamespace getVariable ["YSF_task_request_results", []]; (count (_rows select {(_x # 1) isEqualTo "terminal" && {(_x # 5) isEqualTo "cancelled"}})) isEqualTo 3 || {diag_tickTime > _terminalDeadline}};
missionNamespace setVariable ["TRIBUNAL_GOV_AUTH_CLIENT_DONE", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-governor-authority",
    tier="gameplay",
    server_expected=frozenset(SERVER_ASSERTIONS),
    client_expected=frozenset(CLIENT_ASSERTIONS),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "visual-support-tablet", "feature": "task-governor-authority"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A real authenticated client submits only bounded declarative artillery, transport, and CAS data; Vigil validates requester and asset authority, builds registered handlers on the server, rejects code-bearing, malformed, replayed, and task-equivalent requests, and returns correlated requester-scoped acceptance and terminal results.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="The canonical review found that clients constructed executable handler maps and opaque tasks for generic server execution. The refined data-only endpoint and matched real-client positive and negative requests make boundary arrival, server construction, rejection cause, generation preservation, nonexecution, correlation, and cleanup direct oracles.",
        dependencies=("Vigil server governor", "Vigil artillery/transport/CAS handler factories", "CBA", "one authenticated real player client"),
        evidence_types=frozenset({"request-receipt", "requester-identity", "asset-authority", "schema-validation", "generation-identity", "negative-control", "terminal-cause", "cleanup"}),
        locality_requirements="The dedicated server owns all task generations and builds every executable handler. Client-a is authenticated by remoteExecutedOwner and player ownership; its receipts are targeted only to that owner. Client-N, JIP, ownership migration, and remote cancellation are excluded.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
