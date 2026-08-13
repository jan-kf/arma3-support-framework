YSF_TRX_ARRIVAL_RADIUS = 120;
YSF_TRX_SETTLE_SECONDS = 3;
YSF_TRX_TASK_TIMEOUT = 300;

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
      _d params ["_destATL", ["_maxAlt", 20], ["_enableStabilization", true], ["_ignoreEn", false], ["_playRadio", true], ["_mode", "dispatch"]];

      if !(alive _v && {!isNull driver _v} && {alive driver _v}) exitWith {
        _v setVariable ["YSF_transport_state", "failed", true];
        "fail"
      };
      private _home = _v getVariable ["YSF_transport_homeATL", []];
      if !(_home isEqualType [] && {count _home >= 2}) then {
        _home = getPosATL _v;
        _v setVariable ["YSF_transport_homeATL", _home, true];
      };
      if (_mode isEqualTo "rtb") then { _destATL = _home; };
      _t set ["transportMode", _mode];
      _t set ["deadline", diag_tickTime + YSF_TRX_TASK_TIMEOUT];
      _t set ["groundSince", -1];
      _v setVariable ["YSF_transport_state", ["dispatching", "returning"] select (_mode isEqualTo "rtb"), true];
      _v setVariable ["YSF_transport_taskId", _t get "id", true];

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

      if (diag_tickTime > (_t getOrDefault ["deadline", diag_tickTime + 1])) exitWith { "fail" };

      if (random 1 < 0.1) then { [_v, _dest, "MOVE", 0] call YOSHI_setBasicWaypoint; };

      if ((_v distance2D _dest) <= _rad) then { "advance" } else { "wait" }
    }],

    ["end", {
      params ["_v","_t","_d"];
      private _dest = _t get "destATL";

      private _pad = _t getOrDefault ["lzPad", objNull];
      if (isNull _pad) then {
        private _newPadLoc = [_dest#0, _dest#1, 0];
        _pad = "Land_HelipadEmpty_F" createVehicle [0,0,0];
        _pad setPosATL _newPadLoc;

        format ["[YSF_TransportTask] Created Landing Pad at %1 - tick: %2", _newPadLoc, serverTime] call YSF_fnc_debugMsg;
        _t set ["lzPad", _pad];
        _t set ["deletePadOnFinish", true];
      };
      
      [_v, "LAND"] call YSF_fnc_setVehicleLandMode;

      if (diag_tickTime > (_t getOrDefault ["deadline", diag_tickTime + 1])) exitWith { "fail" };
      private _landed = isTouchingGround _v && {unitReady _v} && {(vectorMagnitude velocity _v) < 2};
      private _groundSince = _t getOrDefault ["groundSince", -1];
      if (_landed) then {
        if (_groundSince < 0) then { _groundSince = diag_tickTime; _t set ["groundSince", _groundSince]; };
      } else {
        _t set ["groundSince", -1];
      };
      if (_landed && {(diag_tickTime - _groundSince) >= YSF_TRX_SETTLE_SECONDS}) then { "advance" } else { "wait" }
    }],

    ["finally", {
      params ["_v","_t","_d"];

      _d params ["_destATL", ["_maxAlt", 20], ["_enableStabilization", true], ["_ignoreEn", true], ["_playRadio", true], ["_mode", "dispatch"]];

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

      private _finalState = if ((_t getOrDefault ["state", "running"]) in ["failed", "cancelled"]) then {
        _t get "state"
      } else {
        ["waiting", "home"] select (_mode isEqualTo "rtb")
      };
      _v setVariable ["YSF_transport_state", _finalState, true];

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

YSF_taskTransportAssign = {
  params ["_vehicle", "_task"];
  if (!isServer || {isNull _vehicle} || {typeName _task isNotEqualTo "HASHMAP"}) exitWith {false};
  private _existing = (call YSF__mgr) getOrDefault [str _vehicle, objNull];
  if (typeName _existing isEqualTo "HASHMAP" && {_existing getOrDefault ["enabled", false]}) exitWith {
    _vehicle setVariable ["YSF_transport_lastRequest", "duplicate_rejected", true];
    false
  };
  _vehicle setVariable ["YSF_transport_lastRequest", "accepted", true];
  [_vehicle, _task] call YSF_taskAssign;
  true
};

YSF_taskTransportAssignRemote = {
  params ["_vehicle", "_task"];
  if (isNull _vehicle || {typeName _task isNotEqualTo "HASHMAP"}) exitWith {false};
  private _taskId = _task getOrDefault ["id", str diag_tickTime];
  ["YSF_taskTransportAssign", [_vehicle, _task], format ["YSF_TRANSPORT_ASSIGN_%1_%2", netId _vehicle, _taskId], 5] call YCD_fnc_runOnServerOnce;
};
