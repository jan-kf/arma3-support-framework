#define YSF_HOME_CANCEL_COL 4

YSF_home_onLoad = {
  params ["_ctrl"];
  disableSerialization;
  uiNamespace setVariable ["YSF_home_display", ctrlParent _ctrl];
  ["refresh"] call YSF_home_tasks;
};

YSF__vehLabel = {
  params ["_veh"];
  if (isNull _veh) exitWith {"<no vehicle>"};
  private _v = vehicleVarName _veh;
  private _d = getText (configFile >> "CfgVehicles" >> typeOf _veh >> "displayName");
  if (_v isEqualTo "") exitWith {_d};
  format ["%1 (%2)", _v, _d]
};

YSF_home_tasks = {
  params ["_mode"];
  disableSerialization;
  private _disp = uiNamespace getVariable ["YSF_home_display", displayNull];
  if (isNull _disp) exitWith {};
  private _lnb = _disp displayCtrl IDC_HOME_TASKS;

  switch _mode do {
    case "refresh": {
      uiNamespace setVariable ["YSF_home_tasks_rows", []];
      lnbClear _lnb;
      private _tasks = call YSF__mgr;
      if (!(_tasks isEqualType [])) then {_tasks = []};
      {
        private _veh = objNull; private _typ=""; private _stg=""; private _sta="";
        private _t = _x;
        private _tn = typeName _t;
        if (_tn == "ARRAY") then {
          _veh = _t param [0, objNull];
          _typ = str (_t param [1, ""]);
          _stg = str (_t param [2, ""]);
          _sta = str (_t param [3, ""]);
        } else {
          if (_tn == "HASHMAP") then {
            _veh = _t getOrDefault ["veh", objNull];
            _typ = str (_t getOrDefault ["type",""]);
            _stg = str (_t getOrDefault ["stage",""]);
            _sta = str (_t getOrDefault ["state",""]);
          } else {
            _veh = _t getVariable ["veh", objNull];
            _typ = str (_t getVariable ["type",""]);
            _stg = str (_t getVariable ["stage",""]);
            _sta = str (_t getVariable ["state",""]);
          };
        };
        private _label = [_veh] call YSF__vehLabel;
        private _row = _lnb lnbAddRow [_label, _typ, _stg, _sta, "Cancel"];
        private _map = uiNamespace getVariable ["YSF_home_tasks_rows", []];
        _map set [_row, _veh];
        uiNamespace setVariable ["YSF_home_tasks_rows", _map];
      } forEach _tasks;
    };
    case "cancelSelected": {
      private _row = lnbCurSelRow _lnb;
      if (_row < 0) exitWith {};
      private _map = uiNamespace getVariable ["YSF_home_tasks_rows", []];
      private _veh = _map param [_row, objNull];
      if (!isNull _veh) then { [_veh] call YSF_taskCancel; ["refresh"] call YSF_home_tasks; };
    };
  };
};

YSF_home_tasks_click = {
  params ["_evt", "_thisArgs"];
  _thisArgs params ["_ctrl", "_selRow"];
  disableSerialization;
  private _sel = lbCurSel _ctrl;
  if (_sel isEqualTo []) exitWith {};
  private _row = _sel#0;
  private _col = _sel#1;
  if (_evt == "dbl" && {_col == YSF_HOME_CANCEL_COL}) then {
    private _map = uiNamespace getVariable ["YSF_home_tasks_rows", []];
    private _veh = _map param [_row, objNull];
    if (!isNull _veh) then { [_veh] call YSF_taskCancel; ["refresh"] call YSF_home_tasks; };
  };
};
