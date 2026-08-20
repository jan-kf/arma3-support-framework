# Pontifex feature inventory

This is a repository-grounded map of the Pontifex runtime at commit `a55d2d1`.
It is an inventory, not a roadmap or a promise that every source surface is
intended to survive. It records what exists so later reviews can choose stable
behavioral contracts before permanent Tribunal coverage is added.

Reviews selected from this inventory follow Tribunal's
[`feature-review-program.md`](feature-review-program.md). A completed review
updates the affected inventory status; the inventory itself does not invent or
establish product semantics.

## Reading the inventory

Implementation state:

* **Implemented** — an active registration/startup path reaches substantive behavior.
* **Partial** — meaningful behavior exists, but a named workflow has a missing,
  fragile, or explicitly unfinished stage.
* **Scaffolded** — types, state, or UI exist without an executable end-to-end capability.
* **Disabled/unreachable** — a guard, missing action, or absent registration blocks normal use.
* **Obsolete/dead** — a path appears superseded or unreachable. This is a review
  finding, not authorization to delete it.
* **Unclear** — repository evidence does not establish supported-product intent.

Coverage status:

* **COVERED** — a permanent scenario has a reviewed specification contract.
* **PARTIALLY COVERED** — only part has a contract, or a composite feature covers
  it while adjacent behavior remains uncovered.
* **REVIEWED / DEFERRED** — formal review found no current testable contract or
  insufficient value.
* **REVIEWED / NEEDS EXPERIMENTATION** — formal review retained an unresolved
  engine or compatibility question requiring controlled evidence.
* **NOT YET REVIEWED** — implementation exists without formal review/permanent coverage.
* **UNKNOWN** — intent or reachability is too unclear for a stronger status.

“Incidentally exercised” never means specification-covered. Static checks,
smoke assertions, and execution as a dependency are useful regression evidence,
but do not establish a user-facing contract.

## Top-level map

Five top-level runtime families are present:

| Family | Purpose | Primary locations | Overall state | Coverage summary |
| --- | --- | --- | --- | --- |
| CORDIS shared runtime | Locality routing, recipient resolution, deduplication, notifications, diagnostics | `source/core/addons/CORDIS` | Implemented, with reserved bootstrap files | **REVIEWED / REFINE BEFORE COVERAGE**; trust, result, and key semantics remain undecided |
| Advanced Systems | Vehicle protection, artillery sensing, area interception | `source/advanced-systems/addons/AdvSys` | Implemented, mixed maturity | **PARTIALLY COVERED**; APS, Counter Battery Radar, and Iron Dome strong; APS anti-drone remains uncovered |
| Vigil support tablet | UI and rotary, artillery, fixed-wing, logistics, designation workflows | `source/visual-support-tablet/addons/VIGIL` | Implemented, with explicit recon/UAV gaps | **PARTIALLY COVERED**; major operational paths strong |
| Field Utilities | Fabrication, logistics, bridges, towing, FPV modifications | `source/field-utilities/addons/FieldUtils` | Implemented, mixed maturity | **PARTIALLY COVERED** through fixed-wing logistics and the reviewed Bridge Builder core |
| Cross-mod composition | Contracts joining CORDIS, Vigil, Field Utilities, ACE/CBA, and editor/Zeus surfaces | calls across all addons/configs | Implemented, some optional/degraded paths | **PARTIALLY COVERED**; one composite path direct, most incidental |

Tribunal/Pontifex validation is documented separately below. It is substantial
repository architecture, but is not counted as a shipped product family.

## 1. CORDIS shared runtime

CORDIS is the common operational runtime, not standalone gameplay. Primary
locations are `source/core/addons/CORDIS/config.cpp` and `functions/`.

### 1.1 Authority-aware execution

* **Server routing** calls a named function locally on the server or sends it to
  owner `2`. **Implemented; REVIEWED / REFINE BEFORE COVERAGE.** Routing is not
  an authorization or completion boundary.
* **Object-owner routing** executes on the machine local to a projectile,
  vehicle, UAV, or cargo object. **Implemented; REVIEWED / NEEDS
  EXPERIMENTATION.** APS, Vigil strike, FPV actions, and towing consume it;
  migration and terminal acknowledgment remain unproven.
* **Group-owner routing** targets `groupOwner`, but the local shortcut tests the
  unit instead of the group. **Implemented; REVIEWED / NEEDS EXPERIMENTATION.**
* **Once-only routed execution** combines routes with server TTL keys.
  **Implemented; REVIEWED / REFINE BEFORE COVERAGE.** Raw global keys may be
  consumed before missing or undeliverable work; success does not prove
  execution. Vigil's own guards do not prove the CORDIS contract.

The completed review separates locality from authorization and result meaning;
see [`core-cordis-review.md`](core-cordis-review.md).

### 1.2 Deduplication and fan-out

* **Server/local TTL caches** claim and prune once keys. **Implemented; REVIEWED
  / REFINE BEFORE COVERAGE.** Key namespace and failed-delivery semantics need
  product decisions.
