YOSHI_isInitialized = {  
    params ["_config"];  
    if (!isNil "_config") then {  
        private _value = _config get "isInitialized";  
        if (typeName _value == "CODE") then { 
            call _value 
        } else { 
            _value  
        };  
    } else {  
        false  
    };  
};

YOSHI_HELIPADS = [
    "Land_HelipadEmpty_F", 
    "Land_HelipadCircle_F", 
    "Land_HelipadCivil_F", 
    "Land_HelipadRescue_F", 
    "Land_HelipadSquare_F", 
    "Land_JumpTarget_F",
    "HeliH",
    "HeliHCivil",
    "Heli_H_civil",
    "HeliHEmpty",
    "HeliHRescue",
    "Heli_H_rescue",
    "PARACHUTE_TARGET"
];

publicVariable "YOSHI_HELIPADS";

YOSHI_DefaultRequiredItems = ["hgun_esd_01_F", "YOSHI_UniversalTerminal"];
YOSHI_DefaultRequiredItems_Reinsert = YOSHI_DefaultRequiredItems + ["YOSHI_ReinsertTerminal"];
YOSHI_DefaultRequiredItems_CAS = YOSHI_DefaultRequiredItems + ["YOSHI_CASTerminal"];
YOSHI_DefaultRequiredItems_Artillery = YOSHI_DefaultRequiredItems + ["YOSHI_ArtilleryTerminal"];
YOSHI_DefaultRequiredItems_Recon = YOSHI_DefaultRequiredItems + ["YOSHI_ReconTerminal"];

YOSHI_MarkersArray = [];
publicVariable "YOSHI_MarkersArray";

YOSHI_ReconMarkersArray = [];
publicVariable "YOSHI_ReconMarkersArray";

YOSHI_ReconMarkersMap = createHashMap;
publicVariable "YOSHI_ReconMarkersMap";

YOSHI_HELIPAD_INDEX = [];
publicVariable "YOSHI_HELIPAD_INDEX";

YOSHI_attachToBelow = { 
	params ["_obj"]; 
	_loc = getPosASL _obj; 
	_locBelow = _loc vectorAdd [0,0,-2]; 

	_hits = lineIntersectsSurfaces [_loc, _locBelow, _obj, objNull, true, 1, "FIRE", "GEOM"]; 

	_hitPos = ((_hits select 0) select 0); 
	_hitObj = ((_hits select 0) select 2); 

	if (!(_hitObj isEqualTo objNull) && !(_hitObj isKindOf "Static")) then {
		private _objectToAttach = _obj; 
		private _targetObject = _hitObj; 
		private _dirObjectToAttach = getDir _objectToAttach;
		private _dirTargetObject = getDir _targetObject;
		private _relativeDir = _dirObjectToAttach - _dirTargetObject;
		_objectToAttach attachTo [_targetObject];
		_objectToAttach setPosASL _hitPos;
		_objectToAttach setDir ( _dirObjectToAttach - _dirTargetObject);
	}; 
};

YOSHI_isArtilleryCapable = {
    params ["_unit"];
    
    // Check if the unit is capable of artillery fire
    // This checks if the unit is an artillery piece by verifying it can accept the doArtilleryFire command
    private _isArtillery = !(_unit isKindOf "Air") && {(_unit isKindOf "LandVehicle") || (_unit isKindOf "Ship")}; // Exclude air units, include land vehicles and ships
    private _canDoArtilleryFire = _isArtillery && {alive _unit} && {getArtilleryAmmo [_unit] isNotEqualTo []}; // Must be alive and have artillery ammo available

    _canDoArtilleryFire // Return true if capable, false otherwise
};

YOSHI_initList = {
    params ["_objSelf", "_hashMap", "_key", "_default"];

    private _listStr = _hashMap getVariable _key;
    private _list = _default;
    if (_listStr != "") then {
        _list = _listStr splitString ", ";
    };
    _objSelf set [_key, _list];
};

private _initParams = [
	["#flags", ["sealed"]],
	["#create", {}],
	["#clone", {}],
	["#delete", {}],
	["#str", {""}],
	["isInitialized", false]
];

YOSHI_HOME_BASE_CONFIG_OBJECT = createHashMapObject [_initParams];
YOSHI_SUPPORT_CAS_CONFIG_OBJECT = createHashMapObject [_initParams];
YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT = createHashMapObject [_initParams];
YOSHI_SUPPORT_RECON_CONFIG_OBJECT = createHashMapObject [_initParams];


