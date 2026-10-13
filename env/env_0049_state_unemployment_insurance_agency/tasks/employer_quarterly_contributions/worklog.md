# employer_quarterly_contributions — instantiation worklog (category taxacct, M=2)

Draw (draw_counts.py --tasks 2): task 0 = 1 prerequisite problem, factor counts [4, 4]; task 1 = 1 prerequisite problem, factor counts [6, 6].

| task | root (owner) | prerequisite (owner) | edge | gold |
|---|---|---|---|---|
| 0 | taxacct_ext_credit_refund_request -> request_credit_refund_f44db5b5 (user) | taxacct_ext_estimated_assessment -> book_estimated_assessment_54fbfb5a (agent) | value_input, state form ("only after") | estimate 2307.06 for 2026-Q2; refund request 293.52 |
| 1 | taxacct_ext_penalty_relief_request -> request_penalty_relief_44d7156f (user) | taxacct_ext_late_report_penalty -> assess_late_report_penalty_9b2fdf0c (agent) | value_input, state form ("not ... until") | penalty 645.76 for 2026-Q2; relief request 73.80 on 2026-Q3 |

Cross-difficulty factors: task 0 appeal_interest_allowance (appeal product: outcome + filing-to-decision span); task 1 claim_notice_cooperation_share (charge product: late answer to a notice of claim).
Multi-source factors: task 0 appeal_interest_allowance; task 1 paper_filing_charge, paper_filing_relief_factor.
Prerequisite deletion runs: task 0 refund without the estimate 2663.39 (vs 293.52); task 1 relief without the penalty 98.40 (vs 73.80).
Seed histories are computed with the charter's own rules (task 0's 2025-Q1 penalty 519.00 with the penalty rule; task 1's 2026-Q2 estimate 1500.91 with the estimate rule).
Customer identifiers stay in the band: phones 6085554118 / 6085554731, FEIN last four 4462 / 4815, ZIPs 53764 / 53772.

Final gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 27.00, steps 10.00; history_rows_max 32; branches_max 30); GROUNDING OK; CACHE-DIFF INFO (diagnostic only); SCOPE OK.
check_traceability not run: it needs the rendered KB. validate_scenario: INVALID only because the KB is not rendered yet ("required document ... not found" for every difficulty, plus "task tool ... not mentioned in any KB document" warnings); all 6 scenario tasks replay cleanly (tasks_ok 6).
Full per-task dossiers: design_rationale in tasks/0.json and tasks/1.json.

## Rework round 2 (audit audits/policy_task/employer_quarterly_contributions: _difficulty.md, 0.md, 1.md)

