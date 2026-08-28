# Vigil artillery preview-marker lifecycle — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: SPLIT.** The reachable artillery strike-pattern preview is
**KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for one client changing a
valid circle request through count `0 -> 1 -> 3 -> 0`: the preview follows the
requested world position, replaces stale markers, and clears on the explicit
zero-count transition. Close-time removal from an active non-empty preview is
**REVIEWED / NEEDS COVERAGE**. The separate coordinate-preview marker created
by the same grid handler is **PARTIALLY COVERED; REFINE BEFORE COVERAGE**
because current source does not include it in dialog cleanup. Line rendering,
range colour, first-round ETA, VLS sizing, tab-switch behavior, client-B/JIP,
and invalid-input presentation remain bounded gaps described below.

This is a durable review closeout of existing source and accepted permanent
evidence. It does not rerun Arma, reinterpret artillery execution as rendering
proof, or alter the accepted `vigil-markers` scenario.

## Canonical review questions

### 1. What should the user observe?

On the reachable Assets / Artillery page, entering a valid grid and changing
count, spread, direction, pattern, or ordnance updates a map preview of the
prospective strike positions. A one-round circle preview is centered on the
requested grid; changing the request replaces rather than accumulates the old
pattern; setting count to zero removes it. Closing the tablet should not leave
Vigil-owned preview markers behind.

The product also places a distinct coordinate symbol at the entered grid. Its
intended lifetime across tab changes and tablet close is not documented. The
safe candidate outcome is therefore cleanup with the owning UI unless product
owners explicitly choose persistence.

### 2. What does the feature actually do now?

The shipped artillery controls in `page_assets.hpp` call the real handlers in
`fn_ui_arty.sqf`. `YOSHI_assetCoordChanged` parses the grid, selects the
artillery branch, updates the artillery grid, redraws the strike pattern, and
creates or moves `YSF_arty_coord_preview`. Each count, spread, direction,
pattern, and ordnance handler updates client UI state and redraws.

`YOSHI_drawStrikePattern` first deletes the marker names from the previous
strike-pattern generation. Count below one stores an empty marker list and
returns no positions. Positive circle requests distribute points through the
golden-angle disk; positive line requests distribute them across the requested
bearing. It creates local ellipse markers, with an optional local ETA icon for
the first position, and stores only those names in `YOSHI_sp_markers`.

The dialog's reachable `onUnload` calls `YSF_clearAllMarkers`, which traverses
`YOSHI_sp_markers` and `YSF_map_overlay_markers`. It neither deletes nor clears
the coordinate-preview variable. Tab selection changes the asset type and
refreshes controls but does not explicitly retire artillery previews.

### 3. Which machines and lifecycle stages own the behavior?

The tablet display, controls, artillery request state, generated positions,
and all preview markers are client-local. The permanent scenario proves this
on authenticated `client-a` and separately proves that the dedicated server is
headless, has no Vigil display, and has no strike-marker state. No server
mutation is needed to draw a preview.

That does not prove client-B isolation, JIP/reconnect state, or simultaneous
independent previews. Client-a evidence must not be reported as those cases.
Artillery submission and firing are separately server-authoritative and belong
to the `vigil-artillery` contract, not this review.

### 4. Which mechanics are generic Arma, CBA, or Tribunal concerns?

Local map-marker creation/deletion, map world-to-screen projection, control
events, framebuffer capture, authenticated pointer/keyboard delivery, and
bounded changed-pixel comparison are generic mechanics. Tribunal's map driver
correlates rendered pixels with exact marker registration and projected world
positions. CBA supplies the tablet input binding but does not own preview
semantics.

Vigil owns the artillery parameters, generated strike geometry, colour/size
policy, state lifetime, and which UI transitions retire previews.

### 5. Which behavior is owned by the product?

Vigil owns grid acceptance, circle/line selection, spread/count/direction
meaning, ordnance/range presentation, VLS marker sizes, first-round ETA text,
whole-generation replacement, and cleanup policy. The product must decide
whether coordinate and strike previews persist while the user visits another
asset tab. It should also explicitly decide whether reopening restores request
state without markers or resets both; current source can preserve artillery
state while deleting only some marker stores.

