# worklog — env_0066_captive_auto_finance_company / retail_payment_servicing (M=2)

## Draw
task 0: prerequisite_problems 3, factor_counts [6,4,4,4]; task 1: prerequisite_problems 2, factor_counts [4,6,6].

## Claim analysis (why these seven problems)
Claimed events: retail_payment, retail_payment_returned, retail_returned_payment_fee, retail_late_charge, retail_fee_waiver,
retail_fee_payment, retail_due_date_change, retail_extension, retail_schedule_updated, retail_payment_restriction_updated.
Tier-computable amounts exist only on late charges, the extension fee and payments: a waiver is always of the whole fee, a
due-date change carries only day numbers/dates (the DSL cannot build a date), a returned payment can only be booked from the
bank's return (no in-call evidence), the fee payment is a trigger of a payment. So the seven problems are three late-charge
situations (re-opened by a returned payment / left unpaid past grace / paid after grace), the extension grant (fee), and three
payments with distinct purposes and owners (agent arrears payment; customer's good-faith payment; customer's catch-up payment).
Signing the extension agreement carries no amount; in task 0 it is already completed before the call (x_signed holds).

| task | problems (root first) | user tool |
|---|---|---|
| 0 | retail_ext_extension_grant <- returned_installment_late_charge, arrears_payment, good_faith_payment | submit_extension_good_faith_payment_c7575c9b |
| 1 | retail_ext_catch_up_payment <- unpaid_installment_late_charge, late_posted_installment_late_charge | submit_catch_up_payment_af77047e |

## compute_basis verbatim sweep (scratch sweep.py; check_extended does not check quotes)
    retail_ext_returned_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_arrears_payment basis-miss [] unbased [] factor-cross []
    retail_ext_good_faith_payment basis-miss [] unbased [] factor-cross []
    retail_ext_extension_grant basis-miss [] unbased [] factor-cross []
    retail_ext_unpaid_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_late_posted_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_catch_up_payment basis-miss [] unbased [] factor-cross []
All compute_basis quotes, baseline sentences, prerequisite sentences and replaced_by sentences are verbatim in their own rule.

## Factor independence (transitive reads of each factor's bindings; scratch sweep.py)
Every factor reads only evidence bindings and parameters; no factor reads another factor's binding. Method transforms
(re-opened relief, graduated charge, mail-float relief) decide a mode from evidence only; the transform is applied in a plain
binding to the rate-figured charge that the baseline defines, in the order each rule's single assembly sentence fixes
(rate adjustments combined first, then the change of method, then the cap, then deductions/additions).
      turned_installment_late_charge         lrf_tenure_rate            reads-plain=[]
      turned_installment_late_charge         lrf_first_return_relief    reads-plain=[]
      turned_installment_late_charge         lrf_lessee_deduction       reads-plain=[]
      turned_installment_late_charge         lrf_lapsed_grace           reads-plain=[]
      rears_payment                          cuf_arrears_share          reads-plain=[]
      rears_payment                          cuf_lessee_share           reads-plain=[]
      rears_payment                          cuf_exposure               reads-plain=[]
      rears_payment                          cuf_fee_carry              reads-plain=[]
      od_faith_payment                       gff_delinquency_risk       reads-plain=[]
      od_faith_payment                       gff_lessee_points          reads-plain=[]
      od_faith_payment                       gff_tenure_points          reads-plain=[]
      od_faith_payment                       gff_first_hardship         reads-plain=[]
      od_faith_payment                       gff_early_life             reads-plain=[]
      od_faith_payment                       gff_overdue_interest       reads-plain=[]
      tension_grant                          xf_fee_method              reads-plain=[]
      tension_grant                          xf_history_reduction       reads-plain=[]
      tension_grant                          xf_lessee_reduction        reads-plain=[]
      tension_grant                          xf_first_extension         reads-plain=[]
      paid_installment_late_charge           ucf_unpaid_rate            reads-plain=[]
      paid_installment_late_charge           ucf_lessee_points          reads-plain=[]
      paid_installment_late_charge           ucf_partial_effort         reads-plain=[]
      paid_installment_late_charge           ucf_clean_schedule         reads-plain=[]
      paid_installment_late_charge           ucf_care_plan              reads-plain=[]
      paid_installment_late_charge           ucf_graduated              reads-plain=[]
      te_posted_installment_late_charge      lpf_posted_rate            reads-plain=[]
      te_posted_installment_late_charge      lpf_lessee_points          reads-plain=[]
      te_posted_installment_late_charge      lpf_care_holder            reads-plain=[]
      te_posted_installment_late_charge      lpf_unchanged_terms        reads-plain=[]
      te_posted_installment_late_charge      lpf_seasoned               reads-plain=[]
      te_posted_installment_late_charge      lpf_mail_float             reads-plain=[]
      tch_up_payment                         cpf_fee_settlement         reads-plain=[]
      tch_up_payment                         cpf_repeat_pull            reads-plain=[]
      tch_up_payment                         cpf_lease_pull             reads-plain=[]
      tch_up_payment                         cpf_overdue_interest       reads-plain=[]

