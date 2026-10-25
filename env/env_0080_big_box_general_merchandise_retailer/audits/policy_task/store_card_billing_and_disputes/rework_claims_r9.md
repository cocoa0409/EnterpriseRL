# Rework claims, round 9 (store_card_billing_and_disputes; renderer STOP render_r1.md)

| item | status | location changed |
|---|---|---|
| M1 | closed | card_ext_catch_up_payment: rule restoration fee sentence (floor stated), compute_basis window_fees / fee_add, restoration_fee ladder |
| M2 | closed | card_ext_credit_balance_refund: rule payment clearing sentence (floor stated), compute_basis, payment_clearing ladder value |
| M3 | closed | card_ext_line_increase: rule usage sentence, low-use tier (floor stated), compute_basis use_add, usage_line_addition ladder |
| M4 | closed | card_ext_line_increase: rule usage sentence, both tiers (cent rounding stated), compute_basis use_add, usage_line_addition ladder |
| M class sweep | closed | card_ext_duplicate_final_credit and card_ext_catch_up_payment: standing late fee sentences (floor stated); card_ext_first_late_fee_courtesy: standing part sentence (floor stated); their compute_basis entries |
| P1 | closed | card_ext_duplicate_final_credit: carried_error_days bindings (post_date, carried_interest) |
| P2 | closed | card_ext_first_late_fee_courtesy: lateness_points bindings (fee_due), coverage_points bindings (fee_paid) |
| P3 | closed | card_ext_credit_balance_refund: residual_interest_hold bindings (latest_stmt, latest_paid) |

Decisions and sweeps are in tasks/store_card_billing_and_disputes/worklog.md under "REWORK round 9".
