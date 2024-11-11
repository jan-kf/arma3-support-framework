fnc_printParents =
{
	disableSerialization;
	if (!isClass _this) exitWith { hint "Argument is not a config Class" };

	private _parents = [];

	while { !isNull _this } do
	{
		_parents pushBack configName _this;
		_this = inheritsFrom _this;
	};

	reverse _parents;

	private _tv = findDisplay 46 createDisplay "RscDisplayEmpty" ctrlCreate ["RscTree", -1];
	_tv ctrlSetPosition [0,0,1,1];
	_tv ctrlSetBackgroundColor [0,0,0,0.5];
	_tv ctrlCommit 0;

	private _path = [];
	{
		_tv tvAdd [_path, _x];
		_path pushBack 0;
	}
	forEach _parents;

	tvExpandAll _tv;
};

(configFile >> "CfgVehicles" >> typeOf _this) call fnc_printParents;