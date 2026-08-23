# Vigil helicopter stabilizer — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REVIEWED / DEFERRED`.** A controlled physical A/B reached
the real force path but did not meet independently fixed usefulness gates.
Automatic transport/CAS enrollment is therefore off; the legacy algorithm is
retained only as explicitly enabled experimental code, not product behavior.

## Scope and reachability

The reviewed path is `fn_heliStabilizer.sqf`, its server PFHs, and enrollment
from `task_transport/fn_transport_task.sqf`. Broad automatic enrollment of all
helicopters/VTOLs is commented out. Current reachable scope is Vigil
transport/RTB (including CAS handoff into that lifecycle), not every aircraft.

The hidden transport `do_not_climb` state now defaults false. Broad automatic
registration remains commented out. The shipped UI cannot enable the feature.

## Canonical review questions

### 1. What should the user observe?

During an AI transport/RTB approach, enabled stabilization is apparently
intended to reduce the helicopter's tendency to balloon upward while
decelerating, without compromising terrain clearance, arrival, or landing.

### 2. What does it do now, including controls?

The server samples enrolled aircraft. It excludes slow/low aircraft,
player-piloted or remote-controlled aircraft, nonlocal/dead/engine-off aircraft,
and aircraft whose forward terrain samples violate a fixed buffer. When speed
decreases while ASL altitude and pitch increase, it enrolls the aircraft in a
per-frame worker. That worker applies a downward world-Z force proportional to
altitude-gain squared, vertical-speed squared, pitch, and mass until altitude,
speed, or pitch exits.

The per-object disable variable and task enrollment boolean remain experimental
surfaces. Production transport and CAS RTB callers pass false.

### 3. Which machine and lifecycle own it?

The server starts the sampler and only mutates server-local aircraft.
Client/HC-owned AI is skipped. The unused registry broadcast was removed.
Explicit experimental enrollment now has one unregister path that removes the
aircraft from both registries and clears its sample state at finalization.

### 4. Which mechanics are generic?

Aircraft trajectory, velocity, pitch, terrain clearance, locality, pilot state,
force-application telemetry, and paired-flight comparison are generic Tribunal
observation mechanics. Vigil owns enrollment, trigger, safety, and intended
flight outcome.

### 5. Which behavior is product-owned?

Eligible task/aircraft/pilot, enabled default/UI control, acceptable ballooning,
safety bounds, terrain policy, owner-routing, and terminal cleanup are Vigil
policy.

### 6. Are unusual engine requirements proven?

The A/B proves that the current server-local `addForce` path can alter a real AI
flight, but not that its nonlinear formula is useful enough to ship. BIKI says
`addForce` lasts one frame, uses world-space force and object-relative position,
and requires locality. The trial also directly showed that model-forward terrain
probes can suppress all sampling even when the eventual landing itself is safe.
The exact sampling cadence and a safe replacement bound remain uncharacterized.

### 7. Which details are fragile or incomplete?

The force is nonlinear and unbounded. Terrain probes follow model-forward, not
velocity, and include ground beyond the destination. The worker repeatedly
entered/exited during eligible treatment. These private mechanics are not a
specification and automatic use is deferred.

### 8. Is a better native mechanism available and proven?

Matched flights show untreated Arma AI completed the tested approaches and
landings. No replacement mechanism was compared, so this review neither claims
vanilla AI is universally adequate nor specifies a new stabilizer.

### 9. What is the candidate contract and causal proof?

The author decision was conditional:

> For a server-owned AI aircraft in a Vigil transport/RTB with stabilization
> enabled, a genuine deceleration-and-climb event is damped relative to a
> matched disabled control, while terrain clearance and successful
> arrival/landing remain safe. Excluded aircraft and unsafe-terrain states
> receive no artificial force, and task finalization ends all feature effects.

That proposition was tested and not established. The current stable product
contract is narrower: normal transport and CAS RTB must not receive the rejected
legacy force, must still complete physically, and must leave no stabilizer state.
Any future automatic mitigation needs a new predeclared causal comparison.

### 10. Which details must remain replaceable?

PFH cadence, constants, formula, terrain sample distances, registry shape,
debug strings, and whether damping uses force or another verified mechanism.

### 11. Which mechanisms deserve characterization?

The retained negative A/B characterizes only the current algorithm's failure to
meet its material-effect gate on one class/corridor/build. A future rewrite
needs its own safe bound, multiple aircraft/corridors, cancellation, terrain,
and ownership experiments.

### 12. What should be promoted into Tribunal?

Only generic aircraft trajectory and force-event observation if another
consumer needs it. Trigger and stabilization semantics stay in Vigil.

## Controlled physical evidence

Live run `20260823T135908Z-f6ce532b` used real server-local
`B_Heli_Light_01_F` transports, engine/crew/full simulation, ordinary Vigil
transport tasks, 0.1-second trajectory sampling, identical weather/fuel/height,
and the real task enrollment boolean as the only treatment difference. All
valid arms reached the LZ, landed, settled, stayed undamaged, and had owner 2.

