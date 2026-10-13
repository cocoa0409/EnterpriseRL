# worklog — personal_services_packages (category services, M=2)

## Step 0 — difficulty pre-check
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/services.yaml, db_schema.json, share_tools.py, gate scripts.
- draw_counts.py --tasks 2:
  - task 0: prerequisite_problems=1, factor_counts=[6, 4]
  - task 1: prerequisite_problems=1, factor_counts=[4, 5]
- Gate-imposed constraints discovered while reading the base:
  - one_draw_per_order dedup binds action args order_reference, draw_basis AND event_type -> any draw/hourly-charge tool must carry an `event_type` argument.
  - one_correction_per_entry dedup binds source_entry_id AND credit_reason -> a services_hours_restore tool would need a credit_reason arg (meaningless on a restore) -> restores avoided as a write subject.
  - user-owned writes in this product (enroll, withdraw, package change, suspension, cancellation, cancellation withdrawal) carry no money field; a user problem's computed value must be an integer (months) or an enum.
  - DSL: SUM/COUNT/LATEST are scoped to the target plan; calendar-month selection is done by reading a billing_period with LATEST and using it as an eq filter.
- Identifier band (coordinator): phone/representative_phone 4695550100-4695550199, ssn_last4 8500-9999, unique e-mails.
- Base automatic clauses to respect: month-start fee+grant (services_monthly_cycle), month-end expiry / rollover, plan_end expiry on end, residency-end proration, returned-payment fee trigger. Seeds keep the monthly cycle consistent for every month shown.

## Claim plan (headroom)
- task 0: root = suspension request (user, 4 factors) <- prerequisite = correction credit for a visit billed on more time than delivered (agent, 6 factors). value_input: the credit lowers the balance the suspension's account-standing factor reads.
- task 1 (reserved space, not yet written): root = package change fitted to use (user, enum, 4 factors) <- prerequisite = hours owed for a late-cancelled / missed visit (agent draw, 5 factors). value_input via hours used.
- Disjoint subjects: task0 {services_suspend, services_credit}; task1 {services_package_change_request, services_hours_draw}.

## Task 0 — CLOSED
- Tree: root services_ext_suspension_months (user, sign_services_suspension_89d6021d, 4 factors) <- services_ext_short_visit_credit (agent, post_services_visit_credit_5ef485c2, 6 factors); value_input edge on past_due; state-form prerequisite sentence ("... is fixed only after ...").
- World: Eleanor Whitfield (AL Care Level 3, on leave for rehab since 2026-09-24, occupied LifeChoice 50% agreement), Companion Package; overbilled Saturday visit SO-2609-0389 (88.00 for 2.00 h, 70 min delivered).
- Gold: credit 87.50 (step 9) then suspension 2026-11-01 x 3 months (step 11). Fall-backs: credit 55.00, suspension 0; skip credit -> 2 months.
- Revisions: account-standing factor moved from cached balance to ledger reconciliation (record-derived evidence); date helper inlined into tool.
- Gates (--task 0): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
- Manual values gates: prerequisite sentence four-point test passed; persona names no visit/charge; tools block nothing; base notice + dispute window boundaries recorded in solvability_contract.

## Task 1 — CLOSED
- Tree: root services_ext_package_fit (user, sign_services_package_change_2a41e92a, 4 factors, enum result) <- services_ext_missed_visit_hours (agent, post_services_order_hours_8d682fe6, 5 factors); value_input edge on late_hours; state-form prerequisite sentence in the negated direction ("... is not chosen until ...").
- World: Harold Brennan (Premier, IL Two-Bedroom double with Margaret, occupied LifeCare agreement, September suspended); no-show SO-2610-1064 on 2026-10-09 never drawn.
- Gold: draw 0.27 h (step 8) then change to Personal Services Comfort Package from 2026-11-01 (step 10). Fall-backs: 0.00 h / Essentials; skip draw -> Companion.
- Revisions: enum docstrings completed for gate; entrance ladder wording distinguished from task 0.
- Gates (--task 1): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.

## Difficulty closing (final run, no --task)
- Coverage: 4 extended policies, tasks 0/1 disjoint (policies, tools, subjects); prerequisite sentences: task 0 affirmative ("only after"), task 1 negated ("not ... until").
- Final gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (branches mean 35.5, steps mean 11.5, history max 20, branches max 39) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK.
- check_traceability skipped: requires the published KB (not yet rendered).
- Temporary authoring scripts lived in /tmp/psp (outside the write domain) and were removed; no __pycache__ left in the difficulty directory.

