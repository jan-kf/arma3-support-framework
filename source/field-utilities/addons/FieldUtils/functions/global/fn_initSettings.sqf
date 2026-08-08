["YFU_playSideMessages", "CHECKBOX",
    ["Play Side Messages", "Plays side chat messages for Field Utilities notifications that use side chat."],
    "Pontifex: Field Utilities",
    true,
    1
] call CBA_fnc_addSetting;

["YFU_showDebugMessages", "CHECKBOX",
    ["Show Debug Messages", "Shows debug messages in systemChat for Field Utilities. When false, messages are diag_log'd instead."],
    "Pontifex: Field Utilities",
    false,
    1
] call CBA_fnc_addSetting;

[
    "YFU_monochromeBaseColor",
    "COLOR",
    [
        "Fabricator UI Base Color",
        "Base monochrome color for the Fabricator UI theme. Darker shades are derived automatically from this color."
    ],
    "Pontifex: Field Utilities",
    [0.15, 0.95, 0.15, 1]
] call CBA_fnc_addSetting;

[
	"YFU_bridge_perPlankBuildDelay",
	"SLIDER",
	[
		"Bridge Per-Plank Build Delay",
		"Delay in seconds between each bridge plank placement during planned builds."
	],
	"Pontifex: Field Utilities",
	[0, 10, 1, 2],
	1
] call CBA_fnc_addSetting;
