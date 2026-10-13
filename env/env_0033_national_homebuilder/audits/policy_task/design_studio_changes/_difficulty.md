# Policy-task audit — design_studio_changes / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent subagent; not the author of the artifacts).
- Freeze time: 2026-10-04T23:36Z, before any task's GT was read. Nothing in this section is derived from a revealed GT.
- Shared inputs frozen:
  - `env/env_0033_national_homebuilder/tasks/design_studio_changes/design.extended.yaml` sha256 `215ae98ba97f21868f816904fc19cd3ecee618f2386c219f77ec259ff7660a38`
  - `env/env_0033_national_homebuilder/tasks/design_studio_changes/task_tools.py` sha256 `8b55ba8b0da0bc3ef341b5236bc313a0bda9f09b9b9c2e5559bf21a9dced3671`
  - The hashes match the orchestrator's MANIFEST.
- Also read: `blueprint/blueprint.yaml` (design_studio_changes summary), `blueprint/products/design.yaml` (base charter), `blueprint/products/{purchase,homesite,lock}.yaml` (only variant names, parameters and lifecycle states, for cross-category reads), `blueprint/db_schema.json` (enums), `blueprint/share_tools.py` (finders, verify, transfer). I also read the DSL primitive implementations in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 224-430) to learn the semantics of LATEST/COUNT/within_months/DAYS/RND/CFIELD/CPARAM. That file reads no task data.
- Permitted per task: `task_id`, `frozen_time`, `user_scenario`, `initial_state` (the masked views `audits/_views/policy_task/design_studio_changes/{0,1}.view.json`, with sha256 verified against MANIFEST).
- Masked until all derivations are frozen: `evaluation_criteria`, `computations`, `db_closure*`, `design_rationale`, `prerequisite_closure`, `solvability_contract`, `charter_scope`, `required_documents`, and `worklog.md`.
- Gate snapshot (supplied by the orchestrator; I cite it and did not re-run it): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. TRACEABILITY NOT OK is expected before the KB is rendered. The entry conditions are complete.

Base-copy check: `diff <(head -670 design.extended.yaml) blueprint/products/design.yaml` finds no difference apart from one trailing blank line. The base section is a verbatim copy.

### policy_conflict_scan

The charter has seven extended policies, each with its own `(target_tool, computes)`:

| policy | subject | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| design_ext_error_goodwill_credit | design_credit_granted (builder_goodwill) | grant_goodwill_credit_33ff7b41 (agent) | credit_amount | [] |
| design_ext_studio_consult_fee | design_option_added (design_consult_fee) | book_studio_consult_fee_3108e630 (agent) | fee_amount | [] |
| design_ext_change_order_fee | design_change_order_recorded | record_change_order_fee_50efc86e (agent) | fee_amount | [] |
| design_ext_option_deposit_due | design_deposit_paid | pay_option_deposit_3846be30 (user) | amount | CO fee, consult fee, goodwill (all value_input) |
| design_ext_returned_payment_fee | design_payment_returned → returned_payment_fee line | book_returned_payment_fee_69a7241d (agent) | fee_amount | [] |
| design_ext_removed_line_allowance | design_credit_granted (package_allowance, source_line_ref) | return_line_allowance_4e51d426 (agent) | credit_amount | [] |
| design_ext_line_reinstatement_price | design_option_added (portal) | reinstate_option_line_5b4fa2c4 (user) | price | allowance (value_input), returned fee (state_gate) |

