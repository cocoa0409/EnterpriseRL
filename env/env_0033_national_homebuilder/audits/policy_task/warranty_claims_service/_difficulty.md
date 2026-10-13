# Policy-task audit — warranty_claims_service / charter-global

## charter_global_frozen

- Frozen: 2026-10-04T23:33Z. Auditor: erl-task-policy-audit (independent auditor subagent; it did not author any audited artifact).
- Inputs and hashes, checked against the orchestrator's MANIFEST before reading:
  - `tasks/warranty_claims_service/warranty.extended.yaml` sha256 `ab936c682ffab86bc0efd0c88c08391eede1763923ed7d26845522fb157d57d9`
  - `tasks/warranty_claims_service/task_tools.py` sha256 `6e71cf46a70367bc1584148d6c2298ebfb4b96ab0efd199a3e1fb6ad4bd1a3fa`
  - `audits/_views/policy_task/warranty_claims_service/0.view.json` sha256 `de48700e…bc2ff1`, `1.view.json` sha256 `d2c12775…22d87b`. Both match.
- Fields I could read: the blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/warranty.yaml`, plus `products/purchase.yaml`, `design.yaml` and `homesite.yaml` to check whether the cross-category seeds are consistent), the full extended charter, the full `task_tools.py`, and each view's `task_id`, `frozen_time`, `user_scenario` and `initial_state`.
- Fields masked and not read before this file and both task derivations were frozen: `evaluation_criteria`, `computations`, `db_closure`, `db_closure_matches_initial_state`, `design_rationale`, `prerequisite_closure`, `solvability_contract`, `charter_scope`, `required_documents`, `worklog.md`, and every other audit.
- Entry conditions (Step 0): the brief supplies a gate snapshot with actual last lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK). The brief also explains why TRACEABILITY is NOT OK: the KB has not been rendered yet. Masked views with their hashes were supplied. I cite these entry conditions and did not re-run any gate.
- Read-domain note: to learn the exact semantics of the restricted compute DSL (`LATEST`/`COUNT` holding scope, the `within_months` window, `MONTHS`, `DAYS`, `RND`, `CFIELD`, `XSUM`, `XCOUNT`), I read the evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 215–425). It is a gate script, not a task artifact. It holds no scored value, and it was the only file read outside blueprint, this difficulty and `erlbench/`. I used its `build_env`/`eval_compute` from a temp script under `/tmp` (deleted at the end) to re-evaluate the charter's own `compute` on the masked worlds.

### policy_conflict_scan

The charter has 14 base policies, copied verbatim (`diff` of extended lines 1–751 against `blueprint/products/warranty.yaml` differs only by one trailing blank line), and 5 extended policies:

| extended policy | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| warranty_ext_missed_appointment_charge | state_due | assess_missed_appointment_charge_27486c7f (agent) | amount | [] |
| warranty_ext_finish_item_settlement | on_request | accept_finish_item_cash_settlement_135d939d (user) | amount | ← missed_appointment_charge (value_input, delay_mult) |
| warranty_ext_reinspection_charge | state_due | assess_reinspection_charge_a99ab20e (agent) | amount | [] |
| warranty_ext_dispatch_charge | state_due | assess_emergency_dispatch_charge_91903470 (agent) | amount | ← reinspection_charge (value_input, nonwarranty_mult) |
| warranty_ext_systems_item_settlement | on_request | accept_systems_item_cash_settlement_9ecd6f20 (user) | amount | ← dispatch_charge (state_gate) |

Overlapping subjects:
- Three policies write `warranty_charge_assessed`, but each writes a distinct `charge_type` (missed_appointment_fee, reinspection_fee, emergency_dispatch_fee) through a distinct tool.
- Two policies write `warranty_payout_approved` with payout_type cash_in_lieu. They are separated by coverage basis: the finish settlement takes the most recent workmanship approval, the systems settlement the most recent systems approval.
- The two settlements never claim the same item, because an item's basis is single-valued (`category_basis`).

Triggers, time anchors and terminal states:
- Every charge is "worked out … on the day it is assessed". Every settlement uses the settlement date.
- The terminal states are disjoint rows.

Cross-category reads:
- purchase: community, contract_price, status.
- design: variant_name and `design_events` option lines.
- homesite: status and `homesite_events` reservation deposits.
- All are read-only and match the `cross_category` declarations.

Conflicts found with base sections: see `override_declarations` and `findings` F1–F2 below.

Scope (inferred from the worlds alone, before reveal):
- Task 0 is a finish-item settlement whose world carries an uncharged missed appointment, so its scope is {finish_item_settlement, missed_appointment_charge}.
- Task 1 is a systems-item settlement whose world carries an uncharged emergency dispatch and an uncharged within-tolerance re-measurement, so its scope is {systems_item_settlement, dispatch_charge, reinspection_charge}.
- Together the two are pairwise disjoint and cover all 5 extended policies. I confirm this against `charter_scope` after the reveal, in the task files.

### rule_compute_equivalence

Every `compute_basis` quotation is a verbatim substring of its policy's `rule` (checked mechanically: 0 misses). For each binding I swept the rule back against `compute`:

- **missed_appointment_charge**
  - `miss_date` and `miss_item` are LATEST by appointment_date, which matches "the most recent missed appointment recorded on the coverage".
  - `miss_count` has three branches, one per ladder sentence. The 24-month window uses `within_months=24` on appointment_date, which the DSL implements as `0 <= MONTHS(d, NOW) < 24` ("later than the same calendar day 24 months before").
  - `notice_mult` uses `<2`, `<7` and else, matching "fewer than 2 / 2 to 6 / 7 or more".
  - `trade_mult` matches the rule's category lists.
  - `repeat_mult`: the 12-month window on assessed charges, less waivers in the window, matches the rule.
  - `result` rounds once and applies the billable ≥ 1 gate.
  - `waived_charges`, `recent_waived` and `delay_waived` (the last in the finish policy) count every `warranty_charge_waived` row, not only waivers of missed-appointment charges. Base `warranty_appointment_charges` says "A charge is waived only when the missed appointment followed a reschedule by Calloway", so the only waivable charge is a missed-appointment charge and the two readings coincide. This is an observation (O1).
- **finish_item_settlement**
  - `item_ref` and `approval_date` are LATEST workmanship approval by event_date.
  - `share`, `market_mult`, `finish_mult` and `delay_mult` follow their sentences.
  - `wait_days = DAYS(approval, NOW)`, which matches "approval date itself not counted".
  - `callbacks` has a 12-month window. `settlement` has three branches. `result` is MN after the callback step.
  - **Mismatch (F3):** `finish_added`/`finish_removed` are `XSUM('design','design_events',…)` over every design ledger row owned by the customer. The rule reads "the Design Studio Selections file of the home's purchase agreement".
- **reinspection_charge**
  - The tolerance mapping, `borderline_mult` (≥0.9, ≥0.75), the 12-month `repeat_mult`, `soil_mult` (category ∧ community), `settling_mult` (MONTHS <12, <24), `delay_mult` (>14, >7, matching "8 to 14") and `item_charge` (walkthrough → 0; covered work → share; else whole) all follow their sentences. Rounding happens once at the end.
  - **Mismatch (F4):** `rm_date`, `rm_item` and `rm_width` are LATEST over every `warranty_claim_inspected` row with inspection_finding within_tolerance. The rule's object is "the most recent **re-measurement** … that found a crack within tolerance … the re-reported claim item that was re-measured". An original (first-report) within-tolerance inspection qualifies in compute but not in the rule.
- **dispatch_charge**
  - `condition_mult`, `finding_mult`, `nonwarranty_mult` (reinspection plus dispatch charges in 12 months), `first_period_mult` (months ∧ no prior dispatch charge), `prorated_fee` (>2×, >1×, else) and `charge_due` (defect_confirmed → 0) follow their sentences.
  - **Mismatch (F5):** `hold_deposits = XCOUNT('homesite','homesite_events', event_type=homesite_payment_received, deposit_component=reservation_deposit)` counts reservation deposits on any of the customer's reservations, and `homesite_hold = EXISTS('homesite', status='held')` is a separate existence test. The rule requires "a homesite reservation on hold **whose** reservation deposit has been received", which ties the deposit to the held reservation.
- **systems_item_settlement**
  - `trade_mult`, `market_mult`, `anchor_shift` (approval_age if >2×target; approval_age−target if >target; else 0), `remaining_days = DAYS(NOW, systems_end) + anchor_shift` (algebraically DAYS(anchor, systems_end)), `remaining_mult` (≥730, ≥365), `maintenance_findings` (three findings, 24 months), `scale_mult` (contract_price ≥700k, ≥500k), `settlement` (RND) and `result` (MN after rounding) follow their sentences.
- **Every policy, ladder coverage:** every ladder tier of every `factors[]` entry is a rule sentence and a branch of its `decides` binding. Every branch is a stated tier. No tier lives in only one face.
- **Rounding mode (O2):** `RND` is Python `round` (half-even on binary floats), while every tool docstring says "rounded half up". No figure in either task lands on a half-cent tie, so there is no task consequence.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (5 distinct tools, each with `computes: amount`).
- Each docstring describes one atomic write, its receipt and its visibility to the homeowner. No docstring names another tool, states a position in a sequence, or adds a confirmation or review step. The only ordering-like word is "then", in "The homeowner can then see the new charge/payout", which describes the call's own effect.
- uuid8s: `27486c7f`, `135d939d`, `a99ab20e`, `91903470`, `9ecd6f20`. They are pairwise distinct, share no prefix and no tail, and are not sequential.
- `make_id` salts differ per tool. The systems tool uses `"cash_in_lieu_systems"`, so the two payout tools cannot collide.
- No function body reads history, judges eligibility or refuses. Each one creates one row and updates `charges_due`/`payouts_owed`.

### prerequisite_graph

- `prerequisite` is filled in on all 5 extended policies (`[]` on missed_appointment_charge and reinspection_charge).
- Edges:
  - finish → missed_appointment_charge
  - dispatch → reinspection_charge
  - systems → dispatch_charge
- Every `problem` is an extended policy id of this file. None is a base policy or a self-reference. The graph is acyclic: two chains of length 1 and 2.
- Each `policy_source` is a verbatim substring of its own policy's `rule` (checked mechanically).
- `form: state` on all three edges, with no `fallback_reason` on any of them. This is consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all three edges.
- `kind`/`gate`:
  - value_input `delay_mult` and value_input `nonwarranty_mult` are real bindings of the blocked policy's compute, and each depended-on write moves them: one more unwaived missed-appointment charge in the 6-month window, and one more reinspection charge in the 12-month window.
  - The systems edge is `state_gate` with `gate: warranty_events.charge_type`. That is a field name, not an eligibility gate: extended policies declare no `eligibility`, and the gate exists only as the rule sentence. This is an observation (O3); the gate is still discoverable from the rule.
- `condition`s restate the handling-time state at the strength of the sentences ("whose billable number … is one or more"; "re-report … within_tolerance … matched by … reinspection_fee"; "not confirmed as a covered defect and whose dispatch charge … is above zero").
- The finish edge's `effect` says the multiplier moves tiers "whenever the repair target days have passed". That holds only when no other unwaived missed-appointment charge already stands in the 6-month window. This is an observation (O4): it is a general statement that no task relies on beyond its own world.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test on each edge:

1. **finish ← missed appointment.**
   - Sentence: "The finish settlement is fixed only after every missed appointment on the coverage that the missed-appointment rules make chargeable carries its missed-appointment charge."
   - Test: ordering connective "only after"; record-visible state "carries its missed-appointment charge", which is a `warranty_charge_assessed`/missed_appointment_fee row; no tool, id or snake_case; scope "that the missed-appointment rules make chargeable" equals condition "billable number … one or more".
   - The only write in this difficulty that creates a missed_appointment_fee row is `assess_missed_appointment_charge_27486c7f`.
   - Derivation: the sentence plus the warranty ledger (misses without a matching charge row) plus the missed-appointment rule ("worked out for the most recent missed appointment … linked to that appointment's claim item") lead to a single resolving action: book the charge for the most recent miss, computed under that rule.
   - The rule carries no second wording, and the missed-appointment rule does not restate the sentence.
   - Result: PASS.
2. **dispatch ← reinspection.**
   - Sentence: "The dispatch charge is fixed only after every re-reported item that a re-measurement again found within tolerance and that the reinspection rules make chargeable carries its reinspection charge."
   - Test: "only after"; state "carries its reinspection charge"; one writer, `assess_reinspection_charge_a99ab20e`.
   - Derivation: the reinspection rule identifies "the most recent re-measurement … within tolerance", which gives a single reading.
   - Result: PASS.
3. **systems ← dispatch.**
   - Sentence: "A systems settlement is not paid until every emergency dispatch recorded on the coverage that the dispatch charge rules make chargeable carries its emergency dispatch charge."
   - Test: connective "not … until"; state "carries its emergency dispatch charge"; one writer, `assess_emergency_dispatch_charge_91903470`.
   - **Problem: the sentence gates "paid", not the policy's own result.** The systems policy's own result is the homeowner's written acceptance, which records a `warranty_payout_approved` row: "it becomes a payout only when the homeowner accepts it in writing", and the tool docstring says "records one approved payout". In this charter's vocabulary "paid" is a different, later event:
     - account `homeowner_payouts`: "Money Calloway has approved to pay the homeowner … and has not yet paid";
     - event `warranty_payout_issued`: "An approved payout is paid to the homeowner";
     - base `warranty_payouts_and_payments`: "Approved payouts are issued within payout_issue_business_days business days".
   - So the sentence admits a second reading: the acceptance (approval) may be recorded now, and only the later issue waits on the dispatch charge.
   - Result: SOURCE-POLICY RED, finding F6. The consequence is demonstrated in `1.md`.
- No extended or base rule states any other cross-problem order. In particular, base `warranty_payouts_and_payments` "an open charge does not stop Calloway from handling claims" concerns unpaid charges, not unbooked ones, so it neither grounds nor contradicts an edge.
- Docstrings are silent about sequence (see `action_binding_and_uuids`).

### override_declarations

Sentence-by-sentence sweep of each extended policy against its `base_policy_refs`, judged by the quantity that is ultimately scored:

- **missed_appointment_charge.** Refs: tolerances_and_exclusions, appointment_charges, structural_claims, transfer, agg_one_owner_per_home.
  - appointment_charges sentence 1 ("Each missed appointment beyond free_missed_appointments … carries missed_appointment_fee_usd, linked to the claim item") is replaced and declared. The `superseded_clause` is verbatim in base, and `replaced_by` is verbatim in the extended rule.
  - appointment_charges sentence 2 (dispatch fee) does not govern this quantity. Its waiver sentences are inherited, and the ladder's waived-charge tier is consistent with them.
  - **agg_one_owner_per_home** says "history that counts over the life of the coverage (missed appointments, one-time repairs) counts across owners of the same home", and base measure `warranty_msr_missed_appointments` uses the window "all coverages sharing the purchase_id". The extended policy counts misses "recorded on the coverage", and the compute's `COUNT` is scoped to this coverage_id. This sentence is not named in `overwrite`. It is an undeclared override, finding F1.
  - tolerances, structural and transfer: no sentence governs the missed-appointment charge.
  - **Not cited, but rendered with the charter:** base `warranty_callbacks` says "An accepted callback is approved under the original coverage basis even when that coverage period has since ended, carries no deductible or fee, and is numbered by callback_seq." In this charter, "fee" names exactly the homeowner charges, including the missed-appointment fee (accounts: "structural deductible, missed appointment, reinspection, transfer and emergency dispatch fees"). The extended rule charges the most recent missed appointment whatever its item, including an appointment for an accepted callback's repair, and does not name this sentence in `overwrite`. This is finding F2, and task 0 demonstrates its consequence.
- **finish_item_settlement.** Refs: structural_claims, payouts_and_payments, coverage_periods, callbacks; `overwrite: []`.
  - payouts: base fixes only a cap ("no more than cash_in_lieu_max_usd") and written acceptance. The extended amount is ≤ cap (MN) and acceptance is kept, so the extended policy refines base without contradicting it.
  - coverage_periods, callbacks and structural are followed.
  - No undeclared override.
- **reinspection_charge.** The tolerances sentence on the reinspection fee is replaced and declared. The other cited sentences (tolerance boundaries "equal … is out of tolerance", appointment charges, service levels) are followed. No undeclared override.
- **dispatch_charge.** The appointment_charges dispatch-fee sentence is replaced and declared. The extended "covered defect carries no dispatch charge" agrees with base "finds a condition caused by the homeowner or not covered". No undeclared override.
- **systems_item_settlement.** Same analysis as the finish settlement: payouts cap and written acceptance kept. No undeclared override.
- No anonymous intermediate factor, 0/1 multiplier or dropped branch found. The waived-charge count and the response-hours zero branch sit inside declared replacements.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source (non-fall-through tiers) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| missed_appt | miss_count_convention | method | miss_count | 3 | tier 2 = no waiver ∧ coverage age (events + coverage row) | – |
| | notice_multiplier | parameter | notice_mult | 3 | no | – |
| | trade_trip_multiplier | parameter | trade_mult | 3 | no | – |
| | repeat_miss_multiplier | parameter | repeat_mult | 3 | yes: billable number ∧ unwaived charges | – |
| finish | settlement_share | parameter | share | 3 | no | – |
| | labor_market_multiplier | parameter | market_mult | 3 | no | purchase |
| | finish_level_multiplier | parameter | finish_mult | 4 | yes: design package ∧ design ledger | design |
| | service_delay_multiplier | parameter | delay_mult | 3 | yes: approval age ∧ charges | – |
| | callback_settlement_method | method | settlement | 3 | no | – |
| reinspection | borderline_multiplier | parameter | borderline_mult | 3 | no | – |
| | repeat_reinspection_multiplier | parameter | repeat_mult | 3 | no | – |
| | soil_movement_multiplier | parameter | soil_mult | 3 | yes: item category ∧ purchase community | purchase |
| | settling_period_multiplier | parameter | settling_mult | 3 | no | – |
| | remeasure_delay_multiplier | parameter | delay_mult | 3 | no | – |
| | shared_visit_method | method | item_charge | 3 | no | – |
| dispatch | condition_class_multiplier | parameter | condition_mult | 3 | no | – |
| | finding_multiplier | parameter | finding_mult | 3 | no | – |
| | nonwarranty_visit_multiplier | parameter | nonwarranty_mult | 3 | no | – |
| | first_period_multiplier | parameter | first_period_mult | 3 | yes: coverage age ∧ dispatch charges | – |
| | active_buyer_multiplier | parameter | buyer_mult | 3 | yes: tier 2 = no active agreement ∧ held reservation ∧ deposit | homesite (plus purchase) |
| | response_proration_method | method | prorated_fee | 3 | no | – |
| systems | systems_trade_multiplier | parameter | trade_mult | 3 | no | – |
| | systems_market_multiplier | parameter | market_mult | 3 | no | purchase |
| | remaining_coverage_anchor | **method** | anchor_shift | 3 | no | – |
| | remaining_coverage_multiplier | parameter | remaining_mult | 3 | no | – |
| | maintenance_record_multiplier | parameter | maintenance_mult | 3 | no | – |
| | home_scale_multiplier | parameter | scale_mult | 3 | no | purchase |

Structural checks over all 27 factors:
- **Counts.** Each policy has 4–6 factors, at least 2 labelled parameter and 1 labelled method (missed 4: 3p+1m; finish 5: 4p+1m; reinspection 6: 5p+1m; dispatch 6: 5p+1m; systems 6: 5p+1m).
- **Shape.** Each factor's `decides` is an input, not `result`. Bindings are disjoint within each policy. Every ladder has at least 3 tiers that are pairwise disjoint as stated.
- **Distinct outcomes.** No two tiers of any ladder select the same value or method.
- **Fall-through equals baseline.** Every fall-through tier equals that factor's `baseline` binding, and every `baseline.rule` sentence is verbatim in its `rule` (checked mechanically).
- **Label honesty, method factors:**
  - miss_count_convention is a method. Its tiers change which records enter the count (net of waivers, a 24-month window, or all).
  - callback_settlement_method is a method: cap, midpoint or scheduled.
  - shared_visit_method is a method: zero, equal share or whole.
  - response_proration_method is a method: zero, ratio proration or whole.
  - **remaining_coverage_anchor is not a method.** Every tier keeps one formula, remaining days = DAYS(anchor date, systems end date), and only substitutes a different date, which is a number: the approval date, approval + repair_target_days, or the settlement date. The compute implements exactly that, as a numeric addend `anchor_shift` added to `DAYS(NOW, systems_end_date)`. This is a parameter labelled `method` (finding F7). With it struck, the systems settlement has 0 honest method factors against a floor of 1. Task 1 records the consequence.
- **Industry realism.** I found no tier condition that holds of every customer who reaches the write, and no outcome that is a straw treatment. Each ladder is the kind of differentiation a production builder's warranty desk would publish:
  - notice given, trade dispatched and repeat behaviour for missed-appointment fees;
  - item category, labor market, finish level, service delay and callback history for cash-in-lieu;
  - closeness to tolerance, soil, settling age, re-measure delay and a shared visit for reinspection;
  - safety class, finding, visit frequency, first-period goodwill, active-buyer goodwill and response lateness for dispatch;
  - trade, market, remaining coverage, maintenance record and home scale for a systems settlement.
- **Coverage over the charter.** Multi-source factors exist in every policy except the systems settlement. Cross-difficulty factors read purchase (labor_market, soil_movement, systems_market, home_scale), design (finish_level) and homesite (active_buyer).
- **Per task**, this gives task 0 multi-source = finish_level and service_delay, cross-difficulty = labor_market (purchase) and finish_level (design); and task 1 multi-source = soil_movement, first_period and active_buyer, cross-difficulty = soil_movement and systems_market (purchase), active_buyer (homesite), home_scale (purchase). Whether each factor bears weight is in each task's `factor_weight`.

### findings

- **F1 — SOURCE-POLICY RED (latent; bears on neither task's scored solution).** Undeclared override of `warranty_agg_one_owner_per_home`.
  - Symptom: the missed-appointment count of the extended policy ignores prior owners' misses.
  - Root cause: the extended rule "The standard missed-appointment charge counts every missed appointment recorded on the coverage" and compute `COUNT('warranty_events', event_type='warranty_appointment_missed')` (scoped to one coverage_id) contradict base "history that counts over the life of the coverage (missed appointments, one-time repairs) counts across owners of the same home". `overwrite` names only the `warranty_appointment_charges` sentence.
  - Consequence: for a subsequent owner whose home carries the previous owner's misses, the base sentence counts those misses and the extended compute does not, so the billable number differs and the charge differs.
  - Location: `warranty.extended.yaml` → `warranty_ext_missed_appointment_charge.overwrite` / `rule` / `compute.life_misses`.
  - Tasks 0 and 1 are both original buyers with one coverage on their home, so neither task's scored values move.
- **F2 — SOURCE-POLICY RED (affects task 0).** Undeclared conflict with base `warranty_callbacks`.
  - Base sentence: "An accepted callback … carries no deductible or fee". The charter's own `accounts` lists "missed appointment" among the homeowner "fees".
  - Extended rule: "A missed-appointment charge is worked out for the most recent missed appointment recorded on the coverage … linked to that appointment's claim item." It makes no exception for an appointment booked for an accepted callback's repair.
  - `warranty_callbacks` is in neither `base_policy_refs` nor `overwrite` of the missed-appointment policy, although it is in the finish policy's refs and so is rendered alongside it.
  - The two passages reach different conclusions on a missed callback-repair appointment: base gives no fee, the extended policy gives a charge.
  - The demonstration against task 0's world is in `0.md`.
- **F3 — SOURCE-POLICY RED (latent; no consequence in task 0).**
  - Problem: the finish-level compute sums the design option lines of every design file the customer owns. The rule says "the Design Studio Selections file of the home's purchase agreement" (`compute.finish_added`/`finish_removed` use XSUM with no selection or purchase filter).
  - Consequence: a homeowner with a second design file (another agreement) gets that file's flooring/cabinetry/countertop lines counted, which can move the tier.
  - Task 0 has exactly one design file, so there is no consequence there.
- **F4 — SOURCE-POLICY RED (latent; no consequence in task 1).**
  - Problem: the reinspection compute's object (`rm_date`/`rm_item`/`rm_width`: latest within-tolerance inspection of any item) is broader than the rule's object (the most recent re-measurement of a re-reported item).
  - Consequence: where the latest within-tolerance inspection is a first report, compute charges it and the rule does not.
  - In task 1 the latest within-tolerance inspection is a re-measurement, so there is no consequence.
- **F5 — SOURCE-POLICY RED (latent; no consequence in task 1).**
  - Problem: the active-buyer middle tier's compute does not tie the received reservation deposit to the held reservation ("a homesite reservation on hold whose reservation deposit has been received").
  - Consequence: for a customer with a held reservation without a deposit plus another reservation with a deposit, compute gives 0.75 and the rule gives 1.00.
  - Task 1 has one reservation, held, whose deposit is received, so there is no consequence.
- **F6 — SOURCE-POLICY RED (affects task 1).** The systems prerequisite sentence gates payment ("is not paid until"), not the policy's own result, the written acceptance or payout approval (see `prerequisite_sentences` item 3). The demonstration is in `1.md`.
- **F7 — SOURCE-FACTOR RED (affects task 1).**
  - Problem: `remaining_coverage_anchor` is labelled `method` but its tiers substitute a date (a number) into one unchanged formula.
  - Consequence: the systems settlement has no honest method factor.
  - Location: `warranty_ext_systems_item_settlement.factors[remaining_coverage_anchor]`.
- Observations:
  - O1: waived-charge counts are not filtered by charge type, which is equivalent under base.
  - O2: RND is half-even while the docstrings say half-up; no task figure sits on a tie.
  - O3: the state_gate `gate` is a field name, not an eligibility id.
  - O4: the finish edge `effect` is worded more broadly than the tier logic.
  - O5: LATEST breaks same-date ties by dictionary order. Task 0 has two workmanship approvals on 2026-04-29, which are not the latest, so nothing depends on it.

## closing_checklist

Written 2026-10-04T23:50Z, after both reveals. This is the only post-reveal section of this file.

- Per-task files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, alongside this file. This is the first revision; there is no older revision.
- Comparison verdicts: **not all PASS.**
  - Task 0: SOURCE-POLICY RED (F2).
  - Task 1: SOURCE-POLICY RED (F6) and SOURCE-FACTOR RED (F7).
- Charter: latent SOURCE-POLICY RED findings F1, F3, F4 and F5 bear on neither task's scored values.
- Coverage and scope: the 5 extended policies are fully covered. The revealed `charter_scope`s are {missed_appointment_charge, finish_item_settlement} and {reinspection_charge, dispatch_charge, systems_item_settlement}: pairwise disjoint and jointly complete. Task tools and GT are closed. The uuid8s are independent.
- Trees:
  - Task 0 has 1 prerequisite problem and 1 value_input edge.
  - Task 1 has 2 prerequisite problems and 1 value_input edge.
  - Each tree's root is owner=user.
  - The difficulty-wide graph is acyclic (two disjoint chains).
- Factors: all 27 declared factors bear weight on their task's world. Every baseline is honest and gives a definite number different from gold (75.00/87.89, 450.00/925.04, 100.00/25.20, 125.00/48.99, 400.00/842.40). The exception is F7, which leaves the systems computation with 0 honest method factors.
- The difficulty does **not** pass the source-layer audit. I did not re-run the instantiation-stage gates on a final form, because no final form exists until the findings are reworked.

---

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-05, before any revision-2 GT reveal. Auditor: erl-task-policy-audit (independent auditor subagent, same as round 1).
- Inputs:
  - `warranty.extended.yaml` sha256 `ebcff8b8d1e09bd0ffc391a1e076925d62cb9cf228e734c266cfe30490e16efb` (round 1: `ab936c68…`, **changed**).
  - `task_tools.py` sha256 `eb1bba45fdd0bd20ba86ba192fadc89544620619ac29eee5f812789fbffa1e1a` (round 1: `6e71cf46…`, **changed**).
  - Views `0.view.json` `ac955e87…`, `1.view.json` `251b41f1…`. Both match the MANIFEST.
- Because both shared inputs changed, every charter-global section below is **re-derived in full**. None is carried forward.
- The base copy is still verbatim: extended lines 1–751 equal `blueprint/products/warranty.yaml` byte-for-byte.
- Fields permitted and masked are as in round 1.
- Read domain this round: blueprint, this difficulty's charter, tools and views. Per the brief, the gate scripts under `skills/` were **not** read. Compute was re-evaluated by the auditor's own re-implementation of the DSL semantics, in a temp script under `/tmp`, deleted at the end.
- Entry conditions: the orchestrator's re-run gate snapshot is cited (all OK; CACHE-DIFF INFO; TRACEABILITY NOT OK, deferred to KB publication). I did not re-run it.
- contamination_disclosure: the round-1 reveal exposed the round-1 GT of both tasks to this auditor; this cannot be undone. Mitigation:
  - Each revision-2 derivation below is computed afresh from the revision-2 charter and views. Every figure was produced by evaluating the revision-2 `compute` on the revision-2 world, not by recalling round-1 numbers.
  - Where a revision-2 figure equals a round-1 figure, I state why the inputs it depends on are unchanged.
  - I opened no revision-2 GT before the freeze.

### What changed in the charter (re-read in full)

- **missed_appointment_charge**
  - `base_policy_refs` adds `warranty_callbacks`.
  - A new `overwrite` entry supersedes the `warranty_agg_one_owner_per_home` sentence "Every owner of the home shares … counts across owners of the same home." It is verbatim in base, and its `replaced_by` is verbatim in the rule.
  - New rule sentence: a miss whose claim item has an accepted callback awaiting its repair (more callback approvals than callback repairs) carries no charge, but still counts.
  - New compute bindings `cb_approvals`, `cb_repairs` and `callback_open` gate `result`.
- **finish_item_settlement**
  - New binding `design_file = CFIELD('design','selection_id', purchase_id=F('purchase_id'))`. The finish XSUMs now filter `selection_id=design_file`.
  - The edge `effect` is reworded conditionally.
- **reinspection_charge**
  - Rule object restated as "the most recent inspection … that found a crack within tolerance".
  - New sentence: "That inspection is the re-measurement of a re-reported item only when the coverage records at least two claim items filed in its defect category and at least two denials for within tolerance; where either count falls short … no reinspection charge is made."
  - New bindings `same_category_items`, `within_tolerance_denials` and `re_report` gate `result`.
- **dispatch_charge**: new binding `held_reservation = CFIELD('homesite','reservation_id', status='held')`. `hold_deposits` now filters `reservation_id=held_reservation`.
- **systems_item_settlement**
  - The prerequisite sentence now reads "A systems settlement is not offered to the homeowner, and no cash-in-lieu payout is approved on it, until …".
  - The `remaining_coverage_anchor` factor and its `anchor_shift` binding are removed. `remaining_days = DAYS(NOW, systems_end_date)`, stated in the rule as "from the settlement date … the settlement date itself not counted".
  - New method factor `repeat_failure_settlement_method` decides `settlement` from the systems callback approvals in 12 months (two or more gives the cash-in-lieu maximum; exactly one gives the midpoint; otherwise the scheduled figure), plus a new param `callback_window_months`.
- **task_tools.py**: the docstrings' amount wording is now "already rounded to the nearest cent". The previous "half up" is gone (O2). Function bodies, owners, signatures and uuid8s are unchanged.

### policy_conflict_scan (rev 2)

- The subject and tool partition is unchanged from round 1: 5 policies, 5 tools, 3 distinct charge_types and 2 payout bases. There is no new overlap.
- New cross-category read: design `selection_id`, a key used for the file filter.
- Scope inferred from the worlds:
  - task 0 = {finish, missed_appointment};
  - task 1 = {systems, dispatch, reinspection};
  - disjoint and jointly complete.

### rule_compute_equivalence (rev 2)

- Every `compute_basis` quotation is verbatim in its rule (checked mechanically: 0 misses). Every baseline.rule sentence is in its rule.
- Sweep of the changed bindings:
  - **missed:** `callback_open` implements "more callback approvals than callback repairs recorded on that item": approvals minus seq-0 approvals vs. repairs minus seq-0 repairs. `result` returns 0 when it is open; "still counted" holds because `life_misses` is not filtered.
  - **finish:** `design_file` with the selection filter equals "the Design Studio Selections file of the home's purchase agreement". **F3 closed.**
  - **reinspection:** `rm_*` = latest within-tolerance inspection equals the new rule object. `re_report` (≥ 2 same-category items ∧ ≥ 2 within_tolerance denials) and `result` 0 when false equal the new sentence. Rule and compute now agree. **F4 closed** as an equivalence defect. The rule's re-report criterion is a count proxy; see O7.
  - **dispatch:** `held_reservation` with the reservation filter ties the deposit to a held reservation. **F5 closed** for one held reservation. Residual: `CFIELD` returns the first held reservation only. With two held reservations where only the second has its deposit, the rule ("a homesite reservation on hold whose reservation deposit has been received") gives 0.75 and the compute gives 1.00. This is latent (O8); neither world has two holds.
  - **systems:** `remaining_days`, `remaining_mult`, `systems_callbacks` (window approvals under systems minus window seq-0 approvals) and `settlement` (three branches) follow their sentences. `result` is MN after the callback step, as stated.
- O1 (waivers not filtered by charge type) is unchanged and still equivalent under base. O5 (LATEST tie-break) is unchanged. Both are recorded only.
- O2 is closed: the docstrings no longer promise half-up rounding.

### action_binding_and_uuids (rev 2)

- Unchanged in substance. There are 5 `(target_tool, computes)` pairs, each claimed once.
- uuid8s `27486c7f`, `135d939d`, `a99ab20e`, `91903470` and `9ecd6f20` are distinct and unchanged.
- No docstring names another tool or states a sequence. The only ordering-like word is "then", meaning the homeowner can see the call's own result.
- No function body reads history, judges or refuses.

### prerequisite_graph (rev 2)

- The edges and graph are unchanged: finish ← missed (value_input, delay_mult); dispatch ← reinspection (value_input, nonwarranty_mult); systems ← dispatch (state_gate). Acyclic.
- Each `policy_source` is verbatim in its own rule (checked mechanically). `resolved_by` equals the depended-on `target_tool`. `form: state` on all, no `fallback_reason`.
- O3 (the state_gate `gate` is a field name) is kept as an observation.
- O4 is closed: the finish `effect` now says the tier moves "where the repair target days have passed and no other unwaived missed-appointment charge of that window stood".
- **N1 (new; SOURCE-POLICY RED, latent).** The finish edge `condition` was not updated for the new callback exemption.
  - The condition is "Every warranty_appointment_missed row on the coverage whose billable number under the missed-appointment rules is one or more is matched by a … missed_appointment_fee row".
  - The `policy_source` sentence covers only misses "that the missed-appointment rules make chargeable", and those rules now say a miss on an item with an open accepted callback "carries no charge".
  - So in a world where the most recent miss has billable ≥ 1 and an open callback, the condition is false (no charge row) while the sentence's state holds (nothing chargeable). The condition is broader than the sentence.
  - Introduced by the F2 rework. Neither task's world has such a miss (see each task file).
- **N2 (newly found; present unchanged since round 1, missed by the round-1 audit; SOURCE-POLICY RED, latent).** The dispatch edge has the same kind of gap.
  - Its `condition` ("Every claim item filed as a re-report whose warranty_claim_inspected row shows inspection_finding within_tolerance … is matched by a … reinspection_fee row") requires a charge row on every re-reported within-tolerance item.
  - The sentence covers only those "that the reinspection rules make chargeable". Those rules give no charge for a re-measurement on a walkthrough day ("where a walkthrough was held at the home that day, no reinspection charge is made") or where the re-report counts fall short.
  - Task 1's re-measurement day 2026-09-08 has no walkthrough, so there is no consequence there.

### prerequisite_sentences (rev 2)

1. **finish ← missed.** The sentence is unchanged and passes the four-point test.
   - Reading derivation: the sentence plus the ledger plus the missed rule (now including the open-callback exemption) yield exactly one resolving action, booking the charge for the most recent miss when the rule makes it chargeable. One writer: `assess_missed_appointment_charge_27486c7f`.
   - The condition/strength mismatch is N1.
2. **dispatch ← reinspection.** The sentence is unchanged and passes. The condition/strength mismatch is N2.
3. **systems ← dispatch.** New sentence: "A systems settlement is not offered to the homeowner, and no cash-in-lieu payout is approved on it, until every emergency dispatch recorded on the coverage that the dispatch charge rules make chargeable carries its emergency dispatch charge."
   - Ordering connective "until".
   - What is blocked is now explicitly the approval of the cash-in-lieu payout, which is exactly the `warranty_payout_approved` row the user tool writes ("records one approved payout"), plus the offer that precedes it.
   - Record-visible state; one writer, `assess_emergency_dispatch_charge_91903470`.
   - No tool, id or snake_case.
   - The "paid = issued" second reading is no longer available. **F6 closed.**
- No rule states any other cross-problem order. The depended-on rules do not restate the sentences.

### override_declarations (rev 2)

- **missed_appointment_charge**
  - The agg_one_owner_per_home sentence is now named in `overwrite`, with a replacement that keeps every other part of it (shared dates, one-time repairs across owners). **F1 closed.**
  - The appointment_charges replacement is unchanged and declared.
  - `warranty_callbacks` is now cited, and the rule carries the callback exemption with its reason ("because an accepted callback carries no fee"). This is consistent with base `warranty_callbacks` "carries no deductible or fee". **F2 closed** for the case it was demonstrated on: a miss on an accepted callback still awaiting its repair.
  - Residual (O6, latent): the exemption is evaluated "on the day it is assessed". A miss on a callback's repair appointment assessed after that callback's repair has been completed would be charged by the extended rule, while base "an accepted callback … carries no … fee" would still exempt it. Neither world contains such a sequence.
- **reinspection_charge**
  - The superseded base clause is unchanged and declared.
  - The rule now defines re-report by counts (O7, latent): the criterion "at least two claim items filed in its defect category and at least two denials for within tolerance" counts the item's own denial and within-tolerance denials of *any* category. So it can classify a first report as a re-report: an earlier same-category item that was approved, plus an unrelated within-tolerance denial elsewhere. In that case the charter's own parameter description (`reinspection_fee_usd`: "Fee (USD) when an item already denied as within tolerance is re-reported and again found within tolerance") and the rule disagree.
  - In task 1's world the earlier same-category item, WSR-55620-01, *was* denied within tolerance, so the proxy and the description agree. No consequence.
- **finish, dispatch, systems**: as in round 1, no undeclared override. The systems repeat-failure method only shapes an amount the base caps at cash_in_lieu_max_usd; MN is kept.

### factor_ladders (rev 2)

The table is unchanged from round 1 except for the systems settlement:

| policy | factor | label | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| systems | systems_trade_multiplier | parameter | trade_mult | 3 | no | – |
| | systems_market_multiplier | parameter | market_mult | 3 | no | purchase |
| | **repeat_failure_settlement_method** | **method** | settlement | 3 | no | – |
| | remaining_coverage_multiplier | parameter | remaining_mult | 3 | no | – |
| | maintenance_record_multiplier | parameter | maintenance_mult | 3 | no | – |
| | home_scale_multiplier | parameter | scale_mult | 3 | no | purchase |

- `repeat_failure_settlement_method` is an honest method. Its tiers select different algorithms: the cash-in-lieu maximum itself, the midpoint between the scheduled figure and the maximum, or the scheduled figure. All three are stated in the rule and implemented as the three branches of `settlement`. Its fall-through equals the baseline (`scheduled`).
- The business reality is plausible: repeated failure of the same system pushes a cash-in-lieu offer toward the maximum.
- `remaining_coverage_anchor` is gone, so there is no mislabelled factor left. **F7 closed.**
- Counts per policy (all within bounds):

  | policy | factors | parameter | method |
  | --- | --- | --- | --- |
  | missed | 4 | 3 | 1 |
  | finish | 5 | 4 | 1 |
  | reinspection | 6 | 5 | 1 |
  | dispatch | 6 | 5 | 1 |
  | systems | 6 | 5 | 1 |

- All ladders still have at least 3 pairwise-disjoint tiers with distinct outcomes. Every tier is in its rule, and every fall-through equals its baseline. The finish_level and active_buyer bindings gained the file and reservation keys, and their tiers are unchanged.
- Per task:
  - task 0: multi-source = finish_level, service_delay; cross-difficulty = purchase, design.
  - task 1: multi-source = soil, first_period, active_buyer; cross-difficulty = purchase, homesite.

### findings (rev 2, charter-global)

| round-1 id | status in rev 2 | evidence |
| --- | --- | --- |
| F1 (latent) | **closed** | `overwrite[0]` names the agg sentence; the replacement is verbatim in the rule |
| F2 (task 0) | **closed** for the demonstrated case | callback exemption in the rule and compute. Residual O6 is latent. Task 0's world moved the charged miss off the callback item (see `0.md`) |
| F3 (latent) | **closed** | `design_file` filter |
| F4 (latent) | **closed** as an equivalence defect | rule and compute agree. The criterion is a count proxy; O7 is latent |
| F5 (latent) | **closed** for a single hold | residual O8 is latent (multiple holds) |
| F6 (task 1) | **closed** | the sentence now blocks the offer and payout approval |
| F7 (task 1) | **closed** | anchor removed; honest method factor added |
| O1, O3, O5 | kept | unchanged; recorded |
| O2, O4 | closed | docstring wording; conditional effect |

New, both SOURCE-POLICY RED and latent (no task world affected):
- **N1**: finish edge condition broader than its sentence. Introduced by the F2 rework.
- **N2**: dispatch edge condition broader than its sentence. Present since round 1 and missed by the round-1 audit, which marked check 6 item 2 PASS. This revision corrects that.

New observations: O6, O7, O8 (all latent, as above).

### closing_checklist (revision 2)

Written 2026-10-05T00:31Z, after both revision-2 reveals.

- Per-task files: `0.md` and `1.md` each carry the round-1 text untouched plus `## revision_2`. Both revision-2 comparison sections read **PASS** on all four relationships.
- Coverage and scope:
  - The revealed `charter_scope`s are {missed, finish} and {reinspection, dispatch, systems}: pairwise disjoint and jointly covering all 5 extended policies.
  - Task tools and GT are closed. The uuid8s are independent and unchanged.
