# Cross-addon CBA settings contract — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REFINED; KEEP AS-IS AND STATIC-CONTRACT; ACCEPTED / COVERED**
for declaration identity, type, default/bounds, synchronization scope, live
consumer handoff, and fallback parity. The gameplay, feedback, sound, color,
Draw3D, and UI effects remain owned by their consumer features.

## Canonical review questions

### 1. What should the user or integrator observe?

Pontifex registers one unambiguous setting for each supported policy or personal
presentation choice. Every consumer reads the same key with a compatible
fallback. Mission-wide settings remain synchronized; client presentation colors
remain local.

### 2. What did the implementation actually do?

Advanced Systems registers radio, debug, and Iron Dome radius; Vigil registers
tablet access, radio, side-chat, debug, tablet color, and laser color; Field
Utilities registers side-chat, debug, Fabricator color, and bridge delay. All 13
keys are prefix-unique and have live consumers.

One defect was refined: Iron Dome registered 1000 m but its getter fell back to
1500 m when the CBA value was absent or early. The fallback now matches 1000 m.
The three debug descriptions also now match the actual CORDIS behavior: logging
always occurs and enabling the setting additionally shows client system chat.

### 3. Which machines and lifecycle own it?

Each add-on registers settings at preInit. CBA scope `1` makes policy/feedback,
tablet access, Iron radius, and bridge delay mission-wide. Omitted scope on the
three color settings intentionally retains CBA's client-local default. Consumers
read mission namespace values at use time; no callback or cached copy owns the
contract.

### 4. Which mechanics are generic?

Static declaration parsing, unique-key/type/default/bounds/scope comparison,
consumer lookup, and fallback parity are generic. The names and meanings of the
13 settings remain Pontifex product policy.

### 5. Which behavior is product-owned?

Whether tablet access, feedback, debug presentation, colors, engagement range,
or build delay are configurable—and their selected defaults/bounds/scopes—is
owned by the corresponding add-on. This review does not own their downstream
world or visual effects.

### 6. Are unusual engine requirements proven?

No unusual engine requirement is claimed. CBA's documented omitted setting
scope is local; explicit scope `1` is global. Direct scenario namespace overrides
prove consumer behavior, not registration metadata, and are not used as the
oracle here.

### 7. Which details are accidental or fragile?

Source formatting, declaration order, setting UI order, tooltip prose, and
consumer helper names are replaceable. The stable parts are unique identity,
type, default/bounds, intended scope, consumer key, and fallback parity.

### 8. Are native/existing alternatives available?

CBA remains the established settings mechanism. There is no reason to duplicate
these values in a custom settings registry or exercise the CBA UI visually.

### 9. What is the stable contract and causal proof?

An independently hard-coded 13-row matrix parses the three declaration files and
requires exact unique keys, types, defaults/bounds, and global/local scope. A
separate consumer table requires each key outside its declaration and exact
fallback values where direct fallbacks exist. The CORDIS oracle separately
requires unconditional `diag_log`, conditional `systemChat`, and true feedback
gates. Drift fails closed.

### 10. Which details must remain replaceable?

Labels, descriptions, category presentation, order, code layout, and wrapper
names may change. Changing a key/default/bound/scope is a product-contract change
and must update evidence deliberately rather than teaching the oracle from the
source.

### 11. What remains unproven or deferred?

Audio audibility under `-noSound`, feedback audience, actual color rendering,
laser Draw3D appearance, and combined-setting interactions remain consumer-owned
or deferred. The Ctrl+Home keybind is not a setting and is covered by Vigil UI.
Mission-wide feedback policy may be reconsidered later, but current scope is
explicit and internally consistent.

### 12. What belongs in Tribunal?

The independent static declaration/consumer/fallback pattern is reusable. No
runtime primitive or visual adapter is warranted for metadata already available
in source. Product-specific keys and defaults stay in this repository test.

## Evidence and compatibility

`tests/test_cba_settings_contract.py` independently asserts the exact 13-setting
matrix, consumer presence, direct fallback parity, and debug logging semantics.
No Arma run was required: the bounded Iron fallback correction changes only the
missing/early-setting case, while the accepted Iron Dome runtime used the normal
CBA-provided 1000 m value. Existing consumer scenarios retain their classifications.
