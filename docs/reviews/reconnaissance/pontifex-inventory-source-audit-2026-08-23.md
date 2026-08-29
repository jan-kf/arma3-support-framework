# Pontifex feature inventory — source audit, 2026-08-23

> **NON-AUTHORITATIVE.** See [`README.md`](README.md). This audit *identifies*
> divergence between [`../pontifex-feature-inventory.md`](../pontifex-feature-inventory.md)
> and the tree at `fa040a2`. It does not correct the inventory, change any
> status, or assert that any divergence is a defect. Applying a correction is
> the inventory owner's decision.

## Method and its limits

* Enumerated every `.sqf`, `.hpp` and `config.cpp` under `mods/`, every
  `CfgFunctions` registration, every `CfgVehicles`/`CfgSounds`/`CfgRadio`/
  `CfgFactionClasses` class, every IDC constant, every `CBA_fnc_addSetting` key,
  and every `TRIBUNAL_SCENARIO` identifier.
* "No caller" means no textual reference to the global's name anywhere under
  `mods/`, `tribunal/{scenarios,runner,mission}`, or `tools/`, excluding its
  own definition line. **This is a textual heuristic.** A symbol reached only by
  a runtime-composed string, a `remoteExec` target named at runtime, or a
  mission-authored call from outside the repository would be misreported as
  having no caller. Every entry below should be re-confirmed before anyone acts
  on it, and none of it is grounds for deletion — the inventory's own rule that
  "unknown intent is not permission to delete" applies unchanged.
* No file outside this directory was modified.

---

## 1. Stale entries

### 1.1 The permanent-scenario table lists 12 of 21 scenarios

The inventory's "Permanent feature scenarios discovered by the runtime adapter"
table lists twelve identifiers. Discovery over the four registered roots yields
**twenty-one**. Nine are absent from the table:

| Identifier | Scenario file |
| --- | --- |
| `advsys-aps-eden-module` | `mods/advanced-systems/tests/tribunal/aps_eden_module.py` |
| `advsys-aps-zeus-module` | `mods/advanced-systems/tests/tribunal/aps_zeus_module.py` |
| `advsys-cbr-modules` | `mods/advanced-systems/tests/tribunal/counter_battery_radar_modules.py` |
| `advsys-iron-dome` | `mods/advanced-systems/tests/tribunal/iron_dome.py` |
| `fieldutils-ace-composition` | `mods/field-utilities/tests/tribunal/ace_composition.py` |
| `fieldutils-bridge-builder` | `mods/field-utilities/tests/tribunal/bridge_builder.py` |
| `fieldutils-eden-modules` | `mods/field-utilities/tests/tribunal/fabricator_eden_modules.py` |
| `fieldutils-towing` | `mods/field-utilities/tests/tribunal/towing.py` |
| `vigil-whitelist-modules` | `mods/visual-support-tablet/tests/tribunal/vigil_whitelist_modules.py` |

Each of these is described in the inventory's prose as accepted or covered, so
the divergence is in the summary table only. It matters because that table is
the fastest thing a cold reader consults to learn what permanent proof exists,
and it currently under-reports it by nine.

### 1.2 `CLAUDE.md` records a manifest inconsistency that no longer exists

`CLAUDE.md` states:

> "Note the known, recorded inconsistency: `tribunal.project.json` lists only the
> advanced-systems root for the generic CLI."

