# Pontifex feature inventory

This is a repository-grounded map of the Pontifex runtime at commit `a55d2d1`.
It is an inventory, not a roadmap or a promise that every source surface is
intended to survive. It records what exists so later reviews can choose stable
behavioral contracts before permanent Tribunal coverage is added.

Reviews selected from this inventory follow Tribunal's
[`feature-review-program.md`](feature-review-program.md). A completed review
updates the affected inventory status; the inventory itself does not invent or
establish product semantics.

Author decisions that resolve review questions are recorded in
[`product-decisions-2026-08-20.md`](product-decisions-2026-08-20.md) and must be
read with the applicable feature review.

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
| CORDIS shared runtime | Locality routing, recipient resolution, deduplication, notifications, diagnostics | `source/core/addons/CORDIS` | Refined, with reserved bootstrap files | **ACCEPTED / COVERED** for the one-client trusted broker; GUI/audio/debug and client-N/JIP remain deferred |
| Advanced Systems | Vehicle protection, artillery sensing, area interception | `source/advanced-systems/addons/AdvSys` | Implemented, mixed maturity | **PARTIALLY COVERED**; APS, Counter Battery Radar, and Iron Dome strong; APS anti-drone remains uncovered |
| Vigil support tablet | UI and rotary, artillery, fixed-wing, logistics, designation workflows | `source/visual-support-tablet/addons/VIGIL` | Implemented, with explicit recon/UAV gaps | **PARTIALLY COVERED**; major operational paths strong |
| Field Utilities | Fabrication, logistics, bridges, towing, FPV modifications | `source/field-utilities/addons/FieldUtils` | Implemented, mixed maturity | **PARTIALLY COVERED** through fabrication, logistics, Bridge Builder, and accepted authoritative physical towing |
| Cross-mod composition | Contracts joining CORDIS, Vigil, Field Utilities, ACE/CBA, and editor/Zeus surfaces | calls across all addons/configs | Implemented, some optional/degraded paths | **PARTIALLY COVERED**; one composite path direct, most incidental |

Tribunal/Pontifex validation is documented separately below. It is substantial
repository architecture, but is not counted as a shipped product family.

## 1. CORDIS shared runtime

CORDIS is the common operational runtime, not standalone gameplay. Primary
locations are `source/core/addons/CORDIS/config.cpp` and `functions/`.

### 1.1 Authority-aware execution

* **Server, object-owner, and group-owner routing** are **REFINED; ACCEPTED /
  COVERED** for server plus one authenticated client. The server resolves
  nonlocal ownership; the local group shortcut checks group locality; exact
  destination callbacks record execution machine and transport origin.
* **Once-only routed execution** is **REFINED; ACCEPTED / COVERED** for trusted
  cooperating operations. Results distinguish rejected/queued/accepted/executed
  broker boundaries; operation-qualified positive-TTL keys are claimed only
  after validation. Routing remains neither authorization nor remote gameplay
  completion. Ownership migration, disconnect, and client-N/JIP remain deferred.

The completed review separates locality from authorization and result meaning;
see [`core-cordis-review.md`](core-cordis-review.md).

### 1.2 Deduplication and fan-out

* **Server/local TTL caches** are **REFINED; ACCEPTED / COVERED** for
  operation-aware positive TTLs, invalid-work non-claim, expiry reuse, and safe
  post-iteration pruning.
* **Recipient resolution and scoped emit** are **REFINED; ACCEPTED / COVERED**
  for live real-player global/side/object/list scopes with one authenticated
  client. Exact callbacks prove positive fan-out; duplicate, explicit-empty,
  wrong-side, dead/non-player, virtual, and headless candidates do not broaden
  delivery. Client-N/JIP audience behavior remains deferred.

### 1.3 Feedback, diagnostics, and bootstrap

* **Side chat/radio** provide setting-aware scoped messages, speaker
  normalization, and `CfgRadio` lookup. **Implemented; REVIEWED / NEEDS
  EXPERIMENTATION.** Audio is unproven under autonomous `-noSound` clients.
* **Curator notification recipient decisions** are **REFINED; ACCEPTED /
  COVERED** for live, explicit-empty, and wrong-side scopes; empty scopes no
  longer broaden to broadcast. Actual final BIS GUI presentation and debug
  `systemChat` remain **REVIEWED / DEFERRED AS PRESENTATION**.
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

* **Eden synchronized enable module** is **REFINED; ACCEPTED / COVERED**. Fresh autonomous proof uses two authentic typed modules with native Sync links, verifies server-local dispatch and retained non-disposable logic, rejects a forged client call, and causally proves two synchronized hard-kill interceptions against an unsynchronized same-threat physical-impact control. Multiple Eden modules aggregate.
* **Zeus per-vehicle activation** is **REFINED; ACCEPTED / COVERED** for one authentic assigned-curator placement. Fresh proof binds exact placer/curator/logic/target/operation identity, causally compares disabled impact with activated interception, targets feedback only to the placing owner, rejects replay and a forged request, and retires the disposable logic/claim. Reverse ON-to-OFF entry, repeated placement in one retained curator display, client-B/JIP isolation, and ownership migration remain deferred. See
  [`advanced-systems-aps-module-review.md`](advanced-systems-aps-module-review.md).
