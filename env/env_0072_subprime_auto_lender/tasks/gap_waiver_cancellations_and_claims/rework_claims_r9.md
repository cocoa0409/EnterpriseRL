# rework_claims_r9 — gap_waiver_cancellations_and_claims (audit revision_8; task 0 reimbursement only)

Task 1, task_tools.py and the starting balance, excluded total and worksheet benefit policies are unchanged. Task 0's
world is not re-seeded. tasks/0.json changes only in the reimbursement's computation entry, its call trace, the
tracking-record read note and the rationale's reimbursement lines.

## C1 — the reimbursement's standard method

- The deductible the reimbursement counts is now the base's own figure in every case: the deductible the primary
  insurer actually deducted, as the claim's deductible withheld shows it, up to deductible_reimbursement_max_usd.
- Removed:
  - the baseline sentence "The deductible the Premier reimbursement counts is the lower of the comprehensive and
    collision deductibles on the latest proof …";
  - `pd_deductible_counted` with its "no settlement figures yet" fall-through.
- The rule states outright: "a deductible the insurer did not withhold is never reimbursed". With nothing withheld,
  the reimbursement is 0.00 under every factor tier.
- The only other element of the standard is a check against the declarations, which can only lower the figure. The
  reimbursement is never more than the deductible on the declarations it reads; as the standard, those are the latest
  accepted proof of the policy on file on the tracking record. With no declarations read, the standard is exactly the
  base's figure.

## C4 — fourth factor

- New `pd_proof_standing` (parameter, cross-difficulty CPI, record-backed on the review result of the settling
  insurer's latest proof). Its ladder:
  - rejected only for a deductible above what the contract allows: that insurer's latest proof is read whatever its
    result, because its declarations are complete and show the policy's deductibles;
  - rejected for any other reason: no declarations are read;
  - otherwise: accepted proofs only, falling back to the policy on file's.
- `pd_policy_at_loss` now decides only whose declarations are read:
  - the settling insurer's;
  - any insurer's when the tracking record has no policy on file;
  - otherwise the insurer of the policy on file.
  It owns a read of the tracking record's policy on file.
- `pd_paying_coverage` and `pd_allowance_test` (cap / void / none) are unchanged.
- Independence:
  - No factor reads another factor's bindings.
  - The count of proofs naming the settling insurer and the policy-on-file insurer are plain bindings, each stated
    once.
  - The candidate declarations are plain reads; plain bindings combine them.
- Each factor moves the result alone on task 0. The probes for the accepted, other-rejection, void, no-policy-on-file,
  no-tracking, nothing-withheld and comprehensive cases are in plan.md, round 9 table.

## Note on the coordinator's literal baseline

A standard of only "withheld up to the plan maximum" cannot carry four weight-bearing factors on any world. Every
honest deductible term (declarations, coverage, allowance) is a ceiling on that one figure. With bare-minimum
standards, only the tightest ceiling moves the result, and the other factors become gated. I therefore kept the
counted deductible equal to the base's figure, and placed the factors' standards inside the declarations check. That
check only lowers the figure and never reimburses a deductible that was not withheld.

## Unchanged and still closed

C2, C3, C11–C15 and the bl member of C1 stay closed. Placement is unchanged: 4 / 6 / 6 / 6. Proof text in the rule,
basis, baseline, traces and rationale was swept for the removed sentences.
