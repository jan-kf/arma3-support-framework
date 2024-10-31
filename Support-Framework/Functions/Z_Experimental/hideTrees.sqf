_myFunction = {
    params ["_bl_corner"];

    _center = [(_bl_corner select 0)+500,(_bl_corner select 1)+500, 0];

    _objectsArray = nearestTerrainObjects [_center, ["Tree"], 750]; 
    _filteredArray = _objectsArray inAreaArray [_center, 500, 500, 0, true];
    _counter = 0;
    { 
        _obj = _x;
         if (_counter % 2 == 0) then {
            _x hideObjectGlobal true;
        };
        _counter = _counter + 1;
    } forEach _filteredArray; 
};

_mapSize = worldSize;

_numGrids = ceil (_mapSize / 1000); 

for "_x" from 0 to _numGrids - 1 do {
    for "_y" from 0 to _numGrids - 1 do {
        _gridCoord = [_x * 1000, _y * 1000];
        [_gridCoord] spawn _myFunction;
    };
};
