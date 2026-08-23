# Pontifex remaining-feature reconnaissance — 2026-08-23

> **NON-AUTHORITATIVE.** See [`README.md`](README.md). Nothing here is a review,
> a classification, a contract, or evidence. Grades are `BIKI`, `COMMUNITY`,
> `LEDGER-CONJECTURE`, `CODE`, `INFERENCE` as defined there.

Scope: the surfaces that [`../pontifex-feature-inventory.md`](../pontifex-feature-inventory.md)
still records as unreviewed, partially covered, deferred, refine/rewrite-pending,
or experimentation-pending. Surfaces already at `ACCEPTED / COVERED` appear only
where a named bounded gap remains.

Where a canonical review already exists, this document deliberately does **not**
restate it. It adds only the Sacred Texts, native-alternative candidates, and
mechanism questions that the existing review records as unretrieved or
uncharacterized.

---

## Part 0 — Cross-cutting mechanisms

These six mechanisms recur across many remaining surfaces. Characterizing one
would unblock several reviews at once, which is why they are separated out.

### M1. `getMass` on freshly created and on remote objects

* **CODE.** Three unrelated features gate on `getMass`:
  `source/field-utilities/addons/FieldUtils/functions/global/fn_fabricator.sqf:21`
  (`getMass _object > 200` → `setMass 200` carryability cap),
  `source/advanced-systems/addons/AdvSys/functions/aps/fn_aps.sqf:830`
  (`getMass _x < 1000` anti-drone eligibility), and
  `source/visual-support-tablet/addons/VIGIL/functions/global/fn_heliStabilizer.sqf:38`
  (force term proportional to `getMass _helicopter`).
* **BIKI.** `getMass` "Returns mass of a PhysX object" (rev 373891; Arma 3
  stable [1.12.0, *)). The documentation does not state what is returned for an
  object whose PhysX body is not yet, or never, simulated.
* **BIKI.** `setMass`: "When main syntax is used on **local** vehicle, the change
  is global" (rev 373893). The mutation is therefore locality-sensitive even
  though the read may not be.
* **CODE.** The Fabricator already carries a refinement that waits for a real
  value before applying the cap, but its predicate is `(getMass _object) > 0`
  (`fn_fabricator.sqf:17`).
* **INFERENCE / suspicious.** The recorded open defect is a crate reporting
  `getMass = 1e-12` across six runs. `1e-12 > 0` is **true**, so the settle wait
  exits on the first tick and the cap is skipped. On this reading the timeout is
  not the failing part of the guard — the threshold is. A guard that required a
  plausible lower bound (or `getMass` stability across two samples) would behave
  differently against the same observation. This is a hypothesis about reachable
  code, not a confirmed defect, and it must not be "fixed" before it is measured.
* **INFERENCE.** If a degenerate `getMass` is what an unsimulated or remote
  PhysX body returns, then the anti-drone `getMass _x < 1000` predicate admits
  *every* such UAV rather than filtering small ones, and the eligibility filter
  silently inverts its intent for exactly the entities it cannot measure.
* **Characterization questions.**
  1. What does `getMass` return for an object in the frame it is created, for an
     object with `enableSimulation false`, and for an object local to another
     machine? Is the value stable, monotone, or arbitrary?
  2. Does the degenerate value differ over land versus over water, and does it
     differ for a `createVehicle` at the map origin followed by `setPos`?
  3. Is a two-sample stability requirement sufficient to distinguish "not yet
     simulated" from "genuinely light"?

### M2. Object event-handler locality

* **BIKI** (Event Handlers page, accepted mirror corpus): "**The object-based
  Event Handler is always executed on the computer where it was added.**"
* **BIKI.** `EpeContactStart` (Arma 3 1.00, `globalArgument`): "Triggered when
  object collision (PhysX) starts."
* **BIKI.** `Engine` (`globalArgument`): "Although the event is global, on
  clients (non-server) and applied to remote vehicles, it will fire only if the
  vehicle is closer than about 6 km from the camera."
* **BIKI.** `Killed` is `localArgument`.
* **BIKI** (dev changelog, 22-07-2026, in the accepted corpus): "Fixed: Entity
  config eventhandlers for WeaponChanged/EpeContactStart/EpeContactEnd/EpeContact,
  did only trigger if there was also a scripted eventhandler of the same type."
  This is a *config* event-handler fix; it is recorded here only so a future
  review does not mistake it for a change to scripted EH behavior, and its
  applicability to the tested stable build is unestablished.
* **CODE.** `YOSHI_setObjectLoadHandling` adds `EpeContactStart` from the
  server's `EntityCreated` mission handler
  (`fn_objectHandling.sqf`, `fn_initServer.sqf`). `YFU_fnc_uavAttachIED` adds a
  `Killed` handler on the UAV's owner and records the fact in a **public**
  object variable `YOSHI_UavKilledHandlerAdded`
  (`fn_fpv.sqf`).
* **INFERENCE / locality concern.** A handler added on the server exists only on
  the server. If the object later becomes client-local, the server-added handler
  and the client's physics simulation are on different machines.
* **INFERENCE / suspicious.** Because the FPV "handler added" flag is public but
  the handler itself is machine-local, an ownership migration leaves a UAV whose
  replicated state asserts an IED death handler that no machine will run. The
  attach guard then refuses to re-add it.
* **Characterization questions.**
  1. For a client-owned box, does a server-added `EpeContactStart` fire at all?
  2. Which machine's `Killed` handler runs for an owner-migrated UAV, and does
     the public "added" flag remain truthful across migration?
  3. Does `removeAllEventHandlers` affect only the calling machine's handlers?
     (See A1.)

### M3. `createVehicle` main syntax ignores the Z coordinate

* **COMMUNITY** (R3vo, rev 377509): "The main syntax creates vehicles at ground
  level ignoring the Z in *pos*… equivalent to
  `createVehicle ["vehclass", [pos select 0, pos select 1, 0], [], 0, "NONE"]`."
* **LEDGER-CONJECTURE** (id `d8d509c7-…`): "The main createVehicle syntax
  ignores the input Z coordinate when placing the vehicle."
* **COMMUNITY** (AgentRev): for the *alternative* syntax, `canFloat = 1` classes
  expect PositionAGL, everything else PositionATL.
* **COMMUNITY** (DreadedEntity): created objects get `vectorUp` = terrain
  surface normal.
* **CODE.** `YFU_fnc_uavDropGrenade` (`fn_fpv.sqf:146`) uses the **main**
  syntax: `"GrenadeHand" createVehicle ((getPosATL _vic) vectorAdd [0,0,-0.1])`.
  The IED `Killed` handler likewise uses main syntax for `"Bo_Mk82"` and
  `"HelicopterExploBig"` (`fn_fpv.sqf:59`, `:82`).
* **INFERENCE / suspicious.** If the conjecture holds, "Drop Grenade" does not
  drop anything from altitude: the grenade materialises at ground level directly
  beneath the drone. The feature would appear to work — a grenade detonates
  under the target — while never exercising a fall at all. That is a textbook
  false-PASS shape for any future scenario that asserts only "an explosion
  occurred near the aim point".
* **Characterization questions.**
  1. Confirm or refute the ledger conjecture on the tested build for an ammo
     class, with the drone at a known altitude and an independent position
     oracle sampled in the creation frame.
  2. Does the alternative syntax with an explicit ATL/ASL position produce a
     free fall from altitude for `"GrenadeHand"`?

### M4. The "create at map origin, then `setPos`" pattern

