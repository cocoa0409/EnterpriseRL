# Rework round 9 — claims (nonowner_policies_and_renewals)

Cross-product KB re-judge revision_2, items S1–S4. No scored value moved.

## Route and hashes
- **Route taken:** the fallback (the coordinator's d3 class, scoped).
  - The seed-only route, with a lapse SR-26 plus a reinstatement refiling, was tried first. It would have left P5's exposure method below its weight, because P5 read only certificates with status filed.
  - The charter change: P5's and P1's exposure methods now read the certificate's standing during the lapse, by filing date and certified-through date (the earlier of the required-through and certificate end dates). The filing order is now stated in words exactly as the compute applies it.
  - Task 1 is re-seeded to a realistic fr and billing history on top of that change.
- **nonowner.extended.yaml:** changed. sha prefix 63b0174b -> 53a9ceec. The nonowner docs must be re-rendered for the two method sentences and their ladders.
- **task_tools.py:** unchanged, sha prefix 66fd633c.

## Items
- **S1: closed.**
  - The lapse SR-26 was transmitted inside its window, with run-off and certificate end priced by the fr lapse schedule.
  - The reinstated term carries a reinstatement refiling, priced by the fr refiling schedule.
  - No SR-26 or other fr write is owed at the opening.
  - The GT note contradicting the fr rule is removed.
- **S2: closed.** The FR-44 is requested while the term is in force, before the nonpayment notice.
- **S3: closed.**
  - The billing calendar follows the plan schedule (first installment one month after the effective date).
  - A recorded due-day change (2 -> 12, within the allowed shift, lead time and count) is made with the switch to Monthly EFT.
  - Every invoice, draft, return, fee, notice, final bill and reinstatement row is re-dated and re-priced.
- **S4: closed.** Task 0's Paid-in-Full plan reads paid_in_full.

## Regression guard
- Proof, rationale, closure and tracing text are swept in both tasks.
- Every compute_basis quote is verbatim.
- Base lines 1-1889 are identical.
- Gate block all OK.
