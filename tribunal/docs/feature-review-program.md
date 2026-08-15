# Tribunal canonical feature-review and validation program

This is the canonical program for reviewing a feature before substantial
permanent Tribunal coverage. It applies to any Arma mod; product names belong
only in the feature-specific review and scenario, never in Tribunal's generic
contracts.

The program consolidates the recurring process established by
[`testing-methodology.md`](testing-methodology.md), `ScenarioReview`, completed
feature reviews, Live experiments, and fresh autonomous proofs. Existing code
is evidence. It is neither automatically correct nor automatically the
specification.

Related repository sources:

* [`testing-methodology.md`](testing-methodology.md) defines the test taxonomy
  and links here for the single canonical review procedure;
* [`ScenarioReview`](../runner/model.py) stores the concise permanent-scenario
  metadata produced by this program;
* [`pontifex-feature-inventory.md`](pontifex-feature-inventory.md) is Pontifex's
  project-specific review queue and coverage record, and links back here.

## How to invoke this program

A review request needs only:

1. the owning project and feature;
2. the project's current feature-inventory entry;
3. a short list of feature-specific concerns.

Unless a request narrows the scope to review-only, “perform the canonical
feature-review and validation program” means: complete the review, run needed
experiments, make only evidence-supported refinements, add justified permanent
coverage, prove it in Live Mode where useful and in a fresh autonomous run,
validate, update the inventory, commit, and report the final state.

## Layer 1 — canonical/static review program

### Required inputs

Inspect the owning mod's configuration, UI, functions, initialization paths,
documentation, history where it clarifies intent, existing scenarios/reviews,
shared dependencies, and current inventory entry. Trace real entry points; a
file or function name alone does not prove reachable or intended behavior.

Record reviewed scope and explicit non-scope. If the named feature contains
separable capabilities, classify them independently and name the primary
outcome for the review.

### The canonical 12 questions

Every completed review must answer these. An answer may be short for a simple
feature, but must include the investigation, evidence, decision, and applicable
stop condition below.

#### 1. What should the user or integrator observe?

* **Investigate:** intended input, action, visible or architectural result,
  failure behavior, and cleanup from the user, mission maker, Zeus operator, or
  consuming mod's perspective.
* **Evidence:** shipped documentation, reachable UI/actions/modules, public
  configuration, established behavior, and history that genuinely establishes
  intent.
* **Decide:** state the candidate product outcome without private helpers or
  data layouts.
* **Stop:** if no coherent intended result can be established, do not invent
  one. Classify it `DEFER` and identify the product decisions required.

#### 2. What does the feature actually do now, including negative paths?

* **Investigate:** every reachable entry through success, rejection,
  cancellation, timeout, destruction/disconnect, repeat use, and cleanup.
* **Evidence:** source/config traces, logs, focused probes, runtime artifacts,
  existing tests, and a controlled baseline where inspection is insufficient.
* **Decide:** distinguish implemented, partial, scaffolded, disabled,
  unreachable, obsolete-looking, and unclear paths; record contract divergences.
* **Stop:** do not add a permanent test while the positive path is unreached or
  the first failure is unknown. Use `NEEDS EXPERIMENTATION`, `REFINE`,
  `REWRITE`, or `DEFER` as warranted.

#### 3. Which machines and lifecycle stages own the behavior?

* **Investigate:** server, object/group owner, each client identity, UI locality,
  authority transfers, request/acknowledgment, replication, JIP, disconnect,
  and cleanup across setup/action/result.
* **Evidence:** `local`, `owner`, `groupOwner`, `netId`, origin logs,
  remote-execution paths, public state, and Tribunal locality records.
* **Decide:** declare authority for every mutation and which clients observe
  which result. Separate proven one-client behavior from multi-client/JIP.
* **Stop:** unknown authority, implicit locality, missing acknowledgment, or a
  local result presented as shared success blocks coverage. Client-a evidence
  must never be reported as client-b/JIP proof.

#### 4. Which mechanics are generic Arma, ACE, CBA, or Tribunal concerns?

* **Investigate:** engine physics, AI, ownership, interactions, rendering,
  input, network conditions, and evidence collection without product meaning.
