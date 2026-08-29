# Vigil task governor — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REFINED; ACCEPTED / COVERED** for the one-client declarative
request-authority boundary, server-owned terminal lifecycle, bounded per-asset
queue/replacement/history policy, compact operational display, side-wide
operational task messages, and task authority for legitimate tablet users.
Existing artillery, transport, and CAS scenarios retain their accepted physical
consumer outcomes. Client-N/JIP, ownership migration, headless/client-owned
vehicles, and fixed-wing separate lifecycle remain excluded.

## Scope

This review covers shared task construction, assignment, stage progression,
terminal handling, finalization, and dispatch in
`functions/governor/fn_governor.sqf`, plus the real artillery, transport, and CAS
submission paths. The legacy homepage task UI remains a retirement candidate;
the resolved lightweight task surface lives on the reachable Assets page.
Questions 2–8 below record the pre-refinement source findings; the accepted
continuations record the resulting product contract and evidence.

## Canonical review questions

### 1. What should the user or integrator observe?

A valid Vigil request should create at most one active authoritative task
generation for its selected vehicle, queue non-equivalent work FIFO within a
small bound, or replace the active generation only through an explicit confirmed
operation. Work progresses through task-specific stages, publishes truthful
activation and terminal results, retains bounded recent history, and cleans its
owned resources. Invalid or task-equivalent requests must not consume capacity
or disturb active work.

### 2. What does the implementation actually do?

The server CBA handler advances normal `advance` returns through
init/start/mission/end/finally. Accepted consumer scenarios prove several such
world outcomes. The abnormal paths are not coherent:

* clients construct tasks containing executable handler code and submit that
  hashmap for execution on the server;
* generic artillery assignment replaces the vehicle-keyed manager without an
  active-task check;
* public cancellation only changes `state` to `cancelled`; a non-running task
  outside FINALLY then exits every tick without its finalizer;
* the dispatcher disables a dead vehicle's record before `YSF_taskTick`, so the
  finalizer never runs;
* a handler `fail` or `cancel` enters FINALLY and runs that handler on the next
  tick, but the early non-running return skips record disablement afterward;
* `complete` before FINALLY jumps directly to DONE and can skip cleanup despite
  its source declaration saying it enters FINALLY;
* unknown returns normalize to unbounded `wait`; no shipped handler uses the
  nominal retry path, so retry/watchdog semantics are uncharacterized.

Successful records are disabled but never retired from the registry.

### 3. Which machines and lifecycle own it?

Only the server starts the CBA dispatcher and owns the manager registry. That is
execution locality, not an authority boundary: normal clients author and transmit
the executable handlers and opaque parameters. Specialized transport/CAS
endpoints reject an active duplicate but do not authenticate the requester,
validate a declarative schema, or build registered handlers server-side. Generic
artillery lacks even the duplicate guard. Current fixtures use server-owned
vehicles; headless/client-owned AI is unproven.

### 4. Which mechanics are generic?

Tokenized callback order/count, bounded timing, object identity/locality, request
receipts, and cleanup observation are Tribunal mechanics. Vigil owns task types,
stages, eligibility, terminal policy, and finalizers.

### 5. Which behavior is product-owned?

The accepted request schemas, one-active-task policy, task-specific equivalence,
FIFO/replacement admission, cancellation authority, registered server handlers,
ordered lifecycle, terminal causes, exact-once finalization, result
acknowledgment, bounded recent history, and operational snapshot are Vigil
semantics.
CORDIS supplies transport/dedupe mechanics only; it does not authorize the
code-bearing payload or prove its execution.

### 6. Are unusual engine requirements proven?

No. There is no evidence that Arma requires client-serialized code, random IDs,
rounded vehicle signatures, the current PFH cadence, or a two-tick terminal path.
These are implementation choices, not characterized requirements.

### 7. Which details are fragile or incomplete?

Client-authored code, generic overwrite, vehicle-string keys, random request
identity, objNull/hashmap type confusion, invalid-return-as-wait, unused retry,
uncorrelated results, divergent terminal paths, and retained records are all
false-PASS or lifecycle risks. CAS installs successor work during finalization,
so a rewrite must disable/retire only the exact finishing generation rather than
a newly installed task.

