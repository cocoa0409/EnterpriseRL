# Policy-task audit — real_estate_closing_plans / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-12T13:39Z. Written before any task's GT was revealed; contains nothing derived from GT.
- Frozen inputs (sha256, re-verified at audit start, identical to the coordinator brief):
  - `tasks/real_estate_closing_plans/realty.extended.yaml` 8c44623aa46ae8306ba8d3b725aa67966509b1408c88b639b9b1d5ba6e2f57b3
  - `tasks/real_estate_closing_plans/task_tools.py` 626837554561b5539c4d2bedc2eb0b09cad461b5297dc50aaa2f25d746d463c2
  - masked views `.audit_views/policy_task/real_estate_closing_plans/0.view.json` 09f824b9…8d9, `1.view.json` 45608944…d55
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/realty.yaml` (+ `homeplan.yaml` tier parameters), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/`within_months`).
- Masked / unread at freeze: all of `tasks/real_estate_closing_plans/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), `worklog.md`, any prior audit. No recursive search touched `tasks/*/tasks/`.
- Entry conditions (Step 0): gate snapshot supplied in the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK only on pre-docs tool-name unlocks; validate_scenario only "required document not found"), masked views with hashes supplied. Entry conditions met; gates cited, not re-run.

Charter shape: base section (lines 1–1943) + 4 extended policies, 4 task tools, M=2.

| Extended policy | target_tool (owner) | prerequisite |
| --- | --- | --- |
| realty_ext_failed_sale_charge | bill_failed_sale_charge_3e9b31c4 (agent) | [] |
| realty_ext_seller_settlement_payment | pay_failed_sale_charge_by_card_a1a6aa51 (user) | realty_ext_failed_sale_charge, value_input, state form |
| realty_ext_reissued_plan_invoice | reissue_plan_invoice_a1bc9266 (agent) | [] |
| realty_ext_buyer_direct_prepayment | prepay_plan_invoice_by_card_13fdf553 (user) | realty_ext_reissued_plan_invoice, value_input, state form |

### policy_conflict_scan

- Base copy: the base section of the extended file parses to exactly the same object as `blueprint/products/realty.yaml` (yaml.safe_load equality: True); only formatting differs. Base copy is verbatim-compatible.
- Overlapping subjects: `realty_payment` is the subject of two extended policies (seller settlement, buyer prepayment), but they act on disjoint invoices (failed-sale invoice vs plan invoice), disjoint order types (listing order that never closed vs buyer_only order before closing) and disjoint tools. `realty_seller_service_charge` and `realty_invoice` each have one extended claimant. No two extended policies reach a conclusion on the same quantity.
- Time anchors: failed-sale due date = billing date + failed_sale_bill_due_days (base and extended agree); reissued invoice due on the expected closing date (base "due on the closing date" before closing is the expected date; event field `due_date` text agrees). No conflict.
- Cross-category read boundaries: failed-sale reads hvaccare + homeplan; settlement reads lineplan; reissue reads homeplan + addon; prepayment reads landlord + hvaccare. All reads are customer-scoped holdings/ledgers; no write crosses categories.
- Terminal states: see findings F1 and F2 below (base terminal semantics the extended payment rules contradict).
- Scope exclusivity/completeness: the four policies split into two disjoint trees {failed_sale → settlement} and {reissue → prepayment}; with M=2 each task can claim exactly one tree, jointly covering all four extended policies. (Verified against the actual claimed scopes only after reveal — see task files.)

### rule_compute_equivalence

Swept every `compute` binding against its `compute_basis` quotation and back against the `rule` text.

- realty_ext_failed_sale_charge: premium_invoiced (sum of plan invoices, not netted by credit memos), seller_benefit_paid (authorizations − reversals), days_in_force (DAYS order_date→end_date), listing_months_begun (MONTHS + 1), charge_cap three-branch, lesser_amount, emergency_requests/rate/dispatch_cost, hvac_benefit (heating/cooling/ductwork net), tuneup_visits (XCOUNT within 12 months of NOW = billing date), maintained_same_home, maintained_share/credit, uncovered_requests/share/credit (× seller_service_call_fee), floored_subtotal with the zero-benefit guard, kept_home_start/monthly (tier `monthly_premium` via CPARAM), waiver_share, result rounding. Each is quoted from the rule and each rule tier has a compute branch. Minor: the compute's lower waiver tier additionally requires `kept_home_monthly > 0`, which the rule does not state; no homeplan tier has a zero monthly_premium, so it never bites (observation O6).
- realty_ext_seller_settlement_payment: all bindings quoted. `compute_basis.result` quotes the baseline sentence "The seller pays the open failed-sale balance in full in one payment" while `result` is `RND(payment_now)` (an installment can be selected) — the quotation does not describe the binding (observation O5; the installment sentences are separately quoted under `payment_now`, so no tier is unstated).
- realty_ext_reissued_plan_invoice: all bindings quoted. `rider_premium_billed` = XSUM of all the customer's `addon_premium_charge` rows (any rider, any base) and the rule says "the rider premium billed to the buyer on optional coverage riders" — literal match; a reader could narrow it to this order's rider (second reading only matters for a buyer holding riders on other bases; observation O7, bites no task here — verified per task).
- realty_ext_buyer_direct_prepayment: all bindings quoted. `buyer_deposits`/`escrow_deposits` sum payments only; refunds are not netted and the rule is silent on refunds (see F2).
- No compute invents a basis; no rule tier is missing from compute. Rule/compute equivalence: PASS (observations only).