* **Evidence:** official framework behavior, existing Tribunal capabilities,
  product-neutral probes, and repeated use by multiple features.
* **Decide:** identify reusable fixture/observer candidates and existing tools.
* **Stop:** do not freeze generic mechanics in a product contract, duplicate an
  existing capability, or introduce product names/semantics into Tribunal.

#### 5. Which behavior is owned by the product?

* **Investigate:** eligibility, request parameters, policy, filtering,
  resources, transitions, outputs, failures, and cleanup choices that define
  this feature.
* **Evidence:** owning-mod source/documentation and reachable behavior; generic
  engine possibilities are not product-intent evidence.
* **Decide:** assign each semantic rule to its owning mod and list missing
  product decisions.
* **Stop:** if a test must choose an undefined sensor, target, output,
  persistence, sharing, balance, or lifecycle policy, `DEFER` rather than
  implementing the test author's design.

#### 6. Are unusual or claimed engine requirements proven?

* **Investigate:** workarounds, odd scheduling, hidden objects, command
  sequences, timing, serialization, or compatibility rewrites attributed to
  Arma/ACE/CBA.
* **Evidence:** preferably a controlled A/B holding every other variable fixed,
  with logs and physical/rendered outcomes. Current code and anecdotes are not
  enough.
* **Decide:** record a proven engine requirement, leave the mechanism free
  behind the specification, or classify it `NEEDS EXPERIMENTATION`.
* **Stop:** no mechanism becomes characterization coverage without its
  alternative, evidence, reason, and outcome being retained.

#### 7. Which details are accidental, legacy, fragile, or incomplete?

* **Investigate:** dead-looking branches, duplicated helpers, stale globals,
  magic timing/coordinates, unreachable UI, empty tasks, commented registration,
  TODOs, unbounded waits, false success, and docs/config/runtime mismatches.
* **Evidence:** reachability/call sites, history, negative probes, cleanup state,
  and repeated execution.
* **Decide:** mark each replaceable, refine-before-coverage,
  rewrite-before-coverage, experimentation-needed, or deferred.
* **Stop:** do not preserve an accident merely because a fixture reproduces it.
  Unknown intent is not permission to delete or redesign it either.

#### 8. Is a better native or existing mechanism available, and is it proven?

* **Investigate:** native Arma commands, ACE/CBA APIs, shared project services,
  and Tribunal tools that could replace bespoke behavior.
* **Evidence:** controlled comparison of current and proposed paths under the
  same conditions, including negative behavior, locality, cleanup, and risk.
* **Decide:** keep, refine, or rewrite from evidence and contract, not aesthetics.
* **Stop:** do not replace working behavior or fossilize a workaround on an
  assumption. If comparison is unavailable, record `NEEDS EXPERIMENTATION` and
  keep the specification mechanism-neutral.

#### 9. What is the stable behavioral contract and its causal proof?

* **Investigate:** inputs, eligibility, authoritative action, visible/physical
  result, controls, resource changes, replication, bounded completion,
  repeatability, and cleanup.
* **Evidence:** favor real input, physical movement/fire/impact/damage,
  framebuffer/audio when relevant, exact identity, and authoritative state.
  Internal flags/ledgers correlate a result rather than replace it.
* **Decide:** write a concise mechanism-neutral contract and evidence matrix
  pairing each claim with an independent oracle and useful controls.
* **Stop:** missing causal evidence/controls, ambiguous identity, or success
  based only on correlated internal state blocks gameplay coverage.

#### 10. Which implementation details must remain free to change?

* **Investigate:** private function/variable names, schemas, ordering, polling,
  fixture classes/coordinates, waypoint shapes, marker names, control IDs,
  observer thresholds, and incidental effects.
* **Evidence:** compare the stable contract with assertions and
  `ScenarioReview.behavior_contract`.
* **Decide:** list evidence-adapter anchors separately from promised behavior.
* **Stop:** reject contracts that expose private layouts or fail a safe refactor
  despite unchanged user-visible behavior.

#### 11. Which mechanisms genuinely deserve characterization?

