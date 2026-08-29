#include "..\..\ui\idc.hpp"

YSF_FW_UAV_DEPLOY_DISABLED_REASON = "Fixed-wing UAV deploy is temporarily disabled because it is unstable right now.";

YSF_fwIsDisabledDeployType = {
  params [["_vehicleType", ""]];
  if (_vehicleType isEqualTo "") exitWith {false};

  (_vehicleType isKindOf "Plane")
  && {(getNumber (configFile >> "CfgVehicles" >> _vehicleType >> "isUav")) > 0}
};

YOSHI_taskFW_GetSelection = {
  private _id = uiNamespace getVariable ["YSF_current_selected_fw_id", ""];
  if (_id isEqualTo "") exitWith {[objNull, "", 0]};

  private _entry = [_id] call YSF_fwGetEntry;
  if !(typeName _entry isEqualTo "HASHMAP") exitWith {[objNull, "", 0]};

  [_entry, _entry getOrDefault ["state", ""], _entry getOrDefault ["roleMask", 0]]
};

YOSHI_taskFW_SetEnabled = {
  params ["_grp", "_idc", "_enabled"];
  private _ctrl = _grp controlsGroupCtrl _idc;
  if (!isNull _ctrl) then {
    _ctrl ctrlEnable _enabled;
    _ctrl ctrlSetFade (if (_enabled) then {0} else {0.4});
    _ctrl ctrlCommit 0;
  };
};

YOSHI_taskFW_SetVisible = {
  params ["_grp", "_idc", "_visible"];
  private _ctrl = _grp controlsGroupCtrl _idc;
  if (!isNull _ctrl) then {
    _ctrl ctrlShow _visible;
    _ctrl ctrlEnable _visible;
  };
};

YSF_fwGetDesignatorSide = {
  params ["_obj"];
  if (isNull _obj) exitWith {sideUnknown};
  if (_obj isKindOf "Man") exitWith {side _obj};

  private _cmd = effectiveCommander _obj;
  if (!isNull _cmd) exitWith {side _cmd};

  private _objSide = side _obj;
  if !(_objSide isEqualTo sideUnknown) exitWith {_objSide};

  private _cfgSide = getNumber (configFile >> "CfgVehicles" >> typeOf _obj >> "side");
  switch (_cfgSide) do {
    case 0: {east};
    case 1: {west};
    case 2: {resistance};
    case 3: {civilian};
    default {sideUnknown};
  };
};

YOSHI_taskFW_GetLaserDesignators = {
  private _out = [];
  private _sources = +allPlayers;
  {
    private _veh = _x;
    if (!isNull _veh && {alive _veh} && {unitIsUAV _veh}) then {
      _sources pushBackUnique _veh;
    };
  } forEach vehicles;

  {
    private _unit = _x;
    if (
      !isNull _unit
      && {alive _unit}
      && {([_unit] call YSF_fwGetDesignatorSide) isEqualTo side player}
      && {
        !(([_unit] call YSF_fwGetDesignationDescriptorForSource) isEqualTo [])
      }
    ) then {
      _out pushBack _unit;
    };
  } forEach _sources;
  _out
};

YOSHI_taskFW_OnDesignatorChanged = {
  params ["_ctrl", "_idx"];
  if (_idx < 0) exitWith {
    uiNamespace setVariable ["YSF_fw_selected_designator_netId", ""];
  };
  uiNamespace setVariable ["YSF_fw_selected_designator_netId", _ctrl lbData _idx];
};

YOSHI_taskFW_RefreshDesignatorCombo = {
  private _ret = [IDC_TASK_G_FIXEDWING] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {false};

  private _combo = _grp controlsGroupCtrl IDC_TASK_FW_LASER_COMBO;
  if (isNull _combo) exitWith {false};

  private _prevNetId = uiNamespace getVariable ["YSF_fw_selected_designator_netId", ""];
  lbClear _combo;

  private _designators = call YOSHI_taskFW_GetLaserDesignators;
  if ((count _designators) <= 0) exitWith {
    private _idx = _combo lbAdd "No active laser designators";
    _combo lbSetData [_idx, ""];
    _combo lbSetCurSel _idx;
    uiNamespace setVariable ["YSF_fw_selected_designator_netId", ""];
    false
  };

  private _selectedIdx = -1;
  {
    private _unit = _x;
    private _label = "";
    if (_unit isKindOf "Man") then {
      _label = name _unit;
    } else {
      private _dn = [_unit] call YSF_fwSourceDisplayName;
      _label = _dn;
    };

    private _idx = _combo lbAdd _label;
    private _netId = netId _unit;
    _combo lbSetData [_idx, _netId];
    if (_netId isEqualTo _prevNetId) then {
      _selectedIdx = _idx;
    };
  } forEach _designators;

  if (_selectedIdx < 0) then {_selectedIdx = 0;};
  _combo lbSetCurSel _selectedIdx;
  uiNamespace setVariable ["YSF_fw_selected_designator_netId", (_combo lbData _selectedIdx)];
  true
};

YSF_fwFormatStrikeOptionLabel = {
  params ["_weapon", ["_count", 0], ["_displayName", ""]];
  private _dn = _displayName;
  if (_dn isEqualTo "") then {
    _dn = getText (configFile >> "CfgWeapons" >> _weapon >> "displayName");
  };
  if (_dn isEqualTo "") then {_dn = _weapon;};
  format ["%1 (%2)", _dn, _count]
};

YSF_fwGetStrikeOptions = {
  private _reg = call YSF_fwGetPublicRegistry;
  private _hasDeployedStrike = false;
  private _bombCounts = createHashMap;
  private _missileCounts = createHashMap;
  private _bombNames = createHashMap;
  private _missileNames = createHashMap;
  private _bombOrder = [];
  private _missileOrder = [];

  {
    if (_x isEqualType [] && {(count _x) >= 7}) then {
      private _state = _x select 1;
      private _mask = _x select 4;
      private _side = [(_x select 5)] call YSF_fwSideFromId;
      private _veh = [(_x select 6)] call YSF_fwResolveObjectRef;
      if (
        (_state isEqualTo "on_station")
        && ((_mask mod 2) isEqualTo 1)
        && (_side isEqualTo side player)
        && {!isNull _veh}
        && {alive _veh}
      ) then {
        _hasDeployedStrike = true;
        private _lg = _veh call YOSHI_GET_LGO;
        private _bombs = _lg select 0;
        private _missiles = _lg select 1;

        {
          _x params ["_weapon", ["_count", 0], ["_dn", ""]];
          if ((_bombCounts getOrDefault [_weapon, -1]) < 0) then {
            _bombOrder pushBack _weapon;
            _bombCounts set [_weapon, 0];
            _bombNames set [_weapon, _dn];
          };
          _bombCounts set [_weapon, (_bombCounts getOrDefault [_weapon, 0]) + _count];
        } forEach _bombs;

        {
          _x params ["_weapon", ["_count", 0], ["_dn", ""]];
          if ((_missileCounts getOrDefault [_weapon, -1]) < 0) then {
            _missileOrder pushBack _weapon;
            _missileCounts set [_weapon, 0];
            _missileNames set [_weapon, _dn];
          };
          _missileCounts set [_weapon, (_missileCounts getOrDefault [_weapon, 0]) + _count];
        } forEach _missiles;
      };
    };
  } forEach _reg;

  private _bombOut = [];
  {
    private _weapon = _x;
    _bombOut pushBack [
      _weapon,
      _bombCounts getOrDefault [_weapon, 0],
      _bombNames getOrDefault [_weapon, ""]
    ];
  } forEach _bombOrder;

  private _missileOut = [];
  {
    private _weapon = _x;
    _missileOut pushBack [
      _weapon,
      _missileCounts getOrDefault [_weapon, 0],
      _missileNames getOrDefault [_weapon, ""]
    ];
  } forEach _missileOrder;

  [_hasDeployedStrike, _bombOut, _missileOut]
};

