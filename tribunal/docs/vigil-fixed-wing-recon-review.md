# Vigil fixed-wing reconnaissance review

Review outcome: **INTENTIONALLY DEFER; DEAD SCAFFOLD RETIRED**.

The repository does not currently establish a coherent, executable fixed-wing
reconnaissance product contract. Permanent gameplay coverage would require
inventing the missing behavior, so no scenario is added by this review.

On 2026-08-28 the unreachable Recon controls, disconnected client state helper,
generic recon classifier, and empty post-init task registration/file were
removed. This is retirement, not a recon implementation. The fixed-wing RECON
role bit, registry/lifecycle model, governor/task seams, aviation observers and
map infrastructure remain available for a later coherent product.

## What currently exists

The shared fixed-wing registry defines `YSF_FW_ROLE_RECON = 2` and automatically
adds that bit when `unitIsUAV` is true. The Fixed Wing page displays `RECON` in
the selected asset's role text. Registration still snapshots and removes the
physical plane, and the common registry retains class, textures, condition,
fuel, pylons, side, ingress, egress, heading and lifecycle state.

That metadata does not lead to a reconnaissance task:

- every fixed-wing UAV class is rejected by `YSF_fwIsDisabledDeployType`, whose
  user-facing reason says UAV deployment is temporarily disabled because it is
  unstable; the guard was historically presentation-only, but is now enforced
  at the authoritative deployment endpoint and covered separately in
  [the UAV deployment boundary review](vigil-fixed-wing-uav-deploy-review.md);
- the Fixed Wing controls expose Deploy, RTB, strike controls and Fabricator,
  but no reconnaissance request control;
- the visible Assets toolbox has Transport, Artillery, CAS and Fixed Wing only;
- the former disconnected `TaskG_Recon`, client state helper and empty task file
  have been retired rather than treated as supported behavior;
- the fixed-wing map path explicitly ignores destination double-clicks;
- no reconnaissance request, server task, sensor collection, detected-contact
  record, imagery, marker/report output, completion result, persistence policy,
  multiplayer propagation or cleanup implementation exists.

No separate recon state helper, classifier, form, submit path, or task
registration remains. Future work begins from an explicit product contract and
the retained fixed-wing/generic extension seams.

The upstream README promises fixed-wing deployment, RTB and laser-guided bomb
or missile requests. It does not promise reconnaissance output. Repository
history contains no earlier implementation that establishes missing intent.

## Twelve-question review

1. **What does the user observe?** A registered UAV plane can be listed and
   labelled `RECON`, but Deploy is unavailable. There is no reachable fixed-wing
   reconnaissance request or result.
2. **What are the current positive and negative paths?** Registration and role
   display work. The only recon-capable fixed-wing classes are UAVs and are
   deliberately blocked before reconstruction. No positive task path exists.
3. **Which machines own the behavior?** The server owns the shared registry and
   registration snapshot. The client owns role/UI display and the disconnected
   recon form state. No reconnaissance task crosses the locality boundary.
4. **Which mechanics are generic?** Existing Tribunal aviation, locality,
   spatial, marker and visual observers could support a future design. There is
   no concrete consumer behavior justifying a new sensor/contact abstraction.
5. **Which behavior is product-owned?** Eligibility, request parameters,
   acquisition rules, output semantics, sharing, persistence and task lifecycle
   would all be Vigil product decisions. None is currently implemented.
6. **Are unusual engine requirements proven?** No. Custom UAV crew creation and
   the temporary deployment block indicate instability, but there is no A/B
   evidence defining an Arma requirement. This remains NEEDS EXPERIMENTATION.
7. **What is accidental or fragile?** A role bit and label suggest capability
   that cannot be used. An unreachable form and empty post-init task file are
   incomplete scaffolding, not a specification.
8. **What native alternatives exist?** Arma sensors, knowledge/reveal state,
   UAV control, camera feeds and markers are possible primitives. Choosing among
   them would define the product and cannot be inferred from their availability.
9. **What stable contract can be tested?** Only shared registry metadata is
   stable, and that is not reconnaissance success. There is no user-visible
   information product suitable for a causal specification test.
10. **Which details may vary?** Future coordinates, sensor APIs, dwell timing,
    marker schema, camera implementation and persistence storage are all free
    until the product contract is chosen.
11. **What should be characterized?** Fixed-wing UAV reconstruction/control
    stability, native sensor visibility and locality may warrant controlled
    experiments after a product direction is selected. None is frozen now.
12. **What belongs in Tribunal?** Nothing new yet. Promote detected-contact or
    sensor evidence only when the first real product contract requires it.

## Classification

| Subsystem | Classification | Finding |
| --- | --- | --- |
| shared fixed-wing registry/snapshot | KEEP AS-IS AND SPEC-TEST | already proven by strike/logistics; not recon success |
| UAV-derived RECON role bit and label | DEFER | intentional-looking metadata, but capability semantics are undefined |
| fixed-wing UAV rejection boundary | ACCEPTED / COVERED | direct remote request is rejected before authoritative mutation |
| fixed-wing UAV reconstruction | NEEDS EXPERIMENTATION | explicitly disabled as unstable; no controlled evidence yet |
| former recon grid/altitude/radius state and empty task | RETIRED | disconnected scaffold removed; do not restore |
| recon submit/request construction | DEFER | absent; submit control has no action |
| server reconnaissance task/lifecycle | DEFER | absent |
| ingress/orbit/dwell/RTB policy | DEFER | shared deployment exists, but recon-specific behavior is unspecified |
| sensor/acquisition mechanism | DEFER | absent and product-defining |
| contacts/markers/imagery/report output | DEFER | absent and product-defining |
| persistence, expiry and stale-contact cleanup | DEFER | absent and product-defining |
| multiplayer sharing/JIP/locality | DEFER | absent and product-defining |
| generic Tribunal sensor/contact tooling | DEFER | no concrete contract justifies an abstraction |

## Product decisions required

Before implementation or permanent testing, decide:

1. whether fixed-wing reconnaissance should exist at all, and whether it is the
   same feature as the disconnected general UAV/UGV Recon form;
2. which aircraft are eligible and whether deployment is AI autonomous, player
   UAV-controlled, or both;
3. whether grid, altitude and radius are the intended request contract, plus
   dwell duration, orbit behavior, completion and RTB policy;
4. what reconnaissance produces for the player: shared map contacts, typed
   markers, coordinates, imagery/live camera, a textual report, or another
   explicit information product;
5. how entities are acquired and filtered, including sensor/LOS rules, enemy,
   friendly and civilian handling, confidence, refresh and loss;
6. who receives results, how JIP is handled, how long data persists, and how
   stale contacts and repeated tasks are distinguished and cleaned up;
7. the expected failure behavior for no sensor, no contacts, invalid area,
   destroyed aircraft, disconnect, duplicate request and timeout.

Once those decisions exist, the review can resume with controlled UAV
deployment experiments and a causal test of the chosen player-visible output.
Until then, adding a gameplay scenario would validate an invented design rather
than Pontifex behavior.
