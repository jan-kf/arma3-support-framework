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

No staging mechanism is frozen. The accepted continuation below shows the prior mass finding sampled the clone after intended ACE carry had attached it to the player; the authentic outcome is now covered at the pre-publication and post-carry boundaries, while staging positions and cadence remain free to change.

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
| Staging-position mechanism | `NO CHARACTERIZATION REQUIRED; OUTCOME-COVERED` |
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

## Accepted continuation — mass and staging isolation

The next-best unblocked candidate was the apparent delivery mass defect and its suspected staging choreography. The Opus reconnaissance supplied hypotheses only. Canonical `getMass`, `setMass`, `hideObjectGlobal`, and `isObjectHidden` dossiers, source inspection, rejected controlled alternatives, and fresh authentic runs established the result.

The earlier oracle sampled too late. A successful single order publishes the exact clone and the ordering client immediately calls ACE `startCarry` on that net ID. In final runs `20260824T184743Z-361320ec` and `20260824T185113Z-a5792be7`, a server-side observer wrapped the real publication boundary without replacing product behavior. Immediately before publication the exact server-owned `Box_NATO_Ammo_F` was visible, unattached, and mass 200. Client-a then resolved that same clone, began ACE carry, and observed it attached to the exact player with `getMass = 1e-12`. Cargo, land placement, authority, atomic controls, retirement, and cleanup all continued to pass.

Those runs closed the original observation as a boundary error. A later unchanged
cold repeat, however, exposed a real race: the server first observed mass 200,
then both peers observed the newly unhidden clone restored to class mass 500 and
ACE refused carry. Pinned ACE 3.21.0 source established that ACE itself propagates
mass changes with `ace_common_setMass`. Pontifex now uses that event, requires one
continuous second of stable capped mass before publishing a single delivery, and
the client boundedly waits for the exact replicated cap and exact attachment.
Raw visible and hidden relocation calibrations still retained mass 500;
speculative spawn-mode, threshold, fallback, safe-stage, settle, and contact
changes were rejected and removed. Staging choreography remains an implementation
detail rather than an engine requirement.

The two final runs each passed 28 server and 11 client feature assertions with zero failures; including smoke, 32 server and 15 client assertions passed.

## Accepted continuation — bounded gradient and obstruction placement

The next canonical priority was broader-terrain placement. Opus reconnaissance
was used only to propose questions; it supplied no accepted fact. Canonical
Sacred Texts dossiers for `surfaceNormal`, `setVectorUp`, `setPosATL`, and
`lineIntersectsSurfaces`, plus source inspection and controlled Live Mode probes,
bounded the experiment. No indexed `BIS_fnc_findSafePos` dossier was available,
so its return was treated as a candidate position rather than proof of suitability.

The first proposed severe-slope fixture was rejected. Around a 63.3-degree
recipient position, returned drops measured roughly 28.8–29.7 degrees and the
same packed container ranged from 0.41 m to 9.22 m of physical travel before
resting. Those diagnostic runs are evidence that severe gradients remain open,
not an accepted promise. A deterministic moderate neighborhood was then scanned:
the recipient was on 15.7-degree ground and every sampled 4–9 m ring point was
12.7–15.9 degrees. The obstruction control placed 64 concrete barriers in four
concentric rings on independently verified flat land.

Permanent coverage drives three real terminal submissions through the authentic
server worker: flat land, the moderate-gradient neighborhood, and the dense
obstruction ring. Each result must be successful and non-water, remain within
15 m of the recipient, contain both exact attached objects in one server-local
container, settle within 2 m of its announced target, and remain continuously
at or below 0.1 m/s with no more than 0.05 m positional change for two seconds.
The flat arm additionally bounds both slopes; the gradient arm requires both
recipient and drop to be 10–20 degrees; the obstructed arm requires all 64
barriers and an announced target no farther than 1.6 m from its nearest barrier.
Together with the separate target-to-final seating bound, this proves the helper
can seat the delivery inside a densely obstructed neighborhood; it does not
promise collision-free clearance for arbitrary shapes.

Independent cold runs `20260825T193508Z-ca6c7798` and
`20260825T194047Z-d3318e29` each passed **29 server + 11 client feature
assertions** with zero failures. Gradient containers travelled 0.062 m in both
runs before stable rest. Obstructed containers travelled 0.175 m and 0.001 m;
their nearest barriers were 1.018 m and 0.874 m away. Both runs also proved the
corrected exact-clone ACE carry handoff and complete cleanup.

