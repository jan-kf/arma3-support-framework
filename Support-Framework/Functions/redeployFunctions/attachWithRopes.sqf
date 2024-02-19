getUpperCornersLocal = { 
    params ["_object"]; 
    private _bbox = boundingBoxReal [_object, "LandContact"];
	private _bboxH = boundingBoxReal [_object, "ViewGeometry"]; 
    private _min = _bbox select 0; 
    private _max = _bbox select 1;
	private _height = _bboxH select 1; 
	hint format ["%1", (_height select 2)*5];
    [ 
        [_max select 0, _max select 1, (_height select 2)*5], 
        [_min select 0, _max select 1, (_height select 2)*5], 
        [_max select 0, _min select 1, (_height select 2)*5], 
        [_min select 0, _min select 1, (_height select 2)*5] 
    ] 
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