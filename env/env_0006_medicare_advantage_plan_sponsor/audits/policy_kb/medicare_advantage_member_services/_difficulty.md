# KB-doc policy audit — closing checklist for medicare_advantage_member_services (product `advantage`)

Revision 1. Auditor independent of the renderer and of the policy-side auditor. M = 2.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 — Marjorie Calloway, ending the membership | **PASS** (no `KB-RUNTIME RED`) | **PASS** (no `KB-BIJECTION RED`) | **PASS** (no `KB-EXPLICIT RED`) |
| 1 — Rosalind Ashby, restating the denied surgery | **PASS** (no `KB-RUNTIME RED`) | **PASS** (no `KB-BIJECTION RED`) | **PASS** (no `KB-EXPLICIT RED`) |

Files: `audits/runtime_context/medicare_advantage_member_services/{0,1}.md` (`blind_answer` frozen to disk before any source-layer read, then `gt_comparison` appended) and `audits/policy_kb/medicare_advantage_member_services/{0,1}.md` (`source_to_kb`, `kb_to_source`, `bijection_verdict`, `dependency_form`). No older revision existed; nothing was rewritten.

## Closing checklist

- **Audit files correspond one-to-one with the tasks.** Two tasks, four files, revision 1 throughout.
- **Blind isolation held.** Both `blind_answer` sections were written to disk before `advantage.extended.yaml`, `task_tools.py` or any GT field was opened. Only `user_scenario` and `frozen_time` were taken from the task JSON, by explicit single-key print; no recursive grep was ever run with `tasks/*.json` in the match domain. No contamination to disclose on either task.
- **Every scored value was derived, not recovered.** Task 0: 228.60 and 102.80. Task 1: 95.80, 185.05 and 1834.00. All five match the source's `expected` exactly. So do all five fall-back numbers the computation documents give with no factor applied — 0.00 and 160.00 on task 0, 63.40, 229.30 and 0.00 on task 1 — against the source's own `baseline_result` values.
- **Both problem trees were derived from the visible materials alone.** Task 0: two problems, one edge, handled relief-credit then ending. Task 1: three problems, two chained edges, handled withdrawal then restoration then correction. Both directions and both orders match `prerequisite_closure`. Every hop was marked **state-derived**; none was action-named and none pre-solved.
- **Every normative atom of the structured source is entailed by the product's docs.** 11 base policies with their eligibility conditions, temporal bases and per-plan parameter tables; 5 extended `baseline.rule`s with their default constants rendered as figures; 3 retired clauses written as retired, one document each, with nothing retired that the source did not declare. Nothing unborne, nothing borne with changed meaning, no claim from outside the source. The reverse scan found **no** added confirmation, review, notification or procedure, **no** cross-problem operational guidance, and **no** task's opening world state written in as a policy fact.
- **Every prerequisite sentence stands verbatim, in its declared form, on the blocked side and nowhere else.** All three edges are `form: state`. Measured across all 60 documents of all seven published products, each sentence occurs in exactly one document — the hub of the policy it blocks. No depended-on document carries the blocked side's sentence, and the three-deep chain of task 1 is nowhere aggregated. `condition`, `resolved_by`, `fallback_reason` and `effect` have no textual trace.
- **Every declared factor's ladder is carried in full, every tier exact, findable from the records its tier rests on.** All 25 factors swept tier by tier: no tier dropped, merged, rounded or softened; every compound condition carried whole; every window and threshold stated in figures; no method tier compressed. The seven cross-product factors each name the other product by its official name and the kind of record it reads.
- **No route, no aggregated chain, no tool name beyond each policy's own.** Exactly five tool names appear in the corpus, one per hub, each in its own invocation block. Zero hits scanning the 25 factor documents for mistake-framing or tier-assignment language, and zero hits scanning the 5 computation documents for variation hints. The discrete topology holds.
- **The document the history flagged was verified directly.** `corrected_liability_reckoning_ff5f3328.json` reaches a definite figure from baseline prose alone; the out-of-network clause and the combined figure are absent from it (measured: 0 occurrences of `out-of-network`, `out of network`, `combined`, `dialysis`); and a solver who never finds `maximum_out_of_pocket_basis` gets a definite wrong 0.00 rather than the right 1834.00. The repair described in the history is holding.
- **Gates re-run once on the final form**, from the repository root, unchanged from the snapshot supplied with the brief:

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0006_medicare_advantage_plan_sponsor advantage
🔎 DOCS gate  product=advantage profile=extended docs=60 roles={'factor': 25, 'policy': 15, 'baseline': 5, 'hub': 5, 'facet': 10} content[min/mean/max]=1169/2121/3973
   required quantitative keys=136  task_tools=5  prerequisite edges=3
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0006_medicare_advantage_plan_sponsor/tasks/medicare_advantage_member_services
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          16        0  True
1.json          24        0  True
TRACEABILITY OK
```

The `[MANUAL REQUIRED]` line is what this audit answers, and it answers it PASS on both tasks.

- **Write domain respected.** Only these four audit files were written. `docs/advantage/` was last written at 15:58 and this difficulty's `tasks/` at 15:54, both before the first audit file at 16:15; nothing under `docs/`, `tasks/`, `blueprint/`, `skills/` or `erlbench/` was touched. No other `env/` scenario and no sibling difficulty's tasks directory was read.

## Difficulty verdict

**PASS.** Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks. This difficulty's rendering passes the audit.

## Policy-side notes carried forward (latent; none bears on either task's scored solution)

These are recorded for the record and do not change the verdict above. Each was tested against the gold path and found not to touch it.

1. **Dead quantities in two `baseline.rule`s.** `advantage_ext_disenrollment_closing_balance.baseline.rule` defines "the coverage months the plan premium charges standing on the account cover" and "the coverage months the enrollment has been in force"; `advantage_ext_reinstatement_restored_premium.baseline.rule` defines "the whole months since the coverage ended". None is used by its own baseline assembly — each is the condition input of a factor, and each is also carried in that factor's own document, where it is needed. Same class as the `quarterly_coverage_months` key already repaired. The documents are faithful (dropping them would be `KB-BIJECTION RED`), so the defect is source-side. **Latent**: both baselines stay definite and I computed them blind to exactly the source's `baseline_result` values, 160.00 and 229.30.
2. **`advantage_ext_corrected_claim_cost_share.rule` still fuses a factor outcome into a cap sentence** — "…which on a line given out of network by a tier that pays for covered out-of-network care is the combined in- and out-of-network maximum out-of-pocket of the tier held". It does **not** reach the KB, because `baseline.rule` carries only the factor-neutral form and the rendered document carries that alone. **Latent**; recorded so a future re-render does not draw the cap sentence from `rule` instead of `baseline.rule`.
3. **The renderer's lead on `advantage_ext_pending_election_withdrawal_credit.compute_basis`, judged: it costs a reader nothing.** The six entries do hold the whole policy rule rather than the binding sentence, but `compute_basis` is an authoring field with no home in any document, and no over-carriage reached the prose: the four rider/payment factor documents carry exactly their ladders and `withdrawal_credit_reckoning_28e6b3ae` is pure baseline. Reading those five documents alone I reached 95.80 blind, and the baseline alone gave 63.40. **Latent, and on the evidence not worth a repair.**
4. **A comparator used but not defined in its own factor document.** `owed_coverage_month_count_46834521` decides two of its three rows on "the coverage months the enrollment has been in force" without defining it there; the definition sits in another extended policy's family. **Latent**: on task 0's world, 2 charges do not outnumber that count on any reading of it, so the row it guards is unreached and the outcome is unaffected.

## Coverage gap, stated honestly

This skill is organised per difficulty and audits only the product this difficulty claims, `advantage`. Cross-product contradictions are outside its detection range — structurally suppressed by the render skill's requirement that every document name its own official product name and by each difficulty's policy content being single-homed, but not proved absent. Any base-type product claimed by no difficulty is entirely outside this audit's scope.