* **Recipient resolution** handles all players, a side, a player object, or a
  list while filtering dead/non-player units. **Implemented; REVIEWED / NEEDS
  EXPERIMENTATION.** Headless/JIP policy and heterogeneous input are unproven.
* **Scoped emit** performs server-deduplicated dispatch to resolved recipients.
  **Implemented; REVIEWED / REFINE BEFORE COVERAGE.** It claims before target
  resolution; curator notification broadens every empty scope to broadcast.

### 1.3 Feedback, diagnostics, and bootstrap

* **Side chat/radio** provide setting-aware scoped messages, speaker
  normalization, and `CfgRadio` lookup. **Implemented; REVIEWED / NEEDS
  EXPERIMENTATION.** Audio is unproven under autonomous `-noSound` clients.
* **Curator notifications** and **debug logging** provide deduplicated hints and
  server-normalized logs/optional `systemChat`. **Implemented; REVIEWED / REFINE
  BEFORE COVERAGE.** Empty scoped curator targets currently broadcast globally.
* **Server cache initialization** and **client initialized marker** are
  implemented and incidentally smoke-covered, not feature contracts.
* `fn_initSettings.sqf` and `fn_utils.sqf` contain no behavior. **Scaffolded;
  UNKNOWN.** Do not test them unless a public capability is added.

## 2. Advanced Systems

Primary locations: `source/advanced-systems/addons/AdvSys/config.cpp` and
`functions/{aps,cbr,iron_dome}`. Dependencies: CORDIS, CBA, ACE interaction,
and Arma vehicle/projectile locality.

### 2.1 LORICA Active Protection System

The permanent `aps-intercept` scenario proves causal hard/soft outcomes, exact
tracked threats, disabled/outside/away controls, resource consumption,
locality, and client replication.

#### 2.1.1 Threat acquisition and arbitration

* **Local discovery/tracking** uses CBA Fired class handlers and a local
  per-frame projectile set. **Implemented; COVERED as part of APS**, although
  handler names/cadence are not specification.
* **Threat predicate** rejects untrackable, disabled, non-closing, excessive-
  TTI, off-bearing, or miss-distance threats. **Implemented; COVERED.**
* **Response selection** chooses charged hard kill, then fuel-backed soft kill.
  **Implemented; COVERED.** Private selection mechanics remain replaceable.
* **Authoritative ledger/deduplication** correlates vehicle/projectile/mode and
  prevents duplicate consumption. **Implemented; PARTIALLY COVERED.** Exact
  identities are evidence; ledger representation is not contract.

#### 2.1.2 Hard kill

* **Interception** stops/deletes the exact inbound projectile before impact.
  **Implemented; COVERED** with identity, neutralization, no-impact, and
  protected-outcome evidence.
* **Charge inventory/fallback** counts, tops up, consumes one, and transitions
  offline/fallback on depletion. **Implemented; COVERED for consumption and
  fallback outcome.** Every inventory class is not specified.
* **Disabled control** lets the same threat impact without engagement or
  consumption. **Implemented; COVERED.**

#### 2.1.3 Soft kill

* **Deflection** changes the same live tracked projectile's velocity without
  deleting it. **Implemented; COVERED** with pre/post velocity, survival,
  trajectory, no impact, and ledger correlation.
* **Fuel resource** consumes the configured amount and disables on insufficient
  power. **Implemented; COVERED for one successful decrement/result;** broader
  threshold/status behavior is not direct coverage.

#### 2.1.4 Installation, controls, and feedback

* **Eden synchronized enable module** and **Zeus per-vehicle toggle** install or
  toggle APS. **Implemented; PARTIALLY COVERED** for API state, but real module/
  curator activation and invalid selection are **NOT YET REVIEWED**.
* **Enable/disable lifecycle** initializes resources/runtime, publishes state,
  starts/stops drone work, and registers/removes actions. **Implemented;
  PARTIALLY COVERED.** Combat outcomes are direct; JIP/action cleanup is not.
* **ACE menu** provides hard-kill off/reboot, soft-kill on/off, status, voice,
  and anti-drone actions. **Implemented; NOT YET REVIEWED.** It needs the future
  real ACE interaction adapter.
* **Beam/particle animation** and **voice/status sequences** expose engagement,
  charge, fuel, and errors. **Implemented; NOT YET REVIEWED.** The scenario
  proves world outcome, not rendering or audible playback.

#### 2.1.5 Experimental anti-drone

Detects nearby fast sub-1000 kg airborne UAVs, consumes soft-kill fuel,
destroys the UAV, schedules cleanup, and exposes ACE controls/status.
**Implemented; REVIEWED / DEFERRED pending product decisions and refinement.**
The review found undefined threat/side/operator policy, a split owner-routed
resource transaction, destructive mutation without an owner acknowledgment,
unscoped event-handler removal, and caller-trusting ACE endpoints. It remains
outside projectile APS coverage. See
[`advanced-systems-aps-anti-drone-review.md`](advanced-systems-aps-anti-drone-review.md).

### 2.2 Counter Battery Radar

