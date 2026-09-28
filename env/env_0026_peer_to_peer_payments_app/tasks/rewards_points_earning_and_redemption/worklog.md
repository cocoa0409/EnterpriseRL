# Worklog — rewards_points_earning_and_redemption (M=2)

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems 2, factor_counts [5, 5, 4]
- task 1: prerequisite_problems 2, factor_counts [6, 6, 5]

## Design constraints found at Step 0
- compute sees records only: a customer-stated face value or point count cannot enter a formula, so both
  redemption roots are whole-balance redemptions (points = balance rounded down to the increment).
- points_pending_days is in days and the DSL windows are months, so the whole-balance roots are laid on
  Pocketwire Rewards Obsidian members (points_pending_days 0: the whole balance is redeemable).
- cash redemptions trigger a wallet internal credit (cross-category write) -> not used; gift card and charity only.
- the base once-per-period bonus gate binds bonus_period to a pre-action system value no record carries,
  so each bonus policy declares a clause-level overwrite restating the dedup by entry date.
- rolling windows ("within the last N months" = later than the same calendar day N months back) are defined
  in each extended rule to match the MONTHS() convention exactly.

## Task 0 (closed)
- tree: gift card value (root, user) <- refund clawback <- anniversary bonus (chain, both value_input)
- gold: anniversary 9851 pts; clawback 3760 pts; gift card 8800 pts = 163.59 USD
- skip sensitivity: no clawback -> gift card 246.12; no anniversary -> clawback 2724, gift card 0.00

## Task 1 (closed)
- tree: charity value (root, user) <- courtesy credit (value_input) and <- 2026-Q3 milestone (value_input); fan-out,
  the two prerequisites commute (swap run: identical terminal DB)
- gold: courtesy 11700 pts; milestone 25850 pts; donation 41400 pts = 764.32 USD
- skip sensitivity: no courtesy -> 29700 pts / 548.32; no milestone -> 15500 pts / 286.16

## Difficulty-level closing
- coverage: task 0 = anniversary, clawback, gift card; task 1 = courtesy, milestone, charity; scopes disjoint,
  all six extended policies covered; six task tools, two owner=user (one per task)
- final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK,
  COMPUTE OK (suite means branches 44.50 / steps 14.00; history_rows_max 66; branches_max 45),
  GROUNDING OK, CACHE-DIFF INFO (no stale-cache trap chosen), SCOPE OK
- check_traceability deferred until the KB is rendered

## Round 2 — policy-task audit r1 rework (audits/policy_task/rewards_points_earning_and_redemption/)
- D1 / T0-R1 / T1-R1: the five multiplier "method" factors were replaced by genuine algorithm switches:
  clawback_age_method (rate method / lower-of-two / proportional share), gift_card_plan_valuation and
  charity_valuation (banded / block bonus / flat), courtesy_volume_form (volume-based / blended / flat),
  milestone_streak_form (spend-based / blended / flat). Factor counts per computation unchanged (draw kept).
- T0-R2 / T1-R2: false "exactly 12 months back" assertions corrected; task 1's 2025-10-03 records moved to
  2025-10-05 so the edge near-misses are exact; every dossier near-miss re-verified by recomputation.
- D2: whole-balance redemptions are stated as available only when nothing is pending (no second value, no override).
- D3: milestone tier amount now "the tier held on the credit date" (rule = compute).
- D4: E1 narrowed to "the most recent enrolment anniversary", E2 to "the latest merchant refund".
- D5: bonus tools no longer take bonus_type; each books its own kind only.
- D6 / T0-O1: every spend-reading rule defines earning entries (boost entries excluded); "boost earning entries" -> "boost entries".
- D7: inputs.history completed (clawback-spend reads of courtesy and charity, and others).
- D8: the courtesy repeat adjustment (unreachable tiers on cap-1 tiers) is gone; boost lift / clean-record / category
  relief kept as observations. D9: base order, no edge, no change. T0-O2 / T1 persona: anticipatory
  phrases removed. T1-O1: terminal states equal in either order (recorded in order_uniqueness).
- task 0 world: opening balance 2724 -> 1924 (2026-09-15 redemption +800) so the rate-method clawback (2520)
  still exceeds it. New gold: task 0 anniversary 9851, clawback 2520, gift card 9200 pts = 159.68;
  task 1 courtesy 14664, milestone 27989, donation 46500 pts = 868.15.
- final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches 46.50 / steps 14.00; history_rows_max 74; branches_max 47), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Round 3 — post-publication traceability (coord snap rewards_render_r1)
- item: tasks/1.json bonus_period '2026-Q3' had no verbatim source in the agent-reachable context.
- fix (world only): seeded the employer's quarterly bonus direct deposit on the linked personal account
  (1250.00, 2026-09-30, app reference BMG-QBONUS-2026-Q3), returned by find_wallet_transactions (step 7),
  before the milestone write (step 11). Wallet ledger_balance +1250.00. Tiers unchanged (3-month deposits
  19850.00 >= 9000; last-month deposits 7450.00 >= 5000); all expected/baseline/sensitivity figures unchanged.
- charter and tools unchanged (rewards.extended.yaml b72678cf...1661, task_tools.py 67433db6...edc8): no re-render needed.
- gates: all OK including TRACEABILITY OK (0.json 19/0, 1.json 20/0).
