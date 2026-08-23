# Reconnaissance — NON-AUTHORITATIVE

> **Nothing in this directory is accepted knowledge.**
>
> These are code-archaeology notes produced *before* any canonical review. They
> record where to look, which engine mechanisms are involved, what the Sacred
> Texts say about those mechanisms, what the code appears to assume, and which
> questions only a controlled Tribunal experiment can answer.
>
> They do **not** classify features, do **not** establish contracts, do **not**
> change any inventory status, and must **never** be cited as evidence.

## What these documents are

The canonical program ([`../feature-review-program.md`](../feature-review-program.md))
asks a reviewer to identify the real Arma/ACE/CBA mechanisms a feature uses and
retrieve their Sacred Texts *before* substantive investigation. That retrieval
is repeatable but slow, and it is currently redone from scratch for every
review. These notes pre-stage that step for the surfaces that are still
unreviewed or only partially covered, so a future review starts from a warm
map instead of a cold one.

## What these documents are not

* Not a review. No document here answers the canonical 12 questions, and none
  assigns a review outcome (`KEEP`, `REFINE`, `REWRITE`, `NEEDS EXPERIMENTATION`,
  `DEFER`, `RETIRE`).
* Not coverage. No claim here has been proven by a run.
* Not a defect list. An observation labelled *suspicious* is a hypothesis about
  reachable code, not a confirmed bug, and is never grounds for changing runtime
  behavior on its own.
* Not a queue. [`../pontifex-feature-inventory.md`](../pontifex-feature-inventory.md)
  remains the only review queue and the only coverage record.

## Epistemic grading used throughout

Each claim carries its strongest available support, and no stronger:

| Grade | Meaning |
| --- | --- |
| **BIKI** | Canonical upstream documentation retrieved through Sacred Texts. Documentation attests what the wiki says; it is not engine proof. |
| **COMMUNITY** | An attributed, unverified community report from the BIKI mirror. Never a fact. |
| **LEDGER-CONJECTURE** | An open conjecture already recorded in the knowledge ledger. |
| **CODE** | Directly readable from the repository at the cited path. |
| **INFERENCE** | A reading that combines CODE with BIKI/COMMUNITY. Plausible, unproven, and the usual source of a characterization question. |

A *characterization question* is always the terminal state of an INFERENCE.
None of them may be answered by reasoning; each needs a controlled A/B whose
other variables are held fixed.

## Contents

* [`pontifex-remaining-feature-recon-2026-08-23.md`](pontifex-remaining-feature-recon-2026-08-23.md)
  — per-surface reconnaissance for the remaining unreviewed and partially
  covered features.
* [`pontifex-inventory-source-audit-2026-08-23.md`](pontifex-inventory-source-audit-2026-08-23.md)
  — inventory-versus-source audit: entries that are missing, stale, or
  inconsistent with the tree.

## Provenance

Produced against `fa040a2` with a clean worktree. Sacred Texts retrieved from
`/mnt/services/arma-knowledge` with `--offline`, resolved against Arma 3 2.22
stable; a small number of pages were read directly from the accepted
`/mnt/services/biki-mirror` corpus where the ledger has no alias for the
subject (notably the Event Handlers and Mission Event Handlers pages).

No runtime code, test, Tribunal scenario, evidence package, or accepted review
was modified in producing these notes.
