# Worklog — pharmacy_coverage_and_exceptions (category rx), M=2

## Step 0 — draws (scripts/draw_counts.py)
{"task": 0, "key": "env_0022_medicaid_managed_care_organization/pharmacy_coverage_and_exceptions/0", "prerequisite_problems": 3, "problems": 4, "factor_counts": [5, 4, 6, 4]}
{"task": 1, "key": "env_0022_medicaid_managed_care_organization/pharmacy_coverage_and_exceptions/1", "prerequisite_problems": 3, "problems": 4, "factor_counts": [5, 4, 6, 4]}

## Step 0 — asset ledger / scope constraints
- Numeric write fields available in rx: rx_fills.days_supply/quantity/member_copay/plan_paid_amount,
  rx_otc_ledger.amount, rx_coverages.otc_balance. rx_exceptions carries no numeric field, so
  exception requests, lock-in changes and bare override grants cannot carry a scored computation.
- Therefore the 8 problems are: OTC ledger writes (task 0) and dispensing-days writes (task 1).
- Task 0 (OTC, PrairieRx Maternity): closed-quarter forfeiture -> quarter load -> posting of a
  transmitted retail receipt -> member's own catalog order (owner=user, root).
- Task 1 (dispensing days, PrairieRx Children): emergency supply, transition fill and release of a
  granted vacation override (all owed on the records) -> lost/stolen replacement fill (owner=user, root).
- Cross-difficulty evidence: plan (plan_memberships / plan_claims), pcp (pcp_assignments).
- Identifier band: phone 4025530000-4025530999; medicaid_id PR30000000-PR39999999; ssn_last4 3000-3999.

## Task 0 — closed (OTC chain)
- Policies: rx_ext_otc_quarter_forfeit (4 factors), rx_ext_otc_quarter_load (6), rx_ext_otc_receipt_posting (5), rx_ext_otc_catalog_order (4, root, owner=user).
- Tools: forfeit_otc_quarter_0e0fa26e, load_otc_quarter_30ec28e6, post_otc_receipt_a5c098d1, place_otc_catalog_order_ca6274ae.
- Gold: forfeit 2026-Q2 3.46 -> load 2026-Q3 75.75 -> post RCPT-0806-44719 60.92 -> order 5.90.
- Per-task gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK.
- Customer: Seraphina Kowalczyk-Adeyemi, phone 4025530627, medicaid_id PR30417726, ssn_last4 3462.

## Task 1 — closed (dispensing days, parallel fan-out)
- Policies: rx_ext_emergency_supply_days (4 factors), rx_ext_transition_fill_days (5), rx_ext_vacation_supply_release (4), rx_ext_lost_stolen_replacement (6, root, owner=user).
- Tools: record_emergency_supply_c348acc4, book_transition_fill_6c1f1c97, release_vacation_supply_4890f9e9, request_replacement_fill_14de4074.
- Gold: emergency supply 13 days -> transition fill 26 days -> vacation release 20 days -> replacement 13 days (member files with police report OPD-26-114907).
- Customer: Caspian Thornquist-Abara (mother Maribel calls), phone 4025530351, medicaid_id PR35820914, ssn_last4 3718.

## Difficulty-level closure (final gates, no --task)
- EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (branches mean 52.00, steps mean 15.50, history_rows_max 26, branches_max 57) / GROUNDING OK / CACHE-DIFF INFO (optional) / SCOPE OK.
- check_traceability not run: the KB documents are not yet published.
- Coverage: tasks 0 and 1 claim disjoint scopes that together cover all eight extended policies and all eight task tools.
- Known design limits for the audit: several factor ladders are plan-invented refinements (retention carry-over, load credits, register co-funding, weekend roll, off-cycle adjustment); the care-program factors read the care category, which has no difficulty, so they are marked cross_difficulty null; plan-based factors carry the cross-difficulty requirement.

