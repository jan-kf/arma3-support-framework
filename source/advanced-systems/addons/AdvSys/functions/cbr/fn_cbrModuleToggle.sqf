params ["_logic"];

if (!isServer) exitWith {
	[_logic] remoteExecCall ["YAS_fnc_cbrModuleToggle", 2];
};

if (isNull _logic) exitWith {};

private _isEnabled = [] call YOSHI_fnc_cbrToggleEnabled;

private _msg = if (_isEnabled) then {
	"Counter Batter Radar (CBR) turned ON"
} else {
	"Counter Batter Radar (CBR) turned OFF"
};

[_msg, "AdvSys CBR"] call YAS_fnc_notifyCurator;

deleteVehicle _logic;
