# Vigil fixed-wing strike review

Review outcome: **REFINE BEFORE PERMANENT COVERAGE**.

Fixed-wing logistics shares the registry and aircraft lifecycle described here,
but delivery behavior is deliberately deferred to the next milestone.

## Behavioral contract

A valid fixed-wing asset can be registered from Eden or at runtime without
leaving a duplicate aircraft in the world. Its gameplay-relevant identity,
appearance, condition, fuel and exact pylon ammunition survive reconstruction.
A client with a Vigil tablet and a valid designation can deploy the registered
strike aircraft, see it physically enter from the configured ingress, and
request a real guided strike. The server-owned aircraft must release the exact
available munition, whose observed trajectory and impact correlate with the
client-owned designation and intended target. A second valid request consumes a
different round without duplicating the aircraft. A designation-free request
does not fire. RTB produces physical egress, bounded despawn, reusable registry
state and complete crew/task cleanup.

## Twelve-question review

1. **User observation.** Register a fixed-wing asset, deploy it from its ingress
   point, designate with either a handheld laser or a weapon IR pointer, request
   a strike, observe a guided physical impact, repeat, then command RTB and see
   the aircraft leave and disappear.
2. **Current behavior and negative paths.** Registration snapshots and removes
   the original. Dispatch reconstructs and crews one aircraft, establishes a
   loiter, and exposes strike actions. Requests are rejected while busy, without
   a tablet/designation, without an on-station strike aircraft, or without a
   suitable loaded weapon. RTB is now bounded and distinguishes successful
   egress, destruction and timeout.
3. **Machines and paths.** Client-a owns Vigil UI/input, its real laser target,
   and the weapon-IR helper. Requests originate on client-a. Registry mutation,
   reconstruction, aircraft/crew/group, fire execution, projectiles, damage,
   RTB and cleanup are dedicated-server authoritative.
4. **Generic mechanics.** Aircraft trajectory/locality, pylon comparison,
   designation identity/lifetime, Fired/projectile sampling, guidance distance,
   HitPart/damage and cleanup evidence belong in Tribunal.
5. **Product behavior.** Role classification, serialization policy, ingress and
   loiter selection, Vigil eligibility, designation consumption, compatible
   weapon selection, repeated strike availability and RTB registry state are
   Vigil semantics.
6. **Proven unusual requirements.** Real client input is required to create the
   engine handheld laser and to toggle the custom weapon-IR helper. The native
   Bomb04 requires no replacement to guide: a real server-local Fired projectile
   repeatedly tracked the client-owned laser and hit its target. No other oddity
   is frozen as an engine requirement.
7. **Accidental/fragile findings.** Fuel and per-pylon counts were lost during
   reconstruction. A broad `LaserBombCore` rewrite doubled native Bomb04 rounds.
   RTB could wait forever. A strike target close to the observer could kill and
   respawn the fixture player, silently losing its tablet. Those issues were
   corrected before specification coverage.
8. **Native alternatives.** Native pylon magazines, `fireAtTarget`, LaserTarget
   objects, MOVE/LOITER, and real aircraft/projectiles are retained. Replacing
   native Bomb04 with GBU12 was empirically unnecessary and removed. The 3CB
   Hellfire-to-Scalpel mapping cannot be evaluated with the installed content
   and remains experimental rather than characterized.
9. **Stable contract.** Correct registered identity and state, one physical
   server-owned aircraft, meaningful ingress/operation, valid client-owned
   designation, exact real weapon/ammo/projectile, physical guidance and effect,
   negative controls, repeatability, bounded egress and cleanup.
10. **Free implementation details.** Registry schema, helper names, exact
    coordinates, waypoint shape, sampling rate, representative aircraft/target,
    public-array layout and UI action IDs may change behind adapters.
11. **Characterization.** Only the real-input designation creation and native
    Bomb04 physical behavior have controlled evidence. AI reveal/watch/target
    ordering, the remaining 3CB mapping and precise loiter construction remain
    replaceable or NEEDS EXPERIMENTATION.