// Event handler for object creation
addMissionEventHandler ["EntityCreated", {
    params ["_entity"];
    if ([_entity] call YOSHI_fnc_isHeliPad) then {
        YOSHI_HELIPAD_INDEX pushBack _entity;
		publicVariable "YOSHI_HELIPAD_INDEX";
    };

    // handle adding objects that can be Attached instead of Ace Loading
    if (_entity isKindOf "ReammoBox_F") then {
       [_entity] call YOSHI_fnc_setObjectLoadHandling;
    };

    if (_entity isKindOf "UAV_01_base_F") then {
       _entity addEventHandler ["Engine", {
            params ["_vehicle", "_engineState"];
            if (_engineState) then {detach _vehicle} else {_vehicle call YOSHI_attachToBelow};
        }];
       [_entity, true, [0,1,0]] call ace_dragging_fnc_setDraggable;
       [_entity, true] call ace_dragging_fnc_setCarryable;
    };

    if (unitIsUAV _entity) then {
        _entity setFuelConsumptionCoef 0.1;
    };

    // if (_entity isKindOf "B_UGV_9RIFLES_F") then {
    //     _thread = [_x] spawn YOSHI_detectRockets;

    //     _x setVariable ["YOSHI_APS_Thread", _thread];
        
    // };

}];

// at the moment, the index will not allow for deleted helipads, their last location will be considered available until this is on the main branch:
// for when 2.18 is released:
// Event handler for object deletion
addMissionEventHandler ["EntityDeleted", {
    params ["_entity"];
	if ([_entity] call YOSHI_fnc_isHeliPad) then {
    	YOSHI_HELIPAD_INDEX = YOSHI_HELIPAD_INDEX - [_entity];
		publicVariable "YOSHI_HELIPAD_INDEX";
    };
}];

YOSHI_beamA2B = {
	params ["_posA", "_posB"];
    
	drawLine3D [_posA, _posB, [1, 0, 0, 1], 20];
};

YOSHI_beamVic2Pos = {
	params ["_vic", "_pos"];

	_count = 5;

	// prevent drawing more than once per instance of APS trigger
	_shouldDraw = player getVariable ["YOSHI_DRAW_DEBOUNCE", true];

	if (_shouldDraw) then {
		player setVariable ["YOSHI_DRAW_DEBOUNCE", false];

		while {(alive _vic) && (_count > 0)} do {
			_topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
			[_topOfVic, _pos] call YOSHI_beamA2B;
			sleep 0.05;
			_count = _count - 1;
		};

		player setVariable ["YOSHI_DRAW_DEBOUNCE", true];
	};
};

YOSHI_FW_BASE_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];

        // RequiredItems
		[_self, _hashMap, "RequiredItems", YOSHI_DefaultRequiredItems_Reinsert] call YOSHI_initList;

		_self set ["syncedObjects", synchronizedObjects _hashMap];

		private _fw_units = [];
		{
			if (_x isKindOf "Module_F") then {
				if (_x isKindOf "SupportFramework_Map_Infil_Module") then {
					_self set ["MapArriveNode", getPosASL _x];
				};
				if (_x isKindOf "SupportFramework_Map_Exfil_Module") then {
					_self set ["MapDepartNode", getPosASL _x];
				};
			} else {
				_fw_units pushBack (_x call YOSHI_COPY_VEHICLE);
				deleteVehicleCrew _x;
				deleteVehicle _x;
			};
		} forEach (_self get "syncedObjects");

		_self set ["SavedUnits", _fw_units];
        _self set ["DeployedUnits", []];

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_FW_BASE_CONFIG_OBJECT" }],
    ["RequiredItems", { _self get "RequiredItems" }],
	["SavedUnits", { _self get "SavedUnits" }],
    ["DeployedUnits", { _self get "DeployedUnits" }],
	["MapArriveNode", { _self get ["MapArriveNode", [0,0,0]] }],
	["MapDepartNode", { _self get ["MapDepartNode", [0,0,0]] }],
	["syncedObjects", { _self get "syncedObjects" }],
	["DeployUnit", {
		params ["_self", "_type", ["_caller", objNull]];

		private _units = +(_self get "SavedUnits");
		{
			if ((_x select 0) isEqualTo _type) exitWith {
				_units deleteAt _forEachIndex;
				private _newVehicle = [_self get "MapArriveNode", _x, ((_self get "MapArriveNode") getDir (_self get "MapDepartNode")), 2000] call YOSHI_PASTE_VEHICLE;
				_self set ["SavedUnits", _units];
                _self set ["DeployedUnits", (_self get "DeployedUnits") + [_newVehicle]];
                if (!isNull _caller) then {
                    _newVehicle setVariable ["YOSHI_FW_CALLER", _caller];
                };
                _newVehicle call YOSHI_CREATE_FUEL_CONSUMPTION_THREAD;
				_newVehicle
			};
		} forEach _units;
	}],
	["StashUnit", {
		params ["_self", "_unit"];

		private _units = +(_self get "SavedUnits");
		_units pushBack (_unit call YOSHI_COPY_VEHICLE);
		_self set ["SavedUnits", _units];
        _self set ["DeployedUnits", (_self get "DeployedUnits") - [_unit]];
        private _fuelThread = _unit getVariable ["YOSHI_FUEL_CONSUMPTION_THREAD", 0];
        terminate _fuelThread;
		deleteVehicleCrew _unit;
		deleteVehicle _unit;
	}]
], objNull];

YOSHI_SPAWN_SAVED_ITEM_ACTION = {
    params ["_target", "_caller", "_params"];
    private _fabricator = _params select 0;
    private _itemToAdd = _params select 1;

    private _originalPos = getPosASL _fabricator; 
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

    _newObject
};