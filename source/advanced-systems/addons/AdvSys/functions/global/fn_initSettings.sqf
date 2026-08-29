["YAS_playRadioMessages", "CHECKBOX",
    ["Play Radio Messages", "Plays radio messages for Advanced Systems notifications that use side radio."],
    "Pontifex: Advanced Systems",
    true,
    1
] call CBA_fnc_addSetting;

[
    "YAS_apsAntiDroneEngagementRadius",
    "SLIDER",
    [
        "APS Anti-Drone Engagement Radius",
        "Nearby radius in meters in which APS evaluates lightweight UAVs as possible closing threats."
    ],
    "Pontifex: Advanced Systems",
    [5, 100, 25, 0],
    1
] call CBA_fnc_addSetting;

[
    "YAS_apsAntiDroneMinimumSpeed",
    "SLIDER",
    [
        "APS Anti-Drone Minimum Closing Speed",
        "Minimum relative and radial closing speed in km/h required before a nearby UAV is a physical threat."
    ],
    "Pontifex: Advanced Systems",
    [5, 100, 40, 0],
    1
] call CBA_fnc_addSetting;

["YAS_showDebugMessages", "CHECKBOX",
    ["Show Debug Messages", "Debug messages are always written to the server log. When enabled, they are also shown in systemChat on clients."],
    "Pontifex: Advanced Systems",
    false,
    1
] call CBA_fnc_addSetting;

[
    "YAS_ironDomeEngagementRadius",
    "SLIDER",
    [
        "Iron Dome Engagement Radius",
        "Maximum distance in meters at which Ophanim will engage artillery shells."
    ],
    "Pontifex: Advanced Systems",
    [100, 5000, 1000, 0],
    1
] call CBA_fnc_addSetting;
