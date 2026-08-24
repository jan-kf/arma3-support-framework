# Field Utilities Fabricator and Virtual Storage — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Review classification: `REFINE BEFORE PERMANENT COVERAGE`. Final disposition:
refined and accepted with permanent coverage** (`fieldutils-fabricator`),
following the product decisions recorded below. Unproven clauses are explicitly
excluded from the accepted contract; see *Unresolved*.

## Scope

In scope: Virtual Storage and Fabricator module registration, the fabricator ACE
action, the asset browser and order queue, single-item fabrication, multi-item
packing and local delivery, inventory fidelity, authority/locality, and cleanup.

The Fabricator-to-Vigil authorization boundary is in scope. Physical airdrop
flight/delivery remains covered as a composite by `vigil-fixed-wing-logistics`.
Bridge Builder, towing, FPV, and ropes are out of scope. The ZEN
virtual-inventory action is in scope only for its registration condition.

Source: `source/field-utilities/addons/FieldUtils/`, principally
`functions/fabricator/fn_assets.sqf`, `functions/fabricator/fn_boxPacking.sqf`,
`functions/fabricator/fn_fabricationActions.sqf`,
`functions/global/fn_fabricator.sqf`,
`functions/global/fn_initModuleLogicSetters.sqf`, `config.cpp`, and
`ui/pages/page_assets.hpp`.

Inventory status at review start: section 4.1, *Implemented; NOT YET REVIEWED /
PARTIALLY COVERED*, listed as the number one review priority.

## Historical baseline at review start

The following questions record the pre-refinement implementation and the path to
the accepted result. The later *Current implementation* section is authoritative.

## Canonical review questions

### 1. What should the user or integrator observe?

A mission maker places a Virtual Storage module and synchronizes objects to it,
and places a Fabricator module and synchronizes station objects to it. A player
at a station gets an ACE action that opens a terminal listing the stored objects
with names, images and quantities. They queue items, submit, and receive real
copies: one item is delivered carryable at their feet, several arrive packed
into containers nearby with a bearing/distance readout. The module tooltips
promise one further control — a checkbox enabling a virtual-inventory action on
containers near a fabricator.

### 2. What does the feature actually do now, including negative paths?

The positive path is reachable and works. Established at runtime in Live Mode
against a fixture that creates both module logics, synchronizes storage and
station objects, and calls the real module setters:

* `YFU_fabricatorGetItems` returned the synchronized storage objects (3, then 1);
* `YFU_registerFabricatorMenuActions` registered exactly one ACE action on the
  synchronized station object;
* the clone carried exact cargo — `w=[["arifle_MX_F"],[3]]`,
  `m=[["30Rnd_65x39_caseless_mag"],[12]]`, `i=[["FirstAidKit"],[5]]`,
  `b=[["B_AssaultPack_rgr"],[2]]` — matching the source object exactly.

Negative paths are thin. With no storage module the list shows
`<No virtual storage items found>`; with no fabricator module the ACE action is
never registered and `YFU_registerFabricatorMenuActions` exits. An empty queue is
rejected with a hint. An invalid airdrop grid is rejected. There is no rejection
for a dead caller, a caller who has left the station, a destroyed station, or a
concurrent order from the same player beyond the `YFU_submit_in_progress` flag,
which is per-client UI state.

### 3. Which machines and lifecycle stages own the behavior?

This is the review's central finding. **Local fabrication is entirely
client-authoritative.** The module setters run on the server (`isGlobal = 0`) and
`publicVariable` the two logics, so discovery is server-owned. Actual JIP was not
exercised by this review. Every
subsequent step is not: the queue lives in the ordering client's `uiNamespace`,
`YOSHI_SPAWN_SAVED_ITEM_ACTION` calls `createVehicle` on that client, packing and
final placement run there too. Measured on the server for a client-ordered clone:

```
serverSeesClone=true|localOnServer=false|ownerOfClone=4
```

The object is globally replicated but owned by the ordering client. The server
never validates the order, never sees a request, and imposes no rate, quantity,
or eligibility limit. The only server-authoritative branch in the whole
fabricator is the airdrop path (`isServer` gate, `remoteExecCall [..., 2]`), and
that path is the one already covered.

