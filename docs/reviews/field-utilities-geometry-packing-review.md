# Field Utilities geometry and packing primitives — canonical feature review

Primary outcome: **REVIEWED / DEFERRED AS A STANDALONE FEATURE;
CONSUMER-OWNED MECHANICS**.

This review covers the shared bounds/transform helpers and Fabricator packing
stack. It does not reopen accepted Fabricator transaction/delivery behavior or
the separately unresolved towing and helicopter-sling physics.

## Twelve-question review

1. **What should the user observe?** There is no user-facing geometry feature.
   Fabricator users receive the exact requested manifest in bounded delivery
   containers or an atomic refusal. Towing/sling users would observe physical
   attachment behavior under their own unresolved contracts.
2. **What does it do now?** Fabricator resolves class/reference corners, derives
   sizes, deterministically orders objects, allocates pallets, attaches objects
   at snapped offsets, reports skipped items, and creates containers. Towing
   consumes center/rotation/lift-corner helpers. Several generic-looking helpers
   have no caller outside their own chain or are orphaned.
3. **Which machines own it?** Accepted Fabricator packing runs server-side within
   its authoritative transaction. Pure geometry inherits caller locality. The
   packer reports each created container immediately so the surrounding
   transaction can track/rollback it. Towing geometry inherits that feature's
   unresolved owner-local boundary.
4. **Which mechanics are generic?** Engine bounds, model/world transforms,
   independent extents, attachment/locality, overlap, containment, and physical
   settling can be Tribunal observation mechanics. Current helper algorithms
   and Field Utilities policies are not generic contracts.
5. **Which behavior is product-owned?** Field Utilities owns pallet/reference
   classes, override table, allowed orientations, ordering/allocation heuristic,
   padding/scale, attachment policy, container selection, size rejection, and
   atomic handling of skipped objects.
6. **Are unusual engine requirements proven?** No. Repeated surface-ray sampling
   with bounds fallback, canonical upright orientation, volume grouping,
   sequential rows/layers, snapped offsets, and attachment are implementation
   choices. Accepted outcomes do not prove these choices necessary or optimal.
7. **What is fragile or incomplete?** The heuristic is not a completeness or
   optimality solver. Bounds fallback can mask failed surface sampling. Attached
   objects can look stable without proving collision-free placement,
   carryability, or behavior after detachment. Towing/sling consumers have no
   accepted physical geometry proof.
8. **Is a better mechanism available?** Engine bounds/transforms remain suitable
   inputs. More sophisticated packing is unnecessary unless a consumer outcome
   fails. Any replacement should be compared through independent delivered
   manifest, spatial, overlap, and lifecycle evidence—not helper self-report.
9. **What is the stable contract and causal proof?** The accepted Fabricator
   contract already proves exact authoritative manifest, bounded container
   placement, atomic oversized refusal, mission-wide absence of skipped clones
   or orphan containers, and transaction retirement. It deliberately does not
   promise exact pallet count, orientation, offset, visual neatness, optimality,
   collision-free layout, or post-detachment stability.
10. **Which details remain free?** All helper names, reference sampling, cache,
    overrides, orientation variants, sort/group heuristic, padding, snap size,
    spawn offsets, pallet count/class selection, and attachment representation
    remain replaceable behind consumer outcomes.
11. **Which mechanisms deserve characterization?** Only when a consumer adopts a
    new physical promise: Fabricator overlap/settling if neat stable packing is
    required; towing/sling exact owner-local trajectories after their authority
    decisions. Do not characterize orphan helpers merely because they compile.
12. **What belongs in Tribunal?** Promote an independent engine-native geometry
    observer only after a second real consumer needs it. Never use the product's
    own computed bounds or transforms as the sole oracle for its placement.

## Existing evidence and false-PASS boundary

The accepted Fabricator scenario proves its consumer boundary: exact server
transaction/result, delivery containers, exact manifest/cargo fidelity, bounded
placement, atomic refusal of an unpackable order, mission-wide leak census, and
cleanup/retirement. Fixed-wing logistics proves delivered manifest and landing,
not packing internals. Towing remains unaccepted.

A packer `success` value, empty skipped list, container count, attached-object
count, deterministic repeated output, or transform round-trip is not independent
physical correctness. Two mutually wrong transform helpers can self-confirm.
Attached objects do not prove non-overlap or stable detached physics. Rejected
oversize is meaningful only when exact stimulus and leak-free rollback are
independently established, as in the accepted Fabricator transaction.

## Decisions and continuation

No standalone product decision or scenario is needed. Keep geometry and packing
consumer-owned. Add independent overlap/containment/settling evidence only if
Fabricator promises those outcomes. Evaluate lift/tow points only through their
future matched physical scenario after authority and rope-lifecycle policy are
chosen. Orphan helper deletion or public-API preservation is a separate
compatibility decision, not a behavioral acceptance requirement.