### action_binding_and_uuids

- `(target_tool, computes)`: (bill_failed_sale_charge_3e9b31c4, amount), (pay_failed_sale_charge_by_card_a1a6aa51, amount), (reissue_plan_invoice_a1bc9266, amount), (prepay_plan_invoice_by_card_13fdf553, amount) — each claimed by exactly one policy.
- Function bodies (task_tools.py): every tool writes unconditionally; none checks status, existence of a prior invoice, or order; none refuses. The tool layer judges no prerequisite.
- Docstrings: no other tool's name. Two temporal clauses point at the neighbouring action: bill docstring "so the seller can quote it when paying"; pay docstring "as given to you by the Bridgewell representative when the charge was billed". These state the bill→pay order in the tool layer (observation O3; no second answer follows from it).
- uuid8s: 3e9b31c4, a1a6aa51, a1bc9266, 13fdf553 — all distinct, no common tail, no sequence. a1a6aa51 and a1bc9266 share the 2-hex prefix `a1` (chance ≈1/256 per pair); not evidence of batch derivation on its own (observation O4).

### prerequisite_graph

- `prerequisite` filled on all four policies ([] on the two depended-on policies).
- Edges: settlement → failed_sale; prepayment → reissue. Both `problem` ids are extended policy ids in this file, neither self-referencing; graph acyclic (two disjoint 2-node chains).
- `policy_source` verbatim in own rule: settlement "A seller's settlement payment toward listing-period service is not taken until the order's billing history carries the failed-sale charge invoice billed for that service." — present verbatim in its rule. Prepayment "A buyer's direct payment toward the plan premium is taken only after the order's billing history carries a plan invoice that no plan-change credit memo offsets." — present verbatim.
- `form: state` on both, no `fallback_reason` (correct).
- `condition`: settlement "realty_billing_entries carries a realty_seller_service_charge row for the order" = the sentence's state, neither stronger nor weaker. Prepayment "more realty_invoice amount than realty_credit_memo amount with credit_reason plan_changed on the order, i.e. a plan invoice issued after the latest plan change stands open" — equivalent to "a plan invoice no plan-change memo offsets" given each memo credits one invoice in full.
- `resolved_by` = the depended-on policy's target_tool in both; `kind: value_input` with `gate` naming a real binding (`failed_sale_billed`, `plan_invoiced`) whose value the write raises. No authoring-viewpoint phrasing.
- Prerequisite graph: PASS.

### prerequisite_sentences

Four-point test, both edges:
1. Ordering connective: "is not taken until" / "is taken only after" — explicit.
2. State form: waited-on state is a billing-history record ("carries the failed-sale charge invoice"; "carries a plan invoice that no plan-change credit memo offsets") in the words of the billing finder ("plan invoices, failed-sale charges, … credit memos"); no actor, no tool.
3. No tool name, policy id, snake_case token or row id.
4. Strength matches `condition` (see graph section).

Single resolving write: the only tool that creates a `realty_seller_service_charge` row is bill_failed_sale_charge_3e9b31c4; the only tool that creates a `realty_invoice` row is reissue_plan_invoice_a1bc9266 (no tool in this difficulty posts credit memos). Derivation as a reader: settlement rule → "not taken until … carries the failed-sale charge invoice" → the failed-sale policy's rule "Bridgewell bills the seller one failed-sale charge … only on an order in status listing_expired or cancelled that never recorded a closing" → the bill action. Prepayment rule → "only after … carries a plan invoice that no plan-change credit memo offsets" → reissue policy "the earlier invoice is credited in full and the reissued plan invoice is issued at the reissued plan premium" → the reissue action. One reading each. Depended-on rules do not restate the sentence; no second wording; no undeclared cross-problem order in any extended rule (the reissue rule's "credited in full and … reissued" orders a credit memo that is no problem of this difficulty). Prerequisite sentences: PASS.

### override_declarations

Sentence-by-sentence against `base_policy_refs`:

- realty_ext_failed_sale_charge vs realty_failed_sale_charges: the lesser-of / zero-benefit / call-fee sentence is superseded and declared; all other base sentences (eligibility on listing_expired/cancelled never-closed, one charge per order, buyer-only exclusion, due = billing + failed_sale_bill_due_days) are restated unchanged. Declared; merged semantics unique.
- realty_ext_reissued_plan_invoice vs realty_premium_pricing / realty_order_requirements: the premium formula sentence, the plan-change reissue sentence and the order-requirements reissue sentence are all declared; replacement scoped "only for such an invoice". Status eligibility kept. Declared; unique.
- realty_ext_seller_settlement_payment (overwrite: []) vs realty_closing_and_escrow / realty_failed_sale_charges: "Payments are applied to the oldest open invoice first" followed; failed-sale "billed to the seller and due failed_sale_bill_due_days calendar days after billing" — the extended settlement reduces what the seller pays by allowance rates and a flat credit but no write books those reductions against the invoice (see F1).
- realty_ext_buyer_direct_prepayment (overwrite: []) vs realty_closing_and_escrow / realty_premium_pricing: base "invoiced once per order, payable through escrow at closing" — extended adds a direct card channel before closing (undeclared, channel only, no scored quantity moves: observation O2). Base "Buyer coverage is confirmed only when the plan invoice is paid in full …" vs extended allowance-reduced payment with no credit booked (F1). Outside its refs: base realty_cancellation_and_credits "Any credit balance is refunded within refund_processing_days calendar days to the party that paid the invoice" vs extended deposit carryover (F2).

