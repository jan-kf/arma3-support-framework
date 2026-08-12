# Tribunal architecture

Tribunal is a generic Arma mod-validation framework. It owns deterministic
mission packaging, assertion parsing, lifecycle/reporting contracts, tier
metadata, and scenario discovery. It does not know individual mod features.

Projects register scenario roots and provide their own build/runtime adapter.
A scenario declares only its tier, expected assertions, required project mods,
and server/client SQF fragments. Tribunal executes those fragments through the
existing real-client lifecycle and records machine-readable evidence.

The current compatibility migration intentionally retains existing project
commands and assertion prefixes. A prefix is configuration, not framework
identity; this lets an established suite adopt Tribunal without invalidating
historical run artifacts.

Future Tribunal runners can add multi-client placement, locality probes,
latency profiles, visual/audio drivers, and replay while keeping the Scenario
contract stable.

## Direct-projectile fixture contract

`tribunal.mission.projectiles.direct_fixture_sqf()` supplies generic, server-
local direct-projectile injection for gameplay scenarios. It owns requested
launch-state application, same-frame requested-versus-observed evidence,
locality and trajectory sampling, physical-impact evidence, and cleanup. The
helper fails closed when the observed position, direction, or velocity is
outside its explicit tolerances; a scenario must not retry until it happens to
get a usable projectile.

Feature scenarios own only their feature-specific setup and assertions. For
example, Pontifex APS explicitly registers the Tribunal-created projectile
with APS, then correlates its netId with the APS ledger and its own resource
and protection assertions. This keeps projectile semantics reusable while
preserving causal, feature-specific evidence.

The runner treats protocol completion as terminal: complete PASS and complete
FAIL both trigger ordinary teardown immediately. The configured deadline is
only a fail-closed safety bound for incomplete or hung runs.
