# Advanced Systems APS anti-drone review

## Scope and result

This review applies the canonical feature-review program to the experimental
anti-drone subsystem in `functions/aps/fn_aps.sqf`. It covers APS activation,
UAV discovery, eligibility, resource consumption, destruction, delayed cleanup,
ACE control statements, locality, authority and the boundary with the accepted
projectile APS contract.

**Classification: `DEFER` (product decisions and refinement required; reviewed,
not covered).**

The repository establishes a broad intent—an APS-equipped vehicle can expose an
experimental anti-drone control and spend soft-kill power against small, fast
airborne UAVs—but it does not establish the threat, side, operator, range or
collateral-event policy needed for a stable specification. The current path is
also unsafe to freeze as behavior: it accepts every qualifying nearby UAV
regardless of allegiance or direction, strips unrelated event handlers, and can
destroy a UAV before asynchronous owner-local resource consumption is known to
have succeeded. No product or Tribunal code is changed by this review.

## Candidate product outcome supported by current evidence

An APS-equipped vehicle may provide an operator-controlled experimental
anti-drone defense which detects eligible airborne UAV threats, consumes one
soft-kill resource only when the authoritative engagement is accepted,
neutralizes the exact threat, publishes an exact terminal result, and cleans up
only state owned by this feature. The repository does not yet decide which UAVs
are threats or which operators are authorized, so this is a boundary for future
decisions rather than an accepted contract.

## Canonical review

### 1. User or integrator observation

The public APS Eden module and Zeus toggle enable APS on a vehicle. APS then
registers an ACE **Anti-Drone** submenu containing on, off and status actions.
The upstream README calls the behavior an “Experimental anti-drone protection”
and warns that defensive behavior and balance may change. That establishes a
reachable experimental capability, but not a complete targeting policy.

### 2. Current behavior and negative paths

APS enable sets anti-drone on by default and starts one server-side scheduled
loop. Unless a caller supplies a range, the loop uses twice the vehicle's real
bounding-box diagonal. Every 0.5 seconds it selects `allUnitsUAV` entries that
are `Air`, weigh less than 1000 kg and are within that range. Any selected UAV
whose absolute speed exceeds 40 km/h and lacks the product hit flag is acted on.

The loop attempts to consume 2 percent vehicle fuel, plays product effects,
removes thirteen classes of object event handlers, applies lethal damage,
marks the UAV hit and schedules deletion after 30 seconds. Low fuel disables
anti-drone. The ACE statements can enable, disable or report status. Disabling
APS terminates the detector thread and unregisters actions.

There is no side, hostility, closing-direction, predicted-impact or line-of-
sight test. A friendly UAV, a departing UAV and a UAV merely transiting the
radius are therefore indistinguishable from a threat. The narrow default range
combined with a 0.5 second poll also leaves detection timing dependent on
vehicle dimensions and crossing speed. These facts describe current code; they
are not accepted product promises.

### 3. Authority, locality and lifecycle

The detector is spawned by the server, but neither the protected vehicle nor a
candidate UAV is required to be server-local. Soft-kill consumption routes to
the vehicle owner through CORDIS when the vehicle is nonlocal, then immediately
returns `true` to the server. The server can consequently continue with lethal
UAV mutation without an owner acknowledgment proving that resource consumption
succeeded. This is a transaction split, not authoritative all-or-nothing
engagement.

The UAV's owner is not used for damage, handler removal or cleanup. Event
handlers are local to the machine on which they were installed, so removing
them on the detector machine neither proves owner cleanup nor prevents removal
of unrelated server-side handlers. There is no exact engagement ledger or
owner-local terminal acknowledgment.

The ACE statements remote-execute globally named handlers on the server. Those
handlers check only `isServer`, a non-null vehicle and, for enable, fuel. They do
not validate `remoteExecutedOwner`, the claimed player, distance, crew/control
relationship or a private server capability. ACE visibility conditions are a
presentation gate, not an authority boundary. A future contract must decide
who is allowed to operate this system before the endpoint can be secured.

### 4. Generic mechanics

Exact object identity, owner/locality receipts, trajectory sampling, damage and
terminal observation, ACE registered-action discovery, replication and cleanup
are generic Tribunal concerns. Threat eligibility, power consumption,
neutralization policy, operator authorization and product effects remain
Advanced Systems semantics. Existing combat/locality/ACE adapters should be
reused before inventing an anti-drone-specific Tribunal primitive.

### 5. Product-owned behavior

Advanced Systems must decide UAV eligibility, friendly/hostile policy, whether
proximity or an inbound/closing threat is required, engagement range, default
activation, authorized operators, resource semantics, neutralization outcome
and cleanup. The current mass, speed, distance, poll and damage details are
implementation evidence, not automatically the specification.

### 6. Claimed engine requirements

No controlled evidence establishes that `allUnitsUAV`, polling, lethal
`setDamage`, broad handler removal or delayed deletion is required by Arma,
ACE or CBA. In particular, there is no retained A/B showing that stripping
handlers is necessary to neutralize a UAV safely. None of these mechanisms is
characterized.

