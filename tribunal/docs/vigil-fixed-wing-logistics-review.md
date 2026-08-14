# Vigil fixed-wing logistics review

Review outcome: **REFINE BEFORE PERMANENT COVERAGE**.

## Behavioral contract

A logistics-role fixed-wing asset uses the established registration snapshot and
reconstruction lifecycle. From the real Vigil/Field Utilities UI, a client may
submit one non-empty physical manifest and a valid destination. The server owns
one task, the reconstructed aircraft and crew, every packed container and its
nested cargo, the parachute, delivery completion, and RTB. The aircraft must fly
to the destination, release the exact packed container under a real parachute,
land it intact within 100 m, preserve the exact weapon, magazine, item and
backpack quantities, reject a concurrent duplicate, physically egress, and
return the registry entry to reusable cooldown/stowed state.

There is no capacity or weight feature in the current UI or request contract.
The permanent specification therefore rejects an empty manifest but does not
invent capacity boundaries.

## Architecture and lifecycle

Registration, snapshot data, reconstruction, role bitmask, ingress/egress
coordinates, aircraft state, crew creation, public registry, bounded RTB and
cooldown are shared with fixed-wing strike. Logistics adds a distinct path:

1. `YOSHI_taskFW_logiStub` opens the Field Utilities fabricator with the selected
   on-station aircraft as its airdrop context.
2. The queue contains physical objects, not abstract item rows. Packing copies
   weapon, magazine, item and backpack cargo into an attached `Land_Pallet_F`.
3. Submit passes aircraft, packed-object netIds, destination and requester to
   `YSF_fwRequestLogistics`. Empty, invalid, wrong-side, unavailable,
   non-logistics and duplicate-active requests fail before dispatch.
4. The server transfers the complete packed object tree to owner 2, flies the
   registered aircraft toward the destination, and releases only inside a 25 m
   horizontal gate and a bounded altitude gate.
5. Field Utilities positions the existing physical pallet below the aircraft,
   creates `B_Parachute_02_F`, attaches the pallet, records bounded descent and
   detaches on ground arrival. Completion is terminal physical evidence, not a
   client-side “drop requested” state.
6. Vigil records a compact replicated terminal event, initiates the shared RTB
   lifecycle, and leaves the delivered cargo usable until scenario cleanup.

Server-private event history retains high-rate ingress/drop evidence for tests.
Only compact identities and terminal summaries are public; trajectory arrays
are not replicated through the registry or last-event variable.

## Manifest semantics

The manifest is a tree of real Arma containers. Tribunal normalizes each node as
container class/netId plus sorted `(class, quantity)` pairs from
`getWeaponCargo`, `getMagazineCargo`, `getItemCargo`, and `getBackpackCargo`.
Empty packing nodes are excluded from the payload comparison. The permanent
fixture requests exactly:

- one `arifle_MX_F`;
- four `30Rnd_65x39_caseless_mag`;
- two `FirstAidKit`;
- one `B_AssaultPack_khk`.

The authoritative requested tree and the landed physical tree must be exactly
equal. This exercises all four distinct inventory APIs without pretending to
cover every catalog item. The client cannot reliably inspect remote source
container cargo during the pre-submit UI phase on this engine build; it proves
the queue/request contract there, then independently proves the replicated
landed tree. The server performs the authoritative exact comparison.

## Parachute and delivery characterization

Controlled Live experiments showed that attached-object `getPosATL` is relative
to its attachment on this engine build. Tribunal therefore derives physical
height from world ASL minus terrain ASL. A packed pallet also begins falling too
slowly for a high-altitude-only deployment threshold to be a safe trigger, so
parachute creation uses a bounded 0.75-second release transition as well as the
altitude condition. Ground arrival is computed from the chute's ASL height above
terrain; disappearance before ground fails closed. These are evidence-backed
engine requirements, not product semantics.

Wind-free calibration separated aircraft release accuracy from parachute drift.
A 250 m release gate landed 262 m away. A 75 m gate produced 65 m in Live Mode
but 132 m in a cold run. The final 25 m gate produced 24.63 m error in cold run
`20260814T202618Z-836d4782`, with release at
`[4180.97,5600.79,172.387]`, landing at `[4182.39,5582.78,1.46893]`,
zero damage, one chute and 127 delivery samples. The 100 m specification limit
has useful margin without accepting the earlier clearly bad releases.

