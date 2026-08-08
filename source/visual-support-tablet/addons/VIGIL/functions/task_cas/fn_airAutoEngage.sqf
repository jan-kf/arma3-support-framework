YSF_AAE_ENABLED = true;
YSF_AAE_INTERVAL = 5;
YSF_AAE_FIRE_COOLDOWN = 8;
YSF_AAE_FACING_DEG = 120;
YSF_AAE_BOMB_FACING_DEG = 60;
YSF_AAE_BOMB_MIN_RELEASE_DISTANCE = 250;
YSF_AAE_TEMP_LASER_LIFETIME = 60;
YSF_AAE_TARGET_REENGAGE_MAX = 120;
YSF_AAE_SPAWN_WARMUP = 10;
YSF_AAE_DEBUG = true;

YSF_AAE_dbg = {
  params ["_msg"];
  if !(missionNamespace getVariable ["YSF_AAE_DEBUG", false]) exitWith {};

  if !(isNil "YCD_fnc_debugMsg") exitWith {
    [_msg, "YSF_AAE", "YSF_AAE_DEBUG"] call YCD_fnc_debugMsg;
  };

  if !(isNil "YSF_fnc_debugMsg") exitWith {
    _msg call YSF_fnc_debugMsg;
  };

  private _line = format ["[YSF_AAE] %1", _msg];
  systemChat _line;
  diag_log _line;
};

YSF_AAE_getFireController = {
  params ["_veh"];
  private _u = gunner _veh;
  if (isNull _u) then {_u = effectiveCommander _veh;};
  if (isNull _u) then {_u = driver _veh;};
  _u
};

YSF_AAE_isAIPilotedVehicle = {
  params ["_veh"];
  if (isNull _veh || {!alive _veh}) exitWith {false};

  private _pilot = driver _veh;
  if (isNull _pilot) exitWith {false};
  if (isPlayer _pilot) exitWith {false};

  private _uavControl = UAVControl _veh;
  if ((count _uavControl) > 0) then {
    private _controller = _uavControl # 0;
    if (!isNull _controller && {isPlayer _controller}) exitWith {false};
  };

  true
};

YSF_AAE_laserClassBySide = {
  params ["_side"];
  switch (_side) do {
    case west: {"LaserTargetW"};
    case east: {"LaserTargetE"};
    case resistance: {"LaserTargetC"};
    default {"LaserTargetC"};
  };
};

YSF_AAE_scheduleDelete = {
  params ["_obj", ["_delay", 60]];
  if (isNull _obj) exitWith {};
  [_obj, _delay] spawn {
    params ["_obj", "_delay"];
    uiSleep _delay;
    if (!isNull _obj) then {deleteVehicle _obj;};
  };
};

YSF_AAE_spawnTempLaser = {
  params ["_veh", "_target"];
  if (isNull _veh || {isNull _target}) exitWith {objNull};

  private _existing = _target getVariable ["YSF_AAE_attachedLaser", objNull];
  if (!isNull _existing && {alive _existing}) exitWith {_existing};

  private _laserCls = [side _veh] call YSF_AAE_laserClassBySide;
  if !(isClass (configFile >> "CfgVehicles" >> _laserCls)) then {
    _laserCls = "LaserTargetC";
  };

  private _laser = createVehicle [_laserCls, getPosASL _target, [], 0, "CAN_COLLIDE"];
  if (isNull _laser) exitWith {objNull};
  _laser attachTo [_target, [0,0,0]];
  _target setVariable ["YSF_AAE_attachedLaser", _laser, false];
  [_laser, missionNamespace getVariable ["YSF_AAE_TEMP_LASER_LIFETIME", 60]] call YSF_AAE_scheduleDelete;
  [_target, _laser] spawn {
    params ["_target", "_laser"];
    waitUntil {
      uiSleep 0.5;
      isNull _target || {!alive _target} || {isNull _laser}
    };
    if (!isNull _laser) then {deleteVehicle _laser;};
    if (!isNull _target) then {_target setVariable ["YSF_AAE_attachedLaser", objNull, false];};
  };
  [format ["temp laser created: veh=%1 laser=%2 target=%3", _veh, _laser, _target]] call YSF_AAE_dbg;
  _laser
};