## Round 2 rework — audits/policy_task/personal_services_packages (_difficulty.md, task_0.md, task_1.md read in full)
- F-1 (SOURCE-FACTOR RED, task 0): previous_suspension_count made a genuine method factor — tiers now select the look-back window (excluded / 6-month look-back for a suspension that ended 3-12 months ago / standard 12-month look-back), counted as MN(months, window - months since end). Task 0 value unchanged (3); factor baseline 2; all-baseline 0. CLOSED.
- F-2 (window boundary; SOURCE-TASK RED in task 1): fit rule states the whole-month convention (fewer than review_months whole months from posting date to request date; same day-of-month review_months earlier is outside, next day inside; last month the same way). Boundary row SO-2607-1121 moved to a 2026-07-10 visit drawn 2026-07-11 (3 months 3 days before). Re-run: Comfort; every factor and the edge bear weight. CLOSED.
- O-1: credit is 0 when the re-rated charge is not below the posted charge (rule sentence + compute guard). CLOSED.
- O-2: past-due subtracts the current-month fee row on the ledger (LATEST fee row posted in the request month), not the tariff. CLOSED.
- O-3: rebooking rule worded on the most recent same-service booking, matching compute. CLOSED.
- O-4: divisor tier 2 no longer asserts a cause ("as when the plan was suspended for a month"). CLOSED.
- O-5: kept — each overwrite still names the base sentence the extended rule contradicts; the auditor confirms no undeclared override. Response recorded, no change.
- O-6: illness relief now requires the visit to have ended short of its booked time (illness cut the visit short); task 0 visit 70/120 min, value 87.50 unchanged. CLOSED.
- O-7: band ladder fall-through is now an in-scope case (same-day cancellation -> late_cancel_hours_charged, the base standard); day-before cancellation -> x day_before_share; cancellations 2+ days ahead stated out of scope. CLOSED.
- task_1 obs 2 (half-up vs binary rounding): multipliers re-set (repeat 1.2, rebook week 0.6) — gold hours 0.34, required 8.17, no figure on a half-hundredth. CLOSED.
- task_0 obs 3 / task_1 obs 4 (multi-source labels): factor_trace / rationale relabelled single-record factors. CLOSED.
- task_1 obs 5 (calendar-month reading C): excluded by the stated convention. CLOSED.
- Full gate block re-run (no --task): all green; check_traceability skipped (no KB).

## Round 3 rework — audits revision_2 sections read in full (_difficulty.md, task_0.md, task_1.md)
- F-1 (SOURCE-FACTOR RED, judged not closed in round 2): previous_suspension_count removed as a factor; the previous suspension is plumbing with the standard 12-month look-back. New method factor time_in_force_count (decides months_in_force): (a) resident admitted to the assisted residency from a Larkspur independent residency -> whole months since that independent move-in date (different anchor record, cross-difficulty independent, multi-source with assisted admission_source); (b) otherwise, a plan with a recorded suspension -> months since effective date less the suspended months; (c) months since effective date. time_in_force_extension stays a parameter ladder on the counted months (owns months_since_effective as its date evidence). Task 0 unchanged: 3 months (2+2+2-1-2); sensitivity 1/2/1/4; all-baseline 0; skip credit 2. CLOSED.
- O-8 (latest fee row vs current billing month): rule now says the fee charged on the first day of the current month; the base charter charges every package fee on the first day of a month (monthly cycle; package changes take effect on the first), so a mid-month fee row cannot arise and MONTHS(fee date, request) == 0 identifies exactly the current month's fee. CLOSED (wording) / not reachable.
- O-9 (Concierge late_cancel_hours_charged 0.0 makes the day-before and same-day tiers coincide): a property of the frozen base tier (Concierge waives late-cancellation hours); the ladder's tiers differ on the five other packages and on every task world. Answered, no change.
- O-5: unchanged observation (each overwrite names the contradicted base sentence; no undeclared override). Answered, no change.
- F-2, O-1, O-2, O-3, O-4, O-6, O-7 and the task observations: confirmed closed in revision_2; not regressed (task 1 world and values untouched: 0.34 h, Comfort).
- Full gate block re-run (no --task): all green; check_traceability skipped.

## Round 4 rework — render-layer audits (policy_kb task_0/task_1, runtime_context task_0/task_1 read in full; runtime verdicts PASS)
- B1 / N1 (assembly floor): services_ext_suspension_months now states the total in one sentence (rule = baseline = overwrite replaced_by): starting allowance + time-in-force months - counted months of the last suspension, "never below zero, the floor being applied once to the final number of months and never to a part of it"; factor sentences add to / deduct from "the total". Compute unchanged in shape (MX(0, ...) on the total). CLOSED.
- B2 / E1 / N2 (factor-only default in baseline, "as the standard"): baseline restructured — time in force is part of the standard computation (whole months since the effective date, ladder 48 -> 2 / 24 -> 1), no "as the standard" wording anywhere; time_in_force_count (method) changes how the whole months are counted; the previous suspension's months are a parameter factor previous_suspension_share (0 / 0.5 / 1) on the baseline's 12-month count. Task 0 suspension now 4 months (2026-11-01..2027-02-28); sensitivity 2/3/5/3; all-baseline 1; skip credit 3. CLOSED.
- B3 / N6 (last whole month in the fit baseline): removed from the review-months sentence; stated in full only in the trend factor's sentence. Task 1 unchanged (0.34 h; Comfort). CLOSED.
- N3: baseline states max_suspension_months_per_12m is the starting allowance, not a ceiling (base description frozen; routed around in the extended rule). CLOSED.
- N4: the three services_hours_and_billing overwrites (rounding / drawing / rest charged) withdrawn so those base rules stay in force for first postings; new credit rule sentence limits re-rating to working out a correction, declared as replacing the disputes clause "A draw or charge that matches ... is not an error." Credit unchanged 87.50. CLOSED.
- N5: lifecare / fee-for-service contracts named by plan in both entrance factors (rule, basis, ladders). CLOSED.
- N7: fit rule states Concierge for required hours above every allotment (independent residence). CLOSED.
- N8: missed-visit scope sentence states lateness is in calendar days and late_cancel_notice_hours plays no part (base description frozen). CLOSED.
- docs/ not touched (re-render belongs to the render agent).
- Full gate block incl. check_traceability (against the current published KB): all green.
