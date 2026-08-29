// Counter Battery Radar
/*
Lord, set a watch before my mouth,
keep guard over the door of my lips.
(Psalm 141:3)

And over our camp, keep watch through the night.
Amen.
*/

// One authoritative row per physical strike observation. Presentation groups
// are derived on each client's map and never become storage containers.
YOSHI_CB_UNCERTAINTY_RADIUS = 100;
YOSHI_CB_VISUAL_LINK_FRACTION = 0.045;
YOSHI_CB_ARMING_DIST = 5;
YOSHI_CB_MEMBER_TTL = 2.0;

YOSHI_CB_queue = [];
YOSHI_CB_observations = [];
YOSHI_CB_visualClusters = [];
YOSHI_CB_renderMarkers = [];
YOSHI_CB_lastRenderSignature = "";
YOSHI_CB_markerIndex = 0;
YOSHI_CB_airborneShells = [];

YOSHI_CB_PREDICT_STEP = 0.1;
YOSHI_CB_PREDICT_MAX_TIME = 180;
YOSHI_CB_LOCAL_UID_COUNTER = 0;
YOSHI_CB_LOCAL_EH_ID = -1;

if (isNil { missionNamespace getVariable "YOSHI_CBR_ENABLED" }) then {
	if (isServer) then {
		missionNamespace setVariable ["YOSHI_CBR_ENABLED", false, true];
	} else {
		missionNamespace setVariable ["YOSHI_CBR_ENABLED", false];
	};
};
if (isNil { missionNamespace getVariable "YOSHI_CBR_EH_ID" }) then {
	missionNamespace setVariable ["YOSHI_CBR_EH_ID", -1];
};
if (isNil { missionNamespace getVariable "YOSHI_CBR_MANAGER_THREAD" }) then {
	missionNamespace setVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull];
};
if (isNil { missionNamespace getVariable "YOSHI_CBR_ORIGIN_THREAD" }) then {
	missionNamespace setVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull];
};
if (isNil { missionNamespace getVariable "YOSHI_CBR_OBSERVATIONS" }) then {
	missionNamespace setVariable ["YOSHI_CBR_OBSERVATIONS", []];
};

YOSHI_CB_enqueue = {
	params ["_uid", "_impactPos", "_eta", ["_provenance", []]];
	private _exp = time + _eta + 1;
	YOSHI_CB_queue pushBack [_uid, _impactPos, _eta, _exp, time, +_provenance];
};

YOSHI_CB_publishObservations = {
	if (!isServer) exitWith {};
	missionNamespace setVariable ["YOSHI_CBR_OBSERVATIONS", +YOSHI_CB_observations, true];
};

YOSHI_CB_prune = {
	private _before = count YOSHI_CB_observations;
	YOSHI_CB_observations = YOSHI_CB_observations select {(_x select 6) > time};
	if ((count YOSHI_CB_observations) != _before) then {call YOSHI_CB_publishObservations};
};

YOSHI_CB_processQueue = {
	while {(count YOSHI_CB_queue) > 0} do {
		private _m = YOSHI_CB_queue deleteAt 0;

		private _id = _m select 0;
		private _pos = _m select 1;
		private _eta = _m select 2;
		private _exp = _m select 3;
		private _observedAt = _m select 4;
		private _provenance = _m select 5;

		private _index = YOSHI_CB_observations findIf {(_x select 0) isEqualTo _id};
		if (_index >= 0) then {
			private _observation = YOSHI_CB_observations select _index;
			_observation set [1, +_pos];
			_observation set [4, _observedAt];
			_observation set [5, _eta];
			_observation set [6, _exp];
			_observation set [7, +_provenance];
			YOSHI_CB_observations set [_index, _observation];
		} else {
			// [uid, position, uncertainty geometry, first/last observation times,
			// eta, expiry, provenance]. Different physical UIDs are never folded
			// together, even when their map presentation is visually clustered.
			YOSHI_CB_observations pushBack [
				_id, +_pos, ["ellipse", [YOSHI_CB_UNCERTAINTY_RADIUS, YOSHI_CB_UNCERTAINTY_RADIUS], 0],
				_observedAt, _observedAt, _eta, _exp, +_provenance
			];
		};
		call YOSHI_CB_publishObservations;
	};
};