* **Enable/disable/re-enable lifecycle** is **REFINED; ACCEPTED / COVERED
  through the authentic current-client ACE control entry** for suspension/resume.
  First install alone initializes resources/defaults; suspension and resume are
  idempotent and preserve hard/soft mode, voice, anti-drone preference, charges,
  and fuel without resupply. Zeus toggle, ownership
  migration, and client-B/JIP remain separate. See
  [`advanced-systems-aps-lifecycle-review.md`](advanced-systems-aps-lifecycle-review.md).
* The **LORICA ACE control menu** is **REFINED; ACCEPTED / COVERED** for
  the current authenticated client and server-owned vehicle. The server derives
  requester identity from transport ownership, authorizes nearby players or
  driver/gunner/commander crew, revalidates transitions, rejects stale/replay/
  distant/unknown requests, and publishes correlated results. Exact active-node
  hard-off/reboot is causally tied to impact/interception; soft, voice, anti-drone
  preference, status, and suspend/resume transitions are covered. Client-B/JIP,
  ownership migration, and anti-drone threat semantics remain separate. See
  [`advanced-systems-aps-ace-controls-review.md`](advanced-systems-aps-ace-controls-review.md).
* **Beam/particle animation** is **REVIEWED / DEFERRED PENDING PRODUCT
  PRESENTATION DECISIONS**: the real engagement path reaches it, but particle creation is
  server-local on a dedicated server and beam concurrency/client rendering are
  unproven. **Audible voice/engagement sound** is **REVIEWED / DEFERRED** under
  `-noSound` pending audience/overlap policy and a sound-enabled observer.
  **Status facts/presentation** remain consumer-owned by the APS control review;
  accepted world state does not prove hint, beam, particle, or audio delivery.
  See
  [`advanced-systems-aps-presentation-review.md`](advanced-systems-aps-presentation-review.md).

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
  **REVIEWED / REFINE BEFORE PERMANENT COVERAGE; PRODUCT DECISIONS REQUIRED**.
  Warning cadence currently depends on firing-machine ownership, cluster
  assignment is fixed at first nearest-center selection, and owner-local launch/
  track endpoints accept unbound caller-authored telemetry. Choose grouping and
  warning semantics, bind updates to source owner/launcher, then prove same- and
  cross-owner close/far pairs, reverse-order invariance, independent origins/
  expiry, and forgery rejection. See
  [`advanced-systems-cbr-concurrency-review.md`](advanced-systems-cbr-concurrency-review.md).
* **Origin estimation** narrows repeated launch origins into a search marker.
  **Implemented; COVERED** for narrowing and confirmation at the real gun
  position. Confirmed-origin persistence is **REVIEWED / DEFERRED** pending a
  product decision.
* **Marker sharing policy** publishes zone and origin markers globally while the
  radio warning is side-filtered. **Implemented; REVIEWED / DEFERRED** as an open
  product decision; no test asserts a preferred answer.
* **Eden enable / Zeus toggle** is **REFINED; ACCEPTED / COVERED** for authentic
  server-local typed Eden dispatch and one authentic assigned-curator ON-to-OFF
  Zeus placement. Fresh run `20260821T153013Z-0a8b2c91` proved exact native
  entry, real-shell detection versus same-fixture disabled flight, replay and
  forgery rejection, placing-curator-only results, replication, retained Eden
  logic, transient own-logic cleanup and full teardown. Reverse-direction,
  repeated-display, client-B/JIP and ownership-migration cases remain bounded
  follow-ups. See
  [`advanced-systems-cbr-module-review.md`](advanced-systems-cbr-module-review.md).

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
and CORDIS-backed debug/radio/curator wrappers are **REVIEWED / DEFERRED AS A
STANDALONE FEATURE; CONSUMER-OWNED**. They have no independent product entry or
coherent standalone outcome. APS, CBR, Iron Dome, and module reviews own their
respective user-visible semantics; incidental helper execution does not
establish beam concurrency, audible output, or notification audience. Dead
marker/beam helpers remain unpromised. See
[`advanced-systems-common-utilities-review.md`](advanced-systems-common-utilities-review.md).

## 3. Vigil support tablet

Primary locations: `source/visual-support-tablet/addons/VIGIL/config.cpp`,
`ui/`, and `functions/`. Vigil depends on CORDIS/CBA and optionally Field
Utilities for fixed-wing airdrop.

### 3.1 Tablet access, shell, and navigation

* **Items/access rule/keybind** provide three side terminal variants, optional
  tablet requirement, and Ctrl+Home open. **Implemented; COVERED.** `vigil-ui`
  proves required/no-item rejection, itemless override, all three terminal
  variants, exact client-local display state, and the real keybind path. See
  [`vigil-tablet-access-review.md`](vigil-tablet-access-review.md).
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

