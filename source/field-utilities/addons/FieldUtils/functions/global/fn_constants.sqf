YOSHI_TowingLookupTable = createHashMapFromArray [
	["CUP_Ridgback_Base", [[[0.27,2.92,0.65], [-0.27,2.92,0.65]],[[0,-2.79,1]]]],
	["CUP_Wolfhound_Base", [[[0.27,2.92,0.65], [-0.27,2.92,0.65]],[[0,-4.13,1.2]]]],
	["UK3CB_BAF_Panther_Base", [[[0.427,2.07,-1.2], [-0.427,2.07,-1.2]],[[0,-2.39,-2]]]],
	["UK3CB_BAF_Jackal2_L111A1_Base", [[[0.238,2.7,-2], [-0.573,2.7,-2]],[[0,-2.54,-2]]]],
	["UK3CB_BAF_Jackal2_L134A1_Base", [[[0.238,2.7,-2], [-0.573,2.7,-2]],[[0,-2.54,-2]]]],
	["UK3CB_BAF_Coyote_Passenger_L134A1_D", [[[0.455,3.68,-2], [-0.355,3.68,-2]],[[0,-2.735,-2]]]],
	["UK3CB_BAF_Coyote_Passenger_L111A1_D", [[[0.455,3.68,-2], [-0.355,3.68,-2]],[[0,-2.735,-2]]]],
	["UK3CB_BAF_MAN_HX60_Cargo_Base", [[[0.63,6.95,-1.38], [-0.54,6.95,-1.38]],[[0,-0.67,-1.55]]]],
	["UK3CB_BAF_MAN_HX60_Transport_Base", [[[0.63,4,-1.38], [-0.54,4,-1.38]],[[0,-3.2,-1.55]]]],
	["UK3CB_BAF_MAN_HX60_Fuel_Base", [[[0.63,4,-1.38], [-0.54,4,-1.38]],[[0,-3.2,-1.55]]]],
	["UK3CB_BAF_MAN_HX60_Repair_Base", [[[0.63,4,-1.38], [-0.54,4,-1.38]],[[0,-3.2,-1.55]]]],
	["UK3CB_BAF_MAN_HX58_Cargo_Base", [[[0.604,8.6,-1.38], [-0.54,8.6,-1.38]],[[0,-0.85,-1.55]]]],
	["UK3CB_BAF_MAN_HX58_Transport_Base", [[[0.604,4.895,-1.38], [-0.54,4.89,-1.38]],[[0,-4.2,-1.55]]]],
	["UK3CB_BAF_MAN_HX58_Fuel_Base", [[[0.604,4.895,-1.38], [-0.54,4.89,-1.38]],[[0,-4.2,-1.55]]]],
	["UK3CB_BAF_MAN_HX58_Repair_Base", [[[0.604,4.895,-1.38], [-0.54,4.89,-1.38]],[[0,-4.2,-1.55]]]]
];

YOSHI_getTowingPoints = {
	params ["_object"];

	_returnValue = [];

	{
		if (_object isKindOf _x) then {
			_returnValue = YOSHI_TowingLookupTable get _x;
		};
	} forEach (keys YOSHI_TowingLookupTable);

	_returnValue

};

YFU_FABRICATOR_MESSAGES = [
	"Packing boxes...",
	"Fetching order...",
	"Allocating materials...",
	"Checking stock levels...",
	"Calibrating tolerances...",
	"Staging components...",
	"Priming fabrication bay...",
	"Verifying order manifest...",
	"Warming up machinery...",
	"Synchronizing modules...",
	"Aligning precision tools...",
	"Assembling components...",
	"Compiling build instructions...",
	"Optimizing production path...",
	"Engaging safety interlocks...",
	"Preparing output tray...",
	"Inspecting components...",
	"Applying quality checks...",
	"Routing internal logistics...",
	"Balancing system load...",
	"Spooling fabrication plans...",
	"Confirming specifications...",
	"Updating inventory records...",
	"Clearing fabrication queue...",
	"Processing material requests...",
	"Securing parts...",
	"Running diagnostics...",
	"Finalizing preparation...",
	"Convincing parts to cooperate...",
	"Negotiating with the machine spirits...",
	"Shaking the box to see what's inside...",
	"Looking for the missing screw...",
	"Applying excessive precision...",
	"Double-checking the double-check...",
	"Blaming the previous operator...",
	"Turning it off and on again...",
	"Pretending this is normal...",
	"Re-reading the instructions...",
	"Ignoring the warning light...",
	"Waiting for it to finish thinking...",
	"Counting bolts (again)...",
	"Asking engineering for clarification...",
	"Measuring twice, cutting anyway...",
	"Holding it together with optimism...",
	"Cross-referencing reality...",
	"Calibrating vibes...",
	"Making sure it's probably fine...",
	"Ensuring nothing explodes...",
	"Sacrificing efficiency for safety...",
	"Checking if anyone is watching...",
	"Reallocating blame vectors...",
	"Engaging emergency coffee protocol...",
	"Letting the machine warm up emotionally...",
	"Consulting ancient documentation...",
	"Hoping the math works out..."
];

