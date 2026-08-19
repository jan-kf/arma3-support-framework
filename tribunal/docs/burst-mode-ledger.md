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

Current feature HEAD: `0badf72`. Accepted/covered in this ledger: Iron Dome
and Tribunal manifest parity. Reviewed/deferred or precisely bounded: FPV,
APS anti-drone, CORDIS, CBR modules, Vigil homepage, Field towing, helicopter
stabilizer, and the laser harness. Open experiments and decisions are recorded
per row. Exact next recommended feature: **Field Utilities automatic object
handling / nearby supply loading**.
