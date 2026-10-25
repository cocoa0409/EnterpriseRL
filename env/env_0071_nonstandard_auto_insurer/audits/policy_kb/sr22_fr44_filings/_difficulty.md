# KB-doc policy audit — sr22_fr44_filings (category fr), difficulty report

## revision_1 (2026-10-21)

### Entry conditions (cited, not re-judged)
- Policy side: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/sr22_fr44_filings/_difficulty.md, verdict line only).
- Coordinator gate snapshot 2026-10-21T00:51:15: check_docs fr DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); check_traceability TRACEABILITY OK (0 misses). Source sha256 fr.extended.yaml 1af74754…2d45e0, task_tools.py b1ec27e0…2a70.
- Re-run of `/tmp/erl0071_coord/kb_snapshot.sh sr22_fr44_filings fr` at 00:51:58 (entry) and again at close: identical lines (DOCS OK, all gates rc=0, TRACEABILITY OK, 0 misses, same hashes, 54 fr docs). docs/fr corpus sha 8804e9ea…ad93 unchanged from blind freeze to close.
- Runtime view: .audit_views/runtime/sr22_fr44_filings/{0,1}.runtime.json; DB access only through db_query.py (blind on the DB side).

### Part verdicts per task
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Files |
|---|---|---|---|---|
| 0 (lapse SR-26 → reinstatement refiling) | PASS | PASS | PASS | runtime_context/sr22_fr44_filings/0.md, policy_kb/sr22_fr44_filings/0.md |
| 1 (cancellation SR-26 → fee charged again → moved certificate) | PASS | PASS | PASS | runtime_context/sr22_fr44_filings/1.md, policy_kb/sr22_fr44_filings/1.md |

Blind answers (frozen before any source read) matched GT on every write, argument, edge and order: task 0 runoff 18 / refiling fee 38.00; task 1 runoff 15 / fee charged again 32.00 / moved fee 35.00. Every hop was state-derived; none pre-solved. Fall-back numbers (computation doc only) differ from gold in every computation (10 / 25.00; 10 / 25.00 / 25.00).

### KB defects
None.

### Cross-product-pending (re-judge when auto and billing publish)
- XP-1: cancellation run-off nonpayment tier reads "the reinstatement window days that the backing term's package carries in the Owner Auto Policy or Named Non-Owner Policy schedule"; the nonowner KB carries the figure (nonpayment_and_reinstatement_figures), the auto KB is not yet published. Not exercised by either task.
- XP-2: task 1's factor tiers rest on Owner Auto Policy records (garaging state, cancellation reason, financial responsibility filing, new-business premium). The fr factor docs name these fields in record words themselves; confirm the auto KB uses compatible vocabulary once published.
- XP-3: "billed on the backing term's / new term's billing plan" — billing KB pending; no amount depends on it.

### Source-side findings (reported separately; not KB defects)
- SRC-1 (seed, task 1, low): the replaced SR-22 Owner-Operator certificate's ledger holds four `fr_filing_fee_assessed` 35.00 charges (2026-07-10, 07-15, 08-14, 09-14), each reversed in full `company_error`. The gold moved-certificate fee is also 35.00 (13 + 2 + 4 + 2 + 8 + 6), so a solver that just carries the old filing's fee onto the new filing reaches the gold end state without applying the moved-certificate schedule. The root write's factor weight is partly masked by a seeded coincidence. Also realism: the same wrong 35.00 charge repeated and reversed four times on one request is an unusual history (the ceiling 140.00 it feeds does not bind).

