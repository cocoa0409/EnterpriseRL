# Policy-task audit — personal_services_packages / task 1

## source_derivation_frozen

- Auditor: independent policy-task auditor (round 1). Freeze time: 2026-10-05T09:16Z (wall clock), before any task GT was revealed (task 0 frozen earlier; no reveal has taken place).
- Source: `env/env_0034_senior_living_operator/audits/_views/policy_task/personal_services_packages/task_1.view.json` sha256 6e7f706f92435e13fc67bc9c4fb6e6a9046f8189d018a2fecd2615d994867ebb (frozen_time, user_scenario, initial_state only); charter and tool hashes as in `_difficulty.md` § charter_global_frozen.
- Masked and unread: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure, worklog.
- contamination_disclosure: none.

World (frozen_time 2026-10-14 11:05 CDT, a Wednesday): customer Harold Brennan (4e38f1ce…), calling himself; IL residency 0122c22a… Independent Living Two-Bedroom, active, occupancy double, second_occupant_name Margaret Brennan; EFA 0315ed89… LifeCare Declining Balance Plan, occupied (contract_type lifecare); services plan af03ebad… Personal Services Premier Package, active, independent, effective 2021-01-01, suspension 2026-09-01..2026-09-30, hours_available 12.5, account_balance 829.00.

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences (Edge B), § override_declarations, § factor_ladders, § findings F-2.
- Declared overrides in this tree versus base: under base services_late_cancellation the no-show SO-2610-1064 would draw no_show_hours_charged = 1.0 h (Premier); the extended result differs, but the base sentence is named in the overwrite list. Package fit has `overwrite: []` and contradicts no base sentence.
- Handling time: missed-visit hours on the opening world; package fit on opening world + the hours entry.
- Real-world waits: none (seeded rows plus the hours write; the customer states the request).
- O-3 checked on this world: the only errand_shopping booking after the missed date is SO-2610-1098 (booked 2026-10-12 09:20), so LATEST and the existential rule agree.
- O-4 checked: the review-window fee shortfall is caused by the September 2026 suspension recorded on the plan, so compute's tier 2 and the rule's "because the plan was suspended" agree.
- F-2 bears on this task — demonstrated under task_independent_derivation.

### problem_chain

