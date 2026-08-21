#include "ui\defines.hpp"

class CfgPatches {
    class YSF_Tablet {
        name = "YSF Tablet";
        units[] = {        
            "YSF_Item_VigilTerminal_B",
            "YSF_Item_VigilTerminal_I",
            "YSF_Item_VigilTerminal_O",
            "YSF_Toggle_To_Whitelist_Module",
            "YSF_Asset_Whitelist_Module",
            "YSF_FixedWing_Asset_Module",
            "YSF_FixedWing_Infil_Module",
            "YSF_FixedWing_Exfil_Module",
            "YSF_FixedWing_Zeus_Add_Module"
        };
        weapons[] = {
            "YSF_VigilTerminal_B",
            "YSF_VigilTerminal_I",
            "YSF_VigilTerminal_O"
        };
        requiredVersion = 2.20;
        requiredAddons[] = {"cba_main", "YCD_CORDIS", "A3_Data_F", "A3_UI_F", "A3_Props_F_Exp_A", "A3_Weapons_F"};
        version = "1.0";
        author = "Yoshi";
    };
};


class CfgFunctions {
    class YSF {
        tag = "YSF";
        
        class Client {
            file = "\VIGIL\functions\client";
            class initPlayerLocal { postInit = 1; };
            class irLaserViz {preInit = 1; };
        };
        class Global {
            file = "\VIGIL\functions\global";
            class constants { preInit = 1; };
            class core { preInit = 1;};
            class fwLaserTest { preInit = 1; };
            class heliStabilizer { preInit = 1; };
            class init { postInit = 1; };
            class utils {preInit = 1; };
            class initSettings {preInit = 1; };
            class whitelistRegistry {preInit = 1; };
            class assetWhitelist {};
            class toggleObjectInWhitelist {};
            class whitelistZeusClaimServer {};
            class whitelistZeusResult {};
        };
        class Governor {
            file = "\VIGIL\functions\governor";
            class governor { preInit = 1; };
        };
        class Server {
            file = "\VIGIL\functions\server";
            class initServer { postInit = 1; };
        };
        class TaskArtillery {
            file = "\VIGIL\functions\task_artillery";
            class arty {preInit = 1;};
            class artillery_task {postInit = 1; };
            class ui_arty { preInit = 1; };
        };
        class TaskCAS {
            file = "\VIGIL\functions\task_cas";
            class cas {preInit = 1;};
            class airAutoEngage { preInit = 1; };
            class cas_task {postInit = 1; };
        };
        class TaskTransport {
            file = "\VIGIL\functions\task_transport";
            class transport {preInit = 1;};
            class transport_task {postInit = 1; };
        };
        class TaskRecon {
            file = "\VIGIL\functions\task_recon";
            class recon {preInit = 1;};
            class recon_task {postInit = 1; };
        };
        class TaskFixedWing {
            file = "\VIGIL\functions\task_fixedWing";
            class initFixedWingFunctions { preInit = 1; };
            class fixedWing { preInit = 1; };
            class fwModuleAsset {};
            class fwModuleInfil {};
            class fwModuleExfil {};
            class fwModuleZeusAdd {};
        };
        class Tablet {
            file = "\VIGIL\functions\tablet";
            class assets {preInit = 1;};
            class homepage { preInit = 1; };
            class ui_utils { preInit = 1;};
        };
    };
};


class YSF_Tablet_Dialog {
    idd = 88000;
    movingEnable = 0;
    enableSimulation = 1;
    onLoad = "uiNamespace setVariable ['YSF_Tablet_Display', _this select 0]; call YSF_UI_Nav;";
    onUnload = "call YSF_clearAllMarkers; uiNamespace setVariable ['YSF_Tablet_Display', displayNull];playSound 'TurnOff';";
    class controlsBackground {};
    class controls {
        #include "ui\tablet_base.hpp"
        #include "ui\pages\page_assets.hpp"

