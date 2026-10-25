# Policy-task audit — appraisal_orders_and_fees / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent auditor, not the instantiator). Freeze time: 2026-10-13T05:50Z (wall clock).
- Frozen inputs (sha256, re-verified against the brief before reading):
  - `tasks/appraisal_orders_and_fees/appraisal.extended.yaml` 6cd61f63ff423d0fa881604c7ae30eb07be8ebcabada183242293db806849d00
  - `tasks/appraisal_orders_and_fees/task_tools.py` cb95da021d5b5a0478a1399f54e32e62f20d71bae9131fed9d8222a67c08af8a
  - `.audit_views/policy_task/appraisal_orders_and_fees/0.view.json` 560c4518bafce87c7893b00c94dbd002e194be110a49436616aa3db6f6d14f82
  - `.audit_views/policy_task/appraisal_orders_and_fees/1.view.json` cf56ce50a081067b3198d849c7c2503b27b381327e1c58659a579c712257fd81
- Fields read: `blueprint/blueprint.yaml`, `blueprint/products/appraisal.yaml`, `blueprint/db_schema.json` (field meanings), `blueprint/share_tools.py` (lookup/verify tools), the extended charter, `task_tools.py`, and from each masked view only `frozen_time`, `user_scenario`, `initial_state`. The DSL semantics of `DAYS`, `MONTHS`, `within_months`, `SUM/COUNT` (scoped to the holding), `CFIELD` and `XCOUNT` (scoped to the customer) were read from `skills/erl-task-instantiate/scripts/check_compute.py`.
- Masked and not read until every per-task derivation was on disk: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), both worklogs, any other difficulty's tasks or audits, any other scenario.
- Entry conditions (Step 0): the brief supplied the masked views with hashes and a gate snapshot. All gates are green except `check_traceability`. The brief says it fails only on `unlock_*_discoverable_tool:tool_name` (task-tool names have no published KB source before rendering), with 0 non-unlock misses. I accept that as a known pre-render state; it is not a defect of these artifacts.
- Base copy: `appraisal.extended.yaml` minus `extended_policies` parses equal, key by key (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies), to `blueprint/products/appraisal.yaml`. The base copy is verbatim compatible.

### policy_conflict_scan

The four extended policies: A `appraisal_ext_size_value_addon` (agent, `book_size_value_addon_5d867e2e`, gla_surcharge line), U `appraisal_ext_update_inspection_charge` (user, `pay_update_inspection_charge_fc307ba0`, reinspection line), R `appraisal_ext_late_rush_refund` (agent, `refund_late_rush_charge_6e5bda3a`, rush line refund), I `appraisal_ext_final_inspection_charge` (user, `pay_final_inspection_charge_e30bacb7`, reinspection line).

- **Subjects and lines.** A and R each write a line no other policy writes. U and I both write `appraisal_fee_charged` on the `reinspection_fee` line.
- **U/I domain overlap.** U fires when "the report's age … to the closing date currently scheduled on the loan file, is above the report type's validity days and no more than its maximum age with an update". I fires on "an order whose value is subject to completion or repairs". An order can meet both. U's visit-scope rule prices the intersection explicitly: "an order whose value is subject to completion and which carries no reinspection charge yet is updated and certified complete in one combined visit, charged the standard update charge plus 60 percent of the report type's reinspection fee". It also prices the case where a recent reinspection charge stands ("recertified from that recent visit at a flat 175 dollars"). I has no sentence that defers to U, or that excludes an order also due an update. No sentence states which policy governs a visit that is both an update and a completion. This is recorded as observation O-1 (see findings). The intersection in which "no reinspection charge yet" holds is closed by U's explicit "one combined visit" wording. The intersection in which a reinspection charge already stands is not closed by any sentence: U gives a flat 175 recertification, I gives trip-fee-based pricing.
- **Triggers and eligibility.** Every fee write inherits base `appraisal_fee_schedule.after_itp_only` (loan file status in processing … clear_to_close). No extended policy weakens it. Refund dedup `charge_not_refunded` is inherited by R.
- **Time anchors.**
  - U ages the report to `loan_files.estimated_closing_date`. That is declared in its overwrite (base said "note date").
  - R counts days late from `due_date` to an endpoint chosen by its counting rule.
  - I's late-original share counts `due_date`→`completed_date`, which equals base `appraisal_turn_time`'s "appraisal delay".
  - R and I therefore use two different lateness measures on the same order. Each is stated in its own rule, and neither quantity is the other's (observation O-2).
- **Cross-category read boundaries.** The `cross_category` declarations match compute:
  - A reads loan.
  - U reads loan and lock (CFIELD lock status=locked).
  - R reads loan, plus the lock history via XCOUNT over `lock_pricing_events`.
  - I reads funding (closings status=scheduled), loan and credit (variant Builder Partner Credit).
- **Scopes of the two tasks.** From the masked views alone (pre-reveal):
  - Task 0's world triggers A (GLA 5180 > 4000) and U (age 170 > 120). I is also triggered (subject_to_completion true; see O-1). R is not triggered (no rush).
  - Task 1's world triggers R (rush paid, completed after due) and I (subject_to_completion true). U is not triggered (age 44 ≤ 180) and A is not triggered (GLA 2240 ≤ 4000).
  - The coordinator's `check_extended` and `check_cross_fire` report the declared scopes as disjoint and jointly covering the 4 policies. The comparison with the declared `charter_scope` is done per task after the reveal.

### rule_compute_equivalence

Every compute binding of A, U, R and I has a `compute_basis` quotation that is a verbatim sentence or clause of that policy's `rule` (checked by substring). Sweeping back, each rule tier appears as a branch of its `decides` binding, and each branch is a rule tier. The gaps found are below. None moves a value on either task world; they are recorded as observations.

