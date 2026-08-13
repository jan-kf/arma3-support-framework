# Vigil rotary-wing CAS review

Review outcome: **REFINE BEFORE PERMANENT COVERAGE**.

## Behavioral contract

A client with a valid selected rotary CAS helicopter and operating area can
submit one bounded task. The correct aircraft physically departs its recorded
home, enters the requested region, identifies a valid hostile ground target,
and attacks it with a real available weapon. Authoritative evidence must
correlate aircraft, intended hostile, weapon/ammunition, fire, and physical
impact. Friendly, civilian/neutral, airborne, dead, and off-area objects are
not intentional targets. The aircraft remains active for the requested time,
then stops initiating attacks, physically returns to its recorded home, lands,
and becomes task-idle. An area with no target produces no fabricated attack;
an aircraft without crew or lethal ammunition fails closed; an active
duplicate request is rejected.

## Twelve-question review

1. **User observation.** Select an eligible armed friendly helicopter, choose
   an area/altitude/duration, dispatch it, observe transit, a real attack on a
   hostile ground target, bounded on-station time, disengagement, and landing
   at home.
2. **Current behavior and negative paths.** The client constructed a governor
   task. The server moved to a 1,000 m arrival region, then a global per-frame
   service asked local AI helicopters to engage sensor targets. The old task
   ended after its timer but did not execute a working return lifecycle. It
   accepted duplicate work and aircraft without usable combat capability.
3. **Machines and paths.** Selection/edit state and `YOSHI_taskCAS_submit` are
   client-local. YCD sends unique assignment to the dedicated server. The
   server owns aircraft, pilot group, target filtering, fire, governor, timer,
   world effects and return task. Public vehicle state and world effects
   replicate to clients.
4. **Generic mechanics.** Aircraft trajectory/locality/landing, Fired-event
   observation, projectile sampling, target HitPart/HandleDamage/Killed
   evidence, weapon/ammunition identity and cleanup are generic Tribunal
   mechanics.
5. **Product behavior.** Eligibility, request construction, operating-area
   boundary, hostile-ground filtering, weapon choice, active-window policy,
   duplicate/invalid rejection, task state and RTB are Vigil semantics.
6. **Proven unusual requirements.** A controlled A/B showed that rebooting the
   helicopter AI alone did not break its combat task; reboot followed by a new
   MOVE task did. That sequence is retained for RTB. No other AI workaround is
   characterized as required.
7. **Accidental/fragile findings.** Engagement was globally eligible rather
   than CAS-scoped; crewed vehicle `side` could report CIV; there was no area
   filter; guided weapons were the only explicit options; a successful fire
   command could be logged without a Fired event; `maxControlRange` incorrectly
   limited direct cannon fire to 350 m despite AI modes extending to 2,500 m;
   duplicate and invalid requests were not bounded; and RTB arguments/home
   state were incompatible with the shared transport handler.
8. **Native alternatives.** Native MOVE/LOITER and `fireAtTarget` are retained.
   A native SAD waypoint was experimentally unsafe: after attacking the area
   target, AI independently switched to an off-area hostile. Explicit,
   area-filtered targeting with BLUE/AWARE AI is therefore used. Broad SAD is
   rejected rather than characterized.
9. **Stable contract.** Correct request/aircraft/area, physical transit, valid
   hostile-only targeting, real appropriate fire plus attributable impact,
   bounded active time, no post-expiry fire, physical RTB/home, locality,
   controls and cleanup.
10. **Free implementation details.** Coordinates, aircraft/target classes,
    task-map keys, observer cadence, waypoint type, scan interval, exact
    weapon, sensor API and ledger representation may change with adapters.
11. **Characterization.** Only the combat-to-MOVE RTB reset has controlled A/B
    support. Sensor reveal, LOITER, fire controller ordering and fire-mode
    selection remain replaceable implementation details.
12. **Promoted Tribunal mechanics.** Product-neutral source Fired observation,
    exact source/weapon/ammo/projectile/locality records, trajectory samples,
    target HitPart/damage/kill evidence, and deterministic handler cleanup join
    the existing aviation trajectory/locality/landing observer.

## Architecture and lifecycle

Asset discovery accepts a friendly, unlocked helicopter with a living crew and
lethal ammunition. The client records grid, altitude, and minutes on station,
then crosses a server-once assignment boundary. The server records ATL home,
validates crew/ammunition, rejects active duplicates, publishes task/area state,
and gives the aircraft a MOVE task. Within the arrival radius it publishes
`on_station`, enables CAS engagement, places the group in BLUE/AWARE, and uses
a LOITER waypoint solely for area flight.

The server-only engagement service ignores every aircraft without
`YSF_cas_active`. It derives effective side from a man/group commander and then
vehicle config for uncrewed targets; accepts only live hostile ground objects
inside the declared circle; and chooses available weapons inside their actual
configured envelope. Direct bullets use CfgWeapons AI fire-mode ranges, not
guidance `maxControlRange`. Guided options retain their existing handling.
Before `fireAtTarget`, the controller receives knowledge and the exact target.
Only the matching Fired event creates a durable ledger entry and cooldown.

