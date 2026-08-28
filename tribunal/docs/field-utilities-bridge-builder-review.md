# Field Utilities Bridge Builder review

Primary review outcome: **REWRITE BEFORE PERMANENT COVERAGE**.

## Behavioral contract

For an alive player within eight metres of a `YFU_Bridge_Box`, ACE resolves the
registered **Open Bridge Builder** action as active. Invoking that exact action
statement opens Bridge Builder, exposes the physical preview plan, and submits
a bounded plan. The dedicated server validates the requester, creates a tagged
server-owned chain of supported bridge segments, publishes a bounded result,
and permits the player to traverse the replicated structure. Removal deletes
only segments created for that construction box and publishes a separate
bounded result. Missing identity, invalid authority, incomplete construction,
failed physical traversal, unrelated-object deletion, or incomplete cleanup is
failure.

This review covers the construction-box entry, lengthwise and wide layouts,
ramps per end, source-matched and world-level orientation, automatic
terrain/building support selection, the 50 metre bound, immutable submitted
plans, preview, server-authoritative build, pedestrian and vehicle traversal,
box-scoped removal, replication to client-a, and cleanup. It does not claim
coverage of interruption/destruction, a genuine second-player contention
attempt, direct segment extension, client-b, disconnect/reconnect, or JIP.

Product decisions recorded on 2026-08-20 define the excluded advanced planning
contract: lengthwise is a narrow end-to-end catwalk; wide is vehicle-capable;
ramp count applies at each end; Keep Level uses world level while Match Box
preserves source tilt; automatic mode stops only on terrain/building support;
slight end embedding is intentional; one server-owned planner lease exists per
box; and the physical span is bounded around 50 metres. Those modes are now
accepted by the fresh proof recorded below. Contention rejection remains
explicitly unproven until a second authenticated client identity is available.

## Canonical review questions

### 1. What should the user or integrator observe?

The shipped construction box and ACE class action establish a coherent entry:
an eligible nearby player sees **Open Bridge Builder**, opens a planning dialog,
sees the proposed bridge in-world, builds it, can cross it, and can remove that
box's bridge. The UI and source also advertise orientation, width, ramp, count,
pitch and automatic planning controls, but those separable capabilities remain
outside this first stable contract.

### 2. What did the feature actually do before review?

The ACE condition correctly rejected dead, distant, building, and removing
states. Dialog and preview logic were reachable and coherent. Construction and
removal ran on the requesting client while using global create/delete commands.
The configured `FootBridge_0_ACR` class did not exist in either the authenticated
client or dedicated runtime, producing `Cannot create non-ai vehicle`; therefore
the positive path could never produce a bridge. Removal searched aligned class
instances without construction-box ownership and could consume unrelated
objects. Direct chain-extension helpers existed, but their attachment function
was empty and no reachable product entry was found.

### 3. Which machines and lifecycle stages own the behavior?

Client-a owns ACE discovery, active-tree evaluation, execution of the exact
registered statement, the dialog, preview and request. The
dedicated server validates `remoteExecutedOwner`, requester identity, life,
class and distance; exclusively creates/removes segments; tags each segment
with box and operation identity; and publishes terminal results. The client
observes nonlocal segment identities and physical collision. This proves only
one authenticated client's request/replication boundary. Client-b and JIP are
explicit future work.

### 4. Which mechanics are generic?

ACE action-adapter mechanics, exact netIds, locality records, spatial sampling
and cleanup reporting are Tribunal concerns. The installed-version adapter
evaluates ACE's active tree and contains no Field Utilities or bridge semantics.
Authenticated RFB/input remains a generic capability for inherently visual
contracts, but the permanent Bridge scenario does not depend on pixels or
camera/menu input.

### 5. Which behavior is product-owned?

Field Utilities owns box eligibility, planning state, supported segment class,
placement geometry, per-segment delay, operation exclusion, the one-planner
lease, requester validation, box-scoped ownership, result lifecycle and
removal semantics. The product does not currently define a resource cost,
persistence policy, or supported contract for direct extension.

### 6. Are unusual engine requirements proven?

No engine workaround is characterized. Runtime inspection proved only that the
legacy class is absent and the Apex `Land_Plank_01_4m_F` class is installed,
constructible and physically collidable. The supported plank has observed model
dimensions 4.1792 m by 0.8982 m by 0.1311 m, so placement uses model-Y length and
model-X width. That is configuration evidence, not a claim that a private
algorithm is engine-required.

### 7. Which details were accidental, fragile, or incomplete?

The absent ACR class, reversed generic length/width interpretation,
client-authoritative world mutation, client-published mutable planning state,
unowned chain discovery/removal, and unbounded result ambiguity blocked
permanent coverage and were rewritten.
Control IDs, screen points, plan-cache layout, request-ID spelling, exact
coordinates and polling cadence remain evidence-adapter details. Direct
extension is **DEFER** because it has no reachable action or coherent ownership
contract. Uncovered planning modes remain implemented-looking but unreviewed.

### 8. Was a better existing mechanism available?

