# Vigil mixed-fleet asset browser — canonical feature review

Reviewed against [`feature-review-program.md`](feature-review-program.md).

**Classification: REFINED; KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for
the live unwhitelisted transport, artillery, and rotary-CAS browser. Eden
whitelisting, Zeus mutation, fixed-wing registry presentation, and the dormant
recon branch remain separate surfaces.

## Canonical review questions

### 1. What should the user observe?

The Assets page lists exactly the live friendly assets eligible for the chosen
transport, artillery, or rotary-CAS category. Hostile, dead, and wrong-role
objects do not appear.

### 2. What did the implementation actually do?

With no whitelist module, each refresh scans `vehicles`, filters by category and
side, groups the results, stores the exact objects in `YSF_assets_items`, and
writes their net IDs into the live tree rows. Before refinement, the side helper
preferred a vehicle's live commander but fell back to `side vehicle`. On a
remote client, stationary support vehicles more than four kilometres away had
no streamed commander proxy and reported civilian vehicle side, so valid
friendly assets disappeared.

The refined helper still prefers the current commander's group side when that
entity is available, preserving captured/re-crewed vehicle behavior. When no
commander proxy exists, it uses the vehicle class affiliation. This makes
normal map-wide mission assets deterministic without requiring distant AI
entities to be streamed merely to render a browser.

### 3. Which machines and lifecycle own it?

The server owns the network vehicles and crews. Each client independently
scans its visible network objects, evaluates eligibility, and owns its backing
list and tree controls. No server UI state is created.

### 4. Which mechanics are generic?

Exact network-object fixtures, object resolution, live tree-row extraction,
and UI state observation are generic Tribunal mechanics. Vigil owns categories,
side policy, eligibility, grouping, and presentation.

### 5. Which behavior is product-owned?

The three reachable live categories and their friendly/live/role eligibility
are Vigil policy. Whitelist restriction and curator mutation are not part of
this contract.

### 6. Are unusual engine requirements proven?

Yes. In cold runs `20260820T004533Z-2f1fc7ce` through
`20260820T005512Z-fb01e9c2`, the dedicated server proved exact living WEST
crews, while the real client still observed null `effectiveCommander` proxies
for distant, stationary, fuel-zero assets after a bounded 15-second wait.
`side vehicle` was civilian. This is direct engine-visible evidence that a
map-wide client browser cannot require a streamed crew entity for ordinary
class-affiliated assets.

### 7. Which details were accidental or fragile?

Depending on crew streaming was accidental. Tree group labels, row ordering,
control IDs, backing-array shape, refresh cadence, and helper names are
replaceable. The old recon classifier exists, but no shipped tab dispatches a
recon selection; it is not silently promoted into this contract.

### 8. Are native alternatives available?

Arma config affiliation is available without crew streaming, while live group
side captures runtime re-crewing when present. The bounded two-source rule is
preferable to forcing crew replication or moving assets near the client.

### 9. What is the stable contract and causal proof?

A fresh tokenized mixed fleet contains one eligible friendly asset for each
reachable category, same-role hostile controls, a dead friendly transport, and
a live friendly wrong-role vehicle. The scenario invokes the real category
selection path and compares both the backing objects and actual tree `tvData`
against independently known net IDs. Exact-set equality rejects missing,
extra, stale, or duplicated rows.

### 10. Which details must remain replaceable?

Config lookup syntax, grouping/order, labels, icons, control layout, helper
names, and refresh implementation may change. A distant captured vehicle whose
live hostile crew is not streamed is not specified by the fallback rule.

### 11. What remains unproven or deferred?

Mission-native Eden whitelist restriction, live Zeus add/remove, client-B/JIP,
fixed-wing registry rows, and the dormant recon path remain unreviewed or
separately covered. Distant captured/re-crewed assets with an unavailable crew
proxy need an explicit authoritative-side design if that edge becomes a product
requirement.

### 12. What belongs in Tribunal?

Tokenized mixed fleets and exact backing/tree identity observation belong in
Tribunal. Vigil's category predicates and fallback side policy remain product
code. No new generic visual or ACE mechanism was needed.

## Permanent evidence

Fresh autonomous run `20260820T010547Z-f5c9dfb1` passed 9 server and 22 client
assertions with zero failures. The server proved all eight exact class/net-ID,
alive/dead, WEST/EAST crew, and server-local stimuli. The client proved exact
transport, artillery, and rotary-CAS backing/tree sets, plus hostile, dead, and
wrong-role exclusion. Existing tablet access, visible navigation, close/reopen,
locality, and framebuffer checks also passed. Both containers, the private
network, and run state cleaned up normally.

The preceding failed cold runs are retained as discriminating evidence rather
than hidden retries: their exact predicate telemetry isolated missing remote
crew proxies, and the same fixture passed only after the bounded product-side
fallback.
