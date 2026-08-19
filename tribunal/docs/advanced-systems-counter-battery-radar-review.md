# Advanced Systems Counter Battery Radar review

Primary review outcome: **REFINE BEFORE PERMANENT COVERAGE**.

## Behavioral contract

While Counter Battery Radar is enabled, artillery fire is detected on the
machine that owns each shell and reported to the dedicated server. The server
maintains, for each group of predicted impacts, a red impact zone and a warning
icon carrying the shell count and remaining time-to-impact; the drawn zone sits
on the ground area the shells will actually strike. Repeated fire from the same
launcher narrows an origin estimate around that launcher until it is promoted to
a confirmed fix at the firing position. The first launch of a cycle plays a
launch-detected radio warning to living players of other sides within the
warning radius, and to nobody else. Predicted impacts expire and their markers
disappear once the threat has landed; stopping the system removes every marker
and resets all state; while the system is disabled the same fire produces
nothing at all.

This review covers detection, impact prediction, clustering, zone/icon markers,
origin estimation and confirmation, the side-filtered launch warning, expiry,
enable/disable lifecycle, marker replication to one authenticated client, and
locality. It does not claim coverage of the Eden module or Zeus toggle entry
points, marker sharing policy, multi-launcher or multi-cluster arbitration,
client-b, disconnect/reconnect, or JIP.

## Canonical review questions

### 1. What should the user or integrator observe?

The shipped Eden module, Zeus toggle, red zone/warning-icon markers, orange
origin estimate, `mil_triangle` confirmed fix, and the registered
`YAS_CBR_WarningLaunchDetected` radio entry establish a coherent intent: a
mission-maker enables the system and defenders then see where incoming fire will
land, how soon, and roughly where it came from, plus an audible launch warning.
The module description ("Placing this module will trigger the CBR code") is thin,
but the marker, radio and origin implementations are specific enough to
establish the product outcome without inventing it.

### 2. What did the feature actually do before review?

The positive path worked end to end. A controlled Live salvo produced one
cluster growing from 1 to 6 members, a `ColorRed` `ELLIPSE` zone whose radius
tracked the member spread, a `mil_warning` icon reading `6 shells | ETA 20-29s`,
an origin estimate narrowing 1000 → 500 → 250 → 125 → 62.5 → 31.25 m, correct
expiry of clusters and markers after impact, and clean reset on stop.

One defect was material. `YOSHI_predictFallTimeAndPos` integrated the
projectile forward under gravity until it fell below **ASL 0** — sea level —
rather than the ground beneath the projected point. Every target above the
waterline therefore produced an impact estimate biased downrange. Negative paths
were sound: the disabled guard suppressed everything, the handler ignored
non-local shells, and the warning excluded the firing side and out-of-radius
players.

### 3. Which machines and lifecycle stages own the behavior?

Detection is owner-local: the `ArtilleryShellFired` mission event handler is
registered at preInit on every machine and exits unless the shell is `local`.
That machine assigns the shell a `clientOwner`-scoped uid, then sends launch
notification and periodic track updates to the server with
`remoteExecCall [..., 2]`. The dedicated server exclusively owns the queue,
clusters, prediction consumption, origin table, every marker, the manager
threads and the enable flag, which is published with `publicVariable` so clients
observe it. Markers are created with the global `createMarker`, so client-a sees
them without any client-side CBR state. This is one authenticated client's
replication boundary only; client-b and JIP remain unproven.

### 4. Which mechanics are generic?

Native artillery firing, `ArtilleryShellFired`, projectile trajectory and
terminal position, terrain height sampling, marker existence and properties,
locality and radio delivery are engine or framework concerns. Tribunal already
owned artillery fire/trajectory observation; it did not own marker evidence, so
a narrow product-neutral marker observer was added.

### 5. Which behavior is product-owned?

