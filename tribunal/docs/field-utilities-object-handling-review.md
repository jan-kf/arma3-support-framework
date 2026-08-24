# Field Utilities object handling and supply loading — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED (bounded split contract).** Explicit nearby supply loading remains **REFINED; ACCEPTED / COVERED** for server-owned objects and one authenticated client. Automatic physical-contact attachment is now **KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** only for a server-owned `B_supplyCrate_F` contacting a server-owned `B_Truck_01_transport_F`, observed by one remote client.

## Scope

In scope: `YFU_initObjectHandling`, `YOSHI_setObjectLoadHandling`,
`YOSHI_attachToBelow`, `YFU_initLoadingActions`, and
`YOSHI_getSuppliesAction`. Fabrication and towing are excluded.

## Canonical review questions

### 1. What should the user observe?

Pallets should become ACE draggable/carryable. Eligible supply objects near an
eligible carrier should expose an exact “Load Into” action whose successful
activation places that exact object in that exact carrier. The contact path
apparently intends boxes landing on a transport surface to attach there.

### 2. What does it actually do?

Server postInit sets every existing/new `ReammoBox_F` ACE cargo size to -1
and installs a local `EpeContactStart` handler. On contact it raycasts two
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
the hook globally. Nearby scans are broad, the action result is ignored, and
eligibility can go stale between menu creation and activation. Contact
attachment can make a cargo-action test appear successful. No detach, deletion,
full-carrier, concurrent-client, or error lifecycle is defined.

### 8. Is a better mechanism available and proven?

ACE cargo provides eligibility helpers, but that does not prove the current
local invocation is correct. No replacement is selected before locality and
return semantics are measured.

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

Existing Tribunal mechanics are sufficient. The accepted cargo result supports one narrow generic `setVehicleCargo` lemma. The contact A/B supports bounded generic observations about a server-local `EpeContactStart` callback and remote `attachedTo` identity; eligibility and automatic-attachment policy remain project-owned.

## Acceptance decision

Explicit loading preserved the existing eligible families, 10 m geometry, and conservative two-Boolean capacity rule, but moved consequential mutation to authenticated server authority with exact receipts. The existing contact hook is retained for the bounded server-owned crate/truck topology proven below; broader automatic-attachment policy remains open.

## Disposition

**Bounded split disposition.** Explicit nearby supply loading remains REFINED; ACCEPTED / COVERED for the declared topology. Automatic contact attachment is KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED for the declared server-local crate/truck topology.

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
