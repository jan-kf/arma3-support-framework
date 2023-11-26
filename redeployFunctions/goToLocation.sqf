#include "leaveCurrentLocation.sqf"
#include "arriveAtDestination.sqf"

// _checkIfStationary = compile preprocessFile "redeployFunctions\checkIfStationary.sqf";

private _goToLocation = {
	params [
		"_vic",  
		"_groupLeader", 
		"_goHome", 
		["_doFallback", nil],
		["_wavingOff", false],
		["_first_message", nil], 
		["_last_message", nil],
		["_fallbackTimeoutDuration", 300],
		["_fallbackStationaryThreashold", 3]
	];
	private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};

	[_vic, _groupLeader, _goHome, _first_message, _wavingOff] call _leaveCurrentLocation;


	if (_vicStatus get "cancelRedeploy" || (_vicStatus get "waveOff" && !_wavingOff)) exitWith {
		true
	};

	

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};

	[_vic, _groupLeader, _goHome, _last_message, _wavingOff] call _arriveAtDestination;
};