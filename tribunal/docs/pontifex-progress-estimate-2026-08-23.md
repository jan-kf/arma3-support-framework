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

## Current estimate after Vigil whitelist closure

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~86% | ~87% | 83–91% | medium |
| Permanent automated coverage | ~65% | ~66% | 62–71% | medium |

The remaining authentic Vigil whitelist-removal experiment moved from partial
coverage to accepted coverage. Two opposite operations now run through one
retained assigned-curator display with exact end-to-end identity correlation,
negative controls, replication, state retirement, and an independent cold repeat.
The modest increase reflects closure of a bounded existing surface rather than a
new large subsystem.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~90% | ~68% | task governor rewrite, recon/homepage decisions, feedback policy, any future stabilizer rewrite |
| Field Utilities | 20 | ~81% | ~46% | FPV authority/effects, towing, object handling/loading, airdrop feedback, land mass/terrain experiments |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~87%** | **~66%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

The whitelist removal/repeated-placement slice is terminal at `ACCEPTED / COVERED`; its runtime reconfiguration and client-N/JIP questions remain separate.
The next recommended unblocked feature is Field Utilities towing, whose product
decisions are established and whose reviewed implementation still requires
refinement and causal permanent coverage.