Advanced Systems owns the link distance and leeway that group predictions into
one zone, the centre-update hysteresis, the marker styling and text, the
1000 m warning radius, the once-per-cycle warning rule, the initial origin
radius, the halving law, the confirmation threshold, the forget/fade timings,
and the enable/disable lifecycle. Undecided product questions are listed under
[Product decisions required](#product-decisions-required).

### 6. Are unusual engine requirements proven?

No engine workaround is claimed or characterized. Two engine facts were measured
and retained as fixture knowledge rather than frozen contract:
`ArtilleryShellFired` fires for artillery-computer shells and supplies the aim
point, and `getArtilleryETA` returned 27.02 s against a 27.07 s real flight, so
the engine's own solution is essentially exact.

One suspected defect was **disproved** by controlled probe and deliberately left
alone: `YOSHI_fnc_originTick` deletes entries from `YOSHI_originTrack` while
iterating it with `forEach`. Five expired entries were removed in a single pass
on this build, so the pattern is not skipping entries and was not "fixed".

### 7. Which details were accidental, fragile, or incomplete?

The sea-level impact solution was a genuine defect and was refined. The
integration loop was also unbounded, which is a fail-closed hazard on the server;
it now carries an explicit time cap. `YOSHI_CB_nextUid` is written and reset but
never read, and `YOSHI_CBR_EH_ID` is stored but never consumed; both are recorded
as replaceable dead state rather than deleted, because neither is load-bearing
and removing them buys nothing. Cluster tuple layout, uid format, marker names
and index counters, polling cadence and the decentred-circle randomisation
remain evidence adapters.

### 8. Was a better existing mechanism available?

Yes for accuracy, and it was adopted in the narrowest form. A one-variable A/B
held the launcher, target, magazine and shell fixed and compared the shipped
sea-level termination with a terrain-aware termination on the same live
projectile:

| Target | Terrain ASL | Sea-level error | Terrain-aware error | Sea-level ETA error | Terrain-aware ETA error |
| --- | --- | --- | --- | --- | --- |
| `[4000,3500]` | 219.44 m | 46.65 m | **2.15 m** | +1.95 s | −0.05 s |
| `[3000,2000]` | 167.19 m | 53.76 m | **6.06 m** | +1.08 s | +0.08 s |
| `[2200,5600]` | 6.14 m | 17.92 m | 17.92 m | +0.26 s | +0.26 s |

The terrain-aware solution is dramatically better above the waterline and
**identical** at sea level, so it carries no regression. The residual ~18 m at
sea level is unmodelled air friction, which is inside the 100 m leeway and was
deliberately not chased.

`_targetPosition` from the fire event and `getArtilleryETA` are both more exact
still, but adopting either would replace tracking-based prediction with the
attacker's own aim point and discard the radar character of the feature. That is
a product redesign, not a defect fix, so the mechanism was left free and only the
proven bug corrected. `getTerrainHeightASL` costs ~5 µs per call, about 2 ms per
prediction, which is acceptable at the 0.5 s per-shell cadence.

### 9. What is the stable contract and causal proof?

The permanent scenario correlates one run token, one launcher, eight tracked
shells and their real terminal positions. Each shell's predicted impact is
compared with **that same shell's** terminal position, so the accuracy claim is
dispersion-free and each shell is its own control. The launch and trajectory
oracle is Tribunal's artillery observer; the per-shell terminal-position poll
that pairs a prediction to its own projectile is scenario-local, and this review
previously described that poll as Tribunal-owned in error. The drawn zone centre
is separately compared with the real impact centroid. Marker identity, shape,
colour, type and label are captured while the zone is live.

The label's numbers are checked against an independent physical oracle rather
than against the state that produced them. An earlier revision compared the drawn
text with the cluster's own count and ETA fields, which proves only that the
product formats its own state consistently. The scenario now records the instant
the peak label was read, then recovers from Tribunal's observed projectiles
which shells were genuinely in the air at that instant and how much flight each
had left, measured from its own terminal timestamp:

* **count** is asserted as a range between the shells that were definitely
  airborne and those that could still have been, using a 1.5 s boundary band. A
  shell can be counted slightly before its first track update reaches the server,
  and a landed shell lingers about a second until its member entry expires, so an
  exact equality would be a race rather than a contract;
* **remaining time** compares the displayed ETA minimum and maximum against the
  minimum and maximum of those independently derived remaining lifetimes;
* the exact projectile identities behind the derived count are retained in the
  assertion evidence.

The ETA tolerance is **asymmetric**, because the error has a direction. A
displayed ETA is computed from a track update up to 0.5 s old, is rounded up to
whole seconds, and is read by a 0.25 s poll, so it legitimately runs *ahead* of
the truth; under load the product's per-shell update spawns lag further still,
and a measured run showed +2.45 s. Over-reporting is therefore allowed **4 s**.
Nothing makes a displayed ETA legitimately *shorter* than the real remaining
flight except rounding and the ~0.13 s prediction error, so under-reporting is
held to **1.5 s**. Both bounds sit far below the ~27 s flight they describe. The
prediction defect itself is guarded by the 20 m position bound in
`cbr.prediction.impactAccuracy`, not by this label check.

Shell identity is the observer's own event index paired with the projectile
class, not `netId`: a shell is not a network object, so `netId` reports `0:0`
for every one of them, which an earlier revision of this oracle recorded as
useless evidence.

Label replication is asserted on the client too: the authoritative peak count is
published and the client must observe an icon whose text carries that exact count
and the product's countdown format. The countdown digits themselves are not
matched, because they change on every product tick while the client samples at a
fixed interval; requiring a specific transient string would be a race. Origin radii are sampled across
the whole engagement and the confirmed fix is required to be a `mil_triangle`
within 5 m of the actual gun.

Every warning claim travels the real pipeline — native launch,
`ArtilleryShellFired`, the product handler, emission, client receipt — and the
scenario never invokes the warning helper directly:

* **positive:** a real hostile three-shell salvo landing 100–1000 m from the
  declared observer delivers **exactly one** warning, which also proves the
  once-per-airborne-cycle rule;
* **out-of-radius control:** the elevated accuracy salvo is real hostile
  artillery kilometres away and must deliver nothing;
* **same-side control:** a real friendly salvo onto the same impact point must
  deliver nothing.

Because a warning is emitted only for the first shell of an airborne cycle, each
phase asserts that the tracker was genuinely idle beforehand; otherwise a control
would pass for the wrong reason. The client correlates the exact authoritative
zone and icon names, position, shape, colour and size published by the server,
rather than accepting any two markers sharing the product prefix, and separately
requires the origin marker to replicate.

Assertion strength was verified rather than assumed: run against the
**un-refined** build the accuracy assertion failed with a worst error of
45.35 m (per-shell 44.73–45.35 m, a systematic bias) against its 20 m bound.

### 10. Which implementation details remain free to change?

Cluster array layout, member tuple shape, uid format, marker naming and index
counters, link distance, leeway, hysteresis, manager sleep cadence, the
prediction step size and integration method, fade timings, the decentred-circle
randomisation, and the private function names may all change. The promised
behavior is: detection while enabled, an accurate drawn impact zone with count
and time-to-impact, a narrowing then confirmed origin, a side-filtered launch
warning, expiry, replication, and complete removal on stop.

### 11. Which mechanisms deserve characterization?

None. The corrected impact solution is a defect fix with an A/B record, not an
engine requirement, and the contract stays mechanism-neutral. The disproved
hashmap-iteration concern is recorded as evidence, not frozen. No current CBR
mechanism has been shown engine-imposed.

### 12. Which mechanics should be promoted into Tribunal?

One: a product-neutral marker observer (`tribunal/mission/markers.py`) providing
a single marker's property record, a prefix-scoped census, a census diff, a
bounded observation loop with a caller-supplied terminal predicate, and derived
appear/peak/clear lifecycle evidence. It has a concrete first consumer, plausible
reuse by any mod that draws markers, and no product semantics: the observed
prefix and its meaning belong to the calling scenario. Zone meaning, origin
meaning, warning correctness and lifecycle expectations stay in the Advanced
Systems scenario. Production code gains no Tribunal dependency.

## Classification and permanent coverage

| Subsystem | Classification | Resolution |
| --- | --- | --- |
| detection and owner-local tracking | KEEP AS-IS AND SPEC-TEST | `local`-scoped handler, server-authoritative track updates |
| impact prediction | REFINE BEFORE PERMANENT COVERAGE | terrain-aware termination plus a bounded integration loop, proven by A/B |
| clustering, zone and icon markers | KEEP AS-IS AND SPEC-TEST | live-captured identity, shape, colour, type, count and ETA text |
| origin estimation and confirmation | KEEP AS-IS AND SPEC-TEST | narrowing radii and a confirmed `mil_triangle` at the real gun position |
| side-filtered launch warning | KEEP AS-IS AND SPEC-TEST | delivery to client-a with same-side and out-of-radius controls |
| expiry and enable/disable lifecycle | KEEP AS-IS AND SPEC-TEST | disabled control, zone removal after impact, full reset on stop |
| origin hashmap iteration | KEEP AS-IS AND SPEC-TEST | suspected defect disproved by controlled probe; left unchanged |
| dead uid/handler-id state | replaceable | recorded, not deleted; not load-bearing |
| marker sharing policy | DEFER | product decision; see below |
| Eden module and Zeus toggle entry | REVIEWED / REFINE BEFORE COVERAGE | configured handlers are reachable, but real framework dispatch/locality and curator authority are unproven; see `advanced-systems-cbr-module-review.md` |
| multi-launcher/multi-cluster arbitration | NOT YET REVIEWED | excluded from the first contract |
| client-b, JIP, disconnect | DEFER | a one-client run must not overclaim these boundaries |

The permanent `advsys-counter-battery-radar` Tier 3 scenario is a specification
test owned beside Advanced Systems. It retains the primary review outcome in
`ScenarioReview`: coverage became admissible only after the impact solution was
corrected.

## Product decisions required

These are recorded rather than invented, and no test asserts a preferred answer:

1. **Marker sharing policy.** Zone and origin markers are created globally, so
   every player on every side sees them, including the side that fired. The
   radio warning is explicitly side-filtered. Live Mode confirmed a WEST client
   observing the EAST launcher's own origin estimate. Whether CBR output should
   be side-scoped (or scoped to a radar asset) is undecided; in a single-side
   cooperative mission the current behavior is harmless.
2. **Confirmed-origin persistence.** A confirmed fix is deliberately named
   `permanent` and is skipped by expiry, so it survives until the system is
   stopped. Whether it should decay is undecided.
3. **Warning coverage.** Exactly one warning is emitted per firing machine per
   airborne cycle, positioned on the first round only, at a fixed 1000 m radius.
   Whether a walking barrage should re-warn is undecided.

## Corrective review after independent audit

An independent audit of the first coverage attempt raised four blocking
findings. All four were verified against the repository and runtime and all four
were correct.

**The disabled control could pass without a shot.** It fired one round, waited,
and asserted only that no detection state appeared. Had the gun failed to fire —
no ammunition, out of range, dead crew — every assertion would still have passed.
The control now proves the shell through Tribunal's observer before CBR's silence
is allowed to mean anything: one `Fired` event from the expected source and
magazine, an `ArtilleryShellFired` correlation, a sampled trajectory, termination,
and an impact within 250 m of the aim point. Silence is asserted as
`_disabledOk = _controlShotOk && ...`, so the shot evidence gates the control.

**Warning coverage bypassed the real pipeline.** The scenario invoked
`YOSHI_fnc_cbrWarnSidePlayers` directly, which proved the helper's side and
radius filtering but never proved launch → `ArtilleryShellFired` → product
handler → emission → client receipt. The helper is no longer invoked anywhere in
the scenario. The positive is a real hostile three-shell salvo inside the radius;
the out-of-radius control is a real hostile salvo placed at runtime to be
unambiguously outside it; the same-side control is a real friendly salvo onto the
same impact point. The three-shell positive also proves the once-per-airborne-cycle
rule, which was previously unproven. Emission and receipt are recorded separately —
a transparent recorder on the server captures what the product decided to warn
about and who qualified, and the client records receipt — so a future failure
localises to one side instead of being ambiguous.

**The live-command guards were wrong for generic SQF.** Scanning raw text for
`//` and `/*` rejected valid string literals such as a URL or a quoted `/*`, and
the size check ran before the client relay wrapper and quote doubling, so a
compliant source could still deliver an oversized, silently truncated payload.
Comment detection now blanks string literals first (handling both delimiters and
doubled-quote escapes) and the size check measures the delivered payload. A
17,012-byte client source that previously passed is now correctly rejected at
26,340 delivered bytes.

**Gameplay-tier documentation misstated the evidence.** Corrected in full above.

Two further defects were found in the scenario itself during remediation, both
of which had produced misleading results:

* **A boundary-distance control.** The elevated accuracy target doubled as the
  out-of-radius warning control, but at ~999 m from the focused-run observer it
  sat exactly on the 1000 m warning radius. The tier mission derives the player's
  x-coordinate from the run token, so the control silently flipped between inside
  and outside across runs. The elevated target is now chosen at runtime from
  high-terrain candidates by maximum separation from the declared observer, and
  the emission record makes the separation explicit.
* **A salvo-overlap race.** Each warning phase must begin from an idle tracker,
  because only the first shell of an airborne cycle warns. The idle check
  accepted the transient gap *between rounds of a still-firing salvo*, so the
  preceding volley sometimes still owned the cycle and the salvo under test
  produced no warning at all. Recorded handler decisions showed the two guns
  interleaved, with `first=true` going to whichever won the race. The confirm
  volley is now drained to termination through its own observer, and idle
  requires stable emptiness rather than an instantaneous sample.

Neither was a product defect; both were defects in the coverage, and both would
have produced an intermittently green scenario.

A third source of nondeterminism was observed and is recorded honestly rather
than claimed solved: on one run the near-warning gun fired zero rounds, with the
same class, position and target that fired normally on the run before and after.
Two speculative fixture changes were tried to suppress it and both were reverted
because they made matters worse: disabling the crew's `TARGET`/`AUTOTARGET`/`FSM`
AI stops an AI gunner accepting `doArtilleryFire` at all, and even a milder
`CARELESS`/`BLUE`/captive variant broke the tracked salvo. Requiring flat ground
outright left phases unplaced and silently skipped, so terrain flatness is now
*preferred* and progressively relaxed instead of required. The fixture is back to
simply arming the gun. The scenario now records `warnGunState` — gun identity,
crew presence, artillery ammunition, damage, position, range and
`inRangeOfArtillery` — captured immediately before firing, so if this recurs the
run diagnoses itself rather than requiring another investigation from scratch.

## False-PASS controls and evidence

The scenario fails closed on: a zone that never appears; markers read after
cleanup has already removed them; internal cluster state without drawn markers;
a drawn zone whose centre does not match the real impact centroid; predicted
impacts agreeing only with other internal state; fewer tracked shells than
rounds fired; an origin estimate that never narrows or never confirms; a
confirmed marker away from the real gun; a warning delivered to the firing side
or beyond the radius; a second warning counted from a control; detection while
the system is disabled; surviving markers or clusters after stop; and any
unbounded wait. Every wait has an explicit deadline.

Structural false-PASS risks found and closed during Live calibration and the
corrective review:

* marker type and text were read at assertion time, after the zone had already
  been pruned, reporting an empty type; they are now captured while it is live;
* the disabled-path control consumed a round, so the tracked salvo silently
  fired seven of eight shells; the magazine is restored before the salvo;
* a sea-level-only target cannot distinguish the two impact solutions, so the
  scenario asserts its target is above 100 m ASL;
* the disabled control asserted absence without proving the stimulus occurred;
* the warning positive and controls exercised the helper rather than the pipeline;
* the out-of-radius control sat on the radius boundary and flipped between runs;
* the idle precondition accepted a transient gap inside a firing salvo, which
  could make a warning phase vacuous rather than causal.

The last four are the ones that matter most for method: a negative control is
only meaningful if the stimulus it withholds a response to is independently
proven to have happened, and a precondition sampled instantaneously is not a
precondition at all.

## Fresh autonomous proof

Cold run `20260817T200638Z-36fa1d1b` passed 29/29 assertions with zero failures
and complete container/network/state cleanup. Its token was
`gameplay-20260817T200638Z-36fa1d1b-998157d0b56a`; mission SHA-256 was
`c113c3e8ba8b443223568f99c4060a2dfa699cc34eae68dbacae1af46fb4e5a0` and PBO
SHA-256 was
`8dfcfc731d8a941fd1b6bc06f0ef0790da743111f5979237ebc11e2f5688a1a2`
with a valid deterministic footer.

The label read `8 shells | ETA 14-27s` at `peakAt=106.229`. Seven projectiles
were definitely airborne at that instant and an eighth was inside the boundary
band, so the shown count of 8 sits in the required `[7, 8]` range. Each
definitely-airborne shell contributed its own launch time, terminal timestamp
and derived remaining flight:

| Shell | Launched | Impacted | Remaining at label |
| --- | --- | --- | --- |
| `0 Sh_82mm_AMOS` | 93.066 | 119.959 | 13.73 s |
| `1 Sh_82mm_AMOS` | 94.858 | 121.746 | 15.52 s |
| `2 Sh_82mm_AMOS` | 96.667 | 123.561 | 17.33 s |
| `3 Sh_82mm_AMOS` | 98.477 | 125.353 | 19.12 s |
| `4 Sh_82mm_AMOS` | 100.292 | 127.162 | 20.93 s |
| `5 Sh_82mm_AMOS` | 102.100 | 129.013 | 22.78 s |
| `6 Sh_82mm_AMOS` | 103.912 | 130.782 | 24.55 s |

The independently derived remaining-time range is therefore 13.73-24.55 s
against a displayed 14-27 s: deltas of +0.27 s and +2.45 s, both in the expected
over-reporting direction and inside the +4/-1.5 s bounds.

The disabled-path control fired a real shell, sampled its trajectory, terminated
and impacted near its aim point while producing no cluster, marker or origin
track. Per-shell impact errors and the four real warning emissions (one naming
the observer, the distant and friendly controls naming nobody) were as recorded
below. Client-a observed the authoritative zone and icon, the origin marker, and
an icon label carrying the exact authoritative count of 8 in the product's
countdown format.

Repeatability was demonstrated by an immediately following identical cold run of
the same revision, `20260817T201712Z-4bf8932a`, token
`gameplay-20260817T201712Z-4bf8932a-b3178fc22722`, which also passed 29/29 with
zero failures. Its label read `15-27 s` against an independently derived
`14.15-24.96 s`, deltas of +0.85 s and +2.04 s: the same over-reporting direction
and the same order of magnitude, which is what a stale-and-rounded countdown
should look like. Two earlier consecutive runs of the preceding revision,
`20260816T212035Z-f6d0d968` and `20260816T212927Z-d80fe834`, likewise both passed
29/29. Repeated execution within a single retained session is still not
demonstrated; the `cbr.cleanup` assertion proves the scenario leaves no fixtures,
markers or scenario state behind, which is the property a repeat run would depend
on.

## Harness findings

Developer Live Mode delivers snippets through the extension and executes them
with `call compile`, which does **not** run the preprocessor: `//` and `/* */`
comments are syntax errors, which previously surfaced as a confusing "Invalid
number in expression" at the comment. Snippets also return through Arma's
`callExtension` output buffer; 20000 bytes round-trips and 24000 truncates
silently, producing an equally confusing "Missing }". `write_live_command` now
rejects both cases with an explicit message. Mission `.sqf` files are
preprocessed normally, so scenario SQF is unaffected.

## What the composed gameplay tier does and does not prove

The `tier` subcommand that `./pontifex test gameplay` dispatches to defaults to
**360 s** (`PONTIFEX_TIER_TIMEOUT`). The 720 s default belongs to the separate
`test` and `e2e` subcommands. An earlier revision of this review misread the
latter and stated 360 s as 720 s; that is corrected here.

A `FAIL (timeout)` run proves nothing on its own. Assertions stop arriving at the
deadline, so "no failure among the assertions that were emitted" is not evidence
that a scenario passed. Two runs during this review were misread that way and are
retracted:

* `20260816T151957Z-c7e7de23` — composed tier at the 360 s default, 94
  assertions, `FAIL (timeout)`, one `vigil.cas.attack.effect` failure.
* `20260816T152724Z-342d0e5b` — `vigil-cas` alone at the 360 s default, `FAIL
  (timeout)`, missing `cleanup`, `noAmmo` and `noTarget`. This was previously
  cited as a standalone pass and as evidence that rotary CAS was a pre-existing
  over-budget scenario last completing on 2026-08-13. That conclusion was wrong.

An independent composed run at an explicit 720 s, `20260816T164010Z-79113df4`,
settles it: all 17 CBR assertions passed, and **rotary CAS completed in full**,
including `vigil.cas.attack.effect` with real `HitPart`, plus `noTarget`,
`noAmmo` and `cleanup`. So CAS is neither broken nor chronically over budget; the
360 s runs simply had insufficient time.

That run still terminated as `FAIL (timeout)` after 142 assertions, with genuine
failures in `vigil.fixedWing.strike.ir.guidance`,
`vigil.fixedWing.strike.ir.effect` and `vigil.logistics.request.accepted`. The
logistics failure carried destination `[6910,2770,0]` rather than the server
fixture's expected destination, which suggests sequential UI/state leakage
between composed scenarios. Those are real, unrelated to Counter Battery Radar,
and are recorded as independent follow-up work; they are not to be resolved by
raising timeouts.

The honest current position is therefore: **the composed tier has never been run
to completion**, so it proves nothing about scenarios after the point it stops.
Per-scenario `--select` runs remain the acceptance method, as they have been for
every milestone in this repository.

## Security and compatibility

The refinement adds no capability, dependency, network path or content
requirement: it replaces one loop termination condition and adds a time bound.
The scenario requires no VNC actor and no framebuffer evidence. Nothing changes
AppArmor, seccomp, capabilities, no-new-privileges, Steam/CEF confinement, or
VNC publication.

## Appendix: retained A/B and pre-refinement evidence

Run artifacts live under the git-ignored `runs/` tree, so the raw measurements
behind the two central claims are retained verbatim here. Both were produced in
Live session `20260816T143021Z-8b039b18` against the pre-refinement build.

The A/B computed both solutions on the *same* live projectile — the shipped
sea-level termination and a candidate terrain-aware termination — and compared
each against that projectile's own observed impact:

```text
CBRAB|target|[4000,3500,0]|terrainH=219.44|nativeETA=27.0243
CBRAB|shell|actual=[4005.54,3504.75,221.58]|flight=27.045
  |CURRENT pos=[4038.79,3472.03,-11.9968] eta=29 err=46.6498 etaErr=1.95496
  |TERRAIN pos=[4007.05,3503.22,219.807] eta=27 err=2.15144 etaErr=-0.0450439
CBRAB|target|[3000,2000,0]|terrainH=167.19|nativeETA=38.8904
CBRAB|shell|actual=[3000.42,2000.18,167.174]|flight=38.915
  |CURRENT pos=[2987.47,1948,-16.0723] eta=40 err=53.7629 etaErr=1.08496
  |TERRAIN pos=[2999.03,1994.28,158.438] eta=39 err=6.06433 etaErr=0.0849609
CBRAB|target|[2200,5600,0]|terrainH=6.14|nativeETA=21.7405
CBRAB|shell|actual=[2190.43,5603.68,9.14028]|flight=21.741
  |CURRENT pos=[2179.22,5617.66,-3.84399] eta=22 err=17.9232 etaErr=0.259033
  |TERRAIN pos=[2179.22,5617.66,-3.84399] eta=22 err=17.9232 etaErr=0.259033
```

The negative `CURRENT` z values are the sea-level termination made visible. The
sea-level case is byte-identical between the two solutions, which is why the
correction carries no regression there.

The permanent scenario's accuracy assertion was then run against that same
pre-refinement build to confirm the bound has teeth rather than merely being
satisfied:

```text
CBRCAL|cbr.prediction.impactAccuracy|FAIL|samples=7|worstMetres=45.351
  |worstEtaSeconds=1.93994|targetHeightASL=219.44
  |errors=[45.3051,44.7344,44.731,45.1227,45.351,44.8193,44.9811]
```

The tight 44.73–45.35 m spread is the systematic bias, not dispersion. To
reproduce, revert `YOSHI_predictFallTimeAndPos` to its sea-level termination and
re-run the scenario; the assertion fails at ~45 m against its 20 m bound.

## Next review

Field Utilities Fabricator and Virtual Storage, excluding the covered fixed-wing
airdrop path. CBR's Eden/Zeus module entry points, marker sharing policy and
multi-launcher arbitration remain separate follow-ups rather than silent
expansions of this contract.
