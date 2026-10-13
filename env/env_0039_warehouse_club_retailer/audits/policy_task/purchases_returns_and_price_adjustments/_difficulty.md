# Policy-task audit — purchases_returns_and_price_adjustments / charter-global

## charter_global_frozen

- Scenario: `env/env_0039_warehouse_club_retailer`; difficulty `purchases_returns_and_price_adjustments` (category `order`, M=2).
- Freeze time: 2026-10-05 21:31 UTC (written before any task's GT was revealed). Auditor: independent erl-task-policy-audit run (Claude); did not author any audited artifact.
- Frozen input hashes (sha256, re-computed by the auditor and equal to the brief):
  - `tasks/purchases_returns_and_price_adjustments/order.extended.yaml` `45e839b3ee6ee08b58af83234bb568ec8e207a85f0d5ab3a63a38df9fea88837`
  - `tasks/purchases_returns_and_price_adjustments/task_tools.py` `a9da31922612dbad32ca25d0a2312fdbf0e72bdfadcb446769463751b0f36450`
  - masked views `audits/views/policy_task/purchases_returns_and_price_adjustments/0.view.json` `4dd1103b…0eee`, `1.view.json` `a3dc0c69…2f475f27`
- Fields read: blueprint `blueprint.yaml` (difficulty entry), `db_schema.json`, `share_tools.py`, `products/order.yaml` (and `products/delivery.yaml`, `products/card.yaml` sections for the cross-category rows' meaning), the full extended charter, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state), `erlbench/` and the gate script `check_compute.py` (DSL semantics only).
- Fields masked / not read: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `worklog.md`, any earlier audit. No recursive search touched `tasks/`.
- Entry conditions (Step 0): the brief supplies the gate snapshot — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK, declared as expected because the KB `docs/` is not rendered yet (deferred to step 3). The masked views and their hashes were supplied. Entry conditions are complete; the TRACEABILITY deferral is recorded and not re-run here.
- Base copy: `order.extended.yaml` keys `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies` compared programmatically against `blueprint/products/order.yaml`: all equal. Base copy is verbatim.

### policy_conflict_scan

Extended policies (5):

| id | segment scope | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- | --- |
| order_ext_business_route_pickup_fee | Business / Business Plus, special-order changed-mind freight pickup | on_request | invoice_route_pickup_fee_16b23a12 (agent) | route_pickup_fee | [] |
| order_ext_business_restocking_charge | Business / Business Plus, special-order changed-mind return | on_request | confirm_business_return_92c81b09 (user) | restocking_fee | value_input <- route pickup fee |
| order_ext_changed_mind_refund | any segment, Special Order, sale line with no Annual Reward, received RA | state_due | post_changed_mind_refund_b29df74c (agent) | refund_amount | [] |
| order_ext_settlement_restocking_fee | consumer segment, Special Order changed-mind | state_due | charge_restocking_fee_79f2f340 (agent) | restocking_fee | value_input <- changed-mind refund |
| order_ext_member_pickup_fee | consumer segment, Special Order changed-mind freight pickup | on_request | confirm_freight_pickup_4c90eb99 (user) | pickup_fee | state_gate <- settlement restocking fee |

Overlap analysis:
- Two policies replace the base restocking sentence (business restocking charge / settlement restocking fee) and two replace the base pickup-fee sentence (route pickup fee / member pickup fee). Each pair is split by presenting-membership segment, and each rule closes its own scope verbatim ("a purchase presented on any other membership is outside this rule" / "a purchase presented on a business-segment membership is outside this rule"). The segments partition the six membership tiers (Business, Business Plus vs Student Club, Heroes Club, Club, Club Plus), so no purchase is governed by both members of a pair.
- Timing anchors differ in kind but do not collide: the business restocking charge is fixed at the member's confirmation and "is not charged again when the refund is later posted"; the settlement restocking fee is charged when the changed-mind refund posts and is consumer-only. On a business purchase the changed-mind refund (any segment) therefore carries no second restocking entry; on a consumer purchase there is no restocking at confirmation. No double charge is reachable.
- `order_ext_changed_mind_refund` applies to both segments; its only downstream consumer in this charter is the consumer settlement fee. Base inheritances that still bind it: `order_agg_return_review` (18 returns / 2,500.00 changed-mind threshold per membership, rolling 365 days), `order_returns` status gate (fulfilled / partially_returned), 30-day Special Order override window counted from fulfilled_date to the RA's requested_date, the received-RA gate, no double refund, refund to tender, status transition.
- Cross-category read boundaries: delivery (holding `variant_name`, `distance_miles`, `delivery_id`; ledger `delivery_charges.units` with `charge_type stair_carry`), card (holding `variant_name`/`status`; ledger `card_transactions.qualifying_spend` with `spend_category northgate_purchases`), membership (holding `variant_name`, `opened_date`). All are reachable through share finders (`find_delivery_holdings`, `find_delivery_charges`, `find_card_holdings`, `find_card_transactions`, `find_membership_holdings`, each returning the full row).
- Claimed scopes of the M=2 tasks cannot be read before reveal (charter_scope is masked). From the masked worlds alone: task 0 (Business Plus member, one submitted RA, no received RA) can only exercise the two business policies; task 1 (Club member, received + submitted RAs) can only exercise changed-mind refund -> settlement restocking fee -> member pickup fee. Jointly these cover all 5 extended policies with no shared policy. Confirmed against charter_scope only in the closing checklist.

No conflict producing two conclusions on one situation was found.

### rule_compute_equivalence

Forward (every binding has a verbatim `compute_basis` quotation) and backward (every rule promise implemented) sweep, per policy:

- route pickup fee: trip = `P('changed_mind_pickup_fee_usd')` ("the channel's changed_mind_pickup_fee_usd for the trip"); distance ladder `> 40` / `> 20` (else-branch gives "no more than 40") / 0 with "no Northgate delivery appointment" as `or 0`; stair ladder `>= 2` / `>= 1` / 0 over `stair_carry` units of that appointment; piece rate by class 18 / 12 / 10 times `MX(0, auth_units - 1)`; cardholder share 0.5 / 0.75 / 1; grouping "first added into one sum, the cardholder share is then applied once", rounding once at the end. Equivalent.
- business restocking charge: returned value = units x unit price; volume rate 9 / 12 / `restocking_fee_pct` with 12-month window over `card_rewards_earned` `northgate_purchases`; share points via `auth_units*2 >= sold` / `auth_units*4 >= sold`; class points 3 / 1 / 0; timing `<= 14` / `<= 21` / full with `DAYS(fulfilled_date, requested_date)` (day 0 = fulfillment); credit 1 / 0.5 / 0 from tier + `MONTHS(opened_date, NOW)`; grouping "rate + share + class into one percentage, applied once, timing multiplier, round; credited route fee subtracted, floor 0, round". Equivalent.
- changed-mind refund: received RA chosen by latest `requested_date` ("the one most recently requested"); collection ladder over kept-after units of the class and the purchase's class sales; repeat points counted on this purchase only; inspection 3 / 10 day ladder; teardown by service level; card share; savings and teardown each rounded then subtracted. Equivalent.
- settlement restocking fee: card rate 10 / 12.5 / `restocking_fee_pct`; tenure 96 / 60 months; value points by unit price 500 / 1,000; kept-order points by kept/sold after refund (80 % / 50 %); timing 7 / 14 days; "card rate less tenure plus value less kept, applied once, timing, round once". Equivalent.
- member pickup fee: trip, distance 30 / 15, stairs 20 / 10, crew by authorized value 1,000 / 500, follow-up credit by count of return_pickup_fee entries on the purchase, cardholder credit 15 / 8, loyalty 0.5 / 0.8 / 1; "added, credits subtracted, floor 0, loyalty applied once, round once". Equivalent.

Every declared factor's ladder tiers appear both as rule sentences and as branches of the `decides` binding; no tier exists in only one face.

Machine-face divergences from the rule's words that are *latent* (no consequence unless the world exercises them; each is checked against each task world in that task's file):
- G1 `auth_units: SUM('order_return_authorizations','quantity', status='submitted')` (route pickup fee, business restocking charge, member pickup fee) sums every submitted RA on the purchase, while the rule says "every unit on the authorization" / "the units on the authorization" (one authorization, the one whose sale line `auth_line` picks). Diverges only on a purchase with two or more submitted RAs.
- G2 `CFIELD('card','variant_name', status='active')` returns the first active card row of the customer; the rules are existential ("the member holds an active Northgate Rewards Visa …"). Diverges only for a customer with two or more active cards.
- G3 `CFIELD('delivery', …, order_id=HID)` takes the first appointment row on the purchase regardless of status; the rules read "the Northgate delivery appointment that delivered the purchase". Diverges only with more than one appointment on the purchase.
- G4 settlement `refund_posted: SUM(… order_line_returned, changed_mind, source_order_line_id=rcv_line)` sums every changed-mind refund on that sale line; the rule says "the changed-mind refund posted for the units of that authorization". Diverges only when the same sale line already carried an earlier changed-mind refund.
- G5 `RND` is Python `round` on a binary float (ties not reliably half up); the rules say "rounded half up to the cent". Diverges only on an exact half-cent intermediate.
- G6 changed-mind refund `rcv_line` / settlement `rcv_line` take the most recently requested *received* RA even if it is already refunded; the rule says the same ("worked for the one most recently requested"), so a purchase whose latest received RA is already refunded would be directed to refund it again against base `no_double_refund`. Diverges only in such a world.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (invoice_route_pickup_fee_16b23a12, route_pickup_fee), (confirm_business_return_92c81b09, restocking_fee), (post_changed_mind_refund_b29df74c, refund_amount), (charge_restocking_fee_79f2f340, restocking_fee), (confirm_freight_pickup_4c90eb99, pickup_fee). Each pair is claimed by exactly one policy; the two `restocking_fee` computations bind different tools.
- Tool bodies (`task_tools.py`): each performs one posting with the given amount; none reads an eligibility, status, prerequisite or computes an amount ("No tool checks an eligibility, a prerequisite or a policy amount"). The two user tools flip the RA to `confirmed` and book one fee entry; neither checks that the RA is `submitted`.
- Docstrings: no tool names another tool, and no docstring places its action relative to another problem. Ordering words present are argument provenance only ("read from the purchase lookup before the call") and an effect clause ("the crew is then scheduled"). `charge_restocking_fee_79f2f340` describes its object as "the refunded sale line" and `invoice_route_pickup_fee_16b23a12` says a receipt "means the fee is now standing on the purchase" — see observation O7.
- uuid8 tails: 16b23a12, 92c81b09, b29df74c, 79f2f340, 4c90eb99 — pairwise distinct, no shared prefix, no arithmetic progression, none reused from the share tools (which carry no uuid tails). Independent.

### prerequisite_graph

- `prerequisite` is present on all 5 policies (`[]` on route pickup fee and changed-mind refund).
- Edges: business_restocking_charge -> business_route_pickup_fee (value_input, gate `route_fee`); settlement_restocking_fee -> changed_mind_refund (value_input, gate `refund_posted`); member_pickup_fee -> settlement_restocking_fee (state_gate, gate `order_lines.fee_type`). Every `problem` is another extended policy id; none points at a base policy or at itself. The graph is two disjoint chains (length 1 and length 2) — acyclic.
- `policy_source` of each edge is locatable verbatim in the blocked policy's own `rule` (checked by substring): yes for all three.
- `form: state` on all three; no `fallback_reason` on any — consistent.
- `resolved_by` equals the depended-on policy's `target_tool` in all three, and the tool's effect produces the condition: the route invoice books a `return_pickup_fee` entry against the RA's sale line; the changed-mind refund books an `order_line_returned` `changed_mind` entry against the sale line; the restocking charge books a `restocking_fee` entry against the sale line.
- `kind`/`gate`: `route_fee` and `refund_posted` are real compute bindings of the blocked policies and their values move with the depended-on write; `order_lines.fee_type` is a field path, which the authoring template admits for a state_gate.
- `condition` vs sentence: edges 1 and 2 match the sentence's strength. Edge 3's condition reads "For every return authorization in status received on the purchase …", dropping the sentence's qualifier "changed-mind return"; the RA table carries no reason field, so the condition is broader than the sentence wherever a received RA is not a changed-mind return (see observation O5).
- No authoring-viewpoint phrasing ("this task", "the opening world") in any `condition`, `policy_source` or `effect`.

### prerequisite_sentences

Edge 1 — "The business restocking charge on a changed-mind return is fixed only after the route pickup fee for that same return authorization stands on the purchase."
- Connective "only after"; state form: "the route pickup fee … stands on the purchase" (a record-visible return pickup fee entry); no tool name, policy id, snake_case or row id; strength equals the condition.
- Writes able to bring a pickup-fee entry about: the route invoice (business) and the member's freight-pickup confirmation (consumer). On a purchase in this rule's scope (business-presented) only the route pickup fee policy applies, and the sentence names "the route pickup fee" by the depended-on rule's own term. One reading.
- Derivation: sentence -> records show no return pickup fee entry on the RA's sale line -> the rule that books "a route pickup fee, entered as one return_pickup_fee entry against the sale line of the return authorization awaiting the member's confirmation" is the route pickup fee policy -> its write (agent) is the resolving action.

Edge 2 — "The settlement restocking fee is fixed only after the changed-mind refund for the units the returns center has logged as received stands on the purchase."
- Connective "only after"; state form; no tool / id; matches the condition. Only `post_changed_mind_refund_b29df74c` books a changed_mind refund entry. One reading.
- Derivation: sentence -> records show the most recently requested received RA's sale line has no changed_mind refund -> the changed-mind refund policy ("refunded by member services once the return authorization for that sale line shows received, as one order_line_returned entry with return_reason changed_mind") -> its write.
- Second wording: the same rule (and its `baseline.rule`) also says the fee "is charged … when the changed-mind refund for those units is posted". It agrees with the prerequisite sentence (observation O6).

Edge 3 — "The member pickup fee on a special order is not fixed until every changed-mind return on that purchase whose merchandise the returns center has logged as received carries its restocking fee entry."
- Connective "not until"; state form; no tool / id. Writes that book a restocking_fee entry: the consumer settlement fee and the business confirmation; the blocked rule is consumer-only, so on its purchases only the settlement policy applies. One reading.
- Derivation: sentence -> find received RAs on the purchase whose sale line has no restocking_fee entry -> the settlement restocking fee rule ("charged as the settlement restocking fee when the changed-mind refund for those units is posted, entered as one restocking_fee entry against the refunded sale line") -> which itself waits (edge 2) on the changed-mind refund.
- Depended-on rules do not restate any blocked side's sentence (checked by whitespace-normalised substring: edge 1's sentence is absent from the route pickup fee rule, edge 2's from the changed-mind refund rule, edge 3's from the settlement rule).
- No rule states a cross-problem order outside these edges. The business restocking clause "it is not charged again when the refund is later posted" refers to a later event as a dedup statement, not as an ordering requirement between problems (observation O9). The changed-mind refund's "once the return authorization … shows received" waits on a returns-center state that no write of this difficulty produces; it is a base-inherited eligibility, not a cross-problem edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- route pickup fee (refs order_returns, order_fees): base "a changed_mind freight pickup is charged changed_mind_pickup_fee_usd as a return_pickup_fee entry" -> replaced, declared in `overwrite`. "neither is charged for a reason in restocking_fee_waived_reasons" -> followed (rule is changed-mind only). order_fees "Restocking and changed-mind pickup fees are charged only as order_returns provides" -> followed (the provision is now the declared replacement). Other order_returns sentences (window, status, freight pickup for freight_pickup_classes, confirmation, ship-by) -> inherited.
- business restocking charge (refs order_returns, order_fees): base "A changed_mind return on a channel with a restocking_fee_pct is charged that percentage of the refund as a restocking_fee entry" -> replaced (base = percent of the refund; extended = percent of units x sale unit price, with factors), declared. Everything else inherited.
- changed-mind refund (refs order_agg_return_review, order_cancellation, order_returns, order_returnless_refunds): base "Each returned unit is refunded at order_msr_sale_unit_price, less the per-unit price adjustment … less order_msr_rebated_unit_credit …" -> replaced, declared. Review thresholds, status gate, window, received gate, no double refund, refund to tender, status transition -> inherited and not weakened. Cancellation / returnless refunds -> not applicable to a changed-mind refund. Not in refs: `order_mail_in_rebates` "a rebated unit returned later is refunded at its sale price minus the rebate already paid on it" governs the same quantity but is vacuous on the Special Order channel (`mail_in_rebate_eligible: false`; `price_adjustment_window_days: 0`), so no second answer is reachable (observation O8).
- settlement restocking fee (refs order_returns, order_fees): base restocking sentence -> replaced, declared; base base ("percentage of the refund") is kept as the standard method. Inherited otherwise.
- member pickup fee (refs order_returns, order_fees): base pickup-fee sentence -> replaced, declared. Inherited otherwise.

