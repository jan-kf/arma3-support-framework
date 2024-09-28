//|| _obj isKindOf "PowerLines_base_F" || _obj isKindOf "PowerLines_Small_base_F" || _obj isKindOf "Land_TTowerBig_1_F" || _obj isKindOf "Land_TTowerBig_2_F"

// _electricCondition = {
//     private _obj = _x;
//     (lightIsOn _obj) != "ERROR";
// };

// _filteredArray = _objectsArray select _electricCondition;
//"Building" filter gets everything except for powerline poles and some of the drat HV lines
//HV: sloup_vn | drat, drat_d, dratz, dratzl, dratzp

_myFunction = {
    params ["_bl_corner"];

    _center = [(_bl_corner select 0)+500,(_bl_corner select 1)+500, 0];

    _objectsArray = nearestTerrainObjects [_center, ["Building", "Power Lines", "Hide", "Transmitter", "Powersolar", "Powerwind", "Powerwave"], 750]; 
    _objectsArray append (nearestObjects [_center, [], 750]);
    _filteredArray = _objectsArray inAreaArray [_center, 500, 500, 0, true];
    { 
        _obj = _x;
        _markerPos = getPosWorld _obj; 
        _marked = false;

        _lightStat = (lightIsOn _obj);
        
        
        if (_obj isKindOf "Lamps_base_F" ) then { 
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
            if (!_marked && ((_modelPath find "trafost" >= 0) || (_modelPath find "transform" >= 0))) then {
                _markerName = format ["_USER_DEFINED BlueMarker_%1", _obj];
                _marker = createMarkerLocal [_markerName, _obj]; 
                _marker setMarkerShapeLocal "ICON"; 
                _marker setMarkerTypeLocal "mil_dot";  
                _marker setMarkerColor "ColorBlue";  
                _marker setMarkerShadow false;
                globalMarkersArray pushBack _marker;
                _marked = true; 
            };
            if (!_marked && _modelPath find "sloup_vn" >= 0) then {
                if (!_marked && ((_modelPath find "drat" >= 0) || (_modelPath find "drat_d" >= 0) || (_modelPath find "dratzl" >= 0) || (_modelPath find "dratzp" >= 0))) then {
                    _markerName = format ["_USER_DEFINED OrangeMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorOrange";  
                    _marker setMarkerShadow false;
                    globalMarkersArray pushBack _marker;
                    _marked = true; 
                } else {
                    _markerName = format ["_USER_DEFINED PurpleMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorCIV";  
                    _marker setMarkerShadow false;
                    globalMarkersArray pushBack _marker;
                    _marked = true; 
                };
            };
            if (!_marked && _modelPath find "highvoltage" >= 0) then {
                if (!_marked && _modelPath find "tower" >= 0) then {
                    _markerName = format ["_USER_DEFINED PurpleMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorCIV";  
                    _marker setMarkerShadow false;
                    globalMarkersArray pushBack _marker;
                    _marked = true;
                };
                if (!_marked && _modelPath find "wire" >= 0) then {
                    _markerName = format ["_USER_DEFINED OrangeMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorOrange";
                    _marker setMarkerShadow false;  
                    globalMarkersArray pushBack _marker;
                    _marked = true;  
                };
                if (!_marked) then {
                    _markerName = format ["_USER_DEFINED UnknownMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorYellow";  
                    _marker setMarkerShadow false;
                    _marker setMarkerTextLocal format ["%1", _modelPath];
                    globalMarkersArray pushBack _marker;
                    _marked = true;
                }; 
            };
            if (!_marked && _modelPath find "power" >= 0) then {
                if (!_marked && ((_modelPath find "pole" >= 0) || (_modelPath find "con" >= 0) || (_modelPath find "wood" >= 0))) then {
                    _markerName = format ["_USER_DEFINED GreenMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorGreen";
                    _marker setMarkerShadow false;  
                    globalMarkersArray pushBack _marker;
                    _marked = true; 
                };
                if (!_marked && _modelPath find "line" >= 0) then {
                    _markerName = format ["_USER_DEFINED OrangeMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorOrange";
                    _marker setMarkerShadow false;  
                    globalMarkersArray pushBack _marker;
                    _marked = true; 
                };
                if (!_marked) then {
                    _markerName = format ["_USER_DEFINED WhiteMarker_%1", _obj];
                    _marker = createMarkerLocal [_markerName, _obj]; 
                    _marker setMarkerShapeLocal "ICON"; 
                    _marker setMarkerTypeLocal "mil_dot";  
                    _marker setMarkerColor "ColorWhite";
                    _marker setMarkerShadow false;  
                    globalMarkersArray pushBack _marker;
                    _marked = true;
                };
            };
            if (!_marked && (_modelPath find "amplion" >= 0)) then {
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
                        
        if (!_marked && (_lightStat == "ON")) then { 
            _markerName = format ["_USER_DEFINED PinkMarker_%1", _obj]; 

            _marker = createMarkerLocal [_markerName, _obj];
            _marker setMarkerShapeLocal "ICON";
            _marker setMarkerTypeLocal "mil_dot"; 
            _marker setMarkerColor "ColorPink";
            _marker setMarkerShadow false; 
            globalMarkersArray pushBack _marker; 
        };
    } forEach _filteredArray; 
    hint str([count _filteredArray, count globalMarkersArray]);
};

globalMarkersArray apply {deleteMarker _x};
globalMarkersArray = [];

_mapSize = worldSize;

_numGrids = ceil (_mapSize / 1000); 

for "_x" from 0 to _numGrids - 1 do {
    for "_y" from 0 to _numGrids - 1 do {
        _gridCoord = [_x * 1000, _y * 1000];
        [_gridCoord] spawn _myFunction;
    };
};



if (isServer) then {    
    _drawBldgs = {
        params ["_mkr"];
        _mkr setmarkerAlpha 0; 
        _pos = markerpos _mkr; 
        _mkrY = getmarkerSize _mkr select 0; 
        _mkrX = getmarkerSize _mkr select 1; 
        _distance = _mkrX; 
        if (_mkrY > _mkrX) 
        then { 
        _distance =_mkrY; 
        }; 
        
        _HouseArray = ["Building","House"]; 
        _nearestBuildings = nearestObjects [_pos, _HouseArray, _distance]; 
        { 
        
            _x setVectorUp [0,0,1]; 
            _x enableSimulation false; 
            
            _boundingBox = boundingBox _x; 
            _dir = getDir _x; 
            _position = getPosATL _x; 
            
            _size = _boundingBox select 1; 
            _size resize 1.5; 
            _markername = "marker" + str(floor(random 500)) + str(floor(random 500)); 
            
            createMarker [_markername, _position]; 
            _markername setMarkerShape "RECTANGLE"; 
            _markername setMarkerSize _size; 
            _markername setMarkerBrush "SolidFull"; 
            _markername setMarkerColor "ColorGrey"; 
            _markername setMarkerDir _dir; 
        } forEach _nearestBuildings;
    }; 
    { 
        [_x] call _drawBldgs;
    } forEach ["construct", "base_area"]; 
};

/////////////


private _allTerrainObjects = nearestObjects 
 [ 
  _this, 
  [], 
  1000 
 ]; 
 _allTerrainObjects append (nearestObjects [_this, [], 1000]);
 { _x switchLight "OFF" } forEach _allTerrainObjects;