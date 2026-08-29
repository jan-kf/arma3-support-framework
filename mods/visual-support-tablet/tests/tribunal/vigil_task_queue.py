"""Permanent contract for Vigil per-asset task queues and operational display."""

from tribunal.runner.model import Scenario, ScenarioReview


TAB_REGIONS = (
    {"x": 160, "y": 40, "width": 120, "height": 40},
    {"x": 280, "y": 40, "width": 120, "height": 40},
    {"x": 400, "y": 40, "width": 120, "height": 40},
    {"x": 520, "y": 40, "width": 120, "height": 40},
)

SERVER_ASSERTIONS = (
    "vigil.queue.fixture",
    "vigil.queue.accepted",
    "vigil.queue.duplicateSpecific",
    "vigil.queue.bounded",
    "vigil.queue.replacement",
    "vigil.queue.fifoActivation",
    "vigil.queue.historyBounded",
    "vigil.queue.snapshot",
    "vigil.queue.cleanup",
)

CLIENT_ASSERTIONS = (
    "vigil.queue.receipts",
    "vigil.queue.overlayCrossTab",
    "vigil.queue.overlayTheme",
    "vigil.queue.refreshMovement",
    "vigil.queue.compactUi",
    "vigil.queue.activationMessages",
    "vigil.queue.clientCleanup",
)

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-task-queue",
        "version": 2,
        "feature_family": "pontifex-vigil-task-queue",
        "name": "Vigil per-asset task queue and operational display",
        "definition": {
            "kind": "dedicated multiplayer specification",
            "reference": "mods/visual-support-tablet/tests/tribunal/vigil_task_queue.py",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA and Vigil; one authenticated WEST client and server-local WEST support assets",
            "participants": {
                "server": "owns active generations, FIFO queues, replacement, bounded history, and public side-scoped presentation rows",
                "client-a": "submits declarative requests and operates the real themed Assets-page map",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:task-queue",
        "label": "Vigil per-asset task queue and operational display",
        "kind": "product_behavior",
        "aliases": ["Vigil task queue", "Vigil operational overlay"],
        "biki_context": ["biki-page:17234", "arma:arma-3-cfgremoteexec"],
    },
    "arms": [
        {"key": "fixture", "role": "baseline", "description": "One transport and one artillery asset establish independent active-task records", "assertions": [SERVER_ASSERTIONS[0]]},
        {"key": "fifo", "role": "treatment", "description": "Four non-equivalent transport requests queue FIFO and activate in request order", "assertions": [SERVER_ASSERTIONS[1], SERVER_ASSERTIONS[5], CLIENT_ASSERTIONS[0], CLIENT_ASSERTIONS[5]]},
        {"key": "duplicates-and-bound", "role": "negative_control", "description": "A transport-equivalent request is rejected by transport semantics and a fifth queued request is rejected at the queue bound", "assertions": [SERVER_ASSERTIONS[2], SERVER_ASSERTIONS[3]]},
        {"key": "replacement", "role": "treatment", "description": "An explicit replacement cancels the current generation, activates first, and preserves the FIFO behind it", "assertions": [SERVER_ASSERTIONS[4], SERVER_ASSERTIONS[5]]},
        {"key": "history", "role": "treatment", "description": "Eleven real terminal transport requests retain only the eight most recent records", "assertions": [SERVER_ASSERTIONS[6], SERVER_ASSERTIONS[7], CLIENT_ASSERTIONS[4]]},
        {"key": "operational-display", "role": "treatment", "description": "The real Assets map draws both active assets and their target lines with theme-derived current/off-tab opacity and current movement", "assertions": CLIENT_ASSERTIONS[1:4]},
        {"key": "cleanup", "role": "baseline", "description": "Dialog-local drawing state, fixtures, manager state, audit, cache, and snapshots return to baseline", "assertions": [SERVER_ASSERTIONS[8], CLIENT_ASSERTIONS[6]]},
    ],
    "causal_relationships": [
        {
            "key": "equivalent-v-non-equivalent",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "duplicates-and-bound",
            "target": "fifo",
            "controlled_dimensions": ["same requester", "same transport", "same request schema", "only task-specific destination equivalence differs"],
        },
        {
            "key": "current-v-other-tab",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "operational-display",
            "target": "operational-display",
            "controlled_dimensions": ["same two active assets", "same map and theme", "only selected asset tab differs"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:per-asset-task-queue",
            "text": "Vigil executes one server-owned task per asset, queues up to four non-equivalent requests FIFO, rejects task-equivalent duplicates and a second pending replacement, prioritizes one explicit replacement without disturbing the FIFO, emits correlated activation and terminal results, and retains only eight recent terminal records.",
            "intended_use": "primary_result",
            "assertions": list(SERVER_ASSERTIONS[:8]) + [CLIENT_ASSERTIONS[0], CLIENT_ASSERTIONS[4], CLIENT_ASSERTIONS[5]],
            "rationale": "Authenticated request audit, exact request IDs in active/replacement/queue records, activation order, terminal receipts, and final bounded history distinguish execution from mere submission.",
        },
        {
            "id": "pontifex:vigil:operational-task-display",
            "text": "While the real Vigil tablet is open, friendly actively tasked assets remain visible across tabs with a line to each task target, off-tab assets use reduced theme-derived opacity, and the display follows current asset movement and task state on a three-second refresh boundary.",
            "intended_use": "primary_result",
            "assertions": list(CLIENT_ASSERTIONS[1:4]) + [SERVER_ASSERTIONS[7], SERVER_ASSERTIONS[8], CLIENT_ASSERTIONS[6]],
            "rationale": "Authenticated framebuffer tab interaction is paired with exact client draw rows, themed RGBA values, object/target positions, refresh timestamps, replicated snapshots, and close cleanup.",
        },
    ],
    "unresolved": [
        "Remote cancellation authorization, client-B/JIP isolation, ownership migration, fixed-wing's separate registry lifecycle, and retry/invalid-return policy remain outside this one-client governor-managed task proof."
    ],
}


SERVER_SQF = r'''
private _initialManagers = missionNamespace getVariable ["YSF_task_managers", createHashMap];
private _initialPFH = missionNamespace getVariable ["YSF_governorPFH", -1];
private _initialAudit = missionNamespace getVariable ["YSF_task_request_audit", []];
private _initialCache = missionNamespace getVariable ["YSF_task_request_cache", createHashMap];
private _initialRows = missionNamespace getVariable ["YSF_TASK_OPERATIONAL_ROWS", []];
if (_initialPFH >= 0) then {call YSF_governorStop;};
missionNamespace setVariable ["YSF_task_managers", createHashMap];
missionNamespace setVariable ["YSF_task_request_audit", []];
missionNamespace setVariable ["YSF_task_request_cache", createHashMap];
missionNamespace setVariable ["YSF_TASK_OPERATIONAL_ROWS", [], true];

private _objects = [];
private _groups = [];
private _makeCrewed = {
    params ["_class", "_pos"];
    private _vehicle = createVehicle [_class, _pos, [], 0, "NONE"];
    private _group = createGroup [west, true];
    private _crew = _group createUnit ["B_crew_F", _pos, [], 0, "NONE"];
    _crew moveInDriver _vehicle;
    _objects pushBack _crew;
    _objects pushBack _vehicle;
    _groups pushBack _group;
    _vehicle
};

private _transport = ["B_Heli_Transport_01_F", [2200, 2200, 0]] call _makeCrewed;
private _arty = ["B_MBT_01_arty_F", [2260, 2200, 0]] call _makeCrewed;
private _ordnance = (getArtilleryAmmo [_arty]) param [0, ""];
private _players = [];
private _playerDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    _players = allPlayers select {isPlayer _x && {owner _x > 2}};
    (count _players) isEqualTo 1 || {diag_tickTime > _playerDeadline}
};
private _fixtureOk = isServer
    && {(count _players) isEqualTo 1}
    && {!isNull driver _transport}
    && {!isNull driver _arty}
    && {_ordnance isNotEqualTo ""}
    && {!isNil "YSF_taskEquivalent"}
    && {!isNil "YSF_taskPublishSnapshot"}
    && {!isNil "YSF_taskActivateNext"};
["vigil.queue.fixture", _fixtureOk, format ["players=%1|transport=%2|arty=%3|ordnance=%4", _players apply {owner _x}, netId _transport, netId _arty, _ordnance]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_FIXTURE", [_token, _transport, _arty, _ordnance], true];
private _sentDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_SENT", ""]) isEqualTo _token || {diag_tickTime > _sentDeadline}};
uiSleep 3;

private _audit = missionNamespace getVariable ["YSF_task_request_audit", []];
private _find = {
    params ["_suffix", "_accepted", "_reason"];
    private _id = format ["%1-%2", _token, _suffix];
    _audit findIf {(_x # 0) isEqualTo _id && {(_x # 3) isEqualTo _accepted} && {(_x # 4) isEqualTo _reason}}
};
private _acceptedOk = (["active", true, "accepted"] call _find) >= 0
    && {(["arty", true, "accepted"] call _find) >= 0}
    && {(["q1", true, "queued"] call _find) >= 0}
    && {(["q2", true, "queued"] call _find) >= 0}
    && {(["q3", true, "queued"] call _find) >= 0}
    && {(["q4", true, "queued"] call _find) >= 0};
["vigil.queue.accepted", _acceptedOk, format ["audit=%1", _audit]] call _assert;

private _duplicateOk = (["equivalent", false, "equivalent_duplicate"] call _find) >= 0;
["vigil.queue.duplicateSpecific", _duplicateOk, format ["audit=%1", _audit]] call _assert;
private _boundedOk = (["overflow", false, "queue_full"] call _find) >= 0;
["vigil.queue.bounded", _boundedOk, format ["audit=%1", _audit]] call _assert;

private _transportRec = (call YSF__mgr) getOrDefault [[_transport] call YSF_taskKey, objNull];
private _artyRec = (call YSF__mgr) getOrDefault [[_arty] call YSF_taskKey, objNull];
private _current = if (typeName _transportRec isEqualTo "HASHMAP") then {_transportRec getOrDefault ["task", objNull]} else {objNull};
private _replacement = if (typeName _transportRec isEqualTo "HASHMAP") then {_transportRec getOrDefault ["replacement", objNull]} else {objNull};
private _queue = if (typeName _transportRec isEqualTo "HASHMAP") then {_transportRec getOrDefault ["queue", []]} else {[]};
private _queueIds = _queue apply {_x getOrDefault ["requestId", ""]};
private _replacementOk = typeName _current isEqualTo "HASHMAP"
    && {(_current getOrDefault ["requestId", ""]) isEqualTo format ["%1-active", _token]}
    && {(_current getOrDefault ["state", ""]) isEqualTo "cancelled"}
    && {typeName _replacement isEqualTo "HASHMAP"}
    && {(_replacement getOrDefault ["requestId", ""]) isEqualTo format ["%1-replace", _token]}
    && {(["replace-pending", false, "replacement_pending"] call _find) >= 0}
    && {_queueIds isEqualTo ([1,2,3,4] apply {format ["%1-q%2", _token, _x]})};
["vigil.queue.replacement", _replacementOk, format ["current=%1|replacement=%2|queue=%3", if (typeName _current isEqualTo "HASHMAP") then {[_current getOrDefault ["requestId", ""], _current getOrDefault ["state", ""]]} else {[]}, if (typeName _replacement isEqualTo "HASHMAP") then {_replacement getOrDefault ["requestId", ""]} else {"missing"}, _queueIds]] call _assert;

call YSF_taskPublishSnapshot;
private _rows = missionNamespace getVariable ["YSF_TASK_OPERATIONAL_ROWS", []];
private _transportRowIndex = _rows findIf {(_x # 0) isEqualTo netId _transport};
private _artyRowIndex = _rows findIf {(_x # 0) isEqualTo netId _arty};
private _snapshotBefore = _transportRowIndex >= 0
    && {_artyRowIndex >= 0}
    && {count ((_rows # _transportRowIndex) # 7) isEqualTo 5}
    && {(((_rows # _transportRowIndex) # 7) # 0) # 4 isEqualTo "replacement"};
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_VISUAL_ARMED", _token, true];
private _visualDeadline = diag_tickTime + 75;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_VISUAL_DONE", ""]) isEqualTo _token || {diag_tickTime > _visualDeadline}};

private _beforeMove = getPosATL _transport;
_transport setPosATL (_beforeMove vectorAdd [35, 0, 0]);
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_MOVED", [_token, getPosATL _transport], true];
private _movementDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_MOVEMENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _movementDeadline}};

private _activationOrder = [];
[_transport] call YSF_taskTick;
for "_index" from 0 to 4 do {
    _transportRec = (call YSF__mgr) getOrDefault [[_transport] call YSF_taskKey, objNull];
    private _task = _transportRec getOrDefault ["task", objNull];
    _activationOrder pushBack (_task getOrDefault ["requestId", ""]);
    [_transport] call YSF_taskTick;
    [_transport] call YSF_taskTick;
    [_task, "complete"] call YSF__terminate;
    [_transport] call YSF_taskTick;
};
private _expectedActivation = ["replace", "q1", "q2", "q3", "q4"] apply {format ["%1-%2", _token, _x]};
private _fifoOk = _activationOrder isEqualTo _expectedActivation;
["vigil.queue.fifoActivation", _fifoOk, format ["actual=%1|expected=%2", _activationOrder, _expectedActivation]] call _assert;

if (typeName _artyRec isEqualTo "HASHMAP") then {
    [_arty] call YSF_taskTick;
    [_arty] call YSF_taskTick;
    private _artyTask = _artyRec getOrDefault ["task", objNull];
    [_artyTask, "complete"] call YSF__terminate;
    [_arty] call YSF_taskTick;
};
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_MAIN_DONE", _token, true];

private _historySentDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_HISTORY_SENT", ""]) isEqualTo _token || {diag_tickTime > _historySentDeadline}};
private _historyAuditDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _audit = missionNamespace getVariable ["YSF_task_request_audit", []];
    ({(_x # 0) find format ["%1-h", _token] isEqualTo 0 && {_x # 3}} count _audit) isEqualTo 5 || {diag_tickTime > _historyAuditDeadline}
};
private _historyActivation = [];
for "_index" from 1 to 5 do {
    _transportRec = (call YSF__mgr) getOrDefault [[_transport] call YSF_taskKey, objNull];
    private _task = _transportRec getOrDefault ["task", objNull];
    _historyActivation pushBack (_task getOrDefault ["requestId", ""]);
    [_transport] call YSF_taskTick;
    [_transport] call YSF_taskTick;
    [_task, "complete"] call YSF__terminate;
    [_transport] call YSF_taskTick;
};

_transportRec = (call YSF__mgr) getOrDefault [[_transport] call YSF_taskKey, objNull];
private _history = _transportRec getOrDefault ["history", []];
private _historyIds = _history apply {_x # 3};
private _expectedHistory = ["q2", "q3", "q4", "h1", "h2", "h3", "h4", "h5"] apply {format ["%1-%2", _token, _x]};
private _historyOk = (count _history) isEqualTo 8
    && {_historyIds isEqualTo _expectedHistory}
    && {_historyActivation isEqualTo (["h1", "h2", "h3", "h4", "h5"] apply {format ["%1-%2", _token, _x]})};
["vigil.queue.historyBounded", _historyOk, format ["history=%1|activation=%2", _historyIds, _historyActivation]] call _assert;

call YSF_taskPublishSnapshot;
_rows = missionNamespace getVariable ["YSF_TASK_OPERATIONAL_ROWS", []];
_transportRowIndex = _rows findIf {(_x # 0) isEqualTo netId _transport};
_artyRowIndex = _rows findIf {(_x # 0) isEqualTo netId _arty};
private _snapshotOk = _snapshotBefore
    && {_transportRowIndex >= 0}
    && {_artyRowIndex >= 0}
    && {!((_rows # _transportRowIndex) # 2)}
    && {!((_rows # _artyRowIndex) # 2)}
    && {((_rows # _transportRowIndex) # 7) isEqualTo []}
    && {count ((_rows # _transportRowIndex) # 8) isEqualTo 8};
["vigil.queue.snapshot", _snapshotOk, format ["before=%1|rows=%2", _snapshotBefore, _rows]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_FINAL", _token, true];

private _clientDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
{if (!isNull _x) then {deleteVehicle _x;};} forEach _objects;
{if (!isNull _x) then {deleteGroup _x;};} forEach _groups;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; ({!isNull _x} count _objects) isEqualTo 0 || {diag_tickTime > _cleanupDeadline}};
missionNamespace setVariable ["YSF_task_managers", _initialManagers];
missionNamespace setVariable ["YSF_task_request_audit", _initialAudit];
missionNamespace setVariable ["YSF_task_request_cache", _initialCache];
missionNamespace setVariable ["YSF_TASK_OPERATIONAL_ROWS", _initialRows, true];
{
    missionNamespace setVariable [_x, nil, true];
} forEach [
    "TRIBUNAL_VIGIL_QUEUE_FIXTURE",
    "TRIBUNAL_VIGIL_QUEUE_SENT",
    "TRIBUNAL_VIGIL_QUEUE_VISUAL_ARMED",
    "TRIBUNAL_VIGIL_QUEUE_VISUAL_DONE",
    "TRIBUNAL_VIGIL_QUEUE_MOVED",
    "TRIBUNAL_VIGIL_QUEUE_MOVEMENT_DONE",
    "TRIBUNAL_VIGIL_QUEUE_MAIN_DONE",
    "TRIBUNAL_VIGIL_QUEUE_HISTORY_SENT",
    "TRIBUNAL_VIGIL_QUEUE_FINAL",
    "TRIBUNAL_VIGIL_QUEUE_CLIENT_DONE"
];
if (_initialPFH >= 0) then {[1] call YSF_governorStart;};
private _cleanupOk = (_objects findIf {!isNull _x}) < 0
    && {(missionNamespace getVariable ["YSF_task_managers", createHashMap]) isEqualTo _initialManagers}
    && {(missionNamespace getVariable ["YSF_task_request_audit", []]) isEqualTo _initialAudit}
    && {(missionNamespace getVariable ["YSF_task_request_cache", createHashMap]) isEqualTo _initialCache}
    && {(_initialPFH < 0) || {(missionNamespace getVariable ["YSF_governorPFH", -1]) >= 0}};
["vigil.queue.cleanup", _cleanupOk, format ["objects=%1|manager=%2|audit=%3|pfh=%4", _objects apply {isNull _x}, (missionNamespace getVariable ["YSF_task_managers", createHashMap]) isEqualTo _initialManagers, (missionNamespace getVariable ["YSF_task_request_audit", []]) isEqualTo _initialAudit, missionNamespace getVariable ["YSF_governorPFH", -1]]] call _assert;
'''


CLIENT_SQF = r'''
uiNamespace setVariable ["YSF_task_request_results", []];
private _initialTheme = missionNamespace getVariable ["YSF_monochromeBaseColor", [0,1,0,1]];
private _fixture = [];
private _fixtureDeadline = diag_tickTime + 90;
waitUntil {uiSleep 0.05; _fixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_FIXTURE", []]; (count _fixture) isEqualTo 4 || {diag_tickTime > _fixtureDeadline}};
_fixture params ["_fixtureToken", "_transport", "_arty", "_ordnance"];
private _submit = {
    params ["_suffix", "_vehicle", "_type", "_payload", ["_policy", "queue"]];
    [format ["%1-%2", _token, _suffix], clientOwner, _vehicle, _type, _payload, _policy] remoteExecCall ["YSF_fnc_taskRequestServer", 2];
};

["active", _transport, "transport", [[2450,2200,0], 40, false, false, "dispatch"]] call _submit;
["arty", _arty, "artillery", [[[2260,2600,0]], _ordnance]] call _submit;
["q1", _transport, "transport", [[2650,2200,0], 40, false, false, "dispatch"]] call _submit;
["q2", _transport, "transport", [[2850,2200,0], 40, false, false, "dispatch"]] call _submit;
["q3", _transport, "transport", [[3050,2200,0], 40, false, false, "dispatch"]] call _submit;
["q4", _transport, "transport", [[3250,2200,0], 40, false, false, "dispatch"]] call _submit;
["overflow", _transport, "transport", [[3450,2200,0], 40, false, false, "dispatch"]] call _submit;
["equivalent", _transport, "transport", [[2658,2200,0], 40, false, false, "dispatch"]] call _submit;
["replace", _transport, "transport", [[3650,2200,0], 40, false, false, "dispatch"], "replace"] call _submit;
["replace-pending", _transport, "transport", [[3850,2200,0], 40, false, false, "dispatch"], "replace"] call _submit;
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_SENT", _token, true];

private _receiptDeadline = diag_tickTime + 30;
private _receipts = [];
waitUntil {
    uiSleep 0.05;
    _receipts = uiNamespace getVariable ["YSF_task_request_results", []];
    (count (_receipts select {(_x # 1) isEqualTo "accepted" && {_x # 2}})) >= 7
        && {(count (_receipts select {(_x # 1) isEqualTo "rejected" && {!(_x # 2)}})) >= 3}
        || {diag_tickTime > _receiptDeadline}
};
private _acceptedReasons = (_receipts select {(_x # 1) isEqualTo "accepted"}) apply {_x # 3};
private _rejectedReasons = (_receipts select {(_x # 1) isEqualTo "rejected"}) apply {_x # 3};
private _receiptsOk = ({_x isEqualTo "queued"} count _acceptedReasons) isEqualTo 4
    && {({_x isEqualTo "accepted"} count _acceptedReasons) isEqualTo 2}
    && {({_x isEqualTo "replacing"} count _acceptedReasons) isEqualTo 1}
    && {"equivalent_duplicate" in _rejectedReasons}
    && {"queue_full" in _rejectedReasons}
    && {"replacement_pending" in _rejectedReasons};
["vigil.queue.receipts", _receiptsOk, format ["rows=%1", _receipts]] call _assert;

private _visualArmDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_VISUAL_ARMED", ""]) isEqualTo _token || {diag_tickTime > _visualArmDeadline}};
private _inputReadyAt = diag_tickTime + 8;
waitUntil {uiSleep 0.1; diag_tickTime >= _inputReadyAt};
missionNamespace setVariable ["YSF_enableTablet", true];
{
    if (_x in assignedItems player) then {player unlinkItem _x;};
} forEach ["YSF_VigilTerminal_B", "YSF_VigilTerminal_I", "YSF_VigilTerminal_O"];
player linkItem "YSF_VigilTerminal_B";
private _equipDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; "YSF_VigilTerminal_B" in assignedItems player || {diag_tickTime > _equipDeadline}};
if (!isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])) then {closeDialog 0;};
private _closedBeforeArm = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || {diag_tickTime > _closedBeforeArm}};
diag_log "TRIBUNAL_VIGIL_QUEUE|ARMED";

private _openDeadline = diag_tickTime + 55;
private _display = displayNull;
waitUntil {
    uiSleep 0.05;
    _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
    !isNull _display || {diag_tickTime > _openDeadline}
};
uiNamespace setVariable ["YSF_current_selected_asset", _transport];
call YSF_taskOperationalRefresh;
private _initialDraw = [];
private _initialDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.05;
    _initialDraw = uiNamespace getVariable ["YSF_task_operational_draw_rows", []];
    (uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "transport"
        && {(count _initialDraw) isEqualTo 2}
        || {diag_tickTime > _initialDeadline}
};
private _targetDraw = [];
private _targetDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _targetDraw = uiNamespace getVariable ["YSF_task_operational_draw_rows", []];
    private _transportIndex = _targetDraw findIf {(_x # 0) isEqualTo netId _transport};
    private _artyIndex = _targetDraw findIf {(_x # 0) isEqualTo netId _arty};
    (uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "arty"
        && {(count _targetDraw) isEqualTo 2}
        && {_transportIndex >= 0}
        && {_artyIndex >= 0}
        && {abs (((_targetDraw # _transportIndex) # 3) - 0.3) < 0.01}
        && {abs (((_targetDraw # _artyIndex) # 3) - 1) < 0.01}
        || {diag_tickTime > _targetDeadline}
};
private _initialTransport = _initialDraw select {(_x # 0) isEqualTo netId _transport};
private _initialArty = _initialDraw select {(_x # 0) isEqualTo netId _arty};
private _targetTransport = _targetDraw select {(_x # 0) isEqualTo netId _transport};
private _targetArty = _targetDraw select {(_x # 0) isEqualTo netId _arty};
private _crossTabOk = (count _initialTransport) isEqualTo 1
    && {(count _initialArty) isEqualTo 1}
    && {(count _targetTransport) isEqualTo 1}
    && {(count _targetArty) isEqualTo 1}
    && {abs (((_initialTransport # 0) # 3) - 1) < 0.01}
    && {abs (((_initialArty # 0) # 3) - 0.3) < 0.01}
    && {abs (((_targetTransport # 0) # 3) - 0.3) < 0.01}
    && {abs (((_targetArty # 0) # 3) - 1) < 0.01};
["vigil.queue.overlayCrossTab", _crossTabOk, format ["initial=%1|target=%2", _initialDraw, _targetDraw]] call _assert;

uiSleep 2;
private _closeDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || {diag_tickTime > _closeDeadline}};
uiSleep 8;
[] spawn {[] call YSF_UI_OpenTablet;};
private _reopenDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    private _candidate = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
    !isNull _candidate
        && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "transport"}
        && {!isNull (_candidate displayCtrl 88230)}
        || {diag_tickTime > _reopenDeadline}
};
_display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
uiSleep 2;
uiNamespace setVariable ["YSF_current_selected_asset", _transport];
missionNamespace setVariable ["YSF_monochromeBaseColor", [0.2,0.6,0.9,0.8]];
["transport"] call YOSHI_selectAssetType;
private _themedDraw = [];
private _themeDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    _themedDraw = uiNamespace getVariable ["YSF_task_operational_draw_rows", []];
    (count _themedDraw) isEqualTo 2 && {((_themedDraw # 0) # 7) # 0 isEqualTo 0.2} || {diag_tickTime > _themeDeadline}
};
private _themedTransport = _themedDraw select {(_x # 0) isEqualTo netId _transport};
private _themedArty = _themedDraw select {(_x # 0) isEqualTo netId _arty};
private _transportColor = if ((count _themedTransport) isEqualTo 1) then {(_themedTransport # 0) # 7} else {[]};
private _artyColor = if ((count _themedArty) isEqualTo 1) then {(_themedArty # 0) # 7} else {[]};
private _themeOk = (count _themedTransport) isEqualTo 1
    && {(count _themedArty) isEqualTo 1}
    && {(count _transportColor) isEqualTo 4}
    && {(count _artyColor) isEqualTo 4}
    && {abs ((_transportColor # 0) - 0.2) < 0.01}
    && {abs ((_transportColor # 1) - 0.6) < 0.01}
    && {abs ((_transportColor # 2) - 0.9) < 0.01}
    && {abs ((_transportColor # 3) - 0.8) < 0.01}
    && {abs ((_artyColor # 0) - 0.2) < 0.01}
    && {abs ((_artyColor # 1) - 0.6) < 0.01}
    && {abs ((_artyColor # 2) - 0.9) < 0.01}
    && {abs ((_artyColor # 3) - 0.24) < 0.01};
["vigil.queue.overlayTheme", _themeOk, format ["draw=%1", _themedDraw]] call _assert;
call YSF_taskOperationalRefresh;
private _statusText = ctrlText (_display displayCtrl 88230);
private _recentText = ctrlText (_display displayCtrl 88231);
private _compactInitial = (_statusText find "TRANSPORT") >= 0 && {(_statusText find "5 queued") >= 0} && {_recentText isEqualTo "Recent: none"};
private _refreshBefore = uiNamespace getVariable ["YSF_task_operational_last_refresh", -1];
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_VISUAL_DONE", _token, true];

private _moved = [];
private _movedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; _moved = missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_MOVED", []]; (count _moved) isEqualTo 2 || {diag_tickTime > _movedDeadline}};
private _movedPos = _moved param [1, []];
private _movementDraw = [];
private _movementRefreshDeadline = diag_tickTime + 12;
waitUntil {
    uiSleep 0.05;
    _movementDraw = (uiNamespace getVariable ["YSF_task_operational_draw_rows", []]) select {(_x # 0) isEqualTo netId _transport};
    (count _movementDraw) isEqualTo 1
        && {((_movementDraw # 0) # 4) distance2D _movedPos < 2}
        && {(uiNamespace getVariable ["YSF_task_operational_last_refresh", -1]) >= (_refreshBefore + 2.5)}
        || {diag_tickTime > _movementRefreshDeadline}
};
private _refreshOk = (count _movementDraw) isEqualTo 1
    && {((_movementDraw # 0) # 4) distance2D _movedPos < 2}
    && {(uiNamespace getVariable ["YSF_task_operational_last_refresh", -1]) >= (_refreshBefore + 2.5)};
["vigil.queue.refreshMovement", _refreshOk, format ["moved=%1|draw=%2|before=%3|after=%4", _movedPos, _movementDraw, _refreshBefore, uiNamespace getVariable ["YSF_task_operational_last_refresh", -1]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_MOVEMENT_DONE", _token, true];

private _mainDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_MAIN_DONE", ""]) isEqualTo _token || {diag_tickTime > _mainDeadline}};
for "_index" from 1 to 5 do {
    [format ["h%1", _index], _transport, "transport", [[3650 + (_index * 180),2200,0], 40, false, false, "dispatch"]] call _submit;
};
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_HISTORY_SENT", _token, true];

private _finalDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_QUEUE_FINAL", ""]) isEqualTo _token || {diag_tickTime > _finalDeadline}};
private _messageDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    _receipts = uiNamespace getVariable ["YSF_task_request_results", []];
    (count (_receipts select {(_x # 1) isEqualTo "started" && {(_x # 3) isEqualTo "activated"}})) isEqualTo 9
        && {(count (_receipts select {(_x # 1) isEqualTo "terminal"})) isEqualTo 12}
        || {diag_tickTime > _messageDeadline}
};
private _startedIds = (_receipts select {(_x # 1) isEqualTo "started"}) apply {_x # 0};
private _expectedStarted = (["replace", "q1", "q2", "q3", "q4", "h2", "h3", "h4", "h5"] apply {format ["%1-%2", _token, _x]});
private _messagesOk = _startedIds isEqualTo _expectedStarted
    && {(count (_receipts select {(_x # 1) isEqualTo "terminal"})) isEqualTo 12};
["vigil.queue.activationMessages", _messagesOk, format ["started=%1|terminal=%2|rows=%3", _startedIds, count (_receipts select {(_x # 1) isEqualTo "terminal"}), _receipts]] call _assert;

call YSF_taskOperationalRefresh;
uiSleep 0.1;
_statusText = ctrlText (_display displayCtrl 88230);
_recentText = ctrlText (_display displayCtrl 88231);
private _finalDraw = uiNamespace getVariable ["YSF_task_operational_draw_rows", []];
private _compactOk = _compactInitial
    && {(_statusText find "idle") >= 0}
    && {(_recentText find "TRANSPORT") >= 0}
    && {(_recentText find "COMPLETE") >= 0}
    && {_finalDraw isEqualTo []};
["vigil.queue.compactUi", _compactOk, format ["initial=%1|status=%2|recent=%3|draw=%4", _compactInitial, _statusText, _recentText, _finalDraw]] call _assert;

if (!isNull _display) then {closeDialog 0;};
private _clientCleanupDeadline = diag_tickTime + 8;
waitUntil {uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || {diag_tickTime > _clientCleanupDeadline}};
player unlinkItem "YSF_VigilTerminal_B";
missionNamespace setVariable ["YSF_monochromeBaseColor", _initialTheme];
private _clientCleanupOk = isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])
    && {(uiNamespace getVariable ["YSF_task_operational_draw_rows", []]) isEqualTo []}
    && {(uiNamespace getVariable ["YSF_task_operational_refresh_token", "stale"]) isEqualTo ""};
["vigil.queue.clientCleanup", _clientCleanupOk, format ["display=%1|draw=%2|token=%3", !isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]), uiNamespace getVariable ["YSF_task_operational_draw_rows", []], uiNamespace getVariable ["YSF_task_operational_refresh_token", "stale"]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_QUEUE_CLIENT_DONE", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-task-queue",
    tier="gameplay",
    server_expected=frozenset(SERVER_ASSERTIONS),
    client_expected=frozenset(CLIENT_ASSERTIONS),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={
        "product": "visual-support-tablet",
        "feature": "task-queue-operational-display",
        "visual_driver": "tabbed-control",
        "visual_armed_marker": "TRIBUNAL_VIGIL_QUEUE|ARMED",
        "visual_regions": TAB_REGIONS,
        "visual_initial_index": 0,
        "visual_target_index": 1,
        "future_client_isolation": "client-b must see only its eligible side-scoped operational rows and no requester-private receipts",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Governor-managed Vigil assets execute one active task, queue four non-equivalent requests FIFO, reject task-equivalent duplicates, accept explicit replacement priority, retain eight terminal records, and render all friendly active assets plus target lines across tabs with theme-derived opacity and periodic current state.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="The resolved product decision replaces global busy rejection and the retired homepage with per-asset server state and a compact Assets-page overlay. Exact request IDs, activation/terminal receipts, bounded snapshots, real tab input, themed draw rows, movement, and cleanup directly prove the retained contract.",
        dependencies=("Vigil governor and task factories", "Vigil tablet", "CBA", "one authenticated real player client", "authenticated framebuffer input"),
        evidence_types=frozenset({"request-receipt", "queue-order", "generation-identity", "terminal-history", "replication", "client-ui-state", "framebuffer", "theme", "movement", "cleanup"}),
        locality_requirements="The dedicated server owns active, replacement, FIFO, history, and public side-tagged rows. Client-a owns the display and filters rows to its side. Client-B/JIP and ownership migration remain excluded.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
