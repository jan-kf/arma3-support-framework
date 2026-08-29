# Pontifex pre-migration differential baseline

The migration invariant is differential equivalence, not completion of the
historical monolithic gameplay composition. The machine-readable contract is
`migration-baseline.v1.json`: every registered scenario ID, tier, participant,
and expected assertion must remain identical across extraction and relocation.

Frozen source commit: `7c658f9f86ca0e5cd23749c980d99fc68339ee84`.

## Required focused gates

| Boundary | Result | Fresh run |
| --- | --- | --- |
| Static/build contract | PASS, 224 tests plus four HEMTT checks | pre-migration working tree |
| CORDIS feature discovery/execution | PASS | `20260829T165029Z-3daf09b7` |
| Advanced Systems product-entrypoint execution | PASS | `20260829T165335Z-408a8993` |
| Field Utilities + ACE composition | PASS | `20260829T165207Z-f341c7e5` |
| Vigil whitelist product-entrypoint execution | PASS | `20260829T165523Z-07414ba5` |

Each post-migration gate must use the same scenario selection and produce
`PASS (complete)` with no missing or failed expected assertions. Run IDs and
artifact paths may differ and are not part of behavioral equivalence.

## Known pre-existing non-invariants

- The all-feature gameplay composition exceeds its 360-second tier deadline.
  A 720-second historical run progresses further but exposes independent
  fixed-wing IR/logistics failures. It is not a migration gate.
- Capability run `20260829T164755Z-49fcb1bc` ended `client_exited` before its
  assertions because Steam did not become ready. This cold-client environment
  failure is recorded, but it is not a passing behavioral baseline.
- Xwayland has previously aborted after an RFB disconnect while marshalling a
  pointer-lock request. Stock-Zeus pointer automation is no longer used by
  permanent feature-behavior scenarios.

No assertion may be removed, renamed, or relaxed to obtain post-migration
equivalence. Any post-migration difference from the machine inventory or the
four passing focused gates is a migration regression.
