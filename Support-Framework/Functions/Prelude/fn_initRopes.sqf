YOSHI_getVehicleInterceptPoints = {
	params ["_object", ["_modifier", -1]];

	_corners = boundingBoxReal _object; 
	_center = ([_object] call YOSHI_getCenterOfMass) select 0; 
	_dir = vectorDir _object; 
	_xdir = (_corners select 0) select 0; 
	_ydir = ((_corners select 0) select 1); 
	_magnitude = sqrt ((_xdir ^ 2) + (_ydir ^ 2)); 
	_vector = _dir vectorMultiply (_magnitude * _modifier); 
	_checkLoc = _center vectorAdd _vector; // ASL or World (ASL is like 5 inches higher) 
	_checkLoc2 = _center vectorAdd (_vector vectorMultiply -1);

	[_checkLoc, _checkLoc2]
};

// TODO: make sure to only check intersects that are of the relevant object
YOSHI_getTowLocation = { 
	params ["_object", ["_isTowing", true], ['_otherObject', objNull]]; 
	
	_modifier = 1; 
	if (_isTowing) then {_modifier = -1}; 
	
	_interceptPoints = [_object, _modifier] call YOSHI_getVehicleInterceptPoints;
	_checkLoc = _interceptPoints select 0;
	_checkLoc2 = _interceptPoints select 1;
	
	if (_isTowing) then {
		_intersects = lineIntersectsSurfaces [_checkLoc, _checkLoc2, _otherObject, objNull, true, 5, "FIRE", "GEOM"];
		_hits = [];
		{
			_intersected_object = _x select 2;
			if (_intersected_object == _object) then {
				_hits pushBack (_x select 0);
			}
		} forEach _intersects;

		if ((count _hits) > 0) then { 
			_hits
		} else { 
			[_checkLoc] 
		};
	} else {
		_checks = [_checkLoc, _checkLoc2] call YOSHI_sweepAngle;
		_checkRight = _checks select 0;
		_checkLeft = _checks select 1;

		_intersects = lineIntersectsSurfaces [_checkLoc, _checkRight, _otherObject, objNull, true, 5, "FIRE", "GEOM"];
		_intersectsLeft = lineIntersectsSurfaces [_checkLoc, _checkLeft, _otherObject, objNull, true, 5, "FIRE", "GEOM"];
		_intersects append _intersectsLeft;

		_hits = [];

		{
			_intersected_object = _x select 2;
			if (_intersected_object == _object) then {
				_hits pushBack (_x select 0);
			}
		} forEach _intersects;
		

		if ((count _hits) > 0) then { 
			_hits
		} else { 
			[_checkLoc] 
		};
	}; 
}; 

YOSHI_deployTowRopes = {
	params ["_towVic", "_cargo"]; 
	
	private _towDeg = -(getDir _towVic);  
	private _cargoDeg = -(getDir _cargo);  

	_towVicLookup = [_towVic] call YOSHI_getTowingPoints;
	_cargoLookup = [_cargo] call YOSHI_getTowingPoints;
	_rot_tr = [0,0,0];
	_rotatedCargoAttachPoints = [[0,0,0]];

	if ((count _towVicLookup) > 0) then {
		_rot_tr = (_towVicLookup select 1) select 0;
	} else {
		_realTowerTowLocation =  [_towVic, true, _cargo] call YOSHI_getTowLocation;
		_towRear = ([getPosWorld _towVic, [_realTowerTowLocation select 0]] call YOSHI_realToLocal) select 0; 
		_rot_tr = [_towRear, -_towDeg] call YOSHI_rotateZ;
	};



	if ((count _cargoLookup) > 0) then {
		_rotatedCargoAttachPoints = _cargoLookup select 0;
	} else {
		_realCargoTowLocation =  [_cargo, false, _towVic] call YOSHI_getTowLocation;

		_cargoFrontAttachPoints = [];

		{
			_cargoFrontAttachPoints pushBack (([getPosWorld _cargo, [_x]] call YOSHI_realToLocal) select 0);
		} forEach _realCargoTowLocation;


		_rotatedCargoAttachPoints = [];
		{
			_rotatedCargoAttachPoints pushBack ([_x, -_cargoDeg] call YOSHI_rotateZ);
		} forEach _cargoFrontAttachPoints;
	};

	_createdRopes = [];
	{
		_createdRopes pushBack (ropeCreate [_towVic, _rot_tr, _cargo, _x, 5, ["RopeEnd", [0, 0, 1]], ["RopeEnd", [0, 0, 1]], "Spring1xRope"]);
	} forEach _rotatedCargoAttachPoints;

	_shouldSetParent = false;
	{
		if (!isNull _x) then {
			_shouldSetParent = true;
		};
	} forEach _createdRopes;

	// TODO: get this to work
	if (_shouldSetParent) then {
		[_cargo, _towVic] remoteExec ["setTowParent"];
		// TODO: add check to reset tow parent once rope no longer exists 
	};
};

