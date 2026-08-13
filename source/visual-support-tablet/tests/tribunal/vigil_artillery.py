"""Causal Tier 3 coverage for Vigil native artillery and VLS execution."""

from tribunal.mission.artillery import artillery_observer_sqf
from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-artillery",
    tier="gameplay",
    server_expected=frozenset({
        "vigil.artillery.platforms",
        "vigil.artillery.circle.roundCount",
        "vigil.artillery.circle.identity",
        "vigil.artillery.circle.spatial",
        "vigil.artillery.circle.completed",
        "vigil.artillery.line.roundCount",
        "vigil.artillery.line.identity",
        "vigil.artillery.line.spatial",
        "vigil.artillery.line.completed",
        "vigil.artillery.control.zeroRounds",
        "vigil.artillery.control.outOfRange",
        "vigil.artillery.control.noAmmo",
        "vigil.artillery.vls.launch",
        "vigil.artillery.vls.vertical",
        "vigil.artillery.vls.guidance",
        "vigil.artillery.vls.arrival",
        "vigil.artillery.locality",
        "vigil.artillery.cleanup",
    }),
    client_expected=frozenset({
        "vigil.artillery.grid.valid",
        "vigil.artillery.grid.invalid",
        "vigil.artillery.request.circle",
        "vigil.artillery.request.line",
        "vigil.artillery.request.locality",
    }),
    server_sqf=artillery_observer_sqf() + r'''
private _source = "B_Mortar_01_F" createVehicle [1800, 5600, 0];
_source setVectorUp (surfaceNormal (getPosATL _source));
createVehicleCrew _source;
private _sourceDeadline = diag_tickTime + 8;
waitUntil {uiSleep 0.1; !isNull (effectiveCommander _source) || diag_tickTime > _sourceDeadline};
private _sourceId = netId _source;
private _ordnance = "8Rnd_82mm_Mo_shells";
private _representatives = [];
{
    private _vehicle = _x createVehicle [1700 + (_forEachIndex * 20), 5500, 0];
    createVehicleCrew _vehicle;
    _representatives pushBack [_x, [_vehicle] call YSF_isArtilleryCapable, getArtilleryAmmo [_vehicle], weapons _vehicle];
    deleteVehicleCrew _vehicle;
    deleteVehicle _vehicle;
} forEach ["B_Mortar_01_F", "B_MBT_01_arty_F", "B_MBT_01_mlrs_F", "B_Ship_MRLS_01_F"];
private _platformsOk = ({(_x # 1)} count _representatives) isEqualTo 4
    && {((_representatives # 0) # 2) find _ordnance >= 0}
    && {((_representatives # 1) # 2) find "32Rnd_155mm_Mo_shells" >= 0}
    && {((_representatives # 2) # 2) find "12Rnd_230mm_rockets" >= 0}
    && {((_representatives # 3) # 2) isEqualTo []}
    && {((_representatives # 3) # 3) find "weapon_VLS_01" >= 0};
["vigil.artillery.platforms", _platformsOk, format ["representatives=%1", _representatives]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_FIXTURE", [_token, _sourceId, _ordnance], true];

private _circleReadyDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_ARTILLERY_CIRCLE"} || diag_tickTime > _circleReadyDeadline};
private _circle = missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_CIRCLE", []];
private _circlePositions = _circle param [1, []];
private _circleToken = format ["%1-circle", _token];
[_circleToken] call TRIBUNAL_fnc_artilleryObserverStart;
private _circleObserved = [_circleToken, _source, _circlePositions] call TRIBUNAL_fnc_artilleryObserveSource;
missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_CIRCLE_GO", _token, true];
private _circleDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.1;
    private _state = [_circleToken] call TRIBUNAL_fnc_artilleryObserverState;
    private _events = _state getOrDefault ["events", []];
    ((count _events) isEqualTo 3 && {({_x getOrDefault ["terminated", false]} count _events) isEqualTo 3}
        && {(_source getVariable ["YSF_arty_mission_completed", ""]) in ["done", "ready_for_next"]})
        || diag_tickTime > _circleDeadline
};
private _circleState = [_circleToken] call TRIBUNAL_fnc_artilleryObserverStop;
private _circleEvents = _circleState getOrDefault ["events", []];
private _circleCountOk = (count _circlePositions) isEqualTo 3 && {(count _circleEvents) isEqualTo 3};
private _circleIdentityOk = _circleObserved && {_circleCountOk} && {({
    (_x getOrDefault ["source", ""]) isEqualTo _sourceId
    && {(_x getOrDefault ["magazine", ""]) isEqualTo _ordnance}
    && {(_x getOrDefault ["ammo", ""]) isEqualTo "Sh_82mm_AMOS"}
    && {_x getOrDefault ["artilleryEvent", false]}
    && {(_x getOrDefault ["targetPosition", []]) distance2D (_x getOrDefault ["expectedPosition", [1e9,1e9,0]]) < 1}
    && {!isNull (_x getOrDefault ["projectileObject", objNull]) || {_x getOrDefault ["terminated", false]}}
    && {_x getOrDefault ["sourceLocal", false]}
    && {_x getOrDefault ["projectileLocal", false]}
} count _circleEvents) isEqualTo 3};
private _circleDistances = [];
{
    private _last = _x getOrDefault ["lastPosition", []];
    private _expected = _x getOrDefault ["expectedPosition", []];
    _circleDistances pushBack (if ((count _last) >= 2 && {(count _expected) >= 2}) then {_last distance2D _expected} else {1e9});
} forEach _circleEvents;
private _circleSpatialOk = _circleCountOk && {({_x < 175} count _circleDistances) isEqualTo 3};
["vigil.artillery.circle.roundCount", _circleCountOk, format ["requested=%1|events=%2", count _circlePositions, count _circleEvents]] call _assert;
["vigil.artillery.circle.identity", _circleIdentityOk, format ["source=%1|projectiles=%2|artilleryEvents=%3", _sourceId, _circleEvents apply {_x getOrDefault ["projectile", ""]}, _circleEvents apply {_x getOrDefault ["artilleryEvent", false]}]] call _assert;
["vigil.artillery.circle.spatial", _circleSpatialOk, format ["positions=%1|distances=%2", _circlePositions, _circleDistances]] call _assert;
["vigil.artillery.circle.completed", (_source getVariable ["YSF_arty_mission_completed", ""]) in ["done", "ready_for_next"], format ["status=%1", _source getVariable ["YSF_arty_mission_completed", "missing"]]] call _assert;

missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_LINE_PHASE", _token, true];
private _lineReadyDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_ARTILLERY_LINE"} || diag_tickTime > _lineReadyDeadline};
private _line = missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_LINE", []];
private _linePositions = _line param [1, []];
private _lineToken = format ["%1-line", _token];
[_lineToken] call TRIBUNAL_fnc_artilleryObserverStart;
private _lineObserved = [_lineToken, _source, _linePositions] call TRIBUNAL_fnc_artilleryObserveSource;
missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_LINE_GO", _token, true];
private _lineDeadline = diag_tickTime + 150;
waitUntil {
    uiSleep 0.1;
    private _events = ([_lineToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
    ((count _events) isEqualTo 4 && {({_x getOrDefault ["terminated", false]} count _events) isEqualTo 4}
        && {(_source getVariable ["YSF_arty_mission_completed", ""]) in ["done", "ready_for_next"]})
        || diag_tickTime > _lineDeadline
};
private _lineState = [_lineToken] call TRIBUNAL_fnc_artilleryObserverStop;
private _lineEvents = _lineState getOrDefault ["events", []];
private _lineCountOk = (count _linePositions) isEqualTo 4 && {(count _lineEvents) isEqualTo 4};
private _lineIdentityOk = _lineObserved && {_lineCountOk} && {({
    (_x getOrDefault ["source", ""]) isEqualTo _sourceId
    && {(_x getOrDefault ["magazine", ""]) isEqualTo _ordnance}
    && {_x getOrDefault ["artilleryEvent", false]}
    && {(_x getOrDefault ["targetPosition", []]) distance2D (_x getOrDefault ["expectedPosition", [1e9,1e9,0]]) < 1}
    && {_x getOrDefault ["sourceLocal", false]}
    && {_x getOrDefault ["projectileLocal", false]}
} count _lineEvents) isEqualTo 4};
private _lineAlong = [];
private _linePerpendicular = [];
private _lineDistances = [];
private _lineCenter = [2200, 5600, 0];
{
    private _last = _x getOrDefault ["lastPosition", []];
    private _expected = _x getOrDefault ["expectedPosition", []];
    if ((count _last) >= 2) then {
        _lineAlong pushBack ((_last # 0) - (_lineCenter # 0));
        _linePerpendicular pushBack abs ((_last # 1) - (_lineCenter # 1));
    } else {_lineAlong pushBack 0; _linePerpendicular pushBack 1e9};
    _lineDistances pushBack (if ((count _last) >= 2 && {(count _expected) >= 2}) then {_last distance2D _expected} else {1e9});
} forEach _lineEvents;
private _lineSpan = if (_lineAlong isEqualTo []) then {0} else {(selectMax _lineAlong) - (selectMin _lineAlong)};
private _lineSpatialOk = _lineCountOk && {_lineSpan > 120} && {({_x < 140} count _linePerpendicular) isEqualTo 4} && {({_x < 175} count _lineDistances) isEqualTo 4};
["vigil.artillery.line.roundCount", _lineCountOk, format ["requested=%1|events=%2", count _linePositions, count _lineEvents]] call _assert;
["vigil.artillery.line.identity", _lineIdentityOk, format ["source=%1|projectiles=%2|artilleryEvents=%3", _sourceId, _lineEvents apply {_x getOrDefault ["projectile", ""]}, _lineEvents apply {_x getOrDefault ["artilleryEvent", false]}]] call _assert;
["vigil.artillery.line.spatial", _lineSpatialOk, format ["positions=%1|distances=%2|along=%3|perpendicular=%4|span=%5", _linePositions, _lineDistances, _lineAlong, _linePerpendicular, _lineSpan]] call _assert;
["vigil.artillery.line.completed", (_source getVariable ["YSF_arty_mission_completed", ""]) in ["done", "ready_for_next"], format ["status=%1", _source getVariable ["YSF_arty_mission_completed", "missing"]]] call _assert;

private _handlers = call YSF_handlers_artillery;
private _zeroTask = ["artillery", _source, _handlers, [[], _ordnance], 2, 1] call YSF_taskNew;
private _zeroResult = [_source, _zeroTask, [[], _ordnance]] call (_handlers get "init");
["vigil.artillery.control.zeroRounds", _zeroResult isEqualTo "fail", format ["result=%1", _zeroResult]] call _assert;
private _controlToken = format ["%1-controls", _token];
[_controlToken] call TRIBUNAL_fnc_artilleryObserverStart;
[_controlToken, _source, [[9999, 9999, 0]]] call TRIBUNAL_fnc_artilleryObserveSource;
[_source, [[9999, 9999, 0]], _ordnance] call YSF_fireSalvo;
uiSleep 1;
private _outEvents = ([_controlToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
["vigil.artillery.control.outOfRange", _outEvents isEqualTo [], format ["range=%1|events=%2", [9999,9999,0] inRangeOfArtillery [[_source], _ordnance], _outEvents]] call _assert;
_source removeMagazines _ordnance;
[_source, [[2200, 5600, 0]], _ordnance] call YSF_fireSalvo;
uiSleep 1;
private _noAmmoEvents = ([_controlToken] call TRIBUNAL_fnc_artilleryObserverStop) getOrDefault ["events", []];
["vigil.artillery.control.noAmmo", _noAmmoEvents isEqualTo [] && {(getArtilleryAmmo [_source]) find _ordnance < 0}, format ["ammo=%1|events=%2", getArtilleryAmmo [_source], _noAmmoEvents]] call _assert;

private _vls = "B_Ship_MRLS_01_F" createVehicle [1000, 1000, 0];
createVehicleCrew _vls;
_vls setPosASL [1000, 1000, 5];
_vls setVelocity [0,0,0];
uiSleep 1;
private _vlsTarget = [3000, 2000, 0];
private _vlsToken = format ["%1-vls", _token];
[_vlsToken] call TRIBUNAL_fnc_artilleryObserverStart;
private _vlsObserved = [_vlsToken, _vls, [_vlsTarget]] call TRIBUNAL_fnc_artilleryObserveSource;
missionNamespace setVariable ["TRIBUNAL_VIGIL_VLS_LAUNCHED", false];
private _vlsLaunchEh = _vls addEventHandler ["Fired", {
    missionNamespace setVariable ["TRIBUNAL_VIGIL_VLS_LAUNCHED", true];
}];
[_vls] spawn {
    params ["_platform"];
    private _deadline = diag_tickTime + 8;
    while {
        !isNull _platform
        && {!(missionNamespace getVariable ["TRIBUNAL_VIGIL_VLS_LAUNCHED", false])}
        && {diag_tickTime < _deadline}
    } do {
        _platform setPosASL [1000, 1000, 0.5];
        _platform setVelocity [0,0,0];
        uiSleep 0.02;
    };
};
[_vls, [_vlsTarget], "magazine_Missiles_Cruise_01_x18"] spawn YSF_fireSalvo;
private _vlsDeadline = diag_tickTime + 100;
waitUntil {
    uiSleep 0.1;
    private _events = ([_vlsToken] call TRIBUNAL_fnc_artilleryObserverState) getOrDefault ["events", []];
    ((count _events) >= 1 && {(_events # 0) getOrDefault ["terminated", false]}) || diag_tickTime > _vlsDeadline
};
private _vlsState = [_vlsToken] call TRIBUNAL_fnc_artilleryObserverStop;
_vls removeEventHandler ["Fired", _vlsLaunchEh];
private _vlsEvents = _vlsState getOrDefault ["events", []];
private _vlsEvent = _vlsEvents param [0, createHashMap];
private _vlsSamples = _vlsEvent getOrDefault ["samples", []];
private _initial = _vlsEvent getOrDefault ["initialPosition", []];
private _maxAltitude = if (_vlsSamples isEqualTo []) then {-1e9} else {selectMax (_vlsSamples apply {(_x # 1) # 2})};
private _horizontalTravel = if (_vlsSamples isEqualTo [] || {(count _initial) < 2}) then {0} else {(_initial distance2D ((_vlsSamples # ((count _vlsSamples) - 1)) # 1))};
private _last = _vlsEvent getOrDefault ["lastPosition", []];
private _arrivalDistance = if ((count _last) >= 2) then {_last distance2D _vlsTarget} else {1e9};
private _vlsLaunchOk = _vlsObserved && {(count _vlsEvents) isEqualTo 1}
    && {(_vlsEvent getOrDefault ["source", ""]) isEqualTo netId _vls}
    && {(_vlsEvent getOrDefault ["weapon", ""]) isEqualTo "weapon_VLS_01"}
    && {(_vlsEvent getOrDefault ["magazine", ""]) isEqualTo "magazine_Missiles_Cruise_01_x18"}
    && {(_vlsEvent getOrDefault ["ammo", ""]) isEqualTo "ammo_Missile_Cruise_01"};
private _vlsVerticalOk = (count _initial) >= 3 && {_maxAltitude > ((_initial # 2) + 50)};
private _vlsGuidanceOk = _horizontalTravel > 800 && {({abs (((_x # 2) # 0)) > 20 || {abs (((_x # 2) # 1)) > 20}} count _vlsSamples) > 5};
private _vlsArrivalOk = _vlsEvent getOrDefault ["terminated", false] && {_arrivalDistance < 350};
["vigil.artillery.vls.launch", _vlsLaunchOk, format ["source=%1|projectile=%2|initial=%3|velocity=%4", netId _vls, _vlsEvent getOrDefault ["projectile", ""], _initial, _vlsEvent getOrDefault ["initialVelocity", []]]] call _assert;
["vigil.artillery.vls.vertical", _vlsVerticalOk, format ["initial=%1|maxAltitude=%2|samples=%3", _initial, _maxAltitude, count _vlsSamples]] call _assert;
["vigil.artillery.vls.guidance", _vlsGuidanceOk, format ["horizontalTravel=%1|samples=%2", _horizontalTravel, count _vlsSamples]] call _assert;
["vigil.artillery.vls.arrival", _vlsArrivalOk, format ["last=%1|target=%2|distance=%3|terminated=%4", _last, _vlsTarget, _arrivalDistance, _vlsEvent getOrDefault ["terminated", false]]] call _assert;
private _localityOk = local _source && {local effectiveCommander _source} && {local _vls} && {local effectiveCommander _vls}
    && {({_x getOrDefault ["sourceLocal", false] && {_x getOrDefault ["projectileLocal", false]} && {(_x getOrDefault ["executionMachine", ""]) isEqualTo "server"}} count (_circleEvents + _lineEvents + _vlsEvents)) isEqualTo (count (_circleEvents + _lineEvents + _vlsEvents))};
["vigil.artillery.locality", _localityOk, format ["source=%1|vls=%2|events=%3", local _source, local _vls, count (_circleEvents + _lineEvents + _vlsEvents)]] call _assert;
deleteVehicleCrew _source; deleteVehicle _source;
deleteVehicleCrew _vls; deleteVehicle _vls;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (isNull _source && {isNull _vls}) || diag_tickTime > _cleanupDeadline};
private _cleanupOk = isNull _source && {isNull _vls} && {(missionNamespace getVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""]) isEqualTo ""};
["vigil.artillery.cleanup", _cleanupOk, format ["sourceNull=%1|vlsNull=%2|active=%3", isNull _source, isNull _vls, missionNamespace getVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_COMPLETE", _token, true];
''',
    client_sqf=r'''
private _fixtureDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.1; !isNil {missionNamespace getVariable "TRIBUNAL_VIGIL_ARTILLERY_FIXTURE"} || diag_tickTime > _fixtureDeadline};
private _fixture = missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_FIXTURE", []];
private _sourceId = _fixture param [1, ""];
private _source = if (_sourceId isEqualTo "") then {objNull} else {objectFromNetId _sourceId};
private _ordnance = _fixture param [2, ""];
private _parsed = ["0220-0560"] call YOSHI_parseGrid;
private _gridPosition = if (_parsed isEqualTo []) then {[]} else {[(_parsed # 0) * 10, (_parsed # 1) * 10, 0]};
["vigil.artillery.grid.valid", _parsed isEqualTo [220,560] && {_gridPosition isEqualTo [2200,5600,0]}, format ["parsed=%1|position=%2", _parsed, _gridPosition]] call _assert;
private _invalid = [[""], ["220-560"], ["0220056x"], ["02200-560"]] apply {[_x # 0] call YOSHI_parseGrid};
["vigil.artillery.grid.invalid", ({_x isEqualTo []} count _invalid) isEqualTo 4, format ["results=%1", _invalid]] call _assert;
["vigil.artillery.request.locality", hasInterface && {!isServer} && {!isNull _source} && {!local _source}, format ["hasInterface=%1|server=%2|source=%3|sourceLocal=%4", hasInterface, isServer, _sourceId, local _source]] call _assert;

uiNamespace setVariable ["YSF_asset_type", "arty"];
uiNamespace setVariable ["YSF_current_selected_asset", _source];
uiNamespace setVariable ["YOSHI_task_vehicle", _source];
private _circlePositions = [_gridPosition, "circle", 80, 3, 0, _source, _ordnance] call YOSHI_drawStrikePattern;
private _circleState = createHashMapFromArray [["grid",_gridPosition],["pattern","circle"],["spread",80],["count",3],["dir",0],["ord",_ordnance]];
uiNamespace setVariable ["YOSHI_taskArty_state", _circleState];
uiNamespace setVariable ["YOSHI_taskArty_strikePattern", _circlePositions];
missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_CIRCLE", [_token, _circlePositions], true];
private _circleGoDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_CIRCLE_GO", ""]) isEqualTo _token || diag_tickTime > _circleGoDeadline};
private _circleRequestOk = (count _circlePositions) isEqualTo 3 && {(_circleState get "grid") isEqualTo [2200,5600,0]} && {(_circleState get "ord") isEqualTo _ordnance};
["vigil.artillery.request.circle", _circleRequestOk, format ["state=%1|positions=%2", _circleState, _circlePositions]] call _assert;
if (_circleRequestOk) then {call YOSHI_taskArty_submit};

private _linePhaseDeadline = diag_tickTime + 150;
waitUntil {uiSleep 0.1; (missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_LINE_PHASE", ""]) isEqualTo _token || diag_tickTime > _linePhaseDeadline};
private _linePositions = [_gridPosition, "line", 240, 4, 90, _source, _ordnance] call YOSHI_drawStrikePattern;
private _lineState = createHashMapFromArray [["grid",_gridPosition],["pattern","line"],["spread",240],["count",4],["dir",90],["ord",_ordnance]];
uiNamespace setVariable ["YOSHI_taskArty_state", _lineState];
uiNamespace setVariable ["YOSHI_taskArty_strikePattern", _linePositions];
missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_LINE", [_token, _linePositions], true];
private _lineGoDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_LINE_GO", ""]) isEqualTo _token || diag_tickTime > _lineGoDeadline};
private _lineRequestOk = (count _linePositions) isEqualTo 4 && {(_lineState get "pattern") isEqualTo "line"} && {(_lineState get "dir") isEqualTo 90};
["vigil.artillery.request.line", _lineRequestOk, format ["state=%1|positions=%2", _lineState, _linePositions]] call _assert;
if (_lineRequestOk) then {call YOSHI_taskArty_submit};
private _completionDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_COMPLETE", ""]) isEqualTo _token
        || diag_tickTime > _completionDeadline
};
''',
    metadata={
        "product": "visual-support-tablet",
        "feature": "vigil-artillery-execution",
        "targeting_modes": "grid-only",
        "patterns": "circle,line",
        "sources": "native-artillery,vls",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A valid grid request fires exactly the requested circle/line rounds near their intended geometry; invalid requests do not fire; VLS launches, guides, and reaches its target region.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The scenario correlates product requests with physical projectiles and outcomes while avoiding promises about private governor variables, event order, or VLS handshake internals.",
        dependencies=("Tribunal artillery observer", "Vigil task governor", "Arma native artillery", "Arma VLS"),
        evidence_types=frozenset({"fire-event", "trajectory", "spatial-distribution", "negative-control", "locality"}),
        locality_requirements="Client-a owns request/UI state; server owns task, platforms, projectiles, trajectory evidence, and completion.",
    ),
)
