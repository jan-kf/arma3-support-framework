params ["_logic", "_id", "_params"];

YOSHI_HOME_BASE_CONFIG_OBJECT = createHashMapObject [[
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

		{
			if (_x isKindOf "Module_F") then {
				if (_x isKindOf "SupportFramework_Base_Arrivals_Module") then {
					_self set ["BaseArriveNode", getPosASL _x];
				};
				if (_x isKindOf "SupportFramework_Base_Departure_Module") then {
					_self set ["BaseDepartNode", getPosASL _x];
				};
			} else {
				if (_x isKindOf "Helicopter") then {
					_x setVariable ["isHeli", true, true];
				};
				_x setVariable ["isRegistered", true, true];
			};
		} forEach (_self get "syncedObjects");

		_self set ["objectArea", _hashMap getVariable ["objectArea", [500, 500, 0, false, 0]]];

		_self set ["location", getPosASL _hashMap];

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_HOME_BASE_CONFIG_OBJECT" }],
	["RequiredItems", { _self get "RequiredItems" }],
	["LzPrefixes", { _self get "LzPrefixes" }],
	["LoiterPrefixes", { _self get "LoiterPrefixes" }],
	["SideHush", { _self get "SideHush" }],
	["VicHush", { _self get "VicHush" }],
	["syncedObjects", { _self get "syncedObjects" }],
	["objectArea", { _self get "objectArea" }],
	["location", { _self get "location" }],
	["BaseArriveNode", { _self get "BaseArriveNode" }],
	["BaseDepartNode", { _self get "BaseDepartNode" }],
	["isInitialized", { true }]
], _logic];