- Trees:
  - Task 0: n = 1, 1 value_input edge. Task 1: n = 2, 1 value_input edge.
  - Each tree has an owner=user root. The difficulty-wide graph is acyclic.
- Factors:
  - Every computation declares a baseline written into its rule, and 4–6 factors with ≥ 2 parameter and ≥ 1 honest method.
  - Every ladder has at least 3 tiers, distinct in outcome, with every tier stated in the rule.
  - All 27 factors bear weight on their task's world.
  - Each task has a multi-source and a cross-difficulty factor.
  - Whole baselines differ from gold: 75.00/87.89, 450.00/925.04, 100.00/25.20, 125.00/48.99, 400.00/886.10.
- Round-1 REDs: F1–F7 are all closed. No regression in any per-task relationship.
- **Open at charter level (latent, no task affected):** N1 and N2, both SOURCE-POLICY RED: two `prerequisite[].condition`s broader than their prerequisite sentences. N1 was introduced by the F2 rework. N2 was present since round 1 and missed by the round-1 audit. Observations O6, O7 and O8 are latent.
- Gates: the orchestrator's re-run on this form is cited from the brief (all correctness gates OK; TRACEABILITY deferred to KB publication). I did not re-run them.
- **Conclusion:**
  - Both tasks pass the source-layer audit.
  - The difficulty's charter-level policy self-consistency is not fully clean until N1 and N2 are resolved. They change no scored value in either task, so they are reported for the charter, not against either task.

