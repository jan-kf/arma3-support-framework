# CORDIS routing, deduplication and fan-out review

## Scope and result

This review applies the canonical feature-review program to the shared CORDIS
runtime in `source/core`: named-function routing to the server, object owner and
group owner; local/server TTL claims; once-routed operations; recipient
resolution and scoped fan-out; side chat/radio, curator notification and debug
wrappers; and bootstrap state.

**Classification: `REFINE BEFORE PERMANENT COVERAGE` (reviewed; not covered).**

CORDIS has a coherent and heavily consumed locality-routing purpose, but the
current implementation conflates queued, accepted and executed results; claims
dedupe keys before proving downstream delivery; shares raw keys across unrelated
operations; silently treats missing functions as success; and turns an empty
curator scope into a broadcast. Most importantly, the repository does not say
whether named operations are trusted internal calls or an authorization
boundary. Permanent coverage would otherwise fossilize accidental security and
failure semantics relied on by several accepted features.

## Candidate stable contract

A trusted named operation routes once to the declared server, object owner or
group owner. A nonempty operation-scoped key suppresses duplicate accepted
operations for its stated TTL and becomes reusable after expiry. Invalid
destinations and unknown operations fail without consuming the key. Recipient
resolution includes only the requested live real players; an empty scoped
recipient set delivers to nobody. A request result distinguishes queued,
accepted, executed and rejected states, and consequential consumers provide
their own authorization plus terminal acknowledgment.

This candidate records the smallest coherent runtime behavior. The trust,
receipt, key namespace and empty-delivery decisions below must be confirmed
before it becomes an accepted contract.

## Canonical review

### 1. User or integrator observation

CORDIS is a framework dependency rather than standalone gameplay. Its README
promises authority-aware execution, one-shot/TTL deduplication, reliable target
resolution, scoped feedback and shared diagnostics. Consuming mods call it by
global named functions. An integrator should therefore observe the operation on
the intended machine, no duplicate within the agreed window, delivery only to
the requested players, and an honest failure/result—not a UI effect specific to
any consuming feature.

### 2. Current behavior and negative paths

Basic routes call a mission-namespace function locally when already at the
declared destination or `remoteExecCall` the supplied function name otherwise.
Missing names resolve to `{}`, so local calls silently do nothing. Remote routes
return `nil`; once wrappers generally return `true` as soon as a request is sent
or a key is claimed.

Server and local caches store raw key expiry times. Empty keys bypass dedupe;
zero or negative TTLs expire immediately. The once server/object/group wrappers
claim a server key before executing or routing. Missing functions, invalid
downstream owners and failed remote execution can therefore consume a key while
the wrapper reports success. All operations and callers share one raw-key
namespace.

Recipient resolution supports scope `0`, side, one object or an array and
filters to alive players. Scoped emit claims before resolution, so an empty
scope consumes the key and returns false. Curator notification instead converts
every empty resolved scope—including a wrong side or dead/invalid player—into a
broadcast to all alive players. Chat/radio wrappers inherit the generic fan-out.

### 3. Authority, locality and lifecycle

CORDIS chooses an execution destination; it does not currently establish that
the caller is authorized. The `*Once` gateways accept caller-provided function
names and arguments, and server guards do not validate `remoteExecutedOwner` or
an operation registry. Consequential accepted features have added their own
capabilities/request validation, which is evidence that routing is not itself a
security decision.

Object routes use `owner _object` and shortcut on `local _object`. Group routes
target `groupOwner group _unit` but shortcut on `local _unit`, not locality of
the group. That mixed criterion needs a controlled owner/group-owner A/B; it
must not be declared correct from source alone. Ownership migration, disconnect
and JIP behavior are unproven.

There is no generic execution receipt. A client-side `true` means only that a
request was queued, while a server-side `true` can mean a key was consumed even
if no named operation ran. This return-shape ambiguity is unsafe for resource or
transaction decisions.

### 4. Generic mechanics

Object/group ownership transitions, execution-machine identity, exact receipts,
timing and target-client observation are Tribunal mechanics. The existing
`locality-probe` already proves server-to-client object ownership and exact
client execution without CORDIS semantics. CORDIS owns the routing, key and
recipient policy interpreted from that evidence.

### 5. Product-owned behavior

CORDIS owns supported destination types, operation registration/trust, key
namespace and TTL rules, failure/result semantics, recipient filtering,
empty-scope behavior and feedback routing. Consuming mods own authorization for
their gameplay operations and the meaning of their payloads. CORDIS must not
turn “owner-local” into permission to mutate an object.

### 6. Claimed engine requirements

No CORDIS-specific engine workaround is characterized. Tribunal has separately
established that a newly created network object must first report stable owner
2 before transfer on this dedicated build; that capability fact does not prove
CORDIS group routing, remote result semantics or ownership-migration behavior.
Audio remains unproven under autonomous `-noSound` clients.

