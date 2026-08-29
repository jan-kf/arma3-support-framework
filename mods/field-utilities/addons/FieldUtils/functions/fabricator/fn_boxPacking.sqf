/*
Let all things be done decently and in order.
(1 Corinthians 14:40)

Lord, grant that what we gather,
we may gather wisely,
and what we send,
we may send in peace.
Amen.
*/

YOSHI_getBoxRotations = {
	params ["_dims", ["_keepUp", true]];

	private _x = _dims select 0;
	private _y = _dims select 1;
	private _z = _dims select 2;

	// Force a single canonical orientation for stable packing.
	[[_x, _y, _z]]
};

YOSHI_packValidateRefs = {
	params ["_refs"];
	if ((typeName _refs) != "ARRAY") exitWith {false};
	if ((count _refs) != 3) exitWith {false};
	{
		if ((typeName _x) != "ARRAY") exitWith {false};
		if ((count _x) != 3) exitWith {false};
	} forEach _refs;
	true
};

YOSHI_packGetRefOverrides = {
	private _overrides = missionNamespace getVariable ["YOSHI_PACKING_REF_OVERRIDES", objNull];
	if ((typeName _overrides) != "HASHMAP") then {
		_overrides = createHashMapFromArray [];
		missionNamespace setVariable ["YOSHI_PACKING_REF_OVERRIDES", _overrides];
	};
	_overrides
};

YOSHI_packSetRefOverride = {
	params ["_className", "_refs"];
	if ((typeName _className) != "STRING" || {_className isEqualTo ""}) exitWith {false};
	if !([_refs] call YOSHI_packValidateRefs) exitWith {false};
	private _overrides = call YOSHI_packGetRefOverrides;
	_overrides set [_className, _refs];
	missionNamespace setVariable ["YOSHI_PACKING_REF_OVERRIDES", _overrides];
	true
};

YOSHI_packSetRefOverrides = {
	params ["_entries"];
	if ((typeName _entries) != "ARRAY") exitWith {0};

	private _applied = 0;
	{
		if ((typeName _x) isEqualTo "ARRAY" && {(count _x) >= 2}) then {
			private _className = _x # 0;
			private _refs = _x # 1;
			if ([_className, _refs] call YOSHI_packSetRefOverride) then {
				_applied = _applied + 1;
			};
		};
	} forEach _entries;

	_applied
};

YOSHI_packGetRefOverrideForObject = {
	params ["_obj"];
	if (isNull _obj) exitWith {[]};

	private _overrides = call YOSHI_packGetRefOverrides;
	private _className = typeOf _obj;
	private _refs = _overrides getOrDefault [_className, []];
	if ([_refs] call YOSHI_packValidateRefs) exitWith {_refs};

	private _cfg = configFile >> "CfgVehicles" >> _className;
	while {isClass _cfg} do {
		private _name = configName _cfg;
		if (_name isEqualTo "") exitWith {};
		_refs = _overrides getOrDefault [_name, []];
		if ([_refs] call YOSHI_packValidateRefs) exitWith {_refs};
		_cfg = inheritsFrom _cfg;
	};

	_refs
};

YOSHI_getPackRefCorners = {
	params ["_obj"];
	private _override = [_obj] call YOSHI_packGetRefOverrideForObject;
	if ([_override] call YOSHI_packValidateRefs) exitWith {_override};
	[_obj] call YOSHI_getAccurateLocalRefCorners
};

