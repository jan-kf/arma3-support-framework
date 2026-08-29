# Vigil Tablet validation

## Runtime architecture

Vigil is a client-local Arma dialog. `YSF_UI_OpenTablet` requires the CBA
`YSF_enableTablet` setting and `YSF_VigilTerminal_B` in the real player's
assigned items, then creates `YSF_Tablet_Dialog` (IDD 88000). CBA binds that
open action to Ctrl+Home. Dialog `onLoad` stores the display in
`uiNamespace["YSF_Tablet_Display"]` and initializes navigation; `onUnload`
clears overlay markers, replaces the display with `displayNull`, and emits the
TurnOff sound event.

The shipped registry currently exposes the Assets page. Its RscToolbox (IDC
88050) has Transport, Artillery, CAS, and Fixed Wing tabs. Selection invokes
`YOSHI_assetsTabChanged`, which records `YSF_assets_tabIndex`, maps it to the
asset type, and refreshes the corresponding controls. The page and selection
state, display reference, and map overlays are client-local in `uiNamespace`.
Support-task/governor data may be server-backed, but the first UI scenario does
not create or execute support tasks. An empty support inventory is valid and
renders the no-assets state.

The UI emits BootUp, DialUp, UiActivate, UiTabSwitch, and TurnOff events. Normal
automated clients currently use `-noSound`; this milestone proves the UI/event
path, not audible output. There are no required animations for the selected
Assets-tab interaction. A cold client can enter `initPlayerLocal.sqf` while
Arma is still building action-map caches, so the scenario arms external input
only after a bounded post-init/inventory settle, then equips and verifies the
fixture item against the gameplay display and living player. This ordering is
important because late join inventory synchronization can overwrite an item
linked immediately from `initPlayerLocal.sqf`.

## MVP scenario and evidence

The permanent `vigil-ui` Tier 3 scenario uses the smallest meaningful path:

