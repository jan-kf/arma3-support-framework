# Vigil task governor — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: SPLIT.** The server-owned abnormal lifecycle is **REFINED;
ACCEPTED / COVERED**. The client request/handler authority boundary remains
**REVIEWED / REWRITE BEFORE PERMANENT COVERAGE**. Existing artillery, transport,
and CAS scenarios retain their accepted physical consumer outcomes.

## Scope

This review covers shared task construction, assignment, stage progression,
terminal handling, finalization, and dispatch in
`functions/governor/fn_governor.sqf`, plus the real artillery, transport, and CAS
submission paths. The unreachable homepage task UI remains separately deferred.

## Canonical review questions

### 1. What should the user or integrator observe?

A valid Vigil request should create at most one authoritative task generation for
its selected vehicle, progress through task-specific work, publish a truthful
terminal result, and clean its owned resources. Invalid, duplicate, cancelled,
failed, or vehicle-lost work must not overwrite active work or remain active.

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

The accepted request schemas, one-active-task policy, cancellation authority,
registered server handlers, ordered lifecycle, terminal causes, exact-once
finalization, result acknowledgment, and record retention are Vigil semantics.
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
private signatures, record storage, and debug messages are free. Preserve only
validated declarative authority, one-active policy, ordered work, truthful
terminal state, exact-once finalization, and cleanup.

### 11. What remains to characterize or decide?

Clients should submit declarative requests and the server should build registered
code; this is a mandatory security/authority correction rather than optional
characterization. Product decisions remain for reject/queue/replace policy,
cancellation eligibility, terminal-history retention, retry versus consumer
bounds, invalid-result handling, and headless/client-owned vehicles.

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
retention, headless/client-owned vehicles, client-N, and JIP remain behind the
mandatory authority rewrite.

The accepted Evidence Contract was ingested twice with unchanged second-pass
counts, and the Sacred Texts audit passed. The final ledger has 21 packages, 22
runs and 474 artifacts. Reviewed distillation advanced to 20 findings and 8
intentionally project-specific results while retaining 7 generic lemmas and 1
generic conjecture. Both lifecycle propositions are `PROJECT-SPECIFIC ONLY`, so
this continuation adds zero generic Sacred Texts notes.
