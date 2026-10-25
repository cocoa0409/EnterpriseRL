# Rework claims, round 5 (store_card_billing_and_disputes)

| item | status | location changed |
|---|---|---|
| R4-1 | closed | card_ext_line_increase: prerequisite[0].policy_source and the same sentence in rule (referral stated verbatim), rule minimum sentence (two-or-more clause removed), compute acct_open / referral / cure_unmet / result, prerequisite[0].condition; card_ext_catch_up_payment: rule (referral sentence), compute acct_open / referral / cure_unmet, compute_basis; tasks/0.json design_rationale and line plain-binding trace |
| R4-2 (a) | closed | card_ext_credit_balance_refund: merchant credit sentences in rule, compute mc_returns_12 / mc_out_1 / mc_blind_1 / credit_hold, merchant_credit_hold ladder and bindings; tasks/1.json initial_state (the recent merchant credit is unreferenced, own reference), evaluation_criteria trace, computations, seed_consistency, user_scenario, design_rationale |
| R4-2 (b) | closed | card_ext_credit_balance_refund: payment sentences in rule, baseline.rule, params, compute pay_* / n12_* / n1_* / p1_* / payment_hold, factor payment_clearing (replaces clearing_period), inputs.history; tasks/1.json gold refund, factor_trace, factor_sensitivity, prerequisite_closure texts, necessity text, design_rationale |
| R4-2 class sweep | closed | card_ext_catch_up_payment: shortfall mailed tier summed over the month (rule, compute cure_mail_1 / shortfall, params, shortfall_measure ladder and bindings) |
| O-14 | kept | none |
| O-15 | closed | tasks/1.json initial_state (merchant credit transaction reference) |
| O-16 | kept | none |
| O-17 | closed | card_ext_duplicate_final_credit: settled_principal ladder method |

Probe table and decisions are in tasks/store_card_billing_and_disputes/worklog.md under "REWORK round 5".
