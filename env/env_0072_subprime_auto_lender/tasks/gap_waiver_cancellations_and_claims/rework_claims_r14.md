# rework_claims_r14 — gap_waiver_cancellations_and_claims (audit revision_13: C14, C4; task 0 reimbursement only)

Task 1, task_tools.py and every other policy are unchanged, and tasks/1.json is byte-identical. Task 0's world is not
re-seeded and its gold is unchanged. In tasks/0.json only the reimbursement's computation entry, its call trace and
its rationale lines changed.

## C14 / C4 — fourth factor replaced

- **Removed.** `pd_policy_disclosure`, together with its rule sentence and bindings.
- **Added.** `pd_loss_schedule` (parameter), which reads only the claim row's own loss type. It is the Harborline GAP
  Waiver Premier 150 deductible reimbursement schedule, and it caps the baseline directly:

  | Loss the claim shows | Reimbursement maximum |
  |---|---|
  | collision total loss | the plan's deductible_reimbursement_max_usd |
  | unrecovered theft | 500.00 (`theft_reimbursement_max_usd`) |
  | comprehensive total loss, or no loss type shown | 250.00 (`comprehensive_reimbursement_max_usd`) |

  The two figures are policy params. The last row is also the standard. The new baseline sentence states it.
- **Baseline.** The deductible the primary insurer actually withheld, up to the reimbursement maximum, and never more
  than the declared deductible of the declarations read. A deductible not withheld is never reimbursed.
- **Unchanged factors.** `pd_policy_at_loss`, `pd_paying_coverage` and `pd_allowance_test` (cap / void / none on the
  withheld amount against the borrower maximum) are unchanged. Each owns its reads, and no factor references another
  factor's selection.

## Acceptance tests

Both tests pass for all four factors. The table and the stated probe worlds are in plan.md, revision 15.

- **T1.** On task 0, substituting each factor's baseline alone moves the result. check_compute confirms this.
- **T2.** For each factor there is a producible variant of task 0 where, with the other three at baseline, the
  factor's taken tier moves the result.
