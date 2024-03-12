params ["_vic", "_baseCallsign", "_baseName", "_baseIsNotVirtual"];
// vic was told to begin it's mission, perform startup
// clear out params:
_vic setVariable ["waveOff", false, true];
_vic setVariable ["destination", nil, true];

_vic setVariable ["isPerformingDuties", true, true];

private _groupLeader = _vic getVariable "targetGroupLeader";
private _straightFromTop =  false;
if (_baseIsNotVirtual && (typeName _baseCallsign != "ARRAY")) then{
	if (_groupLeader == _baseCallsign) then {
		_straightFromTop = true;
	}
};
private _fullRun = _vic getVariable ["fullRun", true];

if (isNil "_groupLeader") exitWith {
	[driver _vic, "No group leader was assigned, Staying Put."] call SupportFramework_fnc_sideChatter;
	_vic setVariable ["currentTask", "waiting", true];
	_vic setVariable ["isPerformingDuties", false, true];
};

private _groupLeaderGroup = group _groupLeader;
private _groupLeaderCallsign = groupId _groupLeaderGroup;

private _location = _vic getVariable "targetLocation";
if (!_straightFromTop) then {
	if (isNil "_location") then {
		private _location = [_vic, _groupLeader, true] call SupportFramework_fnc_findRendezvousPoint;
		private _gl_message = "%3, this is %1, requesting redeployment from %2, over";
		if (!_fullRun) then{
			_gl_message = "%3, this is %1, requesting %2 on my position, over";
		};
		[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, _baseName]] call SupportFramework_fnc_sideChatter;
	}else{
		private _gl_message = "%4, this is %1, requesting %2 at %3, over";
		[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, markerText _location, _baseName]] call SupportFramework_fnc_sideChatter;
	};
	sleep 3;
};




if (isNil "_location") exitWith {
	if (!_straightFromTop) then {
		if (_vic getVariable ["isHeli", false]) then {
			[_baseCallsign, format ["%1, we have no available LZ for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] call SupportFramework_fnc_sideChatter;
		} else {
			[_baseCallsign, format ["%1, we have no available RP for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] call SupportFramework_fnc_sideChatter;
		};
		sleep 3;
	};
	_vic setVariable ["currentTask", "waiting", true];
	_vic setVariable ["isPerformingDuties", false, true];
};


if (!_straightFromTop) then {
	private _base_message = "Roger %1, beginning redeployment, out.";
	if (!_fullRun) then{
		_base_message = "Roger %1, dispatching %2, out.";
	};
	[_baseCallsign, format [_base_message, _groupLeaderCallsign, groupId group _vic]] call SupportFramework_fnc_sideChatter;
	sleep 3;
};

private _destinationPos = nil;
if (typeName _location == "STRING") then {
	// _location is a string
	_destinationPos = getMarkerPos _location;
} else {
	if (typeName _location == "OBJECT") then {
		// _location is an object
		_destinationPos = getPos _location;
	};
};

_vic setVariable ["destination", _location, true];
	
private _currentPos = getPos _vic;

// logic to check if Vic is already at location
if (_vic distance2D _destinationPos < 100) exitWith {
	[_vic] call SupportFramework_fnc_removeVehicleFromPadRegistry;
	[driver _vic, "Already at location, wait one..."] call SupportFramework_fnc_sideChatter;
	if (_fullRun) then {
		_vic setVariable ["currentTask", "requestBaseLZ", true];
	} else {
		_vic setVariable ["currentTask", "waiting", true];
	};
};

// set waypoint
private _grp = group _vic;
private _base_wp = _grp addWaypoint [_destinationPos, 0];
_base_wp setWaypointType "MOVE";
_grp setCurrentWaypoint _base_wp;

private _gridRef = [_destinationPos] call SupportFramework_fnc_posToGrid;
if ((isTouchingGround _vic) && (speed _vic < 1)) then {
	// get gridRef if message has format specifier.
	// msg that driver sends once destination grid is recieved 
	private _base_to_vic_msg = "Over to you %1, you are cleared for departure to %2, over.";
	if (_straightFromTop) then {
		_base_to_vic_msg = "%1, you are cleared for departure to %2, over.";
	};
	[_baseCallsign, format [_base_to_vic_msg, groupId group _vic, _gridRef]] call SupportFramework_fnc_sideChatter;
	sleep 3;
	[driver _vic, format ["Cleared for departure to %1, %2 out.", _gridRef, groupId group _vic]] call SupportFramework_fnc_sideChatter;
}else{
	private _base_to_vic_msg = "Over to you %1, you are cleared for approach to %2, over.";
	if (_straightFromTop) then {
		_base_to_vic_msg = "%1, you are cleared for approach to %2, over.";
	};
	[_baseCallsign, format [_base_to_vic_msg, groupId group _vic, _gridRef]] call SupportFramework_fnc_sideChatter;
	sleep 3;
	[driver _vic, format ["Cleared for approach to %1, %2 out.", _gridRef, groupId group _vic]] call SupportFramework_fnc_sideChatter;
};

// vic is leaving base, release base pad reservation
[_vic] call SupportFramework_fnc_removeVehicleFromPadRegistry;
// cancel request
_vic setVariable ["requestingRedeploy", false, true];
// once vic is underway, set it's task to onMission
_vic setVariable ["currentTask", "onMission", true];