YSF_AAE_isEligibleAirVehicle = {
  params ["_veh"];
  if (isNull _veh || {!alive _veh}) exitWith {false};
  if !(_veh isKindOf "Air") exitWith {false};
  // VIGIL fixed-wing assets have their own strike workflow and should not be
  // driven by the CAS auto-engage layer.
  if (_veh isKindOf "Plane") exitWith {false};
  if (!local _veh) exitWith {false};
  if ((crew _veh) isEqualTo []) exitWith {false};
  if !([_veh] call YSF_AAE_isAIPilotedVehicle) exitWith {false};
  true
};

YSF_AAE_swap3CBHellfireToScalpel = {
  params ["_veh"];
  if (isNull _veh || {!alive _veh}) exitWith {0};
  if (_veh getVariable ["YSF_AAE_hellfireSwapDone", false]) exitWith {0};

  private _changed = 0;
  private _pylons = getPylonMagazines _veh;
  private _p = [];
  {
    private _mag = _x;
    private _tag = toLower _mag;
    _p pushBack _mag;
    private _is3cbHellfire = ((_tag find "uk3cb_baf_pylonrack_") >= 0) && {(_tag find "hellfire") >= 0};
    if (_is3cbHellfire) then {
      private _pylonIdx = _forEachIndex + 1;
      _veh setPylonLoadOut [_pylonIdx, "PylonRack_4Rnd_LG_scalpel", true];
      _changed = _changed + 1;
    };
  } forEach _pylons;

  _veh setVariable ["YSF_AAE_hellfireSwapDone", true, false];
  if (_changed > 0) then {
    [format ["swapped 3CB Hellfire pylons to Scalpel: veh=%1 count=%2", _veh, _changed]] call YSF_AAE_dbg;
  };
  _changed
};

YSF_AAE_ammoInheritsFrom = {
  params ["_ammoClass", "_baseClass"];
  if (_ammoClass isEqualTo "" || {_baseClass isEqualTo ""}) exitWith {false};

  private _cfg = configFile >> "CfgAmmo" >> _ammoClass;
  if !(isClass _cfg) exitWith {false};

  private _needle = toLower _baseClass;
  private _cur = _cfg;
  private _safe = 0;
  private _success = false;
  while {isClass _cur && {_safe < 32}} do {
    private _name = toLower (configName _cur);
    if ((_name find _needle) >= 0) exitWith {_success = true};
    _cur = inheritsFrom _cur;
    _safe = _safe + 1;
  };
  _success
};

YSF_AAE_swapLaserBombCoreToBomb04 = {
  params ["_veh"];
  if (isNull _veh || {!alive _veh}) exitWith {0};
  if (_veh getVariable ["YSF_AAE_laserBombSwapDone", false]) exitWith {0};

  private _changed = 0;
  private _pylons = getPylonMagazines _veh;
  {
    private _mag = _x;
    if (_mag isNotEqualTo "") then {
      private _ammo = getText (configFile >> "CfgMagazines" >> _mag >> "ammo");
      private _isLaserBomb = [_ammo, "LaserBombCore"] call YSF_AAE_ammoInheritsFrom;
      if (_isLaserBomb) then {
        private _pylonIdx = _forEachIndex + 1;
        _veh setPylonLoadOut [_pylonIdx, "PylonRack_Bomb_GBU12_x2", true];
        _changed = _changed + 1;
      };
    };
  } forEach _pylons;

  _veh setVariable ["YSF_AAE_laserBombSwapDone", true, false];
  if (_changed > 0) then {
    [format ["swapped LaserBombCore pylons to Bomb_04: veh=%1 count=%2", _veh, _changed]] call YSF_AAE_dbg;
  };
  _changed
};

