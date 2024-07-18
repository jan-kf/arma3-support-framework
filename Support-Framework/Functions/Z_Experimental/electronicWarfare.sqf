missionNamespace setVariable ["#EM_FMin", 140]; 
missionNamespace setVariable ["#EM_FMax", 150];

missionNamespace setVariable ["#EM_SMin", 0]; 
missionNamespace setVariable ["#EM_SMax", 22];

missionNamespace setVariable ["#EM_SelMin", 141.6]; 
missionNamespace setVariable ["#EM_SelMax", 141.9];


beans = [] spawn {
	private _player = player;
	private _range = 1000;
	private _interval = 0.1;
	private _count = 150;

	while {_count > 0} do {
		private _objects = nearestObjects [_player, ["All"], _range];
		hint str([_count, _objects]);
		private _valuesArray = [];

		{
			if (_x != _player) then {
				private _distance = _player distance _x;
				private _strengthModifier = (1 - (_distance / _range));

				private _angleDiff = _player getRelDir _x;

				if (_angleDiff > 180) then {
					_angleDiff = 360 - _angleDiff;
				};

				private _facingMultiplier = 1 - ((_angleDiff / 180) * 0.99);

				private _finalStrength = _strengthModifier * _facingMultiplier;
				private _strengthValue = round (_finalStrength * 20 * 10) / 10;

				private _randomValue = 0;
				if (isNil {_x getVariable "frequency"}) then {
					_randomValue = round ((random 10 + 140) * 10) / 10;
					_x setVariable ["frequency", _randomValue, true];
				} else {
					_randomValue = _x getVariable "frequency";
				};

				

				_valuesArray pushBack _randomValue;
				_valuesArray pushBack _strengthValue;
			};
		} forEach _objects;

		hint str(_valuesArray);
		missionNamespace setVariable ["#EM_Values", _valuesArray];
		sleep _interval;
		_count = _count - 1;
	};

	missionNamespace setVariable ["#EM_Values", []];
};