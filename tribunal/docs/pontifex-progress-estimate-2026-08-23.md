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

## Current estimate after Fabricator mass/carry closeout

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~91% | ~92% | 88–96% | medium |
| Permanent automated coverage | ~72% | ~73% | 68–77% | medium |

The Fabricator mass and staging candidate moved from an apparent open defect to accepted boundary coverage. In final authentic runs `20260824T184743Z-361320ec` and `20260824T185113Z-a5792be7`, the exact server-owned clone was visible, unattached and mass 200 immediately before the real publication call. Client-a then started the product's intended ACE carry on that same net ID and observed it attached to the exact player, explaining the later `getMass = 1e-12`. Each run passed 28 server and 11 client feature assertions (32 and 15 including smoke), with zero failures and full cleanup. No Pontifex product source changed; staging depth and cadence remain deliberately unfrozen.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~91% | ~71% | task governor rewrite, recon/homepage decisions, feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~96% | ~71% | FPV authority/effects, broader contact topology, airdrop feedback, broader-terrain Fabricator experiments, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~92%** | **~73%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

Fabricator mass/carry is terminal at KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED for the exact single-result boundary on one dedicated server and one authenticated client. The raw hide/relocate calibration rejected staging visibility as the cause, while the authentic scenario proves the pre-publication cap and intended post-publication carry without freezing private choreography. The next recommended unblocked investigation is Fabricator broader-terrain placement characterization for gradient and obstruction behavior; pond, coastline, water-recipient, client-B and JIP domains remain bounded.
