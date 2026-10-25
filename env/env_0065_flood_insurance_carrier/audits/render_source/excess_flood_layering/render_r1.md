# Renderer source-scan findings — product excess, render round 1 (renderer agent adbc037a55c9000f9)
Saved verbatim by the coordinator from the renderer's final message (the renderer STOPPED with 0 docs written). All findings are in tasks/excess_flood_layering/excess.extended.yaml.

## Blocking findings

**F1. Two factor quantities multiplied together** (`excess_ext_loss_of_use_payment`, factors `claim_age_rate` and `interest_due_anchor`)
- Rule: "interest is the new loss-of-use payment times the yearly rate times the days late over 365."
- Compute: `late_interest: lou_due * interest_rate_pct / 100 * days_late / 365`
- `interest_rate_pct` belongs to `claim_age_rate` and `days_late` belongs to `interest_due_anchor`; both default to '0'. Neither factor changes the result on its own: either one set to 0 makes interest 0 whatever the other says. To state its effect, each factor document would have to name the other factor's quantity.

**F2. Rule says calendar months, compute counts whole months** (`excess_ext_loss_of_use_payment`, factor `displacement_period_end`)
- Rule: "where there is no such sale and the report is dated more than the tier's maximum months after the date of loss, it is multiplied by those maximum months over the displacement months"
- Compute: `displacement_months: MX(1, MONTHS(date_of_loss, report_date))` and `period_fraction: ... ((max_months / displacement_months) if displacement_months > max_months else 1)`
- Example: loss on 2025-01-10, report on 2026-01-25, 12-month maximum. The report is more than 12 months after the loss, so the rule cuts. `MONTHS` gives 12, which is not greater than 12, so the compute doesn't cut.

**F3. Same mismatch for certificate age** (`excess_ext_renewal_term_premium`, factor `certificate_source`)
- Rule: "the one received latest, surveyed no more than the tier's maximum certificate age before it was received" (the tier maximum is 10 years)
- Compute: `nfip_cert_age_months: MONTHS(<ec_survey_date>, <recorded_date>)` and `elevation_credit_mult: ... nfip_cert_age_months <= P('ec_max_age_years') * 12 ...`
- Example: surveyed 2015-03-01, received 2025-03-20. That's more than 10 years, so the rule rejects it. `MONTHS` gives 120, which is ≤ 120, so the compute accepts it.

**F4. No reading when no underlying declarations are on file** (`excess_ext_limit_increase_premium`, factor `layer_position`)
- Compute: `underlying_dwelling_limit: LATEST('excess_changes', 'underlying_building_limit', ..., event_type='excess_underlying_evidence_received')` and `layer_relativity: K('relativity_high') if underlying_dwelling_limit + F('excess_building_limit') >= ...`
- That value is None when no declarations rows exist. The base rule allows this: "when the underlying is a Tidemark NFIP Dwelling Form or HomeFlood policy, the Tidemark policy record itself is that evidence". The compute then errors on None plus a number, and the rule ("... 100 percent otherwise") doesn't say what applies in that case.

**F5. Branch that can never apply** (`excess_ext_limit_increase_premium`, factor `signing_window` against its own prerequisite)
- Branch: "for an increase signed when fewer than 60 days of the term remain, the charged share is nothing and the increase is made as of the term end"
- Prerequisite: "The additional premium for a limit increase is figured only once the policy record carries the term in which the increase takes effect, from that term's start up to, but not including, its end."
- An increase made as of the term end falls outside the record's term ("not including, its end"). So this branch is always blocked by the prerequisite. Once the renewal is booked, fewer than 60 days no longer remain, and the other branch applies instead. If the renewal can't be booked, the rule never says what happens.

**F6. Undefined term** (`excess_ext_limit_increase_premium`, factor `rate_derivation`)
- Rule: "times the share the scheduled dwelling charge makes of the scheduled dwelling and personal property charges together"
- This policy's rule never defines "scheduled dwelling charge" or "scheduled personal property charge". Only the compute pins them: `F('excess_building_limit') / 1000 * dwelling_rate` and `F('excess_contents_limit') / 1000 * contents_rate`.

**F7. Overwrites that retire clauses still governing other cases**
Every `replaced_by` names its own scope, but each sends the out-of-scope cases back to "the base rule". That base rule is the retired clause itself, and its content isn't restated:
- `excess_ext_renewal_term_premium` over `excess_premium_rating`: "every other term premium remains under the base rating rule". New-business premiums are governed by the retired sentence.
- `excess_ext_limit_increase_premium` over `excess_waiting_period`: "a new policy and every other change remain under the base waiting rule". A new policy's waiting period is the retired clause.
- `excess_ext_limit_increase_premium` over `excess_endorsements`: "a decrease and every other endorsement remain under the base endorsement rule". The pro-rata decrease credit is in the retired clause.
- `excess_ext_sale_cancellation_return`, four overwrites over `excess_cancellation_refund`: "every other cancellation remains under the base cancellation rule". The retired clauses are the signed-request gate, "PROPERTY_SOLD takes effect on the closing date on the settlement statement", the minimum-earned pro-rata method, and the paid-claim bar. Each still governs other cancellations.
- `excess_ext_loss_of_use_payment` over `excess_claim_intake_pol`: retires "Payment is due within claim_payment_days calendar days after the later of the agreed proof of loss and the underlying settlement record." Its `replaced_by` says "building and personal property payments remain under the base due-date sentence", which is the retired sentence.

## Lower-priority findings

- **N1. Defined once, used by a single factor.** These bindings aren't part of any factor, so the computation document must claim them, but only one factor reads them:
  - renewal: `home_homeflood_id`, used only by `renewal_loss_history`.
  - limit increase: `zone_factor`, `dwelling_rate`, `contents_rate` and `floor_premium`, used only by `rate_derivation`; `home_nfip_id`, used only by `primary_loss_recency`.
  - loss of use: `sale_closing` and `max_months`, used only by `displacement_period_end`; `pay_days`, used only by `interest_due_anchor`.
- **N2. Voided payments are counted.** Renewal loss history says "where at least one layer payment or two or more primary payments stand", but `primary_paid_recent` and `layer_paid_recent` count every paid entry, including ones later voided.
