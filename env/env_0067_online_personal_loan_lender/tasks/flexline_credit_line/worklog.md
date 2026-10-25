# worklog — flexline_credit_line (env_0067_online_personal_loan_lender), M=2

## Step 0 — pre-check and draw
- Base line.yaml read in full: lifecycle, 13 claimed event types, 8 base policies (line_agg_multi_holding, line_application_underwriting, line_evt_draws, line_evt_interest_and_annual_fee, line_evt_payments_and_fees, line_evt_fee_waiver, line_evt_freeze, line_evt_limit_changes, line_evt_draw_period_and_closure, line_evt_autopay_and_due_day). Base closes; no blueprint edit needed (blueprint is frozen).
- draw_counts.py --tasks 2:
  - task 0: prerequisite_problems=3, factor_counts=[6,4,5,5]
  - task 1: prerequisite_problems=3, factor_counts=[5,5,5,5]
- Headroom: task 0 claims closing to draws + three ledger corrections (returned-payment fee, back-billed draw fee, draw-fee error credit); task 1 keeps draw, past-due payment, late fee and late/returned-fee error waiver — disjoint roots, tools and quantities.
- Cross-difficulty source for both tasks: personal_loan_servicing (category loan: loans, loan_transactions).

## Task 0 — close a frozen FlexLine Standard to new draws
Tools (uuid8 drawn one by one with uuid4().hex[:8]): close_line_to_draws_7539d675 (user), assess_returned_payment_fee_0fd8e99d, assess_draw_fee_4f046c6c, credit_draw_fee_error_e1e6ecd0 (agent).
Capability cards: each tool = one atomic write; close: credit_lines status->repayment, draw_period_end_date=today, minimum_payment_due=arg; fee tools: one line_transactions entry (event fixed in the tool, related_txn_id = the object) and outstanding_balance +/- amount; receipts str(dict) with every field described. No tool checks a prerequisite or returns an error.

### XF_recipe.md — 14 points, task 0 policies
1. Factor independence — scratch sweep xf_sweep.py: no factor binding reads another factor's binding (0 issues). Factor-read table:
   | policy | factor | reads (own bindings) | plain bindings read |
   |---|---|---|---|
   | close_to_draws | conversion_term_band | MONTHS(open_date) | conversion_balance |
   | close_to_draws | affordability_extension | XMAX loan installments, EXISTS active current loan | — |
   | close_to_draws | return_addon | COUNT returns 12m, autopay_enrolled | — |
   | close_to_draws | relationship_reduction | XCOUNT loan late fees 12m, EXISTS active loan | — |
   | close_to_draws | repayment_method_by_use | COUNT draws 12m, credit_limit | conversion_balance |
   | close_to_draws | accrued_interest_treatment | DAYS(last closing, now), autopay_enrolled | last_statement_closing |
   | returned fee | first_return_share | COUNT returns 12m, MONTHS(open) | — |
   | returned fee | returned_fee_figuring | LATEST return code | latest_return_amount |
   | returned fee | loan_relationship_credit | XCOUNT loan AutoPay payments 12m, EXISTS | — |
   | returned fee | standing_credit | COUNT line late fees 12m, autopay_enrolled | — |
   | draw fee | seasoned_fee_rate | MONTHS(open), COUNT late fees 12m | — |
   | draw fee | draw_size_points | LATEST draw amount, credit_limit | — |
   | draw fee | frequent_drawer_figuring | COUNT draws 12m | drawn_amount |
   | draw fee | personal_loan_fee_credit | XCOUNT loan late fees 12m, EXISTS active current loan | — |
   | draw fee | back_billing_relief | COUNT lender-error waivers 12m, autopay_enrolled | — |
   | error credit | interest_putback_method | DAYS(fee date, closing) | extra_fee_date, credit_last_closing |
   | error credit | service_recovery_amount | COUNT lender-error waivers 12m, MONTHS(open) | — |
   | error credit | autopay_courtesy_amount | COUNT AutoPay payments 12m | — |
   | error credit | personal_loan_goodwill | XLATEST loan disbursement, EXISTS | — |
   | error credit | extra_entry_rebate | COUNT draws 12m | extra_fee_amount |
   Results are assembled only in plain bindings / result.
2. Assembly stated once, generically, order fixed: each rule ends with one assembly sentence ("first the APR used ... then the number of months ... then the amount repaid ... then the way of figuring ... then any amount added once ... rounded"; "first the figured fee ... scaled by the share ... every credit taken off ... never below 0.00 / above the minimum payment due ... rounded"; draw fee: rate, figure, raise to the minimum, credits, floor 0, round; error credit: sum then round). Non-commuting steps (minimum before credits; capitalization before the method) are ordered explicitly.
3. Factor-only quantities defined in their factor sentences (accrued interest in the accrued-interest sentence; proportional fee in the figuring sentence; equal share in the payment-method sentence; rebate in the rebate sentence). Baselines name no factor quantity.
4. Overwrite hygiene: close_to_draws retires the level-payment sentence only for borrower closings and restates it for draw-period ends; returned fee retires the flat-fee clause only for the most recent return and restates the flat fee for earlier ones; draw fee retires the draw-fee clause for the most recent draw (earlier draws keep the tier percent) and the active-status gate only for fees on draws already made (new draws still need active status); error credit retires the Larkspur-error clause only for the latest duplicated draw fee and names the late/returned-fee case as outside it (the task-1 sibling). No rule defers to a clause its overwrite retires.
5. compute_basis quotes verbatim: xf_sweep.py checks every quote is a whitespace-normalised substring of its rule — 0 issues; every baseline sentence is in its rule.
6. Rounding: root rounds once at the end (RND on result) with accrued interest rounded in its own sentence; returned fee rounds the proportional figure and the result; draw fee rounds the figured fee and the result; error credit rounds interest, rebate and the sum — each matches a RND in compute.
7. Docstrings: describe only effects the bodies have (one entry + balance, or status/date/minimum); no example values, no ordering words, no other tool names.
8. Edge probes (probe.py on scratch copies): no loan rows -> 39.51 / 5.00 / 9.50 / 165.33, no exception; decoy paid-off loan -> unchanged (EXISTS status filters); active loan past due -> affordability and draw-fee credit fall through (5.00 / 164.04); no statement closing -> open date used (stated in rule). Ties: duplicated draw fees are distinguished by booking date (rule: later-booked is the extra); two returns on one latest date -> the first recorded (stated; LATEST keeps the first). Month-end and 12-month windows: each rule states "a month counting only once the current date's day of the month reaches the start date's day" and "entries dated after the same day of the month 12 months before" (= MONTHS / within_months semantics). Entries vs periods: counts are of entries and the rules say entries/payments/draws, never statements. Exclusions stated (lender-error waivers only; AutoPay channel only; scheduled installments only) are compute filters.
9. Method tiers change formula shape — pairwise tier table with distinguishing input:
   | factor | tier A | tier B | tier C (fall-through) | distinguishing input |
   |---|---|---|---|---|
   | repayment_method_by_use | B/n + B*r | max(level, last minimum) | level amortizing | B=2,641.60, n=30, r=24.49/1200: 141.96 / 118.61 vs min 66.90 -> 118.61 / 118.61 — A differs from B,C; B vs C differ when last minimum > level (e.g. minimum 150.00 -> 150.00 vs 118.61) |
   | accrued_interest_treatment | capitalize into B | add once to payment | none | 40.55 interest on 2,601.05 (equal-share method): 141.96 / 139.78 + 40.55 = 180.33 / 139.78 (all distinct) |
   | returned_fee_figuring | min(fee, 2.5% x amt) | max(fee, 2.5% x amt) | flat fee | amount 500: 12.50 / 15.00 / 15.00; amount 1,200: 15.00 / 30.00 / 15.00 — each pair separated by one of the two inputs |
   | frequent_drawer_figuring | rate x (draw-100) | rate x 500 + rate/2 x (draw-500) | rate x draw | draw 400 @2%: 6.00 / (n/a, tier needs >=500) / 8.00; draw 900 @2%: 16.00 / 14.00 / 18.00 |
   | interest_putback_method | fee x APR/36500 x days | fee x APR/1200 | 0 | 30.00, 25 days: 0.51 / 0.62 / 0 |
