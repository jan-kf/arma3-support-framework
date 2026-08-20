# APS and Field Utilities ACE action composition — canonical feature review

## Scope and result

This review covers the cold-client coexistence of APS per-object ACE actions
with Field Utilities class-inherited actions on the same vehicle, including APS
disable/re-enable isolation. It does not re-review individual action effects,
APS operator authority, anti-drone, or the accepted Field Utilities composition.

**Classification: `REVIEWED / DEFERRED UNTIL APS CONTROL POLICY AND AUTHORITY
REFINEMENT` (not covered).**

The accepted `fieldutils-ace-composition` scenario proves Field Utilities class
actions coexist and resolve through ACE 3.21's concrete-class active tree. APS
uses a separate persistent per-object registration path. Its exact combined
tree, unregister isolation, and re-enable uniqueness are unproven, but freezing
an expected tree now would also bless unauthenticated APS statements and the
separately deferred anti-drone submenu.

## Candidate stable contract

On an exact APS-enabled `LandVehicle`, the selected supported APS roots and the
independently registered Field Utilities class roots coexist exactly once in the
real current-client active tree. Disabling APS removes only APS-owned nodes and
preserves the Field census; re-enabling restores one copy. Discovery does not
execute statements or mutate gameplay. Deferred anti-drone nodes, labels/icons,
order, authority/effects, and JIP are not implicit promises.

## Canonical twelve-question review

1. **What should the user observe?** A vehicle that supports multiple addons
   exposes each relevant supported interaction without duplicates or one addon
   suppressing another. APS disable/re-enable should remove/restore only its own
   controls.
2. **What does it do now?** Field Utilities registers Bridge, Logistics, Virtual
   Inventory, Towing/Stow, and FPV class actions during client post-init. APS
   enable persistently remote-registers per-object hard/soft/status, voice, and
   anti-drone nodes; disable reuses the object JIP key to unregister exact IDs;
   a local flag guards duplicate adds.
3. **Which machines own it?** All ACE tree state is client-local. APS lifecycle
   requests registration from server; Field actions arise during each client's
   cold init. Consequential statements still cross their product-specific
   owner/server boundaries. Composition itself grants no authority.
4. **Which mechanics are generic?** Installed-version ACE compilation, active
   tree collection, exact node census, persistent registration receipts,
   coexistence/removal diffs, and no-mutation census are Tribunal mechanics.
5. **Which behavior is product-owned?** Each addon owns supported roots,
   relevance, action authority/effect, lifecycle, and whether a submenu ships.
   The suite owns only noncollision and isolation on shared targets.
6. **Are unusual engine requirements proven?** Field class inheritance requires
   exact-target `compileMenu` under ACE 3.21 and is characterized. APS per-object
   storage/active-tree discovery, persistent JIP-key replacement, unregister,
   and re-enable have not been measured. Client-B/JIP is environment-deferred.
7. **What is fragile or incomplete?** APS local bookkeeping can drift from the
   actual tree. Direct add/remove calls bypass global delivery. The current tree
   includes a deferred anti-drone root and top-level voice nodes whose intended
   ownership/layout is undecided. Stored statements reach an unrefined authority
   boundary. Repeated compilation can hide or manufacture duplicates if the
   adapter mutates ACE scratch state.
8. **Is a better mechanism available?** Preserve ACE's class and object action
   mechanisms. First choose supported APS nodes and refine statement authority;
   then extend the installed-version observer only as needed for per-object
   active nodes. No UI/VNC automation is necessary for data identity.
9. **What is the stable contract and causal proof?** Fresh target pre-enable:
   exact relevant Field roots, no APS roots. Real server enable: exact local
   receipt and chosen APS nodes once, unchanged Field census. Real disable:
   exact APS absence and identical Field census. Re-enable: exact APS nodes once,
   no duplicates. Repeated collection leaves gameplay/resources/world unchanged.
10. **Which details remain free?** Labels, icons, ordering, nesting, private ACE
    namespaces, local flags, remote-exec key, registration helper, and adapter
    internals remain replaceable. Exact product-owned node identity can change
    only with its feature contract.
11. **Which mechanisms deserve characterization?** APS object-action storage and
    active-tree materialization under installed ACE; current-client persistent
    unregister/re-register ordering. JIP/repeated-init/ownership migration wait
    for the existing second-identity boundary.
12. **What belongs in Tribunal?** Extend the existing product-neutral ACE active-
    tree adapter only after real per-object evidence. Keep APS/Field node names,
    relevance, and lifecycle expectations in their product scenario.

## False-PASS boundary

`YOSHI_APS_ActionsAdded_Local`, enabled state, a successful
`addActionToObject`, persistent remoteExec entry, or Field roots do not prove APS
nodes exist. Directly calling local registration bypasses lifecycle delivery.
Invoking stored statements bypasses active relevance and the unresolved
operator boundary; composition proof must not execute them. VNC showing one
root cannot prove exact identities/counts, removal isolation, or duplicates.

Disable needs an exact tree diff while Field roots remain unchanged; APS state
false or local flag false is insufficient. Re-enable requires a fresh ordered
receipt and exact singleton census, not stale registration. The observer must
preserve ACE scratch state and prove no cargo, rope, APS resource, or world
mutation.

## Decisions and continuation

First decide/refine the supported APS operator policy and request boundary,
whether the anti-drone submenu ships before that feature is accepted, intended
voice root ownership, and current-client disable/re-enable semantics. Then reuse
one exact APS-capable LandVehicle and the Field composition fixture for
pre-enable/enable/disable/re-enable census. Do not invoke action statements.
Defer client-B/JIP and repeated init explicitly.
