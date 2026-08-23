# Vigil asset whitelist Eden/Zeus activation — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REFINED; ACCEPTED / COVERED.** Fresh autonomous proof covers
authentic multiple-Eden-module aggregation and two opposite operations in one
retained assigned-curator display: add an absent vehicle, then remove a distinct
present vehicle. The accepted unwhitelisted mixed-fleet browser remains unchanged.

## Canonical review questions

### 1. What should the mission maker and curator observe?

Every authentic Eden whitelist module contributes its synchronized vehicles to
one mission-wide discovery set. An assigned curator can add or remove the exact
vehicle selected through a genuine curator-module placement and receives the
result privately. Replayed, forged, invalid, or unrelated operations change
nothing. Clients refresh from the server-published exact membership snapshot.

### 2. What does the implementation actually do?

Native Eden configured dispatch validates retained typed module logics on the
server and rebuilds a server-private, deduplicated membership union. A separate
public snapshot carries exact object identities to clients; browser discovery no
longer depends on runtime synchronization replication. The native Zeus placement
event starts a bounded target-finalization step because the new module's
`attachedTo` relation and `curatorMouseOver` are not reliably available in the
event's first frame. It then submits one operation ID, exact module, assigned
curator, and resolved target to the server claim boundary. The server authenticates
the remote owner, module ownership/class, assigned curator and non-null target;
rejects replay; applies the membership toggle once; retires only the transient
module; and returns the result only to the placing curator.

### 3. Which machines and lifecycle own it?

The authoritative module registry, claim ledger and membership set are
server-private. Eden module dispatch is server-local. Curator placement and target
resolution originate on the assigned curator's client; `remoteExecutedOwner` is
bound to that curator and a fresh operation ID before mutation. Published
membership and result mirrors are observational only. Eden logics are retained
because their module config is non-disposable; transient Zeus logics are deleted
after finalization. Scenario state and audits are explicitly retired.

### 4. Which mechanics are generic?

Typed mission modules, native Sync links, assigned-curator setup, real curator
placement, exact identity/locality observation, bounded UI stimulus, and targeted
result transport reuse Tribunal mechanics. Eligibility, aggregation, membership
mutation and browser refresh are Vigil product semantics.

### 5. Which behavior is product-owned?

Multiple Eden modules aggregate as a union. Assigned curators are authorized.
Feedback goes only to the placing curator. Operation IDs make module operations
idempotent. The whitelist controls discovery, not separate task authorization.
Zero-module behavior retains the accepted unwhitelisted browser.

### 6. Are unusual engine requirements proven?

Yes, narrowly. Authentic typed Eden modules execute their configured handler and
retain exact native Sync identities. Two real assigned-curator placements in one
display produce distinct `CuratorObjectPlaced` events, authenticated server claims,
opposite exact-target mutations, and placer-only results. A freshly placed module
may have neither a usable attachment nor hover target in the event's first frame;
a bounded scheduled observation can resolve its real attachment without replaying
the placement. Runtime synchronization is not required for client membership
replication.

The scenario also established fixture boundaries rather than product rules.
Mission-authored vehicles required explicit known-land placement and a server-side
grounded stability gate. On the remote client, a stationary server-owned vehicle
could still report gravity-like velocity and `isTouchingGround == false`; replicated
position stability was therefore used only to prove the client fixture had settled.
Surface-intersection-derived screen candidates made each intended hover independently
observable. These observations do not specify general Arma behavior outside the
tested build and fixture.

### 7. Which details were fragile or incomplete?

The prior last-setter-wins public logic reference, client-side Sync traversal,
unguarded global toggle helper, broad feedback and absent replay identity were
false-PASS and authority risks. They were replaced by server-private aggregation,
an exact published snapshot, authenticated claims and requester-only results.
Requiring the server's curator-editable mirror to match the client's placement
frame was also rejected: cold evidence showed that cross-machine mirror was not a
stable authorization predicate. The established product policy authorizes the
assigned curator; exact target identity is instead correlated end to end.

