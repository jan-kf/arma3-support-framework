// function to figure out if a vehicle is able to be called in for CAS

params ["_vehicle"]; 
// these are works that appear in some cases but should be disregarded as weapons
_nonCombatKeywords = ["safe", "designator", "horn"]; 

_allWeapons = weapons _vehicle; 
_combatWeapons = _allWeapons select { 
	_isCombatWeapon = true;
	_weaponNameLower = toLower _x; 
	{  
		if (toLower _x in _weaponNameLower) then {
			_isCombatWeapon = false;
		}; 
	} forEach _nonCombatKeywords; 
	_isCombatWeapon; 
}; 

(count _combatWeapons > 0)

// _ isKindOf "Air" // determine if air or ground


private _pilot = driver _this; 

_pilot disableAI "TARGET";
_pilot disableAI "AUTOTARGET";

_this setCombatMode "RED"; 

_this flyInHeight 250;