YOSHI_taskFW_OnBombWeaponChanged = {
  params ["_ctrl", "_idx"];
  if (_idx < 0) exitWith {
    uiNamespace setVariable ["YSF_fw_selected_bomb_weapon", ""];
  };
  uiNamespace setVariable ["YSF_fw_selected_bomb_weapon", _ctrl lbData _idx];
};

YOSHI_taskFW_OnMissileWeaponChanged = {
  params ["_ctrl", "_idx"];
  if (_idx < 0) exitWith {
    uiNamespace setVariable ["YSF_fw_selected_missile_weapon", ""];
  };
  uiNamespace setVariable ["YSF_fw_selected_missile_weapon", _ctrl lbData _idx];
};

YOSHI_taskFW_RefreshPayloadCombo = {
  params ["_combo", "_options", "_selectedVarName"];
  if (isNull _combo) exitWith {false};

  private _prevWeapon = uiNamespace getVariable [_selectedVarName, ""];
  lbClear _combo;

  if ((count _options) <= 0) exitWith {
    private _idx = _combo lbAdd "None available";
    _combo lbSetData [_idx, ""];
    _combo lbSetCurSel _idx;
    uiNamespace setVariable [_selectedVarName, ""];
    false
  };

  private _selectedIdx = -1;
  {
    _x params ["_weapon", ["_count", 0], ["_dn", ""]];
    private _idx = _combo lbAdd ([_weapon, _count, _dn] call YSF_fwFormatStrikeOptionLabel);
    _combo lbSetData [_idx, _weapon];
    if (_weapon isEqualTo _prevWeapon) then {
      _selectedIdx = _idx;
    };
  } forEach _options;

  if (_selectedIdx < 0) then {_selectedIdx = 0;};
  _combo lbSetCurSel _selectedIdx;
  uiNamespace setVariable [_selectedVarName, _combo lbData _selectedIdx];
  true
};

YOSHI_taskFW_RefreshPayloadCombos = {
  params ["_bombOptions", "_missileOptions"];
  private _ret = [IDC_TASK_G_FIXEDWING] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {[false, false]};

  private _bombCombo = _grp controlsGroupCtrl IDC_TASK_FW_LGB_COMBO;
  private _missileCombo = _grp controlsGroupCtrl IDC_TASK_FW_LGM_COMBO;

  private _hasBombSelection = [_bombCombo, _bombOptions, "YSF_fw_selected_bomb_weapon"] call YOSHI_taskFW_RefreshPayloadCombo;
  private _hasMissileSelection = [_missileCombo, _missileOptions, "YSF_fw_selected_missile_weapon"] call YOSHI_taskFW_RefreshPayloadCombo;

  [_hasBombSelection, _hasMissileSelection]
};

YSF_fwGetSelectedPayloadWeapon = {
  params [["_payloadType", "bomb"]];
  if (_payloadType isEqualTo "missile") exitWith {
    uiNamespace getVariable ["YSF_fw_selected_missile_weapon", ""]
  };
  uiNamespace getVariable ["YSF_fw_selected_bomb_weapon", ""]
};

YOSHI_taskFW_ButtonDebounce = {
  params ["_idc"];
  playSound "UiSubmit";
  [_idc] spawn {
    params ["_idc"];
    private _ret = [IDC_TASK_G_FIXEDWING] call YOSHI_getControl;
    private _grp = _ret # 0;
    private _ok = _ret # 1;
    if (!_ok) exitWith {};

    private _ctrl = _grp controlsGroupCtrl _idc;
    if (isNull _ctrl) exitWith {};

    _ctrl ctrlEnable false;
    hint "Submitting request...";
    uiSleep 3;
    _ctrl ctrlEnable true;
    hintSilent "";
  };
};

