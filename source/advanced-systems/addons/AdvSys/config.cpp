class CfgPatches {
    class YAS_AdvSys {
        name = "YAS Advanced Systems";
        units[] = {
            "YAS_CBR_Module",
            "YAS_CBR_Zeus_Toggle_Module",
            "YAS_APS_Module",
            "YAS_APS_Zeus_Toggle_Module",
            "YAS_OPHANIM_box"
        };
        weapons[] = {};
        requiredVersion = 2.20;
        requiredAddons[] = {"cba_main", "YCD_CORDIS", "ace_interact_menu", "A3_Data_F", "A3_UI_F", "A3_Props_F_Exp_A", "A3_Weapons_F"};
        version = "1.0";
        author = "Yoshi";
    };
};


class CfgFunctions {
    class YAS {
        tag = "YAS";
        
        class Client {
            file = "\AdvSys\functions\client";
            class initPlayerLocal { postInit = 1; };
        };
        class Global {
            file = "\AdvSys\functions\global";
            class constants { preInit = 1; };
            class core { preInit = 1;};
            class initSettings {preInit = 1; };
            class utils { preInit = 1; };
        };
        class CBR {
            file = "\AdvSys\functions\cbr";
            class originHandler { preInit = 1; };
            class cbr { preInit = 1; };
            class cbrModuleEnable {};
            class cbrModuleToggle {};
        };
        class APS {
            file = "\AdvSys\functions\aps";
            class aps { preInit = 1; };
            class apsModuleEnable {};
            class apsModuleToggle {};
            class apsZeusClaimServer {};
            class apsZeusToggleResult {};
        };
        class IronDome {
            file = "\AdvSys\functions\iron_dome";
            class ironDome { preInit = 1; };
        };
        class Server {
            file = "\AdvSys\functions\server";
            class initServer { postInit = 1; };
        };
    };
};

class CfgVehicles {
    class Logic;
    class Module_F: Logic {
        class AttributesBase {
            class Edit;
            class Units;
            class Combo;
            class Checkbox;
        };
        class ModuleDescription;
    };

    class YAS_CBR_Module: Module_F {
        author = "Yoshi";
        category = "AdvSysSupport_Category";
        displayName = "Counter Batter Radar (CBR)";
        icon = "\A3\ui_f\data\map\mapcontrol\Transmitter_CA.paa";
        function = "YAS_fnc_cbrModuleEnable";
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
                "Placing this module will trigger the CBR code."
            };
        };
    };

    class YAS_CBR_Zeus_Toggle_Module: Module_F {
        scope = 1;
        scopeCurator = 2;
        displayName = "Toggle Counter Batter Radar (CBR)";
        category = "AdvSysSupport_ZEUS_Category";
        icon = "\A3\ui_f\data\map\mapcontrol\Transmitter_CA.paa";
        function = "YAS_fnc_cbrModuleToggle";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 1;
        curatorCanAttach = 0;
        vehicleClass = "Modules";
        class ModuleDescription {
            description = "Toggles the Counter Batter Radar event handler on or off during the mission.";
            syncRequired = 0;
        };
    };

    class YAS_APS_Module: Module_F {
        author = "Yoshi";
        category = "AdvSysSupport_Category";
        displayName = "Active Protection System (APS)";
        icon = "\a3\ui_f\data\igui\cfg\simpletasks\types\defend_ca.paa";
        function = "YAS_fnc_apsModuleEnable";
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
                "Sync vehicles to this module to enable APS on mission start."
            };
            sync[] = {"AnyVehicle"};
        };
    };

    class YAS_APS_Zeus_Toggle_Module: Module_F {
        scope = 1;
        scopeCurator = 2;
        displayName = "Toggle Active Protection System (APS)";
        category = "AdvSysSupport_ZEUS_Category";
        icon = "\a3\ui_f\data\igui\cfg\simpletasks\types\defend_ca.paa";
        function = "YAS_fnc_apsModuleToggle";
        functionPriority = 1;
        isGlobal = 0;
        isTriggerActivated = 0;
        isDisposable = 1;
        curatorCanAttach = 1;
        vehicleClass = "Modules";
        class ModuleDescription {
            description = "Place on a vehicle to toggle APS on or off.";
            sync[] = {"AnyVehicle"};
            syncRequired = 0;
        };
    };

    class Box_NATO_AmmoVeh_F;
    class YAS_OPHANIM_box: Box_NATO_AmmoVeh_F {
        _generalMacro = "YAS_OPHANIM_box";
        scope = 2;
        scopeCurator = 2;
        displayName = "OPHANIM (Iron Dome)";
        author = "Yoshi";
        editorCategory = "EdCat_Supplies";
        picture="AdvSys\ui\ophanim\ophanim_preview.paa";
		editorPreview="AdvSys\ui\ophanim\ophanim_preview.paa";
        
        hiddenSelectionsTextures[]=
		{
			"AdvSys\ui\ophanim\ophanim_signs.paa",
			"AdvSys\ui\ophanim\ophanim_box.paa",
		};
        transportAmmo=0;
		supplyRadius=0;
        ace_cargo_size = 2; 
		ace_cargo_canLoad = 1;  // 1 to allow loading into vehicles, 0 to disallow
		ace_dragging_canDrag = 1;  // 1 to enable dragging, 0 to disable
		ace_dragging_canCarry = 1;  // 1 to enable carrying, 0 to disable
		ace_dragging_dragPosition[] = {0, 2, 0};  // Adjust the position as needed
		ace_dragging_dragDirection = 0;  // Adjust the direction as needed
		ace_dragging_ignoreWeightCarry = 1;
		ace_dragging_ignoreWeight = 1;
    };
};

