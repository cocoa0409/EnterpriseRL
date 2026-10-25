# credit_builder_accounts — worklog

## Step 0 (difficulty pre-check)
- Read: skill references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/builder.yaml, db_schema.json, share_tools.py, audits/render_source/XF_recipe.md; other products only for cross-category seed realism (loan, hardship, line charters).
- Draws (`draw_counts.py --tasks 2`): task 0 `prerequisite_problems=3, factor_counts=[4,4,6,5]`; task 1 `prerequisite_problems=3, factor_counts=[5,6,6,5]`.
- Budget: 8 problems need 8 scorable numeric writes. Claimed event families with a number: late fee, returned-payment fee, closing-month dividend, early closure + savings applied (task 0); catch-up payment, payment interest split, fee payment line, goodwill fee credit (task 1). Release of savings is not a problem: the settlement rule pins it to a business day after the closing date.
- Risk noted: builder_savings_interest_credited is a builder event not listed in the difficulty's claimed event_types (a system monthly event). The closing-month dividend is booked as part of early-closure processing (accrued dividends paid at closure), declared by overwrite of the monthly-dividend sentence for the closing month only.

## Task 0 — early closure (Credit Builder 2400 Plan)
- Tree: root builder_ext_early_closure_settlement (user tool confirm_early_closure_8372931d) <- late fee (value_input), returned-payment fee (value_input), closing-month dividend (state_gate). Full dossier in tasks/0.json design_rationale.
- Values (scratch evaluator replaying gold with real tools): late 0.87, returned 1.74, dividend 1.60, savings applied 1177.96; baselines 5.86 / 10.00 / 0.00 / 1199.35; per-factor baselines all differ from expected.
- Edge skips: late -> 1177.09; returned -> 1176.22; dividend -> value 1177.96 unchanged, terminal savings 1225.04 vs 1226.64 and missing dividend line.
- Revision 1: replay closure missed 2 rows (bank account, hardship document) -> added find_bank_accounts read (release destination verification), dropped the unused hardship document row; steps shifted to 12/14/16/18; rationale/necessity/trace text swept.
- Revision 2: XF8 negative-lag probe found that a debit-card prepayment toward a future due date could make interest days negative -> rule now says "the interest days are never counted below zero", compute uses MX(0, cc_lead + cc_tail); basis quote updated; task-0 values unchanged.

