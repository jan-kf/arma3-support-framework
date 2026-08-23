/*
Server-authoritative Field Utilities towing transactions.

The client identifies the exact pair through the registered ACE action. The
server authenticates the transport owner, validates current world state, creates
and retains only this feature's rope handles, and owns finalization.
*/

YFU_TOW_TOKEN = "YFU_TOW_INTERNAL_V1";
YFU_TOW_REQUESTER_RANGE = 10;
YFU_TOW_PAIR_RANGE = 20;
YFU_TOW_MAX_SPEED = 5;

YFU_fnc_towOperations = {
	if (!isServer) exitWith {createHashMap};
	private _all = localNamespace getVariable ["YFU_TOW_OPERATIONS", createHashMap];
	localNamespace setVariable ["YFU_TOW_OPERATIONS", _all];
	_all
};

YFU_fnc_towObjectClaims = {
	if (!isServer) exitWith {createHashMap};
	private _claims = localNamespace getVariable ["YFU_TOW_OBJECT_CLAIMS", createHashMap];
	localNamespace setVariable ["YFU_TOW_OBJECT_CLAIMS", _claims];
	_claims
};

YFU_fnc_towAudit = {
	params ["_token", "_stage", "_reason", "_owner", "_operationId", ["_detail", []]];
	if (!isServer || {_token isNotEqualTo YFU_TOW_TOKEN}) exitWith {};
	private _rows = localNamespace getVariable ["YFU_TOW_AUDIT", []];
	_rows pushBack [_stage, _reason, _owner, _operationId, _detail, diag_tickTime];
	if ((count _rows) > 96) then {_rows deleteRange [0, (count _rows) - 96];};
	localNamespace setVariable ["YFU_TOW_AUDIT", _rows];
};

YFU_fnc_towResult = {
	if (!hasInterface) exitWith {};
	params ["_operationId", "_accepted", "_reason", "_towId", "_cargoId", "_ropeIds", "_state"];
	private _rows = uiNamespace getVariable ["YFU_TOW_RESULTS", []];
	_rows pushBack [_operationId, _accepted, _reason, _towId, _cargoId, _ropeIds, _state, clientOwner, diag_tickTime];
	if ((count _rows) > 64) then {_rows deleteRange [0, (count _rows) - 64];};
	uiNamespace setVariable ["YFU_TOW_RESULTS", _rows];
};

YFU_fnc_towPublishResult = {
	params ["_token", "_owner", "_operationId", "_accepted", "_reason", "_tow", "_cargo", "_ropes", "_state"];
	if (!isServer || {_token isNotEqualTo YFU_TOW_TOKEN}) exitWith {};
	private _towId = if (isNull _tow) then {""} else {netId _tow};
	private _cargoId = if (isNull _cargo) then {""} else {netId _cargo};
	private _ropeIds = _ropes select {!isNull _x} apply {netId _x};
	[_operationId, _accepted, _reason, _towId, _cargoId, _ropeIds, _state] remoteExecCall ["YFU_fnc_towResult", _owner];
	[_token, "result", _reason, _owner, _operationId, [_accepted, _towId, _cargoId, _ropeIds, _state]] call YFU_fnc_towAudit;
};

YFU_fnc_towRequestPlayer = {
	params ["_owner"];
	private _player = objNull;
	{if ((owner _x) isEqualTo _owner) exitWith {_player = _x;};} forEach allPlayers;
	_player
};

YFU_fnc_towHasRelationship = {
	params ["_object"];
	if (isNull _object) exitWith {false};
	(ropes _object) isNotEqualTo []
		|| {(ropesAttachedTo _object) isNotEqualTo []}
		|| {(ropeAttachedObjects _object) isNotEqualTo []}
		|| {!isNull (getTowParent _object)}
};

YFU_fnc_towClearActive = {
	params ["_token", "_operationId"];
	if (!isServer || {_token isNotEqualTo YFU_TOW_TOKEN}) exitWith {};
	private _all = call YFU_fnc_towOperations;
	private _tx = _all getOrDefault [_operationId, createHashMap];
	if !(_tx getOrDefault ["claimed", false]) exitWith {};
	private _tow = _tx getOrDefault ["tow", objNull];
	private _cargo = _tx getOrDefault ["cargo", objNull];
	private _claims = call YFU_fnc_towObjectClaims;
	{
		private _id = if (isNull _x) then {""} else {netId _x};
		if (_id isNotEqualTo "" && {(_claims getOrDefault [_id, ""]) isEqualTo _operationId}) then {
			_claims deleteAt _id;
		};
	} forEach [_tow, _cargo];
	if (!isNull _tow) then {_tow setVariable ["YFU_TOW_ACTIVE", nil, true];};
	if (!isNull _cargo) then {_cargo setVariable ["YFU_TOW_ACTIVE", nil, true];};
	_all deleteAt _operationId;
};

