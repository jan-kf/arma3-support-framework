if (isNil "YSF_fnc_debugMsg") then {
  YSF_fnc_debugMsg = {
    params ["_msg"];
    diag_log format ["[YSF] %1", _msg];
    if (hasInterface) then {
      systemChat format ["[YSF] %1", _msg];
    };
  };
};

YSF_fwLaserTestClassifyMagazine = {
  params ["_mag"];

  private _ammoClass = getText (configFile >> "CfgMagazines" >> _mag >> "ammo");
  private _laserLock = 0;
  private _irLock = 0;
  private _radarLock = 0;
  private _manualControl = 0;
  private _simulation = "";
  private _classification = "unknown";

  if !(_ammoClass isEqualTo "") then {
    _laserLock = getNumber (configFile >> "CfgAmmo" >> _ammoClass >> "laserLock");
    _irLock = getNumber (configFile >> "CfgAmmo" >> _ammoClass >> "irLock");
    _radarLock = getNumber (configFile >> "CfgAmmo" >> _ammoClass >> "airLock");
    _manualControl = getNumber (configFile >> "CfgAmmo" >> _ammoClass >> "manualControl");
    _simulation = toLower getText (configFile >> "CfgAmmo" >> _ammoClass >> "simulation");
  };

  if (_laserLock > 0) then {
    _classification = "laser-trackable";
  } else {
    if ((_manualControl > 0) || {_irLock > 0} || {_radarLock > 0}) then {
      _classification = "guided-nonlaser";
    } else {
      if ((_simulation find "missile") > -1 || {(_simulation find "bomb") > -1}) then {
        _classification = "likely-dumbfire";
      } else {
        _classification = "unguided-or-unknown";
      };
    };
  };

  [_ammoClass, _laserLock, _irLock, _radarLock, _manualControl, _simulation, _classification]
};

YSF_fwLaserTestFindWeaponForMagazine = {
  params ["_veh", "_mag", ["_turretPath", [-1]], ["_pylonIndex", -1]];
  private _weapon = "";

  private _pylonWeapon = getText (configFile >> "CfgMagazines" >> _mag >> "pylonWeapon");
  if !(_pylonWeapon isEqualTo "") exitWith {_pylonWeapon};

  private _candidates = [];
  _candidates append (weapons _veh);
  if ((typeName _turretPath) isEqualTo "ARRAY") then {
    _candidates append (_veh weaponsTurret _turretPath);
  };
  {
    _candidates append (_veh weaponsTurret _x);
  } forEach (allTurrets [_veh, true]);
  _candidates = _candidates arrayIntersect _candidates;

  {
    private _cfgMags = getArray (configFile >> "CfgWeapons" >> _x >> "magazines");
    if ((_cfgMags find _mag) > -1) exitWith {
      _weapon = _x;
    };
  } forEach _candidates;

  _weapon
};

YSF_fwLaserTestCollectTargets = {
  params ["_veh", ["_radius", 1000]];
  if (isNull _veh) exitWith {[]};

  private _classes = ["LaserTargetW", "LaserTargetE", "LaserTargetC", "LaserTargetO"];
  private _targets = [];

  {
    _targets append (allMissionObjects _x);
  } forEach _classes;

  _targets = _targets arrayIntersect _targets;
  _targets = _targets select {
    !isNull _x
    && {alive _x}
    && {(_x distance2D _veh) <= _radius}
  };

  _targets
};

