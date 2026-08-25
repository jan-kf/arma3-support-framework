/*
Fabrication is consequential: it creates real objects out of nothing.
The client owns the terminal and the queue; this file owns the decision.

There are two client-facing operations: submit an order and discard that
caller's own order. Every other consequential function requires the server's
unpublished capability token, so reaching a globally named SQF function does
not grant authority.

Identity is taken from the transport (remoteExecutedOwner), never from the
payload, and every piece of transaction state is keyed by owner#request so two
owners cannot collide on a client-generated id.
*/

YFU_FABRICATOR_ORDER_RANGE = 25;
YFU_FABRICATOR_MAX_ORDER = 30;
YFU_FABRICATOR_RESULT_TTL = 120;
YFU_FABRICATOR_BUILD_DEADLINE = 60;
YFU_FABRICATOR_AUDIT_LIMIT = 128;

// remoteExecutedOwner is reliable at an entry point but NOT inside a script the
// entry point spawns: measured on this build it stays non-zero there, so using it
// as an internal guard blocks the server's own worker. Internal helpers are
// instead gated on a secret this machine generates at init and never publishes.
// A client compiles the same file and gets its own unrelated value, so a
// remote-executed call carries the wrong secret and does nothing.
YFU_FABRICATOR_TOKEN = format ["yfu-%1-%2-%3", diag_tickTime, random 1e9, random 1e9];

// A bounded server-private receipt ledger. Negative controls must prove that
// their stimulus reached the authority boundary and was rejected; absence of a
// result is not evidence. Never publish this ledger or accept its token from a
// payload.
YFU_fnc_fabricatorAudit = {
	params ["_token", "_operation", "_decision", ["_owner", -1], ["_detail", ""]];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {};
	private _rows = missionNamespace getVariable ["YFU_fabricatorAudit", []];
	_rows pushBack [diag_tickTime, _operation, _decision, _owner, _detail];
	if ((count _rows) > YFU_FABRICATOR_AUDIT_LIMIT) then {
		_rows deleteRange [0, (count _rows) - YFU_FABRICATOR_AUDIT_LIMIT];
	};
	missionNamespace setVariable ["YFU_fabricatorAudit", _rows, false];
};

YFU_fnc_fabricatorTxId = {
	params ["_owner", "_requestId"];
	format ["%1#%2", _owner, _requestId]
};

YFU_fnc_fabricatorResultKey = {
	params ["_txId"];
	format ["YFU_ORDER_RESULT_%1", _txId]
};

YFU_fnc_fabricatorTransactions = {
	private _all = missionNamespace getVariable ["YFU_fabricatorTx", createHashMap];
	missionNamespace setVariable ["YFU_fabricatorTx", _all];
	_all
};

// Everything this transaction created, so a finalizer can undo exactly its own
// work and nothing else.
YFU_fnc_fabricatorTrack = {
	params ["_token", "_txId", "_objects"];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {};
	private _all = call YFU_fnc_fabricatorTransactions;
	private _tx = _all getOrDefault [_txId, createHashMap];
	private _created = _tx getOrDefault ["created", []];
	{
		if (!isNull _x) then {
			private _id = netId _x;
			if !(_id in _created) then {_created pushBack _id;};
		};
	} forEach _objects;
	_tx set ["created", _created];
	_all set [_txId, _tx];
	count _created
};

YFU_fnc_fabricatorTxState = {
	params ["_txId"];
	private _all = call YFU_fnc_fabricatorTransactions;
	private _tx = _all getOrDefault [_txId, createHashMap];
	_tx getOrDefault ["state", "unknown"]
};

YFU_fnc_fabricatorSetState = {
	params ["_token", "_txId", "_state"];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {};
	private _all = call YFU_fnc_fabricatorTransactions;
	private _tx = _all getOrDefault [_txId, createHashMap];
	_tx set ["state", _state];
	_all set [_txId, _tx];
	_state
};

