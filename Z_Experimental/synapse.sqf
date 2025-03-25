YOSHI_isObjectElectric = {
    params ["_obj"];

    _model = getModelInfo _obj;
    _modelPath = _model select 1;
    private _value = 0;
    if ((_modelPath find "vegeta" >= 0) || (_modelPath find "camp" >= 0)) exitWith {
        0;
    };
    if ( ((_modelPath find "trafost" >= 0) || (_modelPath find "transform" >= 0))) then {
        _value = 5;
    };
    if ( _modelPath find "sloup_vn" >= 0) then {
        _value = 2;
    };
    if ( _modelPath find "highvoltage" >= 0) then {
        _value = 2;
    };
    if ( _modelPath find "power" >= 0) then {
        if ( ((_modelPath find "pole" >= 0) || (_modelPath find "con" >= 0) || (_modelPath find "wood" >= 0))) exitWith {
            1;
        };
        if ( _modelPath find "line" >= 0) exitWith {
            1;
        };
        _value = 10;
    };
    _value
};

YOSHI_isObjectSupplies = {
    params ["_obj"];

    _model = getModelInfo _obj;
    _modelPath = _model select 1;
    private _value = 0;
    if ( _modelPath find "cargo" >= 0) then {
        if (_modelPath find "cargo20" >= 0) exitWith {
            random [0, 5, 20]; 
        };
        if ( _modelPath find "cargo40" >= 0) exitWith {
            random [0, 10, 40];
        };
        _value = random [0, 1, 10];
    };
    _value
};

YOSHI_resourceTypes = createHashMapFromArray [
    // ["Wood", ["TREE", "SMALL TREE"]],
    // ["RawEarth", ["ROCK", "ROCKS"]], 
    ["Energy", ["POWERSOLAR", "POWERWIND", "POWERWAVE"]], 
    ["Fuel", ["FUELSTATION"]], 
    ["Manpower", ["HOUSE"]],
    ["Water0", ["WATERTOWER"]],
    ["Water1", ["FOUNTAIN"]],
    ["Maneuver0", ["MAIN ROAD"]],
    ["Maneuver1", ["ROAD"]],
    ["Maneuver2", ["TRACK"]],
    ["Maneuver3", ["TRAIL"]],
    ["Faith0", ["CHURCH"]],
    ["Faith1", ["CHAPEL"]],
    ["Faith2", ["CROSS"]],
    ["Communications", ["TRANSMITTER"]]
];

YOSHI_resourceColors = createHashMapFromArray [
    ["Wood", "ColorGreen"],
    ["RawEarth", "ColorGrey"], 
    ["Energy", "ColorYellow"], 
    ["Fuel", "ColorRed"], 
    ["Manpower", "ColorCIV"],
    ["Water", "ColorBlue"],
    ["Maneuver", "ColorOrange"],
    ["Faith", "ColorWhite"],
    ["Communications", "ColorPink"]
];

YOSHI_resources = createHashMapFromArray [
    ["Wood", 0],
    ["RawEarth", 0], 
    ["Energy", 0], 
    ["Fuel", 0], 
    ["Manpower", 0],
    ["Water", 0],
    ["Maneuver", 0],
    ["Faith", 0],
    ["Communications", 0],
    ["isWater", false]
];

YOSHI_MAP_DATA = createHashMap;

YOSHI_INDEXED_COUNT = 0;

