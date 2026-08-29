# Advanced Systems APS install/disable/re-enable lifecycle review

## Scope and result

This review covers the shared APS lifecycle tail used by Eden/Zeus activation:
first enable, repeated enable, disable, re-enable, action registration, transient
work, resources, preferences, and deletion. It does not re-review projectile
combat, ACE operator authority, module dispatch, or anti-drone behavior.

**Classification: `REFINED; ACCEPTED / COVERED THROUGH THE AUTHENTIC ACE
CONTROL ENTRY` for current-client suspension/resume.** First typed Eden install,
Zeus module dispatch, client-B/JIP, ownership migration, and destruction cleanup
remain owned by their separate entry/lifecycle reviews.

Disable is now an idempotent temporary suspension. First installation alone sets
default modes and tops up configured hard-kill charges. Resume does not resupply,
reset modes/preferences, or replace the action tree; it restarts only the runtime
work enabled by preserved state.

## Canonical twelve-question review

1. **What should the user observe?** Authentic first installation makes one
   exact vehicle operational. Disable temporarily suspends interception while
   leaving an eligible operator a Resume control. Resume restores operation with
   the same modes, preferences, charges, and fuel—never an implicit resupply.
2. **What does it do now?** Enable distinguishes first installation from resume.
   First install alone initializes defaults/resources and registers the tree.
   Suspension cancels transient voice/drone work and clears only active state.
   Resume preserves hard/soft, voice, anti-drone, charge, and fuel state, restarts
   applicable work, and reuses the idempotent action registration. Lifecycle
   mutation rejects client-origin calls outside the authenticated operation path.
3. **Which machines own it?** Vehicle state and lifecycle mutation are
   server-owned; action add/remove is client-local through object-keyed
   persistent remote execution. The mission-wide projectile tracker starts on
   every machine after mission time independently of vehicle enable and is not
   removed by disable. Authentic request authority belongs to module/control
   entries.
4. **Which mechanics are generic?** Exact active ACE tree census, request
   receipts, state snapshots, script/source cleanup, vehicle deletion observation,
   and current-client/JIP delivery can be Tribunal mechanics. APS resource/mode
   policy is Advanced Systems.
5. **Which behavior is product-owned?** Disable is temporary suspension; repeated
   enable/disable is idempotent; charges, fuel, hard/soft mode, voice, and anti-drone
   preference are preserved; first installation alone applies defaults/resupply.
   Deletion cleanup and supported ownership/JIP lifecycle remain product-owned.
6. **Are unusual engine requirements proven?** The current-client tree and
   mutually exclusive Suspend/Resume nodes are proven through ACE 3.21. Persistent
   JIP-key delivery, object-deletion cleanup, and ownership transfer remain
   unproven. The global tracker may reasonably be mission-lived, but no contract
   requires its present PFH/class-handler representation.
7. **What is fragile or incomplete?** Stored script handles and local action
   flags remain diagnostics, not proof. Authentic Eden/Zeus dispatch, deletion,
   ownership transfer, and JIP behavior are not established. Anti-drone threat
   semantics remain deferred even though its preference is preserved correctly.
8. **Is a better mechanism available?** The shared server lifecycle now
   distinguishes first install from suspension/resume. The authenticated ACE
   operation endpoint validates and acknowledges the transition; no second public
   lifecycle command surface was added.
9. **What is the stable contract and causal proof?** Through exact active ACE
   nodes, suspension preserves modes/preferences/resources and makes the same
   calibrated threat impact with no ledger event or consumption. Resume preserves
   the snapshot and lets the same threat be exactly intercepted with one charge
   consumed. Duplicate resume is harmless and replay is rejected. Typed install,
   deletion, and JIP are not claimed by this proof.
10. **Which details remain free?** Function names, flags/handles, tracker
    implementation, JIP key, action IDs/layout, worker representation, default
    counts, and receipt schema are replaceable behind chosen semantics.
11. **Which mechanisms deserve characterization?** Typed Eden first-install
    dispatch, enabled-vehicle destruction, client-B/JIP, and ownership migration
    remain. Global tracker teardown is not a goal absent measured cost.
12. **What belongs in Tribunal?** Reuse the ACE active-tree/locality/cleanup
    observers. Keep APS lifecycle state/resources and module/control entry
    meaning in Advanced Systems scenarios.

## False-PASS boundary

Direct enable/disable/toggle calls prove only the tail and are not admissible
entry evidence. `YOSHI_APS_Enabled`, scriptNull handles, local actions-added flag,
persistent remoteExec state, charge count, or no engagement alone cannot prove
cleanup or transition. Every physical phase needs a valid exact threat. Exact
active-tree census must distinguish absent delivery from successful removal.
Re-enable must assert the chosen pre/post resource and preference policy so a
silent refill/reset cannot accidentally pass.

Do not use anti-drone state/effects to prove lifecycle correctness. Do not call
client-a re-registration JIP coverage.

## Acceptance evidence and continuation

The author selected temporary suspension, state/resource preservation, no implicit
resupply, idempotent enable/disable, and anti-drone enabled only on first install.
Fresh run `20260820T222348Z-a22110d3` proved the current-client control entry: the
pre-suspend snapshot survived suspension and resume exactly across hard/soft mode,
voice, anti-drone preference, zero charges, and fuel; the off threat impacted and
the resumed/rebooted threat was intercepted; duplicate resume and replay were
bounded. Server 18/18 and client 10/10 passed with full cleanup.

Next lifecycle work belongs to authentic APS Eden/Zeus module activation: prove
typed first install, multiple-module idempotency/aggregation, curator authorization,
and current-client tree consistency. Keep client-B/JIP and destruction cleanup
explicitly deferred until those entry paths and dependencies are available.