* **Live asset browser** discovers and classifies live friendly support assets.
  **Implemented; COVERED** for unwhitelisted transport, artillery, and rotary
  CAS. `vigil-ui` proves exact mixed-fleet backing/tree identities and excludes
  hostile, dead, and wrong-role controls. Distant crew proxies are not assumed;
  live commander side is preferred and class affiliation is the bounded fallback.
  Fixed-wing registry rows and the dormant recon branch remain separate. See
  [`vigil-asset-browser-review.md`](vigil-asset-browser-review.md).
* **Eden whitelist and Zeus activation** are **REFINED; ACCEPTED / COVERED**.
  Fresh run `20260823T173648Z-86506466` proved authentic multiple-module
  aggregation, retained typed modules, server-private exact membership, and two
  authentic operations in one assigned-curator display: add an absent vehicle,
  then remove a distinct present vehicle. Exact operation/logic/curator/target
  identities, replay/forgery rejection, placing-curator-only feedback,
  current-client replication, state retirement, and cleanup passed (server 14/0,
  client 10/0), following an independent cold repeat. Runtime reconfiguration,
  zero-sync/deleted-module edge policy, and client-B/JIP remain unproven. The
  accepted unwhitelisted browser remains unchanged. See
  [`vigil-asset-whitelist-review.md`](vigil-asset-whitelist-review.md).

### 3.3 Coordinates, vehicle tasking, and governor

* Grid parse/format, map clicks/previews, nearest helipad, waypoints, hard stop/
  AI reboot, engine/landing mode, and safe/transit AI presets are **implemented;
  PARTIALLY COVERED** through artillery/flight outcomes. Helpers are replaceable.
* The **task governor** is **REFINED; ACCEPTED / COVERED** for its server-owned
  terminal lifecycle and one-client declarative request authority. The
  `vigil-governor-lifecycle` contract covers ordered/abnormal terminal paths,
  exact-once finalization, generation-aware retirement and successor
  preservation. `vigil-governor-authority` covers authenticated data-only
  artillery/transport/CAS requests, server-built handlers, same-side/whitelist
  eligibility, replay/busy rejection, forged/code-bearing rejection, correlated
  requester-only receipts and cleanup. Remote cancellation policy, durable
  history, ownership migration, headless/client-owned vehicles, client-N and
  JIP remain excluded. See
  [`vigil-task-governor-review.md`](vigil-task-governor-review.md).

### 3.4 Artillery and VLS

* **Request UI/preview markers** render grid/ordnance/spread/count/direction and
  circle/line state client-locally. **Implemented; COVERED** by `vigil-markers`
  for updates, stale replacement, rendering, locality, and cleanup.
* **Native artillery execution** fires exact physical circle/line counts and
  rejects zero, out-of-range, and no-ammo requests. **Implemented; COVERED** by
  `vigil-artillery` for authority, trajectories, geometry, locality, and cleanup.
* **VLS execution** launches vertically, guides, and reaches the target region.
  **Implemented; COVERED.** Its combined target-report/confirmation handshake
  is a **REVIEWED / CHARACTERIZED ENGINE REQUIREMENT**: four fresh direct-first
  physical A/B pairs prove direct fire emits an unguided missile while the
  handshake reaches the target region. See
  [`vigil-vls-handshake-characterization.md`](vigil-vls-handshake-characterization.md).

### 3.5 Helicopter transport / reinsertion

* **Eligibility/request** captures destination, altitude, ignore-enemy, and
  do-not-climb state. **Implemented; PARTIALLY COVERED.** Eligibility/locality is
  direct; the latter option semantics are not explicit assertions.
* **Outbound/LZ/landing/wait** dispatches once, rejects duplicates, and reaches/
  settles at the LZ. **Implemented; COVERED** by `vigil-transport`.
* **RTB/reinsertion** returns to recorded home, settles, and cleans resources.
  **Implemented; COVERED.** Reinsertion is not a separate implementation.
* Hidden-pad plus `land "LAND"` is **KEEP + CHARACTERIZE ENGINE REQUIREMENT; ACCEPTED / COVERED** for one server-local airborne `B_Heli_Light_01_F`, clear Stratis corridor, `doMove` approach, and 90-second landing deadline. Three independent final A/B runs prove the no-pad control reaches the arrival radius but remains airborne beyond 104 m while the exact `Land_HelipadEmpty_F` treatment lands within 25 m and holds three continuous settled seconds. Other classes, terrain, approaches, landing modes, waypoint-only behavior, locality, client-B, and JIP remain unclaimed.

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

* **Editor/Zeus registration** is **REFINED; ACCEPTED / COVERED**. Authentic
  typed modules aggregate exact synchronized planes and nearest ingress/egress
  points; one assigned curator can add one exact plane with placer-only result,
  replay/wrong-class rejection, replication, and full state cleanup. Mixed Sync,
  point removal/reconfiguration, alternate large-plane curator acquisition, and
  client-N isolation remain bounded follow-ups. See
  [`vigil-fixed-wing-module-review.md`](vigil-fixed-wing-module-review.md).
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

