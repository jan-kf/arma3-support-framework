# CLAUDE.md

Guidance for Claude Code sessions in this repository. Read this first, then read
the authoritative documents it links. Do not restate or duplicate their content
here — they are canonical and this file must not drift from them.

## Two separate things live here

| | Pontifex | Tribunal |
| --- | --- | --- |
| What | The Arma 3 mod suite / in-universe company | A generic Arma mod-validation framework |
| Where | `source/`, `tools/`, `build/`, `server/`, `client/`, `runs/` | `tribunal/` |
| Owns | Four mods (CORDIS, Field Utilities, Advanced Systems, VIGIL), builds, Steam/Proton/server runtime, Live Mode, feature scenarios | Mission/PBO packaging, assertion protocol, scenario discovery, generic fixtures/observers, evidence attachments, terminal lifecycle |

Hard boundaries, enforced by `tests/test_tribunal_architecture.py`:

* **Tribunal must never contain product names or semantics.** No `aps`,
  `vigil`, `field utilities`, `iron dome`, or `pontifex` tokens anywhere under
  `tribunal/**.py`. Tribunal supplies mechanics; it never decides product success.
* **Production mods must never depend on Tribunal.** Nothing in `source/*/addons`
  may reference the framework.
* Tribunal is intended to stay reusable by unrelated future mods. Do not promote
  a mechanic into it speculatively — only with a concrete first consumer and a
  product-neutral I/O contract.

## Canonical methodology — read before changing product behavior

* [`tribunal/docs/feature-review-program.md`](tribunal/docs/feature-review-program.md)
  — **the canonical 12-question feature-review and validation program.** Any
  feature review or substantial permanent coverage must follow it as written,
  including its classification gates, execution phases, and acceptance rules.
  There is exactly one review program; do not create a local variant.
* [`tribunal/docs/testing-methodology.md`](tribunal/docs/testing-methodology.md)
  — test taxonomy, existing coverage audit, generic capability backlog.
* [`tribunal/docs/architecture.md`](tribunal/docs/architecture.md) — who owns
  which mechanism, capability contracts, security/network/audio boundaries.
* [`tribunal/docs/pontifex-feature-inventory.md`](tribunal/docs/pontifex-feature-inventory.md)
  — **the feature inventory and review queue.** Pick the next review from its
  prioritized list; a completed review updates its statuses.

Completed reviews are durable evidence and live beside the program:
`tribunal/docs/*-review.md`. Read the relevant one before touching a covered
feature.

"Perform the canonical feature-review program" means the whole thing: review,
experiments, evidence-supported refinements only, justified permanent coverage,
Live Mode where useful, a **fresh autonomous cold run**, validation, inventory
update, commit, report. Do not wait to be asked for the individual phases.

## Test ownership separation

* **Feature-owned scenarios** live beside the mod they validate, in
  `source/<component>/tests/tribunal/*.py`, and export a `TRIBUNAL_SCENARIO`
  (`Scenario` + `ScenarioReview`). They consume Tribunal mechanics and apply
  product semantics. They may reference private product APIs to reach or observe
  behavior — those names are evidence adapters, never the contract.
* **Generic Tribunal capability scenarios** live in `tribunal/scenarios/` and
  prove the framework, not any product feature.
* **Static/contract tests** live in `tests/` (`python3 -m unittest discover -s tests`).
* Every permanent scenario must carry complete `ScenarioReview` metadata
  (`tribunal/runner/model.py`): test type, behavior contract, outcome,
  rationale, dependencies, evidence types, locality, and any
  `CharacterizedBehavior` records. `behavior_contract` must not name private
  product symbols.
* Scenario roots are registered in `tools/pontifex_multiplayer.py`
  (`FEATURE_SCENARIOS`). A new scenario file is auto-discovered from a
  registered root and joins the `gameplay` tier automatically. Note the known,
  recorded inconsistency: `tribunal.project.json` lists only the
  advanced-systems root for the generic CLI.

## Commands

Run from `/mnt/services/pontifex`:

```bash
./pontifex check                                  # HEMTT config/SQF checks + python unit suite
./pontifex build                                  # four unsigned dev PBOs into build/current/
./pontifex test                                   # fast/static suite (== check)
./pontifex test gameplay                          # fresh real-client gameplay tier (all feature scenarios)
./pontifex test gameplay --select <scenario-id>   # one scenario, fresh cold run
./pontifex test capability                        # Tribunal framework probes
./pontifex test live                              # start durable Developer Live Mode
./pontifex live exec server '<sqf>'               # Live probe (also: live exec client, live status, live reset, live stop)
./pontifex test dedicated                         # real server-only test
jq . runs/latest/results.json                     # machine results of the last run
```

