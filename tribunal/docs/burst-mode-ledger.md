# Pontifex / Tribunal Burst Mode ledger

Operational closeout index for the current Burst Mode. Full evidence and
decisions remain in each canonical feature review and the feature inventory.

| Feature | Outcome | Commit | Fresh proof | Open decision / experiment | Next action |
| --- | --- | --- | --- | --- | --- |
| OPHANIM / Iron Dome | ACCEPTED / COVERED | `74f8db4` | `20260819T222930Z-2ff35050`; server 18/0, client 6/0 | client-owned artillery and threat/side policy deferred | retain baseline; revisit only after policy decision |
| Field Utilities FPV modifications | REVIEWED / REFINE BEFORE COVERAGE | `6be7f61` | none; static review | payload inventory/exclusivity, requester eligibility, effects; owner-local physical A/B | choose policies, add validated request boundary, characterize releases |
| APS anti-drone | REVIEWED / DEFERRED | `c257211` | none; policy/static boundary | threat side/direction/range/default/operator policy; atomic owner resource/result experiment | decide policy, then run exact-UAV locality/transaction A/B |
| CORDIS routing/dedupe | REVIEWED / REFINE BEFORE COVERAGE | `7ac5d77` | none; accepted consumers incidental only | trust model, result semantics, key namespace, failed-delivery/recipient policy | decide API boundary, then run one-session routing/dedupe matrix |
| CBR Eden/Zeus activation | REVIEWED / REFINE BEFORE COVERAGE | `35086f5` | none; downstream CBR baseline remains accepted | real module dispatch/locality, curator authority/feedback, Eden disposal | add typed module fixture; run Eden/no-Eden and curator authority A/B |
| Vigil homepage task management | REVIEWED / DEFERRED | `902d0f5` | none; unreachable static scaffold | whether page ships; task visibility, cancellation authority/history/finalization | no implementation until product decisions exist |
| Field Utilities towing | REVIEWED / REFINE BEFORE COVERAGE | `dd7a310` | none; static boundary review | eligibility/authority, feature-owned ropes, parent/breakage/finalization policy; physical locality A/B | decide contract, then run exact ACE tow/stow and paired-trajectory experiment |
| Vigil helicopter stabilizer | REVIEWED / NEEDS EXPERIMENTATION | `ead2d3e` | retained `20260813T184341Z-317a1605`, `20260816T151957Z-c7e7de23` reach force path; no causal A/B | enabled policy/outcome bound/owner scope; matched flights and cancellation/terrain controls | run paired enabled/disabled transport experiment after product outcome decision |
| Tribunal manifest discovery | ACCEPTED / COVERED | `146cd38` | static CLI lists all 12 runtime product scenarios; 104 tests pass | none | retain independent manifest/runtime parity regression |
| Vigil developer laser harness | REVIEWED / DEFERRED | `0badf72` | none; exhaustive static reachability/boundary review | remove, move to dev/Tribunal, or capability-gate with bounded execution/storage | do not use as product evidence; decide disposition before reuse |
| Field object handling / supply loading | REVIEWED / REFINE BEFORE COVERAGE | `3c17d1a` | none; static boundary review; 104 tests/static checks pass | split contact vs cargo policy; eligibility, authority, unload/finalization; locality/return experiments | run isolated exact ACE cargo and physical-contact A/B after decisions |
| Field map helpers / airdrop feedback | markers REVIEWED / DEFERRED; feedback NEEDS DECISION/EXPERIMENT | `22854e5` | accepted logistics executes announcement incidentally; no feedback oracle | marker reachability/visibility; direction meaning, ETA interval/audience; two-distance timeline A/B | leave markers dormant; define feedback semantics then compare against physical delivery timeline |
| Field helicopter sling helper | REVIEWED / DEFERRED | `8ea789e` | none; exhaustive static reachability review | whether it ships; entry/authority, rope ownership, native/custom mechanism, cleanup | revisit only after a supported entry and authoritative rope-operation policy |
| Vigil fixed-wing UAV deploy boundary | REFINED; ACCEPTED / COVERED | `f609419` | `20260819T235611Z-e6d9a2dc`; server 23/0, client 17/0 | physical UAV reconstruction/control and reconnaissance product remain deferred | retain authoritative rejection; next cover tablet access matrix |
| Vigil tablet access | ACCEPTED / COVERED | `5e53728` | `20260820T000642Z-124746c4`; server 6/0, client 18/0 | itemless override cosmetic skin and fixed-wing override consistency are not access promises | retain data-first B/I/O/rejection/override matrix; characterize VLS handshake next |
| Vigil VLS target handshake | REVIEWED / CHARACTERIZED | `96cdd4f` | Live `20260820T001108Z-c8edbbcc`; four direct-first physical A/B pairs; exact baseline `2:240` diverged and `2:248` terminated 0.74 m from target | individual report-versus-confirm necessity and ordering remain unisolated | retain combined handshake; require another physical A/B before simplifying it |
| Advanced Systems common utilities | REVIEWED / DEFERRED AS STANDALONE; CONSUMER-OWNED | `f414463` | none; exhaustive static reachability and consumer map | beam/audio concurrency and audience only if a consumer promises them | keep helpers internal; test outcomes from each consumer entry |

| Vigil mixed-fleet asset browser | REFINED; ACCEPTED / COVERED | `039ad91` | `20260820T010547Z-f5c9dfb1`; server 9/0, client 22/0 | whitelist/Zeus, fixed-wing rows, dormant recon, client-B/JIP, distant captured-crew edge | retain exact backing/tree identity matrix; next review Field Utilities cold-client ACE composition |
| Field Utilities cold-client ACE composition | ACCEPTED / COVERED | `a1f5ff3` | `20260820T012801Z-0212d338`; server 2/0, client 4/0 | Fabricator delayed object action, effects, repeated-init, client-B/JIP remain separate | retain concrete-class inheritance/relevance matrix; next canonicalize Vigil task governor review |

Current feature HEAD: `a1f5ff3`. Accepted/covered or characterized in
this ledger now also includes the Field Utilities cold-client ACE composition
boundary. Reviewed/deferred and precisely bounded work remains linked above.
Scout evaluation: all three packets materially reduced reconnaissance without
runtime or repository contention; the governor packet supplies a complete
canonical continuation and the other two identify independent follow-ups.
Three-scout parallelism remains useful with explicit non-overlap. Exact next
recommended feature: **Vigil task governor** for a static terminal review, then
the cross-addon CBA settings contract.