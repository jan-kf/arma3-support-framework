YOSHI_setVirtualStorageLogic = {
	params ["_logic", "_id", "_params"];

	YOSHI_VIRTUAL_STORAGE = _logic;
	publicVariable "YOSHI_VIRTUAL_STORAGE";
};

YOSHI_setFabricatorLogic = {
	params ["_logic", "_id", "_params"];

	YOSHI_FABRICATOR = _logic;
	publicVariable "YOSHI_FABRICATOR";

	// The module attribute lives on the logic, which clients cannot read
	// reliably, so the decision is published as its own value. Default true
	// matches the module default and keeps existing missions unchanged.
	YOSHI_FABRICATOR_LOCAL_INVENTORY = _logic getVariable ["Fabricator_Module_EnableLocalArsenal", true];
	publicVariable "YOSHI_FABRICATOR_LOCAL_INVENTORY";
};