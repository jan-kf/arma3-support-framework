params ["_logic", "_id", "_params"];

YOSHI_EXTRA_BASE_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];
		
		// RequiredItems
		[_self, _hashMap, "RequiredItems", YOSHI_DefaultRequiredItems_Reinsert] call YOSHI_initList;

		// LzPrefixes
		[_self, _hashMap, "LzPrefixes", ["lz ", "hls "]] call YOSHI_initList;

		// LoiterPrefixes
		[_self, _hashMap, "LoiterPrefixes", ["loiter"]] call YOSHI_initList;

		// SideHush
		_self set ["SideHush", _hashMap getVariable ["SideHush", false]];

		// VicHush
		_self set ["VicHush", _hashMap getVariable ["VicHush", false]];

		_self set ["syncedObjects", synchronizedObjects _hashMap];

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_EXTRA_BASE_CONFIG_OBJECT" }],
	["isInitialized", { true }]
], _logic];
publicVariable "YOSHI_EXTRA_BASE_CONFIG_OBJECT";