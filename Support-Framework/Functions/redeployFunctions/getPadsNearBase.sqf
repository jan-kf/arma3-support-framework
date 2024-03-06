private _padTypes= [
    "Land_HelipadEmpty_F", 
    "Land_HelipadCircle_F", 
    "Land_HelipadCivil_F", 
    "Land_HelipadRescue_F", 
    "Land_HelipadSquare_F", 
    "Land_JumpTarget_F",
    // CUP pads:
    "HeliH",
    "HeliHCivil",
    "Heli_H_civil",
    "HeliHEmpty",
    "HeliHRescue",
    "Heli_H_rescue",
    "PARACHUTE_TARGET"
];

_nearestPads = nearestObjects [
    (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG"), 
    _padTypes, 
    10000
];

_nearestPads select {_x call (missionNamespace getVariable "isAtBase")}// This is the value that the script will return
