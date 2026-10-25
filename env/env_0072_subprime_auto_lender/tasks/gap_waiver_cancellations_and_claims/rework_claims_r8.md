# rework_claims_r8 — gap_waiver_cancellations_and_claims (audit revision_7; task 0 only, task 1 untouched)

Task 1 bundle (tasks/1.json, the Plus policies, task_tools.py) is byte-identical to round 7. Task 0's world is not
re-seeded; only the reimbursement and the starting balance change. Excluded total and worksheet benefit are unchanged.

## C14 / C4 — Premier deductible reimbursement

- **C14 (gated allowance factor).** `pd_contract_allowance` is removed. `pd_allowance_test` reads the borrower maximum
  deductible of the plan the tracking record carries (`CPARAM borrower_max_deductible_usd`) in its own bindings and
  tests it in every tier. The allowance is no longer a separate factor.
- **C14 (factor reading a factor).** The count of proofs naming the settling insurer is a plain binding. One rule
  sentence states it once ("A proof names the insurer that settled the claim when ..."). No factor's bindings list it.
  `pd_policy_at_loss` (its source choice) and `pd_allowance_test` (cap versus void) both read it as a shared plain
  binding. Neither reads the other's bindings.
- **C4 (no method).** The method is again `pd_allowance_test`, with three shapes:
  - cap: the reimbursement is never more than the borrower maximum;
  - void: nothing is reimbursed;
  - none: the allowance does not enter.
- **Fourth factor.** New `pd_deductible_counted` (parameter, record-backed on the claim's settlement figures):
  - with settlement figures and a deductible withheld: the deductible the insurer withheld;
  - with settlement figures and none withheld: 0.00;
  - with no settlement figures yet: the latest accepted proof's lower deductible.
  The baseline counts the latest accepted proof's lower deductible. The baseline and computation sentences state this.
- **Factor checks.** Each factor alone moves the result on task 0. The probes cover the void tier, a missing tracking
  record, an accepted settling proof, absent settlement figures, a 0.00 withheld deductible and a comprehensive loss
  (plan.md, round 8 table).

## C3 — placed premiums in the starting balance

`bl_placed_premiums` is now a method with three different formulas:
- premiums added less refunds credited;
- with no refund credited and an accepted proof reviewed on or after the latest premium's billing date and effective
  inside its billing period: premiums added less that premium's prorated share from the proof's effective date, both
  counted inclusive;
- otherwise: every premium added.

The baseline now adds every premium gross, and the baseline sentence is rewritten to match. A probe reaches the prorated
tier on a task-0 variant with no refund.

## C1 — delinquency interest

The tier that added the account's carried unpaid interest is gone, and the starting balance no longer reads
`unpaid_interest_usd`. `bl_account_interest` is replaced by `bl_payment_interest` (method):
- per-diem interest from the latest payment to the loss at the rate in force;
- when an SCRA cap took effect or ended between that payment and the loss, the days are split at the change, each part
  at its own rate;
- otherwise none.

## C15 — principal over the accrual period

The rule now states that interest accrues on the principal in place over the period. That is the contract's principal
balance with every service-contract refund credited for the total loss added back, since those credits post after the
loss. The computation matches: the principal balance plus the contract's `vsc_refund` ancillary credits when the
service contract was cancelled for `total_loss`. Rounding happens once, at the end. The overwrite tail now names "the
force-placed premiums and the interest from the account's latest payment it carries". Rule, basis, baseline and
overwrite texts were swept for the old sentences.

## Unchanged and still closed

C2, C11, C12, C13 and the window members of C1 stay closed. Placement is as ruled: 4 / 6 / 6 / 6. Proof text was swept
across the task-0 traces, the rationale and the action notes.
