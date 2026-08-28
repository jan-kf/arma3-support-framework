#include "..\..\ui\idc.hpp"

YFU_bridge_getClassProfile = {
	params ["_className"];

	switch (_className) do {
		case "Land_Plank_01_4m_F": {
			[4.1792, 0.8982, 0.1311, 0]
		};
		default {
			[]
		};
	}
};

YFU_bridge_getClassMetrics = {
	params ["_className"];

	private _profile = [_className] call YFU_bridge_getClassProfile;
	if (_profile isNotEqualTo []) exitWith {
		_profile
	};

	private _cache = missionNamespace getVariable ["YFU_bridge_metrics_cache", createHashMap];
	missionNamespace setVariable ["YFU_bridge_metrics_cache", _cache];

	private _cached = _cache getOrDefault [_className, []];
	if (_cached isNotEqualTo []) exitWith {
		_cache get _className
	};

	private _probe = createVehicle [_className, [0, 0, 1000], [], 0, "CAN_COLLIDE"];
	private _metrics = [_probe] call YFU_bridge_getSegmentMetrics;
	deleteVehicle _probe;

	_cache set [_className, _metrics];
	_metrics
};

YFU_bridge_debugMeasurements = {
	params ["_object"];

	if (isNull _object) exitWith {
		systemChat "YFU bridge debug: object is null";
	};

	private _bounds = boundingBoxReal _object;
	private _bbMin = _bounds select 0;
	private _bbMax = _bounds select 1;
	private _dir = vectorDirVisual _object;
	private _up = vectorUpVisual _object;
	private _right = [_object] call YFU_bridge_getRightVector;
	private _posASL = getPosASL _object;
	private _metrics = [_object] call YFU_bridge_getSegmentMetrics;

	private _report = [
		format ["class=%1", typeOf _object],
		format ["posASL=%1", _posASL],
		format ["bbMin=%1", _bbMin],
		format ["bbMax=%1", _bbMax],
		format ["length=%1", _metrics select 0],
		format ["width=%1", _metrics select 1],
		format ["height=%1", _metrics select 2],
		format ["centerZ=%1", _metrics select 3],
		format ["dir=%1", _dir],
		format ["up=%1", _up],
		format ["right=%1", _right]
	] joinString endl;

	copyToClipboard _report;
	diag_log text format ["[YFU bridge debug]%1%2", endl, _report];
	systemChat "YFU bridge debug copied to clipboard";

	_report
};

YFU_bridge_getSegmentMetrics = {
	params ["_bridgeObject"];

	private _profile = [typeOf _bridgeObject] call YFU_bridge_getClassProfile;
	if (_profile isNotEqualTo []) exitWith {
		_profile
	};

	private _bounds = boundingBoxReal _bridgeObject;
	private _bbMin = _bounds select 0;
	private _bbMax = _bounds select 1;

	private _length = abs ((_bbMax select 1) - (_bbMin select 1));
	private _width = abs ((_bbMax select 0) - (_bbMin select 0));
	private _height = abs ((_bbMax select 2) - (_bbMin select 2));
	private _centerZ = ((_bbMin select 2) + (_bbMax select 2)) * 0.5;

	[
		_length max 0.1,
		_width max 0.1,
		_height max 0.1,
		_centerZ
	]
};

YFU_bridge_getForwardPlacement = {
	params ["_anchorBridge", "_stepIndex"];

	private _metrics = [_anchorBridge] call YFU_bridge_getSegmentMetrics;
	private _stepLength = _metrics select 0;
	private _dir = vectorDirVisual _anchorBridge;
	private _basePos = getPosASL _anchorBridge;

	_basePos vectorAdd (_dir vectorMultiply (_stepLength * _stepIndex))
};

YFU_bridge_getRightVector = {
	params ["_object"];

	vectorNormalized ((vectorUpVisual _object) vectorCrossProduct (vectorDirVisual _object))
};

YFU_bridge_getHorizontalDir = {
	params ["_object"];

	private _dir = vectorDirVisual _object;
	private _flat = [_dir select 0, _dir select 1, 0];
	private _mag = vectorMagnitude _flat;

	if (_mag < 0.001) exitWith {
		[0, 1, 0]
	};

	vectorNormalized _flat
};

YFU_bridge_getBuildOrientation = {
	params ["_sourceObject", ["_widthwise", false], ["_planRequest", []]];

	private _matchBoxAngle = if (_planRequest isEqualTo []) then {
		_sourceObject getVariable ["YFU_bridge_match_box_angle", true]
	} else {
		_planRequest # 2
	};
	private _buildDir = if (_matchBoxAngle) then {
		vectorNormalized (vectorDirVisual _sourceObject)
	} else {
		[_sourceObject] call YFU_bridge_getHorizontalDir
	};
	private _up = if (_matchBoxAngle) then {
		vectorNormalized (vectorUpVisual _sourceObject)
	} else {
		[0, 0, 1]
	};
	private _pitchOffset = if (_planRequest isEqualTo []) then {
		[_sourceObject] call YFU_bridge_getPitchOffsetDegrees
	} else {
		_planRequest # 6
	};
	if ((abs _pitchOffset) > 0.001) then {
		private _sin = sin _pitchOffset;
		private _cos = cos _pitchOffset;
		private _baseDir = _buildDir;
		private _baseUp = _up;
		_buildDir = vectorNormalized ((_baseDir vectorMultiply _cos) vectorAdd (_baseUp vectorMultiply _sin));
		_up = vectorNormalized ((_baseUp vectorMultiply _cos) vectorAdd (_baseDir vectorMultiply (-_sin)));
	};
	private _right = vectorNormalized (_up vectorCrossProduct _buildDir);
	private _segmentDir = if (_widthwise) then { _right } else { _buildDir };

	[_buildDir, _segmentDir, _up]
};

