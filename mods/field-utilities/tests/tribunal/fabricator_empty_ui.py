"""Permanent Tier 3 contract for the empty Field Utilities Fabricator terminal."""
from tribunal.runner.model import Scenario, ScenarioReview

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "pontifex.field-utilities.fabricator.empty-terminal",
        "version": 1,
        "feature_family": "field-utilities/fabricator-ui",
        "name": "Fabricator empty catalogue and empty submit rejection",
        "definition": {
            "kind": "dedicated-multiplayer product specification",
            "reference": "mods/field-utilities/tests/tribunal/fabricator_empty_ui.py",
            "legacy_experiment_key": "tribunal:fieldutils-fabricator-empty-ui",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA, ACE and Field Utilities; one authenticated client; real dialog, registered station and empty Virtual Storage module",
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:fabricator",
        "label": "Pontifex Fabricator",
        "kind": "pontifex.feature",
        "aliases": ["Fabricator"],
        "biki_context": ["biki-page:1622", "biki-page:1630", "biki-page:2814"],
    },
    "arms": [
        {"key": "empty_fixture", "role": "baseline", "description": "A registered server-owned Fabricator station and Virtual Storage module with no synchronized catalogue objects", "assertions": ["fabricator.empty.fixture"]},
        {"key": "empty_actions_negative_control", "role": "negative_control", "description": "The real dialog presents its empty row and live Add and Submit actions cannot select, queue or request an absent item", "assertions": ["fabricator.empty.client.rejected", "fabricator.empty.noRequest"]},
        {"key": "closeout", "role": "treatment", "description": "The station, modules and registration close cleanly", "assertions": ["fabricator.empty.cleanup"]},
    ],
    "causal_relationships": [],
    "propositions": [{
        "id": "pontifex:fabricator:empty-terminal-rejects-actions",
        "text": "Under the tested dedicated-server and one-client conditions, a registered Fabricator backed by an empty Virtual Storage module presents the explicit empty-catalogue row, holds no selection or queue, and its live Add and Submit controls create no client request, server audit, transaction or object.",
        "intended_use": "primary_result",
        "assertions": ["fabricator.empty.fixture", "fabricator.empty.client.rejected", "fabricator.empty.noRequest", "fabricator.empty.cleanup"],
        "rationale": "The observer reads the real listbox and activates both shipped buttons while client sentinels and server audit, transaction and census controls distinguish rejection from an unobserved request.",
    }],
    "unresolved": ["Pixel styling, cosmetic hint rendering, client-B/JIP and runtime Eden-module reconfiguration remain outside this proof."],
}

CLIENT_EXPECTED = frozenset({"fabricator.empty.client.rejected"})