The accepted second package was ingested twice through the supported Sacred
Texts interface. Counts changed once from 16 packages / 17 runs / 354 artifacts
to 17 / 18 / 398 and were unchanged by the repeat; the full knowledge audit
passed. Reviewed distillation remained at 15 findings, 7 generic lemmas and one
generic conjecture. This continuation adds **no generic Sacred Texts finding**:
the terrain matrix is a Pontifex placement outcome, while the observed
ACE/PhysX mass sequence is not a controlled product-neutral locality A/B.
Post-ingest `setMass` and `surfaceNormal` dossiers therefore retained only
their canonical upstream documentation.

## Accepted continuation — bounded shoreline and all-water placement

The next-best unblocked inventory candidate was Fabricator water-adjacent placement. Sacred Texts established that `surfaceIsWater` detects water and loaded pond objects, with Position3D Z ignored; `surfaceNormal` supplies terrain slope, while no indexed dossier existed for `BIS_fnc_findSafePos`. The product now treats the native helper result as a candidate: it must be non-water, at most 20 degrees, and inside the existing 15 m bound. A deterministic 15-degree bearing fallback scans the same bounded neighborhood. If no safe target exists, single and packed local orders return `no-safe-drop` before any object is moved, unhidden, or published; packed orders precompute every target so refusal stays atomic. Airdrop behavior is unchanged.

The permanent version-2 scenario holds the authenticated client, server authority, station, catalogue, two-object packed order, helper, and census constant. At a loaded Stratis shoreline it independently selects a water recipient with 36 suitable land rays; the authentic order settled its exact server-local two-object container at `[1465,4892,0]`, four metres from the recipient, on an 18.37-degree non-water surface. At `[0,0,0]`, every sampled point through 15 m was water; the matched order returned `no-safe-drop`, published no positions or containers, and left the exact mission-wide census unchanged. Final cleanup removed every created object, transaction, result key, and fixture.

Fresh run `20260826T143846Z-07b11de0` passed **31 server + 11 client assertions** with zero failures. Three immediately preceding cold diagnostics remain unaccepted: they exposed that late `surfaceIsWater` re-queries change when the coastline leaves the loaded area, exactly matching the canonical loaded-object caveat. The final fixture therefore records the water observation while the coast is loaded; it does not weaken any placement oracle.

Evidence package `urn:tribunal:evidence-package:20260826T143846Z-07b11de0:1` (payload SHA-256 `29ed606c6f2855111ce0e789ca078d42e73352016952be7ed373ef02bdf968e0`) contains five arms, one causal pair, and the demonstrated `pontifex:fabricator:bounded-water-placement` proposition. It was ingested twice with no second-pass count change. Reviewed distillation classifies the result as project-specific and adds no generic Arma proposition.

## Accepted continuation — severe-gradient recovery and refusal

The next highest-value unblocked candidate was the rejected severe-slope boundary. Sacred Texts documents `surfaceNormal` as the terrain-normal oracle and ignores Position3D Z; it does not establish a suitability threshold. Pontifex therefore retains ownership of the existing 20-degree maximum and 15 m search bound. No additional product mutation was required: the preceding water-placement refinement already validates candidate slope and makes local single and packed orders fail closed with `no-safe-drop`.

Reconnaissance around the previously rejected 63.3-degree face selected two fixed Stratis fixtures, but those diagnostics were not promoted. The fresh permanent scenario independently resamples both coordinates before authentic orders. At `[4573,6664,0]`, the recipient measured 34.03 degrees and 38 of 72 exact fallback-ring samples were moderate non-water terrain. The authentic two-object packed order selected `[4576.83,6657.95,0]`, a 7.39-degree surface inside the bound, preserved exact server locality/contents, and settled. At `[4603,6727,0]`, the recipient measured 38.03 degrees and all 177 points on a 2 m grid through 15 m were land at or above 36.66 degrees. The matched order returned `no-safe-drop`, published no positions or containers, and preserved the exact mission-wide census.

Fresh run `20260826T145821Z-152035b7` passed **33 server + 11 client assertions** with zero failures and exact cleanup. Its Evidence Contract v3 package `urn:tribunal:evidence-package:20260826T145821Z-152035b7:1` (payload SHA-256 `0e4f77aa66df6b316522c1e1521046bcfa109a6f191578824213dac677469378`) contains seven arms, two causal pairs, and demonstrated water and severe-gradient propositions. It was ingested twice without a second-pass count change. Reviewed distillation classifies the new finding as project-specific and adds no generic `surfaceNormal` proposition.