* **Helicopter stabilization** is **REVIEWED / DEFERRED**. Controlled real
  transport A/B reached the force on an eligible flat corridor but missed
  predeclared 5 m altitude and 1 m/s vertical-speed usefulness gates; another
  corridor proved the model-forward terrain guard can suppress all sampling.
  Normal transport and CAS RTB no longer enroll automatically. Explicit
  experimental finalization now clears all stabilizer state. See
  [`vigil-helicopter-stabilizer-review.md`](vigil-helicopter-stabilizer-review.md).
* **Radio/chat/curator feedback** wraps CORDIS. **REVIEWED / NEEDS PRODUCT
  DECISION; PRESENTATION EXPERIMENT DEFERRED.** Real task callers exist,
  but they default to all-live-player routing and curator empty-scope fallback;
  requester/side/curator audience is unresolved. Accepted task state, wrapper
  return, or one recipient does not prove correct delivery, and actual audio is
  unproven under `-noSound`.
* **CAS auto-engage debug** is **REFINED; ACCEPTED / COVERED** for the exact
  server-log and one-client presentation-gate contract. The unregistered
  always-true private gate was removed; exact AAE tokens now always reach the
  server RPT path and use only registered `YSF_showDebugMessages` for false/true
  target-local gating. Runs `20260825T211810Z-e22f0ec6` and
  `20260825T211937Z-cc730425` each passed 3/0 server and 3/0 client feature
  assertions. Visible pixels, client-N/JIP and rate/volume remain unproven.
* **Shared production debug wrapper** is **REFINED; ACCEPTED / COVERED** for
  sole source ownership and the same one-client CORDIS setting route. The
  deferred laser harness no longer conditionally defines the product-wide
  symbol; `fn_utils.sqf` owns it and exact shared tokens prove false/true
  `YSF_showDebugMessages` gating in runs `20260825T221344Z-3814387b` and
  `20260825T221507Z-12376258`. The harness itself remains deferred and untested.

Full analysis: [`vigil-feedback-review.md`](vigil-feedback-review.md).

## 4. Field Utilities

Primary locations: `source/field-utilities/addons/FieldUtils/config.cpp`,
`functions/`, and `ui/`. Dependencies: CORDIS, CBA, ACE, ZEN, optionally Vigil.

### 4.1 Virtual Storage and Fabricator

Reviewed in [`field-utilities-fabricator-review.md`](field-utilities-fabricator-review.md);
primary outcome **REFINE BEFORE PERMANENT COVERAGE**; refinement is complete and
the feature is now **COVERED** by `fieldutils-fabricator`. Orders are
server-authoritative and atomic, the catalogue is an unlimited template source,
and the local virtual-inventory toggle is restored. Active owner cancellation
terminates the transaction worker before rollback and retirement. The exact pre-publication clone is now proven visible, unattached,
server-local,
and capped at mass 200 through ACE's replicated mass event; client-a waits for
that cap and starts ACE carry on that exact identity. Packed placement is also
covered on flat land, a bounded 10–20 degree gradient neighborhood, and a dense
64-barrier ring, including exact contents and continuous physical rest. See the
review for excluded terrain cases.

* **Mission-maker Eden registration** is **REFINED; ACCEPTED / COVERED** for
  authentic typed dispatch, native Sync links, retained server-local logics,
  multiple-module catalogue/station aggregation, default local-inventory
  handoff, current-client mirrors, and server-private authority. Fresh run
  `20260821T153954Z-34a72701` passed server 9/client 7 assertions and proved that
  two forged setters were rejected while successful client poisoning of both
  public mirrors could not alter the exact private catalogue/stations. Mixed
  checkbox values, runtime reconfiguration/deletion, missing-pair editor UX,
  client-B, and JIP remain unproven. Field Utilities has no Zeus activation
  tool. See
  [`field-utilities-eden-module-activation-review.md`](field-utilities-eden-module-activation-review.md).
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
* **Delivery placement** is **REVIEWED; KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for an exact
  server-owned single land delivery and for authentic packed orders on flat,
  moderate-gradient (10–20 degrees), and dense 64-barrier land fixtures. Exact
  contents, bounded recipient/drop distance, physical settling, locality and
  cleanup are observed. Severe gradients, ponds, arbitrary collision clearance,
  coastline fallback and water recipients remain **NEEDS EXPERIMENTATION**.
* **Airdrop handoff** calls Vigil delivery and observes authoritative parachute
  results. **Implemented; COVERED as a cross-mod composite.** Missing API fails
  closed.

### 4.2 Bridge Builder

* **Construction box/ACE entry** exposes “Open Bridge Builder.” **Implemented;
  COVERED.** The exact class action is registered and ACE's active tree proves
  its out-of-range, busy, and eligible states; the permanent feature proof then
  invokes that registered statement without per-feature VNC automation.
