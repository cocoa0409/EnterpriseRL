# Rework round 13 claims (bounded: CG-36 only)

- CG-36: in all six places, the down-payment-premium read no longer depends on the certificate's current status:
  - draft notice, owner branch;
  - draft notice, non-owner branch;
  - deposit;
  - makeup advance;
  - switch down payment;
  - switch old schedule.
  The single exact read is `XSUM('fr','fr_filing_transactions','amount', event_type='fr_filing_fee_assessed', posted_date=F('enrolled_date'))`: every certificate filing fee assessed on the filing ledger on the day the plan was set up, tied by posting date. The sentence now reads "every certificate filing fee the filing ledger shows assessed on the day the plan was set up" in every rule, compute_basis quote and baseline.
  - The billing ledger carries no filing-fee row for the down payment. The fee is billed inside the down payment amount, so the fr ledger row dated the set-up day is the exact record.

Probe (scratch copy), task 0's plan with the SR-22 later moved to cancellation_filed:
- Seed (fee assessed 2026-11-25, after set-up): the schedule down payment premium is the same in all six reads before and after the status change.
- Variant with the fee assessed on the set-up day and the down payment including it: the premium is the same while filed and after cancellation_filed. The set-up fee is subtracted in both states.

Nothing else changed; scored values unchanged. Carried, not regressed: every item closed in rounds 1-12.