* **CODE.** At least three features create an object at `[0,0,0]` and move it:
  the transport LZ pad (`fn_transport_task.sqf:113-114`), the FPV mortar release
  (`fn_fpv.sqf:130-132`), and — per the recorded Fabricator finding — the
  fixture that produced the spurious `surfaceIsWater` failure.
* **INFERENCE.** The map origin is over water on most terrains. Any per-object
  state that the engine samples at creation time (buoyancy, surface normal,
  PhysX body initialisation, `canFloat` position interpretation per AgentRev
  above, `vectorUp` per DreadedEntity) is therefore sampled *at sea* and then
  carried to the real destination.
* **INFERENCE.** This is the strongest available candidate link between M1's
  degenerate `getMass` and the Fabricator's over-water runs, and it is testable
  cheaply by creating the same class at the destination directly.
* **Characterization question.** Does creating at the destination rather than at
  the origin change `getMass`, `vectorUp`, buoyancy, or settle behavior for the
  same class? One variable, two arms.

### M5. `say3D` concurrency and liveness

* **BIKI** (rev 377687): "an object can only 'say' **one** sound at a time."
* **COMMUNITY** (Benargee): in Arma 2 1.63 the object had to be alive for the
  sound to broadcast, and a kill stopped playback immediately; explicitly
  untested by that author in Arma 3.
* **COMMUNITY** (Killzone_Kid): the command creates a `"#soundonvehicle"` object
  detectable via `allMissionObjects`.
* **CODE.** APS voice/engagement audio, Iron Dome launch audio, the FPV
  `DufflebagShuffle` attach cue, and Vigil's `CfgRadio` acknowledgements all
  route through vehicle-attached sound.
* **INFERENCE.** "One sound at a time" is a *product* problem, not only an audio
  one: an APS number-to-voice status readout and a hard-kill engagement cue on
  the same vehicle cannot both play, so the deferred "audience/overlap policy"
  has an engine-imposed floor that any policy must respect.
* **INFERENCE.** Benargee's liveness report, if it still holds, means the FPV
  IED shuffle and any death-adjacent cue are cut off by the very event they
  announce.
* **Characterization questions.** All of these are blocked for autonomous
  clients (`-noSound`), but `allMissionObjects "#soundonvehicle"` is a **data**
  oracle: it may make sound *dispatch* and *overlap* observable without audio.
  1. Does a second `say3D` on the same object replace, queue, or drop the first,
     and is the `"#soundonvehicle"` object count the discriminator?
  2. Does killing the speaker remove the sound object before its duration?

### M6. `createMarker` naming and the `_USER_DEFINED` prefix

* **BIKI** (rev 378854): "The marker name has to be unique; the command will be
  ignored if a marker with the given name already exists." Markers are created
  for every connected player and all JIP players. A marker is invisible until
  `setMarkerType` is set.
* **COMMUNITY** (X39): "one can create markers which are deletable by the user
  by prefixing the name with `_USER_DEFINED`."
* **COMMUNITY** (Tirpitz, POLPOX): `_USER_DEFINED #n1/n2/n3` encodes owner,
  index and channel; a `/` in the name may break channel visibility in MP.
* **COMMUNITY** (Leopard20): `createMarker` can also fail for reasons other than
  a duplicate name, e.g. the maximum marker count.
* **CODE.** Both dead marker helpers use the prefix:
  `YOSHI_addMarker` (`fn_initMapTools.sqf:1`, name built at `:4`) and `YAS_addMarker`
  (`AdvSys/functions/global/fn_core.sqf:10`). Neither checks the return value.
  CBR uses deterministic counter-derived names instead
  (`fn_originHandler.sqf:74`, `:122`; `fn_cbr.sqf:127`, `:133`).
* **INFERENCE / suspicious.** If X39's report holds, any marker created through
  those helpers is **player-deletable from the map**. For an ID/location marker
  that may be intended; for an authoritative CBR-style threat marker it would
  be a silent authority hole. CBR does not use the prefix, so the two families
  have different erasability by accident of helper choice rather than by policy.
* **INFERENCE / suspicious.** `YOSHI_originMarkerIndex` is a plain mission-scope
  counter. If the CBR preInit ever re-runs within one mission, the counter
  restarts, `createMarker` is silently ignored on the duplicate name, and the
  subsequent `setMarkerShape` on an empty string has no valid target.
* **Characterization questions.**
  1. Is a `_USER_DEFINED`-prefixed marker deletable by a non-admin client on the
     tested build?
  2. What does `createMarker` return on a duplicate name, and does the product's
     unchecked chain of setters fail loudly or silently?

---

## Part 1 — Vigil

### V1. Transport LZ: hidden helipad plus `land "LAND"`

Inventory: **REVIEWED / NEEDS EXPERIMENTATION** (landing works; exact mechanism
necessity unproven).

* **Implementation surface.**
  `source/visual-support-tablet/addons/VIGIL/functions/task_transport/fn_transport_task.sqf:110-131`
  creates `"Land_HelipadEmpty_F"` at `[0,0,0]`, `setPosATL`s it to the
  destination, records `deletePadOnFinish`, then calls
  `YSF_fnc_setVehicleLandMode` with `"LAND"`. The landing predicate is
  `isTouchingGround && unitReady && vectorMagnitude velocity < 2`, held for
  `YSF_TRX_SETTLE_SECONDS`. `YSF_fnc_setVehicleLandMode`
  (`fn_core.sqf:412-421`) already routes to the object owner via
  `YCD_fnc_runOnObjectOwner` before calling `_vic land _mode`.
  `YOSHI_getNearestHelipad` (`fn_core.sqf:254-261`) probes
  `nearestObjects [pos, YOSHI_HELIPADS, 20, …]` — a **20 m** default radius.
* **Mechanics.** `land`, helipad classes, AI pilot state, `unitReady`,
  `isTouchingGround`, object locality.
* **BIKI** (`land`, rev 373721): "Forces a helicopter landing. If there is a
  helipad nearby, the helicopter will attempt to land on it. VTOL on the other
  hand will just land somewhere. **To make helicopter or VTOL land on a specific
  helipad use `landAt`.**"
* **COMMUNITY** (Hardrock): helicopters land at the nearest "H" or "Invisible H"
  if one is around — within 500 m in Arma 1.
* **COMMUNITY** (SNKMAN): a `unitReady` check with a short delay before it is a
  known workaround for a landing bug.
* **Native alternative — the strongest finding in this document.**
  **BIKI** (`landAt`, rev 378376): available since Arma 3 1.68 for dynamic
  airport objects; since **2.18** "it is also possible to make a helicopter land
  at a specific helipad"; and since **2.20**:
  > "`landAt` command has been extended. Helicopter can now be landed not only
  > on a helipad but also at arbitrary position, provided that it is empty and
  > can accomodate the helicopter. In 'Land' landing mode the helicopter lands
  > permanently, while in 'GetIn' and 'GetOut' landing mode the helicopter
  > performs a short touch down before going to the next waypoint. In order to
  > make helicopter wait, the 'waitTime' param can be used. Waiting time is
  > available with `landAt` getter variant… The AI pilot state can be monitored
  > with `getUnitState` command. **The helicopter has to be `local` to the
  > machine executing the command.** VTOL waiting time is not supported."
  All four addons declare `requiredVersion = 2.20`, so this is inside the
  supported floor, not a speculative future API.
