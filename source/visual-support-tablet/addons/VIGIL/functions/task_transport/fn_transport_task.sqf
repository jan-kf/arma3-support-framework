YSF_TRX_ARRIVAL_RADIUS = 120;

/*
Hail, Mary, full of grace,
the Lord is with thee.
Blessed art thou among women
and blessed is the fruit of thy
womb, Jesus.
Holy Mary, Mother of God,
pray for us sinners,
now and at the hour of our death.
Amen.
*/

YSF_handlers_transport = {
  createHashMapFromArray [

    ["init", {
      params ["_v","_t","_d"];
	    format ["[YSF_TransportTask] Initializing transport task for vehicle %1", _v] call YSF_fnc_debugMsg;
      _d params ["_destATL", ["_maxAlt", 20], ["_enableStabilization", true], ["_ignoreEn", false], ["_playRadio", true]];

      if (_enableStabilization) then {
        YSF_STABILIZE_HELICOPTERS pushBackUnique _v;
        publicVariable "YSF_STABILIZE_HELICOPTERS";
      };

      if (_ignoreEn) then {
        [_v] call YSF_fnc_setVehicleSafeAI;
      };

      private _resp = [_destATL, 100] call YOSHI_getNearestHelipad;
      private _lz = [0,0,0];
      _t set ["deletePadOnFinish", false];
      if (_resp select 0) then {
        _lz = _resp select 2;
        _t set ["lzPad", _resp select 1];
      } else {
        _lz = [_destATL, _v] call YOSHI_findBestLZ;
      };

      format ["[YSF_TransportTask] Selected LZ at %1 for vehicle %2", _lz, _v] call YSF_fnc_debugMsg;

      if (_lz isEqualTo [0,0,0]) exitWith {
        "fail"
      };
      if ((_lz distance2D (getPosASL _v)) < YSF_TRX_ARRIVAL_RADIUS) exitWith {
        "complete"
      };

      if (_playRadio) then {
        [_v, "YSF_TransportAck"] call YSF_fnc_emitSideRadio;
      };
      _t set ["destATL", _lz];
      _t set ["arrivalRadius", YSF_TRX_ARRIVAL_RADIUS];

      _v flyInHeight _maxAlt;

      [_v] call YSF_fnc_setVehicleTransitAI;

      [_v, "NONE"] call YSF_fnc_setVehicleLandMode;

      "advance"
    }],

    ["start", {
      params ["_v","_t","_d"];
	    format ["[YSF_TransportTask] Starting transport task for vehicle %1", _v] call YSF_fnc_debugMsg;
      private _dest = _t get "destATL";

      [_v, _dest, "MOVE", 2] call YOSHI_setBasicWaypoint;
      

      "advance"
    }],

    ["mission", {
      params ["_v","_t","_d"];
      private _dest = _t get "destATL";
      private _rad  = _t getOrDefault ["arrivalRadius", YSF_TRX_ARRIVAL_RADIUS];

      if (random 1 < 0.1) then { [_v, _dest, "MOVE", 0] call YOSHI_setBasicWaypoint; };

      if ((_v distance2D _dest) <= _rad) then { "advance" } else { "wait" }
    }],

    ["end", {
      params ["_v","_t","_d"];
      private _dest = _t get "destATL";

      private _pad = _t getOrDefault ["lzPad", objNull];
      if (isNull _pad) then {
        _newPadLoc = [_dest#0, _dest#1, 0];
        _pad = "Land_HelipadEmpty_F" createVehicle [0,0,0];
        _pad setPosASL _newPadLoc;

        format ["[YSF_TransportTask] Created Landing Pad at %1 - tick: %2", _newPadLoc, serverTime] call YSF_fnc_debugMsg;
        _t set ["lzPad", _pad];
        _t set ["deletePadOnFinish", true];
      };
      
      [_v, "LAND"] call YSF_fnc_setVehicleLandMode;

      if (isTouchingGround _v && unitReady _v) then { "advance" } else { "wait" }
    }],

    ["finally", {
      params ["_v","_t","_d"];

      _d params ["_destATL", ["_maxAlt", 20], ["_enableStabilization", true], ["_ignoreEn", true]];

      if (_enableStabilization) then {
        private _ix = YSF_STABILIZE_HELICOPTERS findIf { _v isEqualTo _x };
        if (_ix > -1) then {
          YSF_STABILIZE_HELICOPTERS deleteAt _ix;
          publicVariable "YSF_STABILIZE_HELICOPTERS";
        };
      };
     
      [_v] call YOSHI_rebootAI;
      
	    format ["[YSF_TransportTask] Finalizing transport task for vehicle %1", _v] call YSF_fnc_debugMsg;

      [_v, false] call YSF_fnc_setVehicleEngineState;

      private _pad = _t getOrDefault ["lzPad", objNull];
      if (!isNull _pad) then { 
        if (_t get ["deletePadOnFinish", false]) then { 
          deleteVehicle _pad; 
        };
        _t set ["lzPad", objNull]; 
      };

      "complete"
    }]
  ]
};
