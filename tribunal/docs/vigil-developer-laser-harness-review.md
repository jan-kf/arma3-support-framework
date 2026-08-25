# Vigil developer laser harness — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REVIEWED / DEFERRED`.** This is a shipped, preInit
developer characterization harness with no normal product entry. It is not a
Vigil user feature and must not receive permanent product coverage in its
current form. Before reuse, move it to Tribunal/dev tooling or place it behind
an explicit bounded diagnostic capability.

## Scope and reachability

`fn_fwLaserTest.sqf` defines classification, weapon selection, firing,
tracking heuristics, result storage, and the public
`YSF_fwLaserTestStart` entry. `CfgFunctions` compiles it preInit on every
machine. Repository-wide search found no UI, action, module, task, documentation,
or other normal caller.

## Canonical review questions

### 1. What should a user observe?

Nothing: no shipped product workflow exposes the harness. A developer calling
the global entry can make one aircraft iterate compatible pylon magazines,
acquire nearby laser targets, fire up to 120 tests, restore pylons, and publish
a heuristic report.

### 2. What does it actually do?

It routes to the vehicle owner, rewrites pylon loadouts, commands
`fireAtTarget`, falls back to `forceWeaponFire`, samples exact Fired
projectiles, labels likely tracking/impact, restores pylons, and forwards a
large result hashmap to a server-global, replicated, unbounded history.

### 3. Which machine and lifecycle own it?

The vehicle owner mutates and fires the aircraft. Any client can call the
globally named start surface; CORDIS routes it without a product authorization
receipt. Any client can also submit an arbitrary result hashmap to the server
store. No requester, capability, rate, result-size, generation, cancellation,
or retention boundary exists.

### 4. Which mechanics are generic?

Pylon inventory, weapon firing, Fired observation, projectile trajectories,
target identity, and report serialization are generic experiment mechanics.
They belong in Tribunal or explicitly dev-only tooling if retained.

### 5. Which behavior is product-owned?

None has been established. Vigil fixed-wing strike behavior is independently
covered through its real task pipeline; this harness bypasses that pipeline.

### 6. Are unusual engine requirements proven?

No. Its own tracking heuristics and forced-fire fallback are observations, not
accepted engine characterization. They lack independent controls and must not be
cited as product evidence.

### 7. Which details are fragile or incomplete?

The entry is globally callable; the run can fire destructive ordnance and
rewrite pylons; the result sink trusts arbitrary client data; history is
unbounded and publicly replicated; no cancellation/finally path protects pylon
restoration; and heuristic “likely” labels can self-confirm the experiment.

### 8. Is a better mechanism available and proven?

Yes for its likely purpose: Tribunal already owns exact projectile identity,
trajectory, impact, and locality observation, and permanent Vigil strike
scenarios use the real product pipeline. This does not prove every private
diagnostic is replaceable, but it removes any reason to treat this file as a
product feature.

### 9. What stable contract should be covered?

None while unreachable. If retained as a supported diagnostic, its future
contract must be explicitly dev-only, authorized, bounded in shots/time/payload,
cancellable, restore state in a finalizer, and store validated size-limited
results. Product scenarios must still exercise the real strike pipeline.

### 10. Which details must remain replaceable?

All classification heuristics, thresholds, magazine iteration, firing method,
report schema, and output storage. None is product specification.

### 11. Which mechanisms deserve characterization?

Only after a retention decision: whether an ordinary client can invoke the
public surface and submit forged results, plus guaranteed pylon restoration on
cancel/error. Static evidence already establishes the exposed call paths, so a
destructive runtime probe is not warranted merely to close this review.

### 12. What should be promoted into Tribunal?

No code is promoted by this review. If the harness remains useful, extract only
generic, bounded weapon/projectile characterization after a concrete Tribunal
consumer is selected. Do not move Vigil names or product semantics.

## False-PASS boundary

Directly invoking this harness bypasses fixed-wing task authorization,
designation, dispatch, and cleanup. Its `trackedLikely`,
`trackedByImpactLikely`, stored result, fire return, or projectile
disappearance cannot prove Vigil strike behavior. Existing fixed-wing
acceptance scenarios remain the only product evidence.

## Disposition

**Reviewed / deferred as unreachable developer diagnostic debt.** Product
decision required: remove it from the shipped addon, move it into Tribunal/dev
tooling, or retain it behind an explicit private capability with bounded
execution and storage. Do not add a permanent scenario for the current surface.

## Accepted adjacent refinement — shared debug ownership

The Opus reconnaissance was used only to identify a possible ownership question.
Canonical source then established that this preInit harness conditionally
defined the product-wide `YSF_fnc_debugMsg` symbol before the later preInit
`fn_utils.sqf` assigned Vigil's real CORDIS-backed wrapper. A fresh pre-change
run, `20260825T221151Z-2203c468`, proved final runtime behavior was already the
production route: exact shared-wrapper tokens reached CORDIS under both false
and true `YSF_showDebugMessages` values. It did not prove or exercise the laser
harness.

Pontifex removed only the harness's conditional fallback. `fn_utils.sqf` is now
the sole source owner, so final correctness no longer depends on another preInit
assignment replacing a developer fallback. Permanent static coverage enforces
that sole-owner boundary, while `vigil-debug-channel` version 2 proves the shared
wrapper's exact false/true runtime route. Post-change cold runs
`20260825T221344Z-3814387b` and `20260825T221507Z-12376258` each passed 3/0
server and 3/0 client assertions with cleanup.

This is an accepted production-wrapper refinement, not acceptance of the
destructive diagnostic. The harness remains **REVIEWED / DEFERRED**, and its
entry, firing behavior, result submission, authorization, and storage remain
outside permanent coverage.