YOSHI_taskFW_SyncControlsFromState = {
  private _ret = [IDC_TASK_G_FIXEDWING] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {};

  private _sel = call YOSHI_taskFW_GetSelection;
  private _entry = _sel # 0;
  private _state = _sel # 1;
  private _roleMask = _sel # 2;

  if !(typeName _entry isEqualTo "HASHMAP") exitWith {
    (_grp controlsGroupCtrl IDC_TASK_FW_STATUS) ctrlSetText "No Selection";
    (_grp controlsGroupCtrl IDC_TASK_FW_ROLE) ctrlSetText "-";
    private _deployCtrl = _grp controlsGroupCtrl IDC_TASK_FW_BTN_DEPLOY;
    if (!isNull _deployCtrl) then {
      _deployCtrl ctrlSetTooltip "";
    };
    { [_grp, _x, false] call YOSHI_taskFW_SetEnabled; } forEach [
      IDC_TASK_FW_BTN_DEPLOY,
      IDC_TASK_FW_BTN_RTB,
      IDC_TASK_FW_BTN_LOGI,
      IDC_TASK_FW_LASER_COMBO,
      IDC_TASK_FW_LGB_COMBO,
      IDC_TASK_FW_LGM_COMBO,
      IDC_TASK_FW_BTN_LGB_EXT,
      IDC_TASK_FW_BTN_LGM_EXT
    ];
    {
      [_grp, _x, false] call YOSHI_taskFW_SetVisible;
    } forEach [
      IDC_TASK_FW_STRIKE_INFO,
      IDC_TASK_FW_LASER_LABEL,
      IDC_TASK_FW_LASER_COMBO,
      IDC_TASK_FW_LGB_LABEL,
      IDC_TASK_FW_LGB_COMBO,
      IDC_TASK_FW_LGM_LABEL,
      IDC_TASK_FW_LGM_COMBO,
      IDC_TASK_FW_BTN_LGB_EXT,
      IDC_TASK_FW_BTN_LGM_EXT,
      IDC_TASK_FW_BTN_LOGI
    ];
    [_grp, IDC_TASK_FW_BTN_REFRESH, true] call YOSHI_taskFW_SetEnabled;
  };

  private _vehicleType = _entry getOrDefault ["vehicleType", ""];
  private _deployBlocked = [_vehicleType] call YSF_fwIsDisabledDeployType;
  private _stateTxt = _state;
  if (_stateTxt isEqualType "") then {
    _stateTxt = toUpper _stateTxt;
  };
  if (_state isEqualTo "cooldown") then {
    private _cooldownUntil = _entry getOrDefault ["cooldownUntil", -1];
    if (_cooldownUntil > serverTime) then {
      private _left = round (_cooldownUntil - serverTime);
      _stateTxt = format ["COOLDOWN (%1s)", _left];
    };
  };
  if (_deployBlocked && {(_state isEqualTo "stowed") || (_state isEqualTo "cooldown")}) then {
    _stateTxt = _stateTxt + " | UNAVAILABLE";
  };

  private _isStrike = false;
  private _isRecon = false;
  private _isLogi = false;

  if (((_roleMask mod 2) isEqualTo 1)) then { _isStrike = true; };
  if ((((floor (_roleMask / 2)) mod 2) isEqualTo 1)) then { _isRecon = true; };
  if ((((floor (_roleMask / 4)) mod 2) isEqualTo 1)) then { _isLogi = true; };

  private _roleText = "UNSPECIFIED";
  if (_isStrike) then { _roleText = "STRIKE"; };
  if (_isRecon) then {
    if (_roleText isEqualTo "UNSPECIFIED") then {
      _roleText = "RECON";
    } else {
      _roleText = _roleText + " | RECON";
    };
  };
  if (_isLogi) then {
    if (_roleText isEqualTo "UNSPECIFIED") then {
      _roleText = "LOGI";
    } else {
      _roleText = _roleText + " | LOGI";
    };
  };

  (_grp controlsGroupCtrl IDC_TASK_FW_STATUS) ctrlSetText _stateTxt;
  (_grp controlsGroupCtrl IDC_TASK_FW_ROLE) ctrlSetText _roleText;

  private _canDeploy = (_state isEqualTo "stowed") || (_state isEqualTo "cooldown");
  if (_deployBlocked) then {
    _canDeploy = false;
  };
  private _canRtb = (_state isEqualTo "on_station") || (_state isEqualTo "deploying");
  private _isDeployed = (_state isEqualTo "on_station") || (_state isEqualTo "rtb");
  private _showStrike = ((_state isEqualTo "on_station") && _isStrike);
  private _showLogi = (_isDeployed && _isLogi);
  private _hasTablet = call YSF_fwHasVigilTablet;
  private _hasDesignator = call YOSHI_taskFW_RefreshDesignatorCombo;
  private _strikeOptions = call YSF_fwGetStrikeOptions;
  private _bombOptions = _strikeOptions select 1;
  private _missileOptions = _strikeOptions select 2;
  private _comboState = [_bombOptions, _missileOptions] call YOSHI_taskFW_RefreshPayloadCombos;
  private _hasBomb = _comboState select 0;
  private _hasMissile = _comboState select 1;

  private _deployCtrl = _grp controlsGroupCtrl IDC_TASK_FW_BTN_DEPLOY;
  if (!isNull _deployCtrl) then {
    _deployCtrl ctrlSetTooltip (if (_deployBlocked) then {YSF_FW_UAV_DEPLOY_DISABLED_REASON} else {""});
  };

  [_grp, IDC_TASK_FW_BTN_DEPLOY, _canDeploy] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_BTN_RTB, _canRtb] call YOSHI_taskFW_SetEnabled;
  {
    [_grp, _x, _showStrike] call YOSHI_taskFW_SetVisible;
  } forEach [
    IDC_TASK_FW_STRIKE_INFO,
    IDC_TASK_FW_LASER_LABEL,
    IDC_TASK_FW_LASER_COMBO,
    IDC_TASK_FW_LGB_LABEL,
    IDC_TASK_FW_LGB_COMBO,
    IDC_TASK_FW_LGM_LABEL,
    IDC_TASK_FW_LGM_COMBO,
    IDC_TASK_FW_BTN_LGB_EXT,
    IDC_TASK_FW_BTN_LGM_EXT
  ];
  [_grp, IDC_TASK_FW_BTN_LOGI, _showLogi] call YOSHI_taskFW_SetVisible;
  [_grp, IDC_TASK_FW_BTN_LOGI, _showLogi] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_LASER_COMBO, (_showStrike && _hasTablet)] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_LGB_COMBO, (_showStrike && _hasTablet && _hasDesignator && _hasBomb)] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_LGM_COMBO, (_showStrike && _hasTablet && _hasDesignator && _hasMissile)] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_BTN_LGB_EXT, (_showStrike && _hasTablet && _hasDesignator && _hasBomb)] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_BTN_LGM_EXT, (_showStrike && _hasTablet && _hasDesignator && _hasMissile)] call YOSHI_taskFW_SetEnabled;
  [_grp, IDC_TASK_FW_BTN_REFRESH, true] call YOSHI_taskFW_SetEnabled;
};

YOSHI_taskFW_refresh = {
  ["fixedwing"] call YOSHI_refreshAssetTree;
  call YOSHI_taskFW_SyncControlsFromState;
};

YOSHI_taskFW_deploy = {
  private _id = uiNamespace getVariable ["YSF_current_selected_fw_id", ""];
  if (_id isEqualTo "") exitWith {};

  private _entry = [_id] call YSF_fwGetEntry;
  if (typeName _entry isEqualTo "HASHMAP") then {
    private _vehicleType = _entry getOrDefault ["vehicleType", ""];
    if ([_vehicleType] call YSF_fwIsDisabledDeployType) exitWith {
      hint YSF_FW_UAV_DEPLOY_DISABLED_REASON;
    };
  };

  diag_log format [
    "[YSF][FWDBG] scope=CLIENT owner=%1 deployRequest id=%2 selectedPath=%3 regCount=%4",
    clientOwner,
    _id,
    uiNamespace getVariable ["YSF_fixedwing_path", []],
    count (call YSF_fwGetPublicRegistry)
  ];
  [_id, player] call YSF_fwDeployAsset;
  [_id] spawn {
    params ["_id"];
    uiSleep 0.75;
    diag_log format [
      "[YSF][FWDBG] scope=CLIENT owner=%1 deployRefreshBegin id=%2 currentSelection=%3 regCount=%4",
      clientOwner,
      _id,
      uiNamespace getVariable ["YSF_current_selected_fw_id", ""],
      count (call YSF_fwGetPublicRegistry)
    ];
    call YOSHI_taskFW_refresh;
    diag_log format [
      "[YSF][FWDBG] scope=CLIENT owner=%1 deployRefreshEnd id=%2 currentSelection=%3 regCount=%4",
      clientOwner,
      _id,
      uiNamespace getVariable ["YSF_current_selected_fw_id", ""],
      count (call YSF_fwGetPublicRegistry)
    ];
  };
};