## Method tier pairwise table (one distinguishing input per pair)
| factor | tier A | tier B | fall-through | input -> A / B / fall |
|---|---|---|---|---|
| lrf_first_return_relief | halve, floor $ | x3/4, floor $ | to the cent | figure 19.38 -> 9 / 14 / 19.38 |
| cuf_fee_carry | whole fees_due | fees_due up to 30.00 | none | fees 40.00 -> 40.00 / 30.00 / 0 |
| gff_overdue_interest | days beyond 30 | half of days beyond grace, floor | none | 40 days -> 10 / 15 / 0 |
| xf_fee_method | halve, floor $ | x3/4, floor $ | as is | 35 -> 17 / 26 / 35 |
| ucf_graduated | halve, floor $ | x3/4, floor $ | to the cent | 11.82 -> 5 / 8 / 11.82 |
| lpf_mail_float | halve, floor $ | x3/4, floor $ | to the cent | 8.98 -> 4 / 6 / 8.98 |
| cpf_fee_settlement | whole fees_due | up to 30.00 | none | fees 40.00 -> 40 / 30 / 0 |
| cpf_overdue_interest | every day beyond grace | one day | none | 7 days -> 7 / 1 / 0 |

## Edge probes (scratch copies, b/probes.py; gold T0 LR 4.00 CU 545.83 GF 454.49 X 4.00; T1 LC 5.00 LP 4.00 PAY 1056.10)
    P1 closed 2nd lease w/ 2 lease late charges (T0) {'LR': 7.0, 'CU': 610.44, 'GF': 519.1, 'X': 9.0}
    P2 earlier returned payment 2025-01-10 (T0) {'LR': 14.38, 'CU': 545.83, 'GF': 454.49}
    P3 financed Care cancelled + active cash Care (T1) {'LC': 6.0, 'LP': 5.0}
    P4 lease late charge 2026-09-01 (T1) {'LC': 6.0, 'LP': 5.0, 'PAY': 1125.18}
    P5 extra 400.00 payment on 2026-08-28 (T0) {'X': 4.0}
    P5 extra 400.00 payment on 2026-08-29 (T0) {'X': 4.0}
    P6a no lease at all (T0) {'LR': 7.0, 'CU': 610.44, 'GF': 519.1, 'X': 9.0}
    P6b no Care plan (T1) {'LC': 7.0, 'LP': 6.0}
    gold T0 {'LR': 4.0, 'CU': 545.83, 'GF': 454.49, 'X': 4.0} gold T1 {'LC': 5.0, 'LP': 4.0, 'PAY': 1056.1}
Readings: P1 a closed second lease's late charges count (rules read "the customer's Kestrel lease ledger", all leases);
P2 an earlier return removes first-return relief (rule: "the only returned payment ever recorded"); P3 a cancelled financed
Care plan is not "active" -> second tier; P4 a lease late charge within 3 months moves the pull-ahead to 20%; P5 a payment on
2026-08-28 is outside the recent window (posted after the same day of the previous month means 2026-08-29 on), here both are
above the top tier; P6 absent lease / Care plan fall through to zero points. Absent-record cases: no returned payment ->
the re-opened late-charge policy is out of scope by its first sentence; no lease -> lessee tiers fall through; no Care plan ->
Care tiers fall through; no recent payments -> full extension fee; no recent late charge -> no fee settlement. No CFIELD/first-
match read remains (Care plan via EXISTS with the account filter; lease pull via XCOUNT). No division by a record value.

## Gate outputs (final, full difficulty)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    CACHE-DIFF INFO (optional; no correctness gate)
    SCOPE OK
    TRACEABILITY NOT OK
Traceability misses are only the unlock tool_name provenance (KB not yet rendered); no other id/value miss.

## Files
- retail.extended.yaml (base verbatim + 7 extended_policies), task_tools.py (7 tools), tasks/0.json, tasks/1.json, worklog.md
ROUND 1: gates 8/8 green

