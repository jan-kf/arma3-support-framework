#include "..\..\ui\idc.hpp"

params ["_isJip"];
uiNamespace setVariable ["YSF_tablet_registry", createHashMap];
// ["home", IDC_PAGE_HOME] call YSF_UI_RegisterPage;
// ["admin", IDC_PAGE_ADMIN] call YSF_UI_RegisterPage;
["assets", IDC_PAGE_ASSETS] call YSF_UI_RegisterPage;

YSF_getBaseColorHex = {
  private _rgba = missionNamespace getVariable [
      "YSF_monochromeBaseColor",
      [0,1,0,1]
  ];

  private _rgb = _rgba select [0,3];
  _rgb call BIS_fnc_colorRGBtoHTML
};

YSF_getBaseColorFormatted = {
  private _rgba = missionNamespace getVariable [
      "YSF_monochromeBaseColor",
      [0,1,0,1]
  ];

  format ["#(%1, %2, %3, %4)", _rgba#0, _rgba#1, _rgba#2, _rgba#3]
};

YSF_fnc_introIntoCtrl = {
  call YSF_UI_SetCorrectTablet;
  if !(canSuspend) exitWith {_this spawn YSF_fnc_introIntoCtrl};
  params [
    ["_idc",-1],
    ["_hide_idc", -1],
    ["_lines",["Placeholder Line"]],
    ["_initDelay", 1],
    ["_typeSpeed",0.01],
    ["_lineDelay",0.025],
    ["_minDuration",1],
    ["_fadeOutTime",0.5]
  ];
  
  disableSerialization;
  private _ret = [_idc] call YOSHI_getControl;
  private _ctrl = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {};

  private _ret = [_hide_idc] call YOSHI_getControl;
  private _hide_ctrl = _ret # 0;
  private _ok = _ret # 1;
  if (!_ok) exitWith {};
  
  _hide_ctrl ctrlShow false;

  playSound "BootUp";
  uiSleep _initDelay;
  if (_initDelay >= 1) then {
    [] spawn {
      uiSleep 1;
      playSound "DialUp";
    };
  };

  [_idc] call YSF_initTabletHum;

  if (isNull _ctrl) exitWith {};
  private _start = diag_tickTime;
  private _buf = [];
  {
    private _line = _x;
    for "_i" from 1 to (count _line) do {
      private _prefix = _buf joinString "<br/>";
      private _sep = if (_buf isEqualTo []) then {""} else {"<br/>"};
      private _cur = _prefix + _sep + (_line select [0,_i]);
      _ctrl ctrlSetStructuredText parseText format ["<t color='%1'>%2</t>", call YSF_getBaseColorHex, _cur]; 
      uiSleep _typeSpeed;
    };
    _buf pushBack _line;
    if (_forEachIndex < (count _lines - 1)) then {uiSleep _lineDelay};
  } forEach _lines;
  private _elapsed = diag_tickTime - _start;
  if (_elapsed < _minDuration) then {uiSleep (_minDuration - _elapsed)};
  _ctrl ctrlSetFade 1; _ctrl ctrlCommit _fadeOutTime; uiSleep _fadeOutTime; _ctrl ctrlShow false;
  uiNamespace setVariable [format["YSF_init_played_for_%1", netId player], true];
  playSound "UiActivate";
  
  call YOSHI_showOrHideTaskOrders;
  _hide_ctrl ctrlShow true;

  hintSilent "[Hint] Double-click on the map to quickly select a grid-ref";
};
