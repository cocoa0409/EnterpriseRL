# Source mismatches reported by the card renderer (agent aa5f52c63fad4dd40), render round 1 — verbatim from its final report

1. **compute_basis quotes not found in their rule**
   - `card_ext_credit_line_review` `paid_3m`: "whose payments credited in those three months total at least the statement balances of those statements". The rule says "whose payments credited fewer than three full calendar months before today total at least the statement balances of those statements".
   - `card_ext_courtesy_credit` `ct_mf_spend_12m`: "whose Marlowe & Finch purchases charged to the account with a transaction date in the last 12 full calendar months total at least rel_top_spend dollars". The rule says "with a transaction date fewer than 12 full calendar months before today total".
   - `card_ext_courtesy_credit` `ct_missed_due`: "its payment due date is the missed due date." The rule has "missed due date;" — punctuation only.

2. **Rule clause with nothing matching it in compute** (`card_ext_credit_line_review`): "for a cardmember holding no other Marlowe & Finch card account in active or restricted status, is sized at the line review as follows; a cardmember who also holds an account on the other network is sized under the base credit line rule and the combined credit line limit alone." The compute sizes every account the same way. The entry document states the clause as written.

3. **Factor tiers that rest on another factor's output**
   - `utilization_share`: tiers on "line-review utilization", which is built from `measured_balance` (factor `balance_measure`).
   - `billed_interest_part`: "payments credited in the latest billing period cover the error-period statement balance less the grace-test exclusion, the posting in error and its related fee". This uses the outputs of `grace_test_exclusion` and `twin_selection`, and its methods apply `int_base` (factor `interest_base_pick`).
   - `unbilled_accrual_span`: accrues on the posting in error (`twin_selection` output).
   - `missing_credit_proration`: "the credit owed is at least the latest statement balance" (`owed_comparison` output).
   - `missing_credit_accrual`: accrues on the credit owed (`owed_comparison` output).
   - `coverage_follow`: "the coverage is the latest statement's catch-up minimum basis" (`dispute_relief_basis` output).

4. **Two readings I pinned to match compute** (not mismatches, flagged for awareness)
   - `missing_credit_proration`: "issued no more than proration_days calendar days before the latest statement date" is written as "on the latest statement date or within the 30 calendar days before it". A refund dated after the statement falls to the last tier, as compute requires (`refund_lead_days >= 0`).
   - `coverage_follow`: "no more than coverage_window_days calendar days after the day of the catch-up payment" is written to include due dates that have already passed, matching `DAYS(NOW, cu_last_due) <= 21`.
