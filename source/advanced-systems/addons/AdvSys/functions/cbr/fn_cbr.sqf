// Counter Battery Radar
/*
Lord, set a watch before my mouth,
keep guard over the door of my lips.
(Psalm 141:3)

And over our camp, keep watch through the night.
Amen.
*/

YOSHI_CB_LINK_DIST = 100;
YOSHI_CB_LEEWAY = 100;
YOSHI_CB_MEMBER_TTL = 2.0;

YOSHI_CB_queue = [];
YOSHI_CB_clusters = [];
YOSHI_CB_markerIndex = 0;
YOSHI_CB_nextUid = 0;
YOSHI_CB_airborneShells = [];

YOSHI_CB_CENTER_UPDATE_DIST = 25;
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

YOSHI_CB_enqueue = {
	params ["_uid", "_impactPos", "_eta"];
	private _exp = time + _eta + 1;
	YOSHI_CB_queue pushBack [_uid, _impactPos, _eta, _exp];
};

YOSHI_CB_recalcCluster = {
	params ["_cluster"];

	private _members = _cluster select 0;

	private _sumX = 0;
	private _sumY = 0;
	private _n = count _members;
	if (_n == 0) exitWith {[_cluster, [0,0,0], 0, 999, 999]};

	{
		private _p = _x select 1;
		_sumX = _sumX + (_p select 0);
		_sumY = _sumY + (_p select 1);
	} forEach _members;

	private _desiredCenter = [_sumX / _n, _sumY / _n, 0];

	private _center = _cluster select 1;
	if (isNil "_center") then {_center = _desiredCenter};

	if ((_center distance2D _desiredCenter) > YOSHI_CB_CENTER_UPDATE_DIST) then {
		_center = _desiredCenter;
	};

	private _maxD = 0;
	private _etaMin = 999999;
	private _etaMax = -1;

	{
		private _p = _x select 1;
		private _eta = _x select 2;

		private _d = _center distance2D _p;
		if (_d > _maxD) then {_maxD = _d;};

		if (_eta < _etaMin) then {_etaMin = _eta;};
		if (_eta > _etaMax) then {_etaMax = _eta;};
	} forEach _members;

	private _radius = _maxD + YOSHI_CB_LEEWAY;

	_cluster set [1, _center];
	_cluster set [2, _radius];
	_cluster set [3, _etaMin];
	_cluster set [4, _etaMax];
};


YOSHI_CB_drawCluster = {
	params ["_cluster"];

	private _center = _cluster select 1;
	private _radius = _cluster select 2;
	private _etaMin = _cluster select 3;
	private _etaMax = _cluster select 4;
	private _members = _cluster select 0;

	private _mCircle = _cluster select 5;
	private _mIcon = _cluster select 6;

	_mCircle setMarkerPos _center;
	_mCircle setMarkerSize [_radius, _radius];

	_mIcon setMarkerPos _center;
	_mIcon setMarkerText format ["%1 shells | ETA %2-%3s", count _members, _etaMin, _etaMax];
};

YOSHI_CB_createCluster = {
	params ["_member"];

	private _idx = YOSHI_CB_markerIndex;
	YOSHI_CB_markerIndex = YOSHI_CB_markerIndex + 1;

	private _circleName = format ["YOSHI_cb_zone_%1", _idx];
	private _iconName = format ["YOSHI_cb_txt_%1", _idx];

	private _mCircle = createMarker [_circleName, _member select 1];
	_mCircle setMarkerShape "ELLIPSE";
	_mCircle setMarkerBrush "SolidBorder";
	_mCircle setMarkerColor "ColorRed";
	_mCircle setMarkerAlpha 0.35;

	private _mIcon = createMarker [_iconName, _member select 1];
	_mIcon setMarkerType "mil_warning";
	_mIcon setMarkerColor "ColorRed";

	private _cluster = [[_member], [0,0,0], 0, 999, 999, _circleName, _iconName];
	[_cluster] call YOSHI_CB_recalcCluster;
	[_cluster] call YOSHI_CB_drawCluster;

	YOSHI_CB_clusters pushBack _cluster;
};

YOSHI_CB_addToCluster = {
	params ["_cluster", "_member"];

	(_cluster select 0) pushBack _member;
	[_cluster] call YOSHI_CB_recalcCluster;
	[_cluster] call YOSHI_CB_drawCluster;
};

