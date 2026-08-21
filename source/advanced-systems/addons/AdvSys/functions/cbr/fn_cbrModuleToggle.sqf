params [["_logic", objNull, [objNull]]];

if (!isServer || {isNull _logic} || {typeOf _logic isNotEqualTo "YAS_CBR_Zeus_Toggle_Module"}) exitWith {false};

[_logic] spawn {
	params ["_logic"];
	private _logicId = netId _logic;
	private _deadline = diag_tickTime + 5;
	private _claim = [];
	waitUntil {
		uiSleep 0.01;
		_claim = (localNamespace getVariable ["YAS_CBR_ZEUS_CLAIMS", createHashMap]) getOrDefault [_logicId, []];
		_claim isNotEqualTo [] || {isNull _logic} || {diag_tickTime > _deadline}
	};
	if (isNull _logic) exitWith {};
	if (_claim isEqualTo []) exitWith {
		private _audit = localNamespace getVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", []];
		_audit pushBack ["", _logicId, -1, "missing_claim", false, diag_tickTime];
		localNamespace setVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", _audit];
	};
	_claim params ["_operationId", "_curatorId", "_requesterOwner", "_status"];
	private _claims = localNamespace getVariable ["YAS_CBR_ZEUS_CLAIMS", createHashMap];
	if (_status isNotEqualTo "claimed") exitWith {};
	_claim set [3, "processing"];
	_claims set [_logicId, _claim];
	localNamespace setVariable ["YAS_CBR_ZEUS_CLAIMS", _claims];
	private _curator = objectFromNetId _curatorId;
	private _requester = objNull;
	{if (owner _x isEqualTo _requesterOwner) exitWith {_requester = _x;};} forEach allPlayers;
	private _valid = !isNull _curator && {!isNull _requester}
		&& {(getAssignedCuratorLogic _requester) isEqualTo _curator};
	private _reason = if (_valid) then {"accepted"} else {"invalid_curator"};
	private _enabled = missionNamespace getVariable ["YOSHI_CBR_ENABLED", false];
	if (_valid) then {_enabled = [] call YOSHI_fnc_cbrToggleEnabled;};
	_claims deleteAt _logicId;
	localNamespace setVariable ["YAS_CBR_ZEUS_CLAIMS", _claims];
	private _audit = localNamespace getVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _requesterOwner, _reason, _enabled, diag_tickTime];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YAS_CBR_ZEUS_TOGGLE_AUDIT", _audit];
	[_operationId, _logicId, _valid, _reason, _enabled] remoteExecCall ["YAS_fnc_cbrZeusToggleResult", _requesterOwner];
	deleteVehicle _logic;
};
true
