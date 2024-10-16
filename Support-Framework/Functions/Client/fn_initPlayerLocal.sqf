// TODO: maybe add support for landing pads that already exist in the map.
// private _getBuiltInPads = {
// 	// Define the landing pad classes
// 	private _landingPadClasses = [
// 		"Land_HelipadEmpty_F", 
// 		"Land_HelipadCircle_F", 
// 		"Land_HelipadCivil_F", 
// 		"Land_HelipadRescue_F", 
// 		"Land_HelipadSquare_F", 
// 		"Land_JumpTarget_F",
// 		// CUP pads:
// 		"HeliH",
// 		"HeliHCivil",
// 		"Heli_H_civil",
// 		"HeliHEmpty",
// 		"HeliHRescue",
// 		"Heli_H_rescue",
// 		"PARACHUTE_TARGET"
// 	];

// 	// Define the location types
// 	private _locationTypes = [
// 		"Airport", "CityCenter", "CivilDefense", "CulturalProperty",
// 		"DangerousForces", "FlatArea", "FlatAreaCity", "FlatAreaCitySmall",
// 		"Name", "NameCity", "NameCityCapital", "NameLocal", "NameMarine",
// 		"NameVillage", "SafetyZone", "Strategic", "StrongpointArea"
// 	];

// 	// Get the position of YOSHI_HOME_BASE_CONFIG
// 	private _homeBasePos = getPosWorld YOSHI_HOME_BASE_CONFIG;

// 	// Find all landing pads on the map
// 	private _allLandingPads = [];
// 	{
// 		_allLandingPads append (allMissionObjects _x);
// 	} forEach _landingPadClasses;

// 	// Filter landing pads and check for nearby locations
// 	private _validLandingPads = [];
// 	{
// 		private _landingPadPos = getPosWorld _x;
// 		if (_landingPadPos call call YOSHI_fnc_isAtBase) then {
// 			private _nearbyLocations = nearestLocations [_landingPadPos, _locationTypes, 50];
// 			if (count _nearbyLocations > 0) then {
// 				private _nearestLocation = _nearbyLocations select 0;
// 				private _locationName = text _nearestLocation;
// 				if (_locationName != "") then {
// 					_validLandingPads pushBack _x;
// 				};
// 			};
// 		};
// 	} forEach _allLandingPads;

// 	// Return the array of valid landing pads
// 	_validLandingPads

// };


private _redeploymentActions = [
	"RedeploymentActions", "Redeployment", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		// Retrieve the custom argument value
		private _homeBaseConfigured = !(isNil "YOSHI_HOME_BASE_CONFIG");

		if (_homeBaseConfigured) then {
			private _requiredItemsStr = YOSHI_HOME_BASE_CONFIG getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};
			private _hasItem = [_requiredItems, _caller] call YOSHI_fnc_hasItems;
			
		 	_hasItem
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call YOSHI_fnc_getRedeployActions;
	}
] call ace_interact_menu_fnc_createAction;

private _casActions = [
	"CasActions", "CAS Support", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		// Retrieve the custom argument value
		private _CasConfigured = !(isNil "YOSHI_SUPPORT_CAS_CONFIG");

		if (_CasConfigured) then {

			private _requiredItemsStr = YOSHI_SUPPORT_CAS_CONFIG getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};
			private _hasItem = [_requiredItems, _caller] call YOSHI_fnc_hasItems;

			_hasItem 
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		private _actions = [_target, _caller, _params] call YOSHI_fnc_getCasActions;
		_actions 

	}
] call ace_interact_menu_fnc_createAction;

private _reconActions = [
	"ReconActions", "Recon Support", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		// Retrieve the custom argument value
		private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");

		if (_ReconConfigured) then {

			private _requiredItemsStr = YOSHI_SUPPORT_RECON_CONFIG getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};
			private _hasItem = [_requiredItems, _caller] call YOSHI_fnc_hasItems;

			_hasItem
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		private _actions = [_target, _caller, _params] call YOSHI_fnc_getReconActions;
		_actions 

	}
] call ace_interact_menu_fnc_createAction;

