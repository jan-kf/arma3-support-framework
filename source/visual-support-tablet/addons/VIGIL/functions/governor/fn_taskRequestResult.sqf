params ["_requestId", "_phase", "_accepted", "_reason", ["_taskId", ""], ["_state", ""]];
if (!hasInterface || {remoteExecutedOwner > 2}) exitWith {false};
private _rows = uiNamespace getVariable ["YSF_task_request_results", []];
_rows pushBack [_requestId, _phase, _accepted isEqualTo true, _reason, _taskId, _state, clientOwner, diag_tickTime];
uiNamespace setVariable ["YSF_task_request_results", _rows];
true
