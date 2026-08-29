# Vigil artillery execution — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for the
tested client-a request to server-owned native-artillery execution, the
server-local VLS execution branch, and exact normal-success retirement of its
product-owned temporary target. Headless/client-owned firing assets,
client-N/JIP, requests
larger than one magazine, the complete rendered-input path, and VLS requests
through the public client/governor boundary remain outside the accepted proof.

## Scope and source reachability

This review covers the reachable artillery page state and submit function in
`functions/task_artillery/fn_arty.sqf` and `fn_ui_arty.sqf`, grid parsing in
`functions/global/fn_core.sqf`, the declarative request validation and server
task lifecycle in `functions/governor/fn_governor.sqf`, and native/VLS
execution in `functions/task_artillery/fn_artillery_task.sqf`.

These are shipped paths rather than orphan helpers. `config.cpp` loads the
governor at pre-init and the artillery handler at post-init. The artillery page
calls `YOSHI_taskArty_submit`; that function sends only positions and ordnance
through `YSF_taskRequestRemote`; the server validates the typed payload,
eligible asset, side/whitelist policy, replay and active-task state, then builds
`YSF_handlers_artillery` itself. The handler obtains the selected effective
commander's vehicle group and distributes requested positions round-robin.
Native platforms route `doArtilleryFire` to commander locality. The exact
`B_Ship_MRLS_01_F` special case instead creates a target object, establishes
target knowledge, and invokes `fireAtTarget` on commander locality.

Marker rendering and stale-marker cleanup belong to the separate
`vigil-markers` contract. Shared request authentication, task generation,
terminal receipts, cancellation, and exact-once finalization belong to
[`vigil-task-governor-review.md`](vigil-task-governor-review.md). The combined
VLS knowledge step has its own controlled review in
[`vigil-vls-handshake-characterization.md`](vigil-vls-handshake-characterization.md).

## Canonical review questions

### 1. What should the user or integrator observe?

A client selects an eligible friendly artillery asset, supplies a valid
eight-digit grid, ordnance, round count, spread, and circle or line pattern,
then submits one bounded request. Native artillery should emit the requested
physical rounds toward the generated positions and reach a truthful terminal
state. A VLS execution should launch one physical cruise missile per requested
position, climb, guide, and reach the target region. Invalid input, unavailable
ammunition, out-of-range points, and empty work must not fabricate fire.

### 2. What does the feature actually do, including negative paths?

`YOSHI_parseGrid` accepts eight digits with an optional supported separator and
returns two four-digit components. UI handling converts those components to
10-metre world coordinates. `YOSHI_drawStrikePattern` creates golden-angle
circle positions or evenly spaced and ordered line positions. Submission sends
the generated array and magazine name through the public declarative request.

The server rejects malformed/empty arrays, more than 32 positions, invalid
position shapes, empty ordnance, an ineligible asset, and a native magazine
which the selected vehicle does not expose. The artillery handler also fails
an empty position list or empty ordnance and fails if its selected commander's
group has no living vehicles. Native execution range-checks every point and
skips points that cannot be reached; absent ammunition produces no shot. It
waits for commander readiness and publishes `done`, then the governor's final
stage publishes `ready_for_next`.

VLS is class-special-cased, reloads its configured weapon, creates one temporary
helipad target per point, establishes target knowledge, and waits for a Fired
acknowledgment with one retry. It does not use native artillery range or ETA.
The retry/failure branch, platform death during execution, mixed reachable and
unreachable queues, and multi-vehicle round-robin execution do not have
dedicated physical permanent proof.

### 3. Which machines and lifecycle stages own the behavior?

The dialog, page state, grid parsing, preview generation, and initial request
are client-local. The dedicated server authenticates the requester, validates
the declarative payload, builds and owns the governor task, and records its
terminal lifecycle. Actual fire is routed to the effective commander's
locality, so the product is not intrinsically server-only.

Accepted `vigil-artillery` evidence is narrower: client-a owns request/UI state
while the tested mortar, VLS, commanders, physical projectiles, observation,
and completion are server-local. It proves neither headless/client-owned
artillery nor ownership migration. Client-b isolation and JIP observation are
also unproven. The shared governor scenario separately proves the current
client-a authentication and server-owned request boundary, but does not widen
the physical artillery locality result.

### 4. Which mechanics are generic Arma or Tribunal concerns?

`doArtilleryFire`, `inRangeOfArtillery`, ammunition inventory, commander
locality, `Fired`/`ArtilleryShellFired`, VLS projectile physics, target
knowledge, trajectory sampling, termination, and network identity are Arma
mechanics. Tokenized observer windows, exact mods/magazine/ammunition
correlation, projectile sampling, spatial tolerances, negative-event windows,
locality records, and fixture cleanup are Tribunal evidence mechanics. Circle
and line generation, artillery eligibility, request bounds, platform grouping,
VLS selection, and completion policy are Vigil behavior.