YOSHI_CB_clearRenderMarkers = {
	{deleteMarkerLocal _x} forEach YOSHI_CB_renderMarkers;
	YOSHI_CB_renderMarkers = [];
	YOSHI_CB_visualClusters = [];
};

YOSHI_CB_screenLinked = {
	params ["_map", "_left", "_right", "_threshold"];
	private _leftPos = _left select 1;
	private _rightPos = _right select 1;
	if ((_leftPos distance2D _rightPos) <= YOSHI_CB_ARMING_DIST) exitWith {true};
	private _a = _map ctrlMapWorldToScreen _leftPos;
	private _b = _map ctrlMapWorldToScreen _rightPos;
	if ((count _a) < 2 || {(count _b) < 2}) exitWith {false};
	private _dx = (_a select 0) - (_b select 0);
	private _dy = (_a select 1) - (_b select 1);
	sqrt ((_dx * _dx) + (_dy * _dy)) <= _threshold
};

YOSHI_CB_clusterForMap = {
	params ["_map", "_observations"];
	private _position = ctrlPosition _map;
	private _threshold = YOSHI_CB_VISUAL_LINK_FRACTION * ((_position select 2) min (_position select 3));
	private _remaining = +_observations;
	private _groups = [];
	while {(count _remaining) > 0} do {
		private _group = [_remaining deleteAt 0];
		private _front = 0;
		while {_front < count _group} do {
			private _seed = _group select _front;
			for "_i" from ((count _remaining) - 1) to 0 step -1 do {
				private _candidate = _remaining select _i;
				if ([_map, _seed, _candidate, _threshold] call YOSHI_CB_screenLinked) then {
					_group pushBack (_remaining deleteAt _i);
				};
			};
			_front = _front + 1;
		};
		_groups pushBack _group;
	};
	_groups
};

YOSHI_CB_clusterEnvelope = {
	params ["_members"];
	private _first = (_members select 0) select 1;
	private _endA = +_first;
	private _endB = +_first;
	private _longest = 0;
	for "_i" from 0 to ((count _members) - 1) do {
		for "_j" from (_i + 1) to ((count _members) - 1) do {
			private _a = (_members select _i) select 1;
			private _b = (_members select _j) select 1;
			private _distance = _a distance2D _b;
			if (_distance > _longest) then {_longest = _distance; _endA = +_a; _endB = +_b};
		};
	};
	private _radius = 0;
	private _dx = (_endB select 0) - (_endA select 0);
	private _dy = (_endB select 1) - (_endA select 1);
	{
		private _point = _x select 1;
		private _geometry = _x select 2;
		private _uncertainty = selectMax (_geometry select 1);
		private _offset = if (_longest <= 0) then {0} else {
			abs ((_dy * ((_point select 0) - (_endA select 0))) - (_dx * ((_point select 1) - (_endA select 1)))) / _longest
		};
		_radius = _radius max (_offset + _uncertainty);
	} forEach _members;
	private _center = [((_endA select 0) + (_endB select 0)) / 2, ((_endA select 1) + (_endB select 1)) / 2, 0];
	private _direction = if (_longest <= 0) then {0} else {_dx atan2 _dy};
	private _etaValues = _members apply {_x select 5};
	[_center, _endA, _endB, _longest / 2, _radius, _direction, selectMin _etaValues, selectMax _etaValues, count _members, _members apply {_x select 0}]
};