### factor_ladders

| Policy | Factor | effect | tiers | multi-source | cross_difficulty | stated in rule / compute |
| --- | --- | --- | --- | --- | --- | --- |
| failed_sale_charge | listing_cap_proration | method (daily proration / months-begun proration / full) | 3 | no (dates) | — | yes / yes |
| | after_hours_dispatch_recovery | parameter (85 / 110 / 0 per emergency) | 3 | no | — | yes / yes |
| | maintained_hvac_credit | parameter (0.2 / 0.1 / 0) | 3 | yes (agreement status+address AND visit rows) | hvaccare (not a difficulty category — O8) | yes / yes |
| | uncovered_call_fee_credit | parameter (1 / 0.5 / 0) | 3 | no | — | yes / yes |
| | keep_home_waiver | parameter (0.5 / 0.25 / 0) | 3 | yes (homeplan start vs realty end_date AND tier premium) | homeplan | yes / yes |
| seller_settlement | settlement_installments | method (3-installment / 2-installment / whole) | 3 | yes (no seller payment AND amount band) | — | yes / yes |
| | prompt_settlement_allowance | parameter (0.03 / 0.01 / 0) | 3 | no | — | yes / yes — **see F3** |
| | line_plan_loyalty_allowance | parameter (0.02 / 0.01 / 0) | 3 | yes | lineplan | yes / yes |
| | missed_contact_service_credit | parameter (75 / 40 / 0) | 3 | no | — | yes / yes |
| reissued_plan_invoice | plan_reissue_handling | parameter (50 / 25 / 0) | 3 | no | — | yes / yes |
| | early_ordering_allowance | parameter (40 / 20 / 0) | 3 | no | — | yes / yes |
| | homeowner_loyalty_credit | method (per-term × (term−1) / flat 40 / none) | 3 | yes (active contract term AND returned-payment rows) | homeplan | yes / yes |
| | rider_bundle_discount | parameter (60 / 30 / 0) | 3 | yes (rider status on this order AND billed rows) | addon | yes / yes |
| buyer_direct_prepayment | deposit_carryover | method (net of buyer payments / net of all payments less return fee / as stands) | 3 | yes | — | yes / yes — **see F4** |
| | closing_lead_allowance | parameter (0.03 / 0.015 / 0) | 3 | no | — | yes / yes |
| | rental_owner_allowance | parameter (0.02 / 0.015 / 0) | 3 | yes | landlord | yes / yes |
| | comfort_member_allowance | parameter (0.02 / 0.01 / 0) | 3 | yes | hvaccare (O8) | yes / yes |

Counts per policy: failed_sale 5 (1 method, 4 parameter); settlement 4 (1 method, 3 parameter); reissue 4 (1 method, 3 parameter); prepayment 4 (1 method, 3 parameter). Each ladder ≥3 pairwise-disjoint tiers, outcomes distinct, fall-through = the policy baseline in every factor; `decides` is an input binding (never `result`); binding sets disjoint within each policy. Labels honest: the three method factors change the algorithm (proration basis; installment split; per-term vs flat; carry-over arithmetic). Per-tree: {failed_sale, settlement} has multi-source (maintained, keep_home, line, installments) and cross-difficulty (homeplan, lineplan); {reissue, prepayment} has multi-source (loyalty, bundle, rental, comfort) and cross-difficulty (homeplan, addon, landlord).

Realism review of ladders (US home-warranty / closing practice): the lesser-of failed-sale charge, proration of the cap by time in force, missed-contact service credits, installment plans, prompt-payment discounts, keep-the-home conversion waivers, plan-change reissue fees, cross-product loyalty discounts and escrow-vs-card payment are all practices such a business publishes. Weaker but not demonstrably unreal: per-emergency recovery rate lower for two or more emergencies than for one (O9), uncovered-fee credit share rising with the count of denials (O9). Unreal: the escrow tier of deposit_carryover (F4). Structurally degenerate: prompt_settlement_allowance under its own prerequisite edge (F3).

### findings

**F1 — SOURCE-POLICY RED (charter-global; consequence demonstrated in 1.md, observation in 0.md).** Allowance-reduced payments are never booked against the invoice, contradicting the base's "paid in full" terminal semantics.
- Symptom: both payment policies compute a payment smaller than the open invoice by allowance rates/credits, and the payment tools lower `invoice_balance` only by the amount paid; no policy or tool posts the allowance as a credit memo.
- Evidence: base realty_closing_and_escrow "Buyer coverage is confirmed only when the plan invoice is paid in full no later than escrow_payment_window_days calendar days after the sale closes"; extended prepayment "the amount carried is reduced once by that combined rate … the result is rounded to the cent as the direct payment"; prepay tool body `balance = … - amt` (task_tools.py, prepay_plan_invoice_by_card_13fdf553). Base realty_failed_sale_charges "The charge is billed to the seller and due failed_sale_bill_due_days calendar days after billing" vs extended settlement "the open failed-sale balance is reduced once by that combined rate … the missed-contact service credit is then subtracted … the settlement amount due".
- Root cause: realty_ext_buyer_direct_prepayment and realty_ext_seller_settlement_payment declare `overwrite: []` while changing how much of a base-billed invoice the customer must pay; the base terminal rule is neither overwritten nor reconciled.
- Bears on: task 1 (demonstrated there), task 0 (ledger residue; observation there).

