# Field Utilities helicopter sling helper — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REVIEWED / DEFERRED`.** The four-point sling helper is
compiled but has no supported caller, action, module, event, or documented API.
Directly calling it would test an orphaned mechanism, not a shipped feature.

## Scope and observed implementation

`YOSHI_attachHeliLiftRopes` accepts a helicopter and arbitrary cargo,
calculates four geometry-derived points, destroys every existing rope on the
helicopter through shared stow, then attempts four local nine-metre rope
creations from `slingload0`. It returns handles but retains no operation state.

The helper rejects null endpoints and non-helicopters. It has no distance,
mass, size, motion, locality, owner, requester, or concurrency validation.
Partial rope creation is not rolled back. There is no detach entry, exact rope
ownership, break observer, result receipt, or endpoint/deletion/disconnect
finalizer. The computed `_heliAttachPoint` is unused.

## Canonical review questions

### 1. What should a user observe?

No supported user behavior exists. If revived, an authorized user would select
one exact helicopter/cargo pair, establish a complete lift operation, observe
the cargo physically follow, and detach only that operation.

### 2. What happens on positive and negative paths?

The internal helper creates up to four ropes after destructively stowing all
helicopter ropes. Invalid endpoint/type returns an empty array. Individual
creation failure can return a mixed array and leave partial state.

### 3. Which machine and lifecycle own it?

Whichever machine calls it performs all rope mutations. No server/owner routing
or lifecycle owner exists. The globally named function is available everywhere,
but no product path calls it.

### 4. Which mechanics are generic?

Exact rope handles/endpoints, locality, geometry, paired aircraft/cargo
trajectories, and cleanup census are generic observations. Sling eligibility
and lifecycle are Field Utilities policy.

### 5. Which behavior is product-owned?

Whether it ships, entry/authority, eligible endpoints, mass/size/range,
replacement/concurrency, native versus custom sling behavior, resources, and
terminal cleanup.

### 6. Are unusual engine requirements proven?

No. Four ropes, `slingload0`, `Spring1xRope`, nine metres, the corner
formula, and custom rope physics have no controlled A/B.

### 7. Which details are fragile or incomplete?

Pre-stow destroys unrelated/native/mod ropes and clears parent state through
the shared towing helper. Created handles are untracked and non-atomic.
Caller-controlled vertical percentage is unbounded. Breakage and partial
failure leak state.

### 8. Is a better mechanism available and proven?

Arma has native slingload concepts, but no comparison establishes suitability.
Do not choose a replacement while the product entry and contract are absent.

### 9. What is the candidate stable contract and proof?

If revived: an authoritative exact-pair transaction creates a complete,
feature-owned lift or changes nothing; physical cargo following is independently
proven against a no-sling control; detach/terminal events remove only owned
state and preserve an unrelated sentinel rope.

### 10. Which details must remain replaceable?

Rope count/type/length, memory point, corner algorithm, physics mechanism,
function names, and transaction representation.

### 11. Which mechanisms deserve characterization?

Only after a real entry is chosen: rope locality/replication, native sling
comparison, mass limits, partial failure, movement, detach, breakage, endpoint
deletion, and ownership migration.

### 12. What belongs in Tribunal?

Nothing now. Reuse generic rope/trajectory observation only when a concrete
product consumer exists; do not promote this orphan's semantics.

## False-PASS boundary and continuation

Four returned entries may contain null or stale handles. Four helicopter ropes
may be unrelated. Cargo movement may come from native sling, collision,
attachment, or fixture motion. Fixture deletion can hide leaks. A future proof
must use exact identities, an unrelated sentinel, an identical no-sling
movement control, and observe cleanup before deletion.

Product decisions: ship/remove; supported entry; authorization/locality;
endpoint eligibility; coexistence with unrelated ropes; native/custom
mechanism; atomicity; detach/break/deletion/migration/disconnect policy.

## Disposition

**Reviewed / deferred as an orphaned helper.** Revisit only after towing or
another feature establishes an authoritative rope-operation model and the
product selects a supported sling entry.
