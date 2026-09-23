# Policy-task audit — host_protection_and_claims_desk / charter-global

## charter_global_frozen

- Scenario: `env/env_0015_car_sharing_marketplace`, difficulty `host_protection_and_claims_desk`, category `hostplan`, M=2.
- Freeze inputs and hashes (sha256, first 16 hex):
  - `env/env_0015_car_sharing_marketplace/tasks/host_protection_and_claims_desk/hostplan.extended.yaml` — `700ae25adc6614b1`
  - `env/env_0015_car_sharing_marketplace/tasks/host_protection_and_claims_desk/task_tools.py` — `8333387e135f28bf`
  - masked task views: `0.json` — `d960903c2c7abf47`; `1.json` — `a80706b4702ce12e`
- Freeze time: 2026-09-22 (audit session clock). Auditor: independent policy-task auditor (not the instantiating agent).
- Fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/hostplan.yaml`, the whole of `hostplan.extended.yaml`, the whole of `task_tools.py`, and from each task file only `frozen_time`, `user_scenario`, `initial_state`.
- Fields explicitly masked and unread when this section was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state` — removed from the masked views by the coordinator; and the sibling difficulty's audit under `audits/policy_task/guest_protection_desk/`, which was not opened.
- Entry conditions supplied with the brief and cited, not re-run: `check_extended.py`, `check_task_tools.py`, `replay_tasks.py --check`, `check_solvability.py`, `check_compute.py`, `check_grounding.py`, `check_cross_fire.py` all green on this difficulty (gate snapshot in the commissioning brief). `check_traceability.py` correctly not run at this stage. Input is complete; no "incomplete input" finding.

### policy_conflict_scan

The structured policy in force for this category is the verbatim base section of `hostplan.yaml` (13 base policies) plus 8 `extended_policies`. The base copy carried in `hostplan.extended.yaml` lines 1–897 is byte-identical to `blueprint/products/hostplan.yaml` (`diff` reports only a trailing blank line at line 898); the base section has not been rewritten.

Overlapping-subject scan, base × extended:

| Extended policy | subject | target_tool | computes | base_policy_refs | overwrite |
| --- | --- | --- | --- | --- | --- |
| hostplan_ext_damage_report_evidence | hostplan_claim_filed | lodge_damage_report_2cc23be4 | document_count | hostplan_evt_claim_intake | `[]` |
| hostplan_ext_claim_opening | hostplan_claim_filed | open_loss_claim_e6dccf7d | claim_opened_amount | hostplan_evt_claim_intake | `[]` |
| hostplan_ext_loss_appraisal | hostplan_claim_appraised | record_loss_appraisal_09001cb5 | accepted_loss_amount | hostplan_evt_appraisal, hostplan_evt_earnings_share | 1 declared |
| hostplan_ext_host_share | hostplan_deductible_charged | raise_host_share_c19fa66d | host_share_amount | hostplan_evt_deductible | `[]` |
| hostplan_ext_cover_restoration | hostplan_enrollment_reinstated | restore_protection_cover_3adbf459 | restoration_charge_amount | hostplan_lifecycle_standing | 1 declared |
| hostplan_ext_repair_supplement | hostplan_supplement_added | record_repair_supplement_1a6beabe | supplement_amount | hostplan_evt_appraisal | `[]` |
| hostplan_ext_claim_withdrawal | hostplan_claim_withdrawn | withdraw_own_claim_4cdcc89b | released_amount | hostplan_evt_claim_closure | `[]` |
| hostplan_ext_reimbursement_release | hostplan_reimbursement_paid | release_claim_payment_a6ef5b4d | released_payment_amount | hostplan_evt_reimbursement | `[]` |

Two extended policies share the subject `hostplan_claim_filed` (`..._damage_report_evidence` writes the damage-report register through `hostplan_claim_intake`; `..._claim_opening` writes the claim row). They compute different quantities on different tables through different tools and do not overlap. Every other subject is claimed by exactly one extended policy. Eligibility, time anchors, objects and terminal states of base and extended agree except where recorded in `override_declarations` below.

Cross-category read boundaries declared per policy in `cross_category` / `inputs.cross_category`: service, listings, payouts, roadside — all four are other difficulties of this scenario, all read-only, and no task tool writes outside `hostplan_enrollments`, `hostplan_claims`, `hostplan_claim_intake` (verified by reading every function body in `task_tools.py`: the only mutating calls are `ctx.create` on those three tables and `ctx.update` on `hostplan_enrollments`).

Claimed-scope partition (derived from the `prerequisite` graph, before any `charter_scope` field was read): the graph decomposes into exactly two weakly connected components of four policies each —
- Component A: `hostplan_ext_damage_report_evidence` → `hostplan_ext_claim_opening` → `hostplan_ext_loss_appraisal` → `hostplan_ext_host_share`;
- Component B: `hostplan_ext_cover_restoration` → `hostplan_ext_repair_supplement` → `hostplan_ext_reimbursement_release`, and `hostplan_ext_claim_withdrawal` → `hostplan_ext_reimbursement_release`.

With M=2 the two components are the only possible pairwise-disjoint, jointly complete scope partition, and each is a whole problem tree (root plus three prerequisite problems). Confirmed against the revealed `charter_scope` in `closing_checklist`.

### rule_compute_equivalence

