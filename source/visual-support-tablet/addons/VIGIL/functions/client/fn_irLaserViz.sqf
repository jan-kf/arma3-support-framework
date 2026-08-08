YSF_irLaserViz_cleanupFakeLaser = {
  if (isNull player) exitWith {};
  private _fake = player getVariable ["YSF_irFakeLaserTarget", objNull];
  if (!isNull _fake) then {
    deleteVehicle _fake;
  };
  player setVariable ["YSF_irFakeLaserTarget", objNull, true];
};

YSF_irLaserViz_isIrPointerActive = {
  params ["_unit"];
  if (isNull _unit || {!alive _unit}) exitWith {false};
  if (vehicle _unit != _unit) exitWith {false};

  private _heldWeapon = currentWeapon _unit;
  if (_heldWeapon isEqualTo "") exitWith {false};

  private _attachments = _unit weaponAccessories _heldWeapon;
  if ((count _attachments) < 2) exitWith {false};

  private _pointer = toLower (_attachments select 1);
  if ((_pointer find "acc_pointer") < 0 || (_pointer find "_ir") < 0) exitWith {false};

  _unit isIRLaserOn _heldWeapon
};

YSF_irLaserViz_updateFakeLaser = {
  if (isNull player || {!alive player}) exitWith {
    call YSF_irLaserViz_cleanupFakeLaser;
  };

  if !([player] call YSF_irLaserViz_isIrPointerActive) exitWith {
    call YSF_irLaserViz_cleanupFakeLaser;
  };

  private _heldWeapon = currentWeapon player;
  private _dir = player weaponDirection _heldWeapon;
  if ((count _dir) < 3) then {_dir = eyeDirection player;};

  private _startASL = eyePos player;
  private _endASL = [
    (_startASL select 0) + ((_dir select 0) * 4000),
    (_startASL select 1) + ((_dir select 1) * 4000),
    (_startASL select 2) + ((_dir select 2) * 4000)
  ];
  private _fake = player getVariable ["YSF_irFakeLaserTarget", objNull];
  if (isNull _fake) then {
    private _cls = switch (side player) do {
      case west: {"LaserTargetW"};
      case east: {"LaserTargetE"};
      case resistance: {"LaserTargetC"};
      default {"LaserTargetC"};
    };
    _fake = createVehicle [_cls, ASLToAGL _endASL, [], 0, "CAN_COLLIDE"];
    _fake setPosASL _endASL;
    player setVariable ["YSF_irFakeLaserTarget", _fake, true];
  };

  private _cursorObj = cursorObject;
  if (!isNull _cursorObj && getObjectType _cursorObj == 8) then {
    _fake attachTo [_cursorObj, [0,0,0]];
  } else {
    private _hits = lineIntersectsSurfaces [_startASL, _endASL, player, objNull, true, 1, "GEOM", "FIRE"];
    if ((count _hits) > 0) then {
      private _hit = _hits select 0;
      private _hitPosASL = _hit select 0;
      private _hitObj = _hit select 2;
      if (!isNull _hitObj && getObjectType _hitObj == 8) then {
        _fake attachTo [_hitObj, [0,0,0]];
      } else {
        detach _fake;
        _fake setPosASL _hitPosASL;
      };
    } else {
      detach _fake;
      _fake setPosASL _endASL;
    };
  };
};

YSF_irLaserViz_drawBeam = {
  if (isNull player || {!alive player}) exitWith {};
  if (cameraView isEqualTo "GROUP") exitWith {};

  private _visionMode = currentVisionMode player;
  if ((_visionMode isEqualType 0) && {_visionMode isEqualTo 1}) exitWith {};

  private _heldWeapon = currentWeapon player;
  if (_heldWeapon isEqualTo "") exitWith {};

  private _attachments = player weaponAccessories _heldWeapon;
  if ((count _attachments) < 2) exitWith {};

  private _pointer = toLower (_attachments select 1);
  if ((_pointer find "acc_pointer") < 0 || (_pointer find "_ir") < 0) exitWith {};
  if (!(player isIRLaserOn _heldWeapon)) exitWith {};

  private _dir = player weaponDirection _heldWeapon;
  if ((count _dir) < 3) then {
    _dir = eyeDirection player;
  };

  private _fromATL = player modelToWorldVisual (player selectionPosition "righthand");
  private _color = missionNamespace getVariable ["YSF_laserVizColor", [0,1,0,1]];

  drawLaser [
    ATLToASL _fromATL,
    _dir,
    _color,
    [],
    1,
    0.1,
    -1,
    false
  ];
};

YSF_irLaserViz_init = {
  if (!hasInterface) exitWith {};
  if (uiNamespace getVariable ["YSF_irLaserViz_initialized", false]) exitWith {};
  uiNamespace setVariable ["YSF_irLaserViz_initialized", true];

  private _eh = addMissionEventHandler ["Draw3D", {
    call YSF_irLaserViz_drawBeam;
  }];
  uiNamespace setVariable ["YSF_irLaserViz_eh", _eh];

  private _pfh = [{
    call YSF_irLaserViz_updateFakeLaser;
  }, 0.2, []] call CBA_fnc_addPerFrameHandler;
  uiNamespace setVariable ["YSF_irLaserViz_pfh", _pfh];
};

YSF_irLaserViz_testReset = {
  if (!hasInterface) exitWith {};

  private _eh = uiNamespace getVariable ["YSF_irLaserViz_eh", -1];
  if (_eh >= 0) then {
    removeMissionEventHandler ["Draw3D", _eh];
    uiNamespace setVariable ["YSF_irLaserViz_eh", -1];
  };

  private _pfh = uiNamespace getVariable ["YSF_irLaserViz_pfh", -1];
  if (_pfh >= 0) then {
    [_pfh] call CBA_fnc_removePerFrameHandler;
    uiNamespace setVariable ["YSF_irLaserViz_pfh", -1];
  };

  call YSF_irLaserViz_cleanupFakeLaser;
  uiNamespace setVariable ["YSF_irLaserViz_initialized", false];
};