The installed first-party Apex plank is the narrow supported replacement for
the absent ACR asset. Existing ACE interaction remains the real entry rather
than inventing a second menu. Arma remote execution plus server-local creation
provides the authority boundary; no new network service was added. No broader
native bridge-building mechanism was shown to replace the product workflow.

### 9. What is the stable contract and causal proof?

The permanent scenario correlates one run token, box netId, request ID, four
segment netIds and removal result. It proves out-of-range/busy/idle ACE active
states, invokes the exact registered statement, verifies dialog controls and
preview data, server request ownership, exact
class/tag/count, 4.1792 m spacing, direction and height, server locality,
physical player movement over exact segment collision surfaces, wide-layout
vehicle movement against an adjacent fall control, ascent and descent over an
exact ramp chain, terrain/building support observations that reject a nearer
vehicle, removal of all owned identities, survival of a deliberately nearby
untagged control plank, replication, lifecycle reset and cleanup. An internal
result alone cannot pass the traversal or scoped-removal claims.

### 10. Which implementation details remain free to change?

Private SQF function and variable names, cache structure, operation-ID format,
segment class behind an equivalent supported product contract, placement
algorithm, delays, control IDs, sampling thresholds
and result representation may change. The promised behavior is eligibility,
visible planning, validated server authority, usable replicated construction,
box-scoped removal, bounded completion and cleanup.

### 11. Which mechanisms deserve characterization?

None. The review records the failed legacy class as baseline evidence and the
supported class/config measurements as fixture selection. It does not freeze
the old local mutation, direct-extension scaffolding, exact ACE private layout,
or current placement implementation as engine requirements.

### 12. Which mechanics should be promoted into Tribunal?

The generic ACE active-tree adapter is promoted because it is a product-neutral
registration/availability mechanism with this concrete first consumer. The
authenticated real-input driver remains a separate Tribunal compatibility and
visual-evidence tool rather than a dependency of each feature specification.
Bridge eligibility, registered-statement result, dialog meaning, planning,
construction, traversal success and removal meaning remain in the Field
Utilities scenario. Production code has no dependency on Tribunal.

## Classification and permanent coverage

| Subsystem | Classification | Resolution |
| --- | --- | --- |
| construction-box ACE entry | KEEP AS-IS AND SPEC-TEST | registered action plus ACE active-tree out-of-range, busy and eligible states |
| dialog and flat preview | KEEP AS-IS AND SPEC-TEST | registered statement opens dialog; enabled Build control and exact four-item preview state |
| legacy construction asset | REWRITE BEFORE PERMANENT COVERAGE | absent `FootBridge_0_ACR` replaced with installed first-party `Land_Plank_01_4m_F` and explicit dependency |
| build authority/result | REWRITE BEFORE PERMANENT COVERAGE | validated client request, server-only mutation, bounded terminal result |
| physical bridge outcome | REFINE BEFORE PERMANENT COVERAGE | corrected length/width metrics and causal traversal over exact segments |
| removal scope | REFINE BEFORE PERMANENT COVERAGE | box tags and ownership filtering preserve nearby unowned control |
| wide/ramp/pitch/auto/clipping | ACCEPTED / COVERED | immutable server-validated plan; world/source orientation; terrain/building-only endpoint filtering; 50 m cap; wide vehicle and ramp pedestrian physical proofs |
| planner lease | PARTIALLY COVERED | exact server grant/receipt, scheduled dialog, lease-bound submission and cleanup pass; second-player named contention rejection awaits client-b |
| interrupted construction / box destruction | REFINED; ACCEPTED / COVERED | exact accepted client-a request and consumed lease; one-to-five partial identities; builder loss deletes the exact chain and retires the server operation record in `20260828T010359Z-31876e6c` |
| direct chain extension | DEFER | helpers exist but attachment entry is empty and intent/authority are undefined |
| client-b/JIP/concurrency | DEFER | one-client run must not overclaim these boundaries |

The permanent `fieldutils-bridge-builder` Tier 3 scenario is a specification
test owned beside Field Utilities. It deliberately retains the primary review
outcome in `ScenarioReview`: the scenario became admissible only after the
broken positive path and authority model were rewritten.

## False-PASS controls and evidence

The scenario fails on absent action path, wrong ACE version/layout, missing
dialog, disabled Build control, missing request/result, wrong requester,
missing or wrong-class segments, wrong spacing/direction/height, client-local
mutation, inadequate movement, insufficient exact collision samples, missing
removal acknowledgment, surviving owned segments, deleted foreign control,
stale operation flags, missing replication or incomplete cleanup. Every wait is
bounded. The foreign plank is placed close enough to tempt chain discovery and
removal but has no box tag; its survival proves scoping rather than mere empty
cleanup.

Live calibration established once that the generic real-input ACE path opens
the dialog and renders the preview. Permanent feature coverage instead
evaluates ACE's active tree, invokes that exact registered statement and
observes a fresh `bridge-build-*` request.