* **Investigate:** only mechanisms shown engine-imposed, deliberately
  architectural, or materially safer than alternatives.
* **Evidence:** a retained controlled comparison and reproducible artifacts.
* **Decide:** record description, reason, evidence, alternative tested, and
  outcome. Otherwise label it experimentation-needed or replaceable.
* **Stop:** current implementation, folklore, or one successful run cannot
  justify characterization.

#### 12. Which mechanics should be promoted into Tribunal?

* **Investigate:** repeated fixture, observation, interaction, locality, and
  reporting mechanics with a real consumer and plausible reuse.
* **Evidence:** a concrete product scenario, product-neutral I/O contract, and a
  clean mechanics-versus-meaning boundary.
* **Decide:** reuse an existing capability, add a narrow generic capability, or
  keep it feature-local until reuse is justified.
* **Stop:** Tribunal must not know product feature names or decide product
  success. Production mods must not depend on Tribunal. Do not build speculative
  abstractions for hypothetical consumers.

### Review outcomes and progression gates

Use these classifications:

| Outcome | Meaning | Progression rule |
| --- | --- | --- |
| `KEEP AS-IS AND SPEC-TEST` | Current behavior matches a stable contract; no engine mechanism needs freezing. | Proceed to specification coverage. |
| `KEEP + CHARACTERIZE ENGINE REQUIREMENT` | Behavior is sound and controlled evidence proves a required mechanism. | Add specification coverage plus the minimum characterization record. |
| `REFINE BEFORE PERMANENT COVERAGE` | A coherent feature has bounded defects or false-PASS risks. | Refine only proven defects, then repeat relevant evidence before coverage. |
| `REWRITE BEFORE PERMANENT COVERAGE` | Current implementation cannot safely/coherently satisfy the contract. | Rewrite within the established contract; do not preserve the broken mechanism. |
| `NEEDS EXPERIMENTATION` | Evidence cannot decide a mechanism, compatibility claim, or behavior. | Run controlled experiments before freezing/changing it; separable contract areas may proceed. |
| `DEFER` | No coherent contract, insufficient value, missing decisions, or intentionally deferred capability. | Stop; document evidence/decisions needed and add no permanent gameplay coverage. |

`ScenarioReview` stores `DEFER` as `DEFER / insufficient value`, the current
metadata enum. Review documents may use the concise label. A complex feature
may classify subsystems differently; its primary outcome must reflect what
gates the named review.

### Test-type decision

Assign every justified test one primary purpose:

* **Specification test:** protects meaningful inputs, outcomes, controls,
  cleanup, locality, and replication.
* **Evidence-backed characterization test:** protects only a proven required
  mechanism with its complete comparison record.
* **Tribunal tooling test:** protects product-neutral fixture/observer/runtime
  mechanics and contains no owning-mod semantics.
* **Feature-owned integration/gameplay test:** lives beside the feature,
  consumes Tribunal mechanics, and interprets evidence using product semantics.

Not every taxonomy leaf needs a permanent test. Incidental execution is not
specification coverage; private helpers usually belong to static/unit checks.

### False-PASS and evidence rules

Before implementation, enumerate how the scenario could pass without the
promised behavior. Consider stale prior state, unrelated objects/events, wrong
locality, request without execution, disappearance without causal result,
resource change without effect, effect without exact identity, one-frame
contact, missing result treated as success, cleanup hiding failure, and internal
state agreeing with itself.

Assertions fail closed. Nil/empty values, missing identity/evidence, exceptions,
unexpected termination, missing assertions/acknowledgment, and timeout are
failures. Only literal verified conditions pass. Evidence attachments must be
meaningful and run/token-scoped, and diagnose the first failed boundary; volume
alone is not quality.

### Multiplayer and client-N rule

Declare only what the run proves. One authenticated client proves that client's
request, observation, and replication boundary—not client-b, competing
requests, disconnect/reconnect, or JIP.

New scenario/infrastructure APIs use logical identities (`client-a`, future
`client-b`, and so on), identity-keyed expected assertions, and explicit
ownership. Future client-N/JIP evidence must be additive without architectural
rewrites or present-day overclaims.

### Execution and acceptance program

