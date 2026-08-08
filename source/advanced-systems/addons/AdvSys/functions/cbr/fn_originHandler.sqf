YOSHI_ORIGIN_FORGET_AFTER = 60;
YOSHI_ORIGIN_FADE_START = 30;
YOSHI_ORIGIN_FADE_DURATION = 30;

YOSHI_ORIGIN_INITIAL_R = 1000;
YOSHI_ORIGIN_MIN_R = 1;

YOSHI_ORIGIN_CONFIRM_R = 10;

YOSHI_fnc_ts = {
	private _t = systemTime;
	private _hh = _t select 3;
	private _mm = _t select 4;
	private _ss = _t select 5;
	format ["%1:%2:%3",
		[_hh, 2] call BIS_fnc_numberDigits,
		[_mm, 2] call BIS_fnc_numberDigits,
		[_ss, 2] call BIS_fnc_numberDigits
	]
};

YOSHI_originTrack = createHashMap;
YOSHI_originMarkerIndex = 0;

YOSHI_fnc_randomPointInCircle = {
	params ["_center", "_r"];

	private _a = random 360;
	private _d = _r * sqrt (random 1);
	[
		(_center select 0) + (sin _a) * _d,
		(_center select 1) + (cos _a) * _d,
		0
	]
};

YOSHI_fnc_pickDecenteredCircleCenter = {
	params ["_gunPos", "_r"];

	private _offset = 0.6 * _r;
	private _a = random 360;

	private _c = [
		(_gunPos select 0) + (sin _a) * _offset,
		(_gunPos select 1) + (cos _a) * _offset,
		0
	];

	[_c, _r]
};

YOSHI_fnc_originAlpha = {
	params ["_lastShot"];

	private _dt = time - _lastShot;
	if (_dt <= YOSHI_ORIGIN_FADE_START) exitWith {0.6};

	private _t = (_dt - YOSHI_ORIGIN_FADE_START) / YOSHI_ORIGIN_FADE_DURATION;
	if (_t >= 1) exitWith {0};

	0.6 * (1 - _t)
};

YOSHI_fnc_originEnsureMarker = {
	params ["_key", "_pos"];

	private _st = YOSHI_originTrack get _key;
	private _m = _st get "marker";

	if (isNil "_m") then {
		private _idx = YOSHI_originMarkerIndex;
		YOSHI_originMarkerIndex = YOSHI_originMarkerIndex + 1;

		_m = createMarker [format ["YOSHI_origin_%1", _idx], _pos];
		_m setMarkerShape "ELLIPSE";
		_m setMarkerBrush "SolidBorder";
		_m setMarkerColor "ColorOrange";
		_m setMarkerAlpha 0.6;

		_st set ["marker", _m];
		YOSHI_originTrack set [_key, _st];
	};

	_m
};

YOSHI_fnc_originOnShot = {
	params ["_veh"];

	private _key = netId _veh;
	if (_key == "") then {_key = str _veh};

	private _now = time;
	private _pos = getPosASL _veh;
	_pos set [2, 0];

	private _st = YOSHI_originTrack getOrDefault [_key, createHashMap];

	private _last = _st getOrDefault ["lastShot", -1];
	private _r = _st getOrDefault ["radius", YOSHI_ORIGIN_INITIAL_R];

	if (_last < 0 || {(_now - _last) > YOSHI_ORIGIN_FORGET_AFTER}) then {
		_r = YOSHI_ORIGIN_INITIAL_R;
	} else {
		_r = _r / 2;
		if (_r < YOSHI_ORIGIN_MIN_R) then {_r = YOSHI_ORIGIN_MIN_R;};
	};

	_st set ["lastShot", _now];
	_st set ["radius", _r];

	if (_r <= YOSHI_ORIGIN_CONFIRM_R) then {
		private _perm = _st getOrDefault ["permanent", ""];
		if (_perm == "") then {
			private _mOld = _st get "marker";
			if (!isNil "_mOld") then {deleteMarker _mOld;};

			private _idx = YOSHI_originMarkerIndex;
			YOSHI_originMarkerIndex = YOSHI_originMarkerIndex + 1;

			_perm = format ["YOSHI_origin_confirm_%1", _idx];
			private _mPerm = createMarker [_perm, _pos];
			_mPerm setMarkerType "mil_triangle";
			_mPerm setMarkerColor "ColorOrange";
			_mPerm setMarkerAlpha 1;

			_st set ["permanent", _perm];
		};

		private _mPerm2 = _st get "permanent";
		_mPerm2 setMarkerPos _pos;
		_mPerm2 setMarkerText format ["ARTY | %1", call YOSHI_fnc_ts];

		_st set ["confirmed", true];
		YOSHI_originTrack set [_key, _st];
	} else {
		private _centerData = [_pos, _r] call YOSHI_fnc_pickDecenteredCircleCenter;
		private _center = _centerData select 0;

		_st set ["center", _center];
		_st set ["confirmed", false];
		YOSHI_originTrack set [_key, _st];

		private _m = [_key, _center] call YOSHI_fnc_originEnsureMarker;
		_m setMarkerPos _center;
		_m setMarkerSize [_r, _r];
		_m setMarkerAlpha 0.6;
		_m setMarkerText format ["Origin estimate | ±%1m", round _r];
	};
};


YOSHI_fnc_originTick = {
	private _now = time;

	{
		private _key = _x;
		private _st = _y;

		if (_st getOrDefault ["confirmed", false]) then {continue;};

		private _last = _st getOrDefault ["lastShot", -1];
		if (_last < 0) then {continue;};

		private _dt = _now - _last;

		if (_dt > YOSHI_ORIGIN_FORGET_AFTER) then {
			private _m = _st get "marker";
			if (!isNil "_m") then {deleteMarker _m;};
			YOSHI_originTrack deleteAt _key;
		} else {
			private _m = _st get "marker";
			if (!isNil "_m") then {
				private _a = [_last] call YOSHI_fnc_originAlpha;
				_m setMarkerAlpha _a;
			};
		};
	} forEach YOSHI_originTrack;
};

YOSHI_originManager = {
	while {true} do {
		call YOSHI_fnc_originTick;
		sleep 0.25;
	};
};

YOSHI_fnc_originReset = {
	{
		private _st = _y;
		private _m = _st getOrDefault ["marker", ""];
		if (_m != "") then { deleteMarker _m; };

		private _perm = _st getOrDefault ["permanent", ""];
		if (_perm != "") then { deleteMarker _perm; };
	} forEach YOSHI_originTrack;

	YOSHI_originTrack = createHashMap;
	YOSHI_originMarkerIndex = 0;
};
