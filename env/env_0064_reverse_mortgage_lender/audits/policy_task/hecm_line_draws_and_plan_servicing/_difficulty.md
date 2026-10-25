# Policy-task audit — hecm_line_draws_and_plan_servicing / charter-global

## charter_global_frozen

- Frozen: 2026-10-15T07:15:54Z (file mtime; an earlier draft of this line said 07:20Z, an estimate), auditor: erl-task-policy-audit (independent of the instantiating agent), round 1.
- Inputs and their sha256 prefixes, the same as the coordinator's gate snapshot:
  - `tasks/hecm_line_draws_and_plan_servicing/hecm.extended.yaml` 766c0670d5eacaa4
  - `tasks/hecm_line_draws_and_plan_servicing/task_tools.py` 4da8d29f84fb4fe0
  - `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml)
  - DSL semantics: `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS, `_within`, CFIELD/CPARAM first-match, XSUM/XCOUNT scoped to the customer, RND = Python `round`)
- Masked and not read when this section was written: every `tasks/*/tasks/*.json` field other than `frozen_time`, `user_scenario` and `initial_state` (evaluation_criteria, computations, solvability_contract, prerequisite_closure, charter_scope, required_documents, design_rationale).
- Entry conditions (Step 0): the gate snapshot `snapshot_r1.txt` arrived with the brief. It shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK. The only traceability misses are `unlock_agent_discoverable_tool:tool_name`, and validate is INVALID only on "required document not found". The coordinator states both are expected before render. The masked-view hashes c8df131371c95a5e and c09a01b5b59c9a27 were re-checked and match. The entry conditions are accepted; the pre-render INVALID is recorded as an observation and not counted as a red.
- Base copy check: `diff <(head -1916 hecm.extended.yaml) blueprint/products/hecm.yaml` is empty, so the base section is verbatim.

### policy_conflict_scan

The charter has six extended policies:

| policy | target tool (owner) | computes | subject |
|---|---|---|---|
| hecm_ext_draw_ceiling | submit_line_draw_request_b0795434 (user) | requested_amount | hecm_advance_posting |
| hecm_ext_check_void | void_uncashed_draw_check_f08764ed (agent) | reversal_amount | hecm_disbursement_return, hecm_advance_reversal |
| hecm_ext_payment_release | convert_payout_plan_to_line_d82e9c7e (agent) | release_amount | hecm_line_release |
| hecm_ext_reinstatement_restore | restore_reinstated_line_c85e4df8 (agent) | restore_amount | hecm_line_restore |
| hecm_ext_payment_designation | sign_payout_plan_change_346bec33 (user) | requested_amount | hecm_line_commitment |
| hecm_ext_payment_reset | process_payout_plan_change_72a1f37c (agent) | scheduled_payment_amount | hecm_plan_change |

- **Overlapping subject: plan-change processing.** Payment_release (move off scheduled payments onto the Line of Credit) and payment_reset (move onto a plan with scheduled payments) both process a `payment_plan_change` request and both mark it `processed`.
  - Their triggers are disjoint by target plan.
  - But the payment_reset rule also states a Line-of-Credit branch: "for the HECM Line of Credit it is 0 and no payment is set". Its tool enum also accepts `new_plan="HECM Line of Credit"`. So payment_reset's own rule describes a write that its trigger excludes. See F-OBS-3 and the unreachable-tier class F-FAC-1.
- **Plan changes from one scheduled plan to another.** Base `hecm_payment_plan_change` orders "release, then commitment, then update, then fee".
  - Payment_reset's tool books no release.
  - Payment_release's trigger is limited to moves onto the Line of Credit.
  - So no extended policy or tool handles a change from one scheduled plan to another. The base ordering sentence names a cross-problem order (release before commitment) that grounds no declared edge. It matters only in a world whose loan currently pays scheduled payments and asks for a scheduled plan. It is checked per task.
- **Shared quantities.** Draw_ceiling's tax/insurance reserves and designation's tax/insurance holds use identical ladders on different targets, so there is no conflict. Draw_ceiling's arrangement reserve and payment_reset's withholding read the same propcharge record with different tier wording (see F-POL-4).
- **Cross-category read boundaries.** propcharge (status, arrearage_balance, monthly_installment, propcharge_transactions charge_type/amount), setaside (status, annual_property_tax, Repair Set-Aside fields and params), residency (status, plan occupancy_inspection_fee), maturity (cured case variant and closed_date, cure_confirmation notices). All of them are reachable through the share finders `find_propcharge_*`, `find_setaside_*`, `find_residency_*` and `find_maturity_*`.
- **Scopes.** The prerequisite graph splits the six policies into two trees:
  - {draw_ceiling ← payment_release, check_void}
  - {payment_reset ← payment_designation ← reinstatement_restore}
  - The two are disjoint and together cover all six. Whether task 0 and task 1 claim exactly these trees is checked at the reveal.

### rule_compute_equivalence

A mechanical sweep (normalised whitespace) checked the following:
- every `compute_basis` quotation is a substring of its own policy's `rule`;
- every `baseline.rule` sentence is in the `rule`;
- every overwrite `superseded_clause` is verbatim in the base rule, and every `replaced_by` is verbatim in the extended rule;
- every compute binding has a basis, except `hecm_ext_payment_release.is_tenure`, which has none (the rule names the tenure plans in prose; observation).

Sentence by sentence, the following points of non-equivalence remain:

1. **payment_reset `withholding`.**
   - The rule's first tier reads: "when the loan has a property charge repayment record whose status is notice_period or defaulted with an arrearage_balance above 0.00, the withholding is that arrearage_balance divided by 12". It has no "no record active" clause. The compute requires `pc_act == 0` and the ladder `when` adds "and no record is active".
   - The rule's second tier reads: "when the loan has a record whose status is active with a monthly_installment above 0.00". It has no arrearage condition. The compute requires `pc_act > 0`, that is, an active record with arrearage above 0.
   - So the compute and ladder state conditions the rule does not → F-POL-4.
2. **draw_ceiling `rp_paid`.** `XCOUNT('setaside','setaside_transactions', event_type='setaside_repair_disbursement')` counts repair disbursements on every set-aside of the customer. The rule says "an active Repair Set-Aside on the loan has paid at least one repair disbursement". A closed or older Repair Set-Aside's disbursements would be counted → F-POL-5 (consequence per world).
3. **draw_ceiling `pc_lump`.** The compute sums the notice_period and the defaulted record. The rule says "that whole arrearage_balance" (singular). The two differ only when both records exist (per world).
4. **payment_release `r`.** The compute adds `F('rate_type') != 'fixed'`, which no rule sentence states. A fixed-rate loan cannot change plan (base), so this is unreachable (observation).
5. **payment_reset `req_plan`/`req_amt`/`req_term`.** These are LATEST submitted `payment_plan_change` rows with no `request_channel` filter. The rule binds the signed_written request (per world).
6. **CFIELD first-match reads** (`cure_type`, `cure_date`, PCD `closed_date`, propcharge records, residency status). The rule speaks of "the loan's cured case" or "the profile". A second matching record would silently pick a row → decoy test per world.
7. **Rounding.** Every rule says "rounded half up to the cent", but `RND` is Python `round(float, 2)`. That is banker's rounding on a binary float, which differs from half up only on an exact half-cent. Observation; checked per task on the scored value.
8. **MONTHS anniversary fallback.** `MONTHS(closing, NOW) < 12` treats a 29/30/31 closing day in a shorter anniversary month as still before the anniversary on the fallback day. The rule says the anniversary falls back to the last day of that month. These differ only on that day (per world).

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy: six policies and six distinct tools.
- The uuid8 tails are b0795434, f08764ed, d82e9c7e, c85e4df8, 346bec33 and 72a1f37c. None is reused, they share no prefix, and they show no sequence or adjacency. They appear to be independently generated.
- No tool body checks eligibility, a prior step or a prerequisite. Each one creates and updates exactly what its docstring says, and the module docstring says "none of them checks eligibility, ownership, timing or prior steps". The tools do not judge prerequisites.
- Docstrings name no other tool and no policy id. Every docstring ends with an "Afterwards the borrower sees/can quote …" sentence. "Afterwards" is an ordering word, but it describes the call's own post-state, not a position relative to another write (observation F-OBS-1).
- `sign_payout_plan_change_346bec33` stores the Modified-plan designation in `requested_amount`, while db_schema says "amount requested for a draw; 0.00 for other request types". The base rule itself uses requested_amount for the Modified commitment (observation F-OBS-2).
- The 20.00 fee hard-coded in two tools equals `payment_plan_change_fee` on every plan that permits a change.
- The docstrings contain no example values that could leak gold.
- Payment_reset's tool accepts `new_plan="HECM Line of Credit"` and its rule carries a Line-of-Credit tier. A Line-of-Credit request could therefore be "processed" by either `convert_payout_plan_to_line_d82e9c7e` or `process_payout_plan_change_72a1f37c`. The triggers separate them, so this is an observation (F-OBS-3) and is demonstrated per task.

### prerequisite_graph

The graph has four edges:

| # | blocked → depends on | kind | gate | form | resolved_by = dep target_tool |
|---|---|---|---|---|---|
| E1 | draw_ceiling → payment_release | state_gate | hecm_requests.request_status | state | convert_payout_plan_to_line_d82e9c7e ✓ |
| E2 | draw_ceiling → check_void | value_input | drawable (binding exists) | state | void_uncashed_draw_check_f08764ed ✓ |
| E3 | payment_designation → reinstatement_restore | value_input | line (binding exists) | state | restore_reinstated_line_c85e4df8 ✓ |
| E4 | payment_reset → payment_designation | value_input | committed (binding exists) | state | sign_payout_plan_change_346bec33 ✓ |

- Every policy fills `prerequisite`; check_void, payment_release and reinstatement_restore have `[]`.
- Every `problem` is an extended id, none is a base policy, there are no self-edges, and the graph is acyclic (two disjoint chains of depth 1 and 2).
- Every `policy_source` is verbatim in its own policy's rule (mechanical check).
- All edges use the state form, so `fallback_reason` is correctly absent.
- No authoring-viewpoint phrasing appears in any `prerequisite` text.
- Conditions against sentences:
  - E1's condition is broader and narrower than its sentence → F-POL-2.
  - E3's condition is unachievable by its resolving write → F-POL-1.
  - E2's condition "for at least the plan's void period" vs the sentence "past the void period": the base void rule allows the void "on the last counted day itself". So "past" is at most one day stricter (observation).

### prerequisite_sentences

- **E1** "The draw ceiling is worked out only once every signed payout plan change request on file for the loan shows request status processed or declined."
  - Connective "only once" ✓. It names a record state (`request_status`) ✓, with no tool, id or snake_case ✓.
  - Scope against condition ✗ (F-POL-2).
  - Writes that bring "processed" about: `convert_payout_plan_to_line_d82e9c7e` (payment_release) and `process_payout_plan_change_72a1f37c` (payment_reset). No tool of this difficulty or the share layer writes "declined".
  - Derivation: the sentence plus a submitted signed request whose `requested_plan` is the Line of Credit plus payment_release's trigger ("moves a loan off scheduled payments onto the HECM Line of Credit") lead to convert. Payment_reset's trigger ("onto a plan with monthly scheduled payments") excludes it, although its rule's dead Line-of-Credit tier invites the second write (F-OBS-3).
- **E2** "The draw ceiling is not worked out until every draw check on the loan that has stayed uncashed past the void period carries its return entry."
  - Connective "not … until" ✓. Waited-on state "carries its return entry" = `hecm_disbursement_return` with `source_txn_ref` ✓.
  - Exactly one write books return entries (void tool) ✓.
  - The domain "draw check … that has stayed uncashed" is not record-visible: `hecm_transactions` has no cashed or presented field. Which checks are uncashed must come from the customer (observation F-OBS-4; per task, whether the persona supplies it).
- **E3** "The designated amount is not worked out until every prepaid portion applied while the loan was due and payable carries its line restoration entry."
  - Connective ✓, record state ✓.
  - The only resolving write is the restoration, which per its own rule is "booked as one line restoration entry referencing the most recent prepaid portion posted on the loan with restores_line false". It cannot make every portion carry an entry → F-POL-1.
