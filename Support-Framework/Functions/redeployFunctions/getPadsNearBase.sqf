_nearestPads = nearestObjects [
    (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG"), 
    [
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
    ], 
    ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Radius", 500])
];

_nearestPads // This is the value that the script will return
