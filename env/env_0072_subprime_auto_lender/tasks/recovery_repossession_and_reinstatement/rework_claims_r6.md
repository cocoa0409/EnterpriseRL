# rework claims, round 6 (policy_kb kb_round2 S1; S2 accepted residue, not addressed)

Bounded exhaustive seed pass. Every seeded contract row of both worlds was re-priced as of its own date, using the published contract documents: late_charge_amount_computation, autopay_late_charge_relief, first_delinquency_late_charge_relief, late_charge_base_amount_by_installment, state_late_charge_schedule, returned_payment_fee_computation, restriction_review_charge, subsequent_return_charge, bank_charge_recovery_on_returns, failed_payment_offset, return_reason_charge, returned_item_fee_schedule_by_amount and returned_payment_fee_booking. The auditor's readings were reproduced independently; none is disputed.

- S1 direct, task 0 late charges (six rows) → Each is now the published amount: 5.0% of the installment, reduced once by the combined autopay reduction (count of autopay drafts in the rolling 12 months, returned ones included) and first-delinquency reduction (count of late charges in the rolling 12 months), rounded once.
- S1 direct, task 0 returned-payment fee of the second 2026 return → Now the tier fee plus the restriction review charge and the subsequent-return charge, less the autopay offset. WI has no bank-charge recovery or cap. The first return's fee was re-checked and is unchanged.
- S1 direct, task 1 late charges (two rows) → Same published computation. The GA schedule rate does not apply because the contract was signed before its schedule date.
- S1 direct, task 1 returned-payment fee → Now the tier fee plus the restriction review charge and the GA bank-charge recovery for an ACH return, less the autopay offset, within the GA cap.
- S1 derived, fee settlements → The fee portions and fee-settlement rows of the payments that settled those fees, and those payments' amounts, follow the new fees. These are the task 0 2025 reinstatement payment and both 2026 MoneyGram repayments, and the task 1 2024 MoneyGram repayment. Their interest and principal portions are unchanged because the waterfall applies fees after installment credit.
- S1 derived, contracts' fees_due → Both now equal assessed minus settled fees on the ledger.
- S1 derived, right-to-cure stated amounts (task 0, both cases) → Re-priced under the base cure rule: installments past due on the mailing date plus fees due on that date.
- S1 derived, notice of intent to sell stated amounts → The task 0 2025 notice and the task 1 2026 notice were re-priced under the frozen sale-notice rule's mailing-date formula. Sale periods are unchanged.
- Proof text → The seed-consistency checks, design_rationale SEED lines and every stated equation that quoted the old fee figures were updated.
- Scored values → None moved: no scored computation reads a contract fee amount. The certified-funds flag depends on the count of returns, not their amounts.
- Frozen files → recovery.extended.yaml and task_tools.py are byte-identical to the frozen hashes.