- A, `addon_owed`: the rule says the add-on "is owed once on an order …". Compute does not subtract any gla_surcharge charge already on the order, so the "once" is not implemented in compute and rests on the base dedup idea only. No consequence on task 0 (no gla line at the opening). Observation O-3.
- A, `arrival_adjusted`: implemented exactly as the rule states. The ladder is non-monotone in lateness: when the non-living-area parts sum below 100, "subtotal less 100" (1–2 days late) is lower than "living-area part alone" (3+ days late). Recorded under factor_ladders.
- U, `reconsideration_component`: the rule says "an order whose decisions all left the value unchanged adds 40 dollars". Compute tests `rov_unchanged_count >= 1` and ignores `returned_incomplete` decisions. An order holding {returned_incomplete, value_unchanged} gets 40 in compute; the rule's "all … unchanged" can be read either way. No consequence on task 0 (one value_unchanged decision only). Observation O-4.
- R, `lock_extensions`: the rule says "the rate lock on that file carries at least one extension entry". Compute uses `XCOUNT('lock','lock_pricing_events', event_type='lock_extension_booked')`, which counts across every lock the customer holds; the `cross_category.note` even says "of the same customer". Compute is broader than the rule. No consequence on task 1 (one lock, on that file). Observation O-5.
- R, `value_change_date`: the rule says "the decided date of that decision". Compute takes the LATEST value_changed decision. Two value_changed decisions are possible only where `rov_max_per_order` = 2 (Jumbo form). No consequence on task 1 (no reconsideration). Observation O-5.
- R, `refund_owed`: the rule's opening sentence is "nothing is refunded when the report arrived on or before its due date", and the baseline sentence is phrased on `completed_date`. Compute gates on `days_late > 0` with the endpoint picked by the counting rule (delivered date, or the value-change decision date). On an order completed on time but delivered more than 2 days later, compute refunds while "arrived" read as "completed" refunds nothing. No consequence on task 1 (completed 1 day late, so both readings owe a refund). Observation O-6.
- I, `signing_date`: the rule says "counts calendar days from today to its signing date". Compute reads `closings.scheduled_closing_date` (schema: "date the signing is scheduled"). The schema also has `closings.signing_date` ("date the borrower signed the note (consummation); empty until then"). The ladder text "signs 0 to 5 calendar days from today" and the schema meaning resolve the reading to the scheduled date, but the word collision is real. Observation O-7, with the per-task value in 1.md.
- Rounding and caps: `RND(…,2)` matches "kept to the cent". R's `MN(100, MX(0, …))` matches "never more than 100 percent and never less than zero". I's `MX(0, …)` matches "never going below zero". The 50%-of-rush figures are rounded at the binding, which is consistent with the cents rule.

### action_binding_and_uuids

- `(target_tool, computes)`:
  - A: (book_size_value_addon_5d867e2e, addon_amount)
  - U: (pay_update_inspection_charge_fc307ba0, charge_amount)
  - R: (refund_late_rush_charge_6e5bda3a, refund_amount)
  - I: (pay_final_inspection_charge_e30bacb7, charge_amount)
- Each pair is claimed by exactly one policy.
- Owners: A and R are `owner="agent"`, U and I are `owner="user"`. Each tool writes exactly one ledger row on its own line and updates `fee_balance`.
- No function body checks eligibility, ordering, or any prerequisite. The module docstring says so, and the bodies confirm it: no `find` on loan files, locks or ledger state other than reading the order's `fee_balance`/`customer_id`, and no conditional refusal.
- No docstring names another tool or carries a sequencing word. "after this entry / payment / the refund" appears only in the Returns description of `fee_balance`.
- uuid8s are 5d867e2e, fc307ba0, 6e5bda3a, e30bacb7. They share no prefix or suffix, show no sequential or adjacent pattern, and are not reused.
- PASS.

### prerequisite_graph

- Every policy fills `prerequisite`: A `[]`, R `[]`, U and I one edge each.
- Edge U→A:
  - kind `value_input`, gate `billed_addon` (an existing U binding), form `state`, no `fallback_reason` (correct for state form).
  - `policy_source` is verbatim in U's rule.
  - `resolved_by` is book_size_value_addon_5d867e2e, which is A's target_tool. Its effect (one gla_surcharge charge row) is exactly what U's `billed_addon` sums.
  - `condition` ("gross-living-area surcharge charge equal to the complexity add-on the completed report and the loan file call for") is at the same strength as the sentence ("carries the complexity add-on owed for the living area, site, market value, loan program and occupancy that the completed report and the loan file show").
- Edge I→R:
  - kind `value_input`, gate `rush_miss_refunds` (an existing I binding), form `state`.
  - `policy_source` is verbatim in I's rule.
  - `resolved_by` is refund_late_rush_charge_6e5bda3a, which is R's target_tool. That tool stamps `refund_reason=rush_deadline_missed` on a rush_fee refund, which is exactly what I's `rush_miss_refunds` counts.
  - `condition` matches the sentence ("the refund owed on any rush charge whose promised delivery date was missed").
- The graph has two disjoint edges (U→A, I→R) and is acyclic. No edge points at a base policy or at itself. No authoring-viewpoint words ("in this task", "at the opening") appear in any `prerequisite` field.
- PASS.

### prerequisite_sentences

- **U → A.** "The update visit charge is not fixed until the order's fee history carries the complexity add-on owed for the living area, site, market value, loan program and occupancy that the completed report and the loan file show."
  - Four-point test:
    1. The connective "not … until" ties U's own result to a waited-on state.
    2. The waited-on state is record-visible: the order's fee history carrying the add-on. The sentence names no performer, tool or action verb.
    3. It contains no tool name, policy id, snake_case token or row id.
    4. Its strength equals `condition`.
  - Exactly one write of this difficulty puts a charge on the gla_surcharge line: book_size_value_addon_5d867e2e. The other three tools write only the reinspection or rush lines.
  - Derivation: the sentence says the fee history must carry "the complexity add-on". A's rule says "It is booked as one charge on the order's gross-living-area surcharge line". So the reader concludes that A's write must stand, at A's computed amount, before U's figure is fixed. Single reading.
  - A's rule does not restate the sentence. U's rule has no second wording of it.
- **I → R.** "The final inspection charge is fixed only after the order's fee history shows the refund owed on any rush charge whose promised delivery date was missed."
  - Four-point test:
    1. The connective is "only after".
    2. The state is record-visible: the fee history showing the refund.
    3. It contains no tool name, id or snake_case token.
    4. "any rush charge" is stated open, which matches the condition's scope.
  - The only write of this difficulty that books a rush-line refund is refund_late_rush_charge_6e5bda3a.
  - R's rule supplies "A late-rush refund is owed on an order whose borrower paid a rush charge and whose report arrived after its due date … It names the rush charge entry it returns". Single reading.
  - R's rule does not restate the sentence.
- **Undeclared cross-problem orders in rules.** None in the extended rules. The base rule `appraisal_agg_orders_per_file` states "ordered as new_order_after_expiration only after the expired order is cancelled". No task tree rests on it; observation O-8.
- PASS.

### override_declarations

Base sentences, judged sentence by sentence against each `base_policy_refs` entry:

**A** (refs: fee_schedule, validity_and_update, hpml_flip)

- fee_schedule:
  - after-ITP state gate: followed.
  - "gla_surcharge is charged once when gross_living_area_sqft is above gla_surcharge_threshold_sqft": declared superseded.
  - "acreage_surcharge once when site_acres is above acreage_surcharge_threshold_acres": followed. The A site part is a separate quantity.
  - "there is no stacking or discount between components, each is charged at its own amount": declared superseded.
  - "Nothing is charged … for an HPML flip second appraisal": not named. A's rule would charge the add-on on any order whose completed report states a GLA above threshold, including a `second_appraisal_hpml_flip` order. This is a latent undeclared override, but no task world has an HPML flip order, so it moves no scored value. Observation O-9.
