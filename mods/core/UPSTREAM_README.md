[h1]Pontifex: CORDIS[/h1]

[b]C.O.R.D.I.S.[/b] stands for [i]Common Operational Runtime & Distributed Integration Services[/i].

CORDIS is the shared runtime layer behind the Pontifex mod suite. It provides the multiplayer plumbing that routes scripted execution to the right machine, keeps distributed systems synchronized, and delivers notifications and events reliably during live operations.

[h2]What CORDIS Provides[/h2]
[list]
[*]Authority-aware execution helpers for server, object owner, and group owner routing
[*]One-shot and TTL-based deduplication to prevent duplicate event handling
[*]Reliable target resolution for players, sides, and scoped broadcasts
[*]Shared helpers for side chat, side radio, curator notifications, and debug output
[*]A lightweight common foundation for other Pontifex systems and extensions
[/list]

[h2]Routing Contract[/h2]
[list]
[*]Named operations are trusted calls between cooperating Pontifex components. Gameplay features remain responsible for authorization and terminal success/failure acknowledgments.
[*]Route results identify the broker boundary: [code]rejected[/code], [code]queued[/code], [code]accepted[/code], or [code]executed[/code]. A queued or accepted result does not claim that remote gameplay completed.
[*]Nonempty once-keys are scoped to the route and operation name. Invalid operations, destinations, TTLs, and recipient scopes do not consume a key.
[*]Recipient scope [code]0[/code] is a deliberate broadcast to live real players. An explicit empty, invalid, or wrong-side scope delivers to nobody and never falls back to broadcast.
[/list]

[h2]Notes[/h2]
[list]
[*]CORDIS is a framework mod and is intended to support other gameplay systems rather than add standalone content on its own.
[*]Requires CBA_A3.
[/list]
