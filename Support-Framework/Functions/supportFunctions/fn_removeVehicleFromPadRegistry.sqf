params ["_vehicle"];
private _basePads = call SupportFramework_fnc_getPadsNearBase;
// Vehicle netId to check against
private _vehicleNetId = netId _vehicle;

// Iterate over each pad in _basePads
{
	// Get the stored vehicle netId for this pad
	private _storedVehicleNetId = _x getVariable ["assignment", ""];

	// Check if this pad has the vehicle registered
	if (_storedVehicleNetId isEqualTo _vehicleNetId) then {
		// If so, set the variable to nil to unregister the vehicle
		_x setVariable ["assignment", nil];
	};
} forEach _basePads;