1. equip the real Vigil terminal on `client-a`;
2. capture the baseline 1280x720 Arma framebuffer;
3. deliver the product's real Ctrl+Home binding as XTest keycodes on the
   private Xwayland display (so Proton emits CBA's expected DIK event);
4. correlate the rendered Transport page with dialog/control existence and
   `YSF_asset_type="transport"`;
5. click the real Artillery tab, move the pointer away, and correlate the
   persistent rendered page transition with tab index 1, asset type `arty`,
   visible artillery controls, and hidden transport controls;
6. deliver Escape, require visual disappearance, `displayNull`, and cleared
   overlay markers;
7. invoke the normal open action in a fresh scheduled UI context and require a
   clean Transport/index-0 state.

The server independently asserts that it is dedicated/headless, has no Vigil
display, and executed no duplicate server-side UI path. Scenario metadata is
identity-based rather than count-based so a future `client-b` assertion can
require an unchanged display and namespace without redesigning the contract.
The VNC listener remains internal to the confined client container and is not
published to the host for autonomous runs.

Tribunal stores baseline/open/target/closed/reopened captures, region metrics,
protocol negotiation, changed-pixel fractions, and input details as a typed
`interactive-framebuffer-sequence` attachment. Visual checks use stable regions
and tolerant structural differences, never full-frame equality.

Weston's RFB keysym transport is retained for Escape and pointer input, but it
did not translate Ctrl+Home into the DIK Home chord on a cold Proton client.
Tribunal therefore uses the existing container-local XTest library for that
keyboard chord and records the backend in evidence. Both transports remain
inside the unpublished client display boundary.

## False-pass threats

The evidence contract explicitly rejects these misleading outcomes:

* a non-null display with no visible rendered tablet;
* a visible tablet on the wrong page;
* a stale or black framebuffer;
* an existing but hidden, disabled, or off-screen control;
* an RscToolbox hover highlight mistaken for selection;
* a callback or backing-state change without a persistent rendered change;
* a rendered change without matching tab/type/control state;
* an internal function call presented as the primary user input;
* a different page mistaken for a closed tablet;
* uncleared local overlay markers after close;
* stale tab state after reopen;
* server-side display ownership or a duplicate open path;
* missing screenshots, input results, product assertions, or lifecycle states.

The hover case was observed in Live Mode: merely pointing at Artillery painted
it like a selection. The generic driver now moves away and requires the larger
page transition plus independent application-state evidence. Missing or
ambiguous evidence fails closed.

Arma also reports `ctrlShown=false` for Vigil's inherited initial page/control
groups even while their children visibly render. Initial and reopened state
therefore require the real display/control objects, enabled tab control,
selection, and application type, correlated with the framebuffer; the test
does not reinterpret that unreliable parent visibility flag as rendering.

## Dynamic map-marker architecture

Vigil currently has four marker-producing paths, all created with
`createMarkerLocal` in the client UI context:

* artillery strike-pattern previews in `YOSHI_drawStrikePattern`;
* selected asset and fixed-wing overlays in `YOSHI_assetSelected`;
* coordinate-preview markers in `YOSHI_assetCoordChanged`;
* an optional first-round ETA icon created with the strike preview.

There is no incoming-artillery or incoming-rocket detection/aggregation system
in the current Vigil source. The dynamic behavior tested here is therefore the
real artillery *preview*, not an invented threat detector and not artillery
execution. The product stores preview inputs in
`uiNamespace["YOSHI_taskArty_state"]`, generated world positions in
`uiNamespace["YOSHI_taskArty_strikePattern"]`, and current marker names in
`uiNamespace["YOSHI_sp_markers"]`. Changing count, spread, direction, pattern,
grid, or ordnance calls `YOSHI_taskArty_DrawFromState`, which deletes the old
local names and recreates the complete pattern. Count zero clears the pattern.
Dialog unload calls `YSF_clearAllMarkers`; there is no independent time-based
expiry for preview markers.

The permanent `vigil-markers` scenario drives the actual coordinate and count
handlers without submitting a support request. It fixes the map at world
`[4680,2770]` and scale `0.2`, then proves:

1. count zero has no marker names or strike positions;
2. count one creates one registered 100x125 m ellipse at the exact world point;
3. count three deletes that name and creates three distinct registered
   ellipses/positions;
4. returning to zero removes all three names from `allMapMarkers`;
5. Escape destroys the client display and retains empty marker stores.

Scale matters to visual evidence. At scale `0.025`, the 100x125 m ellipse
border lies outside the visible viewport even though its center projects
on-screen. The calibrated `0.2` view keeps the complete marker footprint in
the map and prevents an off-viewport rendering false negative.

The server asserts that it is dedicated/headless and owns neither the display
nor preview marker state. The client asserts `hasInterface`, identity
`client-a`, the map/control objects, exact local marker registry entries, and
world-to-screen projections. This preserves a future client-b contract: its
local namespace must remain empty unless it independently opens and drives its
own preview.

Tribunal's generic `region_difference` helper reports a bounded changed-pixel
count/fraction, full-frame centroid, and bounding box. The authenticated RFB
map driver correlates those metrics with backing state and stores
game/open/page/baseline/one/three/cleared/closed screenshots as an
`interactive-map-marker-sequence` attachment. It accepts anti-aliasing and
scaling differences but requires the change near the expected projected map
anchor, a larger distinct three-marker footprint, two stable restored baseline
frames, and a visibly closed UI.

Marker validation explicitly rejects:

* backing state without rendered pixels;
* unrelated framebuffer changes outside the bounded map;
* a marker whose changed-pixel centroid is inconsistent with the projected
  world coordinate;
* a marker outside the current viewport;
* reused/stale marker names or old names still present in `allMapMarkers`;
* three backing entries with no distinct rendered footprint;
* transient hover paint mistaken for the Artillery page;
* cleanup state whose framebuffer does not return to baseline;
* another client's or the dedicated server's namespace satisfying client-a;
* missing screenshots, protocol evidence, marker properties, or lifecycle
  stages.

## Follow-on order

After this MVP, add coverage in this order:

1. client-b isolation while client-a opens and changes pages;
2. benign invalid/edge-case input and close/reconnect state;
3. artillery request lifecycle;
4. helicopter movement and landing;
5. CAS tasking;
6. network-profile behavior for task and marker replication;
7. audible sound capture after Tribunal gains its opt-in audio backend.

## Artillery execution architecture and coverage strategy

Vigil's artillery path is smaller than the tablet's fixed-wing designation
path. The code-authoritative artillery target is an eight-digit, 10-metre
grid (either `12345678` or two four-digit components separated by whitespace,
`-`, `,`, `:`, or `;`). `YOSHI_parseGrid` rejects every other shape and
`YOSHI_assetCoordChanged` converts the accepted pair to `[x * 10, y * 10, 0]`.
The artillery page does not consume `laserTarget`, `YSF_irFakeLaserTarget`, or
any target descriptor. Real designator and weapon-mounted IR-pointer targets
belong to the fixed-wing strike implementation. They are deliberately not
claimed as artillery modes by this milestone.

The client owns the dialog, input controls, request construction, and local
preview markers. Its only strike options are ordnance magazine, spread, round
count, `circle` or `line`, and line direction. Circle points use a golden-angle
disk distribution inside `spread`; line points are evenly spaced across the
full spread and sorted along the requested bearing. There is no separate
creeping-barrage mode, salvo count, inter-round delay, or source selector.
Round order on a line is the only sequential spatial progression.

Assets are discovered map-wide, filtered to the player's config side, and
accepted when a living non-air land vehicle or ship has non-empty
`getArtilleryAmmo`; `B_Ship_MRLS_01_F` is the one explicit exception. The
selected asset's effective commander's group supplies all firing vehicles,
and strike positions are assigned round-robin across them. Thus mortar,
self-propelled tube, and rocket artillery share Arma's native
`doArtilleryFire` branch. Their class-specific range, magazines, ballistics,
dispersion, and cadence come from engine configuration. Vigil does not keep a
platform whitelist.

`YOSHI_taskArty_submit` sends a task through CORDIS's server-once boundary.
The dedicated server owns the governor and authoritative task record. It
rejects an empty position list, empty magazine, or group with no live firing
vehicle. Each native shot is range-checked again and executed on the effective
commander's locality. A task is complete only after every firing vehicle
reports `YSF_arty_mission_completed` as done/dead, followed by the governor's
final radio/completion stage. Preview range/ETA is advisory and client-local;
server range checks remain authoritative.

VLS is a separate special case keyed exactly to `B_Ship_MRLS_01_F`. For each
point it reloads `weapon_VLS_01`, creates a temporary helipad target, reports
and confirms that sensor target, and calls `fireAtTarget` on the commander's
machine. A Fired handler supplies launch acknowledgement, with one bounded
retry. The temporary target lasts 100 seconds. This path bypasses native
artillery range/ETA checks, does not track missile arrival, and its current
munition label is diagnostic only. Those properties make VLS materially more
fragile: a command/`YSF_fired` transition is not proof of vertical launch,
guided flight, or arrival.

The permanent coverage matrix is branch-oriented rather than Cartesian:

| Scenario | Target/request | Source path | Pattern/count | Physical/control proof |
| --- | --- | --- | --- | --- |
| native circle | real grid control and submit | mortar/native artillery | 3-round circle | exact firing source/magazine/projectiles, termination coordinates, centroid/radial bounds, server completion |
| native line | product task using the same parsed grid | same native branch | 4-round line with large spacing | along-axis span/order and bounded perpendicular error despite dispersion |
| request controls | invalid grid, zero rounds, out of range, empty ammunition | native validation branches | none | no correlated Fired/ArtilleryShellFired events and explicit failed/skipped state |
| platform discovery | engine config/runtime inventory | mortar, tube, rocket representatives | n/a | capability and magazine/range evidence without repeating identical firing code |
| VLS | valid grid/task | custom VLS branch | one cruise missile | exact launcher/missile, vertical phase, guided flight samples, single launch, target-region arrival |

Each strike uses a unique token and a fresh observer window. Tribunal records
the requested and resolved points, firing platform, weapon, magazine/ammo,
projectile netId and locality, fire time, sampled trajectory, last observed
position/termination time, and task state. Spatial assertions tolerate the
calibrated weapon dispersion but fail on missing rounds, wrong source/ammo,
stale events, wrong target region, or internal completion without physical
evidence. Generic collection and geometry live in Tribunal; Vigil scenarios
retain only product controls, tasks, and expected semantics.

Laser-designator and weapon IR-laser scenarios remain a later fixed-wing
strike milestone. A future independently authenticated client-b should prove
that client-a's tablet state stays local while both clients observe the same
authoritative firing and impact events.

The fresh autonomous proof `20260813T130024Z-4b285268` completed with 22/22
server and 9/9 client assertions. Its three-round circle terminated 1.94-8.46
metres from the generated points. Its four-round line covered a 240.4-metre
along-axis span with 0.27-9.25 metres of perpendicular error. All seven native
shells correlated to both `Fired` and `ArtilleryShellFired`, and the zero-round,
out-of-range, and no-ammunition controls produced no shots. The real VLS
missile (`2:214`) launched at 1.04 metres ASL, climbed to 210.0 metres,
travelled 2.228 kilometres horizontally, and terminated 4.66 metres from its
requested region. The fully simulated ship is held at the sea surface only
until its `Fired` event so cold-run water settling cannot destroy the missile
at spawn; the missile's position, velocity, guidance, and lifetime are never
altered by the fixture.

Rendered artillery-tab and dynamic preview evidence remains the responsibility
of the existing `vigil-ui` and `vigil-markers` scenarios. This execution
scenario consumes the same product grid parser, pattern generator, task state,
and submit function, then correlates that backing request with authoritative
fire and flight evidence. Keeping those proofs separate avoids treating a
valid framebuffer as evidence of a shot, or a valid shot as evidence that the
client-local controls rendered correctly.

Each behavioral scenario should keep real input/rendered evidence distinct
from server-authoritative task effects and must pass from a fresh autonomous
run after any Live Mode iteration.

## Rotary-wing CAS

`vigil-cas` combines the real client `YOSHI_taskCAS_submit` path with generic
Tribunal aviation and combat observation. Its server-owned fixture uses a
crewed `B_Heli_Attack_01_F`, a fully simulated hostile tank in the requested
area, and widely spaced friendly, civilian and off-area-hostile controls. The
target's minimum EAST crew supplies native target identity but has all AI
disabled and fuel removed, preventing anti-air return fire from turning a CAS
behavior test into a survivability test.

The attack proof requires exact aircraft/hostile correlation in Vigil's Fired
ledger, real configured cannon/ammunition, ammunition consumption, and HitPart
on the hostile. Controls require no intentional-target ledger, no HitPart and
zero damage. Physical trajectory proves dispatch and return; the authoritative
active window proves timer behavior and no post-expiry fire. The same aircraft
then completes a no-target request with no new fire, and a separate zero-ammo
aircraft must fail closed. See
[`reviews/vigil-cas-review.md`](reviews/vigil-cas-review.md)
for the review, experimental comparisons and false-PASS analysis.

## Fixed-wing strike support

`vigil-fixed-wing` validates Vigil's serialized fixed-wing lifecycle rather
than treating it as rotary CAS. A server-owned A-10 is registered and removed,
then reconstructed at its configured ingress with class, textures, damage,
fuel and exact native Bomb04 pylon counts preserved. Tribunal samples its
physical ingress and records aircraft, pilot and group locality.

The authenticated client creates a real handheld laser with B and mouse input,
then Vigil requests a native `Bomb_04_Plane_CAS_01_F` release. The same deployed
aircraft repeats the path using Vigil's weapon-mounted IR helper activated by a
real L keypress. Each positive correlates designation, aircraft, weapon,
magazine, ammo, projectile trajectory, intended target, HitPart and damage.
The no-designation control requires no additional Fired event. Finally the
aircraft physically travels toward egress and is removed by the bounded RTB
lifecycle while its reusable registry entry remains.

The review removed a generic laser-bomb replacement after Live comparison
showed native Bomb04 already guides physically and the replacement doubled the
round count. Fuel and per-pylon ammunition restoration and a bounded RTB result
were added before permanent coverage. The remaining 3CB Hellfire mapping is
explicitly experimental because the installed content cannot exercise it. See
[`reviews/vigil-fixed-wing-review.md`](reviews/vigil-fixed-wing-review.md).

## Fixed-wing logistics

`vigil-fixed-wing-logistics` drives the real Vigil-to-Field-Utilities interface,
submits a physical mixed-category manifest, and correlates the resulting
server-authoritative aircraft, pallet and parachute through ingress, release,
descent, accurate intact landing, exact delivered inventory, RTB and cleanup.
The empty-manifest and concurrent-duplicate paths fail closed. There is no
capacity/weight implementation, so the scenario does not invent one.

Generic inventory-tree and cargo/parachute evidence lives in Tribunal; Vigil
role, request, task and reuse semantics remain product-side. See
[`reviews/vigil-fixed-wing-logistics-review.md`](reviews/vigil-fixed-wing-logistics-review.md)
for the architecture review, engine characterizations, Live calibration and
false-PASS analysis.

## Fixed-wing reconnaissance

Fixed-wing reconnaissance is not currently a testable product feature. The
registry can label UAV planes `RECON`, but those aircraft are explicitly blocked
from deployment and no request, sensor collection, user-visible result, task
lifecycle or multiplayer propagation exists. The disconnected Recon form has no
submit action and an empty task implementation. Tribunal therefore adds no
gameplay scenario until the information product and lifecycle are decided. See
[`reviews/vigil-fixed-wing-recon-review.md`](reviews/vigil-fixed-wing-recon-review.md).
