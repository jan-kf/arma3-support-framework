# Advanced Systems OPHANIM / Iron Dome review

## Scope and result

This review applies the canonical feature-review program to the automatic
OPHANIM artillery-interception subsystem in `mods/advanced-systems`.  It
covers the public launcher asset, native-artillery entry, server assignment,
physical interceptor, terminal result, bounded retry/task lifecycle, authority,
locality, replication and cleanup.  Launch audio is configuration-checked but
not claimed audible because autonomous clients run with `-noSound`.

**Classification: `KEEP AS-IS AND SPEC-TEST` (refined; accepted / covered).**

## Resolved threat/locality update (2026-08-28)

Iron Dome now qualifies threats by predicted impact: an enabled launcher is a
candidate when its distance to the predicted impact lies within the configured
radius. It does not filter by side or by firing source. Merely passing near or
over the defended area is not sufficient. The native `ArtilleryShellFired`
observer runs on every machine; nonserver owners submit authenticated telemetry
to the server, and successful engagement routes deletion to the shell's current
owner with an authenticated acknowledgement. Server-local shells commit the
same owner-local deletion directly. A 150 m fuse replaced the legacy 40 m value
because controlled runs showed the Jian interceptor self-terminating between
samples after reaching 134–149 m; 150 m is the smallest repeatedly stable
observed envelope and remains a replaceable balance detail.

Fresh accepted Evidence Contract v5 run `20260828T165140Z-686b63d6` passed all
15 server and 2 client assertions. Native client/HC-fired shell creation remains
externally blocked: the automated client could not make a local AI or player
mortar emit the event, ammo objects had no stable `netId`/client object adapter,
and `setOwner` did not migrate them. Rejected calibrations are diagnostic only;
the accepted contract makes no client/HC-owned outcome claim.

Corrected package revision v5 uses canonical numeric BIKI concept identities.
Production ingestion advanced once from 41 to 42 packages and 42 to 43 runs;
the identical second pass was count-stable and the full knowledge audit passed.
Reviewed distillation classified the proposition as project-specific and added
no generic Arma lemma; its identical second pass was idempotent.

The original physical pipeline worked, but two bounded defects blocked honest
coverage.  Any client could remote-execute globally named internal functions on
the server, and a live shell whose attempts were exhausted remained in the task
array.  The accepted implementation gives internal operations an unpublished
server capability, records rejected calls privately, retires exhausted tasks
only after their active monitors finish, and publishes a bounded identity-only
terminal event ledger. The resolved work additionally changed threat policy
from shell proximity to predicted-impact coverage. Visual/audio behavior was
not redesigned.

## Stable contract

An enabled, live OPHANIM observes native artillery shells on their owning
machine and submits nonserver telemetry to the server. A launcher qualifies
when the shell's predicted impact—not its current position or allegiance—lies
inside that launcher's configured protected radius. The server assigns an
available launcher, launches a real interceptor, and retries within bounded
attempt limits until the exact shell is intercepted or becomes terminal.
Successful interception must physically prevent the impact that the same native
artillery fixture produces without an eligible launcher. Separate concurrent
shells are handled independently. A disabled/absent launcher or a predicted
impact unambiguously outside coverage does not alter the real shell.
Consequential internal operations reject client-originated calls, terminal
events replicate, and finished work leaves no task or fixture state behind.

The contract deliberately does not promise Jian, the 150 m private fuse, the
0.35 s steering delay, exact retry/spacing values, task/hash-map layout, object
variable names, fixture coordinates, or ledger schema.

## Canonical review

### 1. User/integrator observation

`YAS_OPHANIM_box` is a public Eden/Zeus supply asset labelled “OPHANIM (Iron
Dome).”  Presence enables it automatically.  A CBA setting describes the
engagement radius as the maximum distance at which it engages artillery shells.
The observable result is a physical launch followed by neutralization of a
nearby artillery shell.  The box has no ammunition inventory or user toggle.

### 2. Current behavior and negative paths

Server postInit installs `ArtilleryShellFired`, starts a dispatcher, registers
existing boxes and observes later `EntityCreated` boxes.  A server-local shell
is deduplicated into a task.  Candidates are live, enabled registered boxes
within the current radius; assignment prefers the earliest launch slot and then
distance.  A real `M_Jian_AT` launches vertically, steers toward the shell, and
the monitor deletes both at fuse proximity.  Failed attempts delete their own
interceptor and retry up to the configured maximum.

No box, a disabled box, an out-of-range shell, a non-server-local shell, a dead
launcher, or an unsupported interceptor produces no successful engagement.
Terminal shells are removed from task state.  The refinement additionally
retires exhausted work once no monitor owns it and releases the shell's
controller flag.

### 3. Authority, locality and lifecycle

Shell observation, assignment, interceptor creation, monitoring, deletion and
the terminal decision are server-owned.  The handler explicitly rejects a
shell that is not local to the server.  Interceptor and shell locality are
recorded at launch/terminal time.  The replicated ledger contains identities
and facts only, never executable input.

The original `isServer` checks were not an authority boundary: a client
remote-executed `YAS_fnc_ironDomeRegisterBox` and re-enabled a disabled box in
Live run `20260819T215108Z-74cbf804`.  Internal operations now require a random
capability compiled independently on each machine and passed only through the
server event/worker chain.  In run `20260819T220732Z-3cb526bf`, the same call
arrived from owner 4, produced a private `token-rejected` receipt, and left the
box disabled and absent from the registry.

### 4. Generic mechanics

Native artillery launch and `Fired`/`ArtilleryShellFired` correlation,
trajectory sampling, locality and physical terminal evidence are generic
Tribunal mechanics.  The permanent feature scenario reuses
`tribunal.mission.artillery`; OPHANIM eligibility, assignment, interception,
retry and result meaning remain in Advanced Systems.

