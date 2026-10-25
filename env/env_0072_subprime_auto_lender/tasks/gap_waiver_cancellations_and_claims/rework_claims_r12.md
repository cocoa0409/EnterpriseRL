# rework_claims_r12 — gap_waiver_cancellations_and_claims (KB revision_2: K1, S3; task 0 reimbursement only)

Task 1, task_tools.py and every policy other than the Premier deductible reimbursement are unchanged. tasks/1.json is
byte-identical to round 11. Task 0's world is not re-seeded. tasks/0.json changes only in the reimbursement's
computation entry, its call trace and the rationale lines about it. The other three scored figures and their traces
are unchanged.

## K1 / S3 — no sentence combines two factors' outputs

I took route (b) from the coordinator's notes.

- **Merged factor.** `pd_policy_at_loss` now makes the whole selection of the declarations read, and each tier is a
  complete selection:
  - the latest proof naming the settling insurer, when it was accepted or was rejected only for a deductible above
    what the contract allows;
  - no declarations, when it was rejected for any other reason;
  - otherwise, the latest accepted proof of the policy on file (the standard).
- **Removed.** `pd_proof_standing` and the round-11 combination sentence are gone.
- **What each document carries.**
  - The computation document carries only the standard. It does not say that the insurer or the review standing can
    vary.
  - Each factor document carries only its own sentence.
  - No rule sentence assembles the outputs of two factors.

## Freed slot — `pd_policy_disclosure` (method)

- It is record-backed on the review date of the latest proof naming the settling insurer.
- It acts on its own against a new baseline sentence: "As the standard, a withheld deductible above the borrower
  maximum deductible … of the collateral protection plan the tracking record carries … is not reimbursed."
- Its tiers:
  - that proof was reviewed on or before the date of loss: the deductible is not barred;
  - it was reviewed only after the date of loss: the reimbursement is never more than the borrower maximum;
  - no proof names that insurer: nothing is reimbursed.
- Its bindings are its own reads. It names no other factor's decision, and its effect is a bar or a bound on the
  reimbursement, which combines with the other bounds without an assembly sentence.

## `pd_allowance_test` (method)

- It still bounds a withheld deductible above the borrower maximum, now by how the settling insurer's latest proof was
  reviewed:
  - rejected for its deductible (the company told the borrower so): never more than the borrower maximum;
  - accepted: never more than the higher of that proof's deductibles;
  - otherwise: no bound.
- Its former void tier is now the disclosure method's, so no case is decided twice.
- It owns all of its reads.

## Closures kept

- The deductible counted is still the deductible the primary insurer actually withheld, up to the plan maximum, and a
  deductible not withheld is never reimbursed.
- No loss-date window is used. The disclosure test is an on-or-before ordering against the date of loss, not a window.
- Labels are honest: two parameters and two methods.
- No factor reads another factor's bindings.

## Probes

Every factor moves the result on its own on task 0. The probe cases are listed in the plan.md round-12 table. Proof
text in the rule, basis, traces and rationale was swept for the removed factor and sentence.
