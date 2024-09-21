params ["_vic"];

// cancel reinsertion, reset request for redeploy
private _groupLeader = _vic getVariable "targetGroupLeader";

_vic setVariable ["isPerformingDuties", false, true];

private _groupLeader = _vic getVariable "targetGroupLeader";
private _groupLeaderGroup = group _groupLeader;
private _groupLeaderCallsign = groupId _groupLeaderGroup;

_vic land "NONE"; // cancel landing
[_vic, "NONE"] remoteExec ["land"]; 

private _vicGroup = group _vic;
{
	_x disableAI "all";
	_x enableAI "ANIM";
	_x enableAI "MOVE";
	_x enableAI "PATH";
} forEach (units _vicGroup);
_vicGroup setCombatMode "BLUE";
_vicGroup setBehaviourStrong "SAFE";

private _group = group _vic;
// delete waypoints 
for "_i" from (count waypoints _group - 1) to 0 step -1 do
{
	deleteWaypoint [_group, _i];
};
_vic setVariable ["currentTask", "requestBaseLZ", true];

[_groupLeader, format ["%1, this is %2, Wave off, over.",groupId group _vic, _groupLeaderCallsign]] call YOSHI_fnc_sideChatter;
sleep 2;
[driver _vic, format ["Roger that %1, Waving off, out.", _groupLeaderCallsign]] call YOSHI_fnc_sideChatter;
sleep 1;
[_vic, "We are waving off."] call YOSHI_fnc_vehicleChatter;