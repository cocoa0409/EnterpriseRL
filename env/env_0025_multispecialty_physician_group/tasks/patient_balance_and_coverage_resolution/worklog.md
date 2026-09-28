# Worklog — erl-task-instantiate — patient_balance_and_coverage_resolution (M=2)

2026-09-24 START round=1 (resumed after rate-limit cut; nothing was on disk).
Draws (draw_counts.py --tasks 2):
  task 0: prerequisite_problems=2, factor_counts=[4, 6, 5]
  task 1: prerequisite_problems=1, factor_counts=[4, 6]
Gate-driven constraint found at Step 0: every base eligibility gate on billing_adjustment_posted
(9 gates incl. the mixed-authority coverage_in_force_on_dos, unsatisfiable on a one-field
correlation key) and on billing_charge_posted (late-fee time gate + waiver_on_file) must be
evidenced on any write of that subject, so no problem of this difficulty writes an adjustment or
a charge; problems are carried by billing_payment_posted (agent card-on-file charge, customer
card payments), billing_refund_issued and billing_statement_issued.
Plan: task 0 = refund tree (credit refund <- returned-payment replacement [customer], card-on-file charge);
      task 1 = final-notice paydown [customer] <- pre-placement cycle statement.
2026-09-24 task0 Step1-2: billing.extended.yaml written (base verbatim + 3 task-0 policies: card-on-file charge,
  pre-placement statement, final-notice paydown); task_tools.py holds the 3 task-0 tools (task-1 tools staged
  for task 1). check_task_tools: TASK TOOL CONTRACT OK. check_extended structural pass (only task-less
  cardinality/coverage messages remain).
2026-09-24 task0 closed: tasks/0.json written (HDHP account in precollection; tree = final-notice paydown [customer]
  <- pre-placement statement <- card-on-file charge; expected 322.52 / 1617.73 / 521.09; baselines 412.75 /
  2095.58 / 1567.74; edge sensitivity: statement without card charge 1250.25, paydown without statement 327.58).
  Fix during gating: replay reported 11 dangling FKs (empty-string parent ids) -> absent parent refs seeded as null.
  Per-task gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, SCOPE OK.
2026-09-24 task1 closed: tasks/1.json written (Commercial PPO/POS account with a duplicate-payment credit and two
  returned payments; tree = credit refund <- returned-payment replacement [customer]; expected 322.60 / 433.35;
  baselines 242.40 / 355.67; refund without the replacement 110.75).
  Fix during gating: check_compute flagged plan_offset (payplan history read touched no rows: no missed
  installments) -> tier (a) now also requires an installment paid in the six months (rule, compute, basis,
  ladder, trace updated together); re-run green.
  Incident: temporary authoring scripts in the shared scratchpad root were deleted by another process mid-task;
  outputs on disk were intact; authoring resumed from a private scratch subfolder.
2026-09-24 FINAL (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite branches mean 57.00, steps mean 15.00, history_rows_max 42, branches_max 74), GROUNDING OK,
  CACHE-DIFF INFO (optional), SCOPE OK. Traceability skipped (needs the published KB).
  Coverage: task0 = {card_on_file_charge, pre_placement_statement, final_notice_paydown}; task1 =
  {returned_payment_replacement, credit_refund}; tools pairwise disjoint; every policy claimed once.
2026-09-24 END erl-task-instantiate d=patient_balance_and_coverage_resolution M=2
2026-09-25 START round=2 rework (audits/policy_task/patient_balance_and_coverage_resolution r1: F-1, F-2, F-3, T1-F1 + observations)
  F-1: paydown returned_12m, replacement returns/returned/latest bindings, refund returns_12m now count only reversals with
       payment_method check or ach; replacement rule/ladders say "check or ACH" throughout; refund prerequisite condition too.
  F-2: card-on-file covered_lines (threshold substitution) replaced by notice_anchor (method: date of service /
       first posting of the encounter / own posting date); mail tier removed; task 0 values unchanged (322.52).
  F-3: refund posting sentence names the payment that created the credit among charges never hit by a returned
       check/ACH payment; states cash-to-check (O-4). Task 1 object/anchor unchanged (2026-08-03 HSA payment).
  T1-F1: task 1 seeds a 2025-08-19 check return (made good) and a 2026-06-24 card chargeback (re-paid) as near-misses.
  T1-O2: task 1 deductible_remaining_usd 118.40 -> refund 464.95 (baseline 355.67; without replacement 142.35).
  O-9: no-show open part defined with adjustments. T0-O2, T0-O3, T1-O3 wording fixed in task files.
  Gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.
2026-09-25 END round=2