YOSHI_getOrientationVariantsFromBounds = {
	params ["_bounds", ["_keepUp", true]];

	private _min = _bounds select 0;
	private _max = _bounds select 1;

	private _corners = [
		[_min select 0, _min select 1, _min select 2],
		[_max select 0, _min select 1, _min select 2],
		[_min select 0, _max select 1, _min select 2],
		[_max select 0, _max select 1, _min select 2],
		[_min select 0, _min select 1, _max select 2],
		[_max select 0, _min select 1, _max select 2],
		[_min select 0, _max select 1, _max select 2],
		[_max select 0, _max select 1, _max select 2]
	];

	private _variants = [];

	private _buildVariant = {
		params ["_dir", "_up"];
		private _right = _dir vectorCrossProduct _up;
		if ((vectorMagnitude _right) < 0.5) exitWith {[]};

		private _minRX = 1e12;
		private _minRY = 1e12;
		private _minRZ = 1e12;
		private _maxRX = -1e12;
		private _maxRY = -1e12;
		private _maxRZ = -1e12;

		{
			private _cx = _x select 0;
			private _cy = _x select 1;
			private _cz = _x select 2;

			private _rx = ((_right select 0) * _cx) + ((_dir select 0) * _cy) + ((_up select 0) * _cz);
			private _ry = ((_right select 1) * _cx) + ((_dir select 1) * _cy) + ((_up select 1) * _cz);
			private _rz = ((_right select 2) * _cx) + ((_dir select 2) * _cy) + ((_up select 2) * _cz);

			_minRX = _rx min _minRX;
			_minRY = _ry min _minRY;
			_minRZ = _rz min _minRZ;
			_maxRX = _rx max _maxRX;
			_maxRY = _ry max _maxRY;
			_maxRZ = _rz max _maxRZ;
		} forEach _corners;

		[[_maxRX - _minRX, _maxRY - _minRY, _maxRZ - _minRZ], _dir, _up, [_minRX, _minRY, _minRZ]]
	};

	// Force a single canonical orientation variant that matches YOSHI_getBoxRotations.
	private _v0 = [[0,1,0], [0,0,1]] call _buildVariant;
	if ((count _v0) > 0) then {_variants pushBack _v0;};

	_variants
};

YOSHI_sortPackItemsByVolumeDesc = {
	params ["_items", ["_keepUp", true]];
	private _remaining = +_items;
	private _sorted = [];

	while {(count _remaining) > 0} do {
		private _bestIdx = 0;
		private _bestScore = -1;

		for "_i" from 0 to ((count _remaining) - 1) do {
			private _dims = (_remaining select _i) select 1;
			private _score = 0;
			if (_keepUp) then {
				private _foot = (_dims select 0) * (_dims select 1);
				private _vol = _foot * (_dims select 2);
				_score = (_foot * 1000) + _vol;
			} else {
				_score = (_dims select 0) * (_dims select 1) * (_dims select 2);
			};

			if (_score > _bestScore) then {
				_bestScore = _score;
				_bestIdx = _i;
			};
		};

		_sorted pushBack (_remaining select _bestIdx);
		_remaining deleteAt _bestIdx;
	};

	_sorted
};

YOSHI_packItemSizesSequentialInContainer = {
	params ["_itemSizes", "_containerSize", ["_keepUp", true], ["_singleLayer", false]];

	private _eps = 0.0001;
	private _sizeX = _containerSize select 0;
	private _sizeY = _containerSize select 1;
	private _sizeZ = _containerSize select 2;

	private _sortedItems = [_itemSizes, _keepUp] call YOSHI_sortPackItemsByVolumeDesc;
	private _placements = [];
	private _unfitted = [];

	private _layerZ = 0;
	private _layerH = 0;
	private _rowY = 0;
	private _rowD = 0;
	private _cursorX = 0;

	private _tryFit = {
		params ["_dims", "_atX", "_atY", "_atZ"];
		private _w = _dims select 0;
		private _d = _dims select 1;
		private _h = _dims select 2;
		((_atX + _w) <= (_sizeX + _eps)) &&
		((_atY + _d) <= (_sizeY + _eps)) &&
		((_atZ + _h) <= (_sizeZ + _eps))
	};

	{
		private _id = _x select 0;
		private _dimsBase = _x select 1;
		private _rotations = [_dimsBase, _keepUp] call YOSHI_getBoxRotations;
		private _placed = false;

		{
			private _dims = _x;
			private _rotIdx = _forEachIndex;

			if ([_dims, _cursorX, _rowY, _layerZ] call _tryFit) exitWith {
				_placements pushBack [_id, [_cursorX, _rowY, _layerZ], _dims, _rotIdx];
				_cursorX = _cursorX + (_dims select 0);
				_rowD = _rowD max (_dims select 1);
				_layerH = _layerH max (_dims select 2);
				_placed = true;
			};
		} forEach _rotations;

		if (!_placed) then {
			{
				private _dims = _x;
				private _rotIdx = _forEachIndex;
				private _nextRowY = _rowY + _rowD;
				if ([_dims, 0, _nextRowY, _layerZ] call _tryFit) exitWith {
					_rowY = _nextRowY;
					_cursorX = _dims select 0;
					_rowD = _dims select 1;
					_layerH = _layerH max (_dims select 2);
					_placements pushBack [_id, [0, _rowY, _layerZ], _dims, _rotIdx];
					_placed = true;
				};
			} forEach _rotations;
		};

		if (!_placed && {!_singleLayer}) then {
			{
				private _dims = _x;
				private _rotIdx = _forEachIndex;
				private _nextLayerZ = _layerZ + _layerH;
				if ([_dims, 0, 0, _nextLayerZ] call _tryFit) exitWith {
					_layerZ = _nextLayerZ;
					_cursorX = _dims select 0;
					_rowY = 0;
					_rowD = _dims select 1;
					_layerH = _dims select 2;
					_placements pushBack [_id, [0, 0, _layerZ], _dims, _rotIdx];
					_placed = true;
				};
			} forEach _rotations;
		};

		if (!_placed) then {
			_unfitted pushBack [_id, _dimsBase];
		};
	} forEach _sortedItems;

	[(count _unfitted) isEqualTo 0, _placements, _unfitted]
};

