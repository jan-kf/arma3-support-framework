params ["_requestId", "_requester", "_vehicle", "_taskType", "_payload"];
if (!isServer) exitWith {false};
private _requestOwner = remoteExecutedOwner;
private _authorityToken = localNamespace getVariable ["YSF_task_authority_token", "missing"];
[_requestId, _requester, _vehicle, _taskType, _payload, _requestOwner, _authorityToken] spawn YSF_taskRequestProcess;
true