More detail: [`README.md`](README.md),
[`docs/multiplayer-testing.md`](docs/multiplayer-testing.md) (tiers, Live Mode,
security boundary), [`docs/dedicated-testing.md`](docs/dedicated-testing.md),
[`docs/vigil-testing.md`](docs/vigil-testing.md).

Live Mode snippets run through `call compile`, which does **not** preprocess:
`//` and `/* */` comments are syntax errors, and payloads above ~20 KB are
silently truncated by Arma's `callExtension` buffer. Both are rejected up front
with a clear message — comment detection ignores string literals, and the size
check measures the *delivered* payload, since a client snippet is relay-wrapped
with every quote doubled and can roughly double in size. Permanent scenario SQF
lives in preprocessed mission files and is unaffected. Live Mode is a
development aid, never proof.

Conventions:

* Each run is retained under `runs/<run-id>/`; `runs/latest` symlinks the newest.
* **A fresh autonomous proof is a single-scenario `--select` run.** That is how
  every milestone to date was proven.
* **Know your timeout.** `./pontifex test gameplay` dispatches to the `tier`
  subcommand, whose default is **360 s** (`PONTIFEX_TIER_TIMEOUT`). The 720 s
  default belongs to the unrelated `test`/`e2e` subcommands — do not confuse
  them. Longer scenarios need an explicit `--timeout`.
* **A `FAIL (timeout)` run proves nothing, even if every emitted assertion
  passed.** Assertions simply stop arriving at the deadline, so absence of
  failure is not evidence of success. Always check `status`/`reason` and compare
  emitted assertions against the plan's expected set before drawing any
  conclusion.
* The composed `gameplay` tier expects ~120 server assertions and does not fit
  360 s. At an explicit 720 s it gets much further but still times out, with
  genuine unrelated failures in fixed-wing IR strike and logistics. Treat those
  as independent follow-ups; do not raise timeouts to hide them.
* Assertion prefix is `PONTIFEX_TEST`; assertion IDs are dotted and
  feature-scoped (`aps.positive.engaged`, `vigil.artillery.circle.roundCount`).
* Product SQF uses the historical `YOSHI_`/`YSF_`/`YAS_`/`YFU_` prefixes.
  Tribunal SQF helpers use `TRIBUNAL_fnc_*`. Keep that split.
* HEMTT 1.20.1 is project-bootstrapped and checksum-verified on first use.
* Some legacy addon SQF files have **mixed CRLF/LF line endings**. Edit them
  byte-precisely, or a two-line change becomes a whole-file diff that hides the
  real change from review.
* `release` is deliberately disabled until versioning/signing policy exists.
* Never put a credential in a command, file, or commit.

## How to treat completed milestones and existing coverage

* **Existing code is evidence — neither automatically correct nor automatically
  the specification.** Do not restart the architecture, and do not "fix" a
  reviewed mechanism on aesthetics.
* A feature marked **COVERED** in the inventory has a reviewed contract and a
  passing permanent scenario backed by real Arma evidence. Do not weaken its
  assertions, expand its timeouts, or silently broaden its contract. Extend
  coverage in a new scenario or an explicit follow-up review.
* **REVIEWED / DEFERRED** means the product decisions are missing. Do not invent
  the behavior to make a test possible; the correct outcome is to stay deferred.
* **REVIEWED / NEEDS EXPERIMENTATION** means a controlled A/B is owed before the
  mechanism may be frozen or replaced.
* Historical run artifacts and assertion prefixes are deliberately retained for
  comparability. Do not renumber or reformat them.
* Finish a milestone the way previous ones were finished: docs + inventory
  updated, static suite green, fresh autonomous run recorded, tree clean, one
  commit.

## Mistakes to avoid

* Adding permanent gameplay coverage before the positive path is reached and the
  first failure is known.
* Passing on internal flags/ledgers alone. Assertions fail closed; nil, missing
  identity, timeout, and absent evidence are failures, and every wait is bounded.
* Reporting one authenticated client's result as client-b, multi-client, or JIP
  proof. There is exactly one authenticated Steam identity today; new APIs use
  logical identities (`client-a`, future `client-b`) so later evidence is
  additive.
* Automating camera/menu/VNC input to reach product code once the generic
  framework interaction is already proven — prefer data oracles; framebuffer
  evidence is for contracts that are themselves visual.
* Claiming audible playback: automated clients run `-noSound`.
* Setting `player_spawn`/`respawn_on_start` in scenario metadata without
  checking the others. They are **tier-global and mutually exclusive** — a
  conflicting value makes the whole gameplay tier refuse to build a mission.
  Prefer deriving fixture geometry from the player's runtime position.
* Scenario SQF in one tier runs concatenated in scenario-id sort order on a
  shared mission. Leave global product state as you found it (the CBR scenario
  stops the system it started), and do not inherit another scenario's state.
* Weakening the client container's security posture (capabilities, AppArmor,
  seccomp, no-new-privileges, VNC publication) to make a test pass.
