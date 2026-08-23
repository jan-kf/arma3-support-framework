# Sacred Texts live trial — Vigil helicopter stabilizer

## Before-work retrieval

The supported `arma-knowledge dossier` interface was queried before product
changes for the mechanisms actually used by the source: `addForce`,
`getCenterOfMass`, `getMass`, `velocity`, `speed`, `vectorDir`, `getPosASL`,
`getPos`, `getTerrainHeightASL`, `modelToWorld`, `local`, `currentPilot`,
`remoteControlled`, and `isEngineOn`. Current release context was Arma 3 2.22.

Useful current-applicable BIKI results were:

- `addForce` applies one frame of impulse-like force; the force is world-space,
  its position is relative to the object, and the affected object/unit locality
  matters. Historical 1.72/2.04 annotations are introduction/change metadata,
  not validity end-points.
- `getCenterOfMass` is relative to model centre for PhysX objects, and `getMass`
  returns the PhysX object's mass.
- `velocity` is world-space m/s. `speed` is km/h along model-space Y, not total
  velocity magnitude. `vectorDir` is world-space and is not promised normalized.
- `getPos` returns surface-relative AGLS and is not a general three-dimensional
  position. `getPosASL` returns ASL. `getTerrainHeightASL` ignores input Z.
- `modelToWorld [0,d,0]` follows model-forward and respects orientation; it is
  not a velocity-path probe.
- `local` is the authority predicate. `currentPilot`, `remoteControlled`, and
  `isEngineOn` provided applicable signatures; the remote-engine community
  caveat was irrelevant because the experiment observed server-local aircraft.

No relevant `OUR VERIFIED NOTES` or open generic conjectures were returned.
Community material added no reliable requirement beyond the canonical command
semantics. The dossiers did not answer whether Vigil's nonlinear formula was
safe/useful, whether its forward terrain horizon matched product intent, or how
Arma AI would react; those gaps required controlled physical evidence.

## What retrieval changed

It prevented three design mistakes: treating `speed` as total speed, treating
`getPos` Z as ASL, and describing the 100/300/500 m probes as predicted flight
path. It made server locality and world-Z force explicit experimental facts.
It did not justify preserving any force formula or threshold.

## Controlled result and post-work retrieval

Live runs `20260823T135908Z-f6ce532b`,
`20260823T143318Z-c3288710`, and final artifact run
`20260823T144525Z-a5b9d6a6` found an inconsistent effect after lane reversal
that missed predeclared usefulness gates and included a treatment-worse
counterexample; exact values and rejected fixture attempts are in
[`vigil-helicopter-stabilizer-review.md`](vigil-helicopter-stabilizer-review.md).
Post-work dossier retrieval returned the same current command semantics. No
Pontifex-specific result was promoted into generic Sacred Texts.

## Reviewed generic distillation

| Candidate | Classification | Disposition |
| --- | --- | --- |
| Current Vigil force misses its product usefulness gate | PROJECT-SPECIFIC ONLY | retained in review/evidence only |
| Model-forward probes saw terrain beyond this LZ | PROJECT-SPECIFIC ONLY | fixture/product-policy fact |
| `addForce` is one-frame/world-space and position-relative | ALREADY REPRESENTED GENERICALLY | BIKI already states it |
| `speed` is model-forward km/h | ALREADY REPRESENTED GENERICALLY | BIKI already states it |
| General claim that model-forward terrain guards are unsafe | GENERIC ARMA CONJECTURE SUGGESTED | not entered; evidence is too narrow |

Zero generic lemmas and zero generic conjectures were added. A future generic
claim would need a dedicated multi-fixture characterization rather than this
Vigil trial.