YOSHI_packItemSizesFlatInContainer = {
	params ["_itemSizes", "_containerSize", ["_keepUp", true]];
	[_itemSizes, _containerSize, _keepUp, true] call YOSHI_packItemSizesSequentialInContainer
};

YOSHI_packItemSizesInContainer = {
	params ["_itemSizes", "_containerSize", ["_keepUp", true]];
	[_itemSizes, _containerSize, _keepUp, false] call YOSHI_packItemSizesSequentialInContainer
};

YOSHI_packObjectsInContainer = {
	params ["_objects", "_containerRefs", ["_keepUp", true], ["_padding", [0, 0, 0]], ["_sizeScale", 1.0], ["_cache", createHashMap]];

	private _containerBounds = [_containerRefs] call YOSHI_refCornersToBounds;
	private _containerMin = _containerBounds select 0;
	private _containerSize = [_containerBounds] call YOSHI_boundsToSize;

	private _items = [];
	private _padX = _padding select 0;
	private _padY = _padding select 1;
	private _padZ = _padding select 2;
	{
		private _obj = _x;
		private _cacheKey = netId _obj;
		if (_cacheKey isEqualTo "") then {_cacheKey = str _obj;};
		private _cached = _cache get _cacheKey;
		private _bounds = [];
		private _sizeRaw = [];
		private _variants = [];

		if (isNil {_cached}) then {
			private _refs = [_obj] call YOSHI_getPackRefCorners;
			_bounds = [_refs] call YOSHI_refCornersToBounds;
			_sizeRaw = [_bounds] call YOSHI_boundsToSize;
			_variants = [_bounds, _keepUp] call YOSHI_getOrientationVariantsFromBounds;
			_cache set [_cacheKey, [_bounds, _sizeRaw, _variants]];
		} else {
			_bounds = _cached select 0;
			_sizeRaw = _cached select 1;
			_variants = _cached select 2;
		};

		private _size = [
			(_sizeRaw select 0) + (2 * _padX),
			(_sizeRaw select 1) + (2 * _padY),
			(_sizeRaw select 2) + (2 * _padZ)
		];
		private _sizeScaled = [
			(_size select 0) * _sizeScale,
			(_size select 1) * _sizeScale,
			(_size select 2) * _sizeScale
		];
		_items pushBack [_forEachIndex, _sizeScaled, _obj, _bounds, _variants, _sizeRaw];
	} forEach _objects;

	private _itemSizes = [];
	{
		_itemSizes pushBack [_x select 0, _x select 1];
	} forEach _items;

	private _packResult = [_itemSizes, _containerSize, _keepUp] call YOSHI_packItemSizesInContainer;
	private _success = _packResult select 0;
	private _placementsRaw = _packResult select 1;
	private _unfittedRaw = _packResult select 2;

	private _placements = [];
	private _snapStep = 0.0025;
	private _snap = {
		params ["_value", ["_step", 0.0025]];
		(round (_value / _step)) * _step
	};
	{
		private _id = _x select 0;
		private _pos = _x select 1;
		private _dims = _x select 2;
		private _rotIdx = _x param [3, -1];

		private _item = _items select _id;
		private _obj = _item select 2;
		private _variants = _item select 4;
		private _sizeRaw = _item select 5;

		private _chosenVariant = [];
		if (_rotIdx >= 0 && {_rotIdx < (count _variants)}) then {
			_chosenVariant = _variants select _rotIdx;
		} else {
			{
				private _vd = _x select 0;
				private _vdPadded = [
					((_vd select 0) + (2 * _padX)) * _sizeScale,
					((_vd select 1) + (2 * _padY)) * _sizeScale,
					((_vd select 2) + (2 * _padZ)) * _sizeScale
				];
				if (
					(abs ((_vdPadded select 0) - (_dims select 0)) < 0.001) &&
					(abs ((_vdPadded select 1) - (_dims select 1)) < 0.001) &&
					(abs ((_vdPadded select 2) - (_dims select 2)) < 0.001)
				) exitWith {
					_chosenVariant = _x;
				};
			} forEach _variants;
			if ((count _chosenVariant) isEqualTo 0) then {
				_chosenVariant = _variants select 0;
			};
		};

		private _dirLocal = _chosenVariant select 1;
		private _upLocal = _chosenVariant select 2;
		private _rotMin = _chosenVariant select 3;
		private _rotMinPadded = _rotMin vectorDiff [_padX, _padY, _padZ];

		private _localMin = _containerMin vectorAdd _pos;
		private _localMinRaw = _localMin vectorAdd [_padX, _padY, _padZ];
		private _localMaxRaw = _localMinRaw vectorAdd _sizeRaw;
		private _attachOffset = _localMin vectorDiff _rotMinPadded;
		_attachOffset = [
			[(_attachOffset select 0), _snapStep] call _snap,
			[(_attachOffset select 1), _snapStep] call _snap,
			[(_attachOffset select 2), _snapStep] call _snap
		];

		_placements pushBack [_obj, _attachOffset, _dims, _dirLocal, _upLocal, _localMinRaw, _localMaxRaw];
	} forEach _placementsRaw;

	private _unfitted = [];
	{
		private _id = _x select 0;
		_unfitted pushBack ((_items select _id) select 2);
	} forEach _unfittedRaw;

	[_success, _placements, _unfitted]
};

