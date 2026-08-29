#include "idc.hpp"
#include "constants.hpp"

#ifndef YSF_UI_DEFINES
#define YSF_UI_DEFINES

// --- Control type constants (if you need them elsewhere) ---
#define CT_STATIC          0
#define CT_BUTTON          1
#define CT_LISTBOX         5
#define CT_CONTROLS_GROUP  15

class RscText;
class RscEdit;
class RscButton;
class RscListbox;
class RscControlsGroup;
class RscPicture;
class RscStructuredText;
class RscProgress;
class RscCheckbox;
class RscCombo;
class RscTree;
class RscToolbox;

// --- Our prefixed classes inherit from vanilla ones ---
class YSF_RscText : RscText {
  x=0; y=0;
  h=TXT_H; w=TXT_W;
  colorText[] = YSF_MAIN_COLOR;
  font = C_FONT; sizeEx = C_FONT_SIZE;
  text = "";
  shadow=0;
};

class YSF_StructuredText : RscStructuredText {
  x=0; y=0;
  h=TXT_H; w=TXT_W;
  colorText[] = YSF_MAIN_COLOR;
  font = C_FONT; sizeEx = C_FONT_SIZE;
  text = "";
  shadow=0;
  class Attributes
	{
		font = C_FONT;
	};
};

class YSF_LargeRscText : YSF_RscText {
  sizeEx = C_FONT_SIZE * 2;
  w=TXT_W*2;
};

class YSF_RscButton : RscButton {
  x=0; y=0;
  style = 2;  // centered
  h = BTN_H;
  w = BTN_W;
  shadow=0;
  colorText[] = YSF_MAIN_COLOR;
  colorBackgroundActive[] = YSF_MED_COLOR;
  colorBackground[] = YSF_V_DARK_COLOR;
  colorFocused[] = YSF_DARK_COLOR;
  colorFocused2[] = YSF_DARK_COLOR;
  colorDisabled[] = YSF_DARK_COLOR;
  font = C_FONT; sizeEx = C_FONT_SIZE;
  text = ""; action = "";
  soundClick[] = {"VIGIL\sounds\tablet\tablet_ui_tab_transition_01.ogg", 1, 1};
  soundEnter[] = {"VIGIL\sounds\tablet\tablet_ui_hover.ogg", 1, 1};
};

class YSF_Toolbox: RscToolbox {
  colorText[] = YSF_MAIN_COLOR;
	color[] = C_NONE;
	colorTextSelect[] = YSF_MAIN_COLOR;
	colorSelect[] = YSF_DARK_COLOR;
	colorSelectedBg[] = YSF_DARK_COLOR;
  font = C_FONT; sizeEx = C_FONT_SIZE;
};

class YSF_RscEdit : RscEdit {
  x=0; y=0;
  h = BTN_H; w = TXT_W-(PADDING*2);
  maxChars = 9;
	colorText[] = YSF_MAIN_COLOR;
  colorBackground[] = YSF_V_DARK_COLOR;
	colorSelection[] = YSF_DARK_COLOR;
  borderSize = 1;
  colorBorder[] = YSF_MAIN_COLOR;
  font = C_FONT; sizeEx = C_FONT_SIZE;
  text = "";
  shadow=0;
  onKeyDown="playSound selectRandom ['UiChar01', 'UiChar02', 'UiChar03', 'UiChar04', 'UiChar05', 'UiChar06'];";
};

class YSF_RscListbox: RscListbox {
  x=0; y=0;
  style = 16; rowHeight = 0.04; shadow = 0;
  colorText[] = YSF_MAIN_COLOR;
  colorSelect[] = YSF_MAIN_COLOR;
  colorSelect2[] = YSF_MAIN_COLOR;
  colorSelectBackground[] = YSF_MAIN_COLOR;
  colorBackground[] = YSF_V_DARK_COLOR;
  borderSize = 1;
  colorBorder[] = YSF_MAIN_COLOR;
  font = C_FONT; sizeEx = C_FONT_SIZE;
  onLBSelChanged = "if (uiNamespace getVariable ['YSF_tablet_silent', false]) exitWith {}; params ['_ctrl','_i']; if (_i < 0) exitWith {}; private _k = _ctrl lbData _i; ['set',_k] call YSF_UI_Nav;";
};


class YSF_RscControlsGroup : RscControlsGroup {
  x=0; y=0;
  h = SIZE_FULL; w = SIZE_FULL;
  colorBackground[] = YSF_V_DARK_COLOR;
  class VScrollbar { width = 0; autoScrollEnabled = 0; };
  class HScrollbar { height = 0; };
  class Controls {};
};

