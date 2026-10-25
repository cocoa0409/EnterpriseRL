# Render-source findings — warranty (round 1)

Source: `tasks/warranty_claims_and_transfers/warranty.extended.yaml` (sha256 242649fc…) + `task_tools.py` (sha256 101f5436…).
None of the findings blocked the render. No rule was rendered around: each one is carried as the source states it, or pinned to what the compute does where the wording allows only that reading. All are low severity.

## F1 — base rule vs base formula: the labor increment rounding is missing from the formula (base, informational)
- Location: `policies[id=warranty_service_charges].rule` vs `policies[id=warranty_service_charges].formula.labor_charge`.
- Rule: "labor at the plan's hourly rate for the billable hours, which are the hours on site with the minimum applied and any time beyond the minimum rounded up to the billing increment."
- Formula: `labor_charge: round(labor_rate_per_hour * max(labor_min_hours, labor_hours), 2)` — it applies no rounding up to `labor_billing_increment_hours`.
- Impact: low. Two overwrites (warranty_ext_visit_trip_billing, warranty_ext_visit_labor_billing) retire that rule sentence. The KB carries it as "no longer in force", and the formula is never published.

## F2 — wording of the proration step: "from its fifth full year" vs `full_years >= 5`
- Location: `extended_policies[id=warranty_ext_prorated_share_acceptance].rule` / `.baseline.rule` / `compute_basis.proration_share`.
- Rule: "one half for the Ridgeline Limited Warranty from its fifth full year and for the Ridgeline Limited Plus Warranty from its tenth, one quarter for the Ridgeline Lifetime Limited Warranty from its tenth".
- Compute: `full_years >= K('limited_step_years')` (5) / `>= K('limited_plus_step_years')` (10) / `>= K('lifetime_limited_step_years')` (10), with `full_years = MONTHS(coverage_start_date, filing_date) // 12`.
- "From its fifth full year" can also be read as "during the fifth year", that is after 4 full years. The same sentence says "counting a year only once its anniversary has been reached", and `parameter_schema.insulated_glass_proration` says "each step applies from after_year onward". The KB carries the sentence verbatim and pins it as "once 5 full years have been reached; 4 full years give nothing". Suggest rewording to "once N full years have elapsed".

## F3 — "CareLine plan" vs the compute excluding the On-Call Service Account
- Locations: `warranty_ext_transfer_fee_confirmation.rule` (Member rate) and `warranty_ext_prorated_share_acceptance.rule` (Owner discount). Also the warranty_ext_missed_visit_fee and warranty_ext_visit_trip_billing rules.
- Rule: "A seller who holds an active CareLine plan enrolled at least the member waiver term …" / "For an owner who holds an active CareLine plan whose waiting period had ended by the acceptance date …".
- Compute: `plan_name != None and plan_name != 'On-Call Service Account'`.
- The service product's display name is "CareLine Service Plans", and the On-Call Service Account is one of its tiers. So in the transfer and share rules, "CareLine plan" does not on its own exclude the On-Call Service Account; the missed-visit and trip rules separate it in the next clause. The KB defines a CareLine plan as a plan of the CareLine Service Plans other than the On-Call Service Account, which matches the compute.

## F4 — 29 February anniversaries: term counting vs the whole-month count (edge case, informational)
- `warranty_registration_and_terms.rule`: "when that anniversary falls on a day the month lacks, it falls back to the last day of the month."
- Full years (`warranty_ext_prorated_share_acceptance.compute.full_years`) and elapsed months (`warranty_ext_transfer_fee_confirmation.compute.months_remaining`) use `MONTHS(...)`, which reaches a month only on the same day of the month. For a 29 February start, the anniversary is not reached on 28 February of a non-leap year.
- The two counts disagree only for a 29 February coverage start date. The KB renders each rule as its source states it.

## F5 — overwrite of the no-defect trip sentence: replaced_by leaves the "even inside the labor term" scope to the rule (informational)
- `warranty_ext_visit_trip_billing.overwrite[1]` retires "When the technician finds no covered defect, the plan's no-defect trip charge applies even inside the labor term."
- Its replaced_by does not restate that a no-defect visit is billed a trip charge even inside the labor term. That scope still holds through the policy rule's opening sentence ("… which is a visit outside the labor term or a visit at which the technician found no covered defect"), which the KB carries in the trip-charge hub. No still-in-force part is lost.

## Notes (no mismatch)
- `warranty_ext_visit_labor_billing.compute.billable_labor_hours` uses `RND(…, 1)`, and no rounding mode is stated ("booked … to one decimal place"). With an increment of 0.5 and allowances of 0.5 or 1.0, the billable hours are always multiples of 0.5, so the mode never changes a result.
- In `warranty_ext_missed_visit_fee.factors[repeat_rate_ladder].bindings`, `lifetime_missed` is the default count of the counting-window factor. The KB homes it in the repeat-rate document (covers), and the computation document states the lifetime count in words.
- The base rule text names internal codes (`warranty_msr_full_years`, `warranty_msr_no_shows`, `warranty_msr_breakage_claims_365d`, enum values such as `denied_out_of_term`, `approved_with_proration`, `prorated_parts_share`). The KB states these in business words, as the leak gate requires. Retired clauses are registered verbatim in `meta.superseded_clauses`.
