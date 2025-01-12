params ["_logic", "_id", "_params"];

YOSHI_FW_RECON_CONFIG_OBJECT = createHashMapObject [[
	["#base", YOSHI_FW_BASE_CONFIG_OBJECT],
	["isInitialized", { true }]
], _logic];
