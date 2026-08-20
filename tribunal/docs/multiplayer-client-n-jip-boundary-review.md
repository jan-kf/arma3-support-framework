# Multi-client and JIP proof boundary — canonical review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REVIEWED / DEFERRED — ENVIRONMENT DEPENDENCY;
FEATURE-SPECIFIC POLICY REQUIRED.** This is a proof-boundary review, not a
product defect. Existing accepted features retain their explicitly proven
single-client contracts.

## Canonical review questions

### 1. What should the user or integrator observe?

Where a feature promises sharing, two independently authenticated players should
observe only its intended authoritative state and audience. A genuinely late
joiner should reconstruct only state the product promises to retain; private UI,
request, and transient state must remain isolated.

### 2. What does the framework actually support now?

Tribunal's model is structurally client-N-aware: `ClientIdentity` requires unique
logical names, addresses, Steam homes, and optional diagnostic ports; scenarios
can declare identity-specific SQF and assertions. Pontifex orchestration remains
concretely single-client. It configures only `client-a`, generates one playable
slot with `maxPlayers=1`, emits client-a SQF/results, launches one container,
waits for one player, and finalizes server plus one client result.

### 3. Which machines and lifecycle own it?

The dedicated server and one independently authenticated Steam/Proton client are
currently owned and observed. There is no second authenticated App 107410 home,
second slot, second launch lifecycle, or per-identity result stream. Renaming
client-a or executing client-b-labelled code on it does not create a second
identity.

### 4. Which mechanics are generic?

Unique identity/resource validation, per-client mission code/assertions, launch
and cleanup lifecycle, exact owner/netId/address evidence, late-join timing, and
result-origin validation are Tribunal/Pontifex mechanics. Visibility, retention,
audience, concurrency, ownership migration, and disconnect policy remain
feature-owned.

### 5. Which behavior is product-owned?

Each feature must define what B may see, whether state is persistent for JIP,
which side/audience receives feedback, how concurrent requests interact, and
what disconnect/reconnect does to work and results. There is no safe universal
JIP policy to infer from `publicVariable` use.

### 6. Are unusual engine requirements proven?

No multi-client or JIP engine behavior is characterized. Current locality probes
prove only server → client-a → server. A second Steam identity and concurrent
Proton capacity are operational dependencies, not product workarounds.

### 7. Which details are fragile or incomplete?

`allPlayers[0]`, hard-coded client-a identity/result origins, one Steam home,
one network record, one slot, one completion state, and one log/process stream
are deliberate current bounds. Scenario `future_client_*` metadata is design
intent, not evidence.

### 8. Are native/existing alternatives available?

The existing Tribunal identity model should be extended rather than duplicated.
No synthetic identity, relabelled log, server-only state inspection, or reused
Steam session can substitute for an independently authenticated second client.

### 9. What is the stable future contract and causal proof?

The eventual generic matrix must prove:

1. distinct names, UIDs, player netIds, owners, containers, addresses, Steam
   homes, and result origins for A and B;
2. true late join by creating tokenized state with A before launching B;
3. intended shared authoritative state plus positive absence of A-private state
   on B;
4. exact same-side/opposing-side audience receipts and non-receipts;
5. token-distinct competing requests with the feature's selected policy;
6. requester disconnect, exact work disposition, reconnect, and stale-result
   rejection.

Each phase fails on missing identity, timing, recipient, isolation, result, or
cleanup evidence.

### 10. Which details must remain replaceable?

Container names, bridge addresses, optional VNC ports, profile names, launch
order implementation, artifact layout, and assertion transport are free. The
independent account/session, exact identity, true late-join ordering, and
feature-specific result are not.

### 11. What remains unproven or deferred?

APS/CBR/Iron Dome replication, Vigil and Field Utilities replicated state,
request isolation, audience fan-out, competing requests, disconnect/reconnect,
ownership migration, and true late join are proven only where their reviews say
client-a. A second independently authenticated Arma account plus feature policy
is required before reopening.

### 12. What belongs in Tribunal?

Identity-aware orchestration, slots, per-client code/results/artifacts, true
late-join sequencing, and generic isolation/audience evidence belong in the
framework. No product sharing or retention rule belongs there.

## False-PASS boundary and continuation

Never count relabelled client-a SQF, simultaneous starts called JIP, server-only
public-state inspection, an object without required metadata, absent B telemetry,
a shared Steam home/ticket, or prior-run/pre-join state as client-B/JIP proof.

After provisioning a second licensed account and persistent independent Steam
home: generate at least two slots, launch/observe both identities independently,
then run the identity, late-join, sharing/isolation, audience, contention, and
disconnect matrix. Add feature-specific scenarios only after each feature chooses
its visibility and lifecycle policy.
