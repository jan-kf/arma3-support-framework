# Vigil helicopter stabilizer — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REVIEWED / NEEDS EXPERIMENTATION`.** Contrary to the old
inventory label, this code is active: normal transport and RTB tasks enroll
their aircraft by default. Retained runs prove the force path was reached, but
not that it caused a useful or safe outcome.

## Scope and reachability

The reviewed path is `fn_heliStabilizer.sqf`, its server PFHs, and enrollment
from `task_transport/fn_transport_task.sqf`. Broad automatic enrollment of all
helicopters/VTOLs is commented out. Current reachable scope is Vigil
transport/RTB (including CAS handoff into that lifecycle), not every aircraft.

The transport form retains a `do_not_climb` state defaulting to true and passes
it into task data. Its visible checkbox is commented out, so the shipped UI
cannot change the default.

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

The per-object disable variable and the task's enrollment boolean are negative
surfaces. The latter defaults true and is not currently user-selectable.

### 3. Which machine and lifecycle own it?

The server starts both PFHs and only mutates server-local aircraft. Transport
initialization adds the aircraft; finalization removes it from the main list.
Client/HC-owned AI is silently skipped. The main registry is unnecessarily
`publicVariable`d despite no client reader found.

Finalization does not remove the aircraft from the active deceleration list or
clear its sample state. A cancelled/failed live aircraft can therefore continue
receiving force until a physical exit predicate happens.

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

No. `addForce` efficacy and cadence, the world-Z choice, forward terrain
sampling, the nonlinear formula, and AI reaction have no controlled
characterization. The nominal two-second sample constant also does not clearly
produce a two-second comparison window because state is rewritten on
intervening checks.

### 7. Which details are fragile or incomplete?

The force is nonlinear and unbounded. Terrain probes follow model-forward, not
necessarily velocity. Active deceleration can outlive task enrollment.
Repeated entry logs in retained runs indicate frequent exit/re-entry but do not
establish correctness. The user control is hidden while true remains default.

### 8. Is a better native mechanism available and proven?

No comparison has been run. Successful vanilla/Vigil landings do not prove this
force is necessary. Do not replace or preserve the algorithm until matched
enabled/disabled evidence exists.

### 9. What is the candidate contract and causal proof?

Pending product decisions:

> For a server-owned AI aircraft in a Vigil transport/RTB with stabilization
> enabled, a genuine deceleration-and-climb event is damped relative to a
> matched disabled control, while terrain clearance and successful
> arrival/landing remain safe. Excluded aircraft and unsafe-terrain states
> receive no artificial force, and task finalization ends all feature effects.

Proof requires matched flights whose control arm independently exhibits the
trigger stimulus. Force telemetry is supplemental; the outcome oracle is the
independent trajectory/vertical-velocity comparison plus terrain clearance and
task completion. Registry/deceleration membership and successful landing alone
must not pass.

### 10. Which details must remain replaceable?

PFH cadence, constants, formula, terrain sample distances, registry shape,
debug strings, and whether damping uses force or another verified mechanism.

### 11. Which mechanisms deserve characterization?

Matched trajectory response to the force; AI variability; terrain guard;
cancel/failure cleanup; server-local versus HC ownership; and the true sampling
window. Characterize, do not assume, a safe force bound.

### 12. What should be promoted into Tribunal?

Only generic aircraft trajectory and force-event observation if another
consumer needs it. Trigger and stabilization semantics stay in Vigil.

## Existing evidence

Accepted transport/CAS runs prove aircraft can complete tasks while this code is
active, which is only non-regression evidence. Retained runs
`20260813T184341Z-317a1605` and `20260816T151957Z-c7e7de23` repeatedly log
`[YSF_HelicopterStab] Culling Altitude...`; that message is emitted only when
the active per-frame path starts. It proves reachability, not a causal benefit
or safe force.

## Product decisions and first experiment

Decide transport-only versus broad enrollment, always-on versus restored UI
control, the measurable outcome/safety bound, server-local-only versus
owner-routed AI, and cancellation/terrain-guard behavior.

Then run multiple paired fresh `B_Heli_Light_01_F` flights in one Live session
using the accepted transport corridor. Hold class, crew, fuel, home/LZ, weather,
and requested altitude fixed; vary only stabilization. Independently record
ASL/ATL, velocity, speed, pitch, distance, terrain clearance, locality, engine,
pilot, and arrival. Both arms must exhibit a qualifying deceleration/climb
interval or the pair is invalid. Compare peak altitude gain and vertical
velocity, then prove safe landing. Add a terrain-guard negative and a
midair-cancellation cleanup probe. If AI variance remains dominant after
several matched pairs, retain `NEEDS EXPERIMENTATION`; do not inject private
trigger state to manufacture a PASS.

## Disposition

**Reviewed, active, and incidentally exercised; effect not covered. Needs
experimentation.** No product or scenario code changed.