`tribunal.project.json` at `fa040a2` lists **all four** scenario roots, and
`tests/test_tribunal_architecture.py::test_project_manifest_discovers_the_runtime_feature_scenario_set`
asserts that manifest discovery equals `multiplayer.FEATURE_SCENARIOS`. The
alignment landed in commit `146cd38` ("Align Tribunal manifest scenario
discovery"). The inventory's own prose is already correct — "The project
manifest and Pontifex runtime now discover the same feature scenario set" — so
the stale text is in the entry document, not the inventory.

`CLAUDE.md` is the cold-read entry point and is guarded by
`tests/test_feature_review_workflow_docs.py`; this note is recorded rather than
edited because it is accepted project guidance.

### 1.3 Two accepted surfaces have no durable review document

The program states that "Completed reviews are durable evidence and live beside
the program: `docs/reviews/*-review.md`". Two scenarios carry complete
`ScenarioReview` metadata with outcome `KEEP AS-IS AND SPEC-TEST`, and are
recorded as **COVERED** in inventory §3.4 and §3.4/§3.1, but have no
corresponding review file:

| Surface | Scenario | Inventory status | Review document |
| --- | --- | --- | --- |
| Artillery request UI, native circle/line execution, VLS | `vigil-artillery` | COVERED | *(none)* — only [`../vigil-vls-handshake-characterization.md`](../vigil-vls-handshake-characterization.md), which covers the handshake alone |
| Artillery preview markers | `vigil-markers` | COVERED | *(none)* |

Every other COVERED Vigil surface links a `See […]` review. §3.4 is the only
section in the document with no such link. A future reader following the
CLAUDE.md instruction "Read the relevant one before touching a covered feature"
has nothing to read for artillery.

---

## 2. Source surfaces the inventory does not name

These exist in the tree and are not represented in any inventory entry. Several
are small; they are listed because the inventory's stated purpose is to "record
what exists so later reviews can choose stable behavioral contracts".

### 2.1 Vigil tablet — an entire unrealized navigation design

`mods/visual-support-tablet/addons/VIGIL/ui/idc.hpp` defines IDC constants for
a page family that has no page file and no reference anywhere in the tree:

* `IDC_PAGE_MAP` (88110) — a map page that does not exist. Its child constants
  `IDC_MAP_COORD_BTN`, `IDC_MAP_TAB_TXP`, `IDC_MAP_TAB_ARTY`, `IDC_MAP_TAB_CAS`,
  `IDC_MAP_TAB_RECON` are likewise unreferenced.
* `IDC_ASSETS_TAB_TXP`, `IDC_ASSETS_TAB_ARTY`, `IDC_ASSETS_TAB_CAS`,
  `IDC_ASSETS_TAB_RECON` — a per-task tab strip for the assets page,
  unreferenced (the shipped page uses `IDC_ASSETS_TAB_BOX` instead).
* `IDC_YSF_VP_GRP`, `IDC_YSF_VP_BG`, `IDC_YSF_VP_TITLE`, `IDC_YSF_VP_PIC`,
  `IDC_YSF_VP_TEXT` — a five-control group with no consumer.
* `IDC_TABLET_TITLE`, `IDC_TABLET_BTN_CLOSE` — defined, never used.

The inventory records the homepage deferral and the recon deferral but not this
third, larger fossil: a map-centric navigation shell with dedicated task tabs.
It is directly relevant to §3.1's "Tabbed navigation … PARTIALLY COVERED. Visible
artillery navigation is direct, not every page", because it shows that the pages
that are "not every page" were designed and then routed through the assets page.

### 2.2 `ui/pages/page_admin.hpp` is a distinct commented surface

The inventory's §3.1 deferral describes the homepage ("Its page and registration
are commented out"). There is a **second** such file: `ui/pages/page_admin.hpp`
is eight lines, all commented, defining an "Admin" page with Home and Assets
buttons; its registration is commented out at `functions/global/fn_init.sqf:6`.
It is not the homepage and is not covered by
[`../vigil-homepage-task-management-review.md`](../vigil-homepage-task-management-review.md),
whose scope is task management.

Unlike the homepage, `page_admin.hpp` contains **no live content whatsoever** —
there is nothing to review, only a naming intent.

### 2.3 A second, orphan whitelist toggle entry point

Inventory §3.2 records the Eden/Zeus whitelist path as **REFINED; ACCEPTED /
COVERED**, with server-private exact membership and replay/forgery rejection.

`mods/visual-support-tablet/addons/VIGIL/functions/global/fn_utils.sqf:33-37`
defines a second, globally named entry point:

```sqf
YSF_toggleWhitelistedObject = {
  params ["_obj"];
  if (!isServer || {remoteExecutedOwner > 2}) exitWith {false};
  [_obj] call YSF_fnc_whitelistToggleServer
};
```

It has no caller. Its guard *does* fail closed against clients (a client's
`remoteExecutedOwner` exceeds 2, and 0/2 are the not-remote and server cases),
so this is not a client-reachable authority hole. What it does bypass is the
entire accepted operation pipeline: no operation id, no curator binding, no
claim, no audit entry, no result routed to the placer, no logic retirement. Any
server-side mission script can mutate the accepted server-private whitelist
without leaving a trace the accepted contract knows about.

This deserves an inventory line next to an ACCEPTED surface, not because it is
currently exploited, but because the accepted contract's audit claim is stated
without reference to it.

### 2.4 Advanced Systems Counter Battery Radar — two dead tuning constants

`mods/advanced-systems/addons/AdvSys/functions/cbr/fn_cbr.sqf`:

* `:13` — `YOSHI_CB_MEMBER_TTL = 2.0;` defined, never read.
* `:18` / `:369` — `YOSHI_CB_nextUid` assigned to 0 twice, never read. Shell UIDs
  come from `YOSHI_CB_LOCAL_UID_COUNTER`.

Both look like live tuning parameters to a reader. The inventory's CBR entries
describe clustering, TTL-like pruning and shell UIDs, so a reader could
reasonably assume `YOSHI_CB_MEMBER_TTL` governs the described pruning. It does
not.

### 2.5 Field Utilities — three dead rope classes

`config.cpp` declares `Spring100xRope`, `Spring50xRope`, `Spring10xRope` and
`Spring1xRope`, differing only in `springFactor`. Only `Spring1xRope` is
referenced (`fn_towingServer.sqf:123`, `fn_initRopes.sqf:140-148`). The
inventory's accepted towing entry does not record that three unused stiffness
variants ship in the config. (They are also the cheapest available A/B material
for any future rope experiment — see the recon document, F6.)

### 2.6 Field Utilities — an empty Zeus category

`CfgFactionClasses >> FieldUtilsSupport_ZEUS_Category` ("Pontifex: Zeus Field
Utilities") is declared, and the inventory correctly states "Field Utilities has
no Zeus activation tool" / "exposes no Zeus tool". The empty category itself is
not recorded. It is the visible residue of an intended Zeus surface and would
appear in a curator's category list.

### 2.7 A suite-wide ACE cargo policy applied with no setting

`YOSHI_setObjectLoadHandling` (`fn_objectHandling.sqf`) calls
`[_object, -1] call ace_cargo_fnc_setSize` on **every** `ReammoBox_F`, at server
init and on every `EntityCreated`. The inventory's §4.3 entry describes contact
attachment and nearby supply actions but does not record that the feature
disables ACE cargo for ammo boxes suite-wide, unconditionally, with no CBA
setting or module attribute. That is a cross-cutting behavioral statement about
any mission running Field Utilities, and it belongs in the inventory whatever
the eventual review decides.

### 2.8 A zero-byte function registered as `postInit`

`functions/task_recon/fn_recon_task.sqf` is **0 bytes** and is registered
`class recon_task {postInit = 1;}` in `config.cpp`. The inventory records
"`fn_recon_task.sqf` is empty"; it does not record that the empty file is
nonetheless wired into the postInit chain.

### 2.9 Duplicated helpers across mods, one pair divergent

* `YOSHI_pad4` / `YOSHI_pos_to_grid` (Vigil, `fn_core.sqf`) and
  `YFU_pad4` / `YFU_posToGrid` (Field Utilities, `fn_initMapTools.sqf`) are
  independent implementations of the same grid formatting.
* `YOSHI_addMarker` (`FieldUtils/functions/global/fn_initMapTools.sqf:1`) and
  `YAS_addMarker` (`AdvSys/functions/global/fn_core.sqf:7`) are near-identical
  and **have diverged**: the Advanced Systems copy declares `_markerName` and
  `_marker` `private`; the Field Utilities copy does not, and leaks two
  mission-namespace globals per call. Both are orphaned.

The inventory treats geometry/packing and map helpers as consumer-owned and
deferred, which is consistent — but cross-mod duplication with a one-sided fix is
a maintenance fact worth a line.

### 2.10 A product function whose only caller is its own scenario

`YFU_bridge_beginPlanPreview` has no product caller. Its sole invocation in the
repository is
`mods/field-utilities/tests/tribunal/bridge_builder.py:344`
(`[_box, false] call YFU_bridge_beginPlanPreview;`).

The canonical program is explicit that a contract must be driven from its real
entry point and that "calling a helper near the end of the owning mod's own
pipeline proves that helper, not the path a user or integrator takes". A
function reached only by the test is the limiting case of that warning. This is
recorded as an inventory/coverage observation, not as a claim that the bridge
preview contract is wrong — the accepted entry states preview is "COVERED
through data for the accepted layouts", which may well be its intent.

---

## 3. Globals with no caller anywhere

Forty-four global symbols are defined and never referenced. Some are already
recorded in the inventory (`YOSHI_addItemsToFabricator`,
`YOSHI_attachHeliLiftRopes`, the vehicle-sound helpers,
`YOSHI_toggleDisplayLocationDataOnMap`, the fixed-wing laser harness helpers);
the rest are not.

| Symbol | File |
| --- | --- |
| `YAS_addMarker` | `advanced-systems/…/global/fn_core.sqf` |
| `YAS_fnc_notifyCurator` | `advanced-systems/…/global/fn_utils.sqf` |
| `YOSHI_beamVic2Pos` | `advanced-systems/…/global/fn_core.sqf` |
| `YOSHI_fnc_apsUnregisterActionsGlobal` | `advanced-systems/…/aps/fn_aps.sqf` |
| `YOSHI_fnc_randomPointInCircle` | `advanced-systems/…/cbr/fn_originHandler.sqf` |
| `YOSHI_CB_MEMBER_TTL`, `YOSHI_CB_nextUid` | `advanced-systems/…/cbr/fn_cbr.sqf` |
| `YFU_bridge_attachActionsToBuilderBox`, `…ToObject`, `…beginPlanPreview`†, `…buildFromObject`, `…createExtendAction`, `…createRootAction`, `…debugMeasurements`, `…debugPlanPreview`, `…getObjectBuildPlacement`, `…getObjectForwardPlacement`, `…setAllowClipping` | `field-utilities/…/bridge/fn_bridgeUtils.sqf` |
| `YOSHI_addItemsToFabricator` | `field-utilities/…/global/fn_fabricator.sqf` |
| `YOSHI_attachHeliLiftRopes` | `field-utilities/…/ropes/fn_initRopes.sqf` |
| `YOSHI_canPackObjectsInContainer`, `YOSHI_packItemSizesFlatInContainer` | `field-utilities/…/fabricator/fn_boxPacking.sqf` |
| `YOSHI_FLING_THING`, `YOSHI_getBoundingCorners`, `YOSHI_localToReal` | `field-utilities/…/global/fn_initGeometry.sqf` |
| `YOSHI_playVehicleSoundGlobal`, `YOSHI_stopVehicleSoundGlobal` | `field-utilities/…/global/fn_sounds.sqf` |
| `YOSHI_toggleDisplayLocationDataOnMap` | `field-utilities/…/global/fn_initMapTools.sqf` |
| `YSF_fnc_notifyCurator`, `YSF_toggleWhitelistedObject` | `visual-support-tablet/…/global/fn_utils.sqf` |
| `YOSHI_isHeliPad`, `YOSHI_progressColor`, `YOSHI_setWaypoint`, `YSF_isVehicle` | `visual-support-tablet/…/global/fn_core.sqf` |
| `YOSHI_refreshAssetList` | `visual-support-tablet/…/tablet/fn_assets.sqf` |
| `YOSHI_taskFW_findNearestFabricator`, `YSF_fwRootActionCondition` | `visual-support-tablet/…/task_fixedWing/fn_fixedWing.sqf` |
| `YSF_fwAmmoInheritsFrom`, `YSF_fwApplyDefaultPointToRegistry` | `visual-support-tablet/…/task_fixedWing/fn_initFixedWingFunctions.sqf` |
| `YSF_fwLaserTestPrintLast` | `visual-support-tablet/…/global/fn_fwLaserTest.sqf` |
| `YSF_governorStop`, `YSF_taskGet` | `visual-support-tablet/…/governor/fn_governor.sqf` |
| `YSF_helicopterStab_pfhSecondId` | `visual-support-tablet/…/global/fn_heliStabilizer.sqf` |
| `YSF_irLaserViz_testReset` | `visual-support-tablet/…/client/fn_irLaserViz.sqf` |

† `YFU_bridge_beginPlanPreview` has no *product* caller but is invoked by the
permanent bridge scenario — see §2.10.

Two entries deserve attention beyond bookkeeping:

* **`YSF_governorStop`.** The task governor can be started through
  `YSF_governorStart` but has no reachable stop. Any scenario that starts it has
  no product-provided way to leave global state as it found it, which the
  project conventions explicitly require of tier-shared scenarios.
* **`YOSHI_fnc_apsUnregisterActionsGlobal`.** It is redundant rather than merely
  unused: `YOSHI_fnc_apsRegisterActionsGlobal` (`fn_aps.sqf:1482`) already
  clears first by broadcasting the *local* unregister itself
  (`:1493`, `remoteExecCall ["YOSHI_fnc_apsUnregisterActionsLocal", 0, _vehicle]`).
  A globally named second global-unregister entry point therefore exists beside
  a live one that does the same job. The accepted lifecycle review covers
  suspension and resume through the ACE control entry; this duplicate is not
  recorded.

---

## 4. Entries confirmed accurate

Recorded so a future audit does not re-derive them.

| Inventory claim | Verified against source |
| --- | --- |
| "13 exact unique keys" of cross-addon CBA settings | Exactly 13: 4 `YFU_*`, 6 `YSF_*`, 3 `YAS_*`. |
| CORDIS `fn_initSettings.sqf` and `fn_utils.sqf` contain no behavior | Confirmed — 4 and 5 lines, no definitions. |
| Ctrl+Home opens the tablet | `[DIK_HOME, [false, true, false]]` in `VIGIL/functions/global/fn_initSettings.sqf`. |
| Three side terminal variants | `YSF_VigilTerminal_B/I/O` plus matching item and texture sets. |
| `YOSHI_addItemsToFabricator` is unreachable repository-wide | Confirmed. |
| Field Utilities exposes no Zeus tool | Confirmed — no `scopeCurator` module in its `CfgVehicles` (but see §2.6). |
| Homepage page and registration are commented out | Confirmed (`fn_init.sqf:5`, `page_home.hpp` not included by the dialog). |
| `fn_recon_task.sqf` is empty | Confirmed — 0 bytes (but see §2.8). |
| Advanced Systems audio content | All 26 APS `CfgSounds` classes and both `YAS_OphanimReload*` classes have at least one SQF reference; no dead audio. |
| Manifest and runtime discover the same scenario set | Confirmed and test-enforced (see §1.2). |

---

## 5. Suggested disposition

For the inventory owner, in descending order of reader impact:

1. **§1.1** — refresh the scenario table to twenty-one rows. Purely mechanical
   and the highest-value correction, because that table is what a cold reader
   trusts.
2. **§1.3** — either write the missing artillery/markers review, or state in
   §3.4 that the contract lives in `ScenarioReview` metadata rather than a
   review document. Today the section silently implies a review that a reader
   cannot find.
3. **§2.3** and **§2.7** — two behavioral statements adjacent to accepted
   contracts (a second whitelist entry point; a suite-wide ACE cargo policy)
   that the inventory does not currently make.
4. **§2.1**, **§2.2**, **§2.4**, **§2.5**, **§2.6**, **§2.8**, **§2.9** —
   scaffolding and residue worth one line each under the relevant family.
5. **§3** — consider whether the orphan list belongs in the inventory at all,
   or whether a periodic regenerated audit like this one is the better home. It
   changes with almost every commit, which argues against embedding it.
6. **§1.2** — a stale sentence in `CLAUDE.md`, not the inventory. Left untouched
   here because it is accepted guidance.

None of the above is a change to any coverage or review status.