Disguised forms: no anonymous intermediate factor overriding a base quantity outside the declared sentences; no 0/1 multiplier zeroing a base quantity (inspection share 0 and card share 0 zero only the extended withholding, not the base refund); no dropped base branch (base restocking/pickup fees are waived for the reasons in restocking_fee_waived_reasons, and every extended rule is limited to changed-mind returns). No undeclared override found.

### factor_ladders

| policy | factor | effect | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| route pickup fee | route_distance_charge | parameter | >40 mi 35 / >20 ≤40 mi 20 / else 0 | no | delivery |
| | route_stair_charge | parameter | ≥2 flights 30 / 1 flight 15 / else 0 | no | delivery |
| | route_piece_handling_rate | parameter | major_appliance 18 / mattress_furniture 12 / else 10 | no | — |
| | route_cardholder_share | method (multiplier on the sum) | Visa tender ∧ Business Plus card 0.5 / (Visa ∧ Business card) ∨ (other tender ∧ Business Plus card) 0.75 / else 1 | yes (order tender + card holding) | card |
| business restocking | business_volume_rate | parameter | card ∧ spend ≥25k 9 / card ∧ 10k–25k 12 / else restocking_fee_pct | yes (card holding + card ledger) | card |
| | business_share_returned | parameter | ≥½ +2 / ≥¼ <½ +1 / else 0 | no | — |
| | business_piece_class | parameter | appliance +3 / furniture +1 / else 0 | no | — |
| | business_return_timing | method (multiplier) | ≤14 d 0.6 / 15–21 d 0.8 / else 1 | no | — |
| | business_route_fee_credit | method (share of route fee subtracted) | Business Plus ∧ ≥60 mo full / (Plus ∧ <60) ∨ (Business ∧ ≥60) half / else none | compound, same membership row | membership |
| changed-mind refund | collection_savings_rate | parameter | kept≥2 ∧ class sales ≥3k 6 % / (kept=1 ∧ ≥1.5k) ∨ (kept≥2 ∧ 1.5k–3k) 4 % / else 0 | yes (kept units from sold+returned rows, class sales from sold rows) | — |
| | repeat_changed_mind_points | parameter | ≥2 +3 / 1 +1.5 / else 0 | no | — |
| | collection_inspection_period | method (share of withheld %) | ≤3 d none / 4–10 d half / else all | no | — |
| | crew_teardown_rate | parameter | White Glove 30 / Room of Choice 15 / else 0 | no | delivery |
| | card_return_protection | method (share of teardown) | Visa ∧ Sig Plus none / (Visa ∧ Sig) ∨ (other ∧ Sig Plus) half / else all | yes (tender + card holding) | card |
| settlement restocking | settlement_card_rate | parameter | card ∧ ≥6k 10 / card ∧ 2k–6k 12.5 / else restocking_fee_pct | yes (card holding + ledger) | card |
| | settlement_tenure_points | parameter | ≥96 mo −2 / 60–96 mo −1 / else 0 | no | membership |
| | settlement_piece_value_points | parameter | <500 +1 / 500–1,000 +0.5 / else 0 | no | — |
| | settlement_kept_order_points | parameter | ≥80 % −1.5 / 50–80 % −0.5 / else 0 | no | — |
| | settlement_timing | method (multiplier) | ≤7 d 0.5 / 8–14 d 0.75 / else 1 | no | — |
| member pickup fee | member_pickup_distance | parameter | >40 30 / >20 ≤40 15 / else 0 | no | delivery |
| | member_pickup_stairs | parameter | ≥2 20 / 1 10 / else 0 | no | delivery |
| | member_pickup_crew | parameter | ≥1,000 15 / 500–1,000 8 / else 0 | no | — |
| | member_pickup_followup_credit | parameter | ≥2 entries −20 / 1 −10 / else 0 | no | — |
| | member_pickup_cardholder_credit | parameter | Sig Plus −15 / Sig −8 / else 0 | no | card |
| | member_pickup_loyalty_rate | method (multiplier) | Club Plus ∧ ≥60 mo 0.5 / (Club Plus ∧ <60) ∨ (other consumer ∧ ≥60) 0.8 / else 1 | compound, same membership row | membership |

