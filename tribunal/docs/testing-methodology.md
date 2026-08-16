# Tribunal testing methodology

Tribunal separates the behavior a project promises from the mechanics used to
prove it. Existing code is evidence: it is neither presumed correct nor
presumed obsolete. A permanent test must say which boundary it protects.

The repository-wide capability and coverage map is maintained in
[`pontifex-feature-inventory.md`](pontifex-feature-inventory.md). That inventory
identifies review candidates; it does not itself create behavioral contracts.

## Taxonomy

### Specification tests

Specification tests protect behavior that users or mod authors may rely on
through a refactor. They assert externally meaningful inputs, outcomes,
controls, cleanup, locality, and replication. Private function names, variable
layouts, arbitrary ordering, fixture coordinates, and helper implementation
are evidence-adapter details and must not appear in `behavior_contract`.

### Characterization tests

Characterization tests preserve a mechanism only after a controlled experiment
shows it is engine-imposed, deliberately architectural, or materially safer
than alternatives. Every characterized behavior records description, reason,
evidence, alternative tested, and outcome. “The current code does this” is not
enough. With no A/B evidence, classify the question as `NEEDS EXPERIMENTATION`
and keep the feature test at the specification boundary.

### Tribunal tooling tests

Tooling tests protect reusable mechanics such as deterministic projectile
launch, weapon-fire observation, locality transfer, input, framebuffer capture,
marker/trajectory/spatial evidence, network profiles, and result parsing. These
tests live in Tribunal and contain no project semantics.

### Feature integration/gameplay tests

Feature-owned tests sit beside feature source and use Tribunal mechanics to
prove a specification. The fixture may reference private APIs to reach or
observe the behavior, but those names are not themselves the contract. A
project production mod never depends on Tribunal.

## Feature review procedure

The single canonical 12-question review, classification gates, feature-specific
fill-in section, execution phases, and acceptance rules are in
[`feature-review-program.md`](feature-review-program.md). Apply that program
before substantial permanent feature coverage; do not maintain a second local
variant of its checklist.

In compact form, the workflow remains:

```text
inventory -> feature-specific scope -> canonical review -> contract/classification
          -> controlled experiment or evidence-supported refinement when needed
          -> generic tooling boundary -> permanent scenario when justified
          -> Live iteration -> fresh autonomous proof -> validation
          -> inventory update -> commit/clean closeout
```

`ScenarioReview` is intentionally small. It records the canonical program's
primary test type, contract, outcome, rationale, dependencies, evidence types,
locality, and any evidence-backed characterization. Detailed engineering notes
remain here or in feature documentation rather than growing a general-purpose
schema.

## Existing coverage audit

| Area | Stable specification | Evidence adapters, not specification | Outcome |
| --- | --- | --- | --- |
| APS | qualifying inbound threat is stopped; disabled/outside/away controls are not; hard/soft resources change correctly; protected state replicates | direct-injection coordinates/speed, private tracker name, ledger representation, polling cadence | KEEP AS-IS AND SPEC-TEST |
| Vigil UI | intended client opens, visibly navigates, closes, cleans up, and reopens in default state; server has no display | IDCs, `uiNamespace` keys, input coordinates, screenshot thresholds | KEEP + CHARACTERIZE ENGINE REQUIREMENT |
| Vigil markers | valid request count/position changes visible preview; stale preview is replaced; clear/close removes it; server has no preview | generated marker names, backing-array layout, exact probe pixels | KEEP AS-IS AND SPEC-TEST |
| Vigil artillery | grid request produces exact round count and circle/line geometry; invalid/range/ammo controls do not fire; VLS physically launches/guides/arrives | governor variables, private submit/parser names, Fired-event ordering, observer sample rate | KEEP AS-IS AND SPEC-TEST |
| Vigil transport | selected crewed transport physically flies, lands and settles at LZ, waits, then physically returns and settles at recorded home; duplicate request is rejected | task IDs/state keys, waypoint/land command sequence, fixture coordinates, observer cadence | REFINE BEFORE PERMANENT COVERAGE |
| Vigil rotary CAS | selected armed helicopter reaches its requested area, attacks only a valid hostile ground target with correlated real fire and impact, respects its timer, disengages and returns home; no-target and invalid controls fail closed | task/ledger layout, fixture coordinates/classes, LOITER/MOVE details, sensor/reveal and observer cadence | REFINE BEFORE PERMANENT COVERAGE |
| Vigil fixed-wing strike | registered state reconstructs once, enters the operating area, consumes real client laser/IR designations for two correlated guided impacts, rejects no-designation fire, then physically egresses and cleans up | registry schema, fixture coordinates/classes, waypoint geometry, observer cadence and private helper names | REFINE BEFORE PERMANENT COVERAGE |
| Counter Battery Radar | enabled detection draws an impact zone on the ground the shells actually strike, with count/ETA, a narrowing then confirmed origin at the real gun, a side-filtered launch warning, expiry, replication and full reset on stop; disabled produces nothing | cluster/member layout, uid format, marker names and index counters, link distance/leeway/hysteresis, integration step and cadence | REFINE BEFORE PERMANENT COVERAGE |

