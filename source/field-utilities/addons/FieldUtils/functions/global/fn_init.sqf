#include "..\..\ui\idc.hpp"

params ["_isJip"];

uiNamespace setVariable ["YFU_ui_registry", createHashMap];
uiNamespace setVariable ["YFU_fabricator_queue_map", createHashMap];
uiNamespace setVariable ["YFU_fabricator_queue_order", []];
uiNamespace setVariable ["YFU_fabricator_queue_dynamic", []];
uiNamespace setVariable ["YFU_fabricator_items", []];
uiNamespace setVariable ["YFU_submit_in_progress", false];
uiNamespace setVariable ["YFU_submit_success", false];

["assets", YFU_IDC_PAGE_ASSETS] call YFU_UI_RegisterPage;
