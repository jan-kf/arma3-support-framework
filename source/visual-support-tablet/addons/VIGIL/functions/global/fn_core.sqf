#include "..\..\ui\idc.hpp"

/*
I believe in one God, the Father almighty,
maker of heaven and earth,
of all things visible and invisible.
I believe in one Lord Jesus Christ,
the Only Begotten Son of God,
born of the Father before all ages.
God from God, Light from Light,
true God from true God, begotten, not made,
consubstantial with the Father;
through him all things were made.
For us men and for our salvation,
he came down from heaven,
and by the Holy Spirit.
was incarnate of the Virgin Mary
and became man.

For our sake, he was crucified under
Pontius Pilate, he suffered death
and was buried, and rose again
on the third day in accordance
with the Scriptures.
He ascended into heaven and
is seated at the right hand of the Father.
He will come again in glory to judge
the living and the dead and his
kingdom will have no end.

I believe in the Holy Spirit,
the Lord, the giver of life,
who proceeds from the Father and the Son,
who with the Father and the Son is adored and glorified,
who has spoken through the prophets.
I believe in one holy, catholic and apostolic Church.
I confess one Baptism for the forgiveness of sins
and I look forward to the resurrection of the dead and
the life of the world to come.
Amen.
*/

// returns true if config side matches player's side
YOSHI_cfgSideIsPlayer = {
  params ["_veh"];
  (((side _veh) call BIS_fnc_sideID) isEqualTo ((side player) call BIS_fnc_sideID))
};

YOSHI_getControl = {
  params ['_idc'];
  disableSerialization;
  
  private _ctrl = displayCtrl _idc;
  if (isNull _ctrl) exitWith { [controlNull, false] };
  [_ctrl, true]
};

// true if helo has meaningful armament
YOSHI_isArmedHelicopter = {
  params ["_veh"];
  if (!(_veh isKindOf "Helicopter")) exitWith {false};
  private _nonLethalSims = ["laserdesignate","shotcm","shotsmoke","shotillum","shotnvGmarker","shotsmokeshell","shotdummy"];
  private _lethal = false;

  {
    private _mag = _x select 0;
    private _cnt = _x select 1;
    if (_cnt > 0) then {
      private _ammo = getText (configFile >> "CfgMagazines" >> _mag >> "ammo");
      if (_ammo != "") then {
        private _sim = toLower getText (configFile >> "CfgAmmo" >> _ammo >> "simulation");
        private _hit = getNumber (configFile >> "CfgAmmo" >> _ammo >> "hit");
        private _ihit = getNumber (configFile >> "CfgAmmo" >> _ammo >> "indirectHit");
        if (!(_sim in _nonLethalSims) && (_hit > 0 || _ihit > 0)) exitWith {_lethal = true};
      };
    };
    if (_lethal) exitWith {};
  } forEach (magazinesAmmoFull _veh);

  if (_lethal) exitWith {true && [_veh] call YOSHI_cfgSideIsPlayer};

  {
    private _ammo = getText (configFile >> "CfgMagazines" >> _x >> "ammo");
    if (_ammo != "") then {
      private _sim = toLower getText (configFile >> "CfgAmmo" >> _ammo >> "simulation");
      private _hit = getNumber (configFile >> "CfgAmmo" >> _ammo >> "hit");
      private _ihit = getNumber (configFile >> "CfgAmmo" >> _ammo >> "indirectHit");
      if (!(_sim in _nonLethalSims) && (_hit > 0 || _ihit > 0)) exitWith {_lethal = true};
    };
    if (_lethal) exitWith {};
  } forEach (getPylonMagazines _veh);

  _lethal && [_veh] call YOSHI_cfgSideIsPlayer
};



// true if vehicle is UAV/UGV recon asset
YOSHI_isRecon = {
  params ["_veh"];
  unitIsUAV _veh && [_veh] call YOSHI_cfgSideIsPlayer
};

YOSHI_isTransportHelicopter = {
  params ["_veh"];
  if (!(_veh isKindOf "Helicopter")) exitWith {false};
  (_veh emptyPositions "cargo") > 0 && locked _veh < 2 && [_veh] call YOSHI_cfgSideIsPlayer
};