### 6. Are unusual or claimed engine requirements proven?

Only the visual calibration is characterized: at map scale `0.025`, the
100-by-125-metre ellipse border fell outside the viewport even though its
center projected on-screen; scale `0.2` kept the footprint visible. The
retained driver therefore uses tolerant bounded pixel differences near the
independently projected anchor rather than exact framebuffer equality.

No controlled evidence proves that using global-form `deleteMarker` from a
client is required or equivalent to `deleteMarkerLocal` for these local-only
names. No such mechanism should be frozen as contract. Likewise, no marker
evidence establishes `inRangeOfArtillery` or `getArtilleryETA` behavior; those
values need their own causal controls if their presentation becomes required.

### 7. Which details are accidental, legacy, fragile, or incomplete?

Marker names based on tick time/random values, `uiNamespace` keys, IDC values,
the fixed test coordinate, and backing-array layout are private adapters, not
promises. Recreating an entire marker generation is replaceable.

Two lifecycle gaps are substantive rather than cosmetic:

* `YSF_arty_coord_preview` is reachable through the same grid interaction but
  is absent from `YSF_clearAllMarkers`; source therefore permits it to survive
  tablet close.
* The accepted scenario sets count to zero before closing. Its close assertion
  proves that the display closes and already-empty strike/overlay stores remain
  empty; it does not causally prove `onUnload` removes an active pattern.

The scenario also uses the product's real grid/count handlers after external
navigation reaches Artillery, but directly calls private setters to calibrate
circle/spread/direction. Those calls establish fixture geometry; they are not
proof of keyboard or combo-box presentation for every parameter.

### 8. Is a better native or existing mechanism available, and is it proven?

Arma local markers are appropriate for a private client preview, and the
existing Tribunal map observer is appropriate evidence. Source already uses
`deleteMarkerLocal` when replacing strike and asset-overlay markers. Aligning
all preview ownership under one explicit local cleanup registry is a plausible
refinement, but this documentation audit did not compare implementations and
does not prescribe a rewrite.

The stable specification should require visible update, exact spatial/count
correlation, replacement, and complete client-local cleanup while leaving the
marker implementation free.

### 9. What is the stable behavioral contract and its causal proof?

For the accepted slice: after the real client reaches the Artillery page, a
valid grid plus count change produces a visible client-local preview whose
count and world position match the request; a later count change replaces old
preview state; count zero removes the generated pattern. The dedicated server
has neither display nor corresponding marker state.

The permanent `vigil-markers` scenario pairs four independent evidence layers:

* real rendered page/map frames and a bounded map-region pixel sequence;
* world-to-screen projection at the exact requested grid;
* live `allMapMarkers` membership plus marker shape/size;
* generation identity and empty-state cleanup on the authenticated client,
  with dedicated-server negative controls.

It proves one circle at the requested point, a distinct three-circle
generation with no stale original marker, and explicit zero-count cleanup.
Backing state alone, unrelated pixels, a marker outside the viewport, reused
names, three array entries without a larger rendered footprint, and server or
another identity satisfying client-a are false-PASS paths.

The close-time claim must be narrower: current evidence proves closed display
plus empty stores only after explicit clear. An accepted active-close arm must
start from independently rendered non-empty markers, close through the real UI,
and prove every old strike, coordinate, ETA, and overlay marker absent.

### 10. Which implementation details must remain free to change?

Private function and namespace names, marker-name generation, exact ellipses,
IDC/layout coordinates, polling intervals, screenshot dimensions, pixel
thresholds, test world coordinate, state-map schema, and full-generation versus
incremental rendering may change. The current 100-by-125 marker size is an
evidence anchor for the accepted fixture, not necessarily a permanent UX API.

The stable promises are client-locality, request-correlated visible geometry,
replacement without stale state, and bounded complete cleanup.

### 11. Which mechanisms genuinely deserve characterization?

