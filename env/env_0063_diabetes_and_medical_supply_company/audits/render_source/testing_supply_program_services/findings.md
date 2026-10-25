# Render-surfaced source findings — bgm (testing_supply_program_services)

Source: `tasks/testing_supply_program_services/bgm.extended.yaml` (sha256 28b5edc3…22847b), `task_tools.py` (sha256 ff767d51…f617c).
Every compute_basis quote and every prerequisite `policy_source` was checked mechanically as a verbatim substring of its rule: all verbatim.
The corpus renders the source as it stands. Where a finding forced a rendering choice, the choice is stated.

## F1 — the computation document's baseline.rule names four factors (hardship waiver)
- Location: `extended_policies[bgm_ext_hardship_cost_share_waiver].baseline.rule`
- Quote: "the waiver is the waivable cost share less every balance adjustment already posted against that posting, never below 0, times the payer share, the payment share, the age share and the household share, each of which is 1 as standard"
- Problem: the standard method names the four factor multipliers (payer_class_share, payment_effort_share, posting_age_share, household_relief_share) and says they are "1 as standard". A computation document that carries this sentence tells the reader that four shares exist and vary, which defeats the silent baseline.
- Rendering: the computation document `hardship_waiver_amount` states the waiver without the four multipliers. At baseline they are all 1, so the number is the same. Each share document states its own acting base: it multiplies the waivable cost share left after earlier adjustments, and the ceilings and rounding then apply to the reduced amount.

## F2 — one factor's method is assembled from the other five factors (courtesy reship)
- Location: `extended_policies[bgm_ext_courtesy_bridge_reship].factors[bridge_shape].ladder` and `.rule`
- Quote (rule): "When the days until the next refill may ship are more than 30, the courtesy reship instead ships the strips for the bridge days plus the transit days at the daily rate, times the repeat share and the sensor share, plus the reserve strips, divided by strips_per_billing_unit and rounded up to a whole unit, never more than the refill's units"
- Quote (ladder): "method: strips for the bridge days plus transit days at the daily rate and shares, rounded up"
- Problem: bridge_shape's tiers compose the outputs of bridge_day_convention, bridge_daily_rate, repeat_courtesy_share, sensor_wear_share and fingerstick_reserve, so this factor reads other factors. The assembly is held in non-factor bindings (`supply_left`, `bridge_days`, `bridge_strips`, `block_strips`, `result`). baseline.rule ("The standard courtesy reship is this: it replaces every unit of the refill it stands in for, one for one.") does not state it, so the computation document cannot carry that assembly and stay silent.
- Rendering: the bridge document (`courtesy_reship_bridge_quantity`) carries the source method as written, so it names the bridge days, daily rate, repeat share, sensor share and reserve strips. The computation document states only the one-for-one quantity, the shipping method and the transit days.

## F3 — the overwrite retires a phrase that does not conflict (non-covered strip charge)
- Location: `extended_policies[bgm_ext_noncovered_strip_charge].overwrite[0].superseded_clause`
- Quote: "that the payer denied, charged at the Larkfield cash price of the units concerned"
- Problem: the retired clause includes "that the payer denied". The extended policy still requires a payer denial ("When the payer denies a strip claim line …"), so only the pricing part ("charged at the Larkfield cash price of the units concerned") conflicts. The replaced_by does not restate the denial condition.
- Rendering: the base document registers the clause verbatim and marks it no longer in force for test-strip charges priced under the current basis.

## F4 — "first strip refill after a newly supplied meter" is undefined when there is no strip refill (new meter strip supply)
- Location: `extended_policies[bgm_ext_new_meter_strip_supply]`, compute `meter_newly_supplied: (F('meter_ship_date') or '') > latest_refill_ship` with `latest_refill_ship: … or ''`
- Rule quote: "A refill is the first strip refill after a newly supplied meter when the meter ship date on the program is later than the ship date of the program's latest strip refill."
- Problem: when the program has no strip refill yet, the rule's comparison is undefined. The compute treats any recorded meter ship date as "later", which has two effects:
  - `supply_span` gives 30 days instead of the tier's supply days.
  - `setup_allowance` gives setup_units_new_meter (1) instead of setup_units_new_program (2). The rule's new-program tier ("the first strip refill of a program activated within the last 30 days, with no earlier strip refill on it, adds setup_units_new_program units") can therefore be reached only by a program that records no meter ship date.