YSF_fwLaserTestAssessTracking = {
  params ["_projectile", "_target", ["_window", 12], ["_sampleStep", 0.01], ["_impactRadius", 20]];

  private _startDist = -1;
  private _minDist = -1;
  private _endDist = -1;
  private _samples = 0;
  private _closingTicks = 0;
  private _alignedTicks = 0;
  private _trackedByImpactLikely = false;
  private _trackedLikely = false;
  private _status = "no-projectile";

  if (isNull _projectile || {isNull _target}) exitWith {
    [_trackedLikely, _trackedByImpactLikely, _status, _startDist, _minDist, _endDist, _samples, _closingTicks, _alignedTicks]
  };

  _status = "sampled";
  _startDist = _projectile distance _target;
  _minDist = _startDist;
  private _prevDist = _startDist;
  private _deadline = time + (_window max 0.5);

  waitUntil {
    uiSleep (_sampleStep max 0.02);
    _samples = _samples + 1;

    if (isNull _projectile) exitWith {true};

    private _dist = _projectile distance _target;
    if (_dist < _minDist) then {_minDist = _dist;};
    if (_dist < (_prevDist - 0.5)) then {
      _closingTicks = _closingTicks + 1;
    };

    private _vel = velocity _projectile;
    if ((vectorMagnitude _vel) > 3) then {
      private _toTarget = (getPosASL _target) vectorDiff (getPosASL _projectile);
      if ((vectorMagnitude _toTarget) > 1) then {
        private _dot = (vectorNormalized _vel) vectorDotProduct (vectorNormalized _toTarget);
        if (_dot > 0.92) then {
          _alignedTicks = _alignedTicks + 1;
        };
      };
    };

    _prevDist = _dist;
    time >= _deadline
  };

  if (isNull _projectile) then {
    _endDist = _minDist;
    _status = "projectile-ended";
  } else {
    _endDist = _projectile distance _target;
  };

  private _ratio = if (_startDist > 0.1) then {_minDist / _startDist} else {1};
  _trackedByImpactLikely = (_minDist >= 0) && {_minDist <= (_impactRadius max 1)};
  _trackedLikely = (_samples > 3) && (
    (_ratio < 0.35)
    || {_minDist < 35}
    || {(_closingTicks >= 6) && (_alignedTicks >= 6)}
  );
  if (_trackedByImpactLikely) then {_trackedLikely = true;};

  [_trackedLikely, _trackedByImpactLikely, _status, _startDist, _minDist, _endDist, _samples, _closingTicks, _alignedTicks]
};

YSF_fwLaserTestIsBombLike = {
  params ["_weapon", "_mag", "_ammoClass"];
  private _token = toLower format ["%1|%2|%3", _weapon, _mag, _ammoClass];
  ((_token find "bomb") > -1)
  || {(_token find "gbu") > -1}
  || {(_token find "mk82") > -1}
  || {(_token find "cluster") > -1}
  || {(_token find "lgb") > -1}
};

YSF_fwLaserTestAssessLaserGuidance = {
  params ["_row"];
  private _impact = _row getOrDefault ["trackedByImpactLikely", false];
  private _laserLock = _row getOrDefault ["laserLock", 0];
  private _irLock = _row getOrDefault ["irLock", 0];
  private _manual = _row getOrDefault ["manualControl", 0];
  private _fired = _row getOrDefault ["fired", false];
  private _status = _row getOrDefault ["trackingStatus", ""];
  private _class = _row getOrDefault ["classification", ""];

  private _assessment = "none";
  private _reason = "no-impact-evidence";

  if (!_fired) exitWith {[_assessment, "did-not-fire"]};
  if (_status isEqualTo "no-projectile") exitWith {[_assessment, "no-projectile"]};

  if (_impact) then {
    if (_laserLock > 0) exitWith {["high", "impact+laserLock"]};
    if ((_irLock > 0) || {_manual > 0}) exitWith {["medium", "impact+guided-nonlaser-config"]};
    if (_class isEqualTo "laser-trackable") exitWith {["medium", "impact+laser-classification"]};
    ["low", "impact-only"]
  } else {
    if (_laserLock > 0) exitWith {["low", "laserLock-but-no-impact"]};
    ["none", "no-impact-evidence"]
  }
};

YSF_fwLaserTestSelectWeapon = {
  params ["_veh", "_weapon", ["_turretPath", [-1]]];
  private _selectedWeapon = "";
  private _selectionOk = false;

  if (_weapon isEqualTo "") exitWith {[_selectionOk, _selectedWeapon]};

  if ((typeName _turretPath) isEqualTo "ARRAY") then {
    _veh selectWeaponTurret [_weapon, _turretPath];
    uiSleep 0.1;
    _selectedWeapon = _veh currentWeaponTurret _turretPath;
    _selectionOk = _selectedWeapon isEqualTo _weapon;
  };

  if (!_selectionOk) then {
    _veh selectWeapon _weapon;
    uiSleep 0.1;
    _selectedWeapon = currentWeapon _veh;
    _selectionOk = _selectedWeapon isEqualTo _weapon;
  };

  [_selectionOk, _selectedWeapon]
};