YOSHI_CB_renderMap = {
	params ["_map"];
	call YOSHI_CB_clearRenderMarkers;
	private _observations = +(missionNamespace getVariable ["YOSHI_CBR_OBSERVATIONS", []]);
	private _groups = [_map, _observations] call YOSHI_CB_clusterForMap;
	{
		private _envelope = [_x] call YOSHI_CB_clusterEnvelope;
		_envelope params ["_center", "_endA", "_endB", "_halfLength", "_radius", "_direction", "_etaMin", "_etaMax", "_count"];
		private _prefix = format ["YOSHI_cb_view_%1_%2", clientOwner, YOSHI_CB_markerIndex];
		YOSHI_CB_markerIndex = YOSHI_CB_markerIndex + 1;
		if (_count <= 1) then {
			private _zone = createMarkerLocal [format ["%1_zone", _prefix], _center];
			_zone setMarkerShapeLocal "ELLIPSE";
			_zone setMarkerBrushLocal "SolidBorder";
			_zone setMarkerColorLocal "ColorRed";
			_zone setMarkerAlphaLocal 0.35;
			_zone setMarkerSizeLocal [_radius, _radius];
			YOSHI_CB_renderMarkers pushBack _zone;
		} else {
			// A real capsule: a narrow oriented body plus circular end caps. It
			// bounds every constituent uncertainty disc without converting a
			// walking barrage into a vast enclosing circle.
			private _body = createMarkerLocal [format ["%1_body", _prefix], _center];
			_body setMarkerShapeLocal "RECTANGLE";
			_body setMarkerBrushLocal "SolidBorder";
			_body setMarkerColorLocal "ColorRed";
			_body setMarkerAlphaLocal 0.35;
			_body setMarkerSizeLocal [_radius, _halfLength];
			_body setMarkerDirLocal _direction;
			YOSHI_CB_renderMarkers pushBack _body;
			{
				private _cap = createMarkerLocal [format ["%1_cap_%2", _prefix, _forEachIndex], _x];
				_cap setMarkerShapeLocal "ELLIPSE";
				_cap setMarkerBrushLocal "SolidBorder";
				_cap setMarkerColorLocal "ColorRed";
				_cap setMarkerAlphaLocal 0.35;
				_cap setMarkerSizeLocal [_radius, _radius];
				YOSHI_CB_renderMarkers pushBack _cap;
			} forEach [_endA, _endB];
		};
		private _icon = createMarkerLocal [format ["%1_icon", _prefix], _center];
		_icon setMarkerTypeLocal "mil_warning";
		_icon setMarkerColorLocal "ColorRed";
		_icon setMarkerTextLocal format ["%1 shells | ETA %2-%3s", _count, _etaMin, _etaMax];
		YOSHI_CB_renderMarkers pushBack _icon;
		YOSHI_CB_visualClusters pushBack _envelope;
	} forEach _groups;
};

YOSHI_CB_rendererManager = {
	while {hasInterface} do {
		private _display = findDisplay 12;
		private _map = if (isNull _display) then {controlNull} else {_display displayCtrl 51};
		private _enabled = missionNamespace getVariable ["YOSHI_CBR_ENABLED", false];
		if (_enabled && {!isNull _map} && {visibleMap}) then {
			private _signature = str [ctrlMapScale _map, missionNamespace getVariable ["YOSHI_CBR_OBSERVATIONS", []]];
			if (_signature isNotEqualTo YOSHI_CB_lastRenderSignature) then {
				[_map] call YOSHI_CB_renderMap;
				YOSHI_CB_lastRenderSignature = _signature;
			};
		} else {
			if !(YOSHI_CB_renderMarkers isEqualTo []) then {call YOSHI_CB_clearRenderMarkers};
			YOSHI_CB_lastRenderSignature = "";
		};
		uiSleep 0.1;
	};
};

YOSHI_CB_manager = {
	while {true} do {
		call YOSHI_CB_processQueue;
		call YOSHI_CB_prune;
		sleep 0.25;
	};
};

YOSHI_CB_pruneAirborneShells = {
	YOSHI_CB_airborneShells = YOSHI_CB_airborneShells select {!isNull _x && {alive _x}};
};

YOSHI_CB_registerAirborneShell = {
	params ["_shell"];

	if (isNull _shell) exitWith {false};

	call YOSHI_CB_pruneAirborneShells;
	private _hadAirborne = (count YOSHI_CB_airborneShells) > 0;

	if !(_shell in YOSHI_CB_airborneShells) then {
		YOSHI_CB_airborneShells pushBack _shell;
	};

	!_hadAirborne
};

YOSHI_CB_unregisterAirborneShell = {
	params ["_shell"];

	if (!isNull _shell) then {
		private _idx = YOSHI_CB_airborneShells find _shell;
		if (_idx >= 0) then {
			YOSHI_CB_airborneShells deleteAt _idx;
		};
	};

	call YOSHI_CB_pruneAirborneShells;
};

