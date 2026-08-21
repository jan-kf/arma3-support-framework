#include "..\..\ui\idc.hpp"

YSF_VERSION = "v0.8.0";

YOSHI_getAllVehicles = {
  private _whitelistConfigured = missionNamespace getVariable ["YSF_WHITELIST_CONFIGURED", false];
  if (_whitelistConfigured) then {
    private _vehicles = +(missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []]);
    format ["Whitelisted assets loaded: %1", _vehicles] call YSF_fnc_debugMsg;
    _vehicles
  } else {
    "All vehicles available for tasking." call YSF_fnc_debugMsg;
    vehicles
  }
};

YOSHI_initAssetList = {
  private _type = uiNamespace getVariable ["YSF_asset_type", "transport"];
  [_type] call YOSHI_selectAssetType;
  "Assets page initialized" call YSF_fnc_debugMsg;
};

YOSHI_playIntro = {
  private _introPlayed = uiNamespace getVariable [format["YSF_init_played_for_%1", netId player], false];
  private _year = date select 0;
  private _lines = [
      format["VIGIL BIOS %1 (C) %2-%3", YSF_VERSION, _year-13, _year+1],
      "CPU: 80386DX @ 33MHz",
      "Memory Test: ##################################### 640KB OK",
      "Detecting IDE devices...",
      "Primary Master: ST-251 42MB",
      "Primary Slave: None",
      "Booting from HDD...",
      "Loading VIGIL-OS...",
      "Initializing devices...",
      "Mounting volumes...",
      "Starting services...",
      "Connecting to intranet...",
      "System ready."
    ];

  if (_introPlayed) then {
    [IDC_TABLET_INTRO, IDC_PAGE_ASSETS, _lines, 0.5, 0.00016, 0.06, 0.1, 0.125] call YSF_fnc_introIntoCtrl;
  } else {
    [IDC_TABLET_INTRO, IDC_PAGE_ASSETS, _lines] call YSF_fnc_introIntoCtrl;
  };
  call YOSHI_checkUplinkStatus;
};