**F2 — SOURCE-POLICY RED (charter-global undeclared override; consequence demonstrated in 1.md).** deposit_carryover vs base credit-balance refund.
- Evidence: base realty_cancellation_and_credits "Any credit balance is refunded within refund_processing_days calendar days to the party that paid the invoice"; extended prepayment "payments already made on the order, including payments toward invoices later credited for a plan change, count against the open plan premium: when such earlier payments were made by the buyer and none through escrow, the open plan premium is reduced by the whole of those buyer payments". realty_ext_buyer_direct_prepayment has `overwrite: []` and does not list realty_cancellation_and_credits in `base_policy_refs`; no extended policy names this sentence.
- Consequence: a payment made on an invoice later credited for a plan change leaves a credit balance that base refunds to the payer and extended applies to the new premium — two answers for the direct payment whenever such a payment exists.
- Bears on: task 1.

**F3 — SOURCE-FACTOR RED (charter-global structure; consequence demonstrated in 0.md).** prompt_settlement_allowance cannot vary on any task that instantiates its policy's prerequisite edge.
- Evidence: rule "The prompt settlement allowance is a rate counted from the billing date of the failed-sale charge to the day the seller settles: settled no more than prompt_upper_days calendar days after billing, the rate is prompt_upper_rate"; compute `billed_on: LATEST('realty_billing_entries','entry_date', …, event_type='realty_seller_service_charge')`, `days_since_billing: DAYS(billed_on, NOW)`. The policy's own edge requires the failed-sale charge to be unbilled at the opening, and bill_failed_sale_charge_3e9b31c4 stamps `entry_date = ctx.now()[:10]`.
- Consequence: on every world where the edge bears (charge unbilled at the opening), days_since_billing = 0 and the tier is prompt_upper_rate for every customer who reaches this write; the tier rests on the gold write's date stamp, not on seeded records; the factor has no near-miss of its own. Struck out, the settlement computation keeps 3 factors (< 4).
- Bears on: task 0.

