params ["_logic"];

if (!isServer) exitWith {};
if (isNull _logic) exitWith {};

private _synced = synchronizedObjects _logic;
private _registered = 0;

{
    private _obj = _x;
    if (!isNull _obj && { _obj isKindOf "Plane" }) then {
        private _ok = [_obj] call YSF_fwRegisterAsset;
        if (_ok) then { _registered = _registered + 1; };
    };
} forEach _synced;

format ["[YSF_FixedWing] Registered %1 synced fixed-wing assets.", _registered] call YSF_fnc_debugMsg;
