# Advanced Systems APS presentation effects — canonical feature review

## Scope and result

This review covers APS hard/soft-kill beams and particles, engagement sounds,
voice sequences, and status/notification presentation. It does not reopen the
accepted physical APS outcomes or the separately reviewed ACE authority/menu.

* **Beam/particle presentation:** **REVIEWED / DEFERRED PENDING PRODUCT
  PRESENTATION DECISIONS**.
* **Audible voice/engagement sound:** **REVIEWED / DEFERRED** under the current
  `-noSound` proof environment and unresolved audience/concurrency contract.
* **Status facts:** consumer-owned by the APS control review; actual hint/audio
  presentation is not covered.

The strongest concrete mechanical divergence is locality: `YOSHI_animateAPS` remote-executes
`YOSHI_effects` only to the server, while `YOSHI_effects` creates local particle
sources. On a dedicated server those particles are not client-visible. The beam
and sound paths use separate global helpers and are reachable, but their client
outcomes are not proven by combat success.

## Canonical twelve-question review

1. **What should the user observe?** A hard-kill can show a red beam, local
   impact particles, and a trigger sound; soft-kill uses a yellow beam and sound;
   anti-drone uses a cyan beam/particles but remains separately deferred. APS
   controls can announce mode/resource/status facts and voice state.
2. **What does it do now?** Each accepted engagement calls `YOSHI_animateAPS`
   with mode-specific values. It routes sound and beam coordination to server.
   It also routes particle creation to server, where local particle sources are
   created and deleted after 0.1 seconds. Voice sequences globally create one
   client-local hidden sound source per vehicle, replacing any previous clip.
   Status handlers format server state and hint the supplied player.
3. **Which machines own it?** Engagement and authoritative facts originate on
   the projectile/server APS path. Beam helpers coordinate server-to-clients.
   Particles currently exist only on the dedicated server. Voice sources are
   client-local after a server broadcast. Status hints target caller-supplied
   player data whose authority defect belongs to the ACE controls review.
4. **Which mechanics are generic?** Draw3D registration/observation,
   framebuffer corroboration, client-local particle-command telemetry, audio
   capture/listener identity, and notification receipts can be Tribunal
   mechanics. APS mode/effect meaning remains Advanced Systems.
5. **Which behavior is product-owned?** Advanced Systems must decide whether
   visual/audible cues are supported outcomes, which modes require them,
   recipient/range policy, overlap/preemption, disabled-voice behavior, and the
   stable status fact set.
6. **Are unusual engine requirements proven?** No. No A/B establishes that the
   singleton beam implementation, exact pulses/colors/widths, local particle
   classes, randomized clips, hard-cut sequencing, or duration table is
   required. `createVehicleLocal` locality directly contradicts current
   server-only particle routing if client visibility is intended.
7. **What is fragile or incomplete?** The common beam helper uses shared global
   coordinates and a singleton `onEachFrame`, so simultaneous effects can
   overwrite one another. Server-local particles are invisible to clients.
   Voice sequences broadcast to all current clients, hard-cut prior clips, and
   have no listener/result acknowledgment. Exact duration values are manually
   duplicated. Status prose can be truthful while the request is unauthorized.
8. **Is a better mechanism available?** Client-targeted local particle creation
   and stacked/per-effect Draw3D handlers are plausible, but first decide that
   these effects are product behavior and use matched visual telemetry. Keep
   authoritative APS state as the status oracle; do not infer it from effects.
9. **What is the stable contract and causal proof?** If selected, an exact
   accepted engagement event causes one correct mode cue at intended clients,
   spatially correlated with the exact vehicle/projectile, while disabled/non-
   engagement controls produce none. Independent APS ledger and projectile
   outcomes prove meaning; destination-side Draw3D/particle receipts plus a
   framebuffer may prove rendering. Concurrent exact engagements must remain
   separately identifiable. Sound needs an actual sound-enabled listener.
10. **Which details remain free?** Exact colors, widths, pulse counts, particle
    classes, clip names, random pool, phrasing, timing table, helper names, and
    rendering/sound mechanisms are replaceable unless explicitly selected.
11. **Which mechanisms deserve characterization?** After product selection,
    first A/B client-targeted particle routing against current server-local
    routing. Then test two overlapping beams. Use audio capture only with sound
    enabled and explicit audience/range/overlap policy. Do not use VNC where
    destination telemetry proves state; use framebuffer only for actual visual
    appearance.
12. **What belongs in Tribunal?** Product-neutral Draw3D/particle destination
    receipts and optional framebuffer/audio observers if a second consumer
    justifies them. Never promote APS colors, mode meanings, voice tokens, or
    status wording.

## False-PASS boundary

A successful interception, ledger event, charge/fuel change, call to
`YOSHI_animateAPS`, server-created particle source, beam coordinator state,
configured sound, voice flag, status string, or notification request is not
client-visible/audible evidence. A screenshot without exact engagement identity
and destination telemetry is also too ambiguous. Silence under `-noSound` is
not a failure. Anti-drone effects cannot establish an accepted contract while
anti-drone itself remains deferred.

## Decisions and continuation

Decide whether each hard-kill/soft-kill visual and audible cue is supported or
best-effort decoration; intended client audience/range; overlap/preemption;
and which status facts are stable. If visuals are supported, fix only the
measured particle destination and beam concurrency defects, then reuse the
accepted exact-projectile APS scenario with destination-side effect telemetry
and a non-engagement control. Audio waits for a sound-enabled proof path. Status
presentation waits for the authenticated APS control boundary and uses
independent authoritative state as its oracle.
