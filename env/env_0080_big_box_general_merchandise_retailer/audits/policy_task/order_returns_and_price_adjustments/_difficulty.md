# Policy-task audit — order_returns_and_price_adjustments / charter-global

## charter_global_frozen

- Freeze time: 2026-10-23T20:55Z (revision_1). Auditor: independent erl-task-policy-audit agent (did not author any artifact of this difficulty).
- Frozen inputs (sha256, identical to the coordinator snapshot `/tmp/erl0080_coord/snaps/order_returns_and_price_adjustments.r1.txt`):
  - `tasks/order_returns_and_price_adjustments/order.extended.yaml` 33d0ff2577a1610dbdcfe97b503dd4e94e16de9b7fa27146443173f9ee992496
  - `tasks/order_returns_and_price_adjustments/task_tools.py` d77e8ea3b327690705208fc822d49e154b93576e4086212d79df4d7a7ad94d34
  - masked views task0 45f58e1a…2896, task1 9ee05a87…b8 (keep only frozen_time, user_scenario, initial_state)
- Entry conditions (cited, not re-run): snapshot lists EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Inputs complete.
- Read: blueprint.yaml, db_schema.json, share_tools.py (tool list), products/order.yaml (base), membership.yaml and plan.yaml (cross-category params/rules), the extended charter, task_tools.py, the two masked views, the coordinator checklists `audits/render_source/XF_recipe.md` and `owner_ruling.md`, and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (to learn SUM/COUNT/LATEST holding scoping, CFIELD first-match and XLATEST tie rules).
- Masked / not read before every task's freeze: tasks/*.json (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents), worklog.md, plan.md (never read), any other difficulty's tasks/ or audits/.
- Scratch (re-checkable): `/tmp/erl0080_audit_order/{calc.py,t0.py,t1.py,sweep.py,probes.py,hist.py}` — they evaluate the charter's own `compute` with the gate's DSL functions on the views and on probe copies.
- Nothing in this section derives from any revealed GT.

### policy_conflict_scan

Extended policies (6): `order_ext_late_change_fee` (root, owner=user tool `reschedule_large_item_delivery_d930ab59`), `order_ext_missed_appointment_credit`, `order_ext_replacement_haul_away_credit`, `order_ext_late_fee_goodwill_refund` (its three prerequisites), `order_ext_drive_up_return_refund` (root, owner=user tool `return_item_at_drive_up_b4cf62ab`), `order_ext_late_express_credit` (its prerequisite).

- Base copy: lines 1–942 of the extended file are byte-identical to `blueprint/products/order.yaml` (diff shows only the trailing blank line). Base verbatim: PASS.
- Overlapping subjects: the four fee-credit policies all write `order_refund_charge` with reason `fee_refund`, each on a different `fee_type` row (large_item_delivery / haul_away / late_cancellation / express_delivery); all four retire the same base sentence of `order_evt_fees` ("A fee is refunded only as stated in order_returns and order_fulfilment_and_cancellation.") and each `replaced_by` limits itself to its own fee and sends every other fee to "the rule written for that charge" — compatible, no two policies price the same fee row.
- Late-change vs base cancellation: the late-change `replaced_by` keeps cancellations under the program's late cancellation fee; reschedule and cancel subjects do not collide.
- Drive-up return vs base `order_returns`: scoped by a self-naming record test ("a changed-mind return, made with a receipt at a store's Drive Up, of the whole of the one electronics-class line of a Same-Day Delivery order"); every other return keeps the base refund restated verbatim. Same-Day `return_methods` = [in_store, drive_up, mail], so the Drive Up channel is a base channel.
- Cross-category read boundaries: replacement credit reads plan settlements (XLATEST, customer-scoped); drive-up reads membership (CFIELD/CPARAM first match). Conflicts with other charters: see F7 (membership_delivery_benefit) below.
- Terminal states / time anchors: no conflict found beyond the findings below.
- Scope partition (from the prerequisite graph; the masked `charter_scope` is compared after reveal): tree A = {late_change_fee ← missed_appointment_credit, replacement_haul_away_credit, late_fee_goodwill_refund}; tree B = {drive_up_return_refund ← late_express_credit}. With M=2 the two trees are disjoint and jointly cover all 6 extended policies.

### rule_compute_equivalence

Mechanical sweep (`sweep.py`): every `compute_basis` quotation, every `policy_source`, every `replaced_by` and every `baseline.rule` is verbatim in its policy's `rule`; every `superseded_clause` is verbatim in its base policy. No forbidden substring in task_tools.py; no factor id is a substring of any tool name; uuid8s d930ab59, 73d9a081, 849732e1, 56da608d, 4845a2c0, b4cf62ab.

Reverse sweep (rule sentence -> compute) per policy; every tier sentence of each ladder is a branch of its `decides` binding and vice versa, EXCEPT the following (each is a finding below):

| Policy | Rule words | Compute | Finding |
| --- | --- | --- | --- |
| goodwill | "whose appointment Northgate itself **later** moved" | `northgate_moves = F('reschedule_count') - own_requests` (no timing) | F2 |
| goodwill | "booked as one refund of the most recent late-change fee row" | amount and cap over `SUM(... fee_type='late_cancellation')` of all rows | F3 |
| drive-up | "where a Northgate price drop adjustment stands **on the line**" | `LATEST/SUM('order_events', ..., event_type='order_adjust_price')` over the whole order, no `original_event_id` filter | F4 |
| drive-up | "the sum of its line amounts less the amounts already returned or refunded and less the returned line" | subtracts return lines and item_not_received / item_damaged_no_return refunds only; price adjustments (which "refund part of one line", base event meaning) are not subtracted | F5 |
| drive-up | "a customer whose paid Northgate+ membership …" | `CFIELD/CPARAM('membership', …)` first holding of the customer | F6 |

Other edges probed and found equivalent: late-change `days_ahead <= 0` vs "on the scheduled day itself" differs only for a request after the scheduled date, which the rule's own scope ("down to the scheduled day itself") excludes (observation O4); replacement XLATEST tie = "the one recorded first is read" (matches LATEST keeping the first row); absent settlement -> every plan extra 0.0 (eligibility then fails anyway). Rounding: every result is `RND(x + 0.000000001, 2)` on a sum stated "rounded half up to the cent"; tool bodies use `Decimal.quantize(ROUND_HALF_UP)` in a class static method.

### action_binding_and_uuids

- `(target_tool, computes)`: (reschedule_large_item_delivery_d930ab59, late_change_fee_usd), (credit_missed_appointment_73d9a081, credit_amount_usd), (credit_replacement_haul_away_849732e1, credit_amount_usd), (refund_late_change_fee_56da608d, refund_amount_usd), (return_item_at_drive_up_b4cf62ab, refund_amount_usd), (credit_late_express_4845a2c0, credit_amount_usd) — each claimed by exactly one policy. PASS.
- uuid8s are six unrelated hex strings, no shared prefix or sequence. PASS.
- Docstrings: the only ordering words are "at once" and "after this change / after the credit" describing the call's own effect; no tool names another tool or a position in a sequence. PASS.
- Every write tool calls ctx.create/ctx.update in its own body; fee tools check the fee row is a row of that order with the right fee_type; the return tool checks the line is a line of that order; no tool checks any prerequisite. PASS.
- Triggers: tools write payment_method_type `external_card`, refund_method `original_payment`, fee_waiver_source `none`, no plan_id -> none of the base `triggers` (card_post_credit, gift_issue_card, plan_cancel, membership_benefit_use) fires. PASS.
- Owner ruling: the two owner=user tools are the customer's own reschedule (blueprint: "rescheduling a delivery … are the customer's own decisions recorded as requests and confirmed by the customer") and a return the customer initiates — both ruling (a). PASS.
- Observation O1: every tool hard-codes `payment_method_type="external_card"` and its docstring says "the external payment card that paid the order", while the four fee-credit rules and the late-change rule say "to the tender that paid it" / "paid by the tender on the order". On a Northgate-Card-paid order no tool books the rule's tender. Not engaged in either world (both orders external_card).

### prerequisite_graph

| Edge | problem | kind / gate | form | resolved_by = problem's target_tool | gate binding exists | policy_source in own rule |
| --- | --- | --- | --- | --- | --- | --- |
| A late_change ← missed | order_ext_missed_appointment_credit | value_input / notice_charge | state | yes | yes | yes |
| B late_change ← haul | order_ext_replacement_haul_away_credit | value_input / crew_charge | state | yes | yes | yes |
| C late_change ← goodwill | order_ext_late_fee_goodwill_refund | value_input / repeat_surcharge | state | yes | yes | yes |
| D drive_up ← late_express | order_ext_late_express_credit | value_input / restock_relief | state | yes | yes | yes |

