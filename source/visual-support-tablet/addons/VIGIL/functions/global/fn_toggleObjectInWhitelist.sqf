params [["_logic", objNull, [objNull]]];

if (!isServer || {isNull _logic} || {typeOf _logic isNotEqualTo "YSF_Toggle_To_Whitelist_Module"}) exitWith {false};
[_logic] spawn {
	params ["_logic"];
	private _logicId = netId _logic;
	private _deadline = diag_tickTime + 5;
	private _claim = [];
	waitUntil {uiSleep 0.01; _claim = (localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIMS", createHashMap]) getOrDefault [_logicId, []]; _claim isNotEqualTo [] || {isNull _logic} || {diag_tickTime > _deadline}};
	if (isNull _logic || {_claim isEqualTo []}) exitWith {};
	_claim params ["_operationId", "_curatorId", "_requesterOwner", "_status", ["_claimedTarget", objNull, [objNull]]];
	if (_status isNotEqualTo "claimed") exitWith {};
	private _claims = localNamespace getVariable ["YSF_WHITELIST_ZEUS_CLAIMS", createHashMap];
	_claim set [3, "processing"]; _claims set [_logicId, _claim]; localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIMS", _claims];
	private _targets = [];
	if (!isNull _claimedTarget) then {_targets pushBackUnique (vehicle _claimedTarget);};
	{_targets pushBackUnique (vehicle _x);} forEach synchronizedObjects _logic;
	private _attached = attachedTo _logic;
	if (!isNull _attached) then {_targets pushBackUnique (vehicle _attached);};
	private _result = if ((count _targets) isEqualTo 1) then {[_targets # 0] call YSF_fnc_whitelistToggleServer} else {[false, "invalid_target_count", false]};
	private _targetId = if ((count _targets) isEqualTo 1) then {netId (_targets # 0)} else {""};
	_claims deleteAt _logicId; localNamespace setVariable ["YSF_WHITELIST_ZEUS_CLAIMS", _claims];
	private _audit = localNamespace getVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", []];
	_audit pushBack [_operationId, _logicId, _requesterOwner, _result # 1, _targetId, _result # 2, diag_tickTime];
	if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
	localNamespace setVariable ["YSF_WHITELIST_ZEUS_TOGGLE_AUDIT", _audit];
	[_operationId, _logicId, _result # 0, _result # 1, _targetId, _result # 2] remoteExecCall ["YSF_fnc_whitelistZeusResult", _requesterOwner];
	deleteVehicle _logic;
};
true
