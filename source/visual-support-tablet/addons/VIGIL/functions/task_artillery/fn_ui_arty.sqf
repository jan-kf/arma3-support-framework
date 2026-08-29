#include "..\..\ui\idc.hpp"

YSF_taskArtyClearWorkspace = {
  { deleteMarkerLocal _x } forEach (uiNamespace getVariable ["YOSHI_sp_markers", []]);
  uiNamespace setVariable ["YOSHI_sp_markers", []];
  uiNamespace setVariable ["YOSHI_taskArty_strikePattern", []];

  private _coordinateMarker = uiNamespace getVariable ["YSF_arty_coord_preview_var", ""];
  if (_coordinateMarker isNotEqualTo "") then {
    deleteMarkerLocal _coordinateMarker;
  };
  uiNamespace setVariable ["YSF_arty_coord_preview_var", ""];

  // Draft targeting state belongs to the artillery page, not to submitted
  // tasks. Removing it makes every new visit construct a clean workspace.
  uiNamespace setVariable ["YOSHI_taskArty_state", nil];
  true
};

YOSHI_taskArty_GetState = {
  private _s = uiNamespace getVariable ["YOSHI_taskArty_state", objNull];
  if !(typeName _s isEqualTo "HASHMAP") then {
    _s = createHashMapFromArray [
      ["grid", [0,0,0]],
      ["pattern","circle"],
      ["spread",50],
      ["count",0],
      ["dir",0],
      ["ord",""]
    ];
    uiNamespace setVariable ["YOSHI_taskArty_state", _s];
  };
  _s
};

YOSHI_taskArty_Set = {
  params ["_k","_v"];
  private _type = uiNamespace getVariable ["YSF_asset_type", "transport"];
  if (_type isNotEqualTo "arty") exitWith {};
  private _s = call YOSHI_taskArty_GetState;
  format ["arty state change: %1 = %2", _k, _v] call YSF_fnc_debugMsg;
  _s set [_k,_v];
  uiNamespace setVariable ["YOSHI_taskArty_state", _s];
};

YOSHI_taskArty_DrawFromState = {
  private _s = call YOSHI_taskArty_GetState;
  private _vehicle = uiNamespace getVariable ["YOSHI_task_vehicle", objNull];
  private _strikePattern = [_s get "grid", _s get "pattern", _s get "spread", _s get "count", _s get "dir", _vehicle, _s get "ord"] call YOSHI_drawStrikePattern;
  uiNamespace setVariable ["YOSHI_taskArty_strikePattern", _strikePattern];
};

YOSHI_arty_setGrid = {
  params ["_pos"];
  ["grid", _pos] call YOSHI_taskArty_Set;
  call YOSHI_taskArty_DrawFromState;
};


YOSHI_setSpread = {
  params ["_key", "_ctrl"];
  [_key, parseNumber (ctrlText _ctrl)] call YOSHI_taskArty_Set;
  call YOSHI_taskArty_DrawFromState;
};

YOSHI_setCount = {
  params ["_key", "_ctrl"];
  [_key, parseNumber (ctrlText _ctrl)] call YOSHI_taskArty_Set;
  call YOSHI_taskArty_DrawFromState;
};

YOSHI_setDirection = {
  params ["_key", "_ctrl"];
  [_key, parseNumber (ctrlText _ctrl)] call YOSHI_taskArty_Set;
  call YOSHI_taskArty_DrawFromState;
};

YOSHI_setPattern = {
  params ["_key", "_ctrl"];
  private _i = lbCurSel _ctrl; 

  if (_i<0) exitWith {}; 

  [_key, toLower (_ctrl lbText _i)] call YOSHI_taskArty_Set;
  call YOSHI_taskArty_DrawFromState;
};

YOSHI_handleOrdinanceSelection = {
  params ["_key", "_ctrl"];
  private _i = lbCurSel _ctrl; 

  if (_i<0) exitWith {}; 

  [_key,  _ctrl lbData _i] call YOSHI_taskArty_Set;
  call YOSHI_taskArty_DrawFromState;
};



YOSHI_taskArty_SyncControlsFromState = {
  private _ret = [IDC_TASK_G_ARTY] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith { "YSF_taskArty_SyncControlsFromState: Control not found" call YSF_fnc_debugMsg; };
  
  private _s = call YOSHI_taskArty_GetState;

  private _patC = ([IDC_TASK_ARTY_PAT_COMBO] call YOSHI_getControl) select 0;
  if (lbSize _patC == 0) then { _patC lbAdd "circle"; _patC lbAdd "line"; };
  private _pat = _s get "pattern";
  private _idxP = (["circle","line"] find _pat) max 0;
  _patC lbSetCurSel _idxP;

  private _ordC = ([IDC_TASK_ARTY_ORD_COMBO] call YOSHI_getControl) select 0;
  if (lbSize _ordC == 0) then {
    { _ordC lbAdd _x } forEach (uiNamespace getVariable ["YOSHI_taskArty_ordOptions", []]);
  };
  private _ord = _s get "ord";
  private _ordIdx = -1;
  for "_i" from 0 to (lbSize _ordC - 1) do { if ((_ordC lbData _i) isEqualTo _ord) exitWith { _ordIdx = _i; }; };
  _ordC lbSetCurSel _ordIdx;

  (([IDC_TASK_ARTY_SPR_EDIT] call YOSHI_getControl) select 0) ctrlSetText str (_s get "spread");
  (([IDC_TASK_ARTY_CNT_EDIT] call YOSHI_getControl) select 0) ctrlSetText str (_s get "count");
  (([IDC_TASK_ARTY_DIR_EDIT] call YOSHI_getControl) select 0) ctrlSetText str (_s get "dir");
  (([IDC_TASK_ARTY_GRID_REF] call YOSHI_getControl) select 0) ctrlSetText ([_s get "grid"] call YOSHI_pos_to_grid);

  call YOSHI_taskArty_DrawFromState;
};


YSF_getArtyOrdComboControl = {
  [IDC_TASK_ARTY_ORD_COMBO] call YOSHI_getControl
};


YOSHI_setOrdinanceOptions = {
  params ["_m"]; 
  disableSerialization;
  private _ret = call YSF_getArtyOrdComboControl;
  private _cmb = _ret # 0;
  private _ok = _ret # 1;

  if (!_ok) exitWith { "YOSHI_setOrdinanceOptions: Control not found" call YSF_fnc_debugMsg; };

  lbClear _cmb;
  private _mags = keys _m;
  if (_mags isEqualTo []) then {
    _cmb lbAdd "<no ordnance>";
  } else {
    private _sorted = [_mags, [], { toLower getText (configFile >> "CfgMagazines" >> _x >> "displayName") }, "ASCEND"] call BIS_fnc_sortBy;
    {
      private _mag = _x;

      if (_mag isNotEqualTo "magazine_Missiles_Cruise_01_Cluster_x18") then {
        private _dn = getText (configFile >> "CfgMagazines" >> _mag >> "displayName");
        if (_dn isEqualTo "") then { _dn = _mag };
        private _info = _m get _mag;
        private _count = _info#0;
        private _ammo = _info#1;
        private _idx = _cmb lbAdd format ["%1 (%2 per mag)", _dn, _ammo];
        _cmb lbSetData [_idx, _mag];
      };
    } forEach _sorted;
    _cmb lbSetCurSel 0;
  };
};
