# paycheck_advance_servicing — difficulty worklog (erl-task-instantiate)

Category: advance (Pocketwire Advance). M = 2.

## Step 0 — difficulty pre-check
- Draws (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=1, factor_counts=[6, 6]
  - task 1: prerequisite_problems=1, factor_counts=[5, 4]
- Base closes: lifecycle, 1 account (outstanding), 16 events, 10 base policies; share tools give
  find_customers / verify_customer_identity (K=3) / find_advance_lines / find_advance_ledger /
  find_wallet_accounts / find_wallet_transactions / find_card_accounts / find_card_transactions.
- Cross-category trigger constraints (principle D): advance_disbursement to personal_balance and
  advance_repayment by autopay_personal_balance / manual_personal_balance fire wallet events, so no
  task tool may write those combinations. Usable customer-owned writes: a disbursement to an
  external debit card, a manual repayment by debit card (manual_debit_card).
- Scope plan (pairwise disjoint, covers all extended policies):
  - task 0: late fee assessment (agent, state_due) -> debit-card repayment (user, on_request)
  - task 1: payroll-delay late-fee relief (agent, state_due) -> new advance with its flat fee (user, on_request)

## Task 0 — closed
- Tree: advance_ext_largest_advance (root, user, request_advance_00c9f515) <- value_input/state-form edge <-
  advance_ext_payroll_delay_relief (agent, state_due, grant_payroll_delay_relief_50112cf3).
- Factors 6 + 6 (draw [6, 6]); cross-difficulty: wallet (deposits, plan, account age), card (tier, purchases).
- Gold: relief 1.80 on the 3.00 June late fee; largest advance 305.00 (285.00 if the relief is skipped), fee 9.00,
  due 2026-10-22.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (closure 76/76), SOLVABILITY OK,
  COMPUTE OK, GROUNDING OK, SCOPE OK; cache-diff info only.
- Revision: authoring scratch files were wiped from the shared scratchpad by another agent; rebuilt the helper in
  this directory's _authoring/ (to be deleted at close), ids recovered from tasks/0.json on disk.

## Task 1 — closed
- Tree: advance_ext_card_repayment_share (root, user, repay_advance_by_card_db2e846d) <- value_input/state-form edge
  (negated direction) <- advance_ext_late_fee_assessment (agent, state_due, assess_late_fee_a649c20a).
- Factors 5 + 4 (draw [5, 4]); cross-difficulty: wallet (deposits, plan).
- Gold: late fee 0.62 for period 1 on the advance due 2026-09-30; card repayment 148.77 (148.32 if the fee is skipped).
- Revision: collection_credit factor owned no record-reading binding -> added advance_principal to its bindings; re-ran OK.

## Difficulty close
- Coverage: 4 extended policies, each claimed by exactly one task; 4 task tools, disjoint per task; both trees
  contain an owner=user write; prerequisite sentences: task 0 affirmative ("only after"), task 1 negated ("not ... until").
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite means branches 33.50 / steps 11.00; history_rows_max 25; branches_max 38), GROUNDING OK, SCOPE OK,
  CACHE-DIFF info only (its value field amount_usd does not exist in this schema, so it reports 0.0 as the event total;
  the seeded owed amounts 0.00 and 206.00 equal the ledger sums). check_traceability deferred until the KB is rendered.

## Rework round 2 (audit: audits/policy_task/paycheck_advance_servicing/)
- F-POL-1: advance_ext_largest_advance now also supersedes advance_agg_outstanding "and their remaining principal plus the
  new advance may not exceed the effective limit." and advance_disbursement_rules "The amount is at least min_advance_amount
  and a whole multiple of advance_increment, within advance_agg_outstanding."; two new rule sentences make the computed
  largest advance the ceiling (concurrency still inherited). Task 0 amount 305 now unique; solvability/tracing/dossier updated.
- F-FAC-1: card_multiplier (relief), card_uplift (largest advance), arrears_timing (card share) now select different
  formulas per tier (per-purchase credit / per-purchase room / per-day points vs a multiplier). New gold: relief 1.76,
  largest advance 305 (unchanged), card repayment 144.63; all sensitivities, closures and dossiers re-derived.
- F-OBS-2, F-OBS-6: relief rule restates the surviving customer-requested courtesy waiver and the cancellation-window waiver.
- F-OBS-3: late-fee rule books a period only while the advance still has unpaid principal (compute returns 0 otherwise).
- F-OBS-4: lateness-record ladder reworded to "at most one late fee in the twelve months" (= compute).
- F-OBS-7: card-share rule restates the base bounds for every other manual repayment.
- Not changed (observations without scored consequence): F-OBS-1 (blueprint claim list is frozen), F-OBS-5, F-OBS-8, F-OBS-9.
- Full gate block re-run: all OK (check_traceability deferred to the KB step).

## Rework round 3 (KB render gate snapshot advance_render_r1)
- Factor id `payroll_delay` of advance_ext_payroll_delay_relief renamed to `collection_lag` (it was a substring of
  grant_payroll_delay_relief_50112cf3, which the hub carries verbatim). Semantics, bindings, figures and tools unchanged.
- tasks/0.json: 4 factor-id references updated (factor_trace, factor_sensitivity, design_rationale x2); tasks/1.json: none.
- Checked: no other factor id is a substring of any task tool name or extended policy id.