The permanent `advsys-counter-battery-radar` scenario proves enabled detection,
ground-accurate impact prediction, zone/icon markers, origin narrowing and
confirmation, the side-filtered launch warning, expiry, replication, locality,
and the disabled and stop controls.

* **Artillery detection/prediction** assigns shell UIDs, tracks airborne rounds,
  projects fall time/position, and sends owner-local updates serverward.
  **Implemented; COVERED.** Prediction previously integrated to sea level and was
  refined to resolve the ground under the projected point; per-shell predicted
  versus real impact is now asserted. The integration mechanism is not contract.
* **Impact clustering/warnings** groups predictions, updates red zone/count/ETA
  markers, warns by side, and prunes expiry. **Implemented; COVERED** for one
  launcher. The zone label is asserted against the product's own count and
  remaining time, and every warning claim travels the real launch pipeline with
  real hostile-far and friendly-near negative controls, including the
  once-per-airborne-cycle rule. Multi-launcher and multi-cluster arbitration are
  **NOT YET REVIEWED**.
* **Origin estimation** narrows repeated launch origins into a search marker.
  **Implemented; COVERED** for narrowing and confirmation at the real gun
  position. Confirmed-origin persistence is **REVIEWED / DEFERRED** pending a
  product decision.
* **Marker sharing policy** publishes zone and origin markers globally while the
  radio warning is side-filtered. **Implemented; REVIEWED / DEFERRED** as an open
  product decision; no test asserts a preferred answer.
* **Eden enable / Zeus toggle** start, stop, reset, and report the system.
  **Implemented; PARTIALLY COVERED.** The start/stop lifecycle is directly
  covered through the API; real module and curator activation are **NOT YET
  REVIEWED**.

Full analysis:
[`advanced-systems-counter-battery-radar-review.md`](advanced-systems-counter-battery-radar-review.md).

### 2.3 OPHANIM / Iron Dome

* **Launcher asset/registry** registers enabled `YAS_OPHANIM_box` instances.
  **REVIEWED / REFINE BEFORE PERMANENT COVERAGE (refined; covered).** The
  server initializes it every run and rejects client-originated internal
  registration calls.
* **Shell tasks/assignment** deduplicate threats, select in-range launchers,
  schedule launcher spacing, and retry within shot limits. **REVIEWED / REFINE
  BEFORE PERMANENT COVERAGE (refined; covered).** Distinct concurrent threats
  are proven and exhausted work now retires after active monitors finish.
* **Interceptor/terminal monitoring** creates a Jian missile, guides/monitors
  it, detonates near the shell, and records retry/end reasons. **REVIEWED /
  SPECIFICATION COVERED.** A same-native-threat A/B proves disabled impact and
  exact enabled interception with an independently sampled physical missile.
* **Range setting/launch audio** expose CBA configuration and randomized sound.
  **PARTIALLY REVIEWED.** The out-of-range physical control is covered; audible
  output remains unproven because autonomous clients use `-noSound`.

Permanent scenario: `advsys-iron-dome`.  Full analysis:
[`advanced-systems-iron-dome-review.md`](advanced-systems-iron-dome-review.md).

### 2.4 Common Advanced Systems utilities

Beam effects, positional helpers, server `say3D`, number-to-voice tokenization,
and CORDIS-backed debug/radio/curator wrappers are **implemented; NOT YET
REVIEWED standalone**. Review only when a consumer establishes user-visible
behavior.

## 3. Vigil support tablet

Primary locations: `source/visual-support-tablet/addons/VIGIL/config.cpp`,
`ui/`, and `functions/`. Vigil depends on CORDIS/CBA and optionally Field
Utilities for fixed-wing airdrop.

### 3.1 Tablet access, shell, and navigation

* **Items/access rule/keybind** provide three side terminal variants, optional
  tablet requirement, and Ctrl+Home open. **Implemented; PARTIALLY COVERED.**
  `vigil-ui` proves the BLU path; side variants, rejection, and override are not.
* **Open/theme/intro/close/reopen** selects skin/colors, initializes, cleans up,
  and resets. **Implemented; COVERED** with real input/framebuffer/locality.
* **Tabbed navigation** registers Home, Assets, and task views. **Implemented;
  PARTIALLY COVERED.** Visible artillery navigation is direct, not every page.
* **Homepage task management** is **REVIEWED / DEFERRED.** Its page and
  registration are commented out; the client renderer rejects the server-local
  manager shape; cancellation has no authoritative request or correct
  finalization; visibility/authority/history policy is undecided. See
  [`vigil-homepage-task-management-review.md`](vigil-homepage-task-management-review.md).

### 3.2 Asset discovery and whitelist

* **Live asset browser** discovers friendly manned assets, classifies artillery,
  rotary CAS, transport, fixed-wing/recon, and renders status/actions.
  **Implemented; PARTIALLY COVERED.** Fixtures prove specific eligibility, not
  mixed-fleet refresh/presentation.
* **Eden whitelist** restricts the source to synchronized objects; **Zeus toggle**
  adds/removes a selected object. **Implemented; NOT YET REVIEWED.**

