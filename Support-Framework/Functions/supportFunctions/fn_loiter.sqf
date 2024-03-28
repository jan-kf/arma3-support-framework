params ["_vic"];
// vic is currently making it's way to loiter point, or is loitering

[_vic, "LOITER"] call SupportFramework_fnc_checkPulse;