One suspicion was tested and **disproved**: the server's `EntityCreated` handler
does reach client-created boxes — `ace_cargo_size` read `-1` on both a
client-fabricated clone and a server-created box of the same class. Whether the
`EpeContactStart` handler that handler installs actually fires for a client-local
object was not established and is not claimed either way.

### 4. Which mechanics are generic Arma, ACE, CBA, or Tribunal concerns?

Module-logic synchronization discovery, ACE action registration and activation,
container cargo enumeration, bounding-box geometry, `BIS_fnc_findSafePos`
placement, and ACE dragging/carrying are all generic. Tribunal already owns
delivery/inventory observation from the logistics work. No new generic capability
is required by this review; one was added to Pontifex tooling (below), which is
harness, not Tribunal.

### 5. Which behavior is owned by the product?

What counts as storage, what counts as a station, queue accounting, the choice
between single and packed delivery, container selection and packing order, drop
placement, the mass cap, and the order lifecycle. Five product decisions are
undefined and are listed under *Product decisions required*; none of them is
invented here.

### 6. Are unusual or claimed engine requirements proven?

No engine requirement is claimed by the code and none is proven by this review.
The underground staging positions (`-40` for a single item, `[0,0,-200]` for a
batch) and the one-tick settle before raycast sizing look like workarounds for
spawn visibility and collider stability, but no controlled alternative was run.
They remain `NEEDS EXPERIMENTATION` and are not frozen by any contract.

### 7. Which details are accidental, legacy, fragile, or incomplete?

* **`YOSHI_addItemsToFabricator` is unreachable.** Defined in
  `fn_fabricator.sqf`, called from nowhere in the repository. It registers a
  per-item "Spawn <item>" ACE action, a different interaction model from the
  terminal. It is globally named and could plausibly be a mission-maker entry
  point, so per question 7 it is recorded, **not deleted**. The inventory's
  caution about the "older globally named helper" refers to
  `YOSHI_SPAWN_SAVED_ITEM_ACTION`, which is very much alive — it is the clone
  primitive both delivery modes call.
* **`Fabricator_Module_EnableLocalArsenal` is declared and never read.** The
  module attribute carries a display name, tooltip and `defaultValue = "true"`,
  but no code anywhere reads it; `YFU_initVirtualInventoryActions` runs
  unconditionally on every client and adds the action to the `ReammoBox_F` class
  whenever the player is within 20 m of a station. A mission maker who unticks
  the box gets the action anyway.
* **Silent partial fulfilment and an object leak.** See below; refined.
* **The progress bar is theatre.** All fabrication and packing completes before
  the progress loop starts; the loop then runs for `count(items)` seconds
  displaying random status strings. No contract should promise that progress
  tracks work.
* **Magic constants:** the implementation attempts to cap `ReammoBox_F` mass at
  200, but later dedicated-server measurements did not establish that the cap
  takes effect (see *Unresolved*); station altitude `> 200` shifts
  the spawn down by 10, staging depths `-40` and `-200`.

### 8. Is a better native or existing mechanism available, and is it proven?

Not investigated by comparison, so nothing is claimed. The obvious candidate —
routing orders through the server the way the airdrop path already does — is an
architecture decision, not a mechanism swap, and belongs to the product owner.

### 9. What is the stable behavioral contract and its causal proof?

Proposed contract, mechanism-neutral:

> A player at a registered fabricator station can browse the objects registered
> to virtual storage, queue them with quantities, and submit an order. A single
> item is delivered as a carryable copy at the player's position; several items
> are delivered packed into containers placed clear of the player. A copy carries
> the source object's weapon, magazine, item and backpack cargo. An order that
> cannot be delivered in full is refused and leaves nothing behind. With no
> storage or no station registered, no order can be placed.

Causal proof is available for every clause through data: synchronized-object
discovery, exact cargo comparison against the source, replicated object identity,
positions relative to the player, and an object census for cleanup. No pixel
evidence is required; the ACE action can be verified as registered and its
statement invoked, following the Bridge Builder boundary.

