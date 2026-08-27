# Pontifex remaining-work audit — 2026-08-27

This is the canonical documentation-only reconciliation of the Pontifex
feature-review and permanent-coverage backlog at product commit `7b54f51`. It
does not change a product contract, classification, scenario, test, or accepted
evidence package.

The audit reconciled all four addon configs and function trees, 41 durable
feature/boundary reviews, the inventory and reconnaissance records, and 29
product `TRIBUNAL_SCENARIO` declarations. The two framework scenarios
(`locality-probe` and `visual-framebuffer`) are not product coverage.

## Counting rules

* A reachable product outcome is one item even when several helpers implement
  it. A consumer-owned helper is not a separate uncovered feature.
* A shared topology boundary is counted once with affected consumers listed.
  Client-B/JIP, ownership migration, runtime module reconfiguration, and
  sound/presentation are therefore not repeated under every review.
* Extra class, map, threshold, and ordering permutations are omitted unless
  they can reveal a meaningfully different contract.
* Commented pages, empty registered functions, no-caller globals, and disabled
  diagnostics do not silently count as unfinished gameplay. They are explicit
  defer or retirement decisions.
* “Blocks review” means the current program cannot honestly call every retained
  reachable behavior reviewed. “Blocks coverage” means it prevents the scoped
  completion criterion below, not literal all-combination coverage.

## Post-audit closeout

* **A2 closed on 2026-08-27.** The Fabricator local virtual-inventory action
  gate is **REFINED; ACCEPTED / COVERED** by fresh run
  `20260827T223431Z-731a6c43`: authentic default-enabled module handoff, exact
  false/true published-state control, the same registered action, exact crate
  and station 10.32 m apart, client-a inactive/active observations, authority
  controls, and cleanup. Mixed per-module policy and runtime reconfiguration
  remain B2/C1 boundaries rather than part of this closeout.

## A. MUST FINISH

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Vigil; artillery request/execution and preview-marker lifecycle | **UNREVIEWED** (durable-record gap) | Two accepted `ScenarioReview` contracts exist, but unlike the other covered Vigil features there is no canonical `*-review.md` for either `vigil-artillery` or `vigil-markers` | Strong: both scenarios are permanent and accepted | The source/authority/false-PASS analysis and explicit free/deferred details are not preserved in the canonical review corpus. Runtime behavior is understood, but the review program's durable handoff is incomplete | None; documentation review only | **small** | **high** | **Yes** | No; evidence already exists | Write canonical artillery and marker reviews from source plus accepted metadata; do not rerun or reclassify them unless the review finds a real contradiction |

## B. SHOULD FINISH

These are valuable representative boundaries. They should improve confidence,
but their absence should not prevent declaring the narrowly stated current
program substantially complete after A1.

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Cross-mod locality; ownership migration/client-owned consequential objects affecting CORDIS, APS, Vigil governor/fixed-wing, Fabricator, towing, and object handling | **PARTIALLY COVERED** | Shared boundary is repeatedly identified and the one-client/server-owned contracts are clear | Routing primitives cover a stable owner; consequential features are mostly server-owned | Whether an accepted operation remains exact-once and cleans up when the target moves between server and client-a, and whether representative client-owned vehicles/objects complete correctly. Locality is a materially different topology, not a class permutation | Actionable with client-a for migration; true cross-client isolation belongs to C1 | **medium** | **high** | No | No, if current topology remains explicit | Build one shared migration probe, then prove only 1–2 high-consequence consumers (recommended: towing and APS or governor); do not clone it across every scenario |
| B2 | Cross-mod editor/curator lifecycle; runtime reversal, repeated placement, module deletion/reconfiguration | **PARTIALLY COVERED** | Eden initialization and one authentic curator direction are reviewed for APS, CBR, Vigil whitelist/fixed-wing, and Fabricator | Strong initial/one-direction coverage | Whether repeated/reverse operations in one display are idempotent, whether deleted/reconfigured retained Eden logic changes authoritative state, and whether state is retired. These are common lifecycle semantics, not five independent gaps | No external blocker; product policy is needed only where deletion semantics are intentionally unspecified | **medium** | **high** | No | No | Select one representative retained Eden feature and one reversible Zeus feature; record shared findings, then add feature-specific proof only if behavior differs |
| B3 | Field Utilities / Bridge Builder; interrupted construction, builder destruction, and resource/lease finalization | **PARTIALLY COVERED** | Stable build/removal and planner lease are reviewed | Normal build, traversal, scoped removal, and client-a lease are covered | Cleanup and lease/partial-chain outcome when construction is interrupted or the box disappears; resource policy is absent. A leaked lease or orphan chain affects real repeated use | Destruction behavior is actionable; any resource-consumption promise needs a product decision | **medium** | **medium** | No | No | Cover one abnormal cleanup path; keep resource economics deferred unless the product adopts them |
| B4 | Field Utilities / object handling; attached-object lifecycle | **PARTIALLY COVERED** | Exact server-owned crate/truck contact contract is reviewed | One matched treatment/control contact, attachment, replication, and normal teardown | Repeat contact, deletion while attached, and carrier/object cleanup can expose stale event/state leakage; broader class/surface matrices do not add the same value | None for server-owned deletion/repeat; migration is B1 | **small** | **medium** | No | No | Add one repeat-and-delete lifecycle continuation to the existing scenario; do not enumerate every crate/truck class |
| B5 | Vigil transport; abnormal terminal cleanup | **PARTIALLY COVERED** | Clear-corridor outbound/LZ/wait/RTB contract and hidden-pad engine requirement are reviewed | Strong normal and duplicate/unavailable coverage | Destruction/failure after dispatch but before landing, including pad/task/governor cleanup. This is a distinct terminal path; other helicopter classes and terrain are only breadth | No external blocker for destruction; remote cancellation policy belongs to C7 | **medium** | **medium** | No | No | Cover one causal in-flight destruction/failure path with exact terminal cleanup; leave class/terrain matrices optional |

