# Render-source findings — install (round 1)

Source: `env/env_0060_window_replacement_company/tasks/installation_scheduling_and_job_charges/install.extended.yaml` + `task_tools.py`.
These source issues were found while rendering. The docs carry the source as written; none of them was rendered around.

## R1. An overwrite retires a whole general sentence that still applies to every other condition (replaced_by keeps it in force)

- `install_ext_trim_capping_charge.overwrite[0]` and `install_ext_interior_casing_charge.overwrite[0]` both retire this `install_site_charges.rule` sentence:
  > "Conditions found or requested at the home are charged on the job, each at the method's rate, on the date the work is done."
- Both `replaced_by` texts then keep that same sentence in force for everything else:
  > "...every other condition found or requested at the home, apart from new interior casing that the customer approves, which is priced under its own rule, remains charged on the job at the method's rate on the date the work is done." (trim capping)
  > "...every other condition found or requested at the home, apart from exterior trim capping that the customer approves, which is priced under its own rule, remains charged on the job at the method's rate on the date the work is done." (casing)
- Effect: the base document has to mark the whole sentence **no longer in force**, even though it still governs rot repair, stucco/mortar patching, storm-window removal, window-treatment removal and upper-story work, including the "on the date the work is done" timing. The only in-force statement left is the rule text inside the two extended hubs.
- Related: the base sentences that are not retired, "New interior casing is charged per opening only where the method does not include it; exterior trim capping is charged per opening only where the method offers it and does not include it", still read as a flat per-opening charge. The two extended policies now price these items on weighted openings with volume tiers, adders and discounts.
- Suggested fix: narrow the overwrite so it retires only the capping and casing application of the "each at the method's rate" basis, for example by splitting the base sentence or retiring the per-opening capping and casing sentences instead.
- As rendered: the sentence is registered as retired in `site_condition_job_charges_7a9bf5a8.json`, and the "every other condition ... remains charged ..." clause is carried in the two hubs (`exterior_trim_capping_approval_7b0ce5ad.json`, `interior_casing_approval_883e505e.json`).

## R2. A parameter_schema description restates a retired clause

- `parameter_schema.openings_per_crew_day`: "Openings (or door units) one crew installs per crew day with this method; crew days planned are the units divided by this, rounded up (count)."
- `install_ext_crew_date_booking.overwrite[0]` retires `install_scheduling`: "Crew days planned are the job's units divided by the method's units per crew day, rounded up to a whole day."
- If the facet copied the schema description, it would teach the retired clause as if it were in force. As rendered: the facet `installation_methods_and_crew_pace_1c3bf7d4.json` gives the pace figure only. The retired clause is carried, marked no longer in force, in `crew_scheduling_and_installation_day_rules_e9ea9eeb.json`.

## R3. Undefined branch: wait adder when the job has no booked crew date

- `install_ext_company_reschedule_credit.rule`: "The wait adder follows the days from the crew date Ridgeline gave up to the crew date the job is now booked for: more than 14 days adds $40.00; 4 to 14 days adds $15.00; fewer than 4 days adds nothing."
- Compute: `wait_days: "DAYS(co_prev, F('scheduled_date')) if F('scheduled_date') else 0"`. When the company reschedule released the date and the job is back to opened with no booked date, compute quietly uses 0 days (no adder). The rule has no branch for that case.
- As rendered: the ladder is stated as the source states it (`rebooking_wait_credit_adder_8dcc606e.json`), and no branch was added.

## R4. Rule band does not match compute: sill adder below 1 linear foot

- `install_ext_lead_safe_fee.rule`: "when it covers 1 to 10 linear feet it is $30.00; when there is no rot repair there is no sill adder."
- Compute: `sill_adder: "K('rot_adder_many') if rot_feet > K('rot_many_feet') else (K('rot_adder_few') if rot_feet > 0 else 0)"`. Rot-repair units are linear feet and may be fractional, so a total above 0 and below 1 foot falls in no rule band, but compute charges $30.00.
- As rendered: the bands are stated as the rule states them (`rotted_sill_lead_disturbance_197154ef.json`).

## R5. Undefined branch: visit basis with 0 crew days held (minor)

- `install_ext_failed_access_fee.rule` covers "3 or more", "2" and "1 crew day held". Compute's else-branch (`P('failed_access_fee')`) also takes 0 crew days held. `book_crew_date_2f98f590` accepts `crew_days_planned` as any "non-negative integer", so 0 can occur in records. The rule says nothing about that case.
- As rendered: the three rule rows only (`held_crew_block_visit_basis_b54f9dd5.json`).

## Note (not a mismatch)

- `install_ext_permit_filing_fee`: the binding `own_signed` belongs to no declared factor, so the computation document has to cover it, but only the `shared_filing_share` ladder uses it. The factor document states the 30-day test between the two contracts' signed dates.
