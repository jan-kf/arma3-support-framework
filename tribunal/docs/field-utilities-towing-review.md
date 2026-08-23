# Field Utilities towing — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: `REFINED; ACCEPTED / COVERED` for one authenticated client
and server-local land vehicles.** Fresh autonomous run
`20260823T190019Z-39badbd1` passed 14 server and 13 client assertions with
complete cleanup. Player-owned vehicle locality, ownership migration,
client-B/JIP, broad fallback geometry, deletion/disconnect, and a natural
projectile-cut rope remain explicit follow-ups.

## Scope

The accepted surface is the reachable `LandVehicle` ACE attach/stow path,
configured or geometry-derived tow points, authenticated request boundary,
feature-owned rope lifecycle, native tow parenting, physical movement, and
client result/replication. The orphan four-point helicopter sling helper remains
separately deferred.

## Canonical review questions

### 1. What should the user observe?

A nearby authenticated player can select an exact eligible land vehicle and
request a tow. Acceptance creates one complete tow operation; the cargo follows
the moving tower. A conflicting, distant, or wrong-class request changes
nothing. Stow or rope loss detaches the pair without destroying unrelated ropes,
and the pair can be reused.

### 2. What does the feature actually do?

The ACE child resolves an exact `LandVehicle` pair and sends an operation ID to
`YFU_fnc_towRequestServer`. The server authenticates
`remoteExecutedOwner`, the owning player, range, class, movement, and existing
rope/tow claims. It computes the existing configured/fallback geometry, creates
all ropes atomically, retains their exact handles, applies `setTowParent`, and
publishes exact transaction/vehicle/rope identities. Stow and the loss monitor
destroy only those handles, clear the exact cargo parent and claims, publish a
requester-only result, and retire state.

### 3. Which machines and lifecycle stages own it?

The server owns authorization, mutation, rope handles, audit, active claims,
monitoring, and finalization for the accepted server-local topology. The client
owns ACE resolution and requests, then observes targeted receipts and replicated
transaction/rope identities. `getTowParent` was observed as locality-specific:
the authoritative server saw the exact parent while the non-owning client
correctly saw none, so the client proof does not demand a false replicated
parent.

### 4. Which mechanics are generic?

ACE data inspection, exact object/netId correlation, locality recording, paired
trajectory sampling, negative-stimulus delivery, and bounded cleanup are generic
testing mechanics. No new Tribunal primitive was needed.

### 5. Which behavior is product-owned?

Land-vehicle eligibility, 10 m requester range, 20 m pair range, 5 km/h motion
limit, single active relationship per object, server authority, exact rope
ownership, tow-parent use, requester-only results, and terminal cleanup remain
Field Utilities policy.

### 6. Are unusual engine requirements proven?

Yes, narrowly on Arma 3 2.22.153995: server-local `B_MRAP_01_F` plus
`C_Offroad_01_F`, native ropes and `setTowParent`, caused the cargo to follow
a naturally AI-driven tower. In the final A/B, the no-tow tower moved 26.3958 m
while cargo moved 0 m; treatment tower moved 27.0593 m while the exact cargo moved
28.3352 m. This does not generalize to every class or locality topology.

### 7. Which prior defects were refined?

The actor client formerly mutated world state, discarded rope handles, accepted
broad `AllVehicles`, and stow destroyed every rope on the tower. There was no
atomic result, conflict ownership, loss finalizer, reuse proof, or causal
movement control. The authoritative transaction removes those false-PASS and
broad-destruction paths.

### 8. Is a better mechanism available and proven?

The retained native rope plus tow-parent mechanism is sufficient for the proven
topology. No custom physics replacement is justified. The server rejects or
fails closed when its complete relationship cannot be observed.

### 9. What is the stable contract and causal proof?

> A nearby authenticated player may establish one exact, complete,
> server-authoritative land-vehicle tow. The same physical movement tows cargo
> only with the accepted operation. Conflicts and invalid requests do not
> mutate state; stow or rope loss removes only feature-owned state and permits
> reuse.

The permanent scenario correlates requester, exact pair, operation, exact rope
IDs, authoritative parent, client-visible transaction/ropes, and paired
trajectories. Its matched no-tow arm is an independent physical oracle.

### 10. Which details remain replaceable?

ACE labels/icons, helper names, operation storage, rope type/count/length, point
coordinates, audit representation, monitor cadence, and the native mechanism
remain implementation details unless a later contract requires them.

### 11. Which follow-up characterization remains?

Player-owned vehicles, ownership migration, client-B/JIP, natural projectile
rope cutting, deletion/disconnect during an active operation, and multiple
unconfigured vehicle geometries. These do not dilute the accepted topology.

### 12. What was promoted into Tribunal or Sacred Texts?

No product semantics moved into Tribunal. The scenario uses existing generic
assertion, locality, and evidence machinery. Evidence Contract v1 was ingested
idempotently and the knowledge audit passed. Both propositions are
`PROJECT-SPECIFIC ONLY`; the product transaction does not independently prove
a context-free engine theorem, so zero generic distillation is correct.

## Permanent evidence

Scenario: `source/field-utilities/tests/tribunal/towing.py`.

Fresh run `20260823T190019Z-39badbd1`:

- server 14/0; client 13/0;
- exact treatment ropes `2:160`, `2:161`;
- no-tow cargo 0 m versus treatment cargo 28.3352 m;
- active-object conflict rejected with delivered `active-conflict` receipt;
- exact feature ropes removed while unrelated rope `2:162` survived;
- destroyed feature rope triggered `rope-lost`, cleared the parent/claims, and
  the same pair attached and stowed again;
- distant requester and wrong-class cargo were delivered and rejected without
  mutation;
- all fixture objects, operations, claims, containers, network, and run state
  were removed.

Evidence emission initially failed closed on a noncanonical arm role and
knowledge ingestion rejected display-name BIKI context. Those metadata defects
were corrected to `baseline` and canonical `biki-page:*` keys; the regenerated
package validated, first ingest changed counts, second ingest was idempotent,
and the full knowledge audit passed.

## Disposition

**REFINED; ACCEPTED / COVERED** within the stated server-local, one-client
boundary. Retain the permanent causal scenario and focused static contract.
Treat the separate helicopter sling helper and the locality/client-N experiments
as independent future work.
