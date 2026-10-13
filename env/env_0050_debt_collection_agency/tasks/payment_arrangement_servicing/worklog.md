# payment_arrangement_servicing (category plan) - instantiate worklog
- draw (draw_counts.py --tasks 2): task 0 prereq 1, factors [4,4]; task 1 prereq 3, factors [6,4,5,5].
- constraint: plan_installment_paid/returned, plan_authorized/broken/reinstated trigger account events -> no task tool writes them.
- task 0: root plan_ext_new_method_handover (authorize_payment_method_50f022be, user) <- plan_ext_returned_installment_redating (redate_returned_installment_ce690b15). gold: shift_days 8, installment_number 7.
- task 1: root plan_ext_post_hold_restructure (authorize_restructured_installments_370d01b0, user) <- plan_ext_post_hold_reaging (reage_missed_installment_128922de) <- plan_ext_post_hold_resumption (resume_suspended_plan_416c1e83) <- plan_ext_presuspension_missed_entry (record_missed_installment_d21cca89). gold: 5, 64 days, 243.00, 215.00.
- final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability pending KB render.
- validate_scenario: only "required document ... not found" errors (KB not rendered yet); tasks_ok 4/4.

## Rework round 2 (audit audits/policy_task/payment_arrangement_servicing: _difficulty.md, 0.md, 1.md)
- F-1: presuspension now declares overwrite of base plan_evt_installments grace sentence and plan_evt_suspension counting sentence; first rule sentence no longer uses base "grace period"; resumption prerequisite sentence reworded to "pre-suspension grace ... by the date missed-installment counting stopped"; task 1 why_false texts rewritten on the extended definition. Gold 5 unchanged.
- F-2: restructure declares overwrite of base "it re-spreads the current arrangement_balance over a new count of installments" (replaced by the restructure-balance sentence). Gold 215.00 unchanged.
- F-3: restructure -> missed-entry sentence now "...last installment whose pre-suspension grace had run out by the time missed-installment counting stopped" (same scope as condition); condition aligned.
- F-4: handover tolerance factor removed; covered amount uses the type's partial_payment_tolerance_usd as base; new parameter factor setup_notice_return_allowance (0/4/2). Task 0 computation B: 7, baselines 8/8/8/8, all 8.
- F-5: re-aging rule: every method places the re-aged installment behind the final (as the tool does); few-installments branch = spread over following installments plus that place (count + 1); under a spread the re-aged installment carries only what the balance leaves.
- F-6: resumption result floored at resume_min_days_to_next_installment (rule + compute).
- F-7: grace watch tier 5 -> 4; restart lead assisted 21 -> 22 and cool-down heavy 7 -> 6 (earliest restart day stays 35, gold 64); handover tolerance collisions gone with F-4.
- O-1: re-dating buffer reads returned payments made outside any payment plan (plan_id empty); task 0 seeded check_by_mail 150.00 (2CHK-40917) 2026-09-15 returned stop_payment 2026-09-22; shift 8 unchanged.
- O-2: "installments paid" (payment rows) renamed "kept installment payments" in all rules/ladders.
- O-3: explanatory clauses removed from the handover day count.
- O-4: (a) hold-timing extension requires request on or after the due date; (b) suspending hold = account hold whose decision_date is the plan's suspended_date (CPARAM/CFIELD filter), assistance decision read by hold_id.
- O-5: (a) "uncured" dropped (most recent missed entry); (b) term-window start fallback stated in rule and compute; (c) as O-4b.
- O-6: debit_within_notice limited to the next three days (0..3) in rule and compute.
- O-7: kept - base plan_resumed declares no trigger and a task tool may not write placed_accounts.
- O-8: kept - <table>.<field> is the contract's gate form for a state gate without a base eligibility.
- O-9: handover edge condition trimmed to the due-date change entry. O-10: effect texts generalized. O-11: re-aging first sentence no longer restates the active-status dependency. O-12: replaced_by now quotes the standard spread sentence.
- task 1 SOURCE-TASK final_due_date: restructure rule states the re-aged installment moves to one period after the last restructured installment; final = its new due date; count = anchor + restructured count; tracing updated (2028-06-12 unique).
- task 1 observations: arrangement_balance > balance_due kept (base keeps client credits off the arrangement; plan cancelled account_resolved_otherwise when the account is paid); identity - any two matching details write the same verification row.
- re-run: full gate block green; validate_scenario only "required document not found".

## Rework round 3 (audit revision_2 sections of _difficulty.md, 0.md, 1.md)
- R2-N1 (task 0 SOURCE-TASK RED): the round-2 check return (2026-09-22) + the plan's 2026-10-07 return hit the Primary Placement returned-payment block (account_evt_payment_channels: 2 returns in 180 days, 90-day block). Moved the non-plan check payment/return to 2026-02-10 / 2026-02-17 (outside the 180-day lookback: only the 2026-10-07 return in 2026-04-12..2026-10-09, 1 < 2, no block; the February return was 232 days old at 2026-10-07). Re-dating buffer window widened to twelve months (rule, compute, ladder, inputs) so it still reads that return (buffer 2, shift 8 unchanged). Charter-global half: handover rule now states a payment-method change does not lift an account returned-payment block and an automatic method is authorized only while the account accepts electronic payments; task 0 tracing/rationale carry the block check. Gold (card_autopay, recorded_call, 7) unchanged.
- O-13: kept as observation - plan base "suspended on the day its account enters ... hardship_hold" and the account enters hardship_hold at approval, which the decision_date identification encodes (auditor: not RED).
- O-14: plan_evt_suspension overwrite narrowed to "Missed-installment counting stops while the plan is suspended" ("restarts from the new schedule" stays inherited); the grace-sentence overwrite stays scoped by the rule's "for that determination ..." clause (ordinary misses keep the base grace via the inherited grace_elapsed gate).
- O-15: handover return allowance now reads returns in the last six months (rule, compute, ladder, inputs), no longer the same condition as the re-dating lead; task 0 tier unchanged.
- task 1: untouched in substance (passed); rationale notes O-14 and the account block (ends 2026-10-13, before the 2026-12-12 restart). Re-run identical.
- re-run: full gate block green; validate_scenario only "required document not found".
