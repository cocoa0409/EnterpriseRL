# worklog — gap_waiver_cancellations_and_claims (env_0072), M=2, round 1 (fresh relaunch)

## Relaunch
- On disk at relaunch: plan.md rev 1 only. Rev 1 replaced (see plan.md "Why revision 1 was replaced"):
  the claim report could not compute a date-of-loss figure (no record carries the loss date before
  the claim row exists), and the denial -> mailed-refund chain needs a paid-off contract whose
  active addendum owes an early-payoff cancellation. New design: claim already reported on first
  notice; every problem is one worksheet figure on that claim row; the borrower's own act is the
  deductible-reimbursement claim with the settlement documents.

## Draws
- task 0: prerequisite_problems=3, factor_counts [6, 4, 6, 6] -> DED Premier 6, BAL 4, EXC Premier 6, BEN 6
- task 1: prerequisite_problems=1, factor_counts [6, 4] -> EXC Plus 6, DED Plus 4

## Trigger table (every event a tool writes, with base triggers)
| tool | owner | write | base triggers | other category? |
|---|---|---|---|---|
| claim_premier_deductible_reimbursement_7815b2b6 | user | update gap_activities claim row: deductible_covered_usd | none (row update; gap_claim_filed's trigger gap:gap_claim_opened is in-category and fired at filing) | no |
| record_claim_balance_at_loss_15fb7d99 | agent | update claim row: balance_at_loss_usd | none | no |
| record_premier_claim_exclusions_258c7293 | agent | update claim row: excluded_amounts_usd | none | no |
| record_claim_worksheet_benefit_931d4ebc | agent | update claim row: benefit_usd | none | no |
| claim_plus_deductible_reimbursement_49e3d00f | user | update claim row: deductible_covered_usd | none | no |
| record_plus_claim_exclusions_41771560 | agent | update claim row: excluded_amounts_usd | none | no |
No decision, refund, cancellation or other-category row is written (gap_claim_decided approved -> contract
credit and gap_refund_issued credited_* -> contract/deficiency are never ours).

## Capability contract cards (one per tool)
- claim_premier_deductible_reimbursement_7815b2b6 — owner user / write. Borrower claims the GAP Waiver Premier 150
  deductible reimbursement with the insurer's settlement documents. Object: the claim record of the reported loss.
  Atomic action: set deductible_covered_usd on that row (round 2). Observable: claim shows the deductible covered.
  Receipt: text with claim reference and amount (USD, 2 dp). No checks, no other field.
- claim_plus_deductible_reimbursement_49e3d00f — same for GAP Waiver Plus 150.
- record_claim_balance_at_loss_15fb7d99 — owner agent / write. Sets balance_at_loss_usd (starting balance). Receipt text.
- record_premier_claim_exclusions_258c7293 / record_plus_claim_exclusions_41771560 — owner agent / write. Set
  excluded_amounts_usd (excluded total). Receipt text.
- record_claim_worksheet_benefit_931d4ebc — owner agent / write. Sets benefit_usd (worksheet benefit, credits nothing,
  decides nothing). Receipt text.

## Method-shape all-pairs table (XF-8)
| factor | pair | distinguishing input / operation |
|---|---|---|
| bl_due_change_count | (a) vs (b) | (a) adds the new next due date and the loss date (second MONTHS term) |
| | (a) vs (c) | (a) reads the change's old/new next due dates; (c) reads only first payment date and loss |
| | (b) vs (c) | (b) counts to the old next due date; (c) to the loss date |
| bl_capped_rate_adjustment | (a) vs (b) | (b) adds a third stage (end date, restored installment) |
| | (a)/(b) vs (c) | (c) is 0; (a),(b) are non-zero on their domain (cap rate < original rate) |
| pd/ud_proof_basis | (a) vs (b) | different inputs (collision vs comprehensive deductible on the proof) |
| | (a)/(b) vs (c) | (a),(b) add a min with the proof deductible; (c) the deductible as deducted |
| ep/eu_addon_basis | (a) vs (b) | (a) reads the issued refund rows; (b) price x (1 - max(day share, mile share)) - claims - fee, min-refund floor |
| | (a)/(b) vs (c) | (c) day-prorated price (no odometer, no claims, no fee) |
| ep/eu_installment_rule | all pairs | three different records: cap-applied installment, cap-ended installment, current scheduled payment |
| bn_excess_share | (a) vs (b) | (a) constant whole excess; (b) remaining installments / term |
| | (b) vs (c) | (c) claim balance / amount financed |

## Decoy / absent-record probe table (XF-11, XF-12) — run on a scratch copy of the task-0 world
| read | decoy or absent case | rule outcome | probe result |
|---|---|---|---|
| latest reported claim (LATEST by activity_date; figures summed by its loss date) | earlier withdrawn hail claim 2026-03-16 (seeded in task 0) | ignored | gold unchanged (seeded) |
| latest accepted proof | a later rejected proof with lower deductibles | ignored (proof_result filter) | unchanged |
| returned payments, last 12 whole months | a return 13 months back | outside window | unchanged |
| force-placed premiums added to the balance | a held_pending_proof_review premium | not counted | unchanged |
| latest due-date change | a change taking effect after the loss | standard count (as the rule states) | BAL 20,841.38 (rule-consistent) |
| service contract | none on the contract | add-on part 0.00 | EXC 1,378.45 (rule-consistent) |
| SCRA cap records | none | no adjustment / scheduled payment | by construction (tier c) |
| next due date after the loss | borrower current at loss | 0 unpaid installments | by construction |
Same-day ties: XLATEST keeps the first row; no two proofs / servicing records share a date in either world.
Known DSL edge (stated in the rule, not hidden): only the contract's LATEST due-date change is read.

## Task 0 — gates (per task, final run below)
- check_extended / task_tools / replay / solvability / compute / grounding / cross_fire: all OK.
- Values: deductible covered 192.78, starting balance 21,073.63, Premier excluded total 1,634.62, worksheet benefit 5,270.86.
- Edge deletion: no balance -> benefit 0.00; no exclusions -> 6,742.02; no reimbursement -> excluded 1,827.40 (benefit 5,097.36).
- Revision: history floor (check_compute) failed with LATEST-only claim reads -> claim amounts summed by the claim's
  own loss date; BAL guard "a starting balance is set only for a reported claim". history_rows_max 4 < 8 -> seeded the
  withdrawn March hail claim (a real decoy); now 8.

## Task 1 — gates
- All per-task gates OK. Values: Plus deductible covered 101.25, Plus excluded total 1,240.02; no reimbursement -> 1,341.27.
- Revision: add-on factor read vsc history with no rows -> seeded the 2025-10-02 authorized drive-axle claim (claims paid 335.00).

## Final gate run (no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
(check_traceability runs after the KB render; CACHE-DIFF info only.)

REWORK round 1: gates 7/7 green

## Rework round 2 (policy-task audit revision_1: C1, C2, C3, C4, C5, C6, C8; task-1 finding 5; O1, O3, O5, O10)
- Charter redesign recorded in plan.md "Revision 3"; per-item closure in rework_claims_r2.md; adversarial probe table
  (every read: decoy, absent, cancelled/prior/second record, same-day tie; every edge: zero, None, negative, date
  difference 0, boundaries) appended to plan.md.
- Worlds regenerated with their owning charters' pricing: task 0 two unpaid installments at the loss, frozen
  2026-10-05 (below charge-off), settlement ACV per the letter, service-contract refund inside 30 days; task 1 second
  fee-assessed extension, two unpaid installments at the loss, service-contract refund inside 30 days.
- Every factor of all six computations moves its result when its baseline is substituted (check_compute), all-baseline
  results differ from gold; rationale, closures, necessity text and traces regenerated from the new compute.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 2: gates 7/7 green

## Rework round 3 (policy-task audit revision_2: C1, C4, C9, C10; R2-O1, R2-O3, O6)
- Closed: C9 (value floor is a baseline quantity; bn_value_floor sets its percent, bn_floor_value its vehicle value),
  C10 (every LATEST read states its same-day tie; latest premium by billing-period start), R2-O1 (Premier past-due
  relief by count only), R2-O3 (pending-refund tier exact, only when the proof starts inside the latest billing period),
  O6 (post-loss late charges leave the fee part of both excluded totals). Worlds unchanged (no re-seed needed: every
  change is to policy text and compute); both bundles regenerated, values and sensitivities re-derived with
  check_compute's evaluator; probe table extended in plan.md; per-item record in rework_claims_r3.md.
- NOT closed: C1 / C4. On the frozen blueprint option (b) has no numeric borrower write besides the claim row's
  reimbursement, and task 0's tree needs all four claim-row fields; option (a) tops out at five record-driven
  reimbursement factors (proof in force, coverage, window start, window length, SCRA tolling) against the Premier draw
  of six. pd/ud keep their round-2 factor sets pending a ruling (analysis in rework_claims_r3.md).
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 3: gates 7/7 green

## Rework round 4 (policy-task audit revision_3: C1 incl. the bn floor default, C4; coordinator ruling on round 3)
- C1: all eight reimbursement schedule shares struck; pd (6) and ud (4) rebuilt on claim-timeliness and policy-at-loss
  terms with a declared, self-naming late_documents overwrite scoped to the reimbursement; duty extension worded as a
  company accommodation on recorded active-duty dates. bn baseline floor age-limited (60 percent under 24 months, none
  after); bn_value_floor ladder back to 80 / 70 / no floor.
- C4: pd 3 method + 3 parameter, ud 1 method + 3 parameter; draws unchanged. Reimbursement edges now action form.
- Re-seed (ids kept): task 0 claim report date, deductible withheld, recorded duty end, new later-starting policy proof;
  task 1 proof deductibles, deductible withheld, recorded duty end, new later-starting policy proof; personas, closures,
  traces, rationale and seed checks regenerated; every factor moves its result (check_compute); probes in plan.md.
- Round-3 closures kept: C9, C10, R2-O1, R2-O3, O6.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 4: gates 7/7 green

## Rework round 5 (policy-task audit revision_4: C1, C2, C4, C11, C12)
- Task 1 re-treed per the coordinator route: Plus reimbursement and tool retired; root Plus excluded total is the
  borrower's own confirmation (owner=user), capped at and waiting on a new Plus starting balance (policy + tool;
  starting balance split by plan); world re-seeded from origination; all factors bear weight; persona aligned.