## C. BLOCKED / NEEDS DECISION

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Program-wide multiplayer; client-B, isolation, concurrency, disconnect and JIP across CORDIS and consequential consumers | **EXTERNALLY BLOCKED** | Canonical boundary review is complete and affected features are enumerated | All accepted replication/audience claims are client-a only | A second independently authenticated player’s visibility, private-result isolation, simultaneous requests, disconnect retirement, and late-join retained state. This is the largest remaining topology gap | Second licensed Steam identity plus feature-specific retention/audience policies | **large** | **critical** | No; boundary is understood | No for the present one-client completion scope; **yes** for any future multi-client/JIP claim | Keep as one program epic; provision client-B, then select a small representative matrix (CORDIS fan-out/private receipt, one module, one stateful task, one physical ownership feature) |
| C2 | Program-wide presentation/audio; CORDIS radio/curator GUI, Vigil task messages, APS/Iron Dome/FPV sound and effects | **NEEDS PRODUCT DECISION** + **EXTERNALLY BLOCKED** | Routing and consumer call sites are reviewed; pixels/audio are deliberately excluded | Recipient decisions and debug gates are partly covered; actual sound and several GUI/effect outcomes are not | Choose audience, overlap/rate, failure visibility, and whether sound/beam/particles are promises; then observe actual target-client output. A call or receipt is not presentation | Sound-enabled observer; client-B for true audience isolation; product policy | **large** | **medium** | No | No unless presentation becomes a supported contract | Decide presentation policy once at program level, then cover only representative consumers; do not create a sound test per call site |
| C3 | Field Utilities / FPV-UAV modifications; small-UAV profile, IED, mortar and grenade payloads | **NEEDS PRODUCT DECISION** (reviewed/refine before coverage) | Canonical review identifies authority flaws and five explicit policy choices | No permanent gameplay scenario; ACE root composition only proves registration | Eligibility, inventory cost, payload exclusivity, attach/use authorization, finite-count enforcement, owner receipts, IED collateral causality, and physical mortar/grenade behavior. This is a reachable destructive feature and the largest retained uncovered subsystem | Product decisions, then owner-authoritative refinement before proof | **large** | **high** | No | No while explicitly decision-blocked; **yes** if retained as supported gameplay | Decide retain/redesign/remove. If retained, refine one request boundary, characterize ordnance, then add profile plus payload contracts; do not test current caller-trusting behavior as specification |
| C4 | Advanced Systems / CBR; multi-launcher clustering, warning cadence, origin isolation and concurrent expiry | **NEEDS PRODUCT DECISION** (reviewed/refine before coverage) | Canonical concurrency review complete | Strong single-launcher scenario only | Cluster meaning, merge/split/reassignment, warning unit/window, walking barrage, independent origin expiry, overload, owner-bound telemetry, and order invariance. Current results vary with firing-machine ownership | Eight listed product/arbitration decisions plus authority refinement; cross-owner equivalence eventually touches C1 | **large** | **high** | No | No while explicitly decision-blocked | Decide semantics, bind source owner/launcher, then cover same-owner close/far and reversed order first; cross-owner arm follows C1 |
| C5 | Advanced Systems / APS; experimental anti-drone mode | **NEEDS PRODUCT DECISION** (reviewed/deferred) | Canonical review complete | ACE preference/status is covered; drone engagement is not | Threat/side/operator policy, eligible UAVs, resource transaction authority, owner acknowledgment, cleanup, and handler scoping. Current destructive behavior is not safe to fossilize | Product decisions and refinement | **large** | **high** | No | No while experimental/deferred | Decide retain/refine/remove; if retained, establish one authoritative transaction and one causal UAV outcome before breadth |
| C6 | Advanced Systems / Iron Dome; client-owned artillery and threat policy | **NEEDS PRODUCT DECISION** | Core server-local interceptor review complete | Strong server-local enabled/disabled/out-of-range/concurrency coverage | Whether client-owned shells are supported and how they are owner-routed; whether friendly/outgoing shells or only protected-impact threats qualify. These choices alter gameplay and authority | Product policy; client-a can characterize ownership, client-B only for broader isolation | **medium** | **high** | No | No for explicit server-local contract | Decide protected-threat and locality policy; extend coverage only if scope expands |
| C7 | Vigil; task radio/chat/curator audience and remote cancellation/history policy | **NEEDS PRODUCT DECISION** | Feedback and governor reviews identify the split | Physical task lifecycle and one-client requester receipts are covered; task-message audience/cancellation/history are not | Requester/side/global/curator audience, empty-scope behavior, remote cancellation authorization, and whether durable history exists. These cannot be inferred from current default-global calls | Product policy; sound/pixels and client-B portions also depend on C1–C2 | **medium** | **high** | No | No | Decide audience and cancellation/history promises; then cover message/state delivery, not wrapper invocation |
| C8 | Field Utilities + Vigil logistics; airdrop direction/ETA announcement | **NEEDS PRODUCT DECISION** | Canonical map-helper review complete | Delivery is covered; feedback truthfulness is not | Whether direction means from/toward, ETA begins/ends at which events, intended audience, and whether ETA should exist. Current vacuum fall formula omits ingress/parachute descent | Product decision; accepted logistics timestamps already provide an oracle | **medium** | **medium** | No | No | Prefer either remove “ETA” or define one bounded interval, then characterize at two ingress distances before permanent proof |
| C9 | Vigil fixed-wing; UAV reconstruction/deploy | **NEEDS PRODUCT DECISION** | Rejection boundary and recon relationship are reviewed | Direct UAV request rejection plus manned control are covered | Whether physical UAV deployment is a supported feature and what control/locality/lifecycle it promises. Current explicit unstable guard means there is no positive contract | Product direction, then controlled engine experiment | **large** | **medium** | No | No while disabled | Retain the covered fail-closed rejection unless a concrete UAV product is approved; otherwise remove dormant positive-path code |
| C10 | Vigil fixed-wing; 3CB Hellfire mapping | **EXTERNALLY BLOCKED** | Reviewed as implemented-looking compatibility branch | No qualifying pylon comparison | Whether the mapping works with a compatible installed 3CB asset/pylon; it is compatibility, not core strike semantics | Deterministic compatible 3CB fixture/capability | **small** | **medium** | No | No | Keep explicit compatibility boundary; test only when the dependency supplies a qualifying row |
| C11 | Field Utilities / Fabricator; pond placement | **EXTERNALLY BLOCKED** and **OPTIONAL / LOW VALUE** | Placement contract and exclusion are explicit | Shoreline/all-water/gradient/obstruction cases are strong | Whether pond water is classified and sampled safely by the bounded placement algorithm on a loaded deterministic fixture | Deterministic loaded pond fixture | **small** | **low** | No | No | Do not block completion; add one pond A/B only when a stable fixture exists |

