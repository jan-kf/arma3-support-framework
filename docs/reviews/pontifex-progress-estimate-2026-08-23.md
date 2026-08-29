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

## Current estimate after Vigil rotary-CAS physical-oracle closeout

| Measure | Before | After | Reasonable after range | Confidence |
| --- | ---: | ---: | ---: | --- |
| Feature-review program | ~97% | ~97% | 94–99% | medium |
| Permanent automated coverage | ~81% | ~82% | 77–86% | medium |

The already reviewed CAS lifecycle now has a stable physical-impact oracle:
independently observed exact fire must correlate with hostile-local `HitPart` or
an exact mods/ammunition `HandleDamage` callback, while every equivalent
control channel remains empty. Final run `20260826T021218Z-72eb945f` passed all
17 server and 6 client feature assertions with zero failures and complete
cleanup. Because the feature review and most CAS lifecycle coverage already
existed, review completion stays about 97%; closing this last oracle gap adds
about one weighted coverage point.

## Current family estimate

| Mod / family | Weighted surface | Review completion | Permanent coverage | Biggest remaining gaps |
| --- | ---: | ---: | ---: | --- |
| CORDIS | 10 | ~90% | ~84% | sound/radio presentation, debug observation, ownership migration, client-N/JIP |
| Advanced Systems | 21 | ~86% | ~67% | APS anti-drone policy/authority, CBR concurrency policy, Iron Dome client-owned threats and audio |
| Vigil | 36 | ~99% | ~92% | recon/homepage decisions, radio/chat/curator feedback policy, other landing classes/terrain, any future stabilizer rewrite |
| Field Utilities | 20 | ~99% | ~81% | FPV authority/effects, broader contact topology, airdrop feedback, extreme/water Fabricator terrain, towing locality breadth |
| Cross-mod composition | 13 | ~89% | ~80% | true client-B/JIP, ownership migration, remaining partial module reversals, broader replicated-state lifecycle |
| **Overall** | **100** | **~97%** | **~82%** | weighted combination above |

## Sensitivity and next block

The estimate could move most if the inventory splits large features more
finely, if reviewed/deferred understanding receives less credit, or if partial
consumer scenarios are judged narrower than their current contracts. The
permanent-coverage number is lower-confidence for presentation/audio and
multi-client behavior because the autonomous client uses `-noSound` and only
one independently authenticated identity exists.

The governor lifecycle, one-client declarative authority boundary, and bounded
rotary-CAS physical-impact oracle are accepted. CAS does not claim material
damage, penetration, kill, sensor/reveal generality, other target or aircraft
classes, client-B/JIP, or poor-network behavior. The next highest-value
unblocked investigation is the Fabricator pond/coastline/water-recipient
placement boundary; it can vary water geometry while retaining the accepted
single-delivery authority, contents, settlement, and cleanup contract.
