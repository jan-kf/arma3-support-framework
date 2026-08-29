class YFU_Page_Assets: YFU_RscControlsGroup {
    idc = YFU_IDC_PAGE_ASSETS;
    x = 0;
    y = 0;
    w = YFU_SIZE_FULL;
    h = YFU_SIZE_FULL;
    onLoad = "uiNamespace setVariable ['YFU_PageAssets_Group', _this select 0];";
    class VScrollbar { width = 0; autoScrollEnabled = 0; disabled = 1; scrollSpeed = 0; };
    class HScrollbar { height = 0; disabled = 1; };

    class Controls {
        class Title: YFU_LargeRscText {
            idc = -1;
            text = YFU_TITLE;
        };

        class ListHeader: YFU_LargeRscText {
            idc = -1;
            y = YFU_P_TXT_H;
            text = "Catalog";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class ListItems: YFU_RscListbox {
            idc = YFU_IDC_ASSETS_LIST;
            y = YFU_P_TXT_H + YFU_P_TXT_H;
            onLBSelChanged = "_this call YFU_assetsItemSelected;";
            onLBDblClick = "_this call YFU_assetsListDblClick;";
        };

        class InspectHeader: YFU_LargeRscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H;
            text = "Inventory";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class InspectItems: YFU_RscListbox {
            idc = YFU_IDC_INSPECT_LIST;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_P_TXT_H + YFU_P_TXT_H;
        };

        class QueueHeader: YFU_LargeRscText {
            idc = -1;
            y = YFU_SIZE_HALF + YFU_P_TXT_H;
            text = "Staging";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class QueueItems: YFU_RscControlsGroup {
            idc = YFU_IDC_QUEUE_GROUP;
            y = YFU_SIZE_HALF + YFU_P_TXT_H + YFU_P_TXT_H;
            w = YFU_SIZE_HALF - YFU_PADDING;
            h = YFU_SIZE_HALF - (YFU_P_TXT_H * 2) - YFU_PADDING;
            class VScrollbar {
                width = 0.01;
                autoScrollEnabled = 0;
                scrollSpeed = 0.04;
            };
            class HScrollbar {
                height = 0;
                disabled = 1;
            };
            class Controls {};
        };
        class QueueAddBtn: YFU_RscButton {
            idc = YFU_IDC_BTN_QUEUE_ADD;
            x = YFU_SIZE_HALF - YFU_BTN_W;
            y = YFU_SIZE_HALF + YFU_P_TXT_H;
            text = "Add to Order";
            action = "call YFU_assetsQueueAdd;";
        };

        class DeliveryHeader: YFU_LargeRscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_SIZE_HALF + YFU_P_TXT_H;
            text = "Delivery";
            sizeEx = YFU_FONT_SIZE * 1.5;
        };
        class DeliveryMethodLabel: YFU_RscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 2);
            text = "Method:";
        };
        class DeliveryMethodValue: YFU_RscText {
            idc = YFU_IDC_DELIVERY_METHOD;
            x = YFU_SIZE_HALF + YFU_P_TXT_W / 2;
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 2);
            text = "Nearby Fabricator";
        };
        class DeliveryNotesLabel: YFU_RscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 3);
            text = "Notes:";
        };
        class DeliveryNotesValue: YFU_RscText {
            idc = YFU_IDC_DELIVERY_NOTES;
            x = YFU_SIZE_HALF + YFU_P_TXT_W / 2;
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 3);
            text = "";
        };
        class DeliveryGridLabel: YFU_RscText {
            idc = -1;
            x = YFU_SIZE_HALF + YFU_PADDING;
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 4);
            text = "Grid:";
        };
        class DeliveryGridValue: YFU_RscEdit {
            idc = YFU_IDC_DELIVERY_GRID;
            x = YFU_SIZE_HALF + YFU_P_TXT_W / 2;
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 4);
            w = YFU_SIZE_HALF - YFU_P_TXT_W;
            text = "";
            onKeyUp = "_this call YFU_deliveryGridChanged;";
            onKillFocus = "_this call YFU_deliveryGridChanged;";
        };
        class SubmitOrderBtn: YFU_RscButton {
            idc = YFU_IDC_BTN_SUBMIT_ORDER;
            x = YFU_SIZE_HALF + YFU_PADDING + (YFU_SIZE_HALF / 2) - (YFU_BTN_W / 2);
            y = YFU_SIZE_HALF + (YFU_P_TXT_H * 6);
            w = YFU_BTN_W * 1.5;
            text = "Submit Order";
            action = "call YFU_assetsSubmitOrder;";
        };

        class SubmitOverlayBG: YFU_RscText {
            idc = YFU_IDC_SUBMIT_OVERLAY_BG;
            x = -YFU_SIZE_EIGHT;
            y = -YFU_SIZE_EIGHT;
            w = YFU_SIZE_FULL + YFU_SIZE_QUART;
            h = YFU_SIZE_FULL + YFU_SIZE_QUART;
            colorBackground[] = {0, 0, 0, 0.65};
            onLoad = "(_this#0) ctrlShow false;";
        };
        class SubmitOverlayClick: YFU_RscButton {
            idc = YFU_IDC_SUBMIT_OVERLAY_CLICK;
            x = -YFU_SIZE_EIGHT;
            y = -YFU_SIZE_EIGHT;
            w = YFU_SIZE_FULL + YFU_SIZE_QUART;
            h = YFU_SIZE_FULL + YFU_SIZE_QUART;
            text = "";
            colorBackground[] = {0, 0, 0, 0};
            colorBackgroundActive[] = {0, 0, 0, 0};
            colorFocused[] = {0, 0, 0, 0};
            colorBorder[] = {0, 0, 0, 0};
            action = "call YFU_assetsSubmitDismiss;";
            onLoad = "(_this#0) ctrlShow false;";
        };
        class SubmitOverlayTitle: YFU_LargeRscText {
            idc = YFU_IDC_SUBMIT_OVERLAY_TITLE;
            x = YFU_SIZE_QUART;
            y = YFU_SIZE_HALF - (YFU_P_TXT_H * 2);
            w = YFU_SIZE_HALF;
            text = "Processing Order";
            style = 2;
            onLoad = "(_this#0) ctrlShow false;";
        };
        class SubmitOverlayStatus: YFU_RscText {
            idc = YFU_IDC_SUBMIT_OVERLAY_STATUS;
            x = YFU_SIZE_QUART;
            y = YFU_SIZE_HALF - YFU_P_TXT_H;
            w = YFU_SIZE_HALF;
            text = "Packing boxes...";
            style = 2;
            onLoad = "(_this#0) ctrlShow false;";
        };
        class SubmitOverlayProgress: YFU_RscProgress {
            idc = YFU_IDC_SUBMIT_OVERLAY_PROGRESS;
            x = YFU_SIZE_QUART;
            y = YFU_SIZE_HALF;
            w = YFU_SIZE_HALF;
            h = YFU_TXT_H / 2;
            onLoad = "(_this#0) progressSetPosition 0; (_this#0) ctrlShow false;";
        };
    };
};
