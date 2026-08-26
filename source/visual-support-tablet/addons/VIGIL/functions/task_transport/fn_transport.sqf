#include "..\..\ui\idc.hpp"

YOSHI_taskTransport_GetState = {
  private _s = uiNamespace getVariable ["YOSHI_taskTransport_state", objNull];
  if !(typeName _s isEqualTo "HASHMAP") then {
    _s = createHashMapFromArray [
      ["grid", [0,0,0]],
      ["alt",20],
      ["ignore_en",false],
      ["do_not_climb",false]
    ];
    uiNamespace setVariable ["YOSHI_taskTransport_state", _s];
  };
  _s
};

YOSHI_taskTransport_Set = {
  params ["_k","_v"];
  private _s = call YOSHI_taskTransport_GetState;
  _s set [_k,_v];
  uiNamespace setVariable ["YOSHI_taskTransport_state", _s];
};

YOSHI_setTRN_Grid = {
  params ["_pos"];
  ["grid", _pos] call YOSHI_taskTransport_Set;
};

YOSHI_setTRN_Altitude = {
  params ["_key", "_ctrl"];
  [_key,parseNumber (ctrlText _ctrl)] call YOSHI_taskTransport_Set;
};

YOSHI_setTRN_IgnoreEnemy = {
  params ["_key", "_ctrl"];
  [_key, ctrlChecked _ctrl] call YOSHI_taskTransport_Set;
};

YOSHI_setTRN_DoNotClimb = {
  params ["_key", "_ctrl"];
  [_key, ctrlChecked _ctrl] call YOSHI_taskTransport_Set;
};

YOSHI_getTRN_key = {
  params ["_key"];
  private _s = call YOSHI_taskTransport_GetState;
  _s get _key
};

YOSHI_taskTRN_SyncControlsFromState = {
  private _ret = [IDC_TASK_G_TRANSPORT] call YOSHI_getControl;
  private _grp = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {};

  private _s = call YOSHI_taskTransport_GetState;

  (_grp controlsGroupCtrl IDC_TASK_TXP_ALT_EDIT) ctrlSetText str (_s get "alt");
  (_grp controlsGroupCtrl IDC_TASK_TXP_IGN_CHK) ctrlSetChecked  (_s get "ignore_en");
  (_grp controlsGroupCtrl IDC_TASK_TXP_DCL_CHK) ctrlSetChecked  (_s get "do_not_climb");
  (_grp controlsGroupCtrl IDC_TASK_TXP_GRID_REF) ctrlSetText  ([_s get "grid"] call YOSHI_pos_to_grid);

};

YOSHI_taskTRN_submit = {

  private _vehicle = uiNamespace getVariable ["YSF_current_selected_asset", objNull];

  if (isNull _vehicle) exitWith {"No vehicle selected for transport task" call YSF_fnc_debugMsg;};

  call YSF_submitButtonDebounce;
  
  private _s = call YOSHI_taskTransport_GetState;
  private _destPos  = _s get "grid";
  private _maxAlt  = _s get "alt";
  private _do_not_climb = _s get "do_not_climb";
  private _ignoreEn = _s get "ignore_en";

  [_vehicle, "transport", [_destPos, _maxAlt, _do_not_climb, _ignoreEn, "dispatch"]] call YSF_taskRequestRemote;

};

YOSHI_taskTRN_rtb = {
  private _vehicle = uiNamespace getVariable ["YSF_current_selected_asset", objNull];
  if (isNull _vehicle) exitWith {"No vehicle selected for transport RTB" call YSF_fnc_debugMsg;};
  private _home = _vehicle getVariable ["YSF_transport_homeATL", []];
  if !(_home isEqualType [] && {count _home >= 2}) exitWith {"Transport has no recorded home" call YSF_fnc_debugMsg;};
  call YSF_submitButtonDebounce;
  private _s = call YOSHI_taskTransport_GetState;
  [_vehicle, "transport", [_home, _s get "alt", _s get "do_not_climb", _s get "ignore_en", "rtb"]] call YSF_taskRequestRemote;
};

YOSHI_findBestLZ = {
  params ["_center", ["_vehicle", objNull]];
  private _radius = 15;
  if (!isNull _vehicle) then {
    private _box = boundingBox _vehicle;
    _radius = (_box#0 distance _box#1) / 2;
  };

  private _safe = [_center, 0, 300, round _radius, 0, 0.3] call BIS_fnc_findSafePos;


  private _pos = [_safe#0, _safe#1, 0];

  if ((count _safe) == 3) then { 
    _pos = _center; 
  };

  format ["[YSF_TransportTask] Calculated LZ at %1", _pos] call YSF_fnc_debugMsg;
  _pos
};
