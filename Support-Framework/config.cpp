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
    class YOSHI {
        class Server {
            file = "\Support-Framework\Functions\Server";
            class initServer { postInit = 1; }; 
        };
        class Client {
            file = "\Support-Framework\Functions\Client";
            class initPlayerLocal { postInit = 1; };
        };
        class Prelude {
            file = "\Support-Framework\Functions\Prelude";
            class initCore { preInit = 1; };
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
            class getVicActions {
                description = "Function to get the vehicle actions";
            };
            class hasItems {
                description = "Function to check if items are present";
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
            class sideChatter {
                description = "Function to handle side channel communications";
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
                tooltip = "Comma-separated list of item classes required for redeploy. If empty, hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F"""; 
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
                tooltip = "Comma-separated list of item classes required for CAS support. If empty, hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F"""; 
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
                defaultValue = "west"; 
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
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F"""; 
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
                tooltip = "Comma-separated list of item classes required for Recon support. If empty, hgun_esd_01_F (spectrum device) will be used.";
                typeName = "STRING"; 
                defaultValue = """hgun_esd_01_F"""; 
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
                defaultValue = "true"; 
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
                "[Experimental module, use at your own risk]",
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
                "[Experimental module, use at your own risk]",
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
            class ModuleDescription: ModuleDescription{}; // Module description should be shown last
        };
        class ModuleDescription: ModuleDescription {
            description[] = {
                "THIS MODULE REQUIRES Home Base Module and Virtual Storage Module TO FUNCTION!",
                "",
                "[Experimental module, use at your own risk]",
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
            class DetectionRange: Edit {
                property = "SupportFramework_CBR_Module_DetectionRange";
                displayName = "Detection Range";
                tooltip = "Radius in meters for the overall detection range of the radar, will beep when projectile is detected";
                typeName = "NUMBER"; 
                defaultValue = "5000"; 
            };
            class CautionRange: Edit {
                property = "SupportFramework_CBR_Module_CautionRange";
                displayName = "Caution Range";
                tooltip = "Radius in meters when the CAUTION alarm will sound (set to 0 to disable)";
                typeName = "NUMBER"; 
                defaultValue = "1000"; 
            };
            class WarningRange: Edit {
                property = "SupportFramework_CBR_Module_WarningRange";
                displayName = "Warning Range";
                tooltip = "Radius in meters when the WARNING alarm will sound (set to 0 to disable)";
                typeName = "NUMBER"; 
                defaultValue = "500"; 
            };
            class IncomingRange: Edit {
                property = "SupportFramework_CBR_Module_IncomingRange";
                displayName = "Incoming Range";
                tooltip = "Radius in meters when the Incoming alarm will sound (set to 0 to disable)";
                typeName = "NUMBER"; 
                defaultValue = "200"; 
            };
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
                "Any synced items will be considered CBR(s), they will have ace interact options to enable/disable their radar", 
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
        isGlobal = 2; // Effect is local (0 for local only, 1 for global, 2 for persistent)
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
};

class CfgSounds {
    sounds[] = {};

    class ApsHit {
        name = "apsHit";
        sound[] = {"\Support-Framework\Sounds\apsHit.ogg", 1, 1};
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
