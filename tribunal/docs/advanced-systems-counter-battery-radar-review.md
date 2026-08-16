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
compared with **that same shell's** engine-observed terminal position, so the
accuracy claim is dispersion-free and each shell is its own control. The drawn
zone centre is separately compared with the real impact centroid. Marker
identity, shape, colour, type and text are captured while the zone is live.
Origin radii are sampled across the whole engagement and the confirmed fix is
required to be a `mil_triangle` within 5 m of the actual gun. The warning is
proven by delivery to client-a's radio playback path with a same-side control
and an out-of-radius control that must add no further warning.

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
| Eden module and Zeus toggle entry | NOT YET REVIEWED | scenario calls the API directly, as other suite scenarios do |
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

Two structural false-PASS risks were found and closed during Live calibration.
Marker type and text were originally read at assertion time, after the zone had
already been pruned, which reported an empty type; they are now captured while
the zone is live. The disabled-path control consumed a round from the magazine,
so the tracked salvo silently fired seven of eight shells; the magazine is now
restored before the tracked salvo. A sea-level-only target would have been a
third false PASS, since it cannot distinguish the two impact solutions, so the
scenario asserts its target is above 100 m ASL.

## Fresh autonomous proof

Cold run `20260816T153345Z-cb3ff3cb` passed 16/16 server and 9/9 client
assertions with zero failures and complete container/network/state cleanup. Its
token was `gameplay-20260816T153345Z-cb3ff3cb-1582c1ac41b1`; mission SHA-256 was
`af29252e89fd36234bc13ae25e6df6a78f278efa2671876d171b37736f0d1f65` and PBO
SHA-256 was
`01b37c01c5c19ce48f71eb756897482305a48c937178bc4a5f966862836d96f2`
with a valid deterministic footer.

All eight tracked shells correlated to `Fired` and produced per-shell impact
errors of 2.12, 3.04, 3.87, 3.90, 4.17, 4.30, 4.38 and 4.54 m against a 219.44 m
target, with a worst ETA error of 0.095 s. The same assertion run against the
pre-refinement build failed at 44.73–45.35 m, so the bound is meaningful rather
than merely satisfied. The drawn zone `YOSHI_cb_zone_0` was a `ColorRed`
`ELLIPSE` of 121.00 m radius centred 3.98 m from the real impact centroid, and
its icon read `8 shells | ETA 15-27s`. The origin estimate narrowed
1000 → 500 → 250 → 125 → 62.5 → 31.25 → 15.625 → 7.8125 m and was promoted to
`YOSHI_origin_confirm_1`, a `mil_triangle` at `[3500.39, 4000.54]` against a real
gun position of `[3500.38, 4000.55]`. Both zone markers were observed being
removed on expiry, client-a observed the replicated zone across 45 samples,
received exactly one launch warning, and gained no further warning from either
the same-side or out-of-radius control.

An earlier equivalent cold run, `20260816T151550Z-33b28dbe`, passed the same
16/16 and 9/9 before a line-ending normalisation in the edited source was
reverted; the run above is the authoritative proof of the committed bytes.

## Harness findings

Developer Live Mode delivers snippets through the extension and executes them
with `call compile`, which does **not** run the preprocessor: `//` and `/* */`
comments are syntax errors, which previously surfaced as a confusing "Invalid
number in expression" at the comment. Snippets also return through Arma's
`callExtension` output buffer; 20000 bytes round-trips and 24000 truncates
silently, producing an equally confusing "Missing }". `write_live_command` now
rejects both cases with an explicit message. Mission `.sqf` files are
preprocessed normally, so scenario SQF is unaffected.

Separately, the combined `gameplay` tier has outgrown its default 720 s bound.
A full-tier run performed during this review reached 94 assertions — the highest
recorded for this repository — and then terminated as `FAIL (timeout)` partway
through rotary CAS, with fixed-wing, logistics, markers, transport and UI never
reached. Every milestone's fresh autonomous proof to date has been a
single-scenario `--select` run, so this is a budget limit rather than a
behavioral regression, but it should be raised deliberately rather than
discovered again. That same combined run recorded one
`vigil.cas.attack.effect` failure with an empty `HitPart` list while fire
correlation and damage events passed; the identical scenario passed standalone
immediately afterwards (`20260816T152724Z-342d0e5b`, zero failures), and no
Vigil source references any CBR symbol, so it is pre-existing sensitivity in
that oracle rather than an effect of this review.

## Security and compatibility

The refinement adds no capability, dependency, network path or content
requirement: it replaces one loop termination condition and adds a time bound.
The scenario requires no VNC actor and no framebuffer evidence. Nothing changes
AppArmor, seccomp, capabilities, no-new-privileges, Steam/CEF confinement, or
VNC publication.

## Next review

Field Utilities Fabricator and Virtual Storage, excluding the covered fixed-wing
airdrop path. CBR's Eden/Zeus module entry points, marker sharing policy and
multi-launcher arbitration remain separate follow-ups rather than silent
expansions of this contract.
