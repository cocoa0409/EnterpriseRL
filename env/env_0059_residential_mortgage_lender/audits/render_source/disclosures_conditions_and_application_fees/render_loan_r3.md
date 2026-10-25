# Remaining source mismatches reported by the loan renderer (agent a98c70f1f4d9199a4), render round 3 — copied verbatim by the coordinator

Rendered source: loan.extended.yaml 9516b83c…, task_tools.py ec0bb1f1…. docs/loan/ republished (69 docs, DOCS OK).

**Remaining source mismatches (rendered as they stand; none moves a scored value):**
1. **Missing scheduled closing date in the corrected Closing Disclosure.** In `loan_ext_corrected_cd_nonrecurring_costs`, the appraisal, title and verification ages each compute `… if (… and F('estimated_closing_date')) else -1`, so every line becomes nothing when the file has no scheduled closing date. The rule gives no tier for that case; it only names "a file with no primary appraisal order in delivered status", "a file with no cleared title commitment condition" and "no cleared verbal verification of employment condition yet". This is probably unreachable, since the policy applies when the closing date moves.
2. **Bindings filed under no factor.** `delivered_order` (corrected Closing Disclosure) and `standard_order` (in both the revised Loan Estimate and the cure) belong to no factor. `delivered_order` is read only by the appraisal factor, and in the cure `standard_order` is read only by the rush factor. The gate therefore makes the computation documents claim them. Their prose describes the order only where the standard figure itself reads it (the fee sheet's base fee).
3. **Base B-1** is unchanged (blueprint-known).
