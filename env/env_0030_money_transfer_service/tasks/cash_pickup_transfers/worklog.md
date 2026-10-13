# cash_pickup_transfers — instantiate worklog (M=2)

## Step 0 pre-check (difficulty level)
- draw_counts --tasks 2:
  - task 0: prerequisite_problems=1, factor_counts=[4, 5]
  - task 1: prerequisite_problems=3, factor_counts=[5, 4, 6, 5]
- Base gate survey (check_solvability requires every gate whose applies_to meets the write subject):
  - cash_fee_refunded writes are unusable: full_refund_window (cancellation-only time gate) and
    available_late (on-time promise) both apply to every fee refund; no honest world satisfies both.
  - cash_name_corrected carries spelling_only with authority=mixed over a single correlation key
    (cash_transfer_id) — mechanically unsatisfiable; usable only if an extended policy supersedes the
    spelling sentence (accent-insensitive refinement, a genuine product change for Latin names).
  - Clean writes: cash_fee_charged (policy_scope x3), cash_paloma_credit / cash_reissued (policy_scope),
    cash_remedy_chosen (error_found_first), cash_pickup_reactivated (reactivation_window, reactivation_cap).
  - fx_rate_sheet is not a category table: compute cannot read mid-market rates (no requote policy).
  - Booking cannot be a computation target (target holding must exist before the write).
- User-owned numeric writes available: customer's fee payments (payment authorisation) and the
  customer's remedy choice (which by base trigger performs the re-issue).
- Allocation (scopes disjoint, all 6 policies covered):
  - task 0 (2 problems): shortfall re-issue choice (USER, 4 factors) -> Paloma shortfall credit (AGENT, root, 5)
  - task 1 (4 problems): reactivation fee payment (USER, 5) -> reactivated window (AGENT, 6);
    reactivation fee payment -> name-correction fee payment (USER, 4); both -> name correction with
    window extension (AGENT, root, 5)
- Tool names (uuid8 minted per tool, frozen):
  choose_shortfall_reissue_92bb83b1 (user), book_shortfall_credit_cb14652e (agent),
  pay_reactivation_fee_6d9bfacd (user), reactivate_expired_pickup_d4e94bda (agent),
  pay_name_correction_fee_e426b8ef (user), record_name_correction_726c5192 (agent)
- Identifier band k=3: phones 555-0140..0159, id_document_last4 starts with 3, every minted reference
  (confirmation_number, pickup_reference, doc_reference, order/payout/batch/deposit refs) numeric part starts with 3.

## Task 0 — closed
- Tree: cash_ext_shortfall_reissue_window (USER) -> cash_ext_shortfall_credit (AGENT, root); value_input edge via the uplift.
- Gold: reissue_window_days=31 (baseline 30), amount_usd=16.68 (baseline 10.72); edge skip -> 15.82.
- Per-task gates: extended OK, task_tools OK, replay OK (closure 38/38), solvability OK, compute OK, grounding OK, cross_fire OK.
- Revisions: dropped unread rate-sheet/rewards-ledger rows, added recipient & bank-transfer reads; helpers moved into a class.

## Task 1 — closed
- Tree (diamond): reactivation fee (USER) -> {reactivated window (AGENT), correction fee (USER)} -> name correction extension (AGENT, root); value edges: extension<-window (days left), correction fee<-reactivation fee (bundle share).
- Gold: 3.04 / 25 / 2.00 / 9 (baselines 4.99 / 30 / 5.00 / 0); swap of the two parallel writes gives the same hash.
- Per-task gates all green (replay closure 47/47).
- Revision: task-0 re-issue window prose renamed to "re-issue network/loyalty/tenure days" and "re-issue window base" so quantity names stay unique across the charter.

## Difficulty-level closing
- Final gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (38/38, 47/47); SOLVABILITY OK;
  COMPUTE OK (suite means branches=38.50, steps=16.00; history_rows_max=9; branches_max=54); GROUNDING OK;
  CACHE-DIFF INFO (no cache trap chosen); SCOPE OK. check_traceability deferred until the KB is published.
- Coverage: 6/6 extended policies claimed, scopes and tools pairwise disjoint; each task calls >= 1 owner=user tool.
- Authoring scripts lived outside the repo (/tmp) and were deleted.

## Round 2 — audit policy_task/cash_pickup_transfers
- F-1 / T1-F1 (RED): replaced the four constant-swap "method" factors of task 1 with genuine method factors
  (reactivation_lateness_charge per-day/flat/none; reactivated_lateness_base per-day shortening/flat shortening/full;
  correction_lateness_charge per-started-week/flat/none; correction_gap_method selection-with-minimum / last-day-excluded
  count / plain count). Gold 3.04/25/2.00/9 -> 3.09/22/1.90/11; all task-1 assets re-propagated; swap run still identical.
- Observations acted on: O-1 (Rewards factors -> cross_difficulty null, 5 factors), P-1 (edge A and C effect texts
  generalised), P-2 (edge C condition matches the binding), T0-O1 / T1-O1 (tenure no longer called multi-source).
- Not acted on: O-2 (tenure ladder shape, plausible as published), O-3 (zero-amount charge, consistent), S-1 (base
  sentence, extended sentence carries the edge), E-1 (gate snapshot formatting; this run prints both replay rows).
- Gates (full run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; traceability deferred.

## Round 3 — audit revision_2
- F-1 rev2 / T1-F1 rev2 (RED): correction_gap_method (floor/offset of one formula) replaced by correction_guarantee_anchor:
  guarantee anchored at the later of the current last day and the correction day plus days lost since the latest name
  refusal (>=2 refusals) / at the later of the current last day and the correction day (1 refusal) / at the correction
  day as a top-up (none). Extension 11 -> 32; anchor baseline 10; edge D skip 58.
- O-4: correction lateness per-started-week accrual now counts weeks beyond the 15 middle days at 0.05/week, monotone
  with the flat 0.25 tier. Correction fee 1.90 -> 1.80.
- Task 0 untouched (PASS); values 31 / 16.68 re-verified.
- Gates (full run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; traceability deferred.

## Round 4 — audit revision_3
- N-1 / T1-C1 (RED): correction_guarantee_anchor read days_left only as MX(0, -days_left) under the refusal tiers, so
  edge D carried only the expired-vs-collectable state. Replaced by correction_extension_method, every tier reading the
  days left through the top-up MX(0, guarantee - days_left): >=2 name refusals -> larger of top-up and days lost since
  the latest refusal; 1 refusal -> top-up plus days lost; none -> top-up alone. Extension 32 -> 59; window
  substitution 7/22/25/30 -> 74/59/56/51 (edge D carries the window value); skip 107.
- F-1 stays closed (distinct algorithms/inputs per tier); O-4 untouched (correction fee 1.80).
- Task files touched: tasks/1.json (content). tasks/0.json content untouched; replay_tasks rewrites db_closure fields in
  both task files on every full run, which is why the auditor saw 0.json's hash move.
- Gates (full run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; traceability deferred.
