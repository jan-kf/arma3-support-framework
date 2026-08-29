# Pontifex remaining-work audit — 2026-08-27

This is the canonical documentation-only reconciliation of the Pontifex
feature-review and permanent-coverage backlog, updated through the accepted
2026-08-28 B4/B5/B6/B7 closeouts. The original audit was
documentation-only; subsequent closeouts are recorded below with their exact
evidence.

The audit reconciled all four addon configs and function trees, 41 durable
feature/boundary reviews (43 after the two A1 closeouts), the inventory and
reconnaissance records, and 31
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
  controls, and cleanup. Mixed per-module policy and Fabricator-specific runtime
  reconfiguration remain optional/decision-bound and C1 boundaries rather than
  part of this closeout.
* **B1 closed on 2026-08-27.** Representative ownership migration is
  **REFINED; ACCEPTED / COVERED** by towing run
  `20260827T231228Z-1b3e79a7` and independent packaged repeat
  `20260827T233022Z-cc14d7dd`: both exact vehicles begin client-a-owned, the
  authenticated attach uses an owner-correlated parent acknowledgment, the
  same operation/ropes/relationship survive active transfer to server ownership,
  and requester stow finalizes once with full cleanup. Baseline regression
  `20260827T231436Z-dd11ab03` preserves server-local physical and rope-loss
  behavior. Reverse/partial migration, client-B/JIP, and feature-specific
  topology expansion remain explicit optional or separately blocked boundaries.
* **B2 closed on 2026-08-27.** Representative editor/curator lifecycle is
  **REFINED; ACCEPTED / COVERED** by Vigil whitelist run
  `20260827T235354Z-46c12195`: deleting one retained Eden source retires only its
  exact contribution on server and client, while three authentic same-target
  placements in one curator display produce add/remove/add without replay,
  leaked logic, or stale state. Other module families need lifecycle expansion
  only where their mechanics or product policy materially differ.
* **A1 closed on 2026-08-28.** Canonical
  [`vigil-artillery-review.md`](vigil-artillery-review.md) and
  [`vigil-artillery-markers-review.md`](vigil-artillery-markers-review.md)
  now preserve all 12 review questions. The accepted artillery and marker cores
  remain covered, but mods/evidence reconciliation narrowed broad cleanup
  claims into B6, B7, and C12 below.
* **B3 closed on 2026-08-28.** Bridge Builder interrupted construction is
  **REFINED; ACCEPTED / COVERED** by run
  `20260828T010359Z-31876e6c`: an authenticated client-a planner consumes its
  lease and starts an exact six-segment operation; after one partial segment is
  observed, deleting the builder retires that segment and the exact server
  operation record. All 25 feature assertions and smoke passed, cleanup was
  complete, and Evidence Contract v1 validated. Rejected diagnostic
  `20260828T005936Z-68c28e96` exposed and calibrated the cleanup control-flow
  defect; it is not accepted evidence. Production ingestion was idempotent,
  the knowledge audit passed, and reviewed distillation added no generic Arma
  finding. Remods/refund policy remains C13.
* **B4 closed on 2026-08-28.** `fieldutils-cargo-loading` Evidence Contract v1
  scenario version 3 proves authentic repeat contact/reattachment of the same
  server-owned crate and deletion while still attached, with exact server and
  client-a identity retirement. Run `20260828T014506Z-4977d65f` passed all 18
  feature assertions and complete cleanup; validated evidence was ingested
  idempotently and the knowledge audit passed.
* **B6 closed on 2026-08-28.** `vigil-artillery` now retains the exact
  product-created `Land_HelipadEmpty_F` VLS target and proves its fixed-delay
  deletion on normal success. Corrected run `20260828T015701Z-5788cedb` passed
  all 24 feature assertions and complete cleanup; validated evidence was
  ingested idempotently and the knowledge audit passed. The earlier
  metadata-rejected calibration package was never ingested.
* **B7 closed on 2026-08-28.** `vigil-markers` now re-arms a live three-strike
  preview through the real count handler and proves authenticated Escape retires
  the exact ellipses, ETA, and selected-asset overlay. Corrected run
  `20260828T015243Z-eba512d9` passed all 15 feature assertions and complete
  cleanup; validated evidence was ingested idempotently and the knowledge audit
  passed. The earlier metadata-rejected calibration package was never ingested.