- C11: task 0 customer duty end 2026-08-19 (cap ended 2026-08-20, the day after); task 1 duty 2026-09-14 / cap 2026-09-15.
- Task 0 Premier reimbursement: not closed (C1, C2, C4, C12) — 4-problem claim tree needs a 4- or 6-factor deductible
  computation the frozen blueprint cannot supply with real terms; round-4 set kept to hold the bundle valid; details in
  rework_claims_r5.md.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 5: gates 7/7 green

## Rework round 6 (policy-task audit revision_5: C11, C13; coordinator structural ruling on task 0)
- Task 1 re-treed: root Plus worksheet benefit (borrower's acceptance) starting from the Plus starting balance (value
  edge); Plus exclusions itemized in place; exclusions policy and tool retired; world re-seeded from origination and
  priced by the contract documents (due-date shift, extension allowances, Georgia late-charge and extension charges,
  SCRA terms); every factor bears weight.
- Task 0: world-type change not possible on this schema (rework_claims_r6.md); left as round 5 pending a decision.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 6: gates 7/7 green

## Rework round 7 (coordinator's final ruling on task 0; task 1 untouched)
- Task 0 placement per ruling (reimbursement 4; starting balance, excluded total, benefit 6). Reimbursement rebuilt on
  record-backed caps and an allowance-test method; starting balance gains placed premiums and account interest; value
  floor line at 36 months; world re-seeded from origination with every contract row per the published documents.
