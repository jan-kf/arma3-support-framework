/*
Server-authoritative nearby vehicle-cargo loading. ACE identifies the pair; the
server authenticates and revalidates it before native mutation.
*/
YFU_CARGO_LOAD_TOKEN = "YFU_CARGO_LOAD_INTERNAL_V1";
YFU_CARGO_LOAD_RANGE = 10;
YFU_fnc_cargoLoadPlayer = {
	params ["_owner"]; private _player = objNull;
	{if ((owner _x) isEqualTo _owner) exitWith {_player = _x;};} forEach allPlayers;
	_player
};
YFU_fnc_cargoLoadSupplyEligible = {
	params ["_supply"];
	!isNull _supply && {alive _supply} && {
		_supply isKindOf "ReammoBox_F" || {_supply isKindOf "Land_Pallet_F"}
			|| {_supply isKindOf "LandVehicle"} || {_supply isKindOf "UAV_01_base_F"}
	}
};
YFU_fnc_cargoLoadPairEligible = {
	params ["_requester", "_supply", "_carrier"];
	if (isNull _requester || {!alive _requester} || {!([_supply] call YFU_fnc_cargoLoadSupplyEligible)}
		|| {isNull _carrier} || {!alive _carrier} || {_carrier isEqualTo _supply}) exitWith {false};
	if ((_requester distance _supply) > YFU_CARGO_LOAD_RANGE || {(_requester distance _carrier) > YFU_CARGO_LOAD_RANGE}
		|| {(_supply distance _carrier) > YFU_CARGO_LOAD_RANGE} || {!isNull (attachedTo _supply)}
		|| {!isNull (isVehicleCargo _supply)}) exitWith {false};
	private _capacity = _carrier canVehicleCargo _supply;
	(_capacity param [0, false]) && {(_capacity param [1, false])}
};
YFU_fnc_cargoLoadResult = {
	if (!hasInterface) exitWith {};
	params ["_operationId", "_accepted", "_reason", "_supplyId", "_carrierId"];
	private _rows = uiNamespace getVariable ["YFU_CARGO_LOAD_RESULTS", []];
	_rows pushBack [_operationId, _accepted, _reason, _supplyId, _carrierId, clientOwner, diag_tickTime];
	if ((count _rows) > 64) then {_rows deleteRange [0, (count _rows) - 64];};
	uiNamespace setVariable ["YFU_CARGO_LOAD_RESULTS", _rows];
};
YFU_fnc_cargoLoadPublish = {
	params ["_token", "_owner", "_operationId", "_accepted", "_reason", "_supply", "_carrier"];
	if (!isServer || {_token isNotEqualTo YFU_CARGO_LOAD_TOKEN}) exitWith {};
	private _supplyId = if (isNull _supply) then {""} else {netId _supply};
	private _carrierId = if (isNull _carrier) then {""} else {netId _carrier};
	[_operationId, _accepted, _reason, _supplyId, _carrierId] remoteExecCall ["YFU_fnc_cargoLoadResult", _owner];
	private _audit = localNamespace getVariable ["YFU_CARGO_LOAD_AUDIT", []];
	_audit pushBack [_operationId, _accepted, _reason, _owner, _supplyId, _carrierId, local _supply, local _carrier, diag_tickTime];
	if ((count _audit) > 96) then {_audit deleteRange [0, (count _audit) - 96];};
	localNamespace setVariable ["YFU_CARGO_LOAD_AUDIT", _audit];
};
YFU_fnc_cargoLoadRequestServer = {
	if (!isServer) exitWith {false};
	params [["_operationId", "", [""]], ["_supply", objNull, [objNull]], ["_carrier", objNull, [objNull]]];
	private _owner = remoteExecutedOwner;
	private _reject = {params ["_reason"]; [YFU_CARGO_LOAD_TOKEN, _owner, _operationId, false, _reason, _supply, _carrier] call YFU_fnc_cargoLoadPublish; false};
	if (_owner <= 2 || {_operationId isEqualTo ""} || {(count _operationId) > 128}) exitWith {["schema"] call _reject};
	private _requests = localNamespace getVariable ["YFU_CARGO_LOAD_REQUESTS", createHashMap]; private _now = diag_tickTime;
	{if ((_now - (_requests getOrDefault [_x, _now])) > 300) then {_requests deleteAt _x;};} forEach keys _requests;
	private _key = format ["%1#%2", _owner, _operationId];
	if ((_requests getOrDefault [_key, -1]) >= 0) exitWith {["duplicate"] call _reject};
	_requests set [_key, _now]; localNamespace setVariable ["YFU_CARGO_LOAD_REQUESTS", _requests];
	private _requester = [_owner] call YFU_fnc_cargoLoadPlayer;
	if (isNull _requester || {!alive _requester}) exitWith {["requester"] call _reject};
	if !([_supply] call YFU_fnc_cargoLoadSupplyEligible) exitWith {["supply"] call _reject};
	if (isNull _carrier || {!alive _carrier} || {_carrier isEqualTo _supply}) exitWith {["carrier"] call _reject};
	if ((_requester distance _supply) > YFU_CARGO_LOAD_RANGE || {(_requester distance _carrier) > YFU_CARGO_LOAD_RANGE}) exitWith {["requester-range"] call _reject};
	if ((_supply distance _carrier) > YFU_CARGO_LOAD_RANGE) exitWith {["pair-range"] call _reject};
	if (!isNull (attachedTo _supply) || {!isNull (isVehicleCargo _supply)}) exitWith {["supply-state"] call _reject};
	if ((_supply getVariable ["YFU_CARGO_LOAD_PENDING", []]) isNotEqualTo []) exitWith {["pending"] call _reject};
	private _capacity = _carrier canVehicleCargo _supply;
	if !((_capacity param [0, false]) && {(_capacity param [1, false])}) exitWith {["capacity"] call _reject};
	_supply setVariable ["YFU_CARGO_LOAD_PENDING", [_operationId, _owner], true];
	[YFU_CARGO_LOAD_TOKEN, _owner, _operationId, _supply, _carrier] spawn {
		params ["_token", "_owner", "_operationId", "_supply", "_carrier"];
		private _commandAccepted = _carrier setVehicleCargo _supply; private _deadline = diag_tickTime + 3;
		waitUntil {uiSleep 0.02; (isVehicleCargo _supply) isEqualTo _carrier || {diag_tickTime > _deadline}};
		private _membership = (isVehicleCargo _supply) isEqualTo _carrier;
		_supply setVariable ["YFU_CARGO_LOAD_PENDING", nil, true];
		private _accepted = _commandAccepted && {_membership};
		private _reason = if (_accepted) then {"accepted"} else {if (_commandAccepted) then {"membership"} else {"command"}};
		[_token, _owner, _operationId, _accepted, _reason, _supply, _carrier] call YFU_fnc_cargoLoadPublish;
	}; true
};
YFU_fnc_cargoRequestLoad = {
	params ["_supply", "_carrier", ["_operationId", ""]];
	if (_operationId isEqualTo "") then {_operationId = format ["cargo-%1-%2-%3", clientOwner, floor (diag_tickTime * 1000), floor random 1000000];};
	[_operationId, _supply, _carrier] remoteExecCall ["YFU_fnc_cargoLoadRequestServer", 2]; _operationId
};


