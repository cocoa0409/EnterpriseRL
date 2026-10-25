# Rework round 13: claims per render_r4 (bounded: G2 only)

No scored value moved. The changes are limited to the one sentence below and its ladder wording and compute_basis quotes.

## G2 (render_r4): the insured-request return did not state a negative lag

**Closed.** Changed in auto_ext_insured_request_cancel_return:

- **Rule.** The last case of the SR-26 transmission-days sentence now reads "processed on or before the cancellation effective date, or with no certificate standing filed on that date, none are." This matches the compute, which keeps 0 days for a lag below one.
- **Ladder.** The last `when` of ic_sr26_transmission_days now reads "otherwise (processed on or before the ending date, or no certificate standing filed on that date)".
- **compute_basis.** The quotes for ic_lag_raw, ic_lag_max and ic_lag are synced to the new sentence.

The nonpayment twin is unchanged and stays correct. Its rule processes the cancellation "no earlier than the cancellation effective date", so its lag is never negative.

## render_r1 F1-F7, render_r2 G1: already closed in earlier rounds (re-verified by render_r2 / render_r4); no change

## Checks

- Verbatim sweep clean: every compute_basis quote is found in its rule.
- Gate block 7/7 green.