Every policy has `prerequisite` filled (`[]` on the four leaves); no edge points at a base policy or at itself; graph acyclic (depth 1); no `fallback_reason` (all state form); no authoring-viewpoint wording. Condition vs sentence strength: edges A and D match; **edges B and C carry a `condition` weaker than their sentence** (F2).

### prerequisite_sentences

Four-point test:

- A "The late-change fee is fixed only after the records carry the missed-appointment credit owed on the large-item delivery fee for an order on which Northgate itself moved an appointment." — connective "only after"; state = a credit carried on the delivery-fee row; no tool/id/snake_case; the only write of this difficulty that books a refund on a large_item_delivery fee row is `credit_missed_appointment_73d9a081`. Derivation: sentence -> missed-appointment rule ("booked as one refund of that fee with reason fee_refund") -> that write. Single reading. PASS (subject to F9 for 0.00 worlds).
- B "The late-change fee is not fixed until the records carry the replacement haul-away credit owed on the haul-away charge of an order bought to replace an appliance settled under a Northgate Protect claim." — connective "not … until"; single resolving write. But "bought to replace" is a fact no record holds, and the condition says "whenever the customer has a Northgate Protect claim settlement recorded" (F2).
- C "Before the late-change fee is fixed, the records must carry the late-change goodwill refund owed on a late-change fee paid on an order whose appointment Northgate itself later moved." — connective "Before"; single resolving write; but "later moved" is undecidable from the records (F2).
- D "The refund for a changed-mind Drive Up return is not fixed until the records carry the late-express credit owed on the express delivery fee of an order fulfilled on a later calendar day than its order date." — connective "not … until"; single resolving write `credit_late_express_4845a2c0`. PASS (subject to F9 for 0.00 worlds).
- The depended-on rules do not restate the sentences; no rule names another problem's tool or id; no rule states a cross-problem order that grounds no edge (the drive-up "where a Northgate price drop adjustment stands" names a state written by no tool of this difficulty and grounds no edge — correct, it is read from history). PASS.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusion per sentence; sentences that do not touch the policy's quantity are marked n/a):

- **late_change_fee** — fulfilment_and_cancellation: hold/unclaimed n/a; "Cancelling … customer's own decision …" followed (reschedule is likewise recorded as a confirmed request); "can be canceled only while … placed" n/a; canceled-order refunds n/a; "A large-item delivery may be rescheduled before the cutoff, the first … reschedules carrying no fee." **overwritten (declared)**; missing items n/a; fee-refund sentence n/a; returned n/a. evt_fees: standard/express/threshold/benefit sentences n/a; haul-away per old item followed (the crew charge is a component of the late-change fee, booked as late_cancellation, not a haul-away fee); "a large-item order canceled or rescheduled within … carries late_cancel_fee_usd" **overwritten (declared)**; fee-refund sentence n/a. multi_holding: followed (all reads holding-scoped). Gap observation O3: after the overwrite no sentence prices a customer reschedule made before the cutoff beyond the free reschedules (base also left it unpriced) — not engaged.
- **missed_appointment_credit** — evt_fees fee-refund sentence **overwritten (declared)**; fulfilment "The fulfilment fee is refunded … only when …" **overwritten (declared)**; refund_tender: tender order followed for an external-card order; "A refund never exceeds what the order's tenders paid … net of earlier refunds on them" — the rule caps at the gross fee charged; equal when no earlier refund stands on the row (observation O2).
- **replacement_haul_away_credit** — evt_fees fee-refund sentence **overwritten (declared)**; refund_tender as for missed (O2).
- **late_fee_goodwill_refund** — evt_fees fee-refund sentence **overwritten (declared)**; refund_tender net-of-earlier-refunds cap **contradicted, not declared** (F3).
- **drive_up_return_refund** — order_returns: fulfilled-only, window, units sentences restated and followed; "The merchandise refund is the line's net amount per unit …" **overwritten (declared, self-scoped)**; fee-refund-reason sentence followed (changed_mind refunds no fee); refund_tender_rule followed; return_methods followed (drive_up is a Same-Day method); plan cancel / Northgate Cash reversal sentences inherited. no_receipt_limits n/a (receipt). refund_tender: "any Northgate Cash redeemed on the order is restored first … any gift card amount is restored next … the remainder goes to the primary payment method" — the extended rule says the return is "refunded to the external card that paid the line" with no Cash/gift-card first step and no overwrite (F10).
- **late_express_credit** — evt_fees fee-refund sentence **overwritten (declared)**; fulfilment fee sentence n/a (express fee is listed apart from the fulfilment fee in the base fee event); refund_tender as O2.
- Three disguised forms swept (anonymous intermediate, 0/1 multiplier, dropped branch): none found beyond the above.

### factor_ladders

| Policy | Factor | effect | tiers (rule = compute) | multi-source tier | cross_difficulty | reachable tiers on the write's own domain |
| --- | --- | --- | --- | --- | --- | --- |
| late_change | notice_charge_step | method | day-of: delivery fee standing / ≥2 days: none / 1 day: program late fee | no | — | 3 |
| late_change | earlier_fee_surcharge | parameter | ≥ late fee: 20 / >0: 10 / else 0 | no | — | 3 |
| late_change | crew_charge_step | method | haul standing & day-of: haul standing / haul standing & earlier: one-item fee / else none | **yes** (fee rows × scheduled date) | — | 3 |
| late_change | installation_surcharge | parameter | ≥2 units 20 / 1 unit 10 / else 0 | no | — | 3 |
| late_change | own_requests_surcharge | parameter | ≥2 above free 15 / 1 above 5 / else 0 | no | — | 3 |
| late_change | northgate_move_courtesy | parameter | ≥2 moves 30 / 1 move 15 / else 0 | no | — | 3 |
| missed | northgate_moves_extra | parameter | ≥2 moves 40% / 1 move 20% / no move 0 | no | — | **2** (F1) |
| missed | waiting_extra | parameter | ≥14 d 10% / 7–13 d 5% / else 0 | no | — | 3 |
| missed | haul_crew_extra | parameter | ≥2 items 5% / 1 item 2% / none 0 | no | — | 3 |
| missed | order_value_extra | parameter | ≥2000 5% / 1000–2000 2% / less 0 | no | — | 3 |
| missed | own_requests_extra | parameter | ≤ free 10% / free+1 5% / ≥ free+2 0 | no | — | 3 |
| missed | appliance_flat_amount | method | ≥2 units 5×units / 1 unit 7.50 / none 0 | no | — | 3 |
| replacement | settlement_timing_extra | parameter | 0–30 d 40% / 31–90 d 20% / else 0 | no | plan | 3 |
| replacement | settlement_kind_extra | parameter | eGift reimbursement 20% / replacement 10% / else 0 | no | plan | 3 |
| replacement | item_kind_extra | parameter | settled major appliance & order major appliance 10% / other category & order large item 5% / else 0 | **yes** (plan × order lines) | plan | 3 |
| replacement | credited_haul_basis | method | ≥2 items: one-item fee / 1 item: charge before benefits / else: haul-away charged | no | — | **2** (F1) |
| goodwill | goodwill_moves_extra | parameter | ≥2 moves 50% / 1 move 25% / no move 0 | no | — | **2** (F1) |
| goodwill | fee_recency_extra | parameter | ≤7 d 25% / 8–30 d 10% / else 0 | no | — | 3 |
| goodwill | goodwill_crew_extra | parameter | ≥2 items 10% / 1 item 5% / none 0 | no | — | 3 |
| goodwill | installation_standby_amount | method | ≥2 units 2.50×units / 1 unit 4.00 / none 0 | no | — | 3 |
| drive-up | category_restocking_rate | parameter | computers/TV 15% / smart home & video games 10% / else program % | no | — | 3 |
| drive-up | holding_time_addition | parameter | >14 d 5% / 8–14 d 2% / else 0 | no | — | 3 |
| drive-up | return_history_addition | parameter | ≥2 earlier 5% / 1 earlier 2% / none 0 | no | — | 3 |
| drive-up | late_delivery_relief | method | credit stands: half the credit / late & no credit: 2.00 / else none | tier 2 yes | — | 3, but gated (F8) |
| drive-up | adjusted_refund_basis | method | price drop: adjusted price × units / competitor match: net less match / else net | no | — | 3 |
| drive-up | small_order_deduction_step | method | member & below min & no same-day fee standing: small-order fee / … & fee standing: max(0, fee − standing) / else 0 | **yes** (membership × lines × fees) | membership | 3 |
| late_express | lateness_rate_step | parameter | ≥2 d 90% / 1 d 60% / else 40% | no | — | **2** (F1) |
| late_express | basket_size_extra | parameter | ≥75 10% / 35–75 5% / less 0 | no | — | 3 |
| late_express | express_price_extra | parameter | full 10% / reduced >0 5% / else 0 | no | — | **2** (F1) |
| late_express | grocery_standby_amount | method | ≥2 lines 0.75×lines / 1 line 1.00 / none 0 | no | — | 3 |

