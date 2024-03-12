getUpperCornersLocal = {
    params ["_object"];
    private _isCar = _object isKindOf "Car";
    private _bb = if (_isCar) then { boundingBoxReal [_object, "LandContact"] } else { boundingBoxReal _object };
    private _min = _bb select 0;
    private _max = _bb select 1;
    private _center = [((_min select 0) + (_max select 0)) * 0.5, ((_min select 1) + (_max select 1)) * 0.5];
    private _zNew = if (_isCar) then { (_max select 2) * 0.25 } else { ((_min select 2) + (_max select 2)) * 0.55 };
    private _shrinkFactor = if (_isCar) then { 0 } else { 0.2 };
    private _corners = [];

    {
        private _xOffset = (_x select 0) - (_center select 0);
        private _yOffset = (_x select 1) - (_center select 1);
        _corners pushBack [
            (_center select 0) + _xOffset * (1 - _shrinkFactor),
            (_center select 1) + _yOffset * (1 - _shrinkFactor),
            _zNew
        ];
    } forEach [
        [_max select 0, _max select 1, _max select 2],
        [_min select 0, _max select 1, _max select 2],
        [_max select 0, _min select 1, _max select 2],
        [_min select 0, _min select 1, _max select 2]
    ];

    _corners
};



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