Structural conclusions:
- Counts per policy: route 4 (3 parameter, 1 method); business restocking 5 (3 / 2); changed-mind refund 5 (3 / 2); settlement 5 (4 / 1); member pickup 6 (5 / 1). All within 4–6, every policy has ≥2 parameter and ≥1 method.
- Method labels: every method factor is a multiplier / share applied to an intermediate or to the result; the authoring framework lists "a transform or multiplier on an intermediate or on the result" as a method family, and in each case the tier changes how much of a computed sum is taken, not a rate inside the same term. Labels accepted as honest. Parameter labels select a number in each case.
- Ladders: every ladder has 3 tiers, pairwise disjoint as stated (boundaries checked: "more than 40" / "more than 20 and no more than 40"; "half or more" / "a quarter or more but less than half"; "4 to 10" / "15 to 21" / "8 to 14" day bands; "at least 2,000 but less than 6,000"; "60 months or more but less than 96"), and no two tiers of one ladder select the same value or method. Every tier, its condition and its value / method is stated in the `rule`; every fall-through equals what `baseline.rule` states (standard trip fee, standard 10.00 piece rate, channel restocking_fee_pct, "nothing withheld", full charge).
- Realism: each condition is one a warehouse club's returns / delivery desk plausibly weighs for that quantity (distance and stairs for a crew trip, class for handling, card / account volume and tenure for loyalty concessions, how early the return was requested, how much of a line or a collection is broken up, how many pickups or changed-mind refunds the purchase already carries, service level for teardown). No tier condition holds of every customer reaching its write (the segment and channel restrictions are scope, not tiers). No fall-through outcome is a treatment the business would not publish (the base charter's own Special Order fees — 79.00 pickup, 15 % restocking, refund at sale price — are the fall-throughs).
- Baselines: each `baseline.rule` is a verbatim sentence span of its `rule`, self-sufficient, and its `params` keys (`changed_mind_pickup_fee_usd`, `standard_piece_rate`, `restocking_fee_pct`) are tier parameters or policy params. Each factor's `baseline` expression equals what that paragraph gives for the input (0 for an added / withheld amount, `K('standard_piece_rate')`, `P('restocking_fee_pct')`, 1 for a share).
- Multi-source and cross-difficulty availability: route + business restocking (task-0 candidates) offer multi-source `route_cardholder_share`, `business_volume_rate` and cross-difficulty delivery / card / membership factors; changed-mind refund + settlement + member pickup (task-1 candidates) offer multi-source `collection_savings_rate`, `card_return_protection`, `settlement_card_rate` and cross-difficulty delivery / card / membership factors. Whether each bears weight and whether its evidence is seeded is per task (`factor_weight`).