* **B5 closed on 2026-08-28.** `vigil-transport` now includes a causal exact-aircraft destruction arm after the same authenticated request reaches stage 3, creates its product-owned landing pad, and remains airborne. Accepted run `20260828T031206Z-24d79c61` passed all 25 feature assertions: the same generation finalized failed, disabled its governor record, deleted exact pad `2:185` on server and client, delivered one requester terminal row, and retired all fixture identities. The run also preserves the full normal round trip. Package SHA-256 is `d71182836849bc8408a6949a1562532e17aa4e5500d788a354e8d7a1ff3f2bd4`; ingestion and reviewed project-specific distillation were each idempotent, and the knowledge audit passed.
* **C3 product decision implemented on 2026-08-28.** The legacy FPV payload surface was redesigned as the native eight-unit Pontifex Payload Manager. `fieldutils-payload-manager` run `20260828T130038Z-9f4e37a1` passed all 16 feature and smoke assertions with complete cleanup, proving themed separated inventory UI, live binding resolution, authenticated atomic transfer/refusals, UAV-owned ordering, replication, and audit. Evidence Contract v1 ingestion was idempotent and the knowledge audit passed. B8 below closes the positive in-control HUD/cycle/deploy causality; mortars remain intentionally deferred.
* **B8 closed on 2026-08-28.** `fieldutils-payload-control` run `20260828T133445Z-8924da44` passed all 19 feature and smoke assertions with complete cleanup. It proves an authentic terminal-linked `B_UAV_01_F` control session, client and server context rejection outside control, configurable Next/Deploy handling, current-binding themed HUD, occupied-only cycling, exact-once MiniGrenade and HandGrenade deployment, empty refusal, and an eight-unit SatchelCharge_Remote_Mag deployment that destroys its owning UAV. Server evidence correlates exactly five accepted and two rejected authority rows with three deployment receipts, exact effect classes/identities and same-moment UAV positions. Evidence Contract v1 ingestion was idempotent, the knowledge audit passed, and no generic Arma lemma was promoted (`PROJECT-SPECIFIC ONLY`).
* **C7 fully closed on 2026-08-28.**
  `vigil-task-queue` v2 run `20260828T215908Z-8d34ac9c` passed 9/0 server
  and 7/0 client feature assertions, with fresh authority/lifecycle regressions
  `20260828T214313Z-1ec1f993` and `20260828T214439Z-e370d418` also
  passing. It closes serialized per-asset FIFO/replacement admission, semantic
  duplicates, bounded history, activation/terminal messaging, and the compact
  themed cross-tab Assets display. Ingestion and reviewed project-specific
  distillation were idempotent and the audit passed. Operational task messages
  are side-wide. Any legitimate authenticated same-side tablet user may queue
  or explicitly overwrite an active asset task after confirmation. Confirmed
  overwrite is the retained cancellation operation; there is no separate
  remote-cancel product surface. Client-B delivery/isolation and simultaneous
  authority remain the shared C1 topology boundary, not unresolved C7 policy.

## A. MUST FINISH

There are **no remaining MUST items** under the scoped completion criterion.

## B. SHOULD FINISH

There are **no remaining SHOULD items** under the scoped completion criterion.

## C. BLOCKED / NEEDS DECISION

