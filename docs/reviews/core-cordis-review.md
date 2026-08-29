# CORDIS routing, deduplication and fan-out review

## Scope and result

This review applies the canonical 12-question program to named-operation
routing to the server/object owner/group owner; server TTL deduplication;
recipient resolution and scoped fan-out; curator notification boundaries; and
bootstrap cache state in `mods/core/addons/CORDIS`.

**Classification: `REFINED; KEEP AS-IS AND SPEC-TEST — ACCEPTED / COVERED`.**

CORDIS remains a trusted broker between cooperating Pontifex components, not a
public adversarial RPC or gameplay-authorization boundary. The refinement makes
its routing result honest, resolves owner IDs only where Arma documents them as
authoritative, scopes once-keys by route and operation, validates work before
claim, prevents explicit empty scopes from broadening, and safely prunes expired
keys. Permanent `cordis-routing` coverage owns this product contract.

Curator UI presentation, side-radio audible output, debug presentation,
ownership migration, multiple-client fan-out, disconnect, and JIP remain
outside this accepted one-client broker contract.

## Stable contract

A known trusted operation routes to the declared server, object owner, or group
owner. Caller-visible results distinguish `rejected`, `queued`, `accepted`, and
`executed` broker boundaries; none claims remote gameplay completion. A
nonempty route-and-operation-scoped key suppresses a duplicate accepted request
within its positive TTL and is reusable after expiry. Unknown operations,
invalid destinations/TTLs, and empty recipient sets reject without consuming a
key. Scope `0` deliberately targets every live human player; an explicit side,
object, or list targets only matching live human players, and an empty/wrong
scope delivers nowhere. Consequential consumers own authorization and terminal
acknowledgment.

## Sacred Texts used first

Sacred Texts resolved the important engine boundaries before refinement:

* `owner` is authoritative on the server and otherwise returns `0`; clients use
  `clientOwner` for their own identity.
* `groupOwner` works only on the server and always returns `0` on clients.
* `setGroupOwner` is server-only, moves a non-player-led group and its units,
  and reports whether locality changed.
* `remoteExecCall` selects unscheduled remote execution; “Call” does not mean
  immediate or completed execution.
* `remoteExecutedOwner` identifies the remote initiator, with documented `0`
  contexts. The existing verified native Eden-dispatch lemma is narrower and
  was not generalized to CORDIS.
* `allPlayers` includes ordinary players plus headless and virtual entities, so
  a real-player scope needs explicit filtering.

These texts prevented client-side owner targeting and false completion claims.
They also exposed that historical `introduced_in` versions remain currently
applicable, not historical-only limits. `BIS_fnc_listPlayers` was absent as a
retrievable canonical subject and returned empty in the tested dedicated
context, so the accepted implementation uses documented `allPlayers` plus an
alive-human intersection.

## Canonical 12-question review

1. **What should an integrator observe?** A trusted named operation runs on the
   requested authority exactly once within a requested TTL; scoped messages go
   only to resolved live human players; invalid work produces an explicit
   rejection and no later suppression.

2. **What did it do before refinement?** Missing names became `{}` and silently
   succeeded; remote requests returned `nil`/`true` without distinguishing
   queueing from execution; raw keys collided and were claimed before
   destination/recipient validation; group routing used unit locality while
   targeting group ownership; empty curator scopes became broadcast; resolver
   argument/control-flow defects rejected valid object/list scopes; cache
   pruning mutated a hashmap during iteration and could skip expired keys.

3. **Which machines own it?** The server owns nonlocal destination resolution,
   deduplication, and recipient selection. A machine already local to the
   object/group may execute a basic route directly. The permanent scenario
   records server owner `2`, client owner `4`, `remoteExecutedOwner`, object and
   group locality, and exact destination callback counts. Client-B/JIP and
   ownership migration remain deferred.

4. **Which mechanics are generic?** Native `remoteExecCall`, `owner`,
   `groupOwner`, `setGroupOwner`, `local`, `allPlayers`, and transport-origin
   observation are Arma mechanics. The scenario-local transferred group and
   receipts are fixtures; Tribunal needs no new generic primitive.

5. **Which behavior is product-owned?** CORDIS owns supported routes, operation
   validation, status vocabulary, key namespace/TTL policy, recipient filtering,
   explicit broadcast, and empty-scope rejection. Consumers own operation
   authorization, payload meaning, resources, transactions, and terminal
   gameplay outcomes.

6. **Are unusual engine requirements proven?** No product workaround is frozen.
   Sacred Texts already document server-only owner queries. The run proves a
   settled non-player-led AI group transfers successfully, but the one-second
   fixture settle is not claimed as engine-required characterization.

7. **Which details were fragile or incomplete?** Default-empty function lookup,
   mixed booleans, pre-validation claims, raw global keys, unit/group locality
   mismatch, branch-heavy heterogeneous scope decoding, mutation during hashmap
   iteration, and curator broadcast fallback were false-PASS risks and were
   removed. Reserved init-settings/utils files remain scaffold only.

8. **Is a better mechanism available?** Native remote execution and ownership
   commands remain appropriate. A generic terminal-receipt subsystem would add
   machinery that no current consumer needs; existing consequential consumers
   already publish feature-owned terminal state. Explicit candidate
   normalization and operation-qualified keys are the smallest supported repair.

