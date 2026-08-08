#include "\a3\ui_f\hpp\defineDIKCodes.inc"

["YSF_enableTablet", "CHECKBOX",
    ["Tablet Required", "When enabled, you'll need the VIGIL Tablet (or any of the Rugged Tablets) in order to use the combat tablet. When disabled, it will always be available even with an empty inventory"],
    "Pontifex: VIGIL Support Tablet",
    true,
    1
] call CBA_fnc_addSetting;

["YSF_playRadioMessages", "CHECKBOX",
    ["Play Radio Messages", "Plays radio messages for task updates, helpful feedback that a unit accepted the task or is done."],
    "Pontifex: VIGIL Support Tablet",
    true,
    1
] call CBA_fnc_addSetting;

["YSF_playSideMessages", "CHECKBOX",
    ["Play Side Messages", "Plays side chat messages for task updates, helpful feedback that a unit accepted the task or is done."],
    "Pontifex: VIGIL Support Tablet",
    true,
    1
] call CBA_fnc_addSetting;

["YSF_showDebugMessages", "CHECKBOX",
    ["Show Debug Messages", "Shows debug messages in systemChat, useful for troubleshooting issues. When false, all messages are diag_log'd instead."],
    "Pontifex: VIGIL Support Tablet",
    false,
    1
] call CBA_fnc_addSetting;

[
    "YSF_monochromeBaseColor",
    "COLOR",
    ["Tablet Base Color", "This is the base color for the mono-chrome display. All iterations of the color, such as darker variants will automatically be created, so it's recommended to leave alpha as 1.00, and use some combination of full red, green, blue so that the display is bright enough."],
    "Pontifex: VIGIL Support Tablet",
    [0, 1, 0, 1]
] call CBA_fnc_addSetting;

[
    "YSF_laserVizColor",
    "COLOR",
    ["Laser Visualization Color", "This is the color for the IR laser visualization. It's recommended to use a bright color with an alpha of 1.00 so that it's easily visible."],
    "Pontifex: VIGIL Support Tablet",
    [0, 1, 0, 1]
] call CBA_fnc_addSetting;

["Pontifex: VIGIL Support Tablet", "openTablet",
    ["Open VIGIL Tablet", "Open the VIGIL support tablet"],
    {
        // key down
        [] call YSF_UI_OpenTablet;
    },
    {
        // key up (optional)
    },
    [DIK_HOME, [false, true, false]]   // [key, [shift, ctrl, alt]]
] call CBA_fnc_addKeybind;