### 10. Which implementation details must remain free to change?

`uiNamespace` key names, the queue map/order layout, IDCs, the container classes
and pallet reference corners, packing order and bin-selection, staging depths,
the progress cadence and message list, drop radii, and every private function
name. The mass cap is user-visible and is therefore a product decision, not a
free detail.

### 11. Which mechanisms genuinely deserve characterization?

None yet. No controlled A/B was retained for the staging depths or the settle
tick, so nothing is eligible.

### 12. Which mechanics should be promoted into Tribunal?

Nothing product-neutral is missing. Tribunal's delivery/inventory observation
covers the evidence this feature needs. One Pontifex **harness** defect was found
and fixed (below) — that is Live Mode tooling, not Tribunal.

## Classification

| Capability | Outcome |
| --- | --- |
| Module registration and discovery | `KEEP AS-IS AND SPEC-TEST` |
| Fabricator ACE action registration | `KEEP AS-IS AND SPEC-TEST` |
| Asset list and queue accounting | `KEEP AS-IS AND SPEC-TEST` |
| Single local fabrication and cargo fidelity | `KEEP AS-IS AND SPEC-TEST` |
| Multi-item packing and local delivery | `REFINE BEFORE PERMANENT COVERAGE` |
| Local virtual-inventory toggle | `REFINE BEFORE PERMANENT COVERAGE` |
| Order authority and validation | `DEFER` — product decision |
| Storage depletion / order limits | `DEFER` — product decision |
| Staging-position mechanism | `NEEDS EXPERIMENTATION` |
| Airdrop handoff | out of scope, already covered |

The primary outcome is `REFINE BEFORE PERMANENT COVERAGE` because the capability
that gates the named review — delivering a submitted order — silently
under-delivered and leaked objects until this review, and because the local
virtual-inventory toggle does not do what its own tooltip promises.

## Refinement made

`YOSHI_spawnContainersNearObjectsAndPackMulti` computed a `_skipped` list of
objects too large for any container, wrote it to the debug log, and then returned
`[true, ...]` regardless. `YFU_assetsSubmitOrder` therefore reported **Success**
for an order it had only partly filled, and — because the success path never
deletes `_tempSpawned` — left the unpacked clones under the map for the rest of
the mission.

Measured before the change, packing a truck and an ammo box together:

```
packOk=true|containers=1|bigNull=false|bigPos=[0.56,-0.09,-198.63]|bigAttached=false|smallAttached=true
```

The packer now returns the skipped objects as a fourth element and reports
success only when nothing was skipped; the caller deletes anything unpacked, and
the order falls through to the product's existing failure path, which already
cleans up and tells the player the order failed. After the change, the same pair:

```
packOk=false|containers=1|skipped=1|smallAttached=true
```

and the same order driven end-to-end through `YFU_assetsSubmitOrder` on the
client reported `YFU_submit_success=false` with **zero** objects remaining below
z = -50 anywhere in the mission — no orphaned clones, no orphaned containers.

Refusing the whole order is the conservative reading: the product has a complete
failure path already, and has no affordance anywhere for telling a player which
items were dropped. Delivering partially would require inventing that UI.
*Whether an under-deliverable order should instead deliver what fits, with an
explicit manifest of what it could not, is a genuine product decision* and is
listed below.

## Product decisions (answered)

1. **Order authority: server-authoritative.** The client owns the terminal and
   the queue; validation and creation belong to the server.
2. **Depletion: none.** Virtual storage is an unlimited catalogue and template
   source. Fabricating never consumes or alters a registered object.
3. **Partial fulfilment: atomic.** An order that cannot be produced in full is
   refused whole and produces nothing. No partial-delivery semantics and no
   missing-items UI were invented.
4. **Mass cap: intentional.** Fabricated delivery crates are capped so a player
   can still carry them. Carryability is the contract, not source-mass fidelity.
5. **Local virtual inventory: a real feature, restored.** See below.

## False-PASS analysis carried into the scenario

