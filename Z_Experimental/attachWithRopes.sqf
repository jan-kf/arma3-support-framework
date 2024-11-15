getUpperCornersLocal = {
    params ["_object"];
    private _isCar = _object isKindOf "Car";
    private _bb = if (_isCar) then { boundingBoxReal [_object, "LandContact"] } else { boundingBoxReal _object };
    private _min = _bb select 0;
    private _max = _bb select 1;
    private _center = [((_min select 0) + (_max select 0)) * 0.5, ((_min select 1) + (_max select 1)) * 0.5];
    private _zNew = if (_isCar) then { (_max select 2) + 1} else { (_min select 2) * 0.5 };
    private _shrinkFactor = if (_isCar) then { 0 } else { 0.35 };
    private _corners = [];


    private _rawCorners = [
        [_max select 0, _max select 1, _max select 2],
        [_min select 0, _max select 1, _max select 2],
        [_max select 0, _min select 1, _max select 2],
        [_min select 0, _min select 1, _max select 2]
    ];
    {
        private _xOffset = (_x select 0) - (_center select 0);
        private _yOffset = (_x select 1) - (_center select 1);
        _corners pushBack [
            (_center select 0) + _xOffset * (1 - _shrinkFactor),
            (_center select 1) + _yOffset * (1 - _shrinkFactor),
            _zNew
        ];
    } forEach _rawCorners;

    hint str(_corners);

    _corners
};

spawnVisualHelpersAtCorners = {
    _object = _this;
    _corners = [_object] call getUpperCornersLocal;
    {
        _helperObject = "Land_Orange_01_NoPop_F" createVehicle [0,0,0];
        _helperObject attachTo [_object, _x];
    } forEach _corners;
};

_this call spawnVisualHelpersAtCorners;





connectObjectWithRopes = { 
    params ["_object1", "_object2"]; 
    private _corners = [_object2] call getUpperCornersLocal; 
    private _attachmentPoint = "slingload0"; 
    private _ropes = []; 
 
    { 
        private _rope = ropeCreate [_object1, _attachmentPoint, _object2, _x, 20]; 
        _ropes pushBack _rope; 
    } forEach _corners; 
 
    _ropes 
}; 


[_this, crate1] call connectObjectWithRopes;



// Spawns oranges at calculated corners

spawnVisualHelpersAtCorners = {
    _object = _this;
    _corners = [_object] call getUpperCornersLocal;
    {
        _helperObject = "Land_Orange_01_NoPop_F" createVehicle [0,0,0];
        _helperObject attachTo [_object, _x];
    } forEach _corners;
};

//_this call spawnVisualHelpersAtCorners;

/////////////////////////////////////

spawnPalletVisualHelpersAtCorners = {
    _object = _this;    
    _spawnPallet = {
        params ["_object"];

        _helper = "Land_Pallet_F" createVehicle [0,0,0];
        _minbb = (boundingBoxReal _object) select 0;
        _minz = _minbb select 2;
        _helper attachTo [_object, [0,0,_minz -0.1]];

        _helper
    };
    _pallet = _object call _spawnPallet;
    _corners = _pallet call getPalletCornersLocal;
    {
        _helperObject = "Land_Orange_01_NoPop_F" createVehicle [0,0,0];
        _helperObject attachTo [_pallet, _x];
    } forEach _corners;
};


getPalletCornersLocal = {
    params ["_object"];
    private _bb = boundingBoxReal _object;
    private _min = _bb select 0;
    private _max = _bb select 1;
    private _center = [((_min select 0) + (_max select 0)) * 0.5, ((_min select 1) + (_max select 1)) * 0.5];
    private _shrinkFactor = 0.35;
    private _corners = [];


    private _rawCorners = [
        [_max select 0, _max select 1, _max select 2],
        [_min select 0, _max select 1, _max select 2],
        [_max select 0, _min select 1, _max select 2],
        [_min select 0, _min select 1, _max select 2]
    ];
    {
        private _xOffset = (_x select 0) - (_center select 0);
        private _yOffset = (_x select 1) - (_center select 1);
        _corners pushBack [
            (_center select 0) + _xOffset * (1 - _shrinkFactor),
            (_center select 1) + _yOffset * (1 - _shrinkFactor),
            0
        ];
    } forEach _rawCorners;

    hint str(_corners);

    _corners
};


getUpperCornersLocal = {
    params ["_object"];
    private _isCar = _object isKindOf "Car";
    private _bb = if (_isCar) then { boundingBoxReal [_object, "LandContact"] } else { boundingBoxReal _object };
    private _min = _bb select 0;
    private _max = _bb select 1;
    private _center = [((_min select 0) + (_max select 0)) * 0.5, ((_min select 1) + (_max select 1)) * 0.5];
    private _zNew = if (_isCar) then { (_max select 2) + 1} else { (_min select 2) * 0.5 };
    private _shrinkFactor = if (_isCar) then { 0 } else { 0.35 };
    private _corners = [];


    private _rawCorners = [
        [_max select 0, _max select 1, _max select 2],
        [_min select 0, _max select 1, _max select 2],
        [_max select 0, _min select 1, _max select 2],
        [_min select 0, _min select 1, _max select 2]
    ];
    {
        private _xOffset = (_x select 0) - (_center select 0);
        private _yOffset = (_x select 1) - (_center select 1);
        _corners pushBack [
            (_center select 0) + _xOffset * (1 - _shrinkFactor),
            (_center select 1) + _yOffset * (1 - _shrinkFactor),
            _zNew
        ];
    } forEach _rawCorners;

    hint str(_corners);

    _corners
};

spawnPalletVisualHelpersAtCorners = {
    params ["_object"];
    if (!(_object isKindOf "Car")) then {
        _spawnPallet = {
            params ["_object"];

            _helper = "Land_Pallet_F" createVehicle [0,0,0];
            _minbb = (boundingBoxReal _object) select 0;
            _minz = _minbb select 2;
            _helper attachTo [_object, [0,0,_minz -0.1]];

            _helper
        };
        _pallet = _object call _spawnPallet;
    };
    _corners = _object call getUpperCornersLocal;
    _corners
};




connectObjectWithRopes = { 
    params ["_heli", "_object"]; 
    private _corners = [_object] call spawnPalletVisualHelpersAtCorners; 
    hint str(_corners);
    private _attachmentPoint = "slingload0"; 
    private _ropes = []; 
 
    { 
        private _rope = ropeCreate [_heli, _attachmentPoint, _object, _x, 20]; 
        _ropes pushBack _rope; 
    } forEach _corners; 
 
    _ropes 
}; 

[_this, crate] call connectObjectWithRopes;