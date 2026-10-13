# Policy-task audit — returns_and_exchanges / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the author of the artifacts.
- Freeze time: 2026-10-05T00:52Z (wall clock of the audit run), before any task GT was revealed.
- Frozen inputs (sha256):
  - `tasks/returns_and_exchanges/returns.extended.yaml` = `3826dee31e0517c9bfd5c752767d8c740560ab2b8f6c9f7df180bec9f5a21618` (matches coordinator HASHES.txt)
  - `tasks/returns_and_exchanges/task_tools.py` = `607ca8be46fa8fdb37e4c36f641f02c726d34d47559c034c0e434323059b6c08` (matches HASHES.txt)
  - `blueprint/products/returns.yaml` = `5398b328f2303e5f50cbbc536dfd88a54236eb3e3d3e5e1efb1456735fcb2782`
- Fields permitted: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/*.yaml` of this scenario), the extended charter, `task_tools.py`, and the masked views `audits/_views/policy_task/returns_and_exchanges/{0,1}.view.json` (frozen_time, user_scenario, initial_state only).
- Fields masked and not read while this section was written: every `tasks/returns_and_exchanges/tasks/*.json`, `tasks/returns_and_exchanges/worklog.md`, the scenario `worklog.md`, all `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closure fields. Nothing in this section is derived from a revealed GT.

### entry_conditions (Step 0)

- Gate snapshot supplied: `audits/_views/policy_task/returns_and_exchanges/GATES.txt` — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to the KB stage (needs published docs). Cited, not re-run.
- Masked views and hashes supplied: `HASHES.txt`; recomputed here — `0.view.json` `e580b303eac291e1c32cc8079c7ae901c5efb12098ffba7e23ea5d021ef6b6cb`, `1.view.json` `02dd083222bc84c2484c2d8713a88156c8c6e22212a4c52ec4ba929ad100d79e`, charter and tool hashes as above: all four match.
- Entry conditions complete.

### base_copy

`returns.extended.yaml` minus `extended_policies` parsed and compared key by key with `blueprint/products/returns.yaml`: `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies` all equal; the only extra key is `extended_policies`. Textual diff of lines 1–1208 against the blueprint file: one trailing blank line. Base copy verbatim.

### policy_conflict_scan

Eight extended policies (all `trigger: state_due` except `returns_ext_courtesy_extension` and `returns_ext_exchange_hold`, `on_request`):

| policy | subject | target_tool | computes | owner |
| --- | --- | --- | --- | --- |
| returns_ext_line_credit | returns_refund_credited | credit_inspected_line_1e38d691 | tax_amount_usd (+ merchandise_amount_usd argument) | agent |
| returns_ext_grade_b_restocking | returns_fee_assessed (restocking_fee) | assess_restocking_fee_49fe3caa | fee_amount_usd | agent |
| returns_ext_spent_credit_recovery | returns_instant_credit_reversed (original_card) | authorize_spent_credit_charge_4aac9d1c | charge_amount_usd | user |
| returns_ext_courtesy_extension | returns_deadline_extended | extend_return_deadline_be33eaa2 | extension_days | agent |
| returns_ext_shoebox_fee | returns_fee_assessed (missing_box_fee) | assess_box_fee_f48699d7 | fee_amount_usd | agent |
| returns_ext_return_shipping_fee | returns_fee_assessed (method_fee) | withhold_return_shipping_fee_e68e1eec | fee_amount_usd | agent |
| returns_ext_final_card_refund | returns_refund_issued (final_settlement, card_or_wallet) | pay_final_card_refund_b5173030 | refund_amount_usd | agent |
| returns_ext_exchange_hold | returns_hold_placed | place_exchange_hold_2c1506d4 | hold_amount_usd | user |

Overlap scan:
- Three policies write `returns_fee_assessed`; they are separated by `fee_type` (restocking_fee / missing_box_fee / method_fee), by subject line (grade B units / footwear box condition / once per return) and by tool. No two compute the same fee.
- Variant coverage of fees is consistent with base parameters: restocking (Standard, Store Credit, Gift — base `restocking_fee_applies` true for exactly these), shoebox (same three — base `missing_box_fee_usd` 10.00 for exactly these), return shipping fee (types with `return_method_fee_applies` — only Standard Return in base).
- Time anchors: every state_due policy opens at `return_cases.status = inspected`; courtesy extension at `status = authorized` and frozen_time ≤ return_by_date (base `returns_evt_deadline` retained); exchange hold has no status anchor beyond its prerequisite.
- Cross-category read boundaries: reads of orders, loyalty, pass, claims, credit are all declared in `cross_category`; no write outside returns tables (all eight tools create/update only `return_settlements` / `return_cases`).
- Terminal states: no policy moves `return_cases.status`; none writes `returns_settled`. No conflicting terminal state.
- Scope exclusivity / completeness (structure only; the per-task trees are derived blind in each task file): the `prerequisite` graph has exactly two connected components — {courtesy_extension → spent_credit_recovery → {line_credit, grade_b_restocking}, grade_b_restocking → line_credit} and {exchange_hold → final_card_refund → {return_shipping_fee, shoebox_fee}}. The two components are disjoint and together cover all eight policies, so with M=2 one tree per task is the only exclusive and complete partition.

### rule_compute_equivalence

Swept every `compute` binding against its `compute_basis` quotation and the `rule`, and every `rule` sentence back to a binding.

- returns_ext_line_credit: credited line / accepted units / booked price / three-tier reduction / placed net / placed tax / cancelled net / accessories shipped / exempt-state share / tax standing / merchandise tax / final single rounding all quoted and implemented. Implementation narrowings (observations): `accessories_shipped` subtracts `cancelled_net` only when the latest cancelled line is accessories (an order with cancellations in two classes would be mis-netted); `credit_line` reads the LATEST accepted line, so one call covers one line, consistent with "one credit entry for each order line".
- returns_ext_grade_b_restocking: all bindings quoted. The rule places the frequency multiplier after the `restocking_fee_cap_per_unit_usd` cap ("Return frequency then multiplies the restocking fee per unit"; `result: MN(RND(unit_fee * frequency_multiplier, 2), credit_per_unit)`), so a capped 30.00 fee becomes up to 60.00 per unit — see override_declarations F-G2.
- returns_ext_spent_credit_recovery: equivalent.
- returns_ext_courtesy_extension: equivalent except the second start-date tier: the rule says "when the return-by date was set by the return window"; compute takes that branch whenever `days_to_return_by >= window_days`, i.e. also when the return-by date lies beyond the window's last day (observation; bites only on such a world). `window_days` uses `base_return_window_days` only (no footwear, holiday or Quality Issue window) — see override_declarations.
- returns_ext_shoebox_fee: equivalent. `box_credit_per_unit` reads the `returns_refund_credited` entry of the fee line (rule: "It is never larger than the line's merchandise credit per accepted unit"); on a world without that entry the compute evaluates the cap to 0.00 and the fee to 0.00 — an input dependency on another problem's write that no prerequisite sentence and no `prerequisite` edge declares (finding F-C1).
- returns_ext_return_shipping_fee: **not equivalent.** The rule's closing formula sentence, which `compute_basis.result` quotes, is "The return shipping fee withheld is the label fee times the member share, the plan share and the accepted share, multiplied in that order and rounded half up to the cent, less the quick-return reduction and the delivery-failure reduction, never below zero." — it carries no label count, and the label-fee sentence says "charged once per return". `compute.result` multiplies `label_fee * label_count * …`. The label count sentence ("The number of labels follows what travelled: … charged the label fee once per parcel, two parcels …") is in the rule, so the rule yields two readings whenever `label_count ≠ 1` and the shares are non-zero (finding F-P1; consequence only on such a world).
- returns_ext_final_card_refund: equivalent. `owed_after_fees` subtracts every `returns_fee_assessed` entry, including restocking fees, though only the shipping-fee and shoebox-fee entries are declared prerequisites (finding F-C2, bites only where a grade B line is on the return).
- returns_ext_exchange_hold: equivalent. `ie_line` reads the LATEST authorized line and `ie_units` sums all authorized lines of the return (multi-line exchange would mix lines; observation). `stored_balance: CFIELD('credit','balance_usd', status='active')` reads one active instrument; with several active instruments the rule's "the customer's stored-value instrument in status active" is not single-valued (observation; bites only on such a world).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: eight distinct pairs, each claimed by exactly one extended policy; no base policy names a task tool.
- Tool bodies (`task_tools.py`): each looks up `return_cases` by `return_id`, then creates one `return_settlements` row (or, for `extend_return_deadline_be33eaa2`, updates `return_by_date` and `deadline_extensions_used`). None reads status, fees, credits, recoveries or other settlement rows; none refuses a call for an unresolved prerequisite. `pay_final_card_refund_b5173030` refuses any stage other than `final_settlement`, any tender other than `card_or_wallet` and any instrument reference — argument validation of its own action, not a prerequisite judgement.
- Docstrings: no tool names another tool, a policy id, or a position in a sequence. "After the call …" describes the call's own post-state; "the hold stays open on the card until the returned units are received or the hold is charged" (`place_exchange_hold_2c1506d4`) describes the hold's own lifecycle (observation only). `assess_restocking_fee_49fe3caa` / `assess_box_fee_f48699d7` / `withhold_return_shipping_fee_e68e1eec` say "a positive amount" for the fee; a policy outcome of 0.00 (full waiver tiers) has no positive amount to pass (observation; bites only where a waiver tier is taken).
- uuid8s: 1e38d691, 49fe3caa, 4aac9d1c, be33eaa2, f48699d7, e68e1eec, b5173030, 2c1506d4 — eight distinct values, no shared prefix or suffix, no arithmetic progression, none reused. Pass.

### prerequisite_graph

| # | blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | grade_b_restocking | line_credit | value_input | credited_merch | state | credit_inspected_line_1e38d691 |
| E2 | spent_credit_recovery | line_credit | value_input | credits_entered | state | credit_inspected_line_1e38d691 |
| E3 | spent_credit_recovery | grade_b_restocking | value_input | fees_entered | state | assess_restocking_fee_49fe3caa |
| E4 | courtesy_extension | spent_credit_recovery | state_gate | return_settlements.recovered_from | state | authorize_spent_credit_charge_4aac9d1c |
| E5 | final_card_refund | return_shipping_fee | value_input | fees_on_return | state | withhold_return_shipping_fee_e68e1eec |
| E6 | final_card_refund | shoebox_fee | value_input | fees_on_return | state | assess_box_fee_f48699d7 |
| E7 | exchange_hold | final_card_refund | state_gate | return_settlements.refund_stage | state | pay_final_card_refund_b5173030 |

- Every policy has `prerequisite` filled (`[]` for line_credit, shoebox_fee, return_shipping_fee). Every `problem` is an extended id of this file, none a base policy, none self. Graph acyclic (two trees, depth ≤ 3).
- Every `policy_source` located verbatim in its own policy's `rule` (string search over the parsed rule text: 7/7 found).
- `form: state` on all seven; no `fallback_reason` anywhere; consistent.
- `value_input` gates name existing bindings: `credited_merch` (grade_b compute), `credits_entered`, `fees_entered` (spent compute), `fees_on_return` (final compute). Pass.
- `state_gate` gates (E4, E7) name table fields (`return_settlements.recovered_from`, `return_settlements.refund_stage`) rather than an eligibility gate id; extended policies carry no `eligibility` block at all. The rule sentence itself carries the gate, so the agent can discover it; recorded as observation O-G1 (no demonstrable consequence).
- `resolved_by` equals the depended-on policy's `target_tool` in all seven edges, and each tool's effect creates exactly the row the `condition` names (returns_refund_credited / returns_fee_assessed restocking_fee / returns_instant_credit_reversed original_card / returns_fee_assessed method_fee / returns_fee_assessed missing_box_fee / returns_refund_issued final_settlement).
- Authoring-viewpoint phrasing: none of "in this task / at the opening / current world" in the file. The E2 `effect` "rise from nothing to the credited value of the accepted line" and E7 `effect` "The order's inspected return is settled to the card" describe one world rather than the general case (observation O-G2).

### prerequisite_sentences

Four-point test per edge (connective / state named in record words / no tool, id or snake_case / strength equals condition):

- E1 "A restocking fee is worked out only after the line it is charged on carries the credit entry for its accepted units." — "only after"; state = a credit entry on the line (returns_refund_credited, visible through `find_return_settlements`); no tool/id; matches condition. Single writer of a credit entry in this difficulty: `credit_inspected_line_1e38d691` (no other tool creates `returns_refund_credited`). Derivation: sentence → the line lacks a credit entry → the policy whose rule "books one credit entry for each order line whose units were accepted" is line_credit → its tool. Single reading. Pass.
- E2 "The amount charged to the original card for spent instant credit is fixed only after every line accepted at inspection on the return carries its credit entry." — same state, same writer, plural scope matches "Every booking line with an accepted or accepted-with-fee inspection entry". Pass.
- E3 "That card charge is not worked out until every line with units graded B on the return carries its restocking fee entry." — "not … until"; state = restocking fee entry; single writer `assess_restocking_fee_49fe3caa` (the other two fee tools write `missing_box_fee` / `method_fee`). Pass.
- E4 "A return-by date is not moved later until every Store Credit Return of the customer whose spent instant credit exceeds what inspection and fees left owed carries a recovery entry from the original card for that difference." — "not … until"; state = a recovery entry from the original card (returns_instant_credit_reversed, recovered_from original_card); single writer `authorize_spent_credit_charge_4aac9d1c`. Scope "every Store Credit Return of the customer whose …" is an open set stated open, matching the condition. The depended-on rule (spent_credit_recovery) does not restate it. Pass.
- E5 "The final card refund on a return is fixed only after the return carries the return shipping fee entry for the method its parcel travelled by." — "only after"; state = the method fee entry; single writer `withhold_return_shipping_fee_e68e1eec`. Strength: unconditional, while the return shipping fee rule applies only to "a return of a type with `return_method_fee_applies`" (base: Standard Return only). For a return refunded to original tenders whose type carries no method fee (Quality Issue Return; Size Exchange settled by the out-of-stock fallback), the sentence makes the refund wait on an entry no policy ever writes — the sentence is broader than any write can satisfy (finding F-P2; consequence only on such a world).
- E6 "That refund is not paid until every footwear line whose shoebox came back missing, damaged or used as the shipping carton carries its shoebox fee entry." — "not … until"; state = shoebox fee entry; single writer `assess_box_fee_f48699d7`. Same strength caveat for Quality Issue Return (shoebox rule: "an exchange or a Quality Issue Return never does") — F-P2.
- E7 "An Instant Exchange card hold against an order is placed only after every return on that order that has passed inspection carries its final-settlement refund." — "only after"; state = a final-settlement refund entry on every inspected return of the order. Writers of a `final_settlement` refund: `pay_final_card_refund_b5173030` for card/wallet; a refund owed to a stored-value instrument or a Store Credit Return's final Return Store Credit has no tool in this difficulty (the docstring: "refunds owed to a stored-value instrument are booked through the instrument's own ledger and are not paid here"). Whether exactly one write satisfies the state is therefore world-dependent (decided per task).
- Undeclared cross-problem orders: no rule other than the seven sentences states an order between two extended problems. Base rule sentences stating cross-problem order ("Fees are assessed only once the return is in status inspected", "A final-settlement refund is issued only once the return is in status inspected") concern lifecycle states, not another extended problem; no task tree rests on a base sentence.
- Undeclared value dependency (no ordering sentence, no edge): returns_ext_shoebox_fee's cap reads the line's credit entry — F-C1.

### override_declarations

Sentence-by-sentence against every `base_policy_refs` entry (finding half only; consequences are demonstrated in the task files).

- **line_credit vs returns_evt_refund_settlement.** Value = net unit price × accepted units: followed in net effect (the reduction sentence reproduces "booked unit price less its allocated promotion discount, less any price adjustment or late promotion"), but the extended baseline sentence "The line's merchandise credit is its booked unit price times its accepted units" contradicts the base sentence it does not declare as superseded (see factor_ladders F-F1: the factor re-creates base as a ladder over a straw baseline). Tax clause: declared. Shipping clause: the line credit carries "no shipping part"; base puts the original shipping share into the credit on a Quality Issue Return; the shipping clause is declared superseded by final_card_refund instead — accepted as declared on the charter. Promotion claw-back, inspected-status gate, one-row-per-stage-tender: followed.
- **grade_b_restocking vs returns_evt_inspection_restocking.** Per-unit fee clause: declared. Cap: the declaration's replaced_by keeps "capped at `restocking_fee_cap_per_unit_usd`", but the frequency multiplier is applied after the cap, so the fee per unit can reach 2 × 30.00 — an override of the base cap that the declaration does not name (finding F-G2; consequence only where unit fee × multiplier > 30.00). Waiver: base reads the tier "on the authorization date", extended reads "membership in status active" at handling time — an undeclared shift of the time anchor (observation O-G3; bites only where the tier changed in between). Gift Return tier exclusion, both-fees rule, grade C, missing units, fee ≤ credited value, inspected-only: followed. `returns_evt_method_fee` is cited in `base_policy_refs` but no sentence of it is governed by this policy (observation).
- **spent_credit_recovery vs returns_evt_instant_credit.** Negative-difference clause: declared (amount "set out below"). Reversal only once inspected: followed. Base recovery from the Return Store Credit balance first: retained in the spent-shortfall formula ("less the current balance"); no tool of this difficulty claws back that balance, so where the balance is positive a write outside this difficulty's tools is due (decided per task).
- **courtesy_extension vs returns_evt_deadline.** Both conflicting clauses declared. Request-by-return-by-date, status authorized, once per return: followed. "The last day of the return window" is defined in this rule as delivered date + `base_return_window_days` + tier extension, while base returns_authorization defines the window with `footwear_return_window_days`, the holiday extension and the Quality Issue windows; returns_authorization is not in `base_policy_refs` (observation O-G4; bites only for footwear-window/holiday/Quality Issue returns).
- **shoebox_fee vs returns_evt_inspection_restocking.** Box-fee clause declared. Waiver read "in status active" vs base "on the authorization date" (same as O-G3). Both-fees rule followed.
- **return_shipping_fee vs returns_evt_method_fee.** Both conflicting clauses declared. Waiver read "in status active" vs base "on the authorization date" (O-G3). All-rejected rule and method-used rule followed.
- **final_card_refund vs returns_evt_refund_settlement.** Amount and shipping clauses declared. Tender routing: base "original_tenders pays the tenders captured on the order in the orders charter's `tender_refund_priority`, each up to what remains refundable on it (returns_msr_refundable_by_tender)"; extended pays "to that card or wallet" whenever "its order was paid by card or wallet" and drops the refundable cap — undeclared where the order also carries stored-value tenders or the card's refundable remainder is below the refund (finding F-G3; decided per task).
- **exchange_hold vs returns_evt_exchange.** Consent clause declared (replaced by the hold amount set out below). Base: an Instant Exchange is offered only with card/wallet tender and a replacement value ≤ 400.00; hold released/charged rules: followed.

### factor_ladders

Per policy (declared label → audited label):

| policy | factor | label | tiers | audited |
| --- | --- | --- | --- | --- |
| line_credit | post_list_reductions | parameter | 3 | **unreal ladder**: tier 1 value "(adjustment + checkout discount + late credit) / units booked", tier 2 "(checkout discount + late credit) / units booked" when adjustment = 0, fall-through 0 when all are 0 — every tier is the one formula Σreductions / units booked evaluated on its own inputs, so tier 1's value equals tier 2's on every tier-2 record and tier 2's equals the fall-through's on every fall-through record. One tier written as three. Its baseline (booked unit price, reduction 0) is also the straw man of base's standing rule "net unit price paid" (F-F1) |
| line_credit | exempt_goods_tax_basis | method | 3 | honest; multi-source (ship-to state on the order × product class on the line) |
| line_credit | tax_standing_at_dispatch | method | 3 | honest; multi-source (cancellation row × payment captures) |
| line_credit | delivery_charge_tax_split | parameter | 3 | **mislabelled**: the tiers are different formulas (PA/NJ/MN accessories proportion; NY/TX merchandise over merchandise + fee; whole tax) — they change how the quantity is computed (F-F2) |
| grade_b_restocking | restock_price_basis | method | 3 | honest (tier 1 adds back the adjustment only, tier 2 the promotions only: distinct algorithms) |
| grade_b_restocking | member_restocking_percent | parameter | 3 | honest; cross_difficulty loyalty; multi-source (tier + enrolment on the membership × return type on the case) |
| grade_b_restocking | scan_timing_points | parameter | 3 | honest (delivered date × first scan date) |
| grade_b_restocking | return_reason_points | parameter | 3 | honest |
| grade_b_restocking | product_class_points | parameter | 3 | honest |
| grade_b_restocking | return_frequency_multiplier | method | 3 | **mislabelled**: tiers substitute 2 / 1.5 / 1 into the same product fee × m (F-F2) |
| spent_credit_recovery | delivery_record_fee_share | parameter | 3 | honest; cross_difficulty claims |
| spent_credit_recovery | twelve_month_spend_goodwill | method | 3 | **mislabelled**: substitutes 0.8 / 0.9 / 1 into shortfall × f (F-F2) → the policy has **no honest method factor** (F-F3) |
| spent_credit_recovery | membership_tenure_writeoff | parameter | 3 | honest; cross_difficulty loyalty |
| spent_credit_recovery | inspection_wait_credit | parameter | 3 | honest |
| courtesy_extension | membership_tenure_days | parameter | 3 | honest; cross_difficulty loyalty |
| courtesy_extension | unlimited_plan_days | parameter | 3 | honest (pass is not a difficulty; cross_difficulty null is correct) |
| courtesy_extension | packing_units_days | parameter | 3 | honest |
| courtesy_extension | delivery_failure_days | parameter | 3 | honest; cross_difficulty claims |
| courtesy_extension | extension_start_date | method | 3 | honest; multi-source (return-by date on the case × delivered date on the order × tier extension) |
| shoebox_fee | box_condition_amount | parameter | 3 | honest |
| shoebox_fee | member_spend_share | parameter | 3 | honest; cross_difficulty loyalty |
| shoebox_fee | pair_price_class | method | 3 | **mislabelled**: substitutes 1.5 / 0.5 / 1 (F-F2) |
| shoebox_fee | box_return_frequency | method | 3 | **mislabelled**: substitutes 2 / 1.5 / 1 (F-F2) → the policy has **no honest method factor** (F-F3) |
| shoebox_fee | delivery_service_share | parameter | 3 | honest |
| return_shipping_fee | parcel_label_count | method | 3 | honest (fixed 2 / ceil(units/4) / 1 — the middle tier is an algorithm) |
| return_shipping_fee | member_label_share | parameter | 3 | honest; cross_difficulty loyalty |
| return_shipping_fee | unlimited_plan_label_share | parameter | 3 | honest |
| return_shipping_fee | accepted_units_share | method | 3 | accepted (middle tier computes a ratio from records) |
| return_shipping_fee | quick_return_reduction | parameter | 3 | honest |
| return_shipping_fee | delivery_failure_reduction | parameter | 3 | honest; cross_difficulty claims |
| final_card_refund | return_reason_shipping_share | parameter | 3 | honest |
| final_card_refund | shipping_refund_basis | method | 3 | honest (on its own domain the first tier's outcome coincides with the others' because fee 0 × anything = 0 — observation) |
| final_card_refund | service_fee_ceiling | parameter | 3 | honest |
| final_card_refund | delivery_charge_tax_refund | parameter | 3 | **mislabelled**: three different formulas (F-F2) |
| exchange_hold | exchange_value_basis | method | 3 | **unreal ladder**: same collapse as post_list_reductions — "price − (promotions + adjustment)/units" on a tier-2 record (adjustment 0) is tier 2's value, and on a fall-through record is the booked price (F-F1) |
| exchange_hold | exempt_goods_hold_tax | method | 3 | honest; multi-source (state × class) |
| exchange_hold | member_hold_share | parameter | 3 | honest; cross_difficulty loyalty |
| exchange_hold | stored_value_security | parameter | 3 | honest; cross_difficulty credit; multi-source (instrument balance × replacement value from the order line) |
| exchange_hold | prompt_exchange_share | parameter | 3 | honest |

- Every ladder has three pairwise-disjoint tiers as stated, every tier is a sentence of its policy's `rule` and a branch of the `decides` binding, and every fall-through equals the policy `baseline` input (checked factor by factor against `baseline.rule`).
- Counts as declared: line_credit 4 (2 P / 2 M), grade_b 6 (4 P / 2 M), spent 4 (3 P / 1 M), courtesy 5 (4 P / 1 M), shoebox 5 (3 P / 2 M), return_shipping 6 (4 P / 2 M), final_card 4 (3 P / 1 M), exchange_hold 5 (3 P / 2 M).
- Counts after the honesty and ladder tests: line_credit — post_list_reductions struck, delivery_charge_tax_split mislabelled → 2 surviving factors, both method, **0 honest parameter** (bound 2); grade_b — 1 honest method (bound met), frequency multiplier mislabelled; spent — **0 honest method**; courtesy — passes; shoebox — **0 honest method**; return_shipping — passes; final_card — delivery_charge_tax_refund mislabelled, 2 honest parameter remain; exchange_hold — exchange_value_basis struck, 4 remaining with 1 honest method.
- Cross-difficulty factors read loyalty, claims and credit (all three are difficulties of this scenario: loyalty_points_and_rewards, delivery_claims, gift_cards_and_store_credit); orders and pass are not difficulties.
- Realism of conditions and outcomes: every condition is one the returns line weighs (tenure, tier, spend, delivery failures, timing, product class, tax jurisdiction) and no condition holds of every customer reaching its write; no fall-through value is a treatment the business would not publish. No realism finding.

### findings

- **F-F1 (SOURCE-FACTOR, structure)** — unreal ladders `returns_ext_line_credit.post_list_reductions` and `returns_ext_exchange_hold.exchange_value_basis`: tiers are one formula. Bears on task 0 (line_credit) and task 1 (exchange_hold); each task file demonstrates on its world.
- **F-F2 (SOURCE-FACTOR, structure)** — mislabelled effects: method→number on `grade_b_restocking.return_frequency_multiplier`, `spent_credit_recovery.twelve_month_spend_goodwill`, `shoebox_fee.pair_price_class`, `shoebox_fee.box_return_frequency`; parameter→formula on `line_credit.delivery_charge_tax_split`, `final_card_refund.delivery_charge_tax_refund`. Task 0: line_credit, grade_b, spent; task 1: shoebox, final_card.
- **F-F3 (SOURCE-FACTOR, counts)** — after F-F1/F-F2: spent_credit_recovery and shoebox_fee have no honest `method` factor; line_credit has no honest `parameter` factor. Task 0 (line_credit, spent) and task 1 (shoebox).
- **F-P1 (SOURCE-POLICY if demonstrated)** — return_shipping_fee rule/compute: closing formula sentence omits the label count. Task 1 decides whether label_count ≠ 1 on its world.
- **F-P2 (SOURCE-POLICY if demonstrated)** — E5/E6 sentences are unconditional; for a refund-to-original-tenders return type with no method/box fee the waited-on entry is never written. Task 1 decides on its world.
- **F-C1 (SOURCE-CHAIN if demonstrated)** — shoebox_fee's cap reads the line's credit entry, an undeclared value input with no prerequisite sentence. Task 1 decides whether the credit entry is seeded.
- **F-C2 (SOURCE-CHAIN if demonstrated)** — final_card_refund subtracts every fee entry but declares only the method-fee and shoebox-fee edges; a grade B line on the return would make an undeclared restocking-fee write a value input. Task 1 decides.
- **F-G2 (SOURCE-POLICY if demonstrated)** — restocking frequency multiplier defeats the base per-unit cap the declaration keeps. Task 0 decides.
- **F-G3 (SOURCE-POLICY if demonstrated)** — final card refund drops base tender routing and refundable cap. Task 1 decides.
- Observations: O-G1 (state_gate gates name fields, no eligibility block), O-G2 (world-specific `effect` wording), O-G3 (waivers read at handling time, base anchors them to the authorization date), O-G4 (courtesy window omits footwear/holiday/Quality windows; returns_authorization not cited), courtesy start-date tier 2 compute broader than rule, exchange_hold multi-line and multi-instrument reads, fee tools' "positive amount" vs 0.00 waiver outcomes, `returns_evt_method_fee` cited without governed sentence by grade_b and shoebox.

## closing_checklist

Written 2026-10-05T01:00Z, after both tasks' derivations were frozen and their GT revealed. The sections above were frozen before any reveal and are left untouched. **The difficulty is not closed: neither task passes all four relationships.**

| item | status |
| --- | --- |
| Per-task files one-to-one with tasks, `_difficulty.md` alongside | `0.md`, `1.md`, `_difficulty.md` present; first revision, no older revisions |
| Every comparison section carries a PASS | **No** — task 0: SOURCE-FACTOR RED; task 1: SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED |
| Extended policies fully covered; scopes pairwise disjoint | Yes — task 0 `charter_scope` {line_credit, grade_b_restocking, spent_credit_recovery, courtesy_extension}, task 1 {return_shipping_fee, shoebox_fee, final_card_refund, exchange_hold}; union = all 8, intersection empty; matches the two graph components derived blind |
| Task tools and GT closed; uuid8s independent | Yes — 4 + 4 tools, each used only in its own task; uuid8s pass (§ action_binding_and_uuids) |
| Each tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, an owner=user write, no cycle; whole-difficulty graph a DAG | Yes — task 0: n=3, 3 value_input, user write `authorize_spent_credit_charge_4aac9d1c`; task 1: n=3, 2 value_input, user write `place_exchange_hold_2c1506d4`; graph acyclic |
| Every computation: self-sufficient baseline, 4–6 factors (2 parameter, 1 method, honest labels), real ladders, factors bearing weight against an honest baseline, baseline ≠ gold | **No** — every factor of all eight computations bears weight and every baseline gives a definite non-gold number, but: unreal ladders `line_credit.post_list_reductions` (straw baseline against base's standing net-price rule) and `exchange_hold.exchange_value_basis`; mislabels on six factors; spent_credit_recovery and shoebox_fee have no honest method factor; line_credit has no honest parameter factor (F-F1/F-F2/F-F3) |
| Per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor, seeded | Yes — task 0: loyalty, claims; task 1: loyalty, claims, credit; rows present in both seeds |
| Unique solution | Task 0 yes; task 1 **no** (return shipping fee 2.47 / 0.00, refund 128.28 / 130.75 — F-P1 demonstrated) |
| Instantiation-stage gates re-run on the final form | Not re-run by the auditor (Step 0: the auditor cites, does not run gates). The artifacts are unchanged since the coordinator's snapshot: charter `3826dee3…`, tools `607ca8be…` re-hashed at reveal and equal to HASHES.txt; `GATES.txt` therefore stands for the audited form |

Charter-global findings demonstrated on a task world: F-F1 (both tasks), F-F2 (both tasks), F-F3 (both tasks), F-P1 (task 1). Not demonstrated on either world (remain observations): F-P2, F-C1, F-C2, F-G2, F-G3, O-G1–O-G4.

Auditor's own slip disclosed in `1.md` § source_gt_comparison: the frozen exchange_value_basis substitution figure (126.97) held the security share fixed; the correct substitution is 169.29 (GT). The weight verdict is unaffected.

---

## revision_2

### charter_global_frozen (revision_2)

- Auditor: same independent auditor as revision 1. Freeze time: 2026-10-05T04:36Z (audit wall clock), before any round-2 task GT was read.
- Shared inputs moved, so every charter-global section is re-derived in full (not carried forward): `returns.extended.yaml` `3826dee3…` → `f8e50d5ef1ea6b05285c4906bce29a1ff3010e685d08c612af9fa713469b430e`; `task_tools.py` `607ca8be…` → `12afc5a55365cd91a3b7a5fdd8ce16306dc00857fb885f4ec272e2caf8140e73`; both equal `r2/HASHES.txt`. `blueprint/products/returns.yaml` unchanged (`5398b328…`).
- Entry conditions: `r2/GATES.txt` (EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF info; traceability deferred) and `r2/HASHES.txt` supplied; view hashes recomputed and equal (`r2/0.view.json` `820b10eb…fedb`, `r2/1.view.json` `3b1fc545…dffe`). Complete.
- Masked and unread while this section was written: the round-2 `tasks/*.json` and every GT field, `worklog.md`. contamination_disclosure: round-1 GT of both tasks was read during revision 1 (inherent to a re-audit); nothing below draws on it, and no round-2 GT has been seen.
- The revision-1 text above is left untouched.

### base_copy (r2)
Key-by-key equal to `blueprint/products/returns.yaml`; only `extended_policies` added. Pass.

### policy_conflict_scan (r2)
Same eight policies, tools, `computes` and owners as revision 1; fee subjects still split by `fee_type`; no policy changes `return_cases.status`; cross-category reads declared (line_credit now also reads `claims.claim_events`; spent_credit_recovery no longer reads claims; shoebox no longer reads the order's delivery service). Graph components unchanged ({courtesy → spent → {line_credit, grade_b}, grade_b → line_credit} and {exchange_hold → final → {return_shipping_fee, shoebox}}); scopes remain exclusive and complete by structure.

### rule_compute_equivalence (r2)
- line_credit: net unit price, claim compensation ladder, exempt share, tax standing, taxable goods / delivery share / merchandise tax and the single final rounding are each quoted and implemented. The rewritten merchandise-tax sentence ("that tax times the taxable goods that shipped divided by those goods plus the shipping fee times the delivery charge's taxable share") matches `merchandise_tax`.
- grade_b_restocking: the cap now sits after the multiplier in both the rule ("capped at … only after that multiplication") and `result` (`MN(cap, RND(unit_fee × m), credit_per_unit)`). Waiver now requires the tier held since on or before the authorization date (`tier_start_date` ≤ `opened_date`). Equivalent.
- spent_credit_recovery: fee-carry share removed from rule and compute; spend history window by tier and spend share both quoted and implemented. Equivalent.
- courtesy_extension: start-date tier 2 now `days_to_return_by == window_days` (rule "set by the return window") — the revision-1 observation is closed; window adds the tier extension only where `loyalty_window_extension_applies`. Equivalent.
- shoebox_fee: per-unit ceiling now the pair's net unit price paid computed from the order line (no settlement read). Equivalent. **F-C1 closed** (no undeclared read of another problem's write).
- return_shipping_fee: the closing formula now reads "the label fee times the number of labels, the member share, the plan share and the accepted share …", matching `compute.result`. **F-P1 closed.**
- final_card_refund: card-refundable ceiling added to rule and compute (`card_refundable` = card captures and card refunds on the order less refunds on this return). Compute adds `half_up_nudge` 0.000001 before each rounding to realise "rounded half up" on binary floats (implementation detail; observation only). Equivalent.
- exchange_hold: value tier 1 is now the adjustment's reference price (`reference_price_usd`), tier 2 the price paid, tier 3 the booked price. Equivalent.

### action_binding_and_uuids (r2)
Bodies of all eight tools unchanged in behaviour (look up the return; write one row / update return-by date); `pay_final_card_refund_b5173030` still validates only its own stage/tender/instrument. Docstrings: fee amounts now "a non-negative amount … (0.00 when the fee is fully waived)" — the revision-1 positive-amount observation is closed. No docstring names another tool or a sequence position. uuid8s unchanged and distinct. Pass.

### prerequisite_graph (r2)
Same seven edges E1–E7, same kinds, gates, forms, `resolved_by`; all `policy_source` verbatim in their own rules (string check 7/7). Acyclic. `state_gate` gates still name fields (O-G1, residual as claimed). E2/E7 `effect` texts are now general (O-G2 closed). E4 `condition` still says "whose instant credit exceeds its credits less its **carried** fees" though spent_credit_recovery no longer carries a fee share — stale wording, observation O-R2-1 (the rule sentence itself is unaffected).

### prerequisite_sentences (r2)
- E1–E4, E7: unchanged sentences; four-point test passes as in revision 1.
- E5 now "The final card refund on a return whose type carries a return shipping fee is fixed only after …" and E6 "… on a return whose type carries shoebox fees, carries its shoebox fee entry." — scoped to the types whose fee policy writes the entry; conditions scoped identically. **F-P2 closed.**
- No other cross-problem order in any rule. Final card refund still subtracts every fee entry while only method-fee and shoebox-fee edges are declared (F-C2, residual as claimed; bites only where a grade B line is on a card-refunded return).

### override_declarations (r2)
- **line_credit vs returns_evt_refund_settlement — NEW undeclared override (finding F-R2-1).** Base: "For each line, the value credited is the net unit price paid — the booked unit price less its allocated promotion discount, less any price adjustment or late promotion credited on that line — times the accepted units". The extended rule now adds: "A unit is never compensated twice, so compensation a delivery claim already paid on the line is also taken off the net unit price paid before the merchandise credit is worked out: when a merchandise refund was paid … ; when no merchandise refund but a Goodwill Credit was given on the line, that credit divided by the units booked on the line is taken off …". This changes the scored merchandise credit (and, through the share, the tax credited) wherever a claim compensated the line, and `overwrite` names only the tax clause. The extended baseline sentence now restates base's net unit price (the revision-1 straw baseline is gone).
- grade_b_restocking: the cap-after-multiplier change is now named in the declaration's `replaced_by` (**F-G2 closed**); waiver anchored to the authorization date through "held since on or before" (**O-G3 closed** for restocking, shoebox and return shipping fee).
- courtesy_extension: `returns_authorization` now in `base_policy_refs`; the window still omits `footwear_return_window_days`, the holiday extension and Quality Issue windows (O-G4 partly closed, as claimed).
- final_card_refund: the card cap and the hand-off of any remainder to the orders charter's priority are declared in the amount clause's `replaced_by` (**F-G3 closed**; residual: the remainder is "not paid by this action", so a mixed-tender order would need a write outside this difficulty's tools).
- Other policies: as in revision 1.

### factor_ladders (r2)

| policy | factor | label | audited |
| --- | --- | --- | --- |
| line_credit | claim_compensation_taken_off | parameter | honest (refund/units covered; goodwill/units booked; 0); cross_difficulty claims |
| line_credit | exempt_goods_tax_basis | method | honest |
| line_credit | tax_standing_at_dispatch | method | honest |
| line_credit | delivery_charge_taxable_share | parameter | honest (tiers select a share value: accessories/merchandise shipped, 1, 0, entered into one formula) |
| grade_b_restocking | restock_price_basis | method | honest |
| grade_b_restocking | member_restocking_percent, scan_timing_points, return_reason_points, product_class_points | parameter | honest |
| grade_b_restocking | return_frequency_multiplier | parameter | honest (relabelled) |
| spent_credit_recovery | **spend_history_window** | method | **mislabelled**: every tier is "qualifying spend of earning postings summed over the last N calendar months" with N = 36 / 24 / 12 — one aggregate with a different number substituted, i.e. a parameter |
| spent_credit_recovery | spend_goodwill_share | parameter | honest (relabelled); multi-source (membership status × ledger spend) |
| spent_credit_recovery | membership_tenure_writeoff, inspection_wait_credit | parameter | honest |
| courtesy_extension | (five factors) | 4 P / 1 M | unchanged, honest |
| shoebox_fee | box_condition_amount, member_spend_share | parameter | honest |
| shoebox_fee | pair_price_class | parameter | honest (relabelled) |
| shoebox_fee | **reversal_counting_window** | method | **mislabelled**: every tier is "points reversals counted over the last N calendar months" with N = 6 / 18 / 12 — one count with a different number substituted |
| shoebox_fee | box_return_frequency | parameter | honest (relabelled) |
| return_shipping_fee | (six factors) | 4 P / 2 M | unchanged, honest |
| final_card_refund | return_reason_shipping_share, service_fee_ceiling | parameter | honest |
| final_card_refund | shipping_refund_basis | method | honest |
| final_card_refund | delivery_charge_tax_refund | method | honest (relabelled; tiers are three formulas) |
| exchange_hold | exchange_value_basis | method | honest now: reference price / price paid / booked price are three distinct valuations (**F-F1 closed** here) |
| exchange_hold | exempt_goods_hold_tax | method | honest |
| exchange_hold | member_hold_share, stored_value_security, prompt_exchange_share | parameter | honest |

- **F-F1**: closed for both factors (line_credit's collapsed ladder is gone, its baseline is base's own net price; exchange_value_basis now distinct).
- **F-F2**: closed for all six revision-1 mislabels.
- **F-F3: not closed for spent_credit_recovery and shoebox_fee.** The method factor each policy gained is a window length substituted into the same aggregate (above); after the label test both policies keep 4 / 4 honest parameter factors and **0 honest method** (bound 1). line_credit now has 2 parameter + 2 method (closed there).
- Realism (observation O-R2-2): reversal_counting_window counts Silver and Gold members' reversals over 18 months, longer than the 12 months used for customers outside the programme's tiers, so mid-tier members are judged on more of their history than non-members — an unusual direction for a loyalty benefit, though not demonstrably one no retailer would publish.
- Ladders: every ladder has three disjoint tiers stated in its rule, every fall-through equals its baseline input, every baseline sentence is in its rule (string check 8/8).
- Cross-difficulty factors: line_credit (claims), grade_b (loyalty ×2), spent (loyalty ×3), courtesy (loyalty, claims), shoebox (loyalty ×3), return_shipping (loyalty, claims), exchange_hold (loyalty, credit).

### findings (r2) — status of revision-1 items and new items

| item | revision-2 status |
| --- | --- |
| F-F1 | closed |
| F-F2 | closed |
| F-F3 | **open** for spent_credit_recovery (task 0) and shoebox_fee (task 1): new method factors are window-length numbers |
| F-P1 | closed |
| F-P2 | closed |
| F-C1 | closed |
| F-C2 | residual (not demonstrable without a grade B line on a card-refunded return) |
| F-G2 | closed (declared) |
| F-G3 | closed (declared), residual remainder routing outside the tools |
| O-G1 | residual (observation) |
| O-G2 | closed |
| O-G3 | closed |
| O-G4 | partly closed (observation) |
| **F-R2-1 (new)** | undeclared override of base's net-unit-price value sentence by line_credit's claim-compensation deduction — consequence demonstrated in task 0 |
| O-R2-1 (new) | stale "carried fees" wording in E4 `condition` |
| O-R2-2 (new) | reversal window direction for Silver/Gold |

### closing_checklist (revision_2)

Written 2026-10-05T04:40Z after both round-2 GTs were revealed; the revision_2 charter-global sections above were frozen before any reveal. **The difficulty is not closed.**

| item | status |
| --- | --- |
| Per-task files one-to-one, revisions traceable | `0.md`, `1.md`, `_difficulty.md`; revision 1 untouched, revision_2 appended |
| Every comparison carries a PASS | **No** — task 0: SOURCE-POLICY RED (F-R2-1), SOURCE-FACTOR RED (spent_credit_recovery method bound), SOURCE-TASK RED (consequence); task 1: SOURCE-FACTOR RED (shoebox_fee method bound) |
| Coverage / scope exclusivity | Yes — same partition of the 8 policies as revision 1 (`charter_scope` of both r2 tasks) |
| Tools / GT closed; uuid8s | Yes |
| Trees: 1–3 prerequisites, value_input floor, owner=user write, acyclic | Yes for both (n=3; 3 and 2 value_input edges; user writes `authorize_spent_credit_charge_4aac9d1c`, `place_exchange_hold_2c1506d4`) |
| Factors: bounds, honest labels, real ladders, weight, honest baselines | **No** — every factor bears weight and every baseline gives a definite non-gold number, but spent_credit_recovery and shoebox_fee each have 0 honest method factors (their method factors are look-back window lengths) |
| Per task multi-source and cross-difficulty, seeded | Yes (task 0: claims, loyalty; task 1: loyalty, claims, credit) |
| Unique solution | Task 0 **no** (F-R2-1: 116.00/9.28 → 23.04 → 108.87 vs 101.00/8.08 → 20.34 → 119.67); task 1 yes |
| Gates on the final form | Not re-run by the auditor; charter and tools re-hashed at reveal equal `r2/HASHES.txt`, so `r2/GATES.txt` stands for the audited form |

Round-1 items closed: F-F1, F-F2, F-P1, F-P2, F-C1, F-G2, F-G3 (declared; residual remainder routing), O-G2, O-G3, task 1 finding 5. Partly closed: O-G4. Residual: F-C2, O-G1. Open: F-F3 (spent_credit_recovery, shoebox_fee). New: F-R2-1 (SOURCE-POLICY, task 0), task 0 proof figures 25.42 / 15.25 (should be 25.43 / 15.26), O-R2-1, O-R2-2. Nothing that passed in revision 1 regressed except through the new F-R2-1, which the rework introduced.

---

## revision_3

### charter_global_frozen (revision_3)

- Freeze time 2026-10-05T05:04Z (audit wall clock), before any round-3 task GT was read. Same auditor.
- `returns.extended.yaml` changed `f8e50d5e…430e` → `3566a1fd55515c04848885901a98616734e92efacb73d3e5ff509c311eebb789`, so the charter-global sections are re-derived; `task_tools.py` unchanged (`12afc5a5…0e73`), so § action_binding_and_uuids is carried forward from revision_2 on that hash. Both equal `r3/HASHES.txt`. `r3/GATES.txt`: seven gates OK, CACHE-DIFF info, traceability deferred. Views `r3/0.view.json` / `r3/1.view.json` are byte-identical to r2 (same sha256 `820b10eb…fedb` / `3b1fc545…dffe`): worlds and personas unchanged.
- Masked and unread before freeze: round-3 `tasks/*.json`, `worklog.md`. contamination_disclosure: round-1 and round-2 GT of both tasks were read in earlier revisions; values whose inputs did not change this round are therefore not independently blind.
- Earlier revisions untouched.

### base_copy / policy_conflict_scan / prerequisite_graph / prerequisite_sentences (r3)
Base copy key-by-key equal (pass). Same eight policies, tools, `computes`, owners, seven edges E1–E7 with the same kinds, gates, forms and `resolved_by`; all `policy_source` verbatim in their rules (7/7); acyclic; graph components and scope partition unchanged. E4 `condition` now reads "whose instant credit exceeds its credit entries less its fees withheld plus its store-credit balance" — matches the spent-shortfall formula (**O-R2-1 closed**). No new cross-problem order in any rule.

### override_declarations (r3)
- line_credit now carries a second `overwrite` naming base returns_evt_refund_settlement's value sentence ("For each line, the value credited is the net unit price paid — … — times the accepted units") with `replaced_by` the claim-compensation sentence. Merged semantics: net unit price paid, less any delivery-claim compensation per the ladder, times accepted units — single reading. **F-R2-1 closed.**
- Other declarations as in revision_2 (F-G2, F-G3 declared; O-G4 partial; F-C2 residual).

### rule_compute_equivalence (r3)
- spent_credit_recovery: `spend_history` = MX(earned 12m, earned in the 12 months before) for Platinum/Icon/Atelier; earned 12m for Gold; earned 12m − reversed spend 12m otherwise — each tier quoted in the rule ("better membership year", "gross spend", "kept spend"). Equivalent.
- shoebox_fee: `return_rate` = reversed points / (earned + bonus points) for Platinum/Icon/Atelier; reversed spend / qualifying spend for Silver/Gold; reversal count / orders placed otherwise, each over `rate_months` and 0 when the divisor is 0; multiplier on rate thresholds 0.5 / 0.2. Each tier quoted in the rule. Equivalent.
- grade_b_restocking now adds `half_up_nudge` before each rounding (as final_card_refund already did) — implementation of "rounded half up" on binary floats; observation only.
- All other policies as revision_2.

### factor_ladders (r3)
- spent_credit_recovery: **spend_measure_basis** (method) — better-of-two-years maximum / gross 12-month sum / 12-month sum net of reversed spend: three different aggregates over different records (two windows; earnings only; earnings and reversals). Honest method. Fall-through (kept spend) = its baseline. Plausible treatments (more generous measures for higher tiers). Counts 3 P / 1 M. **F-F3 closed** here.
- shoebox_fee: **return_rate_measure** (method) — points ratio / value ratio / count ratio over different record sets (ledger points; ledger spend; ledger reversals over orders). Honest method; fall-through (by count) = its baseline. box_return_frequency (parameter) now tiers on rate thresholds. Counts 4 P / 1 M. **F-F3 closed** here; **O-R2-2 closed** (tiers no longer lengthen the look-back).
- line_credit, grade_b, courtesy, return_shipping, final_card, exchange_hold: unchanged from revision_2, honest.
- Cross-difficulty: spent (loyalty ×3), shoebox (loyalty ×3), others as revision_2.

### findings (r3)

| item | status |
| --- | --- |
| F-R2-1 | closed (declared) |
| F-F3 (spent_credit_recovery, shoebox_fee) | closed |
| O-R2-1, O-R2-2 | closed |
| F-C2, F-G3 residual, O-G1, O-G4 partial | unchanged residuals / observations, not demonstrable on either world |
| New charter-level defects | none found |

### closing_checklist (revision_3)

Written 2026-10-05T05:06Z after both round-3 GTs were revealed; the revision_3 charter-global sections above were frozen before any reveal. **The difficulty passes the source-layer audit.**

| item | status |
| --- | --- |
| Per-task files one-to-one, revisions traceable, every comparison PASS | Yes — `0.md` and `1.md` revision_3 comparisons both PASS on all four relationships; revisions 1 and 2 untouched |
| Coverage / scope exclusivity | Yes — the 8 extended policies split 4 / 4 between the tasks (`charter_scope`), disjoint and complete |
| Tools / GT closed; uuid8s independent and frozen | Yes (tools unchanged since revision_2) |
| Trees: 1–3 prerequisites, ≥ max(n−1,1) value_input, owner=user write, acyclic; difficulty graph a DAG | Yes — task 0: n=3, 3 value_input, user `authorize_spent_credit_charge_4aac9d1c`; task 1: n=3, 2 value_input, user `place_exchange_hold_2c1506d4`; seven edges acyclic |
| Every computation: self-sufficient baseline, 4–6 factors, ≥2 P / ≥1 M honest, real ladders, weight against honest baselines, baseline ≠ gold | Yes — all eight computations (line_credit 2P/2M, grade_b 5P/1M, spent 3P/1M, courtesy 4P/1M, shoebox 4P/1M, return_shipping 4P/2M, final_card 2P/2M, exchange_hold 3P/2M); every factor bears weight on its task's world and every whole baseline differs from gold |
| Per task ≥1 multi-source and ≥1 cross-difficulty factor, seeded | Yes — task 0: claims, loyalty; task 1: loyalty, claims, credit |
| Instantiation-stage gates on the final form | Not re-run by the auditor (cited per Step 0): `r3/GATES.txt` all green; charter `3566a1fd…b789` and tools `12afc5a5…0e73` re-hashed at reveal equal `r3/HASHES.txt` |

Residual observations carried (no demonstrated consequence on either world, not grounds for rework): F-C2 (final card refund subtracts every fee though only method/shoebox edges are declared), F-G3 remainder routed outside this difficulty's tools, O-G1 (state_gate gates name fields), O-G4 partial (courtesy window omits footwear/holiday/Quality Issue windows), `half_up_nudge` implementation detail.

---

## revision_4

### charter_global_frozen (revision_4)

- Freeze time 2026-10-05T07:06Z (audit wall clock), before any round-4 task file was read. Same auditor.
- Inputs: `returns.extended.yaml` `3566a1fd…b789` — **unchanged** from revision_3; `task_tools.py` `12afc5a5…0e73` → `64a21ea5ba484d7022c9b4a2370d77208ce1a4a630dc71a2c1586dc5f06e394c`; views `r4/0.view.json` `820b10eb…fedb` and `r4/1.view.json` `3b1fc545…dffe` — byte-identical to r2/r3. All equal `r4/HASHES.txt`. `r4/GATES.txt`: seven gates OK, CACHE-DIFF info, traceability deferred.
- Carried forward by reference on the unchanged charter hash: revision_3 § base_copy, § policy_conflict_scan, § override_declarations, § rule_compute_equivalence, § prerequisite_graph, § prerequisite_sentences, § factor_ladders. Re-derived: § action_binding_and_uuids (tool module moved).
- Noted before reveal, not opened: `tasks/0.json` and `tasks/1.json` sha256 are now `18837036…6cf2` and `0ab42756…0b6d`, different from the hashes recorded at the revision_3 reveal (`57daa52a…69c6`, `c95d05c1…fe7e`), although the round-4 brief says the task files are unchanged. To be explained at reveal.
- contamination_disclosure: GT of rounds 1–3 was read in earlier revisions.

### action_binding_and_uuids (revision_4)

- **Runtime contract (the validator defect):** the module now imports only `from erlbench import ToolContext, tool`; no `datetime`, `time` or any other clock or id source. Every write still dates entries with `ctx.now()[:10]` and ids with `ctx.make_id(...)`. Closed.
- **Seven unchanged tools:** AST comparison of `credit_inspected_line_1e38d691`, `assess_restocking_fee_49fe3caa`, `authorize_spent_credit_charge_4aac9d1c`, `assess_box_fee_f48699d7`, `withhold_return_shipping_fee_e68e1eec`, `pay_final_card_refund_b5173030`, `place_exchange_hold_2c1506d4`: decorators/owners, signatures, lookups, `make_id` keys, created fields and return sentences are identical to the bodies audited in revisions 1–3. Docstrings unchanged, including the revision_2 "non-negative amount" fee contracts (three fee tools; with the credit tool's tax argument, 4 "non-negative amount" occurrences).
- **`extend_return_deadline_be33eaa2`:** same decorator (`owner="agent"`, `rw="write"`), signature, docstring, lookup, error sentence, `deadline_extensions_used` increment and return sentence. The new-date arithmetic changed from `(date(y, m, d) + timedelta(days=extension_days)).isoformat()` to inline month-length arithmetic with a Gregorian leap rule (`y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)`), stepping forwards for positive and backwards for negative day totals, zero-padded `YYYY-MM-DD`. Equivalence test against the old expression, run by executing the extracted function body with a stub context:
  - every calendar date 1999-01-01 … 2100-12-31 × extensions {1, 7, 10, 11, 14, 21, 28, 29, 30, 31, 35, 45, 60, 61, 90, 365, 366, 400, 730, 1461};
  - every date 2020-01-01 … 2031-12-31 × every extension −70 … 139 (including 0 and negatives);
  - 1,665,530 cases, **0 mismatches** in the new return-by date and the extension count. These cover month-end, year-end (12-31 + 1 → next year 01-01), leap days (2028-02-28 + 1 → 02-29), century non-leap (2100-02-28 + 1 → 03-01) and the 400-year leap (2000-02-28 + 1 → 02-29). A stored value with a time suffix (`YYYY-MM-DD 00:00:00`) is read from its first 10 characters, as before.
  - The only divergence is on impossible stored dates (e.g. `2026-04-31`): the old code raised `ValueError`, the new code rolls over. No seed row and no tool of this difficulty can hold or write such a date (the only writer of `return_by_date` is this tool and it emits only valid dates; seeded values are valid), so the difference is unreachable — observation only.
  - Reachable inputs: positive integer extensions (the courtesy-extension policy's result is a sum of non-negative day counts that includes `deadline_extension_days` or more), applied to seeded return-by dates in 2026. Behaviour on that domain is identical.
- The tool still judges no prerequisite (no read of settlements, statuses or dates other than the current return-by date). uuid8s unchanged. Pass.

### findings (revision_4)

| item | status |
| --- | --- |
| Runtime-contract defect (`from datetime` in task_tools.py) | closed; behaviour unchanged on every valid input |
| Round-3 REDs | none were open (revision_3 closed with all PASS) |
| Residual observations (F-C2, F-G3 remainder, O-G1, O-G4 partial) | unchanged, carried from revision_3 |
| New | observation O-R4-1: impossible stored dates now roll over instead of raising (unreachable) |

### closing_checklist (revision_4)

Written 2026-10-05T07:08Z after both round-4 task files were revealed; the revision_4 charter-global sections above were frozen before the reveal. **The difficulty passes the source-layer audit.**

| item | status |
| --- | --- |
| Per-task files one-to-one, revisions traceable, every comparison PASS | Yes — `0.md`, `1.md` revision_4 comparisons PASS on all four relationships; revisions 1–3 untouched |
| Coverage / scope exclusivity | Yes (unchanged: 4 / 4 partition of the 8 policies) |
| Tools / GT closed; uuid8s | Yes — module no longer imports a real clock; seven tools unchanged; the extension tool behaviour-identical on all valid dates (1,665,530 cases, 0 mismatches) |
| Trees, value_input floor, owner=user writes, DAG | Yes (unchanged) |
| Factors: bounds, honest labels, real ladders, weight, honest baselines | Yes (unchanged; figures re-confirmed against the round-4 task files) |
| Per task multi-source and cross-difficulty, seeded | Yes (unchanged) |
| Instantiation-stage gates on the final form | Cited, not re-run: `r4/GATES.txt` all green; charter `3566a1fd…b789` and tools `64a21ea5…394c` re-hashed equal `r4/HASHES.txt` |

Observations: O-R4-1 (impossible stored dates now roll over instead of raising; unreachable), O-R4-2 (task-file hashes changed since the revision_3 reveal despite the brief; all scored and proof fields identical); residuals F-C2, F-G3 remainder, O-G1, O-G4 partial unchanged.
