"""Dynamic client-local map-marker contract for VIGIL's artillery preview."""

from tribunal.runner.model import Scenario, ScenarioReview


TAB_REGIONS = (
    {"x": 160, "y": 40, "width": 120, "height": 40},
    {"x": 280, "y": 40, "width": 120, "height": 40},
    {"x": 400, "y": 40, "width": 120, "height": 40},
    {"x": 520, "y": 40, "width": 120, "height": 40},
)


SERVER_ASSERTIONS = [
    "vigil.marker.serverFixture",
    "vigil.marker.serverNoDisplay",
    "vigil.marker.serverNoState",
    "vigil.marker.serverCleanup",
]

CLIENT_ASSERTIONS = [
    "vigil.marker.fixtureReady",
    "vigil.marker.clientLocality",
    "vigil.marker.mapReady",
    "vigil.marker.initialEmpty",
    "vigil.marker.firstBacking",
    "vigil.marker.firstPosition",
    "vigil.marker.dynamicBacking",
    "vigil.marker.dynamicReplacement",
    "vigil.marker.cleanup",
    "vigil.marker.closeArmed",
    "vigil.marker.closeCleanup",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-markers",
        "version": 1,
        "feature_family": "pontifex-vigil-artillery-preview-markers",
        "name": "Vigil artillery preview-marker lifecycle",
        "definition": {
            "kind": "controlled interactive dedicated-multiplayer UI specification",
            "reference": "source/visual-support-tablet/tests/tribunal/vigil_markers.py",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA and Vigil; authenticated 1280x720 client-a map UI; server-local B_Mortar_01_F fixture",
            "participants": {
                "server": "owns the artillery fixture and proves absence of UI state plus exact fixture cleanup",
                "client-a": "drives the real tablet controls, records rendered map geometry and exact local marker identity lifecycle",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:artillery-preview-markers",
        "label": "Vigil artillery preview-marker lifecycle",
        "kind": "product_behavior",
        "aliases": ["Vigil strike-pattern preview"],
        "biki_context": ["biki-page:5453", "biki-page:1989"],
    },
    "arms": [
        {
            "key": "server_fixture",
            "role": "baseline",
            "description": "A server-local mortar with live ammunition is replicated while the dedicated server retains no tablet display or client preview state",
            "assertions": SERVER_ASSERTIONS[:3],
        },
        {
            "key": "visible_request_lifecycle",
            "role": "positive_control",
            "description": "Real grid and count controls produce one then three visible circles with one exact ETA marker per generation and retire stale names",
            "assertions": CLIENT_ASSERTIONS[:8],
        },
        {
            "key": "explicit_zero",
            "role": "negative_control",
            "description": "The real count control transitions to zero and removes the exact prior strike and ETA generation while the tablet remains open",
            "assertions": [CLIENT_ASSERTIONS[8]],
        },
        {
            "key": "active_escape_close",
            "role": "treatment",
            "description": "The authenticated Escape input arms a non-empty generation in KeyDown, captures strike, ETA, and selected-asset overlay identities, then permits the real onUnload cleanup",
            "assertions": CLIENT_ASSERTIONS[9:],
        },
        {
            "key": "fixture_closeout",
            "role": "treatment",
            "description": "Client completion is received and the exact server artillery fixture is deleted",
            "assertions": [SERVER_ASSERTIONS[3]],
        },
    ],
    "causal_relationships": [
        {
            "key": "active-close-v-explicit-zero",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "active_escape_close",
            "target": "explicit_zero",
            "controlled_dimensions": [
                "same authenticated client",
                "same tablet display",
                "same artillery source and ordnance",
                "same grid, circle pattern, spread, and product count handler",
                "same exact marker-name census",
                "only cleanup stimulus differs",
            ],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:artillery-preview-lifecycle",
            "text": "For the tested client-local Vigil artillery page, real request changes replace visible strike and ETA previews, explicit count zero retires the prior generation, and closing through authenticated Escape retires every exact active strike, ETA, and selected-asset overlay marker identity.",
            "intended_use": "primary_result",
            "assertions": SERVER_ASSERTIONS + CLIENT_ASSERTIONS,
            "rationale": "Framebuffer changes are correlated with projected world geometry and exact allMapMarkers identities; the Escape KeyDown capture proves active names existed immediately before the product onUnload path and the post-close census proves those same names disappeared.",
        },
    ],
    "unresolved": [
        "Coordinate-preview and tab-switch persistence await product decision C12; client-B, simultaneous previews, JIP/reconnect, line rendering, range colour, and VLS sizing remain outside this bounded proof."
    ],
}


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-markers",
    tier="gameplay",
    server_expected=frozenset(SERVER_ASSERTIONS),
    client_expected=frozenset(CLIENT_ASSERTIONS),
    server_sqf=r'''
private _serverDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
private _serverMarkers = uiNamespace getVariable ["YOSHI_sp_markers", []];
private _source = "B_Mortar_01_F" createVehicle [2200, 5000, 0];
_source setVectorUp (surfaceNormal (getPosATL _source));
createVehicleCrew _source;
private _sourceDeadline = diag_tickTime + 8;
waitUntil {uiSleep 0.1; !isNull (effectiveCommander _source) || diag_tickTime > _sourceDeadline};
private _sourceId = netId _source;
private _ordnance = "8Rnd_82mm_Mo_shells";
private _eta = _source getArtilleryETA [[4680, 2770, 0], _ordnance];
private _fixtureReady = _sourceId isNotEqualTo ""
    && {!isNull (effectiveCommander _source)}
    && {(getArtilleryAmmo [_source]) find _ordnance >= 0}
    && {_eta > 0};
["vigil.marker.serverFixture", _fixtureReady, format ["source=%1|commander=%2|ammo=%3|eta=%4", _sourceId, !isNull (effectiveCommander _source), getArtilleryAmmo [_source], _eta]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_MARKER_FIXTURE", [_token, _sourceId, _ordnance], true];
["vigil.marker.serverNoDisplay", isDedicated && {!hasInterface} && {isNull _serverDisplay}, format ["dedicated=%1|hasInterface=%2|display=%3", isDedicated, hasInterface, !isNull _serverDisplay]] call _assert;
["vigil.marker.serverNoState", _serverMarkers isEqualTo [], format ["markers=%1", _serverMarkers]] call _assert;
private _clientDeadline = diag_tickTime + 90;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_VIGIL_MARKER_CLIENT_DONE", ""]) isEqualTo _token || diag_tickTime > _clientDeadline};
deleteVehicleCrew _source;
deleteVehicle _source;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; isNull _source || diag_tickTime > _cleanupDeadline};
["vigil.marker.serverCleanup", isNull _source && {(missionNamespace getVariable ["TRIBUNAL_VIGIL_MARKER_CLIENT_DONE", ""]) isEqualTo _token}, format ["sourceNull=%1|clientDone=%2", isNull _source, missionNamespace getVariable ["TRIBUNAL_VIGIL_MARKER_CLIENT_DONE", ""]]] call _assert;
''',
    client_sqf=r'''
private _fixtureDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_MARKER_FIXTURE"} || diag_tickTime > _fixtureDeadline};
private _fixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_MARKER_FIXTURE", []];
private _sourceId = _fixture param [1, ""];
private _source = if (_sourceId isEqualTo "") then {objNull} else {objectFromNetId _sourceId};
private _ordnance = _fixture param [2, ""];
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
    private _treeResult = [88310] call YOSHI_getControl;
    private _tree = _treeResult # 0;
    private _sourcePath = [];
    if (_treeResult # 1) then {
        for "_root" from 0 to ((_tree tvCount []) - 1) do {
            if ((_tree tvData [_root]) isEqualTo _sourceId) exitWith {_sourcePath = [_root]};
            for "_child" from 0 to ((_tree tvCount [_root]) - 1) do {
                if ((_tree tvData [_root, _child]) isEqualTo _sourceId) exitWith {_sourcePath = [_root, _child]};
            };
            if (_sourcePath isNotEqualTo []) exitWith {};
        };
    };
    if (_sourcePath isNotEqualTo []) then {[_tree, _sourcePath] call YOSHI_assetSelected};
    _map ctrlMapAnimAdd [0, 0.2, _world];
    ctrlMapAnimCommit _map;
    _gridControl ctrlSetText "0468-0277";
    [_gridControl] call YOSHI_assetCoordChanged;
    // Establish this fixture's own geometry instead of inheriting state from
    // an earlier artillery scenario in a composed suite.
    ["pattern", "circle"] call YOSHI_taskArty_Set;
    ["spread", 50] call YOSHI_taskArty_Set;
    ["dir", 0] call YOSHI_taskArty_Set;
    ["ord", _ordnance] call YOSHI_taskArty_Set;
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
private _oneEllipses = _oneMarkers select {markerShape _x isEqualTo "ELLIPSE"};
private _oneEtas = _oneMarkers select {(markerText _x) find "1st Round ETA:" isEqualTo 0};
private _oneSizes = _oneEllipses apply {markerSize _x};
["vigil.marker.firstBacking", (count _oneEllipses) isEqualTo 1 && {(count _oneEtas) isEqualTo 1} && {_oneRegistered isEqualTo []} && {_oneSizes isEqualTo [[100,125]]} && {(count _onePositions) isEqualTo 1}, format ["markers=%1|positions=%2|missing=%3|ellipses=%4|etas=%5|sizes=%6", _oneMarkers, _onePositions, _oneRegistered, _oneEllipses, _oneEtas, _oneSizes]] call _assert;
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
private _threeEtas = _threeMarkers select {(markerText _x) find "1st Round ETA:" isEqualTo 0};
["vigil.marker.dynamicBacking", (call YOSHI_taskArty_GetState) get "count" isEqualTo 3 && {(count _threeMarkers) isEqualTo 4} && {(count _threeEtas) isEqualTo 1} && {(count _threePositions) isEqualTo 3} && {_threeMissing isEqualTo []} && {(_threeMarkers arrayIntersect _oneMarkers) isEqualTo []}, format ["markers=%1|etas=%2|positions=%3|screens=%4|missing=%5", _threeMarkers, _threeEtas, _threePositions, _threeScreens, _threeMissing]] call _assert;
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

if (!isNull _display) then {
    _display displayAddEventHandler ["KeyDown", {
        params ["_display", "_key"];
        if (_key isEqualTo 1) then {
            private _page = _display displayCtrl 88130;
            private _countControl = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 96125};
            if (!isNull _countControl) then {
                _countControl ctrlSetText "3";
                ["count", _countControl] call YOSHI_setCount;
            };
            private _strike = +(uiNamespace getVariable ["YOSHI_sp_markers", []]);
            private _etas = _strike select {(markerText _x) find "1st Round ETA:" isEqualTo 0};
            private _ellipses = _strike select {markerShape _x isEqualTo "ELLIPSE"};
            private _overlays = +(uiNamespace getVariable ["YSF_map_overlay_markers", []]);
            private _positions = +(uiNamespace getVariable ["YOSHI_taskArty_strikePattern", []]);
            private _all = _strike + _overlays;
            private _kindsReady = (count _strike) isEqualTo 4
                && {(count _etas) isEqualTo 1}
                && {(count _ellipses) isEqualTo 3};
            uiNamespace setVariable ["TRIBUNAL_VIGIL_MARKER_CLOSE_CAPTURE", [_strike, _etas, _overlays, _positions, _all apply {_x in allMapMarkers}, _kindsReady]];
        };
        false
    }];
};

private _closeDeadline = diag_tickTime + 12;
waitUntil { uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || diag_tickTime > _closeDeadline };
private _closed = isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]);
private _closeCapture = uiNamespace getVariable ["TRIBUNAL_VIGIL_MARKER_CLOSE_CAPTURE", []];
private _closeStrike = _closeCapture param [0, []];
private _closeEtas = _closeCapture param [1, []];
private _closeOverlays = _closeCapture param [2, []];
private _closePositions = _closeCapture param [3, []];
private _aliveBeforeClose = _closeCapture param [4, []];
private _kindsReady = _closeCapture param [5, false];
private _captured = _closeStrike + _closeOverlays;
private _remainingAfterClose = _captured select {_x in allMapMarkers};
private _closeArmed = (count _closeStrike) isEqualTo 4
    && {(count _closeEtas) isEqualTo 1}
    && {(count _closeOverlays) isEqualTo 1}
    && {(count _closePositions) isEqualTo 3}
    && {_kindsReady}
    && {({!_x} count _aliveBeforeClose) isEqualTo 0};
["vigil.marker.closeArmed", _closeArmed, format ["strike=%1|etas=%2|overlays=%3|positions=%4|alive=%5", _closeStrike, _closeEtas, _closeOverlays, _closePositions, _aliveBeforeClose]] call _assert;
["vigil.marker.closeCleanup", _closed && {_closeArmed} && {_remainingAfterClose isEqualTo []}, format ["closed=%1|captured=%2|remaining=%3|strikeStore=%4|overlayStore=%5", _closed, _captured, _remainingAfterClose, uiNamespace getVariable ["YOSHI_sp_markers", []], uiNamespace getVariable ["YSF_map_overlay_markers", []]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_MARKER_CLIENT_DONE", _token, true];
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
    evidence_contract=EVIDENCE_CONTRACT,
)
