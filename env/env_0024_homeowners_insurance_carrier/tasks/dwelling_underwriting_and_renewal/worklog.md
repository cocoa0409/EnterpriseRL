# dwelling_underwriting_and_renewal — difficulty worklog

## Step 0 draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[5,5,5]
- task 1: prerequisite_problems=3, factor_counts=[5,4,5,4]

## Budget (principle C)
7 extended policies in all. Task 0 claims the renewal chain for a vacant building:
vacancy permit charge (agent) -> renewal indication (agent) -> renewal premium paid in full (user, root).
Task 1 keeps the whole nonpayment / billing-correction space (late fee, returned-payment fee,
unbilled-installment billing, rescission payment) untouched by task 0.

## Tool names (uuid8 generated one per tool)
- issue_vacancy_permit_2309bb3c (agent)  -> dwelling_ext_vacancy_permit_charge
- record_renewal_indication_d716047a (agent) -> dwelling_ext_renewal_indication
- pay_renewal_premium_4100e9a3 (user) -> dwelling_ext_renewal_premium_paid_in_full

## Log
- round 1 cut off before any file landed; round 2 writes charter, tools, task 0 in batches.
- task 0 closed: 114.88 / 2680.20 / 2443.24; per-task gates green (extended, tools, replay, solvability, compute, grounding, cross_fire). Fixes: flood near-miss claim seeded; unread inspection rows removed.
- task 1 tools: assess_installment_fee_8325e06b, assess_late_fee_984fd113, assess_returned_payment_fee_55a26ad1 (agent), pay_off_term_premium_a09f99f1 (user). Theme: returned EFT on installment 3, missing fees, customer pays off the rest of the term.
- task 1 closed: installment fee 9.07, returned-payment fee 41.25, late fee 18.75, pay-off 2269.04; all six orders of the parallel fees give identical results; per-task gates green.
- final difficulty run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite branches mean 44.0, steps 16.0, history max 57, branches max 49), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability skipped (KB not yet published).
- coverage: task 0 = {vacancy_permit_charge, renewal_indication, renewal_premium_paid_in_full}; task 1 = {installment_fee, returned_payment_fee, late_fee, term_payoff}; disjoint, 7/7 policies and 7/7 tools.

## Round 2 — policy-task audit rework (audits/policy_task/dwelling_underwriting_and_renewal)
- F-1 (SOURCE-FACTOR RED): relabelled as parameter: claim_cause_weighting, payment_history_window, repeat_lateness, return_frequency. New honest method factors: indication.vacancy_at_offer (day-prorated / flat annual / none), paid_in_full.rental_book_credit (flat per unit after the percentage / percentage / none), late_fee.late_fee_basis (1.2 % of installment / half tier fee / tier fee), returned_payment_fee.returned_fee_basis (tier fee + 2 % of excess over 1000 / half tier fee / tier fee). Figures: indication 2680.20 -> 2646.10; late fee 18.75 -> 16.10; returned fee 41.25 -> 29.34; pay-off 2269.04 -> 2254.48; others unchanged.
- F-2: umbrella schedule nets removals/lapses and needs an umbrella in force; flood payment count scoped to the same-address FloodGuard policy; latest peril = most recent loss date. No figure moved.
- F-4: household_account_credit cross_difficulty -> home; rental_book_credit cross_difficulty -> null.
- F-5: indication declares overwrites of the dwelling_renewal offer-timing and rating-recording clauses.
- F-3 kept (accepted borderline); F-6/F-7 concern the frozen blueprint (answered in rationale); task-0 obs 2 answered (rate cap by design); task-1 obs 2 fixed (bounce mentioned only when asked); obs 3 answered; obs 4 answered with business reason sentence in the pay-off rule.
- Gates re-run per task and difficulty-wide: all OK.