### 8. Is a better native/existing mechanism available?

Keep server CBA scheduling, but make client requests declarative and validated.
Task-specific server endpoints should authenticate the requester and asset,
build registered handlers locally, and return request-correlated acceptance and
terminal results. A single generation-aware terminal path should run the exact
finalizer once and then retire or disable that same generation.

### 9. What is the stable contract and causal proof?

A server-accepted typed request creates one generation. Ordered stages execute;
`wait` may repeat without advancing. Normal completion, early completion,
handler failure, accepted cancellation, invalid/deadline result, and vehicle loss
each produce the correct terminal cause, invoke the exact finalizer once, remove
owned resources, and produce no later callbacks. Duplicate, replay, wrong-asset,
malformed, and forged-handler stimuli must reach rejection, preserve existing
work, and never execute caller code.

Proof needs exact boundary receipts, task generation, stage/finalizer counts,
terminal result, manager disposition, and owned-resource census. Consumer world
state alone is not the governor oracle.

### 10. Which details must remain replaceable?

Numeric stages, return strings, PFH cadence, map/key layout, task ID format,
private signatures, record storage, and debug messages are free. Preserve
validated declarative authority, one-active policy, task-specific duplicate
semantics, bounded FIFO/replacement behavior, activation/terminal messaging,
bounded recent history, truthful terminal state, exact-once finalization, and
cleanup.

### 11. What remains to characterize or decide?

The declarative server-built request boundary, FIFO queue, confirmed
replacement, bounded recent-history policy, task authority, and task-message
audience are resolved. Any legitimate same-side Vigil tablet user may queue work
or explicitly overwrite the active task after confirmation. That overwrite is
the retained cancellation operation; no separate remote-cancel product surface
exists. Operational task messages are side-wide. Retry versus consumer bounds
and invalid-result handling remain separate low-frequency lifecycle policy;
headless/client-owned vehicles, ownership migration, client-N and JIP remain
topology boundaries.

### 12. What belongs in Tribunal?

Initially only scenario-local tokenized callback receipts and existing
locality/cleanup assertions. Do not promote Vigil's stage machine or hashmap
schema. A generic callback/order observer requires a second real consumer.

## Precise continuation

1. In one retained Live session, use harmless server handlers to record normal
   ordered stages with repeated waits, failure, cancellation, early completion,
   and vehicle death. Require the exact finalizer count and manager disposition.
2. Exercise the real client request boundary with valid, duplicate/replay,
   wrong-asset, malformed, and harmless forged-handler-sentinel requests.
3. Replace all three code-bearing client paths with typed data and server-built
   registered tasks. Add one generation-aware terminal/finalizer path and
   correlated acceptance/terminal receipts.
4. Add a permanent Tier 2 governor lifecycle scenario, then rerun fresh
   artillery, transport, and CAS scenarios as consumer regressions.

A local task injection, product vehicle status, `enabled=false`, deleted fixture,
handler result string, or consumer success cannot independently prove this
contract. Cleanup must be observed before scenario teardown, and an absent forged
sentinel counts only after an exact rejection receipt proves the stimulus reached
the boundary.

## Accepted continuation — server-owned terminal lifecycle

The first unblocked slice was the server-owned terminal state machine. The Opus
reconnaissance supplied only possible inspection points; canonical source and a
predeclared cold baseline established the defects. Run
`20260825T223715Z-d822d2ff` completed with normal order and cleanup controls but
failed 6/9 product assertions: early completion skipped its finalizer; failure
finalized but remained enabled; cancellation never entered FINALLY; vehicle loss
was pre-disabled; active assignment overwrote the original generation; and the
early-complete parent never installed its successor.

Pontifex now routes normal FINALLY, early `complete`, handler failure, accepted
server cancellation, and vehicle loss through one exact-once finalizer. A task
records `finalizing`/`finalized` privately; active replacement is rejected unless
the exact current generation is inside its finalizer. Retirement disables only
the finishing record, so CAS-style finalizer installation of a successor creates
a new enabled record that the predecessor cannot disable. Terminal cause is
preserved as `complete`, `failed`, or `cancelled`.