Declared counts per policy: late_change 6 (2 method), missed 6 (1 method), replacement 4 (1 method), goodwill 4 (1 method), drive-up 6 (3 method), late_express 4 (1 method); each ≥2 parameter. Counts after striking the F1 ladders: missed 5 (pass), **goodwill 3 (<4)**, **late_express 2 (<4)**, **replacement 3 with 0 method (<4, <1 method)**.

Method pairwise tables (distinguishing input/operation per pair; "tariff parameter" counts as an added input per XF A7):

| Factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
| --- | --- | --- | --- |
| notice_charge_step | delivery fee rows − refunds vs none | fee rows vs tariff P(late_cancel_fee_usd) | none vs tariff | 
| crew_charge_step | haul rows − refunds vs tariff P(haul_away_fee_usd) | rows vs none | tariff vs none |
| appliance_flat_amount / installation_standby_amount / grocery_standby_amount | unit/line count × rate vs flat tariff | count vs none | flat tariff vs none |
| credited_haul_basis | tariff vs standard_fee_usd field | tariff vs amount_usd field | standard_fee_usd vs amount_usd (distinct fields) — T3 unreachable (F1) |
| late_delivery_relief | credit rows vs flat tariff | rows vs none | tariff vs none |
| adjusted_refund_basis | adjusted price × units vs net − match amount | adjusted price vs net | match amount vs none |
| small_order_deduction_step | CPARAM fee vs MX(0, fee − standing rows) | fee vs none | max-op over rows vs none |

All labels honest (method tiers change the formula's inputs/operations; parameter tiers change a share or amount). Realism: every condition is one a big-box retailer could weigh for that quantity; no factor value is a straw man except the unreachable fall-throughs of F1. Observations O5 (late_delivery_relief compensates the same lateness twice — the express credit and half of it again as restocking relief) and O6 (missed-appointment waiting extra counts to "the day the credit is worked out", so an owed credit grows with booking delay).

Independence (XF A1/A4): mechanical read-set per factor — no factor binding reads another factor's binding; shared selections (`days_ahead`, `line_amount`, `express_charged`, `haul_charged`) are plain bindings; assembly sentences are generic. T2 (XF A6) holds for every factor except late_delivery_relief (F8).

### findings

**F1 — SOURCE-FACTOR RED (charter-global; bears on task0 and task1). Ladders whose fall-through tier no customer reaching the write can be on.**
- Symptom: five ladders state a fall-through that the policy's own eligibility (or the resolver's positivity) excludes, so each divides the customers who reach the write into two tiers, not three, and the fall-through value (or method) is a treatment the business never gives in that situation (in that situation it gives no credit at all).
- Members (exhaustive sweep of all 30 factors):
  1. missed_appointment_credit.northgate_moves_extra — "no move adds nothing"; rule: the credit is owed only "When Northgate itself moves the delivery appointment" (northgate_moves ≥ 1).
  2. late_fee_goodwill_refund.goodwill_moves_extra — "no move adds nothing"; rule: owed only to a customer "whose appointment Northgate itself later moved".
  3. late_express_credit.lateness_rate_step — "otherwise the standard two fifths apply" (days_late ≤ 0); rule: owed only when "fulfilled date is a later calendar day than its order date".
  4. late_express_credit.express_price_extra — "otherwise nothing is added" (fee charged 0.00): then `result = MN(express_charged=0, …) = 0.00`, which the resolver refuses ("the amount must be above zero"), so no booked credit is ever on this tier; the "charged above its standard" case is excluded by base pricing.
  5. replacement_haul_away_credit.credited_haul_basis — "otherwise it is the haul-away charge on the order" (zero old items); rule applies only to an order "that carries a haul-away charge", and base `order_evt_fees` charges "haul_away_fee_usd … per old item removed", so haul_items ≥ 1.
- Demonstrated consequence: the condition "one or more Northgate moves" / "fulfilled one or more days late" / "fee charged above zero" / "one or more old items booked" holds of every customer who reaches the write, i.e. it restates the policy's scope; the struck ladders leave goodwill with 3 factors, late_express with 2, replacement with 3 and no method factor — below the 4-factor / 1-method floor.
- Affected: order.extended.yaml, the five factors' ladders and the rule sentences quoted above.

**F2 — SOURCE-POLICY RED (charter-global; consequence demonstrated in task0). Rule words for facts no record holds, and edge conditions weaker than their sentences.**
- Goodwill: rule "A customer who paid a late-change fee … and whose appointment Northgate itself **later** moved is owed …" and edge C's sentence "… an order whose appointment Northgate itself later moved". No table dates a Northgate move: `order_holdings.reschedule_count` is a bare counter and `order_requests` records only the customer's own requests (db_schema `order_requests.request_type` ∈ {cancel_order, reschedule_delivery, schedule_return_pickup}). Compute (`northgate_moves = F('reschedule_count') - own_requests`) and edge C's condition ("whenever the reschedule count exceeds the customer's confirmed reschedule requests") both drop "later". The eligibility is therefore undecidable whenever a Northgate move and a paid late-change fee coexist.
- Replacement: edge B's sentence "an order **bought to replace** an appliance settled under a Northgate Protect claim" and the policy's own `replaced_by` ("an order bought to replace an appliance whose Northgate Protect claim was settled") assert an intent no record links (no field ties an order to a settlement); the policy's operative sentence says "placed by a customer whose Northgate Protect plan claim on an old appliance was settled"; edge B's condition says "whenever the customer has a Northgate Protect claim settlement recorded" (any category, any timing). Probe P9 (`probes.py`): settlement dated after the order, on a TV, settled by repair -> compute still owes 7.50 and the condition demands it, while the sentence ("bought to replace an appliance") does not.
- Consequence: see task0 file (second defensible solution). Affected: goodwill rule sentence 1 and edge C condition; replacement replaced_by / edge B sentence and condition.

