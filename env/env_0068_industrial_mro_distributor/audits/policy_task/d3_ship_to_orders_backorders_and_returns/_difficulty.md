# Policy-task audit — d3_ship_to_orders_backorders_and_returns / charter-global

## revision_1

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision_1. Freeze time 2026-10-16T23:46Z. Written before any task's GT was revealed; nothing in this section comes from a revealed GT.
- Frozen inputs (sha256, re-verified at audit start, all matching the brief):
  - `03e4ccf007399381225ed24faa0575b5a38c3624654e3e3a4d7cee040ea03907  tasks/d3_ship_to_orders_backorders_and_returns/order.extended.yaml`
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  tasks/d3_ship_to_orders_backorders_and_returns/task_tools.py`
  - `d239239e2786c4577cd20d5260039afe3b0b0fc3a1092fe5926709399b46b407  .audit_views/policy/d3_ship_to_orders_backorders_and_returns/r1/task0.view.json`
  - `df6f098c6ab9328e6abd32a0a1bb8ce730fd12167f8290aac2cb4f7cdcc85ac7  .audit_views/policy/d3_ship_to_orders_backorders_and_returns/r1/task1.view.json`
- Fields permitted: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), audits/render_source/XF_recipe.md.
- Fields masked and not opened before every freeze: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plan.md, worklog.md. No recursive search was run over tasks/ or the scenario root. The DSL evaluator (skills/erl-task-instantiate/scripts/check_compute.py) was not read: it is outside the read domain; all figures here are from the rule text, recomputed by the auditor's own scratch scripts in /tmp/audit_d3_ship_to_orders_backorders_and_returns_0068/.
- Entry conditions (Step 0): gate snapshot supplied with the brief and saved at `.audit_views/.../r1/gates.txt` — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred to KB publication as stated. Masked views present with hashes. Input complete.
- Base-copy check: lines 1–818 of `order.extended.yaml` are byte-identical to `blueprint/products/order.yaml` (`diff` empty). The base section is verbatim.

### policy_conflict_scan

Extended policies (4): `order_ext_anniversary_review` (agent, `record_anniversary_review_a2ef3cef`, variant_name), `order_ext_stock_rotation_return` (user, `submit_stock_rotation_return_550cd403`, quantity), `order_ext_reactivation_level` (agent, `reactivate_ship_to_971b9440`, variant_name), `order_ext_requested_move_up` (user, `elect_service_level_move_6cd24a6d`, variant_name).

Overlap scan:
- Subjects: anniversary review and requested move-up both claim `order_service_level_changed`; they differ in trigger (state_due / on_request), tool and scope (the move-up's own rule keeps every non-Parcel/Standard ship-to at its level "under this rule"). Both tools write `variant_name` and `last_review_date`; the reactivation tool writes `status` and `variant_name`. No two policies set the same field for the same trigger.
- Time anchors: anniversary review windows end on "the review date" (see finding C3: undefined between the anniversary and the day performed); rotation, reactivation and move-up windows end on the request / reactivation date (= the day of the call). Rotation tenure and reactivation tenure count whole months from `opened_date`.
- Terminal states: reactivation sets status active; the other three leave status alone. The anniversary review's "most recent anniversary that has no review on or after it" is read from `last_review_date`, which the requested move-up also stamps (observation O1).
- Cross-category read boundaries: rotation reads pricing (agreement tier, commitment, item price lines), credit (status, returned payments), vmi (program status, replenishment billed); reactivation reads credit (returned payments, finance charges) and vmi (program status/tier); move-up reads vmi (status, replenishment billed), vending (status, usage billed), credit (status, returned payments 24/12 m) and pricing (commitment). The move-up's vmi read collides with an in-force vmi base clause (finding C1).
- Scope exclusivity: by the persona/root pairing, task 0 = {order_ext_stock_rotation_return (root), order_ext_anniversary_review}; task 1 = {order_ext_requested_move_up (root), order_ext_reactivation_level}. Disjoint and jointly complete over the four extended policies (confirmed against charter_scope only after the reveal; see the per-task files).

### rule_compute_equivalence

Scratch sweep (whitespace-normalised substring test) over every `compute_basis` value: all 76 quotes are verbatim in their own rule; every `baseline.rule` sentence is in its rule; every `overwrite.replaced_by` and every `policy_source` is in its rule. Compute bindings with no `compute_basis` entry: `order_ext_anniversary_review.held_level` and `.route_level_held` (both covered verbatim by the `held_gate` and `review_pct` quotes; observation O2).

Per policy, sentence by sentence (S-numbers are rule sentences in order):
- anniversary review: S2 result ↔ `result` (`shipped_12 > 0` ↔ "shipped order_line_shipped merchandise"); S3 ↔ `spend_12`; S4 ↔ `held_gate`/`review_threshold`; S5 ↔ `level_below`; S6 "compared to the cent, without rounding" ↔ no RND anywhere (XF7 ok); S7 ↔ `route_runs_12`/`review_pct` (order_line_shipped by route_truck only); S8 ↔ `spend_6`, `pace_weight_6/12` (conditions on figures "as booked", weights applied to counted figures); S9/S10 ↔ `dropship_*`/`willcall_*` (share decided on the 12-month weight, applied to both windows); S11 ↔ `counted_12/6`, `review_spend` (counted first, then pace — XF3 order stated; the two subtractions commute). No compute invention found; S1 (one review per anniversary, recorded on the day performed) is procedural and has no binding.
- stock rotation return: S1 ↔ `rot_order/rot_line/rot_sku/rot_requested` (LATEST, `or 0`); S3 RMA unit price ↔ `last_ship_price`; S5 ↔ `result`; S6 ↔ `returnable_qty`; S7 ↔ `all_merch_12`; S8–S10 ↔ `gross_allowance`, `allowance` (RND 2 after cap, XF7 ok), `allowance_units` (floor); S11 order sentence ↔ `gross_allowance` = (base+program) × rate × standing; S12 ↔ `rotation_rate_pct`; S13 ↔ `purchase_base`; S14 ↔ `standing_pct`; S15 ↔ `program_added`; S16 ↔ `unit_value` (DAYS(...) > 0 = "after"; RND 4 on the average); S17 ↔ `allowance_cap`. Divergences: the placement of the standing share (finding C2); "the line's most recent shipment" vs the compute's order_line_shipped-only filter, the unstated zero-unit-value branch, and the S1 eligibility filter (unopened, stocked, returnable class) absent from compute (finding C8); unstated tie / ordering rules for the three LATEST reads (finding C6).
- reactivation level: S1 ↔ `level_rank` (MX 1); S2 ↔ `prior_level`; S3 ↔ `prior_rank`; S4 ↔ `drops_added` (MX 0) and `drops_total`; S5–S9 ↔ the five ladders. Equivalent. The "never below zero" floor in S4 only has work to do if take-backs are inside the sum, which fixes the take-back-before-tenure order the compute uses (observation O4).
- requested move-up: S1 ↔ `next_level/next_gate/result` (next_gate 0 keeps the level); S4 ↔ gates; S5 ↔ `own_12`; S6 ↔ `result` (>=, no rounding); S7 ↔ `own_6`, `repl_*`, `vend_*`; S8 ↔ `repl_share`; S9 ↔ `standing_share`; S10 ↔ `vend_share`; S11 ↔ `total_*`, `growth_weight_*`; S12 ↔ `gate_share`; S13 ↔ `counted_site_*`, `move_measure`. `applied_gate` multiplies the two gate shares; no sentence states the combination generically, S9 says only "further applied" (observation O3).

### action_binding_and_uuids

- `(target_tool, computes)`: (record_anniversary_review_a2ef3cef, variant_name), (submit_stock_rotation_return_550cd403, quantity), (reactivate_ship_to_971b9440, variant_name), (elect_service_level_move_6cd24a6d, variant_name) — each claimed by exactly one policy.
- uuid8s a2ef3cef / 550cd403 / 971b9440 / 6cd24a6d: no shared prefix, suffix or sequence; no reuse; consistent with independent generation.
- Docstrings: each effect claimed is in the body (XF8): review sets variant_name + last_review_date; rotation creates one order_return_authorized row with return_reason no_longer_needed, return_method customer_shipped, item_class standard, stock_status stocked and no credit/fee; reactivation sets status active + variant_name; election sets variant_name + last_review_date. No concrete example values (formats only: SO-NNNNNNN, RMA-NNNNNN, YYYY-MM-DD). No other tool named; no sequence word about other actions ("once stored" describes the call's own effect). The hard-coded `item_class="standard"` agrees with the rule, since every other item class in db_schema (cut_to_length, hazmat, calibrated_instrument) is non-returnable.
- No tool body checks a business precondition (no status, review, window or quantity test) — confirmed by reading all four bodies.

### prerequisite_graph

- `prerequisite` filled on all four: anniversary `[]`, reactivation `[]`, rotation → order_ext_anniversary_review, move-up → order_ext_reactivation_level. Both `problem`s are extended ids in this file, neither self, graph acyclic (two disjoint 2-node chains).
- rotation edge: kind value_input, gate `rotation_rate_pct` (exists in compute), form action with fallback_reason, policy_source verbatim in the rotation rule (S4), resolved_by = anniversary target_tool; effect (rate read from the reviewed level) holds through `route_level_now`/`mid_level_now` reading F('variant_name').
- move-up edge: kind value_input, gate `held_level_now` (exists), form state, no fallback_reason, policy_source verbatim (S2), resolved_by = reactivation target_tool; the effect holds (held_level_now reads the reactivated variant_name).
- `condition` fields: rotation's matches the sentence; the move-up's adds "and its variant_name is the level it was reactivated at" to the sentence's "status is active" — a description of the value effect rather than an extra gate (observation O5). No authoring-viewpoint phrasing in any prerequisite field.

### prerequisite_sentences

- Rotation: "The stock-rotation allowance is fixed only after the review of the ship-to's service level for its most recent opening anniversary has been recorded." Connective "only after"; action form, the review named in business words; no tool, id or snake_case token; strength equals the condition. Fallback test: the review leaves `variant_name` and `last_review_date`, which `elect_service_level_move_6cd24a6d` also writes, so no record-visible state singles out the review — the fallback is justified. Derivation: sentence → "the review of the ship-to's service level for its most recent opening anniversary" → the only rule describing an anniversary review is order_ext_anniversary_review → its write. Single reading. The anniversary rule does not restate the sentence.
- Move-up: "A requested move up is not decided until the ship-to's status is active." Connective "not … until"; state form (`status` = active, the table's own words); no tool/id/token. Exactly one write of this difficulty makes a ship-to active: `reactivate_ship_to_971b9440` (the review and election tools do not touch status; pending_setup→active is a system transition with no task tool). Derivation: sentence + suspended status on the record → order_ext_reactivation_level ("reactivated by the agent at the customer's request") → its write. Single reading. The reactivation rule does not restate the sentence.
- No rule states any other cross-problem order; no base sentence grounds an edge.

### override_declarations

- order_ext_anniversary_review vs order_ship_to_lifecycle S2 first half ("At each anniversary … moves down one service level"): retired by its overwrite; replaced_by names its scope ("for the anniversary review … and only for that review"), declares the no-merchandise departure and hands the move-up half back. Lifecycle S1, S3, S4 untouched and inherited. vs order_agg_ship_to_portfolio: S1/S2/S4 followed (per ship-to, no pooling, single credit account); S3 (entry gates measured on own trailing 12-month spend) is about meeting an entry gate, not the downgrade test, and is not overwritten — observation O11, no conflict demonstrated.
- order_ext_stock_rotation_return vs order_evt_returns S2 (customer-reason window): retired; replaced_by restates the window for every other customer-reason return and names the stock-rotation scope. Every other base sentence (non-returnable classes, special order, opened items, RMA validity, inspection, restocking/label fees, credit basis, issue days, returnable-quantity cap) is inherited; the rotation rule's S3 says receipt, inspection, fee and credit follow the return rules. The S1 eligibility statement ("unopened stocked merchandise of a returnable item class") is inherited base content that the compute does not implement (C8).
- order_ext_reactivation_level vs order_ship_to_lifecycle S1 second half (reactivated "at its prior service level"): retired; replaced_by restates the no-orders and credit-active provisos. Lifecycle S1 first half (suspension) inherited.
- order_ext_requested_move_up vs order_ship_to_lifecycle S2 second half (move up when trailing spend meets the higher gate; route ZIP) and vs order_agg_ship_to_portfolio S3: both retired; each replaced_by names the Parcel/Standard scope "and only such" and restates the base rule for Priority and route levels. No sibling overwrite retires the same clause.
- Cross-category: vmi base `vmi_agg_program_portfolio` S2 "Program spend does not count toward the served ship-to's order minimum, free freight threshold or service level spend" is in force and contradicted by the move-up's S7/S8/S13 — undeclared and undeclarable from this charter (finding C1). No other base clause of credit, pricing, vmi or vending is contradicted (scan of "count toward"/"service level" in all product charters).

### factor_ladders

| policy | factor | label | decides | tiers | multi-source | x-difficulty | ladder in rule | structural verdict |
|---|---|---|---|---|---|---|---|---|
| anniversary | review_route_use_pct | parameter | review_pct | 3 (85/80/70 %) | yes (variant_name AND order_lines route count) | — | S7 | ok |
| anniversary | review_pace_window | method | pace_weight_6/12 | 3 | no | — | S8 | **mislabelled (C4)** |
| anniversary | review_dropship_share | parameter | dropship_share | 3 (0/50/100) | no | — | S9 | ok |
| anniversary | review_willcall_share | parameter | willcall_share | 3 (25/50/100) | no | — | S10 | ok |
| rotation | rotation_rate | parameter | rotation_rate_pct | 3 (10/7/5) | no (both conditions on the ship-to row) | — | S12 | ok |
| rotation | rotation_base_scope | method | purchase_base | 3 (category 12 m / sku 24 m / all 12 m) | no | pricing | S13 | ok (O10) |
| rotation | rotation_standing | parameter | standing_pct | 3 (0/50/100) | tier 2 yes | credit | S14 | ok; placement ambiguous (C2) |
| rotation | rotation_program_share | parameter | program_added | 3 (full/50 %/0) | no | vmi | S15 | ok (O7) |
| rotation | rotation_unit_value | method | unit_value | 3 (later lower contract price / weighted average / last price) | yes | pricing | S16 | ok; reads C8 |
| rotation | rotation_cap | parameter | allowance_cap | 3 (8000/4000/1500) | no | pricing | S17 | ok |
| reactivation | dormancy_level_drops | parameter | dormancy_drops | 3 (2/1/0) | no | — | S5 | ok |
| reactivation | lost_route_drops | parameter | route_drops | 3 (2/1/0) | yes | — | S6 | **unreal condition (C5)** |
| reactivation | payment_level_drops | parameter | payment_drops | 3 (2/1/0) | no | credit | S7 | ok |
| reactivation | stocksmart_takeback | parameter | program_takeback | 3 (2/1/0) | no (status and tier on one row) | vmi | S8 | ok |
| reactivation | tenure_adjustment | method | tenure_rule | 3 (halve / minus one / as added) | no | — | S9 | ok |
| move-up | site_growth_window | method | growth_weight_6/12 | 3 | no | — | S11 | **mislabelled (C4)** |
| move-up | replenishment_counted | parameter | repl_share | 3 (100/50/0) | no | vmi | S8 | ok |
| move-up | standing_gate_share | parameter | standing_share | 3 (90/95/100) | yes | credit | S9 | ok |
| move-up | vending_counted | parameter | vend_share | 3 (100/50/0) | no | vending | S10 | ok |
| move-up | commitment_gate_share | parameter | gate_share | 3 (85/92/100) | no | pricing | S12 | ok |

Structure checks: every `decides` is an input, never `result`; binding sets are pairwise disjoint within each policy; every ladder has three pairwise-disjoint tiers with distinct outcomes, every tier stated in its own rule sentence with condition and value/method, and every compute branch is a stated tier. Baselines: every factor baseline equals what `baseline.rule` gives for that input (rate = rotation_rate_pct, scope = all 12 m, share 100, program 0, unit value = last shipment price, cap = rotation_cap_usd; drops 0, tenure "as added"; pace/growth weights (0,1), shares 100 / 0) and every fall-through tier is that baseline. Each `baseline.rule` is self-sufficient (a definite number from the records with no factor).

XF1 independence: no factor tier reads another factor's binding. Single-factor quantities outside the factor's bindings: `rot_category` (read only by `category_merch_12`, a rotation_base_scope binding) and `last_ship_date` (read only by `lower_contract_after_ship`, a rotation_unit_value binding) — finding C9. All other plain bindings are shared by two or more parts or by the baseline (`shipped_12`, `spend_12`, `rot_sku`, `prior_level`, `site_program_id`, `site_machine_id`, `own_6`/stream bindings shared by the growth factor's totals and the counted figures).

XF11 method tiers, pairwise table:
- review_pace_window / site_growth_window: every tier is the one expression w12·counted_12 + w6·counted_6, the tier choosing (w12, w6) ∈ {(0, 2), (0.5, 1), (1, 0)} — the compute itself encodes the method as two numeric bindings. Tiers 1 and 3 are a swapped window (6 vs 12 months) with a swapped multiplier (2 vs 1); tier 2 is the same sum with intermediate weights. This is exactly the "swapped multiplier or window length" XF11 excludes, and the skill's "a factor labelled method whose tiers only substitute a different number into the same formula" (C4).
- rotation_base_scope: category filter vs sku filter + 24-month window vs no filter; tiers select different record populations (distinguishing input: any shipped line outside the item's category). Accepted as method; its sku tier additionally swaps the window (O10).
- rotation_unit_value: contract-price lookup vs quantity-weighted average vs latest shipment price; distinguishing inputs: a later lower contract line; two shipments at different prices. Distinct.
- tenure_adjustment: floor(x/2) vs max(0, x−1) vs x — division vs subtraction; distinguishing input x = 4 (2 / 3 / 4). Distinct.

Realism (B2B MRO distributor): review threshold raised for route levels that barely use the route truck; run-rate review for steeply declining sites; drop-ship and will-call merchandise discounted in a delivery-service review; rotation allowance of 5–10 % of trailing purchases, net of customer-reason credits, capped by commitment, halved after a returned payment, valued at a later lower contract price; reactivation drops for long dormancy and payment marks, softened by a live StockSmart program and long tenure; move-up gates eased for committed and clean-paying customers — all are treatments a distributor publishes. The exceptions are C5 (a condition that every suspended ship-to satisfies) and the tension in O7.

Counts per policy (before strikes): anniversary 4 (3 P, 1 M), rotation 6 (4 P, 2 M), reactivation 5 (4 P, 1 M), move-up 5 (4 P, 1 M). After the C4 and C5 strikes: anniversary 3 (3 P, 0 M) — fails the 4-factor and 1-method floors; rotation 6 (4 P, 2 M) — ok; reactivation 4 (3 P, 1 M) — ok; move-up 4 (4 P, 0 M) — fails the 1-method floor. Per-task multi-source / cross-difficulty: task 0 has review_route_use_pct and rotation_unit_value (multi-source) and four cross-difficulty factors; task 1 has standing_gate_share (multi-source; lost_route_drops struck) and five cross-difficulty factors.

### findings

Charter-global REDs (each names the tasks it bears on; the demonstration against a world lives in that task's file):

- **C1 — SOURCE-POLICY RED (XF5, undeclared cross-category contradiction).** Symptom: two in-force clauses settle opposite answers for whether StockSmart replenishment counts toward a ship-to's service-level spend. Evidence: `blueprint/products/vmi.yaml` vmi_agg_program_portfolio S2 "Program spend does not count toward the served ship-to's order minimum, free freight threshold or service level spend…"; order_ext_requested_move_up S8 "StockSmart replenishment counts in the site spend of each period in full where the program serving the ship-to is active…" with S13 adding it into the counted site spend that decides the move-up. Root cause: the extended rule departs from another category's base clause, which no overwrite in this charter can retire. Consequence: under the vmi clause the replenishment stream is excluded and the move-up measure changes (task 1 demonstrates Standard kept vs Priority). Bears on: task 1. Location: order.extended.yaml order_ext_requested_move_up rule S7/S8/S13, compute `repl_12`, `repl_6`, `repl_share`, `counted_site_12/6`, `total_12/6`, factor replenishment_counted.
- **C2 — SOURCE-POLICY RED (XF2/XF3, non-commuting placement of the standing share).** Evidence: rotation S8 "The gross allowance is rotation_rate_pct percent of the rotation purchase base."; S9 "…credits already taken… are deducted from the gross allowance, never below 0.00, and what remains is capped at rotation_cap_usd to give the allowance…"; S11 "…every percentage that sets the gross allowance is applied to the adjusted purchase base in one product, credits already taken are then deducted, and the cap is applied last…"; S14 "The rotation allowance is granted at a share set by the customer's Commercial Credit Account…". S8 defines the gross allowance with the rate alone and S14 applies its share to "the rotation allowance", which S9 names as the figure after credits; S11's "every percentage that sets the gross allowance" admits the compute's reading (share inside the gross product) but does not exclude share-after-credits. The two orders do not commute when credits taken > 0. Bears on: task 0 (28 vs 30 bearings). Location: rule S8/S9/S11/S14; compute `gross_allowance`, `allowance`.
- **C3 — SOURCE-POLICY RED ("the review date" undefined).** Evidence: anniversary S1 "the review is recorded on the day it is performed, for the most recent anniversary that has no review on or after it"; S2/S3/S7/S8/S9/S10 measure every window "before the review date"; base measure order_msr_trailing_12m_spend "The 12 calendar months ending on the review date" in a base rule that reviews "At each anniversary of its opening". Whether "the review date" is the anniversary the review is for or the later day it is performed is not stated; the windows (12-month, 6-month, route count, drop-ship, will-call) shift with it. Read sites: `spend_12`, `spend_6`, `shipped_12`, `route_runs_12`, `dropship_12/6`, `willcall_12/6`. Bears on: task 0 (Priority vs Route kept; rotation 28 vs 40). Realism: a distributor measures an anniversary review as of the anniversary; the charter's reading makes the outcome depend on how late the desk records it.
- **C4 — SOURCE-FACTOR RED (XF11, mislabelled method).** Members (complete list): order_ext_anniversary_review.review_pace_window; order_ext_requested_move_up.site_growth_window. Evidence: pairwise table above. Consequence: struck as method factors, the anniversary review has 3 factors and 0 method, the move-up 4 factors and 0 method — both below the bounds. Bears on: task 0 (anniversary computation), task 1 (move-up computation).
- **C5 — SOURCE-FACTOR RED (unreal ladder condition).** order_ext_reactivation_level.lost_route_drops: the condition part "with no order_line_shipped line shipped by route_truck within the 12 months before the reactivation date" holds of every suspended route-level ship-to the policy can reach. Lifecycle S1 suspends only after inactivity_suspend_months (12 / 18 / 24 for Route / Premier / Dedicated) whole months with no booked order, and reactivation follows suspension, so every line was booked at least 12 (18, 24) whole months before reactivation; a route_truck shipment inside the 12-month window would need a line shipped after its booking date by more than the gap between suspension and reactivation (Route) or by 6–12 months (Premier, Dedicated) — only a line held unshipped on a credit hold. The tier therefore divides suspended ship-tos by level held alone and restates the policy's scope. It was the reactivation's only multi-source factor. Bears on: task 1.
- **C6 — SOURCE-POLICY RED (XF9, same-day ties / ordering field).** Members (complete list, all in order_ext_stock_rotation_return): (a) S1 "the ship-to's most recent order_return_declined line whose decline_reason is outside_return_window" — by the event's grain "One row per order line on a declined request", a multi-line declined request yields several rows with one event_date, and the rule names no tie-break; the four compute reads `rot_order`, `rot_line`, `rot_sku`, `rot_requested` are separate LATEST calls and may not even resolve to one row; (b) "the line's most recent shipment" (S3, S10, S16) — a line that ships in two shipments on one date (two packing lists) ties; (c) S16 "the latest contract item price line for the rotation item's sku" — neither the ordering field (effective_date, quote_date or notice_date; compute uses effective_date) nor a same-date tie (e.g. a removal and a re-add effective the same day) is stated. Demonstration (domain): a declined request covering lines 1 (qty 10) and 2 (qty 40) on one date gives requested quantity 10 or 40. No consequence in task 0's world (one declined row, one shipment, distinct effective dates).
- **C7 — SOURCE-POLICY RED (XF9, month-end convention of whole-month counts).** Read sites (complete list): anniversary S2, S3 and S7–S10 ("fewer than N whole months separate its date from the review date", 12 and 6); rotation S7, S9, S12 (rotation_tenure_months), S13 (12 and 24), S14, S15 (12); reactivation S5 (dormancy months), S6, S7 (12), S9 (tenure months); move-up S5, S7 (12, 6), S9 (24, 12). No sentence states how a date on the 29th–31st counts against a shorter month (e.g. a line dated 2025-08-31 against a date of 2026-02-28 is 5 whole months by day-of-month counting, 6 by end-of-month convention, so it falls inside or outside a 6-month window). No consequence in either task world (the call dates are the 14th and 15th; checked against every seeded date).
- **C8 — SOURCE-POLICY RED (XF10, filters stated in the rule vs compute).** Members (complete list, order_ext_stock_rotation_return): (a) "the line's most recent shipment" (S3 RMA unit price, S10 allowance units, S16 tiers 1 and 3) — the charter defines order_backorder_filled as "One row per shipment against a backorder" with its own ship date and unit price, and S6 counts fills among the line's shipments, but the compute reads order_line_shipped only (`last_ship_price`, `last_ship_date`), a filter the rule never states; the zero-unit-value branch (`if unit_value > 0 else 0`) is likewise unstated; (b) S1 "unopened stocked merchandise of a returnable item class" — no compute binding tests item_class against non_returnable_item_classes or stock_status, so a declined outside-window line of a hazmat or special-order item yields a positive quantity in compute while the rule (and inherited order_evt_returns S4) excludes it. Demonstration (domain): line shipped 60 @ 64.80, later fill 20 @ 70.00 — rule reading divides by 70.00, compute by 64.80. No consequence in task 0's world (no fill on the rotation line; item standard/stocked). The "unopened" condition is not record-visible and bears on task 0's persona (see 0.md).
- **C9 — SOURCE-FACTOR RED (XF1, single-factor quantities outside the factor).** Members (complete list): rotation `rot_category` (only rotation_base_scope uses it) and `last_ship_date` (only rotation_unit_value uses it) sit outside their factor's `bindings`, so the declared baseline binding set carries two quantities the baseline rule never defines. No score consequence; recorded per the XF recipe. Bears on: task 0 (structure only).

Observations (not grounds for rework):
- O1: the anniversary rule finds "the most recent anniversary that has no review on or after it" from `last_review_date`, which `elect_service_level_move_6cd24a6d` also stamps; after a requested move recorded past an anniversary the records cannot show whether that anniversary was reviewed (the rotation edge's own fallback_reason concedes the fields are shared). No consequence in either world.
- O2: `held_level`, `route_level_held` have no compute_basis entry (covered by other quotes).
- O3: move-up gate shares — no generic sentence states how the agreement share and the credit share combine; S9's "further applied" implies a product (25000 × 0.92 × 0.90 = 20700) over an additive reading (20500). No consequence in task 1 (measure above both).
- O4: reactivation take-back vs tenure order is fixed by S4's "never below zero" floor.
- O5: the move-up edge's `condition` adds the reactivated-level clause to the sentence's state.
- O6: move-up reads "the VendPoint machine standing at the ship-to" and both rotation and move-up read "the StockSmart program serving the ship-to" through single-record CFIELD; the vending charter allows several machines at one ship-to and the rule does not say which one or whether to sum. No consequence in either world (one machine, one program).
- O7: under a Corbett Category Contract the rotation base is cut to the rotation item's product category, yet S15 then adds all StockSmart replenishment, of every category, in full.
- O8: rotation and move-up read only an agreement whose status is `active`; an agreement in `renewal_pending` (still pricing) falls to the "no active agreement" tier.
- O9: rotation's XLATEST over pricing_items is not limited to the active agreement although S16 says "on the customer's Contract Pricing Agreement".
- O10: rotation_base_scope's sku tier swaps the window (24 months) as well as the filter.
- O11: anniversary review lists order_agg_ship_to_portfolio in base_policy_refs without overwriting its S3; the downgrade test is not an entry-gate measurement, so no conflict is demonstrated.

## closing_checklist

Written after both reveals (2026-10-17T01:55Z); the sections above were written before any reveal and were not edited afterwards except to complete C3/C7 read-site lists before the reveal.

- Per-task files: 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision_1 (no older revision). Neither comparison carries a PASS: task 0 RED (SOURCE-POLICY, SOURCE-TASK, SOURCE-FACTOR), task 1 RED (SOURCE-POLICY, SOURCE-TASK, SOURCE-FACTOR). The difficulty does **not** close.
- Coverage and scope: the four extended policies are fully covered; charter_scope task 0 = {anniversary_review, stock_rotation_return}, task 1 = {reactivation_level, requested_move_up} — pairwise disjoint, matching the blind pairing. Task tools closed over GT; uuid8s independent (§ action_binding_and_uuids).
- Problem trees: each has 1 prerequisite problem, 1 value_input edge, one owner=user write, no cycle; the difficulty graph is two disjoint edges, acyclic. SOURCE-CHAIN PASS for both (task 0's edge loses weight only under C3's second reading).
- Factors: every declared factor bears weight against an honest baseline on its task's world and every baseline gives a definite fall-back different from the scored value (task 0: Route Delivery / 23; task 1: Route Delivery / Standard). Bounds fail after the strikes: anniversary review 3 factors, 0 method (C4); move-up 0 method (C4); lost_route_drops struck (C5). Seed: task 0's credit invoice contradicts the charters (0.md T0-4).
- Gates: not re-run by this auditor (the brief's snapshot is the instantiation-stage run on this final form: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK). Green gates did not catch any finding above.
- Open charter REDs, each with its complete member list in § findings: C1 (vmi service-level-spend clause vs move-up), C2 (rotation standing-share placement), C3 (anniversary "review date"), C4 (pace/growth methods: review_pace_window, site_growth_window), C5 (lost_route_drops condition), C6 (rotation ties/ordering: declined line, most recent shipment, latest price line), C7 (month-end convention: every whole-month read site listed), C8 (rotation filters: "most recent shipment" vs order_line_shipped and the zero-unit branch; S1 eligibility filter), C9 (rot_category, last_ship_date outside their factors).

VERDICT revision_1: task0=RED SOURCE-POLICY(C2,C3) SOURCE-TASK(T0-1,T0-2,T0-3) SOURCE-FACTOR(C4,T0-4,C9) task1=RED SOURCE-POLICY(C1) SOURCE-TASK(T1-1) SOURCE-FACTOR(C4,C5) charter=C1,C2,C3,C4,C5,C6,C7,C8,C9

## revision_2

## charter_global_frozen (revision_2)

- Auditor: same independent auditor, round 2. Written before any round-2 GT was revealed; the revision_1 text above is untouched.
- Entry gate: `tail -1 tasks/d3_ship_to_orders_backorders_and_returns/worklog.md` = `REWORK round 2: gates 7/7 green` (only that line was read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 2` (executed, not read) printed EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (saved at `.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r2/gates.txt`) and the hashes:
  - `f5b590c2dfed2f7f9befe28cbd61397536fe1e56953100b175ef92322d14f9ed  tasks/d3_ship_to_orders_backorders_and_returns/order.extended.yaml` (changed from r1)
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  tasks/d3_ship_to_orders_backorders_and_returns/task_tools.py` (unchanged)
  - `ae637a74e21c3e99ca72747e2951063199b4fbc1f2bc60eb52d2582c4c177e66  .audit_views/policy/d3_ship_to_orders_backorders_and_returns/r2/task0.view.json`
  - `dab45259447e2720c83640e58726c3e53ba642404d472f33da35fb041e7a8cae  .audit_views/policy/d3_ship_to_orders_backorders_and_returns/r2/task1.view.json`
  Input complete.
- Carry-forward rule: the charter hash changed, so every charter-global section is re-derived below; `task_tools.py` is unchanged, so § action_binding_and_uuids is carried forward by reference to revision_1 on the grounds of hash aa4a300d… (bodies, docstrings, uuid8s identical).
- Base copy: lines 1–818 still byte-identical to blueprint/products/order.yaml.
- contamination_disclosure (round 2): round-1 GT of both tasks is known to this auditor from revision_1 (task 0: Priority / 28; task 1: Standard / Priority), as any re-audit's is; no round-2 GT, plan.md or worklog body was read before the freezes below.

### policy_conflict_scan (r2)

Same four extended policies, tools, subjects and task pairing. Changes that touch the overlap scan: the move-up no longer reads StockSmart replenishment (S8 "StockSmart replenishment never counts in the move-up measure, program spend not counting toward a ship-to's service level spend"), so the collision with vmi_agg_program_portfolio S2 is gone; the anniversary review now defines its review date as the day it is recorded and when it is recorded; the rotation reads only the active agreement's price lines. The anniversary review and the requested move-up still both stamp `last_review_date` (O1 stands).

### rule_compute_equivalence (r2)

Sweep re-run: every compute_basis quote verbatim in its rule; every baseline.rule sentence, replaced_by and policy_source in its rule; no compute binding without a basis entry (O2 closed). Sentence-level review of the reworked parts:
- anniversary: S1 now "the review falls due on the anniversary and is recorded on the anniversary or, where it was not recorded that day, on the first later day the ship-to is handled; the review date is the day the review is recorded, and the review is for the most recent anniversary on or before the review date that has no review dated on or after it"; whole-month definition sentence added; review_tenure_basis ↔ `months_open_review`, `review_basis`, `review_spend` = MN / MX / counted_12 — equivalent.
- rotation: S1 tie rule ↔ `rot_date`, `declined_that_day`, `rot_requested` (0 unless exactly one declined row on the latest date); S2 scope ↔ `line_shipments == 1`, `line_fills == 0`, stocked, item_class not in P('non_returnable_item_classes') (the customer's "unopened" statement is a dialogue fact with no record, correctly absent from compute); S7 returnable over order_line_shipped only; S12 zero-price branch ↔ `if unit_value > 0 else 0`; S13/S16 ↔ standing share inside the gross product; S17 ↔ program chosen by status; S18 ↔ `agreement_id`, `lines_that_date == 1`, `aged_shipment`, markdown RND 4. Equivalent.
- reactivation: S6 last-active-year window ↔ COUNT(within D+12) − COUNT(within D) = lines with D ≤ whole months < D+12; whole-month sentence S7. Equivalent, except that S6 states no reading when the ship-to has no last_order_date (compute sets D = 0) — C10.
- move-up: S8 ↔ no replenishment binding; S11 ↔ `own_shipped_lines_12`, `site_months_open`, `measure_basis`, `move_measure` (MX / ×12÷MX(1, months) / counted_12); S14 ↔ `terms_share`; S15 "the next level's entry gate is multiplied by every share that applies to it, the shares together in one product" ↔ `applied_gate` (O3 closed). Equivalent.

### action_binding_and_uuids (r2)

Carried forward from revision_1 (task_tools.py hash unchanged). The rotation docstring's "the invoiced unit price of the shipped line" now matches S4 "carrying the invoiced unit price of the line, the unit price of its one shipment".

### prerequisite_graph and prerequisite_sentences (r2)

Unchanged edges and sentences; both re-verified verbatim in their rules. The move-up edge's condition is now "The ship-to's status is active." (O5 closed). The rotation edge's fallback remains justified (the election tool still writes the same two fields). Re-checked that no new rule sentence states a cross-problem order: anniversary S1's "first later day the ship-to is handled" names no other problem's write.

### override_declarations (r2)

Overwrites unchanged and still genuine. The move-up now follows vmi_agg_program_portfolio S2 (C1 closed). Rotation S2's narrower scope (one shipment, no fill, stocked, returnable class, stated unopened) narrows an extended exception and contradicts no base clause; order_evt_returns S4 is still inherited. No other undeclared departure found (all product charters re-scanned for "count toward" / service-level clauses).

### factor_ladders (r2)

| policy | factor | label | tiers | multi-source | x-difficulty | verdict |
|---|---|---|---|---|---|---|
| anniversary | review_route_use_pct | parameter | 85/80/70 % | yes | — | ok |
| anniversary | review_tenure_basis | method | lower of / higher of (counted 12 m, 2 × counted 6 m) / counted 12 m by months open ≥ 60, < 24, else | no | — | ok (MIN vs MAX vs identity; distinguishing input counted_12 ≠ 2 × counted_6) |
| anniversary | review_dropship_share / review_willcall_share | parameter | 0/50/100; 25/50/100 | no | — | ok |
| rotation | rotation_rate, rotation_standing, rotation_program_share, rotation_cap | parameter | as r1 | standing tier 2 | credit, vmi, pricing | ok |
| rotation | rotation_base_scope | method | category 12 m / sku 24 m / all 12 m | no | pricing | ok (as r1) |
| rotation | rotation_unit_value | method | later lower contract price / invoiced price × (1 − 15 %) / invoiced price | yes | pricing | **mislabelled (C11)** |
| reactivation | dormancy, payment, take-back | parameter | as r1 | no | credit, vmi | ok |
| reactivation | lost_route_drops | parameter | 2 / 1 / 0 by route_truck runs in the last active year (0; 1–5; else) | yes | — | ok (C5 closed); absent-date branch C10 |
| reactivation | tenure_adjustment | method | halve / minus one / as added | no | — | ok |
| move-up | site_ordering_basis | method | higher of (counted 12 m, 2 × counted 6 m) when no own shipment in 12 m / counted 12 m × 12 ÷ months open when open < 12 m / counted 12 m | tier 2 yes | — | ok (MAX vs proration vs identity) |
| move-up | vending_counted, commitment_gate_share, standing_gate_share, terms_gate_share | parameter | 100/50/0; 85/92/100; 90/95/100; 90/95/100 | standing yes | vending, pricing, credit, credit | ok |

XF1 (mechanical reader scan re-run): no factor binding reads another factor's binding; the only plain bindings read solely inside one factor are `last_ship_price` and `all_merch_12`, which are those factors' own baselines (and `last_ship_price` is also the RMA unit price) — legitimate. `rot_category` and `last_ship_date` are now inside their factors (C9 closed). XF2/XF3: every combination is stated generically (anniversary S11, rotation S13/S16, reactivation S4, move-up S15). Counts: anniversary 4 (3 P, 1 M); rotation 6 (4 P, 2 M) → 5 (4 P, 1 M) after the C11 strike — still within bounds; reactivation 5 (4 P, 1 M); move-up 5 (4 P, 1 M). Realism: tiers are treatments a distributor publishes; see observations O12–O14 for the tensions.

### round-1 RED closure (charter)

| id | verdict r2 | evidence |
|---|---|---|
| C1 | closed | move-up S8 excludes StockSmart replenishment, consistent with vmi_agg_program_portfolio S2; replenishment_counted removed |
| C2 | closed | rotation S16 "The gross allowance carries a standing share …, the share being one of the percentages of the gross allowance" + S13 "all of them in one product that is the gross allowance; credits already taken are then deducted from that product" — one order |
| C3 | closed | anniversary S1 defines the review date as the day recorded and when it is recorded |
| C4 | closed | review_pace_window and site_growth_window replaced by MIN/MAX and proration methods |
| C5 | closed | route drops now divide by route use in the last active year (0 / 1–5 / ≥ 6 runs) — a condition that differs among suspended ship-tos |
| C6 | closed | (a) latest event_date, several rows that day → no rotation; (b) S2 limits the rotation to a line with exactly one shipment; (c) latest by effective_date on the active agreement, only line with that date |
| C7 | closed | whole-month definition sentence in all four rules (anniversary, rotation S9, reactivation S7, move-up S6) — day-of-month convention, definite at month ends |
| C8 | closed | (a) one-shipment scope; zero-price branch stated (S12); (b) stocked / returnable-class filters in compute; unopened made a customer statement |
| C9 | closed | rot_category, last_ship_date moved into their factors |
| O2, O3, O5, O9 | closed | basis entries complete; gate product stated; condition = sentence; price lines limited to the active agreement |
| O1, O4, O6, O7, O8, O10, O11 | stand as observations | unchanged text |

### findings (revision_2)

- **C10 — SOURCE-POLICY RED (XF9, absent-record branch).** order_ext_reactivation_level S6 defines the last active year by "D being the whole months from its last_order_date to the reactivation date" and gives no reading for a ship-to with no last_order_date, while S5 of the same rule treats that case as reachable ("or the ship-to has no last_order_date"). Compute sets D = 0 (`dormant_months` → 0), so the "last active year" becomes the 12 months before reactivation. Demonstration (domain): a suspended Route Delivery ship-to with no last_order_date and no shipments — compute gives 2 route drops; a reader for whom no active year exists applies "none for every other ship-to" — 0 drops. Members (complete list): S6 `active_year_route_runs` / `route_drops`. No other absent-record branch is unstated in any of the four rules (checked: anniversary opened_date, rotation shipment / agreement / account / program, move-up opened_date / machine / agreement / account). Bears on no task world (task 1's ship-to has a last_order_date). New in revision_2 (introduced with the C5 rework).
- **C11 — SOURCE-FACTOR RED (XF11, mislabelled method).** order_ext_stock_rotation_return.rotation_unit_value: tier 2 "divide the allowance by the invoiced unit price reduced by aged_stock_markdown_pct percent" and tier 3 "divide the allowance by the invoiced unit price" are the same division with the divisor's multiplier swapped (0.85 vs 1.00); tier 1 substitutes another price into the same division. Every tier is allowance ÷ (a number), the tier choosing the number — a parameter, not a method. Members of the XF11 class in this charter (complete list): rotation_unit_value only (review_tenure_basis, site_ordering_basis, tenure_adjustment, rotation_base_scope checked and distinct). Consequence: struck as a method, the rotation keeps 5 factors with 1 method (rotation_base_scope) — bounds still met — but the declared label is dishonest. Bears on: task 0. New in revision_2 (round 1's tier 2 was a quantity-weighted average, a different computation; the rework replaced it with a markdown).

Observations added in revision_2 (not grounds for rework):
- O12: review_tenure_basis tests the most tenured ship-tos (≥ 60 months) on the lower of the trailing year and the annualized half year and the youngest on the higher — defensible (ramp-up benefit for new sites, decline signal for established ones), though it runs against the usual loyalty slant.
- O13: rotation_unit_value tiers 1 and 2 count units at a value below the invoiced price while the RMA and its credit carry the invoiced price, so before the restocking fee the credit can exceed the dollar allowance by p / c (tier 1) or 1 / 0.85 (tier 2); at a 15 % restocking fee the net credit stays near the allowance, at a 0 % fee (Dedicated) it does not.
- O14: the last active year is anchored on last_order_date (a booking) while the counted lines are shipments dated a day or more later, so for reactivation dates whose day of month falls between the booking day and the shipping day the last shipment drops out of the year.

## closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-17T03:32Z).
- Files: 0.md and 1.md each carry revision_1 untouched and a revision_2 appended (frozen derivation → reveal → comparison → findings). Comparisons: task 1 PASS on all four relationships; task 0 PASS on policy, chain and unique solution, RED on factors (C11 label). The difficulty does not close.
- Coverage / scope: four extended policies covered; charter_scope task 0 = {anniversary_review, stock_rotation_return}, task 1 = {reactivation_level, requested_move_up}; disjoint; tools closed over GT; uuid8s unchanged and independent.
- Trees: one prerequisite problem each, value_input, owner=user root write, acyclic; every edge bears weight (task 0: 28 vs 40; task 1: Priority vs Route Delivery kept).
- Factors: every declared factor bears weight against an honest baseline; fall-backs definite and different from gold (task 0: Route Delivery / 23; task 1: Route Delivery / Standard). Bounds met in every computation (rotation still 1 method after the C11 strike); per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded, charter-consistent rows.
- Every round-1 charter RED (C1–C9) verified closed (§ round-1 RED closure). New in round 2: C10 (XF9, reactivation S6 absent last_order_date — complete member list: that one site) and C11 (XF11, rotation_unit_value — complete member list: that one factor). No regression of any round-1 closure found; XF1–XF13 re-checked on all four policies.
- Gates: the round-2 snapshot (all seven OK) is the instantiation-stage run on this final form; not re-run by the auditor.

VERDICT revision_2: task0=RED SOURCE-FACTOR(C11) task1=PASS charter=C10,C11

## revision_3

## charter_global_frozen (revision_3)

- Same auditor, round 3; written before any round-3 GT reveal; revisions 1 and 2 untouched.
- Entry gate: worklog tail = `REWORK round 3: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 3` (executed only) printed all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r3/gates.txt`) and:
  - `e80ac6f1aa36db538f5ad5e056841d9fad7ae47ac8a52e3fb19abeeb127c3ffb  order.extended.yaml` (changed from r2 f5b590c2…)
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` (unchanged since r1)
  - `ae637a74e21c3e99ca72747e2951063199b4fbc1f2bc60eb52d2582c4c177e66  r3/task0.view.json` (identical to r2's view hash)
  - `dab45259447e2720c83640e58726c3e53ba642404d472f33da35fb041e7a8cae  r3/task1.view.json` (identical to r2's view hash)
  Input complete. Base copy (lines 1–818) still verbatim.
- Charter delta (full `diff` against the r2 copy kept in scratch: 20 changed lines, nothing else): opened_date-absent readings added to anniversary S-tenure, rotation S14, reactivation S10, move-up S11 (rule text, compute_basis and compute guards); rotation S18 fall-through now names "no price line on the active agreement or no active agreement"; reactivation S6 adds "a ship-to with no last_order_date having no last active year and so no route drop" with the compute guard `0 if not F('last_order_date')` and the ladder's fall-through wording; rotation_unit_value relabelled `parameter` with value-form tiers.
- Carry-forward: task_tools.py unchanged → § action_binding_and_uuids carried from revision_1. Charter changed → the sections below are re-checked on the delta. Every r2 conclusion outside the 20 changed lines stands by reference to `## revision_2` (the lines it rests on are byte-identical).
- contamination_disclosure: round-1 and round-2 GT known from earlier revisions; no round-3 GT read before the freezes.

