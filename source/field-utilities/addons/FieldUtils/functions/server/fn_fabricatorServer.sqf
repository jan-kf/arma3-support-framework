/*
Fabrication is consequential: it creates real objects out of nothing.
The client owns the terminal and the queue; this file owns the decision.
A client asks, the server checks the ask against the registered catalogue and
station, and only the server ever creates anything.
*/

// A player must be at the station they are ordering from. Airdrop orders come
// from Vigil's aircraft context instead and are authorized by Vigil.
YFU_FABRICATOR_ORDER_RANGE = 25;
YFU_FABRICATOR_MAX_ORDER = 30;
YFU_FABRICATOR_RESULT_TTL = 120;

YFU_fnc_fabricatorResultKey = {
	params ["_requestId"];
	format ["YFU_ORDER_RESULT_%1", _requestId]
};

// What the server built for one order, so the server can undo its own work if a
// downstream handoff refuses it. The client never deletes a fabricated object.
YFU_fnc_fabricatorRecordOrder = {
	params ["_requestId", "_objects"];
	private _ledger = missionNamespace getVariable ["YFU_fabricatorOrders", createHashMap];
	_ledger set [_requestId, _objects apply {netId _x}];
	missionNamespace setVariable ["YFU_fabricatorOrders", _ledger];
};

YFU_fnc_fabricatorDiscardOrder = {
	params [["_requestId", ""]];
	if (!isServer) exitWith {};
	private _ledger = missionNamespace getVariable ["YFU_fabricatorOrders", createHashMap];
	private _ids = _ledger getOrDefault [_requestId, []];
	{
		private _object = objectFromNetId _x;
		if (!isNull _object) then {deleteVehicle _object;};
	} forEach _ids;
	_ledger deleteAt _requestId;
	missionNamespace setVariable ["YFU_fabricatorOrders", _ledger];
	count _ids
};

YFU_fnc_fabricatorPublishResult = {
	params ["_requestId", "_ok", "_reason", ["_singleId", ""], ["_containerIds", []], ["_positions", []]];
	private _key = [_requestId] call YFU_fnc_fabricatorResultKey;
	missionNamespace setVariable [_key, [_requestId, _ok, _reason, _singleId, _containerIds, _positions], true];
	// A result is a handshake, not a record. Drop it once the client has had
	// every chance to read it so the namespace does not grow for the mission.
	[_key] spawn {
		params ["_key"];
		uiSleep YFU_FABRICATOR_RESULT_TTL;
		missionNamespace setVariable [_key, nil, true];
	};
	_reason
};

// The catalogue is a template source: fabricating never consumes it.
YFU_fnc_fabricatorCatalogue = {
	private _storage = missionNamespace getVariable ["YOSHI_VIRTUAL_STORAGE", objNull];
	if (isNull _storage) exitWith {[]};
	synchronizedObjects _storage
};

YFU_fnc_fabricatorStations = {
	private _logic = missionNamespace getVariable ["YOSHI_FABRICATOR", objNull];
	if (isNull _logic) exitWith {[]};
	synchronizedObjects _logic
};

// A remoteExecCall arrives unscheduled, where uiSleep does nothing at all: a
// freshly created object would never get the frame it needs to report a real
// mass, and the delivery cap would silently never apply. Assemble every order in
// a scheduled script so waiting actually waits.
YFU_fnc_fabricateOrder = {
	if (!isServer) exitWith {};
	if (canSuspend) then {
		_this call YFU_fnc_fabricateOrderWorker;
	} else {
		_this spawn YFU_fnc_fabricateOrderWorker;
	};
};

