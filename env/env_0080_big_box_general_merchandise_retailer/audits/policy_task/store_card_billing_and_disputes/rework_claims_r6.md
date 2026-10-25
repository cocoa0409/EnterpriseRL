# Rework claims, round 6 (store_card_billing_and_disputes)

| item | status | location changed |
|---|---|---|
| R5-1 | closed | card_ext_line_increase: rule and prerequisite[0].policy_source (referral names the missed statement's own most recent billing-error dispute), prerequisite[0].condition, compute referral (acct_open removed), compute_basis; card_ext_catch_up_payment: rule (referral sentence), compute referral (acct_open removed), compute_basis; tasks/0.json design_rationale |
| R5-2 | closed | card_ext_credit_balance_refund: rule (one plain sentence on the payment record; both hold sentences read it), compute returns_12 (pay_returns_12 / mc_returns_12 removed), compute_basis, payment_clearing and merchant_credit_hold ladders and bindings; tasks/1.json factor_trace, factor_sensitivity tier_taken, design_rationale |
| O-18 | kept | none |
| O-19 | closed in part | card_ext_credit_balance_refund: merchant_credit_hold effect method; payment_clearing kept parameter (reason in worklog) |
| O-20 | closed | card_ext_credit_balance_refund: rule sentence defining an unreferenced merchant credit by the empty reference the schema allows |

Probe table and decisions are in tasks/store_card_billing_and_disputes/worklog.md under "REWORK round 6".
