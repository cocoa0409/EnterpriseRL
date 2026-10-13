# overpayment_waiver_and_recovery — instantiate worklog (M=2)

Detailed per-task dossiers live in each task's `design_rationale`; this file is the difficulty-level index.

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems 3, factor_counts [6, 5, 4, 4]
- task 1: prerequisite_problems 2, factor_counts [6, 5, 5]

## Scope (pairwise disjoint, together covering all 7 extended policies)
| task | policy (factors) | tool | owner |
|---|---|---|---|
| 0 | overpay_ext_returned_payment_fee (5) | book_returned_payment_fee_10cb479c | agent |
| 0 | overpay_ext_plan_arrears (4) | pay_overpayment_arrears_d9b1e543 | user |
| 0 | overpay_ext_plan_reinstatement (4) | reinstate_repayment_plan_54c54ed5 | user |
| 0 | overpay_ext_new_plan_installment (6, root) | set_up_repayment_plan_0b609272 | user |
| 1 | overpay_ext_waiver_household_income (5) | complete_waiver_household_income_abba3816 | user |
| 1 | overpay_ext_waiver_decision (6) | record_waiver_decision_07f617be | agent |
| 1 | overpay_ext_plan_change (5, root) | change_repayment_plan_f1933d01 | user |

Trees: task 0 fee -> arrears -> reinstatement -> new plan (value, value, state gate); task 1 income completion -> waiver decision -> plan change (value, value).
Gold values (after rework round 2): task 0 51.00 / 138.00 / 60.22 / 100.50; task 1 31,701.20 / 1,619.20 (partially_granted) / 32.42.

