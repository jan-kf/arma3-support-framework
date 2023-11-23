private _findRendezvousPoint = {
	params ["_vic", "_target", ["_checkOccupied", false], ["_goHome", false]];
	private _dropOffPoint = nil;

	if (_vic getVariable ["isHeli", false]) then {
		private _padRegistry = home_base getVariable "padRegistry";
		private _padsNearBase = home_base getVariable "padsNearBase";

		private _nearestLandingPads = _padsNearBase;
		if (!_goHome) then {
			_nearestLandingPads = nearestObjects [_target, home_base getVariable "landingPadClasses", 1000]; // Adjust the range as needed
		};

		if (_checkOccupied) then {
			// Function to check if a landing pad is occupied
			
			private _isPadOccupied = {
				params ["_pad", "_vic", "_registry", "_goHome", "_classesToSkip"];
				// checks registry if it's going back to base
				private _padId = netId _pad;
				private _homePad = _registry getOrDefault [_padId, "unassigned"];
				if ( (_goHome && _padId in _registry && _homePad == "unassigned") || !_goHome) then {
					private _nearbyObjects = _pad nearEntities 10; // Adjust the radius as needed
					private _occupied = false;
					{
						private _inShouldSkip = typeOf _x in _classesToSkip;
						// if the entity is not the pad itself, the vic itself, and it's not a class to skip, then it's occupied 
						if (_x != _pad && _x != _vic && !_inShouldSkip) then {
							_occupied = true;
						};
					} forEach _nearbyObjects;
					_occupied
				} else {
					true // _pad has a vehicle assigned to it
				};
			};
			private _unoccupiedPad = nil;
			{
				private _isOccupied = [_x, _vic, _padRegistry, _goHome, home_base getVariable "landingPadClasses"] call _isPadOccupied;
				if (!_isOccupied) then {
					_unoccupiedPad = _x;
					break;
				};
			} forEach _nearestLandingPads;
			
			if (isNil "_unoccupiedPad") exitWith {
				if (_vic getVariable ["isHeli", false]) then {
					driver _vic sideChat "No LZ found!";
				} else {
					driver _vic sideChat "No RP found!";
				};
				_vic setVariable ["isReinserting", false, true];
				nil
			};
			// return the _unoccupiedPad
			_padRegistry set [netId _unoccupiedPad, netId _vic]; // assign the _vic to the _unoccupiedPad
			_unoccupiedPad
		} else {
			// this is not checking for obstructions
			if (count _nearestLandingPads > 0) then {
				_nearestLandingPads select 0  // Return the closest point
			} else {
				nil // Return nil if no points are found
			};
		};
		
	} else {
		// Return the target if it's not a heli
		_target
	};
};