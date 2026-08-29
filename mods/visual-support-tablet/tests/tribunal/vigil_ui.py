"""Permanent Tier 3 contract for VIGIL's client-local tablet UI."""

from tribunal.runner.model import CharacterizedBehavior, Scenario, ScenarioReview


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
        "vigil.browser.serverFixture",
        "vigil.browser.serverLocality",
        "vigil.browser.cleanup",
        "vigil.locality.serverNoDisplay",
        "vigil.locality.noServerOpenPath",
    }),
    client_expected=frozenset({
        "vigil.browser.fixtureReplicated",
        "vigil.browser.transportExact",
        "vigil.browser.artilleryExact",
        "vigil.browser.casExact",
        "vigil.access.requiredRejects",
        "vigil.access.overrideOpens",
        "vigil.access.bluOpens",
        "vigil.access.independentOpens",
        "vigil.access.opforOpens",
        "vigil.access.matrixCleanup",
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
private _browserVehicles = [];
private _browserUnits = [];
private _browserGroups = [];
private _spawnBrowserVehicle = {
    params ["_class", "_posATL", "_groupLabel"];
    private _vehicle = createVehicle [_class, _posATL, [], 0, "NONE"];
    createVehicleCrew _vehicle;
    _vehicle allowCrewInImmobile true;
    _vehicle setFuel 0;
    _vehicle engineOn false;
    _browserVehicles pushBack _vehicle;
    _vehicle setVariable ["TRIBUNAL_VIGIL_BROWSER_GROUP_LABEL", _groupLabel];
    _vehicle
};

private _browserTransport = ["B_Heli_Light_01_F", [1450, 5420, 0], "TRIBUNAL TRANSPORT"] call _spawnBrowserVehicle;
private _browserArtillery = ["B_Mortar_01_F", [1480, 5420, 0], "TRIBUNAL ARTILLERY"] call _spawnBrowserVehicle;
private _browserCas = ["B_Heli_Attack_01_F", [1510, 5420, 0], "TRIBUNAL CAS"] call _spawnBrowserVehicle;
private _hostileTransport = ["O_Heli_Light_02_unarmed_F", [1540, 5420, 0], "TRIBUNAL HOSTILE TRANSPORT"] call _spawnBrowserVehicle;
private _hostileArtillery = ["O_Mortar_01_F", [1570, 5420, 0], "TRIBUNAL HOSTILE ARTILLERY"] call _spawnBrowserVehicle;
private _hostileCas = ["O_Heli_Attack_02_dynamicLoadout_F", [1600, 5420, 0], "TRIBUNAL HOSTILE CAS"] call _spawnBrowserVehicle;
private _deadTransport = ["B_Heli_Light_01_F", [1630, 5420, 0], "TRIBUNAL DEAD TRANSPORT"] call _spawnBrowserVehicle;
private _wrongRole = ["B_MRAP_01_F", [1660, 5420, 0], "TRIBUNAL WRONG ROLE"] call _spawnBrowserVehicle;

private _crewReadyDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (_browserVehicles findIf {isNull effectiveCommander _x}) < 0
        || {diag_tickTime > _crewReadyDeadline}
};
{
    private _vehicle = _x;
    {
        doStop _x;
        _browserUnits pushBack _x;
    } forEach crew _vehicle;
    private _group = group effectiveCommander _vehicle;
    if (!isNull _group) then {
        _group setGroupIdGlobal [_vehicle getVariable ["TRIBUNAL_VIGIL_BROWSER_GROUP_LABEL", "TRIBUNAL BROWSER"]];
        _browserGroups pushBackUnique _group;
    };
} forEach _browserVehicles;
_deadTransport setDamage 1;

private _browserIds = _browserVehicles apply {netId _x};
private _fixtureValid = (count (_browserIds select {_x isEqualTo ""})) isEqualTo 0
    && {(count (_browserIds arrayIntersect _browserIds)) isEqualTo count _browserIds}
    && {alive _browserTransport}
    && {alive _browserArtillery}
    && {alive _browserCas}
    && {!isNull effectiveCommander _browserTransport}
    && {!isNull effectiveCommander _browserArtillery}
    && {!isNull effectiveCommander _browserCas}
    && {side (group effectiveCommander _browserTransport) isEqualTo west}
    && {side (group effectiveCommander _browserArtillery) isEqualTo west}
    && {side (group effectiveCommander _browserCas) isEqualTo west}
    && {side (group effectiveCommander _hostileTransport) isEqualTo east}
    && {side (group effectiveCommander _hostileArtillery) isEqualTo east}
    && {side (group effectiveCommander _hostileCas) isEqualTo east}
    && {alive _hostileTransport}
    && {alive _hostileArtillery}
    && {alive _hostileCas}
    && {alive _wrongRole}
    && {!alive _deadTransport};
private _serverLocal = (_browserVehicles findIf {!local _x || {owner _x isNotEqualTo 2}}) < 0;
["vigil.browser.serverFixture", _fixtureValid, format ["ids=%1|classes=%2|alive=%3", _browserIds, _browserVehicles apply {typeOf _x}, _browserVehicles apply {alive _x}]] call _assert;
["vigil.browser.serverLocality", _serverLocal, format ["locality=%1", _browserVehicles apply {[netId _x, local _x, owner _x]}]] call _assert;
missionNamespace setVariable [
    "TRIBUNAL_VIGIL_BROWSER_FIXTURE",
    [
        netId _browserTransport,
        netId _browserArtillery,
        netId _browserCas,
        [netId _hostileTransport, netId _hostileArtillery, netId _hostileCas, netId _deadTransport, netId _wrongRole]
    ],
    true
];

private _serverDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
["vigil.locality.serverNoDisplay", isDedicated && {!hasInterface} && {isNull _serverDisplay}, format ["dedicated=%1|hasInterface=%2|display=%3", isDedicated, hasInterface, !isNull _serverDisplay]] call _assert;
["vigil.locality.noServerOpenPath", isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_SERVER_OPEN"}, "no server UI open execution marker"] call _assert;
private _browserDoneDeadline = diag_tickTime + 90;
waitUntil {
    uiSleep 0.1;
    missionNamespace getVariable ["TRIBUNAL_VIGIL_BROWSER_DONE", false]
        || {diag_tickTime > _browserDoneDeadline}
};
private _browserCompleted = missionNamespace getVariable ["TRIBUNAL_VIGIL_BROWSER_DONE", false];
{deleteVehicle _x;} forEach _browserUnits;
{deleteVehicle _x;} forEach _browserVehicles;
{deleteGroup _x;} forEach _browserGroups;
missionNamespace setVariable ["TRIBUNAL_VIGIL_BROWSER_FIXTURE", nil, true];
private _cleanupDeadline = diag_tickTime + 3;
waitUntil {
    uiSleep 0.05;
    (_browserIds findIf {!isNull (objectFromNetId _x)}) < 0 || {diag_tickTime > _cleanupDeadline}
};
private _browserClean = _browserCompleted
    && {(_browserIds findIf {!isNull (objectFromNetId _x)}) < 0};
["vigil.browser.cleanup", _browserClean, format ["clientDone=%1|remaining=%2", _browserCompleted, _browserIds select {!isNull (objectFromNetId _x)}]] call _assert;
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

private _tabletClasses = ["YSF_VigilTerminal_B", "YSF_VigilTerminal_I", "YSF_VigilTerminal_O"];
{
    if (_x in assignedItems player) then {player unlinkItem _x;};
} forEach _tabletClasses;
private _noneDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; (_tabletClasses findIf {_x in assignedItems player}) < 0 || diag_tickTime > _noneDeadline};

private _closeTablet = {
    if (!isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])) then {closeDialog 0;};
    private _deadline = diag_tickTime + 5;
    waitUntil {uiSleep 0.05; isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || diag_tickTime > _deadline};
    isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])
};
private _openTablet = {
    if (!isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])) exitWith {false};
    [] spawn {[] call YSF_UI_OpenTablet;};
    private _deadline = diag_tickTime + 8;
    waitUntil {uiSleep 0.05; !isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]) || diag_tickTime > _deadline};
    private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
    private _page = if (isNull _display) then {controlNull} else {_display displayCtrl 88130};
    private _tabs = if (isNull _page) then {controlNull} else {_page controlsGroupCtrl 88050};
    !isNull _display && {(ctrlIDD _display) isEqualTo 88000} && {!isNull _page} && {!isNull _tabs}
};

