"""CORDIS routing, deduplication, result, and recipient specification."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_SQF = r"""
TRIBUNAL_CORDIS_fnc_countA = {
    params ["_runToken", "_label"];
    private _rows = missionNamespace getVariable ["TRIBUNAL_CORDIS_COUNT_A", []];
    _rows pushBack [_runToken, _label, isServer, clientOwner, remoteExecutedOwner];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_COUNT_A", _rows];
};
TRIBUNAL_CORDIS_fnc_countB = {
    params ["_runToken", "_label"];
    private _rows = missionNamespace getVariable ["TRIBUNAL_CORDIS_COUNT_B", []];
    _rows pushBack [_runToken, _label, isServer, clientOwner, remoteExecutedOwner];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_COUNT_B", _rows];
};
TRIBUNAL_CORDIS_fnc_late = {
    params ["_runToken"];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_LATE", [_runToken, isServer, clientOwner]];
};
TRIBUNAL_CORDIS_fnc_destination = {
    params ["_runToken", "_label"];
    private _rows = missionNamespace getVariable ["TRIBUNAL_CORDIS_DESTINATION", []];
    _rows pushBack [_runToken, _label, isServer, clientOwner, remoteExecutedOwner];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_DESTINATION", _rows];
};
TRIBUNAL_CORDIS_fnc_fromClient = {
    params ["_runToken", "_label"];
    private _rows = missionNamespace getVariable ["TRIBUNAL_CORDIS_FROM_CLIENT", []];
    _rows pushBack [_runToken, _label, isServer, clientOwner, remoteExecutedOwner];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_FROM_CLIENT", _rows, true];
};
TRIBUNAL_CORDIS_fnc_clientRecord = {};
TRIBUNAL_CORDIS_fnc_clientRecordB = {};
TRIBUNAL_CORDIS_fnc_clientBroadcast = {};
missionNamespace setVariable ["TRIBUNAL_CORDIS_SERVER_READY", _token, true];

private _readyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_READY", ""]) isEqualTo _token
        || {diag_tickTime > _readyDeadline}
};
private _clientOwnerId = missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_OWNER", -1];
private _playerId = missionNamespace getVariable ["TRIBUNAL_CORDIS_PLAYER_ID", ""];
private _clientPlayer = objectFromNetId _playerId;
private _identityDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    _clientOwnerId = missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_OWNER", -1];
    _playerId = missionNamespace getVariable ["TRIBUNAL_CORDIS_PLAYER_ID", ""];
    _clientPlayer = objectFromNetId _playerId;
    !isNull _clientPlayer && {_clientOwnerId > 2} || {diag_tickTime > _identityDeadline}
};

missionNamespace setVariable ["TRIBUNAL_CORDIS_COUNT_A", []];
missionNamespace setVariable ["TRIBUNAL_CORDIS_COUNT_B", []];
missionNamespace setVariable ["TRIBUNAL_CORDIS_DESTINATION", []];

private _localResult = ["TRIBUNAL_CORDIS_fnc_countA", [_token, "local"]] call YCD_fnc_runOnServer;
private _unknownResult = ["TRIBUNAL_CORDIS_fnc_missing", [_token]] call YCD_fnc_runOnServer;
private _resultStatesOk = (_localResult isEqualTo ["executed", ""])
    && {_unknownResult isEqualTo ["rejected", "unknown_operation"]}
    && {(missionNamespace getVariable ["TRIBUNAL_CORDIS_COUNT_A", []]) isEqualTo [[_token, "local", true, 2, 0]]};