private _artilleryActions = [
	"ArtilleryActions", "Artillery", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		private _artyPrefixStr = YOSHI_SUPPORT_ARTILLERY_CONFIG getVariable ["ArtilleryPrefixes", ""];
		private _artyPrefixes = [];
		if (_artyPrefixStr != "") then {
			_artyPrefixes = _artyPrefixStr splitString ", ";
		} else {
			_artyPrefixes = ["target ", "firemission "]; // default value -- hard fallback
		};

		hint format["Awaiting orders, searching for markers prefixed with %1...", _artyPrefixes];

		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		// Retrieve the custom argument value
		private _artyConfigured = !(isNil "YOSHI_SUPPORT_ARTILLERY_CONFIG");

		if (_artyConfigured) then {
			private _requiredItemsStr = YOSHI_SUPPORT_ARTILLERY_CONFIG getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};

			private _hasItem = [_requiredItems, _caller] call YOSHI_fnc_hasItems;
			
			_hasItem

		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call YOSHI_fnc_getArtyTargetActions;
	},
	"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
	4, // 8: Distance <NUMBER>
	[false, false, false, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
] call ace_interact_menu_fnc_createAction;

[player, 1, ["ACE_SelfActions"], _redeploymentActions] call ace_interact_menu_fnc_addActionToObject;
[player, 1, ["ACE_SelfActions"], _casActions] call ace_interact_menu_fnc_addActionToObject;
[player, 1, ["ACE_SelfActions"], _artilleryActions] call ace_interact_menu_fnc_addActionToObject;
[player, 1, ["ACE_SelfActions"], _reconActions] call ace_interact_menu_fnc_addActionToObject;

private _redeploymentActionsZeus = [
	"RedeploymentActions", "Redeployment", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		true
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call YOSHI_fnc_getRedeployActions;
	}
] call ace_interact_menu_fnc_createAction;

private _casActionsZeus = [
	"CasActions", "CAS Support", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		true
	},
	{
		params ["_target", "_caller", "_params"];
		private _actions = [_target, _caller, _params] call YOSHI_fnc_getCasActions;
		_actions 

	}
] call ace_interact_menu_fnc_createAction;

private _reconActionsZeus = [
	"ReconActions", "Recon Support", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		true
	},
	{
		params ["_target", "_caller", "_params"];
		private _actions = [_target, _caller, _params] call YOSHI_fnc_getReconActions;
		_actions 

	}
] call ace_interact_menu_fnc_createAction;

private _artilleryActionsZeus = [
	"ArtilleryActions", "Artillery", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		private _artyPrefixStr = YOSHI_SUPPORT_ARTILLERY_CONFIG getVariable ["ArtilleryPrefixes", ""];
		private _artyPrefixes = [];
		if (_artyPrefixStr != "") then {
			_artyPrefixes = _artyPrefixStr splitString ", ";
		} else {
			_artyPrefixes = ["target ", "firemission "]; // default value -- hard fallback
		};

		hint format["Awaiting orders, searching for markers prefixed with %1...", _artyPrefixes];

		true
	}, 
	{
		true
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call YOSHI_fnc_getArtyTargetActions;
	},
	"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
	4, // 8: Distance <NUMBER>
	[false, false, false, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
] call ace_interact_menu_fnc_createAction;


[["ACE_ZeusActions"], _redeploymentActionsZeus] call ace_interact_menu_fnc_addActionToZeus;
[["ACE_ZeusActions"], _casActionsZeus] call ace_interact_menu_fnc_addActionToZeus;
[["ACE_ZeusActions"], _artilleryActionsZeus] call ace_interact_menu_fnc_addActionToZeus;
[["ACE_ZeusActions"], _reconActionsZeus] call ace_interact_menu_fnc_addActionToZeus;