* **INFERENCE.** If that documentation holds on the tested build, `landAt` at an
  arbitrary position would remove the need for the hidden pad entirely, and its
  `waitTime` plus `getUnitState` would replace both the settle-second polling
  and the ad-hoc `isTouchingGround`/`unitReady`/velocity predicate with engine
  state. The existing owner-routing in `YSF_fnc_setVehicleLandMode` already
  satisfies the documented locality requirement, so the swap is contained.
* **Locality/authority.** Pad creation happens wherever the task stage runs
  (server); `land` is owner-routed. `landAt`'s documented locality requirement
  matches the existing route. Pad deletion is conditional on
  `deletePadOnFinish`; an abandoned or failed task is a cleanup question.
* **Suspicious legacy behavior.** (a) Map-origin creation then `setPosATL`
  (see M4). (b) The product probes for a pre-existing helipad within **20 m**
  while the engine, per Hardrock, may snap to one much further away — so a
  mission-placed pad outside the probe radius could capture the landing without
  the product knowing. (c) A pad the product created is a world object other
  systems can see; nothing scopes it.
* **Characterization questions.**
  1. One-variable A/B on the same corridor and destination: hidden pad +
     `land "LAND"` versus `landAt` at an arbitrary position. Compare touchdown
     position error, time to settle, and whether the aircraft holds.
  2. Does the engine prefer a pre-existing helipad outside the product's 20 m
     probe over the freshly placed one? Place a decoy at 100 m and observe.
  3. Does `landAt` `waitTime` plus `getUnitState` provide a bounded, engine-owned
     "arrived and holding" oracle that is independent of the product's own state?
  4. What happens to a pad whose task fails or is cancelled between creation and
     `deletePadOnFinish`?

### V2. Rotary CAS target acquisition — sensor and `reveal` dependence

Inventory: **REVIEWED / NEEDS EXPERIMENTATION.**

* **Implementation surface.**
  `functions/task_cas/fn_airAutoEngage.sqf:304-…` (`YSF_AAE_collectSensorEnemies`,
  built on `getSensorTargets`) and `:493-496`
  (`_fireUnit reveal [_targetObj, 4]; _fireUnit reveal [_fireTarget, 4];
  _fireUnit doTarget _fireTarget;`).
* **BIKI** (`getSensorTargets`, Arma 3 2.06, **`arg = local`**). Documented
  return shape is `[[target, type, relationship, sensor], …]` where element 1 is
  a **String** type (`"unknown"`, `"footmobile"`, `"air"`, `"ground"`,
  `"laserTarget"`, `"irTarget"`, `"radarTarget"`), element 2 is a **String**
  relationship (`"friendly"`, `"enemy"`, `"destroyed"`, `"unknown"`), element 3
  is an array of sensor strings. See-also lists `getSensorThreats`,
  `listVehicleSensors`, `listRemoteTargets`.
* **CODE / suspicious.** The product's parser reads element 0 as the object
  (correct), then falls back to element 1 if element 0 was not an object — but
  element 1 is documented as a String, so that fallback can never bind an
  object. It also handles `_rel isEqualType 0` (a Number relationship), a shape
  the documented contract never returns. Both branches look like defensive code
  written against an unknown or historical return shape; neither is reachable
  under the documented contract. Note that the product also promotes `"unknown"`
  contacts to enemy when `getFriend < 0.6`, which is product policy layered on
  top of an engine classification.
* **BIKI** (`reveal`, rev 369307): sets the knowledge value to the highest level
  any unit of the revealing side already has, or 1 if the side has no knowledge;
  **"The knowledge level can only be increased by this command, not decreased.
  Use `forgetTarget` first"**.
* **BIKI** (`knowsAbout`, rev 347557): "AI knowledge cannot check beyond current
  `viewDistance` and it resets to zero as soon as the target's distance is over
  it… Losing sight of a target for more than 120 seconds resets its `knowsAbout`
  to zero as well."
* **COMMUNITY** (Bdfy): "`reveal` command sets `knowsAbout` to 1, but planes
  still won't fire at soldiers on the ground." The reported workaround is a
  nearby spotter unit that raises knowledge to 2.5–4.
* **COMMUNITY** (Lou Montana, arma3 1.82; Helling3r, arma2oa 1.62): tabulated
  detection distances and values; both note considerable variation with weather
  and time of day.
* **COMMUNITY** (ComradeCheekiBreeki, ≥2.04): all sides appear to know about
  *props* perfectly (`knowsAbout` 4) within max view distance, after a ~0.5 s
  post-start delay.
* **INFERENCE.** `reveal [_, 4]` requests the maximum, but the documented
  semantics say the resulting value is bounded by what the side already knows.
  Combined with Bdfy's report, "we revealed it" is not evidence that the aircraft
  will engage it, and the product's `doTarget` may be doing the real work.
* **INFERENCE.** `viewDistance` on an autonomous dedicated-server run is a run
  variable that directly bounds AI knowledge. Any CAS experiment that does not
  pin and record `viewDistance` is measuring the run, not the feature.
* **Native alternatives.** `listRemoteTargets` (datalink-shared contacts) and
  `getSensorThreats` are documented siblings that the product does not use; if
  the product intent is "the aircraft engages what the *side* can see", datalink
  sharing may be closer to that intent than a per-aircraft sensor scrape plus a
  knowledge injection.
* **Characterization questions.**
  1. With `viewDistance` pinned, does removing the `reveal` calls change whether
     the exact fire event occurs, holding `doTarget` fixed? And vice versa?
  2. Does `getSensorTargets` ever return the shapes the parser defends against?
     If not, the dead branches are legacy and should be recorded as such rather
     than preserved as if load-bearing.
  3. Is `knowsAbout` decay (120 s / beyond view distance) reachable inside a CAS
     on-station timer, and does it cause re-acquisition churn?

### V3. Tablet shell — page registry and unrealized pages

