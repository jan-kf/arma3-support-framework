params ["_logic"];

if (!isServer || {isNull _logic} || {typeOf _logic isNotEqualTo "YAS_APS_Zeus_Toggle_Module"}) exitWith {false};

/*
 * Native curator placement replicates the client-owned logic before its
 * attachment and authenticated placement claim necessarily arrive.
 */
[_logic] spawn {
	params ["_logic"];
	private _logicId = netId _logic;
	private _deadline = diag_tickTime + 5;
	private _claim = [];
	waitUntil {
		uiSleep 0.01;
		private _claims = localNamespace getVariable ["YAS_APS_ZEUS_CLAIMS", createHashMap];
		_claim = _claims getOrDefault [_logicId, []];
		_claim isNotEqualTo [] || {isNull _logic} || {diag_tickTime > _deadline}
	};
	if (isNull _logic) exitWith {};
	if (_claim isEqualTo []) exitWith {
		private _audit = localNamespace getVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", []];
		_audit pushBack ["", _logicId, "", -1, "missing_claim", false, diag_tickTime];
		localNamespace setVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", _audit];
		deleteVehicle _logic;
	};

	_claim params ["_operationId", "_targetId", "_curatorId", "_requesterOwner", "_status"];
	private _claims = localNamespace getVariable ["YAS_APS_ZEUS_CLAIMS", createHashMap];
	if (_status isNotEqualTo "claimed") exitWith {};
	_claim set [4, "processing"];
	_claims set [_logicId, _claim];
	localNamespace setVariable ["YAS_APS_ZEUS_CLAIMS", _claims];

	private _target = objectFromNetId _targetId;
	private _curator = objectFromNetId _curatorId;
	private _candidates = ((synchronizedObjects _logic) + [attachedTo _logic]) select {
		!isNull _x && {_x isKindOf "AllVehicles"}
	};
	_candidates = _candidates arrayIntersect _candidates;
	private _requester = objNull;
	{if (owner _x isEqualTo _requesterOwner) exitWith {_requester = _x;};} forEach allPlayers;
	private _valid = !isNull _target
		&& {!isNull _curator}
		&& {!isNull _requester}
		&& {(getAssignedCuratorLogic _requester) isEqualTo _curator}
		&& {_target in (curatorEditableObjects _curator)}
		&& {(count _candidates) isEqualTo 1}
		&& {(_candidates # 0) isEqualTo _target};
	private _reason = if (_valid) then {"accepted"} else {"invalid_or_ambiguous_target"};
	private _enabled = _target getVariable ["YOSHI_APS_Installed", false];
	if (_valid) then {
		_enabled = [_target] call YOSHI_fnc_apsToggleVehicle;
	};

	_claims deleteAt _logicId;
	localNamespace setVariable ["YAS_APS_ZEUS_CLAIMS", _claims];
	private _audit = localNamespace getVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _targetId, _requesterOwner, _reason, _enabled, diag_tickTime];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YAS_APS_ZEUS_TOGGLE_AUDIT", _audit];
	[_operationId, _logicId, _targetId, _valid, _reason, _enabled] remoteExecCall ["YAS_fnc_apsZeusToggleResult", _requesterOwner];
	deleteVehicle _logic;
};

true