---

## revision_3

### charter_global_frozen (revision 3)

- Frozen: 2026-10-05, before any revision-3 GT reveal. Auditor: erl-task-policy-audit (independent auditor subagent, same as rounds 1–2).
- Inputs:

  | input | sha256 | vs round 2 |
  | --- | --- | --- |
  | `warranty.extended.yaml` | `8d402f793f05de4fefd54599555e48ffa6170b562e0c58f1407ba620db2a28cd` | **changed** (was `ebcff8b8…`) |
  | `task_tools.py` | `eb1bba45…` | unchanged |
  | `0.view.json` | `ac955e87…` | unchanged |
  | `1.view.json` | `251b41f1…` | unchanged |

- Because the charter changed, every charter-global section is **re-derived** below. Sections whose content turns out identical to round 2 say so explicitly, after the re-check.
- `action_binding_and_uuids` depends only on `task_tools.py` (unchanged) and on each policy's `target_tool`/`computes` (re-checked: unchanged). It is **carried forward** from revision 2, with the two hashes above as grounds.
- The base copy is still verbatim (lines 1–751 equal `blueprint/products/warranty.yaml`).
- No gate scripts were read. Compute was re-evaluated by the auditor's own DSL re-implementation (a temp script under `/tmp`, deleted at the end).
- The gate snapshot (all correctness gates OK; TRACEABILITY deferred) is cited, not re-run.
- contamination_disclosure: round-1 and round-2 GT of both tasks are known to this auditor. Every revision-3 figure is recomputed on the revision-3 charter. No revision-3 GT was read before this freeze.

