#include "goToLocation.sqf"

// Get the vic
private _vic = _this select 0;

// set waveOff to true to stop previous commands
_vic setVariable ["waveOff", true, true];

// cancel reinsertion, reset request for redeploy
_vic setVariable ["isReinserting", false, true];
_vic setVariable ["requestingRedeploy", false, true];

// delete waypoints
private _group = group _vic;  
for "_i" from (count waypoints _group - 1) to 0 step -1 do
{
	deleteWaypoint [_group, _i];
};

// have vic RTB
[_vic, home_base, true, false, "Waving off, Returning to Base at: %1", "Ready for tasking...", true] call _goToLocation;

_vic engineOn false;
// reset State
_vic setVariable ["performedReinsert", false, true];
_vic setVariable ["isReinserting", false, true];
_vic setVariable ["fallbackTriggered", false, true];
_vic setVariable ["waveOff", false, true];
