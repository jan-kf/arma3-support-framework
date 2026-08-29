params ["_requestId", "_requester", "_vehicle", "_taskType", "_payload", ["_policy", "queue"]];
if (!isServer) exitWith {false};
private _requestOwner = remoteExecutedOwner;
private _queue = localNamespace getVariable ["YSF_task_ingress_queue", []];
if ((count _queue) >= 64) exitWith {
    [_requestId, _requestOwner, _taskType, false, "ingress_full", _vehicle] call YSF_taskRequestAudit;
    [_requestOwner, _requestId, "rejected", false, "ingress_full"] call YSF_taskRequestReply;
    false
};
_queue pushBack [_requestId, _requester, _vehicle, _taskType, _payload, _policy, _requestOwner];
localNamespace setVariable ["YSF_task_ingress_queue", _queue];
private _worker = localNamespace getVariable ["YSF_task_ingress_worker", scriptNull];
if (isNull _worker || {scriptDone _worker}) then {
    _worker = [] spawn {
        private _authorityToken = localNamespace getVariable ["YSF_task_authority_token", "missing"];
        while {count (localNamespace getVariable ["YSF_task_ingress_queue", []]) > 0} do {
            private _pending = localNamespace getVariable ["YSF_task_ingress_queue", []];
            private _next = _pending deleteAt 0;
            localNamespace setVariable ["YSF_task_ingress_queue", _pending];
            _next params ["_requestId", "_requester", "_vehicle", "_taskType", "_payload", "_policy", "_requestOwner"];
            [_requestId, _requester, _vehicle, _taskType, _payload, _policy, _requestOwner, _authorityToken] call YSF_taskRequestProcess;
        };
    };
    localNamespace setVariable ["YSF_task_ingress_worker", _worker];
};
true
