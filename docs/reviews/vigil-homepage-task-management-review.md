# Vigil homepage task-management review

## Scope and result

This review applies the canonical feature-review program to the dormant Vigil
homepage task list, row selection and cancellation helpers in
`functions/tablet/fn_homepage.sqf` and `ui/pages/page_home.hpp`.

**Classification: `RETIRE / REMOVE CANDIDATE` (reviewed; unreachable legacy
scaffold; not covered and no longer needed for the resolved task display).**

The entire page class is commented out, page registration is commented out, the
dialog does not include the page, and no shipped caller reaches its functions.
Even if invoked directly, the client renderer rejects the authoritative
governor's hashmap as the wrong type and clears the list. Cancellation is local,
uses only vehicle identity, and does not drive the governor into its finalizer.
No repository documentation establishes the missing visibility, authorization,
history or cancellation policy. Runtime coverage would invent a feature by
bypassing its absent entry.

The later resolved task-queue decision deliberately did not revive this page.
Reachable Assets-page controls now provide lightweight per-asset active status,
bounded recent history, and the cross-tab operational overlay proven by
`vigil-task-queue`. The old homepage's broad list/navigation/cancel scaffold
therefore remains legacy removal work, not unfinished task visibility.

## Canonical review

### 1. User or integrator observation

There is no current user observation. The commented UI suggests a table of
governor tasks with refresh and cancel controls, but it is neither registered
nor present in the shipped tablet. The inventory's earlier claim that it
“navigates to a selected task” has no implementation evidence.

### 2. Current behavior and negative paths

`YSF_home_tasks` expects an array and replaces every other shape with `[]`.
`YSF__mgr` returns the server-local hashmap of vehicle-keyed manager records, so
the would-be client list is always empty. The renderer also expects task fields
at the row object while the live registry nests them under each record's `task`.
The double-click helper treats scalar `lbCurSel` as a two-element array, which
HEMTT correctly reports as invalid. No refresh, empty, stale or error state is
reachable through the product.

### 3. Authority, locality and lifecycle

The governor and its registry are server-local; clients have an independent
empty registry. The homepage calls `YSF_taskCancel` locally with a vehicle and
has no request, requester validation, task generation, acknowledgment or
replicated snapshot. Direct server cancellation only sets state to `cancelled`.
The governor then exits early for a non-running task unless it is already in the
FINALLY stage, so this path can skip finalization and strand its manager.

### 4. Generic mechanics

Table/list rendering, registered page/action discovery, exact task identity,
request receipts and cleanup observation are generic mechanics. Task visibility,
authorization, cancellation policy and history remain Vigil semantics. No new
Tribunal primitive is justified for unreachable code.

### 5. Product-owned behavior

Vigil must decide whether the page ships; which task families and history it
shows; who may see and cancel which task; which stages are cancellable; how an
exact task generation is addressed; and how server snapshots, acknowledgment,
JIP and retention work.

### 6. Claimed engine requirements

There are no engine requirements or workarounds to characterize. All blockers
are repository reachability, data contract and lifecycle issues.

### 7. Fragile or incomplete details

Commented UI/registration, incompatible collection shape, nested-record mismatch,
invalid selection typing, vehicle-only row identity, client-local cancellation,
missing authority/result and broken finalization make this a scaffold rather
than a partially working feature.

### 8. Better native or existing mechanisms

No implementation mechanism should be selected before product decisions. A
future page should consume a deliberate server-authored DTO/snapshot and issue
an exact authenticated cancellation request rather than reading private
governor maps from the client.

### 9. Stable contract and causal proof

No stable current contract exists. If revived, proof must start from the real
registered page, correlate exact server task ID/generation and vehicle to each
row, send an authorized cancel, observe server acceptance, enter FINALLY exactly
once, run task cleanup and show the chosen terminal/retired state. A second task,
stale-generation request, foreign requester, repeated cancel and terminal task
must remain unaffected or be explicitly rejected.

### 10. Replaceable implementation details

Control IDs, columns, registry/DTO layout, refresh transport, navigation and
row styling are free. Only a future visible task/cancellation outcome could
become specification.

### 11. Characterization

Nothing is characterized. The commented code is historical evidence, not an
engine-imposed mechanism.

### 12. Tribunal promotion

None. Reuse existing UI-state, authority and lifecycle evidence after a real
product entry exists. VNC is needed only if visual layout becomes contractual;
data should prove task identity and cancellation.

## Resolved authority disposition

The active/history/display and authority questions are resolved by the
lightweight Assets-page contract. Any legitimate same-side Vigil tablet user may
queue a task or explicitly overwrite the active generation after confirmation.
That exact-generation overwrite is the supported cancellation operation.
Vigil has no separate standalone remote-cancel product requirement. Disconnect,
JIP, and simultaneous-client proof remain shared topology boundaries rather
than an authority-policy decision.

## Precise continuation point and false-PASS boundary

Do not uncomment the page and do not add a standalone cancel control merely to
revive its semantics. The accepted confirmed Replace transaction is the
reachable authenticated cancellation path. A fabricated client list, direct
server helper call, local `cancelled` flag, empty table or handler-return
`YSF_R_CANCEL` would all bypass that public path and cannot count as proof.

## Terminal disposition

The homepage task surface remains removed from the product and is now an
explicit retirement candidate. The lightweight replacement is separately
accepted; no coverage should be added solely to preserve this scaffold.
