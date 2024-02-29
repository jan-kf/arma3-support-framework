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
                description = "Function to set the home base variables.";
            };
        };
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
        };
        class ModuleDescription;
    };

    class SupportFramework_HomeBase_Module: Module_F {
        author = "Yoshi";
        category = "SupportFramework_Category";
        displayName = "Home Base Module";
        icon = "\Support-Framework\UI\watchtower.paa"
        function = "SupportFramework_fnc_setHomeBase";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class Attributes: AttributesBase {
            class Units: Units {};
            class BaseSide: Edit {
                property = "SupportFramework_HomeBase_Module_BaseSide";
                displayName = "Base's Side";
                tooltip = "The choices are: west, east, guer, civ -- [BLUFOR, OPFOR, Independent and Civilian, respectively], only choose one. Default is west (blufor)";
                typeName = "STRING"; // Value type
                defaultValue = """west"""; // Default value
            };
            class RequiredItems: Edit {
                property = "SupportFramework_HomeBase_Module_RequiredItems";
                displayName = "Required item to call in support(s)";
                tooltip = "Comma-separated list of item classes required for redeploy. If empty, hgun_esd_01_F (spectrum device) will be used. Separate items for different supports (redeployment, CAS, artillery, etc.) is a planned feature in the future";
                typeName = "STRING"; // Value type
                defaultValue = """hgun_esd_01_F"""; // Default value
            };
            class Radius: Edit {
                property = "SupportFramework_HomeBase_Module_Radius";
                displayName = "Home Base's Area of Influence";
                tooltip = "Radius in meters that defines where the home base is, calculated from the module itself. (500m if empty)";
                typeName = "NUMBER";
                defaultValue = "500"; // Default radius value in meters
            };
            class LzPrefixes: Edit {
                property = "SupportFramework_HomeBase_Module_LzPrefixes";
                displayName = "Prefixes for landing zone markers";
                tooltip = "Comma-separated list of prefixes that are searched for viable landing zones. Case Insensitive.";
                typeName = "STRING"; // Value type
                defaultValue = """LZ, HLS"""; // Default value
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
};