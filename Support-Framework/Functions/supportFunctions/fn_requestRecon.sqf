params ["_vic", "_location"];
// vic was told to begin it's cas mission, perform startup

private _locationData = [_location, false] call YOSHI_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

private _baseParams = call YOSHI_fnc_getBaseCallsign;
private _baseCallsign = _baseParams select 0;
private _baseName = _baseParams select 1;
private _baseIsNotVirtual = _baseParams select 2;

// clear out params:
_vic setVariable ["destination", nil, true];

_vic setVariable ["isPerformingDuties", true, true];

private _groupLeader = _vic getVariable "targetGroupLeader";
private _straightFromTop =  false;
if (_baseIsNotVirtual && (typeName _baseCallsign != "ARRAY")) then{
	if (_groupLeader == _baseCallsign) then {
		_straightFromTop = true;
	}
};

if (isNil "_groupLeader") exitWith {
	[driver _vic, "No group leader was assigned, Staying Put."] call YOSHI_fnc_sideChatter;
	_vic setVariable ["currentTask", "waiting", true];
	_vic setVariable ["isPerformingDuties", false, true];
};

private _groupLeaderGroup = group _groupLeader;
private _groupLeaderCallsign = groupId _groupLeaderGroup;

_vic setVariable ["destination", _locationPOS, true];
	
private _currentPos = getPos _vic;

// set waypoint
private _grp = group _vic;
private _base_wp = _grp addWaypoint [_locationPOS, 0];
_base_wp setWaypointType "LOITER";
_grp setCurrentWaypoint _base_wp;

private _gridRef = [_locationPOS] call YOSHI_fnc_posToGrid;


if (!_straightFromTop) then {
	private _gl_message = "%3, this is %1, requesting recon mission from %2 at %4, over";
	[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, _baseName, _gridRef]] call YOSHI_fnc_sideChatter;
	sleep 3;
};

if (!_straightFromTop) then {
	_base_message = "Roger %1, dispatching %2, out.";
	[_baseCallsign, format [_base_message, _groupLeaderCallsign, groupId group _vic]] call YOSHI_fnc_sideChatter;
	sleep 3;
};


if ((isTouchingGround _vic) && (speed _vic < 1)) then {
	// get gridRef if message has format specifier.
	// msg that driver sends once destination grid is recieved 
	private _base_to_vic_msg = "Over to you %1, you are cleared for departure to %2, over.";
	if (_straightFromTop) then {
		_base_to_vic_msg = "%1, you are cleared for departure to %2. Mission objective: Recon Area, over.";
	};
	[_baseCallsign, format [_base_to_vic_msg, groupId group _vic, _gridRef]] call YOSHI_fnc_sideChatter;
	sleep 3;
	[driver _vic, format ["Cleared for reconnaissance to %1, %2 out.", _gridRef, groupId group _vic]] call YOSHI_fnc_sideChatter;
}else{
	private _base_to_vic_msg = "Over to you %1, you are cleared for approach to %2, over.";
	if (_straightFromTop) then {
		_base_to_vic_msg = "%1, you are cleared for approach to %2. Mission objective: Recon Area, over.";
	};
	[_baseCallsign, format [_base_to_vic_msg, groupId group _vic, _gridRef]] call YOSHI_fnc_sideChatter;
	sleep 3;
	[driver _vic, format ["Cleared for reconnaissance at %1, %2 out.", _gridRef, groupId group _vic]] call YOSHI_fnc_sideChatter;
};

// vic is leaving base, release base pad reservation
[_vic] call YOSHI_fnc_removeVehicleFromPadRegistry;
// cancel request
_vic setVariable ["requestingRedeploy", false, true];
// once vic is underway, set it's task to onMission
_vic setVariable ["currentTask", "onMission", true];