**F3 — SOURCE-POLICY RED (charter-global; no consequence in task0's world).** Goodwill: "booked as one refund of the most recent late-change fee row …; the late-change fees charged are multiplied once by that percentage …, and the refund never exceeds the late-change fees charged" vs in-force base `order_refund_tender` "A refund never exceeds what the order's tenders paid for the refunded lines and fees, net of earlier refunds on them." (not overwritten). Probe P4: late-change fees 49.00 (10-12) and 15.00 (10-19), one Northgate move -> goodwill computes 59.40 booked against the 15.00 row; the base cap allows at most 15.00 on that row. Two conclusions in one situation.

**F4 — SOURCE-POLICY RED (rule ≠ compute; no consequence in task1's world).** Drive-up `refund_basis`: rule "where a Northgate price drop adjustment stands on the line … where a competitor price match stands on the line …"; compute reads `LATEST('order_events','adjustment_type', event_type='order_adjust_price')` and `SUM(… event_type='order_adjust_price')` over the whole order. Probe P1: a 2.00 competitor match on the towel line, none on the returned line -> compute basis 57.98 (refund 44.59) vs rule basis 59.98 (refund 46.59).

**F5 — SOURCE-POLICY RED (two readings + rule ≠ compute; no consequence in task1's world).** Drive-up `kept_after`: rule "the sum of its line amounts less the amounts already returned or refunded and less the returned line"; base event meaning of `order_adjust_price`: "A price drop adjustment or competitor price match refunds part of one line." Compute omits adjustments. Probe P2: a 10.00 adjustment on a kept line moves kept merchandise from 43.96 (compute, no deduction) to 33.96 (rule, deduction 6.99).

**F6 — SOURCE-POLICY RED (DSL first-match; no consequence in task1's world).** Drive-up membership reads `CFIELD('membership','canceled_date')` / `CPARAM(...)` take the customer's first membership holding; membership.yaml allows re-enrolment ("a customer may re-enroll after it closes"), and no self-naming scope excludes two holdings (XF C19). Probe P3: an older canceled Northgate+ Annual listed first -> compute deduction 0.00 vs rule 6.99 for the current Monthly membership.

**F7 — SOURCE-POLICY RED (cross-charter, XF C18; consequence demonstrated in task1).** Drive-up small-order deduction ("where the kept merchandise is below the membership's free same-day minimum … the deduction is the membership's small-order same-day fee") re-prices the member Same-Day benefit after the order, while membership.yaml `membership_delivery_benefit` reads: "This is the single statement of the membership delivery and return-pickup benefits that apply to Northgate orders. … the Same-Day Delivery fee is waived when the merchandise subtotal is at least same_day_free_min_order_usd … Stacking: membership benefits only waive or reduce delivery and pickup fees and never reduce merchandise prices, so they combine with the Northgate Card discount, item promotions, price adjustments and Northgate Cash without interaction." Under the membership charter the waiver on an order whose subtotal met the minimum is final and nothing in the single statement claws it back from a later merchandise refund; under the drive-up rule the member bears the small-order fee out of the refund.

**F8 — SOURCE-FACTOR RED (XF A1/A6 T2; bears on task1).** Drive-up late_delivery_relief is gated through other factors: the policy is scoped to Same-Day orders, whose `restocking_fee_pct_changed_mind` is 0.0, so with every other factor at baseline the restocking fee is `MX(0, RND(line × 0.0 − relief))` = 0.00 for every relief tier (half the credit, 2.00, none) — no producible world lets this factor move the result on its own; it acts only "once the other tier applies".

**F9 — SOURCE-CHAIN/POLICY RED (XF D20; not engaged in either world).** Zero-amount owed credits on state-form edges: each resolver refuses amounts ≤ 0, each edge `condition` demands a refund row "whenever" its trigger holds, and no de minimis record test is carved out of the wait. Members: edge D — express fee charged 0.00 (base waiver source `promotion`; the charter's own price_extra fall-through contemplates it) -> late-express credit 0.00 (P5); edge A — large-item delivery fee waived -> missed credit 0.00 (P7); edge B — haul-away waived -> replacement credit 0.00 (P8); edge C — a late-change fee booked at 0.00 by the reschedule tool itself (rule "never below zero"; docstring "0.00 when no fee is owed"; e.g. two days ahead, no haul-away, no appliance, one Northgate move -> 0 − 15 -> 0.00) -> goodwill 0.00 (P6). In each such world the root either never becomes fixable (condition reading) or proceeds on a vacuous state (sentence reading) — two readings, one of them blocked.

**F10 — SOURCE-POLICY RED (undeclared override; not engaged in task1's world).** Drive-up: "refunded to the external card that paid the line" vs base `order_refund_tender` "any Northgate Cash redeemed on the order is restored first as Northgate Cash … any gift card amount is restored next … and the remainder goes to the primary payment method". On a Same-Day order where the member redeemed Northgate Cash, base restores the Cash first; the extended rule (and the owner=user tool, which hard-codes external_card) sends the whole refund to the card. No overwrite names `order_refund_tender`.

Observations (no relationship fails on their own): O1 hard-coded external_card tender in every tool; O2 gross-fee caps in the missed / replacement / late-express credits vs base net-of-earlier-refunds cap, and "one refund" left ambiguous for a second Northgate move after a booked credit; O3 reschedule before the cutoff beyond the free reschedules is unpriced after the overwrite; O4 `days_ahead < 0` priced as the scheduled day; O5/O6 realism notes above; O7 late-change `own_requests` is evaluated before the reschedule call records the present request (the call records both at once) — the evaluation-moment convention fixes it, but the rule does not say whether the request being made counts.

## closing_checklist

Written after both reveals (2026-10-23T21:10Z). The difficulty does **not** close in revision_1.

- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this file sits alongside; no older revision exists. Comparison sections: task0 RED, task1 RED — not all PASS.
- Coverage and exclusivity: charter_scope task0 = {late_change_fee, missed_appointment_credit, replacement_haul_away_credit, late_fee_goodwill_refund}, task1 = {drive_up_return_refund, late_express_credit}; pairwise disjoint, jointly all 6 extended policies, each task tool used by exactly one task; uuid8s independent. PASS.
- Problem trees: task0 3 prerequisites / 3 value_input / owner=user root; task1 1 / 1 / owner=user root; difficulty graph acyclic; every edge unmet at the opening and load-bearing (0.md, 1.md problem_chain). PASS on these worlds; charter F2 (edges B and C conditions) and F9 (0.00 worlds) remain open.
- Factors: not met — F1 (five unreachable fall-throughs; goodwill, late_express and replacement fall below 4 factors / 1 method), F8 (late_delivery_relief gated), task0 replacement has no near-miss and its goodwill input rests on an unproducible seeded fee (0.md findings 3–4).
- Unique solution: not met — task0 F2 (53.40 vs 63.40), task1 F7 (42.84 vs 49.83).
- Gate re-run on the final form: not applicable this round (artifacts unchanged since the snapshot; hashes re-checked equal at freeze). Every gold figure in both tasks matched this audit's blind recomputation exactly.

VERDICT revision_1: task0=RED task1=RED charter=F1,F2,F3,F4,F5,F6,F7,F8,F9,F10

## revision_2

### charter_global_frozen (revision_2)

- Freeze time 2026-10-24 (UTC, before any round-2 reveal). Same independent auditor; revision_1 text above left untouched.
- Snapshot executed `/tmp/erl0080_coord/snapshot.sh order_returns_and_price_adjustments 2` (output cited): views task0 69b475af…96ae, task1 adf16c7c…c2b6; `order.extended.yaml` **00a1b16c…b65e (changed)**; `task_tools.py` d77e8ea3…4d34 (unchanged); all blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Reworker claims read: `rework_claims_r2.md` (item ids only); worklog only `tail -1` ("REWORK round 2: gates 7/7 green").
- Because the charter hash moved, every charter-global section is re-derived in full; the tool-module conclusions (§action_binding_and_uuids) are carried forward on the unchanged task_tools.py hash except where a charter sentence they are compared with changed (noted below).
- Base copy: lines 1–942 still byte-identical to `blueprint/products/order.yaml`.
- Mechanical sweep re-run on the new charter (`/tmp/erl0080_audit_order/sweep.py`): every compute_basis, policy_source, replaced_by and baseline.rule verbatim in its rule; every superseded_clause verbatim in its base policy; no factor id inside a tool name; uuid8s unchanged. Round-2 scratch: `r2_t0.py`, `r2_t1.py`, `r2_hist.py`, `r2_probes.py` (round-1 scripts preserved in `r1/`).

### round-1 item closure (charter-global)

| Item | Verdict r2 | Evidence |
| --- | --- | --- |
| F1 unreachable fall-throughs | **closed for 4 of 5; the 5th replaced by a worse defect (F11)** | missed/goodwill moves ladders now "three or more / exactly two / a single move adds nothing" — all three reachable (owed from one move); lateness now "three or more / exactly two / a single day gives the standard half" — reachable; express_price_extra removed, age_check_extra_step (alcohol lines 2+/1/none) reachable. credited_haul_basis fall-through now reachable, but see F11. |
| F2 facts no record holds / weak conditions | closed | goodwill: "on an order on which Northgate itself moved a delivery appointment" (no timing); replacement: "placed on or after the date of the customer's most recent Northgate Protect claim settlement" (record test, same-day settlement counts, lag 0); edges B and C sentence and condition now the same strength. But the broadened replacement eligibility is unreal — N2. |
| F3 goodwill cap vs base cap | closed | goodwill acts on the most recent row (tie: first recorded — matches LATEST) and "never exceeds that fee less every refund already booked against the order's late-change fees" ≤ base net-of-earlier-refunds cap; missed/replacement/late-express caps now on the fee standing. |
| F4 adjustment read | closed | drive-up self-naming scope "every price adjustment stands on that line"; out of scope the base refund is restated. |
| F5, F6, F7 membership deduction | closed | drive-up no longer reads membership; small-order deduction removed. |
| F8 relief gated | closed | baseline restocking is now a stated 10% for this return (declared in the overwrite); with every other factor at baseline the relief tiers give 58.73 / 55.98 / 53.98 (`r2_t1.py`). |
| F9 zero-amount credits | **partly open** | "charged above zero" record tests in all four credit rules and all four edges close edges A, B, D and the round-1 P6 case; one member remains (N3). |
| F10 tender override | closed | drive-up scope "paid with an external card alone, on which no Northgate Cash and no gift card was redeemed"; rule restates the tender rule for that case. |
| O1 tender | closed in the four credit rules ("a credit on any other tender follows the refund tender rule"); **the late-change rule's version opens N1** | |
| O2, O3, O6, O7 | closed | standing caps; free-reschedule branch stated and computed; waiting counted to the scheduled date; "the request being made not counted". O4, O5 unchanged (observations). |

### policy_conflict_scan / override_declarations (revision_2)

Same partition (tree A = late_change ← missed, replacement, goodwill; tree B = drive_up ← late_express); subjects, fee rows and triggers as in revision_1. Sentence-by-sentence sweep repeated on every changed policy; new conclusions:

- late_change: base fulfilment sentence retired with replaced_by "may be rescheduled by the customer at any time down to the scheduled day itself: the program's free reschedules made two or more days ahead carry no fee, and every other reschedule carries the late-change fee this rule sets"; base fees sentence retired with replaced_by "For a customer's reschedule of a Scheduled Large-Item Delivery appointment, and only for such a reschedule, the late-change fee is the amount this rule works out" — **no tender scope**, while the rule now says "paid by the external payment card on file for the order; this rule covers orders paid with an external card" (N1).
- drive-up: the base merchandise-refund sentence is retired for the self-named scope and restated verbatim outside it; the new 10% standard restocking on a Same-Day electronics changed-mind Drive Up return (base Same-Day: 0%, no restocking classes) is inside that declared scope. Tender rule followed for the scope.
- four credit rules: the evt_fees fee-refund sentence remains declared; tender routing stated.

### rule_compute_equivalence (revision_2)

Re-swept every changed binding; rule = compute on: free_reschedule (`days_ahead >= 2 and own_requests < P('large_item_reschedules_free')`), standing caps, `wait_days = DAYS(order_date, scheduled_date)`, goodwill `LATEST(... amount_usd ...)` with the stated tie rule, replacement `settle_lag >= 0` eligibility and ">90 days add nothing", drive-up market XCOUNT "fewer than twelve whole months" (`within_months=12`, MONTHS whole-month convention). Probes on the market read (`r2_t1.py`): absent requests -> 0; a second changed-mind request -> 2; a request exactly 12 whole months before -> excluded; 11 months 30 days -> included; a seller-response row -> excluded; defective request -> excluded. Equivalent.

### prerequisite_graph / prerequisite_sentences (revision_2)

Graph unchanged in shape (4 value_input state-form edges, acyclic, resolvers = target tools). Sentences:
- A "…only after the records carry the missed-appointment credit owed on a large-item delivery fee charged above zero for an order on which Northgate itself moved an appointment." — condition same strength. PASS.
- B "…not fixed until the records carry the replacement haul-away credit owed on a haul-away charge above zero of an order placed on or after the date of the customer's most recent Northgate Protect claim settlement." — condition "whenever the haul-away was charged above zero and the customer's most recent Northgate Protect claim settlement is dated on or before the order date" — same strength. PASS.
- C "Before the late-change fee is fixed, the records must carry the late-change goodwill refund owed on a late-change fee charged above zero on an order on which Northgate itself moved an appointment." — condition "The order's most recent late-change fee row has a refund … whenever a late-change fee above zero stands on the order and …". The sentence keys on a fee charged above zero; the condition and the goodwill rule book the refund on *the most recent* late-change fee row, which may be a 0.00 row (N3).
- D "…late-express credit owed on an express delivery fee charged above zero of an order fulfilled on a later calendar day than its order date." PASS.

### factor_ladders (revision_2)

Changed ladders: missed northgate_moves_extra 3+/2/1 (40/20/0%); goodwill goodwill_moves_extra 3+/2/1 (50/25/0%); replacement settlement_timing_extra 0–30/31–90/>90; credited_haul_basis 2+ items: one-item fee / 1 item charged below pre-benefit: pre-benefit charge / otherwise: haul charged; drive-up category 15/5/10% (fall-through = standard 10% = baseline), marketplace_return_addition (market, 2+/1/0 → 5/2/0%), late_delivery_relief tiers now conjunctions (fulfilled late AND credit stands / fulfilled late AND none) — multi-source; late_express lateness 3+/2/1 day (90/70/50%), age_check_extra_step (2+/1/0 alcohol lines → 10/5/0%). Counts: late_change 6 (2 method), missed 6 (1), replacement 4 (1), goodwill 4 (1), drive-up 6 (2: relief, basis), late_express 4 (1). Every fall-through reachable inside its policy's scope. Pairwise method tables as revision_1 plus: relief T1 (credit rows) vs T2 (tariff) vs T3 (none) — distinct; credited_haul — see F11.

### findings (revision_2, charter-global)

**F11 — SOURCE-FACTOR RED (present since revision_1, missed by that audit; bears on task0).** credited_haul_basis: all three tiers select the same amount on every reachable input. Base charges "haul_away_fee_usd … per old item removed" (25.00 on Scheduled Large-Item Delivery, the only program with haul-away), so tier 1 = P(haul_away_fee_usd) = 25.00; tier 2 (one item, charged below pre-benefit) = haul charge before benefits = 1 × 25.00; tier 3 (one item at full charge) = haul charged = 25.00. `r2_probes.py`: items/charged (1, 25.00), (1, 12.50), (1, 0.01), (2, 50.00), (2, 30.00), (3, 75.00), (4, 100.00) → credited haul 25.00 every time. The ladder is one value written as three tiers; the factor is struck, leaving the replacement computation 3 factors and no method factor (<4, <1 method). (In revision_1 tiers 1 and 2 already coincided at 25.00; that audit failed to report it.)

**N1 — SOURCE-POLICY RED (new in round 2; not engaged in either world).** late_change rule "paid by the external payment card on file for the order; this rule covers orders paid with an external card" vs its own replaced_by of the retired base fee clause "For a customer's reschedule of a Scheduled Large-Item Delivery appointment, and only for such a reschedule, the late-change fee is the amount this rule works out". On a Northgate-Card-paid large-item order rescheduled inside the cutoff beyond the free reschedules: reading 1 — the replaced_by applies, the fee is this rule's amount (charged to the card); reading 2 — the rule does not cover the order and the retired base clause is not restated for it, so no fee rule exists (handoff). XF C16: the out-of-scope case is neither restated nor routed.

**N2 — SOURCE-FACTOR RED (realism, introduced by the F2 fix; not engaged in task0's world).** The replacement haul-away credit is now owed on any haul-away order "placed on or after the date of the customer's most recent Northgate Protect claim settlement", whatever the item, method or age of that settlement. In the all-fall-through situation the business still pays the standard quarter: `r2_probes.py` — only settlement a 2023 repair of a tablet, a 2026 sofa order with one haul-away item → "replacement haul-away credit" 7.50, though nothing was replaced. No retailer publishes a replacement credit for customers who replaced nothing; the fall-through world is an invented entitlement (XF F28).

**N3 — SOURCE-CHAIN/POLICY RED (F9 residual; not engaged in task0's world).** goodwill "booked as one refund of the most recent late-change fee row"; the reschedule tool books a late_cancellation row for every reschedule, at 0.00 for a free reschedule (rule: "is a free reschedule and carries no late-change fee"; docstring "0.00 when no fee is owed") or a computed 0.00 fee. Producible sequence: a paid 79.00 late change, then a free reschedule two or more days ahead (own requests below the free count) booking a 0.00 row, then a Northgate move, then the customer reschedules again. Edge C's condition is engaged ("a late-change fee above zero stands … reschedule count exceeds …") and demands a refund on the most recent row, the 0.00 row; goodwill there computes 0.00 (`r2_probes.py`), which `refund_late_change_fee_56da608d` refuses — the root can never be fixed, while the sentence ("owed on a late-change fee charged above zero") points at the 79.00 row. Two readings, one blocked.

Observation O8 (new): task0's seeded 79.00 late-change fee of 2026-10-19 is producible by the charter (`r2_hist.py`: one prior Northgate move, appointment then on 2026-10-20 → 79.00), but at that moment the charter's own edges A and B already required the missed-appointment and replacement credits to stand before the fee was fixed; the history shows the fee without them. This is the task's own premise (owed credits never booked), so no relationship fails.

### closing_checklist (revision_2)

- Files: 0.md, 1.md and this file each carry revision_1 untouched and an appended revision_2; frozen before reveal (hashes in 0.md). task0 RED, task1 PASS — the difficulty does not close.
- Scope: charter_scope task0 = {late_change, missed, replacement, goodwill}, task1 = {drive_up, late_express} — disjoint, complete; tools one-to-one; uuid8s unchanged and independent. PASS.
- Problem trees: task0 3 prerequisites / 3 value_input / owner=user root; task1 1 / 1 / owner=user root; acyclic; every edge unmet at the opening and load-bearing. PASS (charter N3 remains a producible blocked world for edge C).
- Factors: task1 PASS; task0 fails on F11 (replacement computation 3 factors, 0 method after striking credited_haul_basis); charter N2 (realism of the replacement entitlement).
- Unique solution: both tasks PASS this round.
- Gate re-run: the coordinator's round-2 snapshot (all 7 green) is on the current hashes; every gold figure of both tasks matched this audit's blind recomputation.
- Nothing regressed in task1; in tree A the F2 fix introduced N2, the O1 fix introduced N1, the O3 free-reschedule branch exposed N3; F11 is an old defect first reported now.

VERDICT revision_2: task0=RED task1=PASS charter=F11,N1,N2,N3

## revision_3

### charter_global_frozen (revision_3)

- Freeze 2026-10-24T13:50:01Z, before any round-3 reveal; revisions 1–2 above untouched.
- Snapshot executed `/tmp/erl0080_coord/snapshot.sh order_returns_and_price_adjustments 3` (output cited): views task0 69b475af…96ae and task1 adf16c7c…c2b6 (both unchanged from round 2); `order.extended.yaml` **0d44ca7f…5b75 (changed)**; `task_tools.py` **d239f0b3…efc7 (changed)**; blueprint products unchanged; 7/7 gates green. Claims: `rework_claims_r3.md`; worklog `tail -1` = "REWORK round 3: gates 7/7 green".
- Both shared inputs moved, so every charter-global section is re-derived. Base copy still byte-identical; mechanical sweep (`sweep.py`) clean (quotes verbatim, no factor id in a tool name, no forbidden substring, uuid8s unchanged). Tool change: `reschedule_large_item_delivery_d930ab59` books no fee row when the fee is 0.00 (body and docstring agree); the other five tools unchanged in effect (all still hard-code external_card). Round-3 scratch: `r3_dump.txt`, `r3_probes.py`; `r2_t0.py`/`r2_t1.py` re-run on the round-3 charter.

### round-2 item closure

| Item | r3 | Evidence |
| --- | --- | --- |
| F11 credited_haul tiers coincide | closed | tiers now 25 × min(matched settlements, old items) / 25 / haul charged; `r3_probes.py`: (matched 2, items 3) → 50.00 vs charged 75.00; (matched 1, items 2) → 25.00 vs 50.00; (items 1 discounted) → charged — distinct on producible orders. But see N5. |
| N1 late-change scope vs replaced_by | closed | both replaced_by sentences scope to external-card orders and restate the base content for Northgate-Card orders (before-cutoff free reschedules; late cancellation fee within the cutoff); same restatement in all four credit rules; edge conditions name external-card orders. But see N4. |
| N2 replacement entitlement | closed | owed only after a replacement or reimbursement of an item of a category the order carries, settled 0–90 days before the order date, haul-away above zero; repair, food-loss, other-category and out-of-window settlements owe nothing (probes: 91 days → 0.00; after the order date → 0.00; same-day tie with a repair recorded first → the repair is read → 0.00, as the tie sentence states). Edge B sentence/condition same test. |
| N3 0.00 late-change row | closed | the tool books no row at 0.00; goodwill reads "the latest late-change fee row with an amount above 0.00"; edge C names the same row. |
| O8 | observation kept | |

### re-derived sections (revision_3)

- policy_conflict_scan: same two trees, disjoint and complete; no new subject overlap.
- rule_compute_equivalence: replacement `in_scope` = rule's owed test (method ∈ {replacement, reimbursement_egift_card}, category on the order, lag 0–90, haul charged > 0); timing 0–30/31–60/61–90 → 40/20/0%; kind major appliance / furniture or fitness / other → 20/10/0%; value ≥1000 / 500–1000 / less → 10/5/0%; matched settlements = XCOUNT over 6 whole months before the working day, replacement + reimbursement, same category (probes: a second same-category reimbursement inside 6 months → 2; one 7 months back → excluded; food-loss → excluded; other category → excluded). Goodwill LATEST unchanged (every row > 0.00 by tool). Equivalent.
- prerequisite_graph / sentences: four state-form value_input edges, acyclic, each resolved by its policy's target tool; A, B, C, D sentences and conditions at the same strength (external-card qualifier in A–C matches the root's scope). PASS.
- factor_ladders: counts late_change 6 (2 method), missed 6 (1), replacement 4 (1 method: credited_haul_basis; timing, kind, value parameters; three plan cross-difficulty), goodwill 4 (1), drive-up 6 (2), late_express 4 (1). Every tier reachable. Multi-source: crew_charge_step, credited_haul_basis (plan × order), late_delivery_relief.

### findings (revision_3, charter-global)

**N4 — SOURCE-POLICY RED (XF C18 "one price whatever pays"; introduced by the round-2 F10 scope and the round-3 N1 restatement — the drive-up member existed in round 2 and that revision missed it; not engaged in either world).** Every extended policy now prices the same event differently by tender, while card.yaml `card_cardholder_benefits` reads "This is the single statement of the Northgate Card benefits that apply to Northgate purchases" and lists only the discount, free standard shipping and extra return days. Exhaustive members:
1. late_change (both replaced_by): external card → this rule's fee; Northgate Card → the base late cancellation fee within the cutoff. Task0's records with a Northgate-Card tender: 49.00 instead of 39.65.
2. missed_appointment_credit (both replaced_by): Northgate Card → no credit (41.85 on the same records).
3. replacement_haul_away_credit: Northgate Card → no credit.
4. late_fee_goodwill_refund: Northgate Card → no refund.
5. late_express_credit: Northgate Card → no credit.
6. drive_up_return_refund scope "paid with an external card alone, on which no Northgate Cash and no gift card was redeemed": Northgate Card, or any Northgate Cash / gift card redemption → base refund with no restocking. Task1's records with a Northgate-Card tender: 53.98 instead of 52.13.
A card-paying customer is charged a different reschedule fee, denied four credits and spared a restocking fee — card benefits and penalties stated outside the card charter's single statement.

**N5 — SOURCE-FACTOR RED (realism and the rule's own framing; not engaged in task0's world).** replacement: "is owed a replacement haul-away credit for the old item the claim settled" and credited_haul counts matching settlements "dated fewer than six whole months before the day the credit is worked out". Inside the owed scope (settlement 0–90 days before the order) the fall-through "otherwise it is the haul-away charge on the order" with two or more old items is reached only when the credit is worked out more than six months after the settlement, and there it credits every old item. `r3_probes.py`: task0's records, credit worked out 2026-10-24 → 22.50; the same records worked out 2027-05-01 → 45.00 (a placed order still waiting on its delivery). Booking the owed credit late doubles it, against the rule's own "for the old item the claim settled"; no business pays more for a credit it books late.

Observation O9 (exhaustive pass on working-day anchors): goodwill fee_recency_extra counts "to the day the refund is worked out" (since revision_1; an owed refund shrinks with booking delay — 25% → 10% → 0%). Every other date read is anchored on the transaction's own date (drive-up return date, request day, scheduled date, order/fulfilled dates). Kept as an observation, same class as O6.

### closing_checklist (revision_3)

- Files: each carries revisions 1–3; revision_3 frozen before reveal (hashes in 0.md). task0 PASS, task1 PASS; every gold figure matched the blind recomputation.
- Scope disjoint and complete; tools one-to-one; uuid8s independent. PASS.
- Problem trees: task0 3 / 3 value_input / owner=user root; task1 1 / 1 / owner=user root; acyclic; edges unmet and load-bearing; tools judge nothing. PASS.
- Factors: every computation 4–6 factors with ≥2 parameter and ≥1 method, every tier reachable and distinct, honest baselines, near-misses present, multi-source and cross-difficulty in each task. PASS on both worlds; charter N5 open.
- Unique solution: PASS in both tasks.
- Charter: N4 (one price whatever pays — six members across both trees) and N5 (replacement credit doubles when booked late) remain; O9 noted. The difficulty does not close while the charter carries REDs.
- Gate re-run: coordinator's round-3 snapshot, 7/7 green on the current hashes.

VERDICT revision_3: task0=PASS task1=PASS charter=N4,N5

## revision_4

### charter_global_frozen (revision_4)

- Freeze 2026-10-24T18:10:00Z, before any round-4 reveal; revisions 1–3 untouched.
- Snapshot executed `/tmp/erl0080_coord/snapshot.sh order_returns_and_price_adjustments 4`: views task0 69b475af…96ae, task1 adf16c7c…c2b6 (unchanged); `order.extended.yaml` **d147b4fe…e316 (changed)**; `task_tools.py` **6a602993…4bfb (changed)**; blueprint products unchanged; 7/7 gates green. Claims `rework_claims_r4.md`; worklog `tail -1` "REWORK round 4: gates 7/7 green".
- Both shared inputs moved; every charter-global section re-derived. Base copy byte-identical; `sweep.py` clean; uuid8s unchanged; cross_difficulty labels intact (replacement ×4 plan, drive-up marketplace_return_addition market). Scratch: `r4_dump.txt`, `r4_probes.py`; `r2_t0.py`, `r2_t1.py` re-run.
- Tool change: a shared `_Tender.refusal` (class static method, values only) makes all six tools refuse an order whose `payment_method_type` is not external_card, or that has a `membership_cash_redeem` row (membership_events.order_id) or a `gift_redeem` row (gift_events.source_record_id); field names exist in the charters; docstrings state it.

### round-3 item closure

| Item | r4 | Evidence |
| --- | --- | --- |
| N4 tender-dependent pricing | closed at the rule level | every rule and replaced_by now states the amount "is the same whatever tender paid the order"; drive-up scope no longer tests tender, Cash or gift card; edge conditions A–C no longer name a tender. But the tool contract now refuses exactly those orders — N6. |
| N5 credited haul from the working day | closed | matched settlements now count same-category replacement/reimbursement settlements dated the same day as the settlement read. `r4_probes.py`: base → 1 / 25.00 / 22.50; a second same-day reimbursement → 2 / 50.00 / 45.00; a second one a day earlier → 1; a same-day repair → 1; a same-day other category → 1; worked out 2027-05-01 → 22.50 (no longer moves). Tiers: T1 25 × min(count, items) ≥ 50.00, T2 25.00, T3 haul charged on one item (≤ 25.00, below it when discounted) — distinct with a distinguishing input per pair. |
| O9 goodwill recency to the working day | closed as stated | fee_age now runs to "the scheduled date the order carries"; worked out 2026-12-30 → 72.15 unchanged. See O10. |

### re-derived sections (revision_4)

- policy_conflict_scan: two trees, disjoint and complete. New collision: rule coverage vs tool coverage (N6).
- rule_compute_equivalence: matched_settlements XCOUNT with `event_date=settle_date` = "dated the same day as the settlement read"; fee_age `DAYS(last_fee_date, F('scheduled_date'))` = rule; all other bindings unchanged. Equivalent.
- action_binding: (target_tool, computes) unique; the tool bodies now refuse cases the rules cover (N6).
- prerequisite_graph / sentences: four state-form value_input edges, acyclic; sentences unchanged in A, B, D; C names "the latest late-change fee row with an amount above 0.00"; conditions no longer tender-qualified, so each edge is engaged on every tender.
- override_declarations: each replaced_by now restates nothing per tender (the amount is tender-blind); the retired fee-refund sentence's out-of-scope restatement intact.
- factor_ladders: counts 6/6/4/4/6/4, each ≥2 parameter and ≥1 method; every tier reachable and distinct; T2 holds for every factor.

### findings (revision_4, charter-global)

**N6 — SOURCE-POLICY / SOURCE-CHAIN RED (introduced in round 4; not engaged in either world).** The rules now cover every tender, while every target tool refuses any order not paid by external card or carrying a Northgate Cash or gift card redemption, and the routes the rules name for those tenders are carried out by nothing in the charters. Exhaustive members:
1. late_change: "whatever tender paid the order … on an order paid with a Northgate Card the same fee is charged to the card account as a Northgate purchase through the card charter rather than by this booking". No such path exists: order.yaml `order_charge_fee` triggers only `membership:membership_benefit_use`, and `card:card_post_purchase` is triggered only from plan.yaml and membership.yaml charges. And `reschedule_large_item_delivery_d930ab59` refuses the order, so the customer's own reschedule — the root write — cannot be recorded.
2–5. missed_appointment / replacement_haul_away / goodwill / late_express: "a share for a Northgate Card posts to the card account as a merchant credit through the base card-credit path rather than by this booking", and "any Northgate Cash and gift card share is restored first". The base card-credit path is an `order_refund_charge` row with payment_method_type northgate_card (base trigger `card:card_post_credit`) — the very booking these tools refuse — and no tool restores Cash or gift-card shares.
6. drive_up: the rule covers the return "whatever tender paid the order", and `return_item_at_drive_up_b4cf62ab` refuses it.
Demonstrated consequence: on task0's records with order tender northgate_card, edge A's condition ("The large-item delivery fee row has a refund … whenever that fee was charged above zero and the reschedule count exceeds …") is engaged. `credit_missed_appointment_73d9a081` returns "Error: this order was not paid with an external card", so the late-change fee can never be fixed, and the reschedule tool refuses the order too: no solution exists, though the policy says 41.85 / 22.50 / 72.15 / 39.65 are owed. The same holds on task1's records with a 1.00 Northgate Cash redemption (`membership_cash_redeem` on the order): both tools refuse, though the rule prices the return at 52.13. XF D20: each edge must be "satisfiable by its resolver in every engaged world".

Observation O10: goodwill recency now measures from the fee to the order's current scheduled date, so a later Northgate push of the appointment lowers the goodwill (`r4_probes.py`: scheduled 2026-10-24 → 72.15, 2026-10-27 → 60.30, 2026-11-25 → 52.40). The larger the move Northgate made, the smaller the goodwill — weak realism, recorded without a RED.

### closing_checklist (revision_4)

- Files carry revisions 1–4; revision_4 frozen before reveal. task0 PASS, task1 PASS; every gold figure equals the blind recomputation; no task value moved this round.
- Scope, tools, uuid8s: PASS. Problem trees: PASS in both worlds. Factors: PASS (N5 closed; O10 observation). Unique solution: PASS.
- Charter: N4 and N5 closed; N6 open — the rules cover every tender while all six tools refuse non-external-card and Cash/gift-redeemed orders, and the card / Cash / gift routes the rules name are carried out by no tool or trigger. The difficulty does not close while N6 stands.
- Gate snapshot: round 4, 7/7 green on the current hashes.

VERDICT revision_4: task0=PASS task1=PASS charter=N6

## revision_5

### charter_global_frozen (revision_5)

- Freeze 2026-10-24T18:48:51Z, before any round-5 reveal; revisions 1–4 untouched.
- Snapshot executed `/tmp/erl0080_coord/snapshot.sh order_returns_and_price_adjustments 5`: views task0 69b475af…96ae, task1 adf16c7c…c2b6 (unchanged); `order.extended.yaml` **e9d4a524…359a (changed)**; `task_tools.py` **dd14b9ed…e030 (changed: docstrings only — `_Tender.refusal` and every body unchanged)**; blueprint products unchanged; 7/7 gates green. Claims `rework_claims_r5.md`; worklog `tail -1` "REWORK round 5: gates 7/7 green".
- Re-derived in full. Base copy byte-identical; `sweep.py` clean (every quote, policy_source and replaced_by verbatim in its rule; no factor id in a tool name; uuid8s unchanged). Text diff r4→r5 (`r4_dump.txt` vs `r5_dump.txt`): compute, factors, ladders and params identical; changes confined to the tender sentences, the four prerequisite sentences and their conditions.

### N6 closure

- Every rule now states once: "This rule books it only on an order paid in full by an external card with no Northgate Cash or gift card redeemed on it; on every other order the same amount [late-change fee / refund] applies, its posting to the Northgate Card, Northgate Cash or gift card ledger is made by a human representative to whom the customer is handed over as POLICY_NOT_COVERED, and nothing is booked at the care desk." (one booking-scope test and one hand-off sentence per rule — counted mechanically). The card-charter fee route and the "base card-credit path" sentences are gone; no remaining sentence names a path nothing carries out.
- Tool scope = rule scope: the six docstrings say "Only an order paid in full by an external card with no Northgate Cash or gift card redeemed on it is booked here", and `_Tender.refusal` tests the order's primary tender (external_card) plus `membership_cash_redeem` and `gift_redeem` rows. Base `order_refund_tender` knows exactly those three tenders (Northgate Cash, gift card, primary payment method), so the body tests exactly the docstring's condition. The hand-off is executable by the share tool `transfer_to_human_agent`.
- Edges A–D: each policy_source now opens with the same record test, and each condition carries it verbatim, so no edge is engaged outside the scope in which its resolver books. Four-point test re-run: ordering connective kept; state form; no tool or id; condition and sentence at the same strength. PASS. XF D20: every engaged world is one in which the resolver books (amount > 0 guaranteed by the "charged above zero" tests). PASS.
- One price whatever pays: the figure is tender-blind in every rule (N4 stays closed); only the posting channel differs. PASS.
- O10 kept as an observation (reworker's reply: the move itself is compensated by the missed-appointment credit and the move courtesy of the same tree — accepted as no contradiction).

### re-derived sections (revision_5)

policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, override_declarations and factor_ladders: unchanged in substance from revision_4 apart from the N6 text above; no new defect. Every XF point re-checked on every changed policy: A (independence, assembly, T1/T2) unchanged; B (rule = compute, probes) unchanged; C16–19 (the hand-off restates the in-force figure for every out-of-scope order, scoped by a coarse record test); D20–21 PASS; E22–26 (no forbidden substring; the bodies write as before; docstrings carry no example values; no new trigger); F unchanged.

### findings (revision_5)

None. N6 closed; no class left open.

### closing_checklist (revision_5)

- Files: 0.md, 1.md and this file carry revisions 1–5; each revision frozen before its reveal; every comparison section of revision_5 carries PASS.
- Coverage and exclusivity: task0 = {late_change, missed_appointment, replacement_haul_away, late_fee_goodwill}, task1 = {drive_up_return, late_express}; disjoint, jointly all six extended policies; each task tool used by exactly one task; uuid8s independent and frozen.
- Problem trees: task0 3 prerequisites / 3 value_input / owner=user root; task1 1 / 1 / owner=user root; the difficulty's graph acyclic; every edge unmet at the opening, load-bearing, resolvable without waiting and, after N6, engaged only where its resolver books; tools judge no prerequisite.
- Factors: every computation 4–6 factors (≥2 parameter, ≥1 method), ladders of three distinct reachable tiers stated in full in the rule, honest baselines whose fall-back numbers differ from gold, near-misses present, multi-source and cross-difficulty factors (plan in task0, market in task1) on seeded, charter-true rows.
- Unique solution: both tasks.
- Gates: coordinator round-5 snapshot, 7/7 green on the final hashes (charter e9d4a524…359a, tools dd14b9ed…e030). Correction to the frozen note above: I verified `_Tender.refusal` unchanged from round 4 by reading it; that the other tool bodies are unchanged rests on the reworker's claim and on the bodies I read this round, which still book exactly as revision_4 describes.
- Observation carried: O10 (goodwill recency to the current scheduled date).

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (revision_6)

- Freeze 2026-10-24T23:30:34Z, before any round-6 reveal; revisions 1–5 untouched.
- Snapshot executed `/tmp/erl0080_coord/snapshot.sh order_returns_and_price_adjustments 6`: views task0 69b475af…96ae, task1 adf16c7c…c2b6 (unchanged); `order.extended.yaml` **6aec2c3b…e5c2 (changed)**; `task_tools.py` **351e913f…79cc (changed: `_Money.is_date` only)**; blueprint products unchanged; 7/7 gates green. Inputs: `rework_claims_r6.md` and the renderer stop report `audits/render_source/order_returns_and_price_adjustments/render_r1.md`; worklog `tail -1` "REWORK round 6: gates 7/7 green".
- Re-derived in full. Base copy byte-identical; `sweep.py` clean; text diff r5→r6 (`r5_dump.txt` vs `r6_dump.txt`) confined to the items below; compute unchanged except the new `requests_on_order` binding.

### audit-miss disclosure

The renderer found five source items that my revisions 1–5 passed. R-1 (the drive-up replaced_by drops "where the reason is changed_mind") and R-4 (the late-change fee's replace-vs-add reading) were in the source from revision_1. R-5 (`is_date` shape-only) was in the tool module from revision_1. R-2 (haul_standard / haul_items bound to no factor) dates from round 3. R-3 (a factor-owned count read by the free-reschedule test) dates from round 2. All are recorded here as previously missed by this audit. Revision 5's CLEAN verdict was wrong on these points.

### renderer items (render_r1.md) — closure

| Item | r6 | Evidence |
| --- | --- | --- |
| R-1 XF 16 | closed | drive-up replaced_by and rule now read "less the program's changed-mind restocking percentage where the reason is changed_mind and the class is one of the program's restocking classes" = the retired clause's in-force content. Exhaustive re-read of every replaced_by against its superseded clause (late-change ×2, missed ×2, replacement, goodwill, late-express, drive-up): no other condition dropped. |
| R-2 XF 3 | closed | credited_haul_basis.bindings = [haul_standard, haul_items, matched_settlements, credited_haul]. |
| R-3 XF 4 | closed | `own_requests` is now plain, with its own defining sentence ("The customer's confirmed reschedule requests already on the order, the request being made not counted, are the confirmed reschedule requests recorded on the order before this request."), and only `free_reschedule` reads it; the factor counts through its own `requests_on_order` (same COUNT; quote = the factor's schedule sentence). |
| R-4 XF 12/2 | closed | baseline (rule and baseline.rule): "The standard late-change notice charge is the program's late cancellation fee, and the standard late-change fee is that notice charge, rounded half up to the cent."; combining sentence: "…each schedule's value standing in place of its standard value…". One reading: one day ahead → 49.00, not 98.00; the notice factor's fall-through = baseline. |
| R-5 XF 24 | closed | `_Money.is_date` (class static method, no datetime import) checks month lengths and leap years. Probe: 2026-02-29 F, 2028-02-29 T, 2100-02-29 F, 2000-02-29 T, 2026-04-31 F, 2026-10-31 T, 2026-13-01 F, 2026-1-01 F. Every other docstring claim is enforced in its body (amount format/positivity, quantity, reason enum, fee/line of the order, booking-scope tender test). |
| R-obs XF A2 | closed | combining sentences now generic: late-express "the standard half, or the rate a schedule below sets in its place, plus every extra percentage the schedules give"; drive-up "the line's net amount as charged, or the amount a schedule below sets in its place, less the restocking fee" and "…each schedule's percentage standing in place of its standard value where it sets one…"; replacement "the haul-away charge on the order, or the amount a schedule below sets in its place". Missed and goodwill already generic. Each still has one reading. |

### exhaustive class passes (revision_6)

Mechanical read-set pass over every policy (script inline, rerunnable from `/tmp/erl0080_audit_order/calc.py`):
- XF 3 — no plain binding read only by one factor.
- XF 4 — no plain binding or standard-method binding reads a factor-internal binding; plain bindings read only factor outputs, for assembly.
- XF 1 — no factor reads another factor's binding.
- No binding belongs to two factors.
Manual passes: XF 2 / 12 — every combining sentence generic and single-reading; XF 13 — every quote verbatim; XF 16–17 — every replaced_by restates its retired clause's in-force content; XF D20 — every edge engaged only inside the booking scope where its resolver books an amount above zero; XF E22–26 — clean. Figures and factor sensitivities re-run on both views: unchanged.

### findings (revision_6)

None open. O10 carried as an observation.

### closing_checklist (revision_6)

- Files carry revisions 1–6, each frozen before its reveal; revision_6 comparisons PASS in both tasks; every gold figure equals the blind recomputation.
- Coverage, exclusivity, tools and uuid8s: as revision_5, PASS. Problem trees: PASS. Factors: PASS, now also under the renderer's XF 3/4 read-set classes (mechanical pass clean). Unique solution: PASS (R-4's second reading removed).
- Renderer items R-1..R-5 and R-obs closed; my earlier revisions missed them (disclosed above).
- Gates: coordinator round-6 snapshot, 7/7 green on the final hashes (charter 6aec2c3b…e5c2, tools 351e913f…79cc).
- Observation carried: O10.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global_frozen (revision_7) — seed-only round

- Freeze 2026-10-25T05:14:20Z, before any round-7 reveal; revisions 1–6 untouched.
- Snapshot executed `/tmp/erl0080_coord/snapshot.sh order_returns_and_price_adjustments 7`: view task0 **71386c92…3980 (changed)**, task1 adf16c7c…c2b6 (unchanged). `order.extended.yaml` 6aec2c3b…e5c2 and `task_tools.py` 351e913f…79cc are unchanged and equal `/tmp/erl0080_coord/seed_freeze.txt`. Blueprint products unchanged; 7/7 gates green. Claims `rework_claims_r7.md`; worklog `tail -1` "REWORK round 7: gates 7/7 green".
- Both shared inputs carry the revision_6 hashes, so every charter-global section of revision_6 is carried forward by reference on those two hashes. Only task0's world is re-derived; task1's per-task sections carry forward on its unchanged view hash.

### closing_checklist (revision_7)

- Seed-only round: charter and tools byte-identical to the seed freeze; task0's re-priced plan ledger, plan holding and 2024 order are each producible by docs/plan (table in 0.md §revision_7); task1 unchanged; gold unchanged in both tasks and equal to the blind recomputation.
- All revision_6 closing items carry forward on the unchanged charter and tool hashes; nothing regressed.
- Gates: round-7 snapshot, 7/7 green. Observation carried: O10.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