### re-check on the delta (rule/compute, XF1–XF13)

- XF6 sweep re-run: every compute_basis quote, baseline.rule sentence, replaced_by and policy_source verbatim in its rule; no binding without a basis.
- XF9/XF10: each new absent-record sentence matches its compute guard (anniversary `months_open_review … else 0` → young tier; rotation `months_open … else 0` → base rate; reactivation `months_open_now … else 0` → stands as added; move-up `site_months_open … else 0` → ÷ MX(1, 0) = ÷ 1; reactivation `route_drops` → 0). Absent-record sweep over all four rules finds no remaining unstated branch.
- XF11: rotation_unit_value is now a parameter whose tiers are values (contract price / 0.85 × invoiced, RND 4 / invoiced) — honest. Remaining method factors, pairwise distinct: review_tenure_basis (MIN / MAX / identity), rotation_base_scope (record populations), tenure_adjustment (halve / minus one / identity), site_ordering_basis (MAX / proration / identity). No member of the class remains.
- XF1/XF2/XF3: mechanical reader scan re-run — no factor reads another factor's binding; combination sentences unchanged.
- XF5, XF7, XF8, XF12, XF13: untouched by the delta (tools unchanged; seeds unchanged — view hashes equal r2).
- Counts: anniversary 4 (3 P, 1 M); rotation 6 (5 P, 1 M); reactivation 5 (4 P, 1 M); move-up 5 (4 P, 1 M). All within bounds; multi-source and cross-difficulty per task as in r2.
- Realism: the new absent-record readings (no opened_date → treated as 0 months, i.e. the youngest/base tier; no last_order_date → no route drop) are conservative defaults a distributor would publish.

