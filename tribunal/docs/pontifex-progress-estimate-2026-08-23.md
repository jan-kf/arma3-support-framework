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

## Current estimate after Vigil shared-debug ownership closeout

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~95% | ~96% | 92–99% | medium |
| Permanent automated coverage | ~76% | ~77% | 72–81% | medium |

The shared production debug wrapper moved from duplicate, initialization-order-
sensitive ownership to one owner in `fn_utils.sqf`. A pre-change cold run proved
the final runtime identity was already correct; the refinement removes the
latent harness fallback rather than changing the accepted route. Exact disabled
and enabled tokens from both AAE and the shared wrapper entered the server RPT
path while client-a independently received the CORDIS route under false/true
`YSF_showDebugMessages`. Final runs `20260825T221344Z-3814387b` and
`20260825T221507Z-12376258` each passed 3 server and 3 client assertions with
zero failures and complete restoration.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~96% | ~77% | task governor rewrite, recon/homepage decisions, radio/chat/curator feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~99% | ~81% | FPV authority/effects, broader contact topology, airdrop feedback, extreme/water Fabricator terrain, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~96%** | **~77%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

Vigil production debug is accepted for unconditional server logging, sole
utilities ownership, and the registered false/true client gate on one
authenticated client. Visible pixels, client-N/JIP, client-originated calls and
volume remain excluded; the laser harness remains deferred. The next
highest-value surface is the reviewed Vigil task-governor rewrite, whose
authority and lifecycle defects require product refinement and full consumer
regression rather than a narrow observation-only scenario.