### Policy-side notes (do not change this verdict)
- N-1: each extended baseline's own `rule`/`result` text states the settlement order ("an adjustment that replaces the standard fee is applied first, and every adjustment that adds an amount is then added …"). Rendered as-is in refiling_fee_tariff, recharge_fee_tariff, moved_certificate_fee_tariff, lapse_runoff_reckoning and cancellation_runoff_reckoning. It tells the reader that replacing and additive adjustments exist. It comes from the source, so the KB is not at fault.
- N-2: base law states orderings that independently put the SR-26 first: fr_sr26_notice ("reinstated after its SR-26 … a new filing with filing_reason reinstatement_refiling is required") and the open-filing exception ("allowed while the earlier filing is cancellation_filed"). Rendered as base law.
- N-3: fr_ext_refiling_fee rule parenthetical "(its SR-26 sent under the lapse SR-26 rule)" is not repeated in reinstatement_refiling_order. The lapse doc's scope already implies it, so nothing in meaning is lost.
- N-4: doc example intermediates equal some task intermediates (refiling_fee_basis example "26.00 → 13"; task 0's basis is 13 from 25.00; lapse counting example "21 less 6 = 15"). These are hypothetical figures from different inputs, and no scored final value appears in any example or unlock schema.

### Closing checklist
- Audit files match tasks one-to-one (0, 1), each with blind_answer/gt_comparison and source_to_kb/kb_to_source/bijection_verdict/dependency_form. No prior revisions existed.
- Every normative atom of the five extended policies and their base refs is carried. Every prerequisite sentence (4 edges) is verbatim, state form, only in its blocked policy's hub. Every factor ladder (27 factors) is carried in full in its own document. Each tool name appears only in its own hub. No route or aggregated chain.
- check_docs fr and the gate/traceability snapshot were re-run at close: green, lines above.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1

## revision_2 (2026-10-21, re-audit round 2)

### Gate
- `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN` (policy_task _difficulty.md, verdict line only).
- `/tmp/erl0071_coord/kb_snapshot.sh sr22_fr44_filings fr` (run only):
  - check_docs fr: DOCS OK.
  - Gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all rc=0.
  - check_traceability: TRACEABILITY OK; misses 0, non-unlock misses 0.
  - Source hashes: fr.extended.yaml 1af747543543cd72c97c1d14a14f50353e8fc4bf5283bb26f07433548b2d45e0, task_tools.py b1ec27e054c3706533a256802cec0d8435b5f9df89bc11fe6f688dca1c192a70 (unchanged).
  - 54 fr docs; corpus sha 8804e9ea…ad93 (unchanged, so no re-render).

### Round-1 items
- **SRC-1: CLOSED.**
  - New task-1 seed: the filing state is FL. The replaced certificate's ledger holds 35.00 (FR-44 rate), 25.00 (coded new_requirement), 50.00 (billed for two certificates) and 25.00 (re-sent by the September run). Each was reversed once in full as company_error. Standing is 0.00; reversals total 135.00. The TX plan's billing rows mirror each charge and waiver.
  - New gold: 15 / 32.00 / 31.00. No readable amount equals a scored value.
  - Copying any old fee (25.00 / 35.00 / 50.00), the FR-44 rate, or the 32.00 that the fee charged again leaves standing on the replaced filing gives the wrong moved fee. 31.00 needs the factor schedule, including the FL-vs-VA same-group 4.00 rung.
  - The history is now plausible: each charge has its own visible error mark (rate, reason code, amount), apart from the September re-send, whose cause is visible only as a company_error reversal of a correctly priced charge. That is acceptable as a batch error and is not routed.
- Notes N-1 to N-4 and cross-product items XP-1 to XP-3 carry over unchanged (auto and billing still pending).

### Part verdicts revision_2
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (world and gold unchanged: 18 / 38.00) | PASS | PASS |
| 1 | PASS (new gold 15 / 32.00 / 31.00 derived before reveal) | PASS | PASS |

### Input note
- `.audit_views/runtime/sr22_fr44_filings/1.runtime.json` is stale: it still describes Arizona, while the current task file describes Florida. This round used the task file's frozen_time/user_scenario fields and db_query instead. Regenerate the view.

### Contamination disclosure
- Round 2 is charter-aware (revision_1 read the source and the round-1 GT).
- No round-2 gold value was seen before the round-2 blind answers were frozen. They are appended under revision_2 in runtime_context/sr22_fr44_filings/{0,1}.md.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none

## revision_3 (2026-10-21, re-audit round 3, cross-product re-judge)

### Gate and inputs
- `/tmp/erl0071_coord/kb_snapshot.sh sr22_fr44_filings fr` (run only):
  - check_docs fr: DOCS OK.
  - Gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE: all rc=0.
  - check_traceability: TRACEABILITY OK; misses 0, non-unlock misses 0.
  - Hashes: fr.extended.yaml 1af747543543cd72c97c1d14a14f50353e8fc4bf5283bb26f07433548b2d45e0, task_tools.py b1ec27e054c3706533a256802cec0d8435b5f9df89bc11fe6f688dca1c192a70.
  - Docs tree now holds auto, billing, fr, nonowner, physdam, rental and towing. docs/fr sha 8804e9ea…ad93 is unchanged.
- The runtime views are regenerated and equal the task files' frozen_time/user_scenario.
- World: all 21 customer-scoped finders, run through db_query for both tasks.
- Owning docs read:
  - auto: insured-request cancellation, return figure/methods/rules, short-rate table, certificate run-off and SR-26-days rules, installment-plan charge, fees, state pages, reinstatement figures, package acceptability, liability limits.
  - billing: down payment, schedule, installment, invoice minimum due, fee and late-fee rules, posting, waivers, final bill, refund, reactivation.
  - nonowner: eligibility, acceptance standards, notice, rescission, return standard and conventions, reinstatement and re-write rules with their factors, fees, conversion, underwriting cancellation, realignment.

### Cross-product-pending items: resolved
- XP-1 (auto package reinstatement window): carried in auto reinstatement_terms_d85d6910 by package. The nonowner figure is in nonpayment_and_reinstatement_figures. Both are findable from the fr wording. CLOSED.
- XP-2 (auto vocabulary): consistent. CLOSED.
- XP-3 (billing references): consistent with the fr fee docs; no amount depends on them. CLOSED.
- No cross-product contradiction with the fr docs was found.

### Exhaustive member pass: other products' seeded rows

**Task 0 (Darius Fenwick)**

| # | Row(s) | Owning rule (published) | Verdict |
|---|---|---|---|
| 0.1 | NNO a7050b8c… bound 2026-05-12, Non-Owner 100/300/50, resident_state GA, backing the FR-44 Operator certificate c044b8ff (filed with FL) | nonowner eligibility condition 5 and the acceptance standards: an FR-44 Operator certificate may be backed "only where the residence state is among the package's FR-44 filing states". 100/300/50 lists FL, VA. Blueprint nonowner charter: "only where the residence state is in fr44_filing_states" | **NOT PRODUCIBLE → SRC-2** |
| 0.2 | NNO: points 7, 6-month term, 184 days, full-term 1318.00, policy fee 20.00, Non-Owner Statement 2026-05-09 (no owned vehicle, no regular use) | acceptance max 12, DUI accepted; statement no more than 30 days old; fee schedule 20.00 | consistent |
| 0.3 | Notices 2026-07-15 (invoice f3560418, due 07-12) and 2026-10-15 (invoice 7d319931, due 10-12); effective dates 07-25 / 10-25; minimum due 219.88 | notice issue 3 days after the due date; threshold 10.00; GA 10 notice days (auto state pages); minimum due = past due on the mailing date (late fees post 07-18 / 10-18, after mailing) | consistent |
| 0.4 | July notice ended by the 07-20 payment of 234.88 | rescission: payments of at least the minimum due by the effective date | consistent |
| 0.5 | Cancellation 10-25 for nonpayment; return 128.93 for 18 days; credited to the plan 10-25 | nonpayment return, transaction by transaction: 1318 × 18 / 184 = 128.93; credited within 15 days | consistent |
| 0.6 | Payment 105.95 on 10-26; Statement of No Loss 10-26 (lapse from 10-25); reinstated 10-27 with lapse, lapse 10-25..10-26 | all past due paid; window 20 days; statement no more than 3 days old; effective = later of payment/statement + 1 = 10-27; lapse runs to the day before | consistent |
| 0.7 | Reinstatement re-written premium entry 114.60, 16 days, from 10-27 | nonowner re-write rule with its factors. Certified exposure: FR-44 Operator certificate filed 05-15 (on or before the first lapse day 10-25), required-through 2027-08-31 (after the last lapse day) → "the whole nonpayment cancellation return is re-written as a flat amount, booked from the cancellation effective date with that return's days". Lapse length 2 days → no relativity; Six-Pay → no plan credit; no returned payments → none. The rule gives **128.93, 18 days, from 10-25**. The seeded 114.60 is the plain per-day figure (128.93 × 16 / 18) | **MISPRICED → SRC-3** (knock-on: term_written_premium 1303.67 → 1318.00; plan charge 114.60 → 128.93; balance 134.60 → 148.93) |
| 0.8 | Reinstatement fee 20.00; term_fees_charged 40.00 | fee schedule; once per reinstatement with lapse | consistent |
| 0.9 | Auto FL term fc118c72…: request received 05-08 (vehicle sold or totaled), requested and effective 05-12, confirmed; return 288.89 for 69 days; term_written_premium 553.11 | auto insured-request return: 842 / 181 × 69 = 320.98. Short-rate table: "vehicle sold or totaled … nothing (returned pro rata)". financial_responsibility_filing none → no certificate days. Paid-in-Full → no installment charge. So **320.98**. The seeded 288.89 is the retired 10 % retention (320.98 × 0.9) | **MISPRICED → SRC-4a** (knock-on: term_written_premium 521.02; PIF credit and refund 288.89 → 320.98) |
| 0.10 | Six-Pay plan 63b2bc1e…: down 318.60; five invoices of 210.88 + 9.00 (minimum 219.88) on day-12 due dates, issued 20 days before; late fees 15.00 on 07-18 and 10-18; payments | down = 20 % × 1318 + 20 + 35 (filing fee assessed on set-up day); spread (1318 − 263.60) / 5; fee 9.00; late fee after 5 grace days, one per invoice | consistent |
| 0.11 | Final bill 10-25 of 105.95, due 11-14, no installment fee | balance 234.88 − credit 128.93 = 105.95 debit above 10.00 → final bill due in 20 days | consistent with the seeded 128.93 |
| 0.12 | Reactivation 10-27: charges 114.60 + 20.00; status current; balance 134.60 | reactivation charges the re-written premium and reinstatement fee | mechanically consistent; amount inherits SRC-3 |
| 0.13 | Auto PIF plan 2769cebe…: 867.00 = 842 + 25; credit 05-12; refund 05-26; closed | refund within 15 days; plan closes | consistent; amount inherits SRC-4a |
| 0.14 | FR-44 filing fee 35.00 billed with the NNO plan down payment | billing 1.2 / down payment §1; fr fee schedule | consistent |

**Task 1 (Renee Hollister)**

| # | Row(s) | Owning rule (published) | Verdict |
|---|---|---|---|
| 1.1 | NNO 7a99b075…: TX Minimum Limits, statement 01-12, effective 01-15, fee 20.00, conversion-cancelled 07-10 to owner term 49aec2c4; return 15.14 for 5 days; PIF refund 07-24, plan closed | conversion: effective on the replacing owner term's effective date; pro rata 548 × 5 / 181 = 15.14; refund within 15 days | consistent |
| 1.2 | Auto TX term 49aec2c4…: 100/200/50, garaging TX, 184 days, 1164.00, fee 25.00, sr22, vehicle added at bind; SR-22 Owner-Operator filed 07-13 (FL) | SR-22 backable on every package; no FR-44 garaging test for SR-22 | consistent |
| 1.3 | TX term request received 10-01 (moved out of state), requested and effective 10-05, confirmed; return **552.27 for 97 days**; term_written_premium 611.73 | auto insured-request return. Certificate run-off: term written to back sr22, and certificate 1474f5d5 stood filed on 10-05 → days returned 97 − 10 = 87. Processed on the effective date → no SR-26 days kept. Moved out of state → nothing retained. Four-Pay → 15.00 withheld. 1164 × 87 / 184 − 15.00 = **535.37 for 87 days**. The seeded 552.27 = 1164 × 97 / 184 × 0.9, the retired 10 % retention with no certificate days and no plan charge | **MISPRICED → SRC-4b** (knock-on: term_written_premium 628.63; Four-Pay credit 552.27 → 535.37; balance −251.27 → −234.37) |
| 1.4 | VA term 04d78e25…: 100/300/50, garaging VA, 182 days, 1296.00, fee 25.00, sr22, new-business premium 10-05 | premium written = full-term; fee 25.00 | consistent |
| 1.5 | Four-Pay plan 9bbf388a…: down 351.00; invoices 07-21 / 08-21 / 09-20, premium 291.00 + fee 10.00, minimums 266.00 / 301.00 / 301.00; payments 08-08 / 09-09 | down = 25 % × 1164 + 25 + 35; spread 873 / 3; invoice 1 carries the 35.00 credit from the 07-12 waiver (standing balance −35.00) | consistent |
| 1.6 | Four-Pay rows billing_premium_charged 25.00 (07-15), 50.00 (08-14), 25.00 (09-14), each followed by billing_fee_waived company_error before the next invoice | billing bills a filing fee assessed after set-up only on the next installment invoice, "when that fee … has not been reversed" (1.6; installment_fee_rule). Fees reversed before the next invoice never reach the plan | **NOT PRODUCIBLE (net zero) → SRC-5** |
| 1.7 | Four-Pay status current, balance −251.27 at 10-07 (credit after the 10-05 return); no refund yet | a credit is refunded within 15 calendar days after cancellation (by 10-20) → not yet owed at frozen time | consistent in timing; amount inherits SRC-4b |
| 1.8 | Monthly EFT plan ecdb83f9…: ACH authorization 10-03; down 245.32 = 17 % × 1296 + 25; balance 1075.68; no draft notice yet | authorization before set-up; first draft notice 10 days before 11-05 → 10-26 | consistent |

### Writes another corpus makes owed at once that could move a scored figure
None in either task.
- No auto, nonowner or billing rule makes a write due at frozen time. The task-1 credit refund is due by 10-20; no invoice is due; the underwriting period ended 07-11 for task 0; realignment is not triggered because 100/300/50 accepts DUI.
- No owed or possible write of those corpora changes a field the fr factors read: resident or garaging state, financial_responsibility_filing, lapse dates, reinstatement date, cancellation reason, status, new-business premium date.
- The SRC-3/4 corrections change premium, return and balance rows only. None of these is read by any fr computation.

### Source-side findings
- **SRC-1:** stays CLOSED (revision_2).
- **SRC-2 (task 0, high, gold-moving if fixed by residence):** the seeded NNO backing term (resident_state GA, package Non-Owner 100/300/50) backs an FR-44 Operator certificate. The owning nonowner charter would not have bound that term with that certificate: an FR-44 Operator certificate is backed "only where the residence state is in fr44_filing_states", and 100/300/50 lists FL and VA. The persona ("moved from Tampa to Savannah") states the same conflict. Every fr factor that reads the backing term's own state uses GA:
  - lapse state +2, out-of-state +3;
  - refiling state 3.00, out-of-state 8.00.

  A residence-based fix moves gold. For example, FL residence gives runoff 17 and refiling 33.00; VA gives 18 and 37.00.
- **SRC-3 (task 0, medium, no gold movement):** reinstatement re-written premium 114.60 / 16 days / from 10-27. The published nonowner re-write rule (certified-exposure factor) gives 128.93 / 18 days / from 10-25. Knock-on rows: term_written_premium, the reactivation charge and the plan balance.
- **SRC-4 (both tasks, medium, no gold movement):** auto insured-request returns are priced with the retired 10 % retention, ignoring the published short-rate table, the certificate run-off rule and the installment-plan charge.
  - (a) Task 0 FL term: 288.89 should be 320.98 (69 days).
  - (b) Task 1 TX term: 552.27 / 97 days should be 535.37 / 87 days.
  - Knock-on rows: term_written_premium, plan credits and refunds, plan balance.
- **SRC-5 (task 1, low, net zero):** the three post-set-up filing-fee charges and their waivers are mirrored on the Four-Pay plan as immediate charges. Under the billing rules, fees reversed before the next invoice are never billed to the plan.

### Part verdicts revision_3
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (gold 18 / 38.00 entailed; runtime risk noted under SRC-2) | PASS | PASS |
| 1 | PASS (gold 15 / 32.00 / 31.00 entailed) | PASS | PASS |

### KB defects
None. kb=CLEAN.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=SRC-2,SRC-3,SRC-4,SRC-5

## revision_4 (2026-10-21, re-audit round 4)

### Gate and inputs
- `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`.
- `/tmp/erl0071_coord/kb_snapshot.sh sr22_fr44_filings fr` (run only):
  - check_docs fr: DOCS OK.
  - Gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE: all rc=0.
  - check_traceability: TRACEABILITY OK; misses 0, non-unlock misses 0.
  - Hashes: fr.extended.yaml 1af747543543cd72c97c1d14a14f50353e8fc4bf5283bb26f07433548b2d45e0, task_tools.py b1ec27e054c3706533a256802cec0d8435b5f9df89bc11fe6f688dca1c192a70 (unchanged).
  - docs/fr sha 8804e9ea…ad93 unchanged (no re-render).
- Runtime views: 1.runtime.json is current; **0.runtime.json is stale**. Task 0 used the task file's frozen_time/user_scenario fields plus db_query.
- World: all 22 customer-scoped finders for both tasks, run through db_query.

### Round-3 items, re-judged against the published owning docs
- **SRC-2: CLOSED.**
  - The task-0 customer is now Tampa, FL (home_state FL). The NNO backing term has resident_state FL, package Non-Owner 100/300/50, whose FR-44 states are FL and VA.
  - The nonowner binding rule ("FR-44 Operator certificate only where the residence state is among the package's FR-44 filing states") is met.
  - The FR-44 Operator is now filed with VA (the Virginia DUI in the persona). That is an eligible fr filing state, and the 100/300/50 term meets the VA minimum backing package (Non-Owner 100/200/50).
  - Knock-on rows are consistent:
    - Notice effective dates use FL's 10 nonpayment notice days (07-25 / 10-25).
    - The FL underwriting period ended 07-11, so nothing is owed.
    - Persona, phone, ZIP and policy number (CPN-FL-2471935) match the records.
- **SRC-3: CLOSED.** The re-write entry is 128.93 / 18 days / effective 10-25 (certified throughout: FR-44 filed 05-15 before the first lapse day, required-through 2027-08-31). Knock-on rows: term_written_premium 1318.00; billing reactivation charge 128.93; plan balance 148.93 (0.00 after the 105.95 final-bill payment, plus 128.93 + 20.00).
- **SRC-4: CLOSED.**
  - (a) Task 0 FL term return is 320.98 / 69 days (sold vehicle → nothing retained; no certificate; PIF → no charge). term_written_premium 521.02; PIF credit and refund 320.98.
  - (b) Task 1 TX term return is 535.37 / 87 days. term_written_premium 628.63; Four-Pay credit 535.37; balance −234.37, which recomputes exactly (1164 + 25 + 35 + 30 − 351 − 35 − 266 − 301 − 535.37).
- **SRC-5: CLOSED.** The post-set-up filing-fee mirrors are gone from the Four-Pay plan. Only the set-up-day 35.00 (in the down payment) and its 07-12 waiver remain, and invoice 1 still carries the 35.00 credit (minimum 266.00).
- Revision_3 members marked consistent: re-checked on the new worlds, still consistent. No write another corpus makes owed at once (the task-1 refund is due by 10-20; no invoice, underwriting or realignment write is due). No such write touches an fr factor input.

### Gold on the new worlds (derived before reveal, then compared)
- Task 0: run-off 18 (9 + 1 + 4 + 1 + 3); refiling fee **37.00** (13 + 10 + 2 + 4 + 6 + 2), moved from 38.00. GT: 18 / 37.00, the same.
- Task 1: 15 / 32.00 / 31.00, unchanged; GT the same.
- Fall-backs: 10 / 25.00 and 10 / 25.00 / 25.00.
- Readable amounts: none equals or copies to any gold amount.
- Non-blocking note N-5: task 0's run-off of 18 days coincides with the premium_days (18) of the NNO return and re-write entries (10-25 to 11-12). No doc reading derives run-off from that span. Running off to the expiration from the SR-26 date gives 15, so it is not a shortcut path. Not routed.

### Part verdicts revision_4
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (18 / 37.00) | PASS | PASS |
| 1 | PASS (15 / 32.00 / 31.00) | PASS | PASS |

### KB defects
None. No regression.

### Input note
`.audit_views/runtime/sr22_fr44_filings/0.runtime.json` is stale (pre-rework persona). Regenerate it.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
