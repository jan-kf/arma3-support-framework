class YFU_Page_Bridge: YFU_RscControlsGroup {
    idc = YFU_IDC_BRIDGE_PAGE;
    x = 0;
    y = 0;
    w = YFU_SIZE_FULL;
    h = YFU_SIZE_FULL;

    class Controls {
        class Title: YFU_LargeRscText {
            idc = YFU_IDC_BRIDGE_TITLE;
            text = "PONTIFEX: BRIDGE BUILDER";
        };

        class Summary: YFU_RscStructuredText {
            idc = YFU_IDC_BRIDGE_SUMMARY;
            y = YFU_P_TXT_H;
            w = YFU_SIZE_FULL - YFU_PADDING;
            h = YFU_P_TXT_H * 3;
            text = "";
        };

        class LayoutLabel: YFU_LargeRscText {
            idc = -1;
            y = YFU_P_TXT_H * 4.2;
            text = "Layout";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class LayoutToolbox: YFU_RscToolbox {
            idc = YFU_IDC_BRIDGE_LAYOUT_TOOLBOX;
            x = 0;
            y = YFU_P_TXT_H * 5.4;
            strings[] = {"Lengthwise", "Wide"};
            onToolBoxSelChanged = "_this call YFU_bridge_dialogToolboxChanged;";
        };

        class PreviewLabel: YFU_LargeRscText {
            idc = -1;
            y = YFU_P_TXT_H * 6.9;
            text = "Preview";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class PreviewToolbox: YFU_RscToolbox {
            idc = YFU_IDC_BRIDGE_PREVIEW_TOOLBOX;
            x = 0;
            y = YFU_P_TXT_H * 8.1;
            strings[] = {"Enabled", "Disabled"};
            onToolBoxSelChanged = "_this call YFU_bridge_dialogToolboxChanged;";
        };
        class PlankCountLabel: YFU_RscText {
            idc = -1;
            y = YFU_P_TXT_H * 9.5;
            text = "Planks:";
        };
        class PlankCount: YFU_RscEdit {
            idc = YFU_IDC_BRIDGE_PLANK_COUNT;
            x = YFU_SIZE_EIGHT;
            y = YFU_P_TXT_H * 9.4;
            w = YFU_SIZE_EIGHT;
            text = "0";
            onKeyUp = "call YFU_bridge_dialogPlankCountChanged;";
            onKillFocus = "call YFU_bridge_dialogPlankCountChanged;";
        };
        class AutoCalculateBtn: YFU_RscButton {
            idc = YFU_IDC_BRIDGE_AUTO_CALCULATE;
            x = (YFU_SIZE_EIGHT * 2) + YFU_PADDING;
            y = YFU_P_TXT_H * 9.4;
            w = YFU_SIZE_QUART;
            text = "Auto Calculate";
            action = "call YFU_bridge_dialogAutoCalculate;";
        };

        class OrientationLabel: YFU_LargeRscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H * 4.2;
            text = "Orientation";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class ModeToolbox: YFU_RscToolbox {
            idc = YFU_IDC_BRIDGE_MODE_TOOLBOX;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H * 5.4;
            strings[] = {"Match Box", "Keep Level"};
            onToolBoxSelChanged = "_this call YFU_bridge_dialogToolboxChanged;";
        };

        class RampLabel: YFU_LargeRscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H * 6.9;
            text = "Ramp";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class RampToolbox: YFU_RscToolbox {
            idc = YFU_IDC_BRIDGE_RAMP_TOOLBOX;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H * 8.1;
            strings[] = {"Enabled", "Disabled"};
            onToolBoxSelChanged = "_this call YFU_bridge_dialogToolboxChanged;";
        };
        class RampCountLabel: YFU_RscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H * 9.5;
            text = "Ramp Planks:";
        };
        class RampCount: YFU_RscEdit {
            idc = YFU_IDC_BRIDGE_RAMP_COUNT;
            x = YFU_SIZE_HALF + YFU_SIZE_QUART - (YFU_PADDING * 2);
            y = YFU_P_TXT_H * 9.4;
            w = YFU_SIZE_EIGHT;
            text = "2";
            onKeyUp = "call YFU_bridge_dialogRampCountChanged;";
            onKillFocus = "call YFU_bridge_dialogRampCountChanged;";
        };
        class PitchOffsetLabel: YFU_RscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H * 10.8;
            text = "Pitch Offset:";
        };
        class PitchOffset: YFU_RscEdit {
            idc = YFU_IDC_BRIDGE_PITCH_OFFSET;
            x = YFU_SIZE_HALF + YFU_SIZE_QUART - (YFU_PADDING * 2);
            y = YFU_P_TXT_H * 10.7;
            w = YFU_SIZE_EIGHT;
            text = "0";
            onKeyUp = "call YFU_bridge_dialogPitchOffsetChanged;";
            onKillFocus = "call YFU_bridge_dialogPitchOffsetChanged;";
        };

        class CancelBtn: YFU_RscButton {
            idc = YFU_IDC_BRIDGE_CANCEL;
            x = YFU_SIZE_QUART;
            y = YFU_SIZE_FULL - (YFU_P_BTN_H * 1.5);
            w = YFU_BTN_W * 1.5;
            text = "Close";
            action = "call YFU_bridge_dialogClose;";
        };
        class BuildBtn: YFU_RscButton {
            idc = YFU_IDC_BRIDGE_BUILD;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_SIZE_FULL - (YFU_P_BTN_H * 1.5);
            w = YFU_BTN_W * 1.5;
            text = "Build Bridge";
            action = "call YFU_bridge_dialogSubmit;";
        };
        class RemoveBtn: YFU_RscButton {
            idc = YFU_IDC_BRIDGE_REMOVE;
            x = YFU_SIZE_HALF + (YFU_BTN_W * 1.6);
            y = YFU_SIZE_FULL - (YFU_P_BTN_H * 1.5);
            w = YFU_BTN_W * 1.5;
            text = "Remove Bridge";
            action = "call YFU_bridge_dialogRemove;";
        };
    };
};