YOSHI_localVectorToWorld = {
	params ["_parent", "_localVector"];

	private _origin = _parent modelToWorldVisual [0,0,0];
	private _tip = _parent modelToWorldVisual _localVector;
	private _worldVec = _tip vectorDiff _origin;
	private _mag = vectorMagnitude _worldVec;

	if (_mag < 0.0001) exitWith {[0,1,0]};
	_worldVec vectorMultiply (1 / _mag)
};

YOSHI_dirLocalToYawOffset = {
	params ["_dirLocal"];
	private _dx = _dirLocal select 0;
	private _dy = _dirLocal select 1;
	private _yaw = _dx atan2 _dy; // 0 when pointing +Y
	if (_yaw < 0) then {_yaw = _yaw + 360;};
	_yaw
};

YOSHI_applyPackedPlacement = {
	params ["_container", "_placement", ["_detachFirst", true]];

	private _obj = _placement select 0;
	private _attachOffset = _placement select 1;
	private _dirLocal = _placement select 3;
	private _upLocal = _placement select 4;

	if (_detachFirst) then { detach _obj; };

	// Always start from a canonical orientation so repeated pack calls are deterministic.
	_obj setDir 0;
	_obj setVectorUp [0,0,1];

	_obj attachTo [_container, _attachOffset];

	// Upright placements are more stable with explicit yaw + up vector.
	if ((_upLocal select 2) > 0.99) then {
		private _yawOffset = [_dirLocal] call YOSHI_dirLocalToYawOffset;
		_obj setDir ((getDir _container) + _yawOffset);
		_obj setVectorUp [0,0,1];
	} else {
		private _dirWorld = [_container, _dirLocal] call YOSHI_localVectorToWorld;
		private _upWorld = [_container, _upLocal] call YOSHI_localVectorToWorld;
		_obj setVectorDirAndUp [_dirWorld, _upWorld];
	};

	_obj
};