Only genuinely remaining C items appear below. Resolved C3, C5, C6, C7, C8,
C12, and C13 remain recorded in the closeout history above and are not counted
as remaining work.

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Program-wide multiplayer; client-B, isolation, concurrency, disconnect and JIP across CORDIS and consequential consumers | **EXTERNALLY BLOCKED** | Canonical boundary review is complete and affected features are enumerated | All accepted replication/audience claims are client-a only | A second independently authenticated player’s visibility, private-result isolation, simultaneous requests, disconnect retirement, and late-join retained state. This is the largest remaining topology gap | Second licensed Steam identity plus feature-specific retention/audience policies | **large** | **critical** | No; boundary is understood | No for the present one-client completion scope; **yes** for any future multi-client/JIP claim | Keep as one program epic; provision client-B, then select a small representative matrix (CORDIS fan-out/private receipt, one module, one stateful task, one physical ownership feature) |
| C2 | Program-wide presentation/audio; CORDIS radio/curator GUI and APS/Iron Dome/FPV sound and effects | **EXTERNALLY BLOCKED** + **INTENTIONALLY DEFERRED** for audio; **NEEDS PRODUCT DECISION** only for retained non-task presentation | Routing and consumer call sites are reviewed; Vigil operational task-message audience is resolved side-wide; actual audio is explicitly deferred | One-client task delivery and debug gates are partly covered; actual sound and several non-task GUI/effect outcomes are not | Audio verification waits entirely for a second authenticated client or better sound-enabled observer. Curator empty-scope plus failure/beam/particle presentation promises remain selectable policy. Side-wide Vigil task delivery across real clients is C1 proof only | Second authenticated client or better observer; non-task presentation policy | **large** | **medium** | No | No | Do no audio work now. Reopen one representative audio matrix only when the observer/topology exists; decide only retained non-task presentation promises |
| C4 | Advanced Systems / CBR; warning cadence, origin lifetime/audience, authenticated telemetry and cross-owner topology | **PARTIALLY COVERED** + **NEEDS PRODUCT DECISION** + **EXTERNALLY BLOCKED** | Observation storage and presentation decision resolved; canonical reviews updated | Run 20260828T175511Z-44e26fea proves eight independent timed/provenance rows, replication, real-map four-to-one zoom clustering, elongated capsule, non-destructive identities, no cap, expiry and the single-launcher baseline | Fixed cluster meaning, merge/split/reassignment, walking-barrage migration, aggregate shape and arbitrary cap are closed. Still decide warning unit/re-warning, confirmed-origin decay and global/side/radar audience; bind launch/update telemetry to authenticated owner/launcher; prove same-owner origin/warning isolation. Cross-owner/client-B/JIP remains C1 topology | Three product decisions plus authority refinement; cross-owner equivalence depends on C1 | **medium** | **high** | No | No while decision/topology bounded | Treat observation/presentation as closed. Decide warning, origin lifetime and audience together; then implement authority binding and one same-owner representative arm. Leave cross-owner/client-B to C1 |
| C9 | Vigil fixed-wing; UAV reconstruction/deploy | **NEEDS PRODUCT DECISION** | Rejection boundary and recon relationship are reviewed | Direct UAV request rejection plus manned control are covered | Whether physical UAV deployment is a supported feature and what control/locality/lifecycle it promises. Current explicit unstable guard means there is no positive contract | Product direction, then controlled engine experiment | **large** | **medium** | No | No while disabled | Retain the covered fail-closed rejection unless a concrete UAV product is approved; otherwise remove dormant positive-path code |
| C10 | Vigil fixed-wing; 3CB Hellfire mapping | **EXTERNALLY BLOCKED** | Reviewed as implemented-looking compatibility branch | No qualifying pylon comparison | Whether the mapping works with a compatible installed 3CB asset/pylon; it is compatibility, not core strike semantics | Deterministic compatible 3CB fixture/capability | **small** | **medium** | No | No | Keep explicit compatibility boundary; test only when the dependency supplies a qualifying row |
| C11 | Field Utilities / Fabricator; pond placement | **EXTERNALLY BLOCKED** and **OPTIONAL / LOW VALUE** | Placement contract and exclusion are explicit | Shoreline/all-water/gradient/obstruction cases are strong | Whether pond water is classified and sampled safely by the bounded placement algorithm on a loaded deterministic fixture | Deterministic loaded pond fixture | **small** | **low** | No | No | Do not block completion; add one pond A/B only when a stable fixture exists |

## D. INTENTIONALLY DEFERRED

