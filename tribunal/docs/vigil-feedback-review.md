# Vigil radio, chat, debug, and curator feedback — canonical feature review

Primary outcome: **REVIEWED / NEEDS PRODUCT DECISION; PRESENTATION
EXPERIMENT DEFERRED**.

This review covers Vigil's CORDIS-backed feedback wrappers and their real task
consumers. It does not reopen the accepted artillery, transport, CAS, or
fixed-wing physical outcomes, the reviewed module authority boundaries, or
CORDIS routing/deduplication itself.

## Twelve-question review

1. **What should the user observe?** Accepted support tasks can announce
   acknowledgment, release, failure, abort, or completion. Debug messages are
   always written to the server log and optionally mirrored to client
   `systemChat`. Curator tools attempt to report their result. The intended
   recipient set is not documented consistently enough to be a stable promise.
2. **What does it do now?** Transport, artillery, and CAS emit configured radio
   classes at real lifecycle boundaries. Fixed-wing paths emit side-chat
   status. Module handlers use curator notifications. Thin Vigil wrappers pass
   a CBA setting name to CORDIS; debug always logs and conditionally broadcasts
   `systemChat`.
3. **Which machines own it?** Consequential task state remains server-owned.
   CORDIS resolves recipients server-side and invokes presentation on target
   clients. Every Vigil radio/chat caller currently omits scope, so scope `0`
   resolves all live players. Curator notification also falls back from an
   empty resolved scope to all live players. Target-client setting gates are
   globally synchronized CBA policy.
4. **Which mechanics are generic?** Recipient resolution, dedupe, destination
   receipts, target-local radio/chat observation, RPT capture, and audio
   observation are CORDIS/Tribunal concerns. Message meaning and lifecycle
   placement are Vigil-owned.
5. **Which behavior is product-owned?** Vigil owns which task transition merits
   which acknowledgment, who should receive it, whether transport's per-task
   radio flag coexists with the global setting, and whether curator feedback is
   requester-only, curator-wide, side-wide, or global.
6. **Are unusual engine requirements proven?** No. The autonomous client uses
   `-noSound`, so actual audibility is unproven. No controlled evidence shows
   how `sideRadio`/`sideChat` should scope across sides after explicit remote
   delivery, or that the current all-player fan-out is required.
7. **What is fragile or incomplete?** Wrapper success means queued/claimed, not
   presented. Default all-player scope may leak feedback. Empty curator scope
   becomes a global fallback. Most calls omit once keys, so dedupe is absent.
   Exact prose and fixed-wing ETA truth are separate consumer concerns. Debug
   accepts client-originated text and broadcasts presentation when enabled.
8. **Is a better mechanism available?** Keep CORDIS transport, but first choose
   an audience and require request/task-correlated destination receipts for any
   delivery promise. Task feedback should use the authoritative requester/task
   identity rather than implicit scope `0`. Curator results should target the
   authenticated placing curator once module authority is refined.
9. **What is the stable contract and causal proof?** After an independently
   proven real task transition, enabled feedback reaches exactly the selected
   recipients once and disabled feedback reaches none without changing the
   task outcome. A target-local delegating observer must record recipient,
   speaker, message identity, setting, and order. Negative controls must repeat
   the same physical task stimulus. Debug requires a unique server RPT token
   and, when enabled, an independently observed client presentation.
10. **Which details remain free?** Exact prose, sound files/titles, wrapper
    names, remote-execution shape, TTL, logging prefix, and presentation command
    remain replaceable. Lifecycle meaning and recipient policy do not.
11. **Which mechanisms deserve characterization?** After the audience decision,
   reuse accepted artillery for enabled/disabled acknowledgment/completion and
   accepted fixed-wing strike for side-chat. A second independently
   authenticated side/client is required before claiming side isolation.
   Audibility requires a sound-enabled observer; invocation alone is not sound.
12. **What belongs in Tribunal?** A delegating target-local feedback observer
   and recipient/order receipts may be generic. Do not move Vigil message
   classes, task transitions, or audience policy into Tribunal.

## Current evidence and false-PASS boundary

Accepted task scenarios prove the physical/task states that contain feedback
calls, but none records target-local radio/chat presentation. CBR has a useful
observer precedent, not Vigil coverage. Registered `CfgRadio` metadata, a
wrapper return, a CORDIS claim, server task success, a screenshot, or receipt by
any one client cannot prove correct delivery or audience. Disabled silence is
meaningful only when the same valid task transition independently occurred.

Debug semantics are accurately documented and statically covered by the
cross-addon CBA settings contract: server logging is unconditional and the
setting adds `systemChat`. That does not establish recipient policy or make
arbitrary debug traffic a supported user feature.

## Decisions and continuation

Choose separately for task radio/chat and curator feedback: requester only,
requester side, asset side, assigned curators, or all players. Decide whether
transport's `_playRadio` is supported per-task policy and whether exact
acknowledgment/completion identities are stable. Until then, do not fossilize
scope `0` as specification.

After a decision, instrument the target-local CORDIS presentation function in a
real accepted artillery task, require acknowledgment then completion for the
chosen recipient set, repeat with the setting disabled, and restore the hook.
Use fixed-wing only for the side-chat slice. Defer audible output and true
multi-side isolation until sound-enabled and second-identity dependencies are
available. Curator feedback remains part of each module's authority review.