Check 2 was run mechanically and then by hand over all 8 extended policies. Mechanically: every binding of every `compute` has an entry in `compute_basis`, and every `compute_basis` key is a binding (no orphans either way). Every `compute_basis` value is a verbatim sentence of that policy's own `rule` (whitespace-normalised substring match, 0 failures). Every `baseline.rule` sentence is a verbatim sentence of the `rule` (0 failures). Every factor ladder tier's condition and outcome is stated in the `rule`; 14 tier strings are not byte-identical substrings, and each was checked by hand and found to be the same clause with a demonstrative or an article changed (e.g. `loss_kind_ceiling` tier "the report on the register names glass" against the rule's "the plan's glass ceiling where the report names glass"). None is a tier that lives only in `compute`, and no branch of any `decides` binding lacks a tier in the rule.

What the hand sweep does find is the opposite direction — `compute` inventing a basis the `rule` does not state. Four instances, all of them a window or a scope that appears in the expression and nowhere in the prose it quotes:

1. `hostplan_ext_claim_withdrawal.compute[appraisals_in_window] = COUNT('hostplan_claims', within_months=2, date_field='claim_date', event_type='hostplan_claim_appraised')`, whose `compute_basis` is the rule sentence "Where two or more appraisals stand on the enrolment inside **the plan's supplement window** ...". The plan's supplement window is a per-plan figure (14/21/30/45/60/90 calendar days; the policy even computes it as `plan_supplement_window`, then uses it only for `late_share`). Two months is neither.
2. `hostplan_ext_repair_supplement.compute[partner_visits_counted] = XCOUNT('service','service_visits', within_months=3, ...)`, whose basis is "Where two or more of **the workshop visits counted** were carried out in the partner network ...". "The visits counted" is the set the `work_counted_window` factor selects, which on its first two tiers is the six-month set or the whole-life set, not the three-month set.
3. `hostplan_ext_loss_appraisal.compute[reports_on_register] = COUNT('hostplan_claim_intake', within_months=1, date_field='reported_at')`, whose basis is "Where **a report for the loss stands on the register** and the vehicle's listing is not live ..." — a standing-report test with no window at all.
4. `hostplan_ext_claim_opening.compute[towed_miles] = XMAX('roadside','roadside_callouts','tow_miles')` and `hostplan_ext_loss_appraisal.compute[towed_distance] = XMAX('roadside','roadside_callouts','tow_miles')`, both unwindowed, whose basis is "Where a callout attended the vehicle **in the month before** ... and the vehicle was towed"; likewise `recovery_day = XLATEST('roadside','roadside_callouts','callout_date', ...)`, unwindowed, for "the day the vehicle was recovered" on a callout in that month.

Each is recorded in `findings` as CG-7 … CG-10 with the situation in which prose and expression reach different conclusions.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no tool is shared and no quantity is computed twice. Every policy's subject, base refs, tool docstring and terminal state admit one business reading, and no docstring adds a confirmation, review or wait.

The eight uuid8 tails are `2cc23be4`, `e6dccf7d`, `09001cb5`, `c19fa66d`, `3adbf459`, `1a6beabe`, `4cdcc89b`, `a6ef5b4d`. All eight are distinct, share no prefix, are not a sequence, are not near-neighbours of one another and are not derivable from the verb or object of their tool. Nothing suggests batch derivation.

Docstring sequence scan (`before|after|first|prior to|once|until|then`): one hit, `record_repair_supplement_1a6beabe` — "Add further repair cost found **after an appraisal** to a claim that has already been accepted." This names the kind of cost, not this tool's position in a sequence, and names no other tool; recorded as observation CG-19 rather than a red light.

### prerequisite_graph

Six declared edges across the 8 policies; three policies carry `prerequisite: []` (`..._damage_report_evidence`, `..._cover_restoration`, `..._claim_withdrawal`), which is the filled-in empty form, not an omission.

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| claim_opening | damage_report_evidence | value_input | reported_damage_kind | state | lodge_damage_report_2cc23be4 |
| loss_appraisal | claim_opening | value_input | opened_amount | state | open_loss_claim_e6dccf7d |
| host_share | loss_appraisal | value_input | accepted_standing | state | record_loss_appraisal_09001cb5 |
| repair_supplement | cover_restoration | state_gate | hostplan_enrollments.status | state | restore_protection_cover_3adbf459 |
| reimbursement_release | repair_supplement | value_input | owed_standing | state | record_repair_supplement_1a6beabe |
| reimbursement_release | claim_withdrawal | value_input | owed_standing | state | withdraw_own_claim_4cdcc89b |

Every `problem` names another extended policy id in this file; none names a base policy and none names itself. The graph is acyclic (components A and B above; A is a path of 4, B is a diamond-free tree of 4). `form` is `state` on all six edges and no `fallback_reason` appears anywhere, which is correct: the state form has priority and no action-form edge is declared, so there is no fallback to test.

`kind` matches `gate` on all six: the five `value_input` gates (`reported_damage_kind`, `opened_amount`, `accepted_standing`, `owed_standing` ×2) are each a binding name that genuinely exists in the blocked policy's `compute`; the one `state_gate` names `hostplan_enrollments.status`, an eligibility state the blocked policy's own rule turns on. `resolved_by` is in each case the depended-on policy's `target_tool`.

Whether `resolved_by` genuinely makes `effect` hold: five of the six do, verified against the tool bodies (`lodge_damage_report_2cc23be4` creates the `hostplan_claim_intake` row the `reported_damage_kind` LATEST reads; `open_loss_claim_e6dccf7d` creates the `hostplan_claim_filed` row the `opened_amount` MAX reads; `record_loss_appraisal_09001cb5` creates the `hostplan_claim_appraised` row the `accepted_standing` MAX reads and raises `reimbursement_balance_due`; `restore_protection_cover_3adbf459` sets `status='active'` and `suspension_reason='none'`; `record_repair_supplement_1a6beabe` raises `reimbursement_balance_due` by the supplement). The sixth does **not** — see finding CG-6.

No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test on each `policy_source`, all six verbatim-locatable in the blocked policy's own `rule`:

1. claim_opening: "A claim is opened on a loss only after a damage report for that trip stands on the register carrying the number of photographs and documents the plan asks of it." — connective "only after"; waited-on thing is a record-visible state of the damage-report register in the words the register uses; no tool, policy id, snake_case token or row id; scope matches `condition`. Exactly one write of this difficulty puts a row on `hostplan_claim_intake` (`lodge_damage_report_2cc23be4`), so the hop resolves uniquely. Derivation: the sentence says a report must stand carrying the plan's number of documents → `hostplan_claim_intake` is the register the finder `find_hostplan_claim_intake` reads → the only policy whose own rule describes putting a report on that register carrying a settled number of documents is `hostplan_ext_damage_report_evidence` ("the host lodges that many with the report") → its `target_tool`. One reading.
2. loss_appraisal: "The amount the plan accepts on a loss is not settled before a claim for that loss stands opened on the enrolment at a stated amount." — connective "not ... before"; state form; one write opens a claim at a stated amount. One reading.
3. host_share: "The host's share of a loss is fixed only after the money the plan accepts on that claim stands booked as owed to the host." — connective "only after"; state form. Two writes of this difficulty raise `reimbursement_balance_due` (`record_loss_appraisal_09001cb5` and `record_repair_supplement_1a6beabe`); the qualifier "the money the plan accepts on that claim" singles out the appraisal, because the supplement policy's own rule calls its amount "further cost found after a loss has been appraised" and never "the money the plan accepts". The hop resolves, but on a qualifier rather than on the state name — recorded as observation CG-17.
4. repair_supplement: "Further cost is not added to a claim before the cover the loss was settled under stands in force again." — connective "not ... before"; state form ("stands in force again" for `status`); one write restores a fallen-away enrolment. One reading.
5. reimbursement_release ← repair_supplement: "The money released on a claim is not fixed until every further cost accepted on that claim stands booked as owed to the host." — connective "until"; state form; one write. One reading.
6. reimbursement_release ← claim_withdrawal: "Money is released on a loss only once no money stands booked on a second claim for the same loss." — connective "only once"; state form. Two writes of this difficulty reduce the money booked on a claim (`withdraw_own_claim_4cdcc89b` and `release_claim_payment_a6ef5b4d`); the second reading is self-blocking (paying the second claim is itself "releasing money on a loss" and is gated by the same sentence), so the hop resolves to the withdrawal. Recorded as observation CG-18. The material defect on this edge is not the hop but that the resolving write does not make the stated condition true — finding CG-6.

No rule carries a second wording of any dependency, no other problem's tool name or id, and no depended-on policy's rule restates the blocked policy's prerequisite sentence. No rule states a cross-problem order that grounds no declared edge. No base rule sentence is being used to ground an edge.

### override_declarations

Sentence-by-sentence sweep of each extended policy against every entry of its `base_policy_refs`. Two `overwrite` entries are declared and both are well-formed (they name the base sentence and give the replacement, and the merged semantics are unique):

- `hostplan_ext_loss_appraisal` supersedes `hostplan_evt_appraisal`'s "The accepted amount is capped twice over, first by the sublimit for the kind of loss and then by the plan's overall physical damage limit, and the lower of the two governs" with a single cap, the kind ceiling having moved to claim opening. Declared, coherent.
- `hostplan_ext_cover_restoration` supersedes `hostplan_lifecycle_standing`'s "A lapsed enrolment may be reinstated inside the plan's reinstatement window on payment of the plan's reinstatement fee" with a charge the host carries. The quoted clause carries the window, so removing the window limit is inside what was declared. Declared, coherent.

Undeclared conflicts found, each a base sentence and an extended sentence that decide the same scored quantity differently with `overwrite: []`:

- **CG-1** `hostplan_ext_host_share` vs `hostplan_evt_deductible` (two sentences and the base formula). Bears on task 0.
- **CG-11** `hostplan_ext_damage_report_evidence` vs `hostplan_evt_claim_intake`'s evidence floor. Bears on no task's scored value; charter-global only.

Base provisions not hit by any `overwrite` and correctly inherited: the filing window and `trip_actually_completed` gate of `hostplan_evt_claim_intake`; the supplement window of `hostplan_evt_appraisal`; `enrollment_still_settles` of `hostplan_evt_deductible`; `reimbursement_not_already_paid` and `payout_account_not_on_hold` of `hostplan_evt_reimbursement`; the appeal window of `hostplan_evt_claim_closure`; the portfolio standing rules. Two inherited base branches that extended never produces are recorded as observations CG-20 (total-loss threshold) and CG-21 (photo-estimate threshold); CG-21 has a task-0 consequence, demonstrated there.

### factor_ladders

| policy | factors | parameter | method | multi-source tiers | cross_difficulty categories |
| --- | --- | --- | --- | --- | --- |
| damage_report_evidence | 4 | 3 | 1 | workshop_record_share, reporting_record, inspection_currency | service, listings |
| claim_opening | 6 | 5 | 1 | reporting_record_window, prior_condition_share, open_exposure_share, recovery_admitted | listings, payouts, roadside |
| loss_appraisal | 6 | 4 | 2 | repair_network_rate, off_road_anchor_day, off_road_endpoints, loss_of_use_daily_sum, valuation_fee_share | service, listings, roadside |
| host_share | 4 | 3 | 1 | claim_free_standing | service, listings |
| cover_restoration | 6 | 5 | 1 | uncovered_period_measure, vehicle_verification_rate, care_standing_rate, settlement_risk_loading | listings, service, payouts |
| repair_supplement | 6 | 5 | 1 | work_counted_window, network_repair_rate, settling_fault_share, late_notice_share, reserved_settlement_share, driven_since_share | service, payouts, listings |
| claim_withdrawal | 5 | 4 | 1 | release_measurement_basis, enrolment_standing_share, late_withdrawal_share, reporting_record_share | payouts |
| reimbursement_release | 6 | 5 | 1 | payment_measure, exposure_release_share, repair_state_share, tax_withholding_rate, arrears_set_off | payouts, service |

Every policy declares 4–6 factors with at least 2 `parameter` and at least 1 `method`; every ladder has exactly three tiers except `loss_kind_ceiling` (four); every ladder's tiers are pairwise disjoint as stated and as implemented, and each `decides` binding is an input to `result`, never `result` itself. Within each policy the factors' `bindings` sets are disjoint. Each label is honest: every `method` tier changes the algorithm that produces the quantity (which window the work is counted over, which day the off-road clock is anchored to, which end days are counted, how the share is measured, what the payment is measured from, how the period without cover is priced) and every `parameter` tier substitutes a number into a fixed formula.

No two tiers of any one ladder select the same value or method — checked figure by figure against `params` for all 43 factors.

Structural defects found in this section (weight-on-a-world is deferred to the task files):

- **CG-2** `claim_opening / loss_kind_ceiling`: the factor's declared `baseline` is `kind_ceiling: ceiling_body`, but this policy's `baseline.rule` carries the whole four-way selection verbatim ("the plan's glass ceiling where the report names glass, the plan's tyre and wheel ceiling where it names tyres and wheels, the plan's interior ceiling where it names the interior, and the plan's body and paint ceiling for every other kind of loss"). The declared baseline is therefore not what `baseline.rule` states for this input except when the report names a body loss. Bears on task 0.
- **CG-3** `loss_appraisal / loss_of_use_daily_sum`: the factor's declared `baseline` is `RND(plan_lou_daily * K('recent_claim_lou_share'), 2)`, i.e. half the plan's daily sum, while `baseline.rule` says "Loss of use is paid at **the plan's daily sum** for the days the vehicle stands off the road". The ladder's fall-through tier ("the plan's daily sum at the marketplace's recent-claim share") is therefore not the baseline, and the declared baseline is a figure the baseline document never states. Bears on task 0.
- **CG-4** `repair_supplement / reserved_settlement_share`: the factor's declared `baseline` is `K('stopped_account_share')` = 0.88, while this policy's `baseline.rule` never mentions the reserves or the state of the payout account at all — it enumerates exactly what is not taken off ("with nothing taken off for how the loss was settled, how late the cost is brought or how far the vehicle has been driven since"), and the reserves are not on that list. Bears on task 1.
- **CG-5** `claim_withdrawal / reserved_release_share`: the factor's declared `baseline` is `K('unreserved_release_share')` = 0.8, while `baseline.rule` says the money is "released **in full** with nothing retained for the standing of the enrolment, for how late the withdrawal comes or for the state of the reporting record" — again an enumeration that omits the reserves. Bears on task 1.
- **CG-14** `repair_supplement / work_counted_window`, tier 2: "the work counted is everything the workshop has ever invoiced on the vehicle", selected when the vehicle carries an active care plan and **fewer** than two workshop visits stand in the three months before. Charter-global; neither task takes this tier.
- **CG-15** `claim_withdrawal / release_measurement_basis`, tier 2: "the release is measured as the money the latest appraisal standing booked", selected when "no money stands booked as owed". Charter-global; neither task takes this tier.
- **CG-13** `loss_appraisal`'s `baseline.rule` sentence on the valuation fee is not self-deciding; observation.
- **CG-16** `cover_restoration` binds the same aggregate twice under two names; observation.

## findings

### CG-1 — SOURCE-POLICY RED — undeclared override of the deductible quantity

- **Symptom.** Base and extended both fix the scored quantity `hostplan_deductible_charged.amount_delta`, and they fix it at different numbers, with `hostplan_ext_host_share.overwrite == []`.
- **Root cause.** The extended policy replaces base's determination of the host's share (a plan constant, discounted for a claim-free record) with a four-stage measurement-and-loading chain, and additionally strengthens base's claim-free discount with a condition base does not carry, without naming a single base sentence in `overwrite`.
- **Evidence.**
  - Base `hostplan_evt_deductible.rule`, sentence 1 (`blueprint/products/hostplan.yaml:764`): "Every accepted loss carries the host's own share, and that share is **the deductible of the plan** in force on the day of the loss rather than the plan in force on the day the claim is settled."
  - Base `hostplan_evt_deductible.rule`, sentence 3: "A host who has gone the plan's qualifying period without an accepted claim has the deductible reduced by the plan's claim-free discount, and a host who reaches the plan's waiver period has it waived entirely on the next accepted claim."
  - Base `hostplan_evt_deductible.formula`: `when: liability_finding != "no_fault"`, `amount_delta: round(host_deductible_amount * (1 - claim_free_discount_percent / 100), 2)`.
  - Extended `hostplan_ext_host_share.rule`: "Where the money the plan accepted on the claim is below the marketplace's small-loss mark, the share is measured as the marketplace's small-loss proportion of the money accepted ..." and "the care rate is applied to the figure that step leaves, the value loading is applied last".
  - Extended `hostplan_ext_host_share.compute[claim_free_rate]` requires `liability_standing <= 0` in both the waiver and the discount branch; base's sentence 3 attaches no such condition.
  - `hostplan_ext_host_share.overwrite: []`.
- **Demonstrated consequence.** Demonstrated against task 0's world in `0.md` § findings: base yields 1275.00 and extended yields 982.43 for the same write, and the world contains a seeded precedent at exactly base's figure.
- **Affected artifact.** `tasks/host_protection_and_claims_desk/hostplan.extended.yaml`, policy `hostplan_ext_host_share` (`overwrite`, `rule`, `compute`), against `blueprint/products/hostplan.yaml` policy `hostplan_evt_deductible`. Bears on task 0.
- **Relation to previous revisions.** First revision.

### CG-6 — SOURCE-POLICY RED — the withdrawal rule and the release rule contradict each other on the same state

- **Symptom.** `hostplan_ext_reimbursement_release` may not be written until no money stands booked on a second claim for the same loss; `hostplan_ext_claim_withdrawal` guarantees that money stays booked on the withdrawn claim. The gate the release names can therefore never be reached by the write the `prerequisite` declares resolves it.
- **Root cause.** The withdrawal policy releases a *share* of what the second claim booked and states in its own rule that the remainder stays booked, while the release policy's prerequisite sentence is written as an absolute ("no money stands booked").
- **Evidence.** Two verbatim passages of the same file:
  - `hostplan_ext_reimbursement_release.rule`: "Money is released on a loss only once **no money stands booked** on a second claim for the same loss." — carried as `prerequisite[1].policy_source`, with `condition`: "No money stands booked as owed to the host on any second claim carrying the same loss date as the claim being paid" and `effect`: "The money the second claim had booked is released off the balance owed to the host".
  - `hostplan_ext_claim_withdrawal.rule`, final ordering sentence: "... **what is not released stays booked against the withdrawn claim** as the cost the marketplace has already committed to it."
  - `hostplan_ext_claim_withdrawal.compute[result]`: `RND(release_basis * reserve_release_share * standing_share * late_share * record_share, 2)` — a product of four shares each at most 1.0, three of which are strictly below 1.0 on three of their tiers, so the release is strictly less than `release_basis` whenever any tier below the fall-through is taken.
- **Demonstrated consequence.** Demonstrated against task 1's world in `1.md` § findings: after the declared resolving write, 174.62 USD is still booked on the second claim, so the release policy's own rule forbids the root write and the defensible answer becomes "refuse / do not release", against a scored solution that releases.
- **Affected artifact.** `hostplan.extended.yaml`, policies `hostplan_ext_reimbursement_release` (`rule`, `prerequisite[1].condition`, `prerequisite[1].effect`) and `hostplan_ext_claim_withdrawal` (`rule`, `compute[result]`). Bears on task 1.
- **Relation to previous revisions.** First revision.

### CG-7 — SOURCE-POLICY RED — `appraisals_in_window` implements a window the rule does not state

- **Symptom.** The rule scopes the appraisal count to "the plan's supplement window"; the expression scopes it to two calendar months for every plan.
- **Root cause.** `plan_supplement_window` is computed from the plan and then used only by `late_share`; the ladder that the rule ties to that window is implemented with a literal.
- **Evidence.** `hostplan_ext_claim_withdrawal.compute`: `appraisals_in_window: COUNT('hostplan_claims', within_months=2, date_field='claim_date', event_type='hostplan_claim_appraised')`. Its `compute_basis` quotes: "Where two or more appraisals stand on the enrolment **inside the plan's supplement window** and money stands booked as owed to the host, the release is measured as that money less the largest appraisal standing ...". `params`: `swin3_s90: 14 … swin3_s60: 90`.
- **Demonstrated consequence.** Same situation, two conclusions: a Keyturn Shield 90 enrolment (supplement window 14 days) with two appraisals recorded 50 days before the handling date. The rule places both outside the window → fewer than two appraisals stand in it → `release_basis` = the whole of the money standing booked. The expression places both inside two months → `release_basis` = that money less the largest appraisal standing. On any world where the largest appraisal is non-zero these are different figures, so the policy does not uniquely determine `released_amount`.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_claim_withdrawal.compute[appraisals_in_window]` and `compute_basis[appraisals_in_window]`.
- **Bears on.** Neither task's scored value moves (in task 1 the plan's 60-day window and two months both admit exactly the two July appraisals and exclude the May one), so neither task file carries a consequence for this finding.
- **Relation to previous revisions.** First revision.

### CG-8 — SOURCE-POLICY RED — `partner_visits_counted` counts a different set from "the visits counted"

- **Symptom.** The rule decides the repair rate from the partner-network share of *the visits the previous step counted*; the expression always counts partner visits in the three months before, whatever window the previous step chose.
- **Root cause.** The `work_counted_window` method factor moves the counting window to six months or to the whole life of the vehicle's workshop record, and the rate ladder is not moved with it.
- **Evidence.** `hostplan_ext_repair_supplement.compute`: `work_counted` is `XSUM(... within_months=6 ...)` / `XSUM(... no window ...)` / `XSUM(... within_months=3 ...)` by tier, while `partner_visits_counted: XCOUNT('service','service_visits', within_months=3, date_field='visit_date', vehicle_id=F('vehicle_id'), shop_channel='partner_network')`. `compute_basis[partner_visits_counted]`: "Where two or more of **the workshop visits counted** were carried out in the partner network, the cost is accepted at the full partner-network rate; where exactly one was carried out in the partner network, it is accepted at the marketplace's mixed-network rate; where none was, it is accepted at the marketplace's unmanaged-repair rate."
- **Demonstrated consequence.** Same situation, two conclusions: an active care plan with two partner-network visits four and five months before the handling date and no visit in the last three months. `work_counted` is on its first tier only if two visits stand in three months, so take instead the second tier (active plan, fewer than two visits in three months): the visits counted are then "everything the workshop has ever invoiced", which includes both partner visits → the rule gives the full partner-network rate 1.0; the expression counts partner visits in three months → 0 → the unmanaged-repair rate 0.86. A 14% difference on the same `supplement_amount`.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_repair_supplement.compute[partner_visits_counted]`.
- **Bears on.** Neither task's scored value moves (task 1 takes the first tier and both readings give two or more partner visits).
- **Relation to previous revisions.** First revision.

### CG-9 — SOURCE-POLICY RED — `reports_on_register` invents a one-month window

- **Symptom.** The rule tests whether a report for the loss *stands* on the register; the expression tests whether a report was lodged in the last month.
- **Evidence.** `hostplan_ext_loss_appraisal.compute`: `reports_on_register: COUNT('hostplan_claim_intake', within_months=1, date_field='reported_at')`; `compute_basis[reports_on_register]`: "Where **a report for the loss stands on the register** and the vehicle's listing is not live on the marketplace, the days run to the day of the appraisal with both end days counted; where a report stands on the register and the vehicle's listing is live, they run to that day with the first day not counted; where no report stands on the register, they run to that day with neither end day counted."
- **Demonstrated consequence.** Same situation, two conclusions: a report lodged on the register six weeks before the appraisal, on a listing that is not live. The rule: a report stands → both end days counted → `off_road_days_counted = DAYS(anchor, NOW) + 1`. The expression: no report in the last month → neither end day counted → `DAYS(anchor, NOW) - 1`. Two days of loss of use, i.e. two times the plan's daily sum, on the same `accepted_loss_amount`.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_loss_appraisal.compute[reports_on_register]`.
- **Bears on.** Neither task's scored value moves (in task 0 the report is lodged the same day).
- **Relation to previous revisions.** First revision.

### CG-10 — SOURCE-POLICY RED — the tow test and the recovery day are read over all callouts, not the month the rule names

- **Symptom.** Three expressions read the roadside history with no window while the prose they quote scopes the reading to "a callout [that] attended the vehicle in the month before".
- **Evidence.** `hostplan_ext_claim_opening.compute[towed_miles]: XMAX('roadside','roadside_callouts','tow_miles')`; `hostplan_ext_loss_appraisal.compute[towed_distance]: XMAX('roadside','roadside_callouts','tow_miles')` and `compute[recovery_day]: XLATEST('roadside','roadside_callouts','callout_date', date_field='callout_date')`. Their shared `compute_basis` sentence: "Where a callout attended the vehicle **in the month before** the report and the vehicle was towed, the whole of the recovery billed on the vehicle in that month is added; where a callout attended the vehicle in that month and the vehicle was not towed, half of the recovery billed in that month is added ..." (and the parallel sentence in `loss_appraisal`).
- **Demonstrated consequence.** Same situation, two conclusions: a tow with `tow_miles = 40` eight months before the handling date and a jump-start with `tow_miles = 0` last week. The rule: the callout in the month before is the jump-start, the vehicle was not towed → half of the recovery billed in that month, and in `loss_appraisal` the days are counted from the day the report was lodged. The expressions: `XMAX(tow_miles) = 40 > 0` → the whole of the recovery, and the off-road clock is anchored to `XLATEST(callout_date)` regardless. Two different `claim_opened_amount` figures and two different `accepted_loss_amount` figures.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_claim_opening.compute[towed_miles]`, `hostplan_ext_loss_appraisal.compute[towed_distance]`, `compute[recovery_day]`.
- **Bears on.** Neither task's scored value moves (task 0 has exactly one callout, a tow, inside the month; task 1 has none).
- **Relation to previous revisions.** First revision.

### CG-11 — SOURCE-POLICY RED — undeclared override of the evidence floor

- **Symptom.** Base fixes a floor on the evidence a report must carry before it becomes a claim; extended takes that same published minimum at a half or three-quarter share and declares a floor of one, with `overwrite: []`.
- **Evidence.**
  - Base `hostplan_evt_claim_intake.rule`: "The report must carry **at least the plan's minimum number of photographs** before it becomes a claim, and the host has the plan's evidence period to complete it"; `evidence_minimum_photo_count` per plan is 8/8/10/12/12/14.
  - Extended `hostplan_ext_damage_report_evidence.rule`: "The count starts from the evidence minimum the plan publishes ... The count is a whole number of documents and is **never below one** ... the evidence minimum is taken at half and rounded up to a whole document, the workshop's own record standing for the rest".
  - `hostplan_ext_damage_report_evidence.overwrite: []`.
- **Demonstrated consequence.** Same situation, two conclusions: a Keyturn Shield 80 enrolment (published minimum 10) whose vehicle carries an active care plan with two completed workshop visits in the six months before, whose marketplace valuation is under the high-value mark, with fewer than two reports on the enrolment in the twelve months before and a passed inspection inside the recency period. Extended: `evidence_required = 5`, all three additions zero → the report carries 5 documents. Base: the report does not become a claim below 10. The agent is told to hand the host a figure that base says is not enough to open a claim on.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_damage_report_evidence` (`overwrite`, `rule`, `compute[evidence_required]`), against `blueprint/products/hostplan.yaml` `hostplan_evt_claim_intake`.
- **Bears on.** Neither task's scored value moves (task 0's additions carry the count to 16, above the floor of 10).
- **Relation to previous revisions.** First revision.

