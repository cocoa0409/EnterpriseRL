# Policy-task audit — auto_loan_servicing / charter-global

## charter_global_frozen
- Freeze time: 2026-10-06T09:16Z. Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Inputs and hashes (sha256, matching the orchestrator's SHA256SUMS):
  - `tasks/auto_loan_servicing/finance.extended.yaml` aa5af203ea7f195879ec4363369efbab0c1fff4396a0cc87dac104963fb45ad9
  - `tasks/auto_loan_servicing/task_tools.py` 6df5ff0025167df761ede959520c168c7fca797439655a745a0f9e4ddfc6fb98
  - views `task_0.view.json` cd7838c7…5f9, `task_1.view.json` 16c5e071…9a7
- Fields permitted: blueprint.yaml, db_schema.json, share_tools.py, products/finance.yaml, the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), erlbench/ and the compute-DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/COUNT/LATEST/EXISTS/CFIELD/XCOUNT scoping).
- Fields masked and not read while this section was written: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), worklog.md, any earlier audit. Nothing in this section derives from a revealed GT.
- Entry conditions (Step 0): the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all OK; check_traceability deferred until the KB is published) and the masked views with hashes came with the brief. Checked and cited, not re-run. Hashes re-verified: all four match.

### policy_conflict_scan
- Base copy: `diff` of lines 1–1265 of the extended charter against `blueprint/products/finance.yaml` is empty (the only difference is the 4-line header comment before `extended_policies:`). The base is verbatim.
- Six extended policies, each with its own `(target_tool, computes)`:
  | policy | target_tool | owner | computes |
  |---|---|---|---|
  | finance_ext_late_fee_assessment | assess_late_fee_56686208 | agent | late_fee_amount |
  | finance_ext_returned_payment_fee | assess_returned_payment_fee_ca20439d | agent | returned_fee_amount |
  | finance_ext_deferral_qualifying_payment | pay_deferral_qualifying_amount_eaa14a46 | user | total_received |
  | finance_ext_deferral_fee | grant_payment_deferral_f4f9e9cb | agent | deferral_fee |
  | finance_ext_cure_payment | pay_past_due_installment_fb9b9167 | user | total_received |
  | finance_ext_goodwill_late_fee_credit | credit_goodwill_late_fee_132adaff | agent | credit_amount |
- Overlapping subjects:
  - `finance_fee_assessed` (late fee, returned fee): the fee_type differs (late_fee and returned_payment_fee). One installment can carry both a late fee and a returned-payment fee, and they are compatible because each has its own dedup key in base (one late fee per installment; one returned fee per return).
  - `finance_payment_posted` (qualifying payment, cure payment): the payment_type differs (partial_payment and scheduled_installment), and base finance_payment_application governs both. They are disjoint by type and by whether the next due date moves.
- Triggers and time anchors: the late fee follows base `after_grace` (due date is day 0, assessable from day grace+1). Deferral and cure both anchor days-past-due on `next_due_date`. The goodwill credit anchors on the request date. No two policies give a different clock for the same quantity.
- Terminal states: no policy changes status. The deferral moves next_due/maturity, the cure moves next_due, and the qualifying payment moves neither (base: "a partial payment … never advances the next due date"). These are compatible.
- Cross-category reads: purchase (registration_state, variant_name, vehicle_price charges), warranty (status, finance_contract_id), maintenance (status, visits_remaining) and gap (status, finance_contract_id). All are read-only, and no write touches another category.
- Scope exclusivity and completeness, judged from the user_scenario roots and the declared `prerequisite` graph only (charter_scope is masked):
  - Task 0's root is the deferral (finance_ext_deferral_fee). Through its prerequisite edges it reaches qualifying payment → {late fee, returned fee}.
  - Task 1's root is the goodwill credit. Through its edge it reaches the cure payment.
  - Together the two trees cover all six extended policies and share none. **Exclusive and complete.**

