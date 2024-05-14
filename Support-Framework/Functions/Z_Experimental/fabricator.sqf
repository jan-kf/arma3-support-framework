private _originalObjects = synchronizedObjects _this; 
 
{ 
    private _originalPos = getPos _this; 
    private _newObject = createVehicle [typeOf _x, _originalPos, [], 0, "NONE"]; 
     
    clearWeaponCargoGlobal _newObject; 
    clearMagazineCargoGlobal _newObject; 
    clearItemCargoGlobal _newObject; 
    clearBackpackCargoGlobal _newObject; 
     
     
    private _weapons = getWeaponCargo _x;
    {
        private _weaponType = (_weapons select 0) select _forEachIndex;
        private _weaponCount = (_weapons select 1) select _forEachIndex;
        _newObject addWeaponCargoGlobal [_weaponType, _weaponCount];
    } forEach (_weapons select 0);


    private _magazines = getMagazineCargo _x;
    {
        private _magazineType = (_magazines select 0) select _forEachIndex;
        private _magazineCount = (_magazines select 1) select _forEachIndex;
        _newObject addMagazineCargoGlobal [_magazineType, _magazineCount];
    } forEach (_magazines select 0);


    private _items = getItemCargo _x;
    {
        private _itemType = (_items select 0) select _forEachIndex;
        private _itemCount = (_items select 1) select _forEachIndex;
        _newObject addItemCargoGlobal [_itemType, _itemCount];
    } forEach (_items select 0);

    private _backpacks = getBackpackCargo _x;
    {
        private _backpackType = (_backpacks select 0) select _forEachIndex;
        private _backpackCount = (_backpacks select 1) select _forEachIndex;
        _newObject addBackpackCargoGlobal [_backpackType, _backpackCount];
    } forEach (_backpacks select 0);

 
} forEach _originalObjects; 
