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
	private _members = createHashMap;
	{
		{private _object = vehicle _x; private _id = [_object] call YSF_fnc_whitelistIdentity; if (_id isNotEqualTo "") then {_members set [_id, _object];};} forEach ((_y) # 1);
	} forEach _records;
	localNamespace setVariable ["YSF_WHITELIST_MEMBERS", _members];
	YSF_WHITELISTED_ASSETS_MODULE = _logic;
	publicVariable "YSF_WHITELISTED_ASSETS_MODULE";
	call YSF_fnc_whitelistPublish
};

YSF_fnc_whitelistToggleServer = {
	params ["_target"];
	if (!isServer || {isNull _target}) exitWith {[false, "invalid_target", false]};
	private _object = vehicle _target;
	private _id = [_object] call YSF_fnc_whitelistIdentity;
	if (_id isEqualTo "") exitWith {[false, "invalid_target", false]};
	private _members = localNamespace getVariable ["YSF_WHITELIST_MEMBERS", createHashMap];
	private _added = isNil {_members get _id};
	if (_added) then {_members set [_id, _object];} else {_members deleteAt _id;};
	localNamespace setVariable ["YSF_WHITELIST_MEMBERS", _members];
	call YSF_fnc_whitelistPublish;
	[true, "accepted", _added]
};
