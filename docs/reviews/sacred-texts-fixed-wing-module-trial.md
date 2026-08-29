# Sacred Texts live trial — Vigil fixed-wing modules

## Real-work baseline

The inventory selected Vigil fixed-wing Eden/Zeus activation because it was the
highest-priority reviewed-but-uncovered feature and required genuine Arma module,
Sync, curator, locality, position, and UI behavior. Selection was not based on
knowledge-system richness. Work started at Pontifex commit
`b422ad7e5f9a90f9e4af2ce49ee501c38a4c7820`.

Before implementation, direct fixed-wing registry/deploy/strike/logistics paths
were covered, but the configured module handlers had no exact class/owner/
requester/replay boundary. Multiple point modules were order-dependent, Zeus
feedback was broad, and no authentic typed or curator run existed. The canonical
review classified the feature `REFINE BEFORE PERMANENT COVERAGE` and left mixed
Sync, point precedence/altitude, curator authority/audience, target cardinality,
and disposal/idempotence unresolved. Established product decisions authorized
assigned curators, limited feedback to the placing curator, required idempotence,
and selected the nearest relevant ingress/egress among multiple points.

## Sacred Texts before feature work

The supported `arma-knowledge dossier` interface was queried before new BIKI or
web research for `CuratorObjectPlaced`, `synchronizedObjects`,
`getAssignedCuratorLogic`, `Module Framework`, `getPosASL`, then for
`curatorMouseOver`, `addCuratorEditableObjects`, `distance2D`, and `attachedTo`.

- `synchronizedObjects` returned current BIKI revision 377127 and the important
  restriction that it works on triggers/entities with AI, including logics. This
  prevented assuming arbitrary objects were valid Sync sources.
- `getAssignedCuratorLogic` returned current canonical authority semantics with
  provenance to BIKI revision 340929.
- `curatorMouseOver` precisely distinguished `[]`, `[""]`, and
  `[typeName, object]`; this became the fail-closed pre-click identity oracle.
- `addCuratorEditableObjects`, `distance2D`, and `attachedTo` supplied applicable
  signatures/meaning and direct source provenance.
- `getPosASL` supplied current ASL meaning but also an ancient Arma 1 stacked-
  object community note with unknown applicability. It was not promoted into the
  design.
- `CuratorObjectPlaced` and `Module Framework` did not resolve as subjects or
  aliases. No prior Tribunal evidence was present (`evidence_package=0`). The
  default release context reported Arma 3 2.20, older than the tested runtime.

The first call also exposed a missing `concept_relationship` migration. Friction
was recorded before using the documented `migrate`, `audit`, and `counts`
commands; no retrieval redesign was attempted.

## What retrieval changed before more investigation

It saved time on Sync applicability and made assigned-curator identity plus
exact hover state first-class requirements. It prevented treating a registry
row, broad notification, or screen coordinate as proof of authorized placement.
It did not answer configured module dispatch locality, client-owned curator logic
ownership, large-aircraft curator acquisition, current-runtime applicability, or
Pontifex product policy; those required repository inspection and controlled
Arma runs.

## Controlled characterization

`vigil-fixed-wing-modules` uses two exact asset modules with native Syncs, two
ingress modules, two egress modules, two equal unsynchronized/control planes,
one current authenticated player, and one assigned curator. Independent source
net IDs are captured before the product deletes registered planes. Consequential
deploy/RTB state independently records the nearest selected points. A real Zeus
display selects the configured module and authenticated RFB input clicks only
after `curatorMouseOver` resolves the exact target.

The accepted path correlates module class, logic/plane/curator/requester owner,
operation, registry row, placer-only result, client replica, and cleanup. A
delivered replay and a wrong-class player object are required to reach explicit
rejection without a fourth registry row. The scenario declares five Evidence
Contract arms, two causal relationships, three bounded propositions, participant
roles/locality, applicability, and the client-N limitation.

