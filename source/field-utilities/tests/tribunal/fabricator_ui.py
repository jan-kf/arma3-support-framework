"""Permanent Tier 3 contract for the Field Utilities Fabricator terminal."""

from tribunal.runner.model import Scenario, ScenarioReview


EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "pontifex.field-utilities.fabricator.terminal",
        "version": 2,
        "feature_family": "field-utilities/fabricator-ui",
        "name": "Fabricator terminal browse, mixed packing and grid rejection",
        "definition": {
            "kind": "dedicated-multiplayer product specification",
            "reference": "source/field-utilities/tests/tribunal/fabricator_ui.py",
            "legacy_experiment_key": "tribunal:fieldutils-fabricator-ui",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA, ACE and Field Utilities; one authenticated client; real Fabricator dialog and server-owned registered catalogue",
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:fabricator",
        "label": "Pontifex Fabricator",
        "kind": "pontifex.feature",
        "aliases": ["Fabricator"],
        "biki_context": ["biki-page:1453", "biki-page:1622", "biki-page:2814", "biki-page:9633", "biki-page:14947"],
    },
    "arms": [
        {
            "key": "fixture",
            "role": "baseline",
            "description": "One authenticated client and exact server-owned module, station and three-item catalogue identities",
            "assertions": ["fabricator.ui.fixture"],
        },
        {
            "key": "browse_queue_submit_treatment",
            "role": "treatment",
            "description": "The real dialog presents the exact catalogue and selected cargo, preserves ordered quantities through live controls, and submits that queue to an accepted server order",
            "assertions": ["fabricator.ui.client.browseQueue", "fabricator.ui.client.normalAccepted", "fabricator.ui.normalAccepted"],
        },
        {
            "key": "mixed_class_packed_treatment",
            "role": "treatment",
            "description": "The real dialog submits one heavy and one light catalogue identity in order, and the server publishes exact cargo-preserving heterogeneous clones attached to its packed delivery",
            "assertions": ["fabricator.ui.client.mixedAccepted", "fabricator.ui.mixedPacked"],
        },
        {
            "key": "invalid_grid_negative_control",
            "role": "negative_control",
            "description": "The same live dialog with the same one-item queue rejects malformed airdrop grid text before creating a request, changing the queue, showing progress or reaching server audit",
            "assertions": ["fabricator.ui.client.invalidGridRejected", "fabricator.ui.invalidGridNoRequest"],
        },
        {
            "key": "closeout",
            "role": "treatment",
            "description": "The delivery, catalogue, station, modules, transactions and result variables close cleanly",
            "assertions": ["fabricator.ui.cleanup"],
        },
    ],
    "causal_relationships": [
        {
            "key": "valid-normal-submit-v-invalid-airdrop-grid",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "browse_queue_submit_treatment",
            "target": "invalid_grid_negative_control",
            "controlled_dimensions": ["same authenticated client", "same live Fabricator dialog", "same registered station and catalogue item", "same one-item queue", "valid nearby delivery versus malformed airdrop grid is the varied dimension"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:fabricator:ui-browse-queue-and-invalid-grid",
            "text": "Under the tested dedicated-server and one-client conditions, the real Fabricator dialog presents the exact registered catalogue and selected cargo, preserves ordered quantities through its live queue controls into an accepted nearby order, and rejects malformed airdrop grid text before creating a request or changing client or server transaction state.",
            "intended_use": "primary_result",
            "assertions": ["fabricator.ui.client.browseQueue", "fabricator.ui.client.normalAccepted", "fabricator.ui.normalAccepted", "fabricator.ui.client.invalidGridRejected", "fabricator.ui.invalidGridNoRequest", "fabricator.ui.cleanup"],
            "rationale": "The observer reads live dialog rows and dynamic controls, activates the shipped button handlers, and compares accepted normal submit with malformed-grid submit using exact queue, request sentinel, overlay state, server audit and mission-wide census.",
        },
        {
            "id": "pontifex:fabricator:mixed-class-packed-manifest",
            "text": "Under the tested dedicated-server and one-client conditions, the live Fabricator terminal submits one heavy and one light registered catalogue object in queue order, and the server publishes a packed delivery containing exactly one attached clone of each class with its source cargo preserved.",
            "intended_use": "primary_result",
            "assertions": ["fabricator.ui.client.mixedAccepted", "fabricator.ui.mixedPacked", "fabricator.ui.cleanup"],
            "rationale": "The live controls create the heterogeneous request while server-side type, cargo, attachment, locality and cleanup observations establish the delivered manifest independently of the packer's allocation report.",
        },
    ],
    "unresolved": [
        "Pixel styling, cosmetic progress timing, catalogue/container matrices beyond the exact heavy-plus-light pair, client-B/JIP and ownership migration remain outside this proof.",
    ],
}


