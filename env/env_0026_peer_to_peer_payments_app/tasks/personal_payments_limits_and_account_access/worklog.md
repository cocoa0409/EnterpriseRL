# Worklog — personal_payments_limits_and_account_access (category wallet, M=2)

## Step 0 — difficulty pre-check and draws
- Read: blueprint.yaml, products/wallet.yaml (base copied verbatim into wallet.extended.yaml), db_schema.json, share_tools.py, the three reference contracts. Other products were read only for cross-category fields (card, rewards, savings, advance, business).
- DSL constraints noted: windows are rolling (`within_months`), there is no calendar-month or business-day primitive. So every extended window is stated as "dated later than the same calendar day N months before the handling date", and the base's calendar-month instant-fee measures are overridden explicitly.
- `draw_counts.py --tasks 2`: task 0 has 1 prerequisite problem, factor counts [5, 4]. Task 1 has 1 prerequisite problem, factor counts [4, 5].
- User-side numeric writes that can be computed in the DSL are the customer's cash-outs. A plan change can't be priced generally, because the target plan's parameters can't be read. A claim liability can't be computed, because it needs Federal Reserve business days. So both trees end in a cash-out owned by the customer, and each is fed by a different agent-side obligation.

## Claimed scopes (pairwise disjoint; the two scopes together cover all four policies)
| task | root (owner) | prerequisite (owner) | edge |
|---|---|---|---|
| 0 | wallet_ext_available_balance_transfer → transfer_balance_to_bank_3181bc35 (user), 4 factors | wallet_ext_renewal_plan_fee → charge_plan_fee_0f985a0a (agent), 5 factors | value_input on ledger_now, state form, "not … until" |
| 1 | wallet_ext_claim_money_instant_fee → send_instant_cash_out_cd9063e1 (user), 5 factors | wallet_ext_protection_reimbursement → post_protection_reimbursement_5be5cf5a (agent), 4 factors | value_input on reimb_amt, state form, "only after" |

## Results (handling-time recompute)
- task 0: plan fee 4.79 (baseline 9.99), transfer 3418.38 (baseline 4343.38). Skipping the fee gives 3423.17.
- task 1 (after round 3): reimbursement 2722.76 (baseline 2500.00), instant fee 15.93 (baseline 25.00). Skipping the reimbursement gives a fee of 0.23. (Round 1 values were 2677.86 / 15.67; round 2 values were 2731.42 / 15.98.)
- Every factor substitution moves the result. The figures are recorded in each task's `computations[].factor_sensitivity`.

## Revisions
1. check_extended counted module-level helper functions in task_tools.py as undiscoverable tools. Fixed by inlining them as a defaults dict. Result: PASS.
2. The replay closure missed 2 rows in task 0: an unread account_recovery request and an unread savings ledger row. Both were dropped from the seed. Result: REPLAY OK.
3. The baseline paragraphs originally named the adjustments. Each was split into a pure standard-method sentence (the baseline) and a separate combination sentence in the rule. The compute_basis quotes were updated to match, and all gates were re-run.