private _uavAction = [
	"UAV_field_task", // Action ID
	"Field Actions", // Title
	"", // Icon (leave blank for no icon or specify a path)
	{}, // Code executed when the action is used
	{ // Condition for the action to be available
		params ["_vic", "_caller", "_params"];

		unitIsUAV _vic
	}, 
	{
		params ["_vic", "_caller", "_params"];
		// RECON search details
		private _actions = [];

		private _reconPrefixStr = YOSHI_SUPPORT_RECON_CONFIG getVariable ["ReconPrefixes", ""];
		private _reconPrefixes = [];
		if (_reconPrefixStr != "") then {
			_reconPrefixes = _reconPrefixStr splitString ", ";
		} else {
			_reconPrefixes = ["recon ", "rp ", "watch "]; // default value -- hard fallback
		};

		{ // add all valid markers as valid locations
			
			// marker details
			private _marker = _x;
			private _markerName = markerText _marker;
			private _displayName = toLower _markerName;
			
			{
				private _prefix = toLower _x;
				if (_displayName find _prefix == 0) then {
					private _uavFieldAction = [
						format["reconTo-%2", _marker], format["Request Recon at %1", _markerName], "",
						{
							// statement 
							params ["_target", "_caller", "_args"];
							private _vic = _args select 0;
							private _marker = _args select 1;

							[_vic, getMarkerPos _marker, _caller] remoteExec ["YOSHI_fnc_requestFieldRecon", 2];
						}, 
						{
							params ["_target", "_caller", "_args"];
							private _vic = _args select 0;
							// // Condition code here
							private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
							private _isUAV = unitIsUAV _vic;
							_ReconConfigured && _isUAV
						},
						{}, // 5: Insert children code <CODE> (Optional)
						[_vic, _marker] // 6: Action parameters <ANY> (Optional)
					] call ace_interact_menu_fnc_createAction;
					_actions pushBack [_uavFieldAction, [], _vic];
				};
			} forEach _reconPrefixes;

		} forEach allMapMarkers;

		// Add more field actions:
		private _uavFieldActionIED = [
			"uavIED-action", "Attach IED", "",
			{
				// statement 
				params ["_target", "_caller", "_args"];
				private _vic = _args select 0;
				// attach the ied to the drone here

				_vic setVariable ["YOSHI_UavHasIED", true, true];
				_vic say3D ["DufflebagShuffle", 100, 1];
				_explosive = createVehicle ["ModuleExplosive_SatchelCharge_F", [0,0,0], [], 0, "CAN_COLLIDE"];
				_explosive attachTo [_vic, [0,0,0.1]];

				_boom = [ 
					"uavDetonate",  
					"Detonate",  
					"",  
					{ 
						params ["_target", "_caller", "_args"];
						private _vic = _args select 0;
						private _explosive = _args select 1;
						_explosive setDamage 1;
					},  
					{ 
						true 
					}, {}, [_vic, _explosive] 
				] call ace_interact_menu_fnc_createAction; 
				
				[_vic, 1, ["ACE_SelfActions"], _boom] call ace_interact_menu_fnc_addActionToObject;

				_vic addEventHandler ["Killed", {
					params ["_unit", "_killer", "_instigator", "_useEffects"];
					{_x setDamage 1;} forEach (attachedObjects _unit);
				}];

			}, 
			{
				params ["_target", "_caller", "_args"];
				private _vic = _args select 0;
				// Condition code here
				private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
				private _isUAV = unitIsUAV _vic;
				private _vicHasIED = _vic getVariable ["YOSHI_UavHasIED", false];
				private _vicHasMortar = _vic getVariable ["YOSHI_UavHasMortar", false];
				_ReconConfigured && _isUAV && !_vicHasIED && !_vicHasMortar
			},
			{}, // 5: Insert children code <CODE> (Optional)
			[_vic] // 6: Action parameters <ANY> (Optional)
		] call ace_interact_menu_fnc_createAction;
		_actions pushBack [_uavFieldActionIED, [], _vic];

		private _uavFieldActionMortar = [
			"uavIED-action", "Attach 82mm Mortar Round", "",
			{
				// statement 
				params ["_target", "_caller", "_args"];
				private _vic = _args select 0;
				// attach the ied to the drone here

				_vic setVariable ["YOSHI_UavHasMortar", true, true];
				_vic say3D ["DufflebagShuffle", 100, 0.75];
				_explosive = createVehicle ["Sh_82mm_AMOS", [0,0,0], [], 0, "CAN_COLLIDE"];
				_explosive attachTo [_vic, [0,0.2,0]];

				_boom = [ 
					"uavDetach82mm",  
					"Release 82mm",  
					"",  
					{ 
						params ["_target", "_caller", "_args"];
						private _vic = _args select 0;
						private _explosive = (attachedObjects _vic) select 0;
						detach _explosive;
					},  
					{ 
						params ["_target", "_caller", "_args"];
						private _vic = _args select 0;
						(count (attachedObjects _vic)) > 0 
					}, {}, [_vic, _explosive] 
				] call ace_interact_menu_fnc_createAction; 
				
				[_vic, 1, ["ACE_SelfActions"], _boom] call ace_interact_menu_fnc_addActionToObject;

				_vic addEventHandler ["Killed", {
					params ["_unit", "_killer", "_instigator", "_useEffects"];
					{ detach _x;} forEach (attachedObjects _unit);
				}];

			}, 
			{
				params ["_target", "_caller", "_args"];
				private _vic = _args select 0;
				// Condition code here
				private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
				private _isUAV = unitIsUAV _vic;
				private _vicHasMortar = _vic getVariable ["YOSHI_UavHasMortar", false];
				private _vicHasIED = _vic getVariable ["YOSHI_UavHasIED", false];
				_ReconConfigured && _isUAV && !_vicHasMortar && !_vicHasIED
			},
			{}, // 5: Insert children code <CODE> (Optional)
			[_vic] // 6: Action parameters <ANY> (Optional)
		] call ace_interact_menu_fnc_createAction;
		_actions pushBack [_uavFieldActionMortar, [], _vic];

		private _uavFieldActionGrenade = [
			"uavGrenade-action", "Attach Grenade", "",
			{
				// statement 
				params ["_target", "_caller", "_args"];
				private _vic = _args select 0;
				// attach the Grenade to the drone here
				_vic setVariable ["YOSHI_UavGrenadeCount", 2, true];
				_vic say3D ["DufflebagShuffle", 100, 2];
				// _explosive = createVehicle ["ModuleExplosive_SatchelCharge_F", [0,0,0], [], 0, "CAN_COLLIDE"];
				// _explosive attachTo [_vic, [0,0,0.1]];

				_drop = [ 
					"dropGrenade",  
					"Drop Grenade",  
					"",  
					{ 
						params ["_target", "_caller", "_args"];
						private _vic = _args select 0;
						"GrenadeHand" createVehicle ((getPosATL _vic) vectorAdd [0,0,-0.1]);
						private _vicGrenadeCount = _vic getVariable ["YOSHI_UavGrenadeCount", 1];
						_vic setVariable ["YOSHI_UavGrenadeCount", _vicGrenadeCount-1, true];
					},  
					{ 
						params ["_target", "_caller", "_args"];
						private _vic = _args select 0;
						_vic getVariable ["YOSHI_UavGrenadeCount", 0] > 0; 
					}, {}, [_vic] 
				] call ace_interact_menu_fnc_createAction; 
				
				[_vic, 1, ["ACE_SelfActions"], _drop] call ace_interact_menu_fnc_addActionToObject;

			}, 
			{
				params ["_target", "_caller", "_args"];
				private _vic = _args select 0;
				// Condition code here
				private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
				private _isUAV = unitIsUAV _vic;
				private _vicHasGrenades = _vic getVariable ["YOSHI_UavGrenadeCount", 0] > 0;
				_ReconConfigured && _isUAV && !_vicHasGrenades
			},
			{}, // 5: Insert children code <CODE> (Optional)
			[_vic] // 6: Action parameters <ANY> (Optional)
		] call ace_interact_menu_fnc_createAction;
		_actions pushBack [_uavFieldActionGrenade, [], _vic];
			
		_actions
	}
] call ace_interact_menu_fnc_createAction;