CLIENT_EXPECTED = frozenset({
    "fabricator.ui.client.browseQueue",
    "fabricator.ui.client.normalAccepted",
    "fabricator.ui.client.mixedAccepted",
    "fabricator.ui.client.invalidGridRejected",
})


CLIENT_SQF = r"""
private _base = [4700, 2780, 0];
player setPosATL _base;
private _placedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; player distance2D _base < 2 || {diag_tickTime > _placedDeadline}};
missionNamespace setVariable ["TRIBUNAL_FAB_UI_PLAYER", netId player, true];

private _fixture = [];
private _fixtureDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    _fixture = missionNamespace getVariable ["TRIBUNAL_FAB_UI_FIXTURE", []];
    _fixture isNotEqualTo [] || {diag_tickTime > _fixtureDeadline}
};
_fixture params [["_fixtureToken", ""], ["_stationId", ""], ["_heavyId", ""], ["_lightId", ""], ["_oversizeId", ""]];
private _station = objectFromNetId _stationId;
private _heavy = objectFromNetId _heavyId;

disableSerialization;
[_station, false, mapGridPosition player] call YFU_UI_OpenFabricator;
private _display = displayNull;
private _catalog = controlNull;
private _uiDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _display = uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull];
    if (!isNull _display) then {_catalog = _display displayCtrl 98100;};
    (!isNull _catalog && {(lbSize _catalog) isEqualTo 3}) || {diag_tickTime > _uiDeadline}
};

private _catalogRows = [];
private _heavyRow = -1;
private _lightRow = -1;
for "_i" from 0 to ((lbSize _catalog) - 1) do {
    private _id = _catalog lbData _i;
    _catalogRows pushBack [_id, _catalog lbText _i, _catalog lbPicture _i];
    if (_id isEqualTo _heavyId) then {_heavyRow = _i;};
    if (_id isEqualTo _lightId) then {_lightRow = _i;};
};
private _ids = _catalogRows apply {_x # 0};
private _catalogExact = (count _catalogRows) isEqualTo 3
    && {(_ids find _heavyId) >= 0}
    && {(_ids find _lightId) >= 0}
    && {(_ids find _oversizeId) >= 0}
    && {(_catalogRows findIf {
        private _obj = objectFromNetId (_x # 0);
        (_x # 1) isNotEqualTo getText (configFile >> "CfgVehicles" >> typeOf _obj >> "displayName")
            || {!([_x # 2] call YFU_assetsIsImagePath)}
    }) < 0};

_catalog lbSetCurSel _heavyRow;
private _inspect = _display displayCtrl 98110;
private _inspectDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (lbSize _inspect) isEqualTo 4 || {diag_tickTime > _inspectDeadline}};
private _inspectRows = [];
for "_i" from 0 to ((lbSize _inspect) - 1) do {
    _inspectRows pushBack [_inspect lbText _i, _inspect lbPicture _i];
};
private _expectedInspect = [
    format ["3x Weapon: %1", getText (configFile >> "CfgWeapons" >> "arifle_MX_F" >> "displayName")],
    format ["12x Magazine: %1", getText (configFile >> "CfgMagazines" >> "30Rnd_65x39_caseless_mag" >> "displayName")],
    format ["5x Item: %1", getText (configFile >> "CfgWeapons" >> "FirstAidKit" >> "displayName")],
    format ["2x Backpack: %1", getText (configFile >> "CfgVehicles" >> "B_AssaultPack_rgr" >> "displayName")]
];
private _inspectExact = (count _inspectRows) isEqualTo 4
    && {(_inspectRows apply {_x # 0}) isEqualTo _expectedInspect}
    && {(_inspectRows findIf {!([_x # 1] call YFU_assetsIsImagePath)}) < 0};

private _add = _display displayCtrl 98140;
private _submit = _display displayCtrl 98142;
_add ctrlActivate true;
uiSleep 0.1;
private _dynamic = uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []];
private _oneOk = (count _dynamic) isEqualTo 4
    && {(ctrlText (_dynamic # 0)) isEqualTo getText (configFile >> "CfgVehicles" >> typeOf _heavy >> "displayName")}
    && {(ctrlText (_dynamic # 1)) isEqualTo "1x"}
    && {(ctrlText (_dynamic # 2)) isEqualTo "+"}
    && {(ctrlText (_dynamic # 3)) isEqualTo "-"};
(_dynamic # 2) ctrlActivate true;
uiSleep 0.1;
_dynamic = uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []];
private _incrementOk = (ctrlText (_dynamic # 1)) isEqualTo "2x";
(_dynamic # 3) ctrlActivate true;
uiSleep 0.1;
_dynamic = uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []];
private _decrementOk = (ctrlText (_dynamic # 1)) isEqualTo "1x";
_catalog lbSetCurSel _lightRow;
_add ctrlActivate true;
uiSleep 0.1;
_dynamic = uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []];
private _orderedOk = (count _dynamic) isEqualTo 8
    && {(uiNamespace getVariable ["YFU_fabricator_queue_order", []]) isEqualTo [_heavyId, _lightId]};
(_dynamic # 7) ctrlActivate true;
uiSleep 0.1;
_dynamic = uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []];
private _queueReady = (call YFU_assetsQueueEntries) isEqualTo [[_heavyId, _heavy, 1]]
    && {(count _dynamic) isEqualTo 4}
    && {(ctrlText (_dynamic # 1)) isEqualTo "1x"};
private _browseOk = _catalogExact && {_inspectExact} && {_oneOk}
    && {_incrementOk} && {_decrementOk} && {_orderedOk} && {_queueReady}
    && {ctrlEnabled _add} && {ctrlEnabled _submit};
["fabricator.ui.client.browseQueue", _browseOk, format ["catalog=%1|inspect=%2|one=%3|increment=%4|decrement=%5|ordered=%6|queue=%7", _catalogRows, _inspectRows, _oneOk, _incrementOk, _decrementOk, _orderedOk, call YFU_assetsQueueEntries]] call _assert;

uiNamespace setVariable ["YFU_last_order_request", []];
uiNamespace setVariable ["YFU_last_order_result", []];
uiNamespace setVariable ["YFU_submit_in_progress", false];
uiNamespace setVariable ["YFU_submit_success", false];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_READY", "normal", true];
private _normalGoDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_UI_GO", ""]) isEqualTo "normal"
        || {diag_tickTime > _normalGoDeadline}
};
_submit ctrlActivate true;
private _normalStartDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    (uiNamespace getVariable ["YFU_last_order_request", []]) isNotEqualTo []
        || {diag_tickTime > _normalStartDeadline}
};
private _normalDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    !(uiNamespace getVariable ["YFU_submit_in_progress", false])
        || {diag_tickTime > _normalDeadline}
};
private _normalRequest = uiNamespace getVariable ["YFU_last_order_request", []];
private _normalResult = uiNamespace getVariable ["YFU_last_order_result", []];
private _normalSuccess = uiNamespace getVariable ["YFU_submit_success", false];
private _normalOk = _normalSuccess && {(_normalResult param [1, false])}
    && {(_normalResult param [2, ""]) isEqualTo "single"}
    && {(_normalRequest param [2, []]) isEqualTo [[_heavyId, 1]]};
["fabricator.ui.client.normalAccepted", _normalOk, format ["request=%1|result=%2|success=%3", _normalRequest, _normalResult, _normalSuccess]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FAB_UI_REPORT", [_normalRequest, _normalResult, _normalSuccess, clientOwner], true];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_DONE", "normal", true];

private _dismiss = _display displayCtrl 98151;
_dismiss ctrlActivate true;
private _dismissDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (call YFU_assetsQueueEntries) isEqualTo [] || {diag_tickTime > _dismissDeadline}};


[_station, false, mapGridPosition player] call YFU_UI_OpenFabricator;
private _mixedUiDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (lbSize _catalog) isEqualTo 3 || {diag_tickTime > _mixedUiDeadline}};
_catalog lbSetCurSel _heavyRow;
_add ctrlActivate true;
uiSleep 0.1;
_catalog lbSetCurSel _lightRow;
_add ctrlActivate true;
uiSleep 0.1;
private _mixedQueue = call YFU_assetsQueueEntries;
private _mixedQueueOk = (_mixedQueue apply {[_x # 0, _x # 2]}) isEqualTo [[_heavyId, 1], [_lightId, 1]]
    && {(uiNamespace getVariable ["YFU_fabricator_queue_order", []]) isEqualTo [_heavyId, _lightId]};
uiNamespace setVariable ["YFU_last_order_request", []];
uiNamespace setVariable ["YFU_last_order_result", []];
uiNamespace setVariable ["YFU_submit_in_progress", false];
uiNamespace setVariable ["YFU_submit_success", false];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_READY", "mixed", true];
private _mixedGoDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_UI_GO", ""]) isEqualTo "mixed"
        || {diag_tickTime > _mixedGoDeadline}
};
_submit ctrlActivate true;
private _mixedStartDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    (uiNamespace getVariable ["YFU_last_order_request", []]) isNotEqualTo []
        || {diag_tickTime > _mixedStartDeadline}
};
private _mixedDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.1;
    !(uiNamespace getVariable ["YFU_submit_in_progress", false])
        || {diag_tickTime > _mixedDeadline}
};
private _mixedRequest = uiNamespace getVariable ["YFU_last_order_request", []];
private _mixedResult = uiNamespace getVariable ["YFU_last_order_result", []];
private _mixedSuccess = uiNamespace getVariable ["YFU_submit_success", false];
private _mixedOk = _mixedQueueOk
    && {_mixedSuccess}
    && {(_mixedResult param [1, false])}
    && {(_mixedResult param [2, ""]) isEqualTo "multi"}
    && {(_mixedRequest param [2, []]) isEqualTo [[_heavyId, 1], [_lightId, 1]]}
    && {(count (_mixedResult param [4, []])) > 0};
["fabricator.ui.client.mixedAccepted", _mixedOk, format ["queue=%1|request=%2|result=%3|success=%4", _mixedQueue, _mixedRequest, _mixedResult, _mixedSuccess]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FAB_UI_REPORT", [_mixedRequest, _mixedResult, _mixedSuccess, clientOwner], true];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_DONE", "mixed", true];

_dismiss ctrlActivate true;
private _mixedDismissDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (call YFU_assetsQueueEntries) isEqualTo [] || {diag_tickTime > _mixedDismissDeadline}};

[_station, true, "1234-5678"] call YFU_UI_OpenFabricator;
uiSleep 0.1;
_catalog lbSetCurSel _heavyRow;
_add ctrlActivate true;
uiSleep 0.1;
private _gridCtrl = _display displayCtrl 98131;
_gridCtrl ctrlSetText "12XX-5678";
[_gridCtrl] call YFU_deliveryGridChanged;
private _sentinel = ["tribunal-invalid-grid-sentinel"];
uiNamespace setVariable ["YFU_last_order_request", _sentinel];
uiNamespace setVariable ["YFU_submit_in_progress", false];
uiNamespace setVariable ["YFU_submit_success", false];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_READY", "invalid", true];
private _invalidGoDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_UI_GO", ""]) isEqualTo "invalid"
        || {diag_tickTime > _invalidGoDeadline}
};
_submit ctrlActivate true;
uiSleep 0.5;
private _invalidQueue = call YFU_assetsQueueEntries;
private _overlay = [98150, 98151, 98152, 98153, 98154] apply {_display displayCtrl _x};
private _invalidOk = (ctrlText _gridCtrl) isEqualTo "12XX-5678"
    && {(uiNamespace getVariable ["YFU_delivery_target_pos", [1]]) isEqualTo []}
    && {!(uiNamespace getVariable ["YFU_submit_in_progress", true])}
    && {!(uiNamespace getVariable ["YFU_submit_success", true])}
    && {(uiNamespace getVariable ["YFU_last_order_request", []]) isEqualTo _sentinel}
    && {_invalidQueue isEqualTo [[_heavyId, _heavy, 1]]}
    && {(_overlay findIf {ctrlShown _x}) < 0};
["fabricator.ui.client.invalidGridRejected", _invalidOk, format ["grid=%1|target=%2|request=%3|queue=%4|overlay=%5", ctrlText _gridCtrl, uiNamespace getVariable ["YFU_delivery_target_pos", []], uiNamespace getVariable ["YFU_last_order_request", []], _invalidQueue, _overlay apply {ctrlShown _x}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FAB_UI_REPORT", ["invalid", _invalidOk, _sentinel, _invalidQueue, clientOwner], true];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_DONE", "invalid", true];

private _serverDeadline = diag_tickTime + 120;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_FAB_UI_SERVER_DONE"} || {diag_tickTime > _serverDeadline}};
"""


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-fabricator-ui",
    tier="gameplay",
    server_expected=frozenset({
        "fabricator.ui.fixture",
        "fabricator.ui.normalAccepted",
        "fabricator.ui.mixedPacked",
        "fabricator.ui.invalidGridNoRequest",
        "fabricator.ui.cleanup",
    }),
    client_expected=CLIENT_EXPECTED,
    server_sqf=r"""
private _player = objNull;
private _playerDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    private _id = missionNamespace getVariable ["TRIBUNAL_FAB_UI_PLAYER", ""];
    _player = if (_id isEqualTo "") then {objNull} else {objectFromNetId _id};
    !isNull _player || {diag_tickTime > _playerDeadline}
};
private _base = [4700, 2780, 0];
private _group = createGroup sideLogic;
private _storageLogic = _group createUnit ["Logic", [0, 0, 0], [], 0, "NONE"];
private _fabricatorLogic = _group createUnit ["Logic", [0, 0, 0], [], 0, "NONE"];
private _station = createVehicle ["Land_CargoBox_V1_F", _base vectorAdd [6, 0, 0], [], 0, "CAN_COLLIDE"];
private _heavy = createVehicle ["Box_NATO_Ammo_F", _base vectorAdd [0, 60, 0], [], 0, "CAN_COLLIDE"];
clearWeaponCargoGlobal _heavy; clearMagazineCargoGlobal _heavy; clearItemCargoGlobal _heavy; clearBackpackCargoGlobal _heavy;
_heavy addWeaponCargoGlobal ["arifle_MX_F", 3];
_heavy addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 12];
_heavy addItemCargoGlobal ["FirstAidKit", 5];
_heavy addBackpackCargoGlobal ["B_AssaultPack_rgr", 2];
private _light = createVehicle ["Box_NATO_Support_F", _base vectorAdd [0, 66, 0], [], 0, "CAN_COLLIDE"];
clearWeaponCargoGlobal _light; clearMagazineCargoGlobal _light; clearItemCargoGlobal _light; clearBackpackCargoGlobal _light;
_light addItemCargoGlobal ["ToolKit", 1];
private _oversize = createVehicle ["B_Truck_01_transport_F", _base vectorAdd [0, 74, 0], [], 0, "CAN_COLLIDE"];
_storageLogic synchronizeObjectsAdd [_heavy];
_storageLogic synchronizeObjectsAdd [_light];
_storageLogic synchronizeObjectsAdd [_oversize];
_fabricatorLogic synchronizeObjectsAdd [_station];
[_storageLogic, 0, []] call YOSHI_setVirtualStorageLogic;
[_fabricatorLogic, 0, []] call YOSHI_setFabricatorLogic;
uiSleep 1;

TRIBUNAL_FAB_UI_fnc_census = {
    private _all = [];
    {_all append (allMissionObjects _x);} forEach ["Box_NATO_Ammo_F", "Box_NATO_Support_F", "B_Truck_01_transport_F", "Land_CargoBox_V1_F"];
    (_all apply {netId _x}) call BIS_fnc_sortAlphabetically
};
private _sourceCargo = [getWeaponCargo _heavy, getMagazineCargo _heavy, getItemCargo _heavy, getBackpackCargo _heavy];
private _lightSourceCargo = [getWeaponCargo _light, getMagazineCargo _light, getItemCargo _light, getBackpackCargo _light];
private _fixture = [_token, netId _station, netId _heavy, netId _light, netId _oversize];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_FIXTURE", _fixture, true];
private _fixtureOk = !isNull _player
    && {(count (synchronizedObjects _storageLogic)) isEqualTo 3}
    && {(count (synchronizedObjects _fabricatorLogic)) isEqualTo 1}
    && {local _station} && {local _heavy}
    && {_player distance _station < YFU_FABRICATOR_ORDER_RANGE};
["fabricator.ui.fixture", _fixtureOk, format ["fixture=%1|storage=%2|station=%3|distance=%4", _fixture, synchronizedObjects _storageLogic, synchronizedObjects _fabricatorLogic, _player distance _station]] call _assert;

TRIBUNAL_FAB_UI_fnc_phase = {
    params ["_phase", "_timeout"];
    private _readyDeadline = diag_tickTime + 120;
    waitUntil {
        uiSleep 0.1;
        (missionNamespace getVariable ["TRIBUNAL_FAB_UI_READY", ""]) isEqualTo _phase
            || {diag_tickTime > _readyDeadline}
    };
    private _before = call TRIBUNAL_FAB_UI_fnc_census;
    private _auditBefore = +(missionNamespace getVariable ["YFU_fabricatorAudit", []]);
    missionNamespace setVariable ["TRIBUNAL_FAB_UI_GO", _phase, true];
    private _doneDeadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.1;
        (missionNamespace getVariable ["TRIBUNAL_FAB_UI_DONE", ""]) isEqualTo _phase
            || {diag_tickTime > _doneDeadline}
    };
    [
        _before,
        call TRIBUNAL_FAB_UI_fnc_census,
        missionNamespace getVariable ["TRIBUNAL_FAB_UI_REPORT", []],
        (missionNamespace getVariable ["TRIBUNAL_FAB_UI_DONE", ""]) isEqualTo _phase,
        +(missionNamespace getVariable ["YFU_fabricatorAudit", []]) - _auditBefore
    ]
};

private _normal = ["normal", 90] call TRIBUNAL_FAB_UI_fnc_phase;
private _normalReport = _normal # 2;
private _normalRequest = _normalReport param [0, []];
private _normalResult = _normalReport param [1, []];
private _clone = objectFromNetId (_normalResult param [3, ""]);
private _normalOk = (_normal # 3)
    && {_normalReport param [2, false]}
    && {(_normalRequest param [1, ""]) isEqualTo netId _station}
    && {(_normalRequest param [2, []]) isEqualTo [[netId _heavy, 1]]}
    && {!(_normalRequest param [3, true])}
    && {(_normalResult param [1, false])}
    && {(_normalResult param [2, ""]) isEqualTo "single"}
    && {!isNull _clone} && {local _clone}
    && {typeOf _clone isEqualTo typeOf _heavy}
    && {[getWeaponCargo _clone, getMagazineCargo _clone, getItemCargo _clone, getBackpackCargo _clone] isEqualTo _sourceCargo};
["fabricator.ui.normalAccepted", _normalOk, format ["request=%1|result=%2|clone=%3|local=%4|cargo=%5|census=%6:%7|audit=%8", _normalRequest, _normalResult, netId _clone, local _clone, [getWeaponCargo _clone, getMagazineCargo _clone, getItemCargo _clone, getBackpackCargo _clone], _normal # 0, _normal # 1, _normal # 4]] call _assert;


private _mixed = ["mixed", 120] call TRIBUNAL_FAB_UI_fnc_phase;
private _mixedReport = _mixed # 2;
private _mixedRequest = _mixedReport param [0, []];
private _mixedResult = _mixedReport param [1, []];
private _mixedContainers = (_mixedResult param [4, []]) apply {objectFromNetId _x};
private _mixedObjects = [];
{if (!isNull _x) then {_mixedObjects append (attachedObjects _x);};} forEach _mixedContainers;
private _mixedHeavyIndex = _mixedObjects findIf {typeOf _x isEqualTo typeOf _heavy};
private _mixedLightIndex = _mixedObjects findIf {typeOf _x isEqualTo typeOf _light};
private _mixedHeavy = if (_mixedHeavyIndex < 0) then {objNull} else {_mixedObjects # _mixedHeavyIndex};
private _mixedLight = if (_mixedLightIndex < 0) then {objNull} else {_mixedObjects # _mixedLightIndex};
private _mixedTypes = (_mixedObjects apply {typeOf _x}) call BIS_fnc_sortAlphabetically;
private _expectedTypes = ([typeOf _heavy, typeOf _light]) call BIS_fnc_sortAlphabetically;
private _mixedOk = (_mixed # 3)
    && {_mixedReport param [2, false]}
    && {(_mixedRequest param [1, ""]) isEqualTo netId _station}
    && {(_mixedRequest param [2, []]) isEqualTo [[netId _heavy, 1], [netId _light, 1]]}
    && {!(_mixedRequest param [3, true])}
    && {(_mixedResult param [1, false])}
    && {(_mixedResult param [2, ""]) isEqualTo "multi"}
    && {(count _mixedContainers) > 0}
    && {(_mixedContainers findIf {isNull _x || {!local _x} || {isObjectHidden _x}}) < 0}
    && {(count _mixedObjects) isEqualTo 2}
    && {_mixedTypes isEqualTo _expectedTypes}
    && {(_mixedObjects findIf {isNull _x || {!local _x} || {isObjectHidden _x}}) < 0}
    && {!isNull _mixedHeavy}
    && {!isNull _mixedLight}
    && {[getWeaponCargo _mixedHeavy, getMagazineCargo _mixedHeavy, getItemCargo _mixedHeavy, getBackpackCargo _mixedHeavy] isEqualTo _sourceCargo}
    && {[getWeaponCargo _mixedLight, getMagazineCargo _mixedLight, getItemCargo _mixedLight, getBackpackCargo _mixedLight] isEqualTo _lightSourceCargo};
["fabricator.ui.mixedPacked", _mixedOk, format ["request=%1|result=%2|containers=%3|objects=%4|types=%5|heavyCargo=%6|lightCargo=%7|census=%8:%9|audit=%10", _mixedRequest, _mixedResult, _mixedContainers apply {netId _x}, _mixedObjects apply {netId _x}, _mixedTypes, if (isNull _mixedHeavy) then {[]} else {[getWeaponCargo _mixedHeavy, getMagazineCargo _mixedHeavy, getItemCargo _mixedHeavy, getBackpackCargo _mixedHeavy]}, if (isNull _mixedLight) then {[]} else {[getWeaponCargo _mixedLight, getMagazineCargo _mixedLight, getItemCargo _mixedLight, getBackpackCargo _mixedLight]}, _mixed # 0, _mixed # 1, _mixed # 4]] call _assert;

private _invalid = ["invalid", 30] call TRIBUNAL_FAB_UI_fnc_phase;
private _invalidReport = _invalid # 2;
private _invalidOk = (_invalid # 3)
    && {(_invalid # 0) isEqualTo (_invalid # 1)}
    && {(_invalid # 4) isEqualTo []}
    && {(_invalidReport param [0, ""]) isEqualTo "invalid"}
    && {_invalidReport param [1, false]}
    && {(_invalidReport param [2, []]) isEqualTo ["tribunal-invalid-grid-sentinel"]}
    && {(count (_invalidReport param [3, []])) isEqualTo 1};
["fabricator.ui.invalidGridNoRequest", _invalidOk, format ["before=%1|after=%2|report=%3|audit=%4", _invalid # 0, _invalid # 1, _invalidReport, _invalid # 4]] call _assert;

private _txIds = keys (call YFU_fnc_fabricatorTransactions);
{[YFU_FABRICATOR_TOKEN, _x, 0] call YFU_fnc_fabricatorRetire;} forEach _txIds;
{if (!isNull _x) then {deleteVehicle _x;};} forEach (_mixedObjects + _mixedContainers + [_clone, _station, _heavy, _light, _oversize]);
{deleteVehicle _x;} forEach [_storageLogic, _fabricatorLogic];
deleteGroup _group;
localNamespace setVariable ["YFU_MODULE_STORAGE_RECORDS", createHashMap];
localNamespace setVariable ["YFU_MODULE_FABRICATOR_RECORDS", createHashMap];
call YFU_fnc_rebuildModuleRegistration;
missionNamespace setVariable ["YOSHI_VIRTUAL_STORAGE", nil, true];
missionNamespace setVariable ["YOSHI_FABRICATOR", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_FIXTURE", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_GO", nil, true];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.1; (call TRIBUNAL_FAB_UI_fnc_census) isEqualTo [] || {diag_tickTime > _cleanupDeadline}};
private _keysGone = (_txIds findIf {!isNil {missionNamespace getVariable ([_x] call YFU_fnc_fabricatorResultKey)}}) < 0;
private _cleanupOk = (call TRIBUNAL_FAB_UI_fnc_census) isEqualTo []
    && {(keys (call YFU_fnc_fabricatorTransactions)) isEqualTo []}
    && {_keysGone} && {isNil "YOSHI_FABRICATOR"} && {isNil "YOSHI_VIRTUAL_STORAGE"};
["fabricator.ui.cleanup", _cleanupOk, format ["census=%1|tx=%2|keysGone=%3|stationGone=%4", call TRIBUNAL_FAB_UI_fnc_census, keys (call YFU_fnc_fabricatorTransactions), _keysGone, isNull _station]] call _assert;
missionNamespace setVariable ["YFU_fabricatorAudit", nil, false];
missionNamespace setVariable ["TRIBUNAL_FAB_UI_SERVER_DONE", _token, true];
""",
    client_expected_by_identity={"client-a": CLIENT_EXPECTED},
    client_sqf=CLIENT_SQF,
    client_sqf_by_identity={"client-a": CLIENT_SQF},
    metadata={
        "product": "field-utilities",
        "feature": "fabricator-ui",
        "respawn_on_start": "0",
        "observer_identities": "client-a",
        "future_client_isolation": "client-B/JIP must observe the published catalogue without receiving client-a selection or queue state",
    },
    evidence_contract=EVIDENCE_CONTRACT,
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A player opening a registered Fabricator sees the exact virtual-storage catalogue, can inspect exact nested cargo, and can build an ordered quantity queue through the live controls. The live submit control sends a one-item queue to direct delivery and an exact heavy-plus-light queue to a server-authoritative packed delivery whose two heterogeneous attached clones preserve source cargo. With the same one-item queue in airdrop mode, malformed grid text is rejected locally before request identity, queue, overlay, server audit or mission census changes.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The shipped dialog is reachable from the registered Fabricator action and already implements the intended browsing, queue, packing-request and grid-validation policy. The permanent scenario observes the real controls and exact backing identities, uses their shipped button handlers, proves the exact heterogeneous manifest through independent server-side attachment/type/cargo observations, pairs accepted normal submit with malformed-grid rejection, and excludes unrelated placement physics and cosmetic progress timing.",
        dependencies=(
            "Arma display and listbox controls",
            "Arma editor module logic synchronization",
            "one independently authenticated client",
        ),
        evidence_types=frozenset({
            "real-dialog", "catalogue-identity", "displayed-text", "displayed-picture",
            "nested-cargo", "dynamic-controls", "ordered-queue", "mixed-class-manifest",
            "attached-identity", "cargo-fidelity", "server-authority", "request-identity",
            "negative-control", "mission-wide-census", "audit", "cleanup",
        }),
        locality_requirements="Client-a owns the dialog, selection, queue and grid validation. The dedicated server owns module registration, catalogue templates and fabricated delivery. The malformed grid arm must remain entirely client-local and is checked against server audit and census. Client-B/JIP remains outside this one-client proof.",
    ),
)
