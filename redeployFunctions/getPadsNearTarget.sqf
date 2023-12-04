params ["_target"];

_nearestPads = nearestObjects [
    _target, 
    [
        "Land_HelipadEmpty_F", 
        "Land_HelipadCircle_F", 
        "Land_HelipadCivil_F", 
        "Land_HelipadRescue_F", 
        "Land_HelipadSquare_F", 
        "Land_JumpTarget_F"
    ], 
    250
];

_nearestPads // This is the value that the script will return