### What changed in the charter (revision 2 → 3)

- **missed_appointment_charge (O6).**
  - The callback exemption is restated as "A missed appointment that fell while its claim item had an accepted callback awaiting repair (the item's latest callback is dated on or before the missed appointment date, and the item's latest repair is either dated on or before that callback or dated on or after the missed appointment date) carries no charge …".
  - The compute now uses `last_callback = LATEST(callback_filed.event_date, item)` and `last_repair = LATEST(repair_completed.event_date, item)`, with `callback_open = last_callback ≠ None ∧ last_callback ≤ miss_date ∧ (last_repair = None ∨ last_repair ≤ last_callback ∨ last_repair ≥ miss_date)`.
  - This replaces the count-based test of revision 2.
- **finish edge `condition` (N1).** Now: "Every warranty_appointment_missed row … that the missed-appointment rules make chargeable (billable number one or more, and its appointment date not falling while its claim item had an accepted callback awaiting repair) is matched by … ; a miss the rules leave uncharged needs no such row."
- **reinspection rule (O7).** The re-report sentence is re-worded and moved after the re-measure delay sentence: "… at least two denials for within tolerance, **whichever claim items those denials concern**; where either count falls short, the inspection counts as a first report …". The compute is unchanged.
- **dispatch edge `condition` (N2).** Now: "Every within-tolerance inspection on the coverage that the reinspection rules make chargeable (counted as the re-measurement of a re-reported item by the claim-item and denial counts, and no walkthrough held on its date) is matched by … ; an inspection the rules leave uncharged needs no such row."
- **dispatch active-buyer tier (O8).**
  - Rule, ladder, compute_basis and cross_category note now read "a homesite reservation on hold **and** with a reservation deposit received on the homeowner's homesite ledger within the last 12 calendar months".
  - Compute: `hold_deposits = XCOUNT(… reservation_deposit, within_months=K('deposit_window_months'))` with the new param `deposit_window_months: 12`. `held_reservation` is removed.
