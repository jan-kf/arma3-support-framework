params ["_logic", "_curator", "_operationId", ["_target", objNull, [objNull]]];

if (!isServer) exitWith {false};
private _requesterOwner = remoteExecutedOwner;
private _logicId = if (isNull _logic) then {""} else {netId _logic};
private _curatorId = if (isNull _curator) then {""} else {netId _curator};
private _operations = localNamespace getVariable ["YSF_WHITELIST_ZEUS_OPERATIONS", createHashMap];
private _now = diag_tickTime;
{private _row = _operations getOrDefault [_x, []]; if (_now - (_row param [4, _now]) > 300) then {_operations deleteAt _x;};} forEach keys _operations;
private _prior = _operations getOrDefault [_operationId, []];
if (_operationId isEqualType "" && {_operationId isNotEqualTo ""} && {_prior isNotEqualTo []}) exitWith {
	private _audit = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _curatorId, _requesterOwner, false, "duplicate", diag_tickTime, []];
	localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", _audit];
	[_operationId, _logicId, false, "duplicate", "", false] remoteExecCall ["YSF_fnc_whitelistZeusResult", _requesterOwner];
	false
};
if (_operationId isEqualType "" && {_operationId isNotEqualTo ""}) then {
	_operations set [_operationId, [_logicId, _curatorId, _requesterOwner, "pending", diag_tickTime]];
	while {(count _operations) > 127} do {
		private _oldestKey = ""; private _oldestAt = 1e12;
		{private _at = (_operations getOrDefault [_x, []]) param [4, _now]; if (_at < _oldestAt) then {_oldestAt = _at; _oldestKey = _x;};} forEach keys _operations;
		if (_oldestKey isEqualTo "") exitWith {};
		_operations deleteAt _oldestKey;
	};
	localNamespace setVariable ["YSF_WHITELIST_ZEUS_OPERATIONS", _operations];
};
[_logic, _curator, _operationId, _target, _requesterOwner, _logicId, _curatorId] spawn {
	params ["_logic", "_curator", "_operationId", "_target", "_requesterOwner", "_logicId", "_curatorId"];
	private _requester = objNull;
	{if (owner _x isEqualTo _requesterOwner) exitWith {_requester = _x;};} forEach allPlayers;
	private _predicates = [
		["remote_owner", _requesterOwner > 2],
		["operation_id", _operationId isEqualType "" && {_operationId isNotEqualTo ""}],
		["logic_class", !isNull _logic && {typeOf _logic isEqualTo "YSF_Toggle_To_Whitelist_Module"}],
		["logic_owner", !isNull _logic && {owner _logic isEqualTo _requesterOwner}],
		["assigned_curator", !isNull _requester && {(getAssignedCuratorLogic _requester) isEqualTo _curator}],
		["target", !isNull _target]
	];
	private _failed = _predicates select {!(_x # 1)};
	private _valid = _failed isEqualTo [];
	private _reason = if (_valid) then {"accepted"} else {format ["predicate_%1", (_failed # 0) # 0]};
	if (_valid) then {private _claims = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIMS", createHashMap]; _claims set [_logicId, [_operationId, _curatorId, _requesterOwner, "claimed", _target]]; localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIMS", _claims];};
	private _operations = localNamespace getVariable ["YSF_WHITELIST_ZEUS_OPERATIONS", createHashMap];
	_operations set [_operationId, [_logicId, _curatorId, _requesterOwner, _reason, diag_tickTime]];
	localNamespace setVariable ["YSF_WHITELIST_ZEUS_OPERATIONS", _operations];
	private _audit = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _curatorId, _requesterOwner, _valid, _reason, diag_tickTime, _predicates];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIM_AUDIT", _audit];
	if (!_valid && {_requesterOwner > 2}) then {[_operationId, _logicId, false, _reason, "", false] remoteExecCall ["YSF_fnc_whitelistZeusResult", _requesterOwner];};
};
true