Recorded now so the eventual scenario inherits it. A fabricator scenario could
pass without the behavior by: counting objects that a previous phase left behind;
matching a clone against itself rather than the source; reading the queue from the
same `uiNamespace` keys the product wrote without any object existing; treating
the "Success" overlay as delivery evidence (exactly the defect refined above);
sampling for orphans only near the player rather than mission-wide; or checking
cargo classes without counts. The census evidence must be mission-wide and taken
against an independently recorded pre-order baseline.

## Harness findings

Developer Live Mode executed operator snippets with `call compile` **inline in
the server poll loop**. Any SQF runtime error inside a snippet terminated that
scheduled loop permanently, and `live reset` could not recover the session
because reset is delivered through the same dead inbox — the only remedy was a
full restart. Observed during this review: a `count` applied to a Number stopped
the poller at poll 1440, after which no command was ever executed again.

The poller now runs each snippet in its own script. Proven by an A/B on the same
error: on the fixed build the identical `count`-on-Number error is logged and the
**next** command still executes (`YFUPOLL|after-error-still-alive`), where on the
previous build the loop was dead. Covered by
`test_live_poller_isolates_operator_snippets_from_its_own_loop`.

## Fresh autonomous proof

The final cold acceptance run `20260818T213059Z-4a086b37` passed **26 server +
10 client assertions** with zero failures and complete container/network/state
cleanup. It drove honest orders through the terminal submit path and adversarial
requests through their real public or guarded entry points with no human input.

Selected evidence from that run and the earlier cold runs that shaped it:

* single order delivered server-owned and beside the player -
  `result=[...,true,"single","2:191",...]|localOnServer=true|owner=2`, with the
  client independently resolving that exact net id at `dist=3.24843`;
* packed order - `containers=1|attached=2|allLocal=true`;
* atomic refusal of an unpackable order - `result=[...,false,"unpackable"]` with
  `censusBefore` equal to `censusAfter` and zero staged objects;
* `unregistered`, `out-of-range` and `no-storage` refusals, each census-matched;
* guessed worker and accept capabilities produced exact `token-rejected`
  receipts and no transaction/object change;
* wrong-role and already-busy Vigil aircraft produced the exact shared-validator
  reasons `aircraft_not_logistics` and `duplicate_active_task`;
* the registry setter rejected a guessed token with an exact `set-entry`
  receipt and left the registry unchanged;
* the forced post-creation stall produced `watchdog/worker-terminated`, an
  `abandoned` result, and an identical before/after mission-wide census;
* owner cancellation after the exact clone had been tracked produced both
  `discard/worker-terminated` and `discard/accepted`, restored the exact census,
  and left the transaction finalized rather than letting its worker resume;
* retirement reached `state=unknown|resultPresent=false` only after the terminal
  result had first been observed;
* teardown reported `census=[[],0]`, no transaction/result/registry keys, and
  the harness removed the server, client, private network and run state.

Earlier cold runs were needed to reach it, and the failures were real
rather than flaky: an unstable player position at fixture time (the anchor was
sampled the instant the player object appeared, before it had been placed), the
6,168 m delivery, the deep-staging and hidden-object mass readings, unscheduled
`uiSleep`, and the client reading editor synchronization before it had
replicated. Two further Arma/SQF details surfaced during the adversarial round:
`str` adds quotes when applied to a String, so an exact receipt oracle must keep
an already-string detail unchanged; and a replicated result/object identity can
arrive before the object's final position, so the client boundedly waits on that
same net id rather than substituting a nearby object. Each failure was diagnosed
from run evidence and fixed at its cause.

## Evidence index

All runtime evidence came from Developer Live Mode sessions
`20260817T205801Z-a3fdabcf` (baseline, pre-refinement) and
`20260817T211959Z-4e6658de` (post-refinement), with the poller A/B spanning
`20260817T205801Z-a3fdabcf` and `20260817T211507Z-87c52150`. Live Mode is a
development aid; none of it is a fresh autonomous proof, and none is claimed as
one. The fresh autonomous proof is recorded above.

## Current implementation (supersedes the historical sections above)

