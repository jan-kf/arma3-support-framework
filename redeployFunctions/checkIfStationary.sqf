#include "leaveCurrentLocation.sqf"
#include "arriveAtDestination.sqf"
#include "findRendezvousPoint.sqf"
#include "posToGrid.sqf"

// if redeploy was performed, then it will attempt to RTB, otherwise it will reattempt the redeploy
params ["_vic", "_groupLeader", "_timeout", "_timelimit", "_stationaryThreshold"];
private _lastPos = getPos _vic;
private _startTime = time;

private _didArrive = {
	params ["_vic"];

	private _destination = _vic getVariable ["destination", nil];

	private _destinationPos = getPos _destination;
	if ((isTouchingGround _vic) && (speed _vic < 1) && _vic distance2D _destinationPos < 100) then{
		true;
	}else {
		false;
	};
};

// Check the status of the vic periodically
while {time - _startTime < _timeout} do {
	sleep _timelimit;
	private _currentPos = getPos _vic;
	private _arrived = [_vic] call _didArrive;

	if (isNull _vic || isNil "_vic" || !(alive _vic) || isNil "_arrived" || _arrived) exitWith {
		// hint "exiting stationary check";
		true;
	};

	// Calculate the distance moved
	private _distanceMoved = _currentPos distance _lastPos;
	// should only trigger if it's not on the ground (if heli), it hasn't moved, and stopStationary check if false
	if (!(_vic getVariable ["isHeli", false] && isTouchingGround _vic ) && (_distanceMoved < _stationaryThreshold) && !(_arrived)) exitWith {
		

		_vic setVariable ["fallbackTriggered", true, true];
		// vic is considered stationary, recall to base
		// Take off and fly back to base (defined as a marker or specific coordinates)

		if (_vic getVariable ["performedReinsert", false]) then {
			// stalled, but has reinserted, RTB
			[_vic, _groupLeader, true, "Something went wrong, returning to Base"] call _leaveCurrentLocation;
			[_vic, _groupLeader, true, nil] call _arriveAtDestination;
			_vic setVariable ["isReinserting", false, true];

		} else {
			//stalled but hasn't reinserted, try again
			[_vic, _groupLeader, false, "Something went wrong, attempting redeploy at %1"] call _leaveCurrentLocation;
			[_vic, _groupLeader, true, nil] call _arriveAtDestination;
			_vic setVariable ["performedReinsert", true, true];
		};
		
	};
	_lastPos = _currentPos; // Update last known position
};