// Delete exactly the objects this transaction created. Scoped by construction:
// it can only reach net ids the transaction itself recorded.
YFU_fnc_fabricatorFinalize = {
	params ["_token", "_txId", ["_state", "finalized"]];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {0};
	private _all = call YFU_fnc_fabricatorTransactions;
	private _tx = _all getOrDefault [_txId, createHashMap];
	private _created = _tx getOrDefault ["created", []];
	private _removed = 0;
	{
		private _object = objectFromNetId _x;
		if (!isNull _object) then {
			deleteVehicle _object;
			_removed = _removed + 1;
		};
	} forEach _created;
	_tx set ["created", []];
	_tx set ["state", _state];
	_all set [_txId, _tx];
	_removed
};

// Retire claim, result and ledger together so no transaction state accumulates
// and no stale entry can later resolve a recycled net id.
YFU_fnc_fabricatorRetire = {
	params ["_token", "_txId", ["_ttl", YFU_FABRICATOR_RESULT_TTL]];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {};
	[_txId, _ttl max 0] spawn {
		params ["_txId", "_ttl"];
		uiSleep _ttl;
		missionNamespace setVariable [[_txId] call YFU_fnc_fabricatorResultKey, nil, true];
		private _all = call YFU_fnc_fabricatorTransactions;
		_all deleteAt _txId;
		[YFU_FABRICATOR_TOKEN, "retire", "completed", 2, _txId] call YFU_fnc_fabricatorAudit;
	};
};

YFU_fnc_fabricatorPublishResult = {
	params ["_token", "_txId", "_ok", "_reason", ["_singleId", ""], ["_containerIds", []], ["_positions", []]];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {""};
	// A terminal result is written once. A duplicate or late writer must not be
	// able to overwrite the outcome an in-progress transaction already reached.
	private _key = [_txId] call YFU_fnc_fabricatorResultKey;
	private _state = [_txId] call YFU_fnc_fabricatorTxState;
	if (_state in ["delivered", "refused", "finalized"]) exitWith {_state};
	missionNamespace setVariable [_key, [_txId, _ok, _reason, _singleId, _containerIds, _positions], true];
	[YFU_FABRICATOR_TOKEN, _txId, if (_ok) then {"delivered"} else {"refused"}] call YFU_fnc_fabricatorSetState;
	[YFU_FABRICATOR_TOKEN, _txId] call YFU_fnc_fabricatorRetire;
	_reason
};

YFU_fnc_fabricatorRefuse = {
	params ["_token", "_txId", "_reason"];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {""};
	// Clean up under a non-terminal state: marking it finalized here would trip
	// the write-once guard below and swallow the refusal it is meant to publish.
	[YFU_FABRICATOR_TOKEN, _txId, "cleaning"] call YFU_fnc_fabricatorFinalize;
	[YFU_FABRICATOR_TOKEN, _txId, false, _reason] call YFU_fnc_fabricatorPublishResult;
};

// The catalogue is a template source: fabricating never consumes it.
YFU_fnc_fabricatorCatalogue = {
	if (isServer) exitWith {+(localNamespace getVariable ["YFU_MODULE_CATALOGUE", []])};
	private _mirror = missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", []];
	if (_mirror isNotEqualTo []) exitWith {+_mirror};
	private _storage = missionNamespace getVariable ["YOSHI_VIRTUAL_STORAGE", objNull];
	if (isNull _storage) exitWith {[]};
	synchronizedObjects _storage
};

YFU_fnc_fabricatorStations = {
	if (isServer) exitWith {+(localNamespace getVariable ["YFU_MODULE_STATIONS", []])};
	private _mirror = missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", []];
	if (_mirror isNotEqualTo []) exitWith {+_mirror};
	private _logic = missionNamespace getVariable ["YOSHI_FABRICATOR", objNull];
	if (isNull _logic) exitWith {[]};
	synchronizedObjects _logic
};

