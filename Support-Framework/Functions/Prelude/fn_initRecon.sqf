YOSHI_reconDetectionRange = 1000;

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
	
	if ((count _blockers) > 0) then {
		hint str([_target, _blockers]);
	};
	
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

YOSHI_addMarkerLite = {
	params ["_obj", ["_text", ""], ["_color", "ColorRed"], ["_type", "mil_dot"], ["_shape", "ICON"]];

	_markerName = format ["_USER_DEFINED YOSHI_MARKER_%1_%2", netId _obj, serverTime];
	_marker = createMarker [_markerName, _obj]; 
	_marker setMarkerShape _shape; 
	_marker setMarkerType _type;  
	_marker setMarkerColor _color;
	_marker setMarkerText _text;
	_marker setMarkerShadow false;  

	_marker
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
			
			_lastMarker = _lastLocation select 1;
			_markerLoc = getMarkerPos _lastMarker;
			_target sideChat str(_markerLoc);

			_deltaDistance = _markerLoc distance2D _target;

			if (_deltaDistance < 3) then {
				_shouldUpdateLocation = false; 
				_target sideChat "My marker is staying put!";
			};
		};


		if (_locCount > 5) then {
			_location = _locations select 0;
			_staleMarker = _location select 1;
			deleteMarker _staleMarker;

			_locations deleteAt 0;
			_target sideChat "I had too many markers!";
		};

		if (_shouldUpdateLocation) then {
			_target sideChat "I'm getting a new marker!";
			_marker = [_target, _text, _color] call YOSHI_addMarkerLite;
			_locations pushBack [_target, _marker];
			YOSHI_ReconMarkersMap set [_id, _locations];

			_markerPositions = [];
			{
				_markerToUpdate = _x select 1;
				_markerToUpdate setMarkerAlpha 0;
				_currentMarkerPos = getMarkerPos _markerToUpdate;
				_markerPositions pushBack (_currentMarkerPos select 0);
				_markerPositions pushBack (_currentMarkerPos select 1);
			} forEach _locations;
			_marker setMarkerAlpha 1;

			if (_locCount > 1) then {
				_lastMarker = (_locations select 0) select 1;
				if (count _markerPositions >= 4 && count _markerPositions mod 2 == 0) then {
					_lastMarker setMarkerPolyline _markerPositions;
					_lastMarker setMarkerAlpha 1;
				};
			};
		} else {
			YOSHI_ReconMarkersMap set [_id, [_locations select (_locCount - 1)]];
		};

	} else {
		_target sideChat "I'm new!";
		_marker = [_target, _text, _color] call YOSHI_addMarkerLite;
		YOSHI_ReconMarkersMap set [_id, [[_target, _marker]]];
	};

};

YOSHI_PerformReconScan = {
	params ["_uav", "_detectionRange", ["_showNames", false], ["_hasHyperSpectralSensors", false]];

	_all_units = _uav nearEntities [["Man", "AllVehicles"], _detectionRange];
	_filteredTargets = [];
	{
		if (_hasHyperSpectralSensors || ([_uav, _x, 360] call YOSHI_CanSee)) then {
			_filteredTargets pushBack _x;
		};
	} forEach _all_units;


	// {
	// 	deleteMarker (_x select 0); // TODO: don't delete, update instead
	// } forEach YOSHI_ReconMarkersArray;

	[_filteredTargets, _showNames] spawn {
		params ["_filteredTargets", "_showNames"];
		{
			_target = _x;
			_type = typeOf _target;
			_side = side _x;

			_color = "ColorUNKNOWN";
			if (_side == west) then {_color = "ColorWEST"}; 
			if (_side == east) then {_color = "ColorEAST"}; 
			if (_side == resistance) then {_color = "ColorGUER"}; 
			if (_side == civilian) then {_color = "ColorCIV"};

			_markerName = format ["_USER_DEFINED marker_%1_%2", _type, round random 1000000];

			_text = "";
			if (_showNames) then {
				_text = [_type] call YOSHI_GetReadableName;
			};
			
			[_target, _text, _color] call YOSHI_addReconMarker;
			// YOSHI_ReconMarkersArray pushBack [_marker, _target];
			// YOSHI_ReconMarkersMap set [netId _target, []]; // TODO
			sleep 0.1;

		} forEach _filteredTargets;
	};
};