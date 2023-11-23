//this addAction ["<t color='#00AA00'>Request Reinsert</t>", "redeploy.sqf", nil, 6, false, true, "", "true", 5, false, "", ""];

#include "redeployFunctions\goToLocation.sqf"


// Get the vic
private _vic = _this select 0;

// Check if the vic is already on a mission
if (_vic getVariable "isReinserting") exitWith {
    driver _vic sideChat "I am currently on a mission.";
};

// Group leader's variable name
private _groupLeader = bull;

_vic setVariable ["isHeli", false, true];
_vic setVariable ["performedReinsert", false, true];
_vic setVariable ["destination", nil, true];

if (_vic isKindOf "Helicopter") then {
    _vic setVariable ["isHeli", true, true];
};

driver _vic sideChat "Starting Procedures";

// Prevent multiple simultaneous reinsertion requests
_vic setVariable ["isReinserting", true, true];

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vic getVariable ["isHeli", false]) then {
    _dustOffMessage = "Heading to LZ at: %1";
    _touchdownMessage = "Touchdown, Please disembark now";
} else {
    _dustOffMessage = "Heading to RP at: %1";
    _touchdownMessage = "We're here, Please disembark now";
};

[_vic, _groupLeader, false, true, _dustOffMessage, _touchdownMessage] call _goToLocation;
_vic setVariable ["performedReinsert", true, true];

private _currentIteration = 0;

waitUntil {
    sleep 1; 
    private _cargoList = fullCrew [_vic, "cargo"]; 
    private _cargoCount = count _cargoList; 
    _currentIteration = _currentIteration + 1;
    _cargoCount < 1 || {_currentIteration >= 15};
};

driver _vic sideChat "Transport Unload complete, RTB in 10 seconds.";
sleep 10;

if (!(_vic getVariable ["fallbackTriggered", false])) then {
    // if fallback triggered, this prevents double calling RTB
    [_vic, _groupLeader, true, true, "Returning to Base at: %1", "Ready for tasking..."] call _goToLocation;
};

_vic engineOn false;
_vic setVariable ["performedReinsert", false, true];
_vic setVariable ["isReinserting", false, true];
_vic setVariable ["fallbackTriggered", false, true];