CLIENT_SQF = r"""
private _base = [4700, 2780, 0];
player setPosATL _base;
private _placedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; player distance2D _base < 2 || {diag_tickTime > _placedDeadline}};
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_PLAYER", netId player, true];

private _fixture = [];
private _fixtureDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    _fixture = missionNamespace getVariable ["TRIBUNAL_FAB_EMPTY_FIXTURE", []];
    _fixture isNotEqualTo [] || {diag_tickTime > _fixtureDeadline}
};
_fixture params [["_fixtureToken", ""], ["_stationId", ""]];
private _station = objectFromNetId _stationId;

disableSerialization;
[_station, false, mapGridPosition player] call YFU_UI_OpenFabricator;
private _display = displayNull;
private _catalog = controlNull;
private _uiDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _display = uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull];
    if (!isNull _display) then {_catalog = _display displayCtrl 98100;};
    (!isNull _catalog && {(lbSize _catalog) isEqualTo 1}) || {diag_tickTime > _uiDeadline}
};

private _inspect = _display displayCtrl 98110;
private _add = _display displayCtrl 98140;
private _submit = _display displayCtrl 98142;
private _placeholderBefore = [lbSize _catalog, _catalog lbText 0, _catalog lbData 0, _catalog lbPicture 0];
private _sentinel = ["tribunal-empty-queue-sentinel"];
uiNamespace setVariable ["YFU_last_order_request", _sentinel];
uiNamespace setVariable ["YFU_submit_in_progress", false];
uiNamespace setVariable ["YFU_submit_success", false];

missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_READY", _fixtureToken, true];
private _goDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_EMPTY_GO", ""]) isEqualTo _fixtureToken || {diag_tickTime > _goDeadline}
};
_catalog lbSetCurSel 0;
_add ctrlActivate true;
uiSleep 0.1;
_submit ctrlActivate true;
uiSleep 0.5;

private _overlay = [98150, 98151, 98152, 98153, 98154] apply {_display displayCtrl _x};
private _placeholderAfter = [lbSize _catalog, _catalog lbText 0, _catalog lbData 0, _catalog lbPicture 0];
private _clientOk = _placeholderBefore isEqualTo [1, "<No virtual storage items found>", "", ""]
    && {_placeholderAfter isEqualTo _placeholderBefore}
    && {(lbSize _inspect) isEqualTo 0}
    && {isNull (uiNamespace getVariable ["YFU_selected_fabricator_item", objNull])}
    && {(call YFU_assetsQueueEntries) isEqualTo []}
    && {(uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []]) isEqualTo []}
    && {(uiNamespace getVariable ["YFU_last_order_request", []]) isEqualTo _sentinel}
    && {!(uiNamespace getVariable ["YFU_submit_in_progress", true])}
    && {!(uiNamespace getVariable ["YFU_submit_success", true])}
    && {(_overlay findIf {ctrlShown _x}) < 0};
["fabricator.empty.client.rejected", _clientOk, format ["before=%1|after=%2|inspect=%3|selected=%4|queue=%5|dynamic=%6|request=%7|overlay=%8", _placeholderBefore, _placeholderAfter, lbSize _inspect, uiNamespace getVariable ["YFU_selected_fabricator_item", objNull], call YFU_assetsQueueEntries, uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []], uiNamespace getVariable ["YFU_last_order_request", []], _overlay apply {ctrlShown _x}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_REPORT", [_clientOk, _placeholderAfter, _sentinel, clientOwner], true];
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_DONE", _fixtureToken, true];

private _serverDeadline = diag_tickTime + 120;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_FAB_EMPTY_SERVER_DONE"} || {diag_tickTime > _serverDeadline}};
"""

TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-fabricator-empty-ui",
    tier="gameplay",
    server_expected=frozenset({"fabricator.empty.fixture", "fabricator.empty.noRequest", "fabricator.empty.cleanup"}),
    client_expected=CLIENT_EXPECTED,
    server_sqf=r"""
private _player = objNull;
private _playerDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    private _id = missionNamespace getVariable ["TRIBUNAL_FAB_EMPTY_PLAYER", ""];
    _player = if (_id isEqualTo "") then {objNull} else {objectFromNetId _id};
    !isNull _player || {diag_tickTime > _playerDeadline}
};
private _base = [4700, 2780, 0];
private _group = createGroup sideLogic;
private _storageLogic = _group createUnit ["Logic", [0, 0, 0], [], 0, "NONE"];
private _fabricatorLogic = _group createUnit ["Logic", [0, 0, 0], [], 0, "NONE"];
private _station = createVehicle ["Land_CargoBox_V1_F", _base vectorAdd [6, 0, 0], [], 0, "CAN_COLLIDE"];
_fabricatorLogic synchronizeObjectsAdd [_station];
[_storageLogic, 0, []] call YOSHI_setVirtualStorageLogic;
[_fabricatorLogic, 0, []] call YOSHI_setFabricatorLogic;
uiSleep 1;

private _fixtureToken = _token;
private _fixture = [_fixtureToken, netId _station];
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_FIXTURE", _fixture, true];
private _fixtureOk = !isNull _player
    && {(missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", [objNull]]) isEqualTo []}
    && {(synchronizedObjects _storageLogic) isEqualTo []}
    && {(missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", []]) isEqualTo [_station]}
    && {local _station}
    && {_player distance _station < YFU_FABRICATOR_ORDER_RANGE};
["fabricator.empty.fixture", _fixtureOk, format ["fixture=%1|catalogue=%2|storageSync=%3|stations=%4|distance=%5", _fixture, missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", []], synchronizedObjects _storageLogic, missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", []], _player distance _station]] call _assert;

private _readyDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_EMPTY_READY", ""]) isEqualTo _fixtureToken || {diag_tickTime > _readyDeadline}
};
private _before = (allMissionObjects "Land_CargoBox_V1_F") apply {netId _x};
private _auditBefore = +(missionNamespace getVariable ["YFU_fabricatorAudit", []]);
private _txBefore = keys (call YFU_fnc_fabricatorTransactions);
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_GO", _fixtureToken, true];
private _doneDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_EMPTY_DONE", ""]) isEqualTo _fixtureToken || {diag_tickTime > _doneDeadline}
};
private _after = (allMissionObjects "Land_CargoBox_V1_F") apply {netId _x};
private _auditAfter = +(missionNamespace getVariable ["YFU_fabricatorAudit", []]);
private _txAfter = keys (call YFU_fnc_fabricatorTransactions);
private _report = missionNamespace getVariable ["TRIBUNAL_FAB_EMPTY_REPORT", []];
private _noRequestOk = (_report param [0, false])
    && {(_report param [1, []]) isEqualTo [1, "<No virtual storage items found>", "", ""]}
    && {(_report param [2, []]) isEqualTo ["tribunal-empty-queue-sentinel"]}
    && {_before isEqualTo _after}
    && {_auditBefore isEqualTo _auditAfter}
    && {_txBefore isEqualTo _txAfter};
["fabricator.empty.noRequest", _noRequestOk, format ["report=%1|census=%2:%3|audit=%4:%5|tx=%6:%7", _report, _before, _after, _auditBefore, _auditAfter, _txBefore, _txAfter]] call _assert;

deleteVehicle _station;
{deleteVehicle _x;} forEach [_storageLogic, _fabricatorLogic];
deleteGroup _group;
localNamespace setVariable ["YFU_MODULE_STORAGE_RECORDS", createHashMap];
localNamespace setVariable ["YFU_MODULE_FABRICATOR_RECORDS", createHashMap];
call YFU_fnc_rebuildModuleRegistration;
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_FIXTURE", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_GO", nil, true];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.1; isNull _station || {diag_tickTime > _cleanupDeadline}};
private _cleanupOk = isNull _station
    && {(keys (call YFU_fnc_fabricatorTransactions)) isEqualTo _txBefore}
    && {(missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", [objNull]]) isEqualTo []}
    && {(missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", [objNull]]) isEqualTo []};
["fabricator.empty.cleanup", _cleanupOk, format ["stationGone=%1|catalogue=%2|stations=%3|tx=%4", isNull _station, missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", []], missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", []], keys (call YFU_fnc_fabricatorTransactions)]] call _assert;
missionNamespace setVariable ["YFU_fabricatorAudit", nil, false];
missionNamespace setVariable ["TRIBUNAL_FAB_EMPTY_SERVER_DONE", _fixtureToken, true];
""",
    client_expected_by_identity={"client-a": CLIENT_EXPECTED},
    client_sqf=CLIENT_SQF,
    client_sqf_by_identity={"client-a": CLIENT_SQF},
    metadata={
        "product": "field-utilities",
        "feature": "fabricator-empty-ui",
        "respawn_on_start": "0",
        "observer_identities": "client-a",
        "future_client_isolation": "client-B/JIP must independently observe the published empty catalogue without receiving client-a UI state",
    },
    evidence_contract=EVIDENCE_CONTRACT,
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A player opening a registered Fabricator whose Virtual Storage contains no objects sees one explicit empty-catalogue row and no selected item, inspect rows or queue. Activating the live Add and Submit controls creates no request, progress overlay, server audit, transaction or object.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="The shipped empty row and early-return actions express a coherent fail-closed policy. Clearing selected item state on page initialization prevents a prior populated terminal session from leaking a stale selection into this state. The scenario uses a real empty module fixture and real dialog controls with client and server no-request controls.",
        dependencies=("Arma display and listbox controls", "Arma editor module logic synchronization", "one independently authenticated client"),
        evidence_types=frozenset({"real-dialog", "empty-catalogue", "listbox-data", "live-controls", "selection-state", "ordered-queue", "request-sentinel", "negative-control", "server-audit", "transaction-registry", "mission-wide-census", "cleanup"}),
        locality_requirements="Client-a owns the dialog, selection, empty queue and early rejection. The dedicated server owns module registration and is observed for absence of requests, transactions or objects. Client-B/JIP remains outside this proof.",
    ),
)
