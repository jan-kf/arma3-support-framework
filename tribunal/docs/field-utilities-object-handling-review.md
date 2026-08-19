# Field Utilities object handling and supply loading — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REFINE BEFORE PERMANENT COVERAGE`.** Both shipped paths
are reachable, but neither has an authoritative, exact, fail-closed lifecycle.
Automatic contact attachment and explicit ACE cargo loading must be treated as
separate features during refinement and proof.

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

Nothing yet. Exact cargo membership and contact observation may be generic
after another consumer. Field Utilities rules must not leak into Tribunal.

## Decisions and first experiment

Decide eligible carriers/supplies, whether automatic contact attachment ships,
requester/authority, capacity failure, and unload/detach semantics.

Then use one Live session but isolated phases. First disable/avoid contact and
resolve the exact registered ACE child for tokenized server-owned box/carrier
IDs; invoke it and require literal command success plus exact replicated cargo
membership. Controls: out of range, full/ineligible carrier, wrong ownership,
and a second request with no collateral change. Separately drop the exact box
onto eligible and ineligible surfaces, recording contact, locality, attachment,
position, and cleanup. Never infer load from proximity, disappearance, or
movement alone.

## Disposition

**Reviewed, not covered; refine before permanent coverage.** The continuation
point is the product decisions followed by the separated locality/transaction
experiment above.