- **E4** "The new scheduled payment is fixed only after a signed payout plan change request for the change stands on file for the loan with request status submitted."
  - Connective "only after" ✓, record state ✓, one write (the user's signing tool) ✓.
  - Payment_reset's rule also carries the base eligibility sentence "A plan change is processed only against a payment plan change request on file … signed_written channel …". That is a second wording of the same dependency, inherited from base (observation F-OBS-5). The same base sentence is restated in payment_release.
- **The depended-on rules do not restate their dependents' sentences** ✓.
- **Undeclared cross-problem order.** Base `hecm_payment_plan_change` reads "Processing happens in this order on the handling date: … hecm_line_release; then … hecm_line_commitment …". This is a base sentence ordering two extended problems' subjects without a declared edge. It is an observation unless a task's tree rests on it (per task).

### override_declarations

- **draw_ceiling vs hecm_evt_loc_draw.**
  - The first-year clause and the min/available-line clause are replaced, and both replacements are declared.
  - The scheduled-payment deduction and the four reserves act through the declared first-year-room and draw-ceiling caps.
  - The first-year draws drop the base measure's window and subtract return entries (draw amounts) instead of `hecm_advance_reversal` amounts. Under check_void the reversal is the settlement (draw + interest + MIP), not the draw. This is inside the declared replacement.
  - Every other sentence (plan eligibility, active, request on file, maturity suspension, phone cap, wire, once, posting, processing days) is inherited and not weakened. Closure ✓.
- **check_void vs hecm_evt_disbursement_return.** Both changed sentences are declared: the full-amount reversal and "never exceeds the original amount". The void-timing sentences are restated verbatim. The returned-bank-transfer and set-aside-refund sentences are inherited ✓. `hecm_evt_servicing_fee` is in base_policy_refs, but nothing in check_void touches the fee quantity (observation).
- **payment_release vs hecm_payment_plan_change.** Remaining-payment count/age and the monthly rate are declared, with the timing shift named in the replaced_by. The Line-of-Credit change fields (0.00 / 0 / empty), the fee, active and the signed request are restated ✓.
- **reinstatement_restore vs hecm_evt_prepayment.** The due-and-payable "nothing is restored" sentence is declared and replaced ✓. The restoration of only principal (or principal + interest) portions restores less than the base gives an active loan, but the base sentence for due-and-payable portions ("nothing is restored") is what was replaced, so it is declared.
- **payment_designation vs hecm_payment_plan_change: `overwrite: []`, with an undeclared override → F-POL-3.**
  - Base: "for a change into a Modified plan the committed amount is the requested_amount on the request, which may not exceed the available line after any release, otherwise the request is declined with reason insufficient_available_line". So the most a borrower may commit is the available line.
  - Extended: "the designated amount, the most of the line Cedarline lets the borrower commit to the payments on the handling date". This is the available line less four holds, times a 75/90/100 % share.
  - The two clauses settle the same quantity (the most of the line a Modified plan may commit) differently, and no overwrite names the base sentence. Compare draw_ceiling, which declares the same kind of cap change.
- **payment_reset vs hecm_payment_plan_change.** The new-payment formula and the monthly rate are declared. The committed-amount and payment-count tiers restate the base sentences "For a change into the Tenure or Term plan the whole available line after any release is committed; for a change into a Modified plan the committed amount is the requested_amount" and "the payment count is the requested term … and, for a tenure-based plan, twelve times …". The declared replaced_by says those are "set out here", so the declaration is formally complete. The factor consequence is F-FAC-2.

### factor_ladders

| policy | factor | label | tiers | multi-source tier | x-difficulty | structural verdict |
|---|---|---|---|---|---|---|
| draw_ceiling | first_year_room_basis | method | 3 | anniv × sched history ✓ | — | ok; tier 2 (on/after anniversary → available_line) is part of baseline.rule, so the fall-through equals the baseline only before the anniversary (obs) |
| draw_ceiling | arrangement_installment_reserve | method | 3 | notice/defaulted ∧ no active record ✓ | propcharge | ok; pending_signature records ignored (obs) |
| draw_ceiling | tax_renewal_reserve | parameter | 3 | no-advance ∧ depleted set-aside ✓ | propcharge(+setaside) | ok |
| draw_ceiling | insurance_renewal_reserve | parameter | 3 | no hazard ∧ flood ✓ | propcharge | realism obs: when both hazard and flood were advanced only hazard is reserved |
| draw_ceiling | repair_holdback_reserve | parameter | 3 | active SA ∧ ≥1 disbursement ∧ age ✓ | setaside | **RED F-FAC-3** (double reservation) |
| check_void | interest_return_period | method | 3 | — | — | **RED F-FAC-1** (compound part holds for all; fall-through unreachable) + **F-FAC-3** (rate-type day count) |
| check_void | interest_return_rate | parameter | 3 | rate changed ∧ accruals ✓ | — | **RED F-FAC-1** (accrual part holds for all; fall-through unreachable) |
| check_void | premium_return_period | method | 3 | — | — | **RED F-FAC-1**; label borderline (tier 1 = cap of tier 2: min(m,12)/12) (obs) |
| check_void | premium_return_rate | parameter | 3 | — | — | **RED F-FAC-1** + tier 1 = tier 2 in value (F-FAC-4) |
| payment_release | release_count_rule | method | 3 | tenure ∧ ≥1 payment ✓ | — | **RED F-FAC-2** (tenure plan with no payment falls to term-count fall-through → 0 or negative) |
| payment_release | release_horizon_floor | parameter | 3 | — | — | 95+ tier is HUD practice; 90-94 +10 proprietary (F-FAC-5) |
| payment_release | release_rate_basis | parameter | 3 | — | — | **RED F-FAC-5** (HUD expected-rate method) |
| payment_release | release_timing_shift | method | 3 | — | — | ok structurally (shift exponent changes the annuity form) |
| reinstatement_restore | restore_cure_scope | method | 3 | — | maturity | **RED F-FAC-1** (tiers 2 and 3 unreachable) |
| reinstatement_restore | restore_inspection_netting | parameter | 3 | fees ∧ profile status ✓ | residency | ok |
| reinstatement_restore | restore_delay_period | method | 3 | — | maturity | ok |
| reinstatement_restore | restore_delay_rate | parameter | 3 | — | — | fall-through unreachable (F-FAC-1 member); tier 1 = tier 2 whenever the note rate has not changed since the last growth credit (per world) |
| payment_designation | designation_tax_hold | parameter | 3 | ✓ | propcharge(+setaside) | ok |
| payment_designation | designation_insurance_hold | parameter | 3 | ✓ | propcharge | same hazard-over-flood obs |
| payment_designation | designation_inspection_hold | parameter | 3 | current ∧ fees ✓ | residency | ok |
| payment_designation | designation_queued_hold | method | 3 | — | — | label borderline (tier 2 = cap); caps the total of several phone requests at the single-draw phone cap (realism obs) |
| payment_designation | designation_post_cure_share | method | 3 | PCD cured ∧ notice count ✓ | maturity | **RED F-FAC-4** (mislabel: 75/90/100 % into one formula) |
| payment_reset | new_payment_commitment_basis | method | 3 | — | — | **RED F-FAC-2** (base rule restated; straw-man baseline; fall-through unreachable) |
| payment_reset | new_payment_count_rule | method | 3 | — | — | **RED F-FAC-2** (same) |
| payment_reset | new_payment_horizon_floor | parameter | 3 | — | — | as release_horizon_floor (F-FAC-5) |
| payment_reset | new_payment_rate_basis | parameter | 3 | — | — | **RED F-FAC-5** |
| payment_reset | new_payment_withholding | parameter | 3 | notice/defaulted ∧ no active ✓ | propcharge | rule vs compute drift F-POL-4 |

Declared counts:
- draw_ceiling: 5 (2 method, 3 parameter)
- check_void: 4 (2/2)
- payment_release: 4 (2/2)
- reinstatement_restore: 4 (2/2)
- payment_designation: 5 (2/3)
- payment_reset: 5 (2/3)

Every ladder is stated in full in its rule and implemented in its `decides` binding. The exception is the withholding condition drift (F-POL-4).

Counts after striking the factors the tests remove (F-FAC-*):
- **check_void:** all four fail F-FAC-1 → 0 surviving.
- **payment_reset:** both method factors fail F-FAC-2 and the rate factor fails F-FAC-5 → 2 parameter, 0 method, below the 4-factor and 1-method floors.
- **payment_designation:** post_cure_share is mislabelled → 1 method (queued_hold, borderline).
- **reinstatement_restore:** cure_scope fails → 3 factors.
- **payment_release:** release_count_rule and release_rate_basis fail → 2 factors.
- **draw_ceiling:** repair_holdback_reserve fails → 4 factors.

The bounds failure (F-FAC-6) is therefore charter-global for check_void, payment_release, reinstatement_restore and payment_reset.

### findings

**F-POL-1 — SOURCE-POLICY RED: E3's waited-on state can never be produced by its only resolving write (bears on task 1).**
- Symptom: the designation waits until "every prepaid portion applied while the loan was due and payable carries its line restoration entry" (condition: "Every hecm_prepayment row … posted with restores_line false while it was due_and_payable has a hecm_line_restore row referencing it").
- Root cause: reinstatement_restore's rule says "The reinstatement restoration is booked as one line restoration entry referencing the most recent prepaid portion posted on the loan with restores_line false". The tool books one `hecm_line_restore` with one `source_txn_ref`. Base `hecm_prepayment` posts "one row per remittance per allocation bucket", so one due-and-payable remittance already produces several portions.
- Consequence: wherever more than one restores_line-false portion exists, the prerequisite sentence stays false after the resolving write. A literal reader can never "work out" the designated amount. The alternative is to book one restoration per portion, which contradicts the restoration rule. Demonstrated in task 1's file.

**F-POL-2 — SOURCE-POLICY RED: E1's sentence and condition differ in scope.**
- Sentence: "every signed payout plan change request … shows request status processed or declined".
- Condition: "No hecm_requests row … with request_type payment_plan_change has request_status submitted".
- The sentence is narrower in scope (signed requests only), but stronger in what it demands: processed or declined, while `request_status` also allows `withdrawn`.
- Two situations where they disagree:
  - A withdrawn signed change request: the condition is true, the sentence is false.
  - A submitted phone-channel change request: the sentence is true, the condition is false.
- Whether a task world contains either is checked in task 0's file. Without such a row this edge carries no wrong answer in that task, but the misstatement is charter-global.

**F-POL-3 — SOURCE-POLICY RED: undeclared override in payment_designation (`overwrite: []`).**
- Base cap: "which may not exceed the available line after any release".
- Extended cap: "the most of the line Cedarline lets the borrower commit to the payments on the handling date" = (available_line − tax − insurance − inspection − queued holds) × share.
- The base reading gives a second defensible "most the borrower may commit": the available line. Demonstrated in task 1's file.

**F-POL-4 — SOURCE-POLICY RED (rule ≠ compute/ladder) in payment_reset withholding** (quotations under rule_compute_equivalence item 1).
- The rule's tier 1 has no "no record is active" clause, and its tier 2 has no arrearage condition. The compute and ladder require both.
- With a notice_period/defaulted record and an active record on the same loan, the rule gives arrearage/12, while the compute gives the installment (or 0).
- With an active record whose arrearage is 0.00 and whose installment is above 0, the rule gives the installment and the compute gives 0.
- Consequence per world (task 1).

**F-POL-5 — rule ≠ compute in draw_ceiling `rp_paid` (and `pc_lump`).** The count is not scoped to the active Repair Set-Aside, and the sum runs over two record statuses. This is RED only where a task world seeds the distinguishing record (task 0); otherwise it is an observation.

**F-FAC-1 — SOURCE-FACTOR RED (class): tier conditions that hold of every customer who reaches the write, or fall-through tiers no customer reaching the write can be on.** Members:
1. **check_void interest_return_period.**
   - Tier 1 and tier 2 carry "at least one calendar day has passed" and "at least one whole calendar month has passed". A void is allowed only after `uncashed_check_void_days` = 180 days, so these parts hold for everyone.
   - The fall-through ("otherwise", that is, a fixed rate or 0 elapsed days) is unreachable. Every plan with `loc_draws_permitted: true` permits only `monthly_adjustable` and `annual_adjustable`.
2. **check_void interest_return_rate.**
   - The part "interest accruals have posted … after the same day of the month twelve calendar months before" holds for every active loan carrying a draw at least 180 days old, because base hecm_evt_interest_mip accrues monthly on a positive balance.
   - The fall-through 0 is unreachable.
3. **check_void premium_return_period.** "outstanding at least one … whole calendar month" holds for everyone (180-day void), so the fall-through 0 is unreachable.
4. **check_void premium_return_rate.**
   - Tier 1 "a mortgage insurance premium accrual has posted after the draw's effective_date" holds for every accruing loan with a draw at least 180 days old.
   - Tiers 2 and 3 are unreachable (see also F-FAC-4).
5. **reinstatement_restore restore_cure_scope.**
   - maturity.yaml says "a death or sale case is never cured", and "The cure must arrive by the plan's cure_deadline_basis: the occupancy plans only before the loan is called due". So an Extended Health-Care Absence or Principal Residence Change cure never follows a due-and-payable status, and a Death or Sale case is never cured.
   - This policy applies only to a loan "returns to active status after a cured maturity case" with portions "applied while the loan was due and payable". Every such loan therefore sits on tier 1 (Property Charge or Property Condition Default).
   - Tier 2 and the fall-through (= the baseline "principal portions only") are reachable by no customer at this write.
6. **reinstatement_restore restore_delay_rate.** The fall-through (`line_growth_applies` false) is only the Fixed-Rate Single Disbursement, on which the rule itself says "nothing is restored". It is unreachable.
7. **payment_reset new_payment_commitment_basis and new_payment_count_rule.** The fall-through "otherwise 0.00" and the "HECM Line of Credit → 0" tier are unreachable, because the policy's trigger is a move "onto a plan with monthly scheduled payments" (see F-FAC-2).

**F-FAC-2 — SOURCE-FACTOR RED (class): straw-man baselines, and ladders that restate the base standard.** Members:
1. **payment_reset new_payment_commitment_basis.**
   - The tiers are the base rule ("Modified → requested_amount; Tenure/Term → whole available line").
   - The baseline "The committed amount is the loan's available_line" commits the whole line on a Modified plan, whose defining feature is a borrower-designated part. No servicer applies this.
2. **payment_reset new_payment_count_rule.**
   - The tiers are the base rule.
   - The baseline "the payment count is the requested_term_months on the request, never less than one" pays a tenure request's whole commitment in one month (requested_term_months = 0 → 1). That is a definite but absurd number.
3. **payment_release release_count_rule.**
   - A tenure-based plan that has disbursed no payment yet falls to the fall-through "scheduled_payment_term_months less the scheduled payments already disbursed" = 0 → release 0.00. The baseline.rule applied to any tenure loan with payments made gives a negative count and a negative release.
   - Base's tenure branch "twelve times the difference between tenure_age_horizon_years and the age" is dropped from the baseline (a dropped branch).
   - Whether the task 0 world is tenure-based is checked there.

**F-FAC-3 — SOURCE-FACTOR RED (realism): tier outcomes no HECM servicer publishes.** Members:
1. **draw_ceiling repair_holdback_reserve, tiers 1 and 2.**
   - A Repair Set-Aside already holds `repair_setaside_pct_of_estimate` = 150 % of the estimate outside the line. setaside.yaml says "A Repair Set-Aside equals repair_setaside_pct_of_estimate percent of the accepted repair estimate". `repair_holdback_pct` is defined as "Percent of each progress disbursement held back until the final inspection", that is, held inside the set-aside.
   - Reserving holdback_pct × estimate, or the whole estimate, a second time out of the available line double-reserves funds that are already set aside.
2. **check_void interest_return_period.** The rate type decides the day-count convention (days/365 vs whole months/12) of the interest returned. But the charter accrues interest identically for every rate type: `interest_accrual_method: one_twelfth_note_rate_on_prior_month_end_balance` on all plans, and base hecm_evt_interest_mip "Interest equals the balance basis times one twelfth of the note_rate_pct". The condition is not one the business weighs for that quantity.

**F-FAC-4 — SOURCE-FACTOR RED: a tier collapse and a mislabel.**
1. **premium_return_rate.** Tier 1 ("the annual rate applied by the most recent such accrual") and tier 2 ("the plan's annual_mip_rate_pct") select the same value. Base hecm_evt_interest_mip posts MIP at "one twelfth of annual_mip_rate_pct" with `rate_applied_pct` recording it, and `annual_mip_rate_pct` is 0.5 on every plan.
2. **designation_post_cure_share** is labelled `method`, but its tiers substitute 75 / 90 / 100 into one formula, `remainder × share / 100`. That is a parameter.

**F-FAC-5 — SOURCE-FACTOR RED (realism, HUD-mandated method): release_rate_basis and new_payment_rate_basis.**
- For an FHA-insured HECM, HUD computes tenure and term payments, and recomputes them on a change of payment plan, with the expected average mortgage interest rate plus the annual MIP rate (24 CFR 206.25 / 206.26; HUD Handbook 4000.1 HECM payment-plan sections). The base charter states exactly that.
- A servicer cannot publish a payment or release discounted at the loan's recently applied note rate, or a midpoint of the two.
- Tier 1 and tier 2 of both ladders are therefore treatments no HECM servicer gives.
- Related observation, same class but lower confidence: the 90–94 "+ten_year_floor_years" horizon tier in release_horizon_floor / new_payment_horizon_floor departs from HUD's age-100 table. The 95+ "+5" tier matches HUD's five-year minimum.

**F-FAC-6 — SOURCE-FACTOR RED: factor-count floors not met after striking (see counts above).** Check_void (0 surviving), payment_reset (2 parameter, 0 method), payment_release (2) and reinstatement_restore (3) fall below 4 factors / 1 method.

**Observations (not grounds for rework)**
- **F-OBS-1:** "Afterwards" in every docstring.
- **F-OBS-2:** the requested_amount schema meaning.
- **F-OBS-3:** payment_reset's dead Line-of-Credit tier and tool enum make a second write able to mark a Line-of-Credit change processed.
- **F-OBS-4:** "uncashed" is not record-visible.
- **F-OBS-5:** the base signed-request sentence is restated in two extended rules.
- **Payment_release `is_tenure`** has no basis.
- **The base ordering sentence** (release before commitment) grounds no edge.
- **check_void** carries the hecm_evt_servicing_fee ref.
- **Insurance hazard-over-flood:** when both are advanced, only hazard is reserved.
- **Queued phone requests:** their total is capped at the single-draw phone cap.
- **RND** is not true half-up.
- **The arrangement reserve** ignores a pending_signature record.

**Tasks affected:**
- Task 0 (draw_ceiling, check_void, payment_release): F-POL-2, F-POL-5, F-FAC-1 (1–4), F-FAC-2 (3), F-FAC-3, F-FAC-4 (1), F-FAC-5, F-FAC-6.
- Task 1 (payment_reset, payment_designation, reinstatement_restore): F-POL-1, F-POL-3, F-POL-4, F-FAC-1 (5–7), F-FAC-2 (1–2), F-FAC-4 (2), F-FAC-5, F-FAC-6.

charter-global REDs: F-POL-1, F-POL-2, F-POL-3, F-POL-4, F-FAC-1, F-FAC-2, F-FAC-3, F-FAC-4, F-FAC-5, F-FAC-6

## post_reveal_charter_addendum (written after both tasks were frozen and revealed)

**F-POL-6 — SOURCE-POLICY RED: rule ≠ compute (an undeclared rounding point in rate averages).**
- Found while comparing task 0 with GT. Recorded here because it is a defect of the charter's compute, not of one world.
- The defect:
  - `hecm_ext_check_void.int_avg` and `hecm_ext_payment_reset.avg_rate` average applied rates as `SUM(..., 'rate_applied_pct', ...)/COUNT`.
  - The DSL `SUM` returns `round(s, 2)`, so a sum of three-decimal percentage rates is rounded to two decimals before averaging.
  - The rules say "the average of the annual rates those accruals applied" and "only that total is rounded, half up to the cent" (check_void), and "the average of the annual rates applied by the interest accruals" (payment_reset). Neither states such a rounding.
- Consequence:
  - task 0: 7,791.42 (GT) against 7,791.40 (rule);
  - task 1: not engaged (the rates sum to exactly 77.76).
- Bears on tasks 0 and 1.

## closing_checklist

**Not closed.** The difficulty does not pass the source-layer audit.
- [x] Per-task files 0.md and 1.md correspond to tasks 0 and 1, with `_difficulty.md` alongside. This is the first round, so there are no older revisions.
- [x] Scopes: task 0 = {draw_ceiling, check_void, payment_release}; task 1 = {payment_reset, payment_designation, reinstatement_restore}. They are pairwise disjoint and cover all six extended policies. The uuid8s are independent.
- [x] Trees: each has 2 prerequisite problems, ≥1 value_input edge, an owner=user write and no cycle. The difficulty-wide graph is acyclic.
- [ ] Factor bounds and realism: they fail (F-FAC-1 … F-FAC-6).
- [ ] Every comparison PASS: task 0 fails (SOURCE-POLICY/CHAIN/FACTOR/TASK); task 1 fails (SOURCE-POLICY/FACTOR).
- [ ] Gate re-run on the final form: not applicable until rework. The auditor runs no gates.

task0=SOURCE-POLICY RED task1=SOURCE-POLICY RED
charter=F-POL-1,F-POL-2,F-POL-3,F-POL-4,F-POL-6,F-FAC-1,F-FAC-2,F-FAC-3,F-FAC-4,F-FAC-5,F-FAC-6

## revision_2

### charter_global_frozen (revision_2)

- **Basis.** Built pre-reveal from the charter, schema, tools and DSL only.
  - Auditor: erl-task-policy-audit, round 2.
  - Worklog gate line: `REWORK round 2: gates 7/7 green` ✓.
  - Snapshot `snapshot_r2.txt` was produced by `/tmp/erl0064_coord/snapshot.sh hecm_line_draws_and_plan_servicing 2`.
- **Hashes.**

| file | round 1 | round 2 |
|---|---|---|
| hecm.extended.yaml | 766c0670d5eacaa4 | **d8346da9bf969900** (changed → every charter-global section re-derived in full) |
| task_tools.py | 4da8d29f84fb4fe0 | 4da8d29f84fb4fe0 (unchanged → the action_binding_and_uuids conclusions carry forward) |
| masked view 0 | — | 8cf72c089d71ccd3 |
| masked view 1 | — | f7bfa5f4610cb27d |

- **Base copy.** Still verbatim (diff against blueprint/products/hecm.yaml is empty).
- **Gates.**
  - EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK.
  - Traceability: only the `unlock_agent_discoverable_tool:tool_name` misses remain; there are 0 non-tool_name misses.
  - validate_scenario is INVALID. I called `erlbench.validate.validate_scenario` read-only: its 20 errors are all "required document … not found", across this and two sibling difficulties. This is pre-render and not a red.
- **Mechanical sweep** (normalised substring) passes:
  - every basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim;
  - every compute binding has a basis.

### round-1 items: closure check (whole class)

| id | round-1 defect | round-2 state | closed? |
|---|---|---|---|
| F-POL-1 | E3 waited-on state unreachable with more than one portion | E3: "until the most recent prepaid portion that restored nothing to the line when it was applied carries its line restoration entry"; restore: "that one entry covers every portion" | ✓ for E3. **Class not closed:** a new member on E2 (F-POL-7 below) |
| F-POL-2 | E1 sentence ≠ condition | "only once no payout plan change request on file for the loan still shows request status submitted", identical to the condition | ✓ |
| F-POL-3 | designation cap undeclared | overwrite now names the base sentence and restates it with scope | ✓ |
| F-POL-4 | withholding rule ≠ compute | rule tiers (notice/pending/defaulted, arrearage > 0 → /12; active with installment > 0 → installment) = ladder = compute | ✓ |
| F-POL-5 (obs) | rp_paid / pc_lump scope | repair factor removed; pc_lump sums under "a loan holding at most one open record", consistent with the propcharge rule "a borrower holds at most one open record" | ✓ |
| F-POL-6 | SUM rounds rate sums | no SUM over `rate_applied_pct` remains (check_void, release and restore use LATEST; the reset average was removed) | ✓ |
| F-FAC-1 | universal or unreachable tiers | void now immediate, so daily / ≤6 / >6 months and no-accrual tiers are reachable; restore scope "otherwise" is reachable via Property Condition Default (cure allowed before referral); reset Line-of-Credit tiers removed; all new ladders have reachable fall-throughs | ✓ |
| F-FAC-2 | straw-man baselines | release count no longer gated on payments made; reset baseline states the base committed amount and count; release/reset baselines = base method | ✓ |
| F-FAC-3 | realism | repair holdback removed; rate-type day count replaced by a rate-source ladder that tracks the charged rate (reasonable) | members ✓; **class reopened by a new member** (F-FAC-3b) |
| F-FAC-4 | tier collapse / mislabel | premium rate is now the plan rate (no factor); post-cure share relabelled parameter | members ✓; **class reopened** (F-FAC-4b, F-FAC-4c) |
| F-FAC-5 | non-HUD payment rate | release/reset rate = expected_rate_pct + annual_mip_rate_pct; HUD five-year minimum (age 95+); the 90–94 floor removed | ✓ |
| F-FAC-6 | factor-count floors | declared: ceiling 5 (2 method), void 4 (1 method), release 4 (1 method), restore 4 (2 method), designation 5 (1 method), reset 5 (1 method) | declared ✓; **fails again after striking** (F-FAC-6b) |
| T0-1 | "uncashed" unreachable | E2 now keys on a record-visible `request_status withdrawn`; the persona confirms the stop on ask | ✓ (task file) |
| T0-3 | 7,791.42 vs 7,791.40 | the rounding source is removed; re-checked at reveal | see task file |

### new findings (revision_2, charter-global)

**F-POL-7 — SOURCE-POLICY RED: E2's waited-on state can be unreachable (the F-POL-1 class, new member).**
- E2 reads: "The draw ceiling is not worked out until every check draw on the loan whose draw request shows request status withdrawn carries its return entry."
- The only resolving write follows check_void, whose rule says: "The stopped draw check handled is the line-of-credit draw that references the loan's most recent draw request with disbursement method check and request status withdrawn, and it is handled only while no return entry references that draw." The compute agrees: `stop_rq = LATEST(... request_status='withdrawn')` with no exclusion of draws already returned.
- Situation: a loan with two withdrawn check draws. After the most recent one is voided, the rule's target is still that same draw, which now carries a return, so "handled only while no return entry references that draw" stops it. The older stopped check can never be handled, so E2 never holds.
- Consequence: the draw ceiling can never be worked out.
- Not engaged in either task world (task 0 has one withdrawn request).

**F-FAC-3b — SOURCE-FACTOR RED (realism): `hecm_ext_payment_reset.new_payment_start`.**
- Rule: "when at least one queued draw request came through the servicing portal or a signed written form, the first payment is in the second month after the handling month …; when every queued draw request came by phone, the first payment is in the third month after the handling month".
- Whether a pending draw arrived by phone or portal is weighed by the base only for the single-draw phone cap. No HECM servicer sets when a borrower's tenure or term payments start by the channel of an unrelated pending draw request.
- A change takes effect per the plan's own `plan_change_effective_rule` (first_day_of_month_after_processing). The deferral, and its phone-vs-portal split, is a condition the business does not weigh for that quantity.
- The draws are already held in the line by the designation's queued hold.

**F-FAC-4b — SOURCE-FACTOR RED (unreal ladder: two tiers, one treatment): `hecm_ext_check_void.interest_return_months`.**
- Tier 1 ("an interest accrual posted after the check's effective_date and the most recent one is dated no earlier than the same day of the month as that date, the months outstanding later → the accruals posted in the outstanding window plus one") and tier 2 ("the number of those accruals") both compute one quantity: the number of interest accruals posted after the check's date.
- Proof sketch. Let W be the outstanding window (NOW − m months, NOW] and G the gap (check date, NOW − m months], which is shorter than a month. With monthly accruals on the 1st, G holds an accrual exactly when the check's day of month is greater than the handling day. The tier-1 condition is satisfied in exactly that case (for a check not dated on the 1st), and tier 1 then adds that one accrual.
- The rule's own reason for the +1 ("because the monthly accrual has already charged the check's part month") is the definition of the single quantity.
- So the split is a calendar artifact of how the window is drawn (the day of month of the check against the handling day), not a condition a servicer weighs. The two tiers select the same treatment.
- Edge case: a check dated on the 1st enters tier 1 and is over-counted by one.

**F-FAC-4c — SOURCE-FACTOR RED (mislabel): `hecm_ext_payment_release.release_processing_credit` is labelled `parameter`.**
- Its tiers change how the credit is computed: "one twelfth of the latest line growth rate times those months" vs "the latest line growth rate times those days over 365" (month-count vs day-count convention).
- Round 1 treated the same days/365 vs months/12 split as a `method`.

**F-FAC-6b — SOURCE-FACTOR RED (count floors after striking).**
- check_void: interest_return_months struck (F-FAC-4b) → 3 factors (< 4).
- payment_reset: new_payment_start, its only `method`, struck (F-FAC-3b) → 0 method.

**F-XF-1 — SOURCE-FACTOR RED (structure: assembly and baseline sentences naming factor quantities; factors acting only through another factor).** Every member makes a factor document, or the computation document carrying `baseline.rule`, name another factor, against the render contract that the computation document is "silent about any variation" and that factor documents reference none other. Members:
1. **Baselines naming the factors.**
   - check_void: "the interest return rate, the interest months and the interest return method set out below take the place of that starting point"; "the premium months set out below take the place of the months outstanding".
   - payment_release: "the remaining-payment count, the payment timing, the amount kept committed and the processing credit set out below take the place …".
   - reinstatement_restore: "the portions counted, the wait period, the wait credit rate and the share kept back set out below …".
   - payment_designation: "the amounts kept in the line and the designation share set out below …".
   - payment_reset: "the payment count, the start and the withholdings set out below …".
   - (draw_ceiling's baseline is clean.)
2. **Assembly sentences naming factor quantities.**
   - release: "The payment release is the value of the remaining payments times one plus the processing credit rate, less every amount kept committed".
   - restore: "The reinstatement restoration is the portions counted less the share kept back, plus the wait credit, which is the total of every portion … times the wait credit rate … times the wait period".
   - designation: "the designation share is applied to the remainder".
   - check_void interest_return_method tiers: "grown monthly at one twelfth of the interest return rate … compounded over the interest months"; "times one twelfth of the interest return rate … times the interest months". These name the two other factors' quantities.
   - (draw_ceiling and reset assemble generically: "Each amount … their sum", "less every withholding".)
3. **Factors acting only through another factor.**
   - restore_wait_rate × restore_wait_period: a product; each has no effect when the other is 0.
   - restore_cure_holdback is applied to "the portions counted" (restore_cure_scope's quantity).
   - designation_post_cure_share scales the remainder after the four holds.
   - release_processing_credit multiplies the timing- and count-shaped value.
   - check_void interest_return_rate acts only through the method formula with interest_months: it has no effect when interest_months = 0 in the simple or compound tiers.

**Observations (revision_2).**
- `premium_return_cap_months` = 6 returns fewer MIP months than were charged (realism, proprietary; plausible because the MIP was already remitted).
- The queued-earmark and queued-hold tier 2 (phone cap on the total) is distinct from tier 1 only when phone requests total above 15,000.
- The restore holdback is "kept back … until twelve months pass" with no release rule anywhere in the charter.
- No write in any charter sets a processed draw request to `withdrawn` (the extended rule declares it as the record of a stopped check).
- The process tool's enum still accepts "HECM Line of Credit" (F-OBS-3; the reset rule's Line-of-Credit tier is gone).
- The release_count_floor label is borderline (a floor plus the base term formula).
- "Afterwards" in the docstrings (unchanged tool module).

### reveal note and closing (revision_2)

- Both tasks' blind scored values and every factor figure match GT to the cent (see 0.md and 1.md revision_2).
- The difficulty is **not closed**. Remaining charter-global reds:
  - F-POL-7 (the E2 multi-withdrawn-check reachability, the same class as F-POL-1);
  - F-FAC-3b (queued-draw channel deferring the payment start);
  - F-FAC-4b (interest_return_months: two tiers, one counting rule);
  - F-FAC-4c (processing-credit mislabel);
  - F-FAC-6b (check_void and reset below the floors after striking);
  - F-XF-1 (baselines, assembly sentences and factor-through-factor in five policies).
- I ran no gates beyond the coordinator's snapshot script and a read-only `validate_scenario` call to classify the INVALID.

VERDICT revision_2: task0=SOURCE-FACTOR RED task1=SOURCE-FACTOR RED charter=F-POL-7,F-FAC-3b,F-FAC-4b,F-FAC-4c,F-FAC-6b,F-XF-1

## revision_3

### charter_global_frozen (revision_3)

- **Basis.** Written pre-reveal from the charter, schema, tools, DSL and `audits/render_source/XF_recipe.md` (read in full).
  - Auditor: erl-task-policy-audit, round 3.
  - Gate line: `REWORK round 3: gates 7/7 green` ✓.
  - Snapshot: `snapshot_r3.txt` (via `/tmp/erl0064_coord/snapshot.sh … 3`).
- **Hashes against r2.**

| file | r2 | r3 | consequence |
|---|---|---|---|
| hecm.extended.yaml | d8346da9bf969900 | **95b4c14cc97bf7ce** | changed → charter-global sections re-derived in full |
| task_tools.py | 4da8d29f84fb4fe0 | **7b485dfa95794d49** | changed |
| view 0 | 8cf72c089d71ccd3 | 8cf72c089d71ccd3 | unchanged |
| view 1 | f7bfa5f4610cb27d | **882e35383f674ed9** | changed |

- **Base copy.** Still verbatim.
- **Gates.**
  - EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK.
  - Traceability: only the unlock tool-name misses remain (0 non-tool_name misses).
  - validate_scenario is INVALID. I re-checked it read-only: all 20 errors are "required document … not found", which is pre-render and not a red.
- **Tool change.** `process_payout_plan_change_72a1f37c` now returns "Error: …" and books nothing for `new_plan` "HECM Line of Credit" or "HECM Fixed-Rate Single Disbursement", and its docstring states this.
  - The check is on the tool's own input domain (which plan it writes), not on a prerequisite state, so the tool layer still judges no prerequisite.
  - It closes F-OBS-3: only convert can now mark a Line-of-Credit change processed.
  - The uuid8s are unchanged and independent.
- **Mechanical sweep.**
  - Every compute_basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim in its rule.
  - No compute binding lacks a basis.
  - No "set out below" or "take the place of" phrase remains (0 hits).
  - No "as … figures it" or "sized by its own" phrase.

### round-2 items: closure (whole class)

| id | round-3 state | closed? |
|---|---|---|
| F-POL-7 | check_void rule: "Cedarline takes a stop on a draw check only while no other stopped draw check on the loan awaits its return entry, so a loan carries at most one stopped draw check awaiting its return entry at a time, and every stopped draw check a loan ever has is handled under this rule in turn." Under this invariant, the draw behind the most recent withdrawn request is the only one that can lack a return, so E2 is always reachable by the void. The other three edges were re-checked for the same unreachable-state shape: E1 (one request per convert call, by id), E3 (most recent portion, one entry covering all), E4 (the user's signed request) | ✓ |
| F-FAC-3b | new_payment_start removed; the reset start is the base "month after the handling month", restated in the rule | ✓ |
| F-FAC-4b | interest_return_months ladder removed; "accrual months charged" is now one baseline quantity (whole months to the latest accrual, + 1) | ✓ |
| F-FAC-4c | release_processing_credit relabelled `method` | ✓ |
| F-FAC-6b | check_void 4 factors (2 method: interest_compounding, premium_compounding); reset 5 (1 method: arrearage withholding, spread /12 vs pass-through, an honest method) | ✓ for these two; but see F-FAC-6c |
| F-XF-1 | XF recipe points 1–9 checked on all six policies (table below) | ✓ |

### XF recipe, point by point (all six policies)

| point | ceiling | void | release | restore | designation | reset |
|---|---|---|---|---|---|---|
| 1 baseline defines every combined quantity, names no factor | ✓ amounts kept = 0.00 | ✓ interest rate = note, premium months = accrual months, compounding = 0.00 | ✓ count, timing adj., credit, kept committed = 0.00, standard value | ✓ portions = principal, kept back = 0.00, rate = latest growth, period = days/365 | ✓ amounts kept = 0.00 | ✓ committed, rate, count, withholdings = 0.00 |
| 2 each factor owns one quantity ("In place of …" / "Added to …") | ✓ | ✓ (premium_compounding derives its own "premium-correctable months" from the baseline accrual months and the shared cap parameter; it reads no factor binding) | ✓ timing and credit act on "the standard value" | ✓ holdback now on every portion, not on the counted portions | ✓ post-cure share became an additive hold | ✓ |
| 3 solo and removal tests | per-task files: every factor moves the result alone and on removal | ✓ (task 0) | ✓ (task 0) | ✓ (task 1) | ✓ (task 1) | ✓ (task 1) |
| 4 combination stated once, generically, order fixed | ✓ subtract, then floor | ✓ additions commute; one rounding | ✓ add/subtract, then floor | ✓ then floor | ✓ then floor | ✓ then floor |
| 5 no cross-policy definition | ✓ | ✓ | ✓ | ✓ | ✓ | obs: the escrow sentences describe their purpose as "the tax bill after the one the designated amount keeps in the line". This is descriptive only: the quantity is defined by its own window total/12 |
| 6 overwrites restate, then scope | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (start no longer retired; restated) |
| 7 quotes and rounding placement | ✓ arrangement RND stated | ✓ once | ✓ once | ✓ once | ✓ once | ✓ arrearage /12 rounded as stated; escrows unrounded as stated |
| 8 branches (absent, none, 0) | ✓ | ✓ "a loan with no such draw has nothing to settle"; 0 accrual months | ✓ growth rate 0 when none | ✓ no cured case → 0; no portion → nothing | ✓ sentinel '1900-01-01' → "otherwise nothing" | ✓ "none when the payment count is 0" |
| 9 docstrings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (new error branch stated and implemented) |

### new findings (revision_3)

**F-FAC-4d — SOURCE-FACTOR RED (mislabel: a threshold labelled `method`).** Members:
- `hecm_ext_payment_designation.designation_queued_hold`;
- `hecm_ext_draw_ceiling.queued_request_earmark`.

The problem:
- Tier 1 is "the full total of every queued draw request" and tier 2 is "their total capped at the plan's phone_draw_max_amount". That is one formula, min(total, cap), with the cap substituted: ∞ vs 15,000. Tier 3 is 0.
- The skill names a substituted threshold as the `parameter` case.
- I recorded this label as "borderline (obs)" in revisions 1 and 2. I raise it now because (a) the coordinator asked specifically for a method-shape check, and (b) after the post-cure share became an additive parameter hold in round 3, the designation's whole `method` count rests on this one factor.

**F-FAC-6c — SOURCE-FACTOR RED (count floor).** With F-FAC-4d, `hecm_ext_payment_designation` has 0 honest `method` factors (its 5 factors: tax, insurance, inspection and post-cure holds are parameters; the queued hold is a threshold). The draw ceiling keeps arrangement_installment_reserve as its honest method.

**Observations (revision_3, not grounds for rework).**
- **Restore holdback.** It is a percentage of every restores_line-false portion, even when the cure scope counts only principal or principal + interest. Under those scopes it can withhold from money not being restored; the floor at 0.00 absorbs it. This is an independence artifact; not engaged in task 1 (scope = all).
- **Release timing adjustment.** It is computed on the standard-count value, while the released payments use the five-year-floor count. That is coherent by the rule's letter but not the exact present value.
- **Void "accrual months charged".** It over-counts by one for a check dated on the 1st (MONTHS to the latest accrual, plus one).
- **Insurance reserves.** The draw ceiling still reserves hazard only when both hazard and flood were advanced, while the designation now holds both.
- **Reset escrows.** They stack with the designation's line holds and the arrearage withholding on the same advanced bills (stated by purpose; plausible).
- **Void interest_compounding tier 2.** A first-order approximation is used for 2–6 months against exact compounding above 6. This is a proprietary convention; the tiers are distinct in method.

### reveal note and closing (revision_3)

- Both tasks' blind scored values, factor figures and edge-skip figures match GT to the cent.
- Every round-2 red is closed across its class: F-POL-7, F-FAC-3b, F-FAC-4b, F-FAC-4c, F-FAC-6b and F-XF-1 (recipe points 1–9 on all six policies).
- Nothing regressed.
- The difficulty is **not closed**. One red class remains: F-FAC-4d (two queued-request factors labelled `method` whose tiers only substitute a cap), and its consequence F-FAC-6c (the designation has no honest `method` factor). This was observed as borderline in r1 and r2; it is raised in r3 because of the method-shape check and the designation's method count.

VERDICT revision_3: task0=SOURCE-FACTOR RED task1=SOURCE-FACTOR RED charter=F-FAC-4d,F-FAC-6c

## revision_4

### charter_global_frozen (revision_4)

- **Basis.** Written pre-reveal.
  - Gate line: `REWORK round 4: gates 7/7 green` ✓.
  - Snapshot: `snapshot_r4.txt` (via `/tmp/erl0064_coord/snapshot.sh … 4`).
- **Hashes against r3.**

| file | r3 | r4 | consequence |
|---|---|---|---|
| hecm.extended.yaml | 95b4c14cc97bf7ce | **482fbbf0e4ba6859** | changed → re-derived in full |
| task_tools.py | 7b485dfa95794d49 | 7b485dfa95794d49 | unchanged → r3 tool conclusions carry forward |
| view 0 | 8cf72c089d71ccd3 | 8cf72c089d71ccd3 | unchanged |
| view 1 | 882e35383f674ed9 | 882e35383f674ed9 | unchanged |

- **Base copy.** Verbatim.
- **Gates.**
  - EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK.
  - Traceability: only the unlock tool-name misses remain (0 non-tool_name misses).
  - validate_scenario is INVALID with 20 of 20 errors "required document not found". This is pre-render, re-checked read-only, and not a red.
- **Mechanical sweep.**
  - Every basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim in its rule.
  - No compute binding lacks a basis.
  - 0 "set out below" or "take the place of" phrases.

### round-3 items

**F-FAC-4d — closed.** `designation_queued_hold` and `queued_request_earmark` are now labelled `parameter`. Their tiers are a capped vs uncapped total, a threshold substitution, so the label is now honest.

**F-FAC-6c — closed.** The new method factor is `designation_inspection_hold` (and, in the draw ceiling, `occupancy_inspection_reserve`).
- Tiers:
  - overdue or in absence_monitoring → "schedule basis: twice the profile plan's occupancy_inspection_fee";
  - current with fees in window → "ledger basis: the occupancy inspection fees actually posted in the twelve-month window";
  - otherwise 0.
- **Method shape.** The two non-zero tiers compute the quantity from different sources and algorithms: a plan-parameter multiple vs a ledger sum. That is an honest `method`.
- **Realism.** "What the last cycle actually cost" is a natural reserve basis.
- **Independence.** It reads only its own bindings (`res_status`, `res_fee`, `insp_fees`), adds to the baseline "amounts kept", and names no other factor.
- **Resulting counts:**

| policy | factors | method | parameter |
|---|---|---|---|
| draw ceiling | 5 | 2 (arrangement, inspection) | 3 |
| check_void | 4 | 2 | 2 |
| payment_release | 4 | 2 | 2 |
| reinstatement_restore | 4 | 2 | 2 |
| payment_designation | 5 | 1 (inspection) | 4 |
| payment_reset | 5 | 1 | 4 |

- I re-checked the method shape of every method factor:
  - arrangement: whole arrearage vs installment-based min;
  - void interest and premium compounding: exact vs first-order;
  - release timing and processing credit: month vs day convention;
  - restore cure scope and wait period;
  - reset arrearage withholding: spread /12 vs pass-through.
  All are honest.

**XF recipe (points 1–9).** Re-checked on all six policies against the r4 text. Every point still holds:
- the changed insurance-reserve and inspection sentences use "Added to the amounts kept";
- baselines are unchanged and name no factor;
- the combination sentences are unchanged.

**Same-day tie rules where a "latest" pick exists.** Every LATEST/XLATEST pick now carries a stated uniqueness or tie rule:

| policy | pick | rule |
|---|---|---|
| check_void | stopped check | "most recently created draw request, by its created_at timestamp" |
| check_void | its draw | one draw per request (base "Each request is disbursed at most once") |
| check_void, release, restore | latest interest accrual and growth credit | "Interest accruals and line growth credits each post once a month, so the most recent one is a single entry" |
| check_void | latest MIP accrual | used only as a date comparison, so a tie cannot change the result |
| restore, designation | cured case | "the case named by the loan's most recent cure confirmation notice; a loan has at most one open maturity case at a time, so its cure confirmation notices fall on different dates" |
| release | request | "A loan carries at most one submitted payout plan change request at a time" |
| reset | request | "a loan carrying at most one submitted payout plan change request at a time" |
| restore | most recent restores_line-false portion | the single entry covers every portion |

**Fixed round-3 observations.**
- The void's accrual months are now the calendar-month difference from the check's month to the latest accrual's month. This closes the over-count on checks dated the 1st.
- The draw ceiling's insurance reserve now holds hazard plus flood, the same as the designation.

**Remaining observations (unchanged from r3; not grounds for rework).**
- The restore holdback is a percentage of every portion, regardless of cure scope.
- The release timing adjustment is computed on the standard-count value.
- The reset escrow sentences describe their purpose by reference to the designated amount.

**No new defect and no regression found.**

### reveal note and closing_checklist (revision_4)

Both tasks' scored values and every factor figure match GT to the cent.

- [x] Per-task files 0.md and 1.md, plus `_difficulty.md`. Revisions 1–4 are appended, and the older text is untouched apart from the r1 freeze-timestamp correction disclosed in place.
- [x] Scopes are disjoint and complete: task 0 = {draw_ceiling, check_void, payment_release}; task 1 = {payment_reset, payment_designation, reinstatement_restore}. Task tools are closed, and the uuid8s are independent and unchanged.
- [x] Each tree has 2 prerequisite problems with 2 value_input edges, an owner=user write, and no cycle. The difficulty-wide graph is acyclic. Every prerequisite sentence is in the state form, matches its condition, and is reachable by exactly one write.
- [x] Every computation has a self-sufficient baseline and 4–6 factors with ≥2 `parameter` and ≥1 `method`. Each task has a multi-source factor and a cross-difficulty factor (task 0: propcharge and residency; task 1: propcharge, residency and maturity). Every factor bears weight against an honest baseline, and each whole baseline differs from gold. The XF recipe holds, and the tie rules are stated.
- [x] Gates re-run on the final form by the coordinator's snapshot r4: all green, apart from pre-render traceability (unlock tool-name) and validate "required document" errors.

**Status.** The difficulty passes the source-layer audit at revision_4. The remaining observations listed under revision_4 are not grounds for rework.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (revision_5)

- **Basis.**
  - Gate line: `REWORK round 5: gates 7/7 green` ✓.
  - Snapshot: `snapshot_r5.txt` (via `/tmp/erl0064_coord/snapshot.sh … 5`).
  - Read in full: `audits/render_source/hecm_line_draws_and_plan_servicing/render_r1.md` and `XF_recipe.md`.
- **Hashes against r4.**

| file | r4 | r5 | consequence |
|---|---|---|---|
| hecm.extended.yaml | 482fbbf0e4ba6859 | **8488c479a4d77157** | changed → re-derived in full |
| task_tools.py | 7b485dfa95794d49 | **68143fd08aec008a** | changed |
| view 0 | 8cf72c089d71ccd3 | 8cf72c089d71ccd3 | unchanged |
| view 1 | 882e35383f674ed9 | 882e35383f674ed9 | unchanged |

- **Base copy.** Verbatim.
- **Gates.**
  - EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK.
  - Traceability: only the unlock tool-name misses remain (0 non-tool_name misses).
  - validate_scenario is INVALID with 6 of 6 errors "required document not found" (documents are now 300). Checked read-only; pre-render; not a red.
- **Mechanical sweep.**
  - Every basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim in its rule.
  - No compute binding lacks a basis.
  - 0 "set out below" or "take the place of" phrases.
- **Auditor's note on missed items.** Two of the three render_r1 items were already in my revision-1 notes, but only as observations:
  - `rule_compute_equivalence` item 8 recorded the anniversary/MONTHS divergence;
  - `policy_conflict_scan` recorded that "no extended policy or tool handles a change from one scheduled plan to another" and that the base ordering sentence "grounds no declared edge".
  - Both should have been raised as SOURCE-POLICY RED. Each can be shown with a constructed situation, the same way I demonstrated F-POL-2 and F-POL-7.
  - The third item (overwrite #1 redefining the first-year draws for every draw) I accepted in r1, and that was wrong.
  - This round therefore judges every base clause of every referenced base policy against every extended rule, not only the declared overwrites (sweep below).

### render_r1 items: closure (whole class)

**Mismatch 1 (anniversary fallback vs MONTHS) — closed.**
- Draw-ceiling overwrite #3 now names the base anniversary sentence. Its replaced_by restates it, then scopes a ceiling-only rule: "the first anniversary is reached once first_year_period_months whole calendar months have passed since the closing date, a whole month being complete on the later month's day with the closing date's day number, or on the first day of the following month when that month has no such day number."
- That is exactly `MONTHS` (a day-number shortfall subtracts one month):
  - closing 2024-02-29: on 2025-02-28, MONTHS = 11 and the rule says not yet (complete on 03-01);
  - on 2025-03-01, MONTHS = 12 and the anniversary is reached.
- **Class sweep** (other date-boundary phrases evaluated through MONTHS):
  - payment_reset now states the same whole-month convention for the borrower's age ✓;
  - the check_void accrual months are a pure month-index difference (`MONTHS('2000-01-01', ·)`), so there is no day boundary ✓;
  - the "after the same day of the month N months before the handling date" windows give, through `MONTHS(d, NOW) < N`, the last-day-of-month fallback that is the natural reading when that day does not exist ✓.
- Two silent conventions remain (observation O-5a below).

**Mismatch 2 (payment_reset vs the in-force base release clauses) — closed.**
- Reset rule: "This rule processes a change only for a loan whose current plan pays no scheduled payments, such as the HECM Line of Credit, so no payment release arises and the whole available line after any release is the loan's available_line; a change from a plan that pays scheduled payments needs its payment release booked first and is not processed under this rule."
- The baseline states "the new scheduled payment is 0.00 for a loan outside this rule's scope", and the compute has `in_scope = F('scheduled_payment_amount') <= 0`.
- The tool returns "Error: … nothing was booked" when the loan's `scheduled_payment_amount` > 0, and its docstring says so.
- Within scope, the base "whole available line after any release" equals `available_line`, so the base sentence and the extended rule agree.
- The base processing-order sentence (release, then commitment) now only governs changes that no extended policy processes. A scheduled → scheduled change has no tool in this difficulty and falls outside every claimed policy, so it is not a contradiction.
- The tool's refusal is a scope gate on its own input (the loan's current plan), not a check of the task's prerequisite edges (E3 and E4). The tool layer still judges no prerequisite.

**Non-blocking item (overwrite #1 redefining the first-year draws) — closed.**
- The replaced_by now keeps the base clause verbatim for every draw ("…plus hecm_msr_first_year_draws plus the requested draw…").
- It defines "the draw ceiling's own first-year room" and "the draw ceiling's first-year draws" only for a ceiling-sized request.
- The base `formula` and measure stay in force for other draws, so there is one definition per scope and no general redefinition.

**Sweep: every base clause against every extended rule.** No undeclared contradiction remains. Each referenced base policy, sentence by sentence:

| base policy | extended policy | result |
|---|---|---|
| hecm_evt_loc_draw | draw_ceiling | Three sentences are declared (first-year limit, min/available-line cap, anniversary). Inherited without conflict: plan eligibility, active, request on file, maturity suspension, phone cap (the request is filed via portal), wire minimum, once per request, posting pair, processing days, set-aside exclusion. |
| hecm_evt_disbursement_return | check_void | Three sentences are declared (full-amount reversal, void waiting days, "never exceeds"). Inherited: the returned bank transfer, the set-aside refund, "a returned scheduled payment is not reversed". The `returned_disbursement_line_credit` condition is restated. |
| hecm_evt_servicing_fee | check_void | It is in refs, but no sentence of it is touched. |
| hecm_payment_plan_change | payment_release | The release-amount sentence is declared (age, five-year floor, timing adjustment, credit, kept committed). The monthly rate and "made at the start of each month" sentence is in force, and the timing adjustment works through the declared release-amount sentence. The Line-of-Credit field updates, fee, once-only and signed request are restated or inherited. |
| hecm_payment_plan_change | payment_designation | The Modified committed-amount cap is declared. |
| hecm_payment_plan_change | payment_reset | The new-payment sentence is declared (age, floor, withholdings). The start month is restated. "after any release" and the processing order are reconciled by the scope sentence. The term bounds, signed request and once-only are inherited. |
| hecm_evt_prepayment | reinstatement_restore | The due-and-payable "nothing is restored" sentence is declared. The active-loan restore sentence is untouched (it is about active-loan prepayments). |
| hecm_evt_line_growth | reinstatement_restore | "growth stops for good" is not contradicted: the wait credit is a credit on the restoration, not a `hecm_line_growth` posting. |

### other checks (revision_5)

- **XF recipe points 1–9.** Re-checked on all six policies.
  - The new reset scope sentence and the out-of-scope 0.00 are stated in the baseline (point 8).
  - The anniversary replaced_by restates the base sentence before its scope (point 6).
  - Everything else is unchanged from r4 ✓.
- **Tie rules for "latest" picks.** Unchanged from r4 ✓.
- **Factor structure.** Unchanged from r4. Draw ceiling, void, release, restore, designation and reset are 5/4/4/4/5/5 factors, each with ≥2 parameter and ≥1 honest method ✓.

### observations (revision_5; not grounds for rework)

- **O-5a.** Two whole-period conventions are left unstated in their own rules, although payment_reset now states the same convention:
  - payment_release "the whole years from the closing date to the handling date" (age);
  - reinstatement_restore "whole calendar months … since the cured case's closed_date" (wait period).
  The compute uses `MONTHS`. These matter only for a 29th–31st boundary day, and neither task world touches one (closing 2023-10-12 / 2023-09-14; closed 2026-05-15; handling date the 15th).
- **O-5b.** For a Feb-29 closing, the ceiling's anniversary (03-01) falls one day after the base anniversary (02-28) that governs ordinary draws. This is declared and scoped.
- **O-5c.** The reset scope is the loan's `scheduled_payment_amount` > 0 (compute and tool), while the rule speaks of a current plan that "pays scheduled payments". A Term or Modified Term plan past its last payment keeps a positive amount on record, which is consistent with the plan-type reading of the rule. Such a loan's release is 0 anyway.
- **O-5d.** A stopped-check settlement posts its interest and premium return as a `loc_draw` reversal. So the base `hecm_msr_first_year_draws` (for ordinary first-year draws) and the outstanding-interest and outstanding-MIP measures (for later prepayment allocation) see an amount larger than the draw, and buckets that were not reduced. This is a cross-policy interaction, not scored in this difficulty.
- **Carried from r4:** the restore holdback is a percentage of every portion; the release timing is computed on the standard-count value; the reset escrow purpose phrasing.

**No new red and no regression.**

### closing (revision_5)

Every render_r1 item is closed across its class. No base clause is contradicted without an overwrite, and nothing regressed. Both tasks pass all four relationships, and the r4 closing checklist stands with the r5 hashes above.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global (revision_6)

- **Basis.**
  - Gate line: `REWORK round 6: gates 7/7 green` ✓.
  - Snapshot: `snapshot_r6.txt` (via `/tmp/erl0064_coord/snapshot.sh … 6`).
  - Read: `audits/render_source/hecm_line_draws_and_plan_servicing/render_r2.md`.
- **Hashes against r5.**

| file | r5 | r6 | consequence |
|---|---|---|---|
| hecm.extended.yaml | 8488c479a4d77157 | **c1ad45f0c61b5e3f** | changed → re-checked |
| task_tools.py | 68143fd08aec008a | 68143fd08aec008a | unchanged |
| view 0 | 8cf72c089d71ccd3 | 8cf72c089d71ccd3 | unchanged |
| view 1 | 882e35383f674ed9 | 882e35383f674ed9 | unchanged |

- **Base copy.** Verbatim.
- **Gates: all green.**
  - EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK.
  - **TRACEABILITY OK** (0.json 22/0, 1.json 26/0).
  - **validate_scenario VALID**: 358 documents and 0 errors when re-run read-only.
- **Mechanical sweep.**
  - Every overwrite superseded_clause/replaced_by, compute_basis, baseline sentence and prerequisite policy_source is verbatim in its rule.

**The whole-month / whole-year class is closed.** Every `MONTHS`-based count in the charter now has its convention stated in its own rule:

| policy | count | how its convention is stated |
|---|---|---|
| draw_ceiling | ceiling anniversary (`before_anniv`) | "a whole month being complete on the later month's day with the closing date's day number, or on the first day of the following month when that month has no such day number" (since r5) |
| payment_release | age (`age_now`, `n_rel`) | **new**: "(whole calendar months between two dates are complete on the later month's day with the same day number as the earlier date, or on the first day of the following month when that month has no such day number, and whole years are twelve whole months)" |
| payment_release | processing-credit months | **new**: "the whole calendar months from the request_date … to the handling date, counted in the same way" |
| reinstatement_restore | wait period (`lag_period`) | **new**: "counts the wait in whole months (whole calendar months between two dates are complete on the later month's day with the same day number as the earlier date, or on the first day of the following month …)" |
| payment_reset | age | stated (since r5) |
| check_void | accrual months | a calendar-month-index difference (`MONTHS('2000-01-01', ·)`), "the number of calendar months from the month of … to the month of …", so there is no day boundary |
| windows (`within_months`; designation `pcd_cured` `MONTHS(…) < 12`) | "after the same day of the month N … months before the handling date" | MONTHS gives the natural last-day fallback (see r5) |

Each stated convention is exactly `MONTHS` (a day-number shortfall subtracts one month).

**Render note 1 is closed.** reinstatement_restore's `baseline.params` is now `[]`. `restoration_grace_months` lives only in the wait-period factor's rule text and ladder. Every remaining baseline param in the other policies appears in its baseline rule.

**Nothing else changed or regressed.**
- Factor counts are unchanged (5/2, 4/2, 4/2, 4/2, 5/1, 5/1 factors/method).
- The XF recipe, tie rules and overwrite sweep are unchanged from r5.
- Scored values, evaluated through the DSL on the unchanged views plus hand-applied preceding writes:
  - task 0: void 6,276.67, release 34,892.19, ceiling 179,759.62;
  - task 1: restore 1,933.62, designation 169,078.82, payment 2,757.72.
  These match r5 and GT.
- The revision_5 observations O-5a (now closed), O-5b, O-5c and O-5d, and the carried r4 items, stand as observations.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