* **Planning UI** selects layout, ramp, orientation, clipping, counts, pitch,
  offsets, and auto calculation. **ACCEPTED / COVERED.** The permanent scenario
  proves the narrow lengthwise and vehicle-capable wide layouts, ramps per end,
  world-level versus source-tilt orientation, terrain/building-only automatic
  support, intentional end clipping, an immutable server-validated plan, and a
  50 m bound. A server planner lease and exact grant receipt are covered for
  client-a; genuine second-player named contention remains deferred.
* **Preview** computes/caches queues and renders validity colors. **Implemented;
  COVERED through data for the accepted layouts.** Calibration captured the
  real rendered flat preview; permanent regression validates flat, wide, ramp,
  Match Box and Keep Level plan state without making pixels the oracle.
* **Build/removal** incrementally creates deduplicated segments with configured
  delay and removes chains. **ACCEPTED / COVERED.** Server authority, exact
  geometry/locality, pedestrian flat/ramp traversal, wide vehicle traversal,
  box-scoped removal, bounded results and cleanup are proven;
  interruption/destruction and resources are not.
* **Direct chain-extension actions** coexist with plan UI. **Implemented-looking;
  DEFERRED.** Helpers exist but action attachment is empty and no supported
  intent/authority contract was established.

Full analysis: [`field-utilities-bridge-builder-review.md`](field-utilities-bridge-builder-review.md).

### 4.3 Logistics and object handling

* **Selective ACE cargo preservation** is **REFINED; ACCEPTED / COVERED** for
  the exact `YFU_Bridge_Box` and `YAS_OPHANIM_box` classes on pinned ACE 3.21.
  Both explicitly opt in and retain configured size 2 and ACE load eligibility;
  ordinary ammo boxes retain the existing runtime size -1 policy. Two unchanged
  cold runs (`20260825T202333Z-62ab9c1b`,
  `20260825T202453Z-fd022bea`) proved exact authentic ACE returns, membership,
  attachment, client-a replication and cleanup. Other classes/ACE versions,
  ownership domains, client-B/JIP, menus, unload and concurrent ACE/native work
  remain unproven.
* **Automatic pallet/container handling** makes pallets draggable/carryable and adds a server-installed box contact/attachment hook. **KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for a server-owned `B_supplyCrate_F` physically contacting a server-owned `B_Truck_01_transport_F`, with exact treatment/control contact, treatment-only attachment, carrier-state deltas, client-a replication, and controlled no-leak teardown. Final independent runs `20260824T152814Z-a9dd0df5` and `20260824T152942Z-0e8c4083` each passed 9/0 server and 5/0 client feature assertions. Client ownership/migration, broader classes/surfaces, repeated contacts, deletion while attached, client-B, and JIP remain unproven.
* **Nearby supply actions** expose eligible nearby carriers through ACE. **REFINED; ACCEPTED / COVERED** for server-owned objects and one authenticated client. The server authenticates the requester, revalidates exact class/state/range/capacity, rejects replay and invalid work, requires literal native success plus exact replicated membership, returns an exact private receipt, and cleans up. Fresh run `20260824T135424Z-777de3e6` passed 5/0 server and 4/0 client feature assertions.
* **Safe-fall/fling/attach helpers** support delivery/packing. **Implemented;
  PARTIALLY COVERED** only in fixed-wing cargo.

Full analysis: [`field-utilities-object-handling-review.md`](field-utilities-object-handling-review.md).

### 4.4 Towing and sling ropes

* **Tow points/rope deployment** preserve configured or geometry-derived
  points behind a server-authoritative exact-pair transaction. **REFINED;
  ACCEPTED / COVERED** for server-local land vehicles and one authenticated
  client. Exact feature rope handles, parent state, claims, receipts, loss
  finalization, and reuse are retained and fail closed.
* **ACE tow/stow actions** are **REFINED; ACCEPTED / COVERED**. Fresh run
  `20260823T190019Z-39badbd1` proved the exact registered child, 0 m no-tow
  cargo movement versus 28.3352 m with the same movement under treatment,
  active-conflict and invalid-request controls, preservation of unrelated rope
  `2:162`, rope-loss cleanup, reuse, locality-aware replication, and complete
  cleanup (server 14/0; client 13/0). Player-owned vehicles, migration,
  client-B/JIP, natural projectile cuts, deletion/disconnect, and broad fallback
  geometry remain separate experiments.
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
* **Click/shuffle feedback** is **REVIEWED / DEFERRED AS A STANDALONE FEATURE;
  CONSUMER-OWNED PRESENTATION**. The clicks are reachable from the real FPV ACE
  statements and shuffle is incidental to owner-local attachment, but
  autonomous clients run with `-noSound` and no listener/audience/concurrency
  contract exists. Payload success or a sound-command call is not audible
  evidence. The generic vehicle-sound helpers have no product caller.

Full analysis: [`field-utilities-fpv-review.md`](field-utilities-fpv-review.md).
Audio analysis:
[`field-utilities-fpv-audio-review.md`](field-utilities-fpv-audio-review.md).

### 4.6 Shared libraries

