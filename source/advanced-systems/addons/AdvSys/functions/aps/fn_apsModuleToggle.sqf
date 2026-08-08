params ["_logic"];

if (!isServer) exitWith {
	[_logic] remoteExecCall ["YAS_fnc_apsModuleToggle", 2];
};

if (isNull _logic) exitWith {};

private _targets = synchronizedObjects _logic;
private _target = if (_targets isNotEqualTo []) then { _targets # 0 } else { attachedTo _logic };

if (isNull _target || {!(_target isKindOf "AllVehicles")}) exitWith {
	["Select a valid vehicle for APS toggle", "AdvSys APS"] call YAS_fnc_notifyCurator;
	deleteVehicle _logic;
};

private _isEnabled = [_target] call YOSHI_fnc_apsToggleVehicle;
private _msg = if (_isEnabled) then {
	"APS turned ON"
} else {
	"APS turned OFF"
};

[_msg, "AdvSys APS"] call YAS_fnc_notifyCurator;

deleteVehicle _logic;