| ID | Mod/family; feature/surface | Classification | Current review status | Current permanent coverage | Exactly what remains unknown or unproven; why it matters | Dependencies/blockers | Effort | Value | Blocks review? | Blocks coverage? | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | Vigil; reconnaissance role/form/task/output | **INTENTIONALLY DEFERRED**; dead scaffold **RETIRED** 2026-08-28 | Fully reviewed; unreachable form/state and empty post-init task were removed | UAV rejection boundary only; no recon success claim | The entire information product, eligibility, sensor/filter policy, lifecycle, output, persistence and audience remain deliberately absent. Fixed-wing role metadata and generic registry/task seams remain for a future coherent design | A complete future product design; overlaps C9 and C1 | **large** | **low** | No | No | Do not build or test recon now and do not restore the broken form/task scaffold. Add a real feature later through retained extension seams |
| D2 | Vigil; legacy homepage task management and fossil UI navigation/admin controls | **RETIRE / REMOVE CANDIDATE** | Homepage reviewed; source audit found additional commented/unreferenced page/IDC fossils; the resolved lightweight task surface intentionally lives on Assets | None for the fossil, appropriately; `vigil-task-queue` covers the retained replacement including confirmed overwrite | The old broad page remains unreachable and structurally incompatible. Its display/history purpose has been superseded, and no standalone cancellation requirement remains to justify it | External-consumer/deprecation check before deletion | **small** | **low** | No | No | Retire the commented/unreferenced homepage/admin/map scaffold; evolve only the compact Assets surface |
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
| Advanced Systems | 97–99% | 89–95% | APS projectile/anti-drone, Iron Dome impact, and CBR observation/presentation contracts are strong; CBR warning/origin/audience decisions and externally blocked client/HC artillery topology dominate the remaining gap |
| Vigil | 99–100% | 97–99% | Every meaningful retained stable surface has a durable review and representative proof; client-B/JIP is externally blocked while recon/UAV work is deferred or decision-bound |
| Field Utilities | 97–99% | 96–99% | Fabricator/Bridge/logistics, towing, object lifecycle, and both Payload Manager transaction and live-control contracts have representative proof |
| Cross-mod | 94–98% | 84–90% | Settings/composition/logistics, representative migration, and representative module lifecycle are covered; true multi-client/JIP is not |
| **Overall** | **98–100%** | **94–98%** | The scoped campaign is substantially complete; all remaining classified work is blocked, decision-bound, deferred, retirement-bound, or optional |

The useful second coverage view is the **completion-eligible stable contract
set**: reachable, retained behavior whose product policy and fixtures exist.
That set is approximately **99–100% covered**. The lower 94–98% portfolio number
keeps decision-blocked and externally blocked retained boundaries visible
rather than making them disappear from the denominator.

By estimated remaining effort rather than raw row count:

* Exactly **0% is actionable now** within the current scope.
* Approximately **48–55% is blocked or needs a product decision**; the purely external subset is about 20–25%.
* Approximately **24–30% is intentionally deferred or retirement work**.
* Approximately **20–27% is optional long-tail**.
* Therefore **100% of remaining classified effort is blocked/decision-bound, deferred/retirement, or optional**.

Tangible remaining work:

* **Meaningful actionable feature reviews:** **0**; zero wholly
  uncharacterized reachable subsystems remain.
* **Meaningful permanent additions:** **0** in MUST and **0** in SHOULD.
* **MUST effort:** **0 Sol-sized sessions**.
* **MUST + SHOULD effort:** **0 Sol-sized sessions**.

The five concentrations accounting for most potential future work are:

1. CBR multi-launcher policy, authenticated telemetry, and concurrency proof.
2. Client-B/JIP provisioning plus a deliberately small representative matrix.
3. Remaining CBR and non-task presentation decisions that must precede proof.
4. Native client/HC artillery topology plus fixed-wing UAV policy, only when their external/product boundaries change.
5. Retirement of unreachable legacy/orphan surfaces and optional compatibility/terrain matrices.

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

Under that criterion, the **current scoped campaign is substantially complete**. Every completion-eligible stable contract is reviewed and no MUST or SHOULD item exists. C items expand the supported product/topology only after prerequisites or decisions; D and E remain explicitly non-blocking.

## Next candidate

There is no actionable next candidate within the current scope. Resume only when a C dependency or product decision changes classification; do not pull D or E forward merely to create work.
