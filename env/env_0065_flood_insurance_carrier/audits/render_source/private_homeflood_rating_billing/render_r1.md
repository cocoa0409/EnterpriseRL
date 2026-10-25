# Renderer source-scan findings — product homeflood, render round 1 (renderer agent aa03789041cfe0057)
Saved verbatim by the coordinator from the renderer's final message (the renderer STOPPED with 0 docs written).

## Source mismatches (rule vs compute, overwrite scope, undefined branches)

**M1. `homeflood_ext_sale_cancellation`, factor `claim_share`: HomeFlood Renters gets no premium return.**
- Rule: "is nothing when the claim payments on the policy, net of voided payments, for losses dated fewer than 12 whole months before the processing date total at least claim_heavy_pct percent of the dwelling limit, claim_light_share percent of it when they total more than zero but less than that, and all of it when they total zero."
- Compute: `claim_pct: 0 if claim_net >= K('claim_heavy_pct') / 100 * F('building_coverage') else (K('claim_light_share') if claim_net > 0 else 100)`
- Renters policies have a dwelling limit of 0 (min/max_building_coverage 0). With no claims, both "at least 25% of 0" and "total zero" are true. The compute takes the first branch, so every Renters cancellation returns nothing of the term premium. The rule's ordering does not settle which branch wins.

**M2. `homeflood_ext_sale_cancellation`: two overwrites retire product-wide base clauses without naming their scope.**
- Retired: "The policy fee and installment fees are fully earned when policy_fee_refundable is false." Replaced by "The policy-fee return of the cancellation credit is all of policy_fee when … installment fees stay fully earned, save that the closing payment rule may waive the fee of an overdue installment on a sold home." This has no "only for it" scope.
- Retired: "When no_refund_after_paid_claim is true and a claim with a date of loss in the current term has a net payment above zero … no credit is booked." Replaced by "The paid-claim share of the premium return … is nothing when …". This also has no scope.
- The policy's first replaced_by does say "every other cancellation credit remains under the base refund rule". The KB would therefore have to mark these clauses dead everywhere while also saying they still govern other credits.
- Related problems with the same clause:
  - `homeflood_ext_closing_payment` also retires it. Its scoped replaced_by covers only installment fees ("this overrides the base rule that installment fees are fully earned") and leaves out the policy-fee half.
  - The sale-cancellation text says the waiver applies "on a sold home". The closing-payment rule also gives back half the fee for REPLACED_COVERAGE.

**M3. `homeflood_ext_renewal_booking` (`household_policy`) and `homeflood_ext_closing_payment` (`new_home_courtesy`): the compute checks only one NFIP policy.**
- Rule: "the customer's Tidemark NFIP Dwelling Form policy in force at another address" (closing payment: "in force (status in_force) at a different address").
- Compute: `other_orig: CFIELD('dwelling', 'original_effective_date', status='in_force')`, `other_addr: CFIELD('dwelling', 'property_address', status='in_force')`, then tests `other_addr != F('property_address')`. `nh_eff`/`nh_addr` do the same.
- CFIELD returns the first in-force NFIP holding at any address. Two cases go wrong:
  - If the customer also has an in-force NFIP policy at the HomeFlood address, the compute can return 0 while the rule grants the credit. The NFIP Dwelling charter has a contents-only tier, and REPLACED_COVERAGE by NFIP at the same address is a natural reason to cancel.
  - If there are two in-force policies at other addresses, the rule does not say which original effective date counts.

**M4. `homeflood_ext_closing_payment`, factor `overdue_fee_waiver`: a negative gap is not covered by the rule.**
- Rule: "that installment fell due no more than waiver_window_days days before the request's effective date".
- Compute: `waiver_gap: DAYS(od_due, req_eff) …` and `waiver_gap <= K('waiver_window_days')`.
- If the installment fell due after the request's effective date, the gap is negative. The compute grants the waiver; the rule does not define this case. It can happen for PROPERTY_SOLD, which takes effect at the closing while the policy stays active until processed.
- Related gap in `late_charge`: the rule measures "past its due date", but `od_due` is the posted date of the latest INSTALLMENT_FEE item. The plan schedule (3/6/9 months, with month-end clamping) is never tied to that record in the rule.

**M5. `homeflood_ext_rerate_credit`, factor `review_delay`: the review-completion date is undefined.**
- Rule: "when the review is completed more than delay_long_days days after Tidemark received the certificate".
- Compute: `review_days: DAYS(cert_received, NOW)`, where NOW is the day the credit is booked.
- This policy defines no review-completion date, and no record carries one. The two disagree whenever the review was recorded on a different day from the credit.

**M6. `homeflood_ext_installment_payment`, factor `pay_ahead`: counting breaks at month-end.**
- Rule: "fewer than one whole month has passed since the previous installment's due date".
- Compute: `since_prev: MONTHS(inst_term, NOW) - prev_due_months` (counted from the term start).
- The base rule moves a due date on a missing month-day to the last day of that month. For a term starting on the 31st, the two counts give different tiers.

## Lower-severity items (wording, ties, placement)

- **Wording (`homeflood_ext_installment_payment`):** "the first payment received for the term less the plan's down share of the booked TERM_PREMIUM item, … plus policy_fee" naturally reads as (payment − down share) + fee. The compute is `deposit - (term_item * down_pct / 100 + P('policy_fee'))`.
- **Same-day ties:** LATEST keeps the first row on a same-day tie, and no rule states a tie-break. This affects "most recently received Elevation Certificate entry" (policies 1 and 2). It also affects `hf_cert_count >= 2` read as "another, earlier … entry".
- **Placement:** some definitions sit in non-factor bindings (the computation document) but only factors use them:
  - Used by only one factor:
    - certificate re-rate: `nfip_id` and the re-rating-date definition (`loss_history` only)
    - re-rate credit: `cert_survey` (`credit_start_anchor` only)
    - installment payment: `prev_due_months` (`pay_ahead` only)
    - sale cancellation: `req_reason`/`req_doc` (`earning_basis` only)
    - renewal booking: the NFIP-record definition (`tenure_loyalty` only)
  - Used only by factors, but more than one:
    - closing payment: `od_due`/`od_num`/`od_paid` and `req_*`
    - renewal booking: the booking-date definition
