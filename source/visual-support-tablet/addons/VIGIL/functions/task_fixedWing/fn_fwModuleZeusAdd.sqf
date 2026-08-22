params [["_logic", objNull, [objNull]]];

if (!isServer || {isNull _logic} || {typeOf _logic isNotEqualTo "YSF_FixedWing_Zeus_Add_Module"}) exitWith {false};
[_logic] spawn {
    params ["_logic"];
    private _logicId = netId _logic;
    private _deadline = diag_tickTime + 5;
    private _claim = [];
    waitUntil {
        uiSleep 0.01;
        _claim = (localNamespace getVariable ["YSF_FW_ZEUS_CLAIMS", createHashMap]) getOrDefault [_logicId, []];
        _claim isNotEqualTo [] || {isNull _logic} || {diag_tickTime > _deadline}
    };
    if (isNull _logic || {_claim isEqualTo []}) exitWith {};
    _claim params ["_operationId", "_curatorId", "_requesterOwner", "_status"];
    if (_status isNotEqualTo "claimed") exitWith {};
    private _claims = localNamespace getVariable ["YSF_FW_ZEUS_CLAIMS", createHashMap];
    _claim set [3, "processing"];
    _claims set [_logicId, _claim];
    localNamespace setVariable ["YSF_FW_ZEUS_CLAIMS", _claims];

    private _targets = (synchronizedObjects _logic) apply {vehicle _x};
    private _attached = attachedTo _logic;
    if (!isNull _attached) then {_targets pushBackUnique (vehicle _attached);};
    private _validTargets = _targets select {!isNull _x && {_x isKindOf "Plane"}};
    private _target = _validTargets param [0, objNull];
    private _beforeId = if (isNull _target) then {""} else {_target getVariable ["YSF_FW_ID", format ["FW_%1", netId _target]]};
    private _accepted = (count _targets) isEqualTo 1 && {(count _validTargets) isEqualTo 1} && {[_target] call YSF_fwRegisterAsset};
    private _reason = if (_accepted) then {"accepted"} else {if ((count _targets) isEqualTo 1) then {"invalid_target"} else {"invalid_target_count"}};

    _claims deleteAt _logicId;
    localNamespace setVariable ["YSF_FW_ZEUS_CLAIMS", _claims];
    private _audit = localNamespace getVariable ["YSF_FW_ZEUS_ADD_AUDIT", []];
    _audit pushBack [_operationId, _logicId, _requesterOwner, _accepted, _reason, _beforeId, diag_tickTime];
    if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
    localNamespace setVariable ["YSF_FW_ZEUS_ADD_AUDIT", _audit];
    [_operationId, _logicId, _accepted, _reason, _beforeId] remoteExecCall ["YSF_fnc_fwModuleZeusResult", _requesterOwner];
    deleteVehicle _logic;
};
true
