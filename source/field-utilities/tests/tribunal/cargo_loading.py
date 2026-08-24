"""Server-authoritative nearby supply-loading coverage for Field Utilities."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_SQF = r'''
localNamespace setVariable ["YFU_CARGO_LOAD_REQUESTS", createHashMap];
localNamespace setVariable ["YFU_CARGO_LOAD_AUDIT", []];

private _scenarioPlayer = objNull;
private _playerDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.05;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _playerDeadline}
};
private _origin = [2050,5650,0];
private _spawn = {
    params ["_class", "_offset"];
    private _object = createVehicle [_class, _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setVehiclePosition [_origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _object setDir 0;
    _object setFuel 0;
    _object setVelocity [0,0,0];
    _object setAngularVelocity [0,0,0];
    _object
};
private _supply = ["B_supplyCrate_F", [0,0,0]] call _spawn;
private _carrier = ["B_T_VTOL_01_vehicle_F", [5,0,0]] call _spawn;
private _rangeSupply = ["B_supplyCrate_F", [0,4,0]] call _spawn;
private _wrongSupply = ["Land_HelipadEmpty_F", [2,4,0]] call _spawn;
private _unrelated = ["B_supplyCrate_F", [-5,0,0]] call _spawn;
private _objects = [_supply, _carrier, _rangeSupply, _wrongSupply, _unrelated];
private _ids = _objects apply {netId _x};
private _capacityDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.05;
    private _capacity = _carrier canVehicleCargo _supply;
    ((_capacity param [0, false]) && {_capacity param [1, false]}) || {diag_tickTime > _capacityDeadline}
};
private _capacity = _carrier canVehicleCargo _supply;
private _fixtureOk = !isNull _scenarioPlayer
    && {(_objects findIf {isNull _x || {!local _x} || {(netId _x) isEqualTo ""}}) < 0}
    && {(_capacity param [0, false]) && {_capacity param [1, false]}}
    && {[_supply] call YFU_fnc_cargoLoadSupplyEligible}
    && {!([_wrongSupply] call YFU_fnc_cargoLoadSupplyEligible)}
    && {isNull isVehicleCargo _supply}
    && {isNull attachedTo _supply};
["field.cargo.fixture", _fixtureOk, format ["ids=%1|classes=%2|capacity=%3|locality=%4", _ids, _objects apply {typeOf _x}, _capacity, _objects apply {[local _x,owner _x]}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_CARGO_SETUP", [_token, _ids], true];

private _doneDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_FIELD_CARGO_DONE", ""]) isEqualTo _token
        || {diag_tickTime > _doneDeadline}
};
private _clientDone = (missionNamespace getVariable ["TRIBUNAL_FIELD_CARGO_DONE", ""]) isEqualTo _token;
private _audit = localNamespace getVariable ["YFU_CARGO_LOAD_AUDIT", []];
private _loadOp = missionNamespace getVariable ["TRIBUNAL_FIELD_CARGO_LOAD_OP", ""];
private _acceptedRows = _audit select {(_x # 0) isEqualTo _loadOp && {(_x # 1)} && {(_x # 2) isEqualTo "accepted"}};
private _authorityOk = (count _acceptedRows) isEqualTo 1
    && {(isVehicleCargo _supply) isEqualTo _carrier}
    && {(_acceptedRows # 0) # 3 isEqualTo owner _scenarioPlayer}
    && {(_acceptedRows # 0) # 4 isEqualTo netId _supply}
    && {(_acceptedRows # 0) # 5 isEqualTo netId _carrier}
    && {(_acceptedRows # 0) # 6}
    && {(_acceptedRows # 0) # 7};
["field.cargo.authority", _authorityOk, format ["audit=%1|membership=%2|attached=%3|owners=%4", _audit, netId (isVehicleCargo _supply), netId (attachedTo _supply), _objects apply {owner _x}]] call _assert;

private _reasonFor = {
    params ["_operationId", "_reason"];
    (_audit findIf {(_x # 0) isEqualTo _operationId && {!(_x # 1)} && {(_x # 2) isEqualTo _reason}}) >= 0
};
private _negativeOk = [_loadOp, "duplicate"] call _reasonFor
    && {[format ["%1-range", _token], "requester-range"] call _reasonFor}
    && {[format ["%1-wrong", _token], "supply"] call _reasonFor};
["field.cargo.negatives", _negativeOk, format ["audit=%1", _audit]] call _assert;

private _noCollateral = isNull (isVehicleCargo _rangeSupply)
    && {isNull (isVehicleCargo _wrongSupply)}
    && {isNull (isVehicleCargo _unrelated)}
    && {isNull attachedTo _rangeSupply}
    && {isNull attachedTo _wrongSupply}
    && {isNull attachedTo _unrelated};
["field.cargo.noCollateral", _noCollateral, format ["cargo=%1|attached=%2", [_rangeSupply,_wrongSupply,_unrelated] apply {netId (isVehicleCargo _x)}, [_rangeSupply,_wrongSupply,_unrelated] apply {netId (attachedTo _x)}]] call _assert;

private _unloaded = objNull setVehicleCargo _supply;
private _unloadDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; isNull (isVehicleCargo _supply) || {diag_tickTime > _unloadDeadline}};

// Matched physical-contact A/B. Both server-owned crates fall onto identical
// parked trucks. The treatment retains the product contact handler; the control
// removes it before an observer-only handler is installed.
private _contactOrigin = _origin vectorAdd [0, 30, 0];
private _treatmentCarrier = ["B_Truck_01_transport_F", [0,30,0]] call _spawn;
private _controlCarrier = ["B_Truck_01_transport_F", [25,30,0]] call _spawn;
{
    _x enableSimulationGlobal false;
    _x setDamage 0;
    _x engineOn false;
} forEach [_treatmentCarrier, _controlCarrier];
private _treatmentCrate = createVehicle ["B_supplyCrate_F", _contactOrigin vectorAdd [0, 0, 8], [], 0, "CAN_COLLIDE"];
private _controlCrate = createVehicle ["B_supplyCrate_F", _contactOrigin vectorAdd [25, 0, 8], [], 0, "CAN_COLLIDE"];
{_x enableSimulationGlobal false;} forEach [_treatmentCrate, _controlCrate];
uiSleep 0.5;
_controlCrate removeAllEventHandlers "EpeContactStart";
{
    _x setVariable ["TRIBUNAL_FIELD_CONTACT", [], false];
    _x addEventHandler ["EpeContactStart", {
        params ["_object1", "_object2", "_selection1", "_selection2", "_force", "_reactForce", "_worldPos"];
        if ((_object1 getVariable ["TRIBUNAL_FIELD_CONTACT", []]) isEqualTo []) then {
            _object1 setVariable ["TRIBUNAL_FIELD_CONTACT", [netId _object2, _force, _reactForce, _worldPos, local _object1, local _object2], true];
        };
    }];
} forEach [_treatmentCrate, _controlCrate];
private _placeAbove = {
    params ["_crate", "_carrier"];
    private _top = ((boundingBoxReal _carrier # 1) # 2) + 2;
    _crate setPosATL (_carrier modelToWorld [0, 0, _top]);
    _crate setVelocity [0,0,-0.5];
};
[_treatmentCrate, _treatmentCarrier] call _placeAbove;
[_controlCrate, _controlCarrier] call _placeAbove;
private _contactObjects = [_treatmentCrate, _treatmentCarrier, _controlCrate, _controlCarrier];
private _contactIds = _contactObjects apply {netId _x};
{_x setDamage 0;} forEach [_treatmentCarrier, _controlCarrier];
private _baselinePositions = [_treatmentCarrier, _controlCarrier] apply {getPosASL _x};
private _baselineDamage = [damage _treatmentCarrier, damage _controlCarrier];
{_x enableSimulationGlobal true;} forEach [_treatmentCarrier, _controlCarrier, _treatmentCrate, _controlCrate];
missionNamespace setVariable ["TRIBUNAL_FIELD_CONTACT_SETUP", [_token, _contactIds], true];

private _contactDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.02;
    !((_treatmentCrate getVariable ["TRIBUNAL_FIELD_CONTACT", []]) isEqualTo [])
        && {!((_controlCrate getVariable ["TRIBUNAL_FIELD_CONTACT", []]) isEqualTo [])}
        || {diag_tickTime > _contactDeadline}
};
private _treatmentContact = _treatmentCrate getVariable ["TRIBUNAL_FIELD_CONTACT", []];
private _controlContact = _controlCrate getVariable ["TRIBUNAL_FIELD_CONTACT", []];
private _stimulusOk = !(_treatmentContact isEqualTo []) && {!(_controlContact isEqualTo [])}
    && {(_treatmentContact # 0) isEqualTo netId _treatmentCarrier}
    && {(_controlContact # 0) isEqualTo netId _controlCarrier};
["field.contact.stimulus", _stimulusOk, format ["treatment=%1|control=%2|ids=%3", _treatmentContact, _controlContact, _contactIds]] call _assert;

private _attachDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.02; (attachedTo _treatmentCrate) isEqualTo _treatmentCarrier || {diag_tickTime > _attachDeadline}};
private _maxSpeed = [0,0]; private _minUp = [1,1];
private _sampleDeadline = diag_tickTime + 4;
waitUntil {
    uiSleep 0.02;
    {
        _maxSpeed set [_forEachIndex, (_maxSpeed # _forEachIndex) max vectorMagnitude (velocity _x)];
        _minUp set [_forEachIndex, (_minUp # _forEachIndex) min ((vectorUp _x) # 2)];
    } forEach [_treatmentCarrier, _controlCarrier];
    diag_tickTime > _sampleDeadline
};
private _displacements = [
    (getPosASL _treatmentCarrier) distance (_baselinePositions # 0),
    (getPosASL _controlCarrier) distance (_baselinePositions # 1)
];
private _attachmentOk = (attachedTo _treatmentCrate) isEqualTo _treatmentCarrier && {isNull attachedTo _controlCrate};
["field.contact.attachment", _attachmentOk, format ["treatment=%1|control=%2|cratePos=%3|carrierPos=%4", netId (attachedTo _treatmentCrate), netId (attachedTo _controlCrate), getPosASL _treatmentCrate, getPosASL _treatmentCarrier]] call _assert;
private _damage = [damage _treatmentCarrier, damage _controlCarrier];
private _damageDelta = [(_damage # 0) - (_baselineDamage # 0), (_damage # 1) - (_baselineDamage # 1)];
private _stabilityOk = (_maxSpeed # 0) <= ((_maxSpeed # 1) + 1)
    && {(_minUp # 0) >= ((_minUp # 1) - 0.1)}
    && {(_displacements # 0) <= ((_displacements # 1) + 1)}
    && {(_damageDelta # 0) <= ((_damageDelta # 1) + 0.05)};
["field.contact.carrierStable", _stabilityOk, format ["maxSpeed=%1|minUp=%2|displacement=%3|baselineDamage=%4|damage=%5|delta=%6", _maxSpeed, _minUp, _displacements, _baselineDamage, _damage, _damageDelta]] call _assert;

private _contactClientDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_FIELD_CONTACT_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _contactClientDeadline}};
private _contactClientDone = (missionNamespace getVariable ["TRIBUNAL_FIELD_CONTACT_CLIENT_DONE", ""]) isEqualTo _token;
_treatmentCrate enableSimulationGlobal false;
_treatmentCrate removeAllEventHandlers "EpeContactStart";
detach _treatmentCrate;
_treatmentCrate setPosATL (_contactOrigin vectorAdd [0, -20, 1]);
uiSleep 0.1;
private _detached = isNull attachedTo _treatmentCrate;
{deleteVehicle _x;} forEach _contactObjects;
private _contactCleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_contactIds findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _contactCleanupDeadline}};
private _contactCleanupOk = _contactClientDone && {_detached} && {(_contactIds findIf {!isNull objectFromNetId _x}) < 0};
["field.contact.cleanup", _contactCleanupOk, format ["clientDone=%1|detached=%2|remaining=%3", _contactClientDone, _detached, _contactIds select {!isNull objectFromNetId _x}]] call _assert;

{deleteVehicle _x;} forEach _objects;
missionNamespace setVariable ["TRIBUNAL_FIELD_CARGO_SETUP", nil, true];
missionNamespace setVariable ["TRIBUNAL_FIELD_CARGO_DONE", nil, true];
missionNamespace setVariable ["TRIBUNAL_FIELD_CONTACT_SETUP", nil, true];
missionNamespace setVariable ["TRIBUNAL_FIELD_CONTACT_CLIENT_DONE", nil, true];
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_ids findIf {!isNull objectFromNetId _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
private _cleanupOk = _clientDone && {_unloaded} && {(_ids findIf {!isNull objectFromNetId _x}) < 0}
    && {(localNamespace getVariable ["YFU_CARGO_LOAD_REQUESTS", createHashMap]) isEqualType createHashMap};
["field.cargo.cleanup", _cleanupOk, format ["clientDone=%1|unloaded=%2|remaining=%3|requests=%4", _clientDone, _unloaded, _ids select {!isNull objectFromNetId _x}, count (localNamespace getVariable ["YFU_CARGO_LOAD_REQUESTS", createHashMap])]] call _assert;
'''

CLIENT_SQF = r'''
uiNamespace setVariable ["YFU_CARGO_LOAD_RESULTS", []];
private _setup = [];
private _setupDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    _setup = missionNamespace getVariable ["TRIBUNAL_FIELD_CARGO_SETUP", []];
    (count _setup) isEqualTo 2 || {diag_tickTime > _setupDeadline}
};
private _ids = _setup param [1, []];
private _objects = [];
private _objectsDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    _objects = _ids apply {objectFromNetId _x};
    (count _objects) isEqualTo 5 && {(_objects findIf {isNull _x}) < 0}
        || {diag_tickTime > _objectsDeadline}
};
private _supply = _objects param [0, objNull];
private _carrier = _objects param [1, objNull];
private _rangeSupply = _objects param [2, objNull];
private _wrongSupply = _objects param [3, objNull];
private _unrelated = _objects param [4, objNull];
player setPosATL ((getPosATL _supply) vectorAdd [0,-3,0]);
player setVelocity [0,0,0];
uiSleep 1;

private _findAction = {
    params ["_nodes", "_wanted"];
    private _found = [];
    {
        _x params ["_data", "_children"];
        if ((_data param [0, ""]) isEqualTo _wanted) exitWith {_found = _data};
        private _child = [_children, _wanted] call _findAction;
        if (_child isNotEqualTo []) exitWith {_found = _child};
    } forEach _nodes;
    _found
};
[_supply] call ace_interact_menu_fnc_compileMenu;
private _class = typeOf _supply call ace_common_fnc_getConfigName;
private _root = [ace_interact_menu_ActNamespace getOrDefault [_class, []], "logiActions"] call _findAction;
private _children = [_supply, player, []] call YOSHI_getSuppliesAction;
private _wanted = format ["loadSupplies-%1", netId _carrier];
private _rows = _children select {(((_x param [0, []]) param [0, ""]) isEqualTo _wanted)};
private _action = if (_rows isEqualTo []) then {[]} else {(_rows # 0) # 0};
private _args = _action param [6, objNull];
private _condition = _action param [4, {false}];
private _relevant = if (_action isEqualTo []) then {false} else {[_supply, player, _args] call _condition};
private _actionOk = _root isNotEqualTo [] && {(count _rows) isEqualTo 1}
    && {_args isEqualTo _carrier} && {_relevant}
    && {!local _supply} && {!local _carrier};
["field.cargo.clientAction", _actionOk, format ["root=%1|children=%2|action=%3|arg=%4|relevant=%5|locality=%6", _root param [0,""], _children apply {(_x # 0) param [0,""]}, _action param [0,""], netId _args, _relevant, [_supply,_carrier] apply {[local _x,owner _x]}]] call _assert;

private _waitResult = {
    params ["_operationId", ["_timeout", 15]];
    private _row = []; private _deadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.05;
        private _matches = (uiNamespace getVariable ["YFU_CARGO_LOAD_RESULTS", []]) select {(_x # 0) isEqualTo _operationId};
        if (_matches isNotEqualTo []) then {_row = _matches # ((count _matches) - 1);};
        _row isNotEqualTo [] || {diag_tickTime > _deadline}
    };
    _row
};
private _statement = _action param [3, {}];
[_supply, player, _args] call _statement;
private _generatedRows = [];
private _receiptDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    _generatedRows = uiNamespace getVariable ["YFU_CARGO_LOAD_RESULTS", []];
    _generatedRows isNotEqualTo [] || {diag_tickTime > _receiptDeadline}
};
private _loadResult = _generatedRows param [0, []];
private _loadOp = _loadResult param [0, ""];
missionNamespace setVariable ["TRIBUNAL_FIELD_CARGO_LOAD_OP", _loadOp, true];
private _receiptOk = (_loadResult param [1, false]) && {(_loadResult param [2, ""]) isEqualTo "accepted"}
    && {(_loadResult param [3, ""]) isEqualTo netId _supply}
    && {(_loadResult param [4, ""]) isEqualTo netId _carrier}
    && {(_loadResult param [5, -1]) isEqualTo clientOwner};
["field.cargo.clientReceipt", _receiptOk, format ["rows=%1|receipt=%2|owner=%3", _generatedRows, _loadResult, clientOwner]] call _assert;
private _replicaDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (isVehicleCargo _supply) isEqualTo _carrier || {diag_tickTime > _replicaDeadline}};
private _replicaOk = (isVehicleCargo _supply) isEqualTo _carrier
    && {isNull isVehicleCargo _unrelated};
["field.cargo.clientReplica", _replicaOk, format ["cargo=%1|carrier=%2|attached=%3|unrelated=%4", netId (isVehicleCargo _supply), netId _carrier, netId (attachedTo _supply), netId (isVehicleCargo _unrelated)]] call _assert;

uiNamespace setVariable ["YFU_CARGO_LOAD_RESULTS", (uiNamespace getVariable ["YFU_CARGO_LOAD_RESULTS", []]) select {!((_x # 0) isEqualTo _loadOp)}];
[_supply, _carrier, _loadOp] call YFU_fnc_cargoRequestLoad;
private _duplicate = [_loadOp] call _waitResult;
private _nearASL = getPosASL player;
player setPosASL (_nearASL vectorAdd [40,0,0]);
uiSleep 0.5;
private _rangeOp = format ["%1-range", _token];
[_rangeSupply, _carrier, _rangeOp] call YFU_fnc_cargoRequestLoad;
private _rangeResult = [_rangeOp] call _waitResult;
player setPosASL _nearASL;
uiSleep 0.2;
private _wrongOp = format ["%1-wrong", _token];
[_wrongSupply, _carrier, _wrongOp] call YFU_fnc_cargoRequestLoad;
private _wrongResult = [_wrongOp] call _waitResult;
private _negativeOk = !(_duplicate param [1, true]) && {(_duplicate param [2, ""]) isEqualTo "duplicate"}
    && {!(_rangeResult param [1, true])} && {(_rangeResult param [2, ""]) isEqualTo "requester-range"}
    && {!(_wrongResult param [1, true])} && {(_wrongResult param [2, ""]) isEqualTo "supply"}
    && {isNull isVehicleCargo _rangeSupply} && {isNull isVehicleCargo _wrongSupply};
["field.cargo.clientNegatives", _negativeOk, format ["duplicate=%1|range=%2|wrong=%3|stimulus=%4", _duplicate, _rangeResult, _wrongResult, [player distance _rangeSupply, typeOf _wrongSupply]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_CARGO_DONE", _token, true];

private _contactSetup = [];
private _contactSetupDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; _contactSetup = missionNamespace getVariable ["TRIBUNAL_FIELD_CONTACT_SETUP", []]; (count _contactSetup) isEqualTo 2 || {diag_tickTime > _contactSetupDeadline}};
private _contactIds = _contactSetup param [1, []];
private _contactObjects = [];
private _contactObjectsDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05; _contactObjects = _contactIds apply {objectFromNetId _x};
    (count _contactObjects) isEqualTo 4 && {(_contactObjects findIf {isNull _x}) < 0} || {diag_tickTime > _contactObjectsDeadline}
};
private _treatmentCrate = _contactObjects param [0, objNull];
private _treatmentCarrier = _contactObjects param [1, objNull];
private _controlCrate = _contactObjects param [2, objNull];
private _controlCarrier = _contactObjects param [3, objNull];
private _contactReplicaDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.02; (attachedTo _treatmentCrate) isEqualTo _treatmentCarrier || {diag_tickTime > _contactReplicaDeadline}};
private _contactReplicaOk = !isNull _treatmentCrate && {!isNull _treatmentCarrier}
    && {(attachedTo _treatmentCrate) isEqualTo _treatmentCarrier} && {isNull attachedTo _controlCrate}
    && {!local _treatmentCrate} && {!local _treatmentCarrier} && {!local _controlCrate} && {!local _controlCarrier};
["field.contact.clientReplica", _contactReplicaOk, format ["ids=%1|treatment=%2|control=%3|locality=%4", _contactIds, netId (attachedTo _treatmentCrate), netId (attachedTo _controlCrate), _contactObjects apply {[local _x, owner _x]}]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_CONTACT_CLIENT_DONE", _token, true];
'''

BASELINE = ["field.cargo.fixture", "field.cargo.noCollateral"]
TREATMENT = [
    "field.cargo.clientAction", "field.cargo.clientReceipt",
    "field.cargo.authority", "field.cargo.clientReplica",
]
NEGATIVES = ["field.cargo.clientNegatives", "field.cargo.negatives"]
CLEANUP = ["field.cargo.cleanup"]
CONTACT_BASELINE = ["field.contact.stimulus"]
CONTACT_TREATMENT = ["field.contact.attachment", "field.contact.carrierStable", "field.contact.clientReplica"]
CONTACT_CLEANUP = ["field.contact.cleanup"]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "fieldutils-cargo-loading",
        "version": 2,
        "feature_family": "pontifex-field-utilities-cargo-loading",
        "name": "Field Utilities authoritative nearby supply loading",
        "definition": {
            "kind": "controlled multiplayer specification",
            "reference": "source/field-utilities/tests/tribunal/cargo_loading.py",
            "applicability": "Arma 3 dedicated multiplayer with one authenticated client and server-owned supply/carrier fixtures; contact coverage is bounded to B_supplyCrate_F on B_Truck_01_transport_F",
            "participants": {
                "server": "request authority, native cargo mutation, exact membership oracle, and cleanup",
                "client-a": "registered ACE child observer, authenticated requester, receipt and replication observer",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:cargo-loading",
        "label": "Field Utilities nearby supply loading",
        "kind": "product_behavior",
        "aliases": ["Field cargo loading", "Load Into"],
        "biki_context": ["biki-page:18230", "biki-page:18231"],
    },
    "arms": [
        {"key": "baseline", "role": "baseline", "description": "Eligible exact pair and unrelated objects begin unloaded and unattached", "assertions": BASELINE},
        {"key": "load", "role": "treatment", "description": "The real registered ACE child produces one authenticated exact load and replicated membership", "assertions": TREATMENT},
        {"key": "invalid", "role": "negative_control", "description": "Delivered replay, distant-requester, and wrong-supply requests fail without collateral loading", "assertions": NEGATIVES},
        {"key": "cleanup", "role": "treatment", "description": "The exact loaded object unloads and every fixture identity is deleted", "assertions": CLEANUP},
        {"key": "contact-stimulus", "role": "baseline", "description": "Matched server-owned crates make exact physical contact with identical parked trucks", "assertions": CONTACT_BASELINE},
        {"key": "contact-treatment", "role": "treatment", "description": "Only the crate retaining the product handler attaches; exact identity replicates without carrier instability relative to control", "assertions": CONTACT_TREATMENT},
        {"key": "contact-cleanup", "role": "treatment", "description": "Controlled teardown removes the contact handler, detaches the crate, and deletes every fixture identity", "assertions": CONTACT_CLEANUP},
    ],
    "causal_relationships": [
        {"key": "accepted-v-invalid", "relation": "CAUSAL_PAIR_WITH", "source": "load", "target": "invalid", "controlled_dimensions": ["request endpoint", "requesting client", "carrier identity", "mission"]},
        {"key": "contact-handler-v-control", "relation": "CAUSAL_PAIR_WITH", "source": "contact-treatment", "target": "contact-stimulus", "controlled_dimensions": ["crate class", "truck class", "server locality", "drop geometry", "mission"]}
    ],
    "propositions": [
        {
            "id": "pontifex:field-utilities:cargo-loading-authority",
            "text": "A nearby authenticated player can invoke the exact registered Field Utilities action to load one eligible supply into one eligible server-owned carrier with an exact requester-only receipt and replicated membership; replay, range, and class failures change nothing else.",
            "intended_use": "primary_result",
            "assertions": BASELINE + TREATMENT + NEGATIVES + CLEANUP,
            "rationale": "The registered child statement, authenticated owner, literal command result, server/client exact membership, delivered negative receipts, unrelated controls, and cleanup close the principal false-PASS paths.",
        },
        {
            "id": "pontifex:field-utilities:contact-attachment",
            "text": "For a server-owned B_supplyCrate_F physically contacting a server-owned B_Truck_01_transport_F, the Field Utilities contact hook attaches the exact crate to the exact truck, replicates that identity to client-a, and adds no carrier instability over a matched handler-free control.",
            "intended_use": "primary_result",
            "assertions": CONTACT_BASELINE + CONTACT_TREATMENT + CONTACT_CLEANUP,
            "rationale": "Both arms record exact contact identity and similar forces; treatment alone retains the product handler. Exact attachment, owner/locality, carrier motion/orientation/damage deltas, remote replication, controlled detach, and deletion exclude no-contact, control-attachment, final-damage, and leaked-fixture false passes.",
        }
    ],
    "unresolved": [
        "Client-owned cargo/carriers, ownership migration, client-B/JIP, full-carrier breadth, unload UX, other contact object/surface classes, repeated contacts, and deletion while still attached remain outside this proof."
    ],
}

TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-cargo-loading",
    tier="gameplay",
    server_expected=frozenset({
        "field.cargo.fixture", "field.cargo.authority", "field.cargo.negatives",
        "field.cargo.noCollateral", "field.cargo.cleanup",
        "field.contact.stimulus", "field.contact.attachment",
        "field.contact.carrierStable", "field.contact.cleanup",
    }),
    client_expected=frozenset({
        "field.cargo.clientAction", "field.cargo.clientReceipt",
        "field.cargo.clientReplica", "field.cargo.clientNegatives",
        "field.contact.clientReplica",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "field-utilities", "feature": "nearby-supply-loading"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A nearby authenticated player can invoke the exact registered action to load one eligible supply into one eligible server-owned carrier. Separately, a server-owned B_supplyCrate_F physically contacting a server-owned B_Truck_01_transport_F attaches to that exact truck, replicates to client-a and remains stable relative to a matched handler-free control.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The authoritative explicit-load refinement remains covered. A matched physical contact A/B now isolates the existing handler: both arms contact identical trucks, treatment alone attaches, carrier state is compared from independent baselines, client-a resolves exact attachment identity, and controlled teardown proves no leaked fixtures.",
        dependencies=("ACE 3.21 registered interaction tree", "native vehicle-in-vehicle cargo", "Arma EpeContactStart and attachTo", "one authenticated client"),
        evidence_types=frozenset({"ace-action-data", "exact-identity", "authoritative-state", "native-command-result", "physical-stimulus", "causal-pair", "replication", "negative-control", "cleanup"}),
        locality_requirements="The server owns all fixture objects, cargo mutation, contact handlers, and attachment; client-a owns action resolution and authenticated requests and observes replication. Client-owned objects, migration, and client-B/JIP are unclaimed.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)