### 5. Which behavior is owned by Vigil?

Vigil owns the accepted grid syntax and conversion, circle/line strike plan,
count and spread semantics, artillery-capability filter, selected-group policy,
typed request shape, native-versus-VLS branch, per-position range refusal,
round-robin assignment, acknowledgments, completion state, and temporary VLS
target lifecycle. Engine dispersion, ballistic flight, configured magazine
capacity, and class-specific range are not product promises beyond the
representative contract.

### 6. Are unusual engine requirements proven?

Only the combined VLS target-knowledge step is characterized. Retained Live
run `20260820T001108Z-c8edbbcc` used four fresh direct-first pairs. Direct
`fireAtTarget` emitted real missiles which climbed and travelled away; the
otherwise-equivalent combined report/confirm treatment guided to the target
region. The exact terrain-level treatment terminated 0.74 m from target.
Individual necessity and ordering of report versus confirmation remain
unisolated, so only sufficient target knowledge before fire is stable.

No evidence makes the current sleep cadence, forced reload time, retry count,
temporary-target class, radio timing, variable names, or readiness polling an
engine requirement.

### 7. Which details are accidental, legacy, fragile, or incomplete?

The exact VLS class check and weapon/magazine strings are adapter anchors, not
a general artillery taxonomy. Temporary VLS targets are deleted by an independent fixed 100-second thread
rather than by task finalization. The existing broad `vigil.artillery.cleanup`
assertion deletes the mortar and VLS fixtures and checks Tribunal observer
state. The accepted bounded arm separately baselines same-class objects, retains
the exact normal-success target object and network ID, rejects an unexpected
retry target, and waits for that object to become null. Until that arm is
accepted live, normal-success deletion remains source-intended but permanently
unproven; retry, platform death, and cancellation cleanup remain outside it.

The permanent control calls the handler/fire helper directly for zero-round,
out-of-range, no-ammunition, and VLS execution. Those are valid branch tests,
but they do not prove a public rejected receipt for each condition. Circle and
line do use the public client submit path. The VLS arm does not, so it proves
the server-local VLS execution branch rather than end-to-end client/governor
VLS submission. Parser calls establish valid/invalid syntax but do not automate
the complete rendered edit-control event path.

The source records spawned salvo handles in a local array but does not store
them under the `arty_threads` task key inspected by the end handler. Completion
currently depends on per-vehicle mission state instead. This has not contradicted
accepted outcomes, but the unused handle check is replaceable and should not be
characterized.

### 8. Is a better native or existing mechanism available, and is it proven?

Native artillery fire and range queries are already used for ordinary
platforms. The tested direct VLS alternative was not equivalent, so replacing
the knowledge handshake is not justified. The current governor is the shared
validated request boundary; duplicating authority in the artillery handler
would add no value. Temporary target cleanup could eventually be tied to exact
task/projectile termination, but no controlled comparison justifies a product
rewrite during this documentation closeout.

### 9. What is the stable behavioral contract and causal proof?

For the accepted server-owned, one-client topology:

* a valid client-generated circle request produces exactly three physical
  mortar shells from the selected source and magazine, near all three generated
  points, followed by truthful completion;
* a valid line request produces exactly four attributable shells spanning the
  requested line with bounded perpendicular and target-position error;
* zero positions, an out-of-range point, and missing requested ammunition
  produce no correlated projectile;
* representative mortar, tube, rocket, and VLS classes reach their intended
  capability branches;
* one server-local VLS execution emits the exact cruise missile, climbs more
  than 50 metres, travels more than 800 metres with guided horizontal velocity,
  terminates, and reaches within the accepted 350-metre target region; and
* the tested firing fixtures and Tribunal observer are retired.

Fresh autonomous run `20260813T130024Z-4b285268` completed with 22/22 server
and 9/9 client assertions. The three circle rounds terminated 1.94–8.46 metres
from their generated points. The four line rounds spanned 240.4 metres with
0.27–9.25 metres perpendicular error. All seven native shells correlated to
both firing event channels; all three controls emitted no shot. VLS projectile
`2:214` climbed to 210.0 metres, travelled 2.228 kilometres horizontally, and
terminated 4.66 metres from the target. Later complete combined run
`20260813T151311Z-8353510b` repeated every artillery assertion. Post-governor
diagnostic runs `20260825T224845Z-b0838bdc` and
`20260826T001620Z-30bd6992` were not accepted as whole runs, but all 23
artillery feature assertions passed in each; they are regression support, not
substitutes for their failed/timed-out overall outcomes.