## D. INTENTIONALLY DEFERRED

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | Vigil; reconnaissance role/form/task/output | **INTENTIONALLY DEFERRED** | Fully reviewed as scaffolded/unreachable | UAV rejection boundary only; no recon success claim | The entire information product, eligibility, sensor/filter policy, task lifecycle, output, persistence and audience are absent. Testing would invent a product | A complete product design; overlaps C9 and C1 | **large** | **low** | No | No | Preserve as a named deferred product proposal, not unfinished coverage; remove scaffolding if the product is declined |
| D2 | Vigil; homepage task management and fossil UI navigation/admin controls | **RETIRE / REMOVE CANDIDATE** | Homepage reviewed; source audit found additional commented/unreferenced page/IDC fossils | None, appropriately | No reachable page, compatible server/client data shape, cancellation authority, or history policy. It matters as maintenance/confusion, not missing gameplay | Product choice to revive or remove | **medium** | **low** | No | No | Retire commented/unreferenced UI and empty admin/map design unless a task-management product is explicitly commissioned |
| D3 | Vigil; legacy helicopter stabilizer | **INTENTIONALLY DEFERRED** / **RETIRE / REMOVE CANDIDATE** | Controlled review/experiment complete; usefulness gates failed and automatic enrollment is off | No permanent promise; normal transport/CAS are covered without it | No proven useful physical outcome; future mechanism would be a rewrite, not a missing regression case | New design and fresh physical A/B | **large** | **low** | No | No | Keep disabled or remove legacy force code; do not resume coverage work |
| D4 | Cross-mod orphan/legacy source surfaces: developer laser harness; Field sling helper; Bridge direct-extension helpers; Field ID/location and Advanced marker helpers; `YOSHI_addItemsToFabricator`; empty core settings/utils; empty Field Zeus category; dead rope/tuning/UI constants | **RETIRE / REMOVE CANDIDATE** | Individually reviewed where consequential; current-source reachability reconfirmed. Remaining symbols have no supported caller or substantive behavior | None is required; the laser harness is explicitly excluded from accepted strike | Whether any external mission relies on globally named helpers is repository-unknowable. Retaining them expands attack/maintenance surface and confuses inventory, but coverage would bless unsupported APIs | External-consumer/deprecation policy before deletion | **medium** | **medium** | No | No | Publish a deprecation list, search known missions if available, then remove or capability-gate. Never add permanent scenarios solely to preserve no-caller code |
| D5 | Advanced/Common, Field shared libraries and cross-mod UI skins/wrappers; standalone helper contracts | **INTENTIONALLY DEFERRED** | Consumer-owned classification is reviewed | Consequential Fabricator, towing, logistics, APS/CBR/Iron Dome, Bridge, and debug outcomes cover representative use | Helper algorithms, private state, generic sounds, geometry/packing, safe-fall/fling, and styling are not independent user outcomes. More direct helper tests would couple the suite to replaceable mechanisms | A new reachable consumer with a distinct contract | **tiny** | **low** | No | No | Continue consumer-owned coverage; promote a generic primitive only after a second concrete consumer proves reuse value |