### rule_compute_equivalence
Every compute binding of every policy has a `compute_basis` quotation, and I located each quotation verbatim in that policy's `rule`. Sweeping back sentence by sentence turns up no rule clause without an implementation, except as noted.
- late_fee_assessment: state %, tenure cut, courtesy (12-month late-fee window, 6-month return window), floor (monthly payment vs small-payment limit; contract age), the order pct−cut → cap → ×courtesy → round → floor. The compute matches. "Fewer than N whole months" maps to `within_months=N`, which the DSL defines as `0 <= MONTHS(d, NOW) < N`. These are equivalent.
- returned_payment_fee: state fee, amount add-on (reads `total_received` of the latest return = "full amount"), the 12-month return count including the charged return, tenure credit, protection-plan credit (warranty financed in HID and active; maintenance active), channel charge read off the return entry, and `RND(MX(0, …))`. The compute matches.
- deferral_qualifying_payment: the two prerequisite sentences are not compute bindings (correct, since they are prerequisite sentences). Interest accrual `DAYS(last_payment_date, NOW)` equals base measure finance_msr_days_since_last_payment. The compute matches the rule.
- deferral_fee: the state charge method (FL/TX one month of interest on the installment; GA/NC min(tier fee, 5% share); else the tier fee), return-risk multiplier, good-faith credit, delinquency surcharge, seasoning credit, maintenance credit, `RND(MX(0, …))`. The compute matches.
- cure_payment: installments brought current `1 + int((dpd − grace − 1)/30)` for dpd > grace, which matches "one more for each full 30 days in the days past due beyond the grace days and the day after them". The rest of the compute also matches.
- goodwill_late_fee_credit: the compute matches, with two filter observations (O-4).
- Every `factors[].ladder` tier appears as a sentence of the rule and as a branch of the `decides` binding. No tier exists in only one face.

**Conclusion: PASS.**

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy.
- Docstrings: none names another tool, and none uses before/after/first. `credit_goodwill_late_fee_132adaff` says "a late fee the borrower has paid" (a state of the object, not a sequence). That is an observation only (O-3).
- No tool body validates a prerequisite, eligibility or amount. Each one books the caller's figures:
  - assess_late_fee: lines 34–47
  - assess_returned_payment_fee: lines 76–89
  - pay_deferral_qualifying_amount: lines 122–148
  - grant_payment_deferral: lines 181–208
  - pay_past_due_installment: lines 245–274
  - credit_goodwill_late_fee: lines 301–314
- uuid8s: 56686208, ca20439d, eaa14a46, f4f9e9cb, fb9b9167, 132adaff. They are pairwise distinct, share no prefix or suffix, and show no sequence. **Independent.**

**Conclusion: PASS.**

