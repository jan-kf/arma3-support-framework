"""Dynamic client-local map-marker contract for VIGIL's artillery preview."""

from tribunal.runner.model import Scenario, ScenarioReview


TAB_REGIONS = (
    {"x": 160, "y": 40, "width": 120, "height": 40},
    {"x": 280, "y": 40, "width": 120, "height": 40},
    {"x": 400, "y": 40, "width": 120, "height": 40},
    {"x": 520, "y": 40, "width": 120, "height": 40},
)


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-markers",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.marker.serverNoDisplay",
        "vigil.marker.serverNoState",
    }),
    client_expected=frozenset({
        "vigil.marker.fixtureReady",
        "vigil.marker.clientLocality",
        "vigil.marker.mapReady",
        "vigil.marker.initialEmpty",
        "vigil.marker.firstBacking",
        "vigil.marker.firstPosition",
        "vigil.marker.dynamicBacking",
        "vigil.marker.dynamicReplacement",
        "vigil.marker.cleanup",
        "vigil.marker.closeCleanup",
    }),
    server_sqf=r'''
private _serverDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
private _serverMarkers = uiNamespace getVariable ["YOSHI_sp_markers", []];
["vigil.marker.serverNoDisplay", isDedicated && {!hasInterface} && {isNull _serverDisplay}, format ["dedicated=%1|hasInterface=%2|display=%3", isDedicated, hasInterface, !isNull _serverDisplay]] call _assert;
["vigil.marker.serverNoState", _serverMarkers isEqualTo [], format ["markers=%1", _serverMarkers]] call _assert;
''',
    client_sqf=r'''
private _identity = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""];
private _inputReadyAt = diag_tickTime + 8;
waitUntil { uiSleep 0.1; diag_tickTime >= _inputReadyAt };
player linkItem "YSF_VigilTerminal_B";
private _equipDeadline = diag_tickTime + 3;
waitUntil { uiSleep 0.05; "YSF_VigilTerminal_B" in assignedItems player || diag_tickTime > _equipDeadline };
private _fixtureReady = !isNull (findDisplay 46) && {alive player} && {"YSF_VigilTerminal_B" in assignedItems player};
["vigil.marker.fixtureReady", _fixtureReady, format ["display46=%1|alive=%2|assigned=%3", !isNull (findDisplay 46), alive player, "YSF_VigilTerminal_B" in assignedItems player]] call _assert;
["vigil.marker.clientLocality", hasInterface && {!isServer} && {_identity isEqualTo "client-a"}, format ["hasInterface=%1|server=%2|identity=%3|owner=%4", hasInterface, isServer, _identity, clientOwner]] call _assert;
if (_fixtureReady) then { diag_log "TRIBUNAL_VIGIL_MARKER|ARMED"; };

private _tabDeadline = diag_tickTime + 35;
waitUntil {
    uiSleep 0.05;
    (uiNamespace getVariable ["YSF_assets_tabIndex", -1]) isEqualTo 1
        && {(uiNamespace getVariable ["YSF_asset_type", ""]) isEqualTo "arty"}
        || diag_tickTime > _tabDeadline
};
disableSerialization;
private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
private _page = if (isNull _display) then {controlNull} else {_display displayCtrl 88130};
private _map = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 88111};
private _gridControl = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 96126};
private _countControl = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 96125};
private _world = [4680, 2770, 0];
private _mapReady = !isNull _display && {!isNull _page} && {!isNull _map} && {!isNull _gridControl} && {!isNull _countControl} && {ctrlShown _map};
["vigil.marker.mapReady", _mapReady, format ["display=%1|page=%2|map=%3|mapShown=%4|grid=%5|count=%6", !isNull _display, !isNull _page, !isNull _map, ctrlShown _map, !isNull _gridControl, !isNull _countControl]] call _assert;

if (_mapReady) then {
    _map ctrlMapAnimAdd [0, 0.2, _world];
    ctrlMapAnimCommit _map;
    _gridControl ctrlSetText "0468-0277";
    [_gridControl] call YOSHI_assetCoordChanged;
    // Establish this fixture's own geometry instead of inheriting state from
    // an earlier artillery scenario in a composed suite.
    ["pattern", "circle"] call YOSHI_taskArty_Set;
    ["spread", 50] call YOSHI_taskArty_Set;
    ["dir", 0] call YOSHI_taskArty_Set;
    _countControl ctrlSetText "0";
    ["count", _countControl] call YOSHI_setCount;
};
private _scaleDeadline = diag_tickTime + 3;
waitUntil { uiSleep 0.05; (!isNull _map && {abs ((ctrlMapScale _map) - 0.2) < 0.01}) || diag_tickTime > _scaleDeadline };
private _state = call YOSHI_taskArty_GetState;
private _initialMarkers = uiNamespace getVariable ["YOSHI_sp_markers", []];
["vigil.marker.initialEmpty", _mapReady && {_initialMarkers isEqualTo []} && {(_state get "count") isEqualTo 0} && {(_state get "grid") distance2D _world < 1}, format ["token=%1|markers=%2|state=%3|scale=%4", _token, _initialMarkers, _state, if (isNull _map) then {-1} else {ctrlMapScale _map}]] call _assert;
diag_log format ["TRIBUNAL_VIGIL_MARKER|BASELINE_READY|token=%1|world=%2|screen=%3|map=%4", _token, _world, if (isNull _map) then {[]} else {_map ctrlMapWorldToScreen _world}, if (isNull _map) then {[]} else {ctrlPosition _map}];
uiSleep 4;

if (_mapReady) then {
    _countControl ctrlSetText "1";
    ["count", _countControl] call YOSHI_setCount;
};
private _oneMarkers = +(uiNamespace getVariable ["YOSHI_sp_markers", []]);
private _onePositions = uiNamespace getVariable ["YOSHI_taskArty_strikePattern", []];
private _oneRegistered = _oneMarkers select { !(_x in allMapMarkers) };
private _oneShapes = _oneMarkers apply {markerShape _x};
private _oneSizes = _oneMarkers apply {markerSize _x};
["vigil.marker.firstBacking", (count _oneMarkers) isEqualTo 1 && {_oneRegistered isEqualTo []} && {_oneShapes isEqualTo ["ELLIPSE"]} && {_oneSizes isEqualTo [[100,125]]} && {(count _onePositions) isEqualTo 1}, format ["markers=%1|positions=%2|missing=%3|shapes=%4|sizes=%5", _oneMarkers, _onePositions, _oneRegistered, _oneShapes, _oneSizes]] call _assert;
private _onePosition = _onePositions param [0, [-1,-1,0]];
private _oneScreen = if (isNull _map) then {[]} else {_map ctrlMapWorldToScreen _onePosition};
["vigil.marker.firstPosition", _onePosition distance2D _world < 1 && {(count _oneScreen) isEqualTo 2} && {(_oneScreen # 0) > 0.5} && {(_oneScreen # 0) < 1} && {(_oneScreen # 1) > 0} && {(_oneScreen # 1) < 0.5}, format ["world=%1|marker=%2|screen=%3", _world, _onePosition, _oneScreen]] call _assert;
diag_log format ["TRIBUNAL_VIGIL_MARKER|ONE_READY|token=%1|markers=%2|positions=%3|screen=%4", _token, _oneMarkers, _onePositions, _oneScreen];
uiSleep 4;

if (_mapReady) then {
    _countControl ctrlSetText "3";
    ["count", _countControl] call YOSHI_setCount;
};
private _threeMarkers = +(uiNamespace getVariable ["YOSHI_sp_markers", []]);
private _threePositions = +(uiNamespace getVariable ["YOSHI_taskArty_strikePattern", []]);
private _threeMissing = _threeMarkers select { !(_x in allMapMarkers) };
private _threeScreens = if (isNull _map) then {[]} else {_threePositions apply {_map ctrlMapWorldToScreen _x}};
private _staleOne = _oneMarkers select {_x in allMapMarkers};
["vigil.marker.dynamicBacking", (call YOSHI_taskArty_GetState) get "count" isEqualTo 3 && {(count _threeMarkers) isEqualTo 3} && {(count _threePositions) isEqualTo 3} && {_threeMissing isEqualTo []} && {(_threeMarkers arrayIntersect _oneMarkers) isEqualTo []}, format ["markers=%1|positions=%2|screens=%3|missing=%4", _threeMarkers, _threePositions, _threeScreens, _threeMissing]] call _assert;
["vigil.marker.dynamicReplacement", _staleOne isEqualTo [] && {({markerShape _x isEqualTo "ELLIPSE" && {markerSize _x isEqualTo [100,125]}} count _threeMarkers) isEqualTo 3}, format ["old=%1|stale=%2|new=%3", _oneMarkers, _staleOne, _threeMarkers]] call _assert;
diag_log format ["TRIBUNAL_VIGIL_MARKER|THREE_READY|token=%1|markers=%2|positions=%3|screens=%4", _token, _threeMarkers, _threePositions, _threeScreens];
uiSleep 4;

if (_mapReady) then {
    _countControl ctrlSetText "0";
    ["count", _countControl] call YOSHI_setCount;
};
private _remaining = _threeMarkers select {_x in allMapMarkers};
private _storedAfter = uiNamespace getVariable ["YOSHI_sp_markers", []];
private _positionsAfter = uiNamespace getVariable ["YOSHI_taskArty_strikePattern", []];
["vigil.marker.cleanup", _remaining isEqualTo [] && {_storedAfter isEqualTo []} && {_positionsAfter isEqualTo []} && {((call YOSHI_taskArty_GetState) get "count") isEqualTo 0}, format ["old=%1|remaining=%2|stored=%3|positions=%4", _threeMarkers, _remaining, _storedAfter, _positionsAfter]] call _assert;
diag_log format ["TRIBUNAL_VIGIL_MARKER|CLEARED_READY|token=%1|old=%2|remaining=%3", _token, _threeMarkers, _remaining];

private _closeDeadline = diag_tickTime + 12;
waitUntil { uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || diag_tickTime > _closeDeadline };
private _closed = isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]);
["vigil.marker.closeCleanup", _closed && {(uiNamespace getVariable ["YOSHI_sp_markers", []]) isEqualTo []} && {(uiNamespace getVariable ["YSF_map_overlay_markers", []]) isEqualTo []}, format ["closed=%1|strike=%2|overlay=%3", _closed, uiNamespace getVariable ["YOSHI_sp_markers", []], uiNamespace getVariable ["YSF_map_overlay_markers", []]]] call _assert;
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-artillery-preview-markers",
        "visual_driver": "map-markers",
        "visual_armed_marker": "TRIBUNAL_VIGIL_MARKER|ARMED",
        "visual_regions": TAB_REGIONS,
        "visual_initial_index": 0,
        "visual_target_index": 1,
        "map_region": {"x": 650, "y": 0, "width": 480, "height": 360},
        "map_expected_anchor": {"x": 0.5, "y": 0.5},
        "future_client_isolation": "client-b must retain an empty local marker namespace",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Changing a valid artillery request updates the visible client-local preview count and position, replaces stale preview state, and removes it on clear/close.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="Backing marker names and arrays are used only to disambiguate stale rendering; the stable contract is visible spatial/count lifecycle and cleanup.",
        dependencies=("Tribunal framebuffer/map observer", "Vigil artillery preview"),
        evidence_types=frozenset({"framebuffer", "map-position", "client-ui-state", "cleanup"}),
        locality_requirements="Preview controls and markers are client-a-local; the dedicated server must have neither display nor preview state.",
    ),
)
