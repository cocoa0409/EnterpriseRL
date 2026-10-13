# Policy-task audit — autoship_subscription_care / charter-global

## charter_global_frozen

- Freeze hashes (sha256, verified against the orchestrator brief before reading):
  - `tasks/autoship_subscription_care/autoship.extended.yaml` a1da9f7055266ea8a92b74936d659038ef3e698223a5f6b48dbd883d8fed9c77
  - `tasks/autoship_subscription_care/task_tools.py` 1f6ba94c4c40f02b2af1c4d5de4a447af62121d3c718c0769da2cf82cdead3ce
- Freeze time: 2026-10-06T06:05Z (written before any task GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Fields permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state only), and the evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`/`eval_compute`, read as the engine's definition of SUM/COUNT/within_months/CFIELD/XCOUNT; no task file is opened by it in this use).
- Fields masked (not read before the freezes): everything in `tasks/autoship_subscription_care/tasks/*.json` other than the masked views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the instantiate worklog, `env/env_0040_pet_supplies_retailer/worklog.md`, and any earlier audit. No search was run with tasks/*.json in its domain.
- Entry conditions (Step 0): gate snapshot supplied at `/tmp/e40views/policy_task/autoship_subscription_care/gate_snapshot.txt`. It shows check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all green, with check_traceability deferred. View hashes match the brief (4b86af9d… / be84b74c…). The base section of the extended charter is byte-identical to `blueprint/products/autoship.yaml` (`diff` of lines 1–1590 against the product file is empty).

### policy_conflict_scan

Six extended policies, all `overwrite: []`:

| policy | trigger | event | target_tool (owner) | computes | scope it governs |
|---|---|---|---|---|---|
| autoship_ext_rx_shipment_packages | state_due | autoship_modify | set_rx_shipment_packages_d23afb64 (agent) | quantity | pharmacy Autoship, package count under the linked (renewed) prescription |
| autoship_ext_rx_shipment_interval | state_due | autoship_modify | set_rx_shipment_interval_b175142c (agent) | frequency_weeks | pharmacy Autoship, re-timing under the linked prescription |
| autoship_ext_household_interval | on_request | autoship_modify | set_shipment_interval_36e38cde (agent) | frequency_weeks | non-prescription food Autoship shared by >1 pet, when one pet leaves for an Rx diet |
| autoship_ext_rx_diet_enrollment_bags | on_request | autoship_enroll | enroll_rx_autoship_732fccd3 (user) | quantity | new Autoship Pharmacy for an Rx Prescription Diet of a pet that already has a prescription Autoship |
| autoship_ext_existing_pet_quantity | on_request | autoship_modify | set_shipment_quantity_8a323a9d (agent) | quantity | non-prescription Autoship shared by >1 pet, when another pet gets its own Autoship of the same item |
| autoship_ext_second_pet_enrollment_interval | on_request | autoship_enroll | enroll_everyday_autoship_7ae73b8d (user) | frequency_weeks | new Autoship Everyday for a second pet for an item already on another pet's Autoship |

- Overlapping subjects: the two `quantity` modifies are split by program class (pharmacy vs non-prescription); the two `frequency_weeks` modifies likewise. household_interval and existing_pet_quantity share an object class (a shared non-prescription food Autoship) but have disjoint triggers (a pet leaving for an Rx diet vs. another pet getting its own Autoship of the same item) and write different fields (frequency vs quantity, each rule saying the other field "stay[s] as [it is]"). No two policies reach different values for one field of one subscription under one trigger. The two enrollments are split by program (Pharmacy vs Everyday).
- Time anchors: all extended rules evaluate at the moment of the write ("before the re-set", "ago" = NOW). Month windows ("in the last N months") are not given a counting convention anywhere in the charter; see finding F-G4.
- Cross-category reads: member (status/variant), rx (prescription fields, rx_events fills/overrides/channels, class parameter refill_too_soon_pct), vet (plans, plan events), order (order_line_charge), train (enrollments, sessions). All read-only.
- Scope exclusivity and completeness: inferred tree shapes (from the prerequisite graph alone) are {diet ← interval ← packages; diet ← household} and {second_pet ← existing_pet_quantity}. Those two trees partition the six policies; they are disjoint and jointly complete. The gate snapshot's SCOPE line agrees. The declared `charter_scope` of each task is masked until the reveal and is compared in the task files.

### rule_compute_equivalence

Each binding's `compute_basis` quotation was checked against the rule text, and each rule sentence was checked for an implementing binding. Results:

- packages: every quantity, window (12 months scheduled charges; 6 months declines), tier and cap is quoted and implemented. `mem_tier` lists the three Plus tiers by name, matching "any Tailwise Plus tier" (member.yaml variants are Monthly, Annual and Premier Annual). The rounding (ceil, floor to block) matches. **Equivalent.**
- interval: the lost-then-travel priority, linked-or-renewed prescription, replacements, skips, ship-now, one-time-order fills and panels are all quoted and implemented, as are the order of operations and the clamp. Sweep-back gap: the rule counts "a blood panel … redeemed" on "any of the customer's wellness plans", and the vet charter's own measure counts redeem rows "not voided by a vet_service_void row" (vet.yaml l.655). The compute counts raw `vet_service_redeem` rows without excluding voided ones. This is an observation (O-G1); neither task world contains a void row.
- household: the windows, rose test, branch and terms match the rule. Behaviour with zero charges in a half-year (averages undefined) is unstated in the rule; the compute treats it as "not rose". Observation O-G2. It does not arise in either world.
- rx_diet_enrollment_bags: **one divergence (F-G1)**. The rule caps the bag count by "the program's max_quantity_per_shipment" and "the program's rx_max_days_supply_per_shipment", where the program is the new subscription's, Autoship Pharmacy. The compute reads `P('max_quantity_per_shipment')` and `P('rx_max_days_supply_per_shipment')`, which `build_env` resolves from the variant of the bound holding H. H is the pet's existing prescription Autoship (the companion), and the rule's scope admits a companion on Autoship Compounded Pharmacy. Also an observation (O-G3): `diet_rx_id`, `diet_fill_days` and `diet_fill_bags` pick the customer's first active Rx Prescription Diet (`CFIELD(..., variant_name='Rx Prescription Diet', status='active')`) with no pet filter, while the rule says "the pet's … prescription".
- existing_pet_quantity: all quoted and implemented. The halving uses floor and the three-quarters uses ceil, matching the rule. **Equivalent.**
- second_pet_enrollment_interval: **one divergence (F-G2)**. The rule reads "the customer holds a training enrollment in status in_progress and course_min_sessions or more of **its** sessions were attended in the last course_window_months months". The compute counts `XCOUNT('train','train_sessions', within_months=1, event_type='train_session_attend')` over every training session of the customer, not only those of the in_progress enrollment.
- Every factor's ladder tiers appear both in the rule prose and as branches of the `decides` binding, and every branch is a rule tier. No tier lives in only one face.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct (see table). Each target tool is claimed by exactly one policy.
- Docstrings: no docstring names another tool, states a position in a sequence, or uses before/after/first about the tool order. "after the upcoming one" and "after the previous one" in the two interval tools describe shipment scheduling, not call order. Neither docstring adds a confirmation, wait or review. enroll_everyday's arguments point at "the household's existing Autoship of the item" as the source of sku, description, price and weight. That is a data source, not an order.
- Tool bodies: each is a single `ctx.update`/`ctx.create` with no branch, no validation and no error path. **The tool layer judges no prerequisite** (relevant to every task's problem_chain).
- uuid8s: d23afb64, b175142c, 36e38cde, 8a323a9d, 732fccd3, 7ae73b8d. They are pairwise distinct with no shared prefix, no shared tail and no sequential pattern, so they are consistent with independent generation. PASS.

### prerequisite_graph

Edges (check 7):

| # | blocked policy | problem | kind | gate | form | resolved_by |
|---|---|---|---|---|---|---|
| E1 | rx_shipment_interval | rx_shipment_packages | value_input | shipment_supply_days (exists; reads F('quantity')) | action | set_rx_shipment_packages_d23afb64 (= packages target_tool) |
| E2 | rx_diet_enrollment_bags | rx_shipment_interval | value_input | companion_interval_days (exists; reads F('frequency_weeks')) | action | set_rx_shipment_interval_b175142c (= interval target_tool) |
| E3 | rx_diet_enrollment_bags | household_interval | state_gate | autoship_subscriptions.frequency_weeks (the household Autoship's field; no compute binding, which is acceptable for a gate) | action | set_shipment_interval_36e38cde (= household target_tool) |
| E4 | second_pet_enrollment_interval | existing_pet_quantity | value_input | existing_weekly_units (exists; reads F('quantity')) | action | set_shipment_quantity_8a323a9d (= existing target_tool) |

- `prerequisite` is filled on all six policies (`[]` on packages, household and existing_pet_quantity). Every `problem` is another extended policy id, never a base policy and never self. The graph is acyclic: packages→interval→diet, household→diet, existing→second.
- Each `policy_source` is a verbatim sentence of the blocked policy's own rule (located: interval rule sentence 3; diet rule sentences 2 and 3; second_pet rule sentence 2).
- Every edge is `form: action` with a `fallback_reason`, and `fallback_reason` is present exactly on those edges.
- `condition` states the handling-time state check 6 derives (the depended-on field holds the value that policy's own rule gives). It is not strengthened or weakened, and contains no authoring-viewpoint phrasing.
- Each `effect` is real. The E1 write moves `F('quantity')`, which feeds shipment_supply_days. The E2 write moves `F('frequency_weeks')`, which feeds companion_interval_days. The E4 write moves `F('quantity')`, which feeds existing_weekly_units and also the root's own `F('quantity') * new_pet_unit_days` term. E3 is a pure gate.
- PASS.

### prerequisite_sentences

Four-point test per edge:

- E1 "The weeks between shipments of a pharmacy Autoship are re-timed only after its package count per shipment has been re-set under the prescription it is linked to."
  - Own result (the re-timing) is joined by "only after" to an action in business words. No tool, id or snake_case token appears.
  - Strength matches the condition.
  - Fallback test: the write leaves only `quantity`. No record field marks "re-set under the linked prescription", and the only record-visible test would be the computed value itself. The fallback is justified.
  - Single-reading derivation: "package count per shipment … re-set under the prescription it is linked to" leads to the one policy whose rule "sets the package count per shipment of an Autoship Pharmacy … whenever that count is re-set under the prescription the subscription is linked to" (packages). No other policy writes a pharmacy quantity.
- E2 "The bag count of a prescription diet Autoship that ships alongside the pet's medication Autoship is not fixed until the weeks between that medication Autoship's shipments have been re-timed under its current package count."
  - "not … until", action form, no tool or id. The fallback is justified on the same grounds.
  - Derivation: "weeks between … medication Autoship's shipments … re-timed" leads to the interval policy, which is the only policy re-timing a pharmacy Autoship. ("under its current package count" in turn agrees with E1.)
- E3 "A prescription diet Autoship for a pet is not set up before the shared household food Autoship the pet has been eating from has been re-timed for the pets that stay on it."
  - "not … before", action form, no tool or id. The fallback is justified: a frequency carries no provenance.
  - Derivation: "shared household food Autoship … re-timed for the pets that stay" leads to household_interval, whose rule names exactly that ("re-timed for the pets that stay on it").
- E4 "The weeks between shipments of a second pet's own Autoship for an item the household already receives are worked out only after the existing Autoship of that item has been re-sized to its own pet's usage."
  - "only after", action form. The fallback is justified.
  - Derivation: "re-sized to its own pet's usage" leads to existing_pet_quantity ("the existing subscription is re-sized to its own pet's usage").
- Restatement checks:
  - No depended-on rule restates its dependent's sentence. packages says nothing about interval. household says nothing about the diet enrollment's order; its trigger clause "when a pet that ate from it moves to a prescription diet" states no order. existing_pet_quantity's trigger clause "when another pet of the household gets its own Autoship" states no order.
  - No rule carries a second wording of a dependency, a tool name or another policy id.
  - The diet rule's "the new subscription ships on the same weeks between shipments as that existing prescription Autoship" and second_pet's "ships the same units per shipment as the existing Autoship carries" are value reads already grounded by E2 and E4. They are not undeclared orders.
- No base rule sentence is used to ground an edge.
- PASS (no SOURCE-POLICY finding from check 6).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- `autoship_change_rules`, cited by packages, interval, household and existing_pet_quantity:
  - "The customer may change the frequency, the quantity, the next ship date …": extended follows it. The extended modifies change exactly quantity or frequency.
  - "status … pending_first_shipment, active, paused, payment_hold or rx_hold": inherited; the extended rules do not weaken it.
  - Cutoff sentences: inherited. They govern which shipment a change affects, not the scored number.
  - "A new frequency must respect min_frequency_weeks, max_frequency_weeks and frequency_step_weeks": followed. The clamp is in every frequency compute. Step is 1 week for every program the extended policies touch.
  - "a new quantity may not exceed max_quantity_per_shipment": followed (MN cap in packages and existing).
  - "a new next ship date …", "A swap …", "Custom Meal Plan …", "Pharmacy items cannot be swapped": not touched.
  - Observation O-G4: packages and interval are `state_due` changes made "whether or not the customer raises it". The base event meaning of autoship_modify lists customer changes plus two named system changes (moving the date after a skip, meal-plan recalculation). The base rule's "The customer may change" is permissive, not exclusive, so this is not an undeclared override. It is recorded as an observation.
- `autoship_agg_multi_holding` and `autoship_enrollment_requirements`, cited by the two enrollments:
  - Dedup (same customer, item and pet) is inherited.
  - "Subscriptions for different pets … are separate" is followed (second_pet).
  - "pet_profile_required … linked to a pet profile" is inherited. Both tools take pet_id.
  - Program from item class is followed: the Rx diet is a prescription item, giving Autoship Pharmacy; a standard catalog item gives Everyday.
  - "linked prescription … active … fills_remaining ≥1 … expires_on later than the first ship date" is inherited.
  - The frequency range, quantity cap, and "quantity x days' supply per unit ≤ rx_max_days_supply_per_shipment" are followed. The diet compute caps by `int(rx_max/diet_bag_days)`, but see F-G1 for which program's value it reads.
  - "first ship date is the date the customer chooses, no earlier than the enrollment date … ship_weekdays … moves to the next listed weekday" is followed; both extended rules say "the date the customer chooses".
  - "Enrolling is free" is not touched.
- No disguised override was found. There is no anonymous intermediate factor, no 0/1 multiplier and no dropped base branch. No author note calls a base output wrong.
- PASS (no undeclared override).

### factor_ladders

Per policy, the declared factors are listed below. "MS" means multi-source (the non-fall-through tiers combine two or more conditions over distinct records). "XD" names the cross-difficulty category.

- packages: 5 factors, 4 parameter and 1 method.
  - extended_supply_loyalty: parameter, MS (membership × Autoship enrolment date), XD member. Tiers 60 / 30 / 0.
  - steady_refill_record: parameter. 42 / 35 / 0.
  - renewal_recheck_holdback: parameter, MS (origin × authorized_on), XD rx. 21 / 7 / 0.
  - payment_decline_holdback: parameter. 14 / 10 / 0.
  - senior_recheck_cycle: method, MS (vet plan × rx class), XD vet. Tiers: floor to 14-day blocks / floor to 7-day weeks / as worked out. **Label failure F-G3a**: `target_supply_days` is always a whole number (every input is an integer K or an integer count), so the three tiers are the single expression floor(x/b)·b with b = 14, 7, 1. Only a number is substituted, so the factor is a parameter.
  - Baseline: `baseline.rule` is the rule's sentences 3–6 verbatim and is self-sufficient (standard 30 days → packages). Every fall-through equals the baseline.
- interval: 6 factors, 5 parameter and 1 method.
  - dose_loss_reserve: method, XD rx. Tiers: ×90 % floored / ×95 % floored / in full. **Label failure F-G3b**: this is a rate substitution (90, 95, 100 %) into one expression, which the skill names verbatim as a mislabelled method.
  - replacement_delivery_lead: parameter. 9 / 5 / delivery_days_after_ship.
  - skip_stretch: parameter. 21 / 14 / 0.
  - ship_now_pull: parameter. 6 / 3 / 0.
  - outside_fill_pull: parameter, XD rx. 6 / 3 / 0.
  - lab_recheck_pull: parameter, XD vet. 4 / 2 / 0.
  - Baseline: self-sufficient, verbatim in the rule.
- household: 6 factors, 5 parameter and 1 method.
  - usage_measuring_window: method. Tiers: 3-month units/13 weeks, 4-month units/17 weeks, 6-month units/26 weeks. **Label failure F-G3c**: all three are "scheduled units in the trailing N months ÷ weeks in N months", with N = 3, 4 or 6. Only the window length is substituted.
  - skip_stretch: parameter. 21 / 14 / 0.
  - growing_pet_pull: parameter, MS on the adult tier (plan × enrolment date), XD vet. 7 / 3 / 0.
  - ship_now_pull: parameter. 4 / 2 / 0.
  - outside_food_pull: parameter, XD order. 6 / 3 / 0.
  - diet_switch_overlap: parameter, XD rx. 4 / 2 / 0.
  - Baseline: self-sufficient, verbatim.
- rx_diet_enrollment_bags: 6 factors, 5 parameter and 1 method.
  - companion_consolidation: method, MS (status × last-charge age × interval). Tiers: companion interval+21 / full fill − one bag / full fill. These are genuinely different bases, so the method label is honest.
  - starter_bag_on_hand: parameter, XD rx. 4 / 2 / 0.
  - life_stage_transition: parameter, XD vet. 4 / 2 / 0.
  - regular_food_on_hand: parameter, XD order. 3 / 1 / 0.
  - diet_refill_window: parameter, XD rx (class parameter). 2 / 1 / 0. **Unreal ladder F-G5**: the condition reads "the refill-too-soon percent of the diet prescription's class". The class is always Rx Prescription Diet, both in the rule's own scope and in compute (`variant_name='Rx Prescription Diet'`). rx.yaml l.249 fixes `refill_too_soon_pct: 70` for that class, and window_low_pct is 70. Tier 1 therefore holds of every customer who reaches this write, and tiers 2 and 3 are unreachable.
  - companion_decline_trim: parameter. 3 / 1 / 0.
  - Baseline: self-sufficient, verbatim.
- existing_pet_quantity: 4 factors, 3 parameter and 1 method.
  - member_cushion: method, MS (membership × charge count), XD member. Tiers: floor(14/2)=7 / ceil(14·3/4)=11 / 14. **Label failure F-G3d**: every tier is a fixed number independent of any input, so it is a pure parameter ladder (7 / 11 / 14).
  - skip_trim: parameter. 2 / 1 / 0.
  - life_stage_trim: parameter, XD vet. 1 / −2 / 0.
  - tenure_trim: parameter. 1 / −1 / 0. Observation O-G5: a subscription's age as a driver of a pet's covered days is weakly grounded. It is defensible as a forecast-uncertainty cushion, so it is not struck.
  - Baseline: self-sufficient, verbatim.
- second_pet_enrollment_interval: 6 factors, 5 parameter and 1 method.
  - settled_household_window: method. Tiers: all shipments incl. ship-now over 6 months / all shipments over 3 months / scheduled only over 6 months. The fall-through changes the row set (ship-now excluded) as well as the window. Accepted as an honest method, though borderline.
  - skip_stretch: parameter. 14 / 7 / 0.
  - training_treat_stretch: parameter, MS (enrollment status × sessions), XD train. 9 / 4 / 0.
  - growing_pet_pull: parameter, MS on the adult tier, XD vet. 4 / 2 / 0.
  - replacement_delivery_lead: parameter. 9 / 5 / delivery_days_after_ship.
  - ship_now_pull: parameter. 6 / 3 / 0.
  - Baseline: self-sufficient, verbatim.
- General ladder checks:
  - Every ladder has 3 pairwise-disjoint tiers. No two tiers of one ladder select the same value, method or outcome.
  - Every `decides` is an input, not `result`. Binding sets are pairwise disjoint within each policy.
  - Each factor's `baseline` equals what `baseline.rule` gives for that input (0 for each added or held-back days term, delivery_days_after_ship for the lead, the standard 6-month window and the standard cushion).
- **Counts after striking failed factors.** A mislabelled factor is not counted under its label, and an unreal ladder is not counted.
  - packages: 0 method (F-G3a), so the method count fails.
  - interval: 0 method (F-G3b), so the method count fails.
  - household: 0 method (F-G3c), so the method count fails.
  - diet: 1 method; diet_refill_window is struck (F-G5), leaving 5 factors, which is within bounds.
  - existing: 0 method (F-G3d); with member_cushion re-labelled as parameter it has 4 factors, all parameter, so the method count fails.
  - second_pet: within bounds.
- Per task (inferred trees), multi-source and cross-difficulty factors are present:
  - task 0: MS = loyalty, senior, renewal, growing_pet, companion; XD = member, rx, vet, order.
  - task 1: MS = member_cushion, training, growing_pet; XD = member, vet, train.

### findings

- **F-G1 SOURCE-POLICY RED (rule ≠ compute), rx_diet_enrollment_bags.**
  - Symptom: the bag-count caps read the companion's program parameters, while the rule names the new subscription's program.
  - Evidence: the rule says "The bag count never exceeds … the program's max_quantity_per_shipment, or the whole number of bags whose combined days fit within the program's rx_max_days_supply_per_shipment". The rule's first sentence makes the program "a new Autoship Pharmacy subscription". The compute is `result: int(MN(MN(P('max_quantity_per_shipment'), diet_fill_bags), MN(int(P('rx_max_days_supply_per_shipment') / diet_bag_days), …)))`, with `P` bound to holding H, which is the companion (`F('frequency_weeks')` and `F('status')` are the companion's).
  - Demonstration (constructed situation): a companion on Autoship Compounded Pharmacy (max_q 2, rx_max 30), a diet with days 84 and bags 3 (bag 28 days), and diet days 70. The rule gives min(3, 3, int(90/28)=3, ceil(70/28)=3) = 3 bags. The compute gives min(2, 3, int(30/28)=1, 3) = 1 bag.
  - Affected: the compute `result` of autoship_ext_rx_diet_enrollment_bags. It bears on task 0's scope, but on task 0's world the companion is Autoship Pharmacy, so no scored value moves (see 0.md).
- **F-G2 SOURCE-POLICY RED (rule ≠ compute), second_pet_enrollment_interval.**
  - Symptom: training sessions are counted across all of the customer's enrollments instead of "its" (the in_progress enrollment's).
  - Evidence: the rule text quoted above; the compute is `course_sessions_recent: XCOUNT('train','train_sessions', within_months=K('course_window_months'), event_type='train_session_attend')` with no train_enrollment_id filter.
  - Demonstration (constructed situation): an in_progress enrollment with 1 session last month, plus a just-completed enrollment with 3 sessions last month. The rule gives the light tier (4 days); the compute gives the active tier (9 days).
  - It bears on task 1's scope. On task 1's world there is one enrollment, so nothing moves (see 1.md).
- **F-G3 SOURCE-FACTOR RED (mislabelled method; the per-computation method floor is not met)** in packages (a: senior_recheck_cycle), interval (b: dose_loss_reserve), household (c: usage_measuring_window) and existing_pet_quantity (d: member_cushion). The tier expressions are quoted above.
  - Demonstration: in each case every tier is one expression with a different constant (b ∈ {14, 7, 1}; rate ∈ {0.90, 0.95, 1.00}; N ∈ {3, 4, 6} months; cushion ∈ {7, 11, 14}).
  - Bears on task 0 (a, b, c) and task 1 (d).
- **F-G4 SOURCE-TASK-capable ambiguity: month-window counting convention.**
  - Symptom: no rule of the charter defines whether "in the last N months" includes a record dated exactly N calendar months before the handling date. The engine (`MONTHS` with day adjustment, `0 <= m < N`) excludes it.
  - The base charter elsewhere fixes its windows explicitly ("rolling 365 calendar days ending on the request date"; cutoff "counted in calendar days backward … a request dated exactly … is in time").
  - The convention matters only where a record falls on the boundary date. That happens in task 0: household Autoship charge 2026-07-06 against the 3-month window from 2026-10-06. The demonstration is in 0.md. Task 1 has no boundary hit.
- **F-G5 SOURCE-FACTOR RED (unreal ladder), rx_diet_enrollment_bags / diet_refill_window.**
  - Evidence: the diet rule says "The diet's early-refill window takes days off the diet days: when the refill-too-soon percent of the diet prescription's class is window_low_pct or less, window_low_trim_days days come off; when it is above window_low_pct but no more than window_mid_pct …; otherwise no days come off." The compute is `diet_refill_pct: CPARAM('rx','refill_too_soon_pct', variant_name='Rx Prescription Diet', status='active')`, and rx.yaml l.240–249 gives `Rx Prescription Diet … refill_too_soon_pct: 70`. window_low_pct is 70.
  - Consequence: the condition holds of every customer who reaches this write, so the ladder restates the scope rather than dividing customers.
  - Bears on task 0.
- Observations:
  - O-G1: voided panel redeems are not excluded.
  - O-G2: zero-charge half-year behaviour is unstated.
  - O-G3: the diet prescription lookup is not pet-scoped.
  - O-G4: the state_due modify sits outside base event wording.
  - O-G5: tenure_trim realism is weak.
  - O-G6: packages' "came as a renewal" condition coincides with the state_due trigger ("Once a renewed prescription has been linked"). It does not hold of every customer, because the rule's scope sentence is "whenever that count is re-set", so it is not struck.

## closing_checklist

Written 2026-10-06T06:20Z, after both reveals. It is placed below the pre-reveal charter-global section, which was not edited.

**The difficulty is NOT closed: the source-layer audit does not pass.** Item status:

- Audit files correspond one-to-one with the tasks (0.md, 1.md, plus this file). This is the first revision.
  - The comparisons do **not** all PASS:
    - task 0 has SOURCE-TASK RED (T0-1) and SOURCE-FACTOR RED (T0-2, T0-3);
    - task 1 has SOURCE-FACTOR RED (T1-1).
- Coverage and scope:
  - charter_scope task 0 = {packages, interval, household, diet}; task 1 = {existing_pet_quantity, second_pet}. They are disjoint and complete, and identical to the trees derived blind.
  - The task tools are closed (4 + 2 = 6) and the uuid8s are independent.
  - PASS.
- Trees:
  - task 0: n = 3, 2 value_input edges, user root, acyclic;
  - task 1: n = 1, 1 value_input edge, user root;
  - the union graph is acyclic.
  - PASS, subject to T0-1's reading B, which would leave E3 already met.
- Factors: baselines are self-sufficient and every factor bears weight on its world (all figures match GT). However:
  - the method floor fails in 4 of 6 computations (F-G3a–d);
  - one ladder is unreal (F-G5).
  - **FAIL.**
- Charter-global SOURCE-POLICY rule/compute divergences F-G1 (diet caps read the companion's program) and F-G2 (training sessions are not scoped to the in_progress enrollment). Neither moves a scored value in M = 2, but both are open defects of the charter.
- Instantiation gates: the orchestrator's snapshot is all green, with check_traceability deferred. Not re-run by the auditor (Step 0: cited only). The re-run on the final form is pending a rework.

> Timestamp correction (appended, frozen text left untouched): the wall-clock times written above are estimates. The machine record is: audit dir created 06:01:19Z; all three files written and their pre-reveal sha256 taken at 06:04:44Z (`date -u` in the same command); the GT reveal (first read of tasks/*.json) happened immediately after, in the next command. The order freeze -> hash -> reveal holds; only the stated clock values were approximate.

## revision_2

### charter_global_frozen (revision 2)

- Inputs:
  - `autoship.extended.yaml` sha256 **bae7d16e0f92c6c6d6387cc568c011304519223ee4b8bfc79c252961a72d97cb**, changed from a1da9f70…. The whole charter-global section is therefore re-derived in full below.
  - `task_tools.py` 1f6ba94c… is unchanged. Its tool-module conclusions (bare bodies, uuid8s, docstrings) are carried forward from revision 1 on the strength of the unchanged hash.
- Base section: still byte-identical to `blueprint/products/autoship.yaml`.
- Round-1 charter: recovered byte-exact from the session's persisted output (sha256 a1da9f70… verified) and diffed policy by policy.
  - Changed keys: packages (rule, params, compute, compute_basis, factors); interval (same); household (plus baseline, inputs); diet (plus baseline, inputs, cross_category); existing_pet_quantity (plus baseline); second_pet (rule, compute, compute_basis, factors, cross_category).
  - `prerequisite` fields are unchanged on every policy.
- Gate snapshot r2 (`gate_snapshot_r2.txt`): all 7 green, check_traceability deferred.
- Written before any revision-2 GT was read. Masked: as in revision 1 (tasks/*.json GT fields, worklogs).
- Contamination: none. The coordinator's brief lists item ids only, with no values.

### policy_conflict_scan (r2)

- Subjects, triggers, objects and fields are unchanged from r1. The diet scope is narrowed: "when the pet already has an Autoship Pharmacy subscription in its name".
- No new overlap.
- Every rule now states one month-window convention: "A record counts as dated in the last N months when its date is later than the same calendar day N months before the day the value is worked out, so a record dated exactly N months earlier does not count; a record dated between six and twelve months ago is one dated in the last twelve months but not in the last six months." This is identical to the engine's `0 <= MONTHS(d, NOW) < N`, as checked on both worlds. The sentence is uniform across the six rules, so it creates no conflict.

### rule_compute_equivalence (r2)

- Programmatic sweep: every `compute_basis` value is a verbatim substring of its rule; every binding has a basis; every `baseline.rule` sentence is in the rule; every param is named in its rule except diet `week_days`, which is implicit in "weeks between shipments in days" (observation R2-O5, unchanged from r1).
- Manual review of each changed binding against its new sentence:
  - packages `plan_term_end`/`counted_supply_days` tier 2 = `MN(target, DAYS(NOW, term_end))`. Matches "capped at the days left from the day of the re-set to the last day of that wellness plan's current term".
  - interval `usable_supply_days` tier 1 = `MX(0, supply − lost_reserve_days)`. Matches "held back … never going below zero".
  - interval panels = redeems − voids. Matches "counting blood panels redeemed less those voided" (**O-G1 closed**).
  - household `latest_sched_units`/`household_weekly_units` and the rose test match the new sentences. The rose test now requires both periods to be non-empty (**O-G2 closed**; the same wording was added to existing_pet_quantity and second_pet).
  - diet: CFIELD now carries `pet_id=F('pet_id')`. Matches "the pet's … prescription" (**O-G3 closed**). The caps' `P()` resolves on the companion, whose program the rule now fixes as Autoship Pharmacy ("Autoship Pharmacy is the program of both the new subscription and the pet's existing subscription"; scope "already has an Autoship Pharmacy subscription"). Rule and compute now name the same program (**F-G1 closed**).
  - existing: `household_rose`/`own_pet_weekly_units` (three tiers) and the cushion constants match the rule.
  - second_pet: `course_sessions_recent` is now filtered by `train_enrollment_id = CFIELD('train','train_enrollment_id', status='in_progress')`. Matches "that enrollment's own sessions" (**F-G2 closed**).

### action_binding_and_uuids (r2)

Carried forward. The tool module is unchanged, and the `(target_tool, computes)` pairs are unchanged. PASS.

### prerequisite_graph and prerequisite_sentences (r2)

- E1–E4 are unchanged. Every `policy_source` is still verbatim in its blocked rule (sweep: True for each). No new rule sentence states a cross-problem order. The added sentences are the window convention, the diet companion-skip trim and the existing-pet rose tiers; none is an order.
- **New defect R2-N1 (SOURCE-POLICY RED, check 7 on E3).**
  - The new household tier 1 reads the very field the household write sets. The sentence is "if it rose and the latest scheduled shipment charged carried the units per shipment the subscription holds now, the current usage is those units per shipment divided by the subscription's weeks between shipments"; the compute is `F('quantity') / F('frequency_weeks')`.
  - E3's `condition` is "The shared household food Autoship the pet ate from carries the frequency in weeks worked out by the household re-timing rule for the pets that stay on it". Its `effect` is "Once the shared household food Autoship is re-timed for the pets that stay, the gate … is met."
  - After the resolving write the rule, re-evaluated on the written record, no longer gives the written value. The rule has no fixed point, so `resolved_by` cannot make `condition` hold. Demonstrated on task 0's world in 0.md § revision_2.
  - Under the action-form sentence ("has been re-timed") the gate is met once the write is made, so condition and effect reach different conclusions in the same post-write situation.
- Observation R2-O1: on task 0's world, E2's declared condition is literally true at the opening. See 0.md.

### override_declarations (r2)

Re-swept against `autoship_change_rules`, `autoship_agg_multi_holding` and `autoship_enrollment_requirements`. The changed sentences touch only the extended computations (usage bases, caps by plan term, reserve days, trims). None governs a quantity the base fixes. The frequency clamp, quantity caps, Pharmacy days-supply cap and "date the customer chooses" are still followed. No undeclared override. PASS. O-G4 stands (no change claimed).

### factor_ladders (r2)

- packages: 5 factors (4 parameter, 1 method). senior_recheck_cycle tiers: floor to 14-day blocks / **cap at days left in the plan term** / as worked out. The middle tier is a different operation (a record-driven cap), so the factor is no longer a single expression with substituted constants. **F-G3a closed.**
- interval: 6 factors (5 parameter, 1 method). dose_loss_reserve tiers: **subtract lost_reserve_days (floored at 0)** / ×95 % floored / in full. Tiers 1 and 2 are different operations, so **F-G3b closed**. It is borderline (R2-O3): each non-fall-through tier differs from the fall-through only by a constant inside its own operation.
- household: 6 factors (5 parameter, 1 method). usage_measuring_window tiers: **current setting units ÷ weeks** / 6-month history ÷ 26 / 12-month history ÷ 52. Tier 1 is a distinct algorithm, so **F-G3c closed**, but tier 1 is the source of R2-N1.
- diet: 6 factors (5 parameter, 1 method).
  - diet_refill_window has been removed (**F-G5 closed**).
  - The new companion_skip_trim (4 / 2 / 0; companion customer-requested skips in 12 months) is multi-tier and reachable.
  - Observation R2-O2: "Skips on the pet's existing Autoship Pharmacy subscription show stock building up at home" is a statement about medication stock, used to trim prescription-food days. It is weakly grounded, but no tier of it holds of every customer, so it is not struck.
- existing_pet_quantity: 4 factors (3 parameter, 1 method).
  - member_cushion is now an honest parameter (plus_cushion_days 7 / rewards_cushion_days 11 / standard 14).
  - The new method pre_rise_usage_basis has tiers: pre-rise history ÷ 26 / pre-rise units ÷ (count × interval) / 12-month history ÷ 52. The middle tier is a distinct per-interval estimator, so **F-G3d closed**.
  - tenure_trim has been removed (**O-G5 closed**).
  - Observation R2-O4: the fall-through takes the whole subscription's 12-month usage as "the existing pet's usage" even though the scope says the subscription carries food for more than one pet. It is honest as a stated baseline, but generous.
- second_pet: unchanged structure. training_treat_stretch is now scoped to its enrollment.
- All ladders have 3 distinct tiers, and every tier is in the rule and in compute. Every baseline is self-sufficient and equals `baseline.rule`. Per-policy factor and method counts are within bounds.

### findings (r2, charter-global)

- R2-N1 **SOURCE-POLICY RED** (new; introduced by the F-G3c rework): household_interval reads its own output, so E3's condition is not established by its resolving write. Bears on task 0.
- Closed: F-G1, F-G2, F-G3a, F-G3b (borderline, R2-O3), F-G3c, F-G3d, F-G4, F-G5, O-G1, O-G2, O-G3, O-G5.
- Unchanged and still standing: O-G4 and O-G6 (no change claimed; still accurate).
- New observations: R2-O2, R2-O3, R2-O4, R2-O5.
- Correction to R2-N1 (appended pre-reveal): "the rule has no fixed point" is too strong. Iterating the charter compute on task 0's world, with the written frequency fed back each time, gives 4 → **5** → 9 → 26 → 1 → 1 → 1. The only fixed point is 1 week, which is absurd for a 2-bag household food shipment. The gold value 5 is not a fixed point. The finding stands as stated otherwise.

### closing_checklist (r2)

Written 2026-10-06T09:31Z, after the r2 reveals.

**The difficulty is NOT closed.**

| item | r2 status |
|---|---|
| F-G1 | closed |
| F-G2 | closed |
| F-G3a | closed |
| F-G3b | closed (borderline, R2-O3) |
| F-G3c | closed, but introduced R2-N1 |
| F-G3d / T1-1 | closed |
| F-G4 / T0-1 | closed |
| F-G5 / T0-3 | closed |
| T0-2 | closed |
| O-G1, O-G2, O-G3, O-G5 | closed |
| O-G4, O-G6 | unchanged (no change claimed); observations stand |
| T0-O1, T0-O2, T0-O5, T1-O3 | closed |
| T0-O3, T1-O1 | moot |
| T1-O2 | unchanged; observation |
| T0-O4 | not changed (claimed changed; the read set and necessity texts are identical); observation |
| T1-O4 | partially addressed; observation |
| **R2-N1** | **new SOURCE-POLICY RED** (household rule reads its own output; E3's condition is not established by its resolving write); bears on task 0 |
| R2-O1 … R2-O5 | new observations |

Checklist:

- Per-task verdicts: task 0 SOURCE-POLICY RED (R2-N1); task 1 PASS.
- Scopes are disjoint and complete (charter_scope r2 is identical to r1). The tools are closed and the uuid8s are unchanged.
- Trees: n = 3 with 2 value_input edges and n = 1 with 1 value_input edge; user roots; acyclic. PASS.
- Factors: every computation has 4–6 factors with at least 1 honest method and at least 2 parameter; every factor bears weight; all-baseline differs from gold in all 6 computations; multi-source and cross-difficulty are present per task. PASS.
- Gates: the orchestrator's r2 snapshot is all green, with check_traceability deferred. Not re-run by the auditor.

## revision_3

### charter_global_frozen (revision 3)

- Inputs:
  - `autoship.extended.yaml` sha256 **b2690e0985e185a5f8535e9c64db2408e607f18465a1da85570bc8a8901f1353**, changed from bae7d16e…. Re-derived in full.
  - `task_tools.py` 1f6ba94c… is unchanged; the tool-module conclusions are carried forward.
  - The base section is still byte-identical to the blueprint product.
  - Views are unchanged from r2 (8562e5bb… / be84b74c…).
- The round-2 charter file was not retained by this auditor. The r3 charter was therefore diffed against the r1 file (a1da9f70…), and the result compared with the r2 diffs recorded in this session.
  - **Changes since r2:**
    - household_interval rule tier 1, compute (`latest_sched_date`, `household_weekly_units`), its compute_basis and its ladder;
    - diet `prerequisite[0].condition` (E2);
    - the diet rule's consolidation sentence ("counted in days at week_days days a week");
    - the diet rule's skip-trim rationale sentence.
  - packages, interval, existing_pet_quantity and second_pet are textually as in r2.
- Gate snapshot r3: all 7 green, check_traceability deferred.
- Written before any r3 GT was read. Contamination: none.

### re-derived checks (r3)

- **Rule/compute sweep:** every basis is verbatim in its rule; every binding has a basis; every baseline sentence is in its rule; every param is named in its rule. Diet `week_days` is now named ("counted in days at week_days days a week"), so **R2-O5 closed**. Every `policy_source` is verbatim in its blocked rule.
- **household tier 1:**
  - The rule now reads "the current usage is the units that latest scheduled shipment carried divided by the weeks it was booked to cover, which are the days from its charge date to the subscription's next ship date divided by week_days".
  - The compute is `latest_sched_units / (DAYS(latest_sched_date, F('next_ship_date')) / K('week_days'))`. Rule and compute match, and the ladder text matches.
  - The binding no longer reads `frequency_weeks`. `set_shipment_interval_36e38cde` leaves "the already scheduled next ship date … unchanged" (docstring and body). So the rule's inputs are untouched by its own write.
  - Iterating the charter compute on task 0's world with the written value fed back gives 4 → 5 → 5 → 5 → 5. The rule is idempotent and E3's condition holds after its resolving write. **R2-N1 closed.**
  - Observation R3-O1: tier 1 divides by the days to the next ship date, which is undefined if the next ship date is not after the latest charge date. The rule has no guard. It does not arise in either world.
- **E2 condition (check 7):**
  - It now reads "carries the frequency in weeks that the re-timing rule gives once its package count has been re-set under its linked prescription, the re-timing having been made after that re-set; a frequency left from before the re-set does not meet it even where the numbers happen to agree."
  - This agrees with the interval rule's own E1 sentence ("re-timed only after its package count … has been re-set"), so it is grounded and not an independent strengthening.
  - At the opening it is false: no re-timing after a re-set has occurred, and quantity is 3 against the rule's 2.
  - **R2-O1 closed.**
- **Diet skip-trim sentence:** "Skips on the pet's existing Autoship Pharmacy subscription show that pharmacy deliveries for the pet have been arriving while stock remained, so the diet shipment, which joins those deliveries, carries fewer days". The trim is now tied to the joint delivery stream the diet shipment joins, so the grounding is adequate. **R2-O2 closed.**
- **Unchanged since r2 and carried forward:**
  - conflict scan (no new overlap);
  - override sweep (no undeclared override; O-G4 stands);
  - action binding and uuids (PASS);
  - graph acyclic, E1/E3/E4 conditions as in r2;
  - factor_ladders: counts and labels as in r2. usage_measuring_window keeps 3 distinct tiers with a distinct tier-1 algorithm (booked-cover rate).
- **Standing observations:**
  - R2-O3 (borderline dose_loss method) and R2-O4 (generous existing-pet fall-through): no change claimed, none found; they stand.
  - O-G6: stands.

### findings (r3, charter-global)

- No new RED.
- New observation: R3-O1.
- Closed: R2-N1, R2-O1, R2-O2, R2-O5.

### closing_checklist (r3)

Written 2026-10-06T10:00Z, after the r3 reveals.

**The difficulty passes the source-layer audit:** policy self-consistency, problem tree, factors and unique solution all PASS for tasks 0 and 1.

| item | r3 status |
|---|---|
| R2-N1 | closed |
| R2-O1 | closed |
| R2-O2 | closed |
| R2-O5 | closed |
| T0-O4 | closed |
| R2-O3, R2-O4, O-G4, O-G6, T1-O2 | no change; non-blocking observations stand |
| T1-O4 | partially addressed; non-blocking |
| R3-O1 | new non-blocking observation |
| Round-1 items | all closed as recorded in revision_2 |

Checklist:

- Audit files correspond one-to-one with the tasks. Revisions 1–3 are retained untouched, and every r3 comparison carries a PASS.
- The six extended policies are covered. Scopes are disjoint (task 0: packages, interval, household, diet; task 1: existing, second_pet). The tools are closed, and the six uuid8s are independent and unchanged.
- Trees:
  - task 0: n = 3, 2 value_input edges;
  - task 1: n = 1, 1 value_input edge.
  - Both have user-owned roots, and the union graph is acyclic.
- Factors: all six computations have 4–6 factors with at least 1 honest method and at least 2 parameters, baselines are self-sufficient, every factor bears weight, and every all-baseline result differs from gold. Each task has a multi-source factor and a seeded cross-difficulty factor.
- Gates: the orchestrator's r3 snapshot is all 7 green, with check_traceability deferred until the KB is published. The auditor cites the snapshot and did not re-run it.
