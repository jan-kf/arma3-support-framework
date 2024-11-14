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
	params ["_object", ["_isTowing", true]]; 
	
	_modifier = 1; 
	if (_isTowing) then {_modifier = -1}; 
	
	_interceptPoints = [_object, _modifier] call YOSHI_getVehicleInterceptPoints;
	_checkLoc = _interceptPoints select 0;
	_checkLoc2 = _interceptPoints select 1;
	
	if (_isTowing) then {
		_intersects = lineIntersectsSurfaces [_checkLoc, _checkLoc2, objNull, objNull, true, 1, "PHYSX", "FIRE"]; 
		if ((count _intersects) > 0) then { 
			[(_intersects select 0) select 0]
		} else { 
			[_checkLoc] 
		};
	} else {
		_checks = [_checkLoc, _checkLoc2] call YOSHI_sweepAngle;
		_checkRight = _checks select 0;
		_checkLeft = _checks select 1;

		_intersects = lineIntersectsSurfaces [_checkLoc, _checkRight, objNull, objNull, true, 1, "PHYSX", "FIRE"];
		_intersectsLeft = lineIntersectsSurfaces [_checkLoc, _checkLeft, objNull, objNull, true, 1, "PHYSX", "FIRE"];

		_intersects append _intersectsLeft;

		_hits = [];
		if ((count _intersects) > 0) then { 
			{_hits pushBack (_x select 0)} forEach _intersects;
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

	_realCargoTowLocation =  [_cargo, false] call YOSHI_getTowLocation;
	_realTowerTowLocation =  [_towVic, true] call YOSHI_getTowLocation;

	_cargoFrontR = ([getPosWorld _cargo, [_realCargoTowLocation select 0]] call YOSHI_realToLocal) select 0;
	_cargoFrontL = ([getPosWorld _cargo, [_realCargoTowLocation select 1]] call YOSHI_realToLocal) select 0; 
	_towRear = ([getPosWorld _towVic, [_realTowerTowLocation select 0]] call YOSHI_realToLocal) select 0; 
	_rot_cfr = [_cargoFrontR, -_cargoDeg] call YOSHI_rotateZ;
	_rot_cfl = [_cargoFrontL, -_cargoDeg] call YOSHI_rotateZ;
	_rot_tr = [_towRear, -_towDeg] call YOSHI_rotateZ;

	_rope = ropeCreate [_towVic, _rot_tr, _cargo, _rot_cfr, 5, ["RopeEnd", [0, 0, -1]], ["RopeEnd", [0, 0, -1]]];
	_rope2 = ropeCreate [_towVic, _rot_tr, _cargo, _rot_cfl, 5, ["RopeEnd", [0, 0, -1]], ["RopeEnd", [0, 0, -1]]];

	// TODO: get this to work
	if (!(isNull _rope)) then {
		_cargo setTowParent _towVic;
		// TODO: add check to reset tow parent once rope no longer exists 
	};
};

YOSHI_stowTowRopes = {
	params ["_vic"];

	private _ropes = ropes _vic;

	{ ropeDestroy _x } forEach _ropes;

};

YOSHI_towRopeActions = {
	params ["_towVic", "_target", "_params"];

	private _actions = [];

	private _towDeg = -(getDir _towVic);

	private _realTowerTowLocation =  [_towVic, true] call YOSHI_getTowLocation;
	private _towRear = ([getPosWorld _towVic, [_realTowerTowLocation select 0]] call YOSHI_realToLocal) select 0;
	private _rot_tr = [_towRear, -_towDeg] call YOSHI_rotateZ;
	private _hitchLoc = ([getPosWorld _towVic, [_rot_tr]] call YOSHI_localToReal) select 0;

	_interceptPoints = [_towVic] call YOSHI_getVehicleInterceptPoints;
	_rangePoint = _interceptPoints select 0;

	_vectorAB = ( _rangePoint vectorDiff _hitchLoc) vectorMultiply 2;

	_intersects = lineIntersectsSurfaces [_hitchLoc, (_hitchLoc vectorAdd _vectorAB) , _towVic, objNull, true, 1, "PHYSX", "FIRE"];

	if ((count _intersects) > 0) then {
		private _cargo = (_intersects select 0) select 2;

		if (_cargo isKindOf "AllVehicles") then {

			private _vehicleClass = typeOf _cargo;
			private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");

			private _vicDeployTowAction = [
				format["%1-deployTow", netId _towVic], format["Attach tow rope to %1", _vehicleDisplayName], "",
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
	};

	if ((count (ropeAttachedObjects _towVic)) > 0) then {
		private _vicStowTowAction = [
			format["%1-StowTow", netId _towVic], "Stow tow ropes", "",
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