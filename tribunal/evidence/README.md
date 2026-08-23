# Tribunal Evidence Contract v1

`tribunal.evidence/v1` is the portable, immutable boundary between a Tribunal
characterization and a knowledge consumer. The normative structural schema is
[`tribunal-evidence-v1.schema.json`](tribunal-evidence-v1.schema.json); the
producer-side semantic validator in `contract.py` additionally checks identity
uniqueness, vocabulary, references, execution-state semantics, and integrity.
Unknown fields are deliberately allowed so v1 readers tolerate additive
extensions. Removing a required semantic field is invalid.

This document owns the evidence format, not the feature-review procedure. A
memoryless Pontifex reviewer starts at
[`../docs/feature-review-program.md`](../docs/feature-review-program.md), which
defines when feature semantics may be published, the fresh-run acceptance gate,
`/mnt/services/arma-knowledge` ingestion/idempotency/audit commands, and the
reviewed generic-distillation boundary. Do not invent arms or propositions here
from generic assertion output.

## Model

- `package_id` identifies one published scientific record. `package_revision`
  starts at 1; later revisions name `supersedes_package_id` rather than changing
  accepted bytes.
- `run.id` is Tribunal's native run ID. `execution_state` distinguishes a
  completed experiment (whose `outcome` may be negative) from
  `failed_to_execute` or `cancelled` execution.
- Each scenario has a stable, feature-owned ID and a version that changes when
  its experimental meaning changes. Runs instantiate scenarios; paths do not
  identify them.
- Participants carry extensible roles and runtime facts. Observations name the
  participant that saw the value, and artifacts may name their producer.
- Observations carry a controlled value type, a typed value, an optional arm,
  and raw artifact references. `custom`/`record` values use `schema_id` for
  extension semantics.
- Assertions name a stable definition, assertion type, expected and observed
  values, result, and the observations/artifacts used. An assertion pass is an
  execution fact, never an automatic theorem.
- Experimental arms use `treatment`, `negative_control`, `positive_control`,
  `baseline`, `counterfactual`, or `replicate`. Explicit relationships use
  `COMPARES_WITH`, `CONTROLS_FOR`, `CAUSAL_PAIR_WITH`, or `REPLICATES` and list
  controlled dimensions.
- Proposition evaluations report bounded experimental outcomes and intended
  use. They do not declare truth roles; the consumer applies its proof policy.

## Context and durable references

`context` contains scientifically meaningful product, branch, version/build,
session, server kind, mods, mission, and related runtime facts. It intentionally
does not mirror the process environment.

Source snapshots identify a repository and commit/tree state, plus relevant
path and SHA-256 pairs. Artifact IDs are content-derived SHA-256 URNs and carry
type, hash, compact relative/storage reference, producing participant when
known, and a human description. Source and large artifacts remain in their
repositories/stores.

Stable IDs are based on native run/scenario/definition identities or content,
never package location or database IDs. Moving an identical package does not
change its identity.

## Serialization, integrity, and correction

`tribunal-canonical-json/v1` is UTF-8 JSON serialized with recursively sorted
object keys, no insignificant whitespace, unescaped Unicode, and the standard
JSON representations emitted by Python's `json` encoder. The integrity digest
is SHA-256 over the complete package except `integrity`. Published files are
pretty-printed for inspection; the digest always uses canonical bytes.

The immutable writer accepts an existing file only when its complete published
bytes match. A correction gets a new `package_id`, increments
`package_revision`, names the prior package in `supersedes_package_id`, and uses
publication status `corrected`. Consumers retain both records.

## Production and migration

The normal multiplayer terminal reporter emits `evidence-package.v1.json` next
to `manifest.json` and `results.json`. Generic emission faithfully types legacy
assertion outcomes but does not invent proposition evaluations or causal arms.
Feature scenarios enrich those fields by declaring `Scenario.evidence_contract`.
The reporter publishes those semantics only when the run completed with literal
PASS and exactly that one scenario was selected. Every declared arm assertion
must resolve to a real passing result; missing names fail closed. Failed,
cancelled, timed-out, aggregate, and semantics-free runs remain generic and
cannot publish the feature's propositions or causal relationships.

`tools/convert_accepted_evidence_v1.py` is the one-time migration for the four
accepted APS, CBR, Fabricator, and Vigil runs. Its checked-in packages are in
`packages/`; they preserve the earlier curated boundaries and explicit source
hashes, controls, locality, unresolved questions, and proposition intent.
