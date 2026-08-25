# Field Utilities object handling and supply loading — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: ACCEPTED / COVERED (bounded three-part contract).** Explicit nearby supply loading remains **REFINED; ACCEPTED / COVERED** for server-owned objects and one authenticated client. Automatic physical-contact attachment remains **KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** only for a server-owned `B_supplyCrate_F` contacting a server-owned `B_Truck_01_transport_F`, observed by one remote client. Selective ACE cargo preservation is now **REFINED; ACCEPTED / COVERED** for the exact `YFU_Bridge_Box` and `YAS_OPHANIM_box` classes while ordinary ammo boxes remain ACE-disabled.

## Scope

In scope: `YFU_initObjectHandling`, `YOSHI_setObjectLoadHandling`,
`YOSHI_attachToBelow`, the selective ACE cargo policy, `YFU_initLoadingActions`, and
`YOSHI_getSuppliesAction`. Fabrication and towing are excluded.

## Canonical review questions

### 1. What should the user observe?

Pallets should become ACE draggable/carryable. Eligible supply objects near an
eligible carrier should expose an exact “Load Into” action whose successful
activation places that exact object in that exact carrier. The contact path
apparently intends boxes landing on a transport surface to attach there.

### 2. What does it actually do?

Server postInit installs a local `EpeContactStart` handler on every existing/new
`ReammoBox_F`. It normally sets ACE cargo size to -1, but exact classes with
`YFU_preserveAceCargo = 1` are initialized through ACE's public size API and
restored to their configured size. On contact it raycasts two
metres down and attaches the box to the first non-`Static` hit, preserving a
derived heading. Existing/new pallets are made draggable/carryable.

Every client registers a dynamic ACE parent on pallets, boxes, land vehicles,
and small UAVs. It scans every `AllVehicles` within 10 m, admits pairs for
which both `canVehicleCargo` booleans are true, and creates a child that calls
`setVehicleCargo` locally. The return value is discarded and the child
condition is always true.

### 3. Which machines and lifecycle own it?

Initialization/contact handlers run on the server, but physics events and
attachments are locality-sensitive; behavior for a client-owned box is
unproven. ACE discovery and cargo mutation run on the acting client regardless
of box/carrier ownership. No server request, requester validation, operation
identity, acknowledgement, unload/finalizer, or ownership-migration path exists.

### 4. Which mechanics are generic?

ACE active-action resolution, object/cargo locality, exact `vehicleCargo`
membership, attachment identity, contact telemetry, and independent position
sampling are generic. Product eligibility and automatic-attachment policy are
Field Utilities concerns.

### 5. Which behavior is product-owned?

Eligible supply/carrier classes, capacity policy, authority, range, automatic
contact attachment, unload/detach behavior, failure feedback, and lifecycle are
product decisions.

### 6. Are unusual engine requirements proven?

Partly. The accepted explicit-load proof characterizes server-local `setVehicleCargo`. The new physical A/B proves `EpeContactStart` and `attachTo` only for server-local `B_supplyCrate_F` and `B_Truck_01_transport_F`, including remote observation. Client-owned objects, migration, and broader contact classes remain uncharacterized.

### 7. Which details are fragile or incomplete?

The first downward hit may be an unintended dynamic object. Every ammo box gets
the hook globally. Unmarked ammo-box classes deliberately remain unavailable to
ACE cargo, and other opt-ins are unproven. Nearby scans are broad, and
eligibility can go stale between menu creation and activation. Contact
attachment can make a cargo-action test appear successful. No detach, deletion,
full-carrier, concurrent-client, or error lifecycle is defined.

### 8. Is a better mechanism available and proven?

Pinned ACE 3.21 source and controlled runtime evidence now prove the public
`setSize`/`getSizeItem` path for the two exact opted-in boxes. Explicit native
loading remains a separate Field Utilities mechanism.

### 9. What is the candidate stable contract and causal proof?

Pending decisions, an authorized exact load request either places the exact
supply object into the exact carrier and returns a replicated success receipt,
or changes nothing. A separately enabled contact policy attaches only eligible
objects to eligible surfaces and records exact ownership.

Proof must split the paths. For explicit load, resolve/invoke the exact ACE
child and independently assert exact cargo membership on server and client.
For contact, prove the exact physical contact stimulus and exact attachment.
Negative controls must prove out-of-range/full/ineligible stimuli occurred.

### 10. Which details must remain replaceable?

Labels/icons, scan implementation, offsets, ray length/LOD, ACE helper choice,
transaction representation, and attachment/cargo mechanism.

### 11. Which mechanisms deserve characterization?

Contact EH locality for client-owned boxes; broader surface/class combinations; repeated contacts; `setVehicleCargo` client locality and full-capacity behavior; deletion while attached; and ownership migration.

### 12. What should be promoted into Tribunal?

Existing Tribunal mechanics are sufficient. The accepted native cargo result supports one narrow generic `setVehicleCargo` lemma. The contact A/B supports bounded generic observations about a server-local `EpeContactStart` callback and remote `attachedTo` identity. The selective ACE result is a Pontifex-plus-pinned-ACE product contract and adds no generic lemma.

