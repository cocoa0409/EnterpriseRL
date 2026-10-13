# Policy-task audit — test_orders_and_results / charter-global

## charter_global_frozen

- Scenario: `env/env_0028_clinical_laboratory_company`, difficulty `test_orders_and_results` (category `orders`), M=2.
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiate agent.
- Freeze time of this section: 2026-10-04T16:47Z (before any task GT was revealed; nothing in this section is derived from a revealed GT).
- Freeze hashes (sha256, recomputed by the auditor and equal to `audits/_views/policy_task/test_orders_and_results/HASHES.txt`):
  - `tasks/test_orders_and_results/orders.extended.yaml` = `853dfa819edd7da0182e4c37e315227e61dc2a639d926b1c9d2138af420e7e0b`
  - `tasks/test_orders_and_results/task_tools.py` = `d1ad76b872d60bef399a7e7b5e979c6a54bd1141c379f7166fc7fbf768360541`
- Fields read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (via the evaluator), `blueprint/share_tools.py`, `blueprint/products/{orders,visits,coverage,invoices,assistance}.yaml` (only the parameters the extended charter reads), `orders.extended.yaml`, `task_tools.py`, the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (primitive semantics only).
- Fields masked / not read: every `tasks/test_orders_and_results/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the instantiate worklog, `env/.../worklog.md`, any earlier audit.
- Entry conditions (Step 0): gate snapshot supplied with the brief — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred (KB not rendered). Masked views and HASHES.txt present; hashes verified equal. Entry conditions met (traceability deferral recorded as an observation, not a gap of this audit).
- Base-copy check: lines 1-1352 of `orders.extended.yaml` are byte-identical to `blueprint/products/orders.yaml` (diff differs only by one trailing blank line).

### policy_conflict_scan

Extended policies (5): `orders_ext_recollection_window` (agent, `request_specimen_recollection_7c5f4bb7`, computes `recollection_window_days`), `orders_ext_genetic_self_pay_quote` (agent, `issue_genetic_self_pay_quote_0325000c`, `quote_amount`), `orders_ext_genetic_cancellation_fee` (user, `cancel_genetic_test_order_d90cc330`, `handling_fee_amount`), `orders_ext_reference_self_pay_estimate` (agent, `issue_reference_test_estimate_b0801821`, `estimate_amount`), `orders_ext_reference_cancellation_fee` (user, `cancel_reference_test_order_ed257856`, `handling_fee_amount`).

- Overlapping subjects: the two estimate policies both write `orders_estimate_issued` (same fields `good_faith_estimate_amount`, `estimate_date`), but each is scoped by class in its own first sentence ("an accession of the Hereditary & Reproductive Genetic Testing class that is billed self_pay" / "an accession of the Esoteric Reference Testing class that is billed self_pay"); no accession falls under both. The two cancellation policies are likewise class-scoped. No overlap of trigger/object.
- Eligibility / time anchors: every extended policy inherits the base eligibility of its refs (recollection offered only below `max_no_charge_recollections`; GFE only for self_pay or no-active-coverage patients; patient cancellation only from received/info_hold/accessioned/testing_hold). No extended sentence contradicts an inherited eligibility. Time anchors: `gfe_valid_days` (both cancellation policies count estimate age against today), rejection date day 0 (recollection), received_date (stage/batch multipliers), 12 / 24 months windows (cross reads). Compatible.
- Terminal states: cancellation tools set status cancelled + credits + one fee line; estimate tools overwrite the order's estimate fields; recollection tool adds one request line. Compatible.
- Cross-category read boundaries: reads only (visits, coverage, invoices, assistance); no extended policy writes outside `orders` / `order_events`.
- One conflict with base found — see `override_declarations` F-CG-1 (base GFE sentence "a new estimate replaces the old one on every order of the encounter" vs. the extended "written to that accession only").
- Scope exclusivity (structure only, pre-reveal): the `prerequisite` graph has exactly two weakly connected components — {genetic_cancellation_fee <- genetic_self_pay_quote, genetic_cancellation_fee <- recollection_window} and {reference_cancellation_fee <- reference_self_pay_estimate}. With M=2 these are the only two trees that cover all five policies disjointly; whether the tasks actually claim them is checked after the reveal (closing_checklist).

### rule_compute_equivalence

Verbatim checks (auditor script, whitespace-normalised): every `policy_source`, every `overwrite.replaced_by` and every `baseline.rule` sentence is a substring of its policy's `rule`; every `superseded_clause` is a substring of the named base rule; every `compute_basis` entry is verbatim in the rule except `orders_ext_reference_self_pay_estimate.compute_basis.result`, which splices two non-adjacent passages (each passage is verbatim; observation O-CG-5).

Per policy, sentence-by-sentence sweep (rule -> compute and compute -> rule):

- `orders_ext_recollection_window`: class window `P('recollection_window_days')`; most recent rejection via `LATEST(... event_type='orders_specimen_rejected')`; weekday by `DAYS(K('reference_monday'), rejection_date) % 7` (2024-01-01 is a Monday; implementation constant, not a business basis); cause lengthening 7/3/0; home-visit lengthening 10/5/0; fasting 3/2/0 (12-h tests 7600/36169, 8-h 10231 — consistent with base test_menu fasting_hours); additive build; second-offer factor 0.75 / 0.5 with `int()` floor; cap `requisition_valid_days - DAYS(order_date, rejection_date)`. Equivalent, with two edge observations: "a test ... is charged on the accession" is computed over `orders_test_charge_posted` only (an add-on line of 7600/36169/10231 and a credited line are treated differently from the plain rule reading — O-CG-1), and "the Halverson collection visit recorded for the accession" is read by `EXISTS/CFIELD(... order_id=HID, status='collected')`, which takes the first collected visit when an accession has several (O-CG-2).
- `orders_ext_genetic_self_pay_quote`: standing tests = ordered lines minus credited lines per test code; bundling 1.0 / 0.5 / 0.25 on non-top tests; redraw 0.10/0.05/0; prompt-pay = Self-Pay Patient Invoice `prompt_pay_discount_pct` (15, invoices.yaml) / 0.05 / 0 over `XCOUNT(..., within_months=24)`; coverage 0.10 / 0.05 / 0; rates summed then applied once; round at the end. Equivalent.
- `orders_ext_genetic_cancellation_fee`: fee basis (quote_share x current quote / 0 for patient_billing_prohibited_except_copay payer / class fee); stage multiplier; extra-test amount; authorization reduction; courtesy (no_show_fee + late_cancellation_fee in 12 months, collected visit); assistance rate; floor at zero, then assistance, round at the end; zero when cancelled before accession. One divergence — F-CG-2: `standing_tests` subtracts every credit line of the accession, while the rule counts "tests stand on the accession with an ordered charge line and no credit".
- `orders_ext_reference_self_pay_estimate`: standing tests = ordered + add-on - credited per test code; multi-test 0.12/0.04/0; coverage-loss 0.20/0.05/0; assistance discount_pct / 0.10 / 0; collection-service amount added after reduction; round at the end. One divergence — F-CG-3: rule "when the patient's only assistance case is under_review" vs compute `EXISTS('assistance', status='under_review')` (no "only"). Observation O-CG-3: `CFIELD('coverage','termination_date')` reads the first coverage when several are on file, the rule says "the patient's coverage on file".
- `orders_ext_reference_cancellation_fee`: starting amount (estimate_share x estimate current and dated on/after the latest add-on / 0 / class fee); batch multiplier 0.5 / 0.8 / 1.0; aliquoting 6/3/0 over ordered + add-on - credited; retrieval 8/4/0; payment courtesy 5/2/0; apology 5/2/0; floor; round. One divergence — F-CG-4: `add_ons_standing = COUNT(... orders_add_on_posted)` counts credited add-on lines, while the rule says "When two accepted add-on lines stand on the accession" and the same rule defines standing as "not credited".

### action_binding_and_uuids

- `(target_tool, computes)` pairs: five distinct pairs, each claimed by exactly one extended policy; no base policy names a target tool.
- Docstrings: none names another tool or another problem, none states a position in a cross-problem sequence. Literal ordering words do occur — "before testing starts" (both cancel tools, restating base eligibility), "After the call ..." (all five, describing the visible effect), "already rounded to the cent before it is passed" (estimate tools). None carries a cross-problem order (observation O-CG-6).
- Function bodies: no tool reads status, hold, estimate, recollection or any precondition to refuse or warn; each performs its write unconditionally (recollection: anchors on the rejection's own event_date; cancel tools: credit ordered/reflex/add-on lines not yet credited, post a fee line when > 0, set cancelled). The tool layer judges no prerequisite.
- uuid8s: `7c5f4bb7`, `0325000c`, `d90cc330`, `b0801821`, `ed257856` — pairwise distinct, no shared prefix/suffix, no sequential pattern. Cross-difficulty reuse could not be checked (sibling difficulties' tasks dirs are outside the read domain); blueprint/share_tools.py contains none of them.

### prerequisite_graph

- `prerequisite` present on all five policies (`[]` on recollection_window, genetic_self_pay_quote, reference_self_pay_estimate).
- Edges: E1 genetic_cancellation_fee -> genetic_self_pay_quote (value_input, gate `quote_amount`, form state); E2 genetic_cancellation_fee -> recollection_window (state_gate, gate `order_events.rejected_event_id`, form state); E3 reference_cancellation_fee -> reference_self_pay_estimate (value_input, gate `estimate_on_file`, form state). All `problem` ids are extended ids of this file, none self-referential; graph acyclic.
- `policy_source` verbatim in the blocked policy's own rule: E1, E2, E3 all True.
- `form: state` on all three; no `fallback_reason` — consistent.
- `resolved_by` = the depended-on policy's `target_tool` on all three; the tool effect makes the waited-on state hold (E1/E3: writes `good_faith_estimate_amount` + `estimate_date`=today; E2: writes an `orders_recollection_requested` line with `rejected_event_id`).
- `kind`/`gate`: `quote_amount` and `estimate_on_file` exist as compute bindings. E2's gate names a field (`order_events.rejected_event_id`) rather than an eligibility entry (extended policies carry no `eligibility` list); the gate is the rule sentence itself — observation O-CG-7.
- `condition` vs sentence: E1 condition omits the sentence's scope "For a genetic accession billed to the patient directly" and accepts any `good_faith_estimate_amount` rather than "a genetic self-pay quote" (slightly broader; observation O-CG-8). E2 and E3 conditions match their sentences in strength and scope.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

- E1: "For a genetic accession billed to the patient directly, the handling fee is fixed only after a genetic self-pay quote dated within the estimate validity period of the class stands on the accession." Connective "only after"; waited-on state is record-visible (an estimate amount with an estimate date within `gfe_valid_days` on the order); no tool, id or snake_case token. Single write: only `orders_ext_genetic_self_pay_quote` issues "a genetic self-pay quote" (the reference estimate tool writes the same fields but is scoped to reference-testing orders by its policy and docstring). Derivation: a reader sees no current estimate on a self-pay genetic order -> the rule that "fixes the genetic self-pay quote" is the only rule producing that state -> issue it -> fee basis reads it. One reading.
- E2: "A cancellation of a genetic accession is booked only after every specimen rejection recorded on the other accessions of the same requisition is answered by a recollection request on file, so that the cancellation notice ... lists every collection still owed on the requisition." Connective "only after"; state "every rejection ... answered by a recollection request on file" is record-visible (`rejected_event_id` link); no tool/id. Single write: only `request_specimen_recollection_7c5f4bb7` creates `orders_recollection_requested` lines. One reading. Observation O-CG-4: the sentence is open over "every specimen rejection recorded on the other accessions", including rejections for which base `orders_evt_specimen_rejection` forbids a request ("When no recollection is offered ... no request line is written"); in such a world the gate can never open.
- E3: "For a reference-testing accession billed to the patient directly, the handling fee is not fixed until a reference-testing self-pay estimate dated within the class's estimate validity period, and no earlier than the last add-on test accepted on the accession, stands on it." Connective "not ... until"; state record-visible (estimate date vs latest add-on event_date); single write `issue_reference_test_estimate_b0801821`. One reading.
- Depended-on rules (recollection_window, genetic_self_pay_quote, reference_self_pay_estimate) do not restate any sentence of the blocked rules and name no other problem.
- Undeclared cross-problem orders: none found in any extended rule. Base rules carry orders between non-extended events only (ABN/prior-auth/billing switch/holds); the base GFE sentence "when an add-on test is accepted on a self-pay order ... a new estimate replaces the old one" orders an add-on (not an extended problem) before an estimate and grounds no edge — observation.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- `orders_ext_recollection_window` vs `orders_evt_specimen_rejection`: specimen type, rejection criteria, return to received + notice, offer condition, "When no recollection is offered ...", lapse cancellation — followed. "When a recollection is offered, one orders_recollection_requested line is written ... recollect_by_date equal to the rejection date plus recollection_window_days ..." — handled differently, declared in `overwrite`. Merged semantics unique.
- `orders_ext_genetic_self_pay_quote` and `orders_ext_reference_self_pay_estimate` vs `orders_agg_requisition_encounter`: the GFE-per-encounter clause (through "written to every order of the encounter") — declared. Encounter definition, class split, oversight fee — followed.
- same two vs `orders_evt_good_faith_estimate`:
  - S1 "A good faith estimate is issued only for an order billed self_pay or for a patient with no active coverage on file." — followed (extended scope narrower: billed self_pay; observation O-CG-9 — an insurance-billed genetic/reference order of a patient with no active coverage is still GFE-eligible under S1 while both base amount clauses are superseded by policies scoped to self_pay billing).
  - S2 issuance timing — followed.
  - S3 "The amount follows the requisition-encounter rule." — declared.
  - S4 "An estimate applies to a collection made within gfe_valid_days ...; when an add-on test is accepted on a self-pay order, or the estimate has lapsed before collection, a new estimate replaces the old one on every order of the encounter." — **handled differently, not declared** (F-CG-1).
  - S5 insured patients billing their plan — followed.
- `orders_ext_genetic_cancellation_fee` and `orders_ext_reference_cancellation_fee` vs `orders_evt_patient_cancellation`: S1 cancellable statuses — followed (the extended E2 gate adds a further necessary condition, not a contradiction); S2 patient confirms — declared (refined); S3 credit every uncredited charge/add-on — followed (tool does it); S4 handling fee — declared; S5/S6 consumer orders — followed. vs `orders_agg_requisition_encounter`, `orders_order_intake`: list_price_total arithmetic, intake rules — followed by the tools.
- Disguised forms: no anonymous intermediate overriding a base quantity outside the declared clauses; the 0 fee basis (patient_billing_prohibited_except_copay payer) acts on a quantity whose base sentence is already superseded; no dropped base branch in the cancellation policies (pre-accession cancellation -> 0 kept by `cancelled_after_accession` / `fee_applies`). No author note calls a base output "wrong".

### factor_ladders

Per policy (label as declared -> auditor's classification):

- `orders_ext_recollection_window` (5 declared): rejection_cause parameter (7/3/0; tiers 1-2 multi-source: order_events rejection reason AND visits row; cross_difficulty visits); home_visit_booking parameter (10/5/0; cross visits; both conditions on one visit row); fasting_requirement parameter (3/2/0); weekend_rejection parameter (2/1/0); second_offer declared **method** -> tiers `int(built x 0.75)`, `int(built x 0.5)`, `built` (= `int(built x 1)` since built is an integer) — one formula with a different rate: **parameter** (F-CG-5). Surviving counts: 5 factors, 5 parameter, **0 method**. All ladders >= 3 disjoint tiers, distinct outcomes, every tier stated in the rule and implemented in compute; fall-through = baseline on every factor.
- `orders_ext_genetic_self_pay_quote` (4 declared): test_bundling declared **method** -> tiers `top + 0.25 x (listed - top)`, `top + 0.5 x (listed - top)`, `listed` (= `top + 1.0 x (listed - top)`): one formula with a different share: **parameter** (F-CG-5); redraw_courtesy parameter (0.10/0.05/0); prompt_pay_record parameter (15%/5%/0; cross invoices; multi-source over distinct transaction rows) — **unreal ladder** (F-CG-6); coverage_standing parameter (0.10/0.05/0; tier 2 multi-source coverages.status AND orders.prior_auth_status; cross coverage). Surviving: at most 3 factors (prompt_pay_record struck), **0 method**.
- `orders_ext_genetic_cancellation_fee` (6 declared): fee_basis_source method (quote_share x quote / 0 / class fee — three different base quantities: genuine method; tiers 1-2 multi-source; cross coverage); processing_stage declared **method** -> `basis x 0.6`, `basis x 0.25`, `basis x 1.0`: **parameter** (F-CG-5); extra_tests parameter (20/10/0); authorization_outcome parameter (15/5/0; multi-source orders.prior_auth_status AND coverages.status; cross coverage); appointment_courtesy parameter (8/4/0; cross visits; multi-source fee rows AND collected visit); assistance_award parameter (1.0 / discount_pct / 0; cross assistance). Surviving: 6 factors, 5 parameter, 1 method — counts met; mislabel recorded.
- `orders_ext_reference_self_pay_estimate` (4 declared): multi_test_count parameter (0.12/0.04/0); coverage_loss parameter (0.20/0.05/0; cross coverage) — **tier-2 conjunct restates the policy's scope** (F-CG-7); assistance_position parameter (discount_pct / 0.10 / 0; cross assistance); home_collection_share method (all net visit fees / (net trip + weekend) / (1 + household) / nothing — genuine method; cross visits). Surviving: 3 factors if coverage_loss is struck (below the floor of 4); 1 method.
- `orders_ext_reference_cancellation_fee` (6 declared): starting_amount_source method (estimate_share x estimate / 0 / class fee — genuine; tiers multi-source; cross coverage); batch_stage declared **method** -> `start x 0.5`, `start x 0.8`, `start x 1.0`: **parameter** (F-CG-5); aliquot_count parameter (6/3/0); add_on_retrieval parameter (8/4/0); payment_standing parameter (5/2/0; cross invoices); correction_apology parameter (5/2/0). Surviving: 6 factors, 5 parameter, 1 method — counts met; mislabel recorded.
- Distinct outcomes: no ladder has two tiers selecting the same value or method. Every tier is stated in the rule (condition and value/method) and is a branch of the `decides` binding; no tier lives only in compute.
- Realism: every condition is one a clinical laboratory plausibly weighs for the quantity, except F-CG-6 and F-CG-7; borderline items recorded as observations O-CG-10 (reference payment_standing), O-CG-11 (coverage_loss fall-through for never-insured patients).
- Per-task cross-difficulty / multi-source availability: tree {genetic cancel, genetic quote, recollection} offers cross reads of visits, invoices, coverage, assistance and multi-source factors (rejection_cause, coverage_standing, authorization_outcome, fee_basis_source); tree {reference cancel, reference estimate} offers coverage, assistance, visits, invoices and multi-source factors (starting_amount_source, payment_standing). Whether each is seeded is per task.

### findings

- **F-CG-1 — SOURCE-POLICY RED (undeclared override).** Symptom: base `orders_evt_good_faith_estimate` S4 "when an add-on test is accepted on a self-pay order, or the estimate has lapsed before collection, a new estimate replaces the old one on every order of the encounter" is not named in any `overwrite`, while `orders_ext_genetic_self_pay_quote` and `orders_ext_reference_self_pay_estimate` both state "the quote amount and the issue date are written to that accession only" / "the estimate amount and the issue date are written to that accession only". Same situation, two conclusions: a self-pay reference accession whose requisition also carries a self-pay sibling order with an estimate, after an add-on is accepted — base S4: the new estimate replaces the old one on the sibling as well; extended: the sibling's estimate is untouched. Root cause: only the requisition-encounter clause and S3 were declared. Affected: `orders.extended.yaml` `orders_ext_genetic_self_pay_quote.overwrite`, `orders_ext_reference_self_pay_estimate.overwrite`. Bears on: task 0 (genetic quote) and task 1 (reference estimate) — consequence demonstrated per task.
- **F-CG-2 — SOURCE-POLICY RED (rule/compute divergence).** `orders_ext_genetic_cancellation_fee`: rule "When three or more tests stand on the accession with an ordered charge line and no credit, extra_test_fee_three is added ...; when exactly two such tests stand, extra_test_fee_two is added"; compute `standing_tests: COUNT(... charge_reason='ordered') - COUNT(... event_type='orders_test_charge_credited')`. Situation: two uncredited ordered tests plus one add-on line credited as duplicate_test (genetic class allows 1 add-on) — rule: 2 tests stand -> +10.00; compute: 2 - 1 = 1 -> +0.00. Affected: compute binding `standing_tests`. Bears on task 0.
- **F-CG-3 — SOURCE-POLICY RED (rule/compute divergence).** `orders_ext_reference_self_pay_estimate`: rule "when the patient's only assistance case is under_review, with no decision yet, the assistance rate is provisional_assistance_rate"; compute `case_under_review: EXISTS('assistance', status='under_review')`. Situation: one denied case and one under_review case — rule: not the only case -> 0; compute: 0.10. Affected: compute binding `case_under_review`. Bears on task 1.
- **F-CG-4 — SOURCE-POLICY RED (rule/compute divergence).** `orders_ext_reference_cancellation_fee`: rule "When two accepted add-on lines stand on the accession, add_on_retrieval_two is added ...; when one stands, add_on_retrieval_one is added", where the same rule defines standing as "accepted add-on lines not credited"; compute `add_ons_standing: COUNT('order_events', event_type='orders_add_on_posted')`. Situation: two add-ons posted, one later credited duplicate_test — rule: one stands -> 4.00; compute: 2 -> 8.00. Affected: compute binding `add_ons_standing`. Bears on task 1.
- **F-CG-5 — SOURCE-FACTOR RED (mislabelled effect).** Four factors labelled `method` only substitute a number into one formula: recollection `second_offer` (floor(built x f), f = 0.75 / 0.5 / 1), genetic quote `test_bundling` (top + s x (listed - top), s = 0.25 / 0.5 / 1), genetic cancel `processing_stage` (basis x m, m = 0.6 / 0.25 / 1.0), reference cancel `batch_stage` (start x m, m = 0.5 / 0.8 / 1.0). Consequence: `orders_ext_recollection_window` and `orders_ext_genetic_self_pay_quote` have no honest `method` factor (floor: 1). Bears on task 0 (all three of its policies) and task 1 (reference cancel).
- **F-CG-6 — SOURCE-FACTOR RED (unreal ladder).** `orders_ext_genetic_self_pay_quote.prompt_pay_record`: tier 2 "at least one payment received AND at least one payment reversed in those 24 months" -> 5%, fall-through "any other payment record" -> 0. A patient with one clean payment and no reversal gets 0%, a patient whose only payment was reversed (bounced) gets 5% off the quote: a laboratory does not publish a better self-pay price as the treatment for a returned payment than for a clean one. Struck, the policy keeps 3 factors (floor 4). Bears on task 0.
- **F-CG-7 — SOURCE-FACTOR RED (condition restates the scope).** `orders_ext_reference_self_pay_estimate.coverage_loss` tier 2 "an active coverage on file AND the accession is billed self_pay": the policy's scope sentence is "the good faith estimate written on an accession of the Esoteric Reference Testing class that is billed self_pay" (and base S5 denies a GFE to insured patients billing their plan), so the conjunct "billed self_pay" holds of every customer reaching this write and divides no one. Struck, the policy keeps 3 factors (floor 4). Bears on task 1.

Observations (no demonstrable consequence on the charter alone):

- O-CG-1 recollection fasting counts only `orders_test_charge_posted` lines (add-on lines of 7600/36169/10231 ignored, credited lines counted) where the rule says "charged on the accession".
- O-CG-2 recollection / reference-estimate visit reads take the first collected visit of the accession; the rule speaks of "the" visit.
- O-CG-3 reference estimate `coverage_end` reads the first coverage row on file.
- O-CG-4 E2 sentence is open over rejections that base forbids answering; such a world would make the genetic cancellation permanently unbookable.
- O-CG-5 reference estimate `compute_basis.result` splices two non-adjacent rule passages.
- O-CG-6 tool docstrings carry literal ordering words ("before testing starts", "After the call", "before it is passed"), none stating a cross-problem order.
- O-CG-7 E2 `gate` names a field rather than an eligibility entry.
- O-CG-8 E1 `condition` broader than its sentence (no self-pay scope, any estimate).
- O-CG-9 base GFE S1 still makes insurance-billed orders of no-active-coverage patients GFE-eligible, while both amount clauses are superseded by self_pay-scoped policies (gap, not a conflict).
- O-CG-10 reference cancel `payment_standing` gives a $2 courtesy to a patient with a reversed payment and $0 to one with no payment history — borderline business reading.
- O-CG-11 reference estimate `coverage_loss` fall-through gives a never-insured self-pay patient 0% while a recently lapsed one gets 20% — borderline business reading.
- O-CG-12 base parameter descriptions (`recollection_window_days`, `cancellation_handling_fee_after_accession`, `good_faith_estimate_amount` "for the whole requisition encounter") still describe the base meaning; the extended rules relabel them "standard". Not sentences of a cited base policy.
- O-CG-13 check_traceability deferred (KB not rendered) — the gate set is incomplete until the KB exists.

## closing_checklist

Written after both task reveals (2026-10-04T16:52Z); nothing above this heading was changed after any reveal.

- Per-task files correspond one-to-one with the tasks: `0.md` (task 0), `1.md` (task 1), alongside this file. First revision; no older revision exists.
- Comparison sections: both carry a full `source_gt_comparison`; the independent derivations equal GT on every write, argument, owner, order and terminal state. Neither carries an overall PASS: both carry SOURCE-POLICY RED (charter-global, no consequence on their scored values) and SOURCE-FACTOR RED.
- Coverage and scope (checked against the revealed `charter_scope`): task 0 = {orders_ext_recollection_window, orders_ext_genetic_self_pay_quote, orders_ext_genetic_cancellation_fee} with tools {request_specimen_recollection_7c5f4bb7, issue_genetic_self_pay_quote_0325000c, cancel_genetic_test_order_d90cc330}; task 1 = {orders_ext_reference_self_pay_estimate, orders_ext_reference_cancellation_fee} with {issue_reference_test_estimate_b0801821, cancel_reference_test_order_ed257856}. Pairwise disjoint, jointly cover all five extended policies and all five task tools; each scope spans its whole tree. uuid8s independent (see § action_binding_and_uuids).
- Problem trees: task 0 — 2 prerequisite problems, 1 value_input edge (floor 1), owner=user root; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user root. Whole-difficulty graph acyclic, no cross-task edge.
- Factors: every declared factor bears weight on its task's world against an honest baseline, and every whole baseline gives a definite number different from gold (recollection 14 vs 13; quote 548.00 vs 313.95; genetic fee 150.00 vs 33.17; reference estimate 495.00 vs 334.60; reference fee 25.00 vs 30.77). **Not met:** honest `method` factor missing in `orders_ext_recollection_window` and `orders_ext_genetic_self_pay_quote`, two further `method` labels dishonest (F-CG-5); `prompt_pay_record` ladder unreal (F-CG-6) and `coverage_loss` tier restating scope (F-CG-7), which drop the genetic quote and the reference estimate below 4 surviving factors.
- Policy self-consistency: **not met** — F-CG-1 (undeclared override of base GFE S4), F-CG-2, F-CG-3, F-CG-4 (rule/compute divergences). None changes a scored value in either task world.
- Gate re-run on the final form: not performed — the difficulty does not reach closing (four relationships do not all PASS); the brief's gate snapshot is cited in § charter_global_frozen, with check_traceability still deferred.
- Difficulty result: **does not pass the source-layer audit.** Problem tree and unique solution PASS for both tasks; SOURCE-POLICY RED and SOURCE-FACTOR RED for both.

## revision_2

Round-2 re-audit. Everything above this heading is the round-1 text, left untouched. This section was written before any round-2 task GT was read and contains nothing derived from a round-2 GT.

### charter_global_frozen (revision_2)

- Freeze time: 2026-10-04T17:50Z (system clock read 17:43:38Z at start of the round). Auditor: same independent auditor as round 1.
- Hashes (recomputed, equal to the round-2 HASHES.txt): `orders.extended.yaml` `55509afa95d0d01e7938b7e42fe7c1c7bdb0815475b00746f55e4db7dc2242fa` (round 1: `853dfa81...`, changed); `task_tools.py` `1cddb81e21915e2e95e8c3ef815eb082826f23a0b333d7a14620bfa7fcd9c295` (round 1: `d1ad76b8...`, changed). Both shared inputs moved, so every charter-global section is re-derived in full below rather than carried forward.
- Views: `task0.view.json` `edf627ec...` and `task1.view.json` `1d145d0b...` — identical to round 1 (the task worlds, personas and clocks did not change).
- Base copy: lines 1-1352 still identical to `blueprint/products/orders.yaml` (one trailing blank line differs).
- Entry conditions: round-2 gate snapshot supplied (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred). Met.
- Masked: `tasks/*.json` (round-2 content), worklogs. Disclosure: the auditor read the round-1 GT of both tasks in round 1 (recorded in `0.md` / `1.md`); no round-2 GT was read before this section and the task freezes below.

### policy_conflict_scan (revision_2)

Unchanged in structure: five extended policies, same targets, same class scoping, same two prerequisite components. Changes found and checked: the two estimate policies now each supersede base GFE S4 with a class-scoped replacement ("on that accession only" / "on that accession alone"); recollection second-offer arithmetic; genetic quote prompt-pay restructured; genetic fee test count; E2 narrowed to rejections "still offered a no-charge recollection"; reference estimate coverage-loss and assistance tiers rewritten; reference fee retrieval and courtesy tiers rewritten; tool docstrings reworded. No new overlap of subject, trigger or object; no new cross-category write.

### rule_compute_equivalence (revision_2)

Verbatim script: every `policy_source`, `replaced_by`, `superseded_clause` (including the two new S4 clauses, substrings of the base GFE rule) and `baseline.rule` sentence locates; every `compute_basis` entry is now verbatim in its rule (the round-1 splice in the reference estimate `result` is gone).

- Recollection: fasting now "stands on the accession as an ordered or add-on line that has not been credited" = compute (ordered + add-on - credited per code) — O-CG-1 closed. Second offer: tier "every earlier rejection collection-related" = `MX(minimum_window_days, built - DAYS(latest earlier request, rejection_date))`; tier "a transport-related earlier rejection" = `built + DAYS(rejection_date, NOW)`; first offer = built. Equivalent. Fasting ladder text in `factors` still reads "is charged on the accession" while rule and compute use the uncredited-standing reading (O-R2-4, descriptive text only).
- Genetic quote: rates (redraw + coverage) applied once to the priced amount; prompt-pay reduction subtracted after, as 15% of the priced amount (>= 2 payments, no reversal) or a 10.00 credit (exactly 1 payment, no reversal), else 0. Equivalent.
- Genetic fee: `standing_tests` = per class test number, ordered + add-on - credited = rule "counting the ordered charge lines and accepted add-on lines of the class's test numbers that have not been credited". **F-CG-2 closed.**
- Reference estimate: assistance tier 2 now "when no approved award covers the estimate date and the patient has an assistance case under_review" = compute. **F-CG-3 closed.** Coverage-loss tiers = compute (`EXISTS active`, `CFIELD variant_name status=active`); with several active coverages the first is read (O-R2-3, replaces O-CG-3).
- Reference fee: rule now "When two add-on lines have been posted on the accession, whether or not either was later credited ..." = `COUNT(orders_add_on_posted)`. **F-CG-4 closed.** Courtesy tiers (>= 2 / exactly 1 payment, no reversal) = compute.
- No new divergence found.

### action_binding_and_uuids (revision_2)

Five `(target_tool, computes)` pairs unchanged and unique. uuid8s unchanged and independent. Docstrings: the only remaining ordering word is "after the prefix rcq_" (a format description); "while testing has not started" and "On success" replace the round-1 wording — O-CG-6 closed. Function bodies unchanged in effect; no tool refuses or checks a prerequisite.

### prerequisite_graph (revision_2)

Same three edges, acyclic, `policy_source` verbatim in the blocked rule, state form, `resolved_by` = target tools. E1 condition now "on a genetic accession billed self_pay, orders.good_faith_estimate_amount holds a genetic self-pay quote ..." — matches its sentence's scope (O-CG-8 closed). E2 condition now restricted to rejections "for which a no-charge recollection is still offered (the accession's recollection count below max_no_charge_recollections and no new requisition required)" — matches the reworded sentence. E2 gate still a field name (O-CG-7, left as recorded).

### prerequisite_sentences (revision_2)

- E1, E3 unchanged; four-point test and single writer as in round 1.
- E2 now: "A cancellation of a genetic accession is booked only after every specimen rejection recorded on the other accessions of the same requisition that is still offered a no-charge recollection is answered by a recollection request on file, ...". Connective "only after"; state record-visible (offer status derivable from the base offer condition; request link via `rejected_event_id`); no tool/id; single writer `request_specimen_recollection_7c5f4bb7`. The round-1 unsatisfiable case (rejections base forbids answering) is now excluded — O-CG-4 closed.
- No sentence restated on the depended-on side; no undeclared cross-problem order in any extended rule.

### override_declarations (revision_2)

- Base GFE S4 "when an add-on test is accepted on a self-pay order, or the estimate has lapsed before collection, a new estimate replaces the old one on every order of the encounter." is now named in `overwrite` of both `orders_ext_genetic_self_pay_quote` and `orders_ext_reference_self_pay_estimate`, each replaced by a class-scoped sentence present in its rule. **F-CG-1 closed** for the two classes this difficulty governs. Observation O-R2-1: both replacements are class-scoped, so for an estimate on any other class (e.g. a self-pay Routine order receiving an add-on) the KB carries a superseded base sentence and no replacement; no extended policy of this difficulty writes such an estimate and no task world contains one.
- All other sentence-by-sentence conclusions of round 1 stand unchanged (no other base ref sentence moved).

### factor_ladders (revision_2)

- Recollection (5): rejection_cause, home_visit_booking, fasting_requirement, weekend_rejection parameter; second_offer **method** — tiers now compute different quantities (built less elapsed days since the earlier request, floored at 1; built plus days from rejection to today; built as is), not one formula with a different rate. Honest. Counts 4 parameter + 1 method. **F-CG-5 closed for recollection.**
- Genetic quote (4): test_bundling now labelled parameter (honest); redraw_courtesy, coverage_standing parameter; prompt_pay_record **method** — percentage of the priced amount vs fixed 10.00 credit vs none: different algorithms. Ladder now 15% (>= 2 clean payments) / 10.00 (exactly 1 clean payment) / 0 (none or any reversal) — a returned payment no longer earns a better treatment than a clean one. **F-CG-5 and F-CG-6 closed.** Counts 3 parameter + 1 method.
- Genetic fee (6): processing_stage now parameter (honest); fee_basis_source method. Counts 5 + 1. **F-CG-5 closed.**
- Reference estimate (4): coverage_loss tiers now "no active coverage (never insured or coverage ended)" -> 0.20 / "active Commercial Out-of-Network Plan coverage" -> 0.10 / other -> 0; no conjunct restates the scope, never-insured patients are no longer worse off than lapsed ones. **F-CG-7 closed**, O-CG-11 closed. assistance_position tier 2 now "no approved award covers the estimate date AND a case under_review". home_collection_share method. Counts 3 + 1, total 4.
- Reference fee (6): batch_stage now parameter (honest); starting_amount_source method; payment_standing now 5.00 (>= 2 clean) / 2.00 (exactly 1 clean) / 0 (none or any reversal) — O-CG-10 closed; add_on_retrieval counts every posted add-on ("specimen retrievals already made"). Counts 5 + 1.
- Every ladder >= 3 disjoint tiers, distinct outcomes, stated in the rule and implemented in compute, fall-through = baseline. No condition restating scope found; no tier outcome found that the business would not publish.
- Observation O-R2-2: recollection tier "clock not restarted" floors at `minimum_window_days` 1 counted from the rejection date; when the earlier request is long past, the recollect-by date this writes can already lie before the day of writing, which base `orders_evt_specimen_rejection` treats as lapsed ("the laboratory cancels the order on the following day"). No task world reaches that floor.

### findings (revision_2)

Round-1 REDs:
- F-CG-1 — closed (both S4 overrides declared; replacement sentences in the rules).
- F-CG-2 — closed (genetic test count filtered per class test number and uncredited).
- F-CG-3 — closed (rule rewritten to match compute).
- F-CG-4 — closed (rule rewritten to match compute; the rewritten tier is a plausible business treatment).
- F-CG-5 — closed (four labels changed to parameter; recollection and genetic quote each gained a genuine method factor).
- F-CG-6 — closed (prompt-pay ladder rewritten; perverse ordering removed).
- F-CG-7 — closed (coverage-loss tiers rewritten; no scope restatement).

Round-1 observations: O-CG-1, O-CG-3 (superseded by O-R2-3), O-CG-4, O-CG-5, O-CG-6, O-CG-8, O-CG-10, O-CG-11 closed; O-CG-2, O-CG-7, O-CG-9, O-CG-12, O-CG-13 stand as recorded.

New charter-global REDs: none. New observations: O-R2-1 (class-scoped S4 replacements leave other classes without a replacement sentence), O-R2-2 (recollection floor can yield an already-lapsed recollect-by date), O-R2-3 (first active coverage read when several are active), O-R2-4 (fasting ladder text not updated to the "standing" wording).

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-04T17:47Z); nothing in § revision_2 above this heading was changed after a reveal.

- Per-task files `0.md`, `1.md` correspond one-to-one with the tasks, each with round-1 text preserved and a `revision_2` section; both revision_2 comparisons carry PASS on all four relationships.
- Coverage and scope: task 0 = {recollection_window, genetic_self_pay_quote, genetic_cancellation_fee}, task 1 = {reference_self_pay_estimate, reference_cancellation_fee}; pairwise disjoint, jointly complete over the five extended policies and five task tools; uuid8s independent and unchanged.
- Problem trees: task 0 — 2 prerequisites, 1 value_input, owner=user root; task 1 — 1 prerequisite, 1 value_input, owner=user root; whole graph acyclic.
- Factors: every computation has a self-sufficient baseline giving a definite number different from gold (14 / 548.00 / 150.00 / 495.00 / 25.00), 4-6 honest factors with >= 2 parameter and >= 1 genuine method, every ladder real and stated in full in its rule, every factor bearing weight on its world; each task has multi-source and seeded cross-difficulty factors.
- Policy self-consistency: F-CG-1..F-CG-4 closed; no new divergence or undeclared override.
- Gates re-run by the auditor on the final form (hashes `55509afa...` / `1cddb81e...`): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. check_traceability still deferred to KB publication (O-CG-13).
- Remaining observations (not grounds for rework): O-CG-2, O-CG-7, O-CG-9, O-CG-12, O-CG-13, O-R2-1..O-R2-4; task 0 observations 5, 6; task 1 observations 5, 6.
- Difficulty result (revision_2): **passes the source-layer audit** — all four relationships PASS for both tasks.

## revision_3

Round-3 re-audit, triggered by the render-layer notes P1 and P2 (`audits/policy_kb/test_orders_and_results/0.md` § bijection_verdict, `1.md` line 62 — read for context only; only their P1/P2 lines, section headings and E1/E4 note lines were read, and those carry no task gold values). Round-1 and round-2 text above is untouched. This section was written before any round-3 task GT was read.

### charter_global_frozen (revision_3)

- Clock at start: 2026-10-04T19:08:04Z. Hashes (recomputed = round-3 HASHES.txt): `orders.extended.yaml` `9cf73fc883f70577496078736d906624bff843b32aeedad1768e8d9af1032bdb` (changed from round 2 `55509afa...`); `task_tools.py` `1cddb81e...` (unchanged from round 2); views `edf627ec...`, `1d145d0b...` (unchanged). Because the charter moved, every charter-global check is re-derived; the tool-module conclusions (§ action_binding_and_uuids of revision_2) are carried forward on the unchanged `task_tools.py` hash.
- Base copy lines 1-1352 still identical to `blueprint/products/orders.yaml`. The extended section was re-serialised (flow-style YAML); content compared by parsing.
- Gate snapshot (coordinator, post-rework): all seven OK. Masked: round-3 `tasks/*.json`. Disclosure: round-1 and round-2 GT were read in their rounds; no round-3 GT before the task freezes below.

### What moved (policy by policy)

- Recollection window: the assembly sentence "The class window and every lengthening that applies are added together into the built recollection window." is removed (each lengthening sentence already says "is lengthened by"); `built_window` now quotes the standard-window sentence. The second-offer tiers are reworded as anchors: "counted from the event_date of the latest earlier orders_recollection_requested line instead of from the rejection date, and the recollect-by date it gives is never earlier than minimum_window_days after the rejection date" / "counted from today instead of from the rejection date". Compute unchanged.
- Genetic quote: the base requisition-encounter and S4 replacements now also restate the encounter estimate for every class other than genetic and Esoteric (P2). The standard is named "the test price sum"; each reduction is stated as "the quote is reduced by <rate> of the test price sum" (redraw, coverage, prompt-pay 15% / 10.00 credit / none), replacing the round-2 assembly sentence (P1). Compute: `priced - priced*redraw - priced*coverage - prompt_pay_reduction` (numerically identical to round 2); `genetic_scope` returns no value outside the genetic class.
- Genetic fee: the confirmation replacement now restates, for every class other than genetic and Esoteric, the patient's confirmation and the after-accession class-fee posting (P2). The assembly sentence is removed; each factor sentence names what it acts on: stage multiplier and assistance act on "the fee basis", extra-test / authorization / courtesy are "added to / subtracted from the handling fee", the standard "never below zero and rounded ... only at the end". **Semantic change:** the assistance rate now reduces only the fee basis (round 2: the whole net amount). Compute `MX(0, basis*stage*(1-assist) + extra - auth - courtesy)` matches the new wording.
- Reference estimate: standard named "the test price sum"; multi-test, coverage-loss and assistance reductions are each "of the test price sum"; collection-service amounts "added to the estimate". Numerically identical to round 2.
- Reference fee: standard is "the starting amount"; the batch multiplier acts on the starting amount; additions and subtractions act on "the handling fee"; floor and rounding in the standard sentence. Numerically identical to round 2.

### rule_compute_equivalence (revision_3)

Verbatim script: every `policy_source`, `superseded_clause`, `replaced_by`, `baseline.rule` sentence and `compute_basis` entry locates; every compute binding has a basis. Sentence sweep per policy finds each combining operation stated in its own factor sentence ("lengthened by", "reduced by ... of the test price sum", "added to / subtracted from the handling fee", "the fee basis is multiplied / reduced"), and no assembly binding's basis names a factor quantity — **P1 closed at the source layer.** The operations commute where the wording leaves order open (genetic fee: stage and assistance both multiply the fee basis; quote and estimate: every reduction is a fraction of the same test price sum), so no order ambiguity is introduced. No divergence found.

Observations:
- O-R3-1 (genetic quote): "the test price sum" is defined as the sum of each test's price "each test being priced at the self_pay_price in the class test_menu", and the bundling sentences then re-price tests ("is priced at second_test_share of its self-pay price"). The coherent reading — the reductions are fractions of the bundled sum, the same sum the quote starts from — is the only one under which the quote "is the test price sum" before reductions; a reading that takes the reductions of the unbundled 548-style sum while starting the quote from the bundled sum contradicts that sentence. Not a second defensible answer; wording note for the render layer.
- O-R3-2 (recollection): "the recollection window granted" (the days from the rejection date that `recollect_by_date` adds, and the tool's `recollection_window_days`, documented as "counted from the rejection date as day 0") and "the recollection window ... counted from <another anchor>" are two uses of "window". The derivation is unique (recollect-by = anchor + window, granted = recollect-by − rejection date), but a reader must convert.

### override_declarations (revision_3)

- All round-2 conclusions stand. Additionally, for every superseded class-generic base sentence, the merged charter now carries a clause in force for every class: recollect-by (recollection policy, class-generic), encounter estimate amount and its replacement on add-on/lapse (genetic quote replacement, "every class other than ... genetic ... and Esoteric"), patient confirmation and after-accession handling-fee posting (genetic fee replacement, same scope). **P2 closed**; O-R2-1 closed. The two estimate policies' replacements of the same base clause are complementary (genetic / Esoteric / every other class), not conflicting.

### prerequisite_graph and prerequisite_sentences (revision_3)

Unchanged from revision_2 (same three edges, verbatim sources, conditions, writers). Acyclic.

### factor_ladders (revision_3)

Unchanged ladders, labels and counts from revision_2 (recollection 4+1, quote 3+1, genetic fee 5+1, reference estimate 3+1, reference fee 5+1). assistance_award's value text now reads "as the share by which the fee basis is reduced" — consistent with the new rule. Every fall-through = baseline; every `baseline.rule` self-sufficient (14-day class window capped; test price sum; class fee from accessioned/testing_hold; test price sum; class fee) and none names a factor quantity.

### findings (revision_3)

- P1 — closed (source assembly sentences and their compute_basis no longer name factor quantities; each operation lives in its factor's sentence).
- P2 — closed (every retired class-generic clause has a clause in force for the remaining classes).
- Round-2 state: no REDs were open; F-CG-1..F-CG-7 remain closed (re-checked on the new text: S4 declared and replaced for all classes; per-class test counting; assistance "no approved award covers"; retrieval "whether or not credited"; honest labels; prompt-pay and coverage-loss ladders unchanged from round 2).
- New charter-global REDs: none. New observations O-R3-1, O-R3-2. O-R2-1 closed; O-R2-2, O-R2-3, O-R2-4 and the round-1 observations left as recorded stand.

### closing_checklist (revision_3)

Written after both round-3 reveals (2026-10-04T19:11Z); § revision_3 above was not changed after a reveal.

- `0.md`, `1.md` each carry revision_3 with frozen derivation, freeze record and comparison; all four relationships PASS for both tasks; earlier revisions untouched.
- Scopes unchanged, disjoint and jointly complete over the five extended policies and five task tools; uuid8s unchanged.
- Trees: task 0 — 2 prerequisites, 1 value_input, user root; task 1 — 1 prerequisite, 1 value_input, user root; graph acyclic.
- Factors: honest labels and counts as revision_2; every factor bears weight on its world; every whole baseline definite and different from gold (14 / 548.00 / 150.00 / 495.00 / 25.00).
- Policy self-consistency: P1 and P2 closed at the source; no new divergence or undeclared override.
- Gates re-run by the auditor on the final form (`9cf73fc8...` / `1cddb81e...`): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. check_traceability not run here (render layer).
- Observations standing: O-CG-2, O-CG-7, O-CG-9, O-CG-12, O-CG-13, O-R2-2, O-R2-3, O-R2-4, O-R3-1, O-R3-2; task observations as recorded.
- Difficulty result (revision_3): **passes the source-layer audit.**