## Round 2 — policy-task audit (audits/policy_task/personal_payments_limits_and_account_access/)
- **F-1, F-2 and T1-F1** (the reimbursement's two method ladders were one formula each): the funding fee part and the seller-money deduction are now fixed single formulas inside the baseline. Two factors replace them:
  - claim_lookback_window (method): a 6-, 9- or 12-month look-back chosen by account age. On task 1's world the three tiers give 3034.91, 2731.42 and 2427.93.
  - claim_review_delay_credit (parameter): 2, 1 or 0 percent by the days from report to approval.
  The policy still has 4 factors (3 parameter, 1 method). Task 1 seed: an 88.00 goods payment with a denied 2025-11-20 claim was added as the window's near miss, and the 2026-09-28 payment went from 969.05 to 881.05, so the ledger stays 1240.55. Recomputed values: reimbursement 2731.42, fee 15.98.
- **T0-F1 and T0-O2**: the false "boundary" near-miss text was replaced. A genuine near miss was planted: a time_locked vault of 7200.00. The rule counts only the active vault; summing every vault would give the 10 percent tier. The rationale's multi-source labels and the "one month back" wording were also corrected. Task 0's scored values are unchanged (4.79, 3418.38).
- **O-3**: the renewal rule and tool now cover annual billing (annual_plan_fee, no reductions; billing period YYYY). The transfer's condition now says monthly or annual.
- **O-4**: the deposit window and period length in the renewal rule are anchored on the handling date, as in compute.
- **O-5**: the paid claim is "the purchase protection claim most recently approved", paid once. The other-claims count subtracts the paid claim's own filing within the window.
- **O-6**: the transfer's baseline.params is now [].
- **O-7, O-8, O-9**: kept as observations (the window-type methods are accepted by the auditor; the savings category is unclaimed but other cross-difficulty factors exist; the repeat-claim share counts filings as an abuse signal).
- **O-10**: the rule states that a return carries the speed of the transfer it returns.
- **O-11**: the rate sentence was reworded so the deposit tier applies whatever cuts apply.
- **T1-O2**: the design_rationale of tasks/1.json was "(pending)" on disk; it is now complete.
- **T1-O3**: the discriminating quota record is named in the factor card.
- **Scratch-hygiene note**: in round 1 an `rm -rf` on the shared scratchpad contents was run. Round 2 used only scratchpad/erl_limits_r2/.

## Round 3 — policy-task audit revision_2
The auditor's calibration: a `method` tier must change the algorithm. If one formula with a substituted constant reproduces every tier, the factor is a parameter. Each policy now has one method factor whose tiers are different algorithms:
- **F2-1 / T0-F2, renewal plan fee `restricted_days_credit`**: a takeover lock is credited pro rata by locked day; a limitation is all or nothing (the whole discounted fee when it covered more than half the period); otherwise no credit. `review_grace_days` was removed. Task 0's value is unchanged (4.79); tier 2's algorithm on this world gives 0.
- **F2-1 / T0-F2, available transfer `sales_receipt_hold`**: a new seller has the two-month total held; an established seller has only the single most recent receipt held (LATEST); otherwise nothing. Task 0's value is unchanged (3418.38); the established-seller algorithm gives 180.00.
- **F2-1 / T1-F2, protection reimbursement**:
  - `claim_lookback_window` is relabelled parameter (its tiers only choose N).
  - `claim_review_delay_credit` becomes the method: 30 or more review days earn simple interest at `delay_interest_pct` 18 percent a year (actual/365) on the amount after the share; 15 to 29 days earn a flat 1 percent; below that, nothing.
  - Task 1 reimbursement: 2722.76. The flat tier would give 2704.64 and the fall-through 2677.86.
- **F2-1 / T1-F2, instant fee `deposit_measure_window`**: a 365+ day account uses the median of the last three monthly totals (5200.00); a 180–364 day account uses the lower of the last two monthly totals (1800.00); otherwise the last month's total (1800.00). Task 1 fee: 15.93.
- **O2-1**: the credit period is stated as running from the previous plan fee entry to the handling date.
- **O2-2**: the claim-money prerequisite sentence now waits on "the purchase protection claim most recently approved on the account" (the claim the reimbursement rule pays). The condition was aligned with it.
- **O2-3**: the annual renewal sentence includes the last-day-of-month fallback.
- **T0-O3**: the persona names both vaults when asked.
- **T1-O4**: the rationale claims multi-source only for `deposit_rate_tier`.
- Scratch: round 3 used only scratchpad/erl_limits_r3/, which was deleted file by file.

## Round 4 — policy-task audit revision_3
- T1-F3: tasks/1.json stated the claim-review delay credit as 44.8957 and the pre-rounding reimbursement as 2722.7557. The recomputed figures are 2677.86 x 0.18 x 34 / 365 = 44.900009 and 2722.760009. Both were corrected in the design_rationale factor card, computations[0].factor_trace and evaluation_criteria[7].argument_uniqueness_tracing.amount. The scored values are unchanged (2722.76, 15.93).
- T1-O5: the computations[0].factor_trace label of claim_review_delay_credit now reads "(method)", matching the charter.
- No charter, tool or seed change this round.

## Gates (final, difficulty-wide)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (round 3: branches mean 36.00, steps mean 13.50, history_rows_max 15, branches_max 37)
- check_grounding: GROUNDING OK
- check_cache_diff: CACHE-DIFF INFO (optional; not a correctness gate)
- check_cross_fire: SCOPE OK
- check_traceability: not run (the KB has not been rendered yet)