### 3.3 Coordinates, vehicle tasking, and governor

* Grid parse/format, map clicks/previews, nearest helipad, waypoints, hard stop/
  AI reboot, engine/landing mode, and safe/transit AI presets are **implemented;
  PARTIALLY COVERED** through artillery/flight outcomes. Helpers are replaceable.
* The **task governor** manages vehicle-keyed init/start/mission/end/finally
  stages, outcomes, stale retries, cancellation, completion, and a CBA
  dispatcher. **Implemented; PARTIALLY COVERED.** Transport/artillery/CAS prove
  several success, duplicate, bounded failure, and cleanup outcomes, but no
  independent governor contract exists.

### 3.4 Artillery and VLS

* **Request UI/preview markers** render grid/ordnance/spread/count/direction and
  circle/line state client-locally. **Implemented; COVERED** by `vigil-markers`
  for updates, stale replacement, rendering, locality, and cleanup.
* **Native artillery execution** fires exact physical circle/line counts and
  rejects zero, out-of-range, and no-ammo requests. **Implemented; COVERED** by
  `vigil-artillery` for authority, trajectories, geometry, locality, and cleanup.
* **VLS execution** launches vertically, guides, and reaches the target region.
  **Implemented; COVERED.** Its target-report handshake is **REVIEWED / NEEDS
  EXPERIMENTATION** because no retained A/B proves it engine-required.

### 3.5 Helicopter transport / reinsertion

* **Eligibility/request** captures destination, altitude, ignore-enemy, and
  do-not-climb state. **Implemented; PARTIALLY COVERED.** Eligibility/locality is
  direct; the latter option semantics are not explicit assertions.
* **Outbound/LZ/landing/wait** dispatches once, rejects duplicates, and reaches/
  settles at the LZ. **Implemented; COVERED** by `vigil-transport`.
* **RTB/reinsertion** returns to recorded home, settles, and cleans resources.
  **Implemented; COVERED.** Reinsertion is not a separate implementation.
* Hidden-pad plus `land "LAND"` is **REVIEWED / NEEDS EXPERIMENTATION** as a
  characterization candidate; visible landing is covered without freezing it.

### 3.6 Rotary-wing CAS

* **Dispatch/area/timer/RTB** validates crewed armed aircraft, rejects duplicate/
  unavailable requests, transits on-station, disengages, and returns.
  **Implemented; COVERED** by `vigil-cas`.
* **Target/combat selection** filters hostile ground targets to area, excludes
  friendly/neutral/outside controls, selects real ammunition, and correlates
  fire/projectile/impact plus no-target/no-ammo controls. **Implemented;
  COVERED.** Sensor/reveal dependence is **REVIEWED / NEEDS EXPERIMENTATION**.
* **Combat RTB reset** (reboot plus fresh MOVE) is an evidence-backed engine
  characterization. **COVERED / CHARACTERIZED.**

### 3.7 Fixed-wing shared lifecycle

* **Editor/Zeus registration** configures asset, ingress, exfil, and Zeus add.
  **Implemented; PARTIALLY COVERED.** Direct API registration is covered; real
  module activation is not.
* **Snapshot serialization** retains class, side, crew, fuel, damage, pylons,
  ammunition, role, and points while deleting the source and publishing a
  sanitized registry. **Implemented; COVERED for strike/logistics state.** Exact
  schema is not contract.
* **Deploy/reconstruct/loiter** and **bounded RTB/egress** create one server-owned
  aircraft/crew, restore state, enter operating space, then record outcome and
  clean resources while retaining registration. **Implemented; COVERED** for
  strike/logistics.
* **Fixed-wing UAV deploy** is rejected by an explicit unstable guard. The
  authoritative endpoint now binds the requesting player and rejects the
  stored UAV class before registry/world mutation; a direct client bypass and
  manned positive control are permanent coverage. **Disabled; ACCEPTED /
  COVERED for rejection.** Physical UAV reconstruction remains **REVIEWED /
  NEEDS EXPERIMENTATION**. See
  [the boundary review](vigil-fixed-wing-uav-deploy-review.md).

### 3.8 Fixed-wing strike

* **Payload selection/guards**, **normal laser designation**, and **weapon IR
  designation** produce two exact guided munitions, effects, repeat use,
  no-designation rejection, and cleanup. **Implemented; COVERED** by
  `vigil-fixed-wing`.
* **IR helper** creates/cleans a side-correct fake laser target. Designation is
  covered; beam rendering/color/compatibility are **PARTIALLY COVERED**.
* **3CB Hellfire mapping** has no qualifying installed pylon row for comparison.
  **Implemented-looking; REVIEWED / NEEDS EXPERIMENTATION.**
* `fn_fwLaserTest.sqf` is substantial preInit developer diagnostics with no
  normal product action. **REVIEWED / DEFERRED.** It bypasses the accepted
  strike pipeline and exposes unbounded destructive execution/result storage;
  remove, relocate, or capability-gate it before supported use.

