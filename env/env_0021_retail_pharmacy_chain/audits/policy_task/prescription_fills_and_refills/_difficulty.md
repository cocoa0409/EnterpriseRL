# Policy-task audit — prescription_fills_and_refills / charter-global

## charter_global_frozen

- Revision: 1 (first audit of this difficulty; no earlier revision exists under this directory).
- Freeze time: 2026-09-24 18:22 UTC. Auditor: erl-task-policy-audit auditor (independent subagent, did not author the artifacts).
- Frozen inputs (sha256, recomputed by the auditor and equal to the coordinator's brief):
  - `env/env_0021_retail_pharmacy_chain/tasks/prescription_fills_and_refills/rx.extended.yaml` = `e80720131078c155053f675ef3567417e9d6161c1f0dde9ce880a127a4bad01d`
  - `env/env_0021_retail_pharmacy_chain/tasks/prescription_fills_and_refills/task_tools.py` = `8d4c13ba2630dfc370cc9e36084a94731863d004ea26a6b303c82d9fff6b6c83`
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/rx.yaml`, the cross-category parameter blocks of `blueprint/products/{coverage,copay,delivery}.yaml`, the extended charter, `task_tools.py`, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (semantics of LATEST/COUNT/CPARAM/XCOUNT/DAYS/MONTHS only).
- Masked and not read when this section was written: every field of `tasks/0.json` and `tasks/1.json` other than the coordinator's masked views (task_index, frozen_time, user_scenario, initial_state). No evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract or prerequisite_closure was read. No earlier audit or instantiation transcript was read.
- This section contains nothing derived from a revealed GT.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred until the KB is published) and the masked views with hashes. Hashes match. Entry conditions are met, except that check_traceability has not run yet. The brief says that is expected at this stage.
- Base copy: lines 1–1507 of the extended charter are byte-identical to `blueprint/products/rx.yaml` (verified with `diff`), so the base section is verbatim.

### policy_conflict_scan

Six extended policies. The charter comments split them between two tasks:

| Policy | Subject | target_tool (owner) | computes | Class / object partition | Claimed by |
| --- | --- | --- | --- | --- | --- |
| rx_ext_strength_error_remake_units | rx_error_remake | dispense_strength_error_remake_b4449648 (agent) | quantity_dispensed | confirmed `wrong_strength` reports | task 0 |
| rx_ext_open_balance_decline_credit | rx_balance_cancelled | decline_owed_balance_20c85924 (user) | refund_usd | Non-Controlled Acute / Maintenance / Specialty | task 0 |
| rx_ext_vacation_override_days | rx_refill | record_vacation_override_refill_9f5a083e (agent) | days_supply_dispensed | fill_reason vacation_override | task 0 (root) |
| rx_ext_theft_replacement_days | rx_refill | record_theft_replacement_refill_fbe8d6a8 (agent) | days_supply_dispensed | fill_reason lost_or_stolen_replacement | task 1 (root) |
| rx_ext_controlled_balance_decline_credit | rx_balance_cancelled | decline_controlled_owed_balance_a6435942 (user) | refund_usd | Schedule V / III-IV / II | task 1 |
| rx_ext_label_error_remake_units | rx_error_remake | dispense_label_error_remake_88d3ae78 (agent) | quantity_dispensed | confirmed `wrong_directions_label` reports | task 1 |

- **Overlapping subjects.** Some policies share a subject, but each pair is split by an attribute the records carry, so no write falls under two of them:
  - rx_refill (vacation vs theft) is split by fill_reason.
  - rx_error_remake (strength vs label) is split by error_type.
  - rx_balance_cancelled (non-controlled vs controlled decline) is split by class. The two class sets are disjoint and together cover all six classes.
- **Shared base clause.** Both decline policies supersede the same base clause of rx_evt_dispensing_error ("a fill that was dispensed correctly is never taken back or refunded …"). Each replacement is limited to its own class set, so the merged clause has one meaning per class.
- **Triggers, eligibility, time anchors.**
  - Remakes are `state_due`. Refills and declines are `on_request`.
  - The two refill policies inherit base eligibility in full ("every condition of rx_evt_early_fill_exceptions, rx_evt_refill_authorization and rx_evt_refill_timing continues to apply").
  - Remake policies declare that they change no condition of rx_evt_dispensing_error.
  - The decline policies anchor on the prescription's most recent owed-balance entry.
  - The remake policies anchor on the most recent confirmed report of their type.
  - No time anchors conflict.
- **Cross-category read boundaries.**
  - coverage: variant parameters vacation_override_per_plan_year, max_days_supply_per_claim and lost_stolen_override_per_plan_year, plus coverage_claims rows.
  - copay: Savings Club status and value_generic_30_day_price_usd.
  - delivery: active plan and mail_transit_business_days.
  - refill: the paused enrollment's pause_until_date.
  - Every read is declared in the policy's `cross_category`, and every read is read-only.
- **Conflicts found.** Two, both detailed under findings:
  - G-2: rx_ext_theft_replacement_days adds cancelled owed units back as days of supply. That conflicts with base rx_evt_partial_fill ("the cancelled units are not re-dispensed"). It also conflicts with the sibling rule rx_ext_controlled_balance_decline_credit, which credits the patient for "units that will now never be dispensed".
  - G-1: rx_ext_vacation_override_days promises a cap that its compute does not implement.
- **Scope exclusivity and completeness.** Per the charter comments, task 0 claims {strength remake, open-balance decline, vacation override} and task 1 claims {theft replacement, controlled decline, label remake}. The two sets are disjoint and together cover all six extended policies. Each task's scope spans its whole problem tree (root plus two prerequisites). The per-task `charter_scope` field is masked and is compared at reveal in each task file.

### rule_compute_equivalence

For every policy, every `compute_basis` quotation was checked programmatically: it appears verbatim in that policy's `rule` (whitespace-normalised). Every `baseline.rule` sentence also appears verbatim in its `rule`. Each quantity was then swept in both directions.

- **rx_ext_strength_error_remake_units.**
  - The answered report is the LATEST confirmed `wrong_strength` report by reported_date.
  - The pickup is the rx_pickup whose source_fill_id is the wrong-strength fill.
  - The three replaced-units tiers match the rule: `>= late_report_days`; `< late_report_days and review gap >= slow_review_days`; otherwise.
  - "Other than the one being answered" is implemented as COUNT − 1. This is exact while the answered report is itself inside the 12-month window. It always is on the task world, because the report is the most recent one.
  - The release, waiting and short-fill ladders match the rule.
  - The final `int()` implements "taken down to a whole number".
  - Result: equivalent.
- **rx_ext_open_balance_decline_credit.**
  - The short fill is the fill named by the LATEST rx_partial_fill.
  - The three undelivered-value methods match the rule, including `-(-d // 30)` for "every started club_block_days days".
  - The handling, recovery, tenure and error ladders match.
  - RND(…, 2) is applied once at the end, with MX(0, undelivered − handling).
  - Result: equivalent.
- **rx_ext_vacation_override_days.** Two gaps:
  1. The rule's sentence "the result never exceeds the class's vacation_override_max_days" has no compute_basis entry and no expression. `result = int(MX(0, ceiling − repeat − MX(0, on_hand − grace) − owed_days) + pause_buffer + transit_buffer)` has no upper bound. This is an empty promise of the rule (finding G-1).
  2. `last_pickup_date = LATEST('rx_fills','event_date', event_type='rx_pickup')` reads the latest pickup of *any* fill on the prescription. The rule reads "when the most recent refill was picked up on a later day than it was dispensed". Compute is broader than the rule, so this is a filter that compute invents (finding G-3).
  - The ceiling, repeat, grace, owed, pause and transit bindings are equivalent to the rule.
- **rx_ext_theft_replacement_days.**
  - The replaced fill is the LATEST rx_refill, and its pickup is scoped to `source_fill_id=replaced_fill`, matching the rule.
  - Restraint counts three fill_reasons within 12 months.
  - The plan bridge is a conjunction of the plan parameter and XCOUNT of paid claims for the prescription.
  - The identity count matches.
  - refills_left = refills_authorized − ΣSUM refills_used + ΣSUM refills_restored.
  - Balance days has three branches.
  - Result: equivalent.
- **rx_ext_controlled_balance_decline_credit.**
  - The whole-week method is `c_pay * 7 * ((owed * DS / Q) // 7) / DS`.
  - The cash and otherwise methods, the hold, repeat and history ladders, and the rounding all match the rule.
  - Result: equivalent.
- **rx_ext_label_error_remake_units.**
  - The held-units tiers `> stale_report_days`, `>= 1` and otherwise match "more than", "one day up to" and otherwise.
  - The report channel ladder, the wait ladder and the collection ladder (caregiver; patient AND drive_thru; otherwise) match.
  - Result: equivalent.
- **Factor ladders in both faces.** Every tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding. No branch of a decides binding is missing from the rule.

### action_binding_and_uuids

- **(target_tool, computes).** The six pairs are pairwise distinct, and each is claimed by exactly one policy.
- **Tool bodies** (`task_tools.py`):
  - Each tool performs one `ctx.create` on rx_fills. Some also perform one `ctx.update` on rx_prescriptions: refills_remaining for the two refills, owed_quantity for the two declines.
  - No function body reads a business condition, raises an error or returns a hint. The tool layer judges no prerequisite and no eligibility.
- **Docstrings.**
  - None names another tool or another policy.
  - None states a position in a sequence relative to another action.
  - Every docstring contains "After the call …", which describes the post-state of the call itself. This is observation O-6.
  - The Args text "as returned by the dispensing-error report lookup / prescription lookup" points at a share finder by description, not by name. This is also noted in O-6.
- **uuid8s.** `b4449648`, `20c85924`, `9f5a083e`, `fbe8d6a8`, `a6435942`, `88d3ae78`: no shared prefix or suffix, no sequence, no adjacent values, none reused. There is no sign of batch derivation.
- **Refill accounting.** Both refill tools hard-code `refills_used=1`. db_schema defines refills_used as "days supply divided by the prescription's days supply, rounded up". The two agree whenever days_supply_dispensed ≤ the written days_supply, which holds on both task worlds. See observation O-2.

### prerequisite_graph

- **Declarations.**
  - The four prerequisite-free policies (both remakes, both declines) declare `prerequisite: []`.
  - rx_ext_vacation_override_days declares two edges: → rx_ext_open_balance_decline_credit (`value_input`, gate `owed_days`) and → rx_ext_strength_error_remake_units (`state_gate`, gate `rx_fills.error_report_id`).
  - rx_ext_theft_replacement_days declares two edges: → rx_ext_controlled_balance_decline_credit (`value_input`, gate `balance_days`) and → rx_ext_label_error_remake_units (`state_gate`, gate `rx_fills.error_report_id`).
- **Targets and shape.** Every `problem` is an extended policy id in this file. None is a base policy and none is a self-reference. The graph is two disjoint stars of depth 1, so it is acyclic.
- **policy_source.** Each of the four edges' `policy_source` is found verbatim in its own policy's `rule` (programmatic check: all four VERBATIM).
- **form.** All four edges are `form: state`, and no `fallback_reason` is present. That is consistent.
- **kind and gate.** `value_input` gates name bindings that exist in the blocked compute: `owed_days` in vacation and `balance_days` in theft. The `state_gate` gates name the ledger field `rx_fills.error_report_id`. No eligibility block exists for them in the extended policies; the gate lives in the rule sentence itself. This is accepted.
- **resolved_by.** Each edge's `resolved_by` equals the depended-on policy's `target_tool`.
- **effect.** Each `effect` is real on the write:
  - The decline writes an rx_balance_cancelled row whose owed_units subtract from the vacation `owed_units` sum and feed the theft `cancelled_units`.
  - The remakes write an rx_error_remake row that carries `error_report_id`.
- **condition.** Each `condition` restates its sentence at the same scope. The vacation owed edge covers "every owed-balance entry on the prescription"; the theft owed edge covers "the owed-balance entry booked for the replaced refill". Neither is strengthened or weakened.
- **Viewpoint.** No authoring-viewpoint wording appears in any prerequisite field.

### prerequisite_sentences

Four-point test per edge:

| Edge | Sentence (own rule) | Connective | State named (no action, no tool, no id) | Scope = condition | Single resolving write |
| --- | --- | --- | --- | --- | --- |
| vacation → open-balance decline | "The vacation override days supply is fixed only after the prescription's fill ledger shows no owed balance still open, every short fill's owed units having been completed or cancelled." | only after | fill ledger shows no owed balance open | yes (all owed entries of the prescription) | The only write tool in this difficulty that settles an owed balance is a decline. Completion has no tool. The two decline tools are split by class, so a Non-Controlled Maintenance prescription gets decline_owed_balance_20c85924 only. |
| vacation → strength remake | "A vacation override refill is not dispensed until each confirmed dispensing-error report on the prescription has a corrected remake booked against it on the fill ledger." | not … until | confirmed report has a remake booked against it | yes | Split by error_type: a wrong_strength report is answered only by rx_ext_strength_error_remake_units ("the most recently reported wrong_strength report"), and a wrong_directions_label report only by the label policy. |
| theft → controlled decline | "The theft replacement days supply is not fixed until the fill it replaces carries no open owed balance, its owed units having been completed or cancelled on the ledger." | not … until | replaced fill carries no open owed balance | yes | For a controlled class, only decline_controlled_owed_balance_a6435942. |
| theft → label remake | "A lost-or-stolen replacement refill is dispensed only after every confirmed mislabeled-directions report on the prescription is matched by a corrected remake on the ledger." | only after | mislabeled-directions report matched by a remake | yes | Only rx_ext_label_error_remake_units answers wrong_directions_label. |

- **No leakage into other text.** No sentence names a tool, a policy id, a snake_case token or a row id. The depended-on rules do not restate any sentence. No rule carries a second wording of any dependency. The docstrings are silent about sequence.
- **Written derivations** (sentence + records + depended-on rule → the one resolving action):
  - (a) Vacation, owed. Read the prescription's rx_partial_fill rows and find one whose fill_id no completion or cancellation names. The rule of the non-controlled decline policy says a declined open balance is cancelled in full and credited. The customer chooses decline, because no completion tool exists. So the only action is decline_owed_balance on that entry.
  - (b) Vacation, remake. Read rx_error_reports with review_outcome confirmed, and find one with no rx_fills row carrying its error_report_id. Its error_type selects the remake policy.
  - (c) Theft, owed. Same as (a), restricted to the owed entry whose source is the replaced refill, and resolved through the controlled decline for a controlled class.
  - (d) Theft, remake. Same as (b), restricted to wrong_directions_label.
- **Observation O-5** (not a red light on these worlds): the vacation gate covers *each* confirmed report of *any* type. The charter has no extended write for a confirmed wrong_drug, wrong_quantity_short or wrong_patient report that lacks a remake. On such a world the hop would lead to no tool. Neither task world holds such a report without a remake.
- **Base sentences with a cross-problem order** (rx_transfer_and_move "not transferred out or moved until that balance is completed or cancelled"; rx_lifecycle_closure "not discontinued until that fill is picked up …"). No task tree in this difficulty rests on them. They are recorded as observations only (O-7).

### override_declarations

Sentence-by-sentence conclusions against each `base_policy_refs` entry.

- **rx_ext_strength_error_remake_units / rx_ext_label_error_remake_units vs rx_evt_dispensing_error** (overwrite: []).
  - The "accepts back only for an error" sentence is not touched.
  - The confirmed-report sentence is followed. Both rules say they change none of its conditions.
  - The short-count and error-report window sentences govern the *return* only (`applies_to: [rx_error_return]`) and are not touched.
  - The refund sentence and the returned-at-most-once sentence are not touched.
  - The remake sentence says the remake "dispenses the correct medication at no charge, consumes no refill, carries a ready_date no later than error_remake_ready_days after the return, and is not subject to the refill-eligible date". It sets no quantity. The extended rules add the quantity without contradicting any base sentence.
  - The goodwill and pending/not_confirmed sentences are not touched.
  - Two observations:
    - O-3: the remake ready_date is anchored on "the return", but neither world records a return and no return tool exists.
    - O-4: the base event meaning of rx_error_remake ("to replace a fill confirmed as a dispensing error") reads naturally as the erroneous fill's own quantity. The extended allowances dispense more units than that without an `overwrite`. The base *policy* sets no quantity, so this is not an undeclared override under the sentence test.
- **rx_ext_open_balance_decline_credit / rx_ext_controlled_balance_decline_credit vs rx_evt_partial_fill and rx_evt_dispensing_error.**
  - The base "never taken back or refunded" clause is superseded and declared in both policies, each narrowed to its own classes. The merged meaning is unique.
  - rx_evt_partial_fill's "at no additional charge, the fill's patient pay already covering the full prescribed quantity" is followed and reused as the credit's rationale.
  - "declined … cancelled for its full owed units" is followed; both tools cancel the full owed_units.
  - "the cancelled units are not re-dispensed" is followed by the declines themselves. The controlled rule says "units that will now never be dispensed".
- **rx_ext_vacation_override_days vs rx_evt_refill_authorization / rx_evt_refill_timing / rx_evt_early_fill_exceptions** (overwrite: []).
  - Status, refill-available and validity are inherited.
  - "refills_used = ceil(days_supply_dispensed / days_supply)" (refill_authorization) and "Every early refill still consumes one refill" (early_fill_exceptions) disagree for an early refill longer than the written days supply. That is a base-internal tension, and the extended rule's "the refill consumes one refill" takes one side of it. It does not bind on the task-0 world (39 ≤ 90). Observation O-2.
  - "with a days supply no larger than vacation_override_max_days" is restated in the extended rule but not implemented in compute (G-1).
  - The refill-timing sentences are inherited.
- **rx_ext_theft_replacement_days vs the same three base policies.**
  - The police-report sentence is superseded and declared: it is broadened to any class for 30+ days. The merged meaning is unique.
  - Everything else is inherited.
  - **Undeclared conflict with a base sentence outside its refs:** the "balance days" tier "when that balance was cancelled, the cancelled units divided by the prescribed daily units are added" re-dispenses, as extra days of supply, the units that rx_evt_partial_fill says "are not re-dispensed". rx_evt_partial_fill is not among its base_policy_refs, and no `overwrite` names that sentence. This is the "anonymous intermediate factor" form (finding G-2). The per-task demonstration is in task 1's file.

### factor_ladders

Structure only. Whether each factor bears weight is judged in each task's `factor_weight`.

| Policy | Factor | effect | decides | Tiers (incl. fall-through) | Multi-source (tiers beyond fall-through combine ≥2 conditions over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| strength remake | replaced_units_basis | method | replaced_units | 3 | no (tier 1 is a single condition) | — |
| | repeat_error_allowance | parameter | repeat_spare_days | 3 | no | — |
| | release_channel_allowance | parameter | release_days | 3 | no (the disjunction is over one field of one record) | — |
| | remake_waiting_allowance | parameter | waiting_days | 3 | no | — |
| | short_fill_allowance | parameter | short_fill_days | 3 | no | — |
| open-balance decline | undelivered_value_method | method | undelivered_value | 3 | yes (fill payment_basis AND copay enrollment) | copay |
| | handling_amount | parameter | handling_kept | 3 | no | — |
| | repeat_short_recovery | parameter | recovery_amount | 3 | no | — |
| | tenure_amount | parameter | tenure_amount | 3 | no | — |
| | short_fill_error_amount | parameter | error_amount | 3 | no | — |
| vacation override | vacation_ceiling | parameter | override_ceiling | 3 | by binding name only: both conditions read variant parameters of the *same* coverage plan record, so not over distinct records | coverage |
| | repeat_override_reduction | parameter | repeat_reduction | 3 | no | — |
| | on_hand_anchor | method | on_hand_days | 3 | no | — |
| | adherence_grace | parameter | grace_days | 3 | no | — |
| | paused_refill_buffer | parameter | pause_buffer | 3 | no | — (reads refill, which no difficulty claims) |
| | delivery_transit_buffer | parameter | transit_buffer | 3 | no | delivery |
| theft replacement | lost_days_anchor | method | lost_days | 3 | no | — |
| | early_refill_restraint | parameter | restraint_days | 3 | no | — |
| | plan_bridge | parameter | plan_bridge | 3 | yes (plan parameter AND coverage_claims count) | coverage |
| | identity_allowance | parameter | identity_days | 3 | no | — |
| | renewal_bridge | parameter | renewal_days | 3 | no | — |
| | balance_days_method | method | balance_days | 3 | no | — |
| controlled decline | controlled_unpaid_method | method | c_unpaid_value | 3 | no (tier 2 "paid in cash" is a single condition) | coverage |
| | controlled_count_hold | parameter | count_hold | 3 | no | — |
| | controlled_repeat_amount | parameter | repeat_amount | 3 | no | — |
| | controlled_history_amount | parameter | history_amount | 3 | no | — |
| label remake | held_units_basis | method | held_units | 3 | no | — |
| | relabel_repeat_allowance | parameter | label_repeat_days | 3 | no | — |
| | relabel_report_allowance | parameter | report_days | 3 | no | — |
| | relabel_waiting_allowance | parameter | wait_days | 3 | no | — |
| | relabel_collection_allowance | parameter | collect_days | 3 | no | — |

- **Declared counts:**
  - strength remake: 5 factors (1 method, 4 parameter).
  - open-balance decline: 5 (1 method, 4 parameter).
  - vacation override: 6 (1 method, 5 parameter).
  - theft replacement: 6 (2 method, 4 parameter).
  - controlled decline: 4 (1 method, 3 parameter).
  - label remake: 5 (1 method, 4 parameter).
- **Structural checks that pass for every factor:**
  - Bindings are disjoint, and `decides` is an input, never `result`.
  - Every ladder has three tiers that are disjoint as stated.
  - Every tier is stated in the rule and implemented in compute.
  - Every `baseline` value equals what the policy's `baseline.rule` states for that input, i.e. the fall-through tier.
- **Label honesty.** The `method` tiers change the algorithm: a different anchor date, a different formula, or a sign change with a different source. The `parameter` tiers select numbers.
  - The waiting allowance of the strength remake selects "that same number of days" (the count itself) on its top tier. That is a variable, not a constant, but it is still a number substituted into the same sum, so the label is acceptable (O-8).
- **Tests that fail at the charter level.** Each failure is listed under findings and demonstrated per task:
  - **G-4 (two tiers select the same method).** In both decline policies, the "paid in cash" tier and the fall-through tier are the same computation. See G-4 for the algebra.
  - **G-5 (conditions no pharmacy weighs for a dispensed quantity).** Several remake and replacement allowances add units of prescription medication for conditions no pharmacy weighs when it sets a dispensed quantity:
    - the channel the erroneous fill was released through;
    - the channel the error was reported through;
    - who collected the fill;
    - how many earlier errors Kestrel made;
    - how many pickups showed photo ID.
  - These are unreal ladders. Counts after striking them are given in G-5.
  - **G-2** also fails the unreal-outcome test: theft's balance-days top tier returns units the patient declined and was credited for.

### findings

**G-1 — SOURCE-POLICY RED (charter-global; bears on task 0). Rule promises a cap that compute does not implement.**
- **Symptom.** rx_ext_vacation_override_days rule: "the result never exceeds the class's vacation_override_max_days". Base rx_evt_early_fill_exceptions: "with a days supply no larger than vacation_override_max_days". But compute `result: "int(MX(0, override_ceiling - repeat_reduction - MX(0, on_hand_days - grace_days) - owed_days) + pause_buffer + transit_buffer)"` has no upper bound, and `compute_basis` quotes neither sentence.
- **Root cause.** The pause and transit buffers are added after the floor with no cap.
- **Evidence.** rx.extended.yaml, rx_ext_vacation_override_days `rule` and `compute.result`.
- **Demonstrated consequence (generic situation).** Take a Non-Controlled Maintenance prescription with no active plan (ceiling = vacation_override_max_days = 90), no earlier override, the most recent refill fully used (on-hand 0), no owed units, a refill enrollment paused ≥ 30 days ahead (+7) and an active Kestrel Mail Delivery plan (+3).
  - Compute gives 100.
  - The rule and the base give at most 90.
  - Those are two conclusions in the same situation.
- **Affected.** Policy rule vs compute of rx_ext_vacation_override_days. Task 0 must show whether this binds on its world.

**G-2 — SOURCE-POLICY RED (charter-global; bears on task 1). Theft "balance days" re-dispenses cancelled owed units, an undeclared override of rx_evt_partial_fill that also contradicts the sibling controlled-decline rule.**
- **Symptom.** rx_ext_theft_replacement_days rule: "when that balance was cancelled, the cancelled units divided by the prescribed daily units are added". Base rx_evt_partial_fill: "for every other class the cancelled units are not re-dispensed and the next fill follows the ordinary refill rules". rx_ext_controlled_balance_decline_credit rule: "the part of it that paid for units that will now never be dispensed is credited". The decline tool docstrings also say: "The cancelled units are never dispensed afterwards."
- **Root cause.** The replacement's days supply converts cancelled units into days and dispenses them. The theft policy's `overwrite` names only the police-report sentence, and its `base_policy_refs` omit rx_evt_partial_fill.
- **Evidence.** The quotations above.
- **Demonstrated consequence.** In task 1's file. Under the base reading, the cancelled units may not be re-dispensed, so the balance-days tier contributes nothing. That changes the scored days supply.
- **Affected.** rx_ext_theft_replacement_days `rule`/`compute.balance_days`/`overwrite`/`base_policy_refs`; task 1's scored days_supply_dispensed.

**G-3 — SOURCE-POLICY RED (charter-global; no consequence on either world). Vacation on-hand anchor reads the latest pickup of any fill, not the pickup of the most recent refill.**
- **Symptom.** The rule says: "counted from the pickup when the most recent refill was picked up on a later day than it was dispensed … when the most recent refill has not been picked up, its whole days_supply_dispensed counts as on hand". Compute says `last_pickup_date: "LATEST('rx_fills', 'event_date', event_type='rx_pickup') or ''"`, with no `source_fill_id` filter. The theft policy uses `source_fill_id=replaced_fill` for the same idea.
- **Demonstrated consequence (generic situation).** The most recent refill is dispensed D and never picked up. A balance completion of an older fill is picked up at D+2.
  - The rule selects "whole days_supply_dispensed counts as on hand".
  - Compute selects "days_supply_dispensed less days from D+2 to today".
  - Those are two different on-hand values.
- **Affected.** rx_ext_vacation_override_days `compute.last_pickup_date`. On task 0's handling-time world, the latest pickup (2026-09-17) is the pickup of the most recent refill, so the gold number does not move. Task 0 confirms this.

**G-4 — SOURCE-FACTOR RED (charter-global; bears on tasks 0 and 1). Both decline-credit method factors write one method as two tiers.**
- **Symptom.**
  - undelivered_value_method tier 2 is `short_pay * (DS - d) / DS` and tier 3 is `short_pay * owed / (units + owed)`.
  - controlled_unpaid_method tier 2 is `c_pay * (DS - d) / DS` and tier 3 is `c_pay * owed / (units + owed)`.
- **Root cause.**
  - db_schema defines `rx_fills.days_supply_dispensed` as "days supply the dispensed quantity lasts at the prescribed directions", so d = u·DS/Q.
  - rx_evt_partial_fill books "the shortfall" as the owed balance of a fill short of the prescribed quantity, so u + o = Q.
  - Then (DS − d)/DS = 1 − u/Q = o/Q = o/(u + o). The two tiers are one computation.
- **Evidence.** Every partial fill seeded on either world gives equal values:
  - Task 0: RF3 gives 7.9933 / 7.9933, and RF2 gives 3.9967 / 3.9967.
  - Task 1: RF4 gives 5.00 / 5.00.
- **Consequence.** Each ladder has only two distinct outcomes, so the factor fails the three-distinct-tier test and cannot be counted. Each decline policy declares exactly one `method` factor, so after striking, each has 0 method factors, below the required 1.
  - For the open-balance decline, that factor is also the only genuine multi-source factor of task 0 (see G-6).
  - Per-task consequences are in the task files.
- **Affected.** rx_ext_open_balance_decline_credit and rx_ext_controlled_balance_decline_credit: `factors`, `rule` (method sentences), `compute`.

**G-5 — SOURCE-FACTOR RED (charter-global; bears on tasks 0 and 1). Allowance tiers that no pharmacy weighs when setting a dispensed quantity.**
- **Symptom.** The following tiers add units of prescription medication, including a Schedule V controlled substance in task 1, according to conditions that no retail pharmacy weighs when it sets how much medication to dispense on a corrective remake or a replacement:
  - strength remake **release_channel_allowance**: +2 days if the wrong fill was released through a locker or delivery, +1 at the drive-thru;
  - strength remake **repeat_error_allowance**: +7 / +3 days for Kestrel's own earlier errors on the prescription;
  - label remake **relabel_report_allowance**: +3 days if the error was reported by chat, +1 by phone;
  - label remake **relabel_collection_allowance**: +2 days if a caregiver collected, +1 at the drive-thru;
  - label remake **relabel_repeat_allowance**: +7 / +3 days for earlier errors;
  - theft replacement **identity_allowance**: +2 / +1 days for how many earlier pickups checked photo ID.
- **Root cause.** The dispensed quantity of a prescription drug is set by the prescription's directions and the patient's clinical need. The channel a fill left the store through, the channel a complaint arrived through, who carried the bag home, the count of earlier Kestrel errors, and the count of ID checks change none of those. Kestrel's own charter already names the only compensation a dispensing error earns: the refund, the remake and the rewards goodwill credit (`error_goodwill_eligible`). The blueprint hands off any further compensation as POLICY_NOT_COVERED: "Requests no charter decides, such as compensation for costs beyond the refund, remake and goodwill a dispensing error earns … are handed off". Extra tablets granted for these conditions are compensation in kind, which no pharmacy publishes.
- **Consequence (counts after striking).**
  - Strength remake: 5 → 3 factors (below 4).
  - Label remake: 5 → 2 factors (below 4).
  - Theft replacement: 6 → 5, or 6 → 4 if balance_days_method is also struck under G-2's unreal-outcome test. It still has ≥ 1 method and ≥ 2 parameter, so it holds.
  - Both remake policies fall below the 4-factor floor.
- **Borderline, observations only (O-1):** the remake waiting allowances; the strength short-fill allowance; the decline tenure/history and recovery amounts. These are retail goodwill-shaped money or bridge amounts, and a plausible business could publish them.
- **Affected.** rx_ext_strength_error_remake_units and rx_ext_label_error_remake_units: `factors`/`rule`/`compute`; rx_ext_theft_replacement_days identity_allowance.

**G-6 — SOURCE-FACTOR observation feeding task 0 (multi-source).** vacation_ceiling passes the gate's multi-source test because it uses two binding names. Both conditions, however, read variant parameters of the same coverage plan record (vacation_override_per_plan_year and max_days_supply_per_claim of one plan). By the audit's definition ("conditions over distinct records"), it is not multi-source. Task 0's only genuine multi-source factor is undelivered_value_method, which G-4 strikes.

**Observations (not grounds for rework on their own):**
- **O-1.** Borderline ladders, listed under G-5.
- **O-2.** Base-internal tension between refills_used = ceil(dsd / DS) and "every early refill still consumes one refill". The extended rules and tools take "one". It does not bind on either world.
- **O-3.** The remake's ready_date is anchored on "the return", which has no tool and is absent from both worlds' ledgers. Earlier remakes in both seeds likewise have no return row.
- **O-4.** The base event meaning of rx_error_remake implies the erroneous fill's quantity. The extended allowances exceed it with no `overwrite`.
- **O-5.** The vacation "each confirmed report" gate has no extended resolving write for confirmed report types other than wrong_strength and wrong_directions_label.
- **O-6.** The docstrings' "After the call …" and "as returned by the … lookup" wording.
- **O-7.** Base cross-problem orders in rx_transfer_and_move and rx_lifecycle_closure ground no edge here.
- **O-8.** The strength waiting allowance's top tier returns the day count itself.
- **O-9.** The remake tools write no `days_supply_dispensed`. Base rx_evt_refill_timing counts rx_error_remake among "most recent dispensed fill", so after a gold remake the base refill-eligible date is computed from a row with no days supply.
- **O-10.** db_schema describes `rx_fills.refund_usd` as a dispensing-error refund. The decline tools write it on rx_balance_cancelled rows.
- **O-11.** `rx_prescriptions.refills_remaining` (and `owed_quantity`) is an authoritative field that equals the ledger-derived quantity the renewal-bridge ladder and the owed-days binding compute. Reading the field or the ledger gives the same tier. It is a record of the quantity, not a stamp naming the tier.

## closing_checklist

Written 2026-09-24 18:27 UTC, after both tasks' frozen derivations and reveals. Everything above this heading was written before any reveal and has not been edited since.

- Per-task files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and `_difficulty.md` sits alongside them. This is revision 1; no older revision exists.
- Scope: `charter_scope` of task 0 is {strength remake, open-balance decline, vacation override} and of task 1 is {label remake, controlled decline, theft replacement}. The two are pairwise disjoint, together cover all six extended policies, and each spans its root and both prerequisites. Each task tool is used by exactly one task, and the uuid8s are independent (see action_binding_and_uuids).
- Problem trees: each has 2 prerequisite problems, 1 value_input edge (at least 1 required), 1 owner=user write, and no cycle. The difficulty-wide graph is acyclic.
- Independent derivation vs GT: every scored value and every factor-sensitivity figure agrees (task 0: 35 / 7.25 / 39; task 1: 26 / 3.25 / 25).
- **The difficulty does NOT close.** Not every task's comparison carries a PASS:

| Task | Policy self-consistency | Problem tree | Factors bear weight | Unique solution | Verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (G-1, G-3 on the claimed vacation policy; no score move on this world) | PASS | SOURCE-FACTOR RED (G-4: decline has 0 method and no multi-source factor survives; G-5: strength remake 3 factors) | PASS | RED |
| 1 | SOURCE-POLICY RED (G-2: theft balance days re-dispense declined units) | PASS | SOURCE-FACTOR RED (G-4: controlled decline 3 factors / 0 method; G-5: label remake 2 factors) | SOURCE-TASK RED (25 vs 15 via G-2) | RED |

- Gate re-run on the final form: not performed. Step 4 runs it only once every task passes, and the auditor does not run gates.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-09-24 18:44 UTC. Auditor: the same independent erl-task-policy-audit auditor. Written before either round-2 task file was opened. The revision-1 text above is untouched.
- Inputs (sha256 recomputed by the auditor):
  - `rx.extended.yaml` = `32e717218edce5e3cd479f03005cd77d36cae40546e31f00169d3be0de63ba59`. This **changed** from r1 `e8072013…`, so every charter-global section is re-derived in full below rather than carried forward.
  - `task_tools.py` = `8d4c13ba2630dfc370cc9e36084a94731863d004ea26a6b303c82d9fff6b6c83`, unchanged.
  - Base section lines 1–1507 are still byte-identical to `blueprint/products/rx.yaml` (`diff` clean).
- Masked: every field of round-2 `tasks/0.json` and `tasks/1.json` beyond the r2 masked views. The reworker's claims (item ids only) were treated as pointers, not evidence.
- Entry conditions: the coordinator's r2 gate snapshot has all seven gates at rc=0 (check_traceability is still deferred). The r2 view hashes match the brief.

### policy_conflict_scan (r2)

- The six extended policies, their subjects, target tools, owners, computes and class/object partitions are as in r1. Task tools are unchanged, and per the charter comments the claims are still task 0 = {strength remake, open-balance decline, vacation override} and task 1 = {theft replacement, controlled decline, label remake}. The scopes are disjoint and complete.
- **Theft tree reshaped.** rx_ext_theft_replacement_days now has:
  - a `value_input` edge to rx_ext_label_error_remake_units (binding `remake_on_hand_days`);
  - a `state_gate` edge to rx_ext_controlled_balance_decline_credit (gate `rx_fills.source_fill_id`).
  - The r1 "balance days" add-back is gone. The rule now states "The replacement never brings back owed units that were cancelled: a cancelled balance stays undispensed."
  - This agrees with base rx_evt_partial_fill ("the cancelled units are not re-dispensed") and with the controlled-decline rule, which now also says "the cancelled units are never dispensed afterwards". **G-2 is closed.**
- **New cross-category reads**, each declared in `cross_category`:
  - open-balance decline → coverage (Commercial Copay Plan);
  - controlled decline → coverage `claim_reversal_deadline_days` and copay Savings Club;
  - strength remake → refill (`pause_until_date`);
  - theft → delivery `controlled_substance_delivery_allowed`.
  - Every parameter read exists in its product charter (verified in coverage.yaml, delivery.yaml and copay.yaml).
- No new conflict between policies was found.
- **Cross-policy observation (O-13):** a remake dispensed the same day counts as "medication the patient holds" in the theft rule but is ignored by the vacation rule, which counts on-hand days "from the most recent refill" only. These are different quantities in different policies, and each rule is explicit, so there is no second reading.

### rule_compute_equivalence (r2)

- **Programmatic checks.** Every compute binding of all six policies has a `compute_basis` entry. Every basis quotation appears verbatim in its own `rule`. Every `baseline.rule` sentence appears in its `rule`. Every factor's `decides` and bindings are compute names.
- **Manual sweep of the rewritten parts:**
  - **Vacation.**
    - `result = MN(P('vacation_override_max_days'), int(…))`, and `compute_basis.result` now quotes "…and the total is held to no more than the class's vacation_override_max_days". In the r1 generic case the result is now min(90, 100) = 90. **G-1 is closed.**
    - `last_pickup_date` now filters `source_fill_id=last_refill_fill`, the most recent refill, which is the rule's "when the most recent refill was picked up". **G-3 is closed.**
  - **Strength remake.** release_channel_allowance and repeat_error_allowance are removed from rule, compute and factors. The new continuity allowance (refills left = authorized − ΣSUM used + ΣSUM restored; ≤ 0 / = 1 / otherwise) and pause allowance (≥ 30 / 1–29 days / otherwise) are equivalent to their rule sentences.
  - **Open-balance decline.** Tier 2 is now "billed to insurance AND active Commercial Copay Plan → pay × 7 × floor(owed × DS / Q / 7) / DS". Compute matches, including the rule's "owed units being turned into days at the prescription's days_supply per quantity_prescribed".
  - **Controlled decline.**
    - Tier 2 is now "discount program AND Savings Club → pay − club price × ceil(d / 30)".
    - The rebill amount (insurance AND days > plan claim_reversal_deadline_days / insurance AND ≤ / otherwise) matches.
    - The count amount (a confirmed report / a pending report with none confirmed / none) matches.
    - The result subtracts both hold and rebill inside MX(0, …), matching "less the controlled count hold and the controlled rebill amount, never below zero".
  - **Theft.**
    - identity_allowance and balance_days are removed.
    - The handover buffer matches: an active plan with controlled delivery allowed = True / an active plan without it / none.
    - The remake offset matches: the LATEST rx_error_remake date ≥ the replaced refill's date → its quantity_dispensed / daily units, subtracted after the buffers, and the whole result never below zero. That is the rule's "plus the plan bridge, the renewal bridge and the handover buffer, less the remake days, the total never below zero".
  - **Label remake.** report/collection/repeat allowances are removed. The continuity and short-fill allowances are added, and both are equivalent to their rule sentences.
- **Result:** equivalent in both directions for all six policies.

### action_binding_and_uuids (r2)

task_tools.py is unchanged (same hash). The r1 conclusions stand verbatim:
- the six (target_tool, computes) pairs are distinct;
- no tool judges a prerequisite;
- the uuid8s are independent.
- O-6 still applies.

### prerequisite_graph (r2)

- **Edges:**
  - vacation → open-balance decline (value_input, owed_days) and vacation → strength remake (state_gate), both unchanged;
  - theft → label remake (value_input, `remake_on_hand_days`, a binding present in the theft compute);
  - theft → controlled decline (state_gate, `rx_fills.source_fill_id`).
- **policy_source.** All four are verbatim in their own rule (programmatic check).
- **Other fields.**
  - All four edges are `form: state` with no fallback_reason.
  - `resolved_by` equals the target_tool of the depended-on policy on every edge.
  - The graph is acyclic.
  - Each `condition` restates its sentence at the same scope.
  - Each `effect` is real: the label remake row dated today becomes "the most recent corrected remake … on or after the replaced refill's dispensing date", and the controlled cancellation names the owed entry of the replaced refill.

### prerequisite_sentences (r2)

| Edge | Sentence | Connective | State named | Single resolving write |
| --- | --- | --- | --- | --- |
| vacation → open-balance decline | unchanged from r1 | only after | no owed balance open | decline_owed_balance_20c85924 (class split; no completion tool) |
| vacation → strength remake | unchanged from r1 | not … until | confirmed report has a remake | strength remake (error_type split) |
| theft → label remake | "The theft replacement days supply is fixed only after every confirmed mislabeled-directions report on the prescription is matched by a corrected remake on the ledger." | only after | mislabeled-directions report matched by a remake | only rx_ext_label_error_remake_units answers wrong_directions_label |
| theft → controlled decline | "A lost-or-stolen replacement refill is not dispensed until the fill it replaces carries no open owed balance, its owed units having been completed or cancelled on the ledger." | not … until | replaced fill carries no open owed balance | for a controlled class, only decline_controlled_owed_balance_a6435942 |

- None of the four sentences names a tool, a policy id or a row id.
- The theft rule's other sentences about the remake offset and the "never brings back" clause state the value, not a second wording of the order.
- **Derivations:**
  - theft/label: confirmed wrong_directions_label report with no rx_fills.error_report_id → label remake;
  - theft/decline: the replaced refill's rx_partial_fill is named by no completion or cancellation → controlled decline, with the customer choosing decline.
- **Observations that still apply:** O-5 (vacation gate over all report types) and O-7.

### override_declarations (r2)

- **Remakes vs rx_evt_dispensing_error.** No sentence is overridden, and the r1 conclusion holds. O-3 and O-4 still apply.
- **Declines.**
  - The "never refunded" clause is superseded and declared, per class. The merged meaning is unique.
  - Both rules follow rx_evt_partial_fill's "cancelled for its full owed units" and "not re-dispensed".
  - New controlled rebill amount: this is a kept fee within the credit, and no base sentence governs it. **O-14:** the parameter it borrows, coverage `claim_reversal_deadline_days`, is defined for "an unpicked paid claim", while the short fill was picked up. No second reading of the credit follows.
- **Vacation.** As in r1, but the cap now matches base early_fill_exceptions' "no larger than vacation_override_max_days". O-2 still applies.
- **Theft.**
  - The police-report override is declared.
  - The remake-offset and handover sentences contradict no base sentence.
  - The r1 undeclared override of rx_evt_partial_fill (G-2) is removed.
- **O-12 (new):** both decline rules describe the Commercial Copay Plan as one "whose flat copay is reset by whole weeks of therapy". The coverage charter states no such property (no "week" appears in coverage.yaml). This is a rationale clause and does not change the formula.

### factor_ladders (r2)

| Policy | Factors (effect) | Count | Multi-source factors (distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- |
| strength remake | replaced_units_basis (m), remake_waiting_allowance (p), short_fill_allowance (p), strength_continuity_allowance (p), strength_pause_allowance (p) | 5 (1 m / 4 p) | none | none (pause reads refill, which no difficulty claims) |
| open-balance decline | undelivered_value_method (m), handling_amount, repeat_short_recovery, tenure_amount, short_fill_error_amount (p) | 5 (1 / 4) | undelivered_value_method: tier 1 fill payment_basis AND copay enrollment; tier 2 fill payment_basis AND coverage plan | copay (plus a coverage read) |
| vacation override | unchanged from r1 | 6 (1 / 5) | none genuine (G-6 remains a fact about this policy, but is now moot for task 0) | coverage, delivery |
| theft replacement | lost_days_anchor (m), early_refill_restraint, plan_bridge, renewal_bridge, handover_buffer (p) | 5 (1 / 4) | plan_bridge (plan parameter AND coverage_claims count) | coverage, delivery |
| controlled decline | controlled_unpaid_method (m), controlled_count_hold, controlled_rebill_amount, controlled_repeat_amount, controlled_history_amount, controlled_count_amount (p) | 6 (1 / 5) | controlled_unpaid_method (fill AND coverage plan / fill AND copay enrollment); controlled_rebill_amount (fill payment_basis AND coverage deadline) | coverage (plus a copay read) |
| label remake | held_units_basis (m), relabel_waiting_allowance, relabel_continuity_allowance, relabel_short_fill_allowance (p) | 4 (1 / 3) | none | none |

- **Structural checks that pass for every factor:**
  - Every ladder has 3 tiers, disjoint as stated.
  - Each is stated in its rule and implemented in compute.
  - Bindings are disjoint and `decides` is an input.
  - Each `baseline` equals the `baseline.rule` value.
  - Labels are honest: the method tiers change the formula, the parameter tiers select numbers.
- **G-4 re-tested: closed.** No two tiers of any ladder select the same value or method.
  - Non-controlled: club, whole-week floor and unit proportion are three different computations. The whole-week tier equals the proportion only when the owed days are a multiple of 7. That is a coincidence of value, not one method written twice. On task 0's short fill they give 7.46 vs 7.99.
  - Controlled: whole-week, club and proportion likewise.
- **G-5 re-tested: closed.** The six struck allowances (release channel, strength repeat, report channel, collection, label repeat, identity) are gone. Newly added:
  - The **continuity allowances** (bridge days when one or no refill is left) and the **controlled rebill fee** are treatments a pharmacy publishes.
  - The **strength pause allowance** (a paused auto-refill adds days to a remake) and the **theft handover buffer** (holding a delivery plan adds days although the replacement is collected at the counter) are the same shape as the vacation pause/transit buffers accepted in r1. They are recorded as borderline observations **O-1** (extended), not struck. The label short-fill allowance is treated the same way, consistent with r1's treatment of the strength short-fill allowance.
- **Counts that survive** (nothing struck): strength 5, decline 5, vacation 6, theft 5, controlled 6, label 4. Each has ≥ 2 parameter and ≥ 1 method.
- **The label remake sits exactly at the floor of 4.** It depends on O-1 staying an observation.

### findings (r2)

- **Status of r1 findings:**
  - G-1: closed (see rule_compute_equivalence r2).
  - G-2: closed.
  - G-3: closed.
  - G-4: closed.
  - G-5: closed.
  - G-6: moot. Task 0 now has a genuine multi-source factor in undelivered_value_method.
- **No new SOURCE-POLICY or SOURCE-FACTOR red light** at the charter level.
- **New observations:**
  - O-12: the Commercial Copay Plan "flat copay reset by whole weeks" clause is not in the coverage charter.
  - O-13: a same-day remake is treated differently by the theft rule and the vacation rule.
  - O-14: the rebill amount borrows `claim_reversal_deadline_days`, which the coverage charter defines for unpicked claims.
  - O-1 extended: the strength pause allowance, the theft handover buffer and the label short-fill allowance are borderline, with the label remake at the 4-factor floor.
- **Carried forward unchanged:** O-2 to O-11 (O-9 still applies: the remake tools write no days_supply_dispensed).

### closing_checklist (revision 2)

Written 2026-09-24 18:45 UTC, after both r2 derivations were frozen and revealed. The revision_2 charter-global sections above were written before the reveals.

- **Files.** `0.md` and `1.md` map one-to-one onto `tasks/0.json` and `tasks/1.json`, and each now carries a `## revision_2` section. The r1 text is preserved unedited.
- **Scope.** The r2 `charter_scope` sets are disjoint and together cover all 6 extended policies. Each task tool is used once. The uuid8s are independent, with task_tools.py unchanged.
- **Trees.** Each has 2 prerequisite problems, 1 value_input edge (floor 1), 1 owner=user write (the decline), and no cycle. The difficulty-wide graph (two disjoint stars) is acyclic.
- **Factors.** Every computation has a self-sufficient baseline, 4–6 factors with at least 2 parameter and 1 method, 3-tier ladders stated in the rule, distinct tier outcomes, and every factor bearing weight. Each whole baseline gives a definite number different from gold: task 0 gives 30 / 7.99 / 69 vs 38 / 7.25 / 39; task 1 gives 50 / 5.00 / 0 vs 14 / 4.50 / 8.
  - Multi-source: task 0 has undelivered_value_method; task 1 has plan_bridge and the controlled unpaid and rebill factors.
  - Cross-difficulty: task 0 reads copay, coverage and delivery; task 1 reads coverage and delivery.
- **Blind derivation vs GT.** Every scored value and every factor-sensitivity figure agrees for both tasks.

| Task | Policy self-consistency | Problem tree | Factors bear weight | Unique solution | r2 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

- **Round-1 REDs, verified closed:** G-1, G-2, G-3, G-4, G-5 and G-6. No new SOURCE-* defect. No regression.
- **Open observations** (not grounds for rework):
  - O-1 (r2), borderline ladders. The label remake is at the 4-factor floor.
  - O-2 to O-11, carried forward.
  - O-12 to O-14, new in r2.
- **Gate re-run on the final form.** The coordinator's r2 snapshot has all seven instantiation gates at rc=0. check_traceability remains deferred until the KB is published. The auditor did not run gates.
- **The difficulty passes the source-layer policy-task audit at revision 2.**
