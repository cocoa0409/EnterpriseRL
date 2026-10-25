# worklog — hardship_assistance_plans (env_0067, category `hardship`, M=2)

## Step 0 — difficulty pre-check

Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/hardship.yaml,
db_schema.json, share_tools.py, products/loan.yaml (fee schedule, charge-off, payment application, AutoPay),
products/protection.yaml (parameters), audits/render_source/XF_recipe.md.

Draw (`draw_counts.py <diff> --tasks 2`):
```
{"task": 0, "prerequisite_problems": 2, "problems": 3, "factor_counts": [6, 6, 4]}
{"task": 1, "prerequisite_problems": 2, "problems": 3, "factor_counts": [4, 5, 5]}
```

### Base constraints found (they shape every claim)
1. Writable hardship events. Base events whose `triggers` fire into another category with no `when`
   (hardship_benefit_applied, hardship_plan_accepted, hardship_plan_completed, hardship_plan_broken,
   hardship_plan_cancelled -> loan:loan_terms_modified; hardship_installment_deferred ->
   loan:loan_payment_schedule_updated) may not be written by any task tool (Principle D: "not even through
   the event model"). Writable: hardship_plan_requested, hardship_plan_offered, hardship_plan_declined,
   hardship_offer_expired, hardship_plan_end_date_set, hardship_document_received,
   hardship_plan_installment_scheduled, hardship_plan_payment_credited.
2. Numbers. Of the writable events only hardship_plan_offered (plan terms),
   hardship_plan_end_date_set (plan_months), hardship_plan_installment_scheduled (amount) and
   hardship_plan_payment_credited (amount) carry a number a policy can compute.
3. The borrower's own writes in the base lifecycle are acceptance, turning an offer down and leaving a plan
   — all trigger loan:loan_terms_modified (item 1) and carry no number. The only numeric write the base itself
   leaves to the borrower is hardship_plan_end_date_set ("recorded on the plan as its end date once the
   borrower provides it", hardship_scra_benefit). Route-around (coordinator: existing fields, declared
   overwrite, change what the task tests): the two `owner=user` tools both write hardship_plan_end_date_set's
   existing `plan_months` field — task 1 for its base purpose (the servicemember reports the end of service),
   task 0 for the borrower's own choice of settlement term on a pending request (the base offer rule already
   makes that the borrower's choice: "the borrower chooses one").
4. Gates. check_compute's cross-category floor needs every computation's target holding in initial_state;
   the DSL cannot read a second hardship plan (CFIELD('hardship',..) fails check_extended), so a
   `value_input` edge must join two writes on the same plan. A requested plan accepts at most two computed
   writes (end_date_set, offered); a third problem therefore sits on the borrower's other loan and joins the
   tree by a `state_gate` edge.
5. Every offered write inherits hardship_settlement.days_since_charge_off (subject hardship_plan_offered,
   action_bindings loans.loan_id -> loan_id), so offer tools carry `loan_id`.
6. Small integers composed by MN of caps leave only one cap binding -> every computation composes its factors
   additively/multiplicatively so each factor moves the result on its own.

### Global constraints
- M=2 scopes pairwise disjoint; 6 extended policies, 6 task tools, every policy fired in exactly one task.
- Remaining headroom after task 0: SCRA (end_date_set), plan installments/credits on active plans, TRR/TEM
  offers — task 1 claims SCRA service end + SCRA plan installment + Term Extension Modification offer.

## Task 0 — dossier (copied into tasks/0.json design_rationale)

TASK 0 — settling a charged-off loan for a laid-off borrower who also has a pending payment-reduction request on her other loan (frozen 2026-10-16 10:20 EDT).

1. WHY IT IS A GOOD TEST. The customer asks one thing: settle her charged-off Grade E loan, spread over as many monthly payments as allowed. Gold needs three writes discovered from policy, not from the customer: (a) the overdue decision on her Reduced Payment Plan request on the other (active Grade C) loan, because the settlement rule says "The settlement amount is not fixed until no Reduced Payment Plan request on the borrower's other Larkspur loan still stands in requested status."; (b) her own record of the installment term on the settlement request, because "The settlement amount is worked out only after the request records, as its plan months, the number of monthly installments the borrower has chosen."; (c) the settlement offer. Each write carries its own multi-factor figure (6 / 4 / 6 factors), reconciled from two loan ledgers (84 loan_transactions rows), document lines and the other loan's standing. Difficulty is reading policy, querying and calculating; there is one tool per problem and no near-synonym tool.

2. SCOPE. Draw (draw_counts --task 0): prerequisite_problems 2, factor_counts [6, 6, 4] -> hardship_ext_rpp_offer_payment 6, hardship_ext_settlement_offer_amount 6, hardship_ext_settlement_installment_term 4. Claimed: Reduced Payment Plan offer terms (state_due), settlement term record (user), settlement offer amount (on_request); tools offer_reduced_payment_plan_00434f76, record_settlement_installments_ebffb995 (owner=user), offer_charged_off_settlement_3f4a16ef. Left for task 1: Servicemember Rate Cap Benefit (end of service record, plan installment lines) and the Term Extension Modification offer; nothing reserved idle.

3. PROBLEM-TREE CARD. Root hardship_ext_settlement_offer_amount. Edge 1 -> hardship_ext_settlement_installment_term: kind value_input, gate chosen_installments, form state, sentence above (affirmative direction, connective "only after"); condition: the settlement request carries plan_months >= 1 recorded by the borrower; resolved by record_settlement_installments_ebffb995 (owner user). Opening evidence: initial_state.hardship_plans.<P1>.plan_months = '' (empty). Exactly one write of this difficulty records plan months on a settlement request (the servicemember end-of-service record writes plan months only on a Servicemember Rate Cap Benefit). Edge 2 -> hardship_ext_rpp_offer_payment: kind state_gate, gate hardship_plans.status, form state, sentence above (negated direction, connective "not ... until"); condition: no Reduced Payment Plan request of the borrower on another loan in requested status; resolved by offer_reduced_payment_plan_00434f76 (owner agent). Opening evidence: initial_state.hardship_plans.<P2>.status = requested, variant Reduced Payment Plan, loan <L2>. Exactly one write of this difficulty moves a Reduced Payment Plan request out of requested status (the Term Extension Modification offer decides only Term Extension requests; declining is not a task tool). Derivation: sentence + find_hardship_plans (P2 requested) + the Reduced Payment Plan rule ("the decision is owed whether or not the borrower calls"; the offer records the request as offered) -> the Reduced Payment Plan offer; sentence + P1.plan_months empty + the settlement-term rule ("A borrower settling a charged-off loan records on the pending request, as its plan months, the number of monthly installments chosen") -> the borrower's own record. Topological order: [rpp offer, settlement term] -> settlement offer. The two prerequisites write different plans and neither computation reads the other's plan; swapping them gives the same terminal hash aa3fee2fc94b3073 and the term recomputes to 3. Deletion sensitivity: without the term record the settlement recomputes to 1184.78 (single-payment price 55, floor 30) instead of 1421.73; without the RPP offer, P2 stays requested (status, decision_date, plan_payment_amount 90.86, start/end dates differ in the terminal state). value_input edges: 1 >= max(2-1,1). user_scenario names neither prerequisite (the other loan appears only in a conditional reaction); every task tool body is one unconditional ctx.update with no status check, so nothing blocks.

4. BASE-INVARIANT CARD. Offer writes (subject hardship_plan_offered) inherit hardship_agg_relief_limits, hardship_evt_documents_and_decision, hardship_evt_offer_terms (no gate on this subject: policy_scope) and hardship_settlement.days_since_charge_off (time gate; anchor loans.charged_off_date, relation not_before, duration variants.min_days_since_charge_off, calendar days from the day after the charge-off date, boundary inclusive). Settlement: charged off 2025-12-10, minimum 30 days -> 2026-01-08 (29 days) fails, 2026-01-09 (30) passes, 2026-10-16 = 310 days. RPP: min_days_since_charge_off 0, no charge-off date -> holds on any date. The term record (subject hardship_plan_end_date_set) inherits hardship_scra_benefit, whose gates apply only to hardship_benefit_applied: policy_scope. Request-time gates (one open plan per loan, program usage, status, seasoning) were satisfied when each request was taken: P1 on a charged_off loan with 307 days since charge-off and balance 3949.26 >= 300; P2 on an active loan funded 2024-06-10 (>= 3 months), 27 installments paid (>= 3), 0 days past due on 2026-10-08 (<= 89), principal 1752.17 (>= 500), job_loss qualifying, termination notice on file 2026-10-09 (inside 14 days). RPP decision window: 3 business days after the document -> 2026-10-13, 10-14, 10-15 (10-12 Columbus Day is a Federal Reserve holiday) -> overdue on 2026-10-16 (state_due).

5. BUSINESS-OBJECT CARD. Settlement object: hardship plan P1 on loan L1; charged-off balance = loans.principal_balance 3904.26 + loans.fees_balance 45.00. Fees: returned-payment fees 2025-08-14 and 2025-09-15, late fees 2025-08-28/09-28/10-28/11-28 (15.00 each, OH schedule_a: 5% of 223.88 = 11.19 raised to the 15.00 minimum), returned-payment fee 2026-08-25; payments 2026-04-20 and 2026-07-17 (30.00 each) paid the four oldest fees (loan_fee_paid lines, related_txn_id = fee, source_txn_id = payment); the 2026-08-21 payment paid the 10-28 and 11-28 late fees and was returned 2026-08-25, its two fee payments reversed -> unpaid 45.00. Excluded from the balance: the 2025 returned AutoPay debits (reversed), interest (stops at charge-off). RPP object: plan P2 on loan L2; the 2026-10-10 AutoPay debit (206.50) posted and was returned R01 on 2026-10-13 -> amount_past_due 206.50, fee 15.00 (not part of the installment base). Tool writes carry the plan id and the loan id.

6. FACTOR CARD (tier taken / evidence / baseline figure from the sensitivity run).
RPP offer (result 90.86; all-baseline 103.25): arrears_base (method) past-due tier, base 206.50 + 206.50/3 = 275.33 vs scheduled installment -> 68.14 [near-miss: the 2026-10-10 posted debit looks paid until its return row is read]; documented_hardship (parameter, multi-source) job_loss AND termination notice -> 40 vs 50 -> 118.39; loan_tenure 27 months -> 2 -> 96.37; rate_grade Grade C -> 1 -> 93.61; second_loan_standing charged-off Grade E loan -> 3 -> 99.12; autopay_record (multi-source) AutoPay on AND one returned AutoPay debit in six months -> 1 -> 93.61. 40-2-1-3-1 = 33%; 275.3333 x 0.33 = 90.86.
Settlement term (result 3; all-baseline 6): balance_term (method) 3949.26 < 6000 -> floor(3949.26/750) = 5 vs 6 -> 4; bounced_payment_cut (multi-source) return 2026-08-25 AND no later payment -> 2 -> 5 [near-miss: the 2026-08-21 payment is a posted payment but precedes the return]; active_loan_arrears L2 past due 6 days -> 1 -> 4; hardship_kind_extension (multi-source) job_loss AND termination notice 2026-10-13 -> +1 -> 2. MN(6, MX(2, 5-2-1+1)) = 3.
Settlement amount (result 1421.73; all-baseline 2764.48): term_pricing (method) linear 55 + 3x2 = 61 vs two-step 70 -> 1777.17; charge_off_age 310 days -> 10 -> 1816.66; good_faith_payments (multi-source) 3 payments, 1 returned -> 3 -> 1540.21 [near-miss: counting all three as standing would give the clean tier 6]; relationship_standing L2 past due 6 days -> 2 -> 1500.72 [near-miss: L2 shows AutoPay on and a posted 10-10 debit]; documented_severity job_loss AND notice -> 5 -> 1619.20; predefault_history 29 posted - 2 returned = 27 -> 5 -> 1619.20. 61-10-3-2-5-5 = 36% (floor 30 not binding); 3949.26 x 0.36 = 1421.73.
Cross-difficulty factors read the loan category (another difficulty's product): rate_grade, second_loan_standing, autopay_record, loan_tenure, arrears_base, balance_term, active_loan_arrears, term_pricing, charge_off_age, good_faith_payments, relationship_standing, predefault_history. Multi-source: documented_hardship, autopay_record, bounced_payment_cut, hardship_kind_extension, good_faith_payments, documented_severity. No outcome stamp exists; plan fields read are the reported reason and the recorded term.

7. WORLD ROWS. customers (1), bank_accounts (1: Huntington checking 2593, verified — the AutoPay account; the R01 return does not close it), loans (2), loan_transactions (84: L1 disbursement 2, 27 AutoPay installments, 2 returned debits + returns, 7 fees, 3 post-charge-off payments, 6 fee payments, 1 return, 2 fee-payment reversals; L2 disbursement 2, 27 installments, the 10-10 debit, its return and fee), hardship_plans (2), hardship_plan_events (2 termination notices). Removing the 10-13 return flips arrears_base, autopay_record, relationship_standing and active_loan_arrears; removing the 08-25 return flips the bounced and good-faith tiers; removing either notice drops the documented tiers. Automatic clauses checked: no late fee on the charged-off loan after charge-off (late fees only on active loans); L2's 10-10 installment is inside its 15-day grace (late fee not yet due until 2026-10-26); AutoPay cancellation needs 2 consecutive returns (only one on L2); no acceptance/expiry is due (no offer exists yet).

8. PERSONA. Monica R. Hollister, plain-spoken, laid off in September. Volunteers: settle the old loan, as many monthly payments as allowed, nothing paid today. Given on request: mobile 6145552471 (locator), date of birth 1983-05-27 and ZIP 43207 (3 credentials), email/SSN only if more are needed, reason (laid off; layoff letter uploaded with the Tuesday request), lump vs monthly (monthly, as many as allowed). Passive: confirms her own online request for lower payments on the newer loan only if the representative raises it and lets them proceed; records exactly the installment number the representative gives; repeats the settlement figures, says she will read the offer before accepting, ends the call. No number of gold appears in the persona; she never volunteers a prerequisite.

9. STANDARD SOLUTION AND VERIFICATION. Reads: find_customers(phone) -> verify_customer_identity(phone, dob, zip) -> find_loans -> find_bank_accounts -> find_loan_transactions -> find_hardship_plans -> find_hardship_plan_events. Writes: RPP offer (P2, L2, 206.50, 14.49, 1752.17, 9, 2026-11-10, 2027-01-10, 90.86) -> borrower records plan_months 3 on P1 -> settlement offer (P1, L1, 3949.26, 473.91, 1421.73). Verification: /tmp authoring harness replays gold with the real tools and evaluates each compute on the handling-time world: "B 90.86 U 3 R 1421.73 inst 473.91"; factor baselines as in section 6; "R without U: 1184.78", "R without B: 1421.73"; order swap hashes equal. Probes on scratch copies: no other active loan -> term 4 / amount 1263.76; other loan current -> term 4; other loan 36 days back -> term 2; payment on the day of the return -> term 3 (tie stated in the rule); payment after the return -> 4; single payment -> 1184.78; balance 900 -> amount 283.50, term 2; additional principal 600 -> re-amortized base 76.26, zero rate 72.28; other loan settled -> 96.37; AutoPay off -> 93.61.

10. RULE <-> COMPUTE SWEEP. Forward: every binding of the three policies quotes a sentence that is verbatim in its rule (scratch sweep: 0 misses). Reverse: each policy's rule sentences are claimed — RPP: scope/overwrite sentence (policy header), decision-owed sentence (trigger, no binding), baseline 2 sentences (pre_plan_installment, result), payment base (loan_past_due, extra_principal_12m, loan_principal, loan_rate_monthly, due_dates_left, payment_base), documented percentage (termination_notices, income_statements, hardship_percent), tenure (tenure_months with the month-completion convention, tenure_points), grade, other-loan, AutoPay ladders, assembly sentence (plan_percent: points subtracted before the percentage is applied once; rounding once on the final figure with the 25.00 floor in result). Settlement term: baseline sentence (result's fall-through 6), starting term (charged-off balance definition, months since charge-off with the charge-off-day convention), returned-payment cut incl. the same-day tie, other-loan cut, extension, assembly ("subtracting every installment cut ... then adding any installment extension ... held between 2 and 6"). Settlement amount: two prerequisite sentences (chosen_installments; status gate carries no binding), choice sentence (chosen_installments), balance (co_principal/co_fees/charged_off_balance), standard percentage (standard_percent), amount and installment sentence (result; the installment is the tool's plan_payment_amount = amount / recorded installments), term pricing, age (DAYS, day-after counting), good faith, relationship, documented hardship, payment history, assembly (settlement_percent with the 30 floor applied after all subtractions). Rounding: RND only on the final amount in both money policies, matching "rounded to the cent once, on the final figure".

11. XF RECIPE (14 points).
(1) Independence — factor bindings read only evidence and plain bindings: RPP arrears_base reads pre_plan_installment (plain) + its own loan reads; documented_hardship reads its document counts; tenure/grade/other-loan/AutoPay read only their own loan reads; settlement term balance_term reads its own CFIELDs; bounced/arrears/extension read their own evidence; settlement amount term_pricing reads chosen_installments and standard_percent (plain) + pricing_balance (own); no factor reads another factor's binding; results assemble only in plan_percent/result, result, settlement_percent/result.
(2) Assembly stated once, generically, with order: "Where another rule of this policy replaces ..., the replacement takes its place; every point that applies is then subtracted ...", "taking the term the balance allows, subtracting every installment cut ..., then adding any installment extension", "the replacement is taken first; every point ... is then subtracted ..., never below settlement_floor_pct".
(3) Factor-only quantities defined in their own sentence: payment base, documented percentage, charged-off balance for the term (moved out of the term baseline), term price; baselines name no factor quantity.
(4) Overwrites: RPP retires the RPP installment sentence of hardship_evt_offer_terms with a self-scoped replacement; the settlement term retires only the fragment "for 2 to settlement_max_installments monthly installments" and the settlement amount only the pricing fragment "Charged-Off Settlement Plan sets the settlement amount at settlement_lump_sum_percent of the charged-off balance for one payment, or settlement_installment_percent" — disjoint fragments, each replaced_by naming its own scope; the settlement amount also retires hardship_settlement's flat-percent choice sentence. Each retires a clause that conflicts on this world (base would give 6 installments / 2764.48 / 103.25). No rule defers to a retired clause.
(5) compute_basis verbatim: scratch sweep 0 misses after every edit.
(6) Rounding sentence matches RND placement (final figure only).
(7) Docstrings: effects match bodies (single ctx.update each); no example values except the schema-mandated rate format "(e.g. 12.49 means 12.49%)", which equals no scored value; no ordering words, no other tool names.
(8) Edge probes: listed in section 9 (absent other loan, current other loan, 30+ days, same-day tie, later payment, single payment, small balance, re-amortization incl. zero rate, settled other loan, AutoPay off); None guards on the other-loan reads, zero-rate guard, MONTHS month-end convention stated in tenure and sale-review sentences, DAYS counting stated, entries counted as payments (not periods), returned payments excluded by explicit return counts.
(9) Method tiers change shape: arrears_base {installment + arrears/3 | annuity on principal | installment}; balance_term {floor(balance/750) | months to sale review | constant 6}; term_pricing {55 + 3(n-1) | constant 55 | step 55/70}. Distinguishing inputs: amount_past_due>0 vs extra principal>=500 vs neither; balance<6000 vs >=6000 & >=18 months vs other; balance>=2000 & n>=2 vs balance<1000 vs other. No two tiers coincide on their domains (the step tier never applies where the linear tier does, n>=2 & balance>=2000).
(10) Factor ids vs tool names: none of arrears_base, documented_hardship, loan_tenure, rate_grade, second_loan_standing, autopay_record, balance_term, bounced_payment_cut, active_loan_arrears, hardship_kind_extension, term_pricing, charge_off_age, good_faith_payments, relationship_standing, documented_severity, predefault_history is a substring of a tool name.
(11) No cross-record date pairing is computed (the other loan's past-due test uses that loan's own fields).
(12) Realism: settlement pricing by term, age, good-faith payments, hardship evidence, relationship and pre-default history is ordinary recovery practice; payment-reduction terms by documented hardship, arrears, tenure, grade, other-account distress and AutoPay are company schedules; seeded loan rows are states the loan charter produces (charge-off at 120 DPD, OH schedule_a fees, AutoPay cancelled after two consecutive returns, fees paid oldest-first, reversals on return); no fee on unbilled interest, no fee after charge-off other than the base's returned-payment fee.
(13) frozen_time '2026-10-16 10:20:00 EDT'; task_tools.py imports only erlbench; every write tool calls ctx.update in its own body; no date maths in tools.
(14) Proof sweep: this dossier, the closure, necessity texts and tracing were regenerated from the verification output after the RPP plan months were corrected to 3 (end date 2027-01-10, base 275.33, 90.86) and after the bank-account read moved the call steps to 8/10/12.

12. REACHABILITY AND CLOSURE. Turn by turn: phone -> profile; three credentials -> verified; loans, bank account, ledgers, plans, documents read; the agent explains the pending RPP request must be decided first, the borrower agrees; the RPP offer is written (state_due); the agent states the longest term (3) and hands over the record tool, the borrower records 3 (her own write, return enters the transcript); the settlement offer is written and its figures told. Everything happens at one frozen time; nothing waits for a payment, document or review. Policy -> tool -> computation -> GT -> terminal: hardship_ext_rpp_offer_payment -> offer_reduced_payment_plan_00434f76 -> step 8 plan_payment_amount 90.86 -> P2 offered; hardship_ext_settlement_installment_term -> record_settlement_installments_ebffb995 -> step 10 plan_months 3 -> P1.plan_months 3; hardship_ext_settlement_offer_amount -> offer_charged_off_settlement_3f4a16ef -> step 12 settlement_amount 1421.73 -> P1 offered. required_documents = charter_scope order.

13. SOLVABILITY VS GT. Step 8: state_due intent from P2 (status requested, request 2026-10-08, document 2026-10-09); discriminator variant 'Reduced Payment Plan'; base preconditions = relief limits / documents & decision / offer terms (policy_scope) + days_since_charge_off bound to loan_id L2. Step 10: on_request intent 'you want to spread the settlement out over as many monthly payments as Larkspur will allow'; hardship_scra_benefit policy_scope. Step 12: intent 'you want to settle it for less than the full balance'; days_since_charge_off bound to loan_id L1 with the 2026-01-08/2026-01-09 boundary.

14. DRAFT FROM THE VISIBLE CONTEXT. Masking compute/expected: the published settlement rule shows two waits — the recorded installment count (absent on P1) and no RPP request in requested status on the other loan (P2 requested) — so the RPP decision and the borrower's record precede the offer; the RPP rule's ladders on the loan/ledger rows give 33% of 275.33 = 90.86; the term rule gives 5 - 2 - 1 + 1 = 3; the amount rule gives 36% of 3949.26 = 1421.73 with installments of 473.91. The draft agrees with gold.

15. EASILY GOT WRONG. Treating the 10-10 AutoPay debit as paid (misses the 10-13 return): arrears base 206.50 -> 68.14 and relationship tier 5 points. Counting the returned 08-21 payment as standing: clean good-faith tier and no bounced cut. Pricing the settlement off the flat 70%: 2764.48. Offering the settlement first: priced as a single payment (P1 has no term) and the RPP request still pending. Recording a term of 6 (program maximum) or 5 (ignoring cuts).

## Task 1 — Step 0 claim (after task 0 closed)

Occupied by task 0: hardship_ext_rpp_offer_payment, hardship_ext_settlement_installment_term,
hardship_ext_settlement_offer_amount; tools offer_reduced_payment_plan_00434f76,
record_settlement_installments_ebffb995, offer_charged_off_settlement_3f4a16ef.
Draw (`draw_counts.py --task 1`): prerequisite_problems 2, factor_counts [4, 5, 5].
Headroom: the only remaining borrower-owned numeric write is hardship_plan_end_date_set on a Servicemember
Rate Cap Benefit (base: "recorded on the plan as its end date once the borrower provides it"); a value_input
partner must write the same plan (installment line); the only remaining rich offer is Temporary Rate
Reduction / Term Extension. Claim:
- hardship_ext_scra_service_end_months (user, 4 factors): the servicemember records the end of military
  service; plan_months = covered due dates (start anchor for Reserve orders + transition due dates).
- hardship_ext_scra_closing_installment (agent, 5 factors): the plan installment line for the first due date
  after the end of service (transition step-back installment).
- hardship_ext_trr_offer_payment (agent, root, 5 factors): Temporary Rate Reduction Plan offer on the other loan.
Tree: TRR offer <- closing installment (state_gate) <- service end record (value_input).
Known weakness (documented for the audit): the transition program (covered due dates after release and the
step-back installment) is Larkspur's own servicemember courtesy layered on the base benefit; the base gives
no numeric quantity on this plan that varies by customer otherwise.

## Task 1 — dossier (copied into tasks/1.json design_rationale)

TASK 1 — an Army Reserve borrower, just released from active duty, asks for his pending rate-reduction request on his newer loan to be decided (frozen 2026-10-14 11:40 EDT).

1. WHY IT IS A GOOD TEST. The customer asks one thing: decide his Temporary Rate Reduction Plan request on the Grade C loan. The rate-reduction rule says "A Temporary Rate Reduction Plan for a borrower who holds a Servicemember Rate Cap Benefit on another Larkspur loan is not offered until that benefit carries a scheduled plan installment line for the first loan due date after its recorded end of military service." The records show the benefit on his Grade D loan with no recorded end (end_date empty, plan_months 0) and lines only through 2026-09-15. The closing-installment rule says "The closing installment is worked out only after the benefit records its end of military service as its end date together with its plan months." and the service-end rule makes that record the servicemember's own certification. So the agent must (a) hand the borrower the certification (end 2026-09-30, plan months 13), (b) schedule the closing line for 2026-10-15 (293.41), (c) offer the rate reduction (2.74%, 273.42). Each write has its own multi-factor figure (4 / 5 / 5 factors) from the benefit's 16 history lines, two loan ledgers (47 rows) and the documents.

2. SCOPE. Draw (draw_counts --task 1): prerequisite_problems 2, factor_counts [4, 5, 5] -> hardship_ext_scra_service_end_months 4, hardship_ext_scra_closing_installment 5, hardship_ext_trr_offer_payment 5. Tools report_military_service_end_1d04825e (owner=user), schedule_benefit_plan_installment_71e01653, offer_rate_reduction_plan_52a2ad4e. Disjoint from task 0 (settlement, RPP, settlement term). All six extended policies are now claimed; none idle.

3. PROBLEM-TREE CARD. Root hardship_ext_trr_offer_payment. Edge 1 -> hardship_ext_scra_closing_installment: state_gate, gate hardship_plan_events.installment_due_date, form state, negated direction ("is not offered until"); condition: the other loan's benefit has a hardship_plan_installment_scheduled line due on the first due date after its recorded end_date; opening evidence: P1.end_date '' and the latest line due 2026-09-15; resolved by schedule_benefit_plan_installment_71e01653 (agent). Only that policy's write schedules plan installment lines in this difficulty. Edge 2 (closing installment -> hardship_ext_scra_service_end_months): value_input, gate step_share, form state, affirmative direction ("only after"); condition: the benefit carries end_date and plan_months; opening evidence P1.end_date '', P1.plan_months 0; resolved by report_military_service_end_1d04825e (owner user); only that write records an end date and plan months on a servicemember benefit (the settlement-term record writes plan months only on a settlement request). Order E -> S -> T is a chain; no parallel edge. Deletion: without the certification the closing installment recomputes to 274.55 (share 100) and the benefit's end_date/plan_months stay empty; without the closing line no 2026-10-15 line exists in the terminal state (the rate figure itself is 273.42 either way: state_gate). Terminal hash of gold 13ddb3547e660eff. user_scenario mentions military service only in conditional reactions; tool bodies are single unconditional writes.
Why the gate is a business rule: L2 was funded 2025-10-01, before the service start, so while the borrower is recorded as serving the relief for it is the servicemember benefit, not a civilian plan; Larkspur sets civilian terms on the other loan only once the benefit's service end and its last capped-to-original installment are fixed.

4. BASE-INVARIANT CARD. Certification (hardship_plan_end_date_set) is governed by hardship_scra_benefit, whose gates apply only to hardship_benefit_applied: policy_scope. Closing line (hardship_plan_installment_scheduled) inherits hardship_evt_plan_installments.active_plan_only: P1.status = active, bound by hardship_plan_id. Offer (hardship_plan_offered) inherits relief limits / documents & decision / offer terms (policy_scope) and hardship_settlement.days_since_charge_off: Temporary Rate Reduction Plan min_days_since_charge_off is 0 and L2 has no charge-off date, so it holds on any date. Request-time gates for P2 held on 2026-10-09: active loan, funded 12 months earlier (>= 6), 12 installments paid (>= 6), current, principal 3193.51 (>= 1000), reduced_income qualifying, income statements 2026-10-09/10-12 inside 14 days; decision window ends 2026-10-15 (10-12 Columbus Day), so deciding on 2026-10-14 is in time (on_request). The benefit was applied 2026-01-27 from the service start 2026-01-20 on a loan funded 2024-03-15 (pre-service), with orders recorded 2025-12-08 (before application).

5. OVERWRITES. Service end: retires hardship_scra_benefit "The benefit lasts until the end of military service, recorded on the plan as its end date once the borrower provides it;" (replaced: lasts through the end of service and the transition due dates; recorded once the borrower certifies it) and hardship_evt_plan_installments "a Servicemember benefit completes once the recorded end date has passed." (replaced: completes after the last transition due date). Closing installment: retires "For a plan with plan installments, one plan installment line is scheduled on each loan due date from the start date through the end date, for the plan installment amount." with a replacement that keeps that rule for every other plan and adds the closing line for a benefit with a recorded end. Rate reduction: retires the base Temporary Rate Reduction installment sentence with a self-scoped replacement. Base would give 8 plan months, no closing line (original installment 333.26) and 4.99% level installment 273.37 — each differs from gold.

6. FACTOR CARD (tier / evidence / baseline figure).
Service end (13; all-baseline 8): service_length_transition (method) 253 days >= 240 -> 253 // 240 = 1 -> 12; benefit_record_transition (multi-source, cross loan) lines 2367.44 = credits 2367.44 AND 8 plan payments posted, none returned -> +1 -> 12; certification_timing 14 days (<= 30) -> +1 -> 12; advance_notice requested 43 days before the start -> +2 -> 11. 8 + 5 = 13. Near-miss: the 2026-10-02 release-orders line is a military_orders document but notice counts the request date, not documents; the 800.00 additional-principal payment is not a plan payment (probe: a returned additional-principal payment leaves 13).
Closing installment (293.41; all-baseline 333.26): benefit_length_share (multi-source) plan months 13 >= 12 AND 8 service months >= 6 -> 25 vs 100 -> 274.55; step_target (method) 800.00 additional principal on 2026-06-05 -> level installment on 4267.90 at 17.24% over 18 due dates = 270.77 vs recorded pre-plan installment 333.26 -> 299.66; loan_grade_relief Grade D -> 5 -> 292.16; loan_tenure_relief 30 months -> 5 -> 292.16; debit_record_relief (multi-source) AutoPay on, no return -> 5 -> 292.16. Share 10%: 295.93 + (270.773 - 295.93) x 0.10 = 293.41.
Rate reduction (273.42; all-baseline 273.37): documented_rate (multi-source) reduced_income AND two income statements -> 3.99 vs 4.99 -> 276.08 [near-miss: the 2026-10-12 bank statement is not an income statement; with one statement the rate stays 4.99, probe 276.08]; repayment_shape (method) 12 due dates left -> equal principal + one month's interest vs level -> 270.09; rate_tenure 12 months -> 0.50 -> 274.75; rate_autopay (multi-source) 12 AutoPay debits in twelve months, none returned -> 0.25 -> 274.08; rate_grade_relief Grade C -> 0.50 -> 274.75. Rate 2.74; 3193.51/12 + 3193.51 x 2.74/1200 = 273.42.
Cross-difficulty factors (loan category): benefit_record_transition, step_target, the grade/tenure/AutoPay ladders, repayment_shape. Multi-source: benefit_record_transition, benefit_length_share, debit_record_relief, documented_rate, rate_autopay.
Honest note for the audit: the transition due dates and the closing (step-back) installment are Larkspur's own servicemember courtesy layered on the base benefit; the legal core used is the release date as end of service, pre-service obligation, the 6% cap and the recorded installments. The base offers no other customer-varying number on a Servicemember plan.

7. WORLD ROWS. customers 1, bank_accounts 1 (Synovus checking 2368, verified, AutoPay account of both loans), loans 2, loan_transactions 47 (L1: 2 disbursement lines, 22 pre-benefit AutoPay installments at 333.26, 8 AutoPay plan payments at 295.93, the 2026-06-05 800.00 additional-principal payment; L2: 2 disbursement lines, 12 AutoPay installments at 285.22), hardship_plans 2, hardship_plan_events 21 (8 lines, 8 credits, orders 2025-12-08, release orders 2026-10-02, 2 income statements, 1 bank statement). Automatic clauses: no late fee (no installment unpaid; SCRA active), no line due before 2026-10-15 is missing, the benefit cannot complete before an end date is recorded, the TRR request is inside its decision window.

8. PERSONA. Terrence J. Galloway, polite and brief. Volunteers only: new job pays less; asked online last Friday for a lower rate on the newer (auto-repair) loan with two pay statements and a bank statement; wants it decided today; nothing paid, no fee waived, AutoPay unchanged. Locator 7065552184; verification date of birth 1990-02-14 and ZIP 31909; email/SSN only if needed. Conditional: only if asked about military service or the other loan does he explain the Army Reserve mobilization, release on September 30, 2026 and the release orders uploaded October 2; when handed the step he certifies September 30, 2026 and exactly the number of covered due dates the representative gives; he notes the next payment on the other loan; he repeats the rate and payment, says he will review the offer in the app, and ends.

9. VERIFICATION. Authoring harness replays gold with the real tools: "E 13 S 293.41 T 273.42 rate 2.74"; per-factor baselines as in section 6; "S without E: 274.55", "T without S: 273.42". Probes: no captured end -> 11; 121-day service with release 15 days after the last line -> 13; returned additional-principal payment (decoy) -> 13; returned plan payment -> 12; an uncredited line -> 11; notice 10 days -> 12; AutoPay off -> 292.16; no prepayment -> 299.66; plan months 10 -> 287.13; one income statement -> 276.08; 36 due dates left -> level 92.51; 48 left -> interest-only 7.29 raised to the 25.00 minimum; 20 left -> level 163.53; one due date left -> 3200.80 (no division by zero).

10. SWEEP AND XF RECIPE. compute_basis quotes verbatim (scratch sweep 0 misses after every edit). (1) Independence: each factor reads only its own evidence and plain bindings (plan_installment, pre_plan_installment, loan_principal, due_dates_left); assembly only in result/share_applied/plan_rate. (2) Assembly sentences: "the transition due dates from every rule above being summed first and the sum never taken below zero"; "every point that applies is then subtracted from the share, never below zero, and the share so reached is applied once to the difference ... which is added to the plan installment"; "every point ... subtracted from the plan rate, which is never taken below plan_rate_floor percent, and the installment is worked once at the rate so reached". (3) Factor-only quantities (transition due dates, step-back share/target, documented rate, repayment shape) live in their own sentences; baselines name none. (4) Overwrites as in section 5, each self-scoped. (6) Rounding: RND only on the final figure. (7) Docstrings describe only the single write each body makes; no examples beyond the schema rate format; no ordering words. (8) Probes in section 9; None guards for a missing captured end, a missing line, no due dates left; same-day ties do not arise (one line per due date, LATEST over line due dates); whole-month counts use the day-of-month completion rule stated in the tenure sentences. (9) Method shapes: transition {proportional to service days | position test | none}; step target {annuity on principal | equal principal + interest | recorded installment}; repayment {equal principal + interest | interest only | level annuity} — distinguishing inputs: 253 vs 121 vs 20 service days; prepayment vs <=12 left vs neither; <=12 vs >36 vs 13-36 due dates left. (10) No factor id is a substring of a tool name. (12) Seeded rows are states the loan and hardship charters produce (AutoPay plan payments credited same day, capped installment = level payment of the balance at 6% over 26 due dates). (13) frozen_time '2026-10-14 11:40:00 EDT'; tools import only erlbench and write in their own bodies. (14) Proof text regenerated after the evidence fixes (posted plan payments / AutoPay debits now read so the clean tiers rest on seeded rows).

11. SOLUTION AND CLOSURE. Reads: find_customers -> verify -> find_loans -> find_bank_accounts -> find_loan_transactions -> find_hardship_plans -> find_hardship_plan_events. Writes: unlock+hand over certification (P1, 2026-09-30, 13) -> schedule closing line (P1, customer, L1, 2026-10-15, 293.41) -> offer rate reduction (P2, L2, 285.22, 12.99, 3193.51, 12, 2026-11-01, 2027-04-01, 2.74, 273.42). Policy -> tool -> step/arg -> terminal: service end -> report_military_service_end_1d04825e -> 8 plan_months -> P1.end_date/plan_months; closing installment -> schedule_benefit_plan_installment_71e01653 -> 10 amount -> new line; rate reduction -> offer_rate_reduction_plan_52a2ad4e -> 12 plan_payment_amount -> P2 offered. Draft from the visible context: the rate-reduction rule's wait sends the agent to the benefit, whose closing-installment rule waits on the certification; the published ladders on the read rows give 13, 293.41 and 2.74% / 273.42 — equal to gold. Easily got wrong: offering the rate reduction first; counting the bank statement; using the level installment for a 12-due-date loan; scheduling the closing line before the certification (share 100 -> 274.55); using the recorded pre-plan installment despite the prepayment.

## Difficulty closing record
- Union: 6 extended policies, each claimed by exactly one task (task 0: rpp_offer_payment, settlement_installment_term,
  settlement_offer_amount; task 1: scra_service_end_months, scra_closing_installment, trr_offer_payment); 6 task tools,
  pairwise disjoint; every task calls an owner=user tool (record_settlement_installments_ebffb995,
  report_military_service_end_1d04825e).
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (92/92 and 74/74 closure),
  SOLVABILITY OK, COMPUTE OK (suite means branches 64.00, steps 13.00; history_rows_max 18; branches_max 71),
  GROUNDING OK, SCOPE OK; CACHE-DIFF info only; TRACEABILITY misses only the six unlock tool names (expected before the
  KB is published), no other parameter lacks a source.
- Scratch /tmp/hardship_assistance_plans_0067/ (world builders, verification harness, probes) removed after closing.
REWORK round 1: gates 7/7 green

## Rework round 2 (audit audits/policy_task/hardship_assistance_plans/: _difficulty.md, 0.md, 1.md read in full)

### Task 0 / charter changes
- P1 hardship_ext_rpp_offer_payment: second_loan_standing (relief for a charged-off or settled Larkspur loan) removed; replaced by prehardship_record (scheduled-installment payments posted in twelve months, net of returns) [F-11]. Plan payment capped at the program's max_plan_payment_ratio_percent of the scheduled installment, cap in compute and baseline params, rounding sentence updated [F-4]. Additional-principal wording "totaling" and, in round 2 sweep, "less any of them returned" with the returned rows netted in compute [O-5, XF 8 class]. Six-month look-back boundary sentence added (a row dated exactly six months before falls outside). Generic assembly sentence [F-15].
- P2 hardship_ext_settlement_installment_term: generic, order-fixed assembly sentence [F-15]; same-day tie rule stated; look-back boundary sentence; "no charge-off date counts no months" guard; single-other-active-loan sentence citing the loan charter limit.
- P3 hardship_ext_settlement_offer_amount: good-faith and payment-history rules restated to match compute exactly, boundary sentence [F-5, F-6]; generic assembly [F-15]; single-other-active-loan sentence; "no charge-off date counts no days" guard.
- task_tools.py: no "already" in the settlement docstring, no rate example values (local rounding variables), schedule tool states only its own effect [F-9]. TASK TOOL CONTRACT OK after each edit.
- tasks/0.json: computations, tracing, necessity (bank-account read cites the loan charter verified-account AutoPay rule), rationale (no Term Extension wording, no second_loan_standing) and new section 16 probe table [R-0.1..R-0.4]. Gold values unchanged.

### Task 1 redesign
- P4 hardship_ext_scra_service_end_months (4 factors: protection_start P multi-source cross, payment_step_return M cross, service_length_return P, loan_tenure_return P). plan_months = covered due dates from the protection start (orders sent with a pre-service request -> request date; loan funded after the request -> funding date; else service start) + graduated-return due dates. end_date = last graduated-return due date, so base completion holds; old completion overwrite withdrawn; overwrites on scra "lasts until", scra "applies from ... waived." and offer_terms "it runs from ..." declared and self-scoped [F-1, F-2, F-3, F-7 (plan-record ladder removed), R-1.1, R-1.2]. Transition program removed (realism).
- P5 hardship_ext_scra_closing_installment (5 factors: step_schedule M multi-source, autopay_relief, prepayment_relief, grade_relief, remaining_term_relief). First graduated-return installment = plan installment + MX(0, pre-plan - plan) x share; share by equal step / flat half / whole step, line record netted for returned plan payments; relief points only lower the share [F-13, F-12, R-1.4]. Overwrites on plan_installments line amount, scra installment sentence and offer_terms SCRA installment clause.
- P6 hardship_ext_trr_offer_payment: tenure tiers 24 / 12 months (above the 6-month seasoning) [F-10]; AutoPay rule worded as compute, including "enrolled with no debit posted takes none" [F-8]; shape factor decides a code only, instalment assembled in result [F-14]; equal-principal shape replaced by principal part of the scheduled installment plus plan-rate interest [F-12]; generic assembly [F-15, R-1.5]; income-drop source sentence and persona pay figures [R-1.3].
- task_tools.py: certification docstring describes end_date as the last loan due date the benefit applies to.
- tasks/1.json: gold E 14 / 2027-01-15, S 298.92, T 2.99% / 258.61; computations, tracing, objectives, necessity (bank-account read cites the loan charter rule) [R-1.6], solvability request bindings (discriminator now the benefit id), required inputs (pay figures), prerequisite_closure, rationale regenerated; terminal hash 63e628939ded7e08.
- Honest limitation: the graduated return is Larkspur's own phase-in practice layered on the SCRA benefit (declared by overwrite); the base offers no other customer-varying number on a Servicemember plan the borrower could own.

### Round 2 probe table (scratch copies of each policy's step world; verify_lib + probes_t0/t1)

Rule tier per probe is the tier the rule text assigns; every row equals the rule reading.

| policy | probe (decoy / absent / edge / tie / row order) | result |
|---|---|---|
| rpp_offer_payment | gold | 90.86 |
| rpp_offer_payment | decoy: loan rows swapped | 90.86 |
| rpp_offer_payment | decoy: termination notice on the settlement plan only | 103.25 |
| rpp_offer_payment | absent: no document on request | 103.25 |
| rpp_offer_payment | no arrears + additional principal 600 posted in window | 68.19 |
| rpp_offer_payment | decoy: that additional principal returned | 68.14 |
| rpp_offer_payment | no arrears, no prepayment (scheduled installment base) | 68.14 |
| rpp_offer_payment | zero rate + prepayment (principal / due dates) | 64.25 |
| rpp_offer_payment | AutoPay return 2026-10-13 moved to 2026-04-16 (exactly six months) | 88.11 |
| rpp_offer_payment | month-end: funded 2024-10-31 (request 2026-10-08 -> 23 months) | 93.61 |
| settlement_installment_term | gold | 3 |
| settlement_installment_term | decoy: loan rows swapped (other active loan CFIELD) | 3 |
| settlement_installment_term | decoy: other loan paid_off (status filter) | 4 |
| settlement_installment_term | absent: no other active loan | 4 |
| settlement_installment_term | tie: payment posted same day as latest return (2026-08-25) | 3 |
| settlement_installment_term | payment posted day after latest return | 4 |
| settlement_installment_term | absent: no return in six months | 5 |
| settlement_installment_term | row-order swap ledger | 3 |
| settlement_installment_term | None: no charge-off date | 3 |
| settlement_offer_amount | gold | 1421.73 |
| settlement_offer_amount | decoy: loan rows swapped | 1421.73 |
| settlement_offer_amount | absent: plan months empty (chosen installments 1) | 1184.78 |
| settlement_offer_amount | decoy: other loan paid_off | 1500.72 |
| settlement_offer_amount | other loan current (no past due) | 1303.26 |
| settlement_offer_amount | window: return dated exactly six months before decision | 1303.26 |
| settlement_offer_amount | decoy: returned scheduled installments (history net) | 1421.73 |
| settlement_offer_amount | row-order swap ledger + loans | 1421.73 |
| settlement_offer_amount | None: no charge-off date | 1816.66 |
| settlement_offer_amount | term pricing: 6 installments, balance >= 2000 (two-step 70, not linear) | 1777.17 |
| settlement_offer_amount | term pricing: 5 installments (linear 67) | 1658.69 |
| settlement_offer_amount | term pricing: balance 900, 3 installments (flat 55, floor bites) | 270.0 |
| settlement_offer_amount | term pricing: balance 900, single payment (two-step 55, floor bites) | 270.0 |
| scra_service_end_months | gold | 14 |
| scra_service_end_months | decoy: orders row dated request removed (only 2026-10-02 release orders left) -> start tier | 12 |
| scra_service_end_months | tier b: loan funded 2025-12-20 (after request) | 11 |
| scra_service_end_months | decoy: second loan row order swapped (CFIELD by loan_id) | 14 |
| scra_service_end_months | decoy: line on the other plan due 2026-12-01 | 14 |
| scra_service_end_months | tie: second line on the same due date 2026-09-15 | 14 |
| scra_service_end_months | row-order swap of plan events | 14 |
| scra_service_end_months | absent: no plan installment line | 0 |
| scra_service_end_months | None: no captured end of service | 12 |
| scra_service_end_months | zero-division: pre-plan installment 0 | 12 |
| scra_service_end_months | step 7% (flat tier): installment in force 309.93 | 13 |
| scra_service_end_months | month-end: service start 2026-01-31, lines to 09-15 (MONTHS day rule) | 12 |
| scra_service_end_months | duty boundary: release 2027-01-20 (365 days) | 15 |
| scra_closing_installment | gold | 298.92 |
| scra_closing_installment | absent: end_date empty | 328.78 |
| scra_closing_installment | n=2: end_date 2026-11-15 | 310.12 |
| scra_closing_installment | n=0: end_date = latest line 2026-09-15 | 328.78 |
| scra_closing_installment | decoy: a plan payment returned (net credit short) | 329.53 |
| scra_closing_installment | decoy: the 800.00 additional principal returned | 300.41 |
| scra_closing_installment | window: additional principal dated 2025-10-14 (exactly 12 months) | 300.41 |
| scra_closing_installment | decoy: additional principal on the other loan | 300.41 |
| scra_closing_installment | AutoPay off | 300.41 |
| scra_closing_installment | AutoPay debit returned in window (also plan payment) | 329.53 |
| scra_closing_installment | pre-plan below plan installment (step up 0) | 295.93 |
| scra_closing_installment | row-order swap loans + events | 298.92 |
| trr_offer_payment | gold | 258.61 |
| trr_offer_payment | decoy: one income statement (bank statement left) | 261.27 |
| trr_offer_payment | decoy: income statement on the other plan only | 261.27 |
| trr_offer_payment | shape: 24 due dates left (level) | 137.25 |
| trr_offer_payment | shape: 48 due dates left (interest only) | 25.0 |
| trr_offer_payment | edge: next due = maturity (1 due date) | 258.61 |
| trr_offer_payment | edge: maturity before next due (MX 1) | 258.61 |
| trr_offer_payment | AutoPay enrolled, no debit in window | 259.27 |
| trr_offer_payment | AutoPay debit returned in window | 259.01 |
| trr_offer_payment | tenure 24: funded 2024-10-09 | 257.94 |
| trr_offer_payment | month-end: funded 2025-10-31 (11 months) | 259.27 |
| trr_offer_payment | row-order swap loans | 258.61 |

Rule tiers for the absent and edge cases: no plan line -> 'records no plan months at all'; no captured end -> length and tenure ladders 'add none'; pre-plan missing/0 -> 'adds none' (no division); end date empty or equal to the latest line -> 'charges the whole step up'; step up never below zero; no document -> program percentage / plan_rate_percent; no other active loan -> 'loses / earns none'; no charge-off date -> 'counts no months / days'; due dates left at least one; same-day ties: lines on one due date count once, a payment posted the same day as the latest return is not after it; look-backs: a row dated exactly N months before falls outside; returned rows netted wherever the rule says 'less any returned'. Two other active loans cannot coexist with a charged-off loan (loan charter limit and bar), stated in P2/P3, so the status-filtered CFIELD has one candidate; every other CFIELD is keyed by loan_id.

### Round 2 XF recipe re-check (all 14 points, every policy P1..P6)
1. Independence: per policy, each factor's bindings read only raw fields, history/cross reads and plain bindings (plain bindings: P1 pre_plan_installment, plan_percent; P2 none; P3 chosen_installments, co_principal, co_fees, charged_off_balance, standard_percent, settlement_percent; P4 service_lines, protection and tenure reading the funding date through separate bindings; P5 plan_installment, step_up, share_applied; P6 loan_principal, due_dates_left, scheduled_installment, current_rate_monthly, plan_rate, plan_rate_monthly). A script listing every name each factor binding reads found no read of another factor's binding in any policy. No factor binding assembles a result; P6 shape now decides a code only. Checked mechanically from compute.
2. Assembly: one generic, order-fixed "Where another rule of this policy replaces <base quantity> ..." sentence per policy, naming only base quantities.
3. Factor-only quantities defined in their factor sentences; baselines (P1..P6) name no factor quantity; no factor names another.
4. Overwrites: every replaced_by names its scope ("and only for such ..."; "every other program keeps ..."), sibling overwrites on one base policy retire distinct clauses, none retires an unconflicted clause, no rule defers to a retired clause; P4's withdrawn completion overwrite is no longer needed because end_date is the last graduated-return due date.
5. compute_basis verbatim: scratch sweep "bad 0" after every edit (also checks baseline, replaced_by and prerequisite sentences in rule).
6. Rounding: P1 RND on the payment and the cap then MX; P3, P5 RND once on the final figure; P6 RND once then the minimum; P2/P4 integers. Sentences match.
7. Docstrings: no example values, no "already", no ordering words, no other tool names; each states only its own write (TASK TOOL CONTRACT OK).
8. Probes: table above (decoys, absent, None, zero division, date edges, month-end, ties, row order, look-back boundary, exclusions netted).
9. Method tiers (pairwise distinct on reachable domain): P1 arrears carry / re-amortized level / scheduled installment; P2 proportional / sale-review countdown / program maximum; P3 linear (2..5 installments, 58..67) / flat (balance under the flat basis, two or more installments, 55) / two-step (70 or 55), the O-3 point coincidences closed; P4 proportional (>= 2) / flat 1 / none; P5 100/(n+1) (<= 25) / 50 / 100; P6 principal part + plan interest / interest only / level.
10. Factor ids vs tool names: no factor id is a substring of any of the six tool names (checked by script).
11. No cross-record date pairing in any rule.
12. Realism: struck factors replaced (P1 pre-hardship payment record; P4 SCRA protection from receipt of orders, 50 U.S.C. 3917, plus a declared phase-in; P5 relief only lowers; P6 interest-saving shape, tenure above seasoning); seeded rows are states the loan and hardship charters produce.
13. Runtime: frozen_time "YYYY-MM-DD HH:MM:SS TZ" in both tasks; task_tools.py imports no datetime/time/random/uuid/secrets; each write tool calls ctx.create/update in its own body.
14. Proof text swept in both tasks (design_rationale, prerequisite_closure, necessity, objectives, tracing, solvability effects) with a stale-token scan (old gold figures, transition/closing/step-back wording, old hash) returning none outside policy ids.

### Round 2 observations
- O-1 kept: both cross-loan holds rest on business reasons stated in their prerequisite sentences. O-2 kept: the base sentence grounds no edge. O-3 closed (term pricing, above). O-4 kept: grade relief runs toward the riskier grades because they carry the higher rates and installments a hardship bears hardest, and every grade tier lowers the payment. O-5 closed (additional principal totals net of returns in P1 and P5). O-6 kept: no other charter event records a borrower's installment choice on a request. O-7 closed (look-back boundary sentences in P1, P2, P5, P6; P3 already had one).
- rework_r2_claims.md written: one line per audit item id, no figures.

### Round 2 closing record
- Full gate block from the repository root, no --task: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 13 acts, closure 92/92; 1.json 13 acts, closure 74/74); SOLVABILITY OK; COMPUTE OK (suite means branches 71.00, steps 13.00; history_rows_max 27; branches_max 76); GROUNDING OK; SCOPE OK.
- Scratch /tmp/hardship_assistance_plans_0067/ (authoring scripts, verification harness, probe scripts) and the difficulty __pycache__ removed.
REWORK round 2: gates 7/7 green


## Rework round 3 (audit _difficulty.md, 0.md, 1.md read in full; open items N-1..N-5)

### Changes
- N-1 (P1): the payment-record rule and its ladder name scheduled-installment payments, matching the compute filter; class swept over every policy: P3 history (scheduled-installment, matches), P3 good-faith and P2 returned-payment cut (all payments, no filter, match), P5/P6 AutoPay (AutoPay debits = autopay_ach channel, match), P4/P5 plan record (hardship_plan_payment, "plan payments", match), P1/P5 prepayment (additional_principal net of returns, match).
- N-2 (P5): every graduated-return line is defined: the line on a graduated-return due date is the previous line's amount (latest due date already carrying a line; first recorded on a tie; the plan installment where none) plus a share of the step up from it to the pre-plan installment; the step schedule reads the due dates still to come from the loan's next due date to the recorded end date. Later lines probed.
- N-3 (P6, class: every hold): the hold is scoped by opening-record facts (the other loan carries an active benefit with the end of military service captured) and waits on a line for that loan's next due date; both are decidable at the opening and false there, true after the graduated-return write. Other holds: P3's two sentences read opening-visible states (no requested RPP on the other loan; recorded plan months), P5's reads the recorded end date and plan months — all decidable at the opening.
- N-4 (P4): the protection-start ladder and its overwrite of the base start are withdrawn; covered due dates count from the military service start date, matching benefit_effective_basis "military service start date (retroactive)" and the start_date field. Replaced by plan_record_return (clean / restored / none, seeded on posted plan payments). Seed re-worlded: the 2026-02-15 plan payment's interest is split at the 2026-01-20 service start (17.24% for 5 days, 6.00% after), later portions and the loan's principal recomputed; no due date fell between the service start and the application, so no interest credit is owed and no in-force rule owes an action without a tool. O-11 closed with it: covered due dates include due dates after the latest line and on or before the end of service; O-10 closed: a benefit with no graduated-return due date records its last covered due date as end date.
- N-5 (XF 3): P2's charge-off-date guard moved into the starting-term sentence and its six-month boundary into the returned-payment cut sentence; P3's guard into the charge-off age sentence; P2/P3 single-loan statement into the other-loan sentences; P5's due dates still to come defined inside "Step schedule:". Shared conventions stay separate (P1 look-back, three factors; P5 twelve-month look-back, two factors).
- Zero amounts stated in every write policy: P1 never below its minimum; P2 never below min_settlement_installments; P3 never 0.00 (program minimum balance and floor percentage); P4 0 plan months only with no line, recording the end of service as end date; P5 a 0.00 line is still scheduled (so P6's hold is met by it); P6 never below its minimum.
- Task 1 gold: end date 2027-03-15 (plan months 14), line 296.78 due 2026-10-15, offer 2.99% / 258.61; computations, tracing, objectives, necessity, solvability effects, prerequisite closure and rationale regenerated; terminal hash 433d9aa7f3dd0e8f. Task 0 gold unchanged; dossier section 17 added.

### Round 3 probe table

| policy | probe | result |
|---|---|---|
| rpp_offer_payment | gold | 90.86 |
| rpp_offer_payment | decoy: loan rows swapped | 90.86 |
| rpp_offer_payment | decoy: termination notice on the settlement plan only | 103.25 |
| rpp_offer_payment | absent: no document on request | 103.25 |
| rpp_offer_payment | no arrears + 600 additional principal in window | 68.19 |
| rpp_offer_payment | decoy: that additional principal returned | 68.14 |
| rpp_offer_payment | decoy: a partial-installment payment in the window (not a scheduled installment) | 90.86 |
| rpp_offer_payment | no arrears, no prepayment | 68.14 |
| rpp_offer_payment | zero rate + prepayment | 64.25 |
| rpp_offer_payment | AutoPay return moved to exactly six months before | 88.11 |
| rpp_offer_payment | month-end: funded 2024-10-31 | 93.61 |
| settlement_installment_term | gold | 3 |
| settlement_installment_term | decoy: loan rows swapped | 3 |
| settlement_installment_term | decoy: other loan paid_off | 4 |
| settlement_installment_term | absent: no other loan | 4 |
| settlement_installment_term | tie: payment posted same day as latest return | 3 |
| settlement_installment_term | payment posted day after latest return | 4 |
| settlement_installment_term | absent: no return in six months | 5 |
| settlement_installment_term | window: return dated exactly six months before | 5 |
| settlement_installment_term | row order: ledger reversed | 3 |
| settlement_installment_term | None: no charge-off date | 3 |
| settlement_offer_amount | gold | 1421.73 |
| settlement_offer_amount | decoy: loan rows swapped | 1421.73 |
| settlement_offer_amount | absent: plan months empty (one payment) | 1184.78 |
| settlement_offer_amount | decoy: other loan paid_off | 1500.72 |
| settlement_offer_amount | other loan current | 1303.26 |
| settlement_offer_amount | window: return exactly six months before | 1303.26 |
| settlement_offer_amount | term pricing: 6 installments (two-step) | 1777.17 |
| settlement_offer_amount | term pricing: 5 installments (linear) | 1658.69 |
| settlement_offer_amount | row order: ledger + loans reversed | 1421.73 |
| settlement_offer_amount | None: no charge-off date | 1816.66 |
| scra_service_end_months | gold | 14 |
| scra_service_end_months | decoy: a plan payment returned, not made good (credit short) | 12 |
| scra_service_end_months | a plan payment returned and made good (restored tier) | 13 |
| scra_service_end_months | decoy: plan payment returned on the other loan | 14 |
| scra_service_end_months | decoy: line on the other plan due later | 14 |
| scra_service_end_months | tie: second line on 2026-09-15 | 14 |
| scra_service_end_months | row order: events and loans reversed | 14 |
| scra_service_end_months | lag: 09-15 line missing, end of service 2026-09-30 | 14 |
| scra_service_end_months | month-end: end of service 2026-09-15 (due date on the end day counts covered) | 14 |
| scra_service_end_months | absent: no plan installment line (0) | 0 |
| scra_service_end_months | None: no captured end of service | 12 |
| scra_service_end_months | zero-division: pre-plan installment 0 | 12 |
| scra_service_end_months | step 7% (flat tier) | 13 |
| scra_service_end_months | duty 365 days | 19 |
| scra_closing_installment | gold | 296.78 |
| scra_closing_installment | absent: end date empty | 328.78 |
| scra_closing_installment | end date before the next due date (none to come) | 328.78 |
| scra_closing_installment | two to come: end date 2026-11-15 (flat 50) | 310.12 |
| scra_closing_installment | later line: 2026-10-15 line 296.78 credited, next due 2026-11-15 | 298.48 |
| scra_closing_installment | tie: second 2026-09-15 line 100.00 recorded later (first recorded kept) | 328.78 |
| scra_closing_installment | tie: a 100.00 line on 2026-09-15 recorded before the 295.93 one | 305.27 |
| scra_closing_installment | decoy: plan payment returned (line record short) | 329.53 |
| scra_closing_installment | decoy: the 800.00 additional principal returned | 298.28 |
| scra_closing_installment | window: prepayment dated exactly twelve months before | 298.28 |
| scra_closing_installment | decoy: prepayment on the other loan | 298.28 |
| scra_closing_installment | AutoPay off | 298.28 |
| scra_closing_installment | pre-plan below previous line (step up 0) | 295.93 |
| scra_closing_installment | zero: plan and pre-plan installments 0 (line 0.00) | 0.0 |
| scra_closing_installment | row order reversed | 296.78 |
| trr_offer_payment | gold | 258.61 |
| trr_offer_payment | decoy: one income statement (bank statement left) | 261.27 |
| trr_offer_payment | decoy: income statement on the other plan only | 261.27 |
| trr_offer_payment | shape: 24 due dates left (level) | 137.25 |
| trr_offer_payment | shape: 48 left (interest only, minimum) | 25.0 |
| trr_offer_payment | edge: maturity before next due (at least one due date) | 258.61 |
| trr_offer_payment | AutoPay enrolled, no debit in window | 259.27 |
| trr_offer_payment | AutoPay debit returned in window | 259.01 |
| trr_offer_payment | tenure 24 months | 257.94 |
| trr_offer_payment | month-end: funded 2025-10-31 (11 months) | 259.27 |
| trr_offer_payment | row order: loans reversed | 258.61 |

Rule tier for each absent / edge row: no line -> 0 plan months; no captured end -> length and tenure add none; pre-plan 0 -> no step (no division); end date empty or before the next due date -> whole step up; step up never below zero; 0.00 line still scheduled; no document -> program percentage / plan_rate_percent; no other active loan -> none; no charge-off date -> no months / no days; at least one due date left; ties: lines on one due date count once, the previous line is the one recorded first, a payment on the day of the latest return is not after it; month-end: a due date on the day of the end of service is covered; look-backs exclude a row exactly N months back; returned rows netted wherever the rule says so.

### Round 3 XF recipe re-check (P1..P6)
1. Independence: script lists every name each factor binding reads; no cross-factor read in any policy. Plain bindings: P1 pre_plan_installment, plan_percent; P2 none; P3 chosen_installments, co_principal, co_fees, charged_off_balance, standard_percent, settlement_percent; P4 latest_line_due, covered_due_dates, service_lines; P5 plan_installment, prev_line, prev_amount, step_up, share_applied; P6 loan_principal, due_dates_left, scheduled_installment, current_rate_monthly, plan_rate, plan_rate_monthly.
2. Assembly: one generic order-fixed sentence per policy naming only base quantities (P4 "Every graduated-return due date that applies is added to the covered due dates ...").
3. Factor-only quantities in their own factor sentences (N-5 members moved); baselines name no factor quantity.
4. Overwrites self-scoped; P4 now retires two clauses (scra end, offer_terms run), the base start is followed; P5 three distinct clauses; P6 one; no rule defers to a retired clause; sweep also checks each superseded clause is verbatim in its base policy.
5. compute_basis verbatim: sweep bad 0.
6. Rounding sentences match RND placement (P1 cap then minimum; P3, P5, P6 single outer RND).
7. Docstrings unchanged since round 2 (no examples, no ordering words); TASK TOOL CONTRACT OK.
8. Probe table above.
9. Method tiers: P1 arrears carry / re-amortized / scheduled; P2 proportional / sale-review / maximum; P3 linear / flat / two-step; P4 proportional / flat / none; P5 100/(r+1) / flat 50 / whole; P6 principal part + plan interest / interest only / level; distinguishing inputs in the probes.
10. No factor id is a substring of a tool name (script).
11. No cross-record date pairing.
12. Realism: base SCRA start followed; seed interest split at the service start; graduated return declared as Larkspur practice.
13. frozen_time format and imports unchanged.
14. Proof texts swept in both tasks with a stale-token scan (old end date, old line amount, protection wording, old hash, unscoped payment wording): none left.

### Round 3 closing record
- Full gate block from the repository root, no --task: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json closure 92/92, 1.json 74/74); SOLVABILITY OK; COMPUTE OK (suite means branches 74.00, steps 13.00; history_rows_max 34; branches_max 76); GROUNDING OK; SCOPE OK.
- rework_r3_claims.md written (one line per item id, no figures). Scratch /tmp/hardship_assistance_plans_0067/ and the difficulty __pycache__ removed.
REWORK round 3: gates 7/7 green

## Rework round 4 (audit revision_3 sections of _difficulty.md, 0.md, 1.md read in full; open: M-1; observations O-12..O-14)

### Hold sweep (M-1 class: every hold / wait / prerequisite sentence, every reachable world)
- P6 rate-reduction hold (M-1 member): scope now "an active Servicemember Rate Cap Benefit with the end of military service captured on it and with either no end date recorded on it or an end date recorded on or after that loan's next due date". Worlds: (a) graduated-return due dates exist -> end date after the next due date -> the graduated-return write lifts it (task 1); (b) no graduated-return due date -> the certification records the last covered due date, before the next due date -> the hold no longer binds after that user write; (c) lines lag the end of service -> the next due date is covered -> the same graduated-return policy schedules its line at the plan installment (O-12 closed: covered-line branch now in P5's compute and rule); (d) end of service not yet certified -> the certification is available in the contact. Decision deadline: every lifting write is available in the same contact, so the base decision window is never forced past.
- P3 wait on the other loan's Reduced Payment Plan request (O-14, same class): lifted by the reduced-payment offer whenever the request can be offered; where it cannot, the rule now states the outcome (only the hardship desk's base decline lifts it, so the settlement request is handed to the hardship desk instead of priced in that contact).
- P3 wait on recorded plan months: always produced by the borrower's own settlement-term record in the contact.
- P5 wait on the recorded end date and plan months: scoped to graduated-return installments; covered lines do not wait; the certification is available whenever the end of service is captured, and graduated-return due dates exist only after it.
- P1 decision owed within the decision window: no hold. P5 "owed as soon as that due date is the loan's next due date": a trigger, not a hold.

### Other changes
- O-13 (same-day previous-line ties): the previous line's amount now takes every line on the latest due date together (SUM over that due date), so row order never matters; it is held to no more than the larger of the plan and pre-plan installments so an extra line cannot push a graduated-return line above the pre-plan installment.
- Combination/order sentences unchanged. Scored values unchanged in both tasks (re-verified with sensitivities and all-baseline results).

### Round 4 probes (scratch copies)
| policy | probe | result |
|---|---|---|
| scra_closing_installment | gold | 296.78 |
| scra_closing_installment | covered next due date: end of service 2026-10-20 | 295.93 (plan installment) |
| scra_closing_installment | covered next due date: end of service on the due day 2026-10-15 | 295.93 |
| scra_closing_installment | no end of service captured | 295.93 |
| scra_closing_installment | 2026-09-15 line split 195.93 + 100.00 (taken together) | 296.78 |
| scra_closing_installment | same split, rows reversed | 296.78 |
| scra_closing_installment | extra uncredited 100.00 line on 2026-09-15 (held to pre-plan; record spoilt) | 333.26 |
| scra_closing_installment | same, rows reversed | 333.26 |
| scra_closing_installment | pre-plan below plan installment | 295.93 |
| trr_offer_payment (hold, by rule reading) | no graduated-return due date: end date 2026-09-15 recorded, next due 2026-10-15 | hold no longer binds after certification |
| trr_offer_payment (hold, by rule reading) | task 1 world: no end date at opening; 2027-03-15 after certification | binds; lifted by the 2026-10-15 line |
| all six | gold values, sensitivities, all-baseline results | unchanged |

### Round 4 XF re-check (policies touched: P3, P5, P6)
1. No factor binding reads another factor's binding (script); P5 plain bindings now plan_installment, prev_due, prev_line, prev_amount, step_up, next_due, share_applied, covered_line. 2. Assembly sentences unchanged. 3. New quantities (covered line, previous-line cap) are baseline/scope quantities, not factor quantities; no factor sentence moved. 4. No overwrite changed; sweep checks superseded clauses verbatim in base. 5. Sweep bad 0. 6. Rounding: the covered line is RND of the plan installment, the graduated line one outer RND. 7. Docstrings unchanged. 8. Probes above. 9. Method tiers unchanged. 10. No factor id in a tool name. 11. No cross-record pairing. 12. The P3 outcome sentence is a real desk hand-off for an ineligible pending request. 13. Runtime unchanged. 14. Proof texts swept: task 1 rationale (hold quote, tie probes, XF 8 tie statement, section 12), task 1 prerequisite_closure condition and sentence synced from the charter, task 0 rationale section 18.

### Round 4 closing record
- Full gate block from the repository root, no --task: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (closure 92/92 and 74/74); SOLVABILITY OK; COMPUTE OK (suite means branches 77.00, steps 13.00; history_rows_max 34; branches_max 78); GROUNDING OK; SCOPE OK.
- rework_r4_claims.md written. Scratch /tmp/hardship_assistance_plans_0067/ and the difficulty __pycache__ removed.
REWORK round 4: gates 7/7 green

## Rework round 5 (renderer source scan audits/render_source/hardship_assistance_plans/render_r1.md read in full; 0 docs rendered)

### Items and their classes
- Item 1 (P2 countdown tier, rule vs compute): the tier now reads "allows sale_review_months installments less the whole calendar months elapsed since the charge-off date, so that the term runs out near the account's sale review", with the stated day-of-month completion rule, exactly the compute; ladder method text updated. Class sweep, every whole-month count vs MONTHS(): P1 tenure, P2 months since charge-off, P4 covered due dates and tenure, P5 due dates still to come and remaining term, P6 tenure each already state the convention; the due-dates-left counts that did not (P1 payment base, P6 level baseline and repayment shape) now state "the whole calendar months from the next due date to the maturity date plus one".
- Item 2 (P6 quantities only the repayment shape reads): scheduled_installment and current_rate_monthly are now bindings of repayment_shape. Class sweep (script: every plain binding used by exactly one factor and nothing else): one hit, P3 standard_percent, which is the computation document's standard settlement percentage (the baseline value of term_price, stated in the baseline sentence), so it stays plain.
- Item 3 (shared look-back sentences): P1's "In every look-back ..." and P5's "In every twelve-month look-back ..." are removed; each windowed factor sentence carries its own boundary (P1 payment base, payment record, AutoPay; P5 AutoPay relief, prepayment relief). Class sweep: P2 returned-payment cut, P3 good-faith and P6 AutoPay already carried theirs; no "In every" sentence remains in any policy.
- Item 4 (certification docstring vs the no-plan-line branch): end_date is now "the benefit's end date: the last loan due date the benefit applies to, or the end of military service for a benefit that covers no loan due date", plan_months notes 0 when it covers none. Class sweep of every docstring vs every rule branch: the schedule tool's amount ("the plan installment due on that date") covers covered, graduated and 0.00 lines; the settlement-term tool covers 1 and 2..term; the settlement offer, reduced-payment and rate-reduction offers have no unmatched branch (every amount is held above zero by its rule). TASK TOOL CONTRACT OK.
- Item 5 (sentence after P3's state-form wait): reworded to "Where that Reduced Payment Plan request cannot be offered under its program's rules, the settlement request is handed to the hardship desk together with it instead of being priced in that contact." — the outcome stays, no clearing action is named, and the prerequisite sentence itself is untouched and state-only.

### Probes (scratch copies)
| policy | probe | result |
|---|---|---|
| all six | gold, every factor-baseline sensitivity and the all-baseline result | unchanged |
| settlement_installment_term | balance 7000.00, charged off 2024-03-10, term recorded 2026-10-16 (countdown tier: sale_review_months less 31 months, held at the minimum) | 2 |

### XF re-check (policies touched: P1, P2, P3, P5, P6; tool docstring)
1. No factor binding reads another factor's binding (script). 2. Combination/order sentences untouched. 3. Factor-only quantities: repayment shape now owns its two quantities; script finds no other one-factor plain binding apart from the baseline standard percentage. 4. No overwrite changed. 5. Sweep bad 0 (basis quotes that ended at a sentence end trimmed to the unchanged span). 6. Rounding unchanged. 7. Certification docstring fixed; no examples or ordering words. 8. Window boundaries now in each factor sentence; month counting stated wherever MONTHS() is used. 9-13. Unchanged. 14. Proof text: task 0 dossier sections 9 and 18 corrected and section 19 added; task 1 dossier section 10 plain-binding list corrected and section 13 added.

### Round 5 closing record
- Full gate block from the repository root, no --task: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (closure 92/92 and 74/74); SOLVABILITY OK; COMPUTE OK (suite means branches 77.00, steps 13.00; history_rows_max 34; branches_max 78); GROUNDING OK; SCOPE OK.
- rework_r5_claims.md written. Scratch /tmp/hardship_assistance_plans_0067/ and the difficulty __pycache__ removed.
REWORK round 5: gates 7/7 green

## Rework round 6 (audits/policy_kb/hardship_assistance_plans/0.md, 1.md and audits/runtime_context/hardship_assistance_plans/0.md, 1.md read in full; KB=CLEAN, runtime PASS; source items S1, S3, S4; S2 left unchanged by coordinator decision)

### Items and their classes
- S1 (Servicemember overwrites retire then restate; covered-date installment described two ways): the offer-terms overwrite now retires only the installment clause "and the installment is the level payment at that rate over the remaining months;" and leaves the "lower of" rate clause in force (nothing here changes it); its replacement says the plan installment recorded when the benefit is applied is that level payment and is owed on every covered due date. The scra overwrite's replacement now says the installment owed on every covered due date is the plan installment recorded on the benefit when it was applied, matching the compute's covered-date branch. One description of the covered-date installment throughout. Class sweep of every overwrite: P1, P2, P3 and P6 replacements change content for their own program and restate the base only for other programs; P4's two replacements change the benefit's span; P5's line-amount replacement restates base wording only for other plans and covered dates; no other retired clause is restated unchanged.
- S3 (authoring term and cross-product claim): P2 and P3 now say "because Larkspur lets a borrower hold at most two open personal loans at a time and takes no new loan application while any of the borrower's loans is charged off", true to the loan product's multi-holding limit (applied, approved and active loans counted, two at most) and its application bar on a charged-off loan. Class sweep: no rule text in any policy now uses "charter" or another authoring term; the assembly sentences' "this policy" wording is S2, left as decided.
- S4 (cap read against a replaced base): P1's ceiling now reads "of the loan's own scheduled installment on the decision date (never of a payment base put in its place)", which is what the compute takes (pre_plan_installment). Class sweep of every cap, floor and bound: P2's bounds could be read against the replaced maximum, so a sentence after the assembly sentence now says the bounds are the program's own min_settlement_installments and settlement_max_installments, never a starting term put in their place (assembly sentence itself untouched; the result basis spans both sentences); P3's floor, P5's zero floor and P6's floor and minimum are fixed figures no rule replaces.
- task_tools.py is byte-identical to round 5; hardship.extended.yaml changed (rule text and overwrites only; compute untouched).

### Probes (scratch copies)
| policy | probe | result |
|---|---|---|
| all six | gold, every factor-baseline sensitivity, all-baseline result | unchanged |
| rpp_offer_payment | arrears base with the percentage at 50 and no points | 103.25 (ceiling on the loan's own installment, not 137.67 on the base) |
| settlement_installment_term | balance 30000.00 (program-maximum tier) | 4 (within the program's own bounds) |

### XF re-check (policies touched: P1, P2, P3, P5)
1. Compute untouched; no cross-factor reads. 2. Combination/order sentences unchanged (P2 bound sentence added after it). 3. No factor-only quantity moved. 4. Overwrites: P5 offer-terms overwrite narrowed to the conflicting clause; every replacement names its scope; no retired clause restated unchanged; superseded clauses verbatim in base (sweep). 5. Sweep bad 0. 6. Rounding unchanged. 7. Docstrings unchanged. 8. Probes above. 9-13. Unchanged. 14. Proof text: task 1 dossier section 5 and new section 14; task 0 dossier single-loan sentence and new section 20.

### Round 6 closing record
- Full gate block from the repository root, no --task: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (closure 92/92 and 74/74); SOLVABILITY OK; COMPUTE OK (suite means branches 77.00, steps 13.00; history_rows_max 34; branches_max 78); GROUNDING OK; SCOPE OK.
- rework_r6_claims.md written. Scratch /tmp/hardship_assistance_plans_0067/ and the difficulty __pycache__ removed.
REWORK round 6: gates 7/7 green

## Rework round 7 (seed-only; audits/policy_kb/hardship_assistance_plans/0.md, 1.md and audits/runtime_context/hardship_assistance_plans/0.md, 1.md read in full; loan docs read: pricing_and_disbursement_terms, payment_posting_and_interest, autopay_terms, autopay_enrollment_and_tool, autopay_enrollment_rate_calculation and its three steps, late_fee_assessment_terms, late_fee_amount_calculation and its shares, late_fee_charging_rule_and_tool, returned_payment_terms, returned_payment_fee_amount_calculation and its shares, returned_payment_fee_charging_rule_and_tool, delinquency_and_charge_off, hardship_and_benefit_servicing, rate_grid)
- hardship.extended.yaml (ad4a104e7909386d) and task_tools.py (746ee48bcfece1b5) byte-identical; only the two task files changed.
- No other product's rows besides Personal Loans are seeded in either task (no FlexLine, PracticePay, Credit Builder, card or protection records), so only loan rows were re-priced.

### S6 — installments at the base rate (both tasks, all four loans)
- Installment = level payment on the amount financed at the base rate over the term, rounded half up: task 0 Grade E 224.85, Grade C 207.96; task 1 Grade D 334.76, Grade C 286.63. Interest still accrues at the rate in force (AutoPay-discounted while AutoPay is on, the plan rate under the servicemember benefit), actual/365 from the paid-through date, rounded to the cent; every interest and principal portion, every principal history and every APR (25.11, 17.90, 20.39, 17.65; all under the 35.99 ceiling) re-derived; returns reverse the payment exactly.
- Task 1: the benefit's recorded pre-plan installment 334.76, unpaid principal 7159.76, capped level payment 294.35 (6.00 over 26 due dates), eight lines, eight credits and eight plan payments at 294.35; the 2026-02-15 interest again split at the service start (16.91 + 30.60 = 47.51); Grade D principal 4252.08, Grade C principal 3175.56.
- Task 0: Grade C principal 1705.93 after the reversed 2026-10-10 debit, amount past due 207.96; charged-off loan principal 3871.03 at charge-off, 3848.45 after the post-charge-off principal, amount past due 4 x 224.85 = 899.40.

### S7 — task 0 fee rows under the published fee figuring
- Returned-payment fees: 2025-08-14 11.48 (AutoPay share 0.90 on 23 cleared debits; first-return share 0.85, no other return and 11 net installment payments in the year); 2025-09-15 13.50 (0.90; an earlier return in the year, no first-return share); 2026-08-25 15.00 (11 cleared debits, another return in the year: no share); Grade C 2026-10-13 11.48 (0.90 x 0.85).
- Late fee 2025-08-28 for the 2025-08-12 installment: 5% of 224.85 raised to the 15.00 minimum, x AutoPay-history 0.95 x first-late 0.90 x tenure 0.97 = 12.44.
- Further late fees: settled from late_fee_charging_rule_and_tool and late_fee_assessment_terms — a late fee is assessed on the oldest unpaid installment (the loan's next due date), at most one per installment, and only on an active loan. The next due date stayed 2025-08-12 (the 2025-09-12 debit was returned) until the 2025-12-10 charge-off, so no further late fee could be charged; the 2025-09-28, 10-28 and 11-28 late-fee rows are removed.
- Allocation: the 2025-09-12 AutoPay debit paid interest, the two fees then owed (fee_paid lines) and principal; its 2025-09-15 return reversed all of it (two fee-payment reversal lines). After charge-off (no interest), 2026-04-20 paid 11.48 + 12.44 + 6.08 of the fees oldest first, 2026-07-17 paid the remaining 7.42 and 22.58 of principal, 2026-08-21 went to principal and was returned 2026-08-25. Unpaid fees 15.00; charged-off balance 3863.45.

### S8 — AutoPay servicing records
- loan_servicing_events seeded: an AutoPay enrollment (phone, the verified linked account) on each loan's funding date in both tasks, and on task 0's charged-off loan a system cancellation on 2025-09-15, reason consecutive_returns (two consecutive returned debits). The enrollment rate at funding is the base rate less the grade discount (no debit, loan-age or Credit Builder step at funding), matching each loan's rate. Both golds gained a find_loan_servicing_events read (step 5), so the rows are in the closure; later step numbers moved by one in every proof text.

### Gold, weight and closure after the re-pricing
| task | policy | new gold | baseline-only | factor sensitivities |
|---|---|---|---|---|
| 0 | rpp_offer_payment | 91.50 (base 277.28 x 33%) | 103.98 | 68.63 / 103.98 / 97.05 / 94.28 / 99.82 / 94.28 |
| 0 | settlement_installment_term | 3 | 6 | 4 / 5 / 4 / 2 |
| 0 | settlement_offer_amount | 1390.84 (installment 463.61, balance 3863.45) | 2704.41 | 1738.55 / 1777.19 / 1506.75 / 1468.11 / 1584.01 / 1584.01 |
| 1 | scra_service_end_months | 14, end date 2027-03-15 | 8 | 12 / 12 / 13 / 13 |
| 1 | scra_closing_installment | 295.27 | 334.76 | 329.91 / 296.89 / 296.89 / 296.08 / 296.08 |
| 1 | trr_offer_payment | 260.17 at 2.99% | 271.84 | 262.81 / 268.94 / 260.83 / 260.83 / 261.49 |
- Prerequisites still unmet at the opening (task 0: settlement plan months empty, RPP request requested; task 1: no end date, no line for 2026-10-15); skip effects: task 0 R without U 1159.04; task 1 S without E 329.91. Terminal hashes: task 0 ab08def5647e4e1c (same under the swapped prerequisite order), task 1 53a5a6a2b8d9fe07.

### Probes re-run on the new seed (scratch copies)
- Task 0: notice moved 103.98; 600.00 prepayment 66.39, returned 68.63; no arrears 68.63; zero rate 62.55; return exactly six months 88.73; funded on the 31st 94.28; partial-installment decoy 91.50; ceiling probe 103.98 (not 138.64); U: paid_off 4, none 4, same-day 3, day after 4, no return 5, return exactly six months 5, no charge-off date 3, bounds 4, countdown 2; R: one payment 1159.04, paid_off 1468.11, current 1274.94, return exactly six months 1274.94, 6 installments 1738.55, 5 installments 1622.65, extra returned installment 1390.84, no charge-off date 1777.19, balance 900 270.00 both ways.
- Task 1: two to come 309.71; later line 297.11; returned plan payment 330.72; split line 295.27; extra uncredited line 334.76; covered next due 294.35; 800.00 returned 296.89; pre-plan below 294.35; one income statement 262.81; 24 left 136.48; 48 left 25.00; maturity before next due 260.17; no debit in window 260.83; AutoPay return 260.56; tenure 24 259.51; funded on the 31st 260.83; 7% step 13.
- Proof texts swept in both tasks (computations, tracing, objectives, necessity, solvability effects, prerequisite closure, rationale; stale-figure scan returns none of the old installments, balances, fees or golds).

### Round 7 closing record
- Full gate block from the repository root, no --task, traceability included: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (14 acts each; closure 92/92 and 76/76); SOLVABILITY OK; COMPUTE OK (suite means branches 77.00, steps 14.00; history_rows_max 34; branches_max 78); GROUNDING OK; SCOPE OK; TRACEABILITY OK (0 missing in both tasks).
- hardship.extended.yaml and task_tools.py byte-identical (ad4a104e7909386d, 746ee48bcfece1b5). rework_r7_claims.md written. Scratch /tmp/hardship_assistance_plans_0067/ and the difficulty __pycache__ removed.
REWORK round 7: gates 7/7 green