class YSF_Tree: RscTree {
  x=0; y=0;
  w=SIZE_FULL; h=SIZE_FULL- (P_TXT_H + P_BTN_H);
  colorText[] = YSF_MAIN_COLOR;
  colorArrow[] = YSF_MAIN_COLOR;
  colorBorder[] = YSF_MAIN_COLOR;
  colorLines[] = YSF_DARK_COLOR;
  colorSelect[] = YSF_DARK_COLOR;
  colorSelectBackground[] = YSF_DARK_COLOR;
  colorSelectText[] = YSF_MAIN_COLOR;
  disableKeyboardSearch = 1;
  multiselectEnabled = 0;
  font = C_FONT; sizeEx = C_FONT_SIZE;
  soundSelect[] = {"VIGIL\sounds\tablet\tablet_ui_select.ogg", 1, 1};
};


class YSF_RscCombo: RscCombo {
  h = BTN_H; w = TXT_W-(PADDING*2);
  font = C_FONT; sizeEx = C_FONT_SIZE;
  colorActive[] = YSF_DARK_COLOR;
  colorSelect[] = YSF_V_DARK_COLOR;
	colorText[] = YSF_MAIN_COLOR;
	colorBackground[] = YSF_V_DARK_COLOR;
	colorScrollbar[] = YSF_DARK_COLOR;
	colorDisabled[] = YSF_DARK_COLOR;
	colorPicture[] = YSF_MAIN_COLOR;
	colorPictureSelected[] = YSF_MAIN_COLOR;
	colorPictureDisabled[] = YSF_DARK_COLOR;
	colorPictureRight[] = YSF_MAIN_COLOR;
	colorPictureRightSelected[] = YSF_MAIN_COLOR;
	colorPictureRightDisabled[] = YSF_DARK_COLOR;
	colorTextRight[] = YSF_MAIN_COLOR;
	colorSelectRight[] = YSF_V_DARK_COLOR;
	colorSelect2Right[] = YSF_V_DARK_COLOR;
  colorSelectBackground[] = YSF_MED_COLOR;
  borderSize = 2;
  colorBorder[] = YSF_MAIN_COLOR;
  soundSelect[] = {"VIGIL\sounds\tablet\tablet_ui_tab_transition_01.ogg", 1, 1};
  soundExpand[] = {"VIGIL\sounds\tablet\tablet_ui_open_01.ogg", 1, 1};
  soundCollapse[] = {"VIGIL\sounds\tablet\tablet_ui_close_01.ogg", 1, 1};
  style=160;
  arrowEmpty = "VIGIL\ui\assets\arrow_2.paa";
  arrowFull = "VIGIL\ui\assets\arrow_1.paa";
};

class YSF_Progress: RscProgress {
  x=0; y=0;
  w = TXT_W-PADDING; h = TXT_H/2;
  colorFrame[] = YSF_DARK_COLOR;
  colorText[] = YSF_MAIN_COLOR;
};

class YSF_GridRef: YSF_RscEdit { idc=IDC_MAP_COORD; x=P_TXT_W; y=P_TXT_H; onKeyUp="_this call YOSHI_assetCoordChanged;"; onKillFocus="_this call YOSHI_assetCoordChanged;"; };
class YSF_GridLbl: YSF_RscText { idc=-1; x=0; y=P_TXT_H; text="Task Grid Reference:"; };
class YSF_BtnSubmit: YSF_RscButton { idc=IDC_TASK_SUBMIT; text="Submit"; x=SIZE_HALF-BTN_W; y=SIZE_HALF-BTN_H; };
class YSF_BtnReplace: YSF_RscButton { idc=IDC_TASK_REPLACE; text="Replace"; x=SIZE_HALF-(BTN_W*2+PADDING); y=SIZE_HALF-BTN_H; };
class YSF_Checkbox: RscCheckbox {};

class YSF_UplinkStatusLbl: YSF_RscText { idc=-1; x=0; y=SIZE_FULL-TXT_H; text="Uplink Status:"; };
class YSF_UplinkStatusRef: YSF_RscText { idc=IDC_TABLET_UPLINK; x=P_TXT_W; y=SIZE_FULL-TXT_H; };

class RscMapControl;  // forward declare

class HiddenMapMarker {
  icon = "#(argb,8,8,3)color(0,0,0,0)";
  color[] = {0,0,0,0};
	size = 0;
	importance = 0;
	coefMin = 0;
	coefMax = 0;
};

class ObjectPriority1 {
  color[] = YSF_MAIN_COLOR;
  colorText[] = YSF_MAIN_COLOR;
  colorBackground[] = YSF_MAIN_COLOR;
  colorBorder[] = YSF_MAIN_COLOR;
};

class NameCityCapital;
class NameCity;
class NameVillage;
class NameLocal;