* **Geometry and packing primitives** are **REVIEWED / DEFERRED AS A
  STANDALONE FEATURE; CONSUMER-OWNED**. Fabricator directly covers authoritative
  packed delivery, exact manifest, atomic skipped-item refusal, bounded
  placement, and leak-free cleanup. Pallet choice, reference corners,
  orientation, ordering, allocation, offsets, and helper names remain
  replaceable mechanics. Towing uses a subset but remains separately unresolved;
  product helpers must not serve as their own placement oracle.

Full analysis:
[`field-utilities-geometry-packing-review.md`](field-utilities-geometry-packing-review.md).
* **ID/location marker helpers** are **REVIEWED / DEFERRED**: compiled global
  scaffold with no normal caller; authority, visibility, labels, and cleanup
  have no product contract.
* **Airdrop direction/ETA feedback** is **REVIEWED / NEEDS PRODUCT DECISION AND
  EXPERIMENTATION**. The live client announcement uses target-to-aircraft
  bearing and altitude-only vacuum fall time at acceptance, which does not model
  ingress or parachute descent.
* **Shared sound, global ACE registration, and debug/chat wrappers** are
  **REVIEWED / DEFERRED AS A STANDALONE FEATURE; CONSUMER-OWNED**. Bridge
  Builder proves its exact current-client action, while airdrop feedback keeps
  its own unresolved recipient/meaning contract. Debug is diagnostic and the
  generic vehicle-sound helpers have no caller. Wrapper invocation is not JIP
  delivery, recipient-visible feedback, or audible-output evidence.

Full analysis:
[`field-utilities-shared-runtime-wrappers-review.md`](field-utilities-shared-runtime-wrappers-review.md).

Full analysis: [`field-utilities-map-helpers-review.md`](field-utilities-map-helpers-review.md).

## 5. Cross-mod composition and integration

### 5.1 CORDIS consumer contract

All feature addons declare CORDIS and use authority, dedupe, feedback, or
logging. The shared trusted-broker contract is **REFINED; ACCEPTED / COVERED**
for server plus one authenticated client by `cordis-routing`; consequential
consumer authorization/outcomes remain feature-owned. JIP, disconnects,
ownership migration, and multiple clients remain deferred.

### 5.2 Vigil–Field Utilities logistics bridge

Vigil invokes Fabricator UI; Field Utilities packages manifests and calls
Vigil's authoritative request; Vigil calls Field Utilities parachute mechanics
and returns one result. **Implemented; COVERED** for reviewed fixed-wing
airdrop. General fabrication is outside the contract.

### 5.3 Shared UI and interaction

* Field Utilities reuses Vigil display/terminal skins while keeping separate
  state. **Implemented; PARTIALLY COVERED incidentally** by logistics. Nested
  lifecycle, styling, and use without Vigil are not reviewed.
* Field Utilities cold-client ACE class-action composition is **ACCEPTED /
  COVERED** for Bridge, Logistics, Virtual Inventory, Towing/Stow, and FPV root
  registration, concrete-class inheritance, coexistence, and relevance through
  ACE's installed-version active-tree adapter. Consequential effects, the
  Fabricator delayed object action, client-B, and JIP remain feature-owned or
  deferred. APS plus Field Utilities composition is **ACCEPTED / COVERED** for the current authenticated client. Fresh run `20260820T223222Z-3046910b` proved four exact singleton Field roots on installed and uninstalled same-class tanks, an unchanged Field census across authenticated APS suspension/resume, exactly Resume while suspended, and exact preserved-mode APS controls after resume. Client-B/JIP, explicit uninstall, deletion, repeated init, and ownership migration remain deferred; anti-drone gameplay is not implied. See
  [`field-utilities-ace-composition-review.md`](field-utilities-ace-composition-review.md)
  and
  [`aps-fieldutils-ace-composition-review.md`](aps-fieldutils-ace-composition-review.md).

### 5.4 Eden/Zeus and CBA configuration

* APS Eden activation is **REFINED; ACCEPTED / COVERED** through authentic typed mission entities and native Sync links. APS Zeus activation is also **REFINED; ACCEPTED / COVERED** for one authentic assigned-curator placement and exact causal activation. CBR Eden/Zeus activation is likewise **REFINED; ACCEPTED / COVERED** for authentic typed dispatch and an assigned-curator global toggle. Field Utilities Virtual Storage/Fabricator Eden activation is now **REFINED; ACCEPTED / COVERED** for multiple typed modules, aggregated Sync provenance, and server-private authority. Vigil whitelist Eden aggregation and assigned-curator add/removal are **REFINED; ACCEPTED / COVERED**. Field Utilities exposes no
  Zeus tool. Vigil fixed-wing Eden/Zeus activation is **REFINED; ACCEPTED /
  COVERED** in
  [`vigil-fixed-wing-module-review.md`](vigil-fixed-wing-module-review.md).
