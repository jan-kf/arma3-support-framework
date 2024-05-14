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
		"", // Icon (leave blank for no icon or specify a path)
		{  // Code executed when the action is used
			params ["_target", "_caller", "_params"];
			private _fabricator = _params select 0;
			private _itemToAdd = _params select 1;
			private _originalPos = getPos _fabricator; 
			private _newObject = createVehicle [typeOf _itemToAdd, _originalPos, [], 0, "NONE"]; 
			
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