## Design constraints recorded
- overpay_repayment_received with component principal triggers charge:charge_credit_reversed, so no tool books a principal repayment; the arrears tool books the penalty component only (task 0's fraud overpayment has its principal fully intercepted).
- Empty foreign keys are seeded as null (replay gate treats '' as dangling).
- task_tools.py does date arithmetic with the `_CivilCalendar` static-method class; no datetime/time/random/uuid tokens.
- frozen_time format `YYYY-MM-DD HH:MM:SS CDT`.

## Revisions
- task 0: replay gate failed on '' foreign keys and closure (employer rows unread) -> FKs set to null, employer rows dropped (claim's separating employer null), find_claims read added; re-run REPLAY OK.
- task 1: check_compute "history not load-bearing" for the income completion -> rule/compute gained the "request still awaiting decision" scope (COUNT of received requests); re-run COMPUTE OK, values unchanged.

## Final gates (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 64.50, steps 16.00; history_rows_max 35; branches_max 71); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. check_traceability deferred until the KB is rendered. validate_scenario: only "required document ... not found" errors for this difficulty (KB-dependent).

## Rework round 2 (audits/policy_task/overpayment_waiver_and_recovery: _difficulty.md, 0.md, 1.md)
Blueprint untouched; every fix lives in overpay.extended.yaml, task_tools.py (one docstring line) and the task files.
- G-1 / F0-1 (fee): `return_lookback_window` is now a genuine anchor method: plan current or defaulted with first installment due date passed -> look-back anchored at that date (MONTHS(first due, now) + 1); fraud overpayment without such a plan -> anchored at the determination date (MONTHS(determination, now) + 1); otherwise the standard 12 months back. Params `lookback_months_plan` / `lookback_months_fraud` removed. Task 0 fee unchanged 51.00 (anchor 2025-05-16 -> 5 months; baseline 56.00).
- G-1 / F1-1 (plan change): `determination_clock` replaced by `running_schedule_anchor` (method): first due date passed -> take off installments fallen due (MONTHS(first due, now) + 1); first due recorded but not passed -> whole months since determination, capped at the determination-months cap; none recorded -> nothing. Task 1 takes off 1 (first due 2025-09-26), 32.42 unchanged.
- G-2: month ladders now are shares of the classification maximum (reinstatement 0.50 / 0.75 / max; new plan 0.50 / 0.75 / max; plan change 0.20 / 0.40 / max, whole months, fraction dropped) -> three distinct tiers for every classification (24 to 60). World values unchanged (18, 36, 12).
- G-3: look-back plan test is `status == current or defaulted` (rule and compute).
- G-4: fee rule now counts and prices by return entry ("each return entry counting as one returned item", "amount on the return entry being charged").
- G-5: pension tier adds the latest in-window weekly amount of each pension kind (employer-funded + claimant-contributed) x 52; rule, compute and ladder aligned. Not exercised (task 1 has no pension).
- G-6: decision rule dates the overpaid period from the Sunday six days before the first week-ending date; compute: before = DAYS(start, notice) < -6; within = >= -6 and before the last week end; weeks on/before = 0 if DAYS < 0 else int(DAYS / 7) + 1. Task 1 unchanged (11 of 15 weeks).
- G-7: income completion computes only where the request carries 0.00 (no figure stated); a stated figure stands; the confirmed figure becomes the claimant's own statement on the application (base sentence honoured, no override). Compute `result` gains `lodged_income == 0`.
- G-8: "A request is granted only when the amount waived is the whole unpaid principal; when anything less is waived the request is partially granted"; overwrite replaced_by and baseline.rule follow; decision tool docstring enum text aligned ("whole unpaid principal" / "less than the whole unpaid principal").
- G-9 / F0-2: new-plan returned-payment sentence and ladder scoped to return entries on the overpayment.
- O-1: fee overwrite `replaced_by` is now the composite fee sentence.
- O-2 / F0-4: late-return charge restated as the depository's handling of an item sent back after the normal return period (re-presented or disputed debit).
- O-3: kept (anchor-date method accepted by the audit); no change.
- O-4 / F1-2: decision prerequisite sentence -> "... carries a household annual income above zero." (matches the condition; unique); plan-change condition drops the overpayment-status clause.
- O-5: kept: reinstatement/change keep the original first due date (base sentence governs a plan being set; date is not a tool parameter); no change.
- O-6 / F1-3: `support_order_exclusion`, `other_pay_addition` relabelled method (ladder `method` texts); `partial_band_position` relabelled parameter (ladder `value`). Per-computation floors still met (income 2P/3M; decision 5P/1M).
- O-7: income rule states the completion is made only on a request whose review is already open and does not open one; subject kept (closest base event); task 1 opens with the review open.
- F0-3: task 0 SNAP order eb39a5e0… claim_id -> null (no claim open when it arrived 2025-06-02).
- Task 0 seed re-derived under the revised fee rule: June fee 0063dbe4… 46.00 -> 36.00 (plan-anchored look-back excludes the pre-plan February return); balance_due 6ce505f1… 1,045.44 -> 1,035.44. Gold: arrears 148.00 -> 138.00, reinstatement 59.89 -> 60.22 (383.90 / 12 + 564.54 / 20); skip figures arrears-without-fee 87.00, reinstatement-without-arrears 71.72; all traces, sensitivities, contract texts and rationale updated; rationale row count corrected (29 ledger rows).
- Task 1: values unchanged (31,701.20 / 1,619.20 / 32.42); prerequisite_closure copies, factor names/labels and texts updated.
- Gates re-run (no --task): see final run below.
- Final gates after rework round 2 (no --task, all rc=0): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 16 acts closure 60/60, 1.json 16 acts closure 109/109); SOLVABILITY OK; COMPUTE OK (suite means branches 65.50, steps 16.00; history_rows_max 35; branches_max 73); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. check_traceability deferred until the KB is rendered. validate_scenario: only the 7 "required document ... not found" errors for this difficulty (KB-dependent). Forbidden-token scan of task_tools.py: 0 hits; frozen_time formats 2025-10-14 10:35:00 CDT / 2025-10-21 14:10:00 CDT.

## Rework round 3 (audits revision_2: _difficulty.md, 0.md, 1.md)
Task 0 was PASS in revision 2; its values, seed and gold are untouched (only the fee rule wording of R2-G-10 and a rationale note changed). Blueprint untouched.
- R2-G-11 / F1-4 (plan change): `remaining_principal_months` ladder values now `int(P('max_plan_months') * K('small_remainder_share'))` / `int(P('max_plan_months') * K('mid_remainder_share'))` / `P('max_plan_months')`, identical to the compute branches; a K-key sweep over all 7 policies finds no missing or unused parameter.
- R2-G-12 / F1-1 (plan change): `running_schedule_anchor` redesigned with three tiers all reachable under a current plan: (1) first installment due date passed and no waiver request lodged after it -> MONTHS(first due, now) + 1; (2) first due passed and a waiver request lodged after it -> MONTHS(first due, latest request date) + 1 (billing stops during review, base overpay_waiver); (3) first due not yet passed -> MN(cap, months since determination). New binding `review_opened_on` (LATEST request_date); rule sentence, compute_basis and ladder aligned. Task 1 takes tier 1 (first due 2025-09-26 passed, request 2025-09-19 before it) -> 1 taken off; baseline 30.95; 32.42 unchanged.
- R2-G-10 (fee, latent): dropped the clause "so returns from before the plan began are left out"; ladder method texts now state each anchor as "the whole months elapsed from <anchor> to the handling date plus the month in progress", matching compute's whole-months entry test. Task 0 unchanged (window 5; 51.00).
- R2-O-12: 0.00 is now "the record of a request lodged without any income figure"; a written figure stands (rule, baseline.rule, compute_basis).
- R2-O-13: decision rule: "when an amount above zero but less than the whole unpaid principal is waived the request is partially granted ...; when nothing is waived the request is denied"; baseline.rule and decision tool docstring (partially_granted) aligned. Task 1 still partially_granted.
- O-1 remainder, O-3, O-5: observations accepted by the audit; no change.
- Task 1 texts (decision tracing quotes, schedule-anchor trace/tier label, rationale round-3 note) updated; all values unchanged (31,701.20 / 1,619.20 / 32.42).
- Final gates after round 3 (no --task, all rc=0): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json closure 60/60, 1.json 109/109); SOLVABILITY OK; COMPUTE OK (suite means branches 65.50, steps 16.00; history_rows_max 35; branches_max 73); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. check_traceability deferred (KB not rendered). validate_scenario: only the 7 "required document ... not found" errors for this difficulty. Forbidden-token scan 0 hits; base copy lines 1-1133 identical to blueprint.
