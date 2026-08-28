# Vigil helicopter transport / reinsertion review

Review outcome: **KEEP + CHARACTERIZE ENGINE REQUIREMENT; ACCEPTED / COVERED**.

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
6. **Proven unusual requirements.** One narrow requirement is proven. For a server-local airborne `B_Heli_Light_01_F` on the tested clear Stratis corridor, a `doMove` approach followed by `land "LAND"` settled within 25 m only when one exact `Land_HelipadEmpty_F` existed at the destination. The matched no-pad arm reached the 120 m arrival radius but remained airborne beyond 104 m through the 90-second landing deadline.
7. **Accidental/fragile findings.** Vehicle config side was CIV even with a
   WEST crew; `ignore_en` was dropped by positional arguments; fallback pads
   used ASL z=0; landing passed after one touching/ready tick; repeated task
   assignment replaced active work; mission/end waits were unbounded; and a
   random repeated zero-radius waypoint call had no demonstrated purpose.
8. **Native alternatives.** The permanent A/B uses native `doMove` and `land` in both arms and changes only exact destination-pad presence. The no-pad alternative failed the declared settled-landing contract in three independent final runs, so the hidden pad remains justified for this bounded sequence. `landAt`, other landing modes, waypoint-only approaches and broader terrain remain untested alternatives.
9. **Stable contract.** The user-facing round trip, physical progress, valid
   settled landings, availability while waiting, correct home, duplicate
   rejection, bounded failure, locality and cleanup.
10. **Free implementation details.** Product waypoints, task-map keys, polling cadence, LZ search, radio calls and UI state remain free. The characterization freezes only the exact class/corridor/start/locality/`doMove` + `LAND`/90-second domain it proves; it does not require that all future transport implementations use that sequence.
11. **Characterization.** Accepted as `vigil-transport-pad-ab`. It retains the exact no-pad negative control, hidden-pad treatment, causal dimensions, continuous three-second settling oracle, spatial/deadline bounds, client completion, cleanup, and Evidence Contract proposition. Calibration failures caused by immobile ground-start fixtures were rejected, not used as engine evidence.
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

## Hidden-pad characterization closeout

`vigil-transport-pad-ab` is deliberately separate from the longer product
round-trip. Both server-owned aircraft begin airborne at `[2000,5200,50]`, use
the same class, crew setup, `doMove [2350,5200,0]`, `land "LAND"`, clear
terrain, weather, sampling and deadlines. The control verifies there is no
destination pad within 100 m; the treatment creates exactly one
`Land_HelipadEmpty_F`.

Final independent runs `20260824T165323Z-538afe85`,
`20260824T165824Z-11607833`, and corrected immutable-package run
`20260824T170322Z-9b970179` each passed 5/0 feature assertions on the server
and 1/0 on client-a (9/0 and 5/0 including smoke). Across the final runs,
no-pad controls traveled about 245–246 m, reached 104.1–105.0 m from the
destination, and remained airborne at the 90-second deadline. Hidden-pad
treatments traveled about 353–355 m, reached minimum sampled distances of
roughly 0.2–1.9 m, settled within 2.7–23.9 m, and held ground contact,
`unitReady`, sub-2 m/s speed, damage below 0.5, and continuous three-second
stability. Every aircraft, crew group and destination pad was deleted;
client-a received the replicated bounded-completion token.

The final Evidence Contract publishes three arms, one causal relationship and
one demonstrated proposition. Package `20260824T170322Z-9b970179` ingested
twice with stable scoped counts (5 packages, 5 runs, 59 assertions, 25
observations, 6 proofs and 9 judgments), and the Sacred Texts audit accepted.

## Abnormal terminal closeout

B5 extends the existing `vigil-transport` scenario without creating a second overlapping fixture contract. The client uses the real `YOSHI_taskTRN_submit` path for a second server-local `B_Heli_Light_01_F` on the same accepted clear corridor. The server retains the exact task ID, generation, aircraft, and product-created `Land_HelipadEmpty_F` after stage 3; client-a independently resolves those nonlocal identities while the aircraft is alive and airborne. Server-local `setDamage 1` then varies the terminal cause.

Accepted run `20260828T031206Z-24d79c61` passed 17 server and 8 client feature assertions (21 and 12 including smoke), zero failures, and complete cleanup. The exact aircraft `2:165` was destroyed airborne after task `T3.69663e+08` generation `706935` created pad `2:185`. That same generation finalized with state/status `failed` and stage 5, disabled its manager, deleted pad `2:185` on server and client, produced exactly one requester terminal row, and retired the aircraft, crew, home pad, product pad, and coordination state. The same run preserved the full normal outbound/wait/RTB contract.

The investigation exposed a product cleanup defect: the finalizer queried `deletePadOnFinish` through an invalid default-bearing `get` expression, so the exact product pad remained live after failure. The finalizer now uses `getOrDefault`, guarded statically and proven by the exact null transition. A later calibration exposed a test-only client/server teardown race after the client had already received the terminal row; a two-phase terminal/cleanup acknowledgement now preserves both receipt and null-transition evidence. Rejected calibrations remain unaccepted and were never ingested. Three runs also recorded intermittent normal-RTB low-altitude crashes on the unchanged accepted fixture; the final accepted run and three earlier calibrations completed normal RTB, and no speculative product or fixture change was made.

Evidence package `urn:tribunal:evidence-package:20260828T031206Z-24d79c61:1` has file SHA-256 `d71182836849bc8408a6949a1562532e17aa4e5500d788a354e8d7a1ff3f2bd4`. Production ingestion advanced once to 37 packages and 38 runs; the identical second pass was count-stable and the audit passed. Reviewed distillation classifies both propositions as project-specific and adds no generic Arma claim; its second pass was idempotent.

## Controls and deferred work

The first permanent negative control is duplicate dispatch while active. The
review also adds fail-closed missing/dead-crew validation and bounded timeouts.
Unsafe/unreachable terrain, cancellation, destruction before pad creation or during RTB, crew-only death, retry exhaustion, RTB before arrival, ownership migration, and client-B/JIP remain explicitly decision-bound, blocked, or optional. The representative in-flight destruction terminal is now covered and no further transport work belongs in the current MUST/SHOULD campaign.

The scoped Pontifex campaign has no remaining transport or other MUST/SHOULD candidate. Do not broaden this landing or destruction characterization to other classes, terrain, phases, approach commands, locality, or presentation without first reopening and reclassifying the applicable blocked/decision/optional boundary.
