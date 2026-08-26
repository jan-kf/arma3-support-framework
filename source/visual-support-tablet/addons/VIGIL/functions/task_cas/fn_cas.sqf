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

  [_vehicle, "cas", [_location, _altitude, _time_limit]] call YSF_taskRequestRemote;
};

YSF_taskCASAssign = {
  params ["_vehicle", "_task"];
  if (!isServer || {remoteExecutedOwner > 2} || {isNull _vehicle} || {typeName _task isNotEqualTo "HASHMAP"}) exitWith {false};
  private _existing = (call YSF__mgr) getOrDefault [[_vehicle] call YSF_taskKey, objNull];
  if (typeName _existing isEqualTo "HASHMAP" && {_existing getOrDefault ["enabled", false]}) exitWith {
    _vehicle setVariable ["YSF_cas_lastRequest", "duplicate_rejected", true];
    false
  };
  _vehicle setVariable ["YSF_cas_lastRequest", "accepted", true];
  [_vehicle, _task] call YSF_taskAssign;
  true
};

YSF_taskCASAssignRemote = {
  params ["_vehicle", "_task"];
  if (!isServer || {remoteExecutedOwner > 2}) exitWith {false};
  [_vehicle, _task] call YSF_taskCASAssign
};
