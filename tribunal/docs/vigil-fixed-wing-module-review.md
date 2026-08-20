# Vigil fixed-wing Eden and Zeus activation — canonical feature review

## Scope and result

This review covers the three public Eden modules (asset, ingress, and egress)
and the curator-visible Add Fixed Wing Asset module. It does not reopen the
accepted registry API, snapshot/reconstruction, deployment, strike, logistics,
or RTB physical behavior.

**Classification: `REFINE BEFORE PERMANENT COVERAGE` (reviewed; not covered).**

The configured module handlers are reachable but authentic engine dispatch is
unmeasured. They rely on `isGlobal=0` plus a server-only early exit, validate no
exact module class/locality/requester, and return no correlated result. The
curator handler can register/despawn a caller-selected plane and delete the
caller-supplied logic without curator authorization.

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
2. **What does it do now?** The asset handler ignores non-planes, registers each
   valid synchronized plane through `YSF_fwRegisterAsset`, and leaves its logic.
   Infil/exfil handlers publish module ASL positions, forcing altitude to 1200 m
   below 200 m, and apply them to existing registry rows. Zeus chooses first
   synchronized or attached target, registers it, notifies broadly, and deletes
   its logic.
3. **Which machines own it?** All handlers simply exit off-server. Whether
   native `isGlobal=0` dispatch executes them on server is unmeasured. No exact
   class, logic locality/owner, `remoteExecutedOwner`, assigned-curator,
   operation, or replay validation exists. Registry mutation itself is correctly
   server-owned once the tail API is reached.
4. **Which mechanics are generic?** Typed mission Logic entities, native Sync
   links, configured-function receipts, module position/attributes, real curator
   placement, execution locality, and own-logic cleanup can be Tribunal
   mechanics. Fixed-wing registration/default meaning remains Vigil.
5. **Which behavior is product-owned?** Valid plane/mixed-sync policy, one versus
   multiple asset/default modules, ingress/egress altitude semantics, default
   precedence/reconfiguration, authorized curator population, feedback audience,
   and disposable lifecycle are Vigil policy.
6. **Are unusual engine requirements proven?** No run establishes native module
   execution machine/count, synchronization visibility, curator attachment
   identity, or equivalence of programmatic and UI curator placement. The 1200 m
   floor/default and equal module priorities are not characterized requirements.
7. **What is fragile or incomplete?** Multiple ingress/exfil modules are
   last-writer/order dependent. Mixed valid/invalid asset sync partially
   succeeds silently. Zeus first-target selection is ambiguous and unguarded;
   feedback defaults broadly; its class does not state a disposal policy while
   the handler deletes the logic. Direct remote invocation can reach server
   handlers with arbitrary network-visible logic.
8. **Is a better mechanism available?** Keep the native module framework and
   accepted server registry/default APIs. Measure genuine dispatch before adding
   any transport. If curator placement originates client-side, use an
   authenticated exact operation rather than a generic public handler.
9. **What is the stable contract and causal proof?** A fresh mission with real
   typed modules must record exact handler identity/locality and independently
   prove the exact synced plane became the accepted registry row while an
   unsynced equal control did not. Exact module positions must produce the
   independently observed deployment/egress defaults. A real curator placement
   adds one exact plane; forged/invalid/replay controls reach rejection and
   preserve unrelated objects/registry.
10. **Which details remain free?** Function names, priority, registry schema,
    snapshot internals, notification prose, telemetry schema, altitude
    implementation, fixture coordinates, and exact transport mechanism.
11. **Which mechanisms deserve characterization?** Typed Eden dispatch and Sync
    first; then one real curator placement/attachment. Test multiple/default
    modules only after precedence policy. One bounded VNC characterization is
    justified only if native curator equivalence cannot be established by data.
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

## Decisions and continuation

Decide: one/multiple asset modules; atomic versus partial mixed-sync registration;
one ingress/exfil module and duplicate precedence; supported altitude semantics;
authorized curator scope; exactly-one Zeus selection; feedback audience; and
Zeus logic disposal/replay policy.

Then implement/reuse the typed module fixture, run typed module/no-module A/B,
record actual execution/locality/Sync/position values, and refine only from that
evidence. Characterize one real curator placement and prove authorized add plus
invalid, unauthorized, unrelated-logic, and replay rejection. Preserve the
accepted fixed-wing registry and physical lifecycle unchanged.
