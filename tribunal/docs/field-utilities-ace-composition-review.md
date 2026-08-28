# Field Utilities cold-client ACE composition — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for normal cold-client registration and coexistence of the Bridge, Logistics, Virtual
Inventory, and Towing/Stow ACE class-action roots, plus the small-UAV Payload
Manager as a native world action with the legacy FPV ACE root absent. Their
consequential effects,
Fabricator's delayed per-object action, client-B, and JIP remain separate
contracts.

## Canonical review questions

### 1. What should the user observe?

After normal client initialization, each representative eligible object exposes
the relevant Field Utilities action roots. Actions inherited by the same object
coexist exactly once, while roots whose real conditions are false stay absent.

### 2. What did the implementation actually do?

`YFU_Client_initPlayerLocal` registers Bridge, Logistics, Virtual Inventory,
and Towing/Stow ACE actions plus the native small-UAV Payload Manager entry. ACE 3.21 records inheritance and, when
its menu is compiled for a concrete target, materializes inherited actions in
that concrete class tree. Querying only the abstract registration namespace is
therefore an invalid absence oracle.

The cold-run matrix found the expected roots on exact Bridge box, supply crate,
land vehicle, and UAV fixtures. A nearby native vehicle-cargo candidate made the
dynamic Logistics root active. With no Fabricator module the Virtual Inventory
root remained inactive; with no ropes and no driver the Stow root remained inactive. The Payload Manager
was present in the UAV native action list, and the retired `UAV_field_task` ACE
root was absent from both UAV and MRAP class trees.

### 3. Which machines and lifecycle own it?

The dedicated server owns the tokenized fixture objects. Each real client runs
the normal post-init registration and independently resolves its ACE action
tree. Registration grants presentation/reachability only; it does not confer
authority for an action's eventual statement.

### 4. Which mechanics are generic?

Installed-version ACE menu compilation, recursive action discovery, active-tree
resolution, exact net IDs, locality, and cleanup are Tribunal mechanics. Action
IDs, conditions, grouping, and effects remain Field Utilities semantics.

### 5. Which behavior is product-owned?

Which roots are registered on which class families, their coexistence, and
their relevance predicates are product-owned. Each feature review owns the
authorization and physical result of invoking a consequential child action.

### 6. Are unusual engine/framework requirements proven?

Yes, narrowly: on installed ACE 3.21, inherited class actions become observable
in the concrete class namespace only after compiling the menu for the exact
target. Cold run `20260820T011555Z-029ecabe` demonstrated the false-negative
abstract lookup; later runs proved the concrete-tree adapter. Native
`canVehicleCargo` also needed a bounded post-creation settle before it was a
valid positive stimulus.

### 7. Which details are accidental or fragile?

ACE's private namespace shape, action ordering, icons, labels, internal tree
nodes, initializer call order, and exact fixture classes are replaceable. The
scenario version-bounds the private adapter and fails closed if compilation or
tree resolution no longer works.

### 8. Are native/existing alternatives available?

ACE's own menu compiler and active-tree collector are the closest data oracle
for its real conditions and inherited composition. Repeated VNC camera/menu
driving adds visual timing noise without improving this nonvisual contract.

### 9. What is the stable contract and causal proof?

The stable contract is one expected root per concrete eligible class tree,
coexistence of overlapping roots, real relevance under independently established
object state, absence under real negative state, no statement execution, and no
mutation from discovery. Exact IDs/counts reject stale, missing, duplicated, or
mis-inherited actions. Server fixture and client action assertions are correlated
by exact net IDs, then all objects are removed before success.

### 10. Which details must remain replaceable?

Labels, icons, paths beneath the product root, ACE storage layout, initializer
organization, and interaction rendering are free to change. Coverage does not freeze effects or authorization of Towing, Payload Manager,
Fabricator, or cargo loading.

### 11. What remains unproven or deferred?

Fabricator's delayed object action depends on the unreviewed real module/sync
entry and is excluded. Client-B/JIP registration, repeated initializer
idempotence, action ordering, physical cargo loading and towing retain their existing classifications. Payload Manager authority/loadout and positive controller deployment are separately accepted by `fieldutils-payload-manager` and `fieldutils-payload-control`.

### 12. What belongs in Tribunal?

The installed-version concrete-class ACE adapter and exact fixture/state
observation are reusable. Field Utilities class names, conditions, and expected
composition remain in its scenario. No new visual adapter is warranted.

## Permanent evidence

Fresh autonomous run `20260828T131009Z-fe58f9cc` passed 2 server and 4 client feature assertions with zero failures, plus normal smoke. It proved five exact server-local fixtures, all six retained expected ACE roots, exact overlap and relevance, the native Payload Manager action on the eligible UAV, absence of the retired FPV ACE root, no cargo/rope/payload mutation, and exact cleanup. Evidence Contract v1 ingestion was idempotent and the knowledge audit passed.

Rejected calibration `20260828T130633Z-0f38bc21` proved the new native-action and ACE-absence assertions but exposed physical drift in the composition-only carrier fixture; it is not accepted evidence. Disabling fixture physics retained the required cargo eligibility without changing product code or weakening assertions. Older adapter/range/settle calibrations remain rejected for the reasons already recorded.