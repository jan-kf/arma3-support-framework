params ["_vic", "_target", ["_checkOccupied", false], ["_goHome", false]];
private _dropOffPoint = nil;

if (_vic getVariable ["isHeli", false]) then {
	private _padsNearBase = call SupportFramework_fnc_getPadsNearBase;
	private _padsNearTarget = [_target] call SupportFramework_fnc_getPadsNearTarget;
	private _landingPadClasses = ["Land_HelipadEmpty_F", "Land_HelipadCircle_F", "Land_HelipadCivil_F", "Land_HelipadRescue_F", "Land_HelipadSquare_F", "Land_JumpTarget_F"];

	private _nearestLandingPads = _padsNearBase;
	if (!_goHome) then {
		_nearestLandingPads = _padsNearTarget
	};

	if (_checkOccupied) then {
		// Function to check if a landing pad is occupied
		
		private _isPadOccupied = {
			params ["_pad", "_vic", "_homePads", "_awayPads", "_goHome", "_classesToSkip"];
			// checks registry if it's going back to base
			private _padId = netId _pad;
			
			private _unassigned = false;
			// check if the pad is already assigned
			private _check = _pad getVariable "assignment";
			if (isNil "_check") then {
				_unassigned = true;
			};

			if ( _unassigned) then {
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
			private _isOccupied = [_x, _vic, _padsNearBase, _padsNearTarget, _goHome, _landingPadClasses] call _isPadOccupied;
			if (!_isOccupied) then {
				_unoccupiedPad = _x;
				break;
			};
		} forEach _nearestLandingPads;
		
		if (isNil "_unoccupiedPad") exitWith {
			nil // return nil if there's no valid pad
		};

		// reserve the pad
		_unoccupiedPad setVariable ["assignment", netId _vic, true]; 

		// return the _unoccupiedPad
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