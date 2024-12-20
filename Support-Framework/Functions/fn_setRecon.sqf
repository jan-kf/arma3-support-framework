params ["_logic", "_id", "_params"];

YOSHI_SUPPORT_RECON_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];
		
		// RequiredItems
		[_self, _hashMap, "RequiredItems", YOSHI_DefaultRequiredItems_Reinsert] call YOSHI_initList;

		// ReconPrefixes
		[_self, _hashMap, "ReconPrefixes", ["recon ", "rp ", "watch "]] call YOSHI_initList;

		_self set ["TaskTime", _hashMap getVariable ["TaskTime", 300]];
		_self set ["Interval", _hashMap getVariable ["Interval", 5]];
		_self set ["ShowNames", _hashMap getVariable ["ShowNames", false]];
		// _self set ["HasSat", _hashMap getVariable ["HasSat", false]];
		_self set ["HasHyperSpectralSensors", _hashMap getVariable ["HasHyperSpectralSensors", false]];

		_self set ["syncedObjects", synchronizedObjects _hashMap];
		{
			_x setVariable ["isRegistered", true, true];
			_x setVariable ["isRecon", true, true];
		} forEach (_self get "syncedObjects");

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_SUPPORT_RECON_CONFIG_OBJECT" }],
	["RequiredItems", { _self get "RequiredItems" }],
	["ReconPrefixes", { _self get "ReconPrefixes" }],
	["TaskTime", { _self get "TaskTime" }],
	["Interval", { _self get "Interval" }],
	["ShowNames", { _self get "ShowNames" }],
	// ["HasSat", { _self get "HasSat" }],
	["HasHyperSpectralSensors", { _self get "HasHyperSpectralSensors" }],
	["syncedObjects", { _self get "syncedObjects" }],
	["isInitialized", { true }]
], _logic];