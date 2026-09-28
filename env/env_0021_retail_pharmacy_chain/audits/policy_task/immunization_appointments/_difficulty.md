# Policy-task audit — immunization_appointments / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude Opus 5.5 subagent), not the instantiation agent; no instantiation transcript or scratch material read.
- Freeze time: 2026-09-24T18:43Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Frozen inputs (sha256):
  - `env/env_0021_retail_pharmacy_chain/tasks/immunization_appointments/vax.extended.yaml` = `265f49f19cec59cf18d507b487e457d2d0c3aab6959d191276ed86ca9532df58`
  - `env/env_0021_retail_pharmacy_chain/tasks/immunization_appointments/task_tools.py` = `ffdaeeca577fb576543b8dd85eed9c444fe1b431546c4911bcf6e89312c8c00c`
  - Both match the hashes in the coordinator brief.
- Fields read: `blueprint/blueprint.yaml`, `blueprint/products/vax.yaml` (all of it), the `government_program` flag in `products/coverage.yaml` and the `vaccine_discount_pct` flag in `products/copay.yaml`, the signatures of the `share_tools.py` finders, the whole of `vax.extended.yaml` and `task_tools.py`.
- Masked and not read before this file was written: all of `tasks/0.json` and `tasks/1.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). No earlier audit of this difficulty exists. Sibling difficulties' audit folders were listed by name but not opened.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 with their OK lines; check_traceability deferred until the KB is published), the masked views with their hashes (re-hashed: task0 `76c6b55c…e931`, task1 `93c4e5b1…d3d`, both match), and the source hashes. The entry conditions are complete. The gates were cited and not re-run.
- Base copy: `diff` of `vax.extended.yaml` lines 1–1004 against `blueprint/products/vax.yaml` differs only by the trailing blank line, so the base section is a verbatim copy.

### policy_conflict_scan

The charter has six extended policies, and each writes one quantity through one tool:

| policy | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- |
| vax_ext_dose_invalidation_balance | vax_dose_invalidated, vax_course_reopened | doses_remaining | invalidate_series_dose_51b39017 | agent |
| vax_ext_resumed_course_opening | vax_course_opened | doses_remaining | open_resumed_course_fd79a681 | agent |
| vax_ext_resumed_dose_consent | vax_consent_signed | dose_number | sign_dose_consent_2c77f168 | user |
| vax_ext_series_dose_booking | vax_appointment_booked | days_ahead | book_series_dose_9b68cabc | agent |
| vax_ext_missed_dose_posting | vax_dose_administered | observation_minutes | post_missed_dose_006fe732 | agent |
| vax_ext_dose_charge_settlement | vax_dose_administered | patient_pay_usd | settle_dose_charge_857cec2f | user |

Overlapping subjects:
- `vax_dose_administered` is the subject of both posting and settlement. They write different fields (`observation_minutes` on the posted entry, and `patient_pay_usd` on that same entry, which the posting tool leaves `None`), through different tools, and settlement's scope sentence ("a dose … paid in cash and whose payment is still open on the dose record") starts where posting ends. No conflict.
- `doses_remaining` is computed by both invalidation (on the earlier course) and opening (on the new course), which are different rows. No conflict.

Triggers, eligibility and terminal states:
- Invalidation (state_due) and opening (on_request) do not collide with base `vax_agg_multi_holding`. A new course opens only when no course of the vaccination is scheduled or in_progress. `vax_course_eligibility` blocks a repeat only after a *completed* course. `vax_course_closure` expressly routes "a later wish to finish the series" to a new course in which earlier doses count.
- Booking, and base `vax_evt_booking`'s window and no-earlier-than-earliest-valid-date clauses, conflict for earliest dates beyond the window. See findings F-5.
- Consent is gated to an open course by base `dose_on_open_course`, whose `applies_to` includes `vax_consent_signed`. Consistent.

Cross-category read boundaries:
- Opening reads `coverage_claims`, booking reads `coverage_plans`/`coverage_claims`, posting reads `rx_prescriptions`/`rx_fills`, and settlement reads `copay_enrollments`/`copay_activity`, `coverage_plans.termination_date` and `rx_fills`.
- All are read-only and declared under `cross_category`. None writes outside `vax`.

Claimed scopes: the per-task claims can be read only from the task files, which are masked. The prerequisite graph splits the six policies into two connected components:
- {invalidation, opening, consent, booking} — root booking
- {posting, settlement} — root settlement

This matches the two masked views: task 0 is a booking request and task 1 is a payment request. Exclusivity and completeness are re-checked against `charter_scope` in the task files after the reveal.

### rule_compute_equivalence

This section checks each policy's `compute` against its `compute_basis` quotations and sweeps back sentence by sentence. It covers only mismatches and notable points. Every other binding has a verbatim `compute_basis` quotation that the expression implements.

- **vax_ext_dose_invalidation_balance**
  - `first_set_aside`: the rule's first tier says "Where every such entry carries a lot number and Kestrel reported **a later dose** of the course". The second tier says "…and Kestrel reported a later dose". The compute tests `reported_doses >= 1` (any reported dose, of any number). The rule's "later" is not implemented. **Finding F-3.**
  - `after_close_entries`: "the entries dated within the whole calendar months since the closing date" is implemented as `COUNT(within_months=MONTHS(closed_date, NOW))`. That is a window counted back from today and not "dated after the closing date". The two readings coincide whenever the whole-month count reaches back to the closing date or near it. Observation only.
  - `found_taken_off`: the Kestrel tier takes off `found_entries_kestrel` = 2 ("the dose and the registry copy of Kestrel's report of it"). The registry copy is also subtracted under `registry_copies` in the same rebuild, so an early Kestrel dose that has a registry copy is taken off three times. Observation (no world in this difficulty takes the Kestrel tier).
- **vax_ext_resumed_course_opening**
  - The rule says "every earlier dose that stands is carried: Kestrel's doses, doses documented by another provider, **and nothing else**". Later sentences of the same rule credit `credit_for_unmatched_copies` plan-billed outside entries and `credit_for_lone_undocumented` undocumented entries. Neither is a Kestrel dose or a documented outside dose. **Finding F-4.**
  - `credit_window_months`: the rule gives "zero months where the earlier course holds no dose". The compute tests `series_first_on != None`, that is, whether a *dose 1* entry exists. A course holding only later-numbered entries gets 0 months under the compute and a defined span under the rule. Observation.
- **vax_ext_resumed_dose_consent**
  - The rule says "Where the earlier course is closed and carries no invalidation entry, the dose number follows the doses Kestrel reported on it." In the compute that mode (`continue_mode == 1`) sets `positions_held = reported_on_record`, but `numbered_dose` never reads `positions_held` in mode 1. It returns `MAX(dose_number)+1` ("Otherwise the form covers the highest dose number on record plus one"). The tier method "follow the doses Kestrel reported on it" is therefore implemented nowhere, and the rule's two sentences disagree whenever Kestrel's reported count and the highest dose number differ. **Finding F-6.**
- **vax_ext_series_dose_booking**
  - Rule: "its clock runs from the invalid dose's date with the full minimum interval of the dose it repeats and no grace period". The compute uses `dose2_min_interval_days` when the latest number is ≤2, and `dose3_min_interval_days_from_dose2` otherwise. The compute drops the rule's own dose-3 floor ("with dose 3 also no earlier than the date of dose 1 plus the dose 3 minimum interval from dose 1") in this tier. The base reading of "the same minimum interval" is a separate issue. **Finding F-2.**
  - `result: MN(booking_window, …)`. See F-5.
- **vax_ext_missed_dose_posting**
  - The compute matches the rule tier for tier.
  - `refills_3m` counts `rx_refill` on all prescriptions, and the rule says "a prescription refill", so this is consistent.
  - `completion_extension` uses `doses_before + 1 >= doses_required` for "the dose completes the course". This ignores invalidated doses. Observation.
- **vax_ext_dose_charge_settlement**
  - The compute matches the rule.
  - The rule opens with "The charge is the vaccination's cash price, rounded to the cent half up." This is the baseline sentence, and the later tiers override it inside the same rule. It is a baseline-and-factors construction and not a conflict.
  - `starting_price` tier 1 uses `doses_on_record >= doses_required and plan_billed_doses == 0` for "every earlier dose of it was paid in cash **at Kestrel**". The "at Kestrel" part (store_id not null) is not implemented. Observation (tier not reached in this difficulty's worlds as far as the views show).
  - The rule's pharmacy-patient ladder gives 0 % to a patient with ≥3 pickups and <3 refills, and 2 % to one with 1–2 pickups (non-monotonic). The compute is faithful to this, and it is recorded under factor_ladders.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). All six tools are claimed.
- None of the docstrings names another tool or states a position in a sequence. The only "then" in each docstring ("The new course then appears…", "The dose then shows…") describes that tool's own effect.
  - `open_resumed_course` says "can take appointments". `post_missed_dose` says "the amount the patient pays is left open". `settle_dose_charge` says "whose payment is still open".
  - These describe record states, not orderings. They are hints, but they carry no ordering word and name no tool. Observation only.
- Each function body only creates or updates rows and refuses nothing. None checks status, consent, invalidation or payment state.
- uuid8s: `51b39017`, `fd79a681`, `2c77f168`, `9b68cabc`, `006fe732`, `857cec2f`. The six share no prefix, no suffix and no sequential pattern, which is consistent with independent generation. PASS.

### prerequisite_graph

All six policies fill `prerequisite`: invalidation `[]`, posting `[]`, and the others as follows.

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| resumed_course_opening | dose_invalidation_balance | value_input | outside_credit (binding exists) | state | invalidate_series_dose_51b39017 (= that policy's target_tool) |
| resumed_dose_consent | resumed_course_opening | state_gate | vax_evt_dose_administration.dose_on_open_course (real base eligibility gate, applies_to includes vax_consent_signed) | state | open_resumed_course_fd79a681 |
| series_dose_booking | resumed_dose_consent | state_gate | `vax_events.event_type` | state | sign_dose_consent_2c77f168 |
| series_dose_booking | dose_invalidation_balance | value_input | series_clock_days (binding exists) | state | invalidate_series_dose_51b39017 |
| dose_charge_settlement | missed_dose_posting | value_input | starting_price (binding exists) | state | post_missed_dose_006fe732 |

- Every `problem` points at another extended policy in this file. None points at a base policy or at itself.
- The graph is acyclic: invalidation → opening → consent → booking, invalidation → booking, and posting → settlement.
- Every `policy_source` is verbatim the final sentence(s) of the blocked policy's own `rule`. This was checked by string match against lines 1396–1398, 1671–1672, 1896–1899 and 2524–2526.
- `form` is `state` on every edge, and no edge carries a `fallback_reason`, which is consistent.
- Each `condition` restates its sentence at the same strength.
- No `prerequisite` text uses authoring-viewpoint wording ("in this task", "at the opening").
- Observation: the booking←consent edge is `state_gate` with `gate: vax_events.event_type`. That is a field name, not an eligibility gate. No base eligibility makes a consent a precondition of booking, so the gate exists only through the extended prerequisite sentence. This is a form defect with no demonstrable scoring consequence.

### prerequisite_sentences

Each edge was put through the four-point test (ordering connective / state named in record words / no tool, id or snake_case / strength matches condition). The test also checked uniqueness of the resolving write.

1. **opening ← invalidation**: "A resumed course's opening doses still needed are fixed only after every dose found too early on the earlier course carries its invalidation entry and the earlier course's valid doses still needed are restated."
   - Connective "only after". The state is record words: an invalidation entry on the dose, and the course's doses still needed. The sentence contains no tool or id, and its strength matches the condition.
   - Resolving write: the only write in this difficulty that creates a `vax_dose_invalidated` row and restates `doses_remaining` on an existing course is `invalidate_series_dose_51b39017`. One reading.
   - Derivation: the sentence plus the earlier course's history (a dose inside its minimum interval with no invalidation entry) plus the invalidation rule ("When a dose on a course is found not to count, the invalidation entry restates …") lead to the invalidation write. PASS.
2. **consent ← opening**: "The dose number a form covers is set only once the resumed course of the vaccination stands open on the patient's profile with its opening doses still needed."
   - Connective "only once". The state is record words (course, open, doses still needed).
   - Only `open_resumed_course_fd79a681` creates a course. PASS.
3. **booking ← consent**: "An appointment for the next dose of a series is not booked until a screening and consent form for that dose stands signed on the open course of the vaccination."
   - Connective "not … until". The state is record words.
   - Only `sign_dose_consent_2c77f168` writes `vax_consent_signed`. PASS.
   - Observation: for three-dose vaccines `consent_validity_days` is 7 (HepB/Zoster/RSV). The sentence therefore forces a consent that lapses before the dose whenever the booked date is more than 7 days ahead. The charter's own booking result may be up to 30 days ahead. This is a latent real-world incoherence. Whether it touches a task is judged per task.
4. **booking ← invalidation**: "Before the days ahead of that appointment are fixed, every dose on the series history given sooner than its minimum interval less the grace period must carry its invalidation entry."
   - Connective "Before". The state is record words. Unique write: the invalidation tool. PASS.
5. **settlement ← posting**: "The charge for a dose is settled only after the course history carries that dose as a given dose with its observation minutes recorded."
   - Connective "only after". The state is record words.
   - Only `post_missed_dose_006fe732` creates a `vax_dose_administered` row in this difficulty. PASS.

Other checks on the sentences:
- No depended-on rule restates a sentence that blocks on it.
- No second wording, tool name or policy id appears in any rule.
- No extended rule states a cross-problem order that grounds no declared edge. The invalidation and posting rules carry no ordering sentences.
- Settlement's scope sentence ("a dose given at Kestrel that is paid in cash and whose payment is still open on the dose record") is a state description that is consistent with, and covered by, edge 5.
- Base ordering sentences ("a patient who wants a different time has the open appointment cancelled first"; "A dose is given only when a screening and consent form … was signed") ground no edge of this charter. Observation.

### override_declarations

This is a sentence-by-sentence sweep of each extended policy against its `base_policy_refs`. It records findings only. Each consequence is demonstrated in the task file.

- **vax_ext_dose_invalidation_balance** (refs: vax_evt_invalid_dose, vax_evt_dose_administration; `overwrite: []`)
  - Base vax_evt_invalid_dose: "An invalid dose does not count toward the course: the course needs one more dose, …". The base account says: "doses … credited when the course opens and when a dose is found invalid". Together these fix the restated count at *the doses still needed before the entry + 1*. That is exactly this policy's own `baseline.rule`.
  - The extended rule replaces it, whenever the history holds more entries than the account explains, with a rebuild from the dose history ("the count is rebuilt as the valid doses the course requires less the dose entries that stand once registry copies, the dose found not to count, the dose 1 entries set aside and the entries set aside after closing are taken off").
  - The rebuild governs the scored `doses_remaining` and yields a different number from base. No `overwrite` entry names the base sentence. **Undeclared override — Finding F-1.**
  - Base "A dose is invalid when it was given earlier than its minimum interval less grace_period_days, or when the patient was below min_age_years" is followed (the `latest_too_early` definition). Base "A dose is invalidated at most once" is inherited.
  - Base "a dose given too early elsewhere and recorded as an outside dose is simply not counted" can be read as "no entry needed". The extended policy records an invalidation entry for outside doses (`found_entries_outside` tier). Here "simply not counted" sits in the charging context. Observation.
- **vax_ext_resumed_course_opening** (refs: vax_agg_multi_holding, vax_agg_visit_and_season, vax_course_eligibility, vax_course_closure; `overwrite`: the risk-condition attestation clause)
  - The declared replacement is unique.
  - Base vax_course_closure: "a later wish to finish the series opens a new course in which outside and earlier doses count where outside_record_accepted is true". The extended rule departs from this in four places, and none is declared:
    - "Where it closed more than 365 days ago, only Kestrel's own doses are carried": outside doses no longer count, although `outside_record_accepted` is true for every vaccination.
    - "Where Kestrel reported at least one dose and the plans show fewer paid claims than reported doses, only as many reported doses as there are paid claims are credited": earlier Kestrel doses no longer count.
    - "Where the earlier course is not closed, nothing is carried".
    - The credit window of `credit_months_long_series` = 60 months for a series spanning more than 365 days.
  - These are **undeclared overrides — Finding F-7.** The consequence arises only in worlds that reach those tiers, and is judged per task.
  - Base event `vax_course_opened.fields.doses_remaining: equal to doses_required at opening` is contradicted by any credited opening. The base *policy* vax_course_closure licenses crediting, so this is recorded as an observation.
- **vax_ext_resumed_dose_consent** (ref: vax_evt_dose_administration; `overwrite: []`)
  - Base says nothing about the consent's dose number. Its consent-validity, signer and open-course clauses are inherited. No conflict.
- **vax_ext_series_dose_booking** (refs: vax_evt_booking, vax_evt_dose_administration, vax_evt_invalid_dose; `overwrite: []`)
  1. Base vax_evt_invalid_dose: "the course needs one more dose, which is given no earlier than the invalid dose's date plus **the same minimum interval**". The "same" refers back to "its minimum interval" in the invalidity sentence, which is the interval the dose failed.
     - For a dose 3 that failed only the dose-1 interval (`dose3_min_interval_days_from_dose1`), base places the repeat at invalid date + that interval.
     - The extended compute uses `dose3_min_interval_days_from_dose2` from the invalid date. Its rule text says "the full minimum interval of the dose it repeats", which is itself ambiguous between the two dose-3 intervals.
     - **Undeclared override / competing clause on the scored quantity — Finding F-2.**
  2. Base vax_evt_booking: "For a later dose the appointment date is no earlier than the earliest valid date for that dose" together with "The appointment date is no more than booking_window_days_ahead days after today".
     - Base: an earliest valid date beyond the window leaves no bookable date.
     - The extended `result: MN(booking_window_days_ahead, …)` and rule "The appointment is never booked more than the booking window days ahead" book at the window, which is *before* the earliest valid date.
     - **Undeclared override — Finding F-5.**
  3. Base: "a same-day slot is bookable only until same_day_booking_cutoff_minutes before it starts". The extended rule says "where that date is today or already past the appointment is booked one day ahead". This narrows base but does not contradict it. Observation.
- **vax_ext_missed_dose_posting** (refs: vax_agg_visit_and_season, vax_evt_dose_administration, vax_evt_billing)
  - The declared override of the observation clause is unique after replacement.
  - The base billing order (VFC → Medicare → active coverage → cash) is inherited for the posted dose's route.
  - Base "The dose that brings the course's valid doses to doses_required is recorded as is_final_dose true" is inherited.
- **vax_ext_dose_charge_settlement** (refs: same three)
  - The declared override replaces the cash-price-less-club-discount sentence.
  - The replacement names the three reductions, the cap, the credit and a single rounding. It also changes the starting price ("the starting price is reduced once …"), which is covered by the same superseded clause's "cash_price_usd". Unique after replacement.
  - Base "Where insured_zero_cost_share is true … an insured dose costs the patient 0.00" is inherited (settlement is scoped to cash-paid doses).
  - Base vax_evt_invalid_dose's "The patient is not charged for the repeat dose where the invalid dose was given early by Kestrel" is not in `base_policy_refs` and is not handled by the charge ladder. The settlement tiers would charge such a repeat. Observation: no world in this difficulty reaches it.

### factor_ladders

Counts are shown as *declared* and then *surviving the tests below*.

**vax_ext_dose_invalidation_balance**
- Declared factors: 6. Method: counted_history, registry_copy, outside_first_dose, restatement_way. Parameter: found_dose, after_closing. `cross_difficulty`: none.
- Every ladder has 3 tiers, and every tier appears in the rule and in the `decides` binding.
- `after_closing` — **duplicate tier (Finding F-8)**.
  - Tier 1 selects `K('after_close_set_aside_reported')` = 0.
  - The fall-through ("In every other case every entry dated after the closing date is set aside") holds only when the course is not closed, where the compute gives `after_close_entries` = 0 because there is no `closed_date`, or when no entries fall after closing (0).
  - Wherever the fall-through applies it selects 0, which is tier 1's value. The ladder has two outcomes (0, n−1), not three.
- `counted_history`:
  - The open-course tier counts "only the dose entries dated within the whole calendar months since the course opened, plus one month". Whether a dose counts toward a series does not depend on how many months ago the course was opened. Observation (realism; this tier is not reached in any world of this difficulty as far as the views show).
  - The fall-through "only the doses Kestrel reported are counted" is always 0 where it applies (no Kestrel report). It is distinct from the other tiers.
- `outside_first_dose`: tier 1 "they all stand" and tier 2 "only the entries without a lot number are set aside" both test only "Kestrel reported a later dose". This is the F-3 rule/compute gap.
- Multi-source tiers: registry_copy (plan-billed outside entry ∧ Kestrel registry report), counted_history, outside_first_dose, after_closing.
- Surviving count: removing after_closing leaves 5 factors with one `parameter` (found_dose). That is **below the minimum of 2 `parameter` factors — F-8 consequence**.

**vax_ext_resumed_course_opening**
- Declared factors: 6. Method: carry_scope, kestrel_dose_credit, outside_dose_credit. Parameter: credit_window, copy_credit_rule, undocumented_credit_rule. `cross_difficulty`: kestrel_dose_credit → coverage (`coverage_claims`). Multi-source: kestrel_dose_credit (vax registry rows ∧ coverage paid claims).
- `copy_credit_rule` — **duplicate tier (F-9)**. Tier 1 "none is credited" gives 0. The fall-through "Where no such entry exists, nothing is credited for them" gives 0. The rule text itself gives both tiers the value zero.
- `undocumented_credit_rule` — **duplicate tier (F-9)**. Tier 1 "none of them is credited" gives 0. The fall-through "Where no such entry exists, nothing is credited for them" gives 0.
- `credit_window`:
  - Tiers: 600 months where the series spans ≤365 days, 60 months where it spans more, 0 where there are no doses. A longer series gets a *shorter* look-back, and 600 months is 50 years, which is no window at all.
  - No immunization business sets a record look-back by how long the earlier series took. Observation (realism). It cannot be demonstrated to move any scored number in this difficulty's worlds, because the 600-month tier includes every row.
- `carry_scope` tier 3 ("the earlier course is not closed") is essentially unreachable. Base vax_agg_multi_holding forbids a second course while one is scheduled or in_progress, and a completed non-repeatable course cannot be followed by another. Observation.
- Surviving count: 4 (carry_scope, credit_window, kestrel_dose_credit, outside_dose_credit), with **one `parameter`** (credit_window). That is **below the minimum of 2 — F-9 consequence**.

**vax_ext_resumed_dose_consent**
- Declared factors: 4. Method: numbering_continuation, repeat_numbering. Parameter: copy_positions_rule, unlotted_positions_rule. `cross_difficulty`: none.
- `copy_positions_rule` — **duplicate tier (F-10)**. Tier 1 is "hold copy_positions_matched positions each, that is none". The fall-through is "Where there are none, no position is affected". The value decided (`copy_positions`) is 0 in both.
- `unlotted_positions_rule` — **duplicate tier (F-10)**, the same way ("that is none" and "Where there are none, no position is affected").
- `numbering_continuation` tier 2 "follow the doses Kestrel reported on it" is not implemented (F-6).
- Surviving count: 2 factors (numbering_continuation with a partly unimplemented tier, and repeat_numbering), 0 `parameter`. That is **below 4 factors and below 2 `parameter`**.

**vax_ext_series_dose_booking**
- Declared factors: 6. Method: next_dose_clock, allowance_combination. Parameter: missed_visit, plan_check, resumed_series, outside_record. `cross_difficulty`: plan_check → coverage (`coverage_plans` variant's `government_program` ∧ `coverage_claims` rejected in 3 months). plan_check is multi-source.
- The tier values are distinct in every ladder.
- `missed_visit`:
  - Both non-fall-through tiers require "at least one cancelled appointment" in conjunction with the no-show count. A patient with three no-shows and no cancellation gets no missed-visit allowance. A patient with one no-show and one cancellation gets a day.
  - A scheduler that pads for unreliability weighs the no-shows. The cancellation conjunct is not a condition a pharmacy weighs for that pad, and it inverts the ladder's own logic. **Unreal-condition finding F-11.**
- `allowance_combination`: "added together" when the history's course is closed, and "only the largest" when it is open. Whether allowances stack by course status is a made-up method. Observation.
- The whole "scheduling allowance" quantity (days of padding after the earliest valid date) is a Kestrel-specific scheduling policy. It is asserted by the charter and is not contradicted by base. Observation.
- Surviving count: with missed_visit struck, 5 remain (3 `parameter`, 2 `method`). This still passes the bounds.

**vax_ext_missed_dose_posting**
- Declared factors: 5. Parameter: reaction_history, anticoagulant, immune_status, series_completion. Method: extension_attachment. `cross_difficulty`: reaction_history, anticoagulant and immune_status → rx. Multi-source: reaction_history (prior vax observation ∧ rx epinephrine status).
- The quantity is the post-vaccination observation period. The industry basis, which base itself encodes, is 15 minutes, or 30 minutes where there is a history of severe allergic reaction. The period exists to catch syncope and anaphylaxis. **Finding F-12 (unreal ladders):**
  - `reaction_history` tier 2: a patient whose earlier dose needed the extended watch but who holds *no* epinephrine prescription is observed for 20 minutes, which is *less* than the 30 given to the patient who carries an auto-injector. The value is inverted against the risk it addresses. No immunizer shortens the anaphylaxis watch because the patient lacks an EpiPen.
  - `anticoagulant`: 5 vs 3 extra minutes depending on whether "a prescription refill was dispensed in the last 3 calendar months". Refill recency has no bearing on post-injection monitoring. Anticoagulation is managed by needle choice and site pressure, not by lengthening observation.
  - `immune_status`: immunocompromise affects vaccine choice and interval, not the anaphylaxis or syncope watch. The 3 vs 1 minute split by whether a specialty prescription is on file is weighed by no immunizer.
  - `series_completion`: whether the dose completes the series has no bearing on reaction risk.
- Surviving count: only extension_attachment (a method over struck inputs) remains. That is **below 4 factors and below 2 `parameter`**.

**vax_ext_dose_charge_settlement**
- Declared factors: 6. Method: series_bundle. Parameter: savings_club, coverage_continuity, pharmacy_patient, reduction_ceiling, on_time_series. `cross_difficulty`: savings_club → copay; coverage_continuity → coverage; pharmacy_patient → rx; reduction_ceiling → copay. Multi-source: savings_club (copay enrollment parameter ∧ copay fee activity), coverage_continuity (coverage termination ∧ vax plan-billed dose), pharmacy_patient (pickups ∧ refills), on_time_series.
- The tier values are distinct in every ladder.
- Realism:
  - Series bundle pricing, a club discount that depends on paid membership, and an on-time series credit are recognisable retail promotions.
  - The coverage-continuity reduction (a discount because the plan recently ended) is unusual but coherent as a transition courtesy. Observation.
  - `pharmacy_patient` is non-monotonic: ≥3 pickups with <3 refills gets 0 %, while 1–2 pickups gets 2 %. A loyalty reduction that pays less loyal patients more is not a published treatment. Observation (it becomes a finding only where a world lands in the gap, which is judged per task).
- Surviving count: 6 (5 `parameter`, 1 `method`). Passes the bounds.

### findings

Each finding lists the tasks it bears on, so their files can pick up the demonstration. The task assignment rests on the prerequisite components: task 0 is the booking component and task 1 the payment component. Each task file confirms its assignment.

- **F-1 SOURCE-POLICY RED — undeclared override in vax_ext_dose_invalidation_balance.**
  - Symptom: the scored `doses_remaining` after an invalidation is rebuilt from the dose history.
  - Root cause: base vax_evt_invalid_dose ("An invalid dose does not count toward the course: the course needs one more dose") and the base account ("credited … when a dose is found invalid") fix the value at the prior count + 1. `overwrite: []` declares nothing.
  - Evidence: `vax.extended.yaml` lines 1010 and 1021–1031, against the base copy lines 913–914 (`vax_evt_invalid_dose.rule`) and line 24 (`accounts[doses].meaning`).
  - Consequence: demonstrated in 0.md (base gives 3, the extended rebuild gives 1).
  - Bears on: task 0.
- **F-2 SOURCE-POLICY RED — competing clauses for the repeat-dose clock (vax_ext_series_dose_booking vs base vax_evt_invalid_dose).**
  - Base: "given no earlier than the invalid dose's date plus the same minimum interval".
  - Extended rule: "the full minimum interval of the dose it repeats". The extended compute uses `dose3_min_interval_days_from_dose2`.
  - For a dose 3 invalid only against `dose3_min_interval_days_from_dose1`, base's "same" interval is the dose-1 interval, while the extended compute uses the dose-2 interval. There is no `overwrite` entry.
  - Consequence: demonstrated in 0.md.
  - Bears on: task 0.
- **F-3 SOURCE-POLICY RED (charter-global; no task consequence expected) — rule/compute gap in `first_set_aside`.**
  - The rule conditions on "Kestrel reported a **later** dose", and the compute on any reported dose.
  - In a world where Kestrel reported only dose 1 and outside dose-1 entries exist, the rule falls to "every dose 1 entry recorded from another provider is set aside", while the compute keeps them standing (or sets aside only the unlotted ones).
  - Bears on: task 0 (checked there).
- **F-4 SOURCE-POLICY RED (charter-global) — internal contradiction in vax_ext_resumed_course_opening.**
  - "every earlier dose that stands is carried: Kestrel's doses, doses documented by another provider, and nothing else" vs "Where such entries exist and no documented entry does, credit_for_lone_undocumented of them is credited" (and the unmatched-copy credit).
  - Take a course closed ≤365 days ago holding one cash outside entry without a lot number and nothing else. The first sentence carries nothing, and the second credits 1.
  - Bears on: task 0 (checked there).
- **F-5 SOURCE-POLICY RED (charter-global) — booking beyond the earliest valid date.**
  - Base vax_evt_booking: "For a later dose the appointment date is no earlier than the earliest valid date for that dose" and "The appointment date is no more than booking_window_days_ahead days after today".
  - Extended: "The appointment is never booked more than the booking window days ahead of today" with `result: MN(booking_window, earliest+allowance)`.
  - Where the earliest valid date is more than the window ahead, base has no bookable date, while the extended rule books at the window, before the earliest valid date. Undeclared.
  - Bears on: task 0 (checked there).
- **F-6 SOURCE-POLICY RED (charter-global) — consent numbering mode 1 unimplemented and self-contradictory.**
  - "the dose number follows the doses Kestrel reported on it" vs "Otherwise the form covers the highest dose number on record plus one".
  - The compute implements only the latter.
  - Bears on: task 0 (checked there).
- **F-7 SOURCE-POLICY RED (charter-global) — undeclared departures of vax_ext_resumed_course_opening from base vax_course_closure** ("outside and earlier doses count where outside_record_accepted is true"). These are the >365-day tier, the paid-claims cap on Kestrel doses and the 60-month window.
  - Bears on: task 0 (checked there).
- **F-8 SOURCE-FACTOR RED — `after_closing` ladder duplicates a value.** Tier 1 = 0 and the fall-through is always 0.
  - Consequence: vax_ext_dose_invalidation_balance is left with 1 surviving `parameter` factor.
  - Bears on: task 0.
- **F-9 SOURCE-FACTOR RED — `copy_credit_rule` and `undocumented_credit_rule` ladders duplicate a value** (tier 1 = fall-through = 0, stated so in the rule).
  - Consequence: vax_ext_resumed_course_opening is left with 1 surviving `parameter` factor.
  - Bears on: task 0.
- **F-10 SOURCE-FACTOR RED — `copy_positions_rule` and `unlotted_positions_rule` ladders duplicate a value.**
  - Consequence: vax_ext_resumed_dose_consent is left with 2 factors and 0 `parameter`.
  - Bears on: task 0.
- **F-11 SOURCE-FACTOR RED — `missed_visit` conditions on a cancelled appointment**, which no scheduler weighs for a missed-visit pad and which inverts the ladder.
  - The booking computation still keeps 5 factors.
  - Bears on: task 0.
- **F-12 SOURCE-FACTOR RED — the observation-minutes ladders are not immunization practice.** These are reaction_history tier 2 (inverted value), anticoagulant, immune_status and series_completion.
  - Consequence: vax_ext_missed_dose_posting is left with 1 surviving factor.
  - Bears on: task 1.
- Observations: the booking←consent `gate` is a field, not an eligibility gate. There is also the latent consent-validity-vs-booking-distance incoherence, the base event `doses_remaining` gloss, and the realism notes on credit_window, counted_history's open tier, allowance_combination and pharmacy_patient.

## closing_checklist

Not written. Step 4 closes a difficulty only when every task passes all four relationships, and the findings above (with their per-task demonstrations) prevent that. See the per-task verdicts in `0.md` and `1.md`.

Post-reveal note (recorded here below the pre-reveal charter-global section, after both tasks were revealed at or after 2026-09-24T18:47:59Z):
- `charter_scope` of task 0 is {invalidation, opening, consent, booking} with their four tools. Task 1 is {posting, settlement} with their two tools.
- The scopes are pairwise disjoint and together cover all six extended policies and all six task tools, which confirms the component split assumed above.
- The difficulty-wide `prerequisite` graph stays acyclic.
- The per-task verdicts:
  - Task 0: SOURCE-POLICY RED, CHAIN PASS, SOURCE-FACTOR RED, SOURCE-TASK RED.
  - Task 1: POLICY PASS, CHAIN PASS, SOURCE-FACTOR RED, TASK PASS.
- The closing checklist is therefore not written, and the instantiation gates were not re-run by this audit.
- Freeze-time correction: the "18:43Z" header above is the approximate start of writing. The file's last pre-reveal write (mtime) was 18:45:14Z.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent auditor.
- Frozen before any round-2 task file was read. The round-2 `tasks/*.json` were rewritten at 19:12:00Z and have not been opened.
- Inputs (sha256):
  - `vax.extended.yaml` = `b06f91e9073ac727944279543fb74cefef68f70e7946262d7ac6fdb96b17b151`. **Changed** from round 1 (`265f49f1…`), so every charter-global check below is re-derived in full, not carried forward.
  - `task_tools.py` = `ffdaeeca…c00c`, unchanged. The tool-module checks are carried forward on that hash.
- The blueprint was not touched by the rework:
  - blueprint mtimes are all 16:18–16:26Z;
  - `vax.yaml` sha256 is `d1a48287…a2`;
  - the base copy (lines 1–1004) is still verbatim, differing only by the trailing blank line.
- Gate snapshot and rebuilt views: supplied by the coordinator. I re-hashed both views and they match (task0 `75040a12…ca4`, task1 `42fd65ab…9c5`).
- Masked: all round-2 GT fields.
- Method:
  - I read the six extended policies in full (excluding `inputs`).
  - A script checked that every `compute_basis` sentence occurs verbatim in its policy's `rule` and that every compute binding has a basis. Both checks passed for all six policies.
  - Each rule sentence was then swept against its compute by hand.

### policy_conflict_scan (r2)

- The six policies, target tools and owners are unchanged.
- **One change of computed quantity.** vax_ext_missed_dose_posting now `computes: dose_number` (it was `observation_minutes`).
  - Its observation overwrite is gone (`overwrite: []`). The posted dose's `observation_minutes` is therefore governed by base vax_evt_dose_administration: "observed for observation_minutes, or extended_observation_minutes when they report a history of severe allergic reaction".
  - That is a caller-fact branch, with no computation.
- Overlapping subjects: still `vax_dose_administered` (posting and settlement), with different fields and tools. No conflict.
- Booking and base window: now consistent (see F-5 below).
- The prerequisite graph is unchanged (same five edges, same sentences). It splits the policies into the same two components.

### rule_compute_equivalence (r2)

Round-1 items:
- **F-3 closed.**
  - The rule now reads "Kestrel gave a later dose of the course at one of its stores".
  - `kestrel_later_doses` counts dose-2 and dose-3 entries with a store.
  - The rule and the compute agree.
- **F-6 closed.**
  - Mode 1 now reads "the form covers the dose after the doses Kestrel reported on it", with `result = reported_on_record + 1`.
  - "Otherwise … highest dose number on record plus one" is scoped to "Where the dose number is counted from positions".
  - The rule and the compute agree.
  - Observation: inside mode 2 that "Otherwise" branch is unreachable, because mode 2 requires an invalidation entry and there are only two reasons.
- Opening `credit_window`: the rule now says "zero months where the earlier course holds no dose 1", matching `series_first_on != None`. The round-1 observation is closed.
- Settlement tier 1 now implements "at a Kestrel store" (`outside_on_record == 0`). The round-1 observation is closed.

New items:
- **N-4 SOURCE-POLICY RED (charter-global; no task consequence found pre-reveal) — store restriction added in compute only.** There are two instances.
  1. Posting. Rule: a copy is matched "when it is dated no more than a match window of days after **the latest dose Kestrel gave on the course**". Compute: `kestrel_latest_dose_on: LATEST(…, store_id=F('store_id'))`, which considers only the course's own store.
  2. Settlement on-time credit. Rule: "after **the dose 1 Kestrel gave at the course's store**", with the second tier "after a dose 1 that **no Kestrel store** gave". Compute: `kestrel_first_doses` counts a dose 1 from *any* store.
  - Consequence (instance 2): take a dose 1 that Kestrel gave at a different store. Under the rule neither credit tier holds, so the credit is 0. The compute gives `on_time_credit_kestrel`, 10.00.
  - Consequence (instance 1): take a Kestrel dose at another store. The rule matches from it, while the compute ignores it.
  - Two passages, same situation, different conclusions.
- Booking `result`, observation: where the earliest date is beyond the window, the compute returns `earliest_days_ahead` as a number, while the rule says "no appointment is booked today". The compute value in that branch is not a booking. Whether to write is decided by the rule. No scored consequence.
- **N-2 SOURCE-POLICY RED — internal contradiction in vax_ext_missed_dose_posting.** The two sentences in conflict are:
  - Numbering: "Where Kestrel gave no dose of the course, the number is one past every dose entry on it." (line 2352)
  - Undocumented entries: "…unlotted_positions_documented between them **where Kestrel gave none** and a documented cash-paid outside entry exists" (line 2312).
  - Live zoster: "**where Kestrel gave none** all but one of them are set aside until the pharmacist confirms the product" (line 2315).
  - Situation 1: an RZV course with no Kestrel dose, one documented cash outside entry and two unlotted cash outside entries. The undocumented sentence gives positions 2, so dose 3. The numbering sentence gives dose 4.
  - Situation 2: an RZV course with no Kestrel dose and two pre-2017-10-20 entries. The live-zoster sentence gives dose 2. The numbering sentence gives dose 3.
  - The compute implements only the numbering sentence, because `positions_held` uses the set-asides only when `kestrel_given >= 1`. The two "Kestrel gave none" tiers are therefore promises the compute never keeps.

### action_binding_and_uuids (r2)

- Carried forward: `task_tools.py` is unchanged (`ffdaeeca…`). Every uuid8 is independent, no body refuses or judges a prerequisite, and no docstring states an order.
- The `(target_tool, computes)` pairs are still unique across policies. The posting's `computes` is now `dose_number`, and no other policy claims the `post_missed_dose` + `dose_number` pair.
- PASS.

### prerequisite_graph and prerequisite_sentences (r2)

- The five edges, their `policy_source` sentences, forms, kinds, gates and `resolved_by` are textually unchanged.
- Each sentence is still the verbatim final sentence of its blocked rule. Checked by string search:
  - opening: "A resumed course's opening doses still needed are fixed only after…"
  - consent: "The dose number a form covers is set only once…"
  - booking: both sentences
  - settlement: "The charge for a dose is settled only after…"
- The graph is acyclic. The single-writer uniqueness of each state is unchanged, because the tool module is unchanged.
- The round-1 verdicts stand: PASS, with the `gate: vax_events.event_type` form observation.
- The settlement sentence still waits on "its observation minutes recorded". Those minutes are no longer a computed quantity, but they are still a field only the posting writes. Unchanged.

### override_declarations (r2)

- **F-1 closed.**
  - vax_ext_dose_invalidation_balance now declares `vax_evt_invalid_dose`: "An invalid dose does not count toward the course: the course needs one more dose", replaced by the closed-course rebuild sentence. The merged semantics are unique.
  - Observation: the `replaced_by` quotes only the closed-course sentence, while the open-course rebuild also departs from "one more dose". No world in this difficulty takes the open tier.
- **F-2 closed.**
  - vax_ext_series_dose_booking declares `vax_evt_invalid_dose` "which is given no earlier than the invalid dose's date plus the same minimum interval".
  - It replaces it with "the full minimum interval that separates the invalid dose from the dose before it, with no grace period, and a repeated dose 3 is also given no earlier than the date of dose 1 plus the dose 3 minimum interval from dose 1 less the grace period days". The same wording is in the rule.
  - For a dose 3 this names the dose-2→dose-3 interval, plus the dose-1 floor, so the 112-days-from-the-invalid-date reading is excluded.
  - The compute now includes the dose-1 floor (`MX(…, dose3_from_dose1 - grace - DAYS(dose1, NOW))`).
- **F-5 closed.**
  - The rule now reads "where the earliest date itself lies beyond the booking window, no appointment is booked today".
  - The cap applies only when the earliest date is within the window, which is consistent with base "no earlier than the earliest valid date".
- **F-7 closed.**
  - vax_ext_resumed_course_opening now declares `vax_course_closure` "a later wish to finish the series opens a new course in which outside and earlier doses count where outside_record_accepted is true", replaced by "A resumed course credits earlier doses only as set out here …".
  - The >365-day tier gains the reason "until the outside records are confirmed again".
- **F-4 closed.** "and nothing else" was removed. The rule now says "every earlier dose credited under the rules below is carried", which is consistent with the copy and undocumented credit rules.
- Posting now has `overwrite: []`. It inherits base observation minutes and base billing, and base says nothing about dose numbering for a posting. No conflict.
- Settlement: the declared override is unchanged and still unique.

### factor_ladders (r2)

**Invalidation** (6 factors: method counted_history, registry_copy, outside_first_dose, restatement_way; parameter found_dose, after_closing)
- **F-8 closed.** after_closing:
  - tier 1: all after-close entries lotted ∧ a Kestrel store dose → `after_close_set_aside_documented` = 0
  - tier 2: all lotted ∧ no Kestrel dose → n−1
  - fall-through: "otherwise, including where any such entry carries no lot number" → all set aside (n ≥ 1 when an unlotted after-close entry exists)
  - The fall-through now reaches a nonzero value, so the tiers are distinct.
- counted_history's open tier is now "only the dose entries that carry a lot number are counted". The round-1 realism observation is closed.
- Surviving: 6, with 2 `parameter`. Passes.

**Opening** (6: method carry_scope, kestrel_dose_credit, outside_dose_credit; parameter credit_window, copy_credit_rule, undocumented_credit_rule; cross coverage)
- **F-9 closed.**
  - copy_credit_rule is 0 (Kestrel reported) / MN(n, 1) (no report ∧ a paid claim) / n (no report ∧ no paid claim).
  - undocumented_credit_rule is 0 (a documented entry exists) / MN(n, 1) (none ∧ Kestrel reported) / n.
  - The fall-throughs now reach n.
- credit_window is now 120 months for a series spanning ≤365 days and 240 for one spanning more. A longer series now gets a longer look-back. The round-1 realism observation is closed.
- Observation (realism): copy_credit_rule credits *fewer* unmatched plan-billed entries when a paid claim exists (≤1) than when none does (all). Corroboration reduces credit. The two tiers are not equal, so this is not a duplicate. It is recorded as an observation.
- Surviving: 6, with 3 `parameter`. Passes.

**Consent** (4: method numbering_continuation, repeat_numbering; parameter copy_positions_rule, unlotted_positions_rule)
- **F-10 closed.** copy_positions is 0 each / together 1 / one each; unlotted_positions is 0 each / together 1 / one each. The fall-throughs are reachable with nonzero values in mode 2.
- Surviving: 4, with 2 `parameter`. Passes.

**Booking** (6)
- **F-11 closed.** missed_visit is now 2 / 1 / 0 by the no-show count alone. The cancellation conjunct is removed.
- Surviving: 6. Passes.

**Posting** (rewritten; 5 factors: method numbering_basis, live_zoster_records; parameter copy_match_window, copy_position_rule, undocumented_position_rule. No `cross_difficulty`.)
- **F-12 closed**, in the sense that the observation-minute ladders are removed.
- live_zoster_records realism: `recombinant_available_on: 2017-10-20` is the real licensure date of the recombinant zoster vaccine. Setting aside earlier (live-vaccine) entries is sound practice.
- **N-1 SOURCE-FACTOR RED — copy_position_rule duplicates a value.**
  - Tier 1 ("Kestrel reported a dose of the course") selects `copy_positions_reported` = 0 per matched copy.
  - The fall-through holds exactly when Kestrel reported none *and* no documented cash-paid outside entry exists. Those are the conditions under which copy_match_window falls to "no window at all, so that no entry is matched" (−1), so `matched_copies` = 0 and the fall-through's "one each" is always 0.
  - Tier 1 and the fall-through therefore both select 0 on every world. The ladder has two outcomes.
- **N-3 SOURCE-FACTOR RED — dead tiers (consequence of N-2).**
  - `unlotted_positions` and `live_set_aside` reach the number only when "Kestrel gave a dose of the course" (the numbering tier 1).
  - For undocumented_position_rule, only tier 1 ("Kestrel gave a dose") can ever reach the scored number. Tiers 2 and 3 never move it: tier 2 is contradicted (N-2), and tier 3 coincides with numbering's "every dose entry".
  - For live_zoster_records, tier 2 ("Kestrel gave none: all but one set aside") can never reach the number. The ladder has two effective outcomes: RZV with a Kestrel dose sets all aside, and any other vaccination sets none aside.
  - These are ladders of fewer than three live tiers.
- Surviving: numbering_basis (method) and copy_match_window (`parameter`, 3 / 0 / −1, distinct). That is **2 factors with 1 `parameter`**, which **fails the bounds** (4–6 factors, 2 `parameter`).
- Multi-source: copy_match_window tier 1 (Kestrel registry report ∧ date proximity of a plan-billed outside entry).

**Settlement** (6, unchanged factor set)
- The cap values are now 22 / 18 / 100.
- coverage_continuity now reads "ended, by its termination date".
- on_time_series has a store restriction in the rule (see N-4).
- Tiers are distinct. The pharmacy_patient non-monotonic observation still stands.
- Surviving: 6. Passes.

### findings (r2)

**Round-1 findings, re-verified against the r2 charter:**

| id | r2 status |
|---|---|
| F-1 | closed |
| F-2 | closed |
| F-3 | closed |
| F-4 | closed |
| F-5 | closed |
| F-6 | closed |
| F-7 | closed |
| F-8 | closed |
| F-9 | closed |
| F-10 | closed |
| F-11 | closed |
| F-12 | closed (removed) |

**New in r2** (the rewritten posting policy and a store restriction that exists only in the compute):
- **N-1 SOURCE-FACTOR RED**: copy_position_rule has a duplicate tier. Bears on task 1.
- **N-2 SOURCE-POLICY RED**: the posting rule contradicts itself for courses where Kestrel gave no dose. It has no consequence on a world where Kestrel gave a dose; checked in 1.md.
- **N-3 SOURCE-FACTOR RED**: dead tiers in undocumented_position_rule and live_zoster_records. Together with N-1, the posting computation keeps 2 surviving factors. Bears on task 1.
- **N-4 SOURCE-POLICY RED (charter-global)**: a store restriction that differs between rule and compute, in the posting match window and the settlement on-time credit. Checked on task 1's world.

**Observations:** the partial `replaced_by` of F-1 (open tier), the booking beyond-window compute branch, the corroboration-inverted copy credit, the unreachable "Otherwise" in consent mode 2, and the `gate: vax_events.event_type` form.

### post-reveal note (revision 2)

- Revealed at or after 2026-09-24T19:17:44Z, after the r2 charter-global and per-task frozen sections were on disk.
- `charter_scope`: task 0 has the four resumed-series policies, and task 1 has posting and settlement. The scopes are disjoint and complete, and the graph is acyclic.
- Per-task verdicts, r2:

| task | policy | chain | factor | task | overall |
|---|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | **RED** (N-1/N-3 surviving count 2; the scored `dose_number` stamped on the appointment and consent) | **RED** (gold `observation_minutes` 2 vs 30 in the task's own tracing and under base) | **RED** |

- Charter-global items remaining RED: N-1, N-2, N-3 and N-4.
- The difficulty does not close. The closing checklist is not written, and the instantiation gates were not re-run by this audit.

## revision_3

### charter_global_frozen (revision 3)

- Frozen before any round-3 task file was read (`tasks/*.json` mtime 19:23:06Z, not opened).
- Inputs:
  - `vax.extended.yaml` = `4ab13261647a2b7a0a3c1296bd4d5b564b974fb94e0bb3f4a1dcd0653e3c1b80`. **Changed** from r2 (`b06f91e9…`), so the charter-wide sections are re-derived.
  - `task_tools.py` = `ffdaeeca…c00c`, unchanged. Its checks are carried forward.
- Blueprint: untouched. `vax.yaml` is `d1a48287…`, mtime 16:25Z, and the base copy is still verbatim.
- Both views re-hashed and match: task0 `75040a12…` (identical to r2), task1 `4575f1c7…`.
- A copy of the r3 charter is kept in my own scratch subfolder for later rounds.

**What changed.**
- I read the full r3 text of all six extended policies (rule, compute, factors, overwrite, prerequisite).
- The four resumed-series policies (invalidation, opening, consent, booking) are identical to the r2 text dumped in the round-2 audit: rule, overwrite, params, compute, ladders and baselines.
- Changes are confined to **vax_ext_missed_dose_posting**:
  - a new overwrite
  - a new sentence on printed dose numbers
  - the "Kestrel gave no dose" numbering is now counted from positions
  - the match window's fall-through is now 0 days
  - the undocumented-position tiers are re-keyed
  - the match window is restricted to the course's store in the rule
- And to **vax_ext_dose_charge_settlement**: the on-time credit compute (`course_store_first_doses`).

A script re-check passed: every `compute_basis` sentence is verbatim in its rule, and every binding has a basis.

### re-derived charter-wide sections (r3)

**policy_conflict_scan**
- The subjects, tools and owners are unchanged. The two components and scopes are unchanged.

**override_declarations**
- The new overwrite on vax_ext_missed_dose_posting reads as follows:
  - It supersedes vax_evt_dose_administration: "A dose is given only when a screening and consent form for that dose was signed no more than the consent validity days before, … never by Kestrel staff for them."
  - It replaces it with: "A dose posted after the visit is covered by the screening and consent form signed for the appointment it was given at no more than the consent validity days before, … whatever dose number the appointment and the form print; …".
  - The replacement is unique for posted doses.
- **Reach check** (the coordinator asked for this):
  - The superseded sentence is verbatim the condition of base eligibility `consent_current`, which applies to `vax_dose_administered`.
  - In this difficulty the only write that creates a `vax_dose_administered` row is `post_missed_dose_006fe732`.
    - Settlement's subject is `vax_dose_administered`, but it gives no dose; it only records the payment on an existing row.
    - The four resumed-series policies write no dose row.
    - Task 0's consent ← opening gate is `dose_on_open_course`, a different eligibility, and it is untouched.
  - So inside this difficulty the supersession reaches only posted doses. **No consequence for task 0.**
  - Observation: the superseded clause governs *every* dose, while the replacement speaks only of "a dose posted after the visit". For a non-posted dose, the merged text leaves it open whether base's "for that dose" rule still applies. No write in this difficulty gives a non-posted dose, so this cannot be demonstrated as a consequence here.
- The other overwrites (invalidation, opening ×2, booking, settlement) are unchanged from r2.

**rule_compute_equivalence**
- **N-4 closed.**
  - Posting: the rule now reads "the latest dose Kestrel gave on the course at the course's store", matching `kestrel_latest_dose_on … store_id=F('store_id')`.
  - Settlement: tier 1 now uses `course_store_first_doses` (dose 1 at the course's store), and tier 2 still requires `kestrel_first_doses == 0` ("a dose 1 that no Kestrel store gave"). A Kestrel dose 1 given at another store gets 0 under both rule and compute.
- **N-2 closed.**
  - The rule now reads "Where Kestrel gave no dose of the course, the number is also counted from positions, but no entry can be matched as a registry copy, so only undocumented entries and live zoster records are set aside".
  - The compute's third branch is `dose_entries - (unlotted_entries - unlotted_positions) - live_set_aside`.
  - The undocumented and live-zoster "Kestrel gave none" tiers now reach the number, and they agree with the numbering sentence.
- New sentence: "The dose number printed on the appointment or the form is the booking system's own count and is not the number the posted dose takes." It makes no computation claim.

**prerequisite_graph / prerequisite_sentences**
- Unchanged. The same five edges and verbatim sentences. Acyclic. PASS.

**action_binding_and_uuids**
- Tools are unchanged. PASS, carried forward.

**factor_ladders — posting** (5 declared factors: method numbering_basis, live_zoster_records; parameter copy_match_window, copy_position_rule, undocumented_position_rule)
- **N-1 closed.**
  - copy_match_window's fall-through is now `copy_match_days_other` = 0, meaning "the same day only", instead of no window.
  - In copy_position_rule's fall-through world (no report, no documented outside entry), a copy dated the same day as Kestrel's course-store dose is matched and holds "one each". The value is n ≥ 1, which differs from tier 1's 0.
  - Values across the tiers: 0 / MN(n, 1) / n.
- **N-3 closed.**
  - undocumented_position_rule (0 each where a documented outside entry exists / together 1 where none exists and Kestrel reported / one each otherwise) now feeds the number in both numbering branches that count positions.
  - live_zoster_records tier 2 (Kestrel gave none, all but one set aside) now feeds numbering's third branch.
  - All tiers are live.
- **N-5 SOURCE-FACTOR RED (new) — numbering_basis: tiers 1 and 3 select the same method, and the fall-through is not the baseline.**
  - Tier 1 is "count positions, setting aside matched copies, undocumented entries and live zoster records". The fall-through is "count positions with no copy matching, setting aside undocumented entries and live zoster records only".
  - A copy can be matched only against "the latest dose Kestrel gave on the course at the course's store". Where Kestrel gave no dose (the fall-through), there is no such date, so `matched_copies` = 0 and tier 1's formula gives exactly the fall-through's number. In compute terms, tier 1's expression with `kestrel_latest_dose_on` = None reduces term for term to the third branch.
  - The ladder therefore has two methods: count positions, or take the account.
  - The factor's declared `baseline` `positions_held: dose_entries` ("count every dose entry", the r2 fall-through) is no longer any tier's method. The fall-through tier is not the baseline.
  - Consequence: numbering_basis is struck. The posting keeps 4 surviving factors: copy_match_window, copy_position_rule and undocumented_position_rule (all `parameter`, 3 in total) and live_zoster_records (`method`). That is within the bounds, 4–6 with ≥2 `parameter` and ≥1 `method`.
  - Bears on task 1, but only through the ladder defect itself. The count still holds.
- The settlement ladders are unchanged apart from N-4. There are 6 surviving factors.
- The resumed-series ladders are unchanged from r2 and pass.

### findings (r3)

| finding | r3 status |
|---|---|
| N-1 | closed |
| N-2 | closed |
| N-3 | closed |
| N-4 (both instances) | closed |
| **N-5** | **SOURCE-FACTOR RED, new**: numbering_basis tiers 1 and 3 select the same method, and its fall-through ≠ its baseline. Bears on task 1. |

- Observation: the new consent overwrite's superseded clause is wider than its replacement. There is no consequence inside this difficulty.
- The round-2 per-task items T1-4 (count), T1-5 (stamp) and T1-6 (the gold `observation_minutes` argument) are judged in `1.md` revision_3.

### post-reveal note (revision 3)

- Revealed at 2026-09-24T19:26:34Z, after all r3 frozen sections were on disk.
- Scopes: unchanged, disjoint and complete. The graph is acyclic.

| task | policy | chain | factor | task | overall |
|---|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | **RED** (N-5 / T1-7: numbering_basis tiers 1 and 3 are one method, and its baseline is not its fall-through) | PASS | **RED** |

- Round-2 REDs: N-1, N-2, N-3, N-4, T1-4, T1-5 and T1-6 are all verified closed.
- The difficulty does not close while N-5 stands. The closing checklist is not written, and the instantiation gates were not re-run by this audit.

## revision_4

### charter_global_frozen (revision 4)

- Frozen before any round-4 task file was read (`tasks/*.json` mtime 19:28:58Z, not opened).
- Inputs:
  - `vax.extended.yaml` = `a8c07bff54e124f57e1f7c723c371c02f9015d24f614827c836b82e11b88fe6f`. Changed from r3 (`4ab13261…`).
  - `task_tools.py` = `ffdaeeca…`, unchanged.
- Views: task0 `75040a12…` and task1 `4575f1c7…`, both unchanged from r3. `cmp` of the r3 and r4 task1 view files shows them identical.
- The base copy is still verbatim (a byte comparison differs only by the trailing newline).
- **Diff against my saved r3 copy** (`…/scratchpad/audit_vax_ia/r3.extended.yaml`, a structural comparison of the parsed YAML):
  - top-level keys, base `policies`, `variants` and `events`: identical
  - invalidation, opening, consent, booking and settlement: **no field changed**
  - **only vax_ext_missed_dose_posting changed**, in the fields `rule`, `overwrite`, `compute`, `compute_basis` and `factors`
  - This confirms the reworker's statement.
- Carried forward on unchanged hashes and unchanged text:
  - the charter-wide sections of r3 for the five untouched policies
  - action_binding_and_uuids
  - prerequisite_graph and prerequisite_sentences (no `prerequisite` field changed)

### re-derived for vax_ext_missed_dose_posting (r4)

**Text diff, r3 → r4:**
1. `rule`, numbering: "Where Kestrel gave no dose of the course, the number is also counted from positions, but no entry can be matched…" becomes "Where Kestrel gave no dose of the course, the number is one past every dose entry on it."
2. `compute` `positions_held`, third branch: `dose_entries - (unlotted_entries - unlotted_positions) - live_set_aside` becomes `dose_entries`.
3. Live zoster, in rule and compute: "where Kestrel gave a dose … every such entry is set aside, and where Kestrel gave none all but one …" becomes "where Kestrel reported its dose of the course to the state registry every such entry is set aside, and where Kestrel gave a dose it has not yet reported all but one of them are set aside …; otherwise no entry is set aside for its date". In the compute, `reports_on_course >= 1` gives all, and `kestrel_given >= 1 and reports_on_course == 0` gives all but one.
4. `overwrite.replaced_by` and `rule` gain: "A dose given and recorded at the visit itself is given only when a screening and consent form for that dose was signed no more than the consent validity days before, counted in calendar days with the signing date as day 0."

**Checks:**
- A script check passed: every `compute_basis` sentence occurs in the rule, every binding has a basis, and the `replaced_by` text occurs verbatim in the rule.
- **N-5 closed.**
  - numbering_basis now has three tiers: count positions (excess entries ∧ a Kestrel dose), take the account (no excess ∧ a Kestrel dose), and count every dose entry (no Kestrel dose).
  - The three are distinct methods. Tier 1 applied in the fall-through's domain still removes undocumented entries when a documented outside entry is on the course, so it differs from "every dose entry".
  - The factor's baseline `positions_held: dose_entries` is now exactly the fall-through, and matches `baseline.rule` ("one past the dose entries on the course").
- **N-2 and N-3 stay closed.**
  - The "no Kestrel dose" branch now counts every entry. None of the position ladders (copy, undocumented, live zoster) claims to act in that branch: each is scoped "Where the number is counted from positions", and the live-zoster fall-through "otherwise no entry is set aside" agrees with it.
  - Every tier of each position ladder is reachable inside numbering tier 1, which applies where Kestrel gave a dose:
    - copy_position_rule: reported / unreported with a documented entry / unreported with no documented entry and a same-day copy
    - undocumented_position_rule: documented present / no documented ∧ reported / no documented ∧ unreported
    - live_zoster_records: reported / Kestrel dose unreported / otherwise
  - No rule sentence contradicts another in any situation I constructed.
- N-1 and N-4 are untouched by the diff and remain closed.
- **Consent-overwrite scope observation (r3): addressed.** The replacement now restates base's rule for a non-posted dose ("a dose given and recorded at the visit itself … for that dose"). The superseded clause and its replacement now cover the same set of doses, and the merged semantics are unique for both kinds of dose.
- Realism observation: live_zoster_records now keys its first two tiers on whether Kestrel's own dose was reported to the registry. Whether a 2016 record is a live-zoster record does not depend on that, so the condition is weak as a business criterion. It is a reconciliation-confidence gate, as the r3 "Kestrel gave / gave none" keying also was, and I accepted that keying in r3. The three tiers select distinct outcomes (all / all but one / none). Recorded as an observation, consistent with the r3 treatment.
- Surviving posting factors: 5, with 3 `parameter` and 2 `method`. Within the bounds.

### findings (r4)

- N-5 is **closed**. There are no new charter-level defects and no regressions in the five untouched policies.
- The remaining observations are unchanged:
  - the gate-form of `vax_events.event_type`
  - the closed-date near-miss that the cap makes score-inert
  - the seeded "dose 3" against the base event gloss
  - the partial `replaced_by` of F-1 (open tier)
  - the live-zoster keying observation above

### post-reveal note (revision 4)

- Revealed at 2026-09-24T19:30:21Z, after the r4 frozen sections.
- Task 0: **PASS**. Task 1: **PASS**.
- All four relationships hold for both tasks.

## closing_checklist

Written after revision 4, when both tasks pass all four relationships. The final form is `vax.extended.yaml` `a8c07bff54e124f57e1f7c723c371c02f9015d24f614827c836b82e11b88fe6f` and `task_tools.py` `ffdaeeca577fb576543b8dd85eed9c444fe1b431546c4911bcf6e89312c8c00c`.

- **Audit files.**
  - `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside.
  - Revisions 1–4 are appended in order, and no earlier text was rewritten. Freeze-time corrections are appended as notes.
  - The latest comparison sections (revision_4) both carry PASS.
- **Coverage and scope.**
  - The six extended policies are fully covered: task 0 has invalidation, opening, consent and booking, and task 1 has posting and settlement.
  - The scopes are pairwise disjoint and span each whole problem tree.
  - All six task tools are used by gold. Each has an independently generated, frozen uuid8 (51b39017, fd79a681, 2c77f168, 9b68cabc, 006fe732, 857cec2f), and none refuses or judges a prerequisite.
- **Problem trees.**
  - Task 0 has 3 prerequisite problems and 2 `value_input` edges (the minimum is 2); its user-owned write is the consent.
  - Task 1 has 1 prerequisite problem and 1 `value_input` edge (the minimum is 1); its user-owned write is the settlement.
  - Every edge is unmet at `frozen_time` and bears weight. The difficulty-wide `prerequisite` graph is acyclic.
- **Computations.**
  - Every computation declares a self-sufficient `baseline.rule` and 4–6 factors with at least 2 `parameter` and 1 `method`: invalidation 6, opening 6, consent 4, booking 6, posting 5, settlement 6.
  - Each task has a multi-source factor and a cross-difficulty factor with seeded rows. Task 0 reads coverage through kestrel_dose_credit and plan_check. Task 1 reads copay, coverage and rx through the settlement.
  - Every ladder has at least three distinct tiers stated in its rule, and every factor bears weight against an honest baseline.
  - The whole-baseline fall-back numbers differ from gold: invalidation 3 vs 1, opening 3 vs 1, consent 1 vs 3, booking 1 vs 7, posting 5 vs 2, settlement 229.99 vs 151.45.
- **Instantiation-stage gates on the final form.**
  - The coordinator re-ran them for round 4 on exactly these hashes: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire, all rc=0 with their OK lines.
  - check_traceability is deferred until the KB is published.
  - Per the brief, the auditor cites the snapshot and did not run the gates itself.
- **Remaining observations** (not grounds for rework):
  - the booking ← consent `gate: vax_events.event_type` is a field, not an eligibility id
  - task 0's booking lands on day 7 of a 7-day consent
  - task 1's closed-date near-miss is score-inert under the cap, though other near-misses move the score
  - task 1 seeds a "dose 3" appointment and form on a two-dose series; the extended rule declares the printed number non-authoritative
  - F-1's `replaced_by` quotes only the closed-course rebuild
  - the live-zoster tiers are keyed on Kestrel's registry report
  - some ladders are unusual but coherent Kestrel-specific conventions: scheduling allowances, corroboration-inverted copy credit, the pharmacy-patient non-monotonic gap
- **The difficulty passes the source-layer policy-task audit.**

## revision_5

### charter_global_frozen (revision 5)

- Frozen before the round-5 task files were read (`tasks/*.json` mtime 19:33:23Z, not opened).
- Inputs:
  - `vax.extended.yaml` = `a8c07bff…fe6f`, **unchanged**. `cmp` against my saved r4 copy (`…/scratchpad/audit_vax_ia/r4.extended.yaml`) is byte-identical.
  - `task_tools.py` = `5931824baab43bf59f680cd8f2e066cbe983c1f26b9c2e1a1023254ccc59cdc8`, **changed** from r4 (`ffdaeeca…`).
  - Views: unchanged (`75040a12…`, `4575f1c7…`).
- Carried forward by the unchanged charter hash, per the re-audit rule:
  - policy_conflict_scan
  - rule_compute_equivalence
  - prerequisite_graph and prerequisite_sentences
  - override_declarations
  - factor_ladders
- **Re-derived** because the tool-module hash moved: **action_binding_and_uuids**. Also checked: whether any tool now judges a prerequisite, and whether any docstring moved.

### action_binding_and_uuids (r5)

The reworker claims the change is behaviour-identical and touches nothing else. Each part of that claim was verified.

1. **Nothing else in the module moved.**
   - I did not keep a copy of the r4 file, so I reconstructed it from the r5 file:
     - deleted the `_CivilDate` class;
     - put back `from datetime import date, timedelta` above `from erlbench import ToolContext, tool`;
     - put back the single booking line `appt = (date.fromisoformat(today) + timedelta(days=int(days_ahead))).isoformat()` in place of `appt = _CivilDate._add_days(today, int(days_ahead))`.
   - The reconstruction hashes to exactly `ffdaeeca577fb576543b8dd85eed9c444fe1b431546c4911bcf6e89312c8c00c`, the r4 hash.
   - So the complete r4→r5 diff is these three edits and nothing else: all six tool signatures, owners, docstrings (Args and Returns), bodies and uuid8s are byte-identical. The module docstring is unchanged too.
2. **Date results are identical.**
   - I extracted `_CivilDate` from the module with `ast`, without importing the module, and compared `_add_days(t, n)` against the old `date.fromisoformat(t) + timedelta(days=n)` on 200,014 cases.
   - The cases covered 14 edge cases (leap days 2000/2024/1900/2100, year ends, 0001-01-01 − 1, 9999-12-31 + 1) and 200,000 random dates across 0001–9999 with offsets up to ±4,000,000 days.
   - **0 mismatches.** This includes the error cases: both raise `OverflowError` outside 0001–9999.
   - Input is always `ctx.now()[:10]`, a valid ISO date, so the old `fromisoformat` `ValueError` path for malformed strings is not reachable.
   - Task 0's booking: `_add_days('2026-09-24', 7)` = `2026-10-01`, as before.
3. **The private helper exposes no tool.**
   - `_CivilDate` has no decorator. `erlbench.tools.collect_specs` collects only callables carrying `__toolmeta__`.
   - Loading the module with `erlbench.loader.load_tool_specs(…, 'task')` yields exactly the six tools: invalidate_series_dose_51b39017, open_resumed_course_fd79a681, sign_dose_consent_2c77f168, book_series_dose_9b68cabc, post_missed_dose_006fe732 and settle_dose_charge_857cec2f. Their owners and rw flags are unchanged.
4. **The validator error is resolved and the ctx interface is respected.**
   - None of `erlbench/validate.py` `_FORBIDDEN_TOKENS` occurs in the r5 text. The r4 error token `from datetime` is gone.
   - The `ctx` members used are {create, find, make_id, now, update}, all within `_CTX_ALLOWED`.
5. **No new guard.** The helper raises only in the out-of-range case, as `datetime` did. No tool body gained a check, refusal or prerequisite judgement. The docstrings are unchanged and still state no order.

- `(target_tool, computes)` uniqueness and the uuid8 independence are unchanged, because the names and uuid8s are identical.
- **Section verdict: PASS.** The claim is verified: the change is behaviour-identical, limited to the booking tool's date arithmetic, and adds no tool.

### findings (r5)

- No new defects. No regressions. The round-4 PASS state and the closing checklist stand. The checklist's final-form hashes are now `vax.extended.yaml` `a8c07bff…` and `task_tools.py` `5931824b…` (see the post-reveal note).

### post-reveal note (revision 5)

- Revealed at 2026-09-24T19:34:51Z. Task 0: **PASS**. Task 1: **PASS**.
- The closing checklist written at revision 4 **stands for the r5 final form**: `vax.extended.yaml` `a8c07bff54e124f57e1f7c723c371c02f9015d24f614827c836b82e11b88fe6f` and `task_tools.py` `5931824baab43bf59f680cd8f2e066cbe983c1f26b9c2e1a1023254ccc59cdc8`.
- The uuid8 and tool-contract items are re-verified in revision_5 § action_binding_and_uuids.
- The coordinator's r5 gate snapshot on these hashes is all rc=0: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire.
- The whole-scenario validator's `from datetime` lint no longer matches the module.
- **The difficulty passes the source-layer policy-task audit on the r5 final form.**