        class IntroText: YSF_IntroText {};
        class TabletWrapper: RscPicture {
            idc = IDC_TABLET_BG;
            x = -0.154;
            y = -0.144;
            w = 1.32;
            h = 1.32;
            text = "";
        };
    };
};

class CfgVehicles {
    class Item_Base_F;

    class YSF_Item_VigilTerminal_B: Item_Base_F {
        scope = 2;
        scopeCurator = 2;
        scopeArsenal = 2;
        displayName = "VIGIL Combat Tablet [BLU] (Item)";
        author = "YSF";
        editorCategory = "EdCat_Equipment";
        editorSubcategory = "EdSubcat_InventoryItems";
        faction = "BLU_F";
        descriptionShort = "Use this to connect to the VIGIL intranet";

        class TransportItems {
            class _xx_YSF_VigilTerminal_B {
                name = "YSF_VigilTerminal_B";
                count = 1;
            };
        };
    };

    class YSF_Item_VigilTerminal_I: YSF_Item_VigilTerminal_B {
        displayName = "VIGIL Combat Tablet [IND] (Item)";
        faction = "IND_F";
        class TransportItems {
            class _xx_YSF_VigilTerminal_I {
                name = "YSF_VigilTerminal_I";
                count = 1;
            };
        };
    };

    class YSF_Item_VigilTerminal_O: YSF_Item_VigilTerminal_B {
        displayName = "VIGIL Combat Tablet [OPF] (Item)";
        faction = "OPF_F";
        class TransportItems {
            class _xx_YSF_VigilTerminal_O {
                name = "YSF_VigilTerminal_O";
                count = 1;
            };
        };
    };

    class Logic;
    class Module_F: Logic {
        class AttributesBase
        {
            class Edit;
            class Units;
            class Combo;
            class Checkbox;
        };
        class ModuleDescription;
    };
    class YSF_Asset_Whitelist_Module: Module_F {
        author = "Yoshi";
        category = "VigilSupport_Category";
        displayName = "Asset Whitelist Module";
        icon = "\A3\ui_f\data\map\markers\military\circle_CA.paa";
        function = "YSF_fnc_assetWhitelist";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};            
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "Place this module to set up whitelisted assets.",
                "Location of module is meaningless.",
                "Any synced vehicles will be available to all players via the VIGIL Support Tablet.",
                "Note: You can use the 'Add/Remove Asset from Whitelist' module to dynamically modify the whitelist during the mission.",
            };
            sync[] = {"AnyVehicle"};
        };
    };

    class YSF_Toggle_To_Whitelist_Module : Module_F {
        scope = 1;
        scopeCurator = 2;
        displayName = "Add/Remove from Whitelist";
        category = "VigilSupport_ZEUS_Category";
        function = "YSF_fnc_toggleObjectInWhitelist";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        curatorCanAttach = 1;
        vehicleClass = "Modules";

        class ModuleDescription {
            description = "Place on asset to add/remove it to the whitelist defined by the Asset Whitelist Module.";
            sync[] = {"AnyVehicle"};
            syncRequired = 0;
        };
    };

    class YSF_FixedWing_Asset_Module: Module_F {
        author = "Yoshi";
        category = "VigilSupport_Category";
        displayName = "Fixed Wing Asset Module";
        icon = "\a3\ui_f\data\igui\cfg\simpletasks\types\Plane_ca.paa";
        function = "YSF_fnc_fwModuleAsset";
        functionPriority = 1;
        scope = 2;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class ModuleDescription: ModuleDescription {};
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "Registers synced planes as Fixed Wing assets for VIGIL.",
                "Registered assets are stored as snapshots and despawned until deployed.",
                "Location of this module is irrelevant."
            };
            sync[] = {"AnyVehicle"};
        };
    };

    class YSF_FixedWing_Infil_Module: Module_F {
        author = "Yoshi";
        category = "VigilSupport_Category";
        displayName = "Fixed Wing Infil Point";
        icon = "\A3\ui_f\data\map\markers\military\start_CA.paa";
        function = "YSF_fnc_fwModuleInfil";
        functionPriority = 1;
        scope = 2;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class ModuleDescription: ModuleDescription {};
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "Defines the default spawn point for Fixed Wing deployment.",
                "Module position is used as the infil point."
            };
        };
    };

    class YSF_FixedWing_Exfil_Module: Module_F {
        author = "Yoshi";
        category = "VigilSupport_Category";
        displayName = "Fixed Wing Exfil Point";
        icon = "\A3\ui_f\data\map\markers\military\end_CA.paa";
        function = "YSF_fnc_fwModuleExfil";
        functionPriority = 1;
        scope = 2;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class ModuleDescription: ModuleDescription {};
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "Defines the default RTB/despawn point for Fixed Wing assets.",
                "Module position is used as the exfil point."
            };
        };
    };

    class YSF_FixedWing_Zeus_Add_Module : Module_F {
        scope = 1;
        scopeCurator = 2;
        displayName = "Add Fixed Wing Asset";
        category = "VigilSupport_ZEUS_Category";
        icon = "\a3\ui_f\data\igui\cfg\simpletasks\types\Plane_ca.paa";
        function = "YSF_fnc_fwModuleZeusAdd";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        curatorCanAttach = 1;
        vehicleClass = "Modules";

        class ModuleDescription {
            description = "Place on a plane to add it to the Fixed Wing VIGIL registry.";
            sync[] = {"AnyVehicle"};
            syncRequired = 0;
        };
    };
};

