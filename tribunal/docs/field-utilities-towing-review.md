# Field Utilities towing — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REFINE BEFORE PERMANENT COVERAGE`.** The ACE entry is
reachable, but the current implementation has no authoritative transaction,
does not retain feature-owned rope identity, and cannot reliably finalize tow
state. No permanent scenario is justified until the decisions and controlled
experiment below are completed.

## Scope

In scope: the `LandVehicle` ACE tow/stow actions, configured and
geometry-derived tow points, rope creation/destruction, and `setTowParent`
routing in `fn_initRopes.sqf` and `fn_ropeActions.sqf`. The separate
`YOSHI_attachHeliLiftRopes` helper is excluded because no normal product entry
invoking it was found.

## Canonical review questions

### 1. What should the user or integrator observe?

An eligible actor near two eligible vehicles should see an ACE tow action for
the exact intended cargo. Activation should establish a physical tow between
that exact pair. Stowing should remove only that tow and leave both vehicles in
a coherent untowed state.

### 2. What does the feature actually do now, including negative paths?

Client initialization registers an ACE class action on every `LandVehicle`.
Its dynamic child selects the first nearby intersected `AllVehicles` object
and calls `YOSHI_deployTowRopes` on the actor client. That function calculates
configured or bounding-box fallback points and calls `ropeCreate` twice. It
discards both handles, then owner-routes only `setTowParent` through CORDIS.
Stow clears the tow parent of every `ropeAttachedObjects` result and destroys
every rope on the selected vehicle.

There is no result for failed or partial creation, no exact-pair transaction,
and no supported negative path for ineligible, moving, distant, concurrent,
deleted, ownership-migrated, or disconnected participants.

### 3. Which machines and lifecycle stages own the behavior?

ACE resolution, rope creation, and destruction run on the actor client. Only
the cargo vehicle's parent mutation is routed to its owner. The server does not
authorize or finalize the operation. Without retained rope handles or an
operation generation, no authority owns breakage, deletion, migration,
disconnect, or competing-request cleanup.

### 4. Which mechanics are generic concerns?

ACE action resolution, object locality and identity, rope observation,
tow-parent observation, and paired trajectory sampling are generic. Existing
Tribunal action/locality techniques are sufficient for the first experiment;
towing semantics remain in Field Utilities.

### 5. Which behavior is product-owned?

Vehicle/requester eligibility, distance and motion limits, one-versus-many
cargo policy, tow points, parent semantics, feature rope ownership, breakage,
resources, and cleanup/finalization are product decisions.

### 6. Are unusual engine requirements proven?

No. Configured points, fallback geometry, local `ropeCreate`, and
`setTowParent` have not been characterized in a controlled A/B. Source TODOs
explicitly question parent behavior and reset after rope loss.

### 7. Which details are fragile or incomplete?

First-match spatial selection is not a committed exact target. Rope handles are
discarded. Stow can destroy unrelated ropes and clear unrelated parent state.
Natural rope loss cannot deterministically finalize the parent. Fallback
geometry, partial two-rope creation, and concurrency are unmeasured.

### 8. Is a better mechanism available and proven?

Not yet. Compare the current mechanism against a physical no-tow control under
its real locality before choosing a replacement. This review does not
fossilize `setTowParent` as product specification.

### 9. What is the stable contract and causal proof?

Candidate contract, pending decisions:

> An eligible authenticated actor can request one tow between exact eligible
> tow and cargo vehicles. The authoritative operation either establishes its
> complete feature-owned rope/tow state or changes nothing. Cargo then follows
> physically. Stow or terminal loss removes exactly that operation without
> disturbing unrelated ropes.

Proof must correlate exact actor/vehicle identities, an accepted transaction,
feature-owned rope identities, parent state, and paired trajectories. The same
movement without a tow is the independent control. Observe cleanup before
fixture deletion.

### 10. Which details must remain replaceable?

ACE labels/icons, point coordinates, rope count/type/length, helper names,
transaction representation, polling cadence, and the verified physical
mechanism.

### 11. Which mechanisms deserve characterization?

Whether rope plus parent makes cargo follow in the dedicated topology; which
machine must create/destroy ropes; locality changes; natural breakage; and
fallback geometry on one unconfigured class. Do not promote observations to
requirements without an A/B.

### 12. What should be promoted into Tribunal?

Nothing yet. Exact rope enumeration and paired trajectories may become generic
after a second consumer. Eligibility, transactions, and cleanup stay in the
product.

## Product decisions required

1. Eligible tow/cargo classes, mass/size, range, and motion state.
2. Eligible requester and authoritative machine.
3. Whether either vehicle may join multiple tow operations.
4. Whether tow parenting is intended or only a workaround.
5. Which ropes are feature-owned and what stow may remove.
6. Finalization on break, deletion, migration, disconnect, and concurrency.
7. Whether towing consumes a resource.

## First discriminating experiment

In one retained Live session, use settled server-owned
`B_MRAP_01_F` and `C_Offroad_01_F`. Resolve the exact registered ACE child
and invoke its real statement. Record actor, vehicles, locality, rope handles,
attachments, and parent state on both machines. Move the tow vehicle 25–30 m
and independently sample both trajectories. Invoke exact stow and prove only
feature-owned state is removed. Repeat the movement without a tow as control.
Then add invalid-distance and second-request probes after policies are chosen.

Do not pass on action presence, rope count, parent state, or cargo movement
alone: unrelated ropes, stale state, attachment without movement, and fixture
cleanup are false-PASS paths.

## Disposition

**Reviewed, not covered; refine before permanent coverage.** Continue after the
product decisions with the one-session physical/authority experiment. The
helicopter sling helper remains separately unreviewed.
