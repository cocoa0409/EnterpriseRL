# Render-surfaced source mismatches — product landlord (difficulty rental_property_renewals_and_cancellations)
Source: final report of the landlord render agent (round 1, 2026-10-12), copied verbatim by the coordinator. All three are extended-source items routed to rework.

1. **An overwrite that retires nothing.** `landlord_ext_upgrade_difference_charge` retires the base clause "A monthly-billed contract is billed the new tier's installment from the next billing period;". Its `replaced_by` then says "the new tier's installment is still billed from the next billing period under the base rule". So the clause stays in force and the policy only adds a charge. I rendered it as retired-as-unqualified, with that scope carried over.
2. **Overwrites with no real conflict.** `landlord_ext_rerating_correction_credit` retires three cancellation clauses that never conflicted with a billing-correction credit:
   - "A cancellation credit is posted only after the landlord has confirmed the cancellation request on file."
   - "The sale waiver applies only when notice is given no later than sale_cancellation_window_days calendar days after ..."
   - "Only one cancellation credit and one refund are posted per cancellation request."
   They are carried as declared, each with its scope.
3. **Compute narrower than the wording (minor).** `landlord_ext_returned_payment_fee` reads "10.00 when it had been made by card and was charged back". The compute only checks `returned_method == 'card'` and never tests the "charged back" part separately. I rendered it as written.