YOSHI_CB_prune = {
	private _now = time;

	private _i = 0;
	while {_i < count YOSHI_CB_clusters} do {
		private _c = YOSHI_CB_clusters select _i;
		private _members = _c select 0;

		_members = _members select {(_x select 3) > _now};
		_c set [0, _members];

		if ((count _members) == 0) then {
			deleteMarker (_c select 5);
			deleteMarker (_c select 6);
			YOSHI_CB_clusters deleteAt _i;
		} else {
			[_c] call YOSHI_CB_recalcCluster;
			[_c] call YOSHI_CB_drawCluster;
			_i = _i + 1;
		};
	};
};

YOSHI_CB_processQueue = {
	while {(count YOSHI_CB_queue) > 0} do {
		private _m = YOSHI_CB_queue deleteAt 0;

		private _id = _m select 0;
		private _pos = _m select 1;
		private _eta = _m select 2;
		private _exp = _m select 3;

		private _updated = false;

		for "_ci" from 0 to ((count YOSHI_CB_clusters) - 1) do {
			private _c = YOSHI_CB_clusters select _ci;
			private _members = _c select 0;

			for "_mi" from 0 to ((count _members) - 1) do {
				private _mem = _members select _mi;
				if ((_mem select 0) == _id) exitWith {
					_mem set [1, _pos];
					_mem set [2, _eta];
					_mem set [3, _exp];
					_members set [_mi, _mem];
					_c set [0, _members];

					[_c] call YOSHI_CB_recalcCluster;
					[_c] call YOSHI_CB_drawCluster;

					_updated = true;
				};
			};
			if (_updated) exitWith {};
		};

		if (!_updated) then {
			private _member = [_id, _pos, _eta, _exp];

			private _best = -1;
			private _bestD = 1e12;

			for "_i" from 0 to ((count YOSHI_CB_clusters) - 1) do {
				private _c = YOSHI_CB_clusters select _i;
				private _d = (_c select 1) distance2D _pos;
				if (_d < _bestD) then {
					_bestD = _d;
					_best = _i;
				};
			};

			if (_best == -1 || {_bestD > YOSHI_CB_LINK_DIST}) then {
				[_member] call YOSHI_CB_createCluster;
			} else {
				[YOSHI_CB_clusters select _best, _member] call YOSHI_CB_addToCluster;
			};
		};
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


YOSHI_predictFallTimeAndPos = {
	params["_projectile"];

	private _position = getPosASL _projectile;
	private _velocity = velocity _projectile;
	private _gravity = [0,0,-9.81];
	private _time = 0;

	while {_position select 2 >= 0} do {
		_position = _position vectorAdd (_velocity vectorMultiply 0.1);
		_velocity = _velocity vectorAdd (_gravity vectorMultiply 0.1);

		_time = _time + 0.1;
	};

	[round _time, _position]
};

YOSHI_handleArtilleryFire = {
	params ["_shell"];

	if (isNull _shell) exitWith {};

	private _uid = [_shell] call YOSHI_CB_getShellUid;
	if (_uid isEqualTo "") exitWith {};

	private _next = 0;

	while {alive _shell} do {
		if (time >= _next) then {
			private _impact = _shell call YOSHI_predictFallTimeAndPos;
			[_uid, _impact select 1, _impact select 0] remoteExecCall ["YOSHI_fnc_cbrReceiveTrackUpdate", 2];
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
	{
		private _mCircle = _x select 5;
		private _mIcon = _x select 6;
		deleteMarker _mCircle;
		deleteMarker _mIcon;
	} forEach YOSHI_CB_clusters;

	YOSHI_CB_queue = [];
	YOSHI_CB_clusters = [];
	YOSHI_CB_markerIndex = 0;
	YOSHI_CB_nextUid = 0;
	YOSHI_CB_airborneShells = [];
};

YOSHI_fnc_cbrReceiveTrackUpdate = {
	if (!isServer) exitWith {};
	params ["_uid", "_impactPos", "_eta"];

	if (!(missionNamespace getVariable ["YOSHI_CBR_ENABLED", false])) exitWith {};
	if (_uid isEqualTo "") exitWith {};
	if !(_impactPos isEqualType [] && {(count _impactPos) >= 2}) exitWith {};

	[_uid, _impactPos, _eta] call YOSHI_CB_enqueue;
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
		[_shell] spawn YOSHI_handleArtilleryFire;
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