class CfgFactionClasses {
    class NO_CATEGORY;
    class AdvSysSupport_Category: NO_CATEGORY {
        displayName = "Pontifex: Advanced Systems"; // Name displayed in Eden Editor
        priority = 2; // Position of the category in the list
        side = 7; // Logic
    };

    class AdvSysSupport_ZEUS_Category{
        displayName = "Pontifex: Advanced Systems";
        priority = 2; 
        side = 7;
    };
};


class CfgSounds {
    sounds[] = {
        "ApsActiveProtectionSystem",
        "ApsAmmunitionAcquired",
        "ApsAmmunitionDepleted",
        "ApsDrone",
        "ApsDronePulse1",
        "ApsDronePulse2",
        "ApsHit",
        "ApsHardKillShot2",
        "ApsHardKillShot3",
        "ApsHardKillShot4",
        "ApsFail",
        "ApsInsufficientPower",
        "ApsPowerLevelIs",
        "ApsPercent",
        "ApsRemaining",
        "ApsSelfPropelledGrenade",
        "ApsSoftKillGlitch1",
        "ApsSoftKillGlitch2",
        "ApsSoftKillGlitch3",
        "ApsSoftKillGlitch4",
        "ApsSoftKillGlitch5",
        "ApsActivated",
        "ApsDeactivated",
        "ApsSuccess",
        "ApsExperimentalEnergyWeapon",
        "ApsOnline",
        "ApsVoiceOn",
        "ApsVoiceOff",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
        "one_hundred",
        "comma",
        "period",
        "YAS_OphanimReload1",
        "YAS_OphanimReload2"
    };

