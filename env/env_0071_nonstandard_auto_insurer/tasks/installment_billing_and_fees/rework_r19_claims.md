# Rework round 19 claims (bounded: KB audit SRC-1)

- SRC-1: billing_ext_direct_bill_switch now declares a scoped overwrite of base billing_installment_fee_rule's "After a mid-term plan switch, invoices issued from the switch date carry the new plan's fee; invoices already issued keep theirs." (superseded_clause verbatim).
  - replaced_by (verbatim in the rule): "For the first invoice after an owner plan is moved off automatic draft to the Six-Pay Direct Bill Plan at the named insured's request, and only for that invoice, the fee is the one the state fee schedule below sets; after any other mid-term plan switch, and on every later invoice of a moved plan, invoices issued from the switch date carry the new plan's fee, and invoices already issued keep theirs."
  - It is consistent with the sibling exclusions: the switch's installment-fee and invoice-schedule overwrites and the draft notice's fee sentence each name "the first invoice after an owner plan is moved off automatic draft ... at the named insured's request" as the switch's own case.
  - The state fee is kept; it is the company's filed state schedule for direct-bill installments, accepted under XF points 24/25. Scored values unchanged.

Class sweep: every sentence of every base policy in the charter's base_policy_refs, plus billing_down_payment, billing_late_fee_rule, billing_delinquency and billing_premium_posting, was checked against the five rules.
- No other in-force base sentence is departed from without an overwrite.
- Sentences confirmed consistent:
  - the installment schedule's equal installments, due dates, one invoice per installment number and no installments on Paid-in-Full;
  - one installment fee per invoice, and none on plans without installments;
  - the single-payment cap, posting day, partial payments, personal checks and the agent fee (a separate charge, 0.00 on the Monthly plans);
  - switch targets and the switch limit, applied in force alongside the switch;
  - the returned payment's reversal and NSF fee rules, and automatic moves on returned drafts and certified funds, restated as base;
  - the certified-funds methods.

Nothing else changed. Carried, not regressed: every item closed in rounds 1-18.
