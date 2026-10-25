# Policy-task audit — hardship_assistance_plans / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-16T04:58Z, before any task's GT was revealed. Auditor: independent policy auditor (erl-task-policy-audit), not the instantiator.
- Inputs and hashes: `tasks/hardship_assistance_plans/hardship.extended.yaml` sha256=0dfde14018d00aa779eaa586de74de85aeea1818a357d77375c47e5f05455d02; `tasks/hardship_assistance_plans/task_tools.py` sha256=8115589d05f1ed1538fb950772babc52cd3b776e31d7095ae0b2b4858e52c8b9 (both re-hashed by me and equal to the brief). Also read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (function list), `blueprint/products/hardship.yaml`, `blueprint/products/loan.yaml` (holding, payment, return and charge-off rules), the DSL primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/_within/CFIELD/XLATEST), and `audits/render_source/XF_recipe.md`.
- Masked and not read: `tasks/hardship_assistance_plans/tasks/*.json`, `worklog.md`, `plan.md`, every `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract` and `prerequisite_closure`. No search touched `tasks/*/tasks/`.
- Entry conditions (Step 0): the gate snapshot came with the brief (`.audit_views/policy/hardship_assistance_plans/r1/gate_snapshot.txt`): EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK. TRACEABILITY is NOT OK before publication; every miss is an unlock_*_discoverable_tool:tool_name, which is expected because the KB is not rendered yet. The masked views and their hashes match the brief. Input is complete.
- The base section of the extended file (lines 1–1236) is byte-identical to `blueprint/products/hardship.yaml` (`diff` gives no output apart from the two header lines at 1237–1238).

Policy ids used below: P1 `hardship_ext_rpp_offer_payment`, P2 `hardship_ext_settlement_installment_term`, P3 `hardship_ext_settlement_offer_amount`, P4 `hardship_ext_scra_service_end_months`, P5 `hardship_ext_scra_closing_installment`, P6 `hardship_ext_trr_offer_payment`.

### policy_conflict_scan
- Subjects and tools: P1 offered (Reduced Payment Plan) / `offer_reduced_payment_plan_00434f76`; P2 end_date_set (settlement plan months) / `record_settlement_installments_ebffb995` (owner=user); P3 offered (settlement) / `offer_charged_off_settlement_3f4a16ef`; P4 end_date_set (SCRA plan months) / `report_military_service_end_1d04825e` (owner=user); P5 installment_scheduled / `schedule_benefit_plan_installment_71e01653`; P6 offered (Temporary Rate Reduction) / `offer_rate_reduction_plan_52a2ad4e`.
- P2 and P4 both claim `computes: plan_months` on subject `hardship_plan_end_date_set`. They use different target tools and are scoped to different programs (a settlement request vs a Servicemember benefit), so they do not overlap. P2 does misuse the base event: `hardship_plan_end_date_set` means "The end of an open-ended benefit is recorded once known (the service end date for a Servicemember Rate Cap Benefit)", yet P2 uses it to store a borrower's installment choice on a *requested* settlement, and its tool writes no end_date (observation O-6).
- **Conflict found: P4 vs P5.** They disagree about what is owed on the transition due dates (finding F-1).
- **Conflict found: P4 vs base `hardship_evt_offer_terms`.** P4 departs from the base without declaring it (finding F-2).
- **Conflict found: P5 vs base `active_plan_only`.** The clash arises for a benefit with no transition due dates (finding F-3).
- **Conflict found: P1 vs the charter's `max_plan_payment_ratio_percent`.** The charter caps the Reduced Payment Plan installment at 50 % of the scheduled installment, and P1 can exceed it (finding F-4, latent).
- Cross-category reads: all six policies read only `loan` (personal_loan_servicing). The fields they read all exist in `db_schema.json`.
- Two tasks, two disjoint trees. Task 0 covers {P1, P2, P3} and task 1 covers {P4, P5, P6}. Together they cover all six extended policies, and they share no policy and no tool.

### rule_compute_equivalence
- compute_basis sweep (scratch script): every `compute_basis` quote, every `baseline.rule` sentence, every `prerequisite.policy_source` and every `overwrite.replaced_by` is a verbatim substring of its policy's `rule`. Result: no misses.
- Rounding (XF 6): P1, P3, P5 and P6 each say "rounded to the cent once, on the final figure", and each has exactly one outer RND (P1 and P6 use MX(min, RND(..))). P2 and P4 are integers; P2's `int()` matches "remainder dropped". All match.
- DSL conventions the rules rely on:
  - MONTHS(d1, d2) counts a month only when day2 >= day1. This matches the extended rules' wording "a month completed only when the later date reaches the funding day".
  - `within_months=k` keeps rows with 0 <= MONTHS(row, NOW) < k.
  - CFIELD returns the first matching holding.
  - XLATEST keeps the first row among ties.
- Mismatches between rule and compute are findings F-5 to F-8. Checked and matching: P1 (all bindings), P2 (all bindings), P3 apart from good-faith and payment-history, P4 apart from the plan-record factor, P5 (all bindings), P6 apart from AutoPay.

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy.
- The six uuid8s (00434f76, ebffb995, 3f4a16ef, 1d04825e, 71e01653, 52a2ad4e) are pairwise unrelated, with no shared prefix or sequence. No factor id is a substring of any tool name (XF 10).
- Every write tool calls `ctx.update` or `ctx.create` itself. The file has no datetime, random or uuid imports (XF 13).
- No tool body checks a prerequisite state:
  - the settlement offer does not read plan_months;
  - the schedule tool does not read end_date or status;
  - the rate-reduction offer does not look at the other loan.
- Docstring defects (XF 7) are finding F-9.

### prerequisite_graph
- Edges:
  - P3 ← P2: value_input, gate `chosen_installments`, form state.
  - P3 ← P1: state_gate, gate `hardship_plans.status`, form state.
  - P5 ← P4: value_input, gate `step_share`, form state.
  - P6 ← P5: state_gate, gate `hardship_plan_events.installment_due_date`, form state.
- P1, P2 and P4 have `prerequisite: []`. The graph is acyclic and every `problem` is an extended policy of this file.
- `form` is state on every edge and no `fallback_reason` is present, which is correct.
- Each `resolved_by` is the depended-on policy's `target_tool`. Both value_input gates (`chosen_installments` and `step_share`) are real bindings that read `F('plan_months')` (and `F('end_date')`).
- Conditions match their sentences. No authoring-viewpoint phrasing appears.

### prerequisite_sentences
1. **P3 ← P2.** Sentence: "The settlement amount is worked out only after the request records, as its plan months, the number of monthly installments the borrower has chosen."
   - Four-point test: the ordering connective is "only after"; the waited-on thing is a record-visible state (plan months on the request); no tool, id or snake_case is named; the strength matches the condition.
   - Exactly one write of this difficulty sets plan months on a settlement request: P2's tool. P4's tool also writes plan_months, but its policy and docstring scope it to a Servicemember benefit.
   - Derivation: the request's plan months are empty → the reader looks for a rule that records them → P2 ("A borrower settling a charged-off loan records on the pending request, as its plan months, the number of monthly installments chosen …"). There is one reading.
2. **P3 ← P1.** Sentence: "The settlement amount is not fixed until no Reduced Payment Plan request on the borrower's other Larkspur loan still stands in requested status."
   - Four-point test: passes ("not … until"; status state; program named by its official name).
   - The only write of this difficulty that moves a Reduced Payment Plan out of requested is P1's offer. The share tools have no decline write. P1's rule "the decision is owed whether or not the borrower calls", together with the base entry rules, decides offer vs decline from records. There is one reading.
   - Realism of the cross-loan hold: observation O-1.
3. **P5 ← P4.** Sentence: "The closing installment is worked out only after the benefit records its end of military service as its end date together with its plan months." The four-point test passes. The only writer is P4's certification tool. There is one reading.
4. **P6 ← P5.** Sentence: "A Temporary Rate Reduction Plan for a borrower who holds a Servicemember Rate Cap Benefit on another Larkspur loan is not offered until that benefit carries a scheduled plan installment line for the first loan due date after its recorded end of military service." The four-point test passes, and the only line writer is P5's tool. The *date* this sentence names is the one finding F-1 shows to be contested.

No depended-on rule restates its dependent's sentence. No extended rule states a cross-problem order outside these edges. The base `hardship_agg_multi_holding` sentence "first cancels the open request or plan" grounds no edge of this charter (observation O-2).