YFU_fnc_fabricateOrderWorker = {
	params [["_requestId", ""], ["_callerId", ""], ["_stationId", ""], ["_entries", []], ["_isAirdrop", false]];
	if (!isServer) exitWith {};
	if (_requestId isEqualTo "") exitWith {};

	private _caller = objectFromNetId _callerId;
	private _station = objectFromNetId _stationId;

	if (isNull _caller || {!alive _caller}) exitWith {
		[_requestId, false, "caller"] call YFU_fnc_fabricatorPublishResult;
	};

	private _catalogue = call YFU_fnc_fabricatorCatalogue;
	if (_catalogue isEqualTo []) exitWith {
		[_requestId, false, "no-storage"] call YFU_fnc_fabricatorPublishResult;
	};

	// Airdrop orders name Vigil's aircraft, not a registered station, and Vigil
	// has already authorized them. Local orders must name a real station and the
	// player must actually be standing at it.
	// `exitWith` inside a `then` block exits only that block, so the station
	// verdict is carried out rather than returned from inside the branch.
	private _stationVerdict = "";
	if (!_isAirdrop) then {
		private _stations = call YFU_fnc_fabricatorStations;
		if (isNull _station || {!(_station in _stations)}) then {
			_stationVerdict = "no-station";
		} else {
			if ((_caller distance _station) > YFU_FABRICATOR_ORDER_RANGE) then {
				_stationVerdict = "out-of-range";
			};
		};
	};
	if (_stationVerdict isNotEqualTo "") exitWith {
		[_requestId, false, _stationVerdict] call YFU_fnc_fabricatorPublishResult;
	};

	// Expand the request against the catalogue. An entry naming something that
	// is not registered is refused outright rather than quietly dropped.
	private _sources = [];
	private _rejected = false;
	{
		private _source = objectFromNetId (_x param [0, ""]);
		private _count = _x param [1, 0];
		if (isNull _source || {!(_source in _catalogue)} || {_count <= 0}) then {
			_rejected = true;
		} else {
			for "_i" from 1 to _count do {_sources pushBack _source;};
		};
	} forEach _entries;

	if (_rejected) exitWith {
		[_requestId, false, "unregistered"] call YFU_fnc_fabricatorPublishResult;
	};
	if (_sources isEqualTo []) exitWith {
		[_requestId, false, "empty"] call YFU_fnc_fabricatorPublishResult;
	};
	if ((count _sources) > YFU_FABRICATOR_MAX_ORDER) exitWith {
		[_requestId, false, "too-large"] call YFU_fnc_fabricatorPublishResult;
	};

	private _total = count _sources;
	// Staging underground hides the order while it is being assembled, but an
	// object created inside terrain never initialises a real mass and never
	// recovers one, which silently defeats the delivery mass cap. Build on the
	// surface where the object is valid and hide it instead.
	private _stageBase = getPosATL _caller;
	private _clones = [];
	{
		private _stage = _stageBase vectorAdd [(_forEachIndex mod 5) * 1.5, floor (_forEachIndex / 5) * 1.5, 0];
		private _clone = [objNull, _caller, [_station, _x, _stage]] call YOSHI_SPAWN_SAVED_ITEM_ACTION;
		if (!isNull _clone) then {
			_clone hideObjectGlobal true;
			_clones pushBack _clone;
		};
	} forEach _sources;
	uiSleep 0.25;

	// Orders are atomic. Anything short of the whole order produces nothing.
	private _abort = {
		params ["_objects"];
		{if (!isNull _x) then {deleteVehicle _x;};} forEach _objects;
	};

	if ((count _clones) isNotEqualTo _total) exitWith {
		[_clones] call _abort;
		[_requestId, false, "clone-failed"] call YFU_fnc_fabricatorPublishResult;
	};

	if (!_isAirdrop && {_total isEqualTo 1}) exitWith {
		private _single = _clones # 0;
		private _drop = [getPosATL _caller, 3, 0] call YFU_assetsFindSafeDropPos;
		_single setPosATL _drop;
		_single setVectorUp [0, 0, 1];
		_single hideObjectGlobal false;
		uiSleep 0.25;
		[_single] call YOSHI_capDeliveryMass;
		[_requestId, [_single]] call YFU_fnc_fabricatorRecordOrder;
		[_requestId, true, "single", netId _single, [], [_drop]] call YFU_fnc_fabricatorPublishResult;
	};

	{
		_x setVectorUp [0, 0, 1];
		_x setVelocity [0, 0, 0];
	} forEach _clones;
	uiSleep 0.1;

	private _pack = [_clones] call YOSHI_spawnContainersNearObjectsAndPackMulti;
	private _packOk = _pack # 0;
	private _containers = _pack # 1;

	if (!_packOk || {_containers isEqualTo []}) exitWith {
		[_clones] call _abort;
		[_containers] call _abort;
		[_requestId, false, "unpackable"] call YFU_fnc_fabricatorPublishResult;
	};

	if (_isAirdrop) exitWith {
		{_x hideObjectGlobal false;} forEach (_clones + _containers);
		uiSleep 0.25;
		{[_x] call YOSHI_capDeliveryMass;} forEach (_clones + _containers);
		[_requestId, _containers + _clones] call YFU_fnc_fabricatorRecordOrder;
		[_requestId, true, "airdrop", "", _containers apply {netId _x}, []] call YFU_fnc_fabricatorPublishResult;
	};

	private _centre = getPosATL _caller;
	private _positions = [];
	{
		private _drop = [_centre, 4, _forEachIndex] call YFU_assetsFindSafeDropPos;
		_x setPosATL _drop;
		_x setVectorUp [0, 0, 1];
		_positions pushBack _drop;
	} forEach _containers;
	{_x hideObjectGlobal false;} forEach (_clones + _containers);
	uiSleep 0.25;
	{[_x] call YOSHI_capDeliveryMass;} forEach (_clones + _containers);

	[_requestId, _containers + _clones] call YFU_fnc_fabricatorRecordOrder;
	[_requestId, true, "multi", "", _containers apply {netId _x}, _positions] call YFU_fnc_fabricatorPublishResult;
};
