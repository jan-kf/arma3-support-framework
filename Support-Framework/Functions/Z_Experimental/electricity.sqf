//|| _obj isKindOf "PowerLines_base_F" || _obj isKindOf "PowerLines_Small_base_F" || _obj isKindOf "Land_TTowerBig_1_F" || _obj isKindOf "Land_TTowerBig_2_F"

// _electricCondition = {
//     private _obj = _x;
//     (lightIsOn _obj) != "ERROR";
// };

// _filteredArray = _objectsArray select _electricCondition;

_objectsArray = nearestObjects [cone, [], 1000];



{
    deleteMarker _x;
} forEach globalMarkersArray;

globalMarkersArray = []; 

_filteredArray = _objectsArray;
{ 
    _obj = _x;
    _markerPos = getPos _obj; 
    _marked = false;

    _lightStat = (lightIsOn _obj);
    
    
    if (_obj isKindOf "Lamps_base_F" ) then { 
        _markerName = format ["_USER_DEFINED RedMarker_%1", _obj]; 
    
        _marker = createMarkerLocal [_markerName, _obj]; 
        _marker setMarkerShapeLocal "ICON";
        _marker setMarkerTypeLocal "mil_dot";
        _marker setMarkerColor "ColorRed"; 
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
            globalMarkersArray pushBack _marker;
            _marked = true; 
        };
        if (!_marked && _modelPath find "sloup_vn" >= 0) then {
            _markerName = format ["_USER_DEFINED PurpleMarker_%1", _obj];
            _marker = createMarkerLocal [_markerName, _obj]; 
            _marker setMarkerShapeLocal "ICON"; 
            _marker setMarkerTypeLocal "mil_dot";  
            _marker setMarkerColor "ColorCIV";  
            globalMarkersArray pushBack _marker;
            _marked = true; 
        };
        if (!_marked && _modelPath find "power" >= 0) then {
            if (!_marked && ((_modelPath find "pole" >= 0) || (_modelPath find "con" >= 0) || (_modelPath find "wood" >= 0))) then {
                _markerName = format ["_USER_DEFINED GreenMarker_%1", _obj];
                _marker = createMarkerLocal [_markerName, _obj]; 
                _marker setMarkerShapeLocal "ICON"; 
                _marker setMarkerTypeLocal "mil_dot";  
                _marker setMarkerColor "ColorGreen";  
                globalMarkersArray pushBack _marker;
                _marked = true; 
            };
            if (!_marked && _modelPath find "line" >= 0) then {
                _markerName = format ["_USER_DEFINED OrangeMarker_%1", _obj];
                _marker = createMarkerLocal [_markerName, _obj]; 
                _marker setMarkerShapeLocal "ICON"; 
                _marker setMarkerTypeLocal "mil_dot";  
                _marker setMarkerColor "ColorOrange";  
                globalMarkersArray pushBack _marker;
                _marked = true; 
            };
            if (!_marked) then {
                _markerName = format ["_USER_DEFINED WhiteMarker_%1", _obj];
                _marker = createMarkerLocal [_markerName, _obj]; 
                _marker setMarkerShapeLocal "ICON"; 
                _marker setMarkerTypeLocal "mil_dot";  
                _marker setMarkerColor "ColorWhite";  
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
        globalMarkersArray pushBack _marker; 
    };

} forEach _filteredArray; 
hint str([count _filteredArray, count globalMarkersArray]);



_objectsArray = nearestObjects [_this, [], 15]; 
 
hint str(count _objectsArray); 
 
{ 
    deleteMarker _x; 
} forEach globalMarkersArray; 
 
globalMarkersArray = [];  
   
{  
    _obj = _x;  
       
    if (_obj isKindOf "Lamps_base_F" || _obj isKindOf "PowerLines_base_F" || _obj isKindOf "PowerLines_Small_base_F" || _obj isKindOf "Land_TTowerBig_1_F" || _obj isKindOf "Land_TTowerBig_2_F") then {  
            _markerName = format ["_USER_DEFINED BlueMarker_%1", _obj];  
            _markerPos = getPos _obj;  
            _marker = createMarkerLocal [_markerName, _obj]; 
            _marker setMarkerShapeLocal "ICON"; 
            _marker setMarkerTypeLocal "mil_dot";  
            _marker setMarkerColor "ColorBlue";  
            globalMarkersArray pushBack _marker;  
    } else {
        _model = getModelInfo _obj;
        _modelPath = _model select 1;
        if (_modelPath find "powerline" >=0) then {
            _markerPos = getPos _obj;  
            _marker = createMarkerLocal [_markerName, _obj]; 
            _marker setMarkerShapeLocal "ICON"; 
            _marker setMarkerTypeLocal "mil_dot";  
            _marker setMarkerColor "ColorGreen";  
            globalMarkersArray pushBack _marker; 
        };

    };  
  
} forEach _objectsArray; 

_temp = [];

{_temp pushBack (getModelInfo _x)} forEach _objectsArray;

hint str(_temp);