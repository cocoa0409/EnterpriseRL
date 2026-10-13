# loyalty_points_and_rewards — difficulty worklog

Draws (draw_counts.py --tasks 2): task 0 = 1 prerequisite, factors [4,4]; task 1 = 2 prerequisites, factors [4,5,4].

| task | tree (root first) | user write | tools |
|---|---|---|---|
| 0 | delivery_failure_goodwill <- returned_merchandise_reversal (value_input, state form) | goodwill acceptance | accept_goodwill_points_7ea0a08d (user), post_points_reversal_46de2c04 |
| 1 | birthday_make_good <- tier_upgrade <- missing_points_adjustment (both value_input, state form) | birthday claim | claim_birthday_bonus_8dc2d134 (user), write_tier_upgrade_189dabab, post_missing_points_b5bbe1fa |

Scopes are disjoint and cover all five extended policies. Per-task dossiers are in each task's design_rationale.

Base defects routed around inside the extended charter (blueprint untouched):
1. Only one customer-owned write exists in the blueprint (closure confirmation), and its only figure (the whole positive balance) admits no factor; the user writes are the member's acceptance of a goodwill grant and the member's in-person birthday claim.
2. All goodwill gates and the once-per-reference dedup are attached to the whole loyalty_bonus_posted subject; the birthday policy restates them for itself through declared overwrite entries.
3. The compute DSL has no calendar window; current calendar year/month use within_months = current month number / 1, exact on the last day of a 31-day month (both frozen dates are such days).
4. P() reads only the tier held; the tier policy mirrors the five tier thresholds as params with identical values.
5. Loyalty compute is membership-scoped; the claim, the return and the order concerned are reached through their record status / reservation link (one such object per world).

Gates: all per-task and difficulty-wide gates green; check_traceability not run (needs the published KB under docs/).

## Round 2 — policy-task audit closure (audits/policy_task/loyalty_points_and_rewards)

- G1: goodwill rule now states that a grant is made while the claim stands approved (a resolved claim is closed to a further grant); declared in `overwrite` against the base "approved or resolved" sentence.
- G2: tier upgrade start (date written) and validity (31 December of the year after the year the spend reached the threshold) declared in `overwrite` against the base start/validity sentence; rule text aligned.
- G4: missing-points adjustment scoped to reservation fulfilment orders; object = fulfilment order of the member's fulfilled reservation (rule = compute); reservation ladder fall-through = back-orders.
- G5: birthday shopping window restated as the month ending on the claim date (rule = compute).
- G6: deposit credit reads only the member's Deposit Pre-Order's reservation events.
- G7 / T1-F1: `late_credit_factor` (a rate) replaced by method factor `late_credit` (percentage of rounded points with a floor / flat credit / none).
- G8 / T1-F2: `birthday_month_shopping_factor` (a rate) replaced by method factor `birthday_shopping_boost` (double / credit the month's merchandise again at the tier multiplier / stands); task 1 birthday expected re-run.
- T0-F1: task 0 seed now carries the full tier and points history (2019 inactivity forfeiture, 2024 Silver and 2025 Gold qualifying orders, the 2025-11-14 conversion and its expired note); seed_consistency rewritten.
- Observations: O1 floors stated in the rules; O4/O5 edge conditions reworded; T0-O2/T1-O2 multi-source wording corrected; T1-O1 tier-flipping near-misses planted in task 1. O2, O3, O6-O12 left as recorded (no change required).
