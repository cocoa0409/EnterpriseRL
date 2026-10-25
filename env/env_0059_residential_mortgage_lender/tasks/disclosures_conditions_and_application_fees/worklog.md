# Worklog — disclosures_conditions_and_application_fees (env_0059, category loan), M=2

Per-task dossiers (design thesis, problem-tree / factor / base-invariant / business-object cards, verification) live in tasks/0.json and tasks/1.json design_rationale.

## Draw (draw_counts.py --tasks 2)
{"task": 0, "key": "env_0059_residential_mortgage_lender/disclosures_conditions_and_application_fees/0", "prerequisite_problems": 1, "problems": 2, "factor_counts": [5, 4]}
{"task": 1, "key": "env_0059_residential_mortgage_lender/disclosures_conditions_and_application_fees/1", "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 6, 5, 5]}

## Scope
- task 0: loan_ext_credit_report_repull_fee (user tool authorize_credit_report_repull_408eaf54) -> root loan_ext_corrected_cd_nonrecurring_costs (issue_corrected_closing_disclosure_de3eb1f4); gold 48.26 / 7338.61
- task 1: loan_ext_application_fee_due (user tool pay_application_fee_6c3f9eab) -> loan_ext_revised_le_zero_tolerance (issue_revised_loan_estimate_22df4f86) -> loan_ext_zero_tolerance_cure (assess_tolerance_cure_d5e015cb) -> root loan_ext_closing_disclosure_lender_credit (issue_closing_disclosure_6debf4ff); gold 105.10 / 2703.00 / 150.00 / 2525.10

## Revision log
- task 0 replay: dangling FK loan_files.preapproval_id='' -> set None; 5 unread rows (lock_requests, appraisal_fee_ledger) -> added find_lock_requests (documents the 2026-10-09 changed circumstance) and find_appraisal_fee_ledger (no update charge booked yet) reads; steps shifted 8/13 -> 9/15.
- task 0 solvability: intent_source.kind on_request -> user_scenario.
- task 0 seed: bank statement document date 2026-06-30 -> 2026-07-14 (would have aged past 120 days on the moved closing date and reopened the condition).
- task 1 replay: 11 unread rows (conditions, credit ledger) -> added find_loan_conditions and find_credit_ledger reads; steps shifted 9/16/18/20 -> 11/18/20/22.
- task 1 solvability: Closing Disclosure is state_due -> intent_source initial_state (status clear_to_close, closing 2026-10-22) with structured discriminator value.

## Final gate run (no --task)
### check_extended
🔎 EXTENDED gate  (category=loan, extended_policies=6, cross-cat=6, task_tools=6, tasks=2, no_handoff=True)
EXTENDED OK
### check_task_tools
🔎 TASK-TOOL-CONTRACT gate  (6 tools)
TASK TOOL CONTRACT OK
### replay_tasks
🔎 REPLAY gate  (2 tasks)
task                         acts  det  nonvac errs  clos  init  match
0.json                         16 True    True    0    29    29   True
1.json                         23 True    True    0    30    30   True
REPLAY OK
### check_solvability
🔎 SOLVABILITY gate  (2 tasks, category=loan)
   identity preamble: find_customers -> verify_customer_identity (K=2, log=identity_verifications)
task         verify calls base gates  seed rows   ok
0.json         True     2          2         17 True
1.json         True     4          6         16 True

SOLVABILITY OK
### check_compute
🔎 COMPUTE gate  (2 tasks, 6 extended_policies, 6 cross-category)
task                         comps fact xfac hist brch step  match
0.json                           2    9    3    6   29   16   True
1.json                           4   22   13   10   80   23   True

suite means:  branches=54.50(>= 4.0)   steps=19.50(>= 4.0)
suite depth:  history_rows_max=10(>= 8)   branches_max=80(>= 5)

COMPUTE OK
### check_grounding
🔎 GROUNDING & DISCLOSURE gate  (2 tasks)
task           idAttrsUsed  answers  writes  cond    ok
0.json                   2        2       2    11  True
1.json                   2        4       4     8  True

GROUNDING OK
### check_traceability
task        copied  missing    ok
0.json          20        2 False
1.json          33        4 False

  [FAIL]
   - 0.json: 'authorize_credit_report_repull_408eaf54' (unlock_user_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / frozen_time / prior tool returns). It enters the 
   - 0.json: 'issue_corrected_closing_disclosure_de3eb1f4' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / frozen_time / prior tool returns). It enters
   - 1.json: 'pay_application_fee_6c3f9eab' (unlock_user_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / frozen_time / prior tool returns). It enters the row id via 
   - 1.json: 'issue_revised_loan_estimate_22df4f86' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / frozen_time / prior tool returns). It enters the ro
   - 1.json: 'assess_tolerance_cure_d5e015cb' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / frozen_time / prior tool returns). It enters the row id v
   - 1.json: 'issue_closing_disclosure_6debf4ff' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / frozen_time / prior tool returns). It enters the row i