### 7. Fragile or incomplete details

Unknown names becoming empty code, unqualified global keys, pre-delivery claims,
mixed queued/executed booleans, group shortcut mismatch, heterogeneous list
assumptions, and empty-curator broadcast are false-PASS or boundary risks.
Debug calls are globally routable and optional client messages are not
acknowledged. The two reserved preInit files have no behavior and should not
receive tests.

### 8. Better native or existing mechanisms

Arma native `remoteExecCall`, `owner`, `groupOwner` and target arrays are the
underlying mechanisms already used. Tribunal's locality fixture can observe the
generic engine boundary; it is not a replacement product runtime. An explicit
registered-operation surface and terminal receipt may be safer than arbitrary
names, but adopting one requires the trust and compatibility decisions below
plus a controlled migration of real consumers.

### 9. Stable contract and causal proof

Permanent proof must correlate a unique operation identity with the actual
execution machine and an independently recorded execution count. It must cover:

* local and remote server/object/group destinations;
* one accepted operation, a duplicate comfortably inside TTL, and reuse well
  beyond expiry;
* same raw caller key used by different operations/callers, according to the
  chosen namespace policy;
* missing operation, null/invalid destination and no-recipient failures without
  false success or unintended key consumption;
* global, side, object and list fan-out with exact recipients, plus proven
  wrong-side/empty controls;
* ownership transfer and cleanup;
* one-client replication only, with multi-client/JIP explicitly deferred.

Cache state is not the oracle for execution. Every phase needs a destination-
side receipt containing operation ID, machine identity, owner/locality and
transport origin. Negative controls must prove the request reached the decision
boundary.

### 10. Replaceable implementation details

Function names, cache variable names and hashmap layout, time source, transport
syntax, key representation, pruning cadence, wrapper return representation,
radio normalization and notification UI are replaceable. The eventual promise
is honest destination, dedupe, recipient and result behavior.

### 11. Characterization

Nothing new is characterized. In particular, local-unit group shortcut,
pre-routing key claim and raw global keys have no retained alternatives proving
they are engine-required or deliberately architectural.

### 12. Tribunal promotion

No new generic primitive is justified initially. Extend or compose the existing
locality evidence with scenario-local execution receipts. Only promote a generic
group-ownership or recipient-fan-out observer if the first CORDIS scenario shows
a product-neutral gap and another real consumer.

## Required product decisions

1. Are arbitrary named routes a trusted internal API, or must CORDIS authorize a
   registered set of remotely callable operations?
2. Does a route report queued, accepted or completed execution, and is a generic
   terminal receipt part of the API?
3. Are dedupe keys global raw strings, or qualified by operation and optionally
   caller/target?
4. Does an invalid/missing operation, destination or recipient consume a key?
5. Is an empty explicit scope always no delivery, or may any named API request a
   deliberate broadcast fallback?
6. Which alive/dead players, headless clients and JIP identities belong in each
   recipient scope?
7. What compatibility guarantee applies when object/group ownership changes
   between request and execution?

## Precise continuation point

First select the trusted-operation and result/receipt policies. In one retained
Live session, register a harmless tokenized callback and execute the scout's
bounded matrix: client-to-server duplicate/expiry; server-to-client-owned object
routing; AI group-owner routing; missing function and invalid object; same key
across two operations; global/side/object/list emission; and a wrong-side empty
curator notification. Record execution owner, locality, `remoteExecutedOwner`,
exact count, key reuse and recipient identities.

Refine only the failures demonstrated by that matrix. At minimum, unknown or
undeliverable operations must not return success or burn a key, explicit empty
scopes must not broaden into broadcasts, and group routing must follow the
proven group owner. Migrate one non-consequential consumer first; accepted
gameplay consumers must retain their own authorization and terminal semantics.

## False-PASS audit

A wrapper return, cache entry, emitted hint or accepted consumer outcome does
not prove CORDIS selected the correct machine, executed once or reached the
correct recipient. A missing callback can look deduplicated; an empty wrong-side
scope can look delivered because of the current broadcast fallback; a local
shortcut can hide incorrect owner targeting; a consumer's own duplicate guard
can mask broken CORDIS dedupe; and one client cannot prove fan-out or JIP.
Future assertions must use fresh operation IDs, independent destination receipts
and comfortably separated TTL timing, and must fail closed on every absent,
extra or wrong-recipient execution.

## Terminal disposition

CORDIS is now reviewed but remains uncovered. The current routing can continue
as an internal dependency, but it must not be described as an authorization or
completion boundary. The seven decisions and one-session discriminating matrix
are the exact gate before product refinement and permanent coverage.
