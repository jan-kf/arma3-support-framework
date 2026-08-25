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

## Current estimate after Vigil governor-lifecycle closeout

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~96% | ~97% | 93–99% | medium |
| Permanent automated coverage | ~77% | ~79% | 74–83% | medium |

The server-owned Vigil governor lifecycle moved from divergent terminal paths to
one generation-aware finalizer. Normal completion, early completion, failure,
accepted cancellation, and vehicle loss now finalize exactly once; active
replacement is rejected; and a finalizer-installed successor is preserved.
Final runs `20260825T224551Z-057295d6` and
`20260825T224723Z-f0515a23` each passed 9 server and 1 client feature assertions
with zero failures and complete restoration. Client-authored handler maps remain
outside coverage and behind a mandatory authority rewrite.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~98% | ~83% | governor declarative authority rewrite, recon/homepage decisions, radio/chat/curator feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~99% | ~81% | FPV authority/effects, broader contact topology, airdrop feedback, extreme/water Fabricator terrain, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~97%** | **~79%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

The server-owned governor terminal lifecycle is accepted for one dedicated
server and harmless server-local tasks. Client request authentication,
declarative schemas, forged code-bearing payloads, cancellation eligibility,
retry/invalid-result policy, terminal-history retention, headless/client-owned
vehicles, client-N and JIP remain excluded. The next highest-value surface is
the remaining governor authority rewrite. A separate CAS combat-effect oracle
twice observed correlated fire and a target-local damage event with zero net
damage; that consumer investigation does not reduce the accepted lifecycle
scope and is not silently counted as a passing regression.