### round-2 RED closure

| id | verdict r3 | evidence |
|---|---|---|
| C10 | closed | reactivation S6 "a ship-to with no last_order_date having no last active year and so no route drop" + compute guard; class sweep also closed the opened_date-absent sites in all four rules |
| C11 | closed | rotation_unit_value `effect: parameter`, tiers carry `value`; no other XF11 member |
| O1, O4, O6, O7, O8, O10, O11, O12, O13, O14 | stand as observations | text unchanged |

### findings (revision_3)

No new charter-level RED. No regression of any round-1 or round-2 closure.

## closing_checklist (revision_3)

Written after both round-3 reveals (2026-10-17T13:38Z).
- Files: 0.md, 1.md and this file each carry revisions 1–3, older text untouched; both round-3 comparisons PASS on all four relationships.
- Coverage / scope: the four extended policies are covered; task 0 = {order_ext_anniversary_review, order_ext_stock_rotation_return}, task 1 = {order_ext_reactivation_level, order_ext_requested_move_up}; pairwise disjoint over each whole tree; task tools closed over GT; uuid8s a2ef3cef / 550cd403 / 971b9440 / 6cd24a6d independent and frozen (tools unchanged since r1).
- Trees: each has 1 prerequisite problem, 1 value_input edge (≥ max(n − 1, 1)), an owner=user root write, no cycle; the difficulty graph (two disjoint edges) is acyclic; every edge bears weight (task 0: 28 vs 40; task 1: Priority vs Route Delivery kept).
- Factors: every computation declares a self-sufficient baseline and 4–6 factors with ≥ 2 parameter and ≥ 1 honest method (anniversary 3 P / 1 M; rotation 5 P / 1 M; reactivation 4 P / 1 M; move-up 4 P / 1 M); each task has ≥ 1 multi-source (task 0 review_route_use_pct, rotation_unit_value; task 1 lost_route_drops, standing_gate_share) and ≥ 1 cross-difficulty factor with seeded, charter-consistent rows; every ladder has three distinct tiers stated in its rule; every factor bears weight against an honest baseline; each baseline alone gives a definite number different from gold (Route Delivery / 23; Route Delivery / Standard).
- XF_recipe points 1–13 re-checked on all four extended policies: no member of any class remains.
- Gates: the round-3 snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK) is the instantiation-stage run on this final form.
- Open charter REDs: none. Observations O1, O4, O6–O8, O10–O14 remain on record (not grounds for rework).

