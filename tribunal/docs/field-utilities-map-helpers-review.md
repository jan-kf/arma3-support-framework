# Field Utilities map helpers and delivery feedback — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: marker surface `REVIEWED / DEFERRED`; delivery feedback
`REFINED; ACCEPTED / COVERED`.** The inventory had
combined an unreachable marker scaffold with two live formatting helpers used
only by the Fabricator/Vigil airdrop composition.

## Scope and reachability

`fn_initMapTools.sqf` preInit defines marker creation/toggling, compass labels,
and a vacuum fall-time formula. Repository-wide search finds no caller outside
the marker helpers for `YOSHI_addMarker`, `YOSHI_createIdMarker`, or
`YOSHI_toggleDisplayLocationDataOnMap`. They have no action, task, module, or
documented entry.

`YOSHI_GET_DIRECTION` and `YOSHI_GET_FALL_TIME` are live only through
`YFU_assetsAirdropAnnounce`, called on the requesting client after Vigil
accepts a logistics request. The 2026-08-28 refinement no longer calls the
vacuum fall helper: it waits for real positive closing motion, predicts the
aircraft/package position at Vigil's release gate, and reports a five-second
rounded time to release.

## Canonical review questions

### 1. What should the user observe?

No supported user behavior exists for ID/location markers. For airdrop
feedback, the current message promises package count, direction, and “ETA”.
The intended direction, ETA interval, and audience are not documented.

### 2. What does it actually do?

Marker helpers create global markers and optionally delete/recreate one each
second. The direction helper maps a bearing to eight labels. The fall helper
computes `sqrt(2 * height / 9.81)`. At logistics acceptance, Field Utilities
computes target-to-aircraft bearing and altitude-only vacuum fall time, then
emits side-chat. The validated `_sourceASL` argument is never used.

### 3. Which machines and lifecycle own it?

Global marker commands are callable on every machine without authority. The
moving loop publishes a local script handle as a public object variable and
does not remove the final marker when its object dies.

Airdrop formatting runs on the requesting client after authoritative
acceptance. CORDIS transports the message with default scope zero; intended
requester/side/global audience is unresolved. Vigil owns actual ingress,
release, parachute, and landing timing.

### 4. Which mechanics are generic?

Marker census, bearing labels, message receipt, and independent timeline/position
observation are generic. Marker visibility, delivery language, audience, and ETA
meaning are product/composition policy.

### 5. Which behavior is product-owned?

Whether ID markers ship; who creates/sees them; labels/lifetime; whether
direction means “from” or “toward”; ETA start/end event; audience and rounding.
Vigil is the only current layer with authoritative task timing.

### 6. Are unusual engine requirements proven?

No. Deleting/recreating a global marker is not proven necessary. Vacuum
free-fall does not model aircraft ingress or parachute descent and is not
evidence for either acceptance-to-landing or release-to-landing time.

### 7. Which details are fragile or incomplete?

Marker helpers leak undeclared globals, derive `side` and group labels
incorrectly for some vehicles, overwrite type classifications by branch order,
race concurrent toggles, publish a nonportable script handle, and leak terminal
markers. Airdrop feedback duplicates another compass formatter with different
spellings. Its ETA can be confidently precise but semantically false.

### 8. Is a better mechanism available and proven?

`setMarkerPos` exists, but no reachable marker contract warrants a rewrite.
For delivery timing, the accepted logistics task already records real release
and landing events; whether to estimate them prospectively remains a product
choice rather than a formula substitution.

### 9. What is the stable contract and causal proof?

No marker contract is selected. Do not cover unreachable helpers.

Candidate delivery contract: after an exact accepted request, the intended
audience receives one count/direction message and, only if defined, a bounded
ETA tied to explicit pipeline events. Proof correlates exact request/task/cargo
identities with independently observed acceptance, release, parachute, and
landing timestamps and positions. Rejected requests must produce no message.

### 10. Which details must remain replaceable?

Marker names/types, refresh mechanism, compass spelling/buckets, text format,
transport helper, ETA model, rounding, and private function names.

### 11. Which mechanisms deserve characterization?

Only the live announcement: record its actual audience and compare the current
number against acceptance-to-release, acceptance-to-landing, and
release-to-landing at two ingress distances with the same release altitude.
The dead marker scaffold needs no runtime characterization.

### 12. What should be promoted into Tribunal?

Nothing yet. Tribunal already has product-neutral marker observation. Generic
delivery timeline observation should be reused, not product feedback policy.

## False-PASS boundary and continuation

Formula unit tests do not prove truthful feedback. Message presence does not
prove accepted delivery. Expected values derived from the same helper
self-confirm. Marker screenshots/state are meaningless without a reachable
stimulus.

Decide marker reachability/visibility/lifetime and delivery direction, ETA
interval, audience, and omission policy. Then reuse a retained
`vigil-fixed-wing-logistics` fixture: capture exact client message and
independently timestamp acceptance, release, chute, and landing at two ingress
distances. A wrong/empty rejected order must prove rejection and silence.

## 2026-08-28 resolved contract and evidence

Direction is from the requested target toward the predicted release position,
which tells the player where to expect the aircraft/package at release. ETA is
acceptance-flight observation to package release only; it never means landing
or ETA-to-ground. If the replicated aircraft does not establish at least
15 m/s closing motion within the bounded observation window, no confidently
misleading estimate is emitted.

Permanent `vigil-fixed-wing-logistics` run
`20260828T234039Z-8be1c0e0` passed the full physical delivery contract. The
announcement observed 124.875 m/s closing motion, predicted a release West of
target in 20 seconds, and the authoritative release occurred 19.138 seconds
later and 17.257 m from the predicted point. Package count and release-only
language were exact. Operational message audience is resolved side-wide;
client-B delivery/isolation remains shared C1 proof;
audio is not claimed.

## Disposition

**ID/location markers: reviewed/deferred as unreachable scaffold. Airdrop
direction/ETA: refined, accepted and permanently covered for one requesting
client.** Do not restore altitude-only vacuum-fall semantics.
