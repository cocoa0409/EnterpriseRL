# Renderer findings, preowned render round 1 — STOPPED before writing any doc (saved verbatim by the coordinator from the renderer's final message)

RENDER round 1: STOPPED 4 source mismatches

**Mismatches (each one stops the render):**

1. **`preowned_ext_recovery_transport_charge`, factor `repeat_recovery`: the zero-fee case is never stated.**
   - Rule: "three or more agency fees carry the third-recovery surcharge; exactly two agency fees carry the second-recovery surcharge; a single agency fee carries none."
   - Code: `K('repeat_third_surcharge') if agency_fees_posted >= 3 else (K('repeat_second_surcharge') if agency_fees_posted == 2 else 0.0)`.
   - A contract with no agency fee posted gets 0.0, which the rule never says.

2. **`preowned_ext_recovery_transport_charge`: the charge's date is undefined when there is no condition report for this recovery.**
   - Rule: "one transport charge per recovery, dated the lot-intake date, that is the date of the condition report taken when the vehicle reached the storage lot".
   - The same rule covers "a contract whose most recent condition report is dated on or before the repossession date (no report yet taken for this recovery), or one with no condition report on record", but only for the holding charge.
   - In those cases the `service_date` that `book_recovery_transport_6b5d55b7` needs has no defined value. Taking the latest report's date would date the charge before the repossession. That conflicts with the deficiency-quote prerequisite "the transport charge for that recovery, dated on or after its repossession date".

3. **`preowned_ext_sale_notice_schedule`, factor `auction_transfer_days`: one case falls into no rule case.**
   - Rule: "a vehicle held on the storage lot, shown by a condition report dated after the repossession date of an involuntary recovery … adds the lot transfer days; a voluntary surrender … adds the dealer transfer days; a vehicle still at the agency's yard adds none".
   - The code's last case is "otherwise 0".
   - An involuntary recovery whose most recent report is dated on the repossession date fits none of the three. The transport rule calls that vehicle "a vehicle taken to the lot on the day of the repossession", so it is on the lot, not at the agency's yard.

4. **`preowned_ext_redemption_quote` vs `quote_redemption_amount_aa560e9a`: a boundary case the tool's stated format rules out (latent).**
   - Rule: "a recorded state reinstatement period longer than the company reinstatement window for the tier, still running, interest runs through and the quote is good through the last day of that state period".
   - Code treats the period as still running on its last day: `DAYS(F('repossession_date'), NOW) <= F('state_reinstatement_days')`. The window case works the same way.
   - A quote dated on that last day is good through the same day, so `good_through_days` is 0. The tool description says "`good_through_days`: … a positive integer".

**Other observations (not counted in the 4):**
- **Which "sale date".** The deficiency quote and the settlement read the contract's scheduled sale date. The deficiency rule names "the auction sale" among "the most recent of their kind" records it reads and never says which date is the sale date. The two only diverge if the auction record's date differs from the scheduled sale date.
- **Settlement payment vs base posting rules.** The `remit_deficiency_settlement_2e6b8900` tool posts "today" by online transfer. The base payment rule, still in force, says "a payment received … on a weekend … posts the next business day" and "While certified_funds_only_until is on or after the posting date, only cashiers_check, wire or moneygram payments are accepted". The extended rule ("paid by the customer from the customer's own bank account") declares no overwrite of either.
- **Reinstatement standard method.** `baseline.rule` ("past-due amount plus the fees due balance … rounded to the cent") leaves out the deduction of excluded fees when the state reinstatement right applies. The code applies that deduction even with no adjustments in play. The full rule does state it, so the calculation document can carry it.
- **Placement only.** Some plain calculation steps are used only by one adjustment (deficiency: `post_sale_per_diem`, `disposition_credit`, `storage_billed_days`, `storage_credit`; redemption and reinstatement: `storage_daily_amount`, `projected_storage` / `posting_storage`). The four-policy shared storage paragraph repeats the release-storage free-days and lot-day rules. I would split it in the release-storage docs by subject and keep it scoped to the charge billed at release or sale, as the carried note asks. Neither needs a source change.
