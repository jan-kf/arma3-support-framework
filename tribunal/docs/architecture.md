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