YOSHI_setVehInfoText = {
  params ["_v"];
  private _grid = mapGridPosition _v;
  private _spd = round speed _v;
  private _hdg = round (getDir _v);
  private _fuel = ((fuel _v));
  private _hitPointCount = (((1 - damage _v)*100 max 0)/100);
  private _cap = getNumber (configFile >> "CfgVehicles" >> typeOf _v >> "transportSoldier");
  private _cargoA = count (fullCrew [_v,"cargo",true]);
  private _cargoFree = _v emptyPositions "cargo";
  private _grp = group effectiveCommander _v;
  private _wp = "HOLDING";
  if (!isNull _grp) then {
    private _cw = currentWaypoint _grp;
    private _cnt = count (waypoints _grp);
    if (_cnt > 0 && _cw > 0 && _cw <= _cnt) then {
      private _wt = waypointType [_grp,_cw];
      if (_wt isEqualTo "") then {_wt = "MOVE"};
      _wp = format ["%1 #%2",_wt,_cw];
    };
  };
  private _crew = fullCrew [_v,"",true];
  private _players = _crew select {isPlayer (_x#0)};
  private _pTxt = if (_players isEqualTo []) then {"None"} else {(_players apply {format ["%1 (%2)",name (_x#0),toUpper (_x#1)]}) joinString ", "};
  private _maf = magazinesAmmoFull _v;
  private _m = createHashMap;
  {
    private _mag = _x#0; private _ammo = _x#1;
    if (!isNil "_mag" && {!(_mag isEqualTo "")}) then {
      private _acc = _m getOrDefault [_mag,[0,0]];
      _m set [_mag,[_acc#0+1,_acc#1+_ammo]];
    };
  } forEach _maf;
  private _lines = [];
  { private _dn = getText (configFile >> "CfgMagazines" >> _x >> "displayName"); if (_dn isEqualTo "") then {_dn = _x};
    private _v2 = _m get _x; _lines pushBack format ["%1 x%2 (%3)",_dn,_v2#0,_v2#1];
  } forEach (keys _m);
  private _mTxt = if (_lines isEqualTo []) then {"None"} else {_lines joinString "<br/>"};
  private _side = side (group effectiveCommander _v);
  private _typ = getText (configFile >> "CfgVehicles" >> typeOf _v >> "displayName");

  [IDC_ASSETS_DETAIL_NAME, _typ] call YOSHI_setText;
  [IDC_ASSETS_DETAIL_GRID, _grid] call YOSHI_setText;
  [IDC_ASSETS_DETAIL_SPEED, format ["%1 m/s", str _spd]] call YOSHI_setText;
  [IDC_ASSETS_DETAIL_HEADING, format ["%1°", str _hdg]] call YOSHI_setText;
  [IDC_ASSETS_DETAIL_FUEL, _fuel] call YOSHI_setBar;
  [IDC_ASSETS_DETAIL_HEALTH, _hitPointCount] call YOSHI_setBar;
  [IDC_ASSETS_DETAIL_CARGO, format ["%1 Positions Free", _cargoFree]] call YOSHI_setText;
  [IDC_ASSETS_DETAIL_PLAYERS, _pTxt] call YOSHI_setText;
  // [IDC_ASSETS_DETAIL_WP, _wp] call YOSHI_setText;
  // [IDC_ASSETS_DETAIL_LOADOUT, format ["<t size='0.9'>%1</t>", _mTxt]] call YOSHI_setText;
  [_m] call YOSHI_setOrdinanceOptions;
};

YOSHI_fwRoleText = {
  params ["_mask"];
  private _parts = [];
  if (((_mask mod 2) isEqualTo 1)) then {_parts pushBack "Strike";};
  if ((((floor (_mask / 2)) mod 2) isEqualTo 1)) then {_parts pushBack "Recon";};
  if ((((floor (_mask / 4)) mod 2) isEqualTo 1)) then {_parts pushBack "Logistics";};
  if (_parts isEqualTo []) then {_parts pushBack "Unspecified";};
  _parts joinString " | "
};

YOSHI_setFWInfoText = {
  params ["_fwId"];
  private _entry = [_fwId] call YSF_fwGetEntry;
  if !(typeName _entry isEqualTo "HASHMAP") exitWith {
    [IDC_ASSETS_DETAIL_NAME, "Unknown Fixed Wing Asset"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_GRID, "-"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_SPEED, "-"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_HEADING, "-"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_CARGO, "-"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_PLAYERS, "-"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_FUEL, 0] call YOSHI_setBar;
    [IDC_ASSETS_DETAIL_HEALTH, 0] call YOSHI_setBar;
  };

  private _vehType = _entry getOrDefault ["vehicleType", ""];
  private _callsign = _entry getOrDefault ["callsign", ""];
  private _state = _entry getOrDefault ["state", "stowed"];
  private _roleMask = _entry getOrDefault ["roleMask", 0];
  private _veh = _entry getOrDefault ["spawnedVeh", objNull];

  private _name = getText (configFile >> "CfgVehicles" >> _vehType >> "displayName");
  if (_name isEqualTo "") then {_name = _vehType;};
  if !(_callsign isEqualTo "") then {
    _name = format ["%1 (%2)", _callsign, _name];
  };

  if (!isNull _veh && {alive _veh}) then {
    [_veh] call YOSHI_setVehInfoText;
    [IDC_ASSETS_DETAIL_NAME, _name] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_GRID, mapGridPosition _veh] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_CARGO, [_roleMask] call YOSHI_fwRoleText] call YOSHI_setText;
  } else {
    [IDC_ASSETS_DETAIL_NAME, _name] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_GRID, "STOWED"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_SPEED, "0 m/s"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_HEADING, "-"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_CARGO, [_roleMask] call YOSHI_fwRoleText] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_PLAYERS, "None"] call YOSHI_setText;
    [IDC_ASSETS_DETAIL_FUEL, 1] call YOSHI_setBar;
    [IDC_ASSETS_DETAIL_HEALTH, 1] call YOSHI_setBar;
  };
};

YOSHI_showOrHide = {
  params ["_tab", "_ctrl"];
  disableSerialization;
  private _selectedTab = uiNamespace getVariable ["YSF_asset_type", "transport"];
  private _isSelected = _tab isEqualTo _selectedTab;
  _ctrl ctrlShow _isSelected;
  _ctrl ctrlEnable _isSelected;
  format ["Init: %1 tab is enabled: %2 | meta: %3", _tab, _isSelected, _selectedTab] call YSF_fnc_debugMsg;
  if (_isSelected) then {[] spawn {uiSleep 0.1; call YOSHI_initAssetList;};};
};

YOSHI_showOrHideTaskOrders = {
  disableSerialization;

  private _selectedTab = uiNamespace getVariable ["YSF_asset_type", "transport"];
  private _pairs = [
    [IDC_TASK_G_TRANSPORT,"transport"],
    [IDC_TASK_G_CAS,"cas"],
    [IDC_TASK_G_ARTY,"arty"],
    [IDC_TASK_G_RECON,"recon"],
    [IDC_TASK_G_FIXEDWING,"fixedwing"]
  ];

  {
    private _idc = _x#0;
    private _tab = _x#1;
    private _isSelected = _tab isEqualTo _selectedTab;

    private _ret = [_idc] call YOSHI_getControl;
    private _ctrl = _ret # 0;
    private _ok = _ret # 1;

    if (!(_ok)) exitWith {format["YOSHI_showOrHideTaskOrders: Control not found | %1", _idc] call YSF_fnc_debugMsg;};

    _ctrl ctrlShow _isSelected;
    _ctrl ctrlEnable _isSelected;
    if (_isSelected) then {[] spawn {uiSleep 0.1; call YOSHI_initAssetList;};};
  } forEach _pairs;
};

YOSHI_assetsShowTaskGroup = {
  params ["_tab"];
  disableSerialization;

  private _ret = [IDC_PAGE_ASSETS] call YOSHI_getControl;
  private _g = _ret # 0;
  private _ok = _ret # 1;

  if (!(_ok)) exitWith {"YOSHI_assetsShowTaskGroup: Control not found" call YSF_fnc_debugMsg;};

  private _pairs = [
    [IDC_TASK_G_TRANSPORT,"transport"],
    [IDC_TASK_G_CAS,"cas"],
    [IDC_TASK_G_ARTY,"arty"],
    [IDC_TASK_G_RECON,"recon"],
    [IDC_TASK_G_FIXEDWING,"fixedwing"]
  ];
  {
    private _cg = _g controlsGroupCtrl (_x#0);
    if (!isNull _cg) then { 
      _cg ctrlShow ((_x#1) isEqualTo _tab); 
      _cg ctrlEnable ((_x#1) isEqualTo _tab);
      if ((_x#1) isEqualTo _tab) then {
        switch (_tab) do {
          case "transport": { call YOSHI_taskTRN_SyncControlsFromState; };
          case "cas": { call YOSHI_taskCAS_SyncControlsFromState; };
          case "arty": { call YOSHI_taskArty_SyncControlsFromState; };
          case "recon": { call YOSHI_taskRecon_SyncControlsFromState; };
          case "fixedwing": { call YOSHI_taskFW_SyncControlsFromState; };
        };
      };
    };
  } forEach _pairs;
  format ["Task group shown: %1", _tab] call YSF_fnc_debugMsg;
};

YOSHI_refreshAssetList = {
  params [["_asset_type", uiNamespace getVariable ["YSF_asset_type", "transport"]]];

  disableSerialization;
  // display name + distance
  private _rowText = {
    params ["_veh"];
    private _dn = getText (configFile >> "CfgVehicles" >> typeOf _veh >> "displayName");
    private _dist = round (player distance _veh);
    format ["%1   (%2m)", _dn, _dist]
  };

  // collect vehicles of interest (map-wide)
  private _allVehicles = call YOSHI_getAllVehicles;

  private _items = switch (_asset_type) do {
    // Transport: *player-side helicopters* that are NOT armed (keeps it distinct from CAS)
    case "transport": {
      _allVehicles select {
        alive _x
        && {[_x] call YOSHI_isTransportHelicopter}
      }
    };

    // Artillery: anything your helper returns true for
    case "arty": {
      _allVehicles select {
        alive _x
        && { [_x] call YSF_isArtilleryCapable }
        && {[_x] call YOSHI_cfgSideIsPlayer}
      }
    };

    // CAS: *armed helicopters* on player side
    case "cas": {
      _allVehicles select {
        alive _x
        && {[_x] call YOSHI_isArmedHelicopter}
      }
    };

    // Recon: drones (UAV/UGV) on player side
    default { // "recon"
      _allVehicles select {
        alive _x
        && {[_x] call YOSHI_isRecon}
      }
    };
  };

  // sort by distance

  _items = [_items, [], { player distance _x }, "ASCEND"] call BIS_fnc_sortBy;

  private _ret = [IDC_ASSETS_LIST] call YOSHI_getControl;
  private _list = _ret # 0;
  private _ok = _ret # 1;

  if (!(_ok)) exitWith {"YSF_refreshAssetList: Control not found" call YSF_fnc_debugMsg;};

  lbClear _list;

  // fill list; keep a parallel array so selection can be used later
  private _map = [];
  {
    private _i = _list lbAdd ([_x] call _rowText);
    _list lbSetData [_i, netId _x];
    _map pushBack _x;
  } forEach _items;

  if (_items isEqualTo []) then {
    private _i = _list lbAdd "<No assets found>";
    _list lbSetColor [_i, [1,1,1,0.5]];
  };

  uiNamespace setVariable ["YSF_assets_items", _map];

  format ["%1 assets found of type '%2'", str (count _items), _asset_type] call YSF_fnc_debugMsg;

  _list
};

YOSHI_refreshAssetTree = {
  params [
    ["_asset_type", uiNamespace getVariable ["YSF_asset_type", "transport"]]
  ];

  disableSerialization;
  private _mode = 1;

  private _rowText = {
    params ["_veh"];
    private _dn = getText (configFile >> "CfgVehicles" >> typeOf _veh >> "displayName");
    private _dist = round (player distance _veh);
    format ["%1   (%2m)", _dn, _dist]
  };

  private _allVehicles = call YOSHI_getAllVehicles;

  if (_asset_type isEqualTo "fixedwing") exitWith {
    private _ret = [IDC_ASSETS_TREE] call YOSHI_getControl;
    private _tree = _ret # 0;
    private _ok = _ret # 1;
    if (!_ok) exitWith { "YSF_refreshAssetTree: Control not found" call YSF_fnc_debugMsg };

    // Fixed-wing uses ID-backed rows, not YSF_assets_items/object netIds.
    uiNamespace setVariable ["YSF_assets_items", []];
    tvClear _tree;
    private _registry = call YSF_fwGetRegistrySnapshot;
    diag_log format [
      "[YSF][FWDBG] scope=%1 owner=%2 treeRefresh regCount=%3 savedPath=%4",
      if (isServer) then {"SERVER"} else {"CLIENT"},
      clientOwner,
      count _registry,
      uiNamespace getVariable [format ["YSF_%1_path", _asset_type], []]
    ];
    if (_registry isEqualTo []) exitWith {
      private _i = _tree tvAdd [[], "<No fixed wing assets>"];
      _tree tvSetData [[_i], ""];
      _tree
    };

    private _states = [
      ["stowed", "Ready (Stowed)"],
      ["on_station", "Deployed"],
      ["rtb", "RTB"],
      ["cooldown", "Cooldown"]
    ];

    {
      private _stateKey = _x # 0;
      private _stateLabel = _x # 1;
      private _gIndex = _tree tvAdd [[], _stateLabel];
      private _gPath = [_gIndex];
      private _count = 0;

      {
        _x params ["_id", "_state", "_callsign", "_vehType", "_roleMask"];
        if (_state isEqualTo _stateKey) then {
          private _dn = getText (configFile >> "CfgVehicles" >> _vehType >> "displayName");
          if (_dn isEqualTo "") then {_dn = _vehType;};
          private _name = if (_callsign isEqualTo "") then {_dn} else {format ["%1 (%2)", _callsign, _dn]};

          private _entry = [_id] call YSF_fwGetEntry;
          private _veh = objNull;
          if (typeName _entry isEqualTo "HASHMAP") then {
            _veh = _entry getOrDefault ["spawnedVeh", objNull];
          };
          if (!isNull _veh && {alive _veh}) then {
            _name = format ["%1   (%2m)", _name, round (player distance _veh)];
          };

          private _idx = _tree tvAdd [_gPath, _name];
          _tree tvSetData [_gPath + [_idx], format ["FW:%1", _id]];
          _count = _count + 1;
        };
      } forEach _registry;

      if (_count == 0) then {
        private _idx = _tree tvAdd [_gPath, "<None>"];
        _tree tvSetData [_gPath + [_idx], ""];
      };
    } forEach _states;

    tvExpandAll _tree;
    private _saved_path = uiNamespace getVariable [format ["YSF_%1_path", _asset_type], []];
    _tree tvSetCurSel _saved_path;
    _tree
  };

  private _items = switch (_asset_type) do {
    case "transport": {
      // _mode = 3;
      _allVehicles select {
        alive _x
        && {[_x] call YOSHI_isTransportHelicopter}
      }
    };
    case "arty": {
      _allVehicles select {
        alive _x
        && {[_x] call YSF_isArtilleryCapable}
        && {[_x] call YOSHI_cfgSideIsPlayer}
      }
    };
    case "cas": {
      _allVehicles select {
        alive _x
        && {[_x] call YOSHI_isArmedHelicopter}
      }
    };
    default {
      _mode = 3;
      _allVehicles select {
        alive _x
        && {[_x] call YOSHI_isRecon}
      }
    };
  };

  _items = [_items, [], { player distance _x }, "ASCEND"] call BIS_fnc_sortBy;

  private _ret = [IDC_ASSETS_TREE] call YOSHI_getControl;
  private _tree = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith { "YSF_refreshAssetTree: Control not found" call YSF_fnc_debugMsg };

  tvClear _tree;

  if (_items isEqualTo []) exitWith {
    private _i = _tree tvAdd [[], "<No assets found>"];
    _tree tvSetData [[_i], ""];
    uiNamespace setVariable ["YSF_assets_items", []];
    format ["0 assets found of type '%1'", _asset_type] call YSF_fnc_debugMsg;
    _tree
  };

  private _map = [];

  private _groupMap = createHashMap;

  {
    private _veh = _x;
    private _grp = group _veh;

    private _key = if (isNull _grp) then {
      "__UNGROUPED__"
    } else {
      str _grp
    };

    private _entry = _groupMap getOrDefault [_key, [_grp, []]];
    private _arr = _entry # 1;
    _arr pushBack _veh;
    _entry set [1, _arr];
    _groupMap set [_key, _entry];
  } forEach _items;

  private _keys = keys _groupMap;

  private _sortedKeys = [
    _keys,
    [],
    {
      private _entry = _groupMap get _x;
      private _grp = _entry # 0;
      private _name = if (isNull _grp) then {"Ungrouped"} else {groupId _grp};
      if (_name isEqualTo "") then {_name = "Group"};
      _name
    },
    "ASCEND"
  ] call BIS_fnc_sortBy;

  switch (_mode) do {
    case 1: {
      {
        private _entry = _groupMap get _x;
        private _grp = _entry # 0;
        private _vehicles = _entry # 1;

        private _name = if (isNull _grp) then {"Ungrouped"} else {groupId _grp};
        if (_name isEqualTo "") then {_name = "Group"};

        private _gIndex = _tree tvAdd [[], _name];
        private _gPath = [_gIndex];

        {
          private _veh = _x;
          private _txt = [_veh] call _rowText;
          private _idx = _tree tvAdd [_gPath, _txt];
          private _path = _gPath + [_idx];
          _tree tvSetData [_path, netId _veh];
          _map pushBack _veh;
        } forEach _vehicles;
      } forEach _sortedKeys;
    };
    case 2: {
      {
        private _entry = _groupMap get _x;
        private _grp = _entry # 0;
        private _vehicles = _entry # 1;

        private _name = if (isNull _grp) then {"Ungrouped"} else {groupId _grp};
        if (_name isEqualTo "") then {_name = "Group"};

        private _gIndex = _tree tvAdd [[], _name];
        private _gPath = [_gIndex];

        private _reprVeh = _vehicles select 0;
        _tree tvSetData [_gPath, netId _reprVeh];
        _map pushBack _reprVeh;
      } forEach _sortedKeys;
    };
    default {
      {
        private _veh = _x;
        private _txt = [_veh] call _rowText;
        private _idx = _tree tvAdd [[], _txt];
        private _path = [_idx];
        _tree tvSetData [_path, netId _veh];
        _map pushBack _veh;
      } forEach _items;
    };
  };

  uiNamespace setVariable ["YSF_assets_items", _map];

  format ["%1 assets found of type '%2'", str (count _items), _asset_type] call YSF_fnc_debugMsg;

  tvExpandAll _tree;

  private _saved_path = uiNamespace getVariable [format ["YSF_%1_path", _asset_type], []];

  _tree tvSetCurSel _saved_path;

  _tree
};


YOSHI_assetSelected = {
  params ["_ctrl", "_sel"];

  private _veh = objNull;
  private _data = "";

  private _path = _sel;

  if (_path isEqualTo []) exitWith {
    "No asset selected" call YSF_fnc_debugMsg;
  };

  playSound "UiSelect";

  _data = _ctrl tvData _path;

  // optional fallback: if no data but top-level node, map by index
  private _assetType = uiNamespace getVariable ["YSF_asset_type", "transport"];
  if (_data isEqualTo "" && {count _path == 1} && {!(_assetType isEqualTo "fixedwing")}) then {
    private _i = _path # 0;
    private _items = uiNamespace getVariable ["YSF_assets_items", []];
    if (_i >= 0 && {_i < count _items}) then {
      _veh = _items select _i;
    };
  };

    if (_data != "") then {
    if ((_data find "FW:") == 0) exitWith {
      private _fwId = _data select [3];
      uiNamespace setVariable ["YSF_current_selected_fw_id", _fwId];

      private _entry = [_fwId] call YSF_fwGetEntry;
      private _fwVeh = objNull;
      private _fwState = "";
      if (typeName _entry isEqualTo "HASHMAP") then {
        _fwVeh = _entry getOrDefault ["spawnedVeh", objNull];
        _fwState = _entry getOrDefault ["state", ""];
      };
      diag_log format [
        "[YSF][FWDBG] scope=%1 owner=%2 assetSelected id=%3 state=%4 veh=%5 vehNetId=%6 path=%7",
        if (isServer) then {"SERVER"} else {"CLIENT"},
        clientOwner,
        _fwId,
        _fwState,
        if (isNull _fwVeh) then {"<null>"} else {typeOf _fwVeh},
        if (isNull _fwVeh) then {"<null>"} else {netId _fwVeh},
        _path
      ];

      uiNamespace setVariable ["YSF_current_selected_asset", _fwVeh];
      [_fwId] call YOSHI_setFWInfoText;

      private _arr = uiNamespace getVariable ["YSF_map_overlay_markers", []];
      { deleteMarkerLocal _x } forEach _arr;
      uiNamespace setVariable ["YSF_map_overlay_markers", []];

      if (!isNull _fwVeh && {alive _fwVeh}) then {
        private _m = createMarkerLocal [format ["YSF_mo_fw_%1", _fwId], getPosATL _fwVeh];
        _m setMarkerTypeLocal "loc_plane";
        _m setMarkerTextLocal (getText (configFile >> "CfgVehicles" >> typeOf _fwVeh >> "displayName"));
        _m setMarkerColorLocal (call YSF_getBaseColorFormatted);
        uiNamespace setVariable [
          "YSF_map_overlay_markers",
          (uiNamespace getVariable ["YSF_map_overlay_markers", []]) + [_m]
        ];
      };

      private _asset_type = uiNamespace getVariable ["YSF_asset_type", "transport"];
      uiNamespace setVariable [format ["YSF_%1_path", _asset_type], _path];
      call YOSHI_taskFW_SyncControlsFromState;
      call YOSHI_checkUplinkStatus;
    };
    _veh = objectFromNetId _data;
  };

  if (isNull _veh) exitWith {
    "No asset found" call YSF_fnc_debugMsg;
  };

  uiNamespace setVariable ["YSF_current_selected_asset", _veh];
  uiNamespace setVariable ["YSF_current_selected_fw_id", ""];
  [_veh] call YOSHI_setVehInfoText;
  uiNamespace setVariable ["YOSHI_task_vehicle", _veh];

  private _arr = uiNamespace getVariable ["YSF_map_overlay_markers", []];
  { deleteMarkerLocal _x } forEach _arr;
  uiNamespace setVariable ["YSF_map_overlay_markers", []];

  private _m = createMarkerLocal [format ["YSF_mo_%1", netId _veh], getPosATL _veh];
  _m setMarkerTypeLocal "mil_dot";
  _m setMarkerTextLocal (getText (configFile >> "CfgVehicles" >> typeOf _veh >> "displayName"));
  _m setMarkerColorLocal (call YSF_getBaseColorFormatted);
  uiNamespace setVariable [
    "YSF_map_overlay_markers",
    (uiNamespace getVariable ["YSF_map_overlay_markers", []]) + [_m]
  ];

  private _asset_type = uiNamespace getVariable ["YSF_asset_type", "transport"];
  uiNamespace setVariable [format ["YSF_%1_path", _asset_type], _path];

  format ["Asset selected: %1", name _veh] call YSF_fnc_debugMsg;
  if ((uiNamespace getVariable ["YSF_asset_type", "transport"]) isEqualTo "arty") then {
    call YOSHI_taskArty_DrawFromState;
  };
  call YOSHI_checkUplinkStatus;
};


YOSHI_selectAssetType = {
  params ["_type"];

  uiNamespace setVariable ["YSF_asset_type", _type];
  if !(_type isEqualTo "fixedwing") then {
    uiNamespace setVariable ["YSF_current_selected_fw_id", ""];
  };
  playSound "UiTabSwitch";

  disableSerialization;

  [_type] call YOSHI_refreshAssetTree;
  [_type] call YOSHI_assetsShowTaskGroup;

};

YOSHI_checkUplinkStatus = {

  if ((missionNamespace getVariable ["YSF_governorPFH",-1]) >= 0) then {
    [IDC_TABLET_UPLINK, "CONNECTION ESTABLISHED"] call YOSHI_setText;
  } else {
    [IDC_TABLET_UPLINK, "CONNECTION LOST"] call YOSHI_setText;
  };
};

YOSHI_assetsTabChanged = {
  params ["_ctrl","_idx"];

  uiNamespace setVariable ["YSF_assets_tabIndex", _idx];

  private _types = ["transport","arty","cas","fixedwing"];
  if (_idx < 0 || _idx >= count _types) exitWith {};
  private _type = _types select _idx;

  [_type] call YOSHI_selectAssetType;
  call YOSHI_checkUplinkStatus;
};