YOSHI_CB_getShellUid = {
	params ["_shell"];

	if (isNull _shell) exitWith {""};

	private _uid = _shell getVariable ["YOSHI_CB_uid", ""];
	if (_uid isEqualTo "") then {
		YOSHI_CB_LOCAL_UID_COUNTER = YOSHI_CB_LOCAL_UID_COUNTER + 1;
		_uid = format ["%1:%2", clientOwner, YOSHI_CB_LOCAL_UID_COUNTER];
		_shell setVariable ["YOSHI_CB_uid", _uid];
	};

	_uid
};


// The impact surface is the ground under the projected point, not sea level.
// Clamped at the waterline so shells falling into the sea still terminate.
YOSHI_CB_groundHeightAt = {
	params ["_position"];
	0 max (getTerrainHeightASL [_position select 0, _position select 1, 0])
};

YOSHI_predictFallTimeAndPos = {
	params["_projectile"];

	private _position = getPosASL _projectile;
	private _velocity = velocity _projectile;
	private _gravity = [0,0,-9.81];
	private _time = 0;
	private _ground = [_position] call YOSHI_CB_groundHeightAt;

	while {(_position select 2) > _ground && {_time < YOSHI_CB_PREDICT_MAX_TIME}} do {
		_position = _position vectorAdd (_velocity vectorMultiply YOSHI_CB_PREDICT_STEP);
		_velocity = _velocity vectorAdd (_gravity vectorMultiply YOSHI_CB_PREDICT_STEP);

		_time = _time + YOSHI_CB_PREDICT_STEP;
		_ground = [_position] call YOSHI_CB_groundHeightAt;
	};

	[round _time, _position]
};

YOSHI_handleArtilleryFire = {
	params ["_shell", ["_provenance", []]];

	if (isNull _shell) exitWith {};

	private _uid = [_shell] call YOSHI_CB_getShellUid;
	if (_uid isEqualTo "") exitWith {};

	private _next = 0;

	while {alive _shell} do {
		if (time >= _next) then {
			private _impact = _shell call YOSHI_predictFallTimeAndPos;
				[_uid, _impact select 1, _impact select 0, _provenance] remoteExecCall ["YOSHI_fnc_cbrReceiveTrackUpdate", 2];
			_next = time + 0.5;
		};
		sleep 0.05;
	};

	[_shell] call YOSHI_CB_unregisterAirborneShell;
};

YOSHI_fnc_cbrWarnSidePlayers = {
	params ["_artySide", "_impactPos", ["_radius", 1000]];

	if (!isServer) exitWith {};
	if !(_artySide in [west, east, resistance]) exitWith {};
	if !(_impactPos isEqualType [] && {(count _impactPos) >= 2}) exitWith {};

	{
		private _unit = _x;
		if (!isPlayer _unit || {!alive _unit}) then { continue; };

		private _unitSide = side _unit;
		if (!(_unitSide in [west, east, resistance])) then { continue; };
		if (_unitSide isEqualTo _artySide) then { continue; };
		if ((_unit distance2D _impactPos) > _radius) then { continue; };


		[[side _unit, "Base"], "YAS_CBR_WarningLaunchDetected", _unit] call YAS_fnc_emitSideRadio;
	} forEach allPlayers;
};

YOSHI_fnc_cbrReset = {
	YOSHI_CB_queue = [];
	YOSHI_CB_observations = [];
	call YOSHI_CB_publishObservations;
	YOSHI_CB_markerIndex = 0;
	YOSHI_CB_airborneShells = [];
};