private _count = [
	[
		["Box_NATO_Equip_F",[[0.30,-0.63,-0.38],[-0.30,0.63,-0.38],[-0.30,-0.63,0.38]]],
		["Box_NATO_Support_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_NATO_Ammo_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_NATO_Grenades_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_NATO_AmmoOrd_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_NATO_Wps_F", [[0.5,-0.34,-0.19],[-0.47,0.3,-0.19],[-0.47,-0.34,0.14]]],
		["Box_NATO_WpsLaunch_F", [[0.78,-0.13,-0.19],[-0.73,0.12,-0.19],[-0.73,-0.13,0.15]]],
		["Box_NATO_WpsSpecial_F", [[0.78,-0.32,-0.19],[-0.73,0.30,-0.19],[-0.73,-0.32,0.15]]],
		["Box_NATO_Uniforms_F",[[0.30,-0.63,-0.38],[-0.31,0.63,-0.38],[-0.31,-0.63,0.38]]],
		["Box_NATO_AmmoVeh_F",[[0.75,-0.75,-0.82],[-0.75,0.75,-0.82],[-0.75,-0.75,0.68]]],
		["Box_East_Support_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_East_Ammo_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_East_Grenades_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_East_AmmoOrd_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_East_Wps_F", [[0.5,-0.34,-0.19],[-0.47,0.3,-0.19],[-0.47,-0.34,0.14]]],
		["Box_East_WpsLaunch_F", [[0.78,-0.13,-0.19],[-0.73,0.12,-0.19],[-0.73,-0.13,0.15]]],
		["Box_East_WpsSpecial_F", [[0.78,-0.32,-0.19],[-0.73,0.30,-0.19],[-0.73,-0.32,0.15]]],
		["Box_East_Uniforms_F",[[0.30,-0.63,-0.38],[-0.31,0.63,-0.38],[-0.31,-0.63,0.38]]],
		["Box_East_AmmoVeh_F",[[0.75,-0.75,-0.82],[-0.75,0.75,-0.82],[-0.75,-0.75,0.68]]],
		["Box_IND_Support_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_IND_Ammo_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_IND_Grenades_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_IND_AmmoOrd_F",[[0.21,-0.25,-0.32],[-0.15,0.35,-0.32],[-0.15,-0.25,0.26]]],
		["Box_IND_Wps_F", [[0.5,-0.34,-0.19],[-0.47,0.3,-0.19],[-0.47,-0.34,0.14]]],
		["Box_IND_WpsLaunch_F", [[0.78,-0.13,-0.19],[-0.73,0.12,-0.19],[-0.73,-0.13,0.15]]],
		["Box_IND_WpsSpecial_F", [[0.78,-0.32,-0.19],[-0.73,0.30,-0.19],[-0.73,-0.32,0.15]]],
		["Box_IND_Uniforms_F",[[0.30,-0.63,-0.38],[-0.31,0.63,-0.38],[-0.31,-0.63,0.38]]],
		["Box_IND_AmmoVeh_F",[[0.75,-0.75,-0.82],[-0.75,0.75,-0.82],[-0.75,-0.75,0.68]]],
		["Box_Syndicate_Ammo_F",[[0.43,-0.27,-0.22],[-0.38,0.24,-0.22],[-0.38,-0.27,0.22]]],
		["Box_Syndicate_Wps_F",[[0.47,-0.2,-0.08],[-0.45,0.2,-0.08],[-0.45,-0.2,0.06]]],
		["Box_Syndicate_WpsLaunch_F",[[0.63,-0.18,-0.18],[-0.58,0.17,-0.18],[-0.58,-0.18,0.13]]],
		["B_supplyCrate_F",[[0.77,-0.49,-0.9],[-0.76,0.51,-0.9],[-0.76,-0.49,0.43]]],
		["IG_supplyCrate_F",[[0.77,-0.49,-0.9],[-0.76,0.51,-0.9],[-0.76,-0.49,0.43]]],
		["I_supplyCrate_F",[[0.77,-0.49,-0.9],[-0.76,0.51,-0.9],[-0.76,-0.49,0.43]]],
		["O_supplyCrate_F",[[0.77,-0.49,-0.9],[-0.76,0.51,-0.9],[-0.76,-0.49,0.43]]],
		["Box_9Rifles_Medical_F",[[0.30,-0.63,-0.38],[-0.31,0.63,-0.38],[-0.31,-0.63,0.38]]]
	]
] call YOSHI_packSetRefOverrides;