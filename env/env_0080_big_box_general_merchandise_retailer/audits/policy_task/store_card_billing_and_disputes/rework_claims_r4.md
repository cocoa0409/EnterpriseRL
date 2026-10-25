# Rework claims, round 4 (store_card_billing_and_disputes)

| item | status | location changed |
|---|---|---|
| R3-1 | closed | card_ext_duplicate_final_credit: overwrite[card_evt_late_and_returned_fees].replaced_by and the same sentence in rule (base reversal restated in force wherever the late fee carried by the error is nothing, and for every other fee); error_late_fee ladder |
| R3-2 | closed | card_ext_catch_up_payment: rule (mailed tier same-day tie, entered first), compute_basis of last_cure_channel / last_cure_date / shortfall, shortfall_measure ladder |
| R3-3 | closed | card_ext_catch_up_payment: rule (new missed-statement minimum sentence), compute (s_disp_n, s_disp_id, s_disp_amt, s_disp_date, s_disp_res, m_min; cure_unmet and shortfall read m_min), shortfall_measure baseline; card_ext_line_increase: rule (same minimum sentence after the prerequisite sentence), compute (same bindings; cure_unmet reads m_min), prerequisite[0].condition; tasks/0.json plain-binding traces |
| R3-4 | closed | card_ext_credit_balance_refund: dispute_interest_exposure removed from rule, compute, compute_basis and factors; new parameter factor merchant_credit_hold (rule sentences, params unmatched_credit_days / outside_credit_days, compute mc_* / credit_days / credit_hold, result, inputs.history); overwrite[card_evt_payments].replaced_by and rule (held amounts refunded within the base business days of a written request); tasks/1.json initial_state (one Publix merchant credit against a purchase on the account, holding balance), evaluation_criteria refund amount and trace, computations factor_trace / factor_sensitivity / baseline_result, prerequisite_closure texts, seed_consistency, user_scenario, design_rationale |
| R3-5 | closed (class) | every factor ladder in all five policies: each `when` is now a verbatim span of its rule, text values and methods verbatim; tier_taken strings in tasks/0.json and tasks/1.json remapped |
| O-11 | kept | none (no read touches order lines; task 0 left as passed) |
| O-12 | disputed | none (an uncleared mailed payment does not cure the missed statement until it clears; reasoning in worklog) |
| O-13 | kept | none (second tier floored at zero; reasoning in worklog) |

Probe table, defining-sentence table and the sweep record are in tasks/store_card_billing_and_disputes/worklog.md under "REWORK round 4".
