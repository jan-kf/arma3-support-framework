private _arriveAtDestination = {
	params [
		"_vic",  
		"_groupLeader", 
		"_goHome", 
		["_last_message", nil],
		["_wavingOff", false]
	];

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};

	private _destination = _vic getVariable ["destination", home_base];
	private _destinationPos = getPos _destination;

	//wait until vic is near destination 
	waitUntil {sleep 1; _vic distance2D _destinationPos < 100};

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};

	// wait until vic stopped/landed
	waitUntil {sleep 1; (isTouchingGround _vic) && (speed _vic < 1)};

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};

	_vic engineOn false;

	if (!isNil "_last_message") then {
		driver _vic sideChat _last_message;
	};

	if (_goHome) then {
		// vic sent back home, so since it's home it can take on a new mission
		_vic setVariable ["isReinserting", false, true];
	};
};