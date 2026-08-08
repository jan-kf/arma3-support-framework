params ["_logic"];

if (!isServer) exitWith {};
if (isNull _logic) exitWith {};

private _pos = getPosASL _logic;
if ((count _pos) < 3) then {
    _pos set [2, 1200];
};
if ((_pos select 2) < 200) then {
    _pos set [2, 1200];
};

missionNamespace setVariable ["YSF_FW_DEFAULT_INFIL_POS", _pos, true];
["infil", _pos] call YSF_fwApplyDefaultPointToRegistry;