TRACEABILITY NOT OK
### check_cache_diff
🔎 CACHE-DIFF diagnostic  (2 tasks)  holding=loan_files  quantity_fields=['prepaid_fee_balance', 'tolerance_cure_balance']
task                        reconciled QF (field: seeded vs true)  recheck info
0.json                              prepaid_fee_balance:634.8≠0.0    False    -
1.json       prepaid_fee_balance:92.4≠0.0; prepaid_fee_balance:92    False    -

  [INFO]
   ~ 0.json: history computation has no explicit cache re-check reaction (optional; add one only when the scenario intentionally uses this trap)
   ~ 1.json: cache tolerance_cure_balance=0.0 equals event-stream total 0.0 for account tolerance_cure (no stale-cache trap was selected)
   ~ 1.json: history computation has no explicit cache re-check reaction (optional; add one only when the scenario intentionally uses this trap)

CACHE-DIFF INFO (optional; no correctness gate)
### check_cross_fire
🔎 SCOPE gate  (2 tasks, policies=6, hard-fails=0)
SCOPE OK

## Round 2 (policy-task audit rework)
- F-1 cure: measured increase defined as signed latest-minus-initial; baseline floors only that; compute_basis quotes the definition; result floored once.
- F-2 corrected CD: closing_package_redraw dropped (reschedule_fee 0 = fall-through).
- F-4a corrected CD: report_line_source dropped (estimate tier negated the prerequisite); credit_report_line is a plain read and the edge gate; new factors closing_service_line (method, funding) and title_bringdown now method; repull gains inquiry_supplement; draw split repull 5 / corrected CD 4. T0 values 60.76 / 7376.11.
- F-3 class: fee prerequisite sentences scoped 'wherever the program the file is in charges an application fee'; conditions accept program fee 0.00; fee rule books a 0.00 collection when discounts zero a charging program's fee.
- F-4b,c: fee fall-throughs now live for programs charging no application fee.
- CD open_cure_credit middle tier -> open post_closing_refund cures (balance tier could only contradict entries).
- TRID same-day LE+CD: Closing Disclosure dated the next business day when a Loan Estimate was issued that day; tool takes issued_date; T1 CD dated 2026-10-16.
- O-3 cure condition widened to the sentence's scope; O-5 cure cites loan_changed_circumstance with a declared overwrite.
- Chain RED: T1 prerequisite_closure skip / wrong-order figures recomputed by code (skip fee: LE 3047.90, CD 2420.00, recomputed cure 150.00; skip LE: cure 476.90; skip cure: CD 2375.10; LE before fee: cure 494.90, CD 2870.00).
- Both design_rationale texts rewritten; proof fields recomputed with the charter compute.

## Round 2 final gate run
### check_extended
🔎 EXTENDED gate  (category=loan, extended_policies=6, cross-cat=6, task_tools=6, tasks=2, no_handoff=True)
EXTENDED OK
### check_task_tools
🔎 TASK-TOOL-CONTRACT gate  (6 tools)
TASK TOOL CONTRACT OK
### replay_tasks
🔎 REPLAY gate  (2 tasks)
task                         acts  det  nonvac errs  clos  init  match
0.json                         16 True    True    0    32    32   True
1.json                         23 True    True    0    30    30   True
REPLAY OK
### check_solvability
🔎 SOLVABILITY gate  (2 tasks, category=loan)
   identity preamble: find_customers -> verify_customer_identity (K=2, log=identity_verifications)
task         verify calls base gates  seed rows   ok
0.json         True     2          2         19 True
1.json         True     4          6         16 True

SOLVABILITY OK
### check_compute
🔎 COMPUTE gate  (2 tasks, 6 extended_policies, 6 cross-category)
task                         comps fact xfac hist brch step  match
0.json                           2    9    3    6   31   16   True
1.json                           4   22   13   10   80   23   True

suite means:  branches=55.50(>= 4.0)   steps=19.50(>= 4.0)
suite depth:  history_rows_max=10(>= 8)   branches_max=80(>= 5)

COMPUTE OK
### check_grounding
🔎 GROUNDING & DISCLOSURE gate  (2 tasks)
task           idAttrsUsed  answers  writes  cond    ok
0.json                   2        2       2    12  True
1.json                   2        4       4     8  True

