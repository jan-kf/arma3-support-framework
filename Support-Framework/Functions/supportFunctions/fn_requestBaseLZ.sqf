params ["_vic"];

private _baseParams = call YOSHI_fnc_getBaseCallsign;
private _baseCallsign = _baseParams select 0;
private _baseName = _baseParams select 1;

// vic attempts to kickstart it's RTB procedures
[_vic] call YOSHI_fnc_removeVehicleFromAwayPads;

[driver _vic, format ["%2, this is %1, requesting permission to land, over", groupId group _vic, _baseName]] call YOSHI_fnc_sideChatter;
sleep 3;
_location = [_vic, YOSHI_HOME_BASE_CONFIG, true, true] call YOSHI_fnc_findRendezvousPoint;
if (isNil "_location") exitWith {
	if (_vic getVariable ["isHeli", false]) then {
		[_baseCallsign, format ["%1, No helipad is available at the moment, over.", groupId group _vic]] call YOSHI_fnc_sideChatter;
	} else {
		[_baseCallsign, format ["%1, No parking is available at the moment, over.", groupId group _vic]] call YOSHI_fnc_sideChatter;
	};
	sleep 3;
	[driver _vic, format ["Roger that %2, will check in again later. %1 out.", groupId group _vic, _baseName]] call YOSHI_fnc_sideChatter;
	[_vic] call YOSHI_fnc_removeVehicleFromPadRegistry;
	// what should it's status be?
	_vic setVariable ["currentTask", "marooned", true];
};
_vic setVariable ["destination", _location, true];
_destinationPos = getPos _location; 
_currentPos = getPos _vic;

// logic to check if Vic is already at location
if ((_vic distance2D _destinationPos < 100) && (isTouchingGround _vic) && (speed _vic < 1)) exitWith {
	[driver _vic, "Already at base..."] call YOSHI_fnc_sideChatter;
	_vic setVariable ["currentTask", "waiting", true];
};

private _group = group _vic;
// delete current waypoints 
for "_i" from (count waypoints _group - 1) to 0 step -1 do
{
	deleteWaypoint [_group, _i];
};

// set waypoint
private _grp = group _vic;
private _base_wp = _grp addWaypoint [_destinationPos, 0];
_base_wp setWaypointType "MOVE";
_grp setCurrentWaypoint _base_wp;

if (!isNil "_dustOffMessage") then {
	// get gridRef if message has format specifier.
	private _gridRef = [_destinationPos] call YOSHI_fnc_posToGrid;
	// msg that driver sends once destination grid is recieved 
	[_baseCallsign, format ["%1, you are cleared to land at landing pad at %2, over.", groupId group _vic, _gridRef]] call YOSHI_fnc_sideChatter;
	sleep 3;
	[driver _vic, format ["Cleared for pad at %1, %2 out.", _gridRef, groupId group _vic]] call YOSHI_fnc_sideChatter;
};

// once complete, set task to RTB
_vic setVariable ["currentTask", "RTB", true];