Authoring scripts in a private /tmp dir (rework_ext.py rewrote extended_policies via yaml dump with the base text verbatim; recalc.py re-evaluated with check_compute's evaluator on the real tool replay; patch_t0.py / patch_t1.py patched the task JSONs field by field); removed afterwards. blueprint/ untouched.

Per audit item:
- F-1 (method labels on scalar-pickers): estimate_hold (refund), repeat_multiplier (penalty) and paper_filing_relief_factor (relief) relabelled `parameter`. To keep an honest method in every computation: refund appeal_interest_allowance rebuilt as a method that chooses the interest start date (credited-back quarter's last contribution payment / appeal filing date / no allowance), allowance = class monthly late-payment interest rate x credited-back contributions x interest months (whole months to the request + 1), rounded to the cent; relief gains relief_lookback_length (method: delinquent 36 / clean-record 12 / standard 8 quarters x 3 months window for counting other penalties). Counts: estimate 3P+1M (unchanged), refund 3P+1M, penalty 5P+1M, relief 5P+1M.
- F-2 (cooperation first-match / overlapping answers / good cause unread): late_answer_date now XLATEST('charge','charge_positions','response_date', date_field='response_date', response_timeliness='late'); rule reads "the most recent answer ... recorded as late without good cause (answers recorded as late with good cause do not count)".
- F-3 / T1-F3 (request_timing_share unreal): factor, its sentence, params and bindings (days_to_request, timing_share, penalty_assessed_date) removed; the relief product is now five shares.
- F-4 / T0-F2 (task 0 had no real multi-source factor): appeal_interest_allowance tiers each join the appeal row (decision outcome, filed date; XLATEST by decision_mailed_date, contribution_rate determinations) with a tax-ledger payment row (last contribution payment of the credited-back quarter). Old long_appeal_days / full / partial rates and appeal_days binding removed.
- T0-F1: same as F-1 for the refund (estimate_hold parameter; appeal allowance method).
- T0-O1 (credit_payment_entry_id inferred): refund rule adds "The request cites the payment that created the credit: where the credit arose from contributions credited back to a quarter, it is the last contribution payment received for that quarter."; tracing cites it.
- T0-O2 / O-12 (realism of cushion/hold): no change. These are the Department's own published holds; they are disclosed in the rule and every tier is driven by records. Noted here only.
- T1-F1: paper_filing_relief_factor labelled parameter (still multi-source: the relieved report's channel + other reports' portal filings).
- T1-F2: repeat_multiplier labelled parameter; dossier counts corrected (penalty 5P+1M).
- O-1: estimate trigger and refund prerequisite sentence both say "at least the class's estimated assessment days after its due date" (matches compute >=).
- O-2: estimate windows sentence adds "an average taken over a window in which no original report was filed is zero"; compute_basis updated.
- O-3: appeal read as the most recently decided contribution-rate appeal; contribution hold reads "the most recent contribution assessment booked from an original report".
- O-4: penalty final sentence/overwrite replaced_by/compute_basis: single rounding applied to the sum, not to any part.
- O-5: within_months 34 pin removed from penalty inputs.
- O-6: relief payment share counts payments and credits ("fully covered by the payments and credits applied to them"; quarter_credited binding).
- O-7: task_tools.py docstrings no longer use "until"/"later" ordering words (estimate and refund tools).
- O-8: relief prerequisite sentence narrowed to "the quarter of the original report with the latest filing date, whenever that report was filed after its due date" (the only quarter the penalty rule can compute); condition, effect, closure edge and dossier updated.
- O-9: "decided afterwards" -> "is decided by the Department's tax review unit".
- O-10 (rate year): already declared; no change.
- O-11 (repeat_lookback_length borderline method): kept. It decides which penalty records the count runs over (window convention), not a scalar in the formula.
- Dossier false assertions: method counts corrected; task 0 multi-source claim now true (appeal_interest_allowance); task 1 "paper_filing_charge multi-source" corrected (single report row; multi-source = estimate_charge, paper_filing_relief_factor); stray "XX" placeholder in task 0 four-point test fixed.

Recomputed (check_compute evaluator, handling-time world):
- T0 estimate 2307.06 (unchanged). Refund 325.00 (was 293.52): credit 769.44, appeal decided reversed, filed 2026-01-05, credited-back 2026-Q1 last payment 2026-04-29 (on/after filing) -> 8 months x 0.01 x 1076.50 = 86.12; ((769.44+86.12) x 0.9 - 0.5 x 240.00) x 0.5. Factor baselines {appeal_interest_allowance 286.25, reporting_cushion 367.78, contribution_hold 385.0, estimate_hold 650.0}; all-baseline 769.44; skip-estimate 2726.36.
- T1 penalty 645.76 (unchanged). Relief 51.79 (was 73.80): delinquent -> 36-month lookback -> 2 other penalties -> 0.5; x0.85 x0.9 x0.85 x0.75. Factor baselines {late_penalty_history_share 103.58, relief_lookback_length 77.68, estimated_assessment_share 60.93, quarter_payment_share 57.54, claim_notice_cooperation_share 60.93, paper_filing_relief_factor 69.05}; all-baseline 212.38; skip-penalty 77.68.

Gate re-run (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 10 acts det True closure 63/63; 1.json 10 acts closure 55/55); SOLVABILITY OK; COMPUTE OK (0.json fact 8 xfac 1 hist 33 brch 23 step 10; 1.json fact 12 xfac 1 hist 27 brch 30 step 10; suite means branches 26.50 steps 10.00; history_rows_max 33; branches_max 30); GROUNDING OK; CACHE-DIFF INFO (diagnostic only); SCOPE OK. Forbidden-token scan of task_tools.py: all 11 tokens 0. validate_scenario: INVALID, with all 27 errors "required document ... not found" (KB not rendered) and 27 "task tool ... not mentioned in any KB document" warnings; tasks_ok 10/10. check_traceability not run (needs the rendered KB).

## Rework round 3 (audit revision_2 sections of _difficulty.md, 0.md, 1.md; task 0 PASS, task 1 SOURCE-FACTOR RED)

Private scratch /tmp/erl0049_r3 (yaml loader/dumper reproducing the extended part byte-for-byte at width 110 before editing; charter edit script; task JSON patch script), removed afterwards. blueprint/ untouched (first 1171 lines still byte-identical to blueprint/products/taxacct.yaml).

Per audit item:
- R2-F1 / T1-R2-F1 / T1-F1 (relief computation had no honest method; relief_lookback_length picked one of three constants): relief_lookback_length rebuilt so each non-fall-through tier takes the counting window from a different record date. Delinquent account -> its whole liability since registration (MONTHS(registered_date, NOW) + 1). Active account with no late-payment interest entry in the payment record months -> only back to its most recent late-payment interest entry (MONTHS(that entry, NOW) + 1), or the whole liability when it has never had one. Otherwise -> the standard 8 quarters x 3 (baseline). Rule sentence, compute (new bindings relief_liability_months, last_interest_date), compute_basis, factor ladder/bindings/evidence and inputs (latest interest entry) updated; params delinquent_lookback_months and clean_record_lookback_months removed. Task 1 world: delinquent, registered 2024-02-12 -> 34-month window, still admits the 2024-08-20 penalty -> relief 51.79 unchanged, factor baselines unchanged (relief_lookback_length 77.68), skip-prerequisite 77.68. tasks/1.json: factor_trace, factor_sensitivity tier text, argument tracing, closure flips text, relief factor card and draft recomputation now say 34-month whole-liability window; round-3 dossier section appended.
- R2-O1 (estimate basis strings not contiguous rule fragments): compute_basis.recent_report_count and .longer_average reset to verbatim rule fragments. All compute_basis strings of the four policies are now whitespace-normalised substrings of their rules (asserted by script).
- R2-O2 (stale contribution-hold quote): compute_basis.late_payment_entries now quotes the current rule sentence ("... the most recent contribution assessment booked from an original report: ...").
- R2-O3 (singular credited quarter; NOW sentinel): the rule now puts the allowance "on the contributions credited back within the appeal credit months to the quarter most recently credited back because a contribution rate was reduced on appeal, the credited-back quarter:"; compute computes credited_quarter first and restricts appeal_credit to quarter=credited_quarter. The no-allowance case now yields None (interest_months 0 when start is None; factor baseline interest_start_date None), so a payment dated the request day counts one month. Task 0 world: one credited quarter, no payment on 2026-12-10 -> all figures unchanged (refund 325.00, baselines 286.25/367.78/385.0/650.0, all-baseline 769.44, skip 2726.36); round-3 note appended to tasks/0.json dossier.
- O-10, O-11, O-12 / T0-O2: kept as observations (reasons in the round-2 entries); repeat_lookback_length unchanged.

Gate re-run (no --task), all rc=0: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 10 acts det True errs 0 closure 63/63; 1.json 10 acts errs 0 closure 55/55); SOLVABILITY OK; COMPUTE OK (0.json fact 8 xfac 1 hist 33 brch 23 step 10; 1.json fact 12 xfac 1 hist 27 brch 31 step 10; suite means branches 27.00 steps 10.00; history_rows_max 33; branches_max 31); GROUNDING OK; CACHE-DIFF INFO (diagnostic only); SCOPE OK. Forbidden-token scan of task_tools.py: all 11 tokens 0. validate_scenario: INVALID, with all 23 errors "required document ... not found" and all 23 warnings "task tool ... not mentioned in any KB document"; this difficulty's four documents are not rendered yet; tasks_ok 10/10, documents 82. check_traceability not run (this difficulty's KB not rendered).

