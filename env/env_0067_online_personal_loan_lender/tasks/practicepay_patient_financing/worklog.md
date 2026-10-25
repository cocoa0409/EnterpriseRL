# worklog — practicepay_patient_financing (category pos), M=2

## Step 0 — difficulty pre-check
- Read: references/{product_extended.yaml, task.json, task_tools.py}; blueprint.yaml; products/pos.yaml; db_schema.json (pos + loan/hardship/line/builder tables); share_tools.py (verify threshold 3 of phone/email/dob/ssn_last4/zip); audits/render_source/XF_recipe.md (14 points).
- Claimed event types: pos_payment_posted, pos_payment_returned, pos_late_fee_assessed, pos_returned_payment_fee_assessed, pos_fee_waived, pos_deferred_interest_billed, pos_deferred_interest_cleared, pos_plan_terms_updated, pos_plan_paid_off, pos_account_status_updated.
- Base automatic clauses to watch when seeding: status refresh after every line; DI accrual posted to memo at each statement closing (DI plans); DI billed the day after promo_end_date when the payoff test fails; monthly interest at statement closing (reduced-APR/standard, and DI plans after billing); late fee after 10-day grace; returned fee per fee-bearing return; delinquency reporting at 30 dpd; charge-off at 120 dpd; credit balance refund.
- Identifier band (coordinator): phone / ssn_last4 / bank account_last4 end 3000-3999; surnames J-L; emails from the persona's own name.

### Draw (scripts/draw_counts.py --tasks 2)
```
{"task": 0, "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 6, 5]}
{"task": 1, "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 5, 6]}
```
Six extended policies in all, 32 factors; each task a 3-problem tree with >= 1 value_input edge and >= 1 owner=user tool.

