# Advanced Systems CBR Eden and Zeus activation review

## Scope and result

This review applies the canonical feature-review program to the two public CBR
module surfaces: the Eden `YAS_CBR_Module` and curator-visible
`YAS_CBR_Zeus_Toggle_Module`. It covers configured engine dispatch, module
identity, server transition, authority, feedback and transient logic cleanup.
The already accepted CBR detection, prediction, marker, warning and lifecycle
behavior remains governed by the main CBR review.

**Classification: `REFINED; ACCEPTED / COVERED`.**

Fresh autonomous run `20260821T153013Z-0a8b2c91` passed 14 server and 8 client
assertions. It proved native server-local Eden dispatch from the exact typed
module, retained non-disposable logic, an authentic assigned-curator ground
placement, placing-curator-only result delivery, replay/forgery rejection,
own-logic cleanup, replication and complete run cleanup. The entry was tied to
a narrow physical A/B: the enabled Eden phase tracked a real native artillery
shell and authored its CBR marker pair; the Zeus-disabled phase fired the same
fixture and independently observed its full flight/termination with no CBR
cluster or marker.

## Candidate stable contract

A real placed Eden CBR module enables the global CBR lifecycle once at mission
start. An authorized curator can place the public Zeus module to toggle that
same lifecycle. Each exact module invocation is accepted once on the server,
changes the already accepted CBR state, consumes only its own transient logic,
and produces truthful requester-scoped feedback. Invalid class, unauthorized,
replayed or unrelated-logic requests leave CBR and the supplied object intact.

## Canonical review

### 1. User or integrator observation

The Eden module says placing it triggers CBR. The Zeus module says it toggles
CBR during the mission. Both are public, registered config classes with real
configured functions. The intended observation is therefore enable-at-start and
curator-controlled global on/off, not a second implementation of radar behavior.

### 2. Current behavior and negative paths

The Eden handler forwards itself to owner 2 when non-server, calls
`YOSHI_fnc_cbrSetEnabled` with true, then deletes its logic. The Zeus handler
uses the same forwarding pattern, toggles the global lifecycle, emits a curator
notification, and deletes its logic. Only null logic is rejected. The accepted
lifecycle is idempotent on start and bounded on stop, but entry requests have no
identity, replay result or rejection record.

### 3. Authority, locality and lifecycle

Server ownership of the lifecycle is correct. Module-request authority is
undefined. Neither handler checks exact module class, logic locality,
`remoteExecutedOwner`, assigned curator identity or a private capability. A
client can invoke the global name with unrelated logic; the server can change
global CBR state and delete that object. `isGlobal=0` may mean native framework
dispatch already occurs on the correct machine, which would make forwarding
unnecessary, but this needs engine evidence.

Eden declares `isDisposable=0` while its handler deletes the logic. Zeus declares
`isDisposable=1`. Whether Eden persistence or deletion is intended is a product
lifecycle decision, not an assertion to infer from the current contradiction.

### 4. Generic mechanics

Generating a typed module entity in mission SQM, recording configured-function
dispatch, engine ownership, curator placement and exact logic cleanup are generic
Tribunal mechanics. CBR owns enable/toggle meaning. Existing artillery, marker
and radio observers already provide the independent downstream oracle.

### 5. Product-owned behavior

Advanced Systems owns global enable/toggle policy, valid module classes,
authorized curator policy, duplicate handling, feedback audience and whether
the Eden logic persists. Tribunal must not decide those semantics.

### 6. Claimed engine requirements

No retained run proves where Arma executes an `isGlobal=0` module function, how
a curator-created logic identifies its placer, or whether programmatic curator
placement is equivalent to UI placement. No forwarding, deletion or UI
mechanism is characterized.

### 7. Fragile or incomplete details

Null-only validation, unrestricted forwarding, no operation ID, caller-supplied
object deletion, global toggle races, uncertain Eden disposal and broad curator
notification are refinement blockers. A stale enabled flag or a direct setter
call could falsely make either module look successful.

### 8. Better native or existing mechanisms

The actual Arma module framework is the supported entry and must be measured
before replacing or retaining forwarding. The accepted `YOSHI_fnc_cbrSetEnabled`
lifecycle remains the correct tail. A narrow validated server request may be
needed only if native curator dispatch genuinely originates elsewhere.

### 9. Stable contract and causal proof

Eden proof requires a real typed module in generated mission SQM, exact handler
receipt and one fresh native artillery shell whose accepted CBR markers/warning
appear. A no-module mission must fire and impact the same shell without CBR
evidence. Zeus proof requires actual curator placement, exact logic/requester
identity, on/off transitions and the same physical shell A/B. A forged client
call with unrelated logic must reach the boundary, be rejected, preserve the
object and leave state unchanged.

### 10. Replaceable implementation details

Handler names, module priority, receipt schema, notification wording, private
thread variables, fixture coordinates and exact placement input are replaceable.
The stable promise is authentic module activation, authorized global transition,
truthful result and scoped cleanup.

### 11. Characterization

Nothing is characterized. Real module dispatch/locality and curator placement
equivalence require the controlled experiment below.

### 12. Tribunal promotion

Add a typed mission-module fixture only when implementing the first Eden proof:
validated addon, class, name and position producing a real `dataType="Logic"`
entity and required-addon metadata. Do not expose arbitrary SQM. Curator
placement should remain scenario-local until equivalence is proven and a second
consumer justifies promotion.

## Established product decisions

1. Every assigned curator may toggle the intentionally mission-global CBR state.
2. Feedback goes only to the placing curator.
3. Operation IDs are idempotent and bounded; replay cannot toggle again.
4. Eden enable is idempotent and its non-disposable logic remains available.

## Implementation and evidence

The Eden handler now accepts only the exact server-local typed class from native
dispatch and retains it. The Zeus path observes `CuratorObjectPlaced` on the
placing client, binds a fresh operation to the client-owned exact module and its
assigned curator, revalidates on the server, consumes the claim once, toggles
the accepted lifecycle, and returns the result only to that owner. Missing
claims do not authorize deletion; accepted transient logic is deleted after its
result. The operation cache has a 300-second TTL and deterministic size bound.

Two engine facts were characterized without becoming specification: an
unsynchronized Eden logic can have an empty `vehicleVarName` despite an SQM
name, so evidence uses its exact netId; and a freshly placed ground module can
be local while briefly reporting owner 0 on the placing client. The authority
oracle therefore uses the server's later `owner(logic) == remoteExecutedOwner`
predicate. `curatorMouseOver` is empty for ground placement, so the external
adapter drives a scenario-declared screen point and success comes only from the
exact native placement/claim/result chain.

## False-PASS audit

Calling the handler or lifecycle API directly proves only the tail. Enabled
state, thread existence, a notification or deleted logic can all be stale or
self-authored. Every positive needs fresh module identity plus physical CBR
output; every disabled phase needs a real shell launch/flight/impact; every
authority control needs a recorded request and unchanged independent state.

## Remaining bounds

One authentic ON-to-OFF Zeus placement is covered. Reverse-direction placement,
multiple Eden modules in one mission, repeated placement in one retained Zeus
display, client-B/JIP isolation and ownership migration remain explicit
follow-ups. They do not weaken the accepted single-operation authority and
causal activation contract. The accepted downstream CBR gameplay baseline is
unchanged.
