#include "ui\defines.hpp"

class CfgPatches {
    class YFU_FieldUtils {
        name = "YFU Field Utilities";
        units[] = {"YFU_Bridge_Box"};
        weapons[] = {};
        requiredVersion = 2.20;
        requiredAddons[] = {"cba_main", "YCD_CORDIS", "ace_main", "ace_common", "zen_main","A3_Data_F", "A3_UI_F", "A3_Props_F_Exp_A", "A3_Weapons_F", "A3_Structures_F_Exp_Civilian_Accessories"};
        version = "1.0";
        author = "Yoshi";
    };
};


class CfgFunctions {
    class YFU {
        tag = "YFU";
        
        class Client {
            file = "\FieldUtils\functions\client";
            class initPlayerLocal { postInit = 1; };
        };
        class Bridge {
            file = "\FieldUtils\functions\bridge";
            class bridgeUtils { preInit = 1; };
        };
        class Drone {
            file = "\FieldUtils\functions\drone";
            class fpv { preInit = 1; };
        };
        class Fabricator {
            file = "\FieldUtils\functions\fabricator";
            class fabricationActions { preInit = 1; };
            class assets { preInit = 1; };
            class ui_utils { preInit = 1; };
            class boxPacking { preInit = 1; };
        };
        class Global {
            file = "\FieldUtils\functions\global";
            class constants { preInit = 1; };
            class fabricator {preInit = 1;};
            class core { preInit = 1;};
            class init { postInit = 1; };
            class initGeometry { preInit = 1; };
            class initMapTools { preInit = 1; };
            class initModuleLogicSetters {preInit = 1; };
            class initSettings {preInit = 1; };
            class objectHandling {preInit = 1;};
            class sounds {preInit = 1;};
        };
        class Logi {
            file = "\FieldUtils\functions\logi";
            class logiActions {preInit = 1; };
        };
        class Ropes {
            file = "\FieldUtils\functions\ropes";
            class initRopes { preInit = 1; };
            class ropeActions {preInit = 1;};
        };
        class Server {
            file = "\FieldUtils\functions\server";
            class fabricatorServer { preInit = 1; };
            class initServer { postInit = 1; };
        };
    };
};

class YFU_FieldUtils_Dialog {
    idd = YFU_IDD_FABRICATOR_DIALOG;
    movingEnable = 0;
    enableSimulation = 1;
    onLoad = "uiNamespace setVariable ['YFU_FieldUtils_Display', _this select 0]; [] spawn { uiSleep 0.01; call YFU_assetsInitPage; };";
    onUnload = "uiNamespace setVariable ['YFU_FieldUtils_Display', displayNull];";
    class controlsBackground {};
    class controls {
        #include "ui\tablet_base.hpp"
        #include "ui\pages\page_assets.hpp"

        class TabletWrapper: RscPicture {
            idc = YFU_IDC_TABLET_WRAPPER;
            x = -0.154;
            y = -0.144;
            w = 1.32;
            h = 1.32;
            text = "";
        };
    };
};

class YFU_BridgeBuilder_Dialog {
    idd = YFU_IDD_BRIDGE_DIALOG;
    movingEnable = 0;
    enableSimulation = 1;
    onLoad = "uiNamespace setVariable ['YFU_BridgeBuilder_Display', _this select 0]; [] spawn { uiSleep 0.01; call YFU_bridge_onDialogLoad; };";
    onUnload = "call YFU_bridge_onDialogUnload; uiNamespace setVariable ['YFU_BridgeBuilder_Display', displayNull];";
    class controlsBackground {};
    class controls {
        #include "ui\tablet_base.hpp"
        #include "ui\pages\page_bridge.hpp"

        class TabletWrapper: RscPicture {
            idc = YFU_IDC_TABLET_WRAPPER;
            x = -0.154;
            y = -0.144;
            w = 1.32;
            h = 1.32;
            text = "";
        };
    };
};

class CfgVehicles {
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

