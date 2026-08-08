params ["_logic"];

if (!isServer) exitWith {
	[_logic] remoteExecCall ["YAS_fnc_apsModuleEnable", 2];
};

if (isNull _logic) exitWith {};

private _synced = synchronizedObjects _logic;
{
	if (!isNull _x && { _x isKindOf "AllVehicles" }) then {
		[_x] call YOSHI_fnc_apsEnableVehicle;
	};
} forEach _synced;

deleteVehicle _logic;