Root problem (the customer's only ask): move the plan "to a smaller package — whichever package actually fits what the two of you use", starting as soon as the rules allow, signed by him — services_ext_package_fit, write sign_services_package_change_2a41e92a (owner user).

Walk:
1. Root rule prerequisite sentence: "The package that fits the resident's use is not chosen until every service order recorded in the review months as a late cancellation or a no-show carries its hours entry for that cancellation on the plan's ledger."
2. Cancellation rows (services_orders):
   - SO-2605-1377 no_show 2026-05-20 — outside any 3-month window; has draw bf90aedb anyway.
   - SO-2608-1080 resident_cancelled 2026-08-20 07:30 for 2026-08-20 11:00 (same day -> late) — has draw 3ebf597f 0.5 h late_cancellation. Satisfied.
   - SO-2610-1064 errand_shopping, booked 0.75 h for 2026-10-09 10:00, no_show recorded 2026-10-09 10:00 — no hours row with order_reference SO-2610-1064 in services_ledger. NOT satisfied at the opening.
3. The policy that writes the hours entry: services_ext_missed_visit_hours ("Hours owed for a service order that was cancelled late or missed are posted by the desk once the cancellation or no-show is on record"), write post_services_order_hours_8d682fe6 (owner agent); its prerequisite list is empty.

Derived tree: services_ext_missed_visit_hours -> services_ext_package_fit, one edge, value_input (enters late_hours / late_entries). n = 1, value_input 1 >= 1, acyclic, user write present (the package change). Isomorphic to the declared `prerequisite`.

Load-bearing run: see the two readings below — the edge bears weight under reading A (Companion -> Comfort) and does NOT bear weight under reading B (Companion both ways).

No parallel edges; no wait; tool bodies judge nothing (`_difficulty.md` § action_binding_and_uuids).

Persona: raises only the root problem; prerequisite-adjacent lines are conditional ("If the agent says something on the account has to be posted or brought up to date before the package can be worked out, you tell them to go ahead"); "never mention any particular visit, missed appointment or cancellation". Closes on the signed change. PASS on the persona boundary.

Stray state_due obligations: no hourly charges exist on this plan, so services_ext_short_visit_credit owes nothing; after SO-2610-1064 every late/no-show order already carries its entry.

### task_independent_derivation

Identity: DOB 1941-06-22 + phone 4695550123 -> 2 matches. Harold signs himself.

Step 1 — missed-visit hours (handling time: opening world). Act now.
- miss_ref: most recent cancellation by cancelled_at = SO-2610-1064 (2026-10-09 10:00), no_show, errand_shopping, booked 0.75 h, service date 2026-10-09.
- band: no-show -> Premier no_show_hours_charged 1.0.
- basis: booked 0.75 < band 1.0 -> booked hours 0.75 (not laundry).
- pattern: late/no-show hours entries in the 6 months before the posting (2026-10-14): bf90aedb 2026-05-20 no_show, 3ebf597f 2026-08-21 late_cancellation -> 2 -> repeat_multiplier 1.25 (robust to any boundary convention: both well inside).
- rebooking: latest errand_shopping booking SO-2610-1098 booked 2026-10-12 09:20 -> 3 days after 2026-10-09 -> >2, <=7 -> 0.5. (SO-2610-1071 booked 2026-10-05, before the missed date, is not a rebooking.)
- entrance: EFA 0315ed89 occupied, LifeCare Declining Balance = lifecare -> 0.20.
- hours = RND(max(0, 0.75 x 1.25 x 0.5 - 0.20), 2) = RND(0.26875, 2) = 0.27.
- hours_available 12.5 >= 0.27 -> draw.
- Write: post_services_order_hours_8d682fe6(services_plan_id=af03ebad-416b-44a1-a280-d3bb9e71666f, order_reference=SO-2610-1064, draw_basis=no_show, event_type=services_hours_draw, billing_period=2026-10, hours=0.27, amount=0.00). Effect: hours_available 12.23.

Step 2 — package fit (handling time: opening world + the 0.27 h draw posted 2026-10-14).

Common inputs: change effective date — signed 2026-10-14, on or before cutoff day 20 -> 2026-11-01. Downgrade from Premier: commitment (3 months from 2021-01-01) long run. Independent residence: every package allowed. Fees in a 3-month rolling window: 2026-08-01, 2026-10-01 (2026-07-01 outside); no package_change fee -> divisor tier 2 (suspension in September) -> 2. Late entries in window: 3ebf597f 0.5 (2026-08-21) + new 0.27 (2026-10-14) -> 2 -> counted in full 0.77. Home: "Independent Living Two-Bedroom" (not Cottage Home, not Two-Bedroom Deluxe), double, second occupant named -> headroom 1.0. Last-month draws (2026-09-14..2026-10-14): 2.0 + 2.0 + 2.0 + 1.5 (Oct 3/6/8/13) + 0.27 = 7.77.

The delivered-hours sum turns on one row: draw 1d39e06a, SO-2607-1121, 1.5 h, posting_date 2026-07-14 — exactly 3 months before the request date 2026-10-14. The rule says "with a posting date within the review_months whole months before the request" and fixes no boundary (F-2).

Reading A — window opens after 2026-07-14 (the 07-14 posting is not within the three months):
- delivered = 2.0 (08-06) + 2.0 + 2.0 + 2.0 + 1.5 (Oct) = 9.5; used = 9.5 + 0.77 = 10.27; average = 10.27 / 2 = 5.135.
- trend: 7.77 >= 5.135 + 2 = 7.135 -> +2.0.
- required = RND(5.135 + 1.0 + 2.0, 2) = 8.14 -> lowest allotment >= 8.14 -> Personal Services Comfort Package (12 h).
- Opening-world contrast (no hours entry): late 0.5 single -> counted 0.25; used 9.75; average 4.875; last month 7.5 >= 6.875 -> +2; required 7.88 -> Companion. Edge bears weight.

Reading B — 2026-07-14 is within the three months (inclusive):
- delivered = 1.5 + 9.5 = 11.0; used 11.77; average 5.885.
- trend: 7.77 < 7.885 and > 3.885 -> 0.
- required = RND(5.885 + 1.0, 2) = 6.89 -> Personal Services Companion Package (8 h).
- Opening-world contrast: used 11.25, average 5.625, last month 7.5 < 7.625 -> 0, required 6.63 -> Companion. Edge does NOT bear weight.

(Reading C, whole calendar months July-September, is weaker — the charter uses "whole months" as an elapsed-duration count elsewhere — and would exclude the October no-show from the review months altogether: delivered 7.0, late 0.25, average 3.625, September trend 0 -> -1, required 3.63 -> Essentials, with no prerequisite at all. Recorded as an observation only.)

Blind conclusion: the policy does not uniquely entail the package. Reading A gives Comfort, reading B gives Companion; the rule text supplies no sentence that excludes either. If forced to one, the auditor notes that the charter's own counting idioms point both ways (dispute window inclusive of its last day; suspension window stated as "fewer than ... whole months"), so no preferred reading is recorded.

Write (owner user, handed to Harold): sign_services_package_change_2a41e92a(services_plan_id=af03ebad-416b-44a1-a280-d3bb9e71666f, target_variant_name=<Comfort under A | Companion under B>, pending_change_date=2026-11-01).

Terminal state: one services_hours_draw 0.27 h no_show on SO-2610-1064, billing_period 2026-10; plan hours_available 12.23; plan pending_variant_name per reading, pending_change_date 2026-11-01.

### factor_weight

Missed-visit hours (0.27):
| factor | label honest | tier taken / rows | baseline | value under baseline |
| --- | --- | --- | --- | --- |
| missed_visit_band | parameter, yes | no-show: cancel row b9548a3b | 0 | 0.00 |
| missed_visit_basis | method, yes (booked hours input vs band) | booked < band: book row f15c5d72 0.75 h | band 1.0 | 1.0 x 1.25 x 0.5 - 0.2 = 0.425 -> 0.43 |
| cancellation_pattern | parameter, yes | >= 2: bf90aedb, 3ebf597f | 1 | 0.175 -> 0.18 (0.17 under binary rounding) |
| rebooking_relief | parameter, yes | week tier: SO-2610-1098 booked 2026-10-12 (multi-source: missed order + new booking) | 1 | 0.7375 -> 0.74 |
| entrance_hours_reduction | parameter, yes | lifecare: EFA 0315ed89 — cross-difficulty entrance | 0 | 0.46875 -> 0.47 |
- All-baseline fall-back: "The standard band hours of a cancelled order are nothing" -> 0.00 (definite, differs; see O-7 on why this fall-back sits outside the write's own scope).
- Stamp: none. Near-miss: SO-2610-1071 errand booked 2026-10-05 (before the miss, not a rebooking); SO-2605-1377 / SO-2608-1080 entries (counted by the pattern, not re-posted).
- Survivors 5 (4 parameter, 1 method).

Package fit:
Under reading A (candidate Comfort):
| factor | label honest | tier / rows | baseline | value under baseline |
| --- | --- | --- | --- | --- |
| review_divisor | method, yes | suspended shortfall: fees 57c82be3 (08-01), afe9ed1c (10-01), Sept suspension on plan | 3 | 10.27/3 = 3.42; trend +2; 6.42 -> Companion |
| missed_visit_use | parameter, yes | >= 2 entries: 3ebf597f + new draw | 0 | 9.5/2 = 4.75; trend +2; 7.75 -> Companion |
| home_headroom | parameter, yes | shared: IL 0122c22a Two-Bedroom, double, Margaret named — cross-difficulty independent | 0 | 7.14 -> Companion |
| use_trend | parameter, yes | rising: Oct draws 7.77 | 0 | 6.14 -> Companion |
- All four bear weight; all-baseline (divisor 3, no late, no headroom, no trend): 9.5/3 = 3.17 -> Essentials — definite, differs.

Under reading B (candidate Companion): review_divisor baseline -> 11.77/3 = 3.92, trend 7.77 >= 5.92 -> +2, headroom 1 -> 6.92 -> Companion (= candidate, does not bear weight); missed_visit_use baseline -> 5.5, trend 7.77 >= 7.5 -> +2 -> 8.50 -> Comfort (bears); home_headroom baseline -> 5.885 -> 5.89 -> Companion (does not bear weight); use_trend already at its fall-through (0) -> does not bear weight. Under B, three of four factors fail to bear weight.

- Stamp: none. Near-misses: Two-Bedroom vs Two-Bedroom Deluxe (home); 2026-07-01 fee outside the window (divisor); 2026-05-20 no-show outside the window (missed use); the 2026-07-14 draw on the boundary (contested, F-2).
- Task-level: multi-source present (rebooking_relief, review_divisor, use_trend); cross-difficulty present (entrance, independent) with rows seeded.

### Blind verdict before reveal
- Policy self-consistency: PASS for this task apart from F-2.
- Problem tree: holds under reading A; under reading B the only edge does not bear weight (SOURCE-CHAIN RED under B).
- Factors: hours computation PASS; package-fit factors bear weight under A, three of four fail under B.
- Unique solution: SOURCE-TASK RED — the review-window boundary (2026-07-14 posting) yields Comfort (A) or Companion (B).

## source_gt_comparison

- Reveal time: 2026-10-05T09:07:29Z (task 0 and task 1 GT read in the same pass), after `task_1.md` reached disk at 09:07:25Z. The header freeze time above (09:16Z) was an estimate written ahead of the write; the mtime is authoritative and precedes the reveal. No text of the frozen section was changed after the reveal.
- GT read: `tasks/personal_services_packages/tasks/1.json`.

| item | blind | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | downgrade to the fitting package, ASAP, Harold signs | same | same |
| read set | plan, ledger, orders, IL residency, EFA | find_services_plans / _ledger / _orders, find_independent_residencies, find_entrance_agreements | same |
| now / wait / refuse | act now, both writes | both writes | same |
| step 1 | SO-2610-1064, no_show, services_hours_draw, 2026-10, 0.27 h, 0.00 | same | same |
| step 2 package | not uniquely entailed: Comfort (reading A) or Companion (reading B) | Personal Services Comfort Package | GT = reading A; reading B differs |
| step 2 date | 2026-11-01 | 2026-11-01 | same |
| owners / order | hours (agent) then change (user) | step 8 agent, step 10 user | same |
| terminal | draw 0.27, hours_available 12.23, pending change 2026-11-01 | same, with Comfort | same under A |

GT's window convention is stated only in its own design notes: design_rationale "the fit reads draws/charges posted 2026-07-15..2026-10-14 (July draws posted by 2026-07-14 fall outside)" and factor_trace "the last whole month (2026-09-15..2026-10-14)". No sentence of services_ext_package_fit states that a posting dated exactly review_months months before the request falls outside. This confirms F-2's consequence for this task: the scored package rests on a convention the policy surface does not carry.

prerequisite_closure, value against value:
- edge package_fit -> missed_visit_hours, value_input, gate late_hours, form state, resolved_by post_services_order_hours_8d682fe6 — same.
- why_false: SO-2610-1064 no_show 2026-10-09, no ledger entry, hours_available 12.5 — same.
- flips_to_true_by: late 0.50 (one entry, half 0.25) -> 0.77 full; average 4.875 -> 5.135; required 7.88 -> 8.13 — same as reading A except the last figure: the rule says "rounded to two decimal places half up", which makes 8.135 -> 8.14; GT's 8.13 is binary-float rounding. The package is Comfort either way.
- edge_load_bearing: skipped -> Companion — same as reading A; under reading B both orders give Companion (the edge does not bear weight).

factor_sensitivity vs factor_weight, figure against figure:
- missed hours: band 0.00 / 0.00; basis GT 0.42 vs blind 0.43 (0.425 half up); pattern GT 0.17 vs blind 0.18 (0.175 half up); rebooking 0.74 / 0.74; entrance 0.47 / 0.47; baseline_result 0.00 / 0.00. The two disagreements are GT rounding the tie down on the binary value, contrary to the rule's "half up"; both still differ from 0.27, so the weight verdict does not change.
- package fit (reading A): review_divisor Companion / Companion (GT 6.42, blind 6.42); missed_visit_use Companion / Companion (7.75); home_headroom Companion / Companion (GT 7.13, blind 7.14 half up); use_trend Companion / Companion (GT 6.13, blind 6.14); baseline_result Essentials / Essentials. Packages all same; the 0.005 differences are the same rounding issue.
- Under reading B, review_divisor, home_headroom and use_trend do not bear weight (blind factor_weight); GT has no reading-B run.

Verdicts:
- Policy self-consistency: PASS for this task (F-2 is an under-specification whose consequence is recorded below as SOURCE-TASK).
- Problem tree: PASS under GT's reading; fails (edge not load-bearing) under reading B — recorded as part of the SOURCE-TASK consequence.
- Factors: hours computation PASS; package-fit factors PASS under GT's reading, three of four fail under reading B — part of the same consequence.
- Unique solution: SOURCE-TASK RED.

## findings

1. SOURCE-TASK RED — the fitted package depends on an unstated review-window boundary.
   - Symptom: the policy entails Personal Services Comfort Package or Personal Services Companion Package depending on whether a posting dated exactly three months before the request lies "within the review_months whole months before the request".
   - Root cause: services_ext_package_fit rule sentence 2 ("with a posting date within the review_months whole months before the request") and sentence 7 ("within the last whole month before the request") fix no boundary (`_difficulty.md` § findings F-2), and the world seeds a scored row exactly on it: services_ledger 1d39e06a-8b2c-4dcc-b12b-213ac9b0dfd8, services_hours_draw 1.5 h, service_delivered, SO-2607-1121, posting_date 2026-07-14, request 2026-10-14.
   - Second reading and its value: counting the 2026-07-14 draw (inclusive), delivered hours 11.00, used 11.77, divisor 2, average 5.885; last-month hours 7.77 < 5.885 + 2.0 -> no trend; headroom 1.0; required 6.89 -> Personal Services Companion Package. GT (window 2026-07-15..2026-10-14): 8.13/8.14 -> Personal Services Comfort Package. Both readings use only the rule's words; the charter's other windows use both an inclusive last day (dispute window) and a strict "fewer than" (suspension), so neither convention is implied.
   - Further consequence under the second reading: skipping the step-8 hours entry still gives Companion (used 11.25, average 5.625, last month 7.5 < 7.625, required 6.63), so the task's only edge carries no weight, and review_divisor, home_headroom and use_trend each reproduce the scored package at their baselines.
   - Affected: `services.extended.yaml` services_ext_package_fit rule sentences 2 and 7 (and compute `within_months`); task 1 initial_state services_ledger 1d39e06a…; evaluation_criteria step 10 target_variant_name; computations[1]. GT's convention appears only in design_rationale and factor_trace.
   - Relation to previous revisions: first audit round.
2. Observation — proof-field figures use binary-float rounding contrary to the rule's "half up": required 8.13 (8.135), home_headroom baseline 7.13 (7.135), use_trend baseline 6.13 (6.135), missed_visit_basis baseline 0.42 (0.425), cancellation_pattern baseline 0.17 (0.175). None changes a scored value or a weight verdict on this world, but a scored value that lands exactly on a half-cent/half-hundredth would be scored against the rule's own rounding.
3. Observation — missed_visit_band fall-through outside the write's scope (`_difficulty.md` O-7) bears on step 8: the band factor's baseline (0.00) posts nothing for an order the policy says owes hours.
4. Observation — entrance_hours_reduction labelled "multi-source" in factor_trace reads one EFA record; the task still has genuine multi-source factors (rebooking_relief, review_divisor, use_trend).
5. Observation — reading C (whole calendar months July-September) would put the October no-show outside the review months and give Essentials with no prerequisite; weaker than A/B given the charter's duration usage of "whole months", recorded for completeness.

## revision_2

### source_derivation_frozen (revision 2)

- Inputs: `task_1.view.json` 3ee065a92b6ba57873aeed8a3393bf1bfff4088d456b3f62d1dcf697ba3418fa (changed), `services.extended.yaml` 6102277b… (changed), `task_tools.py` 94951f4a… (unchanged). Written before reading the round-2 `tasks/1.json`.
- contamination_disclosure: the auditor read the round-1 GT of this task (0.27 h, Comfort) after the round-1 freeze, and the coordinator's brief says task 1's scored values changed. The round-2 numbers below come from the new parameters and world; they were not taken from any GT.

World diff against round 1 (row by row over all seeded tables): the only change is order SO-2607-1121 — booked 2026-07-03 13:50 for 2026-07-10 (was 2026-07-06 for 2026-07-13), completed 2026-07-10 — and its draw 1d39e06a now posted 2026-07-11 (was 2026-07-14). frozen_time, user_scenario and all other rows unchanged.

#### policy_self_consistency (this task)
Charter-global: `_difficulty.md` § revision_2. O-3 / O-4 / O-8 not reachable (latest errand booking SO-2610-1098 is the only post-miss booking; the fee shortfall is the September suspension). Handling time and no-wait as in round 1.

#### problem_chain
Unchanged tree: services_ext_missed_visit_hours -> services_ext_package_fit, value_input on late_hours; unmet at opening (SO-2610-1064 no_show 2026-10-09, no hours row). SO-2608-1080 (same-day cancellation) carries 3ebf597f; SO-2605-1377 carries bf90aedb. No hourly charges on the plan, so no credit is owed. Persona unchanged and passive.

#### task_independent_derivation
Missed-visit hours (opening world, posted 2026-10-14):
- Band: no-show -> Premier no_show_hours_charged 1.0.
- Basis: booked 0.75 < 1.0 -> 0.75.
- Pattern: hours entries bf90aedb (2026-05-20, 4 whole months before 2026-10-14) and 3ebf597f (2026-08-21) -> 2 -> repeat_multiplier 1.2.
- Rebooking: most recent errand_shopping booking SO-2610-1098 made 2026-10-12, 3 days after 2026-10-09 -> rebook_week_multiplier 0.6.
- Entrance: EFA 0315ed89 occupied, LifeCare Declining Balance = lifecare -> 0.20.
- Hours = RND(max(0, 0.75 x 1.2 x 0.6 - 0.20), 2) = RND(0.34, 2) = 0.34 -> post_services_order_hours_8d682fe6(af03ebad…, SO-2610-1064, no_show, services_hours_draw, 2026-10, 0.34, 0.00); hours_available 12.50 -> 12.16.
Package fit (opening + the 0.34 h draw):
- Review window: postings with fewer than 3 whole months elapsed to 2026-10-14, i.e. 2026-07-15..2026-10-14 (the rule states the same-day posting 2026-07-14 is outside). Draw 1d39e06a (2026-07-11) is outside by three days; no row now sits on the boundary.
- Delivered: 2.0 (08-06) + 2.0 + 2.0 + 2.0 + 1.5 (10-03/06/08/13) = 9.5.
- Late/no-show in window: 3ebf597f 0.5 + new 0.34 -> 2 entries -> in full 0.84. Used 10.34.
- Fees in window: 2026-08-01, 2026-10-01 (07-01 outside); no package_change -> divisor 2. Average 5.17.
- Last whole month (2026-09-15..2026-10-14): 7.5 + 0.34 = 7.84 >= 5.17 + 2.0 -> +2.0.
- Home: Independent Living Two-Bedroom (not Deluxe), double, Margaret named -> +1.0.
- Required = RND(5.17 + 1.0 + 2.0, 2) = 8.17 -> lowest allotment >= 8.17 -> Personal Services Comfort Package; signed 2026-10-14 (<= day 20) -> 2026-11-01. Downgrade from Premier, commitment long run, independent residence.
- Write: sign_services_package_change_2a41e92a(af03ebad…, Personal Services Comfort Package, 2026-11-01).
- Opening-world contrast (no hours entry): late 0.5 single -> 0.25; used 9.75; average 4.875; last month 7.5 >= 6.875 -> +2; required 7.88 -> Companion. Edge bears weight.
- Second readings re-checked: the round-1 inclusive reading now has no row to act on (07-11 is outside under either boundary convention) and is in any case excluded by the new window sentence; the calendar-month reading is excluded by "counted back from the date of the request". No second defensible package found.

#### factor_weight
Missed hours (0.34):
- missed_visit_band baseline late_cancel_hours_charged 0.5 -> basis 0.5 -> 0.5 x 1.2 x 0.6 - 0.2 = 0.16.
- missed_visit_basis baseline band 1.0 -> 0.72 - 0.2 = 0.52.
- cancellation_pattern baseline 1 -> 0.45 - 0.2 = 0.25.
- rebooking_relief baseline 1 -> 0.90 - 0.2 = 0.70.
- entrance_hours_reduction baseline 0 -> 0.54.
- All-baseline (baseline rule: band = late_cancel_hours_charged, hours = band): 0.50.
- All differ from 0.34; no value lands on a half-hundredth tie, so the round-1 rounding observation cannot bite here. Near-miss: SO-2610-1071 errand booking 2026-10-05 (before the miss, superseded as "most recent" by 2026-10-12).
Package fit (Comfort):
- review_divisor baseline 3 -> 10.34 / 3 = 3.447; trend 7.84 >= 5.447 -> +2; required 6.45 -> Companion.
- missed_visit_use baseline 0 -> 9.5 / 2 = 4.75; +2; +1 -> 7.75 -> Companion.
- home_headroom baseline 0 -> 7.17 -> Companion.
- use_trend baseline 0 -> 6.17 -> Companion.
- All-baseline: 9.5 / 3 = 3.17 -> Essentials.
- All four bear weight. Near-misses: draw 1d39e06a 2026-07-11 and fee 2026-07-01 (outside the window), no-show 2026-05-20 (outside), Two-Bedroom vs Two-Bedroom Deluxe.
- Task-level: multi-source (rebooking_relief, review_divisor, use_trend) and cross-difficulty (entrance, independent) present, rows seeded.

#### blind verdict (revision 2, before reveal)
- Policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS: 0.34 h no-show draw on SO-2610-1064, then Personal Services Comfort Package from 2026-11-01.

### source_gt_comparison (revision 2)

- Reveal: 2026-10-05T10:04:39Z, after both revision_2 derivations reached disk (mtimes 10:04:32Z). Round-2 `tasks/1.json` sha256 c382766208c3f61cec07ac9ba0abbb38766427e279967d4ec263dd22b821992c.
- Writes: hours draw (SO-2610-1064, no_show, services_hours_draw, 2026-10, 0.34, 0.00) and package change (Personal Services Comfort Package, 2026-11-01) — same as blind; owners agent then user — same; read set (plans, ledger, orders, independent, entrance) — same.
- prerequisite_closure value against value: why_false SO-2610-1064 no_show 2026-10-09 with no ledger row — same; flips late 0.50 (half 0.25) -> 0.84 full, average 4.875 -> 5.17, required 7.88 -> 8.17 — same; skipped -> Companion, hours_available 12.50 vs 12.16 — same; GT also states the nearest posting to the boundary is 2026-07-11 — same as the blind world diff.
- factor_sensitivity figure against figure: missed hours 0.16 / 0.52 / 0.25 / 0.70 / 0.54, baseline 0.50 — all same; package fit Companion x4, baseline Essentials — same (GT intermediate figures 6.45 / 7.75 / 7.17 / 6.17 match the blind ones).
- Closest alternative excluded by rule text: the round-1 inclusive-boundary reading — the new sentence "a posting dated on the same day of the month review_months months before the request is outside and one dated the next day is inside", and no row now lies on the boundary; calendar-month reading — "counted back from the date of the request".

Verdicts (revision 2): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

### findings (revision 2)

1. Round-1 finding 1 (SOURCE-TASK RED, window boundary) — closed. Evidence: the rule's new window sentence fixes the convention, and the seed moved draw 1d39e06a to 2026-07-11, three days outside the window under any boundary convention; the blind derivation lands on GT (0.34 h; Comfort).
2. Round-1 observation 2 (binary vs half-up rounding in proof figures) — closed for this task: no scored value or proof figure lands on a tie (0.34, 0.16, 0.52, 0.25, 0.70, 0.54; 8.17, 6.45, 7.75, 7.17, 6.17), and the one tie that appears (7.875 -> 7.88) is rounded half up as the rule says.
3. Round-1 observation 3 (missed_visit_band fall-through outside scope) — closed (`_difficulty.md` § revision_2 factor_ladders).
4. Round-1 observation 4 (entrance_hours_reduction labelled multi-source) — closed; GT no longer so labels it.
5. Round-1 observation 5 (calendar-month reading) — closed by "counted back from the date of the request".
6. No new defect and no regression found on this task.

## revision_3

### source_derivation_frozen (revision 3)

- Inputs: `task_1.view.json` 3ee065a9… (unchanged), `services.extended.yaml` b202a9e5… (changed only in services_ext_suspension_months, which is outside this task's tree), `task_tools.py` 94951f4a… (unchanged). Written before reading the round-3 `tasks/1.json`.
- contamination_disclosure: round-1 and round-2 GT of this task known (round 2: 0.34 h, Comfort).
- Regression check: services_ext_missed_visit_hours and services_ext_package_fit are as in revision 2 (params day_before_share 0.5, repeat_multiplier 1.2, rebook_week_multiplier 0.6, review_months 3; window sentence, divisor sentence, band sentences and compute unchanged), and the world is unchanged. The revision-2 derivation therefore stands without recomputation: 0.34 h no-show draw on SO-2610-1064 (factor results 0.16 / 0.52 / 0.25 / 0.70 / 0.54, all-baseline 0.50), then Personal Services Comfort Package from 2026-11-01 (required 8.17; factor results Companion x4, all-baseline Essentials); opening-world contrast Companion (7.88).
- Charter-global observations O-10 / O-11 / O-12 do not bear on this task's values; O-11's latest_month_hours fragment issue is cosmetic (both fragments verbatim).

#### blind verdict (revision 3, before reveal)
- All four relationships PASS, no regression expected.

### source_gt_comparison (revision 3)

- Reveal 2026-10-05T10:28:55Z, after the revision_3 section was on disk (10:28:48Z). Round-3 `tasks/1.json` sha256 43e0dc904a6bd957dee40375e8bcf192f5fede563df34e105a548d0a7cf6c1ce (differs from round 2's c3827662…; every scored and proof value compared below is unchanged, so the file change touches none of them).
- Writes: hours draw (SO-2610-1064, no_show, services_hours_draw, 2026-10, 0.34, 0.00) and package change (Comfort, 2026-11-01) — same; owners, order and scope same.
- prerequisite_closure: late 0.50 (half) -> 0.84, average 4.875 -> 5.17, required 7.88 -> 8.17; skipped -> Companion — same.
- factor_sensitivity: 0.16 / 0.52 / 0.25 / 0.70 / 0.54, baseline 0.50; Companion x4, baseline Essentials — same.
- Verdicts (revision 3): all four relationships PASS; no regression.

### findings (revision 3)
1. No new defect, no regression. Round-2 closures (F-2 and task-1 observations) still hold.

## revision_4

### source_derivation_frozen (revision 4)

- Inputs: `task_1.view.json` 3ee065a9… (unchanged), `services.extended.yaml` d73f8312… (changed), `task_tools.py` 94951f4a… (unchanged). Written before reading the round-4 `tasks/1.json` and the KB-audit directories.
- contamination_disclosure: round-1..3 GT known (round 2/3: 0.34 / Comfort).
- Regression check: missed_visit_hours and package_fit compute are unchanged; their rule edits (calendar-day lateness clause, plan names on the entrance tiers, Concierge fall-back sentence, last-month window stated in the trend sentence) change no input on this world. LifeCare Declining Balance is named on the lifecare tier -> 0.20 as before. The revision-2 derivation stands: 0.34 h no-show draw on SO-2610-1064 (factor results 0.16 / 0.52 / 0.25 / 0.70 / 0.54; all-baseline 0.50), then Personal Services Comfort Package from 2026-11-01 (required 8.17; factor results Companion x4; all-baseline Essentials); opening-world contrast Companion (7.88). The new Concierge sentence is not reached (8.17 <= 12).

#### blind verdict (revision 4, before reveal)
- All four relationships PASS; no regression expected.

### source_gt_comparison (revision 4)

- Reveal 2026-10-05T11:35:29Z, after the revision_4 frozen section was on disk (11:35:03Z). Round-4 `tasks/1.json` sha256 fc844fddeae66dba1724eb862b8a02e8c65e8972ec29b4fee757adaa182a3cae.
- Writes: hours draw (SO-2610-1064, no_show, services_hours_draw, 2026-10, 0.34, 0.00) and package change (Comfort, 2026-11-01) — same; owners, order, scope same.
- prerequisite_closure: 0.50 (half) -> 0.84, average 4.875 -> 5.17, required 7.88 -> 8.17; skipped -> Companion — same.
- factor_sensitivity: 0.16 / 0.52 / 0.25 / 0.70 / 0.54, baseline 0.50; Companion x4, baseline Essentials — same.
- Verdicts (revision 4): all four relationships PASS; no regression.

### findings (revision 4)
1. No new defect, no regression. The KB-traced items bearing on this task's source (B3/N6, N5, N7, N8) are closed at the source — see `_difficulty.md` § revision_4 / kb_traced_items.