YOSHI_parseGrid = {
  params ["_txt"];
  private _parts = (_txt splitString " -,:;") select { _x != "" };
  private _gx = ""; private _gy = "";
  private _isDigitsLen = {
    params ["_s","_len"];
    private _a = toArray _s;
    (count _a == _len) && { ({_x >= 48 && _x <= 57} count _a) == _len }
  };
  if ((count _parts) == 1) then {
    private _s = _parts # 0;
    if ([_s,8] call _isDigitsLen) then {
      _gx = _s select [0,4];
      _gy = _s select [4,4];
    };
  } else {
    if ((count _parts) == 2) then {
      if ([_parts#0,4] call _isDigitsLen && [_parts#1,4] call _isDigitsLen) then {
        _gx = _parts # 0; _gy = _parts # 1;
      };
    };
  };
  if (_gx == "" || _gy == "") exitWith { [] };
  [parseNumber _gx, parseNumber _gy]
};

YOSHI_findCtrlInGroup = {
  params ["_groupIDC","_childIDC"];
  disableSerialization;
  private _d = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
  if (isNull _d) exitWith { controlNull };
  private _g = _d displayCtrl _groupIDC;
  if (isNull _g) exitWith { controlNull };
  _g controlsGroupCtrl _childIDC
};

YOSHI_setText = {
  params ["_childIDC","_txt"];
  disableSerialization;
  private _c = [IDC_PAGE_ASSETS, _childIDC] call YOSHI_findCtrlInGroup;
  if (isNull _c) exitWith {format ["YSF_setText: Control %1 not found", str _childIDC] call YSF_fnc_debugMsg};
  if (ctrlType _c == 13) then { _c ctrlSetStructuredText parseText (str _txt) } else { _c ctrlSetText _txt };
};

YOSHI_progressColor = {
  params ["_val"];             // expects 0..1
  _val = (_val max 0) min 1;   // clamp

  private _r = 0;
  private _g = 0;

  if (_val <= 0.5) then {
    private _t = _val / 0.5;   // 0→0, 0.5→1
    _r = 1;
    _g = _t;
  } else {
    private _t = (_val - 0.5) / 0.5;  // 0.5→0, 1→1
    _r = 1 - _t;
    _g = 1;
  };

  [_r, _g, 0, 1]
};

YOSHI_setBar = {
  params ["_childIDC","_val"];
  disableSerialization;
  private _c = [IDC_PAGE_ASSETS, _childIDC] call YOSHI_findCtrlInGroup;
  if (isNull _c) exitWith {format ["YOSHI_setBar: Control %1 not found", str _childIDC] call YSF_fnc_debugMsg};
  _c progressSetPosition _val;
  _c ctrlSetTextColor (missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]]);
};

YOSHI_assetCoordChanged = {
  params ["_ctrl"];
  private _r = [ctrlText _ctrl] call YOSHI_parseGrid;
  if (_r isEqualTo []) exitWith { hintSilent "Enter XY: 12345678 or 1234-5678"; };
  _r params ["_gx","_gy"];
  private _pos = [_gx*10, _gy*10, 0];  
  
  private _tab = uiNamespace getVariable ["YSF_asset_type", "transport"];
  private _color = "ColorYellow";
  private _symbol = "mil_dot";
  switch (_tab) do {
    case "transport": {
      _color = call YSF_getBaseColorFormatted;//"Color4_FD_F";
      _symbol = "mil_pickup";
      [_pos] call YOSHI_setTRN_Grid;
    };
    case "cas": {
      _color = call YSF_getBaseColorFormatted;//"Color3_FD_F";
      _symbol = "loc_defend";
      [_pos] call YOSHI_cas_setGrid;
    };
    case "arty": {
      _color = call YSF_getBaseColorFormatted;//"Color1_FD_F";
      _symbol = "loc_destroy";
      [_pos] call YOSHI_arty_setGrid;
      call YOSHI_taskArty_DrawFromState;
    };
    case "fixedwing": {
      _color = call YSF_getBaseColorFormatted;//"Color3_FD_F";
      _symbol = "loc_plane";
    };
    default {
      _color = call YSF_getBaseColorFormatted;//"Color2_FD_F";
      [_pos] call YOSHI_recon_setGrid;
    };
  };

  private _markerName = format ["YSF_%1_coord_preview", _tab];
  private _markerVarName = format ["YSF_%1_coord_preview_var", _tab];

  private _m = uiNamespace getVariable [_markerVarName, ""];
  if (_m isEqualTo "") then {
    _m = createMarkerLocal [_markerName, _pos];
    _m setMarkerTypeLocal _symbol;
    _m setMarkerColorLocal _color;
    uiNamespace setVariable [_markerVarName, _m];
  } else {
    _m setMarkerPosLocal _pos;
  };

};

