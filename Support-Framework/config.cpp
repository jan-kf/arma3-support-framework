class CfgPatches {
    class SupportFramework {
        units[] = {};
        weapons[] = {
            "YOSHI_ReinsertTerminal",
            "YOSHI_CASTerminal",
            "YOSHI_ArtilleryTerminal",
            "YOSHI_ReconTerminal"
        };
        requiredVersion = 1.0;
        requiredAddons[] = {"ace_main", "ace_common"};
        author = "Yoshi";
        authorUrl = "https://github.com/jan-kf/arma3-support-framework";
    };

    class SF_SpectrumAnalyzer
	{
		addonRootClass="A3_Weapons_F_Enoch";
		requiredAddons[]=
		{
			"A3_Weapons_F_Enoch"
		};
		requiredVersion=0.1;
		units[]={};
		weapons[]=
		{
			"ysf_hgun_esd_01_F",
			"ysf_hgun_esd_01_antenna_01_F",
			"ysf_hgun_esd_01_antenna_02_F",
			"ysf_hgun_esd_01_antenna_03_F"
		};
	};
};

class CfgFunctions {
    class YOSHI {
        class Server {
            file = "\Support-Framework\Functions\Server";
            class initServer { postInit = 1; }; 
        };
        class Client {
            file = "\Support-Framework\Functions\Client";
            class initPlayerLocal { postInit = 1; };
        };
        class Actions {
            file = "\Support-Framework\Functions\Actions";
            class fixedWingActions { postInit = 1; };
        };
        class Prelude {
            file = "\Support-Framework\Functions\Prelude";
            class initCore { preInit = 1; };
            class initGeometry { preInit = 1; };
            class initRopes { preInit = 1; };
            class initConstants { preInit = 1; };
            class initMapTools { preInit = 1; };
            class initRecon { preInit = 1; };
            class initAPS { preInit = 1; };
            class initEasterEgg { preInit = 1; };
            class initVehicleFunctions { preInit = 1; };
        };
        class Modules {
            file = "\Support-Framework\Functions";
            class setHomeBase {
                description = "Function to set the Home Base variables.";
            };
            class setCAS {
                description = "Function to set the CAS variables.";
            };
            class setFixedWings {
                description = "Function to set the FixedWing Recon variables.";
            };
            class setArtillery {
                description = "Function to set the Artillery variables.";
            };
            class setRecon {
                description = "Function to set the Recon variables.";
            };
            class setVirtualStorage {
                description = "Function to set the Virtual Storage variables.";
            };
            class setFabricator {
                description = "Function to set the Fabricator variables.";
            };
            class setCBR {
                description = "Function to set the CBR variables.";
            };
            class setAPS {
                description = "Function to enable the APS on synced objects.";
            };
        };
        class SupportFunctions {
            file = "\Support-Framework\Functions\supportFunctions";
            class addItemsToFabricator {
                description = "Function to add items to the fabricator";
            };
            class baseHeartbeat {
                description = "Function to monitor and manage base status updates";
            };
            class checkPulse {
                description = "Function to reapply waypoint if vehicle gets lost";
            };
            class createTargetActions {
                description = "Function to create artillery target actions";
            };
            class createTargetsFromMarkers {
                description = "Function to create artillery target actions from Markers";
            };
            class createTargetsFromLasers {
                description = "Function to create artillery target actions from Lasers";
            };
            class doFieldRecon {
                description = "Function to perform ad-Hoc recon duties";
            };
            class doRecon {
                description = "Function to perform recon duties";
            };
            class findRendezvousPoint {
                description = "Function to locate a meeting point";
            };
            class getArtyTargetActions {
                description = "Function to get the artillery target actions";
            };
            class getBaseCallsign {
                description = "Function to get the params of the base";
            };
            class getCasActions {
                description = "Function to get the CAS vehicle actions";
            };
            class getEnhancedCombatActions {
                description = "Function to get the Enhanced Combat actions";
            };
            class getLocation {
                description = "Function to get the CAS vehicle actions";
            };
            class getLoiterActions {
                description = "Function to get the Loiter actions";
            };
            class getNearestLocationParams {
                description = "Function to get the params for the function to get nearest location";
            };
            class getNearestLocationText {
                description = "Function to get the text of the nearest location";
            };
            class getPadsNearBase {
                description = "Function to find pads in proximity to the base";
            };
            class getPadsNearTarget {
                description = "Function to find pads close to a target location";
            };
            class getReconActions {
                description = "Function to get the recon vehicle actions";
            };
            class getRedeployActions {
                description = "Function to get the redeploy vehicle actions";
            };
            class getRegisteredVehicles {
                description = "Function to retrieve a list of registered vehicles";
            };
            class getSlimBoundingBox {
                description = "Function to retrieve the 4 or 8 verticies of an object's slimmer bounding box";
            };
            class getSuppliesActions {
                description = "Function to get the actions for supplies";
            };
            class getVicActions {
                description = "Function to get the vehicle actions";
            };
            class hasItems {
                description = "Function to check if items are present";
            };
            class hasLanded {
                description = "Function to check if unit is touching ground and speed is zero";
            };
            class isAtBase {
                description = "Function to determine if at base location";
            };
            class isHeliPad {
                description = "Function to determine object is a helipad";
            };
            class landingAtBase {
                description = "Function to manage landing procedures at base";
            };
            class landingAtObjective {
                description = "Function to manage landing procedures at an objective";
            };
            class loiter {
                description = "Function to loiter the vehicle";
            };
            class onMission {
                description = "Function to check or set mission status";
            };
            class performingCAS {
                description = "Function to manage or check Close Air Support operations";
            };
            class performingRecon {
                description = "Function to manage or check Recon operations";
            };
            class playSideRadio {
                description = "Function to play a radio message to the side";
            };
            class playVehicleRadio {
                description = "Function to play a radio message in the vehicle";
            };
            class posToGrid {
                description = "Function to convert position to grid coordinates";
            };
            class removeVehicleFromAwayPads {
                description = "Function to remove a vehicle from away pads registry";
            };
            class removeVehicleFromPadRegistry {
                description = "Function to deregister a vehicle from pad registry";
            };
            class requestBaseLZ {
                description = "Function to request a landing zone at base";
            };
            class requestCas {
                description = "Function to request close air support";
            };
            class requestFieldRecon {
                description = "Function to request field recon support";
            };
            class requestRecon {
                description = "Function to request recon support";
            };
            class requestReinsert {
                description = "Function to begin redeploy procedures";
            };
            class RTB {
                description = "Function to manage Return To Base procedures";
            };
            class sendSideText {
                description = "Function to handle side channel text communications";
            };
            class setObjectLoadHandling {
                description = "Function to handle object's loading handling";
            };
            class setWaypoint {
                description = "Function to set the waypoint for a given unit.";
            };
            class vehicleChatter {
                description = "Function to handle vehicle channel communications";
            };
            class vehicleWatchdog {
                description = "Function to monitor and manage vehicle status";
            };
            class waveOff {
                description = "Function to manage aborting or redirecting a vehicle/operation";
            };
        }
    };
};