- **No change:** finish rule and compute, systems policy, all other factors, baselines, overwrites, refs, tools.

### policy_conflict_scan (rev 3)

- Unchanged in substance: same subject and tool partition, cross-category reads and inferred scopes (task 0 = {missed, finish}; task 1 = {reinspection, dispatch, systems}).
- The O8 change drops the reservation-key read; it now reads homesite status plus the ledger within 12 months.

### rule_compute_equivalence (rev 3)

- All `compute_basis` quotations are verbatim in their rules (checked mechanically: 0 misses). All baseline.rule sentences are in their rules.
- Changed bindings swept:
  - **missed `callback_open`** implements the parenthetical exactly: latest callback ≤ miss date, and latest repair absent, ≤ that callback, or ≥ the miss date. `result` returns 0 when it is open. "Still counted" holds because `life_misses` is unfiltered.
  - **dispatch `hold_deposits`/`buyer_mult`** implement "a homesite reservation on hold and … a reservation deposit received on the homeowner's homesite ledger within the last 12 calendar months". Rule and compute agree. The rule itself now no longer ties the deposit to the held reservation, so the round-2 residual O8 (multiple holds) disappears by definition. **O8 closed.**
  - **reinspection:** the compute is unchanged and the rule now says explicitly that the denials may concern any claim items, which the compute (`COUNT(… claim_denied, denial_reason='within_tolerance')`, no item filter) does. Equivalent.
