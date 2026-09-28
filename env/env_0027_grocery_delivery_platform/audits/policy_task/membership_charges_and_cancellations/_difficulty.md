# Policy-task audit — membership_charges_and_cancellations / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. Not the instantiating agent.
- Freeze time: 2026-09-25T00:10Z (written before any task's GT was revealed; nothing below comes from a revealed GT).
- Freeze hashes (match the brief):
  - `tasks/membership_charges_and_cancellations/membership.extended.yaml` sha256 `b5a6e9ccc8bec0ad01bbf6b18eb835c42c0f6c2a60c5322a0d724e425e3079e4`
  - `tasks/membership_charges_and_cancellations/task_tools.py` sha256 `291b2441cb1ba2e4846bdcc5a53fe82661cd4fc6df6d2023af48534d6afb263a`
- Fields read: `blueprint/blueprint.yaml` (difficulties), `blueprint/products/membership.yaml`, `blueprint/share_tools.py`, targeted lines of `blueprint/products/order.yaml` (fee schedule, service fee, order_fee_waived) and the rewards tier names in `blueprint/products/rewards.yaml`, the full extended charter, the full `task_tools.py`, and the two orchestrator masked views (frozen_time, user_scenario, initial_state only).
- Fields masked and not read at freeze: every `tasks/*.json` field other than the three above (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), the instantiator's `worklog.md`, and any other audit output. No recursive search touched `tasks/`.
- Entry conditions (Step 0): the brief supplies the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred because the KB is not yet published), the masked views and their hashes. The view hashes were re-computed and match. Inputs complete. The deferred traceability gate is noted, not treated as a defect of these artifacts.
- The DSL evaluator's source was not consulted; every compute binding was read against the rule prose (whole-month windows "ending today, a row dated on the same day of the month that many months back not counted"; `DAYS(a, b)` as the calendar days from a up to the day before b, which is what each rule sentence states).

### policy_conflict_scan

Base section: lines 1–1269 of the extended charter are byte-identical to `blueprint/products/membership.yaml` (`diff` empty). Six extended policies, six task tools:

| Policy | Base refs | Subject / computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| membership_ext_term_charge_refund | fee_refund | membership_fee_refunded / amount_usd | confirm_annual_term_early_end_0b7355fe (user) | [] |
| membership_ext_carried_value_refund | fee_refund | membership_fee_refunded / amount_usd | refund_carried_term_value_822a3886 (agent) | [] |
| membership_ext_move_to_monthly_charge | plan_switch | membership_plan_switched / amount_usd | move_annual_plan_to_monthly_dc3bc730 (agent) | term_charge_refund, carried_value_refund |
| membership_ext_pause_length | pause | membership_paused / pause_days | book_membership_pause_b6aef13b (agent) | move_to_monthly_charge |
| membership_ext_past_due_settlement | failed_payment, fee_billing | membership_reinstated / amount_usd | settle_past_due_membership_fee_b438dc6f (user) | [] |
| membership_ext_annual_upgrade_charge | plan_switch | membership_plan_switched / amount_usd | upgrade_membership_plan_10b03fa3 (agent) | past_due_settlement |

Overlapping subjects:
- Two policies compute `membership_fee_refunded.amount_usd` (term and carried). They are separated by object: the term refund is "booked against" "the fee charge on the membership whose billing period start is the first day of the current term"; the carried refund is "booked against" "the fee charge captured most recently before the term's first day". Both tools stamp `refund_type="prorated_annual"`. No conflict on the same charge; order between them is free (neither computation reads a refund row — term reads `membership_fee_charged` rows and order waivers; carried reads the plan-switch charge, `membership_fee_charged` counts and order waivers).
- Two policies compute `membership_plan_switched.amount_usd` (move and upgrade). Separated by direction and scope: move is "A member on Cartwise+ Annual who asks for a pause is moved to Cartwise+ Monthly"; upgrade is "A member on a monthly plan who moves up to Cartwise+ Annual". Disjoint.
- Time anchors: all extended windows use "whole months ending today, a row dated on the same day of the month that many months back not counted"; day counts are "from today up to the day before" the renewal date. Consistent across policies.
- Cross-category reads: order (`order_events` waivers and item charges) and rewards (`rewards_accounts.variant_name`), read-only. No policy writes outside `memberships` / `membership_events`.
- Terminal states: term and carried refunds leave plan/status/dates unchanged (tool docstrings; the carried rule says so outright). Move sets Monthly + new one-month period; pause sets paused; settlement sets active and clears past_due_since; upgrade sets Annual + twelve-month period.
- Scope partition implied by the prerequisite graph: tree A = {pause_length (root), move_to_monthly, term_charge_refund, carried_value_refund}; tree B = {annual_upgrade_charge (root), past_due_settlement}. The two trees are disjoint and together cover all six extended policies. (Checked against `charter_scope` after the reveal, in the task files.)
- Conflicts found: see `### findings` F1 (move scope vs its second prerequisite), F2 (full_unused sentence left standing under both refund policies).

### rule_compute_equivalence