YSF_AAE_getGuidedOptions = {
  params ["_veh"];
  private _ret = _veh call YOSHI_GET_LGO;
  if !(_ret isEqualType [] && {(count _ret) > 1}) exitWith {[[], []]};
  private _bombs = _ret # 0;
  private _missiles = _ret # 1;
  if !(_bombs isEqualType []) then {_bombs = [];};
  if !(_missiles isEqualType []) then {_missiles = [];};
  [_bombs, _missiles]
};

YSF_AAE_normalizeWeaponClass = {
  params ["_value"];
  if (_value isEqualType "") exitWith {_value};
  if !(_value isEqualType []) exitWith {""};
  if ((count _value) <= 0) exitWith {""};
  private _w = _value # 0;
  if (_w isEqualType "") exitWith {_w};
  ""
};

YSF_AAE_weaponAmmoType = {
  params ["_weapon"];
  if (_weapon isEqualTo "") exitWith {""};
  private _mags = getArray (configFile >> "CfgWeapons" >> _weapon >> "magazines");
  if (_mags isEqualTo []) exitWith {""};
  getText (configFile >> "CfgMagazines" >> (_mags # 0) >> "ammo")
};

YSF_AAE_weaponAmmoCount = {
  params ["_veh", "_weapon"];
  if (_weapon isEqualTo "") exitWith {0};
  private _magsCfg = getArray (configFile >> "CfgWeapons" >> _weapon >> "magazines");
  private _vehMags = magazinesAmmoFull _veh;
  private _count = 0;
  {
    private _magClass = _x # 0;
    private _ammoLeft = _x # 1;
    if ((_magsCfg find _magClass) >= 0) then {
      _count = _count + (_ammoLeft max 0);
    };
  } forEach _vehMags;
  _count
};

YSF_AAE_weaponProfile = {
  params ["_veh", "_weapon"];
  private _ammoType = [_weapon] call YSF_AAE_weaponAmmoType;
  private _tag = toLower format ["%1|%2", _weapon, _ammoType];
  private _isBomb = ((_tag find "bomb") > -1) || ((_tag find "gbu") > -1) || ((_tag find "mk82") > -1);

  private _maxRange = 0;
  private _minAlt = 0;
  if (_isBomb) then {
    // Approximation: guided bomb glide envelope grows with altitude.
    private _altAGL = ((getPosASL _veh) # 2) - ((getTerrainHeightASL (getPosASL _veh) max 0));
    _minAlt = 120;
    _maxRange = (_altAGL max 100) * 5;
  } else {
    // Prefer explicit config range if provided.
    _maxRange = getNumber (configFile >> "CfgAmmo" >> _ammoType >> "maxControlRange");
    if (_maxRange <= 0) then {_maxRange = 4000;};
  };

  [_isBomb, _maxRange, _minAlt]
};

YSF_AAE_collectSensorEnemies = {
  params ["_veh"];
  private _raw = getSensorTargets _veh;
  if !(_raw isEqualType []) exitWith {[]};

  private _vehSide = side _veh;
  private _targets = [];
  {
    if (_x isEqualType [] && {(count _x) > 2}) then {
      private _obj = objNull;
      if ((_x # 0) isEqualType objNull) then {_obj = _x # 0;};
      if (isNull _obj && {(count _x) > 1} && {(_x # 1) isEqualType objNull}) then {
        _obj = _x # 1;
      };
      private _rel = _x # 2;
      private _enemy = false;
      if (_rel isEqualType "") then {
        private _relStr = toLower _rel;
        if (_relStr in ["enemy", "hostile"]) then {
          _enemy = true;
        } else {
          // Treat unknown contacts as enemy if side relationship is hostile.
          if (_relStr in ["unknown", ""]) then {
            if (!isNull _obj) then {
              private _objSide = side _obj;
              if !(_objSide isEqualTo sideUnknown) then {
                _enemy = (_vehSide getFriend _objSide) < 0.6;
              };
            };
          };
        };
      } else {
        if (_rel isEqualType 0) then {
          _enemy = _rel < 0.6;
        } else {
          if (_rel isEqualType sideUnknown) then {
            _enemy = (_vehSide getFriend _rel) < 0.6;
          };
        };
      };
      if (!isNull _obj && {alive _obj} && {_enemy}) then {
        _targets pushBackUnique _obj;
      };
    };
  } forEach _raw;
  _targets
};

YSF_AAE_targetKey = {
  params ["_target"];
  if (isNull _target) exitWith {""};
  private _k = netId _target;
  if (_k isEqualTo "") then {_k = str _target;};
  _k
};

YSF_AAE_isTargetOnCooldown = {
  params ["_veh", "_target"];
  private _k = [_target] call YSF_AAE_targetKey;
  if (_k isEqualTo "") exitWith {false};

  private _cd = _veh getVariable ["YSF_AAE_targetCooldowns", createHashMap];
  if !(typeName _cd isEqualTo "HASHMAP") then {_cd = createHashMap;};
  private _until = _cd getOrDefault [_k, -1];
  if (_until <= serverTime) then {
    _cd deleteAt _k;
    _veh setVariable ["YSF_AAE_targetCooldowns", _cd, false];
    false
  } else {
    true
  }
};

YSF_AAE_beginTargetCooldown = {
  params ["_veh", "_target", "_projectile", ["_maxWait", 60]];
  private _k = [_target] call YSF_AAE_targetKey;
  if (_k isEqualTo "") exitWith {};

  private _cd = _veh getVariable ["YSF_AAE_targetCooldowns", createHashMap];
  if !(typeName _cd isEqualTo "HASHMAP") then {_cd = createHashMap;};
  _cd set [_k, serverTime + _maxWait];
  _veh setVariable ["YSF_AAE_targetCooldowns", _cd, false];
};

YSF_AAE_pickEngagement = {
  params ["_veh", "_targets", "_bombs", "_missiles"];
  private _allWeapons = [];
  { _allWeapons pushBack _x; } forEach _missiles;
  { _allWeapons pushBack _x; } forEach _bombs;
  if (_allWeapons isEqualTo [] || {_targets isEqualTo []}) exitWith {[objNull, ""]};

  private _bestTarget = objNull;
  private _bestWeapon = "";
  private _bestScore = 1e10;

  {
    private _t = _x;
    if !([_veh, _t] call YSF_AAE_isTargetOnCooldown) then {
      private _dist = _veh distance2D _t;
      private _dirTo = [_veh, _t] call BIS_fnc_dirTo;
      private _delta = abs (((_dirTo - getDir _veh) + 540) % 360 - 180);

      if (_delta <= YSF_AAE_FACING_DEG) then {
        {
          private _w = [_x] call YSF_AAE_normalizeWeaponClass;
          if (_w isNotEqualTo "") then {
            private _ammoCount = [_veh, _w] call YSF_AAE_weaponAmmoCount;
            if (_ammoCount > 0) then {
              private _profile = [_veh, _w] call YSF_AAE_weaponProfile;
              private _isBomb = _profile # 0;
              private _maxRange = _profile # 1;
              private _minAlt = _profile # 2;
              private _altASL = (getPosASL _veh) # 2;
              private _altGround = getTerrainHeightASL (getPosASL _veh);
              private _altAGL = _altASL - _altGround;

              private _inEnvelope = (_dist <= _maxRange);
              if (_isBomb) then {
                private _bombFacing = missionNamespace getVariable ["YSF_AAE_BOMB_FACING_DEG", 60];
                private _bombMinDist = missionNamespace getVariable ["YSF_AAE_BOMB_MIN_RELEASE_DISTANCE", 250];
                _inEnvelope = _inEnvelope
                  && {_altAGL >= _minAlt}
                  && {_delta <= _bombFacing}
                  && {_dist >= _bombMinDist};
              };

              if (_inEnvelope) then {
                private _score = _dist + (_delta * 20) + (if (_isBomb) then {500} else {0});
                if (_score < _bestScore) then {
                  _bestScore = _score;
                  _bestTarget = _t;
                  _bestWeapon = _w;
                };
              };
            };
          };
        } forEach _allWeapons;
      };
    };
  } forEach _targets;

  [_bestTarget, _bestWeapon]
};

YSF_AAE_tryEngageLocal = {
  params ["_veh"];
  if !([_veh] call YSF_AAE_isEligibleAirVehicle) exitWith {false};
  if !(missionNamespace getVariable ["YSF_AAE_ENABLED", true]) exitWith {false};

  private _warmupUntil = _veh getVariable ["YSF_AAE_warmupUntil", -1];
  if (_warmupUntil > serverTime) exitWith {false};

  [_veh] call YSF_AAE_swap3CBHellfireToScalpel;
  [_veh] call YSF_AAE_swapLaserBombCoreToBomb04;

  private _nextAt = _veh getVariable ["YSF_AAE_nextShotAt", -1];
  if (serverTime < _nextAt) exitWith {false};

  private _opts = [_veh] call YSF_AAE_getGuidedOptions;
  private _bombs = _opts # 0;
  private _missiles = _opts # 1;
  if ((_bombs isEqualTo []) && (_missiles isEqualTo [])) exitWith {false};

  private _targets = [_veh] call YSF_AAE_collectSensorEnemies;
  if (_targets isEqualTo []) exitWith {false};

  private _pick = [_veh, _targets, _bombs, _missiles] call YSF_AAE_pickEngagement;
  private _targetObj = _pick # 0;
  private _weapon = _pick # 1;
  if (isNull _targetObj || {_weapon isEqualTo ""}) exitWith {false};

  private _profile = [_veh, _weapon] call YSF_AAE_weaponProfile;
  private _isBomb = _profile # 0;
  private _fireTarget = _targetObj;
  if (_isBomb) then {
    private _laser = [_veh, _targetObj] call YSF_AAE_spawnTempLaser;
    if (!isNull _laser) then {
      _fireTarget = _laser;
    };
  };

  private _ctrl = [_veh] call YSF_AAE_getFireController;
  private _fireUnit = if (!isNull _ctrl) then {_ctrl} else {_veh};
  _fireUnit reveal [_targetObj, 4];
  _fireUnit reveal [_fireTarget, 4];
  _fireUnit doWatch _fireTarget;
  _fireUnit doTarget _fireTarget;
  _fireUnit commandTarget _fireTarget;
  _fireUnit selectWeapon _weapon;
  if (canSuspend) then {uiSleep 0.2;};

  _veh setVariable ["YSF_AAE_lastProjectile", objNull, false];
  private _eh = _veh addEventHandler ["Fired", {
    params ["_unit", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];
    _unit setVariable ["YSF_AAE_lastProjectile", _projectile, false];
  }];

  private _ok = _fireUnit fireAtTarget [_fireTarget, _weapon];
  _veh removeEventHandler ["Fired", _eh];
  if (_ok) then {
    private _proj = _veh getVariable ["YSF_AAE_lastProjectile", objNull];
    [_veh, _targetObj, _proj, (missionNamespace getVariable ["YSF_AAE_TARGET_REENGAGE_MAX", 60])] call YSF_AAE_beginTargetCooldown;
    _veh setVariable ["YSF_AAE_nextShotAt", serverTime + YSF_AAE_FIRE_COOLDOWN, false];
    [format ["[YSF_AAE] fired veh=%1 weapon=%2 target=%3", _veh, _weapon, _targetObj]] call YSF_AAE_dbg;
  } else {
    _veh setVariable ["YSF_AAE_nextShotAt", serverTime + 2, false];
    [format ["[YSF_AAE] fire rejected veh=%1 weapon=%2 target=%3", _veh, _weapon, _targetObj]] call YSF_AAE_dbg;
  };
  _ok
};

YSF_AAE_tick = {
  {
    [_x] call YSF_AAE_tryEngageLocal;
  } forEach vehicles;
};

if (isNil "CBA_fnc_addPerFrameHandler") exitWith {};
if (missionNamespace getVariable ["YSF_AAE_started", false]) exitWith {};
missionNamespace setVariable ["YSF_AAE_started", true];

private _iv = missionNamespace getVariable ["YSF_AAE_INTERVAL", 5];
missionNamespace setVariable [
  "YSF_AAE_pfh",
  [YSF_AAE_tick, _iv, []] call CBA_fnc_addPerFrameHandler
];