YOSHI_setObjectLoadHandling = {
	params ["_object"];

	[_object, -1] call ace_cargo_fnc_setSize;

	_object addEventHandler ["EpeContactStart", {
		params ["_object1", "_object2", "_selection1", "_selection2", "_force", "_reactForce", "_worldPos"];
		_object1 call YOSHI_attachToBelow;
	}];
};

YOSHI_attachToBelow = {
	params ["_obj"];
	if (isNull _obj) exitWith {false};

	private _loc = getPosASL _obj;
	private _locBelow = _loc vectorAdd [0,0,-2];

	private _hits = lineIntersectsSurfaces [_loc, _locBelow, _obj, objNull, true, 1, "FIRE", "GEOM"];
	if (_hits isEqualTo []) exitWith {false};

	private _firstHit = _hits select 0;
	if ((count _firstHit) < 3) exitWith {false};

	private _hitPos = _firstHit select 0;
	private _hitObj = _firstHit select 2;

	if (!isNull _hitObj && {!(_hitObj isKindOf "Static")}) then {
		private _objectToAttach = _obj;
		private _targetObject = _hitObj;
		private _dirObjectToAttach = getDir _objectToAttach;
		private _dirTargetObject = getDir _targetObject;
		_objectToAttach attachTo [_targetObject];
		_objectToAttach setPosASL _hitPos;
		_objectToAttach setDir ( _dirObjectToAttach - _dirTargetObject);
		true
	} else {
		false
	};
};

YOSHI_getSuppliesAction = {
	params ["_box", "_caller", "_params"];

	private _actions = [];


	{
		private _vic = _x;
		private _checks = _vic canVehicleCargo _box;

		if ((_checks select 0) && (_checks select 1)) then {
			private _loadSuppliesAction = [
				format["loadSupplies-%1", netId _vic], format ["Load Into %1", getText (configFile >> "CfgVehicles" >> typeOf _vic >> "displayName")], "",
				{
					params ["_target", "_caller", "_vic"];

					[_target, _vic] call YFU_fnc_cargoRequestLoad;
				}, 
				{
					params ["_target", "_caller", "_vic"];

					[_caller, _target, _vic] call YFU_fnc_cargoLoadPairEligible
				},
				{},
				_vic
			] call ace_interact_menu_fnc_createAction;
			_actions pushBack [_loadSuppliesAction, [], _box];
		};

	} forEach (_box nearEntities ['AllVehicles', 10]);

	_actions

};
