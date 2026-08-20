# LORICA APS ACE controls — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REVIEWED / REFINE BEFORE PERMANENT COVERAGE.** The menu is a
real, reachable client entry and existing APS combat/state evidence remains
accepted, but visible ACE conditions are the only eligibility boundary. Server
handlers trust caller-supplied player/target arguments and return no correlated
result. Operator policy must be selected before refinement.

## Scope

In scope: the APS root, hard-kill off/reboot, soft-kill on/off, status, voice
on/off, and enable/disable action registration lifecycle. The separately reviewed
anti-drone submenu remains deferred. Audible playback remains unproven under
`-noSound`; this review treats only voice-state control.

## Canonical review questions

### 1. What should the user observe?

After APS installation, an eligible operator should see exactly the controls
relevant to authoritative hard/soft/voice state. A selected transition should
change only that vehicle once, report a truthful result, and update every
client's active tree. Disable should remove only APS-owned controls.

### 2. What does the implementation actually do?

Server enable publishes installed, hard-kill, soft-kill, voice, anti-drone, and
resource state, starts runtime work, and persistently remote-registers actions on
clients. Local registration is idempotent by an object variable. Hard-kill online
shows Off; offline shows Reboot and the applicable soft-kill toggle; voice On/Off
alternate by state; Status is available while installed. Disable clears runtime
state and removes exact action IDs.

Each statement directly remote-executes a globally named server handler with
caller-supplied target and player. Hard/soft handlers check only server context,
nonnull target, and installed state; voice and status do not require installation.
No handler binds `remoteExecutedOwner`, revalidates actor eligibility/proximity,
checks the current visible transition, rejects replay, or returns a request-ID
receipt.

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

Client-only eligibility, unauthenticated server handlers, absent request IDs and
results, stale stored statements, replay, uninstalled voice/status mutation,
local bookkeeping as registration evidence, top-level voice placement, exact
prose, and sound timing are fragile. A notification cannot prove acceptance or
correct recipient.

### 8. Is a better native/existing mechanism available?

Use one narrow server request endpoint like other accepted Pontifex authority
boundaries: derive requester from `remoteExecutedOwner`, validate exact target and
current transition, mutate server state, and publish a request-correlated result.
Keep ACE conditions as responsive presentation, not authority.

### 9. What is the stable contract and causal proof?

After choosing eligibility, prove uninstalled absence; exact root uniqueness;
hard-online Off relevance; registered-node Off request/receipt and replicated
state; refreshed Reboot/Soft relevance; Soft on/off alternation; charged Reboot
restoring hard and disabling soft without consuming a charge; no-charge Reboot
truthfully rejecting; voice-state alternation; disable removal; and clean
re-enable without duplicates.

Adversarial forged-player, ineligible/far actor, uninstalled target, stale
transition, and replay requests must each reach rejection and preserve exact
state/resources. One hard-off/reboot pair should reuse the accepted projectile
oracle: the same calibrated threat impacts while hard-kill is off and is exactly
intercepted after accepted reboot.

### 10. Which details must remain replaceable?

Action IDs, labels, icons, nesting, ACE private arrays, request transport,
notification prose, status formatting, and audio files remain free behind the
adapter. Authoritative eligibility, exact target/state transition, truthful
result, and physical APS outcome are stable.

### 11. What remains unproven or requires decision?

Who may operate APS—any nearby player, same-side player, current crew, engineer,
or another role—is unresolved and blocks implementation. Proximity/alive bounds,
voice menu placement, and status fact set also need selection. Anti-drone actions,
audible playback, client-B/JIP, and action cleanup on ownership migration remain
separate.

### 12. What belongs in Tribunal?

Reuse the generic ACE active-tree, request/locality, exact projectile, replication,
and cleanup capabilities. Do not promote LORICA action names, modes, charge/fuel
policy, or operator rules.

## False-PASS boundary and continuation

Do not pass on an action stored in ACE namespace, `ActionsAdded_Local`, an inactive
node's directly invoked statement, local state, notification, or projectile
outcome alone. Compile the exact concrete target, prove the node active immediately
before invoking that registered statement, require a server receipt plus client
replication, and correlate physical state to the request.

After operator policy is selected: add the authoritative request endpoint and
retired receipts, implement the active-tree/negative-control matrix, connect the
hard-off/reboot pair to the existing physical APS scenario, and prove unregister,
re-enable uniqueness, state restoration, and cleanup in one fresh run.
