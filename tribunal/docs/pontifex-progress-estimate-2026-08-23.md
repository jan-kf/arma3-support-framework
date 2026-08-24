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

## Current estimate after Vigil hidden-pad characterization

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~90% | ~91% | 87–95% | medium |
| Permanent automated coverage | ~71% | ~72% | 67–76% | medium |

The Vigil transport hidden-pad mechanism moved from experimentation to bounded accepted characterization coverage. Three independent final runs (`20260824T165323Z-538afe85`, `20260824T165824Z-11607833`, and corrected-package run `20260824T170322Z-9b970179`) matched one server-local airborne `B_Heli_Light_01_F` approach with no destination pad against one exact `Land_HelipadEmpty_F`. Each no-pad control reached the arrival radius but remained airborne beyond 104 m; each pad treatment landed within 25 m and held three continuous settled seconds. Other classes, terrain, approaches, commands, locality, client-B, and JIP remain unclaimed.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~91% | ~71% | task governor rewrite, recon/homepage decisions, feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~93% | ~66% | FPV authority/effects, broader contact topology, airdrop feedback, mass and broader-terrain experiments, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~91%** | **~72%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

Vigil hidden-pad landing is terminal at KEEP + CHARACTERIZE ENGINE REQUIREMENT; ACCEPTED / COVERED for the exact server-local airborne class, clear Stratis corridor, `doMove` + `LAND` sequence, and 90-second deadline. Broader landing classes, terrain, approaches and locality remain open. The next recommended unblocked investigation is Fabricator staging/mass isolation; the mass cap remains an open defect after several rejected alternatives.