**F4 — SOURCE-FACTOR RED (charter-global; bears on task 1's computation).** deposit_carryover's escrow tier is an unreal treatment.
- Evidence: ladder tier "any earlier payment on the order came through escrow → the open plan premium less all earlier payments net of one escrow_return_fee"; rule "the open plan premium is reduced by all those earlier payments less one escrow_return_fee for returning the escrow funds". The policy covers only a buyer-only order still before closing ("pay the plan premium of a buyer-only order directly by card before closing instead of through escrow").
- Why unreal: in US closings the escrow/title company pays the home-warranty premium from closing funds at closing; it does not disburse the premium on an order still awaiting closing. And the tier charges a fee "for returning the escrow funds" while the same funds are being kept and applied to the premium — a self-contradictory treatment no warranty company would publish. With this tier struck, the ladder has two real tiers (< 3), so deposit_carryover does not count, and the prepayment computation keeps 3 factors (< 4).
- Bears on: task 1 (deposit_carryover is one of its prepayment computation's four declared factors; the task's buyer sits on the buyer-payment tier, so only the ladder's validity is in question, not its weight).

**Observations (no demonstrated consequence)**
- O1 Blueprint `products/realty.yaml` line 22 flow mapping `{… means: The ordering agent cancels a buyer-only order before closing, or the order lapses unclosed.}` parses into a truncated `means` and a stray key `"or the order lapses unclosed.": null` (copied verbatim into the extended file, lines 55–56). Base-scope defect, not of this difficulty.
- O2 Direct card prepayment before closing deviates from base "payable through escrow at closing" without an overwrite; channel only.
- O3 Tool docstrings carry the bill→pay order in temporal clauses ("when paying", "when the charge was billed").
- O4 uuid8s a1a6aa51 / a1bc9266 share the prefix `a1`.
- O5 settlement `compute_basis.result` quotes the baseline sentence, not the installment binding.
- O6 compute's waiver lower tier adds `kept_home_monthly > 0`, unstated in the rule (never bites).
- O7 rider premium scope ("billed to the buyer on optional coverage riders") admits a narrower per-order reading.
- O8 hvaccare is labelled `cross_difficulty` but no difficulty of this blueprint claims hvaccare; each tree still has a genuine cross-difficulty factor (homeplan/lineplan; homeplan/addon/landlord).
- O9 after-hours rate per emergency falls with more emergencies (110 → 85); uncovered-fee credit share rises with more denials — unusual, not shown to be unpublishable.
- O10 Prerequisite realism: both trees rest on a back-office step left undone for weeks (failed-sale charge unbilled 63 days after cancellation; plan changed and old invoice credited 12 days before frozen_time with no replacement invoice, although base issues both together). No billing deadline in the charter is broken, so this is recorded and not red-lit.

## closing_checklist

Written after both reveals (2026-10-12T13:41Z). The difficulty does **not** close: the four relationships do not all PASS.

- Per-task files correspond one-to-one with tasks (0.md, 1.md) alongside this file; first revision, no older revisions.
- Coverage and scopes: charter_scope task 0 = {realty_ext_failed_sale_charge, realty_ext_seller_settlement_payment} with {bill_failed_sale_charge_3e9b31c4, pay_failed_sale_charge_by_card_a1a6aa51}; task 1 = {realty_ext_reissued_plan_invoice, realty_ext_buyer_direct_prepayment} with {reissue_plan_invoice_a1bc9266, prepay_plan_invoice_by_card_13fdf553}. Pairwise disjoint, jointly cover all four extended policies and tools. uuid8s independent (O4 observation only).
- Trees: each task has 1 prerequisite problem, 1 value_input edge, an owner=user root write, no cycle; the difficulty graph is two disjoint 2-node chains (acyclic). PASS in both tasks.
- Factors: task 0 failed-sale computation PASS (5 factors, all bear weight, honest baselines, fall-back 1495.00 ≠ 772.37); task 0 settlement computation RED (F3 — 3 surviving factors); task 1 reissue computation PASS (4 factors, fall-back 970.00 ≠ 827.50); task 1 prepayment computation RED (F4 — 3 surviving factors).
- Policy self-consistency: task 1 RED (F1, F2); task 0 PASS with F1 as observation.
- Unique solution: task 0 PASS (GT 772.37 / 2026-10-15 / 350.74 = blind derivation); task 1 not determinate (592.99 vs 781.99 vs 627.50).
- Gate re-run on the final form: not applicable — no artifact changed during this audit, and the skill forbids running the gates in the audit; the coordinator's snapshot stands as cited.

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS (F1 observation) | PASS | SOURCE-FACTOR RED (F3) | PASS | SOURCE-FACTOR RED |
| 1 | SOURCE-POLICY RED (F2, F1) | PASS | SOURCE-FACTOR RED (F4) | not determinate | SOURCE-POLICY RED + SOURCE-FACTOR RED |

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2, same independent auditor. Freeze written before either round-2 task JSON was opened.
- Shared inputs moved, so every charter-global section is re-derived in full (not carried forward): `realty.extended.yaml` 8c44623a… → fcb6d29bd117a1ee9ced6eb87d5204537da4ed186fa434abd3dd2fb1420b5636; `task_tools.py` 62683755… → b52e2f1612e537fc51ff504ae3f2e1fdedb80dca4bdf4aaf1e5abc484b079e08 (both re-verified on disk). Masked views 0.view.json 0e1c527f…, 1.view.json b70788a2… (re-verified; same mechanical division).
- Entry conditions: round-2 gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY only the 4 pre-docs unlock misses). Cited, not re-run.
- contamination_disclosure: the auditor read round-1 GT of both tasks during round 1. The round-1 conventions for the parts of the charter that did not change (failed-sale cap proration, maintained-system credit, keep-home waiver, reissued-premium factors) are therefore known to the auditor; the derivations of those parts below are re-derivations, not strictly blind. The reworked parts (after-hours rate, missed-contact credit placement, the whole settlement down-payment/installment computation, the whole direct-card-limit computation) and all round-2 GT were unseen at freeze.

### policy_conflict_scan (revision_2)

- Base copy: base section still parses identical to `blueprint/products/realty.yaml` (equality True). O1 (malformed transition in the base) unchanged — coordinator-logged BLUEPRINT-KNOWN.
- Extended set unchanged in shape: failed_sale_charge → bill_failed_sale_charge_3e9b31c4; seller_settlement_payment → pay_failed_sale_charge_by_card_a1a6aa51; reissued_plan_invoice → reissue_plan_invoice_480f4e9f (renamed); buyer_direct_prepayment → prepay_plan_invoice_by_card_13fdf553. Two disjoint trees, no shared quantity. Settlement now scoped to "a seller who asks to spread a failed-sale charge"; prepayment now a capped partial card payment with the rest through escrow at closing.
- Terminal-state semantics now reconciled with base: the seller's open balance is scheduled (down payment + first installment now, equal monthly installments from the charge's due date, declared overwrite of the base due-date sentence); the buyer's unpaid remainder stays open and is paid through escrow at closing (declared overwrite of "payable through escrow at closing"), so base "paid in full … after the sale closes" is met by escrow. No allowance is subtracted from what is owed without being booked. Round-1 F1: closed.

### rule_compute_equivalence (revision_2)