class CfgFactionClasses {
    class NO_CATEGORY;
    class VigilSupport_Category: NO_CATEGORY {
        displayName = "Pontifex: VIGIL Utils"; // Name displayed in Eden Editor
        priority = 2; // Position of the category in the list
        side = 7; // Logic
    };

    class VigilSupport_ZEUS_Category{
        displayName = "Pontifex: VIGIL Utilities"; 
        priority = 2; 
        side = 7;
    };
};

class CfgWeapons {
    class B_UavTerminal;

    class YSF_VigilTerminal_B: B_UavTerminal {
        scope = 2;
        scopeCurator = 2;
        scopeArsenal = 2;
        faction = "BLU_F";
        displayName = "VIGIL Combat Tablet [BLU]";
        editorCategory = "EdCat_Equipment";
        editorSubcategory = "EdSubcat_InventoryItems";
        author = "YSF";

        model = "\A3\Props_F_Exp_A\Military\Equipment\Tablet_02_F.p3d";
        picture = "\VIGIL\ui\assets\b_terminal.paa";
        descriptionShort = "Use this to connect to the Pontifex intranet";

        hiddenSelections[] = {"Camo_1", "Camo_2"};
        hiddenSelectionsTextures[] = {
            "",
            "\VIGIL\ui\assets\vigil_tablet_b.paa"
        };
    };

    class YSF_VigilTerminal_I: YSF_VigilTerminal_B {
        faction = "IND_F";
        displayName = "VIGIL Combat Tablet [IND]";
        picture = "\VIGIL\ui\assets\i_terminal.paa";
        hiddenSelectionsTextures[] = {
            "",
            "\VIGIL\ui\assets\vigil_tablet_i.paa"
        };
    };

    class YSF_VigilTerminal_O: YSF_VigilTerminal_B {
        faction = "OPF_F";
        displayName = "VIGIL Combat Tablet [OPF]";
        picture = "\VIGIL\ui\assets\o_terminal.paa";
        hiddenSelectionsTextures[] = {
            "",
            "\VIGIL\ui\assets\vigil_tablet_o.paa"
        };
    };
};


class CfgSounds {
    sounds[] = {};

