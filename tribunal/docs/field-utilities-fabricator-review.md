# Field Utilities Fabricator and Virtual Storage — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Primary outcome: `REFINE BEFORE PERMANENT COVERAGE`. Refinement is now done and
permanent coverage exists** (`fieldutils-fabricator`), following the product
decisions recorded below. One clause could not be proven and is deliberately not
asserted; see *Mass cap: preserved but unprovable*.

## Scope

In scope: Virtual Storage and Fabricator module registration, the fabricator ACE
action, the asset browser and order queue, single local fabrication, multi-item
packing and local delivery, inventory fidelity, authority/locality, and cleanup.

Explicit non-scope: the airdrop handoff, which is already covered as a composite
by `vigil-fixed-wing-logistics`; Bridge Builder; towing; FPV; ropes. The ZEN
virtual-inventory action is in scope only for its registration condition.

Source: `source/field-utilities/addons/FieldUtils/`, principally
`functions/fabricator/fn_assets.sqf`, `functions/fabricator/fn_boxPacking.sqf`,
`functions/fabricator/fn_fabricationActions.sqf`,
`functions/global/fn_fabricator.sqf`,
`functions/global/fn_initModuleLogicSetters.sqf`, `config.cpp`, and
`ui/pages/page_assets.hpp`.

Inventory status at review start: section 4.1, *Implemented; NOT YET REVIEWED /
PARTIALLY COVERED*, listed as the number one review priority.

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
`publicVariable` the two logics, so discovery is server-owned and JIP-safe. Every
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
placement, the mass cap, and the order lifecycle. Four product decisions are
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
* **Magic constants:** mass capped to 200 for `ReammoBox_F` above that mass
  (measured: a 500-mass source clones to 200), station altitude `> 200` shifts
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

Cold run `20260818T012304Z-571d8734` passed **25/25** assertions with zero
failures and complete container/network/state cleanup, driving every order
through the terminal submit path with no human input.

Selected evidence from that run and the ones that shaped it:

* single order delivered server-owned and beside the player -
  `result=[...,true,"single","2:158",[],[[9.98,12.31,137.99]]]|localOnServer=true|owner=2`;
* packed order - `containers=1|attached=2|allLocal=true`;
* atomic refusal of an unpackable order - `result=[...,false,"unpackable"]` with
  `censusBefore` equal to `censusAfter` and zero staged objects;
* `unregistered`, `out-of-range` and `no-storage` refusals, each census-matched;
* client stations - `clientStations=["2:148","2:149"]|registry=["2:148","2:149"]|idempotent=true`;
* teardown - `census=[0,0]`.

Nine earlier cold runs were needed to reach it, and the failures were real
rather than flaky: an unstable player position at fixture time (the anchor was
sampled the instant the player object appeared, before it had been placed), the
6,168 m delivery, the deep-staging and hidden-object mass readings, unscheduled
`uiSleep`, and the client reading editor synchronization before it had
replicated. Each was diagnosed from run evidence and fixed at its cause.

## Evidence index

All runtime evidence came from Developer Live Mode sessions
`20260817T205801Z-a3fdabcf` (baseline, pre-refinement) and
`20260817T211959Z-4e6658de` (post-refinement), with the poller A/B spanning
`20260817T205801Z-a3fdabcf` and `20260817T211507Z-87c52150`. Live Mode is a
development aid; none of it is a fresh autonomous proof, and none is claimed as
one. The fresh autonomous proof is recorded above.

## Independent audit remediation

An independent audit of the first coverage attempt returned eight blocking
findings. All eight were verified and correct.

**Fixed.** Caller identity now comes from `remoteExecutedOwner` and never from
the payload, so a client can no longer submit another player's identity. A
request id is claimed before anything is built, so a replayed or concurrent
request is refused. Order entries are schema- and integer-bounds-checked before
expansion. The `_isAirdrop` flag can no longer skip validation outright: an
airdrop order must at least name an `Air` object, which is what the Vigil
composite path supplies. A published result and its ledger entry now retire
together, so neither accumulates and a stale entry cannot resolve a recycled net
id. Mass was removed from the permanent behavior contract and from the declared
evidence types, matching the fact that nothing about mass is asserted. The
refusal and cleanup census compares sorted net-id sets rather than counts, and
additionally asserts the catalogue sources survive, so a leaked clone and a
deleted source can no longer cancel out. The review and inventory no longer
contain their pre-refinement conclusions.

**Confirmed and deferred, with evidence.** *Placement suitability.* The audit is
right that bounding a delivery to the player is not the same as proving the spot
is clear. An attempt to reject unsuitable positions using `surfaceIsWater` was
made and reverted: the validation tier runs `-world=empty`, where that test
refused every position and the whole scenario failed with `no-placement`. A real
suitability check needs terrain the validation world does not have, so the
fallback is documented in the source as bounded-but-unverified rather than
approximated. *Transaction finalizer.* Cleanup is proven for the failures the
server detects; a general finalizer covering script errors, result-publication
failure and client timeout is not implemented. *Malicious runtime controls.* The
refusals above are guarded by static contracts only; no runtime control exercises
a spoofed caller, a replay, an airdrop bypass or a malformed order. *Live snippet
supervision.* The poller no longer dies, but spawned snippets still have no
result, timeout, or concurrency bound.

These four remain open and this feature should not be treated as having a proven
adversarial boundary.

## Next review

Two things remain open on this feature. The delivery mass cap never fires,
because a fabricated crate does not report a real mass on a dedicated server;
that needs the real cause, not another guess. And the scenario has no runtime
control for a spoofed caller, a replayed request, an airdrop-flag bypass, a
malformed order, or an order with no valid placement - the server now refuses all
of them and static contracts guard the refusals, but only the honest single-client
path has been exercised end to end.
