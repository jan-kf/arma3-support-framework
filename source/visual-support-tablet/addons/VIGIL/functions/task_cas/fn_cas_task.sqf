/*
Angel of God, my Guardian dear,
To whom God's love commits me here;
Ever this day, be at my side
To light and guard
To rule and guide.
Amen
*/

YSF_handlers_cas = {
  createHashMapFromArray [

    ["init", {
      	params ["_v","_t","_d"];
		format ["[YSF_CasTask] Initializing cas task for vehicle %1", _v] call YSF_fnc_debugMsg;
		_d params ["_destATL", ["_maxAlt", 20], ["_time_limit", 2]];

		_t set ["returnLocation", getPosASL _v];

		_t set ["destATL", _destATL];
		_t set ["arrivalRadius", YSF_CAS_ARRIVAL_RADIUS];
		_t set ["time_limit", _time_limit];

		_v flyInHeight [_maxAlt, true];
		_v flyInHeightASL [_maxAlt, _maxAlt, _maxAlt];

		[_v, "NONE"] call YSF_fnc_setVehicleLandMode;

		"advance"
    }],

    ["start", {
		params ["_v","_t","_d"];
		format ["[YSF_CasTask] Starting cas task for vehicle %1", _v] call YSF_fnc_debugMsg;
		private _dest = _t get "destATL";

		[_v, _dest, "SAD", 2] call YOSHI_setBasicWaypoint;
		[_v, "YSF_CASAck"] call YSF_fnc_emitSideRadio;

		"advance"
    }],

    ["mission", {
		params ["_v","_t","_d"];
		private _dest = _t get "destATL";
		private _rad  = _t getOrDefault ["arrivalRadius", YSF_CAS_ARRIVAL_RADIUS];

		if (random 1 < 0.1) then { [_v, _dest, "SAD", 0] call YOSHI_setBasicWaypoint; };
		

		if ((_v distance2D _dest) <= _rad) then {
			_t set ["start_time", serverTime];
			[_v, _dest, "SAD", 2] call YOSHI_setBasicWaypoint; 
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

		if (_elapsed > (_time_limit * 60)) then {
			[_v] call YOSHI_hardStop;
			[_v, "YSF_CASDone"] call YSF_fnc_emitSideRadio; 
			"advance" 
		} else {
			"wait"
		}
    }],

    ["finally", {
		params ["_v","_t","_d"];

		private _handlers = call YSF_handlers_transport;
		private _destPos  = _t get "returnLocation";

		private _task = ["transport", _v, _handlers, [_destPos, 20, true, false, false], 10, 3] call YSF_taskNew; 
  		[_v, _task] call YSF_taskAssignRemote;

		"complete"
	}]
  ]
};
