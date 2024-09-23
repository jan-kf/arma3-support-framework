HELIPADS = [
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

publicVariable "HELIPADS";

HELIPAD_INDEX = [];
publicVariable "HELIPAD_INDEX";

// Event handler for object creation
addMissionEventHandler ["EntityCreated", {
    params ["_entity"];
    if ([_entity] call YOSHI_fnc_isHeliPad) then {
        HELIPAD_INDEX pushBack _entity;
		publicVariable "HELIPAD_INDEX";
    };
}];

// for when 2.18 is released:
// // Event handler for object deletion
// addMissionEventHandler ["EntityDeleted", {
//     params ["_entity"];
// 	if ([_entity] call YOSHI_fnc_isHeliPad) then {
//     	HELIPAD_INDEX = HELIPAD_INDEX - [_entity];
// 		publicVariable "HELIPAD_INDEX";
//     };
// }];
