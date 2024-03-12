params ['_requiredItems', '_unit'];

// checks inventory of _unit and returns true if they have one of the items in _requiredItems. 

private _hasItem = false;
{
	// Check general inventory
	if (_x in (items _unit)) exitWith {
		_hasItem = true;
	};

	// Check assigned items (like night vision, binoculars, GPS, and radio)
	if (_x in (assignedItems _unit)) exitWith {
		_hasItem = true;
	};

	// Check uniform, vest, and backpack items
	if (_x in (uniformItems _unit) || _x in (vestItems _unit) || _x in (backpackItems _unit)) exitWith {
		_hasItem = true;
	};
} forEach _requiredItems;

_hasItem