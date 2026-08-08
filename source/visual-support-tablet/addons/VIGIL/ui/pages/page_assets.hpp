class Tablet_Page_Assets: YSF_RscControlsGroup {
  idc = IDC_PAGE_ASSETS;
  onLoad = "uiNamespace setVariable ['YSF_PageAssets_Group', _this select 0];";

  class Controls {
    // Title
    class Title: YSF_LargeRscText { idc = -1; text = YSF_TITLE; };

    class TabAssets: YSF_Toolbox {
      idc = IDC_ASSETS_TAB_BOX;
      x = 0;
      y = P_TXT_H;
      w = SIZE_HALF;
      h = BTN_H;
      rows = 1;
      columns = 4;
      strings[] = {"Transport","Artillery","CAS","Fixed Wing"};
      values[]  = {0,1,2,3};
      onLoad = "_ctrl = _this#0; _ctrl lbSetCurSel 0; uiNamespace setVariable ['YSF_assets_tabIndex',0]; ['transport'] call YOSHI_selectAssetType;";
      onToolBoxSelChanged = "_this call YOSHI_assetsTabChanged;";
    };

    class AssetTree: YSF_Tree {
      idc = IDC_ASSETS_TREE; y = P_TXT_H + P_BTN_H; w = SIZE_HALF; h = SIZE_HALF - (P_TXT_H + P_BTN_H);
      onTreeSelChanged = "_this call YOSHI_assetSelected;";
    };

    // 2nd quadrant

    class Map: YSF_RscMap {
      idc = IDC_MAP_CTRL;
      x = SIZE_HALF+PADDING; y=0; w = SIZE_HALF; h = SIZE_HALF;
      onMouseButtonDblClick = "[_this] call YOSHI_assets_mapClick;";   
    };

    // 3rd quadrant

    class AssetLabel: YSF_LargeRscText {
      idc = -1; 
      y = SIZE_HALF;
      text = "Asset Details:";
    };

    class NameLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H;
      text = "Name:";
    };
    class NameData: YSF_RscText {
      idc = IDC_ASSETS_DETAIL_NAME; 
      y = SIZE_HALF + TXT_H; x = P_TXT_W/4;
      text = "-";
    };

    class GridLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*2;
      text = "Grid:";
    };
    class GridData: YSF_RscText {
      idc = IDC_ASSETS_DETAIL_GRID; 
      y = SIZE_HALF + TXT_H*2; x = (TXT_W/4);
      text = "-";
    };

    class SpeedLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*2; x = P_TXT_W + P_TXT_W/4;
      text = "Speed:";
    };
    class SpeedData: YSF_RscText {
      idc = IDC_ASSETS_DETAIL_SPEED; 
      y = SIZE_HALF + TXT_H*2; x = P_TXT_W + P_TXT_W/2;
      text = "-";
    };

    class HeadingLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*2; x = (2*P_TXT_W)/3;
      text = "Heading:";
    };
    class HeadingData: YSF_RscText {
      idc = IDC_ASSETS_DETAIL_HEADING; 
      y = SIZE_HALF + TXT_H*2; x = (2*P_TXT_W)/3 + (TXT_W/3);
      text = "-";
    };

    

    class FuelLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*3;
      text = "Fuel:";
    };
    class FuelData: YSF_Progress {
      idc = IDC_ASSETS_DETAIL_FUEL; 
      y = SIZE_HALF + (TXT_H*3) + (TXT_H/4); x = P_TXT_W;
    };

    class HealthLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*4;
      text = "Health:";
    };
    class HealthData: YSF_Progress {
      idc = IDC_ASSETS_DETAIL_HEALTH; 
      y = SIZE_HALF + (TXT_H*4) + (TXT_H/4); x = P_TXT_W;
    };

    class CapacityLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*5;
      text = "Capacity:";
    };
    class CapacityData: YSF_RscText {
      idc = IDC_ASSETS_DETAIL_CARGO; 
      y = SIZE_HALF + TXT_H*5; x = P_TXT_W;
      text = "-";
    };

    class PassengersLabel: YSF_RscText {
      idc = -1; 
      y = SIZE_HALF + TXT_H*6;
      text = "Passengers:";
    };
    class PassengersData: YSF_RscText {
      idc = IDC_ASSETS_DETAIL_PLAYERS; 
      y = SIZE_HALF + TXT_H*6; x = P_TXT_W;
      text = "-";
    };

    // class CurrentTaskLabel: YSF_RscText {
    //   idc = -1; 
    //   y = SIZE_HALF + TXT_H*6;
    //   text = "Current Task:";
    // };
    // class CurrentTaskData: YSF_RscText {
    //   idc = IDC_ASSETS_DETAIL_WP; 
    //   y = SIZE_HALF + TXT_H*6; x = P_TXT_W;
    //   text = "-";
    // };

    // class LoadoutLabel: YSF_RscText {
    //   idc = -1; 
    //   y = SIZE_HALF + TXT_H*7;
    //   text = "Loadout:";
    // };
    // class LoadoutData: YSF_StructuredText {
    //   idc = IDC_ASSETS_DETAIL_LOADOUT; 
    //   y = SIZE_HALF + TXT_H*7; x = P_TXT_W;
    //   text = "-";
    // };

    class UplinkStatusLbl: YSF_UplinkStatusLbl {};
    class UplinkStatusRef: YSF_UplinkStatusRef {};

    // 4th quadrant
    class TaskLabel: YSF_LargeRscText {
      idc = -1; 
      x = SIZE_HALF; y = SIZE_HALF;
      text = "Task Orders:";
    };

    class TaskG_Transport: YSF_RscControlsGroup {
      idc = IDC_TASK_G_TRANSPORT; x=SIZE_HALF; y=SIZE_HALF; w=SIZE_HALF; h=SIZE_HALF;
      // onLoad = "['transport', _this#0] call YOSHI_showOrHide;";
      class Controls {
        class LblCoord: YSF_GridLbl {};
        class GridCoord: YSF_GridRef {idc=IDC_TASK_TXP_GRID_REF; };
        class LblAlt: YSF_RscText { idc=-1; x=0; y=P_TXT_H*2; text="Flight Altitude (m):"; };
        class EdtAlt: YSF_RscEdit { idc=IDC_TASK_TXP_ALT_EDIT; x=P_TXT_W; y=P_TXT_H*2; text="str(['alt'] call YOSHI_getTRN_key)"; onKeyUp = "['alt', _this#0] call YOSHI_setTRN_Altitude;"; maxChars = 5;};
        // class LblIgn: YSF_RscText { idc=-1; x=0; y=P_TXT_H*3; text="Ignore Enemy:"; };
        // class ChkIgn: YSF_Checkbox { idc=IDC_TASK_TXP_IGN_CHK; x=P_TXT_W*1.75; y=P_TXT_H*3; w=BTN_H; h=BTN_H; onCheckedChanged = "['ignore_en', _this#0] call YOSHI_setTRN_IgnoreEnemy;"; };
        // class LblDcl: YSF_RscText { idc=-1; x=0; y=P_TXT_H*4; text="Don't climb before landing:"; };
        // class ChkDcl: YSF_Checkbox { idc=IDC_TASK_TXP_DCL_CHK; x=P_TXT_W*1.75; y=P_TXT_H*4; w=BTN_H; h=BTN_H; onCheckedChanged = "['do_not_climb', _this#0] call YOSHI_setTRN_DoNotClimb;"; };
        class BtnSubmit: YSF_BtnSubmit { action = "call YOSHI_taskTRN_submit;";};
      };
    };

    class TaskG_CAS: YSF_RscControlsGroup {
      idc = IDC_TASK_G_CAS; x=SIZE_HALF; y=SIZE_HALF; w=SIZE_HALF; h=SIZE_HALF;
      // onLoad = "['cas', _this#0] call YOSHI_showOrHide;";
      class Controls {
        class LblCoord: YSF_GridLbl {};
        class GridCoord: YSF_GridRef {idc=IDC_TASK_CAS_GRID_REF;};
        class LblAlt: YSF_RscText { idc=-1; x=0; y=P_TXT_H*2; text="Flight Altitude (m):"; };
        class EdtAlt: YSF_RscEdit { idc=IDC_TASK_CAS_ALT_EDIT; x=P_TXT_W; y=P_TXT_H*2; onKeyUp= "['alt', _this#0] call YOSHI_setCAS_Altitude;"; maxChars = 5;};
        class LblTL: YSF_RscText { idc=-1; x=0; y=P_TXT_H*3; text="Time Limit (in minutes):"; };
        class EdtTL: YSF_RscEdit { idc=IDC_TASK_CAS_TL_EDIT; x=P_TXT_W; y=P_TXT_H*3; onKeyUp= "['time_limit', _this#0] call YOSHI_setCAS_TimeLimit;"; maxChars = 2;};
        class BtnSubmit: YSF_BtnSubmit {action = "call YOSHI_taskCAS_submit;";};
      };
    };

    class TaskG_Arty: YSF_RscControlsGroup {
      idc = IDC_TASK_G_ARTY; x=SIZE_HALF; y=SIZE_HALF; w=SIZE_HALF; h=SIZE_HALF;
      // onLoad = "['arty', _this#0] call YOSHI_showOrHide;";
      class Controls {
        class LblCoord: YSF_GridLbl {};
        class GridCoord: YSF_GridRef {idc=IDC_TASK_ARTY_GRID_REF;};
        class LblOrd: YSF_RscText { idc=-1; x=0; y=P_TXT_H*2; text="Ordnance:"; };
        class CmbOrd: YSF_RscCombo {
          idc=IDC_TASK_ARTY_ORD_COMBO; x=P_TXT_W; y=P_TXT_H*2; w=SIZE_HALF-P_TXT_W-0.02; h=BTN_H;
          onLBSelChanged = "['ord', _this#0] call YOSHI_handleOrdinanceSelection;";
        };
        class LblSpr: YSF_RscText { idc=-1; x=0; y=P_TXT_H*3; text="Spread: (in meters)"; };
        class EdtSpr: YSF_RscEdit {
          idc=IDC_TASK_ARTY_SPR_EDIT; x=P_TXT_W; y=P_TXT_H*3;
          onKeyUp = "['spread', _this#0] call YOSHI_setSpread;";
          maxChars = 5;
        };
        class LblCnt: YSF_RscText { idc=-1; x=0; y=P_TXT_H*6; text="Count:"; };
        class EdtCnt: YSF_RscEdit {
          idc=IDC_TASK_ARTY_CNT_EDIT; x=P_TXT_W; y=P_TXT_H*6;
          onKeyUp = "['count', _this#0] call YOSHI_setCount;";
          maxChars = 2;
        };
        class LblPat: YSF_RscText { idc=-1; x=0; y=P_TXT_H*4; text="Strike Pattern:"; };
        class CmbPat: YSF_RscCombo {
          idc=IDC_TASK_ARTY_PAT_COMBO; x=P_TXT_W; y=P_TXT_H*4; w=SIZE_HALF-P_TXT_W-0.02; h=BTN_H;
          onLBSelChanged = "['pattern', _this#0] call YOSHI_setPattern;";
        };
        class LblDir: YSF_RscText { idc=-1; x=0; y=P_TXT_H*5; text="Direction: (in deg)"; };
        class EdtDir: YSF_RscEdit {
          idc=IDC_TASK_ARTY_DIR_EDIT; x=P_TXT_W; y=P_TXT_H*5; 
          onKeyUp = "['dir', _this#0] call YOSHI_setDirection;";
          maxChars = 3;
        };
        class BtnSubmit: YSF_BtnSubmit { action = "call YOSHI_taskArty_submit;";};
      };
    };

    class TaskG_Recon: YSF_RscControlsGroup {
      idc = IDC_TASK_G_RECON; x=SIZE_HALF; y=SIZE_HALF; w=SIZE_HALF; h=SIZE_HALF;
      // onLoad = "['recon', _this#0] call YOSHI_showOrHide;";
      class Controls {
        class LblCoord: YSF_GridLbl {};
        class GridCoord: YSF_GridRef {idc=IDC_TASK_RECON_GRID_REF;};
        class LblAlt: YSF_RscText { idc=-1; x=0; y=P_TXT_H*2; text="Flight Altitude (m):"; };
        class EdtAlt: YSF_RscEdit { idc=IDC_TASK_RECON_ALT_EDIT; x=P_TXT_W; y=P_TXT_H*2; onKeyUp="['alt', _this#0] call YOSHI_setRecon_Altitude;"; };
        class LblRad: YSF_RscText { idc=-1; x=0; y=P_TXT_H*3; text="Radius:"; };
        class EdtRad: YSF_RscEdit { idc=IDC_TASK_RECON_RAD_EDIT; x=P_TXT_W; y=P_TXT_H*3; onKeyUp="['radius', _this#0] call YOSHI_setRecon_Radius;";};
        class BtnSubmit: YSF_BtnSubmit {};
      };
    };

    class TaskG_FixedWing: YSF_RscControlsGroup {
      idc = IDC_TASK_G_FIXEDWING; x=SIZE_HALF; y=SIZE_HALF; w=SIZE_HALF; h=SIZE_HALF;
      class Controls {
        class LblStatus: YSF_RscText { idc=-1; x=0; y=P_TXT_H; text="Status:"; };
        class TxtStatus: YSF_RscText { idc=IDC_TASK_FW_STATUS; x=P_TXT_W; y=P_TXT_H; text="-"; };

        class LblRole: YSF_RscText { idc=-1; x=0; y=P_TXT_H*2; text="Role:"; };
        class TxtRole: YSF_RscText { idc=IDC_TASK_FW_ROLE; x=P_TXT_W; y=P_TXT_H*2; text="-"; };

        class BtnDeploy: YSF_RscButton { idc=IDC_TASK_FW_BTN_DEPLOY; x=0; y=P_TXT_H*3; text="Deploy"; action="call YOSHI_taskFW_deploy;"; };
        class BtnRTB: YSF_RscButton { idc=IDC_TASK_FW_BTN_RTB; x=BTN_W + PADDING; y=P_TXT_H*3; text="RTB"; action="call YOSHI_taskFW_rtb;"; };

        class TxtStrikeInfo: YSF_RscText {
          idc=IDC_TASK_FW_STRIKE_INFO;
          x=0; y=P_TXT_H*4;
          w=SIZE_HALF; h=TXT_H;
          text="Strike: use scroll actions with a laser target and VIGIL tablet.";
        };
        class LblLaserDesignator: YSF_RscText {
          idc=IDC_TASK_FW_LASER_LABEL;
          x=0; y=P_TXT_H*5;
          text="Designator:";
        };
        class CmbLaserDesignator: YSF_RscCombo {
          idc=IDC_TASK_FW_LASER_COMBO;
          x=P_TXT_W; y=P_TXT_H*5; w=SIZE_HALF-P_TXT_W-0.02; h=BTN_H;
          onLBSelChanged = "_this call YOSHI_taskFW_OnDesignatorChanged;";
        };
        class LblLGBType: YSF_RscText {
          idc=IDC_TASK_FW_LGB_LABEL;
          x=0; y=P_TXT_H*6;
          text="LGB Type:";
        };
        class CmbLGBType: YSF_RscCombo {
          idc=IDC_TASK_FW_LGB_COMBO;
          x=P_TXT_W; y=P_TXT_H*6; w=SIZE_HALF-P_TXT_W-0.02; h=BTN_H;
          onLBSelChanged = "_this call YOSHI_taskFW_OnBombWeaponChanged;";
        };
        class LblLGMType: YSF_RscText {
          idc=IDC_TASK_FW_LGM_LABEL;
          x=0; y=P_TXT_H*7;
          text="LGM Type:";
        };
        class CmbLGMType: YSF_RscCombo {
          idc=IDC_TASK_FW_LGM_COMBO;
          x=P_TXT_W; y=P_TXT_H*7; w=SIZE_HALF-P_TXT_W-0.02; h=BTN_H;
          onLBSelChanged = "_this call YOSHI_taskFW_OnMissileWeaponChanged;";
        };
        class BtnExtLGB: YSF_RscButton {
          idc=IDC_TASK_FW_BTN_LGB_EXT;
          x=0; y=P_TXT_H*8;
          text="Release LGB";
          action="['bomb'] call YOSHI_taskFW_requestStrikeFromDesignator;";
        };
        class BtnExtLGM: YSF_RscButton {
          idc=IDC_TASK_FW_BTN_LGM_EXT;
          x=BTN_W + PADDING; y=P_TXT_H*8;
          text="Release LGM";
          action="['missile'] call YOSHI_taskFW_requestStrikeFromDesignator;";
        };
        class BtnLogi: YSF_RscButton { idc=IDC_TASK_FW_BTN_LOGI; x=BTN_W + PADDING; y=P_TXT_H*9; text="Fabricator"; action="call YOSHI_taskFW_logiStub;"; };

        class BtnRefresh: YSF_RscButton { idc=IDC_TASK_FW_BTN_REFRESH; x=SIZE_FULL-(BTN_W+PADDING); y=SIZE_FULL-TXT_H; text="Refresh"; action="call YOSHI_taskFW_refresh;"; };
      };
    };
  };
};