YOSHI_packAttachObjectsInContainer = {
	params ["_container", "_objects", "_containerRefs", ["_detachFirst", true], ["_keepUp", true], ["_padding", [0, 0, 0]], ["_sizeScale", 1.0], ["_cache", createHashMap]];

	private _result = [_objects, _containerRefs, _keepUp, _padding, _sizeScale, _cache] call YOSHI_packObjectsInContainer;
	{
		[_container, _x, _detachFirst] call YOSHI_applyPackedPlacement;
	} forEach (_result select 1);

	_result
};

YOSHI_canPackObjectsInContainer = {
	params ["_objects", "_containerRefs", ["_keepUp", true], ["_padding", [0,0,0]], ["_sizeScale", 1.0], ["_cache", createHashMap]];
	(([_objects, _containerRefs, _keepUp, _padding, _sizeScale, _cache] call YOSHI_packObjectsInContainer) select 0)
};

YOSHI_packObjectsOnPalletsSimple = {
	params ["_objects", ["_keepUp", true], ["_padding", [0,0,0]], ["_sizeScale", 1.0], ["_cache", createHashMap]];

	private _palletClass = "Land_Pallet_F";
	private _palletRefs = [[0.80, -0.72, 0.08], [-0.72, 0.75, 0.08], [-0.72, -0.72, 2.00]];
	private _palletBounds = [_palletRefs] call YOSHI_refCornersToBounds;
	private _palletSize = [_palletBounds] call YOSHI_boundsToSize;

	private _padX = _padding select 0;
	private _padY = _padding select 1;
	private _padZ = _padding select 2;

	private _canFitSizes = {
		params ["_sizes", "_containerSize", "_keepUp"];
		private _items = [];
		{
			_items pushBack [_forEachIndex, _x];
		} forEach _sizes;
		(([_items, _containerSize, _keepUp] call YOSHI_packItemSizesInContainer) select 0)
	};

	private _canFitSize = {
		params ["_size", "_containerSize", "_keepUp"];
		private _sx = _size select 0;
		private _sy = _size select 1;
		private _sz = _size select 2;
		private _cx = _containerSize select 0;
		private _cy = _containerSize select 1;
		private _cz = _containerSize select 2;

		if (_keepUp) then {
			(
				(_sx <= _cx && _sy <= _cy && _sz <= _cz) ||
				(_sy <= _cx && _sx <= _cy && _sz <= _cz)
			)
		} else {
			(
				(_sx <= _cx && _sy <= _cy && _sz <= _cz) ||
				(_sx <= _cx && _sz <= _cy && _sy <= _cz) ||
				(_sy <= _cx && _sx <= _cy && _sz <= _cz) ||
				(_sy <= _cx && _sz <= _cy && _sx <= _cz) ||
				(_sz <= _cx && _sx <= _cy && _sy <= _cz) ||
				(_sz <= _cx && _sy <= _cy && _sx <= _cz)
			)
		};
	};

	private _groupCache = createHashMap;
	private _groupBuckets = createHashMap;
	private _skipped = [];
	{
		private _obj = _x;
		// Group strictly by exact class so type-priority ordering is preserved.
		private _groupKey = typeOf _obj;

		private _cacheKey = netId _obj;
		if (_cacheKey isEqualTo "") then {_cacheKey = str _obj;};
		private _cached = _cache get _cacheKey;
		private _bounds = [];
		private _sizeRaw = [];
		private _variants = [];

		if (isNil {_cached}) then {
			private _refs = [_obj] call YOSHI_getPackRefCorners;
			_bounds = [_refs] call YOSHI_refCornersToBounds;
			_sizeRaw = [_bounds] call YOSHI_boundsToSize;
			_variants = [_bounds, _keepUp] call YOSHI_getOrientationVariantsFromBounds;
			_cache set [_cacheKey, [_bounds, _sizeRaw, _variants]];
		} else {
			_bounds = _cached select 0;
			_sizeRaw = _cached select 1;
			_variants = _cached select 2;
		};

		private _size = [
			((_sizeRaw select 0) + (2 * _padX)) * _sizeScale,
			((_sizeRaw select 1) + (2 * _padY)) * _sizeScale,
			((_sizeRaw select 2) + (2 * _padZ)) * _sizeScale
		];

		if (isNil {_groupCache get _groupKey}) then {
			_groupCache set [_groupKey, _size];
		};

		if ([_size, _palletSize, _keepUp] call _canFitSize) then {
			private _group = _groupBuckets get _groupKey;
			if (isNil {_group}) then {_group = [];};
			_group pushBack [_obj, _size];
			_groupBuckets set [_groupKey, _group];
		} else {
			_skipped pushBack _obj;
		};
	} forEach _objects;

	private _groupKeys = keys _groupBuckets;
	private _groupOrder = [];
	{
		private _dims = _groupCache get _x;
		private _vol = (_dims select 0) * (_dims select 1) * (_dims select 2);
		_groupOrder pushBack [-_vol, _x];
	} forEach _groupKeys;
	_groupOrder sort true;

	private _mergedKeys = [];
	private _mergedSizes = [];
	private _mergedBuckets = createHashMap;
	{
		private _groupKey = _x select 1;
		private _size = _groupCache get _groupKey;
		private _vol = (_size select 0) * (_size select 1) * (_size select 2);
		private _matchKey = "";

		for "_i" from 0 to ((count _mergedKeys) - 1) do {
			private _mSize = _mergedSizes select _i;
			private _mVol = (_mSize select 0) * (_mSize select 1) * (_mSize select 2);
			if (_mVol > 0) then {
				private _ratio = (abs (_vol - _mVol)) / _mVol;
				if (_ratio <= 0.01) exitWith {_matchKey = _mergedKeys select _i;};
			};
		};

		if (_matchKey isEqualTo "") then {
			_mergedKeys pushBack _groupKey;
			_mergedSizes pushBack _size;
			_mergedBuckets set [_groupKey, +(_groupBuckets get _groupKey)];
		} else {
			private _bucket = _mergedBuckets get _matchKey;
			_bucket append (_groupBuckets get _groupKey);
			_mergedBuckets set [_matchKey, _bucket];
		};
	} forEach _groupOrder;

	_groupBuckets = _mergedBuckets;
	_groupOrder = [];
	{
		private _size = _mergedSizes select _forEachIndex;
		private _vol = (_size select 0) * (_size select 1) * (_size select 2);
		_groupOrder pushBack [-_vol, _x];
	} forEach _mergedKeys;
	_groupOrder sort true;

	{
		private _groupKey = _x select 1;
		private _objs = _groupBuckets get _groupKey;
		private _binsType = [];

		{
			private _obj = _x select 0;
			private _objSize = _x select 1;
			private _placed = false;

			for "_i" from 0 to ((count _binsType) - 1) do {
				private _bin = _binsType select _i;
				private _binObjs = _bin select 2;
				private _binSizes = _bin select 3;
				private _trySizes = +_binSizes;
				_trySizes pushBack _objSize;
				if ([_trySizes, _palletSize, _keepUp] call _canFitSizes) exitWith {
					_binObjs pushBack _obj;
					_binSizes pushBack _objSize;
					_bin set [2, _binObjs];
					_bin set [3, _binSizes];
					_binsType set [_i, _bin];
					_placed = true;
				};
			};

			if (!_placed) then {
				_binsType pushBack [_palletClass, _palletRefs, [_obj], [_objSize]];
			};
		} forEach _objs;

		_groupBuckets set [_groupKey, _binsType];
	} forEach _groupOrder;

	private _overflowSizes = [];
	private _overflowObjs = [];
	private _overflowGroups = [];
	{
		private _groupKey = _x select 1;
		private _binsType = _groupBuckets get _groupKey;
		if ((count _binsType) > 0) then {
			private _lastBin = _binsType select ((count _binsType) - 1);
			_overflowObjs append (_lastBin select 2);
			_overflowSizes append (_lastBin select 3);
			_overflowGroups pushBack _groupKey;
		};
	} forEach _groupOrder;

	private _combinedOverflow = [];
	if ((count _overflowGroups) > 1) then {
		if ([_overflowSizes, _palletSize, _keepUp] call _canFitSizes) then {
			{
				private _groupKey = _x;
				private _binsType = _groupBuckets get _groupKey;
				_binsType deleteAt ((count _binsType) - 1);
				_groupBuckets set [_groupKey, _binsType];
			} forEach _overflowGroups;
			_combinedOverflow = [[_palletClass, _palletRefs, _overflowObjs]];
		};
	};

	private _bins = [];
	{
		private _groupKey = _x select 1;
		private _binsType = _groupBuckets get _groupKey;
		{
			_bins pushBack [_x select 0, _x select 1, _x select 2];
		} forEach _binsType;
	} forEach _groupOrder;

	{
		_bins pushBack _x;
	} forEach _combinedOverflow;

	[_bins, _skipped]
};

