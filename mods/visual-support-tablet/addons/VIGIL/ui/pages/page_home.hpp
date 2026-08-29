
// class Tablet_Page_Home: YSF_RscControlsGroup {
//   idc = IDC_PAGE_HOME;
//   onLoad = "_this call YSF_home_onLoad;";
//   class Controls {
//     class L1: YSF_RscText { idc=-1; text="Governor Tasks"; };

//     class Tasks: YSF_RscListbox {
//       idc=IDC_HOME_TASKS;
//       y=P_TXT_H*2 + P_TXT_H;
//       w=1;
//       h=1 - (P_TXT_H*4);
//       columns[]={0.00,0.36,0.58,0.78,0.94};
//       onLBDblClick="['dbl',_this] call YSF_home_tasks_click;";
//       onLBSelChanged="['sel',_this] call YSF_home_tasks_click;";
//     };

//     class Refresh: YSF_RscButton {
//       idc=IDC_HOME_REFRESH;
//       y=1 - BTN_H;
//       w=BTN_W;
//       text="Refresh";
//       action="['refresh'] call YSF_home_tasks;";
//     };

//     class CancelSel: YSF_RscButton {
//       idc=IDC_HOME_CANCEL_SELECTED;
//       x=BTN_W;
//       y=1 - BTN_H;
//       w=BTN_W;
//       text="Cancel Selected";
//       action="['cancelSelected'] call YSF_home_tasks;";
//     };
//   };
// };