This difficulty passes the source-layer audit.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision_4)

- Same auditor, round 4; written before any round-4 GT reveal; revisions 1–3 untouched.
- Context: audits/render_source/d3_ship_to_orders_backorders_and_returns/render_r1.md (renderer source scan of charter e80ac6f1…, five items) read in full; each item treated as a RED to verify closed as a class.
- Entry gate: worklog tail = `REWORK round 4: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 4` (executed only): all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r4/gates.txt`); hashes:
  - `c40d654912c72af55a2b456f9d9ff90ff7d9c7342cdfe7eb3973f64b7a365fc3  order.extended.yaml` (changed from r3 e80ac6f1…)
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` (unchanged since r1 → § action_binding_and_uuids carried from revision_1)
  - `ae637a74…66  r4/task0.view.json`, `dab45259…cae  r4/task1.view.json` (both identical to r2/r3 → worlds and personas unchanged)
  Input complete. Base copy (lines 1–818) still verbatim.
- Charter delta (diff against the r3 copy in scratch, 94 changed lines): anniversary — standalone six-month-spend sentence added to the rule and to baseline.rule, removed from the tenure-basis sentence; reactivation — S4 rewritten as one net total, S9 reads only the ship-to's active program (compute `CFIELD(..., status='active')`); move-up — six-month site spend made a standalone sentence in rule and baseline.rule, the vending sentence rewritten (placement status set, "this rule decides a ship-to with at most one such placement"), vending_counted now owns `machine_active_id`, `machine_idle_id`, `vend_active_12/6`, `vend_idle_12/6`, `vend_added_12/6`, and the combination sentence made generic ("Additions to the site spend of a period are made first…"). Every r3 conclusion outside the delta stands by reference to `## revision_3`.
- contamination_disclosure: earlier rounds' GT known; no round-4 GT read before the freezes.