    class ApsActiveProtectionSystem {
        name = "ApsActiveProtectionSystem";
        sound[] = {"AdvSys\sounds\APS\active_protection_system.ogg", 1, 1};
        titles[] = {};
    };
    class ApsAmmunitionAcquired {
        name = "ApsAmmunitionAcquired";
        sound[] = {"AdvSys\sounds\APS\ammunition_acquired.ogg", 1, 1};
        titles[] = {};
    };
    class ApsAmmunitionDepleted {
        name = "ApsAmmunitionDepleted";
        sound[] = {"AdvSys\sounds\APS\ammunition_depleted.ogg", 1, 1};
        titles[] = {};
    };
    class ApsDrone {
        name = "ApsDrone";
        sound[] = {"AdvSys\sounds\APS\drone\drone1.ogg", 1, 1};
        titles[] = {};
    };
    class ApsDronePulse1 {
        name = "ApsDronePulse1";
        sound[] = {"AdvSys\sounds\APS\drone\drone1.ogg", 1, 1};
        titles[] = {};
    };
    class ApsDronePulse2 {
        name = "ApsDronePulse2";
        sound[] = {"AdvSys\sounds\APS\drone\drone2.ogg", 1, 1};
        titles[] = {};
    };
    class ApsHit {
        name = "ApsHit";
        sound[] = {"AdvSys\sounds\APS\hard\shot2.ogg", 1, 1};
        titles[] = {};
    };
    class ApsHardKillShot2 {
        name = "ApsHardKillShot2";
        sound[] = {"AdvSys\sounds\APS\hard\shot2.ogg", 1, 1};
        titles[] = {};
    };
    class ApsHardKillShot3 {
        name = "ApsHardKillShot3";
        sound[] = {"AdvSys\sounds\APS\hard\shot3.ogg", 1, 1};
        titles[] = {};
    };
    class ApsHardKillShot4 {
        name = "ApsHardKillShot4";
        sound[] = {"AdvSys\sounds\APS\hard\shot4.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSoftKillGlitch1 {
        name = "ApsSoftKillGlitch1";
        sound[] = {"AdvSys\sounds\APS\soft\glitch1.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSoftKillGlitch2 {
        name = "ApsSoftKillGlitch2";
        sound[] = {"AdvSys\sounds\APS\soft\glitch2.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSoftKillGlitch3 {
        name = "ApsSoftKillGlitch3";
        sound[] = {"AdvSys\sounds\APS\soft\glitch3.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSoftKillGlitch4 {
        name = "ApsSoftKillGlitch4";
        sound[] = {"AdvSys\sounds\APS\soft\glitch4.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSoftKillGlitch5 {
        name = "ApsSoftKillGlitch5";
        sound[] = {"AdvSys\sounds\APS\soft\glitch5.ogg", 1, 1};
        titles[] = {};
    };
    class ApsFail {
        name = "ApsFail";
        sound[] = {"AdvSys\sounds\APS\fail_sound.ogg", 1, 1};
        titles[] = {};
    };
    class ApsInsufficientPower {
        name = "ApsInsufficientPower";
        sound[] = {"AdvSys\sounds\APS\insufficient_power.ogg", 1, 1};
        titles[] = {};
    };
    class ApsPowerLevelIs {
        name = "ApsPowerLevelIs";
        sound[] = {"AdvSys\sounds\APS\power_level_is.ogg", 1, 1};
        titles[] = {};
    };
    class ApsPercent {
        name = "ApsPercent";
        sound[] = {"AdvSys\sounds\APS\percent.ogg", 1, 1};
        titles[] = {};
    };
    class ApsRemaining {
        name = "ApsRemaining";
        sound[] = {"AdvSys\sounds\APS\remaining.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSelfPropelledGrenade {
        name = "ApsSelfPropelledGrenade";
        sound[] = {"AdvSys\sounds\APS\self_propelled_grenade.ogg", 1, 1};
        titles[] = {};
    };
    class ApsSuccess {
        name = "ApsSuccess";
        sound[] = {"AdvSys\sounds\APS\success_sound.ogg", 1, 1};
        titles[] = {};
    };
    class ApsActivated {
        name = "ApsActivated";
        sound[] = {"AdvSys\sounds\APS\activated.ogg", 1, 1};
        titles[] = {};
    };
    class ApsDeactivated {
        name = "ApsDeactivated";
        sound[] = {"AdvSys\sounds\APS\deactivated.ogg", 1, 1};
        titles[] = {};
    };
    class ApsExperimentalEnergyWeapon {
        name = "ApsExperimentalEnergyWeapon";
        sound[] = {"AdvSys\sounds\AntiDrone\experimental_energy_weapon.ogg", 1, 1};
        titles[] = {};
    };
    class ApsOnline {
        name = "ApsOnline";
        sound[] = {"AdvSys\sounds\utils\online.ogg", 1, 1};
        titles[] = {};
    };
    class ApsVoiceOn {
        name = "ApsVoiceOn";
        sound[] = {"AdvSys\sounds\utils\voice_on.ogg", 1, 1};
        titles[] = {};
    };
    class ApsVoiceOff {
        name = "ApsVoiceOff";
        sound[] = {"AdvSys\sounds\utils\voice_off.ogg", 1, 1};
        titles[] = {};
    };

    class one {
        name = "one";
        sound[] = {"AdvSys\sounds\fvox_numbers\one.ogg", 1, 1};
        titles[] = {};
    };
    class two {
        name = "two";
        sound[] = {"AdvSys\sounds\fvox_numbers\two.ogg", 1, 1};
        titles[] = {};
    };
    class three {
        name = "three";
        sound[] = {"AdvSys\sounds\fvox_numbers\three.ogg", 1, 1};
        titles[] = {};
    };
    class four {
        name = "four";
        sound[] = {"AdvSys\sounds\fvox_numbers\four.ogg", 1, 1};
        titles[] = {};
    };
    class five {
        name = "five";
        sound[] = {"AdvSys\sounds\fvox_numbers\five.ogg", 1, 1};
        titles[] = {};
    };
    class six {
        name = "six";
        sound[] = {"AdvSys\sounds\fvox_numbers\six.ogg", 1, 1};
        titles[] = {};
    };
    class seven {
        name = "seven";
        sound[] = {"AdvSys\sounds\fvox_numbers\seven.ogg", 1, 1};
        titles[] = {};
    };
    class eight {
        name = "eight";
        sound[] = {"AdvSys\sounds\fvox_numbers\eight.ogg", 1, 1};
        titles[] = {};
    };
    class nine {
        name = "nine";
        sound[] = {"AdvSys\sounds\fvox_numbers\nine.ogg", 1, 1};
        titles[] = {};
    };
    class ten {
        name = "ten";
        sound[] = {"AdvSys\sounds\fvox_numbers\ten.ogg", 1, 1};
        titles[] = {};
    };
    class eleven {
        name = "eleven";
        sound[] = {"AdvSys\sounds\fvox_numbers\eleven.ogg", 1, 1};
        titles[] = {};
    };
    class twelve {
        name = "twelve";
        sound[] = {"AdvSys\sounds\fvox_numbers\twelve.ogg", 1, 1};
        titles[] = {};
    };
    class thirteen {
        name = "thirteen";
        sound[] = {"AdvSys\sounds\fvox_numbers\thirteen.ogg", 1, 1};
        titles[] = {};
    };
    class fourteen {
        name = "fourteen";
        sound[] = {"AdvSys\sounds\fvox_numbers\fourteen.ogg", 1, 1};
        titles[] = {};
    };
    class fifteen {
        name = "fifteen";
        sound[] = {"AdvSys\sounds\fvox_numbers\fifteen.ogg", 1, 1};
        titles[] = {};
    };
    class sixteen {
        name = "sixteen";
        sound[] = {"AdvSys\sounds\fvox_numbers\sixteen.ogg", 1, 1};
        titles[] = {};
    };
    class seventeen {
        name = "seventeen";
        sound[] = {"AdvSys\sounds\fvox_numbers\seventeen.ogg", 1, 1};
        titles[] = {};
    };
    class eighteen {
        name = "eighteen";
        sound[] = {"AdvSys\sounds\fvox_numbers\eighteen.ogg", 1, 1};
        titles[] = {};
    };
    class nineteen {
        name = "nineteen";
        sound[] = {"AdvSys\sounds\fvox_numbers\nineteen.ogg", 1, 1};
        titles[] = {};
    };
    class twenty {
        name = "twenty";
        sound[] = {"AdvSys\sounds\fvox_numbers\twenty.ogg", 1, 1};
        titles[] = {};
    };
    class thirty {
        name = "thirty";
        sound[] = {"AdvSys\sounds\fvox_numbers\thirty.ogg", 1, 1};
        titles[] = {};
    };
    class forty {
        name = "forty";
        sound[] = {"AdvSys\sounds\fvox_numbers\fourty.ogg", 1, 1};
        titles[] = {};
    };
    class fifty {
        name = "fifty";
        sound[] = {"AdvSys\sounds\fvox_numbers\fifty.ogg", 1, 1};
        titles[] = {};
    };
    class sixty {
        name = "sixty";
        sound[] = {"AdvSys\sounds\fvox_numbers\sixty.ogg", 1, 1};
        titles[] = {};
    };
    class seventy {
        name = "seventy";
        sound[] = {"AdvSys\sounds\fvox_numbers\seventy.ogg", 1, 1};
        titles[] = {};
    };
    class eighty {
        name = "eighty";
        sound[] = {"AdvSys\sounds\fvox_numbers\eighty.ogg", 1, 1};
        titles[] = {};
    };
    class ninety {
        name = "ninety";
        sound[] = {"AdvSys\sounds\fvox_numbers\ninety.ogg", 1, 1};
        titles[] = {};
    };
    class one_hundred {
        name = "one_hundred";
        sound[] = {"AdvSys\sounds\fvox_numbers\onehundred.ogg", 1, 1};
        titles[] = {};
    };

    class comma {
        name = "comma";
        sound[] = {"AdvSys\sounds\utils\comma.ogg", 1, 1};
        titles[] = {};
    };
    class period {
        name = "period";
        sound[] = {"AdvSys\sounds\utils\period.ogg", 1, 1};
        titles[] = {};
    };
    class YAS_OphanimReload1 {
        name = "YAS_OphanimReload1";
        sound[] = {"AdvSys\sounds\ophanim\reload1.ogg", 1, 1};
        titles[] = {};
    };
    class YAS_OphanimReload2 {
        name = "YAS_OphanimReload2";
        sound[] = {"AdvSys\sounds\ophanim\reload2.ogg", 1, 1};
        titles[] = {};
    };
};

class CfgRadio
{
	sounds[] += {
        "YAS_CBR_WarningLaunchDetected"
    };
    class YAS_CBR_WarningLaunchDetected
	{
		name	= "YAS_CBR_WarningLaunchDetected";
		sound[]	= {"AdvSys\sounds\CBR\warning_launch_detected.ogg", 1, 1};
		title	= "Warning, Launch Detected.";
	};
};
