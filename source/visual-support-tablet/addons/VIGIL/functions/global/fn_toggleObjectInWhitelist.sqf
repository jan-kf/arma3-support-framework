params ["_logic"];

private _targets = synchronizedObjects _logic;
private _target = if (_targets isNotEqualTo []) then {_targets # 0} else {attachedTo _logic};

if (isNull _target) exitWith { deleteVehicle _logic; ["Not a valid asset", "VIGIL Notification"] call YSF_fnc_notifyCurator; };

[_target] call YSF_toggleWhitelistedObject;

deleteVehicle _logic;