### findings

No charter-global SOURCE-POLICY RED. Observations (no consequence demonstrable from the charter alone; each task file checks whether its world exercises them):

- O1 (G1) `auth_units` sums every submitted RA on the purchase while the rules speak of "the authorization". Bears on any task using route pickup fee, business restocking charge or member pickup fee. Affected: `order.extended.yaml` compute of those three policies.
- O2 (G2) first-active-card read vs existential "holds an active …". Bears on every task (all five policies read a card). Affected: `active_card` / `card_variant` bindings.
- O3 (G3) first delivery appointment row on the purchase, any status, vs "the appointment that delivered the purchase". Bears on tasks using route pickup, changed-mind refund, member pickup.
- O4 (G4) settlement `refund_posted` sums all changed-mind refunds on the sale line vs "the refund posted for the units of that authorization". Bears on the task using the settlement fee.
- O5 edge-3 `condition` omits the "changed-mind" qualifier of its sentence, and the settlement policy works only the most recently requested received RA, so a purchase with two received changed-mind RAs both lacking a restocking entry would leave the member-pickup gate unresolvable through the declared chain. Bears on the task using the member pickup fee.
- O6 settlement rule and its `baseline.rule` carry a second wording of the dependency on the refund ("is charged … when the changed-mind refund for those units is posted") besides the prerequisite sentence; both agree. Relevant to the KB-document audit, since the computation document will carry it.
- O7 docstrings: `charge_restocking_fee_79f2f340` names its object "the refunded sale line"; `invoice_route_pickup_fee_16b23a12` echoes the edge-1 state wording ("the fee is now standing on the purchase"). Neither names another tool or orders problems.
- O8 `order_ext_changed_mind_refund.base_policy_refs` omits `order_mail_in_rebates`, whose last sentence governs the same refund quantity; vacuous on Special Order.
- O9 business restocking rule "it is not charged again when the refund is later posted" mentions a later refund as a dedup clause; no ordering obligation.
- O10 delivery cross-category evidence semantics: delivery charter `delivery_service_charged.units` = "billing units (items, flights, miles, or 1)" while its formula is `stair_amount: round(max(0, units - stair_carry_included_flights) * stair_carry_fee_per_flight_usd, 2)` with "A component whose amount comes to zero is not entered". If `units` were flights carried, a stair_carry row with units 1 and amount 20.00 on a level that includes ≥1 flight could not exist; if it is flights billed (beyond those included), the row is consistent. The extended stair ladders read "charged … flights of stairs", which selects the billed reading. Bears on tasks whose world seeds a stair_carry row.
- O11 (G5, G6) float rounding and latest-received-RA selection — latent only.

