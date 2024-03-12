class CfgPatches {
    class SupportFramework {
        units[] = {};
        weapons[] = {};
        requiredVersion = 1.0;
        requiredAddons[] = {"ace_main"};
        author = "Yoshi";
        authorUrl = "https://github.com/jan-kf/arma3-support-framework";
    };
};

class CfgFunctions {
    class SupportFramework {
        class Server {
            file = "\Support-Framework\Functions\Server";
            class initServer { postInit = 1; }; 
        };
        class Client {
            file = "\Support-Framework\Functions\Client";
            class initPlayerLocal { postInit = 1; };
        };
        class Modules {
            file = "\Support-Framework\Functions";
            class setHomeBase {
                description = "Function to set the Home Base variables.";
            };
            class setCAS {
                description = "Function to set the CAS variables.";
            };
            class setArtillery {
                description = "Function to set the Artillery variables.";
            };
        };
        class SupportFunctions {
            file = "\Support-Framework\Functions\supportFunctions";
            class baseHeartbeat {
                description = "Function to monitor and manage base status updates";
            };
            class findRendezvousPoint {
                description = "Function to locate a meeting point";
            };
            class getArtyTargetActions {
                description = "Function to get the artillery target actions";
            };
            class getCasActions {
                description = "Function to get the CAS vehicle actions";
            };
            class getPadsNearBase {
                description = "Function to find pads in proximity to the base";
            };
            class getPadsNearTarget {
                description = "Function to find pads close to a target location";
            };
            class getRedeployActions {
                description = "Function to get the redeploy vehicle actions";
            };
            class getRegisteredVehicles {
                description = "Function to retrieve a list of registered vehicles";
            };
            class getVicActions {
                description = "Function to get the vehicle actions";
            };
            class hasItems {
                description = "Function to check if items are present";
            };
            class isAtBase {
                description = "Function to determine if at base location";
            };
            class landingAtBase {
                description = "Function to manage landing procedures at base";
            };
            class landingAtObjective {
                description = "Function to manage landing procedures at an objective";
            };
            class onMission {
                description = "Function to check or set mission status";
            };
            class performingCAS {
                description = "Function to manage or check Close Air Support operations";
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
            class requestReinsert {
                description = "Function to begin redeploy procedures";
            };
            class RTB {
                description = "Function to manage Return To Base procedures";
            };
            class sideChatter {
                description = "Function to handle side channel communications";
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
        function = "SupportFramework_fnc_setHomeBase";
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
                tooltip = "Comma-separated list of item classes required for redeploy. If empty, hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; // Value type
                defaultValue = """hgun_esd_01_F"""; // Default value
            };
            class LzPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_LzPrefixes";
                displayName = "Prefixes for landing zone markers";
                tooltip = "Comma-separated list of prefixes that are searched for viable landing zones. Case Insensitive.";
                typeName = "STRING"; // Value type
                defaultValue = """LZ, HLS"""; // Default value
            };
            class Hush: Checkbox {
                property = "SupportFramework_HomeBase_Module_Hush";
                displayName = "Disable Radio Chatter";
                tooltip = "By default, the mod will have radio chatter play in side chat that simulates actually calling in the supports, this allows you to disable all chats (will keep hints)";
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

    class SupportFramework_CAS_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "CAS Module";
        icon = "\Support-Framework\UI\cas.paa"
        function = "SupportFramework_fnc_setCAS";
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
                tooltip = "Comma-separated list of item classes required for CAS support. If empty, hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; // Value type
                defaultValue = """hgun_esd_01_F"""; // Default value
            };
            class CasPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_CasPrefixes";
                displayName = "Prefixes for CAS markers";
                tooltip = "Comma-separated list of prefixes that are searched for CAS missions. Case Insensitive.";
                typeName = "STRING"; // Value type
                defaultValue = """Target, Firemission"""; // Default value
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Place this module to set up the ability to use CAS",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced helicopters will be automatically registered as CAS at the start of the mission. No need to sync to the Home Base Module (or any other module)",
                "",
                "Any markers placed that begin with the prefixes defined above, will be added to the list of available support locations. Capitilization is ignored. EX: a prefix of 'Firemission' will register 'firemission Hammer' as a valid location"
            };
            sync[] = {"Helicopter"}; // only able to sync units and helicopters
        };
    };

    class SupportFramework_Artillery_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Artillery Module";
        icon = "\Support-Framework\UI\artillery.paa"
        function = "SupportFramework_fnc_setArtillery";
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
                typeName = "STRING"; // Value type
                defaultValue = "west"; // Default value
                // Listbox items
				class Values
				{
					class BluforWest { name = "Blufor (West)";	value = "west"; };
                    class OpforEast	{ name = "Opfor (East)";	value = "east"; };
                    class IndepGuer	{ name = "Independent (Guer)";	value = "guer"; };
                    class CivilCiv	{ name = "Civilian (Civ)";	value = "civ"; };
				};
            };
            class RequiredItems: Edit {
                property = "SupportFramework_Artillery_Module_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for Artillery support. If empty, hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; // Value type
                defaultValue = """hgun_esd_01_F"""; // Default value
            };
            class ArtilleryPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_ArtilleryPrefixes";
                displayName = "Prefixes for Artillery markers";
                tooltip = "Comma-separated list of prefixes that are searched for Artillery missions. Case Insensitive.";
                typeName = "STRING"; // Value type
                defaultValue = """Target, Firemission"""; // Default value
            };
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
                "",
                "Place this module to set up the ability to use Artillery",
                "",
                "Location of module is meaningless.",
                "",
                "Any synced units will be automatically registered as Artillery at the start of the mission. No need to sync to the Home Base Module (or any other module)",
                "",
                "Any markers placed that begin with the prefixes defined above, will be added to the list of available support locations. Capitilization is ignored. EX: a prefix of 'Firemission' will register 'firemission Hammer' as a valid location"
            };
            sync[] = {"Helicopter"}; // only able to sync units and helicopters
        };
    };
};