Permanent scenario `vigil-governor-lifecycle` stops the scheduler temporarily,
isolates the manager, constructs only harmless server-local handlers, and drives
bounded exact ticks. It records callback order, repeated wait, finalizer count,
owned-pad deletion, terminal cause, manager enablement, rejected-sentinel
nonexecution, predecessor/successor id and generation, a client completion
receipt, and full restoration. Cold runs `20260825T224551Z-057295d6` and
`20260825T224723Z-f0515a23` each passed 9/0 server and 1/0 client feature
assertions with complete cleanup.

The fresh combined artillery/transport/CAS regression
`20260825T224845Z-b0838bdc` passed every artillery and transport assertion and
all governor-relevant CAS boundaries, including accepted dispatch, duplicate
rejection, finalizer-installed RTB successor, home, no-target/no-ammo, and
cleanup. It failed only `vigil.cas.attack.effect`: correlated fire and a
target-local damage event were observed, but net damage remained zero. An
isolated unchanged CAS repeat `20260825T230059Z-fa050097` reproduced only that
same physical-effect failure while again passing the entire governor lifecycle.
Neither failed run is accepted evidence for CAS combat effect, and no speculative
fixture or governor change was made for it.

This continuation does not accept client-authored handler maps. Declarative
request schemas, requester/asset authentication, forged-payload rejection,
cancellation eligibility, retry/invalid-return policy, terminal-history
retention, headless/client-owned vehicles, client-N, and JIP remained behind the
mandatory authority rewrite at that lifecycle-only checkpoint.

The accepted Evidence Contract was ingested twice with unchanged second-pass
counts, and the Sacred Texts audit passed. The final ledger has 21 packages, 22
runs and 474 artifacts. Reviewed distillation advanced to 20 findings and 8
intentionally project-specific results while retaining 7 generic lemmas and 1
generic conjecture. Both lifecycle propositions are `PROJECT-SPECIFIC ONLY`, so
this continuation adds zero generic Sacred Texts notes.

## Accepted continuation — declarative request authority

The remaining mandatory slice crossed all three live rotary/artillery submission
paths and was the highest-value unblocked item in the canonical inventory. The
Opus reconnaissance was used only to locate likely boundaries. Direct source
inspection and the Sacred Texts dossiers for `remoteExec` and `CfgRemoteExec`
established the relevant constraint: transport filtering delivers a call but
does not authenticate the product-level requester or authorize an opaque
executable payload.

Pre-change run `20260825T232521Z-22a1ad6d` was the declared discriminating
baseline. The fixture passed, but 8/9 server feature assertions and 1/2 client
feature assertions failed: no declarative request was audited or accepted, no
server-built task/result existed, and the legacy client code-bearing task map
reached the old broker instead of failing closed.

Pontifex now exposes one registered data-only endpoint for artillery, transport,
and CAS. It captures `remoteExecutedOwner` at the transport boundary, hands the
worker a machine-private token, verifies the claimed owner against the transport
owner, and resolves that exact player from the authoritative server set. The
server validates task type, bounded schema, live same-side asset, optional
whitelist membership, replay and one-active-task state; only then does it build
registered handlers and assign the generation. Vehicle registry keys use stable
network identity. The 120-second replay cache and 128-row server-private audit
are bounded. Accepted, rejected, and terminal receipts carry the request ID and
are targeted only to the requester. All legacy client task-map endpoints fail
closed, so caller code is neither stored nor executed.

Permanent scenario `vigil-governor-authority` proves all three valid declarative
schemas; server-built provenance; forged-requester, wrong-side, malformed
code-bearing, unsupported, replay, and busy rejection; generation preservation;
legacy sentinel nonexecution; requester-only correlated receipts; terminal
results; and complete restoration. Final cold runs
`20260826T005042Z-308c99c8` and `20260826T005206Z-0fb17055` each passed 9/0 server
and 2/0 client feature assertions.