- failed_sale_charge: after_hours_rate (hvac trade present → hvac_after_hours_rate; emergencies none hvac → general; none → 0) quoted and implemented; missed-contact credit moved here, quoted and implemented; uncovered-fee credit removed from rule, compute and factors together; waiver lower tier no longer adds an unstated `> 0` (O6 closed).
- seller_settlement_payment: open_balance, homeowner_returned + line_returned (returned_payment charges on both ledgers, 12 months to NOW), standing_share, tenure (MX of whole months since the first active line plan's and first active homeowner contract's start — "earliest-started … in status active"), autopay_relief (line plan billing_channel ach / card / other), down_share floored, down_payment, split_cents, first_installment (3-way / 2-way / whole on the open balance bands with no earlier seller payment), result = down + first installment. Every binding quoted; `compute_basis.result` now quotes the binding it describes (O5 closed). Minor: CFIELD takes the first active holding of each category, the rule says the earliest-started; equal when the customer holds one active plan per category (observation R2-O2).
- reissued_plan_invoice: unchanged except rider premium now read on the order's own rider (`addon_rider_id=order_rider_id`), matching the rule's "premium billed on that rider" (O7 closed).
- buyer_direct_prepayment: open_plan_invoice, buyer_paid, premium_owed floored, card_paid (card payments on the order), largest_card_payment, order_age_days, limit_basis 3-way, rental/lead/autopay increments, card_limit floored, result = lesser of owed and limit. Every binding quoted and every rule tier implemented.
- No invented basis, no empty promise. PASS.

### action_binding_and_uuids (revision_2)

- Four (target_tool, amount) pairs, one claimant each. Tool bodies: unconditional writes; no status/order/existence checks; no refusal (task_tools.py unchanged in logic).
- Docstrings: the bill→pay temporal clauses are gone (bill: "returned in the receipt"; pay: "as shown on the failed-sale charge in the plan's billing history"); prepay: "any part of the invoice not paid this way stays open on it" — states the tool's own effect, names no other action (O3 closed).
- uuid8s 3e9b31c4, a1a6aa51, 480f4e9f, 13fdf553: distinct, no shared prefix or tail (O4 closed).

### prerequisite_graph and prerequisite_sentences (revision_2)

- Graph unchanged: settlement → failed_sale, prepayment → reissue; value_input, state form, no fallback; acyclic. `resolved_by` updated to reissue_plan_invoice_480f4e9f. `policy_source` sentences verbatim in their own rules; `condition`s unchanged and of equal strength; gates `failed_sale_billed`, `plan_invoiced` are real bindings.
- Four-point test passes on both sentences; single resolving write each (only bill_failed_sale_charge_3e9b31c4 creates a realty_seller_service_charge row; only reissue_plan_invoice_480f4e9f creates a realty_invoice row). No new cross-problem order in any rule. PASS.

### override_declarations (revision_2)

- failed_sale_charge: one declared overwrite (lesser-of sentence); replaced_by keeps "seller service call fees already collected never reduce it" — now identical to base for that clause. Unique.
- seller_settlement_payment: declares the base "The charge is billed to the seller and due failed_sale_bill_due_days calendar days after billing", scoped to charges the seller asks to spread; every other charge keeps the base due date. Unique.
- reissued_plan_invoice: three declared overwrites, unchanged. Unique.
- buyer_direct_prepayment: `base_policy_refs` now include realty_cancellation_and_credits; declares (a) "invoiced once per order, payable through escrow at closing" → partial card payment up to the limit on buyer-only orders before closing, rest through escrow; (b) "Any credit balance is refunded …" → a buyer payment on a plan-change-credited invoice of the same buyer-only order stays and counts toward the reissued invoice, every other credit balance still refunded. Round-1 F2: closed. Coverage confirmation ("paid in full … after the sale closes") is not contradicted (escrow pays the rest). Round-1 O2: closed.

### factor_ladders (revision_2)

| Policy | Factor | effect | tiers (outcomes) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| failed_sale | listing_cap_proration | method | daily / months-begun / full | no | — |
| | after_hours_dispatch_recovery | parameter | 95 (hvac emergency) / 70 (emergencies, none hvac) / 0 | yes (emergency requests AND their trade) | — |
| | maintained_hvac_credit | parameter | 0.2 / 0.1 / 0 | yes | null (O8 closed) |
| | missed_contact_service_credit | parameter | 75 / 40 / 0 | no | — |
| | keep_home_waiver | parameter | 0.5 / 0.25 / 0 | yes | homeplan |
| settlement | settlement_installments | method | 3-way / 2-way / not split | yes (no earlier seller payment AND balance band) | — |
| | payment_history_down_payment | parameter | 0.30 / 0.15 / 0 | yes (homeowner AND line ledgers) | lineplan (+homeplan) |
| | coverage_tenure_down_payment | parameter | 0.25 / 0.10 / 0 | yes | lineplan (+homeplan) |
| | autopay_down_payment_relief | parameter | 0.10 / 0.05 / 0 | no | lineplan |
| reissue | plan_reissue_handling / early_ordering_allowance / homeowner_loyalty_credit (method) / rider_bundle_discount | as round 1 | as round 1 | loyalty, bundle | homeplan, addon |
| prepayment | card_limit_basis | method | 0.5 × open invoice / 2 × largest card payment / flat 400 | yes (card payment AND order age) | — |
| | rental_owner_increment | parameter | 150 / 75 / 0 | yes | landlord |
| | clearing_time_increment | parameter | 100 / 50 / 0 | no | — |
| | homeowner_autopay_increment | parameter | 100 / 50 / 0 | no | homeplan |