One preceding cold diagnostic proved both new slope assertions but failed the existing ACE carry observation; it remains unaccepted. Post-ingest dossier verification also exposed duplicate rendering when two packages corroborated the same proposition. Arma Knowledge now renders one note for equal non-run validity dimensions while retaining both immutable run references.

## Accepted continuation — multi-container placement atomicity

The next highest-value unblocked inventory candidate was multi-container placement atomicity. Ponds were blocked on a deterministic loaded fixture, and client-B/JIP were blocked on another authenticated identity. Canonical `createVehicle`, `setPosATL`, and `attachTo` material defined the underlying operations but did not establish Fabricator policy; ACE 3.21.0 source was inspected for the exact carry-weight and supported override paths.

The authentic eight-object baseline exposed three product defects. The packer accepted `_preferMultiple` and a four-small-object cap but ignored them, so eight light crates collapsed into one pallet. Once the already-valid geometric allocation was split into bounded groups of four, a refused transaction briefly exposed newly created pallets and successful pallets drifted after visibility and mass initialization. Pontifex now hides each transaction-owned container at creation, reserves every distinct target before moving anything, reveals only after complete reservation, and re-seats the server-owned containers before publication. Geometrically unpackable objects remain rejected; the split never turns one into an accepted item.

A matched permanent treatment/control pair drives the real terminal with eight `Box_NATO_Support_F` objects. With two independently validated targets available, the worker publishes two distinct server-local pallets with four attached crates each; both remain within 2 m of their announced targets and continuously settled for two seconds. With the same attempt-zero target but attempt one unavailable, the exact ten transaction objects (eight crates plus two pallets) are still hidden before refusal, neither pallet has moved to the first target, the result is `no-safe-drop`, no container or position is published, and the mission-wide census is unchanged.

The investigation also converted a repeated retained carry failure into a scoped product refinement. ACE computes carry weight from physical mass plus restored container cargo: at the real pre-publication boundary the heavy clone was mass 200 but ACE weight 308.5. ACE explicitly supports `ace_dragging_ignoreWeightCarry`; Fabricator now sets that replicated override only on an accepted single delivery, preserving its promised direct handoff without changing packed cargo policy. Client-a carried the exact clone successfully.

Fresh autonomous run `20260826T161950Z-c1a720a7` passed **35 server + 11 client assertions** with zero failures, no missing identities, and complete client/network/server/state cleanup. Evidence Contract v4 package `urn:tribunal:evidence-package:20260826T161950Z-c1a720a7:1` (payload SHA-256 `24781769d083c8413cb7aa3248750928c8237a73add5b370bfdb3b72e78a2762`; file SHA-256 `92acf41ca045855bf07fdaa47badf45f919a41091918b32948bd4848e81e34bc`) contains nine arms, three causal relationships, and three demonstrated propositions. Ingestion changed counts once from 26 to 27 packages and 27 to 28 runs, then remained stable on repeat. Reviewed distillation revision 12 classifies the new finding as project-specific, adds no generic lemma or conjecture, and is likewise idempotent.

## Accepted continuation — single-item bounded water placement

The inventory’s top unblocked candidate was the distinct single-item terrain-boundary branch. Ponds remained blocked on a deterministic loaded fixture and client-B/JIP on another authenticated identity. Sacred Texts established only the documented terrain operations: `setPosATL` positions relative to terrain, `surfaceIsWater` detects water and loaded ponds with Z ignored, and `surfaceNormal` returns the terrain normal with Z ignored. Pinned ACE 3.21 source confirmed the authentic carry-release function used between matched orders.

No product mutation was justified. Single and packed local deliveries already call the same bounded placement helper, but the direct-delivery branch has a different publication and ACE carry handoff. Evidence Contract v5 therefore adds authentic one-item terminal orders after releasing the previously carried object through ACE. A temporary observer wraps the real helper, snapshots the exact hidden server-local transaction clone before the decision, and delegates unchanged product behavior. The shoreline treatment must publish that identity on moderate non-water land inside 15 m, preserve exact cargo and mass 200, expose the supported ACE carry override, and attach the same net ID to client-a. The all-water control must return `no-safe-drop`, publish no identity or position, delete the exact hidden clone, and leave the mission-wide census unchanged.

The investigation also corrected two scenario-only fixture defects without weakening retained assertions. Multi-container targets are now pinned to an already validated exact land coordinate instead of inheriting sub-metre player replication drift across a terrain-cell boundary. The baseline fixture now publishes its intended base and waits until the server resolves both the declared player identity and that replicated coordinate before constructing the station. Rejected packages remain immutable and were not ingested.

