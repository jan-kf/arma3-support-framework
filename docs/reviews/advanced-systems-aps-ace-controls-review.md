# LORICA APS ACE controls — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REFINED; ACCEPTED / COVERED for the current authenticated
client and server-owned vehicle.** Nearby living players within the established
10 m interaction bound and operational driver/gunner/commander crew are accepted;
cargo, distant actors, stale transitions, replay, and unknown operations fail
closed. Client-B/JIP and audible presentation remain deferred.

## Scope

In scope: the APS root, hard-kill off/reboot, soft-kill on/off, status, voice
on/off, and enable/disable action registration lifecycle. The separately reviewed
anti-drone submenu remains deferred. Audible playback remains unproven under
`-noSound`; this review treats only voice-state control.

## Canonical review questions

### 1. What should the user observe?

After APS installation, an eligible operator sees exactly the controls relevant
to authoritative hard/soft/voice state. A selected transition changes only that
vehicle once and returns a request-correlated authoritative result. Temporary
suspension preserves the installed root and exposes only the valid resume path.

### 2. What does the implementation actually do?

First installation publishes state and persistently registers one local action
tree. Every consequential statement now submits an operation name and unique ID
to one server endpoint. The server derives the only requester from
`remoteExecutedOwner`, checks alive/player identity plus nearby or operational-crew
eligibility, revalidates the exact current transition, rejects replay, applies the
mutation through a machine-local capability, and returns a targeted result.
Legacy direct handlers reject client-origin remote execution. Suspension leaves
the installed tree present so its mutually exclusive Resume action is reachable.

### 3. Which machines and lifecycle own it?

The server owns consequential APS/resource state. Every client owns its local
ACE tree and evaluates visible conditions. Persistent object-keyed remote
registration supports current clients and later execution but has no accepted
client-B/JIP proof. Server execution locality is not requester authorization.

### 4. Which mechanics are generic?

The installed-version concrete-class ACE adapter, exact active-node statement,
request receipts, actor/target identity, state replication, projectile A/B, and
cleanup are reusable Tribunal evidence. APS menu policy and mutations remain
Advanced Systems semantics.

### 5. Which behavior is product-owned?

Operator eligibility; valid hard/soft transitions; mutual exclusion; no-charge
reboot behavior; status facts; voice-state control; enable/disable action
lifecycle; and result policy are product-owned. Anti-drone policy remains outside
this contract.

### 6. Are unusual engine requirements proven?

Only the already-established ACE 3.21 concrete-tree adapter applies. No evidence
shows that direct public remote handlers, current menu nesting, persistent
remoteExec registration, or caller-supplied player identity are engine-required.

### 7. Which details are fragile or incomplete?

The ACE active-tree collector is version-bound private API, so the adapter must
continue to fail closed. Per-object action data retained locally is diagnostic,
not an outcome oracle. The replay cache is deliberately bounded, client-B/JIP and
ownership migration are unproven, and exact labels, top-level voice placement,
notification prose, status formatting, and sound timing remain non-contractual.

### 8. Is a better native/existing mechanism available?

The accepted design uses one narrow server request endpoint. It derives the
requester from `remoteExecutedOwner`, validates target/operator/current transition,
applies state through a server-local capability, and publishes a correlated
result. ACE conditions remain responsive presentation rather than authority.

### 9. What is the stable contract and causal proof?

A nearby living player or driver/gunner/commander sees the applicable active APS
controls. Invoking the exact active node reaches the authenticated server boundary,
changes only the selected vehicle once, and returns/replicates a truthful result.
Hard-off causes the calibrated threat to impact without engagement or consumption;
a charged reboot causes exact interception and one charge consumption. Soft on/off,
voice, anti-drone preference, suspension/resume, no-charge rejection, idempotency,
stale/replayed/unknown requests, crew acceptance, and distant rejection are
covered by exact state snapshots and request receipts.

### 10. Which details must remain replaceable?

Action IDs, labels, icons, nesting, ACE private arrays, request transport,
notification prose, status formatting, and audio files remain free behind the
adapter. Authoritative eligibility, exact target/state transition, truthful
result, and physical APS outcome are stable.

### 11. What remains unproven or requires decision?

Operator policy is resolved and covered for nearby players, driver, and the
distant negative; gunner/commander share the same explicit predicate but were not
separately seated in this one-client run. Cargo exclusion is implemented but not
a separate runtime assertion. Audible playback, client-B/JIP, ownership migration,
and anti-drone threat semantics remain separate. Exact labels/nesting/status prose
are not specification.

### 12. What belongs in Tribunal?

Reuse the generic ACE active-tree, request/locality, exact projectile, replication,
and cleanup capabilities. Do not promote LORICA action names, modes, charge/fuel
policy, or operator rules.

## Acceptance evidence and false-PASS boundary

Do not pass on an action stored in ACE namespace, `ActionsAdded_Local`, an inactive
node's directly invoked statement, local state, notification, or projectile
outcome alone. Compile the exact concrete target, prove the node active immediately
before invoking that registered statement, require a server receipt plus client
replication, and correlate physical state to the request.

Fresh autonomous run `20260820T222348Z-a22110d3` is the acceptance proof
(server 18/18, client 10/10). ACE 3.21 resolved the exact root with active
children, and the scenario invoked the statements from those exact active nodes.
Hard-off made projectile `2:156` physically impact with one charge unchanged and
no ledger event; reboot then made projectile `2:158` produce the exact hard-kill
event, no impact, and the final charge decrement. Soft off/on, anti-drone off,
voice off, no-charge reboot, suspension/resume preservation, idempotent resume,
stale transition, replay, crew acceptance, distant rejection, unknown operation,
and replicated result were all correlated to server receipts. Cleanup removed
client, server, network, and run state. Do not extend this evidence to client-B/JIP
or audible/visual presentation.
