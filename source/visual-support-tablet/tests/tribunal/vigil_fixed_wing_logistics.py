"""Physical Tier 3 contract for Vigil fixed-wing logistics delivery."""

from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.mission.delivery import delivery_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-fixed-wing-logistics",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.logistics.registration",
        "vigil.logistics.reconstructed",
        "vigil.logistics.request.accepted",
        "vigil.logistics.control.duplicateRejected",
        "vigil.logistics.ingress",
        "vigil.logistics.release",
        "vigil.logistics.parachute",
        "vigil.logistics.descent",
        "vigil.logistics.landing",
        "vigil.logistics.accuracy",
        "vigil.logistics.survival",
        "vigil.logistics.manifest",
        "vigil.logistics.locality",
        "vigil.logistics.egress",
        "vigil.logistics.cleanup",
    }),
    client_expected=frozenset({
        "vigil.logistics.client.ui",
        "vigil.logistics.client.emptyRejected",
        "vigil.logistics.client.manifest",
        "vigil.logistics.client.request",
        "vigil.logistics.client.replication",
        "vigil.logistics.client.inventory",
        "vigil.logistics.client.locality",
        "vigil.logistics.client.egress",
    }),
    server_sqf=aviation_observer_sqf() + delivery_observer_sqf() + r'''
private _assetId = format ["FW_LOGISTICS_%1", _token];
private _scenarioPlayer = allPlayers param [0, objNull];
private _operating = if (isNull _scenarioPlayer) then {[2000, 5600, 0]} else {getPosATL _scenarioPlayer};
private _targetATL = [(_operating # 0) + 2200, _operating # 1, 0];
private _infil = [500, _operating # 1, 900];
private _exfil = [500, 1000, 900];
missionNamespace setVariable ["YSF_FW_LOGISTICS_EVENTS", [], false];
setWind [0, 0, true];

private _source = "B_T_VTOL_01_vehicle_F" createVehicle [1500, 5400, 0];
_source setDir 90;
_source setFuel 0.82;
createVehicleCrew _source;
{_x setSkill 1} forEach crew _source;
_source setVariable ["YSF_FW_ID", _assetId, true];
private _registered = [_source, _infil, _exfil, "LIFTER"] call YSF_fwRegisterAsset;
private _registrationDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; isNull _source || {diag_tickTime > _registrationDeadline}};
private _entry = [_assetId] call YSF_fwGetEntry;
private _roleMask = _entry getOrDefault ["roleMask", 0];
private _isLogistics = (((floor (_roleMask / YSF_FW_ROLE_LOGI)) mod 2) isEqualTo 1);
private _registrationOk = _registered && {isNull _source} && {_isLogistics}
    && {(_entry getOrDefault ["vehicleType", ""]) isEqualTo "B_T_VTOL_01_vehicle_F"};
["vigil.logistics.registration", _registrationOk, format ["asset=%1|registered=%2|sourceNull=%3|class=%4|role=%5", _assetId, _registered, isNull _source, _entry getOrDefault ["vehicleType", ""], _roleMask]] call _assert;

private _templatePosition = _operating vectorAdd [30, 20, 0];
private _template = createVehicle ["Box_NATO_Ammo_F", _templatePosition, [], 0, "NONE"];
clearWeaponCargoGlobal _template;
clearMagazineCargoGlobal _template;
clearItemCargoGlobal _template;
clearBackpackCargoGlobal _template;
_template addWeaponCargoGlobal ["arifle_MX_F", 1];
_template addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 4];
_template addItemCargoGlobal ["FirstAidKit", 2];
_template addBackpackCargoGlobal ["B_AssaultPack_khk", 1];
_template allowDamage false;
private _requestedRows = [_template] call TRIBUNAL_fnc_inventoryTree;
private _requestedPayload = [_requestedRows] call TRIBUNAL_fnc_inventoryPayload;
missionNamespace setVariable ["TRIBUNAL_LOGISTICS_FIXTURE", [_token, _assetId, netId _template, _targetATL, _exfil, _requestedPayload], true];

private _deployDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.1;
    _entry = [_assetId] call YSF_fwGetEntry;
    !isNull (_entry getOrDefault ["spawnedVeh", objNull]) || {diag_tickTime > _deployDeadline}
};
private _aircraft = _entry getOrDefault ["spawnedVeh", objNull];
private _pilot = if (isNull _aircraft) then {objNull} else {driver _aircraft};
private _reconstructed = !isNull _aircraft && {alive _aircraft}
    && {typeOf _aircraft isEqualTo "B_T_VTOL_01_vehicle_F"}
    && {count crew _aircraft > 0};
["vigil.logistics.reconstructed", _reconstructed, format ["aircraft=%1|class=%2|crew=%3|fuel=%4|role=%5", if (isNull _aircraft) then {""} else {netId _aircraft}, if (isNull _aircraft) then {""} else {typeOf _aircraft}, if (isNull _aircraft) then {0} else {count crew _aircraft}, if (isNull _aircraft) then {-1} else {fuel _aircraft}, _roleMask]] call _assert;

private _acceptedDeadline = diag_tickTime + 90;
private _accepted = [];
waitUntil {
    uiSleep 0.1;
    private _events = missionNamespace getVariable ["YSF_FW_LOGISTICS_EVENTS", []];
    private _index = _events findIf {(_x param [1, ""]) isEqualTo "accepted"};
    if (_index >= 0) then {_accepted = _events # _index};
    _accepted isNotEqualTo [] || {diag_tickTime > _acceptedDeadline}
};
private _taskId = _accepted param [0, ""];
private _acceptedOk = _taskId isNotEqualTo ""
    && {(_accepted param [2, ""]) isEqualTo _assetId}
    && {(_accepted param [3, ""]) isEqualTo netId _aircraft}
    && {(_accepted param [5, []]) distance2D _targetATL < 1};
["vigil.logistics.request.accepted", _acceptedOk, format ["event=%1", _accepted]] call _assert;

private _duplicateDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_LOGISTICS_DUPLICATE"} || {diag_tickTime > _duplicateDeadline}};
private _duplicate = missionNamespace getVariable ["TRIBUNAL_LOGISTICS_DUPLICATE", []];
private _duplicateOk = (_duplicate param [0, ""]) isEqualTo _token
    && {(_duplicate param [1, true]) isEqualTo false}
    && {(_duplicate param [2, ""]) isEqualTo "duplicate_active_task"};
["vigil.logistics.control.duplicateRejected", _duplicateOk, format ["control=%1", _duplicate]] call _assert;

private _releaseDeadline = diag_tickTime + 210;
private _released = [];
waitUntil {
    uiSleep 0.1;
    private _events = missionNamespace getVariable ["YSF_FW_LOGISTICS_EVENTS", []];
    private _index = _events findIf {(_x param [0, ""]) isEqualTo _taskId && {(_x param [1, ""]) isEqualTo "released"}};
    if (_index >= 0) then {_released = _events # _index};
    _released isNotEqualTo [] || {diag_tickTime > _releaseDeadline}
};
private _containerIds = _released param [4, []];
private _containerId = _containerIds param [0, ""];
private _container = if (_containerId isEqualTo "") then {objNull} else {objectFromNetId _containerId};
private _releaseDetails = _released param [6, []];
private _releaseRows = _releaseDetails param [0, []];
private _ingressSamples = _releaseDetails param [1, []];
private _ingressStartDistance = if (_ingressSamples isEqualTo []) then {-1} else {(_ingressSamples # 0) # 4};
private _ingressMinimum = 1e9;
{_ingressMinimum = _ingressMinimum min (_x # 4)} forEach _ingressSamples;
private _ingressOk = count _ingressSamples > 5 && {_ingressStartDistance > 1000} && {_ingressMinimum <= YSF_FW_LOGISTICS_RELEASE_RADIUS + 25};
["vigil.logistics.ingress", _ingressOk, format ["samples=%1|startDistance=%2|minDistance=%3|target=%4", count _ingressSamples, _ingressStartDistance, _ingressMinimum, _targetATL]] call _assert;
private _releaseOk = !isNull _container && {_containerId isNotEqualTo ""} && {count _releaseRows isEqualTo 1}
    && {((_releaseRows # 0) param [0, ""]) isEqualTo _containerId}
    && {((_releaseRows # 0) param [2, false]) isEqualTo true}
    && {((_releaseRows # 0) param [3, -1]) isEqualTo 2};
["vigil.logistics.release", _releaseOk, format ["aircraft=%1|cargo=%2|rows=%3", netId _aircraft, _containerId, _releaseRows]] call _assert;

private _resultVariable = [_taskId, 0] call YFU_airdropResultVariable;
private _deliverySamples = if (isNull _container) then {[]} else {[_container, _targetATL, _resultVariable, 180, 0.1] call TRIBUNAL_fnc_observeDelivery};
private _deliveryEvidence = [_deliverySamples, _targetATL] call TRIBUNAL_fnc_deliveryEvidence;
private _dropResult = missionNamespace getVariable [_resultVariable, []];
private _parachuteOk = (_dropResult param [3, ""]) isNotEqualTo ""
    && {count (_deliveryEvidence getOrDefault ["chuteIds", []]) isEqualTo 1}
    && {(_deliveryEvidence getOrDefault ["chuteLocalities", []]) isEqualTo [true]}
    && {(_deliveryEvidence getOrDefault ["attachedSamples", 0]) > 0};
["vigil.logistics.parachute", _parachuteOk, format ["chute=%1|chuteIds=%2|locality=%3|owners=%4|attachedSamples=%5", _dropResult param [3, ""], _deliveryEvidence getOrDefault ["chuteIds", []], _deliveryEvidence getOrDefault ["chuteLocalities", []], _deliveryEvidence getOrDefault ["chuteOwners", []], _deliveryEvidence getOrDefault ["attachedSamples", 0]]] call _assert;
private _descentOk = (_deliveryEvidence getOrDefault ["descended", false]) isEqualTo true
    && {(_deliveryEvidence getOrDefault ["samples", 0]) > 20};
["vigil.logistics.descent", _descentOk, format ["samples=%1|maxAlt=%2|minAlt=%3", _deliveryEvidence getOrDefault ["samples", 0], _deliveryEvidence getOrDefault ["maximumAltitudeATL", -1], _deliveryEvidence getOrDefault ["minimumAltitudeATL", -1]]] call _assert;
private _landingOk = (_dropResult param [1, ""]) isEqualTo "landed" && {!isNull _container};
private _dropSummary = [_dropResult param [0, ""], _dropResult param [1, ""], _dropResult param [2, ""], _dropResult param [3, ""], _dropResult param [4, []], _dropResult param [5, []], _dropResult param [6, []], _dropResult param [7, -1], _dropResult param [9, false], _dropResult param [10, -1]];
["vigil.logistics.landing", _landingOk, format ["result=%1|cargoState=%2", _dropSummary, if (isNull _container) then {"missing"} else {_container getVariable ["YFU_airdropState", ""]}]] call _assert;
private _deliveryError = if (isNull _container) then {1e9} else {_container distance2D _targetATL};
["vigil.logistics.accuracy", _deliveryError <= 100, format ["requested=%1|release=%2|landed=%3|error=%4", _targetATL, _dropResult param [4, []], if (isNull _container) then {[]} else {getPosATL _container}, _deliveryError]] call _assert;
private _survivalOk = !isNull _container && {alive _container} && {damage _container < 1} && {simulationEnabled _container};
["vigil.logistics.survival", _survivalOk, format ["cargo=%1|alive=%2|damage=%3|simulation=%4", _containerId, if (isNull _container) then {false} else {alive _container}, if (isNull _container) then {1} else {damage _container}, if (isNull _container) then {false} else {simulationEnabled _container}]] call _assert;
private _deliveredRows = if (isNull _container) then {[]} else {[_container] call TRIBUNAL_fnc_inventoryTree};
private _deliveredPayload = [_deliveredRows] call TRIBUNAL_fnc_inventoryPayload;
["vigil.logistics.manifest", _deliveredPayload isEqualTo _requestedPayload, format ["requested=%1|delivered=%2|tree=%3", _requestedPayload, _deliveredPayload, _deliveredRows]] call _assert;
private _attached = if (isNull _container) then {[]} else {attachedObjects _container};
private _localityOk = !isNull _aircraft && {local _aircraft} && {owner _aircraft isEqualTo 2}
    && {!isNull _pilot} && {local _pilot} && {owner _pilot isEqualTo 2}
    && {!isNull _container} && {local _container} && {owner _container isEqualTo 2}
    && {(_attached findIf {!local _x || {owner _x isNotEqualTo 2}}) < 0}
    && {(_dropResult param [9, false]) isEqualTo true} && {(_dropResult param [10, -1]) isEqualTo 2};
["vigil.logistics.locality", _localityOk, format ["requesterOwner=%1|aircraft=%2/%3|pilot=%4/%5|cargo=%6/%7|attached=%8|drop=%9", owner _scenarioPlayer, local _aircraft, owner _aircraft, local _pilot, owner _pilot, if (isNull _container) then {false} else {local _container}, if (isNull _container) then {-1} else {owner _container}, _attached apply {[netId _x, local _x, owner _x]}, [_dropResult param [9, false], _dropResult param [10, -1]]]] call _assert;

private _rtbStart = if (isNull _aircraft) then {[]} else {getPosATL _aircraft};
private _rtbSamples = if (isNull _aircraft) then {[]} else {[_aircraft, _exfil, {params ["_candidate"]; isNull _candidate}, 300, 0.5] call TRIBUNAL_fnc_observeFlight};
private _rtbEvidence = [_rtbSamples, _rtbStart, _exfil] call TRIBUNAL_fnc_flightEvidence;
private _rtbDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.1;
    _entry = [_assetId] call YSF_fwGetEntry;
    isNull (_entry getOrDefault ["spawnedVeh", objNull]) || {diag_tickTime > _rtbDeadline}
};
private _egressOk = isNull (_entry getOrDefault ["spawnedVeh", objNull])
    && {(_entry getOrDefault ["lastRtbResult", ""]) isEqualTo "success"}
    && {(_rtbEvidence getOrDefault ["maximumTravel", 0]) > 500};
["vigil.logistics.egress", _egressOk, format ["state=%1|result=%2|samples=%3|maxTravel=%4|minDistance=%5", _entry getOrDefault ["state", ""], _entry getOrDefault ["lastRtbResult", ""], _rtbEvidence getOrDefault ["samples", 0], _rtbEvidence getOrDefault ["maximumTravel", 0], _rtbEvidence getOrDefault ["minimumDistance", -1]]] call _assert;

private _clientEgressDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_LOGISTICS_CLIENT_EGRESS"} || {diag_tickTime > _clientEgressDeadline}};
private _clientEgress = missionNamespace getVariable ["TRIBUNAL_LOGISTICS_CLIENT_EGRESS", []];
{deleteVehicle _x} forEach _attached;
if (!isNull _container) then {deleteVehicle _container};
deleteVehicle _template;
private _deleteDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; (isNull _container && {isNull _template}) || {diag_tickTime > _deleteDeadline}};
private _registry = call YSF_fwEnsureRegistry;
_registry deleteAt _assetId;
[_registry] call YSF_fwCommitRegistry;
private _cleanupOk = (_clientEgress param [0, ""]) isEqualTo _token && {(_clientEgress param [1, false]) isEqualTo true}
    && {isNull _container} && {isNull _template} && {isNull (_entry getOrDefault ["spawnedVeh", objNull])}
    && {isNil {_registry get _assetId}};
["vigil.logistics.cleanup", _cleanupOk, format ["cargoNull=%1|templateNull=%2|aircraftNull=%3|registryHas=%4", isNull _container, isNull _template, isNull (_entry getOrDefault ["spawnedVeh", objNull]), !isNil {_registry get _assetId}]] call _assert;
''',
    client_sqf=delivery_observer_sqf() + r'''
private _fixtureDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_LOGISTICS_FIXTURE"} || {diag_tickTime > _fixtureDeadline}};
private _fixture = missionNamespace getVariable ["TRIBUNAL_LOGISTICS_FIXTURE", []];
private _assetId = _fixture param [1, ""];
private _templateId = _fixture param [2, ""];
private _targetATL = _fixture param [3, []];
private _requestedPayload = _fixture param [5, []];
private _template = if (_templateId isEqualTo "") then {objNull} else {objectFromNetId _templateId};
player linkItem "YSF_VigilTerminal_B";

private _registryDeadline = diag_tickTime + 60;
private _entry = objNull;
waitUntil {
    uiSleep 0.1;
    _entry = [_assetId] call YSF_fwGetEntry;
    typeName _entry isEqualTo "HASHMAP" || {diag_tickTime > _registryDeadline}
};
uiNamespace setVariable ["YSF_current_selected_fw_id", _assetId];
call YOSHI_taskFW_deploy;
private _aircraftDeadline = diag_tickTime + 90;
private _aircraft = objNull;
waitUntil {
    uiSleep 0.1;
    _entry = [_assetId] call YSF_fwGetEntry;
    _aircraft = _entry getOrDefault ["spawnedVeh", objNull];
    !isNull _aircraft || {diag_tickTime > _aircraftDeadline}
};
call YOSHI_taskFW_logiStub;
private _uiDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; !isNull (uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull]) || {diag_tickTime > _uiDeadline}};
private _context = call YFU_assetsGetOpenContext;
private _uiOk = !isNull (uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull])
    && {(_context getOrDefault ["isAirdrop", false]) isEqualTo true}
    && {(_context getOrDefault ["fabricator", objNull]) isEqualTo _aircraft};
["vigil.logistics.client.ui", _uiOk, format ["display=%1|aircraft=%2|context=%3", !isNull (uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull]), if (isNull _aircraft) then {""} else {netId _aircraft}, _context]] call _assert;

uiNamespace setVariable ["YFU_fabricator_queue_map", createHashMap];
uiNamespace setVariable ["YFU_fabricator_queue_order", []];
private _requestBefore = uiNamespace getVariable ["YFU_last_airdrop_request", []];
call YFU_assetsSubmitOrder;
uiSleep 0.2;
private _emptyOk = !(uiNamespace getVariable ["YFU_submit_in_progress", false])
    && {(uiNamespace getVariable ["YFU_last_airdrop_request", []]) isEqualTo _requestBefore};
["vigil.logistics.client.emptyRejected", _emptyOk, format ["before=%1|after=%2|inProgress=%3", _requestBefore, uiNamespace getVariable ["YFU_last_airdrop_request", []], uiNamespace getVariable ["YFU_submit_in_progress", false]]] call _assert;

private _grid = [_targetATL] call YFU_posToGrid;
_context set ["grid", _grid];
uiNamespace setVariable ["YFU_open_context", _context];
call YFU_assetsApplyDeliveryDefaults;
uiNamespace setVariable ["YFU_selected_fabricator_item", _template];
call YFU_assetsQueueAdd;
private _queueEntries = call YFU_assetsQueueEntries;
private _clientPayload = [];
private _manifestDeadline = diag_tickTime + 5;
waitUntil {
    _clientPayload = [[_template] call TRIBUNAL_fnc_inventoryRecord] call TRIBUNAL_fnc_inventoryPayload;
    uiSleep 0.05;
    _clientPayload isEqualTo _requestedPayload || {diag_tickTime > _manifestDeadline}
};
private _manifestOk = !isNull _template && {count _queueEntries isEqualTo 1}
    && {((_queueEntries # 0) param [1, objNull]) isEqualTo _template}
    && {_requestedPayload isNotEqualTo []};
["vigil.logistics.client.manifest", _manifestOk, format ["grid=%1|queue=%2|requested=%3|client=%4", _grid, _queueEntries apply {[_x # 0, netId (_x # 1), _x # 2]}, _requestedPayload, _clientPayload]] call _assert;

call YFU_assetsSubmitOrder;
private _requestDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.1;
    private _request = uiNamespace getVariable ["YFU_last_airdrop_request", []];
    (_request param [0, ""]) isNotEqualTo "" || {diag_tickTime > _requestDeadline}
};
private _request = uiNamespace getVariable ["YFU_last_airdrop_request", []];
private _taskId = _request param [0, ""];
private _ack = _request param [4, []];
private _requestOk = _taskId isNotEqualTo "" && {(_ack param [0, false]) isEqualTo true}
    && {(_ack param [1, ""]) isEqualTo "accepted"} && {(_ack param [2, ""]) isEqualTo _assetId};
["vigil.logistics.client.request", _requestOk, format ["task=%1|ack=%2|target=%3|containers=%4", _taskId, _ack, _targetATL, (_request param [2, []]) apply {netId _x}]] call _assert;

private _duplicateCargo = "Land_Pallet_F" createVehicle (getPosATL player vectorAdd [5, 0, 0]);
private _duplicateId = format ["%1_duplicate", _taskId];
private _duplicateAckVariable = format ["YSF_FW_LOGISTICS_ACK_%1", _duplicateId];
missionNamespace setVariable [_duplicateAckVariable, nil, false];
[netId _aircraft, [netId _duplicateCargo], _targetATL, _duplicateId, netId player] remoteExecCall ["YSF_fwRequestLogistics", 2];
private _duplicateDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable _duplicateAckVariable} || {diag_tickTime > _duplicateDeadline}};
private _duplicateAck = missionNamespace getVariable [_duplicateAckVariable, []];
missionNamespace setVariable ["TRIBUNAL_LOGISTICS_DUPLICATE", [_token, _duplicateAck param [0, true], _duplicateAck param [1, ""]], true];
deleteVehicle _duplicateCargo;

private _completeDeadline = diag_tickTime + 240;
private _event = [];
waitUntil {
    uiSleep 0.1;
    private _candidate = missionNamespace getVariable ["YSF_FW_LOGISTICS_LAST_EVENT", []];
    if ((_candidate param [0, ""]) isEqualTo _taskId && {(_candidate param [1, ""]) isEqualTo "completed"}) then {_event = _candidate};
    _event isNotEqualTo [] || {diag_tickTime > _completeDeadline}
};
private _cargoId = (_event param [4, []]) param [0, ""];
private _cargo = if (_cargoId isEqualTo "") then {objNull} else {objectFromNetId _cargoId};
private _resolveDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; !isNull _cargo || {diag_tickTime > _resolveDeadline}};
private _replicationOk = (_event param [0, ""]) isEqualTo _taskId
    && {(_event param [1, ""]) isEqualTo "completed"}
    && {(_event param [2, ""]) isEqualTo _assetId}
    && {(_event param [3, ""]) isEqualTo netId _aircraft}
    && {_cargoId isNotEqualTo ""} && {!isNull _cargo};
["vigil.logistics.client.replication", _replicationOk, format ["event=%1|cargo=%2", _event, _cargoId]] call _assert;
private _deliveredRows = if (isNull _cargo) then {[]} else {[_cargo] call TRIBUNAL_fnc_inventoryTree};
private _deliveredPayload = [_deliveredRows] call TRIBUNAL_fnc_inventoryPayload;
["vigil.logistics.client.inventory", _deliveredPayload isEqualTo _requestedPayload, format ["requested=%1|delivered=%2|tree=%3", _requestedPayload, _deliveredPayload, _deliveredRows]] call _assert;
private _children = if (isNull _cargo) then {[]} else {attachedObjects _cargo};
private _localityOk = !isNull _cargo && {!local _cargo} && {(owner _cargo) in [0, 2]}
    && {(_children findIf {local _x || {!((owner _x) in [0, 2])}}) < 0};
["vigil.logistics.client.locality", _localityOk, format ["requester=%1/%2|aircraft=%3/%4|cargo=%5/%6|children=%7", local player, owner player, if (isNull _aircraft) then {false} else {local _aircraft}, if (isNull _aircraft) then {-1} else {owner _aircraft}, if (isNull _cargo) then {false} else {local _cargo}, if (isNull _cargo) then {-1} else {owner _cargo}, _children apply {[netId _x, local _x, owner _x]}]] call _assert;

private _egressDeadline = diag_tickTime + 330;
waitUntil {
    uiSleep 0.2;
    _entry = [_assetId] call YSF_fwGetEntry;
    isNull (_entry getOrDefault ["spawnedVeh", objNull]) || {diag_tickTime > _egressDeadline}
};
private _clientEgressOk = isNull (_entry getOrDefault ["spawnedVeh", objNull])
    && {(_entry getOrDefault ["state", ""]) in [YSF_FW_STATE_STOWED, YSF_FW_STATE_COOLDOWN]};
["vigil.logistics.client.egress", _clientEgressOk, format ["state=%1|aircraftNull=%2", _entry getOrDefault ["state", ""], isNull (_entry getOrDefault ["spawnedVeh", objNull])]] call _assert;
missionNamespace setVariable ["TRIBUNAL_LOGISTICS_CLIENT_EGRESS", [_token, _clientEgressOk], true];
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-fixed-wing-logistics",
        "fixture": "registered B_T_VTOL_01_vehicle_F delivering one packed Box_NATO_Ammo_F on a parachute pallet",
        "manifest_categories": "weapon,magazine,item,backpack",
        "ui_path": "YOSHI_taskFW_logiStub/YFU_assetsSubmitOrder",
        "player_spawn": "2000,5,5600",
        "respawn_on_start": "0",
        "future_client_isolation": "client-b observes one shared aircraft/drop/container but never inherits client-a fabricator queue or dialog state",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A role-eligible registered fixed-wing logistics aircraft reconstructs once, accepts one non-empty physical-storage manifest from the real Vigil/Fabricator request path, flies to the requested area, releases the exact server-authoritative cargo under a real parachute, lands it intact and accurately with identical weapon, magazine, item, and backpack contents, rejects a concurrent duplicate, then physically egresses and remains reusable.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Review found that the prior client-local helper reported success immediately, flung cargo from arbitrary loiter position, had no task guard, and left parachute completion implicit. The refined contract preserves the physical-object manifest model while making tasking, release, locality, completion, and RTB authoritative and observable.",
        dependencies=("Vigil fixed-wing registry", "Field Utilities fabricator/packing", "Tribunal aviation and delivery observers", "CBA"),
        evidence_types=frozenset({"registration", "client-request", "manifest", "aircraft-trajectory", "cargo-release", "parachute", "paired-trajectory", "landing", "inventory", "locality", "negative-control", "cleanup"}),
        locality_requirements="Client-a owns Vigil/Fabricator UI and constructs the requested packed objects; authority transfers once to the dedicated server, which owns aircraft, crew, cargo, parachute, delivery result, RTB, and cleanup. Client-a observes the single replicated outcome.",
    ),
)