- Rendering: the source definition is carried verbatim in the supply-days and setup documents.

## F5 — the rule dates the earlier plan by withdrawal or completion, the compute by when it was logged (payment plan)
- Location: `extended_policies[bgm_ext_payment_plan_installment].factors[prior_plan_record]`, compute `withdrawn_plans` / `completed_plans` (`date_field='received_at'`)
- Rule quote: "A payment plan request on the program withdrawn within the last 12 calendar months takes withdrawn_plan_months_off installments off, even when another was completed in that span; one completed within that span, with none withdrawn in it, adds completed_plan_months_on installments"
- Problem: the rule dates the withdrawal or completion. The compute counts requests logged (`received_at`) within 12 months that now carry the withdrawn or completed status. The records hold no withdrawal or completion date.
- Rendering: rule wording carried.

## F6 — the compute has a floor of 1 block and a no-authorization fallback the rule never states (above-coverage notice)
- Location: `extended_policies[bgm_ext_above_coverage_notice]`, compute `pa_blocks: MX(1, (DAYS(pa_grant_from, pa_grant_through) + 1) // 30) if pa_grant_from else 1` and `pa_monthly_strips: ((pa_grant_units or 0) / pa_blocks) * …`
- Rule quote: "divided by the whole 30-day blocks of its approved span and multiplied by strips_per_billing_unit"
- Problem: the rule states neither the floor of 1 block (for a span under 30 days) nor the outcome when the prior-authorization tier has no payer prior authorization for test strips.
- Rendering: rule wording carried.

## F7 — two branches of the held-shipment rule are not stated (take-back)
- Location: `extended_policies[bgm_ext_superseded_strip_takeback]`, compute `stand_in_id: (not_received_repl_id or lost_repl_id) …` and `held_from: (stand_in_delivered_on or NOW) if stand_in_id …`
- Rule quote: "The shipment the customer holds is the replacement shipment recorded against the latest strip refill when that refill was replaced as delivered but not received or as lost in transit, its units counted and its days of use starting on the replacement's delivery date"
- Problem: the rule does not say which replacement is held when both a not-received and a lost replacement exist (the compute takes the not-received one). It also does not say what happens when the replacement has no proof of delivery (the compute starts the days of use today, giving 0 days).
- Rendering: rule wording carried.

## F8 — the Advance Beneficiary Notice price has an unstated condition (non-covered strip charge)
- Location: `extended_policies[bgm_ext_noncovered_strip_charge]`, compute `unit_price: (remit_allowed / class_allowance_units) if (P('liability_notice_type') == 'abn_cms_r_131' and remit_allowed > 0 and class_allowance_units > 0) else …`
- Rule quote: "on a tier whose liability_notice_type is abn_cms_r_131 when the denied claim carries a remittance, the allowed amount on that remittance divided by the units the treatment-class allowance gives for the supply days"
- Problem: the compute requires an allowed amount above 0 and allowance units above 0; the rule requires only that a remittance exists. A remittance with 0 allowed, or 0 allowance units, falls to the billed-charge price, a branch the rule does not state.
- Rendering: rule wording carried.

## F9 — the docstring promises a prepaid return label the tool never records
- Location: `task_tools.py`, `issue_return_authorization_3dfb992f`
- Quote: "Issue a return authorization, with a prepaid return label, for unopened sealed units …" and the return text "a prepaid return label is on its way to the customer."
- Problem: the tool body records no label; it only creates the return authorization row.
- Rendering: the docstring capability is carried as the tool contract.

## Base note (for the coordinator's base known-issues log; base text carried verbatim)
- `policies[bgm_combo_cgm_backup].formula.allowance_with_cgm: min(strips_per_90_days_insulin, strips_per_90_days_with_cgm)` disagrees with its rule ("the lower of the treatment-class allowance and strips_per_90_days_with_cgm") for a customer not treated with insulin. The base formula is not published.
