# Renderer scan-first STOP — product timebank, render round 1 (agent a63d01e16b90fd3c4)

Saved verbatim by the coordinator from the renderer's report (2026-10-18). Gate line read: `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`. No documents written.

**Scan.** I checked the 7 extended policies in `tasks/prepaid_service_hours/timebank.extended.yaml` and `task_tools.py` against XF_recipe.md. A scratch sweep passed: every `compute_basis` quote, every prerequisite sentence, every `baseline.rule` and every `replaced_by` appears verbatim in its own rule. Four policies hit the "assembly sentence names factor quantities" class (XF A.3/A.4). The project policy also has the A.5/26 problems listed under item 3.

1. **`timebank_ext_service_visit_draw`**, the rule and `compute_basis.result`:
   > "The figures the service-visit schedules below select replace the standard floor, multiplier and ratio and act on the visit's minutes in this order: the call-out floor raises the rounded minutes first, the call-out weighting then acts on the raised minutes, the band multiplier, the dispatch level ratio and the ClearPath rate multiply the result, and the product is rounded half up to draw_rounding_hours once, at the end."

   This names the outputs of the factors `service_callout_basis`, `service_band_rate`, `service_dispatch_level` and `service_clearpath_rate`.

2. **`timebank_ext_remote_session_draw`**, the rule and `compute_basis.result`:
   > "...act on the session's minutes in this order: the floors raise the rounded minutes first, the call-out weighting then acts on the raised minutes, the band multiplier, the level ratio and the ClearPath rate multiply the result, and the product is rounded half up to draw_rounding_hours once, at the end."

   This names the outputs of `remote_floor_minutes`, `remote_callout_basis`, `remote_band_rate`, `remote_level_ratio` and `remote_clearpath_rate`.

3. **`timebank_ext_project_time_draw`**, three problems:
   - **(a) Assembly sentence** (rule and `compute_basis.result`) names factor quantities:
     > "...with no order between the multipliers: the minutes schedule acts on the summed minutes first, the band multiplier acts on the group's band minutes while its other minutes keep a multiplier of 1, ..."
   - **(b) A quantity only one factor uses is defined in the plain rule.** It sits in non-factor binding `pj_window`, whose `compute_basis` is:
     > "A group's band minutes are, for a weekend group, its summed minutes raised to at least weekend_minimum_minutes, and for a weekday group, its after_hours-band minutes rounded up to the next multiple of 60."

     The compute line is `pj_window: MX(pj_total, K('weekend_minimum_minutes')) if (pj_day == 0 or pj_day == 6) else int((pj_aft + 59) // 60) * 60`. This restates the content of the `project_minutes_basis` factor and is used only through `project_band_rate`.
   - **(c) A plain quantity is defined through the factor schedules.** The undrawn-part sentence (`compute_basis` of `pj_p_a`/`pj_p_s`/`pj_p_t`/`pj_drawn_h`) reads:
     > "A group's undrawn part is its drawn minutes and block hours as the schedules below give them for all its logged lines, less the worked minutes and hours the block's ledger already carries..."

     The plain bindings `pj_p_a`/`pj_p_s`/`pj_p_t` embed the minutes schedule's weekend floor and after-hours rounding, for example `MX(pj_b_a + pj_a_a, K('weekend_minimum_minutes')) if (...) else pj_b_a + int((pj_a_a + 59) // 60) * 60) > pj_dm_a`. Which group gets figured therefore depends on factor content.
   - **Related rule-vs-compute mismatch.** `baseline.rule` says "draws its summed logged minutes, less any minutes already drawn for it, divided by 60". Compute instead subtracts ledger *hours* after conversion: `RND(MX(0, (pj_minutes_basis + pj_window * (pj_band - 1)) / 60 * pj_ratio * pj_discount_rate * pj_class_rate - pj_drawn_h), 2)`.

4. **`timebank_ext_extension_quote`**, the rule and `compute_basis.result`:
   > "The figures the extension schedules below select replace the standard percentage and hourly value or multiply the fee, in this order: the signing schedule sets the percentage, the standing schedule adds its points to that percentage, the valuation schedule sets the value of an hour, and the loyalty, recent-use and project schedules then multiply the fee those give; rounding to the cent happens once, at the end."

   This names the outputs of `signing_lead_rate`, `payment_standing_points`, `hour_valuation_basis`, `clearpath_loyalty_rate`, `recent_use_rate` and `engagement_commitment_rate`.

**Note (not a STOP on its own): `timebank_ext_visit_travel_entry`.** The rule says:
> "A travel figure of zero, whether the block's size carries onsite_trip_hours of zero or a schedule below sets the trip to zero, means no travel entry is drawn for the date."

The trip-value tier "the trip is that trip charge divided by the block's hourly_rate_usd" has no exception for sizes whose `onsite_trip_hours` is 0. Compute zeroes those sizes anyway (`RND(P('onsite_trip_hours') and tv_trip * ...)`). The rule only implies this, and the sentence's "a schedule below" would have to be dropped from the computation document. It could be fixed in the same round.

**Clean:** `timebank_ext_repeat_order_quote`, `timebank_ext_install_visit_draw` (both have generic assembly sentences), the overwrites (properly scoped), and the tool docstrings (no example values, no effects the body lacks).
