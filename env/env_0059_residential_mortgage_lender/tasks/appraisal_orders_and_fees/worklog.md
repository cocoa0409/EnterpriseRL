# appraisal_orders_and_fees — instantiation worklog (M=2)

## Step 0 draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6, 6]
- task 1: prerequisite_problems=1, factor_counts=[4, 6]

## Scope plan (claimed incrementally)
- task 0: root `appraisal_ext_update_inspection_charge` (owner=user, borrower authorises the Form 1004D update charge on her own card, 6 factors)
  <- prerequisite `appraisal_ext_size_value_addon` (owner=agent, complexity add-on booked on the gla_surcharge line, 6 factors), value_input.
- task 1: root `appraisal_ext_final_inspection_charge` (owner=user, borrower authorises the Form 1004D completion re-visit charge, 6 factors)
  <- prerequisite `appraisal_ext_late_rush_refund` (owner=agent, refund of a rush charge whose promise was missed, 4 factors), value_input.
- Routing note: base gives the borrower two own decisions (cancel, ROV submission), neither of which carries a numeric
  field the schema can persist; every problem must carry a computation, so the customer's own write in each tree is the
  borrower authorising a card payment for a new 1004D service on the order (appraisal_fee_charged, an event this
  difficulty claims). Charges collected on the card already on file for the original order stay agent-booked
  (complexity add-on); refunds stay agent actions.

## Task 0 — closed
- Policies: appraisal_ext_size_value_addon (agent, 6 factors, expected 575.00, baseline 250.00) -> appraisal_ext_update_inspection_charge (user, 6 factors, expected 820.00, baseline 250.00); value_input edge on billed_addon (skip -> 700.00).
- Revisions: replay red (dangling FK on '' preapproval_id; closure missing 3 noise rows: 2 loan_fee_ledger + 1 lock_requests) -> empty FKs set to null in seed and tools, noise rows dropped -> REPLAY OK.
- Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK only on the two unlock tool names (no KB yet).

## Task 1 — closed
- Policies: appraisal_ext_late_rush_refund (agent, 4 factors, expected 105.00, baseline 150.00) -> appraisal_ext_final_inspection_charge (user, 6 factors, expected 90.00, baseline 200.00); value_input edge on rush_miss_refunds (skip -> 120.00).
- Revisions: (1) lateness factor had no record-reading binding (gate: evidence) -> endpoint method now decides the end date (late_endpoint) and the lateness factor owns the DAYS count. (2) suite history max was below 8 with the report-age add-on -> replaced by standing_outlay_tier (SUM over every charge and refund on the order); history_rows task 1 = 9. (3) first completion visit seeded at the amount the rule gives on 2026-09-28 (120.00) so the history teaches the charter's own algorithm. (4) access deduction for two trip charges set to 30 points so refund (105.00) and charge (90.00) do not coincide.
- Per-task gates: all OK (TRACEABILITY only unlock names).

## Difficulty-level closure
- Coverage: task 0 {size_value_addon, update_inspection_charge}, task 1 {late_rush_refund, final_inspection_charge}; tools disjoint; every policy claimed once.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 34.0, steps mean 12.5, history max 9, branch max 35), GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; TRACEABILITY NOT OK only for the four unlock tool names (KB not yet rendered).
- Validator traps checked: frozen_time '2026-10-14 10:20:00 EDT'; no banned clock/random/uuid substrings in task_tools.py; every rw=write tool calls ctx.create/ctx.update itself; no factor id is a substring of a tool name.
- Prerequisite sentence directions: task 0 negated ('not fixed until'), task 1 affirmative ('fixed only after').

## Rework round 2 (audit round 1: audits/policy_task/appraisal_orders_and_fees/)
- F-1 (RED): update charge's reconsideration part removed (base: ROV is never charged); replaced by value_cushion_tier (market-conditions refresh when the appraised value clears the loan file's property value by < 1 / 1-3 percent). Task 0: reconsideration read and rows dropped; update charge 820.00 -> 880.00; skip-edge 760.00; terminal fee_balance 2605.00.
- Class sweep across all four policies: O-1 completion charge excludes reports past validity at the scheduled closing, combined visit tier = any order subject to completion; O-2 turn_time appraisal-delay sentence declared in the refund overwrite; O-3 add-on nets amounts already on its line; O-4 gone with F-1; O-5 extension read restricted to the file's lock, latest value-changing decision named; O-6 refund owed on days late >= 1 under the counting rule, cancelled / HPML flip / pre-ITP rush left to base full refund; O-7 'scheduled closing date' wording; O-9 HPML flip exclusion in add-on, update and completion charges; O-10 'no stacking' sentence declared in every charge policy, plus the 'rush on request' sentence in update and completion charges; O-11 effort-days condition removed, per-unit area via loan units; O-12 1-2-day arrival tier floored at the living-area part; O-13 access deduction removed (double counted), replaced by extension_cost_points; O-14 re-visit method nets recent reinspection charges; O-T0-1 rationale names site_acreage_tier (now mechanically multi-source). O-8 is a base sentence outside this charter: no action.
- Task 1: refund 105.00 -> 120.00 (lateness 50 + slip 20 + extension 10 = 80 percent); factual-error reconsideration seeded (value_changed 2026-09-16) for history depth (suite history max 8); final inspection charge 90.00 unchanged; terminal fee_balance 1190.00.
- Gates: all OK except TRACEABILITY (four unlock tool names only, pre-render).

## Rework round 3 (render source report render_appraisal_r1)
- Items 1-7 closed in source (charter wording/overwrites); no scored value changed (575.00 / 880.00 / 120.00 / 90.00). Task rationales swept for withdrawn overwrites and band wording.

## Rework round 4 (render_appraisal_r2 + policy audit revision_3 observations)
- O-R3-1 add-on reductions stated as arrival rule + standing-line netting; O-R3-2 extension-cost quantity named 'lock costs the borrower still bears'; O-R3-3 docstrings 'stored rounded to 2 decimal places'. No scored value changed.