    class FieldUtils_Virtual_Storage_Module: Module_F {
        author = "Yoshi";
        category = "FieldUtilsSupport_Category";
        displayName = "Virtual Storage Module";
        icon = "\FieldUtils\ui\virtualStorage.paa";
        function = "YOSHI_setVirtualStorageLogic";
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
                "THIS MODULE REQUIRES Fabricator Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use Virtual Storage",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced items will be available to Fabricators as an option to spawn a copy in."
            };
            sync[] = {};
        };
    };

    class FieldUtils_Fabricator_Module: Module_F {
        author = "Yoshi";
        category = "FieldUtilsSupport_Category";
        displayName = "Fabricator Module";
        icon = "\FieldUtils\ui\fabricator.paa";
        function = "YOSHI_setFabricatorLogic";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class EnableLocalArsenal: Checkbox {
                property = "Fabricator_Module_EnableLocalArsenal";
                displayName = "Enable local virtual inventory";
                tooltip = "Enabling this will add an action to containers near the fabricator, that will access a virtual inventory -- allowing for easy supply creation without needing to open/close an arsenal (Uses ZEN Inventory)";
                typeName = "BOOLEAN";
                defaultValue = "true"; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Virtual Storage Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use Fabricators",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced items will be considered Fabricators, they will have ace interact options to spawn in any items synced with the Virtual Storage Module.", 
            };
            sync[] = {};
        };
    };

    class Rope;
    class Spring100xRope : Rope
	{
		maxRelLenght = 1.1;			
		maxExtraLenght = 20;
		springFactor = 100;	
		torqueFactor = 0.5;
		dampingFactor[] = {1.0,2.5,1.0};
	};
    class Spring50xRope : Rope
	{
		maxRelLenght = 1.1;			
		maxExtraLenght = 20;
		springFactor = 50;	
		torqueFactor = 0.5;
		dampingFactor[] = {1.0,2.5,1.0};
	};
    class Spring10xRope : Rope
	{
		maxRelLenght = 1.1;			
		maxExtraLenght = 20;
		springFactor = 10;	
		torqueFactor = 0.5;
		dampingFactor[] = {1.0,2.5,1.0};
	};
    class Spring1xRope : Rope
	{
		maxRelLenght = 1.1;			
		maxExtraLenght = 20;
		springFactor = 1;	
		torqueFactor = 0.5;
		dampingFactor[] = {1.0,2.5,1.0};
	};

    class Box_NATO_WpsSpecial_F;
    class YFU_Bridge_Box: Box_NATO_WpsSpecial_F
	{
		author="Yoshi";
		picture="\FieldUtils\ui\preview\bridge_layer_preview.paa";
		editorPreview="\FieldUtils\ui\preview\bridge_layer_preview.paa"; 
		_generalMacro="YFU_Bridge_Box"; 

		displayName="Bridge Construction Box"; 
		editorCategory="EdCat_Supplies";

		maximumLoad=3000;
		ace_cargo_size = 2;  // Adjust the size as needed
		ace_cargo_canLoad = 1;  // 1 to allow loading into vehicles, 0 to disallow
		ace_dragging_canDrag = 1;  // 1 to enable dragging, 0 to disable
		ace_dragging_canCarry = 1;  // 1 to enable carrying, 0 to disable
		ace_dragging_dragPosition[] = {0, 1.2, 0};  // Adjust the position as needed
		ace_dragging_dragDirection = 0;  // Adjust the direction as needed
		ace_dragging_ignoreWeightCarry = 1;
		ace_dragging_ignoreWeight = 1;

		hiddenSelections[]=
		{
			"Camo_Signs",
			"Camo"
		};
		hiddenSelectionsTextures[]=
		{
			"\FieldUtils\ui\assets\bridge_layer_sign.paa", //text
			"\FieldUtils\ui\assets\bridge_layer_base.paa" //base
		};
	};
};

class CfgFactionClasses {
    class NO_CATEGORY;
    class FieldUtilsSupport_Category: NO_CATEGORY {
        displayName = "Pontifex: Field Utilities"; // Name displayed in Eden Editor
        priority = 2; // Position of the category in the list
        side = 7; // Logic
    };

    class FieldUtilsSupport_ZEUS_Category{
        displayName = "Pontifex: Zeus Field Utilities"; 
        priority = 2; 
        side = 7;
    };
};


class CfgSounds {
    sounds[] = {
        "DufflebagShuffle",
        "YFU_FpvClick1",
        "YFU_FpvClick2"
    };

    // class UiChar01 {
    //     name = "ui_char_01";
    //     sound[] = {"FieldUtils\sounds\...", 1, 1};
    //     titles[] = {};
    // };
    class DufflebagShuffle {
        name = "dufflebagShuffle";
        sound[] = {"\FieldUtils\sounds\dufflebagShuffle.ogg", 1, 1};
        titles[] = {};
    };
    class YFU_FpvClick1 {
        name = "YFU_FpvClick1";
        sound[] = {"\FieldUtils\sounds\fpv\click1.ogg", 1, 1};
        titles[] = {};
    };
    class YFU_FpvClick2 {
        name = "YFU_FpvClick2";
        sound[] = {"\FieldUtils\sounds\fpv\click2.ogg", 1, 1};
        titles[] = {};
    };
};

class CfgRadio
{
    // class YFU_TransportAck
	// {
	// 	name	= "TransportAck";
	// 	sound[] = {"FieldUtils\sounds\...", 1, 1};
	// 	title	= "Roger, air-taxi on the way.";
	// };
};