## Rework round 2 (audit: audits/policy_task/pharmacy_coverage_and_exceptions/)
Plan, item by item:
- CG-P1: edge D/E `condition` rewritten to quantify over every qualifying rejection, matching the sentence.
- CG-F1: catalog order_share ladder re-cut on reachable conditions (two or more orders open x previous-quarter usage).
- CG-F2 (order): draw base relabelled as a parameter (withheld share of the carry-over) with non-degenerate conditions; the order's method factor is now the register keep-back counting window (rolling two months / rolling one month / current quarter tag). World: one extra 2026-Q2 retail receipt so the windows differ.
- CG-F2 (vacation) + CG-F4: vacation release rebuilt — baseline is the plan maximum less days on hand; method = how days on hand are measured (controlled refill date / ordinary refill date / days supply); waiting_days removed; new parameter on vacation overrides in twelve months. World: a second drug with an earlier vacation override.
- CG-F3: emergency weekend roll replaced by a genuine day-count convention method (business days / weekend roll-forward / calendar days) keyed on who started the request; replacement weekend roll relabelled parameter.
- Observations addressed: current quarter defined; keep-back counts only posted receipts without an invented window; register total = largest unposted receipt; vacation rounding stated; drug-name wording; carry-over floor stated; replacement third tier floor stated; transition fill answers the latest rejection; rationale wording.

### Round 2 closure record
- CG-P1: rx_ext_lost_stolen_replacement prerequisite[0..1].condition now quantify over every qualifying rejection (matching "every" in the sentences).
- CG-F1: rx_ext_otc_catalog_order.order_share re-cut: six tenths / eight tenths (two or more orders open, split by the forfeited quarter's usage) / whole (fewer than two open); all tiers reachable under the plan parameters.
- CG-F2 (order): draw base relabelled parameter `withheld_carryover` (whole / half / nothing withheld, conditioned on posted current-quarter retail receipts and open orders, fall-through not degenerate); genuine method = `keep_back_count_window` (rolling two whole months / rolling one whole month / calendar-quarter count). World: retail receipt RCPT-0628-19027 (2026-Q2) added; forfeiture and order recomputed.
- CG-F2 (vacation) + CG-F4: vacation release rebuilt — baseline = plan maximum less days on hand; method `on_hand_measure` (controlled refill date / ordinary refill date / days supply); `waiting_days` removed; `override_history_adjustment` added. World: fluticasone refill, vacation override and vacation fill added; release recomputed.
- CG-F3: emergency `weekend_roll` replaced by method `day_count_convention` (business days / weekend roll-forward / calendar days, by who started the request); emergency figure recomputed. `replacement_weekend_roll` relabelled parameter.
- Observations: current quarter defined as the calendar quarter; keep-back standard count uses posted receipts exactly (no invented window); register total = largest unposted receipt with a rule sentence; vacation rounding (fractions dropped) stated; vacation drug wording; carry-over floor stated; replacement third-tier floor stated; transition fill answers the latest rejection; rationale wording on the 2026-02-11 claim corrected.
- Gates after round 2 (difficulty-level): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability not run (KB not published). task_tools.py unchanged in round 2. __pycache__ removed.

## Rework round 3 (audit revision_2 sections)
- R2-T1 (task 0, SOURCE-TASK RED): the receipt-posting rule now defines "the last six whole months" (fewer than six whole calendar months from the date to today; a month is whole once today's day of the month reaches the date's day) and every window sentence, basis and ladder of that policy uses that wording; the posted_retail_receipts basis quotes the definition. The Q1 retail receipt was moved off the six-month anniversary (RCPT-0216-11842, posted 2026-02-16), so no posted receipt sits on the boundary. The price-adjustment tier has one reading; all scored figures re-derived and unchanged.
- Revision-2 observation (vacation baseline "never below zero" vs compute floor of one day): the baseline sentence and the rule now state the one-day floor.
- Other revision-2 observations left as observations: current-quarter compute proxy (coincides with the calendar quarter whenever any row is tagged to today's quarter; the DSL cannot build a quarter string from the date), requester-selected day-count convention and keep-back window realism, keep-back tiers 1/2 differing in window length (accepted shape), carried realism notes.
- Gates after round 3: per-task (0 and 1) all OK; difficulty-level EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability not run (KB unpublished). task_tools.py unchanged. __pycache__ removed.
