# Policy-task audit — appointment_booking_and_missed_visits / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent of the instantiating agent), unattended run.
- Freeze time: 2026-10-05T05:22Z. Written before any task's GT was revealed. Nothing in this section comes from `evaluation_criteria`, `computations` or any other masked field.
- Frozen inputs (sha256):
  - `tasks/appointment_booking_and_missed_visits/series.extended.yaml` = `b0b7fffdfb3dd46949faf3cba45962560aa1086d08a3f819cbbe8a304000f394` (the orchestrator view copy has the same hash)
  - `tasks/appointment_booking_and_missed_visits/task_tools.py` = `78e73f667bc89e3fa81eef1199129ba1204607f9e38acbd1d237324a7240a74f` (view copy has the same hash)
  - `blueprint/products/series.yaml` = `651a34188506718db15db050784ac048aa7fa5de42f7d54eb22f24c3f409942b`
  - `blueprint/blueprint.yaml` = `5bab1bb2…6c7`, `blueprint/db_schema.json` = `3c377c1c…575`, `blueprint/share_tools.py` = `adbaf25b…549`
- Fields read: the blueprint (blueprint.yaml difficulty entry, products/*.yaml, db_schema.json, share_tools.py), the extended charter, task_tools.py, and per task only `frozen_time`, `user_scenario` and `initial_state` (orchestrator views `task{0,1}.visible.json`). To evaluate the charter's own `compute` expressions on the seeds, the auditor imported the evaluator primitives (`build_env` / `eval_compute` / `substitute`) from `skills/erl-task-instantiate/scripts/check_compute.py`. That file holds no task GT.
- Fields masked and left unread until every derivation was frozen: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, and `env/.../worklog.md`. Sibling difficulties' tasks and audits were not read.
- Gate snapshot: supplied by the orchestrator (all instantiation gates green, traceability deferred). The auditor cites it and did not re-run it. Entry conditions are complete.

### policy_conflict_scan

Base section: `sed '/^extended_policies:/,$d' series.extended.yaml` and `blueprint/products/series.yaml` differ by one trailing blank line only. Parsed as YAML, every top-level key (category … policies) is equal. **The base copy is verbatim.**

The extended charter has seven policies. They fall into two connected components of the `prerequisite` graph, which are the two problem trees the charter can produce:

| Component | Policies | Subject / computes | Scope partition |
| --- | --- | --- | --- |
| Insured | `series_ext_insured_portal_booking` (IB, root, owner=user tool), `series_ext_late_cancellation_fee` (LC), `series_ext_no_show_fee` (NS) | IB: series_visits_booked / visits; LC, NS: series_fee_assessed / amount | IB = portal booking on an insurance-funded series |
| Package | `series_ext_package_portal_booking` (PB, root, owner=user tool), `series_ext_first_visit_no_show_fee` (FV), `series_ext_late_arrival_fee` (LA), `series_ext_same_day_cancellation_fee` (SD) | PB: series_visits_booked / visits; FV, LA, SD: series_fee_assessed / amount | PB = portal booking on a package-funded series |

The five fee policies all claim `series_fee_assessed.amount`. Their stated scopes split the missed visits by kind:
- LC: a patient cancellation received **before the appointment day** with notice below the threshold.
- SD: a cancellation **on the appointment day, ahead of its start**.
- LA: an arrival beyond grace, recorded as a **zero-notice cancellation carrying minutes late**.
- NS: a no-show **other than the first appointment**.
- FV: a no-show **on the first appointment**.

These are disjoint on every record shape the charter defines, with the exceptions recorded below as O-1 and O-2. IB and PB are disjoint by `funding_source`.

The scan found these overlaps:
- **O-1 (latent, Telehealth only).** Base `series_evt_notice_and_rescheduling` says "a later arrival is recorded as late_arrival_beyond_grace_treated_as", and base event `series_no_show` means "…or arrives beyond the grace period where that is recorded as a no-show". The LA rule says instead "the arrival is recorded as a cancellation with zero hours of notice that carries the minutes late". For the only `no_show` format (Telehealth 30-Minute) the two disagree on which history entry a late arrival produces, so a Telehealth late arrival recorded as `series_no_show` with `minutes_late` would sit inside both NS's scope and LA's scope. Neither task has a Telehealth series, so the consequence cannot be demonstrated here (observation).
- **O-2 (latent).** LC and SD are each "worked out on the most recent cancellation recorded on the series, the one with the latest appointment date" (compute `LATEST('series_events', …, date_field='appointment_date', event_type='series_visit_cancelled')`). On a series that holds a before-day late cancellation and also a later same-day or zero-notice entry inside the fee window, LC's notice and reason would be read off an entry it does not charge. Neither task world has this shape (observation).
- **Eligibility inherited from base.** Base `series_evt_missed_visit_fees` withholds the fee where `missed_visit_fee_billable` is false, where a package with `missed_visit_forfeits_visit` true forfeits a visit, where a membership forfeits a session, and for WC. It also inherits the per-month cap, `fee_on_first_appointment`, the clinic-cancellation and same-week-reschedule exemptions, and `fee_assessment_days`. None of these is overwritten. The merged reading is unique: an extended amount rule applies only where base still assesses a fee. The package charter agrees: "Where missed_visit_forfeits_visit is false the appointment's series fee rules apply instead." (`package_evt_missed_visit_forfeit`).
- **Cross-category reads.** All are read-only, and no extended policy writes another category:
  - plan: `copay_amount`, `prior_auth_required`, `auth_end_date`, `authorized_visits_remaining`, `benefits_verified_date`
  - package: `single_visit_cash_rate`, `status`, `visits_remaining`, `extended_visit_draw`, `package_events` forfeits
  - membership: `membership_events` forfeits
  - hardship: `status`, `effective_date`, `expiry_date`, `discount_percent`
- **Scope exclusivity / completeness.** With M=2 the two components above are the only possible pair of disjoint trees that covers all seven policies. Whether the two tasks claim exactly these is checked per task, and against `charter_scope` in the closing checklist.

### rule_compute_equivalence

Mechanical sweep:
- every `compute` binding has a `compute_basis` entry;
- every `compute_basis` quotation is verbatim in its policy's `rule` (whitespace-normalised);
- every `baseline.rule` and every `overwrite.replaced_by` is verbatim in the rule.

All three hold for all seven policies. Sentence-by-sentence results:

- **LC.** Each element below is implemented exactly as stated:
  - basis ladder: insured with copay > 0 → `MN(late_cancel_fee, copay)`; package with cash rate > 0 → `cash_rate × 50 %`; otherwise `late_cancel_fee`;
  - notice share ≥18 / ≥6 / <6 h;
  - reason share;
  - attendance ≥8 / ≥4;
  - membership forfeits in 3 whole months, via `XCOUNT(..., within_months=3)` on `event_date` ("an entry counts when fewer than three whole months separate its date from the assessment date");
  - hardship share (in force via `DAYS(eff, NOW) >= 0 and DAYS(NOW, exp) >= 0`);
  - single rounding at the end.

  The scope sentence ("cancelled before the appointment day with notice below late_cancel_notice_hours") is eligibility and has no compute counterpart.
- **NS.** As LC, plus:
  - repeat share = `COUNT(series_fee_assessed, within_months=2)`;
  - slot share by `HH:MM` string bounds 08:00, 10:00, 15:00, 17:00, matching the rule's half-open intervals.

  Observation: `ns_time … or '12:00'` is a default the rule does not state. It is reached only when the series has no no-show, where no NS fee is chargeable, so it has no consequence.
- **IB.** Implemented as stated:
  - window ladder 21 / 28 / horizon, capped at the series end (`MN(window, DAYS(NOW, end))`), whole weeks `// 7`;
  - weekly count by `DAYS(start, NOW)` against 35 / 21;
  - plan-limit method ladder (prior auth and auth end date not passed → `authorized_visits_remaining − booked`; no prior auth and verified < 12 whole months → `max_visits_per_booking_batch`; else 4);
  - attendance limit 12 / 8 / 4;
  - `MX(0, MN(...))`.
- **FV.** Implemented as stated:
  - basis ladder (package first, then insured);
  - lead-time by `DAYS(booking event_date, start)` ≤2 / ≤6;
  - package forfeits in 3 whole months;
  - hardship;
  - `MN(1, first_missed)` as the 0/1 existence factor, grounded in the rule's scope sentence.

  Observations:
  - The rule's "only where fee_on_first_appointment of the series' format is true" has no compute counterpart. It is eligibility, so this is not a quantity drift.
  - `fv_booked_on … or F('opened_date')` is an unstated fallback. It is unused when a booking row holds the start date.
- **LA.** Kind fee by `late_arrival_beyond_grace_treated_as`, basis ladder, lateness ladder, repeat, package forfeits, hardship, new-series share. **Defect F-1, see factor_ladders:** the lateness ladder's rule tiers overlap for some formats, and compute settles the overlap by evaluation order, a choice the rule does not make.
- **SD.** Implemented as stated: basis ladder, notice share <2 / <6 h, repeat, package forfeits, hardship, reason.
- **PB.** Implemented as stated:
  - window 28 / 35 / horizon by ≥3 / ≥1 fees;
  - weekly count by days since the series' surgery date (`'1900-01-01'` default = "or the series carries no surgery date", which the rule states);
  - cover-limit method ladder (draw arithmetic for Extended/Specialty);
  - clearance limit by `DAYS(clearance_date, NOW)` ≤30 / ≤90 (no clearance → standard, as the rule states).

Every ladder named in `factors[].ladder` appears as a sentence of the rule and as a branch of its `decides` binding, and every branch is a stated tier. The only exception is F-1's overlap, where the rule states two values and compute yields one.

### action_binding_and_uuids

| Policy | target_tool | computes | owner |
| --- | --- | --- | --- |
| LC | `assess_late_cancellation_fee_706e910e` | amount | agent |
| NS | `assess_no_show_fee_93f38688` | amount | agent |
| IB | `book_insured_portal_visits_a191f0e3` | visits | user |
| FV | `assess_first_visit_no_show_fee_a4cbc15c` | amount | agent |
| LA | `assess_late_arrival_fee_e6f6ddb6` | amount | agent |
| SD | `assess_same_day_cancellation_fee_8648d00e` | amount | agent |
| PB | `book_package_portal_visits_336412d0` | visits | user |

- Each `(target_tool, computes)` is claimed by exactly one policy.
- The uuid8s `706e910e, 93f38688, a191f0e3, a4cbc15c, e6f6ddb6, 8648d00e, 336412d0` are pairwise distinct, share no common prefix or tail, and show no sequential pattern.
- **Docstrings.** A scan for ordering words found only "on the day ahead of it or earlier" (LC: the cancellation's own timing), "reached … later than the grace period" (LA), and "…owed on the series once this fee is included" (all fee tools). None places a tool in a sequence, names another tool or another problem.
- **Function bodies.** All seven have zero `if` and zero `raise`. No tool validates eligibility or a prerequisite. Each fee tool creates one `series_fee_assessed` row (event_date = now, `source_event_id` = the argument) and adds the amount to `missed_fee_balance`. Each booking tool creates one `series_visits_booked` row (channel `patient_portal`) and adds to `booked_visits_remaining`.
- **Docstring vs policy.** Each docstring's scope sentence matches its policy's scope sentence. LA's `fee_kind` enum matches "the fee is charged under the kind named by late_arrival_beyond_grace_treated_as".
- Note for prerequisite_sentences: LC, SD and (for every format except Telehealth) LA all write `fee_kind = late_cancellation` entries. NS and FV both write `fee_kind = no_show` entries.

### prerequisite_graph

| Edge (blocked ← depended-on) | kind | gate (binding exists in blocked compute) | form | resolved_by = depended-on target_tool |
| --- | --- | --- | --- | --- |
| NS ← LC | value_input | `ns_prior_fees` ✓ | state | ✓ |
| IB ← LC | value_input | `bi_fees` ✓ | state | ✓ |
| IB ← NS | value_input | `bi_fees` ✓ | state | ✓ |
| LA ← FV | value_input | `la_prior_fees` ✓ | state | ✓ |
| SD ← FV | value_input | `sd_prior_fees` ✓ | state | ✓ |
| SD ← LA | value_input | `sd_prior_fees` ✓ | state | ✓ |
| PB ← FV | value_input | `bp_fees` ✓ | state | ✓ |
| PB ← LA | value_input | `bp_fees` ✓ | state | ✓ |
| PB ← SD | value_input | `bp_fees` ✓ | state | ✓ |

- `prerequisite` is filled in on every policy (`[]` on LC and FV).
- Every `problem` is an extended policy id of this file. None is base and none is self.
- Every `policy_source` is verbatim in its own policy's rule (mechanical check).
- All forms are `state` and none carries `fallback_reason`.
- Topological orders are LC → NS → IB and FV → LA → SD → PB. **The graph is acyclic.**
- The `effect` texts describe the depended-on write's real effect: one more `series_fee_assessed` row on the series, which moves the blocked policy's fee-count binding.
- No `prerequisite` text uses authoring-viewpoint wording.
- **Condition vs sentence breadth.** These are latent observations, not consequential on either task world; see prerequisite_sentences.

### prerequisite_sentences

Four-point test, applied edge by edge:

| Edge | Sentence (own rule) | Ordering connective | Record-visible state, no tool / id / snake_case | Strength vs `condition` |
| --- | --- | --- | --- | --- |
| NS ← LC | "The no-show fee is fixed only after every late cancellation recorded on the series within its fee assessment period carries its late-cancellation fee entry." | only after ✓ | "late cancellation … carries its late-cancellation fee entry" ✓ | equal (both cover every late cancellation, notice < threshold, not clinic) |
| IB ← LC | "The number of appointments an insured portal booking opens is fixed only after every late cancellation … shows a late-cancellation fee entry." | only after ✓ | ✓ | equal |
| IB ← NS | "An insured portal booking is not opened until every no-show recorded on the series within its fee assessment period shows a no-show fee entry." | not … until ✓ | ✓ | **sentence broader**: "every no-show" vs condition "other than one on the series' first appointment" (O-3) |
| LA ← FV | "The late-arrival fee is fixed only after a no-show recorded on the series' first appointment … carries its first-appointment no-show fee entry." | only after ✓ | ✓ | equal |
| SD ← FV | "A same-day cancellation fee is not charged until every no-show on the series' first appointment … shows a first-appointment no-show fee entry." | not … until ✓ | ✓ | equal |
| SD ← LA | "The same-day cancellation fee is fixed only after every late arrival beyond the grace period … carries its late-arrival fee entry." | only after ✓ | ✓ | equal |
| PB ← FV | "The number of appointments a package portal booking opens is fixed only after a no-show on the series' first appointment … carries its first-appointment no-show fee entry." | only after ✓ | ✓ | equal |
| PB ← LA | "A package portal booking is not opened until every late arrival beyond the grace period … shows a late-arrival fee entry." | not … until ✓ | ✓ | equal |
| PB ← SD | "The package portal booking count is fixed only after every same-day cancellation recorded on the series … carries its same-day cancellation fee entry." | only after ✓ | ✓ | condition ("received on its own appointment day with notice above zero hours") omits SD's "the patient cancelled" (a same-day clinic cancellation meets the condition but can never carry a fee), and excludes a same-day patient cancellation given under one whole hour ahead of start (O-4) |

**Hop resolution.** The reader goes from the sentence, through the records and the depended-on rule, to the action:
1. The waited-on entry is a specific history row: a late cancellation, a no-show, a first-appointment no-show, a late arrival or a same-day cancellation inside the fee window.
2. That row lies inside exactly one fee policy's scope sentence: before-day vs same-day vs zero-notice-with-minutes-late vs first-appointment vs other no-show.
3. That policy's write is the only write that leaves a fee entry pointing at the row through `source_event_id`.

So for every waited-on row on the two task worlds the hop has one reading.

- No rule carries a second wording of its dependency, a tool name, another problem's id or a route.
- No depended-on rule restates the blocked sentence.
- No rule states a cross-problem order that grounds no declared edge. A text scan of the seven rules for "only after / until / before / first" found only the declared sentences plus scope uses: "cancelled before the appointment day", "first appointment of the series".
- No base sentence grounds an edge.

Latent breadth observations. None is demonstrable on task 0 or task 1, and each is recorded so a later world does not inherit it silently:
- **O-3.** IB ← NS's sentence covers every no-show, including a first-appointment no-show (written by FV, not NS). On an insured series whose first appointment was a no-show inside the window, the sentence makes IB wait on an FV write that no declared edge names. Where `fee_on_first_appointment` is false (Telehealth), no fee can ever be written, and IB waits out the window. Task 0's first appointment (2026-01-19) was attended, so this does not occur.
- **O-5.** "late cancellation" in the NS ← LC and IB ← LC sentences (and conditions) includes, by the base definition ("A cancellation with notice below late_cancel_notice_hours is a late cancellation"), same-day cancellations and late-cancellation-kind late arrivals. Their fee entries are written by SD and LA, which are not declared as NS or IB prerequisites. Task 0 has only a before-day late cancellation, so this does not occur.
- **O-4.** PB ← SD condition vs SD scope: see the table above. Task 1's same-day entry is a patient cancellation with 1 h notice, so this does not occur.

### override_declarations

**`series_evt_missed_visit_fees`**, cited by LC, NS, FV, LA and SD:
- S1 "A late cancellation is charged late_cancel_fee and a no-show is charged no_show_fee of the series' format." Replaced, and declared in each of the five `overwrite` entries. Base's `formula.amount` is the same quantity, so it is covered by the declaration.
- S2 (funding-dependent consequence: plan `missed_visit_fee_billable` false → no fee; WC referral decides; package `missed_visit_forfeits_visit` true → forfeit instead of fee; membership forfeits instead of fee). **Followed.** No extended rule removes it. The package basis tiers apply only to packages whose `missed_visit_forfeits_visit` is false, which is consistent with `package_evt_missed_visit_forfeit`.
- S3 (no fee for a missed first appointment where `fee_on_first_appointment` is false; none beyond `missed_fees_per_month_cap` per series-month; none for a clinic cancellation; none for a same-week reschedule with enough notice). **Followed.** FV restates the first clause. The others are inherited.
- S4/S5 (`fee_assessment_days`, day-zero counting). **Followed** and inherited.

**`series_booking_eligibility`**, cited by IB and PB:
- Bookable status. Followed.
- Slot length. Followed.
- "Each booking holds at most max_visits_per_booking_batch … series_length_weeks_max weeks". Replaced, declared. The extended count still never exceeds `max_visits_per_booking_batch`, because the attendance and clearance limits top out at it and every format's batch is ≥ 8 = mid batch.
- Portal sentence. Followed. Observation O-6: base says Specialty One-on-One has `portal_booking_allowed: false`, yet PB's cover-limit tier 2 names "Extended 60-Minute Visit Series or Specialty One-on-One Visit Series". The Specialty half of that tier can never be reached by a portal booking. Extended keeps the tier real.
- Clearance / specialty / post-op / card. Followed (opening gates).
- Booking blocks (fees past due, plan balance hold, same-day restriction). Followed and inherited.
- Funding holding must allow the visits. Followed; PB's cover limit and IB's plan limit implement it.
- Funding change. Not applicable.

**`series_agg_weekly_frequency`**, cited by IB and PB: followed. IB's weekly count never exceeds the standing count. PB's tier 2 (`visits_per_week_max`) stays within the format band that base requires. Packages carry no combined cap.

**No undeclared override was found.** No anonymous intermediate factor, 0/1 multiplier or dropped branch overrides base. FV's `MN(1, first_missed)` is its own scope, not a base override.

### factor_ladders

Each policy has four to six factors with honest labels; method factors switch the formula, parameter factors switch a number:

| Policy | Factors (label) | #param / #method | Multi-source factor | cross_difficulty (as declared) |
| --- | --- | --- | --- | --- |
| LC | basis (m), notice (p), reason (p), attendance (p), membership-miss (p), hardship (p) | 5 / 1 | basis (series funding × plan copay / package tier rate) | plan, membership, hardship |
| NS | basis (m), repeat (p), slot (p), attendance (p), membership-miss (p), hardship (p) | 5 / 1 | basis | plan, membership, hardship |
| IB | window (p), weekly count (p), plan limit (m), attendance limit (p) | 3 / 1 | plan limit (plan variant prior-auth × plan auth end / verification date) | plan |
| FV | basis (m), lead time (p), package forfeit (p), hardship (p) | 3 / 1 | basis | package, hardship |
| LA | basis (m), lateness (p), repeat (p), package forfeit (p), hardship (p), new series (p) | 5 / 1 | basis | package, hardship |
| SD | basis (m), notice (p), repeat (p), package forfeit (p), hardship (p), reason (p) | 5 / 1 | basis | package, hardship |
| PB | window (p), weekly count (p), cover limit (m), clearance limit (p) | 3 / 1 | cover limit (package status × series format) | package |

- Every factor has three tiers in its ladder, the fall-through included, and every tier is stated in the rule with its condition and value or method.
- `decides` is always an input binding, never `result`, and binding sets are disjoint within each policy.
- Each fall-through equals that factor's `baseline`, and each `baseline` equals what `baseline.rule` states for that input:
  - fee policies: format schedule fee, every share 100 %;
  - booking policies: horizon window, standing weekly count, every limit = standard batch 4.
- Every `method` tier names a computation stated in the rule.
- Each `baseline.rule` is self-sufficient: fee = format fee; booking = whole weeks × standing per week − booked, capped at 4, floored at 0.

**F-1 (SOURCE-FACTOR, also a latent SOURCE-POLICY contradiction) — LA lateness ladder.** Rule text: "…la_near_grace_pct percent where the patient arrived no more than la_near_grace_minutes minutes beyond the grace period, la_under_half_slot_pct percent where the patient arrived later than that but still less than half of visit_length_minutes after the start, and 100 percent where the patient arrived half of visit_length_minutes or more after the start." With `la_near_grace_minutes = 10`:
- **Post-Operative and Standard** (grace 15, length 45): tier 1 = ≤ 25 min, tier 2 = > 25 and < 22.5 min (**empty**), tier 3 = ≥ 22.5 min. **Tiers 1 and 3 overlap on (22.5, 25].**
- **Telehealth** (grace 10, length 30): tier 1 ≤ 20, tier 2 empty, tier 3 ≥ 15, overlapping on [15, 20].
- Only Extended, Specialty (25 < 30) and Aquatic (20 < 22.5) give three disjoint, non-empty tiers.

On the overlap the rule states two values for the same arrival: a 24-minute Post-Op late arrival gets 50 % by tier 1 and 100 % by tier 3. Compute (`K('la_near_grace_pct') if la_minutes <= grace + 10 else (… if la_minutes*2 < length else 100)`) silently returns 50. That is the policy-level contradiction. Bears on task 1 (Post-Operative format).

**F-2 (SOURCE-FACTOR) — PB weekly-count ladder.** Tiers: `visits_per_week_min` (surgery date < 14 days before), `visits_per_week_max` (14–42 days), the series' `visits_per_week` (> 42 days or no surgery date).
- The only series that carries a surgery date is a Post-Operative one: base event field "surgery_date: surgery date for a post-operative series; empty otherwise".
- For that format min = 2 and max = 3, and base `series_agg_weekly_frequency` keeps every series' `visits_per_week` "between visits_per_week_min and visits_per_week_max of its format", so `visits_per_week` ∈ {2, 3}.
- Hence, for every series the ladder actually divides, the fall-through value always equals tier 1's value (series at 2/week) or tier 2's value (series at 3/week). For every customer the ladder can place on tier 1 or 2, it has only two distinct outcomes.
- Bears on task 1.

**Observations** (no consequence demonstrable on either task world):
- IB attendance limit: tiers 1 and 2 both give 8 on Aquatic and Specialty (`max_visits_per_booking_batch` 8 = `bi_mid_batch`). PB clearance limit: same on Aquatic and Specialty. Task 0 is Standard (12/8/4) and task 1 is Post-Op (18/8/4), so neither is affected.
- IB weekly count: tiers 1 and 2 coincide whenever the standing count ≤ min + 1. Task 0 stands at 3 with min 1 (1/2/3), so it is not affected.
- Hardship tier 2 ("100 less discount_percent") equals the fall-through 100 for the 0 % "Catastrophic Medical Hardship" variant. Neither task holds it.
- Package basis tier condition "whose tier lists a single_visit_cash_rate above zero": all six package tiers list 125.00, so this half of the conjunction never divides package-funded customers. The funding-source half carries the tier.
- LC notice share's fall-through "< 6 h": a cancellation received before the appointment day can give under 6 h only for a start before 06:00.
- Declared `cross_difficulty: membership` / `hardship`: blueprint `difficulties` claim only plan, series, package, payplan and wc, so no difficulty of this scenario owns membership or hardship. Each task still has a plan- or package-reading factor, so the "≥ 1 cross-difficulty factor" floor is met through those.
- Realism of conditions and outcomes: every remaining condition is one a PT clinic network plausibly weighs when setting a missed-visit fee or a self-service booking batch:
  - funding, notice, reason, attendance tenure, peak slot, financial hardship, booking lead time, new-series status, package forfeits, recent fees, series age, authorization, package cover, clearance age;
  - the wellness-membership forfeits share (a patient's attendance reliability across the network's programs) is the most remote of these, and is recorded only as an observation.

### findings

| id | Class | Summary | Bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-FACTOR (+ latent SOURCE-POLICY) | LA lateness ladder has an empty middle tier and overlapping outer tiers on Standard, Post-Operative and Telehealth parameters; the rule gives 50 % and 100 % to the same arrival on the overlap | task 1 (Post-Op): demonstrated there |
| F-2 | SOURCE-FACTOR | PB weekly-count ladder: on every series it divides (post-op only), the fall-through always duplicates tier 1 or tier 2 | task 1: demonstrated there |
| O-1 | observation | Telehealth late arrival recorded as no-show (base) vs zero-notice cancellation (LA) | none (no Telehealth series) |
| O-2 | observation | LC/SD "most recent cancellation" anchor can read a non-charged entry | none |
| O-3 | observation | IB ← NS sentence broader than its condition (first-appointment no-show) | task 0: not triggered |
| O-4 | observation | PB ← SD condition vs SD scope (clinic same-day cancel; sub-hour notice) | task 1: not triggered |
| O-5 | observation | "late cancellation" in NS/IB sentences also covers SD/LA-written entries, which are undeclared resolvers | task 0: not triggered |
| O-6 | observation | PB cover-limit tier names Specialty, a format base forbids from portal booking | none |

## closing_checklist

Written after both tasks' blind derivations were frozen and their GT revealed, on 2026-10-05. **The difficulty is NOT closed**: not every task passes all four relationships.

| Item | Status |
| --- | --- |
| Audit files one-to-one with tasks (`0.md`, `1.md`) plus `_difficulty.md`; first revision, no older revision | ✓ |
| Every comparison section carries PASS | ✗: task 0 SOURCE-POLICY RED (T0-1); task 1 SOURCE-FACTOR RED (T1-1, T1-2) |
| Extended policies fully covered; scopes pairwise disjoint | ✓. `charter_scope`: task 0 = {LC, NS, IB}, task 1 = {FV, LA, SD, PB}. These match the two prerequisite-graph components derived here; the union is all 7, and the task tools match one-to-one |
| uuid8 per tool independent and frozen | ✓ (§action_binding_and_uuids) |
| Each tree has 1–3 prerequisite problems, ≥ max(n−1, 1) value_input edges, an owner=user problem, no cycle; whole-difficulty graph acyclic | ✓. Task 0: n=2, 3 value_input. Task 1: n=3, 6 value_input. Both roots are owner=user |
| Each computation has a self-sufficient baseline, 4–6 surviving factors (≥2 p, ≥1 m), real ladders, weight against an honest baseline | ✗ for task 1. PB keeps 3 surviving factors (F-2 / T1-1). The LA lateness ladder is unreal on the Post-Op format (F-1 / T1-2). All other factors bear weight, and every baseline gives a definite number ≠ gold |
| Per task ≥1 multi-source and ≥1 cross-difficulty factor, with rows seeded | ✓. Task 0: plan basis / plan limit. Task 1: package basis / forfeits / cover limit |
| Instantiation gates re-run on final form | Not applicable while RED. The orchestrator's snapshot (all green, traceability deferred) is the one on record; the auditor did not run gates |

Charter-global latent observations O-1 to O-6 stand as recorded above. None is demonstrable on either task world.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit (independent), unattended re-audit, round 2.
- Freeze time: started 2026-10-05T06:20:03Z. This section was written before either task's round-2 GT was revealed. It is built only from the charter, the blueprint and the tool module.
- **Shared inputs changed, so every charter-global section is re-derived in full.** Nothing is carried forward by reference.

| File | Round 1 | Round 2 |
| --- | --- | --- |
| `series.extended.yaml` | `b0b7fffd…` | `870dbcb422496508634885d9cb4c95d4112edf7cf242da09da2308fd8a79d6d8` |
| `task_tools.py` | `78e73f66…` | `23c68c42e57dac8f22e687c7c02bca872e789ee4f8d3a98c7f91db69eb2020ef` |

  The orchestrator views in `/tmp/erl0032_views/appointment_booking_and_missed_visits_r2/` carry the same two hashes as the repository files.
- Unchanged blueprint inputs (same hashes as round 1): `products/series.yaml` `651a3418…`, `blueprint.yaml` `5bab1bb2…`, `db_schema.json` `3c377c1c…`, `share_tools.py` `adbaf25b…`.
- Fields read: as in round 1. Masked until both round-2 derivations are frozen: the same GT fields. `tasks/{0,1}.json` (r2 sha256 `568bdcb7…`, `dd97812b…`) were not opened. No search touched `tasks/`.

### policy_conflict_scan (r2)

- **Base copy.** Still verbatim: everything before `extended_policies:` differs from `products/series.yaml` only by one trailing blank line. Round-2 diffs start at line 729, inside `extended_policies`.
- **Components.** The prerequisite graph has the same two components as round 1: {IB ← LC, NS; NS ← LC} and {PB ← FV, LA, SD; LA ← FV; SD ← FV, LA}. Same seven policies, same tools.
- **Scope partition of `series_fee_assessed.amount`.** Sharpened:
  - LC: patient cancellation received **before** the appointment day.
  - SD: "the patient, **not the clinic**", on the day, ahead of start.
  - LA: now explicitly "on a format whose late_arrival_beyond_grace_treated_as is late_cancellation".
  - NS: not the first appointment. FV: first appointment.
- **O-1 (Telehealth late-arrival recording): CLOSED.** The LA rule now reads "On a format whose late_arrival_beyond_grace_treated_as is no_show, a late arrival is recorded as a no-show carrying the minutes late and is charged as a no-show, outside this fee." This agrees with base `series_evt_notice_and_rescheduling` and the base `series_no_show` event meaning. Such a late arrival is "neither attended nor cancelled", so it lies in NS's scope, or FV's on a first appointment. The LA tool lost its `fee_kind` argument and always writes `late_cancellation`, which is consistent with the narrowed scope.
- **O-2 (LC/SD "most recent cancellation" anchor): PARTIALLY CLOSED, residual latent.**
  - LC and SD are now "worked out on the most recent cancellation recorded on the series that carries no minutes late". Compute adds `minutes_late=None` to both `LATEST` calls.
  - This removes the late-arrival entry from both anchors.
  - The residual: a before-day cancellation and a later same-day cancellation, both inside the window. LC still reads the later same-day entry, and SD reading the latest could meet a later before-day entry.
  - Not reached on either task world (checked per task). Observation.
- **Inherited base eligibility.** Unchanged and consistent, as in round 1.

### rule_compute_equivalence (r2)

Mechanical sweep: every compute binding has a basis, and every basis quotation, `baseline.rule` and `overwrite.replaced_by` is verbatim in its rule. All seven policies pass.

Sentence-level changes since round 1, each verified in both directions:
- **LC.**
  - `lc_mid_notice_hours` 6 → 12. Rule and compute both state ≥18 / ≥12 / <12.
  - Anchor: "carries no minutes late" ↔ `minutes_late=None`. With `_rows`'s `str()` match, `'None' == 'None'` for null or absent values.
  - Hardship tier 2: "discounts more than zero but less than …" ↔ `… and lc_hs_level > 0`.
- **NS / IB.** Prerequisite sentences are re-worded (see prerequisite_sentences). Hardship as LC. Compute is otherwise unchanged. IB `bi_mid_batch` 8 → 6, the same in rule (by parameter name) and compute.
- **FV.** Hardship `> 0` only.
- **LA.**
  - Scope narrowed to `late_cancellation` formats.
  - Lateness ladder now ≤ grace + 10 → 50 %; > grace + 10 and ≤ grace + 20 → 75 %; > grace + 20 → 100 %. Compute matches: `la_minutes <= grace + K('la_near_grace_minutes')`, else `<= grace + K('la_far_grace_minutes')`, else 100.
  - Observation O-8: `baseline.rule` and `la_schedule_fee` keep a "no_show_fee where it is no_show" branch that the narrowed scope can never reach. It is a dead clause with no consequence, since the computation for every in-scope format is `late_cancel_fee`.
- **SD.** "the patient, not the clinic" (scope, no compute counterpart needed). Anchor `minutes_late=None`. Hardship `> 0`.
- **PB.**
  - The weekly-count factor is **removed**. Window appointments are now "the window's whole weeks multiplied by the series' standing appointments per week", ↔ `bp_weeks * F('visits_per_week')`.
  - Cover limit no longer names Specialty One-on-One (rule ↔ compute).
  - `bp_mid_batch` 8 → 6.
  - **New payment limit**: max batch where `amount_paid_total ≥ purchase_price`; `bp_part_paid_batch` 6 where 0 < paid < price; `bp_standard_batch` 4 where nothing is paid. Rule ↔ compute: `bp_price > 0 and bp_paid >= bp_price` / `bp_paid > 0 and bp_paid < bp_price` / else.
  - The result is the minimum of four quantities, in rule and compute alike.

**F-1 rule overlap: CLOSED.** The new LA lateness tiers are disjoint and non-empty for every in-scope format, because they are offsets from grace and no longer compared with the slot length.

### action_binding_and_uuids (r2)

- Same seven `(target_tool, computes)` pairs, each claimed once, and the same seven uuid8s (unchanged and distinct).
- `assess_late_arrival_fee_e6f6ddb6` signature is now `(series_id, source_event_id, amount)`. Its docstring says "books one late-cancellation-kind fee" and the body writes `fee_kind="late_cancellation"`.
- Docstring ordering-word scan: same benign hits as round 1. No tool names another tool or a sequence.
- Bodies: no `if` statement and no `raise`. The only conditionals are `rows[0] if rows else {}` lookups, so no prerequisite or eligibility check exists in the tool layer.

### prerequisite_graph (r2)

- Same nine edges, all value_input / state with no fallback.
- Gates `ns_prior_fees`, `bi_fees` ×2, `la_prior_fees`, `sd_prior_fees` ×2, `bp_fees` ×3 all exist in the blocked policy's compute.
- `resolved_by` = the depended-on policy's `target_tool` on every edge.
- Every `policy_source` is verbatim in its own rule.
- Acyclic. Orders: LC → NS → IB and FV → LA → SD → PB.

### prerequisite_sentences (r2)

| Edge | Round-2 sentence change | Breadth vs condition | Status of round-1 item |
| --- | --- | --- | --- |
| NS ← LC, IB ← LC | "every late cancellation **received before its appointment day** and recorded on the series within its fee assessment period carries/shows its late-cancellation fee entry" | equal: conditions add "event_date earlier than appointment_date" | **O-5 CLOSED.** Same-day and late-arrival entries (received on the day) fall outside the sentence. LC's scope ("cancelled before the appointment day") makes `assess_late_cancellation_fee_706e910e` the only write that brings the state about |
| IB ← NS | "every no-show … **other than one on the series' first appointment**, shows a no-show fee entry" | equal | **O-3 CLOSED** |
| PB ← SD | sentence unchanged; condition now "that the patient, not the clinic, made on its own appointment day ahead of the start and that carries no minutes late" | equal to SD's scope | **O-4 CLOSED** |
| LA ← FV, SD ← FV, SD ← LA, PB ← FV, PB ← LA | unchanged | see O-7 | — |

The four-point test holds on every edge: ordering connective, record-visible state, no tool / id / snake_case token, strength equal to the condition except O-7. The hop resolves uniquely for every entry kind on both task worlds.

**O-7 (new latent observation, a by-product of the O-1 closure).** "every late arrival beyond the grace period recorded on the series" in SD ← LA and PB ← LA covers, in plain words, a late arrival on a `no_show` format too. Since round 2, LA records such an arrival as a no-show charged by NS or FV, so it can never carry a *late-arrival* fee entry. Each edge's `condition` ("zero-notice series_visit_cancelled entry carrying minutes late") is narrower than its sentence. The gap would only matter on a package-funded Telehealth series that has a late arrival inside the window. Task 1 is Post-Operative, so it does not arise there.

### override_declarations (r2)

- Same declared overrides as round 1: S1 of `series_evt_missed_visit_fees` in the five fee policies, and the batch/horizon sentence of `series_booking_eligibility` in IB and PB.
- Every other base sentence is followed or inherited, as in round 1. The base "funding holding must allow the visits … a Self-Pay Visit Package that is active …" sentence is still not overwritten and still governs PB. This matters for F-3 below.
- **O-6 CLOSED.** The cover limit no longer names Specialty.
- No undeclared override was found.

### factor_ladders (r2)

| Policy | Factors (label) | p / m | Multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| LC | as round 1 (6) | 5 / 1 | basis | plan, membership, hardship |
| NS | as round 1 (6) | 5 / 1 | basis | plan, membership, hardship |
| IB | window, weekly, plan limit (m), attendance | 3 / 1 | plan limit | plan |
| FV | basis (m), lead, package forfeit, hardship | 3 / 1 | basis | package, hardship |
| LA | basis (m), lateness, repeat, forfeit, hardship, new series | 5 / 1 | basis | package, hardship |
| SD | as round 1 (6) | 5 / 1 | basis | package, hardship |
| PB | window (p), cover limit (m), clearance limit (p), **payment limit (p, new)** | 3 / 1 | cover limit | package |

**Round-1 items:**
- **F-1 CLOSED.** The LA lateness ladder has three disjoint, non-empty tiers for every in-scope format: 50 / 75 / 100 at ≤ 10, 10–20 and > 20 minutes beyond grace.
- **F-2 CLOSED** by removal. The PB weekly-count factor no longer exists, and window appointments use the standing count.
- **Ladder observations:**
  - IB attendance and PB clearance tiers 1 and 2 coincided on Aquatic / Specialty. Now resolved: mid batch 6 < every format's `max_visits_per_booking_batch` (≥ 8).
  - The hardship tier 2 = fall-through for 0 % levels is resolved by "more than zero".
  - The LC notice fall-through is now reachable for appointments before noon.
  - Kept, with no consequence on either task: IB weekly tiers coincide when the standing count ≤ min + 1; the package basis sub-condition "rate above zero" never divides package customers; membership and hardship are labelled cross-difficulty although no difficulty claims them.

**F-3 (NEW, SOURCE-FACTOR) — PB payment limit and PB cover limit: each fall-through applies to no customer who can lawfully reach the PB write.**
- Base `series_booking_eligibility` (inherited, not overwritten) says "The funding holding must allow the visits: … a Self-Pay Visit Package that is active with visits remaining at least the visits booked…".
- The package charter (`package_purchase_eligibility`) says "The package is activated by its first payment", and the lifecycle transition reads "pending_payment → active: The package is activated when its first (or only) payment is received."
- Hence, for every customer who may lawfully reach a PB write, the funding package is active and its `amount_paid_total` > 0.
  - **Payment limit**: the fall-through "bp_standard_batch appointments where nothing has been paid on it" never applies. The ladder divides lawful customers into two outcomes only: paid in full → `max_visits_per_booking_batch`; part-paid → 6.
  - **Cover limit**: the fall-through "bp_standard_batch appointments in every other case", i.e. a non-active funding package, likewise never applies. The ladder has two lawful outcomes: non-Extended / Extended draw arithmetic.
- In each case the fall-through's outcome ("4 appointments" for an unpaid or non-active package) is not what this very charter gives such customers, which is no booking at all.
- Struck under "a tier's value or method, the fall-through's above all, is a treatment that business would not publish for customers in that situation" and "a ladder of fewer than three tiers".
- **PB then keeps two surviving factors (window, clearance limit), below the floor of 4.**
- Relation to previous revision: the payment limit is new in round 2. The cover-limit fall-through is unchanged in substance since round 1; **the round-1 audit missed it**, and it is recorded now.
- Bears on task 1.

Other new or changed ladders are real:
- PB clearance `max_visits_per_booking_batch` (8–18 by format) vs 6 vs 4, distinct for every format. Its fall-through ("older or no clearance date") is reachable on formats without a clearance requirement.
- IB attendance 12 (or 8 / 18) vs 6 vs 4.
- LC notice 50 / 75 / 100.

### findings (r2, charter-global)

| id | Class | Status | Bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-FACTOR / latent SOURCE-POLICY | CLOSED | — |
| F-2 | SOURCE-FACTOR | CLOSED (factor removed) | — |
| F-3 | SOURCE-FACTOR | **NEW**: PB payment-limit and cover-limit fall-throughs are unreachable for lawful PB writes; PB drops to 2 surviving factors | task 1 |
| O-1, O-3, O-4, O-5, O-6 | observation | CLOSED | — |
| O-2 | observation | residual latent (before-day vs later same-day anchor) | not triggered (see task files) |
| O-7 | observation | NEW latent: SD ← LA / PB ← LA sentence ("every late arrival") broader than condition after the O-1 closure | not triggered |
| O-8 | observation | NEW: dead `no_show` branch in LA `baseline.rule` / `la_schedule_fee` | none |

## closing_checklist (revision 2)

Written after the round-2 blind derivations were frozen and the round-2 GT revealed. **The difficulty is NOT closed.**

| Item | Status |
| --- | --- |
| Audit files one-to-one with tasks; round 1 preserved, round 2 appended under `## revision_2` | ✓ |
| Every comparison section PASS | ✗. Task 0: **PASS**. Task 1: **SOURCE-FACTOR RED (T1-3 / F-3)** |
| Round-1 REDs closed | T0-1 ✓; T1-1 / F-2 ✓; T1-2 / F-1 ✓ |
| Round-1 observations | O-1, O-3, O-4, O-5, O-6, T0-O2 closed. O-2 partially closed (residual latent). T0-O1 and T1-O1 kept |
| New defects | F-3 (SOURCE-FACTOR, task 1): partly introduced by the rework (payment limit), partly a round-1 audit miss (cover limit). New observations O-7, O-8, T0-O4 |
| Scopes disjoint and complete; tools / uuid8s | ✓. `charter_scope`: task 0 {LC, NS, IB}, task 1 {FV, LA, SD, PB} |
| Trees: 1–3 prerequisites, value_input floor, owner=user write, acyclic | ✓ for both tasks |
| Factors: 4–6 surviving, ≥ 2 p / ≥ 1 m, real ladders, weight, baseline ≠ gold | ✓ LC, NS, IB, FV, LA, SD. ✗ **PB (2 surviving, no method)** |
| Gates on final form | The orchestrator's post-rework snapshot is green (traceability deferred). The auditor did not run gates |

## revision_3

### charter_global_frozen (revision 3)

- Auditor: erl-task-policy-audit (independent), unattended re-audit, round 3.
- This section was written before either task's round-3 GT was revealed. It is built only from the charter, the blueprint and the tool module.
- Inputs:

| File | r2 | r3 |
| --- | --- | --- |
| `series.extended.yaml` | `870dbcb4…` | **`d25a64c604233879918fac66a7ec28a3d9776d2e4672aa9c6be848913ff4e8f7`** (changed) |
| `task_tools.py` | `23c68c42…` | `23c68c42…` (**unchanged**) |

  The orchestrator views in `/tmp/erl0032_views/appointment_booking_and_missed_visits_r3/` carry the same hashes.
- Blueprint `series.yaml` `651a3418…`, `blueprint.yaml` `5bab1bb2…`, `db_schema.json` `3c377c1c…` and `share_tools.py` `adbaf25b…` are unchanged. `products/package.yaml` is now `51f272ed…`; rounds 1–2 did not record its hash, so whether it changed cannot be shown. Every package fact relied on below was re-read from it in this round.
- **Re-derivation scope.** The charter file changed, so the charter-global sections are re-derived. The file was also re-serialised, with list and flow-map formatting changed throughout. A whitespace-normalised, parsed comparison against r2 shows:
  - the base section is semantically identical to r2 and to `blueprint/products/series.yaml`;
  - LC, NS, IB and FV are **semantically identical to r2** in every field;
  - changes are confined to LA (rule, baseline, compute, compute_basis, `late_arrival_basis` ladder wording), SD (one rule sentence and its prerequisite `policy_source`), and PB (rule, params, compute, basis, factors, prerequisite[1] `policy_source`, cross_category, inputs, overwrite `replaced_by`).

  The r2 conclusions for LC, NS, IB and FV are therefore carried forward, with the unchanged parsed content as grounds. LA, SD and PB are re-derived below. The tool-module conclusions are carried forward on the unchanged hash.
- Masked: the same GT fields. `tasks/0.json` `0597ce34…` and `tasks/1.json` `b51715d9…` were not opened. No search touched `tasks/`.

### mechanical sweep (r3, all seven policies)

Every compute binding has a `compute_basis` entry. Every basis quotation, `baseline.rule` and `overwrite.replaced_by` is verbatim in its rule. Every `policy_source` is verbatim in its own rule, with its gate present in the blocked compute and `resolved_by` equal to the depended-on `target_tool`. Every factor's `decides` and bindings exist in compute, and every ladder has ≥ 3 tiers. Factor counts and labels:

| Policy | Factors | p / m |
| --- | --- | --- |
| LC | 6 | 5 / 1 |
| NS | 6 | 5 / 1 |
| IB | 4 | 3 / 1 |
| FV | 4 | 3 / 1 |
| LA | 6 | 5 / 1 |
| SD | 6 | 5 / 1 |
| PB | 4 (window p, cover m, clearance p, **expiry p**) | 3 / 1 |

The graph has the same nine value_input / state edges and stays acyclic. The orders are LC → NS → IB and FV → LA → SD → PB.

### LA (r3)

- The rule's baseline sentence is now "Before any adjustment, the late-arrival fee is late_cancel_fee of the series' format, rounded to the nearest cent." `baseline.params` is `[late_cancel_fee]`, `la_schedule_fee` is `P('late_cancel_fee')`, and the basis ladder reads "the lesser of late_cancel_fee and that copay" / "late_cancel_fee".
- The `late_arrival_basis` baseline `la_base: la_schedule_fee` therefore equals `late_cancel_fee`, which is honest.
- **O-8 CLOSED.**
- The scope sentence ("on a format whose late_arrival_beyond_grace_treated_as is late_cancellation", with no_show formats charged as a no-show "outside this fee") and the lateness ladder are unchanged from r2. F-1 stays closed.

### SD and PB prerequisite sentences (r3)

- SD ← LA: "The same-day cancellation fee is fixed only after every late arrival beyond the grace period recorded on the series **as a zero-notice cancellation** within its fee assessment period carries its late-arrival fee entry."
- PB ← LA: "A package portal booking is not opened until every late arrival beyond the grace period recorded on the series **as a zero-notice cancellation** within its fee assessment period shows a late-arrival fee entry."
- Each sentence now has the same breadth as its `condition` ("zero-notice series_visit_cancelled entry carrying minutes late"). A no_show-format late arrival (recorded as a no-show) is outside both.
- The four-point test passes: ordering connective, record-visible state, no tool or id, strength equal to the condition.
- The only write that brings the state about is `assess_late_arrival_fee_e6f6ddb6`.
- **O-7 CLOSED.**
- The other seven edges' sentences are unchanged. **The task-0 edges (NS ← LC, IB ← LC, IB ← NS) are byte-equivalent in content to r2**, so the coordinator's concern about a task-0 regression from the O-7 change does not arise at charter level.

### PB rule ↔ compute (r3)

PB's rule and compute were rewritten. Each element below matches in both directions:
- **Window and window appointments**: unchanged from r2.
- **Covered appointments**: "Each appointment draws extended_visit_draw visits … on an Extended 60-Minute Visit Series and one visit on any other format, and the package's covered appointments are its visits remaining less the visits drawn by the appointments still booked …, divided by the visits one appointment draws and rounded down." ↔ `bp_draw_per_appt`, `bp_covered = (left − draw × booked) // draw`.
- **Installment schedule**: "The first installment … due on its purchase date and each later installment installment_interval_days calendar days after the previous due date, and an installment counts as overdue once more than installment_late_days calendar days have passed since its due date while it is unpaid." ↔ the following bindings:
  - `bp_opened` (package `opened_date`, "purchase date" per the package event field);
  - `bp_interval`, `bp_late` (tier params);
  - `bp_inst_overdue = MN(total, (days − late − 1) // interval + 1) if days > late else 0`. This counts installments k ≥ 0 with k·interval < days − late, which is exactly "more than installment_late_days days past its due date".
- **Cover-limit method ladder**:
  - paid ≥ price → covered;
  - installments, not fully paid, every overdue installment paid → `MN(covered, visits_included // installments)`;
  - otherwise (an overdue installment is unpaid) → 4.

  Compute matches: `bp_paid >= bp_price` / `bp_paid < bp_price and bp_inst_paid >= bp_inst_overdue` / else.
- **Expiry-limit ladder**: runway > 90 → `max_visits_per_booking_batch`; > 30 and ≤ 90 → 6; ≤ 30 → 4. Matches `DAYS(NOW, expiry)` against 90 and 30.
- **Result**: min of window, cover, clearance and expiry, floored at 0.

Observation **O-9**: the rule says "visits_included divided by installment_count" (the tier parameter), but `bp_inst_credit` divides by the package row's `installments_total`. These coincide wherever the tier is evaluated: an unpaid balance exists only when the patient chose installments, and then the price "is split into installment_count equal installments" (`package_evt_payments_and_crediting`). So no consequence follows.

### PB factor ladders (r3) — F-3 status

- **Cover limit (method).** Tiers:
  1. paid in full;
  2. installments current;
  3. an overdue installment unpaid.

  Each is reachable for a customer who can lawfully reach the PB write, which needs an active package per base `series_booking_eligibility`:
  - tier 1: any single-payment package, all of which are paid at activation;
  - tier 2: an installment package (Complete 12, Post-Surgical 18, Comprehensive 24) between due dates;
  - tier 3: an active installment package whose installment is unpaid more than `installment_late_days` (10) days after its due date. The package charter says only that such an installment "stops further crediting until it is paid"; it does not deactivate the package.

  The three methods are distinct: full covered count, covered count capped at the per-installment credit (6, 6 or 8), and a constant 4. The fall-through (4 appointments while an installment is overdue) is a plausible published treatment. The old non-active / unpaid fall-throughs are gone.
- **Expiry limit (parameter, new).** Tiers > 90 / 31–90 / ≤ 30 days of package validity remaining. All three are reachable on active packages, since validity runs 90–365 days by tier. Values `max_visits_per_booking_batch` (8–18) / 6 / 4 are distinct on every format. Limiting a self-booked batch on a package close to expiry is a plausible business rule.
- **Clearance limit and window**: unchanged and real.

**F-3 CLOSED** at charter level. PB has 4 factors, all with three reachable, distinct tiers: 3 p (window, clearance, expiry) and 1 m (cover). The multi-source factor is the cover limit (package row amounts × tier schedule params × `package_events` installment payments).

### carried-forward and residual items (r3)

| Item | Status |
| --- | --- |
| Action binding / uuid8s / tool bodies | Carried forward (tools unchanged, `23c68c42…`) |
| Override declarations | Unchanged: S1 of `series_evt_missed_visit_fees` (five fee policies) and the batch sentence of `series_booking_eligibility` (IB, PB, PB's `replaced_by` now naming the expiry limit). No undeclared override |
| O-2 | Residual latent risk, kept (LC/SD anchor with a before-day and a later same-day cancellation in one window). Checked per task |
| Ladder observations | Kept with no consequence: IB weekly tiers coincide at standing ≤ min + 1; package-basis "rate above zero"; membership / hardship labelled cross-difficulty |
| O-9 | New observation (see above) |

### findings (r3, charter-global)

| id | r2 | r3 |
| --- | --- | --- |
| F-3 | SOURCE-FACTOR RED (task 1) | **CLOSED** |
| O-7 | latent observation | **CLOSED** |
| O-8 | observation | **CLOSED** |
| O-2 | residual latent | residual latent (kept by reworker) |
| O-9 | — | new observation, no consequence |

## closing_checklist (revision 3)

Written after the round-3 blind derivations were frozen and the round-3 GT revealed.

| Item | Status |
| --- | --- |
| Audit files one-to-one with tasks; rounds 1–2 preserved, round 3 appended under `## revision_3` | ✓ |
| Every comparison section PASS | ✓. Task 0 PASS; task 1 PASS |
| Round-2 RED closed | ✓ T1-3 / F-3 |
| Round-2 observations | O-7, O-8 and T0-O4 closed. O-2 residual latent, kept by reworker and not reached on either world. T0-O1 and T1-O1 kept |
| New items this round | O-9 (charter, observation) and T1-O3 (task 1 proof prose, observation). No new RED |
| Extended policies fully covered; scopes pairwise disjoint | ✓. Task 0 {LC, NS, IB}, task 1 {FV, LA, SD, PB}; tools match one-to-one; uuid8s unchanged and independent |
| Trees: 1–3 prerequisite problems, ≥ max(n−1, 1) value_input edges, owner=user problem, acyclic | ✓. Task 0 n=2 / 3 value_input; task 1 n=3 / 6 value_input; both roots owner=user; whole graph acyclic |
| Factors: self-sufficient baseline, 4–6 surviving (≥2 p, ≥1 m), real three-tier ladders, weight against an honest baseline, baseline ≠ gold; per task ≥1 multi-source and ≥1 cross-difficulty with seeded rows | ✓ for all seven computations across both tasks |
| Instantiation gates on final form | The orchestrator's post-rework snapshot is green, with traceability deferred to post-render. The auditor did not run gates |

**The difficulty passes the source-layer policy-task audit at revision 3.** Recorded observations carry no demonstrated consequence: O-2 residual, O-9, T0-O1, T1-O1, T1-O3, and the IB weekly-tier / package-basis / membership-hardship labelling notes.
