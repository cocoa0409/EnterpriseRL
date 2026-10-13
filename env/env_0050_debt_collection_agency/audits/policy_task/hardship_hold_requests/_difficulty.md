# Policy-task audit — hardship_hold_requests / charter-global

## charter_global_frozen

- Freeze time: 2026-10-10T18:15Z. Auditor: an independent Claude audit agent (erl-task-policy-audit), not the instantiating agent.
- Frozen inputs:
  - `tasks/hardship_hold_requests/hardship.extended.yaml` sha256 `26dd15efc7046276d23138fd74c4aeefd8df0b69b30330fd4374f32959bf38ce`
  - `tasks/hardship_hold_requests/task_tools.py` sha256 `d3aaf8ff54d9b898faa5c81e69825b3d7528cd6dbaf6d2b95e4573485239b738`
  - masked views `/tmp/env0050_views/hardship_hold_requests/r1/0.view.json` (sha256 `2e817ec7…802d`) and `1.view.json` (sha256 `2939e071…d715`). I re-hashed all four, and they match the brief.
- Fields I was permitted to read: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/hardship.yaml`, plus `products/account.yaml` / `plan.yaml` for the cross-category variant parameters), the extended charter, the tool module, and `frozen_time` / `user_scenario` / `initial_state` from the views.
- Fields that stayed masked while this section was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, the db_closure fields, and any earlier audit. Nothing in this section comes from a revealed GT. I ran no grep over `tasks/` or over the scenario directory.
- Entry conditions (Step 0): the brief carried the gate snapshot (`/tmp/env0050_views/gates/env0050_hardship_hold_requests_gates.txt`). EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE were all OK, and traceability was deferred because the KB is not published yet. The masked views and their hashes were also supplied. The input is complete.
- The base section is verbatim: the YAML keys `category … policies` in the extended file equal `blueprint/products/hardship.yaml` key for key. The only addition is `extended_policies`, and the textual diff of lines 1–1052 is one trailing blank line.
- DSL semantics I used, from `skills/erl-task-instantiate/references/product_extended.yaml` and `scripts/check_compute.py::build_env`:
  - `COUNT/LATEST/SUM` are scoped to the target holding (`hold_id`).
  - `CFIELD/EXISTS/CPARAM/X*` are scoped to the customer.
  - `within_months=N` keeps a row iff `0 <= MONTHS(row_date, NOW) < N`, where `MONTHS` counts whole months and subtracts one when the day-of-month of NOW is smaller than the row's.
  - `DAYS(a,b)` is `b − a`.

### policy_conflict_scan

There are seven extended policies, each on its own target tool:

| policy | subject | target_tool (owner) | scope as stated by its rule |
|---|---|---|---|
| hardship_ext_cure_notice | documentation_requested | send_cure_notice_c402292e (agent) | undecided request; a submission has arrived; no complete-documentation date |
| hardship_ext_longterm_extension | extension_granted / hold_extended | extend_longterm_hold_aa9e035f (user) | running Long-Term hold; consumer self-books |
| hardship_ext_review_income_records | documentation_requested (income_loss_evidence) | request_income_records_8e86e9ce (agent) | running Long-Term hold, before a status review |
| hardship_ext_medical_recertification | documentation_requested (medical cert) | request_medical_recertification_c8d32721 (agent) | running Long-Term hold, before a status review |
| hardship_ext_service_extension | extension_granted / hold_extended | extend_service_hold_a0a57648 (user) | running Military hold; servicemember self-books |
| hardship_ext_service_review_proof | documentation_requested (active-duty proof) | request_service_review_proof_12b8aafa (agent) | running Military hold, before a status review |
| hardship_ext_service_documentation | documentation_requested (active-duty proof) | request_service_documentation_e72ed459 (agent) | undecided Military request with no documentation request yet |

- **Subjects.** Five policies write `hardship_documentation_requested`. They are told apart by hold state (undecided vs running), by tier (Long-Term vs Military), and by document type. Income records and recertification share the running-Long-Term scope but ask for different document types. The two extension policies are tier-disjoint.
- **Trigger overlap (observation O-1).** `hardship_ext_cure_notice` and `hardship_ext_service_documentation` overlap on one situation: an undecided Military request on which a submission has already arrived while no documentation request exists yet. In that situation both are owed, and the write order decides the outcome:
  - Service documentation first: the cure notice is still owed afterwards.
  - Cure notice first: the history now shows a documentation request, so service documentation is no longer owed.
  
  Neither task world contains this situation. In task 1 the new Military request `a4d301e6…` has no submission, because the orders arrived on the running hold `2a869859…`.
- **Eligibility and time anchors.** No extended policy restates a base eligibility gate. The base gates (`hold_account_status`, `extension_on_active_hold`, `extension_before_end`, `review_on_active_hold`, `notice_hold_status`, `approve_on_eligible_account_status`) are inherited. The time anchor these rules lean on is "the hold's current end date". Its base definition conflicts with the extended extension lengths: see finding CG-2.
- **Terminal states.** Every write leaves the hold status unchanged. The two extension tools only move `end_date` and `extension_count` and append one event. There is no terminal-state conflict.
- **Cross-category reads.** All reads are declared, and none writes another category:
  - account `status`, `validation_period_end_date`, `debt_type`, `balance_due`, `term_end_date`, `variant_name` and `placement_term_days` (via CPARAM)
  - account `account_transactions` and `account_case_events.restriction_type`
  - plan `plan_installments.event_type`
- **Scope exclusivity and completeness.** I derived the scopes from the two trees walked in the task files. Task 0 covers {cure_notice, longterm_extension, review_income_records, medical_recertification}. Task 1 covers {service_documentation, service_extension, service_review_proof}. The two sets are disjoint and together cover all 7 extended policies.

### rule_compute_equivalence

I checked mechanically that every `compute_basis` quotation, every `baseline.rule` sentence, every prerequisite `policy_source` and every overwrite `replaced_by` is verbatim in its policy's own `rule`. Every `superseded_clause` is verbatim in its base rule. All checks pass for all 7 policies, with no missing quotation. Below is the sentence-by-sentence sweep (rule → compute and compute → rule).

- **cure_notice.**
  - The run point is three tiers, binding `cure_run_days`, and the condition order matches the prose.
  - The mailing, form and lag ladders map one-to-one.
  - Resubmissions left = `documentation_resubmission_max − (count of that kind − 1)`. This matches "counting every submission of that kind after the first as one used".
  - The result is a plain sum. The "whole number, not rounded" sentence has no binding and needs none.
  - No empty promise and no invented basis.
- **longterm_extension.**
  - Base length, anchor, capacity cut, program, returned-payment and balance tiers all map one-to-one, and the result is `base + anchor − cut + program + return + balance`.
  - The windows "current or the five preceding months" and "current and the two preceding months" are implemented as `within_months=6` and `within_months=3` on `txn_date`. This is not equivalent at the far month boundary: see finding CG-1.
  - "Reviews falling due every review interval counted from the hold's start date", with the next one "after the current end date", is implemented as `((held//I)+1)*I − held` with `held = DAYS(start, end_date on record)`. "Current end date" is read off the record, not off the base formula: see finding CG-2.
- **review_income_records.**
  - The count point is three tiers. Mailing, term cut and returned-payment tiers map one-to-one.
  - The cap is applied last via `MN(adjusted, DAYS(NOW, end_date))`, as stated.
  - `inc_returned_n` uses `within_months=6`: see CG-1.
- **medical_recertification.**
  - The package method is three tiers. `MX` implements "the later of". Route and age map one-to-one, and the cap is applied last to the sum.
  - The care-billing ladder is not equivalent when a consumer holds two or more medical accounts: see finding CG-4.
- **service_extension.**
  - Anchor, carry, stage, payment cut and new placements map one-to-one, and the result has the stated signs.
  - The carry counts `hardship_extension_granted` events. That matches "counting the extensions already granted on the hold".
  - `sx_net_paid` and `sx_new_placements` use `within_months`: see CG-1.
- **service_review_proof.**
  - The count point is three tiers. Tier 2 adds `decision_sla_business_days` as calendar days to a calendar count; this reading is not unique (observation O-2).
  - Mailing, extension history, review record, stage cut and new placements map one-to-one, and the cap is applied last.
  - `sv_new_placements` uses `within_months=2`: see CG-1.
- **service_documentation.**
  - The send anchor is three tiers. The middle tier compares calendar days sent-late with "the tier's decision days" (`decision_sla_business_days`), which raises the same unit question as O-2.
  - Validation, term-length (CPARAM `placement_term_days`: Early-Out 150, Primary/Secondary 365, Tertiary 455, Legal 730, Warehouse 1095, so all three tiers are reachable) and contact-route tiers map one-to-one.

### action_binding_and_uuids

- **`(target_tool, computes)` pairs.** There are seven distinct pairs, one policy each: `cure_due_days`, two `extension_days` on different tools, and four `due_in_days` on different tools. No tool is claimed twice.
- **uuid8s.** The seven values are `c402292e`, `aa9e035f`, `8e86e9ce`, `c8d32721`, `a0a57648`, `12b8aafa`, `e72ed459`. They are pairwise distinct, share no prefix or suffix pattern, and show no sequence or adjacency. Nothing suggests batch derivation.
- **Docstrings.**
  - None names another task tool or states a position in a cross-problem sequence.
  - Several use "read from the hardship hold lookup before the call" and "Afterwards …". These describe reading the id before calling the tool and its visible effect, not an order between problems (observation O-3).
  - The two extension docstrings assign the write to the consumer or servicemember, consistent with their rules.
- **Tool bodies.**
  - `send_cure_notice`, `request_income_records`, `request_medical_recertification`, `request_service_review_proof` and `request_service_documentation` each look up the hold (or default to `{}`) and append one `hardship_documentation_requested` row with `due_date = today + n`.
  - `extend_*` sets `end_date = previous end_date + n` and `extension_count + 1`, and appends one `hardship_extension_granted` row.
  - None checks status, gate, window or prerequisite, and none refuses or hints. The module docstring states this.

### prerequisite_graph

- **Field filled.** `prerequisite` is filled on every policy. It is `[]` on cure_notice, longterm_extension, service_extension and service_documentation.
- **Edges** (all `form: state`, so no `fallback_reason` is needed and none is present):
  - E1: review_income_records → longterm_extension, `value_input`, gate `inc_end_room` (exists in compute).
  - E2: medical_recertification → review_income_records, `value_input`, gate `rc_income_room` (exists).
  - E3: medical_recertification → cure_notice, `state_gate`, gate `hardship_hold_events.event_type`.
  - E4: service_review_proof → service_extension, `value_input`, gate `sv_end_room` (exists).
  - E5: service_review_proof → service_documentation, `state_gate`, gate `hardship_hold_events.event_type`.
- **Graph shape.** Every `problem` is an extended id in this file, never a base policy and never the policy itself. The graph is acyclic: two disjoint trees of depth ≤ 2.
- **Quotations.** Every `policy_source` is verbatim in the blocked policy's own rule (checked mechanically).
- **`resolved_by`.** It equals the depended-on policy's `target_tool` on all five edges.
- **Effects.**
  - E1 and E4: the extension moves `end_date`, so `DAYS(NOW, end_date)` grows. True by the tool body.
  - E4 also adds an extension event, which `sv_extensions` reads. True.
  - E2: the new income request becomes `LATEST(due_date)`. True by the tool body.
  - E3 and E5: the tool appends a documentation request on the other request. True.
- **State-gate `gate` values** name a column rather than an eligibility id. The extended policies carry no eligibility list (observation O-4).
- **Phrasing.** No authoring-viewpoint wording appears in any `prerequisite` field.
- **`condition` against sentence.** On E1, E2, E4 and E5 the condition matches the sentence. E3's condition is weaker than its sentence: see finding CG-3.

### prerequisite_sentences

Every edge sentence passes the four-point test for connective, state form, no tool / id / snake_case token, and strength — except where noted.

- **E1** — "The income records due date is fixed only after the hold's end date on record reaches past the status review the records are for."
  - Connective "only after"; record-visible state (end_date against the review due date). No tool or id.
  - Strength equals the condition ("falls after the due date of the status review that next falls due").
  - The only write in this difficulty that moves a Long-Term hold's end date is the Long-Term extension. The service extension is Military-only, and the income-records rule is Long-Term-only.
  - Derivation: the sentence plus the record's end_date and the next review date lead to the Long-Term extension rule ("each extension adding … to the hold's end date"), and that rule says the consumer books it in person. There is one reading.
- **E2** — "The recertification due date is not worked out until an income records request with a due date still ahead stands on the hold."
  - Connective "not … until"; record-visible state. Strength equals the condition ("due date is later than today").
  - The only writer of a running hold's income-records request is the income-records policy. The cure notice could carry `income_loss_evidence`, but its rule limits it to undecided requests.
  - One reading.
- **E3** — "The recertification request is not sent until every incomplete documentation submission on the consumer's other Long-Term Hardship Hold requests carries a documentation request dated after that submission, …"
  - Connective "not … until"; record-visible state. The only writer on an undecided Long-Term request is the cure notice; the income, recertification and Military policies are out of scope by their rules.
  - The strength differs from the condition: see CG-3.
- **E4** — "Before the status review proof due date is worked out, the hold's end date on record must already lie beyond that review's due date."
  - Connective "Before … must already"; state form. Strength equals the condition.
  - The only writer for a Military hold is the service extension. One reading.
- **E5** — "The status review proof request is not sent until every undecided Military Service Hold request of the servicemember carries its initial documentation request, …"
  - Connective "not … until"; state form. It matches the condition ("status requested has at least one documentation request for active-duty status proof").
  - The only writer is service_documentation, which is owed exactly when no documentation request exists yet. The cure notice is not owed without a submission.
- **No restatement and no undeclared order.**
  - No depended-on rule restates a sentence that blocks it.
  - No rule carries a second wording, a tool name or another problem's id.
  - The other ordering words in the rules do not order two problems of this difficulty: "Before each status review", "once the updated documentation … is on record", "once updated orders are on record", "an account placed after the servicemember's earlier consumer-level request". The review and the documentation receipt are not writes of this difficulty.
  - No base sentence grounds an edge.

### override_declarations

I checked every sentence of each `base_policy_refs` entry:

- **cure_notice / hardship_evt_documentation.**
  - The resubmission clause is replaced and declared.
  - The initial-request sentence governs the request-date ask and is followed.
  - The denial-on-lapse sentence and its counting rule are not overwritten. A cure due date may now lie beyond the original documentation period, and the base still says "denied … only when the handling date is later than the documentation period". That sentence speaks of documentation that "has not arrived", while here incomplete documentation has arrived, so it is not hit by the scored quantity (observation O-5).
  - The remaining sentences are followed.
- **longterm_extension / hardship_evt_extension, hardship_evt_review.**
  - Sentence 1 ("each extension adding extension_days") is replaced and declared.
  - **Not declared:** the base definition of the current end date, in both `hardship_evt_extension` and `hardship_evt_end`: "The hold's current end date is start_date plus initial_hold_days plus extension_days for each extension already granted, minus 1". The extended rule makes the new end date "the current end date plus the days added", where the days added are not `extension_days`. This is finding CG-2.
  - The annual-limit sentence ("hardship_msr_hold_days_12m plus extension_days") no longer has a unique reading after the override: tier extension_days or the computed days (observation O-6).
  - "It is decided within extension_decision_sla_business_days business days" sits beside the new self-booking by the consumer. The blueprint difficulty summary says "The agent records … extensions". The write moves from agent to consumer, and no overwrite declares this (observation O-7). The tool surface offers no agent-owned extension, so this alone gives no second answer.
  - The review sentences are followed. "A review never shortens or lengthens end_date" is untouched, because the extension, not the review, moves the end date.
- **service_extension / hardship_evt_extension, hardship_evt_review, hardship_agg_consumer_level.** Same as Long-Term: sentence 1 is replaced and declared, the base current-end-date definition is not declared (CG-2), and O-7 applies. Military does not count toward the annual limit, so O-6 does not arise. Consumer-level is followed.
- **review_income_records, medical_recertification, service_review_proof / hardship_evt_documentation, hardship_evt_review (+ consumer_level).** `overwrite: []`. The documentation-rule sentences govern the request-date ask on a hold request. These policies govern a later review-time ask that the base does not regulate, so there is no conflict on the scored due-days. They follow the review rule (continue_hold on updated documentation; ends if not recorded within review_overdue_days). Declaring nothing is correct.
- **service_documentation / hardship_evt_documentation, hardship_agg_consumer_level.**
  - The initial-request sentence and the documentation-period counting rule are both replaced and declared.
  - The counting rule's `replaced_by` covers only the case where the due date is later than request_date + documentation_due_days. In the other case the superseded counting rule is gone and nothing replaces it (observation O-8).
  - Consumer-level is followed, and the rule's explicit "including a request recorded for an account placed after the servicemember's earlier consumer-level request" carries it.

### factor_ladders

Each row below gives the factor, its label, the binding it decides, its tiers (the last is the fall-through, which equals its baseline unless noted), whether it is multi-source, and its cross-difficulty category.

**cure_notice** (5 factors: 1 method, 4 parameter)
- `cure_run_point` (method → `cure_run_days`). Tiers: run to the validation end (account in validation period AND validation end after the original due date) / original due + 3 (validation ended ≤ 30 days ago) / original due (baseline `days_to_original_due`). The first tier is multi-source (account row + documentation request row); the second is single-source. Cross-difficulty: account.
- `cure_mailing` (param): 7 / 3 / 0. Multi-source over submissions (mail/fax AND none electronic).
- `cure_form` (param): 7 / 3 / 0.
- `cure_resubmission` (param): 5 (one left) / 2 (two or more left) / 0. **The middle tier is unreachable**: see finding CG-5.
- `cure_notice_lag` (param): 5 / 2 / 0.

**longterm_extension** (6 factors: 1 method, 5 parameter)
- `lt_payment_capacity` (param → `lt_base_days`): `review_interval_days` (60) / 75 / `extension_days` (90, baseline). Cross-difficulty: account (ledger).
- `lt_review_anchor` (method): from the overdue-window end / from the review due date / from the day after the end (0). Multi-source (hold dates + review rows).
- `lt_plan_capacity` (param): 30 / 15 / 0. Cross-difficulty: plan.
- `lt_debt_program` (param): 30 / 15 / 0. Cross-difficulty: account.
- `lt_returned_payments` (param): 14 / 7 / 0. Cross-difficulty: account.
- `lt_balance_size` (param): 10 / 5 / 0. Cross-difficulty: account.

**review_income_records** (4 factors: 1 method, 3 parameter)
- `inc_count_point` (method): documentation days after the request / after the review / overdue-window end (baseline).
- `inc_mailing` (param): 7 / 3 / 0. Multi-source.
- `inc_term_pressure` (param): 4 / 2 / 0. Cross-difficulty: account.
- `inc_returned_payments` (param): 4 / 2 / 0. Cross-difficulty: account.

**medical_recertification** (4 factors: 1 method, 3 parameter)
- `rc_review_package` (method): the income due date (kept ≥ 2 AND income request ahead) / the later of the income due date and the overdue-window end (kept = 1 AND income request ahead) / the overdue-window end (baseline). Labelled multi-source, **but one conjunct is constant**: see finding CG-6.
- `rc_certification_route` (param): 5 / 2 / 0.
- `rc_care_billing` (param): 5 / 2 / 0. Cross-difficulty: account. **The tiers overlap as stated**: see finding CG-4.
- `rc_certification_age` (param): 5 / 2 / 0.

**service_extension** (5 factors: 1 method, 4 parameter)
- `sx_review_anchor` (method): as `lt_review_anchor`. Multi-source.
- `sx_carry` (param): 90 / 15 / 0. All tiers are reachable with max_extensions = 3.
- `sx_stage_protection` (param): 30 / 15 / 0. Cross-difficulty: account.
- `sx_payment_cut` (param): 30 / 15 / 0. Cross-difficulty: account.
- `sx_new_placement` (param): 30 / 15 / 0. Cross-difficulty: account.

**service_review_proof** (6 factors: 1 method, 5 parameter)
- `sv_count_point` (method): documentation days after the request / documentation + decision days after the review / overdue-window end (baseline).
- `sv_proof_mailing` (param): 10 / 5 / 0. Multi-source.
- `sv_extension_history` (param): 10 / 5 / 0.
- `sv_review_record` (param): 7 / 3 / 0. Multi-source (review rows + hold dates).
- `sv_stage_cut` (param): 10 / 5 / 0. Cross-difficulty: account.
- `sv_new_placement` (param): 7 / 4 / 0. Cross-difficulty: account.

**service_documentation** (4 factors: 1 method, 3 parameter)
- `in_send_anchor` (method): documentation days after the send day / decision + documentation days after the request / documentation days after the request (baseline `30 − late`).
- `in_validation` (param): 5 / 2 / 0. Cross-difficulty: account.
- `in_term_length` (param): 5 / 2 / 0. Cross-difficulty: account.
- `in_contact_route` (param): 7 / 3 / 0. Cross-difficulty: account.

Structure checks across all policies:
- **Bindings and `decides`.** Every factor's bindings are disjoint from the other factors' bindings, and `decides` is always an input, never `result`.
- **Rule and compute.** Every tier is stated in the `rule` with its condition and value or method, and implemented in `compute`.
- **Distinct outcomes.** No two tiers of a ladder select the same value or method.
- **Labels.** They are honest.
  - The method tiers change the date the count runs to or from.
  - `cure_run_point`'s middle tier is "original due + allowance", which is a number on the same method. Its first tier is a genuine method change, so the label stands.
  - Every method tier names a rule the charter states.
- **Baselines.** Every `baseline.rule` is self-sufficient, every sentence of it is in the rule, and its `params` keys are the tier parameters it uses (`[]` for cure_notice). Every factor's fall-through equals its baseline.
- **Counts.** Every computation declares 4–6 factors, with at least 2 `parameter` and at least 1 `method`.
  - Over task 0's policies, the multi-source factors are `lt_review_anchor`, `cure_mailing` and `inc_mailing`, and the cross-difficulty factors read account and plan.
  - Over task 1's policies, the multi-source factors are `sx_review_anchor`, `sv_review_record` and `sv_proof_mailing`, and the cross-difficulty factors read account.
- **Business realism.**
  - These are weakly motivated but not demonstrably unreal: `lt_balance_size` (bigger balance, longer extension) and `sx_new_placement` (recent placements on other accounts lengthen this hold's extension). Observation O-9.
  - CG-5 and CG-6 fail the "real ladder" test.

### findings

**CG-1 — SOURCE-POLICY RED (rule/compute not equivalent: month windows).**
- *Symptom.* The rules describe calendar-month windows ("with their posting or return month falling in the current or the five preceding months", "in the current and the two preceding months", "in the current or the preceding month"). Compute implements them as `within_months=N`, i.e. `0 <= MONTHS(d, NOW) < N`, and `MONTHS` subtracts one month when NOW's day-of-month is smaller than the row's.
- *Root cause.* Whole months elapsed and calendar months diverge in the band "month NOW−N, day > NOW's day".
- *Evidence.* Rule sentences in `hardship_ext_longterm_extension` (base length, returned payments, capacity cut), `hardship_ext_review_income_records` (income returned-payment allowance), `hardship_ext_service_extension` (payment cut, new placements) and `hardship_ext_service_review_proof` (new placements). The affected bindings are `lt_paid_6m`, `lt_returned_6m`, `lt_returned_n`, `lt_plan_paid_3m`, `inc_returned_n`, `sx_net_paid`, `sx_new_placements` and `sv_new_placements`.
- *Demonstrated consequence.* Take NOW = 2026-08-17 and a return dated 2026-02-20. By the rule, February is not among March–August, so the return is excluded. By compute, `MONTHS('2026-02-20','2026-08-17') = 5 < 6`, so it is included. The returned-payment allowance and the net payment then differ.
- *Bears on.* Tasks 0 and 1, latently. No seeded row lies in the band in either world; the task files check this.

**CG-2 — SOURCE-POLICY RED (undeclared override: "current end date").**
- *Symptom.* Both extension overrides replace only "each extension adding extension_days calendar days to end_date". The base definitions stay in force:
  - `hardship_evt_extension`: "The hold's current end date is start_date plus initial_hold_days plus extension_days for each extension already granted, minus 1"
  - `hardship_evt_end`: "… plus extension_days for each extension granted, minus 1", which grounds `term_completed`.
  
  The extended rules say "the new end date is the current end date plus the days added", and those days are not extension_days.
- *Demonstrated consequence.* Take the task-0 hold `da7b5afa…` after a 108-day extension. The base gives the current end date as 2026-02-20 + 180 + 90 − 1 = 2026-11-17, while the extended rule and the record give 2026-12-04. The two disagree on when the hold ends (term_completed), on the next extension window, and on the "hold's current end date" cap used by the income-records, recertification and review-proof rules. Computes read `F('end_date')`, i.e. the extended reading.
- *Bears on.* Tasks 0 and 1. No scored value changes in either world because the caps do not bind; the task files demonstrate this.

**CG-3 — SOURCE-POLICY RED (prerequisite sentence and condition differ: E3).**
- *Symptom.* The sentence requires "a documentation request dated **after** that submission" on "the consumer's other Long-Term Hardship Hold requests" (any status). The condition requires "a documentation request dated **on or after** the submission's arrival", and only on the "other **undecided** Long-Term Hardship Hold request whose hold shows no complete-documentation date".
- *Demonstrated consequence.*
  - (a) Strength: a cure notice dated the same day the submission arrived meets the condition but not the sentence, so the recertification is blocked by the sentence and unblocked by the condition.
  - (b) Scope: a denied Long-Term request with an incomplete submission and no later request blocks the recertification under the sentence, and since a cure notice is owed only on undecided requests, that block can never be lifted. The condition ignores it.
- *Bears on.* Task 0, latently: its only other Long-Term request is undecided and its submission is dated before the opening.

**CG-4 — SOURCE-POLICY RED with SOURCE-FACTOR structure (rc_care_billing tiers overlap; compute picks an arbitrary row).**
- *Symptom.* The tiers read "where the consumer has a placed medical account with a balance due of at least the care-balance amount …; where the consumer has a placed medical account with a balance due below that amount …". Compute is `CFIELD('account','balance_due', debt_type='medical')`, which returns the first matching row.
- *Demonstrated consequence.* A consumer with medical accounts of $1,500 and $400 satisfies both tier 1 and tier 2 as stated, so the tiers are not pairwise disjoint. Compute returns whichever row comes first in the table order, giving 5 or 2.
- *Bears on.* Task 0, latently: it has a single medical account.

**CG-5 — SOURCE-FACTOR RED (cure_resubmission: unreachable tier).**
- *Symptom.* The tier "where two or more remain, the spare-resubmission allowance is added" can never be selected.
- *Root cause.* `documentation_resubmission_max` is 0 for the 30-Day pause, which never needs documentation, and 1 for every other tier (variants block). A cure notice is owed only after a submission of the asked-for kind has arrived, so the count is at least 1. Resubmissions left = `max − (count − 1)` ≤ 1 for every reachable notice.
- *Consequence.* In substance the ladder has two tiers (5 / 0), below the three-tier minimum. This factor does not count. cure_notice keeps 4 surviving factors (1 method, 3 parameter), which is still within bounds.
- *Bears on.* Task 0.

**CG-6 — SOURCE-FACTOR RED (rc_review_package: a conjunct that holds of every customer who reaches the write).**
- *Symptom.* Both non-fall-through tiers include "an income records request with a due date still ahead stands on the hold".
- *Root cause.* The same rule's prerequisite sentence (E2) says the recertification due date "is not worked out until an income records request with a due date still ahead stands on the hold". At the moment the quantity is worked out, the conjunct is therefore true for every customer.
- *Consequence.* The tiers reduce to "kept ≥ 2 / kept = 1 / otherwise". The multi-source claim rests on a constant part, and the ladder restates the policy's own gate instead of dividing its customers. If the factor is struck, medical_recertification keeps 3 factors, all `parameter`: below the bounds of 4 in total and 1 `method`.
- *Bears on.* Task 0.

**Observations** (no demonstrable consequence on a scored value):
- O-1: Trigger overlap between cure_notice and service_documentation on an undecided Military request with a submission and no documentation request. Order-dependent. Not present in either world.
- O-2: "The tier's decision days" (`decision_sla_business_days`, business days) is added to or compared with calendar counts in the middle tiers of `sv_count_point` and `in_send_anchor`. Reading it as business days would give a different number. Neither task's world takes those tiers.
- O-3: Docstrings use "before the call" and "Afterwards" about reading the id and the visible effect. They state no cross-problem order.
- O-4: The state-gate `gate` fields name a column (`hardship_hold_events.event_type`), not an eligibility id.
- O-5: The base documentation-period denial is not overwritten, while a cure due date may run past the original documentation period. This is not a scored quantity.
- O-6: After the override, the base annual-limit sentence's "extension_days" has two readings. In task 0 both stay within the 365-day limit.
- O-7: The extension write moves from agent to consumer ("books it in person through the self-service portal"). This contradicts the blueprint summary "The agent records … extensions" and sits beside the base "It is decided within …". There is no overwrite entry. The tool surface makes the owner unique.
- O-8: service_documentation's `replaced_by` for the documentation period covers only the "later than request + documentation days" case.
- O-9: `lt_balance_size` and `sx_new_placement` are weakly motivated business conditions, but not demonstrably unreal.
- O-10: "The status review that next falls due" is computed as `((held//I)+1)*I − held`, so when today is itself a due date the next review is taken to be one interval later. Neither world is on a due date (178 days held in task 0, 357 in task 1).

## closing_checklist

Written after both reveals (2026-10-10T18:19Z system clock). **The difficulty does not close.** Not every task passes all four relationships, and the charter carries the SOURCE-POLICY RED findings CG-1 to CG-4 and the SOURCE-FACTOR RED findings CG-5 and CG-6.

- **Audit files.** `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, alongside this file. This is the first round, so there are no older revisions. Both comparison sections are present:
  - task 0: SOURCE-FACTOR RED
  - task 1: PASS on the per-task relationships, with latent charter REDs
- **Coverage and scope.** All 7 extended policies are covered. GT `charter_scope`: task 0 has {cure_notice, longterm_extension, review_income_records, medical_recertification}; task 1 has {service_documentation, service_extension, service_review_proof}. The scopes are disjoint and equal my derived trees. Task tools and GT are closed, and every task tool has an independently generated uuid8.
- **Trees.**
  - Task 0: 3 prerequisite problems, 2 `value_input` edges, 1 user write.
  - Task 1: 2 prerequisite problems, 1 `value_input` edge, 1 user write.
  - Neither tree has a cycle, and across the difficulty the edges E1–E5 form an acyclic graph with no cross-task references.
- **Factors.**
  - **Not met** for medical_recertification (CG-6). Once the constant conjunct is struck, `rc_review_package` fails, leaving 3 parameter factors and no method.
  - cure_resubmission's ladder is two-tier in substance (CG-5). cure_notice still has 4 surviving factors.
  - Every other computation has a self-sufficient baseline, 4–6 surviving factors with at least 2 `parameter` and at least 1 `method`, and every factor bears weight against an honest baseline. Each all-baseline figure differs from gold: 7, 90, 17, 17, 20, 180 and 33.
- **Instantiation gates on the final form.** I did not re-run them; the auditor does not run gates (Step 0). The brief's snapshot (all green) applies to the audited hashes `26dd15ef…` / `d3aaf8ff…`, which were unchanged at the reveal.

## revision_2

### charter_global_frozen (revision 2)

- **Freeze.** Written 2026-10-10 ~20:30Z (the system clock read 20:18:48Z at the start of the re-audit), before reading the round-2 `tasks/{0,1}.json` or `tasks/hardship_hold_requests/worklog.md`. Auditor: the same independent Claude audit agent as round 1.
- **Shared inputs changed.**
  - `hardship.extended.yaml`: sha256 `277523944a21193de62bfdc4a418df775b11483f7b20bb4e636536e233c2218d` (round 1: `26dd15ef…`).
  - `task_tools.py`: sha256 `3d6eb589cf7fdba5fd1b0691245bf9feb1de4229d828d0a07ee0d9cded573cf7` (round 1: `d3aaf8ff…`).
  - Because both changed, this section is re-derived in full and nothing is carried forward by reference.
- **Views unchanged.** `r2/0.view.json` `2e817ec7…` and `r2/1.view.json` `2939e071…` are byte-identical in hash to round 1.
- **Gate snapshot.** `/tmp/env0050_views/gates/env0050_hardship_hold_requests_r2_gates.txt`: all seven gates OK. Input complete.
- **Base section.** Still verbatim against `blueprint/products/hardship.yaml` (all ten top-level keys equal); `blueprint/` mtimes are unchanged since 2026-10-08. The DSL evaluator `check_compute.py` and `erlbench/` are unchanged, so the semantics in round 1's `charter_global_frozen` apply.
- **Masked fields.** Same division as round 1.
- **Contamination note.** I already know the round-1 gold values from the round-1 reveal. The round-2 charter-global section is built from the charter and tools alone; the per-task disclosures sit in each task file.

### policy_conflict_scan (revision 2)

- **Unchanged.** Same seven policies, the same `(target_tool, computes)` pairs and the same scope partition by hold state, tier and document type. Task 0 covers {cure, Long-Term extension, income records, recertification}, re-derived from the trees; task 1 covers {service documentation, service extension, review proof}. The two sets are disjoint and together cover all seven.
- **O-1 (cure / service-documentation trigger overlap): CLOSED.** The cure rule now says: "A cure notice is owed only on a request whose history already carries a documentation request for the kind of documentation that arrived; a request with no documentation request yet is answered by its initial documentation request instead." Service documentation remains "owed on every undecided Military Service Hold request whose history shows no documentation request yet". The two triggers are now disjoint.
- **New conflict, N-1 (SOURCE-POLICY RED, latent).** Two extended policies now supersede the same base sentence (`hardship_evt_documentation`: "The documentation period is the tier's documentation_due_days in calendar days, the day after request_date being day one.") with replacements that disagree:
  - `hardship_ext_cure_notice`: "Where a cure notice stands on the request, the documentation period of the request runs to the cure due date, so the request is not denied for documentation not received before that date has passed."
  - `hardship_ext_service_documentation`: "The documentation period of the request runs to the due date set under this rule, that due date being its last day."
  - Situation where they diverge: an undecided Military request with an initial documentation request (due D1), an incomplete active-duty proof submission, and then a cure notice (due D2 > D1). The O-1 fix makes this cure notice owed, because the history carries a documentation request for that kind. The service-documentation rule ends the period on D1; the cure rule runs it to D2. The two policies disagree on when the request may be denied with `documentation_not_received`.
  - Neither task world contains such a request: task 1's `a4d3…` has no submission, and task 0's `b609…` is Long-Term. So this is latent, not a scored-value defect in either task.

### rule_compute_equivalence (revision 2)

I re-ran the mechanical check. Every `compute_basis` quotation, every `baseline.rule` sentence, every `policy_source` and every `replaced_by` is verbatim in its own rule, and every `superseded_clause` is verbatim in its base rule. No item is missing in any of the seven policies. The changed or new items:

- **CG-1 (month windows): CLOSED.**
  - Every windowed rule now reads "dated less than six (three, two) whole months before today, a whole month running from a date to the same day of a later month". That is exactly `0 <= MONTHS(d, NOW) < N`, with `MONTHS` subtracting a month when today's day-of-month is smaller.
  - Spot check: a 2026-02-20 row at NOW 2026-08-17 is 5 whole months back, so the rule includes it, and `MONTHS` gives 5, so compute includes it. A 2026-02-17 row is 6 whole months back, so both exclude it.
  - Affected sentences: the Long-Term base length, capacity cut and returns; the income returns; the service payment cut and new placements; the review-proof new placements.
  - Residual (observation N-O3): the phrase "the same day of a later month" is undefined for a 29th–31st start date in a shorter month, for example 2026-01-31 → June. `MONTHS` treats such a row as 5 whole months back on 2026-07-30. No seeded row in either world starts on the 29th–31st within a window.
- **CG-2 (current end date): CLOSED.**
  - New overwrites in both extension policies, against `hardship_evt_extension` and `hardship_evt_end`: "For a Long-Term Hardship Hold [Military Service Hold] the hold's current end date is the end date on record: start_date plus initial_hold_days minus 1, plus the days each extension already granted added, … and the hold completes its term on that date."
  - Compute reads `F('end_date')`, which is the end date on record.
  - Residual (observation N-O2): the base structured `temporal_basis.counting_rule` fields of `extension_before_end` and `hold_term_completed` still carry the formula with extension_days. These are base metadata, not rule text; the rule text is overwritten.
- **CG-4 (care-billing overlap): CLOSED.**
  - The tiers are now "at least one of the consumer's placed medical accounts is still in its validation period" / "has placed medical accounts but none is still in its validation period" / "no placed medical account". They are mutually exclusive and exhaustive.
  - Compute uses `EXISTS('account', debt_type='medical', status='validation_period')`, then `EXISTS('account', debt_type='medical')`, which is equivalent. No arbitrary row is picked.
- **O-2 (business days added as calendar days): CLOSED.** `sv_count_point` and `in_send_anchor` now say "the decision days counted here as calendar days" and "counted as calendar days", which matches compute.
- **O-8 (service-documentation period gap): CLOSED.** Its `replaced_by` is now unconditional: "runs to the due date set under this rule, that due date being its last day". But see N-1.
- **O-10 (review falling due on the request day): CLOSED.** The income, recertification and review-proof rules now say "a status review falling due on the day of the request counts as already fallen due, so the review that next falls due is the following one". That matches `((held//I)+1)*I − held`. The two anchor rules now say "a review falling due on the current end date itself counting as one inside the hold", which matches `((held//I)+1)*I − held` with held = DAYS(start, end).
- **New cure factor `cure_debt_kind`.** The rule says "a medical debt adds the medical cure days; an auto deficiency, a retail installment debt or a private student loan adds the installment cure days; any other debt type adds none". `cure_debt_days` reads `CFIELD('account','debt_type', account_id=F('account_id'))`, which is equivalent.
- **`rc_review_package`.** The tiers now read only the review count; compute is `rc_income_room if rc_kept >= 2 else (MX(...) if rc_kept == 1 else rc_review_last)`. Equivalent.
- **Cure owed-condition sentence.** It is a trigger condition, not a quantity, and it has no compute binding; none is required.

### action_binding_and_uuids (revision 2)

- The pairs and uuid8s are unchanged and unique: `c402292e`, `aa9e035f`, `8e86e9ce`, `c8d32721`, `a0a57648`, `12b8aafa`, `e72ed459`.
- The tool bodies contain no `if`, no `raise` and no `Error` (grep). Each still does `ctx.find` on the hold row, one `ctx.create`, and for the extension tools one `ctx.update`.
- **O-3: CLOSED.** The docstrings no longer contain "before the call" or "Afterwards"; the id is now "read from the hardship hold lookup." and the effect is introduced with "On success". The only remaining "after" is "after today", which describes a date and is not an ordering.
- The tools still judge no prerequisite.

### prerequisite_graph (revision 2)

- The same five edges E1–E5, with the same kinds and gates, and the graph is still acyclic.
- **E3 is reworded and is now identical to its condition** (CG-3: CLOSED). Sentence: "…every documentation submission on the consumer's other undecided Long-Term Hardship Hold requests that still show no complete-documentation date carries a documentation request dated on or after the day that submission arrived…". Condition: "Every documentation submission received on the consumer's other undecided Long-Term Hardship Hold requests that still show no complete-documentation date is followed by a documentation request dated on or after the day that submission arrived." The scope (undecided, no complete date) and the strength (on or after) now match.
- **O-4 (`gate` names a column): kept,** as the reworker reports; it is still an observation.

### prerequisite_sentences (revision 2)

- E1, E2, E4 and E5 are unchanged and pass as in round 1.
- E3 passes the four-point test. Connective "not sent until"; record-visible state; no tool or id; strength equal to the condition.
- The only write that resolves E3 is the cure notice. Its new owed-condition (a documentation request for that kind already exists) holds for every undecided Long-Term request, because the base asks on the request date. One reading.
- No new cross-problem order was introduced. The added sentences are rationales ("because …"), the review-day convention, the decision-as-booking overwrite, the period overwrites, and the cure / initial-request split. The cure / initial-request split names the other problem's action only as a description of a different request state ("answered by its initial documentation request instead"). It states no order between two problems of one tree, and no tree in this difficulty contains both.

### override_declarations (revision 2)

- **cure_notice.** The resubmission clause is declared (as before). The documentation-period counting rule is now declared as well (O-5: CLOSED). This creates the N-1 conflict with service documentation. When no cure notice stands, a non-Military request falls back to the base counting rule, because the replacement is conditional (observation N-O1).
- **longterm_extension.** Five overwrites are declared:
  - "each extension adding extension_days"
  - the current end date in `hardship_evt_extension` and in `hardship_evt_end` (CG-2: CLOSED)
  - the annual-limit sentence, now "the days the long-term extension adds" (O-6: CLOSED)
  - "It is decided within extension_decision_sla_business_days business days" → "The consumer's own booking through the portal is the decision on the extension and takes effect the day it is made" (O-7: CLOSED for the charter)
  
  The blueprint summary's "The agent records … extensions" is scenario prose that the auditor does not edit. With the overwrite declared, the charter is self-consistent.
- **service_extension.** The same set (sentence 1, current end date ×2, decision); the annual limit does not apply to the Military tier.
- **income records / recertification / review proof.** `overwrite: []`, as before; their sentence-by-sentence conclusions are unchanged.
- **service_documentation.** Both overwrites are declared, and the period replacement is now unconditional (O-8: CLOSED).

### factor_ladders (revision 2)

- **cure_notice.** 5 factors (1 method, 4 parameter): `cure_run_point`, `cure_mailing`, `cure_form`, `cure_debt_kind` (new) and `cure_notice_lag`.
  - **CG-5: CLOSED.** `cure_resubmission`, whose middle tier could never be reached, was removed.
  - `cure_debt_kind` is 5 / 2 / 0 by debt type. All three tiers are reachable: the Documented and Long-Term tiers include medical, installment-type and bank_card/utility/telecom debts.
  - Its condition divides customers, and its value comes from the charter (`K`). The stated rationale (itemised statements and payoff letters from medical and installment creditors) is plausible for a collection agency.
- **medical_recertification.** 4 factors (1 method, 3 parameter).
  - **CG-6: CLOSED.** `rc_review_package` no longer carries the constant conjunct. Its tiers (kept ≥ 2 / kept = 1 / none) divide customers and change the method: the income records due date / the later of the two dates / the overdue-window end. It is no longer multi-source, which is allowed because the task-level multi-source factors lie elsewhere.
  - `rc_care_billing` now has disjoint tiers (CG-4 closed); its values are 5 / 2 / 0.
- **The other five policies.** Their factor structure is unchanged from round 1: the counts, labels, baselines and fall-throughs.
  - **O-9: CLOSED as a rationale question.** The added rationales are "the client reviews a larger balance before collection on it may resume" and "keeps the running protection from lapsing while a newly placed account's own request is still being documented". They are adequate for a weak but plausible business link.
- **Every computation.** It has 4–6 factors with at least 2 `parameter` and at least 1 `method`, a self-sufficient baseline whose every sentence is in the rule, and fall-through = baseline for every factor.
- **Task level.**
  - Task 0 multi-source: `lt_review_anchor`, `cure_mailing` and `inc_mailing`. Cross-difficulty: account and plan.
  - Task 1 multi-source: `sx_review_anchor`, `sv_review_record` and `sv_proof_mailing`. Cross-difficulty: account.

### findings (revision 2)

| round-1 item | round-2 status |
|---|---|
| CG-1 | closed |
| CG-2 | closed |
| CG-3 | closed |
| CG-4 | closed |
| CG-5 | closed |
| CG-6 | closed |
| O-1 | closed (but see N-1) |
| O-2 | closed |
| O-3 | closed |
| O-4 | kept (observation) |
| O-5 | closed (but see N-1) |
| O-6 | closed |
| O-7 | closed for the charter |
| O-8 | closed |
| O-9 | closed |
| O-10 | closed |

**New in revision 2:**
- **N-1 — SOURCE-POLICY RED (latent; new defect introduced by the O-1/O-5 rework).**
  - *Symptom.* The `hardship_ext_cure_notice` and `hardship_ext_service_documentation` overwrites of the same base documentation-period sentence give different last days.
  - *Evidence.* The two quotations above.
  - *Consequence.* The constructed Military case above has two denial dates, D1 and D2.
  - *Bears on.* Neither task's world; no scored value.
  - *Affected.* `hardship.extended.yaml` → `hardship_ext_cure_notice.overwrite[1]` and `rule`; `hardship_ext_service_documentation.overwrite[1]` and `rule`.
- **N-O1 — observation.** The cure notice's period replacement is conditional ("Where a cure notice stands"), so a non-Military request without a cure notice falls back to the base counting rule; the natural reading gives the same result.
- **N-O2 — observation.** The base structured `counting_rule` fields still state the extension_days formula; the rule text is overwritten.
- **N-O3 — observation.** "A whole month running from a date to the same day of a later month" is undefined for start dates on the 29th–31st; no seeded row is affected.

### closing_checklist (revision 2)

Written after the round-2 reveals (about 20:23Z). Note: the "~20:30Z" freeze stamp above is a hand estimate that ran ahead of the clock. The actual order was this section's pre-reveal part, then `0.md`, then `1.md` (finished 20:22:32Z), then the reveal.

**The difficulty does not close in round 2.** Two items block closure:
- Task 0 is SOURCE-CHAIN RED (R2-T0-F1). The task-0 closure and rationale still assert the round-1 "skip income → 26" figure, but the reworked recertification rule gives −34.
- The charter carries the new latent SOURCE-POLICY RED N-1: the cure notice and service documentation give different documentation-period last days for a Military request that has a cure notice.

Checklist:
- **Audit files.** One-to-one; revision 2 is appended under `## revision_2`, and the round-1 text is untouched.
- **Coverage and scope.** The 7 policies are covered with disjoint scopes; GT `charter_scope` equals my derived trees. Tools and GT are closed. The uuid8s are unchanged and unique.
- **Trees.**
  - Task 0: 3 prerequisites, 2 value_input edges, 1 user write.
  - Task 1: 2 prerequisites, 1 value_input edge, 1 user write.
  - Both are acyclic, and the difficulty-wide graph E1–E5 is acyclic.
- **Factors.** Every computation now has 4–6 surviving factors, at least 2 `parameter` and at least 1 `method`, and a self-sufficient baseline. Each all-baseline figure differs from gold (7 / 90 / 17 / 17; 20 / 180 / 33). Every factor bears weight. Each task has a multi-source and a cross-difficulty factor.
- **Gates.** I did not re-run them (Step 0). The coordinator's round-2 snapshot is all green, for hashes `27752394…` / `3d6eb589…`.
- **Round-1 claims.** Every closure the reworker claimed checks out at the charter and task level:
  - closed: CG-1 to CG-6, O-1, O-2, O-3, O-5 to O-10, T0-F1 to T0-F3, T0-O1, T0-O2, T1-F1, T1-O1, T1-O2
  - kept: O-4, which remains an observation, as declared
  
  The closures of O-1 and O-5 are what introduced N-1.

## revision_3

### charter_global_frozen (revision 3)

- **Freeze.** Written before reading the round-3 `worklog.md` section or `tasks/{0,1}.json`. The system clock read 2026-10-10T23:54:58Z at the start of the re-audit.
- **Inputs.**
  - `hardship.extended.yaml`: sha256 `7212db09f8819470c3a776d5ec76c5fa8c7fba8c2ae2fae05d81a41845122f6a`, changed from round 2's `27752394…`.
  - `task_tools.py`: sha256 `3d6eb589…3cf7`, unchanged.
  - Views `r3/0.view.json` (`2e817ec7…`) and `r3/1.view.json` (`2939e071…`): unchanged.
  - Gate snapshot `/tmp/env0050_views/gates/env0050_hardship_hold_requests_r3_gates.txt`: 7/7 OK.
- **Scope of re-derivation.**
  - The charter changed, so the charter-dependent sections are re-derived below.
  - The tool module is unchanged, so its body and docstring checks are carried forward from revision 2 on the identical hash.
  - The base section is still verbatim, with all ten keys equal to `blueprint/products/hardship.yaml` (mtime 2026-10-08).
  - The DSL evaluator and `erlbench/` are unchanged.
- **Mechanical re-check.** Every `compute_basis` quotation, every `baseline.rule` sentence, every `policy_source`, every `replaced_by` and every `superseded_clause` is still verbatim in its own rule. None is missing in any of the seven policies.
- **Masked fields.** Same division as before.

### What changed in the charter and what it closes

- **N-1 (documentation-period conflict): CLOSED.** The two overwrites of the base documentation-period sentence now agree.
  - Cure notice: "Where a cure notice stands on the request, the documentation period of the request runs to the cure due date, …; where none stands, the documentation period is the one the request's initial documentation request set: the tier's documentation days counted from the day after the request date or, for a Military Service Hold request, the due date its initial documentation request set."
  - Service documentation: "The documentation period of the request runs to the due date set under this rule, that due date being its last day, unless a cure notice later stands on the request, in which case it runs to the cure due date."
  - Re-running round 2's constructed Military case (initial request due D1, an incomplete submission, then a cure notice due D2): both rules now give D2. Without a cure notice, both give D1.
- **N-O1 (conditional cure replacement): CLOSED.** The cure replacement now also covers the "none stands" case, and for non-Military requests it restates the base period.
- **N-O3 (undefined whole month): CLOSED.** Every windowed sentence now defines the term: "whole months being the difference in calendar months between the date and today, less one when today's day of the month is smaller than the date's day of the month". That is exactly `MONTHS(d, NOW)`, and with "less than N" it is exactly `within_months=N`. The month-end case is now defined; for example, 01-31 against 07-30 gives 6 − 1 = 5, the same as compute.
  - Covered sentences: the Long-Term base length (with the definition carried by the same rule into the capacity cut and the returns), the income returns, the service payment cut and new placements, and the review-proof new placements.
  - The compute_basis quotations follow the new wording.
- **N-O2 (base `counting_rule` metadata): kept.** It stays an observation; the base is frozen and the overwritten rule sentences govern.
- **Recertification E2 `effect`: reworded.** "The latest income records due date moves from a date already passed to the newly set due date, so the review-package tier, which counts to the latest income records due date, sets the recertification on a date still ahead instead of a past one." This is now true of the revision-2 tier rule.
- **Unchanged.** Every other rule text, compute, factor, ladder, baseline and parameter, as far as I checked:
  - all overwrites listed
  - every rule sentence carrying a month window, a documentation period or an overdue window
  - E1–E5 sentences, conditions and gates
  - every factor id and effect
  - params identical to revision 2

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph / prerequisite_sentences / override_declarations / factor_ladders (revision 3)

- **Conflicts.** N-1 is closed and no new conflict appears. Scope and coverage are unchanged: 7 policies, disjoint per-task sets.
- **Rule and compute.** They are equivalent on every binding, and the month-window definition now matches the compute exactly.
- **Prerequisites.**
  - E1–E5 are acyclic and verbatim, and each condition equals its sentence (including E3).
  - Each edge has exactly one resolving write.
  - No undeclared cross-problem order exists. The cure rule's new "where none stands" clause names only another request kind's due date as a period definition, not an order between problems of one tree.
- **Overrides.** All declared. The two overwrites of the same base sentence by cure_notice and service_documentation are now mutually consistent.
- **Factors.** Unchanged from revision 2. Each computation has 4–6 factors, at least 2 parameter and at least 1 method, and a self-sufficient baseline equal to every fall-through. Every tier is reachable and divides customers.
- **Tools.** Unchanged: the uuid8s are unique and independently generated, and no body judges a prerequisite.

### findings (revision 3)

| item | status |
|---|---|
| N-1 | closed |
| N-O1 | closed |
| N-O3 | closed |
| N-O2 | kept (observation) |
| O-4 | kept (observation) |

No new charter-global defect.

### closing_checklist (revision 3)

Written after the round-3 reveals (about 23:57Z). **The difficulty closes on the source layer.**

- **Audit files.** One-to-one for tasks 0 and 1. Revisions 1, 2 and 3 are appended in order, with the older text untouched. Both revision-3 comparison sections are PASS.
- **Coverage and scope.** The 7 extended policies are fully covered. GT `charter_scope` gives task 0 {cure, Long-Term extension, income records, recertification} and task 1 {service documentation, service extension, review proof}. The scopes are pairwise disjoint (each covers its whole tree) and equal my derived trees. Task tools and GT are closed, and all seven uuid8s are independently generated and frozen.
- **Trees.**
  - Task 0: 3 prerequisite problems, 2 `value_input` edges, the user-owned Long-Term extension, no cycle.
  - Task 1: 2 prerequisite problems, 1 `value_input` edge, the user-owned service extension, no cycle.
  - The difficulty-wide graph E1–E5 is acyclic, with no cross-task edges.
- **Factors.**
  - Every computation of every task declares a self-sufficient baseline and 4–6 factors, with at least 2 `parameter` and at least 1 `method`.
  - Each task has a multi-source factor (task 0: `lt_review_anchor`, `cure_mailing`, `inc_mailing`; task 1: `sx_review_anchor`, `sv_review_record`, `sv_proof_mailing`) and a cross-difficulty factor (account, plus plan in task 0).
  - Every ladder has at least three reachable, distinct tiers stated in full in its rule, with conditions that divide customers.
  - Every factor bears weight against an honest baseline, and each all-baseline figure differs from gold: 7 / 90 / 17 / 17 and 20 / 180 / 33.
- **Gates.** The instantiation-stage gates on the final form are 7/7 OK per the coordinator's round-3 re-run (`/tmp/env0050_views/gates/env0050_hardship_hold_requests_r3_gates.txt`) at charter `7212db09…` and tools `3d6eb589…`. I checked the cited snapshot; per Step 0 the auditor does not run the gates.
- **Remaining observations** (not grounds for rework):
  - O-4: the state-gate `gate` field names a column.
  - N-O2: the base structured `counting_rule` metadata still states the extension_days formula. The base is frozen and the overwritten rule sentences govern; in both worlds the record equals the formula before the booking.

## revision_4

### charter_global_frozen (revision 4)

- **Freeze.** Written before reading the round-4 section of `worklog.md` or the round-4 `tasks/{0,1}.json`. The system clock read 2026-10-11T01:06:27Z at the start of the re-audit.
- **Inputs.**
  - `hardship.extended.yaml`: sha256 `9f2d8aec230bac0ce3b08d777f9486291423ee8ae32f65b7110152bf4bdeeef8`, changed from round 3's `7212db09…`.
  - `task_tools.py`: `3d6eb589…`, unchanged.
  - Views `r4/0.view.json` and `r4/1.view.json`: unchanged.
  - Gate snapshot `/tmp/env0050_views/gates/env0050_hardship_hold_requests_r4_gates.txt`: 8/8 OK, now including TRACEABILITY.
- **Additional permitted reads.** `audits/policy_kb/hardship_hold_requests/{0,1}.md` and `audits/runtime_context/hardship_hold_requests/{0,1}.md`.
- **What changed.** I have no byte copy of the round-3 file, so I cannot diff it. I re-checked mechanically instead:
  - every quotation, `baseline.rule` sentence, `policy_source`, `replaced_by` and `superseded_clause` is verbatim, with none missing in any of the 7 policies
  - the factor counts are unchanged (5 / 6 / 4 / 4 / 5 / 6 / 4)
  - every scored, baseline and per-factor figure is unchanged on both worlds (below)
  - the only visible change is `hardship_ext_cure_notice.compute.original_due`
  
  This is consistent with the reworker's "compute binding only" claim.
- **Base section.** Still verbatim. `blueprint/` is unchanged (mtime 2026-10-08).

### Cure "original documentation request" against compute (render-layer note 3)

- **New binding:**
  ```
  original_due: LATEST(..., 'due_date', event_type='hardship_documentation_requested', document_type=missing_type, event_date=F('request_date'))
                if COUNT(... same filters, event_date=F('request_date')) >= 1
                else LATEST(..., 'due_date', event_type='hardship_documentation_requested', document_type=missing_type)
  ```
  Rule: "The days allowed to cure run from the day the notice is sent to the due date of the original documentation request for that same kind of documentation."
- **Verdict on the round-3 mismatch: CLOSED for every state the charter lets a first cure notice arise in.**
  - Where the original request of the kind is dated the hold's request date, the first branch reads it. A later cure notice cannot displace it. My probe on task 0's world after the cure notice is written still gives 2026-08-24.
  - For a Military request whose initial request was sent after the request date, the fallback reads the latest request of that kind. Before any cure notice, that is the initial request, the only one.
- **Residual (observation R4-O1).** The fallback can diverge from "original" in one state: a Military request whose initial request is not dated the request date, which already carries a cure notice, and on which a further incomplete submission makes a second cure notice owed under the cure rule's owed-condition.
  - Constructed probe: the initial request is dated 2026-10-12 against a request date of 2026-10-02 and is due 11-18; cure #1 is dated 10-20 and due 12-01. The fallback then returns 12-01, while "original" gives 11-18.
  - That state needs a second cure notice after the single permitted resubmission. The cure overwrite accepts a resubmission only "while the request's resubmissions remain below the tier's resubmission maximum" (1 for every documented tier), and the base's in-force "a further incomplete submission is denied with documentation_not_received" points to denial there.
  - So the divergence sits only in a state where the charter already says no further submission can be accepted. No consequence in either task.
  - Note also that the first branch's premise (non-Military originals dated the request date) rests on base R-1, which the overwrite contract retires wholesale; see R4-F1.

### Kept-with-reason items (render-layer notes 1 and 2, and the spouse note): independent assessment

**R4-F1 — SOURCE-POLICY RED (charter-global, latent).** This is newly recognised in this round. It is not a regression: the defect has existed since round 1 for R-1 and X-1, and since round 2 for X-2, X-3, X-4 and end 1.2. I missed it in revisions 1–3 because I read the overwrites as tier-scoped.

- **Symptom.** Several overwrites retire a base clause for every tier, but their replacement covers only Long-Term and/or Military holds.
- **Root cause.** The overwrite contract (`skills/erl-task-instantiate/references/product_extended.yaml`, `overwrite`) says: "The granularity is the CLAUSE …: only the named sentence is retired". A declared superseded clause is therefore retired as a sentence, with no tier scope. The KB renders it the same way, which the policy-KB audit confirms as faithful (`audits/policy_kb/hardship_hold_requests/0.md`, policy-side note 1).
- **Evidence.** The affected clauses:
  - `hardship_ext_service_documentation` retires R-1, "For tiers whose documentation_required is true, Ridgeline asks for the tier's documentation_type on the request date with a due date documentation_due_days calendar days later, and accepts it only through the tier's documentation_channels." Its replacement begins "For a Military Service Hold request, …".
  - Both extension policies retire X-1, "A running hold may be extended … up to the tier's max_extensions times, each extension adding extension_days calendar days to end_date." Their replacements: "A running Long-Term Hardship Hold …" and "A running Military Service Hold …".
  - Both extension policies retire X-2 and end-clause 1.2 (the current-end-date counting rules), replaced "For a Long-Term Hardship Hold …" / "For a Military Service Hold …" only.
  - X-3 (the annual-limit refusal) is replaced for Long-Term only.
  - X-4 ("It is decided within extension_decision_sla_business_days business days") is replaced for Long-Term and Military only.
- **Demonstrated consequence.** Take a running Documented Hardship Hold (max_extensions 1, extension_days 30, counts toward the annual limit) whose consumer asks for an extension within the window. No in-force sentence of the charter says how many days an extension adds, how the current end date is counted (which the in-force gates `extension_before_end` and `hold_term_completed` read), whether the annual limit refuses it, or how quickly it is decided. A reader either restores the retired base clause (30 days) or finds no rule. Two readings, or no answer. Likewise, a Disaster, Financial Assistance, Documented or Long-Term hold *request* has no in-force sentence saying when its initial documentation is asked for or through which channels.
- **Bears on.** Neither task's scored solution: both trees are Long-Term and Military only, and the subjects whose replacements exist are the ones the tasks exercise. Task 0's undecided request `b609…` was seeded with its 08-03 requests on the request date, so it is unaffected.
- **Affected.** `hardship.extended.yaml`, the `overwrite` entries of `hardship_ext_service_documentation[0]`, `hardship_ext_longterm_extension[0,1,2,3,4]` and `hardship_ext_service_extension[0,1,2,3]`.
- **Judgement on "kept with reason".** On my independent assessment the item is not sound to keep as an observation. I will compare against the reworker's stated reason after this freeze.

**Retired counting rules bound to in-force gates (render-layer note 2; my N-O2).**
- For Long-Term and Military the replacement "end date on record" governs. In both worlds the gate is evaluated before the booking, when the record equals the base formula (2026-08-18 and 2026-10-14), so keeping this as an observation is sound for those tiers.
- `documentation_period_lapsed` / R-2: the cure overwrite's replacement now defines the period for every tier ("where none stands, … the tier's documentation days counted from the day after the request date or, for a Military Service Hold request, the due date its initial documentation request set"), so it is covered.
- `extension_before_end` / `hold_term_completed` on the other tiers: not covered. That is part of R4-F1, not a separate item.

**Spouse active-duty note.**
- The Military variant's `entry_gate: {consumer_or_spouse_on_active_duty: true}` lives in the frozen base `variants` block. No extended policy, compute or task of this difficulty reads it, and both personas are the servicemember himself or a consumer who is not military.
- The base is the blueprint's, which this difficulty may not edit. Keeping it as an observation is sound for this audit; it is a blueprint-level matter.

### Unchanged sections (revision 4)

- The conflict scan (N-1 closed), the rest of rule/compute equivalence, the prerequisite graph and sentences (E1–E5), the remaining override declarations and the factor ladders are all re-confirmed unchanged by the mechanical re-check.
- Tools are unchanged (same hash).

### findings (revision 4, before the reveal)

- **Cure rule/compute item:** closed, with residual observation R4-O1.
- **R4-F1:** SOURCE-POLICY RED, latent, newly recognised.
- **N-O2:** for Long-Term and Military, kept as an observation (sound); the other tiers are covered by R4-F1.
- **Spouse note:** kept as an observation (sound).

### reveal comparison and closing_checklist (revision 4)

Written after the round-4 reveal (about 01:10Z).

- **Scored values.** None moved. This matches the reworker's claim; every per-factor figure and baseline also equals my recomputation.
- **Cure rule against compute: CLOSED** (residual observation R4-O1, as frozen above).
  - The reworker's argument that a cure notice "cannot be stacked on an earlier cure notice for the same request" holds by the in-force resubmission cap and the base's in-force "a further incomplete submission is denied".
  - Note, however, that its premise "the base asks 'on the request date'" cites R-1, which `hardship_ext_service_documentation` retires as a whole sentence (R4-F1). The compute stays correct regardless, because with a single request of the kind both branches read the original.
- **Overwrite scope (render-layer note 1): kept with reason. I do not accept the reason; R4-F1 stands as a latent SOURCE-POLICY RED.**
  - Reason (a), that an overwrite cannot carry a tier qualifier, describes a difficulty in authoring the fix. It does not show that the charter is self-consistent.
  - Reason (b), that requests on the uncovered tiers are POLICY_NOT_COVERED and go to a human, conflicts with clauses that remain in force:
    - The base `hardship_evt_extension` still regulates extensions of every tier: "Extensions are granted only on a hold whose status is active", "An extension is granted only when the handling date is no later than the hold's current end date…", and "The request must also arrive no earlier than extension_request_window_days calendar days before that end date, must carry updated documentation…".
    - The base parameters give Documented holds max_extensions 1 and extension_days 30.
    - The blueprint scope lists extending a hold in this difficulty.
    - A reader of the published rules can therefore defensibly grant a Documented extension of 30 days by restoring the retired X-1, or hand off for lack of an in-force rule. Two defensible outcomes, which is exactly what the policy relationship forbids.
    - The same holds for the in-force `hold_term_completed` gate, whose current end date has no in-force definition for Documented, Disaster and Financial Assistance holds.
  - Reason (c), that no task touches these tiers, is true, and it is why the finding is latent. It does not make the charter consistent.
- **Retired counting rules (render-layer note 2): sound** for Long-Term and Military and for the documentation period. The uncovered tiers' end-date counting is part of R4-F1.
- **Spouse entry-gate note: sound as an observation.** It is frozen blueprint variant data, unread by this difficulty.

**closing_checklist (revision 4).** The difficulty does not close on the source layer in round 4. Both tasks PASS all four relationships, and nothing that passed in revision 3 regressed. But the charter carries R4-F1: a latent SOURCE-POLICY RED that is pre-existing and newly recognised this round, not introduced by the round-4 rework. The other checklist items are as in revision 3: coverage and disjoint scopes; trees of 3/2 and 2/1 with user writes and no cycle; factors within bounds and bearing weight; gates 8/8 green per the coordinator's snapshot (not re-run by the auditor).

**findings (revision 4, final):**

| item | status |
|---|---|
| Cure rule/compute | closed |
| R4-O1 | observation |
| R4-F1 | SOURCE-POLICY RED (latent, charter-global; bears on neither task's scored solution) |
| N-O2 | observation, for Long-Term and Military |
| O-4 | observation |
| Spouse note | observation |

## revision_5

### charter_global_frozen (revision 5)

- **Freeze.** Written before reading the round-5 section of `worklog.md` or the round-5 `tasks/{0,1}.json`. The system clock read 2026-10-11T01:21:52Z at the start of the re-audit.
- **Inputs.**
  - `hardship.extended.yaml`: sha256 `740691dcd56efe54cee664d2156967bcb74ba75ea8767ae30f77e1fcd7666e3f`, changed from round 4's `9f2d8aec…`.
  - `task_tools.py`: `3d6eb589…`, unchanged.
  - Views `r5/0.view.json` and `r5/1.view.json`: unchanged.
  - Gate snapshot `/tmp/env0050_views/gates/env0050_hardship_hold_requests_r5_gates.txt`: 8/8 OK.
- **Base section.** Still verbatim (all keys equal); `blueprint/` is unchanged.
- **Mechanical re-check.** Every `compute_basis` quotation, `baseline.rule` sentence, `policy_source`, `replaced_by` and `superseded_clause` is verbatim, with none missing in any of the 7 policies.
- **Structure.** The factor ids, effects and counts are unchanged (5 / 6 / 4 / 4 / 5 / 6 / 4), as are the compute binding counts. The prerequisites E1–E5 are unchanged in sentence, kind, gate and form. The `cure_notice.original_due` binding is the round-4 one.

### R4-F1 (wholesale-retired base clauses with tier-limited replacements): CLOSED

Every retired clause now has an in-force replacement covering every tier the base clause applied to.

| retired base clause | replaced by | tiers now covered |
|---|---|---|
| R-1: initial documentation ask, due date, channels | `hardship_ext_service_documentation` | Military as worked out; "for a request of any other tier whose documentation is required, Ridgeline asks for the tier's documentation type on the request date with a due date the tier's documentation days later, and accepts it only through the tier's documentation channels" |
| R-2: documentation period | cure notice and service documentation | The two replacements agree: Military runs to the initial request's due date, other tiers run the tier's documentation days from the day after the request date, and once a cure notice stands both run to the cure due date. N-1 stays closed. |
| R-3: resubmission | cure notice | "…while the request's resubmissions remain below the tier's resubmission maximum and the due date in force has not passed: the cure due date … where a cure notice stands, otherwise the due date of the original documentation request". The no-cure case is now covered. |
| X-1: number and length of extensions | Long-Term and Military extensions | Each states its own tier, cross-refers the other ("under its own extension rule"), and gives the same sentence for every other tier ("up to the tier's maximum number of extensions, each extension adding the tier's extension days"). The two replacements agree. |
| X-2 and end-clause 1.2: current end date | Long-Term and Military extensions | "For a Long-Term Hardship Hold [Military Service Hold], as for a hold of every other tier, the hold's current end date is the end date on record…". The in-force gates `extension_before_end` and `hold_term_completed` now have an in-force counting basis on every tier. |
| X-3: annual-limit refusal | Long-Term extension | Long-Term uses the days the long-term extension adds; "any other tier that counts toward the limit" uses the tier's extension days. Military does not count toward the limit. |
| X-4: decision timing | Long-Term and Military extensions | The booking is the decision for Long-Term and Military; for any other tier, "within the tier's extension decision days, counted as business days". The two agree. |

Re-running round 4's demonstration: a running Documented Hardship Hold's extension now has an in-force answer. It may be extended up to 1 time, adds 30 days, is refused if the rolling-12-month hold days + 30 exceed 120, and is decided within 5 business days; its current end date is the end date on record. There is a single reading.

- **Residual (observation R5-O2).** The Long-Term and Military extension policies now legislate the other tiers' extensions in their own rule text. That is a choice of where the clause lives, not a conflict: the two texts are identical for the other tiers, and the overwrite contract is clause-granular. The KB render surface will show other-tier extension law inside the Long-Term and Military documents.

### R4-O1 (fallback could read a prior cure notice): CLOSED

- **New cure sentence:** "No cure notice is owed once the resubmissions of that kind on the request have reached the tier's resubmission maximum, counting every submission of that kind after the first as one used; such a request is denied for documentation not received instead."
- A cure notice can now arise only while the resubmissions are below the maximum (1 on every documented tier), that is, only on the first submission of the kind. When it arises, no earlier cure notice of that kind stands, so `original_due`'s fallback branch ("latest of the kind") is always the initial request. Rule and compute agree on every reachable state.
- The new denial clause agrees with the base's in-force "a further incomplete submission is denied with documentation_not_received".

### New-defect and regression scan (revision 5)

- **E3 against the new cure sentence (observation R5-O1).** Take another undecided Long-Term request whose first submission was cured and whose resubmission (dated after the cure notice) is also incomplete. E3 is unmet there: the resubmission has no documentation request dated on or after it. No cure notice is owed now; the request is "denied … instead". The denial removes it from E3's scope ("undecided"), so the gate is still resolved by exactly one action in that state. But that action is a base `hardship_hold_denied`, which no task tool of this difficulty performs, so in such a world the recertification would wait on an action the agent cannot take.
  - This is not a conflict or a second reading: in each state exactly one action applies.
  - It is not present in either task world: `b609…` has a single submission, so its resubmissions are 0 < 1.
  - Recorded as an observation, not a red light.
- **Cross-problem orders.** No new one. The added sentences are tier scoping, cross-references between the two extension policies ("under its own extension rule"), the cure owed-condition and the resubmission due date in force. None orders two problems of one tree. E1–E5 are unchanged.
- **Rule/compute.** No compute changed, and no new sentence carries a quantity the compute should implement for the tasks' tiers. The other-tier extension days and decision days are not computed by any policy of this difficulty, because no tool books them.
- **Factor ladders.** Unchanged, and still within bounds.
- **Tools.** Unchanged.
- **Kept observations.** O-4, N-O2 (Long-Term/Military counting metadata) and the spouse entry-gate note remain observations.

### findings (revision 5, before the reveal)

| item | status |
|---|---|
| R4-F1 | closed |
| R4-O1 | closed |
| R5-O1 | new observation |
| R5-O2 | new observation |
| New red lights | none |

### reveal comparison and closing_checklist (revision 5)

Written after the round-5 reveal (about 01:24Z).

- **Worklog.** It lists eleven changed sentences, and each matches what I found in the frozen section: R-1, R-2 and R-3 via service documentation and the cure notice; X-1, X-2, end 1.2, X-3 and X-4 via the two extension policies; and the new cure owed-condition.
  - The `superseded_clause` texts are unchanged.
  - The compute_basis edits of `lt_held` and `sx_held` only follow the reworded current-end-date sentence, and both still quote verbatim.
  - No compute, factor, parameter, prerequisite sentence or tool changed. This agrees with my mechanical check.
- **Scored values.** None moved; all equal my recomputation.
- **R4-F1 and R4-O1:** closed.
- **New red lights:** none.
- **New observations:** R5-O1 (in the "resubmission already used" state, E3 is resolved by a base denial that no tool of this difficulty performs; neither world reaches that state) and R5-O2 (other-tier extension law now lives in the Long-Term and Military policy texts).

**closing_checklist (revision 5).** **The difficulty closes on the source layer.**

- **Audit files.** One-to-one; revisions 1–5 are appended in order, with older text untouched. Both revision-5 comparisons are PASS.
- **Coverage and scope.** The 7 extended policies are fully covered by two pairwise-disjoint scopes that equal the derived trees. Task tools and GT are closed. The uuid8s are independently generated and frozen.
- **Trees.**
  - Task 0: 3 prerequisite problems, 2 `value_input` edges, the user-owned Long-Term extension.
  - Task 1: 2 prerequisite problems, 1 `value_input` edge, the user-owned service extension.
  - No cycles, and the difficulty-wide graph E1–E5 is acyclic.
- **Factors.**
  - Every computation has a self-sufficient baseline and 4–6 factors, with at least 2 `parameter` and at least 1 `method`.
  - Each task has a multi-source factor and a cross-difficulty factor.
  - Every ladder has at least three reachable, distinct tiers stated in full in its rule.
  - Every factor bears weight against an honest baseline, and each all-baseline figure differs from gold: 7 / 90 / 17 / 17 and 20 / 180 / 33.
- **Policy self-consistency.** Every overwrite is declared, and each replacement covers every tier it retires. Rule and compute are equivalent. Every prerequisite sentence is in state form and matches its condition.
- **Gates.** 8/8 green per the coordinator's round-5 snapshot (not re-run by the auditor, per Step 0), at charter `740691dc…` and tools `3d6eb589…`.
- **Remaining observations** (not grounds for rework): O-4, N-O2 (Long-Term/Military counting metadata), the spouse entry-gate note, R5-O1 and R5-O2.