- Task 1 bundle byte-identical to round 6.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 7: gates 7/7 green

## Rework round 8 (audit revision_7: C1, C3, C4, C14, C15; task 1 untouched)
- Reimbursement: allowance read inside pd_allowance_test (method); proof-naming count a plain shared binding;
  pd_contract_allowance replaced by pd_deductible_counted (param). Starting balance: placed premiums a three-formula
  method with a gross baseline; carried-unpaid-interest tier dropped; payment interest per-diem / split at a cap change /
  none on the principal in place before the post-loss service-contract refund credit.
- Every factor re-probed solo on task 0 (all move the result); probes in plan.md; per-item record in rework_claims_r8.md.
- Task 1 and task_tools.py byte-identical to round 7.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 8: gates 7/7 green

## Rework round 9 (audit revision_8: C1, C4 on the reimbursement; task 1 untouched)
- Deductible counted = the deductible the primary insurer actually deducted, up to the plan maximum; never a deductible
  not withheld. pd_deductible_counted removed; new pd_proof_standing (param); pd_policy_at_loss now reads the policy
  on file as its standard; declarations check only lowers the withheld figure. No re-seed.
- Every pd factor re-probed solo on task 0 (all move the result); probes in plan.md; per-item record in rework_claims_r9.md.
- Task 1, task_tools.py and the bl/ep/bn/bp/pb policies byte-identical in effect to round 8.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 9: gates 7/7 green