### 8. Is a better native/existing mechanism available?

Native Eden and curator entry mechanisms remain the public surface. Server-private
membership is preferable to treating public variables or synchronization graphs
as authority. The existing curator event/claim/result infrastructure is reused;
Vigil does not import APS, CBR, or other product meaning.

### 9. What is the stable contract and causal proof?

The fresh mission contains two authentic Eden modules synchronized to different
eligible vehicles. Native dispatch yields their exact union, both retained module
identities, and the same exact client snapshot. In one retained curator display,
the first authentic placement targets absent vehicle C and adds its exact identity;
the second targets present vehicle A and removes its exact identity. Each client
placement record, server claim, server toggle, targeted result, and final replica
correlates by operation, transient logic, curator and target identity. Duplicate
replay and a forged invalid logic are receipt-proven rejected with membership
unchanged. Both transient logics and all scenario state are retired.

### 10. Which details remain replaceable?

Module positions/IDs, snapshot schema, handler names, operation-record layout,
browser grouping/order, notification prose, hover candidates, target-finalization
interval and audit layout remain free. Exact membership, assigned-curator
authority, idempotence, targeted result, authentic opposite transitions and
client-visible consistency are stable.

### 11. What remains unproven or requires experimentation?

Runtime Eden module deletion/reconfiguration; zero-sync and duplicate-module edge
policy beyond exact union; client-B/JIP isolation; curator reassignment and
ownership migration. Those are separate lifecycle or environment surfaces, not
qualifications on the accepted Eden aggregation and assigned-curator add/remove
contract.

### 12. What belongs in Tribunal?

Only generic typed-module generation, Sync links, assigned-curator placement,
hover/receipt telemetry and exact identity replication. Vigil membership policy,
authorization decisions and browser interpretation remain product-local.

## Evidence and reusable-knowledge disposition

The accepted Evidence Contract publishes two product propositions: exact Eden
aggregation and the assigned-curator toggle contract. Eden Sync behavior is
`ALREADY REPRESENTED GENERICALLY`; whitelist membership, authorization,
idempotence, feedback and removal semantics are `PROJECT-SPECIFIC ONLY`.
Same-frame curator attachment/hover timing and remote-client grounded-state
telemetry are `GENERIC ARMA CONJECTURE SUGGESTED` /
`NEEDS DEDICATED CHARACTERIZATION`: this product run did not contain controlled
generic A/B propositions broad enough to promote either as a verified Arma note.
Zero new generic lemmas is the correct distillation outcome.

## False-PASS boundary and accepted evidence

Direct setter/helper calls, plain runtime Logic, a published module reference,
internal Sync state, notification, deleted logic or cached browser rows are not
proof. Negative claims require a proven boundary receipt and unchanged independent
membership snapshot. Removal passes only when its second authentic hover,
placement, exact server mutation and client replica are all correlated.

Cold failures documented the refinement boundary: run
`20260823T171315Z-1b0fc913` proved that exact pre-click hover did not guarantee a
same-frame native attachment; run `20260823T172224Z-d1de1c06` disproved the
server curator-editable mirror as a stable cross-machine predicate; and run
`20260823T172822Z-0697cb14` showed same-frame event target capture could still be
nil. The final bounded target-finalization implementation then passed two
consecutive cold runs: `20260823T173516Z-c9b3b3db` and acceptance run
`20260823T173648Z-86506466`.

The acceptance run passed server 14/0 and client 10/0. It correlated operations
`whitelist-4-24964-972078` and `whitelist-4-26497-588851` with exact targets
`2:19` (added) and `2:13` (removed), exact transient logics `4:9` and `4:11`, and
assigned curator `2:162` owned by client 4. Replay and forged-logic controls were
rejected; the client resolved final members `2:16` and `2:19`; all assertions and
container/network/run-state cleanup passed.