### APS findings

Hard kill, soft-kill deflection, physical disabled impact, outside-envelope and
direction-away controls, exact projectile correlation, authoritative state,
locality, charge/fuel behavior, and replication form a causal specification
suite. The engagement ledger is valuable authoritative evidence but its array
shape is not promised. Threat-fixture geometry and explicit tracking are
Tribunal/adaptor necessities, not APS behavior. No APS production mechanism is
newly characterized or rewritten by this audit.

### Vigil UI findings

Open/tab/close/reopen assertions are user-visible and paired with framebuffer
evidence. Client/server locality is part of the feature contract. Control IDs
and state keys merely anchor that evidence. One Arma-specific mechanism is
eligible for characterization: on this build, calling the unmodified open API
from the same scheduled worker that observed Escape-driven display destruction
did not recreate the dialog, while a fresh scheduled worker did. The retained
test records the prior controlled outcome rather than generalizing it to all UI
code. The audit also corrected the generic reopen observer: a bright terrain
strip could resemble the initially selected tab, so reopen now requires both
the tab anchor and a material full-frame transition from the closed game
surface.

### Vigil marker findings

The suite correctly combines rendered evidence with backing state so a stale
or unrelated image cannot pass. Exact internal marker registration, ellipse
shape, and size help prove that the rendered preview is the intended product
object; they are not named in the stable contract and may change with the
adapter if the UI is refactored. During this audit, combined-suite runs exposed
an order dependency: the marker fixture inherited the preceding artillery
scenario's line/spread/direction state, while its isolated run started with
circle defaults. The fixture now establishes its own geometry. No product
rewrite, timing expansion, or assertion weakening was needed.

### Vigil artillery and VLS findings

Round counts, physical shells, spatial geometry, controls, locality, cleanup,
and full VLS flight are specification evidence. `ArtilleryShellFired`/`Fired`
correlation and waterline platform stabilization are Tribunal fixture concerns.
Vigil currently creates a temporary VLS target, reports it to the launcher
side, confirms it, and calls `fireAtTarget`. This handshake is a
characterization candidate, not yet a characterized contract: no retained
controlled A/B proves that direct fire necessarily launches vertically without
guidance on the current engine build. The permanent test therefore requires
physical guidance/arrival but does not freeze the handshake. A future isolated
A/B may promote it to characterization with artifacts.

### Vigil transport findings

The transport review found no distinct reinsertion implementation: the term
describes the same helicopter transport task. The existing path lacked a user
RTB request/state, accepted duplicate replacement, lost one request parameter,
classified crewed BLUFOR aircraft using their civilian vehicle side, created
fallback pads in the wrong coordinate space, accepted one-tick ground contact,
and could wait forever. Those were refined before permanent coverage. The
specification now combines the real client request with independent server
trajectory, landing, stable-wait, return, locality, and cleanup evidence.

Hidden-pad creation plus `land "LAND"` remains a characterization candidate,
not a frozen requirement: the successful baseline proves the mechanism works,
but no controlled alternative has yet shown that it is required by Arma.

### Vigil rotary-CAS findings

The CAS review found globally eligible engagement, incorrect effective-side
resolution, no operating-area filter, guided-only explicit selection, cannon
range derived from an unrelated guidance property, fire commands without
physical acknowledgement, and unreliable combat RTB. The refined behavior is
active-CAS scoped, filters live hostile ground targets to the area, uses
ammunition-backed weapon fire-mode envelopes, records only matching Fired
events, and hands timer expiry to the proven transport RTB path.

