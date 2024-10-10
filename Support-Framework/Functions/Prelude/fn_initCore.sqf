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

YOSHI_MarkersArray = [];
publicVariable "YOSHI_MarkersArray";

YOSHI_HELIPAD_INDEX = [];
publicVariable "YOSHI_HELIPAD_INDEX";

// Event handler for object creation
addMissionEventHandler ["EntityCreated", {
    params ["_entity"];
    if ([_entity] call YOSHI_fnc_isHeliPad) then {
        YOSHI_HELIPAD_INDEX pushBack _entity;
		publicVariable "YOSHI_HELIPAD_INDEX";
    };
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