### re-check on the delta

Sweeps re-run on c40d6549…: all compute_basis quotes, baseline.rule sentences, replaced_by and policy_source verbatim; no binding without a basis; no factor reads another factor's binding; reader scan of plain bindings — every plain binding is read by the baseline path or by two or more parts (`spend_6`/`own_6` feed the counted six-month figures that the method factor and the drop-ship / will-call / vending factors all reach). CFIELD sweep: credit and pricing reads are unique by charter (credit_agg / pricing_agg max_per_customer 1); VMI reads in rotation and reactivation filter by status, unique by vmi_agg_multi_holding's one-program-per-ship-to dedup over enrolled/active/paused/terminating; the vending reads are the only multi-placement read (vending_agg_multi_holding: "including several at one ship-to").

### render_r1 items — closure and prior coverage

| item | verdict r4 | class sweep (all four policies) | covered in my earlier revisions? |
|---|---|---|---|
| 1 move-up: one machine assumed, compute picks first row | **not closed** (R4-1 below) | only multi-placement read in the charter | r1/r2 O6 — recorded as an observation only, under-classified |
| 2 reactivation: closed program readable | closed — S9 names the active program, compute filters status='active' | rotation already status-filtered; move-up vending → item 1; credit/pricing unique | not covered (r1 O6 named the rotation and move-up program reads, not the reactivation) |
| 3 move-up: vending usage outside its factor; combination names it | closed — vending_counted owns all vending bindings; combination sentence generic | anniversary drop-ship/will-call already own theirs; rotation program owns its | not covered (my r2 reader scan counted only direct factor-binding readers and passed it) |
| 4 six-month figures defined only inside a method factor | closed — standalone sentence in rule and baseline.rule (anniversary, move-up), method sentences no longer define them | rotation/reactivation have no six-month figure | not covered (considered in r2 and passed) |
| 5 reactivation: take-back vs halving order | closed — S4 "every drop taken back is subtracted, all in one total … any adjustment made to the total itself is made to that net total" | anniversary, rotation, move-up combination orders already fixed | r1 O4 — recorded as an observation (judged fixed by the zero floor), under-classified |

### findings (revision_4)

- **R4-1 — SOURCE-POLICY RED (render item 1 residual; XF12 / XF5 scoping).** Symptom: for a Parcel or Standard ship-to with two or more VendPoint placements in status active, suspended or removal_pending, two sentences of the move-up rule conclude differently and the compute decides a case the rule leaves undecided. Evidence: S1 (also the overwrite's replaced_by) "for a ship-to holding Corbett Parcel Ship-To or Corbett Standard Ship-To, and only for such a ship-to, the move up to the next level is decided on the move-up measure"; S10 "that machine being the one placement at the ship-to whose status is active, suspended or removal_pending (a removed or requested placement is never read, and this rule decides a ship-to with at most one such placement)". The retired base clause no longer covers Parcel/Standard ship-tos, so a multi-placement ship-to is decided by S1 and not decided by S10, with no in-force rule for it; compute `machine_active_id` / `machine_idle_id` take the first active row (else the first suspended/removal_pending row) and return a level, with no count test. Demonstration (domain): a Standard ship-to with an active machine (12-month usage 18000.00, 6-month 10000.00) and a suspended one — compute measures the active machine alone and can move it up; S10 leaves it undecided. XF12's remedy — the scope named in the self-naming overwrite (so the out-of-scope case stays under the base clause) and tested as a count of exact-status placements — is not applied. Members (complete list): order_ext_requested_move_up S1/replaced_by vs S10, compute `machine_active_id`, `machine_idle_id`, `vend_added_12/6`, factor vending_counted's ladder (its fall-through "no machine … in one of those statuses" is silent about two). No other read in the charter can see several candidate holdings. Bears on no task world (task 1 has one placement).
- No other new defect; no regression of the r1–r3 closures. Observations O1, O6 (now R4-1), O7, O8, O10–O14 as before; O4 superseded by item 5's closure.

## closing_checklist (revision_4)

Written after both round-4 reveals (2026-10-17T18:18Z).
- Files: revisions 1–4 present in all three files, older text untouched; both round-4 comparisons PASS on all four relationships.
- Scope, trees, factors and tools: as in § closing_checklist (revision_3), re-verified on c40d6549… — four policies covered, disjoint task scopes, one value_input edge per tree with a customer-run root write, every factor bearing weight against an honest baseline, bounds met (anniversary 3 P / 1 M; rotation 5 P / 1 M; reactivation 4 P / 1 M; move-up 4 P / 1 M), uuid8s unchanged.
- render_r1 items: 2, 3, 4, 5 closed as classes; item 1 not closed (R4-1). Earlier-revision coverage recorded in § render_r1 items: items 1 and 5 were on record only as observations (O6, O4), items 2, 3, 4 were missed.
- XF_recipe points 1–13 re-checked on all four policies: the only remaining member is R4-1 (XF12 scoping / XF5 out-of-scope case), single member.
- Gates: round-4 snapshot all seven OK.
- Open charter REDs: R4-1. The difficulty does not close.

VERDICT revision_4: task0=PASS task1=PASS charter=R4-1

## revision_5

## charter_global_frozen (revision_5)

- Same auditor, round 5; written before any round-5 GT reveal; revisions 1–4 untouched.
- Entry gate: worklog tail = `REWORK round 5: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 5` (executed only): all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r5/gates.txt`); hashes:
  - `469d4dad71105b71f886efdbb024434d9aaa6b5437cb2abd9947bcec276cbd1f  order.extended.yaml` (changed from r4 c40d6549…)
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` (unchanged since r1)
  - `ae637a74…66  r5/task0.view.json`, `dab45259…cae  r5/task1.view.json` (identical to r2–r4)
  Input complete; base copy verbatim.
- Charter delta (diff against the r4 copy): only order_ext_requested_move_up — its lifecycle overwrite replaced_by, rule S1 and baseline.rule S1 now scope the move-up measure to a Parcel/Standard ship-to "with at most one VendPoint placement whose status is active, suspended or removal_pending" and restate the rest as "every other ship-to remains under the base rule, a ship-to holding Corbett Parcel Ship-To or Corbett Standard Ship-To with more such placements moving up to the next level when its trailing 12 month spend (its twelve-month site spend) meets that level's entry gate"; a new sentence "The VendPoint placements are counted over the ship-to's placements whose status is active, suspended or removal_pending, one for each status and VendPoint model found among them."; new compute `placements_active/suspended/pending` (sum over the six models of `int(EXISTS('vending', ship_to_id=HID, status=…, variant_name=…))`), `placement_count`, `base_move_result` (own_12 ≥ next_gate), and `result` branching on `placement_count <= 1`. The anniversary, rotation and reactivation policies are byte-identical to r4 → their r4 conclusions carried forward by reference.
- contamination_disclosure: earlier rounds' GT known; no round-5 GT read before the freezes.

### renderer-class sweeps (XF 1, 2, 3, 9, 10, 12) on all four policies

- XF1 (mechanical, re-run on 469d4dad…): no factor binding reads another factor's binding; plain bindings read only inside one factor are `last_ship_price` and `all_merch_12`, each that factor's own baseline (legitimate, as in r2–r4); the new move-up bindings are read only by `result`; nothing unread.
- XF2: combination sentences unchanged and generic (anniversary counted-first; rotation one gross product; reactivation one net total; move-up additions first, gate in one product); the new scope branch lives in `result`.
- XF3: orders fixed as in r4; the new branch is a selection, not an adjustment.
- XF9: absent-record branches covered (no vending placement → count 0 → measure path, nothing added); ties as in r2; month-end sentence in all four rules.
- XF10: the placement filter (status active / suspended / removal_pending) is stated and implemented; the model enumeration covers the vending charter's six models.
- XF12: the one-placement scope is now in the self-naming overwrite with the out-of-scope case restated — but the count it relies on does not count placements (R5-1).
- Verbatim sweeps (compute_basis, baseline.rule, replaced_by, policy_source) all pass.

### R4-1 closure

| id | verdict r5 | evidence |
|---|---|---|
| R4-1 | **partly closed** | the scope is now named in the overwrite and the out-of-scope ship-to has a stated rule (closes the "no in-force rule" half); the count test it rests on miscounts — see R5-1 |

### findings (revision_5)

- **R5-1 — SOURCE-POLICY RED (R4-1 residual; XF12 count, XF5 contradiction with the vending charter).** Symptom: two or more machines at one ship-to can pass the "at most one VendPoint placement" test, and the rule then reads "the one placement" among several. Evidence: move-up S1 "with at most one VendPoint placement whose status is active, suspended or removal_pending"; new sentence "The VendPoint placements are counted over the ship-to's placements whose status is active, suspended or removal_pending, one for each status and VendPoint model found among them."; compute `placements_active = Σ_models int(EXISTS('vending', ship_to_id=HID, status='active', variant_name=model))` (likewise suspended, pending); vending charter `vending_agg_multi_holding`: "A customer may hold any number of VendPoint machines, including several at one ship-to; each machine is a separate placement with its own model tier". Two passages, two conclusions: by the vending charter two active VendPoint Coil 40 machines at one ship-to are two placements (outside the measure path → trailing-spend rule); by the counting sentence and compute they are one (measure path), and S10's "the one placement at the ship-to whose status is active, suspended or removal_pending" then has two candidates — compute `machine_active_id` (CFIELD) reads the first only. Demonstration (domain): Standard ship-to, no own shipments in 12 months, two active Coil 40s each billing 9000.00 / 5000.00 (12 m / 6 m), gates as in task 1 (19665.00): compute reads one machine → max(9000.00, 10000.00) = 10000.00 → keeps Standard; reading both machines' usage → 20000.00 → Priority; reading them as two placements → trailing-spend rule, own spend 0.00 → keeps Standard. XF12's remedy ("count = sum of exact-status counts") is not met: the sum is over exact-status-and-model presence, not over placements. Members (complete list): move-up S1 / overwrite replaced_by / baseline.rule S1 ("at most one VendPoint placement"), the counting sentence, compute `placements_active`, `placements_suspended`, `placements_pending`, `placement_count`, and S10 / `machine_active_id` / `machine_idle_id` which rely on it. No other read in the charter. Bears on no task world (task 1 has one machine). Realism: no distributor would call two machines of one model "one placement".
- Observation O15: the restated out-of-scope rule ("moving up to the next level when its trailing 12 month spend … meets that level's entry gate") reads the retired base clause ("when the ship-to's trailing spend meets the higher level's entry gate") as a one-level move; the base clause is open to that reading, so no contradiction is demonstrated.
- No other new defect; nothing regressed (anniversary, rotation, reactivation unchanged; render_r1 items 2–5 still closed).

## closing_checklist (revision_5)

Written after both round-5 reveals (2026-10-17T19:08Z).
- Files: revisions 1–5 in all three files, older text untouched; both round-5 comparisons PASS on all four relationships.
- Scope, trees, factors, tools: as in § closing_checklist (revision_4), re-verified on 469d4dad… (move-up factors unchanged: 4 P / 1 M; the new placement bindings are plain scope bindings read only by `result`).
- Renderer-class sweeps XF 1, 2, 3, 9, 10, 12 re-run on all four policies: the only remaining member is R5-1 (single member: the move-up placement count and the reads that rely on it).
- Gates: round-5 snapshot all seven OK.
- Open charter REDs: R5-1. The difficulty does not close.

VERDICT revision_5: task0=PASS task1=PASS charter=R5-1

## revision_6

## charter_global_frozen (revision_6)

- Same auditor, round 6; written before any round-6 GT reveal; revisions 1–5 untouched.
- Entry gate: worklog tail = `REWORK round 6: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 6` (executed only): all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r6/gates.txt`); hashes:
  - `ae8824aada7211c4e4e463d44ccca0904813da8e2edb9ff5147bccaf003a9918  order.extended.yaml` (changed from r5 469d4dad…)
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` (unchanged since r1)
  - `ae637a74e21c3e99ca72747e2951063199b4fbc1f2bc60eb52d2582c4c177e66  r6/task0.view.json` (unchanged since r2)
  - `f97d61ebd8c5a3554fcd6e0d672fd60b303498b786df3d80f391e3dbab18ef0d  r6/task1.view.json` (changed from r2–r5 dab45259…)
  Input complete; base copy verbatim.
- Charter delta (diff against the r5 copy, 145 changed lines): order_ext_requested_move_up only. Route taken: the multi-holding read is removed rather than counted — VendPoint usage no longer counts ("StockSmart replenishment never counts in the move-up measure, program spend not counting toward a ship-to's service level spend, and VendPoint usage does not count in it either."), factor vending_counted and every vending binding, the placement count and the r5 scope clause are deleted; the overwrite replaced_by returns to the r4 wording (O15 moot). site_ordering_basis tier 1 now "the same merchandise less return credits over its last active year, the lines dated at least D and fewer than D + 12 whole months before the request date, D being the whole months from its last_order_date to the request date, multiplied by 12 and divided by D + 12 (a ship-to with no last_order_date having no last active year and a measure of 0.00)"; the six-month site spend is gone; a new factor credit_tenure_gate_share (95 % for ≥ 120 months held, 97 % for 60–119, full otherwise); gate shares retuned (commitment 88/94, standing 95/97, terms mid 94). Anniversary, rotation and reactivation are byte-identical to r5 → their conclusions carried forward by reference.
- contamination_disclosure: earlier rounds' GT known; no round-6 GT read before the freezes.

### renderer-class sweeps (XF 1, 2, 3, 9, 10, 12) on all four policies, and the replaced factor

- Verbatim sweeps (compute_basis, baseline.rule, replaced_by, policy_source) pass; no binding without basis; no stale basis entry.
- XF1: no factor reads another factor's binding; `months_since_last_order` and `last_active_year_spend` sit inside site_ordering_basis; `credit_opened`/`credit_months_held` inside credit_tenure_gate_share; plain bindings read only inside one factor are still only `last_ship_price` and `all_merch_12` (rotation baselines). Nothing unread.
- XF2: move-up S14 "The next level's entry gate is multiplied by every share that applies to it, the shares together in one product, and the move-up measure is compared with that product." — generic; the measure has no additions left to combine. Others unchanged.
- XF3: gate shares commute; no other order to fix.
- XF9: new absent branches stated and implemented (no last_order_date → measure 0.00; no account / no opened_date → full gate); D + 12 ≥ 12, no zero division; ties none.
- XF10: tier-1 "same merchandise less return credits" ↔ shipped + filled − received credits over the window; filters stated = filters applied.
- XF12: the last-active-year window is a NOW-relative window offset by D (computed from one field of the holding) — expressible, no record-to-record pairing. CFIELD sweep: the move-up now reads only pricing (one agreement per customer) and credit (one account per customer); no multi-holding read remains anywhere in the charter.
- XF11 for the reworked method, pairwise: tier 1 (last active year × 12 ÷ (D + 12)) vs tier 3 (trailing twelve months as booked) — a different record population anchored on last_order_date, prorated over elapsed months; tier 2 (trailing twelve months × 12 ÷ months open) vs tier 3 — proration by a record-derived month count, reachable only below 12 months open, so never coincident with tier 3. The multipliers are time-weightings computed from record dates, not swapped constants; accepted as a method (distinguishing inputs: any dormant ship-to; any ship-to open < 12 months).
- Floors: move-up 5 factors (4 P: commitment, standing, terms, credit tenure; 1 M: site_ordering_basis); multi-source standing_gate_share; cross-difficulty pricing and credit. Realism: a returning site judged on its last year of buying spread over the time since that year began, and the gate eased for long-held credit accounts, are treatments a distributor would publish.

### R5-1 closure

| id | verdict r6 | evidence |
|---|---|---|
| R5-1 | closed | the vending multi-placement read is removed from rule and compute; the move-up reads no holding that can occur more than once per ship-to; the scope clause that depended on the count is gone |

### findings (revision_6)

- No new charter-level RED; nothing regressed in the three unchanged policies.
- Observation O16: the persona still mentions StockSmart self-scan volume as the site's main supply; StockSmart never counts in the measure (S8) — a customer fact, not a steer.

## closing_checklist (revision_6)

Written after both round-6 reveals (2026-10-17T19:37Z).
- Files: revisions 1–6 in all three files, older text untouched; both round-6 comparisons PASS on all four relationships.
- Coverage / scope: four extended policies; task 0 = {anniversary_review, stock_rotation_return}, task 1 = {reactivation_level, requested_move_up}; disjoint; tools unchanged, closed over GT; uuid8s independent.
- Trees: one prerequisite problem each, one value_input edge, owner=user root write, acyclic; edges bear weight (task 0: 28 vs 40; task 1: Priority vs Route Delivery kept).
- Factors: anniversary 4 (3 P / 1 M), rotation 6 (5 P / 1 M), reactivation 5 (4 P / 1 M), move-up 5 (4 P / 1 M); every ladder three distinct tiers stated in its rule; every factor bears weight on its world against an honest baseline; baselines alone give Route Delivery / 23 (task 0) and Route Delivery / Standard (task 1), all different from gold; task 0 multi-source review_route_use_pct, rotation_unit_value, cross-difficulty pricing/credit/vmi; task 1 multi-source lost_route_drops, standing_gate_share, cross-difficulty credit/vmi/pricing — all rows seeded and charter-consistent.
- Renderer-class sweeps XF 1, 2, 3, 9, 10, 12 and the rest of XF 1–13 re-run on all four policies: no member remains. Every RED from rounds 1–5 (C1–C11, render_r1 items 1–5, R4-1, R5-1) is closed.
- Gates: round-6 snapshot all seven OK.
- Open charter REDs: none. Observations on record: O1, O6 (moot), O7, O8, O10–O14, O16.

This difficulty passes the source-layer audit.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)