### Scope plan (principle C headroom)
- task 0 (claims 3): returned-payment fee (agent, state_due) -> late fee (agent, state_due) -> promotional payoff payment (customer's own one-time payment, root, on_request). Fees + payoff on a deferred-interest plan still inside its promotion.
- task 1 (claims 3, disjoint): deferred-interest billing (agent, state_due) -> deferred-interest credit for a provider-credited dispute (agent, state_due) -> post-promotion payment reset with AutoPay (customer's own, root, on_request).
- Nothing reserved; task 1's space (end of promotion, dispute credits, re-amortisation) is untouched by task 0 (inside the promotion, fees, payoff).

### Task tools (uuid8 drawn one call per tool)
- assess_returned_payment_fee_f9ef5ea0 (agent) — task 0
- assess_late_fee_02ab9d3a (agent) — task 0
- pay_off_plan_f18fb847 (user) — task 0 root
- bill_deferred_interest_8f2fb1f1 (agent) — task 1
- credit_disputed_deferred_interest_91950e60 (agent) — task 1
- reset_payment_and_autopay_03cef1f2 (user) — task 1 root

### Design note (Step 0, in progress)
- Finding: payment/payoff amounts carry few customer-tiered rules in real servicing; tiered rules live in fees, rates,
  interest accrual conventions, settlement (good-through) days and credits. Each user-owned computation is therefore
  built on interest mechanics (rate in force, accrual anchor, good-through days) rather than invented payment programs.
- Decision (task 0, fan-out tree): root payoff payment (user) <- late fee (agent, value_input via the balance) and
  root <- returned-payment fee (agent, value_input via the balance). The one-fee-per-returned-payment limit sits in the
  payoff (both fees must stand first). Plan: PracticePay 24-Month Reduced APR Plan (interest-bearing, so the payoff
  carries a stub of simple daily interest, a good-through period, disputes and fee-event rules).
- Decision (task 1, chain): root post-promotion payment reset + AutoPay (user) <- deferred-interest credit for a
  provider-credited dispute (agent) <- deferred-interest billing (agent).

## Task 0 — closed (per-task gates green)
- Tree: pos_ext_payoff_quote (root, user tool pay_off_plan_f18fb847) <- pos_ext_late_fee_schedule (agent) <- pos_ext_returned_item_fee (agent); both edges value_input, state form.
- Gold: returned-payment fee 10.77 (step 10) -> late fee 2.18 (step 12) -> payoff 2150.29 (step 14, customer's own payment from UW Credit Union 3741).
- Revisions: (1) first draft put a fee-event limit inside the payoff -> root cause: a payoff that leaves a booked fee uncollected cannot close the plan -> moved the one-fee-per-returned-payment rule into the late-fee policy (chain edge late fee <- returned fee). (2) good-through days kept as quoting interest through a settlement period whose excess is refunded under the base credit-balance rule. (3) `in [...]` lists are not in the DSL -> rewritten as `==`/`or`. (4) replay closure flagged unread rows (old vet plan, its merchant) -> removed. (5) check_compute: the loan-standing factor read loan late fees but none were seeded -> seeded a real 2025-08-09 loan late fee (schedule C, 10.00, paid) 14 months back as the near-miss; historic July/August fees recomputed by gen0.py on their dated worlds (14.40 / 10.80).
- Gate run (per task 0): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.

## Task 1 — closed (per-task gates green)
- Tree (chain): pos_ext_post_promo_reset (root, user tool reset_payment_and_autopay_03cef1f2) <- pos_ext_disputed_interest_credit (agent) <- pos_ext_deferred_interest_bill (agent); both edges value_input, state form.
- Gold: deferred interest billed 226.02 dated 2026-10-09 (step 10) -> dispute-resolved credit 5.85 against the billing entry ptx_aafc4159f260 from the step-10 receipt (step 12) -> reset payment 91.90 with AutoPay (step 14, the customer's own).
- Revisions: (1) the courtesy gates of pos_evt_fee_waiver would have bound the credit to a courtesy request window/count and could not be evidenced on a billing entry booked by a prior step -> declared scoped overwrites restating the courtesy rules and exempting a dispute-resolved deferred-interest credit. (2) the post-promo APR clause is a gate sentence (billed_after_promo); both the billing and reset policies declare sibling overwrites naming each other's case; the billing rule restates the day-after-promo-end timing. (3) shortfall/paydown factors read only plan fields -> rewritten on the ledger principal (SUM). (4) history-zeroed floor: autopay and paydown cuts cancelled -> reset_quarter_cut 1.25. (5) world: due day 20 so the reset falls 8 days before an already-billed installment (remaining-payments tier) and frozen_time precedes the 2026-10-14 closing (no post-billing interest due).
- Gate run (per task 1): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.

## XF_recipe.md — point-by-point record (all six policies)
1. Factor independence — scratch sweep xfcheck.py (factor binding reads factor binding of another factor): [] for all six. Factor-read table (each factor's bindings read only its own bindings or plain bindings):
   | policy | factor -> plain bindings it reads |
   |---|---|
   | returned_item_fee | returned_item_level -> none; return_reason_share -> none; item_size_rule -> monthly_due; plan_age_band -> none; ledger_balance_band -> none; personal_loan_standing -> none |
   | late_fee_schedule | late_record_level -> none; partial_payment_rule -> due_date, unpaid_part, monthly_due; late_plan_age_band / late_ledger_balance_band / late_loan_standing -> none |
   | payoff_quote | stub_interest_span -> interest_base, daily_rate, last_closing; disputed_carve_out / return_record_hold / return_reason_hold / personal_loan_return_hold -> none |
   | deferred_interest_bill | di_unposted_span -> accrual_base, daily_rate, last_posting, promo_end; disputed_interest_relief -> daily_rate, promo_end; shortfall / record / autopay / loan -> none |
   | disputed_interest_credit | credit_days_rule -> credited_amount, dispute_resolved, refund_date; shortfall / record / autopay / loan -> none |
   | post_promo_reset | remaining_payments_rule -> due_date; loan / record / autopay / paydown cuts -> none |
   Results are assembled only in plain bindings / result.
2. Assembly stated once, generically, with order: each rule has one "Where a rule of this ... sets ..." sentence naming no factor quantity: fees — level replaces, shares multiply together, cap, single rounding (late fee: netting after the cap, before rounding); payoff — span replaces, days added, amount left out subtracted, single rounding; bill — span replaces, amount not billed subtracted, then shares, single rounding; credit — days replace, shares, cap, single rounding; reset — cuts subtracted (floor 0), count replaces, payment worked out once.
3. Factor-only quantities live in the factor's own sentence (e.g. "The item-size share of a returned-payment fee ...", "The paydown rate cut of a reset ..."); baselines name none of them; no sentence says "as another policy figures it".
4. Overwrite hygiene: every replaced_by names its scope ("for a ... and only for such ...") and restates what stays in force (non-fee codes carry no fee; one late fee per due date and the open-dispute exclusion; courtesy rules for courtesy waivers; partial refunds that settle no dispute; plan APR for billed plans not reset; activation payment for other plans). Sibling overwrites of the post-promo APR clause (bill, reset) each name the other's case. No rule defers to a clause it retires. Payoff declares [] (it adds a quote; interest and credit-balance rules are the base's own).
5. compute_basis verbatim sweep (xfcheck.py): basis-not-verbatim [] and bindings-without-basis [] for all six.
6. Rounding: every rule says "rounded to the nearest cent once, at the end" matching a single RND on result (fees, payoff, bill, credit); the reset says "rounded up to the next cent", implemented by the integer-cents round-up on the final level amount only.
7. Docstrings: describe formats only (no example values), claim only body effects (balance/memo/past-due updates, entries created), no ordering words, no other tool names (check_task_tools OK).
8. Edge probes (probe0.py / probe1.py, scratch copies) — decoy/absent-record table:
   | read | probe | outcome |
   |---|---|---|
   | latest return (fee) | none / R10 / same-day second return | 0.00 / 0.00 / first recorded kept 10.77 |
   | loan CFIELD/EXISTS | no loan / loan past due | share 1 / 0.95 |
   | latest payment toward due date (late fee) | not booked fee / partial on last grace day / none standing / dispute open | 12.95 / proportional / flat 14.75 / unpaid 0 -> 0.00 |
   | latest closing / latest payment (payoff) | no interest charge / payment on closing day / credit refund posted / no loan | purchase anchor / closing anchor (not "after") / nothing left out / 0 extra days |
   | latest dispute (bill) | none / open / withdrawn | 0 / filing-to-promo-end / 0 |
   | latest payment (bill) | after promo end / returned AutoPay debit | no split / record 0.98, autopay 0.98 |
   | billing entry / refund (credit) | no entry / refund not posted / other reason / refund on resolution date | 0.00 / 0.00 / 4 days / 23 days |
   | due dates (reset) | past due / next due far off | 19 payments / 18 |
   Same-day ties stated in the rules ("the one recorded first"); month-end convention stated ("a month being whole once the ... day of the month has reached ..."); days counted "from the day after the start date through the end date"; None guarded with `!= None` / `or 0`; no division by a zero monthly payment (min 25) or zero rate (equal division branch).
9. Method tiers change formula shape — pairwise tier table with distinguishing input:
   | factor | tier A vs B vs fall-through | distinguishing input |
   |---|---|---|
   | item_size_rule | ratio vs fixed 0.5 vs flat 1 | 90.00/121.82 = 0.74 -> ratio; 50.00 -> 0.5 (ratio 0.41); 121.82 -> 1 |
   | partial_payment_rule | ratio vs MX(0.5, ratio) vs 1 | 100.00 of 121.82 paid (unpaid ratio 0.18): in grace -> 0.18, after grace -> 0.5; nothing standing -> 1 |
   | stub_interest_span | split vs purchase anchor vs closing anchor | 60.00 on 10-14 -> 2.4532 vs 2.4204 (closing) vs no closing -> 108.31 |
   | di_unposted_span | split vs purchase anchor vs posting anchor | 8.6676 vs 7.3365 vs 148.36 |
   | disputed_interest_relief | filing-to-resolution vs filing-to-promo-end vs none | 13.21 vs 44.68 vs 0 |
   | credit_days_rule | 23+4 vs 23 vs 4 | refund 06-22 / 06-18 / other reason |
   | remaining_payments_rule | from oldest unpaid vs next-less-one vs elapsed | 19 vs 17 vs 18 |
10. No factor id is a substring of any tool name (xfcheck.py: []).
11. No cross-record pairing: loan reads are single-record CFIELD/EXISTS on status=active plus customer-scoped XCOUNTs.
12. Realism: fees are a Larkspur fee schedule (first/repeat levels in the Reg Z safe-harbour pattern, account-problem return reasons, partial-item proportion, one fee per returned payment); the payoff quotes interest through a good-through period with any excess refunded under the base credit-balance rule; disputed-amount interest relief and the credit of interest on a provider-credited duplicate charge follow the billing-error principle; post-promotion re-amortisation over the remaining term with relationship/record rate cuts. Seeded loan rows are states the loan charter produces (WI = fee schedule C: 10.00 flat late fee, no returned-payment fee line; 15-day grace; fee-payment lines). No fee on unbilled interest, no post-closing fee raise, no fee on a fee.
13. Runtime: frozen_time "2026-10-16 10:20:00 CDT" / "2026-10-12 11:05:00 CDT"; task_tools.py imports only erlbench, no datetime/time/random/uuid/secrets; every write tool calls ctx.create/update in its own body; no module-level helper functions (only tools).
14. Proof text swept after each revision: rationales, prerequisite_closure, necessity and trace arithmetic regenerated from build0/build1 outputs (numbers0.json / numbers1.json) on every rebuild.

## Difficulty-level closing
- Union: tasks 0 and 1 claim {returned_item_fee, late_fee_schedule, payoff_quote} and {deferred_interest_bill, disputed_interest_credit, post_promo_reset}: disjoint, covering all six extended policies and all six tools.
- Full gate run (no --task): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 50.00, steps 15.00; history_rows_max 55; branches_max 50) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK; TRACEABILITY: the only 6 misses are the unlock tool names (pre-publication, expected).
- Scratch /tmp/practicepay_patient_financing_0067/ (generators, probes, sweeps) removed; __pycache__ removed.
REWORK round 1: gates 7/7 green

## Rework round 2 — redesign plan (audits/policy_task/practicepay_patient_financing/, revision_1)
- Audit REDs: CG-1..CG-10, T0-1, T0-2, T1-1..T1-6. Root cause of CG-8/9/10: deferred-interest billing and the
  dispute deferred-interest credit admit no real customer-tiered rule (deferred interest is assessed in full; a
  billing-error credit is never scaled), so both are retired and replaced by computations whose tiers are real
  servicing practice; every method factor now changes the formula's shape.
- New scope: task 0 = payoff (root, user) <- late fee (agent) and <- returned-payment fee reversal on a replaced
  payment (agent); task 1 = courtesy waiver of a returned-payment fee (root, agent, on request) <- returned-payment
  fee (agent) and <- post-promotion payment reset with AutoPay (user; the courtesy rule's AutoPay gate and its
  AutoPay-record tier).
- Class fixes planned: personal-loan / FlexLine reads over all of the customer's accounts by ledger history (no
  first-match CFIELD); a tie rule on every LATEST read; no negative day counts; prerequisite sentences worded to
  exactly their conditions; docstrings naming no other write; the reset stores the rate it sets; no overwrite of a
  clause that never conflicted.

## Rework round 2 — what changed (task by task)
- Charter now: pos_ext_returned_item_fee (task 1), pos_ext_late_fee_schedule (task 0), pos_ext_make_good_reversal (task 0, new),
  pos_ext_payoff_quote (task 0, root), pos_ext_courtesy_returned_fee_waiver (task 1, root, new), pos_ext_post_promo_reset (task 1).
  Retired: pos_ext_deferred_interest_bill and pos_ext_disputed_interest_credit with their tools; new tools
  reverse_returned_payment_fee_68fd6551 and grant_courtesy_fee_waiver_c5ffad08 (uuid8 drawn one call per tool); the reset tool
  now also stores the rate it sets (plan_apr).
- Struck factor families replaced: return-reason and plan-age shares, the proportional item size, deferred-interest
  forgiveness shares and scaled billing-error credits are gone; methods now change shape (graduated / proportional / none
  surcharge; floored ratio / ratio / flat partial-payment share; amount ratio / day ratio / full make-good extent;
  no-interest / split / single-span payoff interest; read / difference / none carve-out; re-amortize / re-divide / keep
  reset; capped / excess / whole courtesy sizing).
- Personal-loan and FlexLine reads: whether the customer holds an active account (EXISTS) and late fees / returned payments /
  courtesy waivers counted over all of the customer's accounts' ledgers; no first-match CFIELD remains; tiers monotone (a worse
  record never earns a larger concession).
- Every LATEST read sits under a rule sentence with "the one recorded first where two share that date"; every window states
  the whole-month convention; spans count from the day after the start; remaining payments never fewer than one; the late
  fee's unpaid part never below zero.
- Prerequisite sentences now say exactly what the resolving rule can book (oldest unpaid due date; latest returned payment);
  the make-good edge uses the action form because a requested courtesy waiver leaves the same record.
- Worlds rebuilt (gen0/gen1): task 0 keeps Renata's plan with a 30.00 make-good of the 2026-10-06 return and adds her FlexLine;
  task 1 is Desmond's deferred-interest plan after system billing, a bounced 600.00 payment, AutoPay off, a withdrawn dispute,
  his loan (courtesy waiver 16 months back, a return within 12 months) and FlexLine (a return within 12 months).
- Skip figures recomputed by replaying each skip with every later write re-evaluated on the skipped world (build0/build1).

### Probe table (scratch copies of each handling-time world; probes.py)
| policy | probe | outcome |
|---|---|---|
| returned_item_fee | gold | item_fee_level=10.0, item_surcharge=15.0, loan_share=0.95, line_share=0.98, result=20.95 |
| returned_item_fee | absent: no returned payment | item_fee_level=15.0, item_surcharge=0, loan_share=0.95, line_share=0.98, result=0 |
| returned_item_fee | decoy: latest return R10 (no fee) | item_fee_level=10.0, item_surcharge=15.0, loan_share=0.95, line_share=0.98, result=0 |
| returned_item_fee | tie: second same-day return recorded later | item_fee_level=15.0, item_surcharge=15.0, loan_share=0.95, line_share=0.98, result=25.14 |
| returned_item_fee | row-order swap: same-day return recorded first | item_fee_level=15.0, item_surcharge=0, loan_share=0.95, line_share=0.98, result=12.57 |
| returned_item_fee | second loan (refinanced, late fee 4 months back) | item_fee_level=10.0, item_surcharge=15.0, loan_share=1, line_share=0.98, result=22.05 |
| returned_item_fee | absent: no personal loan | item_fee_level=10.0, item_surcharge=15.0, loan_share=1, line_share=0.98, result=22.05 |
| returned_item_fee | decoy: FlexLine closed | item_fee_level=10.0, item_surcharge=15.0, loan_share=0.95, line_share=1, result=21.38 |
| returned_item_fee | tier: item above 1000 (graduated) | item_fee_level=10.0, item_surcharge=45.0, loan_share=0.95, line_share=0.98, result=46.08 |
| returned_item_fee | edge: item smaller than the fee (cap) | item_fee_level=10.0, item_surcharge=0, loan_share=0.95, line_share=0.98, result=8.0 |
| late_fee_schedule | gold | unpaid_part=91.82, late_fee_level=35.0, partial_share=0.7537, loan_share=0.95, line_share=0.98, result=22.1 |
| late_fee_schedule | decoy: latest toward due date is the returned 90.00 | unpaid_part=91.82, late_fee_level=35.0, partial_share=1, loan_share=0.95, line_share=0.98, result=29.33 |
| late_fee_schedule | tie: second payment same latest date | unpaid_part=91.82, late_fee_level=35.0, partial_share=0.7537, loan_share=0.95, line_share=0.98, result=22.1 |
| late_fee_schedule | tier: partial on the last grace day | unpaid_part=91.82, late_fee_level=35.0, partial_share=0.7537, loan_share=0.95, line_share=0.98, result=22.1 |
| late_fee_schedule | decoy: dispute still open | unpaid_part=6.82, late_fee_level=35.0, partial_share=0.5, loan_share=0.95, line_share=0.98, result=6.82 |
| late_fee_schedule | second loan (refinanced, late fee 4 months back) | unpaid_part=91.82, late_fee_level=35.0, partial_share=0.7537, loan_share=1, line_share=0.98, result=23.27 |
| late_fee_schedule | edge: negative past due | unpaid_part=0, late_fee_level=35.0, partial_share=0.5, loan_share=0.95, line_share=0.98, result=0.0 |
| make_good_reversal | gold | made_good=30.0, make_good_extent=0.3333, days_to_make_good=8, timing_share=0.75, result=1.47 |
| make_good_reversal | absent: nothing made good | made_good=0.0, make_good_extent=1, days_to_make_good=0, timing_share=1, result=0 |
| make_good_reversal | absent: return carries no fee | made_good=30.0, make_good_extent=1, days_to_make_good=0, timing_share=1, result=0 |
| make_good_reversal | decoy: fee already waived | made_good=30.0, make_good_extent=1, days_to_make_good=0, timing_share=1, result=0 |
| make_good_reversal | tier: made good in full within grace | made_good=90.0, make_good_extent=1, days_to_make_good=3, timing_share=1, result=5.89 |
| make_good_reversal | tier: made good in full after grace (day ratio) | made_good=90.0, make_good_extent=0.8333, days_to_make_good=8, timing_share=0.75, result=3.68 |
| make_good_reversal | tie: two make-good payments same date | made_good=40.0, make_good_extent=0.4444, days_to_make_good=8, timing_share=0.75, result=1.96 |
| make_good_reversal | absent: no return | made_good=0.0, make_good_extent=1, days_to_make_good=0, timing_share=1, result=0 |
| payoff_quote | gold | interest_base=2240.81, stub_interest=2.4696, amount_left_out=85.0, loan_extra_days=2, line_extra_days=1, result=2209.67 |
| payoff_quote | absent: no interest charge yet | interest_base=2240.81, stub_interest=109.7819, amount_left_out=85.0, loan_extra_days=2, line_extra_days=1, result=2316.98 |
| payoff_quote | tier: deferred-interest plan inside promotion | interest_base=2240.81, stub_interest=0, amount_left_out=85.0, loan_extra_days=2, line_extra_days=1, result=2197.39 |
| payoff_quote | edge: payment on the closing day | interest_base=2240.81, stub_interest=2.4532, amount_left_out=85.0, loan_extra_days=2, line_extra_days=1, result=2209.66 |
| payoff_quote | decoy: dispute open | interest_base=2240.81, stub_interest=2.4696, amount_left_out=85.0, loan_extra_days=2, line_extra_days=1, result=2209.67 |
| payoff_quote | decoy: credit refund posted | interest_base=2240.81, stub_interest=2.4696, amount_left_out=0, loan_extra_days=2, line_extra_days=1, result=2294.67 |
| payoff_quote | second loan (refinanced, late fee 4 months back) | interest_base=2240.81, stub_interest=2.4696, amount_left_out=85.0, loan_extra_days=5, line_extra_days=1, result=2211.51 |
| payoff_quote | absent: no loan or FlexLine history | interest_base=2240.81, stub_interest=2.4696, amount_left_out=85.0, loan_extra_days=0, line_extra_days=0, result=2207.83 |
| courtesy_returned_fee_waiver | gold | sized_waiver=15.0, courtesy_share=0.75, autopay_share=0.75, result=4.75 |
| courtesy_returned_fee_waiver | gate: AutoPay off | sized_waiver=15.0, courtesy_share=0.75, autopay_share=0.75, result=0 |
| courtesy_returned_fee_waiver | decoy: fee already waived | sized_waiver=15.0, courtesy_share=0.75, autopay_share=0.75, result=0 |
| courtesy_returned_fee_waiver | absent: no fee booked | sized_waiver=0.0, courtesy_share=0.75, autopay_share=0.75, result=0 |
| courtesy_returned_fee_waiver | tier: small item, second return (excess) | sized_waiver=10.95, courtesy_share=0.75, autopay_share=0.75, result=3.46 |
| courtesy_returned_fee_waiver | absent: no loan history | sized_waiver=15.0, courtesy_share=1, autopay_share=0.75, result=8.44 |
| post_promo_reset | gold | remaining_payments=18, reset_rate=24.24, method_choice=1, result=107.91, stored_rate=24.24 |
| post_promo_reset | tier: no deferred-interest billing (keep payment) | remaining_payments=18, reset_rate=24.24, method_choice=0, result=155.52, stored_rate=26.99 |
| post_promo_reset | tier: no-interest plan with refund (equal division) | remaining_payments=18, reset_rate=24.24, method_choice=2, result=89.72, stored_rate=26.99 |
| post_promo_reset | edge: cuts exceed APR (rate floor 0) | remaining_payments=18, reset_rate=0, method_choice=1, result=89.72, stored_rate=0 |
| post_promo_reset | edge: next due beyond the term (one payment) | remaining_payments=1, reset_rate=24.24, method_choice=1, result=1647.49, stored_rate=24.24 |
| post_promo_reset | second loan (refinanced, late fee 4 months back) | remaining_payments=18, reset_rate=25.24, method_choice=1, result=108.7, stored_rate=25.24 |
| post_promo_reset | month-end: purchase 01-31, next due 02-28 | remaining_payments=24, reset_rate=24.24, method_choice=1, result=85.58, stored_rate=24.24 |
Readings of the table: ties keep the entry recorded first (row-order swap flips the choice exactly as the rule says); a
second, refinanced loan with a recent late fee moves every personal-loan factor because the rules read all of the customer's
loans; closed FlexLines, withdrawn disputes, waived fees, returned payments and missing records each fall to their stated
tier; no probe crashes (no None, zero-division or negative-day path).

### XF_recipe.md — round-2 point-by-point (all six policies; xfcheck.py with transitive reads)
1. Factor independence: transitive factor->factor reads [] for all six. Shared selections are plain (returned payment ids,
   fee ids, due date, unpaid part, interest base, reset balance, reset rate, method amount). The reset's method factor decides
   the method choice only; the annuity that uses the cut factors is assembled in plain bindings.
2. Assembly: one generic "Where a rule of this ... sets ..." sentence per policy fixes order (level + surcharge, then shares,
   then cap, then one rounding; extent x shares capped at the fee; cuts off the APR, floor 0, then one payment computation,
   rounded up, floor 25.00; span replaced, good-through days added, carve-out subtracted, one rounding).
3. Factor-only quantities are defined in their own sentence; baselines name none of them.
4. Overwrites: returned fee (amount clause, self-scoped, non-fee codes restated); late fee (amount/dedup clause, restated);
   make-good (courtesy-count clause: a make-good reversal is booked on the courtesy basis without a request — a real
   conflict); reset (post-billing APR clause, AutoPay no-discount clause, activation payment clause — each self-scoped and
   restating the base for every other plan); payoff and courtesy waiver declare []. The three round-1 non-conflicting
   fee-waiver overwrites are gone.
5. compute_basis verbatim sweep: [] for all six; every baseline sentence and replaced_by is in its rule.
6. Rounding: single RND at the end (fees, reversal, payoff, waiver); the reset rounds up to the cent once, then the floor.
7. Docstrings: no example values (the rate argument describes its format only), no ordering words, no reference to another
   tool or its receipt; every effect claimed is stored (ledger entry, balance, plan_apr, AutoPay).
8. Edge branches: probe table above (decoy, absent, tie, row-order, second loan, closed FlexLine, month-end, zero/negative).
9. Method tiers change shape (round-2 list above); pairwise distinguishing inputs are the probe rows of each method factor.
10. No factor id is a substring of a tool name ([]).
11. No cross-record date pairing; loan/FlexLine reads are customer-scoped counts plus an existence test.
12. Realism: relationship and record bands on penalty fees, return holds, rate cuts and courtesy sizing are the families the
    round-1 audit kept; struck families are removed; the graduated large-item surcharge mirrors tiered returned-item
    schedules; seeded loan/FlexLine rows are charter states (WI schedule C, FlexLine fees and statement lead).
13. Runtime: frozen_time "YYYY-MM-DD HH:MM:SS CDT"; task_tools.py imports only erlbench; every write tool writes in its body.
14. Proof text: both design_rationales rewritten; closures, necessity, traces and skip figures regenerated from the
    re-run outputs (numbers0.json / numbers1.json); the round-1 skip figures and the stale tier labels no longer exist.

### Gate run (full difficulty, round 2)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 2: gates 7/7 green

## Rework round 3 — plan (audit revision_2: CG-3, CG-9, CG-10, R2-1..R2-12, T0-R2-1, T1-R2-1..3)
- Root causes: (a) task 1's gold reset the payment and APR although the customer asked only for a fee waiver (the courtesy
  rule's AutoPay gate could be met only through the reset); (b) the make-good reversal's fractional extent and the returned-fee
  item-size surcharge are not lender practice, leaving those computations without a real method factor; (c) the reset's rate
  cuts moved the payment only under its non-baseline method.
- New scope: task 0 (Renata, 48-Month Reduced APR plan, two courtesy waivers per 12 months) = payoff (root, user) <- automatic
  late-fee relief and <- automatic returned-payment-fee relief (both owed on fees already charged); task 1 (Desmond,
  deferred-interest plan after billing) = the payment reset he asks for (root, user; payment and rate only, no AutoPay) <-
  returned-payment fee <- late fee (one payment that came back is never charged two full fees: the returned-payment fee is
  reduced by the late fee of the same due date, net of any waiver of it). The courtesy waiver on request and the make-good
  reversal are retired with their tools; the reset tool is replaced by one that writes only the payment and the rate.
- Every write policy states what happens when its amount is 0.00 (nothing is booked and the waited-on state counts as met).

## Rework round 3 — implementation (audit revision_2)
- Scope now: task 0 = {pos_ext_late_fee_relief, pos_ext_returned_fee_relief, pos_ext_payoff_quote} with tools
  relieve_late_fee_b1a4bf3c, relieve_returned_payment_fee_3fbe4785 (new uuid8s, one draw each), pay_off_plan_f18fb847 (user);
  task 1 = {pos_ext_late_fee_schedule, pos_ext_returned_item_fee, pos_ext_payment_reset} with assess_late_fee_02ab9d3a,
  assess_returned_payment_fee_f9ef5ea0, reset_monthly_payment_233e8b10 (new, user; writes payment and rate only).
  Retired with their tools: make-good reversal (reverse_returned_payment_fee_68fd6551), courtesy waiver
  (grant_courtesy_fee_waiver_c5ffad08), post-promotion reset with AutoPay (reset_payment_and_autopay_03cef1f2).
- Draws kept: task 0 counts {6,5,5} (PQ 6, reliefs 5+5); task 1 {6,5,5} (reset 6, fees 5+5); 2 prerequisites each.
- Task 1 re-worlded: Desmond asks only for a payment reset at any lower rate he qualifies for; gold writes are the two
  fees the system owes (late fee for 2026-10-04 after its grace period, then the returned-payment fee of the 600.00 that
  came back, which the one-penalty limit decides only after that late fee) and the reset he asked for. Frozen 2026-10-15.
- Task 0 re-worlded: Renata (48-Month Reduced APR, two courtesy waivers per 12 months, none used) asks only for a payoff;
  the reliefs owed on her 2026-09-21 late fee and 2026-10-06 returned-payment fee (both made up on 2026-10-13, cleared
  2026-10-16) are booked first.
- Zero-amount rule in every write policy: a late fee, returned-payment fee or relief that works out to 0.00 is not owed
  and nothing is booked; a payoff of 0.00 takes no payment; a reset is never below min_monthly_payment_usd.
- New overwrites: LFR restates the courtesy sentence (reliefs granted without request, booked on the courtesy basis,
  counted among the courtesy waivers; scope named); the reset restates the activation payment method, the AutoPay
  sentence (history count only; AutoPay is never set by the reset) and the partial-refund recast sentence (only on the
  customer's request). PQ needs no overwrite: interest after a deferred-interest billing now runs from the billing date.

### Round 3 — XF recipe, point by point (all six policies)
1. Factor independence: mechanical transitive sweep (xfcheck) — no factor binding reaches another factor's binding; every
   factor alone against the all-baseline compute moves the result (factor_report alone column, both tasks). PQ's
   promotion test now sits inside the interest factor (stub and good-through accrual), its baseline restoring both (R2-6).
   The reset's baseline method is rate-sensitive (activation formula at the reset rate), so each rate cut moves alone (R2-7).
2. Assembly stated once with order: LFS/RIF "level, shares, limit/cap, then round once"; reliefs "size, shares, cap at the
   unwaived fee, round once"; reset "cuts from the APR (floor 0), payment by the method, round up, floor"; PQ unchanged.
3. Factor-only quantities: the reset balance is now defined inside the method sentence (removed from the baseline);
   relief sizes, timing days, AutoPay/principal shares are defined in their own ladders; no baseline sentence names one.
4. Overwrites: every departure declared and self-scoped (LFR courtesy sentence naming both relief schedules; RFR follows it;
   reset x4 each naming "only for a plan whose customer asks"); LFS/RIF fee clauses unchanged; no overwrite retires an
   unconflicted clause; no rule defers to a clause it retires.
5. compute_basis verbatim: sweep 0 problems (also baseline sentences, replaced_by, superseded, policy_source).
6. Rounding: RND once at result in LFS/RIF/LFR/RFR/PQ; reset rounds up once (cents ceiling) then floors at 25.00.
7. Docstrings: formats only, no example values, no other tool names or ordering words; relief/reset tools claim only
   the rows and fields their bodies write (the reset leaves AutoPay, due day and next due date as they are).
8. Edge branches: see the probe table (decoy/absent/tie/month-end/negative lag/zero cases). Every LATEST states its tie
   rule; make-up and replacement payments must be dated after the fee/return and not have come back (R2-3 class).
9. Method tiers (pairwise, distinguishing input): RIF one-event difference vs capped-at-monthly vs unlimited (payment
   dated inside grace with a standing late fee / dated after grace / no due date); reset re-divide vs re-amortize vs
   activation formula (no-interest plan / DI-billed or refunded / neither; the last uses financed amount and term, the
   second the balance and remaining payments); LFR capped vs keep-back vs whole (two returns / one / none in 6 months);
   RFR capped vs keep-back vs whole (late fee names the due date / other late fee in 6 months / none); LFS and PQ as
   accepted in revision_2.
10. No factor id is a substring of any tool name (swept).
11. No cross-record date pairing; the only date pairs are within one plan's ledger.
12. Realism: the item-size surcharge and fractional make-good extent are gone; the returned-payment fee's method is the
   Reg Z-style one-penalty limit (return and its late fee are one event; dollar cap at the payment due); reliefs use the
   accepted capped/keep-back/whole sizing with record and relationship shares; seeded loan/FlexLine rows unchanged.
13. Runtime: frozen_time in YYYY-MM-DD HH:MM:SS TZ; task_tools imports only erlbench; every write tool writes in its body.
14. Proof text: both tasks' rationale, closure, tracing and skip figures rebuilt from the round-3 replay (no carried text).

### Round 3 — factor-read table (XF1; mechanical, transitive through plain bindings: no factor binding reaches another factor's binding)
| policy | factor | P/M | bindings | reads (records / plain bindings) |
|---|---|---|---|---|
| pos_ext_payoff_quote | interest_since_closing_rule | M | di_billed_count, promo_running, last_pay_id, last_pay_date, last_pay_amount, last_pay_returned, stub_interest, hold_accrual | COUNT(pos_transactions), F(promo_end_date), LATEST(pos_transactions), daily_rate, interest_base, last_closing, span_start |
| pos_ext_payoff_quote | dispute_carve_out_rule | M | open_disputed, credited_disputed, refunds_posted, amount_left_out | SUM(pos_billing_disputes), SUM(pos_transactions) |
| pos_ext_payoff_quote | return_record_hold | P | returns_6m, return_hold_days | COUNT(pos_transactions), K(repeat_return_hold_days), K(single_return_hold_days), K(standard_hold_days) |
| pos_ext_payoff_quote | return_reason_hold | P | account_problem_returns_6m, funds_returns_6m, reason_extra_days | COUNT(pos_transactions), K(account_problem_extra_days), K(funds_return_extra_days) |
| pos_ext_payoff_quote | personal_loan_return_hold | P | loan_returns_6m, loan_late_12m, loan_extra_days | K(loan_late_extra_days), K(loan_returned_extra_days), XCOUNT(loan) |
| pos_ext_payoff_quote | flexline_return_hold | P | line_returns_6m, line_late_12m, line_extra_days | K(line_late_extra_days), K(line_returned_extra_days), XCOUNT(line) |
| pos_ext_late_fee_relief | late_relief_size_rule | M | returns_6m, relief_size | COUNT(pos_transactions), K(late_relief_cap_usd), K(late_relief_keep_usd), lfee_amount |
| pos_ext_late_fee_relief | late_relief_timing_band | P | make_up_days, timing_share | K(late_relief_mid_timing_share), K(late_relief_quick_days), K(late_relief_slow_days), K(late_relief_slow_timing_share), lfee_date, made_up, make_up_date |
| pos_ext_late_fee_relief | late_relief_autopay_record | P | autopay_debits, autopay_share | COUNT(pos_transactions), K(late_relief_autopay_full_count), K(late_relief_autopay_none_share), K(late_relief_autopay_some_count), K(late_relief_autopay_some_share) |
| pos_ext_late_fee_relief | late_relief_loan_record | P | loan_late_12m, loan_returns_12m, loan_share | K(late_relief_loan_late_share), K(late_relief_loan_returned_share), XCOUNT(loan) |
| pos_ext_late_fee_relief | late_relief_flexline_record | P | line_late_12m, line_returns_12m, line_share | K(late_relief_line_late_share), K(late_relief_line_returned_share), XCOUNT(line) |
| pos_ext_returned_fee_relief | returned_relief_size_rule | M | same_due_late_count, late_fees_6m, relief_size | COUNT(pos_transactions), K(returned_relief_cap_usd), K(returned_relief_keep_usd), credited, ret_due, rfee_amount |
| pos_ext_returned_fee_relief | returned_relief_timing_band | P | replace_days, timing_share | K(returned_relief_mid_timing_share), K(returned_relief_quick_days), K(returned_relief_slow_days), K(returned_relief_slow_timing_share), replace_date, replaced, ret_date |
| pos_ext_returned_fee_relief | returned_relief_principal_band | P | principal_left, principal_share | K(returned_relief_high_principal_share), K(returned_relief_high_principal_usd), K(returned_relief_low_principal_usd), K(returned_relief_mid_principal_share), SUM(pos_transactions) |
| pos_ext_returned_fee_relief | returned_relief_loan_record | P | loan_late_12m, loan_returns_12m, loan_share | K(returned_relief_loan_late_share), K(returned_relief_loan_returned_share), XCOUNT(loan) |
| pos_ext_returned_fee_relief | returned_relief_flexline_record | P | line_late_12m, line_returns_12m, line_share | K(returned_relief_line_late_share), K(returned_relief_line_returned_share), XCOUNT(line) |
| pos_ext_late_fee_schedule | late_record_level | P | late_fees_6m, late_fees_12m, late_fee_level | COUNT(pos_transactions), K(first_late_fee_usd), K(repeat_late_fee_usd), P(late_fee_usd) |
| pos_ext_late_fee_schedule | partial_payment_rule | M | last_credit_id, last_credit_date, last_credit_returned, credit_stands, credit_day_after_due, unpaid_ratio, partial_share | COUNT(pos_transactions), K(late_after_grace_floor_share), LATEST(pos_transactions), P(late_fee_grace_days), due_date, monthly_due, unpaid_part |
| pos_ext_late_fee_schedule | late_principal_band | P | principal_left, principal_share | K(late_low_principal_limit_usd), K(late_low_principal_share), K(late_mid_principal_limit_usd), K(late_mid_principal_share), SUM(pos_transactions) |
| pos_ext_late_fee_schedule | late_fee_loan_record | P | loan_active, loan_late_12m, loan_returns_12m, loan_share | EXISTS(loan), K(late_loan_clean_share), K(late_loan_returned_share), XCOUNT(loan) |
| pos_ext_late_fee_schedule | late_fee_flexline_record | P | line_active, line_late_12m, line_returns_12m, line_share | EXISTS(line), K(late_line_clean_share), K(late_line_returned_share), XCOUNT(line) |
| pos_ext_returned_item_fee | returned_item_level | P | returns_6m, late_fees_6m, late_fees_12m, item_fee_level | COUNT(pos_transactions), K(first_item_fee_usd), K(repeat_item_fee_usd), P(returned_payment_fee_usd) |
| pos_ext_returned_item_fee | one_penalty_limit_rule | M | paid_id, item_due, paid_date, credited_due, within_grace, same_due_late_id, same_due_late, one_event, penalty_offset, penalty_cap | F(monthly_payment_amount), LATEST(pos_transactions), P(late_fee_grace_days), SUM(pos_transactions), item_amount |
| pos_ext_returned_item_fee | returned_fee_balance_band | P | ledger_balance, balance_share | K(low_balance_limit_usd), K(low_balance_share), K(mid_balance_limit_usd), K(mid_balance_share), SUM(pos_transactions) |
| pos_ext_returned_item_fee | returned_fee_loan_record | P | loan_active, loan_late_12m, loan_returns_12m, loan_share | EXISTS(loan), K(loan_clean_share), K(loan_returned_share), XCOUNT(loan) |
| pos_ext_returned_item_fee | returned_fee_flexline_record | P | line_active, line_late_12m, line_returns_12m, line_share | EXISTS(line), K(line_clean_share), K(line_returned_share), XCOUNT(line) |
| pos_ext_payment_reset | reset_payment_method | M | di_billed_count, refund_count, method_choice | COUNT(pos_transactions), P(promo_type) |
| pos_ext_payment_reset | reset_loan_record | P | loan_active, loan_late_12m, loan_returns_12m, loan_cut | EXISTS(loan), K(reset_loan_clean_cut), K(reset_loan_returned_cut), XCOUNT(loan) |
| pos_ext_payment_reset | reset_flexline_record | P | line_active, line_late_12m, line_returns_12m, line_cut | EXISTS(line), K(reset_line_clean_cut), K(reset_line_returned_cut), XCOUNT(line) |
| pos_ext_payment_reset | reset_payment_record | P | late_fees_12m, record_cut | COUNT(pos_transactions), K(reset_clean_record_cut), K(reset_one_late_record_cut) |
| pos_ext_payment_reset | reset_autopay_record | P | autopay_debits, autopay_cut | COUNT(pos_transactions), K(reset_autopay_full_count), K(reset_autopay_full_cut), K(reset_autopay_partial_count), K(reset_autopay_partial_cut) |
| pos_ext_payment_reset | reset_paydown_band | P | principal_left, paydown_ratio, paydown_cut | F(financed_amount), K(reset_half_cut), K(reset_half_limit), K(reset_three_quarter_cut), K(reset_three_quarter_limit), SUM(pos_transactions) |

### Round 3 — probe table (decoys, absent records, ties, month-end, negative lags, zero amounts; scratch copies of the task worlds)
| policy | probe | value | verdict |
|---|---|---|---|
| LFR | gold world | 7.31 | ok |
| LFR | absent: no late fee on the plan | 0 | ok |
| LFR | fee already waived | 0 | ok |
| LFR | make-up not cleared (frozen 2026-10-15) | 0 | ok |
| LFR | outside 45-day window (frozen 2026-11-06) | 0 | ok |
| LFR | negative lag: make-up dated before the fee | 0 | ok |
| LFR | courtesy allowance used up (2 in 12 months) | 0 | ok |
| LFR | decoy older late fee (2026-07-21) - latest still read | 7.31 | ok |
| LFR | same-day tie: second late fee on 2026-09-21 recorded after the gold one | 7.31 | ok |
| LFR | month-end: return dated 2026-04-16 is exactly 6 whole months back (not within 6) | 1 | ok |
| RFR | gold world (after LFR) | 8.31 | ok |
| RFR | absent: no returned payment | 0 | ok |
| RFR | latest return not credited toward a due date (decoy extra payment returned 2026-10-07) | 0 | ok |
| RFR | R2-3 class: replacement-sized credit dated before the return | 0 | ok |
| RFR | return without fee entry | 0 | ok |
| PQ | gold world | 3919.28 | ok |
| LFS | gold world | 11.37 | ok |
| RIF | gold world | 9.58 | ok |
| RIF | late fee of the same due date waived -> capped tier | 20.95 | ok |
| RIF | payment dated after the grace period -> separate event, capped | 20.95 | ok |
| RIF | payment not credited toward a due date -> no limit | 20.95 | ok |
| RIF | one event with late fee above the product -> 0.00, nothing booked | 0.0 | ok |
| RIF | latest return R07 -> 0.00 | 0 | ok |
| RESET | gold world | 111.11 | ok |
| RESET | R2-11: purchase 2026-04-09, due day 20, next 2026-10-20 (first due 2026-05-20) | 19 | ok |
| RESET | due day = purchase day: purchase 2026-04-09, due day 9, next 2026-10-09 (first due 2026-05-09) | 19 | ok |
| RESET | short wrap: purchase 2026-01-28, due day 1, next 2026-10-01 (first due 2026-03-01) | 17 | ok |
| RESET | leap February: purchase 2028-02-05, due day 1, next 2028-09-01 (first due 2028-03-01, 25 days) | 18 | ok |
| RESET | non-leap February: purchase 2027-02-05, due day 1, next 2027-09-01 (first due 2027-04-01, 2027-03-01 is 24 days) | 19 | ok |
| RESET | first due in purchase month: purchase 2026-04-01, due day 28, next 2026-10-28 (first due 2026-04-28, 27 days) | 18 | ok |
| RESET | decoy: no deferred-interest billing entry -> activation method at the reset rate | 0 | ok |

### Round 3 — full gate block (final run, after the last edit)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK (6 tools)
- replay_tasks: REPLAY OK (0.json 17 acts, closure 94 = init; 1.json 17 acts, closure 106 = init; --check OK)
- check_solvability: SOLVABILITY OK (0.json 3 calls / 7 base gates / 19 seed rows; 1.json 3 / 4 / 23)
- check_compute: COMPUTE OK (16 factors per task; suite means branches 73.00, steps 17.00; history_rows_max 42; branches_max 74)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_traceability: NOT OK only for the unlock tool names before publication (0.json: relieve_late_fee_b1a4bf3c,
  relieve_returned_payment_fee_3fbe4785, pay_off_plan_f18fb847; 1.json: assess_late_fee_02ab9d3a,
  assess_returned_payment_fee_f9ef5ea0, reset_monthly_payment_233e8b10) — no other miss.
- check_cache_diff: INFO only (no cache trap designed).
- Scratch /tmp/practicepay_patient_financing_0067/ removed after this run.
REWORK round 3: gates 7/7 green

## Rework round 4 — audit revision_3 (R3-1 … R3-4 and the observations in their classes)
- R3-1 (waits must be satisfiable): the returned-payment fee waits on a late fee only when its payment was credited
  toward the plan's oldest unpaid due date (the only due date the late-fee schedule books); otherwise it waits on nothing
  and its one-penalty limit reads whatever late fee stands. Class sweep of every prerequisite sentence: payoff <- late-fee
  relief (the relief schedule writes on the latest late fee), payoff <- returned-fee relief (writes on the latest
  return's fee), reset <- returned-payment fee (writes on the latest return), returned-payment fee <- late fee (now scoped
  to the oldest unpaid due date); every condition is producible or vacuous (0.00 not owed) in every reachable world.
- R3-2 (one limit, two writes): the restated courtesy sentence gives a last remaining courtesy waiver to a make-up relief
  before a request and to the late-fee relief before the returned-payment-fee relief; the returned-fee schedule states and
  computes the reservation in its own words (latest late fee unwaived, made up after the fee, cleared, in window).
- R3-3 (fields the producing event writes): the make-up / replacement test reads the plan's next due date (oldest unpaid,
  written by the status refresh) and the latest payment entry toward the due date (installment_due_date is a payment
  field), a return being matched to the payment it names (related_txn_id); return rows no longer carry a due date in
  either world. Class sweep: every remaining read of pos_transactions uses fields its event type defines.
- R3-4 (real, fully amortizing method tiers): the reset's tiers are re-divide (no-interest), principal-and-interest
  (deferred interest billed or a provider refund; repays by the final due date, last payment absorbing the difference)
  and re-amortize (fall-through, the standard method); the activation-formula tier is gone. A past-due amount stays due as
  it stands and the reset applies from the due date after it (O3-5).
- Observations closed with their classes: half-cent rounding is stated "rounded half up" in every money rule and the
  computes implement it exactly (cents rounded to 6 places, then half up) — the seeded 23.275 fee is 23.28; the payoff's
  split adds back every payment entry of the latest payment date (O3-1); the payoff no longer claims the billed memo covers
  every earlier day (O3-2).
- XF recipe re-applied to every touched policy (RIF, reset, LFR, RFR, PQ, LFS rounding): sweep of basis / baseline /
  replaced_by / superseded / policy_source verbatim, transitive factor reads, no factor id in a tool name: 0 problems;
  each factor alone against the baseline still moves its result (both tasks); method tiers pairwise distinct on inputs
  (reset: no-interest / DI-billed-or-refunded / other); docstrings unchanged.
- Re-scored: task 0 7.31 / 8.31 / 3920.45 (payoff moved by the same-day add-back and the half-up fee); task 1 11.37 / 9.58 /
  123.81 at 24.49 (reset moved by R3-4 and O3-5). All proof text, traces and skip figures replayed from the round-4 state.

### Round 4 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| LFR/RFR | R3-2: 1-waiver plan, before any booking: late-fee relief / returned-fee relief owed | [7.31, 0] | ok |
| LFR/RFR | R3-2: 1-waiver plan, after the late-fee relief: returned-fee relief | 0 | ok |
| LFR | R3-3: make-up only 20.00, 2026-09-10 still the oldest unpaid due date | 0 | ok |
| RFR | R3-3: same world, returned-fee relief | 0 | ok |
| ALL | R3-3: no return row carries installment_due_date | 0 | ok |
| RIF | half cent: fee product 23.275 books 23.28 (seeded fee of 2026-10-06) | 23.28 | ok |
| PQ | same-day payments: both 2026-10-13 payments added back to the closing-to-payment span | 233.74 | ok |
| RIF | R3-1: latest return toward 2026-10-04 while 2026-09-04 is the oldest unpaid: fee set at once, limit reads the standing 10-04 late fee | [9.58, True] | ok |
| RIF | R3-1: same, no 2026-10-04 late fee on the ledger (none bookable): capped tier, no wait | [12.57, 155.52] | ok |
| RESET | R3-4: principal-and-interest payment repays the reset balance within the reset payments | [16, -63.25] | ok |
| RESET | R3-4: fall-through re-amortization repays exactly within the reset payments | [0, [18, -0.1]] | ok |
| RESET | O3-5: current plan (nothing past due) counts the next due date among the reset payments | 19 | ok |

### Round 4 — full gate block (final run)
- check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK (--check OK);
  check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK;
  check_traceability NOT OK only for the six unlock tool names (pre-publication).
REWORK round 4: gates 7/7 green

## Rework round 5 — audit revision_4 (R4-1, R4-2, T1-R4-1, T1-R4-2)
- R4-1 (priority yielding to a 0.00 write): the class is removed rather than patched — a make-up relief is now owed
  whatever the number of courtesy waivers already granted (it still counts among them, and a fee whose relief is owed is
  relieved rather than waived on request), so the two reliefs share no limit and no yield/awaiting condition remains in
  the charter. Sweep of every priority, yield or awaiting condition: none left (the reset, fee and payoff rules carry
  none; the returned-payment fee's wait on a late fee is a prerequisite, satisfiable as closed in round 4).
- R4-2 (method tiers must fit the remaining payments exactly): the reset's tiers are re-divide (no-interest plans),
  split payment (deferred interest billed: the billed deferred interest, capped at the reset balance, repaid in equal parts
  without further interest — the restated deferred-interest sentence excludes its unrepaid part from the interest base —
  plus the level payment on the rest) and re-amortize (fall-through, the standard method). Every tier repays the reset
  balance with exactly the reset payments, the last taking only the rounding difference (probed below); the
  provider-refund condition left the deferred-interest tier, refunded plans re-amortize.
- Task 1 (T1-R4-1/2): gold reset is the payment that fits his 18 remaining reset payments under his tier: 106.07 at
  24.49 (baseline 111.12); persona and request alignment ("paid off over the rest of the term") now match; traces, skip
  figure and rationale replayed. Task 0's solution unchanged (7.31 / 8.31 / 3920.45); its proof text no longer cites a
  courtesy count.
- XF recipe re-applied to the touched policies (LFR, RFR, reset): verbatim sweep, transitive factor reads, tool-name
  check 0 problems; every factor still moves its result alone against the baseline; method tiers pairwise distinct
  (no-interest / DI-billed / other) and all fully amortizing.

### Round 5 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| LFR/RFR | R4-1: 1-waiver plan, late fee 4.50 (keep-back gives 0.00), one return in 6 months | [0.0, 8.31] | ok |
| LFR/RFR | R4-1 class: 1-waiver plan, both booking orders | [[7.31, 8.31], [7.31, 8.31]] | ok |
| RESET | R4-2: split tier (DI billed) after the 18 reset payments: residue | [1, 106.07, -0.19] | ok |
| RESET | R4-2: re-amortize tier (no DI billing) residue | [0, 109.11, -0.1] | ok |
| RESET | R4-2: re-divide tier (no-interest) residue | [2, 90.55, -0.05] | ok |

### Round 5 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 5: gates 7/7 green

## Rework round 6 — audit revision_5 (R5-1, R5-2, T1-R5-1)
- R5-1 (coordinator decision applied): the plan's courtesy limit binds both make-up reliefs again and both count as
  courtesy waivers. The restated courtesy sentence states once that where only one waiver remains in the rolling 12
  months the late-fee relief takes it only if one above 0.00 is owed, and otherwise the returned-payment-fee relief takes
  it. Both schedules check it: the late-fee relief by the limit; the returned-payment-fee relief by the limit and, at the
  last waiver, by working out the late-fee relief owed on the latest late fee exactly as that schedule does (plain
  bindings, no factor reads another factor). Probed on a one-waiver plan in both booking orders (one end state) and the
  0.00 case.
- R5-2: the reset declares a scoped, self-naming overwrite of the payment-application sentence: on a reset plan, and only
  there, the reset schedule allocates each payment (its equal share of the deferred-interest part, interest billed since
  the reset, fees, balance); every other plan keeps the base order. Under that order task 1's 18 payments of 106.07 end
  at the rounding remainder (probe below). pos_evt_payments_and_fees added to the reset's base_policy_refs.
- Task 0 solution unchanged (7.31 / 8.31 / 3920.45); task 1 unchanged (11.37 / 9.58 / 106.07 at 24.49). Proof text
  (traces, tracing, order note, rationale) swept for the restored limit and the allocation order.
- XF recipe re-applied to LFR, RFR and the reset: verbatim / transitive-read / tool-name sweep 0 problems; factor
  sensitivities and baselines unchanged on both worlds; the new overwrite retires a clause that genuinely conflicted and
  names its scope.

### Round 6 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| LFR/RFR | R5-1: 1-waiver plan, late-fee relief owed above 0.00 - order LFR then RFR / RFR then LFR | [[7.31, 0], [7.31, 0]] | ok |
| LFR/RFR | R5-1 0.00 case: 1-waiver plan, late fee 4.50 (keep-back 0.00): late-fee relief / returned-fee relief / late-fee relief after | [0.0, 8.31, 0] | ok |
| LFR/RFR | R5-1: 1-waiver plan with its waiver already used in 12 months: both reliefs | [0, 0] | ok |
| RESET | R5-2: 18 reset payments allocated as the restated order says (DI share, interest since reset, fees, balance): residue | [-0.0, -0.19] | ok |

### Round 6 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 6: gates 7/7 green

## Rework round 7 — audit revision_6 (R6-1 and its class)
- Class: every policy that computes interest or a balance on a plan, against the reset's restated deferred-interest
  sentence (a reset plan's unrepaid deferred-interest part bears no interest).
  - Payoff: its interest-bearing balance now also leaves out, on a plan reset to a split payment, the reset's
    deferred-interest part not yet repaid — the deferred interest billed times the reset payments still due over the
    reset payments (the due dates after the billing through the final due date), a plan reset to a split payment being
    one whose deferred interest was billed and whose payment no longer equals its activation payment. Stated in the
    rule and the baseline; plain bindings only.
  - Reset: a plan whose deferred interest was billed is reset only once, only while no payment has posted since the
    billing and only before the first due date after it (otherwise no reset is made and payment and APR stay); its
    split-payment reset payments are the due dates after the billing, so the deferred-interest part is always the
    whole billed amount at the one reset and the part still unrepaid is record-derivable afterwards. A second reset
    is outside the schedule with its outcome stated.
  - Late fee, returned-payment fee and both reliefs read the ledger balance or principal only to choose a band, never
    to run interest; the deferred-interest part is part of the balance owed, so no treatment differs. No other policy
    runs interest.
- Task 1 world: the 50.00 partial payment is dated 2026-10-08 (before the billing) so the one-time reset is available;
  scored values unchanged (11.37 / 9.58 / 106.07 at 24.49); persona and traces swept. Task 0 unchanged (7.31 / 8.31 /
  3920.45; its plan carries no deferred-interest billing).
- XF recipe re-applied to the payoff and the reset: verbatim / transitive-read / tool-name sweep 0 problems; factor
  sensitivities and baselines unchanged on both worlds; every combination and order sentence kept.

### Round 7 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| PQ | R6-1: payoff on task 1 world right after the reset: interest base leaves out the unrepaid deferred-interest part | [1747.02, 1447.1, 267.32] | ok |
| PQ | R6-1: same plan one reset payment later (next due 2026-12-04, nothing past due): unrepaid part = 267.32 x 17/18 | 252.47 | ok |
| RESET | R6-1: second reset of the reset plan: not reset, payment and APR stay | [106.07, 24.49, True] | ok |
| RESET | first reset after a payment posted since the billing: not reset | [155.52, True] | ok |
| RESET | first reset after the first due date past the billing (2026-11-05): not reset | [155.52, True] | ok |
| PQ | payoff on task 1 world before any reset: no part left out | [1750.58, False] | ok |

### Round 7 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 7: gates 7/7 green

## Rework round 8 — audit revision_7 (R7-1 and observations O7-1, O7-2)
- R7-1: the reset-payment count on a past-due plan is now the due dates after the latest due date before today, every
  installment due before today staying in the amount past due (any number of them) and an installment due today counting
  among the reset payments; a current plan keeps the remaining payments from its next due date. One sentence, used by the
  re-divide and re-amortize tiers and the standard method (rule and baseline); the split tier keeps its count from the
  billing date. Probed on the auditor's two-past-due case and its neighbours (none, one, three past due; the due date
  itself; the day after).
- O7-1: a reset plan is recognised by its monthly payment differing from its activation payment or its plan APR
  differing from its plan's APR, and a reset that would leave both as they are makes no change and is not made — so the
  recognition cannot misfire (payoff and reset state the same test).
- O7-2: a refused reset, or one that would change nothing, works out to 0.00 and nothing is written; rule and compute agree.
- Scored values unchanged (task 0: 7.31 / 8.31 / 3920.45; task 1: 11.37 / 9.58 / 106.07 at 24.49); task 1 trace and
  rationale swept. XF recipe re-applied to the reset and the payoff: sweep 0 problems; sensitivities unchanged; every
  combination and order sentence kept.

### Round 8 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| RESET | R7-1: 48-month plan, 2026-09-10 and 2026-10-10 past due (233.74): reset payments = due dates after 2026-10-10 | [43, 106.91, -0.09] | ok |
| RESET | neighbour: one installment past due (2026-10-10) | [43, 110.31] | ok |
| RESET | neighbour: nothing past due, next due 2026-11-10 in the future | [43, 113.71, -0.15] | ok |
| RESET | neighbour: three installments past due (08-10, 09-10, 10-10) | [43, 103.51] | ok |
| RESET | O7-2: refused second reset works out to 0.00 (nothing written) | [0, True] | ok |
| PQ | O7-1: reset plan whose payment landed on the activation figure but APR changed is still recognised | [True, 267.32] | ok |
| RESET | neighbour: today is the 2026-10-10 due date, only 2026-09-10 past due: 10-10 is the first reset payment | [44, True] | ok |
| RESET | neighbour: day after the 2026-10-10 due date, both installments past due | [43, False] | ok |

### Round 8 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 8: gates 7/7 green

## Rework round 9 — renderer source scan render_r1 (D1–D6, each with its class)
- D1: the returned-fee relief no longer recomputes the late-fee relief (all lr_* bindings and the copied params removed).
  It waits on the late-fee relief in state form — "A returned-payment-fee relief is set only after the plan's ledger
  carries the late-fee relief owed on the plan's latest late fee, which takes a last remaining courtesy waiver first when
  it is above 0.00." (edge kind state_gate on its courtesy count) — and then reads only its own limit. The restated
  courtesy sentence keeps the priority. Task 0's tree gains that edge (fan-out plus the gate; same problems, same order).
- D2: the late-fee level's third tier is "a late fee dated within the last 12 months but none within the last 6 months",
  so the three tiers partition the record exactly; every other ladder re-checked for gaps/overlaps (none).
- D3/D6: the month-window convention now sits inside each factor sentence that uses it (loan/FlexLine/record factors of
  every policy, the payoff's four holds, the relief size and fee level ladders); the timing shares carry their own day-span
  convention; the one-penalty limit carries its own grace-period definition; the standalone convention sentences are gone
  except where a non-factor quantity uses them (the reliefs' courtesy count, the payoff's day span).
- D4: the reset's method factor owns each tier's interest-free part and payments; one generic sentence states how a way's
  interest-free part and the rest combine into the payment; no tier formula or split quantity sits outside the factor.
- D5: the split reset is barred by a payment dated on or after the billing date (rule and compute agree).
- Scored values unchanged (task 0: 7.31 / 8.31 / 3920.45; task 1: 11.37 / 9.58 / 106.07 at 24.49); factor
  sensitivities unchanged. XF recipe re-applied to all six policies: verbatim / transitive-read / tool-name sweep 0
  problems; every combination and order sentence kept.

### Round 9 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| LFR/RFR | D1: 1-waiver plan, prescribed order (late-fee relief decided first): late-fee relief / returned-fee relief | [7.31, 0] | ok |
| RFR | D1: 1-waiver plan, returned-fee relief before the late-fee relief is booked: its prerequisite state is unmet (late-fee relief 7.31 owed, no waiver names the late fee), so it may not be set yet | True | ok |
| LFR/RFR | D1 0.00 case: 1-waiver plan, late fee 4.50 (late-fee relief 0.00, nothing booked, prerequisite met vacuously): returned-fee relief takes the waiver | [0.0, 8.31] | ok |
| LFS | D2: latest late fee exactly 6 whole months back (2026-04-15 vs 2026-10-15) -> standard level | [27.0, 0, 1] | ok |
| LFS | D2: latest late fee exactly 12 whole months back (2025-10-15) -> first-time level | [20.0, 0] | ok |
| RESET | D5: a payment dated on the billing date bars the split reset (0.00, nothing written) | [0, True] | ok |

### Round 9 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 9: gates 7/7 green

## Rework round 10 — audit revision_9 (T0-R9-1)
- The returned-fee relief's wait on the late-fee relief now bears weight on task 0's world: its size method reads whether
  the late fee of the same missed payment already carries a waiver entry (capped when it does — the missed payment has been
  relieved once; keep-back when that late fee is unwaived or another late fee falls within 6 months; whole otherwise). The
  edge is value_input on that record test; skipping the late-fee relief moves the returned-fee relief to the keep-back size.
- Charter change limited to the returned-fee relief's size ladder, its two record bindings and the edge kind; the D1
  record-test design (no recomputation, no copied params), the courtesy priority and every D2–D6 closure are intact.
  XF recipe re-applied: verbatim / transitive-read / tool-name sweep 0 problems; tiers partition (waived / unwaived or
  other late fee in 6 months / none).
- Task 0 scored values unchanged (7.31 / 8.31 / 3920.45); skip figures replayed (returned-fee relief 12.66 without the
  late-fee relief; payoff 3923.46 without the late-fee relief, 3928.90 without the returned-fee relief); proof text,
  traces, closure and rationale swept. Task 1 untouched.

### Round 10 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| RFR | T0-R9-1: returned-fee relief on task 0 without the late-fee relief booked (keep-back tier) vs with it (capped tier) | [12.66, 8.31] | ok |
| LFR/RFR | D1 kept: 1-waiver plan, late-fee relief first then returned-fee relief | [7.31, 0] | ok |
| LFR/RFR | D1 kept: 1-waiver plan, late-fee relief 0.00 (nothing booked): returned-fee relief takes the waiver (late fee unwaived -> keep-back tier) | [0.0, 12.66] | ok |

### Round 10 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 10: gates 7/7 green

## Rework round 11 — audit revision_10 (R10-1 and its class)
- R10-1: the returned-fee relief's capped tier is now the keep-back figure but never more than the cap (capped keep-back),
  so at every fee the relieved tier gives no more than the unrelieved tier, which gives no more than the whole fee; the
  three tiers stay different shapes (capped keep-back / keep-back / whole) and differ above the crossover.
- Class sweep of every ladder for the same inversion: the late-fee relief size ladder had it (two returns gave the fee up
  to the cap, more than the one-return keep-back for fees up to the crossover) and is fixed the same way; all share,
  level, hold, cut and method ladders are monotone in the direction their rules state (checked tier by tier).
- Task 0 values unchanged (7.31 / 8.31 / 3920.45) and skip figures unchanged (12.66; 3923.46; 3928.90); traces swept.
  Task 1 untouched. D1–D6 closures intact. XF recipe re-applied: sweep 0 problems.

### Round 11 — probe table (auditor's fees and the crossover region)
| policy | probe | value | verdict |
|---|---|---|---|
| RFR | R10-1: fee 10.00: size relieved tier / unrelieved tier / whole | [5.0, 5.0, 10.0] | ok |
| RFR | R10-1: fee 15.00: size relieved tier / unrelieved tier / whole | [10.0, 10.0, 15.0] | ok |
| RFR | R10-1: fee 17.00: size relieved tier / unrelieved tier / whole | [12.0, 12.0, 17.0] | ok |
| RFR | R10-1: fee 17.01: size relieved tier / unrelieved tier / whole | [12.0, 12.01, 17.01] | ok |
| RFR | R10-1: fee 20.00: size relieved tier / unrelieved tier / whole | [12.0, 15.0, 20.0] | ok |
| RFR | R10-1: fee 23.28: size relieved tier / unrelieved tier / whole | [12.0, 18.28, 23.28] | ok |
| RFR | R10-1: fee 30.00: size relieved tier / unrelieved tier / whole | [12.0, 25.0, 30.0] | ok |
| LFR | R10-1 class: fee 8.00: size two returns / one return / whole | [3.0, 3.0, 8.0] | ok |
| LFR | R10-1 class: fee 12.00: size two returns / one return / whole | [7.0, 7.0, 12.0] | ok |
| LFR | R10-1 class: fee 15.00: size two returns / one return / whole | [10.0, 10.0, 15.0] | ok |
| LFR | R10-1 class: fee 15.01: size two returns / one return / whole | [10.0, 10.01, 15.01] | ok |
| LFR | R10-1 class: fee 18.62: size two returns / one return / whole | [10.0, 13.62, 18.62] | ok |
| LFR | R10-1 class: fee 27.00: size two returns / one return / whole | [10.0, 22.0, 27.0] | ok |

### Round 11 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 11: gates 7/7 green

## Rework round 12 — KB audit source items (S2, S3, S4; S1 unchanged by coordinator decision)
- S2: the payoff's dispute carve-out sentence now states that the amount left out is subtracted from the payoff amount
  only, the interest-bearing balance and its interest staying as they are (matching the compute). Class sweep of every
  deduction/base order: late fee (unpaid part net of open disputes, then cap), returned-payment fee (level, shares, one-
  penalty limit, cap at the returned amount), reliefs (size, shares, cap at the unwaived fee), reset (balance less past due,
  cuts from the APR, interest-free part then level payment) and payoff (fees owed and unrepaid deferred-interest part off
  the interest base, holds on the same base) — every order is stated in its rule.
- S3: the returned-payment fee's scope sentence now says only that a fee for a payment credited toward a due date that is
  not the oldest unpaid one waits on no late fee; the one-penalty factor's own sentence carries the late-fee reading.
- S4: the late-fee relief's restated courtesy sentence no longer states the priority; the priority sentence sits only in
  the returned-fee relief's rule (the waiting side), beside its prerequisite sentence. Compute unchanged.
- Scored values unchanged in both tasks; D1–D6 and R10-1 closures intact; XF sweep 0 problems; proof text swept.

### Round 12 — probe table
| policy | probe | value | verdict |
|---|---|---|---|
| PQ | S2: interest-bearing balance before the dispute deduction (gold) vs the reading that deducts it first | [3920.45, 3909.11, 3849.11] | ok |
| LFR/RFR | S4: priority stated only on the waiting side, compute unchanged: 1-waiver plan, late-fee relief then returned-fee relief | [7.31, 0] | ok |
| RIF | S3: one-penalty limit still reads the standing late fee of the same due date (task 1) | 9.58 | ok |

### Round 12 — full gate block (final run)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  TRACEABILITY NOT OK only for the six unlock tool names (pre-publication).
REWORK round 12: gates 7/7 green

## Rework round 13 — seed-only (cross-product re-judge X1–X4)
- X1: FlexLine returned-payment fee rows re-priced by the published FlexLine rules (percentage of the returned amount,
  history/tenure/shared-event/late-booking shares) in both tasks, and the replacement payments re-sized on that fee.
  Every FlexLine statement interest row was re-derived from the published rule (average daily balance of the cycle times
  the APR over 365 times the cycle days, draws accruing from the draw date), and each line's outstanding balance and
  draw-period minimum payment (3% of the balance, floor 35.00) re-derived from them.
- X2: personal-loan late fee rows re-priced with the first-late share (schedule C flat fee times the share) in both tasks;
  task 0's late installment payment and its fee-payment line re-sized on that fee (interest and principal portions
  unchanged).
- X3: task 1's late installment payment now pays the unpaid late fee from the payment (interest, then the fee as its own
  fee-payment line, then principal), and the courtesy waiver of an already-paid fee is removed.
- X4: task 1's scheduled loan payment is the level payment rounded to the cent; every installment row's interest and
  principal portions (daily simple interest actual/365 from the paid-through date), the returned payment's mirrored
  portions and the loan's principal balance were re-derived.
- Own PracticePay rows re-checked against the charter on their dates (both tasks' fees reproduce exactly).
- pos.extended.yaml and task_tools.py byte-identical (2920d0573e23e7b7 / a2765a87783af6f2); no pos tier, scored value,
  skip figure or edge moved; the only proof-text change is the task 1 loan-ledger read objective.
- Full gate block (final run): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check OK); SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK; TRACEABILITY OK.
REWORK round 13: gates 7/7 green
