#include "..\..\ui\idc.hpp"

YOSHI_taskArty_submit = {
    private _vehicle = uiNamespace getVariable ["YSF_current_selected_asset", objNull];
    if (isNull _vehicle) exitWith {"No vehicle selected for artillery task" call YSF_fnc_debugMsg;};
    call YSF_submitButtonDebounce;

    private _s = call YOSHI_taskArty_GetState;
    private _ordinance = _s get "ord";
    private _strikePositions = uiNamespace getVariable ["YOSHI_taskArty_strikePattern", []];

    [_vehicle, "artillery", [_strikePositions, _ordinance]] call YSF_taskRequestRemote;
};

YOSHI_drawStrikePattern = {
  params ["_pos", ["_pattern", "circle"], ["_spread", 50], ["_num", 0], ["_dir", 0], ["_vehicle", objNull], ["_ord", ""]];
  
  private _origin = _pos;
  if (!(isNull _vehicle)) then {
    _origin = getPosATL _vehicle;
  };

  private _cx = _pos select 0;
  private _cy = _pos select 1;
  private _positions = [];
  private _vec = [sin _dir, cos _dir];
  private _varKey = "YOSHI_sp_markers";

  { deleteMarkerLocal _x } forEach (uiNamespace getVariable [_varKey, []]);
  private _tab = uiNamespace getVariable ["YSF_asset_type", "transport"];
  if (_tab isNotEqualTo "arty") exitWith {};
  private _created = [];

  if (_num < 1) exitWith {
    uiNamespace setVariable [_varKey, []];
    []
  };

  switch (toLower _pattern) do {
    case "line": {
      if (_num == 1) then {
        _positions = [[_cx, _cy]];
      } else {
        private _half = _spread / 2;
        private _step = _spread / (_num - 1);
        for "_i" from 0 to (_num - 1) do {
          private _t = -_half + (_i * _step);
          _positions pushBack [_cx + ((_vec select 0) * _t), _cy + ((_vec select 1) * _t), 0];
        };
      };
    };
    case "circle": {
      if (_num == 1) then {
        _positions = [[_cx, _cy]];
      } else {
        private _ga = 137.50776405003785;
        for "_k" from 0 to (_num - 1) do {
          private _r = _spread * sqrt((_k + 0.5) / _num);
          private _ang = (_ga * _k) mod 360;
          _positions pushBack [_cx + (sin _ang) * _r, _cy + (cos _ang) * _r, 0];
        };
      };
    };
    default {
      _positions = [[_cx, _cy, 0]];
    };
  };

  if ((toLower _pattern) isEqualTo "line" && {_num > 1}) then {
    _positions = [_positions, [], { (((_x select 0) - _cx) * (_vec select 0)) + (((_x select 1) - _cy) * (_vec select 1)) }, "ASCEND"] call BIS_fnc_sortBy;
  } else {
    _positions = [_positions, [], { ((([_pos, _x] call BIS_fnc_dirTo) - _dir) + 360) mod 360 }, "ASCEND"] call BIS_fnc_sortBy;
  };

  private _base = format ["YOSHI_sp_%1_%2", floor (diag_tickTime * 1000), floor (random 1e6)];

  private _isVLS = (typeOf _vehicle isEqualTo "B_Ship_MRLS_01_F");
  for "_i" from 0 to ((count _positions) - 1) do {
    private _p = _positions select _i;
    private _e = format ["%1_e_%2", _base, _i];
    private _iM = format ["%1_i_%2", _base, _i];
    private _inRange = true;
    private _eta = 0;
    private _units = units (group (effectiveCommander _vehicle));
    if (!(isNull _vehicle) && (_ord isNotEqualTo "")) then {
      _inRange = _p inRangeOfArtillery [_units, _ord];
      _eta = _vehicle getArtilleryETA [_p, _ord];
    };
    format ["Position %1: %2 | In Range: %3 | ETA: %4 | ord: %5", (_i + 1), _p, _inRange, _eta, _ord] call YSF_fnc_debugMsg;
    format ["Units: %1", _units] call YSF_fnc_debugMsg;

    createMarkerLocal [_e, _p];
    _e setMarkerShapeLocal "ELLIPSE";
    _e setMarkerBrushLocal "Border";
    if (_inRange || _isVLS) then {
      _e setMarkerColorLocal (call YSF_getBaseColorFormatted); //"ColorRed";
    } else {
      _e setMarkerColorLocal "ColorGrey";
    };
    if (_isVLS) then {
      if ("cluster" in (toLower _ord)) then {
        _e setMarkerSizeLocal [140, 200];
      } else {
        _e setMarkerSizeLocal [25, 25];
      };
    } else {
      _e setMarkerSizeLocal [100, 125];
    };
    _markerDir = _origin getDir _p;
    _e setMarkerDirLocal _markerDir;
    _created pushBack _e;

    if (_i == 0 && _eta > 0) then {
      createMarkerLocal [_iM, _p];
      _iM setMarkerTypeLocal "mil_dot";
      _iM setMarkerColorLocal (call YSF_getBaseColorFormatted);//"ColorRed";
      _iM setMarkerTextLocal format["1st Round ETA: %1s", round _eta];
      _iM setMarkerSizeLocal [0.6, 0.6];
      _created pushBack _iM;
    };
  };

  uiNamespace setVariable [_varKey, _created];
  _positions
};
