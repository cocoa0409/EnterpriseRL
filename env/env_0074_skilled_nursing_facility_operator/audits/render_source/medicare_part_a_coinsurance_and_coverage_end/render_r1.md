# Renderer scan-first findings — medicare (render round 1, renderer agent a383c6b6056be918b, 2026-10-22)

Saved verbatim by the coordinator from the renderer's report. The renderer wrote no documents.

Gate passed: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`.

The pre-render scan of `tasks/medicare_part_a_coinsurance_and_coverage_end/medicare.extended.yaml` and its `task_tools.py` found two real source defects:

## Finding 1: the card payment and bank draft contradict a base clause that is still in force (XF C.16)

Base policy `medicare_evt_payment_posting`, rule (line 1223), is not retired by any overwrite:
> "Every payment is applied to one named coinsurance charge and only up to that charge's open balance; … any remainder beyond the open charges is not posted but returned to the payer."

`medicare_ext_card_payment_share`, rule (around line 2569):
> "The daily rate the card payment settles follows the calendar year in which the paid block's days were furnished: … any other paid block at 217.00 a day." … "the rounded figure less the payments already applied to that charge, net of any returned payments, is the card payment, never less than nothing and never more than the card payment maximum of 5000.00."

Compute (line 2792):
`result: MN(MX(0, RND(int(yr_rate * (...) + 0.5) / 100 - net_paid, 2)), K('card_max')) if in_scope else 0`

`medicare_ext_bank_draft_payment`, rule:
> "the rounded figure less the payments already applied to the resident's charge, net of any returned payments, is the bank draft, never less than nothing."

Compute (line 6282):
`result: MX(0, RND(int(yr_rate * (...) + 0.5) / 100 - net_paid, 2)) if in_scope else 0`

Neither figure is capped at the charge's open balance. The rate-year correction and the reversed-day reduction both are capped.
- Where it breaks: a resident charge priced below the year-of-service rate. The base names this error itself: "never at the rate of the posting date or of the admission year."
- Example: tier without supplemental coverage, no supplemental effective date. One days_21_100 block of 10 days in 2026 with no reversals and no leave. Its resident charge was posted at 209.50, for 2,095.00, with nothing paid.
- Result in that example: the block passes both record tests, so both policies give 2,170.00. The open balance is 2,095.00, so the base clause gives 2,095.00 applied and 75.00 returned.
- No fix through a correction: the rate-year correction gives 0 ("never less than nothing"), so the charge cannot be corrected first.
- Effect: two readings of the scored amount.

## Finding 2: the bank-draft prerequisite can wait on a reduction that nothing prices (XF B.11, undefined branch)

`medicare_ext_bank_draft_payment`, prerequisite `policy_source` (line 6101):
> "A bank-draft payment toward a resident coinsurance charge is not taken until the records carry, against that charge, a reduction for every day reversal posted against its booked-days entry after the charge itself was posted."

`medicare_ext_reversed_day_reduction`, rule (around line 4944):
> "…and it prices the days of the uncertified-day reversal posted against that booked-days entry after the charge was posted, under that reversal's own reason."

Compute (lines 5177–5178, 5198):
- `un_after: un_n > 0 and … DAYS(tc_post, un_post_x) > 0`
- `un_priced: un_days if un_after else 0`
- `result: MN(int(red_rate * (u_early * early_share + (un_priced - u_early) * tier_share) + 0.5) / 100, open_bal)`

- Where it breaks: a hospital-day or leave-of-absence reversal posted after the resident charge.
- Why the block is still in scope: `chg_ok` only compares the charge's day count with the reversals posted on or before the charge date.
- The gap: the bank draft waits on a reduction for that reversal; the reduction policy prices only uncertified-day reversals, so it gives 0, and `reduce_coinsurance_for_reversed_days_0894f336` rejects a non-positive amount; for such a block the shared overwrite's `replaced_by` defers to "as their own policies state", and the reduction policy states nothing for that reason.
- Effect: the hop cannot be resolved at the source's strength.

## Checks that came back clean
- All `compute_basis` quotes appear verbatim in their own rules.
- The overwrites' `superseded_clause` and `replaced_by` match, including the five-way exclusion between sibling policies.
- Rounding placement matches between rule and compute in all five policies.
- Tie and absent-record handling is covered by the count tests in each record test.
- No factor reads another factor's binding.
- Docstrings match the tool bodies.
- The 2024–2026 coinsurance rates and the Medigap K/L shares are realistic.
