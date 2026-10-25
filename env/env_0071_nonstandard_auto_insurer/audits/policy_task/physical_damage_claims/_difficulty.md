# Policy-task audit — physical_damage_claims / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-18T10:45Z, auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes verified on read (match the coordinator brief):
  - `tasks/physical_damage_claims/physdam.extended.yaml` sha256 4626ce7d0824e214d8084f6b3589ffd34bb61b8f85a64ec6a0395b9aabd561cb
  - `tasks/physical_damage_claims/task_tools.py` sha256 43a3e10b642a8ed6ba8cddafdd921de11099cfdb7c650884abf6815eec8b2d54
  - masked views `.audit_views/policy/physical_damage_claims/r1/0.masked.json` fdf380eb…ed490, `1.masked.json` af9278fe…61cb (keys kept: frozen_time, user_scenario, initial_state; `_masked_keys` lists the rest).
- Read: blueprint.yaml, db_schema.json (enums), share_tools.py (finder signatures), products/physdam.yaml (base), products/auto.yaml and products/rental.yaml (rules/params of the rows the factors read), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the two masked views.
- Masked / unread when this section was written: every task's evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure; plan.md; both worklog.md files; the sibling audit dir `audits/policy_task/sr22_fr44_filings/`. No recursive grep touched `tasks/`. This section contains nothing derived from a revealed GT.
- Entry conditions (Step 0): gate snapshot `/tmp/erl0071_coord/snap_physical_damage_claims_r1.txt` present, seven gates rc=0 (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK); masked views with hashes supplied. Inputs complete.
- Base copy: the ten top-level keys of the extended file (`category` … `policies`) are `==` to `blueprint/products/physdam.yaml` (python yaml compare, all True); only `extended_policies` is added.

### policy_conflict_scan
Five extended policies, one target tool each:

| policy | target_tool (owner) | subject | prerequisite |
| --- | --- | --- | --- |
| physdam_ext_repair_assignment | assign_repair_payment_77b6ee43 (user) | physdam_repair_payment | [] |
| physdam_ext_deductible_refund | issue_deductible_refund_f60554e2 (agent) | physdam_deductible_reimbursement | ← repair_assignment (value_input, gate deductible_borne) |
| physdam_ext_lienholder_settlement | pay_loss_payee_settlement_0684ec8f (agent) | physdam_total_loss_payment (payee loss_payee) | [] |
| physdam_ext_owner_tax_title | accept_total_loss_settlement_6ed13516 (user) | physdam_total_loss_payment (payee named_insured) | ← lienholder_settlement (value_input, gate tax_base) |
| physdam_ext_totaled_coverage_return | remove_totaled_coverage_12b8272a (agent) | physdam_coverage_removed + physdam_premium_returned | ← owner_tax_title (value_input, gate return_days) |

- Overlapping subjects: the two total-loss-payment policies are split by payee (loss payee vs named insured) and each names the other's case in its replaced_by; the repair and loss-payee policies both retire the base deductible clause and each names the other's case. Scopes partition cleanly.
- Claimed scopes of the two tasks (from the masked personas and seeds, not from charter_scope): task 0 = {repair_assignment, deductible_refund}; task 1 = {lienholder_settlement, owner_tax_title, totaled_coverage_return}. Pairwise disjoint and jointly complete over the five extended policies.
- Trigger rule (XF 14): every event the tools write (physdam_repair_payment, physdam_deductible_reimbursement, physdam_total_loss_payment, physdam_coverage_removed → physdam_premium_returned with transaction_reason coverage_removed) has `triggers: []` or a physdam-only trigger in base `events`. Nothing lands in another category. CLEAN.
- Cross-category read boundaries: reads are auto (garaging_state, term_number, violation_points, term_days, CPARAM insured_cancel_short_rate_retention_pct, replacement_vehicle_reporting_days, auto_policy_changes.vehicle_acquired_date) and rental (rental_benefit_transactions.amount by claim_number). Nothing is written outside physdam.
- Conflicts found: see `findings` C-POL-1 (deductible-refund prerequisite vs its own total-loss tiers) and C-POL-2 (non-commuting deductible adjustments with no fixed order, XF 3).

### rule_compute_equivalence
- Mechanical sweep (scratch script, whitespace-normalised): every `compute_basis` quote in all five policies is verbatim in its own `rule` (XF 4 CLEAN). Every `baseline.rule` sentence is in the rule. Every `replaced_by` is in the rule. Every `policy_source` is in the rule.
- Bindings with no compute_basis entry: repair_assignment `earlier_cash`, `earlier_cash_deductible`, `earlier_facility`; lienholder_settlement `lp_earlier_cash`, `lp_earlier_ded`, `lp_earlier_fac`. These are the all-minus-this subtractions and are backed in words by "earlier claims are every claim on the coverage other than the claim being paid/settled", which is quoted on the sibling bindings. Observation O-1.
- Ladders vs compute (tier by tier, all 28 factors): every tier `factors[].ladder` names is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier. Enum check against db_schema: collision codes `collision_with_vehicle`/`collision_single_vehicle`, everything else (`comprehensive_theft|glass|weather|animal|fire|vandalism`) is comprehensive, as the rules say; driver statuses match the permissive-operator parenthesis.
- Rounding (XF 6): each rule's rounding sentence ("rounded once to the nearest cent at the end and never below zero") matches `MX(0, RND(…, 2))` as the outermost step in all five results. CLEAN.
- Date boundaries (XF 8, part): appraisal wait (estimate day counted, confirmation day not) = DAYS(conf, est); held days (loss day counted, acquisition day not) = DAYS(acq, loss); replacement "no more than … days after the declaration" = DAYS(decl, acq) ≤ window, "on or after the date of loss" = DAYS(loss, acq) ≥ 0; late days = DAYS(decl, NOW) − paid-through; return days (expiration counted, start not); "dated before that claim's date of loss" = DAYS(charge, loss) > 0; in-force days (today counted). All match.
- Same-day ties (XF 8, part): claim LATEST reads are covered by the stated invariant "a vehicle never has two claims reported on the same day". Not stated: coverage_return `latest_charge_*` (LATEST premium charge by transaction_date, no tie rule) and owner_tax_title `replacement_acquired` (XLATEST vehicle added by change_effective_date, no tie rule). See finding C-XF8.
- Factor-only plain bindings (XF 1): `repair_payment_count` (deductible_refund; read only by repair_part_measure's `repair_damages`, outside its bindings, and a duplicate of `source_repair_count`); `lp_cause` (lienholder; read only by `lp_surcharge`, outside lp_permissive_operator's bindings, duplicate of `lp_cause_for_deductible`); `lp_loss_date` (lienholder; read only by `held_days` of recent_purchase, outside its bindings); `tt_loss_date` (owner_tax_title; read only by `acquired_after_loss` of replacement_share, outside its bindings). No factor reads another factor's binding or output (checked binding by binding). See C-XF1.

### action_binding_and_uuids
- `(target_tool, computes)` pairs: five distinct tools, each claimed by exactly one policy, each `computes: amount`. CLEAN.
- uuid8 tails 77b6ee43, f60554e2, 0684ec8f, 6ed13516, 12b8272a: no shared prefix, no sequence, no adjacency. CLEAN.
- Factor ids vs tool names (XF 15): no factor id is a substring of any tool name (scripted). CLEAN.
- Tool bodies: each performs one create (+ coverage update) with the supplied values; none reads a claim state, a prior payment or a prerequisite, none refuses or warns. CLEAN.
- Docstrings (XF 7): no example values (format specs only: `CLM-<9 digits>`, "2 decimal places", "0.00 when none"). The claimed effects match the bodies (payment row, net claim payments += amount; removal sets status/removal_reason/closed_date, books physdam_premium_returned, lowers term_coverage_premium). Narrative clauses ("the facility receives the funds") claim no record effect. Each Args line carries "read from the coverage lookup before the call", which is an ordering word about a read, not about another problem. Observation O-2.

