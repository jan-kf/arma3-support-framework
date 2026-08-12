"""Permanent Tier 3 contract for VIGIL's client-local tablet UI."""

from tribunal.runner.model import Scenario


TAB_REGIONS = (
    {"x": 160, "y": 40, "width": 120, "height": 40},
    {"x": 280, "y": 40, "width": 120, "height": 40},
    {"x": 400, "y": 40, "width": 120, "height": 40},
    {"x": 520, "y": 40, "width": 120, "height": 40},
)


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-ui",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.locality.serverNoDisplay",
        "vigil.locality.noServerOpenPath",
    }),
    client_expected=frozenset({
        "vigil.fixture.itemEquipped",
        "vigil.fixture.inputReady",
        "vigil.locality.clientContext",
        "vigil.open.display",
        "vigil.open.controls",
        "vigil.input.artilleryTab",
        "vigil.close.state",
        "vigil.reopen.state",
    }),
    server_sqf=r'''
private _serverDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
["vigil.locality.serverNoDisplay", isDedicated && {!hasInterface} && {isNull _serverDisplay}, format ["dedicated=%1|hasInterface=%2|display=%3", isDedicated, hasInterface, !isNull _serverDisplay]] call _assert;
["vigil.locality.noServerOpenPath", isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_SERVER_OPEN"}, "no server UI open execution marker"] call _assert;
''',
    client_sqf=r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];
["vigil.locality.clientContext", hasInterface && {!isServer} && {_identity isEqualTo "client-a"}, format ["hasInterface=%1|server=%2|identity=%3|clientOwner=%4", hasInterface, isServer, _identity, clientOwner]] call _assert;
// initPlayerLocal can run while a cold client is still building its action-map
// cache and applying its authoritative inventory. Let that transient work
// settle before equipping the fixture item so late synchronization cannot
// remove it after the test has armed external input.
private _inputReadyAt = diag_tickTime + 8;
waitUntil { uiSleep 0.1; diag_tickTime >= _inputReadyAt };
player linkItem "YSF_VigilTerminal_B";
private _equipDeadline = diag_tickTime + 3;
waitUntil { uiSleep 0.05; "YSF_VigilTerminal_B" in assignedItems player || diag_tickTime > _equipDeadline };
private _equipped = "YSF_VigilTerminal_B" in assignedItems player;
["vigil.fixture.itemEquipped", _equipped, format ["assigned=%1", assignedItems player]] call _assert;
private _gameDisplay = findDisplay 46;
private _inputReady = !isNull _gameDisplay && {alive player} && {"YSF_VigilTerminal_B" in assignedItems player};
["vigil.fixture.inputReady", _inputReady, format ["display46=%1|alive=%2|assigned=%3|diagTick=%4", !isNull _gameDisplay, alive player, "YSF_VigilTerminal_B" in assignedItems player, diag_tickTime]] call _assert;
if (_inputReady) then { diag_log "TRIBUNAL_VIGIL|ARMED"; };

private _openDeadline = diag_tickTime + 35;
waitUntil {
    uiSleep 0.05;
    private _candidateDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
    private _candidatePage = if (isNull _candidateDisplay) then {controlNull} else {_candidateDisplay displayCtrl 88130};
    private _candidateTabs = if (isNull _candidatePage) then {controlNull} else {_candidatePage controlsGroupCtrl 88050};
    (!isNull _candidateTabs && {(lbCurSel _candidateTabs) isEqualTo 0} && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "transport"}) || diag_tickTime > _openDeadline
};
disableSerialization;
private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
private _page = if (isNull _display) then {controlNull} else {_display displayCtrl 88130};
private _tabs = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 88050};
["vigil.open.display", !isNull _display && {(ctrlIDD _display) isEqualTo 88000}, format ["display=%1|idd=%2", !isNull _display, ctrlIDD _display]] call _assert;
["vigil.open.controls", !isNull _page && {!isNull _tabs} && {ctrlEnabled _tabs} && {(lbCurSel _tabs) isEqualTo 0} && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "transport"}, format ["page=%1|tabs=%2|enabled=%3|selection=%4|type=%5", !isNull _page, !isNull _tabs, ctrlEnabled _tabs, lbCurSel _tabs, uiNamespace getVariable ["YSF_asset_type", ""]]] call _assert;
diag_log format ["TRIBUNAL_VIGIL|OPEN_STATE|display=%1|selection=%2|type=%3", !isNull _display, lbCurSel _tabs, uiNamespace getVariable ["YSF_asset_type", ""]];

