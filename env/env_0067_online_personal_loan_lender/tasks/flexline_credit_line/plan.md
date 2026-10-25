# plan — flexline_credit_line (env_0067), M=2 (rework round 3)

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3, factor_counts=[6,4,5,5]
- task 1: prerequisite_problems=3, factor_counts=[5,5,5,5]

Identifier band: last-four values 4000-4999; persona surnames M-P; emails from the persona's own name.

## Task 0 — close an active, past-due FlexLine Standard to new draws (root, owner=user)
Root  line_ext_close_to_draws_payment  close_line_to_draws_7539d675 (user)        6 factors  computes repayment_payment
  <- line_ext_late_fee                 assess_late_fee_ba469c06 (agent)           5 factors  value_input (late_term_cut)
  <- line_ext_limit_review             apply_limit_review_5d0a2d8e (agent)        5 factors  value_input (payment_method_code)
  <- line_ext_workout_fee_relief       grant_workout_fee_relief_903cc630 (agent)  4 factors  value_input (conversion_balance)
       <- line_ext_late_fee            value_input (relief_way)
World: Standard line, active, 28 days past due on the 2026-09-18 minimum after a partial payment in grace (Standard freezes
at 30 days); late fees 2025-07 and 2026-03, returns 2025-09 and 2026-02, courtesy waiver 2025-09; current Grade-C loan with a
2026-09 late fee (cross-difficulty). Customer asks only to close the line to new draws and keep paying monthly.

## Task 1 — authorize the hard inquiry on a pending FlexLine Plus increase (root, owner=user)
Root  line_ext_limit_increase          authorize_limit_increase_21546d5b (user)   5 factors  computes approved_limit
  <- line_ext_returned_payment_fee     assess_returned_payment_fee_0fd8e99d (agent) 5 factors value_input (returned_fee_share)
  <- line_ext_backbilled_draw_fee      assess_draw_fee_4f046c6c (agent)           5 factors  value_input (recent_draw_charges)
  <- line_ext_returned_fee_relief      grant_returned_fee_relief_6fbb0f32 (agent) 5 factors  value_input (usage_balance)
       <- line_ext_returned_payment_fee value_input (relieved_fee)
World: Plus line, current; 2026-09-14 AutoPay payment returned R02 (closed account) on 2026-09-16 with no fee entry, replaced
in part on 2026-09-23 from the new verified account; 2026-09-10 draw posted without its fee; one late fee 2026-02; Grade-B loan
with a same-day R02 return and fee (cross-difficulty); increase request of 2026-10-09 pending the borrower's inquiry consent.

Scratch: /tmp/flexline_credit_line_0067/ only. XF_recipe.md 14 points applied per policy, recorded in worklog.md.