- Same auditor, round 7; written before any round-7 GT reveal; revisions 1–6 untouched.
- Context: audits/policy_kb/d3_ship_to_orders_backorders_and_returns/_verdict.md — only its src items read: SRC-1 (rotation: order of the contract narrowing vs the StockSmart addition unstated; compute narrows then adds → 28, reverse order → 17) treated as a RED to verify closed as an XF3 class; SRC-2 / SRC-3 are base text logged BLUEPRINT-KNOWN and not re-judged here.
- Entry gate: worklog tail = `REWORK round 7: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 7` (executed only): all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r7/gates.txt`); hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` (changed from r6 ae8824aa…)
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` (unchanged since r1)
  - `ae637a74e21c3e99ca72747e2951063199b4fbc1f2bc60eb52d2582c4c177e66  r7/task0.view.json` (unchanged since r2)
  - `f97d61ebd8c5a3554fcd6e0d672fd60b303498b786df3d80f391e3dbab18ef0d  r7/task1.view.json` (unchanged since r6)
  Input complete; base copy verbatim.
- Charter delta (diff against the r6 copy): one sentence of order_ext_stock_rotation_return (rule S13 and its `gross_allowance` compute_basis quote) — now "Adjustments to the rotation purchase base are made before any percentage is applied, an adjustment that narrows the merchandise the base counts being made first and an addition to the base being made after it, on the narrowed figure; every percentage that sets the gross allowance multiplies the adjusted purchase base, …". Compute unchanged (`gross_allowance = (purchase_base + program_added) × …`, purchase_base already the narrowed figure). Everything else byte-identical to r6 → all r6 sections carried forward by reference on these hashes.
- contamination_disclosure: earlier rounds' GT known; no round-7 GT read before the freezes.

### SRC-1 closure and XF3 class sweep (all four policies)

- Prior coverage: not covered as a RED. Revision_1 checked rotation S11 ("Adjustments to the rotation purchase base are made before any rate is applied") and judged the base adjustments ordered; O7 recorded only the realism tension of adding all-category StockSmart spend to a category-narrowed base. The non-commuting pair (narrow vs add, 28 vs 17 on task 0) was missed.
- Closure: the sentence now fixes narrowing first, addition after, on the narrowed figure — the compute's order; stated generically, without naming either factor's quantity (XF2 kept). On task 0 the reverse reading (add 20000.00 StockSmart, then narrow to bearings, dropping the uncategorised replenishment → 36268.75 → 17) is now excluded.
- Class sweep for every remaining non-commuting pair:
  - anniversary: drop-ship and will-call removals (commute with each other) are formed before the tenure-basis MIN/MAX — "the counted figures are formed first, and the review spend is then formed from them"; the route-use percent sets the threshold only. Fixed.
  - rotation: narrow → add → one product of percentages (commuting) → credits deducted → cap → rounding to the cent → division into units; the unit value and the min of three quantities have no order question. Fixed.
  - reactivation: drops added and take-backs subtracted in one net total, floored at zero, then the tenure adjustment — "any adjustment made to the total itself is made to that net total". Fixed.
  - move-up: one measure method, no additions; gate shares in one product (commute). Fixed.
  No member of the XF3 class remains.
- Sweeps re-run on e78daed4…: compute_basis, baseline.rule, replaced_by, policy_source verbatim; no binding without basis.

### findings (revision_7)

- SRC-1 closed. No new charter-level RED; nothing regressed.

## closing_checklist (revision_7)

Written after both round-7 reveals (2026-10-17T22:03Z).
- Files: revisions 1–7 in all three files, older text untouched; both round-7 comparisons PASS on all four relationships.
- Scope, trees, factors, tools, seeds: unchanged from § closing_checklist (revision_6) and re-confirmed on e78daed4… (the delta is one ordering sentence).
- XF3 class swept on all four policies: no remaining member. XF 1–13 otherwise as in revision_6. SRC-1 closed; SRC-2/SRC-3 are base text logged BLUEPRINT-KNOWN, outside this charter's write domain.
- Gates: round-7 snapshot all seven OK.
- Open charter REDs: none.

This difficulty passes the source-layer audit.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (revision_8)

- Same auditor, round 8 (seed-only rework); written before any round-8 GT reveal; revisions 1–7 untouched.
- Context read: audits/policy_kb/d3_ship_to_orders_backorders_and_returns/_verdict.md, src items of its latest revision only (SRC-R3-1 … SRC-R3-5).
- Entry gate: worklog tail = `REWORK round 8: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 8` (executed only): all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r8/gates.txt`); hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` — equals r7, as the brief requires
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` — equals r1–r7
  - `49106ddca8d55db9813d92f5642a76f067c6946a355e177f65f411d379b0db63  r8/task0.view.json` (changed)
  - `22adaeed6f8a39530b40f5a799392232cfd48a34f2cf6e435fd7a4f128e46d6f  r8/task1.view.json` (changed)
  Input complete.