## closing_checklist

Written 2026-10-05 21:37 UTC, after both tasks' derivations were frozen and both GT comparisons appended. Nothing above this heading was changed after the reveal.

- Audit files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json` (contiguous, M=2); this file sits alongside. First audit round — no older revision exists. Both comparison sections carry PASS.
- Coverage and scope: task 0 `charter_scope` = {order_ext_business_route_pickup_fee, order_ext_business_restocking_charge} with tools {invoice_route_pickup_fee_16b23a12, confirm_business_return_92c81b09}; task 1 = {order_ext_changed_mind_refund, order_ext_settlement_restocking_fee, order_ext_member_pickup_fee} with tools {post_changed_mind_refund_b29df74c, charge_restocking_fee_79f2f340, confirm_freight_pickup_4c90eb99}. All 5 extended policies and all 5 task tools covered; scopes pairwise disjoint, each spanning its whole tree. Every GT write is a claimed tool; uuid8 tails independent (§ action_binding_and_uuids).
- Trees: task 0 — 1 prerequisite problem, 1 value_input edge, user-owned root; task 1 — 2 prerequisite problems, 1 value_input + 1 state_gate edge (≥ max(1,1)), user-owned root. Difficulty-wide prerequisite graph: two disjoint chains, acyclic, no cross-task reference.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors with ≥2 parameter and ≥1 method (4, 5 / 5, 5, 6); each task carries ≥1 multi-source factor (task 0: route_cardholder_share, business_volume_rate; task 1: collection_savings_rate, card_return_protection, settlement_card_rate) and ≥1 cross-difficulty factor with seeded evidence (delivery, card, membership in both). Every ladder has 3 distinct-outcome tiers stated in full in the rule; every factor moves its task's scored value under its baseline, and every whole-baseline figure (109.00, 269.99; 449.99, 62.72, 79.00) differs from gold.
- Gates on the final form: the artifacts audited are byte-identical to those of the coordinator's gate snapshot of 2026-10-05 (sha256 of `order.extended.yaml`, `task_tools.py` re-checked at close: `45e839b3…88837`, `a9da3192…f36450`; `tasks/0.json` `fef18cb5…5c39`, `tasks/1.json` `522691b1…bfb6`). Snapshot: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK pending the KB render (deferred to step 3, outside this audit). The auditor did not re-run the gates (Step 0: cite, do not run).
- Result: source-layer audit of this difficulty — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS, for both tasks. Open items are observations only (`_difficulty.md` O1–O11; `0.md` F0-2, F0-3; `1.md` F1-2, F1-3), none of which demonstrates a consequence on either task's scored solution.
