# Counter Battery Radar multi-launcher arbitration — canonical feature review

## Scope and result

This review covers simultaneous launchers/shell owners, cluster assignment,
warning cadence, origin isolation, and concurrent expiry. It does not reopen the
accepted single-launcher detection, terrain-aware prediction, marker accuracy,
warning, origin, replication, or lifecycle baseline.

**Classification: `REFINE BEFORE PERMANENT COVERAGE; PRODUCT ARBITRATION
DECISIONS REQUIRED` (reviewed; not covered).**

Current behavior is coherent for one firing machine but not ownership-neutral:
launch warning cadence is once per firing machine's local airborne cycle.
Otherwise identical simultaneous rounds can therefore produce one warning when
co-owned and multiple warnings when split across machines. Owner-local launch
and track endpoints also accept unbound caller-authored identities, side,
impact, launcher, and first-cycle state.

## Candidate stable contract

After a chosen policy, simultaneous exact real artillery rounds are grouped and
warned according to gameplay geometry/salvo meaning, never incidental process
ownership or arrival order. Every track update remains bound to its authenticated
source owner/launcher. Close/far clusters, independent origin estimates, expiry,
and warnings are deterministic under reversed fire order and locality. Forged,
wrong-owner, stale, or replayed telemetry changes no marker/origin/warning state.

## Canonical twelve-question review

1. **What should the user observe?** Concurrent real artillery produces one or
   more threat zones, counts/ETAs, warnings, and launcher-origin estimates whose
   grouping and lifetime reflect a stated product policy. The current UI does
   not explain whether zones mean impact proximity, salvo, or launcher.
2. **What does it do now?** Each owner-local shell gets a `clientOwner:counter`
   UID and sends predicted impact/ETA every 0.5 seconds. Server queue processing
   assigns a new UID to the nearest current cluster center within 100 m and
   never migrates it. Centers move only after 25 m; members expire separately.
   Origin state is keyed by launcher netId. Warning eligibility is computed from
   a machine-local list of airborne shells.
3. **Which machines own it?** Shell observation correctly follows shell
   locality; cluster/origin/marker mutation is server-owned. Authority is not:
   server receivers do not bind UID to `remoteExecutedOwner`, and the launch
   handler trusts caller-supplied vehicle, side, impact, and first-cycle state.
   Cross-owner arrival order can affect initial cluster choice.
4. **Which mechanics are generic?** Exact real artillery identities,
   trajectories, locality/owner evidence, concurrent windows, marker census,
   metamorphic order reversal, and expiry observation are Tribunal mechanics.
   Cluster/warning/origin policy remains CBR product meaning.
5. **Which behavior is product-owned?** Impact proximity versus launcher/salvo
   grouping; merge/split/reassignment; warning cadence; walking-barrage
   behavior; multi-origin persistence; concurrency bounds; and overload policy
   belong to Advanced Systems.
6. **Are unusual engine requirements proven?** No. The shell-local observer is
   sensible but no evidence requires raw caller-authored UID, per-machine
   airborne cycles, fixed-first-cluster membership, 100 m linking, 25 m center
   hysteresis, or serial arrival-order arbitration. Shell netId was `0:0` in
   prior evidence, so it cannot simply be assumed to solve identity.
7. **What is fragile or incomplete?** Warning count changes with owner locality.
   Moving predicted impacts never reassign. Near ties select the first array
   entry. A source can forge clusters/origins/warnings. Global marker state can
   self-confirm forged telemetry. No cap or overload behavior exists.
8. **Is a better mechanism available?** Keep owner-local physical observation,
   but register an authenticated launch identity/owner/launcher on server and
   accept later updates only from that owner. Choose arbitration policy before
   replacing grouping. Do not guess an engine identity mechanism; measure the
   real event/owner values first.
9. **What is the stable contract and causal proof?** Same-owner close and far
   pairs must have overlapping airborne intervals and independently sampled
   real trajectories. Exact product UIDs map to those observed shells; cluster
   memberships/count/ETA and origin keys match policy. Reversing fire order
   preserves partitions away from thresholds. Cross-owner geometry produces the
   same result. Wrong-owner/unregistered/spoofed updates reach rejection and
   leave independent marker/origin/warning census unchanged.
10. **Which details remain free?** UID format, queue/hash structures, polling
    cadence, exact marker names, tie algorithm, thresholds/hysteresis, receipt
    schema, and storage remain replaceable once policy/outcomes are selected.
11. **Which mechanisms deserve characterization?** First measure real same-owner
    versus cross-owner launch/locality/`remoteExecutedOwner` and UID transport.
    Then test close targets comfortably under 100 m and far targets over 300 m,
    both fire orders. Boundary values wait until core semantics are accepted.
12. **What belongs in Tribunal?** Existing native artillery/trajectory and marker
    observers suffice. Add only a generic concurrent-window/order-reversal
    helper if a second consumer needs it. Never promote CBR clustering policy.

## False-PASS boundary

Two markers do not prove two real simultaneous threats. Each phase must prove
both exact guns fired the expected ammunition, both shells flew during a common
window, and their independently observed trajectories/terminal impacts support
the intended geometry. Internal queue/cluster state, product UID, marker count,
or warning alone can all be caller-authored. One cluster can disappear before a
late census and make a sequential test look concurrent. A negative authority
control is valid only after an exact request receipt proves it reached rejection.

Reverse launch order is mandatory away from thresholds. A changed partition is
evidence of order dependence, not a tolerance problem. Same-owner and
cross-owner pairs must use equivalent geometry; client-a alone cannot establish
client-N behavior.

## Product decisions and continuation

Decide:

1. impact-proximity, launcher/salvo, or hybrid cluster meaning;
2. fixed membership versus dynamic merge/split/reassignment;
3. warning cadence per mission, launcher, salvo, cluster, or time window;
4. whether two launchers aimed together merge;
5. whether walking fire moves or splits a zone and when it re-warns;
6. independent origin confirmation/expiry semantics;
7. concurrency limits and overload behavior;
8. authenticated owner-local telemetry and rejection/result policy.

Then bind a server launch record to source owner and launcher, and accept track
updates only from that identity. Run same-owner close/far pairs, reversed order,
cross-owner equivalents, forged/wrong-owner controls, independent origin
confirmation/fade, and staggered cluster expiry. Reuse the accepted terrain-aware
oracle and marker observer. Do not extend the 720-second bound or weaken the
single-launcher assertions.