- Charter and tools unchanged → every charter-global section (rule/compute equivalence, bindings and uuids, prerequisite graph and sentences, overwrite declarations, factor ladders, XF 1–13) carried forward by reference to revision_7 / revision_6 on these two hashes. No charter-level finding is possible in this round.
- contamination_disclosure: earlier rounds' GT known; no round-8 GT read before the per-task freezes.
- Seed producibility is judged against the owning products' charters in blueprint/products/ (the published docs/<product>/ render them). The per-task files carry the checks.

### findings (revision_8)

- No charter-level RED. Task-level: see 1.md R8-1 (cross-product seed state not producible, gold-moving). The class is "a cross-product periodic review whose published outcome the seed contradicts". Members checked on both worlds:
  - credit terms review: task 1 now consistent (fixed SRC-R3-1); task 0 has its next review due 2026-11-03, after the call date.
  - **pricing commitment review: task 1 not producible (R8-1).** Task 0 is producible: its implied qualifying spend in 2025-07-01 … 2026-06-30 is order merchandise 51249.75 + StockSmart 19923.70 = 71173.45, against a threshold of 56250.00.
  - StockSmart go-live anniversary review: Self-Scan cannot move down, and both programs meet the Self-Scan gate.
  - VMI non-moving bin removal: Self-Scan has no par review.
  - Credit finance charges: each matches its tier.

## closing_checklist (revision_8)

Written after both round-8 reveals (2026-10-18T01:53Z).
- Files: revisions 1–8 are present in all three files, with the older text untouched.
- Task 0 PASS on all four relationships. Task 1 RED on factors: R8-1, the seeded pricing agreement state contradicts pricing_commitment_review, and the scored election would move.
- The charter and tools are unchanged (e78daed4…, aa4a300d…), so every charter-global conclusion of revision_7 stands. No open charter RED.
- Seed checks on both worlds: every changed or added row is producible by its owning charter except CPA-32214's post-anniversary tier and commitment (R8-1). No added row leaves a write due on either call day. Both personas match. Both problem trees and every factor still bear weight on the seeded worlds.
- Gates: the round-8 snapshot is all seven OK.
- The difficulty does not close until R8-1 is resolved.

VERDICT revision_8: task0=PASS task1=RED SOURCE-FACTOR(R8-1) charter=CLEAN

## revision_9

## charter_global_frozen (revision_9)

- Same auditor, round 9 (seed-only rework); written before any round-9 GT reveal; revisions 1–8 untouched.
- Entry gate: worklog tail = `REWORK round 9: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 9` (executed only): all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r9/gates.txt`); hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` — as required
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` — as required
  - `8bb06052fcdad5d5bd9b04b5fd180400977e49add18c16479e251be761bf2f7c  r9/task0.view.json` (changed: one field)
  - `976c721ac2ba08b615daa918834cd061c2737bb805f8b7e2e2797ed64dbae433  r9/task1.view.json` (changed: 128 order lines, 158 credit rows)
  Input complete. Charter and tools unchanged → every charter-global section carried forward by reference to revision_7. No charter-level finding possible.
- contamination_disclosure: earlier rounds' GT known; no round-9 GT read before the per-task freezes.

### periodic reviews — recorded outcome vs what the seeded records produce (both worlds, one place)

| world | review (owning charter) | date | what the seeded records produce | seeded state | verdict |
|---|---|---|---|---|---|
| 0 | order anniversary review, Euclid | 2026-10-14 (call day) | due | not yet recorded | the task's own P1 write (carried) |
| 0 | order anniversary review, Bedford | anniversary 2026-05-17, recorded 2026-05-18 | no order_line_shipped within 12 months → keeps Corbett Standard Ship-To | Standard, last_review_date 2026-05-18 | consistent (new in r9) |
| 0 | inactivity suspension, Euclid / Bedford | — | last orders 2026-09-08 / 2026-09-22 | active | consistent |
| 0 | credit terms review, Net 45 Business (12-month cycle) | last 2025-11-03, next 2026-11-03 | no invoice due in the window → 100 % → keeps tier | Net 45 Business | consistent; next after the call |
| 0 | credit finance charge / holds | monthly | INV-3381206 repaid 2026-05-28, before the May month end; one returned payment, below the hold count | no charge, no hold | consistent |
| 0 | **pricing commitment review, CPA-31206** | anniversary 2026-07-01 | qualifying spend from credit_invoice_posted rows dated 2025-07-01 … 2026-06-30 = **924.00** (one invoice), < 56250.00 → moves down to Corbett Volume Discount Agreement (commitment 25000.00) | active Category Contract, commitment 75000.00 | **not produced — R9-1** |
| 0 | pricing rebate | quarterly | Category Contract rebate_eligible false | none | consistent |
| 0 | StockSmart go-live anniversary | 2026-02-24 | Self-Scan cannot move down | Self-Scan active | consistent |
| 1 | order anniversary review, Twinsburg | 2026-06-12 → recorded 2026-06-15 | no shipped merchandise in 12 months → keeps level | Route Delivery | consistent |
| 1 | order anniversary review, Macedonia | 2026-08-03 → recorded 2026-08-04 | 12-month spend about 62856.00 against a 3000.00 threshold → keeps level | Standard | consistent |
| 1 | inactivity suspension | — | Twinsburg last order 2024-06-03 → suspended; Macedonia orders monthly → active | as seeded | consistent |
| 1 | credit terms review, Net 30 Preferred | 2026-04-14 | 24 invoices due 2025-04-15 … 2026-04-14, 23 on time = 95 % ≥ 90 → keeps tier; next 2027-04-14 | Net 30 Preferred | consistent |
| 1 | credit finance charges | month ends | eligible past-due only at 2025-12-31 (604.10 → 9.06) and 2026-04-30 (601.80 → 9.03) | exactly those two | consistent |
| 1 | credit holds / collections | daily | longest past due 16 days < 30 | no hold | consistent |
| 1 | pricing commitment review, CPA-32214 | 2026-04-01 | invoices 2025-04-01 … 2026-03-31: Macedonia 62856.00 + StockSmart 7307.05 = 70163.05 ≥ 56250.00 → keeps tier | Category Contract, 75000.00 | consistent — R8-1 closed |
| 1 | pricing rebate | quarterly | not rebate-eligible | none | consistent |
| 1 | StockSmart go-live anniversary | 2026-10-13 | gate met (12-month spend ≥ 6000, 25 bins); Self-Scan cannot move down | Self-Scan active | consistent; no write due on the call day |

### findings (revision_9)

- R8-1 closed (task 1).
- **R9-1 — SOURCE-FACTOR RED (task 0; same class as R8-1, XF13).** Detail and consequence are in 0.md § revision_9. The class across both worlds has this one remaining member.
- **Prior-coverage note:** revision_8 passed task 0's commitment review on the spend its shipments imply (71173.45). The round-9 standard is that every review must be reproduced from the seeded records, as task 1's completed ledger now is. Under that standard the seeded invoice rows give 924.00, so the revision_8 pass is revised here.

## closing_checklist (revision_9)

Written after both round-9 reveals (2026-10-18T02:02Z).
- Files: revisions 1–9 in all three files, with older text untouched.
- Task results:
  - Task 1 PASS on all four relationships; every periodic review is reproduced from its records.
  - Task 0 RED on factors (R9-1): its pricing commitment review is not reproduced from the seeded invoices.
- Charter and tools unchanged; no open charter RED.
- Seed checks:
  - Every new or changed row in both worlds is producible by its owning charter.
  - No write is due on either call day besides task 0's own anniversary review.
  - Both personas match.
  - Both trees and every factor bear weight on the seeded worlds.
- Gates: the round-9 snapshot is all seven OK.
- The difficulty does not close until R9-1 is resolved.

VERDICT revision_9: task0=RED SOURCE-FACTOR(R9-1) task1=PASS charter=CLEAN

## revision_10

## charter_global_frozen (revision_10)

- Same auditor, round 10 (seed-only rework of task 0). Written before any round-10 GT reveal; revisions 1–9 are untouched.
- Entry gate: the worklog tail is `REWORK round 10: gates 7/7 green` (only that line was read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 10` was executed only; all seven gates are OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r10/gates.txt`). Hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` — as required
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` — as required
  - `37beae1c30bcb315683483fe305fe2e8d6126f8cd2cbae5b77c52fc5ccd09d73  r10/task0.view.json` — changed
  - `976c721ac2ba08b615daa918834cd061c2737bb805f8b7e2e2797ed64dbae433  r10/task1.view.json` — byte-identical to r9 (`cmp` clean)
  Input is complete.
- Carry-forward: the charter and tools are unchanged, so the charter-global sections are carried forward from revision_7. Task 1's view is identical, so its revision_9 derivation, periodic-review rows and PASS carry forward. Only task 0 is re-derived.
- contamination_disclosure: earlier rounds' GT is known; no round-10 GT was read before the task-0 freeze.

### periodic reviews — task 0 rows updated from the r10 records (task 1 rows unchanged from revision_9)

| world | review | date | what the seeded records produce | seeded state | verdict |
|---|---|---|---|---|---|
| 0 | order anniversary review, Euclid | 2026-10-14 (call day) | due | not recorded | the task's own P1 write (carried) |
| 0 | order anniversary review, Bedford | 2026-05-17, recorded 2026-05-18 | 12-month spend 33750.00, 6-month 16488.00; 60 months open, so the lower of the two figures is used: 32976.00 ≥ 3000.00 → keeps Standard | Standard | consistent |
| 0 | inactivity suspension | — | Euclid last order 2026-09-08, Bedford 2026-09-22 (now backed by a booked line) | both active | consistent |
| 0 | credit terms review, Net 45 Business | 2025-11-03 | 28 invoices due 2024-11-04 … 2025-11-03, all on time = 100 % ≥ 85 → keeps the tier; next review 2026-11-03 | Net 45 Business | consistent; next review after the call |
| 0 | credit finance charges | month ends | only INV-3340038's 369.00 remainder is ever open past due (see O-R10-1); otherwise none | none | consistent under the charter's on-account draw |
| 0 | credit holds / collections | daily | longest lateness 13 days; one returned payment, below the hold count of 2; open past due at most 369.00, below 1000.00 | none | consistent |
| 0 | pricing commitment review, CPA-31206 | 2026-07-01 | invoices 2025-07-01 … 2026-06-30 (shipments + StockSmart) less return credits = 104149.45 ≥ 56250.00 → keeps the tier | Category Contract, 75000.00 | consistent — R9-1 closed |
| 0 | pricing entry gate at signing | 2025-07-01 | trailing purchases ≈ 61026.10 ≥ 60000.00 | Category Contract | consistent |
| 0 | pricing rebate | quarterly | not rebate-eligible | none | consistent |
| 0 | StockSmart go-live anniversary | 2026-02-24 | Self-Scan cannot move down | Self-Scan | consistent |

### findings (revision_10)

- R9-1 closed: the class has no remaining member on either world.
- No charter-level RED.
- O-R10-1 (task 0, observation): ACH-3360075 (2379.00) pays INV-3340038 (2748.00) short by exactly the ON-ACCOUNT return credit CM-3305936 (369.00).
  - Under credit_evt_credit_memo ("held ON-ACCOUNT as an open credit that the next payment or refund draws on"), the invoice is settled on 2026-06-03, and ar_balance 8705.70 equals the open invoices less that credit.
  - Nothing records the draw against the invoice. A reader of the invoice rows alone would see 369.00 past due from 2026-06-07, above the 250.00 waiver, and so monthly finance charges of 4.61 each from 2026-06 to 2026-09.
  - No scored input reads this: rotation_standing counts returned payments only, and there is no hold since 369.00 < 1000.00.

## closing_checklist (revision_10)

Written after the round-10 reveal (2026-10-18T02:09Z).
- Files: revisions 1–10 in all three files, with older text untouched. Both tasks PASS all four relationships.
- Charter and tools are unchanged, so every charter-global conclusion of revision_7 stands; no open charter RED.
- Seed:
  - Every row added to task 0 is producible by its owning charter.
  - Every periodic review on both worlds reproduces its recorded outcome from the seeded records (§ periodic reviews, revisions 9 and 10).
  - No write is due on either call day besides task 0's own anniversary review.
  - Personas match.
  - Trees and every factor bear weight; fall-backs differ from gold (Route Delivery / 23; Route Delivery / Standard).
- Gates: the round-10 snapshot is all seven OK.
- Observations on record (not grounds for rework): O1, O6 (moot), O7, O8, O10–O14, O16, T1-O1, O-R10-1.

This difficulty passes the source-layer audit.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

## charter_global_frozen (revision_11)

- Same auditor, round 11 (final seed-only rework). Written before any round-11 GT reveal; revisions 1–10 untouched. Context read: the KB verdict's SRC-R4-1 … SRC-R4-4 lines only.
- Entry gate: worklog tail = `REWORK round 11: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 11` was executed only; all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r11/gates.txt`). Hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` — as required
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` — as required
  - `0c5a4f255f3ba731f4daf91622726166b3c056d186116173ea17b9fd5c565c44  r11/task0.view.json` — changed
  - `93346780c80d314ec37a290824f0fb4884a0214213de12d48cdbf49c63a47b3b  r11/task1.view.json` — changed
  Input complete. Charter-global sections carried forward from revision_7.