## Acceptance decision

Explicit loading preserved the existing eligible families, 10 m geometry, and conservative two-Boolean capacity rule, but moved consequential mutation to authenticated server authority with exact receipts. The existing contact hook is retained for the bounded server-owned crate/truck topology proven below; broader automatic-attachment policy remains open.

## Disposition

**Bounded three-part disposition.** Explicit nearby supply loading remains REFINED; ACCEPTED / COVERED for the declared topology. Automatic contact attachment is KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED for the declared server-local crate/truck topology. Selective ACE cargo preservation is REFINED; ACCEPTED / COVERED for the exact Bridge and OPHANIM boxes on ACE 3.21.

## Accepted continuation — explicit nearby supply loading

This continuation supersedes the prospective cargo-loading statements above. The later contact continuation below supersedes the original experimentation boundary only for its declared topology.

The accepted contract is: a nearby authenticated player can invoke the exact
registered Field Utilities child for one eligible supply/carrier pair. Success
requires literal native command success plus exact isVehicleCargo membership on
server and client-a. Delivered replay, distant-requester, and wrong-class
requests fail without loading unrelated objects. Teardown unloads the exact
supply and deletes every fixture.

The refinement replaced the local fire-and-forget statement and literal-true
child condition with activation-time eligibility, remoteExecutedOwner
authentication, live-player resolution, server validation of class/state/range/
capacity, bounded replay keys, an exact pending claim, requester-only receipts,
and server verification of command return plus membership. Product eligibility,
the 10 m bounds, the conservative two-Boolean capacity policy, and result meaning
remain Field Utilities semantics. Labels, scan/order details, operation IDs,
audit layout, and the engine's internal representation remain replaceable.

Fresh autonomous run 20260824T135424Z-777de3e6 passed all 5 server and 4 client
feature assertions with zero failures and complete acknowledgments. Owner 4
invoked the exact ACE child; the server-owned B_supplyCrate_F loaded into the
exact server-owned B_T_VTOL_01_vehicle_F; the same isVehicleCargo identity
replicated to client-a; replay/range/class controls were delivered and rejected;
the unrelated supply remained unchanged; unload, deletion, containers, network,
and state all cleaned up.

The precursor run 20260824T135058Z-1b2764ad usefully disproved a scenario
assumption: native loaded cargo also reported the carrier through attachedTo on
both machines. Because that is not a promised outcome and exact isVehicleCargo
plus literal command success already excludes contact-only false passes, the
accidental post-load not-attached constraint was removed.

Sacred Texts documented setVehicleCargo's Boolean and canVehicleCargo's tuple,
but no locality rule. The accepted run directly supports one generic lemma,
scoped to Arma 2.22.153995, these two classes, server locality, dedicated
multiplayer, and client-a: server-local setVehicleCargo returned true and exact
isVehicleCargo membership was observed on both server and client. Authorization,
eligibility, replay, receipts, and cleanup stayed project-specific. No generic
Tribunal code was added; existing action-data, exact-identity, replication,
negative-control, Evidence Contract, and cleanup facilities were sufficient.

Client-owned objects, ownership migration, disconnect, client-B/JIP,
full-carrier breadth, and unload UX are not claimed. Automatic contact attachment outside the bounded server-owned crate/truck topology remains REVIEWED / NEEDS EXPERIMENTATION because client ownership/migration, broader eligible surfaces/classes, repeated contacts, and deletion while attached remain unknown.


## Accepted continuation — automatic contact attachment

The next-best unblocked candidate was the automatic contact hook. APS anti-drone, CBR concurrency, and FPV modifications remain behind product-policy decisions; client-B/JIP remains behind an independent identity; and the Fabricator mass defect had already rejected several isolated alternatives. The Opus reconnaissance was used only to identify possible collision risk. Source, canonical review, retrieved Sacred Texts, and a fresh controlled experiment established the conclusion.

The retained contract is deliberately narrow: when a server-owned `B_supplyCrate_F` physically contacts a server-owned `B_Truck_01_transport_F`, the existing server-installed hook attaches the exact crate to the exact truck. Client-a observes the same exact `attachedTo` identity. Controlled harness teardown removes the handler, freezes and detaches the crate, then deletes every fixture. This is cleanup evidence, not a user-facing detach promise. No promise is made for other classes or surfaces, client-owned objects, ownership migration, repeated contacts, deletion while attached, client-B, or JIP.

Final autonomous runs `20260824T152814Z-a9dd0df5` and `20260824T152942Z-0e8c4083` independently passed 9 server and 5 client feature assertions across the combined scenario (13 and 9 including smoke), with zero failures and complete acknowledgements. In the later run both matched server-local crates generated exact `EpeContactStart` observations against their identical parked trucks at force magnitudes `324.731` and `324.717`. Only treatment retained the product handler and attached to its exact truck; the handler-free control remained unattached. Client-a resolved the same treatment attachment while all four objects remained server-owned. Over four seconds treatment/control trucks reached only `0.148514`/`0.162602` m/s, retained minimum up-vector Z `0.999945`/`0.999726`, and displaced `0.026345`/`0.025389` m. Both began at zero damage and both damage deltas remained zero. Controlled handler removal, detach, and exact deletion completed. The preceding final repeat reported the same contact forces, treatment-only attachment, zero damage deltas, and comparably negligible motion.

