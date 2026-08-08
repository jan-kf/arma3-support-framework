YOSHI_setVirtualStorageLogic = {
	params ["_logic", "_id", "_params"];

	YOSHI_VIRTUAL_STORAGE = _logic;
	publicVariable "YOSHI_VIRTUAL_STORAGE";
};

YOSHI_setFabricatorLogic = {
	params ["_logic", "_id", "_params"];

	YOSHI_FABRICATOR = _logic;
	publicVariable "YOSHI_FABRICATOR";
};