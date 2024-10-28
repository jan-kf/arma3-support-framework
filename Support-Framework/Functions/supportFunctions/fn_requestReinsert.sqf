params ["_vic", "_location"];
// vic was told to begin it's mission, perform startup

private _currentTask = _vic getVariable ["currentTask", "waiting"];
private _isLoitering = _currentTask == "loiter";

private _locationData = [_location] call YOSHI_fnc_getLocation;
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
private _fullRun = _vic getVariable ["fullRun", true];

if (isNil "_groupLeader") exitWith {
	[driver _vic, "No group leader was assigned, Staying Put."] call YOSHI_fnc_sendSideText;
	_vic setVariable ["currentTask", "waiting", true];
	_vic setVariable ["isPerformingDuties", false, true];
};

private _groupLeaderGroup = group _groupLeader;
private _groupLeaderCallsign = groupId _groupLeaderGroup;

if (!_straightFromTop || !_isLoitering) then {
	if (isNil "_locationPOS") then {
		private _locationPOS = [_vic, _groupLeader, true] call YOSHI_fnc_findRendezvousPoint;
		private _gl_message = "%3, this is %1, requesting redeployment from %2, over";
		if (!_fullRun) then{
			_gl_message = "%3, this is %1, requesting %2 on my position, over";
		};
		[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, _baseName]] call YOSHI_fnc_sendSideText;
	}else{
		private _gl_message = "%4, this is %1, requesting %2 at %3, over";
		[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, _locationName, _baseName]] call YOSHI_fnc_sendSideText;
	};
	[_groupLeader, "YOSHI_TransportRequested"] call YOSHI_fnc_playSideRadio;
	sleep 3;
};




if (isNil "_locationPOS") exitWith {
	if (!_straightFromTop) then {
		if (_vic getVariable ["isHeli", false]) then {
			[_baseCallsign, format ["%1, we have no available LZ for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] call YOSHI_fnc_sendSideText;
		} else {
			[_baseCallsign, format ["%1, we have no available RP for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] call YOSHI_fnc_sendSideText;
		};
		sleep 3;
	};
	_vic setVariable ["currentTask", "waiting", true];
	_vic setVariable ["isPerformingDuties", false, true];
};


if (!_straightFromTop || !_isLoitering) then {
	private _base_message = "Roger %1, beginning redeployment, out.";
	if (!_fullRun) then{
		_base_message = "Roger %1, dispatching %2, out.";
	};
	[_baseCallsign, format [_base_message, _groupLeaderCallsign, groupId group _vic]] call YOSHI_fnc_sendSideText;
	sleep 3;
};


_vic setVariable ["destination", _locationPOS, true];
	
private _currentPos = getPosATL _vic;

// logic to check if Vic is already at location
if (_vic distance2D _locationPOS < 100) exitWith {
	[_vic] call YOSHI_fnc_removeVehicleFromPadRegistry;
	[driver _vic, "Already at location, wait one..."] call YOSHI_fnc_sendSideText;
	if (_fullRun) then {
		_vic setVariable ["currentTask", "requestBaseLZ", true];
	} else {
		_vic setVariable ["currentTask", "waiting", true];
	};
};

// set waypoint
[_vic, _locationPOS] call YOSHI_fnc_setWaypoint;

private _gridRef = [_locationPOS] call YOSHI_fnc_posToGrid;
if (!_isLoitering) then {
	if ([_vic] call YOSHI_fnc_hasLanded) then {
		// get gridRef if message has format specifier.
		// msg that driver sends once destination grid is recieved 
		private _base_to_vic_msg = "Over to you %1, you are cleared for departure to %2, over.";
		if (_straightFromTop) then {
			_base_to_vic_msg = "%1, you are cleared for departure to %2, over.";
		};
		[_baseCallsign, format [_base_to_vic_msg, groupId group _vic, _gridRef]] call YOSHI_fnc_sendSideText;
		sleep 3;
		[driver _vic, format ["Cleared for departure to %1, %2 out.", _gridRef, groupId group _vic]] call YOSHI_fnc_sendSideText;
	}else{
		private _base_to_vic_msg = "Over to you %1, you are cleared for approach to %2, over.";
		if (_straightFromTop) then {
			_base_to_vic_msg = "%1, you are cleared for approach to %2, over.";
		};
		[_baseCallsign, format [_base_to_vic_msg, groupId group _vic, _gridRef]] call YOSHI_fnc_sendSideText;
		sleep 3;
		[driver _vic, format ["Cleared for approach to %1, %2 out.", _gridRef, groupId group _vic]] call YOSHI_fnc_sendSideText;
	};
	sleep 1;
	[_vic, format ["Tasking received, heading out to %1.", _gridRef]] call YOSHI_fnc_vehicleChatter;
	[_vic, "YOSHI_TransportTaskRecieved"] call YOSHI_fnc_playVehicleRadio;
} else {
	private _gl_message = "%2, this is %1, proceed to %3, over";
	[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, _locationName]] call YOSHI_fnc_sendSideText;
};

// vic is leaving base, release base pad reservation
[_vic] call YOSHI_fnc_removeVehicleFromPadRegistry;
// cancel request
_vic setVariable ["requestingRedeploy", false, true];
// once vic is underway, set it's task to onMission
_vic setVariable ["currentTask", "onMission", true];