## REWORK round 2 closure (audit: audits/policy_task/retail_payment_servicing/, round 1)
| item | change |
|---|---|
| CG-1 (a) / task 1 F1 | retail_ext_late_posted_installment_late_charge declares a second overwrite of retail_late_charges, superseded clause "No late charge is assessed when the unpaid portion is less than late_charge_min_unpaid_amount, on an installment deferred by an extension, or on an installment that was paid in full within the grace period."; replaced_by measures the minimum at grace end for its own scope only, keeps the deferred-installment exclusion, and restates the whole base sentence for every other installment, naming the unpaid and re-opened cases. The rule sentence that re-anchored the portion is now this declared sentence plus "Since no payment reached the installment within its grace period, the portion that stood when the grace period ended is one full monthly_payment." |
| CG-1 class sweep | Late-charge policies vs every base retail_late_charges sentence: status/grace/counting/one-per-installment followed by all three; amount sentence overwritten by all three (tails name the siblings); exclusion sentence: overwritten only by LPC (restated for the others); measure "as of the assessment date": ULC uses the lesser of past_due_amount and one monthly_payment (as of the last nightly cycle, no payment posts between cycle and assessment), RLC uses the reversed amount (the base returned-payment rule restores it). (b) O-13: RLC now states that a re-opened installment is not one paid in full within grace. |
| CG-2 | Sentences narrowed to the next-due installment in all members: EXT<-RLC ("the installment it defers, when a returned payment re-opened it ..."), GFP<-RLC, ARR<-RLC (also "an installment" -> the next-due installment), CUP<-ULC; conditions rewritten to the same scope; prerequisite_closure fields re-copied from the charter. CUP<-LPC already singular. |
| task 1 F2 + seed sweep | T1 lease: next_due 2026-11-20, 18 made incl. signing + 18 remaining = 36, signing and funding rows, balance = funding - 18 x 285.67. T0 lease: 30 + 6 = 36, signing/funding rows and the 2024-05..2025-05 payments added (2025-05-27 payment posted late 2025-06-09 under the 2025-06-07 late charge), balance = funding - 30 x 274.36 (runs to the residual). T1 Care: care_limit_established row (38350.00 <= 40000.00 Platinum cap) + find_care_transactions read (writes now steps 9/11/13). T1 customer_since = first account date. T0 interest_paid_to_date = last posting date. Lease, Care, pre-owned and balloon rows added to seed_consistency. Retail rows re-checked (next_due vs payments_made / dpd / past_due / last_payment_date) - consistent. |
| O-1 (payment tools never apply the payment) | ARR, GFP and CUP each declare an overwrite of retail_payment_posting "Each payment is applied in payment_allocation_order: ..." with a self-naming replaced_by (recorded on posting day; the nightly posting cycle applies it in payment_allocation_order, same order restated); each tail names the two sibling payment cases; payment-tool docstrings state the split is applied by the nightly cycle, not by the call; "carries/settles fees" reworded to "includes an amount equal to" the fees. |
| O-2 | EXT<-ARR sentence names the channel ("a payment through the agent-assisted phone ACH channel"). |
| O-3 | effect texts of ARR<-RLC, GFP<-RLC, EXT<-ARR, EXT<-GFP made general. |
| O-4 | kept: EXT<-RLC is a state_gate on the ledger field; its ground is the base sentence "no late charge is assessed on a deferred installment" (stated in the edge effect). |
| O-5 | gff_early_life replaced by gff_long_term (contract length contract_date -> maturity_date >= 60 months: Tier 4/5 +7, other +2.5); no longer the same dimension as tenure and no longer cancels. |
| O-6 | kept: halve+floor vs x3/4+floor vs cent are different computation paths (pairwise table below). |
| O-7 | kept (accepted as company schedule by the auditor). |
| O-8 | kept: retail_reinstatement_and_redemption is in lineage because its subject includes retail_payment (gate requirement); it sets no gate (policy_scope). |
| O-9 | ARR subtracts one monthly_payment per installment the most recent completed signed extension agreement defers (LATEST retail_requests.requested_installments). |
| O-10 | LPC scope excludes an installment a returned payment re-opened. |
| O-11 | kept (no factor reads the splits). O-12: no change (EXT carries its own action-form sentence). |
| task 0 minor 1-5 | step numbers 10/12/14 in prerequisite_closure; order_uniqueness read lists corrected; REVISIONS (r1) wording corrected; persona "Last week"; O-1/O-5 as above. |
| task 1 observations | seed_consistency no longer claims an unrecorded receipt time; persona line without "first". |

### Re-run: compute_basis verbatim sweep (scratch sweep.py)
    retail_ext_returned_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_arrears_payment basis-miss [] unbased [] factor-cross []
    retail_ext_good_faith_payment basis-miss [] unbased [] factor-cross []
    retail_ext_extension_grant basis-miss [] unbased [] factor-cross []
    retail_ext_unpaid_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_late_posted_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_catch_up_payment basis-miss [] unbased [] factor-cross []

### Re-run: factor independence (transitive non-factor reads per factor; factor-cross [] everywhere)
      returned_installment_late_charge         lrf_tenure_rate            reads-nonfactor=[]
      returned_installment_late_charge         lrf_first_return_relief    reads-nonfactor=[]
      returned_installment_late_charge         lrf_lessee_deduction       reads-nonfactor=[]
      returned_installment_late_charge         lrf_lapsed_grace           reads-nonfactor=[]
      arrears_payment                          cuf_arrears_share          reads-nonfactor=[]
      arrears_payment                          cuf_lessee_share           reads-nonfactor=[]
      arrears_payment                          cuf_exposure               reads-nonfactor=[]
      arrears_payment                          cuf_fee_carry              reads-nonfactor=[]
      good_faith_payment                       gff_delinquency_risk       reads-nonfactor=[]
      good_faith_payment                       gff_lessee_points          reads-nonfactor=[]
      good_faith_payment                       gff_tenure_points          reads-nonfactor=[]
      good_faith_payment                       gff_first_hardship         reads-nonfactor=[]
      good_faith_payment                       gff_long_term              reads-nonfactor=[]
      good_faith_payment                       gff_overdue_interest       reads-nonfactor=[]
      extension_grant                          xf_fee_method              reads-nonfactor=[]
      extension_grant                          xf_history_reduction       reads-nonfactor=[]
      extension_grant                          xf_lessee_reduction        reads-nonfactor=[]
      extension_grant                          xf_first_extension         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_unpaid_rate            reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_lessee_points          reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_partial_effort         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_clean_schedule         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_care_plan              reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_graduated              reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_posted_rate            reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_lessee_points          reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_care_holder            reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_unchanged_terms        reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_seasoned               reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_mail_float             reads-nonfactor=[]
      catch_up_payment                         cpf_fee_settlement         reads-nonfactor=[]
      catch_up_payment                         cpf_repeat_pull            reads-nonfactor=[]
      catch_up_payment                         cpf_lease_pull             reads-nonfactor=[]
      catch_up_payment                         cpf_overdue_interest       reads-nonfactor=[]

