# Policy-task audit — insulin_pump_program_services / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1.
- Freeze time: 2026-10-15T08:29Z, written before the 08:33Z reveal. This section was written before any task's GT was revealed; nothing in it derives from a revealed GT.
- Frozen inputs (sha256, re-checked on disk at start, identical to the coordinator's list):
  - `tasks/insulin_pump_program_services/pump.extended.yaml` 938e50486af7e603a02527c834b5e80d0a89d56dd63ff0d70fd35400475b69a5
  - `tasks/insulin_pump_program_services/task_tools.py` 6c9e70cbf5fe5450aaac9446c18b2642b734f2d320e89c854aa955379b236601
  - `.audit_views/policy/insulin_pump_program_services/0.view.json` 24814afb6803e67f6fc6386508f802bec05327996dfecf2779a93710231c327f
  - `.audit_views/policy/insulin_pump_program_services/1.view.json` 4dc7584d386025d9e040ad1b71bbe05a20728968ee2e8a4857f82d3b1760a062
- Read before the freeze: `blueprint/blueprint.yaml`, `blueprint/products/pump.yaml` (base), `blueprint/products/insulin.yaml` and `cgm.yaml` (parameter and balance sentences only), `blueprint/share_tools.py` (signatures), the extended yaml, `task_tools.py`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (semantics of `within_months`, `LATEST`, `CFIELD`, `X*`). Not read: `tasks/*.json`, any `audits/` file, the instantiator worklog, any other difficulty or scenario.
- Masked in the views (per `_masked_keys`): design_rationale, db_closure, db_closure_matches_initial_state, solvability_contract, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents.
- Scratch: `/tmp/audit_pump_0063/` (harness that evaluates the charter's own `compute` on the view worlds and replays the auditor's own derived writes through the real tool functions).

### entry_conditions (step 0)

- Gate snapshot came with the brief: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; TRACEABILITY NOT OK, coordinator-attributed only to unlock tool names lacking a KB source because the KB is not rendered yet. Recorded as an observation: the entry condition "all instantiation gates green" is not literally met, and the coordinator's attribution was not re-run here (per skill, gates are cited, not run).
- Masked views present, hashes match. Entry otherwise complete.

### policy_conflict_scan

Eight extended policies, one tool each:

| policy | target_tool (owner) | computes | trigger |
| --- | --- | --- | --- |
| pump_ext_infusion_set_refill_quantity | ship_infusion_set_refill_1f98af27 (agent) | pieces | on_request |
| pump_ext_payment_plan_installment | accept_payment_plan_163cafb9 (user) | monthly_amount_usd | on_request |
| pump_ext_non_covered_item_charge | post_non_covered_item_charge_86d5d568 (agent) | amount | state_due |
| pump_ext_unsupported_charge_reversal | reverse_unsupported_liability_charge_60bc70aa (agent) | amount | state_due |
| pump_ext_cartridge_refill_quantity | ship_cartridge_refill_a415cb78 (agent) | units | on_request |
| pump_ext_cartridge_liability_notice | sign_cartridge_liability_notice_61b55bc8 (user) | notice_units | on_request |
| pump_ext_hardship_waiver_amount | post_hardship_waiver_2af40412 (agent) | amount | state_due |
| pump_ext_remittance_posting_correction | correct_remittance_posting_ab84bf6f (agent) | amount | state_due |

Overlapping subjects and conflicts found (details under `findings`):
- Two refill policies gate on the same quantity (past-due amount) with different definitions: the set refill leaves out the balance an approved payment plan covers, the cartridge refill does not (C3).
- Two writes post `billing_correction` adjustments (reversal, remittance correction), and the hardship waiver posts `hardship_waiver`. All three size their adjustment from "amount less adjustments already posted", none from the base "unpaid remainder" after payments applied oldest-first (C2).
- The notice policy signs the cartridge notice under "the newest written order for the cartridge item"; the charge and reversal policies look for "the liability notice signed under the line's written order" = the order the line's grant rests on. These are different records whenever a new order has arrived without a new grant (C4).
- The non-covered item charge and the reversal both price the liable units below the base cash price through courtesy percents (C1).
- Scopes: the two problem trees the charter's prerequisite graph forms are {set refill ← payment plan ← (reversal, non-covered charge ← reversal)} and {cartridge refill ← (notice, hardship waiver ← remittance correction)}. They share no policy and together cover all eight policies, so two tasks can claim them disjointly and completely. Whether the tasks actually claim them that way is a per-task fact.

### rule_compute_equivalence

- Every `compute_basis` entry of all eight policies is verbatim in that policy's `rule` (checked by script, sentence by sentence; zero misses). Every `baseline.rule` sentence is verbatim in the `rule` (zero misses). Every `overwrite.replaced_by` is verbatim in the `rule`; every `superseded_clause` is verbatim in the base rule it names.
- Windows: `within_months=N` keeps rows with `MONTHS(d, NOW)` in [0, N), which equals the rule's "later than the same day of the month N months before" for the three/six-month dispensing windows, and "not aged" for the plan's aged test ("on or before the same day of the month the aged months before"). Consistent.
- Rounding: "rounded up to the cent" (plan) is implemented as a ceiling on cents, consistent. "rounded half up to the cent" (charge, reversal, waiver, correction) is implemented by `RND` = Python `round`, which is not half-up on binary floats (for example 10.275 can round either way). Observation O4. No task value found to fall on a half cent that rounds the wrong way.
- Departures where compute invents a condition or reads a different set than the rule states:
  - C5: daily-pump-insulin tier 1 (`window_basis` in the set and cartridge policies) adds `w_days_6m > 0` to the compute, and the rule does not state it.
  - C6: "pump insulin" is filtered to J1817 / rapid-acting vials in the rule. The compute's `w_days_3m`, `w_days_6m`, `r_days_6m` (set) and `w_days_3m`, `w_days_6m`, `rate_days_6m` (cartridge) sum supply days over every insulin item. The set policy's tier-1 "newest pump insulin dispensing" (`n_item`, `n_units`, `n_days`) reads the newest shipment of any item. The cartridge policy implements the same sentence item by item (`cnj_*`, `cna_*`, `cnl_*`), so one sentence has two implementations in one charter.
  - C7: the non-covered charge's "the Larkfield cash price of the line's item" is implemented as A4232 price or else A4225 price for every other item.
- Cartridge `baseline.rule` carries two complete three-case ladders (covered rate, cartridge rate) that are not declared factors. The rule and compute still match. Observation O3: the computation document will not be silent about variation.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- uuid8 tails: 1f98af27, 163cafb9, 86d5d568, 60bc70aa, a415cb78, 61b55bc8, 2af40412, ab84bf6f. All distinct, with no shared prefix, no sequence and no adjacent values. Treated as independently generated.
- No tool body checks eligibility, status, ownership or any prerequisite (module docstring and every body read: each just `ctx.create` / `ctx.update`).
- No docstring names another tool or places its action in a sequence. The only ordering word is "rounded half up to the cent before posting" (four amount tools), which is intra-call. Observation O15.
- Docstring effect claims: "rounded half up to the cent before posting" and "rounded up to the next cent" (plan) are not what the bodies do (`round(float(x), 2)`). Gold values that are already in exact cents are unaffected. Observation O4. No concrete example values in any docstring.

### prerequisite_graph

| edge (blocked ← depended) | kind | gate | form | policy_source verbatim in own rule | resolved_by = depended target_tool |
| --- | --- | --- | --- | --- | --- |
| set refill ← payment plan | state_gate | pump_requests.request_status | state | yes | yes |
| payment plan ← reversal | value_input | plan_balance (exists) | state | yes | yes |
| payment plan ← non-covered charge | value_input | plan_balance (exists) | state | yes | yes |
| non-covered charge ← reversal | state_gate | pump_billing.adjustment_reason | state | yes | yes |
| cartridge refill ← notice | value_input | noticed_cartridges (exists) | state | yes | yes |
| cartridge refill ← hardship waiver | state_gate | pump_billing.amount | state | yes | yes |
| hardship waiver ← remittance correction | value_input | hw_base (exists) | state | yes | yes |

- Every policy fills `prerequisite` (reversal, notice and remittance correction use `[]`). No edge points at a base policy or at itself. The graph is acyclic (two trees, depth ≤ 3). No `fallback_reason` is needed (no action-form edge).
- Condition / effect versus sentence: the set ← plan `condition` is stronger than its sentence and its `effect` asserts a false general fact (C9). The two conditions that describe the same "no overstated non-covered charge" state are worded differently ("no larger than the cash price of the units…" on the plan edge, "no larger than the amount … support" on the charge edge). Observation O9. The cart ← hardship-waiver `effect` ("the past-due amount is below the hold minimum") is a general claim the rule does not guarantee. Observation O7.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test, one line per edge:
1. "The infusion-set refill is not shipped until the program's past-due amount, after leaving out any balance an approved payment plan covers, is below the tier's past-due hold minimum." Connective "not … until". State form: past-due amount and approved plan, both record-visible. No tool, id or snake_case. Writes in this charter that can make it true: accepting a payment plan, the reversal, or a hardship waiver (only where a hardship application is approved). Which one decides is a world fact, handled per task.
2. "The plan's installments are fixed only after the program carries no non-covered item charge larger than the units the customer's signed liability notice and the payer's denial support." Connective "only after". State form. The write that brings it about is the reversal (a hardship waiver against the charge could also, where an approved application names the charge; checked per task). The wording "larger than the units" compares dollars with units. It is readable but imprecise (O9).
3. "The plan's installments are fixed only after the program's balance carries the non-covered item charge owed for every payer-denied line a signed liability notice covers." State form, one resolving write (non-covered charge). Scope: the sentence spans every denied line, but the charge policy posts only for "the newest CO-151 claim denial". In a world with two or more uncharged noticed denials, the gate cannot be closed by any write. Neither task world has this; observation O8.
4. "A non-covered item charge is posted only after the program carries no non-covered item charge larger than the units its shipment's signed liability notice and the payer's denial support." Same state as edge 2, same resolving write.
5. "The noticed cartridges are fixed only after the cartridge item carries a liability notice signed after the program's previous refill of that item." State form, one resolving write (notice, owner=user). The rule's own "and none otherwise" clause could suggest shipping with zero noticed cartridges. The "fixed only after" sentence excludes that reading, so it is single-reading; observation only.
6. "The cartridge refill is not shipped until the past-due amount the program's patient-balance postings show is below the tier's past-due hold minimum." State form. The sentence leaves out plan-covered balance, but the inherited base keeps the leave-out (C3). Under merged semantics an approved payment plan is a second resolving write alongside the hardship waiver.
7. "The hardship waiver on a posting is figured only after that posting carries no patient responsibility beyond what its remittance supports." State form, one resolving write (remittance correction).

The depended-on rules do not restate any of these sentences (script-checked). No rule names another problem's tool or id. The prerequisite derivation (sentence + records + depended rule → resolving action) is written out per task in each task file.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry. Only departures are listed; every other sentence is followed or untouched.

- pump_ext_infusion_set_refill_quantity: supply days and confirmation are declared overwrites. The confirmation overwrite only narrows ("on that day") and retires nothing (O1). The base sentence "the units and pieces follow from the supply days under pump_evt_quantity_limits" is followed for A4224 units (one per 7 days, rounded up). The base is silent on A4224 pieces, so the new pieces rule is additive. The past-due gate matches pump_holds_and_closure / pump_evt_patient_account (plan leave-out kept). No undeclared departure.
- pump_ext_payment_plan_installment (`overwrite: []`): stays within base min balance, max months and min installment. Leaving a received hardship application's posting out of the plan is additive. No undeclared departure found.
- pump_ext_non_covered_item_charge (`overwrite: []`):
  - C1: base pump_liability_notice prices a non_covered_item charge "at the Larkfield cash price of the units concerned". Extended takes up to 35 percentage points off through late-billing, payment-history and first-liability courtesies. Undeclared.
  - C8: base "On the Medicare Advantage tier no notice can make the member liable; the member becomes liable only for an item for which the plan has issued a pre-service organization determination denial". Extended's liable units come only from a signed notice, so the base MA branch is never produced (dropped branch). Undeclared.
- pump_ext_unsupported_charge_reversal (`overwrite: []`):
  - C1: the supported charge carries the same courtesies, so the reversal posts a courtesy discount as `billing_correction`. Base allows billing_correction only for "a posting made in error, or a timely-filing write-off", and base prices the charge at cash price. Undeclared.
  - C2: base pump_evt_patient_account says "each against the one posting it adjusts and never for more than that posting's unpaid remainder" and "a payment is applied to the oldest unpaid posting first". The open amount is "its amount less the credits already set against it", ignoring applied payments. Undeclared.
- pump_ext_cartridge_refill_quantity: quantity, supply days and confirmation are declared (confirmation narrows only, O1). C3: the past-due gate drops the base leave-out ("while an approved plan's installments are current the balance it covers is left out of the past-due test", pump_evt_patient_account; "no approved payment plan covers it", pump_holds_and_closure). Not declared.
- pump_ext_cartridge_liability_notice: the signing overwrite narrows only (O1). C4 is a cross-policy key conflict, not a base departure.
- pump_ext_hardship_waiver_amount (`overwrite: []`): the base eligibility gates (approved application, tier allowed) are respected. C2 class member: the waiver base is "amount less every balance adjustment already posted against it", which ignores applied payments, against the base "unpaid remainder" cap.
- pump_ext_remittance_posting_correction: the patient-responsibility overwrite is declared. C2 class member: the correction is "the remittance posting's amount less the billing corrections already posted against it, less the supported responsibility", which ignores applied payments. C14: the tier-2 return credit ("a return authorization for the line is issued and nothing is received yet, the authorized units are returned") departs from base pump_evt_returns, which credits only "When the warehouse accepts the returned units as unopened_sealed" and states "Returned units the warehouse finds opened are not accepted and no receipt is recorded". Undeclared (pump_evt_returns is in its base refs, and the overwrite names only pump_evt_claims).

### factor_ladders

Per policy (declared label; m = method, p = parameter). "Multi-source" means every non-fall-through tier is a conjunction or disjunction over distinct records. Structural defects are cited by id.

| policy | factors (label) | #p / #m | multi-source | cross_difficulty | structural findings |
| --- | --- | --- | --- | --- | --- |
| set refill | fx_set_span (m), fx_set_insulin_source (m), fx_set_rate_basis (m), fx_set_dose_window (m), fx_set_cartridge_fill (p), fx_set_defect_spares (p) | 2 / 4 | fx_set_rate_basis (insulin program × insulin shipments); fx_set_cartridge_fill (pump model × pump shipments) | insulin ×3 | C10 strikes fx_set_cartridge_fill, leaving 1 parameter. O10: insulin_source label is borderline |
| payment plan | fx_pl_left_out (m), fx_pl_term (p), fx_pl_household (p), fx_pl_insulin_balance (p), fx_pl_history (p), fx_pl_aged_balance (p) | 5 / 1 | fx_pl_household (cgm_requests × cgm_programs) | cgm, insulin | O5: term tier 1 unreachable on HMO/PPO (min balance 150 = short ceiling), reachable on MA/OM (100) |
| non-covered charge | fx_nc_cover (p), fx_nc_returns (m), fx_nc_late_billing (p), fx_nc_payment_history (p), fx_nc_first_liability (p) | 4 / 1 | fx_nc_cover tier 2 (grant basis × OLJ record) | none | C11: fx_nc_returns is a figure swap, so 0 honest methods. C14: returns tier 2 unreal. C1 on the three courtesy factors |
| reversal | fx_rv_cover (p), fx_rv_returns (m), fx_rv_late_billing (p), fx_rv_payment_history (p), fx_rv_first_liability (p), fx_rv_credits (m) | 4 / 2 | fx_rv_cover tier 2 | none | C11 (both methods are figure swaps), C12 (credits ladder collapses to one formula; straw-man baseline), C14 |
| cartridge refill | fx_cart_span (m), fx_cart_order_basis (p), fx_cart_insulin_source (m), fx_cart_dose_window (m), fx_cart_usable_fill (p) | 2 / 3 | fx_cart_usable_fill (pump model × pump shipments); fx_cart_dose_window tier 2 (orders × shipments) | insulin ×2 | C10 strikes fx_cart_usable_fill, leaving 1 parameter |
| notice | fx_nt_period (m), fx_nt_allowance (p), fx_nt_expected (p), fx_nt_further (p) | 3 / 1 | fx_nt_allowance tier 2 | none | none structural |
| hardship waiver | fx_hw_burden (m), fx_hw_effort (p), fx_hw_aged (p), fx_hw_history (p), fx_hw_balance (p), fx_hw_cost_share (p) | 5 / 1 | fx_hw_burden (insulin program × cgm program) | insulin (+cgm read) | O14: the five points factors bear weight only on burden tier 2 |
| remittance correction | fx_rc_covered_rate (p), fx_rc_unit_value (p), fx_rc_contractual (m), fx_rc_returns (m) | 2 / 2 | fx_rc_covered_rate tier 2 | none | C13: unit_value tiers 2 and 3 cannot be told apart, so the factor is struck and the policy has 3 factors. C11: rc_returns is a figure swap. C14 |

Checked for every factor:
- Bindings are disjoint across factors, and each factor's `decides` is one of its own bindings, not `result`.
- No factor binding reads, transitively, another factor's binding or `result` (script-checked).
- Two bindings were duplicated only to keep binding sets disjoint: `term_balance` ≡ `plan_balance`; `r_days_6m` ≡ `w_days_6m` (set); `rate_days_6m` ≡ `w_days_6m` (cartridge). Observation O2.
- Every ladder states 3 tiers in the rule and implements the same 3 in compute, so the rule and compute match. Exceptions: C5 and C6 (compute conditions and filters not in the rule), C12 and C13 (tiers that coincide).
- Every factor's fall-through equals its declared baseline, and that baseline encodes `baseline.rule` for that input.

Realism notes (industry practice), beyond the RED items above:
- Pump warranty (48 months), PPO replacement interval (48 months) and Medicare capped rental are base parameters and are not touched by this charter's factors.
- Set rate floor of 10 per 30 days (a change every 3 days), J1817 = 50 units, a 10 mL vial = 1000 units, Mobi cartridge 200 u, iLet 160 u, t:slim and 780G 300 u, and a 3-day in-pump stability floor all match manufacturer and HCPCS practice.
- Hardship "points" and payment-plan extensions are company schedules that are plausible as written (O11).
- The non-covered charge's courtesy discounts are plausible goodwill schedules on their own, but they contradict the base price sentence (C1). Payment-history discounts on a Medicare beneficiary's liability would also be an inducement concern on Medicare tiers (O11).

### findings

C-ids are charter-global REDs. Each lists the tasks whose files must demonstrate it.

- **C1 SOURCE-POLICY RED — undeclared courtesy pricing of non-covered charges.**
  - Symptom: the non-covered charge and the reversal's "supported charge" are reduced by late-billing, payment-history and first-liability percents.
  - Root cause: `overwrite: []` on both policies, while base pump_liability_notice fixes the price ("non_covered_item (… that the payer denied, charged at the Larkfield cash price of the units concerned)") and base pump_evt_patient_account limits billing_correction to "a posting made in error, or a timely-filing write-off".
  - Evidence: rule sentences "The courtesy percents add together, and the charge is the liable units less the returned units, never below zero, times the cash price per unit, less the added courtesy percents of that product, rounded half up to the cent." and "The supported charge is the liable units less the returned units, …, less the added courtesy percents of that product …"; compute `result` / `x_supported` with `(100 - late_pct - pay_pct - first_pct)`.
  - Consequence: two defensible charge amounts and two reversal amounts in any world with a nonzero courtesy (demonstrated in task 0).
  - Affected: pump_ext_non_covered_item_charge (`result`, factors fx_nc_late_billing, fx_nc_payment_history, fx_nc_first_liability); pump_ext_unsupported_charge_reversal (`x_supported`, factors fx_rv_late_billing, fx_rv_payment_history, fx_rv_first_liability).
  - Bears on: task 0.
- **C2 SOURCE-POLICY RED — adjustment sized above the base "unpaid remainder".**
  - Symptom: three adjustment policies size the adjustment from amount less prior adjustments and ignore payments.
  - Root cause: base "never for more than that posting's unpaid remainder" with "a payment is applied to the oldest unpaid posting first" is not declared overridden.
  - Class members: reversal `x_open` (`x_amount - x_credits`); hardship waiver `hw_base` (`hw_amount - hw_adjusted`); remittance correction `result` (`rc_amount - rc_prior - rc_supported`).
  - Consequence: demonstrated in task 0 (reversal 332.22 against an unpaid remainder of 200.50). Task 1's members stay within the cap, so there is no consequence there.
  - Bears on: task 0, plus task 1 for class completeness.
- **C3 SOURCE-POLICY RED — the cartridge past-due gate drops the base plan leave-out.**
  - Evidence: the cartridge sentence "…past-due amount the program's patient-balance postings show is below the tier's past-due hold minimum" against the inherited base "while an approved plan's installments are current the balance it covers is left out of the past-due test measured by pump_msr_past_due_amount" and pump_holds_and_closure "…and no approved payment plan covers it". The set refill's gate keeps the leave-out, so the charter's two refill gates disagree.
  - Consequence: on merged semantics, `accept_payment_plan_163cafb9` is a second write that brings the state-form edge's state about, next to `post_hardship_waiver_2af40412`.
  - Bears on: task 1.
- **C4 SOURCE-POLICY RED — notice record key conflict between policies.**
  - Evidence: the notice rule says it is signed "under the newest written order for the cartridge item", and the notice tool says the customer "becomes able to receive those units billable to them". The charge rule says "The liable units are the lesser of the denied units and the units of the liability notice signed under the line's written order", where the written order is "the order that grant rests on" (compute `nt_date`/`nt_units` keyed on `related_pump_order_id=d_order`; same in the reversal, `xn_*` on `x_order`).
  - Consequence: where the newest written order is not the grant's order, a notice signed exactly as the notice policy requires is invisible to the charge policy, and the noticed units become Larkfield's write-off. Demonstrated on task 1's world. It does not change task 1's scored values.
  - Bears on: task 1 (world demonstration only).
- **C5 SOURCE-POLICY RED — compute adds a condition to daily-insulin tier 1.**
  - Evidence: rule "where a written order dated in the three months before the ship date is on that insulin pharmacy program, the daily pump insulin is the newest pump insulin dispensing's insulin divided by its own supply days" against compute `window_basis: 1 if (w_orders_3m > 0 and w_days_6m > 0) …` (set) and the same with `c_orders_3m` (cartridge).
  - Demonstration (constructed situation): an order 1 month ago and the last vial dispensing 7 months ago. The rule gives tier 1 (newest dispensing ÷ its days, > 0). The compute gives tier 3 (3-month window, 0). The set rate then differs (insulin-driven vs floor).
  - Bears on: no task (both worlds dispense within 6 months).
- **C6 SOURCE-POLICY RED — "pump insulin" filter dropped in compute.**
  - Evidence: the rule's pump insulin is "its J1817 dispensing" / "its rapid-acting 10 mL vial dispensing". Compute `w_days_3m`, `w_days_6m`, `r_days_6m`, `rate_days_6m` take `XSUM` of supply_days over every `insulin_refill_shipment`. The set compute's `n_item`, `n_units`, `n_days` take `XLATEST` over every item, and `new_ins` treats any non-J1817 newest item as vials at 1000 units.
  - Demonstration (constructed): a pump-delivery PPO program whose newest shipment is `syringes_31g_half_ml_100` (1 unit, 90 days). The set compute gives 1000/90 = 11.1 u/day; the rule takes the newest aspart or lispro vial dispensing. The cartridge compute (item-specific `cna_*`, `cnl_*`) follows the rule, so the same sentence yields two numbers inside one charter.
  - Bears on: no task (both worlds ship only aspart vials).
- **C7 SOURCE-POLICY RED — charge unit price differs between rule and compute for non-cartridge lines.**
  - Evidence: rule "The cash price per unit is the Larkfield cash price of the line's item, …" against compute `unit_price: K('cash_price_a4232') if d_item == 'A4232' else K('cash_price_a4225')`. A newest CO-151 on an A4224 line gives 38.40 per unit by the rule and 6.85 by the compute.
  - Bears on: no task (both denied lines are A4225).
- **C8 SOURCE-POLICY RED (dropped branch) — Medicare Advantage liability branch never produced.**
  - Evidence: as in override_declarations. On an MA world the base makes the member liable on a plan organization determination denial with no notice. The extended charge needs a signed notice and gives 0.
  - Bears on: no task (both PPO).
- **C9 SOURCE-POLICY RED (check 7) — set ← plan `condition` stronger than its sentence, `effect` false.**
  - Evidence: the sentence makes the gate open when the past-due amount, "after leaving out any balance an approved payment plan covers", is below the minimum. The `condition` reads "…is below the tier's past-due hold minimum, or a pump_requests payment_plan row for the program with request_status approved covers that balance", and the `effect` says "the past-due amount left after it is zero".
  - Consequence: in a world where the plan covers only part of the past-due amount, the sentence opens the gate and the condition does not. Demonstrated in task 0.
  - Bears on: task 0.
- **C10 SOURCE-FACTOR RED (unreal ladder condition) — cartridge-fill factors.**
  - Evidence: the Mobi and iLet tiers of fx_set_cartridge_fill and fx_cart_usable_fill require "the program's newest cartridge refill shipped the A4225 cartridge". A cartridge's fill is a property of the pump (Mobi 200 u, iLet 160 u). Base `reservoir_item_by_model` maps both models to A4225, and A4225 is the single HCPCS code shared by t:slim X2 and Mobi cartridges. So the conjunct holds of every Mobi or iLet program with any cartridge history (it restates scope), and it weighs nothing the business weighs. Where it fails (a Mobi with no cartridge refill yet), the fall-through gives a Mobi a 300-unit fill no Mobi cartridge holds.
  - Consequence: striking both leaves the set policy with 1 `parameter` (fx_set_defect_spares) and the cartridge policy with 1 (fx_cart_order_basis), below the floor of 2.
  - Class: fx_set_cartridge_fill, fx_cart_usable_fill (complete).
  - Bears on: task 0, task 1.
- **C11 SOURCE-FACTOR RED (mislabelled effect).**
  - Evidence: fx_nc_returns, fx_rv_returns and fx_rc_returns choose which recorded unit count (received / authorized / 0) is subtracted in an unchanged formula. fx_rv_credits chooses which adjustments are summed into an unchanged "amount less credits". Each swaps a figure; none changes the algorithm.
  - Consequence: the non-covered charge then has 0 `method` factors and the reversal has 0 (floor 1). The remittance correction keeps fx_rc_contractual, a genuine formula change.
  - Borderline members recorded as observation O10, not counted: fx_set_insulin_source and fx_cart_insulin_source (item filter plus conversion constant). Counting them as parameters would not rescue the C10 counts in the cartridge policy, and would rescue the set policy's parameter count only if they were relabelled.
  - Class (complete): fx_nc_returns, fx_rv_returns, fx_rv_credits, fx_rc_returns.
  - Bears on: task 0 (charge, reversal), task 1 (remittance correction label only).
  - Verdict strength: PLAUSIBLE (a label judgement against the skill's "substitute a different number into the same formula" test).
- **C12 SOURCE-FACTOR RED — fx_rv_credits ladder collapses, straw-man baseline.**
  - Evidence: tier 1 = corrections + waivers; tier 2 (no corrections) = waivers = corrections + waivers; tier 3 (neither) = 0 = corrections + waivers. All three tiers are one formula. The baseline "The standard review sets no credit against the charge" re-reverses corrections already on the ledger, which no business would do (the remittance correction's own baseline always nets prior corrections, `rc_prior`).
  - Bears on: task 0.
- **C13 SOURCE-FACTOR RED — fx_rc_unit_value tiers 2 and 3 cannot be told apart.**
  - Evidence: both tiers apply only when `rc_allowed == 0`, and then `rc_member = MX(0, 0 - rc_paid - rc_off)` = 0 for every `rc_off ≥ 0`. The CO-197 branch gives `MX(0, 0 - rc_paid + rc_paid)` = 0 too. So supported = 0 and the correction = amount − prior whatever the unit value. The ladder has two outcomes, not three.
  - Consequence: striking it leaves the remittance correction with 3 factors (floor 4).
  - Bears on: task 1.
- **C14 SOURCE-FACTOR RED (unreal tier) — returns tier 2.**
  - Evidence: "where a return authorization for the line is issued and nothing is received yet, the authorized units come off" credits units the warehouse has not inspected. Base pump_evt_returns credits only "When the warehouse accepts the returned units as unopened_sealed" and refuses opened units with no receipt.
  - Class: fx_nc_returns, fx_rv_returns, fx_rc_returns (complete).
  - Bears on: no task reaches tier 2 (both worlds carry receipts). Charter-level only.

Observations (no demonstrated consequence on these worlds):
- O1 Overwrites that retire nothing (narrowing restatements): the set confirmation overwrite, the cartridge confirmation overwrite, and the notice signing overwrite. They add "on that day" / "on the call, through the signing step the representative hands over". Merged semantics are unique. They leave the base caller_statement evidence contract (BLUEPRINT-KNOWN) as it is.
- O2 Duplicate bindings used to keep factor binding sets disjoint (listed above).
- O3 The cartridge baseline embeds two undeclared three-case ladders.
- O4 `RND` is not half-up; tool docstrings claim half-up or round-up that the bodies do not perform.
- O5 fx_pl_term tier 1 is unreachable on HMO/PPO.
- O6 The reversal's first-liability "none posted in those months" is ambiguous on whether it counts the reviewed charge. The compute counts it.
- O7 The cart ← hardship-waiver `effect` makes a general world claim the rule does not guarantee.
- O8 The plan ← non-covered-charge sentence spans every denied line, but the charge policy handles only the newest CO-151.
- O9 Two wordings of the same "no overstated charge" state; "larger than the units" compares dollars with units.
- O10 The insulin-source factor labels are borderline.
- O11 Courtesy and hardship-point schedules are company schedules. Payment-history discounts on Medicare beneficiaries' liability would be an inducement concern on Medicare tiers.
- O12 The reversal rule's "working on the program's largest non-covered item charge first" uses an ordering word with no second step defined.
- O14 The hardship points factors are coupled to the burden tier.
- O15 The intra-call "before posting" in four docstrings.
- O16 The reversal's late-billing courtesy counts to the charge's posting date, while its payment-history and first-liability courtesies are measured "before today", so one supported charge mixes two reference dates.

## closing_checklist

Written after both reveals (2026-10-15T08:33Z). The section above was frozen before them and is unchanged.

**Status: NOT CLOSED.** The source-layer audit does not pass, because not all four relationships hold for both tasks.

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`. This is revision 1, with no older revisions. Neither comparison section carries a PASS.
- Coverage and scope: task 0 claims {set refill, payment plan, reversal, non-covered charge}; task 1 claims {cartridge refill, notice, hardship waiver, remittance correction}. All 8 policies and 8 tools are covered, the scopes are pairwise disjoint across whole trees, and the uuid8s are independent. **OK.**
- Problem trees: each has 3 prerequisite problems, 2 value_input edges, 1 user write, and no cycle. The combined graph is acyclic. **OK** (SOURCE-CHAIN PASS for both).
- Factors: **NOT OK.**
  - Set refill: 1 parameter after C10.
  - Non-covered charge: 0 methods after C11.
  - Reversal: 0 methods after C11 and C12.
  - Cartridge refill: 1 parameter after C10.
  - Remittance correction: 3 factors after C13.
  - Both tasks: cross-category balances unsupported by their ledgers (C15-t0, C15-t1).
- Policy self-consistency: **NOT OK.** C1, C2, C9 bite task 0; C3 bites task 1; C4–C8 are charter-level.
- Gate re-run on final form: not performed. There is no final form while REDs stand, and the brief limits this audit to citing the coordinator's gate snapshot.

Verdicts: task 0 RED (SOURCE-POLICY, SOURCE-FACTOR); task 1 RED (SOURCE-POLICY, SOURCE-FACTOR); charter RED items C1–C14.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Started 2026-10-15T10:16Z. This section was written before any round-2 GT was revealed.
- Inputs (sha256, verified on disk and matching the coordinator's list):
  - `pump.extended.yaml` 6936c57f7ec17e1dee6dafb8acc0179354529e740334eda08bb18632d43ed7ac
  - `task_tools.py` 01563d460faf3b418857c7fffee1adb4919977a489ddeb51ece168bb72f85042
  - `0.view.json` 91558ccc2342bb560d65f2770c08238809ead4fafaf9d5d6f64bba4f30839912
  - `1.view.json` c0321b340ffe089929c6bee20153035fe5ed2af6dfacbb737477344b711dad4c
- Both the extended charter and the tool module changed since revision 1 (938e5048… / 6c9e70cb…), so every charter-global section below was re-derived in full, not carried forward.
- The base section is still a verbatim copy of `blueprint/products/pump.yaml` (diff clean).
- Masking is the same as in revision 1. No `tasks/*.json` was read before the revision-2 freeze, and no other scenario or difficulty was read. Scratch: `/tmp/audit_pump_0063/r2/`.
- Gate snapshot (coordinator): all OK except TRACEABILITY on unlock names, as before. Observation only.
- Auditor's disclosure: revision 1 was not archived as a file copy, so "changed" below is judged against the quotations recorded in revision 1 of this report.

### rule_compute_equivalence (rev 2)

Script-checked over all 8 policies:
- every compute binding has a `compute_basis` entry, and every basis sentence is verbatim in its rule;
- every baseline sentence is in the rule;
- every `superseded_clause` is verbatim in base, and every `replaced_by` is verbatim in its rule.

Status of each round-1 rule/compute RED:
- **C5 closed.** Daily-insulin tier 1 is now `window_basis = 1 if w_orders_3m > 0 …` in the set compute and `… c_orders_3m > 0 …` in the cartridge compute. This matches "where a written order dated in the three months before the ship date is on that insulin pharmacy program".
- **C6 closed.**
  - `w_days_3m`, `w_days_6m`, `r_days_6m` (set) and `w_days_*`, `rate_days_6m` (cartridge) now sum J1817 supply days on the Part B tier and aspart/lispro vials otherwise.
  - The set's newest dispensing now uses item-specific `nj_*`, `na_*`, `nl_*`, the same implementation as the cartridge policy.
- **C7 closed for the charge and the reversal.** `unit_price` / `x_price` now cover A4225, A4232, A4224, A4239 and E0784 by model, as the rules list them. The extra params match base `supply_cash_price_by_item` and `pump_cash_price_by_model`.
- **C7 not closed for the remittance correction (new for this report; it was missed in revision 1).**
  - Rule: "The standard value of a denied unit is the Larkfield cash price of the line's item".
  - Compute: `rc_cash: K('cash_price_a4232') if rc_item == 'A4232' else K('cash_price_a4225')`.
  - This sentence and compute were already in the round-1 charter. My round-1 class list for C7 named only the non-covered charge, so this is an auditor omission, not a regression.
  - Constructed demonstration (task 1 world, line item set to A4224, remittance with no allowed amount and no billed amount): compute 6.85 per unit gives a correction of 63.46. The rule's 38.40 gives off = 345.60, member 0, correction 87.00.
- Rounding (O4 closed): every money result that the rule says is "rounded half up to the cent" now uses `(x*100 + 0.5000001)//1/100`. The plan still rounds up correctly. Tool docstrings now say "as the governing policy rounds it", and the bodies' `round(…, 2)` only re-rounds a cent value. O15's "before posting" is gone.
- O3 (partly persists, observation): the cartridge baseline still carries the three-case covered-rate ladder. The cartridge-rate ladder is now a declared factor (fx_cart_rate_basis).

### action_binding_and_uuids (rev 2)

- Same 8 `(target_tool, computes)` pairs, each claimed once.
- uuid8 tails are unchanged and independent.
- No tool body validates anything.
- The notice tool's docstring and parameter now say the notice is "signed against" "the authorization grant record for the item that the noticed units will draw on". This is consistent with the notice, charge and reversal rules.
- No docstring carries a sequence word or names another tool.

### prerequisite_graph and prerequisite_sentences (rev 2)

The same 7 edges, kinds and resolvers. The graph is acyclic, every `policy_source` is verbatim in its own rule and absent from the depended-on rule, and every `resolved_by` equals the depended-on `target_tool` (all script-checked).

- **C9 closed.** The set ← plan `condition` now reads "…after leaving out the balance an approved pump_requests payment_plan row covers (its plan months times its monthly installment), is below the tier's past-due hold minimum", matching the sentence. The `effect` no longer claims zero (O7 closed).
- O8 closed: the plan ← charge sentence is now "…owed for the line the program's newest CO-151 denial bills", the same scope as the charge policy.
- O9 closed: both conditions read "no larger than the charge its line's liability records and payer denial support under the reversal policy".
- **C3 sentence changed.** The cartridge gate is now "The cartridge refill is not shipped until the program's past-due amount the patient-balance postings show, after leaving out any balance an approved payment plan covers, is below the tier's past-due hold minimum." This restores the base leave-out, so the charter's two refill gates now agree.
  - The edge's state can therefore be brought about by the hardship waiver or by an approved plan wherever a plan is offerable (balance ≥ tier minimum).
  - Uniqueness of the resolving write is now a per-world question. The new plan sentence "No plan is offered where the program balance is below the tier's payment-plan minimum balance" decides it, and it is checked per task.

### override_declarations (rev 2)

- **C1 closed by declaration.**
  - The charge and the reversal each declare `pump_liability_notice` "charged at the Larkfield cash price of the units concerned". Each is replaced by a self-scoped sentence ("For a non-covered item charge this policy posts, and only for such a charge, the charge is the cash price of the liable units less the courtesy percents…" / "…this policy reviews…").
  - Both replacements leave "every other patient charge" on the base rule, and each defers to the other policy's figures for its own case, so the merged meaning is unique.
  - Realism: late-billing, payment-history and first-liability courtesies are goodwill discounts off a supplier's own cash price on items the payer does not cover. That is plausible for a commercial or Medicare supplier: these are not waivers of plan cost-sharing. Their published percents (20 / 5 / 10) are moderate. No RED.
  - The base billing_correction reason ("a posting made in error") still covers the reversal's courtesy portion only by implication. Observation O17: the reversal's overwrite now makes the courtesy-reduced figure the "supported" charge, so the excess counts as an error by declaration.
- **C2 closed by declaration** in all three class members.
  - The reversal and the remittance correction declare "never for more than that posting's unpaid remainder" replaced by "…reverses the whole unsupported part … even where payments were already applied to it, and the payments it frees are applied to the program's next oldest unpaid posting or refunded under the credit-balance rule".
  - The waiver declares the same, adding "…as financial assistance refunds what a customer paid above the assisted amount".
  - Each is self-scoped and names the other two as following their own limit.
  - Realism: reversing an erroneous charge in full, and re-applying or refunding the payments it frees, is standard patient-accounting practice, and refunding payments made above an assisted amount is standard financial-assistance practice. Correct and realistic.
- **C8 closed.** The charge and the reversal now carry "where the tier is the Medicare Advantage tier and the plan issued an organization determination denial for the line's item, every denied unit is liable" (`nc_od` / `x_od` = `pump_prior_auth_denial` rows for the item). This matches base "recorded as a prior authorization denial for that item".
- **C14 closed.** All three returns ladders now read "where a corrected claim for the line has been transmitted, the returned units are the units it no longer bills…; where no corrected claim is on file but the warehouse has received unopened units … those received units; otherwise none". This matches base pump_evt_returns (re-bill by corrected claim after acceptance). The RMA-only tier is gone.
- **C4 closed.** The notice is now "signed … against the newest authorization grant for the cartridge item, the grant that refill draws on". The charge and reversal read "a liability notice signed against the line's grant" (`related_pump_order_id=d_grant` / `x_grant`), and the cartridge refill reads the newest notice for the item. All key the same record.
  - Base defines no `related_pump_order_id` meaning for a notice; db_schema defines it only for PA requests, grants and denials. So keying the notice on the grant is a consistent convention, not a departure.
  - Replay on the task 1 world: a hypothetical CO-151 on the new shipment now finds the 12-unit notice, liable 10.
- The confirmation and signing overwrites are unchanged (O1 persists: they narrow and retire nothing).

### factor_ladders (rev 2)

| policy | factors (label) | #p/#m | multi-source | cross-difficulty | round-1 items |
| --- | --- | --- | --- | --- | --- |
| set refill | span (m), insulin_source (p), rate_basis (m), dose_window (m), defect_spares (p) | 2/3 | rate_basis | insulin ×3 | C10 closed (fill is now the fixed device sentence "Mobi fill for a Tandem Mobi, the iLet fill for a Beta Bionics iLet and the standard fill for every other model"); O10 resolved by relabel |
| payment plan | left_out (m), term, household, insulin_balance, history, aged (p) | 5/1 | household | cgm, insulin | unchanged; O5 persists |
| charge | cover, returns, late, pay, first (p), liability (m) | 5/1 | liability (tier × OD record / notice × shipment date) | none | C11 closed (returns relabelled; new honest method: identity / lesser-of / zero) |
| reversal | cover, returns, late, pay, first (p), liability (m) | 5/1 | liability | none | C11, C12 closed (credits is now the fixed sentence "The credits set against the charge are the billing corrections and hardship waivers already posted against it", no straw man) |
| cartridge | span (m), order_basis (p), insulin_source (p), dose_window (m), rate_basis (m) | 2/3 | rate_basis | insulin ×3 | C10 closed |
| notice | period (m), allowance (p), expected (p), insulin_cap (m) | 2/2 | none | insulin | fx_nt_further replaced by fx_nt_insulin_cap. Cap: prescribed dose ÷ fill / 6-month dispensed ÷ fill / none, three different formulas. Realistic: a notice no larger than the dose needs |
| waiver | burden (m), effort, aged, history, balance, cost (p) | 5/1 | burden | insulin (+cgm) | unchanged |
| remittance | covered_rate, unit_value, returns (p), contractual (m) | 3/1 | covered_rate tier 2 | none | C13 closed (see below). CO-197 tier replaced by CO-29 ("the whole member responsibility … comes off"), which matches base "CO-29 … never billed to the customer; Larkfield writes it off with a billing_correction adjustment" |

C13 check:
- Member responsibility is now "the remittance's allowed amount less the payer's payment, or the posted amount where the remittance itemizes no allowed amount", so unit-value tiers 2 and 3 now give different corrections.
- Constructed demonstration (task 1 world, allowed 0): tier 2 (billed 456.45/51 = 8.95) gives 81.01; tier 3 (cash 6.85) gives 63.46.

Script checks:
- no factor binding reads, transitively, another factor's binding or `result`;
- every ladder has 3 tiers in rule and compute;
- every fall-through equals its baseline.

O2 persists: duplicate bindings `w_variant`, `r_variant`, `rt_variant`, `cap_variant` are copies of the insulin-source variant read, used to keep binding sets disjoint. They read the raw program tier, not the source factor's decided value. No consequence was demonstrable: substituting the source factor's baseline zeroes the daily insulin whatever these tiers take.

### findings (rev 2)

- C1, C2, C3 (sentence), C4, C5, C6, C8, C9, C10, C11, C12, C13, C14: closed, as above. C15 is per-task and judged in each task file.
- **C7-r2 SOURCE-POLICY RED (class remainder, auditor-missed in revision 1).** The remittance correction's `rc_cash` does not implement "the Larkfield cash price of the line's item" for non-cartridge lines. Bears on no task: task 1's reviewed line is A4225.
- Observations still open: O1, O2, O3 (partial), O5, O16, O17. O4, O6, O7, O8, O9, O12, O15 are closed.

### closing_checklist (rev 2)

Written after the round-2 reveal (2026-10-15T10:23Z).
- Task files correspond one-to-one with the tasks. Revision 1 is preserved unchanged above each `revision_2` section. Both rev-2 comparisons carry PASS.
- Scopes unchanged: disjoint and complete over the 8 policies and 8 tools. The uuid8s are independent.
- Problem trees: 3 prerequisite problems, 2 value_input edges and 1 user write in each task; the combined graph is acyclic.
- Factors:
  - set 5 (2p/3m), plan 6, charge 6, reversal 6, cartridge 5 (2p/3m), notice 4 (2p/2m), waiver 6, remittance 4 (3p/1m);
  - each task has a multi-source factor and a cross-difficulty factor, backed by consistent seeded ledgers;
  - every factor bears weight on its task's world, and every all-baseline value is definite and differs from gold.
- Charter self-consistency: **one RED remains, C7-r2.** The remittance correction's `rc_cash` defaults every non-A4232 line to the A4225 price, while its rule says "the Larkfield cash price of the line's item". It has no task consequence. It was present in round 1 and missed by this auditor's round-1 class listing; it is not a regression.
- Gates: not re-run by this audit; the coordinator's round-2 snapshot is cited.

**Status: tasks 0 and 1 PASS. The difficulty is not closed while charter item C7-r2 stands.**

## revision_3

### charter_global_frozen (rev 3)

- Started 2026-10-15T10:40Z. This section was written before the round-3 GT reveal.
- Inputs (sha256, verified):
  - `pump.extended.yaml` f1be48af900cfcdd59bab6adf0da3f18ef1e9e556d5aafa02c2816fe8307ceae (changed; snapshot kept at `/tmp/audit_pump_0063/r3/ext_r3.yaml`)
  - `task_tools.py` 01563d46… (unchanged)
  - views 91558ccc… / c0321b34… (unchanged)
- The base section is still verbatim.
- Because the charter hash moved, all charter-global checks were re-run: verbatim basis, baseline sentences, overwrite clauses, prerequisite sources and resolvers, factor independence, and ladder shape. All are clean (`r2/checks.py`).
- Factor structure is unchanged from revision 2 (same ids, labels and counts in all 8 policies). `action_binding_and_uuids` is carried forward on the unchanged tool hash.

### findings (rev 3)

- **C7-r2 closed.**
  - The remittance correction's `rc_cash` now maps A4225, A4232, A4224, A4239 and E0784 (by pump model) to the matching params (38.40, 395.00 and the four pump prices match base `supply_cash_price_by_item` / `pump_cash_price_by_model`).
  - Rule and basis read "The standard value of a denied unit is the Larkfield cash price of the line's item: the A4225 cash price for an A4225 cartridge, … and the pump cash price for the program's pump model for an E0784 pump."
  - The round-2 constructed demonstration (A4224 line, no allowed or billed amount) now gives `rc_cash` 38.40 and a correction of 87.00, matching the rule.
- **C7-class sweep** (charge `unit_price`, reversal `x_price`, remittance `rc_cash`): all three are identical item maps.
  - A pump model outside the four now prices at 0. That branch is unreachable: `pump_model` is an enum of exactly those four (base `reservoir_item_by_model`, `pump_cash_price_by_model`).
  - No other compute binding reads a cash price.
- **Regression replay:** both view worlds were re-run end to end with the auditor's derived writes. Every scored value, every per-factor baseline value, every all-baseline value, every skip and reorder replay, and the C4 and C13 demonstrations are identical to revision 2.
- **Observation O18 (new, no task consequence).** In the charge, reversal and remittance correction, `baseline.params` lists `cash_price_a4224/a4225/a4232/a4239` but not the four pump-price keys that the baseline sentence "the pump cash price for the program's pump model for an E0784 pump" uses. The metadata names fewer default keys than the baseline reads. It bites only an E0784 line, which neither world has.
- Open observations: O1, O2, O3 (partial), O5, O16, O17, O18.

### closing_checklist (rev 3)

Written after the round-3 reveal (2026-10-15T10:41Z).
- Task files correspond one-to-one with the tasks, and revisions 1–3 are preserved in order. Both rev-3 comparisons carry PASS.
- Coverage: all 8 policies and 8 tools; scopes disjoint across whole trees; uuid8s independent.
- Problem trees: 3 prerequisite problems, 2 value_input edges and 1 user write in each task; the combined graph is acyclic.
- Factors: 4–6 per computation (2 parameter / 1 method floor met everywhere). Each task has a multi-source and a cross-difficulty factor on consistent seeded ledgers. Every factor bears weight against an honest baseline, and every all-baseline number is definite and differs from gold.
- Charter self-consistency: all REDs closed (C1–C14, C7-r2). Open observations O1, O2, O3 (partial), O5, O16, O17 and O18 carry no demonstrated consequence.
- Gates: the coordinator's round-3 snapshot is cited (all OK except TRACEABILITY on unlock names, which is deferred to KB render). This audit did not re-run them.

**Status: CLOSED at the source layer. Tasks 0 and 1 PASS; the charter is clean.**

## revision_4

### charter_global_frozen (rev 4)

- Started 2026-10-15T12:21Z. This section was written before the round-4 GT check.
- Inputs (sha256, verified):
  - `pump.extended.yaml` f8c4bf1c264e8bc6a1f5f3c85c073de7045b681e267507fae7e2d754765ae089 (changed; snapshot at `/tmp/audit_pump_0063/r4/ext_r4.yaml`)
  - `task_tools.py` 01563d46… (unchanged)
  - views 91558ccc… / c0321b34… (unchanged)
- The base section is verbatim, and every non-extended top-level key is equal to the round-3 snapshot.
- Read for this round, as the coordinator allowed: `audits/render_source/insulin_pump_program_services/findings.md` (F1–F7) and the source-side notes S1–S3 in `audits/policy_kb/insulin_pump_program_services/{0,1}.md`.
- A structured diff against `/tmp/audit_pump_0063/r3/ext_r3.yaml` (`r4/cmp.py`) shows changes only in rule, compute_basis, baseline, factor ladder text, three compute bindings (`cgm_active`, `x_pr204` / `x_co197` / `x_gthru`, `x_denied`), and the notice overwrite. No tool changed.
- Gate snapshot: all OK, including TRACEABILITY.
- Structural checks re-run and clean: verbatim basis, baseline sentences in rule, overwrite clauses, prerequisite sources and resolvers, factor binding independence, ladder shape.
- Both worlds were replayed end to end. Every scored value, per-factor figure, all-baseline figure, skip and reorder result is identical to revision 3, which confirms "values_changed=none".

### item-by-item verification (rev 4)

| item | change | verdict |
| --- | --- | --- |
| F2 reversal of non-CO-151 charges | Denied units now follow the denial: CO-151 as before; "where a PR-204 denial answers it, or a CO-197 denial does and the grant the line drew on was not valid on its ship date so that the denial is not appealed, every unit of the line is denied"; compute `x_pr204`, `x_co197`, `x_gthru`. This matches base pump_evt_denials_and_appeals routing PR-204 and unappealable CO-197 to pump_liability_notice. | **closed**. O19 below |
| F3 "a notice" vs newest | Rule now reads "the newest liability notice signed against the line's grant was signed on or before the line's ship date … a notice signed after the ship date covering only later lines of the grant", in the charge and the reversal (rule + ladder). This matches the compute LATEST. Plausible: a later notice belongs to later shipments. | **closed** |
| F4 past-due hold days 0 | Both refill rules add "On a tier whose past-due hold days are 0, the refill is never held for a past-due balance"; both edge conditions add "on a tier whose past-due hold days are 0 the gate does not apply". This matches `parameter_schema.past_due_hold_days` ("0 = shipments are never held"). | **closed** |
| F5 household without an active CGM program | Tiers now require "holds an active CGM program", with fall-through "otherwise, including where the customer holds no active CGM program"; compute `cgm_active` added to fx_pl_household bindings. Disjointness holds (script). | **closed** |
| F6 notice overwrite | `superseded_clause` is now just "the customer signs it personally". "and no Larkfield representative can sign it for them" is no longer superseded and stays inherited, so no in-force part is dropped. The replacement still only narrows the channel (O1). | **closed** (O1 persists) |
| F7 window boundaries | All four refill/plan/charge/notice/waiver/reversal/remittance rules now state the same-day-of-month convention for orders and for every N-month window. This matches `within_months` (record in [0, N) months) and the plan's aged test (on or before the same day = outside the window). | **closed** |
| S1 remittance CO-151 deduction | Now "the denied units, as the payer denied them and before any returned units come off, times the value of a denied unit come off"; the ladder says the same. This matches compute `rc_off = rc_denied * rc_unit_value`. Realistic: a contractual denial is fixed by the payer's own units. The second reading (6.21 on task 1) is excluded. | **closed** (it was a task-1 unique-solution exposure that I missed in rounds 1–3) |
| S2 baselines naming factor-only quantities | Each `baseline.rule` now ends with one "In the standard computation …" sentence that gives a definite number with no factor quantity. Checked on both worlds: set 30, plan 42.15, charge 0.00, reversal 342.50, cartridge 54, notice 9, waiver 19.50, correction 0.00. All equal the all-factor-baseline substitutions and differ from gold. Every sentence is in its rule. | **closed**. O18 widened below |
| S3 which application or plan is read | Rule and ladder now say "the most recently received such application" / "the most recently received approved plan", matching compute LATEST by `received_at`. | **closed** |
| **F1 burden tier reads the points factors** | Rewording only. Each points sentence now carries "which count toward the waiver share only where exactly one of the customer's active pump-delivery insulin pharmacy program and active CGM program carries a balance above zero". Compute, ladder and factor structure are unchanged. | **NOT closed** — see C16 and C17 |

### findings (rev 4)

- **C16 SOURCE-FACTOR RED — factor independence (F1, not closed by rewording; auditor-missed in rounds 1–3).**
  - Symptom: fx_hw_burden's tier 2 method is "the waiver is the waiver base times the standard share percent plus all the points, never more than 100 percent". That tier's outcome is assembled from the outputs of fx_hw_effort, fx_hw_aged, fx_hw_history, fx_hw_balance and fx_hw_cost_share. The round-4 points sentences now also make each points factor's effect conditional on fx_hw_burden's own tier condition. So the dependency runs both ways.
  - Evidence: compute `share_pct = MN(100, K('standard_share_pct') + effort_pts + aged_pts + history_pts + balance_pts + cost_pts)` and `result = hw_base if burden_basis == 1 else (… hw_base * share_pct … if burden_basis == 2 else std_waiver)`.
  - Demonstration (task 1 world): with fx_hw_burden on tier 2, its outcome is 31.20. Substituting any single points factor's baseline changes that same tier's outcome (29.25, or 27.30 for cost share), so the tier's value is not fixed by its own records. Substituting fx_hw_burden's baseline makes all five points factors decoration at once (19.50 whatever they take).
  - This is the coordinator's standing focus item ("no tier reading another factor's binding or output"). In rounds 1–3 I carried it only as observation O14 because the bindings themselves are disjoint. That was an under-call, disclosed here; the structure has not changed since round 1.
  - Affected: pump_ext_hardship_waiver_amount (fx_hw_burden ladder[1], the five points factors, `share_pct` / `result`). Bears on task 1.
- **C17 SOURCE-POLICY RED (new in round 4) — the points sentences' scope disagrees with the burden rule and compute.**
  - The burden sentence reads "where the customer's active insulin pharmacy program and active CGM program each carry a balance above zero …; where exactly one of them carries a balance above zero …". Compute `ins_balance = CFIELD('insulin', 'patient_balance_due', status='active')` has no delivery-method filter.
  - The new points sentences condition on "the customer's active **pump-delivery** insulin pharmacy program".
  - Demonstration (constructed: task 1 world after the correction, insulin program set to pen delivery): rule and compute burden take tier 2 → share 80% → 31.20. Read by the points sentences, no pump-delivery program carries a balance, so no points count → 50% × 39.00 = 19.50.
  - Bears on no task (task 1's insulin program is pump-delivery), but it is a charter contradiction introduced by the F1 rewording.
- Observations:
  - O18 (widened): `baseline.params` still omits the pump-price keys in charge, reversal and remittance correction. It now also lists keys the rewritten baselines no longer read: `standard_fill` (set); `fill_*`, `pump_insulin_unit_insulin`, `vial_insulin` (notice).
  - O19 (new): the reversal's CO-197 branch tests only the drawn grant's valid-through date. Base appealability reads "an authorization grant valid on the date of service" (any grant), and base refill eligibility forbids drawing an expired grant, so the branch is reachable only in base-inconsistent worlds. No task consequence.
  - O1, O2, O3 (partial), O5, O16 and O17 are unchanged.
- C1–C15 and C7-r2 remain closed (re-verified by the replay).

### closing_checklist (rev 4)

**Status: NOT CLOSED.**
- Task 0 PASS.
- Task 1 RED (SOURCE-FACTOR, C16).
- Charter RED items: C16, C17.
- All other checklist items are as in revision 3.
- Gates: the coordinator's snapshot (all OK) is cited, not re-run.

## revision_5

### charter_global_frozen (rev 5)

- Started 2026-10-15T12:54Z.
- Inputs (sha256, verified):
  - `pump.extended.yaml` 2cb90ffa1c232994a1fd2e2523c37094fdbe4b3714d61e0387c82a59369ee015 (snapshot `/tmp/audit_pump_0063/r5/ext_r5.yaml`)
  - `task_tools.py` 01563d46… (unchanged)
  - views 91558ccc… / c0321b34… (unchanged)
- The base section is verbatim.
- A structured diff against the round-4 snapshot (`r5/cmp.py`) shows that only `baseline.params` changed in seven policies. The hardship waiver also changed in rule, compute_basis, factors, compute (`ins_balance`) and cross_category. The other policies' rules, computes and factors are untouched.
- Structural checks re-run and clean: verbatim basis, baseline sentences in rule, overwrite clauses, prerequisite sources and resolvers, transitive factor independence, and ladder shape.
- Both worlds were replayed. Every scored, per-factor, all-baseline, skip and gate figure is identical to revision 4, so values_changed=none is confirmed. The GT, re-read at 12:54:55Z, is identical.
- Gate snapshot: all OK.

### item-by-item verification (rev 5)

| item | change | verdict |
| --- | --- | --- |
| C16 factor independence | fx_hw_burden's ladder now reads "the waiver is figured in the whole-base mode / points mode / flat mode". The share is assembled once, in "The waiver is the waiver base times its share …: in the whole-base mode the share is 100 percent, in the points mode it is the standard share percent plus every point the program earns under the scoring below, never more than 100 percent, and in the flat mode it is the standard share percent", and in compute `share_pct` / `result`. Each points sentence is now unconditional ("the program earns the full … points"). No tier reads another factor's output (script plus reading), and assembly sits in the result. Fall-through "flat mode" = baseline `burden_basis: '3'` = "The standard waiver mode is the flat mode". | **closed** |
| C17 pump-delivery scope | Rule "the active insulin pharmacy program whose delivery method is insulin pump", ladder tier 1 the same, compute `ins_balance = CFIELD('insulin', 'patient_balance_due', status='active', delivery_method='insulin_pump')`, and cross_category reads `delivery_method`. Constructed pen-delivery world: rule and compute both give flat mode, 19.50. | **closed** |
| O18 baseline.params | Set `["supply_days_per_shipment","block_days","standard_sets_per_30_days","a4224_days_per_unit"]`; plan adds `payment_plan_min_balance_usd`; notice trimmed to the three keys it reads; the charge, reversal and remittance correction add the four pump-price keys. | **closed** for the omissions. Residual over-listing: the reversal and remittance-correction baselines read no cash price yet list them. Observation, no consequence |

### findings (rev 5)

- No RED remains. C1–C17 and C7-r2 are closed.
- Observations:
  - O18 residual over-listing (above).
  - O20 (new, cosmetic): five sentences still read "The standard waiver carries no … points" after the sentence defining "the standard waiver" was replaced by "The standard waiver mode is the flat mode". The meaning is unchanged (the standard computation adds no points), and nothing contradicts it.
  - O1, O2, O3 (partial), O5, O16, O17 and O19 are unchanged and have no consequence.

### closing_checklist (rev 5)

- Tasks 0 and 1 PASS on all four relationships, with revisions 1–5 preserved in order.
- Scopes are disjoint and complete; trees have 3 prerequisite problems, 2 value_input edges and 1 user write; the graph is acyclic.
- Factors are 4–6 per computation, meet the 2-parameter / 1-method floor, include a multi-source and a cross-difficulty factor per task, bear weight against an honest baseline, and have definite all-baseline numbers that differ from gold.
- The charter is clean. Gates: the coordinator's round-5 snapshot is cited.

**Status: CLOSED at the source layer.**
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (rev 6)

- Started 2026-10-15T16:19Z.
- Inputs (sha256, verified):
  - `pump.extended.yaml` fa4db57cbeb262387a9de22de8eaf6ee69d569511d4d5119e694c2db72594528 (snapshot `/tmp/audit_pump_0063/r6/ext_r6.yaml`)
  - `task_tools.py` 01563d46… (unchanged)
  - views unchanged
- The base section is verbatim.
- Read for this round: `audits/render_source/XF_recipe.md` and `audits/policy_kb/insulin_pump_program_services/1.md` revision_2 (S-XF members 1–14, R2-1).
- Structured diff against the round-5 snapshot (`r6/cmp.py`):
  - All eight policies changed in rule, compute_basis, factor ladder text and baseline.
  - Compute changed in only four places: `ins_source` / `c_src` (fall-through now J1817 counting); reversal `x_gfrom` and `x_denied` (valid-from test); hardship `burden_add`, `share_pct`, `result`, and `std_waiver` removed.
  - Params: hardship `standard_share_pct` 50→40, new `burden_points` 10.
- Structural checks re-run and clean: verbatim basis, baseline sentences in rule, overwrite clauses, prerequisite sources and resolvers, transitive factor independence, ladder shape.
- Replay of both worlds: every scored value and every per-factor / all-baseline figure is identical to revision 5, except the two hardship baselines the coordinator announced (burden 19.50→27.30, all-baseline 19.50→15.60). The GT, re-read at 16:22:20Z, matches all of it.

### verification (rev 6)

| item | verdict | evidence |
| --- | --- | --- |
| S-XF 1–8 (baselines and results naming factor quantities) | **closed** | Every `baseline.rule` is now a standard method in record terms ending in one "In the standard computation …" sentence. A keyword sweep finds no factor quantity or zero-default phrase; the only hits are "model". Every `result` basis is one generic sentence ("Each adjustment set out above changes the standard figure it names, replacements before additions …" and similar), with an explicit order where it matters (replacements, then amounts taken off, then percentage reductions; replacement before additions in the waiver). These match the compute order, e.g. reversal `MX(0, x_liable - x_returned) * x_price * (100 - …)/100` = replace, then subtract floored at 0, then percent. Baseline outputs are definite and differ from gold: set 30, plan 42.15, charge 0.00, reversal 342.50, cartridge 54, notice 9, waiver 15.60, correction 0.00. |
| S-XF 9–12 (rate and window factors reading counted or daily insulin) | **closed** | "The customer's pump insulin …" and "The daily pump insulin is, in the standard way, …" are now defined once in each refill policy's standard method. The rate and window factors read those standard quantities and their own pump-insulin item ("J1817 on the … Part B … and rapid-acting 10 mL vials on any other tier"), never another factor's tier. The script finds no factor binding that reads another factor's binding transitively. |
| S-XF 13 (contractual factor reading returns) | **closed** | "the denied units, as the payer denied them, times the value of a denied unit are taken off". The returns scaling is its own sentence, and the order sits in the generic result sentence. Compute is unchanged (`rc_off = rc_denied * rc_unit_value`). |
| S-XF 14 (notice cap reading expected rate) | **closed** | The cap sentence states its own change ("the expected rate is held to no more than …"), and "replacements before limits" is stated generically. Compute is unchanged. |
| R2-1 (reversal CO-197 grant validity) | **closed** | Rule "the grant the line drew on did not cover its ship date, its valid-from date being later or its valid-through date earlier than the ship date"; compute adds `x_gfrom > x_date`. O19 persists: base appealability reads any grant valid on the date of service. |
| Hardship restructure: realism of the 40% standard share | **acceptable** | A partial-waiver default of 40% for an approved application, rising by fixed points to at most 100% and replaced by 100% when both other programs carry balances, has the shape of published sliding-scale financial-assistance schedules (partial discounts in 10–20-point steps, full waiver at the top). It is reachable as the fall-through (no other-program balance, no points earned). |
| Hardship restructure: method tiers | **closed** | fx_hw_burden tiers are "replaced with 100 percent" / "the burden points are added" / "nothing is added": three distinct outcomes. It reads only its own two balances and outputs only its own change. Points factors add their own points unconditionally. |
| Insulin-source fall-through (J1817) | **acceptable** | Tiers: non-Part-B program → vials at 1000; no program → none; otherwise (Part B program) → J1817 at 50. These are pairwise disjoint and distinct, and the fall-through is reachable on the Original Medicare tier and is realistic (HCPCS J1817 = 50 units). The baseline still bears weight on both worlds (30 / 20). |
| Factor floors | **held** | set 2p/3m; plan 5p/1m; charge 5p/1m; reversal 5p/1m; cartridge 2p/3m; notice 2p/2m; waiver 5p/1m; correction 3p/1m. Multi-source and cross-difficulty per task as in revision 5. |

### findings (rev 6)

- No RED. All previous REDs remain closed.
- Observations with no consequence: O1, O2, O3 (partial: the cartridge baseline still states the covered-rate three-case rule), O5, O16, O17, O18 residual, O19.
- O20 is moot: the "standard waiver" sentences are gone.

### closing_checklist (rev 6)

- Tasks 0 and 1 PASS on all four relationships, and revisions 1–6 are preserved.
- Scopes, trees and factors are as in revision 5, with the floors held.
- The charter is clean. Gates: the coordinator's round-6 snapshot (all OK) is cited.

**Status: CLOSED at the source layer.**
VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
