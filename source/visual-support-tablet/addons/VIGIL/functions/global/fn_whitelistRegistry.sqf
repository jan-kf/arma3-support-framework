YSF_fnc_whitelistIdentity = {
	params ["_object"];
	if (isNull _object) exitWith {""};
	private _id = netId _object;
	if (_id isEqualTo "") then {str _object} else {_id}
};

YSF_fnc_whitelistPublish = {
	if (!isServer) exitWith {false};
	private _members = localNamespace getVariable ["YSF_WHITELIST_MEMBERS", createHashMap];
	private _assets = [];
	{
		private _object = _y;
		if (!isNull _object) then {_assets pushBackUnique (vehicle _object);};
	} forEach _members;
	missionNamespace setVariable ["YSF_WHITELIST_CONFIGURED", true, true];
	missionNamespace setVariable ["YSF_WHITELISTED_ASSETS", _assets, true];
	true
};

YSF_fnc_whitelistReconcileEden = {
	if (!isServer) exitWith {false};
	private _records = localNamespace getVariable ["YSF_WHITELIST_EDEN_RECORDS", createHashMap];
	private _overrides = localNamespace getVariable ["YSF_WHITELIST_OVERRIDES", createHashMap];
	private _members = createHashMap;
	private _removed = [];
	private _retainedModule = objNull;
	{
		private _row = _records getOrDefault [_x, []];
		private _logic = _row param [0, objNull, [objNull]];
		if (isNull _logic || {typeOf _logic isNotEqualTo "YSF_Asset_Whitelist_Module"} || {!local _logic} || {owner _logic isNotEqualTo 2}) then {
			_records deleteAt _x;
			_removed pushBack _x;
		} else {
			if (isNull _retainedModule) then {_retainedModule = _logic;};
			private _sync = synchronizedObjects _logic apply {vehicle _x};
			_records set [_x, [_logic, _sync]];
			{
				private _id = [_x] call YSF_fnc_whitelistIdentity;
				if (_id isNotEqualTo "" && {!isNull _x}) then {_members set [_id, _x];};
			} forEach _sync;
		};
	} forEach +(keys _records);
	{
		private _row = _overrides getOrDefault [_x, []];
		private _object = _row param [0, objNull, [objNull]];
		private _enabled = _row param [1, false, [false]];
		if (isNull _object) then {
			_overrides deleteAt _x;
		} else {
			if (_enabled) then {_members set [_x, _object];} else {_members deleteAt _x;};
		};
	} forEach +(keys _overrides);
	private _prior = localNamespace getVariable ["YSF_WHITELIST_MEMBERS", createHashMap];
	private _changed = (count _prior) isNotEqualTo (count _members)
		|| {((keys _prior) findIf {isNil {_members get _x} || {!((_prior get _x) isEqualTo (_members get _x))}}) >= 0};
	localNamespace setVariable ["YSF_WHITELIST_EDEN_RECORDS", _records];
	localNamespace setVariable ["YSF_WHITELIST_OVERRIDES", _overrides];
	localNamespace setVariable ["YSF_WHITELIST_MEMBERS", _members];
	YSF_WHITELISTED_ASSETS_MODULE = _retainedModule;
	publicVariable "YSF_WHITELISTED_ASSETS_MODULE";
	if (_changed || {_removed isNotEqualTo []}) then {
		private _audit = localNamespace getVariable ["YSF_WHITELIST_RECONCILE_AUDIT", []];
		_audit pushBack [_removed, keys _records, keys _members, diag_tickTime];
		if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
		localNamespace setVariable ["YSF_WHITELIST_RECONCILE_AUDIT", _audit];
		call YSF_fnc_whitelistPublish;
	};
	true
};

YSF_fnc_whitelistEnsureMonitor = {
	if (!isServer) exitWith {false};
	private _handle = localNamespace getVariable ["YSF_WHITELIST_EDEN_MONITOR", scriptNull];
	if (!scriptDone _handle) exitWith {true};
	_handle = [] spawn {
		private _done = false;
		while {!_done} do {
			uiSleep 0.25;
			call YSF_fnc_whitelistReconcileEden;
			_done = (count (localNamespace getVariable ["YSF_WHITELIST_EDEN_RECORDS", createHashMap])) isEqualTo 0;
		};
		localNamespace setVariable ["YSF_WHITELIST_EDEN_MONITOR", scriptNull];
	};
	localNamespace setVariable ["YSF_WHITELIST_EDEN_MONITOR", _handle];
	true
};

YSF_fnc_whitelistRegisterEden = {
	params ["_logic"];
	if (!isServer) exitWith {false};
	private _remoteOwner = remoteExecutedOwner;
	private _class = if (isNull _logic) then {""} else {typeOf _logic};
	private _native = !isNull _logic && {_class isEqualTo "YSF_Asset_Whitelist_Module"} && {local _logic} && {owner _logic isEqualTo 2} && {_remoteOwner <= 2};
	private _accepted = _native;
	private _reason = if (_native) then {"accepted_native"} else {if (_remoteOwner > 2) then {"remote_request"} else {"invalid_logic"}};
	private _sync = if (isNull _logic) then {[]} else {synchronizedObjects _logic};
	private _audit = localNamespace getVariable ["YSF_WHITELIST_EDEN_AUDIT", []];
	_audit pushBack [_class, if (isNull _logic) then {""} else {netId _logic}, isServer, local _logic, if (isNull _logic) then {-1} else {owner _logic}, _remoteOwner, _accepted, _reason, _sync apply {[typeOf _x, vehicleVarName _x, netId (vehicle _x)]}, diag_tickTime];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YSF_WHITELIST_EDEN_AUDIT", _audit];
	if (!_accepted) exitWith {false};
	private _records = localNamespace getVariable ["YSF_WHITELIST_EDEN_RECORDS", createHashMap];
	private _logicId = [_logic] call YSF_fnc_whitelistIdentity;
	_records set [_logicId, [_logic, _sync apply {vehicle _x}]];
	localNamespace setVariable ["YSF_WHITELIST_EDEN_RECORDS", _records];
	call YSF_fnc_whitelistReconcileEden;
	call YSF_fnc_whitelistEnsureMonitor
};

YSF_fnc_whitelistToggleServer = {
	params ["_target"];
	if (!isServer || {isNull _target}) exitWith {[false, "invalid_target", false]};
	private _object = vehicle _target;
	private _id = [_object] call YSF_fnc_whitelistIdentity;
	if (_id isEqualTo "") exitWith {[false, "invalid_target", false]};
	call YSF_fnc_whitelistReconcileEden;
	private _members = localNamespace getVariable ["YSF_WHITELIST_MEMBERS", createHashMap];
	private _added = isNil {_members get _id};
	private _overrides = localNamespace getVariable ["YSF_WHITELIST_OVERRIDES", createHashMap];
	_overrides set [_id, [_object, _added]];
	localNamespace setVariable ["YSF_WHITELIST_OVERRIDES", _overrides];
	call YSF_fnc_whitelistReconcileEden;
	[true, "accepted", _added]
};
