# Vigil asset whitelist Eden/Zeus activation — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** The accepted
unwhitelisted mixed-fleet browser remains covered. A configured Eden whitelist
and curator add/remove are real advertised entries, but their module dispatch,
synchronization replication, authority, duplicate policy, and exact client
membership have not been proven.

## Canonical review questions

### 1. What should the mission maker and curator observe?

A real Eden whitelist should restrict each client's browser to eligible vehicles
synchronized to that exact module. An authorized curator should add or remove one
exact selected vehicle, after which refreshed clients observe the same global
membership. Invalid, unauthorized, stale, or repeated requests must not alter it.

### 2. What does the implementation actually do?

The Eden module setter publishes one module object. Each client chooses either
all `vehicles` when that variable is nil or `vehicle _x` for every synchronized
object when configured, then applies existing category/side/live predicates.
The Zeus module chooses its first synchronized object or `attachedTo` target,
calls a global helper that adds/removes synchronization on the published Eden
logic, emits a notification, and deletes the transient logic.

No permanent scenario enters either configured module function. The accepted
browser scenario deliberately uses the no-whitelist path.

### 3. Which machines and lifecycle own it?

Both modules declare `isGlobal=0`, but actual framework execution locality is
unmeasured. The Eden setter has no server/class/locality guard. Zeus handling has
no server boundary, exact class, assigned-curator/requester validation, operation
identity, replay guard, acknowledgment, or proven propagation. The browser is
client-local and reads synchronization independently.

### 4. Which mechanics are generic?

Typed module/SQM Sync fixtures, configured-function receipts, exact object
identity/locality, actual curator placement characterization, client tree-row
extraction, and cleanup are generic Tribunal mechanics. Whitelist eligibility,
mutation policy, and refresh semantics remain Vigil product behavior.

### 5. Which behavior is product-owned?

Fallback-all versus restricted mode, one/multiple/empty-module policy, authorized
curators, valid target normalization, mission-global/JIP persistence, refresh
cadence, duplicate handling, and feedback audience are Vigil semantics.

### 6. Are unusual engine requirements proven?

No. `isGlobal=0` handler location, mission-native synchronization on clients,
runtime `synchronizeObjectsAdd/Remove` replication, curator attach target shape,
transient module deletion, and JIP persistence are unmeasured. Publishing the
logic reference does not prove that its synchronization graph is shared.

### 7. Which details are fragile or incomplete?

Last-setter-wins Eden globals, stale/deleted module references, zero-sync behavior,
normalized duplicate vehicles, first-target selection, missing authority/result,
client-local refresh, and CORDIS notification fallback are fragile. The helper is
globally callable and can attempt mutation without proving a curator entry.

### 8. Is a better native/existing mechanism available?

Keep native Eden/curator modules after measuring their transport, but hold the
authoritative whitelist in a server-owned exact-identity set. Native entries
should submit validated operations; clients should receive a deliberate snapshot
rather than depend on runtime synchronization replication. Do not select that
refinement until the genuine framework locality/requester values are captured.

### 9. What is the stable contract and causal proof?

For Eden, a fresh typed SQM module links exact eligible A, leaves same-class
eligible B unsynchronized, and links ineligible C. Actual configured dispatch and
server/client sync identities must be recorded; a real client refresh must have
exact backing/tree set `{A}`. An otherwise identical no-module mission must list
both eligible A/B and exclude controls.

For Zeus, one actual authorized placement adds B and a later placement removes B.
Exact logic/target/placer/owner receipt, authoritative membership, client backing
and tree net IDs, and cleanup must correlate. Invalid selection, unauthorized raw
call, replay, and stale/deleted-module controls must reach rejection and preserve
membership. Notification or synchronization state alone is not the oracle.

### 10. Which details must remain replaceable?

Module positions, logic IDs, synchronization/snapshot implementation, action
labels, tree grouping/order, refresh implementation, notifications, and handler
names remain free. Exact eligible membership, authority, global consistency, and
truthful result are stable.

### 11. What remains unproven or requires decision?

Choose authorized curator scope; one versus multiple Eden modules; zero-sync and
deleted-module behavior; duplicate normalized targets; immediate versus explicit
refresh; mission-global/JIP promise; and feedback audience. Typed Eden dispatch
and runtime sync locality need a bounded engine experiment before refinement.
Client-B/JIP remains separately deferred.

### 12. What belongs in Tribunal?

Reuse the first proven typed module/Sync fixture, real curator transport
characterization, exact net-ID sets, and browser tree observer. Vigil class names,
eligibility, whitelist policy, and mutation authorization remain product-local.

## False-PASS boundary and continuation

Directly calling the setter/helper, runtime-created plain Logic, a public module
reference, internal sync array, notification, deleted Zeus logic, or browser row
without exact dispatch and source identity does not prove the feature. Absence
requires an independently valid eligible object and a proven refresh stimulus.

Next: first establish the reusable typed Eden module fixture with a simpler
consumer; run whitelist/no-whitelist exact-set A/B; measure genuine curator
placement/locality/target resolution once; choose authority and lifecycle policy;
then refine to server-owned membership and prove add/remove plus adversarial
controls. Do not reopen the accepted unwhitelisted browser or use VNC unless real
curator placement cannot be characterized through native data APIs.