A controlled SAD experiment attacked an off-area hostile after the requested
target; BLUE/AWARE plus explicit filtered `fireAtTarget` did not. A controlled
RTB experiment showed reboot alone remained stuck while reboot plus a fresh
MOVE task returned. Only that reset is an evidence-backed engine
characterization. Full analysis is in
[`vigil-cas-review.md`](vigil-cas-review.md).

### Vigil fixed-wing findings

The fixed-wing review proved that registration is serialization rather than a
persistent parked-aircraft model: the original aircraft and crew are removed,
then one server-local aircraft is reconstructed at ingress. Fuel and exact
pylon ammunition were previously lost, a generic laser-bomb rewrite doubled
native Bomb04 ammunition, and RTB was unbounded. Reconstruction now preserves
those values, native Bomb04 is retained after physical guidance evidence, and
RTB records bounded success/destruction/timeout.

Real client input creates both supported designation paths: Arma's handheld
LaserTarget and Vigil's daylight weapon-IR helper. Tribunal correlates their
netIds and locality through real server-owned Bomb04 Fired trajectories and
HitPart/damage, followed by a designation-free control and physical RTB. The
remaining 3CB Hellfire mapping is NEEDS EXPERIMENTATION because no qualifying
installed pylon class exists for an honest comparison. Full analysis is in
[`vigil-fixed-wing-review.md`](vigil-fixed-wing-review.md).

### Vigil fixed-wing logistics findings

The logistics review found that the old path opened the real Field Utilities physical-object queue but then reported success from a client-local fling with no authoritative task, ingress gate, duplicate protection, physical completion, or RTB. The refined path transfers the packed object tree to the server, flies the shared registered aircraft to a bounded release gate, uses a real parachute, proves exact weapon/magazine/item/backpack inventory after landing, and then uses the shared bounded RTB lifecycle. No capacity feature exists, so no capacity contract was invented. Full analysis is in [`vigil-fixed-wing-logistics-review.md`](vigil-fixed-wing-logistics-review.md).

### Counter Battery Radar findings

The CBR review found a working detection, clustering, warning and origin
pipeline with one material defect: impact prediction integrated the projectile
to sea level rather than to the ground under the projected point, biasing the
drawn impact zone downrange for every target above the waterline. A one-variable
A/B on the same live shells measured 46.65 m and 53.76 m error at 219 m and
167 m elevation against 2.15 m and 6.06 m for a terrain-aware solution, and
identical results at sea level. Only that termination condition was corrected,
plus an explicit bound on the previously unbounded integration loop; the
prediction mechanism itself is not frozen by the contract.

A suspected defect was disproved and deliberately left unchanged: deleting from
`YOSHI_originTrack` while iterating it removed all five expired entries in one
pass. Marker sharing policy, confirmed-origin persistence and warning coverage
are genuine open product decisions — zone and origin markers are global while
the radio warning is side-filtered — and no test asserts a preferred answer.

An independent audit of the first coverage attempt produced two structural
corrections worth generalising. A negative control must independently prove that
the stimulus it withholds a response to actually occurred: the disabled-path
control originally fired a round and asserted only that no detection state
appeared, so it would have passed had the gun never fired at all. It now proves
the shell launched, flew and impacted before CBR's silence means anything.
Likewise, a scenario must exercise the real pipeline rather than the helper at
its end: the warning coverage originally invoked the side-filter helper
directly, proving filtering but not launch-to-receipt. Positive and both
negative controls are now real artillery launches. Full analysis is in
[`advanced-systems-counter-battery-radar-review.md`](advanced-systems-counter-battery-radar-review.md).

A run that ends `FAIL (timeout)` is not evidence of success for the assertions it
did emit. Assertions simply stop arriving at the deadline, so a scenario is
proven only by a `PASS (complete)` run whose emitted set matches the plan's
expected set.

## Generic Tribunal capability backlog

Already generic: deterministic PBO packaging; assertion/result protocol;
direct projectile launch; artillery/weapon-fire trajectory observation;
spatial evidence; locality transfer; remote execution; authenticated
framebuffer/input; map/marker observation, including a product-neutral marker
property/census/lifecycle observer; evidence attachments; named network
profiles; version-bounded ACE interaction discovery plus authenticated real
input.

Tribunal is data-first. Prefer engine-visible configuration, identities,
locality, state transitions, physical contacts and authoritative results over
pixels or synthetic input whenever those observations prove the contract.
Framebuffer/VNC evidence is reserved for behavior whose contract is itself
visual (for example dialog layout, Draw3D, map rendering, or an animation with
no reliable state proxy). Once a generic framework interaction mechanism is
proven, feature scenarios should not repeatedly automate its camera, key and
menu mechanics merely to reach product code.

