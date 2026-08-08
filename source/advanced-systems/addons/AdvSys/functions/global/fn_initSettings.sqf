["YAS_playRadioMessages", "CHECKBOX",
    ["Play Radio Messages", "Plays radio messages for Advanced Systems notifications that use side radio."],
    "Pontifex: Advanced Systems",
    true,
    1
] call CBA_fnc_addSetting;

["YAS_showDebugMessages", "CHECKBOX",
    ["Show Debug Messages", "Shows debug messages in systemChat for Advanced Systems. When false, messages are diag_log'd instead."],
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
