# worklog — contract_payments_fees_and_servicing (env_0072), M=2

## relaunch (fresh agent after account cut)
- Read plan.md (predecessor), XF_recipe.md (all 31 points), blueprint, contract charter, schema, share tools.
- plan.md rewritten to v2 (factor split, closed recovery case, returned-fee subject, open online request).

## task 0 — hardship extension tree (closed)
- Draw: prerequisite_problems=2, factor_counts=[6,6,4] -> months 6, fee 6, late charge 4.
- Tools: assess_late_charge_1a8e6313 (agent), sign_extension_agreement_772d986b (user), grant_hardship_extension_883d335d (agent).
- Gold: late charge 7.68 (baseline 25.00), months 2 (baseline 1), fee 43.98 (baseline 30.00).
- Revisions: prerequisite sentences reworded (code tokens request_type / next_due_date); due-date allowance replaced
  by payment-activity allowance (history floor of check_compute); dealer parent rows dropped, dealer_agreement_id null
  (replay closure).
- Per-task gates (task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## task 1 — payoff tree (closed)
- Draw: prerequisite_problems=2, factor_counts=[6,6,5] -> returned-item fee 6, payoff statement 6, borrower payoff 5.
- Tools: assess_returned_payment_fee_c98c0726 (agent), issue_payoff_quote_f4f38627 (agent), authorize_payoff_payment_7f0b790b (user).
- Gold: returned fee 42.05 (baseline 25.00); statement 8554.01 good through 2026-10-31 (baseline 8537.99);
  payoff 8529.01 by ach_agent (baseline 8493.11). Skip-fee: statement 8511.96, payoff 8486.96.
- Revisions: seeded quote row and the quote tool write service_request_id null (replay FK gate flagged "").
- Known weakness for the audit: the payoff's five factors are company funds-final hold conventions (little real
  variability exists in a posting-date payoff); returned-history evidence is reused by the fee, statement and payoff.

## final gates (difficulty level, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
SCOPE OK
- Scratch /tmp/contract_payments_fees_and_servicing_0072/ (generators, harness, builders) deleted.
REWORK round 1: gates 7/7 green

## rework round 2 (policy-task audit revision_1: task0=RED task1=RED, CW-1..CW-9)
- Read 0.md, 1.md, _difficulty.md in full and XF_recipe.md again; claims per item in rework_claims_r2.md; probe table in plan.md (v3).
- Charter: months (signing date, rolling windows, due-date counts, generic assembly); fee (generic self-contained
  assembly, signed-not-applied prerequisite sentence, unique recovery reads); returned-item fee (tie rule, bank-charge
  recovery replaces late-return handling, state cap, zero never booked); statement (insurance-lapse and remittance
  factors replace referral and repeat-statement, anchor relabelled parameter, rolling windows, tie rule); payoff
  (review-day good-through framing, Monday-consistent weekend days, referral review replaces autopay hold, tie rules).
- Seeds regenerated: single late charge per delinquency stretch in both worlds; T0 amount financed 21490.00 (no tie);
  T1 moved to Tampa FL with a CPI record. Task JSONs fully regenerated (traces, closure, contract, rationale).
- Gates (difficulty level): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Scratch deleted.
REWORK round 2: gates 7/7 green

## rework round 3 (audit revision_2: task0=PASS task1=RED charter=N-1,N-2)
- Minimal charter edits: statement remittance-method rule (returned-or-not count; complete last tier); "waived or not" stated on late-charge counts and the fee's late-charge credit. No figure moved; task 1 traces/rationale and task 0 rationale note updated. Claims in rework_claims_r3.md; probes in plan.md.
REWORK round 3: gates 7/7 green

## rework round 4 (audit revision_3: task0=PASS task1=RED charter=N-3)
- Minimal edit: failed-payment offset states "waived or not" (compute unchanged); sweep of all fee/payment row reads confirms every one states its status. No figure moved. Claims in rework_claims_r4.md.
REWORK round 4: gates 7/7 green
