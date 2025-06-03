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