9. **What is the causal proof?** Destination callbacks independently record
   exact token, count, machine and transport origin. Inside-TTL duplicate,
   same-key/different-operation, comfortably post-expiry reuse,
   missing-then-defined, null-then-valid, explicit-empty, wrong-side, and
   deliberate-global arms all reach their decision boundary. Exact client
   callbacks independently prove emit delivery and negative-scope absence.
   Curator notification coverage stops at the server recipient-decision boundary:
   Arma marks both BIS GUI functions final, so the rejected override experiment
   is not treated as a delivery oracle. Cache/result flags alone are never the
   oracle for execution or fan-out.

10. **Which details remain free?** Function/cache variable names, hashmap shape,
    pruning cadence, status array representation, transport syntax, fixture
    classes/coordinates, exact TTL duration, and callback schema may change
    while the stable outcome remains.

11. **What deserves characterization?** Nothing new. The run supplies a product
    specification. Its native group-transfer and transport observations are
    supporting fixture evidence, not sufficiently isolated cross-context Arma
    lemmas.

12. **What belongs in Tribunal?** Only the existing generic scenario runner,
    identity-aware assertions, evidence packaging, and cleanup machinery.
    `cordis-routing` stays in `mods/core/tests/tribunal`; no CORDIS semantics
    enter generic Tribunal code.

## Permanent evidence matrix

| Claim | Independent evidence and controls |
| --- | --- |
| Honest result boundary | local server receipt, client queued result, direct transport positive control, server callback origin |
| Operation-aware TTL | exact callback counts for first/duplicate/different-operation/expired requests |
| Failure does not claim | missing-then-defined and null-object-then-valid pairs reuse the same operation/key |
| Object/group destination | server-local callbacks plus client-owned object and explicitly transferred AI-group receipts |
| Exact emit recipients | client callback census for object/list/global; delivered duplicate/empty/wrong-side controls |
| Curator notification decision | exact live-player, explicit-empty, and wrong-side server decisions; visible BIS GUI output explicitly unproven |
| Cleanup | client completion acknowledgment, transferred group returned/deleted, object deletion, and no tokenized cache key after prune |

The scenario carries Evidence Contract v1 product semantics with treatment,
negative-control, replication, causal relationships, bounded applicability, and
three explicit propositions. It intentionally does not convert passing
assertions into generic engine theorems.

## Controlled investigation history

Fresh diagnostic runs failed closed and each drove one bounded correction:

* `20260823T122837Z-899d9d43` exposed malformed filter call shapes, local-object
  validation ordering, an invalid default-player-group fixture, and a callback
  absent from the client preflight surface.
* `20260823T123303Z-e987fce6` proved server-local routes/dedupe but showed the
  transferred-group fixture needed a settle and direct transport control.
* `20260823T123858Z-cb82be29` proved client object/group ownership and
  client-to-server origin, isolating recipient resolution.
* Live run `20260823T124142Z-c028c123` recorded one connected real player with
  `isPlayer=true`, alive, `Man=true`, headless=false; direct filtering and array
  scope succeeded while object and scalar branch shapes diverged.
* `20260823T124442Z-8f049a62` proved deliberate global delivery and exposed an
  expired hashmap entry skipped during mutation-in-iteration pruning.
* `20260823T124814Z-ec8b53d3` confirmed safe pruning and kept the remaining
  failure strictly at heterogeneous object/list normalization.
* `20260823T130120Z-e2a5b7fc` proved the cold scenario retained an init-time
  player unit after Arma had retired it: owner remained `4`, but it was dead,
  no longer a player, and absent from `allPlayers`. The fixture now reacquires
  and asserts the sole live client-owned player at the consequential boundary.
* `20260823T130433Z-48f72009` proved all routing/fan-out assertions, then exposed
  the invalid GUI oracle: Arma rejected attempts to override final BIS curator
  functions. That oracle was removed and its claim explicitly deferred.
* `20260823T130828Z-567a712a` passed the narrowed matrix (server 16/0, client
  8/0), with complete cleanup. Its package then failed ingestion before mutation
  because human-readable pseudo-keys were not canonical Sacred Texts concept
  keys; the source contract was corrected and regenerated in the final run.

Run `20260823T131215Z-e3def785` passed and first proved canonical-key ingestion;
the adversarial review then caught a stale rationale describing the already
rejected GUI interception. Final fresh run `20260823T131712Z-6210a6c1`
regenerated the corrected artifact and passed server 16/0 and client 8/0 with
client/server containers, private network, and run state removed. Its Evidence
Contract v1 package ingested successfully into `arma-knowledge`; a second
identical ingest left all database counts unchanged. The product dossier contains
three exact-domain theorems. Reviewed distillation classified all three as
`project_specific_only` (zero generic theorems/lemmas/conjectures), because the
run corroborates documented engine mechanics but isolates CORDIS policy.

## False-PASS audit and unresolved boundaries

A wrapper state, key entry, missing callback, or consumer guard cannot establish
correct CORDIS routing. The permanent scenario therefore requires destination
receipts and exact positive/negative emit-recipient observations; notification
coverage is explicitly limited to the authoritative recipient-decision boundary. Unique run tokens,
operation-qualified keys, a 1.5-second margin beyond a 1-second TTL, direct
transport control, and post-run cache/object cleanup prevent stale satisfaction.

Still unresolved: visible curator notification delivery, second-client
fan-out/isolation, JIP/disconnect, locality migration during an accepted request,
audible side radio under a sound-enabled observer, and debug/systemChat
presentation. These do not weaken the accepted one-client trusted-broker
contract and must not be inferred from it.

## Terminal disposition

CORDIS routing, once-deduplication, result boundaries, recipient resolution, and
curator recipient-decision behavior are refined and permanently covered for
dedicated server plus one authenticated client. Visible curator GUI presentation
is not claimed. The contract is deliberately narrower than public RPC security
or remote gameplay completion.