Runtime investigation established two useful fixture facts. A server-side
curator initially remained assigned to the pre-respawn player; the fixture must
bind the current `allPlayers` object by the runner-authenticated owner. Also, an
A-10's curator glyph did not resolve from either physical surface or object-
origin projection despite exact editability. A smaller valid civil `Plane`
resolved. Tribunal now accepts a bounded list of data-derived cursor candidates,
but still refuses to click until the mission reports the exact target. This is a
fixture capability, not a product claim that large planes are unsupported.

## Complete-loop evaluation

1. **Time saved?** Yes, modestly: Sync eligibility, curator assignment, hover
   return shapes, and position/distance semantics did not need manual rediscovery.
2. **Mistake prevented?** Yes: arbitrary Sync-source assumptions and a visual-
   coordinate-only Zeus PASS were avoided.
3. **Important omissions?** Yes: module-event aliases, native dispatch/locality,
   current runtime version, and existing Pontifex/Tribunal facts were absent.
4. **Misleading content?** Nothing directly false, but the Arma 1 `getPosASL`
   note and 2.20 context needed explicit applicability skepticism.
5. **Breadth?** Command dossiers were appropriately narrow; concept discovery
   was too narrow because natural module/event names failed rather than routing
   to related canonical subjects.
6. **Provenance?** Yes. BIKI revision, timestamp, fragment, mirror locator, and
   hash made deeper inspection straightforward.
7. **Evidence duplication?** Some. Scenario authors must explicitly repeat arm,
   proposition, and assertion mappings, but the duplication is purposeful and
   statically checked. Automatic publication removed a separate converter step.
8. **Formal mapping?** Yes for one literal passing scenario: exact assertions map
   cleanly to arms, observations, relationships, and proposition evaluations.
9. **Post-work accuracy?** Evaluated after idempotent ingestion below; the new
   product subject must remain scoped to this one-client exact-valid contract.
10. **Next-agent readiness?** Materially better if retrieval exposes the new
    product subject: it should distinguish proven dispatch/authority/nearest-
    point behavior from mixed-Sync, altitude, large-plane fixture, and client-N
    unknowns.

## Ingestion and after-query result

Fresh run `20260822T201311Z-cb69f3fa` passed 13/0 server and 9/0 client
assertions (9 and 5 feature assertions after smoke), passed its authentic RFB
curator placement, emitted a valid `tribunal.evidence/v1` package, and removed
its client, server, network, and run state. The package declared five arms, two
causal relationships, 22 assertion observations, and three demonstrated
`primary_result` propositions.

The first ingestion attempt exposed two integration facts without committing
partial state: evidence assertion instances from two participants may share a
reusable definition ID, and bulk-corpus BIKI concepts use stable
`biki-page:<id>` keys rather than title-derived keys. The importer now keys
artifacts by unique result-instance ID while retaining the definition in the
payload, and the scenario names the six actual context concepts. Ingesting the
corrected immutable package three times returned the same 1 package, 1 run, 22
assertions/observations, 3 proofs, and 3 judgments; database cardinalities
remained one package and one run. The full knowledge audit remained accepted.

The post-work dossier resolves the new canonical product subject and adds three
THEOREM judgments with exact run, commit, artifact, engine/build, hash, and
one-client context. It also follows the six implementation-context relationships
to applicable BIKI documentation. Compared with the before query, it now tells a
future reviewer exactly what Eden aggregation, nearest-point selection, and
assigned-curator authorization/idempotence were demonstrated. Applicability is
honestly shown as `HISTORICAL`, because the repository's default release context
still says 2.20 while the controlled run records 2.22.153995; client-N and the
other bounded follow-ups remain unresolved rather than being promoted.

Overall, the live trial succeeded. It materially improved the review and future
retrieval, while also exposing discoverability, release-context freshness, and
package-directory ergonomics as non-blocking infrastructure follow-ups.

## Recommendation

Improve subject/alias discovery for event and framework concepts and refresh the
default current-version context before broader infrastructure work. Retrieval
should also surface closely related product Tribunal subjects once ingested.
Do not bulk-import historical runs or infer scientific intent from generic
assertions.