A mechanical check (every `compute_basis` value, every `policy_source`, every sentence of `baseline.rule` and every `replaced_by` is a whitespace-normalised substring of that policy's `rule`; every factor's `decides` and `bindings` names a compute binding; bindings are pairwise disjoint across a policy's factors; every ladder has 3 tiers) returned no failure for any of the six policies.

Sentence-by-sentence sweep back (rule -> compute), per policy:
- term_charge_refund: opening charge (`SUM ... billing_period_start=F('current_period_start')`), whole-months enrolment, last-month waiver count, months completed, the three unused-share methods, the switch-opened test, the three opening rates, gross rounding, 12-month capture count, the 1/2/3-month waiver window, rewards tier, offset rate, rounded offset, floor at zero: all present both ways. `waivers_last_month` / `offset_waivers` read every `order_fee_waived` row, whereas the rule says "member fee waivers"; the order charter defines `order_fee_waived` as "A fee that would otherwise apply is waived or reduced by a membership benefit" (order.yaml `order_fee_waived.meaning`), so the two are the same set. No empty promise.
- carried_value_refund: carried value, switch age, three share methods, rewards rate, retry-based handling, capture-based waiver share, last-month waiver sum, inner rounding of the waiver share, floor at zero: present both ways.
- move_to_monthly_charge: value held (`term_opening_charge + (P - term_opening_charge) - SUM(prorated_annual refunds, 1 month)`; the unfiltered opening-charge sum cancels algebraically, so it equals the rule's "plan-switch charge ... plus the value carried ... less every prorated-annual refund"), three value-run methods, retry-based credit share, rewards move rate, renewal-count welcome-back, last-month waiver-count activity credit, floors and roundings: present both ways.
- pause_length: plan allowance, tenure (captures and enrolment), rewards, 3-month item spend, 12-month pause-days reduction by first paused day, fresh-period reduction (switched in last month; latest plan-switch charge vs period fee), notice (days to renewal), floor at pause_min_days: present both ways.
- past_due_settlement: period fee, days past due, the three settled-share methods, courtesy (12-month retry count and lifetime captures), rewards partner credit, early credit (compute tests `eligibility_reverification_months > 0` for "a plan that requires eligibility proof"; over the six variants this is the same set: Assist and Student are the only plans with proof and with 12), final rounding and floor: present both ways.
- annual_upgrade_charge: kept fee of the current period, three credit methods, graduation rate (Student + captures), rewards offer, 3-month item spend, re-verification offer (proof plan + months since proof), anniversary offer, final rounding and floor: present both ways.

Result: no rule/compute mismatch that yields a different number on any input.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are six distinct tools, each claimed by exactly one policy.
- uuid8 suffixes: `0b7355fe`, `822a3886`, `dc3bc730`, `b6aef13b`, `b438dc6f`, `10b03fa3`: pairwise distinct, no common prefix or tail, no sequence or adjacent-value pattern. Nothing suggests reuse or batch derivation.
- No task tool body checks status, timing, prerequisites or ownership (all six bodies read the membership row only to copy `customer_id`, `current_period_start` or `current_period_end` into the write). The module docstring says: "No tool checks status, timing, ownership or any other business condition".
- Docstrings name no other tool and state no position in a call sequence. Two use after-the-fact wording that is not about sequence: confirm_annual_term_early_end ("whose refund reference the member can quote afterwards") and refund_carried_term_value ("the refund then shows among the membership's entries"). Observation O6.
- `upgrade_membership_plan_10b03fa3` accepts any `variant_name`. The docstring rules out the three monthly plans ("never used with this action"), and the policy scope is monthly -> Cartwise+ Annual, so it gives only one business reading.

### prerequisite_graph

Edges (all `form: state`, no `fallback_reason`, all `kind: value_input`):

| Blocked policy | problem | gate (binding exists?) | resolved_by = depended-on target_tool? |
| --- | --- | --- | --- |
| move_to_monthly_charge | term_charge_refund | value_held (yes) | confirm_annual_term_early_end_0b7355fe (yes) |
| move_to_monthly_charge | carried_value_refund | value_held (yes) | refund_carried_term_value_822a3886 (yes) |
| pause_length | move_to_monthly_charge | plan_allowance (yes) | move_annual_plan_to_monthly_dc3bc730 (yes) |
| annual_upgrade_charge | past_due_settlement | period_kept_fee (yes) | settle_past_due_membership_fee_b438dc6f (yes) |

- Every policy has `prerequisite` filled (`[]` on the four others). Every `problem` names an extended policy in this file, never a base policy or itself. The graph is acyclic (two trees, depth 2 and 1).
- Every `policy_source` is quoted verbatim from the blocked policy's own `rule` (mechanical check above).
- `resolved_by` genuinely moves the binding: confirm/carried book `membership_fee_refunded` rows with `refund_type="prorated_annual"` that `value_held` subtracts. Move sets `variant_name` to Monthly (so `P('pause_max_days')` becomes 90) and sets `plan_switched_date`/the new plan-switch charge that `fresh_period_reduction` reads. Settle creates the `renewal_retry` charge whose `billing_period_start` equals `current_period_start`, which `period_kept_fee`/`period_retry_captures` read.
- `condition` vs sentence:
  - move <- term: the condition says "whose source_event_id is the **plan-switch** charge that opened the current annual term"; the sentence says "the charge that opened the annual term". The condition is narrower than the sentence (observation O3; it is the same row wherever the term was opened by a plan switch).
  - move <- carried: the condition matches the sentence.
  - pause <- move: the condition matches.
  - upgrade <- settlement: the condition adds "memberships.status is active", which the sentence does not state (the sentence says "shows a captured retry fee and the membership no longer carries a past-due date"). It is slightly strengthened; the settle tool sets both together. Observation O4.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test per edge:

1. move <- term: "The move-to-monthly charge is fixed only after the charge that opened the annual term carries a prorated-annual refund booked against it." Its ordering connective is "only after". What it waits on is record-visible: a refund row whose source is the term-opening charge. It names no tool, id or snake_case token. Its strength matches the condition except for the narrowing in O3. Exactly one write brings it about: the term policy books against "the fee charge ... whose billing period start is the first day of the current term", while the carried policy books against the earlier charge, so the reader resolves this edge to the term policy. The reader's path is the sentence, then the term policy's first overwrite (which replaces base's `prorated_annual` clause), then its own rule. Single reading.
2. move <- carried: "The move-to-monthly charge is not fixed until the fee charge captured most recently before the annual term began carries its own refund of the value it carried into the term." Its connective is "not until". It waits on a record-visible state: a refund row on the charge captured most recently before the term's first day. It names nothing forbidden. It matches the carried rule's own object ("The earlier charge is the fee charge captured most recently before the term's first day"). One write brings it about. Single reading. **But** that write is available only to a term "that was opened by a plan switch" (carried rule, first sentence), while the blocked policy's scope is every Cartwise+ Annual member asking for a pause. See F1.
3. pause <- move: "The pause length for a member who asked for a pause while on Cartwise+ Annual is not fixed until the membership shows Cartwise+ Monthly as its plan, with a plan-switch charge captured on the day its current period began." Its connective is "not until". Plan name, plan-switch charge and period start are all record-visible. One write brings it about: the upgrade tool's docstring excludes Monthly, and the upgrade policy is monthly -> Annual. Single reading.
4. upgrade <- settlement: "The upgrade charge on a past-due membership is fixed only after the period being billed shows a captured retry fee and the membership no longer carries a past-due date." Its connective is "only after". It waits on a record-visible state: a `renewal_retry` charge for the current period and an empty `past_due_since`. Only the settle tool writes `renewal_retry` or clears `past_due_since`. Single reading.

- No rule restates another policy's prerequisite sentence. The term and carried rules say nothing about the move, and the settlement rule says nothing about the upgrade. No rule names a tool or a policy id.
- No undeclared cross-problem order was found in any extended rule. The base sentences that state an order (membership_agg_multi_holding "must first be removed"; plan_switch "requires that plan's eligibility proof to be accepted first") ground no edge in this difficulty.

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry (conclusions only; consequences are demonstrated in the task files):

- **term_charge_refund vs membership_evt_fee_refund**
  - "A refund always targets one captured fee charge ..." is followed.
  - "A full refund is available only when ... within the unused-refund window" is declared superseded.
  - "The window is counted ..." is moot after that supersession.
  - "Where refund_requires_no_benefit_use is true, a full refund additionally requires membership_msr_benefit_uses_since_charge to be 0; a refund_type of full_unused refunds the whole charge." is **not declared**, and the term rule computes a different amount for the same charge. See F2.
  - "Outside the window, or once a benefit has been used, an annual plan ... receives a prorated_annual refund ..." is declared superseded.
  - "Monthly plans receive no refund outside the full-refund rule" does not apply (annual term).
  - The duplicate_charge sentence does not apply.
  - "Each fee charge can be refunded at most once" is inherited.
  - "Refunds go to refund_destination" is followed (original payment method).
  - "A refund of a first period or renewal charge ends the membership: after a full_unused or prorated_annual refund the membership is canceled ..." is **not declared**. It does not fire when the opening charge is a plan-switch charge. When the term was opened by a first-period or renewal charge, it cancels the membership on the member's confirmation, while the confirm tool "does not change" status. See F1 and O2.
- **carried_value_refund vs membership_evt_fee_refund**
  - The window sentence and the "ends the membership" sentence are declared superseded.
  - The full_unused sentence is **not declared** (F2).
  - "Monthly plans receive no refund outside the full-refund rule" is not declared. The charge the carried refund targets can be a monthly-plan charge while the membership now holds an annual plan. The sentence speaks of the plan held, so it has no second reading on the membership's current plan. Observation O5.
  - The `prorated_annual` sentence is superseded by the term policy's declaration. After that merge no base clause prices a refund of the earlier charge.
- **move_to_monthly_charge vs membership_evt_plan_switch**
  - Allowed targets and "only while it is active" are inherited (Annual -> Monthly is allowed).
  - The upgrade clause does not apply.
  - The downgrade "next renewal date with no proration" clause and the one-switch-per-period clause are declared superseded.
  - The proof and priority-upgrade sentences do not apply.
  - membership_evt_fee_billing's "Every paid period is billed once, on its first day, at the plan's period_fee_usd; the fee_type records whether it is ... a plan_switch charge" is not in `base_policy_refs` and not declared, and the move charge is a computed amount. The base charter itself already prices plan_switch charges away from the list fee (plan_switch's upgrade proration), and the downgrade clause that fixed the amount ("no proration") is the one declared superseded. Observation O1.
- **pause_length vs membership_evt_pause**
  - "Only plans with pause_allowed true ... only from active" is inherited.
  - The min/max length sentence is declared superseded.
  - The cutoff, the rolling-365 count, the no-fee/no-benefit sentence and the resume sentence are inherited and followed.
- **past_due_settlement vs failed_payment / fee_billing**
  - The fee_billing "billed once ... at the plan's period_fee_usd" clause is declared superseded.
  - failed_payment: retries, benefits during past_due, "A capture during past_due reinstates ... the period dates do not move", grace and the unpaid reason are inherited and followed.
  - "Price is the one in force for the plan on the charge date; no tier pays another tier's fee" is about which price list applies and does not conflict.
- **annual_upgrade_charge vs membership_evt_plan_switch**
  - The proration clause is declared superseded.
  - Allowed targets (Student/Assist/Monthly -> Annual all listed), "only while it is active" and the one-switch-per-period clause are inherited.
  - Timing "takes effect immediately" is followed.
  - fee_billing: same as O1.

No anonymous intermediate factor, 0/1 multiplier or dropped base branch was found. No author note calls base's output a "wrong value".

### factor_ladders

Per policy (label as declared -> auditor's assessment):

- **term_charge_refund** (4 factors):
  - unused_share_method, method: months-with-month-in-progress / calendar days / months not yet started. The calendar-day tier is a genuine change of algorithm. Multi-source (enrolment date and order waivers). Reads the order difficulty.
  - opening_retention_rate, parameter: 1.0 / 0.95 / 0.9. Multi-source (term age and the type of the opening charge).
  - waiver_offset_window, method: the tiers change only the window length (1 / 2 / 3 months) of the same sum, so it is closer to a parameter. Observation O7; the policy still keeps one genuine method.
  - waiver_offset_rate, parameter: 0.5 / 0.75 / 1.0. Reads rewards.
  - Counts: 2 parameter + 1 genuine method (3 + 1 if O7 is applied). Every ladder has 3 distinct outcomes, every tier is stated in the rule, and every fall-through equals the baseline.
- **carried_value_refund** (4 factors):
  - carried_share_method, method: whole / months-not-started / calendar days. Genuine. Multi-source (switch age and carried value).
  - carried_retention_rate, parameter: 1.0 / 0.95 / 0.9. Reads rewards.
  - carried_handling_amount, parameter: 0 / 0.25 / 0.5.
  - carried_waiver_share, parameter: 0.1 / 0.25 / 0.5.
  - 3 parameter + 1 method. Distinct outcomes, stated in the rule, fall-through = baseline.
- **move_to_monthly_charge** (5 factors):
  - term_run_value_method, method: whole weeks / months started / calendar days. Genuine as algorithms, but **tier 2 ("term opened by a first-period or renewal charge") is unreachable and tier 1's part "term opened by a plan-switch charge" holds of every member whose move charge can be fixed** (F1). After the strike only two real tiers remain.
  - move_credit_share, parameter: 1.0 / 0.75 / 0.5.
  - move_rate, parameter: 0.9 / 0.95 / 1.0. Reads rewards.
  - welcome_back_amount, parameter: 1.0 / 0.5 / 0.
  - activity_credit, parameter: 0.5 / 0.25 / 0. Reads order.
  - Declared: 4 parameter + 1 method. **Surviving: 4 parameter + 0 method, so the policy fails the "at least 1 method" bound** (F3).
- **pause_length** (6 factors):
  - tenure_extension, parameter: 28 / 14 / 0. Multi-source (captures and enrolment).
  - rewards_extension, parameter: 10 / 5 / 0. Reads rewards.
  - spending_extension, parameter: 7 / 3 / 0. Reads order.
  - earlier_pause_reduction, method, **mislabelled**: whole booked length / half rounded down / none is floor(k·P) with k ∈ {1, ½, 0} over the same quantity P = pause days logged in 12 months.
  - fresh_period_reduction, method, **mislabelled**: floor(k·D) with k ∈ {1, ½, 0}, D = days from today to the day before renewal.
  - notice_extension, parameter: 7 / 3 / 0.
  - Declared: 4 parameter + 2 method. **Surviving: 6 parameter + 0 method, so the policy fails the "at least 1 method" bound** (F4).
- **past_due_settlement** (4 factors):
  - settled_share_method, method: days ahead / period less whole weeks past due / whole fee. Genuine. Multi-source (plan parameter and past-due date).
  - courtesy_rate, parameter: 0.9 / 0.95 / 1.0. Multi-source (12-month retry count and lifetime captures).
  - partner_credit, parameter: 0.5 / 0.25 / 0. Reads rewards.
  - early_settlement_credit, parameter: 0.3 / 0.15 / 0.
  - 3 parameter + 1 method.
- **annual_upgrade_charge** (6 factors):
  - upgrade_credit_method, method: whole fee / whole weeks ahead / days ahead. **Tier 2 ("the plan's order benefits keep applying while past due") is unreachable, and tier 1's part "the plan's order benefits stop while past due" holds of every member who reaches this write.** The rule's scope is "A member on a monthly plan", and every monthly plan has `benefits_during_past_due: false` (membership.yaml variants: Assist line 164, Student line 220, Monthly line 277). Only two real tiers remain (F5).
  - graduation_rate, parameter: 0.8 / 0.9 / 1.0. Multi-source (plan and captures).
  - rewards_offer, parameter: 10 / 5 / 0. Reads rewards.
  - shopper_offer, parameter: 3 / 1.5 / 0. Reads order.
  - reverification_offer, parameter: 2 / 1 / 0. Multi-source (plan and proof date).
  - anniversary_offer, parameter: 1 / 0.5 / 0.
  - Declared: 5 parameter + 1 method. **Surviving: 5 parameter + 0 method, so the policy fails the "at least 1 method" bound** (F5).

Cross-difficulty categories read: order (the order_item_refunds_fees_and_tips difficulty) and rewards. The rewards category is claimed by no difficulty in `blueprint.yaml` (observation O8). Every tree still has an order-reading factor: tree A in term, move and pause; tree B in upgrade.

Business realism: no two tiers of any ladder share an outcome. Rewards-tier, tenure, spend, notice and anniversary conditions are ones a membership business plausibly weighs. No fall-through was found to be a straw-man treatment.

### findings

- **F1 — SOURCE-POLICY RED (charter-global).**
  - Symptom: the move policy orders a move for every Annual member who asks for a pause, but its second prerequisite can be resolved only for terms opened by a plan switch.
  - Evidence: the move rule says "A member on Cartwise+ Annual who asks for a pause is moved to Cartwise+ Monthly on the day of the request" and "The move-to-monthly charge is not fixed until the fee charge captured most recently before the annual term began carries its own refund of the value it carried into the term". The carried rule, the only policy that books that refund, says "When an annual term that was opened by a plan switch ends early, the value an earlier fee charge carried into the term is refunded ...", and its tool requires "a positive number".
  - Same situation, two conclusions: take an Annual member whose term was opened by a renewal charge and who asks for a pause. Passage 1 says they are moved today. Passages 2 and 3 say the charge is never fixed. In addition, the term refund on a renewal/first-period opening charge falls under the undeclared base sentence "A refund of a first period or renewal charge ends the membership: after a full_unused or prorated_annual refund the membership is canceled ...". The membership would be canceled, while plan_switch requires "only while it is active".
  - Consequence for the factor structure: see F3.
  - Bears on: task 0, via F3 only. Task 0's term was opened by a plan switch, so the deadlock itself does not arise in its world.
- **F2 — SOURCE-POLICY RED (charter-global).**
  - Symptom: the base full_unused sentence is left standing under both refund policies, and it prices the same refund differently.
  - Evidence: base membership_evt_fee_refund says "Where refund_requires_no_benefit_use is true, a full refund additionally requires membership_msr_benefit_uses_since_charge to be 0; a refund_type of full_unused refunds the whole charge." Neither refund policy names this sentence in `overwrite`. Both replace only its window gate, the term policy with "whenever the early end is asked for, however long ago that charge was captured".
  - Same situation, two conclusions: an annual term opened 5 days ago with no benefit used since. Base gives the whole charge (full_unused). The term rule gives charge × unused share × opening rate − offset. The same holds for the carried refund, for an earlier charge within its plan's window with no benefit use.
  - Bears on: no task in this bundle. Task 0's opening charge (2026-07-10) and earlier charge (2026-06-27) both have member fee waivers after them (2026-08-02, 08-29, 09-14), so full_unused is unavailable there. Task 1 has no refund.
- **F3 — SOURCE-FACTOR (structure) for move_to_monthly_charge.** term_run_value_method has only two reachable tiers (F1), which leaves 0 method factors. The demonstration is in task 0's `factor_weight`.
- **F4 — SOURCE-FACTOR (structure) for pause_length.** Both "method" factors are rate substitutions (floor(k·X), k ∈ {1, ½, 0}), which leaves 0 method factors. The demonstration is in task 0's `factor_weight`.
- **F5 — SOURCE-FACTOR (structure) for annual_upgrade_charge.** upgrade_credit_method tier 2 is unreachable on every monthly plan, which leaves 0 method factors. The demonstration is in task 1's `factor_weight`.
- **O1 (observation):** fee_billing "at the plan's period_fee_usd" vs the computed plan-switch charges of move and upgrade. Neither overwrite names it, but base plan_switch already departs from it, so no new second answer is demonstrated.
- **O2 (observation):** term_charge_refund leaves base "A refund of a first period or renewal charge ends the membership ..." undeclared, while its tool says status "not changed". This is inert when the opening charge is a plan-switch charge.
- **O3 (observation):** the condition of edge move <- term is narrower than its sentence ("plan-switch charge" vs "the charge that opened the annual term").
- **O4 (observation):** the condition of edge upgrade <- settlement adds "status is active", which the sentence does not state.
- **O5 (observation):** carried_value_refund leaves "Monthly plans receive no refund outside the full-refund rule" undeclared, while the charge it refunds can be a monthly-plan charge.
- **O6 (observation):** after-the-fact wording ("afterwards", "then") in two tool docstrings. Not a sequence statement.
- **O7 (observation):** waiver_offset_window is labelled method but only varies a window length. No count consequence, because unused_share_method remains a genuine method.
- **O8 (observation):** the factors labelled `cross_difficulty: rewards` read a product that no difficulty claims. The order-reading factors satisfy the cross-difficulty bound.

## closing_checklist

Written after both reveals (2026-09-25T00:13Z). It is kept below the pre-reveal charter-global section, which was not edited after the reveal.

The closing checklist cannot be signed. Not every task PASSes:

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | SOURCE-FACTOR RED | PASS | RED |
| 1 | PASS | PASS | SOURCE-FACTOR RED | PASS | RED |

Item status:
- Per-task files: 0.md, 1.md and this file sit side by side. Revision 1; no older revision exists.
- Extended-policy coverage: complete. Task 0 covers {term, carried, move, pause} and task 1 covers {settlement, upgrade}. The scopes are pairwise disjoint over whole trees (checked against `charter_scope` after the reveal).
- Task tools: each is claimed once and has an independent uuid8 (§ action_binding_and_uuids).
- Trees:
  - Task 0: 3 prerequisites, 3 value_input edges, 1 user write.
  - Task 1: 1 prerequisite, 1 value_input edge, 1 user write.
  - The difficulty-wide graph is acyclic.
- Factors: fails.
  - move_to_monthly_charge: 0 surviving method factors (F1/F3).
  - pause_length: 0 honest method factors (F4).
  - annual_upgrade_charge: 0 surviving method factors (F5).
  - Task 0's order seed contradicts the order charter (0.md finding 3).
- Charter-global SOURCE-POLICY findings F1 and F2 stand. F1 bears on task 0 only through F3; F2 bears on no task of this bundle.
- Gate re-run on the final form: not performed by this auditor (gates are supplied with the brief). The artifacts were not changed during this audit (charter and tool hashes unchanged from the freeze).

## revision_2

### charter_global_frozen (revision 2)
- Auditor: the same independent auditor, round 2 re-audit. Freeze time: 2026-09-25T04:04Z. This section was written before any round-2 GT was revealed; the revision-1 text above is left untouched.
- Hashes have changed since revision 1, so the whole charter-global section is re-derived rather than carried forward:
  - `membership.extended.yaml` `5c86766d8663c44d7ca8b43a58f564217b6b99fd12f5377a05a6fd8bb0d77260` (r1: `b5a6e9cc…`)
  - `task_tools.py` `8e3ae6d4cd6488d06cd184627bf0bfe9773b57aabc0711a3de1a776f2bf96ce2` (r1: `291b2441…`)
- Base section: lines 1–1269 are still byte-identical to `blueprint/products/membership.yaml` (`diff` empty).
- Read: the full extended section (lines 1271–3205), the full `task_tools.py`, and the two round-2 masked views (sha256 `a6260c7c…` and `337270e8…`; both recomputed and matching the brief).
- Masked and not read before the freeze: every masked task field, the worklog, and the reworker's notes. Only the brief's item-id claims were seen.
- contamination_disclosure (round 2): I carry revision-1 knowledge. That includes the round-1 GT values (69.91 / 4.86 / 2.25 / 97; 2.89 / 66.81) and my own round-1 counterfactual (68.40 / 4.56 / 0.44 on a charter-consistent order ledger). No round-2 GT field was seen before this freeze. The round-2 values derived below come from the new charter and the new views.
- Entry conditions: the brief supplies the gate snapshot (all rc=0; traceability deferred) and the view hashes. Complete.

### policy_conflict_scan (revision 2)

The same six policies, tools, owners and edges as revision 1. What changed:

| Policy | Change | Effect |
| --- | --- | --- |
| term_charge_refund | Scope narrowed to "an annual term that a plan switch from a monthly plan opened"; adds "An annual term opened by a first-period or renewal charge is not ended early under this rule" | |
| term_charge_refund | Opening-rate ladder now keys on "no retry capture / at least one retry capture in the last twelve months" (was: how the term was opened) | |
| term_charge_refund | New overwrite of the full_unused sentence | |
| term_charge_refund | `waiver_offset_window` relabelled parameter | |
| carried_value_refund | New overwrites of the full_unused sentence and of "Monthly plans receive no refund outside the full-refund rule" | |
| move_to_monthly_charge | Scope narrowed to a term "opened by a plan switch from a monthly plan"; adds "A member whose annual term was opened by a first-period or renewal charge is not moved under this rule" | |
| move_to_monthly_charge | fee_billing added to `base_policy_refs`, and its clause declared | |
| move_to_monthly_charge | `term_run_value_method` tiers now split on the switch age (< 3 / ≥ 3 whole months) | |
| move_to_monthly_charge | Edge move <- term condition reworded to "the fee charge whose billing_period_start equals memberships.current_period_start" | |
| pause_length | `earlier_pause_reduction` tier 2 is now "each of those pauses counts as a flat pause_min_days days …: the allowance is reduced by their number times pause_min_days" | New binding `earlier_pause_count` |
| pause_length | `fresh_period_reduction` relabelled parameter | |
| past_due_settlement | Unchanged | |
| annual_upgrade_charge | fee_billing declared | |
| annual_upgrade_charge | `upgrade_credit_method` tiers now split on the retry capture being below / at or above the plan's period_fee_usd | |
| annual_upgrade_charge | Edge condition drops "status is active" | |
| task_tools.py | Docstrings of confirm/refund reworded ("which carries the refund reference the member can quote"; "and the refund shows among the membership's entries") | Bodies unchanged: still unconditional writes; uuid8s unchanged |

Overlaps, time anchors, cross-category reads, terminal states and the tree partition ({pause, move, term, carried} / {upgrade, settlement}) are as in revision 1. No new conflict.

### rule_compute_equivalence (revision 2)

The mechanical check was re-run on the new file: every `compute_basis` value, `policy_source`, `baseline.rule` sentence and `replaced_by` is verbatim in its own rule; `decides` and `bindings` exist; bindings are disjoint; every ladder has three tiers. It found no failure.

Sweep back over the changed passages:
- term `opening_rate` ↔ "no retry capture in the last twelve months" (`term_retry_captures`, 12-month `renewal_retry` count).
- move `value_run` ↔ the switch-age tiers (`move_switch_age = MONTHS(plan_switched_date, NOW)`).
- pause `earlier_pause_reduction` ↔ the count × pause_min_days tier (`earlier_pause_count`, a 12-month count by `billing_period_start`).
- upgrade `credit_share` ↔ "captured as a retry for less than / the plan's period_fee_usd or more" (`period_kept_fee < P('period_fee_usd')`; this equals "the retry capture" wherever the period carries a single capture).

All present both ways. No quantity is invented and no empty promise remains.

### action_binding_and_uuids (revision 2)

- Unchanged: six tools, each claimed once. uuid8s `0b7355fe`, `822a3886`, `dc3bc730`, `b6aef13b`, `b438dc6f`, `10b03fa3`.
- No body checks state.
- Docstrings name no other tool and carry no sequence wording (the revision-1 "afterwards"/"then" are gone).

### prerequisite_graph (revision 2)

- Same four edges, all `value_input` / `state`, no `fallback_reason`. Gates exist. Each `resolved_by` is the depended-on `target_tool`. Acyclic.
- move <- term: the condition now names "the fee charge whose billing_period_start equals memberships.current_period_start (the charge that opened the current annual term)". This matches the sentence ("the charge that opened the annual term"); the r1 narrowing is gone.
- upgrade <- settlement: the condition is now "renewal_retry … billing_period_start equal to memberships.current_period_start … and memberships.past_due_since is empty". This matches the sentence.
- No authoring-viewpoint phrasing.

### prerequisite_sentences (revision 2)

- The four sentences are unchanged and pass the four-point test as in revision 1.
- Each state-form edge is still brought about by exactly one write of this difficulty.
- **The move's second edge is now resolvable for every member in the move's scope.** The move applies only when the current annual term was "opened by a plan switch from a monthly plan", and the carried rule books its refund for any "annual term that was opened by a plan switch". So a member the move reaches always has an "earlier charge" and a carried-value policy that covers it.
- Edge case (observation N-O2): the carried and term rules both floor at zero ("never below zero"), while both tools' docstrings ask for "a positive number". A member whose carried or term refund computes to 0.00 cannot meet the move's waiting state through the documented tool contract. No world in this bundle is near it (task 0: 68.40 and 4.56).

### override_declarations (revision 2)

- **term_charge_refund.**
  - Declared: the window, prorated_annual and full_unused sentences.
  - "A refund of a first period or renewal charge ends the membership …" is still undeclared. It is now inert: the term rule applies only to terms opened by a plan-switch charge, and that is the charge it refunds.
  - Other sentences are followed or inherited, as in revision 1.
- **carried_value_refund.** Declared: the window, "ends the membership", full_unused and "Monthly plans receive no refund outside the full-refund rule". The last is the r1-O5 fix.
- **move_to_monthly_charge.** Declared: downgrade timing, one switch per period, and fee_billing "billed … at the plan's period_fee_usd" (the r1-O1 fix).
- **pause_length.** Unchanged (min/max declared).
- **past_due_settlement.** Unchanged (fee_billing declared).
- **annual_upgrade_charge.** Declared: proration and fee_billing.
- New observation N-O1: the term policy's second overwrite supersedes base "Outside the window, or once a benefit has been used, an annual plan … receives a prorated_annual refund …", and its replacement now reaches only switch-opened terms ("An annual term opened by a first-period or renewal charge is not ended early under this rule"). Whether that supersession is scoped to the term policy's situation (the natural reading, invited by "under this rule") or applied globally decides whether a renewal-opened annual member keeps base's prorated refund. No task world involves a renewal-opened annual term, so no consequence is demonstrable.

### factor_ladders (revision 2)

- **term_charge_refund** (4 factors; 3 parameter + 1 method):
  - unused_share_method (method; calendar-day vs month methods, genuine).
  - opening_retention_rate (parameter; 1.0 / 0.95 / 0.9). Every tier is reachable within the scope: term age and retry record both vary over switch-opened terms.
  - waiver_offset_window (now parameter, which is honest).
  - waiver_offset_rate (parameter).
  - Multi-source: unused_share_method, opening_retention_rate. Cross-difficulty: order.
- **carried_value_refund** (4; 3 + 1): unchanged.
- **move_to_monthly_charge** (5; 4 parameter + 1 method):
  - term_run_value_method: whole weeks / months started / calendar days. Genuine methods.
  - All three tiers are reachable within the narrowed scope: switch age runs 0–11 whole months across a switch-opened term, and enrolment can be under or over 18 months.
  - No tier condition restates the scope. The r1 defect (a tier keyed on "opened by first-period or renewal") is gone. **The method bound is met.**
- **pause_length** (6; 5 parameter + 1 method):
  - earlier_pause_reduction is now: the sum of booked days / (number of pauses) × pause_min_days / no reduction. Tier 2 counts pauses, not days, so it is a different measure and genuinely a method. It is reachable: a single logged pause of pause_min_days–29 days totals 1–29.
  - fresh_period_reduction is now labelled parameter: D, ⌊D/2⌋ or 0, which is honest.
  - **The method bound is met.**
- **past_due_settlement** (4; 3 + 1): unchanged.
- **annual_upgrade_charge** (6; 5 parameter + 1 method):
  - upgrade_credit_method: whole fee / whole weeks ahead / days ahead.
  - Tier 1 (a retry captured below the fee) is reached through the settlement.
  - Tier 2 (a retry captured at or above the fee) is reached through base's automatic retry, which "captures the outstanding period fee" at the period fee ("A retry or an updated payment card captures the outstanding period fee").
  - Tier 3 is any period not captured as a retry.
  - No condition holds of every member in scope. **The method bound is met.**

Every ladder has three distinct outcomes, every tier is stated in its rule, and every fall-through equals the baseline. Cross-difficulty coverage per tree is unchanged: order is read in tree A and tree B. O8 remains: rewards is claimed by no difficulty.

### findings (revision 2, charter-global)

| r1 item | r2 status | Evidence |
| --- | --- | --- |
| F1 SOURCE-POLICY (move scope vs unresolvable second edge) | **closed** | The move now reaches only switch-opened terms, and renewal-opened members are "not moved under this rule". Every member in scope has an earlier charge the carried policy covers. |
| F2 SOURCE-POLICY (undeclared full_unused) | **closed** | Declared in both term and carried overwrites, with replacements stated in both rules. |
| F3 (move method factor) | **closed at structure** | Weight is re-checked in 0.md r2. |
| F4 (pause mislabel) | **closed at structure** | Weight is re-checked in 0.md r2. |
| F5 (upgrade method factor) | **closed at structure** | Weight is re-checked in 1.md r2. |
| O1 fee_billing | **closed** (declared by move and upgrade) | |
| O2 term vs "ends the membership" | **closed** | Inert under the narrowed scope. |
| O3 edge-condition narrowing | **closed** | |
| O4 extra "status active" | **closed** | |
| O5 "Monthly plans receive no refund" | **closed** (declared) | |
| O6 docstring wording | **closed** | |
| O7 window-length label | **closed** (relabelled parameter) | |
| O8 rewards not a difficulty | **open** (left, as the reworker states) | Observation only. |

New in revision 2:
- **N-O1 (observation):** the scope of the prorated_annual supersession for renewal-opened annual terms. Not demonstrable in either world.
- **N-O2 (observation):** a zero-amount term or carried refund vs the docstrings' "positive number". Not demonstrable in either world. The same structure existed in r1 and was not reported there.

No new SOURCE-POLICY finding.

### closing_checklist (revision 2)
Written after both r2 reveals (2026-09-25T04:07Z). It sits below the r2 charter-global section, which was not edited after the reveal.

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

Checklist:
- **Files:** 0.md, 1.md and `_difficulty.md` sit together. Revision 1 is preserved verbatim, and each file ends in a revision_2 comparison carrying PASS.
- **Coverage:** all six extended policies are covered. Task 0 claims {term, carried, move, pause} and task 1 claims {settlement, upgrade}. Pairwise disjoint over whole trees.
- **Tools:** six task tools, each claimed once. uuid8s independent and unchanged.
- **Trees:**
  - Task 0: 3 prerequisites, 3 value_input edges, 1 user write.
  - Task 1: 1 prerequisite, 1 value_input edge, 1 user write.
  - The difficulty-wide graph is acyclic.
- **Factors:** every computation declares a self-sufficient baseline and 4–6 factors with at least 2 parameter and 1 method:
  - term 3 + 1
  - carried 3 + 1
  - move 4 + 1
  - pause 5 + 1
  - settlement 3 + 1
  - upgrade 5 + 1

  Per task, multi-source and order cross-difficulty factors are present. Every ladder has three reachable, distinct tiers. Every factor bears weight on its world (0.md / 1.md r2 factor_weight). Each baseline gives a definite fall-back that differs from gold: 44.66, 0.00, 7.27, 90, 4.99 and 96.78.
- **Gate re-run on the final form:** performed by the orchestrator per the brief (all rc=0; traceability deferred). Not re-run by this auditor. The artifact hashes were re-checked as unchanged at the close.
- **Open observations (not grounds for rework):**
  - O8: rewards is not a difficulty.
  - N-O1: the scope of the prorated_annual supersession for renewal-opened terms.
  - N-O2: a zero-amount refund vs the "positive number" docstring.
  - T0-O1 and T0-O3.
  - T0r2-O1: thin 0.44/0.00 edge weight.
  - T0r2-O2: GT counterfactuals use float rounding.

The difficulty passes the source-layer audit at revision 2.

## revision_3

### charter_global_frozen (revision 3)
- Auditor: the same independent auditor, round 3 re-audit. Freeze time: 2026-09-25T04:59Z, before any round-3 task file was opened. Revisions 1 and 2 above are untouched.
- Hashes:
  - `membership.extended.yaml` `5c86766d8663c44d7ca8b43a58f564217b6b99fd12f5377a05a6fd8bb0d77260`: **unchanged since r2**.
  - Views `a6260c7c…` / `337270e8…` (under views_r3): **identical to r2**. Recomputed; they match the brief.
  - `task_tools.py` `5dfeca55deacac76dc66e004bc76661fc73d0a3a64bcf9efe25e048a4f4b09b4`: **changed**.
- Carry-forward rule: every charter-global conclusion that rests only on the charter is carried forward from § revision_2 by reference: policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations and factor_ladders. The grounds are the unchanged charter hash. Everything that rests on the tool module is re-derived below.
- Validator item read: `audits/merge_acceptance/validate_scenario.round1.txt` line 2 says: "ERROR: tasks/membership_charges_and_cancellations/task_tools.py: forbidden 'from datetime' (real clock) — use ctx.now() for time and ctx.create for ids". My revision-1 and revision-2 tool checks did not flag this import. It is a scenario-validator rule outside the four relationships, and it is recorded here as the item under verification.
- contamination_disclosure: I carry r1 and r2 GT for both tasks. Because world and charter are unchanged, the r2 per-task derivations stand as frozen; nothing new is derived from GT.

### action_binding_and_uuids (revision 3, re-derived)
- **Imports** (AST): only `from erlbench import ToolContext, tool`. No `datetime`, `calendar`, `time`, `random` or `uuid` import. The token "calendar" appears only in prose ("calendar days"; lines 32, 169, 177). **The validator item is closed.**
- **What changed in the module:** the helper `_Util.add_months` now takes month lengths from a new `_Util.month_length` (proleptic Gregorian rule) instead of `calendar.monthrange`. The new `_Util.add_days` (days-from-civil / civil-from-days) replaces `date(...) + timedelta(days=days - 1)` in `book_membership_pause_b6aef13b`. Everything else is as I read it in r1/r2: the six tool names, uuid8s (`0b7355fe`, `822a3886`, `dc3bc730`, `b6aef13b`, `b438dc6f`, `10b03fa3`), owners, signatures, docstrings, ids from `ctx.make_id`, the `ctx.create` / `ctx.update` fields and the return dictionaries.
- **Equivalence tested by the auditor** (script in the report's tmp folder, deleted afterwards). The old arithmetic was re-implemented exactly as read in r1 (`calendar.monthrange` clamp; `date + timedelta(days-1)`) and compared with the new helpers:
  - `add_months`: every day from 1600-01-01 to 2500-12-31, with offsets −25, −13, −12, −1, 0, 1, 2, 11, 12, 13, 24, 48.
  - `add_days` vs the old pause end: every day of that span, with n ∈ {−400, −366, −365, −31, −1, 0, 1, 2, 14, 28, 29, 30, 31, 59, 60, 90, 97, 127, 365, 366, 1461, 146097}. This covers pause_days 0 and negative values, as the old code allowed.
  - Result: 11,188,856 comparisons, **0 mismatches**.
  - `month_length(y, m)` equals `calendar.monthrange(y, m)[1]` for every month of years 1–9999, which covers leap years including the 1900/2000 century rules.
  - Spot checks: 2024-02-29 +12 months → 2025-02-28; 2026-01-31 +1 month → 2026-02-28; 2028-02-28 +1 day → 2028-02-29; 2000-03-01 −1 day → 2000-02-29; 1900-03-01 −1 day → 1900-02-28.
  - The only behavioural difference: the old code raised on a non-existent calendar date or a year outside 1–9999, and the new code does not. Neither can arise here, because the dates come from `ctx.now()` and seeded period ends.
- **Tool-layer independence:** still no body checks status, timing or prior state. Both new helpers are pure date functions.
- **Docstrings:** unchanged. They name no other tool and carry no sequence wording.

### findings (revision 3, charter-global)
- Validator item (`forbidden 'from datetime'`): **closed**.
- No other charter-global item moved. Everything from revision 2 carries forward: F1–F5 and O1–O7 closed, O8, N-O1 and N-O2 open as observations.
- No new finding.

### closing_checklist (revision 3)
Written after the r3 reveals (2026-09-25T04:59Z).

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

- **Validator item** (`forbidden 'from datetime'` in task_tools.py): closed. The module imports only `erlbench`. The new date helpers match the old arithmetic across 11,188,856 comparisons with 0 mismatches, covering month lengths, leap and century years, negative offsets and month-end clamping.
- **What moved in round 3:**
  - Only the internals of `task_tools.py` (the date helpers).
  - The charter and both views are hash-identical to r2.
  - Both task files were rewritten on disk. Their initial_state, frozen_time and user_scenario equal the views, and their GT fields equal r2.
  - Tool names, uuid8s, owners, signatures, docstrings, DB writes and receipts are unchanged for every input these tasks and policies produce.
- The rest of the checklist carries forward from § revision_2 / closing_checklist unchanged. That includes the open observations O8, N-O1, N-O2, T0-O1, T0-O3, T0r2-O1 and T0r2-O2.
- Gates: re-run by the orchestrator (all 7 rc=0; traceability deferred), not by this auditor. The artifact hashes were re-checked at the close.

The difficulty passes the source-layer audit at revision 3.
