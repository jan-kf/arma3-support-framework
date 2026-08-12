# Vigil Tablet validation

## Runtime architecture

Vigil is a client-local Arma dialog. `YSF_UI_OpenTablet` requires the CBA
`YSF_enableTablet` setting and `YSF_VigilTerminal_B` in the real player's
assigned items, then creates `YSF_Tablet_Dialog` (IDD 88000). CBA binds that
open action to Ctrl+Home. Dialog `onLoad` stores the display in
`uiNamespace["YSF_Tablet_Display"]` and initializes navigation; `onUnload`
clears overlay markers, replaces the display with `displayNull`, and emits the
TurnOff sound event.

The shipped registry currently exposes the Assets page. Its RscToolbox (IDC
88050) has Transport, Artillery, CAS, and Fixed Wing tabs. Selection invokes
`YOSHI_assetsTabChanged`, which records `YSF_assets_tabIndex`, maps it to the
asset type, and refreshes the corresponding controls. The page and selection
state, display reference, and map overlays are client-local in `uiNamespace`.
Support-task/governor data may be server-backed, but the first UI scenario does
not create or execute support tasks. An empty support inventory is valid and
renders the no-assets state.

The UI emits BootUp, DialUp, UiActivate, UiTabSwitch, and TurnOff events. Normal
automated clients currently use `-noSound`; this milestone proves the UI/event
path, not audible output. There are no required animations for the selected
Assets-tab interaction. A cold client can enter `initPlayerLocal.sqf` while
Arma is still building action-map caches, so the scenario arms external input
only after a bounded post-init/inventory settle, then equips and verifies the
fixture item against the gameplay display and living player. This ordering is
important because late join inventory synchronization can overwrite an item
linked immediately from `initPlayerLocal.sqf`.

## MVP scenario and evidence

The permanent `vigil-ui` Tier 3 scenario uses the smallest meaningful path:

1. equip the real Vigil terminal on `client-a`;
2. capture the baseline 1280x720 Arma framebuffer;
3. deliver the product's real Ctrl+Home binding as XTest keycodes on the
   private Xwayland display (so Proton emits CBA's expected DIK event);
4. correlate the rendered Transport page with dialog/control existence and
   `YSF_asset_type="transport"`;
5. click the real Artillery tab, move the pointer away, and correlate the
   persistent rendered page transition with tab index 1, asset type `arty`,
   visible artillery controls, and hidden transport controls;
6. deliver Escape, require visual disappearance, `displayNull`, and cleared
   overlay markers;
7. invoke the normal open action in a fresh scheduled UI context and require a
   clean Transport/index-0 state.

The server independently asserts that it is dedicated/headless, has no Vigil
display, and executed no duplicate server-side UI path. Scenario metadata is
identity-based rather than count-based so a future `client-b` assertion can
require an unchanged display and namespace without redesigning the contract.
The VNC listener remains internal to the confined client container and is not
published to the host for autonomous runs.

Tribunal stores baseline/open/target/closed/reopened captures, region metrics,
protocol negotiation, changed-pixel fractions, and input details as a typed
`interactive-framebuffer-sequence` attachment. Visual checks use stable regions
and tolerant structural differences, never full-frame equality.

Weston's RFB keysym transport is retained for Escape and pointer input, but it
did not translate Ctrl+Home into the DIK Home chord on a cold Proton client.
Tribunal therefore uses the existing container-local XTest library for that
keyboard chord and records the backend in evidence. Both transports remain
inside the unpublished client display boundary.

## False-pass threats

The evidence contract explicitly rejects these misleading outcomes:

* a non-null display with no visible rendered tablet;
* a visible tablet on the wrong page;
* a stale or black framebuffer;
* an existing but hidden, disabled, or off-screen control;
* an RscToolbox hover highlight mistaken for selection;
* a callback or backing-state change without a persistent rendered change;
* a rendered change without matching tab/type/control state;
* an internal function call presented as the primary user input;
* a different page mistaken for a closed tablet;
* uncleared local overlay markers after close;
* stale tab state after reopen;
* server-side display ownership or a duplicate open path;
* missing screenshots, input results, product assertions, or lifecycle states.

The hover case was observed in Live Mode: merely pointing at Artillery painted
it like a selection. The generic driver now moves away and requires the larger
page transition plus independent application-state evidence. Missing or
ambiguous evidence fails closed.

Arma also reports `ctrlShown=false` for Vigil's inherited initial page/control
groups even while their children visibly render. Initial and reopened state
therefore require the real display/control objects, enabled tab control,
selection, and application type, correlated with the framebuffer; the test
does not reinterpret that unreliable parent visibility flag as rendering.

## Follow-on order

After this MVP, add coverage in this order:

1. client-b isolation while client-a opens and changes pages;
2. map-marker presence, placement, visibility, and dynamic marker counts;
3. benign invalid/edge-case input and close/reconnect state;
4. artillery request lifecycle;
5. helicopter movement and landing;
6. CAS tasking;
7. network-profile behavior for task and marker replication;
8. audible sound capture after Tribunal gains its opt-in audio backend.

Each behavioral scenario should keep real input/rendered evidence distinct
from server-authoritative task effects and must pass from a fresh autonomous
run after any Live Mode iteration.
