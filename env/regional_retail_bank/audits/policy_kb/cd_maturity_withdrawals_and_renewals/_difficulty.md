# KB-doc audit closing checklist — cd_maturity_withdrawals_and_renewals (product `cd`)

Auditor: independent of the renderer and of the policy-side auditor; read none of `audits/policy_task/`.
Corpus audited: `env/regional_retail_bank/docs/cd/` — 49 documents, sha256 (title+content, path-sorted) `86a0225d6c42ad1a4a4eaa96854f8ad1`.
Tasks: M = 2. Blind audits frozen to disk before any source-layer file was opened; no contamination.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 — Roland Whitacre, overdue renewal then the largest partial withdrawal | **PASS** | **PASS** | **PASS** |
| 1 — Marisol Teague, the owed charge then the restoring deposit | **PASS** | **PASS** | **PASS** |

**Difficulty verdict: PASS.** No `KB-RUNTIME RED`, no `KB-BIJECTION RED`, no `KB-EXPLICIT RED`.

## Closing checklist

- **Audit files correspond one-to-one with the tasks.** `audits/runtime_context/cd_maturity_withdrawals_and_renewals/{0,1}.md` and `audits/policy_kb/cd_maturity_withdrawals_and_renewals/{0,1}.md`. This is revision 1; no earlier revision exists, so nothing was overwritten. Each `blind_answer` was written to disk before the reveal and is unaltered; each `gt_comparison` was appended after.
- **Every normative atom entailed.** All eleven base policies, their measures, all six variants' parameters and all four extended policies correspond losslessly at the level of entailment. Tier tables were verified cell by cell by script against the charter — every numeric, boolean, frequency and list column matches, including the qualifying-checking-tier lists as exact sets. Nothing is unborne, nothing bears a changed meaning, and no claim appears from outside the source (a pattern scan for added confirmations, reviews, notifications and failure procedures returns nothing).
- **The retired surface is exact.** The charter declares eight distinct superseded clauses; the corpus carries eight retirement statements and no ninth, each written as no longer in force and not to be applied, each in a document bearing the subject matter, with the other clauses of those policies still stated as clauses in force.
- **Both prerequisites carried correctly.** Each prerequisite sentence stands verbatim, with its "only after" connective and its declared **state** form, in the hub of the policy it blocks and — verified corpus-wide — in no other document. Each hop is resolvable at the source's strength from that sentence, the depended-on policy's own rules and the records: for task 0 the certificate's `status`, term dates and rate against the frozen date and the ten grace days; for task 1 the ledger's `early_partial` row that no entry's `source_item_id` names. `condition`, `resolved_by` and `fallback_reason` appear in no document.
- **Every declared factor's ladder carried in full.** All eighteen graded clauses were matched against the corpus by script: every tier, every part of every compound condition, every window, threshold, operation, rounding mode and moment is carried verbatim in exactly one document, that factor's own, with named policy constants rendered as figures. The fifteen residual fall-through clauses — including all six that carry the trailing gloss naming the variables the residual ignores — are carried verbatim, none paraphrased into a positive condition anywhere in the corpus; each factor document's condition-and-result table enumerates the residual as its own rows, and all eighteen tables partition their domain exhaustively and disjointly. Each factor is findable from the plain business words its evidence records use, and each names the other product line it reads by its official name.
- **Every worked example recomputed.** All worked readings in all 49 documents are arithmetically correct, including the four the renderer reports repairing before publishing. No silent-but-wrong example remains.
- **All four computation baselines are self-sufficient.** Each carries its `baseline.rule` complete — inputs, defaults, rounding, windows, bases, order and assembly — names every product figure it reads in findable words, adds nothing, and yields a definite fall-back number that differs from the scored answer (task 0: 4.22 / 4.30 and a wrong penalty; task 1: 117.76 and 14500.00). No baseline hints that anything modifies it; no factor document points at a baseline or at another factor. The topology is discrete.
- **No route stated beyond the sentences.** The four task-tool names appear once each, in their own problem's invocation block, and nowhere else. No dependency table, checklist, roadmap, cross-problem procedure or "if unmet, first call X" exists. No state-form sentence is restated as an action. All 49 titles name general subjects; none mirrors a task's situation.
- **The gates.** Per the brief, the auditor ran neither gate; both were run by the orchestrator against the now-complete document tree and their output lines are on record in `0.md`. No document was edited during this audit, so the audited form **is** the form the gates were run against:
  - `DOCS gate product=cd profile=extended docs=49 roles={'factor': 18, 'policy': 13, 'hub': 4, 'baseline': 4, 'facet': 10} … [PASS] mechanical gates … DOCS OK`
  - `TRACEABILITY gate (2 tasks) — 0.json 17 copied / 0 missing / True; 1.json 21 copied / 0 missing / True — TRACEABILITY OK`

## Coverage gap, stated honestly

This audit is organised per difficulty and covers only the product this difficulty claims (`cd`). Cross-product contradictions are outside its detection range: the render skill hard-requires every document to name its own official product name and this difficulty's policy content is single-homed in `cd`, so such contradictions are structurally suppressed rather than proved absent. Base-type products claimed by no difficulty are entirely outside this skill's scope.

## Policy-side notes carried forward (not this skill's verdict)

Four places where the charter's rule text and its `compute` expression differ. The documents render the **rule's** words in every case — the faithful choice — and none of the four changes a scored value in either task. Recorded in `0.md` for the source layer to weigh: the jumbo grade's "holds an active savings or money market account" against a `balance > 0` test; the late-booking allowance's same shape; the owed-charge rate and the lost-principal measure's "auto loan … not past due" against a `status == 'active'` test; and the penalty-days grade's "any other tier", which was checked against `blueprint/products/card.yaml` and found to be the exact complement of the two tiers named, so rule and code agree there.

## Revision history

Revision 1 (2026-09-13, commit 427143d) audited an earlier generation of this scenario: 57 `cd` documents, a workflow task, and the policies `cd_wf_post_grace_renewal_and_add_on`, `cd_ext_penalty_rate_reversal` and `cd_ext_grace_withdrawal_penalty_reversal`, with different frozen times and different task tools. The corpus, the policies and both tasks were regenerated afterwards, so revision 1's findings do not bear on the current tree. Its text is preserved verbatim at the head of each of the four per-task audit files and was not rewritten to accommodate the new documents; the audit recorded here is **revision 2**, filed beneath it under `## revision_2` in each file.
