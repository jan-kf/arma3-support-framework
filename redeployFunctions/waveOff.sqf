#include "goToLocation.sqf"

// Get the vic
private _vic = _this select 0;

_vic setVariable ["waveOff", true, true];

private _group = group _vic;  // Replace 'myUnit' with your unit's variable name
for "_i" from (count waypoints _group - 1) to 0 step -1 do
{
	deleteWaypoint [_group, _i];
};

[_vic, bull, true, false, "Waving off, Returning to Base at: %1", "Ready for tasking..."] call _goToLocation;

_vic engineOn false;
_vic setVariable ["performedReinsert", false, true];
_vic setVariable ["isReinserting", false, true];
_vic setVariable ["fallbackTriggered", false, true];
_vic setVariable ["waveOff", false, true];
