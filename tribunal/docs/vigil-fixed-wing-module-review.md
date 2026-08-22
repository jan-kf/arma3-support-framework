# Vigil fixed-wing Eden and Zeus activation — canonical feature review

## Scope and result

This review covers the three public Eden modules (asset, ingress, and egress)
and the curator-visible Add Fixed Wing Asset module. It does not reopen the
accepted registry API, snapshot/reconstruction, deployment, strike, logistics,
or RTB physical behavior.

**Classification: `KEEP AS-IS AND SPEC-TEST`; REFINED, ACCEPTED / COVERED.**

The refined handlers preserve the accepted fixed-wing registry/lifecycle while
adding exact typed server authority, aggregated mission points, authenticated
curator claims, replay protection, placer-only results, and bounded audit state.
Fresh autonomous proof covers those boundaries without reopening strike or
logistics combat behavior.

## Candidate stable contract

Real typed Eden modules register exact synchronized valid planes and establish
one authoritative ingress/egress policy from their actual mission positions.
A genuine authorized curator module adds exactly one selected plane. Every
invocation is authenticated, replay-safe, result-correlated, and changes only
its exact intended registry/default state. Invalid, ambiguous, unauthorized, or
competing modules do not delete unrelated objects or partially rewrite policy.

## Canonical twelve-question review

1. **What should the user observe?** Synced Eden planes become stowed Vigil
   assets; ingress and egress modules define deployment/RTB points; an authorized
   curator can add a plane during play. These entries should feed the accepted
   fixed-wing lifecycle, not create alternate registry semantics.
2. **What does it do now?** Exact typed asset modules register valid synchronized
   planes and remain in the mission. Infil/exfil modules retain all positions;
   deployment chooses the closest ingress to the requester and RTB chooses the
   closest egress to the aircraft. Zeus accepts exactly one attached/synchronized
   plane, registers it once, replies only to its placer, then deletes its own
   disposable logic.
3. **Which machines own it?** Native `isGlobal=0` Eden dispatch was observed once
   per module on the server (`local=true`, owner 2, `remoteExecutedOwner=0`). A
   curator-created logic is client-owned; server mutation requires a correlated
   `CuratorObjectPlaced` claim whose remote owner owns the current player and
   whose curator equals `getAssignedCuratorLogic` for that player.
4. **Which mechanics are generic?** Typed mission Logic entities, native Sync
   links, configured-function receipts, module position/attributes, real curator
   placement, execution locality, and own-logic cleanup can be Tribunal
   mechanics. Fixed-wing registration/default meaning remains Vigil.
5. **Which behavior is product-owned?** Valid plane/mixed-sync policy, one versus
   multiple asset/default modules, ingress/egress altitude semantics, default
   precedence/reconfiguration, authorized curator population, feedback audience,
   and disposable lifecycle are Vigil policy.
6. **Are unusual engine requirements proven?** Yes for the accepted slice:
   typed Sync is visible on the server, client-owned curator logic attaches to
   the exact plane, and a real display-312 selection plus authenticated RFB click
   reaches the configured handler. A large A-10's curator glyph was not located
   reliably from model origin/physical geometry; a smaller valid civil plane
   resolved through `curatorMouseOver`. That is fixture knowledge, not a product
   restriction. The inherited below-200 m to 1200 m altitude floor is not a
   separately accepted product promise.
7. **What is fragile or incomplete?** Mixed valid/invalid Sync policy is not
   specified beyond filtering valid planes. Multi-client audience isolation is
   structurally owner-targeted but awaits client-N infrastructure. The 1200 m
   floor and runtime reconfiguration/removal of retained point modules remain
   uncharacterized.
8. **Is a better mechanism available?** Keep the native module framework and
   accepted server registry/default APIs. Measure genuine dispatch before adding
   any transport. If curator placement originates client-side, use an
   authenticated exact operation rather than a generic public handler.
9. **What is the stable contract and causal proof?** `vigil-fixed-wing-modules`
   records exact configured dispatch/locality, derives registry IDs from
   pre-deletion Sync identities, preserves an unsynchronized control, observes
   nearest ingress/egress at consequential lifecycle boundaries, performs one
   real curator placement, and delivers replay/wrong-class controls. Exact
   registry, logic, target, operation, requester, result, replication, and
   cleanup identities must all agree.
10. **Which details remain free?** Function names, priority, registry schema,
    snapshot internals, notification prose, telemetry schema, altitude
    implementation, fixture coordinates, and exact transport mechanism.
11. **Which mechanisms deserve characterization?** The accepted scenario covers
    typed Eden dispatch/Sync, multiple nearest points, and one genuine curator
    placement. Mixed Sync, point removal/reconfiguration, alternate large-plane
    curator acquisition, and client-N isolation remain bounded follow-ups.
12. **What belongs in Tribunal?** Reuse the same narrow typed-Logic/SQM-Sync and
    dispatch observer required by APS/CBR/Field Utilities modules. Keep module
    class, plane eligibility, default points, and registry outcomes in Vigil.

## False-PASS boundary

Calling `YSF_fwRegisterAsset`, default setters, or module handlers directly is a
pipeline bypass. A registry row, debug count, notification, deleted original
plane, or deleted logic can be stale/self-authored. Positive proof needs a fresh
exact typed module receipt plus independent registry/world identity. A no-module
control needs the same valid plane stimulus. A forged control is meaningful only
with a receipt showing it reached rejection and a mission-wide census proving no
plane/crew/registry/default mutation.

The accepted fixed-wing scenarios prove downstream API and physical behavior,
not module activation. Their evidence remains valid and can be reused as a
bounded downstream oracle rather than rerunning the entire strike contract for
every module case.

## Acceptance evidence and continuation

Fresh autonomous run `20260822T201311Z-cb69f3fa` proved all 14 product
assertions (server 9, client 5; plus four smoke assertions per origin), emitted
a valid Evidence Contract v1 package, and completed all container/network/state
cleanup. Two asset, two ingress, and two egress modules
dispatched natively. Registry identities `FW_2:17`/`FW_2:18` matched independent
Sync identities, nearest points were `[4650,2800,1200]` and
`[4750,3000,1200]`, and authentic curator operation
`fixed-wing-4-26396-694314` attached logic `4:9` to plane `2:19`, producing
`FW_2:19`. Delivered replay and wrong-class requests returned `duplicate` and
`predicate_logic_class`; no fourth registry row appeared. Client-a resolved the
same three authoritative rows and cleanup empties both private and public state.

Keep mixed-Sync policy, point removal/reconfiguration, inherited altitude-floor
semantics, alternate large-plane curator acquisition, and client-B/JIP as
explicit follow-ups. They do not weaken the accepted exact-valid, one-client
contract above.