10. No factor id is a substring of any tool name (sweep: 0 hits).
11. No cross-record date pairing is computed; record selections are "most recent" entries scoped by self-naming overwrites.
12. Realism: relationship pricing and service-recovery credits for a lender error, risk-based repayment terms, proportional NSF fee for small insufficient-funds returns, back-billing relief after a lender error; seeded loan rows are states loan_evt_* produce (AutoPay installments, a schedule_a late fee paid the next month). No fee on interest never billed; no fee raised after closing; credits never pyramid.
13. frozen_time "2026-10-16 11:20:00 MST"; task_tools.py imports nothing but erlbench; every write tool calls ctx.update/create itself; no date maths needed in tools.
14. Proof text swept after each revision (rationale, closure, necessity, traces): figures re-taken from the harness (skip runs 144.28 / 141.75 / 141.50; permutation runs identical).

### Gates (task 0)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK · CACHE-DIFF INFO

## Task 1 — largest draw on a FlexLine Premier after a missed payment
Tools (uuid8 drawn one by one): post_line_draw_ce97e56d (agent), pay_past_due_amount_8ea5bc66 (user), assess_late_fee_ba469c06 (agent), waive_fee_charged_in_error_c67a36f8 (agent).
Capability cards: draw — one draw entry to the named linked account + balance; payment — one online bank-transfer payment entry, balance, minimum payment due and amount past due lowered, next due date moved one month once the past due reaches 0.00 (date step done in the _DueDates static method; no date library); late fee — one entry for the named due date + balance; waiver — one lender_error waiver entry against the fee + balance. No tool checks a prerequisite or returns an error.
Chain: late-fee error waiver -> late fee -> past-due payment (user) -> largest draw; all three edges state form, value_input.

### XF_recipe.md — 14 points, task 1 policies
1. Factor independence (xf_sweep.py, 0 issues). Factor-read table:
   | policy | factor | reads (own bindings) | plain bindings read |
   |---|---|---|---|
   | largest draw | interest_cushion_method | LATEST closing, autopay_enrolled | draw_balance, draw_limit |
   | largest draw | delinquency_reserve | COUNT late fees 12m, COUNT lender-error waivers 12m, XSUM loan principal 12m | — |
   | largest draw | returned_payment_reserve | COUNT returns 12m by code | — |
   | largest draw | single_draw_share | MONTHS(open) | — |
   | largest draw | draw_period_taper | MONTHS(now, draw period end) | — |
   | past-due payment | missed_date_paydown_share | COUNT late fees 12m, COUNT lender-error waivers 12m, autopay_enrolled | — |
   | past-due payment | seasoning_allowance | MONTHS(open) | — |
   | past-due payment | personal_loan_allowance | XCOUNT loan late fees 12m, EXISTS active loan | — |
   | past-due payment | returned_account_adjustment | COUNT returns 12m (R02/R03/R04 and all) | — |
   | past-due payment | current_minimum_treatment | DAYS(next due, now), autopay_enrolled | — |
   | late fee | first_miss_share | COUNT late fees 12m, COUNT lender-error waivers 12m, MONTHS(open) | — |
   | late fee | unpaid_minimum_figuring | MONTHS(open) | unpaid_minimum |
   | late fee | loan_repayment_credit | XSUM loan principal 12m | — |
   | late fee | payment_history_credit | COUNT payments 12m | — |
   | late fee | unused_courtesy_credit | COUNT courtesy waivers 12m, tier courtesy allowance | — |
   | waiver | interest_reversal_method | DAYS(fee date, closing), autopay_enrolled | erroneous_fee_date, waiver_last_closing |
   | waiver | error_service_recovery | COUNT lender-error waivers 12m, MONTHS(open) | — |
   | waiver | loan_principal_goodwill | XSUM loan principal 12m | — |
   | waiver | courtesy_tier_rebate | LATEST late-fee amount, tier courtesy allowance | — |
   | waiver | payment_courtesy | COUNT payments 12m | — |