Exact mods/ammunition/event identity prevents unrelated fire from satisfying
the native result. Requested-versus-observed counts prevent a completion flag
from replacing physical fire. Independent target points and sampled terminal
positions reject wrong-region rounds. The VLS result requires exact launch
identity, climb, lateral guidance, termination, and arrival; internal
`YSF_ordered`/`YSF_fired` variables cannot pass it alone. Tokenized, empty
control windows reject stale projectiles.

### 10. Which implementation details must remain free to change?

Private function and variable names, task hashmap layout, marker names,
coordinates, fixture classes, observer cadence, spatial tolerances selected for
fixture dispersion, task-stage numbering, radio sounds, assignment arrays,
poll intervals, retry implementation, target-object class, and exact knowledge
commands may change with the evidence adapter. Preserve grid/pattern/count
meaning, authenticated declarative assignment, attributable physical fire,
truthful controls and completion, adequate VLS target knowledge, and owned
resource cleanup.

### 11. Which mechanisms genuinely deserve characterization?

Only adequate VLS target knowledge before `fireAtTarget` has a retained
controlled physical A/B. The current combined report/confirm sequence is kept
because its direct-first alternative failed to guide, but neither individual
call nor ordering is frozen. Native `doArtilleryFire`, per-shot readiness
polling, reload-time manipulation, round-robin assignment, and target lifetime
are implementation choices or ordinary engine adapters, not characterized
requirements.

### 12. Which mechanics should be promoted into Tribunal?

The existing product-neutral artillery observer is the correct promotion:
tokenized exact mods/weapon/magazine/ammunition/projectile records, locality,
requested-position correlation, trajectory/termination samples, and negative
windows. Generic circle/line spatial analysis is also appropriately reusable.
Vigil grid syntax, capability policy, governor stages, VLS class selection,
and target-knowledge policy must stay out of Tribunal.

## Coverage disposition

| Surface | Current disposition | Meaningful remaining boundary |
| --- | --- | --- |
| grid parsing and strike-plan generation | **ACCEPTED / COVERED** for representative valid/invalid syntax and circle/line plans | full rendered edit-control interaction is optional because `vigil-markers` owns visual lifecycle |
| native circle/line execution | **ACCEPTED / COVERED** for one server-owned mortar and representative platform discovery | requests beyond one magazine and physical multi-platform round-robin are reviewed gaps, not blockers for representative completion |
| zero/range/ammunition controls | **ACCEPTED / COVERED** at execution branches | end-to-end rejection receipts are shared-governor/combination work, not a distinct core firing contract |
| VLS flight | **ACCEPTED / COVERED** for the server-local execution branch | public VLS request, retry exhaustion, and other launcher/loadout classes remain unproven |
| VLS target-knowledge handshake | **REVIEWED / CHARACTERIZED** | report-only/confirm-only/order matrix is intentionally deferred until simplification is proposed |
| VLS temporary-target cleanup | **ACCEPTED / COVERED** for normal success | the permanent scenario baselines same-class objects, retains the exact normal-success target reference/network ID, rejects an unexpected retry target, and proves deletion; retry, death, and cancellation remain unproven and outside this bounded closeout |
| locality and topology | **PARTIALLY COVERED** | headless/client-owned assets, ownership migration, client-N/JIP, disconnect, and poor-network behavior remain shared blocked/long-tail boundaries |

## Completion judgment

The core artillery execution contract is comprehensively reviewed and has
strong permanent causal coverage; no product or scenario change is justified
by this closeout. Literal matrices over artillery classes, terrain, magazines,
counts, and clients should not block program completion. The remaining cleanup contradiction is bounded: the broad fixture cleanup claim
does not itself prove deletion of the product-created VLS target. Cold run
`20260828T015701Z-5788cedb` closed that gap: all 19 server and 5 client feature
assertions passed (32 total including smoke), and the exact target row was
`id=2:213|position=[3000,2000,0]|ownedCount=1|null=true`. Evidence package
`urn:tribunal:evidence-package:20260828T015701Z-5788cedb:1`
(`sha256:0ef37936abe0ce7b878dbe8d73df34bd366fd210839a3504e02d75f4e40fe4e7`)
validated, was ingested twice idempotently, and the knowledge audit passed.
Behaviorally passing run `20260828T014649Z-88c344f1` used noncanonical contract
context keys; its package was rejected before mutation, never ingested, and is
calibration evidence only. Retry,
platform-death, and cancellation cleanup remain reviewed combinations rather
than reasons to expand this SHOULD item or block representative completion.

Requests beyond one magazine are a bounded reviewed gap because engine reports
indicate `doArtilleryFire` may stop at a magazine reload boundary. They should
be tested only if Vigil intends round count to exceed a single magazine.
Headless/client-owned artillery, client-b/JIP, and ownership migration remain
shared topology gaps and must not be inferred from this scenario. The
report-only/confirm-only VLS matrix is intentionally deferred, and broader
class/terrain/loadout combinations are optional long-tail coverage.
