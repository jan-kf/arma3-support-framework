class CfgPatches {
    class YCD_CORDIS {
        name = "C.O.R.D.I.S.";
        units[] = {};
        weapons[] = {};
        requiredVersion = 2.20;
        requiredAddons[] = {"cba_main"};
        version = "1.0";
        author = "Yoshi";
    };
};

class CfgFunctions {
    class YCD {
        tag = "YCD";

        class Client {
            file = "\CORDIS\functions\client";
            class initPlayerLocal { postInit = 1; };
        };

        class Global {
            file = "\CORDIS\functions\global";
            class core { preInit = 1; };
            class initSettings { preInit = 1; };
            class utils { preInit = 1; };
        };

        class Server {
            file = "\CORDIS\functions\server";
            class initServer { postInit = 1; };
        };
    };
};
