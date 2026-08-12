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

## Capability contracts

Locality is declarative and evidenced, not inferred. A scenario names the
intended machine (`server`, `client-a`, or a future client identity), waits for
the engine-reported owner/local state, records every observed transition, and
fails before feature actions if the arrangement was not achieved. The
`locality-probe` capability scenario validates server ownership, transfer to
the authenticated client, execution exactly once on that client, and transfer
back to the server.

Clients are represented by `ClientIdentity` records and keyed maps. Each has
its own profile, Steam home, bridge address allocation, results origin, and
optional diagnostic endpoint. The current Pontifex adapter configures only
`client-a`, because there is one authenticated identity, but Tribunal's
scenario/protocol model accepts `client-b`, `client-c`, and future identities.

Evidence attachments incrementally extend existing schema-2 results. An
attachment has a type, origin, label, optional artifact path, and structured
metadata. This supports locality records, trajectories, events, screenshots,
audio captures, timing, and network measurements without changing scalar
assertion compatibility.

Generic gameplay fixtures follow one lifecycle:

1. setup;
2. verify setup and locality;
3. perform the action;
4. observe typed evidence;
5. assert feature meaning;
6. clean up every created resource.

Tribunal owns generic Arma mechanics. A project scenario owns the feature-
specific interpretation of those mechanics.

## Rendered-state observability

The `visual-framebuffer` capability scenario renders and removes a known
full-screen element. A test-only observer connects to Weston's existing
loopback-only VNC endpoint using VeNCrypt/X509Plain, captures the real
1280x720 Arma surface, and verifies presence and absence using tolerant
luminance/structure ratios. It stores baseline, present, absent, and protocol
artifacts. Exact-pixel matching is deliberately not the sole strategy.

Framebuffer input remains an optional backend. Mission/native interfaces are
preferred; authenticated RFB input is appropriate only when the UI or input
path itself is under test. No host VNC publish is required by the capability
probe.

## Network-condition boundary

The client has an empty capability bounding set. A direct `tc netem` probe in
the confined client therefore fails with `RTNETLINK answers: Operation not
permitted`, as intended. Network impairment must not add `CAP_NET_ADMIN` to
the Arma client/server containers.

Tribunal defines `lan`, `normal`, `remote`, and `poor` profiles, but applying a
non-baseline profile is reserved for a narrow host helper. That helper should:

* accept only a run ID, validated Docker labels, client identity, and named
  profile;
* resolve only the run-scoped client veth peer;
* hold only `CAP_NET_ADMIN` (for example in a transient service with a strict
  command allow-list);
* apply and read back netem on that one interface;
* record requested and observed qdisc/RTT evidence in the manifest;
* remove the qdisc during teardown and fail closed if verification or cleanup
  fails.

This is the least-privilege design; host-wide interfaces, the Docker bridge,
and unrelated containers remain untouched.

## Audio feasibility

Current automated clients launch Arma with `-noSound`, and the image contains
no PulseAudio/PipeWire capture tools. Engine/mod event assertions are therefore
available today, but they do not prove actual playback.

Actual playback evidence should be a separate opt-in capability: omit
`-noSound` only for that scenario, start a container-local null sink, record
its monitor to a run artifact, and compare duration/spectral fingerprints with
tolerances. This preserves isolation and supports positive and negative per-
client assertions without exposing host audio. Until that backend exists,
Tribunal must label sound-path events as internal evidence and must not claim
audible playback.

## Optional Pythia backend

Pythia remains unadopted. Its primary project documents SQF-to-Python type
conversion, embedded Python, and official 64-bit Linux support, so it is a
credible future test-only backend. It still requires an SQF `callExtension`, a
test mod, and separate Windows/Proton and Linux artifacts. Native SQF already
provides clearer locality and state-query evidence with less startup and
debugging surface. Pythia may be reconsidered for computation-heavy offline
analysis, but production mods and baseline Tribunal scenarios must not depend
on it.
