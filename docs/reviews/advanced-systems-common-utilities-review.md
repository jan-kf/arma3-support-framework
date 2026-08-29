# Advanced Systems common utilities — canonical feature review

Primary outcome: **REVIEWED / DEFERRED AS A STANDALONE FEATURE;
CONSUMER-OWNED**.

This review covers the global helpers compiled by `fn_core.sqf` and
`fn_utils.sqf`: positional calculation, beam drawing, serialized positional
sound, number-to-voice tokenization, and the thin CORDIS notification/debug/
radio adapters. It does not reopen the accepted APS, Counter Battery Radar, or
Iron Dome contracts that consume some of them.

## Twelve-question review

1. **What should the user or integrator observe?** There is no independent
   user entry or advertised common-utility feature. Consumers use the helpers
   to produce APS effects/voice and CBR or module feedback. Those outcomes
   belong to the consuming feature.
2. **What does it do now?** `YOSHI_getFrontPosition` derives a point from
   velocity; the beam family broadcasts global coordinates and uses the
   singleton `onEachFrame` slot; `YOSHI_serverSay3dOnce` globally serializes
   one sound; `YOSHI_numToTextArray` tokenizes integers 0--199; the
   `YAS_fnc_*` wrappers delegate to CORDIS. `YAS_addMarker` and
   `YOSHI_beamVic2Pos` have no repository caller.
3. **Which machines own it?** Ownership is chosen by each caller rather than
   enforced by the helpers. APS owner-local interception calls the position
   helper; its effects route beam and sound coordinators to server and
   broadcast rendering/audio. CBR and module handlers inherit CORDIS routing.
   The helpers do not constitute an authority boundary.
4. **Which mechanics are generic?** Position sampling, Draw3D observation,
   audio observation, marker evidence, recipient/locality evidence, and
   bounded scheduling are generic Arma/Tribunal concerns. The present helper
   implementations are not automatically reusable Tribunal contracts.
5. **Which behavior is product-owned?** APS owns when an effect or voice line
   occurs and what it means. CBR owns its warning. Modules own their operator
   feedback. CORDIS owns routing and deduplication semantics.
6. **Are unusual engine requirements proven?** No. No controlled evidence
   establishes that the singleton `onEachFrame`, public coordinate globals,
   global sound mutex, or these exact remote-execution shapes are required.
7. **What is fragile or incomplete?** Concurrent beams overwrite shared
   positions and clear the global `onEachFrame` handler; all beam calls share
   one server debounce. All sounds share one server mutex. The marker helper is
   globally mutating and unreachable. `YOSHI_getPosTop` leaks temporary
   variables outside private scope. Wrapper authorization is only whatever
   CORDIS and the caller provide.
8. **Is a better mechanism available?** Stacked mission Draw3D handlers,
   per-effect identities, and consumer-scoped audio state are plausible, but
   replacing current paths requires a same-consumer A/B. No standalone outcome
   justifies a rewrite now.
9. **What is the stable contract and causal proof?** There is no standalone
   contract. A consuming review may require an exact visual/audio/radio effect
   and independently prove it from that consumer's real entry. It must not pass
   merely because a helper was called or a debounce flag changed.
10. **Which details remain free?** Every helper name, shared variable, token
    spelling, marker name, beam pulse cadence/width/color, scheduling primitive,
    and audio serialization mechanism remains replaceable unless a consumer
    deliberately adopts it as product behavior.
11. **Which mechanisms deserve characterization?** None yet. A consumer must
    first demonstrate necessity with a controlled alternative. Current code
    and incidental accepted runs are reachability evidence only.
12. **What belongs in Tribunal?** Existing product-neutral marker, framebuffer,
    locality, and event observers should be reused. Add an audio or Draw3D
    observer only when a concrete consumer needs it and the observer contains
    no Advanced Systems meaning.

## Reachability and evidence

Repository-wide callers are bounded:

* APS uses `YOSHI_getFrontPosition`, `YOSHI_serverBeamVic2Pos`,
  `YOSHI_serverSay3dOnce`, and number tokenization;
* CBR uses the CORDIS radio wrapper;
* APS/CBR module toggles use the curator-notification wrapper;
* Iron Dome uses only the debug wrapper;
* the marker helper, direct local beam helper, and client-side vehicle beam
  helper have no product caller.

Accepted APS, CBR, and Iron Dome runs prove those features while incidentally
executing some utilities. They do not prove beam concurrency, audible output,
notification audience, or the utilities as a public API. Autonomous clients
use `-noSound`, so sound remains explicitly unproven.

## False-PASS boundaries

Do not treat any of these as standalone success:

* a helper symbol compiling or being present in `missionNamespace`;
* a helper invocation, public coordinate value, debounce flag, or command
  return;
* one visible beam when concurrency is the claim;
* one missing sound when `-noSound` is active;
* a notification reaching any client when recipient scoping is the claim;
* direct invocation of the dead marker or beam helpers.

Consumer coverage must correlate exact consumer stimulus and identity with an
independent visible, audible, spatial, or recipient-specific outcome.

## Decisions and continuation

No product decision is needed merely to leave these helpers internal. Review a
helper only when a reachable consumer makes its outcome contractual. If
simultaneous APS effects or voice overlap becomes supported, first decide
per-effect concurrency and preemption policy, then run a matched multi-event
experiment. Remove or expose the dead marker/beam surfaces only as a separate
cleanup/product decision. Do not create a permanent standalone scenario.