2. Assembly once, generic, ordered: draw ("first every amount kept back ... never below 0.00; then multiplied by every share; then rounded down to the whole dollar; then held to the daily maximum; below the minimum draw -> 0"); payment ("first the good-standing share ... then the paydown ... rounded and never below 0.00; then the current-minimum treatment; then the past due and the late fee are added; rounded"); late fee (figure, share, credits, floor 0 / cap unpaid minimum, round); waiver (sum, round).
3. Factor-only quantities in their own sentences (cushion interest, current minimum, rebate, interest reversed); baselines name none.
4. Overwrites: largest draw retires the draw-limits sentence only for a draw asked to be as large as allowed and restates it for every other draw; late fee retires the flat-amount clause (same scope: the late fee amount); late-fee error waiver retires the Larkspur-error clause only for the most recent late fee charged in error and names draw fees as outside it (task 0's sibling names late/returned-payment fees as outside its own) — the two siblings each exclude the other's case; past-due payment has overwrite [] (no base sentence fixes that amount).
5. compute_basis quotes verbatim — sweep 0 issues (both tasks).
6. Rounding: draw rounds down once (int) after the shares; cushion interest rounded to the cent in its sentence; payment rounds the paydown and the sum; late fee rounds the figured fee and the result; waiver rounds interest, rebate and the sum.
7. Docstrings: effects only as the bodies do them; no example values, no ordering words, no other tool names.
8. Edge probes (probe1.py, scratch copies): no loan rows -> 36.27 / 11.33 / 1,134.79 / 753, no exception; decoy paid-off loan -> unchanged; AutoPay on -> payment 248.14 (no paydown tier), draw 549; a second late fee on the same latest date -> the one recorded first is read (rule now states it; same for draws and draw-fee entries). No-statement case: the open date stands in (stated). Month and window conventions stated in every rule. Entries, not periods, are counted, and the rules say so.
9. Method tiers — pairwise table with distinguishing inputs:
   | factor | tier A | tier B | tier C | distinguishing input |
   |---|---|---|---|---|
   | interest_cushion_method | bal x APR/1200 | bal x APR/36500 x days since closing | 0 | 12,777.26 @15.99, 13 days: 170.26 / 72.77 / 0 |
   | current_minimum_treatment | paydown + current min | max(paydown, current min) | paydown | 308.91 & 272.74: 581.65 / 308.91 / 308.91; current min 400.00: 708.91 / 400.00 / 308.91 |
   | unpaid_minimum_figuring | min(25, 10% x unpaid) | max(25, 5% x unpaid) | 25 flat | 238.81: 23.88 / - / 25.00; 600.00: - / 30.00 / 25.00 |
   | interest_reversal_method | fee x APR/36500 x days | fee x APR/1200 | 0 | 25.00, 25 days @15.99: 0.27 / 0.33 / 0 |
10. No factor id is a substring of a tool name (sweep).
11. No cross-record date pairing computed; "most recent" selections scoped by self-naming overwrites/scope sentences.
12. Realism: risk-based draw reserves after a missed payment and a returned (closed-account) payment, a good-standing paydown before draws resume, smaller late fees for first misses and small unpaid minimums, relationship credits from a personal loan being repaid, service recovery for a fee charged in error; loan rows are states loan_evt_* produce (AutoPay installments moved to the new bank, one late installment with its schedule_a fee). Late fee never exceeds the unpaid minimum; no fee on unbilled interest.
13. frozen_time "2026-10-16 14:05:00 CDT"; task_tools.py has no imports besides erlbench; the next-due-date step is a class static method; every write tool calls ctx.create/update in its own body.
14. Proof text swept after each revision (dossier, closure, necessity, traces): all figures re-taken from the harness (skip runs 18.88/3,128.61/2,293; 511.55/923; 0; reorder run 27.88/850.73).

## Final difficulty run (no --task)
- EXTENDED OK · TASK TOOL CONTRACT OK (8 tools) · REPLAY OK (0.json 153/153, 1.json 143/143) · SOLVABILITY OK · COMPUTE OK (suite branches mean 68.00, steps 15.00, history_rows_max 129, branches_max 72) · GROUNDING OK · SCOPE OK · CACHE-DIFF INFO (optional).
- check_traceability (pre-render): 8 misses, all unlock_*_discoverable_tool tool_name values (the 8 hidden tool names, published only once the KB is rendered); 0 other misses.
- Coverage: task 0 {line_ext_draw_fee_error_credit, line_ext_draw_fee, line_ext_returned_payment_fee, line_ext_close_to_draws_payment}; task 1 {line_ext_late_fee_error_waiver, line_ext_late_fee, line_ext_past_due_payment, line_ext_largest_draw} — disjoint, all 8 covered.
- Scratch authoring scripts under /tmp/flexline_credit_line_0067/ removed.
REWORK round 1: gates 7/7 green

## REWORK round 2 (audits/policy_task/flexline_credit_line/0.md, 1.md, _difficulty.md)
Audit read in full: CG-1..CG-12 (charter), F-0a..F-0e (task 0), F-1a..F-1d (task 1), observations O-0a..O-0d, O-1a..O-1c.
Every struck factor class was closed across all eight policies, not only where it was reported.

### New design (8 distinct cores, disjoint scopes)
- Task 0 (Marisol Pereira, FlexLine Standard, ACTIVE, 28 days past due on the 2026-09-18 minimum; Standard freezes at 30 days, so the closing is allowed - CG-1/F-0a):
  root line_ext_close_to_draws_payment (user, 6 factors) <- line_ext_late_fee (5), line_ext_limit_review (5), line_ext_workout_fee_relief (4); workout relief <- late fee.
- Task 1 (Desmond Okafor, FlexLine Plus, current; R02 return of the 2026-09-14 AutoPay payment, replaced in part on 2026-09-23; 2026-09-10 draw posted without its fee; increase request of 2026-10-09 pending his hard-inquiry consent):
  root line_ext_limit_increase (user, 5) <- line_ext_returned_payment_fee (5), line_ext_backbilled_draw_fee (5), line_ext_returned_fee_relief (5); replacement relief <- returned-payment fee.
- Struck and not reused: draw-fee error credit, late-fee error waiver, past-due cure payment, largest-draw holdbacks (CG-5, CG-6, CG-9, CG-10).
- Draw counts kept: task 0 prerequisite_problems=3 factor_counts=[6,4,5,5]; task 1 prerequisite_problems=3 [5,5,5,5].

### Class closures applied to every policy
- Methods change formula shape (CG-3): every method tier is a different formula (min/max of flat and percent, kept-base vs graduated vs whole cut, equal-share vs max(level, minimum) vs level, re-age vs spread vs whole, largest vs larger-of vs latest fee, fee-free portion vs graduated vs whole draw, fee-less-loan-waiver vs min(fee, flat) vs fee, graduated vs above-base vs whole increase). No period-length, multiplier, window or constant ladders.
- AutoPay (CG-4): no compute binding of any policy reads autopay_enrolled or AutoPay payments.
- Small credits / goodwill / rebates (CG-5): none; fee schedules are formula fees (percent with flat floor/ceiling) and shares tied to the obligation itself; relationship effects only as exposure or a shared bank event.
- Waivers never above the fee (CG-6): both reliefs are a share of, or capped by, the fee they are booked against; tool books against that fee.
- Rate (CG-7): the repayment payment uses F('line_apr') only; no rate add-ons.
- Interest (CG-8): no unbilled interest folded in or added once; the equal-share tier adds one month of interest at the line APR as part of a fixed payment.
- Cure / holdback (CG-9, CG-10): no cure amount, no availability holdback anywhere.
- Seasoning (CG-11): tenure only reduces a fee (draw-fee tenure points are taken off, never added).
- Netting (CG-12): every count is a plain count of entries of one event type; no count nets waivers.
- Base conflicts (CG-2/F-0b): the close overwrite now retires exactly "in repayment it is the level repayment payment plus any amount past due." and restates it for every line not closed by the borrower; the non-conflicting draw-period clause is no longer retired. The two reliefs share one overwrite of the courtesy-waiver sentence (granted without a request under their own paragraphs, still inside the courtesy count); the workout relief alone retires the request window.

### XF recipe, 14 points, per policy (round 2)
| # | close (C) | late fee (LF) | limit review (LDEC) | workout relief (WO) | returned fee (R) | back-billed draw fee (D) | limit increase (LI) | replacement relief (RELIEF) |
|---|---|---|---|---|---|---|---|---|
| 1 factor independence | each of 6 factors moves the result alone; no factor reads another's binding (script) | 5/5 alone | 5/5 alone | 4/4 alone | 5/5 alone | 5/5 alone; draw-size reads its own copy of the draw amount | 5/5 alone | 5/5 alone; cover reads its own SUM copy |
| 2 assembly once, ordered | "assembled in this order" sentence: months, payment, past-due part, round | figured fee, shares, cap, round | cut, tenure, apply, step, floors | fee chosen, shares, round | figured fee, shares, cap, round | percent, figure, floor, share, round | figure, shares, add+step, caps | basis, shares, round |
| 3 factor-only quantities | own sentences per factor; baseline names none | same | same | same | same | same | same; requested-limit sentence added | same |
| 4 overwrite hygiene | retires only the level-payment sentence for borrower closings, restates it for others | retires flat late-fee clause for still-unpaid due dates, restates flat fee for paid-late ones | none needed (lender review adds to base) | window clause + shared courtesy clause | flat-fee clause for the most recent return only | draw-fee clause for the most recent fee-less draw; status clause for back-billing only | increase clause (30-days-late criterion, amount by paragraph) | shared courtesy clause |
| 5 compute_basis verbatim | sweep 0 issues | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 rounding | rounded once at the end | RND fee once | int step + ceil floor | RND once | RND once | RND figure, RND result | int step | RND once |
| 7 docstrings | effects only, no example values | same | same | same | same | same | same (new tool) | same (new tool) |
| 8 edges | probes below (no loan, no past due, term floor) | tie, absent loan fee, no grace payment, 0 past due, grace day 11 | paid-off loan decoy, exact-multiple floor, not past due | tie of equal fees, lender-error decoy, no late fee | same-day return tie, no loan return, other customer's loan, 0 minimum, month-end | same-day draw tie, 0-percent tier, other line's draw | approved/declined request decoys, paid-off loan, no loan | no replacement, no fee, older-return decoy, same-day replacements, loan fee waived/absent |
| 9 method shapes | 2 methods, tables below | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 10 factor id not in tool names | sweep 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11 cross-record date pairing | none (same-date match only via txn_date filter) | loan due date vs line due date by DAYS on two read values | none | none | same-date filter | none | none | same-date filter |
| 12 realism | equal-share or level amortization at the line APR; term extension for a current loan and a workout | late fee capped by the unpaid minimum, smaller for a partial payment in grace | lender CLD for 15+ days past due, deeper for returns and loan lates | workout concession on a late fee, never above it | percent fee on large returns, one bank event across products shares | back-billed fee shrinks with delay; tenure only lowers | CLI sized by late history, usage, NSF count, total exposure | relief for a replaced return, scaled by speed, cover and reason |
| 13 runtime | frozen_time 2026-10-16 11:20:00 MST; only erlbench import | - | - | - | frozen_time 2026-10-16 14:05:00 CDT | - | - | - |
| 14 proof text | dossier, closure, necessity, traces rebuilt from the replay after the last change | same | same | same | same | same | same | same |

### line_ext_late_fee (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| late_history_share | parameter | late_entries_12m, late_history_share | COUNT | 0.9 |
| unpaid_part_figuring | method | days_late_now, unpaid_figuring_code | DAYS | 1 |
| grace_payment_share | parameter | grace_payment_date, grace_payment_amount, grace_payment_share | DAYS, F, LATEST | 0.9 |
| late_fee_tenure_share | parameter | late_line_age, late_tenure_share | F, MONTHS | 0.95 |
| same_month_loan_share | parameter | loan_late_due_date, same_month_loan_share | DAYS, XLATEST | 0.75 |

unpaid_part_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | small_unpaid_percent percent of the unpaid part, rounded to the cent, never more than the tier's late fee (the smaller of the two) | 5.08 |
| 2 | the larger of the tier's late fee and large_unpaid_percent percent of the unpaid part | 14.43 |
| 0 | the tier's late fee as a flat amount | 14.43 |

### line_ext_workout_fee_relief (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| delinquency_depth_share | parameter | relief_days_late, depth_share | DAYS, F | 0.75 |
| prior_relief_share | parameter | courtesy_waivers_12m, courtesy_waivers_24m, prior_relief_share | COUNT | 0.75 |
| relief_tenure_share | parameter | relief_line_age, relief_tenure_share | F, MONTHS | 0.9 |
| relief_fee_choice | method | relief_late_fees_12m, recent_returned_fees, fee_choice | COUNT | 1 |

relief_fee_choice pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the largest late fee on the line (of equal amounts, the most recently booked) | 12.66 |
| 2 | the larger of that late fee and the most recent returned-payment fee | 7.59 |
| 0 | the most recent late fee | 2.57 |

### line_ext_limit_review (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| lateness_cut | parameter | review_days_late, lateness_cut | DAYS, F | 0.1 |
| return_cut | parameter | review_returns_12m, return_cut | COUNT | 0.05 |
| personal_loan_cut | parameter | review_loan_late_fees_12m, loan_cut | EXISTS, XCOUNT | 0.05 |
| review_tenure_relief | parameter | review_line_age, tenure_relief | F, MONTHS | 0.75 |
| cut_application | method | cut_way | F, MONTHS | 1 |

cut_application pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the first protected_base_usd of the limit is kept and the cut applies only to the part above it | 3300.0 |
| 2 | the cut applies to the first graduated_first_usd and twice the cut to the part above it | 3300.0 |
| 0 | the cut applies to the whole limit | 3100.0 |

### line_ext_close_to_draws_payment (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| conversion_term_band | parameter | line_age_months, conversion_term_band | F, MONTHS | 24 |
| affordability_extension | parameter | largest_loan_installment, affordability_months | EXISTS, XMAX | 6 |
| recent_draw_trim | parameter | recent_draw_total, recent_draw_trim | F, SUM | 3 |
| workout_extension | parameter | days_late_at_closing, workout_months | DAYS, F | 6 |
| repayment_method_by_use | method | line_draws_12m, payment_method_code | COUNT, F | 2 |
| past_due_treatment | method | late_fee_entries_12m, past_due_mode | COUNT, F, MONTHS | 2 |

repayment_method_by_use pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 2 | one equal share of the amount repaid (amount divided by the number of months) plus one month of interest on the whole amount at the monthly rate | 144.54 |
| 1 | the larger of the level payment and the current-cycle minimum (minimum payment due less amount past due) | 121.35 |
| 0 | the level payment that repays the amount over the number of months | 121.35 |

past_due_treatment pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | re-age: the amount past due stays in the balance repaid and nothing is added to the payment | 132.8 |
| 2 | spread: one spread_payment_count-th of the amount past due, rounded to the cent, is added to the payment | 144.54 |
| 0 | the whole amount past due is added to the payment | 168.01 |

### line_ext_returned_payment_fee (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| return_history_share | parameter | returns_last_12m, returns_last_24m, return_history_share | COUNT | 0.85 |
| returned_fee_figuring | method | charged_return_code, fee_figuring_code | LATEST | 2 |
| late_booking_share | parameter | booking_lag_months, late_booking_share | MONTHS | 0.9 |
| shared_return_event | parameter | loan_returns_same_day, loan_return_fees_same_day, shared_event_share | XCOUNT | 0.75 |
| line_tenure_share | parameter | fee_line_age, tenure_share | F, MONTHS | 0.95 |

returned_fee_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | proportional_percent percent of the amount returned, rounded to the cent, never more than the tier's returned-payment fee (the smaller of the two) | 8.18 |
| 2 | the larger of the tier's returned-payment fee and proportional_percent percent of the amount returned | 16.35 |
| 0 | the tier's returned-payment fee as a flat amount | 8.18 |

### line_ext_backbilled_draw_fee (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| draw_size_points | parameter | sized_draw_amount, draw_size_points | F, LATEST | 0.5 |
| recent_use_points | parameter | recent_use_total, recent_use_points | F, SUM | 0.5 |
| draw_fee_tenure_points | parameter | fee_line_age, tenure_points | F, MONTHS | 0.25 |
| frequent_drawer_figuring | method | draws_last_12m, fee_figuring_way | COUNT | 2 |
| backbilling_share | parameter | backbill_lag_months, backbill_share | MONTHS | 0.9 |

frequent_drawer_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the percent is charged only on the part of the draw above fee_free_portion_usd | 56.93 |
| 2 | the full percent on the first graduated_threshold_usd and half the percent on the rest of the draw | 35.89 |
| 0 | the percent on the whole draw | 59.4 |

### line_ext_returned_fee_relief (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| replacement_timing_share | parameter | replacement_days, timing_share | DAYS | 0.8 |
| replacement_cover_share | parameter | cover_replaced_total, cover_share | SUM | 0.75 |
| return_reason_share | parameter | relief_return_code, reason_share | LATEST | 0.85 |
| relief_late_history | parameter | relief_late_fees_12m, relief_late_share | COUNT | 0.8 |
| bank_event_relief_basis | method | loan_fee_same_day_id, loan_fee_waived_amount, relief_basis_way | XLATEST, XSUM | 2 |

bank_event_relief_basis pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the line's fee less the amount waived on that loan fee, never below 0.00 | 6.67 |
| 2 | the smaller of the line's fee and the tier's flat returned-payment fee | 6.12 |
| 0 | the line's fee | 6.67 |

### line_ext_limit_increase (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| increase_late_history | parameter | increase_late_fees_24m, late_history_scale | COUNT | 0.75 |
| increase_usage_scale | parameter | usage_balance, usage_scale | SUM | 0.8 |
| increase_returned_fee_scale | parameter | returned_fee_entries_12m, returned_fee_share | COUNT | 0.75 |
| combined_exposure_scale | parameter | loan_principal_now, exposure_scale | CFIELD | 0.9 |
| increase_figuring | method | increase_way | F, MONTHS | 1 |

increase_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the maximum increase percent on the first graduated_first_usd and half of it on the rest of the limit | 8700.0 |
| 2 | the maximum increase percent only on the part of the limit above protected_base_usd | 8800.0 |
| 0 | the maximum increase percent on the whole limit | 8900.0 |
### Probe table (scratch copies of each task world at the policy's handling time; expectation from the rule tier)
| policy | probe | result | vs rule |
|---|---|---|---|
| returned_payment_fee | tie: second return same date recorded later | 19.24 | PASS |
| returned_payment_fee | absent: no loan return on the date (loan rows removed) | 21.8 | PASS |
| returned_payment_fee | decoy: other customer loan return same date | 16.35 | PASS |
| returned_payment_fee | edge: minimum payment due 0.00 caps fee at 0 | 0.0 | PASS |
| returned_payment_fee | month-end: return 2026-08-31 -> 1 month on 10-16 | 21.8 | PASS |
| backbilled_draw_fee | tie: second draw same date recorded later | 35.89 | PASS |
| backbilled_draw_fee | edge: 0-percent tier gives no back-billed fee | 0 | PASS |
| backbilled_draw_fee | decoy: draw on another line not counted | 35.89 | PASS |
| returned_fee_relief | absent: no replacement payment -> no relief | 0 | PASS |
| returned_fee_relief | absent: fee not booked -> no relief | 0 | PASS |
| returned_fee_relief | decoy: payment recorded against an older return ignored | 6.12 | PASS |
| returned_fee_relief | second replacement same day: cover adds up, timing same | 8.16 | PASS |
| returned_fee_relief | loan fee waived in full -> basis fee less 15.00 | 0.55 | PASS |
| returned_fee_relief | absent: no loan fee that day -> basis is the line fee | 6.67 | PASS |
| limit_increase | decoy: older approved increase request not the cap | 8700.0 | PASS |
| limit_increase | absent: no pending request -> cap is current limit | 8000.0 | PASS |
| limit_increase | decoy: paid-off second loan ignored by exposure | 8700.0 | PASS |
| limit_increase | absent: no active loan -> exposure full | 8800.0 | PASS |
| late_fee | tie: second payment same date as the latest, recorded later | 5.08 | PASS |
| late_fee | absent: no loan late fee -> loan share full | 6.77 | PASS |
| late_fee | absent: no payment after the due date -> grace share full | 5.64 | PASS |
| late_fee | edge: nothing past due -> fee held to 0.00 | 0.0 | PASS |
| late_fee | grace boundary: payment on day 10 counts, day 11 does not | 5.64 | PASS |
| workout_fee_relief | tie: equal largest late fees -> amount is the same 25.00 | 12.66 | PASS |
| workout_fee_relief | decoy: lender-error waiver not a courtesy waiver | 12.66 | PASS |
| workout_fee_relief | absent: no late fee at all -> relief 0.00 | 0.0 | PASS |
| limit_review | decoy: paid-off loan ignored by the loan cut | 3300.0 | PASS |
| limit_review | edge: balance floor exact multiple stays | 3400.0 | PASS |
| limit_review | edge: not past due -> no lateness cut | 3500.0 | PASS |
| close_to_draws_payment | absent: no loan -> no affordability months | 162.03 | PASS |
| close_to_draws_payment | decoy: loan additional-principal payment not an installment | 144.54 | PASS |
| close_to_draws_payment | edge: no amount past due -> nothing added, no workout months | 150.29 | PASS |
| close_to_draws_payment | edge: term floor 12 months holds | 15.96 | PASS |
Probe-driven fixes: grace-payment tie rule added to the late fee; 'largest scheduled installment payment ever posted' wording in the close (the compute reads posted installments); requested-limit selection sentence (latest pending request, first recorded on a tie, current limit when none) in the increase; zero-percent tiers return 0.00 in the back-billed draw fee.

### Round 2 final difficulty run (no --task)
- EXTENDED OK · TASK TOOL CONTRACT OK (8 tools) · REPLAY OK (0.json 152/152, 1.json 158/158) · SOLVABILITY OK (base gates 5 / 4, seed rows 113 / 124) · COMPUTE OK (suite branches mean 69.00, steps 16.00, history_rows_max 152, branches_max 69) · GROUNDING OK · SCOPE OK (cross-fire).
- check_traceability (pre-render): 8 misses, all unlock_*_discoverable_tool tool_name values (the 8 hidden tool names, published only once the KB is rendered); 0 other misses.
- check_cache_diff: info only (no cache re-check trap used).
- Coverage: task 0 {line_ext_late_fee, line_ext_workout_fee_relief, line_ext_limit_review, line_ext_close_to_draws_payment}; task 1 {line_ext_returned_payment_fee, line_ext_backbilled_draw_fee, line_ext_returned_fee_relief, line_ext_limit_increase}; disjoint, all eight covered.
- Claims per audit item: rework_r2_claims.md.
- Scratch authoring scripts under /tmp/flexline_credit_line_0067/ removed.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audits revision_2: R2-CG-2, R2-CG-3, R2-CG-8, R2-N1, R2-N2, R2-N3, R2-N4; task items F-0r2a..d, F-1r2a..b)
Every class was swept across all eight policies.

