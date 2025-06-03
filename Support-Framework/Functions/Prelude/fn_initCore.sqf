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
    private _canDoArtilleryFire = (_isArtillery && (alive _unit) && (getArtilleryAmmo [_unit] isNotEqualTo [])) || ((typeOf _unit) isEqualTo "B_Ship_MRLS_01_F"); // Must be alive and have artillery ammo available

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
        _entity setUnitTrait ["camouflageCoef", 0.3];
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
	params ["_posA", "_posB", ["_color", [1, 0, 0, 1]], ["_thickness", 20]];
    
	drawLine3D [_posA, _posB, _color, _thickness];
};

YOSHI_beamVic2Pos = {
	params ["_vic", "_pos", ["_pulseCount", 5], ["_color", [1, 0, 0, 1]], ["_thickness", 20]];

	_count = _pulseCount;

	// prevent drawing more than once per instance of APS trigger
	_shouldDraw = player getVariable ["YOSHI_DRAW_DEBOUNCE", true];

	if (_shouldDraw) then {
		player setVariable ["YOSHI_DRAW_DEBOUNCE", false];

		while {(alive _vic) && (_count > 0)} do {
			_topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
			[_topOfVic, _pos, _color, _thickness] call YOSHI_beamA2B;
			sleep 0.05;
			_count = _count - 1;
		};

		player setVariable ["YOSHI_DRAW_DEBOUNCE", true];
	};
};

YOSHI_findNearestBorderPos = {
    params ["_pos"];

    private _mapSize = worldSize;
    private _buffer = 100;

    private _x = _pos select 0;
    private _y = _pos select 1;

    private _distWest = _x;
    private _distEast = _mapSize - _x;
    private _distSouth = _y;
    private _distNorth = _mapSize - _y;

    private _minDist = selectMin [_distWest, _distEast, _distSouth, _distNorth];

    private _borderX = _x;
    private _borderY = _y;

    if (_minDist == _distWest) then { _borderX = -_buffer; }; // Move 100m past West
    if (_minDist == _distEast) then { _borderX = _mapSize + _buffer; }; // Move 100m past East
    if (_minDist == _distSouth) then { _borderY = -_buffer; }; // Move 100m past South
    if (_minDist == _distNorth) then { _borderY = _mapSize + _buffer; }; // Move 100m past North

    [_borderX, _borderY, _pos select 2]
};

YOSHI_SPAWN_SAVED_ITEM_ACTION = {
    params ["_target", "_caller", "_params"];
    private _fabricator = _params select 0;
    private _itemToAdd = _params select 1;

    private _newObject = createVehicle [typeOf _itemToAdd, _fabricator, [], 0, "NONE"]; 
    
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

YOSHI_GET_DIRECTION = {
    params ["_degree"];

    _degree = _degree % 360;

    private _directions = [
        "North",
        "Northeast",
        "East",
        "Southeast",
        "South",
        "Southwest",
        "West",
        "Northwest"
    ];

    private _index = floor ((_degree + 22.5) / 45) % 8;
    private _direction = _directions select _index;

    _direction

};

YOSHI_GET_FALL_TIME = {
    params ["_initialHeight", "_finalHeight"];

    private _g = 9.81;

    private _distance = _initialHeight - _finalHeight;
    private _time = sqrt((2 * _distance) / _g);

    (round (_time * 100))/100

};


YOSHI_playVehicleSoundLocal = {
    params ["_soundName", "_source"];

    private _soundSource = _source say3D [_soundName, 1000, 1];
	_source setVariable ["YOSHI_soundSource", _soundSource];

};

YOSHI_playVehicleSoundGlobal = {
    params ["_soundName", "_source"];

    [[_soundName, _source], YOSHI_playVehicleSoundLocal] remoteExec ["call", 0];

};

YOSHI_stopVehicleSoundGlobal = {
    params ["_source"];

	private _soundSource = _source getVariable ["YOSHI_soundSource", objNull];
    deleteVehicle _soundSource;

};