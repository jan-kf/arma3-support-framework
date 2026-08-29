# Counter Battery Radar concurrency and arbitration review

## Current result

**PARTIALLY RESOLVED AND PERMANENTLY COVERED.**

The 2026-08-28 decision eliminated permanent warning-zone membership. CBR now
retains independent strike observations and derives non-destructive
client-local screen-space clusters. Close zoom splits rows, overview zoom merges
them, and a buffered capsule preserves a linear barrage. No active-observation
cap exists. Run 20260828T175511Z-44e26fea proves this boundary.

## Decisions closed

- cluster meaning is visual proximity at the current map scale, never durable
  ownership;
- membership is dynamically recomputed merge/split presentation;
- two launchers aimed together may visually merge while rows stay independent;
- walking fire needs no migration policy;
- aggregate geometry is a compact shape-preserving envelope;
- overload has no arbitrary cap without performance evidence.

Arrival order can no longer permanently assign a strike to a zone. Reversing
row order should preserve components away from thresholds; exhaustive boundary
matrices are optional long-tail.

## Remaining product decisions

1. **Warning cadence:** current behavior is once per firing machine's owner-local
   airborne cycle. Choose launcher, salvo, time window, visual group, or another
   unit, including moving-barrage re-warning.
2. **Confirmed-origin lifetime:** choose stop-only persistence or independent
   timed decay.
3. **Audience:** rows currently replicate to every client and origin markers
   remain global. Choose global, side-scoped, or radar/operator-scoped output.

## Remaining authority and topology

Retained provenance is not authentication. A future refinement should register
the physical launch against remote owner and launcher, accept updates only from
that owner, and reject wrong-owner, unregistered, stale and replayed rows.

Same-owner origin isolation and warning policy can be proved after those
decisions. Cross-owner equivalence, client-B, JIP and disconnect remain shared
external topology work. Performance testing is not required now; if measurement
later reveals a limit, overload semantics must precede a cap.

Any future concurrency proof must retain exact real guns/ammunition,
overlapping independent trajectories, terminal impacts, provenance and
negative authority receipts. A visual merge does not imply destructive data
aggregation, common launcher identity, or one warning.