- Counts: failed_sale 5 (1 method, 4 parameter); settlement 4 (1, 3); reissue 4 (1, 3); prepayment 4 (1, 3). Every ladder ≥3 disjoint tiers with distinct outcomes, stated in the rule and implemented in compute; every fall-through equals the policy baseline; `decides` is an input; labels honest (card_limit_basis changes how the limit is formed: proportional to the invoice / anchored on card history / flat).
- Round-1 F3 (prompt allowance pinned by the edge): the factor is removed; no remaining settlement factor reads the billing date the gold write stamps (returned payments, plan start dates and billing channel are seeded). Closed.
- Round-1 F4 (unreal escrow tier of deposit_carryover): the factor is removed; carry-over is now a declared overwrite, not a ladder. Closed.
- Realism review of the new ladders: higher after-hours recovery when an HVAC emergency was dispatched; down payments on a seller payment plan set by returned-payment history, customer tenure and autopay enrollment; per-order card acceptance limits scaled by card history and order age, raised for established rental and autopay customers and for longer card-clearing lead time before closing — all are credit/fraud-risk treatments a US warranty/servicing business publishes. No unreal tier found. O9 closed (per-emergency rate no longer falls with count; uncovered-fee credit removed).
- Observation R2-O1: the conjunct "no earlier seller payment on the order" of settlement_installments' first two tiers can only be false if the seller paid on the order before the failed-sale charge existed (one charge per order, and the edge requires it unbilled at the opening); within any task carrying this edge it is effectively always true. The tier is still selected by the balance band, which rests on seeded records, so the factor keeps its weight and its count; recorded, not red-lit. (The conjunct was present in round 1 and was not noted then.)

### findings (revision_2)

- Round-1 F1 closed; F2 closed; F3 closed; F4 closed; O2–O9 closed as described above; O10 closed in both seeds (see task files); O1 remains BLUEPRINT-KNOWN (base frozen).
- New charter-global findings: none red. Observations R2-O1 (installment conjunct) and R2-O2 (first vs earliest active holding in tenure).

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-12T18:21Z).
- Per-task files 0.md / 1.md correspond one-to-one with the tasks; revision_1 text untouched; each carries a revision_2 comparison ending in PASS.
- Coverage/scopes: task 0 {failed_sale_charge, seller_settlement_payment} + {bill_failed_sale_charge_3e9b31c4, pay_failed_sale_charge_by_card_a1a6aa51}; task 1 {reissued_plan_invoice, buyer_direct_prepayment} + {reissue_plan_invoice_480f4e9f, prepay_plan_invoice_by_card_13fdf553}; pairwise disjoint, jointly complete; uuid8s independent.
- Trees: 1 prerequisite each, 1 value_input edge each, owner=user root writes, difficulty graph acyclic.
- Factors: every computation 4–5 factors (1 method, ≥3 parameter), ladders ≥3 tiers stated in the rule, distinct and realistic outcomes; every factor bears weight against an honest baseline; fall-backs differ from gold (1495.00, 869.87, 970.00, 200.00 vs the respective gold values); each task has multi-source and seeded cross-difficulty factors.
- Gates: coordinator's round-2 snapshot cited (all OK; TRACEABILITY only the 4 pre-docs unlock misses). The audit changed no artifact.
- Round-1 REDs: F1, F2, F3, F4 closed; no regression; no new RED. Open observations: O1 (BLUEPRINT-KNOWN), R2-O1, R2-O2.

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

The difficulty passes the source-layer audit at revision_2.

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3, same auditor. Frozen at 2026-10-12T20:59:00Z (system clock), before either round-3 task JSON was opened.
- Shared inputs moved, so the charter-global sections are re-derived: realty.extended.yaml → bab40cf1b5488ab0fc6a20023d04608fd902e20f4db4540065034dbfc621dde2; task_tools.py → 89f375911776b3d2b5fc561929289685b04c72ab0e861a2c5c0ef171e45fe009 (both verified on disk). Masked views unchanged (0e1c527f…, b70788a2…, verified), so both worlds are the round-2 worlds.
- Additional input read: audits/render_notes/realty.md (items 1–6).
- Gate snapshot (coordinator, round 3): all OK including TRACEABILITY. Cited, not re-run.
- contamination_disclosure: round-2 GT of both (unchanged) worlds was read in round 2; per-task sections below are re-verifications under the round-3 charter, not blind derivations.

### render_notes items (revision_3)

| item | round-3 source | status |
| --- | --- | --- |
| 1 — reissue overwrite on realty_order_requirements leaves the plan-change right unstated | replaced_by: "The plan ordered may still be changed to another plan at any time before closing, and the invoice is then reissued at the reissued plan premium this policy works out; only such a reissued invoice is priced this way." The right survives verbatim; the scope is stated. Same-class pricing-formula overwrite: replaced_by now restates the full base formula for "every other plan invoice". | closed |
| 2 — refund overwrite drops "(escrow refunds go to the buyer once the escrow file is closed)" | replaced_by ends "…to the party that paid the invoice, and escrow refunds still go to the buyer once the escrow file is closed." | closed |
| 3 — escrow-payment overwrite drops "invoiced once per order" | replaced_by: "The plan premium covers the whole buyer term and is invoiced once per order, a plan change before closing crediting that invoice and reissuing it; …" — restated and reconciled with the reissue policy's own overwrites. | closed |
| 4 — base rule/formula disagreement in realty_cancellation_and_credits | base unchanged (base copy still parses identical to the blueprint); BLUEPRINT-KNOWN. No task of this difficulty computes a buyer cancellation credit. | open, not this difficulty's |
| 5 — "The invoice is due on the closing date" vs reissued invoice due on the expected closing date | new declared overwrite on realty_premium_pricing: "A plan invoice reissued after a plan change before closing is due on the expected closing date shown on the order, and only such an invoice; every other plan invoice remains due on the closing date." Matches the reissue tool body (`due = expected_closing_date`). | closed |
| 6 — card tool docstrings claim a profile card is charged | both card tools now say "records one payment from the {seller,buyer}, with payment method card"; the Args say "recorded exactly as given"; the bodies post a realty_payment row with payment_method "card" and read no card or profile. | closed (residue: see R3-O1) |

