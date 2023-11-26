private _findRendezvousPoint = {
	params ["_vic", "_target", ["_checkOccupied", false], ["_goHome", false]];
	private _dropOffPoint = nil;
	private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

	if (_vicStatus get "isHeli") then {
		private _manifest = home_base getVariable "homeBaseManifest";
		private _padRegistry = _manifest get "padRegistry";
		private _activeAwayPads = _manifest get "activeAwayPads";
		private _padsNearBase = _manifest get "padsNearBase";

		private _nearestLandingPads = _padsNearBase;
		if (!_goHome) then {
			_nearestLandingPads = nearestObjects [_target, _manifest get "landingPadClasses", 250]; // Adjust the range as needed
		};

		if (_checkOccupied) then {
			// Function to check if a landing pad is occupied
			
			private _isPadOccupied = {
				params ["_pad", "_vic", "_registry", "_awayPads", "_goHome", "_classesToSkip"];
				// checks registry if it's going back to base
				private _padId = netId _pad;
				private _homePad = _registry getOrDefault [_padId, "unassigned"];
				private _homeHasFreePads = (_goHome && _padId in _registry && _homePad == "unassigned");
				private _awayHasFreePads = (!_goHome && !(_padId in _awayPads));
				if ( _homeHasFreePads || _awayHasFreePads) then {
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
				private _isOccupied = [_x, _vic, _padRegistry, _activeAwayPads, _goHome, _manifest get "landingPadClasses"] call _isPadOccupied;
				if (!_isOccupied) then {
					_unoccupiedPad = _x;
					break;
				};
			} forEach _nearestLandingPads;
			
			if (isNil "_unoccupiedPad") exitWith {
				nil // return nil if there's no valid pad
			};
			// return the _unoccupiedPad
			if (!_goHome) then {
				// add the pad to the list of pads in use that are not at the homebase
				private _locationID = netId _unoccupiedPad;
				_activeAwayPads pushBack _locationId;
				_vicStatus set ["awayParkingPass", _locationID];
			} else {
				// assign the _vic to the _unoccupiedPad at home
				_padRegistry set [netId _unoccupiedPad, netId _vic]; 
			};

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