YFU_fnc_towFinalize = {
	params ["_token", "_operationId", "_resultOperationId", "_reason", "_owner", ["_publish", true]];
	if (!isServer || {_token isNotEqualTo YFU_TOW_TOKEN}) exitWith {false};
	private _all = call YFU_fnc_towOperations;
	private _tx = _all getOrDefault [_operationId, createHashMap];
	if !(_tx getOrDefault ["claimed", false]) exitWith {false};
	private _tow = _tx getOrDefault ["tow", objNull];
	private _cargo = _tx getOrDefault ["cargo", objNull];
	private _featureRopes = _tx getOrDefault ["ropes", []];
	private _ropeIds = _featureRopes select {!isNull _x} apply {netId _x};
	{if (!isNull _x) then {ropeDestroy _x;};} forEach _featureRopes;
	if (!isNull _cargo) then {[_cargo, objNull] call YFU_fnc_setTowParent;};
	[_token, _operationId] call YFU_fnc_towClearActive;
	if (_publish) then {
		[_token, _owner, _resultOperationId, true, _reason, _tow, _cargo, [], "detached"] call YFU_fnc_towPublishResult;
	};
	[_token, "finalize", _reason, _owner, _resultOperationId, [_operationId, if (isNull _tow) then {""} else {netId _tow}, if (isNull _cargo) then {""} else {netId _cargo}, _ropeIds]] call YFU_fnc_towAudit;
	true
};

YFU_fnc_towCreate = {
	params ["_token", "_tow", "_cargo"];
	if (!isServer || {_token isNotEqualTo YFU_TOW_TOKEN}) exitWith {[false, [], "authority"]};
	private _geometry = [_tow, _cargo] call YFU_fnc_resolveTowGeometry;
	private _towPoint = _geometry param [0, []];
	private _cargoPoints = _geometry param [1, []];
	if ((count _towPoint) isNotEqualTo 3 || {_cargoPoints isEqualTo []} || {(_cargoPoints findIf {(count _x) isNotEqualTo 3}) >= 0}) exitWith {
		[false, [], "geometry"]
	};
	private _created = [];
	{
		_created pushBack (ropeCreate [_tow, _towPoint, _cargo, _x, 5, ["RopeEnd", [0, 0, 1]], ["RopeEnd", [0, 0, 1]], "Spring1xRope"]);
	} forEach _cargoPoints;
	if ((count _created) isNotEqualTo (count _cargoPoints) || {(_created findIf {isNull _x}) >= 0}) exitWith {
		{if (!isNull _x) then {ropeDestroy _x;};} forEach _created;
		[false, [], "rope-create"]
	};
	[_cargo, _tow] call YFU_fnc_setTowParent;
	private _deadline = diag_tickTime + 2;
	waitUntil {
		uiSleep 0.02;
		((getTowParent _cargo) isEqualTo _tow && {_cargo in (ropeAttachedObjects _tow)})
			|| {diag_tickTime > _deadline}
	};
	if !((getTowParent _cargo) isEqualTo _tow && {_cargo in (ropeAttachedObjects _tow)}) exitWith {
		{if (!isNull _x) then {ropeDestroy _x;};} forEach _created;
		[_cargo, objNull] call YFU_fnc_setTowParent;
		[false, [], "relationship"]
	};
	[true, _created, "accepted"]
};

