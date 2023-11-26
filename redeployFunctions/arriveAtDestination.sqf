private _arriveAtDestination = {
	params [
		"_vic",  
		"_groupLeader", 
		"_goHome", 
		["_last_message", nil],
		["_wavingOff", false]
	];

	private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};

	private _destination = _vicStatus get "destination";

	if (isNil "_destination") exitWith {
		// destination being nil means that there was no LZ/RP found
		true
	};

	private _destinationPos = getPos _destination;

	//wait until vic is near destination 
	waitUntil {sleep 1; (_vic distance2D _destinationPos < 100) || (_vicStatus get "waveOff" && !_wavingOff)};

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};

	// wait until vic stopped/landed
	waitUntil {sleep 1; ((isTouchingGround _vic) && (speed _vic < 1)) || (_vicStatus get "waveOff" && !_wavingOff)};

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};

	_vic engineOn false;

	// if (!isNil "_last_message") then {
	// 	driver _vic sideChat _last_message;
	// };

	if (_goHome) then {
		// vic sent back home, so since it's home it can take on a new mission
		_vicStatus set ["isReinserting", false];
	};
};