YSF_fwLaserTestFireWeapon = {
  params ["_veh", "_target", "_weapon", ["_turretPath", [-1]], ["_forceOnly", false]];
  private _fireMethod = "none";
  private _commandAccepted = false;
  private _muzzles = getArray (configFile >> "CfgWeapons" >> _weapon >> "muzzles");
  if (_muzzles isEqualTo []) then {_muzzles = [_weapon];};

  if (!_forceOnly) then {
    _commandAccepted = _veh fireAtTarget [_target, _weapon];
  };
  if (_commandAccepted) exitWith {
    _fireMethod = "fireAtTarget";
    [_commandAccepted, _fireMethod]
  };

  {
    _veh forceWeaponFire [_x, _x];
    _fireMethod = format ["forceWeaponFire:%1", _x];
    _commandAccepted = true;
    uiSleep 0.05;
  } forEach _muzzles;

  [_commandAccepted, _fireMethod]
};

YSF_fwLaserTestStoreRunServer = {
  params ["_run"];
  if (!isServer) exitWith {
    [format ["FW Laser Test: forwarding run to server (client=%1).", clientOwner]] call YSF_fnc_debugMsg;
    [_run] remoteExecCall ["YSF_fwLaserTestStoreRunServer", 2];
  };

  private _runId = _run getOrDefault ["runId", "unknown"];
  private _allRuns = missionNamespace getVariable ["YSF_fwLaserTestRuns", []];
  _allRuns pushBack _run;
  missionNamespace setVariable ["YSF_fwLaserTestRuns", _allRuns, true];
  missionNamespace setVariable ["YSF_fwLaserTestLastRun", _run, true];
  [format ["FW Laser Test [%1] stored on server. totalRuns=%2", _runId, count _allRuns]] call YSF_fnc_debugMsg;
};

YSF_fwLaserTestPrintLast = {
  private _run = missionNamespace getVariable ["YSF_fwLaserTestLastRun", createHashMap];
  if !(typeName _run isEqualTo "HASHMAP") exitWith {
    "FW Laser Test: no run data found." call YSF_fnc_debugMsg;
  };

  private _runId = _run getOrDefault ["runId", "unknown"];
  private _vehType = _run getOrDefault ["vehicleType", "unknown"];
  private _total = _run getOrDefault ["totalTests", 0];
  private _fired = _run getOrDefault ["firedCount", 0];
  private _tracked = _run getOrDefault ["trackedLikelyCount", 0];
  private _laser = _run getOrDefault ["laserClassifiedCount", 0];
  private _dumb = _run getOrDefault ["likelyDumbfireCount", 0];

  [
    format [
      "FW Laser Test [%1] veh=%2 tests=%3 fired=%4 tracked=%5 laser=%6 dumb=%7",
      _runId,
      _vehType,
      _total,
      _fired,
      _tracked,
      _laser,
      _dumb
    ]
  ] call YSF_fnc_debugMsg;
};