### prerequisite_graph
- Every extended policy has `prerequisite` filled ([] for repair_assignment and lienholder_settlement). Three edges, all `problem` ids are extended policies of this file, none points at itself or at a base policy. Graph: repair_assignment → deductible_refund; lienholder_settlement → owner_tax_title → totaled_coverage_return. Acyclic.
- Each `policy_source` is verbatim in the blocked policy's own rule (sweep). All three are `form: state`, no `fallback_reason`, correct.
- `resolved_by` = the depended-on policy's target_tool in all three. `kind: value_input` with `gate` = an existing binding of the blocked compute (`deductible_borne`, `tax_base`, `return_days`), and each resolving write changes that binding's value (the payment row is read by the binding's tier condition). No authoring-viewpoint phrasing in the prerequisite fields.
- `condition` vs sentence: E1 "carries a repair payment whose estimate sequence is the highest estimate sequence recorded on the claim" = "a repair payment stands on the claim for its latest recorded estimate" (the sentence also scopes to "a claim that records a repair estimate"; the condition drops that scope word, harmless since the condition presupposes an estimate). E2 and E3 match word for word in meaning. CLEAN apart from C-POL-1 (scope of E1).

### prerequisite_sentences
- E1 "The deductible refund on a claim that records a repair estimate is figured only after a repair payment stands on the claim for its latest recorded estimate." Connective "only after"; state named in record words (repair payment, estimate sequence on physdam_claim_payments); no tool, id or snake_case; one write of this difficulty produces it (assign_repair_payment_77b6ee43 is the only tool that books a physdam_repair_payment). Derivation: the state is a repair payment on the claim → the only policy whose rule defines a repair payment written here is physdam_ext_repair_assignment ("the repair payment the named insured directs to the repair facility") → its tool. Single reading. Scope defect: see C-POL-1.
- E2 "The owner's tax-and-title payment is not figured until a total loss payment to the loss payee stands on the claim." Connective "not until"; record state (total loss payment, payee loss payee); one write produces it (pay_loss_payee_settlement_0684ec8f; accept_total_loss_settlement writes payee named_insured). Derivation: state → physdam_ext_lienholder_settlement ("the total loss payment made to the loss payee") → its tool. Single reading.
- E3 "The coverage return on a vehicle whose latest claim records a total loss declaration is figured only after a total loss payment to the named insured stands on that claim." Connective "only after"; record state; one write (accept_total_loss_settlement_6ed13516). Derivation: state → physdam_ext_owner_tax_title ("the total loss payment made to the named insured … for the sales tax, the title fee and the owner's other settlement items") → its tool. Single reading.
- The depended-on rules do not restate the sentences; no rule carries a second wording, a tool name or another problem's id; no rule states a cross-problem order that grounds no edge (the cross-references "under its own rule" / "under the loss-payee settlement rule" carry no ordering connective). Docstrings are silent about sequence between writes.
- Base sentence "A deductible reimbursement is made only after a subrogation recovery has been received on the claim." states an order on a record no tool of this difficulty writes; it grounds no edge. Observation-free.

### override_declarations
Sentence by sentence against each `base_policy_refs` entry.

physdam_settlement (cited by repair_assignment, lienholder_settlement, owner_tax_title):
1. "A claim payment is issued only after a coverage confirmation is recorded for the claim." — followed by all (no extended text touches it; inherited).
2. "The deductible is the package's collision_deductible … applied once per claim;" — retired by repair_assignment (assigned repair payments) and lienholder_settlement (vehicle value to a loss payee); sibling replaced_by texts each exclude the other's case by name and restate the in-force rule for every other payment (XF 5a, 5c met). The trailing clause "no deductible applies to windshield repair or replacement in windshield_zero_deductible_states, nor to glass that is repaired rather than replaced" stays in force; repair_assignment's glass tier (all glass in a zero state) and its glass-repair carve-out sit inside its declared deductible scope. Followed.
3. "A repair payment is the latest cumulative repair estimate less the deductible less repair payments already made on the claim." — retired by repair_assignment for assigned payments, in-force text restated for others. Declared.
4. "A total loss settlement is the actual cash value less the deductible, plus … sales tax … title fee, less the salvage value …; it is paid first to the loss payee up to the payoff amount and the rest to the named insured." — retired by lienholder_settlement and owner_tax_title for loss-payee-listed losses, each naming the other's half; the no-loss-payee settlement restated in both. Declared.
5. Theft waiting period sentences — not touched (no theft in scope of either world); inherited.
6. "Towing from the scene is paid up to tow_limit per loss and storage through storage_paid_through_days_after_notice days after the release notice." — owner_tax_title's owner's storage charge follows it (charges the owner beyond the paid-through days). repair_assignment's appraisal-wait storage allowance is paid inside the repair payment, a quantity the retired clause 3 governs; no conflict with clause 6 on its own terms. Observation O-3 (possible double pay of storage with a tow-and-storage vendor payment; not demonstrable from records).
7. "Payments are issued within payment_issue_days … never exceeds the total loss settlement amount plus towing and storage." — inherited; not binding on either world.

physdam_agg_multi_vehicle_loss: vehicle-by-vehicle handling, own deductible, never combined or waived for multiple vehicles — followed (renewal credit and surcharge do not turn on multiple vehicles).

physdam_recoveries (deductible_refund):
1. "Salvage proceeds and subrogation recoveries reduce the net loss paid." — followed.
2. "A deductible reimbursement is made only after a subrogation recovery has been received on the claim." — inherited.
3. "The named insured's deductible is returned in proportion to … and in full when the recovery is full;" — retired for every refund; replaced_by keeps the cap at the deductible. Declared.
4. "a salvage sale never returns any deductible." — followed (recoveries shared are subrogation only).

physdam_premium_rule (totaled_coverage_return): "a return uses the days from the removal or termination date to the expiration date." — retired for insured-requested removals, in-force text restated with its rate and term-days. The short-rate, paid-claim, notice and minimum-earned deductions sit inside "the return is the coverage return this rule sets out". Declared.

physdam_inspection_rule (totaled_coverage_return): "A coverage with a loss payee is removed no earlier than loss_payee_notice_days calendar days after the loss payee was notified." — retired for totaled coverages; replaced_by says only "the loss payee is taken to have been notified on the day of the total loss declaration". Read literally the retirement removes the waiting period for a totaled coverage and the notification date then has no effect; read purposively the 10 days still run from the declaration. On both task worlds the readings coincide (task 1: declaration 2026-10-02, +10 = 10-12 ≤ 10-18). Observation O-4 (ambiguity with no consequence on either world).

physdam_valuation (not in any base_policy_refs) says each estimate entry already records "the actual cash value by acv_valuation_method" (average of two comparable-vehicle reports). lienholder_settlement calls the estimate entries "valuation reports" and averages / takes the lower of the two latest; this sits inside its declared settlement overwrite. Observation O-5 (the renamed concept may confuse a renderer; not a conflict that changes a reachable number).

No undeclared override found (XF 5d/5f CLEAN); no overwrite retires nothing (5b CLEAN); no rule defers to a clause its own overwrite retires (5e CLEAN).

### factor_ladders
Counts per policy (label as declared; ✓ = structure passes; struck = fails a test below):

| policy | factors | parameter | method | multi-source factors | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| repair_assignment | 5 | cause_rate_ladder, permissive_operator, good_driver_renewal | appraisal_wait, earlier_unrepaired | appraisal_wait (tow payment ∧ wait dates), earlier_unrepaired (insured payments ∧ facility payments), cause_rate_ladder tier 1 only | cause_rate_ladder (auto), good_driver_renewal (auto) |
| deductible_refund | 5 | surcharge_never_refunded, installment_expense | refund_deductible_source, repair_part_measure, expense_part_measure | expense_part_measure (rental ∧ tow), repair_part_measure tier 2 | expense_part_measure (rental) |
| lienholder_settlement | 6 | market_adjustment, total_loss_cause, lp_permissive_operator | valuation_reports, recent_purchase, earlier_damage_carve | recent_purchase (auto change ∧ claim date), earlier_damage_carve | market_adjustment (auto), recent_purchase (auto) |
| owner_tax_title | 6 | state_tax_rate, replacement_share, state_title_fee, title_clearing, release_storage | sales_tax_base | replacement_share (auto change ∧ claim dates), release_storage | state_tax_rate, replacement_share, state_title_fee (auto) |
| totaled_coverage_return | 6 | short_rate_share, paid_claim_retention, loss_payee_notice, minimum_earned | return_start, charge_rate_basis | charge_rate_basis (premium charge ∧ claim) | short_rate_share (auto) |

- All ladders ≥ 3 tiers, pairwise disjoint as stated, domains covered (XF 9 gap/overlap check passed for all 28). `decides` is never `result`; binding sets are disjoint across factors of a policy. Fall-through tier = factor `baseline` in every factor. Every tier stated in the rule with condition and value/method.
- Tiers selecting the same value/method: none.

All-pairs method-shape table (XF 10; aggregates of one field count as one input whatever the filter, constant multipliers ignored):

| policy / factor | T1 | T2 | T3 | pair 1-2 | pair 1-3 | pair 2-3 |
| --- | --- | --- | --- | --- | --- | --- |
| repair / appraisal_wait | (W−free)·rate | MN((W−free)·rate, cap) | 0 | PASS (adds cap) | PASS (T1 > 0 on its domain) | PASS |
| repair / earlier_unrepaired | ΣNI amt + ΣNI ded | ΣNI amt | 0 | PASS (adds deductible input) | PASS | PASS |
| refund / refund_deductible_source | Σ deductible_applied (repair rows) | Σ deductible_applied (total-loss rows) | P(collision_deductible) | **FAIL** (same field, filter only) | PASS (tariff param) | PASS |
| refund / repair_part_measure | latest repair_estimate_amount | acv − salvage | Σ payments + Σ deductibles | PASS | PASS | PASS |
| refund / expense_part_measure | rental paid − reversed + tow | tow | 0 | PASS (adds rental inputs) | PASS | PASS (T2 > 0 on its domain) |
| lienholder / valuation_reports | avg(top, prior) | MN(top, prior) | declared acv | PASS (min pick) | PASS (averaging op) | PASS |
| lienholder / recent_purchase | MN(adj, VB) | MN(adj, 1.10·VB) | adj | **FAIL** (constant multiplier only) | PASS | PASS |
| lienholder / earlier_damage_carve | ΣNI amt + ΣNI ded | ΣNI amt | 0 | PASS | PASS | PASS |
| owner / sales_tax_base | LP amount + LP deductible | value at binding | declared acv | PASS | PASS | PASS |
| return / return_start | DAYS(loss, exp) | DAYS(declaration, exp) | DAYS(today, exp) | PASS (data-selected anchor) | PASS | PASS |
| return / charge_rate_basis | LATEST rate (package-change row) | coverage-added rate + package-change amount | LATEST rate (coverage-added row) | PASS (adds refund input) | **FAIL** (same field vehicle_term_coverage_premium, filter only) | PASS |

Live-tier test against the policy's own scope (XF 9 "every tier re-checked against the policy's own scope"):
- owner_tax_title / sales_tax_base: the rule says the payment "is not figured until a total loss payment to the loss payee stands on the claim"; tier 1's condition is exactly that state, so it holds for every customer who reaches this write and tiers 2 and 3 are never live. Struck.
- totaled_coverage_return / return_start: the rule says a return on a declared total loss "is figured only after a total loss payment to the named insured stands on that claim"; tier 2 ("declaration and no total loss payment to the named insured") is never live. Live tiers: 2. Struck.
- deductible_refund / refund_deductible_source and repair_part_measure: every tier stays live (theft total loss with no estimate; zero-deductible glass; tow-only claim). Pass on this test.

Realism (XF 16, brief: hard criterion):
- earlier_unrepaired (repair) and earlier_damage_carve (lienholder), tier 2: when the earlier claims also carry a repair-facility payment, the carve-out drops the deductible and takes only the cash paid. Whether some earlier claim was repaired at a shop has nothing to do with how much unrepaired damage a cash-out claim left on the car, and taking off the cash without the deductible measures nothing. No physical damage desk would publish this split. RED.
- expense_part_measure (refund): rental benefits count toward the damages only when a tow-and-storage payment also stands; rental-paid-without-tow falls to "nothing". Whether there was a tow does not decide whether rental is part of the loss. RED.
- replacement_share (owner_tax_title): no replacement vehicle → half the tax; replacement bought on time → all of it; replacement bought late → zero. That pays a late buyer less than someone who never buys a replacement, which no carrier's tax reimbursement schedule does. RED.
- paid_claim_retention (coverage return): keeps 25% / 10% of the unearned physical damage premium because an earlier, already-settled claim was paid in cash or at a shop. Unearned premium refunds are pro rata or short rate, and are not cut by past claim payments. RED.
- short_rate_share (coverage return) tier 2: the short-rate penalty is halved just because the term is a renewal (term number ≥ 2), a loyalty-count key that XF 16 names as trivia. RED.
- Observations, not RED: market_adjustment (a state uplift on comparable-vehicle valuations, which can pass as an explicit company schedule) O-6; loss_payee_notice (a fee for the lienholder notice taken from the return premium) O-7; good_driver_renewal (tenure plus a clean record, like real disappearing-deductible programs) O-8; the two "shop storage" daily rates (35 paid to shops vs 15 charged to owners) O-9. State tax rates and title fees match real 2026 schedules (FL 6.0/77.75, TX 6.25/33, GA 7.0 TAVT/18, AZ 5.6/4, OH 5.75/15, VA 4.15/15).

Assembly / order (XF 2, XF 3):
- XF 2: lienholder_settlement's combination sentence names factor quantities ("the valuation figure is chosen first, the market adjustment multiplies it next, the purchase cap is applied …, the earlier-damage carve-out …"). totaled_coverage_return's names the factor-only quantities "any package-change charge refunded in full" and "the paid-claim share". RED members. repair_assignment, deductible_refund and owner_tax_title use generic sentences (owner_tax_title names only baseline quantities: base, rate, share, title fee).
- XF 3: repair_assignment ("deductible adjustments are combined first"), deductible_refund ("they are all settled before the share is taken") and lienholder_settlement ("the combined deductible") each mix a **replacement** of the deductible (cause ladder / payment-source ladder / total-loss cause ladder) with an **addition or subtraction** (permissive surcharge, renewal credit), and none fixes which comes first. Replacing last wipes the surcharge and the credit. RED members, demonstrated in the task files.
- XF 11 (each factor's text names the result it modifies): owner_tax_title "A title-clearing fee is added for the owner's cost of clearing the title" and "An owner's storage charge is taken off for storage after the release notice"; totaled_coverage_return "A paid-claim share is kept …", "A loss payee notice charge is taken off", "A minimum-earned charge is taken off …". None of these names the payment/return it changes. RED members.

### findings
- **C-POL-1 SOURCE-POLICY RED (deductible_refund).** Symptom: two passages of one rule give different outcomes on a non-theft total-loss claim. Passage A (prerequisite sentence): "The deductible refund on a claim that records a repair estimate is figured only after a repair payment stands on the claim for its latest recorded estimate." Passage B: "on a claim without a repair payment that records a total loss declaration, the declared actual cash value less the declared salvage value" (repair part), with "failing that, when total loss payments on the claim carry a deductible, the deductibles those total loss payments carry". Root cause: base physdam_valuation declares a total loss only on "the latest estimate", so every non-theft total loss records an estimate and never gets a repair payment. Consequence: total-loss claim, estimate recorded, subrogation received → by A the refund is never figured (it waits on a write that never comes, and the customer is owed nothing); by B it is deductible × recoveries / (ACV − salvage + expenses). Location: physdam.extended.yaml `physdam_ext_deductible_refund.rule` + `prerequisite[0].policy_source`. Bears on: no task's scored value (task 0 is a repair claim); charter-level.
- **C-XF3 (RED, XF 3).** Non-commuting deductible adjustments with no order: repair_assignment, deductible_refund, lienholder_settlement. Demonstrated: task 0 file (repair and refund), task 1 file (loss-payee payment).
- **C-XF2 (RED, XF 2).** Combination sentences naming factor quantities: lienholder_settlement, totaled_coverage_return. Bears on task 1.
- **C-XF10 (SOURCE-FACTOR RED, mislabelled method).** refund_deductible_source (pair 1-2), recent_purchase (pair 1-2), charge_rate_basis (pair 1-3) fail the shape test: their tiers substitute a number into the same formula. Bears on task 0 (refund) and task 1 (loss-payee payment, coverage return).
- **C-XF9 (SOURCE-FACTOR RED, dead tiers).** sales_tax_base (tier 1 holds for every customer who reaches the write) and return_start (tier 2 never live). After striking these and charge_rate_basis, owner_tax_title and totaled_coverage_return each keep **zero** honest `method` factors. Bears on task 1.
- **C-REAL (SOURCE-FACTOR RED, unreal ladders).** earlier_unrepaired, earlier_damage_carve, expense_part_measure, replacement_share, paid_claim_retention, short_rate_share (tiers named above). Bears on task 0 (earlier_unrepaired, expense_part_measure) and task 1 (the rest).
- **C-XF1 (RED, XF 1).** Factor-only plain bindings outside their factor: repair_payment_count, lp_cause, lp_loss_date, tt_loss_date. Bears on task 0 (refund) and task 1 (loss-payee payment, owner payment).
- **C-XF8 (RED, XF 8).** No same-day tie rule for the LATEST premium charge (coverage return) or the XLATEST added vehicle (owner_tax_title). Neither world has a tie; bears on task 1 as a charter defect only.
- **C-XF11 (RED, XF 11).** Five factor sentences do not name the result they modify (owner_tax_title ×2, totaled_coverage_return ×3). Bears on task 1.
- Observations: O-1 (missing compute_basis on the subtraction intermediates), O-2 (docstring "before the call"), O-3 (appraisal storage vs vendor storage double-pay, cannot be shown from records), O-4 (totaled-coverage notice wait ambiguity, no consequence on either world), O-5 ("valuation reports" = estimate entries), O-6..O-9 (realism notes above).
- Seed realism (XF 13) is per world: see each task file.

VERDICT charter (pre-reveal): charter=C-POL-1,C-XF1,C-XF2,C-XF3,C-XF8,C-XF9,C-XF10,C-XF11,C-REAL

## closing_checklist
Written after both reveals (2026-10-18T10:48Z). Everything above this heading was frozen before them.

- Files: `0.md`, `1.md` and this file match tasks 0..1 one to one. Revision_1 is the first revision, so there are no older ones to keep.
- Comparison sections: every GT write, argument, owner, order, tree edge, skipped-edge value and factor-sensitivity figure matches the frozen derivations. The only exceptions are two exact-tie figures in GT proof fields (251.12, 273.62; half-up gives 251.13, 273.63), and these are not scored.
- Coverage and scopes: the five extended policies are fully covered (task 0 two, task 1 three) and the scopes are disjoint. Each task tool has a distinct, independent uuid8.
- Trees: task 0 has n=1 with 1 value_input edge; task 1 has n=2 with 2 value_input edges. Each tree contains an owner=user write (assign_repair_payment, accept_total_loss_settlement). The difficulty graph is acyclic. Every edge was unmet at the opening and bears weight. SOURCE-CHAIN PASS for both tasks.
- Factors: 4-6 per computation, ≥2 parameter, multi-source and cross-difficulty present per task, and every declared factor bears weight against its baseline. But the structural tests fail: C-XF9, C-XF10, C-REAL, C-XF1, C-XF8, C-XF11, plus per-world XF 13 seed ledgers. NOT closable.
- Policy: C-POL-1 (charter), C-XF2, and C-XF3 (second readings demonstrated on both worlds). NOT closable.
- Additional charter finding from the reveal, **C-RND (observation)**: the DSL's RND is Python `round` (ties to even on exact binary ties), while every package's `premium_rounding` is `nearest_cent_half_up` and the rules say only "nearest cent". No scored value of either task sits on a tie.
- Gate re-run on a final form: not performed. The audit does not run gates, and the artifacts are not in a final form.
- Result: the difficulty does **not** pass the source-layer audit.

VERDICT revision_1: task0=RED task1=RED charter=C-POL-1,C-XF1,C-XF2,C-XF3,C-XF8,C-XF9,C-XF10,C-XF11,C-REAL

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-18, written to disk before the round-2 reveal command ran at 17:29:19Z (`date -u`); no round-2 GT field was read before then.
- Gate: `tail -1 tasks/physical_damage_claims/worklog.md` = `REWORK round 2: gates 7/7 green` (only that line was read from the worklog).
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh physical_damage_claims 2` (2026-10-18T17:22:26). EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r2/0.masked.json 9f270329…f2eb, r2/1.masked.json fcae2632…95eb (re-verified), physdam.extended.yaml **bf40a7d5…168c (changed from round 1)**, task_tools.py 43a3e10b…b54 (unchanged).
- Re-derivation scope: the extended charter changed, so every charter-global section is re-derived in full. task_tools.py is unchanged, so `action_binding_and_uuids` (uuid8s, docstrings, tool bodies, trigger rule) is carried forward from revision_1 by reference on that hash.
- Read: the reworked charter, rework_r2_claims.md (claims only), XF_recipe.md points 1-19, the r2 masked views, billing.yaml (rules for the newly seeded ledgers).
- contamination_disclosure: this auditor read the round-1 GT of both tasks (revision_1 reveal). The round-2 derivations are blind to the round-2 GT fields, but not to the round-1 conventions. The round-1 GT was consistent with the auditor's round-1 blind answer, so no formula was learnt from it. This is disclosed and does not void the round.
- Base copy still `==` blueprint (all ten keys).

### policy_conflict_scan (r2)
Same five policies, tools, owners and edges (E1 refund←repair, E2 owner←loss payee, E3 return←owner). The scopes of task 0 = {repair, refund} and task 1 = {loss payee, owner, return} are still disjoint and complete. Trigger rule unchanged (CLEAN). New cross-category reads: rental_authorizations (refund), auto variant_name and change_effective_date (return). All are reads; nothing is written cross-category.

### rule_compute_equivalence (r2)
- Sweep: every compute_basis quote is verbatim in its rule. **Every binding now has a basis (O-1 closed).** Every baseline sentence is in the rule. No factor-only plain binding and no binding read across factors by name (scripted).
- Claim selection is now the highest claim number (stated "issued in sequence and never repeat"), and LATEST runs on claim_number (fixed width, so lexicographic order is correct). Premium-charge tie: "a package change and a restoration sharing the latest effective date count as the package change" = `DAYS(rest_date, pc_date) >= 0`. Replacement tie: "two vehicles acquired on the same day give the same share" (the read is a date, so a tie is harmless). Absent-record tiers are stated.
- **Rule words ≠ compute (XF 11/12):** totaled_coverage_return rule [11] "a vehicle was added to the owner term on or after that claim's date of loss" and [12] "a vehicle was added to the owner term within …". The compute reads `XLATEST('auto','auto_policy_changes','change_effective_date', …, event_type='auto_vehicle_added')` with no owner-term key (anchor_vehicle_added_on, sr_vehicle_added_on), i.e. a vehicle added to **any** of the customer's owner terms. A vehicle added to a second owner term (a second garaging address, per auto_agg_multi_holding) moves the return start and the share kept although no vehicle was added to this term. The lienholder read is keyed by VIN, as its rule says.
- **XF 8 decoy:** deductible_refund rental part tier 2 pairs `XLATEST(rental_authorized).authorized_start_date` with `XLATEST(rental_authorization_closed).entry_date`, keyed only by claim number. With a second authorization on the claim (one rental at a time, sequentially), an earlier authorization's closing date pairs with a later one's start (a negative or wrong day count). There is no tie rule and no decoy exclusion.
- Rounding: "rounded to the nearest cent" everywhere, RND outermost inside MX. Scored values on the r2 worlds sit on no exact half-cent (checked in the task files).

### prerequisite_graph / prerequisite_sentences (r2)
- E1 is now "The deductible refund on a claim that records a repair estimate and no total loss declaration is figured only after a repair payment stands on the claim for its latest recorded estimate." Its condition carries the same two scope words (XF 19 strength match). **C-POL-1 closed:** total-loss claims are no longer held.
- E2 is unchanged; gate moved to `title_clearing_fee` (an existing binding, and the one the loss-payee write actually moves on the r2 world). E3 is unchanged. All are state form, single producing write, acyclic, quotable, condition = sentence. No rule states an ungrounded cross-problem order.
- **XF 19, unsatisfiable waits on reachable worlds (RED members, all three edges).** Every producing tool's contract takes "amount … as a positive number", and every producing rule floors its figure at zero, so a figured zero can never "stand":
  - E1: estimate 600, collision cause with a non-household permissive driver ($500 + $500 deductible), subrogation received. The assigned repair payment is 0, no repair payment can stand, and the refund on a claim that "records a repair estimate and no total loss declaration" is never figured. Base physdam_recoveries makes a refund available once a recovery is received.
  - E2: $1,000 package, theft cause, permissive driver (deductible 1,000 + 250 + 250), declared ACV 2,000 with no reports. The loss-payee vehicle value is MX(0, 2000 − 1500) = 500, but with a 25% condition carve-out (500) it is 0. No loss-payee payment can stand, so the owner payment is never figured.
  - E3: lessor-financed TX total loss with yard storage and 10 late days. Owner payment = 0 (tax base 0) + 33 + 40 − 350 → 0. No named-insured payment can stand, so the coverage return is never figured and the removal never comes.

### override_declarations (r2)
Base sentences re-checked against the same refs (see revision_1 table). Declared overwrites unchanged except physdam_inspection_rule's replaced_by, which now keeps the wait explicitly ("removed no earlier than loss_payee_notice_days calendar days after it") — **O-4 closed**. New content all sits inside declared scopes: refund rental and tow parts, return deletion fee and the inspection-pending return from the effective date (an insured-request removal, inside the premium-rule overwrite), owner tax-base tiers, repair storage rate. No undeclared departure, no idle overwrite, sibling exclusions intact (XF 5 CLEAN).

### factor_ladders (r2)

| policy | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| repair (5) | cause_rate_ladder, permissive_operator, good_driver_renewal, storage_market_rate | appraisal_wait | appraisal_wait | cause_rate_ladder, good_driver_renewal, storage_market_rate (auto) |
| refund (5) | refund_deductible_source, surcharge_never_refunded, tow_reasonable_charge | repair_part_measure, rental_part_measure | rental_part_measure tier 2 (no payment ∧ authorization) | rental_part_measure (rental) |
| loss payee (6) | market_adjustment, recent_purchase, total_loss_cause, lp_permissive_operator | valuation_reports, earlier_damage_carve | recent_purchase, earlier_damage_carve | market_adjustment, recent_purchase (auto) |
| owner (6) | state_tax_rate, replacement_share, state_title_fee, title_clearing | sales_tax_base, release_storage | replacement_share, sales_tax_base | state_tax_rate, replacement_share, state_title_fee (auto) |
| return (6) | charge_rate_basis, short_rate_share, minimum_earned, deletion_endorsement, loss_payee_charge_ladder | return_start | return_start, short_rate_share | return_start, short_rate_share, deletion_endorsement (auto) |

Method-shape all-pairs (XF 10):

| factor | T1 / T2 / T3 (/T4) | pairs |
| --- | --- | --- |
| appraisal_wait | W−free / MN(W−free, cap) / 0 | 1-2 PASS (cap), 1-3, 2-3 PASS |
| repair_part_measure | latest estimate / acv−salvage / Σpay+Σded | all PASS |
| rental_part_measure | paid−reversed / rate·DAYS(start, close∨today) / 0 | all PASS (distinct inputs, date op) |
| valuation_reports | avg / MN / declared | all PASS |
| earlier_damage_carve | Σcash+Σded / 0.25·declared ACV / 0 | all PASS (different input = min pick) |
| sales_tax_base | 0 / declared ACV / recognised value | all PASS (T1 nothing, T3 > 0 on its domain) |
| release_storage | late·yard / MN(late·shop, cap) / 0 | 1-2 PASS (cap), others PASS |
| return_start | DAYS(replacement add, exp) / DAYS(loss, exp) / DAYS(effective, exp) / DAYS(today, exp) | all 6 pairs PASS (data-selected anchors) |

The three relabelled factors (refund_deductible_source, recent_purchase, charge_rate_basis) are now `parameter` and honestly select values. **C-XF10 closed.**

Live tiers (XF 9): every tier of every ladder is reachable inside its policy's scope. sales_tax_base no longer keys on the prerequisite state; return_start has no declared-but-unpaid tier. **C-XF9 closed.**

Independence / gating (XF 1, XF 2 "no factor is gated through another factor"; "the baseline defines no quantity only factors use"):
- repair_assignment: the baseline says "The appraisal-wait storage … is its storage days times the standard daily storage rate, and at the standard no storage days are allowed". Storage is therefore identically 0 at the baseline, and storage_market_rate changes the payment only when appraisal_wait is off its fall-through (storage = days × rate). Shown in 0.md. **RED member.**
- owner_tax_title: the baseline sales tax is taken "for the share of that tax the owner is due, and at the standard that share is none", so it is identically 0 at the baseline. state_tax_rate and sales_tax_base change the payment only when replacement_share is off its fall-through. Shown in 1.md. **RED members (two factors).**

Assembly (XF 2), naming factor quantities in the combination sentence:
- repair [10] "the deductible for the loss's cause replaces it first, the permissive-operator surcharge is added next, and the good-driver renewal credit is taken off last"
- refund [8] "the deductible taken from the claim's own payments replaces it first and the never-refunded surcharge is taken off next …; the damages are the repair part of the damages plus the rental part plus the tow part"
- loss payee [8] "within the deductible, the cause's deductible replaces it first and the surcharge is added after"

**RED members (3).** The rework fixed the order (XF 3, **C-XF3 closed**) by naming the factors, where the recipe's generic form would do ("replacements first, then additions …", as the loss-payee rule's first clause and the owner/return rules already do). This is a regression in repair and refund, and the loss-payee rule is still a member. owner [7] and return [9] are generic and CLEAN.

XF 11 (factor text names its result): all factor sentences now name the payment, refund or return. **C-XF11 closed** apart from the rule-word/compute mismatch above (return [11], [12]).

Realism (XF 16/17):
- Closed: shop-repaired carve-out split (removed), rental-only-with-tow (rental counted on its own), late-replacement below none (now full / half / none, monotone), paid-claim retention (removed), renewal-halved short rate (now substitution), installment expense (removed). The new earlier_damage_carve (unrepaired prior cash-out damage, capped at 25% of ACV) is a real condition deduction.
- **RED (XF 17):** market_adjustment, a state multiplier (TX/AZ 1.015, FL 1.02, GA 1.01) on ACV taken from comparable-vehicle valuation reports, which are already local-market figures. No carrier publishes such an uplift for that very charge (previously O-6; now RED under point 17).
- **RED (XF 17):** loss_payee_charge_ladder, a $15 "total-loss handling charge for clearing the loss payee's interest" or a $10 notice charge taken out of the insured's unearned-premium return. That is a company add-on to a premium refund with no published counterpart (previously O-7; now RED under point 17).
- Observations: deletion_endorsement (a policy-change fee by liability package; carriers do publish endorsement fees, though rarely package-tiered) O-12; storage_market_rate (a reasonable storage schedule by state, defensible); return_start tier 1 (premium earned until the replacement is added, defensible through newly-acquired-vehicle continuity) O-14; tow part capped at the tow-from-scene limit although the payment includes storage O-15; the two storage schedules (repair: GA 35 / TX-AZ 30 / standard 25 vs owner: yard 35 / shop 25) O-9.

Status stamps (XF 18): coverage-return tier 3 keys honestly on `physdam_coverages.status = inspection_pending`. driver_household_status is the recorded claim-report standing the rules name. The cached `rental_coverages.benefits_paid_total` (per coverage) states the rental part's tier-1 value directly whenever the coverage has one claim; see 0.md. **RED member (rental_part_measure).**

Seed-side blueprint note (observation O-13): physdam_premium_rule says coverage premium is "billed on the owner term's billing plan", but billing_transactions carries only source_auto_txn_id / source_nonowner_txn_id and the billing charter has no physdam or rental premium route. The seeds (rightly) bill no physdam or rental premium. This is a scenario-constitution gap, not a task defect.

### findings (r2, charter)
- Closed: C-POL-1, C-XF1 (factor-only bindings), C-XF3, C-XF8 (round-1 members), C-XF9, C-XF10, C-XF11 (round-1 members), C-REAL (all six round-1 members), O-1, O-4.
- **R2-XF2 (RED)**: combination sentences name factor quantities in repair, refund and loss payee. Regression in repair and refund.
- **R2-GATE (RED, XF 1/2)**: storage_market_rate gated through appraisal_wait; state_tax_rate and sales_tax_base gated through replacement_share (baseline quantity identically zero).
- **R2-XF19 (RED)**: E1, E2, E3 can never be satisfied on reachable zero-amount worlds.
- **R2-XF11 (RED)**: return rule says "added to the owner term" but the compute reads every owner term.
- **R2-XF8 (RED)**: rental authorization start/close pairing has no decoy exclusion or tie rule.
- **R2-XF17 (RED)**: market_adjustment, loss_payee_charge_ladder.
- **R2-XF18 (RED)**: benefits_paid_total stamp states rental_part_measure's value.
- Observations: O-2, O-3, O-5, O-8, O-9, O-12..O-15, C-RND (DSL ties-to-even; no tie on r2 worlds).

## closing_checklist (revision_2)
Written after the round-2 reveal (17:29Z).
- Files: revision_2 has been appended to `_difficulty.md`, `0.md` and `1.md`, with revision_1 untouched. Every GT write, argument, edge, skip value and sensitivity figure in both tasks equals the frozen r2 derivations.
- Coverage: scopes disjoint and complete; uuid8s unchanged and independent.
- Trees: task 0 n=1 / 1 value_input; task 1 n=2 / 2 value_input. Each has a user write, everything is acyclic, every edge is unmet at the opening and bears weight. SOURCE-CHAIN PASS for both.
- Factors: 5/5/6/6/6 factors, with ≥2 parameter and ≥1 honest method per computation, and multi-source and cross-difficulty factors present in each task. Every factor bears weight against its baseline, and every fall-back differs from gold. Still failing: R2-GATE (task 0, task 1), R2-XF18 (task 0), R2-XF17 (task 1). NOT closable.
- Policy: no second reading on either world, but the charter keeps RED members R2-XF2 (incl. a regression in repair/refund), R2-XF19, R2-XF11 and R2-XF8.
- Round-1 closure: C-POL-1, C-XF1, C-XF3, C-XF8, C-XF9, C-XF10, C-XF11, C-REAL and the XF 13 seed ledgers are all closed. C-XF2 is only partly closed (the return rule is fixed, the loss-payee rule is still a member, and repair and refund have regressed).
- Gate snapshot r2: 7/7 OK (cited above). The difficulty does **not** pass the source-layer audit.

- Erratum: the revision_1 freeze clock times in 0.md/1.md were estimates, stated after the 10:48:18Z reveal; the files were in fact on disk before the reveal command ran. The revision_1 text is left unedited.

VERDICT revision_2: task0=RED task1=RED charter=R2-XF2,R2-GATE,R2-XF19,R2-XF11,R2-XF8,R2-XF17,R2-XF18

## revision_3

## charter_global_frozen (revision_3)
- Written to disk before the round-3 reveal command (time recorded by `date -u` at the reveal, below).
- Gate: worklog tail = `REWORK round 3: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh physical_damage_claims 3` (2026-10-19T22:32:34): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK, rc=0.
- Hashes: r3/0.masked.json ca9ff86d…7647, r3/1.masked.json 014a3224…12ea (re-verified), physdam.extended.yaml **1b40d6f9…6f67 (changed)**, task_tools.py 43a3e10b…b54 (unchanged, so action_binding_and_uuids is carried by reference).
- Read: the reworked charter, rework_r3_claims.md (claims only), XF_recipe.md 1-23, r3 views. Base copy still `==` blueprint.
- contamination_disclosure: round-1 and round-2 GT were read in earlier revisions. Round-3 GT is unread at this point.
- Point 23 is applied as written: the rating-plan dimensions it lists, applied to premium-derived amounts, count as realistic; RED covers fees/credits on incidental counts or on dimensions no filing uses for that very charge, add-ons stacked on statutory amounts, one dimension charged twice, and retaining premium for days with no exposure.

### sweeps (r3)
- Scripted: compute_basis verbatim; every binding has a basis; baseline sentences in rules; every factor's fall-through equals its `baseline`; no factor id in a tool name; no factor-only plain binding; no cross-factor binding read. CLEAN.

### round-2 items
- **R2-XF2 closed.** The repair [11], refund [8] and loss-payee [8] combination sentences are now generic by kind ("replacements first, then caps, then additions, then the amounts taken off, then the floor"). Owner [8] and return [10] are generic.
- **R2-GATE closed.**
  - Repair baseline storage days = MN(MX(0, wait − free), allowance), which is non-zero once the wait exceeds the free days, so storage_market_rate acts alone.
  - Owner baseline takes the whole tax and a storage charge of MN(late, allowance) × standard rate, so state_tax_rate, sales_tax_base and owner_storage_schedule each act alone.
  - Return minimum-earned baseline = 10% × rate × 1, so both minimum-earned factors act alone.
- **R2-XF19 closed as a deadlock class.**
  - E1 now waits only where "the latest recorded repair estimate is more than the repair payments … for its earlier estimates plus the package's larger deductible and the permissive-collision surcharge". That is a record test, and with it the assigned payment is always > 0.
  - E3's producer is floored at the title fee (> 0).
  - E2's carve-out, however, is not a record test (see R3-XF15).
- **R2-XF11 closed.** The vehicle-added reads are keyed `auto_policy_id=F('auto_policy_id')`.
- **R2-XF8 closed.** The rental read is the latest authorisation by entry date (tie rule stated), and a closing counts only if dated on or after that authorisation's entry; the compute matches.
- **R2-XF17 closed.** market_adjustment and loss_payee_charge_ladder are removed.
- **R2-XF18 closed** for the stamp (benefits_paid_total is now 0 with no benefit rows). The way it was closed creates R3-XF13a.

### new / remaining (r3)
- **R3-XF15 (RED, XF 15 + check 6).** The E2 sentence is "The owner's tax-and-title payment on a claim for which the loss-payee settlement rule leaves a vehicle value to pay the loss payee is not figured until …". Its scope is "if policy X would compute a positive amount", which XF 15 names as forbidden; it is not a record-visible state, and the condition repeats it. Location: physdam_ext_owner_tax_title.rule [3] and prerequisite[0].
- **R3-LADDER (SOURCE-FACTOR RED, XF 9/10).**
  - Root cause: appraisal_wait tier 2 ("the appraisal wait is no longer than the free appraisal days → no storage days") is the fall-through/baseline formula MN(MX(0, W − free), allowance) restricted to its own domain, where that formula is 0 everywhere. One tier has been written as two, and substituting the baseline on tier 2 never changes a value.
  - Consequence: the ladder really has two outcomes (towed: uncapped; otherwise: the baseline). The factor fails the ≥3-real-tier test, and repair_assignment is left with no honest `method` factor.
- **R3-XF23a (RED, retaining premium for days with no exposure).** return_start tier 1 starts the return "from the change effective date of the latest such vehicle added (the replacement takes over from that day)". It keeps the totaled vehicle's premium from its date of loss to the replacement's add date, days on which the destroyed vehicle had no exposure. This was O-14 in round 2 and is now RED under point 23 as written. Shown in 1.md.
- **R3-XF23b (RED, one dimension charged twice / dimension no filing uses for that charge).**
  - The return already keeps the owner package's short-rate percent, which varies by liability package (auto: 10/10/10/10/0/0). deletion_endorsement takes a second liability-package-keyed retention from the same return (25/25/15/15/0/0).
  - Endorsement fees in filings are flat per transaction, not tiered by liability limits.
  - Example (non-total-loss removal on Minimum Limits): 10% short rate plus $25, both because of the package. On task 1's world the short rate is 0 (total loss), but the fee still bites (25.00).
- Realism passes under point 23: minimum-earned by payment plan ("company's filed minimum-earned percents by payment plan", a listed dimension on a premium-derived amount); minimum-earned share by days in force; renewal deductible credit by term number and violation points (filed disappearing-deductible analogue); permissive deductible surcharge; theft add-on; storage schedules by state (O-9 closed: the repair and owner storage schedules are now one schedule); tow part at the package tow limit (O-15 stays an observation).
- One-dimension-twice check across the other charges: garaging state drives different components (statutory tax rate, statutory title fee, storage schedule; FL glass vs storage). These are not the same charge levied twice. CLEAN apart from R3-XF23b.
- XF 21 look-backs: the factors read term_number/violation_points of the coverage's own term and the payment plan of that term; no priced window reaches before the seeded records.
- Seed realism per world: R3-XF13a (task 0 rental) and R3-XF13b (task 1 auto renewal), in the task files.

## closing_checklist (revision_3)
- Revealed at 22:36:54Z, after both frozen r3 sections were written (22:36:50Z). Every GT write, argument, edge, skip value and sensitivity equals the frozen derivations in both tasks.
- Coverage, scopes, uuid8s, acyclic graph: unchanged and PASS. Trees: task 0 n=1 / 1 value_input, task 1 n=2 / 2 value_input, a user write in each, every edge unmet at the opening and bearing weight. SOURCE-CHAIN PASS ×2.
- Round-2 items: R2-XF2, R2-GATE, R2-XF11, R2-XF8, R2-XF17 and R2-XF18 are closed. R2-XF19 is closed as a deadlock class, but E2 is closed by a computed scope (R3-XF15).
- Remaining REDs:
  - charter: R3-XF15, R3-LADDER, R3-XF23a, R3-XF23b
  - per-world seeds: R3-XF13a (task 0), R3-XF13b (task 1)
- Observations: O-2, O-3, O-5, O-8, O-12 (absorbed into R3-XF23b), O-13, O-15, C-RND (no ties on r3 worlds). O-9 closed. O-14 became R3-XF23a under point 23.
- Gates r3: 7/7 OK. The difficulty does **not** pass the source-layer audit.

VERDICT revision_3: task0=RED task1=RED charter=R3-XF15,R3-LADDER,R3-XF23a,R3-XF23b

## revision_4

## charter_global_frozen (revision_4)
- Written before the round-4 reveal command.
- Gate: worklog tail = `REWORK round 4: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh physical_damage_claims 4` (2026-10-20T04:06:48): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK, rc=0.
- Hashes: r4/0.masked.json eff13912…5989, r4/1.masked.json 31105db9…a962 (re-verified), physdam.extended.yaml **112f2fe9…04ef (changed)**, task_tools.py 43a3e10b…b54 (unchanged; action_binding_and_uuids carried by reference).
- Read: the charter, rework_r4_claims.md (claims only), XF_recipe 1-24, r4 views. contamination_disclosure: round-1..3 GT read earlier, round-4 GT unread.
- Scope: changed parts re-derived (repair appraisal_wait; refund rental part; owner E2; return start, deletion fee → tenure share; both seeds). Unchanged parts were checked for regression by a full mechanical sweep: compute_basis verbatim, every binding based, baseline sentences in rules, fall-through = baseline, no cross-factor or factor-only bindings, no factor id in a tool name. All CLEAN.

### round-3 items
- **R3-XF15 closed.**
  - E2 is now "The owner's tax-and-title payment on a claim whose total loss declaration records a payoff for the loss payee, and on which every actual cash value recorded on the claim's estimates and total loss declaration and the coverage's value at binding are each more than a quarter of the declared actual cash value plus the package's larger deductible, the theft deductible add-on and the permissive-collision surcharge, is not figured until a total loss payment to the loss payee stands on the claim." Every term is a record field or a package/charter figure, so it is a record test (XF 15 met). The condition states the same test (XF 19 strength met).
  - XF 20 proof: inside the test, the capped starting value (an average or minimum of the recorded ACVs, the declared ACV, or the cap at value at binding ×1 / ×1.1) exceeds 0.25·ACV + maximum deductible. The carve-out is ≤ 0.25·ACV, the deductible is ≤ larger deductible + theft add-on + 500, and the credit is ≥ 0. So the loss-payee figure is always > 0 and the wait is always satisfiable.
- **R3-LADDER closed.** appraisal_wait tiers are now glass → 0; non-glass towed → MX(0, W − free) with no allowance; otherwise the baseline MN(MX(0, W − free), allowance).
  - Tier 1 differs from the baseline on its domain whenever W > free (glass with a long wait).
  - Shape pairs: 1-2 PASS (0 vs an input that is > 0 on its domain), 1-3 PASS, 2-3 PASS (cap). A glass replacement not holding the car for appraisal is a real distinction.
- **R3-XF23a closed.** return_start is now: paid total loss → from the date of loss ("since the totaled vehicle had no exposure after it"); inspection pending → from the effective date; otherwise → today. No premium is kept for days without exposure. Shape PASS (data-selected anchors), all tiers live.
- **R3-XF23b closed.** deletion_endorsement, its params and its sentence are removed. Liability package now enters the return only through the baseline short-rate percent.
- Charter state of the other round-2/3 closures: unchanged and still closed (sweep).

### changed parts, full check (r4)
- **refund rental_part_measure.**
  - Tier 1 is now "benefits paid less those reversed plus the rental days not yet invoiced at the authorised daily rate, from the day after the last day of the latest paid invoice period to the end of the rental, the end not counted". The compute is `rate × MX(0, DAYS(paid_through, end) − 1)`, which matches, end not counted.
  - Decoy check on `rental_paid_through` (latest paid period, reversed rows not excluded). For each of the three reversal reasons, treating the period as invoiced is right: a duplicate is still paid by the original; an agency credit was invoiced; days outside the eligible period must not be re-added. CLEAN.
  - Shape: tier 1 adds the unbilled-days input vs tier 2; tier 3 nothing. PASS.
- **return minimum_earned_tenure (new, parameter).** The renewal share of the minimum-earned charge is 0 / ½ / 1 by owner term number (≥3 / 2 / new business), "as the company's filed minimum-earned rule for renewal business".
  - It scales an existing premium-derived charge (rate × plan percent × in-force share × renewal share). It is not an add-on and does not double a dimension: the in-force days, the payment plan and the term number are three different dimensions on one charge.
  - Under point 23 as written: new-business vs renewal (persistency) is a dimension real filings use for minimum-earned premium, it is applied to a premium-derived amount, and it is stated as the company's filed rule. **PASS.**
  - Observation O-16: XF 16's "loyalty counts" language is in tension with tiering 2 vs ≥3 renewals; the coordinator's point-23 bar governs and is applied exactly.
  - Gating: all three multipliers have non-zero baselines (10%, 1, 1), so each moves the charge alone (demonstrated in 1.md).
- **Combination sentence** (return [10]) still generic by kind (it enumerates the quantities adjustments change, the form accepted in every policy); the order is fixed. CLEAN.
- XF 21: every priced read (term number, points, payment plan, VIN acquisition) lands on seeded rows, including task 1's term 1 now. XF 24: no computation is built on a flat service charge with incidental keys (the title-clearing and title fees are state or payee-type schedules). CLEAN.
- Realism sweep of the whole factor set under points 17/22/23/24: no fee or credit on incidental counts, no add-on stacked on a statutory figure, no dimension charged twice in one charge, and no premium kept for days without exposure.

### findings (r4, charter)
- Closed: R3-XF15, R3-LADDER, R3-XF23a, R3-XF23b. No new charter RED.
- Observations: O-2 (docstring "before the call"), O-3 (appraisal storage vs vendor storage double pay, not demonstrable), O-5 ("valuation reports" are the estimate entries), O-8, O-13 (blueprint: no billing route for physdam/rental premium), O-15 (tow part at the tow limit), O-16 (tenure tiers vs XF 16 wording), C-RND (ties-to-even; no tie on r4 worlds).

## closing_checklist (revision_4)
- Revealed at 04:10:44Z, after both frozen r4 sections (04:10:18Z). Every GT write, argument, edge, skip value and the 29 sensitivity/fall-back figures equal the frozen derivations.
- One-to-one files: `_difficulty.md`, `0.md`, `1.md`, revisions 1-4 kept.
- Coverage of the five extended policies complete; scopes disjoint; uuid8s independent (tools unchanged since revision_1).
- Trees: task 0 n=1 / 1 value_input; task 1 n=2 / 2 value_input. Each has a user write, every edge is unmet at the opening and bears weight, and the graph is acyclic. Every wait is satisfiable on every reachable world: E1 and E2 by record tests, E3 by the title-fee floor.
- Factors: 5/5/6/6/6 per computation, with ≥2 parameter and ≥1 honest method each. Multi-source and cross-difficulty (auto, rental, billing) are present in each task. Every factor bears weight against an honest baseline, and every all-baseline fall-back differs from gold. No gating, no stamp, no unreal ladder under points 16/17/22/23/24 as applied.
- Policy: overrides declared, combination sentences generic with the order fixed, compute = rule (sweep), no second reading on either world.
- Gate snapshot r4 (above) 7/7 OK on this final form.
- The difficulty passes the source-layer audit.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Written before the round-5 reveal command.
- Gate: worklog tail = `REWORK round 5: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh physical_damage_claims 5` (2026-10-20T14:43:38): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK, rc=0.
- Hashes: r5/0.masked.json eff13912…5989 and r5/1.masked.json 31105db9…a962, **identical to r4** (the seeds, personas and frozen_time are unchanged, so the per-world seed checks of revision_4 carry forward on these hashes). physdam.extended.yaml **f165003a…13db (changed)**. task_tools.py 43a3e10b…b54 (unchanged).
- This round's REDs to verify are the renderer's source-scan items F1-F4 (`audits/render_source/physical_damage_claims/render_r1.md`). Also read: rework_r5_claims.md (claims only), XF_recipe 1-26.
- contamination_disclosure: GT of rounds 1-4 read earlier; round-5 GT unread.

### F1 — recent_purchase scope (rule vs compute of a cross read): closed
- Rule [10] now: "the vehicle's original acquisition date, recorded on the vehicle-added change for the coverage's VIN on any of the named insured's owner terms (a renewal carries the vehicle over without a new change, so the change that first scheduled it is read, and of several such changes the one with the latest change effective date)". This equals `XLATEST(…, vehicle_vin=F('vehicle_vin'))` (customer-scoped, VIN-filtered, latest by change_effective_date). The renderer's renewal-carried-vehicle world now gets the cap under both rule and compute.
- Class sweep of cross reads: garaging state, term number, points, term days, the CPARAMs, the billing plan (`auto_policy_id=F('auto_policy_id')`) and the vehicle-added read of the share kept are keyed on the coverage's own owner term in both rule and compute. The rental reads are keyed on the claim number in both. CLEAN.
- Observation O-17: "original … first scheduled" and "of several such changes the one with the latest change effective date" pick different rows only if two vehicle-added changes for one VIN carry different acquisition dates (a sale and re-purchase of the same car). Every realistic re-add carries the same acquisition date, so this has no consequence on any plausible world.

### F2 — negative day counts: closed
- Rule [12] adds "and no days when the rental ends on or before its start date", and the compute floors it: `rental_auth_rate * MX(0, DAYS(rental_auth_start, rental_end))`.
- Class sweep of every DAYS read:
  - repair appraisal wait: negative values go to MX(0, …) in all tiers.
  - held days: negative means "held fewer than", and rule and compute agree.
  - owner late days: MX(0, …).
  - unbilled rental days: MX(0, …).
  - return days: start before expiration on every live tier; overall floor at zero.
  - in-force days: negative means "fewer than the first minimum days" in both rule and compute.
  - substitution days-ago: −1 when absent, tested ≥ 0.
  - package-change vs restoration date order: tie rule stated.
- CLEAN.

### F3 — latest-row reads and window boundaries: closed
- Rule [13] now: "the latest vehicle added to the owner term, latest by change effective date, took effect no earlier than the owner package's replacement-vehicle reporting days before today and no later than today, both of those days counted". This equals `0 <= DAYS(added_on, NOW) <= window` on the latest add. The renderer's future-dated-add world now gives the package percent under both rule and compute.
- Class sweep of latest-row reads: claim (highest claim number), estimate (highest sequence), authorisation (latest entry date, no two share a date), latest paid invoice period (a date value; duplicate rows share it harmlessly), latest premium charge (package-change-wins tie stated), latest vehicle-added change (a date value), declaration and confirmation (one per claim by base). CLEAN.

### F4 — minimum-earned assembly: closed
- Baseline/rule [8] now defines the charge as "the minimum-earned percent of the full-term rate, times the time-in-force share …, times the tenure share …; at the standard the percent is the standard minimum-earned percent and both shares are one". Factors [14], [16] replace a share and [15] replaces the percent. The product is stated once in the computation document's own sentence, which removes the one-quarter vs one-half second reading.
- The combination sentence [10] names only baseline quantities (rate, days, share kept, percent, time-in-force share, tenure share). Compute = `rate × pct/100 × share × renewal_share`. XF 1/2/3 met.
- Class sweep: every other policy's combination sentence names only baseline quantities or kinds of adjustment. CLEAN.

### regression and new points (r5)
- Mechanical sweep of all five policies (verbatim compute_basis, every binding based, baseline sentences in rules, prerequisite sources in rules, no cross-factor or factor-only binding, no factor id in a tool name): CLEAN. Factor counts 5/5/6/6/6 unchanged, labels unchanged.
- Edges E1-E3, record tests, satisfiability (XF 19/20) and the realism outcome of revision_4: unchanged by the edits (only rule [10] of the loss-payee rule, [12] of the refund rule, and [8], [10], [13], [14], [16] of the return rule were reworded).
- XF 25: no service-charge computation in this difficulty. CLEAN.
- XF 26 (factor already embedded in a recorded amount):
  - The only recorded amounts near a factor are premium-charge rates (which the charge-rate factor selects among, the transaction's own method), net benefits 630 (≠ the rule's rental part 750) and net loss paid.
  - No recorded deductible, tax, storage, repair or return figure exists before its write.
  - CLEAN.

### findings (r5, charter)
- F1-F4 closed. No new charter RED. Observations: O-2, O-3, O-5, O-8, O-13, O-15, O-16, O-17, C-RND.

## closing_checklist (revision_5)
- Revealed at 14:45:07Z, after both frozen r5 sections (14:45:02Z). Every GT figure equals the frozen derivations in both tasks.
- F1-F4 closed across their classes. XF 1-26 checked on every changed policy; the full regression sweep is CLEAN.
- Scopes disjoint and complete. Trees hold with weight-bearing, satisfiable edges and a user write in each. Factors 5/5/6/6/6, all weight-bearing against honest baselines, with no gating, stamp, embedded-amount or unreal ladder.
- Gate snapshot r5: 7/7 OK on this final form. The difficulty passes the source-layer audit.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Written before the round-6 reveal command.
- Gate: worklog tail = `REWORK round 6: gates 7/7 green`.
- Entry evidence: `/tmp/erl0071_coord/snapshot.sh physical_damage_claims 6` (2026-10-21T19:59:44): all 7 gates OK, rc=0.
- **Frozen files byte-identical:** physdam.extended.yaml f165003a…13db and task_tools.py 43a3e10b…b54, both equal to revision_5. The charter-global sections of revision_5 therefore carry forward by reference.
- Views: r6/0.masked.json eff13912…5989 (unchanged since r4) and r6/1.masked.json **91b8b32d…622a (changed)**.
- Read: rework_r6_claims.md (claims only), docs/auto `vehicle_additions_and_removals_1ce54ba7` and `premium_written_and_additional_9f6643b4`.
- contamination_disclosure: GT of rounds 1-5 read earlier; round-6 GT unread.

### S3 — task 1 bind-time "vehicle added" row (seed-only): closed
- r5 → r6 diff of task 1 initial_state: exactly one row removed, auto_policy_changes 7c5e1a93 (auto_vehicle_added, term 1, 2025-11-15, Camry). Nothing else changed; persona and frozen_time are identical.
- Against docs/auto:
  - "Premium written equals the term's full-term premium. It is booked once when a new-business term is bound". That is term 1's 1248 auto_premium_written row, which carries the bind-time Camry.
  - "Additional vehicles … Additional and return premium are the vehicle's full-term premium share, prorated from the change effective date". A vehicle-added change is a mid-term schedule change with additional premium, which the removed row never had.
- The Camry is now carried only by the new-business premium (1248), vehicle_count 1 and its replacement-date removal change b4f08d2e, whose recorded full-term share 1248 still prices the 268.91 return (1248 × 39/181). This matches task 0's convention (no rows for bind-time vehicles).
- Regression: no physdam rule or compute reads that row. The recent-purchase cap reads the Accord's VIN (9a0b2d6f); the substitution share reads term 2's adds; nothing else reads vehicle changes. No look-back of any priced row reaches it (XF 21). CLEAN.

## closing_checklist (revision_6)
- Revealed at 20:00:21Z, after the frozen r6 sections (20:00:16Z). Gold is unchanged in both tasks and equals the derivations.
- Seed-only round confirmed: the charter and tools are byte-identical. S3 is closed against docs/auto with one row removed and nothing else touched. No priced read is affected, and the revision_5 charter conclusions carry forward.
- Gate snapshot r6: 7/7 OK. The difficulty passes the source-layer audit.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
