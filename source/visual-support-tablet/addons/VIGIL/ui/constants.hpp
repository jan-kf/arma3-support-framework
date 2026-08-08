#define YSF_TITLE "VIGIL Combat Tablet v0.8.0"
#define YSF_FULL_TITLE "Virtual Interfaced Governor for Integrated Logistics"

#define UNIT_SCALE  0.1

#define SIZE_FULL   (UNIT_SCALE * 10)
#define SIZE_HALF   (UNIT_SCALE * 5)
#define SIZE_THIRD  (UNIT_SCALE * 3.33)
#define SIZE_QUART  (UNIT_SCALE * 2.5)
#define SIZE_EIGHT  (UNIT_SCALE * 1.25)

#define BTN_W  SIZE_EIGHT
#define BTN_H  (UNIT_SCALE * 0.5)

#define TXT_H  BTN_H
#define TXT_W  SIZE_QUART

#define PADDING  0.01

#define P_BTN_W  (BTN_W + PADDING)
#define P_BTN_H  (BTN_H + PADDING)

#define P_TXT_H (TXT_H + PADDING)
#define P_TXT_W (TXT_W + PADDING)

#define C_FONT "EtelkaMonospacePro"
#define C_FONT_SIZE 0.025
#define C_WHITE {1, 1, 1, 1}
#define C_LIGHT_GRAY {0.67, 0.67, 0.67, 1}
#define C_DARK_GRAY {0.33, 0.33, 0.33, 1}
#define C_BLACK {0, 0, 0, 1}
#define C_BLUE {0, 0, 1, 1}
#define C_GREEN {0, 1, 0, 1}
#define C_RED {1, 0, 0, 1}
#define C_NONE {0, 0, 0, 0}
#define C_LIGHT_GREEN {0.33, 1, 0.33, 1}
#define C_MED_GREEN {0.33, 1, 0.33, 0.66}
#define C_DARK_GREEN {0.33, 1, 0.33, 0.33}

#define C_BACKGROUND {0, 0.1, 0, 1}
#define C_LAND {0, 0.1, 0, 1}
#define C_WATER {0, 0, 0.1, 1}


#define YSF_COLOR_BASE_R "(missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 0)"
#define YSF_COLOR_BASE_G "(missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 1)"
#define YSF_COLOR_BASE_B "(missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 2)"
#define YSF_COLOR_BASE_A "(missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 3)"

#define YSF_COLOR_MED_R  "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 0) * 0.66)"
#define YSF_COLOR_MED_G  "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 1) * 0.66)"
#define YSF_COLOR_MED_B  "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 2) * 0.66)"

#define YSF_COLOR_DARK_R "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 0) * 0.33)"
#define YSF_COLOR_DARK_G "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 1) * 0.33)"
#define YSF_COLOR_DARK_B "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 2) * 0.33)"

#define YSF_COLOR_V_DARK_R "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 0) * 0.1)"
#define YSF_COLOR_V_DARK_G "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 1) * 0.1)"
#define YSF_COLOR_V_DARK_B "((missionNamespace getVariable ['YSF_monochromeBaseColor',[0,1,0,1]] select 2) * 0.1)"

#define YSF_MAIN_COLOR    {YSF_COLOR_BASE_R,YSF_COLOR_BASE_G,YSF_COLOR_BASE_B,YSF_COLOR_BASE_A}
#define YSF_MED_COLOR     {YSF_COLOR_MED_R,YSF_COLOR_MED_G,YSF_COLOR_MED_B,YSF_COLOR_BASE_A}
#define YSF_DARK_COLOR    {YSF_COLOR_DARK_R,YSF_COLOR_DARK_G,YSF_COLOR_DARK_B,YSF_COLOR_BASE_A}
#define YSF_V_DARK_COLOR   {YSF_COLOR_V_DARK_R,YSF_COLOR_V_DARK_G,YSF_COLOR_V_DARK_B,YSF_COLOR_BASE_A}

