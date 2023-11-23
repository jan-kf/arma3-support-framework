#include "leaveCurrentLocation.sqf"
#include "arriveAtDestination.sqf"
// #include "checkIfStationary.sqf"

_checkIfStationary = compile preprocessFile "redeployFunctions\checkIfStationary.sqf";

private _goToLocation = {
	params [
		"_vic",  
		"_groupLeader", 
		"_goHome", 
		["_doFallback", nil],
		["_first_message", nil], 
		["_last_message", nil],
		["_fallbackTimeoutDuration", 300],
		["_fallbackStationaryThreashold", 3]
	];

	if (_vic getVariable "waveOff") exitWith {
		true
	};

	[_vic, _groupLeader, _goHome, _first_message] call _leaveCurrentLocation;

	if (_vic getVariable "waveOff") exitWith {
		true
	};

	if (!isNil "_doFallback") then {
		private _fallbackTimelimit = 10;
		if (_vic getVariable ["isHeli", false]) then {
			_fallbackTimelimit = 5;
		};
		[_vic, _groupLeader, _fallbackTimeoutDuration, _fallbackTimelimit, _fallbackStationaryThreashold] spawn _checkIfStationary;
	};

	if (_vic getVariable "waveOff") exitWith {
		true
	};

	[_vic, _groupLeader, _goHome, _last_message] call _arriveAtDestination;
};