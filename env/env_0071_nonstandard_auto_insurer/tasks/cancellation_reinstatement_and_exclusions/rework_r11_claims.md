# Rework round 11: claims per revision_10 audit item

No scored value moved. Nothing outside the four sentences listed below was changed, except the baseline sentence noted under member 2.

## R10-01: four assembly sentences named a factor or a factor-only quantity

**Closed.** Each sentence now states the order by kind of adjustment and keeps every order that does not commute.

1. **Nonpayment return.** The order now reads: those that settle the days returned come first, an adjustment that replaces the standard days returned being applied before any that takes further days off them, never below zero. After that comes the pro rata unearned premium, then the amounts subtracted, then the floor and the single rounding.
   - Matching compute_basis quote updated: `nc_days_returned`.
2. **Insured-request return.** The baseline genuinely uses the daily basis, so its definition moves into the baseline sentence: "the daily basis, the current full-term rate divided by term_days". The assembly sentence now reads: those that settle the daily basis and the days returned come first, a replacing adjustment applied before any that takes further days off them. It gives the unearned premium "or the amount an adjustment returns in its place". The percentages, then the amounts, then the floor and the single rounding follow as before.
   - Matching compute_basis quotes updated: `ic_days`, `ic_unearned`.
3. **Reinstatement fee.** The order now reads: "an adjustment that replaces the standard reinstatement fee is applied first; those stated as amounts are then added together to the result".
4. **Lift.** The order now reads: "an adjustment that replaces the standard lift share is applied first; the relativities below are then multiplied together with the result into the lift share, rounded to the cent".

## Checks

- Verbatim sweep clean: compute_basis, replaced_by, baseline and policy_source sentences.
- Both tasks' computations still match their gold.