The authoritative timer begins on arrival. Expiry disables engagement before
hard-stop/reboot, then assigns shared transport RTB to the recorded ATL home.
The transport completion callback publishes CAS `home`. Failure/cancellation
removes the killed handler and never starts a success RTB. A 300-second task
deadline prevents indefinite dispatch/on-station waits.

## Implementation-quality classification

| Subsystem | Classification | Resolution |
| --- | --- | --- |
| UI state and server-once handoff | KEEP AS-IS AND SPEC-TEST | real client request retained |
| vehicle-side resolution | REFINE BEFORE PERMANENT COVERAGE | commander/config effective side |
| global engagement eligibility | REFINE BEFORE PERMANENT COVERAGE | require active CAS state |
| target discovery/filtering | REFINE BEFORE PERMANENT COVERAGE | hostile ground + declared area + alive |
| sensor/reveal dependency | NEEDS EXPERIMENTATION | used but not frozen as contract |
| SAD combat waypoint | REWRITE BEFORE PERMANENT COVERAGE | safe LOITER plus explicit targets |
| gun/guided weapon selection | REFINE BEFORE PERMANENT COVERAGE | ammunition and real config envelopes |
| Fired/target evidence | REFINE BEFORE PERMANENT COVERAGE | ledger created only from matching Fired |
| timer authority | KEEP AS-IS AND SPEC-TEST | server time, bounded deadline |
| duplicate/invalid work | REFINE BEFORE PERMANENT COVERAGE | reject duplicate, crew, lethal-ammo failures |
| combat disengagement/RTB | REFINE BEFORE PERMANENT COVERAGE | proven reboot + MOVE through transport RTB |
| cancellation/death | KEEP AS-IS AND SPEC-TEST | explicit terminal states and handler cleanup |
| fixed-wing and loadout swaps | DEFER | outside this rotary milestone |

## Live characterization and controls

Live runs `20260813T170401Z-ac3cb08a` through
`20260813T181715Z-59d6c035` used clear Stratis terrain, server-local aircraft,
targets and AI, and the real authenticated client request path. Baseline
experiments proved an idle armed helicopter could attack without a CAS task,
vehicle-side CIV misclassification, no-ammunition acceptance, and a failed RTB.
A controlled combat reset showed reboot alone did not move the aircraft, while
reboot plus reissued MOVE returned it physically.

A broad SAD run attacked the requested hostile and then selected a separate
hostile 1.4 km outside the area. Under BLUE/AWARE, explicit `fireAtTarget`
produced real cannon fire and impact without that switch. Weapon inspection
showed `ACE_gatling_20mm_Comanche` AI modes with maximum ranges 400, 1,000,
1,800, and 2,500 m; using its 350 m projectile control range had incorrectly
forced DAGR selection. With the corrected envelope, the server-local aircraft
fired `ACE_20mm_HE`, its ledger named the exact hostile, ammunition decreased,
and a stationary tank emitted HitPart. Friendly at +300 m, civilian at -300 m,
and hostile at +1,400 m were neither ledger targets nor physically hit.

The target is fueled off and fully simulated. An ordinary active tank crew
returned fire and destroyed the helicopter after a valid CAS hit, which tests
anti-air survival rather than CAS correctness; an uncrewed tank was selectable
through config-side fallback but produced unreliable cannon solutions. The
calibrated target therefore has the minimum EAST crew needed for native target
acquisition with every crew AI subsystem disabled. This removes unrelated
return fire without disabling vehicle collision, damage, targeting or physics.

The no-target repeat uses the same aircraft after physical home completion,
removes hostile targets, re-dispatches through the client API, waits for its
short active timer and second RTB, and requires no new Fired or ledger entries.
The no-ammunition control uses a separately crewed attack helicopter with zero
ammunition and requires authoritative `failed`, inactive state. Duplicate work
must preserve the original task ID.

## False-PASS and network analysis

The scenario cannot pass from a task-state label, unrelated target death,
wrong shooter, stale prior fire, a missile/cannon miss, timer-only return,
temporary homeward travel, or control-target collateral. Each observer window
is tokenized and records server-local ownership. The attack requires matching
aircraft fire, an appropriate configured weapon/ammo, ammunition decrement,
the product ledger's exact aircraft/hostile pair, and HitPart on that hostile.
Controls require no targeting ledger, no HitPart, and zero damage. Return
requires a sampled physical trajectory, approach, landing, settling and home
state; cleanup requires an idle manager and deleted fixtures.

Delayed replication can postpone client-visible state, but authoritative
selection/fire/timer effects run once on the server. The unique server-once
request and active-task rejection guard duplicate delivery. Future client-b
coverage should prove its UI buffer remains independent while both clients
observe the same aircraft/combat state. Poor-network profiles and fixed-wing
weapons are deferred rather than inferred from this local private-network run.