Inventory: tabbed navigation is **PARTIALLY COVERED** ("Visible artillery
navigation is direct, not every page"). No canonical review covers the shell
itself; [`../vigil-tablet-access-review.md`](../vigil-tablet-access-review.md)
covers items, access rule, keybind, open/close.

* **Implementation surface.** `ui/idc.hpp`, `ui/tablet_base.hpp`,
  `ui/pages/page_assets.hpp`, `functions/tablet/fn_ui_utils.sqf`
  (`YSF_UI_RegisterPage`, `YSF_UI_SetPage`, `YSF_UI_Nav`),
  `functions/global/fn_init.sqf`.
* **CODE.** Exactly **one** page is registered:
  `["assets", IDC_PAGE_ASSETS] call YSF_UI_RegisterPage`. The `home` and `admin`
  registrations are commented out in `fn_init.sqf:5-6`. `config.cpp`'s dialog
  includes only `tablet_base.hpp` and `pages/page_assets.hpp`;
  `ui/pages/page_home.hpp` and `ui/pages/page_admin.hpp` are not included, and
  `page_admin.hpp` is **entirely commented out** — it has no live content at all.
* **CODE / suspicious.** The dialog's `onLoad` calls `call YSF_UI_Nav`, but
  `YSF_UI_Nav` declares `params ["_mode","_key"]` and `onLoad` supplies
  `_this = [display]`. `_mode` therefore binds the **Display**, the `switch`
  matches neither `"build"` nor `"set"`, and the whole navigation bootstrap
  works only because it lands in the `default` branch, which happens to do
  `build` then `set "assets"`. That is a working outcome produced by a type
  mismatch rather than by an intended call.
* **CODE / suspicious.** `YSF_UI_OpenTablet` returns without acting when a
  display already exists, so the keybind is open-only, never a toggle.
* **CODE.** `YSF_UI_Nav "build"` iterates `keys _reg` — hash-map key order, not
  a declared tab order. With one page this is unobservable; with three it is a
  contract question.
* **Orphan scaffolding (also recorded in the audit).** `IDC_PAGE_MAP` (88110)
  and its whole child family `IDC_MAP_COORD_BTN`, `IDC_MAP_TAB_TXP`,
  `IDC_MAP_TAB_ARTY`, `IDC_MAP_TAB_CAS`, `IDC_MAP_TAB_RECON` have **no page
  file and no reference anywhere**. The same is true of `IDC_ASSETS_TAB_TXP`,
  `IDC_ASSETS_TAB_ARTY`, `IDC_ASSETS_TAB_CAS`, `IDC_ASSETS_TAB_RECON`, the
  `IDC_YSF_VP_*` group (five controls), `IDC_TABLET_TITLE`, and
  `IDC_TABLET_BTN_CLOSE`. This is the fossil of a different navigation design —
  a dedicated map page with per-task tabs — that the shipped build reaches
  through the assets page instead.
* **Locality.** Entirely `uiNamespace`/display-local; no authority surface.
* **Characterization questions.** Mostly none — this is a product-decision
  surface, not an engine one. The one genuine engine question is whether
  `ctrlShow false` on every registered page plus `ctrlShow true` on one is
  sufficient isolation, or whether hidden controls still receive input/tooltips.

### V4. Coordinate, waypoint and AI-preset helpers

Inventory: **PARTIALLY COVERED** through artillery/flight outcomes; "helpers are
replaceable". No canonical review.

* **Implementation surface.** `functions/global/fn_core.sqf` —
  `YOSHI_parseGrid`, `YOSHI_pos_to_grid`, `YOSHI_pad4`, `YOSHI_getNearestHelipad`
  (:254), `YOSHI_setWaypoint` (:275, **orphan**), `YOSHI_isHeliPad` (:249,
  **orphan**), `YSF_isVehicle` (:541, **orphan**), `YOSHI_progressColor` (:168,
  **orphan**), `YSF_fnc_setVehicleLandMode` (:412),
  `YSF_fnc_setVehicleEngineState` (:423), plus the safe/transit AI presets.
* **Mechanics.** Grid ↔ world conversion, `nearestObjects`, waypoint commands,
  `land`, `engineOn`, AI behaviour/combat-mode presets.
* **INFERENCE.** Grid formatting is a pure function and belongs in static/unit
  coverage, not gameplay coverage; the artillery and transport scenarios that
  currently exercise it incidentally cannot distinguish a formatting error from
  a targeting error, because both surface as "rounds landed elsewhere".
* **Suspicious legacy.** Four orphan helpers in one file, including a waypoint
  setter, suggests an earlier waypoint-driven tasking design superseded by the
  governor.
* **Characterization questions.** None engine-level. The open question is a
  product one: is grid parse/format a promised integrator API or an internal
  detail? The presence of `YOSHI_pad4` in Vigil and `YFU_pad4`/`YFU_posToGrid`
  in Field Utilities (duplicated, independently maintained) is evidence that it
  is being treated as internal by each mod separately.

### V5. Artillery and VLS — covered, but with two unrecorded engine boundaries

Inventory: **COVERED** by `vigil-artillery` and `vigil-markers`; VLS handshake is
**REVIEWED / CHARACTERIZED**. No durable `*-review.md` exists for either (see
the audit).

* **BIKI** (`doArtilleryFire`, rev 377401): "Orders an artillery unit to fire a
  burst on the given position (silently)"; target is **PositionAGL**.
* **COMMUNITY** (ansin11): "This command can not fire bursts consisting of more
  rounds than the given magazine type holds, even if there are several magazines
  of the same type available. The fire mission issued by this command ends once
  the artillery unit has to reload." Worked example: a Mk6 with four
  `8Rnd_82mm_Mo_shells` magazines fires **8**, not 10, when asked for 10.
* **COMMUNITY** (Leopard20): use `unitReady` to detect completion.
* **BIKI** (`getArtilleryETA`, rev 377528): returns **-1** if the target cannot
  be hit; target is **PositionAGLS**.
* **COMMUNITY** (Killzone_Kid): "To avoid wrong ETA readings, position of the
  target should only be obtained via `position` or `getPos`."
* **INFERENCE / bounded gap.** The accepted round-count contract is proven with
  a fixture using `8Rnd_82mm_Mo_shells`. If ansin11's report holds, a request
  for more rounds than one magazine holds is silently truncated by the engine,
  and the product's count contract has an undeclared upper bound equal to the
  magazine size. The current coverage cannot distinguish "the product fired what
  was asked" from "the product asked for more and the engine capped it" unless
  a request above magazine size is exercised.
* **INFERENCE.** Position-type discipline differs between the two commands
  (AGL for fire, AGLS for ETA). Any helper that feeds both from one stored value
  is relying on those being interchangeable at the tested altitudes.
* **Characterization questions.**
  1. Request `magazineSize + N` rounds from a platform holding several
     magazines. Count physical rounds. This is a cheap, decisive A/B.
  2. Does `getArtilleryETA` return -1 for the product's own out-of-range refusal
     cases, i.e. is the product's range check redundant with an engine one?

### V6. Reconnaissance

Inventory: **REVIEWED / DEFERRED**; product decisions recorded in
[`../vigil-fixed-wing-recon-review.md`](../vigil-fixed-wing-recon-review.md).

* **CODE.** `functions/task_recon/fn_recon.sqf` is 49 lines of pure client-local
  form state (grid/alt/radius) plus a control sync;
  `functions/task_recon/fn_recon_task.sqf` is **0 bytes** yet is registered
  `postInit = 1` in `config.cpp`. `IDC_TASK_G_RECON` and the three recon control
  IDCs are referenced; `IDC_ASSETS_TAB_RECON` and `IDC_MAP_TAB_RECON` are not.
  `YSF_FW_ROLE_RECON` exists in the fixed-wing role bits.
* **INFERENCE.** Nothing here needs an engine experiment. Recording it in this
  document is only to note that a *zero-byte* file is registered as a postInit
  function — worth confirming that CfgFunctions tolerates that silently rather
  than logging an error each mission start, which would be a cheap observation
  during any unrelated run.

### V7. Fixed-wing IR visualization and 3CB Hellfire mapping

Inventory: IR beam rendering/color/compatibility **PARTIALLY COVERED**;
3CB Hellfire mapping **REVIEWED / NEEDS EXPERIMENTATION** ("no compatible
installed pylon row for A/B").

* **Implementation surface.** `functions/client/fn_irLaserViz.sqf` (151 lines,
  `preInit`, with an orphan `YSF_irLaserViz_testReset`);
  `YSF_AAE_swap3CBHellfireToScalpel` and `YSF_AAE_swapLaserBombCoreToBomb04` in
  `fn_airAutoEngage.sqf`; `YSF_AAE_laserClassBySide` / `YSF_fwLaserClassBySide`.
* **INFERENCE.** The 3CB item is blocked on a *content dependency*, not on an
  engine unknown: no installed pylon row qualifies. That makes it structurally
  the same class of blocker as client-B — an environment dependency. It should
  not be repeatedly re-selected as an unblocked candidate.
* **Characterization question.** The one thing that can be done without 3CB is
  to prove the *mapping function* in isolation as a static/unit check over a
  synthetic class table, keeping the physical claim unmade. That is a different
  test type (specification vs. characterization) and should be labelled as such.

### V8. Task governor — mechanism notes only

The governor is already reviewed at **REWRITE BEFORE PERMANENT COVERAGE**
([`../vigil-task-governor-review.md`](../vigil-task-governor-review.md)), which
this document does not restate. Two mechanism observations are added:

* **CODE.** `YSF_governorStop` (`fn_governor.sqf:296`) and `YSF_taskGet` (`:88`)
  have **no callers anywhere**. The dispatcher can be started but never stopped
  through a shipped path; only `CBA_fnc_removePerFrameHandler` via that orphan
  would do it. Any rewrite needs a reachable stop, and any scenario that starts
  the governor currently has no product-provided way to leave global state as it
  found it.
* **CODE.** `YSF_sigVeh` builds a staleness signature from
  `round`ed world position, `speed`, waypoint count and `round`ed direction.
  A helicopter holding a stable hover produces a constant signature, so
  "no progress" and "correctly holding station" are indistinguishable to the
  watchdog. The retry path is unreached today, which is why this has never
  surfaced.

---

## Part 2 — Advanced Systems

### A1. APS anti-drone

Inventory: **REVIEWED / DEFERRED**
([`../advanced-systems-aps-anti-drone-review.md`](../advanced-systems-aps-anti-drone-review.md)).
The review already records undefined threat/side/operator policy, split resource
transactions, destructive mutation without acknowledgement, unscoped handler
removal, and caller-trusting endpoints. Three additions:

* **CODE.** `fn_aps.sqf:842-854` removes **thirteen** event-handler types from a
  third-party UAV, including the legacy misspelled `"Dammaged"`. Per M2, an
  object EH runs on the machine that added it, and `removeAllEventHandlers` is
  correspondingly machine-scoped.
* **INFERENCE / cross-mod, in-suite.** Field Utilities installs its own `Engine`
  handler on every configured small UAV and its IED `Killed` handler on the same
  object, both **on the UAV's owner** (`fn_fpv.sqf`). The APS anti-drone loop
  also runs on the protected vehicle's owner. When both are the same machine —
  the ordinary single-client and dedicated-server-owned cases — an anti-drone
  engagement **destroys Field Utilities' own FPV handlers** before killing the
  drone. The existing review names "missions, other mods and evidence
  observers"; the concrete first casualty is a sibling Pontifex mod. This makes
  the anti-drone/FPV pair a composition question, not only an anti-drone one.
* **INFERENCE.** The `getMass _x < 1000` eligibility filter inherits M1 wholesale.
* **Characterization questions.**
  1. Does `removeAllEventHandlers` on machine A remove a handler added on
     machine B? (Expected no, per M2 — but the product's safety argument depends
     on the answer, so it should be measured, not assumed.)
  2. Given an FPV UAV with an attached IED, does an anti-drone engagement
     suppress the IED death effects entirely? What does a defender observe?
  3. Is `setDamage [1, false]` after handler stripping distinguishable, by any
     independent oracle, from an ordinary kill?

### A2. Counter Battery Radar — concurrency, markers, confirmed origin

Inventory: multi-launcher/multi-cluster arbitration **REVIEWED / REFINE BEFORE
PERMANENT COVERAGE**; marker sharing policy and confirmed-origin persistence
**REVIEWED / DEFERRED**; warning coverage **DEFERRED**. See
[`../advanced-systems-cbr-concurrency-review.md`](../advanced-systems-cbr-concurrency-review.md).

* **CODE / dead constants.** `YOSHI_CB_MEMBER_TTL = 2.0` (`fn_cbr.sqf:13`) is
  defined and **never read**. `YOSHI_CB_nextUid` (`:18`, reset at `:369`) is
  assigned twice and **never read**; shell UIDs come from
  `YOSHI_CB_LOCAL_UID_COUNTER` instead. Two abandoned mechanisms — a member
  time-to-live and a UID source — are still sitting in the file where a future
  reader may take them for live tuning parameters.
* **CODE.** Origin markers are created with counter-derived names
  (`fn_originHandler.sqf:74`, `:122`) — see M6 for the silent-failure mode when
  the counter restarts.
* **BIKI** (`createMarker`): markers are created for every connected player and
  all JIP players. The deferred "marker sharing policy" therefore has an engine
  default — global — and the side-filtered radio warning is the exception, not
  the rule.
* **INFERENCE.** `YOSHI_fnc_originOnShot` halves the search radius per shot with
  a floor, and promotes to a permanent `mil_triangle` marker at
  `YOSHI_ORIGIN_CONFIRM_R`. The promotion deletes the ellipse and creates a new
  marker under a **new** counter index, so a confirmed origin is a different
  marker identity from the search circle that produced it. Any future contract
  about "the origin marker" must say which of the two it means.
* **Characterization questions.**
  1. Two launchers firing on the same cluster from different owners: does
     cluster assignment depend on arrival order? (The review already frames
     this; the mechanism to instrument is `YOSHI_CB_addToCluster` plus the fixed
     first-nearest-center selection.)
  2. Does a client-owned launcher's `ArtilleryShellFired` reach the server at
     all? (See A3 — the answer is shared between CBR and Iron Dome.)

### A3. Iron Dome — client-owned artillery

Inventory: **REVIEWED / DEFERRED** ("current server handler deliberately rejects
non-server-local shells; no owner-routing product policy is chosen").

* **CODE.** `functions/iron_dome/fn_ironDome.sqf:785-788` installs
  `addMissionEventHandler ["ArtilleryShellFired", …]` on the server;
  `:743-753` then rejects the shell with a log if `!local _shell`.
* **BIKI** (Mission Event Handlers page, accepted corpus): `ArtilleryShellFired`
  is introduced in Arma 3 **2.18** and is described as a **"Global Mission Event
  Handler. Executes each time a vehicle classified as artillery (has an
  artillery computer) fires a shell."** Its arguments include the `_shell`
  object itself.
* **INFERENCE — the important one.** If "Global Mission Event Handler" means the
  event reaches every machine, then the server **does already observe** shells
  fired by client-owned artillery; what it lacks is the ability to mutate a
  remote projectile. The current guard therefore conflates two different things:
  *detection*, which may already work everywhere, and *interception*, which is
  locality-bound. A product policy could keep server-side detection and tasking
  while routing only the terminal mutation to the shell's owner — which is
  precisely the shape CORDIS already provides. This reframes the deferred item
  from "no policy chosen" to "a specific, testable split is available".
* **INFERENCE.** The same reframing applies to CBR's owner-local launch/track
  endpoints (A2), which currently accept caller-authored telemetry rather than
  deriving it from a globally observed engine event.
* **Characterization questions.**
  1. Fire from a client-owned artillery vehicle. Does the **server's**
     `ArtilleryShellFired` handler fire? With what `_shell`, and what does
     `local _shell` / `owner _shell` report there?
  2. If it fires, can the server derive the same track data it currently accepts
     from the owner, removing the unbound-telemetry surface entirely?
  3. What is the minimum set of operations that genuinely require shell
     locality — velocity change, deletion, `setDamage`, or none of them?

### A4. Iron Dome range setting and launch audio; APS presentation

Inventory: Iron Dome range/audio **PARTIALLY REVIEWED**; APS beam/particle and
voice **REVIEWED / DEFERRED**
([`../advanced-systems-aps-presentation-review.md`](../advanced-systems-aps-presentation-review.md)).

* **CODE.** All 26 APS `CfgSounds` classes and both `YAS_OphanimReload*` classes
  have at least one SQF reference — there is no dead audio content in AdvSys.
  The number-to-voice tokens (`one`…`one_hundred`, `comma`, `period`) are a
  complete spoken-number vocabulary.
* **INFERENCE.** M5's "one sound at a time" bound is the sharpest constraint on
  the deferred audience/overlap policy: a spoken percentage readout occupies the
  vehicle's single sound slot for its whole duration, during which no engagement
  cue can play on that vehicle. `YOSHI_fnc_apsGetSoundDuration` exists, which
  suggests the implementation already reasons about this.
* **Characterization question.** Using `allMissionObjects "#soundonvehicle"` as a
  data oracle (M5), is a second `say3D` on the same vehicle dropped, queued, or
  does it replace the first? This is answerable under `-noSound`.

---

## Part 3 — Field Utilities

### F1. Object handling and nearby supply loading

Inventory: **REVIEWED / REFINE BEFORE COVERAGE**; named as the next recommended
unblocked feature in
[`../pontifex-progress-estimate-2026-08-23.md`](../pontifex-progress-estimate-2026-08-23.md).
The existing review
([`../field-utilities-object-handling-review.md`](../field-utilities-object-handling-review.md))
already sets out the two-path split, the authority gap, and the first
experiment. It records the required locality of `setVehicleCargo`, `attachTo`
and contact EHs as **uncharacterized**. This section supplies the Sacred Texts
for exactly those three.

* **`setVehicleCargo`** — **BIKI** (rev 349523, Arma 3 [1.62.0, *)): "Load cargo
  vehicle inside vehicle if possible, returns bool based on whether the vehicle
  was able to be loaded. Can also be used to unload a specific loaded vehicle or
  all loaded vehicles." Return is "whether or not operation was a success".
  **COMMUNITY** (ImperialAlex): `objNull setVehicleCargo _cargoVehicle` unloads
  a specific vehicle, `_transportVehicle setVehicleCargo objNull` unloads all,
  and "the unloaded vehicles will be paradropped if the altitude is high enough."
  The retrieved documentation does **not** state a locality requirement — that
  absence is itself the finding: it means the answer must come from an
  experiment, not from the wiki.
* **`canVehicleCargo`** — **BIKI** (rev 336373): "Returns bool array if it is
  possible to load cargo inside vehicle and if possible to load cargo into empty
  vehicle." The product requires **both** booleans true, i.e. it requires the
  carrier to be loadable *and* loadable-when-empty; whether that is the intended
  eligibility rule or an over-strict reading is a product question.
* **`attachTo`** — **BIKI** (rev 378853): all direction commands on an attached
  object are relative to the reference object's model space; with no offset the
  current offset is preserved.
  **COMMUNITY (Demellion), the most consequential note found:** "Using `attachTo`
  with objects that have ragdoll physics (such as **ammo boxes, containers**,
  etc.) may cause unexpected behaviour… if the attached object intersect origin
  object, origin object may gain some **enormous collision properties**… Vehicles
  may start flipping with no mass calculation (ie tank might fly), player object
  might gain infinite Z-vector velocity…"
  **COMMUNITY** (ondrejkuzel): attaching does not update AI path accessibility.
  **COMMUNITY** (TeaCup): some objects cannot meaningfully be attached to.
  **COMMUNITY** (ffur2007slx2_5): re-attaching to a *different* object resets
  `setVectorDirAndUp` to default.
* **`lineIntersectsSurfaces`** — **BIKI** (rev 377700): "if `begPosASL` is under
  the ground and `endPosASL` is above it, the command will only return
  intersection with the ground, this is an engine limitation and none of the
  `intersectXXX` commands will work when initiated from under the ground"; "only
  a single LOD is checked"; hardcoded max distance 5000 m; no sea-surface
  intersection.
* **INFERENCE / suspicious — the headline for this feature.** `YOSHI_attachToBelow`
  attaches a `ReammoBox_F` (a ragdoll-physics container, exactly Demellion's
  example class) to the first non-`Static` object below it, which in the intended
  use case is a **vehicle**. If Demellion's report still holds, the shipped
  automatic contact-attachment path is a candidate cause of the classic
  "tank suddenly flies" symptom, and a scenario that merely asserts
  "box ended up on the truck" would pass while the truck is being launched. This
  is a hypothesis, not a finding; it is recorded because it changes what a first
  experiment should observe (the **carrier's** velocity and orientation, not just
  the box's attachment).
* **INFERENCE.** The `lineIntersectsSurfaces` under-ground limitation ties this
  feature to F3: a Fabricator crate staged below the surface cannot raycast, so
  contact attachment is inoperative for exactly the objects the Fabricator
  produces during staging.
* **CODE / suspicious.** `[_object, -1] call ace_cargo_fnc_setSize` is applied to
  every `ReammoBox_F` at server init and on every `EntityCreated`. The feature
  therefore *disables* ACE cargo for ammo boxes suite-wide and substitutes
  vanilla vehicle-in-vehicle transport. That is a significant, silent,
  suite-wide policy affecting any mission that expected ACE cargo to work — and
  it is applied unconditionally, with no setting.
* **CODE / suspicious.** `YFU_initObjectHandling` is asymmetric: at init it adds
  contact handling only to `ReammoBox_F` and dragging only to `Land_Pallet_F`,
  while the `EntityCreated` path adds contact handling to `ReammoBox_F`,
  dragging to `Land_Pallet_F`, and UAV configuration. Pallets never get contact
  handling and boxes never get dragging, in either path.
* **CODE.** The load action's second code block — the child condition — is a
  literal `true`. Eligibility is evaluated once, when the parent action builds
  its children.
* **Characterization questions.**
  1. Attach an ammo box to a light vehicle under contact and sample the
     **carrier's** velocity, `vectorUp` and position over the following seconds
     against an unattached control. Does Demellion's report reproduce?
  2. Does `setVehicleCargo` succeed when called on a machine where neither the
     carrier nor the cargo is local? Record the boolean return, then verify
     `vehicleCargoEnabled`/cargo membership independently on server and client.
  3. Does the ACE `setSize -1` policy prevent all ACE cargo loading of ammo
     boxes, and is that the intended product statement?
  4. From under the ground, does `YOSHI_attachToBelow` return `false` cleanly or
     misbehave?

### F2. FPV / UAV field modifications

Inventory: small-UAV profile **NEEDS EXPERIMENTATION**; IED and mortar/grenade
payloads **REFINE BEFORE PERMANENT COVERAGE**; click/shuffle **DEFERRED**.
See [`../field-utilities-fpv-review.md`](../field-utilities-fpv-review.md).
The review already covers the authority and underflow findings. Additions:

* **COMMUNITY (Pixinger), on `attachTo` — directly contradicts the shipped IED
  path:** "If you attach an explosive charge to an object (e.g. ammobox), the
  charge will **not detonate** when you simply set the damage to 1. **You must
  detach it before.**" The quoted example detaches, then sets damage.
* **CODE.** `fn_fpv.sqf:48-49` attaches a `ModuleExplosive_SatchelCharge_F` to
  the UAV. `fn_fpv.sqf:57` — inside the `Killed` handler — does
  `{ _x setDamage 1; } forEach (attachedObjects _unit)` **without detaching**.
* **INFERENCE / suspicious.** If Pixinger's report holds, the attached satchel
  never detonates, and everything a player observes comes from the
  `"Bo_Mk82"` (low branch) or the 29-`ModuleExplosive_Claymore_F` ring (high
  branch) plus `"HelicopterExploBig"`. The feature would look correct while its
  named primary mechanism is inert. A future scenario asserting only "a large
  explosion occurred at the UAV" cannot tell the two apart.
* **COMMUNITY (General Barron), on `setVectorDirAndUp`:** "The object's
  `vectorDir` can only control its **pitch**, while its `vectorUp` can only
  control its **bank**. To set an object's yaw (direction), use the `setDir`
  command… any `vectorDir` that would adjust yaw is ignored."
  **COMMUNITY** (ffur2007slx2_5): `setDir` overwrites `setVectorDirAndUp`, and
  `setVectorDirAndUp` also affects `setVelocity`.
* **CODE.** `fn_fpv.sqf:66` sets each claymore's orientation with
  `_ex setVectorDirAndUp [_x, [0,0,1]]`, where `_x` iterates the 27 corners of a
  3×3×3 direction cube plus `[0,1,10]` and `[0,-1,-10]`.
* **INFERENCE / suspicious.** Under General Barron's reading, the yaw component
  of each `_x` is ignored, so the horizontal fan of a directional-mine ring is
  not actually being aimed; only pitch varies, and `[0,0,±1]` entries are
  degenerate against an up vector of `[0,0,1]`. The visual result may still be a
  convincing airburst, which is exactly why it would never be questioned.
* **CODE / M3.** `YFU_fnc_uavDropGrenade` (`:146`) uses `createVehicle` main
  syntax — see M3 for why the grenade may never fall.
* **CODE / M4.** `YFU_fnc_uavReleaseMortar` (`:130-132`) creates
  `Sh_82mm_AMOS` at the map origin, attaches it to the UAV, and detaches it in
  the same call. The assumption that `detach` leaves the shell at the attached
  world position with usable velocity is unstated; `detach`'s documentation
  (rev 369227) says only "Detaches previously attached with `attachTo` object"
  and specifies nothing about velocity.
* **Characterization questions.**
  1. Attached versus detached-then-damaged satchel, same UAV, same altitude:
     does the attached charge produce any explosion of its own?
  2. Does the claymore ring produce a measurably directional damage pattern, or
     is it isotropic? Sample damage on a ring of witnesses.
  3. Does a released `Sh_82mm_AMOS` inherit the UAV's velocity on `detach`, and
     does it arm and detonate on impact, or land inert?
  4. Does `"GrenadeHand"` created by main syntax appear at the drone's altitude
     or at ground level? (M3.)

### F3. Fabricator remaining experiments

Inventory: delivery mass cap **OPEN DEFECT**; placement suitability
**NEEDS EXPERIMENTATION**; staging depths **NEEDS EXPERIMENTATION**;
client-b discard **NOT YET PROVEN**.

* **Mass cap.** See M1 — the `> 0` predicate is satisfied by the observed
  `1e-12`, so the settle wait is a no-op against the exact failure mode it was
  added for. The recorded caveat that all six runs were over water connects to
  M4.
* **Placement suitability.** **BIKI** (`surfaceIsWater`, rev 377565): "Returns
  whether there is water at given position. In Arma 3, it also detects pond
  objects, **but only if they are loaded in memory (normally only true if the
  objects are within the object view distance)**." Position Z is ignored.
  * **INFERENCE.** On a dedicated server with a low object view distance,
    `surfaceIsWater` is not a dependable pond oracle. If a suitability contract
    is ever written against it, it would encode a view-distance-dependent answer
    as a product rule. A terrain-gradient plus `lineIntersectsSurfaces` probe is
    the more likely native basis, but see F1 for the under-ground limitation.
* **Staging depths.** **BIKI** (`lineIntersectsSurfaces`): nothing intersects
  when initiated from under the ground. Any settle/placement logic that probes
  downward from a staged position below the surface returns empty, and an empty
  result is currently treated as "no obstruction".
* **Characterization questions.**
  1. Same class, same terrain, created at destination (M4) versus at origin —
     compare `getMass` over ten seconds.
  2. `surfaceIsWater` over a known pond at the server's actual object view
     distance, versus at a forced high view distance.
  3. Does the staging depth used in production sit above or below the surface
     for the terrain under test, and what does a downward probe return there?

### F4. Bridge Builder — direct chain extension, interruption, resources

Inventory: direct chain-extension actions **Implemented-looking; DEFERRED**
("helpers exist but action attachment is empty"); build interruption/destruction
and resources are explicitly not proven.

* **CODE — more than the inventory records.** There are **two** orphaned
  registration paths, not one:
  * `YFU_bridge_attachActionsToObject` (`fn_bridgeUtils.sqf:1721`) is the empty
    stub the inventory describes — its entire body is
    `if (isNull _bridgeObject) exitWith {};`, so it does nothing even for a
    valid object.
  * `YFU_bridge_attachActionsToBuilderBox` (`:1727`) is **fully implemented**:
    it initialises the plan renderer, ensures box defaults, builds a complete
    "Open Bridge Builder" action with id `YFU_BoxBridgeOpenUI`, and registers it
    per-object through `YOSHI_addActionToObjectForEveryClient`. It duplicates,
    on a per-object basis, what the shipped class-based `YFU_initBridgeActions`
    (`:1758`) registers as `YFU_BoxBridgeOpenUI_Class`.
  Neither has a caller. Twelve `YFU_bridge_*` globals have no product caller
  at all (see the audit) — and one of them, `YFU_bridge_beginPlanPreview`, is
  invoked **only** from the permanent scenario
  (`source/field-utilities/tests/tribunal/bridge_builder.py:344`). A product
  function whose sole caller is its own test is worth naming explicitly: the
  canonical program requires a contract to be driven from its real entry point,
  and this one currently has none.
* **INFERENCE / suspicious.** If `YFU_bridge_attachActionsToBuilderBox` were
  ever wired up alongside the shipped class registration, a box would carry
  **two** Open Bridge Builder entries with different ids. The accepted
  ACE-composition contract asserts exact singleton roots; this is the specific
  latent way that invariant could be broken, which makes it worth recording
  rather than deleting.
* **Characterization questions.** None engine-level. The product question is
  whether direct extension is intended at all; the composition question is
  whether the accepted singleton-root assertion would catch a double
  registration if it happened.

### F5. Map helpers, ID markers, and airdrop direction/ETA

Inventory: ID/location marker helpers **REVIEWED / DEFERRED**; airdrop
direction/ETA **REVIEWED / NEEDS PRODUCT DECISION AND EXPERIMENTATION**. See
[`../field-utilities-map-helpers-review.md`](../field-utilities-map-helpers-review.md).

* **CODE / suspicious — divergent duplicates.** `YOSHI_addMarker`
  (`fn_initMapTools.sqf:1-17`) and `YAS_addMarker`
  (`AdvSys/functions/global/fn_core.sqf:7-…`) are near-identical helpers in two
  different mods, both orphaned, both using the `_USER_DEFINED` prefix (M6).
  They have diverged: the Field Utilities copy assigns `_markerName` and
  `_marker` **without `private`**, leaking two mission-namespace globals on every
  call; the Advanced Systems copy declares both `private`. One is a fixed copy
  of the other and the fix was not propagated.
* **CODE.** `YOSHI_toggleDisplayLocationDataOnMap` starts a `spawn`ed loop that
  deletes and recreates the marker **every second**, and stops it with
  `terminate`.
  **BIKI** (`terminate`, rev 376945): "The given script will not terminate
  immediately upon `terminate` command execution, it will do so the next time
  the script is processed by the scheduler." So there is a window in which a
  terminated loop can still recreate a marker that the toggle just deleted.
* **CODE.** Airdrop announcement (`fn_assets.sqf:391-416`):
  bearing is `_targetATL getDir _assetATL` — the direction **from the target to
  the aircraft** — and ETA is
  `[_assetATL select 2, _targetATL select 2] call YOSHI_GET_FALL_TIME`, a vacuum
  free-fall `sqrt(2Δh/g)` evaluated at acceptance.
* **CODE / suspicious.** `YOSHI_GET_FALL_TIME` (`fn_initMapTools.sqf`) computes
  `sqrt((2 * (_initialHeight - _finalHeight)) / 9.81)`. If the aircraft is lower
  than the target, the argument is negative and the result is **NaN**, which
  would be formatted straight into the announcement string.
* **CODE / suspicious.** The speaker fallback chain ends with
  `if (isNull _speaker) then { _speaker = player; }`. On a dedicated server
  `player` is null, so the final fallback cannot rescue the null case.
* **Characterization questions.**
  1. Does `terminate` plus an immediate `deleteMarker` race the loop's next
     recreate? (Trivially observable; the answer likely follows directly from
     the quoted scheduler note.)
  2. What does the announcement render when the aircraft is below the target
     altitude?

### F6. Helicopter sling helper

Inventory: **REVIEWED / DEFERRED** — compiled orphan, destructive all-rope stow,
non-atomic creation
([`../field-utilities-helicopter-sling-review.md`](../field-utilities-helicopter-sling-review.md)).

* **CODE.** `YOSHI_attachHeliLiftRopes` (`fn_initRopes.sqf:120`) has no caller,
  and `YOSHI_getStableLiftCorners` (`fn_initGeometry.sqf:267`) is referenced
  only from inside it (`fn_initRopes.sqf:127`) — an orphan pair, not one orphan. The shipped towing path uses `ropeCreate` with the custom
  `"Spring1xRope"` class (`fn_towingServer.sqf:123`, `fn_initRopes.sqf:140-148`).
* **CODE / audit.** `config.cpp` declares four custom rope classes —
  `Spring100xRope`, `Spring50xRope`, `Spring10xRope`, `Spring1xRope` — and only
  `Spring1xRope` is referenced anywhere. The other three are dead config,
  evidently a stiffness-tuning ladder left behind after the value was chosen.
* **INFERENCE.** The three unused classes are the cheapest available A/B
  material for any future rope-behavior experiment: they already exist, differ
  in exactly one documented parameter (`springFactor`), and need no new content.

---

## Part 4 — Cross-mod

### X1. Shared UI reuse without Vigil, and nested display lifecycle

Inventory §5.3 states plainly: "Nested lifecycle, styling, and use without Vigil
are **not reviewed**." This is the largest genuinely *unreviewed* surface found.

* **Implementation surface.** Field Utilities ships its own
  `ui/tablet_base.hpp`, `ui/defines.hpp`, `ui/idc.hpp`, `ui/constants.hpp` and
  its own copies of the three `ui_tablet_ysf_vigilterminal_*.paa` textures, plus
  `YFU_UI_RegisterPage` / `YFU_UI_SetPage` / `YFU_UI_SetCorrectTablet` mirroring
  the Vigil functions of the same shape. Two dialogs are declared:
  `YFU_FieldUtils_Dialog` and `YFU_BridgeBuilder_Dialog`.
* **CODE.** `CfgPatches` for `YFU_FieldUtils` requires `YCD_CORDIS`, CBA, ACE and
  ZEN — but **not** the Vigil addon. The skin is duplicated rather than
  depended on, so Field Utilities is installable without Vigil.
* **CODE.** `YFU_UI_SetCorrectTablet` selects a texture by the player's assigned
  `YSF_VigilTerminal_*` item — a **Vigil** item class. Without Vigil installed
  those classes do not exist, so the selection loop matches nothing.
* **INFERENCE.** Field Utilities is structurally independent of Vigil but
  cosmetically coupled to it through item class names. The uncovered question is
  what the Fabricator/Bridge dialogs look like and whether they function with
  Vigil absent — which is a real deployment configuration, since the mods ship
  as four separable PBOs.
* **INFERENCE / locality.** Vigil's tablet and the Fabricator dialog can both be
  open in one session (the accepted logistics path opens Field Utilities *from*
  Vigil). Each stores its display in its own `uiNamespace` key
  (`YSF_Tablet_Display`, `YFU_FieldUtils_Display`), and each `onUnload` clears
  only its own. Vigil's `onUnload` additionally calls `YSF_clearAllMarkers` and
  `playSound 'TurnOff'` — global side effects fired by closing the *outer*
  dialog, whose ordering relative to a nested close is undeclared.
* **Characterization questions.**
  1. With Vigil not loaded, do the Field Utilities dialogs open, render, and
     close correctly? Does `YFU_UI_SetCorrectTablet` leave an empty background?
  2. Opening Fabricator from Vigil and closing in each order: are both display
     variables cleared, are markers cleared exactly once, and is any control
     left showing?
  3. Is `createDialog` nesting or replacement the actual engine behavior here?

### X2. Replicated state and serialization lifecycle

Inventory §5.5: **PARTIALLY COVERED** by one-client replication scenarios; no
durable persistence exists; JIP/multi-client is **REVIEWED / DEFERRED —
ENVIRONMENT DEPENDENCY**
([`../multiplayer-client-n-jip-boundary-review.md`](../multiplayer-client-n-jip-boundary-review.md)).

* **INFERENCE.** The environment blocker (one authenticated Steam identity) is
  real and is not reconnaissance-solvable. What *is* available now is an audit
  of which public object/mission variables the suite writes with the broadcast
  flag, since every one of them is a JIP-visible surface whose retention policy
  is currently implicit. Building that list is a cheap, purely static piece of
  work that would make the eventual client-N review much shorter.
* **CODE.** Public setters observed while reading for this document include
  APS state (`YOSHI_APS_*`), FPV payload counts and the `Killed`-handler-added
  flag, whitelist/registry mirrors, Iron Dome engagement events, and the
  governor PFH id. The FPV handler-added flag (M2) is a concrete example of a
  public variable whose truth is machine-local.
* **Characterization question (deferred, environment-bound).** For each public
  variable: what should a joining client see, and for how long? That is a
  per-feature product decision, exactly as the boundary review records.

---

## What a future review should take from this

Ranked by how much a single controlled experiment would unblock:

1. **`landAt` versus hidden pad (V1).** A documented 2.20 native mechanism that
   may replace a bespoke workaround *and* its polling oracle, inside the
   declared `requiredVersion`. Cheapest high-value A/B available.
2. **`ArtilleryShellFired` reach (A3).** One observation reframes both the Iron
   Dome client-owned-threat deferral and CBR's unbound owner telemetry.
3. **`getMass` behavior (M1).** One characterization touches Fabricator's open
   defect, anti-drone eligibility, and the stabilizer force term.
4. **`attachTo` on ragdoll containers (F1).** Determines what a supply-loading
   experiment must observe, and may explain a symptom nobody has attributed yet.
5. **`createVehicle` Z-ignoring (M3).** Already a ledger conjecture; confirming
   it decides whether an FPV payload path works at all.
6. **Attached-charge detonation (F2).** Decides whether the IED's named
   mechanism is inert.
7. **`doArtilleryFire` magazine cap (V5).** A bounded, undeclared upper limit on
   an already-accepted contract.

None of these is a defect report. Each is a question whose answer is currently
being assumed.
