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

## Current estimate after Field contact-handler closure

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~89% | ~90% | 86–94% | medium |
| Permanent automated coverage | ~70% | ~71% | 66–75% | medium |

The Field contact hook moved from experimentation to bounded accepted permanent coverage. A matched server-local `B_supplyCrate_F`/`B_Truck_01_transport_F` physical A/B proves exact contact in both arms, treatment-only attachment, client-a replication, no added carrier instability relative to the handler-free control, and controlled no-leak teardown. Client ownership/migration, broader classes/surfaces, repeated contacts, deletion while attached, client-B, and JIP remain unclaimed.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~90% | ~68% | task governor rewrite, recon/homepage decisions, feedback policy, any future stabilizer rewrite |
| Field Utilities | 20 | ~93% | ~66% | FPV authority/effects, broader contact topology, airdrop feedback, mass and broader-terrain experiments, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~90%** | **~71%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

Field automatic contact attachment is terminal at KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED for the declared server-owned crate/truck topology. Broader classes/localities remain open. The next recommended unblocked feature is a controlled Vigil transport hidden-pad landing-mechanism A/B; the Fabricator mass cap remains an open defect after several rejected alternatives.
