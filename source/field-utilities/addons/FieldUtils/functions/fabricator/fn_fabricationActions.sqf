/*
May the favor of the Lord our God rest on us
And may the work of our hands prosper—
indeed, may the work of our hands prosper.
(Psalm 90:17)
Amen.
*/

YFU_registerFabricatorMenuActions = {
	private _fabricatorConfigured = !(isNil "YOSHI_FABRICATOR");
	if (!_fabricatorConfigured) exitWith {};

	private _registered = uiNamespace getVariable ["YFU_registered_fabricator_actions", []];
	private _syncedFabricatorObjects = synchronizedObjects YOSHI_FABRICATOR;
	{
		private _fabricatorObject = _x;
		private _fabricatorId = netId _fabricatorObject;
		if !(_fabricatorId in _registered) then {
			private _openFabricatorAction = [
				format ["openFabricatorAction-%1", _fabricatorId],
				"Open Fabricator Menu",
				"\a3\ui_f\data\igui\cfg\simpletasks\types\documents_ca.paa",
				{
					params ["_target", "_caller", "_actionId", "_arguments"];
					[_target, false, mapGridPosition _caller] call YFU_UI_OpenFabricator;
				},
				{
					params ["_target", "_caller", "_actionId", "_arguments"];
					true
				}
			] call ace_interact_menu_fnc_createAction;

			[_fabricatorObject, 0, ["ACE_MainActions"], _openFabricatorAction] call ace_interact_menu_fnc_addActionToObject;
			_registered pushBack _fabricatorId;
		};
	} forEach _syncedFabricatorObjects;

	uiNamespace setVariable ["YFU_registered_fabricator_actions", _registered];
};

YFU_initFabricatorItems = {
	[] spawn {
		waitUntil {
			!(isNil "YOSHI_FABRICATOR")
		};
		call YFU_registerFabricatorMenuActions;
	};
};

YFU_initVirtualInventoryActions = {
	private _virtualInventoryActions = [
		"zenInventoryActions", "Open Virtual Inventory", "\a3\ui_f\data\igui\cfg\simpletasks\types\rearm_ca.paa",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code
			[_target] call zen_inventory_fnc_configure;
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Conditional Code
			private _isNearFabricator = false;
			// The Fabricator module's "Enable local virtual inventory" attribute
			// gates this. It is the escape hatch for stock a mission maker forgot
			// to synchronize, so it is deliberately optional per mission.
			private _inventoryEnabled = missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", true];
			private _fabricatorConfigured = !(isNil "YOSHI_FABRICATOR") && {_inventoryEnabled};
			if (_fabricatorConfigured) then {
				private _syncedFabricatorObjects = synchronizedObjects YOSHI_FABRICATOR;
				{
					if (_target distance _x < 20) exitWith {
						_isNearFabricator = true;
					};
				} forEach _syncedFabricatorObjects;
			};
			_isNearFabricator
		}
	] call ace_interact_menu_fnc_createAction;

	["ReammoBox_F", 0, ["ACE_MainActions"], _virtualInventoryActions, true] call ace_interact_menu_fnc_addActionToClass;
};