### override_declarations (revision_3)

Sweep of every overwrite: each replaced_by restates every still-in-force part of its retired clause and names its scope.
- failed_sale on realty_failed_sale_charges: keeps "no failed-sale charge is billed when the seller-phase benefit paid is zero" and "seller service call fees already collected never reduce it"; replaces only the lesser-of amount.
- settlement on realty_failed_sale_charges: scoped to charges the seller asks to spread; "every other failed-sale charge remains billed to the seller and due failed_sale_bill_due_days calendar days after billing".
- reissue on realty_premium_pricing (formula; plan-change sentence; due date) and on realty_order_requirements: all scoped to the reissued invoice, with the base text restated for every other invoice.
- prepayment on realty_premium_pricing (once per order / escrow) and on realty_cancellation_and_credits (credit balance refunds): scoped, all retained parts restated.
- Remaining base sentences swept against each policy's refs (failed-sale eligibility and dedup, payments applied to the oldest open invoice first, coverage confirmed only when paid in full after closing, invoicing only in listing_coverage/awaiting_closing): followed. No undeclared departure found. Two extended policies overwrite different sentences of realty_premium_pricing; their replacements agree (once per order, a plan change credits and reissues; reissued invoice priced and dated by the reissue policy).

### rule_compute_equivalence, action_binding, prerequisites (revision_3)

- Compute unchanged except settlement_installments: the "no earlier seller payment" conjunct is gone from the ladder and from `first_installment`; the rule instead says "The settlement plan is set up once, before the seller has made any payment on the order, and the first settlement payment is the payment taken when it is set up." Rule and compute agree. Every other binding as in revision_2.
- Tool bodies unchanged in logic; no refusal or prerequisite check; uuid8s unchanged and independent. Docstrings: no other tool named, no ordering word between tools.
- Prerequisite graph and sentences unchanged (verbatim, state form, single resolving write each, acyclic). PASS.

### factor_ladders (revision_3)

- R2-O1 closed: settlement_installments' tiers are now the balance bands alone (above three_installment_floor / above two_installment_floor up to three_installment_floor / otherwise). Every tier condition is a seeded-balance condition that varies across customers. The plan-level "before any payment" sentence is an eligibility of the policy, not a tier.
- Effect on counts: settlement_installments is no longer multi-source. Settlement keeps 4 factors (1 method, 3 parameter). Multi-source factors remain in both trees: failed-sale/settlement tree has maintained_hvac_credit (agreement AND visits), keep_home_waiver (order end date AND homeowner start/tier), payment_history_down_payment (homeowner AND line ledgers), coverage_tenure_down_payment (line AND homeowner holdings); reissue/prepayment tree has homeowner_loyalty_credit, rider_bundle_discount, card_limit_basis, rental_owner_increment. Cross-difficulty factors unchanged (homeplan, lineplan; homeplan, addon, landlord). Requirement still met.
- All other ladders unchanged from revision_2. PASS.

### findings (revision_3)

- Render-notes items 1, 2, 3, 5, 6 closed. Item 4 is BLUEPRINT-KNOWN (base frozen). R2-O1 closed. R2-O2 still open (observation). O1 unchanged (BLUEPRINT-KNOWN).
- New observation R3-O1: in the Returns sections of both card tools, "amount is the amount charged in USD" survives. The body records the amount and charges nothing. This is the same class as item 6 but only in the description of the return value. It changes no argument, owner or scored value.
- No new RED.

### closing_checklist (revision_3)

Written after both round-3 reveals (2026-10-12T20:59:24Z).
- 0.md and 1.md correspond to the tasks. revision_1 and revision_2 text is untouched. Each file carries a revision_3 comparison ending in PASS.
- Scopes are disjoint and jointly cover all four extended policies and tools. uuid8s are independent.
- Each task's tree has 1 prerequisite, 1 value_input edge and an owner=user root write. The graph is acyclic.
- Every computation has 4–5 factors (1 method, ≥3 parameter), and every factor bears weight against an honest baseline. Each tree has multi-source factors and seeded cross-difficulty factors (re-checked after the installment conjunct moved).
- render_notes items 1, 2, 3, 5 and 6 are closed. Item 4 is BLUEPRINT-KNOWN. R2-O1 is closed. Every overwrite restates the retired clause's still-in-force parts and names its scope. No undeclared base departure remains. Tool docstrings describe the bodies, except the R3-O1 residue ("amount charged" in Returns).
- Gates: the coordinator's round-3 snapshot is cited (all OK). This audit changed no artifact.

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

The difficulty passes the source-layer audit at revision_3. Open observations: O1 and render item 4 (BLUEPRINT-KNOWN), R2-O2, R3-O1.
