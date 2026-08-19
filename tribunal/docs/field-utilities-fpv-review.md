# Field Utilities FPV/UAV field-modification review

## Scope and result

This review applies the canonical feature-review program to
`functions/drone/fn_fpv.sqf`: automatic small-UAV configuration, ACE field
actions, IED attachment/detonation, finite mortar/grenade payloads, and their
owner-local execution route.

**Classification: `REFINE BEFORE PERMANENT COVERAGE` (reviewed; not covered).**

The feature is reachable and its broad intent is documented, but destructive
operations trust client-side action conditions rather than enforcing them at
the object's owner. Direct function calls can detonate an unqualified UAV,
release ordnance without a payload, and drive counts below zero. Several
product semantics are also not stated. A permanent scenario would fossilize
accidental behavior until those boundaries are refined or decided.

## Stable contract available from repository evidence

Field Utilities offers ACE actions on live UAVs to attach an IED, two mortar
rounds, or four grenades. A controlling pilot/UAV operator can use an attached
payload. Small UAVs are configured on their owner for engine attach/detach,
ACE dragging/carrying, reduced fuel consumption, and camouflage. Consequential
object mutation is intended to execute where the UAV is local.

The repository does not establish that attachments are free inventory, that
grenades may coexist with another payload, that low/high IED effects are exact
specification, or that direct globally named functions are a supported API.

## Canonical review

1. **User observation.** A player sees a programmatically registered ACE Field
   Actions branch on a live UAV. Attach actions add payload state; self-actions
   let the current pilot/UAV controller detonate or release it. Audio is
   feedback, not the core outcome.
2. **Current behavior and negative paths.** IED and mortar attachments exclude
   one another, but grenade attachment ignores both. Attach helpers overwrite
   counts. Release helpers default a missing count to one and decrement without
   a lower bound. IED detonation simply kills the UAV; its Killed handler then
   creates low-altitude or high-altitude effects.
3. **Authority/locality.** Helpers route to `owner _vic` through CORDIS, but the
   routed functions accept only the object. They do not carry requester
   identity, do not re-check pilot/controller authorization, and do not prove a
   server-issued capability. ACE conditions are presentation gates, not an
   authority boundary. All helper names are globally callable.
4. **Generic mechanics.** Exact object/projectile identity, owner-local command
   receipts, trajectory/impact/damage observation, action registration and
   relevance evaluation, and cleanup belong in Tribunal. Payload meaning and
   authorization policy remain Field Utilities product semantics.
5. **Product behavior.** Field Utilities owns eligible UAVs, payload choices,
   quantities, exclusivity, attachment/use authorization, effects, and UAV
   profile changes.
6. **Engine requirements.** Owner-local mutation is plausible and consistent
   with the routing helper, but no controlled owner/non-owner A/B exists. The
   physical behavior of a zero-velocity `createVehicle "Sh_82mm_AMOS"` release
   is unproven. Neither is characterized.
7. **Fragile/incomplete details.** UI-only authorization, default-one release,
   underflow, duplicate attachment, broad `AllVehicles` registration, IED
   effect fan-out, and missing terminal records create false-PASS and abuse
   paths. Server `EntityCreated` also invokes owner routing without a durable
   completion receipt.
8. **Better native/existing mechanisms.** Keep CORDIS owner routing for
   locality, but route a validated request containing requester identity and a
   unique transaction/receipt. ACE action presence and condition relevance can
   be evaluated programmatically; VNC does not add evidence for them.
9. **Required causal proof.** Each payload needs the same exact UAV and a
   qualified controller, exact owner-local receipt, exact spawned ordnance or
   attached explosive, physical trajectory/impact/damage, finite state change,
   duplicate/depleted/foreign-controller controls whose stimulus is proven,
   replication, and cleanup. The IED case needs exact damage/effect causality,
   not merely UAV death.
10. **Replaceable details.** Action IDs, variable names, sound choices, object
    classes, attachment offsets, effect classes, handler IDs, and routing
    representation are not specification unless a later experiment proves an
    engine constraint.
11. **Characterization.** Nothing is characterized yet. In particular, do not
    preserve the mortar creation ordering or high-altitude effect array merely
    because it exists.
12. **Tribunal promotion.** No new generic primitive is justified before the
    first controlled run. Reuse existing projectile, combat, ACE-action, and
    locality evidence where possible; keep FPV semantics in Field Utilities.

## Required product decisions

1. Are payload attachments intentionally free/unlimited, or must they consume
   player/nearby inventory?
2. Are IED, mortar, and grenade payloads mutually exclusive, or may grenades
   coexist with one of the other two?
3. Who may attach a payload: any nearby player, only the UAV controller, or a
   role/permission-qualified player?
4. Is IED destruction meant to vary by altitude as currently implemented, and
   what user-visible destructive outcome is intended?
5. Is the feature for every `unitIsUAV` vehicle or only the small
   `UAV_01_base_F` family described by the field profile?

## Precise continuation point

Before gameplay proof, introduce one owner-authoritative request boundary that
revalidates requester, UAV eligibility, payload state, and positive count at
execution time; reject replays/duplicates and publish bounded terminal receipts.
Do not choose inventory or exclusivity policy in that refinement. Then use Live
Mode to characterize an exact mortar and grenade release from a stationary,
owner-local UAV with same-frame and trajectory telemetry. If the mortar is not
physically valid, discriminate setter/class/order alternatives before changing
product code. With product decisions answered, split permanent coverage into
UAV profile, IED, mortar, and grenade contracts and finish with a fresh
autonomous run.

## False-PASS risks

An action being registered does not prove authorization or effect. A count
decrement does not prove ordnance existed or impacted. UAV death does not prove
the attached IED caused collateral damage. Projectile disappearance does not
prove impact. A silent negative control is meaningless unless the attempted
foreign/duplicate/depleted request reached the authority boundary and was
rejected. Stale attached objects, killed handlers, counts, receipts, and
projectiles must be isolated between phases.
