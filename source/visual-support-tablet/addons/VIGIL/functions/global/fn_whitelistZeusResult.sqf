params ["_operationId", "_logicId", "_accepted", "_reason", "_targetId", "_added"];

if (!hasInterface || {remoteExecutedOwner > 2}) exitWith {false};
private _rows = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_RESULTS", []];
_rows pushBack [_operationId, _logicId, _accepted, _reason, _targetId, _added, clientOwner, diag_tickTime];
if ((count _rows) > 64) then {_rows deleteRange [0, (count _rows) - 64];};
uiNamespace setVariable ["YSF_WHITELIST_ZEUS_RESULTS", _rows];
if (_accepted) then {
	private _message = if (_added) then {"Added Asset to Whitelist"} else {"Removed Asset from Whitelist"};
	[objNull, _message] call BIS_fnc_showCuratorFeedbackMessage;
	["Whitelist Updated", _message, 5] call BIS_fnc_curatorHint;
};
true
