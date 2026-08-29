params ["_operationId", "_logicId", "_accepted", "_reason", "_assetId"];

if (!hasInterface || {remoteExecutedOwner > 2}) exitWith {false};
private _rows = uiNamespace getVariable ["YSF_FW_ZEUS_RESULTS", []];
_rows pushBack [_operationId, _logicId, _accepted, _reason, _assetId, clientOwner, diag_tickTime];
if ((count _rows) > 64) then {_rows deleteRange [0, (count _rows) - 64];};
uiNamespace setVariable ["YSF_FW_ZEUS_RESULTS", _rows];
if (_accepted) then {
    [objNull, "Added Fixed-Wing Asset"] call BIS_fnc_showCuratorFeedbackMessage;
    ["VIGIL", "Added Fixed-Wing Asset", 5] call BIS_fnc_curatorHint;
};
true
