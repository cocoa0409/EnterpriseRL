# Policy-task audit — service_contract_claims_and_cancellations / charter-global

## charter_global_frozen

- Auditor: independent audit agent (erl-task-policy-audit), round 1. Written 2026-10-06, before any task's GT was revealed; nothing in this section is derived from a revealed GT.
- Freeze hashes (sha256, re-computed on disk and matching the brief's SHA256SUMS):
  - `warranty.extended.yaml` 572ab380dcaf475d6f48c5e6bbfed8aa570bdb8a94c2b6d8fc00bec3c202f5c5
  - `task_tools.py` 1842fa485fdae3fb79fe21526deb63a40449d460a40a9d8dfe610165471f091d
  - `task_0.view.json` 279a5a2c04c60b0f16cb378f7da53aa1945b0c8a6c63dab770927282265c5813 (`sha256sum -c` OK)
  - `task_1.view.json` bb7abced0db9946ed936ddbdb6424fe7ad356c927ef8838415277974ca02d6a9 (`sha256sum -c` OK)
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/warranty.yaml`, the variant parameters and `purchase_limited_warranty` rule in `blueprint/products/purchase.yaml`, the whole extended charter, `task_tools.py`, the two masked views. The DSL semantics (MONTHS, DAYS, COUNT/LATEST windows, CFIELD/CPARAM/X* customer scoping) were read from `skills/erl-task-instantiate/scripts/check_compute.py` (function bodies only).
- Masked and not read: `tasks/0.json`, `tasks/1.json` (every GT field), the scenario `worklog.md`, all audit files other than these. No recursive grep touched `tasks/`.
- Entry conditions (Step 0): the gate snapshot came with the brief: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; check_traceability is deferred until the KB is published. The masked views came with their hashes. Input complete.

### policy_conflict_scan

- Base copy: every top-level key of `warranty.extended.yaml` other than `extended_policies` is identical to `blueprint/products/warranty.yaml`. A parse comparison and a text comparison both match.
- Extended policies (7), each with a distinct `(target_tool, computes)`:
  | policy | subject | target_tool (owner) | computes |
  | --- | --- | --- | --- |
  | warranty_ext_stack_remainder_authorization | warranty_claim_adjudicated | authorize_stack_remainder_2296c771 (agent) | approved_amount |
  | warranty_ext_rental_reimbursement_settlement | warranty_benefit_reimbursed | file_rental_reimbursement_5fdd83af (user) | reimbursement_amount |
  | warranty_ext_cancellation_settlement | warranty_contract_cancelled + refund | cancel_plan_with_refund_1804bd93 (agent) | refund_amount |
  | warranty_ext_claim_overpayment_recovery | warranty_claim_payment_recovered | recover_overpaid_claim_bcfb33cc (agent) | recovery_amount |
  | warranty_ext_diagnostic_time_payment | warranty_claim_paid | pay_diagnostic_time_6cc9f33c (agent) | payment_amount |
  | warranty_ext_release_repair_payment | warranty_claim_paid | pay_repair_facility_1c2b8918 (agent) | payment_amount |
  | warranty_ext_trip_interruption_reimbursement | warranty_benefit_reimbursed | file_trip_interruption_claim_d37559b2 (user) | reimbursement_amount |
- Overlapping subjects:
  - Diagnostic and release both book `warranty_claim_paid`. They are separated by the rule's object: diagnostic time vs repair work on the most recent approved decision. Two distinct tools exist, and release's prerequisite sentence fixes their order.
  - Rental and trip both book `warranty_benefit_reimbursed`. They are separated by benefit type.
  - No two policies decide the same quantity on the same trigger.
- Time anchors: each policy anchors at NOW or at its own decision date. No conflicting anchors were found.
- Cross-category reads:
  - stack reads purchase (limited-warranty claims, registration state) and maintenance;
  - rental reads purchase;
  - cancellation reads purchase and tradein;
  - diagnostic, release and trip read the purchase `variant_name`.
  - All of these are declared in `cross_category`.
- Scopes, derived from the prerequisite graph and the two worlds, to be confirmed against `charter_scope` after the reveal:
  - Tree A = {cancellation (root), stack, rental}, played by task 0.
  - Tree B = {trip (root), release, diagnostic, recovery}, played by task 1.
  - The two trees are pairwise disjoint and together cover all 7 extended policies.

### rule_compute_equivalence

A script checked every `compute_basis` quotation verbatim against its own normalised `rule`, and every compute binding for a basis entry (temporary script, since removed). Result:

- **One quotation is not in its rule.** `warranty_ext_rental_reimbursement_settlement.compute_basis.lw_repair_estimate` = "where the limited warranty decision's estimate is at or above the major-repair estimate and the repair is on the engine or the transmission". The rule's night-cap sentence reads "... and the plan has approved repairs on the same vehicle system at least twice within the last twelve months ...". The "engine or the transmission" condition is in neither the rule nor the compute (`night_cap` tests `system_repairs_12m >= K('repeat_failure_min_repairs')`). It is a stale quotation: rule and compute agree with each other, so no scored value differs. Recorded as observation O-1.
- Every other basis quotation is verbatim in its own rule. Every `baseline.rule` sentence is verbatim in its rule. Every `overwrite.replaced_by` is verbatim in its extended rule, and every `superseded_clause` is verbatim in the cited base rule.
- Ladders against rule and compute: for each of the 39 factors, every ladder tier is a sentence of the rule and a branch of the `decides` binding, and the reverse also holds. Checked by reading each factor against its rule paragraph.
- Compute details checked against the rule. All are consistent except where noted:
  - stack: the deductible comes first; wear, repeat and notice shares are multiplicative; the tax is added last; the result is then capped and rounded once ("The per-visit limit and the coverage remaining are compared with the figure after the tax").
  - rental: credit, then tax, then share; floored at 0.
  - cancellation: `full_refund` (flat reason or free-look with no claim paid), use start/end, the state time basis, the fee times its share, claims_charge composition, and rounding once.
  - recovery: the `in_window` gate; error × aged × collection + handling.
  - diagnostic: (system + program hours) → long adjustment → repeat share; × rate; min coverage.
  - release: refigure → × (1−allowance)(1−core) × comeback × (1+uplift)(1+interest); min coverage.
  - trip: `trip_end_date`, `start_adjustment`, cap, allowance, recent share, coverage share.
- Compute detail that goes beyond the rule wording (observation O-2): cancellation `other_delivered = CFIELD('purchase','handover_date',status='delivered')` does not exclude the covered vehicle's own purchase order, although the rule says "another Kestrel purchase order". This matters only where the covered vehicle's own order is still `delivered` and not traded in. Neither world is in that state (task 0: covered order `completed` and traded in; task 1 does not use this policy).

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- uuid8s: 2296c771, 5fdd83af, 1804bd93, bcfb33cc, 6cc9f33c, 1c2b8918, d37559b2. Each is used once. They share no common prefix or suffix and show no sequential or adjacent pattern, so none looks batch-derived.
- Tool bodies:
  - Every tool books exactly what its docstring says and validates no policy condition: no status check, no prerequisite check, no amount computation (module docstring: "none of them checks a policy condition or computes an amount").
  - The tools that touch `coverage_remaining` do so as stated: stack leaves it unchanged; recovery adds the recovered amount; diagnostic and release subtract their payment; rental and trip leave it unchanged.
  - `cancel_plan_with_refund` sets status `cancelled` and `closed_date = effective_date`, and books a refund entry with `refund_payee="customer"`.
- Docstring ordering words: one only, in `authorize_stack_remainder_2296c771` (task_tools.py line 17): "The contract's coverage remaining does not change until the facility is paid." This describes the tool's own effect, not a position in a sequence, and names no tool. Recorded as observation O-3. No other before/after/first/then/once appears outside the denial-code definitions.

### prerequisite_graph

| # | blocked policy | problem | kind | gate (binding) | form | policy_source verbatim in own rule |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | rental | stack | value_input | system_repairs_12m (exists) | state | yes |
| E2 | cancellation | stack | value_input | approved_total (exists) | state | yes |
| E3 | cancellation | rental | value_input | benefits_paid (exists) | state | yes |
| E4 | diagnostic | recovery | state_gate | `service_contract_transactions.event_type` | state | yes |
| E5 | release | recovery | value_input | coverage_now (exists) | state | yes |
| E6 | release | diagnostic | value_input | coverage_now (exists) | action + fallback_reason | yes |
| E7 | trip | release | value_input | ro_paid_total (exists) | action + fallback_reason | yes |

- `prerequisite` is filled in on every extended policy (`[]` on stack and recovery). Every `problem` names an extended policy of this file, never a base policy and never itself.
- The graph is acyclic. Topological orders: stack → rental → cancellation, and recovery → diagnostic → release → trip.
- `fallback_reason` is present exactly on the two action-form edges (E6, E7).
- `resolved_by` equals the depended-on policy's `target_tool` on every edge.
- E4's `gate` is a field name rather than an eligibility id; the extended policy carries no `eligibility` list. The gate the sentence describes is real: the diagnostic payment is not booked while an overpaid payment lacks its recovery. Observation O-4.
- No `prerequisite` text uses authoring-viewpoint phrasing ("in this task", "at the opening", and so on).
- `condition` against sentence:
  - E2's condition reads "covered less than the repair estimate", while its sentence says "left partly unpaid". A wholly denied limited-warranty decision (covered 0) satisfies the condition, but "partly" arguably excludes it. Neither world has a denied limited-warranty decision, so there is no consequence here. Observation O-5.
  - E3's condition ("every repair order whose limited warranty decision is approved with rental days above zero") has the same scope as its sentence ("each repair order whose limited warranty decision recorded approved rental days"). Neither is restricted to the latest decision or to the repair order being handled. Its consequence in task 0 is demonstrated in `0.md` (finding F-0-1).

### prerequisite_sentences

Four-point test on each edge:

- **E1** "A rental car reimbursement is booked only after the repair order it belongs to carries an approved KestrelCare authorization on the plan."
  - Connective "only after". The state is record-visible (a `warranty_claim_adjudicated` entry, decision approved, on that repair order). No tool, id or snake_case token.
  - Exactly one write of this difficulty books an adjudication: `authorize_stack_remainder_2296c771`. Derivation: sentence → records (the repair order lacks an approved entry) → the stack rule ("the KestrelCare authorization of the same repair order settles what the plan still owes on it") → the stack authorization. Single reading. PASS.
- **E2** "A cancellation refund is fixed only after every repair order that a limited warranty decision for the holder left partly unpaid carries a KestrelCare authorization decision on the plan."
  - "only after"; state form; one write (the stack authorization). PASS, with the scope caveat in O-5.
- **E3** "A cancellation refund is not worked out until each repair order whose limited warranty decision recorded approved rental days carries a rental car reimbursement entry on the plan."
  - "not ... until"; state form. One write books `benefit_type=rental_car`: `file_rental_reimbursement_5fdd83af`. The derivation reaches the rental rule, a customer-filed reimbursement.
  - The sentence quantifies over **every** such repair order. Whether the tree's writes can satisfy it depends on the world; see task 0.
  - As a charter sentence: PASS.
- **E4** "A diagnostic time payment is not booked until every claim payment on the plan that exceeds the approved amount of the decision it settled carries a recovery entry."
  - State form. One write books a recovery: `recover_overpaid_claim_bcfb33cc`. PASS.
- **E5** "The payment of an approved decision is worked out only after every claim payment on the plan that exceeds the approved amount of the decision it settled carries a recovery entry."
  - State form; one write (recovery). PASS.
- **E6** "The repair payment on a decision is figured only after the facility's diagnostic time on that repair order has been paid."
  - Action form in business words. Test of `fallback_reason`: the diagnostic payment and the repair payment leave identical `warranty_claim_paid` rows (same repair order and source decision; the tool bodies differ only in the hidden `make_id` salt). So a state such as "the repair order carries a claim payment" would also be met by the release payment itself. The fallback is justified. PASS.
- **E7** "A trip interruption reimbursement is not fixed until the facility has been paid for the repair work on the repair order that stranded the holder."
  - Action form. Same fallback test: the repair-work payment cannot be told apart from the diagnostic payment by any record, so the fallback is justified. The business words "repair work" separate it from "diagnostic time". PASS.
- No rule restates another policy's prerequisite sentence. No rule names a tool or another policy id.
- Docstrings are silent about sequence (O-3 aside).
- Undeclared cross-problem orders inside extended rules: none found.
- Base sentences that state a cross-problem order:
  - `warranty_benefits`: "Benefits are paid only with an approved claim." Where a tree rests on it (rental), the extended rule carries its own sentence (E1), so this is an observation (O-6). For trip, the approved decision is already seeded, so no edge rests on it.
  - `warranty_cancellation`: "A cancellation is processed only after the holder has confirmed a cancellation request". The request is a seeded record, not a write of the tree. Observation.

### override_declarations

Sentence-by-sentence sweep of each `base_policy_refs` entry.

**stack** (base: `warranty_agg_vehicle_coverage_stack`, `warranty_claims`)
- coverage_stack, sentence 1 (fixed stacking order; the plan "pays only the part ... that the earlier coverage did not pay"): followed. It is an upper bound, and the extended starting amount never exceeds what the limited warranty left unpaid.
- coverage_stack, sentence 2 ("limited to what the LW decision left unpaid ... deductible not applied a second time"): declared overwrite.
- warranty_claims, denial order (waiting period, not in force, component, preexisting, maintenance records): not overwritten. Inherited in full; the extended rule computes only the approved amount.
- warranty_claims, approval clause (labor cap, diagnostic, deductible, lesser-of): declared overwrite.
- warranty_claims, "A claim is paid only on a plan whose status is active", recovery and facility-payment sentences: untouched and inherited.
- The extended tax is "added last" before the cap. It is new and is declared in `replaced_by` ("the repair sales tax is added last").

**rental** (base: `warranty_benefits`)
- Rental sentence: declared overwrite.
- Inherited: "Benefits are paid only with an approved claim", the towing and trip sentences, "Receipts must be submitted within the benefit receipt submission days after the repair is completed", once per repair order per type, no reduction of coverage, status active or exhausted.
- The receipt-window sentence is inherited in full and is not restated in the extended rule. Its consequence in task 0 is demonstrated in `0.md` (F-0-2).

**cancellation** (base: `warranty_cancellation`)
- Effective-date sentence: declared overwrite. Pro-rata sentence: declared overwrite. "issued only on a plan whose status is cancelled": declared overwrite.
- Inherited: the confirmed-request gate; lapse after the confirmation days; the flat-cancel and free-look order (restated identically); one refund per plan; the lienholder sentence (restated: "while a financed plan's finance contract is still active the refund belongs to Kestrel Auto Finance ... not settled through this booking"); refund timing.
- The base measure `warranty_msr_days_used` ("from sale_date to the cancellation request date") is superseded through the declared pro-rata overwrite.
- No undeclared override.

**recovery** (base: `warranty_claims`)
- Recovery sentence: declared overwrite.
- The extended "plus the repeat-error handling charge ... the amount recovered restores the coverage remaining" means the coverage limit is restored by an amount that includes a handling charge, not only the payment made in error. The declaration covers it, so this is no undeclared override. Its business realism is noted in factor_ladders (O-8).

**diagnostic** (base: `warranty_claims`)
- Approval clause: declared overwrite.
- The base "diagnostic time only when the plan covers it" survives in the extended rule ("When the plan covers diagnostic time ...") and in compute (`if P('diagnostic_covered_when_repair_covered') else 0`).

**release** (base: `warranty_claims`)
- Approval clause: declared overwrite.
- "A claim is paid only on a plan whose status is active" and "Facilities are paid within the facility payment business days" are inherited. The late-payment interest factor prices lateness rather than forbidding it, and does not contradict the base timing sentence.

**trip** (base: `warranty_benefits`)
- Trip sentence: declared overwrite.
- **The dropped branch.** The superseded clause carries the eligibility condition "when the breakdown happens at least the minimum distance from the holder's residential address". The `replaced_by` and the extended rule restate the computation but not the 100-mile distance condition. The extended rule says only "while a covered breakdown keeps the holder away from home".
- The override is declared, so it is not undeclared. But a distance gate that base states has been removed with no sentence stating that it no longer applies.
- No consequence in task 1 (the breakdown is about 500 miles from home, so either reading pays). Observation O-7.

Disguised forms:
- Anonymous intermediate factors: none outside the declared clauses.
- 0/1 multiplier: diagnostic `result ... if P('diagnostic_covered_when_repair_covered') else 0` carries the base condition. Recovery `in_window` carries the base window. Both are base conditions, not overrides.
- No rule calls base output a "wrong value".

### factor_ladders

Counts per computation (honest labels per the auditor's reading):

| policy | factors | parameter | method (declared) | method that passes the label test | multi-source factor | cross_difficulty factors |
| --- | --- | --- | --- | --- | --- | --- |
| stack | 6 | 5 | 1 (limited_warranty_remainder) | 1: the tiers change which terms are subtracted | limited_warranty_remainder tier 1 (decision AND deductible on one record); remainder_deductible tier 2 (maintenance plan AND redemptions, two records) | purchase ×3, maintenance ×1 |
| rental | 6 | 4 | 2 (rental_night_count, limited_warranty_rental_credit) | 2: a recorded figure vs a date span; subtract paid vs nights beyond | rental_night_cap tier 1 (limited-warranty estimate AND plan ledger count) | purchase ×5 |
| cancellation | 6 | 2 | 4 (use_start_day, use_end_day, time_fraction_basis, claims_charge_composition) | 2: time_fraction_basis (months vs months+1 vs days) and claims_charge_composition (different terms). use_start_day and use_end_day only select a date operand fed to the same span (O-9) | kestrel_relationship_fee_share tiers 1–2 (trade-in record AND purchase-order status) | purchase ×2, tradein ×2 |
| recovery | 4 | 3 | 1 (payment_error_measure) | 1: different subtrahend | none within the policy | none |
| diagnostic | 5 | 4 | 1 (long_diagnosis_adjustment) | 1: multiply vs add vs none | none | purchase ×1 |
| release | 6 | 5 | 1 (limited_decision_refigure) | 1 | limited_decision_refigure tier 1 (decision AND contract coverage) | purchase ×1 |
| trip | 6 | 4 | 2 (trip_end_day, trip_start_counting) | **0**: see below | trip_day_cap tier 1 (payments total AND decision system) | purchase ×1 |

- **Trip's two method labels do not pass the label test** (finding F-D-1, below). The compute line is `counted_trip_days = MX(0, DAYS(trip_failure_date, trip_end_date) + start_adjustment)`. `trip_end_day` only selects which date fills the `trip_end_date` operand (`ro_last_payment_date` / `NOW` / `trip_decision_date`). `trip_start_counting` only selects the number `start_adjustment` ∈ {1, −1, 0}. Both substitute a value into one unchanged formula. That is the `parameter` shape ("a factor labelled method whose tiers only substitute a different number into the same formula").
- Ladder shape: every ladder has 3 tiers, and each is pairwise disjoint as stated. No two tiers of one ladder select the same value or method. Two sets of tiers coincide only on particular inputs, which is not a ladder defect:
  - stack `limited_warranty_remainder` tiers 1 and 2 coincide when the deductible is 0, but tier 1 requires a deductible above 0;
  - recovery `payment_error_measure`.
- Fall-through tier equals `baseline` for every factor of every policy. Each `baseline.rule` is verbatim in its rule and self-sufficient (gives a definite number with no factor). `baseline.params` keys exist in the variant parameters.
- Business realism, judged per tier. No tier condition restates the policy's scope; each divides the customers who reach the write. Realism notes, each an observation:
  - O-8: a recovery handling charge restores the holder's coverage limit (recovery is declared to restore the full recovered amount).
  - O-10: a plan paying 50%/75% on a repeat repair on the same system (stack `repeat_repair_share`, release `comeback_repair_share`, diagnostic `repeat_diagnosis_share`) penalises the holder for the facility's comeback. This is unusual in vehicle service contracts, but it is a published reduction a business can apply and not an unreal tier.
  - Rental secondary-coverage share: plausible.
  - State repair and rental tax rates: plausible.
- Cross-difficulty coverage per task:
  - Tree A has purchase, maintenance and tradein reads.
  - Tree B has only purchase `variant_name` reads (program hours, parts uplift, trip allowance). That is a CFIELD value read of another difficulty's holding, so the requirement is met (at least 1 per task).

### findings

- **F-D-1 — SOURCE-FACTOR RED (bears on task 1).**
  - Symptom: the trip-interruption computation declares 2 `method` factors, and neither changes the algorithm.
  - Root cause: `trip_end_day` and `trip_start_counting` are labelled `method`, but their tiers substitute an operand into the single expression `MX(0, DAYS(trip_failure_date, trip_end_date) + start_adjustment)`.
  - Evidence: `warranty_ext_trip_interruption_reimbursement.compute` bindings `trip_end_date`, `start_adjustment` and `counted_trip_days`; `factors[0..1].effect: method`.
  - Consequence: counted honestly, the computation has 0 `method` factors, below the floor of 1 per computation. It stays at 6 factors and 6 parameter-shaped. Task 1's file demonstrates it on its world.
  - Affected: extended charter, trip policy, `factors`.
- **F-D-2 (bears on task 0).** The cancellation prerequisite E3 quantifies over every repair order with approved limited-warranty rental days, and the rental policy's reimbursement can be computed only for the latest limited-warranty decision (every lw_* binding is `XLATEST`). Where a holder has two such repair orders, the gate cannot be closed by the tree's writes. This is a charter-level fact; the demonstration against task 0's world is in `0.md`.
- **F-D-3 (bears on task 0).** The base `warranty_benefits` receipt window ("Receipts must be submitted within the benefit receipt submission days after the repair is completed") is inherited by the rental policy. No record in the schema carries a repair-completion date (`purchase_limited_warranty_claims` and `service_contract_transactions` have no such field). Demonstration in `0.md`.
- Observations O-1 to O-10 as listed above. None of them is a ground for rework.

## closing_checklist

(Pending. Written below, under its own heading, only after every task's blind derivation is frozen and its GT revealed. Nothing above this line is derived from a revealed GT.)

### closing_status (written after both reveals, 2026-10-06 09:35 UTC)

The difficulty does **not** close, so the Step 4 checklist is not certified. Status of each item:

- Audit files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside. This is the first revision, so there is no older revision to trace.
  - Task 0 comparison: **RED** (SOURCE-CHAIN and SOURCE-TASK: F-0-1, F-0-2).
  - Task 1 comparison: **RED** (SOURCE-FACTOR: F-D-1 / F-1-1).
- Coverage and scope: the GT `charter_scope` of the two tasks are {cancellation, stack, rental} and {trip, recovery, diagnostic, release}. They are pairwise disjoint and cover all 7 extended policies. Task tools and GT are closed. Every uuid8 is independent.
- Trees:
  - task 0: n=2, 3 value_input edges, user write = rental;
  - task 1: n=3, 3 value_input edges, user write = trip.
  - Both acyclic, and the union graph of E1–E7 is a DAG.
  - Task 0's E3 cannot be satisfied for RO-552614 (F-0-1).
- Factors: every factor of every computation bears weight against an honest baseline, and every whole baseline gives a definite number different from gold. The exception is the trip computation's method count (F-D-1).
- Gates: not re-run by this auditor. The brief's snapshot is all green, with traceability deferred.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent audit agent, round 2. Written 2026-10-06 ~10:30 UTC, before any round-2 GT was revealed. Nothing in this section is derived from a revealed round-2 GT.
- Freeze hashes, re-computed on disk and matching the coordinator's list:
  - `warranty.extended.yaml` b49e4d7a393fff62c470e9dbc45f61bfab58256754dcbf8f1fe07e7d6adba30e (changed)
  - `task_tools.py` 7741e966d318d2514bdb000705810cedafd83e8645306c46189af897baa957da (changed)
  - `task_0.view.json` 279a5a2c… (unchanged)
  - `task_1.view.json` 767ba935df22938f74d0475f761088845bdf7bf775fdcdd84baa5531f907dce0 (changed)
- Both shared inputs changed, so every charter-global section below is re-derived in full rather than carried forward.
- contamination_disclosure (charter level): this auditor revealed the round-1 GT of both tasks during round 1. Nothing in this section relies on it.
- Gate snapshot (orchestrator re-run): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred.

### policy_conflict_scan (r2)

- Base copy: still identical to `blueprint/products/warranty.yaml`. The only top-level key added is `extended_policies`.
- The 7 extended policies, their target tools and computes, and the two trees are as in round 1.
- Changes found:
  - **rental**: a second overwrite of `warranty_benefits`. The receipt-window sentence is replaced by a window counted from the plan's approved authorization. The compute adds `receipt_window_open` and `result … if receipt_window_open else 0`.
  - **cancellation**: E2 now says "wholly or partly unpaid". The E3 sentence and condition now exclude repair orders whose plan authorization is older than the benefit receipt submission days. `other_delivered_vin != F('vin')` is added to the fee-share compute. `use_start_day` and `use_end_day` are relabelled `parameter`.
  - **trip**: the distance condition is restored to the rule. The end-day factor is removed; the release day (latest claim payment, else the decision date) is now part of the baseline sentence. The start factor is renamed `failure_day_count` (parameter). A new method factor `overflow_day_payment` pays days beyond the cap.
  - **task_tools.py**: the line-17 docstring now reads "This booking leaves the contract's coverage remaining unchanged." Function bodies are unchanged; there are still no condition branches.
- No new conflicts: the new rental receipt sentence and E3 use the same anchor (the date of the plan's approved authorization) and the same N days.

### rule_compute_equivalence (r2)

- The verbatim script was re-run (temporary, since removed). Every `compute_basis` quotation is now in its own rule, so **O-1 is closed** (no stale "engine or the transmission" quote). Every baseline sentence, `replaced_by` and `superseded_clause` is verbatim where required.
- New rental `receipt_window_open` quotes the new overwrite sentence. Its compute is `DAYS(auth_date, NOW) <= P('benefit_receipt_submission_days')`, which is equivalent.
- New trip bindings are equivalent to their rule sentences:
  - `release_date`, `failure_day_count`, `overflow_days` and `trip_days_amount`;
  - "The days booked on the reimbursement are the capped days plus the days beyond the cap where those days are paid" fixes the `trip_days` tool argument.
- **O-2 is closed** in practice. A residual (observation O-13): `CFIELD('purchase','vin',status='delivered')` returns the first delivered order. For a holder with two delivered orders, one of which is the covered vehicle, the test can still read the covered order. Neither world has this state.

### action_binding_and_uuids (r2)

- Unchanged: the same 7 tools and uuid8s, each claimed once, with no validation in any body.
- **O-3 is closed**: no ordering word remains in any docstring outside the denial-code definitions.

### prerequisite_graph (r2)

- Same E1–E7: same kinds, forms, gates and `resolved_by`; acyclic.
- Each `policy_source` is still verbatim in its own rule (script check).
- E2's condition ("covered less than the repair estimate") now matches the sentence's "wholly or partly unpaid", so **O-5 is closed**.
- E3's sentence and condition are narrowed together:
  - sentence: "and which either has no KestrelCare authorization yet or has one dated within the plan's benefit receipt submission days";
  - condition: "… dated no more than the plan's benefit receipt submission days before the day of the refund".
  - The sentence omits the anchor "before the day of the refund". The natural reading is "within the last N days", which matches the rental rule's own window ("counted … from the date of the plan's approved authorization"). Observation O-12: a reader who anchored at the cancellation request date would read the gate differently.
- E4 still has a field-name gate (O-4 unchanged by choice).

### prerequisite_sentences (r2)

- E1, E4, E5, E6 and E7 are unchanged and PASS as in round 1.
- **E2** "A cancellation refund is fixed only after every repair order that a limited warranty decision for the holder left wholly or partly unpaid carries a KestrelCare authorization decision on the plan." State form; one write (the stack authorization). PASS.
- **E3** "A cancellation refund is not worked out until each repair order whose limited warranty decision recorded approved rental days, and which either has no KestrelCare authorization yet or has one dated within the plan's benefit receipt submission days, carries a rental car reimbursement entry on the plan."
  - "not … until"; state form; one write books a `rental_car` entry (the rental filing).
  - The new scope matches the rental policy's own receipt window. A repair order the gate covers can be resolved by a rental filing whose window is open, and a repair order whose window has closed is outside the gate. The sentence is no longer broader than what the tree can resolve.
  - Edge case (no consequence in either world): a repair order with no authorization whose stack decision would be a denial could never receive a rental. Observation O-14.
  - PASS.

### override_declarations (r2)

- **rental**: two declared overwrites. The second supersedes the whole base sentence "Receipts must be submitted within the benefit receipt submission days after the repair is completed, and each benefit type is reimbursed once per repair order." Its replacement restates both halves for **rental only**.
  - That base sentence also governed towing and trip interruption. After the overwrite, no surviving sentence states a receipt window or a once-per-repair-order limit for towing or trip. This is the dropped-branch form, though declared.
  - Observation O-11. No consequence in task 1: the repair is complete today, and RO-558204 carries no earlier trip reimbursement.
- **trip**: the overwrite still supersedes the clause containing the distance condition. The extended rule now restates it ("applies only when the breakdown happened at least the plan's trip interruption minimum distance from the holder's residential address"), so **O-7 is closed**.
- **cancellation**: the three overwrites are unchanged. No undeclared override.
- **stack, recovery, diagnostic, release**: unchanged from round 1.

### factor_ladders (r2)

| policy | factors | parameter | method passing the label test | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| stack | 6 | 5 | 1 | yes | purchase, maintenance |
| rental | 6 | 4 | 2 | yes | purchase |
| cancellation | 6 | 4 (use_start_day and use_end_day now labelled parameter, so **O-9 is closed**) | 2 (time_fraction_basis, claims_charge_composition) | yes | purchase, tradein |
| recovery | 4 | 3 | 1 | — | — |
| diagnostic | 5 | 4 | 1 | — | purchase |
| release | 6 | 5 | 1 | yes | purchase |
| trip | 6 | 5 | **1: overflow_day_payment** | yes (trip_day_cap tier 1; overflow tier 1) | purchase |

- **Trip label test.** `overflow_day_payment` tiers:
  - (capped + overflow × share) × allowance;
  - capped × allowance + overflow × meals amount;
  - capped × allowance.
  - Each composes the amount from different terms (an added overflow term priced two different ways, or none). That is a genuine method; the fall-through equals the baseline.
  - `failure_day_count` is now honestly labelled parameter (+1 / −1 / 0).
  - **F-D-1 is closed at charter level**; whether the new factor bears weight is decided on task 1's world.
- Every ladder still has 3 disjoint tiers, each stated in the rule and implemented in compute. No two tiers select the same value or method. Every fall-through equals its baseline.
- Realism of the new overflow ladder (powertrain repairs past the cap paid at half allowance; other repairs meals only at 35.00/day; otherwise unpaid): a published extended-stay treatment, plausible. Observation O-10 (repeat shares) and O-8 (handling charge restoring the limit) are unchanged by choice and remain observations.

### findings (r2)

- **F-D-1: closed**. The trip computation now has an honest method factor (`overflow_day_payment`).
- **F-D-2 (the E3 scope against the latest-only rental computation): closed at charter level.** E3 now covers only repair orders whose rental can still be filed under the rental policy's own window. Task 0's file shows that RO-552614 falls outside.
- **F-D-3 (receipt window resting on an unrecorded completion date): closed at charter level** for rental, whose window is now counted from the plan's authorization date, a ledger field.
- **New observations, none of them rework grounds:**
  - O-11: towing and trip lose their receipt and once-per-repair-order sentences through the rental overwrite;
  - O-12: the E3 sentence omits the "before the day of the refund" anchor;
  - O-13: `other_delivered_vin` first-match residual;
  - O-14: the E3 / denied-authorization edge case.
- No new RED found at charter level.

### closing_status (r2, written after the round-2 reveals, 2026-10-06 10:30 UTC)

- Per-task r2 verdicts:
  - task 0: **RED**. SOURCE-CHAIN F-0-3 and SOURCE-FACTOR F-0-4, both false world assertions in `design_rationale` ("rental_days 6"; claims charge "1531.93"). The scored GT is correct and uniquely entailed.
  - task 1: **PASS**.
- Round-1 REDs: F-0-1, F-0-2 and F-D-1/F-1-1 are all **closed**, verified against the artifacts.
- Observations, verified against the artifacts:
  - O-1, O-2, O-3, O-5, O-7 and O-9: closed.
  - The rounding observation: **not** closed (GT still rounds half-even in non-scored figures).
  - O-4, O-6, O-8, O-10 and O-0-1: unchanged by choice; they remain observations.
  - New observations: O-11 to O-14.
- No regression: every scored value of task 0 is unchanged, and task 1's other three writes are unchanged.
- Checklist items, as of r2:
  - files correspond one-to-one, and the old revisions are kept intact above;
  - scopes are disjoint and complete;
  - uuid8s are independent;
  - trees: n=2 with 3 value_input edges, and n=3 with 3 value_input edges, each with one user write; the union graph is a DAG;
  - every computation has 4–6 factors with at least 1 honest method and at least 2 parameter; every task has a multi-source and a cross-difficulty factor; every factor bears weight against an honest baseline; every all-baseline value is definite and differs from gold;
  - gates: the orchestrator's r2 snapshot is all green (not re-run by this auditor).
- The difficulty **does not close** while task 0 carries F-0-3 and F-0-4.

## revision_3

### charter_global_frozen (revision 3)

- Same auditor, round 3. Written 2026-10-06 ~10:45 UTC, before any round-3 GT was revealed.
- Hashes, re-computed and matching the coordinator's list:
  - `warranty.extended.yaml` 2861240a9fd8bad11570db860f1bcb780f05b00d76beb9604a99a38c41e7beca (changed)
  - `task_tools.py` 7741e966… (unchanged since r2)
  - `task_0.view.json` ce7756d4481a698b4507f72f84b99010b1e70e403c32cad38ece930f3252bf6f (changed)
  - `task_1.view.json` 767ba935… (unchanged)
- The charter changed, so every charter-global section is re-derived below. The tool module is unchanged, so `action_binding_and_uuids` is carried forward from r2 on the grounds of the unchanged hash 7741e966….
- contamination_disclosure: the round-1 and round-2 GT of both tasks were read in earlier rounds.
- Gate snapshot: all green (traceability deferred).

### policy_conflict_scan / rule_compute_equivalence (r3)

- The base copy is still identical. The verbatim script was re-run (temporary, since removed): every `compute_basis` quotation, `baseline.rule` sentence, `replaced_by` and `superseded_clause` is verbatim where required.
- Changes against r2:
  - **rental**:
    - the second overwrite's `replaced_by` adds "Towing and trip interruption receipts remain due within the benefit receipt submission days after the repair is completed, the release of the vehicle by the repairing facility marking that completion, and each of those benefit types is reimbursed once per repair order.";
    - the compute adds `auth_repair_order` and `rental_already_paid`, and `result` is now gated on `receipt_window_open and rental_already_paid == 0`, which implements "the rental is reimbursed once per repair order".
  - **cancellation**: E3's sentence and condition now read "… and which carries either no KestrelCare decision yet or an approved one dated no more than the plan's benefit receipt submission days before the refund is worked out …".
  - **trip**:
    - the rule adds "Trip interruption receipts are accepted within the plan's benefit receipt submission days counted in calendar days from the day the vehicle is released, and trip interruption is reimbursed once per repair order.";
    - the compute adds `trip_receipt_window_open` (DAYS(release_date, NOW) ≤ N) and `trip_already_paid`, and gates `result` on both.
  - **stack, recovery, diagnostic, release**: rule lengths and factor sets are unchanged, and the evaluator reproduces the r2 figures.
- Consistency: the trip receipt window now appears in two rules. The rental overwrite says "after the repair is completed, the release of the vehicle … marking that completion", and the trip rule says "counted … from the day the vehicle is released". They state the same anchor and the same N, so there is no conflict. Observation O-15: one quantity is stated in two policies; it is consistent.

### prerequisite_graph / prerequisite_sentences (r3)

- E1, E2, E4, E5, E6 and E7 are unchanged and PASS.
- **E3** "A cancellation refund is not worked out until each repair order whose limited warranty decision recorded approved rental days, and which carries either no KestrelCare decision yet or an approved one dated no more than the plan's benefit receipt submission days before the refund is worked out, carries a rental car reimbursement entry on the plan."
  - The anchor is now explicit ("before the refund is worked out"), so **O-12 is closed**.
  - Only approved decisions keep a repair order in scope, so a repair order whose plan decision is a denial falls outside and can no longer leave the gate unsatisfiable. **O-14 is closed**.
  - The condition carries the same scope ("absent or an approval dated no more than … before the day the refund is worked out").
  - State form; the only resolving write is the rental filing. PASS.

### override_declarations (r3)

- **O-11 closed.** The rental policy's overwrite of the whole base receipt and once-per-repair-order sentence now restates both halves for towing and trip as well.
  - Towing keeps the base meaning, with "after the repair is completed" glossed as the vehicle's release.
  - Trip interruption's window and once-per-repair-order limit are restated in its own rule too.
  - No base provision is left unrestated.
- The other overwrites are as in r2. No undeclared override.

### factor_ladders (r3)

- Unchanged from r2: 6/6/6/4/5/6/6 factors, each computation with at least 1 honest method and at least 2 parameter, ladders of 3 disjoint tiers stated in the rule, fall-through equal to baseline.
- The new `receipt_window_open`, `rental_already_paid`, `trip_receipt_window_open` and `trip_already_paid` are eligibility gates implementing declared rule sentences (0/1 on the result). They are not factors and do not override base.
- The rental 0/1 gate does change one charter-level fact the tree relies on. With no plan authorization on the latest-limited-warranty repair order, `auth_repair_order` falls back to the latest approved authorization on any repair order, and the window test reads that date. Task 0's file shows the effect on its load-bearing figure.

### findings (r3)

- No new charter-level RED.
- Observations: O-11, O-12 and O-14 closed; O-15 new (the trip receipt window stated in two rules, consistently). O-4, O-6, O-8, O-10 and O-13 are unchanged by choice.

### closing_status (r3, written after the round-3 reveals, 2026-10-06 10:44 UTC)

- Per-task r3 verdicts:
  - task 0: **RED**. F-0-5 (SOURCE-CHAIN, proof assertion): `prerequisite_closure.edge_load_bearing[2]` and two `design_rationale` sentences state the rental-without-authorization value as 109.65. The r3 rental compute gives 0.00 (the receipt window is read off RO-552614's 2026-08-04 authorization). This is a regression introduced by the r3 rental gate. Scored GT is unchanged, correct and uniquely entailed.
  - task 1: **PASS**, no regression.
- Round-2 REDs F-0-3 and F-0-4: **closed**, verified.
- Observations:
  - closed and verified: O-11, O-12, O-14, O-0-1, and the rounding observation (re-documented);
  - unchanged by choice: O-4, O-6, O-8, O-10, O-13;
  - new: O-15 (the trip receipt window stated in two rules, consistently) and O-1-2 (the March trip seed row priced at the base allowance).
- Checklist status:
  - scopes disjoint and complete;
  - uuid8s independent (tool module unchanged);
  - trees n=2/n=3 with 3 value_input edges each and one user write each; union graph a DAG;
  - every computation within factor bounds, every factor bearing weight against an honest baseline;
  - gates green per the orchestrator's r3 snapshot (not re-run by this auditor).
- The difficulty **does not close** while F-0-5 stands.

## revision_4

### charter_global_frozen (revision 4)

- Same auditor, round 4. Written 2026-10-06 ~11:05 UTC, before any round-4 GT was revealed.
- Hashes, re-computed and matching the coordinator's list:
  - `warranty.extended.yaml` cd1f8523bc1cf2b8c9e5e8fc91e2583534d305f262f46f7ed4e74dca98a81a67 (changed)
  - `task_tools.py` 7741e966… (unchanged, so `action_binding_and_uuids` is carried forward from r2)
  - `task_0.view.json` ce7756d4… (unchanged)
  - `task_1.view.json` 8d5dcf2b00977b2f1070fa5c37cc02f412a68c387e8b9f8e62069362afda050c (changed)
- contamination_disclosure: the round-1 to round-3 GT of both tasks were read earlier.
- Gates: all green per the orchestrator.

### changes and re-derived checks (r4)

- The base copy is still identical. The verbatim script was re-run (temporary, since removed): no `compute_basis`, baseline, overwrite or `policy_source` issue in any policy.
- Only the **rental** policy changed.
  - New rule sentence: "The repair order a rental reimbursement is figured on is the one named on the holder's latest limited warranty decision, and the plan's approved authorization it reads is the one on that same repair order; while that repair order carries no approved authorization, no rental reimbursement is due on it."
  - The compute adds `lw_repair_order`. `auth_failure_date` and `auth_date` are now filtered by `repair_order_number=lw_repair_order`. `receipt_window_open` is now `… if auth_date else False`, and `rental_already_paid` is keyed on `lw_repair_order`.
  - Rule and compute are equivalent in both directions, and the new sentence is the basis of the three re-keyed bindings.
  - This removes the r3 fallback to another repair order's authorization, the root cause of F-0-5, at charter level.
- prerequisite_graph and prerequisite_sentences: E1–E7 are unchanged and PASS.
  - Observation **O-16**: the new rental sentence's last clause ("while that repair order carries no approved authorization, no rental reimbursement is due on it") is a second wording of E1's state ("booked only after the repair order it belongs to carries an approved KestrelCare authorization").
  - Check 6 asks the blocked rule to carry nothing else about the dependency. Here both wordings name the same state on the same repair order with the same scope, and neither yields a different order or value. No consequence can be demonstrated, so it is not a RED. It is flagged because the KB doc audit tests that the prerequisite sentence is carried alone.
- override_declarations: unchanged from r3. No undeclared override.
- factor_ladders: unchanged. Rental's six factors keep their ladders, labels and baselines. The re-keying changes the binding of the authorization date, not any tier.
- Findings: no new charter-level RED. O-15, O-4, O-6, O-8, O-10 and O-13 are unchanged by choice.

### closing_checklist (r4, written after the round-4 reveals, 2026-10-06 11:05 UTC)

All M = 2 tasks PASS all four relationships in r4, so the difficulty closes:

- **Audit files:**
  - `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside.
  - Revisions 1–4 are appended in order, and older revision text is untouched.
  - Each r4 comparison section carries PASS (task 0: `0.md` § source_gt_comparison (r4); task 1: `1.md` § source_gt_comparison (r4)).
- **Coverage and scopes:**
  - The 7 extended policies are fully covered: task 0 = {cancellation, stack, rental}, task 1 = {trip, recovery, diagnostic, release}. The scopes are pairwise disjoint over whole trees.
  - Task tools and GT are closed. The 7 uuid8s are independently generated and frozen (tool module 7741e966…, unchanged since r2).
- **Trees:**
  - task 0: n = 2 prerequisite problems, 3 value_input edges (≥ 1), user write = rental;
  - task 1: n = 3, 3 value_input edges (≥ 2), user write = trip.
  - No cycles. The union graph E1–E7 is a DAG with no cross-task reference.
- **Factors:**
  - Every computation declares 4–6 factors with at least 2 honest `parameter` and at least 1 honest `method`. Every ladder has 3 disjoint tiers stated in full in the rule.
  - Tiers are distinct in outcome, and their conditions and outcomes are ones this line of business holds (realism notes O-8 and O-10 remain observations).
  - Each task has a multi-source factor and a cross-difficulty factor whose rows are seeded (task 0: purchase, tradein, maintenance; task 1: purchase).
  - Every factor bears weight on its world against an honest baseline, and every all-baseline value is definite and differs from gold (task 0: 4520.00 / 225.00 / 1762.10; task 1: 1480.00 / 175.00 / 4889.62 / 500.00).
- **Gates:** re-run on the final form by the orchestrator (r4 snapshot: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred to post-publication). Not re-run by this auditor, per the skill's Step 0 division.
- **Open observations (not rework grounds):** O-4, O-6, O-8, O-10, O-13, O-15, O-16.