private _browserFixture = [];
private _browserFixtureDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    _browserFixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_BROWSER_FIXTURE", []];
    (count _browserFixture) isEqualTo 4 || {diag_tickTime > _browserFixtureDeadline}
};
private _fixtureObjects = [];
private _browserObjectsDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    _fixtureObjects = [];
    if ((count _browserFixture) isEqualTo 4) then {
        _fixtureObjects = [
            objectFromNetId (_browserFixture # 0),
            objectFromNetId (_browserFixture # 1),
            objectFromNetId (_browserFixture # 2)
        ];
        {_fixtureObjects pushBack (objectFromNetId _x);} forEach (_browserFixture # 3);
    };
    ((count _fixtureObjects) isEqualTo 8
        && {(_fixtureObjects findIf {isNull _x}) < 0})
        || {diag_tickTime > _browserObjectsDeadline}
};
private _fixtureClasses = _fixtureObjects apply {if (isNull _x) then {"<null>"} else {typeOf _x}};
private _fixtureReplicated = (count _fixtureObjects) isEqualTo 8
    && {(_fixtureObjects findIf {isNull _x}) < 0}
    && {_fixtureClasses isEqualTo [
        "B_Heli_Light_01_F",
        "B_Mortar_01_F",
        "B_Heli_Attack_01_F",
        "O_Heli_Light_02_unarmed_F",
        "O_Mortar_01_F",
        "O_Heli_Attack_02_dynamicLoadout_F",
        "B_Heli_Light_01_F",
        "B_MRAP_01_F"
    ]}
    && {alive (_fixtureObjects # 0)}
    && {alive (_fixtureObjects # 1)}
    && {alive (_fixtureObjects # 2)}
    && {alive (_fixtureObjects # 3)}
    && {alive (_fixtureObjects # 4)}
    && {alive (_fixtureObjects # 5)}
    && {alive (_fixtureObjects # 7)}
    && {!alive (_fixtureObjects # 6)};
private _predicateInputs = _fixtureObjects apply {
    if (isNull _x) then {
        []
    } else {
        private _commander = effectiveCommander _x;
        [
            netId _x,
            typeOf _x,
            alive _x,
            side _x,
            if (isNull _commander) then {"<null>"} else {side (group _commander)},
            _x emptyPositions "cargo",
            locked _x,
            count (magazinesAmmoFull _x),
            [_x] call YOSHI_cfgSideIsPlayer,
            [_x] call YOSHI_isTransportHelicopter,
            [_x] call YOSHI_isArmedHelicopter,
            [_x] call YSF_isArtilleryCapable
        ]
    }
};
["vigil.browser.fixtureReplicated", _fixtureReplicated, format ["fixture=%1|classes=%2|alive=%3|locality=%4|predicateInputs=%5", _browserFixture, _fixtureClasses, _fixtureObjects apply {if (isNull _x) then {false} else {alive _x}}, _fixtureObjects apply {if (isNull _x) then {[]} else {[netId _x, local _x, owner _x]}}, _predicateInputs]] call _assert;

private _browserTreeNetIds = {
    params ["_tree"];
    private _ids = [];
    if (isNull _tree) exitWith {_ids};
    private _roots = _tree tvCount [];
    for "_root" from 0 to (_roots - 1) do {
        private _rootData = _tree tvData [_root];
        if !(_rootData isEqualTo "") then {_ids pushBack _rootData;};
        private _children = _tree tvCount [_root];
        for "_child" from 0 to (_children - 1) do {
            private _childData = _tree tvData [_root, _child];
            if !(_childData isEqualTo "") then {_ids pushBack _childData;};
        };
    };
    _ids
};

private _assertBrowserCategory = {
    params ["_category", "_expectedIds", "_assertion"];
    [_category] call YOSHI_selectAssetType;
    uiSleep 0.15;
    private _items = (uiNamespace getVariable ["YSF_assets_items", []])
        select {!isNull _x};
    private _itemIds = _items apply {netId _x};
    private _treeResult = [88310] call YOSHI_getControl;
    private _tree = _treeResult # 0;
    private _treeIds = [_tree] call _browserTreeNetIds;
    private _expected = +_expectedIds;
    _itemIds sort true;
    _treeIds sort true;
    _expected sort true;
    private _passed = (_treeResult # 1)
        && {_itemIds isEqualTo _expected}
        && {_treeIds isEqualTo _expected};
    [_assertion, _passed, format ["category=%1|expected=%2|items=%3|tree=%4|fixtureClasses=%5", _category, _expected, _itemIds, _treeIds, _fixtureClasses]] call _assert;
};

missionNamespace setVariable ["YSF_enableTablet", true];
private _requiredStimulus = (missionNamespace getVariable ["YSF_enableTablet", false])
    && {(_tabletClasses findIf {_x in assignedItems player}) < 0}
    && {isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])};
missionNamespace setVariable ["TRIBUNAL_VIGIL_REQUIRED_CALL_AT", nil];
[] spawn {
    missionNamespace setVariable ["TRIBUNAL_VIGIL_REQUIRED_CALL_AT", diag_tickTime];
    [] call YSF_UI_OpenTablet;
};
uiSleep 1;
private _requiredCalledAt = missionNamespace getVariable ["TRIBUNAL_VIGIL_REQUIRED_CALL_AT", -1];
private _requiredRejected = _requiredStimulus && {_requiredCalledAt >= 0} && {isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])};
["vigil.access.requiredRejects", _requiredRejected, format ["setting=%1|assigned=%2|calledAt=%3|display=%4", missionNamespace getVariable ["YSF_enableTablet", false], assignedItems player, _requiredCalledAt, !isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])]] call _assert;

missionNamespace setVariable ["YSF_enableTablet", false];
private _overrideOpened = (missionNamespace getVariable ["YSF_enableTablet", true]) isEqualTo false
    && {(_tabletClasses findIf {_x in assignedItems player}) < 0}
    && {call _openTablet};
["vigil.access.overrideOpens", _overrideOpened, format ["setting=%1|assigned=%2|display=%3", missionNamespace getVariable ["YSF_enableTablet", true], assignedItems player, !isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])]] call _assert;
if (_overrideOpened && {_fixtureReplicated}) then {
    ["transport", [_browserFixture # 0], "vigil.browser.transportExact"] call _assertBrowserCategory;
    ["arty", [_browserFixture # 1], "vigil.browser.artilleryExact"] call _assertBrowserCategory;
    ["cas", [_browserFixture # 2], "vigil.browser.casExact"] call _assertBrowserCategory;
    ["transport"] call YOSHI_selectAssetType;
} else {
    ["vigil.browser.transportExact", false, format ["override=%1|fixture=%2", _overrideOpened, _fixtureReplicated]] call _assert;
    ["vigil.browser.artilleryExact", false, format ["override=%1|fixture=%2", _overrideOpened, _fixtureReplicated]] call _assert;
    ["vigil.browser.casExact", false, format ["override=%1|fixture=%2", _overrideOpened, _fixtureReplicated]] call _assert;
};
missionNamespace setVariable ["TRIBUNAL_VIGIL_BROWSER_DONE", true, true];
call _closeTablet;

missionNamespace setVariable ["YSF_enableTablet", true];
private _variantAssertions = [
    ["YSF_VigilTerminal_B", "vigil.access.bluOpens"],
    ["YSF_VigilTerminal_I", "vigil.access.independentOpens"],
    ["YSF_VigilTerminal_O", "vigil.access.opforOpens"]
];
{
    _x params ["_class", "_assertion"];
    {
        if (_x in assignedItems player) then {player unlinkItem _x;};
    } forEach _tabletClasses;
    player linkItem _class;
    private _equipVariantDeadline = diag_tickTime + 3;
    waitUntil {uiSleep 0.05; _class in assignedItems player || diag_tickTime > _equipVariantDeadline};
    private _exactAssigned = _class in assignedItems player
        && {(_tabletClasses select {_x in assignedItems player}) isEqualTo [_class]};
    private _opened = _exactAssigned && {call _openTablet};
    [_assertion, _opened, format ["class=%1|setting=%2|assigned=%3|display=%4", _class, missionNamespace getVariable ["YSF_enableTablet", false], assignedItems player, !isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull])]] call _assert;
    private _closed = call _closeTablet;
    if (!_closed) then {diag_log format ["TRIBUNAL_VIGIL|ACCESS_CLOSE_FAILED|class=%1", _class];};
} forEach _variantAssertions;

private _matrixClean = isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]);
["vigil.access.matrixCleanup", _matrixClean, format ["display=%1|assigned=%2", !isNull (uiNamespace getVariable ["YSF_Tablet_Display", displayNull]), assignedItems player]] call _assert;

{
    if (_x in assignedItems player) then {player unlinkItem _x;};
} forEach _tabletClasses;
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
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="The equipped client can open Vigil, see exactly the live friendly eligible transport, artillery, and rotary-CAS assets while excluding hostile, dead, and wrong-role controls, navigate visible tabs, close cleanly, and reopen at a reset default state without server UI state.",
        outcome="KEEP + CHARACTERIZE ENGINE REQUIREMENT",
        rationale="Exact tokenized fixture netIds are compared with both the live tree rows and client backing objects; framebuffer/input remains limited to the inherently visual navigation contract.",
        dependencies=("Tribunal authenticated framebuffer input", "Vigil terminal item", "Arma UI scheduler"),
        evidence_types=frozenset({"framebuffer", "input", "client-ui-state", "exact-identity", "negative-control", "locality"}),
        locality_requirements="All display/input state exists only on client-a; the dedicated server retains displayNull.",
        characterized_behaviors=(CharacterizedBehavior(
            description="Reopen Vigil from a fresh scheduled script after Escape destroys the prior display.",
            reason="This Arma build silently fails to recreate the dialog from the same scheduled worker that observed its destruction.",
            evidence="Controlled failed/successive UI runs preceding 20260812T211714Z-358dbef7; the fresh worker produced stable closed-to-reopened framebuffer and backing-state transitions.",
            alternative_tested="Call YSF_UI_OpenTablet in the original close-observer worker.",
            outcome="The same-worker call did not recreate the dialog; a fresh scheduled context did.",
        ),),
    ),
)
