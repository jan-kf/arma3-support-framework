missionNamespace setVariable ["#EM_FMin", 140]; 
missionNamespace setVariable ["#EM_FMax", 150];

missionNamespace setVariable ["#EM_SMin", 0]; 
missionNamespace setVariable ["#EM_SMax", 22];

missionNamespace setVariable ["#EM_SelMin", 141.6]; 
missionNamespace setVariable ["#EM_SelMax", 141.9];

// Tracked things:
//
// Anti-air - Medium Engine
// APCs - Medium Engine 
// Artillery - Medium Engine
// Boats - Small Engine
// Cars - 315 MHz, 433 MHz
// Drones - 2.4 GHz, 5.8 GHz, 900 MHz, 433 MHz (1.2 GHz Video)
//  Quad/Hexacopters
//  Planes 
//  Helicopters
//  Turrets
//  UGV - Small Engine
// Helicopters - 118-137 MHz
// Planes - 118-137 MHz
// Submersibles - Small Engine
// Tanks - Large Engine
// Military Vehicles with Radios - 30-88 MHz, 225-400 MHz
// Civ Vehicles with Radios - 136-174 MHz, 400-470 MHz
// People
//  Radios 30 - 500 MHz
//  GPS - 1575.42 MHz, 1227.60 MHz
//
// Support Framework
// APS
// CBR
//
// Engines
//  Tiny - Up to 1.5 liters - 50 Hz to 1 kHz
//  Small - 1.6 to 3.0 liters - 1 kHz to 2 kHz
//  Medium - 3.1 to 6.0 liters - 2 kHz to 5 kHz
//  Large - Above 6.0 liters - 5 kHz to 10 kHz

// Range 1: Low Frequencies

//// 0 Hz - 10 kHz - muzzle_antenna_03_f
// Tiny Engines: 50 Hz to 1 kHz
// Small Engines: 1 kHz to 2 kHz
// Medium Engines: 2 kHz to 5 kHz
// Large Engines: 5 kHz to 10 kHz


// Range 2: Medium Frequencies

//// 30 MHz - 500 MHz - muzzle_antenna_02_f
// Cars: 315 MHz, 433 MHz
// Military Vehicles with Radios: 30-88 MHz, 225-400 MHz
// Civ Vehicles with Radios: 136-174 MHz, 400-470 MHz
// Helicopters: 118-137 MHz
// Planes: 118-137 MHz
// People with Radios: 30-500 MHz
// Drones: 433 MHz, 900 MHz (control and telemetry)


// Range 3: High Frequencies

//// 1 GHz - 6 GHz - muzzle_antenna_01_f
// Drones: 1.2 GHz (video), 2.4 GHz, 5.8 GHz (control and video)
// GPS: 1575.42 MHz (L1 band), 1227.60 MHz (L2 band)


