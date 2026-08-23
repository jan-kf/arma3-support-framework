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
* [`../evidence/README.md`](../evidence/README.md) defines Tribunal Evidence
  Contract v1 production and correction semantics;
* `/mnt/services/arma-knowledge/README.md` defines Sacred Texts retrieval,
  Evidence Contract ingestion, applicability, audit, and reviewed generic
  distillation.

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

The following is also a complete invocation; it does not require a larger
prompt or conversational history:

> Look into uncovered features in Pontifex, select and cover the next best
> candidate, and report back the conclusions.

### Selecting the feature

When the request does not name a feature:

1. Start from the actual current
   [`pontifex-feature-inventory.md`](pontifex-feature-inventory.md), its
   prioritized-next section, applicable author decisions, and the newest
   `pontifex-progress-estimate-*.md`. Confirm the accepted HEAD and worktree
   before changing anything.
2. Exclude already `COVERED` surfaces unless the inventory names a bounded gap;
   exclude work blocked by an unavailable product decision, dependency,
   authenticated client identity, or engine fixture. Record those blockers
   rather than silently skipping them.
3. Prefer the highest-value unblocked surface, considering its inventory
   weight, user impact, architectural dependencies, risk, ability to unlock
   other work, and likelihood that controlled evidence can reach a justified
   terminal state. “Next best” does not mean merely the smallest change.
4. Read the feature's existing review, accepted adjacent contracts, source,
   entry points, configuration, and history before proposing a contract. State
   why the selected feature outranks the alternatives.
5. Recommend the next candidate at closeout, but do not begin it unless the
   user explicitly requested sequential or self-continuing work.

### Sacred Texts first

Before substantive product investigation, implementation, external research,
or engine assumptions, inspect the feature enough to identify the Arma/ACE/CBA
mechanisms it actually uses, then retrieve their Sacred Texts dossiers:

```bash
cd /mnt/services/arma-knowledge
.venv/bin/arma-knowledge dossier '<concept>'
# Use --offline when a fresh release-context refresh is unnecessary/unavailable.
```

Record useful canonical BIKI documentation, attributed community reports,
`OUR VERIFIED NOTES`, generic `OPEN CONJECTURES`, project findings, tested build
and applicability, and unanswered questions. Source documentation is not engine
proof; community reports are not verified facts.

Version annotations have distinct meanings. `introduced_in` and
`available_since` normally describe an open-ended currently applicable range
unless later evidence establishes `changed_in`, `deprecated_in`, `removed_in`,
or a narrower validity range. `documented_on`, `tested_on`, and `verified_on`
describe evidence scope, not validity end-points. Distinguish continuity-based
`CURRENTLY_APPLICABLE`, `DIRECTLY_VERIFIED_ON_CURRENT_BUILD`,
`LAST_VERIFIED_ON_OLDER_BUILD`, historical introduction, and actual
changed/removed/deprecated behavior. Never report old introduction metadata as
historical-only guidance.

## Layer 1 — canonical/static review program

### Required inputs

Inspect the owning mod's configuration, UI, functions, initialization paths,
documentation, history where it clarifies intent, existing scenarios/reviews,
shared dependencies, and current inventory entry. Trace real entry points; a
file or function name alone does not prove reachable or intended behavior. The
same applies to the validation harness itself: read a default, budget, or flag
from the subcommand the run actually dispatches to, not from a similarly named
neighbour.

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
* **Evidence:** favor engine-visible data, exact identity, authoritative state,
  and physical movement/fire/impact/damage. Use real input, framebuffer, audio,
  or animation capture when the contract is inherently about that interface or
  no reliable data oracle exists. Once a generic framework interaction is
  proven, feature scenarios may verify its registered/active action and invoke
  that exact statement rather than repeatedly automating camera/menu input.
  Internal flags/ledgers correlate a result rather than replace it. Drive the
  contract from its real entry point: calling a helper near the end of the
  owning mod's own pipeline proves that helper, not the path a user or
  integrator takes. The framework-interaction allowance above is narrow — it
  substitutes a proven generic input mechanism for the same registered action
  node; it does not license skipping the owning mod's stages.
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
| `RETIRE / REMOVE` | Evidence establishes that the reachable behavior is unwanted, unsafe, obsolete, or has no supported product contract. | Remove or disable only the proven surface, protect the intended absence where valuable, and do not award functional coverage for the retired capability. |

A `KEEP` result, or a completed `REFINE`/`REWRITE`, becomes `ACCEPTED / COVERED`
only after its permanent scenario and fresh proof pass. Review classification and
inventory coverage status answer different questions; do not use “accepted” to
hide an uncompleted progression gate.

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

These rules follow from that enumeration and apply to every scenario:

* **Use authentic engine stimulus where practical.** Prefer native firing,
  movement, module dispatch, registered interaction statements, and real product
  entry points over synthetic end-state injection. A synthetic fixture must be
  identified and cannot prove the omitted engine/product pipeline. Visual input
  automation is necessary only when the contract is visual or no dependable data
  oracle exists.
* **A negative control must prove its own stimulus.** Asserting that nothing
  happened means something only once the run has independently proven, through a
  separate oracle, that the input the feature was supposed to ignore actually
  occurred. Otherwise a fixture that silently failed to act passes the control.
* **A control must sit unambiguously on its side of every threshold it tests.**
  Fixture geometry derived from run-varying inputs is resolved at runtime and
  recorded in the evidence; a control left at the boundary tests the run rather
  than the feature.
* **Derive expected values from independent observation, never from the state
  that produced the observed value.** Comparing a rendered or reported value
  against an expectation computed from the same fields proves formatting, not
  behavior. Where the comparison is against a rounded, sampled, or deliberately
  stale presentation, state an explicit tolerance, justify each bound from a
  named mechanism, and make it asymmetric when the error has a known direction.
* **A precondition sampled once is not a precondition.** Quiescence, emptiness,
  idleness and similar states that a concurrent process can transiently satisfy
  must be required to hold across a bounded interval, and preceding activity
  must be drained through its own oracle rather than assumed finished.

Assertions earn their place by failing. Where a review refines a proven defect,
run the new assertion against the unrefined build and record that it fails and
by what margin. An assertion never observed to fail is not yet evidence that it
protects anything.

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

1. **Selection/preflight:** select from the current inventory as described
   above; record accepted HEAD, worktree state, current review/coverage estimate,
   related contracts, and blockers.
2. **Sacred Texts:** retrieve dossiers for the mechanisms actually used and
   record their applicability and gaps before substantive changes.
3. **Baseline/scope:** inspect repository/inventory and capture current positive
   and negative behavior without changing it.
4. **Twelve-question review:** classify capabilities; write contract,
   replaceable details, dependencies, locality, false-PASS risks, and evidence.
5. **Controlled experiments:** use one-variable A/B for uncertain engine
   requirements/native alternatives. Retain artifacts; do not shotgun changes.
6. **Refine/rewrite when classified:** change only evidence-proven defects and
   repeat the relevant baseline/control.
7. **Tooling boundary:** reuse Tribunal first; promote only narrow
   product-neutral mechanics with a concrete consumer.
8. **Permanent scenario:** keep semantics beside the owning mod; declare all
   assertions; use bounded waits, causal controls, locality, and cleanup; add
   complete `ScenarioReview` metadata.
9. **Live Mode:** investigate, calibrate, repeat, and check leaks/order dependence
   in retained state where useful. Live success is not final proof.
10. **Fresh autonomous proof:** stop Live Mode and run the complete permanent
    scenario cold, with independent lifecycle ownership and no human input.
11. **Validation:** run focused regressions, relevant static checks, and the
    owning repository's full validation.
12. **Evidence and knowledge:** publish/retain Evidence Contract v1, ingest it
    idempotently, audit the knowledge ledger, perform reviewed generic
    distillation, and retrieve affected Sacred Texts again as described below.
13. **Closeout:** update feature/review docs, inventory status, weighted progress
    and remaining-priority surfaces; inspect the diff, commit, report, and leave
    the tree clean unless instructed otherwise.

For a pure `DEFER`, `NEEDS EXPERIMENTATION`, or documentation-only terminal
review, phases that would falsely imply accepted runtime behavior may be
inapplicable. Say why they were omitted. A new/refined permanent gameplay
contract requires a fresh single-scenario autonomous proof; Live or a stale run
cannot substitute for it.

Terminal success requires all declared server/client assertions, zero failures,
complete acknowledgments/results, prompt teardown, and cleanup. Terminal
failure reports the first concrete blocker; do not reopen unrelated layers
without evidence.

Two rules govern how a run is read:

* **A run that ends in timeout proves nothing, including for the assertions it
  did emit.** Assertions stop arriving at the deadline, so absence of failure is
  not evidence of success. Compare the emitted set against the plan's expected
  set before drawing any conclusion, and never raise a time budget to conceal an
  unrelated failure — scope that failure as separate work instead.
* **Do not chase intermittent behavior with speculative fixture changes.** An
  unexplained non-reproduction is evidence to be captured, not a defect to be
  guessed at. Revert any change not shown to address a confirmed cause, add
  diagnostics that capture the deciding state at the moment of use so a
  recurrence diagnoses itself, and record residual nondeterminism honestly
  rather than declaring it solved.

### Evidence Contract and knowledge closeout

Accepted characterization uses `tribunal.evidence/v1`. Feature-owned scenario
semantics belong in `Scenario.evidence_contract`; Tribunal's generic reporter
must not infer a product proposition from line assertions. The package names a
stable scenario and proposition intent, treatment/control arms and causal
relationships, participants/locality, typed observations and assertions,
applicability/build, source snapshot, and durable artifacts. An assertion PASS
is an execution fact, not automatically a theorem. Failed, timed-out,
cancelled, aggregate, or semantics-free runs cannot publish accepted feature
propositions. A scientifically valid negative characterization may publish a
negative/counterexample outcome without pretending the rejected product claim
passed. Published bytes are immutable; corrections use a new revision and
`supersedes_package_id`.

After accepting a package, use the supported consumer interface:

```bash
cd /mnt/services/arma-knowledge
.venv/bin/arma-knowledge counts
.venv/bin/arma-knowledge ingest-evidence-v1 --package-file /mnt/services/pontifex/runs/<run-id>/evidence-package.v1.json
.venv/bin/arma-knowledge counts
# Run the identical ingest again; the second post-ingest counts must not change.
.venv/bin/arma-knowledge ingest-evidence-v1 --package-file /mnt/services/pontifex/runs/<run-id>/evidence-package.v1.json
.venv/bin/arma-knowledge counts
.venv/bin/arma-knowledge audit
```

If an immutable corrected revision exists, ingest its named predecessor first,
then the correction, then repeat the correction for idempotency. Never repair an
accepted package in place. Retrieve the feature and affected mechanism dossiers
again after ingestion and record exactly what changed.

Every potentially reusable finding receives a reviewed disposition before
running the accepted `.venv/bin/arma-knowledge distill-tribunal` workflow:

* `PROJECT-SPECIFIC ONLY`;
* `GENERIC ARMA LEMMA DIRECTLY DEMONSTRATED`;
* `GENERIC ARMA CONJECTURE SUGGESTED`;
* `ALREADY REPRESENTED GENERICALLY`;
* `NEEDS DEDICATED CHARACTERIZATION`.

The permanent semantic boundary is strict: **`OUR VERIFIED NOTES` contains only
generic Arma lemmas**, meaningful after all Pontifex/mod terminology is removed,
directly supported by exact observations and passing assertion identities, and
scoped no wider than the source evidence. Project findings remain attached to
project concepts. A suggested but unproved reusable claim may appear only as a
generic `OPEN CONJECTURE`, never a verified note. Zero generic findings is a
valid result; do not run extra experiments or broaden a proposition merely to
manufacture reusable knowledge. The reviewed manifest and safeguards are
documented in `/mnt/services/arma-knowledge/docs/TRIBUNAL_GENERIC_DISTILLATION_REPORT.md`.

### Progress accounting and final report

Update the newest `pontifex-progress-estimate-*.md` using the established
weighted meaningful-feature-surface model, not assertion counts and not a
denominator chosen to improve the percentage. Report two separate measures:

* **Feature-review completion:** credit for durable understanding and a
  justified terminal classification. Reviewed/refined/rewritten/deferred/retired
  surfaces may advance this measure.
* **Permanent automated coverage:** credit only for accepted behavioral
  contracts with proportionate permanent proof. Deferred, retired,
  experimentation-needed, incidental, static-only, or intellectually understood
  behavior receives no invented functional-coverage credit.

Preserve the current family weights unless repository-grounded inventory change
requires an explicit recalculation. Report before/after point estimates,
ranges/confidence, the per-family table, and the largest gaps. As completion
approaches, classify remaining surfaces operationally:

* **MUST:** blocks a core accepted product contract, authority, safety, cleanup,
  or trustworthy suite acceptance;
* **SHOULD:** meaningful supported behavior worth permanent coverage but not a
  release/authority blocker;
* **DEFERRED:** explicitly blocked, rejected, retired, or awaiting a named
  product decision/dependency/experiment;
* **OPTIONAL:** presentation, breadth, or low-value characterization that is not
  currently promised.

A normal concise final report includes:

1. selected feature and why it was highest-value/unblocked;
2. starting/ending commit and final review classification;
3. important product, adapter, or generic-infrastructure changes;
4. fresh autonomous run ID, server/client totals, terminal result, and cleanup,
   or the exact documented stopping gate when runtime proof is inapplicable;
5. important behavior causally proven, disproven, or left unproven;
6. Sacred Texts that materially affected the investigation;
7. generic Arma lemmas/conjectures added, or an explicit zero result;
8. project findings intentionally kept non-generic;
9. remaining boundaries, including client-N/JIP and unavailable dependencies;
10. focused/full/static validation and final worktree state;
11. feature-review and permanent-coverage percentages before/after, ranges,
    confidence, per-family table, and remaining MUST/SHOULD/DEFERRED/OPTIONAL
    surfaces when useful;
12. recommended next candidate without starting it unless requested.

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
