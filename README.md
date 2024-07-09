# Yoshi's Support Framework

[Steam Workshop Page](https://steamcommunity.com/sharedfiles/filedetails/?id=3119475113)

**This is a simple and easy to use system for implementing AI-driven deployments.**

Disclaimer: This is my first ever attempt at creating a mod, so I by no means am considering myself an expert. If you find any issues, I appreciate if you could kindly report them in the [comments](https://steamcommunity.com/sharedfiles/filedetails/?id=3119475113) and I will do my best to try and take a look.

## Contents

1. Future Plans
2. What does this mod do
3. Reinserts
4. Close Air Support (CAS)
5. Artillery
6. Recon
7. Counter Battery Radar (CBR)
8. Fun Facts
9. Special Thanks

## 1. Future Plans / Backlog

*Why not start with looking towards the future?*

These are a few ideas that I hope to look into and implement either because they would enrich the mod, or simply because I think they would be a cool addition.

> Note: these ideas are nothing more than a promise to look into the idea. Some may be unrealistic to implement, either due to limitations of the game, or limitations of my skill-set at the moment, and others may even be flat-out impossible.

In no particular order:

- Logistic
  - I have a few ideas for this one, but I think the main focus may be on automating things such as airlifts of supplies and/or vehicles.
- Active Protective System (APS)
  - I actually have a lot of the code written, but I still need to figure out the consistency given the requirement that this would have to work in multiplayer (syncing between players and server can be a pain sometimes)
- Electricity
  - Though a bit of a tangent from the original mod, I had this idea to look into some system that could make maps have a functioning "electric grid" or at least some semblance of one. This could potentially allow you to take out a power-line and knock out power to a base before your next raid. Or perhaps it will result in a humanitarian mission to restore power to a town.
- Electronic Warfare
  - Tangentially related to the idea above, I'd love to actually add some form of electronic warfare to the game.
- Make nicer icons for ace interact
  - I like nice quality-of-life things, so at some point I hope to go back and make all the actions have nice icons.
- Add more sounds
  - Although I might have gone overboard with the counter battery radar, I think it would be neat to have more sounds, even if it's something simple like a tiny acknowledgement sound when you perform an action.

## 2. What does this mod do

This mod allow a player to call in helicopter missions from their ace self interact menu, if they have the "required item" (configured in the "how to use" section).

**Please note: in an effort to try and reduce the potential load on the server, this mod runs on a 3 second clock, so please be patient if you call something in and nothing happens immediately... it might be delayed by about 3 seconds, but you should never have to wait more than 5 ever.**

You are able to add markers on your map that will automatically be considered viable landing zones for the helicopter. (an invisible helipad will be spawned at that location if there is no other viable pad nearby, so be cautious when adding a marker in a dangerous location, the helicopter will try to forcibly land even in a dense forest)

You may configure the module's size/shape, as well as configuring what prefixes are considered as landing zones (default is LZ and HLS, case insensitive)

## 3. How to use: Reinserts

In the eden editor, under modules, there will be a tab called "Yoshi's Redeployment System" and inside, there will be a module called "Home Base Module"

All you need to get started is to place the module down in the center of your base.

Note: hopefully this would be obvious, but Helicopters need A.I. pilots in order for this to work.

By default, the "base" is considered to be everything inside of a 500 meter radius around the module. This is important since any helicopters inside of the radius will receive  ace interactions on them, where you can register the vehicle for redeployment. The value of the radius can be changed by double-clicking on the module and changing from the default 500 in the transformation tab.

Also by default, the basic spectrum device is considered to be your "required item" in order to call in the helicopter missions. However, you can add any item (by class-name) by double clicking the module and providing a comma separated list of all items you want to have considered.

> Note: the "required item" check is performed on the items in your inventory, not held items (like your rifle/pistol) those items can be used, but will only be recognized if you place them somewhere like your backpack

Helicopters need to be "registered" before they become available to players with the required item. Registration is available for any helicopters that are on the ground, and in the home base's radius. You can automatically register helicopters by sync-ing them to the home base module.

Once a helicopter is registered, members near the helicopter will also be able to "request redeployment" from the helicopter's ace menu. All this does is highlight said helicopter with a green color to those who have the "required item" -- this is not a required step, it's purely a visual feature, but one that could be used to signal that a helicopter is "ready to go"

## 4. How to use: CAS (EXPERIMENTAL)

Placing down the CAS module allows you to set what map markers will be considered for CAS (default prefixes are "target" and "firemission", but these can be changed, or added to as a comma separated list, much like the reinsert markers)

**Module does not need to be synced to any other module, and the Module's location is irreverent.**

Synchronizing a helicopter will automatically have it considered to be CAS at mission start, but you can still assign to CAS with the ace interaction on a CAS capable helicopter within the base.

Calling in the CAS heli will result in it going to the marked target, and engaging any hostiles it detects. After 3 minutes and 30 seconds, the heli will stop it's attack, and land back at base.

## 5. How to use: Artillery (EXPERIMENTAL)

The Artillery module must be placed down, and similarly, it will recognize certain markers as viable targets. (Prefixes can be configured similarly to Reinserts and CAS)

**Module does not need to be synced to any other module, and the Module's location is irreverent.**

There are many checks for allowing an artillery piece to fire. Once you have a registered artillery (synchronizing it to the artillery module will automatically register it) you then need to place a target marker on the map, and it will appear in your self-interactions in the artillery option. Next you can choose your artillery unit for the firemission, then what ammo type it should use, and then lastly how many rounds will be fired. Letting go on the number will immediately call in the artillery strike.

The option to use the artillery unit will not appear if the unit does not have any ammo capable of hitting the target.

Sometimes the artillery may not fire, and usually it's because of it's positioning. I've noticed that if it's too close to nearby structures, it has a difficult time acquiring the target, even though it's capable to hitting it.

## 6. How to use: Recon (EXPERIMENTAL)

The Recon module must be placed down, and similarly, it will recognize certain markers as viable targets. (Prefixes can be configured similarly to Reinserts, CAS, and Artillery)

**Module does not need to be synced to any other module, and the Module's location is irreverent.**

At the moment, the only way to register recon units are via syncing them to the Recon Module. Any synced units will be available for recon missions, which involves loitering near a marked objective, and marking targets on the map. The interval of which the marks appear can be configured, as well as how long the recon mission will last. Additionally, you can enable "hyperspectral sensors" which can give the recon unit perfect knowledge and marking ability, if you would like to forgo the more realistic "line of sight" detection used by default.

The more interesting option (in my opinion) is what I'm calling "Field Recon Task" which allows a player to interact with a drone on the ground, and the drone itself will have a the option to be called on a recon mission. Once the mission is completed, the drone will automatically fly back to the player who ordered the mission. The player does not need to remain stationary; once the drone is done, a hint will appear that lets the player know that it's returning, and only then should you wait for it to land near you. This task does NOT require the drone to be registered in the system. The scripts will automatically add the relevant actions to any viable drones that exist in the mission, even if they are placed down during the mission runtime.

## 7. How to use: Counter Battery Radar (EXPERIMENTAL)

The Counter Battery Radar module must be placed down, and synchronized to any vehicle or object that will serve as your counter battery radar. Walking up and interacting with the vehicle will give you the ability to enable the radar, and you will hear an audible click, followed by a status beep every 5 seconds to remind you that the radar is operational.

This radar will mark on the map any projectile that it detects, and will also calculate an estimated impact location, where it will also sound the corresponding alarm depending on where the estimated impact is calculated to be.

**Module does not need to be synced to any other module, and the Module's location is irreverent.**

In the settings of the module, you will have the ability to set zones of alarm, ranging from basic detection, caution, warning, and incoming. I think the default values for the ranges are quite nice, but feel free to modify them, or set them to 0 if you would like to disable a particular alarm. Each alarm will trigger if a projectile is detected to have an impact within the relevant range that was configured, with each tier taking higher precedence than the last, to prevent overlapping alarms.

## 8. Fun Facts

By default, the built in game's "Base" gets used as the ATC side communication, but you can sync any unit to the module and that unit's call-sign will be used instead.

The CAS and Artillery can be configured to have a different required item for each. This way you can make it so that only certain modules are accessible to certain people.

This mod should be compatible with any modded helicopter, assuming it inherits from the base Arma's "Helicopter" class

if your mission includes a Zeus, the Game master will be able to place down additional helicopters and helipads at the home base, and they will all become recognized dynamically.

Zeus will also automatically have access to any and all actions regardless of if they have a required equipment on their character or not. However, this will only be if they self-interact within the game master interface.

## 9. Special Thanks

- Bull (Moppy), the man who inspired the Mod

- Chamberlain (lackofcoolness), for putting up with me when I would constantly pester to help me test this

- 9 Rifles, the community which I originally made this mod for: [Community Post](https://steamcommunity.com/app/107410/discussions/10/4358995119368996357/)