YSF_fwLaserTestRunLocal = {
  params [
    "_veh",
    ["_radius", 1000],
    ["_cooldown", 2],
    ["_acqDelay", 0.75],
    ["_maxTests", 120],
    ["_impactRadius", 20],
    ["_minBombReleaseAltASL", 350]
  ];

  if (isNull _veh || {!alive _veh}) exitWith {};
  if !(local _veh) exitWith {};

  private _runId = format ["FWLT_%1_%2", netId _veh, round (serverTime * 100)];
  [
    format [
      "FW Laser Test [%1] local start: veh=%2 owner=%3 local=%4 radius=%5 cooldown=%6 acq=%7 max=%8",
      _runId,
      typeOf _veh,
      owner _veh,
      local _veh,
      _radius,
      _cooldown,
      _acqDelay,
      _maxTests
    ]
  ] call YSF_fnc_debugMsg;
  private _targets = [_veh, _radius] call YSF_fwLaserTestCollectTargets;
  private _pylons = getAllPylonsInfo _veh;
  private _originalPylons = [_veh] call YOSHI_GET_PYLON_INFO;
  private _results = [];
  [
    format [
      "FW Laser Test [%1] discovered targets=%2 pylons=%3",
      _runId,
      count _targets,
      count _pylons
    ]
  ] call YSF_fnc_debugMsg;

  if (_targets isEqualTo []) exitWith {
    private _run = createHashMapFromArray [
      ["runId", _runId],
      ["vehicleType", typeOf _veh],
      ["vehicleNetId", netId _veh],
      ["owner", owner _veh],
      ["status", "no_targets"],
      ["totalTests", 0],
      ["firedCount", 0],
      ["laserClassifiedCount", 0],
      ["likelyDumbfireCount", 0],
      ["results", []]
    ];
    [_run] call YSF_fwLaserTestStoreRunServer;
    [format ["FW Laser Test [%1] aborted: no laser targets in %2m.", _runId, _radius]] call YSF_fnc_debugMsg;
  };

  private _ctx = createHashMapFromArray [
    ["fired", false],
    ["weapon", ""],
    ["muzzle", ""],
    ["mode", ""],
    ["ammo", ""],
    ["magazine", ""],
    ["projectileType", ""],
    ["projectileObj", objNull]
  ];
  _veh setVariable ["YSF_fwLaserTestEHCtx", _ctx, false];

  private _eh = _veh addEventHandler ["Fired", {
    params ["_unit", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];
    private _state = _unit getVariable ["YSF_fwLaserTestEHCtx", createHashMap];
    _state set ["fired", true];
    _state set ["weapon", _weapon];
    _state set ["muzzle", _muzzle];
    _state set ["mode", _mode];
    _state set ["ammo", _ammo];
    _state set ["magazine", _magazine];
    _state set ["projectileType", typeOf _projectile];
    _state set ["projectileObj", _projectile];
    _unit setVariable ["YSF_fwLaserTestEHCtx", _state, false];
  }];

  private _stop = false;
  private _tested = 0;

  {
    if (_stop) exitWith {};
    private _pylonIndex = _x select 0;
    private _turretPath = _x select 2;
    private _compatibleMags = _veh getCompatiblePylonMagazines _pylonIndex;
    _compatibleMags = _compatibleMags arrayIntersect _compatibleMags;
    [
      format [
        "FW Laser Test [%1] pylon=%2 turret=%3 compatibleMags=%4",
        _runId,
        _pylonIndex,
        str _turretPath,
        count _compatibleMags
      ]
    ] call YSF_fnc_debugMsg;

    {
      if (_stop) exitWith {};
      if (_tested >= _maxTests) then {
        _stop = true;
      };
      if (_stop) exitWith {};

      private _mag = _x;
      _veh setPylonLoadout [_pylonIndex, _mag, true, _turretPath];
      uiSleep 0.2;

      private _weapon = [_veh, _mag, _turretPath, _pylonIndex] call YSF_fwLaserTestFindWeaponForMagazine;
      [format ["FW Laser Test [%1] test=%2 pylon=%3 mag=%4 weapon=%5", _runId, _tested + 1, _pylonIndex, _mag, _weapon]] call YSF_fnc_debugMsg;
      if (_weapon isEqualTo "") then {
        private _skip = createHashMapFromArray [
          ["pylonIndex", _pylonIndex],
          ["turretPath", _turretPath],
          ["magazine", _mag],
          ["pylonWeaponCfg", getText (configFile >> "CfgMagazines" >> _mag >> "pylonWeapon")],
          ["weapon", ""],
          ["status", "skip-no-weapon"]
        ];
        _results pushBack _skip;
        _tested = _tested + 1;
      } else {
        private _target = _targets select (_tested mod (count _targets));
        private _targetType = typeOf _target;
        private _targetNetId = netId _target;
        private _targetPos = getPosASL _target;

        private _classData = [_mag] call YSF_fwLaserTestClassifyMagazine;
        private _ammoClass = _classData select 0;
        private _laserLock = _classData select 1;
        private _irLock = _classData select 2;
        private _radarLock = _classData select 3;
        private _manualControl = _classData select 4;
        private _simulation = _classData select 5;
        private _classification = _classData select 6;
        private _vehAltASL = (getPosASL _veh) select 2;
        private _isBombLike = [_weapon, _mag, _ammoClass] call YSF_fwLaserTestIsBombLike;
        if (_isBombLike && {_vehAltASL < _minBombReleaseAltASL}) then {
          private _skipBomb = createHashMapFromArray [
            ["pylonIndex", _pylonIndex],
            ["turretPath", _turretPath],
            ["magazine", _mag],
            ["weapon", _weapon],
            ["ammoClass", _ammoClass],
            ["classification", _classification],
            ["laserLock", _laserLock],
            ["irLock", _irLock],
            ["manualControl", _manualControl],
            ["simulation", _simulation],
            ["vehicleAltASL", _vehAltASL],
            ["status", "skip-low-alt-bomb"],
            ["skipReason", format ["bomb-like payload below minBombReleaseAltASL=%1", _minBombReleaseAltASL]]
          ];
          _results pushBack _skipBomb;
          _tested = _tested + 1;
          [format ["FW Laser Test [%1] skip: bomb-like mag=%2 altASL=%3 below %4", _runId, _mag, round _vehAltASL, _minBombReleaseAltASL]] call YSF_fnc_debugMsg;
        } else {

          _veh setVariable [
            "YSF_fwLaserTestEHCtx",
            createHashMapFromArray [
              ["fired", false],
              ["weapon", ""],
              ["muzzle", ""],
              ["mode", ""],
              ["ammo", ""],
              ["magazine", ""],
              ["projectileType", ""],
              ["projectileObj", objNull]
            ],
            false
          ];

          _veh reveal [_target, 4];
          _veh doWatch _target;
          _veh doTarget _target;
          _veh commandTarget _target;
          uiSleep _acqDelay;

          private _sel = [_veh, _weapon, _turretPath] call YSF_fwLaserTestSelectWeapon;
          private _selectionOk = _sel select 0;
          private _selectedWeapon = _sel select 1;
          private _fire = [_veh, _target, _weapon, _turretPath] call YSF_fwLaserTestFireWeapon;
          private _firedRet = _fire select 0;
          private _fireMethod = _fire select 1;
          private _fallbackAttempted = false;
          private _fallbackAccepted = false;
          private _deadline = time + (_cooldown max 0.5);
          waitUntil {
            uiSleep 0.1;
            (time >= _deadline) || {((_veh getVariable ["YSF_fwLaserTestEHCtx", createHashMap]) getOrDefault ["fired", false])}
          };

          private _firedCtx = _veh getVariable ["YSF_fwLaserTestEHCtx", createHashMap];
          private _firedEH = _firedCtx getOrDefault ["fired", false];
          if (!_firedEH) then {
            _fallbackAttempted = true;
            private _force = [_veh, _target, _weapon, _turretPath, true] call YSF_fwLaserTestFireWeapon;
            _fallbackAccepted = _force select 0;
            private _fallbackMethod = _force select 1;
            if (_fallbackAccepted && !(_fallbackMethod isEqualTo "none")) then {
              if (_fireMethod isEqualTo "none") then {
                _fireMethod = _fallbackMethod;
              } else {
                _fireMethod = format ["%1|%2", _fireMethod, _fallbackMethod];
              };
            };
            private _deadlineFallback = time + 0.6;
            waitUntil {
              uiSleep 0.05;
              (time >= _deadlineFallback) || {((_veh getVariable ["YSF_fwLaserTestEHCtx", createHashMap]) getOrDefault ["fired", false])}
            };
            _firedCtx = _veh getVariable ["YSF_fwLaserTestEHCtx", createHashMap];
            _firedEH = _firedCtx getOrDefault ["fired", false];
          };
          private _projectileObj = _firedCtx getOrDefault ["projectileObj", objNull];
          private _fired = _firedEH || {!isNull _projectileObj};
          private _tracking = [_projectileObj, _target, 12, 0.01, _impactRadius] call YSF_fwLaserTestAssessTracking;
          private _trackedLikely = _tracking select 0;
          private _trackedByImpactLikely = _tracking select 1;
          private _trackingStatus = _tracking select 2;
          private _trackingStartDist = _tracking select 3;
          private _trackingMinDist = _tracking select 4;
          private _trackingEndDist = _tracking select 5;
          private _trackingSamples = _tracking select 6;
          private _trackingClosingTicks = _tracking select 7;
          private _trackingAlignedTicks = _tracking select 8;
          [
            format [
              "FW Laser Test [%1] fired: pylon=%2 mag=%3 weapon=%4 selected=%5 selectionOk=%6 method=%7 target=%8 firedRet=%9 firedEH=%10 tracked=%11 impactLikely=%12 minDist=%13",
              _runId,
              _pylonIndex,
              _mag,
              _weapon,
              _selectedWeapon,
              _selectionOk,
              _fireMethod,
              _targetType,
              _firedRet,
              _firedEH,
              _trackedLikely,
              _trackedByImpactLikely,
              _trackingMinDist
            ]
          ] call YSF_fnc_debugMsg;

          private _row = createHashMapFromArray [
            ["pylonIndex", _pylonIndex],
            ["turretPath", _turretPath],
            ["magazine", _mag],
            ["weapon", _weapon],
            ["selectedWeapon", _selectedWeapon],
            ["selectionOk", _selectionOk],
            ["fireMethod", _fireMethod],
            ["ammoClass", _ammoClass],
            ["classification", _classification],
            ["laserLock", _laserLock],
            ["irLock", _irLock],
            ["airLock", _radarLock],
            ["manualControl", _manualControl],
            ["simulation", _simulation],
            ["vehicleAltASL", _vehAltASL],
            ["isBombLike", _isBombLike],
            ["targetType", _targetType],
            ["targetNetId", _targetNetId],
            ["targetPosASL", _targetPos],
            ["firedReturn", _firedRet],
            ["fallbackAttempted", _fallbackAttempted],
            ["fallbackAccepted", _fallbackAccepted],
            ["firedEH", _firedEH],
            ["fired", _fired],
            ["trackedLikely", _trackedLikely],
            ["trackedByImpactLikely", _trackedByImpactLikely],
            ["trackingStatus", _trackingStatus],
            ["trackingStartDist", _trackingStartDist],
            ["trackingMinDist", _trackingMinDist],
            ["trackingEndDist", _trackingEndDist],
            ["trackingSamples", _trackingSamples],
            ["trackingClosingTicks", _trackingClosingTicks],
            ["trackingAlignedTicks", _trackingAlignedTicks],
            ["eventWeapon", _firedCtx getOrDefault ["weapon", ""]],
            ["eventMuzzle", _firedCtx getOrDefault ["muzzle", ""]],
            ["eventMode", _firedCtx getOrDefault ["mode", ""]],
            ["eventAmmo", _firedCtx getOrDefault ["ammo", ""]],
            ["eventMagazine", _firedCtx getOrDefault ["magazine", ""]],
            ["eventProjectileType", _firedCtx getOrDefault ["projectileType", ""]],
            ["time", serverTime]
          ];
          private _laserAssess = [_row] call YSF_fwLaserTestAssessLaserGuidance;
          _row set ["laserGuidanceAssessment", _laserAssess select 0];
          _row set ["laserGuidanceReason", _laserAssess select 1];
          _results pushBack _row;
          _tested = _tested + 1;
        };
      };
    } forEach _compatibleMags;
  } forEach _pylons;

  _veh removeEventHandler ["Fired", _eh];
  [_veh, _originalPylons] call YOSHI_SET_VEHICLE_PYLONS;

  private _firedCount = {_x getOrDefault ["fired", false]} count _results;
  private _laserCount = {_x getOrDefault ["classification", ""] isEqualTo "laser-trackable"} count _results;
  private _dumbCount = {_x getOrDefault ["classification", ""] isEqualTo "likely-dumbfire"} count _results;
  private _trackedLikelyCount = {_x getOrDefault ["trackedLikely", false]} count _results;
  private _laserGuidanceHighCount = {_x getOrDefault ["laserGuidanceAssessment", ""] isEqualTo "high"} count _results;
  private _laserGuidanceMediumCount = {_x getOrDefault ["laserGuidanceAssessment", ""] isEqualTo "medium"} count _results;
  private _laserGuidanceLowCount = {_x getOrDefault ["laserGuidanceAssessment", ""] isEqualTo "low"} count _results;
  private _laserGuidanceNoneCount = {_x getOrDefault ["laserGuidanceAssessment", ""] isEqualTo "none"} count _results;
  private _skippedLowAltBombCount = {_x getOrDefault ["status", ""] isEqualTo "skip-low-alt-bomb"} count _results;

  private _run = createHashMapFromArray [
    ["runId", _runId],
    ["vehicleType", typeOf _veh],
    ["vehicleNetId", netId _veh],
    ["owner", owner _veh],
    ["status", "complete"],
    ["targetCount", count _targets],
    ["totalTests", count _results],
    ["firedCount", _firedCount],
    ["trackedLikelyCount", _trackedLikelyCount],
    ["laserGuidanceHighCount", _laserGuidanceHighCount],
    ["laserGuidanceMediumCount", _laserGuidanceMediumCount],
    ["laserGuidanceLowCount", _laserGuidanceLowCount],
    ["laserGuidanceNoneCount", _laserGuidanceNoneCount],
    ["skippedLowAltBombCount", _skippedLowAltBombCount],
    ["laserClassifiedCount", _laserCount],
    ["likelyDumbfireCount", _dumbCount],
    ["cooldown", _cooldown],
    ["acqDelay", _acqDelay],
    ["impactRadius", _impactRadius],
    ["minBombReleaseAltASL", _minBombReleaseAltASL],
    ["radius", _radius],
    ["results", _results]
  ];

  [_run] call YSF_fwLaserTestStoreRunServer;
  [
    format [
      "FW Laser Test [%1] done: tests=%2 fired=%3 laser=%4 dumb=%5",
      _runId,
      count _results,
      _firedCount,
      _laserCount,
      _dumbCount
    ]
  ] call YSF_fnc_debugMsg;
};

