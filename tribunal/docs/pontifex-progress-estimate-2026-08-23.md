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

## Current estimate after Vigil CAS debug-channel closeout

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~94% | ~95% | 91–98% | medium |
| Permanent automated coverage | ~75% | ~76% | 71–80% | medium |

The CAS auto-engage debug adapter moved from an uncovered hardcoded private gate
to Vigil's supported setting contract. Unique disabled and enabled tokens always
entered the server RPT path while client-a independently received the exact
CORDIS route under false/true `YSF_showDebugMessages` values. Final runs
`20260825T211810Z-e22f0ec6` and `20260825T211937Z-cc730425` each passed 3 server
and 3 client feature assertions with zero failures and complete restoration.
The unchanged full CAS scenario passed in `20260825T212117Z-841a8c18`.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~93% | ~74% | task governor rewrite, recon/homepage decisions, radio/chat/curator feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~99% | ~81% | FPV authority/effects, broader contact topology, airdrop feedback, extreme/water Fabricator terrain, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~95%** | **~76%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

CAS auto-engage debug is accepted for unconditional server logging and the
registered false/true client gate on one authenticated client. Visible pixels,
client-N/JIP, client-originated calls and volume remain excluded. The next
unblocked source audit is the developer laser harness's conditional shared-debug
fallback; reconnaissance is only a lead, so canonical registration order and
runtime function identity must precede any decision.