    class UiChar01 {
        name = "ui_char_01";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_char_01.ogg", 1, 1};
        titles[] = {};
    };
    class UiChar02 {
        name = "ui_char_02";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_char_02.ogg", 1, 1};
        titles[] = {};
    };
    class UiChar03 {
        name = "ui_char_03";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_char_03.ogg", 1, 1};
        titles[] = {};
    };
    class UiChar04 {
        name = "ui_char_04";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_char_04.ogg", 1, 1};
        titles[] = {};
    };
    class UiChar05 {
        name = "ui_char_05";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_char_05.ogg", 1, 1};
        titles[] = {};
    };
    class UiChar06 {
        name = "ui_char_06";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_char_06.ogg", 1, 1};
        titles[] = {};
    };

    class UiHover {
        name = "ui_hover";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_hover.ogg", 1, 1};
        titles[] = {};
    };
    class UiTabSwitch {
        name = "ui_tab_switch";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_tab_transition_01.ogg", 1, 1};
        titles[] = {};
    };
    class UiActivate {
        name = "ui_activate";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_activation.ogg", 1, 1};
        titles[] = {};
    };
    class UiSelect {
        name = "ui_select";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_select.ogg", 1, 1};
        titles[] = {};
    };
    class UiMapSelect {
        name = "ui_map_select";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_map_select.ogg", 1, 1};
        titles[] = {};
    };

    class UiOpen {
        name = "ui_open";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_open_01.ogg", 1, 1};
        titles[] = {};
    };
    class UiClose {
        name = "ui_close";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_close_01.ogg", 1, 1};
        titles[] = {};
    };

    class UiSubmit {
        name = "ui_submit";
        sound[] = {"VIGIL\sounds\tablet\tablet_ui_submit.ogg", 1, 1};
        titles[] = {};
    };

    class UiHum {
        name = "ui_hum";
        sound[] = {"VIGIL\sounds\tablet\tablet_hum.ogg", 1, 1};
        titles[] = {};
    };
    class DialUp {
        name = "ui_dial_up";
        sound[] = {"VIGIL\sounds\tablet\dial-up-internet.ogg", 1, 1};
        titles[] = {};
    };
    class BootUp {
        name = "ui_boot_ui";
        sound[] = {"VIGIL\sounds\tablet\boot_up.ogg", 1, 1};
        titles[] = {};
    };
    class TurnOff {
        name = "ui_turn_off";
        sound[] = {"VIGIL\sounds\tablet\turnOff.ogg", 1, 1};
        titles[] = {};
    };
};

class CfgRadio
{
	sounds[] += {
		"YSF_TransportAck",
		"YSF_ArtilleryAck",
		"YSF_ArtilleryRoundsComplete",
		"YSF_CASAck",
		"YSF_CASDone"
	};
    class YSF_TransportAck
	{
		name	= "YSF_TransportAck";
		sound[]	= { "\VIGIL\sounds\support\transport_acknowledged.ogg", 1, 1 };
		title	= "Roger, air-taxi on the way.";
	};
    class YSF_ArtilleryAck
	{
		name	= "YSF_ArtilleryAck";
		sound[]	= { "\VIGIL\sounds\support\artillery_acknowledged.ogg", 1, 1 };
		title	= "Target location received, ordinance is in-bound, Out.";
	};
    class YSF_ArtilleryRoundsComplete
	{
		name	= "YSF_ArtilleryRoundsComplete";
		sound[]	= { "\VIGIL\sounds\support\artillery_rounds_complete.ogg", 1, 1 };
		title	= "Rounds complete, Out.";
	};
    class YSF_CASAck
	{
		name	= "YSF_CASAck";
		sound[]	= { "\VIGIL\sounds\support\cas_heli_acknowledged.ogg", 1, 1 };
		title	= "Roger, coordinates received, CAS is in-bound, Out.";
	};
    class YSF_CASDone
	{
		name	= "YSF_CASDone";
		sound[]	= { "\VIGIL\sounds\support\cas_heli_accomplished.ogg", 1, 1 };
		title	= "CAS mission complete, RTB, Out.";
	};
};