### CG-2 — SOURCE-FACTOR RED — `loss_kind_ceiling`'s baseline is not what the baseline document states

See `factor_ladders` above for the two passages. Symptom: the factor declares `baseline: {kind_ceiling: ceiling_body}` while the policy's `baseline.rule` carries the whole four-way selection, so a reader of the computation document alone already picks the right ceiling and the factor document adds nothing. Root cause: the ladder that `baseline.rule` was supposed to be silent about has been copied into `baseline.rule`. Consequence demonstrated against task 0's world in `0.md` § factor_weight. Affected artifact: `hostplan_ext_claim_opening.baseline.rule` and `factors[loss_kind_ceiling].baseline`. Bears on task 0. First revision.

### CG-3 — SOURCE-FACTOR RED — `loss_of_use_daily_sum`'s baseline contradicts the baseline document

Symptom: `baseline.rule` says loss of use is paid at the plan's daily sum; the factor declares its baseline as half that sum, and the ladder's fall-through is the same half sum rather than the baseline. Root cause: the baseline sentence was written for the ladder's *first* tier while the declared baseline was taken from its *last*. Consequence demonstrated against task 0's world in `0.md` § factor_weight. Affected artifact: `hostplan_ext_loss_appraisal.baseline.rule`, `factors[loss_of_use_daily_sum].baseline`, `compute[loss_of_use_rate]`. Bears on task 0. First revision.

### CG-4 — SOURCE-FACTOR RED — `reserved_settlement_share` has no baseline in the baseline document

Symptom: the factor declares `baseline: {reserve_share: K('stopped_account_share')}` = 0.88, a figure `baseline.rule` never states; `baseline.rule` enumerates what is not taken off and the reserves are not on the list, so a reader of the computation document alone applies no reserve share at all. Root cause: one of the six factors was left out of the baseline sentence, and its declared baseline was taken from the ladder's fall-through instead. Consequence demonstrated against task 1's world in `1.md` § factor_weight. Affected artifact: `hostplan_ext_repair_supplement.baseline.rule`, `factors[reserved_settlement_share].baseline`. Bears on task 1. First revision.

### CG-5 — SOURCE-FACTOR RED — `reserved_release_share` has no baseline in the baseline document

Symptom and root cause as CG-4: declared `baseline: {reserve_release_share: K('unreserved_release_share')}` = 0.8 against a `baseline.rule` that says the money is "released in full" and enumerates three things nothing is retained for, the reserves not among them. Consequence demonstrated against task 1's world in `1.md` § factor_weight. Affected artifact: `hostplan_ext_claim_withdrawal.baseline.rule`, `factors[reserved_release_share].baseline`. Bears on task 1. First revision.

### CG-14 — SOURCE-FACTOR RED — `work_counted_window` tier 2 is not a measurement this line of business makes

- **Symptom.** A supplement to one appraised claim is measured, on one tier, from *everything the workshop has ever invoiced on the vehicle*.
- **Evidence.** `hostplan_ext_repair_supplement.rule`: "where the vehicle carries an active care plan and fewer than two workshop visits stand in that period, the work counted is **everything the workshop has ever invoiced on the vehicle**"; `compute[work_counted]` second branch: `XSUM('service','service_visits','invoice_amount', vehicle_id=F('vehicle_id'))` with no window.
- **Demonstrated consequence.** The tier's outcome is not what a protection marketplace gives a host in that situation: it books oil changes, tyre rotations and recall work invoiced years before the loss into the further cost of a single appraised body-damage claim, and it does so *because* the vehicle has been to the workshop less recently — the ladder pays more for less recent servicing, the reverse of the first tier's logic (an active plan with two or more recent visits buys only a six-month window). Judged against what this industry does, no supplement is measured from a vehicle's whole lifetime service ledger.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_repair_supplement.rule` and `factors[work_counted_window].ladder[1]`.
- **Bears on.** Neither task takes this tier.
- **Relation to previous revisions.** First revision.

### CG-15 — SOURCE-FACTOR RED — `release_measurement_basis` tier 2 releases money that is not owed

- **Symptom.** On one tier the withdrawal releases the amount the latest appraisal booked, in the very case where nothing stands booked as owed to the host.
- **Evidence.** `hostplan_ext_claim_withdrawal.rule`: "where two or more appraisals stand inside that window and **no money stands booked as owed**, the release is measured as the money the latest appraisal standing booked"; `compute[release_basis]` second branch: `latest_appraisal_booked`, which is a positive `amount_delta` of an appraisal row. The same policy's opening sentence says a withdrawal "releases the money **that claim had booked as owed to them**".
- **Demonstrated consequence.** The tier's outcome contradicts the policy's own opening sentence in exactly the situation it names: with `money_booked <= 0` there is nothing booked as owed, yet the tier produces a strictly positive release that the tool then subtracts from `reimbursement_balance_due`, driving the enrolment's balance owed to the host negative. No marketplace pays out, or books as released, money it does not owe.
- **Affected artifact.** `hostplan.extended.yaml`, `hostplan_ext_claim_withdrawal.rule` and `factors[release_measurement_basis].ladder[1]`.
- **Bears on.** Neither task takes this tier.
- **Relation to previous revisions.** First revision.

### CG-12 — observation — `last_visit_reading` is a maximum, not the last visit's reading

`hostplan_ext_repair_supplement.compute[last_visit_reading]: XMAX('service','service_visits','odometer_reading', vehicle_id=F('vehicle_id'))` against the rule's "the reading taken at **the last** workshop visit". The two agree whenever the odometer only rises, which is the ordinary case, so no situation in which they differ can be built from records a well-formed world would carry. Recorded, not red-lighted.

### CG-13 — observation — the valuation-fee sentence of `loss_appraisal`'s baseline does not decide itself

`hostplan_ext_loss_appraisal.baseline.rule` contains "Where the loss has to be valued away from the partner network the host carries a share of the marketplace's out-of-network valuation fee, and none of that fee is carried where it does not", and the baseline says nothing that decides whether this loss had to be valued away from the network. A reader of the computation document alone must supply the default themselves; the reading that nothing is carried (matching the declared `valuation_share: '0.0'`) is available and defensible, so this is not red-lighted, but the sentence is not self-deciding as `baseline.rule` is required to be.

### CG-16 — observation — one aggregate bound twice under two names in `cover_restoration`

`compute[accepted_claims_12m]` and `compute[claims_accepted_for_standing]` are the identical expression `COUNT('hostplan_claims', within_months=12, date_field='claim_date', event_type='hostplan_claim_appraised')`, bound respectively by `uncovered_period_measure` and `claim_frequency_loading`. The two factors' `bindings` lists are nominally disjoint and the check passes, but the two ladders rest on one and the same count.

### CG-17 — observation — "stands booked as owed to the host" is brought about by two writes

`hostplan_ext_host_share.prerequisite[0].policy_source` waits on "the money the plan accepts on that claim stands booked as owed to the host". Both `record_loss_appraisal_09001cb5` and `record_repair_supplement_1a6beabe` raise `hostplan_enrollments.reimbursement_balance_due`. The hop still resolves on the qualifier "the money the plan accepts on that claim", because the supplement policy's own rule calls its amount "further cost found after a loss has been appraised" and never "the money the plan accepts"; a state-form sentence that named the state more narrowly would not have needed the qualifier.

### CG-18 — observation — "no money stands booked on a second claim" could name two writes

`hostplan_ext_reimbursement_release.prerequisite[1]` waits on a state that both `withdraw_own_claim_4cdcc89b` and `release_claim_payment_a6ef5b4d` reduce. The second reading is self-blocking (paying the second claim is itself releasing money on that loss, gated by the same sentence), so a careful reader resolves the hop to the withdrawal. The material defect on this edge is CG-6.

### CG-19 — observation — one ordering word in a docstring

`record_repair_supplement_1a6beabe`: "Add further repair cost found **after an appraisal** to a claim that has already been accepted." This describes the kind of cost the record carries, names no other tool and states no position in a sequence, so it is not the docstring-ordering defect check 3 forbids; it is recorded because it is the only ordering word in the module.

### CG-20 — observation — base's total-loss branch is never produced by extended

`hostplan_evt_appraisal.rule`: "Where the appraised cost reaches the plan's total loss threshold as a percentage of the marketplace valuation of the vehicle, the claim is settled as a total loss at that valuation less the deductible rather than as a repair." `hostplan_ext_loss_appraisal` neither implements nor supersedes this branch, and `record_loss_appraisal_09001cb5` offers `total_loss_valuation` as an `appraisal_channel`. Inherited in full, and a world in which the appraised cost reaches the threshold would have two answers; neither task's world reaches it (task 0: 2727.80 against 0.75 × 41200.00 = 30900.00).

### CG-21 — observation, with a task-0 consequence — base's photo-estimate threshold leaves two channels open

`hostplan_evt_appraisal.rule`: "A claim worth more than the plan's photo estimate threshold cannot be settled on photographs and goes to an **in-person adjuster or a repair shop invoice**; a claim at or below the threshold may be settled on photographs alone." This is inherited in full and decides the `appraisal_channel` argument of `record_loss_appraisal_09001cb5`, but only down to two admissible values. The consequence for task 0's scored argument is demonstrated in `0.md`.

## closing_checklist

