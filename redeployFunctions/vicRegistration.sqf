#include "homeBaseManifest.sqf"

params ["_vic"];

private _vicIsRegistered = [_vic] call _isVehicleRegistered;

if (_vicIsRegistered) then {
	// driver _vic sideChat "I am already registered and awaiting further tasking.";
	private oldRegActionID = _vic getVariable ["regActionID", nil];
	if (!isNil oldRegActionID) then {
		_vic removeAction oldRegActionID;
	};
	private actionID = _vic addAction [
		"Unregister Vehicle", 
		{
			private _vehicle = _this select 0;
			[_vehicle] call _unregisterVehicle;
		}
	];
	_vic setVariable ["regActionID", regActionID];
} else {
	private oldRegActionID = _vic getVariable ["regActionID", nil];
	if (!isNil oldRegActionID) then {
		_vic removeAction oldRegActionID;
	};
	private regActionID = _vic addAction [
		"Register Vehicle", 
		{
			private _vehicle = _this select 0;
			[_vehicle] call _registerVehicle;
		}
	];
	_vic setVariable ["regActionID", regActionID];
};