private _tabDeadline = diag_tickTime + 25;
waitUntil { uiSleep 0.05; (!isNull _tabs && {(uiNamespace getVariable ["YSF_assets_tabIndex", -1]) isEqualTo 1} && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "arty"}) || diag_tickTime > _tabDeadline };
private _artilleryGroup = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 96120};
private _transportGroup = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 96100};
["vigil.input.artilleryTab", !isNull _tabs && {(uiNamespace getVariable ["YSF_assets_tabIndex", -1]) isEqualTo 1} && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "arty"} && {!isNull _artilleryGroup} && {ctrlShown _artilleryGroup} && {!ctrlShown _transportGroup}, format ["tabIndex=%1|type=%2|artyShown=%3|transportShown=%4", uiNamespace getVariable ["YSF_assets_tabIndex", -1], uiNamespace getVariable ["YSF_asset_type", ""], ctrlShown _artilleryGroup, ctrlShown _transportGroup]] call _assert;
diag_log "TRIBUNAL_VIGIL|TAB_STATE|artillery";
// Retain the transitioned state long enough for the independent framebuffer
// observer to capture it before exercising the close lifecycle.
uiSleep 2;

private _closeDeadline = diag_tickTime + 10;
waitUntil { uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || diag_tickTime > _closeDeadline };
private _closed = isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]);
private _markers = uiNamespace getVariable ["YSF_map_overlay_markers", []];
["vigil.close.state", _closed && {_markers isEqualTo []}, format ["closed=%1|markers=%2", _closed, _markers]] call _assert;
diag_log "TRIBUNAL_VIGIL|CLOSED_STATE";
// Retain the user-closed game surface for the independent observer before
// rebuilding a fresh dialog.
uiSleep 8;

// Arma does not reliably recreate a dialog from the same scheduled worker that
// observed its Escape-driven destruction. Dispatch the product's unmodified
// open API in a fresh scheduled context, matching a subsequent user action.
private _reopenWorker = [] spawn {
    [] call YSF_UI_OpenTablet;
};
private _reopenDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    private _candidateDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
    private _candidatePage = if (isNull _candidateDisplay) then {controlNull} else {_candidateDisplay displayCtrl 88130};
    private _candidateTabs = if (isNull _candidatePage) then {controlNull} else {_candidatePage controlsGroupCtrl 88050};
    (!isNull _candidateTabs && {(lbCurSel _candidateTabs) isEqualTo 0} && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "transport"}) || diag_tickTime > _reopenDeadline
};
_display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
_page = if (isNull _display) then {controlNull} else {_display displayCtrl 88130};
_tabs = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 88050};
private _reopened = !isNull _display && {!isNull _page} && {!isNull _tabs} && {ctrlEnabled _tabs} && {(lbCurSel _tabs) isEqualTo 0} && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "transport"};
["vigil.reopen.state", _reopened, format ["display=%1|page=%2|tabs=%3|enabled=%4|selection=%5|type=%6", !isNull _display, !isNull _page, !isNull _tabs, ctrlEnabled _tabs, lbCurSel _tabs, uiNamespace getVariable ["YSF_asset_type", ""]]] call _assert;
diag_log "TRIBUNAL_VIGIL|REOPENED_STATE";
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-assets-tabs",
        "visual_driver": "tabbed-control",
        "visual_armed_marker": "TRIBUNAL_VIGIL|ARMED",
        "visual_regions": TAB_REGIONS,
        "visual_initial_index": 0,
        "visual_target_index": 1,
        "future_client_isolation": "client-b must retain displayNull and unchanged uiNamespace state",
    },
)