YOSHI_stowTowRopes = {
	params ["_vic"];

	private _attachedObjects = ropeAttachedObjects _vic;

	{ [_x, objNull] remoteExec ["setTowParent"] } forEach _attachedObjects;
	
	private _ropes = ropes _vic;

	{ ropeDestroy _x } forEach _ropes;

};


//CUP_Ridgback_Base
YOSHI_towRopeActions = {
	params ["_towVic", "_target", "_params"];

	private _actions = [];

	private _hitchLoc =  ([_towVic, true] call YOSHI_getTowLocation) select 0;

	_interceptPoints = [_towVic] call YOSHI_getVehicleInterceptPoints;
	_rangePoint = _interceptPoints select 0;

	_vectorAB = ( _rangePoint vectorDiff _hitchLoc) vectorMultiply 5;
	_aBitBack = (_hitchLoc vectorAdd _vectorAB);
	_aBitUp = _aBitBack vectorAdd [0,0,1];
	_aBitDown = _aBitBack vectorAdd [0,0,-1];

	_intersects1 = lineIntersectsSurfaces [_hitchLoc,  _aBitBack, _towVic, objNull, true, 1, "FIRE", "GEOM"];
	_intersects2 = lineIntersectsSurfaces [_hitchLoc, _aBitUp, _towVic, objNull, true, 1, "FIRE", "GEOM"];
	_intersects3 = lineIntersectsSurfaces [_hitchLoc, _aBitDown, _towVic, objNull, true, 1, "FIRE", "GEOM"];

	_intersects = _intersects1+_intersects2+_intersects3;

	{
		private _cargo = _x select 2;

		if (_cargo isKindOf "AllVehicles") exitWith {

			private _vehicleClass = typeOf _cargo;
			private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");

			private _vicDeployTowAction = [
				format["%1-deployTow", netId _towVic], format["Attach tow rope to %1", _vehicleDisplayName], "\A3\ui_f\data\map\markers\military\join_CA.paa",
				{
					params ["_target", "_caller", "_args"];
					// statement 
					private _towVic = _args select 0;
					private _cargo = _args select 1;

					[_towVic, _cargo] call YOSHI_deployTowRopes;

				}, 
				{
					params ["_target", "_caller", "_args"];
					// // Condition code here
					private _towVic = _args select 0;
					private _cargo = _args select 1;

					private _check = true;
					{
						if (_x == _cargo) then {
							_check = false;
						}
					} forEach (ropeAttachedObjects _towVic);

					_check

				},
				{}, // 5: Insert children code <CODE> (Optional)
				[_towVic, _cargo] // 6: Action parameters <ANY> (Optional)
			] call ace_interact_menu_fnc_createAction;

			_actions pushBack [_vicDeployTowAction, [], _target];
		};
	} forEach _intersects;

	if ((count (ropeAttachedObjects _towVic)) > 0) then {
		private _vicStowTowAction = [
			format["%1-StowTow", netId _towVic], "Stow tow ropes", "\A3\ui_f\data\map\markers\nato\respawn_unknown_ca.paa",
			{
				params ["_target", "_caller", "_towVic"];
				// statement 

				[_towVic] call YOSHI_stowTowRopes;
			}, 
			{
				params ["_target", "_caller", "_towVic"];
				// // Condition code here
				true
			},
			{}, // 5: Insert children code <CODE> (Optional)
			_towVic // 6: Action parameters <ANY> (Optional)
		] call ace_interact_menu_fnc_createAction;

		_actions pushBack [_vicStowTowAction, [], _target];
	};


	_actions
};