#include "..\..\ui\idc.hpp"

YSF_CAS_ARRIVAL_RADIUS = 1000;

YOSHI_taskCAS_GetState = {
  private _s = uiNamespace getVariable ["YOSHI_taskCAS_state", objNull];
  if !(typeName _s isEqualTo "HASHMAP") then {
    _s = createHashMapFromArray [
      ["grid", [0,0,0]],
      ["alt",20],
      ["time_limit",2]
    ];
    uiNamespace setVariable ["YOSHI_taskCAS_state", _s];
  };
  _s
};

YOSHI_taskCAS_Set = {
  params ["_k","_v"];
  private _s = call YOSHI_taskCAS_GetState;
  _s set [_k,_v];
  uiNamespace setVariable ["YOSHI_taskCAS_state", _s];
};

YOSHI_cas_setGrid = {
  params ["_pos"];
  ["grid", _pos] call YOSHI_taskCAS_Set;
};

YOSHI_setCAS_Altitude = {
  params ["_key", "_ctrl"];
  [_key, parseNumber (ctrlText _ctrl)] call YOSHI_taskCAS_Set;
};

YOSHI_setCAS_TimeLimit = {
  params ["_key", "_ctrl"];
  [_key, parseNumber (ctrlText _ctrl)] call YOSHI_taskCAS_Set;
};

YOSHI_taskCAS_SyncControlsFromState = {
  private _ret = [IDC_TASK_G_CAS] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {};

  private _s = call YOSHI_taskCAS_GetState;
  (_grp controlsGroupCtrl IDC_TASK_CAS_ALT_EDIT) ctrlSetText str (_s get "alt");
  (_grp controlsGroupCtrl IDC_TASK_CAS_TL_EDIT) ctrlSetText str (_s get "time_limit");
  (_grp controlsGroupCtrl IDC_TASK_CAS_GRID_REF) ctrlSetText ([_s get "grid"] call YOSHI_pos_to_grid);
};

YOSHI_taskCAS_submit = {
  private _vehicle = uiNamespace getVariable ["YSF_current_selected_asset", objNull];
  if (isNull _vehicle) exitWith {"No vehicle selected for cas task" call YSF_fnc_debugMsg;};

  call YSF_submitButtonDebounce;

  private _s = call YOSHI_taskCAS_GetState;
  private _location = _s get "grid";
  private _altitude = _s get "alt";
  private _time_limit = _s get "time_limit";

  private _handlers = call YSF_handlers_cas;
  private _task = ["cas", _vehicle, _handlers, [_location, _altitude, _time_limit], 10, 3] call YSF_taskNew;
  [_vehicle, _task] call YSF_taskAssignRemote;
};
