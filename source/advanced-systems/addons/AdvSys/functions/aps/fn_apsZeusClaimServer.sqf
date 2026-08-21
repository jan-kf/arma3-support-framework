params ["_logic", "_target", "_curator", "_operationId"];

if (!isServer) exitWith {false};
private _requesterOwner = remoteExecutedOwner;
private _logicId = if (isNull _logic) then {""} else {netId _logic};
private _targetId = if (isNull _target) then {""} else {netId _target};
private _curatorId = if (isNull _curator) then {""} else {netId _curator};
private _operations = localNamespace getVariable ["YAS_APS_ZEUS_OPERATIONS", createHashMap];
private _now = diag_tickTime;
{
	private _row = _operations getOrDefault [_x, []];
	if (_now - (_row param [5, _now]) > 300) then {_operations deleteAt _x;};
} forEach keys _operations;
while {(count _operations) > 127} do {
	private _oldestKey = "";
	private _oldestAt = 1e12;
	{
		private _at = (_operations getOrDefault [_x, []]) param [5, _now];
		if (_at < _oldestAt) then {_oldestAt = _at; _oldestKey = _x;};
	} forEach keys _operations;
	if (_oldestKey isEqualTo "") exitWith {};
	_operations deleteAt _oldestKey;
};
localNamespace setVariable ["YAS_APS_ZEUS_OPERATIONS", _operations];
private _prior = _operations getOrDefault [_operationId, []];
if (_operationId isEqualType "" && {_operationId isNotEqualTo ""} && {_prior isNotEqualTo []}) exitWith {
	private _audit = localNamespace getVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _targetId, _curatorId, _requesterOwner, false, "duplicate", diag_tickTime, []];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", _audit];
	diag_log format ["YAS_APS_ZEUS|CLAIM|operation=%1|logic=%2|target=%3|owner=%4|accepted=false|reason=duplicate", _operationId, _logicId, _targetId, _requesterOwner];
	[_operationId, _logicId, _targetId, false, "duplicate", false] remoteExecCall ["YAS_fnc_apsZeusToggleResult", _requesterOwner];
	false
};
if (_operationId isEqualType "" && {_operationId isNotEqualTo ""}) then {
	_operations set [_operationId, [_logicId, _targetId, _curatorId, _requesterOwner, "pending", diag_tickTime]];
	localNamespace setVariable ["YAS_APS_ZEUS_OPERATIONS", _operations];
};
[_logic, _target, _curator, _operationId, _requesterOwner, _logicId, _targetId, _curatorId] spawn {
	params ["_logic", "_target", "_curator", "_operationId", "_requesterOwner", "_logicId", "_targetId", "_curatorId"];
	private _requester = objNull;
	{if (owner _x isEqualTo _requesterOwner) exitWith {_requester = _x;};} forEach allPlayers;
	private _predicates = [
		["remote_owner", _requesterOwner > 2],
		["operation_id", _operationId isEqualType "" && {_operationId isNotEqualTo ""}],
		["logic_net_id", _logicId isNotEqualTo ""],
		["logic_class", !isNull _logic && {typeOf _logic isEqualTo "YAS_APS_Zeus_Toggle_Module"}],
		["logic_owner", !isNull _logic && {owner _logic isEqualTo _requesterOwner}],
		["assigned_curator", !isNull _requester && {(getAssignedCuratorLogic _requester) isEqualTo _curator}],
		["vehicle_target", !isNull _target && {_target isKindOf "AllVehicles"}],
		["editable_target", !isNull _curator && {_target in (curatorEditableObjects _curator)}]
	];
	private _failed = _predicates select {!(_x # 1)};
	private _valid = _failed isEqualTo [];
	private _reason = if (_valid) then {"accepted"} else {format ["predicate_%1", (_failed # 0) # 0]};
	private _operations = localNamespace getVariable ["YAS_APS_ZEUS_OPERATIONS", createHashMap];
	if (_operationId isEqualType "" && {_operationId isNotEqualTo ""}) then {
		_operations set [_operationId, [_logicId, _targetId, _curatorId, _requesterOwner, _reason, diag_tickTime]];
		localNamespace setVariable ["YAS_APS_ZEUS_OPERATIONS", _operations];
	};
	if (_valid) then {
		private _claims = localNamespace getVariable ["YAS_APS_ZEUS_CLAIMS", createHashMap];
		_claims set [_logicId, [_operationId, _targetId, _curatorId, _requesterOwner, "claimed"]];
		localNamespace setVariable ["YAS_APS_ZEUS_CLAIMS", _claims];
	};
	private _audit = localNamespace getVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _targetId, _curatorId, _requesterOwner, _valid, _reason, diag_tickTime, _predicates];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YAS_APS_ZEUS_CLAIM_AUDIT", _audit];
	diag_log format ["YAS_APS_ZEUS|CLAIM|operation=%1|logic=%2|target=%3|curator=%4|owner=%5|accepted=%6|reason=%7|predicates=%8", _operationId, _logicId, _targetId, _curatorId, _requesterOwner, _valid, _reason, _predicates];
	if (!_valid && {_requesterOwner > 2}) then {
		[_operationId, _logicId, _targetId, false, _reason, false] remoteExecCall ["YAS_fnc_apsZeusToggleResult", _requesterOwner];
	};
};
true