### Re-run: method tier pairwise table
| factor | tier A | tier B | fall-through | input -> A / B / fall |
|---|---|---|---|---|
| lrf_first_return_relief | halve, floor $ | x3/4, floor $ | to the cent | 19.38 -> 9 / 14 / 19.38 |
| cuf_fee_carry | includes whole fees_due | includes fees up to 30.00 | nothing | fees 40.00 -> 40 / 30 / 0 |
| gff_overdue_interest | days beyond 30 | half of days beyond grace, floor | none | 40 days -> 10 / 15 / 0 |
| xf_fee_method | halve, floor $ | x3/4, floor $ | as is | 35 -> 17 / 26 / 35 |
| ucf_graduated | halve, floor $ | x3/4, floor $ | to the cent | 11.82 -> 5 / 8 / 11.82 |
| lpf_mail_float | halve, floor $ | x3/4, floor $ | to the cent | 8.98 -> 4 / 6 / 8.98 |
| cpf_fee_settlement | includes whole fees_due | includes up to 30.00 | nothing | fees 40.00 -> 40 / 30 / 0 |
| cpf_overdue_interest | every day beyond grace | one day | none | 7 days -> 7 / 1 / 0 |
Factor counts after rework: RLC 4 (3P/1M), ARR 4 (3P/1M), GFP 6 (5P/1M), EXT 4 (3P/1M), ULC 6 (5P/1M), LPC 6 (5P/1M), CUP 4 (2P/2M).

