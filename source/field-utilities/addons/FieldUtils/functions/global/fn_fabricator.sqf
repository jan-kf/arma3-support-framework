// Delivery crates must stay light enough for a player to pick up. An object
// only reports a real mass once it has settled at a position inside the map, so
// this has to be re-applied after a staged clone is placed: capping it while it
// is still staged out of sight silently does nothing.
YOSHI_capDeliveryMass = {
    params ["_object", ["_settleTimeout", 10]];
    if (isNull _object) exitWith {false};
    if !(_object isKindOf "ReammoBox_F") exitWith {false};

    // A newly created object reports no mass for a while. Reading it straight
    // away returns ~0, so the cap silently never fires and the delivery keeps a
    // degenerate mass. Wait for a real value first, when the caller can wait.
    if (canSuspend) then {
        private _deadline = diag_tickTime + _settleTimeout;
        waitUntil {
            uiSleep 0.25;
            (getMass _object) > 0 || {diag_tickTime > _deadline}
        };
    };

    if ((getMass _object) > 200) then {
        _object setMass 200;
        true
    } else {
        false
    };
};

YOSHI_SPAWN_SAVED_ITEM_ACTION = {
    params ["_target", "_caller", "_params", ["_onCreated", {}], ["_onCreatedArgs", []]];
    private _fabricator = _params select 0;
    private _itemToAdd = _params select 1;
    private _locationOverride = _params param [2, objNull];

    private _fabricatorPos = getPosATL _fabricator;
    private _location = _fabricator;
    private _hasLocationOverride = (typeName _locationOverride) isEqualTo "ARRAY" && {(count _locationOverride) isEqualTo 3};
    if (_hasLocationOverride) then {
        _location = _locationOverride;
    };
    if (!_hasLocationOverride && {_fabricatorPos select 2 > 200}) then {
        _location = [_fabricatorPos select 0, _fabricatorPos select 1, (_fabricatorPos select 2) - 10];
    };


    private _newObject = createVehicle [typeOf _itemToAdd, _location, [], 0, "NONE"];
    // Consequential callers can record ownership at the creation boundary,
    // before cargo restoration or any later operation can fail.
    [_newObject, _onCreatedArgs] call _onCreated;

    clearWeaponCargoGlobal _newObject;
    clearMagazineCargoGlobal _newObject;
    clearItemCargoGlobal _newObject;
    clearBackpackCargoGlobal _newObject;


    private _weapons = getWeaponCargo _itemToAdd;
    {
        private _weaponType = (_weapons select 0) select _forEachIndex;
        private _weaponCount = (_weapons select 1) select _forEachIndex;
        _newObject addWeaponCargoGlobal [_weaponType, _weaponCount];
    } forEach (_weapons select 0);


    private _magazines = getMagazineCargo _itemToAdd;
    {
        private _magazineType = (_magazines select 0) select _forEachIndex;
        private _magazineCount = (_magazines select 1) select _forEachIndex;
        _newObject addMagazineCargoGlobal [_magazineType, _magazineCount];
    } forEach (_magazines select 0);


    private _items = getItemCargo _itemToAdd;
    {
        private _itemType = (_items select 0) select _forEachIndex;
        private _itemCount = (_items select 1) select _forEachIndex;
        _newObject addItemCargoGlobal [_itemType, _itemCount];
    } forEach (_items select 0);

    private _backpacks = getBackpackCargo _itemToAdd;
    {
        private _backpackType = (_backpacks select 0) select _forEachIndex;
        private _backpackCount = (_backpacks select 1) select _forEachIndex;
        _newObject addBackpackCargoGlobal [_backpackType, _backpackCount];
    } forEach (_backpacks select 0);

    [_newObject] call YOSHI_capDeliveryMass;

    _newObject
};

YOSHI_addItemsToFabricator = {
	params ["_fabricator", "_itemsToAdd"];

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


		private _spawnItemAction = [
			format ["SpawnItemAction-%1", _classOfItemToSpawn], // Action ID
			format ["Spawn %1", _displayName], // Title
			"\a3\ui_f\data\igui\cfg\simpletasks\types\Download_ca.paa",
			{  // Code executed when the action is used
				params ["_target", "_caller", "_params"];
				private _object = [_target, _caller, _params] call YOSHI_SPAWN_SAVED_ITEM_ACTION;

				[_caller, _object] call ace_dragging_fnc_startCarry;
			},
			{ // Condition for the action to be available
				params ["_vic", "_caller", "_params"];

				true
			},
			{}, // children
			[_fabricator, _itemToSpawn]
		] call ace_interact_menu_fnc_createAction;

		[_fabricator, 0, ["ACE_MainActions"], _spawnItemAction] call ace_interact_menu_fnc_addActionToObject;


	} forEach _itemsToAdd;

};