* Cross-addon CBA setting declarations are **REFINED; ACCEPTED / COVERED**
  for 13 exact unique keys, types, defaults/bounds, global/local scope, live
  consumer handoff, and fallback parity. Iron Dome's fallback now matches its
  registered 1000 m default, and debug descriptions match always-log plus
  optional-systemChat behavior. Downstream gameplay, feedback, sound, colors,
  Draw3D, and combined-setting effects remain consumer-owned. See
  [`cba-settings-contract-review.md`](cba-settings-contract-review.md).

### 5.5 State, serialization, and persistence

* Replicated object/mission variables carry APS, task, registry, cargo-result,
  whitelist, and config state. **Implemented; PARTIALLY COVERED** by one-client
  replication scenarios.
* No durable campaign/database persistence exists in the four mods.
* **JIP/multi-client semantics** are **REVIEWED / DEFERRED — ENVIRONMENT
  DEPENDENCY; FEATURE-SPECIFIC POLICY REQUIRED**. Tribunal is structurally
  client-N-aware, but Pontifex currently provisions, slots, launches, observes,
  and validates exactly one independently authenticated client. Existing
  replication claims remain client-a-only. Reopen after a second licensed Steam
  identity is provisioned and each feature defines visibility, retention,
  audience, concurrency, and disconnect policy. See
  [`multiplayer-client-n-jip-boundary-review.md`](multiplayer-client-n-jip-boundary-review.md).

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
| `cordis-routing` | trusted server/object/group routing, operation-aware TTL dedupe, exact scoped fan-out, recipient decisions, cleanup |
| `aps-intercept` | APS hard/soft kill, controls, locality, resources, replication |
| `vigil-ui` | real tablet open/navigation/close/reopen and UI locality |
| `vigil-markers` | artillery preview rendering/state lifecycle and cleanup |
| `vigil-artillery` | circle/line artillery, controls, VLS, locality/cleanup |
| `vigil-transport` | helicopter outbound/LZ/wait/RTB lifecycle |
| `vigil-transport-pad-ab` | bounded hidden-pad versus no-pad landing characterization |
| `vigil-cas` | rotary CAS filtering, attack, timer, controls, RTB |
| `vigil-debug-channel` | CAS auto-engage and shared production debug server logging, registered false/true client presentation gate, restoration |
| `vigil-governor-lifecycle` | server-owned ordered stages, terminal causes, exact-once finalization, duplicate rejection, successor preservation, cleanup |
| `vigil-governor-authority` | authenticated declarative artillery/transport/CAS requests, server-built tasks, rejection/correlation, terminal receipts, cleanup |
| `vigil-fixed-wing` | registry/reconstruction, two designation strikes, control, egress |
| `vigil-fixed-wing-logistics` | manifest airdrop, parachute/landing/inventory, egress |
| `vigil-fixed-wing-modules` | authentic typed Eden aggregation, nearest points, assigned-curator add, authority/replication/cleanup |
| `fieldutils-cargo-loading` | nearby authenticated exact-pair vehicle cargo loading, rejection, replication, cleanup |
| `fieldutils-ace-cargo-policy` | selective configured ACE cargo preservation, ordinary-box negative control, authentic load/replication/cleanup |
| `fieldutils-fabricator` | server-authoritative atomic orders, catalogue fidelity, refusals, cleanup |
| `advsys-counter-battery-radar` | artillery detection, impact prediction/zone, origin fix, side warning, lifecycle |

Framework `locality-probe` and `visual-framebuffer` scenarios prove Tribunal,
not product features. Promote generic backlog mechanics only for a concrete
consumer.

The project manifest and Pontifex runtime now discover the same feature scenario
set across Core/CORDIS, Advanced Systems, Field Utilities, and Vigil. A regression compares
their independently loaded identifiers so future manifest drift fails closed.

## Deferred, incomplete, disabled, and unclear areas

