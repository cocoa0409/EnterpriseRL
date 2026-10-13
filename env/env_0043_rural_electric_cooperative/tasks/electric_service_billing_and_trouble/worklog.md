# worklog electric_service_billing_and_trouble (M=2)
- draw (draw_counts.py --tasks 2): task0 prerequisite_problems=3 factor_counts=[6,6,5,6]; task1 prerequisite_problems=2 factor_counts=[4,6,5]
- task0 tree: reconnect fee (root, agent) <- reconnection payment (member, user) <- {late charge assessment (agent), meter error refund credit (agent)}
- task0 tools: assess_late_charge_b4948c69, post_meter_error_credit_d380ee62, pay_reconnection_amount_66e1876e (user), reconnect_service_ea86e786
- task0 written; per-task gates green (traceability deferred)
- task1 tools: bill_seasonal_minimum_25412e46, pay_restore_balance_91f3e2ab (user), restore_seasonal_service_78495a78
- task1 written; final suite gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred (KB not published); authoring scripts deleted
- round 2 rework (audit policy_task): G1 G2 G3 G4 G5 G6 G7 G8 G10 G11 G13 G14 G15 T0-1 T1-1 T1-2 O1-b O1-c O1-d and false assertions closed; values task0 3.77 / 39.95 / 983.25 / 115.00, task1 1512.57 / 687.68 / 145.00
- round 3: R2-G1/R2-1 closed - reconnect look-back tiers change the anchor event (connect date / latest return / rolling 12); values unchanged
