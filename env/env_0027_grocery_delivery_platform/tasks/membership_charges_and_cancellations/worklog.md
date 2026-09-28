# Difficulty worklog — membership_charges_and_cancellations (category: membership), M=2

## Step 0 — difficulty pre-check (done)
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/membership.yaml,
  db_schema.json, share_tools.py (identity: find_customers -> verify_customer_identity, K=2 of phone/email/dob/zip).
- Draws (scripts/draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=3, factor_counts=[4, 4, 5, 6]
  - task 1: prerequisite_problems=1, factor_counts=[4, 6]
- Numeric writes the membership charter supports: renewal_retry capture (reinstatement), renewal capture on
  resume, plan_switch capture, fee refunds (full_unused / prorated_annual / duplicate_charge), pause length,
  credit-back earning / credit lapse. Cancellation and auto-renew toggles carry no number, so they cannot be a
  scored problem (every gold write carries a computation). A duplicate-charge refund is always the whole second
  capture (no load-bearing factor possible), so it is not claimed.
- Ownership (final): paying an outstanding past-due fee with the member's card is the member's own payment
  (user); confirming the early end of an annual term is the member's own decision (user). Refunds, plan
  switches and pauses are booked by the agent, as the blueprint states.

## Design (claimed scope) — revision 2 (supersedes revision 1)
Symptom: revision 1 used credit-back earning/lapse writes; the compute DSL can only aggregate by equality filters
and month windows, so a per-order earning or a per-earning lapse cannot be selected generically (rule/compute
equivalence would break), and those event types are outside this difficulty's claim. Root cause: DSL + claim.
Change: every problem is a claimed membership write (fee charge, fee refund, pause).
- task 1 (1 prerequisite; draws [4,6]): Student Monthly member, past due, wants to move to Cartwise+ Annual.
  - root: annual upgrade charge (plan_switch capture; agent; 6 factors)
  - <- past-due settlement (renewal_retry capture; USER pays; 4 factors) [value_input: the settled capture is
    the fee the unused-days credit is taken from; state: active]
- task 0 (3 prerequisites; draws [4,4,5,6]): Family Annual member (upgraded from Annual mid-year) asks for a pause;
  annual plans cannot pause, the published route is an early move to Cartwise+ Monthly.
  - root: pause length (agent; 6 factors) <- early move to monthly charge (agent; 5 factors) [value_input]
  - move charge <- unused-months refund of the charge that opened the annual term (USER confirms ending the
    annual term early; 4 factors) [value_input]
  - move charge <- carried-value refund against the earlier charge whose unused value was carried into the term
    (agent; 4 factors) [value_input]
- Not claimed: duplicate refund (always the whole second capture), early resume, cancellation/auto-renew.

## Progress log
- (entries appended below as each piece lands)
- Step 2 (tools, difficulty-wide): task_tools.py written with six tools, each uuid8 drawn separately:
  confirm_annual_term_early_end_0b7355fe (user), refund_carried_term_value_822a3886 (agent),
  move_annual_plan_to_monthly_dc3bc730 (agent), book_membership_pause_b6aef13b (agent),
  settle_past_due_membership_fee_b438dc6f (user), upgrade_membership_plan_10b03fa3 (agent).
  check_task_tools.py -> "TASK TOOL CONTRACT OK". No tool checks status, timing or any prerequisite.
- Design revision 3: task-0 member is on Cartwise+ Annual (Family Annual cannot switch to Monthly: its
  allowed_switch_targets are Annual/Premier). The annual term was opened by a plan switch from Monthly on
  2026-07-10, so the value carried from the last monthly charge is part of the term.
- Task 0 / Step 1 (policies on disk): membership.extended.yaml = base copied verbatim + four extended policies
  (membership_ext_term_charge_refund 4 factors, membership_ext_carried_value_refund 4, membership_ext_move_to_monthly_charge 5,
  membership_ext_pause_length 6 = draw [4,4,5,6]). Helper functions of task_tools.py moved into a class (the gates
  count every top-level function as a tool). check_extended: policy structure clean; only the missing tasks and
  the two task-1 tools remain open.
- Task 0 / Step 5 pre-run (scratch evaluator over the seeded world, writes simulated in topological order):
  term refund 69.91 (factor baselines 66.01 / 62.52 / 66.92 / 65.92; all-baseline 49.04); carried refund 4.86
  (3.68 / 4.29 / 4.36 / 1.67; all-baseline 0.00); move charge 2.25 (3.87 / 4.87 / 3.25 / 3.25 / 2.75; all-baseline
  8.18; skipping either refund -> 0.00); pause length 97 days (all-baseline 90).
- Task 0 closed on disk (tasks/0.json). Per-task gates: check_task_tools OK, replay_tasks OK (after dropping empty
  order_id/batch_id keys that the FK check read as dangling), check_solvability OK, check_compute OK (19 factors,
  8 cross-difficulty, handling-time recompute equals gold 69.91 / 4.86 / 2.25 / 97), check_grounding OK,
  check_cross_fire OK. check_extended per-task only flags the two task-1 tools not yet named by a policy.
- Manual values gates (task 0): the tree length is 3 hops with a fan-in on the move charge; the only customer
  write is the term-opening confirmation (ending the annual term is the member's own decision); persona volunteers
  only the pause request and the July move to the yearly plan; every factor tier rests on seeded rows; the
  two refunds commute (neither reads refund rows). Known weak spot: the waiver/handling/credit ladders are
  published-rule inventions layered on base mechanics; each is declared in overwrite where it departs from base.
- Task 1 / Steps 0-1: draw prerequisite_problems=1, factor_counts=[4, 6]. Occupied by task 0: the four
  pause-route policies and their tools. Claimed: membership_ext_past_due_settlement (4 factors, user tool
  settle_past_due_membership_fee_b438dc6f) and membership_ext_annual_upgrade_charge (6 factors, agent tool
  upgrade_membership_plan_10b03fa3); both appended to the extended charter. Scratch evaluation on the seeded
  Student Monthly world (past due since 2026-09-17): settlement 2.89 (baselines 3.94 / 3.28 / 3.14 / 3.19;
  all 4.99); upgrade 66.81 after the settlement (67.48 / 86.61 / 71.81 / 68.31 / 68.81 / 67.81; all 96.78);
  without the settlement the upgrade computes 69.70 (value_input bears weight).
- Task 1 closed on disk (tasks/1.json). Per-task gates all OK: check_extended, check_task_tools, replay_tasks,
  check_solvability, check_compute (settlement 2.89, upgrade 66.81 recomputed at handling time), check_grounding,
  check_cross_fire.
- Manual values gates (task 1): one hop, value_input; the settlement is the member's own payment; persona never
  mentions the declined renewal; near-misses: the 2025-03-20 retry (18 months back) and the 2026-06-18 order.
- Final difficulty-wide gates (check_traceability skipped: the KB is not published yet): EXTENDED OK,
  TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means branches 39.50 / steps 13.00,
  history_rows_max 73, branches_max 54), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Rework round 2 — policy-task audit (audits/policy_task/membership_charges_and_cancellations/)
The extended_policies block was rewritten by script with the base section left byte-identical (diff against
products/membership.yaml checked). Numbers were re-derived by replaying the real tools on each handling-time world.
- F1 (charter-global, move scope vs carried prerequisite): the move rule now covers only "a member on Cartwise+
  Annual whose current annual term was opened by a plan switch from a monthly plan", and says a term opened by a
  first-period or renewal charge is not moved under it. The term-opening refund likewise covers only terms "that a
  plan switch from a monthly plan opened", so the base "a refund of a first period or renewal charge ends the
  membership" clause can no longer fire under it (closes O2 as well).
- F2 (full_unused sentence left standing): both refund policies now declare the base sentence "Where
  refund_requires_no_benefit_use is true, ... a refund_type of full_unused refunds the whole charge." superseded,
  each with a sentence in its own rule stating that the refund is always priced by its method, never as a whole
  charge.
- F3 / task-0 finding 1 (move method factor unreachable): term_run_value_method now splits on the age of the plan
  switch into the term: whole weeks when it took effect fewer than recent_switch_months (3) months ago, months
  started when 3 or more, calendar days otherwise. All tiers are reachable within the narrowed scope.
- F4 / task-0 finding 2 (pause "method" factors were rate substitutions): earlier_pause_reduction is now a genuine
  method: the whole booked length in days (booked days >= 30), a flat pause_min_days per earlier pause whatever
  its length (1-29 booked days), or no reduction. fresh_period_reduction is relabelled as a parameter (share 1 /
  1/2 / 0). The pause policy is now 5 parameter + 1 method factors.
- F5 / task-1 finding 1 (upgrade method tier unreachable): upgrade_credit_method now tests whether the current
  period's retry capture was below the plan's period fee (credit the whole captured fee) or at/above it (credit the
  whole weeks ahead), falling back to calendar days. Tier 2 is reachable by a member who settles inside the first
  retry interval.
- Task-0 finding 3 (order seed vs the order charter): service fees are now computed with order_evt_service_fee
  (rounded half up, bounded before comparing). Each member/non-member difference is booked as an order_fee_waived
  row with basis member_service_fee_rate: 1.66, 1.35, 1.37 and 0.86. Re-derived task-0 values: term refund 69.91
  -> 68.40, carried refund 4.86 -> 4.56, move charge 2.25 -> 0.44, pause 97 (unchanged). Traces, factor_trace,
  factor_sensitivity, closure texts and the dossier were updated.
- O1: the move and upgrade policies add membership_evt_fee_billing to base_policy_refs and declare its
  "billed ... at the plan's period_fee_usd" clause superseded.
- O3: the move<-term edge condition now names the fee charge whose billing_period_start equals
  current_period_start. O4: the upgrade<-settlement condition drops "status is active" to match the sentence (the
  task closure copies were updated too).
- O5: the carried refund declares "Monthly plans receive no refund outside the full-refund rule." superseded.
- O6: the two tool docstrings no longer use "afterwards" or "then". O7: waiver_offset_window is relabelled
  parameter; the term refund keeps unused_share_method as its method. O8: kept; the order-reading factors already
  meet the cross-difficulty floor.
- T1-O1: task-1 service fees are now charter-consistent (3.00 at the floor for member orders, 3.09 non-member for
  the past-due order, 0.99 for pickup). No waiver arises. T1-O2: a membership_credit_earned row of 0.79 was added
  for the 2026-09-02 pickup order, with credit_balance_usd 0.79 and a seed_consistency entry. Task-1 values are
  unchanged (2.89 / 66.81).
- T0-O2 (half-cent tie): the counterfactual now reads 64.50 from the evaluator, recorded as such.
- Gates after the rework: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (traceability deferred).

## Rework round 3 — merge acceptance (audits/merge_acceptance/validate_scenario.round1.txt)
- Item "task_tools.py: forbidden 'from datetime' (real clock)": `import calendar` and
  `from datetime import date, timedelta` were removed from task_tools.py. In their place, `_Util` gained two
  pure helpers over 'YYYY-MM-DD' strings: month_length (proleptic Gregorian leap rule) and add_days
  (days-from-civil / civil-from-days). add_months now uses month_length. book_membership_pause_b6aef13b computes
  pause_end_date with _Util.add_days(start, days - 1).
- Equivalence check (scratch, since deleted): for every day from 1999-01-01 to 2100-12-31, add_days(n) was compared
  with the datetime result for n in {0, 1, 13, 29, 96, 364, 365, -1}, and add_months(1 and 12) with the previous
  calendar-based version. 0 mismatches. Tool behaviour and return values are identical, so GT, replay hashes and
  scored values do not move. The file now contains none of the frozen lint's forbidden tokens.
- No task field changed. Re-running replay_tasks rewrites db_closure with a different row order: the files differ
  byte-wise, but the sorted-key JSON is identical.
- validate_scenario: the only errors naming this difficulty are the six expected 'required document ... not found'
  (KB not rendered yet). Full gate block green (see final report).