### override_declarations
- **P1** refs [agg_relief_limits, documents_and_decision, offer_terms, settlement].
  - The Reduced Payment Plan sentence of offer_terms is declared.
  - Followed: "Plan terms are computed from the loan as it stands on the decision date…", the first-due-date rule, "No program charges an enrollment fee", and every sentence of documents_and_decision.
  - Undeclared departure from the parameter-dictionary cap `max_plan_payment_ratio_percent` (F-4).
- **P2** refs [scra_benefit, offer_terms]. "for 2 to settlement_max_installments monthly installments" is declared. Nothing else departs.
- **P3** refs [agg_relief_limits, documents_and_decision, offer_terms, settlement].
  - Two declared overwrites: the offer_terms settlement-amount clause and the hardship_settlement choice clause.
  - The 30-day charge-off minimum, settlement_payment posting and the 1099-C rule are inherited.
  - "Charged-off balance = principal + fees" agrees with `db_schema` `hardship_plans.balance_at_request` ("for a settlement, the charged-off balance (unpaid principal plus unpaid fees)").
- **P4** refs [scra_benefit, plan_installments]. Two overwrites are declared. Undeclared departures from base `hardship_evt_offer_terms` ("it runs from the military service start date until the end of service is recorded") and from the base event field `end_date: Last date the benefit applies` (F-2).
- **P5** refs [plan_installments]. The first sentence is declared. Undeclared departure from "Plan installments are scheduled and credited only while the plan is active", combined with the completion rule P4 leaves in force for a benefit with no transition due dates (F-3). P5 also conflicts with P4 (F-1).
- **P6** refs [agg_relief_limits, documents_and_decision, offer_terms, settlement]. The rate-reduction sentence is declared. Base eligibility is inherited, including `min_documented_income_drop_percent: 20`, which no record can evidence (bears on task 1, see task_1.md).
- Overwrite hygiene (XF 4):
  - every `replaced_by` names its own scope;
  - the sibling overwrites in P2 and P3 retire different clauses of the same base sentence, so they do not collide;
  - no overwrite retires nothing.

### factor_ladders
| policy | factors (effect) | P / M | multi-source factors | cross_difficulty |
|---|---|---|---|---|
| P1 | arrears_base (M), documented_hardship (P), loan_tenure (P), rate_grade (P), second_loan_standing (P), autopay_record (P) | 5/1 | documented_hardship (reason × document row), autopay_record (holding flag × ledger returns), arrears_base | loan ×5 |
| P2 | balance_term (M), bounced_payment_cut (P), active_loan_arrears (P), hardship_kind_extension (P) | 3/1 | bounced_payment_cut (return row × payment row), hardship_kind_extension (plan reason × document row), balance_term | loan ×3 |
| P3 | term_pricing (M), charge_off_age (P), good_faith_payments (P), relationship_standing (P), documented_severity (P), predefault_history (P) | 5/1 | term_pricing (loan × request plan months), good_faith_payments, documented_severity | loan ×5 |
| P4 | service_length_transition (M), benefit_record_transition (P), certification_timing (P), advance_notice (P) | 3/1 | service_length_transition (benefit dates × line rows), benefit_record_transition (plan events × loan ledger) | loan ×1 |
| P5 | benefit_length_share (P), step_target (M), loan_grade_relief (P), loan_tenure_relief (P), debit_record_relief (P) | 4/1 | benefit_length_share (plan months × dates), step_target, debit_record_relief | loan ×4 |
| P6 | documented_rate (P), repayment_shape (M), rate_tenure (P), rate_autopay (P), rate_grade_relief (P) | 4/1 | documented_rate (reason × document rows), rate_autopay | loan ×4 |

- Every ladder has three disjoint tiers, and its fall-through equals the factor's `baseline`. Every tier is a sentence of the rule and a branch of its `decides` binding. Every `decides` is an input binding, never `result`, and the binding sets are disjoint.
- Labels:
  - method tiers change the formula shape: proportional / sale-review / max; linear / flat / two-step; proportional / position test / none; level / equal-principal / pre-plan;
  - parameter tiers change only numbers.
