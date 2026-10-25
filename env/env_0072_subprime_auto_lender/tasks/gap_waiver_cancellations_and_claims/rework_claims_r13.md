# rework_claims_r13 — gap_waiver_cancellations_and_claims (audit revision_12: C14, C4; task 0 reimbursement only)

I followed the coordinator's route. Task 1, task_tools.py and every other policy are unchanged, and tasks/1.json is
byte-identical. Task 0's world is not re-seeded and its gold is unchanged. In tasks/0.json only the reimbursement's
computation entry, its call trace and its rationale lines changed.

## Baseline (softened)

- The reimbursement is the deductible the primary insurer actually withheld, up to the plan maximum. It is bounded by
  one cap: the declared deductible of the declarations read. The standard is the latest accepted proof, taking the
  lower of its two deductibles.
- A deductible the insurer did not withhold is never reimbursed.
- The round-12 standard bar is removed ("a withheld deductible above the borrower maximum … is not reimbursed").

## Factors

All four own their reads. The borrower maximum and the settling insurer (from the claim row) are plain bindings,
each stated once. No factor references what another factor selects, and no sentence combines factor outputs.

- **`pd_policy_at_loss`** (parameter; merged selection of the declarations read):
  - the latest proof naming the settling insurer, when it was accepted or was rejected only for its deductible;
  - no declarations, when it was rejected for any other reason;
  - otherwise, the latest accepted proof.
- **`pd_paying_coverage`** (parameter): collision, comprehensive, or the lower of the two.
- **`pd_allowance_test`** (method; records only, comparing the withheld amount with the borrower maximum and checking
  whether a proof names the settling insurer):
  - never more than the borrower maximum;
  - nothing reimbursed, for a policy never put before the company;
  - no bound.
- **`pd_policy_disclosure`** (method; the review date of the latest proof naming the settling insurer, compared with
  the date of loss):
  - reviewed on or before the loss: the insurance on file does not bound the reimbursement;
  - reviewed only after it: never more than the borrower maximum;
  - no such proof: never more than the lower deductible of the policy on file's latest accepted proof, which is the
    insurance the company held.

## C14 (gating)

- `pd_allowance_test` no longer depends on any other factor's tier. It acts on the reimbursement whatever the
  disclosure method decides.
- Pair probes ran on twelve world variants, with one factor at its baseline and another toggled:
  - every ordered pair has a world where the toggled factor moves the result;
  - no factor is inert through a single other factor's tier.

## C4 (counts)

- On task 0, each of the four factors moves the result when its own baseline is substituted, and check_compute
  agrees.
- Disclosed limitation: with all three other factors at baseline, `pd_policy_disclosure`'s standard (the policy on
  file) coincides on every open tracking record with the declarations standard (the latest accepted proof). It also
  masks `pd_paying_coverage` there. Both factors bear weight as soon as any one other factor leaves its baseline.
- Why this limit exists: in a lesser-of-caps formula a factor can bear weight only by binding, or by having a
  standard tighter than gold. The allowance cap binds on task 0, so the fourth factor needs a tighter standard. The
  only tighter, record-backed one is the insurance on file.
