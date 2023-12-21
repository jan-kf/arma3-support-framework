class CfgPatches {
    class RedeploymentSystem {
        units[] = {};
        weapons[] = {};
        requiredVersion = 1.0;
        requiredAddons[] = {"ace_main"};
        author = "Yoshi";
        authorUrl = "https://github.com/jan-kf/arma3-redeploy-framework";
    };
};

class CfgFunctions {
    class RedeploymentSystem {
        class Server {
            file = "\Redeployment-System\Functions\Server";
            class initServer { postInit = 1; }; 
        };
        class Client {
            file = "\Redeployment-System\Functions\Client";
            class initPlayerLocal { postInit = 1; };
        };
        class Modules {
            file = "\Redeployment-System\Functions";
            class setHomeBase {
                description = "Function to set the home base variables.";
            };
        };
    };
};

class CfgFactionClasses {
    class NO_CATEGORY;
    class RedeploymentSystem_Category: NO_CATEGORY {
        displayName = "Yoshi's Redeployment System"; // Name displayed in Eden Editor
        priority = 2; // Position of the category in the list
        side = 7; // Logic
    };
};


class CfgVehicles {
    class Logic;
    class Module_F: Logic {
        class ArgumentsBaseUnits;
        class ModuleDescription;
    };

    class RedeploymentSystem_HomeBase_Module: Module_F {
        author = "Yoshi";
        category = "RedeploymentSystem_Category";
        displayName = "Home Base Module";
        icon = "\Redeployment-System\UI\watchtower.paa"
        function = "RedeploymentSystem_fnc_setHomeBase";
        functionPriority = 1; // Execution priority, lower numbers are executed first
        scope = 2; // Editor visibility. 2 is for normal use.
        isGlobal = 0; // Effect is local (0 for local only, 1 for global, 2 for persistent)
        isTriggerActivated = 0;
        isDisposable = 0;
        class ModuleDescription: ModuleDescription {
            description[] = {
                "Place this module where you want your home base to be.",
                "Position designates center of search for nearby helicopters and landing pads.",
                "Any synced helicopters will be automatically registered at the start of the mission.",
                "If you'd like to have a custom callsign for the Base, then sync a single unit (non-vehicle) and it will use that unit's callsign instead." 
            };
            sync[] = {"Man", "Helicopter"}; // only able to sync units and helicopters
        };
    };
};