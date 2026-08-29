/*
Direct, we beseech Thee, O Lord,
all our actions by Thy holy inspiration,
and carry them on by Thy gracious assistance,
that every prayer and work of ours
may begin from Thee
and by Thee be happily ended.
Through Christ our Lord. Amen.
*/

call YFU_initObjectHandling;

// Event handler for object creation
addMissionEventHandler ["EntityCreated", {
    params ["_entity"];

    // handle adding objects that can be Attached instead of Ace Loading
    if (_entity isKindOf "ReammoBox_F") then {
       [_entity] call YOSHI_setObjectLoadHandling;
    };

    if (_entity isKindOf "UAV_01_base_F") then {
       [_entity] call YFU_fnc_configureUAVLocal;
    };

    if (unitIsUAV _entity) then {
        [_entity] call YFU_fnc_configureUAVLocal;
    };

    if (_entity isKindOf "Land_Pallet_F") then {
       [_entity, true, [0, 1.6, 0]] call ace_dragging_fnc_setDraggable;
       [_entity, true, [0, 1.6, 1]] call ace_dragging_fnc_setCarryable;
    };

}];
