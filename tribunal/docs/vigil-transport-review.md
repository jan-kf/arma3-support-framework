# Vigil helicopter transport / reinsertion review

Review outcome: **REFINE BEFORE PERMANENT COVERAGE**.

## Behavioral contract

A client with a valid selected transport and LZ can submit one dispatch. The
correct helicopter must leave home, make meaningful physical progress toward
the LZ, land without crashing, remain settled and available, then accept RTB,
return to its originally recorded home, land and settle there. A concurrent
duplicate request is rejected, terminal failures are bounded, authoritative
task/world state agrees with client-visible request state, and fixture/task
resources are clean afterward.

Transport and reinsertion are not separate implementation modes. “Reinsertion”
is terminology for the transport lifecycle; before this review only outbound
transport existed. The explicit return phase added here is an RTB mode of the
same task handler.

## Twelve-question review

1. **User observation.** Select a crewed friendly cargo helicopter and LZ,
   dispatch it, see it fly and land, wait, then command return to its home.
2. **Current behavior and negative paths.** The client built a governor task;
   the server selected a nearby/safe LZ, created a MOVE waypoint, issued LAND,
   and finalized. There was no RTB UI/path, bounded timeout, durable waiting
   state, or duplicate rejection. Dead aircraft was handled by the governor;
   missing/dead crew and unsuitable landing could otherwise stall or misreport.
3. **Machines and paths.** Vigil selection/request state is client-local. The
   request crosses YCD's server-once boundary. The dedicated server owns the
   aircraft, pilot group, waypoints, task governor, landing and authoritative
   state. World state replicates back to the client.
4. **Generic mechanics.** Vehicle/crew creation, locality, waypoint movement,
   trajectory sampling, altitude, velocity, ground contact and settling are
   Arma mechanics and belong in Tribunal evidence tooling.
5. **Product behavior.** Eligibility, Vigil selection and request construction,
   LZ policy, waiting/home states, RTB, task serialization and UI status are
   Vigil responsibilities.
6. **Proven unusual requirements.** None. Hidden pads plus `land "LAND"` worked
   in calibration but have not passed a controlled A/B proving necessity.
7. **Accidental/fragile findings.** Vehicle config side was CIV even with a
   WEST crew; `ignore_en` was dropped by positional arguments; fallback pads
   used ASL z=0; landing passed after one touching/ready tick; repeated task
   assignment replaced active work; mission/end waits were unbounded; and a
   random repeated zero-radius waypoint call had no demonstrated purpose.
8. **Native alternatives.** MOVE waypoints and `land` are already native. A
   `doMove`/waypoint-only/no-pad alternative needs a controlled comparison
   before replacing the successful path. No characterization test is added.
9. **Stable contract.** The user-facing round trip, physical progress, valid
   settled landings, availability while waiting, correct home, duplicate
   rejection, bounded failure, locality and cleanup.
10. **Free implementation details.** Exact waypoints, task-map keys, polling
    cadence, coordinates, helicopter class, LZ-search algorithm, radio calls,
    flight altitude and landing-command sequence may change with adapters.
11. **Characterization.** None yet. Pad/land sequencing is explicitly marked
    NEEDS EXPERIMENTATION rather than fossilized.
12. **Promoted Tribunal mechanics.** Product-neutral aircraft snapshots,
    bounded trajectory collection, movement/approach/altitude evidence,
    landing/settling facts, crew/locality evidence and timeout detection.

## Architecture and lifecycle

Asset discovery scans the configured/whitelisted map vehicles, classifies
transport helicopters by cargo capacity, lock state and effective crew side,
and stores selection in client `uiNamespace`. Dispatch captures grid, altitude,
stabilization and enemy-handling values and sends a unique task server-side.
The server records home once, selects an existing helipad or safe LZ, configures
AI, moves, lands, requires three continuous settled seconds, then publishes
`waiting`. RTB targets recorded home through the same handler and publishes
`home`. Active duplicates are rejected. A 300-second task deadline and crew
validation fail closed. Cancellation still follows the governor's finalizer.

Reopening/reconnecting reconstructs world status from public aircraft state;
the private in-progress UI edits remain client-local, as intended. A future
second client should observe aircraft/task state but not inherit client-a's
selection/edit buffer.

## Evidence and calibration

Live baseline `20260813T153422Z-65c09545` used a server-local, crewed
`B_Heli_Light_01_F` on clear Stratis terrain. The outbound aircraft traveled
about 803 m, settled about 3.3 m from its LZ, and returned about 806 m to roughly
3 m from home with zero damage and near-zero velocity. Reissuing the real
dispatch path toward home proved the physical return behavior before an RTB
contract was added. Live inspection also proved the eligibility bug: crewed
WEST helicopters reported `side vehicle == CIV`, while their commander group
was WEST.

The permanent deterministic corridor is clear Stratis terrain from
`[1900,5600]` to `[2350,5600]`, with explicit pads and no combat/weather. The
test rejects task-only false passes: it requires substantial travel, decreasing
distance, altitude, final LZ/home proximity, ground contact, `unitReady`, speed
below 2 m/s, survival, low damage, five seconds of stable waiting, server/pilot
locality, unique task IDs and inactive manager cleanup.

Potential false positives rejected include no movement, wrong helicopter,
nearby hover, momentary bounce, crash near destination, despawn, stale previous
state, duplicate overwrite, return-state-only success, and client/server state
disagreement.

Fresh autonomous run `20260813T161039Z-963a4092` passed 15 server and
10 client assertions with zero failures. Outbound evidence contained 142
samples, 452.115 m maximum travel, 0.388 m minimum sampled distance and a
2.139 m settled LZ result. Return evidence contained 203 samples, 453.822 m
maximum travel and a 2.156 m settled home result. Both final states had ground
contact, `unitReady`, near-zero speed and zero damage. The server-local
aircraft/pilot/group were owner 2, while client-a observed the replicated
non-local aircraft. Cleanup removed the aircraft and left its manager disabled.

## Controls and deferred work

The first permanent negative control is duplicate dispatch while active. The
review also adds fail-closed missing/dead-crew validation and bounded timeouts.
Unsafe/unreachable terrain, destruction during flight, cancellation, RTB before
arrival and client-b observation are meaningful follow-ups, but do not belong
in the stable clear-corridor MVP.

Rotary-wing CAS is next. It may reuse Tribunal trajectory/locality/stall/RTB
evidence, but must receive its own review of target selection, attack evidence,
ammunition and hostile/friendly controls before implementation or coverage.
