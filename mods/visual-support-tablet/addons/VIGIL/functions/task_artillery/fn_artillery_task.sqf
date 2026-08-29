/*
Eternal rest grant upon them, O Lord
   and let perpetual light shine upon them.
May the souls of all the faithful departed,
  through the mercy of God, rest in peace. Amen.
*/

// he:
//weapon_vls_01

//magazine_Missiles_Cruise_01_Cluster_x18
//magazine_Missiles_Cruise_01_x18

YSF_fireVLS = {
	params ["_artyUnit", "_target"];

	private _commander = effectiveCommander _artyUnit;

    if (local _commander) then {
		private _gunner = gunner _artyUnit;
		_artyUnit setWeaponReloadingTime [_gunner, currentMuzzle _gunner, 0];

        (side _artyUnit) reportRemoteTarget [_target, 3600];
		_target confirmSensorTarget [(side _artyUnit), true];
		_artyUnit fireAtTarget [_target, "weapon_vls_01"];
		_artyUnit setVariable ["YSF_ordered", true, true];

		private _gunner = gunner _artyUnit;
		_artyUnit setWeaponReloadingTime [_gunner, currentMuzzle _gunner, 0];
    } else {
        [_artyUnit, _target] remoteExec ["YSF_fireVLS", _commander];
    };
};

YSF_fnc_doArtyFire = {
    params ["_artyUnit", "_pos", "_mag"];
    if (!alive _artyUnit) exitWith {};
	
    private _commander = effectiveCommander _artyUnit;

    if (local _commander) then {
        _commander doArtilleryFire [_pos, _mag, 1];
		waitUntil {sleep 2; !alive _artyUnit || unitReady _artyUnit};
        _artyUnit setVariable ["YSF_fired", true, true];
    } else {
        [_artyUnit, _pos, _mag] remoteExec ["YSF_fnc_doArtyFire", _commander];
    };
};


