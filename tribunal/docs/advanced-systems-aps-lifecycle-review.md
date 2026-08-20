# Advanced Systems APS install/disable/re-enable lifecycle review

## Scope and result

This review covers the shared APS lifecycle tail used by Eden/Zeus activation:
first enable, repeated enable, disable, re-enable, action registration, transient
work, resources, preferences, and deletion. It does not re-review projectile
combat, ACE operator authority, module dispatch, or anti-drone behavior.

**Classification: `REVIEWED / DEFERRED AS A STANDALONE FEATURE;
ENTRY-CONSUMER-OWNED`.**

A direct lifecycle-API scenario would bypass the authentic module/control entry
that gives install/toggle meaning. The unresolved behavior is consequential:
every enable tops hard-kill cargo to the target/default, turns voice and
anti-drone on, selects hard kill, and turns soft kill off. Thus OFF→ON is
currently also resupply and preference/mode reset, not a neutral resume.

## Canonical twelve-question review

1. **What should the user observe?** Authentic first installation makes one
   exact vehicle operational. Disable stops APS and removes its controls. A
   later enable restores operation according to an explicitly chosen resource
   and preference policy, without duplicate actions/workers or leaked effects.
2. **What does it do now?** Enable validates server/non-null/vehicle, tops up
   charges, resets voice/anti-drone/hard/soft and warning flags, ensures global
   runtime, starts a drone worker, and persistently registers object actions.
   Disable cancels voice, terminates drone work, clears modes, and persistently
   unregisters actions. Toggle chooses from the local enabled flag and ignores
   callee failure in its returned choice.
3. **Which machines own it?** Vehicle state and lifecycle mutation are
   server-owned; action add/remove is client-local through object-keyed
   persistent remote execution. The mission-wide projectile tracker starts on
   every machine after mission time independently of vehicle enable and is not
   removed by disable. Authentic request authority belongs to module/control
   entries.
4. **Which mechanics are generic?** Exact active ACE tree census, persistent
   registration receipts, script/source cleanup, vehicle deletion observation,
   and current-client/JIP delivery can be Tribunal mechanics. APS resource/mode
   policy is Advanced Systems.
5. **Which behavior is product-owned?** Suspend versus uninstall versus reload;
   repeated-enable idempotence; charge/fuel preservation or resupply; mode/voice
   preference reset; deletion cleanup; and supported ownership/JIP lifecycle.
6. **Are unusual engine requirements proven?** No. Current-client action
   registration/removal, persistent JIP-key replacement, re-enable uniqueness,
   object-deletion cleanup, and ownership transfer have no direct proof. The
   global tracker may reasonably be mission-lived, but no contract requires its
   present PFH/class-handler representation.
7. **What is fragile or incomplete?** Re-enable silently replenishes spent
   charges and erases operator choices. Repeated Eden enable does the same.
   Disable has weaker type validation. Toggle can report a transition when its
   server-only callee did nothing. Stored script handles and local action flags
   can drift from actual workers/tree. Anti-drone work is entangled despite its
   product contract being deferred.
8. **Is a better mechanism available?** Keep the shared server lifecycle tail,
   but distinguish first install, temporary suspension, and explicit resupply/
   reset if product semantics require it. The real module/control endpoint
   should validate and acknowledge the selected operation. Do not add a second
   standalone lifecycle command surface.
9. **What is the stable contract and causal proof?** Through authentic entries,
   first install has exact initial resources/state and one active action tree;
   OFF causes the same calibrated threat to impact with resources unchanged and
   exact APS nodes removed; ON restores the selected resource/preference state,
   one tree, and exact interception. Voice/source/worker cleanup is bounded.
   Unrelated vehicles/actions remain unchanged. Repeat/replay and deletion leave
   no vehicle-scoped effects.
10. **Which details remain free?** Function names, flags/handles, tracker
    implementation, JIP key, action IDs/layout, worker representation, default
    counts, and receipt schema are replaceable behind chosen semantics.
11. **Which mechanisms deserve characterization?** Current-client persistent
    register/unregister/re-enable ordering and exact active-tree uniqueness.
    Client-B/JIP and ownership migration wait for the existing second-identity
    dependency. Global tracker teardown is not a goal absent measured cost.
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

## Decisions and continuation

Decide whether disable is suspension, uninstall, or reload; whether repeated/
re-enable preserves or resets charges, fuel, hard/soft mode and voice; whether
enabling an enabled vehicle is idempotent, reset, or rejection; and deletion/
owner-migration support.

Fold proof into the authentic APS module and control refinements: typed first
install, authenticated Zeus OFF, second authenticated ON, exact current-client
ACE removal/re-add, calibrated impact/interception pair, resource/preference
assertions, repeat/replay, unrelated-vehicle isolation, and enabled-vehicle
deletion cleanup. Keep client-B/JIP explicitly deferred.