Promote only on first concrete consumer or clear reuse:

1. vanilla action-menu discovery/activation;
2. reusable spawn/settle and damage probes;
3. AI creation/tasking and vehicle movement/landing evidence;
4. module synchronization/Eden-like fixtures;
5. weapon selection and real fire;
6. opt-in audio and animation evidence.

## ACE interaction adapter

`AceInteractionRequest` is the product-neutral prototype: actor identity,
target identity, external/self type, action path, expected availability, and
whether to activate. It intentionally has no Pontifex action names.

ACE's official framework says scripted action registration is client-side,
passes `[_target, ace_player, actionParams]` to condition/statement, and does
not automatically include `ace_common_fnc_canInteractWith`. ACE's internal
`collectActiveActionTree` evaluates modifier, condition, dynamic children, and
object/class children; its key-release path rechecks the condition immediately
before running the statement. Both functions are marked private by ACE.

The implemented capability has two layers:

1. an ACE-version adapter on the actor client enumerates the same active tree,
   records action IDs/path/display names, and verifies the requested action is
   genuinely actor-available, including the registered condition, modifiers
   and dynamic children;
2. authenticated framebuffer/input opens the real ACE menu and selects the
   verified path when ACE rendering/input itself is the subject of the proof.

Feature specifications normally use the first layer, then invoke the statement
from the exact registered action node and validate the resulting product state.
That is deliberately described as registered-statement execution, not
real-user input. Depending on ACE's private arrays is isolated behind
installed-version evidence and fails closed when the expected action tree is
unavailable. The Field Utilities Bridge Builder specification follows this
boundary: it proves absence while out of range/busy, presence when alive and
within 8 m, invokes the registered “Open Bridge Builder” statement, and then
asserts dialog state, preview, authoritative construction and physical outcome
through data. The generic authenticated input adapter remains available for a
single compatibility proof or an inherently visual interaction requirement;
it is not part of every ACE feature scenario.

Primary references for that design are ACE's
[Interaction Menu framework documentation](https://ace3.acemod.org/wiki/framework/interactionmenu-framework.html),
the private
[`collectActiveActionTree`](https://github.com/acemod/ACE3/blob/master/addons/interact_menu/functions/fnc_collectActiveActionTree.sqf)
implementation, and the private
[`keyUp`](https://github.com/acemod/ACE3/blob/master/addons/interact_menu/functions/fnc_keyUp.sqf)
activation path. The version adapter, rather than feature tests, owns any future
compatibility work caused by changes to those private functions.

## Preliminary review of next feature families

| Priority | Family | Preliminary outcome | Review focus before coverage |
| --- | --- | --- | --- |
| 1 | Helicopter transport/reinsertion | REFINE BEFORE PERMANENT COVERAGE | completed review and physical outbound/wait/RTB proof |
| 2 | Rotary-wing CAS | REFINE BEFORE PERMANENT COVERAGE | completed review: hostile/area filtering, correlated fire/impact, timer, invalid/no-target controls and combat RTB |
| 3 | Fixed-wing strike support | REFINE BEFORE PERMANENT COVERAGE | completed review: serialization, ingress/loiter/egress, both designation paths, native guided impact, controls and compatibility refinement |
| 4 | Fixed-wing logistics | REFINE BEFORE PERMANENT COVERAGE | completed review: authoritative physical manifest, bounded ingress/drop/parachute/landing, exact inventory, locality, controls and RTB |

Fixed-wing logistics now reuses the proven registry, serialization, aviation and cleanup adapters while retaining a separate physical-delivery contract. Its review is complete. Fixed-wing reconnaissance was reviewed next and deferred because no executable product contract exists.

### Vigil fixed-wing reconnaissance finding

The reconnaissance review found only a UAV-derived fixed-wing role bit and UI
label. Fixed-wing UAV deployment is explicitly disabled as unstable, the
separate Recon form is unreachable and has no submit action, its task file is
empty, and no sensor, contact, imagery, reporting, persistence or multiplayer
result path exists. Because the player-visible information product is undefined,
the feature is DEFERRED rather than completed by inference. See
[`vigil-fixed-wing-recon-review.md`](vigil-fixed-wing-recon-review.md).