class NamePriority1: NameCityCapital {
  colorText[] = YSF_MAIN_COLOR;
  color[] = YSF_MAIN_COLOR;
  font = C_FONT;
};
class NamePriority2: NameCity {
  colorText[] = YSF_MAIN_COLOR;
  color[] = YSF_MAIN_COLOR;
  font = C_FONT;
};
class NamePriority3: NameVillage {
  colorText[] = YSF_MED_COLOR;
  color[] = YSF_MAIN_COLOR;
  font = C_FONT;
};
class NamePriority4: NameLocal {
  colorText[] = YSF_DARK_COLOR;
  color[] = YSF_MAIN_COLOR;
  font = C_FONT;
};


class YSF_RscMap: RscMapControl {
  maxSatelliteAlpha=0;
  drawObjects=0;
  drawShaded=0;

  font = C_FONT;
  fontGrid = C_FONT;
  fontInfo = C_FONT;
  fontLabel = C_FONT;
  fontLevel = C_FONT;
  fontNames = C_FONT;
  fontUnits = C_FONT;
  runwayFont = C_FONT;
  sizeEx = C_FONT_SIZE;

  colorBackground[] = YSF_V_DARK_COLOR;
  colorText[] = YSF_MAIN_COLOR;
  colorSea[] = YSF_DARK_COLOR;
	colorCountlines[] = C_NONE;
	colorMainCountlines[] = YSF_MAIN_COLOR;
	colorCountlinesWater[] = C_NONE;
	colorMainCountlinesWater[] = YSF_V_DARK_COLOR;
	colorRocks[] = C_NONE;
	colorForest[] = YSF_DARK_COLOR;
	colorForestBorder[] = YSF_DARK_COLOR;
	colorRocksBorder[] = YSF_DARK_COLOR;
	colorPowerLines[] = YSF_DARK_COLOR;
	colorRailWay[] = YSF_MED_COLOR;
	colorNames[] = YSF_MAIN_COLOR;
	colorInactive[] = YSF_MAIN_COLOR;
	colorLevels[] = YSF_DARK_COLOR;
	colorTracks[] = C_BLACK;
	colorRoads[] = C_BLACK;
	colorMainRoads[] = C_BLACK;
	colorTracksFill[] = YSF_DARK_COLOR;
	colorRoadsFill[] = YSF_MED_COLOR;
	colorMainRoadsFill[] = YSF_MAIN_COLOR;
	colorGrid[] = YSF_MAIN_COLOR;
	colorGridMap[] = YSF_MAIN_COLOR;
  colorOutside[] = C_NONE;
  colorBuildings[]     = YSF_MAIN_COLOR;
  colorBuildingsFill[] = YSF_DARK_COLOR;

  class NameMarine: NamePriority2{};
  class NameCityCapital: NamePriority1{};
  class NameCity: NamePriority2{};
  class NameVillage: NamePriority3{};
  class NameLocal: NamePriority4{};
  class Hill: NamePriority4{};

  class Name: HiddenMapMarker{};

  class Building: ObjectPriority1{};
  class House: ObjectPriority1{};
  class Fence: ObjectPriority1{};

  class VegetationBroadleaf: HiddenMapMarker{};
  class VegetationFir: HiddenMapMarker{};
  class VegetationPalm: HiddenMapMarker{};
  class VegetationVineyard: HiddenMapMarker{};
  class RockArea: HiddenMapMarker{};

	class Waypoint : HiddenMapMarker{};
	class WaypointCompleted : HiddenMapMarker{};
	class CustomMark : HiddenMapMarker{};
	class Command : HiddenMapMarker{};
	class Bush : HiddenMapMarker{};
	class Rock : HiddenMapMarker{};
	class SmallTree : HiddenMapMarker{};
	class Tree : HiddenMapMarker{};
	class BusStop : HiddenMapMarker{};
	class Fuelstation : HiddenMapMarker{};
	class Hospital : HiddenMapMarker{};
	class Church : HiddenMapMarker{};
	class Lighthouse : HiddenMapMarker{};
	class power : HiddenMapMarker{};
	class powersolar : HiddenMapMarker{};
	class powerwave : HiddenMapMarker{};
	class powerwind : HiddenMapMarker{};
	class Quay : HiddenMapMarker{};
	class Shipwreck : HiddenMapMarker{};
	class Transmitter : HiddenMapMarker{};
	class Watertower : HiddenMapMarker{};
	class Bunker : HiddenMapMarker{};
	class Cross : HiddenMapMarker{};
	class Fortress : HiddenMapMarker{};
	class Fountain : HiddenMapMarker{};
	class Chapel : HiddenMapMarker{};
	class Ruin : HiddenMapMarker{};
	class Stack : HiddenMapMarker{};
	class Tourism : HiddenMapMarker{};
	class ViewTower : HiddenMapMarker{};
};

class YSF_IntroText : YSF_StructuredText {
  idc = IDC_TABLET_INTRO;
  x = 0; y = 0; w = SIZE_FULL; h = SIZE_FULL;
  colorBackground[] = YSF_V_DARK_COLOR;
  colorText[] = YSF_MAIN_COLOR;
  onLoad = "call YOSHI_playIntro;";
};

#endif
