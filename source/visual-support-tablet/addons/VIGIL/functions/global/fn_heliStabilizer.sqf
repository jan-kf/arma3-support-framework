if (isNil "CBA_fnc_addPerFrameHandler") exitWith {"[YSF_HelicopterStab] CBA missing" call YSF_fnc_debugMsg;};

if (isNil "YSF_helicopterStab_MIN_SPEED") then { YSF_helicopterStab_MIN_SPEED = 25; };
if (isNil "YSF_helicopterStab_MIN_ALT") then { YSF_helicopterStab_MIN_ALT = 25; };
if (isNil "YSF_helicopterStab_TERRAIN_BUFFER") then { YSF_helicopterStab_TERRAIN_BUFFER = 20; };
if (isNil "YSF_helicopterStab_AHEAD") then { YSF_helicopterStab_AHEAD = [100,300,500]; };
if (isNil "YSF_helicopterStab_SAMPLE_INTERVAL") then { YSF_helicopterStab_SAMPLE_INTERVAL = 2; };

if (isNil "YSF_STABILIZE_HELICOPTERS") then { YSF_STABILIZE_HELICOPTERS = []; };
if (isNil "YSF_helicopterStab_helicopterDecel") then { YSF_helicopterStab_helicopterDecel = []; };
YSF_helicopterStab_pfhFrameId = nil;
YSF_helicopterStab_pfhSecondId = nil;

YSF_helicopterStab_perFrame = {
  params ["_t","_id"];
  if (isGamePaused) exitWith {};
  if ((count YSF_helicopterStab_helicopterDecel) == 0) exitWith {
    [_id] call CBA_fnc_removePerFrameHandler;
    YSF_helicopterStab_pfhFrameId = nil;
  };
  private _minSpd = YSF_helicopterStab_MIN_SPEED;
  for "_i" from ((count YSF_helicopterStab_helicopterDecel) - 1) to 0 step -1 do {
    private _e = YSF_helicopterStab_helicopterDecel # _i;
    _e params ["_helicopter","_initSpd","_initAlt","_initTime"];
    private _spd = speed _helicopter;
    private _alt = getPosASL _helicopter # 2;
    private _pitch = vectorDir _helicopter # 2;
    if (_alt < _initAlt || {_spd < _minSpd} || {_pitch <= 0}) then { YSF_helicopterStab_helicopterDecel deleteAt _i; continue; };
    private _altClimbed = _alt - _initAlt;
    private _vz = (velocity _helicopter # 2) max 1;
    private _force = _altClimbed^2 * _vz^2 * _pitch * getMass _helicopter * -0.01;
    _helicopter addForce [[0,0,_force], getCenterOfMass _helicopter];
  };
};

YSF_helicopterStab_startFramePFH = {
  if (!isNil "YSF_helicopterStab_pfhFrameId") exitWith {};
  YSF_helicopterStab_pfhFrameId = [YSF_helicopterStab_perFrame, 0, serverTime] call CBA_fnc_addPerFrameHandler;
  "[YSF_HelicopterStab] Culling Altitude..." call YSF_fnc_debugMsg;
};

YSF_helicopterStab_perSecond = {
  params ["","_id"];
  private _time = serverTime;
  private _minSpd = YSF_helicopterStab_MIN_SPEED;
  private _minAlt = YSF_helicopterStab_MIN_ALT;
  private _buf = YSF_helicopterStab_TERRAIN_BUFFER;
  private _ahead = YSF_helicopterStab_AHEAD;
  private _interval = YSF_helicopterStab_SAMPLE_INTERVAL;

  for "_i" from ((count YSF_STABILIZE_HELICOPTERS) - 1) to 0 step -1 do {
    private _helicopter = YSF_STABILIZE_HELICOPTERS # _i;
    if (isNull _helicopter) then { YSF_STABILIZE_HELICOPTERS deleteAt _i; continue; };

    private _spd = speed _helicopter;
    private _altASL = getPosASL _helicopter # 2;
    private _radAlt = getPos _helicopter # 2;

    if ((_helicopter getVariable ["YSF_helicopterStab_disable", false]) || {isPlayer currentPilot _helicopter} || {_spd < _minSpd} || {_radAlt < _minAlt}) then {
      private _ix = YSF_helicopterStab_helicopterDecel findIf { (_x # 0) isEqualTo _helicopter };
      if (_ix > -1) then { YSF_helicopterStab_helicopterDecel deleteAt _ix; };
      continue;
    };

    if !(local _helicopter && {alive _helicopter} && {isEngineOn _helicopter} && {isNull (remoteControlled driver _helicopter)}) then {
      private _ix2 = YSF_helicopterStab_helicopterDecel findIf { (_x # 0) isEqualTo _helicopter };
      if (_ix2 > -1) then { YSF_helicopterStab_helicopterDecel deleteAt _ix2; };
      continue;
    };

    private _skip = false;
    {
      if ((getTerrainHeightASL (_helicopter modelToWorld [0, _x, 0]) + _buf) > _altASL) exitWith { _skip = true; };
    } forEach _ahead;
    if (_skip) then {
      private _ix3 = YSF_helicopterStab_helicopterDecel findIf { (_x # 0) isEqualTo _helicopter };
      if (_ix3 > -1) then { YSF_helicopterStab_helicopterDecel deleteAt _ix3; };
      continue;
    };

    if (YSF_helicopterStab_helicopterDecel findIf { _helicopter isEqualTo (_x # 0) } > -1) then { continue; };

    private _sa = _helicopter getVariable ["YSF_helicopterStab_speedAlt", [-1,-1,-1]];
    _sa params ["_lastSpd","_lastAlt","_lastTime"];

    if (_lastTime + _interval < _time) then {
      _helicopter setVariable ["YSF_helicopterStab_speedAlt", [_spd, _altASL, _time]];
      continue;
    };

    if (_lastSpd > _spd && { _lastAlt < _altASL } && { vectorDir _helicopter # 2 > 0 }) then {
      YSF_helicopterStab_helicopterDecel pushBack [_helicopter, _spd, _altASL, _time];
    };

    if (isNil "YSF_helicopterStab_pfhFrameId") then { call YSF_helicopterStab_startFramePFH; };

    _helicopter setVariable ["YSF_helicopterStab_speedAlt", [_spd, _altASL, _time]];
  };
};

// trigger code:

// {
//   [_x, "Init", {
//     params ["_helicopter"];
//     YSF_STABILIZE_HELICOPTERS pushBackUnique _helicopter;
//   }, true, [], true] call CBA_fnc_addClassEventHandler;
// } forEach ["Helicopter","VTOL_Base_F"];

// [] spawn {
//   uiSleep 0.2;
//   { if (_x isKindOf "Helicopter" || {_x isKindOf "VTOL_Base_F"}) then { YSF_STABILIZE_HELICOPTERS pushBackUnique _x; }; } forEach vehicles;
// };

