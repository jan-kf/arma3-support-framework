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
// 	private _homeBasePos = getPos (missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", objNull]);

// 	// Find all landing pads on the map
// 	private _allLandingPads = [];
// 	{
// 		_allLandingPads append (allMissionObjects _x);
// 	} forEach _landingPadClasses;

// 	// Filter landing pads and check for nearby locations
// 	private _validLandingPads = [];
// 	{
// 		private _landingPadPos = getPos _x;
// 		if (_landingPadPos call call SupportFramework_fnc_isAtBase) then {
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
		private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
		private _homeBaseConfigured = !(isNil "_homeBase");

		if (_homeBaseConfigured) then {
			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};
			private _hasItem = [_requiredItems, _caller] call SupportFramework_fnc_hasItems;
			
		 	_hasItem
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call SupportFramework_fnc_getRedeployActions;
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
		private _casConfig = missionNamespace getVariable ["YOSHI_SUPPORT_CAS_CONFIG", nil];
		private _CasConfigured = !(isNil "_casConfig");

		if (_CasConfigured) then {

			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_SUPPORT_CAS_CONFIG") getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};
			private _hasItem = [_requiredItems, _caller] call SupportFramework_fnc_hasItems;

			_hasItem 
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		private _actions = [_target, _caller, _params] call SupportFramework_fnc_getCasActions;
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
		private _reconConfig = missionNamespace getVariable ["YOSHI_SUPPORT_RECON_CONFIG", nil];
		private _ReconConfigured = !(isNil "_reconConfig");

		if (_ReconConfigured) then {

			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_SUPPORT_RECON_CONFIG") getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};
			private _hasItem = [_requiredItems, _caller] call SupportFramework_fnc_hasItems;

			_hasItem
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		private _actions = [_target, _caller, _params] call SupportFramework_fnc_getReconActions;
		_actions 

	}
] call ace_interact_menu_fnc_createAction;

private _artilleryActions = [
	"ArtilleryActions", "Artillery", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		private _artyPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["ArtilleryPrefixes", ""];
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
		private _artyConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
		private _artyConfigured = !(isNil "_artyConfig");

		if (_artyConfigured) then {
			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["RequiredItems", ""];
			private _requiredItems = [];
			if (_requiredItemsStr != "") then {
				_requiredItems = _requiredItemsStr splitString ", ";
			} else {
				_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
			};

			private _hasItem = [_requiredItems, _caller] call SupportFramework_fnc_hasItems;
			
			_hasItem

		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call SupportFramework_fnc_getArtyTargetActions;
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
		[_target, _caller, _params] call SupportFramework_fnc_getRedeployActions;
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
		private _actions = [_target, _caller, _params] call SupportFramework_fnc_getCasActions;
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
		private _actions = [_target, _caller, _params] call SupportFramework_fnc_getReconActions;
		_actions 

	}
] call ace_interact_menu_fnc_createAction;

private _artilleryActionsZeus = [
	"ArtilleryActions", "Artillery", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		private _artyPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["ArtilleryPrefixes", ""];
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
		[_target, _caller, _params] call SupportFramework_fnc_getArtyTargetActions;
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

		private _reconPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_RECON_CONFIG") getVariable ["ReconPrefixes", ""];
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

							[_vic, getMarkerPos _marker, _caller] remoteExec ["SupportFramework_fnc_requestFieldRecon", 2];
						}, 
						{
							params ["_target", "_caller", "_args"];
							private _vic = _args select 0;
							// // Condition code here
							private _reconConfig = missionNamespace getVariable ["YOSHI_SUPPORT_RECON_CONFIG", nil];
							private _ReconConfigured = !(isNil "_reconConfig");
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
		private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
		private _homeBaseConfigured = !(isNil "_homeBase");
		if (_homeBaseConfigured) then {
			private _atBase = _target call SupportFramework_fnc_isAtBase;
			_atBase
		} else {
			false
		};
	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call SupportFramework_fnc_getVicActions;
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
		private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
		private _homeBaseConfigured = !(isNil "_homeBase");

		private _artilleryConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
		private _artilleryConfigured = !(isNil "_artilleryConfig");

		if (_homeBaseConfigured && _artilleryConfigured) then {
			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
			_canDoArtilleryFire
		} else {
			false
		};

	},
	{
		params ["_target", "_caller", "_params"];
		[_target, _caller, _params] call SupportFramework_fnc_getVicActions;
	}
] call ace_interact_menu_fnc_createAction;

// Add the actions to the classes that might have arty support
["LandVehicle", 0, ["ACE_MainActions"], _artilleryVicActions, true] call ace_interact_menu_fnc_addActionToClass;
["Ship", 0, ["ACE_MainActions"], _artilleryVicActions, true] call ace_interact_menu_fnc_addActionToClass;