The experiment also corrected an important false-PASS hazard. Raw final damage differed because the treatment truck already had `0.211829` damage at the pre-impact baseline while the control began at zero; both damage deltas were zero. A preliminary raw-final-damage comparison therefore could not support a collision-harm or retirement conclusion. A later repeat also showed that `detach` while the live handler remained in contact could immediately reattach; deterministic harness cleanup now freezes the crate and removes the handler first, while live-contact detach remains explicitly unclaimed. A trial bottom-offset refinement and a trial hook retirement were withdrawn after they failed to change that pre-existing asymmetry. No Pontifex product source change is retained.

Sacred Texts warns, through a community note rather than an official guarantee, that attaching PhysX containers can destabilize vehicles. That warning was not reproduced for this exact pair and duration, but the accepted result does not generalize beyond it. `disableCollisionWith` was rejected because the official documentation says it does not disable collision between PhysX objects. `setPhysicsCollisionFlag` was rejected as too broad and lacking a verified restoration/getter contract. Existing Tribunal exact-identity, physical-stimulus, causal-pair, locality, replication, delta, and cleanup mechanics were sufficient; no generic Tribunal runtime code was added. Evidence package `20260824T152942Z-0e8c4083` was ingested twice with unchanged counts (5 packages, 5 runs, 67 assertions, 33 observations, 8 proofs, 10 judgments), and the knowledge audit passed. Reviewed distillation added two build-scoped generic Sacred Texts lemmas: server-local `EpeContactStart` exact-contact observation and server-local `attachTo` exact client replication with bounded four-second stability. Distillation advanced to 14 reviewed findings, 6 lemmas, 6 proofs, and 7 propositions.

## Accepted continuation — selective ACE cargo preservation

The next-best unblocked candidate was the runtime ACE cargo-size override. The
Opus reconnaissance identified a possible contradiction but was not treated as
evidence. Canonical config declares `ace_cargo_size = 2` and
`ace_cargo_canLoad = 1` on both `YFU_Bridge_Box` and `YAS_OPHANIM_box`; both are
`ReammoBox_F` descendants, so the prior server hook replaced that declaration
with runtime size -1. Pinned ACE 3.21 source established that negative size
disables cargo interactions, that runtime variables precede config lookup, and
that `setSize` exits early when the requested size already equals the config
fallback. A controlled Live transition then reproduced runtime -1/ineligible,
size-2 restoration/eligibility, and re-disable behavior on both exact classes.

Pontifex now uses an explicit `YFU_preserveAceCargo = 1` class marker on only
the Bridge and OPHANIM boxes. The server hook transitions each opted-in object
through ACE size -1 and then its configured size. The first transition avoids
ACE's equal-size early exit; the second initializes ACE's globally replicated
can-load state and JIP action at the declared value. Ordinary ammo boxes retain
the previous size -1 policy. This is an additive ACE path, not a replacement or
claim about native vehicle cargo.

Permanent scenario `fieldutils-ace-cargo-policy` proves config/runtime parity,
ACE eligibility, an ordinary-box negative control, literal authentic ACE load
returns, exact loaded membership and attachment on the server, replicated size,
eligibility, membership and attachment on client-a, server ownership, and exact
cleanup. Unchanged sealed cold runs `20260825T202333Z-62ab9c1b` and
`20260825T202453Z-fd022bea` each passed 4/0 server and 2/0 client feature
assertions. Existing scenario `fieldutils-cargo-loading` then passed its full
native/contact regression in `20260825T202621Z-3b757834`.

Two calibration failures prevented broader false claims. Runs
`20260825T201455Z-8cc6488f` and `20260825T201903Z-fca893e1` showed that a live
native-capacity result was fixture-dependent and outside this proposition; it
was removed rather than converted into a product assertion. They also exposed
physics damage in active crate fixtures, so the ACE-only specification now
freezes and damage-protects its objects while retaining authentic ACE mutation.
An earlier config-only attempt failed because size lookup already returned 2
and ACE's early exit did not initialize runtime can-load state; that directly
motivated the two-step public-API transition.

Other opted-in classes, other ACE versions and carriers, client-owned objects,
ownership migration, client-B/JIP, menus, unload placement, concurrency and
interactions between simultaneous ACE/native requests remain outside the proof.
The evidence is product-specific; no generic Tribunal runtime facility or
Sacred Texts lemma is warranted. The accepted package was ingested twice with
unchanged second-pass counts; the knowledge audit passed. Reviewed distillation
advanced to 16 findings while retaining 7 generic lemmas and 1 conjecture: this
finding is `PROJECT-SPECIFIC ONLY`, so it added zero generic Sacred Texts notes.
The final ledger contains 18 packages, 19 runs and 416 artifacts. Post-ingest
`setVariable` revision 369355 and `getVariable` revision 369203 dossiers retained
only their upstream material, while the new project dossier exposes the bounded
Bridge/OPHANIM theorem and exact Tribunal provenance.
