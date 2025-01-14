params ["_logic", "_id", "_params"];

YOSHI_FW_CONFIG_OBJECT = createHashMapObject [[
	["#base", YOSHI_FW_BASE_CONFIG_OBJECT],
	["isInitialized", { true }]
], _logic];

YOSHI_GET_BOMB = {
    params ["_plane"];

    _plane = _this;
    private _weapons = weapons _plane;
    private _magazines = magazines _plane;

    private _bombWeapon = "";
    {
        if ((_x find "Bomb") > -1) exitWith {
            _bombWeapon = _x;
        };
        if ((_x find "Vblauncher") > -1) exitWith {
            _bombWeapon = _x;
        };
        if ((_x find "GBU") > -1) exitWith {
            _bombWeapon = _x;
        };
    } forEach _weapons;

    _bombWeapon
};

YOSHI_HAS_LEFT_MAP = {
    params ["_unit"];
    private _pos = getPosASL _unit;
    private _mapSize = worldSize;
    if (_pos select 0 < 0 || _pos select 0 > _mapSize || _pos select 1 < 0 || _pos select 1 > _mapSize) then {
        true
    } else {
        false
    };
};

YOSHI_FIXED_WING_ACTIONS = {
	
	params ["_target", "_caller", "_params"];

	private _storedWings = YOSHI_FW_CONFIG_OBJECT get "SavedUnits";
	private _fixedWingActions = [];
	{
		private _vehicleClass = _x select 0;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _storedWingAction = [
			format["deploy-%1", _vehicleClass], format["Deploy %1", _vehicleDisplayName], "",
			{
				params ["_target", "_caller", "_vehicleClass"];
				//statement
				
				_unit = [YOSHI_FW_CONFIG_OBJECT, _vehicleClass] call (YOSHI_FW_CONFIG_OBJECT get "DeployUnit");
				[_unit, getPosASL _caller, "LOITER"] call YOSHI_fnc_setWaypoint;

			}, 
			{
				params ["_target", "_caller", "_vehicleClass"];
				// Condition code here
				true
			},
			{ // 5: Insert children code <CODE> (Optional)
			},
			_vehicleClass // 6 Params
		] call ace_interact_menu_fnc_createAction;
		_fixedWingActions pushBack [_storedWingAction, [], _target];
	} forEach _storedWings;
	private _deployedWings = YOSHI_FW_CONFIG_OBJECT get "DeployedUnits";
	{
		private _vehicleClass = typeOf _x;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _deployedWingAction = [
			format["store-%1", netId _x], format["Store %1", _vehicleDisplayName], "",
			{
				params ["_target", "_caller", "_unit"];
				//statement
				
                [_unit] spawn {
                    params ["_unit"];
                    [_unit, YOSHI_FW_CONFIG_OBJECT get "MapDepartNode", "MOVE"] call YOSHI_fnc_setWaypoint;

                    waitUntil {
                        sleep 5;
                        _unit call YOSHI_HAS_LEFT_MAP;
                    };

				    [YOSHI_FW_CONFIG_OBJECT, _unit] call (YOSHI_FW_CONFIG_OBJECT get "StashUnit");
                };

			}, 
			{
				params ["_target", "_caller", "_unit"];
				// Condition code here
				true
			},
			{ // 5: Insert children code <CODE> (Optional)
			},
			_x // 6 Params
		] call ace_interact_menu_fnc_createAction;
		_fixedWingActions pushBack [_deployedWingAction, [], _target];
	} forEach _deployedWings;
	
	_fixedWingActions
};
