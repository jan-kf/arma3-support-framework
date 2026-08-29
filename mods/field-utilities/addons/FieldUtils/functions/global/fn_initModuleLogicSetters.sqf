YFU_fnc_rebuildModuleRegistration = {
	if (!isServer) exitWith {false};
	private _storage = localNamespace getVariable ["YFU_MODULE_STORAGE_RECORDS", createHashMap];
	private _fabricators = localNamespace getVariable ["YFU_MODULE_FABRICATOR_RECORDS", createHashMap];
	private _catalogue = [];
	private _stations = [];
	private _storageLogics = [];
	private _fabricatorLogics = [];
	private _inventoryValues = [];
	{private _row = _y; _storageLogics pushBackUnique (_row # 0); {_catalogue pushBackUnique _x;} forEach (_row # 1);} forEach _storage;
	{private _row = _y; _fabricatorLogics pushBackUnique (_row # 0); {_stations pushBackUnique _x;} forEach (_row # 1); _inventoryValues pushBackUnique (_row # 2);} forEach _fabricators;
	localNamespace setVariable ["YFU_MODULE_CATALOGUE", _catalogue];
	localNamespace setVariable ["YFU_MODULE_STATIONS", _stations];
	missionNamespace setVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", _catalogue, true];
	missionNamespace setVariable ["YFU_FABRICATOR_STATIONS", _stations, true];
	YOSHI_VIRTUAL_STORAGE = _storageLogics param [0, objNull];
	YOSHI_FABRICATOR = _fabricatorLogics param [0, objNull];
	publicVariable "YOSHI_VIRTUAL_STORAGE";
	publicVariable "YOSHI_FABRICATOR";
	// A uniform value preserves the old mission-wide switch. Mixed per-module
	// values are intentionally fail-closed until their station policy is chosen.
	YOSHI_FABRICATOR_LOCAL_INVENTORY = (count _inventoryValues) isEqualTo 1 && {_inventoryValues # 0};
	publicVariable "YOSHI_FABRICATOR_LOCAL_INVENTORY";
	true
};

YFU_fnc_registerEdenModule = {
	params ["_logic", "_expectedClass", "_recordKey", ["_inventory", true]];
	if (!isServer) exitWith {false};
	private _remoteOwner = remoteExecutedOwner;
	private _class = if (isNull _logic) then {""} else {typeOf _logic};
	private _native = !isNull _logic && {_class isEqualTo _expectedClass} && {local _logic} && {owner _logic isEqualTo 2} && {_remoteOwner <= 2};
	// Preserve direct server-local mission API compatibility while preventing it
	// from becoming a remote authority path.
	private _legacy = !isNull _logic && {_class isEqualTo "Logic"} && {local _logic} && {_remoteOwner <= 2};
	private _accepted = _native || {_legacy};
	private _reason = if (_native) then {"accepted_native"} else {if (_legacy) then {"accepted_legacy"} else {if (_remoteOwner > 2) then {"remote_request"} else {"invalid_logic"}}};
	private _sync = if (isNull _logic) then {[]} else {synchronizedObjects _logic};
	private _audit = localNamespace getVariable ["YFU_MODULE_DISPATCH_AUDIT", []];
	_audit pushBack [_expectedClass, _class, if (isNull _logic) then {""} else {netId _logic}, isServer, local _logic, if (isNull _logic) then {-1} else {owner _logic}, _remoteOwner, _accepted, _reason, _sync apply {[typeOf _x, vehicleVarName _x, netId _x]}, _inventory, diag_tickTime];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YFU_MODULE_DISPATCH_AUDIT", _audit];
	if (!_accepted) exitWith {false};
	private _records = localNamespace getVariable [_recordKey, createHashMap];
	private _identity = if ((netId _logic) isEqualTo "") then {str _logic} else {netId _logic};
	_records set [_identity, [_logic, _sync, _inventory]];
	localNamespace setVariable [_recordKey, _records];
	call YFU_fnc_rebuildModuleRegistration
};

YOSHI_setVirtualStorageLogic = {
	params ["_logic", ["_id", 0], ["_params", []]];
	[_logic, "FieldUtils_Virtual_Storage_Module", "YFU_MODULE_STORAGE_RECORDS", true] call YFU_fnc_registerEdenModule
};

YOSHI_setFabricatorLogic = {
	params ["_logic", ["_id", 0], ["_params", []]];
	private _inventory = if (isNull _logic) then {false} else {_logic getVariable ["Fabricator_Module_EnableLocalArsenal", true]};
	[_logic, "FieldUtils_Fabricator_Module", "YFU_MODULE_FABRICATOR_RECORDS", _inventory] call YFU_fnc_registerEdenModule
};
