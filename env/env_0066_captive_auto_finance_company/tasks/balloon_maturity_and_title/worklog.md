# worklog — balloon_maturity_and_title (env_0066), erl-task-instantiate round 1
draws: task0 prerequisite_problems=3 factor_counts=[5,5,6,6]; task1 prerequisite_problems=2 factor_counts=[5,6,5]
design decision: user-owned writes must carry a policy-determined computed amount; ledger-closing payments (pay a quote, pay fees due) cannot carry load-bearing factors honestly, so task 0's customer write is a return balance plan payment and task 1's is the pre-refinance payment (amounts set by company schedules).
task 0 (returned-vehicle settlement): problems balloon_ext_return_mileage_charge(6f) balloon_ext_return_wear_charge(6f) balloon_ext_return_fee(5f) -> root balloon_ext_return_balance_plan(5f, user). gold 623.20 / 179.66 / 205.00 / 355.25. per-task gates all OK (docs not yet rendered). Full dossier in tasks/0.json design_rationale.
task 1 (matured-balloon refinance): problems balloon_ext_payoff_quote(5f) -> balloon_ext_refinance_precondition_payment(5f, user) -> root balloon_ext_balloon_refinance(6f) plus root -> quote (diamond); edges: payment<-quote state/value_input, refinance<-quote state/value_input, refinance<-payment action/value_input (fallback: balloon_payment rows are also written by the return balance payment tool). gold 27235.19 / 3667.19 / 742.24 (amount 23568.00, 36 months, 8.34%). Full dossier in tasks/1.json design_rationale.
overwrites declared: mileage, wear, return fee clauses of balloon_vehicle_return; payable_status (returned contracts only) and the 30-day due clause (planned charges only) for the return balance plan; good-through and per-diem/payoff sentences of balloon_payoff_and_refunds (customer payoff quotes under the rule); allocation order of balloon_payment_posting (pre-refinance payment only); amount-refinanced, term/APR and refi_history sentences of balloon_refinancing (late-charge cap kept).
probes, factor-independence tables, method pairwise tables and compute_basis sweep (0 misses) are recorded in each task's design_rationale.
final gate block (bash /tmp/erl0066_coord/d_gates.sh balloon_maturity_and_title, TRACE=1):
[check_extended ] EXTENDED OK
[check_task_tools ] TASK TOOL CONTRACT OK
[replay_tasks --check] REPLAY OK
[check_solvability ] SOLVABILITY OK
[check_compute ] suite means: branches=88.00(>= 4.0) steps=14.00(>= 4.0) suite depth: history_rows_max=41(>= 8) branches_max=104(>= 5) COMPUTE OK
[check_grounding ] GROUNDING OK
[check_cross_fire ] SCOPE OK
[check_traceability] NOT OK — only the 7 unlock tool_name provenance misses (docs not yet published); no id/value miss.
[validate_scenario] INVALID scenario-wide; for this difficulty the only errors are the 7 "required document ... not found" (docs not yet rendered).
files: balloon.extended.yaml, task_tools.py, tasks/0.json, tasks/1.json, worklog.md
ROUND 1: gates 7/7 green