Retain the scale/viewport calibration only as Tribunal observer calibration,
not Vigil behavior. No product mechanism currently deserves characterization.
In particular, random marker naming, whole-generation recreation, global-form
deletion, golden-angle point ordering, and exact colour/size constants have no
controlled alternative proving them engine-imposed.

Circle/line execution geometry is covered elsewhere, but execution proof does
not characterize rendered marker geometry. Add visual variants only where they
expose a meaningfully distinct product promise rather than a combinatorial
matrix.

### 12. Which mechanics should be promoted into Tribunal?

The generic authenticated map driver, projected-anchor correlation, local
marker census, generation/stale-name check, and rendered cleanup sequence
already belong in Tribunal. A reusable active-marker-before-close arm would be
valuable for other UI-owned overlays. Vigil parameter policy, marker styling,
and state persistence remain in Pontifex.

## Permanent evidence and accepted boundary

The accepted repository record is permanent scenario `vigil-markers`, added by
commit `592d916` and subsequently given its explicit `ScenarioReview` contract
by `fe1e74c`. The retained validation narrative in `docs/vigil-testing.md`
records the calibrated interactive map-marker sequence and its false-PASS
controls. Current static architecture coverage requires scenario discovery,
the map-marker visual driver, projected anchor, real count path, independent
circle/spread/direction fixture setup, stale-name checks, and inclusion in the
gameplay plan.

No Evidence Contract v1 package or autonomous run identifier for this older
acceptance is referenced by the current repository documentation. This review
therefore does not invent package provenance or imply production
`arma-knowledge` ingestion. The scenario and its accepted visual artifact
contract remain the permanent proof named by the canonical inventory.

## Remaining boundaries and disposition

| Boundary | Status | Recommended disposition |
| --- | --- | --- |
| Circle count/position `0 -> 1 -> 3 -> 0`, stale replacement | **ACCEPTED / COVERED** | Retain permanent scenario |
| Active non-empty pattern closed through real UI | **REVIEWED / NEEDS COVERAGE** | Add a small causal close arm when the scenario is next revised |
| Coordinate-preview marker cleanup | **PARTIALLY COVERED; PRODUCT DEFECT CANDIDATE** | Decide persistence, refine cleanup, then prove active close/reopen |
| Tab switch with active artillery preview | **NEEDS PRODUCT DECISION** | Choose retain-versus-retire semantics before testing |
| Visible line/spread/direction variants | **OPTIONAL / LOW VALUE** | One representative line image is enough if visual parity matters; do not build a matrix |
| Range colour, first-round ETA, VLS-specific sizes | **REVIEWED / NEEDS COVERAGE** | Cover only if these cues are retained product promises; use valid/out-of-range controls |
| Invalid grid/count presentation | **PARTIALLY COVERED elsewhere** | Parser rejection belongs with artillery request review; visual hint/field behavior is optional UI work |
| Client-B isolation, simultaneous previews, JIP/reconnect | **EXTERNALLY BLOCKED / SHARED GAP** | Reuse the program-level client-B/JIP boundary; do not duplicate it here |
| Network profiles | **INTENTIONALLY DEFERRED** | Local previews do not need replication matrices |
| Artillery firing/impact | **SEPARATELY COVERED** | Keep `vigil-artillery`; never infer execution from preview pixels |

## Inventory contradiction requiring reconciliation

The canonical inventory currently says the artillery request UI/preview
markers are covered for grid, ordnance, spread, count, direction, circle/line,
rendering, locality, and cleanup. Source plus the exact permanent assertions
support a narrower conclusion: the accepted scenario directly proves the
circle count/position replacement slice and explicit zero-count cleanup. It
does not render a line arm, exercise range/ETA/VLS cues, close from a non-empty
pattern, inspect `YSF_arty_coord_preview`, or prove tab-switch cleanup.

Accordingly, the accepted core should remain covered, while the family is
recorded as partially covered for the meaningful lifecycle gaps above. This
review reports the contradiction without changing the shared inventory or any
accepted evidence classification during the documentation-only closeout.