### 5. Product-owned behavior

Advanced Systems owns automatic registration, shell eligibility, engagement
radius, assignment, physical interception, retry limits and terminal cleanup.
The implementation has no side filter and no consumable launcher resource.  No
new hostile-only, protected-impact-area, ammunition or operator-control policy
is invented here.

### 6. Engine requirements

The current interceptor class reports `manualControl = 1` and the vertical then
steered sequence works.  No retained A/B establishes that this exact class or
steering sequence is engine-required, so neither is characterized.

Two fixture behaviors were established narrowly. Ammo-class `M_Jian_AT`
objects did not reach a mission `EntityCreated` observer on this dedicated
build, even when classification was deferred to the next scheduled frame; a
bounded `allMissionObjects` observer did see and sample the same physical
objects. Also, deleting an intercepted artillery shell before its expected
impact could leave the AI mortar's prior fire command occupied, causing later
orders to produce no shell. Permanent phases therefore use fresh, identically
configured mortars after interceptions. Both are evidence-adapter constraints,
not OPHANIM promises or general Arma claims beyond the observed build.

### 7. Fragile/incomplete details

The original spawn counter was not a success oracle; the replicated
`taskedShell` value was reset every dispatcher pass; logs and the product's hit
flag were self-authored; immediate shell netIds can be `0:0`; exhausted live
tasks could persist; and internal global names were client-callable.  Permanent
coverage does not use the spawn counter or `taskedShell`.  Stable per-object
event identities handle the same-frame netId case.  Authority and retirement
were refined before coverage.

### 8. Better native/existing mechanisms

The real `ArtilleryShellFired` entry and real physical missile already provide
the desired pipeline.  Tribunal's artillery observer replaces duplicated test
observation, not product behavior.  No speculative native rewrite is justified.

### 9. Causal proof

Live run `20260819T215108Z-74cbf804` held mortar, ammunition, target and aim point
constant.  With an enabled launcher, a real shell was server-local and a real
interceptor closed from about 510 m to 27 m before terminal deletion.  Without
an active launcher, the next real shell produced `HitPart`, passed within 2.85 m
of the tank and changed its damage.  This established the baseline A/B before
product refinement.

The permanent scenario requires:

* a native mortar shell correlated through both firing observers;
* disabled and out-of-range controls with sampled flight, exact `HitPart` and
  damage, plus zero matching engagement events;
* one exact eligible shell, launcher and physical interceptor correlated across
  independently sampled movement, authoritative terminal event, no `HitPart`
  and protected damage;
* two distinct simultaneous shell identities and two distinct interceptors;
* client-origin call receipt and rejection;
* server locality, exact client replication and full cleanup.

### 10. Replaceable implementation details

Private function/variable names, missile class, fuse distance, steering,
dispatcher cadence, retry and spacing values, selection ordering, UID format,
event-array layout, fixture classes/coordinates and sampling cadence are evidence
adapters or balance details.  They may change with the adapter while the stable
contract remains true.

### 11. Characterization

No mechanism is characterized.  The working missile control sequence and
server-local artillery restriction have not been compared against controlled
alternatives sufficiently to freeze them as engine requirements.

### 12. Tribunal promotion

No new generic Tribunal primitive was necessary.  Existing native-artillery
observation is reused.  Exact engagement semantics, authority receipts and
terminal records remain product-owned.

## False-PASS audit

The scenario cannot pass from a failed gun, a disappearing shell, a counter
increment, a stale event, a wrong projectile, or cleanup alone.  Every negative
control first proves its own real shell traveled and hit.  Positive protection
is conditional on that disabled impact baseline and correlates exact shell,
launcher and independently moving interceptor identities.  Events are reset at
scenario setup and filtered by fresh per-shot identities.  Missing identities,
events, samples, impact, damage, locality, rejection receipt, replication or
cleanup all fail closed.

An adversarial review additionally moved the unpublished capability from a
mission-global variable into machine-local `localNamespace`; otherwise a client
could replace a known global name through ordinary mission-variable broadcast
before calling the guarded function. The client knows neither the server-local
value nor a transport that returns it.

## Fresh autonomous acceptance

Fresh supervised run `20260819T222930Z-2ff35050` passed with 18 server and 6
client assertions and zero failures. The disabled shell produced 585 trajectory
samples, exact `HitPart`, 6.88 m closest approach and target damage. The enabled
shell `shell-85102-5.93993e+08` was joined to launcher `launcher-net-2:155` and
interceptor `interceptor-net-2:158`; the independent observer recorded 68
samples, 437.90 m physical travel and 27.48 m closest approach before the exact
shell terminated without target hit or damage. Two concurrent shell identities
used two distinct interceptor identities. The 3.61 km out-of-range launcher at
a 300 m radius left its real shell to hit and damage the target. Client owner 4
received the authority stimulus, the server recorded and rejected it, and the
client resolved the exact replicated terminal identities. Task, registry,
fixture, client, server, private-network and run-state cleanup all completed.

## Deferred/unproven behavior

* Client-owned artillery shells are deliberately not claimed; the current
  server handler rejects them and no owner-routing policy has been chosen.
* Friendly/outgoing-shell policy and protected-impact-area filtering are not
  specified beyond the current proximity-based behavior.
* Boundary values, exact retry/spacing balance and multi-launcher optimization
  are not specification promises.
* Audible launch output is unproven under `-noSound`.
* Client-b/JIP observation remains outside the one-authenticated-client proof
  boundary, although assertions are identity-scoped for extension.