- **Overlapping subjects.**
  - Goodwill and allowance-return both write `design_credit_granted`, but under different `credit_source` values (builder_goodwill vs package_allowance) and with different keys (change_order_number vs source_line_ref), so they cannot collide.
  - The consult fee, the returned payment fee and the reinstatement all write `design_option_added`, but under different categories (design_consult_fee / returned_payment_fee / the removed line's category). No two policies compute the same quantity on the same row.
- **Triggers and eligibility.** Every write sits on a file in status `structural_closed` in both worlds. The base gates `open_for_changes`, `change_order_state` and `credit_state` admit that status.
- **Time anchors.** These are policy-specific and do not overlap. One exception is **finding F2**: the reinstatement's quote escalation and the base `price_protection` gate anchor the staleness of the same quote differently.
- **Cross-category reads.** All of them are read-only:
  - purchase: stage, start/completion dates, financing, base price, reservation_id, the collection's contract_amendment_fee_usd, and the purchase ledger's returned payments;
  - lock: status;
  - homesite: variant.

  They are bounded to the purchase agreement the file serves, and no extended policy writes another category.
- **Scope exclusivity and completeness (derived from the `prerequisite` graph alone, since `charter_scope` is masked).**
  - Tree A is design_ext_option_deposit_due ← {change_order_fee, studio_consult_fee, error_goodwill_credit}.
  - Tree B is design_ext_line_reinstatement_price ← {removed_line_allowance, returned_payment_fee}.
  - The two trees are disjoint and together cover all seven extended policies. A two-task difficulty with one tree per task is therefore exclusive and complete.
- **Conflicts found.** F1 is an internal double-classification in the deposit rule. F2 is an undeclared override between the reinstatement policy and the base price-protection gate. Both are under findings.

### rule_compute_equivalence

I swept every binding against its `compute_basis` quote, and every rule sentence back to a binding. Results per policy:

- **design_ext_error_goodwill_credit.**
  - Every binding is quoted.
  - Every tier of the three-way error-amount, the channel/age percent, the financing points, the repeat multiple and the slip addition is in the rule and in compute.
  - The operation order is stated and implemented: cap+slip, then ×multiple, then −granted, then max 0; then min(rounded amount, room).
  - **Pass.**
- **design_ext_studio_consult_fee.**
  - All five ladders (channel, build stage, fee count, repeat visit, order relief) are in the rule and in compute, and the single rounding at the end is implemented.
  - Observation O2: `recent_order` is `LATEST(change_order_number)` over every `design_option_added`, including fee lines that carry no change order number. The rule speaks of "the change order whose option lines were added most recently". If a fee line were the latest-dated addition, compute would return None. This does not occur in either world.
  - **Pass.**
- **design_ext_change_order_fee.**
  - All six ladders are in the rule and in compute, and the operation order is stated and implemented: schedule × multiple × (1 − relief) + change-pct part + surcharge, rounded once.
  - Observation O1: the rule says "A change order written at the buyer's request is fee-bearing when … ; otherwise its fee is 0.00". The `result` binding tests only `buyer_orders_recorded >= free_change_orders` and never `change_order_reason`, so a builder_error change order on a file past its free orders would be charged by compute but not by the rule. Neither world records such a change order, so no consequence can be demonstrated.
- **design_ext_option_deposit_due.**
  - All bindings are quoted. However, `finish_group = finish_added - finish_removed - long_lead_added + long_lead_removed - credit_offset` excludes from the finish group *every* removal credit booked on cabinetry or countertop lines at foundation or framing. That includes the credit of a line that had been added before those stages. The rule does not state this exclusion; see **F1**.
  - Every other tier is two-way: structural % by stage, finish % by returns in the last 12 months, long-lead % by long-lead total, replaced-item share, credit offset, lender relief, ladder floor and cap guard.
- **design_ext_returned_payment_fee.**
  - All five ladders are two-way, and the operation order is stated and implemented: (basis × multiple + purchase addition + late addition) × cure, rounded once.
  - `within_months=12` uses the MONTHS(event, NOW) < 12 convention.
  - **Pass.**
- **design_ext_removed_line_allowance.**
  - The three-way return measure, the return share, the homesite points, the delay points and the cap at 100 are all two-way.
  - **Pass.**
- **design_ext_line_reinstatement_price.**
  - All five ladders and `credit_carried` are two-way, and the operation order is implemented: round(basis × (1+esc)) + surcharges − credit carried, floored at 0.
  - **Pass** on rule↔compute. The conflict with the base price-protection gate is a check-1 matter; see F2.
- **Rounding (observation O4).** `RND` is Python `round(float, 2)`, which rounds half-even on a binary float, while every rule says "rounded half up". Neither world produces a half-cent intermediate in any scored chain, so there is no consequence.

### action_binding_and_uuids

- **Bindings.** Every `(target_tool, computes)` pair is claimed by exactly one policy, as the table above shows.
- **Docstrings.**
  - No docstring names another tool or carries a sequencing word (before/after/first/then) about other actions.
  - No function body judges eligibility or prerequisites. The bodies only `find` a row to copy a date, code or category, then `create`/`update`. No branch refuses, errors or hints.
  - Each docstring admits one business reading.
- **uuid8s.** The seven are 50efc86e, 3108e630, 33ff7b41, 3846be30, 69a7241d, 4e51d426 and 5b4fa2c4.
  - They have no common prefix longer than one hex digit (three begin with "3": 3108e630, 33ff7b41, 3846be30).
  - None is sequential or a shared stem with a different tail.
  - Nothing suggests batch derivation.
- **Pass.**

### prerequisite_graph

- `prerequisite` is filled in on all seven policies (five are `[]`).
- Every `problem` points at an extended policy id in this file. None points at a base policy or at itself.
- The graph is acyclic: two roots, depth 1.
- Each `policy_source` is verbatim in its own policy's `rule`:
  - the deposit rule's last three sentences;
  - the reinstatement rule's last two sentences.
- Every edge is `form: state`, and no edge has a `fallback_reason`, which is consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge.
- `kind`/`gate`:
  - The value_input gates `order_fees`, `studio_fee_lines`, `credit_offset` and `credit_carried` are real bindings in the blocked policy's compute.
  - The state_gate `design_events.option_category` is a `<table>.<field>` path that the condition reads, which the instantiate reference allows.
- `condition` wording:
  - The returned-fee edge's condition "carrying its receipt number or dated on its return date" is a record-matching rule for "its returned payment fee line". It neither strengthens nor weakens the edge. Historical fee lines may lack `source_payment_ref`; in task 1 the earlier one carries it.
  - The consult edge's count-equality condition is equivalent to the per-appointment sentence.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.
- **Pass.**

### prerequisite_sentences

Each sentence was given the four-point test: an ordering connective, a record-visible state named in record words, no tool / id / snake_case token, and exact strength.

1. Deposit ← CO fee: "The option deposit due is fixed only after every change order number carried by an option line on the file has its change order entry on the design ledger." The connective is "only after", and the state is ledger-visible (change order numbers on option lines vs change order entries). Only `record_change_order_fee_50efc86e` writes `design_change_order_recorded`, so there is exactly one writer. The CO fee rule ("Every set of option lines added or removed under a change order number is recorded as one change order entry carrying its fee") leads the reader to the resolving write. One reading. **Pass.**
2. Deposit ← consult fee: "The option deposit due is not fixed until every selection appointment held beyond the package's included appointments has its consultation fee line on the file." The connective is "not until". Only `book_studio_consult_fee_3108e630` writes `design_consult_fee` lines, so there is exactly one writer. The consult rule ("A selection appointment held beyond the package's included appointments is billed with one consultation fee line") gives the resolving write. **Pass.**
3. Deposit ← goodwill: "The option deposit due is worked out only once every error-correcting change order on the file carries its builder goodwill credit memo." The connective is "only once". Only `grant_goodwill_credit_33ff7b41` writes builder_goodwill grants; the allowance return writes package_allowance. Exactly one writer. **Pass.**
4. Reinstatement ← allowance: "The reinstatement price is not fixed until the package allowance applied to the removed line stands returned on the file under its own credit memo." The connective is "not until", and the state is a package_allowance grant carrying the line number. Only `return_line_allowance_4e51d426` writes it. **Pass.**
5. Reinstatement ← returned fee: "A removed option line is reinstated only after every option deposit payment returned unpaid on the file carries its returned payment fee line." The connective is "only after". Only `book_returned_payment_fee_69a7241d` writes returned_payment_fee lines. **Pass.**

General checks across all five edges:
- None of the depended-on rules restates the blocked policy's sentence.
- No rule carries a second wording, a tool name or another policy id.
- No rule states a cross-problem order that grounds no declared edge.
- Some rules read other problems' records as value inputs: the CO fee's studio-error relief counts error change orders, and the reinstatement's re-selection fee counts buyer change orders. These read seeded records that no other write in the same tree changes, so they impose no order.
- No base rule sentence grounds an edge.

### override_declarations

I checked each extended policy sentence by sentence against its `base_policy_refs`.

- **design_ext_error_goodwill_credit** (design_credits, design_change_orders).
  - Superseded and declared: "A studio manager may grant builder goodwill credit up to goodwill_credit_cap_usd in total on one file;". The extended room (cap + slip) × multiple − granted can exceed the base total cap, and that is legal through this declaration.
  - All other design_credits sentences are followed (allowance once; order of application; never to fee lines; forfeiture; state gate), as are the design_change_orders sentences (builder_error change orders carry no fee and do not count).
  - No undeclared override.
- **design_ext_studio_consult_fee** (design_appointments, design_option_selection, design_package_eligibility, design_change_orders, design_option_deposits).
  - Declared: the "each further selection appointment carries extra_appointment_fee_usd" clause, and "After the first appointment, every addition or removal is written under a change order" (scoped by replaced_by to consult lines).
  - The electrical walk being free when included, the video permission and the first-appointment deadline are followed.
  - No undeclared override.
- **design_ext_change_order_fee** (design_change_orders, design_option_selection).
  - Declared: "each later one carries change_order_fee_usd while … in_selection and post_structural_change_order_fee_usd once … structural_closed."
  - The free-order count, max_change_orders, the builder_error waiver and the finalized cutoff are followed. The removal-credit sentences of design_option_selection are consistent with the change amount.
  - No undeclared override.
- **design_ext_option_deposit_due** (design_option_deposits, design_credits, design_change_orders, design_option_selection).
  - Declared: the group-percent clause and the ladder/cap clause.
  - "Fee lines … and change order fees are deposited in full" is followed.
  - The due-date, payment-method and card-cap sentences are inherited.
  - "A returned payment comes off the deposits held" is followed, because deposits held already net of returns.
  - No undeclared override. The internal conflict F1 is a separate matter.
- **design_ext_returned_payment_fee** (design_option_deposits).
  - Declared: "A returned payment comes off the deposits held and adds a returned_payment_fee line of returned_payment_fee_usd."
  - No other conflict.
- **design_ext_removed_line_allowance** (design_credits, design_option_selection), `overwrite: []`.
  - "The package allowance … is granted once" is reconciled by the extended rule's own sentence "the return restores allowance already granted and is not a second grant". The base is silent on allowance applied to a removed line.
  - No undeclared override.
- **design_ext_line_reinstatement_price** (design_option_selection, design_package_eligibility, design_appointments, design_change_orders, design_option_deposits).
  - Declared: "Options are added to the file at the price quoted at the appointment."
  - **Not declared: the price-protection sentence of design_option_selection.** It decides the same quantity (whether the quote is honored or escalated) from a different anchor. See **F2**.
  - The portal permission and cap, the state gate, the finish-line-after-structural-close permission and the included-level pricing are followed.
  - Observation O6: "Every set of changes after the first appointment is written as one numbered change order" is literally satisfied by writing the reinstated line under the removing change order, so there is no demonstrable conflict.

### factor_ladders

Per policy, factors are written as id (label; decides; multi-source?; cross_difficulty).

- **Goodwill (5 factors: 4 parameter, 1 method).**
  - error_amount_basis (method; error_amount; replacement vs removed price, two records; —)
  - entry_channel_and_age (parameter; goodwill_pct; channel + days between the add row and the CO row; —)
  - affiliated_financing_points (parameter; financing_points; purchase financing + lock status, distinct records; lock)
  - repeat_error_multiple (parameter; —)
  - build_slip_addition (parameter; two purchase dates; purchase)

  Every ladder has 3 tiers with pairwise-distinct outcomes, every tier is in the rule and in compute, and each fall-through equals the baseline. Labels are honest: the error-amount tiers are three different formulas.
- **Consult fee (5 factors: 4 parameter, 1 method).**
  - appointment_channel_rate (parameter)
  - build_stage_rate (parameter; purchase start date + appointment date; purchase)
  - billed_fee_count (method: tier 1 computes ceil(hours/package hours), the others are constants. This is a change of algorithm, so the label is accepted.)
  - repeat_visit_multiple (parameter)
  - order_relief_rate (parameter; CO lines date/total + appointment date)

  All tiers are distinct, stated in the rule and in compute, and each fall-through equals the baseline.
- **Change order fee (6 factors: 5 parameter, 1 method).**
  - schedule_fee_stage (parameter; file status + purchase stage; purchase)
  - change_percent
  - change_amount_measure (method; three different formulas, honest)
  - paid_order_multiple
  - lead_time_surcharge
  - studio_error_relief

  Observation O3: the tier-2 sub-condition "structural_closed … while … not_started" cannot hold under the lifecycle (structural close is construction start), and the stage `complete` is absent from the framing/drywall/finishes lists here and in the deposit and reinstatement ladders. Both are vacuous, not universal, so no RED.
- **Option deposit due (6 factors as labelled: 4 parameter, 2 method).**
  - structural_stage_percent (parameter; purchase)
  - returned_payment_finish_percent (parameter)
  - long_lead_percent (parameter)
  - **replaced_item_share (labelled method, but it is a parameter; see F3)**
  - credit_offset_method (method)
  - lender_relief (parameter; financing + lock status; lock)

  Observation O5 on credit_offset_method: algebraically the three tiers are applied + s × unapplied with s ∈ {1, 0.5, 0}. They are stated as different ledger bases (credit granted less forfeited / applied plus half the unapplied / applied), so I accept the method label. If it were judged a parameter, F3 would leave this computation with no method factor.

  Each fall-through equals the baseline. The deposit's baseline.rule is self-sufficient: package percents, credit offset = credit applied, removal credits in full, no relief, with ladder and cap guards.
- **Returned payment fee (5 factors: 4 parameter, 1 method).**
  - return_fee_basis (method; three formulas)
  - repeat_return_multiple
  - purchase_return_addition (parameter; purchase ledger XCOUNT; purchase)
  - late_return_addition (posted date vs return date, two rows)
  - cure_rate (method + date of the latest payment vs return date)

  All are distinct and two-way.
- **Allowance return (4 factors: 3 parameter, 1 method).**
  - return_measure (method; three formulas; removal credit vs selected price)
  - removal_return_share
  - homesite_points (parameter; homesite variant through purchase.reservation_id; homesite)
  - delay_points

  All are distinct and two-way.
- **Reinstatement (5 factors: 4 parameter, 1 method).**
  - reinstatement_basis (method; three formulas)
  - quote_escalation
  - reorder_surcharge (purchase)
  - reselection_fee
  - lender_amendment_fee (financing + collection fee; purchase)

  All are distinct and two-way.

Per-task coverage, given that each task holds one tree:
- Task 0 has computations deposit, CO fee, consult fee and goodwill. Multi-source factors include schedule_fee_stage and affiliated_financing_points; cross-difficulty factors cover purchase and lock.
- Task 1 has computations reinstatement, returned fee and allowance. Multi-source factors include cure_rate and return_measure; cross-difficulty factors cover purchase (ledger) and homesite.

Realism observations (O10) do not amount to a RED:
- Homesite premium class raising an allowance return.
- Error amount = the *replacement* price when the replacement costs as much as or more than the removed line.

Both are unusual but cannot be shown to be treatments no builder would publish.

### findings

- **F1 — SOURCE-POLICY RED (design_ext_option_deposit_due; bears on task 0).**
  - *Symptom:* one removal credit is assigned by the rule to two groups, and compute assigns it to neither.
  - *Root cause:* the long-lead group subtracts "the removal credits booked on cabinetry and countertop lines at those stages", and the replaced-item sentence reads "Removal credits booked on cabinetry and countertop lines while the construction stage was foundation or framing are deducted from the long-lead group by a replaced-item share: where cabinetry or countertop lines were also added at those stages, the share is zero and those credits are not deducted". The finish group is "every other cabinetry, countertop, flooring, appliance and exterior line less the removal credits booked on those lines". A cabinetry or countertop line *added before* foundation and *removed at* foundation or framing is an "other" line, so its removal credit is "booked on those lines" and is also "booked … while the construction stage was foundation or framing". Compute (`finish_group … + long_lead_removed`) removes it from the finish group. With share 0 it is then deducted nowhere. The rule never states that exclusion.
  - *Consequence:* demonstrated in task 0 (`0.md`): 8443.55 under compute vs 7884.11 under the literal group reading.
  - *Affected:* deposit rule (finish-group and long-lead sentences), compute `finish_group`.
- **F2 — SOURCE-POLICY RED (design_ext_line_reinstatement_price; bears on task 1).** This is an undeclared override.
  - *Passage 1:* the base design_option_selection says "A quoted option price is honored only when the line is added within option_price_protection_days calendar days after the appointment at which it was quoted. Counting starts the day after the appointment date and the last counted day is included; after that the current studio price applies." This is the `price_protection` gate, applying to design_option_added.
  - *Passage 2:* the extended rule says "…names the most recent selection appointment as the appointment at which it was quoted", and "The quote escalation percent is set by the calendar days from the date the removed line was first selected to the day it is put back: … more than the package's price protection days and up to long_quote_days days give mid_quote_escalation_pct percent; the package's price protection days or fewer give none."
  - The two passages set the staleness of the same quote with the same parameter from different anchors. `overwrite` names only "Options are added to the file at the price quoted at the appointment."
  - *Consequence:* demonstrated in task 1 (`1.md`): 3453.80 vs 3335.00.
  - *Affected:* reinstatement `overwrite`, rule, and compute `quote_escalation_pct`.
- **F3 — SOURCE-FACTOR RED (design_ext_option_deposit_due.factors.replaced_item_share; bears on task 0).** This is a mislabelled effect.
  - The factor is labelled `method`, but compute is `long_lead_group = MX(0, long_lead_added - long_lead_removed * replaced_item_share)` with `replaced_item_share ∈ {0, K('unreplaced_share')=0.5, 1}`. The tiers substitute a number into one formula, and the policy's own text calls it a "share".
  - Counts survive: the computation keeps credit_offset_method as its method factor (subject to O5) and has 4–5 parameters.
- **Observations (no demonstrated consequence):**
  - O1: CO fee `result` lacks the buyer_request test.
  - O2: consult `recent_order` can pick a fee line that carries no change order number.
  - O3: vacuous structural_closed+not_started tier; `complete` stage omitted from the stage lists.
  - O4: half-even vs half-up rounding.
  - O5: credit_offset_method is algebraically a share.
  - O6: the reinstated line is written under an existing change order.
  - O7: three uuid8s begin with "3"; this is not batch derivation.
  - O8: returned-payment fee lines added after the first appointment carry no change order. This is inherited from the base, which itself books them that way, and no scored parameter is affected.
  - O9: the consult order-relief phrase "the option lines of that change order total" could be read net of removals. The antecedent "those lines were added" supports compute. Task 0's value under the net reading would be 562.50.
  - O10: the realism notes above.

## closing_checklist

Written after the reveal (2026-10-04T23:38:45Z). The sections above were frozen with sha256 `4ed8469f…` before that time and are unchanged.

**The difficulty does not pass the source-layer audit.** Not all M tasks PASS:

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
|---|---|---|---|---|
| 0 (`0.md`) | RED (F1) | PASS | RED (F3) | RED (F1: 8443.55 vs 7884.11) |
| 1 (`1.md`) | RED (F2) | PASS | PASS | RED (F2: 3453.80 vs 3335.00) |

Items of the Step 4 list that do hold:
- **Audit files.** The per-task files map one-to-one to tasks 0 and 1, and `_difficulty.md` sits alongside them. This is the first revision.
- **Coverage and scopes.** The extended policies are fully covered (GT charter_scope: task 0 has 4 policies, task 1 has 3, disjoint, and together they make all 7). Task tools and GT are closed, and the uuid8s are independent.
- **Trees.**
  - Each task's tree has 1–3 prerequisites with ≥ max(n−1, 1) value_input edges: 3 of 3, and 1 of 2.
  - Each tree has an owner=user root.
  - The difficulty-wide prerequisite graph is acyclic.
- **Factors.**
  - Every computation has 4–6 factors and a self-sufficient baseline that gives a definite number different from gold.
  - Every factor bears weight on its world.
  - Each task has multi-source and cross-difficulty factors.
  - The exception is F3, a mislabel.

Items not met, with their findings:
- F1 is an internal double-classification in the deposit rule, together with a compute choice the rule does not state.
- F2 is an undeclared override of the base price-protection gate.
- F3 is the mislabelled `replaced_item_share`.

The instantiation-stage gate re-run on the final form is not performed by this audit (the artifacts are not edited here). The orchestrator's snapshot stands as cited in § charter_global_frozen.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit (independent subagent, the same auditor as round 1). Re-audit started 2026-10-05T00:17Z. This section was written before any round-2 GT was read.
- Shared inputs at round 2 (hashes verified on disk and matching the round-2 MANIFEST):

  | file | sha256 | vs round 1 |
  |---|---|---|
  | `design.extended.yaml` | `c1b552cae7e99c19a72104809f2c85d14e70c1b26e840158b1b0453c401ba08b` | changed from `215ae98b…` |
  | `task_tools.py` | `e134ea4cd50ed2699bd92cb062785baa1d0d0b826b7904c60b97b288ca74a205` | changed from `8b55ba8b…` |
  | `0.view.json` | `44751194…` | unchanged |
  | `1.view.json` | `ae337ab2…` | changed |

- Both shared inputs changed, so every charter-global section below is **re-derived in full**: I re-read all seven extended policies (lines 671–2235) and every tool docstring and body. Nothing is carried forward by reference.
- Base copy: `diff <(head -669 design.extended.yaml) blueprint/products/design.yaml` shows no difference. It is still verbatim.
- Masked fields: as in round 1. Gate snapshot (orchestrator, after rework): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK, CACHE-DIFF is INFO, and TRACEABILITY NOT OK is deferred until the KB is published. Entry conditions are complete.

### What changed (from the re-read, compared with the round-1 quotations in this file)

- **design_ext_option_deposit_due.**
  - The long-lead and finish group sentences are rewritten: "the long-lead group, being the cabinetry and countertop lines added while the agreement's construction stage was foundation or framing less the long-lead removal credits deducted from it"; "the finish group, being every other … line less the removal credits booked on those lines other than the long-lead removal credits, less any long-lead removal credits sent to it, and less the credit offset".
  - It adds a definition: "The long-lead removal credits are the removal credits booked on cabinetry and countertop lines while the agreement's construction stage was foundation or framing, whenever those lines were added; they are deducted only where the long-lead credit rule places them."
  - It adds a placement ladder: "The long-lead credit rule places the long-lead removal credits: where cabinetry or countertop lines were also added while the construction stage was foundation or framing, the removed item counts as replaced, its credits are deducted from neither group and the long-lead group is the added lines alone; where long-lead removal credits exist but no such line was added at those stages, the credits are deducted from the finish group and not from the long-lead group; otherwise the long-lead removal credits are deducted from the long-lead group."
  - Factor `replaced_item_share` and param `unreplaced_share` are removed. A new factor `long_lead_credit_rule` is added (method; bindings long_lead_removed, long_lead_group, long_lead_credit_to_finish).
  - Compute now has `long_lead_group`, `long_lead_credit_to_finish`, and `finish_group = MX(0, finish_added - finish_removed - long_lead_added + long_lead_removed - long_lead_credit_to_finish - credit_offset)`.
  - The structural % stage list gains `complete`.
- **design_ext_line_reinstatement_price.**
  - A second overwrite entry supersedes the base clause "after that the current studio price applies." with "A reinstated line is priced by this rule alone, never at a quoted price or at the current studio price, whether or not the appointment it is recorded against falls within the package's price protection days; the age of its price is counted from the date the removed line was first selected." The same sentence now stands in the rule.
  - "names the most recent selection appointment as the appointment at which it was quoted" becomes "is recorded against the most recent selection appointment on the file".
  - The re-order surcharge stage list gains `complete`.
- **design_ext_change_order_fee.**
  - New sentence: "An error-correcting change order is recorded at 0.00 under the package's builder-error waiver and is not priced by this rule."
  - Schedule-fee tier 1 becomes "framing, drywall, finishes or complete" and tier 2 "foundation" (the impossible `not_started` sub-condition is removed). Rule, compute and ladder agree.
- **design_ext_studio_consult_fee.** "the option lines of that change order total" becomes "the option lines added under that change order total", in both tiers and in compute_basis. Compute is unchanged (it sums adds).
- **design_ext_returned_payment_fee.** The cure ladder is now "an ACH or wire payment … cleared_cure_pct; a check or card payment … paper_cure_pct; otherwise 100". The params are renamed (cleared_cure_pct 50, paper_cure_pct 75), and compute matches.
- **design_ext_removed_line_allowance.** The return-share stage list in rule and compute gains `complete`.
- **design_ext_error_goodwill_credit.** No change found.
- **task_tools.py.** `reinstate_option_line_5b4fa2c4` docstring: "the appointment at which it was last quoted" becomes "the selection appointment it is recorded against", and the appointment_seq arg becomes "the sequence number of the most recent selection appointment on your file, the appointment the reinstated line is recorded against". The other six tools, all bodies, all owners and all uuid8s are unchanged.

### policy_conflict_scan (revision 2)

- **Subjects, triggers, targets and cross-category reads.** The same seven policies and `(target_tool, computes)` pairs as round 1. Tree A (deposit ← CO fee, consult, goodwill) and Tree B (reinstatement ← allowance, returned fee) are still disjoint and jointly complete.
- **F1 (closed at charter level).** A removal credit booked at foundation or framing on a cabinetry or countertop line added earlier is now a "long-lead removal credit" ("whenever those lines were added"). The finish group explicitly excludes it ("other than the long-lead removal credits"), and the credit rule alone places it. One reading remains.
- **F2 (closed at charter level).** The base price-protection sentence speaks of "a quoted option price". The extended rule now says a reinstated line is "never at a quoted price … whether or not the appointment it is recorded against falls within the package's price protection days; the age of its price is counted from the date the removed line was first selected". The base "after that the current studio price applies" is declared superseded. The base gate therefore cannot attach to a reinstated line, the anchor is stated once, and the merged semantics are unique. The declaration's replaced_by is scoped to reinstated lines, the same pattern accepted for the consult fee's scoped override in round 1.
- **New conflicts found:** none.

### rule_compute_equivalence (revision 2)

- **Deposit.**
  - `long_lead_group`: tier 1 gives `long_lead_added`, matching "the long-lead group is the added lines alone". Tier 2 gives `long_lead_added` (0 when none added), matching "not from the long-lead group". Tier 3 gives `MX(0, added − removed)`, matching "deducted from the long-lead group".
  - `long_lead_credit_to_finish` is the tier-2 credits, matching "deducted from the finish group".
  - `finish_group` subtracts finish removals other than long-lead ones (`- finish_removed + long_lead_removed`) and the credits sent to it, matching the rewritten finish sentence.
  - Every new sentence has its binding and every new binding has its quote. **Two-way. F1's compute/rule gap is closed.**
- **CO fee.** The new scope sentence removes error-correcting change orders from this rule, so `result`'s lack of a reason test is no longer an empty promise. **O1 is addressed** (it remains a scope statement with no binding, which is acceptable). The stage tiers agree in rule, compute and ladder. **O3 is addressed.**
- **Consult.** "added under that change order" now matches `recent_order_total` (adds only). **O9 is addressed.** O2 (LATEST may hit a fee line with no change order number) is kept; it has no effect in either world.
- **Returned fee.** The cure ladder is two-way.
- **Allowance, reinstatement, goodwill.** Two-way.
- **New observation O11.** In design_ext_removed_line_allowance, the factor ladder text of `removal_return_share` still reads "foundation, framing, drywall or finishes", while the rule and compute now include `complete`. This is a metadata-only mismatch: a removal at `complete` cannot occur once the file is finalized at drywall, and task 1's stage is foundation. No consequence.
- O4 (half-even rounding) is kept, with no half-cent case in either world.

### action_binding_and_uuids (revision 2)

- Each `(target_tool, computes)` pair is still claimed by exactly one policy.
- The uuid8s are unchanged (50efc86e, 3108e630, 33ff7b41, 3846be30, 69a7241d, 4e51d426, 5b4fa2c4) and the owners are unchanged.
- The reworked reinstate docstring names no other tool and carries no ordering word ("most recent" refers to the appointment record, not to a call sequence).
- No body judges eligibility or prerequisites.
- **Pass.**

### prerequisite_graph and prerequisite_sentences (revision 2)

- The `prerequisite` fields of the deposit and the reinstatement are textually unchanged. The other five are `[]`. The graph is acyclic.
- Each policy_source is still verbatim in its own rule (deposit rule lines 1413–1417; reinstatement rule lines 2068–2070).
- All edges are state form. Each resolving tool is the sole writer of its state.
- The new rule sentences (the long-lead credit rule; "priced by this rule alone …"; the CO fee scope sentence) state no cross-problem order and name no tool or policy id.
- **Pass.** This is the same derivation as round 1, re-checked against the new text.

### override_declarations (revision 2)

- **Reinstatement.**
  - Declared: "Options are added to the file at the price quoted at the appointment." and "after that the current studio price applies."
  - The base sentence "A quoted option price is honored only when the line is added within option_price_protection_days …" is not itself superseded, but it no longer conflicts: it governs quoted prices, and the extended rule states that a reinstated line is never at a quoted price.
  - "Every set of changes after the first appointment is written as one numbered change order" is literally satisfied by writing the line under CO-2. O6 is kept.
  - **No undeclared override. F2 is closed.**
- **Deposit.** The two declarations are unchanged. The new credit-placement sentences touch no base sentence (the base has no group or long-lead concept). No undeclared override.
- **CO fee.** The new scope sentence agrees with base design_change_orders "A change order written to correct a studio or builder error carries no fee … where change_order_fee_waived_builder_error is true" (true for every package). No conflict.
- **Returned fee.** The cure ladder by payment method is consistent with base accepted_payment_methods. No conflict.
- **Others.** Unchanged from round 1; no undeclared override.

### factor_ladders (revision 2)

- **Deposit (6 factors: 4 parameter, 2 method).**
  - Factors: structural_stage_percent (P), returned_payment_finish_percent (P), long_lead_percent (P), **long_lead_credit_rule (M)**, credit_offset_method (M, O5 kept), lender_relief (P).
  - long_lead_credit_rule's tiers route the credits to neither group, to the finish group (at the finish percent), or to the long-lead group (at the long-lead percent). That changes how the line deposit is computed, not a number in one formula, so the `method` label is honest. **F3 is closed.**
  - Its fall-through ("otherwise … deducted from the long-lead group") equals baseline.rule's "the long-lead removal credits are deducted from the long-lead group". The baseline bindings are `long_lead_group: MX(0, long_lead_added - long_lead_removed)` and `long_lead_credit_to_finish: 0`, which is honest.
  - The bindings are disjoint from long_lead_percent's.
- **CO fee.** schedule_fee_stage is still 3 distinct tiers, each with a satisfiable condition. The others are unchanged.
- **Returned fee.** cure_rate tiers: ACH/wire 50, check/card 75, otherwise 100. They are distinct and plausible (cleared versus paper funds).
- **Consult, goodwill, allowance (O11 aside), reinstatement.** Unchanged in structure.
- **Per-task coverage.** As in round 1: task 0 has multi-source factors and covers purchase and lock; task 1 has multi-source factors and covers the purchase ledger and homesite.

### findings (revision 2, charter-global)

- **F1: closed.** The rule now names the double-classified credit and places it once. See the deposit sections above.
- **F2: closed.** The base clause is declared superseded, and the extended rule states its own anchor and excludes the quoted-price reading.
- **F3: closed.** The mislabelled factor is replaced by an honest method factor.
- **O1, O3, O9 addressed** (above). **O-T1** is a task-1 seed matter, judged in `1.md` revision_2.
- **Kept:** O2, O4, O5, O6, O8, O10, unchanged from round 1 and still without consequence.
- **New:** O11 (observation only; see rule_compute_equivalence).
- **No new RED at charter level. No regression** in any section re-derived above.

### closing_checklist (revision 2)

Written after the round-2 reveal. The revision_2 charter-global sections above were frozen (sha256 `8ada9f6c…`, 2026-10-05T00:20:35Z) before any round-2 GT was read.

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
|---|---|---|---|---|
| 0 (`0.md` § revision_2) | PASS | PASS | PASS | PASS |
| 1 (`1.md` § revision_2) | PASS | PASS | PASS | PASS |

- **Audit files.** The per-task files map one-to-one to tasks 0 and 1, and `_difficulty.md` sits alongside them. Round-1 text is preserved, revision_2 is appended, and every revision_2 comparison carries a PASS.
- **Coverage and scopes.**
  - The extended policies are fully covered.
  - Scopes are pairwise disjoint (GT charter_scope: task 0 has CO fee, goodwill, consult and deposit; task 1 has returned fee, allowance and reinstatement), and each scope spans its whole tree.
  - Task tools and GT are closed.
  - The uuid8s are independent and frozen, unchanged since round 1.
- **Trees.**
  - Task 0: 3 prerequisites, 3 value_input edges (≥ 2), owner=user root.
  - Task 1: 2 prerequisites, 1 value_input edge (≥ 1), owner=user root.
  - The difficulty-wide prerequisite graph is acyclic.
- **Factors.**
  - Every computation declares a self-sufficient baseline and 4–6 factors, with at least 2 parameter and 1 method factors. Each task has multi-source and cross-difficulty factors (task 0: purchase, lock; task 1: purchase ledger, homesite).
  - Every ladder has at least 3 distinct tiers stated in its rule, labels are honest (F3 closed), and every factor bears weight on its world.
  - Every whole-baseline figure is definite and differs from gold.
- **Gate re-run on the final form.** Cited from the orchestrator's round-2 snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK; TRACEABILITY is deferred until the KB is published). This audit did not re-run the gates.
- **Remaining observations (no consequence; not grounds for rework):** O2, O4, O5, O6, O8, O10 (kept from round 1) and O11 (new).

**The difficulty passes the source-layer audit at revision 2.**
