class YFU_PayloadManager_Dialog {
    idd = YFU_IDD_PAYLOAD_DIALOG;
    movingEnable = 0;
    enableSimulation = 1;
    onLoad = "uiNamespace setVariable ['YFU_PayloadManager_Display', _this select 0]; call YFU_fnc_payloadDialogLoad;";
    onUnload = "uiNamespace setVariable ['YFU_PayloadManager_Display', displayNull]; uiNamespace setVariable ['YFU_PayloadManager_UAV', objNull]; uiNamespace setVariable ['YFU_PayloadManager_Proposal', []];";
    class controlsBackground {
        class Backdrop: YFU_RscText {
            x = "safeZoneX + safeZoneW * 0.08";
            y = "safeZoneY + safeZoneH * 0.10";
            w = "safeZoneW * 0.84";
            h = "safeZoneH * 0.80";
            colorBackground[] = YFU_BLACK;
        };
        class Header: YFU_RscText {
            x = "safeZoneX + safeZoneW * 0.08";
            y = "safeZoneY + safeZoneH * 0.10";
            w = "safeZoneW * 0.84";
            h = "safeZoneH * 0.07";
            text = "PONTIFEX // PAYLOAD MANAGER";
            sizeEx = YFU_FONT_SIZE * 1.35;
            colorBackground[] = YFU_DARK_COLOR;
        };
        class UniformLabel: YFU_RscText {
            x = "safeZoneX + safeZoneW * 0.10";
            y = "safeZoneY + safeZoneH * 0.19";
            w = "safeZoneW * 0.18";
            text = "UNIFORM";
        };
        class VestLabel: UniformLabel { x = "safeZoneX + safeZoneW * 0.30"; text = "VEST"; };
        class BackpackLabel: UniformLabel { x = "safeZoneX + safeZoneW * 0.50"; text = "BACKPACK"; };
        class CapacityLabel: UniformLabel { x = "safeZoneX + safeZoneW * 0.70"; w = "safeZoneW * 0.20"; text = "UAV CAPACITY // 8 UNITS"; };
    };
    class controls {
        class Uniform: YFU_RscListbox {
            idc = YFU_IDC_PAYLOAD_UNIFORM;
            x = "safeZoneX + safeZoneW * 0.10";
            y = "safeZoneY + safeZoneH * 0.24";
            w = "safeZoneW * 0.18";
            h = "safeZoneH * 0.42";
            canDrag = 1;
            onLBDblClick = "['uniform', _this select 1] call YFU_fnc_payloadAddFromSource;";
        };
        class Vest: Uniform {
            idc = YFU_IDC_PAYLOAD_VEST;
            x = "safeZoneX + safeZoneW * 0.30";
            onLBDblClick = "['vest', _this select 1] call YFU_fnc_payloadAddFromSource;";
        };
        class Backpack: Uniform {
            idc = YFU_IDC_PAYLOAD_BACKPACK;
            x = "safeZoneX + safeZoneW * 0.50";
            onLBDblClick = "['backpack', _this select 1] call YFU_fnc_payloadAddFromSource;";
        };
        class Capacity: YFU_RscListbox {
            idc = YFU_IDC_PAYLOAD_CAPACITY;
            x = "safeZoneX + safeZoneW * 0.70";
            y = "safeZoneY + safeZoneH * 0.24";
            w = "safeZoneW * 0.20";
            h = "safeZoneH * 0.42";
            canDrag = 1;
            onLBDrop = "_this call YFU_fnc_payloadHandleDrop;";
        };
        class Summary: YFU_RscStructuredText {
            idc = YFU_IDC_PAYLOAD_SUMMARY;
            x = "safeZoneX + safeZoneW * 0.10";
            y = "safeZoneY + safeZoneH * 0.68";
            w = "safeZoneW * 0.80";
            h = "safeZoneH * 0.05";
        };
        class Status: YFU_RscStructuredText {
            idc = YFU_IDC_PAYLOAD_STATUS;
            x = "safeZoneX + safeZoneW * 0.10";
            y = "safeZoneY + safeZoneH * 0.74";
            w = "safeZoneW * 0.48";
            h = "safeZoneH * 0.06";
            text = "Drag eligible inventory items into UAV capacity. Installed payloads cannot be reclaimed.";
        };
        class Remove: YFU_RscButton {
            idc = YFU_IDC_PAYLOAD_REMOVE;
            x = "safeZoneX + safeZoneW * 0.60";
            y = "safeZoneY + safeZoneH * 0.74";
            w = "safeZoneW * 0.09";
            text = "REMOVE";
            action = "call YFU_fnc_payloadRemoveSelected;";
        };
        class Up: Remove {
            idc = YFU_IDC_PAYLOAD_UP;
            x = "safeZoneX + safeZoneW * 0.70";
            text = "UP";
            action = "[-1] call YFU_fnc_payloadMoveSelected;";
        };
        class Down: Remove {
            idc = YFU_IDC_PAYLOAD_DOWN;
            x = "safeZoneX + safeZoneW * 0.80";
            text = "DOWN";
            action = "[1] call YFU_fnc_payloadMoveSelected;";
        };
        class Cancel: YFU_RscButton {
            idc = YFU_IDC_PAYLOAD_CANCEL;
            x = "safeZoneX + safeZoneW * 0.60";
            y = "safeZoneY + safeZoneH * 0.82";
            w = "safeZoneW * 0.14";
            text = "CANCEL";
            action = "closeDialog 2;";
        };
        class Apply: Cancel {
            idc = YFU_IDC_PAYLOAD_APPLY;
            x = "safeZoneX + safeZoneW * 0.76";
            text = "APPLY LOADOUT";
            action = "call YFU_fnc_payloadApply;";
        };
    };
};

class RscTitles {
    class YFU_Payload_HUD {
        idd = YFU_IDD_PAYLOAD_HUD;
        duration = 1e10;
        fadeIn = 0;
        fadeOut = 0;
        movingEnable = 0;
        onLoad = "uiNamespace setVariable ['YFU_Payload_HUD_Display', _this select 0];";
        onUnload = "uiNamespace setVariable ['YFU_Payload_HUD_Display', displayNull];";
        class controls {
            class PayloadText: YFU_RscStructuredText {
                idc = YFU_IDC_PAYLOAD_HUD_TEXT;
                x = "safeZoneX + safeZoneW * 0.735";
                y = "safeZoneY + safeZoneH * 0.76";
                w = "safeZoneW * 0.245";
                h = "safeZoneH * 0.11";
                colorBackground[] = YFU_V_DARK_COLOR;
            };
        };
    };
};
