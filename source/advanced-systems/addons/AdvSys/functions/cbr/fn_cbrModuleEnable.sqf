params ["_logic"];

if (!isServer) exitWith {
	[_logic] remoteExecCall ["YAS_fnc_cbrModuleEnable", 2];
};

if (isNull _logic) exitWith {};

[true] call YOSHI_fnc_cbrSetEnabled;

deleteVehicle _logic;
