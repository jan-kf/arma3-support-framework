params ["_object"];

[_object, -1] call ace_cargo_fnc_setSize;

_object addEventHandler ["EpeContactStart", {
	params ["_object1", "_object2", "_selection1", "_selection2", "_force", "_reactForce", "_worldPos"];
	_object1 call YOSHI_attachToBelow;
}];