YSF_fireSalvo = {
	params ["_artyUnit","_queue","_mag"];
	format ["[YSF_ArtilleryTask] Assigning unit %1 to strike positions: %2", _artyUnit, _queue] call YSF_fnc_debugMsg;
	_artyUnit setVariable ["YSF_arty_mission_completed", "firing", true];
	{
		private _isVLS = ((typeOf _artyUnit) isEqualTo "B_Ship_MRLS_01_F");
		if (!alive _artyUnit) exitWith {_artyUnit setVariable ["YSF_arty_mission_completed", "dead", true];};
		private _strikePos = _x;

		

		if (_isVLS) then {
			_artyUnit loadMagazine [[0], "weapon_VLS_01", _mag];
			sleep 0.5;
			private _gunner = gunner _artyUnit;
			_artyUnit setWeaponReloadingTime [_gunner, currentMuzzle _gunner, 0];
			sleep 0.5;
			private _munition = "HE";
			if ("cluster" in (toLower (currentMuzzle _gunner))) then {
				_munition = "Cluster";
			};
			private _position = [_strikePos#0, _strikePos#1, 0];
			format ["[YSF_ArtilleryTask] VLS %1 launching %3 missile at position %2 | round: %4/%5", _artyUnit, _position, _munition, _forEachIndex+1, count _queue] call YSF_fnc_debugMsg;
			private _target = createVehicle ["Land_HelipadEmpty_F", _position, [], 0, "CAN_COLLIDE"];
			[_target] spawn {params ["_t"]; sleep 100; deleteVehicle _t;};

			_artyUnit setVariable ["YSF_ordered", false, true];
			_artyUnit setVariable ["YSF_fired", false, true];

			private _eH_index = _artyUnit addEventHandler ["Fired", {
				params ["_unit", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];
				_unit setVariable ["YSF_fired", true, true];
			}];

			[_artyUnit, _target] call YSF_fireVLS;

			private _count = 0;
			private _retry = false;
			waitUntil {
				sleep 1; 
				private _ordered = _artyUnit getVariable ["YSF_ordered", false];
				private _fired = _artyUnit getVariable ["YSF_fired", false];
				if (_ordered && !_fired) then {
					_count = _count + 1;
					if (_count > 3) then {
						format ["[YSF_ArtilleryTask] WARNING: Unit %1 did not fire after being ordered. Retrying...", _artyUnit] call YSF_fnc_debugMsg;
						_retry = true;
					};
				};
				!alive _artyUnit || _fired || _retry
			};

			if (_retry) then {
				private _new_target = createVehicle ["Land_HelipadEmpty_F", _position, [], 0, "CAN_COLLIDE"];
				[_new_target] spawn {params ["_t"]; sleep 100; deleteVehicle _t;};
				format ["Trying once more for good measure: %1 | %2", _artyUnit, _new_target] call YSF_fnc_debugMsg;

				[_artyUnit, _new_target] call YSF_fireVLS;
				private _count = 0;
				private _skip = false;

				_artyUnit setVariable ["YSF_ordered", false, true];
				_artyUnit setVariable ["YSF_fired", false, true];
				waitUntil {
					sleep 1; 
					private _ordered = _artyUnit getVariable ["YSF_ordered", false];
					private _fired = _artyUnit getVariable ["YSF_fired", false];
					if (_ordered && !_fired) then {
						_count = _count + 1;
						if (_count > 3) then {
							format ["[YSF_ArtilleryTask] WARNING: Unit %1 Failed again, skipping...", _artyUnit] call YSF_fnc_debugMsg;
							_skip = true;
						};
					};
					!alive _artyUnit || _fired || _skip
				};
			};

			_artyUnit removeEventHandler ["Fired", _eH_index];

		} else {
			if (_strikePos inRangeOfArtillery [[_artyUnit],_mag]) then {
				_artyUnit setWeaponReloadingTime [gunner _artyUnit, currentMuzzle gunner _artyUnit, 0];
				format ["[YSF_ArtilleryTask] Unit %1 firing at position %2 | round: %3/%4", _artyUnit, _strikePos, _forEachIndex+1, count _queue] call YSF_fnc_debugMsg;
				
				_artyUnit setVariable ["YSF_fired", false, true];
				[_artyUnit, _strikePos, _mag] call YSF_fnc_doArtyFire;
				waitUntil {sleep 2; !alive _artyUnit || ((_artyUnit getVariable ["YSF_fired", false]) && unitReady _artyUnit)};
			} else {
				format ["[YSF_ArtilleryTask] WARNING: Unit %1 cannot reach position %2 with ordinance %3", _artyUnit, _strikePos, _mag] call YSF_fnc_debugMsg;
			};
		};

	} forEach _queue;
	_artyUnit setVariable ["YSF_arty_mission_completed", "done", true];
};

YSF_handlers_artillery = {
  createHashMapFromArray [
    ["init", {
      params ["_v","_t","_d"];
	  format ["[YSF_ArtilleryTask] Initializing artillery task for vehicle %1", _v] call YSF_fnc_debugMsg;
      _d params ["_strike_positions", "_ordinance"];

	  if (count _strike_positions == 0) exitWith {
		"fail"
	  };
	  if (_ordinance == "") exitWith {
		"fail"
	  };

	  private _group = group (effectiveCommander _v);
	  private _vehicles = []; 
	  { 
		private _v = vehicle _x; 
		if (_v != _x) then { 
			_vehicles pushBackUnique _v;
		}; 
	} forEach units _group; 

	  _t set ["arty_units", _vehicles];

      "advance"
    }],

    ["start", {
		params ["_v","_t","_d"];
		format ["[YSF_ArtilleryTask] Starting artillery task for vehicle %1", _v] call YSF_fnc_debugMsg;
		[_v, "YSF_ArtilleryAck"] call YSF_fnc_emitSideRadio;

      	"advance"
    }],

    ["mission", {
      	params ["_v","_t","_d"];
      	_d params ["_strike_positions", "_ordinance"];
		private _units = (_t get "arty_units") select {alive _x};
		if (_units isEqualTo []) exitWith {"fail"};

		private _numberOfUnits = count _units;
		private _assign = [];
		_assign resize _numberOfUnits;
		for "_i" from 0 to (_numberOfUnits - 1) do {_assign set [_i, []];};

		{
			(_assign select (_forEachIndex mod _numberOfUnits)) pushBack _x;
		} forEach _strike_positions;

		private _handles = [];
		{
			private _artyUnit = _x;
			
			private _queue = _assign select _forEachIndex;
			_handles pushBack ([_artyUnit,_queue,_ordinance] spawn YSF_fireSalvo);
		} forEach _units;

		format ["[YSF_ArtilleryTask] Launched artillery strikes with assignments: %1", _assign] call YSF_fnc_debugMsg;

	  	"advance"
    }],

    ["end", {
      params ["_v","_t","_d"];
      private _units = (_t get "arty_units") select {alive _x};
	  private _waitingVehicles = [];

	  {
		private _status = _x getVariable ["YSF_arty_mission_completed", "unknown"];
		if (!(_status in ["done","dead"])) exitWith	{
			_waitingVehicles pushBack _x;
		};
	  } forEach _units;

	  private _handles = _t getOrDefault ["arty_threads", []];
      private _active = _handles select {scriptDone _x isEqualTo false};

	  if ((count _waitingVehicles) > 0 || (count _active) > 0) then {
		"wait"
	  } else {
	  	"advance"
	  };

    }],

    ["finally", {
      params ["_v","_t","_d"];

	  private _units = (_t get "arty_units") select {alive _x};
	  {
		_x setVariable ["YSF_arty_mission_completed", "ready_for_next", true];
	  } forEach _units;

	  format ["[YSF_ArtilleryTask] Artillery task for vehicle %1 complete", _v] call YSF_fnc_debugMsg;
	  [_v, "YSF_ArtilleryRoundsComplete"] call YSF_fnc_emitSideRadio;

      "complete"
    }]
  ]
};
