# Field Utilities FPV click/shuffle feedback — canonical feature review

Primary outcome: **REVIEWED / DEFERRED AS A STANDALONE FEATURE;
CONSUMER-OWNED PRESENTATION**.

This review covers the two randomized FPV interaction clicks, the
`DufflebagShuffle` attachment sound, and the otherwise unused generic vehicle
sound helpers. It does not reopen the Field Utilities FPV payload authority or
physical-effect contract.

## Twelve-question review

1. **What should the user observe?** The reachable FPV ACE statements play one
   local click when selected. Successful owner-local IED, mortar, or grenade
   attachment requests a shuffle sound from the UAV. Neither sound is an
   independent product operation.
2. **What does it do now?** `YFU_fnc_playRandomFpvClickLocal` selects one of two
   configured sounds and is called by all six FPV attach/use statements.
   Attachment functions invoke `say3D` with `DufflebagShuffle` after their
   owner-local state mutation. The four generic `YOSHI_*VehicleSound*` helpers
   have no repository consumer.
3. **Which machines own it?** The interaction click executes on the actor
   client. Payload attachment owner-routes through CORDIS and calls `say3D` on
   the UAV owner. Listener reach, attenuation, and actual playback are engine
   presentation behavior and are unmeasured. These paths grant no additional
   gameplay authority.
4. **Which mechanics are generic?** Sound-command observation, listener
   identity/range, audio capture, overlap, and teardown can be Tribunal
   mechanics if a concrete product adopts an audible contract. FPV action and
   payload meaning stays in Field Utilities.
5. **Which behavior is product-owned?** Field Utilities owns whether an FPV
   operation should have click/shuffle feedback and which operation state makes
   that feedback truthful. Payload authorization, inventory, mutation, and
   physical effects remain governed by the parent FPV review.
6. **Are unusual engine requirements proven?** No. Autonomous Arma clients run
   with `-noSound`; no evidence establishes audible playback, audience, range,
   concurrency, or a need for these exact `playSound`/`say3D` calls.
7. **What is fragile or incomplete?** Click choice is intentionally random and
   has no result. Shuffle is issued after setting attachment state but before
   the IED object is fully constructed. The generic global helpers broadcast
   raw code, store only one sound source per object, overwrite concurrent
   handles, and stop only the latest handle.
8. **Is a better mechanism available?** Possibly a consumer-scoped feedback
   event with explicit listener and overlap policy, but no accepted audible
   outcome justifies replacing the current incidental calls. Unused generic
   helpers should not become specification merely because they compile.
9. **What is the stable contract and causal proof?** There is no standalone
   audio contract. A future accepted FPV payload test must prove the exact
   authorized operation and physical result without relying on sound. If audio
   becomes promised, correlate that operation with a sound-enabled listener's
   independent capture and meaningful silence/range controls.
10. **Which details remain free?** Sound class names/files, random selection,
    pitch/range, helper names, command choice, source-handle storage, and exact
    timing remain replaceable presentation details.
11. **Which mechanisms deserve characterization?** None until audible feedback
    is selected as supported behavior. Then use one sound-enabled client, a
    real accepted payload operation, in/out-of-range listeners, overlapping
    operations, and exact cleanup. Do not characterize under `-noSound`.
12. **What belongs in Tribunal?** Only a product-neutral audio/listener observer
    if a second real consumer justifies it. Do not promote FPV sound policy or
    the unused vehicle-sound helpers.

## Evidence and false-PASS boundary

The click helper is reachable through the real ACE action statements; it is
not an orphan. The shuffle sound is reachable through owner-local payload
attachment. Their presence, a helper invocation, `say3D` return, configured
`CfgSounds`, a successful payload mutation, or a source object are not evidence
that a listener heard the intended feedback. Conversely, silence from the
current `-noSound` autonomous client is not a product failure.

The generic vehicle-sound helpers have no product caller. Directly invoking
them would manufacture reachability and fossilize concurrency and broadcast
semantics that no feature currently promises.

## Decisions and continuation

No decision is needed to keep audio consumer-owned and non-blocking. Reopen
only if Field Utilities explicitly promises audible FPV feedback, then decide
listener audience/range, disabled behavior, overlap/preemption, exact cleanup,
and whether the sound reports request selection, accepted attachment, or
completed physical mutation. The parent FPV feature still requires its own
authority and physical-effect refinement regardless of audio.
