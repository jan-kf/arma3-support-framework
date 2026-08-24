# Field Utilities object handling and supply loading — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: split outcome.** Explicit nearby supply loading is **REFINED; ACCEPTED / COVERED** for server-owned objects and one authenticated client. Automatic physical-contact attachment remains **REVIEWED / NEEDS EXPERIMENTATION** and outside that contract.

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

No. Fabricator evidence only established that the server's EntityCreated path
replicated `ace_cargo_size=-1` to a client-created box. It did not prove the
server-local contact handler fires for that nonlocal object. The required
locality of `setVehicleCargo`, `attachTo`, and contact EHs is uncharacterized.

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

Contact EH locality for server- and client-owned boxes; `setVehicleCargo`
locality/return/replication; full-capacity behavior; attachment collision
effects; and deletion/ownership migration.

### 12. What should be promoted into Tribunal?

Existing Tribunal mechanics are sufficient. The accepted cargo result supports one narrow generic setVehicleCargo lemma; Field Utilities rules remain project-owned.

## Acceptance decision

Explicit loading preserved the existing eligible families, 10 m geometry, and conservative two-Boolean capacity rule, but moved consequential mutation to authenticated server authority with exact receipts. Contact attachment remains a separate product decision and experiment.

## Disposition

**Split disposition.** Explicit nearby supply loading is REFINED; ACCEPTED / COVERED for the declared topology. Contact attachment remains REVIEWED / NEEDS EXPERIMENTATION.

## Accepted continuation — explicit nearby supply loading

This continuation supersedes the prospective cargo-loading statements above;
the automatic contact path remains at the original experimentation boundary.

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
full-carrier breadth, and unload UX are not claimed. Automatic contact
attachment remains REVIEWED / NEEDS EXPERIMENTATION because handler locality,
eligible surfaces, attach collision safety, detach, and cleanup remain unknown.