Use the smallest applicable sequence; record why a phase is unnecessary rather
than silently omitting it.

1. **Baseline/scope:** inspect repository/inventory and capture current positive
   and negative behavior without changing it.
2. **Twelve-question review:** classify capabilities; write contract,
   replaceable details, dependencies, locality, false-PASS risks, and evidence.
3. **Controlled experiments:** use one-variable A/B for uncertain engine
   requirements/native alternatives. Retain artifacts; do not shotgun changes.
4. **Refine/rewrite when classified:** change only evidence-proven defects and
   repeat the relevant baseline/control.
5. **Tooling boundary:** reuse Tribunal first; promote only narrow
   product-neutral mechanics with a concrete consumer.
6. **Permanent scenario:** keep semantics beside the owning mod; declare all
   assertions; use bounded waits, causal controls, locality, and cleanup; add
   complete `ScenarioReview` metadata.
7. **Live Mode:** investigate, calibrate, repeat, and check leaks/order dependence
   in retained state where useful. Live success is not final proof.
8. **Fresh autonomous proof:** stop Live Mode and run the complete permanent
   scenario cold, with independent lifecycle ownership and no human input.
9. **Validation:** run focused regressions, relevant static checks, and the
   owning repository's full validation.
10. **Closeout:** update feature/review docs and inventory status, inspect diff,
    commit, report evidence/run/assertions as applicable plus commit/worktree
    state, and leave the tree clean unless instructed otherwise.

Terminal success requires all declared server/client assertions, zero failures,
complete acknowledgments/results, prompt teardown, and cleanup. Terminal
failure reports the first concrete blocker; do not reopen unrelated layers
without evidence.

### Required review outputs

A durable review contains:

* scope, inventory status, and source/entry-point map;
* intended and current positive/negative behavior;
* answers to all 12 questions;
* subsystem classifications and primary outcome;
* stable contract and explicitly replaceable details;
* authority/locality/replication statement and current client-count limits;
* false-PASS analysis, controls, evidence matrix, cleanup, and time bounds;
* experiment records/characterized behaviors, if any;
* Tribunal capability reuse/promotion decisions;
* validation/fresh-run evidence or the exact stopping gate;
* updated inventory status and next product decisions.

For a permanent scenario, mirror the concise durable subset in
`ScenarioReview`: test type, contract, outcome, rationale, dependencies,
evidence types, locality, and complete `CharacterizedBehavior` records.

## Layer 2 — feature-specific investigation

Copy this small section into the review or working plan. It augments the
canonical program; it does not restate it.

```markdown
## Feature-specific investigation

- Feature / owning mod:
- Inventory entry and current status:
- Source, config, UI, and normal entry points:
- Explicit review scope:
- Explicit non-scope:
- Product-specific questions or decisions already known:
- Areas deserving special attention:
- Known dependencies and adjacent reviewed contracts:
- Current client identities and unproven multiplayer/JIP cases:
- Existing scenarios, artifacts, or historical evidence to reuse:
```

Special attention may name geometry, interaction, selection, resources,
cleanup, presentation, or other feature concerns. It cannot override the 12
questions, weaken evidence, or invent missing semantics.

## Sanity checks against established outcomes

The program permits all established outcomes:

* **Refine before coverage:** Vigil transport and rotary CAS had coherent goals
  but authority, filtering, lifecycle, physical-evidence, and false-success
  defects. Questions 2, 3, 7, and 9 gate coverage until refinement and proof.
* **Characterize or experiment:** Vigil UI's scheduler behavior had a retained
  controlled alternative and supports characterization. VLS handshake,
  hidden-pad landing, sensor/reveal dependence, and 3CB mapping lack equivalent
  proof and remain experimentation candidates under questions 6, 8, and 11.
* **Defer:** Vigil fixed-wing reconnaissance has labels/disconnected scaffolding
  but no reachable request, task, sensor/output, persistence, or sharing
  contract. Questions 1, 2, 5, and 9 stop at `DEFER`, documenting product
  decisions instead of inventing behavior/tests.

These are examples of applying a generic process, not Pontifex-specific
Tribunal requirements.
