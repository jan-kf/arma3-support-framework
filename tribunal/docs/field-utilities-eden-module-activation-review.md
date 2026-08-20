# Field Utilities Eden module activation — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** Accepted
Fabricator catalogue, transaction, packing, and delivery behavior remains valid.
Its permanent scenario manually creates generic Logic objects, adds runtime
synchronization, and directly calls the two setters; it does not prove the real
Eden configuration/function pipeline or authoritative catalogue provenance.
Field Utilities defines no Zeus activation tool.

## Scope

In scope: `FieldUtils_Virtual_Storage_Module`,
`FieldUtils_Fabricator_Module`, their configured setters, mission-native
synchronization, the local-inventory attribute, and the server catalogue/station
source. Already-accepted order semantics are downstream evidence only.

## Canonical review questions

### 1. What should the mission maker observe?

Real typed Eden modules should establish the exact synchronized catalogue and
Fabricator stations once on the authoritative server, publish the intended
client mirrors and inventory-toggle value, and make accepted orders use only
that mission-authored source.

### 2. What does the implementation actually do?

Both public Module_F classes use `isGlobal=0` and configured global setter names.
Each setter accepts any supplied object, assigns a public mission-namespace
logic reference, and broadcasts it; Fabricator also broadcasts its checkbox.
The authoritative order validator later reads those same public globals and
calls `synchronizedObjects` for catalogue/station membership.

The accepted scenario bypasses configured dispatch by creating plain `Logic`
objects, adding runtime synchronization, and directly calling both setters on
the server. It proves downstream semantics but not typed class reachability,
mission-SQM Sync links, framework execution owner/count, attribute serialization,
or client/JIP synchronization.

### 3. Which machines and lifecycle own it?

Intended module dispatch appears server-local, but no runtime evidence records
execution owner, logic locality, or `remoteExecutedOwner`. Setters have no
`isServer`, exact-class, locality, generation, or duplicate guard. Their public
mirror globals are also consumed as authoritative server input, so a client-side
publication or forged setter call is an unmeasured catalogue-provenance hazard.

### 4. Which mechanics are generic?

Typed mission module entities, validated Sync links, configured-function
receipts, execution locality, exact synchronized identities, attribute capture,
and adversarial publication observation are generic Tribunal mechanics. Virtual
Storage/Fabricator meaning remains Field Utilities policy.

### 5. Which behavior is product-owned?

The catalogue/station relationship, unlimited catalogue semantics, local ZEN
inventory switch, zero/one/multiple module policy, missing-counterpart behavior,
source authority, replication/JIP promise, and order refusal are product-owned.

### 6. Are unusual engine requirements proven?

No. `isGlobal=0` dispatch location, mission-native synchronization replication,
attribute serialization, retained `isDisposable=0` logic behavior, duplicate
module order, and JIP visibility are unmeasured. Runtime-created synchronization
was previously observed as unreliable client evidence and cannot substitute for
real SQM links.

### 7. Which details are fragile or incomplete?

Both module classes are omitted from `CfgPatches.units[]`; HEMTT reports that
explicitly. Equal priority plus unguarded assignment makes duplicate modules
last-writer-wins. Missing counterpart behavior is implicit. Public mirrors and
server authority share the same variables. Class validation, invocation count,
immutable source identity, and JIP are absent.

### 8. Is a better native/existing mechanism available?

Use the real Eden module framework and mission-native synchronization. After
measuring native dispatch, validate exact server-local typed modules and store
server-private authoritative identities/snapshots; publish separate client
mirrors. Server order validation must never trust a client-writable mirror.
There is no Field Utilities Zeus tool to invent or test.

### 9. What is the stable contract and causal proof?

A fresh mission must contain typed module entities, exact tokenized catalogue and
station objects, real SQM Sync links, and the checkbox value. Without direct
setter calls, record class/netId/configured function, invocation count, execution
owner/locality/request origin, exact sync sets, and published mirrors. Then reuse
one accepted exact order as an independent downstream oracle.

A same-fixture no-module run must produce no invocation and refuse the order. A
client-origin rogue-global/setter stimulus must demonstrably reach the boundary
and leave the server's original catalogue/stations and world census unchanged.
Missing/duplicate module cases follow only after their product policy is chosen.

### 10. Which details must remain replaceable?

Setter/global names, function priority, logic netIds, internal snapshot schema,
mirror transport, and scenario class choices remain free. Typed real dispatch,
exact mission-authored source, authoritative isolation, checkbox meaning, and
truthful downstream refusal/acceptance are stable.

### 11. What remains unproven or requires decision?

Choose whether missions permit exactly one of each module, how duplicates and a
missing counterpart fail, whether client/JIP synchronization is promised, and
whether the logics remain available after init. Actual module dispatch/locality,
SQM synchronization, checkbox serialization, and adversarial mirror poisoning
require one bounded engine run. The CfgPatches omission should be corrected with
that typed-entry proof rather than reported as the sole cause in advance.

### 12. What belongs in Tribunal?

A narrow validated typed-Logic plus Sync-link mission fixture belongs in Tribunal
only after this first consumer proves the representation. Arbitrary raw SQM and
Field Utilities class/sync semantics do not. Existing Fabricator transaction and
world-census oracles should be reused, not copied into generic code.

## False-PASS boundary and continuation

A config classname, direct setter call, plain Logic, runtime synchronization,
public global, internal receipt, or successful order after the scenario itself
registered the source cannot prove module activation. Absence without an exact
valid no-module stimulus also fails.

Next: add a typed mission-module fixture; run real module/no-module dispatch and
locality capture; select duplicate/missing-module policy; split authoritative
server source from public mirrors; reject rogue publications with receipts; then
rerun one accepted order and cleanup from a completely fresh mission. Keep the
full Fabricator scenario as downstream regression rather than re-testing it here.