### Class closures
- R2-CG-2 (undeclared departures, incl. parameter and event-field descriptions): close adds a second scoped overwrite retiring the draw-period level-payment sentence; its replaced_by names the tier's repayment payment method and the closing record's level repayment-period payment. Late fee, returned fee and back-billed draw fee replaced_by sentences now name the tier parameter they replace (late_fee_usd, returned_payment_fee_usd, draw fee percent); the back-billed draw fee names its booking date against the draw-date field; the increase names limit_increase_min_on_time_payments; the limit review declares the lender-initiated decrease against the base "request" sentence and the limit-change record's meaning.
- R2-CG-3 (methods): close's past-due treatment (a multiplier) removed; workout relief's fee choice (substituted input) replaced by relief_figuring: fee less a retained part / the amount past due / the whole fee. Pairwise tables below.
- R2-CG-8 (stored effect for every month): the amount past due is repaid inside the balance; nothing is added to the payment; the rule states the repayment payment is one fixed amount, recorded as the minimum payment due and owed every month until repaid (equal-share repays before the term ends).
- R2-N1 / R2-N3 (realism): late fee's same-month loan share replaced by a balance-tier share (smaller fee on a smaller balance); back-billed draw fee's size and recent-use surcharges became point reductions (draw size, payment record); no tier anywhere lowers a fee for worse behaviour or raises only the lender's missed billing.
- R2-N2 (one write per state): the close now waits on a courtesy waiver against a late fee; the workout relief books against late fees only, the replacement relief against returned-payment fees only. Every other waited-on record (late-fee entry, decided decrease row, returned-fee entry, draw-fee entry, waiver on a returned fee) has one producing tool.
- R2-N4 (edges bear weight): workout relief <- late fee is value_input (relief_way: one -> two late fees in 12 months); increase <- back-billed draw fee is value_input (recent_draw_charges: the increase's draw-intensity share reads draws with their draw fees in 3 months, replacing its late-history share). Skip runs: every edge moves a scored value (see dossiers).
- Zero outcomes stated in every write rule: late fee and returned fee book a 0.00 entry; back-billed draw fee is never 0.00 on a fee tier and nothing on a 0.00 tier; workout and replacement relief book a 0.00 entry when due (nothing when no fee/replacement); limit review and increase never 0.00, recorded at the current limit when unchanged; close never sets a payment on a 0.00 balance (closed outright).
- Rounding: every rule states that an exact half cent goes to the even cent (the DSL rounding); probed.
- World: task 1 re-seeded (July draw lowered, October payment tuned) so the draw charges sit just under the 65 percent mark before the back-billed fee and the ledger just above the 80 percent mark before the relief.

### XF recipe, 14 points, per policy (round 3)
| # | C | LF | LDEC | WO | R | D | LI | RELIEF |
|---|---|---|---|---|---|---|---|---|
| 1 independence | 6/6 alone (script) | 5/5 | 5/5 | 4/4 | 5/5 | 5/5 | 5/5 | 5/5 |
| 2 assembly once | months, payment, round; fixed monthly amount | figure, shares, cap, round | cut, tenure, apply, step, floors | figure from fee, shares, round | figure, shares, cap, round | percent less points, figure, floor, share, round | figure, shares, add+step, caps | basis, shares, round |
| 3 factor-only quantities | own sentences | own sentences | own | own | own | own | own | own |
| 4 overwrite hygiene | two scoped overwrites, self-naming param+field | flat fee clause, names late_fee_usd | request sentence, names record meaning | window + shared courtesy clause | flat fee clause, names returned_payment_fee_usd | fee clause names percent and booking date; status clause | increase clause names min on-time param | shared courtesy clause |
| 5 basis verbatim | 0 issues | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 rounding | once, half-even stated | stated | int step | stated, 10.125 -> 10.12 probed | stated | stated | int step | stated |
| 7 docstrings | effects only | effects only | effects only | late fee only (updated) | effects only | effects only | effects only | effects only |
| 8 edges/zero | 0.00 balance closed outright; probes | 0.00 entry; balance tier boundary/decoy | never 0; floor exact multiple | 0.00 entry; never below 0; tie | 0.00 entry; tie, month-end | 0 tier nothing; month-end; points floor 0 | never 0; window boundary; decoys | 0.00 entry; absent fee/replacement |
| 9 method shapes | equal-share / max(level, minimum) / level | min / max / flat | kept base / doubled above / whole | fee - retained / past due / fee | min / max / flat | above free portion / graduated / whole | graduated / above base / whole | fee - loan waiver / min(fee, flat) / fee |
| 10 factor id not in tool names | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11 date pairing | none | none | none | none | same-date filter | none | none | same-date filter |
| 12 realism | risk term cut, workout term, affordability | first-miss, partial-in-grace, tenure, balance tier | lender CLD for delinquency | workout concession <= fee | % fee on large returns, shared bank event | only reductions on a late bill | CLI on draw intensity, usage, NSF, exposure | relief for replaced return |
| 13 runtime | frozen_time MST; erlbench import only | - | - | - | frozen_time CDT | - | - | - |
| 14 proof text | rebuilt from replay; swept | same | same | same | same | same | same | same |

### line_ext_late_fee (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| late_history_share | parameter | late_entries_12m, late_history_share | COUNT | 0.9 |
| unpaid_part_figuring | method | days_late_now, unpaid_figuring_code | DAYS | 1 |
| grace_payment_share | parameter | grace_payment_date, grace_payment_amount, grace_payment_share | DAYS, F, LATEST | 0.9 |
| late_fee_tenure_share | parameter | late_line_age, late_tenure_share | F, MONTHS | 0.95 |
| balance_tier_share | parameter | fee_ledger_balance, balance_tier_share | SUM | 0.8 |

unpaid_part_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | small_unpaid_percent percent of the unpaid part, rounded to the cent, never more than the tier's late fee (the smaller of the two) | 5.42 |
| 2 | the larger of the tier's late fee and large_unpaid_percent percent of the unpaid part | 15.39 |
| 0 | the tier's late fee as a flat amount | 15.39 |

### line_ext_workout_fee_relief (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| delinquency_depth_share | parameter | relief_days_late, depth_share | DAYS, F | 0.75 |
| prior_relief_share | parameter | courtesy_waivers_12m, courtesy_waivers_24m, prior_relief_share | COUNT | 0.75 |
| relief_tenure_share | parameter | relief_line_age, relief_tenure_share | F, MONTHS | 0.9 |
| relief_figuring | method | relief_late_fees_12m, relief_way | COUNT, F | 1 |

relief_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the fee less retained_usd, never below 0.00 | 10.12 |
| 2 | the amount past due | 17.83 |
| 0 | the whole fee | 12.66 |

### line_ext_limit_review (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| lateness_cut | parameter | review_days_late, lateness_cut | DAYS, F | 0.1 |
| return_cut | parameter | review_returns_12m, return_cut | COUNT | 0.05 |
| personal_loan_cut | parameter | review_loan_late_fees_12m, loan_cut | EXISTS, XCOUNT | 0.05 |
| review_tenure_relief | parameter | review_line_age, tenure_relief | F, MONTHS | 0.75 |
| cut_application | method | cut_way | F, MONTHS | 1 |

cut_application pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the first protected_base_usd of the limit is kept and the cut applies only to the part above it | 3300.0 |
| 2 | the cut applies to the first graduated_first_usd and twice the cut to the part above it | 3300.0 |
| 0 | the cut applies to the whole limit | 3100.0 |

### line_ext_close_to_draws_payment (task 0) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| conversion_term_band | parameter | line_age_months, conversion_term_band | F, MONTHS | 24 |
| affordability_extension | parameter | largest_loan_installment, affordability_months | EXISTS, XMAX | 6 |
| recent_draw_trim | parameter | recent_draw_total, recent_draw_trim | F, SUM | 3 |
| workout_extension | parameter | days_late_at_closing, workout_months | DAYS, F | 6 |
| repayment_method_by_use | method | line_draws_12m, payment_method_code | COUNT, F | 2 |
| late_history_term_cut | parameter | late_fee_entries_12m, late_term_cut | COUNT | 6 |

repayment_method_by_use pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 2 | one equal share of the amount repaid (amount divided by the number of months) plus one month of interest on the whole amount at the monthly rate | 150.45 |
| 1 | the larger of the level payment and the current-cycle minimum (minimum payment due less amount past due) | 126.88 |
| 0 | the level payment that repays the amount over the number of months | 126.88 |

### line_ext_returned_payment_fee (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| return_history_share | parameter | returns_last_12m, returns_last_24m, return_history_share | COUNT | 0.85 |
| returned_fee_figuring | method | charged_return_code, fee_figuring_code | LATEST | 2 |
| late_booking_share | parameter | booking_lag_months, late_booking_share | MONTHS | 0.9 |
| shared_return_event | parameter | loan_returns_same_day, loan_return_fees_same_day, shared_event_share | XCOUNT | 0.75 |
| line_tenure_share | parameter | fee_line_age, tenure_share | F, MONTHS | 0.95 |

returned_fee_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | proportional_percent percent of the amount returned, rounded to the cent, never more than the tier's returned-payment fee (the smaller of the two) | 8.18 |
| 2 | the larger of the tier's returned-payment fee and proportional_percent percent of the amount returned | 16.35 |
| 0 | the tier's returned-payment fee as a flat amount | 8.18 |

### line_ext_backbilled_draw_fee (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| draw_size_points | parameter | sized_draw_amount, draw_size_points | F, LATEST | 0.25 |
| payment_record_points | parameter | record_late_fees_12m, record_points | COUNT | 0.1 |
| draw_fee_tenure_points | parameter | fee_line_age, tenure_points | F, MONTHS | 0.25 |
| frequent_drawer_figuring | method | draws_last_12m, fee_figuring_way | COUNT | 2 |
| backbilling_share | parameter | backbill_lag_months, backbill_share | MONTHS | 0.9 |

frequent_drawer_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the percent is charged only on the part of the draw above fee_free_portion_usd | 28.98 |
| 2 | the full percent on the first graduated_threshold_usd and half the percent on the rest of the draw | 18.27 |
| 0 | the percent on the whole draw | 30.24 |

### line_ext_returned_fee_relief (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| replacement_timing_share | parameter | replacement_days, timing_share | DAYS | 0.8 |
| replacement_cover_share | parameter | cover_replaced_total, cover_share | SUM | 0.75 |
| return_reason_share | parameter | relief_return_code, reason_share | LATEST | 0.85 |
| relief_late_history | parameter | relief_late_fees_12m, relief_late_share | COUNT | 0.8 |
| bank_event_relief_basis | method | loan_fee_same_day_id, loan_fee_waived_amount, relief_basis_way | XLATEST, XSUM | 2 |

bank_event_relief_basis pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the line's fee less the amount waived on that loan fee, never below 0.00 | 6.67 |
| 2 | the smaller of the line's fee and the tier's flat returned-payment fee | 6.12 |
| 0 | the line's fee | 6.67 |

### line_ext_limit_increase (task 1) - factor reads
| factor | effect | bindings | records read | tier on the task world |
|---|---|---|---|---|
| draw_intensity_scale | parameter | recent_draw_charges, draw_intensity_scale | SUM | 0.8 |
| increase_usage_scale | parameter | usage_balance, usage_scale | SUM | 0.8 |
| increase_returned_fee_scale | parameter | returned_fee_entries_12m, returned_fee_share | COUNT | 0.75 |
| combined_exposure_scale | parameter | loan_principal_now, exposure_scale | CFIELD | 0.9 |
| increase_figuring | method | increase_way | F, MONTHS | 1 |

increase_figuring pairwise tiers (result with the method code forced, everything else as on the task world):
| tier | method | result |
|---|---|---|
| 1 | the maximum increase percent on the first graduated_first_usd and half of it on the rest of the limit | 8800.0 |
| 2 | the maximum increase percent only on the part of the limit above protected_base_usd | 8900.0 |
| 0 | the maximum increase percent on the whole limit | 9000.0 |
### Probe table round 3 (scratch copies at each policy's handling time)
| policy | probe | result | vs rule |
|---|---|---|---|
| returned_payment_fee | tie: second return same date recorded later | 19.24 | PASS |
| returned_payment_fee | absent: no loan return on the date (loan rows removed) | 21.8 | PASS |
| returned_payment_fee | decoy: other customer loan return same date | 16.35 | PASS |
| returned_payment_fee | edge: minimum payment due 0.00 caps fee at 0 | 0.0 | PASS |
| returned_payment_fee | month-end: return 2026-08-31 -> 1 month on 10-16 | 21.8 | PASS |
| backbilled_draw_fee | tie: second draw same date recorded later | 18.27 | PASS |
| backbilled_draw_fee | edge: 0-percent tier gives no back-billed fee | 0 | PASS |
| backbilled_draw_fee | decoy: draw on another line not counted | 18.27 | PASS |
| returned_fee_relief | absent: no replacement payment -> no relief | 0 | PASS |
| returned_fee_relief | absent: fee not booked -> no relief | 0 | PASS |
| returned_fee_relief | decoy: payment recorded against an older return ignored | 6.12 | PASS |
| returned_fee_relief | second replacement same day: cover adds up, timing same | 8.16 | PASS |
| returned_fee_relief | loan fee waived in full -> basis fee less 15.00 | 0.55 | PASS |
| returned_fee_relief | absent: no loan fee that day -> basis is the line fee | 6.67 | PASS |
| limit_increase | decoy: older approved increase request not the cap | 8800.0 | PASS |
| limit_increase | absent: no pending request -> cap is current limit | 8000.0 | PASS |
| limit_increase | decoy: paid-off second loan ignored by exposure | 8800.0 | PASS |
| limit_increase | absent: no active loan -> exposure full | 8900.0 | PASS |
| backbilled_draw_fee | points never take the percent below 0.00 (tier percent 0.5) | 18.27 | PASS |
| backbilled_draw_fee | clean record -> 0.25 points off | 16.31 | PASS |
| backbilled_draw_fee | month-end: draw 2026-08-31 -> one whole month on 10-16 | 18.27 | PASS |
| limit_increase | draw intensity: draw-fee entries counted with draws | 8800.0 | PASS |
| limit_increase | decoy: draw on another line not in draw charges | 8800.0 | PASS |
| limit_increase | window: draw dated exactly 3 months back (2026-07-16) excluded | 8600.0 | PASS |
| returned_fee_relief | rounding: exact half cent goes to the even cent | 6.12 | PASS |
| late_fee | tie: second payment same date as the latest, recorded later | 5.42 | PASS |
| late_fee | balance tier: ledger below 500.00 -> small share | 4.06 | PASS |
| late_fee | balance tier boundary: ledger exactly 3,000.00 -> full share | 6.77 | PASS |
| late_fee | decoy: entries of another line not in the ledger total | 5.42 | PASS |
| late_fee | absent: no payment after the due date -> grace share full | 6.02 | PASS |
| late_fee | edge: nothing past due -> fee held to 0.00 | 0.0 | PASS |
| late_fee | grace boundary: payment on day 10 counts, day 11 does not | 6.02 | PASS |
| workout_fee_relief | tie: equal largest late fees -> 25.00, repeat tier | 10.12 | PASS |
| workout_fee_relief | one late fee in 12 months, past due below the fee -> the amount past due | 10.12 | PASS |
| workout_fee_relief | repeat tier never below 0.00 (fee 4.00) | 0.0 | PASS |
| workout_fee_relief | rounding: 20.00 x 0.75 x 0.75 x 0.90 = 10.125 -> even cent 10.12 | 10.12 | PASS |
| workout_fee_relief | decoy: lender-error waiver not a courtesy waiver | 10.12 | PASS |
| workout_fee_relief | absent: no late fee at all -> relief 0.00 | 0.0 | PASS |
| limit_review | decoy: paid-off loan ignored by the loan cut | 3300.0 | PASS |
| limit_review | edge: balance floor exact multiple stays | 3400.0 | PASS |
| limit_review | edge: not past due -> no lateness cut | 3500.0 | PASS |
| close_to_draws_payment | absent: no loan -> no affordability months | 177.97 | PASS |
| close_to_draws_payment | decoy: loan additional-principal payment not an installment | 150.45 | PASS |
| close_to_draws_payment | edge: no amount past due -> no workout months, nothing added | 177.97 | PASS |
| close_to_draws_payment | late-history cut: one late fee -> 3 months | 140.82 | PASS |
| close_to_draws_payment | edge: term floor 12 months holds | 4.88 | PASS |

### Round 3 final difficulty run (no --task)
- EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK (cross-fire); check_traceability pre-render: 8 misses, all hidden tool names. Claims: rework_r3_claims.md. Scratch /tmp/flexline_credit_line_0067/ removed.
REWORK round 3: gates 7/7 green

## REWORK round 4 (audits/policy_kb, runtime_context, render_source: src-1, src-2, src-3, render_r1 edges)
- src-1 (floor that bites only on adjusted values): close's min_term_months floor left the assembly sentence and now sits in the two factor sentences that take months off ("the trim never takes the term below min_term_months"; "the cut never takes the term below min_term_months"); the assembly states the months added before the months taken off. Compute mirrors it (term_after_trim floored, then the cut floored); a sequential floor equals the floor on the total because every addition precedes every reduction (probed). Class sweep: every other floor/cap (late fee unpaid-part cap, returned fee minimum-due cap, draw fee minimum, review balance/minimum floors and new limit cap, increase requested/tier caps) can bind at baseline and stays in the baseline sentence; relief "never below 0.00" clauses already sit in the method tiers that produce them.
- src-2 (state form names the action): increase <- replacement relief now reads "The approved limit is fixed only after the returned-payment fee of a return that has a replacement payment recorded against it carries a courtesy fee-waiver entry."; condition adds the courtesy basis. Sweep of the other seven prerequisite sentences: each names an entry or row state (late-fee entry, decided decrease row, courtesy waiver against a late fee, returned-fee entry, draw-fee entry), none an action.
- src-3 (retired clauses live in extended hubs): kept as is — each retiring replaced_by restates the retired clause for every case outside its scope (request window for borrower-asked courtesy waivers; active status for new draws; level payment for lines whose draw period ends; flat late and returned fees outside the computed due date/return; base increase conditions; borrower-requested limit changes), so the clause stays fully in force where the base applies; justified in rework_r4_claims.md.
- render_r1 relief edge: the relief basis tier now keys on a personal-loan fee-waiver entry existing (XCOUNT >= 1), as its rule says, so a 0.00 waiver entry gives "fee less 0.00" (probed).
- render_r1 review edge: the review is never above the credit limit before the review, in the baseline and assembly sentences and the compute (MN with the current limit); over-limit balance probed.
- Same class (rule vs compute on reachable edges): the increase compute now enforces the stated "never below the current credit limit" (MX with the current limit; probed with a request below the current limit).
- Scored values: unchanged in both tasks (all expected, baselines and 44 sensitivity figures identical). task_tools.py byte-identical; line.extended.yaml changed (policy edits above).
- XF 14 points re-applied to the touched policies (C, LDEC, LI, RELIEF): 1 independence clean (script); 2 assembly sentences kept, C's states the add-then-take-off order; 3 floor now in the factors that move the term; 4 overwrites unchanged; 5 compute_basis verbatim (0 issues); 6 rounding unchanged; 7 docstrings unchanged; 8 new probes below; 9 methods unchanged; 10 clean; 11 none; 12 realism unchanged; 13 runtime unchanged; 14 dossiers regenerated from the replay, revision logs extended.

### Probe table round 4 (all rounds, scratch copies)
| policy | probe | result | vs rule |
|---|---|---|---|
| returned_payment_fee | tie: second return same date recorded later | 19.24 | PASS |
| returned_payment_fee | absent: no loan return on the date (loan rows removed) | 21.8 | PASS |
| returned_payment_fee | decoy: other customer loan return same date | 16.35 | PASS |
| returned_payment_fee | edge: minimum payment due 0.00 caps fee at 0 | 0.0 | PASS |
| returned_payment_fee | month-end: return 2026-08-31 -> 1 month on 10-16 | 21.8 | PASS |
| backbilled_draw_fee | tie: second draw same date recorded later | 18.27 | PASS |
| backbilled_draw_fee | edge: 0-percent tier gives no back-billed fee | 0 | PASS |
| backbilled_draw_fee | decoy: draw on another line not counted | 18.27 | PASS |
| returned_fee_relief | absent: no replacement payment -> no relief | 0 | PASS |
| returned_fee_relief | absent: fee not booked -> no relief | 0 | PASS |
| returned_fee_relief | decoy: payment recorded against an older return ignored | 6.12 | PASS |
| returned_fee_relief | second replacement same day: cover adds up, timing same | 8.16 | PASS |
| returned_fee_relief | loan fee waived in full -> basis fee less 15.00 | 0.55 | PASS |
| returned_fee_relief | absent: no loan fee that day -> basis is the line fee | 6.67 | PASS |
| limit_increase | decoy: older approved increase request not the cap | 8800.0 | PASS |
| limit_increase | absent: no pending request -> cap is current limit | 8000.0 | PASS |
| limit_increase | decoy: paid-off second loan ignored by exposure | 8800.0 | PASS |
| limit_increase | absent: no active loan -> exposure full | 8900.0 | PASS |
| backbilled_draw_fee | points never take the percent below 0.00 (tier percent 0.5) | 18.27 | PASS |
| backbilled_draw_fee | clean record -> 0.25 points off | 16.31 | PASS |
| backbilled_draw_fee | month-end: draw 2026-08-31 -> one whole month on 10-16 | 18.27 | PASS |
| limit_increase | draw intensity: draw-fee entries counted with draws | 8800.0 | PASS |
| limit_increase | decoy: draw on another line not in draw charges | 8800.0 | PASS |
| limit_increase | window: draw dated exactly 3 months back (2026-07-16) excluded | 8600.0 | PASS |
| returned_fee_relief | rounding: exact half cent goes to the even cent | 6.12 | PASS |
| late_fee | tie: second payment same date as the latest, recorded later | 5.42 | PASS |
| late_fee | balance tier: ledger below 500.00 -> small share | 4.06 | PASS |
| late_fee | balance tier boundary: ledger exactly 3,000.00 -> full share | 6.77 | PASS |
| late_fee | decoy: entries of another line not in the ledger total | 5.42 | PASS |
| late_fee | absent: no payment after the due date -> grace share full | 6.02 | PASS |
| late_fee | edge: nothing past due -> fee held to 0.00 | 0.0 | PASS |
| late_fee | grace boundary: payment on day 10 counts, day 11 does not | 6.02 | PASS |
| workout_fee_relief | tie: equal largest late fees -> 25.00, repeat tier | 10.12 | PASS |
| workout_fee_relief | one late fee in 12 months, past due below the fee -> the amount past due | 10.12 | PASS |
| workout_fee_relief | repeat tier never below 0.00 (fee 4.00) | 0.0 | PASS |
| workout_fee_relief | rounding: 20.00 x 0.75 x 0.75 x 0.90 = 10.125 -> even cent 10.12 | 10.12 | PASS |
| workout_fee_relief | decoy: lender-error waiver not a courtesy waiver | 10.12 | PASS |
| workout_fee_relief | absent: no late fee at all -> relief 0.00 | 0.0 | PASS |
| limit_review | decoy: paid-off loan ignored by the loan cut | 3300.0 | PASS |
| limit_review | edge: balance floor exact multiple stays | 3400.0 | PASS |
| limit_review | edge: not past due -> no lateness cut | 3500.0 | PASS |
| close_to_draws_payment | absent: no loan -> no affordability months | 177.97 | PASS |
| close_to_draws_payment | decoy: loan additional-principal payment not an installment | 150.45 | PASS |
| close_to_draws_payment | edge: no amount past due -> no workout months, nothing added | 177.97 | PASS |
| close_to_draws_payment | late-history cut: one late fee -> 3 months | 140.82 | PASS |
| close_to_draws_payment | edge: term floor 12 months holds | 4.88 | PASS |
| close_to_draws_payment | term floor via trim: young small line, heavy draws, two late fees -> 12 | 270.83 | PASS |
| close_to_draws_payment | floor per reduction equals floor on the total (sequential vs final) | 150.45 | PASS |
| limit_review | over-limit balance: floor capped at the limit before the review | 4000.0 | PASS |
| returned_fee_relief | loan fee waiver entry of 0.00 still selects tier 1 (fee less 0.00) | 6.67 | PASS |
| limit_increase | requested limit below the current limit -> approved stays at the current limit | 8000.0 | PASS |
### Round 4 final difficulty run (no --task)
- EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK (cross-fire); check_traceability: 0 misses. Claims: rework_r4_claims.md. Scratch /tmp/flexline_credit_line_0067/ removed.
REWORK round 4: gates 7/7 green

## REWORK round 5 (seed only; KB revision_3 cross-product re-judge: src-4a..4c, src-5a..5d, own-product historical fees)
- line.extended.yaml and task_tools.py byte-identical (sha256 prefixes 45031e0626d8f261 / 0b2cd9bdfe20e668 verified after the rebuild).
- Task 0 personal loan (Grade C, AZ, schedule A), re-priced from docs/loan: installment = level payment at the base rate 16.24 over 48 months (pricing_and_disbursement_terms); the loan was never on AutoPay (autopay_enrolled false, no AutoPay account, every payment online), so no AutoPay debit or enrollment record is expected and interest accrues at the base rate; the 2026-09-21 late fee = schedule A figure on the unpaid installment × first-late share (no late fee in 12 months, fewer than 12 net installments) × loan-tenure share (24 to 47 months), no AutoPay share, no pay-cycle form (latest FlexLine late fee more than 45 days from the installment's due date); the fee payment row follows it and now points at the fee; APR recomputed from net proceeds.
- Task 1 personal loan (Grade B, IL, schedule A): origination fee at the Grade B percent, net proceeds and both disbursement lines follow; installment at the base rate 11.99; never on AutoPay (so the account change needs no records); the 2026-09-16 returned-payment fee = schedule A amount × first-return share (no other return, fewer than 12 net installments), no AutoPay share, bank-event form case 3 (no FlexLine returned-payment fee then); the partial payment and fee-paid rows follow; APR recomputed.
- Own-product history: the line's historical late fees (task 0 twice, task 1 once) were re-dated to the day after the late minimum payment, so each falls under the late-fee paragraph's flat clause for a minimum paid in full only after the grace period; task 0's two historical returned-payment fees were re-priced with the returned-fee paragraph as on their booking dates (each the most recent return then: R01 below 1,000.00 → the smaller of 2.5 percent and the flat fee, times the return-history share then and the tenure share then), and the courtesy waiver follows the first in full. Both worlds were re-simulated end to end (interest, minimums, balances), not patched.
- Scored values: task 1 unchanged; task 0 late fee and repayment payment moved by cents (gold recomputed with the real tools through the builders; relief and reviewed limit unchanged); every factor and every edge still moves a scored value; every prerequisite still unmet at the opening (solvability OK); task 1 knife-edges (usage just under 80 percent after the relief, draw charges just over 65 percent with the draw fee) re-verified.
- Probe table re-run (52 PASS) with refreshed world figures and a new half-cent case (25 percent of the unpaid part landing on an exact half cent).
- Proof text swept for stale figures and dates (old installment, fee, past-due and late-fee dates); seed_consistency checks rewritten for the historical late and returned fees.

### Round 5 final difficulty run (no --task)
- EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK (cross-fire) · TRACEABILITY OK. Claims: rework_r5_claims.md. Scratch /tmp/flexline_credit_line_0067/ removed.
REWORK round 5: gates 7/7 green
