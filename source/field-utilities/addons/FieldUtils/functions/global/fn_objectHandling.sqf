
YOSHI_setObjectLoadHandling = {
	params ["_object"];

	[_object, -1] call ace_cargo_fnc_setSize;

	_object addEventHandler ["EpeContactStart", {
		params ["_object1", "_object2", "_selection1", "_selection2", "_force", "_reactForce", "_worldPos"];
		_object1 call YOSHI_attachToBelow;
	}];
};

YOSHI_attachToBelow = {
	params ["_obj"];
	if (isNull _obj) exitWith {false};

	private _loc = getPosASL _obj;
	private _locBelow = _loc vectorAdd [0,0,-2];

	private _hits = lineIntersectsSurfaces [_loc, _locBelow, _obj, objNull, true, 1, "FIRE", "GEOM"];
	if (_hits isEqualTo []) exitWith {false};

	private _firstHit = _hits select 0;
	if ((count _firstHit) < 3) exitWith {false};

	private _hitPos = _firstHit select 0;
	private _hitObj = _firstHit select 2;

	if (!isNull _hitObj && {!(_hitObj isKindOf "Static")}) then {
		private _objectToAttach = _obj;
		private _targetObject = _hitObj;
		private _dirObjectToAttach = getDir _objectToAttach;
		private _dirTargetObject = getDir _targetObject;
		_objectToAttach attachTo [_targetObject];
		_objectToAttach setPosASL _hitPos;
		_objectToAttach setDir ( _dirObjectToAttach - _dirTargetObject);
		true
	} else {
		false
	};
};

YOSHI_getSuppliesAction = {
	params ["_box", "_caller", "_params"];

	private _actions = [];


	{
		private _vic = _x;
		private _checks = _vic canVehicleCargo _box;

		if ((_checks select 0) && (_checks select 1)) then {
			private _loadSuppliesAction = [
				format["loadSupplies-%1", netId _vic], format ["Load Into %1", getText (configFile >> "CfgVehicles" >> typeOf _vic >> "displayName")], "",
				{
					params ["_target", "_caller", "_vic"];

					_vic setVehicleCargo _target;
				}, 
				{
					params ["_target", "_caller", "_vic"];

					true
				},
				{},
				_vic
			] call ace_interact_menu_fnc_createAction;
			_actions pushBack [_loadSuppliesAction, [], _box];
		};

	} forEach (_box nearEntities ['AllVehicles', 10]);

	_actions

};
