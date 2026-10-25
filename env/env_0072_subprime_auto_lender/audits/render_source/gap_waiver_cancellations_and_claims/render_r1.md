# Render round 1: source scan, gap (gap.extended.yaml rev 9). STOPPED before any document was written

Gate line read: `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`.
I scanned the source against XF_recipe.md and the erl-kb-doc-render criteria before writing anything.
No documents were written and nothing was staged. Line numbers refer to
`tasks/gap_waiver_cancellations_and_claims/gap.extended.yaml`.

Checks that came back clean:
- Every `compute_basis` quote appears verbatim in its rule.
- All three prerequisite `policy_source` sentences appear verbatim in their rules.
- Every `superseded_clause` appears verbatim in its base rule, and every `replaced_by` appears verbatim in its rule.
- No factor id is a substring of a tool name.
- Each of the 6 tools is the `target_tool` of exactly one policy (all exclusive).
- No factor reads another factor's binding: shared selections (`pd_named_n`, `bl_std_count`, `ep_unpaid`,
  `bn_balance` …) are plain bindings.
- I checked the SCRA "re-applied cap" configuration (latest cap-ended record older than the latest
  cap-applied record) and dropped it. The contract charter gives each borrower a single active-duty period
  (contract_scra_rate_cap), so that state cannot be produced.

## S1 (RED: sibling-overwrite gap / undeclared departure from an in-force base clause): Plus loan-to-value excess

- gap_ext_claim_worksheet_benefit overwrite #1 (l.2803-2806) retires the base clause
  `less the portion above max_ltv_covered_pct (gap_msr_excess_ltv_amount)`. Its tail keeps the Plus claim
  under the base measure:
  > "on a claim on any other plan it is still reduced by the portion above max_ltv_covered_pct, amortized in the same proportion as the scheduled balance."

  The base measure gap_msr_excess_ltv_amount (l.535) defines that proportion as
  "(scheduled balance at loss divided by amount financed)".
- gap_ext_plus_worksheet_benefit rule / baseline (l.3820-3823; `eu_excess`) instead computes the Plus excess as
  > "times the starting balance the claim shows divided by the amount financed"

  On a Plus claim, the starting balance the claim shows is the Plus starting balance. That balance differs from
  the scheduled balance at loss: it includes the capitalized first-period and added days, the due-change
  count and the SCRA adjustment, and carries no interest to the date of loss.
- gap_ext_plus_worksheet_benefit declares no overwrite of that clause. The Premier tail does not exclude the
  Plus case by name, although its sibling overwrite #2 does ("a GAP Waiver Plus 150 claim is worked under the
  Plus worksheet benefit").
- Effect on the corpus: the gap_claim_benefit document would have to carry the retired clause together with
  an in-force tail that sends Plus claims to the scheduled-balance proportion. The Plus worksheet documents
  would carry the starting-balance proportion. That gives two numbers for one Plus claim (recipe D.20, D.21, D.22).
- Suggested direction (coordinator's call):
  - Either have gap_ext_plus_worksheet_benefit declare its own overwrite of the same clause, with its tail
    naming the Premier case.
  - Or have the Premier tail exclude the Plus case by name ("a GAP Waiver Plus 150 claim is worked under the
    Plus worksheet benefit") and keep only the 120-150 plans on the base proportion.

## S2 (RED: undefined edge / rule vs compute): payment interest when a rate cap both took effect and ended after the latest payment

- Rule sentence in gap_ext_claim_starting_balance (l.1196-1200), repeated in replaced_by (l.1108-1112) and in the
  factor bl_payment_interest:
  > "when the latest payment was posted on or before the date of loss and a cap took effect or ended between them, the days before that change accrue at the rate in force before it and the days from it at the rate in force after it"

  The sentence assumes a single change. It does not say what happens when the cap-applied effective date
  and the cap-ended effective date both fall after the latest payment and on or before the date of loss.
- The contract charter can produce this state. The cap takes effect from the active-duty start date and
  ends the day after the active-duty end date, and it may be requested after service ends. A borrower whose
  latest payment predates the service period reaches it.
- Compute (l.1339-1346):
  - `ai_chg` takes the cap-applied date only.
  - `ai_rate_before` is the original APR.
  - `ai_rate_loss` is the original APR, because `ai_live_loss` is false once the cap has ended.
  - The result is that every day from the latest payment to the loss accrues at the original APR, and the cap period is never accrued at the cap's rate.
- Witness (generic figures, not from any task):
  - Records: latest payment Jan 10; cap at 6% effective Mar 1; cap ended Jul 1; loss Sep 1; APR 24.
  - Compute gives 50 days and 184 days, both at 24%.
  - The natural reading of "the rate in force" gives 50 days at 24%, 122 days at 6% and 62 days at 24%.
- The sentence admits no single reading for this state (recipe C.11). The rule needs to say how two changes
  inside the period are handled, or carve the case out with a record test. The compute must then match.

## S3 (LOW: month-end edge, rule vs compute): fee part's "installments that fell due after the date of loss"

- Premier rule (l.2047-2049) and Plus rule (l.3832-3833):
  > "the late charges assessed on installments that fell due after the date of loss"
- Compute (`ep_post_window` / `ep_post_late` l.2166-2169; `eu_post_window` / `eu_post_late` l.3957-3960) uses a
  window that runs back from today: `MONTHS(next_due, NOW) - MONTHS(next_due, loss)` months over `installment_due_date`.
- When the next due date falls on day 29-31 and the loss falls on a clipped month-end due date, the
  installment due on the date of loss is counted as "after" the loss.
  - Witness: next due Jan 31, loss Feb 28, today May 10.
  - The window is 3 months, and the late charge on the installment due Feb 28 has `MONTHS(Feb 28, May 10) = 2`, which is less than 3, so that charge is subtracted.
  - Under the rule it fell due on, not after, the date of loss.
- This is narrow, and only matters if a seed uses a 29th-31st due day (recipe C.13). Fix the wording or the
  window together with S2, or log it as accepted.

## Observation (not counted as a finding; scenario-wide pattern)

- All six task-tool docstrings describe the amount parameter as "kept to 2 decimal places (rounded half-up
  to the cent)". The body is `round(float(x), 2)`, which is Python's binary round-half-even, not half-up.
- The same wording and body appear in the contract and cpi task_tools, which have already been rendered.
- It matters only for inputs with more than 2 decimals. I would carry it verbatim; logged for the coordinator.

RENDER round 1: STOPPED (S1, S2, S3). No document written.
