# Pontifex → Tribunal boundary audit

## Tribunal-owned infrastructure

| Existing responsibility | Tribunal boundary |
| --- | --- |
| Deterministic PBO construction and footer hashing | `tribunal.mission.pbo` |
| PASS/FAIL line parsing and fail-closed completion checks | `tribunal.assertions.protocol` |
| Atomic result artifacts | `tribunal.reporting.artifacts` |
| Tier and scenario contracts | `tribunal.runner.model` |
| Scenario discovery | `tribunal.discovery` |
| Future runners, runtime provisioning, networking, latency, Live Mode, and reporting | `tribunal/` extension points |

## Pontifex-owned product content

Pontifex retains its mod builds, component policy, authenticated installation
adapter, security policy, and all feature scenarios. The APS scenario contract
is at `mods/advanced-systems/tests/tribunal/aps_intercept.py`; future VIGIL,
Field Utilities, and CORDIS scenarios belong beside their respective features.

## Compatibility migration

Existing `./pontifex` commands and `PONTIFEX_TEST` log prefix remain intact.
They are Pontifex's adapter to Tribunal, preserving existing E2E artifacts and
automation while generic code moves behind the new namespace. The generated
APS SQF fixture remains in that adapter for this initial migration because
moving it would unnecessarily alter the accepted autonomous mission. Its
feature contract now lives with Advanced Systems, and the adapter discovers it
through Tribunal rather than carrying APS assertion names.

The next extraction can move the unchanged SQF fragments into the same feature
directory without changing the Tribunal scenario contract or any lifecycle.
