# Vigil radio, chat, debug, and curator feedback — canonical feature review

Primary outcome: **SPLIT**. Task radio/chat and curator feedback remain
**REVIEWED / NEEDS PRODUCT DECISION; PRESENTATION EXPERIMENT DEFERRED**. The CAS
auto-engage debug channel is **REFINED; ACCEPTED / COVERED** for unconditional
server logging plus the registered Vigil debug setting as the one-client
presentation gate.

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
   clients. Every Vigil radio/chat caller uses default or explicit
   scope `0`, which resolves all live players. Curator notification also falls back from an
   empty resolved scope to all live players. Target-client setting gates are
   globally synchronized CBA policy.
4. **Which mechanics are generic?** Recipient resolution, dedupe, destination
   receipts, target-local radio/chat observation, RPT capture, and audio
   observation are CORDIS/Tribunal concerns. Message meaning and lifecycle
   placement are Vigil-owned.
5. **Which behavior is product-owned?** Vigil owns which task transition merits
   which acknowledgment, who should receive it, whether transport's internal
   per-task-data radio override coexists with the global setting, and whether curator feedback is
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

Generic wrapper semantics are documented and statically covered by the
cross-addon CBA settings contract: server logging is unconditional and the
setting adds `systemChat`. The CAS auto-engage adapter previously bypassed that
contract through a separate unregistered gate hardcoded true; the accepted
continuation below supersedes this paragraph for that exact channel. It does not
make arbitrary debug traffic a supported user feature.

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

## Accepted continuation — CAS auto-engage debug channel

The next-best unblocked candidate was the CAS auto-engage diagnostic adapter.
The Opus reconnaissance was used only as a pointer. Canonical source established
that `fn_airAutoEngage.sqf` is a pre-init function, assigns
`YSF_AAE_DEBUG = true` on every machine, and passes that unregistered name to
CORDIS as the target-local presentation gate. CORDIS always writes the server
line, remotely invokes its client function on all machines, and lets that named
variable decide whether to execute `systemChat`. Vigil's supported global CBA
setting is instead `YSF_showDebugMessages`, default false. Thus the old adapter
always exposed AAE traffic to client chat and could not be controlled through
the documented setting.

Pontifex now removes the private hardcoded gate and passes
`YSF_showDebugMessages` to the existing CORDIS adapter while retaining the
distinct `YSF_AAE` log prefix. Its no-CORDIS last fallback logs only; it no
longer creates an ungated local `systemChat` path. Task feedback audience and
CAS combat behavior are unchanged.

Permanent scenario `vigil-debug-channel` installs a temporary delegating
observer around the exact client-local CORDIS presentation function. The server
invokes the exact AAE adapter with unique disabled and enabled tokens; both
tokens appear in its RPT. Client-a independently records the same exact lines,
the setting key, and false/true target-local values before delegating to the
original function. The scenario proves the obsolete private variable absent,
restores the original function and initial setting, and removes its shared
coordination state.

Unchanged cold runs `20260825T211810Z-e22f0ec6` and
`20260825T211937Z-cc730425` each passed 3/0 server and 3/0 client feature
assertions with complete acknowledgements and cleanup. Full existing CAS
gameplay then passed unchanged in `20260825T212117Z-841a8c18`, excluding a
combat-path regression. The initial static control failed solely because the
hardcoded private assignment and lookup were present; after refinement the new
contract and existing 13-setting contract both pass.

Visible framebuffer pixels, other clients/sides, client-originated AAE calls,
network interruption, CBA settings UI interaction, and rate/volume remain
outside this proof. Because the result primarily joins Pontifex and CORDIS
policy rather than isolating an undocumented Arma mechanic, generic Sacred
Texts promotion requires separate review and is not presumed.

The accepted Evidence Contract was ingested twice with unchanged second-pass
counts, and the Sacred Texts audit passed. Reviewed distillation advanced to 17
findings while retaining 7 generic lemmas and 1 conjecture; this finding is
`PROJECT-SPECIFIC ONLY`, so it added zero generic notes. The final ledger has 19
packages, 20 runs and 434 artifacts. Post-ingest `systemChat` revision 376770
retains only upstream documentation; the new project dossier exposes the
bounded Vigil theorem and exact Tribunal provenance.
