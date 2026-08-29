# Pontifex / Tribunal migration completion

Completed 2026-08-29 under the no-behavior-change migration charter.

## Final layout

```text
/mnt/services/
├── tribunal/                         # independent Tribunal Git repository
├── arma-projects/
│   └── pontifex/                     # independent Pontifex Git repository
│       ├── mods/
│       ├── docs/
│       ├── tests/
│       ├── evidence/accepted/
│       └── tribunal.project.json
└── arma-state/
    └── pontifex/                     # outside Git/source
        ├── builds/
        ├── client/
        ├── dependencies/
        ├── runs/
        └── server/
```

`PONTIFEX_STATE_ROOT` overrides the state location. In the standard
`arma-projects/pontifex` layout it defaults to the sibling
`arma-state/pontifex` directory. `TRIBUNAL_ROOT` similarly overrides
Tribunal discovery. Pontifex consumes Tribunal API version 1 through
`tribunal.project.json` and the public `tribunal run PROJECT ...` command.

Feature scenarios remain beside their mods under
`mods/<component>/tests/tribunal/`. Durable accepted evidence remains in
`evidence/accepted/`; raw runs remain outside Git.

## Differential validation

The immutable comparison input is `docs/migration-baseline.v1.json`.
`python3 tools/migration_baseline.py compare` reports 36 equivalent scenarios
(34 Pontifex feature scenarios and 2 Tribunal capability scenarios), including
the same expected assertions. Tribunal's project CLI reports the 34
Pontifex-owned scenarios registered in `tribunal.project.json`.

| Family | Before | After |
| --- | --- | --- |
| CORDIS routing | `20260829T165029Z-3daf09b7` PASS | `20260829T172507Z-477644c3` PASS |
| Advanced Systems APS Zeus | `20260829T165335Z-408a8993` PASS | `20260829T172651Z-2e43ac07` PASS |
| Field Utilities ACE composition | `20260829T165207Z-f341c7e5` PASS | `20260829T172844Z-c37c6be2` PASS |
| Vigil whitelist modules | `20260829T165523Z-07414ba5` PASS | `20260829T173003Z-226ea3c6` PASS |

The final Pontifex static gate passes 231 tests and HEMTT checks for all four
mods. The four-mod build writes successfully to
`$PONTIFEX_STATE_ROOT/builds/current`. Standalone Tribunal passes 3 tests.
The final capability run `20260829T173520Z-8148bec4` also passes.

The pre-migration capability run `20260829T164755Z-49fcb1bc` failed before
capability assertions because the Steam client exited before readiness. This
was recorded as a pre-existing environment failure, not made a migration
prerequisite. The historical monolithic gameplay composition remains excluded:
its 360-second limit and the previously recorded fixed-wing IR/logistics
failures are not differential migration invariants.

## Migration defects found and fixed

Two migration-caused path/package defects were caught by the incremental gates:

1. `20260829T172309Z-655ec342` failed because external build paths could not
   be made relative to the repository. Commit `4d174de` preserves the
   Evidence Contract's historical `build/current/...` artifact identity
   independently of physical storage and adds regression coverage.
2. `20260829T173220Z-0616c731` reached all locality assertions but the
   container visual probe could not import the extracted Tribunal package.
   Commit `fada01e` mounts Tribunal read-only at `/tribunal`, exports its
   package path, and adds a container-contract regression.

No product behavior, scenario assertion, gameplay oracle, or accepted evidence
package was changed to resolve either defect. No migration-caused defect
remains known.

## History and compatibility

Tribunal was created with a history-preserving subtree extraction, not a file
copy. `git log --follow tribunal/mission/pbo.py` reaches
`e9d4aa6 Establish Tribunal testing framework boundary`. Pontifex rename
history is likewise followable across `source/` to `mods/`.

There is no compatibility symlink at `/mnt/services/pontifex`, and embedded
Tribunal has been removed. Four tracked `.hemttout` symlinks remain because
HEMTT fixes that output name; they point only into
`arma-state/pontifex/builds/hemtt`. The explicit state and Tribunal
environment overrides remain supported. A legacy state layout fallback for
non-`arma-projects` checkouts and Tribunal's hidden legacy `--project` CLI
form remain for compatibility; neither is used by the final layout.