YOSHI_taskFW_rtb = {
  private _id = uiNamespace getVariable ["YSF_current_selected_fw_id", ""];
  if (_id isEqualTo "") exitWith {};

  [_id] call YSF_fwRtbAsset;
  [] spawn {
    uiSleep 0.75;
    call YOSHI_taskFW_refresh;
  };
};

YOSHI_taskFW_findNearestFabricator = {
  if (isNil "YOSHI_FABRICATOR") exitWith {objNull};

  private _logic = YOSHI_FABRICATOR;
  if (isNull _logic) exitWith {objNull};

  private _synced = synchronizedObjects _logic;
  if ((count _synced) < 1) exitWith {objNull};

  private _best = objNull;
  private _bestD = 1e10;
  {
    private _obj = _x;
    if (!isNull _obj) then {
      private _d = player distance2D _obj;
      if (_d < _bestD) then {
        _bestD = _d;
        _best = _obj;
      };
    };
  } forEach _synced;

  _best
};

YOSHI_taskFW_logiStub = {
  if !(isClass (configFile >> "CfgPatches" >> "YFU_FieldUtils")) exitWith {
    hint "Field Utilities is not loaded.";
  };

  if (isNil "YFU_UI_OpenFabricator") exitWith {
    hint "Fabricator UI is unavailable right now.";
  };

  private _sel = call YOSHI_taskFW_GetSelection;
  private _entry = _sel # 0;
  private _airAsset = objNull;
  if (typeName _entry isEqualTo "HASHMAP") then {
    _airAsset = _entry getOrDefault ["spawnedVeh", objNull];
  };

  if (isNull _airAsset) exitWith {
    hint "Selected LOGI aircraft is not available.";
  };

  [_airAsset, true, mapGridPosition player] call YFU_UI_OpenFabricator;
};

YOSHI_taskFW_requestStrikeFromDesignator = {
  params [["_payloadType", "bomb"]];

  if (!(call YSF_fwHasVigilTablet)) exitWith {
    hint "You need a VIGIL Support Tablet in your GPS slot to request strike actions.";
  };

  private _designatorNetId = uiNamespace getVariable ["YSF_fw_selected_designator_netId", ""];
  if (_designatorNetId isEqualTo "") exitWith {
    hint "No active laser designator selected.";
  };

  private _designator = objectFromNetId _designatorNetId;
  if (isNull _designator || {!alive _designator}) exitWith {
    hint "Selected designator is no longer available.";
  };

  private _designatorSide = [_designator] call YSF_fwGetDesignatorSide;
  if (_designatorSide != side player) exitWith {
    hint "Selected designator is not on your side.";
  };

  private _btnIdc = if (_payloadType isEqualTo "missile") then {
    IDC_TASK_FW_BTN_LGM_EXT
  } else {
    IDC_TASK_FW_BTN_LGB_EXT
  };
  [_btnIdc] call YOSHI_taskFW_ButtonDebounce;

  private _preferredWeapon = [_payloadType] call YSF_fwGetSelectedPayloadWeapon;
  [_payloadType, _designator, _preferredWeapon] call YSF_fwRequestStrikeFromDesignator;
};

YSF_fwLaserClassBySide = {
  params ["_side"];
  switch (_side) do {
    case west: {"LaserTargetW"};
    case east: {"LaserTargetE"};
    case resistance: {"LaserTargetC"};
    default {"LaserTargetC"};
  };
};

YSF_fwNormalizeWeaponClass = {
  params ["_value"];
  if (_value isEqualType "") exitWith {_value};
  if !(_value isEqualType []) exitWith {""};
  if ((count _value) <= 0) exitWith {""};

  private _first = _value # 0;
  if (_first isEqualType "") exitWith {_first};
  if (_first isEqualType [] && {(count _first) > 0}) then {
    private _inner = _first # 0;
    if (_inner isEqualType "") exitWith {_inner};
  };
  ""
};

YSF_fwFindStrikeAircraft = {
  params [
    ["_payloadType", "bomb"],
    ["_preferredWeapon", ""]
  ];
  private _reg = call YSF_fwGetPublicRegistry;
  private _bestVeh = objNull;
  private _bestWeapon = "";
  private _bestDist = 1e9;
  private _hasDeployedStrike = false;
  private _hasAnyBomb = false;
  private _hasAnyMissile = false;
  private _hasPreferred = false;

  {
    if (_x isEqualType [] && {(count _x) >= 7}) then {
      private _state = _x select 1;
      private _mask = _x select 4;
      private _side = [(_x select 5)] call YSF_fwSideFromId;
      private _veh = [(_x select 6)] call YSF_fwResolveObjectRef;
      if (
        (_state isEqualTo "on_station")
        && ((_mask mod 2) isEqualTo 1)
        && (_side isEqualTo side player)
        && {!isNull _veh}
        && {alive _veh}
      ) then {
        _hasDeployedStrike = true;
        private _lg = _veh call YOSHI_GET_LGO;
        private _bombs = _lg select 0;
        private _missiles = _lg select 1;
        if ((count _bombs) > 0) then { _hasAnyBomb = true; };
        if ((count _missiles) > 0) then { _hasAnyMissile = true; };

        private _pool = if (_payloadType isEqualTo "missile") then {_missiles} else {_bombs};
        private _candidateWeapon = "";

        if (_preferredWeapon isNotEqualTo "") then {
          private _prefIdx = _pool findIf {([_x] call YSF_fwNormalizeWeaponClass) isEqualTo _preferredWeapon};
          if (_prefIdx >= 0) then {
            _candidateWeapon = [(_pool select _prefIdx)] call YSF_fwNormalizeWeaponClass;
            _hasPreferred = true;
          };
        };

        if (_candidateWeapon isEqualTo "" && {(count _pool) > 0}) then {
          _candidateWeapon = [(_pool select 0)] call YSF_fwNormalizeWeaponClass;
        };

        if (_candidateWeapon isNotEqualTo "") then {
          private _d = _veh distance2D player;
          if (_d < _bestDist) then {
            _bestDist = _d;
            _bestVeh = _veh;
            _bestWeapon = _candidateWeapon;
          };
        };
      };
    };
  } forEach _reg;

  [_bestVeh, _bestWeapon, _hasDeployedStrike, _hasAnyBomb, _hasAnyMissile, _hasPreferred]
};