12. **Promoted Tribunal mechanics.** A product-neutral designation record and
    bounded observer capture class, netId, owner/locality, position, movement,
    lifetime and loss. Combat HitPart evidence now carries structured target,
    shooter, projectile, ammo, position, velocity and locality identity. The
    X11 probe supports real mouse buttons as well as keys.

## Architecture and lifecycle

`YSF_fwRegisterAsset` is the common entry used by synchronized Eden assets and
the Zeus/runtime module. It records a snapshot plus side, callsign, ingress,
egress, heading and a bitmask of strike, recon and logistics roles, commits a
public registry view, and deletes the original vehicle and crew. Strike, recon
and logistics therefore share registration, serialization, dispatch, public
state and RTB infrastructure; logistics delivery itself is not covered here.

The snapshot contains vehicle class, textures, fuel, pylon index/magazine/turret
and ammunition count, damage plus hitpoint state, role-relevant identity and UAV
state. Reconstruction creates the vehicle at the configured ASL ingress,
reapplies textures, pylons and exact counts, fuel and damage, creates crew,
establishes heading/velocity, and creates a loiter around the caller's operating
area. Registration removes the original, so successful dispatch must correlate
the stored asset ID to exactly one new physical aircraft.

The client chooses an on-station role-eligible aircraft and available LGB/LGM.
For a man, the designation descriptor first checks the engine laser target and
then the custom IR-helper target. A three-second live countdown rejects loss of
designation. The resolved LaserTarget is passed across the object-owner boundary
and the server-local aircraft executes `fireAtTarget`. The busy flag guards only
request construction; physical success is established separately from Fired,
trajectory and impact evidence.

RTB removes combat waypoints, assigns a full-speed MOVE toward the recorded ASL
egress, and despawns inside its completion radius. A 300-second deadline fails
closed as `timeout`; destruction and successful egress are distinct durable
results. The registered entry remains stowed/cooldown and reusable while the
spawned aircraft and crew are cleared.

## Implementation-quality classification

| Subsystem | Classification | Resolution |
| --- | --- | --- |
| Eden/runtime registration | KEEP AS-IS AND SPEC-TEST | both feed one authoritative registry API |
| snapshot/remove/reconstruct model | REFINE BEFORE PERMANENT COVERAGE | restore fuel and exact pylon counts |
| role bitmask and shared lifecycle | KEEP AS-IS AND SPEC-TEST | strike/recon/logistics identified; logistics deferred |
| client request/server ownership | KEEP AS-IS AND SPEC-TEST | locality asserted at every object boundary |
| handheld laser descriptor | KEEP AS-IS AND SPEC-TEST | real input, lifetime and ownership proven |
| weapon-IR helper | KEEP + CHARACTERIZE ENGINE REQUIREMENT | real L input creates/moves/cleans client-local LaserTarget in daylight without NVG |
| native Bomb04 | KEEP AS-IS AND SPEC-TEST | physically guides and impacts under current Arma build |
| generic LaserBombCore replacement | REWRITE BEFORE PERMANENT COVERAGE | removed; it changed one native round into two GBU12 rounds without benefit |
| 3CB Hellfire replacement | NEEDS EXPERIMENTATION | no compatible installed 3CB pylon row available for an honest A/B |
| AI reveal/watch/target sequence | NEEDS EXPERIMENTATION | retained but not frozen as contract |
| ingress/loiter | KEEP AS-IS AND SPEC-TEST | physical travel, altitude, operating center and locality asserted |
| repeated strike state | KEEP AS-IS AND SPEC-TEST | two distinct rounds/targets on one deployed aircraft |
| RTB/despawn | REFINE BEFORE PERMANENT COVERAGE | bounded success/destroyed/timeout result |
| fixed-wing logistics delivery | DEFER | next feature milestone |

## Serialization and compatibility findings

The initial controlled serialize/reconstruct comparison reported fuel
`0.37 -> 0.999948`, pylon ammunition `3 -> 7`, and native
`PylonMissile_1Rnd_Bomb_04_F/1` becoming
`PylonRack_Bomb_GBU12_x2/2`. Reconstruction now preserves fuel and each pylon's
actual count and no longer rewrites every `LaserBombCore` descendant.

