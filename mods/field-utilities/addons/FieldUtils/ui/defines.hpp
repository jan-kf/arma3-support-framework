#include "idc.hpp"
#include "constants.hpp"

#ifndef YFU_UI_DEFINES
#define YFU_UI_DEFINES

class RscText;
class RscPicture;
class RscListbox;
class RscButton;
class RscEdit;
class RscControlsGroup;
class RscStructuredText;
class RscProgress;
class RscToolbox;

class YFU_RscText: RscText {
    x = 0;
    y = 0;
    h = YFU_TXT_H;
    w = YFU_TXT_W*2;
    colorText[] = YFU_MAIN_COLOR;
    colorBackground[] = YFU_TRANSPARENT;
    font = YFU_FONT;
    sizeEx = YFU_FONT_SIZE;
    text = "";
    shadow = 0;
};

class YFU_LargeRscText: YFU_RscText {
    sizeEx = YFU_FONT_SIZE * 2;
    w = YFU_TXT_W * 2;
};

class YFU_RscListbox: RscListbox {
    x = 0;
    y = 0;
    w = YFU_SIZE_HALF - YFU_PADDING;
    h = YFU_SIZE_HALF - (YFU_P_TXT_H + YFU_PADDING);
    rowHeight = YFU_TXT_H;
    colorText[] = YFU_MAIN_COLOR;
    colorSelect[] = YFU_MAIN_COLOR;
    colorSelect2[] = YFU_MAIN_COLOR;
    colorSelectBackground[] = YFU_DARK_COLOR;
    colorBackground[] = YFU_V_DARK_COLOR;
    colorScrollbar[] = YFU_DARK_COLOR;
    colorBorder[] = YFU_MAIN_COLOR;
    borderSize = 0.002;
    font = YFU_FONT;
    sizeEx = YFU_FONT_SIZE;
    shadow = 0;
};

class YFU_RscButton: RscButton {
    x = 0;
    y = 0;
    w = YFU_BTN_W;
    h = YFU_BTN_H;
    colorText[] = YFU_MAIN_COLOR;
    colorBackground[] = YFU_V_DARK_COLOR;
    colorBackgroundActive[] = YFU_DARK_COLOR;
    colorFocused[] = YFU_DARK_COLOR;
    colorBorder[] = YFU_MAIN_COLOR;
    borderSize = 0.002;
    font = YFU_FONT;
    sizeEx = YFU_FONT_SIZE;
    text = "";
    shadow = 0;
    style = 2;
};

class YFU_RscEdit: RscEdit {
    x = 0;
    y = 0;
    w = YFU_TXT_W;
    h = YFU_BTN_H;
    colorText[] = YFU_MAIN_COLOR;
    colorSelection[] = YFU_DARK_COLOR;
    colorBackground[] = YFU_V_DARK_COLOR;
    colorBorder[] = YFU_MAIN_COLOR;
    borderSize = 0.002;
    font = YFU_FONT;
    sizeEx = YFU_FONT_SIZE;
    text = "";
    shadow = 0;
};

class YFU_RscStructuredText: RscStructuredText {
    x = 0;
    y = 0;
    w = YFU_TXT_W;
    h = YFU_TXT_H;
    colorText[] = YFU_MAIN_COLOR;
    colorBackground[] = YFU_TRANSPARENT;
    text = "";
    size = YFU_FONT_SIZE;
    class Attributes {
        font = YFU_FONT;
        color = "#99FF99";
        align = "left";
        shadow = 0;
    };
};

class YFU_RscProgress: RscProgress {
    x = 0;
    y = 0;
    w = YFU_TXT_W;
    h = YFU_TXT_H / 2;
    colorFrame[] = YFU_MAIN_COLOR;
    colorBar[] = YFU_MAIN_COLOR;
    colorBackground[] = YFU_V_DARK_COLOR;
    texture = "#(argb,8,8,3)color(1,1,1,1)";
};

class YFU_RscControlsGroup: RscControlsGroup {
    x = 0;
    y = 0;
    w = YFU_SIZE_HALF;
    h = YFU_SIZE_HALF;
    colorBackground[] = YFU_TRANSPARENT;
    class VScrollbar { width = 0; autoScrollEnabled = 0; disabled = 1; scrollSpeed = 0; };
    class HScrollbar { height = 0; disabled = 1; };
    class Controls {};
};

class YFU_RscToolbox: RscToolbox {
    x = 0;
    y = 0;
    w = YFU_SIZE_HALF - YFU_PADDING;
    h = YFU_BTN_H * 1.6;
    rows = 1;
    columns = 2;
    colorText[] = YFU_MAIN_COLOR;
    colorTextSelect[] = YFU_MAIN_COLOR;
    colorSelectedBg[] = YFU_DARK_COLOR;
    color[] = YFU_V_DARK_COLOR;
    colorTextDisable[] = YFU_MED_COLOR;
    font = YFU_FONT;
    sizeEx = YFU_FONT_SIZE;
};

#endif
