params ["_vehicle"];
private _groupLeader = _vehicle getVariable "targetGroupLeader";

if (isNil "_groupLeader") exitWith {};

private _vehicleNetId = netId _vehicle;
private _awayPads = [_groupLeader] call YOSHI_fnc_getPadsNearTarget;
{
	private _storedVehicleNetId = _x getVariable ["assignment", ""];
	// Check if this pad has the vehicle registered
	if (_storedVehicleNetId isEqualTo _vehicleNetId) then {
		// If so, set the variable to nil to unregister the vehicle
		_x setVariable ["assignment", nil];
	};
} forEach _awayPads;