YOSHI_spawnContainersNearObjectsAndPackMulti = {
	// Use small physical clearance to avoid collider jitter while keeping near-true dimensions.
	params ["_objects", ["_containerDefs", []], ["_detachFirst", true], ["_keepUp", true], ["_spawnDistance", 2.0], ["_padding", [0,0,0]], ["_containerDir", 0], ["_preferMultiple", true], ["_maxSmallCountCap", 4], ["_allowExtra", false], ["_onContainerCreated", {}], ["_onContainerCreatedArgs", []]];

	private _validObjects = _objects select {!isNull _x};
	if ((count _validObjects) isEqualTo 0) exitWith {
		[false, [], []]
	};

	// Keep true dimensions for tighter packing; jitter is handled by snapped attach offsets.
	private _sizeScale = 1.0;
	private _geomCache = createHashMap;
	private _packed = [_validObjects, _keepUp, _padding, _sizeScale, _geomCache] call YOSHI_packObjectsOnPalletsSimple;
	private _allocs = _packed select 0;
	private _skipped = _packed select 1;

	// The caller explicitly chooses whether small packed orders should be spread
	// across multiple delivery containers. Geometry still decides whether each
	// object fits at all; splitting an accepted bin into subsets cannot make an
	// unpackable object acceptable.
	if (_preferMultiple && {_maxSmallCountCap > 0}) then {
		private _cap = (floor _maxSmallCountCap) max 1;
		private _boundedAllocs = [];
		{
			_x params ["_class", "_refs", "_objectsInBin"];
			for "_offset" from 0 to ((count _objectsInBin) - 1) step _cap do {
				_boundedAllocs pushBack [_class, _refs, _objectsInBin select [_offset, _cap]];
			};
		} forEach _allocs;
		_allocs = _boundedAllocs;
	};
	if ((count _skipped) > 0) then {
		[format ["[pack] skipped too-large=%1", count _skipped]] call YFU_fnc_debugMsg;
	};

	private _avg = [0,0,0];
	{
		_avg = _avg vectorAdd (getPosATL _x);
	} forEach _validObjects;
	_avg = _avg vectorMultiply (1 / (count _validObjects));

	private _offsets = [
		[_spawnDistance, 0, 0],
		[-_spawnDistance, 0, 0],
		[0, _spawnDistance, 0],
		[0, -_spawnDistance, 0],
		[_spawnDistance, _spawnDistance, 0],
		[-_spawnDistance, _spawnDistance, 0],
		[_spawnDistance, -_spawnDistance, 0],
		[-_spawnDistance, -_spawnDistance, 0]
	];

	private _containers = [];
	private _allocOut = [];
	private _offsetIdx = 0;

	{
		private _class = _x select 0;
		private _refs = _x select 1;
		private _objs = _x select 2;

		private _spawnPos = (_avg vectorAdd (_offsets select (_offsetIdx mod (count _offsets)))) vectorAdd [5,5,0];
		_offsetIdx = _offsetIdx + 1;
		[format ["[pack] spawn idx=%1 objs=%2 pos=%3", _offsetIdx, count _objs, _spawnPos]] call YFU_fnc_debugMsg;

		private _container = createVehicle [_class, _spawnPos, [], 0, "NONE"];
		// Report the object immediately, before packing/attachment can fail.
		[_container, _onContainerCreatedArgs] call _onContainerCreated;
		_container setPosATL _spawnPos;
		_container setDir _containerDir;
		_container setVectorUp [0,0,1];

		private _packResult = [_container, _objs, _refs, _detachFirst, _keepUp, _padding, _sizeScale, _geomCache] call YOSHI_packAttachObjectsInContainer;
		_containers pushBack _container;
		_allocOut pushBack [_container, _class, _refs, _packResult];
	} forEach _allocs;

	// An item too large for any container is dropped, not packed. Report that
	// rather than only logging it: the caller owns the clones and cannot
	// clean up or refuse an under-filled order it was never told about.
	[(count _skipped) isEqualTo 0, _containers, _allocOut, _skipped]
};
