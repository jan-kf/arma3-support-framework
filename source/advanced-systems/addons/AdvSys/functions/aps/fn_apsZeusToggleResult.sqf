params ["_operationId", "_logicId", "_targetId", "_accepted", "_reason", "_enabled"];

if (!hasInterface || {remoteExecutedOwner > 2}) exitWith {false};
private _rows = uiNamespace getVariable ["YAS_APS_ZEUS_RESULTS", []];
_rows pushBack [_operationId, _logicId, _targetId, _accepted, _reason, _enabled, clientOwner, diag_tickTime];
if ((count _rows) > 64) then {_rows deleteRange [0, (count _rows) - 64];};
uiNamespace setVariable ["YAS_APS_ZEUS_RESULTS", _rows];
if (_accepted) then {
	private _message = if (_enabled) then {"APS turned ON"} else {"APS turned OFF"};
	[objNull, _message] call BIS_fnc_showCuratorFeedbackMessage;
	["AdvSys APS", _message, 5] call BIS_fnc_curatorHint;
};
true