- validity_and_update: A does not touch it.

**U** (refs: fee_schedule, validity_and_update, hpml_flip)

- validity:
  - "Between validity_days and max_age_with_update_days … charged reinspection_fee": declared superseded. The replacement also moves the age anchor to the scheduled closing date.
  - "max_age_with_update_days is 0 cannot be updated": followed.
  - "Past max … new order": followed.
- fee_schedule:
  - "reinspection_fee is charged once for each Form 1004D completion or update inspection": declared superseded.
  - "Nothing is charged for a reconsideration of value (rov_fee)", together with the base `appraisal_reconsideration_of_value` sentence "The borrower is never charged (rov_fee)": **not named.** U's reconsideration part adds 40 or 80 dollars to the borrower's update charge solely because the order carries a decided reconsideration. This is the "anonymous intermediate factor" form: the quantity is a fee to the borrower that arises from exercising a reconsideration, which base says is never charged. **Finding F-1 (SOURCE-POLICY + SOURCE-FACTOR).** The consequence is demonstrated in 0.md.
  - "there is no stacking or discount between components": A's overwrite supersedes this sentence charter-wide; its replacement speaks only of the add-on. U's billed-add-on part (stacking keyed on another component) relies on that removal without naming the sentence itself. Observation O-10.

**R** (refs: fee_refund, turn_time)

- fee_refund:
  - "When the order was delivered later than its due_date after the borrower paid for rush, the rush_fee is refunded in full (rush_deadline_missed)": declared superseded.
  - Stage refunds, the ITP refund, the HPML refund, dedup, original payment method, and naming the charge entry: followed.
- turn_time:
  - "the number of calendar days between due_date and completed_date is the appraisal delay that other Larkspur policies rely on": R does not name it. R defines its own "days late" with an explicit counting rule.
  - The base sentence defines a named quantity ("the appraisal delay"). The base rush-refund sentence that R replaced used the delivered date, not the appraisal delay. So R's days late is not the quantity that sentence governs. Observation O-2 (the alternative value is shown in 1.md for completeness).

**I** (refs: fee_schedule, validity_and_update, hpml_flip)

- validity:
  - "A value subject to completion … charged reinspection_fee": declared superseded.
- fee_schedule:
  - The reinspection sentence: declared superseded. U also supersedes it; see O-1.
  - The trip_fee sentence: followed. I uses the trip-fee amount as a visit-base value on the reinspection line, not as a trip charge.
  - "no stacking or discount between components": see O-10. The outlay courtesy is a discount keyed on the other components' standing charges.

### factor_ladders

Per policy: factors (effect, decides). Every factor's bindings are disjoint from the other factors' bindings, every `decides` is an input to the result rather than `result` itself, every ladder has 3 tiers including the fall-through, every tier is stated in the `rule` and implemented in `compute`, every fall-through equals the factor's `baseline`, and no two tiers of one ladder select the same value or method.

**A**: 6 factors (5 parameter, 1 method).

| factor | effect | multi-source? | cross_difficulty |
| --- | --- | --- | --- |
| living_area_overage_tier | parameter | no (both conditions on the order row) | — |
| market_value_tier | parameter | no | loan |
| loan_program_tier | parameter | no | loan |
| occupancy_tier | parameter | no | loan |
| site_acreage_tier | parameter | **yes** (order site_acres ∧ loan property_type) | loan |
| arrival_lateness_method | method | no | — |

- Labels: arrival_lateness_method's tiers switch which parts compose the add-on (living-area part alone / subtotal minus a flat amount / subtotal). That counts as method.
- Realism:
  - Value, program, occupancy and acreage complexity add-ons are recognisable AMC or lender pricing.
  - living_area_overage_tier conditions part of the tier on "how many calendar days the appraiser took from the inspection date to the completed date". That is the appraiser's own turnaround, so the borrower pays more when the appraiser is slower. This sits uneasily with base `appraisal_turn_time` ("Delays by the appraiser … never move due_date"). It is borderline as a condition a lender weighs; it is not struck because it can be read as an effort proxy. Observation O-11.
  - arrival_lateness_method is non-monotone (see rule_compute_equivalence). The ladder is not unreal on task 0's world, where the subtotal minus 100 (575) is above the living-area part (350). Observation O-12.

**U**: 6 factors (5 parameter, 1 method).

| factor | effect | multi-source? | cross_difficulty |
| --- | --- | --- | --- |
| note_date_age_tier | parameter | no | loan |
| billed_addon_class | parameter | no | — |
| lock_horizon_tier | parameter | no | lock |
| reconsideration_outcome_tier | parameter | no | — |
| loan_amount_tier | parameter | no | loan |
| visit_scope_method | method | partial (tier 1: order flag ∧ ledger; tier 2: ledger only) | — |

- Realism: **reconsideration_outcome_tier is struck as unreal (F-1).** It charges the borrower 40 or 80 dollars on a 1004D update because the borrower exercised a reconsideration of value. The charter itself says "The borrower is never charged (rov_fee) and Larkspur never asks the appraiser to hit a target value" and "Nothing is charged for a reconsideration of value (rov_fee)". No US mortgage lender publishes a surcharge keyed on a borrower's ROV; it is the kind of ROV deterrent the ECOA valuation framework the charter cites in `appraisal_delivery` is meant to prevent.
- With that factor struck, U still has 5 factors (4 parameter, 1 method), which is within bounds. The defect is the unreal ladder itself, not the count.

**R**: 4 factors (3 parameter, 1 method).

| factor | effect | multi-source? | cross_difficulty |
| --- | --- | --- | --- |
| lateness_share_tier | parameter | no | — |
| days_late_endpoint | method | partial (tier 1 reconsiderations; tier 2 order dates) | — |
| closing_slip_points | parameter | **yes** (loan dates ∧ lock pricing events) | lock |
| access_trip_deduction | parameter | no | — |

- Realism: the access deduction reduces the refund for borrower-side access failures even though base turn_time already moves `due_date` for borrower access delays. That double-counts the same access delay against the borrower. The deduction is plausible as stated, so this is an observation (O-13).

**I**: 6 factors (5 parameter, 1 method).

| factor | effect | multi-source? | cross_difficulty |
| --- | --- | --- | --- |
| revisit_base_method | method | no | — |
| signing_turn_tier | parameter | no | funding |
| government_program_tier | parameter | no | loan |
| standing_outlay_tier | parameter | no | — |
| partner_builder_tier | parameter | no | credit |
| late_original_share | parameter | **yes** (ledger rush refund ∧ order dates) | — |

- Labels: revisit_base_method's tiers select trip fee / reinspection fee + trip fee / reinspection fee. That is a composition of schedule amounts rather than a different algorithm, so the `method` label is borderline. It is acceptable because the tier changes what the visit is billed as (return trip vs fresh visit). Observation O-14.

**Per-task totals (structure only; weight is in each task file):**

