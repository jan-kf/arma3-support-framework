// Function to register a vehicle
private _registerVehicle = {
    params ["_vehicle"];
    private _registeredVehicles = home_base getVariable ["registeredVehicles", []];
    _registeredVehicles pushBackUnique _vehicle;
    home_base setVariable ["registeredVehicles", _registeredVehicles, true];
};

// Function to unregister a vehicle
private _unregisterVehicle = {
    params ["_vehicle"];
    private _registeredVehicles = home_base getVariable ["registeredVehicles", []];
    _registeredVehicles deleteAt (_registeredVehicles find _vehicle);
    home_base setVariable ["registeredVehicles", _registeredVehicles, true];
};

// Function to check if a vehicle is registered
private _isVehicleRegistered = {
    params ["_vehicle"];
    private _registeredVehicles = home_base getVariable ["registeredVehicles", []];
    _vehicle in _registeredVehicles
};

// // Usage
// [_vehicle] call _registerVehicle;
// [_vehicle] call _unregisterVehicle;
// private _registered = [_vehicle] call _isVehicleRegistered;