beans = [] spawn {
	private _player = player;
	private _range = 1000;
	private _interval = 0.1;
	private _count = 150;

	_getGPSFreq = {
		if (selectRandom [true, false]) then { // GPS
			random [1565.42, 1575.42, 1585.42]; 
		} else {
			random [1217.60, 1227.60, 1237.60];
		};
	};

	_getMilVicRadio = {
		if (selectRandom [true, false]) then { //Military Vehicles with Radios - 30-88 MHz, 225-400 MHz
			random [30, 55, 88]
		} else {
			random [225, 350, 400]
		};
	};

	_getCivVicRadio = {
		if (selectRandom [true, false]) then { //Civ Vehicles with Radios - 136-174 MHz, 400-470 MHz
			random [136, 155, 174]
		} else {
			random [400, 435, 470]
		};
	};
	
	_getAvionics = { // 118-137 MHz
		random [118, 125, 137]
	};
	
	_getExtraLargeEngine = { // 5 kHz to 10 kHz
		random [0.01, 0.015, 0.02]
	};
	_getLargeEngine = { // 5 kHz to 10 kHz
		random [0.005, 0.008, 0.01]
	};

	_getMediumEngine = { // 2 kHz to 5 kHz
		random [0.002, 0.004, 0.005]
	};

	_getSmallEngine = { // 1 kHz to 2 kHz
		random [0.001, 0.0015, 0.002]
	};

	_getTinyEngine = { // 50 Hz to 1 kHz
		random [0.0005, 0.0009, 0.001]
	};

	while {_count > 0} do {
		private _objects = nearestObjects [_player, ["All"], _range];
		hint str([_count, _objects]);
		private _valuesArray = [];

		{
			if (_x != _player) then {
				private _distance = _player distance _x;
				private _strengthModifier = (1 - (_distance / _range));

				private _angleDiff = _player getRelDir _x;

				if (_angleDiff > 180) then {
					_angleDiff = 360 - _angleDiff;
				};

				private _facingMultiplier = 1 - ((_angleDiff / 180) * 0.99);

				private _finalStrength = _strengthModifier * _facingMultiplier;
				private _strengthValue = round (_finalStrength * 20 * 10) / 10;

				_frequencies = [];
				if (isNil {_x getVariable "Frequencies"}) then {

					if (unitIsUAV _x) then { // Drones
						_frequencies pushBack (random [1150, 1200, 1250]); // video
						if (selectRandom [true, false]) then { // control
							_frequencies pushBack (random [2350, 2400, 2450]); 
						} else {
							_frequencies pushBack (random [5750, 5800, 5850]);
						};
						_frequencies pushBack (call _getGPSFreq); // GPS

						_frequencies pushBack (random [890, 900, 910]); // Telemetry
						_frequencies pushBack (random [430, 433, 436]); // Telemetry
					};

					if (_x isKindOf "Plane") then {
						_frequencies pushBack (call _getAvionics);					
					};
					if (_x isKindOf "Helicopter") then {
						_frequencies pushBack (call _getAvionics);					
					};

					_mass = getMass _x;

					if (_mass < 1000) then { // Tiny
						_frequencies pushBack (call _getTinyEngine);
					};
					if (_mass >= 1000 and _mass < 10000) then { // Small
						_frequencies pushBack (call _getSmallEngine);
					};
					if (_mass >= 10000 and _mass < 20000) then { // Medium
						_frequencies pushBack (call _getMediumEngine);
					};
					if (_mass >= 20000 and _mass < 30000) then { // Large
						_frequencies pushBack (call _getLargeEngine);
					};
					if (_mass >= 30000 ) then { // ExtraLarge
						_frequencies pushBack (call _getExtraLargeEngine);
					};



					if (str(side _x) == 'CIV') then {
						_frequencies pushBack (call _getCivVicRadio);
					} else {
						_frequencies pushBack (call _getMilVicRadio);
					};

					_x setVariable ["Frequencies", _frequencies, true];

				} else {

					_frequencies = _x getVariable "Frequencies";

				};

				{_valuesArray pushBack [_x, _strengthValue];} forEach _frequencies;
				
			};
		} forEach _objects;

		hint str(_valuesArray);
		missionNamespace setVariable ["#EM_Values", _valuesArray];
		sleep _interval;
		_count = _count - 1;
	};

	missionNamespace setVariable ["#EM_Values", []];
};


beans = [_this] spawn {
	params ["_player"];

	if(hasInterface) then {
		_player setVariable ["currentWeapon", currentWeapon _player];
		_player setVariable ["handgunMuzzle", (handgunItems _player) select 0];

		_weaponChangeHandler = {
			params ["_player"];
			private _newWeapon = currentWeapon _player;
			private _sideMuzzle = (handgunItems _player) select 0;
			_currentWeapon = _player getVariable ["currentWeapon", currentWeapon _player];
			_currentSideMuzzle = _player getVariable ["handgunMuzzle", (handgunItems _player) select 0];
			if (_newWeapon != _currentWeapon) then {
				hint format ["Weapon changed to: %1", _newWeapon];

				_player setVariable ["currentWeapon", _newWeapon];
			};
			if (_sideMuzzle != _currentSideMuzzle) then {
				hint format ["Muzzle changed to: %1", _sideMuzzle];

				_player setVariable ["handgunMuzzle", _sideMuzzle];
			};
		};

		while {true} do {
			[_player] call _weaponChangeHandler;
			sleep 0.5; 
		};
	};
};