### XF recipe — task 0 policies (14 points)
1. Factor independence (factor-read table; no factor binding reads another factor's binding — scratch sweep printed no XF1 hits):
   - late: lf_base<-{lf_dc_credit(SUM debit-card toward next due), lf_final_gap(DAYS next_due,maturity)}; lf_pct<-{lf_prior_late COUNT late fees 12m, lf_months_open MONTHS}; lf_hardship<-{EXISTS hardship active disaster, EXISTS active}; lf_return_share<-{lf_returns COUNT returns 3m}. result multiplies the four.
   - returned: rf_base<-{rf_amount LATEST return amount}; rf_history<-{rf_other_returns COUNT 12m -1}; rf_other_line<-{XCOUNT line returns 1m, 3m}; rf_reason<-{rf_code LATEST return code}; rf_seasoning<-{rf_months MONTHS, rf_credited COUNT posted - returned}.
   - dividend: dv_rate<-{EXISTS loan active, XCOUNT loan late fees 12m}; dv_autopay<-{COUNT autopay 12m - returns 12m}; dv_tenure<-{MONTHS}; dv_fraction<-{COUNT dividends, LATEST dividend date}.
   - settlement: cc_lead<-{COUNT debit card toward next due}; cc_tail<-{LATEST pending request date}; cc_rate<-{MONTHS, COUNT posted - returned}; cc_hardship<-{EXISTS x3}; cc_autopay<-{COUNT returns 3m}; cc_tenure<-{COUNT dividends}; plain cc_fees (SUM fee lines - waivers - fee payments), cc_interest, result.
2. Assembly stated once, generically: each rule has one assembly sentence ("Every adjustment below that applies acts on the unrounded fee, the adjustments are multiplied together in any order ..."; dividend: "Any rate addition below is added to the rate before the rate is applied, the fraction below replaces the closing-month fraction ..."; settlement: "a rate below replaces the APR, the day counts below replace their part of the interest days, the interest days are never counted below zero, the shares below multiply ..."). All adjustments commute (products / sums) and the one cap (late-fee maximum) and the savings cap are placed explicitly after rounding.
3. Factor-only quantities live in their factor sentences (debit-card credit, final installment, first-late percents, shares, bonuses, fractions, rate cuts, interest-stop days); baseline paragraphs name only the standard method (plan percent of monthly payment; flat returned fee; plan APY with no closing-month fraction; 30 + actual days at APR). No rule refers to another policy's figure.
4. Overwrite hygiene: each replaced_by restates the in-force remainder and names its own scope (late fee: once per due date, active status; returned fee: fee-bearing codes, never R07/R10/R29/chargeback; dividend: closing month only, every other month as base; settlement: early closing only, delinquency closing still base order; confirmation date sentence: closes on confirmation date). Every overwrite retires a clause that really conflicts on the task-0 world (5.86 vs 0.87; 10.00 vs 1.74; 0.00 vs 1.60; base closing interest 24.11 vs 2.72). No sibling overwrites retire the same clause.
5. compute_basis verbatim sweep: scratch sweep.py checked every basis sentence (split on '.'/';') is a whitespace-insensitive substring of its rule — 0 misses for all four policies.
6. Rounding: every rule says rounded to the nearest cent once, after all adjustments; compute has exactly one RND per fee/dividend/interest (plus RND of the settlement sum, stated "the total rounded to the cent"); the final-installment interest RND is stated ("that interest rounded to the cent").
7. Docstrings: describe only effects the bodies have (create one line, update one balance / status), no example values, no ordering words, no other tool names.
8. Edge probes (probe_t0.py on scratch copies; result column = recomputed value):
   | probe | policy | result | reading |
   | withdrawn request dated 2026-10-15 | settlement | 1177.96 | status filter excludes it |
   | no pending request | settlement | 1178.12 | falls to closing-date tier |
   | hardship plan completed | late / settlement | 1.74 / 1180.68 | only active plans count |
   | no hardship plan | late | 1.74 | fall-through |
   | loan late fee dated exactly 12 months ago (2025-10-16) | dividend | 2.60 | outside window -> clean tier |
   | no personal loan | dividend | 0.80 | plan APY |
   | FlexLine return 3 whole months ago | returned | 3.47 | outside 3-month window |
   | no FlexLine | returned | 3.47 | fall-through |
   | debit card payment toward another due date | late / settlement | 1.32 / 1182.76 | filter on installment_due_date |
   | second return same day booked later | returned | 2.31 | first-booked tie rule stated in the rule |
   Zero division: none (divisors are constants or the monthly payment). Negative lag: guarded by MX(0, ...) and stated. Month-end: windows use whole calendar months with the same-day-excluded convention stated in each rule. Entries vs periods: dividend counts are lines (one per month by grain); payments credited = posted lines - returned lines, stated as such.
9. Method tiers (pairwise, with a distinguishing input):
   - lf_base: monthly - debit-card credits | balance + one month's interest | monthly payment. Distinguishing input: debit-card credit 40 -> 77.16 vs 117.16; maturity due date -> balance + interest (1168.63 + 15.28 = 1183.91 on this account) vs 117.16.
   - rf_base: 10% of returned amount capped at fee | the returned amount | flat fee. Input 77.16 -> 7.716; input 6.00 -> 6.00 (vs 0.60 under the first shape); input 117.16 -> 10.00.
   - dv_fraction: 1/12 | days since last dividend / 365 | 0. On 2026-10-16 with last dividend 2026-09-30: 0.0833 vs 0.0438 vs 0.
   - cc_lead: 0 | 30 x whole payments past due | 30. Two payments past due -> 60 vs 30 vs 0.
   - cc_tail: request date | request date + 3 | closing date. Request 2026-10-12, closing 2026-10-16: 14 / 17 / 18 days from the due date.
10. Factor ids (lf_*, rf_*, dv_*, cc_*) are not substrings of any tool name (sweep printed none).
11. No cross-record date pairing is used.
12. Realism: hardship relief on fees and interest for borrowers in an active Larkspur hardship program; same-bank-event relief when a FlexLine debit bounced the same month; relationship APY for borrowers with an active personal loan; first-late percent for seasoned accounts; R09 (uncollected funds) treated more leniently than R01. Seeded cross rows are states their charters produce: Grade C OH loan with a schedule-A late fee (5 percent of the 303.42 installment = 15.17, above the 15.00 minimum) paid with its fee-payment line; Reduced Payment Plan active for 3 months (reason reduced_income); FlexLine Starter frozen for returned_payment with its 15.00 returned-payment fee (not more than the 35.00 minimum due). No fee on interest never billed, no post-closing fee (all fees booked while active), no fee on a fee.
13. Runtime: frozen_time "2026-10-16 10:05:00 EDT"; task_tools.py imports only erlbench; every write tool calls ctx.create/update in its own body; no date maths in tools.
14. Proof text swept after revisions 1 and 2 (step numbers in rationale, necessity, traces; MX guard in the settlement trace).

## Task 1 — goodwill credit after a catch-up (Credit Builder 3000 Plan)
- Draw: `prerequisite_problems=3, factor_counts=[5,6,6,5]` -> split 5, relief 6, credit 6, AutoPay re-enrollment 5.
- Design revision (before writing): a borrower-made catch-up payment could not carry five load-bearing factors without invented items, so the catch-up is seeded (made in the app this morning, split pending) and the borrower's own write is AutoPay re-enrollment (authorizing a recurring debit), whose due day is reset by rule. Root builder_ext_goodwill_late_fee_credit <- payment split (state_gate), returned-fee relief (value_input), AutoPay re-enrollment (value_input, owner=user). Full dossier in tasks/1.json.
- Values: split 4.83, relief 2.85, due day 8 (next due 2026-11-08), credit 1.08; baselines 24.72 / 1.20 / 26 / 0.28. Edge skips: 1.08 (terminal split missing) / 1.41 / 1.02.
- Historical-charter consistency: seeded fees recomputed with the task-0 rules on their dates (late fee 1.41 on 2026-10-12, returned fee 4.00 on 2026-09-29). The split rule is scoped to one-time payments of at least the monthly payment posted after grace, so no seeded payment of either task falls under it (task-0 partial payments 40.00 / 77.16 are below the monthly payment; on-time AutoPay keeps base monthly interest).
- Revision 1: check_solvability — late-fee row lacked related_txn_id (gate evidence field) -> seeded as empty. check_compute — gw_loan reads the loan ledger but no matching row existed -> seeded a 2025-07-06 schedule-A loan late fee (15.00, outside the 12-month window: near-miss) with its payment and fee-payment line; values unchanged; rationale swept.

### XF recipe — task 1 policies (14 points)
1. Factor-read table (no factor binding reads another factor's binding; scratch sweep: no XF1 hits):
   - split: al_days<-{LATEST payment due date, LATEST payment date}; al_rate<-{CFIELD hardship TRR rate, EXISTS active plan}; al_free<-{MONTHS open, COUNT late fees-1}; al_loan<-{EXISTS loan active+AutoPay, EXISTS loan active}; al_ap_hist<-{COUNT AutoPay 12m}. result multiplies/subtracts.
   - relief: rr_timing<-{LATEST return amount, LATEST return date, LATEST payment date}; rr_first<-{COUNT returns-1}; rr_season<-{MONTHS, COUNT posted-returned}; rr_line<-{XCOUNT FlexLine payments 6m}; rr_reason<-{LATEST return code}; rr_age<-{LATEST fee date}; plain rr_fee.
   - AutoPay: ad_anchor<-{CFIELD FlexLine due day, CFIELD loan due day}; ad_return_buf<-{COUNT returns of the monthly amount 12m}; ad_reason_buf<-{LATEST code}; ad_history<-{COUNT AutoPay 12m}; ad_line_buf<-{XCOUNT FlexLine returns 12m, CFIELD FlexLine past due}.
   - credit: gw_base<-{LATEST fee due date, COUNT AutoPay toward it, COUNT returns 1m} (+ plain gw_fee, fees_balance); gw_tenure<-{MONTHS}; gw_loan<-{EXISTS loan, XCOUNT loan late fees}; gw_history<-{COUNT late fees-1}; gw_autopay<-{COUNT returns 3m}; gw_speed<-{LATEST fee date}.
2. Assembly once, generic, order fixed: split ("a rate replaces the APR, a day count replaces the interest days, interest-free days are taken off (never below zero), shares multiply, round once"); relief/credit ("additions are added to the base share, total share capped at 100 percent, applied to the fee/base, timing applied, round once", credit "never more than the late fee"); AutoPay ("anchor plus every buffer, never later than 28 nor earlier than 1").
3. Factor-only quantities sit in their factor sentences; baselines name only plan APR with one-twelfth-year interest, base relief share of the fee, base goodwill share of the late fee, current due day.
4. Overwrites: split retires the base allocation sentence for late one-time catch-up payments only and restates the in-force remainder for every other payment; relief and credit both retire the courtesy-on-request sentence, each naming the other's case ("a goodwill credit on a late fee follows its own rule" / "a returned-payment fee relief follows its own rule") and restating the count limit; AutoPay re-enrollment declares none (base never says who picks the day; once-per-account and 1-28 are kept).
5. compute_basis verbatim sweep: 0 misses (sweep.py, all 8 policies).
6. Rounding: one RND per result; stated "rounded to the nearest cent once"; due day is an integer by construction.
7. Docstrings describe only body effects; no examples, ordering words or other tool names (TASK TOOL CONTRACT OK).
8. Probes (probe_t1.py): TRR plan completed / absent -> split 14.98; loan late fee moved inside 12 months -> credit 1.00; no FlexLine -> relief 2.55, due day 23; FlexLine frozen -> still anchors 8; FlexLine closed -> loan anchor 25; no loan -> credit 0.95; FlexLine return exactly 12 months ago -> excluded, due day 6. Ties: LATEST first-booked rule stated in split, relief and credit rules. Absent records: al_trr None -> next tier; rr/gw COUNT-1 floors handled by tier tests; DIV/LATEST of dividends only evaluated when present. Negative lag: MX(0, ...) on interest days; due day clamped 1..28.
9. Method tiers (pairwise, distinguishing input): al_days 30+L | 30 | 365/12 (L=40 -> 70 vs 30 vs 30.42); rr_timing 1-d/60 | 0.5 | 1 (d=15 -> 0.75 vs 0.5 vs 1); ad_anchor FlexLine day | loan day | own day (3 / 20 / 26); gw_base unpaid fees | late fee + month's returned fees | late fee (2.56 / 5.41 / 1.41 on this world before relief: 5.41 / 5.41 / 1.41 — the first two coincide only when no fee was paid or relieved; after the relief 2.56 vs 5.41).
10. Factor ids (al_*, rr_*, ad_*, gw_*) are not substrings of any tool name.
11. No cross-record date pairing.
12. Realism: hardship rate relief extended to catch-up interest (Temporary Rate Reduction Plan rate 4.99), interest-free days for seasoned accounts, returned-fee relief that shrinks with the days taken to make the payment good, goodwill credit sized by tenure/loan standing/history/AutoPay/promptness and gated on AutoPay re-enrollment, AutoPay day realigned after funds-related returns. Cross rows: CO Grade B loan on a TRR plan (plan payment 206.60 = level payment of 2804.11 at 4.99% over 14 months, current rate 4.99), schedule-A minimum late fee 15.00; FlexLine Standard with an R01 return, its 15.00 fee and a make-up debit-card payment, active again after the 10-day freeze.
13. Runtime: frozen_time "2026-10-14 10:30:00 MDT"; tools import only erlbench; every write tool writes in its own body.
14. Proof text swept after revision 1 (near-miss sentence, seed paragraph, probe paragraph).

## Final gate run (difficulty-wide, no --task)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite branches mean 58.00, steps 18.50, history_rows_max 88, branches_max 65); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
- check_traceability: misses only the 8 unlock tool names (docs not yet published) — expected.

REWORK round 1: gates 7/7 green

## Round 2 rework (audit revision_1)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full. Plan recorded in plan.md ("Round 2 rework plan").
- Charter rebuilt: removed the closing-month dividend and payment-interest-split policies and their tools; added builder_ext_closing_late_fee_relief (relieve_late_fee_at_closing_c21c573e) and builder_ext_closing_returned_fee_relief (relieve_returned_fee_at_closing_90cd40e1); early-closure settlement redesigned (4 factors: interest-paid-through anchor, rate-setting hardship rate, payment-relief hardship share, clearing-ACH add-back); AutoPay re-enrollment redesigned (5 factors: return buffer as a proportional/flat/none method, return-reason, FlexLine, personal-loan and PracticePay buffers); goodwill credit's AutoPay requirement scoped to borrowers whose AutoPay debit was returned; returned-payment-fee charge moved to task 1; all window/credited conventions moved into their own factor sentences; tie rules and chargeback/status filters added. Scratch sweep: 0 basis misses, no XF1 or XF10 hits; TASK TOOL CONTRACT OK.
- Task 0 rebuilt (Credit Builder 2400 Plan, frozen 2026-10-16): tree settlement <- {late fee, early-closure late-fee relief, early-closure returned-fee relief}, late-fee relief <- late fee; all four edges value_input and each moves a scored value (skips: settlement 1174.70 / 1175.95 / 1176.27; relief has no fee without the late fee). Values: late 0.87, late-fee relief 0.38, returned-fee relief 0.70, savings applied 1175.57. Seeded fees recomputed with the charter's own rules on their dates (4.00 on 2026-09-30, 1.74 on 2026-10-07). Hardship rows: Reduced Payment Plan payment 151.71 = 50% of 303.42; Temporary Rate Reduction Plan payment 140.42 = level payment of 2300.03 at 4.99% over 17 months (both exactly the hardship charter's formulas).
- Task 1 rebuilt (Credit Builder 3000 Plan, frozen 2026-10-09): tree goodwill <- {returned-payment fee (vi), made-good relief (vi), AutoPay re-enrollment (state_gate on the goodwill rule's own AutoPay requirement)}, relief <- fee (vi); 3 genuine value_input edges. Values: fee 2.02, relief 0.81, due day 27 (next due 2026-10-27), credit 1.10. Seeded late fee 1.41 = the late-fee rule on 2026-10-01. TRR plan payment 200.46 = level payment of 2720.78 at 4.99% over 14 months.
- Revision: check_compute flagged the relief's history as not load-bearing when zeroed (first-return addition coincidentally equal to the lost additions) -> first-return addition lowered; the task-1 relief is unchanged (it takes the second-return tier).

### Probe table (scratch copies, probe.py; value = recomputed result)
| probe | policy | value | rule reading |
| --- | --- | --- | --- |
| TRR plan completed | settlement | 1178.60 | only active plans set the rate -> APR tier |
| SCRA benefit active alongside TRR | settlement | 1175.86 | SCRA tier checked first: lower of APR and 6.0 |
| no hardship plans | settlement | 1183.05 | APR, no hardship share |
| debit card payment charged back (CB) | settlement | 1177.93 | not "credited and not charged back" -> 30-day lead |
| latest online ACH later returned | settlement | 1155.57 | not later than the most recent return -> nothing added back |
| ACH 11 days old | settlement | 1155.57 | outside the 10-day hold |
| no pending request | early-closure returned-fee relief | (not owed) | scope requires a pending request; compute guards dates |
| later R10 return without a fee | both returned-fee reliefs | (not owed) | the most recent return carries no fee -> relief not owed |
| second loan past due, first current | early-closure late-fee relief | 0.38 | "a loan with no amount past due" exists |
| no loans | early-closure late-fee relief | 0.36 | no-loan tier |
| FlexLine return 3 whole months ago | early-closure returned-fee relief | 0.52 | outside both windows |
| closed FlexLine with amount past due, no returns | AutoPay re-enrollment | 25 | only an active or frozen FlexLine's past due counts |
| active FlexLine past due, no returns | AutoPay re-enrollment | 26 | past-due tier |
| second return same day booked later | AutoPay re-enrollment | 28 | first-booked tie rule keeps R09; the extra 104.72 return counts as an AutoPay return |
| two AutoPay returns | AutoPay re-enrollment | 28 | proportional buffer then the day-28 cap |
| current due day 25 | AutoPay re-enrollment | 28 | never later than day 28 |
| loan late fee moved inside 12 months | goodwill credit | 1.02 | loan-late tier |
| no personal loan | goodwill credit | 0.97 | no-loan tier |
| no FlexLine | made-good relief | 0.71 | fewer than 3 FlexLine payments |
Absent-record guards: every LATEST date read used in DAYS is guarded (fee, return, request, payment); a missing fee gives no relief/credit; CFIELD reads of hardship rates return None -> next tier. Zero division: only divisions by the monthly payment, 60, 100, 365. Month-end: every window states "whole calendar months, a line dated on the same day of the month that many months earlier falls outside", matching MONTHS(). Entries vs periods: counts are of ledger lines and say so ("payments posted less payments returned", "AutoPay debits returned = returned payments whose amount equals the monthly payment").

### XF recipe, round 2 (all eight policies)
1. Factor independence: scratch sweep printed no factor binding reading another factor's binding; shared selections (most recent fee, unpaid fees, clearing ACH, request date) are plain bindings or the factor's own evidence.
2. Assembly once per rule, generic, with order fixed (share additions capped at 100% then the method's multiplier; settlement: rate replaces APR, day count replaces the lead, share multiplies, add-back joins the total before rounding; due day: buffers added then the day-28 cap).
3. Factor-only conventions (12/6/3/1-month windows, payments credited, AutoPay-return definition) now live in the factor's own sentence; no baseline names a factor quantity.
4. Overwrites: the courtesy-on-request sentence is superseded by the four waiver policies, each naming the other three by kind and restating the count rule for every other waiver; the settlement keeps only the early-closing payment-order overwrite (the confirmation-date sentence is in force again and restated); the late-fee and returned-fee overwrites unchanged; AutoPay re-enrollment declares none and takes no rate discount (CG-1: no extended policy cuts Credit Builder interest for AutoPay).
5. compute_basis verbatim sweep: 0 misses for all eight policies.
6. Rounding: one RND per result; reliefs and credit capped at the fee after rounding as stated.
7. Docstrings describe only body effects; no example values, ordering words or other tool names.
8. Probes: table above.
9. Method tiers (distinguishing input): lf_base (77.16 / balance + interest / 117.16); rf_base (6.00 at 60.00 / 6.00 at 6.00 vs 0.60 / 10.00); cc_lead (0 / 30 x n for n >= 2, e.g. 60 / 30); hl_paid (paid share 0.51 / 0.5 / 1); hr_timing and rr_timing (1 - d/60 / 0.5 / 1, e.g. d = 15 -> 0.75); gw_base (unpaid fees / late fee + 3-month returned fees / late fee); ad_return_buf (2 x n, e.g. 4 for two / flat 3 / 0). No two tiers coincide on their reachable domain (cc_lead tier 2 now needs two whole payments past due).
10. Factor ids are not substrings of tool names.
11. No cross-record date pairing.
12. Realism: no tier prices leaving the schedule better than keeping it (no closing-interest cut except hardship, no dividend bonus, no late-payment interest discount); fee reliefs for hardship closures and made-good returns, goodwill sized by standing; due-day buffers only from funds-timing evidence. Seeded cross rows equal their charters' formulas (hardship plan payments, schedule-A fees, FlexLine/PracticePay returned fees 15.00).
13. Runtime: frozen_time 'YYYY-MM-DD HH:MM:SS TZ'; tools import only erlbench; every write tool writes in its own body.
14. Proof text: both task dossiers, closures, necessities and traces rewritten from the rebuilt worlds; every figure re-derived by the scratch evaluator.

### Final gate run (round 2)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite branches mean 68.00, steps 20.00, history_rows_max 47, branches_max 69); GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.

REWORK round 2: gates 7/7 green

## Round 3 rework (audit revision_2)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_2 sections). Plan in plan.md ("Round 3 rework plan" and its as-built note). Items: R2-1..R2-6 and the task-1 rounding tie.
- R2-1 (closure deadlock class), all waits in every policy: the settlement's two relief edges and the goodwill credit's made-good edge are now action form ("the ... relief owed on the account, if any, has been granted") with a fallback reason; every relief/credit rule states when it is not owed (no fee, the fee already waived or paid, courtesy count used where it applies, a pending early-closure request where another relief has priority, the relief at 0.00) and compute returns 0 in each case; fee waits are narrowed to the record the depended-on policy actually prices (the oldest unpaid due date's late fee; the most recent return's fee) and exempt a fee that comes to 0.00; the early-closure reliefs count toward the courtesy waivers but are granted whatever the count, and the three request-less reliefs are not held to the request window (declared overwrites, siblings named). Every write policy states its 0.00 outcome (late fee and returned fee not charged; reliefs/credit not booked; settlement still confirmed with nothing applied; due day unchanged at a 0-day buffer).
- R2-2: priority sentences — with a pending early-closure request the early-closure late-fee relief takes the late fee (no goodwill credit on it) and the early-closure returned-fee relief takes the returned fee (no made-good relief); the made-good relief and the goodwill credit compute 0 while a request is pending. One relief per fee.
- R2-3: the waits whose row is shared by two writes are action form naming the write; the remaining state-form waits (late-fee line, returned-fee line) each have one writer.
- R2-4: hold add-back removed; hl_paid tiers cover every past-due case (no payment toward the due date -> halved); hr_timing counts a request before the return as 0 days (never above 1) and hr_request gives no addition for it; the debit-card lead tier checks a chargeback of that payment itself (CB return pointing at it) instead of any CB on the account; late fee base never below zero; returned fee computes 0 for non-fee-bearing codes and for a return already charged; made-good test is "most recent payment toward that due date dated after the return date" (same-day payment does not count); goodwill compute enforces the courtesy count, the 60-day window and the AutoPay gate.
- R2-5: one plain binding per shared record selection: most recent return id/date, fee id/amount, request date, late fee id/due date/date; reason factors read COUNT(... builder_txn_id=<plain id>, return_code=...) in their own bindings; factor sweep shows no shared selection across factors and no factor reading another factor.
- R2-6: clearing-ACH add-back and its hold factor struck; replaced by cc_record (credited payments 12+ -> 0.9, 6-11 -> 0.95, else 1.0) — a payment-record reduction on closing interest that rewards payments kept; settlement back to 4 factors (1 method, 3 parameter, 2 cross hardship).
- Rounding: every money policy carries "Every rounding to the cent in this policy goes to the nearest cent, a half cent or more rounding up."; compute rounds with int(x * 100 + 0.500001) / 100 at exactly the stated points (decimal half-up, no binary artifact). Task 1's partial payment changed 60.00 -> 62.00 (fee 2.0925 -> 2.09); no gold value on either task lands on a half cent (raw 0.86805, 0.3787, 0.696, 1.27196 / 2.0925, 0.836, 1.1172).
- Task 0 recomputed: 0.87, 0.38, 0.70, settlement 1155.43 (all-baseline 1177.86; cc_lead 1157.55, cc_rate 1158.16, cc_hardship 1156.70, cc_record 1155.57). Edge skips 1154.94 (late fee; mechanical 1154.56) / 1155.81 / 1156.13.
- Task 1 recomputed: 2.09, 0.84 (new fee id from the step-14 receipt), 27, 1.12. Edge skips 0.59 (fee; mechanical 0.24) / 1.41 / 0.00 (AutoPay).
- check_solvability: the courtesy_window entries were dropped from the waiver steps' temporal_feasibility/base_preconditions (the window clause is now superseded for the request-less reliefs; the goodwill credit restates and enforces it in its own rule).
- Proof sweep: both design_rationale texts rewritten; prerequisite_closure edges re-copied from the charter (form, fallback_reason, condition, policy_source), why_false / flips / order / edge_load_bearing rewritten; every tracing, factor_trace, factor_sensitivity, baseline_result and business_effect re-derived; seed_consistency rows for the 62.00 payment and return updated. No stale "add back", "hold", "shows its ... relief", "every lapsed", RND or old figure remains.

### Probe table, round 3 (scratch copies; value = recomputed result)
| probe | policy | value | rule reading |
| --- | --- | --- | --- |
| debit card payments cover the payment | late fee | 0.00 | base never below zero; not charged |
| CB return of the debit card payment | late fee | 1.32 | credit netted; monthly-payment base |
| return on the same day 3 months earlier | late fee | 1.04 | outside the window; one-return share |
| that debit card payment charged back | settlement | 1157.55 | not "not charged back" -> 30-day lead |
| no fees on the account | settlement | 1149.90 | no wait open; settles |
| fewer than 6 credited payments | settlement | 1155.57 | record share falls through |
| no late fee | early-closure late-fee relief | 0 | not owed |
| late fee already waived | early-closure late-fee relief | 0 | not owed (once per fee) |
| past due, no payment toward the due date | early-closure late-fee relief | 0.40 | halved tier |
| newer R07 return without a fee | early-closure returned-fee relief | 0 | most recent return carries no fee |
| fee already paid | early-closure returned-fee relief | 0 | not owed |
| request before the return | early-closure returned-fee relief | 0.57 | no promptness add; timing not above 1 |
| most recent return R07 | returned-payment fee | 0 | not fee-bearing |
| fee already charged for the return | returned-payment fee | 0 | charged once |
| 0.01 return | returned-payment fee | 0.00 | not charged |
| pending early-closure request | made-good relief | 0 | priority to the early-closure relief |
| two courtesy waivers in 12 months | made-good relief | 0 | count used up |
| making-good payment on the return date | made-good relief | 0 | not made good |
| waiver on the same day 12 months earlier | made-good relief | 0.84 | outside the count window |
| pending early-closure request | goodwill credit | 0 | priority to the early-closure relief |
| AutoPay not re-enrolled | goodwill credit | 0 | AutoPay gate |
| request on day 61 / day 60 | goodwill credit | 0 / 0.98 | request window inclusive |
| late fee already waived | goodwill credit | 0 | once per fee |
Absent records: every id-keyed read is guarded (None id -> 0 or None, never a filter on None); DAYS only on guarded dates; no division except by the monthly payment.

### XF recipe, round 3 (all eight policies)
1. Factor independence: sweep shows no factor binding reading another factor's binding and no record selection shared across factors; shared selections are plain bindings.
2. Assembly once per rule with order fixed (shares capped at 100%, then the paid-part/timing method, then one half-up rounding, then the fee cap; settlement: rate replaces APR, day count replaces the lead, days never below zero, shares multiply, one rounding of interest, one of the total, savings cap).
3. Factor-only quantities (credited payments, AutoPay-debit definition, windows, request lag) live in their factor's sentence; the baseline names none.
4. Overwrites: courtesy-count clause retired by the four waiver policies, each naming the others; request-window clause retired by the three request-less reliefs, each naming the other two and restating the window for every other waiver; the goodwill credit keeps and enforces the window; settlement keeps its early-closing scope.
5. compute_basis verbatim sweep: 0 misses; every baseline sentence and replaced_by in its rule.
6. Rounding: half-up stated in every money rule; int(x * 100 + 0.500001) / 100 exactly where the rule rounds.
7. Docstrings unchanged: body effects only, no example values, ordering words or other tool names.
8. Probes: table above (decoys, absent records, ties, month-end, negative lag, 0.00 outcomes).
9. Method tiers unchanged in shape (lf_base, rf_base, cc_lead, hl_paid, hr_timing, rr_timing, gw_base, ad_return_buf); hl_paid now total over every past-due case.
10. No factor id (incl. cc_record) is a substring of a tool name.
11. No cross-record date pairing: the made-good test follows ids (return -> its payment -> that due date -> latest payment toward it).
12. Realism: no money taken twice (add-back struck); one relief per fee; fees never charged at 0.00; closing-interest reductions only for hardship and a kept payment record.
13. Runtime: tools unchanged; frozen_time format kept.
14. Proof text swept (see above).

### Final gate run (round 3)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 3: gates 7/7 green

## Round 4 rework (audit revision_3)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_3 sections). Plan in plan.md ("Round 4 rework plan").
- R3-1: cc_record struck. New settlement factor cc_cause (parameter, cross-difficulty hardship): an active Larkspur hardship plan granted for the death of a household earner, a natural disaster or a medical hardship -> severe-cause share; none of those but one granted for job loss, reduced income or divorce or separation -> income-cause share; otherwise no reduction. Its tiers are rule sentences of their own, the generic "each share below multiplies the interest" assembly sentence is kept, the hardship cross-category reads now declare hardship_reason. Settlement back to 4 factors (1 method, 3 parameter, all three parameters cross hardship). Task 0's plans are granted for reduced income, so the factor takes the 0.9 tier and every task-0 figure is unchanged (settlement 1155.43, cc_cause baseline 1155.57).
- R3-2: re-enrollment now declares an overwrite of the base due-day sentence ("the due day may be changed once per account ..."), scoped to an account whose AutoPay debit was returned and that turns AutoPay on again, restating the base sentence for every other account; a reset that moves the day keeps the first new due date in the same month; a 0-day buffer or the day-28 cap leaves the due day and the next due date unchanged; an account showing an amount past due keeps its due day and next due date (compute returns the current day). Other date-producing rules checked: the late fee takes the account's next due date as given and the settlement and reliefs produce no dates.
- R3-3: late-fee rule narrowed to the account's oldest unpaid due date (a later lapsed due date carries no fee of its own until it becomes the oldest; nothing when the late due date already carries its fee — compute lf_charged); returned-payment-fee rule narrowed to the account's most recent returned payment (a run of returns before the fee is charged costs one fee). Both narrowings sit in the replaced_by of each policy's declared overwrite of the base fee clause; the waits that depend on them already name exactly those records. Other "every ..." statements checked: the settlement's unpaid fees (every fee less every waiver and fee payment) and the re-enrollment buffers are computed for every item.
- Proof sweep: task 0 rationale, settlement trace, sensitivity tier, hand-over tracing and the hardship-plan read's necessity now name cc_cause; task 1 rationale (base-invariant card, due-date line), the next-due-date tracing and the re-enrollment base precondition cite the declared overwrite and the same-month move. No figure changed in either task.

### Probe table, round 4 (scratch copies)
| probe | policy | value | rule reading |
| --- | --- | --- | --- |
| active plan granted for medical hardship | settlement | 1155.29 | severe-cause tier |
| active plans granted for other causes | settlement | 1155.57 | cause share falls through |
| expired death-of-earner plan beside the active reduced-income plans | settlement | 1155.43 | only active plans count (decoy) |
| buffers add to 0 | AutoPay re-enrollment | 15 | due day and next due date unchanged |
| current due day 28 | AutoPay re-enrollment | 28 | cap leaves the day; no month skip |
| amount past due | AutoPay re-enrollment | 15 | unpaid installment not moved later |
| late due date already carries its fee | late fee | 0 | charged at most once |
| late fee only on an older due date | late fee | 1.45 | still owed for the oldest unpaid due date |
| older uncharged fee-bearing return before the most recent | returned-payment fee | 2.79 | one fee, on the most recent return (history tier moves) |

### XF recipe, round 4 (touched: settlement, AutoPay re-enrollment, late fee, returned-payment fee; others unchanged)
1. Sweep: no factor reads another factor; no record selection shared across factors. 2. Assembly sentences unchanged. 3. Cause tiers in their own sentences; baseline names none. 4. Re-enrollment overwrite self-scoped and restating the base for every other account; fee overwrites carry the narrowings; no undeclared departure. 5. compute_basis sweep 0 misses. 6. Rounding unchanged. 7. Docstrings unchanged. 8. Probes above. 9. Method tiers unchanged. 10. cc_cause is not in any tool name. 11. No cross-record pairing. 12. Realism: no closing discount outside hardship; no installment deferred by re-enrollment; no fee stacked on an installment late only because of an earlier one. 13. Tools unchanged. 14. Proof text swept.

### Final gate run (round 4)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 4: gates 7/7 green

## Round 5 rework (renderer source scan, audits/render_source/credit_builder_accounts/render_r1.md)
- Read render_r1.md in full (S1–S7). Every edit was made as a text transform applied at once to rule, compute_basis, baseline, overwrite and prerequisite texts (verbatim links kept) and to the quoting strings of both task files.
- S1 (branch stated as computed): late fee lf_base — the debit-card branch now applies whenever one or more debit card payments were credited toward the late due date (new plain count lf_dc_count, a binding of lf_base), and the net debit-card credit after chargebacks is never counted below zero (rule says so; compute floors it). Other branch conditions re-read against compute: hl_paid, cc_lead, hr/rr timing (AutoPay debit by amount), ad_line_buf, hl_loan, gw_loan, lf_hardship — all stated as computed.
- S2 ("no other" counts): rf_history now tests "<= 0" like hl_first, hr_first, rr_first and gw_history; no other "count less one" comparison remains with "== 0".
- S3 (window ends): every "N whole calendar months before today / the assessment date" and "less than N whole calendar months before today" window now says a row dated today (the assessment date for the late fee) counts and one dated on the same day of the month N months earlier falls outside, matching within_months (0 <= MONTHS < N); the three windows that had no boundary note (FlexLine quarter tiers of the closing returned-fee relief and the returned fee, the goodwill AutoPay gate) and the goodwill base's 3-month fee window now carry it in their own sentence.
- S4 (months open): every "open N months" factor sentence (lf_pct, hl_season, rf_seasoning, rr_season, gw_tenure) now states that months open are whole calendar months from the open date, each complete on the day of the month matching the opening day or, in a month too short for that day, on the first day of the following month — exactly MONTHS().
- S5 (one definition): "AutoPay debit" means a payment whose amount equals the monthly payment everywhere; gw_base's second tier now counts posted payments of that amount toward the late fee's due date (was the AutoPay channel), and the goodwill gate's definition is worded the same way; the 3-month window boundary sits in gw_base's own sentence.
- S6 (docstrings): confirm_early_closure accepts "an amount of 0.00 or more" (the rule's 0.00 confirmation); reenroll_autopay's due day and next due date say they are the current ones when the due day does not change. No other docstring contradicts a branch (fee and relief tools never book 0.00).
- S7 (day counts): the settlement's interest days are "the calendar days after the oldest unpaid due date up to and including the closing date (the closing date less that due date)"; cc_lead's second tier says it replaces the month before the oldest unpaid due date with 30 days per whole payment past due (amount past due over the monthly payment, rounded down), the oldest unpaid installment included; hr/rr timing count days after the return date up to and including the request / making-good payment date; fee-age tiers (hl_age, rr_age, gw_speed) state today less the fee's date.
- No scored value, factor figure or baseline figure moved in either task (re-evaluated on the scratch evaluator).

### Probe table, round 5 (scratch copies)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| debit card payment fully charged back on the maturity due date | late fee | 1.32 | debit-card branch, monthly-payment base (not the final installment) |
| chargebacks above the debit card credit | late fee | 1.32 | net credit floored at zero |
| most recent return 12+ whole months old | returned-payment fee | 1.40 | first-return share ("no other") |
| courtesy waiver dated today on a 1-waiver plan | made-good relief | 0 | today's waiver counts |
| open exactly 12 whole months today / one day short | goodwill credit | 1.12 / 0.98 | MONTHS() month-completion convention |
| no return in the month, full-payment amount toward the fee's due date | goodwill credit | 1.41 | AutoPay debit by amount; second base tier (capped at the fee) |

### XF recipe, round 5 (all eight policies touched by the text transform)
1. Sweep: no factor reads another factor; no record selection shared across factors (lf_dc_count joins lf_base's bindings). 2. Assembly sentences unchanged. 3. Window, month-open and day-count conventions sit in the factor sentence that uses them. 4. Overwrites unchanged in scope; their replaced_by texts carried through the same transform. 5. compute_basis verbatim sweep 0 misses. 6. Rounding unchanged. 7. Docstrings aligned (S6), no example values. 8. Probes above. 9. Method tiers unchanged. 10. No factor id in a tool name. 11. No cross-record pairing. 12. Realism unchanged. 13. Tools: docstring text only. 14. Proof text swept (task 1 quoting strings updated; task 0 had none affected).

### Final gate run (round 5)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 5: gates 7/7 green

## Round 6 rework (audit revision_5: R5-1, R5-2)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_5 sections).
- R5-1: "AutoPay debit" now means a payment made through the AutoPay channel (payment_channel autopay_ach), and its return is the return line that reverses it in full, points at it and carries that channel. The definition is stated in each sentence that uses the term: the closing returned-fee relief's and the made-good relief's AutoPay timing tiers (compute hr_ap / rr_ap: the most recent return's line carries the AutoPay channel; the other tiers now read "any other payment" below / at or above the monthly payment), the goodwill AutoPay gate (gw_ap_returned counts AutoPay-channel return lines in the window), the goodwill base's second tier (gw_autopay_toward counts AutoPay-channel payments toward the late fee's due date), the re-enrollment scope sentence and its AutoPay-return count (ad_ap_returns). No amount-based proxy remains.
- R5-2: a debit card payment is netted only of its own chargeback, in both policies: the late fee subtracts only CB return lines that reverse a debit card payment toward the late due date (the return line points at the payment and carries its channel and due date), and the settlement keeps reading the CB return pointing at that payment. An unrelated old chargeback no longer touches the late fee.
- Seeds: every builder return line in both tasks now carries the channel and due date of the payment it points at (a reversal in full); no other row changed. No scored value, factor figure or baseline figure moved (scratch evaluator: 0 differences on both tasks).
- Proof sweep: both dossiers, traces, sensitivity tiers and tracings now describe the returned payments as AutoPay-channel or online debits and the debit card credit as having no chargeback of its own; task 1's AutoPay edge policy_source/condition re-copied from the charter; seed_consistency rows of every return line state the carried channel and due date.

### Probe table, round 6 (scratch copies)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| old unrelated debit card payment charged back (task 0) | late fee | 0.87 | the 40.00 credit stands (own chargeback only) |
| same world | settlement | 1155.43 | lead still 0 — same reading as the late fee |
| chargeback of the 40.00 payment itself | late fee | 1.32 | credit lost, monthly-payment base |
| same world | settlement | 1157.55 | month before counted |
| never on AutoPay; own online payment of the monthly amount returned | goodwill credit | 1.06 | AutoPay gate does not apply |
| same world | AutoPay re-enrollment | 24 | no AutoPay-return buffer |
| task 1 world: Andre's own 10-09 online payment | goodwill base | not counted | only the AutoPay-channel 09-15 debit counts |
| most recent return carries the AutoPay channel (task 0) | closing returned-fee relief | 1.28 | AutoPay decay tier instead of halving |

### XF recipe, round 6 (touched: late fee, settlement, closing returned-fee relief, made-good relief, goodwill credit, AutoPay re-enrollment)
1. Sweep clean: no cross-factor reads; hr_ap / rr_ap are bindings of their timing factors keyed by the plain most-recent-return id. 2. Assembly sentences unchanged. 3. The AutoPay-debit and own-chargeback definitions sit in each sentence that uses them. 4. Overwrites unchanged in scope (the re-enrollment replaced_by text unchanged). 5. compute_basis verbatim. 6. Rounding unchanged. 7. Docstrings unaffected (no definition in them). 8. Probes above. 9. Method tiers keep their shapes (decay / half / full). 10. No factor id in a tool name. 11. Links followed by id (return -> payment), no cross-record date pairing. 12. Realism: AutoPay treatment keyed to AutoPay debits the ledger records; no unrelated chargeback netted. 13. Tools unchanged. 14. Proof text swept.

### Final gate run (round 6)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 6: gates 7/7 green

## Round 7 rework (audit revision_6: R6-1)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_6 sections).
- Seed reverted: the four return lines (task 0 b2a9795b, 41d9e490; task 1 8c21ba81, 6dac29a8) are again exactly what the base event builder_payment_returned writes (txn_date, amount, related_txn_id, return_code, interest and principal reversed); the added payment_channel / installment_due_date are gone from initial_state and db_closure; the seed_consistency notes claiming them are removed.
- R6-1, every member now reaches the reversed payment through the return line's link (related_txn_id), as the settlement's chargeback check and the made-good relief's payment lookup already did:
  - late fee: the debit-card credit is the most recent debit card payment credited toward the late due date, not counted when a CB return points at it (lf_dc_id / lf_dc_cb / lf_dc_credit) — the same reading as the settlement's cc_lead, so one payment and one term give one answer;
  - goodwill AutoPay gate: the most recent AutoPay debit (latest payment posted through the AutoPay channel) has a return line pointing at it dated in the 3-month window (gw_ap_id / gw_ap_returned); the policy_source and condition of task 1's AutoPay edge were rewritten to that sentence and re-copied into the task;
  - re-enrollment return buffer: the method now reads the most recent AutoPay debit and the return pointing at it — returned two or more days after it was debited -> those days plus one; returned the same or next day -> a flat 2 days; not returned in 12 months / no AutoPay debit -> none (proportional / flat / none shapes);
  - both returned-fee reliefs' AutoPay timing tier: the payment the most recent return points at was made through the AutoPay channel (hr_ret_pay / rr_ret_pay -> hr_ap / rr_ap).
- Sweep of every builder-ledger read against the fields its producing base event writes (posted: date, amount, channel, bank account, portions, due date; returned: date, amount, related payment, code, portions; late fee: date, amount, due date; returned fee: date, amount, return line; waiver: date, amount, fee, basis; fee paid: date, amount, fee): no other read of a field the event does not write.
- Task 1 on the reverted world: the AutoPay edge still holds through the link (86024252, AutoPay channel, returned by 8c21ba81 two days later) and ad_return_buf still takes a weight-bearing tier (3 days); no re-worlding needed. No scored value, factor figure or baseline figure moved on either task (scratch evaluator: 0 differences).
- Proof sweep: task 0 late-fee traces say "no chargeback pointing at that payment"; task 1 dossier, trace, sensitivity tier and due-day tracing describe the AutoPay debit and its return through the link; the AutoPay edge's why_false cites the link.

### Probe table, round 7 (scratch copies)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| auditor 1: CB line (base-event shape) pointing at the 40.00 debit card payment | late fee | 1.32 | credit lost, monthly-payment base |
| auditor 1: same world | settlement | 1157.55 | month before counted — same reading |
| auditor 2: reverted task-1 world, no re-enrollment | goodwill credit | 0 | AutoPay gate holds through the link |
| auditor 2: reverted task-1 world | AutoPay re-enrollment | 27 | buffer tier holds through the link |
| unrelated old chargeback | late fee / settlement | 0.87 / 1155.43 | untouched |
| earlier 30.00 debit card payment toward the same due date | late fee | 0.87 | only the most recent debit card payment is netted |
| never on AutoPay, own monthly-amount payment returned | goodwill credit / re-enrollment | 1.06 / 24 | not an AutoPay debit |
| AutoPay debit returned the next day / 5 days later | AutoPay re-enrollment | 26 / 28 | flat 2 / 5 + 1 (cap 28) |
| a later AutoPay debit cleared after the bounced one | goodwill credit | 1.06 | gate reads the most recent AutoPay debit |
| most recent return points at an AutoPay-channel payment | closing returned-fee relief | 1.28 | AutoPay decay tier |

### XF recipe, round 7 (touched: late fee, closing returned-fee relief, made-good relief, goodwill credit, AutoPay re-enrollment)
1. Sweep clean (lf_dc_id/lf_dc_cb join lf_base; ad_ap_* join ad_return_buf; hr_ret_pay plain; gw_ap_id plain for the gate). 2. Assembly sentences unchanged. 3. Each AutoPay-debit / own-chargeback reading sits in the sentence that uses it. 4. Overwrites unchanged. 5. compute_basis verbatim. 6. Rounding unchanged. 7. Docstrings unaffected. 8. Probes above, decoys included. 9. ad_return_buf tiers change shape (proportional / flat / none). 10. No factor id in a tool name. 11. Links followed by id only. 12. Realism: AutoPay treatment and chargebacks keyed to the payments the ledger records; seeded rows are what the base events write. 13. Tools unchanged. 14. Proof text swept.

### Final gate run (round 7)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 7: gates 7/7 green

## Round 8 rework (audit revision_7: R7-1, R7-2; coordinator decision on R7-1)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_7 sections).
- R7-1 (coordinator decision): the late fee's declared overwrite now scopes the policy's own figuring by name — "for a late due date with no more than one debit card payment credited toward it, and only for such a due date, its amount is figured as this policy sets out ...; every other late due date remains under the base clause: The late fee is late_fee_percent of the monthly payment, rounded to the cent and not more than late_fee_max_usd, at most max_late_fees_per_due_date per due date, and only on an account in active status." (base text restated verbatim). Inside the scope the one debit card payment is netted unless a chargeback points at it (the settlement's reading); compute takes the base clause (plan percent of the monthly payment, capped, half-up) when two or more card payments were credited toward the late due date (lf_dc_count, now a plain binding stated by the scope sentence and the card sentence). The final-installment interest rounding and the new-account months-open test now carry their own conventions in their factor sentences.
- R7-2: the re-enrollment return buffer (the policy's method factor) now reads when the borrower's funds actually arrived: the most recent AutoPay debit was returned in the 12 months and made good by the borrower's own payment (the latest payment toward that debit's due date, dated after the return) within the plan's late-fee grace days after the due date -> the buffer is those days plus one (the new due day falls the day after the funds arrived); returned but made good only after the grace period, or not yet made good -> a flat 3 days; not returned / no AutoPay debit -> none. Shapes proportional / flat / none; every tier reachable (probed). Task 1 takes the flat tier (made good 24 days after the due date, beyond the 15-day grace), so the due day stays 27.
- Renderer-class checks (sibling stops): every window / whole-month / day-count convention a factor needs sits in that factor's own sentences (back-references only within one factor); no factor's decided value reaches the result only through another factor; every non-factor binding is stated by a non-factor sentence — the closing returned-fee relief gained "The return looked at is that most recent returned payment: its return date is the date of its return line, the payment it reverses is the payment that line points at, and the request looked at is the account's pending early-closure request, dated the day it was registered." for its plain return-date, reversed-payment and request-date bindings.
- No scored value, factor figure or baseline figure moved on either task (scratch evaluator: 0 differences).
- Proof sweep: task 0 late-fee traces name the 40.00 as the only card payment toward 2026-09-28 (own figuring applies); task 1 dossier, trace, sensitivity tier and due-day tracing describe the make-good date and the flat tier.

### Probe table, round 8 (scratch copies)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| auditor: two debit card payments toward the late due date | late fee | 5.86 | base clause (5% of 117.16, under the cap) |
| one card payment, not charged back (gold world) | late fee | 0.87 | own figuring, base 77.16 |
| one card payment, charged back | late fee / settlement | 1.32 / 1157.55 | monthly-payment base / month before counted — one reading |
| no card payment, not the maturity date | late fee | 1.32 | monthly-payment base |
| gold world (made good 24 days after the due date) | re-enrollment return buffer | 3 | flat tier |
| made good 5 days after the due date | re-enrollment return buffer | 6 | 5 + 1 |
| returned, not yet made good | re-enrollment return buffer | 3 | flat tier |
| no AutoPay debit / returned 12+ months ago | re-enrollment return buffer | 0 | none |

### XF recipe, round 8 (touched: late fee, closing returned-fee relief, AutoPay re-enrollment)
1. Sweep clean; lf_dc_count plain; ad_* bindings all in ad_return_buf. 2. Assembly sentences unchanged. 3. Conventions in the factor sentences that use them; plain bindings stated by plain sentences. 4. Late-fee overwrite self-scoped with the base clause restated verbatim; re-enrollment overwrite unchanged. 5. compute_basis verbatim. 6. Half-up applies to the base-clause path too. 7. Docstrings unaffected. 8. Probes above. 9. ad_return_buf shapes proportional / flat / none. 10. No factor id in a tool name. 11. Links by id only. 12. Realism: due day from when the borrower's own make-good payment landed; no card payment ignored inside the scope. 13. Tools unchanged. 14. Proof text swept.

### Final gate run (round 8)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 8: gates 7/7 green

## Round 9 rework (audit revision_8: R8-1, R8-2)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_8 sections).
- R8-1, whole class (a payment that was itself returned never counts as credited or as making a debit good, checked through the return that points at it):
  - re-enrollment return buffer: the make-good payment is the latest payment toward the AutoPay debit's due date "which no return points at" (ad_good_id / ad_good_ret); a bounced make-good leaves the debit not made good (flat tier);
  - made-good relief: "made good" now also requires that the most recent payment toward that due date has not itself been returned (rr_good_id / rr_good_ret in rr_owed) — explicit even though a bounced make-good would also become the most recent return;
  - late fee and settlement: the one / most recent debit card payment is not counted when any return points at it (a chargeback, code CB, or any other return) — same reading in both;
  - not members: gw_autopay_toward and hl_toward test that a payment was posted (presented), not credited; hl_paid's part-paid tier also needs an amount past due below the monthly payment, which already nets every return.
- R8-2, whole class (a quantity only one factor uses belongs to that factor): hr_ret_pay is now a binding of hr_timing (defined by its AutoPay tier sentence; the plain "return looked at" sentence no longer names it), gw_fee_due a binding of gw_base (defined by its second-tier sentence). Mechanical check over all 8 policies: no plain binding is read by a single factor only, none is defined only by factor sentences, none lacks a basis, and no factor reaches the result only through another factor.
- No scored value, factor figure or baseline figure moved on either task (scratch evaluator: 0 differences). S1–S7 conventions untouched.
- Proof sweep: task 0 traces now say the 40.00 debit card payment was not returned (no return points at it); task 1 dossier notes the make-good payment has no return pointing at it; both dossier headers record the round-9 reading.

### Probe table, round 9 (scratch copies)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| auditor: make-good payment 09-25 returned R10 09-29 | re-enrollment return buffer | 3 | not made good -> flat tier |
| same make-good payment standing | re-enrollment return buffer | 11 | 10 days + 1 |
| gold world | re-enrollment | 27 | unchanged |
| making-good payment returned the same day (booked after) | made-good relief | 0 | not made good -> not owed |
| gold world | made-good relief | 0.84 | unchanged |
| debit card payment returned R01 (not CB) | late fee / settlement | 1.32 / 1157.55 | not counted / month before counted — one reading |

### XF recipe, round 9 (touched: late fee, settlement, closing returned-fee relief, made-good relief, goodwill credit, AutoPay re-enrollment)
1. Sweep clean; single-factor quantities moved into their factors; plain bindings shared or read by plain bindings. 2. Assembly sentences unchanged. 3. Conventions unchanged in their factor sentences. 4. Overwrites unchanged (late-fee scope sentence kept verbatim). 5. compute_basis verbatim. 6. Rounding unchanged. 7. Docstrings unaffected. 8. Decoy probes above (bounced make-good, returned card payment). 9. Method shapes unchanged. 10. No factor id in a tool name. 11. Links by id only. 12. Realism: a returned payment never counts as funds received. 13. Tools unchanged. 14. Proof text swept.

### Final gate run (round 9)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 9: gates 7/7 green

## Round 10 rework (audit revision_9: R9-1)
- Read audits/policy_task/credit_builder_accounts/{_difficulty,0,1}.md in full (revision_9 sections).
- R9-1: the re-enrollment tier-1 parenthetical now says exactly what the compute does — "the payment looked at is the latest payment posted toward that due date: it makes the debit good only when no return points at it, it is dated after the return and it is dated no more than the plan's late-fee grace days after the due date ...; when a return points at that latest payment, the debit has not been made good" (selection first, then the test; no restrictive relative clause).
- Same-shape sweep over every rule sentence with a relative clause near a selection (which / that / whose): two more sentences could be read as restricting the selection and were reworded the same way —
  - returned-payment fee scope (also its overwrite's replaced_by): "only for the account's most recent returned payment and only when that payment's return code is one of the plan's fee-bearing return codes" (was "the most recent returned payment whose return code is ...", readable as the most recent fee-bearing return);
  - late fee card tier: "less that payment, never on less than zero, instead of on the monthly payment; when a return points at that payment ..., the payment is not netted and the fee is figured on the monthly payment" (was "that payment, which is not counted when ...").
  The rest test rather than select (the made-good relief's "is dated after the return date and has not itself been returned", the goodwill gate's and re-enrollment's "most recent AutoPay debit (the latest payment made through the AutoPay channel) was returned", the reliefs' "the payment its return line points at").
- Every edited sentence was replaced in the rule, compute_basis and replaced_by at once (verbatim sweep 0 misses); no compute changed; no scored value moved (0 differences on both tasks); no task text quoted the edited sentences.

### Probe table, round 10 (scratch copy)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| auditor: 104.72 on 09-25 (cleared) and 20.00 on 10-05 toward 09-15 returned 10-08 | re-enrollment return buffer | 3 | the latest payment toward the due date is returned -> not made good -> flat tier (rule and compute agree) |
| same world without the bounced 20.00 | re-enrollment return buffer | 11 | latest payment 09-25, unreturned, 10 days + 1 |
| gold worlds | all eight computations | unchanged | |

### XF recipe, round 10
Text-only edits in the late fee, returned-payment fee and re-enrollment: points 1–3 unchanged; 4 the returned-fee overwrite's replaced_by carries the reworded scope; 5 verbatim sweep clean; 8 probe above; 14 proof text checked (no task string quoted the edited sentences). Other points unaffected.

### Final gate run (round 10)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 10: gates 7/7 green

## Round 11 rework (renderer source scan render_r2.md: N1)
- Read audits/render_source/credit_builder_accounts/render_r1.md and render_r2.md in full.
- N1: the three "latest payment" selections without a stated tie now carry the charter's tie clause, matching LATEST's first-booked behaviour:
  - goodwill AutoPay gate (gw_ap_id) and re-enrollment return buffer (ad_ap_id): "(the latest payment made through the AutoPay channel; when two were posted on the same day, the one booked first counts as the latest)" — the goodwill prerequisite sentence changed with it: policy_source in the charter and both quoting strings of tasks/1.json (prerequisite_closure edge and dossier) replaced verbatim (copies re-checked equal);
  - re-enrollment make-good lookup (ad_good_id): "the payment looked at is the latest payment posted toward that due date, and when two were posted toward it on the same day the one booked first counts as the latest: ...".
- Sweep of every LATEST / "most recent" / "latest" selection in all eight policies: hl_fee_id, hr_ret_id, hr_fee_id, rf_ret_id, rr_ret_id, rr_good_id, rr_fee_id, gw_fee_id, ad_code, cc_dc_id already state the first-booked tie; lf_dc_id needs none (its scope holds at most one card payment toward the late due date); ad_ap_ret_date reads the return pointing at one payment (one return row per returned payment in the base event); hr_req_date reads the pending request (the base allows only one pending request). CFIELD reads (hardship rates, FlexLine past due) are not LATEST selections and are unchanged.
- render_r1 S1–S7 untouched (no window, month, day-count, branch or docstring text edited). No compute changed; no scored value moved (0 differences on both tasks).

### Probe, round 11 (scratch copy; renderer's example on task 1's world)
| probe | policy | value | reading |
| --- | --- | --- | --- |
| two same-day payments toward the debit's due date, the card payment booked first and charged back, an ACH payment booked second | re-enrollment return buffer | 3 | the first-booked payment is the latest; a return points at it -> not made good -> flat |
| same two payments, the ACH payment booked first | re-enrollment return buffer | 6 | made good 5 days after the due date -> 5 + 1 |
| gold worlds | all eight computations | unchanged | |

### XF recipe, round 11
Text-only edits in the goodwill credit and the re-enrollment: 1–3 unchanged; 4 overwrites untouched; 5 verbatim sweep 0 misses (rule, compute_basis, replaced_by, policy_source); 8 tie probe above; 14 task-file copies of the changed prerequisite sentence updated and re-checked. Other points unaffected.

### Final gate run (round 11)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- check_traceability: misses only the 8 unlock tool names (KB not yet published) — expected.
- Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 11: gates 7/7 green

## Round 12 rework (seed-only: KB audit src items, audits/policy_kb + audits/runtime_context)
- Read audits/policy_kb/credit_builder_accounts/{0,1}.md and audits/runtime_context/credit_builder_accounts/{0,1}.md in full; priced every seeded row of another product in both tasks from that product's published docs (docs/hardship, docs/loan, docs/line, docs/pos). builder.extended.yaml (9873a89a342f4080) and task_tools.py (f8707267e656aa97) untouched.
- Loans (src-loan-ledger-sparse, src-loan-late-fee-share-t0, src-loan-fee-schedule-co-t1): every loan ledger now carries its monthly installments (online, on the due date or the business day before it; interest actual/365 on the paid-through date, interest then fees then principal; returns reverse in full), so balances, paid-through dates and next due dates follow the ledger. The loans are not on AutoPay (current rate = base rate, no AutoPay discount or AutoPay points anywhere).
  - Task 0 loan A (OH, schedule A): the 2026-05-10 late fee re-priced 13.65 (5% of 303.42 within the 15.00 minimum and 30.00 maximum, times the 0.9 first-late share), paid with that installment on 2026-05-29.
  - Task 1 loan (CO, schedule B): late fee 9.76 (5% of 216.88 times 0.9 first-late), returned-payment fee 8.50 (10.00 schedule-B fee times the 0.85 first-return share), both on schedule B; the 2026-07-20 installment is an online payment returned R01 and made up by debit card on 2026-07-24.
- Hardship (src-hardship-trr-rate-t0, src-hardship-rpp-installment-t0, src-hardship-trr-rate-t1): with no document recorded on the requests, the program figures apply — task 0 Reduced Payment Plan 50% less 5 points (grade C 1, 18 months 1, 12 net installments 3) = 45% of 303.42 = 136.54; task 0 Temporary Rate Reduction Plan 4.99 less 0.75 grade-E points = 4.24, installment = level installment of the decision-date principal over 17 due dates; task 1 Temporary Rate Reduction Plan 4.99 less 0.25 loan-age points = 4.74, level installment over 14 due dates. balance_at_request, plan installments, loan current rates and scheduled amounts all follow the rebuilt ledgers; plan installments are posted as hardship-plan payments.
- FlexLine (src-line-returned-fee-t0/t1): returned-payment fees re-priced 0.75 (2.5% of 35.00 figured at 0.88, times 0.85 for the only return in 24 months) and 0.95 (2.5% of 45.00 at 1.12, times 0.85); task 0 line balance lowered by the fee difference; task 1 make-up payment 45.95 (balance unchanged).
- PracticePay (src-pos-returned-fee-t1): the 2026-06-12 R01 return is made up within the 10-day grace period by a 100.00 payment; its returned-payment fee is booked after the grace period (2026-06-22) at 7.60 = 10.00 fee level x 0.8 (ledger balance under 1000.00) x 0.95 (active FlexLine with a clean 12-month record), the personal-loan share staying 1 (the 2025-07-06 loan late fee is within 12 months); a 7.60 payment on 2026-06-25 pays it, so the plan balance stays 600.00.
- Kept: every prerequisite unmet at the opening; every factor bears weight; the builder rows, the near-misses (task 1's 2025-07-06 loan late fee outside the goodwill window, 7 FlexLine payments in 6 months) and every row id that task text cites (loan 2a27c1a2 etc. re-keyed onto the rebuilt rows); new ids are uuid4.
- Scored move: task 0 settlement 1155.24 (cc_rate now 4.24); sensitivities cc_lead 1157.04 / cc_rate 1158.16 / cc_hardship 1156.32 / cc_cause 1155.36, all-baseline 1177.86; edge skips 1154.75 (mechanical 1154.37) / 1155.62 / 1155.94; opening 1155.45; terminal savings left 1247.76. Gold recomputed with the real tools (scratch evaluator, 0 differences); every proof text, trace, skip figure and sensitivity figure of task 0 swept; task 1's dossier seed paragraph rewritten (no scored value moved there).
- src-closing-interest-param logged as a known base issue (not routed); src-baseline-variation-wording not routed (coordinator decision).

### Final gate run (round 12)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY OK (docs published).
- builder.extended.yaml and task_tools.py byte-identical (9873a89a342f4080 / f8707267e656aa97). Scratch /tmp/credit_builder_accounts_0067/ and __pycache__ removed.

REWORK round 12: gates 7/7 green
