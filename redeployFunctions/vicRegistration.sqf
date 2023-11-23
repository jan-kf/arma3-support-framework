private _addRegistrationChoicesToVehicles = {
	params ["_vic"];

	private _vicIsRegistered = [_vic] call (missionNamespace getVariable "_isVehicleRegistered");

	if (_vicIsRegistered) then {
		private _oldRegActionID = _vic getVariable ["regActionID", nil];
		if (!isNil "_oldRegActionID") then {
			_vic removeAction _oldRegActionID;
		};
		private _vehicleClass = typeOf _vic;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _regActionID = _vic addAction [
			format ["<t color='#FF8000'>Unregister %1</t>", _vehicleDisplayName], 
			{
				private _vehicle = _this select 0;
				[_vehicle] call (missionNamespace getVariable "_unregisterVehicle");
			},
			nil, 6, false, true, "", "true", 5, false, "", ""
		];
		_vic setVariable ["regActionID", _regActionID, true];
	} else {
		private _oldRegActionID = _vic getVariable ["regActionID", nil];
		if (!isNil "_oldRegActionID") then {
			_vic removeAction _oldRegActionID;
		};
		private _vehicleClass = typeOf _vic;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _regActionID = _vic addAction [
			format ["<t color='#00ABFF'>Register %1</t>", _vehicleDisplayName], 
			{
				private _vehicle = _this select 0;
				[_vehicle] call (missionNamespace getVariable "_registerVehicle");
			},
			nil, 6, false, true, "", "true", 5, false, "", ""
		];
		_vic setVariable ["regActionID", _regActionID, true];
	};
};