Everything above this line describes what the feature *was* and how it was
reviewed. This section is what it *is*.

**Authority.** Two operations are client-facing: order submission and an
owner-bound discard. Identity comes from `remoteExecutedOwner` at those entry
points and never from the payload. Every internal helper - accept, worker, track,
finalize, publish, refuse, set state, and retire - is gated on
`YFU_FABRICATOR_TOKEN`, a secret each machine
generates at init and never publishes, so a remote-executed call to any of them
carries the wrong value and does nothing. A discard rebuilds the transaction id
from the owner the transport reports, so naming another owner's request reaches
nothing.

An earlier attempt used `remoteExecutedOwner isEqualTo 0` as the internal guard.
That is wrong on this build: measured in run `20260818T194317Z-773b507b`, the
value stays non-zero inside a script spawned from a remote-executed frame, so the
guard blocked the server's own worker - the transaction was claimed
(`knownTx=["4#YFU_4_83155_176009"]`) but no result was ever published. The token
replaced it.

**Airdrop.** A client cannot select airdrop mode into a bypass. Field Utilities
delegates authorization to Vigil's product-owned
`YSF_fwValidateLogisticsAsset`, which is also used by Vigil's logistics request.
The exact aircraft must be alive and registered as the spawned vehicle, in
`on_station`, have the LOGI role, match the requester's side, and have no active
logistics task. Naming an arbitrary aircraft, a registered strike aircraft, or a
busy logistics aircraft authorizes nothing. Vigil registry mutation is protected
by its own unpublished per-machine capability token; Field Utilities neither
interprets nor mutates the registry.

**Transaction identity.** One id, `owner#request`, keys the claim, the published
result, the ledger of created objects, finalization, discard and retirement. Two
owners using the same client-generated id cannot collide. A claim is taken before
the worker is scheduled, so a duplicate is refused rather than built, and a
terminal result is written once so a late or duplicate writer cannot overwrite the
outcome an in-progress transaction already reached.

**Schema.** The complete top-level and nested schema is validated before anything
is claimed, scheduled, expanded or created: request id, station ref, Boolean mode,
entry structure, string refs, finite positive integer quantities, per-entry and
total bounds. A malformed payload produces an explicit refusal, not an SQF error.

**Atomicity.** Objects are tracked into the transaction ledger as they are
created, not only at known failure branches, and every refusal runs one path that
finalizes before it publishes. The finalizer deletes exactly the net ids the
transaction itself recorded and can reach nothing else. A watchdog handles any
transaction that has not reached a terminal state within its build deadline. It
terminates the worker before finalizing, so a stalled script cannot resume after
rollback and create or publish late state. This covers unexpected script failure
and stalls as well as the anticipated branches.
The boundary is defined as: from claim to terminal result, on the server, over the
objects that transaction created. Client disconnect mid-order is *not* separately
handled beyond that watchdog, and no claim is made about it.

The owner-bound discard path retains and terminates an active transaction's exact
worker before finalization, then schedules normal retirement. A timeout checks
that the claim still exists before acting, so a sleeping watchdog cannot recreate
state after an earlier short-TTL retirement.

## Runtime adversarial controls

Static contracts are not evidence for a remote boundary, so these are proven in
the fresh autonomous run with exact before/after identity sets:

| Control | Evidence |
| --- | --- |
| Direct worker invocation | exact `worker/token-rejected` server receipt, census identical, `txState=unknown` |
| Direct internal-accept invocation with forged owner | exact `accept/token-rejected` receipt, census identical, no transaction |
| Duplicate identical request | one `accepted` and one `replay-rejected` receipt; exactly one created identity |
| Client-selected airdrop on an unregistered aircraft | `airdrop-unauthorized`, census identical |
| Registered wrong-role and busy-logistics aircraft | exact Vigil rejection reasons; no delivery |
| Registry-mutation guard | direct guessed-token invocation of the actual server setter records `token-rejected`; registry and census unchanged |
| Malformed quantity | `malformed-quantity`, census identical |
| Oversized order | `too-large`, census identical |
| Discarding another owner's transaction | exact owner-miss receipt; victim alive, its ledger intact, census identical |
| Owner discards an active transaction | exact clone first tracked; `worker-terminated` then `accepted`; census restored and transaction finalized |
| Worker stalls after object creation | exact `worker-terminated` receipt, `abandoned` result, and immediate creation tracking restore the exact mission-wide census |
| Result retirement | terminal result is first observed, then transaction and published key both disappear after a short test TTL |