YFU_bridge_setBuilderMode = {
	params ["_boxObject", "_matchBoxAngle"];

	if (isNull _boxObject) exitWith {};

	_boxObject setVariable ["YFU_bridge_match_box_angle", _matchBoxAngle, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	systemChat format [
		"Bridge builder mode: %1",
		if (_matchBoxAngle) then { "Match Box Angle" } else { "Keep Level" }
	];
};

YFU_bridge_setPlanMode = {
	params ["_boxObject", "_widthwise"];

	if (isNull _boxObject) exitWith {};

	_boxObject setVariable ["YFU_bridge_plan_widthwise", _widthwise, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	systemChat format [
		"Bridge plan mode: %1",
		if (_widthwise) then { "Wide" } else { "Lengthwise" }
	];
};

YFU_bridge_setRampMode = {
	params ["_boxObject", "_enabled"];

	if (isNull _boxObject) exitWith {};

	_boxObject setVariable ["YFU_bridge_ramp_mode", _enabled, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	systemChat format ["Bridge ramp mode: %1", if (_enabled) then {"On"} else {"Off"}];
};

YFU_bridge_setAllowClipping = {
	params ["_boxObject", "_enabled"];

	if (isNull _boxObject) exitWith {};

	_boxObject setVariable ["YFU_bridge_allow_clipping", _enabled, false];
	systemChat format ["Bridge allow clipping: %1", if (_enabled) then {"On"} else {"Off"}];
};

YFU_bridge_getVerticalOffset = {
	params ["_boxObject", ["_planRequest", []]];

	private _rampMode = if (_planRequest isEqualTo []) then {_boxObject getVariable ["YFU_bridge_ramp_mode", false]} else {_planRequest # 3};
	if (_rampMode) exitWith {
		-1
	};

	if (_planRequest isNotEqualTo []) exitWith {-0.2};
	_boxObject getVariable ["YFU_bridge_vertical_offset", -0.2]
};

YFU_bridge_getPerPlankBuildDelay = {
	(missionNamespace getVariable ["YFU_bridge_perPlankBuildDelay", 1]) max 0
};

YFU_bridge_newRequestId = {
	params [["_action", "operation"]];
	format ["bridge-%1-%2-%3-%4", _action, clientOwner, round (diag_tickTime * 1000), floor (random 1000000)]
};

YFU_bridge_capturePlanRequest = {
	params ["_boxObject"];
	[
		"bridge-plan-v1",
		_boxObject getVariable ["YFU_bridge_plan_widthwise", false],
		_boxObject getVariable ["YFU_bridge_match_box_angle", true],
		_boxObject getVariable ["YFU_bridge_ramp_mode", false],
		[_boxObject] call YFU_bridge_getRampPlankCount,
		[_boxObject] call YFU_bridge_getManualPlankCount,
		[_boxObject] call YFU_bridge_getPitchOffsetDegrees
	]
};

YFU_bridge_validatePlanRequest = {
	params ["_planRequest"];
	if !(typeName _planRequest isEqualTo "ARRAY") exitWith {[false, "invalid_plan_type", []]};
	if ((count _planRequest) isNotEqualTo 7) exitWith {[false, "invalid_plan_shape", []]};
	if ((_planRequest # 0) isNotEqualTo "bridge-plan-v1") exitWith {[false, "unsupported_plan_version", []]};
	if !((typeName (_planRequest # 1)) isEqualTo "BOOL") exitWith {[false, "invalid_plan_layout", []]};
	if !((typeName (_planRequest # 2)) isEqualTo "BOOL") exitWith {[false, "invalid_plan_orientation", []]};
	if !((typeName (_planRequest # 3)) isEqualTo "BOOL") exitWith {[false, "invalid_plan_ramp", []]};
	if !((typeName (_planRequest # 4)) isEqualTo "SCALAR") exitWith {[false, "invalid_plan_ramp_count", []]};
	if !((typeName (_planRequest # 5)) isEqualTo "SCALAR") exitWith {[false, "invalid_plan_segment_count", []]};
	if !((typeName (_planRequest # 6)) isEqualTo "SCALAR") exitWith {[false, "invalid_plan_pitch", []]};
	private _rampCount = round (_planRequest # 4);
	private _manualCount = round (_planRequest # 5);
	private _pitch = _planRequest # 6;
	if (_rampCount < 1 || {_rampCount > 20}) exitWith {[false, "plan_ramp_count_out_of_bounds", []]};
	if (_manualCount < 0 || {_manualCount > 500}) exitWith {[false, "plan_segment_count_out_of_bounds", []]};
	if (_pitch < -15 || {_pitch > 15}) exitWith {[false, "plan_pitch_out_of_bounds", []]};
	[true, "accepted", ["bridge-plan-v1", _planRequest # 1, _planRequest # 2, _planRequest # 3, _rampCount, _manualCount, _pitch]]
};

YFU_bridge_validateServerRequest = {
	params ["_boxObject", "_requester", "_requestOwner"];

	if (!isServer) exitWith {[false, "not_server"]};
	if (isNull _boxObject || {typeOf _boxObject isNotEqualTo "YFU_Bridge_Box"} || {!alive _boxObject}) exitWith {[false, "invalid_box"]};
	if (isNull _requester || {!isPlayer _requester} || {!alive _requester}) exitWith {[false, "invalid_requester"]};
	if (_requestOwner > 0 && {owner _requester isNotEqualTo _requestOwner}) exitWith {[false, "requester_owner_mismatch"]};
	if ((_requester distance _boxObject) >= 8) exitWith {[false, "requester_out_of_range"]};

	[true, "accepted"]
};

YFU_bridge_publishResult = {
	params ["_boxObject", "_requestId", "_action", "_status", "_reason", ["_objectIds", []], ["_requestOwner", 0]];
	if (isNull _boxObject) exitWith {};
	_boxObject setVariable ["YFU_bridge_last_result", [_requestId, _action, _status, _reason, _objectIds, serverTime, _requestOwner], true];
};

YFU_bridge_segmentBelongsToBox = {
	params ["_segment", "_boxObject"];
	!isNull _segment
	&& {!isNull _boxObject}
	&& {(_segment getVariable ["YFU_bridge_builder_box", ""]) isEqualTo netId _boxObject}
};

YFU_bridge_getManualPlankCount = {
	params ["_boxObject"];

	private _count = _boxObject getVariable ["YFU_bridge_manual_plank_count", 0];
	(round _count) max 0
};

YFU_bridge_getPitchOffsetDegrees = {
	params ["_boxObject"];

	_boxObject getVariable ["YFU_bridge_pitch_offset_degrees", 0]
};

YFU_bridge_getPreviewSurfaceOffset = {
	params [["_className", "Land_Plank_01_4m_F"]];

	private _metrics = [_className] call YFU_bridge_getClassMetrics;
	(_metrics select 2) * 0.5
};

YFU_bridge_ensureBoxDefaults = {
	params ["_boxObject"];

	if (isNull _boxObject) exitWith {};

	if (isNil {_boxObject getVariable "YFU_bridge_match_box_angle"}) then {
		_boxObject setVariable ["YFU_bridge_match_box_angle", true, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_plan_widthwise"}) then {
		_boxObject setVariable ["YFU_bridge_plan_widthwise", false, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_plan_max_distance"}) then {
		_boxObject setVariable ["YFU_bridge_plan_max_distance", 50, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_chain_search_radius"}) then {
		_boxObject setVariable ["YFU_bridge_chain_search_radius", 100, true];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_ramp_mode"}) then {
		_boxObject setVariable ["YFU_bridge_ramp_mode", false, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_ramp_plank_count"}) then {
		_boxObject setVariable ["YFU_bridge_ramp_plank_count", 2, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_manual_plank_count"}) then {
		_boxObject setVariable ["YFU_bridge_manual_plank_count", 0, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_pitch_offset_degrees"}) then {
		_boxObject setVariable ["YFU_bridge_pitch_offset_degrees", 0, false];
	};
	if (isNil {_boxObject getVariable "YFU_bridge_allow_clipping"}) then {
		_boxObject setVariable ["YFU_bridge_allow_clipping", true, false];
	};
};

YFU_bridge_getRampPlankCount = {
	params ["_boxObject"];

	private _count = _boxObject getVariable ["YFU_bridge_ramp_plank_count", 2];
	(round _count) max 1
};

YFU_bridge_getDialogDisplay = {
	uiNamespace getVariable ["YFU_BridgeBuilder_Display", displayNull]
};

YFU_bridge_dialogGetBox = {
	uiNamespace getVariable ["YFU_bridge_builder_box", objNull]
};

YFU_bridge_dialogClose = {
	closeDialog 0;
};

YFU_bridge_releasePlanner = {
	params ["_boxObject", ["_requester", objNull], ["_leaseId", ""]];
	if (!isServer) exitWith {
		[_boxObject, player, _leaseId] remoteExecCall ["YFU_bridge_releasePlanner", 2];
	};
	private _owner = remoteExecutedOwner;
	private _lease = _boxObject getVariable ["YFU_bridge_planner_lease", []];
	if (
		(count _lease) isEqualTo 5
		&& {(_lease # 0) isEqualTo netId _requester}
		&& {(_lease # 1) isEqualTo _owner}
		&& {(_lease # 3) isEqualTo _leaseId}
	) then {
		_boxObject setVariable ["YFU_bridge_planner_lease", [], true];
	};
};

YFU_bridge_renewPlanner = {
	params ["_boxObject", ["_requester", objNull], ["_leaseId", ""]];
	if (!isServer) exitWith {
		[_boxObject, player, _leaseId] remoteExecCall ["YFU_bridge_renewPlanner", 2];
	};
	private _owner = remoteExecutedOwner;
	private _lease = _boxObject getVariable ["YFU_bridge_planner_lease", []];
	if (
		(count _lease) isEqualTo 5
		&& {(_lease # 0) isEqualTo netId _requester}
		&& {(_lease # 1) isEqualTo _owner}
		&& {(_lease # 3) isEqualTo _leaseId}
	) then {
		_lease set [4, serverTime + 15];
		_boxObject setVariable ["YFU_bridge_planner_lease", _lease, true];
	};
};

YFU_bridge_onDialogUnload = {
	private _boxObject = call YFU_bridge_dialogGetBox;
	private _leaseId = uiNamespace getVariable ["YFU_bridge_planner_lease_id", ""];
	if (
		!isNull _boxObject
		&& {_leaseId isNotEqualTo ""}
		&& {!(uiNamespace getVariable ["YFU_bridge_planner_submitting", false])}
	) then {
		[_boxObject, player, _leaseId] remoteExecCall ["YFU_bridge_releasePlanner", 2];
	};
	if !(uiNamespace getVariable ["YFU_bridge_planner_submitting", false]) then {
		uiNamespace setVariable ["YFU_bridge_planner_lease_id", ""];
	};
};

YFU_bridge_dialogRefresh = {
	disableSerialization;

	private _display = call YFU_bridge_getDialogDisplay;
	if (isNull _display) exitWith {};

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	private _widthwise = _boxObject getVariable ["YFU_bridge_plan_widthwise", false];
	private _previewEnabled = (missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull]) isEqualTo _boxObject;
	private _matchBoxAngle = _boxObject getVariable ["YFU_bridge_match_box_angle", true];
	private _rampMode = _boxObject getVariable ["YFU_bridge_ramp_mode", false];
	private _rampCount = [_boxObject] call YFU_bridge_getRampPlankCount;
	private _manualPlankCount = [_boxObject] call YFU_bridge_getManualPlankCount;
	private _pitchOffset = [_boxObject] call YFU_bridge_getPitchOffsetDegrees;
	private _buildDelay = call YFU_bridge_getPerPlankBuildDelay;
	private _isBuilding = _boxObject getVariable ["YFU_bridge_building", false];
	private _isRemoving = _boxObject getVariable ["YFU_bridge_removing", false];
	private _orientationLabel = if (_matchBoxAngle) then {"Match Box"} else {"Keep Level"};
	private _layoutLabel = if (_widthwise) then {"Wide"} else {"Lengthwise"};
	private _summary = parseText format [
		"<t size='0.95'>Layout: %1<br/>Orientation: %2 (%3 deg)<br/>Preview: %4<br/>Planks: %5<br/>Ramp: %6 x%7<br/>Clipping: Always On<br/>Per-plank delay: %8s<br/>State: %9</t>",
		_layoutLabel,
		_orientationLabel,
		_pitchOffset,
		if (_previewEnabled) then {"Enabled"} else {"Disabled"},
		if (_manualPlankCount > 0) then {str _manualPlankCount} else {"Auto"},
		if (_rampMode) then {"Enabled"} else {"Disabled"},
		_rampCount,
		_buildDelay,
		if (_isRemoving) then {"Removing"} else {if (_isBuilding) then {"Building"} else {"Idle"}}
	];

	uiNamespace setVariable ["YFU_bridge_dialog_refreshing", true];
	(_display displayCtrl YFU_IDC_BRIDGE_SUMMARY) ctrlSetStructuredText _summary;
	lbSetCurSel [YFU_IDC_BRIDGE_LAYOUT_TOOLBOX, if (_widthwise) then {1} else {0}];
	lbSetCurSel [YFU_IDC_BRIDGE_PREVIEW_TOOLBOX, if (_previewEnabled) then {0} else {1}];
	lbSetCurSel [YFU_IDC_BRIDGE_MODE_TOOLBOX, if (_matchBoxAngle) then {0} else {1}];
	lbSetCurSel [YFU_IDC_BRIDGE_RAMP_TOOLBOX, if (_rampMode) then {0} else {1}];
	(_display displayCtrl YFU_IDC_BRIDGE_RAMP_COUNT) ctrlSetText str _rampCount;
	(_display displayCtrl YFU_IDC_BRIDGE_RAMP_COUNT) ctrlEnable _rampMode;
	(_display displayCtrl YFU_IDC_BRIDGE_PLANK_COUNT) ctrlSetText str _manualPlankCount;
	(_display displayCtrl YFU_IDC_BRIDGE_PITCH_OFFSET) ctrlSetText str _pitchOffset;
	(_display displayCtrl YFU_IDC_BRIDGE_BUILD) ctrlEnable !(_isBuilding || _isRemoving);
	(_display displayCtrl YFU_IDC_BRIDGE_REMOVE) ctrlEnable !(_isBuilding || _isRemoving);
	(_display displayCtrl YFU_IDC_BRIDGE_REMOVE) ctrlSetText "Remove Bridge";
	uiNamespace setVariable ["YFU_bridge_dialog_refreshing", false];
};

YFU_bridge_dialogToolboxChanged = {
	params ["_control", "_selectedIndex"];

	if (uiNamespace getVariable ["YFU_bridge_dialog_refreshing", false]) exitWith {};

	switch (ctrlIDC _control) do {
		case YFU_IDC_BRIDGE_LAYOUT_TOOLBOX: {
			[_selectedIndex == 1] call YFU_bridge_dialogSetLayout;
		};
		case YFU_IDC_BRIDGE_PREVIEW_TOOLBOX: {
			[_selectedIndex == 0] call YFU_bridge_dialogSetPreview;
		};
		case YFU_IDC_BRIDGE_MODE_TOOLBOX: {
			[_selectedIndex == 0] call YFU_bridge_dialogSetOrientation;
		};
		case YFU_IDC_BRIDGE_RAMP_TOOLBOX: {
			[_selectedIndex == 0] call YFU_bridge_dialogSetRampMode;
		};
	};
};

YFU_bridge_dialogRampCountChanged = {
	disableSerialization;

	private _display = call YFU_bridge_getDialogDisplay;
	if (isNull _display) exitWith {};

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	private _ctrl = _display displayCtrl YFU_IDC_BRIDGE_RAMP_COUNT;
	private _value = parseNumber (ctrlText _ctrl);
	if (_value <= 0) then {
		_value = 2;
	};
	_value = ((round _value) max 1) min 20;
	_boxObject setVariable ["YFU_bridge_ramp_plank_count", _value, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	_ctrl ctrlSetText str _value;
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogPlankCountChanged = {
	disableSerialization;

	private _display = call YFU_bridge_getDialogDisplay;
	if (isNull _display) exitWith {};

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	private _ctrl = _display displayCtrl YFU_IDC_BRIDGE_PLANK_COUNT;
	private _value = parseNumber (ctrlText _ctrl);
	if (_value < 0) then {
		_value = 0;
	};
	_value = ((round _value) max 0) min 500;
	_boxObject setVariable ["YFU_bridge_manual_plank_count", _value, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	_ctrl ctrlSetText str _value;
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogPitchOffsetChanged = {
	disableSerialization;

	private _display = call YFU_bridge_getDialogDisplay;
	if (isNull _display) exitWith {};

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	private _ctrl = _display displayCtrl YFU_IDC_BRIDGE_PITCH_OFFSET;
	private _value = parseNumber (ctrlText _ctrl);
	_value = (_value max -15) min 15;
	_boxObject setVariable ["YFU_bridge_pitch_offset_degrees", _value, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	_ctrl ctrlSetText str _value;
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogAutoCalculate = {
	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	private _widthwise = _boxObject getVariable ["YFU_bridge_plan_widthwise", false];
	private _planRange = [_boxObject] call YFU_bridge_getPlanRange;
	private _plan = [_boxObject, "Land_Plank_01_4m_F", _widthwise, _planRange] call YFU_bridge_computePlan;
	if (_plan isEqualTo []) exitWith {};

	private _segmentCount = _plan select 11;
	private _hasEndHit = _plan select 12;
	private _queue = [_boxObject, _segmentCount, "Land_Plank_01_4m_F", _widthwise, _hasEndHit] call YFU_bridge_buildQueueFromObject;
	_boxObject setVariable ["YFU_bridge_manual_plank_count", count _queue, false];
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogSetLayout = {
	params ["_widthwise"];

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	[_boxObject, _widthwise] call YFU_bridge_setPlanMode;
	if ((missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull]) isEqualTo _boxObject) then {
		missionNamespace setVariable ["YFU_bridge_active_plan_box", _boxObject];
	};
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogSetPreview = {
	params ["_enabled"];

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	if (_enabled) then {
		[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
		missionNamespace setVariable ["YFU_bridge_active_plan_box", _boxObject];
	} else {
		if ((missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull]) isEqualTo _boxObject) then {
			call YFU_bridge_endPlanPreview;
		};
	};

	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogSetOrientation = {
	params ["_matchBoxAngle"];

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	[_boxObject, _matchBoxAngle] call YFU_bridge_setBuilderMode;
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogSetRampMode = {
	params ["_enabled"];

	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	[_boxObject, _enabled] call YFU_bridge_setRampMode;
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_dialogSubmit = {
	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};

	call YFU_bridge_dialogRampCountChanged;
	call YFU_bridge_dialogPlankCountChanged;
	call YFU_bridge_dialogPitchOffsetChanged;
	uiNamespace setVariable ["YFU_bridge_planner_submitting", true];
	closeDialog 0;
	[_boxObject] call YFU_bridge_startBuildFromPlan;
	uiNamespace setVariable ["YFU_bridge_planner_submitting", false];
	uiNamespace setVariable ["YFU_bridge_planner_lease_id", ""];
};

YFU_bridge_dialogRemove = {
	private _boxObject = call YFU_bridge_dialogGetBox;
	if (isNull _boxObject) exitWith {};
	if ((_boxObject getVariable ["YFU_bridge_building", false]) || (_boxObject getVariable ["YFU_bridge_removing", false])) exitWith {};
	closeDialog 0;
	[_boxObject] call YFU_bridge_startRemoveFromBox;
};

YFU_bridge_onDialogLoad = {
	call YFU_bridge_dialogRefresh;
};

YFU_bridge_openBuilderDialogLocal = {
	params ["_boxObject", "_leaseId"];
	[_boxObject, _leaseId] spawn {
		params ["_boxObject", "_leaseId"];
		uiNamespace setVariable ["YFU_bridge_planner_lease_id", _leaseId];
		uiNamespace setVariable ["YFU_bridge_planner_submitting", false];
		uiNamespace setVariable ["YFU_bridge_builder_box", _boxObject];

		private _display = call YFU_bridge_getDialogDisplay;
		if (isNull _display) then {
			private _tabletDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
			if (!isNull _tabletDisplay) then {
				_display = _tabletDisplay createDisplay "YFU_BridgeBuilder_Dialog";
				if (isNull _display) then {createDialog "YFU_BridgeBuilder_Dialog";};
			} else {
				createDialog "YFU_BridgeBuilder_Dialog";
			};
		} else {
			call YFU_bridge_dialogRefresh;
		};

		while {
			uiSleep 5;
			!isNull (call YFU_bridge_getDialogDisplay)
			&& {(call YFU_bridge_dialogGetBox) isEqualTo _boxObject}
		} do {
			private _leaseId = uiNamespace getVariable ["YFU_bridge_planner_lease_id", ""];
			if (_leaseId isNotEqualTo "") then {
				[_boxObject, player, _leaseId] remoteExecCall ["YFU_bridge_renewPlanner", 2];
			};
		};
	};
};

YFU_bridge_openBuilderDialog = {
	params ["_boxObject", ["_requester", objNull], ["_leaseId", ""]];

	if (isNull _boxObject) exitWith {};
	[_boxObject] call YFU_bridge_ensureBoxDefaults;
	if (!isServer) exitWith {
		private _leaseId = ["planner"] call YFU_bridge_newRequestId;
		[_boxObject, player, _leaseId] remoteExecCall ["YFU_bridge_openBuilderDialog", 2];
	};
	private _owner = remoteExecutedOwner;
	private _validation = [_boxObject, _requester, _owner] call YFU_bridge_validateServerRequest;
	if !(_validation # 0) exitWith {
		_boxObject setVariable ["YFU_bridge_planner_last_result", [_leaseId, "rejected", _validation # 1, _owner, serverTime], true];
	};
	private _lease = _boxObject getVariable ["YFU_bridge_planner_lease", []];
	private _active = (count _lease) isEqualTo 5 && {(_lease # 4) > serverTime};
	if (_active && {(_lease # 1) isNotEqualTo _owner || {(_lease # 0) isNotEqualTo netId _requester}}) exitWith {
		_boxObject setVariable ["YFU_bridge_planner_last_result", [_leaseId, "rejected", "planner_in_use", _owner, serverTime], true];
		format ["Bridge planner is currently in use by %1.", _lease # 2] remoteExecCall ["hint", _owner];
	};
	_lease = [netId _requester, _owner, name _requester, _leaseId, serverTime + 15];
	_boxObject setVariable ["YFU_bridge_planner_lease", _lease, true];
	_boxObject setVariable ["YFU_bridge_planner_last_result", [_leaseId, "granted", "accepted", _owner, serverTime], true];
	// The remote handler explicitly spawns the UI work because createDialog is
	// not reliable when executed directly in a remote-call context.
	[_boxObject, _leaseId] remoteExecCall ["YFU_bridge_openBuilderDialogLocal", _owner];
};

YFU_bridge_getPreviewColors = {
	params ["_boxObject"];

	private _matchBoxAngle = _boxObject getVariable ["YFU_bridge_match_box_angle", true];

	if (_matchBoxAngle) exitWith {
		[
			[0.1, 0.4, 1, 1],
			[0.5, 0.8, 1, 1]
		]
	};

	[
		[0.1, 1, 0.1, 1],
		[0.5, 1, 0.5, 1]
	]
};

YFU_bridge_getPreviewSegmentColors = {
	params ["_boxObject", ["_segmentType", "flat"]];

	private _baseColors = [_boxObject] call YFU_bridge_getPreviewColors;

	switch (_segmentType) do {
		case "ramp_up";
		case "ramp_down": {
			[
				[1, 0.85, 0.2, 1],
				[1, 1, 0.45, 1]
			]
		};
		case "clip": {
			[
				[1, 0.45, 0.1, 1],
				[1, 0.7, 0.3, 1]
			]
		};
		default {
			_baseColors
		};
	}
};

YFU_bridge_getEffectivePlanCount = {
	params ["_boxObject", "_baseCount", "_hasExistingChain", ["_finalizeEnd", false], ["_planRequest", []]];

	private _effectiveCount = _baseCount max 0;
	private _rampMode = if (_planRequest isEqualTo []) then {_boxObject getVariable ["YFU_bridge_ramp_mode", false]} else {_planRequest # 3};
	private _rampSegmentCount = if (_planRequest isEqualTo []) then {[_boxObject] call YFU_bridge_getRampPlankCount} else {_planRequest # 4};

	if (_rampMode) then {
		if (!_hasExistingChain) then {
			_effectiveCount = _effectiveCount + _rampSegmentCount;
		};
		if (_finalizeEnd) then {
			_effectiveCount = _effectiveCount + _rampSegmentCount;
		};
	};

	if (_finalizeEnd) then {
		_effectiveCount = _effectiveCount + 1;
	};

	_effectiveCount
};

YFU_bridge_computePlan = {
	params ["_sourceObject", ["_className", "Land_Plank_01_4m_F"], ["_widthwise", false], ["_maxDistance", 500], ["_planRequest", []]];

	if (isNull _sourceObject) exitWith {[]};
	if (_planRequest isNotEqualTo []) then {_widthwise = _planRequest # 1;};
	_maxDistance = (_maxDistance max 0) min 50;

	private _modeData = [_sourceObject, _widthwise, _className, _planRequest] call YFU_bridge_getBuildModeData;
	private _buildDir = _modeData select 0;
	private _segmentDir = _modeData select 1;
	private _up = _modeData select 2;
	private _step = _modeData select 3;
	private _bridgeMetrics = [_className] call YFU_bridge_getClassMetrics;
	private _bridgeLength = _bridgeMetrics select 0;
	private _bridgeWidth = _bridgeMetrics select 1;
	private _sourcePos = getPosASL _sourceObject;
	private _sourceForwardSize = [_sourceObject] call YFU_bridge_getSourceForwardSize;
	private _chainEnd = [_sourceObject, _className, _widthwise, _maxDistance + 30, _planRequest] call YFU_bridge_findNearbyChainEnd;
	private _startCenter = if (isNull _chainEnd) then {
		_sourcePos vectorAdd (_buildDir vectorMultiply ((_sourceForwardSize * 0.5) + (_step * 0.5)))
	} else {
		(getPosASL _chainEnd) vectorAdd (_buildDir vectorMultiply _step)
	};
	private _laserStart = if (isNull _chainEnd) then {
		_sourcePos vectorAdd (_buildDir vectorMultiply (_sourceForwardSize * 0.5))
	} else {
		(getPosASL _chainEnd) vectorAdd (_buildDir vectorMultiply (_step * 0.5))
	};
	private _laserEnd = _laserStart vectorAdd (_buildDir vectorMultiply _maxDistance);
	private _hits = lineIntersectsSurfaces [_laserStart, _laserEnd, _sourceObject, objNull, true, 16, "FIRE", "GEOM"];
	_hits = _hits select {
		private _hitObject = _x # 2;
		private _parentObject = _x # 3;
		(isNull _hitObject && {isNull _parentObject})
		|| {!isNull _hitObject && {_hitObject isKindOf "House"}}
		|| {!isNull _parentObject && {_parentObject isKindOf "House"}}
	};
	private _planEnd = _laserEnd;
	private _hasEndHit = false;
	private _distance = _startCenter distance (_laserStart vectorAdd (_buildDir vectorMultiply _maxDistance));

	if ((count _hits) > 0) then {
		_planEnd = (_hits select 0) select 0;
		_distance = _startCenter distance _planEnd;
		_hasEndHit = true;
	};

	private _baseSegmentCount = floor ((_distance + (_step * 0.5)) / _step);
	private _effectiveCount = [_sourceObject, _baseSegmentCount, !(isNull _chainEnd), _hasEndHit, _planRequest] call YFU_bridge_getEffectivePlanCount;
	private _boundAxis = vectorNormalized (_up vectorCrossProduct _buildDir);
	private _boundSpacing = if (_widthwise) then { _bridgeLength } else { _bridgeWidth };

	[
		_laserStart,
		_planEnd,
		_effectiveCount max 0,
		_widthwise,
		_buildDir,
		_segmentDir,
		_up,
		_step,
		_boundAxis,
		_boundSpacing,
		_chainEnd,
		_baseSegmentCount,
		_hasEndHit
	]
};

YFU_bridge_beginPlanPreview = {
	params ["_boxObject", ["_widthwise", false]];

	if (isNull _boxObject) exitWith {};

	[_boxObject, _widthwise] call YFU_bridge_setPlanMode;
	[_boxObject] call YFU_bridge_invalidatePlanPreviewCache;
	missionNamespace setVariable ["YFU_bridge_active_plan_box", _boxObject];
	systemChat "Bridge plan preview enabled";
};

YFU_bridge_endPlanPreview = {
	[objNull] call YFU_bridge_invalidatePlanPreviewCache;
	missionNamespace setVariable ["YFU_bridge_active_plan_box", objNull];
	systemChat "Bridge plan preview disabled";
};

YFU_bridge_debugPlanPreview = {
	params ["_boxObject"];

	if (isNull _boxObject) exitWith {
		systemChat "Bridge preview debug: box is null";
	};

	private _widthwise = _boxObject getVariable ["YFU_bridge_plan_widthwise", false];
	private _plan = [_boxObject, "Land_Plank_01_4m_F", _widthwise, 500] call YFU_bridge_computePlan;
	if (_plan isEqualTo []) exitWith {
		systemChat "Bridge preview debug: no plan";
	};

	private _start = _plan select 0;
	private _end = _plan select 1;
	private _segments = _plan select 2;
	private _buildDir = _plan select 4;
	private _up = _plan select 6;
	private _boundAxis = vectorNormalized (_up vectorCrossProduct _buildDir);
	private _boundSpacing = _plan select 9;
	private _halfSpacing = _boundSpacing * 0.5;
	private _startA = _start vectorAdd (_boundAxis vectorMultiply _halfSpacing);
	private _endA = _end vectorAdd (_boundAxis vectorMultiply _halfSpacing);
	private _startB = _start vectorAdd (_boundAxis vectorMultiply (-_halfSpacing));
	private _endB = _end vectorAdd (_boundAxis vectorMultiply (-_halfSpacing));

	private _report = [
		format ["widthwise=%1", _widthwise],
		format ["segments=%1", _segments],
		format ["start=%1", _start],
		format ["end=%1", _end],
		format ["buildDir=%1", _buildDir],
		format ["up=%1", _up],
		format ["boundAxis=%1", _boundAxis],
		format ["boundSpacing=%1", _boundSpacing],
		format ["startA=%1", _startA],
		format ["endA=%1", _endA],
		format ["startB=%1", _startB],
		format ["endB=%1", _endB],
		format ["startDelta=%1", _startA vectorDiff _startB],
		format ["endDelta=%1", _endA vectorDiff _endB]
	] joinString endl;

	copyToClipboard _report;
	diag_log text format ["[YFU bridge preview debug]%1%2", endl, _report];
	systemChat "Bridge preview debug copied to clipboard";

	_report
};

YFU_bridge_getPlannedQueue = {
	params ["_boxObject"];

	if (isNull _boxObject) exitWith {[]};

	private _widthwise = _boxObject getVariable ["YFU_bridge_plan_widthwise", false];
	private _planRange = [_boxObject] call YFU_bridge_getPlanRange;
	private _plan = [_boxObject, "Land_Plank_01_4m_F", _widthwise, _planRange] call YFU_bridge_computePlan;
	if (_plan isEqualTo []) exitWith {[]};

	private _segmentCount = _plan select 11;
	private _hasEndHit = _plan select 12;
	private _manualCount = [_boxObject] call YFU_bridge_getManualPlankCount;
	if (_manualCount > 0) then {
		_segmentCount = _manualCount;
	};
	if (_segmentCount <= 0) exitWith {[]};

	[_boxObject, _segmentCount, "Land_Plank_01_4m_F", _widthwise, _hasEndHit] call YFU_bridge_buildQueueFromObject
};

YFU_bridge_getRemovalQueue = {
	params ["_boxObject", ["_className", "Land_Plank_01_4m_F"]];

	if (isNull _boxObject) exitWith {[]};

	private _widthwise = _boxObject getVariable ["YFU_bridge_box_mode_widthwise", false];
	private _modeData = [_boxObject, _widthwise, _className] call YFU_bridge_getBuildModeData;
	private _buildDir = _modeData select 0;
	private _segmentDir = _modeData select 1;
	private _step = _modeData select 3;
	private _searchRadius = _boxObject getVariable ["YFU_bridge_chain_search_radius", 600];
	private _boxPos = getPosASL _boxObject;
	private _kickoffRadius = 5;
	private _kickoffCandidates = nearestObjects [ASLToAGL _boxPos, [_className], _kickoffRadius, true] select {[_x, _boxObject] call YFU_bridge_segmentBelongsToBox};
	private _candidates = nearestObjects [ASLToAGL _boxPos, [_className], _searchRadius, true] select {[_x, _boxObject] call YFU_bridge_segmentBelongsToBox};
	private _nearestStart = objNull;
	private _nearestDistance = 1e9;
	private _aligned = [];
	private _sorted = [];
	private _queue = [];

	{
		private _distance = _boxPos distance (getPosASL _x);
		if (_distance < _nearestDistance) then {
			_nearestDistance = _distance;
			_nearestStart = _x;
		};
	} forEach _kickoffCandidates;

	if (isNull _nearestStart) exitWith {[]};

	{
		private _candidate = _x;
		private _delta = (getPosASL _candidate) vectorDiff _boxPos;
		private _forward = _delta vectorDotProduct _buildDir;
		private _lateralVec = _delta vectorDiff (_buildDir vectorMultiply _forward);
		private _lateral = vectorMagnitude _lateralVec;
		private _dirAlignment = abs ((vectorNormalized (vectorDirVisual _candidate)) vectorDotProduct _segmentDir);

		if (
			(_forward >= (-_step * 2)) &&
			(_lateral <= (_step * 1.5)) &&
			(_dirAlignment >= 0.7)
		) then {
			_aligned pushBack [_candidate, _forward];
		};
	} forEach _candidates;

	{
		private _entry = _x;
		private _inserted = false;

		for "_i" from 0 to ((count _sorted) - 1) do {
			if ((_entry select 1) < ((_sorted select _i) select 1)) exitWith {
				_sorted insert [_i, [_entry]];
				_inserted = true;
			};
		};

		if (!_inserted) then {
			_sorted pushBack _entry;
		};
	} forEach _aligned;

	private _startIndex = -1;
	{
		if ((_x select 0) isEqualTo _nearestStart) exitWith {
			_startIndex = _forEachIndex;
		};
	} forEach _sorted;

	if (_startIndex < 0) exitWith {[]};

	for "_i" from _startIndex to ((count _sorted) - 1) do {
		_queue pushBack ((_sorted select _i) select 0);
	};

	_queue
};

YFU_bridge_getPlanRange = {
	params ["_boxObject"];

	_boxObject getVariable ["YFU_bridge_plan_max_distance", 500]
};

YFU_bridge_invalidatePlanPreviewCache = {
	params [["_boxObject", objNull]];

	if (isNull _boxObject) exitWith {
		missionNamespace setVariable ["YFU_bridge_plan_preview_cache", createHashMap];
	};

	private _cache = missionNamespace getVariable ["YFU_bridge_plan_preview_cache", createHashMap];
	private _cacheKey = netId _boxObject;
	if (_cacheKey isEqualTo "") then {
		_cacheKey = str _boxObject;
	};

	_cache deleteAt _cacheKey;
	missionNamespace setVariable ["YFU_bridge_plan_preview_cache", _cache];
};

YFU_bridge_getCachedPlannedQueue = {
	params ["_boxObject", ["_maxAge", 0.15]];

	if (isNull _boxObject) exitWith {[]};

	private _cache = missionNamespace getVariable ["YFU_bridge_plan_preview_cache", createHashMap];
	private _cacheKey = netId _boxObject;
	if (_cacheKey isEqualTo "") then {
		_cacheKey = str _boxObject;
	};

	private _entry = _cache getOrDefault [_cacheKey, createHashMapFromArray []];
	if !(typeName _entry isEqualTo "HASHMAP") then {
		_entry = createHashMapFromArray [];
	};

	private _updatedAt = _entry getOrDefault ["updatedAt", -1];
	private _shouldRebuild =
		(_updatedAt < 0) ||
		{(diag_tickTime - _updatedAt) >= (_maxAge max 0)};

	if (_shouldRebuild) then {
		_entry set ["updatedAt", diag_tickTime];
		_entry set ["queue", [_boxObject] call YFU_bridge_getPlannedQueue];
		_cache set [_cacheKey, _entry];
		missionNamespace setVariable ["YFU_bridge_plan_preview_cache", _cache];
	};

	_entry getOrDefault ["queue", []]
};

YFU_bridge_startBuildFromPlan = {
	params ["_boxObject", ["_requester", objNull], ["_requestId", ""], ["_planRequest", []], ["_leaseId", ""]];

	if (!isServer) exitWith {
		if (!isNull (missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull])) then {call YFU_bridge_endPlanPreview;};
		if (_requestId isEqualTo "") then {_requestId = ["build"] call YFU_bridge_newRequestId;};
		_planRequest = [_boxObject] call YFU_bridge_capturePlanRequest;
		_leaseId = uiNamespace getVariable ["YFU_bridge_planner_lease_id", ""];
		missionNamespace setVariable ["YFU_bridge_last_request", [_requestId, "build", netId _boxObject]];
		[_boxObject, player, _requestId, _planRequest, _leaseId] remoteExecCall ["YFU_bridge_startBuildFromPlan", 2];
		true
	};

	private _requestOwner = remoteExecutedOwner;
	if (_requestId isEqualTo "") then {_requestId = ["build"] call YFU_bridge_newRequestId;};
	private _validation = [_boxObject, _requester, _requestOwner] call YFU_bridge_validateServerRequest;
	if !(_validation # 0) exitWith {
		[_boxObject, _requestId, "build", "failed", _validation # 1, [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	private _planValidation = [_planRequest] call YFU_bridge_validatePlanRequest;
	if !(_planValidation # 0) exitWith {
		[_boxObject, _requestId, "build", "failed", _planValidation # 1, [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	_planRequest = +(_planValidation # 2);
	private _lease = _boxObject getVariable ["YFU_bridge_planner_lease", []];
	if (
		(count _lease) isNotEqualTo 5
		|| {(_lease # 0) isNotEqualTo netId _requester}
		|| {(_lease # 1) isNotEqualTo _requestOwner}
		|| {(_lease # 3) isNotEqualTo _leaseId}
		|| {(_lease # 4) <= serverTime}
	) exitWith {
		[_boxObject, _requestId, "build", "failed", "planner_lease_invalid", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	if (_boxObject getVariable ["YFU_bridge_building", false] || {_boxObject getVariable ["YFU_bridge_removing", false]}) exitWith {
		[_boxObject, _requestId, "build", "failed", "operation_in_progress", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};

	private _widthwise = _planRequest # 1;
	private _planRange = 50;
	private _plan = [_boxObject, "Land_Plank_01_4m_F", _widthwise, _planRange, _planRequest] call YFU_bridge_computePlan;
	if (_plan isEqualTo []) exitWith {
		[_boxObject, _requestId, "build", "failed", "invalid_plan", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};

	private _segmentCount = _plan select 11;
	private _hasEndHit = _plan select 12;
	private _manualCount = _planRequest # 5;
	if (_manualCount > 0) then {_segmentCount = _manualCount;};
	if (_segmentCount <= 0) exitWith {
		[_boxObject, _requestId, "build", "failed", "empty_plan", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	private _modeData = [_boxObject, _widthwise, "Land_Plank_01_4m_F", _planRequest] call YFU_bridge_getBuildModeData;
	if ((_segmentCount * (_modeData # 3)) > 50.01) exitWith {
		[_boxObject, _requestId, "build", "failed", "plan_span_out_of_bounds", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};

	private _queue = [_boxObject, _segmentCount, "Land_Plank_01_4m_F", _widthwise, _hasEndHit, _planRequest] call YFU_bridge_buildQueueFromObject;
	if (_queue isEqualTo []) exitWith {
		[_boxObject, _requestId, "build", "failed", "empty_queue", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	_boxObject setVariable ["YFU_bridge_planner_lease", [], true];
	private _buildDelay = call YFU_bridge_getPerPlankBuildDelay;
	_boxObject setVariable ["YFU_bridge_chain_search_radius", (_planRange + 30) max 80, true];
	_boxObject setVariable ["YFU_bridge_box_mode_widthwise", _widthwise, true];
	_boxObject setVariable ["YFU_bridge_last_accepted_plan", +_planRequest, true];
	_boxObject setVariable ["YFU_bridge_building", true, true];
	_boxObject setVariable ["YFU_bridge_operation_id", _requestId, true];
	private _activeOperations = missionNamespace getVariable ["YFU_bridge_active_operations", createHashMap];
	_activeOperations set [_requestId, [netId _boxObject, "build", _requestOwner, serverTime]];
	missionNamespace setVariable ["YFU_bridge_active_operations", _activeOperations];
	[_boxObject, _requestId, "build", "accepted", "accepted", [], _requestOwner] call YFU_bridge_publishResult;

	[_boxObject, _queue, _buildDelay, _requestId, _requestOwner] spawn {
		params ["_boxObject", "_queue", "_buildDelay", "_requestId", "_requestOwner"];
		private _created = [];
		private _interrupted = false;
		{
			if (isNull _boxObject) exitWith {_interrupted = true;};
			_x params ["_positionASL", "_className", "_segmentDir", "_up", "_dedupeRadius"];
			private _segment = [_positionASL, _className, _segmentDir, _up, _dedupeRadius, _boxObject, _requestId] call YFU_bridge_spawnPlacedSegment;
			if (!isNull _segment) then {_created pushBack _segment;};
			if (_forEachIndex < ((count _queue) - 1)) then {uiSleep _buildDelay;};
		} forEach _queue;

		if (_interrupted || {isNull _boxObject}) then {
			{if (!isNull _x) then {deleteVehicle _x;};} forEach _created;
		} else {
			private _complete = (count _created) isEqualTo (count _queue);
			private _ids = _created apply {netId _x};
			if (!_complete) then {{if (!isNull _x) then {deleteVehicle _x;};} forEach _created;};
			_boxObject setVariable ["YFU_bridge_building", false, true];
			_boxObject setVariable ["YFU_bridge_operation_id", "", true];
			[_boxObject, _requestId, "build", ["failed", "complete"] select _complete, ["segment_creation_incomplete", "complete"] select _complete, _ids, _requestOwner] call YFU_bridge_publishResult;
		};
		private _activeOperations = missionNamespace getVariable ["YFU_bridge_active_operations", createHashMap];
		_activeOperations deleteAt _requestId;
		missionNamespace setVariable ["YFU_bridge_active_operations", _activeOperations];
	};
	true
};

YFU_bridge_startRemoveFromBox = {
	params ["_boxObject", ["_requester", objNull], ["_requestId", ""]];

	if (!isServer) exitWith {
		if (!isNull (missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull])) then {call YFU_bridge_endPlanPreview;};
		if (_requestId isEqualTo "") then {_requestId = ["remove"] call YFU_bridge_newRequestId;};
		missionNamespace setVariable ["YFU_bridge_last_request", [_requestId, "remove", netId _boxObject]];
		[_boxObject, player, _requestId] remoteExecCall ["YFU_bridge_startRemoveFromBox", 2];
		true
	};

	private _requestOwner = remoteExecutedOwner;
	if (_requestId isEqualTo "") then {_requestId = ["remove"] call YFU_bridge_newRequestId;};
	private _validation = [_boxObject, _requester, _requestOwner] call YFU_bridge_validateServerRequest;
	if !(_validation # 0) exitWith {
		[_boxObject, _requestId, "remove", "failed", _validation # 1, [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	if (_boxObject getVariable ["YFU_bridge_building", false] || {_boxObject getVariable ["YFU_bridge_removing", false]}) exitWith {
		[_boxObject, _requestId, "remove", "failed", "operation_in_progress", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};

	private _queue = [_boxObject, "Land_Plank_01_4m_F"] call YFU_bridge_getRemovalQueue;
	if (_queue isEqualTo []) exitWith {
		[_boxObject, _requestId, "remove", "failed", "no_owned_segments", [], _requestOwner] call YFU_bridge_publishResult;
		false
	};
	private _removeDelay = (call YFU_bridge_getPerPlankBuildDelay) * 0.5;
	private _ids = _queue apply {netId _x};
	_boxObject setVariable ["YFU_bridge_removing", true, true];
	_boxObject setVariable ["YFU_bridge_operation_id", _requestId, true];
	[_boxObject, _requestId, "remove", "accepted", "accepted", _ids, _requestOwner] call YFU_bridge_publishResult;

	[_boxObject, _queue, _removeDelay, _requestId, _requestOwner, _ids] spawn {
		params ["_boxObject", "_queue", "_removeDelay", "_requestId", "_requestOwner", "_ids"];
		{
			if (isNull _boxObject) exitWith {};
			if (!isNull _x) then {deleteVehicle _x;};
			if ((_forEachIndex < ((count _queue) - 1)) && {_removeDelay > 0}) then {uiSleep _removeDelay;};
		} forEach _queue;

		if (!isNull _boxObject) then {
			private _deleteDeadline = diag_tickTime + 2;
			waitUntil {
				uiSleep 0.01;
				(_queue findIf {!isNull _x}) < 0 || {diag_tickTime >= _deleteDeadline}
			};
			private _complete = (_queue findIf {!isNull _x}) < 0;
			_boxObject setVariable ["YFU_bridge_removing", false, true];
			_boxObject setVariable ["YFU_bridge_operation_id", "", true];
			[_boxObject, _requestId, "remove", ["failed", "complete"] select _complete, ["segment_removal_incomplete", "complete"] select _complete, _ids, _requestOwner] call YFU_bridge_publishResult;
		};
	};
	true
};

YFU_bridge_initPlanRenderer = {
	if (missionNamespace getVariable ["YFU_bridge_plan_renderer_init", false]) exitWith {};

	missionNamespace setVariable ["YFU_bridge_plan_renderer_init", true];
	addMissionEventHandler ["Draw3D", {
		private _boxObject = missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull];
		if (isNull _boxObject) exitWith {};
		if ((player distance _boxObject) > 10) exitWith {};

		private _widthwise = _boxObject getVariable ["YFU_bridge_plan_widthwise", false];
		private _queue = [_boxObject] call YFU_bridge_getCachedPlannedQueue;
		if ((count _queue) <= 0) exitWith {};

		private _bridgeMetrics = ["Land_Plank_01_4m_F"] call YFU_bridge_getClassMetrics;
		private _surfaceOffset = ["Land_Plank_01_4m_F"] call YFU_bridge_getPreviewSurfaceOffset;
		private _boundSpacing = if (_widthwise) then { _bridgeMetrics select 0 } else { _bridgeMetrics select 1 };
		private _start = (_queue select 0) select 0;
		private _end = (_queue select ((count _queue) - 1)) select 0;
		private _labelPos = _end vectorAdd [0, 0, 0.35];
		private _prevEndA = [];
		private _prevEndB = [];
		private _prevColorA = [];
		private _prevColorB = [];

		{
			private _positionASL = _x select 0;
			private _up = _x select 3;
			private _buildDir = _x select 5;
			private _advance = _x select 6;
			private _segmentType = _x select 7;
			private _segmentColors = [_boxObject, _segmentType] call YFU_bridge_getPreviewSegmentColors;
			private _colorA = _segmentColors select 0;
			private _colorB = _segmentColors select 1;
			private _halfAdvance = _advance * 0.5;
			private _boundAxis = vectorNormalized (_up vectorCrossProduct _buildDir);
			private _halfSpacing = _boundSpacing * 0.5;
			private _surfaceShift = _up vectorMultiply _surfaceOffset;
			private _startCenter = (_positionASL vectorAdd (_buildDir vectorMultiply (-_halfAdvance))) vectorAdd _surfaceShift;
			private _endCenter = (_positionASL vectorAdd (_buildDir vectorMultiply _halfAdvance)) vectorAdd _surfaceShift;
			private _startA = _startCenter vectorAdd (_boundAxis vectorMultiply _halfSpacing);
			private _endA = _endCenter vectorAdd (_boundAxis vectorMultiply _halfSpacing);
			private _startB = _startCenter vectorAdd (_boundAxis vectorMultiply (-_halfSpacing));
			private _endB = _endCenter vectorAdd (_boundAxis vectorMultiply (-_halfSpacing));

			if (_prevEndA isNotEqualTo []) then {
				drawLine3D [ASLToAGL _prevEndA, ASLToAGL _startA, _prevColorA];
				drawLine3D [ASLToAGL _prevEndB, ASLToAGL _startB, _prevColorB];
			};

			drawLine3D [ASLToAGL _startA, ASLToAGL _endA, _colorA];
			drawLine3D [ASLToAGL _startB, ASLToAGL _endB, _colorB];
			drawLine3D [ASLToAGL _startA, ASLToAGL _startB, _colorA];
			drawLine3D [ASLToAGL _endA, ASLToAGL _endB, _colorB];

			drawIcon3D [
				"\A3\ui_f\data\map\markers\military\dot_CA.paa",
				_colorA,
				ASLToAGL _startA,
				0.45,
				0.45,
				0,
				"",
				2,
				0.02,
				"PuristaMedium"
			];

			drawIcon3D [
				"\A3\ui_f\data\map\markers\military\dot_CA.paa",
				_colorB,
				ASLToAGL _startB,
				0.45,
				0.45,
				0,
				"",
				2,
				0.02,
				"PuristaMedium"
			];

			drawIcon3D [
				"\A3\ui_f\data\map\markers\military\dot_CA.paa",
				_colorA,
				ASLToAGL _endA,
				0.45,
				0.45,
				0,
				"",
				2,
				0.02,
				"PuristaMedium"
			];

			drawIcon3D [
				"\A3\ui_f\data\map\markers\military\dot_CA.paa",
				_colorB,
				ASLToAGL _endB,
				0.45,
				0.45,
				0,
				"",
				2,
				0.02,
				"PuristaMedium"
			];

			_prevEndA = _endA;
			_prevEndB = _endB;
			_prevColorA = _colorA;
			_prevColorB = _colorB;
		} forEach _queue;

		private _labelColors = [_boxObject] call YFU_bridge_getPreviewColors;

		drawIcon3D [
			"",
			(_labelColors select 0),
			ASLToAGL _labelPos,
			0,
			0,
			0,
			format ["%1 m | %2 planks | %3", round (_start distance _end), count _queue, if (_widthwise) then {"wide"} else {"length"}],
			2,
			0.03,
			"PuristaMedium"
		];
	}];
};

YFU_bridge_getSourceForwardSize = {
	params ["_sourceObject"];

	private _objectBounds = boundingBoxReal _sourceObject;
	private _objMin = _objectBounds select 0;
	private _objMax = _objectBounds select 1;
	private _sizeX = abs ((_objMax select 0) - (_objMin select 0));
	private _sizeY = abs ((_objMax select 1) - (_objMin select 1));

	(_sizeX max _sizeY) max 0.1
};

YFU_bridge_getRampOrientation = {
	params ["_buildDir", "_segmentDir", "_up", "_widthwise", ["_slopeSign", 1], ["_degrees", 30]];

	private _sin = sin (_degrees * _slopeSign);
	private _cos = cos _degrees;

	if (_widthwise) exitWith {
		[
			_segmentDir,
			((_up vectorMultiply _cos) vectorAdd (_buildDir vectorMultiply (-_sin)))
		]
	};

	[
		((_buildDir vectorMultiply _cos) vectorAdd (_up vectorMultiply _sin)),
		((_up vectorMultiply _cos) vectorAdd (_buildDir vectorMultiply (-_sin)))
	]
};

YFU_bridge_buildQueueFromObject = {
	params ["_sourceObject", ["_segmentCount", 1], ["_className", "Land_Plank_01_4m_F"], ["_widthwise", false], ["_finalizeEnd", false], ["_planRequest", []]];

	if (isNull _sourceObject) exitWith {[]};
	if (_planRequest isNotEqualTo []) then {_widthwise = _planRequest # 1;};

	private _modeData = [_sourceObject, _widthwise, _className, _planRequest] call YFU_bridge_getBuildModeData;
	private _buildDir = _modeData select 0;
	private _segmentDir = _modeData select 1;
	private _up = _modeData select 2;
	private _step = _modeData select 3;
	private _metrics = [_className] call YFU_bridge_getClassMetrics;
	private _dedupeRadius = (((_metrics select 0) min (_metrics select 1)) * 0.35) max 0.5;
	private _rampMode = if (_planRequest isEqualTo []) then {_sourceObject getVariable ["YFU_bridge_ramp_mode", false]} else {_planRequest # 3};
	private _rampDegrees = 30;
	private _rampSegmentCount = if (_planRequest isEqualTo []) then {[_sourceObject] call YFU_bridge_getRampPlankCount} else {_planRequest # 4};
	private _rampRise = _step * (sin _rampDegrees);
	private _rampAdvance = _step * (cos _rampDegrees);
	private _verticalOffset = [_sourceObject, _planRequest] call YFU_bridge_getVerticalOffset;
	private _searchRadius = if (_planRequest isEqualTo []) then {_sourceObject getVariable ["YFU_bridge_chain_search_radius", 600]} else {80};
	private _chainEnd = [_sourceObject, _className, _widthwise, _searchRadius, _planRequest] call YFU_bridge_findNearbyChainEnd;
	private _hasExistingChain = !(isNull _chainEnd);
	private _startClipDistance = if (!_hasExistingChain) then {_step} else {0};
	private _endClipCount = if (_finalizeEnd) then {1} else {0};
	private _startRampCount = if (_rampMode && !_hasExistingChain) then {_rampSegmentCount} else {0};
	private _endRampCount = if (_rampMode && _finalizeEnd) then {_rampSegmentCount} else {0};
	private _reservedCount = _endClipCount + _startRampCount + _endRampCount;
	private _flatCount = (_segmentCount - _reservedCount) max 0;
	private _currentEdge = if (_hasExistingChain) then {
		(getPosASL _chainEnd) vectorAdd (_buildDir vectorMultiply (_step * 0.5))
	} else {
		private _originEdge = getPosASL _sourceObject;
		_originEdge = _originEdge vectorAdd (_buildDir vectorMultiply ((([_sourceObject] call YFU_bridge_getSourceForwardSize) * 0.5) - _startClipDistance));
		_originEdge
	};
	private _deckOffset = 0;
	private _queue = [];

	private _queueSegment = {
		params ["_advance", "_segmentDirToUse", "_upToUse", ["_zOffset", 0], ["_segmentType", "flat"]];
		private _placementPos = _currentEdge vectorAdd (_buildDir vectorMultiply (_advance * 0.5));
		_placementPos = _placementPos vectorAdd [0, 0, _zOffset + _verticalOffset];
		_queue pushBack [_placementPos, _className, _segmentDirToUse, _upToUse, _dedupeRadius, _buildDir, _advance, _segmentType];
		_currentEdge = _currentEdge vectorAdd (_buildDir vectorMultiply _advance);
	};

	if (_startRampCount > 0) then {
		for "_i" from 1 to _startRampCount do {
			private _rampUpOrientation = [_buildDir, _segmentDir, _up, _widthwise, 1, _rampDegrees] call YFU_bridge_getRampOrientation;
			[_rampAdvance, _rampUpOrientation select 0, _rampUpOrientation select 1, _deckOffset + (_rampRise * 0.5), "ramp_up"] call _queueSegment;
			_deckOffset = _deckOffset + _rampRise;
		};
	};

	for "_i" from 1 to _flatCount do {
		[_step, _segmentDir, _up, _deckOffset, "flat"] call _queueSegment;
	};

	if (_endRampCount > 0) then {
		for "_i" from 1 to _endRampCount do {
			private _rampDownOrientation = [_buildDir, _segmentDir, _up, _widthwise, -1, _rampDegrees] call YFU_bridge_getRampOrientation;
			[_rampAdvance, _rampDownOrientation select 0, _rampDownOrientation select 1, (_deckOffset - (_rampRise * 0.5)) max 0, "ramp_down"] call _queueSegment;
			_deckOffset = (_deckOffset - _rampRise) max 0;
		};
	};

	if (_endClipCount > 0) then {
		[_step, _segmentDir, _up, _deckOffset, "clip"] call _queueSegment;
	};

	_queue
};

YFU_bridge_getBuildModeData = {
	params ["_sourceObject", ["_widthwise", false], ["_className", "Land_Plank_01_4m_F"], ["_planRequest", []]];
	if (_planRequest isNotEqualTo []) then {_widthwise = _planRequest # 1;};

	private _bridgeMetrics = [_className] call YFU_bridge_getClassMetrics;
	private _bridgeLength = _bridgeMetrics select 0;
	private _bridgeWidth = _bridgeMetrics select 1;
	private _orientation = [_sourceObject, _widthwise, _planRequest] call YFU_bridge_getBuildOrientation;
	private _buildDir = _orientation select 0;
	private _segmentDir = _orientation select 1;
	private _up = _orientation select 2;
	private _step = if (_widthwise) then { _bridgeWidth } else { _bridgeLength };

	[_buildDir, _segmentDir, _up, _step]
};

YFU_bridge_getObjectForwardPlacement = {
	params ["_sourceObject", ["_stepIndex", 0], ["_className", "Land_Plank_01_4m_F"]];

	private _bridgeMetrics = [_className] call YFU_bridge_getClassMetrics;
	private _bridgeLength = _bridgeMetrics select 0;
	private _objectBounds = boundingBoxReal _sourceObject;
	private _objMin = _objectBounds select 0;
	private _objMax = _objectBounds select 1;
	private _objectLength = abs ((_objMax select 0) - (_objMin select 0));
	private _sourcePos = getPosASL _sourceObject;
	private _dir = vectorDirVisual _sourceObject;

	private _offset = (_objectLength * 0.5) + (_bridgeLength * 0.5) + (_bridgeLength * _stepIndex);
	_sourcePos vectorAdd (_dir vectorMultiply _offset)
};

YFU_bridge_getObjectBuildPlacement = {
	params ["_sourceObject", ["_stepIndex", 0], ["_className", "Land_Plank_01_4m_F"], ["_widthwise", false]];

	private _modeData = [_sourceObject, _widthwise, _className] call YFU_bridge_getBuildModeData;
	private _buildDir = _modeData select 0;
	private _step = _modeData select 3;
	private _sourcePos = getPosASL _sourceObject;
	private _sourceForwardSize = [_sourceObject] call YFU_bridge_getSourceForwardSize;
	private _offset = (_sourceForwardSize * 0.5) + (_step * 0.5) + (_step * _stepIndex);

	_sourcePos vectorAdd (_buildDir vectorMultiply _offset)
};

YFU_bridge_hasNearbySegment = {
	params ["_className", "_positionASL", "_radius"];

	private _nearby = nearestObjects [ASLToAGL _positionASL, [_className], _radius, true];
	(count _nearby) > 0
};

YFU_bridge_spawnPlacedSegment = {
	params ["_positionASL", "_className", "_segmentDir", "_up", ["_dedupeRadius", 0.5], ["_builderBox", objNull], ["_operationId", ""]];

	if ([_className, _positionASL, _dedupeRadius max 0.5] call YFU_bridge_hasNearbySegment) exitWith {
		objNull
	};

	private _segment = createVehicle [_className, ASLToAGL _positionASL, [], 0, "CAN_COLLIDE"];
	_segment setPosASL _positionASL;
	_segment setVectorDirAndUp [_segmentDir, _up];
	_segment setDamage 0;
	_segment allowDamage false;
	_segment enableSimulationGlobal false;
	if (!isNull _builderBox) then {
		_segment setVariable ["YFU_bridge_builder_box", netId _builderBox, true];
		_segment setVariable ["YFU_bridge_operation_id", _operationId, true];
	};

	_segment
};

YFU_bridge_spawnSegment = {
	params ["_anchorBridge", "_positionASL", ["_className", ""]];

	if (_className isEqualTo "") then {
		_className = typeOf _anchorBridge;
	};

	private _metrics = [_anchorBridge] call YFU_bridge_getSegmentMetrics;
	private _dedupeRadius = ((_metrics select 0) min (_metrics select 1)) * 0.35;

	[_positionASL, _className, vectorDirVisual _anchorBridge, vectorUpVisual _anchorBridge, _dedupeRadius] call YFU_bridge_spawnPlacedSegment
};

YFU_bridge_extendStraight = {
	params ["_anchorBridge", ["_segmentCount", 1], ["_className", ""]];

	if (isNull _anchorBridge) exitWith {[]};

	if (_className isEqualTo "") then {
		_className = typeOf _anchorBridge;
	};

	private _spawned = [];

	for "_i" from 1 to _segmentCount do {
		private _placementPos = [_anchorBridge, _i] call YFU_bridge_getForwardPlacement;
		private _segment = [_anchorBridge, _placementPos, _className] call YFU_bridge_spawnSegment;

		if (!isNull _segment) then {
			_spawned pushBack _segment;
		};
	};

	_spawned
};

YFU_bridge_findNearbyChainEnd = {
	params ["_sourceObject", ["_className", "Land_Plank_01_4m_F"], ["_widthwise", false], ["_radius", 40], ["_planRequest", []]];

	if (isNull _sourceObject) exitWith {objNull};
	if (_planRequest isNotEqualTo []) then {_widthwise = _planRequest # 1;};

	private _modeData = [_sourceObject, _widthwise, _className, _planRequest] call YFU_bridge_getBuildModeData;
	private _buildDir = _modeData select 0;
	private _segmentDir = _modeData select 1;
	private _step = _modeData select 3;
	private _candidates = nearestObjects [ASLToAGL (getPosASL _sourceObject), [_className], _radius, true];
	if (typeOf _sourceObject isEqualTo "YFU_Bridge_Box") then {
		_candidates = _candidates select {[_x, _sourceObject] call YFU_bridge_segmentBelongsToBox};
	};
	private _best = objNull;
	private _bestForward = -1e9;

	{
		private _candidate = _x;
		private _delta = (getPosASL _candidate) vectorDiff (getPosASL _sourceObject);
		private _forward = _delta vectorDotProduct _buildDir;
		private _lateralVec = _delta vectorDiff (_buildDir vectorMultiply _forward);
		private _lateral = vectorMagnitude _lateralVec;
		private _dirAlignment = abs ((vectorNormalized (vectorDirVisual _candidate)) vectorDotProduct _segmentDir);

		if (
			(_forward >= (-_step * 0.5)) &&
			(_lateral <= (_step * 1.25)) &&
			(_dirAlignment >= 0.7)
		) then {
			if (_forward > _bestForward) then {
				_bestForward = _forward;
				_best = _candidate;
			};
		};
	} forEach _candidates;

	_best
};

YFU_bridge_buildFromObject = {
	params ["_sourceObject", ["_segmentCount", 1], ["_className", "Land_Plank_01_4m_F"], ["_widthwise", false], ["_finalizeEnd", false]];

	if (isNull _sourceObject) exitWith {[]};

	private _modeData = [_sourceObject, _widthwise, _className] call YFU_bridge_getBuildModeData;
	private _buildDir = _modeData select 0;
	private _segmentDir = _modeData select 1;
	private _up = _modeData select 2;
	private _step = _modeData select 3;
	private _metrics = [_className] call YFU_bridge_getClassMetrics;
	private _dedupeRadius = (((_metrics select 0) min (_metrics select 1)) * 0.35) max 0.5;
	private _allowClipping = _sourceObject getVariable ["YFU_bridge_allow_clipping", false];
	private _rampMode = _sourceObject getVariable ["YFU_bridge_ramp_mode", false];
	private _rampDegrees = 30;
	private _rampRise = _step * (sin _rampDegrees);
	private _rampAdvance = _step * (cos _rampDegrees);
	private _spawned = [];
	private _searchRadius = _sourceObject getVariable ["YFU_bridge_chain_search_radius", 600];
	private _chainEnd = [_sourceObject, _className, _widthwise, _searchRadius] call YFU_bridge_findNearbyChainEnd;
	private _hasExistingChain = !(isNull _chainEnd);
	private _startClipCount = if (_allowClipping && !_hasExistingChain) then {1} else {0};
	private _endClipCount = if (_allowClipping && _finalizeEnd) then {1} else {0};
	private _startRampCount = if (_rampMode && !_hasExistingChain) then {1} else {0};
	private _endRampCount = if (_rampMode && _finalizeEnd) then {1} else {0};
	private _reservedCount = _startClipCount + _endClipCount + _startRampCount + _endRampCount;
	private _flatCount = (_segmentCount - _reservedCount) max 0;
	private _currentEdge = if (_hasExistingChain) then {
		(getPosASL _chainEnd) vectorAdd (_buildDir vectorMultiply (_step * 0.5))
	} else {
		private _originEdge = getPosASL _sourceObject;
		_originEdge = _originEdge vectorAdd (_buildDir vectorMultiply (([_sourceObject] call YFU_bridge_getSourceForwardSize) * 0.5));
		_originEdge
	};
	private _deckOffset = 0;

	private _placeSegment = {
		params ["_advance", "_segmentDirToUse", "_upToUse", ["_zOffset", 0]];
		private _placementPos = _currentEdge vectorAdd (_buildDir vectorMultiply (_advance * 0.5));
		_placementPos = _placementPos vectorAdd [0, 0, _zOffset];
		private _segment = [_placementPos, _className, _segmentDirToUse, _upToUse, _dedupeRadius] call YFU_bridge_spawnPlacedSegment;
		if (!isNull _segment) then {
			_spawned pushBack _segment;
		};
		_currentEdge = _currentEdge vectorAdd (_buildDir vectorMultiply _advance);
	};

	if (_startClipCount > 0) then {
		[_step, _segmentDir, _up, _deckOffset] call _placeSegment;
	};

	if (_startRampCount > 0) then {
		private _rampUpOrientation = [_buildDir, _segmentDir, _up, _widthwise, 1, _rampDegrees] call YFU_bridge_getRampOrientation;
		[_rampAdvance, _rampUpOrientation select 0, _rampUpOrientation select 1, _deckOffset + (_rampRise * 0.5)] call _placeSegment;
		_deckOffset = _deckOffset + _rampRise;
	};

	for "_i" from 1 to _flatCount do {
		[_step, _segmentDir, _up, _deckOffset] call _placeSegment;
	};

	if (_endRampCount > 0) then {
		private _rampDownOrientation = [_buildDir, _segmentDir, _up, _widthwise, -1, _rampDegrees] call YFU_bridge_getRampOrientation;
		[_rampAdvance, _rampDownOrientation select 0, _rampDownOrientation select 1, (_deckOffset - (_rampRise * 0.5)) max 0] call _placeSegment;
		_deckOffset = (_deckOffset - _rampRise) max 0;
	};

	if (_endClipCount > 0) then {
		[_step, _segmentDir, _up, _deckOffset] call _placeSegment;
	};

	_sourceObject setVariable ["YFU_bridge_box_mode_widthwise", _widthwise, true];
	_sourceObject setVariable ["YFU_bridge_chain_search_radius", _searchRadius, true];
	_spawned
};

YFU_bridge_canExtend = {
	params ["_target", "_caller"];

	alive _target &&
	{(_caller distance _target) < 8} &&
	{(attachedTo _target) isEqualTo objNull}
};

YFU_bridge_createRootAction = {
	private _buildRoot = [
		"YFU_BridgeRoot",
		"Bridge Builder",
		"\a3\ui_f\data\igui\cfg\simpletasks\types\bridge_ca.paa",
		{ true },
		{
			params ["_target", "_caller"];
			[_target, _caller] call YFU_bridge_canExtend
		}
	] call ace_interact_menu_fnc_createAction;

	_buildRoot
};

YFU_bridge_createExtendAction = {
	params ["_id", "_label", "_segmentCount"];

	[
		_id,
		_label,
		"",
		{
			params ["_target", "_caller", "_args"];
			_args params ["_segmentCount"];
			[_target, _segmentCount] call YFU_bridge_extendStraight;
		},
		{
			params ["_target", "_caller"];
			[_target, _caller] call YFU_bridge_canExtend
		},
		{},
		[_segmentCount]
	] call ace_interact_menu_fnc_createAction
};

YFU_bridge_attachActionsToObject = {
	params ["_bridgeObject"];

	if (isNull _bridgeObject) exitWith {};
};

YFU_bridge_attachActionsToBuilderBox = {
	params ["_boxObject"];

	if (isNull _boxObject) exitWith {};
	call YFU_bridge_initPlanRenderer;
	[_boxObject] call YFU_bridge_ensureBoxDefaults;

	private _openUiAction = [
		"YFU_BoxBridgeOpenUI",
		"Open Bridge Builder",
		"",
		{
			params ["_target"];
			[_target] call YFU_bridge_openBuilderDialog;
		},
		{
			params ["_target", "_caller"];
			alive _target &&
			{(_caller distance _target) < 8} &&
			{!(_target getVariable ["YFU_bridge_building", false])} &&
			{!(_target getVariable ["YFU_bridge_removing", false])}
		},
		{},
		[],
		[0, 0, 0],
		8
	] call ace_interact_menu_fnc_createAction;

	["YFU_box_bridge_open_ui", _boxObject, _openUiAction, 0, []] call YOSHI_addActionToObjectForEveryClient;
};

YFU_initBridgeActions = {
	call YFU_bridge_initPlanRenderer;

	private _openUiAction = [
		"YFU_BoxBridgeOpenUI_Class",
		"Open Bridge Builder",
		"",
		{
			params ["_target"];
			[_target] call YFU_bridge_openBuilderDialog;
		},
		{
			params ["_target", "_caller"];
			alive _target &&
			{(_caller distance _target) < 8} &&
			{!(_target getVariable ["YFU_bridge_building", false])} &&
			{!(_target getVariable ["YFU_bridge_removing", false])}
		},
		{},
		[],
		[0, 0, 0],
		8
	] call ace_interact_menu_fnc_createAction;

	["YFU_Bridge_Box", 0, [], _openUiAction] call ace_interact_menu_fnc_addActionToClass;
};
