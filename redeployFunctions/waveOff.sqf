#include "goToLocation.sqf"

// Get the vic
private _vic = _this select 0;

// set waveOff to true to stop previous commands
private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

_vicStatus set ["waveOff", true];

// cancel reinsertion, reset request for redeploy
_vicStatus set ["isReinserting", false];
_vicStatus set ["requestingRedeploy", false];

// delete waypoints
private _group = group _vic;  
for "_i" from (count waypoints _group - 1) to 0 step -1 do
{
	deleteWaypoint [_group, _i];
};


// make sure that the vic releases it's parking pass during a wave off
private _activeAwayPads = home_base getVariable "homeBaseManifest" get "activeAwayPads";
private _parkingPassToReturn = _vicStatus get "awayParkingPass";

if (!isNil "_parkingPassToReturn") then {
	private _index = _activeAwayPads find _parkingPassToReturn;
	if (_index != -1) then {
		// Remove the element
		_activeAwayPads deleteAt _index;
	};
};

// have vic RTB
[_vic, home_base, true, false, true, "Waving off, Returning to Base at: %1", "Ready for tasking..."] call _goToLocation;

sleep 20;

if (!isTouchingGround _vic) then {
	// waveOff was likely called while the vic was taking off, re-waveOff after a few seconds:
	sleep 10;
	[_vic, home_base, true, false, true, "Waving off, Returning to Base at: %1", "Ready for tasking..."] call _goToLocation;
};

[driver _vic, "Ready for tasking..."] remoteExec ["sideChat"];
_vic engineOn false;
// reset State
_vicStatus set ["performedReinsert", false];
_vicStatus set ["isReinserting", false];

_vicStatus set ["waveOff", false];