*(Reserved. This section is written only after both tasks' `source_derivation_frozen` sections are on disk and their GT has been revealed; everything above it was written before any reveal. A first draft of this section was written out of order and removed unread of any masked field — no masked field had been opened at that point, so nothing derived from GT entered the charter-global sections above.)*

Written now that both tasks' `source_derivation_frozen` sections are on disk and both GT reveals and comparisons are complete. **The difficulty does not close.**

- **Audit files and revisions — met.** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and `_difficulty.md` sits alongside them. This is revision 1; no older revision exists to preserve. Each task file carries its own `source_derivation_frozen`, `source_gt_comparison` and `findings`, and cites this file by path and heading for every charter-global conclusion rather than restating it.
- **Every comparison carries a PASS — NOT met.** `0.md` § verdict: SOURCE-POLICY RED (T0-F1), problem tree PASS, SOURCE-FACTOR RED (T0-F2, T0-F3), SOURCE-TASK RED (T0-F4). `1.md` § verdict: SOURCE-POLICY RED (T1-F3), problem tree PASS, SOURCE-FACTOR RED (T1-F1, T1-F2), unique solution PASS conditional on T1-F3.
- **Coverage, scope exclusivity and closure — met.** The revealed `charter_scope` of task 0 is `[hostplan_ext_damage_report_evidence, hostplan_ext_claim_opening, hostplan_ext_loss_appraisal, hostplan_ext_host_share]` with their four tools; of task 1, `[hostplan_ext_cover_restoration, hostplan_ext_claim_withdrawal, hostplan_ext_repair_supplement, hostplan_ext_reimbursement_release]` with their four. That is exactly the two-component partition of the `prerequisite` graph this file derived before any reveal (`policy_conflict_scan`), each component a whole problem tree — root plus all three of its prerequisite problems. The eight extended policies and eight task tools are covered once each and claimed twice by nobody. Each tool uses an independently generated, frozen uuid8 (`action_binding_and_uuids`).
- **Problem trees — met.** Each task has three prerequisite problems and no cycle; task 0 has three `value_input` edges and task 1 two, against a floor of `max(n−1,1) = 2`; each tree resolves one problem through an `owner=user` tool that the persona runs only on the agent's hand-over (`lodge_damage_report_2cc23be4`, `withdraw_own_claim_4cdcc89b`). The difficulty's six edges together form one DAG with no cross-task cycle. Every edge is unmet at its task's `frozen_time` on DB evidence and every edge bears weight, with the auditor's own replayed figures agreeing value for value with `prerequisite_closure.edge_load_bearing` in both tasks.
- **Factors — NOT met.** Every computation declares 4–6 factors with at least 2 `parameter` and 1 `method`; every ladder has three or more pairwise-disjoint tiers stated in full in its own `rule`, with no two tiers of any ladder selecting the same value or method; every task carries multi-source and cross-difficulty factors whose other-product holding and ledger rows are seeded and consistent with their own charters; and every computation carries a genuine near-miss. But four factors do not bear weight against an honest baseline — `loss_kind_ceiling` and `loss_of_use_daily_sum` in task 0 (CG-2, CG-3), `reserved_settlement_share` and `reserved_release_share` in task 1 (CG-4, CG-5) — and in three of the four cases the whole-baseline fall-back a reader derives from the computation document differs from the recorded `baseline_result` (5000.00 against 26000.00; 2422.00 against 2397.00; 2115.60 against 1861.73; 7630.00 against 6104.00). Two ladders also carry a tier this line of business does not (CG-14, CG-15), though neither task takes it.
- **Gates re-run on the final form — not applicable.** This audit modified no audited artifact, so the gate snapshot supplied with the brief still describes the final form: `check_extended`, `check_task_tools`, `replay_tasks --check`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire` are all green. Every red light in this audit is invisible to all seven of them — the undeclared overrides (CG-1, CG-11) are invisible because no gate compares base and extended sentence by sentence on the quantity that gets scored; the four straw-man baselines are invisible because the gates check `factor_sensitivity` against the *declared* `baseline` bindings rather than against `baseline.rule`; CG-6 is invisible because no gate evaluates a prerequisite `condition` on the world the resolving write leaves; CG-7 … CG-10 are invisible because `compute_basis` quotation is checked in one direction only; and T0-F4 is invisible because no gate reads a calendar against `user_scenario`.

**Overall: this difficulty does not pass the source-layer audit.** "Policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique solution PASS" does not hold for either task: the problem trees are sound in both, and everything else that the four relationships require of the worlds, the writes and the arithmetic checks out value for value, but policy self-consistency fails in both tasks, the factors fail in both, and task 0's unique solution fails on one scored argument.

---

## revision_2

Round 2 re-audit. Revision 1 above is left exactly as written.

### charter_global_frozen (revision 2)

- Freeze inputs and hashes (sha256:16), against round 1:
  - `hostplan.extended.yaml` — `05f0b141d1d48055` (round 1 `700ae25adc6614b1`, **changed**) → the charter-global section is **re-derived in full** below.
  - `task_tools.py` — `8333387e135f28bf` (round 1 `8333387e135f28bf`, **unchanged**) → `action_binding_and_uuids`'s tool-module half and the tool-body findings of revision 1 are **carried forward by reference on those two hashes**, not re-derived: the eight uuid8s, the absence of eligibility judgement from every function body, and observation CG-19 stand as recorded in revision 1.
  - masked views `0.json` — `6fd89fb6ddac095c` (round 1 `d960903c2c7abf47`, changed); `1.json` — `062eae421453c4ff` (round 1 `a80706b4702ce12e`, changed). Both worlds moved, so neither task's per-task sections are carried forward.
- Freeze time: 2026-09-22, round 2, before any field of either `tasks/*.json` outside `frozen_time` / `user_scenario` / `initial_state` was opened in this round. Auditor: the round-1 auditor, same isolation.
- Fields permitted and masked: as revision 1. Additionally read this round, and within the read domain: `blueprint/products/payouts.yaml` (the `payouts_evt_reserve` policy and the Standard schedule's reserve parameters), because two of this round's factor tiers rest on a seeded `payouts` holding and ledger row and the audit must test those rows against their own product's charter.
- `contamination_disclosure`: none. The coordinator's brief relayed dispositions by item id only and no value, parameter or intermediate; every figure below is the auditor's own. `tasks/*.json` entered no match domain before this freeze.
- Entry conditions: the coordinator's re-run gate snapshot is cited, not re-run. All seven gates green on the reworked artifacts.
- Independently confirmed, as the brief states: the extended file's base section is identical to `blueprint/products/hostplan.yaml` — `diff` over lines 1–897 is empty and a key-by-key comparison of every top-level block including `policies` reports SAME. Base was not edited.

### policy_conflict_scan (revision 2)

Structure is unchanged: 8 extended policies, one per target tool, same `(target_tool, computes)` pairs, same two graph components, same claimed-scope partition. `overwrite` has grown from 2 entries to 5:

| policy | overwrite entries | base policy | superseded clause verbatim in base? |
| --- | --- | --- | --- |
| damage_report_evidence | 1 (new) | hostplan_evt_claim_intake | yes |
| loss_appraisal | 1 (round 1) | hostplan_evt_appraisal | yes |
| host_share | 2 (new) | hostplan_evt_deductible ×2 | yes, both |
| cover_restoration | 1 (round 1) | hostplan_lifecycle_standing | yes |

Each `superseded_clause` was checked as a whitespace-normalised substring of the named base policy's own `rule` (5/5 located), and each `replaced_by` as a substring of the superseding extended policy's `rule` (5/5 located).

One conflict between base and extended that revision 1 did **not** record has become demonstrable this round, and one seeded cross-category row that revision 1 passed has become load-bearing. Both are written up as R2-1 and R2-2 in `findings`.

### rule_compute_equivalence (revision 2)

Re-run mechanically over all 8 policies: every `compute` binding has a `compute_basis` entry and every entry is a binding; every `compute_basis` value is a verbatim sentence of its own policy's `rule`; every `baseline.rule` sentence is a verbatim sentence of the `rule`; every factor's `bindings` are disjoint within its policy and every `decides` is an input binding, never `result`. 16 ladder-tier strings are not byte-identical substrings and each was checked by hand as the same clause with an article or demonstrative changed.

The four round-1 defects in the other direction — `compute` implementing a window the prose did not state — are each closed by the prose now stating the window the expression computes:

| round-1 item | round-2 rule text | expression | closed? |
| --- | --- | --- | --- |
| CG-7 | "two or more appraisals stand on the enrolment **in the two months before**" | `COUNT(..., within_months=2, ...)` | yes |
| CG-8 | "two or more workshop visits on the vehicle **in the three months before** were carried out in the partner network" | `XCOUNT(..., within_months=3, ..., shop_channel='partner_network')` | yes |
| CG-9 | "a report **lodged in the month before the appraisal** stands on the register" | `COUNT('hostplan_claim_intake', within_months=1, ...)` | yes |
| CG-10 | "the vehicle was towed **in that month**"; "counted from the day of **the most recent callout on the vehicle**" | `XSUM('roadside','roadside_callouts','tow_miles', within_months=1, ...)`; `XLATEST('roadside','roadside_callouts','callout_date', ...)` | yes |
| CG-12 | "more than that mark above **the highest reading taken at a workshop visit**" | `XMAX('service','service_visits','odometer_reading', ...)` | yes |

Note that CG-8 and CG-10 were closed by moving the prose to the expression rather than the expression to the prose. That is a legitimate closure of the equivalence defect — the two faces now agree — and it is what makes CG-8's ladder honest, since the rate is now stated to rest on the three-month visits rather than on "the visits counted", which the work-window factor moves.

One **new** equivalence defect in the other direction was introduced by the CG-6 rework: two clauses of `hostplan_ext_claim_withdrawal`'s `rule` describe the release and its residue in terms of what another claim on the loss covers, and no binding computes anything of the kind. Written up as R2-3.

### action_binding_and_uuids (revision 2)

Carried forward on the unchanged `task_tools.py` hash `8333387e135f28bf`; see revision 1 under this heading. Re-checked this round only for the part that depends on the charter: each `(target_tool, computes)` pair is still claimed by exactly one policy, and the eight pairs are unchanged.

### prerequisite_graph (revision 2)

Six edges, same six problems, same kinds and gates, same acyclic two-component shape. Two edges' sentences changed (host_share ← loss_appraisal; reimbursement_release ← claim_withdrawal). All six `policy_source` values are verbatim in the blocked policy's own `rule` (6/6 located mechanically). `form` is `state` on all six and no `fallback_reason` appears, which remains correct. No `prerequisite` field carries authoring-viewpoint phrasing. No rule names a tool, a policy id or a snake_case token; no depended-on rule restates the blocked policy's prerequisite sentence (both checked mechanically, 0 hits).

`resolved_by` genuinely makes `effect` hold — the round-1 failure on the sixth edge is closed. `withdraw_own_claim_4cdcc89b` writes a `hostplan_claim_withdrawn` row carrying `source_claim_id` on every call, whatever figure it releases, and the rewritten gate asks for exactly that record: "Money is released on a loss only once every other claim opened on that loss carries a withdrawal against it." The gate no longer depends on the amount, so the withdrawal makes it true outright.

### prerequisite_sentences (revision 2)

Four-point test on each of the six:

1. claim_opening ← damage_report_evidence — unchanged from revision 1; passes.
2. loss_appraisal ← claim_opening — unchanged; passes.
3. host_share ← loss_appraisal — **rewritten**: "The host's share of a loss is fixed only after **an appraisal of that loss stands on the enrolment with the money it accepts booked as owed to the host**." Connective "only after"; state form; no tool, id or token; scope matches the edge's `condition`. The round-1 ambiguity (CG-17) is closed: the waited-on state is now an appraisal record, and `record_loss_appraisal_09001cb5` is the only write of this difficulty that creates a `hostplan_claim_appraised` row, whereas `record_repair_supplement_1a6beabe` creates a `hostplan_supplement_added` row. One write, one reading.
4. repair_supplement ← cover_restoration — unchanged; passes.
5. reimbursement_release ← repair_supplement — unchanged; passes.
6. reimbursement_release ← claim_withdrawal — **rewritten**: "Money is released on a loss only once every other claim opened on that loss carries a withdrawal against it." Connective "only once"; the waited-on thing is a record-visible state named in the words the claim records use (a withdrawal standing against a claim); no tool, id or token; the `condition` — "Every other claim opened on the same loss as the claim being paid carries a withdrawal record against it on the enrolment" — is neither stronger nor weaker. Exactly one write of this difficulty creates a `hostplan_claim_withdrawn` row, so CG-18's second candidate (`release_claim_payment_a6ef5b4d`, which in round 1 could also bring the old money-based state about) is gone. **CG-18 dissolved.**

### override_declarations (revision 2)

Sentence-by-sentence sweep repeated against every `base_policy_refs` entry.

Closed: **CG-1** — both base sentences that fixed the deductible quantity are now named verbatim in `hostplan_ext_host_share.overwrite`, and the merged semantics are unique (the measurement ladder replaces "the share is the deductible"; the claim-free ladder with its unpaid-balance condition replaces base's unconditional discount-and-waiver sentence). **CG-11** — base's evidence floor is named verbatim in `hostplan_ext_damage_report_evidence.overwrite` and replaced by the desk-settled count.

Still open, and newly demonstrable: **R2-1**, base `hostplan_evt_appraisal`'s loss-of-use daily rate against `hostplan_ext_loss_appraisal`'s rebuilt daily-sum ladder, with `overwrite` naming only the double-cap clause.

Inherited base provisions re-checked and unchanged: the filing window and `trip_actually_completed`; the supplement window; `enrollment_still_settles`; `reimbursement_not_already_paid` and `payout_account_not_on_hold`; the appeal window; the portfolio standing rules. Observations CG-20 (total-loss branch) and CG-21 (photo-estimate threshold) stand unchanged, as the reworker claims.

### factor_ladders (revision 2)

| policy | factors | parameter | method | cross_difficulty read | changed this round |
| --- | --- | --- | --- | --- | --- |
| damage_report_evidence | 4 | 3 | 1 | service, listings | no |
| claim_opening | 6 | 5 | 1 | listings, payouts, roadside | `loss_kind_ceiling` outcome wording; `towed_miles` windowed |
| loss_appraisal | 6 | 4 | 2 | service, listings, roadside | `loss_of_use_daily_sum` rebuilt; anchor and endpoint tiers rewindowed |
| host_share | 4 | 3 | 1 | service, listings | no |
| cover_restoration | 6 | 5 | 1 | listings, service, payouts | no |
| repair_supplement | 6 | 5 | 1 | service, payouts, listings | `work_counted_window` tier 2 replaced; rate tier rewindowed; reserve ladder inverted |
| claim_withdrawal | 5 | 4 | 1 | payouts | measurement ladder tier 2 replaced and rewindowed; reserve ladder inverted |
| reimbursement_release | 6 | 5 | 1 | payouts, service | no |

Counts still inside 4–6 with at least 2 `parameter` and 1 `method` everywhere; every ladder still three tiers (four for `loss_kind_ceiling`), pairwise disjoint as stated and as implemented; no two tiers of any ladder select the same value or method (re-checked figure by figure against `params`); every label still honest.

Each of the four round-1 "decoration" factors now declares a baseline that is **both** the ladder's fall-through **and** what its own `baseline.rule` states:

| factor | round-2 `baseline.rule` sentence | declared `baseline` | fall-through tier | agrees? |
| --- | --- | --- | --- | --- |
| `loss_kind_ceiling` | "The provisional figure starts from the ceiling the plan carries for **damage to the body and paint** of the vehicle." | `kind_ceiling: ceiling_body` | "the report … names any other kind of loss" → the body and paint ceiling | yes |
| `loss_of_use_daily_sum` | "Loss of use is paid at **the plan's daily sum** for the days the vehicle stands off the road" | `loss_of_use_rate: plan_lou_daily` | "no defect stands recorded in that period" → the plan's daily sum in full | yes |
| `reserved_settlement_share` | "…with nothing taken off for how the loss was settled, how late the cost is brought, **what the host's payout account holds in reserve** or how far the vehicle has been driven since" | `reserve_share: '1.0'` | "those reserves are at least that ceiling and the account is active" → nothing taken off | yes |
| `reserved_release_share` | "…with nothing retained for the standing of the enrolment, for how late the withdrawal comes, **for what the host's payout account holds in reserve** or for the state of the reporting record" | `reserve_release_share: '1.0'` | "those reserves are at least that money and no money is stopped on the account" → nothing retained | yes |

CG-13 is closed the same way: `hostplan_ext_loss_appraisal.baseline.rule` now says outright "No share of the marketplace's out-of-network valuation fee is carried by the host", so the baseline decides `valuation_share` itself.

Two unreal tiers replaced:

- **CG-14** `work_counted_window` tier 2 is now "the work counted is **the largest single invoice the workshop has raised on the vehicle**" (`XMAX('service','service_visits','invoice_amount', …)`) in place of summing everything ever invoiced. A single real invoice on the vehicle is a measurement a marketplace could publish, and it no longer books a lifetime of routine servicing into one claim. Closed; one residual observation at R2-6.
- **CG-15** `release_measurement_basis` tier 2 is now "where **exactly one appraisal** stands in that period **and money stands booked as owed**, the release is measured as the money that appraisal booked" (`latest_appraisal_booked if (appraisals_in_window == 1 and money_booked > 0)`). The tier that released a positive sum precisely when nothing was owed is gone, and the three tiers are disjoint with the fall-through equal to the baseline. Closed.

Whether each factor bears weight is a fact about one world and is decided in `0.md` and `1.md` under `factor_weight` (revision 2). Two of them — `reserved_settlement_share` and `reserved_release_share` — bear weight only on a seeded reserve figure that the `payouts` charter cannot produce; that is R2-2.

### findings (revision 2)

Round-1 dispositions, verified item by item:

| item | round-1 verdict | round-2 verdict | where verified |
| --- | --- | --- | --- |
| CG-1 / T0-F1 | SOURCE-POLICY RED | **CLOSED**, by both declared routes | `override_declarations` (revision 2); the rebooked row at R2-4 |
| CG-11 | SOURCE-POLICY RED | **CLOSED** | `override_declarations` (revision 2) |
| CG-6 / T1-F3 | SOURCE-POLICY RED | **CLOSED** (resolved, not documented) | `prerequisite_graph` / `prerequisite_sentences` (revision 2); `1.md` revision 2 |
| CG-7 | SOURCE-POLICY RED | **CLOSED** | `rule_compute_equivalence` (revision 2) |
| CG-8 | SOURCE-POLICY RED | **CLOSED** | `rule_compute_equivalence` (revision 2) |
| CG-9 | SOURCE-POLICY RED | **CLOSED** | `rule_compute_equivalence` (revision 2) |
| CG-10 | SOURCE-POLICY RED | **CLOSED** | `rule_compute_equivalence` (revision 2) |
| CG-2 / T0-F2 | SOURCE-FACTOR RED | **CLOSED** | `factor_ladders` (revision 2); `0.md` revision 2 |
| CG-3 / T0-F3 | SOURCE-FACTOR RED | **CLOSED** (rebuilt) | `factor_ladders` (revision 2); `0.md` revision 2 |
| CG-4 / T1-F1 | SOURCE-FACTOR RED | **CLOSED on the charter; the world it now bites on is R2-2** | `factor_ladders` (revision 2); `1.md` revision 2 |
| CG-5 / T1-F2 | SOURCE-FACTOR RED | **CLOSED on the charter; the world it now bites on is R2-2** | `factor_ladders` (revision 2); `1.md` revision 2 |
| CG-14 | SOURCE-FACTOR RED | **CLOSED** | `factor_ladders` (revision 2) |
| CG-15 | SOURCE-FACTOR RED | **CLOSED** | `factor_ladders` (revision 2) |
| T0-F4 | SOURCE-TASK RED | **CLOSED** | `0.md` revision 2 |
| CG-12 | observation | **FIXED** | `rule_compute_equivalence` (revision 2) |
| CG-13 | observation | **FIXED** | `factor_ladders` (revision 2) |
| CG-17 / T0-F6 | observation | **FIXED** | `prerequisite_sentences` (revision 2) |
| CG-18 | observation | **DISSOLVED** | `prerequisite_sentences` (revision 2) |
| CG-16 | observation | no change, as claimed — `accepted_claims_12m` and `claims_accepted_for_standing` are still the identical expression under two names | re-read this round |
| CG-19 | observation | no change — `task_tools.py` is byte-identical | carried forward on the hash |
| CG-20 | observation | no change — `hostplan_evt_appraisal`'s total-loss branch is still neither implemented nor superseded | re-read this round |
| CG-21 | observation | no change | `0.md` revision 2 |
| T0-F5, T1-F5 | withdrawn on reveal in round 1 | remain withdrawn | — |

New findings this round:

### R2-1 — SOURCE-POLICY RED (new this round) — the rebuilt loss-of-use ladder pays less than base's daily rate, undeclared

- **Symptom.** Base and extended both fix the daily sum paid for loss of use, and on task 0's world they now fix it at two different figures. `hostplan_ext_loss_appraisal.overwrite` names only the double-cap clause.
- **Root cause.** CG-3 was closed by rebuilding the ladder so that its fall-through is the plan's full daily sum and its other two tiers reduce it. That is what made the factor honest against its own baseline — and it is also what put the scored world on a reduced rate for the first time, against a base sentence that fixes the rate at the plan's published figure.
- **Evidence.**
  - Base `hostplan_evt_appraisal.rule`: "Loss of use is paid at **the plan's daily rate** for the days the vehicle is genuinely off the road, up to the plan's maximum, and is not paid at all on plans that carry no loss of use benefit; **a benefit the plan does not carry is not paid at a reduced rate**."
  - Extended `hostplan_ext_loss_appraisal.rule`: "…where a defect stands recorded in that period and fewer than two claims have been opened on the enrolment in the twelve months before, it is paid at **the marketplace's part-earning share**"; `params.part_earning_share: 0.8`.
  - `hostplan_ext_loss_appraisal.overwrite` — one entry, on "The accepted amount is capped twice over…". Nothing about the daily rate.
- **Demonstrated consequence.** Demonstrated against task 0's world in `0.md` revision 2 § findings: base gives 50.00 a day and extended 40.00, and the difference carries through to two scored values.
- **Affected artifact and location.** `hostplan.extended.yaml`, `hostplan_ext_loss_appraisal.overwrite`, `.rule`, `.compute[loss_of_use_rate]`, `factors[loss_of_use_daily_sum]`; against `blueprint/products/hostplan.yaml` `hostplan_evt_appraisal.rule`.
- **Relation to previous revisions.** The clause conflict existed in the revision-1 charter, where both tasks sat on the full-rate tier so no consequence was demonstrable on any world; revision 1 therefore did not record it, and this audit records that as a miss of revision 1 rather than as a new defect of the charter. What is new in revision 2 is that the rebuild moved task 0 onto a reduced tier and made the conflict bite.

### R2-2 — SOURCE-FACTOR RED (new this round) — the two reserve factors bear weight only on a seeded reserve the `payouts` charter cannot produce

- **Symptom.** CG-4 and CG-5 were closed on the charter by inverting the two reserve ladders, and made to bite on task 1's world by rebooking `payouts_accounts.reserve_balance` from 3600.00 to 900.00 together with its ledger hold. 900.00 is not a figure the `payouts` charter can produce for this host.
- **Root cause.** The reserve figure the two factors read is a cross-difficulty holding, and it was moved to land the world on a reducing tier without being checked against the charter that governs it.
- **Evidence.**
  - `blueprint/products/payouts.yaml`, `payouts_evt_reserve.rule`: "An open claim holds **the claimed amount multiplied by the schedule's claim multiple, capped at the schedule's claim ceiling**, and that hold stands until the claim is paid, refused or withdrawn whatever the routine hold period says." The same policy enumerates the only other grounds — a routine reserve at the schedule's stated share of each earning, and a new-host reserve — and adds "a reserve is never taken from money that was itself a reserve release".
  - Keyturn Standard Payout Schedule parameters: `claim_reserve_multiple: 1.0`, `claim_reserve_cap_amount: 5000.0`, `reserve_percent_of_earning: 0`, `new_host_reserve_trips_count: 5`.
  - Task 1's seeded row `payouts_ledger['009a7390-e7e3-4e82-b5a4-fd8d5d0e0d44']`: `event_type='payouts_reserve_held'`, `entry_basis='reserve_hold'`, `hold_reason='claim_open'`, `booking_id='d76b6c45-…'`, `entry_date='2026-07-21'`, `entry_amount=-900.0`; and `payouts_accounts['a8c5e4ca-…'].reserve_balance = 900.0`, `payout_schedule_name='Keyturn Standard Payout Schedule'`.
  - The claim the hold names: `hostplan_claims['431643d4-…']`, filed 2026-07-21 on that booking, `claim_amount = 7900.0`. Under the quoted rule the hold is `min(7900.00 × 1.0, 5000.00) = **5000.00**`. Reading the hold off the appraised figure instead gives `min(6480.00 × 1.0, 5000.00) = 5000.00`. Counting the second open claim on the same loss only raises it. The routine share is 0 per cent on this schedule, the host opened the account in 2023 and has settled trips since, so neither of the other two grounds can supply 900.00 either, and no release row stands against the hold.
- **Demonstrated consequence.** Demonstrated against task 1's world in `1.md` revision 2 § findings: on a reserve figure the `payouts` charter does produce, both factors return to their fall-through and both become decoration again — which is the defect CG-4 and CG-5 were raised for.
- **Affected artifact and location.** `tasks/1.json` `initial_state.payouts_accounts['a8c5e4ca-…'].reserve_balance` and `initial_state.payouts_ledger['009a7390-…'].entry_amount`, against `blueprint/products/payouts.yaml` `payouts_evt_reserve` and the Standard schedule's parameters. Bears on task 1, through `hostplan_ext_repair_supplement.factors[reserved_settlement_share]` and `hostplan_ext_claim_withdrawal.factors[reserved_release_share]`.
- **Relation to previous revisions.** The round-1 world carried 3600.00, which the same charter also cannot produce; revision 1 passed the cross-category seeding check without testing the amounts against `payouts_evt_reserve`, and this audit records that as a miss of revision 1. What is new in revision 2 is that the figure has become load-bearing: in round 1 both ladders put 3600.00 and 5000.00 alike on the same tier, so the inconsistency changed nothing.

### R2-3 — SOURCE-POLICY RED (new this round) — the withdrawal rule now promises a release and a residue its own compute does not produce

- **Symptom.** Two clauses added to `hostplan_ext_claim_withdrawal` while closing CG-6 describe what the withdrawal releases, and what is left over, in terms of what another claim on the same loss covers. No binding of that policy computes anything about coverage by another claim, and on task 1's world the two accounts give different figures from the compute.
- **Root cause.** CG-6's residue needed an explanation once the release gate stopped speaking of money; the explanation was written into the rule and into `baseline.rule` as a second account of the same quantity rather than being implemented.
- **Evidence.**
  - `hostplan_ext_claim_withdrawal.rule` and `.baseline.rule`, opening sentence: "A host may take their own claim back off the enrolment, and doing so releases the money that claim had booked as owed to them **so far as another claim on the same loss already covers it**."
  - `hostplan_ext_claim_withdrawal.rule`, closing clause of the order sentence: "…what is not released **stays owed on the loss itself, being the part of the withdrawn claim that no other claim on that loss covers**."
  - `hostplan_ext_claim_withdrawal.compute[result]`: `RND(release_basis * reserve_release_share * standing_share * late_share * record_share, 2)`. Nothing in `release_basis`, and nothing in the four shares, reads what another claim covers: `release_basis` is measured from `money_booked`, `largest_appraisal` and `appraisals_in_window`, and the four shares from the payout reserves, the accepted-claim count, the days since the latest appraisal and the incomplete-report count.
  - `baseline.rule`'s next sentence gives a different quantity again: "What a withdrawal releases is **the whole of the money the claims on the enrolment have booked as owed to the host and not yet paid out**, released in full…", which is what the declared `baseline` (`release_basis: money_booked`) implements.
- **Demonstrated consequence.** Demonstrated against task 1's world in `1.md` revision 2 § findings, where the rule's own account gives a release of 1150.00 and a residue of 0.00 against a compute that gives 780.31 and 369.69, and where `baseline.rule` yields two different definite numbers — 1150.00 by its first sentence and 7630.00 by its second — for the figure a reader of the computation document is supposed to compute.
- **Affected artifact and location.** `hostplan.extended.yaml`, `hostplan_ext_claim_withdrawal.rule` (opening sentence and the closing clause of the order sentence) and `.baseline.rule` (opening sentence).
- **Relation to previous revisions.** New in revision 2. Revision 1's CG-6 was a contradiction between two policies; this is a contradiction inside one policy, between its prose and its compute, introduced while removing the first.

### R2-4 — observation — the rebooked historical deductible is consistent, on one reading

CG-1's second route rebooked `tasks/0.json initial_state.hostplan_claims['0fee43a6-…'].amount_delta` from 1275.00 to **436.36**, and its matching recovery `['53a49f5a-…'].amount_delta` from −1275.00 to **−436.36**, so that the enrolment's `liability_balance_due` still nets to 0.00 and no seeded row teaches base's retired formula. The figure is reachable from the charter as it now stands, but only on one reading of the enrolment's own history: 436.36 = `MN(RND(RND(0.4 × 1240.00, 2) × 0.85 × 0.90 × 1.15, 2), 1240.00)`, and the 0.85 is the claim-free rate, which needs at least the plan's 18 qualifying months claim-free on 2024-10-14. The enrolment's `claim_free_since_date` reads 2024-10-12 today, two days before that write — so the reading that makes the row consistent is that the field stood at the activation date 2022-05-18 when the deductible was raised (28 months) and was reset to 2024-10-12 by the accepted claim itself. That reading is the natural one and matches `hostplan_msr_claim_free_months`, so the row is not red-lighted; it is recorded because the row's consistency is not visible on the face of the seed.

Rebooking disturbed no aggregate: the only computes that touch `hostplan_deductible_charged` or `hostplan_recovery_received` rows are counts (`shares_raised_12m`, `recoveries_6m`), never the amounts, and both rows fall outside their windows in any case; and the netted `liability_balance_due` of 0.00 is what `claim_free_standing` and `late_notice_share` read.

### R2-5 — observation — task 0's payout reserve has no ground the `payouts` charter supplies

`tasks/0.json initial_state.payouts_accounts['496ba3da-…']` carries `reserve_balance = 1850.0` with `hold_reason = 'none'` on the Keyturn Standard Payout Schedule, whose `reserve_percent_of_earning` is 0; the host opened the account in 2022 and has five settled trips, so the new-host reserve does not apply; and at the opening no claim stands open on the enrolment, so `payouts_evt_reserve`'s claim hold does not apply either. Read as an exhaustive enumeration of the grounds on which money is reserved, the `payouts` charter supplies no ground for 1850.00. This is **not** red-lighted, for two reasons: no `payouts_ledger` row is seeded in this task, so there is no row that contradicts the charter — only a holding field whose provenance is unstated; and the figure is unchanged from round 1 and is no part of this rework. It is recorded because `hostplan_ext_claim_opening.factors[open_exposure_share]` bears weight on task 0 only through it: at a reserve of 0.00 the ladder returns its fall-through and the factor would be decoration.

### R2-6 — observation — `work_counted_window` tier 2 is still unbounded in time

CG-14's replacement, "the work counted is the largest single invoice the workshop has raised on the vehicle" (`XMAX('service','service_visits','invoice_amount', vehicle_id=…)` with no window), no longer sums a lifetime of servicing into one supplement, but it still reaches back over the whole workshop record and can select an invoice raised before the loss the claim settles. Neither task takes this tier, so nothing is demonstrated against a world.

### R2-7 — observation — two computation documents still publish figures their own standard method never uses

`hostplan_ext_claim_opening.baseline.params` lists `glass_sublimit_amount`, `tyres_wheels_sublimit_amount` and `interior_damage_sublimit_amount` alongside `exterior_damage_sublimit_amount`, although the baseline's method now starts from the body and paint ceiling alone; and `hostplan_ext_loss_appraisal.baseline.rule` still closes with "…and its out-of-network valuation share among them, is read from the plan", although the same baseline states that no share of that fee is carried. In both cases the closing sentence of the baseline is what licenses the extra figures, so the two are consistent with each other; the effect is that the computation document publishes plan figures its standard method does not consume, which weakens the separation between the baseline and the factor documents without making the baseline indefinite.

### closing_checklist (revision 2)

Written after both tasks' round-2 `source_derivation_frozen` sections were on disk and both GT reveals and comparisons were complete. **The difficulty still does not close**, on two findings rather than round 1's seven.

- **Audit files and revisions — met.** `0.md` and `1.md` correspond one-to-one with the two tasks; `_difficulty.md` sits alongside. Revision 1 is preserved intact in all three files, errata included, and revision 2 is appended below it; no round-1 blind answer was rewritten to accommodate round-2 GT.
- **Every comparison carries a PASS — NOT met.** Task 0: SOURCE-POLICY RED (T0-R2-1), problem tree PASS, factors PASS, unique solution PASS. Task 1: SOURCE-POLICY RED (T1-R2-2), problem tree PASS, factors SOURCE-FACTOR RED (T1-R2-1), unique solution PASS.
- **Coverage, scope exclusivity and closure — met.** `charter_scope` is unchanged and still the two components of the prerequisite graph, four policies and four tools each, disjoint and jointly complete. Tool uuid8s carried forward on the unchanged `task_tools.py` hash.
- **Problem trees — met, and better than round 1.** Three prerequisite problems per task, three `value_input` edges in task 0 and two in task 1 against a floor of 2, one `owner=user` write per tree, no cycle within or across tasks. Every edge unmet at `frozen_time` on DB evidence and every edge load-bearing, with the auditor's replayed figures agreeing value for value with `prerequisite_closure.edge_load_bearing` in both tasks. Task 1's sixth edge, which in round 1 declared an `effect` its resolving write did not bring about, now names a record the write creates unconditionally.
- **Factors — NOT met, on one finding.** All 43 declared factors across the two tasks now bear weight against baselines that are simultaneously the ladder's fall-through and what `baseline.rule` states, and all 43 `factor_sensitivity` figures and all 8 `baseline_result` figures were reproduced independently and agree. Every ladder still has three or more disjoint tiers stated in full in its rule, with distinct outcomes, and the two tiers this line of business would not publish have been replaced. Counts, multi-source and cross-difficulty requirements all hold. The one failure is R2-2: task 1's two reserve factors bear weight only on a seeded `payouts` reserve of 900.00 that the `payouts` charter cannot produce for this host, and on the figure that charter does produce, 5000.00, both revert to the decoration CG-4 and CG-5 were raised for.
- **Gates re-run on the final form — not applicable.** This audit modified no audited artifact; the coordinator's re-run snapshot describes the final form and all seven gates are green. Both round-2 findings are invisible to all seven: R2-1 because no gate compares base and extended sentence by sentence on the quantity that gets scored; R2-2 because no gate tests a seeded cross-category amount against the charter of the product that governs it; R2-3 because `compute_basis` quotation is checked from compute to rule only, so a rule sentence that no binding implements passes.

**Round-2 disposition of every round-1 item.** Thirteen of the fourteen round-1 REDs are genuinely closed, verified against the reworked charter and both reworked worlds: CG-1, CG-11, CG-6, CG-7, CG-8, CG-9, CG-10, CG-2, CG-3, CG-14, CG-15, T0-F4, and CG-4/CG-5 on the charter. The four observations the reworker claimed fixed — CG-12, CG-13, CG-17, CG-18 — are fixed or dissolved. The four it claimed unchanged — CG-16, CG-19, CG-20, CG-21 — are unchanged, with reasoning re-checked. Three defects remain or are new: **R2-1** (a base clause conflict that existed in round 1 but bore no consequence, made load-bearing by the CG-3 rebuild — and missed by revision 1), **R2-2** (a seeded cross-product row that contradicted its charter in round 1 too and bore no weight, made load-bearing by the CG-4/CG-5 world move — and missed by revision 1), and **R2-3** (newly introduced by the CG-6 rewrite). The first two are not regressions of the rework's own reasoning so much as pre-existing faults the rework stepped onto while moving the worlds; the third is a fresh defect of the rework. All three are recorded against the artifacts, none against any solving agent, and none is accompanied by a proposed fix.

**Overall: this difficulty does not pass the source-layer audit at revision 2.** Policy self-consistency fails in both tasks and the factors fail in task 1; the problem trees and the unique solutions pass in both, and every one of the sixteen scored values, arguments, balances and fall-backs the auditor derived independently matches GT to the cent.

---

## revision_3

Round 3 re-audit. Revisions 1 and 2 above are left exactly as written.

### charter_global_frozen (revision 3)

- Freeze inputs and hashes (sha256:16), against round 2:
  - `hostplan.extended.yaml` — `2c4706cfcc0dca29` (round 2 `05f0b141d1d48055`, **changed**) → charter-global section **re-derived in full**.
  - `task_tools.py` — `8333387e135f28bf` (**unchanged through all three rounds**) → the tool-module half of `action_binding_and_uuids`, every function-body citation and observation CG-19 are carried forward by reference on that hash.
  - masked views `0.json` — `5e7687a77f96d177` (round 2 `6fd89fb6ddac095c`, changed); `1.json` — `25628e95ff0aacd5` (round 2 `062eae421453c4ff`, changed). Both worlds moved again, so both per-task derivations are redone from scratch.
- Freeze time: 2026-09-22, round 3, before any field of either `tasks/*.json` outside `frozen_time` / `user_scenario` / `initial_state` was opened in this round.
- Permitted and masked: as revision 2, including `blueprint/products/payouts.yaml`, which R2-2's verification requires and which is in the read domain. No `payouts` tasks directory was opened.
- `contamination_disclosure`: none. The brief relayed dispositions by item id only; every figure below is the auditor's own. As in revision 2, the audit is not blind in the round-1 sense — rounds 1 and 2 GT are on disk — and that is disclosed rather than claimed away.
- Entry conditions: the coordinator's re-run gate snapshot is cited, not re-run; all seven gates green.
- Independently confirmed: `diff` of `blueprint/products/hostplan.yaml` against the extended file's first 898 lines reports only the trailing blank line, and a key-by-key comparison of every top-level block including `policies` reports SAME. Base was not edited.

### policy_conflict_scan (revision 3)

Structure unchanged: 8 extended policies, one per target tool, the same `(target_tool, computes)` pairs, the same two graph components and the same scope partition. `overwrite` has grown from 5 entries to 6, the new one on `hostplan_ext_loss_appraisal`. One factor was replaced outright (`reserved_release_share` → `overlapping_claims_share` in `hostplan_ext_claim_withdrawal`), one was re-based onto a different comparison quantity (`reserved_settlement_share` in `hostplan_ext_repair_supplement`), and one ladder was inverted (`open_exposure_share` in `hostplan_ext_claim_opening`). `hostplan_ext_claim_withdrawal` now declares `cross_category: []`.

All six `overwrite` entries were checked mechanically: each `superseded_clause` is a whitespace-normalised substring of the named base policy's own `rule` (6/6 located) and each `replaced_by` a substring of the superseding extended policy's `rule` (6/6). All six prerequisite `policy_source` values are verbatim in the blocked policy's own `rule` (6/6).

### rule_compute_equivalence (revision 3)

Re-run mechanically over all 8 policies, **with zero findings in either direction**:

- Forward: every `compute` binding has a `compute_basis` entry; every entry is a binding; every entry's value is a verbatim sentence of its own policy's `rule`; every `baseline.rule` sentence is a verbatim sentence of the `rule`; every factor's `bindings` are disjoint within its policy and every `decides` is an input binding.
- **Reverse sweep, run independently of the reworker's**: every sentence of every extended `rule` was tested for coverage by some `compute_basis` entry or by `baseline.rule`. Seven sentences are uncovered, and each was inspected by hand:

| policy | uncovered sentence | carries a quantity? |
| --- | --- | --- |
| damage_report_evidence | "When a host reports damage … the desk settles how many photographs and documents the report must carry, and the host lodges that many with the report." | no — the `replaced_by` text of its own `overwrite`, naming the subject |
| claim_opening | "A claim is opened on a loss only after a damage report for that trip stands on the register…" | no — its prerequisite sentence |
| loss_appraisal | "The amount the plan accepts on a loss is not settled before a claim for that loss stands opened…" | no — its prerequisite sentence |
| host_share | "The host's share of a loss is fixed only after an appraisal of that loss stands on the enrolment…" | no — its prerequisite sentence |
| repair_supplement | "Further cost is not added to a claim before the cover the loss was settled under stands in force again." | no — its prerequisite sentence |
| reimbursement_release | "The money released on a claim is not fixed until every further cost accepted…" | no — its prerequisite sentence |
| reimbursement_release | "Money is released on a loss only once every other claim opened on that loss carries a withdrawal against it." | no — its prerequisite sentence |

Every uncovered sentence is a gate, implemented by the problem tree rather than by a binding; **no rule sentence carries a quantity no binding produces**. This independently confirms the reworker's sweep claim, and it is the direct evidence that R2-3 is closed: round 2's two offending clauses — "so far as another claim on the same loss already covers it" and "the part of the withdrawn claim that no other claim on that loss covers" — would have appeared in this table as uncovered quantity-bearing sentences, and neither is present in the charter.

- **Cross-category declaration vs compute, checked mechanically**: for each policy the set of categories named in `CFIELD`/`CPARAM`/`EXISTS`/`XSUM`/`XCOUNT`/`XMAX`/`XLATEST` calls equals the set declared in `cross_category`, with zero mismatches. In particular `hostplan_ext_claim_withdrawal` declares none and calls none — its `cross_category: []` is honest, and the policy now reads only this category's own records.

### action_binding_and_uuids (revision 3)

Carried forward on the unchanged `task_tools.py` hash. Re-checked for the charter-dependent half: each `(target_tool, computes)` pair is still claimed by exactly one policy and the eight pairs are unchanged.

### prerequisite_graph and prerequisite_sentences (revision 3)

Six edges, unchanged in problems, kinds, gates and shape, acyclic, two components. All six sentences unchanged from round 2 and all six pass the four-point test as recorded there; the two that round 2 rewrote (host_share ← loss_appraisal; reimbursement_release ← claim_withdrawal) are unchanged in this round and remain correct. `resolved_by` still makes `effect` hold on every edge. No `prerequisite` field carries authoring-viewpoint phrasing; no rule names a tool, policy id or snake_case token.

### override_declarations (revision 3)

**R2-1 closed, and the partial quotation is sound.** `hostplan_ext_loss_appraisal.overwrite` now carries a second entry quoting base verbatim as far as the cap:

- Base sentence in full: "Loss of use is paid at the plan's daily rate for the days the vehicle is genuinely off the road, up to the plan's maximum, **and is not paid at all on plans that carry no loss of use benefit; a benefit the plan does not carry is not paid at a reduced rate.**"
- `superseded_clause`: "Loss of use is paid at the plan's daily rate for the days the vehicle is genuinely off the road, up to the plan's maximum" — a verbatim prefix.
- `replaced_by`: the policy's own three-tier daily-sum ladder, verbatim in its `rule`.
- Remainder left in force: ", and is not paid at all on plans that carry no loss of use benefit; a benefit the plan does not carry is not paid at a reduced rate."

A partial quotation is right only if the compute cannot violate the remainder **on any world the policy governs**, so that was tested over the whole plan ladder rather than on the two task worlds:

- The only plan carrying no loss-of-use benefit is Keyturn Shield 90 (`loss_of_use_daily_amount = 0.00`, `loss_of_use_max_days = 0`); every other plan carries 35.00/50.00/65.00/85.00/120.00 a day over 7/10/14/21/30 days.
- Every tier of the ladder is `plan_lou_daily` or `RND(plan_lou_daily × share, 2)`, so on Shield 90 the rate is 0.00 on **all three** tiers, whatever the defect and claim counts.
- Independently, `off_road_days = MN(MX(off_road_days_counted, 0), plan_lou_max_days)` is 0 on Shield 90 whatever the anchor and endpoint factors select.
- Hence `loss_of_use_element = RND(0.00 × 0, 2) = 0.00` on every Shield 90 world: nothing is paid at all, and because nothing is paid, nothing is paid at a reduced rate. The remainder is honoured everywhere, and it is not vacuous — it is exactly what stops the ladder's 0.6 and 0.8 shares from being read as a reduced-rate payment on a plan without the benefit.
- Quoting the cap away costs nothing: the extended rule re-states it ("never for more days than the plan's longest period") and the compute implements it.

The other five entries are unchanged and were re-verified verbatim. No new undeclared conflict was found: the sentence-by-sentence sweep against every `base_policy_refs` entry was repeated, and the base provisions recorded as inherited in revisions 1 and 2 are still inherited unweakened.

### factor_ladders (revision 3)

| policy | factors | parameter | method | cross_difficulty | changed this round |
| --- | --- | --- | --- | --- | --- |
| damage_report_evidence | 4 | 3 | 1 | service, listings | no |
| claim_opening | 6 | 5 | 1 | listings, payouts, roadside | `open_exposure_share` ladder inverted and its params renamed |
| loss_appraisal | 6 | 4 | 2 | service, listings, roadside | second `overwrite`; `baseline.params` trimmed |
| host_share | 4 | 3 | 1 | service, listings | no |
| cover_restoration | 6 | 5 | 1 | listings, service, payouts | no |
| repair_supplement | 6 | 5 | 1 | service, payouts, listings | `reserved_settlement_share` re-based onto `appraised_total` |
| claim_withdrawal | 5 | 4 | 1 | — (none) | `reserved_release_share` replaced by `overlapping_claims_share`; `cross_category` emptied |
| reimbursement_release | 6 | 5 | 1 | payouts, service | no |

Counts still inside 4–6 with at least 2 `parameter` and 1 `method` everywhere; ladders still three tiers (four for `loss_kind_ceiling`), pairwise disjoint as stated and as implemented, no two tiers of a ladder sharing a value or method, every label honest, every declared baseline simultaneously the ladder's fall-through and what `baseline.rule` states.

The three changed ladders:

- **`open_exposure_share`** (claim_opening) is turned round: the reducing tiers are now taken when the reserves are **below** the marketplace's provisioned-exposure mark, and the fall-through is "those reserves reach that mark → the figure is opened in full" = the declared baseline 1.0. The parameters were renamed to match (`provisioned_exposure_mark`, `unprovisioned_exposure_share`); the figures 1000.00 / 0.75 / 0.90 are unchanged. The new direction also agrees with the reading `reserved_settlement_share` now takes — the marketplace opening at less when its own provision is short — so the two ladders no longer point opposite ways.
- **`reserved_settlement_share`** (repair_supplement) is re-based from "below the plan's supplement ceiling" to "below **everything the appraisals on the enrolment have valued**", implemented as a new binding `appraised_total = SUM('hostplan_claims','amount_delta', event_type='hostplan_claim_appraised')`. Its ladder is also turned round, so the fall-through is "those reserves are at least everything those appraisals have valued and the account is active → nothing is taken off", equal to the declared baseline 1.0 and to `baseline.rule`'s enumeration. The rule gives the reason in business words: "the marketplace's own provision being short of what it has already accepted."
- **`overlapping_claims_share`** (claim_withdrawal) replaces `reserved_release_share` entirely, deciding a new binding `overlap_share` from the enrolment's own claim records: `same_kind_filings` (filed claims naming the same kind of loss as the most recently filed one) and `filings_2m`. Its three tiers are 0.93 / 0.97 / 1.0, the fall-through equal to the declared baseline, and `baseline.rule`'s enumeration was updated in step — "nothing retained … for claims on the enrolment that overlap the one being withdrawn". The factor is apt rather than merely available: the situation this policy exists to handle is a duplicate claim on one loss, and holding a share back "until it is settled which claim covers what" is what the ladder now weighs.

Whether each bears weight is decided per world in `0.md` and `1.md` under `factor_weight` (revision 3).

### findings (revision 3)

| round-2 item | round-2 verdict | round-3 verdict | where verified |
| --- | --- | --- | --- |
| R2-1 | SOURCE-POLICY RED (task 0) | **CLOSED** — declared by partial quotation, and the unquoted remainder honoured on every world the policy governs | `override_declarations` (revision 3); `0.md` revision 3 |
| R2-2 | SOURCE-FACTOR RED (task 1) | **CLOSED** — both seeded holds are figures the `payouts` charter produces, and both factors bear weight on the grounded world | `1.md` revision 3 § findings; task 0's twin closed at R3-1 |
| R2-3 | SOURCE-POLICY RED (task 1) | **CLOSED** — both offending clauses gone, `baseline.rule` yields one number, reverse sweep clean | `rule_compute_equivalence` (revision 3); `1.md` revision 3 |
| R2-4 | observation | stands — the rebooked precedent is unchanged at 436.36 and still consistent on the same reading | re-read this round |
| R2-5 | observation (task 0's ungrounded reserve) | **CLOSED unprompted** — see R3-1 | `0.md` revision 3 |
| R2-6 | observation | stands unchanged — `work_counted_window` tier 2 is still time-unbounded, and neither task takes it | re-read this round |
| R2-7 | observation | **FIXED** — `claim_opening.baseline.params` is now `['exterior_damage_sublimit_amount']` alone, and `loss_appraisal.baseline.rule` and `.params` no longer carry the valuation-fee figures its standard method does not use | re-read this round |
| CG-16, CG-19, CG-20 | observations | unchanged | re-read / carried on the tool hash |

### R3-1 — task 0's reserve regrounded, and the exposure ladder turned round with it — R2-5 closed

Revision 2 recorded as an observation that `tasks/0.json` carried `payouts_accounts.reserve_balance = 1850.0` for which the `payouts` charter supplies no ground, and that `open_exposure_share` bore weight on task 0 only through it. The reworker closed this unprompted. The field now reads **0.00**, which is what `payouts_evt_reserve` produces for this host: the Keyturn Standard Payout Schedule takes `reserve_percent_of_earning = 0`, the account was opened in 2022 and has five settled trips so the new-host ground cannot apply, and no claim stands open on the enrolment at the opening, so no claim hold stands. No `payouts_ledger` rows are seeded in this task, which is consistent with a zero balance rather than in tension with it.

The ladder was turned round in the same step so that the factor still bears weight at a reserve of 0.00, and the figures it selects are unchanged, so **no task-0 scored value moved** — verified by recomputing all four computations (`0.md` revision 3). This is the right shape of fix: the world was moved to what its own charter produces, and the policy was adjusted to that world, rather than the world being moved to rescue the policy.

### R3-2 — observation — `overlapping_claims_share` reads the whole life of the claim record on one conjunct

`same_kind_filings = COUNT('hostplan_claims', event_type='hostplan_claim_filed', damage_category=LATEST('hostplan_claims','damage_category', date_field='claim_date', event_type='hostplan_claim_filed'))` carries no window, so "two or more claims on the enrolment name the same kind of loss as the one most recently opened" reaches back over the enrolment's whole life. The rule says exactly that and the compute implements exactly that, so the two faces agree and this is not a rule/compute defect; it is recorded because a host with two glass claims four years apart would be counted as overlapping on that conjunct alone. The second conjunct (`filings_2m`) bounds the tier that actually reduces the release, so the effect is contained.

### R3-3 — observation — the two reserve ladders now point the same way, and one consequence is worth noting

`open_exposure_share` and `reserved_settlement_share` both now reduce what the marketplace books when its own provision is **short**. That is coherent and it is what closed R2-2 and R2-5. The consequence worth recording is that a host whose payout account carries no reserve at all — the ordinary case for a host with no open claim on the Standard schedule, which is exactly task 0 — sits on a reducing tier rather than on the fall-through, so the fall-through of `open_exposure_share` is reached only by hosts who *do* have money provisioned against them. That is defensible as written (the mark is 1000.00, not zero, and a host with earnings reserved under any ground clears it), but it means the ladder's ordinary customer is not on its ordinary tier.

### R3-4 — observation — two tracing sentences still name bases superseded in round 2

`tasks/1.json` carries two sentences that name a basis the charter retired in round 2 while quoting figures that are correct under the current basis: `computations[1].factor_trace[0]` says two appraisals stand "inside the plan's supplement window" where the rule, the ladder and that computation's own `tier_taken` read "in the two months before" (CG-7's fix), and `computations[2].factor_trace[1]` with its matching `design_rationale` line says "two of the visits counted were carried out in the partner network" where the rule reads "in the three months before" (CG-8's fix). Neither moves a figure on this world. Demonstrated and attributed in `1.md` revision 3 § T1-R3-4, including that this audit's own revision 2 missed them by checking tracing figures without checking tracing prose against the rule wording.

### closing_checklist (revision 3)

Written after both tasks' round-3 `source_derivation_frozen` sections were on disk and both reveals and comparisons were complete. **The difficulty closes.**

- **Audit files and revisions — met.** `0.md` and `1.md` correspond one-to-one with the two tasks, `_difficulty.md` sits alongside, and revisions 1, 2 and 3 are all present with the earlier text untouched, errata and all. No blind answer from any round was rewritten to accommodate a later round's GT.
- **Every comparison carries a PASS — met.** Task 0: policy self-consistency PASS, problem tree PASS, factors PASS, unique solution PASS. Task 1: the same four. Every one of the sixteen scored values, whole-baseline fall-backs and edge-load-bearing figures, and all forty-three factor sensitivities, were derived independently before the reveal and agree with GT to the cent.
- **Coverage, scope exclusivity and closure — met.** `charter_scope` unchanged and still the two components of the prerequisite graph, four policies and four tools each, disjoint and jointly complete; eight tools, eight policies, eight writes. Tool uuid8s independently generated and frozen, carried on a `task_tools.py` hash unchanged through all three rounds.
- **Problem trees — met.** Three prerequisite problems per task; three `value_input` edges in task 0 and two in task 1 against a floor of 2; one `owner=user` write per tree, handed over passively; no cycle within or across tasks; every edge unmet at `frozen_time` on DB evidence and every edge load-bearing.
- **Factors — met.** Every computation declares 4–6 factors with at least 2 `parameter` and 1 `method`; every ladder has three or more pairwise-disjoint tiers stated in full in its own rule, with distinct outcomes and with conditions and outcomes this line of business holds; every task carries multi-source and cross-difficulty factors whose other-product rows are seeded **and consistent with the charters that govern them**; every computation carries a near-miss; and **all 43 factors across the two tasks bear weight against baselines that are simultaneously the ladder's fall-through and what `baseline.rule` states**, with the whole-baseline fall-back a definite number different from gold in all eight computations.
- **Gates re-run on the final form — not applicable.** This audit modified no audited artifact; the coordinator's re-run snapshot describes the final form and all seven gates are green.

**Disposition of every finding raised across the three rounds.** Round 1 raised fourteen REDs and eight observations; round 2 verified thirteen REDs closed and raised three findings; round 3 verifies all three closed:

- **R2-1** closed by a partial `overwrite` quotation whose unquoted remainder this audit tested over the whole plan ladder rather than over the two task worlds, and found honoured everywhere.
- **R2-2** closed in both the parts revision 2 demanded: the reserve is now carried by two seeded holds the `payouts` charter itself produces at the schedule's multiple and ceiling, and both factors were changed — one re-based onto the enrolment's appraised total, one rebuilt outright onto the enrolment's own claim records — so that each bears weight on the grounded world rather than on an arranged figure. The rebuilt factor was tested for decoration and is not.
- **R2-3** closed by removing both clauses that promised a quantity no binding produces, leaving a `baseline.rule` that yields one definite number; confirmed by an independent reverse sweep over all eight policies, which found no rule sentence carrying an unimplemented quantity.
- **R2-5** closed unprompted and in the right direction: task 0's reserve was regrounded to what its charter produces and the ladder fitted to that world, with no scored value moved.
- **R2-7** fixed. **R2-4** and **R2-6** stand as observations, unchanged. Three new observations are recorded this round — **R3-2**, **R3-3** and **R3-4** — none of which moves a figure or fails a relationship.

**Overall: this difficulty passes the source-layer audit at revision 3.** Policy self-consistency, the problem tree, the factors' weight and the unique solution all hold for both tasks, on a charter whose every deviation from base is now declared and whose every rule sentence is implemented, and on two worlds whose cross-product rows are consistent with the charters that govern them.

---

## revision_4

Round 4 re-audit. Revisions 1–3 above are left exactly as written.

### charter_global_frozen (revision 4)

- Hashes, against round 3: `hostplan.extended.yaml` — `e7d1a91d212b1b19` (round 3 `2c4706cfcc0dca29`, **changed**) → charter-global section re-derived in full. `task_tools.py` — `8333387e135f28bf` (**unchanged through all four rounds**) → tool-module conclusions carried by reference. Masked views `0.json` — `5deb169dd668efb5` (changed); `1.json` — `25628e95ff0aacd5` (**unchanged from round 3**). Both derivations are redone from scratch regardless, because the charter moved under both.
- Freeze time: 2026-09-22, round 4, before any masked field of either task file was opened in this round.
- `contamination_disclosure`: none. Dispositions were relayed by item id; every figure below is the auditor's own. The audit is not blind in the round-1 sense and that is disclosed.
- Independently confirmed: base section `diff`-identical to `blueprint/products/hostplan.yaml` but for the trailing blank line.
- Entry conditions: all eight gates green per the coordinator's re-run, including `check_traceability` for the first time.

### the oracle used this round

Rounds 1–3 recomputed this charter with Python floats and `round()`, which **is the evaluator**, not the convention the prose states. That is why a tie survived three audits. This round the arithmetic was re-implemented exactly, in `Fraction` throughout — never `Decimal`, whose `//` truncates where the evaluator floors and would silently change `int(days/30)`-style counts — with each `RND` call instrumented to record the exact value reaching it. The test applied is the one that matters and is weaker than "every published figure is exact to the cent": **no rounding point is a tie**, i.e. the exact arithmetic arriving at each rounding never lands on a half-cent. A figure that is not exact to the cent is perfectly sound; a rounding point that sits on a half-cent is not, because half-up and the evaluator's banker's rounding part company there.

Result over both tasks, covering every scored value, every whole-baseline fall-back, every factor sensitivity, every edge-skip replay and every intermediate rounding inside them:

| task | rounding points instrumented | ties at a rounding point | half-up vs evaluator divergences | closest approach to a half-cent |
| --- | --- | --- | --- | --- |
| 0 | 64 | **0** | **0** | 1157.50368 (0.132 of a cent clear) |
| 1 | 90 | **0** | **0** | 1698.41475 (0.025 of a cent clear) |

154 rounding points, no tie, no divergence. The reworker's claim is confirmed, and confirmed on the correct property.

### the tie that was removed, and its cascade

The tie is reproducible and was real. At the round-3 loading of 1.15, `hostplan_ext_host_share`'s `share_measurement_basis` sensitivity is `1500.00 × 0.85 × 0.9 × 1.15`, which is exactly `10557/8 = 1319.625` — a rounding point sitting precisely on a half-cent. Half-up gives **1319.63**; the evaluator's `round()` gives **1319.62**, and 1319.62 is what round 3's GT recorded and what this audit's own rounds 1–3 reproduced, because those rounds ran the evaluator rather than the stated convention. At 1.16 the same product is `1331.10` exactly, and the full six-plan × three-tier × three-tier × three-tier matrix at the new loading — 162 combinations of published deductible, claim-free rate, care rate and loading — yields **0 ties and 0 divergences**, independently checked.

A tie is never one wrong number, so the cascade was traced rather than the named figure alone. Everything that reads `value_loading` moves:

| figure | at 1.15 | at 1.16 |
| --- | --- | --- |
| task 0 `host_share_amount` (scored) | 975.40 | **983.88** |
| `share_measurement_basis` sensitivity | 1319.62 | **1331.10** |
| `claim_free_standing` sensitivity | 1147.53 | **1157.50** |
| `vehicle_care_standing` sensitivity | 1083.77 | **1093.20** |
| `vehicle_value_loading` sensitivity | 848.17 | 848.17 (substitutes 1.0, correctly unmoved) |
| edge-skip, appraisal skipped | 436.36 | **440.15** |
| edge-skip, claim opening skipped | 501.11 | **505.46** |
| edge-skip, report skipped | 472.95 | **477.07** |
| terminal `liability_balance_due` | 975.40 | **983.88** |
| seeded 2024 share and its recovery | 436.36 / −436.36 | **440.15 / −440.15** |

Whether GT carries the whole of that cascade rather than only the named figure is checked in `0.md` revision 4 § `source_gt_comparison`.

### the audited rounding defect — route and reasoning

The render-layer auditor's finding was that `hostplan_ext_reimbursement_release` rounded mid-chain at `measured_payment` while its prose promised rounding once on the final result. Two routes existed: write the exception into the prose, or drop the `RND`. The reworker dropped it. **Both the route and the reasoning are right**, and the reasoning is verifiable rather than merely plausible:

- *All four baselines publish the same convention.* Every one of the eight policies states its rounding as "once" — "once, at the end", "once, on the final result", "once, after every rate has been applied". Writing an exception into one of them would have left that policy's computation document contradicting the other seven on the charter's most-repeated convention.
- *The rounding sat on a factor path.* `measured_payment` is the binding the `payment_measure` **method** factor decides. Naming a rounding that happens "when the payment is measured" in `baseline.rule` would tell a reader of the computation document that something varies at the measurement step — which is a ladder leaking into the document that is required to be silent about it.
- *And the route taken is the one that makes the prose true, rather than the one that makes the prose accommodate the code.* That is the correct direction for a source-layer fix.

The defect's consequence on task 1: `measured_payment` was `RND(8635.33 × 0.6, 2) = 5181.20`; unrounded it is `5181.198`, and the difference carries to `gross_payment` (4016.47 → **4016.46**) and to the scored release (2392.90 → **2392.89**).

### positive-direction sweep, re-run independently

Nine `RND` calls survive in the charter. Each was matched to the sentence that states it:

| policy | surviving rounding | stated by |
| --- | --- | --- |
| claim_opening | `result` | "the figure is rounded half up to two decimal places once, at the end" + "…once, on that final result, and never at an intermediate step" |
| loss_appraisal | `repair_element` | "the betterment share is then taken off the figure that step leaves **and that figure is rounded half up to two decimal places**" |
| loss_appraisal | `result` | "the accepted amount is rounded half up to two decimal places on that final result" |
| host_share | `result` | "rounded half up to two decimal places once, after every rate has been applied" |
| cover_restoration | `result` | "once, on the final result, and never at an intermediate step" |
| repair_supplement | `result` | "once, on the final result, and the ceiling is applied to that rounded figure" |
| claim_withdrawal | `result` | "rounded half up to two decimal places once, at the end" |
| reimbursement_release | `gross_payment` | "…applied one after another to the figure each step leaves **and that figure is rounded half up to two decimal places**, the withholding is taken from the rounded figure" |
| reimbursement_release | `result` | "it is rounded half up to two decimal places once, on the final result" |

Ten roundings were dropped — the audited one plus the nine the reworker reports: `recovery_addition`, `loss_of_use_rate`, `loss_of_use_element`, `valuation_charge`, `share_basis`, `period_charge`, `supplement_ceiling`, `money_booked`, `withheld`, `set_off`. Each removal also makes true a sentence that was previously false: the three "never at an intermediate step" claims now hold, and "once" now holds in the six policies that assert it.

Every other machine convention was swept independently, and each is stated where it acts: the document round-up (`int(x)+1 if…`) by "rounded up to a whole document"; the document floor (`MX(1,…)`) by "never below one"; the day floor (`MX(…,0)`) by "never for fewer than none"; the day cap (`MN(…, plan_lou_max_days)`) by "never for more days than the plan's longest period"; the three amount caps (`MN` against the physical damage limit, the accepted amount, the supplement ceiling) each by its own clause; the payment floor (`MX(…,0.0)`) by "the payment is never less than nothing"; the period counts (`int(days/30)`, `int(days/7)`) by "whole months of thirty days" and "whole weeks of seven days", with the threshold restated as "thirty days or more"; and the three selection conventions by "the largest amount a claim stands opened at on the enrolment", "the largest amount an appraisal on the enrolment has booked" and "the most recent report on the register". One residual is recorded at R4-1.

### negative-direction sweep, re-run independently

Both reported instances are closed, and the prose moved with the compute:

- **Roadside, six reads.** `callouts_1m`, `towed_miles`, `recovery_billed_1m` in `claim_opening` and `tow_callouts_1m`, `towed_distance`, `recovery_day` in `loss_appraisal` all now carry `event_type='roadside_callout_completed'`, and the prose reads "a callout on the roadside cover the vehicle carries **was completed** in the month before" and "the day of the most recent **completed** callout". This matters: the `roadside` product publishes `roadside_credit_granted`, `roadside_callout_dispatched`, `roadside_excess_charged` and `roadside_callout_cancelled` on the same table, so an unfiltered read counted credits and cancellations as callouts that attended the vehicle.
- **Inspections, seven reads.** `months_since_passed_inspection`, both `defects_6m`, `latest_defect_date`, `latest_pass_date` and both `passed_inspections_12m` now carry `vehicle_id=F('vehicle_id')`, matching prose that says "on the vehicle" and "on it" throughout. A host with two listings would otherwise have had another vehicle's inspection clear this vehicle's defect.

One instance of the same class the sweep did not reach is recorded at R4-2.

### rule_compute_equivalence, prerequisite graph, override declarations (revision 4)

Re-run mechanically over all eight policies with zero findings in either direction: every binding has a verbatim `compute_basis`; every `baseline.rule` sentence is in the `rule`; every factor's bindings are disjoint and real; every `decides` is an input; the reverse sweep finds seven uncovered sentences, each a prerequisite gate or an `overwrite` scene-setter and none carrying a quantity; and the categories each policy calls equal the categories it declares. The six `overwrite` entries and six prerequisite sentences are unchanged from round 3 and re-verified verbatim. Ladder structure is unchanged except for `high_value_loading`, whose three outcomes remain distinct (1.16 / 1.08 / 1.0).

### findings (revision 4)

| round-3 item | round-4 verdict |
| --- | --- |
| audited mid-chain rounding | **CLOSED** — route and reasoning both sound; verified against the exact oracle |
| positive-direction sweep | **complete**, with one residual observation (R4-1) |
| negative-direction sweep | **complete as to the two instances reported**, with one further instance of the same class found by this audit (R4-2) |
| tie sweep | **complete** — 154 rounding points, 0 ties, 0 divergences, cascade traced |
| R3-2, R3-3, R3-4 (round-3 observations) | R3-4 is **fixed** — both stale tracing labels now name the current basis; R3-2 and R3-3 stand unchanged |

### R4-1 — observation — one "once" claim coexists with a second stated rounding

`hostplan_ext_reimbursement_release` is the only policy whose rounding sentence says "once" while its compute rounds twice: "it is rounded half up to two decimal places **once**, on the final result" sits in the same rule as the order sentence's "…and that figure is rounded half up to two decimal places, the withholding is taken from the rounded figure". Both roundings are stated, so nothing is hidden, and under the baseline the claim is literally true — with every share at 1.0 and `measured_payment = owed_standing`, the `gross_payment` rounding is a no-op on an already-two-decimal figure. The tension exists only in the full rule.

This audit treated the two readings as the addendum directs — by checking the rounding points, not by observing that the outputs agree. A reader who takes "once" literally and does not round at `gross_payment` computes `4016.4646896 − 963.951525504 − 659.62 = 2392.893164096`, a rounding point 0.316 of a cent clear of a half-cent; the route the compute takes passes through 4016.4646896 (0.031 clear) and 2392.8896 (0.46 clear). Neither reading has a tie, so the agreement at 2392.89 is not an agreeing tie masking a divergence — it is a genuine agreement. Recorded as an observation and not red-lighted: no figure moves, and this is the same sentence the reworker deliberately kept out of `baseline.rule`, for the sound reason recorded under the four policy-side items.

### R4-2 — observation — the service-visit reads carry no event-type filter, and one of them is load-bearing

The negative-direction sweep closed the roadside and inspection reads but did not reach `service_visits`, which the `service` product populates with `service_credit_granted`, `service_visit_completed`, `service_excess_charged`, `service_visit_missed` and `service_plan_billed` rows. Of this charter's eight reads of that table, only `damage_report_evidence`'s `completed_visits_6m` filters (`outcome='completed'`); `visits_3m`, `workshop_visits_6m`, `visits_1m`, `partner_visits_6m`, `partner_visits_counted`, `work_counted` and `last_visit_reading` do not.

The prose is defensible for most of them — `work_counted` says "what the workshop has **invoiced**", which is exactly what a `service_excess_charged` row is — but two readings are worth stating on the record rather than leaving silent, because a `service_visit_missed` row is by the product's own words "a booked visit [that] does not happen" and a `service_plan_billed` row is a monthly fee, and neither is a workshop visit:

- `cover_restoration.workshop_visits_6m` against "a workshop visit stands on it in the six months before";
- `reimbursement_release.visits_1m` against "a workshop visit stands on it in the month before, **the vehicle being still in the shop**".

This is **load-bearing on task 1**: its two September-quarter rows are `service_excess_charged`, so on the reading that counts any row `visits_1m = 2` and `repair_share = 0.95`, while on a reading restricted to visits that happened `visits_1m` would be 0 and `repair_share` 0.98, moving the scored payment. The compute and the prose do agree on the reading taken — a billed excess is a workshop record standing on the vehicle — and neither task's world contains a missed visit or a plan billing, so no second answer is demonstrable and this is **not** red-lighted. It is recorded because the same reasoning that justified filtering the roadside reads applies here unexamined, and because a world seeded with a missed visit would turn it into the defect the sweep was for.

### R4-3 — judgement on the four policy-side items

1. **Base `hostplan_evt_appraisal.formula`** — `when: damage_category == "glass"`, `amount_delta: min(appraisal_amount, glass_sublimit_amount, physical_damage_limit_amount)`. This encodes the double cap that `hostplan_ext_loss_appraisal.overwrite` declares superseded. The reworker judged it unfixable and unwarranted; **agreed on both counts**. Unfixable: the base section must be copied verbatim from a blueprint this difficulty may not edit, and `overwrite` names clauses of a base `rule`, so no mechanism exists to retire a `formula`. Unwarranted: it does not fire on task 0's world at all (`damage_category = 'interior'`), and the clause it encodes is declared superseded in the prose that is what gets rendered.
2. **Base `hostplan_evt_deductible.formula`** — `round(host_deductible_amount × (1 − claim_free_discount_percent/100), 2)`, which on task 0 gives 1275.00 against a scored 983.88. **Agreed, with the reasoning stated rather than assumed.** Both base *rule* sentences this formula encodes are named verbatim in `hostplan_ext_host_share.overwrite` and declared superseded — that was CG-1's closure — so the prose a reader meets no longer states it. The formula is a machine residue of retired prose, reachable by no reader of the documents. This judgement rests on the render contract carrying rules rather than formulas; `check_traceability` is green on the published KB, which is the evidence available to a source-layer audit.
3. **The two compute-only conventions now written into prose** — "thirty days or more", "whole months of thirty days", "whole weeks of seven days" for `int(days/30)` and `int(days/7)`, and "never for fewer than none" for the day floor. **Right call.** Here the machine was correct and the document silent, so the fix belongs in the prose; the opposite direction from the audited rounding defect, where the document was correct and the machine wrong. Both were resolved toward the document's own standing convention, which is the consistent principle.
4. **The assembly sentence left in `rule` only** — `reimbursement_release`'s order sentence, kept out of `baseline.rule`. **Right call.** It names the shares for the standing of the enrolment, the state of the repair and an earlier payment, which are three ladders; putting it in the computation document would leak all three. The cost is R4-1's residual "once" tension, which moves no figure, and that is the cheaper of the two prices.

### R4-4 — judgement on the reseeding

Task 0's seeded 2024 history was reseeded with the loading: `hostplan_claims['0fee43a6-…'].amount_delta` 436.36 → **440.15** and its matching recovery −436.36 → **−440.15**. This audit flagged at round 2 the shape where a world is moved to rescue a factor, so the two cases are worth separating explicitly.

**This is the honest case, and it is the opposite manoeuvre.** Three tests distinguish them:

- *Is the new figure derived or chosen?* Derived. Recomputing the 2024 write with this charter's own policy at the new loading gives `MN(RND(0.4 × 1240.00 × 0.85 × 0.90 × 1.16, 2), 1240.00) = 440.1504 → **440.15**`, reproduced independently to the cent. The round-2 case failed exactly here: 900.00 was a figure the governing charter could not reach by any route.
- *Does it change which tier anything sits on?* No. The pair still nets `liability_balance_due` to 0.00, which is what `claim_free_standing` and `late_notice_share` read, and no binding of this difficulty reads a deductible or recovery **amount** — `shares_raised_12m` and `recoveries_6m` are counts, and both rows fall outside their windows in any case. No factor's weight depends on the reseeding; the round-2 case existed solely to move a tier.
- *Which direction did it travel?* The rate moved first, for a reason internal to the charter, and the world was brought back into conformity with it. At round 2 the world moved first, to make a ladder bite. A seeded history that still obeyed the retired 1.15 would have been the defect — a precedent on the enrolment teaching a rate the charter no longer publishes, which is precisely what CG-1's second route was closed to prevent.

The reseeding rests, as at round 2, on reading the enrolment's `claim_free_since_date` as having stood at the activation date when the 2024 deductible was raised and been reset by that accepted claim; that reading is unchanged and is recorded at R2-4. **Not red-lighted; recorded as sound.**

### R4-5 — `auditor_erratum` against this revision's own pre-reveal table

The round-3 disposition table above records "R3-4 is **fixed**". It is not: both stale tracing labels survive unchanged, as the reveal shows and as `1.md` revision 4 § T1-R4-2 documents with citations. That line was written before the reveal from the reworker's general account rather than from evidence, which is a discipline failure of this audit — a disposition relayed by item id is not evidence, and no claim about GT content belongs in a pre-reveal section. The frozen text is left as written; **R3-4 stands open** as an observation, unchanged in substance: correct figures, retired basis names, no figure moved.

It is also worth recording that the reworker's own framing, repeated in both task files' `design_rationale` — "an exact-decimal (Fraction) re-implementation recomputed all 59 published figures … 59 of 59 reproduced" — is a stronger and less exact statement of the property than the one that matters. Exactness of the published figures is neither necessary nor sufficient; **no rounding point is a tie** is the sound property, and it is the one this audit tested and confirmed. The count itself checks out: 8 scored values + 8 `baseline_result` figures + 43 factor sensitivities = 59.

### closing_checklist (revision 4)

Written after both tasks' round-4 frozen sections were on disk and both reveals and comparisons were complete. **The difficulty closes, as at revision 3, on a charter and two worlds that are now also arithmetically sound.**

- **Audit files and revisions — met.** Four revisions in each of the three files, every earlier revision intact, errata preserved rather than repaired in place. Two errata are recorded this round-family: this one, and the two arithmetic slips of revisions 1 and 2.
- **Every comparison carries a PASS — met.** Both tasks pass all four relationships. All 59 published figures, plus every edge-load-bearing figure and every intermediate rounding inside them, were derived exactly before the reveal and agree with GT to the cent.
- **Coverage, scope, problem trees, factors — met**, unchanged from revision 3 and re-verified: eight policies, eight tools, two disjoint whole trees; three prerequisite problems per task with the `value_input` floor met and one `owner=user` write each; 43 factors all bearing weight against baselines that are simultaneously the ladder's fall-through and what `baseline.rule` states.
- **Arithmetic — met, and newly so.** 154 rounding points across the two tasks, **0 ties and 0 half-up-vs-evaluator divergences**, on an oracle implemented in `Fraction` and instrumented at the rounding points rather than at the outputs. Ten unstated intermediate roundings were removed, nine stated ones remain and each was matched to the sentence that states it, and every other machine convention — two floors, four caps, two round-ups, two period counts, three selection rules — was found stated where it acts.
- **Gates — all eight green** on the final form per the coordinator's re-run, including `check_traceability`. The tie was invisible to all of them, as it was to this audit's first three rounds, because it sat in a sensitivity figure and produced agreement rather than disagreement.

**The three sweeps.** The positive-direction sweep is complete, with one residual observation (R4-1). The negative-direction sweep is complete as to the two instances reported, and this audit found a third instance of the same class it did not reach (R4-2, the service-visit reads), load-bearing on task 1 but not demonstrable as a second answer on either world. The tie sweep is complete and was re-run independently on the correct property, with the cascade traced and confirmed propagated in both tasks.

**Standing observations at close:** R2-4 and R2-6 (from round 2), R3-2 and R3-3 (from round 3), R3-4 (from round 3, **still open**), R4-1 and R4-2 (this round). None fails a relationship; none is a red light; each is on the record with the reason it was not red-lighted.

**Overall: this difficulty passes the source-layer audit at revision 4.** Across four rounds it has been through seventeen red lights — fourteen at round 1, three at round 2 — every one of which is now closed and verified closed against the artifacts rather than against an account of them.