- O1 and O5 are kept and unchanged.

### action_binding_and_uuids (rev 3)

Carried forward from revision 2 on unchanged `task_tools.py` (`eb1bba45…`) and unchanged `target_tool`/`computes` per policy: PASS.

### prerequisite_graph (rev 3)

- Edges, kinds, gates, forms, `resolved_by` and acyclicity are unchanged. `policy_source`s are verbatim in their rules (checked mechanically).
- **N1: closed.** The finish edge condition now carries the callback exemption and states that "a miss the rules leave uncharged needs no such row". It matches the sentence's "that the missed-appointment rules make chargeable".
- **N2: closed.** The dispatch edge condition now carries the count test and the walkthrough exclusion and states that "an inspection the rules leave uncharged needs no such row". It matches the sentence.
- O3 is kept.
- **O9 (new observation; also latent in rounds 1–2, not raised then).** Both conditions, like their sentences, leave implicit *as of when* "the rules make chargeable" is judged for an earlier record. The rules themselves compute a charge only "for the most recent missed appointment / inspection … on the day it is assessed".
  - As-of-its-own-date reading: each earlier record was judged when it was the most recent. This is the only reading under which the rules compute anything for it, and it is the one I used in rounds 1–3.
  - As-of-now reading: re-applying today's counts to old records (task 0's 2025-06-12 miss, billable 2 today; task 1's first reports WSR-55102-01 and WSR-55620-01, which meet today's counts) would make those conditions unsatisfiable. No rule computes a charge for a non-latest record, so this reading yields no executable action and is not a second defensible solution.
  - Recorded as an observation only.