### 7. Fragile or incomplete details

The default range derives from the protected vehicle model, the detector sleeps
inside its per-UAV loop, the hit flag is written only after damage, asynchronous
resource routing is treated as success, and cleanup is a detached untracked
script. Broad `removeAllEventHandlers` can erase behaviors owned by missions,
other mods and evidence observers. A hit flag or UAV disappearance could be
self-confirming, while a stale delayed-delete script can outlive scenario
cleanup. The on/off/status handlers trust caller-supplied objects and player
identity.

### 8. Better native or existing mechanisms

No replacement should be chosen before the threat contract and locality A/B are
known. The accepted projectile APS already demonstrates an exact identity
ledger and authoritative resource/result correlation, but anti-drone need not
share its threat geometry or interception implementation. Tribunal already has
the observation mechanics needed to compare owner-local and non-owner mutation.

### 9. Stable contract and causal proof

There is not yet enough product intent for permanent coverage. Eventual proof
must begin with the real supported activation and exact registered ACE control
statement, then correlate exact protected-vehicle and UAV identities across:

* an independently sampled eligible threat that actually crosses the chosen
  threat boundary;
* authoritative acceptance and exactly one acknowledged resource decrement;
* exact UAV neutralization and a physical protected outcome;
* friendly/non-threat, departing, disabled and insufficient-power controls
  whose UAV stimulus and motion are independently proven;
* owner-local and non-owner-local UAV/vehicle cases;
* rejected unauthorized control requests;
* client replication and bounded cleanup.

No internal flag, fuel change, damage value or disappearance is sufficient on
its own. A negative control must prove that a real eligible UAV traversed the
relevant geometry and remained physically valid.

### 10. Replaceable implementation details

Function and variable names, the polling mechanism and cadence, exact model
classes, mass/speed/range values, damage mechanism, cleanup delay, sound and
beam choices, ACE action IDs and any eventual ledger schema must remain free to
change unless a later controlled comparison proves one necessary.

### 11. Characterization

Nothing deserves characterization. Every unusual mechanism currently has only
source-code existence, not a controlled alternative and retained outcome.

### 12. Tribunal promotion

No new Tribunal primitive is justified at this stage. Reuse generic ACE action,
combat, locality and trajectory evidence in the first discriminating Live
experiment. Promote a new mechanic only if that experiment exposes a reusable,
product-neutral gap with another plausible consumer.

## Required product decisions

1. Does anti-drone engage only hostile UAVs, or intentionally every qualifying
   UAV including friendly assets?
2. Is a threat defined by proximity alone, or must it be closing on / predicted
   to endanger the protected vehicle?
3. Which UAV families, mass and speed states are eligible, and is the range a
   fixed setting, vehicle-relative value or another policy?
4. Is anti-drone intentionally enabled automatically with APS, or explicitly
   opt-in through mission configuration or an operator?
5. Who may operate on/off/status: crew, UAV/vehicle controller, nearby players,
   a role-qualified player, Zeus, or another authority?
6. Is one 2-percent fuel decrement the intended per-engagement resource, and
   must it commit atomically before neutralization?
7. What user-visible neutralization is intended, and may the feature ever
   remove event handlers it did not install?

## First discriminating experiment after decisions

Use one retained Live session and exact identities. Place a server-local APS
vehicle and a controlled UAV comfortably inside the selected geometry. First
run the disabled case and independently sample the UAV's stable flight through
the region. Then enable anti-drone with identical geometry and record protected
vehicle/UAV owner and locality, action request origin, resource acknowledgment,
UAV trajectory/damage/terminal state, event-handler sentinel survival and
cleanup. Repeat with the UAV and protected vehicle owner-local to the client.
Follow with hostile/friendly, inbound/departing, insufficient-power and
unauthorized-action controls, each proving its stimulus reached the decision
boundary.

The first stopping boundary is the split transaction: determine whether the
current nonlocal vehicle case can kill a UAV before failed or delayed owner-side
fuel consumption completes. Do not proceed to a permanent scenario until
resource acceptance and neutralization have one authoritative terminal result.

## False-PASS audit

The current hit flag, `setDamage`, deletion timer, fuel value and action-visible
state are all product-authored and can agree while the wrong UAV was selected,
the resource operation failed, the UAV was already doomed, unrelated handlers
were removed or stale state survived. Future coverage must require exact netIds
(or a stable same-frame identity when netId is unavailable), independently
sampled motion and locality, a decision receipt, an owner acknowledgment,
physical terminal evidence, sentinel handler survival, replication and cleanup.
Controls must use fresh identities and fresh resource state so a prior hit or
delayed deletion cannot satisfy them.

## Terminal disposition

This review completes reconnaissance and removes APS anti-drone from the
unreviewed queue, but it deliberately adds no permanent scenario and makes no
product change. The next step requires the seven product decisions above,
followed by the bounded locality/transaction experiment. Until then the feature
remains experimental, destructive and **not accepted coverage**.