## E. OPTIONAL LONG-TAIL

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | All families; extra class/map/terrain/count/threshold matrices | **OPTIONAL / LOW VALUE** | Contracts and representative equivalence classes are established | Strong representative A/Bs across APS, aviation, Fabricator, Bridge, towing and cargo | Other aircraft/vehicle/crate/projectile classes, islands, coastlines, terrain beyond 15 m, packing permutations, exact thresholds and ACE versions. These matter only when they exercise a different adapter or policy | Fixture availability and maintenance cost | **large** | **low** | No | No | Add cases only for a reported defect, supported compatibility promise, or a new equivalence class; never pursue a Cartesian matrix |
| E2 | UI/effects; skins, pixels, cosmetic progress, hint layout, beam color/rendering | **OPTIONAL / LOW VALUE** | State/input contracts are reviewed; presentation exclusions are explicit | Real input plus framebuffer proof exists where causally useful | Exact visual styling and animation timing. Pixel tests are brittle and add little to authority/physical outcome confidence | Interactive/screenshot fixtures | **medium** | **low** | No | No | Keep a small visual smoke layer; do not turn cosmetics into program blockers |
| E3 | Engine-mechanism isolation; individual VLS report/confirm calls, CAS sensor/reveal dependency, alternative landing commands/classes, natural rope cuts and fallback geometry | **OPTIONAL / LOW VALUE** | Combined mechanisms or accepted outcomes are reviewed; hidden-pad combined requirement is characterized | Product outcomes are covered for bounded fixtures | Which internal substep is individually necessary and how alternate mechanics behave. This can aid future rewrites but does not expose an unproved current promise | Controlled fixtures; sometimes long physical runs | **large** | **medium** | No | No | Characterize only when planning a rewrite or diagnosing a regression |

## Ground-up completion estimate

This recalculation uses 100 normalized meaningful-surface units selected from
the current source: CORDIS 10, Advanced Systems 23, Vigil 35, Field Utilities
25, and cross-mod contracts 7. It does not inherit the prior estimate's credit.
Accepted causal contracts receive full coverage credit; bounded partials receive
credit only for their proven slice; decision-blocked, disabled, orphan, and
consumer-owned surfaces receive review credit when their boundary is understood
but no permanent-coverage credit for behavior they do not promise.

