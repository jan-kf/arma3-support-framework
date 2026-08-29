# Pontifex source archaeology — 2026-08-24

> **NON-AUTHORITATIVE.** See [`README.md`](README.md). This is not a review, not
> a classification, not coverage, and not a defect list. Every consequential
> reading ends in a question for a future Sol review or characterization, never
> in a conclusion. Nothing here changes any feature status.

Pass performed against `6d12984` with a clean worktree, after the five coverage
commits that followed the previous reconnaissance. Method: a full cross-reference
of every `YOSHI_`/`YSF_`/`YAS_`/`YFU_`/`YCD_` global (813 definitions) against
product source, permanent scenarios, static tests and tooling, separately; plus
config/IDC/sound consumption audits and targeted reading.

Grades: **CODE** (directly visible in source), **DOCUMENTATION** (stated by an
accepted doc), **BIKI**/**COMMUNITY** (upstream material), **INFERENCE** (my
reading, requiring verification).

Findings marked **[NEW]** were not in
[`pontifex-remaining-feature-recon-2026-08-23.md`](pontifex-remaining-feature-recon-2026-08-23.md).
Section 10 records leads that turned out **not** to be defects, and corrects two
claims from that earlier pass — it should be read before acting on anything in it.

---

## Priority summary

| # | Finding | Importance | Difficulty |
| --- | --- | --- | --- |
| F1 | "Do Not Climb" tablet option is the enrolment switch for the deferred stabilizer | **Very high** | Low |
| F2 | `YSF_AAE_DEBUG` is an unregistered debug channel hardcoded on, broadcasting to all clients | **High** | Low |
| F3 | Runtime `ace_cargo_fnc_setSize -1` overrides Pontifex's own `ace_cargo_size = 2` boxes | **High** | Low |
| F4 | CORDIS ships a complete second dedupe cache and a duplicate side resolver, both dead | **High** | Low |
| F5 | Stabilizer's per-second server handler has no stop path | Medium-high | Low |
| F6 | Developer laser harness installs a debug fallback that ignores the settings contract | Medium | Low |
| F7 | Three tablet sound classes ship with assets and no player | Low-medium | Trivial |
| F8 | `YSF_AAE_ENABLED` is a hardcoded, undocumented kill switch over covered CAS behavior | Medium | Trivial |

---

## F1 [NEW] — The tablet's "Do Not Climb" option enrols the deferred stabilizer

### Code surface

* `source/visual-support-tablet/addons/VIGIL/functions/task_transport/fn_transport.sqf:80`
  (dispatch) and `:92` (RTB)
* `source/visual-support-tablet/addons/VIGIL/functions/task_transport/fn_transport_task.sqf:23`, `:41-43`, `:137-140`
* `source/visual-support-tablet/addons/VIGIL/functions/global/fn_heliStabilizer.sqf`
* `source/visual-support-tablet/addons/VIGIL/functions/task_cas/fn_cas_task.sqf:152`

### Directly observed facts (CODE)

The transport task's opaque parameter array is unpacked positionally:

```sqf
_d params ["_destATL", ["_maxAlt", 20], ["_enableStabilization", false],
           ["_ignoreEn", false], ["_playRadio", true], ["_mode", "dispatch"],
           ["_completionVariable", ""]];
```

Both tablet entry points build that array from tablet state:

```sqf
private _do_not_climb = _s get "do_not_climb";
...
[_destPos, _maxAlt, _do_not_climb, _ignoreEn, true, "dispatch"]
```

The **third element (index 2)** is therefore `do_not_climb` on the caller side
and `_enableStabilization` on the handler side. When it is true, the handler runs
`YSF_STABILIZE_HELICOPTERS pushBackUnique _v` (`:42`), which the per-second
scanner consumes and which starts the per-frame `addForce` loop. The `finally`
stage unregisters under the same flag (`:139`).

The CAS RTB caller passes a hardcoded `false` in that element
(`fn_cas_task.sqf:152`: `[_destPos, 20, false, false, false, "rtb", "YSF_cas_state"]`),
so CAS never enrols.

### Why it looks suspicious

The user-facing concept ("do not climb") and the internal concept ("enable
stabilization") are joined only by array position, with no named binding
anywhere. A reader of either file alone cannot see the connection.

### Existing review/coverage status (DOCUMENTATION)

* Inventory §3.5: eligibility/request "captures destination, altitude,
  ignore-enemy, and do-not-climb state. **Implemented; PARTIALLY COVERED.**
  Eligibility/locality is direct; **the latter option semantics are not explicit
  assertions**." So `vigil-transport` does not assert what this option does.
* Inventory §3.11 and
  [`vigil-helicopter-stabilizer-review.md`](../vigil-helicopter-stabilizer-review.md):
  the stabilizer is **REVIEWED / DEFERRED** — a controlled physical A/B "missed
  predeclared 5 m altitude and 1 m/s vertical-speed usefulness gates", another
  corridor showed the terrain guard can suppress all sampling, and "**Normal
  transport and CAS RTB no longer enroll automatically.**"

That documented sentence is literally accurate: the parameter defaults to
`false`, so nothing enrols *automatically*. What it does not say is that a
shipped tablet checkbox sets it.

### Relevant upstream knowledge

**BIKI** `addForce`: "Applies given force for **one frame** (essentially an
impulse)". Candidate **C10** in
[`GENERIC_CHARACTERIZATION_BACKLOG.md`](/mnt/services/arma-knowledge/docs/GENERIC_CHARACTERIZATION_BACKLOG.md)
asks whether per-frame `addForce` is frame-rate dependent; the force term here
also multiplies `getMass`, which is backlog candidate **C7**.

### Possible consequence if the suspicion is correct

A shipped, reachable UI option would be the sole user-facing control for a
mechanism that a controlled experiment already found did not meet its own
usefulness gates, on a code path no permanent scenario asserts. Either the
option quietly does nothing useful, or the "deferred" classification does not
describe the shipped product surface.

### Question for Sol

Is "Do Not Climb" intended to be the user-facing control for the helicopter
stabilizer? If yes, does the stabilizer's `DEFERRED` classification and its
failed usefulness gates apply to a reachable shipped option, and what does the
option promise a user? If no, what was the third element of the transport parameter
array meant to carry, and is `do_not_climb` implemented anywhere else?

**Importance: very high.** **Difficulty: low** (static reading plus one product
decision; no experiment needed to pose the question).

---

## F2 [NEW] — `YSF_AAE_DEBUG` is an unregistered debug channel, hardcoded on

### Code surface

* `source/visual-support-tablet/addons/VIGIL/functions/task_cas/fn_airAutoEngage.sqf:10`, `:16-22`, `:114`, `:153`, `:200`, `:544`, `:550`
* `source/core/addons/CORDIS/functions/global/fn_core.sqf:468-487`

### Directly observed facts (CODE)

`fn_airAutoEngage.sqf:10` sets, at preInit on every machine:

```sqf
YSF_AAE_DEBUG = true;
```

`YSF_AAE_dbg` then gates on it and passes it as the *setting name*:

```sqf
if !(missionNamespace getVariable ["YSF_AAE_DEBUG", false]) exitWith {};
if !(isNil "YCD_fnc_debugMsg") exitWith {
  [_msg, "YSF_AAE", "YSF_AAE_DEBUG"] call YCD_fnc_debugMsg;
};
```

CORDIS then broadcasts the line to every machine and each one re-checks the same
variable:

```sqf
YCD_fnc_showDebugLine = { ... if (missionNamespace getVariable [_settingName, false]) then { systemChat _line; }; };
YCD_fnc_debugMsg = { ... [_line, _settingName] remoteExecCall ["YCD_fnc_showDebugLine", 0]; diag_log _line; };
```

Because the preInit assignment runs on clients too, both gates are true
everywhere. Two of the five call sites are on the engagement path
(`fired` at `:544`, `fire rejected` at `:550`), reached from the auto-engage tick, whose interval is
`missionNamespace getVariable ["YSF_AAE_INTERVAL", 5]` seconds (`:564-568`).

`YSF_AAE_DEBUG` is **not** one of the registered CBA settings — the three
registered debug keys are `YSF_showDebugMessages`, `YAS_showDebugMessages` and
`YFU_showDebugMessages`, all defaulting to `false`.

### Why it looks suspicious

Every other debug channel in the suite is an opt-in CBA setting defaulting off.
This one is a plain global, hardcoded on, and it reaches `systemChat` on all
clients rather than only the log.

### Existing review/coverage status (DOCUMENTATION)

[`cba-settings-contract-review.md`](../cba-settings-contract-review.md) is
**REFINED; ACCEPTED / COVERED** for "13 exact unique keys, types,
defaults/bounds, global/local scope, live consumer handoff, and fallback parity",
and specifically that "debug descriptions match always-log plus
optional-systemChat behavior". Inventory §3.11 records "The static
always-log/conditional-`systemChat` control flow is covered; actual client
presentation remains unproven." `vigil-cas` is **COVERED**.

### Possible consequence if the suspicion is correct

Shipped rotary-wing CAS would emit `systemChat` to every player for every shot
and every rejected shot, in every mission, with no supported way to turn it off
short of a mission script setting the undocumented global. The accepted
13-key settings contract would have an unenumerated fourteenth channel whose
condition is always true.

### Question for Sol

Is `YSF_AAE_DEBUG` intended to be a shipped, always-on, all-client channel, or
is it a development default that outlived its purpose? If it should be
configurable, does it belong in the accepted CBA settings contract as a
fourteenth key, and does that contract's "defaults/bounds" claim need to be
re-stated to account for consumers that pass their own setting name to
`YCD_fnc_debugMsg`?

**Importance: high.** **Difficulty: low.**

---

## F3 [NEW] — Runtime cargo-size override contradicts Pontifex's own box configs

### Code surface

* `source/field-utilities/addons/FieldUtils/functions/global/fn_objectHandling.sqf:91`
* `source/field-utilities/addons/FieldUtils/functions/server/fn_initServer.sqf` (postInit sweep and `EntityCreated`)
* `source/field-utilities/addons/FieldUtils/config.cpp:238` (`YFU_Bridge_Box`)
* `source/advanced-systems/addons/AdvSys/config.cpp:176` (`YAS_OPHANIM_box`)

### Directly observed facts (CODE)

`YOSHI_setObjectLoadHandling` begins with:

```sqf
[_object, -1] call ace_cargo_fnc_setSize;
```

It is applied to every existing `ReammoBox_F` at server postInit and to every
newly created one via the `EntityCreated` mission handler.

Both Pontifex boxes declare the opposite intent in config:

```cpp
class YFU_Bridge_Box: Box_NATO_WpsSpecial_F { ... ace_cargo_size = 2; ace_cargo_canLoad = 1; ... };
class YAS_OPHANIM_box: Box_NATO_AmmoVeh_F  { ... ace_cargo_size = 2; ace_cargo_canLoad = 1; ... };
```

### Relevant upstream knowledge (installed ACE 3.21.0.110)

Read from `server/runtime/dependency-mods/@ace/addons/ace_cargo.pbo`:

* the eligibility chain includes `{_item call FUNC(getSizeItem) >= 0}` — a size
  below zero disqualifies the item;
* ACE's own Eden attribute uses
  `defaultValue = GET_NUMBER(configOf _this >> ace_cargo_size, -1)`, i.e. **-1
  is ACE's "unset" sentinel**, and unset means not loadable.

### Why it looks suspicious (INFERENCE)

If `Box_NATO_WpsSpecial_F` and `Box_NATO_AmmoVeh_F` both descend from
`ReammoBox_F` — which needs a one-line config confirmation, not an experiment —
then a Field Utilities feature silently revokes the ACE cargo loadability that
two Pontifex addons explicitly configure, including a box whose entire purpose
is to be transported to a bridge site.

There is a coherent alternative reading: the feature deliberately replaces ACE
cargo with vanilla vehicle-in-vehicle transport, which the newly covered
`fieldutils-cargo-loading` path uses (`setVehicleCargo`). Under that reading the
`ace_cargo_size = 2` config lines are vestigial rather than the runtime being
wrong.

### Existing review/coverage status (DOCUMENTATION)

[`field-utilities-object-handling-review.md`](../field-utilities-object-handling-review.md)
records the fact ("Server postInit sets every existing/new `ReammoBox_F` ACE
cargo size to -1") but not what -1 means in the installed ACE, not that it
collides with Pontifex's own configs, and not whether the collision is intended.
The accepted `fieldutils-cargo-loading` contract covers native loading only.

### Possible consequence if the suspicion is correct

Two shipped, config-declared cargo-able boxes would be un-loadable by ACE cargo
in any mission running Field Utilities, and the suite would carry two config
declarations that never take effect.

### Question for Sol

Do `YFU_Bridge_Box` and `YAS_OPHANIM_box` inherit from `ReammoBox_F`, and does
the runtime `setSize -1` therefore override their configured
`ace_cargo_size = 2`? Is replacing ACE cargo with native vehicle-in-vehicle
transport for all ammo boxes an intended, suite-wide product statement — and if
so, should the two config declarations be retired and the statement recorded,
or should the sweep exclude Pontifex's own classes?

**Importance: high.** **Difficulty: low** (config inheritance check plus a
product decision).

---

## F4 [NEW] — CORDIS carries a complete dead dedupe cache and a dead duplicate side resolver

### Code surface

`source/core/addons/CORDIS/functions/global/fn_core.sqf` — `:124`
(`YCD_fnc_pruneLocalOnceCache`), `:139` (`YCD_fnc_claimLocalOnceKey`), `:286`
(`YCD_fnc_targetsFromSide`), `:39` (`YCD_fnc_runOnServer`), `:292`
(`YCD_fnc_resolveTargets`).

### Directly observed facts (CODE)

Cross-reference over product source, all 23 permanent scenarios, all static
tests and all tooling:

| Symbol | product | scenario | static |
| --- | ---: | ---: | ---: |
| `YCD_fnc_claimLocalOnceKey` | 0 | 0 | 0 |
| `YCD_fnc_pruneLocalOnceCache` | 0 | 0 | 0 |
| `YCD_localOnceCache` | 0 | 0 | 0 |
| `YCD_fnc_targetsFromSide` | 0 | 0 | 0 |
| `YCD_fnc_runOnServer` | **0** | 2 | 0 |

All three `*Once` routing functions claim through the **server** cache
(`YCD_fnc_claimOnceKey`, `YCD_onceCache`, `serverTime`-based) — verified at
`:204`, `:231` and `:266`. No caller anywhere claims through the local cache
(`diag_tickTime`-based).

`YCD_fnc_targetsFromSide` computes `allPlayers select {side _x isEqualTo _side}`
then filters; `YCD_fnc_resolveTargets`' `case "SIDE"` **repeats that expression
inline** rather than calling it.

`YCD_fnc_runOnServer` has no product caller. Its only callers in the repository
are two lines of `source/core/tests/tribunal/cordis_routing.py`.

### Why it looks suspicious

Three separate shapes in one accepted module: a complete parallel subsystem with
no consumer; a public helper duplicated inline at its only conceptual use site;
and a public routing primitive exercised only by its own permanent scenario.

### Existing review/coverage status (DOCUMENTATION)

Inventory §1.2 states: "**Server/local TTL caches** are **REFINED; ACCEPTED /
COVERED** for operation-aware positive TTLs, invalid-work non-claim, expiry
reuse, and safe post-iteration pruning." §5.1 records the CORDIS consumer
contract as `ACCEPTED / COVERED`. The `cordis-routing` scenario exercises
`YCD_fnc_pruneOnceCache` (server) and does not touch the local cache.

### Possible consequence if the suspicion is correct

The accepted inventory sentence would claim coverage for a "local TTL cache"
that has no caller and no assertion. The two duplicate side resolvers could
diverge silently under a future change, with the orphan remaining a public,
plausibly-supported entry point for missions and sibling mods. And a documented
CORDIS routing primitive would be kept alive only by its test.

### Question for Sol

Does "Server/**local** TTL caches" in inventory §1.2 refer to
`YCD_localOnceCache`, or to the local-machine side of the server cache? If the
former, what is the local cache for, why does no route claim through it, and
should the accepted coverage sentence be narrowed? Separately: is
`YCD_fnc_runOnServer` a promised part of the CORDIS public contract that
consumers should use, or an internal that only the scenario keeps alive — and is
`YCD_fnc_targetsFromSide` the supported side-resolution API or a duplicate that
should defer to `YCD_fnc_resolveTargets`?

**Importance: high** (touches an accepted shared contract every other mod
depends on). **Difficulty: low.**

---

## F5 [NEW] — The stabilizer's per-second server handler has no stop path

### Code surface

* `source/visual-support-tablet/addons/VIGIL/functions/server/fn_initServer.sqf:21`
* `source/visual-support-tablet/addons/VIGIL/functions/global/fn_heliStabilizer.sqf:12`, `:24-27`, `:49`

### Directly observed facts (CODE)

```sqf
YSF_helicopterStab_pfhSecondId = [YSF_helicopterStab_perSecond, 1, nil] call CBA_fnc_addPerFrameHandler;
```

runs unconditionally at server postInit. `YSF_helicopterStab_pfhSecondId` is
assigned in exactly two places (here and a `nil` initialiser at
`fn_heliStabilizer.sqf:12`) and is **read nowhere** — cross-reference reports
zero product, scenario, static and tooling reads.

By contrast the per-*frame* handler self-removes when its work list empties
(`:24-27`) and clears its own handle.

The only remaining product touchpoint of the stabilizer besides enrolment is
`YSF_helicopterStab_unregister`, called once from
`fn_transport_task.sqf:140`.

### Why it looks suspicious

A deferred experimental mechanism keeps a 1 Hz server handler running for the
whole mission, and the handle that would allow removing it is stored in a
variable nothing reads.

### Existing review/coverage status (DOCUMENTATION)

Inventory §3.11: the stabilizer is **REVIEWED / DEFERRED**, and "Explicit
experimental finalization now clears all stabilizer state."

### Possible consequence if the suspicion is correct

"Clears all stabilizer state" could not include the scanning handler itself,
since no code path can remove it. Every mission would run a permanent background
scan for a feature classified as deferred. The per-iteration cost is small while
`YSF_STABILIZE_HELICOPTERS` is empty, so this is a lifecycle and honesty
question rather than a performance one.

### Question for Sol

Does "clears all stabilizer state" include the per-second handler, and if not,
should the deferred classification permit an unstoppable always-on server
handler? Is `YSF_helicopterStab_pfhSecondId` meant to be read by a stop path
that was never written?

**Importance: medium-high.** **Difficulty: low.**

---

## F6 [NEW] — The deferred laser harness installs a debug fallback that ignores the settings contract

### Code surface

* `source/visual-support-tablet/addons/VIGIL/functions/global/fn_fwLaserTest.sqf:1-9`
* `source/visual-support-tablet/addons/VIGIL/functions/global/fn_utils.sqf:13-16`
* `source/visual-support-tablet/addons/VIGIL/config.cpp` (`class Global` preInit order)

### Directly observed facts (CODE)

`YSF_fnc_debugMsg` — used at 76 product call sites — is defined twice.

The canonical definition honours the setting:

```sqf
YSF_fnc_debugMsg = { params ["_msg"]; [_msg, "YSF", "YSF_showDebugMessages"] call YCD_fnc_debugMsg; };
```

The laser harness installs a guarded fallback:

```sqf
if (isNil "YSF_fnc_debugMsg") then {
  YSF_fnc_debugMsg = { params ["_msg"]; diag_log format ["[YSF] %1", _msg];
    if (hasInterface) then { systemChat format ["[YSF] %1", _msg]; }; };
};
```

The fallback consults no setting and `systemChat`s unconditionally. In
`config.cpp`, `class fwLaserTest` is declared **before** `class utils` in the
same preInit group.

### Why it looks suspicious (INFERENCE)

If preInit functions run in declaration order, the fallback is installed first
and later overwritten by the canonical definition, leaving the correct end state
but an interval during init in which the unconditional version is live for any
caller. If preInit order is not declaration order, the outcome depends on
something no comment records.

### Existing review/coverage status (DOCUMENTATION)

[`vigil-developer-laser-harness-review.md`](../vigil-developer-laser-harness-review.md)
classifies `fn_fwLaserTest.sqf` as **REVIEWED / DEFERRED** and says to "remove,
relocate, or capability-gate it before supported use" for reasons of destructive
execution and result storage. It does not record that the file also shadows a
shared function whose behavior is part of an accepted contract.

### Question for Sol

What order does the Functions Library use for preInit entries in one class, and
is there any window during mission init in which the unconditional-`systemChat`
fallback is the live `YSF_fnc_debugMsg`? Independently of the answer: should a
deferred developer harness be permitted to define a shared function that an
accepted settings contract describes?

**Importance: medium.** **Difficulty: low** (a Sacred Texts retrieval on the
Functions Library plus a static ordering check).

---

## F7 [NEW] — Three tablet sound classes ship with assets and no player

### Directly observed facts (CODE)

Consumption audit of every `CfgSounds` class in `VIGIL/config.cpp` across all
product `.sqf`/`.hpp`/`.cpp`:

| Class | Played by |
| --- | --- |
| `UiOpen` | **nothing** |
| `UiClose` | **nothing** |
| `UiHover` | **nothing** |
| `BootUp` | `fn_init.sqf:55` |
| `TurnOff` | `config.cpp:111` (dialog `onUnload`) |
| `UiChar01`–`06`, `UiTabSwitch`, `UiActivate`, `UiSelect`, `UiMapSelect`, `UiSubmit`, `UiHum`, `DialUp` | one site each |

The three unused classes ship their assets:
`tablet_ui_open_01.ogg`, `tablet_ui_close_01.ogg`, `tablet_ui_hover.ogg`.

Separately, every class declares a `name = "ui_..."` value; **no code references
any of those `name` values** — call sites use the class name. Whether the `name`
field has any consumer at all is unclear.

### Why it looks suspicious (INFERENCE)

Open and close *do* have sounds (`BootUp`, `TurnOff`), so `UiOpen`/`UiClose`
look like a superseded earlier pairing; `UiHover` has no analogue, suggesting
hover feedback was designed and never wired.

### Existing review/coverage status (DOCUMENTATION)

Inventory §3.1 covers open/theme/intro/close/reopen; audio generally is deferred
under `-noSound`. No review mentions these classes.

### Question for Sol

Are `UiOpen`, `UiClose` and `UiHover` intended tablet feedback that was never
wired, or superseded assets to retire? Does the `name` field of `CfgSounds`
entries have any consumer in this suite, or is it inert?

**Importance: low-medium** (obsolete complexity; also cheap deletion candidates).
**Difficulty: trivial.**

---

## F8 [NEW] — `YSF_AAE_ENABLED` is a hardcoded, undocumented kill switch

### Directly observed facts (CODE)

`fn_airAutoEngage.sqf:1` sets `YSF_AAE_ENABLED = true;` at preInit. It is read
exactly once, at `:455`:

```sqf
if !(missionNamespace getVariable ["YSF_AAE_ENABLED", true]) exitWith {false};
```

Nothing ever sets it false. It is not a CBA setting and not a module attribute.

### Why it looks suspicious

It is a globally named, mission-settable switch that can silently disable a
`COVERED` behavior with no feedback and no documentation.

### Existing review/coverage status (DOCUMENTATION)

`vigil-cas` is **COVERED** for dispatch, target selection, attack and RTB.
[`vigil-cas-review.md`](../vigil-cas-review.md) does not mention this global.

### Question for Sol

Is `YSF_AAE_ENABLED` a supported mission-maker kill switch for rotary CAS
auto-engagement, or stale scaffolding? If supported, where is it documented and
should the covered contract state that a global can disable it? If not, should
it be retired so the covered path has one entry condition?

**Importance: medium.** **Difficulty: trivial.**

---

## 9. Confirmed-still-present, previously recorded

Re-verified at `6d12984`, unchanged, and **not** re-argued here:

* the unrealized map-page IDC family — `IDC_PAGE_MAP`, `IDC_MAP_COORD_BTN`,
  `IDC_MAP_TAB_*`, `IDC_ASSETS_TAB_*`, all five `IDC_YSF_VP_*`,
  `IDC_TABLET_TITLE`, `IDC_TABLET_BTN_CLOSE`: still **zero** live references;
* `YSF_toggleWhitelistedObject` — still no caller; its guard
  (`!isServer || remoteExecutedOwner > 2`) still fails closed against clients,
  so it remains a bypass of the accepted audit pipeline rather than a client-
  reachable hole;
* `YOSHI_CB_MEMBER_TTL` and `YOSHI_CB_nextUid` — still assigned and never read;
* the twelve orphaned `YFU_bridge_*` globals, including the empty
  `YFU_bridge_attachActionsToObject` stub and the fully-implemented
  `YFU_bridge_attachActionsToBuilderBox` duplicate registration path;
* `YFU_bridge_beginPlanPreview` — still no product caller; still invoked by
  `bridge_builder.py:344` and asserted by `tests/test_bridge_builder_contract.py:108`;
* `YSF_governorStop` and `YSF_taskGet` — still unreachable.

The orphan-global count is now **47** (was 44); the three additions are the
CORDIS symbols in F4.

Scenario documentation drift has partly closed and partly not: there are now
**23** permanent scenarios. The two newest (`fieldutils-cargo-loading`,
`vigil-transport-pad-ab`) **are** listed in the inventory table, but seven older
identifiers are still absent — `advsys-aps-eden-module`, `advsys-aps-zeus-module`,
`advsys-cbr-modules`, `fieldutils-ace-composition`, `fieldutils-bridge-builder`,
`fieldutils-eden-modules`, `vigil-whitelist-modules`.

---

## 10. Leads investigated that are **not** defects

Recorded so that nobody spends a review on them, and so two earlier claims are
corrected.

**Transport does not auto-enrol the stabilizer.** `_enableStabilization`
defaults to `false` and CAS RTB passes a hardcoded `false`, so the documented
sentence in inventory §3.11 is accurate as written. The live question is F1 — the
tablet checkbox — not automatic enrolment.

**`YAS_fnc_notifyCurator` is deliberately displaced, not accidentally dead.**
`tests/test_cbr_module_contract.py:57` and
`tests/test_aps_zeus_module_contract.py:76` both `assertNotIn` it, pinning that
the Zeus paths use `BIS_fnc_showCuratorFeedbackMessage` instead so feedback
reaches the placing curator only. Wiring it back in would break accepted tests.
The residual question is only whether the wrapper should be retired.
(`YSF_fnc_notifyCurator` is dead with no such test and has no equivalent
protection.)

**Scenarios do invoke real UI entry points.** Spot-checking every scenario-called
product global with a single product caller: `YOSHI_taskArty_submit`,
`YOSHI_taskCAS_submit`, `YOSHI_taskTRN_submit`, `YOSHI_taskFW_deploy`,
`YOSHI_taskFW_logiStub`, `YFU_assetsSubmitOrder` and `YFU_bridge_dialogSubmit`
are each called from exactly one place — the `action=` statement of the
corresponding UI control in `page_assets.hpp` / `page_bridge.hpp`. The scenarios
invoke the same statement the button runs, which is what the canonical program
permits. `YSF_UI_OpenTablet`'s single caller is the CBA keybind. No evidence was
found that any scenario stimulates a feature at a lower level than its real entry
point, with the two exceptions already named (`YFU_bridge_beginPlanPreview`,
`YCD_fnc_runOnServer`).

**Per-mod debug/chat/curator wrappers are an intended pattern, not duplication.**
`YSF_/YAS_/YFU_fnc_debugMsg`, `emitSideChat`, `emitSideRadio` all delegate to
CORDIS with their own setting key; this is the documented shared-runtime wrapper
design. Only the two `notifyCurator` wrappers are unused.

**Correction to the 2026-08-23 recon (V1).** That document said Pontifex "probes
for a pre-existing helipad within **20 m**". 20 m is only
`YOSHI_getNearestHelipad`'s *default*; the transport LZ path calls it with
**100 m** (`fn_transport_task.sqf`, `[_destATL, 100] call YOSHI_getNearestHelipad`).
The underlying question — whether the engine may snap to a pad outside the
product's probe radius — stands, but at 100 m, not 20 m.

**Correction to the 2026-08-23 recon (F2 area).** That document listed
`YSF_fnc_debugMsg` as having a single definition. It has two (F6). The second is
guarded by `isNil`, so it is a fallback rather than an override.

---

## 11. Clusters — one review that would resolve several paths

### Cluster A — Vigil transport altitude control and the stabilizer
**Resolves: F1, F5, plus the deferred stabilizer and the "do-not-climb semantics
are not explicit assertions" gap in inventory §3.5.**

One product decision ("what does Do Not Climb promise?") plus one lifecycle
question ("can the scanner be stopped?") would close the enrolment path, the
unasserted UI option, the unstoppable handler, and the stabilizer's deferred
status in a single review. It would also give backlog candidates **C7**
(`getMass`) and **C10** (`addForce` frame-rate dependence) a concrete first
consumer. This is the highest-value cluster in this pass.

### Cluster B — the debug and telemetry contract
**Resolves: F2, F6, and the boundary of the accepted CBA settings contract.**

Both findings are about the same mechanism: consumers passing their own setting
name to `YCD_fnc_debugMsg`, and a shared debug function that can be shadowed.
One review could establish how many debug channels exist, which are registered,
what their defaults are, and who may define `YSF_fnc_debugMsg`. It would also
settle whether `YSF_AAE_ENABLED` (F8) belongs in the same configuration surface.

### Cluster C — CORDIS dead surface versus accepted claim
**Resolves: F4 in full, and tightens inventory §1.2 and §5.1.**

A single static review of CORDIS' public API — which symbols are promised, which
are internal, which are dead — would settle the local cache, the duplicate side
resolver and the test-only routing primitive together, with no experiment.

### Cluster D — who owns cargo eligibility
**Resolves: F3, the two vestigial `ace_cargo_size` config declarations, and the
relationship between ACE cargo and the newly covered native loading path.**

One decision ("is ACE cargo deliberately disabled suite-wide for ammo boxes?")
determines whether config or runtime is authoritative and whether Pontifex's own
boxes are meant to be ACE-loadable.

### Cluster E — orphan retirement sweep
**Resolves: much of §9 at once.**

47 globals with no caller, three unplayed sound classes with assets, ~17 unused
IDC constants, two dead CBR constants, and twelve orphaned bridge helpers. These
are individually trivial and collectively a large reduction in surface area. They
share one question — *is this promised, or is it residue?* — and the inventory's
own rule that unknown intent is not permission to delete means the answer has to
come from the author, not from a reviewer. A single pass asking that question
once per family would be far cheaper than eleven separate reviews.

---

## Method notes and limits

"No caller" is a textual cross-reference over `source/`,
`source/*/tests/tribunal/`, `tests/`, `tools/` and `tribunal/`, excluding each
symbol's own definition line. A symbol reached only through a runtime-composed
string, a `remoteExec` target named at runtime, a config `function =` entry, or a
mission-authored call from outside the repository would be misreported. Every
finding above was additionally read in source before being recorded, but none of
it is grounds for deletion on its own.

ACE behavior in F3 was read from the installed
`ace_cargo.pbo` (3.21.0.110) shipped under `server/runtime/dependency-mods/`, not
from upstream documentation. No experiment was designed or run.