## REWORK round 2 closure (audit env/env_0066_captive_auto_finance_company/audits/policy_task/balloon_maturity_and_title/)
- T1-F1 -> tasks/1.json initial_state retail row: next_due_date advanced past the 28th paid installment; installment and principal re-derived from the Tier 1 72-month amortization; pre-owned row apr/installment put on the Tier 2 rate sheet. Seed realism sweep of both tasks: returned balloon in 0.json now shows 36 installments satisfied and an empty next_due_date; lease row residual, purchase option fee and payments follow Lease Tier 2; old retail row on its Tier 2 rate sheet.
- C-F1 member 1 (wc_standing_forgiveness) -> rungs are tier cap plus a standing bonus (new params wear_standing_bonus_preferred / _entry); no rung at or below its fall-through.
- C-F1 member 2 (rp_minimum_share) -> risk-ordered ladder over late count (24m) and returned count (12m) with params min_share_high / min_share_standard; no inert or inverted rung.
- C-F1 member 3 (mc_tolerance_miles, wc_share_billed) -> both rungs allow at most one late charge; no cross-tier inversion. Class sweep of every other ladder: monotone, no change needed.
- C-F1 member 4 (cp_down_standing) -> Tier 4/5 rung without the vacuous late-charge clause, own param down_pct_subprime (also closes G3).
- C-P1 -> refinance <- pre-refinance payment edge is state form; fallback_reason removed (also closes O-S1); O-S2 replaced_by rephrased.
- G1 (first-match reads, class) -> days_past_due reads are existential and exact in plan, quote, pre-refinance payment and refinance; mileage/wear/fee schedules scoped in their declared replaced_by to customers holding at most one record of each read kind.
- G2 -> term schedule wording states term_long_months counts as one. O-1.1 -> refinance <- quote edge is state_gate. O-1.2 -> quote tool per_diem argument names the contract-APR per diem. O-1.3 -> rationale VINs corrected. O-1.4 -> multi-source label fixed; ri_late_charge_addon made multi-source (late count, returned count). O-T1 -> ordering words removed from all tool descriptions. O-T2 -> refinance tool books a balloon_fee_payment entry for the fees it clears. O-OV1 -> plan replaced_by now follows the base allocation order. O-L1, O-R1, O-R2, O-S3, O-0.1, O-0.2 -> recorded in the task dossiers (no change needed).
- Re-run records (in each task's design_rationale "REWORK round 2" section): method pairwise tier table, transitive factor-independence table, compute_basis sweep (0 misses), decoy/absent-record probe table. Scored values and sensitivities unchanged.
final gate block (TRACE=1):
[check_extended ] EXTENDED OK
[check_task_tools ] TASK TOOL CONTRACT OK
[replay_tasks --check] REPLAY OK
[check_solvability ] SOLVABILITY OK
[check_compute ] suite means: branches=83.50(>= 4.0) steps=14.00(>= 4.0) suite depth: history_rows_max=41(>= 8) branches_max=104(>= 5) COMPUTE OK
[check_grounding ] GROUNDING OK
[check_cross_fire ] SCOPE OK
[check_traceability] NOT OK — only the 7 unlock tool_name provenance misses (docs not yet published); 0 other misses.
[validate_scenario] INVALID scenario-wide; for this difficulty only the 7 "required document ... not found" (pre-render).
REWORK round 2: gates 7/7 green

## REWORK round 3 closure (revision_2 PASS, charter=CLEAN; pre-render hardening per audits/render_source/XF_recipe.md)
Audit items:
- O2-1.1 -> tasks/1.json factor_trace labels for qt_post_maturity_rate and cp_down_standing no longer say multi-source; ri_late_charge_addon factor_sensitivity tier label corrected to the rung taken.
- O2-2 -> balloon_ext_balloon_refinance prerequisite[0].effect no longer self-refers ("this edge").
- O2-3 -> rp_minimum_share ladder reads the 24-month late-charge count only; the returned-payment disjunct and its binding removed; task 0 trace/tracing text swept.
- O2-1 -> mileage, wear and fee scope clauses state the multi-holding case as outside the rule and its tool and restate the governing base sentence.
- O-S2, O-S3, O-R1, O-R2, O-L1, O-0.1, O-0.2 -> unchanged observations, already answered in the dossiers.
XF recipe check table (P = passes as is, F = fixed this round):
| point | mileage | wear | fee | plan | quote | precondition | refinance |
| 1 assembly sentence generic | P | F | F | P | F | P | P |
| 2 non-commuting order stated | P | P (made first / taken last) | P | P | P | P | P (additive) |
| 3 factor independence (transitive) | P | P | P | P | P | P | P |
| 4 ownership (single-factor quantities in the factor) | P | P | P | P | P | P | P |
| 5 compute_basis verbatim (script sweep: 0 misses) | P | F (quotes re-pointed) | P | F | F | F | F |
| 6 ties on LATEST/first reads stated | F (inspection) | F (inspection, late charge) | n/a (no LATEST) | n/a | F (election) | F (quote) | F (quote) |
| 7 counting conventions stated | F | F | F | F | F | F | F |
| 8 every branch both ways (absent/out-of-scope) | F (no inspection; multi-holding outside tool) | F (same) | F (multi-holding outside tool) | F (other payments outside tool) | F (other quotes outside tool) | F (other payments outside tool) | P |
| 9 base clauses restated for out-of-scope cases | F | F | F | P | P | P | P |
| 10 rounding sentence = RND placement | P | P | P | P | P | P | P |
| 11 tools (effects, no examples, no ordering words) | P | P | P | P | P | P | P |
| 12 proof text agrees | P | P | P | F | P | P | F (labels) |
Re-run records:
- Method pairwise table: mc_odometer_reading, mc_allowance_basis, wc_forgiveness_proration, fc_fee_basis, rp_plan_length, qt_good_through, cp_vehicle_age, ri_term_schedule — each pair has a distinguishing input (unchanged from round 2; no method ladder edited this round).
- Factor independence (transitive): no factor binding reads another factor's binding; rp_minimum_share now owns share_late_window only; assembly in plain bindings/result.
- compute_basis sweep: 0 misses (quotes, baseline sentences, replaced_by, policy_source).
- Probe table: same-date second inspection recorded later -> task 0 values unchanged; no inspection -> mileage/wear outside rule and tool; same-day second election recorded later -> task 1 values unchanged; round-2 decoys (closed lease first, second past-due retail first, stale quote, older election) unchanged.
- Scored values and every sensitivity figure unchanged.
final gate block (TRACE=1):
[check_extended ] EXTENDED OK
[check_task_tools ] TASK TOOL CONTRACT OK
[replay_tasks --check] REPLAY OK
[check_solvability ] SOLVABILITY OK
[check_compute ] suite means: branches=83.50(>= 4.0) steps=14.00(>= 4.0) suite depth: history_rows_max=41(>= 8) branches_max=104(>= 5) COMPUTE OK
[check_grounding ] GROUNDING OK
[check_cross_fire ] SCOPE OK
[check_traceability] NOT OK — only the 7 unlock tool_name provenance misses (pre-render); 0 other misses.
[validate_scenario] INVALID scenario-wide; for this difficulty only the 7 "required document ... not found" (pre-render).
REWORK round 3: gates 7/7 green

## REWORK round 4 closure (revision_3: C3-X2, C3-X9, T0-R3-1)
- C3-X2 (wear member) -> wear combination sentence fixes the order generically: replacements of the forgiveness first, proration second, then the subtraction of forgiveness and credits, then any share last; forgiveness_applied basis quote updated.
- C3-X2 (fee member) -> fee combination sentence: the basis of the return fee is set first, every reduction then subtracted from it; basis quote updated.
- C3-X2 class sweep -> mileage (replacements act on inputs, forgiveness subtracted from the derived difference, rate reduced before pricing), plan (larger-of, then prior part, then deferrals off, then upfront added), quote (courtesy days off, then each day at its rate), precondition (points summed, figured, rounded, then credits), refinance (additive rate adjustments, then term and installment): each already fixes its order; no change.
- T0-R3-1 -> closed by C3-X2: wear 179.66, fee 205.00 and plan 355.25 are again the only readings (task 0 dossier "REWORK round 4").
- C3-X9 -> quote overwrite[1].replaced_by (and its rule copy) restates the base per diem / payoff wording for out-of-scope quotes. Overwrite sweep: mileage, wear, fee, plan (both), quote[0], precondition restate their retired clauses; refinance needs none (every balloon refinance is booked under that rule, O3-2).
- O3-1 -> plan compute_basis now carries return_charges with its rule sentence. O3-2 -> no change (observation).
- XF table corrections vs round 3: point 2 wear F, fee F; point 9 quote F; point 5 plan F (return_charges). All other cells as recorded in round 3. Method pairwise, factor-independence and probe tables unchanged (no compute edited); compute_basis sweep 0 misses.
final gate block (TRACE=1):
[check_extended ] EXTENDED OK
[check_task_tools ] TASK TOOL CONTRACT OK
[replay_tasks --check] REPLAY OK
[check_solvability ] SOLVABILITY OK
[check_compute ] suite means: branches=83.50(>= 4.0) steps=14.00(>= 4.0) suite depth: history_rows_max=41(>= 8) branches_max=104(>= 5) COMPUTE OK
[check_grounding ] GROUNDING OK
[check_cross_fire ] SCOPE OK
[check_traceability] NOT OK — only the 7 unlock tool_name provenance misses (this difficulty's KB not yet rendered); 0 other misses.
[validate_scenario] INVALID {'scenario': 'env_0066_captive_auto_finance_company', 'difficulties': 5, 'tasks': 10, 'tasks_ok': 10, 'tools': 59, 'documents': 169}; for this difficulty only "required document ... not found" errors.
REWORK round 4: gates 7/7 green

## REWORK round 5 closure (KB audit policy_kb round 1, src=SRC-1..SRC-4; render_source render_r1 notes)
- SRC-1 (renderer note 1) -> quote overwrite[1].replaced_by and its rule copy restate the out-of-scope per diem as the base formula computes it, including the division by 100. The base text itself is frozen (blueprint-known slip).
- SRC-2 (renderer note 2) -> "one or more" in the plan prior-fee share, the plan upfront amount and the precondition returned-payment rung (rule sentences, basis quotes, ladder labels). Class sweep: other "one" uses are "exactly one" (fee record, plan minimum share, refinance late add-on, wear/mileage "at most one") or "one or two" (quote grace) and match their compute.
- SRC-3 -> quote: plain sentence defines the days after maturity; qt_post_maturity_rate now decides post_per_diem (baseline: the per diem), so the post-maturity daily rate lives only in the factor; pre_maturity_days basis re-pointed to the plain sentence.
- SRC-4 -> task 0 persona backstory timing corrected.
- PN-1, PN-2 and the held-payment record-detail observation -> recorded only. The held payment's balances are applied by the refinance booking (interest paid to today, fees cleared with a fee-payment entry, principal = amount refinanced).
- Re-runs: compute_basis sweep 0 misses. Factor independence is unchanged except that post_per_diem moved into qt_post_maturity_rate, which reads only its own post_rate. Method pairwise table unchanged (no method ladder edited). Probe table unchanged: every scored value and sensitivity figure is the same, as COMPUTE OK confirms.
- XF table: points 1/4 quote F (SRC-3); point 9 quote F (SRC-1); point 12 plan/precondition F (SRC-2), task 0 persona F (SRC-4). All other cells as in round 4.
final gate block (TRACE=1):
[check_extended ] EXTENDED OK
[check_task_tools ] TASK TOOL CONTRACT OK
[replay_tasks --check] REPLAY OK
[check_solvability ] SOLVABILITY OK
[check_compute ] suite means: branches=83.50(>= 4.0) steps=14.00(>= 4.0) suite depth: history_rows_max=41(>= 8) branches_max=104(>= 5) COMPUTE OK
[check_grounding ] GROUNDING OK
[check_cross_fire ] SCOPE OK
[check_traceability] 0.json 18 0 True 1.json 15 0 True TRACEABILITY OK
[validate_scenario] INVALID {'scenario': 'env_0066_captive_auto_finance_company', 'difficulties': 5, 'tasks': 10, 'tasks_ok': 10, 'tools': 59, 'documents': 303}; no error names balloon_maturity_and_title.
REWORK round 5: gates 8/8 green