### prerequisite_sentences (rev 3)

- All three sentences are unchanged from revision 2 and pass the four-point test.
- One writer per state-form edge.
- No other cross-problem order is stated in any rule.
- The reading derivations of revision 2 still hold. The missed rule's exemption test changed, but the resolving action derived from sentence + records + rule is still "book the charge for the most recent miss when the rule makes it chargeable".

### override_declarations (rev 3)

- **missed:** the declared overwrites (agg_one_owner_per_home, appointment_charges) are unchanged and verbatim.
- **O6 (callback exemption vs base `warranty_callbacks`) is narrowed but not eliminated.** The new date test removes the revision-2 gap (a callback repair completed between the miss and the assessment now leaves the miss exempt, since the latest repair ≥ the miss date). Because the test reads the item's *latest* callback and *latest* repair rather than the callback and repair around the miss, two sequences still diverge from "fell while its claim item had an accepted callback awaiting repair" and from base "an accepted callback … carries no … fee":
  - (a) Miss during callback 1's open window, callback 1 repaired, then a second callback filed after the miss: latest callback > miss date, so the miss is charged although it fell during an open callback.
  - (b) Callback repaired before the miss, then another repair completed after the miss: latest repair ≥ miss date, so the miss is exempt although no callback was open.

  Neither task's world contains a callback-bearing miss (task 0's charged miss is on WSR-51592-01, which has no callback). **Latent; kept as observation O6.**