## Review classification

| Subsystem | Classification | Resolution |
| --- | --- | --- |
| shared registration/snapshot/reconstruction | KEEP AS-IS AND SPEC-TEST | reuse fixed-wing role and lifecycle; logistics role asserted |
| physical-object manifest model | KEEP AS-IS AND SPEC-TEST | exact normalized landed tree proves weapon/magazine/item/backpack paths |
| capacity/weight | DEFER | no claimed implementation exists |
| old client-local fling finalizer | REWRITE BEFORE PERMANENT COVERAGE | replaced by acknowledged server-authoritative request/task |
| request validation and duplicate guard | REFINE BEFORE PERMANENT COVERAGE | fail-closed requester/role/state/object/destination checks and one active task |
| ingress/release | REFINE BEFORE PERMANENT COVERAGE | physical MOVE, bounded deadline, 25 m/altitude gate, sampled path |
| parachute lifecycle | KEEP + CHARACTERIZE ENGINE REQUIREMENT | real chute, bounded attach/descent/ground/detach with ASL-derived height |
| inventory mutation locality | REFINE BEFORE PERMANENT COVERAGE | transfer pallet and all attached objects to server before release |
| completion/event replication | REFINE BEFORE PERMANENT COVERAGE | physical terminal result; compact public event, private trajectories |
| RTB/cooldown/reuse | KEEP AS-IS AND SPEC-TEST | reuse proven bounded fixed-wing RTB |
| repeated delivery | KEEP + CHARACTERIZE | two distinct Live tasks/manifests proved no stale task or payload |
| future client-b | DEFER | contract already separates requester-local UI from one shared delivery |

## Evidence and false-PASS controls

The test correlates one tokenized task, aircraft, pallet and chute across
request, ingress, release, attachment samples, descent, landing, physical
inventory and RTB. It cannot pass on an old container because netIds and exact
manifest are taken from the accepted task. It cannot pass when an aircraft only
flies over, a chute is unassociated, cargo is destroyed, inventory is partial or
duplicated, landing is outside tolerance, duplicate dispatch overwrites state,
or cleanup removes evidence before the client observes it. All waits are
bounded and absent/nil/ambiguous evidence is false.

Locality is explicit: client-a owns the UI/requester; server owns aircraft,
pilot, pallet and nested manifest objects. Tribunal samples the parachute as
server-local throughout its observed lifetime (its engine-reported owner may be
0 even while `local` is true). The client observes one nonlocal aircraft,
container and content tree with matching netIds and terminal event.

Live calibration completed two deliveries in one retained session. Task
`LOGI_4_233318_187250` delivered cargo `4:9` under chute `2:191`; after RTB and
reuse, task `LOGI_4_470602_204558` used aircraft `2:193`, cargo `4:12`, chute
`2:219`, and a different MXC/Medikit/Kitbag manifest. The distinct identities
and exact second inventory proved cleanup and stale-state isolation.

Fresh cold run `20260814T202618Z-836d4782` passed 19 server and 12 client
assertions with zero failures and removed client, server, private network and
runtime state. Final post-review run `20260814T203444Z-c44a034a` also passed 19 server and 12 client assertions with zero failures. It recorded chute `2:196` as server-local throughout observation, landed cargo `4:5` 42.20 m from the requested point with zero damage and exact inventory, sampled 5,330.45 m of RTB travel, and completed normal cleanup.

## Generic Tribunal tooling

`tribunal.mission.delivery` is product-neutral. It normalizes physical container
trees and supplies paired cargo/parachute sampling plus descent, attachment,
locality, survival and delivery-error evidence. Vigil meaning—eligible role,
request validation, manifest policy, dispatch, completion and reuse—remains in
the product scenario.

## Next feature review

Review fixed-wing reconnaissance next. It shares the proven registered-aircraft
lifecycle while introducing a distinct observation/sensor contract; it should
not inherit strike targeting or logistics cargo assumptions.
