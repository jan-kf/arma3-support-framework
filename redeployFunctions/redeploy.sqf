//this addAction ["<t color='#00AA00'>Request Reinsert</t>", "redeploy.sqf", nil, 6, false, true, "", "true", 5, false, "", ""];

#include "goToLocation.sqf"

// Get the vic
private _vic = _this select 0;

// Group leader's variable name
private _groupLeader = _this select 1;

private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

private _padRegistry = home_base getVariable "homeBaseManifest" get "padRegistry";
// prior to performing a redeploy, vic unassigns itself from the pad registry for cleanup
[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");

// Check if the vic is already on a mission
if (_vicStatus get "isReinserting") exitWith {
    [driver _vic, "I am currently on a mission."] remoteExec ["sideChat"];
};

_vicStatus set ["waveOff", false];
_vicStatus set ["cancelRedeploy", false];
_vicStatus set ["requestingRedeploy", false];
_vicStatus set ["performedReinsert", false];
_vicStatus set ["destination", nil];

// driver _vic sideChat "Starting Procedures";

// Prevent multiple simultaneous reinsertion requests
_vicStatus set ["isReinserting", true];

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vicStatus get "isHeli") then {
    _dustOffMessage = "Heading to LZ at: %1";
    _touchdownMessage = "Touchdown, Please disembark now";
} else {
    _dustOffMessage = "Heading to RP at: %1";
    _touchdownMessage = "We're here, Please disembark now";
};

if (_vicStatus get "waveOff") exitWith {
    true
};

[_vic, _groupLeader, false, true, false, _dustOffMessage, _touchdownMessage] call _goToLocation;
_vicStatus set ["performedReinsert", true];


if (_vicStatus get "waveOff" || _vicStatus get "cancelRedeploy") exitWith {
    true
};

private _currentIteration = 0;
waitUntil {
    sleep 1; 
    private _cargoList = fullCrew [_vic, "cargo"]; 
    private _cargoCount = count _cargoList; 
    _currentIteration = _currentIteration + 1;
    _cargoCount < 1 || {_currentIteration >= 15} || _vicStatus get "waveOff";
};

if (_vicStatus get "waveOff" ) exitWith {
    true
};

[driver _vic, "Transport Unload complete, RTB in 10 seconds."] remoteExec ["sideChat"];
sleep 10;

if (_vicStatus get "waveOff" ) exitWith {
    true
};

if (!(_vicStatus get "waveOff")) then {
    [_vic, _groupLeader, true, true, false, "Returning to Base at: %1", "Ready for tasking..."] call _goToLocation;
};

if (_vicStatus get "waveOff") exitWith {
    true
};

// always release parking request 
[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");

[driver _vic, "Ready for tasking..."] remoteExec ["sideChat"];

_vic engineOn false;
_vicStatus set ["performedReinsert", false];
_vicStatus set ["isReinserting", false];