class CfgFactionClasses {
    class NO_CATEGORY;
    class SupportFramework_Category: NO_CATEGORY {
        displayName = "Yoshi's Support Framework"; // Name displayed in Eden Editor
        priority = 2; // Position of the category in the list
        side = 7; // Logic
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


    class SupportFramework_HomeBase_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Home Base Module [REQUIRED]";
        icon = "\Support-Framework\UI\tower.paa"
        function = "YOSHI_fnc_setHomeBase";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;

        //https://community.bistudio.com/wiki/Modules#Creating_the_Module_Config
        canSetArea = 1;						// Allows for setting the area values in the Attributes menu in 3DEN
		canSetAreaShape = 1;				// Allows for setting "Rectangle" or "Ellipse" in Attributes menu in 3DEN
        canSetAreaHeight = 0;

		class AttributeValues
		{
			// This section allows you to set the default values for the attributes menu in 3DEN
			size3[] = { 500, 500, -1 };		// 3D size (x-axis radius, y-axis radius, z-axis radius)
			isRectangle = 0;				// Sets if the default shape should be a rectangle or ellipse
		};

        class Attributes: AttributesBase {
            class Units: Units {};
            class RequiredItems: Edit {
                property = "SupportFramework_HomeBase_Module_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for redeploy. Only one of the items is required to be in the inventory. If empty, the universal terminal, and the module specific terminal (located in the ace Tools section) along with the hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F, YOSHI_UniversalTerminal, YOSHI_ReinsertTerminal"""; 
            };
            class LzPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_LzPrefixes";
                displayName = "Prefixes for landing zone markers";
                tooltip = "Comma-separated list of prefixes that are searched for viable landing zones. Case Insensitive.";
                typeName = "STRING"; 
                defaultValue = """LZ, HLS"""; 
            };
            class LoiterPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_LoiterPrefixes";
                displayName = "Prefixes for loiter zone markers";
                tooltip = "(Applies to CAS too) Comma-separated list of prefixes that the vehicle can be ordered to loiter at. Case Insensitive.";
                typeName = "STRING"; 
                defaultValue = """Loiter, Hold"""; 
            };
            class SideHush: Checkbox {
                property = "SupportFramework_HomeBase_Module_SideHush";
                displayName = "Disable Side Radio Chatter";
                tooltip = "By default, the mod will have radio chatter play in side chat that simulates actually calling in the supports, this allows you to disable all side radio chats (will keep hints)";
                typeName = "BOOLEAN";
                defaultValue = "false"; 
            };
            class VicHush: Checkbox {
                property = "SupportFramework_HomeBase_Module_VicHush";
                displayName = "Disable Vehicle Radio Chatter";
                tooltip = "By default, the mod will have radio chatter play in vehicle chat that simulates pilot/driver communicating with passengers/crew, this allows you to disable vehicle chats";
                typeName = "BOOLEAN";
                defaultValue = "false"; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "Place this module where you want your home base to be.",
                "",
                "Position designates center of search for nearby helicopters and landing pads.",
                "",
                "Any synced helicopters will be automatically registered at the start of the mission.",
                "",
                "Any markers places that begin with the prefixes defined above, will be added to the list of available support locations. Capitilization is ignored. EX: a prefix of 'HLS' will register 'hls Conway' as a valid location",
                "",
                "If you'd like to have a custom callsign for the Base, then sync a single unit (non-vehicle) and it will use that unit's callsign instead. Syncing a player is allowed." 
            };
            sync[] = {"Man", "Helicopter"}; // only able to sync units and helicopters
            position=1;
        };
    };

    // class SupportFramework_AdditionalBase_Module: Module_F {
    //     author = "Yoshi";
    //     category = "SupportFramework_Category";
    //     displayName = "Additional Base Module";
    //     icon = "\Support-Framework\UI\tower.paa"
    //     function = "YOSHI_fnc_setAdditionalBase";
    //     functionPriority = 1; // Execution priority, lower numbers are executed first
    //     scope = 2; // Editor visibility. 2 is for normal use.
    //     isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
    //     isTriggerActivated = 0;
    //     isDisposable = 0;

    //     //https://community.bistudio.com/wiki/Modules#Creating_the_Module_Config
    //     canSetArea = 1;						// Allows for setting the area values in the Attributes menu in 3DEN
	// 	canSetAreaShape = 1;				// Allows for setting "Rectangle" or "Ellipse" in Attributes menu in 3DEN
    //     canSetAreaHeight = 0;

	// 	class AttributeValues
	// 	{
	// 		// This section allows you to set the default values for the attributes menu in 3DEN
	// 		size3[] = { 200, 200, -1 };		// 3D size (x-axis radius, y-axis radius, z-axis radius)
	// 		isRectangle = 0;				// Sets if the default shape should be a rectangle or ellipse
	// 	};

    //     class Attributes: AttributesBase {
    //         class Units: Units {};
    //         class ModuleDescription: ModuleDescription{}; // Module description should be shown last
    //     };
    //     class ModuleDescription: ModuleDescription {
    //         description[] = {
    //             "THIS MODULE REQUIRES Home Base Module TO FUNCTION! -- place down a home base before placing any additional bases",
    //             "",
    //             "Place this module where you want additional bases to be.",
    //             "",
    //             "Don't sync this to any other module",
    //             "",
    //             "Position designates center of search for nearby helicopters and landing pads for the base.",
    //             "",
    //             "Any synced helicopters will be automatically registered at the start of the mission.",
    //             "",
    //             "If you'd like to have a custom callsign for the Base, then sync a single unit (non-vehicle) and it will use that unit's callsign instead. Syncing a player is allowed." 
    //         };
    //         sync[] = {"Man", "Helicopter"}; // only able to sync units and helicopters
    //         position=1;
    //     };
    // };

    class SupportFramework_CAS_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "CAS Module";
        icon = "\Support-Framework\UI\cas.paa"
        function = "YOSHI_fnc_setCAS";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class RequiredItems: Edit {
                property = "SupportFramework_CAS_Module_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for CAS support. Only one of the items is required to be in the inventory. If empty, the universal terminal, and the module specific terminal (located in the ace Tools section) along with the hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F, YOSHI_UniversalTerminal, YOSHI_CASTerminal"""; 
            };
            class CasPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_CasPrefixes";
                displayName = "Prefixes for CAS markers";
                tooltip = "Comma-separated list of prefixes that are searched for CAS missions. Case Insensitive.";
                typeName = "STRING"; 
                defaultValue = """Target, Firemission"""; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use CAS",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced helicopters will be automatically registered as CAS at the start of the mission. No need to sync to the Home Base Module (or any other module)",
                "",
                "Any markers placed that begin with the prefixes defined above, will be added to the list of available support locations. Capitilization is ignored. EX: a prefix of 'Firemission' will register 'firemission Hammer' as a valid location"
            };
            sync[] = {"Helicopter"}; 
        };
    };

    class SupportFramework_Artillery_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Artillery Module";
        icon = "\Support-Framework\UI\artillery.paa"
        function = "YOSHI_fnc_setArtillery";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class BaseSide: Combo {
                property = "SupportFramework_HomeBase_Module_BaseSide";
                displayName = "Base's Side";
                tooltip = "The choices are: west, east, guer, civ -- [BLUFOR, OPFOR, Independent and Civilian, respectively]. Default is west (blufor)";
                typeName = "STRING"; 
                defaultValue = """west"""; 
                // Listbox items
				class Values
				{
					class BluforWest { name = "Blufor (West)";	value = """west"""; };
                    class OpforEast	{ name = "Opfor (East)";	value = """east"""; };
                    class IndepGuer	{ name = "Independent (Guer)";	value = """guer"""; };
                    class CivilCiv	{ name = "Civilian (Civ)";	value = """civ"""; };
				};
            };
            class RequiredItems: Edit {
                property = "SupportFramework_Artillery_Module_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for Artillery support. Only one of the items is required to be in the inventory. If empty, the universal terminal, and the module specific terminal (located in the ace Tools section) along with the hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F, YOSHI_UniversalTerminal, YOSHI_ArtilleryTerminal"""; 
            };
            class ArtilleryPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_ArtilleryPrefixes";
                displayName = "Prefixes for Artillery markers";
                tooltip = "Comma-separated list of prefixes that are searched for Artillery missions. Case Insensitive.";
                typeName = "STRING"; 
                defaultValue = """Target, Firemission"""; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use Artillery",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced units will be automatically registered as Artillery at the start of the mission. No need to sync to the Home Base Module (or any other module)",
                "",
                "Any markers placed that begin with the prefixes defined above, will be added to the list of available support locations. Capitilization is ignored. EX: a prefix of 'Firemission' will register 'firemission Hammer' as a valid location"
            };
            sync[] = {}; 
        };
    };

    class SupportFramework_Recon_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Recon Module";
        icon = "\Support-Framework\UI\recon.paa"
        function = "YOSHI_fnc_setRecon";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class RequiredItems: Edit {
                property = "SupportFramework_Recon_Module_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for Recon support. Only one of the items is required to be in the inventory. If empty, the universal terminal, and the module specific terminal (located in the ace Tools section) along with the hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F, YOSHI_UniversalTerminal, YOSHI_ReconTerminal"""; 
            };
            class ReconPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_ReconPrefixes";
                displayName = "Prefixes for Recon markers";
                tooltip = "Comma-separated list of prefixes that are searched for Recon missions. Case Insensitive.";
                typeName = "STRING"; 
                defaultValue = """Recon, RP, Watch"""; 
            };
            class TaskTime: Edit {
                property = "SupportFramework_Recon_Module_TaskTime";
                displayName = "Time for recon mission";
                tooltip = "Time (in seconds) that the recon unit will loiter in the area. Default is 300 seconds (5 minutes)";
                typeName = "NUMBER"; 
                defaultValue = "300"; 
            };
            class Interval: Edit {
                property = "SupportFramework_Recon_Module_Interval";
                displayName = "Time in between each scan";
                tooltip = "Time (in seconds) between each scan. If hyperspectral sensors are not enabled, then setting something really low like 0 it might take a performance hit!";
                typeName = "NUMBER"; 
                defaultValue = "5"; 
            };
            class ShowNames: Checkbox {
                property = "SupportFramework_Recon_Module_ShowNames";
                displayName = "Show names on markers";
                tooltip = "By default, the markers that the recon mission generates will contain the description of the unit marked (e.g: 'Team Lead', 'Medic', 'Offroad (HMG)', etc) ... disable this to only use dots and no description";
                typeName = "BOOLEAN";
                defaultValue = "false"; 
            };
            // class HasSat: Checkbox {
            //     property = "SupportFramework_Recon_Module_HasSat";
            //     displayName = "Include satellite support";
            //     tooltip = "Enabling this will add a satellite option to the list of actions, this can be considered an immediate recon solution at the mission area.";
            //     typeName = "BOOLEAN";
            //     defaultValue = "false"; 
            // };
            class HasHyperSpectralSensors: Checkbox {
                property = "SupportFramework_Recon_Module_HasHyperSpectralSensors";
                displayName = "Use hyperspectral sensors";
                tooltip = "Enabling this will allow recon units to use the latest and greatest in hyperspectral sensors. (This basically gives units omniscience, i.e: seeing though walls)";
                typeName = "BOOLEAN";
                defaultValue = "false"; 
            };
            
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use Recon",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced units will be automatically registered as Recon at the start of the mission. No need to sync to the Home Base Module (or any other module)",
                "",
                "Any markers placed that begin with the prefixes defined above, will be added to the list of available support locations. Capitilization is ignored. EX: a prefix of 'Recon' will register 'recon Hammer' as a valid location"
            };
            sync[] = {};
        };
    };

    class SupportFramework_Virtual_Storage_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Virtual Storage Module";
        icon = "\Support-Framework\UI\virtualStorage.paa"
        function = "YOSHI_fnc_setVirtualStorage";
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
                "THIS MODULE REQUIRES Home Base Module and Fabricator Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use Virtual Storage",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced items will be available to Fabricators as an option to spawn a copy in. No need to sync to the Home Base Module (or any other module)"
            };
            sync[] = {};
        };
    };

    class SupportFramework_Fabricator_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Fabricator Module";
        icon = "\Support-Framework\UI\fabricator.paa"
        function = "YOSHI_fnc_setFabricator";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class EnableLocalArsenal: Checkbox {
                property = "SupportFramework_Fabricator_Module_EnableLocalArsenal";
                displayName = "Enable local virtual inventory";
                tooltip = "Enabling this will add an action to containers near the fabricator, that will access a virtual inventory -- allowing for easy supply creation without needing to open/close an arsenal (Uses ZEN Inventory)";
                typeName = "BOOLEAN";
                defaultValue = "true"; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module and Virtual Storage Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use Fabricators",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced items will be considered Fabricators, they will have ace interact options to spawn in any items synced with the Virtual Storage Module.", 
                "",
                "No need to sync to the Home Base Module (or any other module)"
            };
            sync[] = {};
        };
    };

    class SupportFramework_CBR_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Counter Battery Radar Module";
        icon = "\Support-Framework\UI\cbr.paa"
        function = "YOSHI_fnc_setCBR";
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
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Place this module to set up the ability to use Counter Battery Radar",
                "",
                "Location of module is meaningless.",
                "",
                "This is a passive module, simply having it placed down will provide intel on artillery fire.",
                "",
                "No need to sync to the Home Base Module (or any other module)"
            };
            sync[] = {};
        };
    };
    class SupportFramework_APS_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Active Protection System Module (APS)";
        icon = "\Support-Framework\UI\aps.paa"
        function = "YOSHI_fnc_setAPS";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 1; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};            
            class ChargeCount: Edit {
                property = "SupportFramework_APS_Module_ChargeCount";
                displayName = "Charge Count";
                tooltip = "Number of incoming targets that the APS can counter. Once the charges are empty, the APS no longer provides protection.";
                typeName = "NUMBER"; 
                defaultValue = "40"; 
            };
            class Range: Edit {
                property = "SupportFramework_APS_Module_Range";
                displayName = "Range";
                tooltip = "Radius in meters for the action range of the APS. Set to -1 to allow an automatic size calculation to be performed (recommended)";
                typeName = "NUMBER"; 
                defaultValue = "-1"; 
            };
            class Interval: Edit {
                property = "SupportFramework_APS_Module_Interval";
                displayName = "Interval";
                tooltip = "Time in seconds that the object checks for incoming targets. Default is 0.05 seconds => 50ms";
                typeName = "NUMBER"; 
                defaultValue = "0.05"; 
            };
            class Cooldown: Edit {
                property = "SupportFramework_APS_Module_Cooldown";
                displayName = "Cooldown";
                tooltip = "Time in seconds that the object waits before targeting another incoming attack. Used for balancing purposes. Default is 0.1 seconds => 100ms";
                typeName = "NUMBER"; 
                defaultValue = "0.1"; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "[Experimental module, use at your own risk]",
                "",
                "Place this module to set up an Active Protection System (APS)",
                "",
                "Location of module is meaningless.",
                "",
                "MULTIPLE MODULES ARE SUPPORTED: If you want different configs for different purposes,",
                "then you can place down multiple APS modules and configure them differently.",
                "All objects synced to the same module will have the same shared config.",
                "",
                "Any synced items will have an APS set up according to the configuration of the module.", 
                "",
                "No need to sync to the Home Base Module (or any other module)"
            };
            sync[] = {};
        };
    };

    class SupportFramework_Base_Arrivals_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Base Arrival Node";
        icon = "\A3\ui_f\data\map\markers\military\end_CA.paa"
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
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Sync this module to a base module to set up the an arrival node for a base.",
                "",
                "Location of module designates the direction that helicopters will take before landing at the base.",
            };
            sync[] = {};
            position=1;
        };
    };

    class SupportFramework_Base_Departure_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Base Departure Node";
        icon = "\A3\ui_f\data\map\markers\military\start_CA.paa"
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
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Sync this module to a base module to set up the a departure node for a base.",
                "",
                "Location of module designates the direction that helicopters will take as they are departing the base.",
            };
            sync[] = {};
            position=1;
        };
    };

    class SupportFramework_Map_Infil_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Map Infil Node";
        icon = "\A3\ui_f\data\map\markers\handdrawn\end_CA.paa"
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
                "THIS MODULE REQUIRES Home Base Module and Map Exfil TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Place this module on the outside edge of the map",
                "",
                "Sync this module to a fixed wing module to set up the infil for that fixed wing module",
                "",
                "Location of module designates the direction that off-map support units will arrive from.",
            };
            sync[] = {};
            position=1;
        };
    };

    class SupportFramework_Map_Exfil_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Map Exfil Node";
        icon = "\A3\ui_f\data\map\markers\handdrawn\start_CA.paa"
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
                "THIS MODULE REQUIRES Home Base Module and Map Infil TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Place this module on the outside edge of the map",
                "",
                "Sync this module to a fixed wing module to set up the exfil for that fixed wing module",
                "",
                "Location of module designates the direction that off-map support units will depart to.",
            };
            sync[] = {};
            position=1;
        };
    };

    class SupportFramework_FixedWing_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Fixed Wing Module";
        icon = "\a3\ui_f\data\igui\cfg\simpletasks\types\Plane_ca.paa"
        function = "YOSHI_fnc_setFixedWings";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class RequiredItems: Edit {
                property = "SupportFramework_FixedWing_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for redeploy. Only one of the items is required to be in the inventory. If empty, the universal terminal, and the module specific terminal (located in the ace Tools section) along with the hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F, YOSHI_UniversalTerminal, YOSHI_FixedWingTerminal"""; 
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "Place this module to set up the ability to use off-map fixed wing units",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced aircraft will be automatically registered and stored in virtual storage the start of the mission. No need to sync to the Home Base Module (or any other module)",
                "Virtual Storage = the vehicle will not appear where it was placed in the editor, but instead will be stored in memory for later use."
            };
            sync[] = {"Helicopter"}; 
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

};