| Family | Feature-review completion | Permanent automated coverage | Interpretation |
| --- | ---: | ---: | --- |
| CORDIS | 97–100% | 83–89% | Core one-client broker is complete; presentation and changing ownership remain outside the proof |
| Advanced Systems | 91–96% | 70–78% | APS/CBR/Iron Dome cores are strong; anti-drone, CBR concurrency policy, and expanded Iron Dome threat/locality policy dominate the gap |
| Vigil | 94–98% | 88–93% | Operational tablet/task/aviation paths are strong; two durable review records are missing, while recon/homepage/UAV-positive behavior is consciously outside scope |
| Field Utilities | 93–97% | 81–88% | Fabricator/Bridge/logistics/towing and the local-inventory gate are strong; reachable FPV dominates the deficit |
| Cross-mod | 92–97% | 76–84% | Settings/composition/logistics are covered; migration and true multi-client/JIP are not |
| **Overall** | **94–97%** | **83–89%** | Review gap is small; coverage gap is concentrated rather than broad |

The useful second coverage view is the **completion-eligible stable contract
set**: reachable, retained behavior whose product policy and fixtures exist.
That set is approximately **92–95% covered**. The lower 83–89% portfolio number
keeps decision-blocked retained features such as FPV and anti-drone visible
rather than making them disappear from the denominator.

By estimated remaining effort rather than raw row count:

* **24–30% is actionable now** (A plus B).
* **40–46% is blocked or needs a product decision**; the purely external subset
  is about 8–12%.
* **16–20% is intentionally deferred or retirement work**.
* **12–16% is optional long-tail**.
* Therefore **70–76% of the remaining effort is presently
  blocked/decision-bound, deferred/retirement, or optional**, rather than a
  queue of ready feature iterations.

Tangible remaining work:

* **Meaningful actionable feature reviews:** 2 durable closeouts
  (`vigil-artillery`, `vigil-markers`); zero wholly uncharacterized reachable
  subsystems were found.
* **Meaningful permanent additions:** 0 MUST additions, or about **4–7**
  additions for the representative SHOULD boundaries. These are additions/arms,
  not necessarily 4–7 new scenario files.
* **MUST effort:** about **1 Sol-sized session** for the two documentation-only
  review closeouts.
* **MUST + SHOULD effort:** about **8–12 Sol-sized sessions**, depending mainly
  on physical Arma calibration and whether B1/B2 can share fixtures.

The five concentrations accounting for most meaningful future work are:

1. FPV/UAV product decisions, authority refinement, and physical payload proof.
2. CBR multi-launcher policy, authenticated telemetry, and concurrency proof.
3. Client-B/JIP provisioning plus a deliberately small representative matrix.
4. Representative ownership migration/client-owned consequential behavior.
5. Shared runtime module reconfiguration/reversal and abnormal lifecycle
   cleanup (including Bridge/contact/transport continuations).

## Completion criterion

Pontifex may be called **comprehensively reviewed** when:

1. every reachable retained product surface has a durable canonical review or
   accepted scenario review that states its user outcome, authority/locality,
   negative paths, false-PASS boundary, and disposition;
2. there are no critical/high-value **UNREVIEWED** surfaces;
3. every scaffold, disabled path, orphan, compatibility branch, and product
   decision is explicitly assigned to blocked, deferred, optional, or retire —
   never silently counted as covered; and
4. shared gaps are named once with affected consumers and an honest topology
   scope.

Pontifex may be called **well permanently covered** when every stable,
reachable, high/critical contract in the supported dedicated-server + one
authenticated-client topology has causal permanent proof with exact identity,
authority/locality, meaningful controls, replication where promised, terminal
outcome, and cleanup; no MUST coverage item remains; and all absent proof is
explicitly decision-blocked, externally blocked, intentionally deferred,
retirement-bound, or optional. Literal coverage of every class, map, threshold,
presentation pixel, helper, ownership permutation, and engine-command
combination is neither required nor desirable.

Under that criterion, completing A1 is sufficient to declare the
**current scoped program substantially complete**. B items improve maturity;
C items expand the supported product/topology only after their prerequisites
are resolved.

## Next candidate

The next gameplay coverage candidate after the two documentation-only review
closeouts is **B1, representative ownership migration/client-owned consequential
behavior**. Start with one shared routing/migration probe and only one or two
high-consequence consumers (towing plus APS or the governor); do not replicate
the topology matrix across every feature. This closeout does not begin that
work.