YSF_fwLaserTestStart = {
  params [
    "_veh",
    ["_radius", 1000],
    ["_cooldown", 2],
    ["_acqDelay", 0.75],
    ["_maxTests", 120],
    ["_impactRadius", 20],
    ["_minBombReleaseAltASL", 350]
  ];

  if (isNull _veh || {!alive _veh}) exitWith {
    "FW Laser Test: invalid vehicle." call YSF_fnc_debugMsg;
    false
  };

  [
    format [
      "FW Laser Test: start requested veh=%1 netId=%2 owner=%3 local=%4 radius=%5 cooldown=%6 acq=%7 max=%8 impactRadius=%9",
      typeOf _veh,
      netId _veh,
      owner _veh,
      local _veh,
      _radius,
      _cooldown,
      _acqDelay,
      _maxTests,
      _impactRadius
    ]
  ] call YSF_fnc_debugMsg;
  [format ["FW Laser Test: minBombReleaseAltASL=%1", _minBombReleaseAltASL]] call YSF_fnc_debugMsg;

  if (!local _veh) exitWith {
    [format ["FW Laser Test: rerouting to vehicle owner %1.", owner _veh]] call YSF_fnc_debugMsg;
    ["YSF_fwLaserTestStart", _veh, _this] call YCD_fnc_runOnObjectOwner;
    true
  };

  "FW Laser Test: running locally on vehicle owner." call YSF_fnc_debugMsg;
  _this spawn YSF_fwLaserTestRunLocal;
  true
};
