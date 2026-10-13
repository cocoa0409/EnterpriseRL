# Policy-task audit — home_delivery_orders_and_billing / charter-global

## charter_global_frozen

- scenario: env/env_0047_pharmacy_benefit_manager; difficulty: home_delivery_orders_and_billing; category: mail; M = 2
- frozen inputs (sha256, verified by the auditor at 2026-10-08 07:14 UTC, equal to the brief):
  - tasks/home_delivery_orders_and_billing/mail.extended.yaml `e11386fcba08ec8747ea5ee09d5e718f2cc3f169ecbd4d5620618667032f78a6`
  - tasks/home_delivery_orders_and_billing/task_tools.py `18aaa7f8faa1728d2ed5595b9c01a155e4e56104ad64765d856a413072ac1fc2`
  - masked views: task_0.view.json `350ad0649e1de6e9017ad82849e4d9cad7e87b0d7e60b2b07b349c7dbf6cc8ed`, task_1.view.json `2499443c505ea991f07618f6fbecbcbb7210f06f759fc9231b64ddf09081a2b8` (hashes verified equal to brief)
- freeze time: 2026-10-08 07:16 UTC (written before any task's GT was revealed); auditor: erl-task-policy-audit (independent of the instantiator)
- read for this section: blueprint/blueprint.yaml, blueprint/db_schema.json, blueprint/share_tools.py (tool list), blueprint/products/mail.yaml, blueprint/products/plan.yaml (plan_design_type only), blueprint/products/retail.yaml (maintenance_choice only), mail.extended.yaml, task_tools.py, erlbench DSL semantics as implemented in skills/erl-task-instantiate/scripts/check_compute.py (`MONTHS`, `DAYS`, `LATEST`, `COUNT(within_months)`, `CFIELD`, `CPARAM`, `XCOUNT`)
- masked / not read: tasks/*.json (all GT fields: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), the instantiator's worklog.md, any other env/ scenario, any sibling difficulty's tasks directory.
- entry conditions (Step 0): gate snapshot supplied in the brief (07:12 UTC): check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred (needs the published KB). Masked views supplied with hashes. Entry conditions complete.

### policy_conflict_scan

Base section: `mail.extended.yaml` lines 1-1005 are textually identical to `blueprint/products/mail.yaml` (`diff` shows only the trailing blank line; a parsed-dict comparison of every top-level key returns SAME). The base copy is verbatim.

Extended policies (7), their write and the edges among them:

| id | trigger | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- | --- |
| mail_ext_expedited_fee_catchup | state_due | mail_shipping_charged | shipping_fee | book_expedited_fee_b4b37c53 (agent) | [] |
| mail_ext_missed_delivery_credit | state_due | mail_credit_issued | amount | credit_missed_delivery_02a65815 (agent) | [] |
| mail_ext_plan_down_payment | on_request | mail_payment_posted | amount | pay_plan_down_payment_b796ac1b (user) | fee_catchup (value_input, state), missed_delivery_credit (value_input, state) |
| mail_ext_installment_terms | on_request | mail_preferences_update | plan_monthly_amount | confirm_payment_plan_4c427b9b (user) | plan_down_payment (value_input, action) |
| mail_ext_dispensing_delay_credit | state_due | mail_credit_issued | amount | credit_dispensing_delay_47b21103 (agent) | [] |
| mail_ext_installment_catchup | state_due | mail_payment_posted | amount | pay_plan_installment_04171a93 (user) | [] |
| mail_ext_past_due_settlement | on_request | mail_payment_posted | amount | pay_past_due_balance_de0abde8 (user) | installment_catchup (state_gate, state), dispensing_delay_credit (value_input, state) |

Overlapping subjects:
- `mail_credit_issued.amount` is computed by two policies (missed_delivery_credit, dispensing_delay_credit). Both supersede the **same** base clause of `mail_shipping` ("it is credited back with reason shipping_fee_waived when the shipment misses its promised delivery because of the pharmacy or carrier") with different `replaced_by` texts, and both tools write a byte-identical record shape (`event_type mail_credit_issued`, `credit_reason shipping_fee_waived`, `source_order_id` = order). Their triggers differ (an order replaced for loss/damage/temperature vs. the most recent expedited shipment dispensed late), and the dispensing-delay trigger is "carries no shipping-fee credit" while the missed-delivery trigger is "no missed-delivery credit is posted for that order". On an order that is at once the latest expedited shipment, dispensed late **and** replaced, both policies would fire and whichever posts first blocks the other at the record level (G-OBS-2). Whether any task world contains such an order is checked per task.
- `mail_payment_posted.amount` is computed by three policies (plan_down_payment, installment_catchup, past_due_settlement) with distinct triggers (on request of a plan / plan installments fallen due / on request to bring current). The down-payment and past-due tools write the identical record shape (`installment_number 0`, `credit_reason not_applicable`); only the installment tool carries a non-zero installment number.
- `mail_preferences_update.plan_monthly_amount`: installment_terms only.
- `mail_shipping_charged.shipping_fee`: expedited_fee_catchup only.

Triggers / eligibility / time anchors: every extended policy evaluates on `frozen_time` (the handling date); no extended policy declares its own `eligibility` list, so base eligibility on the cited base policies is inherited in full. Inherited base gates that bear on extended writes and that the per-task files must check: `mail_payment_plan.plan_threshold` ("A payment plan may be set up only when the balance due is at least payment_plan_min_balance and the months requested do not exceed payment_plan_max_months") on the confirm write; `mail_evt_payment.pay_open_account` (account not closed) on the three payment writes; `mail_shipping.one_fee_per_order` on the fee write; `mail_payment_plan` sentence "While the plan is in good standing and payment_plan_hold_exempt is true, a balance_over_limit hold is released" (a possible extra `mail_release` write if an account is on hold).

Cross-category read boundaries: retail (retail_claims paid, by drug_name and date_of_service; retail_benefits.maintenance_choice of the active benefit), specialty (`balance_due` of the `status=active` enrollment, via `CFIELD`, which returns the first match only), plan (`plan_design_type` parameter of the active plan enrollment's variant via `CPARAM`). `plan_design_type` takes exactly the three values the rule names (hdhp_hsa, deductible_copay, copay_only — blueprint/products/plan.yaml line 32), so the plan-design ladder is closed.

Scope exclusivity / completeness: from the policies alone the `prerequisite` graph has two connected components — {installment_terms → plan_down_payment → {expedited_fee_catchup, missed_delivery_credit}} and {past_due_settlement → {installment_catchup, dispensing_delay_credit}}. The two components share no policy, so two trees rooted at installment_terms and past_due_settlement would be pairwise disjoint and jointly cover all 7 extended policies. (Which task claims which component is only visible in the masked `charter_scope`; it is compared after reveal in each task file.)

### rule_compute_equivalence

Swept binding by binding against `compute_basis` and back against every `rule` sentence. Every binding has a verbatim `compute_basis` quotation; every factor ladder tier is a rule sentence and a branch of its `decides` binding. DSL conventions used below: `COUNT/SUM(within_months=W)` keeps a row iff `0 <= MONTHS(row_date, NOW) < W` with `MONTHS` = whole months (day-of-month borrow), matching the rule's "dated less than W whole months before the handling date"; `LATEST` breaks a same-date tie by keeping the first row encountered (strict `>`).

Policy by policy — matches unless noted:

- expedited_fee_catchup: fee by requested method on the placed row (`mail_order_id = fx_src`) ✓; Saturday surcharge reads the requested method + ship weekday (`DAYS('2021-01-01',d)%7`: 2021-01-01 is a Friday, so 0 = Friday, 6 = Thursday) ✓; remote surcharge reads the **shipped** row's method + account ZIP — the rule says "when the shipment went out overnight", so the asymmetry with the Saturday tier ("asked for") is stated in the rule ✓; window/discount/late share ✓; add → discount → late share → round once ✓.
- missed_delivery_credit: `wv_src` = latest `mail_order_replaced` row regardless of replacement reason; the rule's "worked out on the account's most recent replacement shipment" says the same, while its trigger sentence restricts to replacements for loss/damage/temperature — a pharmacy-error replacement dated after the target would make the two sentences point at different orders (checked per task). Fee booked = SUM of `mail_shipping_charged` on the order ✓; cause/travel shares ✓; fail count excludes pharmacy_error ✓; bridge counts paid retail claims for the replaced drug name in 2 whole months ✓; supply allowance from the shipped row's days_supply ✓; formula ✓.
- plan_down_payment: `dn_ended` = payment_plan requests with `request_status = cancelled` in 24 months — the rule says "ended early because an installment was missed"; the schema's `request_status` enum (submitted, awaiting_member_confirmation, completed, cancelled) carries no cause, so any cancelled payment-plan request is counted (G-OBS-3). `dn_completed` = requests with `request_status = completed` in 48 months — the rule says "payment plans the member completed", while `confirm_payment_plan_4c427b9b` writes `request_status completed` at **confirmation** ("records your confirmed payment plan as a completed payment-plan request"), so a plan still in force is "completed" in the record (G-OBS-3; consequence checked per task). `dn_card_cut` uses `payment_method_on_file != 'none'`; the schema enum is {credit_card, debit_card, hsa_fsa_card, none}, so "!= none" ≡ "a card is on file" ✓. Floor 5 % ✓, single rounding ✓.
- installment_terms: lengthenings ✓ (plan-design ladder closed, see above); cap `MN(…, P('payment_plan_max_months'))` ✓; financed-amount basis ✓; re-enrolment charge ✓ (the 24–47 tier is reached only when the 24-month count is 0); autopay credit ✓; ceiling to the cent ✓. `pl_shipments` counts `mail_order_shipped` rows only; the rule's "shipments" — and the charter's own language "replacement shipment" — could include `mail_order_replaced` rows (G-OBS-4, checked per task).
- dispensing_delay_credit: promise = new_rx_processing_business_days for a `new_prescription` placed order else refill_processing_business_days; delay = **calendar** days order→ship minus those promised days. The base rule `mail_evt_order_dispense` states the promise in **business** days ("New prescriptions dispense within new_rx_processing_business_days and refills within refill_processing_business_days business days"); the extended rule measures the overrun against calendar days and its `overwrite` does not name that base sentence (G-F2, consequence checked per task). Courtesy amounts and single rounding ✓.
- installment_catchup: `in_paid = MAX(installment_number)` over **all** payments of the account (not only the current plan's) — the rule says "an installment unpaid on its due date is overdue" of "the member's payment plan" (checked per task); `in_last_date` = latest payment with `installment_number = in_paid` — when `in_paid = 0` this reads a non-installment payment (checked per task). Waivers are combined additively, `late × (1 − tenure_waiver − spec_waiver)`; the rule says "Part of the late charge is waived … half" and "A further part of the late charge is waived … a quarter", which does not state whether the further part is of the original charge or of what is left (G-F3, consequence checked per task). Count ladder ✓; floor at zero ✓.
- past_due_settlement: span `N = MONTHS(start, NOW) + 1` with `within_months = N` keeps rows with `MONTHS(d,NOW) <= MONTHS(start,NOW)`, which includes rows dated up to about one month **before** the plan's request date, while the same rule sentence gives as its reason "because charges dated before the plan started are financed by the plan and are never part of the settlement" (G-F4, consequence checked per task). Waiting period by the most recent `mail_payment_posted` row's method (any payment, including an installment posted earlier in the same handling) ✓ as stated. Credits = every `mail_credit_issued` in span ✓; payments = `installment_number = 0` payments in span less those on the request date ✓ (the compute removes every non-installment payment on that date, the rule names only the down payment). Courtesy rates ✓; `pd_card` card test ✓ (enum, as above).

No binding invents a basis that the rule lacks; no rule tier lacks a compute branch. The noted items are ambiguities of the rule text whose consequence exists only against a world.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (book_expedited_fee_b4b37c53, shipping_fee), (credit_missed_delivery_02a65815, amount), (pay_plan_down_payment_b796ac1b, amount), (confirm_payment_plan_4c427b9b, plan_monthly_amount), (credit_dispensing_delay_47b21103, amount), (pay_plan_installment_04171a93, amount), (pay_past_due_balance_de0abde8, amount) — each claimed by exactly one policy.
- uuid8s: b4b37c53, 02a65815, b796ac1b, 4c427b9b, 47b21103, 04171a93, de0abde8 — seven distinct values, no shared prefix beyond one hex digit, no sequence/adjacency pattern, none reused with a different tail.
- Docstrings: no docstring names another tool, states a position in a sequence or carries an ordering word (`grep -niE '\b(before|after|first|then|prior)\b'` hits only "balance due after the fee/credit/payment" in Returns blocks, which describe a write's own result).
- Function bodies: every tool does `ctx.find` of the account, `ctx.create` of one row and `ctx.update` of `balance_due` (plus `payment_plan_months` for the confirm tool). None checks eligibility, a prerequisite, an amount or a balance; none refuses or hints. The tool layer judges no prerequisite.
- Observation (G-OBS-5): credit_missed_delivery_02a65815 and credit_dispensing_delay_47b21103 have identical runtime effects (same table, event_type, credit_reason, fields); only the docstring's purpose sentence and the scored tool name tell them apart.

### prerequisite_graph

- Every extended policy carries `prerequisite` (`[]` for the four leaves). Edges: installment_terms→plan_down_payment; plan_down_payment→expedited_fee_catchup; plan_down_payment→missed_delivery_credit; past_due_settlement→installment_catchup; past_due_settlement→dispensing_delay_credit. All `problem` ids are extended ids of this file, none base, none self; graph acyclic (two trees of depth 2 and 1).
- `policy_source` verbatim in the blocked policy's own `rule`: PD-1 line 1401 ✓, PD-2 line 1402 ✓, IT-1 line 1604 ✓, PS-1 line 2164 ✓, PS-2 line 2165 ✓.
- `form`: PD-1, PD-2, PS-1, PS-2 `state`; IT-1 `action` with `fallback_reason` present; no other edge carries a fallback_reason ✓.
- `resolved_by` = the depended-on policy's `target_tool` on all five edges ✓, and each tool's effect moves the gated quantity (fee raises / credits lower `balance_due` → `dn_balance`; down payment lowers `balance_due` → `pl_balance`; installment payment raises the max installment number → PS-1 gate; delay credit adds a `mail_credit_issued` row → `pd_credits`).
- `kind`/`gate`: value_input gates `dn_balance` (plan_down_payment compute), `pl_balance` (installment_terms compute), `pd_credits` (past_due_settlement compute) exist ✓. PS-1 is `state_gate` with `gate: mail_payments.installment_number` — a record field, not an eligibility id (extended policies declare no `eligibility`); the gate is nevertheless the rule's own prerequisite sentence and its condition is a definite record test, so recorded as observation G-OBS-6.
- `condition` vs sentence strength:
  - PD-1 sentence "every expedited shipment the member asked for carries a booked expedited fee on the account" vs condition "Every shipped order whose placed order asked for overnight or two-day shipping has a shipping-charge entry": the condition drops `cold_chain`, which the fee-catchup rule itself treats as an expedited method with its own fee (cold_chain_shipping_fee = 0.00 in every variant). Narrower condition; consequence only where a world has a requested cold-chain shipment with no fee row (checked per task).
  - PD-2 sentence "every replaced shipment that the member paid to expedite carries a posted missed-delivery credit" vs condition restricted to replacements for loss/damage/temperature: the restriction is supplied by the depended-on rule's trigger, so the two read the same ✓.
  - PS-2 sentence "every expedited shipment the pharmacy dispensed later than its processing promise carries a posted dispensing-delay credit" vs condition "… and whose fee is booked …": the condition adds the fee-booked restriction that the sentence lacks (the depended-on rule's trigger says "the member paid for"). Consequence only where a world has a late expedited shipment without a booked fee (checked per task).
  - Both PD-1/PD-2 and PS-2 quantify over **every** such shipment on the account, while each depended-on policy writes only on one order (the most recent shipment / the most recent replacement). If a world holds an older shipment in the quantified class without the waited-on record, the sentence can never be made true by the declared resolving write (checked per task — G-F5).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text ✓.

### prerequisite_sentences

Four-point test per edge:

| edge | ordering connective | form / what it waits on | no tool / id / snake_case | strength vs condition |
| --- | --- | --- | --- | --- |
| PD-1 "The down payment is fixed only after every expedited shipment the member asked for carries a booked expedited fee on the account." | only after ✓ | state: a booked expedited fee (a `mail_shipping_charged` row) on each requested-expedited shipment ✓ | ✓ | slightly broader than condition (cold_chain), see above |
| PD-2 "The down payment is not fixed until every replaced shipment that the member paid to expedite carries a posted missed-delivery credit." | not until ✓ | state: a posted credit on the replaced order ✓ | ✓ | ✓ |
| IT-1 "The installment terms are not fixed until the member has made the plan's down payment." | not until ✓ | action (business words) ✓ | ✓ | ✓ |
| PS-1 "The past-due settlement is taken only after no installment of the member's payment plan stands unpaid past its due date." | only after ✓ | state: no installment overdue ✓ | ✓ | ✓ |
| PS-2 "The past-due settlement is not worked out until every expedited shipment the pharmacy dispensed later than its processing promise carries a posted dispensing-delay credit." | not until ✓ | state ✓ | ✓ | broader than condition (fee-booked), see above |

Fallback test (IT-1): the down payment writes `mail_payment_posted`, `installment_number 0`, `credit_reason not_applicable`, `source_order_id ""` — byte-identical in shape to the past-due payment and any ordinary member payment; no record-visible state singles it out. The fallback is justified ✓.

One write per state-form edge:
- PD-1: only book_expedited_fee_b4b37c53 creates a `mail_shipping_charged` row ✓.
- PD-2: the record a "posted missed-delivery credit" leaves (`mail_credit_issued`, `shipping_fee_waived`, on the order) is also produced by credit_dispensing_delay_47b21103; the sentence disambiguates by the business name "missed-delivery credit", which is the name only mail_ext_missed_delivery_credit's rule uses ("the missed-delivery credit is posted now against that order"). The hop resolves in one reading by name; at the record level the two writes are indistinguishable (G-OBS-2).
- PS-1: only pay_plan_installment_04171a93 writes a non-zero `installment_number` ✓.
- PS-2: same record-level twin as PD-2, disambiguated by "dispensing-delay credit", the name only mail_ext_dispensing_delay_credit's rule uses ✓ (G-OBS-2).

Derivations (sentence + records + depended-on rule → resolving action):
- PD-1: a shipped order whose placed row asked two_day/overnight with no `mail_shipping_charged` row → the rule that books "the missing fee … now as one separate charge on that order" is mail_ext_expedited_fee_catchup → book the fee. Single reading, provided the unbooked shipment is the account's most recent shipment (the depended-on rule acts only there; G-F5).
- PD-2: a replaced (loss/damage/temperature) order with a booked fee and no credit → mail_ext_missed_delivery_credit ("the missed-delivery credit is posted now against that order") → post the credit. Single reading, provided that order is the most recent replacement (G-F5).
- IT-1: action named → mail_ext_plan_down_payment → the member pays the down payment (owner user).
- PS-1: overdue installments → mail_ext_installment_catchup ("the member catches the plan up with an installment payment") → member pays installments.
- PS-2: latest expedited shipment dispensed later than promise, fee booked, no credit → mail_ext_dispensing_delay_credit → post the credit.

No rule restates another problem's sentence; no depended-on rule restates the blocked sentence; no tool name or policy id in any rule. No cross-problem order is stated in any extended rule beyond the five sentences. Base rules: `mail_rx_transfer`/`mail_account_closure`/`mail_evt_credit_hold` state orders between base events only; none grounds an extended edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- expedited_fee_catchup ← mail_shipping. S1 (fee by requested method) — handled differently (adds cold-chain fee for a member-requested cold-chain order and the surcharges/discount/late share) and **declared** (overwrite names S1). S2 (temperature packaging; cold-chain "never treated as a member-requested upgrade") — the extended rule charges the cold-chain fee as a member-requested expedited fee, which S2 says it never is; not named in `overwrite`. All variants set cold_chain_shipping_fee 0.00, so the amount is the same either way; recorded as observation G-OBS-1 (no scored figure can differ). S3 (US/APO, never abroad) followed. S4 (fee at most once per order; credited back on missed delivery) followed (trigger "no expedited fee is booked on that order").
- missed_delivery_credit ← mail_evt_cancel_credit (S1-S4: cancellation, pharmacy-error credit, small-balance write-off — no quantity in common) followed; mail_shipping S4 credit-back clause **declared** (replaced by shares + allowances); mail_evt_replacement (report window, quota, pharmacy error, once per reason) — governs the replacement write, not the credit amount; followed.
- plan_down_payment ← mail_evt_payment (oldest-first application, instruments, installment_number 0 for non-installments, open account) followed; mail_payment_plan "the first installment is collected when the plan starts" **declared**. mail_payment_plan threshold sentence inherited (not hit).
- installment_terms ← mail_payment_plan "may ask to pay it in up to payment_plan_max_months monthly installments" **declared**; "The installment amount is the balance due divided by the number of months chosen, rounded up to the cent" **declared**; threshold sentence ("only when the balance due is at least payment_plan_min_balance …") inherited, not hit — it applies to the confirm write at its handling time (checked per task); mail_auto_refill followed.
- dispensing_delay_credit ← mail_shipping S4 credit-back clause **declared**; mail_evt_cancel_credit followed; mail_evt_order_dispense S6 ("New prescriptions dispense within new_rx_processing_business_days and refills within refill_processing_business_days business days …") — the extended rule measures the delay as **calendar** days order→ship minus the promised number, i.e. an anonymous intermediate that handles the base's business-day promise differently, and `overwrite` does not name S6 → **undeclared override (G-F2)**; whether it hands a task a second answer is demonstrated per task.
- installment_catchup ← mail_payment_plan "a missed installment ends the plan" **declared**; mail_evt_payment followed (installment carries its number).
- past_due_settlement ← mail_evt_payment "each order charge is due within payment_due_days of shipment" **declared** (replaced by the waiting-period ladder); other sentences followed.

Disguised forms: no 0/1 multiplier zeroes a base-fixed amount except `fx_late_share = 0` ("after 60 days no fee is booked"), which is a declared tier of the extended rule on the fee the extended policy itself computes (not a base quantity); no dropped base branch found.

### factor_ladders

Every policy declares 6 factors; every ladder has 3 tiers, pairwise-disjoint as stated, every tier stated in prose in the rule and implemented in `compute`; no two tiers of one ladder select the same value or method; every fall-through equals the policy baseline (two-day fee / share 1.0 / 0 surcharge / 10 % / 3 months / one installment / one-month wait). `decides` is never `result`; binding sets are disjoint within each policy.

| policy | parameter | method (declared) | honest method after label test | multi-source (non-fall-through tiers over ≥2 records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| expedited_fee_catchup | 5 | expedite_review_window | **0** | saturday_delivery_surcharge (placed row method + shipped row date), remote_destination_surcharge (shipped row method + account ZIP) | none |
| missed_delivery_credit | 5 | failure_review_window | **0** | retail_bridge_allowance (replaced row drug + retail claims) | retail_bridge_allowance → retail |
| plan_down_payment | 5 | card_review_window | **0** | card_payment_reduction (account card + payment rows) | specialty_balance_reduction → specialty |
| installment_terms | 5 | financed_amount_basis | 1 | account_history_lengthening (account tenure + shipped rows), automatic_payment_credit (account card + placed rows) | specialty_balance_lengthening → specialty (benefit_design_lengthening reads plan, not a difficulty) |
| dispensing_delay_credit | 5 | prior_credit_window | **0** | remote_destination_courtesy (shipped row + account ZIP), retail_bridge_courtesy | retail_bridge_courtesy → retail |
| installment_catchup | 5 | installments_collected | 1 | tenure_late_waiver (account tenure + service requests), automatic_refill_late_credit (account flag + placed rows) | specialty_late_waiver → specialty |
| past_due_settlement | 5 | past_due_waiting_period | **0** | card_history_rate, automatic_refill_rate | maintenance_choice_rate → retail |

Label test (G-F1): the five window/period factors labelled `method` select only a different **number** substituted into the same formula — `COUNT(…, within_months=fx_window)` with `fx_window ∈ {K('long_window_months')=24, K('short_window_months')=6, K('standard_window_months')=12}` (likewise `wv_window`, `dn_window`, `lt_window`), and `SUM(…, within_months=pd_window)` with `pd_window ∈ {2, 0, 1}`. The tier values are even drawn from the same `params` block as the policies' `parameter` factors. These are look-back/threshold lengths — "a factor labelled `method` whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)". They are mislabelled; counted honestly, those five policies have 0 `method` factors against the floor of 1. installments_collected (count = overdue count / overdue + final / one) and financed_amount_basis (balance less recent charges / less recent fees / whole balance) select different expressions and pass the label test.

Reality of conditions/outcomes: all conditions are ones a home-delivery pharmacy plausibly weighs (requested method, weekday, AK/HI ZIP, expedite frequency, booking delay, replacement cause/route, repeat failures, bridge supply at retail, supply length, plan history, tenure, specialty balance owed, card history, benefit design, recent charges, auto-refill use, payment instrument). None restates a policy's scope (each tier divides the customers reaching the write). Observations only: the "card-processing grace" keyed to the instrument of the last installment and the specialty-balance discounts/waivers are unusual but stated with a business rationale; no tier outcome is a straw man.

### findings

- **G-F1 — SOURCE-FACTOR RED (structural; consequence per task).** Symptom: the declared `method` factor of expedited_fee_catchup (expedite_review_window), missed_delivery_credit (failure_review_window), plan_down_payment (card_review_window), dispensing_delay_credit (prior_credit_window) and past_due_settlement (past_due_waiting_period) only substitutes a number (a 24/6/12-month or 2/0/1-month window) into the same aggregate. Root cause: window length labelled `method`. Evidence: `mail.extended.yaml` compute lines 1058-1059, 1237-1238, 1451-1452, 1830-1831, 2211-2213; factor declarations lines 1125-1139, 1294-1308, 1519-1533, 1871-1885, 2239-2253. Demonstrated consequence: counted honestly each of those five computations has 0 `method` factors (< 1 required). Bears on every task whose computations include any of these five policies (both trees do: task 0 via fee_catchup, missed_delivery_credit, plan_down_payment; task 1 via dispensing_delay_credit, past_due_settlement).
- **G-F2 — undeclared override, consequence per task.** dispensing_delay_credit measures the dispensing delay in calendar days minus the promised processing days, while base `mail_evt_order_dispense` S6 states the promise in business days; `overwrite` does not name S6. Bears on the task that claims dispensing_delay_credit; the per-task file demonstrates whether a business-day reading moves the delay tier or the credit.
- **G-F3 — ambiguous combination of the two late-charge waivers, consequence per task.** installment_catchup: "Part of the late charge is waived … half …" + "A further part of the late charge is waived … a quarter …" admits additive (`1 − 0.5 − 0.25`) and sequential (`0.5 × 0.75`) readings; the compute takes additive. Bears on the task that claims installment_catchup when both waivers and a non-zero late charge apply.
- **G-F4 — internal contradiction in the settlement period, consequence per task.** past_due_settlement's span `N = months(request→handling) + 1` includes entries up to about a month before the plan's request date, while the same sentence states "charges dated before the plan started … are never part of the settlement". Bears on the task that claims past_due_settlement when the world holds entries in that gap.
- **G-F5 — "every … shipment" quantifiers vs single-order resolving writes, consequence per task.** PD-1, PD-2 and PS-2 quantify over every shipment of a class on the account, while the depended-on policies act on one order (the most recent shipment / most recent replacement). Bears on each task whose world holds a second unresolved member of the class.
- G-OBS-1 (observation): cold-chain charged as a member-requested expedited fee contradicts base mail_shipping S2 ("never treated as a member-requested upgrade"), undeclared; every cold_chain_shipping_fee is 0.00, so no figure can differ.
- G-OBS-2 (observation): missed-delivery and dispensing-delay credits are indistinguishable at record level (both `shipping_fee_waived` on the order); both supersede the same base clause; edges PD-2/PS-2 resolve by business name only. A world with one order qualifying for both would admit two credits and an order dependency (checked per task).
- G-OBS-3 (observation): `request_status cancelled` is read as "ended early because an installment was missed" and `request_status completed` (written at confirmation) as "plans the member completed"; the schema carries no cause/payoff marker. Consequence checked per task.
- G-OBS-4 (observation): "shipments" counted from `mail_order_shipped` only, while the charter itself calls a replacement a "replacement shipment". Consequence checked per task.
- G-OBS-5 (observation): two credit tools with identical effects.
- G-OBS-6 (observation): PS-1 `gate` names a record field rather than an eligibility id.

## closing_checklist

Written 2026-10-08 ~07:30 UTC, after both reveals. The charter-global section above was frozen before any reveal and is unchanged.

The difficulty is **not closed**: neither task passes all four relationships.

- Per-task files correspond one-to-one with the tasks (0.md, 1.md) beside this file; first revision, no older revision to trace. Comparison sections: task 0 RED (SOURCE-TASK T0-F1, SOURCE-FACTOR T0-F2); task 1 RED (SOURCE-POLICY T1-F1, SOURCE-TASK T1-F2, SOURCE-FACTOR T1-F3).
- Coverage and exclusivity: task 0 charter_scope = {expedited_fee_catchup, missed_delivery_credit, plan_down_payment, installment_terms}; task 1 = {dispensing_delay_credit, installment_catchup, past_due_settlement}. Pairwise disjoint, jointly all 7 extended policies, matching the two connected components derived from the charter alone. Task tools match scopes one-to-one; uuid8s independent (see action_binding_and_uuids). **But scope exclusivity does not hold on the handling world of task 0**: after its own fee write, task 1's dispensing-delay policy fires on task 0's order `112a8df1` (T0-F1).
- Trees: task 0 — 3 prerequisite problems, 3 value_input edges, owner=user writes 2, acyclic; task 1 — 2 prerequisite problems, 1 value_input edge, owner=user writes 2, acyclic; whole-difficulty graph acyclic, no cross-task edge. PASS on the tree relationship for both.
- Factors: every computation declares 6 factors with honest baselines, all bearing weight, whole baselines definite and different from gold; cross-difficulty and multi-source factors present and seeded in both tasks. Fails the `method` floor in 5 of 7 computations (G-F1).
- Gates: not re-run by the auditor (Step 0: the brief's 07:12 UTC snapshot is cited; the audit edits nothing, so the final form is the audited form).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit requested by the coordinator (round 2) after rework. Freeze time 2026-10-08 ~08:57 UTC, written before either task's round-2 GT was revealed; nothing below derives from a revealed GT.
- Inputs verified by the auditor (sha256): mail.extended.yaml `4adcdae3655f47c37ea3c48a35f58a85a0b545bbaa312ba748727eaadd068fa4` (**changed** from `e11386fc…` → every charter-global section re-derived in full); task_tools.py `18aaa7f8faa1728d2ed5595b9c01a155e4e56104ad64765d856a413072ac1fc2` (unchanged → action_binding_and_uuids carried forward on that hash); views task_0 `68f43bc2…3147ec`, task_1 `4402ea26…48ed8aa` (both changed).
- Entry conditions: round-2 gate snapshot supplied by the orchestrator (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; traceability deferred). Masked views supplied with hashes. Complete.
- Masked / unread until the per-task freezes: tasks/*.json, worklog.md; no recursive search over tasks/.
- Round-1 text above is left untouched.

### policy_conflict_scan (revision 2)

- Base section lines 1-1005 still textually identical to blueprint/products/mail.yaml (diff: trailing blank line only).
- Same 7 extended policies, same targets, triggers, subjects and `(target_tool, computes)` pairs; same two prerequisite components {installment_terms → plan_down_payment → {expedited_fee_catchup, missed_delivery_credit}} and {past_due_settlement → {installment_catchup, dispensing_delay_credit}}.
- PD-1, PD-2 and PS-2 now quantify over the account's **most recent** shipment / replacement — the same object the depended-on policies act on (G-F5 closed, below).
- The two credit policies still supersede the same base clause and still write identical records (G-OBS-2 unchanged, as declared by the reworker). Their triggers can now coincide only on an order that is at once the latest shipment, late by business days and the latest replacement; checked per task.
- installment_catchup's trigger now names the plan in force ("the account records a plan length").

### rule_compute_equivalence (revision 2)

Swept again binding by binding; the changed bindings:
- expedited_fee_catchup: `fx_fee` cold-chain tier → 0.0 ✓ (rule: "an order that went in cold-chain packaging is charged no expedited fee"); `fx_late_share` = 1 − 0.01 × (days − 30) for 31-60 days ✓ ("reduced by one percent of the fee for every day beyond the 30th"), 0 beyond 60 ✓ ("written off"). Observation R2-OBS-1: "one percent of **the fee**" uses the word the rule elsewhere gives to the program fee alone ("The fee, the Saturday surcharge and the remote surcharge are first added together"), but the combining sentence fixes it as a share ("the late-booking share is then applied to the discounted amount"), so the multiplicative reading is the only one consistent with the whole rule.
- missed_delivery_credit: `wv_supply` = 0.05 × days for ≥ 61 days ✓, flat 2.50 for 31-60 ✓, none ≤ 30 ✓.
- plan_down_payment: `dn_tenure_cut` = 0.005 × whole years for ≥ 60 months ✓ ("half a point for each whole year"), flat 0.02 for 36-59 ✓; `dn_ended`/`dn_completed` wording now names the record ("recorded as cancelled (the record of a plan that ended early …)", "recorded as completed payment-plan requests") ✓ — G-OBS-3 closed.
- installment_terms: "shipped orders (replacement shipments are not counted)" = `event_type mail_order_shipped` ✓ — G-OBS-4 closed for this policy.
- dispensing_delay_credit: promise in business days; `lt_bdays` counts Monday-Friday days after the order date through the ship date (`DAYS('2021-01-04', d) % 7`, 2021-01-04 = Monday → 0 = Monday) ✓ ("counting the ship date and not the order date"); share = 0.25 × delay for 1-2 ✓, 0.75 for 3-4 ✓, 1.0 for ≥ 5 ✓. Public holidays are not mentioned by the rule and not excluded by the compute — consistent with "Monday through Friday".
- installment_catchup: the rule now states "both waived parts are shares of the original late charge, so they are added together and taken off that charge once" = `in_late * (1 - in_tenure_waiver - in_spec_waiver)` ✓ — G-F3 closed.
- past_due_settlement: span sentence now reads "entries dated earlier than that belong to the balance the plan financed"; the contradictory reason ("charges dated before the plan started … are never part") is gone, and the one-month band before the request date is the band installment_terms leaves out of the financed amount ("member charges for shipments dated less than one whole month before … billed on their normal terms") — G-F4 closed. Down-payment exclusion now "payments other than installments posted on the plan's request date" = compute ✓. Volume rate per order (0.005 × count) for ≥ 8, flat 2 % for 4-7 ✓, "replacement shipments are not counted" ✓.
No binding without a rule basis, no rule tier without a branch.

### action_binding_and_uuids (revision 2)

Carried forward unchanged on task_tools.py hash `18aaa7f8…72ac1fc2` (identical to round 1); `(target_tool, computes)` pairs unchanged.

### prerequisite_graph (revision 2)

- Same five edges, acyclic; `policy_source` verbatim in each blocked rule: PD-1 line 1401, PD-2 line 1402, IT-1 line 1604, PS-1 line 2172, PS-2 line 2173 ✓. `form`/`fallback_reason` unchanged (IT-1 only action form). `resolved_by` = target tools ✓; gates exist ✓.
- Conditions now match their sentences in strength and scope: PD-1 "When the placed order of the account's most recent shipment asked for overnight or two-day shipping, a shipping-charge entry is booked against that order" = sentence (overnight or two-day; most recent shipment) ✓; PD-2 ✓; PS-2 "When the account's most recent shipment went out by an expedited service the member paid for and its ship date is more business days after its order date than the program's processing days …" = sentence ("the member paid to expedite it and the pharmacy dispensed it later than its processing promise") ✓.
- G-OBS-6 (PS-1 gate names a field) unchanged.

### prerequisite_sentences (revision 2)

Four-point test re-run on the reworded PD-1, PD-2, PS-2: connectives "only after" / "not until" ✓; state form naming record-visible states (a booked fee on the latest shipment; a posted credit on the latest replacement's order; a posted credit on the latest shipment) ✓; no tool, id or snake_case ✓; strength = condition ✓. One write per state edge: PD-1 only the fee tool books a shipping-charge row ✓; PD-2 / PS-2 the record-level twin (G-OBS-2) still exists and is still disambiguated by the business names "missed-delivery credit" / "dispensing-delay credit". Derivations: PD-1 → the fee policy acts on "the account's most recent shipment" = the sentence's object ✓; PD-2 → the credit policy works "on the account's most recent replacement shipment" = the sentence's object ✓; PS-2 → the delay policy acts on "the account's most recent shipment" = the sentence's object ✓. G-F5 closed.

### override_declarations (revision 2)

- expedited_fee_catchup: `overwrite` replaced_by now carries the cold-chain sentence; base mail_shipping S2 ("drugs that must ship cold go cold_chain at cold_chain_shipping_fee, and that is never treated as a member-requested upgrade") is now followed (cold chain is not a member-requested expedited fee; cold_chain_shipping_fee is 0.00 in every variant) — G-OBS-1 closed.
- dispensing_delay_credit: the promise is now stated in business days, matching base mail_evt_order_dispense S6; the delay is the business-day overrun of that promise. No base sentence is handled differently, so no declaration is needed — G-F2 closed.
- Other policies: unchanged conclusions (declared overrides as in round 1).

### factor_ladders (revision 2)

| policy | parameter | method (honest) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| expedited_fee_catchup | 5 (window now `parameter`) | late_booking_treatment: write-off / per-day proration / full | saturday, remote | none |
| missed_delivery_credit | 5 (window now `parameter`) | lost_supply_allowance: per-day 0.05 × days / flat 2.50 / none | retail_bridge_allowance | retail |
| plan_down_payment | 5 (window now `parameter`) | tenure_rate_reduction: per-year 0.5 pt × years / flat 2 pts / none | card_payment_reduction | specialty |
| installment_terms | 5 | financed_amount_basis (unchanged) | account_history_lengthening, automatic_payment_credit | specialty |
| dispensing_delay_credit | 5 (window now `parameter`) | dispensing_delay_share: per-day 0.25 × delay / flat 0.75 / whole fee | remote_destination_courtesy, retail_bridge_courtesy | retail |
| installment_catchup | 5 | installments_collected (unchanged) | tenure_late_waiver, automatic_refill_late_credit | specialty |
| past_due_settlement | 5 (waiting period now `parameter`) | shipment_volume_rate: per-order 0.5 % × orders / flat 2 % / none | card_history_rate, automatic_refill_rate | retail |

- The five window/period factors are now labelled `parameter` (honest). Each policy now has exactly one `method` factor whose tiers select different algorithms (a per-unit proration over a record-derived quantity vs. a flat amount vs. none); each passes the label test — G-F1 closed. Observation R2-OBS-2: dispensing_delay_share's per-day tier spans only delays 1-2, so it can yield only 0.25 or 0.50; it is still a different rule from the flat tier and is accepted.
- Ladders: 3 tiers each, disjoint, every tier in rule prose and compute, no duplicated outcome (checked at the boundaries: late share 1.00 at 30 days vs 0.99 at 31; supply 2.50 at 60 vs 3.05 at 61; tenure 2 pts at 59 months vs 2.5 at 60; volume 2 % at 7 vs 4 % at 8; delay share 0.50 at 2 vs 0.75 at 3). Conditions and outcomes are ones a home-delivery pharmacy plausibly weighs; observation R2-OBS-3: the per-order volume rate and per-year tenure reduction are unbounded in count (bounded in effect only by the 5 % down-payment floor / not at all for the settlement), which matters only for implausibly large counts.

### findings (revision 2)

| round-1 item | status in revision 2 | evidence |
| --- | --- | --- |
| G-F1 | **closed** (charter) | factor_ladders (revision 2) |
| G-F2 | **closed** | override_declarations (revision 2); rule line 1808 |
| G-F3 | **closed** | rule line 2002 |
| G-F4 | **closed** | rule line 2174 |
| G-F5 | **closed** | prerequisite_sentences (revision 2); lines 1401, 1402, 2173 |
| G-OBS-1 | closed | fee rule line 1040 |
| G-OBS-2 | unchanged (observation) | both credit tools still write `shipping_fee_waived` |
| G-OBS-3 | closed | lines 1404, 1409, 1611, 2001 |
| G-OBS-4 | closed | lines 1606, 2178 |
| G-OBS-5 | unchanged (observation) | task_tools.py unchanged |
| G-OBS-6 | unchanged (observation) | line 2187 |

New charter-global defects: none found. New observations: R2-OBS-1, R2-OBS-2, R2-OBS-3 (above). Per-task closure of T0-F1, T0-F2, T1-F1, T1-F2, T1-F3 is judged in each task file's revision_2.

### closing_checklist (revision 2)

Written after both round-2 reveals (~09:00 UTC); the revision-2 charter-global section above was frozen before them and is unchanged.

- Per-task files 0.md and 1.md carry round 1 untouched plus revision_2; both revision-2 comparison sections PASS.
- Coverage/exclusivity: task 0 = {expedited_fee_catchup, missed_delivery_credit, plan_down_payment, installment_terms}; task 1 = {dispensing_delay_credit, installment_catchup, past_due_settlement}; disjoint, jointly complete; and now also exclusive on each handling world (no policy of the other task fires after any gold write — task 0's latest shipment is on time by business days; task 1 has no unbooked fee and no replacement). Task tools closed and uuid8s independent (unchanged module).
- Trees: task 0 n = 3 (3 value_input), task 1 n = 2 (1 value_input); each has 2 owner=user writes; whole-difficulty graph acyclic, no cross-task edge.
- Factors: every computation 6 factors, 5 parameter + 1 honest method, multi-source and cross-difficulty factors present and seeded per task, every factor bears weight against an honest baseline, every whole baseline definite and different from gold (task 0: 0.00 / 22.45 / 14.58 / 42.51; task 1: 34.16 / 38.13 / 108.12).
- Gates: round-2 orchestrator snapshot (all OK, traceability deferred) cited; the auditor edited nothing.
- **Difficulty passes the source-layer audit in revision 2.** Remaining items are observations only: G-OBS-2, G-OBS-5, G-OBS-6, the ledger observation, R2-OBS-1…3.