YOSHI_INDEX_CELL = {
    params ["_bl_corner", ["_granularity", 1000]];

    _halfSize = _granularity / 2;
    _offsetDelta = (_granularity / 100) * 2;

    // _markerName = format ["_USER_DEFINED corner %1", random 10000000];
    // _marker = createMarkerLocal [_markerName, _bl_corner];
    // _marker setMarkerShapeLocal "ICON";
    // _marker setMarkerTypeLocal "mil_dot";
    // _marker setMarkerColor "ColorBlack"; 
    // _marker setMarkerShadow false;
    // globalMarkersArray pushBack _marker;

    _center = [(_bl_corner select 0)+_halfSize,(_bl_corner select 1)+_halfSize, 0];

    _isWater = surfaceIsWater _center;

    private _filteredArray = [];

    private _data = +YOSHI_resources;

    if (_isWater) then {
        // _markerName = format ["_USER_DEFINED isWater %1", random 10000000];
        // _marker = createMarkerLocal [_markerName, (_bl_corner vectorAdd [_offsetDelta, _offsetDelta, 0])];
        // _marker setMarkerShapeLocal "ICON";
        // _marker setMarkerTypeLocal "mil_dot";
        // _marker setMarkerColor "ColorBlue"; 
        // _marker setMarkerShadow false;
        // _marker setMarkerTextLocal "IsWater";
        // globalMarkersArray pushBack _marker;

        _data set ["isWater", true];
    } else {
        _data set ["isWater", false];

        private _offset = _offsetDelta;

        {
            private _type = _x;
            private _objects = _y;
            private _nearestObjects = nearestTerrainObjects [_center, _objects, (_halfSize * 1.5)];
            private _filteredArray = _nearestObjects inAreaArray [_center, _halfSize, _halfSize, 0, true];
            private _count = count _filteredArray;
            if (_count > 0 ) then {
                switch (_type) do {
                    // case "Wood": { _count = _count * 10; };
                    // case "RawEarth": { _count = _count * 10; };
                    // case "Energy": { _count = _count * 10; };
                    case "Fuel": { _count = _count * 50; };
                    case "Manpower": {
                        private _energy = 0;
                        private _instances = 0;
                        {
                            private _value = _x call YOSHI_isObjectElectric;
                            if (_value > 0) then {
                                _energy = _energy + _value;
                                _instances = _instances + 1;
                            };
                            private _cargo = ceil (_x call YOSHI_isObjectSupplies);
                            if (_cargo > 0) then {
                                _randomType = selectRandom ["Fuel", "Wood", "RawEarth"];
                                _data set [_randomType, (_data get _randomType) + _cargo];
                                _instances = _instances + 1;
                            };
                        } forEach _filteredArray;
                        if (_instances > 0) then {
                            _data set ["Energy", (_data get "Energy") + _energy];
                            _count = _count - _instances;
                        };
                    };
                    case "Water0": { _count = _count * 100; _type = "Water"; };
                    case "Water1": { _count = _count * 10; _type = "Water"; };
                    case "Maneuver0": { _count = _count * 10; _type = "Maneuver"; };
                    case "Maneuver1": { _count = _count * 5; _type = "Maneuver"; };
                    case "Maneuver2": { _count = _count * 2; _type = "Maneuver"; };
                    case "Maneuver3": { _count = _count * 1; _type = "Maneuver"; };
                    case "Faith0": { _count = _count * 100; _type = "Faith"; };
                    case "Faith1": { _count = _count * 25; _type = "Faith"; };
                    case "Faith2": { _count = _count * 1; _type = "Faith"; };
                    case "Communications": { _count = _count * 100; };
                };
                _data set [_type, _count];
            };
            
        } forEach YOSHI_resourceTypes;

        {
            private _type = _x;
            private _count = _y;
            if (_type != 'isWater') then {
                if ( _count > 0) then {
                    _markerName = format ["_USER_DEFINED %1 %2", _type, random 10000000];
                    _marker = createMarkerLocal [_markerName, (_bl_corner vectorAdd [_offsetDelta, _offset, 0])];
                    _marker setMarkerShapeLocal "ICON";
                    _marker setMarkerTypeLocal "mil_dot";
                    _marker setMarkerColor (YOSHI_resourceColors get _type); 
                    _marker setMarkerShadow false;
                    _marker setMarkerTextLocal format ["%1", _count];
                    globalMarkersArray pushBack _marker;
                    _offset = _offset + _offsetDelta; 
                };
            };
        } forEach _data;
    };
    YOSHI_MAP_DATA set [_bl_corner, _data];

    YOSHI_INDEXED_COUNT = YOSHI_INDEXED_COUNT + 1;
};

globalMarkersArray apply {deleteMarker _x};
globalMarkersArray = [];

_mapSize = worldSize;

_granularity = 500;

_numGrids = ceil (_mapSize / _granularity); 

for "_x" from 0 to _numGrids - 1 do {
    for "_y" from 0 to _numGrids - 1 do {
        _gridCoord = [_x * _granularity, _y * _granularity];
        [_gridCoord, _granularity] spawn YOSHI_INDEX_CELL;
    };
};

[_numGrids*_numGrids] spawn {
    params ["_totalGridCount"];

    while {YOSHI_INDEXED_COUNT < _totalGridCount} do {
        sleep 1;
    };

    hint "Done!";
}