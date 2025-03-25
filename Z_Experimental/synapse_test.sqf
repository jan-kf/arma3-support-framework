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
    ["Wood", ["TREE", "SMALL TREE"]],
    ["RawEarth", ["ROCK", "ROCKS"]], 
    ["Energy", ["POWERSOLAR", "POWERWIND", "POWERWAVE"]], 
    ["Fuel", ["FUELSTATION"]], 
    ["Manpower", ["HOUSE"]],
    ["Water", ["WATERTOWER", "FOUNTAIN"]],
    ["Maneuver", ["MAIN ROAD", "ROAD"]],
    ["Faith", ["CHURCH", "CHAPEL"]],
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

YOSHI_INDEX_CELL = {
    params ["_bl_corner", ["_granularity", 1000]];

    private _halfSize = _granularity / 2;
    private _center = _bl_corner vectorAdd [_halfSize, _halfSize, 0];

    private _data = createHashMapFromArray [
        ["Wood",0], ["RawEarth",0], ["Energy",0], ["Fuel",0],
        ["Manpower",0], ["Water",0], ["Maneuver",0], ["Faith",0],
        ["Communications",0], ["isWater",false]
    ];

    if (surfaceIsWater _center) then {
        _data set ["isWater", true];
        YOSHI_MAP_DATA set [_bl_corner, _data];
    } else {

        private _commonTypes = ["TREE", "SMALL TREE", "ROCK", "ROCKS"];
        private _rareTypes = ["FUELSTATION", "WATERTOWER", "FOUNTAIN", "CHURCH", "CHAPEL", "TRANSMITTER", "POWERSOLAR", "POWERWIND", "POWERWAVE", "MAIN ROAD", "ROAD", "HOUSE"];

        private _commonObjs = nearestTerrainObjects [_center, _commonTypes, _halfSize * 1.5];
        private _rareObjs = nearestTerrainObjects [_center, _rareTypes, _halfSize * 1.5];

        private _woodObjs = _commonObjs select {typeOf _x in ["TREE", "SMALL TREE"]};
        private _rockObjs = _commonObjs select {typeOf _x in ["ROCK", "ROCKS"]};

        _data set ["Wood", count _woodObjs];
        _data set ["RawEarth", count _rockObjs];

        {   
            private _type = _x;
            if (_type == "Wood") exitWith {};
            if (_type == "RawEarth") exitWith {};
            private _filteredArray = _rareObjs select {typeOf _x in (_y)};
            private _count = count _filteredArray;

            if (_type == "Manpower") then {
                private _energy = 0;
                private _cargoTotal = 0;
                {
                    private _elec = _x call YOSHI_isObjectElectric;
                    private _cargo = ceil (_x call YOSHI_isObjectSupplies);
                    if (_elec > 0) then {
                        _energy = _energy + _elec;
                        _count = _count - 1;
                    };
                    if (_cargo > 0) then {
                        private _randomType = selectRandom ["Fuel", "Wood", "RawEarth"];
                        _data set [_randomType, (_data get _randomType) + _cargo];
                        _count = _count - 1;
                    };
                } forEach _filteredArray;
                _data set ["Energy", (_data get "Energy") + _energy];
            };

            if (_type == 'Fuel') then {_count = _count * 50};
            _data set [_type, (_data get _type) + _count];
            
        } forEach (YOSHI_resourceTypes);

        private _offsetDelta = _granularity / 50;
        private _offset = _offsetDelta;

        {
            private _type = _x;
            private _count = _y;
            if (_type != 'isWater') then {
                if (_count > 0) then {

                    private _marker = createMarkerLocal [format ["_USER_DEFINED marker_%1_%2", _type, random 100000], _bl_corner vectorAdd [_offsetDelta, _offset, 0]];
                    _marker setMarkerShapeLocal "ICON";
                    _marker setMarkerTypeLocal "mil_dot";
                    _marker setMarkerColor (YOSHI_resourceColors get _type);
                    _marker setMarkerShadow false;
                    _marker setMarkerTextLocal format ["%1: %2", _type, _count];
                    globalMarkersArray pushBack _marker;
                    _offset = _offset + _offsetDelta; 
                };
            };
        } forEach _data;

        YOSHI_MAP_DATA set [_bl_corner, _data];
    };

    _data

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