| Munition path | Config metadata | Observed physical behavior | Decision |
| --- | --- | --- | --- |
| `PylonMissile_1Rnd_Bomb_04_F` / `Bomb_04_F` | `laserLock=1`, `simulation=shotMissile` | real server-local projectile steered to the client LaserTarget and produced matching HitPart/damage | keep native baseline |
| `PylonRack_Bomb_GBU12_x2` replacement | laser-guided | also guided, but doubled ammunition and did not improve reliability | remove generic rewrite |
| 3CB Hellfire to Scalpel mapping | hard-coded class-name family | installed environment contains no qualifying `uk3cb_baf_pylonrack_*hellfire` row | NEEDS EXPERIMENTATION |

The compatibility decision is behavioral, not label-only: every permanent
positive requires exact weapon, magazine, ammo, Fired projectile, sampled path,
closest approach and attributable target effect.

## Designation findings

The normal path uses Arma's client-local `LaserTargetW`. Tribunal records the
same netId remotely on the server, correct side/owner, ASL position, movement
and cleanup. The custom IR path detects the current primary weapon's active IR
pointer, raycasts the aim point, maintains a client-local LaserTarget helper,
updates it while the weapon moves, and deletes it when the light is toggled off.
Live input proved that it works in daylight without NVGs. The local beam/UI
surface is supporting evidence only; world-state designation and the physical
strike remain authoritative.

## Evidence and false-PASS controls

Live experiments separated registration, reconstruction, real input, native
munition behavior and replacement behavior before the permanent scenario was
built. Each strike correlates asset ID, aircraft netId, designation netId,
target netId, weapon, magazine, ammo and projectile netId. Trajectory samples
must approach the intended target and the same projectile must appear in that
target's structured HitPart record with positive damage. Thus a state label,
wrong aircraft, unrelated explosion, unguided coincidental miss, stale target,
old event or changed loadout cannot satisfy the scenario.

The no-designation control removes both designation mechanisms and requires no
new Fired record. Repeated coverage requires two distinct projectiles and two
distinct targets from the same still-live on-station aircraft. The fixture
client is damage-isolated during nearby strike observation so collateral cannot
replace the player and silently discard its tablet; normal damage handling is
restored during cleanup. RTB requires substantial sampled travel toward egress,
successful bounded despawn, null spawned state and retained registry identity.

Client-a owns its input and both LaserTarget objects. The dedicated server owns
the registry, aircraft, crew/group, both projectiles, HitPart/damage observation,
RTB and cleanup. Future client-b coverage should require it to observe shared
aircraft/projectile effects once without inheriting client-a's input/helper
state; it is not a blocker for this single-account milestone.

Fresh autonomous run `20260813T223927Z-1903e68c` passed 22 server and
16 client assertions with zero failures. The reconstructed aircraft retained
fuel `0.73`, damage `0.04`, and three native Bomb04 pylons with one round each.
It traveled 2,389.5 m during the ingress observation without a ground sample.
The handheld designation `4:3` produced projectile `2:155`; 368 samples reached
7.73 m from target `2:154` and the exact projectile appeared in HitPart. The
weapon-IR helper `4:4` produced projectile `2:157`; 371 samples reached 11.83 m
from target `2:156` and again produced exact-projectile HitPart. The control
left the fire count at two. RTB then sampled 5,820.81 m of physical travel,
reached 379.22 m from egress, despawned successfully, and left the registry in
cooldown. Authenticated framebuffer evidence recorded one B selection, one
mouse activation, one L activation, three bounded downward aim corrections,
and designation cleanup. All containers, private network and runtime state were
removed by normal teardown.

## Next milestone

Fixed-wing logistics should reuse the proven registry, serialization,
reconstruction, aviation and cleanup tooling, but needs its own behavioral
review of payload creation, delivery destination, release/landing mechanics and
failure controls. Strike assumptions must not be copied into that test.
