_nearestPads = nearestObjects [
    (missionNamespace getVariable "home_base"), 
    [
        "Land_HelipadEmpty_F", 
        "Land_HelipadCircle_F", 
        "Land_HelipadCivil_F", 
        "Land_HelipadRescue_F", 
        "Land_HelipadSquare_F", 
        "Land_JumpTarget_F"
    ], 
    ((missionNamespace getVariable "home_base") getVariable ["Radius", 500])
];

_nearestPads // This is the value that the script will return