YOSHI_isHeliPad = {
  params ["_obj"];
  (typeOf _obj) in YOSHI_HELIPADS
};

YOSHI_getNearestHelipad = {
  params ["_posATL", ["_maxDist", 20]];
  private _pads = nearestObjects [_posATL, YOSHI_HELIPADS, _maxDist, true, true];

  if (count _pads == 0) exitWith { [false, objNull, [0,0,0]] };

  [true, (_pads select 0), getPosATL (_pads select 0)]
};

YOSHI_pos_to_grid = {
  params ["_pos"];
  private _pad4 = {
    params ["_n"];
    private _s = str (floor ((_n/10) max 0));
    private _len = count _s;
    if (_len >= 4) exitWith { _s select [_len - 4, 4] };
    format ["%1%2", "0000" select [0, 4 - _len], _s]
  };
  format ["%1%2", ([_pos#0] call _pad4), ([_pos#1] call _pad4)]
};

YOSHI_setWaypoint = {
  params ["_unit", "_location", ["_type", "MOVE"]];

  private _group = group _unit;
  private _location2D = [_location select 0, _location select 1, 0];

  private _wp = _group addWaypoint [_location2D, 0];
  _wp setWaypointType _type;
  _wp setWaypointSpeed "NORMAL"; 

  _group setCurrentWaypoint _wp;
};

YOSHI_pad4 = {
  params ["_n"];
  private _s = str (floor _n);
  while {count toArray _s < 4} do {_s = "0" + _s};
  _s
};

YOSHI_handleDoubleClick = {
  params ["_grp", "_grid"];

  private _tab = uiNamespace getVariable ["YSF_asset_type","transport"];
  private _idc = switch (_tab) do {
    case "arty": {IDC_TASK_ARTY_GRID_REF};
    case "cas": {IDC_TASK_CAS_GRID_REF};
    case "recon": {IDC_TASK_RECON_GRID_REF};
    case "fixedwing": {-1};
    default {IDC_TASK_TXP_GRID_REF};
  };

  if (_idc < 0) exitWith {};

  private _gridCtrl = _grp controlsGroupCtrl _idc;
  if (isNull _gridCtrl) exitWith {};
  _gridCtrl ctrlSetText _grid;
  [_gridCtrl] call YOSHI_assetCoordChanged;
};

YOSHI_assets_mapClick = {
  params ["_args"];

  _args params ["_ctrl","_button","_sx","_sy"];

  if (_button != 0) exitWith {};

  disableSerialization;

  private _posW = _ctrl ctrlMapScreenToWorld [_sx,_sy];
  private _gx = floor ((_posW#0)/10);
  private _gy = floor ((_posW#1)/10);
  private _grid = format ["%1-%2", [_gx] call YOSHI_pad4, [_gy] call YOSHI_pad4];

  private _grp = uiNamespace getVariable ["YSF_PageAssets_Group", controlNull];
  if (isNull _grp) exitWith {};
  private _tab = uiNamespace getVariable ["YSF_asset_type","transport"];
  if (_tab isEqualTo "fixedwing") exitWith {};

  [_grp, _grid] call YOSHI_handleDoubleClick;
  playSound "UiMapSelect";
};

YOSHI_setBasicWaypoint = {
  params ["_unit", "_location", ["_type", "MOVE"], ["_override", 1]];

  private _group = group _unit;
  if (!local _unit && {!isNull _group}) exitWith {
    ["YOSHI_setBasicWaypoint", _unit, [_unit, _location, _type, _override]] call YCD_fnc_runOnGroupOwner;
  };

  private _waypoints = waypoints _group;
  private _hasWaypoints = (count _waypoints) > 0;

  if (_override isEqualTo 0 && _hasWaypoints) exitWith {
    currentWaypoint _group
  };

  if (_override isEqualTo 2) then {
    for "_i" from ((count _waypoints) - 1) to 0 step -1 do {
      deleteWaypoint [_group, _i];
    };
  };

  private _location2D = [_location select 0, _location select 1, 0];

  private _wp = _group addWaypoint [_location2D, 0];
  _wp setWaypointType _type;
  _wp setWaypointSpeed "NORMAL"; 

  _group setCurrentWaypoint _wp;

  _wp
};

YOSHI_hardStop = {
  params ["_vic"];

  if (!local _vic) exitWith {
    ["YOSHI_hardStop", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
  };

  _vic land "NONE";

  private _vicGroup = group _vic;
  {
    _x disableAI "all";
    _x enableAI "ANIM";
    _x enableAI "MOVE";
    _x enableAI "PATH";
  } forEach (units _vicGroup);
  _vicGroup setCombatMode "BLUE";
  _vicGroup setBehaviourStrong "SAFE";

  private _group = group _vic;

  for "_i" from (count waypoints _group - 1) to 0 step -1 do
  {
    deleteWaypoint [_group, _i];
  };
};

YOSHI_rebootAI = {
  params ["_vic"];

  if (!local _vic) exitWith {
    ["YOSHI_rebootAI", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
  };

  private _vicGroup = group _vic; 
  {  
    _x enableAI "all";  
  } forEach (units _vicGroup); 
  _vicGroup setCombatMode "GREEN";
  _vicGroup setBehaviourStrong "AWARE";
};

YSF_fnc_setVehicleLandMode = {
  params ["_vic", ["_mode", "NONE"]];

  if (isNull _vic) exitWith {};
  if (!local _vic) exitWith {
    ["YSF_fnc_setVehicleLandMode", _vic, [_vic, _mode]] call YCD_fnc_runOnObjectOwner;
  };

  _vic land _mode;
};

YSF_fnc_setVehicleEngineState = {
  params ["_vic", ["_state", false]];

  if (isNull _vic) exitWith {};
  if (!local _vic) exitWith {
    ["YSF_fnc_setVehicleEngineState", _vic, [_vic, _state]] call YCD_fnc_runOnObjectOwner;
  };

  _vic engineOn _state;
};

YSF_fnc_setVehicleSafeAI = {
  params ["_vic"];

  if (isNull _vic) exitWith {};
  if (!local _vic) exitWith {
    ["YSF_fnc_setVehicleSafeAI", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
  };

  private _vicGroup = group _vic;
  {
    _x disableAI "all";
    _x enableAI "ANIM";
    _x enableAI "MOVE";
    _x enableAI "PATH";
  } forEach (units _vicGroup);
  _vicGroup setCombatMode "BLUE";
  _vicGroup setBehaviourStrong "SAFE";
};

YSF_fnc_setVehicleTransitAI = {
  params ["_vic"];

  if (isNull _vic) exitWith {};
  if (!local _vic) exitWith {
    ["YSF_fnc_setVehicleTransitAI", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
  };

  private _grp = group effectiveCommander _vic;
  if (isNull _grp) exitWith {};

  _grp setSpeedMode "FULL";
  _grp setBehaviour "CARELESS";
};

YOSHI_GET_LGO = { 
  params ["_vehicle"]; 
  private _bombOrder = [];
  private _missileOrder = [];
  private _bombCounts = createHashMap;
  private _missileCounts = createHashMap;
  private _vehicleMags = magazinesAmmoFull _vehicle;

  { 
    private _weapon = _x; 
    private _mags = getArray (configFile >> "CfgWeapons" >> _weapon >> "magazines"); 

    { 
      private _magazine = _x; 
      private _ammoType = getText (configFile >> "CfgMagazines" >> _magazine >> "ammo"); 
      if !(_ammoType isEqualTo "") then {
        private _laserLock = getNumber (configFile >> "CfgAmmo" >> _ammoType >> "laserLock");
        private _irLock = getNumber (configFile >> "CfgAmmo" >> _ammoType >> "irLock");
        private _airLock = getNumber (configFile >> "CfgAmmo" >> _ammoType >> "airLock");

        private _aceGuidanceCfg = configFile >> "CfgAmmo" >> _ammoType >> "ace_missileguidance";
        private _hasAceGuidance = isClass _aceGuidanceCfg;
        if (_hasAceGuidance && {getNumber (_aceGuidanceCfg >> "enabled") <= 0}) then {
          _hasAceGuidance = false;
        };

        private _isGuidedCandidate = (_laserLock > 0) || (_irLock > 0) || _hasAceGuidance;
        private _isFalsePositiveAA = _airLock > 0;

        private _tag = toLower format ["%1|%2|%3", _weapon, _magazine, _ammoType];
        private _isBomb = ((_tag find "bomb") > -1) || ((_tag find "gbu") > -1) || ((_tag find "vblauncher") > -1) || ((_tag find "mk82") > -1) || ((_tag find "cluster") > -1);
        private _ammoCount = 0;
        {
          if ((_x select 0) isEqualTo _magazine) then {
            _ammoCount = _ammoCount + ((_x select 1) max 0);
          };
        } forEach _vehicleMags;
        private _hasAmmo = _ammoCount > 0; 

        if (_isGuidedCandidate && !_isFalsePositiveAA && _hasAmmo) then { 
          if (_isBomb) then { 
            if ((_bombOrder find _weapon) < 0) then {_bombOrder pushBack _weapon;};
            _bombCounts set [_weapon, (_bombCounts getOrDefault [_weapon, 0]) + _ammoCount];
          } else { 
            if ((_missileOrder find _weapon) < 0) then {_missileOrder pushBack _weapon;};
            _missileCounts set [_weapon, (_missileCounts getOrDefault [_weapon, 0]) + _ammoCount];
          }; 
        }; 
      };
    } forEach _mags; 
  } forEach (weapons _vehicle); 

  private _bombOut = [];
  {
    private _weapon = _x;
    private _count = _bombCounts getOrDefault [_weapon, 0];
    private _dn = getText (configFile >> "CfgWeapons" >> _weapon >> "displayName");
    if (_dn isEqualTo "") then {_dn = _weapon;};
    _bombOut pushBack [_weapon, _count, _dn];
  } forEach _bombOrder;

  private _missileOut = [];
  {
    private _weapon = _x;
    private _count = _missileCounts getOrDefault [_weapon, 0];
    private _dn = getText (configFile >> "CfgWeapons" >> _weapon >> "displayName");
    if (_dn isEqualTo "") then {_dn = _weapon;};
    _missileOut pushBack [_weapon, _count, _dn];
  } forEach _missileOrder;

  [_bombOut, _missileOut] 
};

YSF_isVehicle = { params ["_o"]; (_o isKindOf "AllVehicles") && !(_o isKindOf "Man") };

YSF_initTabletHum = {
  params ["_idc"];
  

  [_idc] spawn {
    params ["_idc"];

    while {
      private _ret = [_idc] call YOSHI_getControl;
      private _ctrl = _ret # 0;
      private _ok = _ret # 1;
      _ok
    } do {
      playSound "UiHum";
      uiSleep 2;
    };
  };
};

YSF_submitButtonDebounce = {
  playSound "UiSubmit";
  [] spawn {
    private _ret = [IDC_TASK_SUBMIT] call YOSHI_getControl;
    private _ctrl = _ret # 0;
    private _ok = _ret # 1;
    if (!_ok) exitWith {};
    
    _ctrl ctrlEnable false;
    hint "Submitting request...";
    uiSleep 3;
    _ctrl ctrlEnable true;
    hintSilent "";
  };
};

YSF_isArtilleryCapable = {
    params ["_unit"];
    
    private _isArtillery = !(_unit isKindOf "Air") && {(_unit isKindOf "LandVehicle") || (_unit isKindOf "Ship")}; 
    private _canDoArtilleryFire = (_isArtillery && (alive _unit) && (getArtilleryAmmo [_unit] isNotEqualTo [])) || ((typeOf _unit) isEqualTo "B_Ship_MRLS_01_F"); 

    _canDoArtilleryFire 
};

// _this addEventHandler ["HitPart", {
//   {
// 		_x params [
// 			"_target", "_shooter", "_projectile", "_position", "_velocity",
// 			"_selection", "_ammo", "_vector", "_radius", "_surfaceType",
// 			"_isDirect", "_instigator"
// 		];
//     private _F = _velocity vectorAdd [0,0,20];
//     private _modifier = (vectorMagnitude _F)/2000;
//     _F = _F vectorMultiply _modifier;
//     if (vectorMagnitude _F < 200) exitWith {};
//     private _impactSite = _position vectorDiff (getPosASL _target);
//     _target addForce [_F, _impactSite , false];

// 	} forEach _this;

// }];