## Rework round 4 (audit audits/policy_kb/employer_quarterly_contributions: 0.md, 1.md; both tasks KB-RUNTIME / KB-BIJECTION / KB-EXPLICIT PASS)

taxacct.extended.yaml and task_tools.py NOT changed: the published KB was rendered from them (sha256 c3401e74... / 9f7c924f..., unchanged after this round). Private scratch /tmp/erl0049_r4 (one value-for-value string patch script), removed afterwards.

Per audit item:
- Policy-side note (c), task-side proof text: tasks/0.json find_appeals necessity said the allowance tier is decided by "the appeal outcome and its filing-to-decision span (133 days)", a leftover of the round-1 ladder. It now says the tier is decided from the outcome and filing date of the most recently decided contribution-rate appeal (selected by decision mailing date), set against the credited-back quarter's last contribution payment (2026-04-29, on/after the 2026-01-05 filing, so interest runs from the payment date). Same staleness swept in other proof text, all value-for-value with no number changed:
  - tasks/0.json wage-report necessity: "more than 60 days past due" -> "still unfiled at least 60 days after its due date" (O-1 wording).
  - tasks/0.json ledger necessity: now names the credited-back quarter's credit and its last contribution payment (interest start and cited payment).
  - tasks/0.json estimate-write necessity: "every unfiled quarter past the estimate days" -> "every quarter still unfiled at least the estimate days after its due date".
  - tasks/1.json account-read necessity: adds that the delinquent status and registration date set the relief lookback.
  - tasks/1.json reports necessity: names the latest-filed original report (2026-Q2) as the unmet prerequisite (O-8 wording).
  - tasks/1.json ledger necessity: adds the 2024-08-20 penalty counted in the relief lookback.
  - tasks/1.json cooperation necessity: "most recent answer recorded as late without good cause" (F-2 wording).
  - tasks/1.json penalty-write necessity: "a penalty for every late-filed quarter" -> "the quarter of the original report with the latest filing date, whenever that report was filed late".
- Note (a), stale parameter_schema description of penalty_abatement_lookback_quarters: no change (base-side; coordinator instruction).
- Note (b), source factor definitions that reference one another: no change (source-forced; coordinator instruction).

Gate re-run (no --task), all rc=0: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 10 acts errs 0 closure 63/63; 1.json 10 acts errs 0 closure 55/55); SOLVABILITY OK; COMPUTE OK (suite means branches 27.00 steps 10.00; history_rows_max 33; branches_max 31); GROUNDING OK; TRACEABILITY OK (0.json copied 13 missing 0; 1.json copied 14 missing 0); CACHE-DIFF INFO (diagnostic only); SCOPE OK. Forbidden-token scan: all 0. validate_scenario: INVALID only from other difficulties' still-missing documents (12 errors, 12 warnings, none for employer_quarterly_contributions); tasks_ok 10/10, documents 200.