YSF_fwGetDesignationDescriptor = {
  [player] call YSF_fwGetDesignationDescriptorForUnit
};

YSF_fwGetEffectiveLaserTargetForUnit = {
  params ["_unit"];
  if (isNull _unit || {!alive _unit}) exitWith {objNull};

  private _laser = laserTarget _unit;
  if ((_laser isEqualType objNull) && {!isNull _laser}) exitWith {_laser};

  private _fake = _unit getVariable ["YSF_irFakeLaserTarget", objNull];
  if ((_fake isEqualType objNull) && {!isNull _fake}) exitWith {_fake};

  objNull
};

YSF_fwGetDesignationDescriptorForUnit = {
  params ["_unit"];
  if (isNull _unit || {!alive _unit}) exitWith {[]};

  private _laser = [_unit] call YSF_fwGetEffectiveLaserTargetForUnit;
  if (!isNull _laser) exitWith {
    ["laser", _laser]
  };

  []
};

YSF_fwGetDesignationDescriptorForSource = {
  params ["_source"];
  if (isNull _source || {!alive _source}) exitWith {[]};

  if (_source isKindOf "Man") exitWith {
    [_source] call YSF_fwGetDesignationDescriptorForUnit
  };

  private _laser = [_source] call YSF_fwGetEffectiveLaserTargetForUnit;
  if (!isNull _laser) exitWith {
    ["laser", _laser]
  };

  private _uavControl = UAVControl _source;
  if ((count _uavControl) > 0) then {
    private _controller = _uavControl select 0;
    if (!isNull _controller) then {
      private _d = [_controller] call YSF_fwGetDesignationDescriptorForUnit;
      if !(_d isEqualTo []) exitWith {_d};
    };
  };

  {
    private _d = [_x] call YSF_fwGetDesignationDescriptorForUnit;
    if !(_d isEqualTo []) exitWith {_d};
  } forEach crew _source;

  []
};

YSF_fwCanUseStrikeKeybind = {
  params [["_notify", true], ["_allowDialog", false]];
  if (!alive player) exitWith {false};

  true
};

YSF_fwHasStrikeDesignation = {
  !(call YSF_fwGetDesignationDescriptor isEqualTo [])
};

YSF_fwGetStrikeAvailability = {
  private _opts = call YSF_fwGetStrikeOptions;
  [
    _opts select 0,
    (count (_opts select 1)) > 0,
    (count (_opts select 2)) > 0
  ]
};

YSF_fwHasVigilTablet = {
  private _slottedItems = assignedItems player;
  ("YSF_VigilTerminal_B" in _slottedItems)
  || ("YSF_VigilTerminal_I" in _slottedItems)
  || ("YSF_VigilTerminal_O" in _slottedItems)
};

YSF_fwActionRemove = {
  params ["_varName"];
  private _id = uiNamespace getVariable [_varName, -1];
  if (_id >= 0) then {
    player removeAction _id;
    uiNamespace setVariable [_varName, -1];
  };
};

YSF_fwActionClearMenu = {
  params [["_includeRoot", true]];
  if !(_includeRoot isEqualType true) then {
    _includeRoot = true;
  };
  {
    [_x] call YSF_fwActionRemove;
  } forEach [
    "YSF_fwAction_direct_bomb",
    "YSF_fwAction_direct_missile",
    // Legacy staged menu IDs (kept for cleanup compatibility).
    "YSF_fwAction_profile_surgical",
    "YSF_fwAction_profile_laser",
    "YSF_fwAction_profile_package",
    "YSF_fwAction_payload_bomb",
    "YSF_fwAction_payload_missile",
    "YSF_fwAction_back",
    "YSF_fwAction_cancel"
  ];
  if (_includeRoot) then {
    ["YSF_fwAction_root"] call YSF_fwActionRemove;
  };
};

YSF_fwActionSetStage = {
  params ["_stage", ["_profile", ""]];
  uiNamespace setVariable ["YSF_fwAction_stage", _stage];
  uiNamespace setVariable ["YSF_fwAction_profile", _profile];
  private _expiry = if (_stage > 0) then {time + 10} else {-1};
  uiNamespace setVariable ["YSF_fwAction_expireAt", _expiry];
};

YSF_fwActionShowPayloadMenu = {
  params [["_profile", "surgical"]];
  [2, _profile] call YSF_fwActionSetStage;
  [false] call YSF_fwActionClearMenu;

  private _availability = call YSF_fwGetStrikeAvailability;
  private _hasDeployedStrike = _availability select 0;
  private _hasBomb = _availability select 1;
  private _hasMissile = _availability select 2;

  if (!_hasDeployedStrike) exitWith {
    [0, ""] call YSF_fwActionSetStage;
    hint "No deployed strike aircraft in AO.";
  };

  if (_hasBomb) then {
    private _idBomb = player addAction [
      "VIGIL Strike: LGB Release",
      {["bomb"] call YSF_fwRequestStrike;},
      nil,
      2,
      false,
      true
    ];
    uiNamespace setVariable ["YSF_fwAction_payload_bomb", _idBomb];
  };

  if (_hasMissile) then {
    private _idMissile = player addAction [
      "VIGIL Strike: LGM Release",
      {["missile"] call YSF_fwRequestStrike;},
      nil,
      2,
      false,
      true
    ];
    uiNamespace setVariable ["YSF_fwAction_payload_missile", _idMissile];
  };

  private _idBack = player addAction [
    "VIGIL Strike: Back",
    {call YSF_fwActionShowProfileMenu;},
    nil,
    1.8,
    false,
    true
  ];
  uiNamespace setVariable ["YSF_fwAction_back", _idBack];

  private _idCancel = player addAction [
    "VIGIL Strike: Cancel",
    {
      [0, ""] call YSF_fwActionSetStage;
      [false] call YSF_fwActionClearMenu;
      hintSilent "";
    },
    nil,
    1.7,
    false,
    true
  ];
  uiNamespace setVariable ["YSF_fwAction_cancel", _idCancel];
};

YSF_fwActionShowProfileMenu = {
  [1, ""] call YSF_fwActionSetStage;
  [false] call YSF_fwActionClearMenu;

  private _idPackage = player addAction [
    "VIGIL Strike: Strike Packages",
    {["package"] call YSF_fwActionShowPayloadMenu;},
    nil,
    2,
    false,
    true
  ];
  uiNamespace setVariable ["YSF_fwAction_profile_package", _idPackage];

  private _idCancel = player addAction [
    "VIGIL Strike: Cancel",
    {
      [0, ""] call YSF_fwActionSetStage;
      [false] call YSF_fwActionClearMenu;
      hintSilent "";
    },
    nil,
    1.7,
    false,
    true
  ];
  uiNamespace setVariable ["YSF_fwAction_cancel", _idCancel];
};