GROUNDING OK
### check_traceability
1.json          33        4 False

  [FAIL]
   - 0.json: 'authorize_credit_report_repull_408eaf54' (unlock_user_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator 
   - 0.json: 'issue_corrected_closing_disclosure_de3eb1f4' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simul
   - 1.json: 'pay_application_fee_6c3f9eab' (unlock_user_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue / 
   - 1.json: 'issue_revised_loan_estimate_22df4f86' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator di
   - 1.json: 'assess_tolerance_cure_d5e015cb' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialogue
   - 1.json: 'issue_closing_disclosure_6debf4ff' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source in the agent-reachable context (published KB / visible tool schemas / simulator dialo
TRACEABILITY NOT OK
### check_cache_diff
task                        reconciled QF (field: seeded vs true)  recheck info
0.json                              prepaid_fee_balance:634.8≠0.0    False    -
1.json       prepaid_fee_balance:92.4≠0.0; prepaid_fee_balance:92    False    -

  [INFO]
   ~ 0.json: history computation has no explicit cache re-check reaction (optional; add one only when the scenario intentionally uses this trap)
   ~ 1.json: cache tolerance_cure_balance=0.0 equals event-stream total 0.0 for account tolerance_cure (no stale-cache trap was selected)
   ~ 1.json: history computation has no explicit cache re-check reaction (optional; add one only when the scenario intentionally uses this trap)

CACHE-DIFF INFO (optional; no correctness gate)
### check_cross_fire
🔎 SCOPE gate  (2 tasks, policies=6, hard-fails=0)
SCOPE OK

## Round 3 (revision_2 audit)
- N-1: revised-LE fee line and cure add-back detect a collection by entry COUNT (0.00 collection = collection); add-back tier 1 covers collection = program fee.
- N-2: closing service tier 2 = Mobile Notary on a weekday or RON on any day (matches compute).
- O-11: credit report line folded into corrected-CD baseline paragraph (baseline = all-factor-baseline 6903.11).
- Class sweep: repull bundle tier 3 covers single-borrower file; fee offset tier 1 takes booked amount even if 0.00; returning tiers drop 'only'; corrected-CD tool enum example removed (matched gold); verbatim basis/overwrite/baseline/policy_source check passes for all 6 policies.
- No scored value changed.
### gates
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
TRACEABILITY OK
SCOPE OK

## Round 4 (policy revision_3 + render_loan_r1)
- N-3 closing service partition by opening date (later than CD issue date / on or before / none scheduled); O-13 guard.
- N-4 repull 0.00 charge stated in rule; tool contract accepts 0.00.
- Render 1-3 scoped replaced_by with still-in-force parts; 5 desktop appraisal overlap; 4,6,7,8 closed in round 3; 9 BLUEPRINT-KNOWN.
- O-9 returning tiers read latest funding wire (XLATEST); T1 seed + read find_funding_wires; steps 12/19/21/23.
- Class: count-based tiers for revised LE / cure entry conditions; cure books no entry at 0; CD tool accepts 0.00; no scored value changed.
### gates
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
TRACEABILITY OK
  [INFO]
CACHE-DIFF INFO (optional; no correctness gate)
SCOPE OK

## Round 5 (render_loan_r2)
- Item 1 first-match class: CD lock (locked), closing (scheduled), credit line (ledger standing balance + reserved estimate); fee/LE/cure pre-approval by file preapproval_id, Heroes credit by file, appraisal by standard order id (LE/cure, fee-ledger lines scoped to it) and delivered standard order (corrected CD); lock-extension wording 'any rate lock of the customer'.
- Item 2 stale funding note fixed; item 3 BLUEPRINT-KNOWN.
- No scored value changed.
### gates
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
TRACEABILITY OK
CACHE-DIFF INFO (optional; no correctness gate)
SCOPE OK

## Round 6 (policy revision_5, N-5) — enumerated record reads (every CFIELD / CPARAM / LATEST / MAX / X* read in the six policies)
| # | policy | read | selection now | rule wording | probe (decoy stored first) |
|---|---|---|---|---|---|
| 1 | repull | MAX/COUNT/SUM on this file's fee ledger; COUNT issued credit_inquiry_explanation conditions | aggregates over this file | "on the file" | n/a (aggregate) |
| 2 | repull | XSUM lock_pricing_events (all the customer's extensions) | aggregate | "the customer's rate lock extensions" | n/a (aggregate, rule says all) |
| 3 | corrected CD | latest CD nonrecurring / issue date | CD with the highest disclosure_sequence (MAX then filter) | "the latest Closing Disclosure ... (the one with the highest disclosure sequence)" | same-date lower-sequence CD -> 7376.11 OK |
| 4 | corrected CD | SUM credit report charges < 1 month | aggregate | as stated | n/a |
| 5 | corrected CD | appraisal inspection_date / validity / max_age / fees | status=delivered AND order_reason=standard_order (unique per base) | "the file's standard appraisal order ... in delivered status" | cancelled standard order -> 7376.11 OK |
| 6 | corrected CD | title commitment age | LATEST document_date keyed on document_date (value = max) | "the most recent document date among the cleared title commitment conditions" | older-document, later-resolved title -> OK |
| 7 | corrected CD | VVOE age | LATEST resolved_date keyed on resolved_date | "the most recent resolved date among the cleared VVOE conditions" | earlier VVOE -> OK |
| 8 | corrected CD | closing method / opened / signing date / fees | status=scheduled (one per file per base) | "the file's closing in scheduled status" | cancelled RON closing -> OK |
| 9 | fee, revised LE, cure | pre-approval level | preapproval_id = file's preapproval_id | "the pre-approval the file was converted from" | second pre-approval -> OK |
| 10 | fee, revised LE, cure | Hometown Heroes status / occupation | loan_file_id + variant + status=verified | "the Hometown Heroes Credit reserved against the file ... verified" | expired firefighter credit -> 105.10 / 2703.00 / 150.00 OK |
| 11 | fee | ITP / LE delivery counts; recent credit report SUMs | aggregates | as stated | n/a |
| 12 | fee, CD | returning tier | XLATEST funding_wires wire_date (max) | "the most recent funding wire Larkspur sent on any closing of the customer" | older wire -> OK |
| 13 | revised LE, cure | standard appraisal order id (base fee, rush flag, rush fee, its fee-ledger charges) | standard_order in any non-cancelled status (OR-chain of the seven live statuses; at most one per base) | "the order placed on the file with order reason standard_order that is not cancelled" | cancelled standard order with its own acreage surcharge -> OK |
| 14 | revised LE, cure | XSUM/XCOUNT lock extensions / relocks in window | aggregate | "any rate lock of the customer" | n/a |
| 15 | revised LE, cure | application fee collections/refunds | COUNT/SUM this file | as stated | n/a |
| 16 | cure | latest LE total | LE with the highest disclosure_sequence | "the latest Loan Estimate ..., the one with the highest disclosure sequence" | same-date lower-sequence LE -> 150.00 OK |
| 17 | cure, CD | initial LE total / lender credit | event_type=loan_le_issued (one per file) | "the initial Loan Estimate" | n/a (unique) |
| 18 | CD | lock state / points / amount | status=locked (one per file) | "the file's rate lock in locked status" | cancelled lock at -1.000 -> 2525.10 OK |
| 19 | CD | digital closing credit | status=scheduled | "the file's closing in scheduled status" | cancelled RON closing -> OK |
| 20 | CD | standing credit balance | XSUM credit_ledger awards+payouts-applied-reduced-forfeited (customer) | "the customer's closing cost credits" (O-14) | n/a (aggregate) |
| 21 | CD | reserved estimate | sum over the seven programs of fixed_credit_amount with status=reserved (one per program per file) | "the fixed_credit_amount of every program reserved against the file ... added up" | Heroes+First Home reserved, expired grant -> 5025.10 (1000+2500) OK |
| 22 | CD | open cures | SUM assessed - paid by cure method | aggregate | n/a |
- No scored value changed. Gates: all OK (TRACEABILITY 0 misses).

## Round 7 (policy revision_6, N-6) — absent-record cases, probed on scratch copies of each world
Aggregate reads (SUM/COUNT/MAX/XSUM/XCOUNT) give 0 on an absent record and their rules already state 'nothing'; all DAYS() date differences are now guarded by the presence of both dates; the only divisions (/100 lock points, /1000 title rate) have constant divisors.
| task | policy | absent record | rule tier | probe result | expected | ok |
|---|---|---|---|---|---|---|
| 0 | corrected_cd_nonrecurring_costs | no primary appraisal order in delivered status | appraisal line adds nothing | 7201.11 | 7201.11 | OK |
| 0 | corrected_cd_nonrecurring_costs | delivered order is transferred_in | primary order read: reinspection 175.00 | 7376.11 | 7376.11 | OK |
| 0 | corrected_cd_nonrecurring_costs | no cleared title commitment | title line adds nothing | 7301.11 | 7301.11 | OK |
| 0 | corrected_cd_nonrecurring_costs | no cleared VVOE yet | re-verification adds nothing | 7328.11 | 7328.11 | OK |
| 0 | corrected_cd_nonrecurring_costs | no closing in scheduled status | closing service adds nothing | 7201.11 | 7201.11 | OK |
| 0 | corrected_cd_nonrecurring_costs | no Closing Disclosure on the file | carried-forward 0.00, closing service nothing | 358.76 | 358.76 | OK |
| 0 | corrected_cd_nonrecurring_costs | no scheduled closing date on the file | age lines add nothing | 7078.11 | 7078.11 | OK |
| 0 | credit_report_repull_fee | no scheduled closing date | no delivery fee | 55.76 | 55.76 | OK |
| 0 | credit_report_repull_fee | no lock extension entries | whole charge | 121.52 | 121.52 | OK |
| 0 | credit_report_repull_fee | no earlier credit report charge | program price, individual reports | 109.9 | 109.9 | OK |
| 0 | credit_report_repull_fee | no credit inquiry condition | no supplement | 48.26 | 48.26 | OK |
| 1 | application_fee_due | file converted from no pre-approval | rate 1.0 | 217.6 | 217.6 | OK |
| 1 | application_fee_due | no Hometown Heroes Credit | no discount | 155.1 | 155.1 | OK |
| 1 | application_fee_due | no funding wire | no returning discount | 155.1 | 155.1 | OK |
| 1 | application_fee_due | no e-sign intent record | no e-disclosure discount | 145.1 | 145.1 | OK |
| 1 | application_fee_due | no credit report charge | no offset | 197.5 | 197.5 | OK |
| 1 | revised_le_zero_tolerance | no live primary appraisal order | no appraisal base fee, surcharge or rush | 1753.0 | 1753.0 | OK |
| 1 | revised_le_zero_tolerance | live order is transferred_in | primary order read | 2703.0 | 2703.0 | OK |
| 1 | revised_le_zero_tolerance | no lock extension entries | extension line nothing | 2335.0 | 2335.0 | OK |
| 1 | revised_le_zero_tolerance | no pre-approval | no underwriting relief | 3003.0 | 3003.0 | OK |
| 1 | revised_le_zero_tolerance | no Heroes credit | no processing relief | 2903.0 | 2903.0 | OK |
| 1 | zero_tolerance_cure | no live primary appraisal order | rush nothing taken out | 300.0 | 300.0 | OK |
| 1 | zero_tolerance_cure | no initial Loan Estimate row | initial total counts 0.00 | 3029.9 | 3029.9 | OK |
| 1 | zero_tolerance_cure | no lock extension entries | nothing taken out | 518.0 | 518.0 | OK |
| 1 | closing_disclosure_lender_credit | no rate lock in locked status | initial LE credit stays | 1973.1 | 1973.1 | OK |
| 1 | closing_disclosure_lender_credit | no closing in scheduled status | digital credit nothing | 2375.1 | 2375.1 | OK |
| 1 | closing_disclosure_lender_credit | no scheduled closing date | notice credit nothing | 2425.1 | 2425.1 | OK |
| 1 | closing_disclosure_lender_credit | no closing cost credit at all | credit line nothing | 1525.1 | 1525.1 | OK |
| 1 | closing_disclosure_lender_credit | no funding wire | returning credit nothing | 2425.1 | 2425.1 | OK |
| 1 | closing_disclosure_lender_credit | no lock and no initial Loan Estimate | LE credit 0.00 | 1605.1 | 1605.1 | OK |
- No scored value changed. Gates: all OK (TRACEABILITY 0 misses).

## Round 8 (render_loan_r3, kb_audit_notes_r1)
- r3#1 corrected-CD age lines name 'no scheduled closing date' (nothing added).
- r3#2 delivered_order -> appraisal_recertification; cure standard_order -> rush_rebaseline; revised-LE standard_order stays unowned (read by fee_sheet baseline plus two factors; a binding belongs to at most one factor).
- kb#3 CD: short-notice and returning credits counted from the preparation day, stated. kb#6: revised-LE/cure extension and relock lines net lock_cost_waived entries in the period (floor 0); repull counts waived extensions by recorded days. kb#4/#5: no source change (wording already 'verified occupation'; report type's reinspection_fee read from tariff).
- probes: waiver full/partial/over (LE 2335/2603/2335, cure 518/250), repull with waiver 60.76, corrected CD no date 7078.11 - all equal rule outcome. No scored value changed.
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
TRACEABILITY OK
SCOPE OK
