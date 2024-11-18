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