## Rework round 10 (render-source scan render_r1.md: S1, S2, S3, docstring note)
- S1: Plus worksheet benefit declares its own overwrite of the LTV-excess clause; Premier tail names the Plus case.
- S2: payment interest at the rate in force on each day for any number of cap changes in the period (rule + compute).
- S3: whole-months definition in every month-counting policy; post-loss late-charge window stated as computed.
- task_tools.py docstrings claim only the body's rounding. No figure changed; tasks/0.json and tasks/1.json unchanged.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 10: gates 7/7 green

## Rework round 11 (KB audit kb_round1: S1, S2, P1)
- S1: the withdrawal is a status transition with no activity row; seed-consistency text says so (no row changed).
- S2: task 0 CPI tracking moved to lapse notice at the 2026-09-18 policy expiry with a first lapse notice 2026-09-21
  per docs/cpi; no figure reads either.
- P1: pd_proof_standing decides only which review results count; combination stated as one plain sentence; the insurer
  factor and the allowance test own their counts.
- Bounded pass over every cross-category seeded row of both worlds against the published docs: no other change.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 11: gates 7/7 green

## Rework round 12 (KB revision_2: K1, S3; task 1 untouched)
- Route (b): insurer and review-standing choice merged into pd_policy_at_loss (complete selections); combination
  sentence and pd_proof_standing removed. Freed slot: pd_policy_disclosure (method; bar/bound by when the policy that
  paid was put before the company) against a new standard sentence; pd_allowance_test keeps the bound tiers.
- Every pd factor re-probed solo on task 0 (all move the result); probes in plan.md; per-item record in rework_claims_r12.md.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 12: gates 7/7 green

## Rework round 13 (audit revision_12: C14, C4; task 1 untouched)
- Coordinator route: softened baseline (withheld up to the plan maximum, one declarations cap; no borrower-maximum bar);
  selectors pd_policy_at_loss (merged) and pd_paying_coverage; methods pd_allowance_test (cap / void / none) and
  pd_policy_disclosure (no bound / borrower maximum / policy on file), each owning its reads.
- Solo substitutions all move task 0; pair probes over twelve worlds show no factor inert through another single
  factor's tier; limitation at full baseline disclosed in rework_claims_r13.md.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 13: gates 7/7 green

## Rework round 14 (audit revision_13: C14, C4; task 1 untouched)
- pd_policy_disclosure replaced by pd_loss_schedule (Premier schedule maximum by the claim's loss type: collision ->
  plan maximum, unrecovered theft -> 500.00, otherwise 250.00 = standard), capping the baseline directly.
- T1 and T2 verified for all four reimbursement factors (table in plan.md); no re-seed; gold unchanged.
- Final gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK /
  GROUNDING OK / SCOPE OK.

REWORK round 14: gates 7/7 green
