# Rework round 4 — claims (nonowner_policies_and_renewals)

Each revision_3 item, by id, with how it was closed. No scored values appear here; the task files carry them.

## Charter findings (revision_3)
- **R3-A** (P6 non-commuting order): closed.
  - P6's generic combination sentence now says the combined relativity multiplies the increase rated premium once, before the increase deduction is subtracted.
  - The sentence's order (replacements, relativities, rounding) is unchanged and it names no factor quantity.
  - Rule words and compute are identical. The compute_basis quote is updated verbatim.
- **R3-B** (P6 additional premium on a limits decrease): closed.
  - P6's scoped overwrite replaced_by names the direction of every package change: limits_increase for a move to a higher six-month base rate, limits_decrease for a lower one.
  - A move to a lower base rate whose charge is above zero (the DUI realignment) is charged as additional premium, and only such a move.
  - Every other move to a lower base rate still returns unearned premium as the base states. The reinstatement clause is restated.
  - The tool records the direction-matched reason, so it no longer stamps limits_increase on every change.
  - P4's prerequisite condition is aligned. P4's wait stays non-zero (XF20).

## Task findings (revision_3)
- **T1-R3-1** (R3-A): closed.
- **T1-R3-2** (R3-B): closed. The gold call records the limits-decrease reason.
- **Task 0**: PASS in revision_3; untouched.

## Observations (revision_3)
- **O3-6**: factual error fixed. Task 1's final bill splits its total by field meaning (past due, unbilled premium, unbilled fee); the total is unchanged.
- **O3-7**: factual error fixed. The rework_r3_claims.md wording about task 0 values is corrected.
- **O3-3**: not a factual error; recorded in the worklog.
- **O3-1, O3-2, O3-4, O3-5**: not factual errors; carried. The O3-2 residual risk is disclosed.

## Regression guard
- Only these changed:
  - P6 overwrite, rule and one basis quote;
  - P4 prerequisite condition;
  - one tool's signature and body;
  - task 1's gold call, edge condition, rationale and final-bill row.
- All earlier closures (CG-1..CG-9, R2-A..R2-H, XF1..XF23) are untouched, and the gate block is all OK.