Fresh cold run `20260815T172201Z-cda47faf` passed 24/24 assertions with zero
failures and complete container/network/state cleanup. Its token was
`gameplay-20260815T172201Z-cda47faf-5c8694385775`; mission SHA-256 was
`4209f1a3e4d2d1aea46325f3a0d7160cb58731c47d98f86543f608a231be347a` and
PBO SHA-256 was
`2acdc03eb899c60daff6eeb364832ec8f4ab6c1125eb52524671cae1efa4715f`
with a valid deterministic footer. The server created four tagged local
segments at 4.18203/4.18007/4.178 m spacing. Physical traversal produced 101
exact segment-contact samples; all four owned netIds were removed, the nearby
untagged control survived until fixture cleanup, and client/server cleanup
acknowledgment completed.

Fresh autonomous run `20260820T213913Z-d70d2c4f` passed the expanded matrix:
17 server assertions and 14 client assertions, zero failures, with client,
server, network and run-state cleanup all complete. Its planner receipt bound
the granted lease ID to client owner 4 before the dialog opened and the build
accepted the versioned immutable plan. The wide quadbike advanced 11.50 m over
the exact 16-segment deck with 69 contact samples while the adjacent no-bridge
control fell 9.27 m. The ramp player advanced 29.29 m, rose from 2.00 m to a
4.48 m peak, descended to 0.50 m, remained within 0.0011 m laterally, and
recorded 436 exact ramp contacts. Automatic planning observed a nearer MRAP at
7.26 m, ignored it, and selected the building support at 19.71 m; the same ray
also observed terrain support farther along. All 25 advanced fixture segments,
both test vehicles, and both boxes were retired before terminal PASS.

## Security and compatibility

The permanent Bridge proof requires no VNC actor. The optional generic visual
adapter still connects only to Weston's authenticated loopback endpoint inside
the confined client namespace. Nothing publishes VNC, weakens TLS, exposes
host X11/D-Bus, adds capabilities, or changes AppArmor, seccomp,
no-new-privileges, Steam/CEF or namespace confinement. The only new official
content dependency is the already-enabled first-party Apex accessories addon.

## Next review

Review the now-unblocked APS operation/control lifecycle next. Bridge
second-player contention, interruption/destruction, client-b/JIP, and direct
extension remain explicit follow-ups rather than being inferred from this
one-client proof.

## B3 candidate continuation — interrupted construction

Source review found one concrete abnormal-lifecycle defect. The build worker
stopped iterating when its construction box became null, but its terminal block
also required that box to remain non-null. Segments created before destruction
therefore remained as an orphan partial chain, while the box-local operation
state disappeared and left no authoritative way to prove finalization.

The candidate refinement registers each accepted build by exact request ID in a
server-local active-operation map. Normal completion, incomplete creation, and
construction-box disappearance all retire that entry. On disappearance the
worker deletes every segment it created before retiring the operation. The
planner lease remains consumed at accepted submission, before any segment is
created, so deletion cannot leave a renewable lease attached to an ongoing
operation.

The expanded permanent scenario uses the same independently authenticated
client-a transport as the normal build. It obtains an exact planner grant,
submits a six-segment immutable plan through `YFU_bridge_startBuildFromPlan`,
and waits for the server to observe the accepted operation, consumed lease,
exact registry row, and between one and five operation-tagged segments. Only
then does the server delete the exact builder box. The new assertions require
all captured segment netIds to disappear and the exact registry key to retire
within a bounded cleanup interval. This excludes deletion before acceptance,
an empty-chain false pass, normal completion, unrelated cleanup, and result-only
success.

Fresh serialized run `20260828T010359Z-31876e6c` passed
`bridge.interruption.request`, `bridge.interruption.cleanup`, the complete
pre-existing Bridge matrix, and smoke with 15/15 client and 18/18 server
assertions. Cleanup completed and `evidence-package.v1.json` validated against
Evidence Contract v1. Rejected diagnostic `20260828T005936Z-68c28e96` proved
the request, lease, partial-chain, and registry preconditions but caught a
cleanup code block that was constructed rather than executed; it is retained
only as calibration, not accepted evidence.
Package `urn:tribunal:evidence-package:20260828T010359Z-31876e6c:1`
(file SHA-256
`2f0b500c99e80004812fbe375c6599ae651b7fb94c0d5e48e98912fd55452249`)
was ingested twice: production counts advanced once from 32 to 33 packages and
33 to 34 runs, then remained identical. The full knowledge audit passed.
Reviewed distillation remained at 32 findings, 19 project-only dispositions,
7 generic lemmas, 1 generic conjecture, and 5 needs-characterization items on
both passes; this Bridge result added no generic Arma claim. Post-ingestion
offline dossiers expose the two bounded Bridge theorems while `deleteVehicle`
continues to report only its existing documented next-frame deletion behavior.
Resource consumption and refunds still have no product contract and remain
**NEEDS PRODUCT DECISION**. Second-player contention, client-B/JIP,
disconnect/reconnect, interruption during removal, and direct chain extension
remain explicitly unclaimed.