YFU_fnc_towMonitor = {
	params ["_token", "_operationId"];
	if (!isServer || {_token isNotEqualTo YFU_TOW_TOKEN}) exitWith {};
	[_operationId] spawn {
		params ["_operationId"];
		private _invalidSince = -1;
		private _done = false;
		while {!_done} do {
			uiSleep 0.1;
			private _all = call YFU_fnc_towOperations;
			private _tx = _all getOrDefault [_operationId, createHashMap];
			if !(_tx getOrDefault ["claimed", false]) then {
				_done = true;
			} else {
				private _tow = _tx getOrDefault ["tow", objNull];
				private _cargo = _tx getOrDefault ["cargo", objNull];
				private _featureRopes = _tx getOrDefault ["ropes", []];
				private _valid = !isNull _tow
					&& {!isNull _cargo}
					&& {_featureRopes isNotEqualTo []}
					&& {(_featureRopes findIf {isNull _x}) < 0}
					&& {_cargo in (ropeAttachedObjects _tow)}
					&& {(getTowParent _cargo) isEqualTo _tow};
				if (_valid) then {
					_invalidSince = -1;
				} else {
					if (_invalidSince < 0) then {_invalidSince = diag_tickTime;};
					if ((diag_tickTime - _invalidSince) >= 0.5) then {
						private _owner = _tx getOrDefault ["owner", 2];
						[YFU_TOW_TOKEN, _operationId, _operationId, "rope-lost", _owner, true] call YFU_fnc_towFinalize;
						_done = true;
					};
				};
			};
		};
	};
};

YFU_fnc_towReject = {
	params ["_owner", "_operationId", "_reason", "_tow", "_cargo"];
	[YFU_TOW_TOKEN, _owner, _operationId, false, _reason, _tow, _cargo, [], "rejected"] call YFU_fnc_towPublishResult;
	false
};

