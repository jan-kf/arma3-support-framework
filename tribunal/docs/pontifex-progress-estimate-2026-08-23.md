# Pontifex feature-review and permanent-coverage estimate — 2026-08-23

This is an engineering estimate over meaningful feature surfaces in the
canonical inventory, not a ratio of assertions. Small features carry weight 1,
medium features 2, and large subsystems 3. Status credit is deliberately
different for the two measures: accepted coverage receives 100%; strong partial
coverage about 60–80%; reviewed refine/experiment/defer outcomes about 55–65%
for review understanding but normally 0% permanent coverage; incidental proof
at most 10–25%; and unknown scaffolding 0–25% review and 0–10% coverage.

The model contains 100 total weight units: CORDIS 10, Advanced Systems 21,
Vigil 36, Field Utilities 20, and cross-mod composition 13. This convenient
total is a consequence of the selected inventory surfaces, not a target fitted
to the result.

## Current estimate after selective ACE cargo closeout

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~93% | ~94% | 90–97% | medium |
| Permanent automated coverage | ~74% | ~75% | 70–79% | medium |

The Field Utilities ACE-size override moved from an uncovered source mismatch
to a bounded accepted policy. Exact Bridge and OPHANIM boxes explicitly retain
their configured ACE size 2; ordinary ammo boxes retain runtime size -1. Final
runs `20260825T202333Z-62ab9c1b` and `20260825T202453Z-fd022bea` each passed 4
server and 2 client feature assertions with zero failures, authentic ACE loaded
membership/attachment, remote replication and full cleanup. Existing native and
contact behavior also passed its unchanged regression in
`20260825T202621Z-3b757834`.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~91% | ~71% | task governor rewrite, recon/homepage decisions, feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~99% | ~81% | FPV authority/effects, broader contact topology, airdrop feedback, extreme/water Fabricator terrain, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~94%** | **~75%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

Selective ACE cargo is accepted only for the exact Bridge and OPHANIM classes,
pinned ACE 3.21, one dedicated server and one authenticated client. Other
classes/versions, ownership migration, client-B/JIP, menus, unload and concurrent
ACE/native requests remain explicit exclusions. The next unblocked source audit
is Vigil's CAS auto-engage debug channel; the reconnaissance is only a lead, so
canonical reachability, audience and runtime behavior must precede any decision.
