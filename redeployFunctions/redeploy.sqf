//this addAction ["<t color='#00AA00'>Request Reinsert</t>", "redeploy.sqf", nil, 6, false, true, "", "true", 5, false, "", ""];

#include "goToLocation.sqf"

// Get the vic
private _vic = _this select 0;

// Group leader's variable name
private _groupLeader = _this select 1;

private _padRegistry = home_base getVariable "padRegistry";
// prior to performing a redeploy, vic unassigns itself from the pad registry for cleanup
{
    // systemChat format ["_x, _y: %1, %2", _x, _y];
    if (_y == (netId _vic)) then {
        // release assignment of pad if vic leaves the base
        _padRegistry set [_x, "unassigned"];
    }
} forEach _padRegistry;

// Check if the vic is already on a mission
if (_vic getVariable "isReinserting") exitWith {
    driver _vic sideChat "I am currently on a mission.";
};

_vic setVariable ["waveOff", false];
_vic setVariable ["requestingRedeploy", false];



_vic setVariable ["isHeli", false];
_vic setVariable ["performedReinsert", false];
_vic setVariable ["destination", nil];

if (_vic isKindOf "Helicopter") then {
    _vic setVariable ["isHeli", true];
};

// driver _vic sideChat "Starting Procedures";

// Prevent multiple simultaneous reinsertion requests
_vic setVariable ["isReinserting", true];

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vic getVariable ["isHeli", false]) then {
    _dustOffMessage = "Heading to LZ at: %1";
    _touchdownMessage = "Touchdown, Please disembark now";
} else {
    _dustOffMessage = "Heading to RP at: %1";
    _touchdownMessage = "We're here, Please disembark now";
};

if (_vic getVariable "waveOff") exitWith {
    true
};

[_vic, _groupLeader, false, true, false, _dustOffMessage, _touchdownMessage] call _goToLocation;
_vic setVariable ["performedReinsert", true];


if (_vic getVariable "waveOff" ) exitWith {
    true
};

private _currentIteration = 0;
waitUntil {
    sleep 1; 
    private _cargoList = fullCrew [_vic, "cargo"]; 
    private _cargoCount = count _cargoList; 
    _currentIteration = _currentIteration + 1;
    _cargoCount < 1 || {_currentIteration >= 15} || _vic getVariable "waveOff";
};

if (_vic getVariable "waveOff" ) exitWith {
    true
};

driver _vic sideChat "Transport Unload complete, RTB in 10 seconds.";
sleep 10;

if (_vic getVariable "waveOff" ) exitWith {
    true
};

if (!(_vic getVariable ["fallbackTriggered", false]) && !(_vic getVariable ["waveOff", false])) then {
    // if fallback triggered, this prevents double calling RTB
    [_vic, _groupLeader, true, true, false, "Returning to Base at: %1", "Ready for tasking..."] call _goToLocation;
};

if (_vic getVariable "waveOff") exitWith {
    true
};

driver _vic sideChat "Ready for tasking...";

_vic engineOn false;
_vic setVariable ["performedReinsert", false];
_vic setVariable ["isReinserting", false];
_vic setVariable ["fallbackTriggered", false];
