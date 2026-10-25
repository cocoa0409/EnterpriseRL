# Render-source notes — alignment (extended, alignment_plan_service)

Source: tasks/alignment_plan_service/alignment.extended.yaml + task_tools.py. Corpus: docs/alignment/ (59 docs). Base text was carried verbatim; nothing below was rendered around.

Mechanically verified: every compute_basis quote, every replaced_by, every baseline.rule and every prerequisite policy_source is verbatim in its rule; every superseded_clause is verbatim in its base rule.

## Source mismatches / issues

1. **[medium] Overwrites that retire a clause still in force (self-referencing replaced_by).**
   - alignment_ext_open_visit_labor → alignment_evt_service retires "On a plan the alignment is plan_included, with charge_amount 0.00, when alignment_msr_interval_reached is true ... which restarts the interval when early_price_counts_as_interval is true." Its replaced_by keeps "the purchase-day alignment and every alignment that is not priced as an open work order stay plan_included or member_early_price under the base rule" — the only base statement of that rule is the retired clause, which the corpus must mark "no longer in force". The hub carries the replaced_by as written; a reader following it back finds the clause marked retired.
   - alignment_ext_readjustment_parts → alignment_evt_readjustment retires "The readjustment labor is free (charge_amount 0.00); parts needed are charged as parts_charge under the parts warranty only when the part itself failed within parts_warranty_months and parts_warranty_miles." Its replaced_by says "every other readjustment keeps free labor and charges its parts under the base parts warranty" — the base parts warranty sentence is inside the retired clause.
   - (lower) alignment_ext_open_visit_parts restates the remainder in full ("carries any of parts_charged_list the vehicle needed, plus steering_angle_reset_charge, plus adas_recalibration_charge under the base rule"), so it is self-sufficient; the household/renewal overwrites of alignment_purchase_pricing likewise restate the ordinary-plan pricing and purchase-visit alignment in full.

2. **[medium] Factor independence — alignment_ext_term_renewal.** grace_period_anchor decides `in_grace`, which reaches the result only through the non-factor binding `granted_rate: "renewal_rate if in_grace else 0"` — it gates another factor's output. With renewal_grace_rate at its baseline (0) the grace factor has no effect, and the sentence "The renewal rate is given only to a renewal inside its grace period; outside it no renewal rate is given." cannot sit in the silent computation doc. Rendered in the renewal-rate factor doc and restated in the grace-period doc, so those two factor docs each name the other's subject ("grace period" / "renewal rate").

3. **[low] Result-assembly sentences that reference factor quantities (all six policies).** The ordering sentences bound to non-factor bindings (`result`, `combined_rate`) — e.g. "The three credits are subtracted after the cardholder rate has been applied", "The two rates are added into one rate that is applied once to plan_price", "Both credits are subtracted after the cardholder rate has been applied", "The tier's steering_angle_reset_charge is added after both rates" — name factor quantities, so the silent computation docs cannot carry them. Carried instead in each factor doc as its own acting base ("subtracted after any cardholder labor rate has been applied", "added to the household rate ... applied once to the plan price", "does not apply to the steering angle sensor reset charge, which is added after it", "never combined by addition with another rate").

4. **[low] Undefined branch — alignment_ext_household_enrollment.protection_credit.** Rule: "when the customer holds an active Crestline Road Hazard Plus 36-Month Protection or Crestline Road Hazard Life-of-Tread Protection certificate, the credit is per_tire_protection_credit for each tire that certificate covers". When the customer holds both kinds (or two qualifying certificates) the rule does not say which certificate's tire count applies; compute takes the Plus 36-Month certificate's covered_tire_count (first found).

5. **[low] Rule vs compute — alignment_ext_cancellation_settlement.processing_fee.** Rule: "and the plan also has an earlier request that was withdrawn"; compute `withdrawn_at` is the latest withdrawn request with no check that it predates the pending request.

6. **[low] Rule vs compute — alignment_ext_cancellation_settlement.deduction.** Rule: "Each deducted alignment's value is multiplied by the deduction type share of the alignment performed"; compute applies `td_share` (type of the latest tire-day alignment) to all `n_td` tire-day alignments — diverges only with more than one included alignment of different types on the install date.

7. **[low] alignment_ext_readjustment_parts.baseline.params** lists parts_warranty_months and parts_warranty_miles, which the baseline.rule ("parts the store listed on it at their list price, rounded to the nearest cent") does not read.

8. **[low] Docstring — confirm_alignment_cancellation_b0865de9.refund_amount** says "positive (0.00 when nothing is refunded)", self-contradictory; the body does not check sign. Rendered as "USD with 2 decimal places, 0.00 when nothing is refunded".

## round 2

Source re-fingerprinted: alignment.extended.yaml sha256 ed09e0e1…, task_tools.py sha256 04e41c28…. All compute_basis / replaced_by / baseline.rule / policy_source quotes verbatim in their rules; base policies unchanged.

Re-rendered (factors restructured to independent percentage reductions and credits): all 6 hubs or their changed clauses (labor replaced_by, readjustment replaced_by — XF-S closed, renewal "in place of the tire bundle price", refund_amount docstring), all 6 computation docs' covers (labor/parts/household/renewal/readjustment `reductions`; cancellation `n_td`), parts / readjustment / renewal computation prose (kit charge, parts amount, reinstatement charge 20.00 after 30 days), and 27 factor docs. Factor `alignment_type_share` → `alignment_type_reduction` (new doc alignment_type_labor_reduction_44da15a9), `guarantee_slip_share` → `guarantee_slip_reduction` (new doc guarantee_slip_reduction_755f45bb), `renewal_grace_rate` → `renewal_usage_rate`; the two retired files were deleted. XF-a..l closed: every factor doc now states its effect on a computation-document quantity only (pricing base, kit charge, parts amount, plan price, labor/parts/renewal/household charge) with "worked out on its own"; no factor doc names another factor's subject (vocabulary scan clean). N-1 hypothetical 224.99 changed to 229.99. Source notes 1–8 closed by the source rework except as below.

Remaining source mismatches:
- [low] confirm_alignment_cancellation_b0865de9.refund_amount docstring still reads "2 decimal places, positive; the amount is never negative and is 0.00 when the refund works out to nothing" — "positive" sits beside a 0.00 value; rendered as "never negative, and 0.00 when the refund works out to nothing".
- [low] alignment_ext_cancellation_settlement.processing_fee: rule "the age runs to the registration date of the latest such withdrawn request" (a withdrawn request registered on or before the pending request's registration day); compute takes `withdrawn_at` = the latest withdrawn request overall and tests `DAYS(withdrawn_at, pending_at) >= 0`, so a plan whose latest withdrawn request postdates the pending one but which also has an earlier withdrawn request falls to `fee_pending` instead of the earlier withdrawn date. Edge only.
- [info, not render-side] CP-1 from the KB audit (tire line "complimentary alignment check" attribute) depends on the tires product render.

RENDER round 2: DOCS OK, TRACEABILITY OK
