if (!isServer) exitWith {};

diag_log "[SUPPORT] initHomeBase is beginning initilization...";

execVM "\Support-Framework\Functions\Client\counterBatteryRadar.sqf";

///////////////////////////////////////////////////

private _worldSize = worldSize;
private _center = [_worldSize / 2, _worldSize / 2, 0];
private _radius = _center distance [0, 0, 0];

{ 
    if (_x isKindOf "HeliH") then { 
        YOSHI_HELIPAD_INDEX pushBack _x; 
    }; 
} forEach (nearestTerrainObjects [_center, [], _radius]);

//////////////////////////////////////////////////

{
    [_x] call YOSHI_fnc_setObjectLoadHandling;
} forEach entities "ReammoBox_F";

{
	_x addEventHandler ["Engine", {
		params ["_vehicle", "_engineState"];
		if (_engineState) then {detach _vehicle} else {_vehicle call YOSHI_attachToBelow};
	}];
	[_x, true, [0,1,0]] call ace_dragging_fnc_setDraggable;
    [_x, true] call ace_dragging_fnc_setCarryable;
} forEach entities "UAV_01_base_F";

//// //// /////////////////////////////////////

{
    _x setFuelConsumptionCoef 0.1;
} forEach allMissionObjects "UAV_01_base_F";


// {
// 	_thread = [_x] spawn YOSHI_detectRockets;

// 	_x setVariable ["YOSHI_APS_Thread", _thread];

// } forEach allMissionObjects "B_UGV_9RIFLES_F";

///////////////////////////////////////////



// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[SUPPORT] kicking off heartbeat...";
// ["[SUPPORT] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn YOSHI_fnc_baseHeartbeat;

diag_log "[SUPPORT] initHomeBase is done initializing";
// ["[SUPPORT] initHomeBase is done initializing"] remoteExec ["systemChat"];