class CfgRadio
{
	sounds[] = {};
	class YOSHI_SectorClear
	{
		name	= "Sector Clear";
		sound[]	= { "\Support-Framework\Sounds\support\sector_clear.ogg", 1, 1 };
		title	= "Sector is Clear";
	};
	class YOSHI_LaunchDetected
	{
		name	= "Launch Detected";
		sound[]	= { "\Support-Framework\Sounds\support\launch_detected.ogg", 1, 1 };
		title	= "Be advised, launch detected";
	};
    class YOSHI_TransportTaskRecieved
	{
		name	= "Transport Requested";
		sound[]	= { "\Support-Framework\Sounds\support\transport_lz_selected.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_TransportRequested
	{
		name	= "Transport Requested";
		sound[]	= { "\Support-Framework\Sounds\support\transport_request.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_TransportAck
	{
		name	= "Transport Acknowledged";
		sound[]	= { "\Support-Framework\Sounds\support\transport_acknowledged.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_TransportComplete
	{
		name	= "Transport Complete";
		sound[]	= { "\Support-Framework\Sounds\support\transport_accomplished.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_TransportLeave
	{
		name	= "Transport Leave";
		sound[]	= { "\Support-Framework\Sounds\support\transport_welcome.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_ArtilleryAck
	{
		name	= "ArtilleryAck";
		sound[]	= { "\Support-Framework\Sounds\support\artillery_acknowledged.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_ArtilleryRoundsComplete
	{
		name	= "ArtilleryRoundsComplete";
		sound[]	= { "\Support-Framework\Sounds\support\artillery_rounds_complete.ogg", 1, 1 };
		title	= "Rounds complete, Out.";
	};
    class YOSHI_CASRequest
	{
		name	= "CASRequest";
		sound[]	= { "\Support-Framework\Sounds\support\cas_heli_request.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_CASAck
	{
		name	= "CASAck";
		sound[]	= { "\Support-Framework\Sounds\support\cas_heli_acknowledged.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_CASDone
	{
		name	= "CASDone";
		sound[]	= { "\Support-Framework\Sounds\support\cas_heli_accomplished.ogg", 1, 1 };
		title	= "";
	};
    class YOSHI_ValkyrieIntro1
	{
		name	= "ValkyrieIntro1";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_intro_airborneinbound.ogg", 1, 1 };
		title	= "Valkyrie is airborne and inbound. Out.";
	};
    class YOSHI_ValkyrieIntro2
	{
		name	= "ValkyrieIntro2";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_intro_omao.ogg", 1, 1 };
		title	= "Acknowledged, Valkyrie is Oscar Mike to the AO. Out.";
	};
    class YOSHI_ValkyrieIntro3
	{
		name	= "ValkyrieIntro3";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_intro_wheelsup.ogg", 1, 1 };
		title	= "This is Valkyrie, wheels are up. Out.";
	};
    class YOSHI_ValkyrieLowFuel1
	{
		name	= "ValkyrieLowFuel1";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_lowfuel_2minstation.ogg", 1, 1 };
		title	= "Valkyrie here, Fuel’s getting low, two minutes left on station. Out.";
	};
    class YOSHI_ValkyrieLowFuel2
	{
		name	= "ValkyrieLowFuel2";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_lowfuel_critical.ogg", 1, 1 };
		title	= "Fuel status critical, Valkyrie’s wrapping up soon. Out.";
	};
    class YOSHI_ValkyrieLowFuel3
	{
		name	= "ValkyrieLowFuel3";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_lowfuel_indicator.ogg", 1, 1 };
		title	= "Valkyrie‘s low fuel indicator is on, two minutes before RTB. Out.";
	};
    class YOSHI_ValkyrieNoFuel1
	{
		name	= "ValkyrieNoFuel1";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_nofuel_bingo.ogg", 1, 1 };
		title	= "Valkyrie is reporting Bingo fuel, breaking off. Out.";
	};
    class YOSHI_ValkyrieNoFuel2
	{
		name	= "ValkyrieNoFuel2";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_nofuel_out.ogg", 1, 1 };
		title	= "Out of fuel, Valkyrie is returning to base. Out.";
	};
    class YOSHI_ValkyrieNoFuel3
	{
		name	= "ValkyrieNoFuel3";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_nofuel_spent.ogg", 1, 1 };
		title	= "Fuel spent, Valkyrie is returning for refuel. Out.";
	};
    class YOSHI_ValkyrieLeave1
	{
		name	= "ValkyrieLeave1";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_leave_ao.ogg", 1, 1 };
		title	= "Solid copy, Valkyrie is leaving the AO. Out.";
	};
    class YOSHI_ValkyrieLeave2
	{
		name	= "ValkyrieLeave2";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_leave_base.ogg", 1, 1 };
		title	= "Valkyrie acknowledges, returning to base. Out.";
	};
    class YOSHI_ValkyrieLeave3
	{
		name	= "ValkyrieLeave3";
		sound[]	= { "\Support-Framework\Sounds\support\Valk_leave_rtb.ogg", 1, 1 };
		title	= "Copy that, Valkyrie is RTB. Out.";
	};
    class YOSHI_AlbatrossIntro1
	{
		name	= "AlbatrossIntro1";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_intro_etasoon.ogg", 1, 1 };
		title	= "Affirmative, Albatross has taken off. ETA soon. Out.";
	};
    class YOSHI_AlbatrossIntro2
	{
		name	= "AlbatrossIntro2";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_intro_roger.ogg", 1, 1 };
		title	= "Roger, Albatross is en route to the AO. Out.";
	};
    class YOSHI_AlbatrossIntro3
	{
		name	= "AlbatrossIntro3";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_intro_understood.ogg", 1, 1 };
		title	= "Understood, Albatross is airborne, en route. Out.";
	};
    class YOSHI_AlbatrossLowFuel1
	{
		name	= "AlbatrossLowFuel1";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_lowfuel_reporting.ogg", 1, 1 };
		title	= "Albatross reporting low fuel, two minutes left on station. Out.";
	};
    class YOSHI_AlbatrossLowFuel2
	{
		name	= "AlbatrossLowFuel2";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_lowfuel_bingo.ogg", 1, 1 };
		title	= "Approaching bingo, Albatross is wrapping up the mission. Out.";
	};
    class YOSHI_AlbatrossLowFuel3
	{
		name	= "AlbatrossLowFuel3";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_lowfuel_rtb.ogg", 1, 1 };
		title	= "Albatross has two minutes left, then RTB. Out.";
	};
    class YOSHI_AlbatrossNoFuel1
	{
		name	= "AlbatrossNoFuel1";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_nofuel_bingo.ogg", 1, 1 };
		title	= "Albatross reports bingo fuel, returning to base. Out.";
	};
    class YOSHI_AlbatrossNoFuel2
	{
		name	= "AlbatrossNoFuel2";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_nofuel_zerofuel.ogg", 1, 1 };
		title	= "Fuel's dry, Albatross is disengaging. Out.";
	};
    class YOSHI_AlbatrossLeave1
	{
		name	= "AlbatrossLeave1";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_leave_copy.ogg", 1, 1 };
		title	= "Copy, Albatross is exiting AO. Out.";
	};
    class YOSHI_AlbatrossLeave2
	{
		name	= "AlbatrossLeave2";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_leave_roger.ogg", 1, 1 };
		title	= "Roger, Albatross is returning to base. Out.";
	};
    class YOSHI_AlbatrossLeave3
	{
		name	= "AlbatrossLeave3";
		sound[]	= { "\Support-Framework\Sounds\support\Alba_leave_orderrecieved.ogg", 1, 1 };
		title	= "Order received, Albatross is pulling out. Out.";
	};
};

class CfgSounds {
    sounds[] = {};

    class RideOfValkyries {
        name = "rideOfValkyries";
        sound[] = {"\Support-Framework\Sounds\easterEgg\ride_of_the_valk.ogg", 1, 1};
        titles[] = {};
    };
    class FortunateSon {
        name = "fortunateSon";
        sound[] = {"\Support-Framework\Sounds\easterEgg\fourtunate_son.ogg", 1, 1};
        titles[] = {};
    };
    class ApsHit {
        name = "apsHit";
        sound[] = {"\Support-Framework\Sounds\apsHit.ogg", 1, 1};
        titles[] = {};
    };
    class ApsDrone {
        name = "apsDrone";
        sound[] = {"\Support-Framework\Sounds\apsDrone.ogg", 1, 1};
        titles[] = {};
    };
    class DufflebagShuffle {
        name = "dufflebagShuffle";
        sound[] = {"\Support-Framework\Sounds\dufflebagShuffle.ogg", 1, 1};
        titles[] = {};
    };
    class CautionCaution {
        name = "CautionCaution";
        sound[] = {"\Support-Framework\Sounds\warnAlert.ogg", 1, 1};
        titles[] = {};
    };
    class WarningWarning {
        name = "WarningWarning";
        sound[] = {"\Support-Framework\Sounds\sirenWarning.ogg", 1, 1};
        titles[] = {};
    };
    class IncomingKlaxon {
        name = "IncomingKlaxon";
        sound[] = {"\Support-Framework\Sounds\alarmDanger.ogg", 1, 1};
        titles[] = {};
    };
    class launchDetected {
        name = "launchDetected";
        sound[] = {"\Support-Framework\Sounds\launchDetected.ogg", 1, 1};
        titles[] = {};
    };
    class sectorClear {
        name = "sectorClear";
        sound[] = {"\Support-Framework\Sounds\sectorClear.ogg", 1, 1};
        titles[] = {};
    };
    class beepIdle {
        name = "beepIdle";
        sound[] = {"\Support-Framework\Sounds\beepIdle.ogg", 1, 1};
        titles[] = {};
    };
    class turnOn {
        name = "turnOn";
        sound[] = {"\Support-Framework\Sounds\turnOn.ogg", 1, 1};
        titles[] = {};
    };
    class turnOff {
        name = "turnOff";
        sound[] = {"\Support-Framework\Sounds\turnOff.ogg", 1, 1};
        titles[] = {};
    };
    class sector {
        name = "sector";
        sound[] = {"\Support-Framework\Sounds\sector.ogg", 1, 1};
        titles[] = {};
    };
    class clear {
        name = "clear";
        sound[] = {"\Support-Framework\Sounds\clear.ogg", 1, 1};
        titles[] = {};
    };
    class targets {
        name = "targets";
        sound[] = {"\Support-Framework\Sounds\targets.ogg", 1, 1};
        titles[] = {};
    };
    class detected {
        name = "detected";
        sound[] = {"\Support-Framework\Sounds\detected.ogg", 1, 1};
        titles[] = {};
    };
    class activatingInstantKill {
        name = "activatingInstantKill";
        sound[] = {"\Support-Framework\Sounds\easterEgg\activateInstantKill.ogg", 1, 1};
        titles[] = {};
    };
    class deactivatingInstantKill {
        name = "deactivatingInstantKill";
        sound[] = {"\Support-Framework\Sounds\easterEgg\deactivateInstantKill.ogg", 1, 1};
        titles[] = {};
    };

    class droneScan {
        name = "droneScan";
        sound[] = {"\Support-Framework\Sounds\recon\droneScan.ogg", 1, 1};
        titles[] = {};
    };

    class one {
        name = "one";
        sound[] = {"\Support-Framework\Sounds\numbers\one.ogg", 1, 1};
        titles[] = {};
    };

    class two {
        name = "two";
        sound[] = {"\Support-Framework\Sounds\numbers\two.ogg", 1, 1};
        titles[] = {};
    };

    class three {
        name = "three";
        sound[] = {"\Support-Framework\Sounds\numbers\three.ogg", 1, 1};
        titles[] = {};
    };

    class four {
        name = "four";
        sound[] = {"\Support-Framework\Sounds\numbers\four.ogg", 1, 1};
        titles[] = {};
    };

    class five {
        name = "five";
        sound[] = {"\Support-Framework\Sounds\numbers\five.ogg", 1, 1};
        titles[] = {};
    };

    class six {
        name = "six";
        sound[] = {"\Support-Framework\Sounds\numbers\six.ogg", 1, 1};
        titles[] = {};
    };

    class seven {
        name = "seven";
        sound[] = {"\Support-Framework\Sounds\numbers\seven.ogg", 1, 1};
        titles[] = {};
    };

    class eight {
        name = "eight";
        sound[] = {"\Support-Framework\Sounds\numbers\eight.ogg", 1, 1};
        titles[] = {};
    };

    class nine {
        name = "nine";
        sound[] = {"\Support-Framework\Sounds\numbers\nine.ogg", 1, 1};
        titles[] = {};
    };

    class eleven {
        name = "eleven";
        sound[] = {"\Support-Framework\Sounds\numbers\eleven.ogg", 1, 1};
        titles[] = {};
    };

    class twelve {
        name = "twelve";
        sound[] = {"\Support-Framework\Sounds\numbers\twelve.ogg", 1, 1};
        titles[] = {};
    };

    class thirteen {
        name = "thirteen";
        sound[] = {"\Support-Framework\Sounds\numbers\thirteen.ogg", 1, 1};
        titles[] = {};
    };

    class fourteen {
        name = "fourteen";
        sound[] = {"\Support-Framework\Sounds\numbers\fourteen.ogg", 1, 1};
        titles[] = {};
    };

    class fifteen {
        name = "fifteen";
        sound[] = {"\Support-Framework\Sounds\numbers\fifteen.ogg", 1, 1};
        titles[] = {};
    };

    class sixteen {
        name = "sixteen";
        sound[] = {"\Support-Framework\Sounds\numbers\sixteen.ogg", 1, 1};
        titles[] = {};
    };

    class seventeen {
        name = "seventeen";
        sound[] = {"\Support-Framework\Sounds\numbers\seventeen.ogg", 1, 1};
        titles[] = {};
    };

    class eighteen {
        name = "eighteen";
        sound[] = {"\Support-Framework\Sounds\numbers\eighteen.ogg", 1, 1};
        titles[] = {};
    };

    class nineteen {
        name = "nineteen";
        sound[] = {"\Support-Framework\Sounds\numbers\nineteen.ogg", 1, 1};
        titles[] = {};
    };

    class ten {
        name = "ten";
        sound[] = {"\Support-Framework\Sounds\numbers\ten.ogg", 1, 1};
        titles[] = {};
    };

    class twenty {
        name = "twenty";
        sound[] = {"\Support-Framework\Sounds\numbers\twenty.ogg", 1, 1};
        titles[] = {};
    };

    class thirty {
        name = "thirty";
        sound[] = {"\Support-Framework\Sounds\numbers\thirty.ogg", 1, 1};
        titles[] = {};
    };

    class fourty {
        name = "fourty";
        sound[] = {"\Support-Framework\Sounds\numbers\fourty.ogg", 1, 1};
        titles[] = {};
    };

    class fifty {
        name = "fifty";
        sound[] = {"\Support-Framework\Sounds\numbers\fifty.ogg", 1, 1};
        titles[] = {};
    };

    class sixty {
        name = "sixty";
        sound[] = {"\Support-Framework\Sounds\numbers\sixty.ogg", 1, 1};
        titles[] = {};
    };

    class seventy {
        name = "seventy";
        sound[] = {"\Support-Framework\Sounds\numbers\seventy.ogg", 1, 1};
        titles[] = {};
    };

    class eighty {
        name = "eighty";
        sound[] = {"\Support-Framework\Sounds\numbers\eighty.ogg", 1, 1};
        titles[] = {};
    };

    class ninety {
        name = "ninety";
        sound[] = {"\Support-Framework\Sounds\numbers\ninety.ogg", 1, 1};
        titles[] = {};
    };

    class hundred {
        name = "hundred";
        sound[] = {"\Support-Framework\Sounds\numbers\hundred.ogg", 1, 1};
        titles[] = {};
    };

    class thousand {
        name = "thousand";
        sound[] = {"\Support-Framework\Sounds\numbers\thousand.ogg", 1, 1};
        titles[] = {};
    };

    class million {
        name = "million";
        sound[] = {"\Support-Framework\Sounds\numbers\million.ogg", 1, 1};
        titles[] = {};
    };

};

class CfgWeapons {
    class ACE_ItemCore;
	class CBA_MiscItem_ItemInfo;
	class YOSHI_Terminal: ACE_ItemCore
	{
		author="$STR_ace_common_ACETeam";
		scope=2;
        scopeArsenal=2;
		displayName="$STR_ace_microdagr_itemName";
		model="\A3\Weapons_F\DummyItemHorizontal.p3d";
		// picture="\z\ace\addons\microdagr\images\microDAGR_item.paa";
		ACE_isTool=1;
		class ItemInfo: CBA_MiscItem_ItemInfo
		{
			mass=1;
		};
	};
    class YOSHI_ReinsertTerminal: YOSHI_Terminal
	{
		displayName="(YSF) Reinsert Terminal";
        _generalMacro="YOSHI_ReinsertTerminal";
	};
    class YOSHI_CASTerminal: YOSHI_Terminal
	{
		displayName="(YSF) CAS Terminal";
        _generalMacro="YOSHI_CASTerminal";
	};
    class YOSHI_ArtilleryTerminal: YOSHI_Terminal
	{
		displayName="(YSF) Artillery Terminal";
        _generalMacro="YOSHI_ArtilleryTerminal";
	};
    class YOSHI_ReconTerminal: YOSHI_Terminal
	{
		displayName="(YSF) Recon Terminal";
        _generalMacro="YOSHI_ReconTerminal";
	};
    class YOSHI_UniversalTerminal: YOSHI_Terminal
	{
		displayName="(YSF) Universal Terminal";
        _generalMacro="YOSHI_UniversalTerminal";
	};
};


// class Mode_SemiAuto;
// class MuzzleSlot;
// class PointerSlot;
// class ESD_PointerSlot: PointerSlot
// {
// 	class compatibleItems
// 	{
// 		acc_esd_01_flashlight=1;
// 	};
// };
// class CfgWeapons
// {
// 	class Pistol;
// 	class Pistol_Base_F: Pistol
// 	{
// 		class WeaponSlotsInfo;
// 	};
// 	class hgun_esd_01_base_F: Pistol_Base_F
// 	{
// 		scope=1;
// 		DLC="Enoch";
// 		inertia=1;
// 		reloadAction="";
// 		weaponInfoType="RscWeaponSpectrumAnalyzerGeneric";
// 		magazines[]={};
// 		picture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\gear_ESD_01_CA.paa";
// 		class Library
// 		{
// 			libTextDesc="A device used to send and recieve EM signals";
// 		};
// 		modes[]=
// 		{
// 			"Single"
// 		};
// 		class Single: Mode_SemiAuto
// 		{
// 			sounds[]={};
// 			minRange=1;
// 			minRangeProbab=0.0099999998;
// 			midRange=2;
// 			midRangeProbab=0.0099999998;
// 			maxRange=3;
// 			maxRangeProbab=0.0099999998;
// 		};
// 		muzzles[]=
// 		{
// 			"this",
// 			"Muzzle_1",
// 			"Muzzle_2",
// 			"Muzzle_3",
// 			"Muzzle_4",
// 			"Muzzle_5",
// 			"Muzzle_6",
// 			"Muzzle_7",
// 			"Muzzle_8",
// 			"Muzzle_9",
// 			"Muzzle_10"
// 		};
// 		class Muzzle_base: Pistol_Base_F
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_1"
// 			};
// 			showToPlayer=0;
// 		};
// 		class Muzzle_1: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_1"
// 			};
// 		};
// 		class Muzzle_2: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_2"
// 			};
// 		};
// 		class Muzzle_3: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_3"
// 			};
// 		};
// 		class Muzzle_4: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_4"
// 			};
// 		};
// 		class Muzzle_5: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_5"
// 			};
// 		};
// 		class Muzzle_6: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_6"
// 			};
// 		};
// 		class Muzzle_7: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_7"
// 			};
// 		};
// 		class Muzzle_8: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_8"
// 			};
// 		};
// 		class Muzzle_9: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_9"
// 			};
// 		};
// 		class Muzzle_10: Muzzle_base
// 		{
// 			magazines[]=
// 			{
// 				"ESD_01_DummyMagazine_10"
// 			};
// 		};
// 		discreteDistance[]={0,1,2,3,4,5,6,7,8,9,10};
// 		discreteDistanceInitIndex=5;
// 		cursor="esd";
// 		class WeaponSlotsInfo
// 		{
// 			mass=5;
// 			holsterScale=0;
// 			class MuzzleSlot
// 			{
// 				iconPosition[]={0.30000001,0.55000001};
// 				iconScale=0.75;
// 				iconPicture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\hgun_esd_01_antenna_01_F_ca.paa";
// 				iconPinpoint="Center";
// 				linkProxy="\A3\data_f\proxies\weapon_slots\MUZZLE";
// 				compatibleItems[]=
// 				{
// 					"muzzle_antenna_test_01",
// 					"muzzle_antenna_01_f"
// 				};
// 			};
// 			class MuzzleSlot2: MuzzleSlot
// 			{
// 				iconPosition[]={0.40000001,0.55000001};
// 				iconPicture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\hgun_esd_01_antenna_02_F_ca.paa";
// 				compatibleItems[]=
// 				{
// 					"muzzle_antenna_02_f"
// 				};
// 			};
// 			class MuzzleSlot3: MuzzleSlot
// 			{
// 				iconPosition[]={0.1,0.55000001};
// 				iconPicture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\hgun_esd_01_antenna_03_F_ca.paa";
// 				compatibleItems[]=
// 				{
// 					"muzzle_antenna_03_f"
// 				};
// 			};
// 			class PointerSlot: ESD_PointerSlot
// 			{
// 				iconPicture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\hgun_esd_01_flashlight_01_F_ca.paa";
// 				iconPinpoint="Center";
// 				iconPosition[]={0.64999998,0.73000002};
// 				iconScale=0.25;
// 			};
// 		};
// 	};
// 	class ysf_hgun_esd_01_F: hgun_esd_01_base_F
// 	{
// 		author="$STR_A3_Bohemia_Interactive";
// 		_generalMacro="ysf_hgun_esd_01_F";
// 		scope=2;
// 		displayName="Yoshi's Spectrum Device";
// 		model="\a3\Weapons_F_Enoch\Pistols\ESD_01\ESD_01_F";
// 		baseWeapon="ysf_hgun_esd_01_F";
// 	};
// 	class ysf_hgun_esd_01_dummy_F: ysf_hgun_esd_01_F
// 	{
// 		author="$STR_A3_Bohemia_Interactive";
// 		_generalMacro="ysf_hgun_esd_01_dummy_F";
// 		weaponInfoType="RscWeaponZeroing";
// 	};
// 	class ysf_hgun_esd_01_antenna_01_F: ysf_hgun_esd_01_F
// 	{
// 		class LinkedItems
// 		{
// 			class LinkedItemsMuzzle
// 			{
// 				slot="MuzzleSlot";
// 				item="muzzle_antenna_01_f";
// 			};
// 			class LinkedItemsFlashlight
// 			{
// 				slot="PointerSlot";
// 				item="acc_esd_01_flashlight";
// 			};
// 		};
// 	};
// 	class ysf_hgun_esd_01_antenna_02_F: ysf_hgun_esd_01_F
// 	{
// 		class LinkedItems
// 		{
// 			class LinkedItemsMuzzle
// 			{
// 				slot="MuzzleSlot";
// 				item="muzzle_antenna_02_f";
// 			};
// 			class LinkedItemsFlashlight
// 			{
// 				slot="PointerSlot";
// 				item="acc_esd_01_flashlight";
// 			};
// 		};
// 	};
// 	class ysf_hgun_esd_01_antenna_03_F: ysf_hgun_esd_01_F
// 	{
// 		class LinkedItems
// 		{
// 			class LinkedItemsMuzzle
// 			{
// 				slot="MuzzleSlot";
// 				item="muzzle_antenna_03_f";
// 			};
// 			class LinkedItemsFlashlight
// 			{
// 				slot="PointerSlot";
// 				item="acc_esd_01_flashlight";
// 			};
// 		};
// 	};
// 	class ItemCore;
// 	class InventoryMuzzleItem_Base_F;
// 	class muzzle_antenna_base_01_F: ItemCore
// 	{
// 		DLC="Enoch";
// 		class ItemInfo: InventoryMuzzleItem_Base_F
// 		{
// 			mass=6;
// 			muzzlePos="usti hlavne";
// 			muzzleEnd="konec hlavne";
// 			alternativeFire="";
// 		};
// 	};
// 	class muzzle_antenna_test_01: muzzle_antenna_base_01_F
// 	{
// 		displayName="Antenna Test 01";
// 		scope=1;
// 		model="\a3\Weapons_F_Enoch\Pistols\ESD_01\muzzle_antenna_01_F";
// 		class EM
// 		{
// 			antenna="Test_Directional";
// 		};
// 	};
// 	class muzzle_antenna_01_f: muzzle_antenna_base_01_F
// 	{
// 		author="$STR_A3_Bohemia_Interactive";
// 		_generalMacro="muzzle_antenna_01_f";
// 		scope=2;
// 		displayName="Antenna (Low Hz Frequency)";
// 		picture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\gear_muzzle_antenna_01_ca.paa";
// 		model="\a3\Weapons_F_Enoch\Pistols\ESD_01\muzzle_antenna_01_F";
// 		class EM
// 		{
// 			antenna="Antenna_01";
// 		};
// 	};
// 	class muzzle_antenna_02_f: muzzle_antenna_base_01_F
// 	{
// 		author="$STR_A3_Bohemia_Interactive";
// 		_generalMacro="muzzle_antenna_02_f";
// 		scope=2;
// 		displayName="Antenna (Medium MHz Frequency)";
// 		picture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\gear_muzzle_antenna_02_ca.paa";
// 		model="\a3\Weapons_F_Enoch\Pistols\ESD_01\muzzle_antenna_02_F";
// 		class EM
// 		{
// 			antenna="Antenna_02";
// 		};
// 	};
// 	class muzzle_antenna_03_f: muzzle_antenna_base_01_F
// 	{
// 		author="$STR_A3_Bohemia_Interactive";
// 		_generalMacro="muzzle_antenna_03_f";
// 		scope=2;
// 		displayName="Antenna (High GHz Frequency)";
// 		picture="\a3\Weapons_F_Enoch\Pistols\ESD_01\data\ui\gear_muzzle_antenna_03_ca.paa";
// 		model="\a3\Weapons_F_Enoch\Pistols\ESD_01\muzzle_antenna_03_F";
// 		class EM
// 		{
// 			antenna="Antenna_03";
// 		};
// 	};
// };