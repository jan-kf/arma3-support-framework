params [["_logic", objNull, [objNull]]];

if (!isServer) exitWith {false};

private _remoteOwner = remoteExecutedOwner;
private _className = if (isNull _logic) then {""} else {typeOf _logic};
private _local = !isNull _logic && {local _logic};
private _owner = if (isNull _logic) then {-1} else {owner _logic};
private _accepted = !isNull _logic
	&& {_className isEqualTo "YAS_CBR_Module"}
	&& {_local}
	&& {_owner isEqualTo 2}
	&& {_remoteOwner <= 2};
private _reason = if (_accepted) then {"accepted"} else {
	if (isNull _logic) exitWith {"null_logic"};
	if (_className isNotEqualTo "YAS_CBR_Module") exitWith {"wrong_class"};
	if (!_local || {_owner isNotEqualTo 2}) exitWith {"wrong_locality"};
	"remote_request"
};
private _row = [
	_className, vehicleVarName _logic, if (isNull _logic) then {""} else {netId _logic},
	if (isNull _logic) then {[]} else {getPosASL _logic}, isServer, _local,
	_owner, _remoteOwner, _accepted, _reason, diag_tickTime
];
private _audit = localNamespace getVariable ["YAS_CBR_MODULE_DISPATCH_AUDIT", []];
_audit pushBack _row;
if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
localNamespace setVariable ["YAS_CBR_MODULE_DISPATCH_AUDIT", _audit];
diag_log format ["YAS_CBR_MODULE_DISPATCH|%1", _row];

if (!_accepted) exitWith {false};
[true] call YOSHI_fnc_cbrSetEnabled;
true