### prerequisite_graph
- `prerequisite` is filled on all six policies (`[]` on late fee, returned fee and cure).
- Edges:
  1. deferral_fee → deferral_qualifying_payment: value_input, gate `partial_payments_today` (a binding of deferral_fee's compute), state form.
  2. deferral_qualifying_payment → late_fee_assessment: value_input, gate `fees_outstanding` (a binding), state form.
  3. deferral_qualifying_payment → returned_payment_fee: value_input, gate `fees_outstanding`, state form.
  4. goodwill_late_fee_credit → cure_payment: value_input, gate `cure_days` (a binding), state form.
- Every `problem` is an extended policy id of this file. No edge points at a base policy or at itself. The graph is acyclic (depth ≤ 2).
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges. No edge declares `fallback_reason`, which is correct because all are state form.
- `condition` against the sentence:
  - Edge 1 condition ("partial-payment entry dated the request date, fees due at zero, last payment date = request date") matches "a partial payment posted on the request date has cleared the fees due and the interest accrued".
  - Edges 2 and 3 conditions restate their sentences at the same scope.
  - Edge 4 adds "and the contract's next due date has moved past that installment", which is a consequence base attaches to a scheduled-installment payment for that installment. That is not a strengthening with a different result.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite`.

**Conclusion: PASS.**

### prerequisite_sentences
Four-point test on each sentence (all quoted verbatim from the blocked policy's own rule):
1. "The deferral qualifying payment is fixed only after the fees due carry a late-fee entry for every installment that is still unpaid after its grace period."
   - Connective "only after". The state is a late-fee entry per unpaid-after-grace installment, in table words. No tool, id or snake_case.
   - Exactly one write of this difficulty creates a late-fee entry: assess_late_fee_56686208 (the deferral fee entry has fee_type deferral_fee).
   - Derivation: sentence + loan history (installment past grace, no late_fee row naming it) + finance_ext_late_fee_assessment's rule ("A late fee is charged once on an installment that is still unpaid after its grace period, as a late-fee entry …") gives one reading.
2. "The deferral qualifying payment is not fixed until the fees due carry a returned-payment fee entry for every borrower payment the bank has returned."
   - Connective "not until". One write creates a returned-payment fee entry: assess_returned_payment_fee_ca20439d.
   - Observation O-1: read literally, "the fees due carry" fails for an old return whose fee was already paid. The returned-fee rule's "charged once for each borrower payment" forecloses a second charge, so no second resolving action exists.
3. "A deferral fee is not fixed until a partial payment posted on the request date has cleared the fees due and the interest accrued on the contract."
   - Connective "not until". A partial payment is posted only by pay_deferral_qualifying_amount_eaa14a46. The cure tool posts scheduled_installment, which is excluded by the word "partial".
   - Derivation: sentence + the qualifying-payment rule ("the one-time partial payment a borrower makes … when asking to defer an installment … applied to that accrued interest and then to those fees") gives one reading.
4. "Goodwill relief on a late fee is not fixed until a scheduled-installment payment has posted on the contract for the installment that late fee was charged on."
   - Connective "not until". Only pay_past_due_installment_fb9b9167 posts a scheduled-installment payment naming an installment.
   - Derivation: sentence + the cure-payment rule ("the one-time scheduled-installment payment a borrower makes … to bring the installments … past their grace period up to date") gives one reading.

Further checks:
- No depended-on rule restates its dependent's sentence. No rule names a tool or another policy id.
- No other cross-problem order appears in any extended rule.
- The phrase "Goodwill relief on a late fee the borrower has paid" in the goodwill rule is a second, scope-level wording of the same dependency. It leads to the same resolving write, so there is no alternative terminal state (observation O-2).
- No base sentence grounds an edge.

**Conclusion: PASS, with observations O-1 and O-2.**

### override_declarations
Sentence by sentence against each `base_policy_refs` entry:
- late_fee_assessment vs finance_late_fees:
  - The fee-amount sentence is superseded and declared.
  - The grace, one-per-installment, waiver and clear-state sentences are followed.
- late_fee_assessment vs finance_payment_application: not touched (no payment quantity).
- returned_payment_fee vs finance_returned_payments:
  - "and the tier's returned-payment fee is assessed" is superseded and declared.
  - Reversal of principal and fees, revert of dates, once-only reversal and autopay are followed.
  - Observation O-5: the base `events:` trigger `finance_payment_returned → finance_fee_assessed` (txn_date of the return) still describes automatic assessment on the return date. The extended rule books the fee "dated the assessment date". The tool takes no date parameter, so no scored value differs.
- deferral_qualifying_payment vs finance_payment_application (`overwrite: []`):
  - Daily simple interest on the last-payment-to-posting days follows base.
  - The interest → fees → principal waterfall follows base.
  - "a partial payment … never advances the next due date" follows base.
  - App/online payment bears no agent-assisted fee, which follows base.
  - No undeclared override.
- deferral_fee vs finance_deferral:
  - "The tier's deferral fee, when above zero, is assessed …" is superseded and declared.
  - Eligibility (active, max DPD, min installments, 12-month and lifetime counts, same-month exclusion) and the one-month moves of next_due/maturity are followed.
  - Base finance_deferral states no payment requirement for a deferral. The extension gates only the fee's value on a partial payment. It does not add a grant condition, so there is no conflict.
- cure_payment vs finance_payment_application (`overwrite: []`):
  - Waterfall followed.
  - Base: "A scheduled-installment payment advances the next due date by one month for each full monthly payment it contains". Extended: "moves the next due date one month later for each installment it brings current".
  - These two differ only when fees + catch-up + deposit reach one monthly payment. The policy has no declaration for that case, which is latent (observation O-6). The consequence must be demonstrated per task.
- goodwill_late_fee_credit vs finance_late_fees / finance_principal_credits:
  - The waiver-count sentence is superseded and declared (the new count includes goodwill credits; 12 whole months).
  - The partial-relief amount replaces the base's whole-fee "waived as goodwill" through that same superseded sentence.
  - "Returned-payment, agent-assisted and deferral fees are never waived as goodwill" and "a fee is cleared only on … active or unwound" are inherited.
  - Principal credit is posted only on an active or unwound contract, which is followed.
  - No share or task tool can waive a fee, so the base waiver path offers no executable second solution.

**Conclusion: no undeclared override.**

### factor_ladders
| policy | factor | label | tiers | multi-source tiers | cross_difficulty | honest label? |
|---|---|---|---|---|---|---|
| late_fee | late_fee_state_percentage | parameter | 3 | no | purchase | yes |
| late_fee | late_fee_tenure_reduction | parameter | 3 | no | – | yes |
| late_fee | late_fee_courtesy | method | 3 | yes (late fees ∧ returns) | – | multiplier (see O-7) |
| late_fee | late_fee_small_payment_floor | parameter | 3 | yes (monthly payment ∧ contract age) | – | yes |
| returned_fee | returned_fee_state_schedule | parameter | 3 | no | purchase | yes |
| returned_fee | returned_amount_addon | parameter | 3 | no | – | yes |
| returned_fee | repeat_return_multiplier | method | 3 | no | – | multiplier (O-7) |
| returned_fee | returned_fee_tenure_credit | parameter | 3 | no | – | yes |
| returned_fee | returned_fee_protection_plan_credit | parameter | 3 | yes (warranty ∧ maintenance) | warranty | yes |
| returned_fee | returned_payment_channel_charge | parameter | 3 | no | – | yes |
| qualifying | qualifying_standing_days | parameter | 3 | yes (installments ∧ returns) | – | yes |
| qualifying | qualifying_lateness_multiplier | method | 3 | no | – | multiplier (O-7) |
| qualifying | qualifying_program_allowance | parameter | 3 | no | purchase | yes |
| qualifying | qualifying_delinquency_allowance | parameter | 3 | no | – | yes |
| qualifying | qualifying_seasoning_reduction | parameter | 3 | no | – | yes |
| deferral_fee | deferral_state_charge_method | method | 3 | no | purchase | **yes, genuine algorithm change** |
| deferral_fee | deferral_return_risk | method | 3 | no | – | multiplier (O-7) |
| deferral_fee | deferral_good_faith_credit | parameter | 3 | yes (installments ∧ partial today) | – | yes |
| deferral_fee | deferral_delinquency_surcharge | parameter | 3 | no | – | yes |
| deferral_fee | deferral_seasoning_credit | parameter | 3 | no | – | yes |
| deferral_fee | deferral_maintenance_plan_credit | parameter | 3 | yes (plan ∧ visits) | maintenance | yes (but see F-1) |
| cure | cure_tenure_catch_up | parameter | 3 | yes (dpd ∧ installments) | – | yes |
| cure | cure_program_catch_up | parameter | 3 | no | purchase | yes |
| cure | cure_contract_age_scaling | method | 3 | no | – | multiplier (O-7) |
| cure | cure_lateness_deposit | parameter | 3 | no | – | yes |
| goodwill | goodwill_record_share | parameter | 3 | yes (late fees ∧ returns) | – | yes |
| goodwill | goodwill_cure_speed | method | 3 | no | – | multiplier (O-7) |
| goodwill | goodwill_prior_relief_reduction | parameter | 3 | no | – | yes |
| goodwill | goodwill_protection_bonus | parameter | 3 | yes (warranty ∧ gap) | warranty | yes |
| goodwill | goodwill_tenure_bonus | parameter | 3 | no | – | yes |
| goodwill | goodwill_repeat_buyer_bonus | parameter | 3 | no | purchase | yes |

- Counts per policy, all within 4–6 factors, at least 2 parameter and at least 1 method as labelled:
  | policy | factors | parameter | method |
  |---|---|---|---|
  | late fee | 4 | 3 | 1 |
  | returned fee | 6 | 5 | 1 |
  | qualifying payment | 5 | 4 | 1 |
  | deferral fee | 6 | 4 | 2 |
  | cure | 4 | 3 | 1 |
  | goodwill | 6 | 5 | 1 |
- Every ladder has 3 pairwise-disjoint tiers as stated, and every fall-through equals the factor's `baseline`. No two tiers of one ladder select the same value or method:
  - Late fee: 4.0 / 5.5 / tier 5.0, 1.0 / 0.5 / 0, 0.5 / 0.6 / 1, and 10 / 12.5 / 15.
  - Others: checked the same way, and all distinct.
- `bindings` are disjoint within each policy, and every `decides` is an input, never `result`.
- Each `baseline.rule` is a verbatim prefix of its `rule`, and each yields a definite number from the records:
  - tier late fee %, cap and floor
  - tier returned fee
  - interest + fees
  - tier deferral fee
  - n×monthly + fees
  - full latest late fee
- Every tier condition and value appears in the rule prose, and every method tier names a computation the rule states.

**Conclusion: structure PASS, subject to findings F-1 and observation O-7.**

### findings
- **F-1 — SOURCE-FACTOR RED (unreal ladder), bears on task 0.**
  - Symptom: deferral_maintenance_plan_credit splits its tiers on "two or more prepaid visits remaining" versus "fewer than two prepaid visits remaining" on the borrower's KestrelCare maintenance plan.
  - Root cause: a loan-deferral fee is a credit/servicing charge. Lenders settle it on the loan's own terms and, at most, on relationship depth. How many prepaid oil-change visits are left on a separate service product is not a condition any auto lender weighs for a deferral fee. The second part of each tier's compound condition (visit count) is invented to make a ladder.
  - Evidence: rule sentence "an active plan with two or more prepaid visits remaining takes the plan-with-visits deferral credit; an active plan with fewer than two prepaid visits remaining takes the plan-last-visit deferral credit". Compute `plan_visits_left: CFIELD('maintenance', 'visits_remaining', status='active')`.
  - Consequence: demonstrated per task in task_0.md (factor_weight).
  - Affected: finance.extended.yaml, finance_ext_deferral_fee rule/compute/factors.
- **O-1** (observation): the literal "fees due carry" wording of the returned-fee prerequisite sentence (above). No second reading with a different value exists.
- **O-2** (observation): goodwill rule's scope phrase "a late fee the borrower has paid" restates the cure dependency a second time. It has the same resolving write.
- **O-3** (observation): the goodwill tool docstring says "a late fee the borrower has paid" (state wording, no tool or ordering word).
- **O-4** (observation): goodwill `prior_reliefs_24m` counts every `finance_principal_credited` with credit_source billing_correction, and every waived late-fee clearance, as "goodwill". It does not filter on the credit naming a late-fee entry, or on the waiver being goodwill rather than in-error. This matters only on worlds with such rows.
- **O-5** (observation): the base event trigger books the returned-payment fee on the return date. The extended rule books it on the assessment date (above).
- **O-6** (observation, latent): the cure payment's due-date advance follows "installments brought current". Base finance_payment_application ties the advance to "each full monthly payment it contains". The two diverge when fees + catch-up + deposit ≥ one monthly payment. The override is undeclared, and the consequence must be checked per task.
- **O-7** (observation): five of the six `method` factors are multipliers on an intermediate or on the result:
  - courtesy 0.5/0.6/1
  - repeat-return 2.0/1.5/1
  - lateness 2.0/1.5/1
  - return-risk 1.5/1.25/1
  - contract-age 0.5/0.75/1, plus cure-speed 0.5/0.8/1 (goodwill)
  
  The audit test reads "a factor labelled method whose tiers only substitute a different number into the same formula" as a mislabel. The instantiate contract (`skills/erl-task-instantiate/SKILL.md`, effect: method) expressly lists "a transform or multiplier on an intermediate or on the result" as a method family. Because the pipeline's own contract sanctions it, this is recorded as an observation and not as a red light. Only deferral_state_charge_method changes the algorithm outright.
- **O-8** (observation, realism): the relationship credits are plausible relationship-pricing treatments but weakly grounded in auto-finance practice. Not red-lit:
  - protection-plan credit on a returned-payment fee
  - protection bonus on goodwill
  - repeat-buyer bonus

  Also recorded here:
  - The payment-channel surcharge on a returned-payment fee.
  - The vehicle-program allowances: the good-faith days and the catch-up days (a collateral-quality proxy).

## closing_checklist
Written after both reveals (2026-10-06T09:20Z). Everything above this heading was frozen before any reveal (sha256 1b06b3c9…184a at 09:19:11Z).
- The per-task files are 0.md and 1.md, one per task, with this file alongside them. This is the first revision.
- Comparison sections:
  - task 0: SOURCE-FACTOR RED
  - task 1: PASS
- **The difficulty does not close.** Step 4 requires every task to pass all four relationships, and task 0 fails the factors relationship. The reasons are the missing near-miss in the deferral-fee computation and F-1. Both are demonstrated in 0.md § findings.
- Items that do hold:
  - The six extended policies are fully covered by the two scopes. GT `charter_scope` confirms task 0 = {returned fee, late fee, qualifying payment, deferral fee} and task 1 = {cure, goodwill}, which are pairwise disjoint.
  - Tools and GT are closed, and the uuid8s are independent.
  - Task 0's tree has 3 prerequisite problems and 3 value_input edges. Task 1's tree has 1 prerequisite problem and 1 value_input edge.
  - Each tree has a user-owned write, and the difficulty-wide graph is acyclic.
  - Every factor bears weight against an honest baseline, and each whole baseline differs from gold.
- Gate re-run on the final form: not performed by this audit. The auditor cites the orchestrator's snapshot from the brief (all OK; check_traceability deferred until the KB is published).

## revision_2

### charter_global_frozen (revision 2)
- Freeze time: 2026-10-06T10:21Z. Auditor: the same independent policy-task auditor as round 1.
- New hashes, which match the orchestrator's brief:
  - finance.extended.yaml bfb6bf7d61ec61fcd53c9167580589a3499a1360acf3c247f0561977386f591e
  - task_tools.py 29d9a1e0aadee08bdb5b0082d9fead12379950a9ed2871a64564b0acfdbb50b1
  - task_0.view.json 0173ad0b…b1bb
  - task_1.view.json 16c5e071…9a7 (unchanged)
- Both shared inputs changed, so every charter-global section below was re-derived in full against the new files and not carried forward.
- Round-1 text above is left untouched.
- Base copy: lines 1–1265 diff empty against blueprint/products/finance.yaml, so the base is still verbatim.
- contamination_disclosure (round 2): I read round-1 GT (tasks/0.json and tasks/1.json of round 1) during round 1. This section is built from the charter, the schema and the tool module only, and contains nothing taken from a revised GT. The revised tasks/*.json had not been opened when it was written.

### changes found (artifact against round-1 reading, by inspection)
- finance_ext_returned_payment_fee rule and baseline.rule now add: "…; a returned-payment fee not charged on the date of the return is charged on the date it is assessed." (O-5).
- finance_ext_deferral_qualifying_payment prerequisite sentences are reworded from "the fees due carry …" to "the loan history carries a late-fee entry naming every installment …" and "… a returned-payment fee entry naming every borrower payment the bank has returned". The rule and `policy_source` match verbatim (O-1).
- finance_ext_deferral_fee drops `deferral_maintenance_plan_credit` (F-1). In its place it adds `deferral_first_extension_credit`:
  - Rule: "A first-extension credit follows the deferrals already granted on the contract, counted as its deferral entries: a contract with no earlier deferral takes the first-extension deferral credit; a contract with exactly one earlier deferral takes the second-extension deferral credit; a contract with two or more earlier deferrals takes none."
  - Values: 2.00 / 1.00 / 0.
  - Compute: `prior_deferrals: COUNT(finance_deferral_granted)`.
  - The overwrite replaced_by, the result formula, compute_basis and inputs are updated consistently, and the maintenance cross_category is removed.
- finance_ext_cure_payment now declares an overwrite of base finance_payment_application: "A scheduled-installment payment advances the next due date by one month for each full monthly payment it contains, never beyond the maturity date;". It is replaced by "… moves the next due date one month later for each installment it brings current, never beyond the maturity date." The rule and baseline.rule carry the replaced_by text (O-6).
- finance_ext_goodwill_late_fee_credit:
  - The rule opening "Goodwill relief on a late fee the borrower has paid …" becomes "Goodwill relief on a late fee is posted …" (O-2).
  - Both relief counts now read "counting every waived late fee and every billing-correction principal credit on the contract as a goodwill relief", which matches the compute filters (O-4). The overwrite replaced_by matches.
- task_tools.py: only the credit_goodwill_late_fee_132adaff docstring changed ("Give goodwill relief on a late fee charged on …"; "has paid" removed) (O-3). The function bodies, signatures, owners and uuid8s are unchanged.

### policy_conflict_scan (revision 2)
- Six extended policies, the same `(target_tool, computes)` pairs, the same owners and the same overlapping subjects as round 1. These remain compatible.
- The goodwill relief count now counts **every** waived late fee as a goodwill relief. Base finance_late_fees (not superseded) keeps "a late fee assessed in error (the installment was in fact paid within grace, or the due date had been moved) is waived without using a goodwill waiver." The superseded clause names only the count sentence, so the two now disagree on whether an in-error waiver uses up the 12-month goodwill allowance. This is a new observation, O-9, below.
- Scope exclusivity and completeness are unchanged by the edits: deferral tree = {deferral fee, qualifying payment, late fee, returned fee}; goodwill tree = {goodwill, cure}.

### rule_compute_equivalence (revision 2)
- Re-swept all six policies.
- New and changed bindings `prior_deferrals`, `first_extension_credit`, `result` (deferral fee), and `prior_reliefs_24m` (goodwill) each have a verbatim compute_basis quote locatable in the rule.
- The goodwill compute filters (fee_cleared late_fee waived + principal_credited billing_correction) now equal the rule's "every waived late fee and every billing-correction principal credit".
- No empty promise and no invented basis.

**PASS.**

### action_binding_and_uuids (revision 2)
- Unchanged tool bodies, which still validate nothing.
- The goodwill docstring is now free of the "has paid" state wording.
- No docstring names another tool or carries an ordering word.
- uuid8s unchanged and independent.

**PASS.**

### prerequisite_graph (revision 2)
- The same four edges, all value_input and state form. The gates `fees_outstanding`, `partial_payments_today` and `cure_days` all exist as bindings.
- Acyclic, and `resolved_by` equals the target tools.
- Each `policy_source` is verbatim in its own rule. The two reworded qualifying-payment sentences were re-located verbatim.

**PASS.**

### prerequisite_sentences (revision 2)
- Sentences 1 and 2 now name a record-visible state ("the loan history carries a … entry naming every …") and drop the literal "fees due carry" (O-1 closed). Connectives "only after" and "not until". Exactly one write creates each entry.
- Sentences 3 and 4 are unchanged and still pass.
- The goodwill rule no longer carries the second scope-level wording "a late fee the borrower has paid" (O-2 closed).
- No other cross-problem order appears in any rule.

**PASS.**

### override_declarations (revision 2)
- O-6 closed: the cure policy now declares the base advance sentence. The merged semantics are unique: for the cure payment the advance equals the installments brought current, capped at maturity.
- New O-9: the base in-error waiver sentence is contradicted by the goodwill counting rule and is not named in the overwrite. Whether it has a consequence is judged per task.
- Everything else is as in round 1.

### factor_ladders (revision 2)
- Deferral fee: 6 factors.
  - deferral_state_charge_method (method, genuine)
  - deferral_return_risk (method label, multiplier; O-7 unchanged)
  - good-faith credit (parameter, multi-source)
  - delinquency surcharge (parameter)
  - seasoning credit (parameter)
  - **deferral_first_extension_credit** (parameter; 3 tiers; values 2.00 / 1.00 / 0 distinct; fall-through 0 = baseline; evidence history; the condition is prior deferrals on this contract)
- Prior deferrals are a condition lenders actually weigh for an extension fee. A first-extension concession is a common servicing practice, and the condition divides the customers who reach this write, since a Tier B contract may carry up to 4 lifetime deferrals.
- Counts for the deferral fee: 4 parameter, 2 method by label (1 genuine).
- The deferral fee now reads only purchase cross-difficulty data. Task 0 still carries warranty and maintenance cross-difficulty factors through the returned-payment fee.
- The other five policies' factor structure is unchanged from round 1.

**Structure PASS.** O-7 and O-8 stand, unchanged by choice.

### findings (revision 2)
- **F-1: closed at charter level.** The visits-remaining ladder is gone from the rule, compute, factors and cross_category. The replacement ladder passes the realism, distinctness and baseline tests above. Confirmation on the task-0 world is in 0.md revision_2.
- **O-1, O-2, O-3, O-4, O-5, O-6:** closed or acted on as listed under changes found.
- **O-9 (new, observation):**
  - The goodwill relief gate now counts every waived late fee, in-error waivers included.
  - The base sentence "a late fee assessed in error … is waived without using a goodwill waiver" is still in force and is not named in the overwrite.
  - On a world with an in-error waiver inside 12 months, the two would disagree on eligibility.
  - Neither task world holds such a row. Task 1's only waiver, 643d7178, is a goodwill waiver 15 whole months old, and task 0 has no waiver. No consequence can be demonstrated, so this is not a red light.
- **O-7, O-8:** unchanged, left by choice. Observations only.

### closing_checklist (revision 2)
Written after both revised reveals (2026-10-06T10:22Z). Everything above this heading in revision_2 was frozen pre-reveal.
- One audit file per task (0.md, 1.md), with this file alongside. Revision 1 text is preserved, and each file appends its own revision_2.
- Every revision_2 comparison carries PASS: task 0 PASS (round-1 SOURCE-FACTOR RED closed), task 1 PASS.
- The six extended policies are fully covered. The scopes are disjoint: task 0 = {returned fee, late fee, qualifying payment, deferral fee}; task 1 = {cure, goodwill}.
- Tools and GT are closed, and the uuid8s are independent and unchanged.
- The trees are:
  - task 0: 3 prerequisite problems, 3 value_input edges, user write
  - task 1: 1 prerequisite problem, 1 value_input edge, user write

  The difficulty-wide graph is acyclic.
- Every computation:
  - declares a self-sufficient baseline that differs from gold
  - has 4–6 factors with at least 2 parameter and at least 1 method by label
  - has every factor bear weight against an honest baseline, with ladders of 3 distinct tiers
- Each task has at least one multi-source factor and at least one cross-difficulty factor, with the rows seeded. Each computation has at least one near-miss.
- Open observations: O-7 (multiplier "method" factors, sanctioned by the instantiate contract), O-8 (realism of the relationship credits) and O-9 (in-error waivers counted as goodwill reliefs, undeclared against base, with no consequence on either world).
- Gates: not re-run by this auditor. Cited from the orchestrator's round-2 snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; check_traceability deferred).

**The difficulty passes the source-layer audit at revision 2.**