Fresh autonomous run `20260827T173751Z-eab21efe` passed **37 server + 11 client assertions** with zero failures and complete cleanup. The shoreline recipient was `[1460,4903,0]`; the real helper selected `[1460,4906,0]`, a 16.86-degree non-water surface. Before the decision the exact `Box_NATO_Ammo_F` clone was hidden and server-local; immediately before publication it was visible, server-local, mass 200, 0.62 m from the selected point, and carried the replicated ACE override. Exact weapon, magazine, item, and backpack cargo matched, and client-a carried that same net ID. At the sea-origin control the helper returned no position, published nothing, and preserved the exact census.

Accepted package `urn:tribunal:evidence-package:20260827T173751Z-eab21efe:1` has 11 arms, four causal relationships, four demonstrated propositions, and 48 passing assertion results. Its canonical payload SHA-256 is `d4208c0285d7d4548b008dc98cf27ddcff5ea4e9d57aeec0dbe1d8aeedd87606`; file SHA-256 is `3922dc6397f7472574af4962c0497ec19dfa947e1781155887de6e2916c49e2b`. Ingestion and reviewed distillation were each idempotent on their second pass. Distillation revision 13 classifies the new theorem as project-specific and adds no generic lemma or conjecture. Final knowledge counts are 5,581 concepts, 774 artifacts, 28 packages, 6,446 relationships, 21 experiments, 29 runs, 5,941 judgments, 5,915 proofs, 5,831 propositions, 5,606 source revisions, 26,766 fragments, and 22,918 statements; the full audit accepted every check.

## Accepted continuation — terminal browsing, queue and invalid-grid rejection

The next highest-value unblocked inventory candidate was the reachable Fabricator terminal surface. Sacred Texts documented the exact UI primitives used by the implementation: `lbData` and `lbText` read row backing data and text, `lbPicture` reads row pictures, `lbSetCurSel` selects a row and fires its selection path, and the full form of `ctrlActivate` invokes button actions and ButtonClick handlers. Those documents establish command interfaces, not Pontifex catalogue, queue or grid policy.

No product mutation was justified. The shipped ACE action opens the real Field Utilities dialog; its onLoad initializes the authoritative virtual-storage catalogue, selection populates exact weapon/magazine/item/backpack rows, and live add/plus/minus controls maintain ordered quantities. The live submit button sends the accepted nearby order through the existing server-authoritative endpoint. In airdrop context malformed grid text exits before setting in-progress state, generating request identity or calling the server. Styling and the count-based progress animation remain outside the contract.

A first extension of the large transaction scenario reproduced the new browse/queue and invalid-grid assertions but inherited unrelated dense-obstruction settling and ACE-carry nondeterminism. Rejected runs `20260827T182731Z-aaca32f7`, `20260827T184025Z-ae780187`, `20260827T184533Z-845381af`, and `20260827T185102Z-bd0663d0` remain diagnostic only. The permanent `fieldutils-fabricator-ui` scenario therefore keeps the same real module, three exact catalogue objects, station, dialog and server endpoint while excluding terrain and carry physics. It observes exact row identities/names/pictures and four nested cargo rows, proves quantity 1→2→1, ordered two-row insertion and removal, submits the remaining one-item queue through the live button, then compares it with the same queue under malformed airdrop grid input. The control preserves its request sentinel and queue, leaves every overlay hidden, and produces zero server audit or census change.

Fresh autonomous run `20260827T190358Z-c39f2669` passed **4 server + 3 client feature assertions** with zero failures and complete client/network/server/state cleanup. Package `urn:tribunal:evidence-package:20260827T190358Z-c39f2669:1` has four arms, one causal relationship and one demonstrated proposition; payload SHA-256 is `715ed42f38071a622bec067fd41d0f42e12b2abfa5007ddde651808918d08431` and file SHA-256 is `efb066a479e6b7314b3df4b6c7246bbd00df5786628d54b76fd8fcf8d523bbc2`. Ingestion changed counts once to 29 packages, 30 runs and 793 artifacts and was stable on repeat. Reviewed distillation revision 14 classifies the result as project-specific, adds no generic lemma or conjecture, and is idempotent; the full ledger audit passes.


## Accepted continuation - empty catalogue and empty-submit rejection

The normal terminal proof already observes heavy, light and oversize catalogue rows and queues two distinct object classes, so an additional "alternate class" scenario would duplicate accepted behavior. The next distinct unblocked boundary was a valid Fabricator station backed by a registered Virtual Storage module with zero synchronized objects. Sacred Texts documents that `lbSize` returns listbox row count, `lbData` returns a row's backing data, and full `ctrlActivate` invokes button actions and ButtonClick handlers; none defines Pontifex empty-state policy.