// Vigil owns which aircraft may carry a drop. Ask its authoritative validator;
// do not reinterpret a registry record in Field Utilities.
YFU_fnc_fabricatorAirAssetAuthorized = {
	params ["_aircraft", "_requester"];
	if (isNull _aircraft || {isNull _requester}) exitWith {false};
	if (isNil "YSF_fwValidateLogisticsAsset") exitWith {false};
	private _verdict = [_aircraft, _requester] call YSF_fwValidateLogisticsAsset;
	(_verdict isEqualType []) && {(count _verdict) >= 1} && {(_verdict # 0) isEqualTo true}
};

// Complete schema check, run before anything is claimed, scheduled or created.
// Returns "" when the payload is well formed, otherwise the refusal reason.
YFU_fnc_fabricatorValidateRequest = {
	params [["_requestId", nil], ["_stationId", nil], ["_entries", nil], ["_isAirdrop", nil]];
	if (isNil "_requestId" || {!(_requestId isEqualType "")} || {_requestId isEqualTo ""}) exitWith {"malformed-request-id"};
	if (isNil "_stationId" || {!(_stationId isEqualType "")}) exitWith {"malformed-station"};
	if (isNil "_isAirdrop" || {!(_isAirdrop isEqualType false)}) exitWith {"malformed-mode"};
	if (isNil "_entries" || {!(_entries isEqualType [])} || {_entries isEqualTo []}) exitWith {"malformed-entries"};
	if ((count _entries) > YFU_FABRICATOR_MAX_ORDER) exitWith {"too-large"};
	private _verdict = "";
	private _total = 0;
	{
		if (_verdict isEqualTo "") then {
			if (!(_x isEqualType []) || {(count _x) < 2}) then {
				_verdict = "malformed-entries";
			} else {
				private _ref = _x # 0;
				private _quantity = _x # 1;
				if (!(_ref isEqualType "") || {_ref isEqualTo ""}) then {
					_verdict = "malformed-entries";
				} else {
					if (!(_quantity isEqualType 0) || {!finite _quantity} || {_quantity isNotEqualTo (floor _quantity)} || {_quantity <= 0}) then {
						_verdict = "malformed-quantity";
					} else {
						_total = _total + _quantity;
					};
				};
			};
		};
	} forEach _entries;
	if (_verdict isNotEqualTo "") exitWith {_verdict};
	if (_total > YFU_FABRICATOR_MAX_ORDER) exitWith {"too-large"};
	""
};

// The one endpoint a client may call.
YFU_fnc_fabricateOrder = {
	if (!isServer) exitWith {};
	private _owner = remoteExecutedOwner;
	// A local call is the server asking on its own behalf.
	if (_owner isEqualTo 0) then {_owner = 2};
	[YFU_FABRICATOR_TOKEN, _this, _owner] call YFU_fnc_fabricatorAccept;
};

YFU_fnc_fabricatorAccept = {
	if (!isServer) exitWith {};
	params ["_token", "_request", "_owner"];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {
		[YFU_FABRICATOR_TOKEN, "accept", "token-rejected", remoteExecutedOwner, str _owner] call YFU_fnc_fabricatorAudit;
		"unauthorized"
	};
	if !(_request isEqualType []) exitWith {};

	private _requestId = _request param [0, nil];
	private _stationId = _request param [1, nil];
	private _entries = _request param [2, nil];
	private _isAirdrop = _request param [3, false];

	// Schema first: a malformed payload is refused as a product decision, never
	// left to raise an SQF error somewhere downstream.
	private _schema = [_requestId, _stationId, _entries, _isAirdrop] call YFU_fnc_fabricatorValidateRequest;
	if (_schema isNotEqualTo "") exitWith {
		if (_requestId isEqualType "" && {_requestId isNotEqualTo ""}) then {
			private _badTx = [_owner, _requestId] call YFU_fnc_fabricatorTxId;
			[YFU_FABRICATOR_TOKEN, _badTx, false, _schema] call YFU_fnc_fabricatorPublishResult;
		};
		_schema
	};

	private _txId = [_owner, _requestId] call YFU_fnc_fabricatorTxId;
	private _all = call YFU_fnc_fabricatorTransactions;
	if (_all getOrDefault [_txId, createHashMap] getOrDefault ["claimed", false]) exitWith {
		[YFU_FABRICATOR_TOKEN, "order", "replay-rejected", _owner, _txId] call YFU_fnc_fabricatorAudit;
		// The original transaction keeps its result; this duplicate gets nothing.
		"replay"
	};
	private _tx = createHashMap;
	_tx set ["claimed", true];
	_tx set ["owner", _owner];
	_tx set ["state", "claimed"];
	_tx set ["created", []];
	_all set [_txId, _tx];
	[YFU_FABRICATOR_TOKEN, "order", "accepted", _owner, _txId] call YFU_fnc_fabricatorAudit;

	private _worker = [YFU_FABRICATOR_TOKEN, _txId, _stationId, _entries, _isAirdrop, _owner] spawn YFU_fnc_fabricateOrderWorker;
	// Keep the exact worker with the transaction. Both timeout and an explicit
	// owner cancellation must stop it before rolling back what it created.
	_tx set ["worker", _worker];
	_all set [_txId, _tx];

	// A durable finalizer: if the worker never reaches a terminal state - an
	// unexpected script error, a stall, a failure after objects exist - this
	// deletes exactly what the transaction created and records the refusal.
	[_txId, _worker, _owner] spawn {
		params ["_txId", "_worker", "_owner"];
		uiSleep YFU_FABRICATOR_BUILD_DEADLINE;
		private _all = call YFU_fnc_fabricatorTransactions;
		private _tx = _all getOrDefault [_txId, createHashMap];
		// A retired transaction is already complete. Do not resurrect it merely
		// because its state now correctly reads as unknown.
		if ((_tx getOrDefault ["claimed", false]) && {!(([_txId] call YFU_fnc_fabricatorTxState) in ["delivered", "refused", "finalized"])}) then {
			if (!scriptDone _worker) then {
				terminate _worker;
				[YFU_FABRICATOR_TOKEN, "watchdog", "worker-terminated", _owner, _txId] call YFU_fnc_fabricatorAudit;
			};
			[YFU_FABRICATOR_TOKEN, _txId, "abandoned"] call YFU_fnc_fabricatorRefuse;
		};
	};
	"accepted"
};

YFU_fnc_fabricateOrderWorker = {
	if (!isServer) exitWith {};
	params ["_token", "_txId", "_stationId", "_entries", "_isAirdrop", "_owner"];
	if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith {
		[YFU_FABRICATOR_TOKEN, "worker", "token-rejected", remoteExecutedOwner, _txId] call YFU_fnc_fabricatorAudit;
	};

	[YFU_FABRICATOR_TOKEN, _txId, "building"] call YFU_fnc_fabricatorSetState;

	private _caller = objNull;
	{
		if ((owner _x) isEqualTo _owner) exitWith {_caller = _x};
	} forEach allPlayers;
	private _station = objectFromNetId _stationId;

	if (isNull _caller || {!alive _caller}) exitWith {
		[YFU_FABRICATOR_TOKEN, _txId, "caller"] call YFU_fnc_fabricatorRefuse;
	};

	private _catalogue = call YFU_fnc_fabricatorCatalogue;
	if (_catalogue isEqualTo []) exitWith {
		[YFU_FABRICATOR_TOKEN, _txId, "no-storage"] call YFU_fnc_fabricatorRefuse;
	};

	// `exitWith` inside a `then` block exits only that block, so the verdict is
	// carried out rather than returned from inside the branch.
	private _stationVerdict = "";
	if (_isAirdrop) then {
		// Airdrop is not a mode a client may simply select. Vigil must validate
		// this exact requester/aircraft pair as a current logistics capability.
		if !([_station, _caller] call YFU_fnc_fabricatorAirAssetAuthorized) then {
			_stationVerdict = "airdrop-unauthorized";
		};
	} else {
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
		[YFU_FABRICATOR_TOKEN, _txId, _stationVerdict] call YFU_fnc_fabricatorRefuse;
	};

	private _sources = [];
	private _rejected = false;
	{
		private _source = objectFromNetId (_x # 0);
		if (isNull _source || {!(_source in _catalogue)}) then {
			_rejected = true;
		} else {
			for "_i" from 1 to (_x # 1) do {_sources pushBack _source;};
		};
	} forEach _entries;

	if (_rejected) exitWith {
		[YFU_FABRICATOR_TOKEN, _txId, "unregistered"] call YFU_fnc_fabricatorRefuse;
	};

	private _total = count _sources;
	// Assembled out of sight but on the surface: an object created inside terrain
	// never initialises a real physical state and never recovers one.
	private _stageBase = getPosATL _caller;
	private _clones = [];
	{
		private _stage = _stageBase vectorAdd [(_forEachIndex mod 5) * 1.5, floor (_forEachIndex / 5) * 1.5, 0];
		private _clone = [objNull, _caller, [_station, _x, _stage], {
			params ["_created", "_txId"];
			[YFU_FABRICATOR_TOKEN, _txId, [_created]] call YFU_fnc_fabricatorTrack;
		}, _txId] call YOSHI_SPAWN_SAVED_ITEM_ACTION;
		if (!isNull _clone) then {
			_clone hideObjectGlobal true;
			_clones pushBack _clone;
			// Tracked as it is created, so a failure at any later point - including
			// one this code does not anticipate - still has something to undo.
		};
	} forEach _sources;
	uiSleep 0.25;

	if ((count _clones) isNotEqualTo _total) exitWith {
		[YFU_FABRICATOR_TOKEN, _txId, "clone-failed"] call YFU_fnc_fabricatorRefuse;
	};

	if (!_isAirdrop && {_total isEqualTo 1}) exitWith {
		private _single = _clones # 0;
		private _drop = [getPosATL _caller, 3, 0] call YFU_assetsFindSafeDropPos;
		_single setPosATL _drop;
		_single setVectorUp [0, 0, 1];
		_single hideObjectGlobal false;
		uiSleep 0.25;
		[_single, 10, 1] call YOSHI_capDeliveryMass;
		[YFU_FABRICATOR_TOKEN, _txId, true, "single", netId _single, [], [_drop]] call YFU_fnc_fabricatorPublishResult;
	};

	{
		_x setVectorUp [0, 0, 1];
		_x setVelocity [0, 0, 0];
	} forEach _clones;
	uiSleep 0.1;

	private _pack = [_clones, [], true, true, 2.0, [0,0,0], 0, true, 4, false, {
		params ["_created", "_txId"];
		[YFU_FABRICATOR_TOKEN, _txId, [_created]] call YFU_fnc_fabricatorTrack;
	}, _txId] call YOSHI_spawnContainersNearObjectsAndPackMulti;
	private _packOk = _pack # 0;
	private _containers = _pack # 1;

	if (!_packOk || {_containers isEqualTo []}) exitWith {
		[YFU_FABRICATOR_TOKEN, _txId, "unpackable"] call YFU_fnc_fabricatorRefuse;
	};

	if (_isAirdrop) exitWith {
		{_x hideObjectGlobal false;} forEach (_clones + _containers);
		uiSleep 0.25;
		{[_x] call YOSHI_capDeliveryMass;} forEach (_clones + _containers);
		[YFU_FABRICATOR_TOKEN, _txId, true, "airdrop", "", _containers apply {netId _x}, []] call YFU_fnc_fabricatorPublishResult;
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

	[YFU_FABRICATOR_TOKEN, _txId, true, "multi", "", _containers apply {netId _x}, _positions] call YFU_fnc_fabricatorPublishResult;
};

// A client may only discard its own transaction: the id is rebuilt from the
// owner the transport reports, so naming someone else's request reaches nothing.
YFU_fnc_fabricatorDiscardOrder = {
	if (!isServer) exitWith {0};
	params [["_requestId", ""]];
	if !(_requestId isEqualType "") exitWith {0};
	private _owner = remoteExecutedOwner;
	if (_owner isEqualTo 0) then {_owner = 2};
	private _txId = [_owner, _requestId] call YFU_fnc_fabricatorTxId;
	private _all = call YFU_fnc_fabricatorTransactions;
	private _tx = _all getOrDefault [_txId, createHashMap];
	if !(_tx getOrDefault ["claimed", false]) exitWith {
		[YFU_FABRICATOR_TOKEN, "discard", "owner-miss-rejected", _owner, _txId] call YFU_fnc_fabricatorAudit;
		0
	};
	private _worker = _tx getOrDefault ["worker", scriptNull];
	if (_worker isNotEqualTo scriptNull && {!scriptDone _worker}) then {
		terminate _worker;
		[YFU_FABRICATOR_TOKEN, "discard", "worker-terminated", _owner, _txId] call YFU_fnc_fabricatorAudit;
	};
	private _removed = [YFU_FABRICATOR_TOKEN, _txId] call YFU_fnc_fabricatorFinalize;
	[YFU_FABRICATOR_TOKEN, "discard", "accepted", _owner, _txId] call YFU_fnc_fabricatorAudit;
	[YFU_FABRICATOR_TOKEN, _txId] call YFU_fnc_fabricatorRetire;
	_removed
};
