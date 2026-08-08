params ["_logic"];

if (!isServer) exitWith {};

private _targets = synchronizedObjects _logic;
private _target = if (_targets isNotEqualTo []) then { _targets # 0 } else { attachedTo _logic };

if (isNull _target || {!(_target isKindOf "Plane")}) exitWith {
    deleteVehicle _logic;
    ["Select a valid fixed-wing asset", "VIGIL Notification"] call YSF_fnc_notifyCurator;
};

private _ok = [_target] call YSF_fwRegisterAsset;
if (!_ok) then {
    ["Failed to add fixed-wing asset", "VIGIL Notification"] call YSF_fnc_notifyCurator;
} else {
    ["Added Fixed-Wing Asset", "VIGIL Notification"] call YSF_fnc_notifyCurator;
};

deleteVehicle _logic;
