private _findRendezvousPoint = {
	params ["_vic", "_target", ["_checkOccupied", false]];
	private _dropOffPoint = nil;

	if (_vic getVariable ["isHeli", false]) then {
		private _landingPadClasses = ["Land_HelipadEmpty_F", "Land_HelipadCircle_F", "Land_HelipadCivil_F", "Land_HelipadRescue_F", "Land_HelipadSquare_F", "Land_JumpTarget_F"];
		private _nearestLandingPads = nearestObjects [_target, _landingPadClasses, 1000]; // Adjust the range as needed
		
		if (_checkOccupied) then {
			// Function to check if a landing pad is occupied
			private _isPadOccupied = {
				params ["_pad", "_classesToSkip"];
				private _nearbyObjects = _pad nearEntities 10; // Adjust the radius as needed
				private _occupied = false;
				{
					private _inShouldSkip = typeOf _x in _classesToSkip;
					if (_x != _pad && !_inShouldSkip) then {
						_occupied = true;
					};
				} forEach _nearbyObjects;
				_occupied
			};
			private _unoccupiedPad = nil;
			{
				private _isOccupied = [_x, _landingPadClasses] call _isPadOccupied;
				if (!_isOccupied) then {
					_unoccupiedPad = _x;
					break;
				};
			} forEach _nearestLandingPads;
			
			_unoccupiedPad
		} else {
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