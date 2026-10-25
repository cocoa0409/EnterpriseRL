# Render-source findings — warranty (round 2)

Source re-rendered: `warranty.extended.yaml` sha256 c1d4cdf1e6e34ce45d07b090f385e68080293916d158d11f8ecfec73e6ae399c, `task_tools.py` sha256 afbde65ba37788195ecf896572da248eb1495f9f32f6257be77cc870e231b08f.
Upstream gate: policy re-audit `revision_4 verdict` is PASS for task 0 and task 1.

## Closure of the round-1 items
- **F1** (base labor formula has no increment rounding) — BLUEPRINT-KNOWN. The base sentence is still carried verbatim and marked "no longer in force" in the service-terms document. No change.
- **F2** (proration step wording) — closed. The source now reads "once five/ten full years have been reached", and the KB carries it verbatim in the share calculation document.
- **F3** ("CareLine plan" vs the On-Call Service Account) — closed. The source sentence "A CareLine plan in this policy is any plan of the CareLine Service Plans other than the On-Call Service Account" is carried in each document that uses the term.
- **F4** (29 February) — closed. The share rule states the anniversary fallback and the transfer rule states the month-completion convention. Both are rendered with boundary cases; the compute agrees (`+1` when the day reached is the last day of a month that lacks the start day).
- **F5** (overwrite scope) — informational only, unchanged, no action.

## New items (round 2)
### R2-1 — helper bindings for the transfer month count sit outside the factor that uses them (informational)
- Location: `extended_policies[id=warranty_ext_transfer_fee_confirmation]`. The compute bindings `start_ordinal … start_day`, `confirm_ordinal … confirm_month_days` feed only `months_elapsed`, which is a binding of factor `remaining_term_share`. They are not listed in that factor's `bindings`.
- Effect: under the gate, these date-decomposition bindings must be claimed by the computation document (role baseline, `covers`), whose standard calculation never uses whole months. The rule they implement ("a month being complete once the day of the month of the original coverage start date is reached and, in a month that lacks that day, on the last day of that month") is rendered in the remaining-term document, where it is used.
- No semantic mismatch. Suggest adding these bindings to `remaining_term_share.bindings` in a later revision.

No rule-vs-compute mismatch, non-verbatim compute_basis quote (all quotes are verbatim substrings of the rule), rounding mismatch, retirement error or docstring/body mismatch was found in this source.