["AllVehicles", 0, ["ACE_MainActions"], _uavAction, true] call ace_interact_menu_fnc_addActionToClass;

private _heliActions = [
	"HelicopterActions", "Support Actions", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _homeBaseConfigured = !(isNil "YOSHI_HOME_BASE_CONFIG");
		if (_homeBaseConfigured) then {
			private _atBase = _target call YOSHI_fnc_isAtBase;
			_atBase
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call YOSHI_fnc_getVicActions;
	}
] call ace_interact_menu_fnc_createAction;

// Add the actions to the Helicopter class
["Helicopter", 0, ["ACE_MainActions"], _heliActions, true] call ace_interact_menu_fnc_addActionToClass;


private _artilleryVicActions = [
	"ArtilleryVicActions", "Support Actions", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _homeBaseConfigured = !(isNil "YOSHI_HOME_BASE_CONFIG");
		private _artilleryConfigured = !(isNil "YOSHI_SUPPORT_ARTILLERY_CONFIG");

		if (_homeBaseConfigured && _artilleryConfigured) then {
			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
			_canDoArtilleryFire
		} else {
			false
		};

	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call YOSHI_fnc_getVicActions;
	}
] call ace_interact_menu_fnc_createAction;

// Add the actions to the classes that might have arty support
["LandVehicle", 0, ["ACE_MainActions"], _artilleryVicActions, true] call ace_interact_menu_fnc_addActionToClass;
["Ship", 0, ["ACE_MainActions"], _artilleryVicActions, true] call ace_interact_menu_fnc_addActionToClass;


private _virtualStorageConfigured = !(isNil "YOSHI_VIRTUAL_STORAGE");
private _fabricatorConfigured = !(isNil "YOSHI_FABRICATOR");
if (_virtualStorageConfigured && _fabricatorConfigured) then {
	private _syncedVirtualStorageObjects = synchronizedObjects YOSHI_VIRTUAL_STORAGE;
	private _syncedFabricatorObjects = synchronizedObjects YOSHI_FABRICATOR;
	{
		[_x, _syncedVirtualStorageObjects] call YOSHI_fnc_addItemsToFabricator;
	} forEach _syncedFabricatorObjects;
};