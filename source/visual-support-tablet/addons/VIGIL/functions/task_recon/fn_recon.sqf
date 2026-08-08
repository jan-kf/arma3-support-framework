#include "..\..\ui\idc.hpp"

YOSHI_taskRecon_GetState = {
  private _s = uiNamespace getVariable ["YOSHI_taskRecon_state", objNull];
  if !(typeName _s isEqualTo "HASHMAP") then {
    _s = createHashMapFromArray [
      ["grid", [0,0,0]],
      ["alt",200],
      ["radius",300]
    ];
    uiNamespace setVariable ["YOSHI_taskRecon_state", _s];
  };
  _s
};

YOSHI_taskRecon_Set = {
  params ["_k","_v"];
  private _s = call YOSHI_taskRecon_GetState;
  _s set [_k,_v];
  uiNamespace setVariable ["YOSHI_taskRecon_state", _s];
};

YOSHI_recon_setGrid = {
  params ["_pos"];
  ["grid", _pos] call YOSHI_taskRecon_Set;
};

YOSHI_setRecon_Altitude = {
  params ["_key", "_ctrl"];
  [_key,parseNumber (ctrlText _ctrl)] call YOSHI_taskRecon_Set;
};

YOSHI_setRecon_Radius = {
  params ["_key", "_ctrl"];
  [_key,parseNumber (ctrlText _ctrl)] call YOSHI_taskRecon_Set;
};

YOSHI_taskRecon_SyncControlsFromState = {
  private _ret = [IDC_TASK_G_RECON] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {};

  private _s = call YOSHI_taskRecon_GetState;

  (_grp controlsGroupCtrl IDC_TASK_RECON_ALT_EDIT) ctrlSetText str (_s get "alt");
  (_grp controlsGroupCtrl IDC_TASK_RECON_RAD_EDIT) ctrlSetText str (_s get "radius");
  (_grp controlsGroupCtrl IDC_TASK_RECON_GRID_REF) ctrlSetText ([_s get "grid"] call YOSHI_pos_to_grid);
};
