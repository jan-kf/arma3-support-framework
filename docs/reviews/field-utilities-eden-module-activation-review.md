# Field Utilities Eden module activation — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REFINED; ACCEPTED / COVERED** for authentic typed Eden
dispatch, multiple-module aggregation, server-private catalogue/station
authority, current-client mirrors, the default local-inventory value, the
registered local virtual-inventory action's disabled/enabled gate, and
adversarial setter/mirror controls. Accepted Fabricator transaction and delivery
coverage remains the downstream behavioral baseline. Field Utilities defines no
Zeus activation tool.

Fresh autonomous proof: `20260821T153954Z-34a72701` — server 9 assertions and
client 7 assertions, zero failures, normal container/network/state cleanup.
The unchanged accepted Fabricator matrix was then rerun as compatibility proof:
`20260821T154740Z-81b7dd89` — server 26/client 10, zero failures, including the
authoritative no-storage refusal and normal cleanup.

Accepted continuation `20260827T223431Z-731a6c43` passed **10 server + 9
client assertions** with zero failures and complete client/network/server/state
cleanup. Authentic configured dispatch first established the default enabled
mirror. A one-variable control then published false and true without manually
calling a module setter. Client-a resolved the exact registered
`zenInventoryActions` action on crate `2:18`, 10.32 m from station `2:21`: the
active tree was empty while false and contained the same “Open Virtual
Inventory” action while true. Calibration run
`20260827T223241Z-dc829a2a` proved both new arms but remains rejected because the
false phase raced the older enabled-mirror assertion; an explicit baseline
acknowledgment corrected evidence ordering without changing product behavior.
Independent cold repeat `20260827T224324Z-e731d666` then reproduced all 10
server and 9 client passes, including both action-gate arms, with complete
cleanup. Attempt `20260827T223908Z-b6c159e0` is not feature evidence: Steam did
not become ready, no client joined, and no feature assertion executed.

## Scope and canonical review questions

### 1. What should the mission maker observe?

Every authentic Virtual Storage module contributes its exact synchronized
catalogue templates, and every authentic Fabricator module contributes its exact
synchronized stations. The combined catalogue is unlimited/non-depleting.
Clients receive discovery mirrors, but fabrication authorization uses only the
server-owned registration.

### 2. What does the implementation do now?

Both typed `Module_F` classes execute their configured setters at mission start.
Accepted server-local modules are recorded idempotently by network identity;
their synchronized objects are de-duplicated into private server catalogue and
station arrays. Separate arrays are replicated for presentation. Legacy
server-local plain-Logic setters remain supported for existing missions and the
accepted Fabricator scenario, but remote clients cannot use that compatibility
path. Both public module classes are now present in `CfgPatches.units[]`.

### 3. Which machines and lifecycle own it?

Native dispatch was measured on the server with `local logic == true`,
`owner logic == 2`, and framework `remoteExecutedOwner == 0`. The retained
non-disposable logics and mission-native Sync links remain available. Server
order validation reads `localNamespace`; public mirrors are not authority.

### 4. Which mechanics are generic?

Typed mission entities, validated Sync links, configured-dispatch receipts,
locality capture, and exact identity comparison are Tribunal mechanics already
proven by APS/CBR and reused here. Catalogue, station, inventory, and order
meaning remain Field Utilities policy.

### 5. Which behavior is product-owned?

Multiple module aggregation, unlimited catalogue semantics, exact registered
station authorization, local virtual-inventory gating, and compatibility with
server-local legacy mission setup are Field Utilities behavior. There is no
Field Utilities curator product surface.

### 6. Which engine facts were established?

Authentic `isGlobal=0` module functions execute server-locally; mission-SQM Sync
links resolve exact synchronized objects on the server and current client; and
non-disposable typed logic survives initialization. These are observations, not
requirements to preserve a particular private registry representation.

### 7. Which fragile details were corrected?

The prior last-writer-wins globals, missing `CfgPatches.units[]` entries, and
shared mirror/authority source were corrected. Registration is keyed and
aggregate, authoritative arrays are server-private, and remote setter calls are
rejected with bounded audit evidence. A client in the fresh run successfully
replaced both public mirrors with its player object; the private exact catalogue
and station sets remained unchanged.

### 8. Is a better native mechanism available?

The native Eden module and synchronization framework is the supported entry and
is retained. No custom editor or Zeus layer is needed. Public mirrors remain a
presentation transport rather than being promoted into server authority.

### 9. What is the stable contract and causal proof?

The permanent `fieldutils-eden-modules` scenario starts with two real typed
storage modules, two real typed Fabricator modules, and four native Sync links.
It independently resolves the exact named catalogue/station objects, requires
four accepted native dispatches and retained local logics, compares both private
aggregate sets, and verifies current-client mirrors/default inventory state. After client-a
acknowledges that baseline, the scenario holds the exact crate, station,
proximity and registered ACE action constant while the published inventory
switch changes false then true; inactive then active tree observations form the
causal pair. The client then sends both forged setters and publishes rogue mirrors. Exact
rejection receipts plus unchanged private identity sets prove the authority
boundary. Cleanup removes every fixture and empties the registrations.

### 10. Which details remain replaceable?

Setter names, audit layout, HashMap keys, mirror names/transport, module order,
logic netIds, scenario classes/coordinates, and aggregation implementation are
free. Typed supported entry, exact synchronized meaning, multiple-module union,
server authority, and fail-closed remote mutation are stable.

### 11. What remains unproven or deferred?

Mixed `Fabricator_Module_EnableLocalArsenal` values across multiple Fabricator
modules are deliberately fail-closed and are not accepted as a per-station
policy; all permanent fixtures use the documented default `true`. Runtime module
addition/removal, module deletion after init, a missing counterpart as a
standalone editor workflow, client-B, and JIP remain unproven. Existing accepted
order validation already fails closed when its exact catalogue/station source is
absent; this review does not re-prove the full transaction.

### 12. What belongs in Tribunal?

Only the existing typed-entity/Sync fixture and identity/locality evidence.
Field Utilities registration policy and adversarial semantics stay in its
product scenario. No new generic primitive or product meaning was promoted.

## False-PASS audit

A classname, manual setter, raw Logic, public mirror, dispatch receipt, action
registration, or successful pre-registered order is insufficient alone. The
accepted proof requires authentic typed dispatch and Sync identity, independent
named-object sets, the same registered action under exact false/true state,
observed remote stimuli/rejections, server-private state after successful public
poisoning, client replication, and bounded cleanup. It intentionally does
not claim mixed-checkbox, runtime-reconfiguration, client-N, or JIP behavior.
