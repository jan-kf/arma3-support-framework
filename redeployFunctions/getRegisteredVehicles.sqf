// Initialize an empty array to store registered vehicles
private _registeredVehicles = [];

// Iterate over all vehicles
{
    // Check if the vehicle is registered
    if (_x getVariable ["isRegistered", false]) then {
        // Add the registered vehicle to the array
        _registeredVehicles pushBack _x;
    };
} forEach vehicles; // using 'vehicles' to get all vehicles

// _registeredVehicles now contains all the registered vehicles
_registeredVehicles
