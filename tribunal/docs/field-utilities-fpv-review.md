# Field Utilities small-UAV Payload Manager review

## Scope and result

This review covers `functions/drone/fn_fpv.sqf`: the `UAV_01_base_F` field
profile, the native Pontifex Payload Manager, inventory-backed installation,
UAV-owned ordered payload state, controller keybinds, HUD, and grenade/satchel
deployment.

**Classification: `REFINED; ACCEPTED / COVERED`.**

The former ACE payload tree, free counters, client-trusting destructive calls,
IED altitude-effect split, and mortar release have been replaced by one explicit
product contract. Fresh run `20260828T130038Z-9f4e37a1` permanently proves the
manager and authoritative loadout transaction. Fresh run `20260828T133445Z-8924da44` permanently proves authentic live-UAV control, context gating, HUD/binding/theme rendering, occupied-only selection, grenade and satchel deployment, server-authoritative receipts, empty refusal, and cleanup. Client-B/JIP remains program-blocked. Mortar payloads are intentionally deferred
until they have a coherent inventory item.

## Stable product contract

Eligible small UAVs expose a native world action that opens the Pontifex Payload
Manager without ACE interaction. Uniform, vest, and backpack remain separate
visible sources. The player drags real eligible inventory instances into an
ordered proposal with eight capacity units: fragmentation grenades cost one and
a satchel costs eight. Applying is a bounded server-authorized prepare/commit
transaction. The server authenticates requester, range, UAV, revision, IDs,
duplicates, definitions, and capacity; the inventory owner snapshots and debits
only after approval; the server commits the UAV manifest only after exact debit
verification. Refusal or invalidation restores the snapshot and consumes
nothing. Installed entries belong to the UAV, may be reordered, and cannot be
reclaimed through the manager.

While the authenticated player actually controls an eligible UAV, **Next
Payload** cycles only the occupied manifest and **Deploy Payload** consumes the
selected entry. Both are CBA-configurable controls. A compact persistent HUD
shows the selected occupied payload and resolves the user's current bindings at
render time. The manager and HUD validate and apply the existing
`YFU_monochromeBaseColor` theme setting.

## Canonical review

1. **User observation.** A nearby player sees one simple Payload Manager world
   action, three distinct inventory lists, an ordered eight-unit capacity area,
   Apply/Cancel controls, and themed status. A controller sees the compact HUD
   and uses the configured next/deploy bindings.
2. **Behavior and negatives.** Valid new items are debited exactly once and
   become UAV records. Over-capacity, stale revision, duplicate instance,
   missing installed ID, wrong source, range, requester, busy, controller, and
   empty-state requests fail closed. Existing UAV entries can be reordered but
   omission/reclamation is rejected.
3. **Authority/locality.** The dedicated server owns validation, serialization,
   UAV state, selection, deployment, results, and audit. Inventory mechanics run
   only on the authenticated inventory-owning client through a server-origin
   prepare/finalize leg with snapshot rollback. Server and player/UAV pending
   locks prevent overlapping commits.
4. **Generic mechanics.** Remote execution, inventory-local commands, UAV
   control, projectile creation, and display controls are engine mechanisms.
   Payload definitions, capacity, ownership, eligibility, ordering, and control
   policy are Field Utilities semantics.
5. **Product behavior.** Pontifex owns the manager UI, theme use, eight-unit
   capacity, inventory catalogue, ordered UAV manifest, non-refundable
   installation, bindings, controller gate, HUD, and deploy effects.
6. **Engine requirements.** Inventory mutation must execute where the player's
   inventory is local; consequential UAV state remains server-authoritative.
   The accepted run proves this split in the supported dedicated-server plus one
   authenticated-client topology.
7. **Fragile details.** Inventory order and engine magazine ordinals are never
   treated as durable IDs beyond one proposal revision. Transaction IDs,
   manifest IDs, revisions, bounded audits, phase gates, and rollback prevent
   replay, stale, timeout, and late-ack races.
8. **Existing mechanisms.** Native `addAction`, Arma listbox drag/drop,
   CBA-configurable keybinds, and the existing Pontifex color setting are reused.
   Payload operation has no ACE interaction dependency; optional ACE drag/carry
   in the broader UAV field profile is guarded and remains a separate dependency
   review.
9. **Required causal proof.** Accepted coverage correlates one exact UAV and
   authenticated client with exact source inventory deltas, server audit,
   replicated revisions/IDs/order, capacity and stale negative controls, result
   receipts, UI control state, theme value, binding resolution, and cleanup.
10. **Replaceable details.** Dialog IDCs, labels, action priority, binding
    defaults, manifest representation, transaction timeout, attachment offsets,
    and audit representation are not specification.
11. **Characterization.** Manager run `20260828T130038Z-9f4e37a1` passed all 16 smoke and feature assertions. Control/deploy run `20260828T133445Z-8924da44` passed all 19 smoke and feature assertions with complete cleanup. Both Evidence Contract v1 packages were ingested idempotently and the knowledge audit passed. No generic Arma lemma was promoted; the results are `PROJECT-SPECIFIC ONLY`.
12. **Tribunal promotion.** The feature-owned scenarios are
    `fieldutils-payload-manager` and `fieldutils-payload-control`. No new generic Tribunal primitive is justified.

## Permanent coverage boundary

Accepted proof covers world entry, dialog creation, separated real inventory, validated theme, live binding resolution, authenticated three-item transfer, eight-unit capacity refusal, stale refusal, UAV-owned reorder, replication, authentic live-UAV control, negative context gating, occupied-only cycling, controller HUD with actual configured bindings and theme, grenade and satchel deployment causality, exact server authority/effect receipts, empty refusal, audit, and cleanup. Client-B/JIP and ownership migration remain shared program boundaries. Mortars are deliberately absent rather than uncovered. Broader ACE
dependency removal is outside this feature.

## False-PASS risks

Dialog presence alone does not prove inventory provenance or atomicity. A local
item delta without the matching server revision is not a commit. A UAV manifest
without exact source debit is not installation. Refusal must prove the request
reached authority and that both loadout and UAV state stayed unchanged. A projectile spawn alone does not prove deployment causality; accepted proof correlates the exact selected ID, revision, effect class and identity, controller, receipt, UAV position, and cleanup.

## Precise continuation point

No actionable review or permanent-coverage work remains for the supported dedicated-server plus one authenticated-client contract. Mortars remain intentionally deferred; client-B/JIP is a shared external boundary; arbitrary catalogues/classes, broader ACE removal, and presentation matrices remain optional or separately decision-bound.