Full analysis: [`vigil-developer-laser-harness-review.md`](vigil-developer-laser-harness-review.md).

### 3.9 Fixed-wing logistics / aerial delivery

* **Vigil-to-Fabricator order** opens Field Utilities with aircraft/grid/airdrop
  context and rejects empty/concurrent orders. **Implemented; COVERED** by
  `vigil-fixed-wing-logistics` as a composite feature.
* **Manifest/authority transfer** expands/packs objects, transfers them
  serverward, and preserves weapon/magazine/item/backpack contents.
  **Implemented; COVERED for this path.** General Fabricator use is not.
* **Ingress/release/parachute/descent/landing** releases exact cargo, lands it
  intact/accurately, replicates outcome, and egresses/cleans up. **Implemented;
  COVERED.**
* **Capacity/weight limits** do not exist. **Absent; REVIEWED / DEFERRED.**

### 3.10 Reconnaissance

* **RECON role bit/label** is **scaffolded; REVIEWED / DEFERRED** because
  semantics are undefined.
* **Grid/altitude/radius form state** is **scaffolded/unreachable; REVIEWED /
  DEFERRED**: no reachable tab/submit and `fn_recon_task.sqf` is empty.
* **Task, sensors, contacts/imagery/report, persistence, cleanup, replication/**
  **JIP** are absent and **REVIEWED / DEFERRED**. Define the information product
  and lifecycle first.

### 3.11 Other Vigil support systems

* **Helicopter stabilization** has sampling/force code, but aircraft registration
  is commented out. **Disabled/unreachable; UNKNOWN.** Review intent first.
* **Radio/chat/debug/curator feedback** wraps CORDIS. **Implemented; NOT YET
  REVIEWED.** Task state does not prove visible/audible feedback.

## 4. Field Utilities

Primary locations: `source/field-utilities/addons/FieldUtils/config.cpp`,
`functions/`, and `ui/`. Dependencies: CORDIS, CBA, ACE, ZEN, optionally Vigil.

### 4.1 Virtual Storage and Fabricator

Reviewed in [`field-utilities-fabricator-review.md`](field-utilities-fabricator-review.md);
primary outcome **REFINE BEFORE PERMANENT COVERAGE**; refinement is complete and
the feature is now **COVERED** by `fieldutils-fabricator`. Orders are
server-authoritative and atomic, the catalogue is an unlimited template source,
and the local virtual-inventory toggle is restored. Active owner cancellation
terminates the transaction worker before rollback and retirement. The delivery
mass cap is preserved but could not be validated at runtime and is asserted by
nothing - see the review.

* **Mission-maker registration** uses synchronized storage objects and designated
  Fabricator stations, optionally with nearby ZEN inventory. **Implemented;
  REVIEWED / KEEP AS-IS AND SPEC-TEST.** Module setters run server-side and
  publish both logics. Server ownership is proven; actual JIP and client-visible
  runtime synchronization are not.
* **Fabricator UI/queue** lists assets/images/quantities, ordered queue, grid,
  progress, success/failure, and may reuse Vigil skins. **Implemented; PARTIALLY
  COVERED.** Airdrop context/manifest/result is covered; normal browsing, local
  orders, invalid grids, and styling are not. The progress bar is cosmetic — all
  work completes before it starts — so no contract may promise it tracks work.
* **Single-item fabrication** clones one stored object near the player on the
  server.
  **Implemented; REVIEWED / KEEP AS-IS AND SPEC-TEST.** `YOSHI_SPAWN_SAVED_ITEM_ACTION`
  is the live clone primitive for both delivery modes and copies weapon, magazine,
  item and backpack cargo exactly. The separate `YOSHI_addItemsToFabricator` is
  **unreachable repository-wide**; it is recorded, not deleted, because it is
  globally named and may be a mission-maker entry point.
* **Multi-item packing** clones objects, computes bounds/orientations, packs
  containers/pallets, preserves inventory, and delivers locally. **Implemented;
  REVIEWED / REFINED.** It reported success while silently dropping items too
  large for any container and orphaning their clones under the map. The packer now
  returns the skipped objects and succeeds only when nothing was skipped; the
  caller deletes anything unpacked and the order is refused.
* **Local virtual-inventory toggle** (`Fabricator_Module_EnableLocalArsenal`) gates
  the ZEN inventory action used to add stock that was never synchronized. The
  module setter now publishes it and the action condition honours it, default
  enabled. **Implemented; REVIEWED / REFINED.**
* **Order authority** is server-authoritative through one order endpoint plus an
  owner-bound discard endpoint.
  Identity comes from `remoteExecutedOwner`; internal helpers are gated on an
  unpublished per-machine token; transaction state is keyed `owner#request` for
  claim, result, ledger, discard and retirement; orders are atomic with a
  watchdog finalizer scoped to the transaction's own objects. **Implemented;
  COVERED**, including exact server receipts for worker/accept bypass, replay,
  registry mutation and foreign discard; malformed/oversized refusals; watchdog
  worker termination plus rollback after creation; and bounded result retirement.
* **Airdrop authorization** is server-side and delegated to Vigil's shared
  validator. The exact aircraft must be alive, registered/on-station, LOGI-role,
  same-side, and not already busy. Vigil registry mutation has its own private
  capability boundary. **Implemented; COVERED for one authenticated client.**
* **Delivery placement** is contracted only as *server-owned delivery within a
  bounded distance of the recipient*. Terrain/water/obstruction suitability is
  **REVIEWED / NEEDS EXPERIMENTATION**; the earlier `surfaceIsWater` failure was
  caused by the fixture spawning at the map origin over water, not by the world.
* **Airdrop handoff** calls Vigil delivery and observes authoritative parachute
  results. **Implemented; COVERED as a cross-mod composite.** Missing API fails
  closed.

### 4.2 Bridge Builder

* **Construction box/ACE entry** exposes “Open Bridge Builder.” **Implemented;
  COVERED.** The exact class action is registered and ACE's active tree proves
  its out-of-range, busy, and eligible states; the permanent feature proof then
  invokes that registered statement without per-feature VNC automation.
* **Planning UI** selects layout, ramp, orientation, clipping, counts, pitch,
  offsets, and auto calculation. **PARTIALLY COVERED.** Flat lengthwise manual
  planning is covered; wide/ramp/pitch/auto/clipping remain unreviewed.
* **Preview** computes/caches queues and renders validity colors. **Implemented;
  PARTIALLY COVERED.** Calibration captured the real rendered four-segment flat
  preview; permanent regression validates its exact planning state through
  data. Other modes remain unreviewed.
* **Build/removal** incrementally creates deduplicated segments with configured
  delay and removes chains. **COVERED for the reviewed flat contract.** Server
  authority, exact geometry/locality, physical traversal, box-scoped removal,
  bounded results and cleanup are proven; interruption/resources are not.
* **Direct chain-extension actions** coexist with plan UI. **Implemented-looking;
  DEFERRED.** Helpers exist but action attachment is empty and no supported
  intent/authority contract was established.

Full analysis: [`field-utilities-bridge-builder-review.md`](field-utilities-bridge-builder-review.md).

### 4.3 Logistics and object handling

* **Automatic pallet/container handling** makes pallets draggable/carryable and
  adds a server-installed box contact/attachment hook. **REVIEWED / REFINE
  BEFORE PERMANENT COVERAGE.** Contact locality, eligible surfaces, ownership,
  detach, and cleanup are undefined.
* **Nearby supply actions** expose eligible nearby carriers through ACE.
  **REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** The client invokes
  `setVehicleCargo` without authority or result handling; exact replicated
  cargo membership is unproven.
* **Safe-fall/fling/attach helpers** support delivery/packing. **Implemented;
  PARTIALLY COVERED** only in fixed-wing cargo.

Full analysis: [`field-utilities-object-handling-review.md`](field-utilities-object-handling-review.md).

### 4.4 Towing and sling ropes

* **Tow points/rope deployment** use configured or geometry-derived points and
  owner-local tow parent. **REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** The
  actor client creates ropes, discards their handles, and only owner-routes the
  parent mutation; authority, atomicity, and terminal cleanup are unresolved.
* **ACE tow/stow actions** are registered on vehicles. **REVIEWED / REFINE
  BEFORE PERMANENT COVERAGE.** The path is reachable, but stow can destroy
  unrelated ropes and physical towing has no controlled causal proof.
* **Four-point helicopter sling helper** is **REVIEWED / DEFERRED**. It is a
  compiled orphan with no supported caller; it destroys all helicopter ropes
  before non-atomic local creation and has no authority/cleanup contract.

Full analysis: [`field-utilities-towing-review.md`](field-utilities-towing-review.md).
Sling analysis: [`field-utilities-helicopter-sling-review.md`](field-utilities-helicopter-sling-review.md).

### 4.5 FPV/UAV field modifications

* **Small-UAV profile** adds owner-local engine attach/detach, drag/carry, fuel,
  and camouflage behavior. **REVIEWED / NEEDS EXPERIMENTATION.** Owner-local
  routing exists, but completion and owner/non-owner behavior are unproven.
* **IED payload** attaches/detonates a charge and creates effects on UAV death.
  **REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** Destructive functions do not
  revalidate the requester at the owner; collateral causality is unproven.
* **Mortar/grenade payloads** grant finite counts, create physical ordnance, and
  decrement counts. **REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** Direct
  calls can release absent/depleted payloads and underflow counts; physical
  impact, duplicate, and ownership controls are unproven.
* **Click/shuffle feedback** is **implemented; NOT YET REVIEWED**; audio unproven.

Full analysis: [`field-utilities-fpv-review.md`](field-utilities-fpv-review.md).

### 4.6 Shared libraries

* **Geometry/packing primitives** provide bounds, transforms, lift corners,
  orientations, and placement. **Implemented; PARTIALLY COVERED incidentally**
  by logistics, not standalone specification.
* **ID/location marker helpers** are **REVIEWED / DEFERRED**: compiled global
  scaffold with no normal caller; authority, visibility, labels, and cleanup
  have no product contract.
* **Airdrop direction/ETA feedback** is **REVIEWED / NEEDS PRODUCT DECISION AND
  EXPERIMENTATION**. The live client announcement uses target-to-aircraft
  bearing and altitude-only vacuum fall time at acceptance, which does not model
  ingress or parachute descent.
* **Sound, global ACE registration, debug/chat wrappers** are **implemented; NOT
  YET REVIEWED.** Current callers remain; do not label them dead.

Full analysis: [`field-utilities-map-helpers-review.md`](field-utilities-map-helpers-review.md).

## 5. Cross-mod composition and integration

### 5.1 CORDIS consumer contract

All feature addons declare CORDIS and use authority, dedupe, feedback, or
logging. **Implemented; PARTIALLY COVERED incidentally.** APS/Vigil multiplayer
success proves use, but no scenario promises CORDIS behavior across owners,
sides, JIP, disconnects, or multiple clients.

### 5.2 Vigil–Field Utilities logistics bridge

Vigil invokes Fabricator UI; Field Utilities packages manifests and calls
Vigil's authoritative request; Vigil calls Field Utilities parachute mechanics
and returns one result. **Implemented; COVERED** for reviewed fixed-wing
airdrop. General fabrication is outside the contract.

### 5.3 Shared UI and interaction

* Field Utilities reuses Vigil display/terminal skins while keeping separate
  state. **Implemented; PARTIALLY COVERED incidentally** by logistics. Nested
  lifecycle, styling, and use without Vigil are not reviewed.
* APS and Field Utilities register many ACE object/class actions. **Implemented;
  NOT YET REVIEWED as a suite boundary.** No product scenario proves real
  ACE-menu availability/activation.

### 5.4 Eden/Zeus and CBA configuration

* APS/CBR, whitelist, fixed-wing points/assets, Virtual Storage, and Fabricator
  Eden modules plus Zeus tools are **implemented; NOT YET REVIEWED**. Scenarios
  call APIs directly, not real synchronization/curator paths.
* CBA startup/settings cover access, feedback, colors, timing, and range.
  **Implemented; PARTIALLY COVERED incidentally.** Cold init is proven, not each
  default/scope/change/combination.

### 5.5 State, serialization, and persistence

* Replicated object/mission variables carry APS, task, registry, cargo-result,
  whitelist, and config state. **Implemented; PARTIALLY COVERED** by one-client
  replication scenarios.
* No durable campaign/database persistence exists in the four mods.
* **JIP/multi-client semantics** are **NOT YET REVIEWED**. One authenticated
  client is the proof boundary; future identities are architecture, not proof.

## Validation architecture (not a product family)

Tribunal owns mission/PBO construction, discovery, contracts/reviews, generic
projectile/artillery/aviation/combat/delivery/designation/locality/visual
evidence, fail-closed assertions, artifacts, and terminal lifecycle. Pontifex
owns builds, Steam/Proton/server runtime, private network/security, Live Mode,
and feature scenarios. Locations include `tribunal/`, `tools/`, and
`source/*/tests/tribunal`.

Permanent feature scenarios discovered by the runtime adapter are:

| Scenario | Reviewed behavior |
| --- | --- |
| `aps-intercept` | APS hard/soft kill, controls, locality, resources, replication |
| `vigil-ui` | real tablet open/navigation/close/reopen and UI locality |
| `vigil-markers` | artillery preview rendering/state lifecycle and cleanup |
| `vigil-artillery` | circle/line artillery, controls, VLS, locality/cleanup |
| `vigil-transport` | helicopter outbound/LZ/wait/RTB lifecycle |
| `vigil-cas` | rotary CAS filtering, attack, timer, controls, RTB |
| `vigil-fixed-wing` | registry/reconstruction, two designation strikes, control, egress |
| `vigil-fixed-wing-logistics` | manifest airdrop, parachute/landing/inventory, egress |
| `fieldutils-fabricator` | server-authoritative atomic orders, catalogue fidelity, refusals, cleanup |
| `advsys-counter-battery-radar` | artillery detection, impact prediction/zone, origin fix, side warning, lifecycle |

Framework `locality-probe` and `visual-framebuffer` scenarios prove Tribunal,
not product features. Promote generic backlog mechanics only for a concrete
consumer.

The project manifest and Pontifex runtime now discover the same feature scenario
set across Advanced Systems, Field Utilities, and Vigil. A regression compares
their independently loaded identifiers so future manifest drift fails closed.

## Deferred, incomplete, disabled, and unclear areas

| Area | Classification | Repository-grounded reason |
| --- | --- | --- |
| Vigil homepage task management | **REVIEWED / DEFERRED** | unreachable commented page; incompatible client/server data shape and no authoritative cancellation contract |
| Vigil reconnaissance | **REVIEWED / DEFERRED** | role/state only; unreachable form, no submit, empty task, no sensor/output/lifecycle |
| Fixed-wing UAV deploy | **REVIEWED / NEEDS EXPERIMENTATION** | explicitly rejected as unstable |
| Helicopter stabilizer | **REVIEWED / NEEDS EXPERIMENTATION** | transport/RTB enrolls by default and retained runs reach the force path; matched flight causality, safety, and cancellation cleanup unproven |
| 3CB Hellfire mapping | **REVIEWED / NEEDS EXPERIMENTATION** | no compatible installed pylon row for A/B |
| VLS target handshake | **REVIEWED / NEEDS EXPERIMENTATION** | physical outcome covered; internal necessity unproven |
| Transport hidden-pad landing | **REVIEWED / NEEDS EXPERIMENTATION** | landing works; exact mechanism necessity unproven |
| Developer laser harness | **REVIEWED / DEFERRED** | unreachable preInit diagnostic; destructive owner-routed run and unbounded client-supplied result store lack a product boundary |
| APS anti-drone | **REVIEWED / DEFERRED** | threat/side/operator policy is undecided; resource authority and destructive cleanup require refinement before coverage |
| CBR marker sharing policy | **REVIEWED / DEFERRED** | zone/origin markers are global while the radio warning is side-filtered |
| CBR confirmed-origin persistence | **REVIEWED / DEFERRED** | confirmed fix never expires; decay policy undecided |
| CBR warning coverage | **REVIEWED / DEFERRED** | one warning per firing machine per airborne cycle, on the first round only, at a fixed 1000 m radius; re-warning for a walking barrage undecided |
| CBR module/Zeus activation | **REVIEWED / REFINE BEFORE COVERAGE** | real framework dispatch/locality and curator authority need one controlled module-path experiment |
| Iron Dome client-owned artillery | **REVIEWED / DEFERRED** | current server handler deliberately rejects non-server-local shells; no owner-routing product policy is chosen |
| Iron Dome threat policy/audio | **REVIEWED / DEFERRED** | friendly/outgoing versus protected-impact-area filtering is undecided; audio is unproven under `-noSound` |
| Fabricator delivery mass cap | **REVIEWED / OPEN DEFECT** | a fabricated crate reported `getMass = 1e-12` across six runs, so the carryability cap never fires; those runs were over water and it has not been re-measured on land |
| Fabricator placement suitability | **REVIEWED / NEEDS EXPERIMENTATION** | delivery is bounded to the recipient; water/gradient/obstruction unproven |
| Fabricator client-b discard | **NOT YET PROVEN** | one authenticated client; the foreign-discard control uses a server-owned transaction |
| Fabricator staging depths | **REVIEWED / NEEDS EXPERIMENTATION** | underground staging and the settle tick have no retained controlled alternative |
| Field towing | **REVIEWED / REFINE BEFORE COVERAGE** | client-owned, non-atomic rope lifecycle; exact physical/locality A/B and product policy required |
| Field object handling / supply loading | **REVIEWED / REFINE BEFORE COVERAGE** | contact attachment and explicit cargo loading conflate locality-sensitive paths without authority, exact result, or cleanup |
| Field ID/location markers | **REVIEWED / DEFERRED** | no product caller; global marker authority/lifetime/cleanup undefined |
| Field airdrop direction/ETA | **REVIEWED / NEEDS PRODUCT DECISION AND EXPERIMENTATION** | direction/audience/ETA interval undefined; current fall formula omits ingress and parachute descent |
| Helicopter sling helper | **REVIEWED / DEFERRED** | compiled orphan; destructive all-rope stow, non-atomic creation, no supported entry/authority/cleanup |
| Bridge direct extension | **DEFERRED** | helpers exist, but no reachable action or supported ownership contract was established |
| Core settings/utils files | **Scaffolded / UNKNOWN** | reserved files contain no behavior |
| Multi-client/JIP | **NOT YET REVIEWED** | one authenticated-client proof boundary |

## Prioritized next feature reviews

1. **Vigil fixed-wing UAV disabled guard.** The UI rejects UAV deployment but
   the authoritative deploy endpoint lacks the same guard.

Then consider the reviewed CBR module experiment, APS module activation, the
reviewed-but-uncovered CORDIS decision matrix, suite editor/Zeus modules, and
the helicopter stabilizer. APS anti-drone is now
reviewed but deferred at the product-decision and authority/refinement boundary
recorded in its review. Do not resume reconnaissance until the product
decisions in `vigil-fixed-wing-recon-review.md` are answered, and do not resume
CBR marker scoping or confirmed-origin persistence until the product decisions
in `advanced-systems-counter-battery-radar-review.md` are answered. Fabricator's
product decisions are resolved and its accepted one-client contract is covered;
its remaining experiments are listed in the backlog above.
FPV/UAV refinement and its unresolved product choices are recorded in
`field-utilities-fpv-review.md`; do not invent those policies during coverage.

## Evidence sources

This inventory was derived from all four addon configs/function trees and
`UPSTREAM_README.md` files; feature scenarios and `ScenarioReview` metadata;
and durable reviews in this directory. Testing distinctions remain in
[`testing-methodology.md`](testing-methodology.md), with runtime/tool ownership
in [`architecture.md`](architecture.md).