| Area | Classification | Repository-grounded reason |
| --- | --- | --- |
| Vigil homepage task management | **REVIEWED / DEFERRED** | unreachable commented page; incompatible client/server data shape and no authoritative cancellation contract |
| Vigil reconnaissance | **REVIEWED / DEFERRED** | role/state only; unreachable form, no submit, empty task, no sensor/output/lifecycle |
| Fixed-wing UAV deploy | **REVIEWED / NEEDS EXPERIMENTATION** | explicitly rejected as unstable |
| Helicopter stabilizer | **REVIEWED / DEFERRED** | controlled physical A/B missed predeclared usefulness gates; automatic transport/CAS enrollment is off; any future mechanism requires a new bounded rewrite/experiment |
| 3CB Hellfire mapping | **REVIEWED / NEEDS EXPERIMENTATION** | no compatible installed pylon row for A/B |
| VLS target handshake | **REVIEWED / CHARACTERIZED** | four fresh physical A/B pairs prove the combined knowledge step is required; individual calls remain unisolated |
| Transport hidden-pad landing | **KEEP + CHARACTERIZE ENGINE REQUIREMENT; ACCEPTED / COVERED** | three independent server-local airborne A/B proofs: exact hidden-pad treatment settles within 25 m; matched no-pad control remains airborne beyond 104 m at 90 seconds; scope is one class/corridor/approach |
| Developer laser harness | **REVIEWED / DEFERRED** | unreachable preInit diagnostic; destructive owner-routed run and unbounded client-supplied result store lack a product boundary |
| Vigil CAS auto-engage debug | **REFINED; ACCEPTED / COVERED** for one-client setting-gate topology | unique exact tokens in server RPT plus delegated client false/true receipts through registered `YSF_showDebugMessages`; pixels, client-N/JIP and rate/volume excluded |
| APS anti-drone | **REVIEWED / DEFERRED** | threat/side/operator policy is undecided; resource authority and destructive cleanup require refinement before coverage |
| CBR marker sharing policy | **REVIEWED / DEFERRED** | zone/origin markers are global while the radio warning is side-filtered |
| CBR confirmed-origin persistence | **REVIEWED / DEFERRED** | confirmed fix never expires; decay policy undecided |
| CBR warning coverage | **REVIEWED / DEFERRED** | one warning per firing machine per airborne cycle, on the first round only, at a fixed 1000 m radius; re-warning for a walking barrage undecided |
| CBR module/Zeus activation | **REFINED; ACCEPTED / COVERED** | fresh typed Eden + authentic assigned-curator proof; reverse/repeated/client-B cases bounded |
| Iron Dome client-owned artillery | **REVIEWED / DEFERRED** | current server handler deliberately rejects non-server-local shells; no owner-routing product policy is chosen |
| Iron Dome threat policy/audio | **REVIEWED / DEFERRED** | friendly/outgoing versus protected-impact-area filtering is undecided; audio is unproven under `-noSound` |
| Fabricator delivery mass cap and carry boundary | **REFINED; ACCEPTED / COVERED** | the exact clone is stably mass 200 before publication through ACE's global mass event; client-a waits for that replicated boundary and begins ACE carry on the same net ID |
| Fabricator bounded land/terrain placement | **KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** | exact single delivery is land; authentic packed orders settle with exact contents on flat, 10–20 degree gradient, and dense 64-barrier fixtures; severe gradients, ponds, coastlines, water recipients and arbitrary clearance remain unproven |
| Fabricator client-b discard | **NOT YET PROVEN** | one authenticated client; the foreign-discard control uses a server-owned transaction |
| Fabricator staging choreography | **NO CHARACTERIZATION REQUIRED; OUTCOME-COVERED** | controlled calibrations rejected hiding/relocation as the mass cause; permanent coverage freezes the authentic pre-publication and post-carry outcomes, not staging depth or cadence |
| Field towing | **REFINED; ACCEPTED / COVERED** for server-local vehicles and one authenticated client | exact authority/rope identity, matched physical A/B, scoped stow, break finalization, reuse, negative requests, replication, and cleanup; player-owned/migration/client-N remain deferred |
| Field contact handling | **KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for one server-owned crate/truck topology | exact matched physical contact, treatment-only attachment, carrier-state deltas, client-a replication and controlled no-leak teardown; broader classes/localities/lifecycle remain open |
| Field nearby supply loading | **REFINED; ACCEPTED / COVERED** for server-owned, one-client topology | exact ACE child, authenticated authority, command + membership receipt, negatives, replication and cleanup |
| Field selective ACE cargo | **REFINED; ACCEPTED / COVERED** for exact Bridge/OPHANIM classes on ACE 3.21 | explicit opt-in preserves size 2 and authentic loadability; ordinary ammo box remains ACE-disabled; other classes/versions/localities and unload/concurrency remain open |
| Field ID/location markers | **REVIEWED / DEFERRED** | no product caller; global marker authority/lifetime/cleanup undefined |
| Field airdrop direction/ETA | **REVIEWED / NEEDS PRODUCT DECISION AND EXPERIMENTATION** | direction/audience/ETA interval undefined; current fall formula omits ingress and parachute descent |
| Helicopter sling helper | **REVIEWED / DEFERRED** | compiled orphan; destructive all-rope stow, non-atomic creation, no supported entry/authority/cleanup |
| Bridge direct extension | **DEFERRED** | helpers exist, but no reachable action or supported ownership contract was established |
| Core settings/utils files | **Scaffolded / UNKNOWN** | reserved files contain no behavior |
| Multi-client/JIP | **REVIEWED / DEFERRED** | second independently authenticated Steam identity plus per-feature visibility/retention/audience/concurrency/disconnect policy required |

## Prioritized next feature reviews

Vigil's task governor is now refined and permanently covered for the one-client
declarative authority boundary and server-owned lifecycle. The next highest-value
unblocked investigation is the separately reproduced CAS physical-effect oracle:
correlated fire and a target-local damage event currently coexist with zero net
damage. Treat that as a consumer-oracle diagnosis, not a reason to reopen the
accepted governor. Fabricator's severe slopes, ponds, coastline,
water-recipient, client-B and JIP remain bounded. Explicit nearby supply loading
and bounded Field contact attachment remain accepted. The Vigil helicopter stabilizer is closed as deferred;
do not reactivate its legacy force without a new bounded physical A/B. APS anti-drone is now
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
