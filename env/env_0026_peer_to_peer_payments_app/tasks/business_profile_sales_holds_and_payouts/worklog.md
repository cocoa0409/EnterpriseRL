# worklog — business_profile_sales_holds_and_payouts (M=2)

## Step 0 — draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[4, 6]
- task 1: prerequisite_problems=2, factor_counts=[6, 6, 4]

## Asset plan (claimed task by task, pairwise disjoint)
- task 0: root business_ext_instant_payout_amount (6 factors, owner=user send_instant_payout_0ea58e95)
          <- business_ext_subscription_month_charge (4 factors, agent book_subscription_fee_2324701e), value_input on balance
- task 1 (reserved headroom): root business_ext_bank_payout_amount (6 factors, owner=user pay_out_to_bank_7d50e7f4)
          <- business_ext_chargeback_fee_charge (6, agent book_chargeback_fee_9ab6815a), value_input on balance
          <- business_ext_refund_fee_credit (4, agent credit_refund_fee_b8556c63), value_input on balance
- tool uuid8s generated one by one with uuid.uuid4().hex[:8]: 0ea58e95 2324701e 7d50e7f4 b8556c63 9ab6815a

## Log
- base charter copied verbatim into business.extended.yaml; task 0 policies appended.
- task_tools.py (task 0 tools) -> check_task_tools: TASK TOOL CONTRACT OK
- task 0 written (world, gold, contract, closure, dossier). Values: subscription 9.99, instant amount 1358.00 (+ fee 20.00).
- task 0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- revisions: inlined tool helpers (check_extended counted them as tools); dropped 3 unread seed rows (replay closure).
- open item: confirm the historic chargeback fee 31.50 (2026-06-02) against the chargeback-fee charter once task 1 policies exist.
- task 1 policies (chargeback fee, refund fee credit, bank payout) and tools appended; check_task_tools OK
- verified: task 0 historic chargeback fee 31.50 equals the chargeback-fee charter evaluated on 2026-06-02 (t0 world)
- task 1 written: chargeback fee 11.50, refund fee credit 5.81, bank payout 2099.84; swapped prerequisite order identical; edge skips 2111.34 / 2094.03.
- task 1 revision: refunds at 1.88% of rolling-month sales sat on the refund-exposure fall-through -> narrowed online order sizes (70-400) -> 2.24%.
- task 1 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- final difficulty-wide gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite branches mean 38.00, steps 12.00, history max 309, branch max 46), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred until the KB is rendered.

## Round 2 — policy-task audit r1 rework (audits/policy_task/business_profile_sales_holds_and_payouts/)
- CG-F1 / T1-F1: removed the fixed_fee_return factor, its params and its sentences from business_ext_refund_fee_credit, and added the refund_timing parameter factor (>60 days 25 / >14 days 60 / otherwise 100 percent of the percentage credit). The overwrite replaced_by now restates that the fixed part and cross-border fee are never credited, matching parameter_schema.fee_refund_pct_portion_on_refund and events.business_fee_credit. Task 1 world: the refunded 840.00 invoice sale and its fee moved 2026-09-10 -> 2026-08-27, and its delivery 2026-09-12 -> 2026-08-29. Credit 5.81 -> 3.31; bank payout 2099.84 -> 2097.34; all factors still bear weight.
- T0-F1: the owner's wallet plan_started_date is now 2026-08-20 (Plus -> Prime); the August subscription row is recomputed on Plus as 13.99, and the balance goes 5767.01 -> 5763.01. September's fee is still 9.99, so the stamp no longer matches. Instant payout 1358.00 -> 1356.00 (fee 20.00); skip-edge 1361.00; the June chargeback fee is unchanged at 31.50 (Plus and Prime share the tier).
- CG-O2: both payout policies now declare the base daily-limit clause in their overwrite.
- CG-O3: credit_refund_fee_b8556c63 docstring reworded (no ordering word).
- T1-O2: near-miss sentence in task 1's rationale corrected.
- CG-O1, CG-O4, CG-O5, CG-O6, T1-O1 and the seed-history observation are recorded in the rationale section 15 of each task; no artifact change needed.