YSF_fwRootActionCondition = {
  private _stage = uiNamespace getVariable ["YSF_fwAction_stage", 0];
  if (_stage != 0) exitWith {false};

  private _availability = call YSF_fwGetStrikeAvailability;
  private _hasDeployedStrike = _availability select 0;
  if (!(_hasDeployedStrike)) exitWith {false};

  if (!(call YSF_fwHasStrikeDesignation)) exitWith {false};

  if (!([false] call YSF_fwCanUseStrikeKeybind)) exitWith {false};

  true
};

YSF_fwDirectActionCondition = {
  params [["_payloadType", "bomb"]];
  if (!(call YSF_fwHasVigilTablet)) exitWith {false};

  private _availability = call YSF_fwGetStrikeAvailability;
  private _hasDeployedStrike = _availability select 0;
  private _hasBomb = _availability select 1;
  private _hasMissile = _availability select 2;

  if (!(_hasDeployedStrike)) exitWith {false};
  if (_payloadType isEqualTo "bomb" && {!_hasBomb}) exitWith {false};
  if (_payloadType isEqualTo "missile" && {!_hasMissile}) exitWith {false};
  if (!(call YSF_fwHasStrikeDesignation)) exitWith {false};
  if (!([false] call YSF_fwCanUseStrikeKeybind)) exitWith {false};

  true
};

YSF_fwActionTick = {
  if (!hasInterface) exitWith {};
  if (isNull player) exitWith {};

  private _bombId = uiNamespace getVariable ["YSF_fwAction_direct_bomb", -1];
  if (_bombId < 0) then {
    private _newBombId = player addAction [
      "VIGIL Strike: LGB Release",
      {["bomb"] call YSF_fwRequestStrike;},
      nil,
      2,
      false,
      true,
      "",
      "['bomb'] call YSF_fwDirectActionCondition"
    ];
    uiNamespace setVariable ["YSF_fwAction_direct_bomb", _newBombId];
  };

  private _missileId = uiNamespace getVariable ["YSF_fwAction_direct_missile", -1];
  if (_missileId < 0) then {
    private _newMissileId = player addAction [
      "VIGIL Strike: LGM Release",
      {["missile"] call YSF_fwRequestStrike;},
      nil,
      2,
      false,
      true,
      "",
      "['missile'] call YSF_fwDirectActionCondition"
    ];
    uiNamespace setVariable ["YSF_fwAction_direct_missile", _newMissileId];
  };
};

YSF_fwActionInit = {
  if (!hasInterface) exitWith {};
  if (isNull player) exitWith {};

  uiNamespace setVariable ["YSF_fwAction_stage", 0];
  uiNamespace setVariable ["YSF_fwAction_profile", ""];
  uiNamespace setVariable ["YSF_fwAction_expireAt", -1];
  [false] call YSF_fwActionClearMenu;

  private _existingRoot = uiNamespace getVariable ["YSF_fwAction_root", -1];
  if (_existingRoot >= 0) then {
    player removeAction _existingRoot;
    uiNamespace setVariable ["YSF_fwAction_root", -1];
  };
  ["YSF_fwAction_direct_bomb"] call YSF_fwActionRemove;
  ["YSF_fwAction_direct_missile"] call YSF_fwActionRemove;

  private _bombId = player addAction [
    "VIGIL Strike: LGB Release",
    {["bomb"] call YSF_fwRequestStrike;},
    nil,
    2,
    false,
    true,
    "",
    "['bomb'] call YSF_fwDirectActionCondition"
  ];
  uiNamespace setVariable ["YSF_fwAction_direct_bomb", _bombId];

  private _missileId = player addAction [
    "VIGIL Strike: LGM Release",
    {["missile"] call YSF_fwRequestStrike;},
    nil,
    2,
    false,
    true,
    "",
    "['missile'] call YSF_fwDirectActionCondition"
  ];
  uiNamespace setVariable ["YSF_fwAction_direct_missile", _missileId];

  if (!(uiNamespace getVariable ["YSF_fwAction_initialized", false])) then {
    uiNamespace setVariable ["YSF_fwAction_initialized", true];
    [{
      call YSF_fwActionTick;
    }, 0.25, []] call CBA_fnc_addPerFrameHandler;
  };
};

YSF_fwClientInit = {
  if (!hasInterface) exitWith {};
  if (uiNamespace getVariable ["YSF_fwClientInitDone", false]) exitWith {};

  [] spawn {
    waitUntil {hasInterface && {!isNull player}};
    if (uiNamespace getVariable ["YSF_fwClientInitDone", false]) exitWith {};
    uiNamespace setVariable ["YSF_fwClientInitDone", true];

    [] call YSF_fwActionInit;

    player addEventHandler ["Respawn", {
      [] call YSF_fwActionInit;
    }];

    if (!(uiNamespace getVariable ["YSF_fwUiTickInitialized", false])) then {
      uiNamespace setVariable ["YSF_fwUiTickInitialized", true];
      [{
        call YOSHI_taskFW_LiveUiTick;
      }, 1.5, []] call CBA_fnc_addPerFrameHandler;
    };
  };
};

YOSHI_GET_BOMB_FALL_TIME = {
    params ["_initialHeight", "_finalHeight"];

    private _g = 9.81;

    private _distance = _initialHeight - _finalHeight;
    private _time = sqrt((2 * _distance) / _g);

    (round (_time * 100))/100
};

YSF_fwDbg = {
  params ["_msg"];
  if !(isNil "YSF_fnc_debugMsg") exitWith {
    _msg call YSF_fnc_debugMsg;
  };
  if !(isNil "YCD_fnc_debugMsg") exitWith {
    [_msg, "YSF", "YSF_showDebugMessages"] call YCD_fnc_debugMsg;
  };
  diag_log format ["[YSF][DBG] %1", _msg];
};