["cordis.result.states", _resultStatesOk, format ["local=%1|unknown=%2|rows=%3", _localResult, _unknownResult, missionNamespace getVariable ["TRIBUNAL_CORDIS_COUNT_A", []]]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_late", nil];
private _missingOnce = ["TRIBUNAL_CORDIS_fnc_late", [_token], format ["%1-late", _token], 1] call YCD_fnc_runOnServerOnce;
TRIBUNAL_CORDIS_fnc_late = {
    params ["_runToken"];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_LATE", [_runToken, isServer, clientOwner]];
};
private _lateOnce = ["TRIBUNAL_CORDIS_fnc_late", [_token], format ["%1-late", _token], 1] call YCD_fnc_runOnServerOnce;
private _missingDidNotClaim = (_missingOnce isEqualTo ["rejected", "unknown_operation"])
    && {_lateOnce isEqualTo ["executed", ""]}
    && {(missionNamespace getVariable ["TRIBUNAL_CORDIS_LATE", []]) isEqualTo [_token, true, 2]};
["cordis.failure.noClaim", _missingDidNotClaim, format ["missing=%1|late=%2|receipt=%3", _missingOnce, _lateOnce, missionNamespace getVariable ["TRIBUNAL_CORDIS_LATE", []]]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CORDIS_COUNT_A", []];
missionNamespace setVariable ["TRIBUNAL_CORDIS_COUNT_B", []];
private _sharedKey = format ["%1-shared", _token];
private _onceA = ["TRIBUNAL_CORDIS_fnc_countA", [_token, "first"], _sharedKey, 1] call YCD_fnc_runOnServerOnce;
private _duplicateA = ["TRIBUNAL_CORDIS_fnc_countA", [_token, "duplicate"], _sharedKey, 1] call YCD_fnc_runOnServerOnce;
private _sameKeyB = ["TRIBUNAL_CORDIS_fnc_countB", [_token, "other-operation"], _sharedKey, 1] call YCD_fnc_runOnServerOnce;
uiSleep 1.5;
private _expiredA = ["TRIBUNAL_CORDIS_fnc_countA", [_token, "expired"], _sharedKey, 1] call YCD_fnc_runOnServerOnce;
private _countA = missionNamespace getVariable ["TRIBUNAL_CORDIS_COUNT_A", []];
private _countB = missionNamespace getVariable ["TRIBUNAL_CORDIS_COUNT_B", []];
private _dedupeOk = (_onceA isEqualTo ["executed", ""])
    && {_duplicateA isEqualTo ["rejected", "duplicate"]}
    && {_sameKeyB isEqualTo ["executed", ""]}
    && {_expiredA isEqualTo ["executed", ""]}
    && {_countA isEqualTo [[_token, "first", true, 2, 0], [_token, "expired", true, 2, 0]]}
    && {_countB isEqualTo [[_token, "other-operation", true, 2, 0]]};
["cordis.dedupe.operationTtl", _dedupeOk, format ["states=%1|a=%2|b=%3", [_onceA, _duplicateA, _sameKeyB, _expiredA], _countA, _countB]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CORDIS_DESTINATION", []];
private _invalidObject = ["TRIBUNAL_CORDIS_fnc_destination", objNull, [_token, "invalid"], format ["%1-destination", _token], 1] call YCD_fnc_runOnObjectOwnerOnce;
private _serverObject = createVehicle ["Land_HelipadEmpty_F", [3150, 4050, 0], [], 0, "CAN_COLLIDE"];
private _validObject = ["TRIBUNAL_CORDIS_fnc_destination", _serverObject, [_token, "valid"], format ["%1-destination", _token], 1] call YCD_fnc_runOnObjectOwnerOnce;
private _destinationRows = missionNamespace getVariable ["TRIBUNAL_CORDIS_DESTINATION", []];
private _destinationOk = (_invalidObject isEqualTo ["rejected", "invalid_destination"])
    && {_validObject isEqualTo ["executed", ""]}
    && {_destinationRows isEqualTo [[_token, "valid", true, 2, 0]]};
["cordis.destination.noClaim", _destinationOk, format ["invalid=%1|valid=%2|rows=%3", _invalidObject, _validObject, _destinationRows]] call _assert;

private _aiGroup = createGroup [west, true];
private _ai = _aiGroup createUnit ["B_Soldier_F", [3160, 4050, 0], [], 0, "NONE"];
private _serverGroupResult = ["TRIBUNAL_CORDIS_fnc_destination", _ai, [_token, "server-group"]] call YCD_fnc_runOnGroupOwner;
private _groupRow = (missionNamespace getVariable ["TRIBUNAL_CORDIS_DESTINATION", []]) select {(_x # 1) isEqualTo "server-group"};
private _serverGroupOk = (_serverGroupResult isEqualTo ["executed", ""])
    && {local _aiGroup}
    && {(groupOwner _aiGroup) isEqualTo 2}
    && {(count _groupRow) isEqualTo 1}
    && {(_groupRow # 0) isEqualTo [_token, "server-group", true, 2, 0]};
["cordis.group.serverOwner", _serverGroupOk, format ["status=%1|groupOwner=%2|groupLocal=%3|rows=%4", _serverGroupResult, groupOwner _aiGroup, local _aiGroup, _groupRow]] call _assert;

private _clientGroup = createGroup [west, true];
private _clientGroupUnit = _clientGroup createUnit ["B_Soldier_F", [3170, 4050, 0], [], 0, "NONE"];
private _clientGroupId = netId _clientGroupUnit;
uiSleep 1;
private _transferAccepted = _clientGroup setGroupOwner _clientOwnerId;
private _transferDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; (groupOwner _clientGroup) isEqualTo _clientOwnerId || {diag_tickTime > _transferDeadline}};
private _liveClientPlayers = allPlayers select {
    alive _x
        && {isPlayer _x}
        && {_x isKindOf "Man"}
        && {!(_x isKindOf "HeadlessClient_F")}
        && {(owner _x) isEqualTo _clientOwnerId}
};
_clientPlayer = _liveClientPlayers param [0, objNull];
_playerId = netId _clientPlayer;
private _recipientFixtureOk = (count _liveClientPlayers) isEqualTo 1
    && {!isNull _clientPlayer}
    && {_clientPlayer in allPlayers}
    && {alive _clientPlayer}
    && {isPlayer _clientPlayer}
    && {(owner _clientPlayer) isEqualTo _clientOwnerId};
["cordis.recipient.fixture", _recipientFixtureOk, format ["players=%1|selected=%2|netId=%3|owner=%4|expected=%5|alive=%6|isPlayer=%7", _liveClientPlayers, _clientPlayer, _playerId, owner _clientPlayer, _clientOwnerId, alive _clientPlayer, isPlayer _clientPlayer]] call _assert;

private _remoteObjectResult = ["TRIBUNAL_CORDIS_fnc_clientRecord", _clientPlayer, [_token, "object-owner", _playerId], format ["%1-object", _token], 1] call YCD_fnc_runOnObjectOwnerOnce;
private _remoteGroupResult = ["TRIBUNAL_CORDIS_fnc_clientRecord", _clientGroupUnit, [_token, "group-owner", _clientGroupId], format ["%1-group", _token], 1] call YCD_fnc_runOnGroupOwnerOnce;

private _emitKey = format ["%1-emit", _token];
private _emitObject = ["TRIBUNAL_CORDIS_fnc_clientRecord", [_token, "object-scope", _playerId], _clientPlayer, _emitKey, 1] call YCD_fnc_emitToTargets;
private _emitDuplicate = ["TRIBUNAL_CORDIS_fnc_clientRecord", [_token, "duplicate", _playerId], _clientPlayer, _emitKey, 1] call YCD_fnc_emitToTargets;
private _emitOtherOperation = ["TRIBUNAL_CORDIS_fnc_clientRecordB", [_token, "same-key-other-operation", _playerId], [_clientPlayer, objNull, _ai], _emitKey, 1] call YCD_fnc_emitToTargets;
private _emitEmpty = ["TRIBUNAL_CORDIS_fnc_clientRecord", [_token, "empty", _playerId], [], format ["%1-empty", _token], 1] call YCD_fnc_emitToTargets;
private _emitWrongSide = ["TRIBUNAL_CORDIS_fnc_clientRecord", [_token, "wrong-side", _playerId], east, format ["%1-wrong", _token], 1] call YCD_fnc_emitToTargets;
private _emitGlobal = ["TRIBUNAL_CORDIS_fnc_clientBroadcast", [_token, "global", _playerId], 0, format ["%1-global", _token], 1] call YCD_fnc_emitToTargets;
private _emitStatusesOk = (_emitObject isEqualTo ["accepted", "recipients"])
    && {_emitDuplicate isEqualTo ["rejected", "duplicate"]}
    && {_emitOtherOperation isEqualTo ["accepted", "recipients"]}
    && {_emitEmpty isEqualTo ["rejected", "no_recipients"]}
    && {_emitWrongSide isEqualTo ["rejected", "no_recipients"]}
    && {_emitGlobal isEqualTo ["accepted", "recipients"]};
["cordis.emit.decisions", _emitStatusesOk, format ["statuses=%1|resolved=%2", [_emitObject, _emitDuplicate, _emitOtherOperation, _emitEmpty, _emitWrongSide, _emitGlobal], [[_clientPlayer] call YCD_fnc_resolveTargets, [[_clientPlayer, objNull, _ai]] call YCD_fnc_resolveTargets, [east] call YCD_fnc_resolveTargets, [0] call YCD_fnc_resolveTargets]]] call _assert;

private _notifyEmpty = ["empty", "CORDIS", 1, [], format ["%1-notify-empty", _token], 1] call YCD_fnc_notifyCurator;
private _notifyWrongSide = ["wrong", "CORDIS", 1, east, format ["%1-notify-wrong", _token], 1] call YCD_fnc_notifyCurator;
private _notifyPositive = ["positive", "CORDIS", 1, _clientPlayer, format ["%1-notify-positive", _token], 1] call YCD_fnc_notifyCurator;
private _notifyDecisionsOk = (_notifyEmpty isEqualTo ["rejected", "no_recipients"])
    && {_notifyWrongSide isEqualTo ["rejected", "no_recipients"]}
    && {_notifyPositive isEqualTo ["accepted", "recipients"]};
["cordis.notify.decisions", _notifyDecisionsOk, format ["empty=%1|wrong=%2|positive=%3", _notifyEmpty, _notifyWrongSide, _notifyPositive]] call _assert;

private _remoteDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (count (missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_RECORDS", []])) >= 5
        && {(count (missionNamespace getVariable ["TRIBUNAL_CORDIS_FROM_CLIENT", []])) >= 2}
        || {diag_tickTime > _remoteDeadline}
};
private _clientRecords = missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_RECORDS", []];
private _fromClient = missionNamespace getVariable ["TRIBUNAL_CORDIS_FROM_CLIENT", []];
private _remoteOwnersOk = (_remoteObjectResult isEqualTo ["accepted", "object_owner"])
    && {_remoteGroupResult isEqualTo ["accepted", "group_owner"]}
    && {_transferAccepted}
    && {(owner _clientPlayer) isEqualTo _clientOwnerId}
    && {(groupOwner _clientGroup) isEqualTo _clientOwnerId}
    && {({_x # 1 isEqualTo "object-owner" && {_x # 5}} count _clientRecords) isEqualTo 1}
    && {({_x # 1 isEqualTo "group-owner" && {_x # 6}} count _clientRecords) isEqualTo 1};
["cordis.owner.remote", _remoteOwnersOk, format ["statuses=%1|transferAccepted=%2|playerOwner=%3|groupOwner=%4|expected=%5|records=%6", [_remoteObjectResult, _remoteGroupResult], _transferAccepted, owner _clientPlayer, groupOwner _clientGroup, _clientOwnerId, _clientRecords]] call _assert;

private _clientRequestOk = (count _fromClient) isEqualTo 2
    && {(_fromClient findIf {_x isEqualTo [_token, "direct-transport", true, 2, _clientOwnerId]}) >= 0}
    && {(_fromClient findIf {_x isEqualTo [_token, "client-server", true, 2, _clientOwnerId]}) >= 0};
["cordis.client.serverRoute", _clientRequestOk, format ["expectedOwner=%1|rows=%2", _clientOwnerId, _fromClient]] call _assert;

private _recipientEvidenceOk = ({_x # 1 isEqualTo "object-scope"} count _clientRecords) isEqualTo 1
    && {({_x # 1 isEqualTo "same-key-other-operation"} count _clientRecords) isEqualTo 1}
    && {({_x # 1 isEqualTo "global"} count _clientRecords) isEqualTo 1}
    && {({_x # 1 in ["duplicate", "empty", "wrong-side"]} count _clientRecords) isEqualTo 0};
["cordis.recipients.exact", _recipientEvidenceOk, format ["records=%1", _clientRecords]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CORDIS_SERVER_RESULT", [_token, _playerId, _clientOwnerId], true];
private _doneDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _doneDeadline}};
uiSleep 1.2;
call YCD_fnc_pruneOnceCache;
private _cache = missionNamespace getVariable ["YCD_onceCache", createHashMap];
private _cacheClean = ((keys _cache) findIf {_token in _x}) < 0;
deleteVehicle _ai;
deleteGroup _aiGroup;
_clientGroup setGroupOwner 2;
private _returnDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (groupOwner _clientGroup) isEqualTo 2 || {diag_tickTime > _returnDeadline}};
deleteVehicle _clientGroupUnit;
deleteGroup _clientGroup;
deleteVehicle _serverObject;
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_countA", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_countB", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_late", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_destination", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_fromClient", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_clientRecord", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_clientRecordB", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_clientBroadcast", nil];
private _cleanupDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; isNull _serverObject && {isNull _ai} || {diag_tickTime > _cleanupDeadline}};
["cordis.cleanup", (missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_DONE", ""]) isEqualTo _token && {_cacheClean} && {isNull _serverObject} && {isNull _ai} && {isNull _clientGroupUnit}, format ["clientDone=%1|cacheKeys=%2|objectNull=%3|aiNull=%4|clientGroupUnitNull=%5", missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_DONE", ""], keys _cache, isNull _serverObject, isNull _ai, isNull _clientGroupUnit]] call _assert;
"""


CLIENT_SQF = r"""
missionNamespace setVariable ["TRIBUNAL_CORDIS_TOKEN", _token];
missionNamespace setVariable ["TRIBUNAL_CORDIS_CLIENT_RECORDS", []];

TRIBUNAL_CORDIS_fnc_clientRecord = {
    params ["_runToken", "_label", "_playerId"];
    private _subject = objectFromNetId _playerId;
    private _rows = missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_RECORDS", []];
    _rows pushBack [_runToken, _label, isServer, clientOwner, remoteExecutedOwner, local _subject, local group _subject];
    missionNamespace setVariable ["TRIBUNAL_CORDIS_CLIENT_RECORDS", _rows, true];
};
TRIBUNAL_CORDIS_fnc_clientRecordB = TRIBUNAL_CORDIS_fnc_clientRecord;
TRIBUNAL_CORDIS_fnc_clientBroadcast = TRIBUNAL_CORDIS_fnc_clientRecord;
TRIBUNAL_CORDIS_fnc_fromClient = {};

private _identityOk = !isNull player && {(netId player) isNotEqualTo ""} && {local player} && {clientOwner > 2};
["cordis.client.identity", _identityOk, format ["player=%1|owner=%2|groupOwner=%3|clientOwner=%4|local=%5|groupLocal=%6", netId player, owner player, groupOwner group player, clientOwner, local player, local group player]] call _assert;
missionNamespace setVariable ["TRIBUNAL_CORDIS_CLIENT_OWNER", clientOwner, true];
missionNamespace setVariable ["TRIBUNAL_CORDIS_PLAYER_ID", netId player, true];
missionNamespace setVariable ["TRIBUNAL_CORDIS_CLIENT_READY", _token, true];

private _serverReadyDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_CORDIS_SERVER_READY", ""]) isEqualTo _token || {diag_tickTime > _serverReadyDeadline}};
[_token, "direct-transport"] remoteExecCall ["TRIBUNAL_CORDIS_fnc_fromClient", 2];
private _clientKey = format ["%1-client-server", _token];
private _queuedA = ["TRIBUNAL_CORDIS_fnc_fromClient", [_token, "client-server"], _clientKey, 1] call YCD_fnc_runOnServerOnce;
private _queuedB = ["TRIBUNAL_CORDIS_fnc_fromClient", [_token, "duplicate"], _clientKey, 1] call YCD_fnc_runOnServerOnce;
["cordis.client.queued", (_queuedA isEqualTo ["queued", "server"]) && {_queuedB isEqualTo ["queued", "server"]}, format ["first=%1|second=%2", _queuedA, _queuedB]] call _assert;

private _result = [];
private _resultDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_CORDIS_SERVER_RESULT", []]; (count _result) isEqualTo 3 || {diag_tickTime > _resultDeadline}};
private _records = missionNamespace getVariable ["TRIBUNAL_CORDIS_CLIENT_RECORDS", []];
private _ownerEvidence = ({_x # 1 isEqualTo "object-owner" && {_x # 5} && {_x # 4 isEqualTo 2}} count _records) isEqualTo 1
    && {({_x # 1 isEqualTo "group-owner" && {_x # 6} && {_x # 4 isEqualTo 2}} count _records) isEqualTo 1};
["cordis.client.ownerExecution", _ownerEvidence, format ["records=%1", _records]] call _assert;
private _fanoutEvidence = ({_x # 1 isEqualTo "object-scope"} count _records) isEqualTo 1
    && {({_x # 1 isEqualTo "same-key-other-operation"} count _records) isEqualTo 1}
    && {({_x # 1 isEqualTo "global"} count _records) isEqualTo 1}
    && {({_x # 1 in ["duplicate", "empty", "wrong-side"]} count _records) isEqualTo 0};
["cordis.client.fanout", _fanoutEvidence, format ["records=%1", _records]] call _assert;

missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_clientRecord", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_clientRecordB", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_fnc_clientBroadcast", nil];
missionNamespace setVariable ["TRIBUNAL_CORDIS_CLIENT_DONE", _token, true];
"""


ASSERT_RESULTS = ["cordis.result.states", "cordis.client.queued", "cordis.client.serverRoute"]
ASSERT_DEDUPE = ["cordis.failure.noClaim", "cordis.dedupe.operationTtl", "cordis.destination.noClaim"]
ASSERT_LOCALITY = ["cordis.group.serverOwner", "cordis.owner.remote", "cordis.client.identity", "cordis.client.ownerExecution"]
ASSERT_RECIPIENTS = ["cordis.recipient.fixture", "cordis.emit.decisions", "cordis.notify.decisions", "cordis.recipients.exact", "cordis.client.fanout"]
ASSERT_CLEANUP = ["cordis.cleanup"]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "cordis-routing", "version": 1,
        "feature_family": "pontifex-cordis-routing",
        "name": "CORDIS routing, deduplication, results, and recipient fan-out",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "mods/core/tests/tribunal/cordis_routing.py",
            "applicability": "Arma 3 dedicated multiplayer with one independently authenticated client and cooperating trusted Pontifex operations",
            "participants": {"server": "routing, deduplication, and recipient authority", "client-a": "object/group owner, request origin, recipient, and independent observer"},
        },
    },
    "knowledge_subject": {
        "key": "pontifex:cordis:routing", "label": "CORDIS authority routing and fan-out", "kind": "product_behavior",
        "aliases": ["CORDIS routing", "CORDIS deduplication"],
        "biki_context": ["biki-page:17235", "biki-page:8369", "biki-page:16966", "biki-page:16964", "biki-page:1644", "biki-page:18596", "biki-page:17291", "biki-page:15663"],
    },
    "arms": [
        {"key": "result_boundaries", "role": "treatment", "description": "Known local and client-origin operations expose executed and queued boundaries while missing operations reject", "assertions": ASSERT_RESULTS},
        {"key": "accepted_once", "role": "treatment", "description": "A valid operation executes once within TTL, a different operation may reuse the caller key, and the original operation executes again after expiry", "assertions": ["cordis.dedupe.operationTtl"]},
        {"key": "invalid_once", "role": "negative_control", "description": "Missing operations and invalid destinations reject before claim, then the corrected request remains executable", "assertions": ["cordis.failure.noClaim", "cordis.destination.noClaim"]},
        {"key": "owner_routes", "role": "treatment", "description": "Server-local and client-owned object/group operations produce exact destination-side locality receipts", "assertions": ASSERT_LOCALITY},
        {"key": "scoped_recipients", "role": "treatment", "description": "Object, filtered-list, and deliberate global emit scopes reach the exact live client; notification calls expose recipient-decision status", "assertions": ["cordis.recipient.fixture", "cordis.emit.decisions", "cordis.notify.decisions", "cordis.recipients.exact", "cordis.client.fanout"]},
        {"key": "empty_wrong_recipient", "role": "negative_control", "description": "Explicit-empty and wrong-side requests reach the server decision boundary without emit delivery", "assertions": ASSERT_RECIPIENTS},
        {"key": "cleanup", "role": "replicate", "description": "The client acknowledges observation and tokenized cache/object state retires", "assertions": ASSERT_CLEANUP},
    ],
    "causal_relationships": [
        {"key": "valid-invalid-claim", "relation": "CAUSAL_PAIR_WITH", "source": "accepted_once", "target": "invalid_once", "controlled_dimensions": ["run token", "operation name after repair", "caller key", "server cache"]},
        {"key": "scoped-empty-delivery", "relation": "CAUSAL_PAIR_WITH", "source": "scoped_recipients", "target": "empty_wrong_recipient", "controlled_dimensions": ["run token", "receiving client", "callback observer", "server authority"]},
        {"key": "server-client-locality", "relation": "COMPARES_WITH", "source": "result_boundaries", "target": "owner_routes", "controlled_dimensions": ["run token", "trusted operation surface", "destination receipt schema"]},
    ],
    "propositions": [
        {"id": "pontifex:cordis:honest-route-result", "text": "CORDIS trusted routes distinguish rejection, queueing, server acceptance, and local execution without representing remote gameplay completion.", "intended_use": "primary_result", "assertions": ASSERT_RESULTS + ASSERT_LOCALITY, "rationale": "Caller-visible states are correlated with exact destination receipts containing machine, transport-origin, object, and group locality evidence."},
        {"id": "pontifex:cordis:operation-aware-dedupe", "text": "A nonempty CORDIS once-key suppresses duplicate accepted operations only within the same operation and TTL, while invalid work consumes no key.", "intended_use": "primary_result", "assertions": ASSERT_DEDUPE, "rationale": "Independent callback counts pair an inside-TTL duplicate, a different operation with the same raw key, comfortably post-expiry reuse, and invalid-then-valid controls."},
        {"id": "pontifex:cordis:exact-recipient-scope", "text": "CORDIS fan-out reaches only requested live real players; an explicit empty or wrong-side scope delivers nowhere rather than broadening to broadcast.", "intended_use": "primary_result", "assertions": ASSERT_RECIPIENTS + ASSERT_CLEANUP, "rationale": "An exact client callback observer records positive object/list/global emit delivery while duplicate, empty, and wrong-side stimuli produce no callback; notification evidence is limited to the authoritative recipient-decision boundary."},
    ],
    "unresolved": [
        "Multiple-client fan-out, client-B isolation, JIP, disconnect, and ownership migration require a second independently authenticated identity.",
        "Visible curator GUI and side-radio audible output remain unproven and are not part of this routing specification.",
        "Consequential consumers continue to own authorization and terminal gameplay acknowledgment; CORDIS remains a trusted broker rather than a public adversarial RPC boundary.",
    ],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="cordis-routing",
    tier="gameplay",
    server_expected=frozenset({
        "cordis.result.states",
        "cordis.failure.noClaim",
        "cordis.dedupe.operationTtl",
        "cordis.destination.noClaim",
        "cordis.group.serverOwner",
        "cordis.recipient.fixture",
        "cordis.emit.decisions",
        "cordis.notify.decisions",
        "cordis.owner.remote",
        "cordis.client.serverRoute",
        "cordis.recipients.exact",
        "cordis.cleanup",
    }),
    client_expected=frozenset({
        "cordis.client.identity",
        "cordis.client.queued",
        "cordis.client.ownerExecution",
        "cordis.client.fanout",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "core", "feature": "cordis-routing"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Trusted named operations execute on the declared server, object owner, or group owner; operation-aware TTL keys suppress only accepted duplicates; invalid work consumes no key; results distinguish rejected, queued, accepted, and executed boundaries; scoped fan-out reaches exactly the requested live real players and never broadens an empty scope.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The reviewed broker required bounded corrections before permanent coverage. The scenario uses destination-side receipts, exact machine identity, independent execution counts, wrong-side/empty controls, expiry margins, and client-observed recipient evidence rather than cache or wrapper status alone.",
        dependencies=("one authenticated client", "native remote execution", "native object/group locality"),
        evidence_types=frozenset({"exact-identity", "authoritative-state", "locality", "negative-control", "replication", "cleanup"}),
        locality_requirements="The server resolves nonlocal object/group ownership; owner-local callbacks independently record clientOwner, remoteExecutedOwner, object/group locality, and exact execution count. Multi-client and JIP fan-out remain deferred.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
