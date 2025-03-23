_myFunction = {
    params ["_bl_corner", ["_granularity", 1000]];

    _halfSize = _granularity / 2;
    _offsetDelta = (_granularity / 100) * 2;

    _markerName = format ["_USER_DEFINED corner %1", random 10000000];
    _marker = createMarkerLocal [_markerName, _bl_corner];
    _marker setMarkerShapeLocal "ICON";
    _marker setMarkerTypeLocal "mil_dot";
    _marker setMarkerColor "ColorBlack"; 
    _marker setMarkerShadow false;
    globalMarkersArray pushBack _marker;

    _center = [(_bl_corner select 0)+_halfSize,(_bl_corner select 1)+_halfSize, 0];

    _isWater = surfaceIsWater _center;

    private _filteredArray = [];

    if (_isWater) then {
        _markerName = format ["_USER_DEFINED isWater %1", random 10000000];
        _marker = createMarkerLocal [_markerName, (_bl_corner vectorAdd [_offsetDelta, _offsetDelta, 0])];
        _marker setMarkerShapeLocal "ICON";
        _marker setMarkerTypeLocal "mil_dot";
        _marker setMarkerColor "ColorBlue"; 
        _marker setMarkerShadow false;
        _marker setMarkerTextLocal "IsWater";
        globalMarkersArray pushBack _marker;
    } else {
        _resourceTypes = createHashMapFromArray [
            ["Wood", ["TREE", "SMALL TREE"]],
            ["Stone", ["ROCK", "ROCKS"]], 
            ["Energy", ["POWERSOLAR", "POWERWIND", "POWERWAVE", "TRANSMITTER"]], 
            ["Fuel", ["FUELSTATION"]], 
            ["Manpower", ["HOUSE"]],
            ["Water", ["WATERTOWER", "FOUNTAIN"]],
            ["Maneuver", ["MAIN ROAD", "ROAD"]],
            ["Faith", ["CHURCH", "CHAPEL"]] 
        ];

        _resourceColors = createHashMapFromArray [
            ["Wood", "ColorGreen"],
            ["Stone", "ColorGrey"], 
            ["Energy", "ColorYellow"], 
            ["Fuel", "ColorRed"], 
            ["Manpower", "ColorCIV"],
            ["Water", "ColorBlue"],
            ["Maneuver", "ColorOrange"],
            ["Faith", "ColorWhite"]
        ];

        
        private _offset = _offsetDelta;

        {
            private _type = _x;
            private _objects = _y;
            private _nearestObjects = nearestTerrainObjects [_center, _objects, (_halfSize * 1.5)];
            private _filteredArray = _nearestObjects inAreaArray [_center, _halfSize, _halfSize, 0, true];

            if ((count _filteredArray) > 0 ) then {
                _markerName = format ["_USER_DEFINED %1 %2", _type, random 10000000];
                _marker = createMarkerLocal [_markerName, (_bl_corner vectorAdd [_offsetDelta, _offset, 0])];
                _marker setMarkerShapeLocal "ICON";
                _marker setMarkerTypeLocal "mil_dot";
                _marker setMarkerColor (_resourceColors get _type); 
                _marker setMarkerShadow false;
                _marker setMarkerTextLocal format ["%1: %2", _type, count _filteredArray];
                globalMarkersArray pushBack _marker;
                _offset = _offset + _offsetDelta; 
            };
            
        } forEach _resourceTypes;
    };
};

globalMarkersArray apply {deleteMarker _x};
globalMarkersArray = [];
globalPowerlinesArray = [];

_mapSize = worldSize;

_granularity = 100;

_numGrids = ceil (_mapSize / _granularity); 

for "_x" from 0 to _numGrids - 1 do {
    for "_y" from 0 to _numGrids - 1 do {
        _gridCoord = [_x * _granularity, _y * _granularity];
        [_gridCoord, _granularity] spawn _myFunction;
    };
};
