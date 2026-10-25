# rework_claims_r10 — gap_waiver_cancellations_and_claims (render-source scan render_r1.md)

The edits are minimal. No scored figure, trace or task file changes: tasks/0.json and tasks/1.json are byte-identical
to round 9. Each class was swept once over all six policies.

## S1 — sibling overwrite of the base LTV-excess clause

- **Premier worksheet benefit.** The overwrite tail now names the Plus case: "a GAP Waiver Plus 150 claim is reduced
  by the Plus worksheet benefit's own loan-to-value excess". The 120–150 plans stay on the base proportion.
- **Plus worksheet benefit.** It now declares its own overwrite of `less the portion above max_ltv_covered_pct
  (gap_msr_excess_ltv_amount)`. The replaced_by sentence is added to its rule. It says the Plus excess is figured on
  the starting balance the claim shows, and it names the Premier case and the other plans.
- **Sweep of the other sibling pairs.** I checked every other pair:
  - starting balance (Premier / Plus);
  - excluded amounts, add-on refund and force-placed premiums (Premier / Plus);
  - ACV and deductible covered (Premier / Plus);
  - the deductible reimbursement tail.

  Each already names the other plan's case.

## S2 — payment interest with more than one rate-cap change in the period

- The rule now covers every case. When a cap took effect, ended, or both after the latest payment and on or before
  the loss, each calendar day from that payment to the loss accrues at the rate in force on it:
  - the cap's rate from the cap's effective date up to the day before its end took effect;
  - the original APR on every other day.
- The compute matches. The capped days are the overlap of [cap start, cap end) with [payment, loss), and the
  remaining days accrue at the APR. The single-change cases give the same figures as before. The ladder's middle tier
  is relabelled to match.
- **Sweep.** I checked the other date-window ladders: past-due and deferral installment amounts, the capped-rate
  adjustment, and the Plus counterparts. Each has an explicit fall-through for every cap configuration, and none
  assumes a single change.

## S3 — month-end wording

- One sentence defining whole months, exactly as computed, is added to every policy that counts months (both
  starting balances, both excluded totals, the worksheet benefit): "Whole months from one date to a later one are the
  difference in calendar months between them, less one when the later date's day of the month is below the earlier
  date's."
- The post-loss late-charge part of both fee rules now states the window as computed. The installments that fell due
  after the loss are those whose due date is fewer whole months before today than the whole months from the next due
  date to today, less the whole months from the next due date to the loss.

## Docstring note

- The amount parameters of all six task tools now read "kept to 2 decimal places (rounded to the cent)", which is
  what the body's `round(float(x), 2)` does.
- Names, signatures, parameters and bodies are unchanged.
