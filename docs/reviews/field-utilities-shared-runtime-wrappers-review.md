# Field Utilities shared runtime wrappers — canonical feature review

Primary outcome: **REVIEWED / DEFERRED AS A STANDALONE FEATURE;
CONSUMER-OWNED**.

This review covers Field Utilities' global object-action registration helper,
CORDIS debug/chat adapters, and generic vehicle-sound helpers. Geometry and
packing primitives, FPV click/shuffle feedback, and each consuming feature's
semantics remain outside this boundary.

## Twelve-question review

1. **What should the user or integrator observe?** No shared-wrapper feature is
   directly advertised. Bridge users see its exact ACE action; logistics users
   may receive an airdrop message; developers receive diagnostics. Generic
   vehicle sounds have no product entry.
2. **What does it do now?** `YOSHI_addActionToObjectForEveryClient` broadcasts a
   raw ACE registration call to current clients and uses an object-local flag
   to deduplicate each client. The debug/chat wrappers delegate to CORDIS. The
   sound helpers broadcast `say3D`, store one handle per source, and delete the
   latest stored handle on stop.
3. **Which machines own it?** The Bridge server requests registration but ACE
   state is client-local. The dedupe flag is deliberately local so one client
   cannot suppress another current client. Chat/debug ownership is inherited
   from CORDIS. Sound playback is requested on every current client. These
   wrappers do not establish gameplay authority.
4. **Which mechanics are generic?** Client destination receipts, JIP delivery,
   ACE active-tree observation, feedback recipient observation, and audio
   capture can be Tribunal mechanics. These wrapper implementations are not a
   generic product contract.
5. **Which behavior is product-owned?** Bridge owns its action identity,
   relevance, and effect. Airdrop feedback owns its meaning/audience. Fabricator
   owns diagnostic content. A future sound consumer must own audience,
   overlap, and stop semantics.
6. **Are unusual engine requirements proven?** The accepted Bridge scenario
   proves the concrete current client receives and can execute its action. It
   does not prove that raw broadcast or local flag storage is required, nor
   that future/JIP clients receive dynamic registrations. Sound playback is
   unproven under `-noSound`.
7. **What is fragile or incomplete?** Object-action delivery has no JIP-persistent
   record, acknowledgment, retry, or result. The wrapper accepts arbitrary code
   and depends on the caller's authority. Chat/debug inherit CORDIS's unresolved
   destination/result semantics. Concurrent sounds overwrite one object
   variable, so stop can address only the latest stored handle.
8. **Is a better mechanism available?** Persistent per-object remote execution
   or a client initialization registry could support JIP, but should be adopted
   only for a consumer that requires it. CORDIS remains the shared feedback
   layer. Orphan sound helpers need no replacement absent a real consumer.
9. **What is the stable contract and causal proof?** There is no standalone
   contract. A consumer must prove its real entry, exact destination identity,
   client-visible registration/presentation, and consequential result with an
   independent oracle. Wrapper invocation or a dedupe flag cannot substitute.
10. **Which details remain free?** Helper names, local flag key, raw-code
    transport, registration path, retry/persistence mechanism, message wrapper,
    sound handle variable, range, pitch, and stop representation are
    replaceable.
11. **Which mechanisms deserve characterization?** Revisit action delivery only
    in a true client-B/JIP experiment. Revisit feedback after its audience
    decision. Revisit sound only after a reachable consumer adopts explicit
    audible, concurrency, and cleanup behavior.
12. **What belongs in Tribunal?** Reuse the existing ACE active-tree adapter and
    future client-N destination receipts. Add audio observation only for a
    concrete product need. Do not promote raw code broadcasting or
    Field Utilities helper semantics.

## Evidence and false-PASS boundary

Bridge Builder is the only consumer of the global object-action wrapper and its
accepted scenario proves that exact current-client ACE action, relevance, real
statement invocation, and bridge outcome. That does not generalize to arbitrary
objects or JIP delivery. A local dedupe flag proves neither registration nor
future-client visibility.

The airdrop announcement is the only side-chat consumer and retains its own
unresolved meaning/audience experiment. Debug is diagnostic. The generic
vehicle-sound helpers have no repository caller; direct invocation would
manufacture reachability. A dispatch/return, log line, stored sound handle, or
`CfgSounds` class is not recipient-visible or audible evidence.

## Decisions and continuation

Keep these wrappers internal and consumer-owned. No standalone scenario is
justified. If dynamic object actions must support JIP, use the future real
client-B/JIP matrix and prove exact active-tree delivery before changing the
transport. Resolve airdrop audience and ETA in its existing review. Decide
whether the generic sound API is supported before preserving or replacing its
single-handle concurrency model.