Static review found a stale-selection lifecycle defect: page initialization reset the queue but retained `YFU_selected_fabricator_item`. A client reopening the page after a populated session could therefore carry an old selection into an empty catalogue. The page now clears that selection to `objNull` before refreshing the list. No server or packing behavior changed.

The permanent `fieldutils-fabricator-empty-ui` scenario uses the real module setters, a server-owned registered station, an empty storage module, the real dialog, and live Add and Submit buttons. The client observed exactly one `<No virtual storage items found>` row with empty data and picture, zero inspect rows, a null selection, and empty queue/dynamic controls. Both actions preserved the request sentinel and hidden overlay. The server independently observed unchanged exact station census, empty audit and transaction keys, followed by complete registration cleanup.

Fresh autonomous run `20260827T212148Z-9a38342f` passed **3 server + 1 client feature assertions** with zero failures. Package `urn:tribunal:evidence-package:20260827T212148Z-9a38342f:1` has three arms and one demonstrated proposition; canonical payload SHA-256 is `585f6312d724bf2ea7b1c1d1e26396abbcaa6a95bf46355c923429d41a1ecdcb` and file SHA-256 is `0b80aa47de438c8dfa1a65e3b88de380ef9fd997a3e394edea387daa66826888`. Ingestion and reviewed distillation revision 16 were each idempotent. The finding is project-specific and adds no generic lemma or conjecture; the full ledger audit passes.


## Accepted continuation - mixed-class packed manifest

The next bounded unblocked packing gap was not another catalogue row: the accepted UI scenario already observed heavy, light and oversize rows, while the main Fabricator scenario's packed treatment submitted two copies of the same light crate. No accepted order had crossed the real terminal, authoritative cloning and packing boundary with heterogeneous registered classes. Sacred Texts documents `typeOf` as the class-name query, `getWeaponCargo` as a cargo-manifest query, and `attachedObjects` as the attachment census; those commands provide independent observations but do not define Fabricator eligibility, packing or publication policy.

No product mutation was justified. Evidence Contract v2 extends the bounded `fieldutils-fabricator-ui` scenario after its retained one-item delivery. The real catalogue controls enqueue one `Box_NATO_Ammo_F` followed by one `Box_NATO_Support_F`, and the live Submit button sends those exact identities and quantities. The server independently resolves the published container IDs, enumerates their attachments, and requires exactly two visible server-local objects with the two source classes and exact weapon, magazine, item and backpack cargo. The proof deliberately leaves pallet count, allocation heuristic, orientation, offsets, visual neatness, collision-free geometry and other class/count matrices free.

Fresh autonomous run `20260827T213025Z-cd53bd2a` passed **5 server + 4 client feature assertions** with zero failures and complete cleanup. The result used one published pallet at `[4700.03,2783.99,0.00236225]`; its two attached clones were the exact heavy/light classes and retained their distinct cargo. Package `urn:tribunal:evidence-package:20260827T213025Z-cd53bd2a:1` has five arms, one causal relationship and two demonstrated propositions; canonical payload SHA-256 is `c00459764d3245da2beac0f6e81ab8a8596ed4eb2eb78e3f4a7c5e940d8592fa` and file SHA-256 is `f6204a4fd6b69831698b2cffdc757451c2e126c54b5bd9251653f7b93bbd2249`. Ingestion and reviewed distillation revision 17 were idempotent. The new finding is project-specific and adds no generic lemma, conjecture or theorem; the full ledger audit passes.

## Unresolved

* **Broader terrain suitability beyond the accepted matrix.** Ponds, other severe terrain shapes, suitable terrain farther than 15 m, other coastline shapes/islands, multi-container orders beyond the tested eight-light-crate/two-pallet matrix, single-item terrain boundaries beyond the tested shoreline/all-water pair, arbitrary obstacle shapes/densities, and collision-free clearance remain open.
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
scenario isolation; flat, moderate-gradient, dense-obstruction, shoreline and severe-gradient-recovery packed placement within the stated bounds; atomic all-water and all-severe refusal; exact pre-publication mass 200; and exact
client carry attachment. Pond, other-severe-terrain, other-coastline, land-beyond-15-m, multi-container orders beyond the accepted matrix, single-item terrain boundaries beyond the accepted shoreline/all-water pair, and arbitrary-obstruction suitability, actual client-b/JIP behavior, ACE-internal action visibility,
runtime-created editor synchronization, and Live-snippet supervision remain the
explicit follow-ups listed above; none is implied by the accepted PASS.
