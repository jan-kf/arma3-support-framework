# Advanced Systems Counter Battery Radar review

Primary outcome: **KEEP AS-IS AND SPEC-TEST; ACCEPTED / COVERED** for per-strike
impact observations, scale-aware map presentation, terrain-aware prediction,
origin estimation, the current warning policy, lifecycle, and one authenticated
client. Multi-owner authority, warning cadence, confirmed-origin expiry,
audience, client-B and JIP remain separate boundaries.

## Behavioral contract

While CBR is enabled, the shell-owning machine detects each artillery shell and
reports its predicted impact to the dedicated server. The server retains one
independent strike observation per physical shell. Each row carries its stable
tracking identity, current position, uncertainty geometry, first/latest
observation times, ETA/expiry, and launch provenance. Updates for one identity
revise that row; different shell identities are never destroyed or folded
together.

Each interface client derives disposable presentation from the replicated rows
and current real map scale. Observations close in screen space merge as the user
zooms out and split when zooming in. A fixed five-metre arming threshold
prevents nearly coincident icons flickering apart. Visual grouping never mutates
the rows, and there is no active-observation cap.

A singleton draws its uncertainty ellipse. A group draws a capsule comprising
an oriented rectangular body and circular end caps. The farthest constituent
pair supplies the axis; the radius includes each member's uncertainty plus its
perpendicular offset. A linear walking barrage therefore stays long and narrow
instead of becoming an enormous enclosing circle. Its icon reports observation
count and ETA range.

Repeated fire from one launcher still narrows its orange origin estimate to a
confirmed fix. The first shell of the current owner-local airborne cycle still
warns living opposing-side players within 1000 metres. Rows expire independently
after landing. Stop clears rows, presentation, origins, threads and enabled
state. A proven disabled shot produces none of those outcomes.

## Redesign conclusion

The retired implementation permanently assigned a new shell to the nearest
server cluster inside 100 metres, never migrated it, and drew one leeway-inflated
circle. Grouping could depend on arrival order and walking fire needed an
artificial zone-migration policy.

Server state is now YOSHI_CB_observations; YOSHI_CBR_OBSERVATIONS is its
replicated presentation input. Clusters exist only as client-local derived views
and rebuild when rows or map scale change. No fixed zone membership,
reassignment policy, or arbitrary capacity limit remains.

The earlier terrain fix remains: integration terminates at ground below the
projected point rather than ASL zero and has an explicit time bound.

## Ownership and authority

Detection remains shell-owner-local through ArtilleryShellFired and the local
shell gate. The dedicated server owns observations, prediction, origins,
warnings and lifecycle. Clients own only local visual markers.

Provenance records sending owner, launcher net ID, weapon, ammo, side, and
server-observed remote execution owner. This supports the retained contract and
diagnostics but does not finish authority: a future change must register a
physical launch against its authenticated owner/launcher before rejecting
forged or wrong-owner telemetry.

## Stable versus replaceable

Stable behavior is independent per-shell retention; position, uncertainty,
timing and provenance stored together; non-destructive zoom presentation; a
compact elongated envelope for linear groups; no cap without performance
evidence; terrain accuracy; origin behavior; current warning behavior;
independent expiry; and complete stop cleanup.

Array layout, UID format, variable/marker names, numeric presentation
thresholds, connected-component implementation, capsule algorithm, brush,
polling cadence and prediction step remain replaceable.

## Permanent causal proof

Accepted run **20260828T175511Z-44e26fea** passed all feature assertions and
complete teardown under Evidence Contract v1.

The server fired eight exact native mortar shells. Tribunal independently
observed launch, trajectory and terminal position. At peak CBR held eight unique
rows with ellipse uncertainty, coherent timing/expiry and exact
launcher/weapon/ammo/side/owner provenance. Prediction stayed within the
established 20-metre position and three-second ETA bounds; the row centroid
stayed within 30 metres of the real impact centroid.

The real client received the eight rows, rendered local red area/icon markers,
held no authoritative server table, and removed its view after expiry. A
controlled walking-barrage arm then held four unchanged observations at
300-metre intervals:

| Map scale | Derived groups | Underlying rows |
| --- | ---: | ---: |
| 0.01 | 4 | 4 |
| 1.0 | 1 | 4 |

The overview capsule measured 450 metres half-length by 100 metres radius,
retained all four identities, and used an oriented rectangle plus two circular
caps rather than an enclosing circle.

The run also retained the prior causal controls: a proven disabled shot produced
nothing; hostile-near warned exactly once; hostile-far and friendly-near did
not; origin uncertainty narrowed and confirmed at the gun; observations
expired; stop and cleanup removed owned resources.

Calibration run 20260828T174254Z-b453020e was rejected because scale 0.5 left
four groups and the aggregate/shape assertions failed. Changing only the
overview endpoint to scale 1.0 produced the four-to-one transition in
20260828T174807Z-5b0778c6; the final run repeated it with the feature-owned
proposition.

## Sacred Texts and evidence

Local dossiers for ctrlMapWorldToScreen, ctrlMapScale, drawEllipse and drawLine
confirmed map projection/scale and drawing APIs, not product policy or
performance.

Package urn:tribunal:evidence-package:20260828T175511Z-44e26fea:1 has file
SHA-256 3d860e9d1c30dd3cc03129fc0fd7aa9a2a3234b1c666cafa8d023b17a2deac4d.
It was ingested twice without second-pass change. Production advanced from 42
packages/43 runs to 43 packages/44 runs and the audit passed.

Reviewed distillation accepted-tribunal-findings-2026-08-28-cbr-observations-1
classified the result **PROJECT-SPECIFIC ONLY**, added no generic claim, and was
idempotent.

## Remaining boundaries

This closes fixed-zone meaning, merge/split/reassignment, walking-barrage
migration, shape-preserving aggregation and the proposed arbitrary cap. It does
not decide warning cadence/re-warning, confirmed-origin decay, observation and
origin audience, authenticated telemetry rejection, client-B/JIP/disconnect,
cross-owner artillery, or a performance limit that has not been measured.
