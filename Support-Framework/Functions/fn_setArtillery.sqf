params ["_logic", "_id", "_params"];

YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];
		
		// RequiredItems
		[_self, _hashMap, "RequiredItems", YOSHI_DefaultRequiredItems_Reinsert] call YOSHI_initList;

		// ArtilleryPrefixes
		[_self, _hashMap, "ArtilleryPrefixes", ["lz ", "hls "]] call YOSHI_initList;

		_self set ["syncedObjects", synchronizedObjects _hashMap];

		{
			_x setVariable ["isRegistered", true, true];
			_x setVariable ["isArtillery", true, true];
		} forEach (_self get "syncedObjects");

		private _baseSideStr = _hashMap getVariable ["BaseSide", "west"];
		private _baseSide = west;
		private _baseSide = switch (_baseSideStr) do
		{	
			case "civ": { civilian };
			case "guer": { independent };
			case "east": { east };
			default { west }; // Default to "west"
		};
		_self set ["BaseSide", _baseSide];

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT" }],
	["RequiredItems", { _self get "RequiredItems" }],
	["ArtilleryPrefixes", { _self get "ArtilleryPrefixes" }],
	["syncedObjects", { _self get "syncedObjects" }],
	["BaseSide", { _self get "BaseSide" }],
	["isInitialized", { true }]
], _logic];
publicVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT";