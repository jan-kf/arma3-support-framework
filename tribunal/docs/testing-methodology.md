# Tribunal testing methodology

Tribunal separates the behavior a project promises from the mechanics used to
prove it. Existing code is evidence: it is neither presumed correct nor
presumed obsolete. A permanent test must say which boundary it protects.

## Taxonomy

### Specification tests

Specification tests protect behavior that users or mod authors may rely on
through a refactor. They assert externally meaningful inputs, outcomes,
controls, cleanup, locality, and replication. Private function names, variable
layouts, arbitrary ordering, fixture coordinates, and helper implementation
are evidence-adapter details and must not appear in `behavior_contract`.

### Characterization tests

Characterization tests preserve a mechanism only after a controlled experiment
shows it is engine-imposed, deliberately architectural, or materially safer
than alternatives. Every characterized behavior records description, reason,
evidence, alternative tested, and outcome. “The current code does this” is not
enough. With no A/B evidence, classify the question as `NEEDS EXPERIMENTATION`
and keep the feature test at the specification boundary.

### Tribunal tooling tests

Tooling tests protect reusable mechanics such as deterministic projectile
launch, weapon-fire observation, locality transfer, input, framebuffer capture,
marker/trajectory/spatial evidence, network profiles, and result parsing. These
tests live in Tribunal and contain no project semantics.

### Feature integration/gameplay tests

Feature-owned tests sit beside feature source and use Tribunal mechanics to
prove a specification. The fixture may reference private APIs to reach or
observe the behavior, but those names are not themselves the contract. A
project production mod never depends on Tribunal.

## Feature review procedure

Before substantial permanent coverage, write a short review that answers:

1. What should the user observe?
2. What does the feature do now, including negative paths?
3. Which machines and code paths implement it?
4. Which mechanics are generic Arma, ACE, or CBA behavior?
5. Which behavior is project-specific?
6. Which unusual details have controlled evidence that they are required?
7. Which details look accidental, legacy, fragile, or need experimentation?
8. Is a better native mechanism available, and has it been proven?
9. What is the stable behavioral contract?
10. Which implementation details must remain free to change?
11. Which mechanisms genuinely deserve characterization?
12. Which repeated mechanics should be promoted into Tribunal?

Assign one outcome: `KEEP AS-IS AND SPEC-TEST`, `KEEP + CHARACTERIZE ENGINE
REQUIREMENT`, `REFINE BEFORE PERMANENT COVERAGE`, `REWRITE BEFORE PERMANENT
COVERAGE`, `NEEDS EXPERIMENTATION`, or `DEFER / insufficient value`. Proposals
to replace working code require a controlled comparison before implementation.

The workflow is:

```text
feature -> review -> behavioral contract -> generic tools
        -> experiment/refine uncertain mechanics
        -> specification tests (+ evidence-backed characterization only)
        -> Live iteration -> fresh autonomous proof -> commit
```

`ScenarioReview` is intentionally small. It records the primary test type,
contract, outcome, rationale, dependencies, evidence types, locality, and any
evidence-backed characterization. Detailed engineering notes remain here or in
feature documentation rather than growing a general-purpose schema.

## Existing coverage audit

| Area | Stable specification | Evidence adapters, not specification | Outcome |
| --- | --- | --- | --- |
| APS | qualifying inbound threat is stopped; disabled/outside/away controls are not; hard/soft resources change correctly; protected state replicates | direct-injection coordinates/speed, private tracker name, ledger representation, polling cadence | KEEP AS-IS AND SPEC-TEST |
| Vigil UI | intended client opens, visibly navigates, closes, cleans up, and reopens in default state; server has no display | IDCs, `uiNamespace` keys, input coordinates, screenshot thresholds | KEEP + CHARACTERIZE ENGINE REQUIREMENT |
| Vigil markers | valid request count/position changes visible preview; stale preview is replaced; clear/close removes it; server has no preview | generated marker names, backing-array layout, exact probe pixels | KEEP AS-IS AND SPEC-TEST |
| Vigil artillery | grid request produces exact round count and circle/line geometry; invalid/range/ammo controls do not fire; VLS physically launches/guides/arrives | governor variables, private submit/parser names, Fired-event ordering, observer sample rate | KEEP AS-IS AND SPEC-TEST |

### APS findings

Hard kill, soft-kill deflection, physical disabled impact, outside-envelope and
direction-away controls, exact projectile correlation, authoritative state,
locality, charge/fuel behavior, and replication form a causal specification
suite. The engagement ledger is valuable authoritative evidence but its array
shape is not promised. Threat-fixture geometry and explicit tracking are
Tribunal/adaptor necessities, not APS behavior. No APS production mechanism is
newly characterized or rewritten by this audit.

### Vigil UI findings

Open/tab/close/reopen assertions are user-visible and paired with framebuffer
evidence. Client/server locality is part of the feature contract. Control IDs
and state keys merely anchor that evidence. One Arma-specific mechanism is
eligible for characterization: on this build, calling the unmodified open API
from the same scheduled worker that observed Escape-driven display destruction
did not recreate the dialog, while a fresh scheduled worker did. The retained
test records the prior controlled outcome rather than generalizing it to all UI
code. The audit also corrected the generic reopen observer: a bright terrain
strip could resemble the initially selected tab, so reopen now requires both
the tab anchor and a material full-frame transition from the closed game
surface.

### Vigil marker findings

The suite correctly combines rendered evidence with backing state so a stale
or unrelated image cannot pass. Exact internal marker registration, ellipse
shape, and size help prove that the rendered preview is the intended product
object; they are not named in the stable contract and may change with the
adapter if the UI is refactored. During this audit, combined-suite runs exposed
an order dependency: the marker fixture inherited the preceding artillery
scenario's line/spread/direction state, while its isolated run started with
circle defaults. The fixture now establishes its own geometry. No product
rewrite, timing expansion, or assertion weakening was needed.

### Vigil artillery and VLS findings

Round counts, physical shells, spatial geometry, controls, locality, cleanup,
and full VLS flight are specification evidence. `ArtilleryShellFired`/`Fired`
correlation and waterline platform stabilization are Tribunal fixture concerns.
Vigil currently creates a temporary VLS target, reports it to the launcher
side, confirms it, and calls `fireAtTarget`. This handshake is a
characterization candidate, not yet a characterized contract: no retained
controlled A/B proves that direct fire necessarily launches vertically without
guidance on the current engine build. The permanent test therefore requires
physical guidance/arrival but does not freeze the handshake. A future isolated
A/B may promote it to characterization with artifacts.

## Generic Tribunal capability backlog

Already generic: deterministic PBO packaging; assertion/result protocol;
direct projectile launch; artillery/weapon-fire trajectory observation;
spatial evidence; locality transfer; remote execution; authenticated
framebuffer/input; map/marker observation; evidence attachments; named network
profiles.

Promote only on first concrete consumer or clear reuse:

1. ACE interaction discovery/activation;
2. vanilla action-menu discovery/activation;
3. reusable spawn/settle and damage probes;
4. AI creation/tasking and vehicle movement/landing evidence;
5. module synchronization/Eden-like fixtures;
6. weapon selection and real fire;
7. opt-in audio and animation evidence.

## ACE interaction recommendation

`AceInteractionRequest` is the product-neutral prototype: actor identity,
target identity, external/self type, action path, expected availability, and
whether to activate. It intentionally has no Pontifex action names.

ACE's official framework says scripted action registration is client-side,
passes `[_target, ace_player, actionParams]` to condition/statement, and does
not automatically include `ace_common_fnc_canInteractWith`. ACE's internal
`collectActiveActionTree` evaluates modifier, condition, dynamic children, and
object/class children; its key-release path rechecks the condition immediately
before running the statement. Both functions are marked private by ACE.

Therefore the recommended executor has two layers:

1. an ACE-version adapter on the actor client enumerates the same active tree,
   records action IDs/path/display names, and verifies the requested action is
   genuinely actor-available (including global can-interact, distance/LOS/menu
   context, action condition, modifiers, and dynamic children);
2. authenticated framebuffer/input opens the real ACE menu and selects the
   verified path; the adapter records the selected callback and the feature
   test independently verifies resulting world state.

Directly calling an action statement is permitted only as a lower-level
tooling probe and must not be called real-user interaction. Depending on ACE's
private arrays should be isolated behind a version check and fail closed when
the installed ACE layout differs. First runtime consumer should be a small
Field Utilities bridge action: assert absent while out of range/busy, present
when alive and within 8 m, activate “Open Bridge Builder” with real input, then
assert the dialog/preview separately.

Primary references for that design are ACE's
[Interaction Menu framework documentation](https://ace3.acemod.org/wiki/framework/interactionmenu-framework.html),
the private
[`collectActiveActionTree`](https://github.com/acemod/ACE3/blob/master/addons/interact_menu/functions/fnc_collectActiveActionTree.sqf)
implementation, and the private
[`keyUp`](https://github.com/acemod/ACE3/blob/master/addons/interact_menu/functions/fnc_keyUp.sqf)
activation path. The version adapter, rather than feature tests, owns any future
compatibility work caused by changes to those private functions.

## Preliminary review of next feature families

| Priority | Family | Preliminary outcome | Review focus before coverage |
| --- | --- | --- | --- |
| 1 | Helicopter transport/reinsertion | NEEDS EXPERIMENTATION | destination contract, dispatch/landing/wait/RTB states, AI locality, terrain-safe LZ, native task alternatives |
| 2 | Rotary-wing CAS | NEEDS EXPERIMENTATION | hostile selection, friendly exclusion, attack evidence, loiter duration, ammunition and RTB behavior |
| 3 | Fixed-wing strike support | REFINE BEFORE PERMANENT COVERAGE | synchronized asset serialization, ingress/loiter/egress, laser and weapon-IR designation, loadout replacement, actual weapon/ammo compatibility |
| 4 | Fixed-wing logistics | NEEDS EXPERIMENTATION | manifest authority, cargo construction, parachute deployment, delivery accuracy, cleanup/egress |

Helicopter transport is next because it exercises reusable AI tasking,
movement, landing, and lifecycle evidence without first requiring the deeper
munition-compatibility review needed by fixed-wing support. This document does
not authorize implementing those features; each begins with its own review.