YFU_fnc_towRequestServer = {
	if (!isServer) exitWith {false};
	params [
		["_operationId", "", [""]],
		["_action", "", [""]],
		["_tow", objNull, [objNull]],
		["_cargo", objNull, [objNull]]
	];
	private _owner = remoteExecutedOwner;
	if (_owner isEqualTo 0) then {_owner = 2};
	private _requestKey = format ["%1#%2", _owner, _operationId];
	private _requests = localNamespace getVariable ["YFU_TOW_REQUESTS", createHashMap];
	private _now = diag_tickTime;
	{
		private _at = _requests getOrDefault [_x, _now];
		if ((_now - _at) > 300) then {_requests deleteAt _x;};
	} forEach keys _requests;
	if (_operationId isEqualTo "" || {!(_action in ["attach", "stow"])}) exitWith {
		[_owner, _operationId, "schema", _tow, _cargo] call YFU_fnc_towReject
	};
	if ((_requests getOrDefault [_requestKey, -1]) >= 0) exitWith {
		[_owner, _operationId, "duplicate", _tow, _cargo] call YFU_fnc_towReject
	};
	_requests set [_requestKey, _now];
	localNamespace setVariable ["YFU_TOW_REQUESTS", _requests];

	private _requester = [_owner] call YFU_fnc_towRequestPlayer;
	if (_owner <= 2 || {isNull _requester} || {!alive _requester}) exitWith {
		[_owner, _operationId, "requester", _tow, _cargo] call YFU_fnc_towReject
	};
	if (isNull _tow || {!alive _tow} || {!(_tow isKindOf "LandVehicle")}) exitWith {
		[_owner, _operationId, "tow-vehicle", _tow, _cargo] call YFU_fnc_towReject
	};
	if (_action isEqualTo "stow") exitWith {
		private _claims = call YFU_fnc_towObjectClaims;
		private _activeId = _claims getOrDefault [netId _tow, ""];
		private _all = call YFU_fnc_towOperations;
		private _tx = _all getOrDefault [_activeId, createHashMap];
		if (_activeId isEqualTo "" || {!(_tx getOrDefault ["claimed", false])} || {!((_tx getOrDefault ["tow", objNull]) isEqualTo _tow)} || {(_tx getOrDefault ["owner", -1]) isNotEqualTo _owner}) exitWith {
			[_owner, _operationId, "not-active", _tow, objNull] call YFU_fnc_towReject
		};
		[YFU_TOW_TOKEN, _activeId, _operationId, "stowed", _owner, true] call YFU_fnc_towFinalize
	};

	if ((_requester distance _tow) > YFU_TOW_REQUESTER_RANGE) exitWith {
		[_owner, _operationId, "requester-range", _tow, _cargo] call YFU_fnc_towReject
	};

	if (isNull _cargo || {!alive _cargo} || {!(_cargo isKindOf "LandVehicle")} || {_cargo isEqualTo _tow}) exitWith {
		[_owner, _operationId, "cargo-vehicle", _tow, _cargo] call YFU_fnc_towReject
	};
	if ((_tow distance _cargo) > YFU_TOW_PAIR_RANGE) exitWith {
		[_owner, _operationId, "pair-range", _tow, _cargo] call YFU_fnc_towReject
	};
	if ((abs speed _tow) > YFU_TOW_MAX_SPEED || {(abs speed _cargo) > YFU_TOW_MAX_SPEED}) exitWith {
		[_owner, _operationId, "moving", _tow, _cargo] call YFU_fnc_towReject
	};
	private _claims = call YFU_fnc_towObjectClaims;
	if ((_claims getOrDefault [netId _tow, ""]) isNotEqualTo "" || {(_claims getOrDefault [netId _cargo, ""]) isNotEqualTo ""}) exitWith {
		[_owner, _operationId, "active-conflict", _tow, _cargo] call YFU_fnc_towReject
	};
	if ([_tow] call YFU_fnc_towHasRelationship || {[_cargo] call YFU_fnc_towHasRelationship}) exitWith {
		[_owner, _operationId, "rope-conflict", _tow, _cargo] call YFU_fnc_towReject
	};

	private _all = call YFU_fnc_towOperations;
	private _tx = createHashMapFromArray [
		["claimed", true],
		["owner", _owner],
		["tow", _tow],
		["cargo", _cargo],
		["ropes", []],
		["state", "creating"],
		["createdAt", diag_tickTime]
	];
	_all set [_operationId, _tx];
	_claims set [netId _tow, _operationId];
	_claims set [netId _cargo, _operationId];
	[_operationId, _owner] spawn {
		params ["_operationId", "_owner"];
		private _all = call YFU_fnc_towOperations;
		private _tx = _all getOrDefault [_operationId, createHashMap];
		private _tow = _tx getOrDefault ["tow", objNull];
		private _cargo = _tx getOrDefault ["cargo", objNull];
		private _created = [YFU_TOW_TOKEN, _tow, _cargo] call YFU_fnc_towCreate;
		if !(_created # 0) exitWith {
			private _reason = _created # 2;
			[YFU_TOW_TOKEN, _operationId] call YFU_fnc_towClearActive;
			[YFU_TOW_TOKEN, _owner, _operationId, false, _reason, _tow, _cargo, [], "rejected"] call YFU_fnc_towPublishResult;
		};
		private _ropes = _created # 1;
		private _all = call YFU_fnc_towOperations;
		private _tx = _all getOrDefault [_operationId, createHashMap];
		_tx set ["ropes", _ropes];
		_tx set ["state", "active"];
		_all set [_operationId, _tx];
		private _active = [_operationId, netId _tow, netId _cargo, _ropes apply {netId _x}];
		_tow setVariable ["YFU_TOW_ACTIVE", _active, true];
		_cargo setVariable ["YFU_TOW_ACTIVE", _active, true];
		[YFU_TOW_TOKEN, _owner, _operationId, true, "accepted", _tow, _cargo, _ropes, "active"] call YFU_fnc_towPublishResult;
		[YFU_TOW_TOKEN, "activate", "accepted", _owner, _operationId, [_active, local _tow, local _cargo, owner _tow, owner _cargo]] call YFU_fnc_towAudit;
		[YFU_TOW_TOKEN, _operationId] call YFU_fnc_towMonitor;
	};
	true
};

YFU_fnc_towOperationId = {
	params [["_prefix", "tow"]];
	format ["%1-%2-%3-%4", _prefix, clientOwner, floor (diag_tickTime * 1000), floor random 1000000]
};

YFU_fnc_towRequestAttach = {
	params ["_tow", "_cargo", ["_operationId", ""]];
	if (_operationId isEqualTo "") then {_operationId = ["tow"] call YFU_fnc_towOperationId;};
	[_operationId, "attach", _tow, _cargo] remoteExecCall ["YFU_fnc_towRequestServer", 2];
	_operationId
};

YFU_fnc_towRequestStow = {
	params ["_tow", ["_operationId", ""]];
	if (_operationId isEqualTo "") then {_operationId = ["stow"] call YFU_fnc_towOperationId;};
	[_operationId, "stow", _tow, objNull] remoteExecCall ["YFU_fnc_towRequestServer", 2];
	_operationId
};
