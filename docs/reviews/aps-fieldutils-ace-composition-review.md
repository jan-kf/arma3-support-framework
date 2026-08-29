# APS and Field Utilities ACE action composition — canonical feature review

## Scope and result

This review covers the cold-client coexistence of APS per-object ACE actions
with Field Utilities class-inherited actions on the same vehicle, including APS
suspension/resume isolation. It does not re-review individual action effects,
APS operator authority, anti-drone, or the accepted Field Utilities composition.

**Classification: `KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED` for the current authenticated client.**

The accepted Field Utilities scenario established the concrete-class ACE adapter. After the APS request boundary was authenticated, the permanent `aps-intercept` scenario reused that adapter on the same exact tank and proved the Field class census remains identical while APS is active, suspended, and resumed. An otherwise identical uninstalled tank had the same Field census and no APS registration. This accepts composition only; it does not claim anti-drone interception behavior.

## Stable contract

On an exact APS-installed `LandVehicle`, the supported active APS controls and independently registered Field Utilities class roots coexist exactly once in the current-client ACE tree. Suspending APS preserves the Field census and leaves exactly the APS Resume control relevant; resuming restores exactly the controls relevant to the preserved APS modes and preferences. Discovery does not
execute statements or mutate gameplay. Anti-drone gameplay, labels/icons,
order, authority/effects, and JIP are not implicit promises.

## Canonical twelve-question review

1. **What should the user observe?** A vehicle that supports multiple addons
   exposes each relevant supported interaction without duplicates or one addon
   suppressing another. APS suspension/resume must change only APS relevance while preserving every Field root.
2. **What does it do now?** Field Utilities registers Bridge, Logistics, Virtual
   Inventory, Towing/Stow, and FPV class actions during client post-init. APS
   first installation persistently remote-registers its per-object controls once. Suspension retains those registrations but makes only Resume relevant; resume restores relevance from preserved state. Explicit uninstall/object cleanup remains outside this contract.
3. **Which machines own it?** All ACE tree state is client-local. APS lifecycle
   requests registration from server; Field actions arise during each client's
   cold init. Consequential statements still cross their product-specific
   owner/server boundaries. Composition itself grants no authority.
4. **Which mechanics are generic?** Installed-version ACE compilation, active
   tree collection, exact node census, persistent registration receipts,
   coexistence/relevance diffs, and no-mutation census are Tribunal mechanics.
5. **Which behavior is product-owned?** Each addon owns supported roots,
   relevance, action authority/effect, lifecycle, and whether a submenu ships.
   The suite owns only noncollision and isolation on shared targets.
6. **Are unusual engine requirements proven?** Field class inheritance requires
   exact-target `compileMenu` under ACE 3.21 and is characterized. APS per-object action data is evaluated through ACE's real active-tree collector; active/suspended/resumed relevance and singleton identity are measured on client-a. Persistent client-B/JIP delivery and explicit unregistration remain deferred.
7. **What is fragile or incomplete?** APS local bookkeeping alone can drift from the actual tree, so the scenario feeds exact action data through ACE's collector and correlates lifecycle changes with authenticated results. Anti-drone gameplay, labels, nesting, and top-level voice layout remain outside this composition specification. Repeated compilation can hide or manufacture duplicates if the
   adapter mutates ACE scratch state.
8. **Is a better mechanism available?** Preserve ACE's class and object action
   mechanisms. The authenticated APS endpoint and installed-version ACE observer now provide the required existing mechanisms; no additional UI automation or composition framework is needed. No UI/VNC automation is necessary for data identity.
9. **What is the stable contract and causal proof?** An identical uninstalled control has the three applicable singleton Field roots and no APS registration. The installed target has the same singleton Field roots; only Towing is relevant under the measured fixture state. The retired `UAV_field_task` root is absent because Payload Manager now registers its object action only on eligible UAVs. Across authenticated suspension and resume, the entire Field snapshot remains byte-for-byte equal, APS leaves become exactly Resume, then return to the exact preserved-mode set. Field rope and UAV payload state remain unchanged.
10. **Which details remain free?** Labels, icons, ordering, nesting, private ACE
    namespaces, local flags, remote-exec key, registration helper, and adapter
    internals remain replaceable. Exact product-owned node identity can change
    only with its feature contract.
11. **Which mechanisms deserve characterization?** Explicit uninstall, repeated client initialization, object deletion, client-B/JIP, and ownership migration remain deferred. They are not inferred from current-client suspension/resume.
12. **What belongs in Tribunal?** The existing product-neutral ACE active-tree adapter is sufficient. APS/Field identities and lifecycle expectations remain scenario-owned product data.

## False-PASS boundary

`YOSHI_APS_ActionsAdded_Local`, enabled state, a successful
`addActionToObject`, persistent remoteExec entry, or Field roots do not prove APS
nodes exist. Directly calling local registration bypasses lifecycle delivery.
The scenario executes only already-accepted exact APS statements to create the lifecycle phases; it never executes a Field statement. The composition oracle is the independent class/object census and no-mutation snapshot, not the APS result itself. VNC showing one
root cannot prove exact identities/counts, removal isolation, or duplicates.

Suspension needs an exact relevance diff while Field roots remain unchanged; APS state false or a local flag is insufficient. Resume requires a fresh authenticated result and exact singleton/relevance census, not stale registration. The observer must
preserve ACE scratch state and prove no cargo, rope, APS resource, or world
mutation.

## Permanent evidence

The original autonomous run `20260820T223222Z-3046910b` passed 18 server and 11 client assertions with zero failures before Payload Manager replaced the legacy `UAV_field_task` root. The current `aps.controls.composition` contract requires the three still-applicable singleton Field roots on both installed and uninstalled same-class tanks, explicitly excludes that retired UAV root from tanks, requires only `TowActions` to be relevant in the controlled state, and retains zero rope/payload mutation, exact APS active leaf sets, exactly `YOSHI_APS_Resume` while suspended, and restoration of the preserved-mode leaf set after resume. The causal hard-off impact and reboot interception pair remain unchanged.

Client-B/JIP, explicit uninstall, repeated init, object deletion, and ownership migration remain deferred. Anti-drone gameplay remains governed by its separate review.
