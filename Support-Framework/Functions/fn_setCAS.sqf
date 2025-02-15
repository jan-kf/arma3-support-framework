params ["_logic", "_id", "_params"];

YOSHI_SUPPORT_CAS_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];
		
		// RequiredItems
		[_self, _hashMap, "RequiredItems", YOSHI_DefaultRequiredItems_Reinsert] call YOSHI_initList;

		// CasPrefixes
		[_self, _hashMap, "CasPrefixes", ["target ", "firemission "]] call YOSHI_initList;

		_self set ["syncedObjects", synchronizedObjects _hashMap];

		{
			if (_x isKindOf "Helicopter") then {
				_x setVariable ["isHeli", true, true];
			};
			_x setVariable ["isRegistered", true, true];
			_x setVariable ["isCAS", true, true];
		} forEach (_self get "syncedObjects");

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_SUPPORT_CAS_CONFIG_OBJECT" }],
	["RequiredItems", { _self get "RequiredItems" }],
	["CasPrefixes", { _self get "CasPrefixes" }],
	["syncedObjects", { _self get "syncedObjects" }],
	["isInitialized", { true }]
], _logic];
publicVariable "YOSHI_SUPPORT_CAS_CONFIG_OBJECT";