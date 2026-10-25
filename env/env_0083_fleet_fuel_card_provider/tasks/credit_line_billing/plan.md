# plan — credit_line_billing (env_0083), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3, factor_counts=[4,5,4,4]
- task 1: prerequisite_problems=1, factor_counts=[6,4]

Write domain: tasks/credit_line_billing/ only. Scratch: /tmp/credit_line_billing_0083/.
Persistence order: plan.md -> credit.extended.yaml (base copy, then one policy at a time) -> task_tools.py (one tool at a time, check_task_tools after each) -> tasks/0.json piecewise -> gates -> task 1.

## Task 0 — Lone Star Plumbing & Drain LLC, Meridian Preferred Fleet Line, monthly cycle (terms 20, grace 3)
Surface goal: temporary limit increase for a busy month (storm-repair contracts).
Tree (root first):
- TEMP  credit_ext_temp_increase (agent; temp increase amount; 5 factors) — root
  - <- PAY  credit_ext_cure_payment (user; portal ACH payment amount; 4 factors)  [value_input: balance the increase is sized on; also the no-past-due wait]
    - <- LATE credit_ext_late_fee (agent; late fee on the statement whose grace days passed; 4 factors) [value_input: balance]
    - <- REV  credit_ext_late_fee_correction (agent; reversal of an earlier late fee figured on an over-stated past-due; 4 factors, mirrors LATE) [value_input: balance]
Cross-difficulty: dispute (open disputed amount left out of the past-due amount), program (purchases for the seasonal need).

## Task 1 — Brazos Valley Produce Co., Meridian Starter Fleet Line (deposit-secured), weekly cycle
Surface goal: fund a bigger deposit so the line can be raised.
Tree:
- DEP credit_ext_deposit_topup (user; deposit amount; 4 factors) — root
  - <- CLI credit_ext_limit_request (agent; requested limit; 6 factors) [value_input: the limit the deposit is figured on]
Cross-difficulty: program purchases (next tier's entry spend), customers.customer_since.

Design notes are kept in worklog.md (factor tables, defining-sentence table, probe table, method-tier table, T1/T2, trigger list).