YSF_fwEmitSideChat = {
  params ["_speaker", "_message", ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
  if !(isNil "YSF_fnc_emitSideChat") exitWith {
    [_speaker, _message, _targets, _onceKey, _ttl] call YSF_fnc_emitSideChat;
  };
  if !(isNil "YCD_fnc_emitSideChat") exitWith {
    [_speaker, _message, _targets, _onceKey, _ttl, "YSF_playSideMessages"] call YCD_fnc_emitSideChat;
  };
  if (!isNull _speaker) then {
    _speaker sideChat _message;
  } else {
    systemChat _message;
  };
};

YSF_fwDbgName = {
  params ["_obj"];
  if (isNull _obj) exitWith {"<null>"};
  if (_obj isKindOf "Man") exitWith {name _obj};

  private _dn = getText (configFile >> "CfgVehicles" >> typeOf _obj >> "displayName");
  if (_dn isEqualTo "") then {_dn = typeOf _obj;};
  _dn
};

YSF_fwExecuteStrikeLocal = {
  params ["_veh", "_weapon", "_targetObj", ["_requester", objNull], ["_payloadType", "bomb"]];
  if (isNull _veh || {!alive _veh}) exitWith {};
  private _weaponClass = [_weapon] call YSF_fwNormalizeWeaponClass;
  if (_weaponClass isEqualTo "") exitWith {
    [format ["FW execute abort: invalid weapon input=%1", _weapon]] call YSF_fwDbg;
  };
  if (isNull _targetObj) exitWith {};
  if !(local _veh) exitWith {};


  _veh reveal [_targetObj, 4];
  _veh doWatch _targetObj;
  _veh doTarget _targetObj;
  _veh commandTarget _targetObj;
  if (canSuspend) then {uiSleep 1;};

  private _fired = _veh fireAtTarget [_targetObj, _weaponClass];
  [
    format [
      "FW execute: veh=%1 weapon=%2 target=%3 payload=%4 requester=%5 t=%6 | local=%7 owner=%8 fired=%9",
      [_veh] call YSF_fwDbgName,
      _weaponClass,
      [_targetObj] call YSF_fwDbgName,
      _payloadType,
      [_requester] call YSF_fwDbgName,
      serverTime,
      local _veh,
      owner _veh,
      _fired
    ]
  ] call YSF_fwDbg;
  [_veh, _weaponClass, _targetObj, _fired, _payloadType] call YSF_handleFired;
};

YSF_handleFired = {
  params ["_veh", "_weapon", "_targetObj", "_fired", ["_payloadType", "bomb"]];
  if (_fired) then {
    private _eta = -1;
    private _dist = _veh distance2D _targetObj;
    private _height = (getPosASL _veh) select 2;
    private _targetHeight = (getPosASL _targetObj) select 2;
    if (_payloadType isEqualTo "missile") then {
      _eta = (_dist / 300) max 2;
    } else {
      _eta = [_height, _targetHeight] call YOSHI_GET_BOMB_FALL_TIME;
    };

    [_veh, format ["Payload away, impact ETA %1 seconds. | %2", round _eta, _weapon]] call YSF_fwEmitSideChat;

  } else {
    [_veh, "Weapon failed to fire."] call YSF_fwEmitSideChat;
  };

};

YSF_fwSourceDisplayName = {
  params ["_source"];
  if (isNull _source) exitWith {"Unknown"};
  if (_source isKindOf "Man") exitWith {name _source};

  private _dn = getText (configFile >> "CfgVehicles" >> typeOf _source >> "displayName");
  if (_dn isEqualTo "") then {_dn = typeOf _source;};
  private _cmd = effectiveCommander _source;
  if (!isNull _cmd) exitWith {format ["(%2) %1", _dn, group _source]};
  _dn
};

YSF_fwPrimaryHintTargetForSource = {
  params ["_source"];
  if (isNull _source) exitWith {player};
  if (_source isKindOf "Man") exitWith {_source};
  private _cmd = effectiveCommander _source;
  if (!isNull _cmd) exitWith {_cmd};
  player
};

YSF_fwGuardRequest = {
  params ["_source", "_allowDialog"];
  if (!(call YSF_fwHasVigilTablet)) exitWith {
    hint "You need a VIGIL Support Tablet in your GPS slot to request strike actions.";
    false
  };
  if (!([true, _allowDialog] call YSF_fwCanUseStrikeKeybind)) exitWith {false};
  if (isNull _source || {!alive _source}) exitWith {
    hint "Designator source is unavailable.";
    false
  };
  if (missionNamespace getVariable ["YSF_fw_strikeBusy", false]) exitWith {
    hint "Strike request already in progress.";
    false
  };
  true
};

YSF_fwSelectStrikePair = {
  params ["_payloadType", ["_preferredWeapon", ""]];
  private _pair = [_payloadType, _preferredWeapon] call YSF_fwFindStrikeAircraft;
  private _veh = _pair select 0;
  private _weapon = _pair select 1;
  private _hasDeployedStrike = _pair select 2;
  private _hasAnyBomb = _pair select 3;
  private _hasAnyMissile = _pair select 4;
  private _hasPreferred = _pair select 5;

  if (!isNull _veh && {!(_weapon isEqualTo "")}) exitWith {
    if (_preferredWeapon isNotEqualTo "" && {!_hasPreferred}) then {
      hint "Selected weapon type unavailable right now. Using default available type.";
    };
    [_veh, _weapon]
  };

  if (!_hasDeployedStrike) then {
    hint "No deployed strike aircraft in AO.";
  } else {
    if (_payloadType isEqualTo "bomb") then {
      if (_hasAnyMissile) then {
        hint "Strike aircraft have no LGB bombs loaded. Select missile.";
      } else {
        hint "Deployed strike aircraft have no laser-guided bombs or missiles loaded.";
      };
    } else {
      if (_hasAnyBomb) then {
        hint "Strike aircraft have no LGM missiles loaded. Select bomb.";
      } else {
        hint "Deployed strike aircraft have no laser-guided bombs or missiles loaded.";
      };
    };
  };
  [objNull, ""]
};

YSF_fwValidateSourceSide = {
  params ["_source", "_veh"];
  private _designatorSide = [_source] call YSF_fwGetDesignatorSide;
  private _assetSide = side _veh;
  if (
    (_designatorSide != sideUnknown)
    && (_assetSide != sideUnknown)
    && (_designatorSide != _assetSide)
  ) exitWith {
    hint "Selected designator is not on the strike aircraft side.";
    false
  };
  true
};

YSF_fwResolveLaserFromDescriptor = {
  params ["_descriptor", "_assetSide"];
  if ((typeName _descriptor != "ARRAY") || {(count _descriptor) < 2}) exitWith {[objNull, false]};

  private _kind = _descriptor select 0;
  private _value = _descriptor select 1;
  private _laserType = if (_kind isEqualTo "laser") then {"designator"} else {"ir"};
  [format ["3. kind=%1 laserType=%2", _kind, _laserType]] call YSF_fwDbg;

  if (_kind isEqualTo "laser") exitWith {
    if (!(_value isEqualType objNull)) exitWith {[objNull, false]};
    if (isNull _value) then {[objNull, false]} else {[_value, false]}
  };

  private _cls = [_assetSide] call YSF_fwLaserClassBySide;
  if (_kind isEqualTo "object") exitWith {
    private _obj = objectFromNetId _value;
    if (isNull _obj) exitWith {[objNull, false]};
    private _laser = createVehicle [_cls, getPosASL _obj, [], 0, "CAN_COLLIDE"];
    _laser attachTo [_obj, [0,0,0]];
    [_laser, true]
  };

  if (_kind isEqualTo "position") exitWith {
    private _laser = createVehicle [_cls, ASLToAGL _value, [], 0, "CAN_COLLIDE"];
    _laser setPosASL _value;
    [_laser, true]
  };

  [objNull, false]
};

YSF_fwResolveLaserForSource = {
  params ["_source"];
  [_source] call YSF_fwGetDesignationDescriptorForSource
};

YSF_fwCleanupTempLaser = {
  params ["_laser"];
  if !(_laser isEqualType objNull) exitWith {};
  if (isNull _laser) exitWith {};
  [_laser] spawn {
    params ["_t"];
    sleep 100;
    if (!isNull _t) then {deleteVehicle _t;};
  };
};

YSF_fwRunStrikeCountdown = {
  params ["_source", "_payloadType", "_sourceName", "_hintTarget"];
  private _descriptor = [];

  for "_i" from 3 to 1 step -1 do {
    private _liveDescriptor = [_source] call YSF_fwResolveLaserForSource;
    if (_liveDescriptor isEqualTo []) exitWith {[]};
    _descriptor = _liveDescriptor;

    [format ["%1 release in %2... (%3)", toUpper _payloadType, _i, _sourceName]] remoteExecCall ["hint", _hintTarget];
    uiSleep 1;
  };

  _descriptor
};

YSF_fwAbortStrikeRequest = {
  params ["_veh", "_hintTarget", "_tempLaser"];
  missionNamespace setVariable ["YSF_fw_strikeBusy", false];
  ["Laser/designation lost before release. Strike aborted."] remoteExecCall ["hint", _hintTarget];
  [_veh, "Designation lost, strike aborted."] call YSF_fwEmitSideChat;
  if (!isNull _tempLaser) then {deleteVehicle _tempLaser;};
};

YSF_fwFinalizeStrikeRequest = {
  params ["_veh", "_weapon", "_laserTarget", "_payloadType", "_hintTarget", "_clearActionMenu", "_tempLaser"];
  [""] remoteExecCall ["hintSilent", _hintTarget];
  [
    "YSF_fwExecuteStrikeLocal",
    _veh,
    [_veh, _weapon, _laserTarget, player, _payloadType],
    format ["YSF_FW_EXECUTE_%1_%2_%3", netId _veh, _weapon, netId _laserTarget],
    5
  ] call YCD_fnc_runOnObjectOwnerOnce;
  missionNamespace setVariable ["YSF_fw_strikeBusy", false];
  if (_clearActionMenu) then {
    [0, ""] call YSF_fwActionSetStage;
    [false] call YSF_fwActionClearMenu;
  };
  [_tempLaser] call YSF_fwCleanupTempLaser;
};

YSF_fwRequestStrikeCore = {
  params [
    ["_payloadType", "bomb"],
    ["_source", objNull],
    ["_allowDialog", false],
    ["_clearActionMenu", false],
    ["_isDirect", true],
    ["_preferredWeapon", ""]
  ];
  private _callerName = [player] call YSF_fwDbgName;
  private _sourceName = [_source] call YSF_fwSourceDisplayName;
  private _hintTarget = [_source] call YSF_fwPrimaryHintTargetForSource;
  [
    format [
      "1. direct=%1 caller=%2 laserOwner=%3 payload=%4 t=%5",
      _isDirect,
      _callerName,
      _sourceName,
      _payloadType,
      serverTime
    ]
  ] call YSF_fwDbg;

  if !([_source, _allowDialog] call YSF_fwGuardRequest) exitWith {};
  private _pair = [_payloadType, _preferredWeapon] call YSF_fwSelectStrikePair;
  private _veh = _pair select 0;
  private _weapon = _pair select 1;
  if (isNull _veh || {_weapon isEqualTo ""}) exitWith {};
  if !([_source, _veh] call YSF_fwValidateSourceSide) exitWith {};

  private _assetSide = side _veh;
  missionNamespace setVariable ["YSF_fw_strikeBusy", true];
  private _designationType = if ((toLower _payloadType) isEqualTo "bomb") then {"LGB"} else {"LGM"};
  [
    _veh,
    format ["%1 selected, using %2 designation.", _designationType, _sourceName],
    0,
    format ["YSF_FW_DESIGNATION_%1_%2_%3", netId _veh, netId _source, _designationType],
    5
  ] call YSF_fwEmitSideChat;

  private _descriptor = [_source, _payloadType, _sourceName, _hintTarget] call YSF_fwRunStrikeCountdown;
  if (_descriptor isEqualTo []) exitWith {
    [_veh, _hintTarget, objNull] call YSF_fwAbortStrikeRequest;
  };

  private _resolved = [_descriptor, _assetSide] call YSF_fwResolveLaserFromDescriptor;
  _resolved params ["_laserTarget", "_isTempLaser"];
  private _tempLaser = objNull;
  if (_isTempLaser isEqualType true && {_isTempLaser}) then {
    _tempLaser = _laserTarget;
  };
  if (isNull _laserTarget) exitWith {
    [_veh, _hintTarget, _tempLaser] call YSF_fwAbortStrikeRequest;
  };

  [_veh, _weapon, _laserTarget, _payloadType, _hintTarget, _clearActionMenu, _tempLaser] call YSF_fwFinalizeStrikeRequest;
};

YSF_fwRequestStrike = {
  params [["_payloadType", "bomb"], ["_preferredWeapon", ""]];
  [_payloadType, player, false, true, true, _preferredWeapon] spawn YSF_fwRequestStrikeCore;
};

YSF_fwRequestStrikeFromDesignator = {
  params [["_payloadType", "bomb"], ["_designator", objNull], ["_preferredWeapon", ""]];
  [_payloadType, _designator, true, false, false, _preferredWeapon] spawn YSF_fwRequestStrikeCore;
};

YOSHI_taskFW_LiveUiTick = {
  if (!hasInterface) exitWith {};
  if (isNull player) exitWith {};

  private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
  if (isNull _display) exitWith {};

  if !((uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "fixedwing") exitWith {};
  private _selId = uiNamespace getVariable ["YSF_current_selected_fw_id", ""];
  private _entry = [_selId] call YSF_fwGetEntry;
  private _state = if (typeName _entry isEqualTo "HASHMAP") then {
    _entry getOrDefault ["state", ""]
  } else {
    ""
  };
  private _sig = format ["%1|%2", _selId, _state];
  private _prevSig = uiNamespace getVariable ["YSF_fw_lastLiveTickSig", ""];
  if !(_sig isEqualTo _prevSig) then {
    uiNamespace setVariable ["YSF_fw_lastLiveTickSig", _sig];
    diag_log format [
      "[YSF][FWDBG] scope=CLIENT owner=%1 liveTick selection=%2 state=%3 regCount=%4",
      clientOwner,
      _selId,
      _state,
      count (call YSF_fwGetPublicRegistry)
    ];
  };
  call YOSHI_taskFW_SyncControlsFromState;
};