- **Structural or realism defects:** F-10 (P6 rate_tenure tier restates the program's scope), F-11 (P1 second_loan_standing rewards a default with deeper relief), F-12 (the "equal principal plus one month's interest" shape is a payment-raising method in a payment-relief program, P6 tier 1 and P5 tier 2), F-13 (P5 relief ladders invert when the step-back target is below the plan installment), F-14 (XF 1: P6 repayment_shape binding reads the assembled plan rate), F-15 (XF 2/3: assembly sentences that name factor quantities).
- Observations:
  - O-3: P3 term_pricing tiers coincide at single points (≥2000 with 6 installments gives 70 = two-step 70; under 1000 with a single payment gives 55 = 55). Each pair still has distinguishing inputs.
  - O-4: grade-based relief direction in P1, P5 and P6.

### findings
Each finding has the form symptom → root cause → evidence → consequence, followed by the tasks it bears on.

- **F-1 SOURCE-POLICY RED — P4 and P5 disagree about the transition due dates.**
  - Symptom: P4 extends the benefit through "transition due dates" after the end of service, while P5 makes the first due date after the end of service the closing installment on which "the loan's original installment resumes".
  - Root cause: two extended rules govern the same due date with incompatible treatments, and no rule says what installment a transition due date carries.
  - Evidence:
    - P4 rule: "the benefit lasts through the end of military service and through the transition due dates worked out below"; "The plan months recorded are the due dates of the service period plus the transition due dates".
    - P4 overwrite on plan_installments: "A Servicemember Rate Cap Benefit with transition due dates completes only once its last transition due date has passed".
    - Base scra_benefit (in force for the benefit's duration): "The installment is lowered to the level payment at the capped rate".
    - P5 rule: "the first loan due date after the end of military service also carries a plan installment line, the closing installment"; "so that the loan's original installment resumes on that due date".
  - Consequence: on any world where the transition due dates are ≥1, the installment owed on the first due date after service is the capped benefit installment under P4 + base, but the closing step-back installment under P5. A second defensible reading puts the closing line after the last transition due date. Task 1 demonstrates this.
  - Bears on: task 1.
- **F-2 SOURCE-POLICY RED (XF 4, undeclared departure) — P4 vs base `hardship_evt_offer_terms`.**
  - Evidence: base offer_terms says the benefit "runs from the military service start date until the end of service is recorded". The base event field says "`end_date: Last date the benefit applies`". P4 records end_date = end of service while the benefit applies through later transition due dates. offer_terms is in neither P4's `base_policy_refs` nor its `overwrite`.
  - Consequence: following that base sentence, the benefit covers only the service-period due dates, so plan_months equals P4's baseline (the count of service-period due dates) and not the extended count. Task 1 shows the second answer.
  - Bears on: task 1.
- **F-3 SOURCE-POLICY RED (XF 4, latent) — P5 vs base `active_plan_only`.**
  - Evidence:
    - Base: "Plan installments are scheduled and credited only while the plan is active."
    - P4 leaves in force: "one without them completes once the recorded end date has passed".
    - P5 schedules its line on a due date *after* the end of service.
  - Consequence: for a benefit with zero transition due dates, the plan has completed before that due date, so base forbids the very line P5 says is owed. That gives two conclusions (schedule vs no line).
  - Bears on: no task world. In task 1 the transitions are 5 and the benefit stays active.
- **F-4 SOURCE-POLICY RED (latent) — P1 vs the Reduced Payment Plan's 50 % ceiling.**
  - Evidence: parameter_schema says `max_plan_payment_ratio_percent: "Highest plan installment as a percent of the scheduled installment"` and the Reduced Payment Plan value is 50. P1's arrears tier says "the payment base is the scheduled installment plus that amount past due divided evenly over the program's plan months".
  - Constructed case: scheduled 206.50, past due 413.00, no points. P1 gives (206.50+137.67)×50 % = 172.08, which is 83 % of the scheduled installment. The cap reading gives 103.25.
  - Bears on: no task world. Task 0's Reduced Payment Plan is 44 %.
- **F-5 SOURCE-POLICY RED (XF 8) — P3 good-faith.**
  - Rule: "at least two payments posted in the six calendar months before the decision date and none of those payments returned" and "at least one payment in those six months that still stands".
  - Compute: `recent_returns == 0` counts any return dated in the window, and "still stands" is approximated by `recent_payments - recent_returns`.
  - Constructed case: decision 2026-10-16; a payment posted 2026-04-15 (outside the window) is returned 2026-04-17 (inside); two clean payments are in the window. The rule gives 6 points; the compute gives 3.
  - Bears on: no task world (task 0's return pairs with an in-window payment).
- **F-6 SOURCE-POLICY RED (XF 8) — P3 payment history.**
  - Rule: "scheduled installments paid and never returned before it was charged off".
  - Compute: `paid_installments` has no date bound at the charge-off date. A scheduled_installment payment posted after charge-off (the loan charter accepts payments on charged_off loans) is counted by the compute and excluded by the rule.
  - Bears on: no task world (task 0's post-charge-off payments are partial_installment).
- **F-7 SOURCE-POLICY RED (XF 8) — P4 plan record.**
  - Rule: "all fully credited"; base `hardship_evt_plan_installments` says "a payment credited and later returned no longer counts" and the `hardship_msr_unpaid_plan_installments` measure is "net of credited payments later returned".
  - Compute: `lines_credited_total` sums every credited row, net of nothing.
  - Constructed case: one 100.00 line credited by a payment that was later returned. The rule gives "not fully credited" → −1; the compute gives "fully credited, payment returned" → 0.
  - Second member: with zero lines and zero payments, the rule's tier 1 holds vacuously (+1), and the rule describes its fall-through only as "fully credited but with a returned plan payment". The compute requires `posted_plan_payments >= 1` → 0.
  - Bears on: no task world (task 1 has 8 credited lines and no returns).
- **F-8 SOURCE-POLICY RED (XF 8) — P6 AutoPay.**
  - Rule: "a loan with AutoPay enrolled whose AutoPay debits of the twelve calendar months before the decision date all stood, none returned".
  - Compute: adds `autopay_debits_12m >= 1`, a condition the rule does not state.
  - Constructed case: AutoPay enrolled with no debit yet in the window. The rule gives 0.25 off; the compute gives 0.
  - Bears on: no task world.
- **F-9 SOURCE-CHAIN/XF 7 RED — docstrings.**
  - `offer_charged_off_settlement_3f4a16ef` docstring: "the settlement installment payable for each of the monthly installments already recorded on the request". "Already" states that the installment record comes first, which is the P3 ← P2 order, at the tool layer.
  - `offer_reduced_payment_plan_00434f76` and `offer_rate_reduction_plan_52a2ad4e` carry the concrete example "(e.g. 12.49 means 12.49%)" for interest rates. XF 7 says to describe the format only.
  - Bears on: task 0 (the "already" docstring) and both tasks (the examples). Whether an example equals a scored value is checked after the reveal.
- **F-10 SOURCE-FACTOR RED — P6 rate_tenure tier restates the program's scope.**
  - Evidence: Temporary Rate Reduction Plan `min_months_since_funding: 6`, and base seasoning "the request is taken only when the current date is at least the program's minimum months after the loan's funding date". Tier 2 is "funded at least 6 but fewer than 12 whole calendar months"; the fall-through is "a younger loan takes none".
  - Every request that reaches this write has at least 6 months, so the "≥ 6" condition holds of every customer and the fall-through (= baseline 0) is a value no eligible borrower receives.
  - The only way the fall-through can be reached is through a month-end convention clash. Base counting is "when the later month has no matching day the last day of that month is used"; P6 counting is "a month counting as complete only when the later date reaches the funding day". Example: funded 08-31, request 02-28 → base 6, P6 5.
  - Bears on: task 1.
- **F-11 SOURCE-FACTOR RED (realism) — P1 second_loan_standing.**
  - Evidence: "a borrower who holds another Larkspur personal loan in charged_off status earns other_loan_points_charged_off points; a borrower … who holds another Larkspur personal loan closed as settled or paid_after_charge_off earns other_loan_points_recovered points". The points are subtracted from the payment percentage, so a deeper payment cut goes to a borrower who already defaulted with Larkspur, or who settled a loan with Larkspur for less than was owed.
  - No US consumer lender publishes a hardship schedule that grants extra concession *because* the borrower caused it a charge-off or settlement loss. The loan charter treats a charged-off loan as a bar to new credit ("No personal loan of the borrower is in charged_off status").
  - Bears on: task 0.
- **F-12 SOURCE-FACTOR RED (realism) — equal-principal shape in payment-relief programs.**
  - P6 repayment_shape tier 1: "pays, on each plan due date, its unpaid principal divided evenly over those due dates plus one month's interest". P5 step_target tier 2 uses the same shape.
  - At any rate above zero and with more than one due date left, this payment is higher than the level installment at the same rate. A temporary *rate-reduction* plan exists to lower the payment, and a consumer installment lender does not switch a near-maturity borrower to a front-loaded payment in a relief program.
  - Bears on: task 1 (P6 tier 1 taken).
- **F-13 SOURCE-FACTOR RED (realism) — P5 relief ladders invert.**
  - P5's three "relief" ladders (grade, tenure, AutoPay) and its benefit-length share assume the installment stepped back to exceeds the plan installment.
  - Where it is lower (tier 1 re-amortization after additional-principal payments), each "relief" point *raises* the closing installment, and a longer benefit (share 25) charges more than a short one (share 100).
  - Bears on: task 1, which demonstrates it.
- **F-14 SOURCE-FACTOR RED (XF 1) — P6 repayment_shape reads other factors.**
  - The `installment_shape` binding reads `plan_rate`, which is assembled from documented_rate, rate_tenure, rate_autopay and rate_grade_relief, so the factor binding transitively reads four factors' outputs and assembles the result inside a factor binding (`result` only clamps and rounds it).
  - Bears on: task 1.
- **F-15 SOURCE-POLICY RED (XF 2/3) — assembly sentences name factor quantities.** All members:
  - P2: "taking the term the balance allows, subtracting every installment cut that applies, then adding any installment extension". This names the starting-term, cut and extension quantities.
  - P5: "replaces the share of the difference or the installment stepped back to … applied once to the difference between the installment stepped back to and the plan installment". "Installment stepped back to" is step_target's quantity.
  - P6: "replaces the plan rate or the repayment shape". "Repayment shape" is the factor's own subject.
  - P1, P3 and P4 phrase their assembly generically ("the replacement", "every point that applies", "the transition due dates from every rule above"), so they are not members.
  - Consequence: the computation document must carry the assembly sentence, so it names factor quantities.
  - Bears on: task 0 (P2) and task 1 (P5, P6).

Observations (no consequence demonstrable):
- O-1 realism of the two cross-loan holds (P3 ← P1, P6 ← P5). A whole-relationship review is defensible.
- O-2 the base cross-problem sentence in agg_multi_holding.
- O-3 P3 term_pricing point coincidences.
- O-4 grade-based relief direction.
- O-5 "additional-principal payments of at least X" can be read as a sum or as any single payment (P1, P5). Compute uses the sum, and a returned additional-principal payment is not netted.
- O-6 P2 uses the `hardship_plan_end_date_set` event for a requested settlement.
- O-7 `within_months` boundary: a row dated exactly k months back is excluded.

## closing_checklist
Not closed in revision_1: neither task passes all four relationships.

| check | status |
|---|---|
| per-task files | `0.md`, `1.md` and this file correspond one-to-one with tasks 0 and 1. Each blind derivation was frozen before any reveal (mtimes 04:56:03Z / 04:57:02Z / 04:57:55Z; first GT read 04:58:00Z). |
| scope | holds. {P1, P2, P3} and {P4, P5, P6} are disjoint, jointly complete and tool-disjoint. Every uuid8 is independent. |
| problem trees | hold. Each task has 2 prerequisites, 1 value_input edge and 1 owner=user write; both graphs are acyclic and the difficulty-wide graph is acyclic. |
| factors | do not hold. Counts and bounds pass. REDs F-10 to F-14 remain, of which F-11 bites task 0 and F-10, F-12, F-13, F-14 bite task 1. |
| policy self-consistency | does not hold (F-1 to F-9, F-15). |
| unique solution | task 0 matches GT. Task 1 does not hold (R-1.1, R-1.3 in `1.md`). |
| gate re-run on final form | not applicable until rework. |

Open charter-wide REDs: F-1 F-2 F-3 F-4 F-5 F-6 F-7 F-8 F-9 F-10 F-11 F-12 F-13 F-14 F-15.

VERDICT revision_1: task0=RED SOURCE-FACTOR/SOURCE-POLICY/SOURCE-CHAIN task1=RED SOURCE-POLICY/SOURCE-TASK/SOURCE-FACTOR charter=F-1,F-2,F-3,F-4,F-5,F-6,F-7,F-8,F-9,F-10,F-11,F-12,F-13,F-14,F-15

## revision_2

## charter_global_frozen (revision_2)
- Written before any round-2 GT read. It is built from the charter, the tools, the blueprint and the XF recipe only.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 2: gates 7/7 green`.
- Gate snapshot: `/tmp/erl0067_coord/snapshot.sh hardship_assistance_plans 2` (2026-10-16T11:14:24). EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY NOT OK. The miss list is checked after the task freezes (see closing_checklist r2).
- Hashes:
  - `hardship.extended.yaml` cedb5bb7ba128dbb3ee4031273869c909385d01857bd1f898b94c46061ddfafd;
  - `task_tools.py` d0dc45f377008b721b95061fe050e4b4bf23c2d6e749d49b4da40ecb8bda5b8c;
  - views `r2/task_0.json` 91e563d6… (= r1) and `r2/task_1.json` bd947436….
- Both shared inputs changed, so every charter-global section is re-derived in full. The blueprint mtimes predate round 1, so the blueprint is unchanged, and the base copy is still byte-identical.
- Reworker claims are read by item id from `rework_r2_claims.md`. Each is verified below against the charter, not accepted.

### policy_conflict_scan (r2)
- Subjects, tools and the two task scopes are unchanged: {P1, P2, P3} and {P4, P5, P6}, disjoint and complete.
- P4 and P5 now govern the same due dates the same way. The covered due dates run through the latest line, and the graduated-return due dates follow it one month apart. The end date is the last graduated-return due date, so base completion ("once the recorded end date has passed") keeps the benefit active through them.
- New conflict N-4: P4's protection start vs the base parameter `benefit_effective_basis: "military service start date (retroactive)"` (base `hardship_scra_benefit` params) and the base field `start_date … the service start date (Servicemember)`.

### rule_compute_equivalence (r2)
- Scratch sweep: every compute_basis quote, baseline sentence, policy_source and replaced_by is verbatim in its rule; every superseded_clause is verbatim in the base. 0 misses.
- Rounding:
  - P1 is MX(min, MN(RND(cap), RND(x))), matching "rounded … once … then held to no more than … rounded to the cent, and to no less than";
  - P3, P5 and P6 have a single outer RND;
  - P2 and P4 are integers.
- Look-back boundary sentences are present in P1, P2, P3 (good-faith), P5 and P6, and match `_within` (MONTHS < k).
- Mismatches found:
  - **N-1:** the P1 payment-record rule says "installment payments", but the compute filters `payment_type='scheduled_installment'` only.
  - **N-2:** P5 promises an installment for every graduated-return due date but works out only the first.

### action_binding_and_uuids (r2)
- The (tool, computes) pairs and uuid8s are unchanged and unique.
- Docstrings carry no example values, no "already" or ordering words, and no other tool names. The certification end_date is described as "the last loan due date the benefit applies to", which matches the base field.
- Imports are erlbench only. Each write tool writes in its own body. No body checks a prerequisite.

### prerequisite_graph (r2)
- Edges: P3 ← P2 (value_input), P3 ← P1 (state_gate), P5 ← P4 (value_input, gate `graduated_due_dates`, a real binding reading F('end_date')), P6 ← P5 (state_gate). Acyclic. All forms state, no fallback_reason.

### prerequisite_sentences (r2)
- P3's two sentences and P5's sentence ("worked out only after the benefit records its end date together with its plan months") pass the four-point test, with one writer each.
- **N-3 — P6's new sentence.** "…for a borrower who holds a Servicemember Rate Cap Benefit with graduated-return due dates on another Larkspur loan is not offered until that benefit carries a scheduled plan installment line for its first graduated-return due date."
  - The scope qualifier "with graduated-return due dates" depends on a state P5 defines only against the *recorded* end date: "The graduated-return due dates of a benefit are the whole calendar months from the latest due date carrying a plan installment line to the recorded end date".
  - Before P4's write, a benefit therefore has no graduated-return due dates by definition, and the sentence does not bind.
  - The edge's `condition` carries no such qualifier, so the sentence is narrower than the condition. It admits a second reading in which the hold is vacuous at the opening.

### override_declarations (r2)
- P1: the Reduced Payment Plan sentence is declared. The cap is now applied (F-4 closed).
- P2 and P3: as in round 1. P3's base clause fragments stay disjoint from P2's.
- **P4.** Three overwrites:
  1. scra "The benefit lasts until…";
  2. scra "The benefit applies from the military service start date…";
  3. offer_terms "it runs from the military service start date until the end of service is recorded." (F-2 closed).

  Undeclared departure (N-4): the base parameter `benefit_effective_basis` "military service start date (retroactive)", read by base policy `hardship_scra_benefit` params, and the event field `start_date` meaning "the service start date (Servicemember)". Under P4's protection start the benefit's start is the request date.
- **P5.** Three overwrites (plan_installments line sentence; scra installment sentence; offer_terms SCRA installment clause), each self-scoped and disjoint from P4's. Base `active_plan_only` and completion are now consistent (F-3 closed).
- **P6.** Overwrite of the rate-reduction sentence. It adds `hardship_program_eligibility` to its refs and adds an income-drop reading sentence, which extends rather than conflicts. Observation O-9: "the borrower reads both figures from the statements when asked" sits next to base documents_and_decision "a borrower's description of a document is never a substitute for the recorded document". The documents are recorded and the figures come from them, so no second conclusion is forced.

### factor_ladders (r2)
| policy | factors (P/M) | changes from r1 | structure |
|---|---|---|---|
| P1 | 6 (5/1) | second_loan_standing → prehardship_record | net payments 11+ / 6–10 / else (realistic: clean record → more relief) |
| P2 | 4 (3/1) | none | |
| P3 | 6 (5/1) | term_pricing tiers re-bounded | linear only for 2 ≤ n < max, flat only for n ≥ 2. The r1 point coincidences are gone (O-3 closed) |
| P4 | 4 (3/1) | protection_start (P), payment_step_return (M), service_length_return (P), loan_tenure_return (P) | protection start follows the SCRA reservist rule (realistic) |
| P5 | 5 (4/1) | step_schedule (M), autopay_relief, prepayment_relief, grade_relief, remaining_term_relief | the target is now the pre-plan installment and the step ≥ 0, so every point lowers the line (F-13 closed) |
| P6 | 5 (4/1) | repayment_shape decides a code only (F-14 closed); shape code 2 passes on the interest saved (F-12 closed); tenure 24/12 (F-10 closed) | |

- Every ladder has 3 disjoint tiers, the fall-through equals the baseline, and the tiers are distinct in outcome.
- Method tiers change shape:
  - P4 step: proportional / flat / none;
  - P5 schedule: 1/(k+1) / flat 50 / 100;
  - P6 shape: principal-part + plan interest / interest-only / level.
- Labels are honest. protection_start's tiers change only the anchor date of the same due-date count, so `parameter` is acceptable.
- XF 1: no factor binding reads another factor's output.
- XF 2: P1–P6 assembly sentences are generic ("the replacement", "every point/reduction/addition", "every graduated-return due date"). F-15 closed.
- **N-5 (XF 3), every member listed.** These are factor-only quantities defined in a sentence outside their factor's own sentence:
  - P2 "A loan with no charge-off date recorded counts no months since charge-off." This is used only by balance_term, and it is appended to the look-back sentence, which itself is used only by bounced_payment_cut.
  - P3 "A loan with no charge-off date recorded counts no days since charge-off." Used only by charge_off_age.
  - P5 "The graduated-return due dates of a benefit are the whole calendar months from the latest due date … to the recorded end date…". Used only by step_schedule.
  - Shared conventions are not members: P1's look-back sentence (three factors) and P5's twelve-month sentence (two factors).

### findings (r2)
Round-1 items, verified against the r2 charter:

| item | status | how verified |
|---|---|---|
| F-1 | CLOSED | P4 and P5 now define the same due dates |
| F-2 | CLOSED | offer_terms clause overwritten |
| F-3 | CLOSED | end date = last graduated date; base completion is consistent |
| F-4 | CLOSED | cap in rule, compute and baseline params |
| F-5 | CLOSED | rule restates compute |
| F-6 | CLOSED | "ever posted, less returned" |
| F-7 | CLOSED | ladder removed; P5 nets returns and requires ≥ 1 line |
| F-8 | CLOSED | P5 and P6 state the ≥ 1-debit condition, including the enrolled-without-debit case |
| F-9 | CLOSED | docstrings |
| F-10 | CLOSED | |
| F-11 | CLOSED | |
| F-12 | CLOSED | code 2 = scheduled principal part + plan interest, below the level installment at the plan rate for an on-schedule loan |
| F-13 | CLOSED | |
| F-14 | CLOSED | |
| F-15 | CLOSED | |
| O-3, O-5, O-7 | closed | |
| O-1, O-2, O-4, O-6 | kept (observations) | |

New findings:
- **N-1 SOURCE-POLICY RED (latent, check 2), P1 prehardship_record.**
  - Rule: "the installment payments posted in the twelve calendar months before the decision date, less the installment payments returned".
  - Compute: counts only `payment_type='scheduled_installment'`. The ledger has `partial_installment` and `hardship_plan_payment` types, both of which are installment payments in plain words.
  - Constructed case: 10 scheduled plus 2 partial-installment payments in the window, no returns. The rule reading gives 12 → 3 points; the compute gives 10 → 1 point.
  - Bears on: no task world (task 0's L2 has only scheduled_installment rows).
- **N-2 SOURCE-POLICY RED (latent, check 2: empty promise), P5.**
  - The overwrite and rule promise "the line on each graduated-return due date is for the graduated-return installment worked out below", but the rule works out only "The first graduated-return installment". The "equal step, one part in the number of its graduated-return due dates plus one" names no rule for the second and later due dates.
  - Consequence: the 2026-11-15, 12-15 and 2027-01-15 lines of task 1's benefit have several readings (the same share, 2/5, 3/5, or the pre-plan installment).
  - Bears on: no scored write in either task.
- **N-3 SOURCE-POLICY RED (check 6), P6 sentence scope.**
  - The second reading makes the hold vacuous at the opening, so the offer is defensible without the P4/P5 writes.
  - Bears on: task 1, demonstrated in `1.md` § revision_2.
- **N-4 SOURCE-POLICY RED (undeclared departure; XF 4 last bullet), P4 protection start.**
  - Base `benefit_effective_basis` "military service start date (retroactive)" and field `start_date` "the service start date (Servicemember)" against the P4 tier "counts its covered due dates from the request date".
  - P4's overwrite also declares that "interest already paid above the cap since that start is credited to principal". Whether a world seeded under the base start can carry this tier is checked per task.
  - Bears on: task 1.
- **N-5 SOURCE-POLICY RED (XF 3).** Three members, listed above.
  - Bears on: task 0 (P2, P3) and task 1 (P5).
- Observations:
  - O-9: income figures read by the borrower.
  - O-10: P4 alone does not say what end date is recorded when no graduated-return due date applies. P5 implies the latest line due date.
  - O-11: "graduated-return due dates follow the latest due date carrying a plan installment line" can leave service-period due dates uncovered when lines lag the end of service. This is latent: task 1 has its latest line on 09-15 and the end of service on 09-30.

## closing_checklist (revision_2)
Not closed.

| check | status |
|---|---|
| per-task files | `0.md` and `1.md` carry revision_2 freezes. GT was read at 11:20:56Z, after all three r2 sections were on disk. |
| gates | snapshot 2026-10-16T11:14:24: 7/7 OK. TRACEABILITY misses are 6 unlock tool names only (verified after the freeze). |
| scope, trees, uuids | unchanged and holding (2 prerequisites, 1 value_input, 1 user write per task; acyclic). |
| factors | all r1 factor REDs closed. All factors bear weight on both worlds (sensitivities match GT figure for figure). |
| round-1 REDs | F-1 to F-15 closed; R-0.1 to R-0.4 and R-1.1 to R-1.6 closed. |
| still open | N-1 (latent), N-2 (latent), N-3 (task 1), N-4 (task 1), N-5 (tasks 0 and 1). |
| regression | none on scored values. Every r2 value equals my blind derivation; task 0 values equal r1. |

VERDICT revision_2: task0=RED SOURCE-POLICY task1=RED SOURCE-POLICY/SOURCE-TASK charter=N-1,N-2,N-3,N-4,N-5

## revision_3

## charter_global_frozen (revision_3)
- Written before any round-3 GT read.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 3: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh hardship_assistance_plans 3` (2026-10-16T15:37:20): EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY NOT OK is pre-publication. Per the brief, I did not run check_traceability myself this round.
- Hashes:
  - charter 0c6d8ba076514081d9b3d3b5f030bcb41ee80a820bf1d6997217624bd28c33ba (changed);
  - `task_tools.py` d0dc45f377008b721b95061fe050e4b4bf23c2d6e749d49b4da40ecb8bda5b8c (unchanged since r2);
  - views r3/task_0 91e563d6… (unchanged) and r3/task_1 a4192fa1….
- Re-derived sections: the charter changed, so all charter sections below are re-derived. The tool sections (action binding, uuids, docstrings) are carried from revision_2 by reference on the unchanged tools hash. The blueprint is unchanged (mtimes 2026-10-15) and the base copy is byte-identical.
- This round I swept the whole charter class by class: XF 1–14, checks 1–7, and realism on all six policies.

### sweeps (r3)
- Verbatim (compute_basis, baseline sentences, policy_source, replaced_by in rule; superseded_clause in base): 0 misses.
- Rounding: matches in all six policies.
- No factor id is a substring of a tool name.
- XF 1 (independence):
  - P4 record_due_dates reads its own bindings;
  - P5 step_schedule reads next_due and remaining_due_dates (its own), while prev_amount is plain;
  - P6 shape decides a code.
  - No member.
- XF 2 (assembly): generic in all six. P4 "Every graduated-return due date that applies is added to the covered due dates" commutes. No member.
- XF 3 (factor-only quantities outside their factor sentence):
  - P2's guard and boundary, and P3's guard, are now inside their factor sentences;
  - P5's "still to come" is defined inside "Step schedule:";
  - P5's "A graduated-return due date is a loan due date after the benefit's last covered due date and on or before its recorded end date" is a scope/trigger definition used by the line rule, not by a factor;
  - P1's look-back and P5's twelve-month sentences are shared by two or more factors.
  - No member. N-5 closed.
- XF 4 (overwrites):
  - P4 retires scra "The benefit lasts until…" and offer_terms "it runs from … until the end of service is recorded.";
  - P5 retires the plan_installments line sentence, the scra installment sentence and the offer_terms SCRA installment clause;
  - all are disjoint, self-scoped and conflicting.
  - Base `benefit_effective_basis` "military service start date (retroactive)" now agrees with P4 ("runs from the military service start date"). N-4 closed charter-side.
- XF 8 (edges):
  - P4: absent lines → 0 plan months and end date = end of service; absent end of service → no extra covered due dates and no duty/tenure; a negative step → none; month-end convention stated ("the later date reaches the earlier date's day").
  - P5: the previous-line tie ("the line recorded first") matches LATEST's first-row tie; absent end date → none still to come → whole step; returned plan payments are netted.
  - P1 (N-1 closed) and P3 payment kinds now match their filters.
- XF 9 (tier coincidence): P4 record 2/1/0 and step proportional/flat/none; P5 1/(n+1) ≤ 25 / 50 / 100. No coincidence.
- XF 12 (realism):
  - P4 plan-record return (a clean plan record earns a longer phase-in) is realistic;
  - P5 relief points lower the line;
  - O-4 is kept.
- Check 6:
  - P6's new sentence is scoped by opening-visible facts (active benefit, end of service captured) and waits on a line for the loan's next due date. It matches its condition. N-3 closed.
  - P5's sentence passes.
  - P3's sentences are unchanged and pass.

### findings (r3)
| item | status |
|---|---|
| N-1 | CLOSED |
| N-2 | CLOSED: every graduated-return line is defined (previous line + share of the step up, share read from the due dates still to come) |
| N-3 | CLOSED |
| N-4 | CLOSED (charter and seed; see `1.md` r3) |
| N-5 | CLOSED |
| O-10, O-11 | closed (the end date with no graduated-return due date is defined; lagging lines are covered through the end of service) |

New:
- **M-1 SOURCE-POLICY RED (latent, check 6 / SOURCE-CHAIN shape) — P6's hold can wait on a back-office transition.**
  - The hold binds every borrower whose other loan "carries an active Servicemember Rate Cap Benefit with the end of military service captured on it".
  - For a benefit that earns no graduated-return due date, P4 records "its last covered due date as its end date" and no rule schedules any line after it. P5 lines exist only on graduated-return due dates, and base lines run "from its start date through its end date".
  - The loan's next due date therefore never gets a line. The hold lifts only when the system completes the benefit ("completes once the recorded end date has passed", a `by: system` transition), which no write of this difficulty performs.
  - Meanwhile base documents_and_decision says the rate-reduction request "is made within the program's decision business days".
  - Constructed world: plan record with an unpaid line (0), step < 5 % (0), service < 180 days (0), loan < 24 months (0) → end date = last covered due date. The agent can neither satisfy the hold nor decide the request on time, so the only solution is to wait.
  - The class has one member. P3 ← P1 is not a member: its waited-on state is always produced by a charter decision, offer or base decline. The decline path has no task tool, which is observation O-14 below.
  - Neither task is affected: task 1's benefit earns 6 graduated-return due dates.
  - Disclosure: this world became possible with the r3 scope change; it is not a regression of any scored value.
- Observations:
  - O-12: P6's hold can also be resolved by a *covered* due-date line under the base line rule (same tool) when lines lag the end of service, so the declared `problem: P5` would not be the governing policy in such a world. This is latent.
  - O-13: same-day previous-line ties rely on row insertion order matching "recorded first".
  - O-14: missed in r1/r2, disclosed now. An ineligible Reduced Payment Plan request blocking P3 can be resolved only by a base decline, for which this difficulty has no tool. It is a hand-off path, not a contradiction.

## closing_checklist (revision_3)
| check | status |
|---|---|
| per-task files | `0.md` and `1.md` carry r3 freezes before the 15:40:38Z reveal. Old revisions are untouched. Both comparisons are PASS. |
| scope | {P1, P2, P3} and {P4, P5, P6}: disjoint, complete, tool-disjoint. uuid8s are independent (tools unchanged since r2). |
| trees | each has 2 prerequisites, 1 value_input edge and 1 owner=user write; acyclic, also across the whole difficulty. |
| factors | every computation has 4–6 factors with ≥ 2 P and 1 M. Each task has multi-source (P3 documented_severity / P6 documented_rate and more) and cross-difficulty factors (loan) on seeded rows. Every factor bears weight against an honest baseline, and baseline-only ≠ gold on all six computations. |
| gates on final form | 7/7 OK in the r3 snapshot. TRACEABILITY is pre-publication and was not run by me this round, per the brief. |
| open charter RED | M-1 (latent; no task world). |

The difficulty does not close until M-1 is resolved.

VERDICT revision_3: task0=PASS task1=PASS charter=M-1

## revision_4

## charter_global_frozen (revision_4)
- Written before any round-4 GT read.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 4: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh hardship_assistance_plans 4`: EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY is pre-publication and was not run by me.
- Hashes: charter 551d6cd1e53a8d1245736e3d1a210eb6a452b62d814f644fab37be5731464435; tools d0dc45f3… (unchanged); views r4/task_0 91e563d6… and r4/task_1 a4192fa1… (both = r3).
- The base copy is byte-identical and the blueprint is unchanged.
- What moved: P3 (one sentence), P5 (covered-line sentence, previous-line sentence, compute) and P6 (hold scope). P1, P2 and P4 are unchanged. Every charter section is re-checked below over all six policies.

### sweeps (r4)
- Verbatim (compute_basis, baseline sentences, policy_source, replaced_by; superseded_clause in base): 0 misses.
- Every factor binding and decides is a compute name, binding sets are disjoint, and no factor id is in a tool name.
- XF 1: P5's `covered_line` and `next_due` are plain and read by `result` and `remaining_due_dates`, and no factor reads another factor. No member.
- XF 2: the assemblies are unchanged and generic. No member.
- XF 3: the covered-due-date and previous-line definitions are scope and baseline quantities, not factor-only quantities. No member.
- XF 4: overwrites are unchanged. The P5 replaced_by already states covered due dates at the plan installment, and the new rule sentence agrees. No member.
- XF 6: rounding matches; the covered line is RND(plan installment) and the graduated line has one final RND.
- XF 8 (edges):
  - same-day lines are summed, so there is no row-order dependence (O-13 closed);
  - the cap is stated in both rule and compute;
  - absent lines fall back to the plan installment;
  - absent end of service gives a covered line;
  - absent end date gives none still to come.
  - No member.
- XF 9 and XF 12: unchanged; no member.
- XF 7 and XF 13: tools unchanged; no member.
- XF 14: checked at reveal.
- Check 6:
  - The P6 hold's scope is opening-visible. Every reachable state is lifted by a write in this difficulty:
    - next due date covered → P5 covered line;
    - graduated → P4 then P5;
    - no graduated-return due date → P4's end date < next due date takes the benefit out of scope.
  - M-1 closed.
  - P3's hold now states its outcome when the request cannot be offered (hand-off). O-14 closed.
  - P5's sentence is unchanged and passes.
- Hold sweep, every hold in the charter:
  - P3 ← P2 and P5 ← P4 are user and record writes, always available.
  - P3 ← P1 is an offer, or the stated hand-off.
  - P6 ← P5 is covered above.
  - Observation O-15: a Reduced Payment Plan request still inside its 14-day document window can be neither offered nor declined. The P3 sentence routes it to the hand-off ("cannot be offered under its program's rules"), so an outcome is stated.
- Check 1 (overrides): the P3 hand-off assigns a decline to "the hardship desk", while the base lifecycle lists requested→declined `by: agent`. This difficulty has no decline tool, so the representative can act only by handing off, under either reading. No differing terminal state, so this is observation O-16.

### findings (r4)
| item | status |
|---|---|
| M-1 | CLOSED |
| O-12 | closed |
| O-13 | closed |
| O-14 | closed |

No new RED found in a full-charter sweep. Observations kept: O-1, O-2, O-4, O-6, O-9, O-15, O-16.

## closing_checklist (revision_4)
| check | status |
|---|---|
| per-task files | one per task. The r4 freezes preceded the 21:20:07Z reveal. Old revisions are untouched. Both comparisons are PASS. |
| coverage and scope | all six extended policies are covered. Task scopes {P1, P2, P3} and {P4, P5, P6} are pairwise disjoint and include each whole tree. Task tools and GT are closed. uuid8s are independent and frozen. |
| trees | each task has 2 prerequisite problems, 1 value_input edge (≥ max(2 − 1, 1)) and 1 owner=user write (P2, P4). The difficulty-wide graph is acyclic. |
| factors | every computation has a self-sufficient baseline and 4–6 factors with ≥ 2 parameter and 1 method. Each task has multi-source and cross-difficulty (loan) factors on seeded rows. Every ladder has 3 distinct tiers stated in the rule, and its conditions and outcomes are realistic. Every factor bears weight, and baseline-only ≠ gold for all six (103.25/90.86, 6/3, 2764.48/1421.73, 8/14, 333.26/296.78, 273.37/258.61). |
| gates on final form | 7/7 OK in the r4 snapshot. TRACEABILITY is pre-publication only (unlock tool names, verified in r2; not re-run by me per the brief). |
| open REDs | none. Observations O-1, O-2, O-4, O-6, O-9, O-15, O-16 are recorded and are not grounds for rework. |

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Written before any round-5 GT read.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 5: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh hardship_assistance_plans 5` (2026-10-17T02:12:35): EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY is pre-publication and was not run by me.
- Hashes:
  - charter eada409383d1a50bfc8a0146b4cd2e9bf0946b6ce1c051db8eb763786b0a2f54 (changed);
  - `task_tools.py` 746ee48bcfece1b53dc33ddf897c185440faea3ac3212d3a36cc6ed62511e8b5 (changed);
  - views r5/task_0 91e563d6… and r5/task_1 a4192fa1… (both = r3/r4).
- Base copy byte-identical; blueprint unchanged.
- Inputs this round: the renderer's source scan (`audits/render_source/hardship_assistance_plans/render_r1.md`, items 1–5) and `rework_r5_claims.md`. Both shared objects moved, so every charter section and every tool section is re-derived over all six policies and six tools.
- **Disclosure — what my earlier revisions missed.** The renderer found defects that my revisions 1–4 passed:
  - item 1, the P2 sale-review tier, a rule/compute mismatch present since r1, which I marked as matching in r1;
  - item 2, P6's scheduled-installment and current-rate bindings, an XF 3 member present since r2;
  - item 3, shared look-back sentences, which I judged non-members in r2/r3;
  - item 4, the certification docstring vs the "no plan installment line" end-date branch, present since r3;
  - item 5, the hand-off sentence next to P3's state-form prerequisite, which I recorded only as observations O-14/O-16.
  The round-4 PASS should be read in that light.

### render items, verified with their whole class
- **Item 1 (rule/compute on whole-month counts).** P2's tier now reads "allows sale_review_months installments less the whole calendar months elapsed since the charge-off date". That equals `K('sale_review_months') - months_since_charge_off`, with the stated day-reached convention. CLOSED.
  - Class sweep of every MONTHS and whole-month count in the charter:
    - P1 due dates left ("whole calendar months from the next due date to the maturity date plus one") and tenure;
    - P2 elapsed months;
    - P4 covered due dates and tenure;
    - P5 still-to-come and due dates left;
    - P6 due dates left in baseline and shape, and tenure;
    - every look-back window ("fewer than N whole calendar months separate").
  - Each matches its compute (MONTHS counts a month only when day2 ≥ day1). No member remains.
- **Item 2 (quantities only one factor uses, held outside it).** P6 `scheduled_installment` and `current_rate_monthly` are now bindings of `repayment_shape`, the only reader. CLOSED.
  - Class sweep of every plain binding:
    - P1 `pre_plan_installment` (baseline and cap);
    - P3 `chosen_installments`, `co_*`, `charged_off_balance`, `standard_percent` (baseline percent and fall-through);
    - P4 `latest_line_due`, `covered_due_dates`, `service_lines` (baseline and guard);
    - P5 `plan_installment`, `prev_*`, `step_up`, `next_due` (shared with `covered_line`), `covered_line` (result branch);
    - P6 `loan_principal`, `due_dates_left`, `plan_rate*` (baseline level).
  - Every one is a baseline, assembly or shared quantity. No member remains.
- **Item 3 (shared convention sentences).** P1's and P5's shared look-back sentences are removed. Each windowed factor sentence now carries its own boundary: P1 R5, R9, R10; P2 R4; P3 R10; P5 R10, R11; P6 R10. CLOSED.
  - Class sweep: no sentence outside a factor sentence now serves two or more factors. The P2 and P3 single-other-loan clauses sit inside each factor sentence; P4's month convention is baseline text, and P4's tenure carries its own. No member remains.
- **Item 4 (docstring vs rule branch).** The certification `end_date` is now "the last loan due date the benefit applies to, or the end of military service for a benefit that covers no loan due date", and plan_months notes "0 when it covers none". This matches P4 R9 and R10. CLOSED.
  - Class sweep of all six docstrings against every rule branch:
    - Reduced Payment Plan offer: three plan months; installment ≥ minimum, never 0.00;
    - settlement record: 1 = single payment, never 0;
    - settlement offer: single-payment installment = the whole amount;
    - schedule tool: covered line, graduated line, and the 0.00 line (P5 R8: amount "the plan installment due on that date" covers it);
    - rate-reduction offer: six months, plan rate recorded.
  - No ordering words, no example values, no other tool names. uuid8s are unchanged; imports are erlbench only; every write tool writes in its own body; no body checks a prerequisite. No member remains.
- **Item 5 (sentence naming the clearing action next to a state-form prerequisite).** P3 R3 now reads "Where that Reduced Payment Plan request cannot be offered under its program's rules, the settlement request is handed to the hardship desk together with it instead of being priced in that contact." It states the outcome and names no clearing action. CLOSED.
  - Class sweep of the sentences beside every prerequisite sentence (P3 R1/R2, P5 R3, P6 R1): none names the action that brings the waited-on state about. The depended-on rules (P1 R1, P2 R1, P4 R2, P5 R5) carry only their own triggers and do not restate the dependent's sentence. No member remains.

### full-charter sweeps (r5)
- Verbatim (compute_basis, baseline sentences, policy_source, replaced_by; superseded_clause in base): 0 misses. No factor id is in a tool name.
- XF 1, 2, 4, 6, 9, 10 and 13: no member.
  - XF 1: factors read only their own and plain bindings. P6 `result` reads `repayment_shape`'s evidence bindings only inside the method branch that factor selects; with the factor at baseline (code 0) they are unused.
  - XF 2: assemblies are generic, with order fixed.
  - XF 4: overwrites are disjoint and self-scoped.
- XF 8: edges are stated for absent lines, end dates and charge-off dates; ties are summed; returns are netted. No member.
- XF 12: realism is unchanged from r4; the item 1 rewording keeps the sale-review rationale. No member.
- Checks 6 and 7: the prerequisite graph and sentences are unchanged from r4, apart from P3 R3 (item 5). The four-point test passes on all four edges.

### findings (r5)
Render items 1–5 are CLOSED with their whole classes. No new RED. Observations kept: O-1, O-2, O-4, O-6, O-9, O-15, O-16 (O-16 is now moot: the P3 hand-off no longer names who declines).

## closing_checklist (revision_5)
| check | status |
|---|---|
| per-task files | one per task. The r5 freezes preceded the 02:15:01Z reveal. Old revisions are untouched. Both comparisons are PASS. |
| coverage and scope | all six extended policies are covered. The task scopes {P1, P2, P3} and {P4, P5, P6} are disjoint and include each whole tree. Tools and GT are closed. uuid8s are independent and unchanged. |
| trees | each has 2 prerequisites, 1 value_input edge and 1 owner=user write. Acyclic across the difficulty. |
| factors | 4–6 per computation with ≥ 2 parameter and 1 method. Multi-source and cross-difficulty (loan) factors on seeded rows in each task. Every ladder is stated in the rule with distinct, realistic tiers. Every factor bears weight, and baseline-only ≠ gold for all six computations (DSL-evaluated, equal to GT). |
| gates on final form | 7/7 OK in the r5 snapshot. TRACEABILITY is pre-publication (not run by me, per the brief). |
| render scan items 1–5 | closed with their whole classes. |
| open REDs | none. |

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Written before any round-6 GT read.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 6: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh hardship_assistance_plans 6` (2026-10-17T03:58:03): EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE / **TRACEABILITY all OK** (the documents are published).
- Hashes:
  - charter ad4a104e7909386d1f685a73a2ab8ee77108bfe22238aadaa7384f1232e330bd (changed);
  - tools 746ee48b… (unchanged since r5, so the tool sections carry forward from r5 by reference);
  - views r6/task_0 91e563d6… and r6/task_1 a4192fa1… (both unchanged).
- Base copy byte-identical; blueprint unchanged.
- Inputs: KB-audit source items S1, S3, S4 (`audits/policy_kb/hardship_assistance_plans/0.md` lines 70–71 and `1.md` line 60; I read only those items); S2 was excluded by coordinator decision. Reworker claims: `rework_r6_claims.md`.

### source items, verified with their whole class
- **S1 (a retired clause restated as in force; one quantity described two ways).**
  - P5's offer_terms overwrite now retires only "and the installment is the level payment at that rate over the remaining months;". The rate clause ("sets the plan rate to the lower of the pre-plan rate and the program's plan rate") stays in force.
  - P5's two installment replacements now say one thing:
    - scra replacement: "the installment owed on every covered due date is the plan installment recorded on the benefit when it was applied";
    - offer_terms replacement: "the plan installment recorded when the benefit is applied is the level payment at that rate over the remaining months, and it is the installment owed on every covered due date".
  - This agrees with R4 and with compute (`RND(plan_installment)`, `F('plan_payment_amount')`), and with the seed (295.93 = level payment at 6 % on 7198.28 over 26 due dates). The level payment now describes how the recorded installment was set at application, not a second covered-date installment. CLOSED.
  - Class sweep of all 9 overwrites:
    - P1, P3 ×2, P6 retire a clause and replace it with "set by this rule / worked out below" content;
    - P2 replaces the upper bound;
    - P4 ×2 bring new duration and start content;
    - P5's plan_installments replacement restates the line rule only for out-of-scope plans and covered dates (the XF 4 allowed form).
  - No other quantity has two descriptions: P4's "installment now in force on the benefit's loan" is the loan's scheduled installment, a distinct quantity. No member remains.
- **S3 (authoring terms or unverifiable cross-product claims in rule text).** P2 R5 and P3 R11 now read "because Larkspur lets a borrower hold at most two open personal loans at a time and takes no new loan application while any of the borrower's loans is charged off". This is true against `blueprint/products/loan.yaml` `loan_agg_multi_holding` (`max_per_customer: 2`; "No personal loan of the borrower is in charged_off status"). CLOSED.
  - Class sweep: a regex over all six rules for charter / compute / binding / factor / tier / ladder / baseline finds none. No other rule makes a claim about another product beyond reading its record fields. No member remains.
- **S4 (a cap or bound whose base a replacement sentence could move).**
  - P1 R3 now reads "of the loan's own scheduled installment on the decision date (never of a payment base put in its place)", which is the compute's `pre_plan_installment`.
  - P2 adds "The bounds are the program's own min_settlement_installments and settlement_max_installments, never a starting term put in their place.", which matches the compute MN(P(max), MX(K(min), …)).
  - CLOSED.
  - Class sweep of every cap and floor: P3 `settlement_floor_pct`; P5's share floor 0 and the previous-line cap (larger of plan/pre-plan; no rule replaces either); P6 `plan_rate_floor` and `min_plan_payment_usd` (applied to the final figure). Each is a fixed figure that no replacement sentence reaches. No member remains.
  - Observation O-17: P2 calls `min_settlement_installments` "the program's own", but it is this policy's parameter. The value (2) and the reading are unaffected.

### full-charter sweeps (r6)
- Verbatim (compute_basis, baseline, policy_source, replaced_by; superseded_clause in base): 0 misses. No factor id is in a tool name.
- The compute is unchanged in substance: the DSL evaluation of all six policies equals r5.
- XF 1–14 have no member: assemblies are untouched (S2 stays by decision), docstrings and tools are unchanged, and edges, rounding and realism are as in r5.
- Checks 6 and 7: the prerequisite sentences and graph are unchanged.

### findings (r6)
S1, S3 and S4 are CLOSED with their whole classes. No new RED. Observations: O-1, O-2, O-4, O-6, O-9, O-15, O-17.

## closing_checklist (revision_6)
| check | status |
|---|---|
| per-task files | one per task. The r6 freezes preceded the 04:00:00Z reveal. Old revisions are untouched. Both comparisons are PASS. |
| coverage, scope and uuids | unchanged: disjoint and complete; tools unchanged since r5. |
| trees | 2 prerequisites, 1 value_input edge and 1 user write per task; acyclic. |
| factors | counts and bounds hold. Every factor bears weight, and baseline-only ≠ gold for all six computations (DSL-evaluated, equal to GT). |
| gates on final form | 8/8 OK, traceability included. |
| KB source items | S1, S3, S4 closed with their whole classes. S2 is excluded by coordinator decision. |
| open REDs | none. |

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- Written before any round-7 GT read.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 7: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh hardship_assistance_plans 7` (2026-10-17T20:17:35): all 8 gates OK, TRACEABILITY included.
- **Byte-identity confirmed:** `hardship.extended.yaml` sha256 ad4a104e7909386d… and `task_tools.py` 746ee48bcfece1b5…, equal to r6. Every charter-global and tool section of revision_6 is therefore carried forward by reference on those two hashes; nothing in them can have moved.
- Views changed: r7/task_0 46432268…, r7/task_1 96a89b2e… (seed-only rework for KB items S6, S7, S8).

### cross-product seed verification (S6, S7, S8)
- **Sources.** I checked every seeded loan row of both tasks against:
  - `blueprint/products/loan.yaml`: loan_pricing_and_disbursement, loan_evt_payment_application, loan_evt_late_fee, loan_evt_returned_payment, loan_evt_autopay, loan_agg_multi_holding;
  - the published loan corpus `docs/loan/`: late-fee figuring and its AutoPay-history, first-late, tenure, term-extension and FlexLine shares; returned-fee figuring and its AutoPay, first-return, bank-event and term-extension shares; late_fee_charging_rule ("assessed on the oldest unpaid installment … at most one per installment").
- **S6 (installment at the base rate):** CLOSED.
  - Each scheduled installment equals the level payment of the amount financed over the term at the base rate:
    - 224.85 (7200 / 21.49 % / 48);
    - 207.96 (6000 / 14.99 % / 36);
    - 334.76 (11500 / 17.49 % / 48), the servicemember benefit's pre-plan installment;
    - 286.63 (6000 / 13.49 % / 24).
  - Every interest portion equals principal × rate in force / 365 × days, on a replayed principal history: 21.24 % while AutoPay was on for the Grade E loan, then 21.49 % after the 2025-09-15 cancellation; 14.49 %; 17.24 % then 6 % from 2026-01-20; 12.99 %. The final principal balances match the seed: 3848.45, 1705.93, 4252.08, 3175.56.
  - The benefit's recorded installment 294.35 is the 6 % level payment of 7159.76 over 26 due dates. Its 8 lines and 8 plan payments are 294.35, and its balance_at_request 7159.76 equals principal after the 2026-01-15 payment.
  - The APRs recompute exactly from net proceeds (25.11 / 17.90 / 20.39 / 17.65).
  - The amounts past due are 4 × 224.85 = 899.40 and 207.96.
- **S7 (fee rows under the published loan fee figuring):** CLOSED.
  - Each fee row recomputes on its assessment date:
    - RPF 2025-08-14: 15 × 0.9 (23 cleared AutoPay debits in 24 months) × 0.85 (no other return, 11 net installments) = 11.48.
    - LF 2025-08-28 for the 2025-08-12 installment: schedule-A figure 15.00 × 0.95 (23 AutoPay debits) × 0.9 (no late fee, 11 net) × 0.97 (28 months' tenure) = 12.44.
    - RPF 2025-09-15: 15 × 0.9 (22 cleared); other return in 12 months, so no first-return share → 13.50.
    - RPF 2026-08-25: 11 cleared and another return in the window, so no share → 15.00.
    - Grade C loan RPF 2026-10-13: 15 × 0.9 × 0.85 = 11.48.
  - No further late fee: the oldest unpaid installment stayed 2025-08-12, which had its one late fee.
  - Allocations follow interest → fees oldest-first → principal, with no interest on a charged-off loan:
    - 2025-09-12: 139.66 interest (62 days), 11.48 + 12.44 fees, 61.27 principal. Reversed in full on 2025-09-15, fee payments included.
    - 2026-04-20: 11.48 + 12.44 + 6.08.
    - 2026-07-17: 7.42 + 22.58 principal.
    - 2026-08-21: 30.00 principal, re-added by its return.
  - Resulting balances: unpaid fees 15.00 and charged-off balance 3863.45.
- **S8 (AutoPay servicing records):** CLOSED.
  - `loan_autopay_enrolled` records exist on each loan's funding date (2023-04-12, 2024-06-10, 2024-03-15, 2025-10-01), each on an active loan with the verified linked account.
  - `loan_autopay_cancelled` is dated 2025-09-15 with reason consecutive_returns, after the 2025-08-14 and 2025-09-15 AutoPay returns (`autopay_consecutive_returns_to_cancel: 2`). After it the Grade E loan shows autopay_enrolled false and interest at 21.49 %.
- Class sweep: no other cross-product row exists in either seed. Customer, bank and hardship rows are this difficulty's own and are consistent with the charter.

### findings (r7)
S6, S7 and S8 are CLOSED. The charter and tools are unchanged, so no charter RED can have moved. Per-task re-derivations are in `0.md` and `1.md` § revision_7.

## closing_checklist (revision_7)
| check | status |
|---|---|
| per-task files | one per task. The r7 freezes preceded the 20:20:51Z reveal. Old revisions are untouched. Both comparisons are PASS. |
| charter and tools | byte-identical to r6 (ad4a104e7909386d / 746ee48bcfece1b5). The charter-global sections carry forward on those hashes. |
| seeds | every cross-product loan row is what the loan rules and the published loan corpus produce (S6/S7/S8 closed). Every prerequisite is still unmet at the opening, and every edge and factor bears weight. Baseline ≠ gold for all six computations. The recomputed gold equals my independent derivation, and the proof text carries no stale figure. |
| gates | 8/8 OK (traceability included). |
| open REDs | none. |

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