YOSHI_fnc_cbrReceiveTrackUpdate = {
	if (!isServer) exitWith {};
	params ["_uid", "_impactPos", "_eta", ["_provenance", []]];

	if (!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", false])) exitWith {};
	if (_uid isEqualTo "") exitWith {};
	if !(_impactPos isEqualType [] && {(count _impactPos) >= 2}) exitWith {};

	private _receivedProvenance = +_provenance;
	_receivedProvenance pushBack remoteExecutedOwner;
	[_uid, _impactPos, _eta, _receivedProvenance] call YOSHI_CB_enqueue;
};

YOSHI_fnc_cbrHandleLocalArtilleryFire = {
	if (!isServer) exitWith {};
	params ["_vehicle", "_artySide", "_impactPos", ["_isFirstLaunchInCycle", false]];

	if (!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", false])) exitWith {};

	if (_isFirstLaunchInCycle) then {
		[_artySide, _impactPos, 1000] call YOSHI_fnc_cbrWarnSidePlayers;
	};

	if (!isNull _vehicle) then {
		[_vehicle] call YOSHI_fnc_originOnShot;
	};
};

YOSHI_fnc_cbrEnsureLocalHandler = {
	if (YOSHI_CB_LOCAL_EH_ID >= 0) exitWith {true};

	YOSHI_CB_LOCAL_EH_ID = addMissionEventHandler ["ArtilleryShellFired", {
		params ["_vehicle", "_weapon", "_ammo", "_gunner", "_instigator", "_artilleryTarget", "_targetPosition", "_shell"];

		if (!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", false])) exitWith {};
		if (isNull _shell || {!local _shell}) exitWith {};

		private _impactPos = _targetPosition;
		if !(_impactPos isEqualType [] && {(count _impactPos) >= 2}) then {
			_impactPos = (_shell call YOSHI_predictFallTimeAndPos) select 1;
		};

			private _artySide = if (!isNull _gunner) then { side group _gunner } else { side _vehicle };
			private _isFirstLaunchInCycle = [_shell] call YOSHI_CB_registerAirborneShell;
			[_vehicle, _artySide, _impactPos, _isFirstLaunchInCycle] remoteExecCall ["YOSHI_fnc_cbrHandleLocalArtilleryFire", 2];
			private _provenance = [clientOwner, if (isNull _vehicle) then {""} else {netId _vehicle}, _weapon, _ammo, str _artySide];
			[_shell, _provenance] spawn YOSHI_handleArtilleryFire;
	}];

	true
};

YOSHI_fnc_cbrStart = {
	if (!isServer) exitWith {false};

	private _isEnabled = missionNamespace getVariable ["YOSHI_CBR_ENABLED", false];
	if (_isEnabled) exitWith {true};

	[] call YOSHI_fnc_cbrReset;
	if (!isNil "YOSHI_fnc_originReset") then {
		[] call YOSHI_fnc_originReset;
	};

	private _manager = [] spawn YOSHI_CB_manager;
	private _originManager = [] spawn YOSHI_originManager;

	missionNamespace setVariable ["YOSHI_CBR_MANAGER_THREAD", _manager];
	missionNamespace setVariable ["YOSHI_CBR_ORIGIN_THREAD", _originManager];
	missionNamespace setVariable ["YOSHI_CBR_EH_ID", YOSHI_CB_LOCAL_EH_ID];
	missionNamespace setVariable ["YOSHI_CBR_ENABLED", true, true];

	missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]
};

YOSHI_fnc_cbrStop = {
	if (!isServer) exitWith {false};

	private _manager = missionNamespace getVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull];
	if (!scriptDone _manager) then {
		terminate _manager;
	};

	private _originManager = missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull];
	if (!scriptDone _originManager) then {
		terminate _originManager;
	};

	[] call YOSHI_fnc_cbrReset;
	if (!isNil "YOSHI_fnc_originReset") then {
		[] call YOSHI_fnc_originReset;
	};

	missionNamespace setVariable ["YOSHI_CBR_MANAGER_THREAD", scriptNull];
	missionNamespace setVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull];
	missionNamespace setVariable ["YOSHI_CBR_EH_ID", YOSHI_CB_LOCAL_EH_ID];
	missionNamespace setVariable ["YOSHI_CBR_ENABLED", false, true];

	missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]
};

YOSHI_fnc_cbrSetEnabled = {
	params [["_enable", true]];

	if (_enable) exitWith {
		[] call YOSHI_fnc_cbrStart;
	};

	[] call YOSHI_fnc_cbrStop;
};

YOSHI_fnc_cbrToggleEnabled = {
	if (!isServer) exitWith {missionNamespace getVariable ["YOSHI_CBR_ENABLED", false]};

	private _isEnabled = missionNamespace getVariable ["YOSHI_CBR_ENABLED", false];
	[!_isEnabled] call YOSHI_fnc_cbrSetEnabled;
};

[] call YOSHI_fnc_cbrEnsureLocalHandler;
if (hasInterface) then {[] spawn YOSHI_CB_rendererManager};