The foreign-discard control uses a server-owned transaction rather than a second
authenticated player, because this scenario has one client. **The client-b case -
one player discarding another player's transaction - remains unproven**, and the
boundary is built to be client-N ready: the observer declares its own unit by net
id rather than being taken from `allPlayers` ordering.

## Placement contract

The permanent contract now proves **a server-owned single delivery placed on land
within a bounded distance of a recipient who is on land**. The exact delivered
net ID and the independently published target both report non-water positions.
The same run proves the observer can distinguish water because
`surfaceIsWater [0,0,0]` is true at Stratis sea origin; missing/always-false
observation therefore cannot pass the assertion.

The earlier `surfaceIsWater` experiment was reported as failing because the tier
runs `-world=empty`. That explanation was wrong and is withdrawn: `-world=empty`
is only the server's startup world, and the mission itself is `.Stratis`. The real
cause was the fixture. The scenario did not set `respawn_on_start`, so the player
respawned at the map origin over water. With `respawn_on_start = "0"`, the final
cold run `20260824T143714Z-6bb99e1c` passed 27 server and 10 client assertions.
Its exact clone was on land at `[4702,2779,1.38931]`, the announced target was on
land at `[4702,2781,0.00282764]`, the recipient base was non-water, and the clone
remained 2.82 m from the announced target after physics settling. This is
`KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED` for the bounded land fixture.
Gradient, pond detection, obstruction clearance, coastline fallback and a water
recipient remain experimentation boundaries, not implied suitability promises.

## Unresolved

* **Delivery mass cap.** Preserved as one named rule and asserted by nothing.
  Land removed the prior confound but did not fix it: runs
  `20260824T141149Z-e94699db`, `20260824T141708Z-cb060664`,
  `20260824T142213Z-2664619a`, `20260824T142659Z-23dd851a`, and
  `20260824T143212Z-c4291fda` all observed the exact server-owned and remotely
  replicated clone at `getMass = 1e-12` while its source reported 500. A matched
  `createVehicle` `NONE`/`CAN_COLLIDE` land comparison was stable at
  `[[500,500],[500,500],[500,500]]`, disproving creation mode as the cause. A
  `> 0.001` wait, source-mass fallback, and clear-land staging each failed and
  were reverted rather than fossilized. The mass mechanism remains an open
  defect requiring a more isolated cargo/hide/physics experiment.
* **Broader terrain suitability**, per the section above; bounded land
  placement is covered.
* **Client-b and JIP.** One authenticated client is the proof boundary.
* **ACE-side action presence.** ACE 3.21 stores object actions where neither an
  object variable nor the class-keyed `ace_interact_menu_ActNamespace` exposes
  them, so the scenario proves the module handshake reaches the client and the
  registrar is idempotent, not that ACE holds the action.
* **Runtime editor synchronization.** `synchronizedObjects` does not replicate to
  clients for sync created at runtime, so per-station client-side registration
  cannot be proven with a runtime-built fixture.
* **Live snippet supervision** is separate Tribunal infrastructure work, not a
  Fabricator concern.

## Acceptance boundary

The accepted milestone covers one authenticated client, server-authoritative
atomic fabrication, unlimited catalogue semantics, exact cargo, packed delivery,
the shared Vigil authorization boundary, adversarial request receipts,
active-cancellation and watchdog rollback, result retirement, and complete
scenario isolation, and bounded land placement. The mass cap, broader terrain
suitability, actual client-b/JIP behavior, ACE-internal action visibility,
runtime-created editor synchronization, and Live-snippet supervision remain the
explicit follow-ups listed above; none is implied by the accepted PASS.
