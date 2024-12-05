YOSHI_reconDetectionRange = 1000;

YOSHI_lastScanTime = 0;
publicVariable "YOSHI_lastScanTime";

YOSHI_CanSee = {
	params [
		["_looker",objNull,[objNull]],
		["_target",objNull,[objNull]]
	];

	_blockers = lineIntersectsSurfaces [
				getPosASL _looker, 
				(getPosASL _target) vectorAdd [0,0,0.2], 
				_target, 
				_looker, 
				true, 
				1,
				"GEOM",
				"FIRE"
			];
	
	if (
		count (_blockers) > 0
		) exitWith {false};
	true

};

YOSHI_GetReadableName = { 
	params ["_className"];
 
    private _config = configFile >> "CfgVehicles" >> _className; 
    private _displayName = getText(_config >> "displayName");
	 
    _displayName 
};


// maybe don't store the markers, instead add them to an array for deletion?
YOSHI_addReconMarker = {
	params ["_target", "_text", "_color", "_type"];

	_id = netId _target;

	_targetPos = getPosASL _target;
	_targetPos resize 2;

	if (_id in YOSHI_ReconMarkersMap) then {
		
		_data = YOSHI_ReconMarkersMap get _id;
		_prevMarker = _data select 0;
		_trail = _data select 1;
		_locations = _data select 2;
		
		hint _prevMarker;
		_markerLoc = getMarkerPos _prevMarker;
		deleteMarker _prevMarker;

		_marker = [_target, _text, _color, _type] call YOSHI_addMarker;

		_deltaDistance = _marker distance2D _target;

		if (_deltaDistance < 3) then {
			_locations = [];
			_trail setMarkerAlpha 0; 
		};

		_locations pushBack _targetPos;
		_locCount = count _locations;

		if (_locCount > 5) then {
			_locations deleteAt 0;
		};

		if (_locCount > 1) then {
			_positions = [];
			{
				_positions pushBack (_x select 0);
				_positions pushBack (_x select 1);
			} forEach _locations;

			if (count _positions >= 4 && count _positions mod 2 == 0) then {
				_trail setMarkerPolyline _positions;
				_trail setMarkerAlpha 0.75;
			};
		};
		
		YOSHI_ReconMarkersMap set [_id, [_marker, _trail, _locations, serverTime]];

	} else {
		_marker = [_target, _text, _color, _type] call YOSHI_addMarker;
		_markerTrail = [_target, _text, _color, _type] call YOSHI_addMarker;
		_markerTrail setMarkerAlpha 0;
		_targetPos = getPosASL _target;
		_targetPos resize 2;
		YOSHI_ReconMarkersMap set [_id, [_marker, _markerTrail, [_targetPos], serverTime]];
	};

	publicVariable "YOSHI_ReconMarkersMap";
};

YOSHI_getDeadKeys = {
    params ["_hashmap"];
    
    private _allKeys = keys _hashmap;
    private _keysToRemove = [];
	{
		_obj = objectFromNetId _x;

		if (!(alive _obj)) then {
			_keysToRemove pushBack _x;
		};
	} forEach _allKeys;
    
    _keysToRemove
};

YOSHI_removeMarker = {
    params ["_hashmap", "_key"];
    
    if (_key in YOSHI_ReconMarkersMap) then {
		_entry = YOSHI_ReconMarkersMap get _key;
		_marker = _entry select 0;
		_trail = _entry select 0;

		deleteMarker _marker;
		deleteMarker _trail;
	};

	YOSHI_ReconMarkersMap deleteAt _key;
	publicVariable "YOSHI_ReconMarkersMap";
};

YOSHI_PerformReconScan = {
	params ["_uav", "_detectionRange", ["_showNames", false], ["_hasHyperSpectralSensors", false]];

	YOSHI_lastScanTime = serverTime;
	publicVariable "YOSHI_lastScanTime";

	_all_units = _uav nearEntities [["Man", "AllVehicles"], _detectionRange];
	_filteredTargets = [];
	{
		if (_hasHyperSpectralSensors || ([_uav, _x, 360] call YOSHI_CanSee)) then {
			_filteredTargets pushBack _x;
		};
	} forEach _all_units;

	[_uav, _filteredTargets, _showNames] spawn {
		params ["_uav", "_filteredTargets", "_showNames"];
		[_uav, ["droneScan", 300, 1]] remoteExec ["say3D"];
		sleep 1.5;
		{
			_target = _x;
			_side = side _x;
			
			_type = "mil_dot";
			if (_target isKindOf "Car") then {
				_type = "loc_car";
			};
			if (_target isKindOf "Plane") then {
				_type = "loc_plane";
			};
			if (_target isKindOf "Ship") then {
				_type = "loc_boat";
			};
			if (_target isKindOf "Helicopter") then {
				_type = "loc_heli";
			};


			_color = "ColorUNKNOWN";
			if (_side == west) then {_color = "ColorWEST"}; 
			if (_side == east) then {_color = "ColorEAST"}; 
			if (_side == resistance) then {_color = "ColorGUER"}; 
			if (_side == civilian) then {_color = "ColorCIV"};
			if (_target == _uav) then {_color = "ColorBlack"};

			_text = "";
			// if (_showNames) then {
			// 	_text = [typeOf _target] call YOSHI_GetReadableName;
			// };
			
			[_target, _text, _color, _type] call YOSHI_addReconMarker;
			sleep 0.1;

		} forEach _filteredTargets;
	};

	//// old code that might not be necessary if the baseHeartbeat does it's job:
	// _all_units_keys = [];
	// {_all_units_keys pushBack (netId _x)} forEach _all_units;

	_keys_to_remove = [YOSHI_ReconMarkersMap] call YOSHI_getDeadKeys;

	{[YOSHI_ReconMarkersMap, _x] call YOSHI_removeMarker} forEach _keys_to_remove;

};