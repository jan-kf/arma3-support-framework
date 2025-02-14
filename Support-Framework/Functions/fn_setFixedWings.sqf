params ["_logic", "_id", "_params"];

YOSHI_FW_CONFIG_OBJECT = createHashMapObject [[
	["#base", YOSHI_FW_BASE_CONFIG_OBJECT],
	["isInitialized", { true }]
], _logic];

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

YOSHI_SEND_FW_AWAY = {
    params ["_unit"];
    _unit setVariable ["YOSHI_FW_CALLER", objNull];
    [_unit] spawn {
        params ["_unit"];
        [_unit, YOSHI_FW_CONFIG_OBJECT get "MapDepartNode", "MOVE"] call YOSHI_fnc_setWaypoint;

        waitUntil {
            sleep 5;
            _unit call YOSHI_HAS_LEFT_MAP;
        };

        [YOSHI_FW_CONFIG_OBJECT, _unit] call (YOSHI_FW_CONFIG_OBJECT get "StashUnit");
    };
};

YOSHI_FIXED_WING_DEPLOYMENTS = {
	
	params ["_target", "_caller", "_params"];

	private _storedWings = YOSHI_FW_CONFIG_OBJECT get "SavedUnits";
	private _fixedWingActions = [];
	{
		private _vehicleClass = _x select 0;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _storedWingAction = [
			format["deploy-%1-%2", _vehicleClass, random 1000], format["Deploy %1", _vehicleDisplayName], "",
			{
				params ["_target", "_caller", "_vehicleClass"];
				//statement
				
				_unit = [YOSHI_FW_CONFIG_OBJECT, _vehicleClass, _caller] call (YOSHI_FW_CONFIG_OBJECT get "DeployUnit");
				[_unit, getPosASL _caller, "LOITER"] call YOSHI_fnc_setWaypoint;
                hint "Deploying Asset"; 

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
				
				_unit call YOSHI_SEND_FW_AWAY;
                hint "Sending Asset Away";

			}, 
			{
				params ["_target", "_caller", "_unit"];
				// Condition code here
				alive _unit
			},
			{ // 5: Insert children code <CODE> (Optional)
			},
			_x // 6 Params
		] call ace_interact_menu_fnc_createAction;
		_fixedWingActions pushBack [_deployedWingAction, [], _target];
	} forEach _deployedWings;
	
	_fixedWingActions
};

YOSHI_FIXED_WING_LOGI_ACTIONS = {
	
	params ["_target", "_caller", "_params"];
	
    private _fixedWingLogiActions = [];

    private _deployedWings = YOSHI_FW_CONFIG_OBJECT get "DeployedUnits";
	{
        if ((_x call YOSHI_GET_FW_ROLE) >= 4) then {
            private _vehicleClass = typeOf _x;
            private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
            private _FW_CustomSupplies_Action = [
                format["requestSupplies-%1", netId _x], format["Custom Drop: %1", _vehicleDisplayName], "\a3\ui_f\data\igui\cfg\simpletasks\types\rearm_ca.paa",
                {
                    params ["_target", "_caller", "_unit"];
                    //statement
                    
                    // Do Custom Logi Stuff

                    private _newObject = createVehicle ["B_supplyCrate_F", getPosASL _unit, [], 0, "NONE"];
                    [_newObject] call zen_inventory_fnc_configure; 

                    [_newObject, _caller] call YOSHI_FLING_THING;
                    
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
            _fixedWingLogiActions pushBack [_FW_CustomSupplies_Action, [], _target];
            private _virtualStorageConfigured = !(isNil "YOSHI_VIRTUAL_STORAGE");
            if (_virtualStorageConfigured) then {
                private _FW_SupplyDrop_Action = [
                    format["requestSupplies-%1", netId _x], format["Supply Drop: %1", _vehicleDisplayName], "\a3\ui_f\data\igui\cfg\simpletasks\types\box_ca.paa",
                    {
                        params ["_target", "_caller", "_unit"];
                        // Parent Placeholder
                                            
                    }, 
                    {
                        params ["_target", "_caller", "_unit"];
                        
                        true
                    },
                    { // 5: Spawner Code
                        params ["_target", "_caller", "_unit"];

                        private _syncedVirtualStorageObjects = synchronizedObjects YOSHI_VIRTUAL_STORAGE;

                        private _supplyDropActions = [];
                        {
                            private _itemToSpawn = _x;
                            private _classOfItemToSpawn = (typeOf _itemToSpawn);
                            HG_getConfig =
                            {
                                params["_item"];

                                switch true do
                                {
                                    case(isClass(configFile >> "CfgMagazines" >> _item)): {"CfgMagazines"};
                                    case(isClass(configFile >> "CfgWeapons" >> _item)): {"CfgWeapons"};
                                    case(isClass(configFile >> "CfgVehicles" >> _item)): {"CfgVehicles"};
                                    case(isClass(configFile >> "CfgGlasses" >> _item)): {"CfgGlasses"};
                                };
                            };
                            _config = [_classOfItemToSpawn] call HG_getConfig;
                            _displayName = getText(configFile >> _config >> _classOfItemToSpawn >> "displayName");
                            private _FW_SupplyDrop_Action_Singular = [
                                format ["SpawnItemAction-%1", _classOfItemToSpawn], // Action ID
		                        format ["Spawn %1", _displayName], // Title, 
                                "\a3\ui_f\data\igui\cfg\simpletasks\types\Download_ca.paa",
                                {
                                    params ["_target", "_caller", "_params"];
                                    private _newObject = [_target, _caller, _params] call YOSHI_SPAWN_SAVED_ITEM_ACTION;

                                    [_newObject, _caller] call YOSHI_FLING_THING;          
                                }, 
                                {
                                    params ["_target", "_caller", "_params"];
                                    // Condition code here
                                    true
                                },
                                {},
                                [_unit, _x] // 6 Params
                            ] call ace_interact_menu_fnc_createAction;
                            _supplyDropActions pushBack [_FW_SupplyDrop_Action_Singular, [], _target];
                            
                        } forEach _syncedVirtualStorageObjects;
                        _supplyDropActions

                    },
                    _x // 6 Params
                ] call ace_interact_menu_fnc_createAction;
                _fixedWingLogiActions pushBack [_FW_SupplyDrop_Action, [], _target];
            };
        };
	} forEach _deployedWings;

    _fixedWingLogiActions
};

YOSHI_FIXED_WING_ACTIONS = {
	
	params ["_target", "_caller", "_params"];
	
    private _targetActions = ([false] call YOSHI_fnc_createTargetsFromLasers);

    private _logiActions = [_target, _caller, _params] call YOSHI_FIXED_WING_LOGI_ACTIONS;

    _targetActions + _logiActions;
};
