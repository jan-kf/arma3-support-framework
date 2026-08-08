#ifndef YFU_UI_CONSTANTS
#define YFU_UI_CONSTANTS

#define YFU_TITLE "PONTIFEX: O.R.D.O"

#define YFU_FONT "EtelkaMonospacePro"
#define YFU_FONT_SIZE 0.025

#define UNIT_SCALE  0.1

#define YFU_SIZE_FULL (UNIT_SCALE * 10)
#define YFU_SIZE_HALF (UNIT_SCALE * 5)
#define YFU_SIZE_QUART (UNIT_SCALE * 2.5)
#define YFU_SIZE_EIGHT (UNIT_SCALE * 1.25)

#define YFU_PADDING 0.01
#define YFU_BTN_H (UNIT_SCALE * 0.5)
#define YFU_BTN_W YFU_SIZE_EIGHT
#define YFU_TXT_H YFU_BTN_H
#define YFU_TXT_W YFU_SIZE_QUART

#define YFU_P_TXT_H (YFU_TXT_H + YFU_PADDING)
#define YFU_P_TXT_W (YFU_TXT_W + YFU_PADDING)
#define YFU_P_BTN_H (YFU_BTN_H + YFU_PADDING)

#define YFU_COLOR_BASE_R "(missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 0)"
#define YFU_COLOR_BASE_G "(missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 1)"
#define YFU_COLOR_BASE_B "(missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 2)"
#define YFU_COLOR_BASE_A "(missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 3)"

#define YFU_COLOR_MED_R  "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 0) * 0.66)"
#define YFU_COLOR_MED_G  "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 1) * 0.66)"
#define YFU_COLOR_MED_B  "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 2) * 0.66)"

#define YFU_COLOR_DARK_R "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 0) * 0.33)"
#define YFU_COLOR_DARK_G "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 1) * 0.33)"
#define YFU_COLOR_DARK_B "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 2) * 0.33)"

#define YFU_COLOR_V_DARK_R "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 0) * 0.1)"
#define YFU_COLOR_V_DARK_G "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 1) * 0.1)"
#define YFU_COLOR_V_DARK_B "((missionNamespace getVariable ['YFU_monochromeBaseColor',[0.15,0.95,0.15,1]] select 2) * 0.1)"

#define YFU_MAIN_COLOR {YFU_COLOR_BASE_R, YFU_COLOR_BASE_G, YFU_COLOR_BASE_B, YFU_COLOR_BASE_A}
#define YFU_MED_COLOR {YFU_COLOR_MED_R, YFU_COLOR_MED_G, YFU_COLOR_MED_B, YFU_COLOR_BASE_A}
#define YFU_DARK_COLOR {YFU_COLOR_DARK_R, YFU_COLOR_DARK_G, YFU_COLOR_DARK_B, YFU_COLOR_BASE_A}
#define YFU_V_DARK_COLOR {YFU_COLOR_V_DARK_R, YFU_COLOR_V_DARK_G, YFU_COLOR_V_DARK_B, YFU_COLOR_BASE_A}
#define YFU_BLACK {0, 0, 0, 1}
#define YFU_WHITE {1, 1, 1, 1}
#define YFU_TRANSPARENT {0, 0, 0, 0}

#endif