- **reinspection (O7):** the re-worded sentence makes the proxy unambiguous within the rule ("whichever claim items those denials concern"). What remains latent is its divergence from the base `parameter_schema` description of `reinspection_fee_usd` ("when an item already denied as within tolerance is re-reported"): an earlier same-category item that was *approved*, plus any unrelated within-tolerance denial, satisfies the proxy. Task 1's earlier concrete item WSR-55620-01 was itself denied within tolerance, so there is no case. **Kept as observation O7.** The wording part is addressed.
- finish, dispatch, systems: no undeclared override.

### factor_ladders (rev 3)

- Unchanged except active_buyer. Its ladder tier 2 now reads "holds no such agreement but holds a homesite reservation on hold and has a reservation deposit received on the homesite ledger within the last 12 calendar months". The rule, the ladder and the `buyer_mult` branch agree. Bindings: another_build, homesite_hold, hold_deposits, buyer_mult.
- Counts per policy (all within bounds):

  | policy | factors | parameter | method |
  | --- | --- | --- | --- |
  | missed | 4 | 3 | 1 |
  | finish | 5 | 4 | 1 |
  | reinspection | 6 | 5 | 1 |
  | dispatch | 6 | 5 | 1 |
  | systems | 6 | 5 | 1 |

- All ladders have at least 3 tiers with distinct outcomes, every tier stated in its rule, and every fall-through equal to its baseline.
- **O10 (observation; equally true of the round-1/2 wording, not raised then).** The deposit conjunct of active_buyer tier 2 is implied by its other conjunct. By the homesite charter, a reservation reaches `held` only when "the reservation deposit and any premium holding fee have been received in full", and a hold lasts at most `max_total_hold_days` (28 for Interior Homesite) plus a short reinstatement window. So every homeowner with a held reservation has a reservation deposit received within 12 months, and the conjunct does not divide customers. The factor still has three real tiers (agreement under construction / held reservation / neither) and bears weight. Each task's multi-source requirement is met by other factors (task 1: soil_movement, first_period). Observation only.

### findings (rev 3, charter-global)

| id | status in rev 3 |
| --- | --- |
| N1 | **closed** |
| N2 | **closed** |
| O6 | narrowed; latent residual kept (sequences a, b) |
| O7 | wording addressed; latent divergence from the parameter description kept |
| O8 | **closed** (the rule now decouples the deposit from the held reservation, and compute matches) |
| O1, O3, O5 | kept |
| O9, O10 | new observations; both latent, and both equally applicable to earlier revisions |

**No charter-level SOURCE-POLICY / SOURCE-FACTOR RED is open in revision 3.**

### closing_checklist (revision 3)

Written 2026-10-05T00:44Z, after both revision-3 reveals. Note: the session was interrupted after the charter-global section above. The per-task revision-3 sections were frozen afterwards and before any revision-3 GT was read; nothing was redone.

- Per-task files: `0.md` and `1.md` carry rounds 1 and 2 untouched plus `## revision_3`. Both revision-3 comparisons read **PASS** on all four relationships.
- Round-2 items:
  - N1 and N2 are **closed**.
  - O8 is **closed**.
  - O6 is narrowed (latent residual sequences only).
  - O7 wording is addressed (latent divergence from the parameter description only).
  - O1, O3 and O5 are kept.
  - New observations O9 and O10 are both latent and were equally present earlier.
- **No charter-level SOURCE-POLICY or SOURCE-FACTOR RED is open.**
- Coverage and scope: the revealed `charter_scope`s are disjoint and jointly cover all 5 extended policies. Task tools and uuid8s are unchanged and independent.
- Trees: task 0 has n = 1 and task 1 has n = 2; each has ≥ 1 value_input edge and an owner=user root. The difficulty-wide graph is acyclic.
- Factors:
  - Every computation has a baseline written into its rule that gives a definite non-gold number.
  - Every computation has 4–6 factors with ≥ 2 parameter and 1 honest method.
  - All 27 factors bear weight.
  - Each task has a multi-source and a cross-difficulty factor.
- Gates: the orchestrator's re-run on this form is cited (all correctness gates OK; TRACEABILITY deferred to KB publication). I did not re-run them.
- **Conclusion: this difficulty passes the source-layer audit at revision 3.**
