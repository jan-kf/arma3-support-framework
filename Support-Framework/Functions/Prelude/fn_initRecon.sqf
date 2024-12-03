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


YOSHI_addReconMarker = {
	params ["_target", "_text", "_color"];

	_id = netId _target;
	

	if (_id in YOSHI_ReconMarkersMap) then {
		
		_locations = YOSHI_ReconMarkersMap get _id;
		_locCount = count _locations;

		_shouldUpdateLocation = true;

		if (_locCount > 0) then {
			_lastLocation = _locations select (_locCount - 1);
			
			if (!(isNil "_lastMarker")) then {
				_lastMarker = _lastLocation select 1;
				_markerLoc = getMarkerPos _lastMarker;

				_deltaDistance = _markerLoc distance2D _target;

				if (_deltaDistance < 3) then {
					_shouldUpdateLocation = false; 
				};
			};
		};


		if (_locCount > 5) then {
			_location = _locations select 0;
			if (!(isNil "_location")) then {
				_staleMarker = _location select 1;
				deleteMarker _staleMarker;

				_locations deleteAt 0;
			};
		};

		if (_shouldUpdateLocation) then {
			_marker = [_target, _text, _color] call YOSHI_addMarker;
			_locations pushBack [_target, _marker];
			YOSHI_ReconMarkersMap set [_id, _locations];

			if (_locCount > 1) then {
				_markerPositions = [];
				{
					if (!(isNil "_x")) then {
						_markerToUpdate = _x select 1;
						_markerToUpdate setMarkerAlpha 0;
						_currentMarkerPos = getMarkerPos _markerToUpdate;
						_markerPositions pushBack (_currentMarkerPos select 0);
						_markerPositions pushBack (_currentMarkerPos select 1);
					};
				} forEach _locations;
				_marker setMarkerAlpha 1;

				_lastMarker = (_locations select 0) select 1;
				if (count _markerPositions >= 4 && count _markerPositions mod 2 == 0) then {
					_lastMarker setMarkerPolyline _markerPositions;
					_lastMarker setMarkerAlpha 0.75;
				};
			};
		} else {
			YOSHI_ReconMarkersMap set [_id, [_locations select (_locCount - 1)]];
		};

	} else {
		_marker = [_target, _text, _color] call YOSHI_addMarker;
		YOSHI_ReconMarkersMap set [_id, [[_target, _marker]]];
	};

	publicVariable "YOSHI_ReconMarkersMap";

};

YOSHI_getKeysNotInArray = {
    params ["_hashmap", "_keyArray"];
    
    private _allKeys = keys _hashmap;
    
    private _keysToRemove = _allKeys - _keyArray;

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
		{
			_marker = _x select 1;
			deleteMarker _marker;
		} forEach _entry;
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
		[_uav, ["droneScan", 500, 1]] remoteExec ["say3D"];
		sleep 1.5;
		{
			_target = _x;
			_type = typeOf _target;
			_side = side _x;

			_color = "ColorUNKNOWN";
			if (_side == west) then {_color = "ColorWEST"}; 
			if (_side == east) then {_color = "ColorEAST"}; 
			if (_side == resistance) then {_color = "ColorGUER"}; 
			if (_side == civilian) then {_color = "ColorCIV"};

			_text = "";
			if (_showNames) then {
				_text = [_type] call YOSHI_GetReadableName;
			};
			
			[_target, _text, _color] call YOSHI_addReconMarker;
			sleep 0.1;

		} forEach _filteredTargets;
	};

	_all_units_keys = [];
	{_all_units_keys pushBack (netId _x)} forEach _all_units;

	_keys_to_remove = [YOSHI_ReconMarkersMap, _all_units_keys] call YOSHI_getKeysNotInArray;

	{[YOSHI_ReconMarkersMap, _x] call YOSHI_removeMarker} forEach _keys_to_remove;

};