- A + U (task 0's expected pair): multi-source = site_acreage_tier. Cross-difficulty = loan (A, U) and lock (U).
- R + I (task 1's expected pair): multi-source = closing_slip_points and late_original_share. Cross-difficulty = lock (R), funding (I), loan (I) and credit (I).

### findings

- **F-1 — SOURCE-POLICY RED + SOURCE-FACTOR RED (bears on task 0, the only task whose tree includes U).**
  - Symptom: U's reconsideration part charges the borrower +40 dollars (unchanged) or +80 dollars (changed) on the update visit because the order had a decided reconsideration of value.
  - Root cause: an undeclared override, in disguised anonymous-intermediate form, of the base sentences "Nothing is charged for a reconsideration of value (rov_fee)" (`appraisal_fee_schedule`) and "The borrower is never charged (rov_fee)" (`appraisal_reconsideration_of_value`). U's `overwrite` names neither. The ladder's condition and outcome are a treatment no lender would publish.
  - Evidence: U rule "The reconsideration part of the update visit charge reads the reconsideration decisions recorded on the order: an order with a decision that changed the value adds 80 dollars, an order whose decisions all left the value unchanged adds 40 dollars"; compute `reconsideration_component`; factor `reconsideration_outcome_tier`.
  - Affected: `appraisal.extended.yaml` → `extended_policies[appraisal_ext_update_inspection_charge]` rule, compute `reconsideration_component`, `factors[reconsideration_outcome_tier]`, `overwrite`.
  - Consequence demonstrated in 0.md.
- **Observations** (no scored value moved on either world, or the second reading is excluded by explicit text): O-1 through O-14 above.
  - O-1: U/I domain overlap with no precedence sentence.
  - O-2: R's days late differs from turn_time's appraisal delay.
  - O-3: A's "owed once" is not in compute.
  - O-4: returned_incomplete is ignored in U's reconsideration part.
  - O-5: R's lock-extension count is customer-scoped, and its value-change date takes the latest decision.
  - O-6: R's "arrived" versus the endpoint-based gate.
  - O-7: I's "signing date" versus the `closings.signing_date` column.
  - O-8: a base cross-problem order sentence (agg_orders_per_file).
  - O-9: A on HPML flip orders.
  - O-10: the no-stacking sentence is superseded once and relied on by U and I.
  - O-11: the appraiser-turnaround condition in A's living-area tier.
  - O-12: A's arrival ladder is non-monotone.
  - O-13: R's access deduction double-counts access delays.
  - O-14: the revisit_base_method label.

## closing_checklist

Written after both reveals (2026-10-13T06:00Z). Nothing above this heading was edited after a reveal.

- **Difficulty status: NOT CLOSED.** Task 0 is SOURCE-POLICY RED + SOURCE-FACTOR RED (F-1); task 1 is PASS. Step 4 requires all four relationships to pass on every task.
- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and this file sits alongside them. This is the first audit round, so there are no older revisions.
- Coverage and scopes:
  - task 0 `charter_scope` = {appraisal_ext_size_value_addon, appraisal_ext_update_inspection_charge}
  - task 1 `charter_scope` = {appraisal_ext_late_rush_refund, appraisal_ext_final_inspection_charge}
  - The two scopes are pairwise disjoint, each covers its whole problem tree, and together they cover all 4 extended policies.
  - Each task tool has an independent uuid8 (see `#action_binding_and_uuids`).
- Problem trees: each has 1 prerequisite problem, 1 value_input edge and one `owner=user` root write. The difficulty-wide graph is {U→A, I→R}, which is acyclic with no cross-task references.
- Factors:
  - Every computation has 4–6 factors with at least 2 parameter and at least 1 method.
  - Every factor bears weight on its own task's world, with honest baselines.
  - Every full baseline differs from gold: A 250 vs 575, U 250 vs 820, R 150 vs 105, I 200 vs 90.
  - Each task has at least one multi-source factor and at least one cross-difficulty factor.
  - The exception is F-1: `reconsideration_outcome_tier` is struck as an unreal ladder and an undeclared override. Without it, U still has 5 factors.
- Gates: I did not re-run them (an auditor does not run gates). The coordinator's snapshot in the brief is green except `check_traceability`, which fails only on the pre-render unlock tool names. Gates must be re-run on whatever final form follows the resolution of F-1.

## revision_2

### charter_global_frozen (round 2)

- **Auditor and freeze.** Same independent auditor as round 1. Frozen at 2026-10-13T09:16Z (wall clock).
- **Input hashes.** All re-verified before reading:
  - `appraisal.extended.yaml` 87f9ca3bc69068addb282c4a04c35def2e5c99a73bbf4ff2d9fba8722a401364. **Changed** from round 1, so every charter-global section below is re-derived in full.
  - `task_tools.py` cb95da021d5b5a0478a1399f54e32e62f20d71bae9131fed9d8222a67c08af8a. Unchanged, so round 1 `#action_binding_and_uuids` is carried forward by reference for the tool half.
  - Views: 0.view.json ac79f0b8…9105, 1.view.json ecd873dc…bf66.
- **Read and masked.** Same permitted and masked fields as round 1. The reworker's closure claims were received by item id only and are not treated as evidence. Nothing below derives from a round-2 reveal.
- **Base copy.** The base section still parses equal, key by key, to `blueprint/products/appraisal.yaml`.
- **Verbatim checks** (scripted substring test):
  - every `compute_basis` value is inside its policy's `rule`;
  - every `overwrite.superseded_clause` is inside the named base rule;
  - every `overwrite.replaced_by` is inside the extended `rule`;
  - every `baseline.rule` sentence is inside the `rule`;
  - both `policy_source` sentences are inside their blocked rules.
  - **All pass.**

### policy_conflict_scan (round 2)

- **U and I overlap (O-1): closed.**
  - I now says: "An order whose report is older than the report type's validity days at the closing date currently scheduled on the loan file is outside this rule: a report that can still be updated is certified complete in the combined update visit, and an older report is replaced by a new order." Compute matches: `completion_charged_here` requires `report_age_at_close <= validity_days`.
  - U's visit-scope tier 1 now covers every subject-to-completion order: "an order whose value is subject to completion is updated and certified complete in one combined visit".
  - Result: past validity, U charges the combined visit and I charges 0. Within validity, U charges 0 and I charges. Past the update limit, both charge 0 and base "new order" governs.
  - No order now has two prices.
- **HPML flip orders.** All four policies now exclude them, consistent with base "Nothing is charged … for an HPML flip second appraisal" and base refund rule "any charge on an HPML flip second appraisal is refunded in full".
- **R's pre-ITP and cancelled-order carve-outs.** These defer to base `appraisal_fee_refund`, as its own sentences require.
- **Scopes.** By trigger facts in the two worlds (pre-reveal):
  - Task 0 triggers A (5180 per unit > 4000) and U (age 170). I is excluded (170 > 120), R is excluded (no rush).
  - Task 1 triggers R (rush paid, days late 5 by the counting rule) and I (completion, age 44 ≤ 180). U is excluded (44 ≤ 180), A is excluded (2280 ≤ 4000).
  - Disjoint, and jointly cover the 4 policies.

### rule_compute_equivalence (round 2)

Swept both ways for all four policies. Round-1 gaps:

| item | round-2 state | status |
| --- | --- | --- |
| O-3 (A "owed once") | Rule: "Any amount already standing on the order's gross-living-area surcharge line is taken off the complexity add-on, the result never going below zero". Compute `already_billed` / `MX(0, …)`. Replaying A after its own write gives 0.00. | closed |
| O-4 (U returned_incomplete) | The reconsideration part is removed. | moot |
| O-5 (R lock scope, latest decision) | `lock_id=file_lock_id` scopes the read to the file's lock. Rule now says "the decided date of the latest such decision". | closed |
| O-6 (R "arrived") | Rule now gates on "whose days late are one or more", counted under its own counting rule, and compute gates the same way. | closed |
| O-7 (I signing date) | Rule now says "counts calendar days from today to its scheduled closing date". | closed |
| O-12 (A non-monotone arrival rule) | "never less than the living-area part" (`MX(size_component, …)`). | closed |

New gap:

- **O-R2-3** (observation): R's rule says extension costs "less any waiver of them". Compute subtracts every `lock_cost_waived` cost_amount on the lock, including waivers of relock or float-down fees. Compute is broader than the rule. No consequence on task 1, where the lock has no waiver rows.

### action_binding_and_uuids (round 2)

- **Tool half.** Carried forward from round 1 by hash: `task_tools.py` is unchanged.
- **Charter half.** `(target_tool, computes)` pairs are unchanged and each is claimed once. PASS.

### prerequisite_graph and prerequisite_sentences (round 2)

- **Edges unchanged.** U→A (value_input, `billed_addon`, state) and I→R (value_input, `rush_miss_refunds`, state). Both `policy_source` sentences are verbatim and their `condition`, `resolved_by` and `kind` are unchanged.
- **Resolving writes still unique.**
  - A's rule still says "It is booked as one charge on the order's gross-living-area surcharge line".
  - R's rule still names the rush charge entry it returns.
- **No new cross-problem orders.**
  - The new I sentence about the combined update visit is a scope boundary between U and I, not an ordering of writes.
  - R's "because the fee refund policy returns it in full" points at a base policy and states no order.
- The graph is acyclic. **PASS.**

### override_declarations (round 2)

**F-1 (U reconsideration surcharge): closed.**
- The reconsideration part is gone from U's rule, compute and factors. No extended policy now charges the borrower anything keyed on a reconsideration of value.
- The only remaining read of reconsiderations is R's counting rule. It moves the late-rush **refund** to the borrower and never adds a charge, so base "The borrower is never charged (rov_fee)" is respected.

**O-10 (stacking supersession): closed.** The base "no stacking or discount" sentence is now named by A, U and I, each with its own order-of-work sentence as replacement.

**O-2 (turn-time appraisal delay): closed by declaration.**
- R now names `appraisal_turn_time` "the number of calendar days between due_date and completed_date is the appraisal delay that other Larkspur policies rely on." and replaces it with its counting rule.
- **New O-R2-2** (observation): the superseded sentence is a scenario-wide definition, and its replacement is a refund-specific counting rule.
  - Within this difficulty no extended rule relies on "the appraisal delay": A's arrival rule and I's late-original share both state "completed … after its due date" explicitly.
  - The lock charter (`blueprint/products/lock.yaml` ~l.956) states its own arithmetic ("completed_date minus due_date in calendar days"), so its numbers do not depend on the appraisal definition.
  - No scored value moves. Recorded so the renderer keeps the base turn-time definition legible.

**New O-R2-1** (observation): U and I each name base `appraisal_fee_schedule` "rush_fee is charged once when the borrower asks for rush and rush_available is true." as superseded, with **different** replacement sentences (U's lock-horizon part, I's closing-turn part).
- Neither replacement restates when a rush fee is charged on a rush request. Read as a text replacement, the merged charter would lose the base rule that charges rush on request.
- Neither U nor I books a rush-line charge; they add an amount equal to the rush fee on the reinspection line. So the declared conflict is broader than the actual one.
- No scored value in either task depends on the base rush-charging sentence: task 1's rush charge is seeded history.

**Other base sentences.** Re-checked sentence by sentence against each `base_policy_refs` entry:
- A: new per-unit living-area test is declared in the replaced gla sentence; HPML exclusion follows base.
- U: new market-conditions part touches no base sentence.
- R: new extension-cost points touch no base sentence; ITP, cancelled and HPML carve-outs follow base.
- I: re-visit netting is covered by the declared reinspection replacement.
- No undeclared override found.

**O-9 (A on HPML flip orders): closed.** "An order placed as an HPML flip second appraisal is never charged the complexity add-on."

**O-8: unchanged.** It sits in a base rule; observation only.

### factor_ladders (round 2)

**A**: 6 factors (5 parameter, 1 method).
- `living_area_overage_tier` now reads per-unit area: stated GLA ÷ loan-file `units`. It is a single condition on a derived quantity, so not multi-source.
- `site_acreage_tier` stays multi-source (order site ∧ loan property type).
- O-11 (appraiser turnaround condition): closed; the condition is removed.
- The per-unit reading is a recognisable way to treat 2–4 unit properties.
- Realism of all tiers: acceptable.

**U**: 6 factors (5 parameter, 1 method).
- `reconsideration_outcome_tier` is replaced by `value_cushion_tier` (parameter, cross-difficulty loan).
  - Ladder: appraised value over loan-file property value < 1% (or not above) → 100 ("full market-conditions refresh"); 1 to < 3% → 50; otherwise 0.
  - Realism: a 1004D update must state whether value has declined since the effective date. Where the original value barely covers the price, that market-conditions analysis carries the loan, so a heavier refresh is a credible scope-based price.
  - Every refinance lands on tier 1, because there property_value is the appraised value. That holds for a class of customers, not for every customer who reaches the write. Accepted.
- `visit_scope_method`:
  - tier 1: completion flag only;
  - tier 2: not-completion ∧ recent reinspection charge, multi-source across order and ledger.

**R**: 4 factors (3 parameter, 1 method).
- `access_trip_deduction` is replaced by `extension_cost_points` (parameter, cross-difficulty lock). O-13 is closed by removal.
- `closing_slip_points` now reads slip days on the loan file only. It is no longer multi-source; it is cross-difficulty loan.
- Lateness shares are now 25 / 50 / 100.
- No multi-source factor remains in R. Task 1's multi-source floor rests on I's `late_original_share` (ledger refund ∧ order dates).

**I**: 6 factors (5 parameter, 1 method).
- `revisit_base_method` tier 1 is now a netting rule floored at the trip fee. That is an algorithm change, so the `method` label holds. O-14 is closed.

**Structural checks.** Every ladder:
- has 3 disjoint tiers;
- has a fall-through equal to its baseline;
- is stated in the rule and implemented in compute;
- has no two tiers sharing a value or method.

**Totals per expected pair.**
- Task 0 (A+U): multi-source = `site_acreage_tier`; cross-difficulty factors on loan and lock.
- Task 1 (R+I): multi-source = `late_original_share`; cross-difficulty factors on loan, lock, funding and credit.

### findings (round 2)

No charter-global RED. F-1 is closed.

Observations:
- **O-R2-1:** the base rush sentence is superseded twice, by different replacements, and neither restates rush-on-request.
- **O-R2-2:** the turn-time "appraisal delay" definition is superseded by a refund-specific counting rule.
- **O-R2-3:** R's waiver subtraction is broader than its rule.
- **O-8:** carried.

Round-1 observations O-1 to O-7, O-9 to O-14 are closed or moot as itemised above.

### closing_checklist (round 2)

Written after both round-2 reveals. Nothing above this heading in revision_2 was edited after a reveal.

**Difficulty status: CLOSED for the source-layer audit.** Task 0 PASS, task 1 PASS.

- **Files:** `0.md` and `1.md` each carry round 1 untouched plus `## revision_2`, matching the two tasks one to one.
- **Scopes:**
  - task 0 = {size_value_addon, update_inspection_charge}
  - task 1 = {late_rush_refund, final_inspection_charge}
  - The two are disjoint and cover all 4 policies. The task-tool uuid8s are independent and unchanged.
- **Problem trees:**
  - Each tree has 1 prerequisite problem, 1 value_input edge and a root that is a user-owned write.
  - The difficulty graph {U→A, I→R} is acyclic, with no cross-task cycle.
- **Factors:**
  - Every computation has 4–6 factors, with at least 2 parameter and at least 1 method.
  - Every ladder has 3 tiers, the rule states each tier in full, and the fall-through tier equals the honest baseline.
  - Every factor bears weight on its task world.
  - Full baselines (A 250, U 250, R 150, I 200) all differ from gold (575, 880, 120, 90).
  - Multi-source per task: site_acreage_tier (task 0), late_original_share (task 1). Every task also has cross-difficulty factors.
- **Round-1 findings:**
  - F-1 is closed.
  - O-1 through O-7 and O-9 through O-14 are closed or moot; O-T0-1 is closed.
  - O-8 stands (it is in a base policy).
- **Open observations:** O-R2-1, O-R2-2, O-R2-3 and O-T1-R2-1. None of them is a RED.
- **Gates:** the coordinator's round-2 snapshot is green except `check_traceability`, whose 4 misses are all pre-render `unlock_*_discoverable_tool:tool_name` entries. That gate must be re-run after the KB is rendered.

## revision_3

### charter_global_frozen (round 3)

- **When and who.** Same independent auditor, frozen 2026-10-13. This is a gated chain link, so I ran the coordinator's scripts myself, read-only.
- **Gate snapshot.** I ran `/tmp/erl0059_coord/gates.sh appraisal_orders_and_fees --trace` from the repo root. The output was captured to scratch and shown to me with numeric argument values masked, so no gold figure could enter context. Status lines:
  - `EXTENDED OK`, `TASK TOOL CONTRACT OK`
  - `replay_tasks --check`: 0.json 10 acts, det/nonvac True, closure 5=5; 1.json 14 acts, closure 14=14. `REPLAY OK`.
  - `SOLVABILITY OK`
  - `COMPUTE OK` (suite depth history_rows_max=8(>= 8), branches_max=42(>= 5))
  - `GROUNDING OK`, `SCOPE OK`
  - `check_traceability`: 0.json copied 15, missing 0; 1.json copied 19, missing 0. **`TRACEABILITY OK`.**
  - Every gate is green, so this is not RED-INPUT.
- **Views.** Rebuilt with `.venv/bin/python /tmp/erl0059_coord/mkviews.py appraisal_orders_and_fees`:
  - `0.view.json` sha256=ac79f0b81c5427eec929f4edb8197ef971a401c4cc23a570a80713ce39ed9105 (identical to round 2)
  - `1.view.json` sha256=ecd873dc5e13b754846043ca983782cde0cfa6a796fde3bb47308816d6c0bf66 (identical to round 2)
  - `task_tools.py` sha256=cb95da021d5b5a0478a1399f54e32e62f20d71bae9131fed9d8222a67c08af8a (unchanged)
  - `appraisal.extended.yaml` sha256=5fca2f1fb9b42f8edd28830b2695d3b04485c1fd5ead9da56924ba51a45751ff (**changed**, so the charter-global sections are re-derived in full)
- **Base copy.** Still parses equal, key by key, to the blueprint product.
- **Verbatim checks** (scripted substring tests), all pass:
  - every `compute_basis` value is in its rule;
  - every `superseded_clause` is in its base rule;
  - every `replaced_by` is in its extended rule;
  - every `baseline.rule` sentence is in its rule;
  - every ladder has 3 tiers.
- **Inputs read.** `audits/render_source/appraisal_orders_and_fees/render_appraisal_r1.md`, as the coordinator directed. It contains no task value.

### compute changes (round 3)

Diffing each policy's compute against round 2 shows the compute is unchanged in all four policies. Round 3 rewrites only rule text, `overwrite` entries and `cross_category` notes. My recomputation on the unchanged views therefore reproduces round 2 exactly:

| task | figures |
| --- | --- |
| 0 | A 575.00, U 880.00, opening-world U 760.00 |
| 1 | R 120.00, I 90.00, opening-world I 120.00 |

Every factor sensitivity and every full baseline is also identical to round 2.

### render-report items (render_appraisal_r1.md): closure check

1. **Rush sentence retired by U and I: closed.**
   - Neither U's nor I's `overwrite` names "rush_fee is charged once when the borrower asks for rush and rush_available is true." any more. U has 3 entries and I has 3, none of them on the rush sentence.
   - Both rules now say the premium "is not a rush charge on the order, which is still charged only when the borrower asks for rush at order".
   - That keeps the base sentence in force and consistent. This also closes my O-R2-1.
2. **U `overwrite[0]` dropped "by the original appraiser … keeps it usable": closed.**
   - The replacement now opens "A Form 1004D update by the original appraiser keeps the report usable, and its update visit is charged under this rule, when …".
   - It adds "a report past its maximum age with an update is replaced by a new order", which matches base validity sentence 4.
3. **I `overwrite[0]` dropped "before funding": closed.**
   - The replacement opens "A value subject to completion or repairs needs a Form 1004D completion inspection before funding; that completion visit is charged under this rule when …".
4. **R retired the turn-time appraisal-delay definition: closed.**
   - The `appraisal_turn_time` entry is removed from R's `overwrite`.
   - R's rule now says "The days late of the late-rush refund are this refund's own count; the appraisal delay, the calendar days from the due date to the completed date that other Larkspur rules rely on, is unchanged."
   - That is consistent with the base, so no declaration is needed. This also closes my O-R2-2.
5. **R waivers, rule vs compute: closed.**
   - The rule now says "less every lock-cost waiver booked on that lock", which matches the compute's `XSUM(... event_type='lock_cost_waived', lock_id=file_lock_id)`. This also closes my O-R2-3.
   - Residual wording (observation O-R3-2): the netted quantity is still named "extension costs … less every lock-cost waiver", so a waiver of a relock or float-down fee nets against extension costs. Rule and compute now agree. Task 1's lock has no waiver row.
6. **I re-visit "standing" vs counted charges: closed.**
   - The rule now reads "when the order's fee history carries reinspection charges dated within the last 2 calendar months … carries only older reinspection charges … carries no reinspection charge". That matches compute's COUNT and SUM of `appraisal_fee_charged` rows.
7. **A overage band wording: closed.**
   - The rule now reads "an overage of at least 500 but under 1,500 square feet is 1.4 times … an overage under 500 square feet is the surcharge itself", which matches compute `>= 500`, `< 1500`.

### six-kind sweep over the whole charter (round 3)

- **(a) Rule vs compute: rounding, floors, caps.**
  - A: `RND(…,2)` matches "kept to the cent"; the `MX(size_component, …)` floor and the `MX(0, … − already_billed)` floor are both stated.
  - U: `RND(rush × 50%)` and `RND(result)`.
  - R: `MN(100, MX(0, …))` matches "never more than 100 percent and never less than zero".
  - I: `MX(0, …)`, the trip-fee floor `MX(P('trip_fee'), …)`, and `RND`.
  - All match the rule text.
- **(b) compute_basis quotes are verbatim.** Scripted check passes.
- **(c) replaced_by completeness and scope.**
  - Each `replaced_by` now carries every clause of its superseded sentence that is still in force:
    - gla line and "charged once": A;
    - original appraiser / keeps usable: U;
    - before funding: I;
    - reinspection "once": U and I, with the residual "any other Form 1004D inspection is still charged the report type's reinspection fee once";
    - no-stacking: A, U and I each keep "every other appraisal charge is still charged at its own amount with no stacking or discount".
  - The three no-stacking replacements and the two reinspection replacements are mutually consistent; each assigns its own charge and names the others.
  - **Observation O-R3-1.** A's no-stacking replacement says the add-on "is reduced only by its arrival rule". A's rule also says "Any amount already standing on the order's gross-living-area surcharge line is taken off the complexity add-on". Read literally these two collide.
    - On a world with a standing gla charge, the first reading gives the full add-on and the second gives the netted amount.
    - The netting sentence is the specific one: "so the add-on is collected only once". Neither task world has a gla charge standing when A is evaluated (task 0's `already_billed` = 0.00; A does not fire on task 1).
    - No scored value moves, so this is an observation.
- **(d) Overwrites that retire nothing, or retire a clause they do not conflict with: none remain.** Every remaining entry retires a sentence the extended rule actually departs from:
  - A: the gla trigger becomes per-unit, and the amount becomes composed.
  - A/U/I: stacking.
  - U: the age anchor becomes the scheduled closing.
  - U/I: the reinspection amount.
  - I: the completion visit split by age.
  - R: rush refund in full becomes a share.
- **(e) Undeclared base departures: none found.**
  - R's own day count is declared non-conflicting.
  - The U/I turn-time premiums are declared not to be rush charges.
  - U's market-conditions part, R's extension points and I's partner reduction touch no base sentence.
  - The HPML exclusions follow base.
  - Base validity sentence 1 (age to the note date) is compatible with the scheduled-closing anchor.
- **(f) Docstring effects vs body, and gold in docstrings.**
  - The tool module is unchanged. Bodies write exactly the effects their docstrings state (line, sign, `fee_balance` delta, `refund_reason`).
  - No docstring carries a numeric example or any gold figure; the only digits are format descriptions.
  - **Observation O-R3-3** (present since round 1; I missed it then). Every `amount` Arg says "it is stored rounded half-up to 2 decimal places", but each body uses Python `round(float(x), 2)`. That is round-half-even on binary floats; for example 0.125 is stored as 0.12, not 0.13.
    - No consequence on these tasks: every gold amount is an exact cent figure (575.00, 880.00, 120.00, 90.00).

### earlier closures: no regression

- **F-1 stays closed.** No extended rule charges anything keyed on a reconsideration.
- **O-1 stays closed.** I is limited to reports inside validity; U's combined visit covers the rest; both replacements state this split.
- O-3, O-5, O-6, O-7, O-9, O-10, O-11, O-12, O-13, O-14 and O-T0-1 stay closed. Each was rechecked against the round-3 text; none was reopened.
- O-R2-1, O-R2-2 and O-R2-3 are now closed (items 1, 4 and 5 above).
- O-8 is unchanged (base).
- O-T1-R2-1 is a fact about the world: the decision-date and delivered-date endpoints share the 50% tier. It is unchanged.

### prerequisite graph, sentences, factor_ladders (round 3)

- Both `policy_source` sentences are verbatim and unchanged.
- A's rule still names the gross-living-area surcharge line ("charged once, on the order's gross-living-area surcharge line"), so the U→A hop resolves to one write.
- R still names the rush entry it refunds.
- The graph is unchanged and acyclic.
- Factor structure is unchanged from revision_2: A 6, U 6, R 4, I 6, each with at least 2 parameter and at least 1 method.
  - Task 0 multi-source factor: `site_acreage_tier`.
  - Task 1 multi-source factor: `late_original_share`.
- No ladder text changed except the band wording in item 7.

### findings (round 3)

- No RED.
- New observations: O-R3-1 (A "reduced only by its arrival rule" vs its netting sentence), O-R3-2 (waiver netting is named as extension cost), O-R3-3 (docstring "half-up" vs `round()` in the body).

### closing_checklist (round 3)

Written after both round-3 reveals. I did not edit anything above this heading after a reveal.

- **Status:** the difficulty stays CLOSED for the source-layer audit.
- **Render items:** all 7 in `render_appraisal_r1.md` are closed in the source.
- **Gates:** all gates are green, including `TRACEABILITY OK`, which now passes against the published `docs/appraisal/`.
- **Views:** unchanged from round 2.
- **Compute:** unchanged.
- **Scored values:** unchanged (575 / 880 / 120 / 90), each uniquely entailed.
- **Scopes, trees and factors:** as in revision_2.
- **Open observations (none is RED):** O-R3-1, O-R3-2, O-R3-3, O-T1-R2-1 and O-8.

**task0=PASS  task1=PASS**

## revision_4

### charter_global_frozen (round 4)

- Same independent auditor. Gated chain link: I ran the coordinator scripts myself, read-only.
- Inputs read: `audits/render_source/appraisal_orders_and_fees/render_appraisal_r2.md`. It carries no task value.

**Gate snapshot.** `/tmp/erl0059_coord/gates.sh appraisal_orders_and_fees --trace`, run from the repository root. Numeric argument values were masked in what I viewed.

| gate | result |
| --- | --- |
| EXTENDED | OK |
| TASK TOOL CONTRACT | OK |
| `replay_tasks --check` | 0.json 10 acts, True/True, closure 5=5; 1.json 14 acts, closure 14=14; REPLAY OK |
| SOLVABILITY | OK |
| COMPUTE | OK (history_rows_max=8(>= 8), branches_max=42(>= 5)) |
| GROUNDING | OK |
| SCOPE | OK |
| TRACEABILITY | OK (0.json copied 15, missing 0; 1.json copied 19, missing 0) |

All gates are green, so this is not RED-INPUT.

**Views and hashes.** Rebuilt with `mkviews.py`:

| file | sha256 | change |
| --- | --- | --- |
| `0.view.json` | ac79f0b81c5427eec929f4edb8197ef971a401c4cc23a570a80713ce39ed9105 | unchanged since round 2 |
| `1.view.json` | ecd873dc5e13b754846043ca983782cde0cfa6a796fde3bb47308816d6c0bf66 | unchanged since round 2 |
| `task_tools.py` | 9377a01348f71ea5414670e61f1b5bf8953acf53e62b3705d094d15ece2070bf | changed |
| `appraisal.extended.yaml` | 7f9ca88c5988f606979a73b03c95c177cc7f02ee9098ad3b6fcba13a82971bbd | changed |

**What changed versus round 3.** I diffed each policy's rule, compute and `overwrite` programmatically against my round-3 dump of the same file:

- **A (`appraisal_ext_size_value_addon`):** one rule sentence changed, together with the matching no-stacking `replaced_by`. Compute is unchanged.
- **R (`appraisal_ext_late_rush_refund`):** one rule sentence changed (extension-cost points), with matching `compute_basis`, ladder text and `cross_category` note. Compute is unchanged.
- **U and I:** rule, compute and `overwrite` are all unchanged.
- **`task_tools.py`:** the four `amount` Arg docstrings changed. Bodies, signatures and uuid8s are unchanged.

**Checks.**
- The base copy still equals the blueprint product.
- Every `compute_basis` quote, `superseded_clause`, `replaced_by`, `baseline.rule` sentence and `policy_source` passes the verbatim check.

### round-3 observations (also render_appraisal_r2 items): closure

**O-R3-1 / render item 1 (A contradicts itself): closed.**
- A's sentence, and its no-stacking `replaced_by`, now reads: "The complexity add-on is built from the parts below, in place of the report type's gross-living-area surcharge alone, and is reduced by two things only, its arrival rule and any amount already standing on its own line; …".
- That agrees with the netting sentence "Any amount already standing on the order's gross-living-area surcharge line is taken off the complexity add-on, the result never going below zero".
- It also agrees with compute: `MX(0, arrival_adjusted − already_billed)`.
- The two statements are now one reading.

**O-R3-2 (waiver netting named as extension cost): closed.**
- R now defines the quantity as "the lock costs the borrower still bears there, that is the extension costs booked to the borrower on that lock less every lock-cost waiver booked on that lock". The tiers read "lock costs still borne of 500 dollars or more … more than zero and under 500 … nothing still borne".
- Name, definition and compute (`XSUM(extension, borrower) − XSUM(lock_cost_waived)` on the file's lock) now coincide.
- The ladder text and the `cross_category` note carry the same definition.

**O-R3-3 / render item 2 (docstring "half-up" vs body `round()`): closed.**
- All four Args now say "it is stored rounded to 2 decimal places". The bodies keep `round(float(x), 2)`.
- The docstrings no longer claim a rounding mode the body does not implement, so docstring and body agree.
- No docstring carries a numeric example or a gold figure.

### six-kind sweep (round 4)

| kind | finding |
| --- | --- |
| (a) rounding / floors | Unchanged from revision_3. Compute is identical. The two changed rule sentences add no rounding or floor that compute lacks; A's "reduced by two things only" names exactly the two floors-and-reductions compute applies. |
| (b) `compute_basis` verbatim | Pass, scripted check. R's `borrower_extension_cost` basis quotes the new sentence. |
| (c) `replaced_by` completeness and scope | A's no-stacking replacement still keeps "every other appraisal charge is still charged at its own amount with no stacking or discount". It stays consistent with the U and I replacements, which are unchanged and name the add-on as stacking "its own parts under its own rules". |
| (d) overwrites retiring nothing or non-conflicting clauses | None. The `overwrite` lists are unchanged apart from A's replacement text. |
| (e) undeclared base departures | None. The two changed sentences touch no base sentence. |
| (f) docstring vs body | Agree (O-R3-3 above). Effects, line, sign, `fee_balance` delta and `refund_reason` are as in revision_3. |

### regression and unique entailment

- **Recomputation.** Compute is unchanged and both views are unchanged. My recomputation on the round-4 charter reproduces revision_3 exactly:
  - Task 0: A 575.00 and U 880.00 (opening-world U 760.00), every factor sensitivity, and both full baselines (250 and 250).
  - Task 1: R 120.00 and I 90.00 (opening-world I 120.00), every factor sensitivity, and both full baselines (150 and 200).
  - The non-firing policies stay at 0.00 in both worlds.
- **Earlier closures.** All still hold: F-1, O-1 through O-14 except O-8, O-T0-1, and O-R2-1 through O-R2-3.
- **Unchanged structure.** Prerequisite edges, sentences, factor structure and scopes are as in revision_2 and revision_3.

### findings (round 4)

- No RED and no new observation.
- Still open: O-8 (a base sentence) and O-T1-R2-1 (task 1's two endpoint tiers share the 50% share). Neither is a defect demanding rework.

### closing_checklist (round 4)

Written after both round-4 reveals. Nothing above this heading was edited after the reveal.

- **Difficulty status:** remains CLOSED for the source-layer audit.
- **Gates:** all green, including TRACEABILITY OK.
- **Earlier findings:**
  - O-R3-1, O-R3-2 and O-R3-3 are closed. Render report r2's two items are closed with them.
  - The rule wording and the tool docstrings now agree with compute and with the tool bodies.
  - No earlier closure regressed.
- **Scored values:** unchanged (575 / 880 / 120 / 90). I recomputed each and found it uniquely entailed. Each matches gold figure for figure.
- **Open observations:** only O-8 (in a base policy) and O-T1-R2-1 (a fact about task 1's world). Neither is RED.

**task0=PASS  task1=PASS**
