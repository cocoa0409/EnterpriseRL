# Policy-task audit — home_oxygen_service / charter-global

## charter_global_frozen

- Freeze time: 2026-10-12T19:13Z (written before any task's GT was revealed; nothing in this section derives from a masked field).
- Auditor: erl-task-policy-audit, a separate agent from the instantiator. A previous auditor on this unit was cut off by an account limit before it wrote anything, so this audit starts clean.
- Hashes, re-computed by the auditor and matching the brief and `.audit_views/policy_task/home_oxygen_service/HASHES.txt`:
  - `tasks/home_oxygen_service/oxygen.extended.yaml` sha256=0ed08c3f1f5c0972593237f6285bc7adbdb2b5138b95b98eb538d69d14fdc9af
  - `tasks/home_oxygen_service/task_tools.py` sha256=5f5da85d02e12e32350cd29aa08927f65b95ed7aa9bf54a749cfb274ff04adc5
  - `.audit_views/.../0.view.json` sha256=bf5fca41ecbfa6364e4376043088c6a1d08a9030609baf645ad505a565912525
  - `.audit_views/.../1.view.json` sha256=3f21940c6aa2cfc5bd88466f2d813fa6c0cf0b601abda174429e5349ca212f8c
- Fields read: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/oxygen.yaml`, and the variant parameters of `products/coverage.yaml`); the extended charter; `task_tools.py`; the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (for the semantics of MONTHS, DAYS, LATEST, CFIELD and the other functions); and the masked views (frozen_time, user_scenario, initial_state).
- Fields masked and not read: evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure*. No `tasks/*.json` was opened, and no recursive search was run over the scenario directory.
- Entry conditions: the gate snapshot came with the brief. Eight gates are green (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE, CACHE-DIFF info). check_traceability returns rc=1 because the only misses are the 7 task-tool names, which are deferred to post-render by design. This is recorded as an observation, not as incomplete input.

### policy_conflict_scan

- The base copy is verbatim. A key-by-key comparison of `products/oxygen.yaml` against the base section of the extended charter (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) found all of them equal.
- The 7 extended policies have pairwise disjoint subjects and target tools:

| Policy | Subject | Target tool | Owner |
| --- | --- | --- | --- |
| setup_start_day | oxygen_setup_complete | record_oxygen_setup_e2e7878b | agent |
| stay_suspension_day | oxygen_suspend | record_oxygen_suspension_f17584ff | agent |
| paid_in_full_equipment_month | oxygen_rental_paid | record_oxygen_equipment_payment_51bbc3fc | agent |
| post_break_period_start | oxygen_period_restart | restart_oxygen_payment_period_b66f451e | user |
| paid_in_full_contents_month | oxygen_contents_paid | record_oxygen_contents_payment_7caaff46 | agent |
| new_primary_first_day | oxygen_payer_update | confirm_oxygen_primary_coverage_03bf25f6 | user |
| return_closing_day | oxygen_return | confirm_oxygen_return_2399228d | user |

- Overlapping subjects with base: each extended policy refines the base policy it cites. No two extended policies write the same field in the same state:
  - setup writes setup_date and rental_period_start_date from order_received.
  - restart writes rental_period_start_date from suspended.
  - new-primary writes rental_period_start_date on a coverage change.
  The three are separated by trigger state.
- Cross-category reads:
  - coverage: variant_name, allowed_pct_of_fee_schedule, last_eligibility_check_date, effective_date, status, coverage_priority.
  - pap: status, suspended_date, rental_period_start_date, coverage_id, ownership_date, and pap_billing pap_rental_paid.
  - beds: status, suspended_date, rental_period_start_date, hospice_election_date.
  - All are read-only and each is declared in `cross_category`.
- One derived (undeclared) order between two policies sharing a predecessor:
  - The equipment-payment rule waits on "the oxygen record shows the system set up, with its setup date and an active rental". The base `oxygen_billable_status` eligibility also requires rental_active. The suspension write moves the record off rental_active.
  - So within any tree that contains both, the policy entails payment before suspension. This is an entailed order, not a stated cross-problem order; see observation O-6.
  - Both orders give the same terminal values (shown in task 0's file). It matters only if GT scores the relative order of these two writes.
- Scope (pre-reveal, from the views only): task 0's world exercises setup, equipment payment, suspension and restart. Task 1's world exercises contents payment, new primary and return. Together they cover all 7 extended policies exactly once. charter_scope is compared after the reveal.

### rule_compute_equivalence

I swept every compute binding against its `compute_basis` quotation, and every quotation back to the `rule`.
- A script check confirmed that every `compute_basis` sentence and every `baseline.rule` sentence is verbatim in its policy's `rule`.
- I also read each binding against its sentence. Notes:
- **setup_start_day**: the three tiers of the first day at home, the three conditions (allowance, reach and lead, each counted as later minus earlier), and the YYYY-MM-DD result all correspond.
- **stay_suspension_day**: the evidence-day ladder ("otherwise, when"), reach, home-use window and established rental all correspond. Small asymmetry: the home-use window has no `>= 0` guard in compute (`home_use_gap_days <= in_use_window_days`), while the rule says "falls no more than N days before". A refill dated after the evidence day passes in compute, and the rule is silent on that case. Not reached by task 0 (refill 2026-07-06 is before evidence day 2026-07-18). Recorded as observation O-4.
- **paid_in_full_equipment_month**: these all correspond:
  - usage share, flow combination (MX for the high-flow + portable tier), payer high-flow %, rental position (paid less reversed under the record's coverage), discharge training, multi-rental, the plan allowed %;
  - the stated multiplication order and the single rounding.
- **post_break_period_start**: these all correspond:
  - the day-home ladder, filing reach (DAYS(day home, NOW)), coverage recheck (`>= 0` and `<= limit`), paid-month floor, and paid-month span (DAYS(latest paid service_from_date under the coverage, suspended_date)).
  The overlap between tiers 1 and 2 of the day-home ladder is a statement-level defect; see factor_ladders and F-3.
- **paid_in_full_contents_month**: usage, flow treatment, position (+1), refill size (average), refill frequency (`within_months=6`, which in compute is MONTHS in [0,6)), PAP bundle and plan % all correspond.
- **new_primary_first_day**: the anchor ladder corresponds. compute adds `next_billed_start > new_effective_day` where the rule says the earlier coverage "denied a later month". A month later than a paid month that began less than one whole month before the effective date necessarily begins after the effective date, so these are equivalent. Window, check and lag correspond.
- **return_closing_day**: need-end ladder ("otherwise, when"), carve-out reach, last-use window (`>= 0` and `<= window`) and closing check all correspond.
- No compute binding lacks a rule basis, and no rule sentence lacks an implementation, apart from O-4 above.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy. allowed_amount is computed by two policies, but through two different tools (51bbc3fc for equipment, 7caaff46 for contents).
- uuid8s: e2e7878b, f17584ff, 51bbc3fc, b66f451e, 7caaff46, 03bf25f6, 2399228d. They have no common prefix, no sequence and no copied tails, so they look independently generated.
- Tool bodies (task_tools.py): each is an unconditional `ctx.update` / `ctx.create`. No tool checks status, refuses, errors or hints on an unresolved prerequisite.
- Docstrings name no other tool and state no write's position relative to another problem.
  - Words such as "before" appear only in "read from the … lookup before the call" (argument provenance).
  - "Afterwards" describes the tool's own effect.
  - "first"/"after the cap" are ordinal or situational.
  - Observation O-7.

### prerequisite_graph

The graph:
- setup ← [].
- suspension ← setup.
- equipment ← setup.
- restart ← suspension, equipment.
- contents ← [].
- new_primary ← contents.
- return ← new_primary.

Check-7 results:
- Every policy has a filled `prerequisite`.
- Every `problem` is an extended id, never a base policy and never itself.
- The graph is acyclic.
- Every `policy_source` is verbatim in its own policy's rule (script check) and is not restated in the depended-on rule.
- `form`: state on 6 edges and action on 1 (return ← new_primary), with `fallback_reason` present exactly on that one.
- `resolved_by` equals the depended-on target_tool on every edge.
- Every `gate` names a real compute binding of the blocked policy: stay_evidence_day, training_rate_pct, home_again_day, old_period_paid, earlier_paid_start, close_reach_days.
- No authoring-viewpoint phrasing ("in this task", "at the opening").
- Condition strength:
  - restart ← suspension: `condition` says suspended_date "carries the date the stay began". That matches the sentence ("with the date it began"). But the suspension policy's own fall-back dates the suspension on the report day, so in a world where the evidence day fails, the suspension write cannot make this condition true. That is a charter-level reach issue (observation O-5). Task 0's world takes the evidence tier, so it is not reached there.
  - new_primary ← contents: `condition` adds "including the month running on the new effective date". This is a specialisation of "each contents month the earlier coverage paid", not a strengthening.

### prerequisite_sentences

Four-point test on each edge: ordering connective, waited-on state or action, no tool/id/snake_case, and the same strength as `condition`.
1. **suspension ← setup**: "A stay is recorded as a suspension only after the oxygen record shows an active rental with its setup date."
   - "Only after" plus a record-visible state (status, setup date). Passes.
   - Which write brings the state about from a record lacking it: only the setup write (order_received → rental_active with setup_date). Restart also sets rental_active, but only from suspended, which already presupposes a setup date.
   - Single reading: sentence + record (order_received, no setup_date) + setup rule ("a home oxygen system that has been delivered while its oxygen record still shows the order as awaiting setup is recorded as set up") → record the setup.
2. **equipment ← setup**: "An equipment month is posted as paid only after the oxygen record shows the system set up, with its setup date and an active rental."
   - Passes. One write (setup). Same derivation as edge 1.
3. **restart ← suspension**: "A new payment period after a stay is not opened until the oxygen record shows the stay as a suspension with the date it began."
   - "Not … until" plus a state. Passes.
   - One write (the suspension write; no other tool of this difficulty sets status suspended).
   - Derivation: the record is not suspended, so the suspension rule ("an inpatient or skilled nursing stay that is reported after it began is recorded as a suspension") applies.
4. **restart ← equipment**: "The first day of a new payment period after a stay is fixed only after the oxygen claim history carries the payer's paid line for each equipment month that began before the stay."
   - Passes. One write (equipment payment; the contents tool posts contents lines, not equipment months).
5. **new_primary ← contents**: "A new coverage's first day of service for the oxygen is fixed only after the oxygen claim history carries the paid line of each contents month the earlier coverage paid after the payment cap."
   - Passes. One write (contents payment).
6. **return ← new_primary** (action form): "A return for a patient whose need ended before the confirmation is dated only after the change to the patient's current primary coverage has been confirmed on the oxygen record."
   - "Only after" plus an action in business words. No tool name. Passes.
   - The `fallback_reason` argues that the state "oxygen record naming a coverage" is also written by the setup write.
   - But the return applies only to delivered records (rental_active / suspended / payment_cap_reached), and setup only to order_received records. So the state "the oxygen record names the coverage that is now active and primary" would single out the coverage-confirmation write in every world the return rule reaches. The fallback is unjustified: observation O-3, naming that state.
- No rule carries a second wording of any dependency, a tool name or another problem's id.
- The bare token `allowed_pct_of_fee_schedule` appears in the equipment and contents rules. It is a coverage parameter name inherited from the base wording, not a tool or policy id.
- No rule states a cross-problem order that grounds no declared edge. The payment-before-suspension order is entailed by edge 2's state plus base eligibility (O-6), not stated.

### override_declarations

Each `base_policy_refs` sentence is checked below; each line gives whether extended follows the sentence or handles the quantity differently.

- **setup_start_day / oxygen_qualification** (overwrite: []):
  - Qualifying test, portable billability, rx validity: followed.
  - "Setup is made within setup_lead_hours of a complete order, on the day of hospital discharge where discharge_same_day_setup is true…": not contradicted. The training-delivery tier dates the setup on the first day at home, which is consistent with "on the day of hospital discharge".
  - Prior auth and eligibility: inherited.
  - No undeclared override inside the cited policy.
  - Outside the cited refs, the base **event** model maps `oxygen_delivery` (delivery_purpose initial_setup) → `oxygen_setup_complete` with `setup_date: service_date, rental_period_start_date: service_date`. The training-delivery tier sets setup_date to a different date (the most recent backup-cylinder or refill delivery). That base mapping is not named in `overwrite`. It is not a policy sentence of the cited refs, and the extended rule addresses the exact situation specifically, so it is recorded as observation O-1, not RED.
- **stay_suspension_day / oxygen_suspension_break**:
  - "admission date as suspended_date" is declared superseded, and the merged semantics are unique.
  - "no month whose first day falls during the suspension is billed", the resume allowance, the longer-break restart and the travel clause are untouched or inherited.
- **paid_in_full_equipment_month / oxygen_evt_monthly_billing, oxygen_payment_cap, oxygen_group_ii_retest**:
  - Fee sentence declared superseded. The superseded clause begins "The month's fee is `stationary_monthly_fee` …", so the usage-share scaling, which also changes "the fee", falls under the named clause.
  - Allowed-amount/rounding sentence declared superseded.
  - Anniversary/month number, the low-flow treatment (consistent with base `low_flow_fee`), the add-on when furnished and billable, contents included, group II, rental_active only, and the line codes are all followed.
  - Payment cap sentences (stop at cap; earlier coverage/period months not counted toward the cap): followed. The rental-position step counts paid months under the coverage across periods, but it is a rate step, not the cap.
  - Group II: followed.
- **post_break_period_start / oxygen_suspension_break**: "A longer break starts a new payment period on the return-home date with the month count back at 1" is declared superseded. "Needs the class's new_period_requirements before billing" is inherited.
- **paid_in_full_contents_month / oxygen_contents_billing**:
  - The fee×allowed sentence is declared superseded.
  - Anniversary days, the minimum deliveries per month, "concentrator… never bill contents" and "only after the cap" are inherited.
- **new_primary_first_day / oxygen_payer_transition**:
  - "a new payment period begins under it on the first date of service it covers" is declared superseded (really a refinement).
  - "months under earlier coverage do not count toward the new cap" is inherited.
  - "the new coverage pays only when payer_entry_requalification is met…" is inherited. It governs payment, not the move; see task 1 observation.
  - "moves only once that coverage is verified (active)" is inherited.
- **return_closing_day / oxygen_return_pickup**:
  - "billing stops with the last month that began before the return" is declared superseded.
  - Return-only-at-confirmation-of-approved-request, pickup lead and the charges are inherited.
- Result: no undeclared override within the cited base policies. O-1 is the only base-vs-extended divergence, and it lives in the base event model.

### factor_ladders

Per policy, each factor's label, `decides`, tiers (charter values) and cross-difficulty tag.

**setup_start_day** (4 factors: 1 method, 3 parameter)
- home_arrival_anchor (method → at_home_day): hospital + backup after setup → latest backup; SNF + refill after setup → latest refill; otherwise → setup delivery. Multi-source (oxygen holding + service history).
- training_delivery_allowance (parameter): 2 / 1 / 0.
- setup_backdating_reach (parameter, xd coverage): 365 / 180 / 90.
- order_delivery_lead (parameter): 1 / 2 / 0.

**stay_suspension_day** (4 factors: 1 method, 3 parameter)
- stay_evidence_source (method, xd pap): PAP-suspended date / bed-suspended date / report day, with explicit "otherwise, when". Multi-source (oxygen status + PAP record).
- stay_backdating_reach (parameter, xd coverage): 365 / 180 / 90.
- home_use_window (parameter): P(cylinder) / P(liquid) / 0.
- established_other_rental (parameter, xd pap): 3 / 1 / 12.

**paid_in_full_equipment_month** (6 factors: 1 method, 5 parameter)
- awake_usage_share: 60 / 50 / 80 / 100.
- flow_fee_combination (method): MAX(raised, plus add-on) / raised / reduced + add-on / plus add-on. These are genuinely different algorithms, so the method label is honest.
- payer_high_flow_rate (xd coverage): 40 / 30 / P(50).
- rental_position_step: 110 / 90 / 100.
- discharge_training_rate: 105 / 103 / 100. Multi-source (service delivery date vs holding setup_date, plus referral).
- pap_multi_rental (xd pap): 97 / 99 / 100. **Tiers 1 and 2 overlap as stated (F-3).**

**post_break_period_start** (5 factors: 1 method, 4 parameter)
- home_return_evidence (method): visit after suspension / refill after suspension / confirmation day. **Tiers 1 and 2 overlap as stated (F-3).**
- restart_filing_reach (xd coverage): 365 / 30 / 7.
- coverage_recheck_window (xd coverage): 90 / 30 / 0.
- closing_paid_floor: 1 / 2 / 3. Tiers decided by coverage class, but cross_difficulty is null (labelling observation O-8).
- stay_paid_span: 31 / 28 / 21. Same labelling observation O-8.

**paid_in_full_contents_month** (6 factors: labelled 1 method, 5 parameter)
- contents_usage_share: 60 / 50 / 80 / 100.
- contents_flow_treatment (labelled method): +u/2 % / +u % / −r % / unchanged. **Mislabelled (F-2):** every tier is the same formula `fee × (100 + x)/100` with x ∈ {u/2, u, −r, 0}, so the tiers substitute a number and do not change the algorithm.
- contents_position_step: 90 / 95 / 100.
- refill_size_rate: 110 / 90 / 100.
- refill_frequency_rate: 105 / 95 / 100.
- contents_pap_bundle (xd pap): 97 / 99 / 100. **Tiers 1 and 2 overlap as stated (F-3).**

**new_primary_first_day** (5 factors: 1 method, 4 parameter)
- covered_day_anchor (method): first day of most recent coverage-inactive month / first day of that paid month / effective date. Tiers are disjoint. Multi-source (coverage effective date vs oxygen claim history).
- new_coverage_reach (xd coverage): 365 / 180 / 90.
- inactive_denial_window (xd coverage): 180 / 120 / 60.
- new_coverage_check (xd coverage): 90 / 30 / 0.
- inactive_denial_lag: 60 / 45 / 30. Tiers decided by the earlier coverage class, but cross_difficulty is null (O-8).

**return_closing_day** (4 factors: 1 method, 3 parameter)
- need_end_source (method, xd beds): hospice election / suspension date / confirmation day, with explicit "otherwise, when".
- carve_out_reach (xd coverage): 365 / 180 / 0.
- last_use_window: P(cylinder) / P(liquid) / 0.
- closing_coverage_check (xd coverage): 90 / 30 / 0.

Results across all policies:
- Every ladder has at least 3 tiers, and every tier's value is a charter K/P value.
- Within each ladder no two tiers select the same value or method.
- Every tier is stated in the rule and implemented in the `decides` binding. Every factor's `baseline` equals its fall-through tier.
- Every `baseline.rule` is in the rule and gives a definite number by itself:
  - setup: initial-setup delivery date;
  - suspension: report day;
  - equipment: (stationary + add-on when billable) × allowed %;
  - restart: confirmation day;
  - contents: post-cap fee × allowed %;
  - new primary: effective date;
  - return: confirmation day.
- Disjointness as stated fails in three ladders (F-3). Two use "when A, X; when B, Y" with no "otherwise", and A and B can hold together:
  - pap_multi_rental and contents_pap_bundle: a PAP record with the same coverage, no ownership date, at least 3 months rented and 13 or more paid rental months satisfies both tiers → 97 vs 99.
  - home_return_evidence: a suspended record with both a technician visit and a cylinder refill after the suspension date satisfies both tiers → two different dates.
- Label honesty fails for contents_flow_treatment (F-2).
- Business realism observation (O-9; I cannot demonstrate that no business would publish these):
  - discharge_training_rate pays a 105%/103% uplift because the system was delivered before discharge.
  - order_delivery_lead's 0-day fall-through.
  - closing_paid_floor / stay_paid_span gate a back-dated restart on paid-month counts and the suspension's distance from the last paid month.
- Counts after removing struck factors:
  - Contents: 0 honest methods. contents_flow_treatment is relabelled as parameter, and contents_pap_bundle is struck for overlap.
  - Restart: 0 methods. home_return_evidence is struck for overlap.
  - Equipment: 5 factors, 1 method (pap_multi_rental struck), still within bounds.
  - The other four policies are within bounds.

### findings

- **F-1 — none (no SOURCE-POLICY RED at charter level).** The override sweep, the rule/compute equivalence, the prerequisite graph and the prerequisite sentences all pass. The divergences found are observations O-1 … O-9 below.
- **F-2 — SOURCE-FACTOR RED (charter-global, mislabelled method). Affects: task 1 (contents computation).**
  - Symptom: contents_flow_treatment is labelled `method`, but its four tiers differ only in the percentage that enters one formula.
  - Evidence:
    - Rule: "the scaled contents fee is raised by half of the class's `high_flow_uplift_pct` percent; … raised by the full `high_flow_uplift_pct` percent; … reduced by the class's `low_flow_reduction_pct` percent; otherwise it is unchanged."
    - Compute `contents_flow_fee`: `usage_contents_fee * (100 + P('high_flow_uplift_pct') / 2) / 100` / `… (100 + P('high_flow_uplift_pct')) / 100` / `… (100 - P('low_flow_reduction_pct')) / 100` / `usage_contents_fee`. That is one expression `fee*(100+x)/100` with x = 25, 50, −50, 0.
  - Consequence: once relabelled, the contents computation has no method factor, below the floor of 1. Per-task demonstration in 1.md.
  - Location: `oxygen.extended.yaml`, `oxygen_ext_paid_in_full_contents_month.factors[contents_flow_treatment]`.
- **F-3 — SOURCE-FACTOR RED (charter-global, ladder tiers overlap as stated). Affects: task 0 (restart computation, equipment computation) and task 1 (contents computation).**
  - (a) home_return_evidence:
    - Rule text: "when the record is suspended and a technician visit is on record later than the suspension date, the day home is the date of the most recent technician visit; when the record is suspended and a cylinder refill is on record later than the suspension date, it is the date of the most recent cylinder refill; otherwise …"
    - Situation: suspended 2026-07-18, visit 2026-10-20, refill 2026-10-24. Sentence 1 gives 2026-10-20 and sentence 2 gives 2026-10-24. Compute resolves this by precedence, which the rule does not state. Compare the "otherwise, when" used in stay_evidence_source and need_end_source.
  - (b) pap_multi_rental and (c) contents_pap_bundle:
    - Rule text: "by `rented_pap_pct` percent when the patient's PAP device record names the same coverage, carries no ownership date and its payment period began at least `rented_pap_min_months` … months before the posting date; by `owned_pap_pct` percent when the PAP device record carries an ownership date or 13 or more PAP rental months have been paid".
    - Situation: same coverage, no ownership date, 14 months rented, 13 paid. 97 or 99.
  - Consequence: the restart computation's only method factor fails the disjointness test (0 methods left). The equipment and contents computations each lose one parameter factor. Neither task world reaches the overlap; see the task files.
  - Location: the three `factors[]` entries and the corresponding rule sentences.
- **Observations (not grounds for rework):**
  - **O-1** Base event trigger `oxygen_delivery(initial_setup) → setup_date: service_date` diverges from the setup policy's training-delivery tier and is not named in `overwrite`. The cited base policy sentences agree with extended. If the KB renders the trigger mapping as a rule, it would offer a second setup date (the initial-setup delivery date). This is a render-stage risk.
  - **O-2** check_traceability rc=1 pre-render (7 task-tool names), deferred by design.
  - **O-3** The action-form fallback on return ← new_primary is unjustified: the state "the oxygen record names the coverage that is now active and primary" singles out the coverage-confirmation write in every world the return rule reaches (setup applies only to order_received records, which cannot be returned).
  - **O-4** The suspension home-use window has no `>= 0` guard: a refill after the evidence day passes in compute, and the rule is silent on it.
  - **O-5** The restart ← suspension condition ("suspended_date carries the date the stay began") cannot be met by the suspension write when its evidence tier fails and it dates on the report day. Charter-level reach only.
  - **O-6** Payment-before-suspension is entailed (edge 2 state "an active rental" plus base `oxygen_billable_status`), not declared. Both orders give equal terminal values.
  - **O-7** Docstrings contain "before the call" (argument provenance). No tool names and no sequence statements.
  - **O-8** cross_difficulty labels: closing_paid_floor, stay_paid_span and inactive_denial_lag choose their tier by coverage class but are tagged null.
  - **O-9** Business realism of some ladders, as listed under factor_ladders.

## closing_checklist

Written after both tasks' reveals.

Timestamp note: the "Freeze time" stamps written in 0.md and 1.md (19:20Z and 19:25Z) were estimated and run late. Measured by the shell clock, the GT files were first opened at 19:16Z. Both frozen sections were on disk before that read, so the order freeze-all-then-reveal held. The frozen text was not edited afterwards; only the comparison and findings sections were appended.

- **Audit files:** one per task (`0.md`, `1.md`) plus this file. First revision; no older revisions.
- **Coverage and scope:**
  - Task 0 charter_scope = {setup, equipment payment, suspension, restart}. Task 1 = {contents, new primary, return}.
  - They are pairwise disjoint and together cover all 7 extended policies. Their tool sets are disjoint and cover all 7 task tools.
  - This matches the pre-reveal scope scan.
- **uuid8s:** independently generated (§ action_binding_and_uuids).
- **Problem trees:**
  - Task 0: 3 prerequisite problems, 4 value_input edges, user root.
  - Task 1: 2 prerequisite problems, 2 value_input edges, 2 user writes.
  - The difficulty graph is acyclic, with no cross-task edges.
- **Factors:** this check does not pass.
  - F-2: contents_flow_treatment is mislabelled, so the contents computation has 0 methods.
  - F-3: three ladders overlap as stated, so the restart computation has 0 methods.
  - Task 1 additionally has the 88.42 stamp and a false near-miss assertion.
  - Every declared factor does bear weight under baseline substitution, and every whole-baseline fall-back differs from gold:
    - task 0: 2026-06-20, 211.09, 2026-10-28, 2026-10-28;
    - task 1: 83.08, 2026-06-01, 2026-10-21.
- **Unique solution:** both tasks' GT matches the blind derivation on every argument and in order.
- **Gates:** not re-run by this audit; the coordinator's snapshot is cited in § charter_global_frozen. The difficulty is not at final form, so a re-run on the final form is pending.

**Difficulty result: does not pass the source-layer audit.**

| Task | Policy | Chain | Factor | Task |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **SOURCE-FACTOR RED** (F-3a) | PASS |
| 1 | PASS | PASS | **SOURCE-FACTOR RED** (stamp 88.42; F-2; false near-miss assertion) | PASS |

---

## revision_2

### charter_global_frozen (revision_2)

- Written at 2026-10-12 20:26Z (shell clock), before any round-2 task JSON was opened. Built from the charter, the tool module and the blueprint alone.
- Hashes:
  - `oxygen.extended.yaml` sha256=d2b6cfa97e40f7da01dc1455d57ea303ca19b0eb165a335f58605bd4e9d98581 — **changed**, so every charter-global section is re-derived below.
  - `task_tools.py` sha256=5f5da85d…4adc5 — unchanged, so § action_binding_and_uuids is carried forward by reference.
  - Blueprint files are unchanged; the base copy is still verbatim (key-by-key comparison against `products/oxygen.yaml` is equal).
- Gate snapshot (coordinator, after rework): all gates OK, except traceability, which still misses only the 7 unlock tool names (pre-render, deferred).
- Masked and unread before freezing: the same fields as round 1. contamination_disclosure: this auditor read the round-1 GT of both tasks during round 1, so the round-1 scored values are known. The round-2 derivations are computed mechanically from the round-2 charter and views; every figure below comes from the recomputation, not from the round-1 GT.

### Round-1 items re-checked against the artifacts

| Round-1 item | Round-2 evidence | Status |
| --- | --- | --- |
| **F-2** contents_flow_treatment mislabelled | The tiers now read: "a flat `conserver_flow_allowance` dollars is added to the scaled contents fee instead of any percentage raise" / "raised by the class's `high_flow_uplift_pct` percent" / "reduced by … `low_flow_reduction_pct` percent and the reduced fee is then compared with `low_flow_contents_floor` dollars, the higher of the two being kept" / "unchanged". Compute: `usage_contents_fee + K('conserver_flow_allowance')` / `fee*(100+u)/100` / `MX(fee*(100-r)/100, K('low_flow_contents_floor'))` / `fee`. These are an additive allowance, a multiplicative raise, a reduction floored by a maximum, and identity: genuinely different algorithms. Values 12.5 and 25.0 are in `params`, and the rule cites them by name. | **closed** |
| **F-3(a)** home_return_evidence overlap | Rule: "…the day home is the date of the most recent technician visit; otherwise, when the record is suspended, no technician visit is on record later than the suspension date and a cylinder refill is, it is the date of the most recent cylinder refill; otherwise…". Compute adds `visit_after_stay <= F('suspended_date')` (an empty visit compares as ≤). The ladder `when` text matches. Disjoint. | **closed** |
| **F-3(b)/(c)** pap_multi_rental / contents_pap_bundle overlap | Tier 1 now adds "has fewer than 13 PAP rental months paid" in the rule, the ladder, and compute (`pap_paid_months < 13` / `pap_months_paid < 13`). Tier 2 is "ownership date or ≥13 paid", and tier 1 requires no ownership date and fewer than 13. Disjoint. | **closed** |
| **O-1** base event mapping vs setup day | Setup rule adds: "The setup day worked out under this policy is the only setup date and payment-period start recorded for such a system; the date of the initial-setup delivery is carried as the setup date only when this policy keeps the setup day on that delivery." The extended rule now explicitly governs the quantity the event mapping also names. The mapping still lives in the base `events` (not a policy, so it cannot be an `overwrite` target). The render risk is reduced. | **closed (observation level)** |
| task-0 eligibility note | Setup rule adds: "For a setup recorded after the system was delivered, the eligibility response that counts toward the setup is the most recent eligibility check on the coverage's eligibility history dated on or before the setup day." This settles the reading I adopted in round 1. New observation O-10 below: it glosses the base `oxygen_eligibility_current` sentence without an `overwrite` entry. | **closed**, see O-10 |
| **O-3** action-form fallback | The edge is now `form: state`, with no fallback_reason. Sentence: "A return for a patient whose need ended before the confirmation is dated only after the oxygen record names as its coverage the coverage that is now active and primary." Four-point test: "only after"; a record-visible state; no tool, id or snake_case token; condition "oxygen_holdings.coverage_id names the coverage record that is active and primary" at the same strength. Writer of the state: only the coverage confirmation in any world the return reaches (setup writes coverage_id only from order_received, which cannot be returned). The return rule's other sentences carry no second wording. | **closed** |
| **O-4** home-use window ≥ 0 | Rule: "falls on or before the evidence day and no more than…". Compute: `home_use_gap_days >= 0 and …`. | **closed** |
| **O-5** restart←suspension condition reach | Sentence: "…shows the stay as a suspension with its suspension date." Condition: "status is suspended and suspended_date is filled in". Reachable by the suspension write on every tier. Verbatim in the rule. | **closed** |
| **O-6** payment-before-suspension entailed | The charter is unchanged here (the payment rule still waits on "an active rental"). The round-1 object was the GT closure's "either order" claim; it is checked per task after the reveal (task 0). | per-task |
| **O-8** cross_difficulty labels | closing_paid_floor, stay_paid_span and inactive_denial_lag are now `cross_difficulty: coverage`, each with its own class binding (`floor_payer_class`, `span_payer_class`, `lag_earlier_class`) so that factor binding sets stay disjoint (script check: no binding appears in two factors). | **closed** |
| task-1 requalification note | new_primary rule adds: "Moving the oxygen to the new coverage and fixing its first day of service do not wait on the new coverage's requalifying test: that test decides whether equipment months under the new coverage are paid, not the first day of service or the move itself." This is consistent with base ("the new coverage pays only when…"). It states the absence of a dependency, grounds no edge, and names no tool or id. | **closed** |
| O-2 / O-7 | Unchanged (traceability pre-render; "before the call" in docstrings). The tool module is unchanged. | unchanged |
| O-9 | Business-realism notes unchanged. New values: a flat $12.50 conserver allowance and a $25.00 low-flow floor. These are plausible supplier contract terms. | kept |

### Re-derived charter-global sections (revision_2)

- **policy_conflict_scan:**
  - Subjects, tools, owners and trigger states are the same as round 1, pairwise disjoint.
  - Cross-category reads: same, plus the coverage variant read by the three relabelled factors.
  - The payment-before-suspension entailment is unchanged.
- **rule_compute_equivalence:**
  - Script check: every `compute_basis` sentence and every `baseline.rule` sentence is verbatim in its rule, and the compute_basis keys equal the compute binding names.
  - Re-read of the changed bindings: home_again_day, contents_flow_fee, multi_rental_pct, contents_multi_pct, result (suspension `>= 0`), floor_payer_class / span_payer_class / lag_earlier_class. They match their sentences.
  - The new setup sentences (sole setup date; eligibility response) and the new_primary requalification sentence are normative statements with no compute quantity. They make no empty promise about a computed value.
- **prerequisite_graph:**
  - Same 6 edges, acyclic, every `problem` an extended id.
  - All 6 now `form: state`, with no fallback_reason.
  - Every policy_source is verbatim in its own rule and not restated in the depended-on rule. Every gate is a real binding, and every resolved_by is the depended-on target tool.
- **prerequisite_sentences:**
  - Edges 1, 2, 4 and 5: sentences unchanged; round-1 derivations stand.
  - Edge 3: "with its suspension date". Passes; one writer (the suspension write).
  - Edge 6: state form, as in the table above.
  - No rule names a tool or another problem's id. No cross-problem order is stated without a declared edge.
- **override_declarations:**
  - Same declarations as round 1; no new `overwrite` entries were needed for the changed tiers. Each change is inside a sentence already declared superseded (the contents fee clause) or refines an extended-only factor.
  - Only O-10 (below) touches a base sentence.
- **factor_ladders:**
  - Contents: 6 factors (1 honest method, 5 parameter).
  - Restart: 5 factors (1 method, 4 parameter; all 4 parameter factors now tagged coverage).
  - Equipment: 6 factors (1 method, 5 parameter), with every ladder disjoint.
  - Other policies are unchanged from round 1.
  - Every ladder has at least 3 pairwise-disjoint tiers as stated, distinct values or methods, a fall-through equal to the baseline, and every tier in both the rule and compute.

### findings (revision_2)

- F-2: **closed.**
- F-3 (a, b, c): **closed.**
- No new SOURCE-POLICY or SOURCE-FACTOR finding at charter level.
- **O-10 (new observation).** The setup rule's eligibility-response sentence re-states which check satisfies base `oxygen_eligibility_current` ("the coverage's last eligibility check is within … eligibility_reverify_days before the setup date"; evidence field `coverage_holdings.last_eligibility_check_date`), without an `overwrite` entry naming that base sentence.
  - Under the reading adopted in round 1 (last check as of the setup), it changes nothing.
  - Under a literal evidence-field reading it would be an undeclared narrowing of a base gate. No second scored value follows.

### closing_checklist (revision_2)

- Written after both revision_2 reveals (20:27Z).
- **Audit files:** `0.md` and `1.md`, each with revision_2 appended. Round-1 text is untouched.
- **Coverage and scope:**
  - charter_scope: task 0 = {setup, equipment payment, suspension, restart}; task 1 = {contents, new primary, return}.
  - They are pairwise disjoint and cover all 7 extended policies and all 7 task tools.
  - uuid8s are unchanged and independent.
- **Problem trees:**
  - Task 0: 3 prerequisite problems, 4 value_input edges, user root.
  - Task 1: 2 prerequisite problems, 2 value_input edges, 2 user writes.
  - All edges are now state form. The difficulty graph is acyclic.
- **Factors:**
  - Every computation has 4–6 factors with at least 2 parameter and at least 1 honest method.
  - Every ladder has at least 3 tiers, disjoint as stated and distinct in outcome.
  - Every factor bears weight on its task's world.
  - Whole-baseline fall-backs differ from gold:
    - task 0: 2026-06-20 / 211.09 / 2026-10-28 / 2026-10-28;
    - task 1: 83.08 / 2026-06-01 / 2026-10-21.
  - Multi-source and cross-difficulty factors are present per task (coverage, pap, beds), with seeded rows.
  - No stamp names a gold value.
- **Unique solution:** both tasks' GT matches the blind round-2 derivation argument for argument.
- **Gates:** the coordinator's post-rework snapshot is green except pre-render traceability (deferred by design). This audit did not re-run them.

**Difficulty result (revision_2): passes the source-layer audit.**

| Task | Policy | Chain | Factor | Task |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Open observations: O-2, O-7, O-9, O-10, and the task-1 history-narrative note.

---

## revision_3

### entry (revision_3)

- Gates: `bash /tmp/erl0057_coord/gates.sh home_oxygen_service`, run by this auditor at 2026-10-13 ~04:55Z. All 8 lines are OK or INFO:
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK
  - SOLVABILITY OK
  - COMPUTE OK
  - GROUNDING OK
  - CACHE-DIFF INFO
  - SCOPE OK
- Views rebuilt with `make_views.py`. Printed hashes:
  - 0.view.json bf5fca41ecbfa6364e4376043088c6a1d08a9030609baf645ad505a565912525 (unchanged)
  - 1.view.json a3e1261b18849ff84f09cce89d54f4aba766f6d3e2ec2c89d6e6900177520b2e (unchanged)
  - oxygen.extended.yaml 5c483891d76813562a7395881134d424943e63d2ea8b0be6307a233774e182dc (**changed**)
  - task_tools.py 5f5da85d…4adc5 (unchanged)
- Blueprint unchanged; the base copy is still verbatim.
- The charter changed, so every charter-global section is re-derived. The tool module is unchanged, so § action_binding_and_uuids is carried forward.
- Inputs also read: `audits/render_source/home_oxygen_service/render_r1_source_mismatches.md` (render-found items R1–R7 plus two minor items).
- contamination_disclosure: round-1 and round-2 GT were read in earlier rounds. Round-3 values below are mechanical recomputations on the round-3 charter; no `tasks/*.json` was opened in this round before the per-task freezes below.

### charter_global_frozen (revision_3) — written before any round-3 reveal

**Render-found items:**

| Item | Round-3 evidence | Status |
| --- | --- | --- |
| R1 equipment overwrite wider than its replacement | Both `overwrite` entries on oxygen_evt_monthly_billing now carry a scoped replacement, quoted verbatim in the rule: "For an equipment month this policy governs, and only for such a month, the month's fee is worked out by the flow combination and the percentage steps below in place of the stationary fee and its flow adjustment; every other equipment month remains under the base monthly billing rule for its fee." The allowed-amount entry has the same shape. Paid-in-full months go to extended; all other months go to the base fee and allowed-amount sentences. Exactly one rule each. | **closed** |
| R2 contents overwrite scope | "For a contents month this policy governs, and only for such a month, … every other contents month remains under the base contents billing rule." Exactly one rule per month. | **closed** |
| R3 baseline depends on a factor binding | baseline.rule is now "The standard month's fee is the class's `stationary_monthly_fee`. The standard allowed amount is the month's fee times the coverage class's allowed_pct_of_fee_schedule divided by 100, rounded once…". params is [stationary_monthly_fee]. The portable-billable definition moved inside the flow-combination sentence. The baseline is self-sufficient: 172.61 × 105% = 181.24 on task 0. | **closed** |
| R4 factor computing with another factor's output | flow_fee_combination now uses the class's `high_flow_uplift_pct` directly (`P('high_flow_uplift_pct')`). The payer rate is a separate multiplier step, payer_high_flow_rate (`payer_flow_pct`: 93 / 87 / 100), conditioned on flow above threshold and coverage class. No binding of one factor appears in another factor's tier or method. | **closed** |
| R5 established-rental tier on another factor's output | Rule and ladder now state the condition on records: "when the oxygen record is an active rental and the patient's PAP device record is suspended with a suspension date later than the oxygen setup date … otherwise, when the oxygen record is an active rental and the patient's hospital bed record is suspended … otherwise the oxygen record's own payment period…". Compute adds the `F('status') == 'rental_active'` check and measures to each record's own suspension date. | **closed** |
| R6 zero-refill average | The rule adds "when at least one cylinder refill is on record and…" to both tiers, and "by 100 percent otherwise, including when no cylinder refill is on record". Compute adds `sized_refills > 0` guards. | **closed** |
| R7 no coverage-inactive denial | The rule adds, for window and for lag, "when the earlier coverage has no coverage-inactive denial on the oxygen claim history, the denial window is met" and "the denial lag is met". Compute defaults: window `or NOW` → 0, lag `or new_effective_day` → 0. Both met. | **closed** |
| minor: suspension overwrite takes the trigger | The superseded clause is now only "with the admission date as suspended_date", scoped "For a stay this policy governs … every other stay remains under the base rule". The base trigger stays in force. | **closed** |
| minor: span coverage filter | Rule: "the most recent equipment month paid under the coverage named on the oxygen record". This matches the compute filter. | **closed** |

**My revision_2 observations:**

| Observation | Round-3 evidence | Status |
| --- | --- | --- |
| O-10 eligibility gloss without overwrite | A new `overwrite` on oxygen_qualification supersedes "Oxygen is set up only when the coverage's last eligibility check is within that coverage class's eligibility_reverify_days before the setup date." (verbatim in base). Its scoped replacement is quoted in the setup rule. | **closed** |
| O-2 / O-7 | Unchanged (traceability pre-render; docstrings). | unchanged |
| O-9 realism | New items: setup training allowance now `contracted_predelivery_days` 2 (Medicare, MA and commercial classes) vs `other_predelivery_days` 1 (other classes), 0 for non-facility orders; payer high-flow 93% / 87% of the month. Plausible contract terms. | kept |

**Re-derived sections:**
- **Overwrite scopes (every base clause governed by exactly one rule).** I script-checked that every `superseded_clause` is verbatim in its base policy's rule and every `replaced_by` is verbatim in the extended rule. All 8 overwrite entries pass. Each replaced_by names "this policy governs … and only for such …; every other … remains under the base rule", so no base clause is left ungoverned.
  - Base sentences *not* superseded that touch governed months:
    - Equipment: "The portable add-on … is added when portable equipment is furnished and billable" and the QG/QF/QE modifier text. The extended flow combination adds the add-on in the same cases and takes the higher of uplift vs add-on exactly as base does, so they are consistent.
    - Contents: the anniversary/min-deliveries/concentrator-class sentences are untouched by the replacement.
  - No base clause is left with two rules or none.
- **rule_compute_equivalence.** Script check: every compute_basis sentence and every baseline.rule sentence is verbatim in its rule; compute_basis keys equal binding names; every factor binding exists in compute; no binding is shared between factors. Re-read of the changed bindings:
  - month_equipment_fee (5 tiers, the last split by portable billable);
  - payer_flow_pct;
  - the result order (flow → usage → payer → position → training → multi → plan);
  - contents order (flow on the unscaled fee → usage → …);
  - sized_refills;
  - denial lag/window defaults;
  - evidence_rental_months / established_months;
  - predelivery_days (facility referral × coverage class).
  All match their sentences.
- **prerequisite_graph / prerequisite_sentences.** The same 6 state-form edges and sentences as revision_2, verbatim, not restated in the depended-on rules, gates real, resolved_by correct, acyclic.
- **factor_ladders.**
  - Factor counts: setup 4 (1 method, 3 parameter; xd coverage ×2); suspension 4; equipment 6 (1 method, 5 parameter); restart 5; contents 6; new primary 5; return 4.
  - Every ladder has at least 3 tiers, disjoint as stated (the training allowance is now: facility + listed coverages / facility + other coverage / non-facility), with distinct values and the fall-through equal to the baseline.
  - flow_fee_combination's five tiers are distinct algorithms (MAX, raise, reduce plus add-on, plus add-on, identity).
- **findings (revision_3):** every render item and O-10 is closed. No new SOURCE-POLICY or SOURCE-FACTOR finding.

### closing_checklist (revision_3)

- Written after both revision_3 reveals (04:58Z).
- **Audit files:** `0.md` and `1.md`, each with revision_3 appended. Earlier revisions are untouched.
- **Scope:** charter_scope is unchanged: task 0 {setup, equipment payment, suspension, restart}, task 1 {contents, new primary, return}. Disjoint and complete over 7 policies and 7 tools. uuid8s unchanged.
- **Overwrite scopes:** all 8 overwrite entries are scoped "this policy governs … only … every other … remains under the base rule". Every base month and clause is governed by exactly one rule.
- **Problem trees:** unchanged (3 prerequisite problems with 4 value_input edges; 2 prerequisite problems with 2 value_input edges). All edges are state form, every tree has a user write, and the graph is acyclic.
- **Factors:**
  - Every computation has 4–6 factors with at least 2 parameter and 1 honest method, ladders disjoint as stated, and fall-through = baseline.
  - Every factor bears weight.
  - Whole-baseline fall-backs differ from gold:
    - task 0: 2026-06-20 / 181.24 / 2026-10-28 / 2026-10-28;
    - task 1: 83.08 / 2026-06-01 / 2026-10-21.
  - Multi-source and cross-difficulty factors are present and seeded. No stamp.
- **Unique solution:** GT matches the blind round-3 derivation for both tasks.
- **Gates:** green at the start of this round (run by this auditor through the coordinator script).

**Difficulty result (revision_3): passes the source-layer audit. No regression from revision_2.**

| Task | Policy | Chain | Factor | Task |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Open observations: O-2, O-7, O-9, the task-1 history-narrative note, and the task-1 change-log figure slip.