- contamination_disclosure: earlier rounds' GT known; no round-11 GT read before the per-task freezes.
- Ledger audit: a scratch script, `/tmp/audit_d3_ship_to_orders_backorders_and_returns_0068/ledger_check.py`, was run on both r11 views. It checks invoice ↔ shipment, fee, StockSmart-billing and setup-fee matching; memo targets; open balance vs ar_balance; finance-charge month ends; lateness and holds; on-time at the last terms review; and pricing qualifying spend.

### periodic reviews and recurring charges — r11 records (both worlds, one place)

| world | item | records produce | seeded | verdict |
|---|---|---|---|---|
| 0 | Euclid anniversary review (call day) | due | not recorded | the task's own P1 write |
| 0 | Bedford anniversary review 2026-05-18 | 32976.00 ≥ 3000.00 → keeps Standard | Standard | consistent |
| 0 | credit terms review 2025-11-03 | 28 / 28 on time = 100 % ≥ 85 → keeps Net 45 Business; next 2026-11-03 | Net 45 Business | consistent |
| 0 | finance charges | no month end with eligible past-due ≥ 250.00 (only INV-3381206, 13 days late, repaid before the May month end) | none | consistent |
| 0 | holds / collections | one returned payment (< 2); lateness ≤ 13 days | none | consistent |
| 0 | pricing commitment review 2026-07-01 | 104149.45 ≥ 56250.00 → keeps Category Contract | Category Contract, 75000.00 | consistent |
| 0 | StockSmart monthly minimum | only 2023-02 (go-live month, no spend) below 500.00 → one 75.00 fee | VPF-340901 75.00, invoiced | consistent (SRC-R4-3 closed) |
| 0 | StockSmart setup fee / bins / anniversary | 250.00 at go-live, invoiced; 25 bins; Self-Scan cannot move down | as seeded | consistent |
| 0 | Route Delivery drop-ship fees | 10.00 per drop-shipped line, invoiced as order_service_fee merchandise | two 10.00 rows (2025-10-29, 2026-05-12), invoiced | consistent (SRC-R4-2 closed) |
| 0 | return-credit memos | CM-3305118 → INV-3340036, the invoice that billed SP-30392 (correct). CM-3305936 → per credit_evt_credit_memo, ON-ACCOUNT, because INV-3340034, the invoice that billed CT-30871, was paid in full on 2026-04-06 | CM-3305936 applied to INV-3340038, an unrelated Bedford invoice | **not produced — R11-1** |
| 1 | Twinsburg / Macedonia anniversary reviews | keep Route Delivery / Standard | as seeded | consistent |
| 1 | credit terms review 2026-04-14 | 23 / 24 = 95 % ≥ 90 → keeps Net 30 Preferred | Net 30 Preferred | consistent |
| 1 | finance charges | exactly 2025-12-31 (9.06) and 2026-04-30 (9.03) | the same two | consistent |
| 1 | holds | lateness ≤ 16 days | none | consistent |
| 1 | pricing commitment review 2026-04-01 | 70163.05 ≥ 56250.00 → keeps tier | Category Contract, 75000.00 | consistent |
| 1 | StockSmart setup fee | 250.00 at go-live, invoiced | VPF-352900 + invoice | consistent (SRC-R4-4 closed) |
| 1 | StockSmart minimum / anniversary 2026-10-13 | every month ≥ 500.00; gate met; no write | as seeded | consistent |

On both worlds ar_balance equals the open invoices, net of payments and memos as seeded (8705.70; 5908.35). SRC-R4-1 is closed: FS-30219 on 2025-03-11 is now 2.185, the Account Price Schedule price of list 2.30; the 2026-09-09 price of 1.84 is that list less the 20 % fasteners discount.

### findings (revision_11)

- SRC-R4-1 … SRC-R4-4 closed. No charter-level RED.
- **R11-1 — SEED RED (XF13, task 0; introduced by this rework).** Details are in 0.md § revision_11. The fix of my O-R10-1 replaced a producible state with an unproducible one.
  - Revision_10's state was producible: CM-3305936 held ON-ACCOUNT, and the next payment, short by 369.00, drawn on it. It was only unrecorded on the invoice rows.
  - Members (complete list): CM-3305936's applied_invoice_number. No other memo, invoice, fee or payment row on either world deviates.

## closing_checklist (revision_11)

Written after both round-11 reveals (2026-10-18T02:24Z).
- Files: revisions 1–11 are in all three files, with older text untouched.
- Task 1 PASSes on all four relationships, and every row of its world is producible.
- Task 0 PASSes on all four relationships and its scored values are unchanged. One seeded credit row is not producible by the credit charter (R11-1, XF13, no scored consequence).
- Charter and tools are unchanged, and no charter RED is open.
- Seed checks: every periodic review and recurring charge on both worlds reproduces its recorded outcome (§ periodic reviews, revision_11). No write is due on either call day besides task 0's own anniversary review. Both personas match. Trees and every factor bear weight.
- Gates: the round-11 snapshot shows all seven OK.
- The difficulty closes once R11-1 is fixed.

VERDICT revision_11: task0=RED XF13(R11-1) task1=PASS charter=CLEAN

## revision_12

## charter_global_frozen (revision_12)

- Entry gate: worklog tail = `REWORK round 12: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 12` was executed only, and all seven gates are OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r12/gates.txt`). Hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` — as required
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` — as required
  - `c01a2a070de89b83248125332a87f327186ce51e3d22f30fc634c67a073859d2  r12/task0.view.json`
  - `93346780c80d314ec37a290824f0fb4884a0214213de12d48cdbf49c63a47b3b  r12/task1.view.json` (byte-identical to r11)
- Carry-forward: the charter-global sections carry forward from revision_7; task 1 carries forward from revision_11.
- Diff of the r12 views against r11: task 0 changes exactly one field, CM-3305936's applied_invoice_number (INV-3340038 → ON-ACCOUNT); task 1 has no change.
- contamination_disclosure: earlier rounds' GT is known; the task-0 freeze preceded the round-12 reveal.

### findings (revision_12)

- R11-1 is closed. CM-3305936 is held ON-ACCOUNT as credit_evt_credit_memo requires, and ar_balance 8705.70 reconciles to the open invoices less that open credit. The periodic-review table of revision_11 stands; the memo row now reads "consistent".
- No other change, no new defect and no regression. Scored values are unchanged on both tasks.

## closing_checklist (revision_12)

- Revisions 1–12 are in all three files, with older text untouched.
- Both tasks PASS all four relationships.
- Every seeded row on both worlds is producible by its owning charter, and every periodic review reproduces its recorded outcome. No write is due on either call day besides task 0's own anniversary review.
- Personas, trees and factor weights hold.
- The charter and tools are unchanged, and no charter RED is open.
- Gates: the round-12 snapshot is all seven OK.
- Observations on record (not grounds for rework): O1, O6 (moot), O7, O8, O10–O14, O16, T1-O1, O-R10-1.

This difficulty passes the source-layer audit.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

## charter_global_frozen (revision_13)

- Entry gate: worklog tail = `REWORK round 13: gates 7/7 green` (only that line read). `/tmp/erl0068_coord/snapshot.sh d3_ship_to_orders_backorders_and_returns 13` was executed only; all seven gates OK (`.audit_views/policy/d3_ship_to_orders_backorders_and_returns/r13/gates.txt`). Hashes:
  - `e78daed4f2c2787a1100840669bb66fee4f927286d470584a973ccce8d3ce148  order.extended.yaml` — as required
  - `aa4a300d258f63361cde116300351898f63d863167800ba786abc6dac7f08e4a  task_tools.py` — as required
  - `994ccd0ffa9cb4b77d24793a24ed94df4069dfddec9c438abc4c87a8c8b260b9  r13/task0.view.json`
  - `2179605161fc05693398997ba3dd5156dfd53b85290a67f55e9285f8063f39f0  r13/task1.view.json`
  Charter-global sections carry forward from revision_7.
- Context read: the KB verdict revision_5 rows SRC-R5-1 … SRC-R5-4 only.
- contamination_disclosure: the per-task sections of this revision were written after the round-13 GT reveal (2026-10-18T02:47Z). Every conclusion in them rests on input-identity checks run before that reveal: every table and row any scored binding reads is identical to r12, as listed below. No derivation depends on GT.

### diff of the r13 views against r12 — exactly the four KB items

| item | change seen (both worlds unless noted) | producibility check | verdict |
|---|---|---|---|
| SRC-R5-1 | One vmi_program_fee_charged bin_add_fee row per program: task 0 VPF-340902 90.00 on 2023-02-28; task 1 VPF-352901 90.00 on 2023-10-31. Each has its invoice and payment. | 25 new bins in the go-live month less 5 included adds = 20 × 4.50 = 90.00; one fee of the type in the month. | closed |
| SRC-R5-2 | 311 (task 0) / 290 (task 1) vmi_replenishment_delivered lines added, one set per billed scan order. The 25 bins were re-pointed to StockSmart-only SKUs (VM-…) with re-labelled min/max. | Every billed scan order has deliveries whose extended amounts sum exactly to its billed amount, on the same date. Every delivered SKU is a bin SKU, and no quantity exceeds its bin's max. Each unit price is the price in effect on the delivery date: list less the Account Price Schedule 5 % before the item's contract line takes effect, then the contract price. Extended amount = quantity × unit price. | closed |
| SRC-R5-3 | 25 pricing_item_added lines for the VM SKUs. Task 0's lines are effective 2025-07-01 (its agreement now carries 27 items); task 1's are effective 2025-04-01 (25 items). | ≥ fixed_net_items_min 25. Contract prices equal list less the Category Contract discounts (ratios 0.80–0.90). Every item moved at least 28 units in the last 12 months, against the 12-unit minimum. **No overlap with any order-line SKU**, and no BR-31406 line was added. | closed |
| SRC-R5-4 | The settling payments now equal their invoices: task 0 WIR-3306104 924.00; task 1 WIR-3201930 1200.00, ACH-3391402 604.10, ACH-3392215 601.80. Separate payments were added for each returned-payment fee and finance charge. | Payments are applied to the documents they settle. Every invoice and charge nets to zero or to its true open amount. ar_balance reconciles exactly: 8705.70 (task 0, after the ON-ACCOUNT 369.00) and 5908.35 (task 1). | closed |

Unchanged in both worlds, byte for byte: order_lines, ship_to_accounts, pricing_agreements, vmi_programs, every pre-existing vmi_activity row (all replenishment_billed amounts and dates), the returned-payment, finance-charge and returned-payment-fee rows, the credit account, and every pre-existing pricing item. Persona and frozen_time unchanged.

### periodic reviews / dues (r13)

Every row of § periodic reviews (revision_11) reproduces unchanged from the records:
- **Credit:** on time 100 % (task 0, 2025-11-03) and 95 % (task 1, 2026-04-14). Finance charges exactly as seeded: none on task 0, and on task 1 2025-12-31 9.06 and 2026-04-30 9.03. No hold on either world.
- **Pricing commitment review:** 104149.45 (task 0) and 70163.05 (task 1), both ≥ 56250.00.
- **StockSmart:** minimum fees as before. The bin-add fees fall in the go-live month only.
- **Anniversary reviews:** consistent.

No write is due on either call day besides task 0's own Euclid review. O-R10-1 is unchanged.

### findings (revision_13)

- SRC-R5-1 … SRC-R5-4 closed.
- No new defect, no regression, no charter RED.
- Scored inputs unchanged → every scored value, factor tier and sensitivity is unchanged (see the task files).

## closing_checklist (revision_13)

- Revisions 1–13 in all three files, older text untouched.
- Both tasks PASS all four relationships.
- Every seeded row producible.
- Every periodic review reproduced; no write due on either call day besides task 0's own anniversary review.
- Charter and tools unchanged; gates all OK.

This difficulty passes the source-layer audit.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN
