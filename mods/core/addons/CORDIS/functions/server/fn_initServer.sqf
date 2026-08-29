/*
CORDIS server bootstrap.
Initializes shared runtime state used by the authority and dedupe helpers.
*/

if (!isServer) exitWith {};

if (isNil { missionNamespace getVariable "YCD_onceCache" }) then {
    missionNamespace setVariable ["YCD_onceCache", createHashMap];
};
