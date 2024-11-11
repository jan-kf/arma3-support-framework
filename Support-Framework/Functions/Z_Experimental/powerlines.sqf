_myFunction = {
    params ["_bl_corner"];

    _center = [(_bl_corner select 0)+500,(_bl_corner select 1)+500, 0];

    _objectsArray = nearestTerrainObjects [_center, ["Building", "Power Lines", "Hide", "Transmitter", "Powersolar", "Powerwind", "Powerwave"], 750]; 
    _objectsArray append (nearestObjects [_center, [], 750]);
    _filteredArray = _objectsArray inAreaArray [_center, 500, 500, 0, true];
    { 
        _obj = _x;
        _markerPos = getPosATL _obj; 
        _marked = false;

        _lightStat = (lightIsOn _obj);
        
        
        if (_obj isKindOf "Lamps_base_F" ) then { 
			globalPowerlinesArray pushBack _obj;
            _markerName = format ["_USER_DEFINED RedMarker_%1", _obj]; 
        
            _marker = createMarkerLocal [_markerName, _obj]; 
            _marker setMarkerShapeLocal "ICON";
            _marker setMarkerTypeLocal "mil_dot";
            _marker setMarkerColor "ColorRed"; 
            _marker setMarkerShadow false;
            globalMarkersArray pushBack _marker;
            _marked = true; 
        };  
        if (!_marked) then { 
            _model = getModelInfo _obj;
            _modelPath = _model select 1;
            if ((_modelPath find "vegeta" >= 0) || (_modelPath find "camp" >= 0)) then {
                _marked = true;
            };
            if (!_marked && _modelPath find "power" >= 0) then {
                if (!_marked && ((_modelPath find "pole" >= 0) || (_modelPath find "con" >= 0) || (_modelPath find "wood" >= 0))) then {
                    globalPowerlinesArray pushBack _obj;
                    _markerName = format ["_USER_DEFINED GreenMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorGreen";
                    _marker setMarkerShadow false;  
                    globalMarkersArray pushBack _marker;
                    _marked = true; 
                };
            };
            if (!_marked && (_modelPath find "amplion" >= 0)) then {
				globalPowerlinesArray pushBack _obj;
                _markerName = format ["_USER_DEFINED GreenMarker_%1", _obj];
                _marker = createMarkerLocal [_markerName, _obj]; 
                _marker setMarkerShapeLocal "ICON"; 
                _marker setMarkerTypeLocal "mil_dot";  
                _marker setMarkerColor "ColorGUER";  
                _marker setMarkerShadow false;
                globalMarkersArray pushBack _marker;
                _marked = true; 
            };
        }; 
    } forEach _filteredArray; 
    hint str([count _filteredArray, count globalMarkersArray]);
};

globalMarkersArray apply {deleteMarker _x};
globalMarkersArray = [];
globalPowerlinesArray = [];

_mapSize = worldSize;

_numGrids = ceil (_mapSize / 1000); 

for "_x" from 0 to _numGrids - 1 do {
    for "_y" from 0 to _numGrids - 1 do {
        _gridCoord = [_x * 1000, _y * 1000];
        [_gridCoord] spawn _myFunction;
    };
};




/////////////////


// Define a function to establish connections between power poles

// Parameters
// _poles: Array of all pole objects
// _radius: Maximum distance within which poles should connect



private _connectPoles = { 
    params ["_poles", "_radius"]; 
    private _connections = []; 
 
    { 
        private _currentPole = _x; 
        private _eligibleConnections = []; 
 
        { 
            if (_x != _currentPole) then { 
                if ((_x distance _currentPole) <= _radius) then { 
                    _eligibleConnections pushBack _x; 
                }; 
            }; 
        } forEach _poles; 
 
        if (count _eligibleConnections > 0) then { 
            _eligibleConnections sort true; 
 
            { 
                private _closestPole = _x; 
                private _currentConnections = []; 
 
                { 
                    private _pair = _x; 
                    if ((_pair select 0) == _closestPole || (_pair select 1) == _closestPole) then { 
                        _currentConnections pushBack _pair; 
                    }; 
                } forEach _connections; 
 
                if (count _currentConnections < 2) exitWith { 
                    _connections pushBack [_currentPole, _closestPole]; 
 
 
                    _rope = ropeCreate [_currentPole, getPos _currentPole, _closestPole, getPos _closestPole, 20, (_currentPole distance _closestPole)*1.5];
					hint str(_rope);  
                }; 
 
            } forEach _eligibleConnections; 
        }; 
 
    } forEach _poles; 
 
    _connections 
}; 
 

private _poles = globalConeArray; 
private _radius = 50; 
[_poles, _radius] call _connectPoles;
