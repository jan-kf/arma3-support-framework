"""Client-owned and active-ownership-migration coverage for Field Utilities towing."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_SQF = r'''
localNamespace setVariable ["YFU_TOW_OPERATIONS", createHashMap];
localNamespace setVariable ["YFU_TOW_OBJECT_CLAIMS", createHashMap];
localNamespace setVariable ["YFU_TOW_REQUESTS", createHashMap];
localNamespace setVariable ["YFU_TOW_AUDIT", []];

private _readyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_READY", ""]) isEqualTo _token
        || {diag_tickTime > _readyDeadline}
};
private _clientOwner = missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_OWNER", -1];
private _player = objNull;
private _playerDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _players = allPlayers select {alive _x && {isPlayer _x} && {(owner _x) isEqualTo _clientOwner}};
    _player = _players param [0, objNull];
    !isNull _player || {diag_tickTime > _playerDeadline}
};

private _origin = [2400, 5600, 0];
private _spawn = {
    params ["_class", "_offset"];
    private _object = createVehicle [_class, _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setVehiclePosition [_origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setDir 0;
    _object setFuel 0;
    _object engineOn false;
    _object setVelocity [0, 0, 0];
    _object setAngularVelocity [0, 0, 0];
    _object
};
private _tow = ["B_MRAP_01_F", [0, 5, 0]] call _spawn;
private _cargo = ["C_Offroad_01_F", [0, -3, 0]] call _spawn;
private _towId = netId _tow;
private _cargoId = netId _cargo;
private _transferDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    if (owner _tow isNotEqualTo _clientOwner) then {_tow setOwner _clientOwner;};
    if (owner _cargo isNotEqualTo _clientOwner) then {_cargo setOwner _clientOwner;};
    owner _tow isEqualTo _clientOwner && {owner _cargo isEqualTo _clientOwner}
        || {diag_tickTime > _transferDeadline}
};
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_SETUP", [_token, _towId, _cargoId, _clientOwner], true];
private _clientOwnedDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_OWNED", ""]) isEqualTo _token
        || {diag_tickTime > _clientOwnedDeadline}
};
private _proximityDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _players = allPlayers select {alive _x && {isPlayer _x} && {(owner _x) isEqualTo _clientOwner}};
    _player = _players param [0, objNull];
    (!isNull _player && {_player distance _tow < 8}) || {diag_tickTime > _proximityDeadline}
};
private _fixtureOk = !isNull _player
    && {_clientOwner > 2}
    && {!local _tow} && {!local _cargo}
    && {owner _tow isEqualTo _clientOwner} && {owner _cargo isEqualTo _clientOwner}
    && {_tow distance _cargo < YFU_TOW_PAIR_RANGE}
    && {_player distance _tow < 8}
    && {(missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_OWNED", ""]) isEqualTo _token};
["field.towingMigration.clientOwnedFixture", _fixtureOk, format ["player=%1|clientOwner=%2|tow=%3|cargo=%4|distance=%5|requesterDistance=%6", netId _player, _clientOwner, [_towId, local _tow, owner _tow], [_cargoId, local _cargo, owner _cargo], _tow distance _cargo, _player distance _tow]] call _assert;
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_REQUEST_READY", _token, true];

private _attachDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (_tow getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo []
        || {diag_tickTime > _attachDeadline}
};
private _active = _tow getVariable ["YFU_TOW_ACTIVE", []];
private _operationId = _active param [0, ""];
private _tx = (call YFU_fnc_towOperations) getOrDefault [_operationId, createHashMap];
private _ropes = _tx getOrDefault ["ropes", []];
private _parentAck = _tx getOrDefault ["parentAck", []];
private _activeAudit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
private _activeOk = _operationId isNotEqualTo ""
    && {(_tx getOrDefault ["state", ""]) isEqualTo "active"}
    && {(_tx getOrDefault ["owner", -1]) isEqualTo _clientOwner}
    && {_ropes isNotEqualTo []}
    && {(_ropes findIf {isNull _x}) < 0}
    && {_parentAck isEqualTo [_cargoId, _towId, true, _clientOwner]}
    && {_cargo in ropeAttachedObjects _tow}
    && {({_x # 0 isEqualTo "activate" && {_x # 3 isEqualTo _operationId}} count _activeAudit) isEqualTo 1};
["field.towingMigration.activeOnClientOwner", _activeOk, format ["operation=%1|tx=%2|ropes=%3|relationship=%4|locality=%5|audit=%6", _operationId, _tx, _ropes apply {[netId _x, local _x]}, [netId getTowParent _cargo, (ropeAttachedObjects _tow) apply {netId _x}], [_tow, _cargo] apply {[netId _x, local _x, owner _x]}, _activeAudit]] call _assert;
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_ACTIVE", [_token, _operationId, _towId, _cargoId], true];
private _activeClientDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_ACTIVE_CLIENT", ""]) isEqualTo _token
        || {diag_tickTime > _activeClientDeadline}
};

_tow setOwner 2;
_cargo setOwner 2;
private _returnDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    local _tow && {local _cargo} && {owner _tow isEqualTo 2} && {owner _cargo isEqualTo 2}
        || {diag_tickTime > _returnDeadline}
};
uiSleep 1;
private _sameActive = _tow getVariable ["YFU_TOW_ACTIVE", []];
private _migratedTx = (call YFU_fnc_towOperations) getOrDefault [_operationId, createHashMap];
private _migratedRopes = _migratedTx getOrDefault ["ropes", []];
private _migratedOk = local _tow && {local _cargo}
    && {owner _tow isEqualTo 2} && {owner _cargo isEqualTo 2}
    && {_sameActive isEqualTo _active}
    && {(_migratedTx getOrDefault ["state", ""]) isEqualTo "active"}
    && {_migratedRopes isEqualTo _ropes}
    && {(_migratedRopes findIf {isNull _x}) < 0}
    && {(getTowParent _cargo) isEqualTo _tow}
    && {_cargo in ropeAttachedObjects _tow};
["field.towingMigration.activeSurvivesMigration", _migratedOk, format ["before=%1|after=%2|ropes=%3|relationship=%4|locality=%5", _active, _sameActive, _migratedRopes apply {[netId _x, isNull _x, local _x]}, [netId getTowParent _cargo, (ropeAttachedObjects _tow) apply {netId _x}], [_tow, _cargo] apply {[netId _x, local _x, owner _x]}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_RETURNED", [_token, _operationId], true];

private _finalDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (call YFU_fnc_towOperations) isEqualTo createHashMap
        && {(missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_DONE", ""]) isEqualTo _token}
        || {diag_tickTime > _finalDeadline}
};
private _audit = localNamespace getVariable ["YFU_TOW_AUDIT", []];
private _activateRows = _audit select {_x # 0 isEqualTo "activate" && {_x # 3 isEqualTo _operationId}};
private _finalizeRows = _audit select {_x # 0 isEqualTo "finalize" && {(_x # 1) isEqualTo "stowed"} && {((_x # 4) param [0, ""]) isEqualTo _operationId}};
private _finalizedOk = (count _activateRows) isEqualTo 1
    && {(count _finalizeRows) isEqualTo 1}
    && {(call YFU_fnc_towOperations) isEqualTo createHashMap}
    && {(call YFU_fnc_towObjectClaims) isEqualTo createHashMap}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {(_cargo getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {isNull getTowParent _cargo}
    && {(_ropes findIf {!isNull _x}) < 0};
["field.towingMigration.exactOnceFinalization", _finalizedOk, format ["operation=%1|activate=%2|finalize=%3|operations=%4|claims=%5|active=%6|parent=%7|ropes=%8|audit=%9", _operationId, _activateRows, _finalizeRows, count call YFU_fnc_towOperations, count call YFU_fnc_towObjectClaims, [_tow getVariable ["YFU_TOW_ACTIVE", []], _cargo getVariable ["YFU_TOW_ACTIVE", []]], netId getTowParent _cargo, _ropes apply {isNull _x}, _audit]] call _assert;

deleteVehicle _tow;
deleteVehicle _cargo;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _tow && {isNull _cargo} || {diag_tickTime > _cleanupDeadline}};
private _cleanupOk = isNull _tow && {isNull _cargo}
    && {(missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_DONE", ""]) isEqualTo _token}
    && {(call YFU_fnc_towOperations) isEqualTo createHashMap}
    && {(call YFU_fnc_towObjectClaims) isEqualTo createHashMap};
["field.towingMigration.cleanup", _cleanupOk, format ["client=%1|towNull=%2|cargoNull=%3|operations=%4|claims=%5", missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_DONE", ""], isNull _tow, isNull _cargo, count call YFU_fnc_towOperations, count call YFU_fnc_towObjectClaims]] call _assert;
'''


CLIENT_SQF = r'''
uiNamespace setVariable ["YFU_TOW_RESULTS", []];
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_OWNER", clientOwner, true];
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_READY", _token, true];
private _setup = [];
private _setupDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    _setup = missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_SETUP", []];
    (count _setup) isEqualTo 4 || {diag_tickTime > _setupDeadline}
};
private _tow = objectFromNetId (_setup param [1, ""]);
private _cargo = objectFromNetId (_setup param [2, ""]);
private _objectDeadline = diag_tickTime + 15;
waitUntil {uiSleep 0.05; !isNull _tow && {!isNull _cargo} || {diag_tickTime > _objectDeadline}};
private _originalASL = getPosASL player;
private _originalSimulation = simulationEnabled player;
player enableSimulation false;
if (!isNull _tow) then {player setPosASL ((getPosASL _tow) vectorAdd [0, 2, 0]);};
private _clientOwnedOk = !isNull _tow && {!isNull _cargo}
    && {local _tow} && {local _cargo}
    && {(_setup param [3, -1]) isEqualTo clientOwner};
["field.towingMigration.clientOwnedReplica", _clientOwnedOk, format ["setup=%1|tow=%2|cargo=%3|clientOwner=%4", _setup, [netId _tow, local _tow, owner _tow], [netId _cargo, local _cargo, owner _cargo], clientOwner]] call _assert;
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_OWNED", _token, true];
private _requestReadyDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_REQUEST_READY", ""]) isEqualTo _token
        || {diag_tickTime > _requestReadyDeadline}
};

private _attachId = format ["%1-migration-attach", _token];
[_tow, _cargo, _attachId] call YFU_fnc_towRequestAttach;
private _attachResult = [];
private _attachDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _matches = (uiNamespace getVariable ["YFU_TOW_RESULTS", []]) select {(_x # 0) isEqualTo _attachId};
    _attachResult = _matches param [0, []];
    _attachResult isNotEqualTo [] || {diag_tickTime > _attachDeadline}
};
private _active = [];
private _activeDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _active = missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_ACTIVE", []];
    (count _active) isEqualTo 4 || {diag_tickTime > _activeDeadline}
};
private _attachMatches = (uiNamespace getVariable ["YFU_TOW_RESULTS", []]) select {(_x # 0) isEqualTo _attachId};
private _attachOk = (count _attachMatches) isEqualTo 1
    && {(_attachResult param [1, false])}
    && {(_attachResult param [2, ""]) isEqualTo "accepted"}
    && {(_attachResult param [3, ""]) isEqualTo netId _tow}
    && {(_attachResult param [4, ""]) isEqualTo netId _cargo}
    && {(_attachResult param [6, ""]) isEqualTo "active"}
    && {(getTowParent _cargo) isEqualTo _tow}
    && {_cargo in ropeAttachedObjects _tow};
["field.towingMigration.attachReceipt", _attachOk, format ["result=%1|matches=%2|active=%3|relationship=%4|locality=%5", _attachResult, _attachMatches, _active, [netId getTowParent _cargo, (ropeAttachedObjects _tow) apply {netId _x}], [_tow, _cargo] apply {[local _x, owner _x]}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_ACTIVE_CLIENT", _token, true];

private _returned = [];
private _returnDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _returned = missionNamespace getVariable ["TRIBUNAL_TOW_MIGRATION_RETURNED", []];
    (count _returned) isEqualTo 2
        && {!local _tow} && {!local _cargo}
        || {diag_tickTime > _returnDeadline}
};
private _migrationOk = (_returned param [1, ""]) isEqualTo (_active param [1, ""])
    && {!local _tow} && {!local _cargo}
    && {_cargo in ropeAttachedObjects _tow}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo []};
["field.towingMigration.clientMigrationReplica", _migrationOk, format ["returned=%1|active=%2|relationship=%3|locality=%4", _returned, _tow getVariable ["YFU_TOW_ACTIVE", []], [netId getTowParent _cargo, (ropeAttachedObjects _tow) apply {netId _x}], [_tow, _cargo] apply {[local _x, owner _x]}]] call _assert;

private _stowId = format ["%1-migration-stow", _token];
[_tow, _stowId] call YFU_fnc_towRequestStow;
private _stowResult = [];
private _stowDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _matches = (uiNamespace getVariable ["YFU_TOW_RESULTS", []]) select {(_x # 0) isEqualTo _stowId};
    _stowResult = _matches param [0, []];
    _stowResult isNotEqualTo [] && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
        || {diag_tickTime > _stowDeadline}
};
private _stowMatches = (uiNamespace getVariable ["YFU_TOW_RESULTS", []]) select {(_x # 0) isEqualTo _stowId};
private _stowOk = (count _stowMatches) isEqualTo 1
    && {(_stowResult param [1, false])}
    && {(_stowResult param [2, ""]) isEqualTo "stowed"}
    && {(_stowResult param [6, ""]) isEqualTo "detached"}
    && {(ropeAttachedObjects _tow) isEqualTo []}
    && {(_tow getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []}
    && {(_cargo getVariable ["YFU_TOW_ACTIVE", []]) isEqualTo []};
["field.towingMigration.stowReceipt", _stowOk, format ["result=%1|matches=%2|relationship=%3|active=%4|locality=%5", _stowResult, _stowMatches, [netId getTowParent _cargo, (ropeAttachedObjects _tow) apply {netId _x}], [_tow getVariable ["YFU_TOW_ACTIVE", []], _cargo getVariable ["YFU_TOW_ACTIVE", []]], [_tow, _cargo] apply {[local _x, owner _x]}]] call _assert;
player setPosASL _originalASL;
player enableSimulation _originalSimulation;
missionNamespace setVariable ["TRIBUNAL_TOW_MIGRATION_CLIENT_DONE", _token, true];
'''


EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "fieldutils-towing-ownership-migration",
        "version": 1,
        "feature_family": "pontifex-field-utilities-towing",
        "name": "Field Utilities towing ownership migration",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "mods/field-utilities/tests/tribunal/towing_ownership_migration.py",
            "applicability": "Arma 3 dedicated multiplayer with one authenticated client; exact B_MRAP_01_F and C_Offroad_01_F pair transferred client-a to server during one active tow",
            "participants": {
                "server": "owner transitions, transaction authority, authenticated parent acknowledgment, monitor, exact-once finalization and cleanup",
                "client-a": "initial object owner, authenticated requester, owner-local tow-parent mutation, receipts and replication observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:towing-ownership-migration",
        "label": "Field Utilities towing ownership migration",
        "kind": "product_behavior",
        "aliases": ["Client-owned towing", "Tow locality migration"],
        "biki_context": ["biki-page:11222", "biki-page:11227", "biki-page:16747", "biki-page:16751", "biki-page:32302", "biki-page:29427", "biki-page:34337"],
    },
    "arms": [
        {"key": "client-owned-fixture", "role": "baseline", "description": "Both exact vehicles settle on client-a and both machines observe the initial topology", "assertions": ["field.towingMigration.clientOwnedFixture", "field.towingMigration.clientOwnedReplica"]},
        {"key": "client-owned-attach", "role": "treatment", "description": "One authenticated request creates one exact transaction and owner-confirmed relationship", "assertions": ["field.towingMigration.activeOnClientOwner", "field.towingMigration.attachReceipt"]},
        {"key": "active-migration", "role": "treatment", "description": "Both endpoints move to server ownership while operation, rope and relationship identities remain unchanged", "assertions": ["field.towingMigration.activeSurvivesMigration", "field.towingMigration.clientMigrationReplica"]},
        {"key": "finalization", "role": "treatment", "description": "The original requester stows once and all feature and fixture state is removed", "assertions": ["field.towingMigration.exactOnceFinalization", "field.towingMigration.cleanup", "field.towingMigration.stowReceipt"]},
    ],
    "causal_relationships": [
        {"key": "same-operation-across-owner-change", "relation": "COMPARES_WITH", "source": "client-owned-attach", "target": "active-migration", "controlled_dimensions": ["operation ID", "tow identity", "cargo identity", "rope identities", "requesting owner", "mission"]},
    ],
    "propositions": [
        {
            "id": "pontifex:field-utilities:towing-migration-survival",
            "text": "A one-client authenticated Field Utilities tow can start with both vehicles client-owned, preserve its exact active transaction and relationship when both migrate to the server, and finalize once through normal requester stow with complete cleanup.",
            "intended_use": "primary_result",
            "assertions": ["field.towingMigration.clientOwnedFixture", "field.towingMigration.activeOnClientOwner", "field.towingMigration.activeSurvivesMigration", "field.towingMigration.exactOnceFinalization", "field.towingMigration.cleanup", "field.towingMigration.clientOwnedReplica", "field.towingMigration.attachReceipt", "field.towingMigration.clientMigrationReplica", "field.towingMigration.stowReceipt"],
            "rationale": "Independent locality observations, an owner-authenticated exact parent acknowledgment, unchanged operation/object/rope identities, requester receipts, one activate/finalize audit pair and deletion exclude mixed ownership, recreated-operation, timeout-cleanup and stale-state false passes.",
        },
    ],
    "unresolved": [
        "Client-B/JIP/disconnect, reverse active server-to-client transfer, partial endpoint migration, owner change during creation, physical driving during migration, and non-towing consumer locality remain outside this representative proof."
    ],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-towing-ownership-migration",
    tier="gameplay",
    server_expected=frozenset({
        "field.towingMigration.clientOwnedFixture",
        "field.towingMigration.activeOnClientOwner",
        "field.towingMigration.activeSurvivesMigration",
        "field.towingMigration.exactOnceFinalization",
        "field.towingMigration.cleanup",
    }),
    client_expected=frozenset({
        "field.towingMigration.clientOwnedReplica",
        "field.towingMigration.attachReceipt",
        "field.towingMigration.clientMigrationReplica",
        "field.towingMigration.stowReceipt",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "field-utilities", "feature": "towing-ownership-migration"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="An authenticated client can start one exact tow while both vehicles are client-owned; the active relationship and server transaction survive migration of both vehicles to the server, and the same requester can stow it exactly once with complete state and rope cleanup.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="This is the representative high-consequence ownership-migration proof: both machines independently observe each owner transition, exact operation and object identities remain constant, client receipts bracket server audit rows, and finalization removes only the feature transaction, claims, relationship and ropes.",
        dependencies=("CORDIS owner routing", "Field Utilities authoritative towing", "one authenticated client"),
        evidence_types=frozenset({"ownership-transfer", "authoritative-state", "exact-identity", "transaction", "replication", "exact-once", "cleanup"}),
        locality_requirements="The server creates the fixtures, transfers both to client-a before the authenticated attach, retains transaction authority while CORDIS routes owner-local mutation, then reclaims both during the active operation before requester-owned stow and cleanup.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
