/*
Angel of God, my Guardian dear,
To whom God's love commits me here;
Ever this day, be at my side
To light and guard
To rule and guide.
Amen
*/

YSF_CAS_TASK_TIMEOUT = 300;

YSF_CAS_hasLethalAmmo = {
	params ["_vehicle"];
	if (isNull _vehicle) exitWith {false};
	private _nonLethalSims = ["laserdesignate", "shotcm", "shotsmoke", "shotillum", "shotnvgmarker", "shotsmokeshell", "shotdummy"];
	private _lethal = false;
	{
		private _magazine = _x param [0, ""];
		private _count = _x param [1, 0];
		if (_count > 0 && {_magazine isNotEqualTo ""}) then {
			private _ammo = getText (configFile >> "CfgMagazines" >> _magazine >> "ammo");
			private _simulation = toLower getText (configFile >> "CfgAmmo" >> _ammo >> "simulation");
			private _hit = getNumber (configFile >> "CfgAmmo" >> _ammo >> "hit");
			private _indirectHit = getNumber (configFile >> "CfgAmmo" >> _ammo >> "indirectHit");
			if (_ammo isNotEqualTo "" && {!(_simulation in _nonLethalSims)} && {(_hit > 0) || (_indirectHit > 0)}) exitWith {
				_lethal = true;
			};
		};
		if (_lethal) exitWith {};
	} forEach (magazinesAmmoFull _vehicle);
	_lethal
};

YSF_handlers_cas = {
  createHashMapFromArray [

    ["init", {
      	params ["_v","_t","_d"];
		format ["[YSF_CasTask] Initializing cas task for vehicle %1", _v] call YSF_fnc_debugMsg;
		_d params ["_destATL", ["_maxAlt", 20], ["_time_limit", 2]];

		if !(alive _v && {!isNull driver _v} && {alive driver _v} && {[_v] call YSF_CAS_hasLethalAmmo}) exitWith {
			_v setVariable ["YSF_cas_active", false, true];
			_v setVariable ["YSF_cas_state", "failed", true];
			"fail"
		};

		private _home = _v getVariable ["YSF_cas_homeATL", []];
		if !(_home isEqualType [] && {count _home >= 2}) then {
			_home = getPosATL _v;
			_v setVariable ["YSF_cas_homeATL", _home, true];
		};
		_v setVariable ["YSF_transport_homeATL", _home, true];
		_t set ["returnLocation", _home];

		_t set ["destATL", _destATL];
		_t set ["arrivalRadius", YSF_CAS_ARRIVAL_RADIUS];
		_t set ["time_limit", _time_limit];
		_t set ["deadline", diag_tickTime + YSF_CAS_TASK_TIMEOUT];
		_v setVariable ["YSF_cas_taskId", _t get "id", true];
		_v setVariable ["YSF_cas_areaATL", _destATL, true];
		_v setVariable ["YSF_cas_targetRadius", YSF_CAS_ARRIVAL_RADIUS, true];
		_v setVariable ["YSF_cas_active", false, true];
		_v setVariable ["YSF_cas_state", "dispatching", true];
		private _killedEh = _v addEventHandler ["Killed", {
			params ["_vehicle"];
			_vehicle setVariable ["YSF_cas_active", false, true];
			_vehicle setVariable ["YSF_cas_state", "failed", true];
		}];
		_t set ["killedEh", _killedEh];

		_v flyInHeight [_maxAlt, true];
		_v flyInHeightASL [_maxAlt, _maxAlt, _maxAlt];

		[_v, "NONE"] call YSF_fnc_setVehicleLandMode;

		"advance"
    }],

    ["start", {
		params ["_v","_t","_d"];
		format ["[YSF_CasTask] Starting cas task for vehicle %1", _v] call YSF_fnc_debugMsg;
		private _dest = _t get "destATL";

		[_v] call YSF_fnc_setVehicleTransitAI;
		[_v, _dest, "MOVE", 2] call YOSHI_setBasicWaypoint;
		[_v, "YSF_CASAck"] call YSF_fnc_emitSideRadio;

		"advance"
    }],

    ["mission", {
		params ["_v","_t","_d"];
		private _dest = _t get "destATL";
		private _rad  = _t getOrDefault ["arrivalRadius", YSF_CAS_ARRIVAL_RADIUS];
		if (diag_tickTime > (_t getOrDefault ["deadline", diag_tickTime + 1])) exitWith {"fail"};

		if (random 1 < 0.1) then { [_v, _dest, "MOVE", 0] call YOSHI_setBasicWaypoint; };
		

		if ((_v distance2D _dest) <= _rad) then {
			_t set ["start_time", serverTime];
			_v setVariable ["YSF_cas_active", true, true];
			_v setVariable ["YSF_cas_state", "on_station", true];
			[_v] call YOSHI_rebootAI;
			private _group = group effectiveCommander _v;
			if (!isNull _group) then {
				_group setCombatMode "BLUE";
				_group setBehaviourStrong "AWARE";
			};
			[_v, _dest, "LOITER", 2] call YOSHI_setBasicWaypoint;
			"advance" 
		} else {
			"wait" 
		}
    }],

    ["end", {
		params ["_v","_t","_d"];
		private _dest = _t get "destATL";
		private _elapsed = serverTime - (_t getOrDefault ["start_time", serverTime]);
		private _time_limit = _t getOrDefault ["time_limit", 2];
		if (diag_tickTime > (_t getOrDefault ["deadline", diag_tickTime + 1])) exitWith {"fail"};

		if (_elapsed > (_time_limit * 60)) then {
			_v setVariable ["YSF_cas_active", false, true];
			_v setVariable ["YSF_cas_state", "disengaging", true];
			[_v] call YOSHI_hardStop;
			[_v, "YSF_CASDone"] call YSF_fnc_emitSideRadio; 
			"advance" 
		} else {
			"wait"
		}
    }],

    ["finally", {
		params ["_v","_t","_d"];
		_v setVariable ["YSF_cas_active", false, true];
		private _killedEh = _t getOrDefault ["killedEh", -1];
		if (_killedEh >= 0) then {_v removeEventHandler ["Killed", _killedEh];};
		private _state = _t getOrDefault ["state", "running"];
		if (_state in ["failed", "cancelled"]) exitWith {
			_v setVariable ["YSF_cas_state", _state, true];
			"complete"
		};

		private _handlers = call YSF_handlers_transport;
		private _destPos  = _t get "returnLocation";

		_v setVariable ["YSF_cas_state", "returning", true];
		[_v] call YOSHI_rebootAI;
		private _task = ["transport", _v, _handlers, [_destPos, 20, false, false, false, "rtb", "YSF_cas_state"], 10, 3] call YSF_taskNew;
		[_v, _task] call YSF_taskAssign;

		"complete"
	}]
  ]
};
