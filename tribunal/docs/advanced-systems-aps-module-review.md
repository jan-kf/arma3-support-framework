# Advanced Systems APS Eden and Zeus activation review

## Scope and result

This review covers the public Eden `YAS_APS_Module` and curator-visible
`YAS_APS_Zeus_Toggle_Module`: configured dispatch, exact target selection,
authority, result, and logic lifecycle. Accepted APS projectile interception,
resources, replication, and lifecycle-tail behavior remain unchanged.

**Classification: `REFINE BEFORE PERMANENT COVERAGE` (reviewed; not covered).**

Both module classes are reachable and their downstream APS APIs work, but the
actual module-framework and curator entry paths are unmeasured. Both handlers
forward arbitrary client calls to server, validate neither exact class nor
requester, mutate caller-selected targets, and delete caller-supplied logic.
Direct API or handler invocation would bypass the feature being reviewed.

## Candidate stable contract

A genuine typed Eden module installs APS once on each exact valid synchronized
vehicle. A genuine authorized curator module toggles exactly one selected
vehicle once. The server validates module identity, requester, target, current
transition, and replay; returns a correlated truthful result; and consumes only
its own disposable logic. Invalid, ambiguous, unauthorized, stale, or replayed
requests change no vehicle/resource and delete no unrelated object.

## Canonical twelve-question review

1. **User or integrator observation.** Mission makers synchronize vehicles to
   the Eden module to install APS at mission start. An authorized curator places
   the Zeus module on one vehicle to toggle APS. The observation is authentic
   activation of accepted APS behavior, not another APS implementation.
2. **Current behavior and negative paths.** Eden forwards to server, iterates
   all synchronized `AllVehicles`, calls the accepted enable API, then deletes
   its logic despite `isDisposable=0`. Zeus forwards similarly, selects the
   first synchronized object or `attachedTo`, calls toggle, emits broad feedback,
   and deletes the logic. Only null/invalid target checks exist.
3. **Authority, locality, and lifecycle.** APS mutation is server-owned, but
   module-request authority is undefined. Neither handler checks exact class,
   logic locality/owner, `remoteExecutedOwner`, assigned curator, operation ID,
   or replay. Actual `isGlobal=0` engine dispatch has not been measured. Eden's
   configured persistence contradicts unconditional deletion.
4. **Generic mechanics.** Typed mission-module generation, native SQM Sync
   links, configured-function receipts, execution locality, real curator
   placement, and exact logic cleanup can be product-neutral Tribunal mechanics.
   APS state and combat meaning remain Advanced Systems.
5. **Product-owned behavior.** Advanced Systems owns valid vehicles, authorized
   curators, exactly-one Zeus selection, Eden multi-module/mixed-target policy,
   feedback audience, installation side effects, and logic disposal.
6. **Claimed engine requirements.** None are established. No run proves native
   module execution machine, genuine `remoteExecutedOwner`, curator attachment
   representation, or that non-server forwarding is required.
7. **Fragile or incomplete details.** Null-only/classless forwarding, ambiguous
   first-target selection, deletion of supplied objects, no result/replay guard,
   broad notification, and Eden lifecycle contradiction create false-PASS and
   authority risks. Toggle also resets APS mode defaults and can replenish hard-
   kill inventory; whether that is intended module behavior is unresolved.
8. **Better native or existing mechanism.** Keep Arma's native module framework
   and the accepted server APS lifecycle tail. Measure authentic transport
   before deciding whether any explicit request route is needed. A validated
   operation endpoint is appropriate only where curator transport requires it.
9. **Stable contract and causal proof.** Eden requires a real typed SQM module
   and Sync link, exact dispatch receipt, exact installed target, and one accepted
   calibrated projectile interception. An identical unsynchronized/no-module
   target must physically impact. Zeus requires real curator placement, exact
   requester/logic/target, OFF-impact then ON-interception, and forged/invalid/
   replay controls with unchanged independent state.
10. **Replaceable details.** Function names, priority, internal variables,
    notification wording, private receipt schema, fixture coordinates, ACE
    registration details, and transport mechanism remain free.
11. **Characterization.** First characterize typed Eden dispatch/locality and
    Sync identity. Then characterize one real curator placement. One bounded VNC
    placement is justified only if a programmatic native path cannot be proven
    equivalent; permanent outcomes remain data-driven.
12. **Tribunal promotion.** Add a narrow validated typed-Logic/SQM-Sync fixture
    after its first real consumer succeeds; never expose arbitrary raw SQM.
    Curator transport stays scenario-local until a second consumer proves reuse.

## False-PASS audit

Calling either handler or `YOSHI_fnc_apsEnableVehicle`/toggle API directly is a
pipeline bypass. Config presence, enabled variables, charge top-up, ACE actions,
notification, or logic deletion do not prove authentic module activation.
Positive proof needs fresh exact module/vehicle/projectile identities and the
accepted physical APS oracle. The negative must independently prove a valid
projectile impacts. An absent forged effect is meaningful only after an exact
request receipt proves the authority boundary was reached.

Do not include anti-drone in this contract: its activation policy is separately
deferred. Do not claim curator, JIP, or client-N behavior from client-a.

## Decisions and continuation

Decide: authorized curator population; exactly-one Zeus target and sync-versus-
attach precedence; Eden duplicate/mixed valid-invalid policy; whether Eden logic
persists; whether module enable intentionally resets voice/hard/soft/anti-drone
state and replenishes charges; and feedback audience.

Then implement the generic typed-module fixture once, run Eden module/no-module
physical A/B with dispatch telemetry, and refine only from measured transport.
Run a real curator OFF-impact/ON-interception pair plus invalid, unrelated,
unauthorized, and replay controls. Preserve all accepted APS combat semantics.