### Re-run: decoy / absent-record probes (scratch probes.py, writes held at gold arguments)
    gold T0 {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    gold T1 {'unpaid_installment_late_charge': 5.0, 'late_posted_installment_late_charge': 4.0, 'catch_up_payment': 1056.1}
    P1 closed 2nd lease, 2 lease late charges in 12m (T0) {'returned_installment_late_charge': 7.0, 'arrears_payment': 610.44, 'good_faith_payment': 532.02, 'extension_grant': 9.0}
    P2 earlier returned payment 2025-01-10 (T0) {'returned_installment_late_charge': 14.38, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P3a later EXPIRED agreement for 2 installments (T0) {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P3b older COMPLETED agreement for 2 installments (T0) {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P4 no lease at all (T0) {'returned_installment_late_charge': 7.0, 'arrears_payment': 610.44, 'good_faith_payment': 532.02, 'extension_grant': 9.0}
    P5 financed Care cancelled + active cash Care listed later (T1) {'unpaid_installment_late_charge': 6.0, 'late_posted_installment_late_charge': 5.0, 'catch_up_payment': 1056.1}
    P6 lease late charge 2026-09-01 inside 3 months (T1) {'unpaid_installment_late_charge': 6.0, 'late_posted_installment_late_charge': 5.0, 'catch_up_payment': 1125.18}
    P7 no Care plan (T1) {'unpaid_installment_late_charge': 7.0, 'late_posted_installment_late_charge': 6.0, 'catch_up_payment': 1056.1}
Readings: P1/P4 lessee tiers read the whole customer lease ledger and an active lease (rule text); P2 an earlier return removes first-return relief; P3a an expired agreement is ignored, P3b an older completed agreement is not the most recent one (LATEST by created_at over completed agreements); P5 a cancelled financed plan is not active -> second tier (EXISTS with the account filter, no first-match); P6 a lease late charge within 3 months -> 20%; P7 no Care plan -> fall-through. No CFIELD first-match read remains.

### Gate outputs (REWORK round 2, full difficulty)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    CACHE-DIFF INFO (optional; no correctness gate)
    SCOPE OK
    TRACEABILITY NOT OK
Traceability: only unlock tool_name provenance misses (KB not yet rendered); 0 other misses. CACHE-DIFF is informational.
REWORK round 2: gates 8/8 green

## REWORK round 3 closure (audit revision_2 + audits/render_source/XF_recipe.md)
| item | change |
|---|---|
| CG-3 (charter) | retail_ext_returned_installment_late_charge: the re-opened amount is now the unpaid portion, as of the assessment date, of the installment the next due date shows (past_due_amount less one monthly_payment for each whole monthly_payment in the past_due_amount less one cent), not the dishonoured payment's whole amount; the rule states the minimum-unpaid and deferred exclusions on that amount. |
| CG-3 class sweep | retail_ext_unpaid_installment_late_charge uses the same as-of-assessment measure (replacing "the lesser of past_due_amount and one monthly_payment", which mis-measured a partly paid oldest installment followed by a later one) and states the minimum-unpaid and deferred exclusions itself instead of deferring to the base sentence the late-posted policy retires for its own scope. The late-posted policy's declared exception (portion at grace end) is the only other measure; its replaced_by tail for re-opened and unpaid installments now reads the same as both rules. Probes P5/P6/P10 below. |
| leftover (task 0) | arrears factor_trace says the late charge is booked at step 10. |
| leftover (task 1) | design_rationale base-invariant card no longer attributes a receipt time to the 2026-09-16 posting. |
| O-14 | decoy-probed (P3a expired later agreement, P3b older completed agreement): the most recent completed agreement is read; tie rule stated in the rule. |
| O-4, O-6, O-7, O-8, O-11, O-12 | kept as observations (reasons in round-2 closure). |
| proof text | tracing for both late charges and both factor_traces restate the new measure arithmetic; good-faith tracing wording "for this extension"; rationale section 12 added to both tasks. |

### XF recipe: per-policy x per-point check (after the round-3 edits)
| point | RLC | ARR | GFP | EXT | ULC | LPC | CUP |
|---|---|---|---|---|---|---|---|
| 1 assembly sentence generic | fixed ("any amount a schedule below deducts") | fixed ("any amount a schedule below includes") | fixed ("any amount a schedule below adds"; cover rounding moved to its factor sentence) | ok | ok | ok | fixed ("every other amount a schedule below adds"; interest rounding moved to its factor sentence + own binding) |
| 2 non-commuting order fixed | rate -> method -> cap -> deductions | share combined -> applied -> addition | points combined -> applied -> addition | method -> reductions | rates combined -> method -> cap | rates combined -> method -> cap | percentages combined -> applied -> additions |
| 3 independence (transitive) | ok (sweep) | ok | ok | ok | ok | ok | ok |
| 4 ownership | cap/amount baseline; lag in its factor | other past due baseline; deferred count baseline | per diem in its factor | recent payments in its factor | recent payments, days beyond grace in factors | mailed-check count in its factor | per diem, days beyond grace in its factor |
| 5 basis verbatim | ok | ok | ok | ok | ok | ok | ok |
| 6 ties | stated (returns on same date share it) | stated (same creation time: first recorded) | no latest/earliest read | none | none | none | none |
| 7 counting conventions | months + days stated | months stated | months + days stated | months stated | months + days stated | months stated | months + days stated |
| 8 branches / scope | out-of-scope tail "not figured under this policy"; zero/negative lag -> no deduction | applies only with a completed agreement (stated) | absent lease -> 0 points | no recent payment -> fee as is | absent lease/Care -> 0 | absent mailed check -> to the cent | no recent late charge -> nothing for fees |
| 9 base clauses | amount clause overwritten; exclusion stated in own rule | allocation overwritten (siblings named) | allocation + good-faith clause overwritten | fee clause overwritten | amount clause overwritten; exclusion stated in own rule | amount + exclusion clauses overwritten, tails restate | allocation overwritten (siblings named) |
| 10 rounding | re-opened amount, rate figure, result RND = rule | share amount, result | pct amount, cover, result | result | portion, rate figure, result | rate figure, result | pull amount, interest carried, result |
| 11 tools | ok | docstring "on the past-due installments" (was "toward") | docstring "for an extension" (was "toward") | arg text "for this extension" | ok | ok | ok |
| 12 proof text | tracing/trace updated | trace step 10 | ok | ok | tracing/trace updated | ok | ok |

### Re-run: compute_basis verbatim sweep
    retail_ext_returned_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_arrears_payment basis-miss [] unbased [] factor-cross []
    retail_ext_good_faith_payment basis-miss [] unbased [] factor-cross []
    retail_ext_extension_grant basis-miss [] unbased [] factor-cross []
    retail_ext_unpaid_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_late_posted_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_catch_up_payment basis-miss [] unbased [] factor-cross []

### Re-run: factor independence (transitive; factor-cross [] for every policy)
      returned_installment_late_charge         lrf_tenure_rate            reads-nonfactor=[]
      returned_installment_late_charge         lrf_first_return_relief    reads-nonfactor=[]
      returned_installment_late_charge         lrf_lessee_deduction       reads-nonfactor=[]
      returned_installment_late_charge         lrf_lapsed_grace           reads-nonfactor=[]
      arrears_payment                          cuf_arrears_share          reads-nonfactor=[]
      arrears_payment                          cuf_lessee_share           reads-nonfactor=[]
      arrears_payment                          cuf_exposure               reads-nonfactor=[]
      arrears_payment                          cuf_fee_carry              reads-nonfactor=[]
      good_faith_payment                       gff_delinquency_risk       reads-nonfactor=[]
      good_faith_payment                       gff_lessee_points          reads-nonfactor=[]
      good_faith_payment                       gff_tenure_points          reads-nonfactor=[]
      good_faith_payment                       gff_first_hardship         reads-nonfactor=[]
      good_faith_payment                       gff_long_term              reads-nonfactor=[]
      good_faith_payment                       gff_overdue_interest       reads-nonfactor=[]
      extension_grant                          xf_fee_method              reads-nonfactor=[]
      extension_grant                          xf_history_reduction       reads-nonfactor=[]
      extension_grant                          xf_lessee_reduction        reads-nonfactor=[]
      extension_grant                          xf_first_extension         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_unpaid_rate            reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_lessee_points          reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_partial_effort         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_clean_schedule         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_care_plan              reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_graduated              reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_posted_rate            reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_lessee_points          reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_care_holder            reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_unchanged_terms        reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_seasoned               reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_mail_float             reads-nonfactor=[]
      catch_up_payment                         cpf_fee_settlement         reads-nonfactor=[]
      catch_up_payment                         cpf_repeat_pull            reads-nonfactor=[]
      catch_up_payment                         cpf_lease_pull             reads-nonfactor=[]
      catch_up_payment                         cpf_overdue_interest       reads-nonfactor=[]

### Re-run: method tier pairwise table (unchanged ladders)
| factor | input -> tier A / tier B / fall-through |
|---|---|
| lrf_first_return_relief | 19.38 -> 9 / 14 / 19.38 |
| cuf_fee_carry | fees 40.00 -> 40 / 30 / 0 |
| gff_overdue_interest | 40 days -> 10 / 15 / 0 |
| xf_fee_method | 35 -> 17 / 26 / 35 |
| ucf_graduated | 11.82 -> 5 / 8 / 11.82 |
| lpf_mail_float | 8.98 -> 4 / 6 / 8.98 |
| cpf_fee_settlement | fees 40.00 -> 40 / 30 / 0 |
| cpf_overdue_interest | 7 days -> 7 / 1 / 0 |

### Re-run: decoy / absent-record / CG-3 probes (writes held at gold arguments)
    gold T0 {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    gold T1 {'unpaid_installment_late_charge': 5.0, 'late_posted_installment_late_charge': 4.0, 'catch_up_payment': 1056.1}
    P1 closed 2nd lease, 2 lease late charges in 12m (T0) {'returned_installment_late_charge': 7.0, 'arrears_payment': 610.44, 'good_faith_payment': 532.02, 'extension_grant': 9.0}
    P2 earlier returned payment 2025-01-10 (T0) {'returned_installment_late_charge': 14.38, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P3a later EXPIRED agreement for 2 installments (T0) {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P3b older COMPLETED agreement for 2 installments (T0) {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P4 no lease at all (T0) {'returned_installment_late_charge': 7.0, 'arrears_payment': 610.44, 'good_faith_payment': 532.02, 'extension_grant': 9.0}
    P5 CG-3: re-opened portion 6.04 + one later installment (T0) re-opened amount 6.04
    P6 oldest partly paid (300.00 unpaid) + one later installment (T0) re-opened amount 300.0
    P7 financed Care cancelled + active cash Care (T1) {'unpaid_installment_late_charge': 6.0, 'late_posted_installment_late_charge': 5.0, 'catch_up_payment': 1056.1}
    P8 lease late charge 2026-09-01 inside 3 months (T1) {'unpaid_installment_late_charge': 6.0, 'late_posted_installment_late_charge': 5.0, 'catch_up_payment': 1125.18}
    P9 no Care plan (T1) {'unpaid_installment_late_charge': 7.0, 'late_posted_installment_late_charge': 6.0, 'catch_up_payment': 1056.1}
    P10 two whole installments past due (T1) unpaid portion 690.82
P5: a re-opened installment of which only 6.04 had been paid by the dishonoured payment measures 6.04 -> below the 10.00 minimum, no late charge (same answer under the late-posted policy's tail). P6/P10: the measure isolates the oldest installment when later installments are past due.

### Gate outputs (REWORK round 3, full difficulty)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    CACHE-DIFF INFO (optional; no correctness gate)
    SCOPE OK
    TRACEABILITY NOT OK
Traceability: only unlock tool_name provenance misses (KB not yet rendered); 0 other misses. CACHE-DIFF is informational.
REWORK round 3: gates 8/8 green

## REWORK round 4 closure (audit revision_3)
| item | change |
|---|---|
| CG-4 (3) ARR | The standard method now defines the arrears share: "The arrears share is standard_share_pct percent, and the arrears payment amount is the arrears share of the other past-due amount, rounded to the cent." (new param standard_share_pct, in baseline.params). cuf_arrears_share replaces it (fall-through = standard_share_pct); cuf_lessee_share deducts from it and cuf_exposure adds to it, both against the baseline-defined share. The combination sentence is generic and fixes the order: "any replacement of the arrears share comes first, then every addition to it or deduction from it, giving one share that is applied once to the other past-due amount and rounded to the cent". |
| CG-4 (6) CUP | The standard method now defines the pull-ahead share: "The pull-ahead share is standard_pull_pct percent, and the catch-up amount is the contract's past_due_amount plus the pull-ahead share of one monthly_payment, rounded to the cent." (standard_pull_pct = 0, in baseline.params and in compute). cpf_repeat_pull and cpf_lease_pull each add points to the pull-ahead share; "a further ..." wording removed, so neither is stated relative to the other. Combination: "every addition to the pull-ahead share is first combined with it into one share, which is applied once to one monthly_payment and rounded to the cent". |
| CG-4 class check | Every other factor contributes against a baseline-defined quantity: RLC (rate vs late_charge_pct; method on the rate figure; deductions from the charge), GFP (points vs extension_good_faith_pct; cover added to the good-faith amount), EXT (method on extension_fee; reductions from the fee), ULC/LPC (rate points vs late_charge_pct; method on the rate figure), ARR fee carry and CUP fee/interest added to the baseline amount. |
| CG-5 (1-3) RLC, ULC, LPC ovw 1 | replaced_by tails (and rule) now restate the base content for out-of-scope charges: "any other late charge is late_charge_pct_of_unpaid_installment percent of retail_msr_unpaid_installment_portion, capped at the lower of late_charge_company_max and the contract's recorded late_charge_max_amount, and is not figured under this policy." Sibling cases still named. |
| CG-5 (4-6) ARR, GFP ovw 2, CUP | tails restate the base allocation for every other payment: "every other payment is applied in payment_allocation_order when it posts, first to simple interest accrued over retail_msr_interest_accrual_days at the contract apr on a per_diem_day_basis-day year, then to principal until retail_msr_installments_due is satisfied, then to fees due, and any remainder to principal, and is not posted under this policy." |
| CG-5 class check | All 9 overwrites listed: none defers to "the base rule"; EXT fee and GFP good-faith overwrites have no out-of-scope remainder (auditor agrees); LPC ovw 2 already restated. No rule sentence defers to a retired clause (the remaining "as the base ... rule states them" references name only unretired clauses: grace, status, one-per-installment, extension gates, payable status/cutoff). |
| CG-4 withdrawn members 1, 2, 4, 5 | unchanged (generic "any amount a schedule below ..." sentences kept, per auditor). |
| O-15 | kept as observation (day-count convention sentence is a convention, not a quantity). O-4, O-6, O-7, O-8, O-11, O-12, O-14 kept. |
| proof text | task 0 arrears tracing wording ("standard 100% replaced by 85%"); rationale section 13 in both tasks. No scored value changed (all sensitivities and baselines identical on recompute). |

### XF recipe per-policy x per-point (round 4)
| point | RLC | ARR | GFP | EXT | ULC | LPC | CUP |
|---|---|---|---|---|---|---|---|
| 1 assembly generic | ok | fixed (share defined by baseline; generic order) | ok | ok | ok | ok | fixed (pull-ahead share defined by baseline; generic) |
| 2 order | ok | replacement -> additions/deductions -> apply+round -> add | ok | ok | ok | ok | additions combined with share -> apply+round -> add |
| 3 independence | ok | ok | ok | ok | ok | ok | ok |
| 4 ownership | ok | share in baseline | ok | ok | ok | ok | pull-ahead share in baseline |
| 5 quotes | ok | ok | ok | ok | ok | ok | ok |
| 6 ties | ok | ok | n/a | n/a | n/a | n/a | n/a |
| 7 counting | ok | ok | ok | ok | ok | ok | ok |
| 8 branches | ok | ok | ok | ok | ok | ok | ok |
| 9 base clauses | fixed (tail restates) | fixed | fixed (ovw 2) | ok | fixed | fixed (ovw 1) | fixed |
| 10 rounding | ok | ok | ok | ok | ok | ok | ok |
| 11 tools | ok | ok | ok | ok | ok | ok | ok |
| 12 proof text | ok | updated | ok | ok | ok | ok | ok |

### Re-run: compute_basis verbatim sweep
    retail_ext_returned_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_arrears_payment basis-miss [] unbased [] factor-cross []
    retail_ext_good_faith_payment basis-miss [] unbased [] factor-cross []
    retail_ext_extension_grant basis-miss [] unbased [] factor-cross []
    retail_ext_unpaid_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_late_posted_installment_late_charge basis-miss [] unbased [] factor-cross []
    retail_ext_catch_up_payment basis-miss [] unbased [] factor-cross []

### Re-run: factor independence (transitive; factor-cross [] everywhere)
      returned_installment_late_charge         lrf_tenure_rate            reads-nonfactor=[]
      returned_installment_late_charge         lrf_first_return_relief    reads-nonfactor=[]
      returned_installment_late_charge         lrf_lessee_deduction       reads-nonfactor=[]
      returned_installment_late_charge         lrf_lapsed_grace           reads-nonfactor=[]
      arrears_payment                          cuf_arrears_share          reads-nonfactor=[]
      arrears_payment                          cuf_lessee_share           reads-nonfactor=[]
      arrears_payment                          cuf_exposure               reads-nonfactor=[]
      arrears_payment                          cuf_fee_carry              reads-nonfactor=[]
      good_faith_payment                       gff_delinquency_risk       reads-nonfactor=[]
      good_faith_payment                       gff_lessee_points          reads-nonfactor=[]
      good_faith_payment                       gff_tenure_points          reads-nonfactor=[]
      good_faith_payment                       gff_first_hardship         reads-nonfactor=[]
      good_faith_payment                       gff_long_term              reads-nonfactor=[]
      good_faith_payment                       gff_overdue_interest       reads-nonfactor=[]
      extension_grant                          xf_fee_method              reads-nonfactor=[]
      extension_grant                          xf_history_reduction       reads-nonfactor=[]
      extension_grant                          xf_lessee_reduction        reads-nonfactor=[]
      extension_grant                          xf_first_extension         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_unpaid_rate            reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_lessee_points          reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_partial_effort         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_clean_schedule         reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_care_plan              reads-nonfactor=[]
      unpaid_installment_late_charge           ucf_graduated              reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_posted_rate            reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_lessee_points          reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_care_holder            reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_unchanged_terms        reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_seasoned               reads-nonfactor=[]
      late_posted_installment_late_charge      lpf_mail_float             reads-nonfactor=[]
      catch_up_payment                         cpf_fee_settlement         reads-nonfactor=[]
      catch_up_payment                         cpf_repeat_pull            reads-nonfactor=[]
      catch_up_payment                         cpf_lease_pull             reads-nonfactor=[]
      catch_up_payment                         cpf_overdue_interest       reads-nonfactor=[]

### Re-run: method tier pairwise table (ladders unchanged)
lrf_first_return_relief 19.38 -> 9/14/19.38; cuf_fee_carry fees 40 -> 40/30/0; gff_overdue_interest 40 days -> 10/15/0; xf_fee_method 35 -> 17/26/35; ucf_graduated 11.82 -> 5/8/11.82; lpf_mail_float 8.98 -> 4/6/8.98; cpf_fee_settlement fees 40 -> 40/30/0; cpf_overdue_interest 7 days -> 7/1/0.

### Re-run: decoy / absent-record probes (writes held at gold arguments)
    gold T0 {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    gold T1 {'unpaid_installment_late_charge': 5.0, 'late_posted_installment_late_charge': 4.0, 'catch_up_payment': 1056.1}
    P1 closed 2nd lease, 2 lease late charges in 12m (T0) {'returned_installment_late_charge': 7.0, 'arrears_payment': 610.44, 'good_faith_payment': 532.02, 'extension_grant': 9.0}
    P2 older completed agreement for 2 installments (T0) {'returned_installment_late_charge': 4.0, 'arrears_payment': 545.83, 'good_faith_payment': 467.41, 'extension_grant': 4.0}
    P3 no lease (T0) {'returned_installment_late_charge': 7.0, 'arrears_payment': 610.44, 'good_faith_payment': 532.02, 'extension_grant': 9.0}
    P4 lease late charge inside 3 months (T1) {'unpaid_installment_late_charge': 6.0, 'late_posted_installment_late_charge': 5.0, 'catch_up_payment': 1125.18}
    P5 no lease (T1) {'unpaid_installment_late_charge': 6.0, 'late_posted_installment_late_charge': 5.0, 'catch_up_payment': 987.02}
    P6 financed Care cancelled (T1) {'unpaid_installment_late_charge': 7.0, 'late_posted_installment_late_charge': 6.0, 'catch_up_payment': 1056.1}

### Gate outputs (REWORK round 4, full difficulty)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    CACHE-DIFF INFO (optional; no correctness gate)
    SCOPE OK
    TRACEABILITY NOT OK
Traceability: only unlock tool_name provenance misses (KB not yet rendered); 0 other misses. CACHE-DIFF is informational.
REWORK round 4: gates 8/8 green

## REWORK round 5 closure (KB audit audits/policy_kb/retail_payment_servicing + render_source notes)
| item | change |
|---|---|
| SRC-1 | post_arrears_payment_6321a7ae, submit_extension_good_faith_payment_c7575c9b, submit_catch_up_payment_af77047e now post on the posting day of the base posting rule: a class helper (_PostingDay, pure ordinal-day arithmetic) converts the call time to Central Time; received earlier than 20:00 CT on a business day -> today, otherwise the next business day, skipping Saturdays, Sundays and US federal holidays (fixed-date holidays observed Fri/Mon when on a weekend). txn_date and last_payment_date take that day; docstrings state it ("posting day"). Class closed: these are the only tools that post payments; late-charge and extension tools book entries dated today, which their rules state. |
| SRC-2 | retail_ext_good_faith_payment overwrite replaced_by restores the clause's in-force ordering ("before the extension is granted, a good-faith payment of at least that amount must still have posted since the most recent installment due date") and keeps the 0.00 branch; retail_ext_extension_grant's action-form sentence now reads "... wherever the good-faith amount for the extension is above 0.00" and its condition matches, so the 0.00 branch and the prerequisite agree. Task 0 prerequisite_closure re-copied. |
| N-4 | task 1 find_care_transactions objective/necessity no longer claim a ledger check no rule makes. |
| renderer note 1 / XF pt 4 | placement only (per_diem / interest bindings); not changed (auditor: no KB defect, not routed). |
| N-3 | base payoff wording (outside this difficulty's extended tree; blueprint frozen) - no change. |
| proof text | rationale sections 14 (both tasks); X edge sentence quoted in task 0 rationale updated. No scored value moved (COMPUTE OK on the unchanged expected values). |

### XF recipe per-policy x per-point (round 5)
All points as in round 4; changes this round: pt 9 GFP (good-faith overwrite restates the ordering part; 0.00 branch agrees with EXT's sentence), pt 8 EXT (0.00 good-faith branch stated in the prerequisite sentence), pt 11 tools (payment docstrings state the posting day the body computes). Every other cell unchanged (ok).

### Re-run: compute_basis verbatim sweep and factor independence
    retail_ext_returned_installment_late_charge basis-miss [] factor-cross []
    retail_ext_arrears_payment basis-miss [] factor-cross []
    retail_ext_good_faith_payment basis-miss [] factor-cross []
    retail_ext_extension_grant basis-miss [] factor-cross []
    retail_ext_unpaid_installment_late_charge basis-miss [] factor-cross []
    retail_ext_late_posted_installment_late_charge basis-miss [] factor-cross []
    retail_ext_catch_up_payment basis-miss [] factor-cross []
Method tier pairwise table and decoy/absent-record probes: compute and ladders unchanged since round 4 (table and probe results in the round 4 section stand; recompute identical, COMPUTE OK).

### Posting-day probe (tool helper)
    2026-09-28 10:20:00 EDT -> 2026-09-28
    2026-10-22 10:20:00 EDT -> 2026-10-22
    2026-10-22 20:59:00 EDT -> 2026-10-22
    2026-10-22 21:00:00 EDT -> 2026-10-23
    2026-10-24 09:00:00 EDT -> 2026-10-26
    2026-11-25 23:30:00 EST -> 2026-11-27
    2026-07-03 12:00:00 EDT -> 2026-07-06
    2026-10-12 09:00:00 EDT -> 2026-10-13
    2026-12-24 22:30:00 CST -> 2026-12-28

### Gate outputs (REWORK round 5, full difficulty)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    CACHE-DIFF INFO (optional; no correctness gate)
    SCOPE OK
    TRACEABILITY OK
Traceability is now OK (docs published). Note for the coordinator: the GFP/EXT rule sentences and the three payment-tool docstrings changed this round, so docs/retail needs a re-render of those hubs.
REWORK round 5: gates 9/9 green
