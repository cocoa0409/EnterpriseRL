# Rework round 8: claims per render_r2 findings

No scored value moved.

## G1 — the lift's second prerequisite waited on residents the re-listing does not price

**Closed** the way F7 was closed. The lift's second prerequisite sentence, its edge condition, and task 1's closure text and rationale quote are now scoped to exactly the resident the re-listing prices: the household resident on the term's latest claim report recording an unlisted household resident, unless that resident is named on an exclusion form on file.

In the same class, the re-listing's own scope sentence and its two overwrite replaced_by sentences now name that same single resident instead of "a household resident reported ... while unlisted". Every other driver added stays under the base rule.

Edge sweep: every edge in the charter now waits on no more than its depended-on policy prices.
- **Lift → exclusion:** the latest form, when it names a reported-unlisted resident.
- **Lift → re-listing:** the latest unlisted report's resident.
- **Insured-request cancellation → reinstatement:** the recorded re-written entry and the reinstatement date.
- **Reinstatement → nonpayment cancellation:** the recorded cancellation for nonpayment.

## Minor note — the lift's points read

**Closed.** `ab_vpts` is now LATEST over the driver's exclusion entries by change effective date, so the first entered is kept on a tie, as the rule states.

Sweeps clean: compute_basis quotes, replaced_by, baseline and policy_source sentences.