Two disabled flights on the original eastbound corridor independently produced
the balloon stimulus but peaked at 92.06/92.37 m ATL and 12.59/12.57 m/s upward.
The two enabled flights were indistinguishable (92.01/92.07 m and 12.55/12.54
m/s) because the 500 m model-forward probe saw the hill beyond the LZ; exact
predicate telemetry showed `terrainSkip=true` and sample state `[-1,-1,-1]`
throughout. This is the terrain-guard negative, not treatment evidence.

A flat northbound land corridor held terrain around 3–6 m ASL through and beyond
the LZ. Its disabled replicates peaked at 81.95/82.33 m ATL and 1.33/1.29 m/s
upward. Before enabled results were observed, material benefit was fixed at at
least 5 m lower peak approach altitude **and** at least 1 m/s lower peak upward
velocity—about 13x/26x the respective control spreads. Enabled replicates
reached the real worker for 21/33 sampled intervals and landed safely, but peaked
at 80.42/79.65 m and 1.41/1.04 m/s. They missed both gates; one worsened peak
upward velocity. Handler execution, membership, and landing were not used as
the outcome oracle.

Exploratory run `20260823T143318Z-c3288710` first exposed large between-flight
AI variance and lane effects. The final artifact-quality Live run
`20260823T144525Z-a5b9d6a6` therefore ran two simultaneous parallel pairs and
reversed treatment between x=1880 and x=1920. In the west lane, control peaked
at 71.5199 m/0.494478 m/s and treatment at 67.0442 m/0.230856 m/s: reductions
of 4.4757 m/0.263622 m/s, below both gates. In the east lane, control peaked at
82.5645 m/1.66972 m/s while treatment worsened to 89.5423 m/6.21236 m/s. The
treatments reached 18/28 active samples while controls reached zero. All four
aircraft remained local to owner 2, landed, settled, and had zero damage. The
dedicated `stabilizer-physical-series.rpt` retains all 2,416 individual 0.1 s
physical samples (SHA-256
`62f2fc9a6d34fcd2687d7b4658fca7cdadbee00d847fc3ccd9dd35566f6bed80`).

The initial no-waypoint disturbance was rejected from product evidence because
AI shut the engine down after the transient. One proposed shoreline start was
also rejected because the aircraft died before task initialization. These are
fixture failures, not feature outcomes. The first run's single oversized RPT
series line was truncated; later runs corrected this by emitting bounded
per-sample records. A blocking Live-stop artifact defect was also fixed: if the
operator has already removed a container, polling/finalization now preserves the
last captured RPT instead of overwriting it with Docker's lookup error. The
compact summaries and complete final-run series remain retained artifacts.

## Activation, deactivation, and false-PASS audit

Automatic activation is now false at the hidden client default, handler default,
transport request, and CAS RTB handoff. Explicit experimental true still uses
the real detector. Its finalizer removes main/active entries and sample state.
The permanent transport scenario samples the full dispatch/RTB lifecycle and
fails if automatic registration, active force, or sample state appears.

False-PASS exclusions: both control replicates exhibited real flight and the
qualifying disturbance; all arms used the same class, corridor and task path;
server locality/owner were recorded; treatment reached the actual worker only
on the eligible corridor; physical altitude/velocity—not internal state—were
the effect oracle; thresholds preceded treatment; safe landing alone could not
pass; state was reset between arms.

## Fresh autonomous acceptance

Fresh Tier 3 run `20260823T150347Z-06abb5c7` passed 16/16 server and
10/10 real-client assertions. The exact server-local aircraft flew 451.767 m to
the LZ, settled undamaged, flew 452.955 m home, settled undamaged, and was then
removed. The lifecycle monitor observed no main-registry or active-force entry,
no sample state remained, client-a observed the same dispatch/waiting/RTB/home
lifecycle, and container/network/run-state cleanup completed. An immediately
preceding identical run was rejected because the aircraft took full ground
damage before RTB departure; its no-force assertion passed, but its physical
round trip correctly failed. The unchanged replicate distinguishes that fixture
outcome from the stabilizer disposition without weakening the physical oracle.

## Sacred Texts and knowledge disposition

Pre-work dossiers covered `addForce`, `getCenterOfMass`, `getMass`, `velocity`,
`speed`, `vectorDir`, `getPosASL`, `getPos`, `getTerrainHeightASL`,
`modelToWorld`, `local`, `currentPilot`, `remoteControlled`, and `isEngineOn`.
Useful current-applicable BIKI facts are summarized in
[`sacred-texts-helicopter-stabilizer-trial.md`](sacred-texts-helicopter-stabilizer-trial.md).
No generic Arma lemma was accepted: the trial isolates a Vigil formula/policy,
and the terrain observation is too fixture-specific to generalize. The negative
project characterization is retained here and in its Live artifact, not placed
in `OUR VERIFIED NOTES`. Evidence Contract v1 revision 1 and its immutable
`stabilizer-evidence-package-correction-2.v1.json` field-name correction were
ingested; repeating revision 2 changed no
ledger counts, and the full knowledge audit passed. Reviewed distillation found
zero new generic lemmas or conjectures from this feature.

## Disposition

**Reviewed and deferred as an automatic product feature.** The current force
failed its predeclared causal usefulness gate, so normal transport/CAS no longer
enrolls it. Existing physical transport coverage now also proves the deferred
mechanism stays inactive and clean. A future stabilizer is a new bounded
experiment/rewrite, not continuation of an accepted algorithm.