The affected regression batch `20260826T001620Z-30bd6992` completed artillery
and governor lifecycle with all assertions passing and passed every CAS
authority/state boundary. It reproduced only the already isolated
`vigil.cas.attack.effect` zero-net-damage failure, then reached the batch timeout
while transport was returning. Isolated transport run
`20260826T002703Z-96a8f56c` passed completely. The timeout and known CAS physical
effect failure are not accepted evidence packages and do not weaken the new
authority propositions.

Remote cancellation eligibility, queue/replace beyond reject-active, durable
terminal history, retry/invalid-return policy, headless/client-owned vehicles,
client-N, JIP, ownership migration, and network interruption remain excluded.

The accepted authority Evidence Contract was ingested twice with identical
second-pass counts and the Sacred Texts audit passed. Reviewed distillation now
contains 22 findings: 10 intentionally project-specific, 7 generic lemmas, and
1 generic conjecture. Both authority propositions are project-specific, so this
continuation adds zero generic Sacred Texts notes.

## Accepted continuation — bounded queue, history, and operational display

The resolved product decision keeps exactly one active governor generation per
asset. Up to four non-equivalent requests queue FIFO. Equivalence is
task-specific: artillery compares ordered strike positions and ordnance,
transport compares mode/options/altitude/destination, and CAS compares target,
altitude, and duration. A fifth queued request fails atomically. Explicit
replacement uses its own slot, requires client confirmation, cancels the exact
active generation, activates ahead of the FIFO, and does not reorder that FIFO.
Server ingress is serialized so concurrent remote calls cannot scramble
admission order.

Every newly active queued task emits its correlated start result and every
terminal task emits the existing correlated terminal result. Each manager keeps
only its eight newest terminal summaries. The replicated side-tagged
operational snapshot contains data only, never handler code. While the real
tablet is open, the Assets map draws every friendly active governor-managed
artillery, transport, and rotary-CAS asset plus its current target line.
Off-tab entries use 30 percent of the configured theme alpha; current-tab
entries use full configured alpha. A compact selected-asset status/history
display and the map refresh approximately every three seconds. Fixed-wing
retains its separate registry lifecycle and is not falsely included.

Permanent scenario `vigil-task-queue` uses one authenticated client, real
server request ingress, real transport/artillery managers, real tablet controls,
and an authenticated framebuffer tab driver. Accepted run
`20260828T215908Z-8d34ac9c` (Evidence Contract v2) passed 9/0 server
and 7/0 client feature assertions: independent actives, exact semantic duplicate
rejection, four-entry bound, explicit replacement priority, fail-closed second
pending replacement, exact FIFO activation, eight-entry history,
activation/terminal receipts, side snapshot, cross-tab opacity, configured
theme RGBA, movement refresh, compact status/history, and complete restoration.
The permanent static contract separately guards the real client confirmation
dialog and all three reachable Replace controls.
The immutable package file SHA-256 is
`5325bfcc3aa1f91841b765c9c12ff2fd8e5db1d1c049e6d2a8e49c70f6a92685`.
Earlier accepted v1 run `20260828T214109Z-aca16fac` remains valid for its
narrower contract; v2 is canonical because it adds the pending-replacement
refusal boundary.

Fresh post-change regressions `20260828T214313Z-1ec1f993`
(`vigil-governor-authority`) and `20260828T214439Z-e370d418`
(`vigil-governor-lifecycle`) also passed completely. All four accepted
packages were ingested serially and were count-stable on repeat; the production
ledger advanced to 47 packages, 48 runs, and 1,260 evidence artifacts. Reviewed
distillation classified every new disposition as `PROJECT-SPECIFIC ONLY`,
added no generic claim, was idempotent, and the full Sacred Texts audit passed.

Standalone remote cancellation is not part of the retained product. Explicit
confirmed overwrite supplies the resolved cancellation semantics and is
available to any authenticated, eligible same-side tablet user. Operational
task messages are side-wide. Client-B/JIP proof of audience isolation and
concurrent authority, retry/invalid-return policy, headless/client-owned assets,
and ownership migration remain excluded. The legacy full task-management
homepage was not revived.
