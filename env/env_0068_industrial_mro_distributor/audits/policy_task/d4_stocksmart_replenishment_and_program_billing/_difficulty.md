# Policy-task audit — d4_stocksmart_replenishment_and_program_billing / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-16T23:44Z, auditor: independent policy-task auditor (erl-task-policy-audit), written before any task GT was revealed; contains nothing derived from GT.
- `tasks/d4_stocksmart_replenishment_and_program_billing/vmi.extended.yaml` sha256 be81e46ff9ca2d922ff4ed4e80e2ff0cb21d174f3a37c3d9f1922142ec545a8a
- `tasks/d4_stocksmart_replenishment_and_program_billing/task_tools.py` sha256 09b2eef9b3cd9f91ec7bfd4b7cc2f590e46c31a10dde976c6bda1ef50e8b782c
- Read: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py-not-needed, products/vmi.yaml and, for cross-category states, products/{order,vending,credit,pricing}.yaml), the extended charter, task_tools.py, the two masked views (r1/task0.view.json 821ed562…, r1/task1.view.json b1489d97…), audits/render_source/XF_recipe.md, r1/gates.txt.
- Masked / not opened: tasks/*.json, plan.md, worklog.md; every key in `_masked_keys` (design_rationale, db_closure*, solvability_contract, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents). No recursive search was run over tasks/ or the scenario root.
- Entry conditions: gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred), masked views and hashes supplied and re-verified (all four hashes match). Input complete.
- Base copy: lines 1–828 of the extended charter are byte-identical to blueprint/products/vmi.yaml (diff empty).

### policy_conflict_scan
Six extended policies, two problem trees:
- Tree A (vended item to consignment): `vmi_ext_vended_item_fill_level` (P1, user tool, max_qty of a new consigned bin) → `vmi_ext_consigned_reorder_point` (P2, agent, min_qty par entry) → `vmi_ext_opening_consignment` (P3, agent, vmi_consignment_stocked quantity).
- Tree B (consignment converted at par review): `vmi_ext_converted_critical_fill` (P4, user tool, customer-owned max_qty + critical flag) → `vmi_ext_conversion_reorder_point` (P5, agent, conversion par entry min_qty, consigned=false) → `vmi_ext_hold_converted_fill` (P6, agent, first customer-owned replenishment quantity under hold).
- Subjects: P1/P2/P4/P5 all write `vmi_bin_set`, but on disjoint objects: P1 = change_type new_bin consigned=true (tool fixes min 0, critical false); P2 = par_change consigned=true; P4 = par_change by customer with min 0; P5 = par_change consigned=false. P3 writes vmi_consignment_stocked; P6 writes vmi_replenishment_delivered. No two policies set the same field of the same row kind.
- Object selectors: P1 "transferred item" = most recent customer VendPoint selection removal; P2/P3 = most recent consigned new-bin entry's item plus the item's most recent customer removal machine; P4/P5/P6 "converted item" = most recent vmi_consignment_withdrawn. Within a tree the selectors coincide on every world the tree's first write produces; across trees they read disjoint records.
- Triggers / time anchors: all "today" (frozen date) with the shared "age in whole months" convention stated in each rule; no conflicting anchor.
- Cross-category reads: vending (planogram, transactions), order (order_lines, route_deliveries_per_week, opened_date), credit (ar_balance, credit_limit, status, hold_reason, returned payments), pricing (pricing_items, tier params) — read-only, no writes outside vmi.
- Terminal states: Tree A ends with a consigned bin carrying stock (consigned_stock_value up); Tree B ends with a customer-owned bin and one delivered line at the latest visit. No terminal-state collision.
- Scope exclusivity: by construction one tree per task (task0 = Tree A, task1 = Tree B as inferred from user_scenario + seed; confirmed only after reveal). Claimed event types in blueprint (vmi_bin_set, vmi_replenishment_delivered, …) are not all exercised; the claim is a ceiling, not a coverage obligation.
- Conflict found: P6 against base `vmi_evt_replenishment` (see F3). No other policy reaches a conclusion incompatible with another on an overlapping subject.

### rule_compute_equivalence
Mechanical sweep (scratch script, /tmp/audit_…_0068): every `compute_basis` quote is a verbatim substring of its rule (all six policies, 0 misses); every compute binding has a basis entry; every sentence of every `baseline.rule` is in its rule; every `policy_source` is in its own rule. RND placement: P1/P2/P4/P5 `int(-(-RND(x,6)//1))` = "taken to six decimal places and (then) rounded up"; P3 `int(RND(x,6)//1)` = "rounded down to a whole unit"; P6 `MX(0, int(RND(left/price,6)//1))` = "taken to six decimal places and rounded down, never below zero"; P6 fill price RND(…,4) = "rounded half up to 4 decimal places". P2/P5 add the unit buffer after rounding, as the rule states ("…rounded up to the next whole unit, plus the draw buffer / lumpy-demand units"). Filters: change_source='customer' ↔ "made at the customer's request"; vending_machine_id=removal_machine ↔ "vends … at any other machine are not counted"; ship_method='next_day_air' ↔ "Next-day-air bookings"; visit_type filters ↔ "scheduled visits" (P1, P2), "scheduled or onsite daily visits" (P4), "onsite daily visits" (P5); critical_item=True ↔ "critical replenishment already delivered at the same visit" (P6).
Defects found: F5 (backorder ladder branch present only in compute) and F6 (absent-record branches with no rule sentence and a None comparison in compute). Everything else: equivalent in both directions.

### action_binding_and_uuids
- (target_tool, computes): submit_vended_item_bin_request_0334ff8e/max_qty (P1), record_consigned_reorder_point_33b5bdc5/min_qty (P2), stock_opening_consignment_2b5b5df3/quantity (P3), submit_critical_bin_request_f65e9169/max_qty (P4), record_customer_owned_conversion_b1c25ecb/min_qty (P5), book_converted_bin_fill_19b3cec5/quantity (P6) — each claimed once.
- uuid8s 0334ff8e, 33b5bdc5, 2b5b5df3, f65e9169, b1c25ecb, 19b3cec5: no shared prefix/suffix, no sequence pattern; independent.
- Owners: P1 and P4 tools owner="user"; the rest owner="agent". No body validates eligibility, ordering or any prerequisite (each body is find program → create row → return receipt; P3 also updates consigned_stock_value).
- Docstring defects: F7 (ordering words naming another write in two user tools) and F8 (an effect claimed that the body does not perform).

### prerequisite_graph
Edges (all `form: state`, no fallback declared):
| id | blocked | depends on | kind / gate | policy_source located in own rule | resolved_by = dep target_tool |
|---|---|---|---|---|---|
| E1 | P2 | P1 | value_input / new_item (binding exists) | yes | yes |
| E2 | P3 | P1 | value_input / fill_to (exists) | yes | yes |
| E3 | P3 | P2 | value_input / reorder_point (exists) | yes | yes |
| E4 | P5 | P4 | value_input / critical_flag (exists) | yes | yes |
| E5 | P6 | P4 | state_gate / vmi_bins.critical_item | yes | yes |
| E6 | P6 | P5 | state_gate / vmi_bins.consigned | yes | yes |
P1 and P4 carry `prerequisite: []`. Every `problem` is an extended id of this file; none is a base policy or self; graph acyclic (P1→P2→P3, P1→P3; P4→P5→P6, P4→P6). Conditions match the sentences (E5's "(and its critical flag)" is vacuous — every entry carries a flag — not a strengthening). No authoring-viewpoint wording in any prerequisite field. Observation O3: E6's gate is eligibility only — P6's compute does not read `consigned`, so the scored quantity is identical with or without P5; the edge bears weight only through the gate (the write must not happen before it).

### prerequisite_sentences
- E1 "Corbett's reorder point for such a bin is recorded only after the customer's new-bin entry for it, flagged consigned, stands in the program's bin history." — ordering connective "only after"; state = a vmi_bin_set new_bin entry with consigned=true; no tool/id/snake_case. Only P1's tool writes change_type new_bin consigned=true (P2/P4/P5 write par_change). Derivation: sentence → records (no consigned new_bin) → P1's rule ("A customer's own written request for a new consigned bin … carries the fill-to level") → submit_vended_item_bin_request. Single reading.
- E2 "The opening stock of such a bin is worked out only after its new-bin entry, flagged consigned and carrying its fill-to level, stands in the program's bin history." — same state, same unique write (P1).
- E3 "The opening stock is not placed until the bin's par level entries carry a reorder point above zero." — "not until"; P1's entry carries min 0 (tool docstring and body), P2 writes a par_change with the reorder point; P4/P5 operate on converted (non-new) bins. Unique write P2. Derivation: sentence → P2's rule ("Corbett records that bin's reorder point … as a par level entry").
- E4 "Corbett's conversion entry for such a bin is recorded only after the customer's written request setting the bin's customer-owned fill-to level stands in its bin history." — "only after"; unique write P4.
- E5 "That fill is not booked until the bin's entries carry the customer-owned fill-to level set by the customer's written request for it." — unique write P4.
- E6 "That fill is booked only after the bin's entries show it no longer consigned." — P4's tool writes the `consigned` flag passed in ("true when the bin's latest entry still shows the bin as consigned"), so on any world where the latest entry is still consigned only P5 writes consigned=false. Unique write P5.
- Depended-on rules do not restate any sentence; no rule carries a second wording, a tool name or another problem's id; no cross-problem order is stated without a declared edge (P2's/P5's opening "When … stands/has been withdrawn" clauses are triggers on the same edge's state or on a seeded event).
- Observation O2: E1/E2/E4/E5 name the performer ("the customer's new-bin entry", "the customer's written request"); vmi_bins has no field that distinguishes a customer request from a Corbett entry (schema: change_reference "Customer request or review reference (VBR-NNNNNN)"; all four tools emit VBR-). No second reading is demonstrable on either world, so not a RED.
- Docstring sequence silence: FAILS — see F7.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:
- vmi_bins_and_par S1 "…at any time on an active program; changes take effect from the next visit or scan." — P1, P2, P4, P5 follow (writes dated today, no visit placement claimed). P3 departs (opening stock at today's visit) and declares it: overwrite retires "changes take effect from the next visit or scan." with a self-scoped replaced_by that restates the base for every other change. Valid.
- vmi_bins_and_par S2 special stock cap / S3 par review removals — followed by all. S4 "A bin is flagged critical only at the customer's written request" — P4 follows (flag set in the customer's own request); P2/P5 only carry the existing flag.
- vmi_evt_consignment S1 "Consigned bins are allowed only on a tier whose consignment_available is true, and consigned stock is placed only while … at or below consigned_value_cap_usd" — P1 and P3 restate it. S5 "At each par review a consigned item turning fewer than … is withdrawn and converted to customer-owned replenishment" — P4/P5/P6 follow. S2–S4 untouched.
- vmi_evt_replenishment (P6): S1/S2 status gates — P6 restates. S2 cap clause "and only up to critical_item_replenishment_cap_usd per visit (bins are filled in bin label order until the next bin would exceed the cap)" — retired by a self-scoped overwrite. S3 "Every bin at or below its min level at a visit or self-scan is filled to its max level under auto_replenish_to; each item is billed at the price pricing_price_basis gives for the delivery date" — P6 fills a capped bin to "the lesser of the bin's fill-to level and the whole units the allowance left buys", i.e. below its max level, and this sentence is named by no overwrite → undeclared override (F3). The same rule also keeps, in its own replaced_by, "bins are still filled in bin label order until the next bin would exceed it", which stops filling at a bin whose fill exceeds the allowance → internal contradiction (F3). Pricing half of S3: P6's fill price coincides with pricing_price_basis on every in-scope line (scope guard removes category-discount, special-order and quantity-break removal lines); observation O9 only.
- P2 and P5 Corbett par entries are counted by base vmi_msr_bin_changes_month toward par change fees (observation O11; not a scored quantity of this charter).

### factor_ladders
| policy | factor | label | ladder tiers (reachable on this write) | multi-source | cross_difficulty | verdict |
|---|---|---|---|---|---|---|
| P1 | usage_trend | method | 3 | no | vending | mislabelled (F1) |
| P1 | restock_cover | parameter | 3 stated / 2 reachable | yes (tier + visits) | – | dead tier (F2) |
| P1 | route_cover | parameter | 3 | no | order | ok |
| P1 | vend_safety | parameter | 3 | no | vending | ok |
| P1 | abc_share | parameter | 3 | no | vending | ok |
| P1 | payment_exposure | parameter | 3 | no | credit | ok |
| P2 | visit_gap | method | 4 stated / 3 reachable | yes | – | mislabelled (F1), dead tier (F2) |
| P2 | backorder_allowance | parameter | 3 (+ branch only in compute) | yes | order | F5 |
| P2 | rush_allowance | parameter | 3 | no | order | ok |
| P2 | route_allowance | parameter | 3 | no | order | ok |
| P2 | draw_buffer | parameter | 3 (absent-record undefined) | no | vending | F6 |
| P2 | supply_allowance | parameter | 3 | partly | vending | ok |
| P3 | trial_level | method | 3 | no | vending | ok (midpoint tier is a new operation) |
| P3 | credit_room | parameter | 3 | same record | credit | ok |
| P3 | supply_check | parameter | 3 (+ compute-only branch) | yes | order | F5 |
| P3 | site_age | parameter | 3 | no | order | ok |
| P3 | return_rate | parameter | 3 | yes (two event kinds) | vending | ok |
| P4 | draw_basis | method | 3 (lumpy tier undefined when nothing on record) | no | – | F6 |
| P4 | storeroom_cover | parameter | 3 | yes | – | ok |
| P4 | outage_cover | parameter | 3 | no | – | ok |
| P4 | rush_cover | parameter | 3 | no | order | ok |
| P4 | supply_cover | parameter | 3 | partly | order | ok |
| P4 | limit_share | parameter | 3 | same record | credit | ok (O7) |
| P5 | replenish_gap | method | 3 stated / 2 reachable | yes | – | mislabelled (F1), dead tier (F2) |
| P5 | backorder_lead | parameter | 3 (+ compute-only branch) | yes | order | F5 |
| P5 | delivery_lead | parameter | 3 | no | order | ok |
| P5 | hold_lead | parameter | 3 | yes | credit | ok |
| P5 | lumpy_buffer | parameter | 3 (absent-record undefined) | no | – | F6 |
| P6 | hold_service | method | 3 | yes | credit | ok |
| P6 | fill_price_basis | method | 3 | yes | pricing | gated (F4) |
| P6 | hold_share | parameter | 3 | no | credit | gated (F4) |
| P6 | conversion_release | parameter | 3 | no | – | gated (F4), O6 |
- Every tier of every ladder is stated in the rule (condition and value/method) and implemented in its `decides` binding; bindings are disjoint within each policy; no `decides` is `result`; no factor reads another factor's binding (mechanical read check per policy). Assembly sentences are generic ("every added cover week", "every share that applies", "every allowance day added") and fix the non-commuting order where it matters (round, then add the unit buffer).
- Counts surviving the tests: P1 — 0 method (usage_trend struck), 5 parameter; P2 — 0 method (visit_gap struck), 5 parameter; P3 — 1 method, 4 parameter; P4 — 1 method, 5 parameter; P5 — 0 method (replenish_gap struck), 4 parameter; P6 — 2 method, 2 parameter, three of four gated through hold_service.
- Realism (top priority): trend/lumpy demand bases, review-period and lead-time allowances, ABC value class, emergency-restock and rush-booking safety, supply allowances for special/backordered items, credit-exposure shares on Corbett-owned consignment, and critical-item hold allowances are all treatments a B2B MRO distributor applies; fall-throughs (2 weeks cover, no allowance, share 1, list-less-discount, whole fill) are ordinary defaults. Exceptions: F2 (Onsite Storeroom gets more cover than Twice-Weekly) and observations O6/O7.

### findings
**F1 — SOURCE-FACTOR RED, XF class 11 (mislabelled method).** Class members (complete list):
1. P1 `usage_trend`: tiers "latest-month net vends × 12 / 52", "half of latest + middle month × 12 / 52", "net vends of the last three months / 13" — all three are the mean monthly net vend over a window of w = 1, 2, 3 months × 12/52 (3m/13 = (3m/3)·12/52). Only the window length changes.
2. P2 `visit_gap`: tiers "1 day", "30 / scheduled visits completed", "7 days", "30 / visits the tier schedules" — two constants and one expression with its divisor swapped (completed vs scheduled). No tier changes how the gap is computed.
3. P5 `replenish_gap`: tiers "0 days", "7 days", "30 / visits the tier schedules" — two constants and the standard.
Consequence: with these struck, P1, P2 and P5 each have no `method` factor (minimum 1 per computation). Bears on task0 (P1, P2) and task1 (P5).

**F2 — SOURCE-FACTOR RED, unreal ladder (tier that holds of no customer reaching the write).** Members:
1. P1 `restock_cover` tier 1 "a program whose tier schedules 20 or more visits a month and that completed 18 or more scheduled visits in the latest month". Only StockSmart Onsite Storeroom schedules ≥20 visits (22), and its visits are recorded as `onsite_daily`, not `scheduled` (db_schema vmi_activity.visit_type enum; base event "A scheduled, emergency or onsite service visit"; the sibling rules P4 "scheduled or onsite daily visits" and P5 "onsite daily visits" count them so). The tier is unreachable, so an Onsite Storeroom (daily visits) always falls to the standard 2 weeks, while Twice-Weekly gets 1 week — a daily-serviced storeroom carrying twice the cover of a twice-weekly one is not a treatment any distributor publishes. Two reachable tiers.
2. P2 `visit_gap` tier "for a tier scheduling no visits at all, the visit gap is 7 days": the write is for a new consigned bin, consigned bins exist only on Twice-Weekly (8) and Onsite (22). Unreachable (P2 keeps 3 reachable tiers).
3. P5 `replenish_gap` tier "a program whose tier schedules no visits takes 7 days": the write follows a par-review consignment withdrawal; Self-Scan has par_level_review_months 0 and no consignment. Unreachable — P5's ladder has 2 reachable tiers.
Bears on task0 (P1) and task1 (P5).

**F3 — SOURCE-POLICY RED, XF class 5 (undeclared departure + overwrite contradicting its own rule), P6.** Base vmi_evt_replenishment S3 "Every bin at or below its min level at a visit or self-scan is filled to its max level under auto_replenish_to" is named by no overwrite, yet P6 fills a capped bin to "the lesser of the bin's fill-to level and the whole units the allowance left buys". And P6's own replaced_by keeps "bins are still filled in bin label order until the next bin would exceed it" — a bin whose fill would exceed the allowance is not filled — while the next rule sentence fills it partially. Two readings whenever the full fill exceeds the allowance left: partial units vs 0. Demonstration in task1's file.

**F4 — SOURCE-FACTOR RED, XF class 2 (factor gated through another factor), P6.** `fill_price_basis`, `hold_share` and `conversion_release` enter only `capped_units`, which is used only when `hold_service` selects the capped tier (`fill_units: fill_to if fill_mode == K('full_fill') else (MN(fill_to, capped_units) if …)`). Under hold_service's other tiers all three are inert. Demonstration in task1's file.

**F5 — SOURCE-POLICY RED, XF classes 9/10 (branch present only in compute).** Ladder text: "where more were opened than were filled or cancelled in those months, X; where some were opened and as many were filled or cancelled, Y; where none was opened, none". The case "some opened, more filled or cancelled in the window" (fills of backorders opened before the window) has no tier in the rule; compute gives it Y (`backorders > 0`). Members: P2 `backorder_allowance` (1 day), P3 `supply_check` (0.9), P5 `backorder_lead` (2 days). Not reached on either task's world (task0: 1 opened / 1 filled; task1: 1 opened / 0) — no per-task consequence; open charter defect.

**F6 — SOURCE-POLICY RED, XF class 9 (absent-record / None branch).** Members:
1. P2 `draw_buffer`: "The largest single vend … ever recorded at the demand machine sets the draw buffer … any smaller largest vend adds none" — no sentence for an item never vended there (P1 explicitly allows it: "zero where it has no vend there"); compute `XMAX(...) >= K(...)` on None.
2. P4 `draw_basis` lumpy tier: "billed in 4 or fewer of the last twelve billing months [includes 0] … largest single billing month of consumption on record × 12 / 52" — undefined for a withdrawn item never consumed (the slowest mover a par review withdraws); compute `None * 12`.
3. P5 `lumpy_buffer`: "largest single billing month of consumption on record … less adds none" — same absent case; compute `None >= 40`.
Not reached on either world (vends and consumption present) — open charter defect.

**F7 — SOURCE-POLICY RED, check 3 (docstring states sequence / names another write).** Members:
1. submit_vended_item_bin_request_0334ff8e: "with a reorder point of 0 that stays at 0 until Corbett records its own reorder point entry for the bin"; also "a request reference … that the customer can quote afterwards".
2. submit_critical_bin_request_f65e9169: "carries a reorder point of 0 that stays at 0 until Corbett records the bin's conversion entry".
Each names the write of another problem of its tree (P2 / P5) with an ordering word, i.e. the tool layer announces a hop the solver is meant to derive from the rules. Bears on task0 (P1→P2) and task1 (P4→P5).

**F8 — SOURCE-POLICY RED, XF class 8 (docstring effect absent from body).** book_converted_bin_fill_19b3cec5: "The line is dated today and joins the visit's replenishment for billing on the visit's invoice." The body creates one vmi_replenishment_delivered row only; no vmi_replenishment_billed / invoice row or link is written. Bears on task1.

**Observations (not grounds for rework):**
- O1 Thin seeds against the vmi charter: task0's Twice-Weekly program has 3 bins (entry gate 300) and no replenishment or monthly-minimum rows across 16 visits; task1's Onsite Storeroom has 5 bins (gate 1500); task1's three critical deliveries at today's visit have no price lines and no billing row.
- O2 Performer named in state-form sentences (above).
- O3 E6 gate not encoded in compute (above).
- O6 P6 `conversion_release` (allowance raised by half / a quarter of the value of Corbett's own just-withdrawn consigned stock) is defensible as "site exposure freed" but unusual.
- O7 P4 `limit_share` bakes a transient credit state into a standing customer-owned par level.
- O8 Unstated same-day ties: P1 "most recent vend" price, P6 "latest service visit", P2 "latest VendPoint selection entry" (removal rows also carry special_item), P4 "bin entries flag it as special stock" (any vs latest). No consequence on either world.
- O9 P6 tiers 2/3 read list_price / supplier_cost off a removal line; pricing_item_removed's charter fields do not list them (schema columns exist).
- O11 Corbett par entries counted toward par-change fees by base measure.
- O12 P1 baseline uses net_3m, which is declared inside usage_trend's binding set.

## closing_checklist
Not written: the difficulty does not pass (see each task file). Open charter REDs: F1–F8.

### post-reveal closing note (revision_1, written after both task files were frozen and compared)
- Both blind derivations match GT on every write, owner, order, argument, baseline_result and factor_sensitivity figure (0.md, 1.md §source_gt_comparison); task1's root additionally has the second reading 0 (F3).
- Charter-global findings F1–F8 above stand unchanged by the reveal; each lists all its members in one place: F1 = {P1 usage_trend, P2 visit_gap, P5 replenish_gap}; F2 = {P1 restock_cover tier 1, P2 visit_gap 7-day tier, P5 replenish_gap 7-day tier}; F3 = {P6 partial fill vs replaced_by label-order stop and base S3}; F4 = {P6 fill_price_basis, hold_share, conversion_release}; F5 = {P2 backorder_allowance, P3 supply_check, P5 backorder_lead}; F6 = {P2 draw_buffer, P4 draw_basis lumpy tier, P5 lumpy_buffer}; F7 = {submit_vended_item_bin_request_0334ff8e "until … reorder point entry" and "afterwards", submit_critical_bin_request_f65e9169 "until … conversion entry"}; F8 = {book_converted_bin_fill_19b3cec5 "joins the visit's replenishment for billing on the visit's invoice"}.
- Per-task proof-text class (not charter; all members across both tasks): tasks/0.json computations[2].factor_trace trial_level "(first 2026-05-05)" and design_rationale "vends since 2026-05-05" (first carousel vend is 2026-05-12); tasks/0.json computations[0].factor_trace usage_trend "highest month x 12/52" (rule says latest month); tasks/1.json design_rationale "Draft recomputation … with no second reading" (contradicted by F3).
- Gates were not re-run by this audit (the skill supplies them as entry conditions); closing checklist not applicable while REDs are open.

VERDICT revision_1: task0=RED[SOURCE-FACTOR:F1,F2,proof-text;SOURCE-POLICY:F7] task1=RED[SOURCE-POLICY:F3,F7,F8;SOURCE-FACTOR:F1,F2,F4] charter=F1,F2,F3,F4,F5,F6,F7,F8

## revision_2

## charter_global_frozen
- Frozen 2026-10-17 (UTC), before any round-2 task GT was revealed; contains nothing derived from round-2 GT.
- Entry input (coordinator snapshot `/tmp/erl0068_coord/snapshot.sh … 2`, r2/gates.txt): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Worklog tail: `REWORK round 2: gates 7/7 green`.
- Hashes: vmi.extended.yaml 720f42df1192c673d462f7f35cc2a6824b452aa3905c954a8a48e0e7e3470171; task_tools.py 805a54d8e4d6489c112111bfde69b108660ac9fb9e1109eb6e08425a09346e51; r2/task0.view.json b051e6703be6cd560044f264abd8a1bee20f9ec20b4f9ed658bb5e9028d72359; r2/task1.view.json f950d4d122ff8c8a407aad6d3d3ebce47f7e7c027281db938747ba7411e2a26d. Both shared inputs changed → every charter-global section re-derived in full below. Base copy (lines 1–828) still byte-identical to blueprint/products/vmi.yaml.
- Same masking as revision_1; tasks/*.json, plan.md not opened; worklog.md read only via the coordinator's `tail -1`.

### policy_conflict_scan
Same six policies, same two trees and target tools. Changes relevant to overlap: P6 now scopes itself to "While the customer's Commercial Credit Account is on hold … whose tier's credit hold service rule is critical items only, and whose bin entries of their latest date include one flagging it critical; any other bin, and any bin while the account is active, is outside this schedule" — no overlap with base full-fill replenishment. P2/P3 add a same-date tie rule on the item's removal; P5/P6 select the bin's entries "of their latest date". No new cross-policy conflict. Scopes still disjoint.

### rule_compute_equivalence
Mechanical sweep: all compute_basis quotes verbatim in their rules, every binding quoted, every baseline sentence in its rule, every policy_source in its own rule (0 misses). Rounding: P1/P2 add "never below zero" and compute wraps MX(0,…) ✓; P5 "(… plus the safety units), all times the value share, taken to six decimal places and rounded up" = `int(-(-RND((lead_demand + safety_units) * value_share, 6)//1))` ✓; P3 floor ✓; P6 floor with MX(0) ✓. Backorder ladders now read "as many or more were filled or cancelled in those months" and compute `backorders > 0` — equivalent (F5 closed). Remaining mismatches: absent-record branches stated in the rule but not implemented (F6, below).

### action_binding_and_uuids
Unchanged tool names/uuid8s (0334ff8e, 33b5bdc5, 2b5b5df3, f65e9169, b1c25ecb, 19b3cec5), each (target_tool, computes) claimed once; owners unchanged; bodies still validate nothing. Docstrings: the two "until Corbett records …" sentences and "afterwards" are gone (P1/P4 tools now say "a reorder point of 0, since the request itself names no reorder point"); the P6 tool no longer claims billing on the visit invoice. No ordering word, no other tool named, no example values (F7, F8 closed).

### prerequisite_graph
Edges E1–E6 unchanged in source sentence, form and direction; E4's gate is now `critical_entries` (exists in P5 compute). Acyclic; P1/P4 `[]`. O3 stands (E6 gate not read by P6's compute).

### prerequisite_sentences
Unchanged sentences, same single resolving write per state-form edge (P4's tool still writes the `consigned` value of the latest entry, so only P5 writes consigned=false). O2 (performer named; no requester field in vmi_bins) stands as an observation.

### override_declarations
- P3: unchanged valid overwrite of "changes take effect from the next visit or scan."
- P6: two overwrites of vmi_evt_replenishment — (1) the cap clause, replaced for "the first customer-owned fill of a converted critical bin, and only that fill … it is not passed over when its whole fill would exceed what is left; every other replenishment during a hold stays capped … with bins filled in bin label order until the next bin would exceed the cap"; (2) "Every bin at or below its min level at a visit or self-scan is filled to its max level under auto_replenish_to", replaced by "That fill takes the bin from empty toward its fill-to level only as far as the visit allowance below reaches …; every other bin … is still filled to its max level." Both retire genuinely conflicting clauses, name their own scope, restate the base for every other case, and the rule no longer defers to a retired clause. F3 closed. The unretired tail of S3 ("each item is billed at the price pricing_price_basis gives …") is followed on every in-scope line; P6's new substitute tier follows pricing_evt_contract_items ("the Corbett-approved substitute is billed at the discontinued item's contract unit price for discontinued_item_price_protection_days days") — observation O13: P6 counts the days from the substitute line's effective date, the pricing charter "from the discontinuation".

### factor_ladders
| policy | factor | label | reachable tiers | verdict |
|---|---|---|---|---|
| P1 | usage_trend | method: forward projection L+(L−E)/2 / recency-weighted (3L+2M+E)/6 / plain 3m/13 | 3 | honest (F1 closed) |
| P1 | restock_cover | parameter; now counts "scheduled or onsite daily visits" | 3 (Onsite tier reachable) | F2 closed |
| P1 | route_cover, vend_safety, abc_share, payment_exposure | parameter | 3 each | ok |
| P2 | demand_rate (replaces visit_gap) | method: peak month/30 / (peak + 3m mean)/2/30 / 3m/91 | 3 | honest; visit gap now baseline only |
| P2 | backorder_allowance, rush_allowance, route_allowance, supply_allowance | parameter | 3 | ok (F5 closed) |
| P2 | draw_buffer | parameter | 3 | F6 (compute) |
| P3 | trial_level (method), credit_room, supply_check, site_age, return_rate | 1 method / 4 parameter | 3 each | ok; F6 regression on `reorder_point` input |
| P4 | draw_basis | method: largest month / midpoint(largest, 12m mean) / 12m/52 | 3 | honest; F6 (compute) |
| P4 | storeroom_cover, outage_cover, rush_cover, supply_cover, limit_share | parameter | 3 | ok |
| P5 | safety_basis (replaces replenish_gap, lumpy_buffer) | method: (largest − avg billed)×std days/30 / ½·draw·std days / none | 3 | honest (F1/F2 closed) |
| P5 | backorder_lead, delivery_lead, hold_lead, value_class | parameter | 3 | ok |
| P6 | fill_price_basis | method: protected prior price / contract price / list less list discount | 3 (substitute tier reachable on Category, Net-Price, Strategic tiers) | honest; F9 |
| P6 | hold_share, conversion_release, payment_release | parameter | 3 | ok — no longer gated (hold_service removed, scope moved into the rule) — F4 closed |
- No factor reads another factor's binding (mechanical sweep). Assembly sentences generic, order fixed (P5: lead demand plus safety units, then the value share; P6: cap × share, plus every release, less deliveries).
- Counts: P1 1m/5p, P2 1m/5p, P3 1m/4p, P4 1m/5p, P5 1m/4p, P6 1m/3p — all within 4–6 with ≥2 parameter, ≥1 method. Multi-source: P1 restock_cover, P4 storeroom_cover, P5 hold_lead. Cross-difficulty in every computation.
- Realism: new ladders (trend projection, peak sizing for volatile demand, spread-based safety stock, ABC value share on a reorder point, price-protected substitutes, payment-based hold release) are treatments a B2B MRO distributor applies. O6 (conversion_release) and O7 (limit_share on a standing par) stand as observations.

### findings
Round-1 items: **F1 closed** (all 3 members), **F2 closed** (all 3), **F3 closed**, **F4 closed**, **F5 closed** (all 3), **F7 closed** (both tools), **F8 closed**. **F6 open** (class list below). New: **F9**, **F10**.

**F6 — SOURCE-POLICY RED, XF class 9 (absent-record branch stated in the rule, not implemented in compute).** Complete member list:
1. P2 draw_buffer — rule now: "any smaller largest vend, or none at all, adds none"; compute still `K('buffer_large_units') if largest_draw >= K('buffer_large_min') else …` with `largest_draw = XMAX(...)` and no None guard. Reachable: P1 explicitly admits an item with no vends at the demand machine ("an item with none of them has net vends of zero").
2. P4 draw_basis — rule now: "an item with no consumption on record has a weekly draw of zero"; compute tier 1 (`consumed_months <= 4`, true at 0) evaluates `largest_month * K('months_per_year') …` with `largest_month = MAX(...)` unguarded.
3. P3 reorder_point (regression) — rule: "its reorder point is the highest reorder point any of its par level entries carries, and zero where it has none"; compute now `MAX('vmi_bins','min_qty', … par_change, bin_label=new_label)` used raw in `opening_target` (round 1 had `reorder_point if reorder_point != None else 0`).
The charter's own compute treats empty LATEST/XLATEST selections as None (P1 `vend_price != None`, P5 `contract_price != None`, P6 `fill_to != None`); the evaluator's MAX/XMAX semantics are outside this audit's read domain, so the consequence is: on these absent-record worlds the rule gives a definite number while the compute applies `>=`/`*`/`+` to an empty-selection result.

**F9 — SOURCE-POLICY RED, XF class 2 (shared record selection inside a factor).** P6 `line_kind` (latest price line's event type) is a binding of factor `fill_price_basis` but is also read by the plain scope binding `priced_in_scope` ("… and (line_kind != 'pricing_item_removed' or …)"). A record selection several parts share must be a plain binding stated once. Only member (mechanical sweep over all six policies). Present unchanged in revision_1 and missed there.

**F10 — XF class 13 (seeded cross-category rows not priced by their own charter).** Member list (per task, demonstrated in 0.md): task0 order_lines SO-4413870 (2026-03-24) and SO-4414112 (2026-03-30), item 43318, stock_status non_stock_special_order, repriced in r2 to 8.358 = list 9.95 less the safety_ppe category discount 16%. pricing_price_basis takes the non-stock special-order basis before the category basis: "otherwise, for a non-stock special-order item, supplier cost increased by special_order_markup_pct percent; otherwise, list price less the item category's discount" → 4.61 × 1.18 = 5.4398 on the Net-Price tier. (Booked prices are "an estimate" under order_evt_booking_and_shipping; no factor reads the price.) No task1 member.

**Observations:** O1 largely closed (514/518 bins, replenishment priced at contract and billed per visit, hold-period deliveries critical-only within the 3,000.00 cap) — residual: task0's program history starts 2026-09-03 although it went live 2026-03-16 (no visits, spend or monthly-minimum fees for April–August); task1's three deliveries at today's visit VV-446110 are not yet billed. O2, O3, O6, O7, O11 stand; O8, O12 closed; O13 new (above).

### post-reveal closing note (revision_2)
- Both round-2 blind derivations match GT on every write, argument, expected value, baseline_result and factor_sensitivity figure (0.md / 1.md revision_2 comparisons).
- Closed round-1 ids: F1, F2, F3, F4, F5, F7, F8; per-task PT-1, PT-2 (task0) and the task1 "no second reading" proof text.
- Open: F6 (members P2 draw_buffer, P4 draw_basis, P3 reorder_point — rule states the absent-record figure, compute does not implement it; P3 is a regression), F9 (P6 line_kind shared selection inside fill_price_basis, missed in revision_1), F10 (task0 seed: two order lines repriced off the pricing charter's basis order — per-task, not a charter defect).
- Gates were supplied green by the coordinator snapshot and not re-run here; closing checklist not applicable while REDs are open.

VERDICT revision_2: task0=RED[XF13:F10] task1=PASS charter=F6,F9

## revision_3

## charter_global_frozen
- Frozen 2026-10-17 (UTC) before any round-3 GT reveal. Entry input (`/tmp/erl0068_coord/snapshot.sh … 3`, r3/gates.txt): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; worklog tail `REWORK round 3: gates 7/7 green`.
- Hashes: vmi.extended.yaml a838d492143b00c4ee3605b225b81e279698c013b458bcc0463c6662dd84037a (changed); task_tools.py 805a54d8e4d6489c112111bfde69b108660ac9fb9e1109eb6e08425a09346e51 (unchanged since revision_2); r3/task0.view.json fba2d82d…; r3/task1.view.json d488615a….
- Charter changed → its sections re-derived: a full diff against the revision_2 copy (scratch r2/vmi.extended.yaml) confines the change to the bindings and sentences listed below; every other line is byte-identical to the text re-derived in revision_2, and the mechanical sweeps were re-run on the whole r3 file. Tools unchanged → §action_binding_and_uuids carried forward from revision_2 by reference (hash 805a54d8… both rounds).

### policy_conflict_scan / prerequisite_graph / prerequisite_sentences / override_declarations
Carried by content: no policy id, target tool, overwrite, prerequisite edge, policy_source or factor ladder value changed (diff). New rule sentences only add absent-record clauses and one definition ("The item's latest price line is its price line in the customer's agreement with the latest effective date, and its kind is that line's event: an addition, a repricing or a removal."; P6 scope "A customer with no pricing agreement on record is outside this schedule"). No new conflict; revision_2 conclusions stand.

### rule_compute_equivalence
Mechanical sweep on r3: every compute_basis quote verbatim in its rule, every binding quoted, every baseline sentence and policy_source in its rule (0 misses). Each new compute guard has its rule sentence:
- P1, P2, P5 route: `… if CPARAM(...) != None else K('route_unrecorded_per_week')` (7) ↔ "a ship-to whose service level is not on record adds none" (falls into the 3-or-more tier = none).
- P2 `largest_draw … if XCOUNT(...) > 0 else 0` ↔ "any smaller largest vend, or none at all, adds none".
- P3 `reorder_point … if COUNT(par_change) > 0 else 0` ↔ "and zero where it has none"; `fill_to … if new_set_date != None else 0` ↔ "or there is none, no opening stock is set"; `credit_use … receivable != None` ↔ "no account on record, counting as 0.9 or more"; `site_months … if site_opened != None else 0` ↔ "a ship-to with no opening date on record counts as opened today".
- P4 `largest_month … if COUNT(...) > 0 else 0` ↔ "an item with no consumption on record has a weekly draw of zero"; `limit_use` ↔ "or no account on record, counting as 1.0 or more".
- P5 `largest_month` guard (safety tiers already require average > 0).
- P6 price fields `if price_lines > 0 else 0`, CPARAM fields `!= None`, `priced_in_scope` starts `CPARAM('pricing','list_discount_pct') != None` ↔ "no pricing agreement on record is outside this schedule"; `fill_units … if fill_price and fill_to` ↔ "where the bin has no entry, no fill is booked".
Every empty MAX/XMAX/LATEST/CPARAM/CFIELD result that feeds arithmetic or a comparison is now guarded explicitly, so the outcome no longer depends on the evaluator's empty-selection semantics (no DSL evaluator exists under erlbench/, so no probe was possible or needed). Remaining reliance: empty XSUM/SUM/COUNT = 0, the convention the rules themselves state ("an item with none of them has net vends of zero").

### action_binding_and_uuids
Carried forward from revision_2 (tools hash unchanged).

### factor_ladders
Ladders, labels, tier values and counts unchanged from revision_2 (P1 1m/5p, P2 1m/5p, P3 1m/4p, P4 1m/5p, P5 1m/4p, P6 1m/3p). Absent-record values fall on existing fall-through or conservative tiers (unrecorded route → none; no account → tightest credit share; no opening date → youngest site share) — realistic defaults. P6 `fill_price_basis` bindings no longer include `line_kind`; `line_kind` is now a plain binding read by both the factor and `priced_in_scope`, stated once in the rule. Mechanical sweep: no plain binding reads another factor's internal binding; no factor reads another factor.

### XF_recipe re-check (all 13 points, all six policies)
1 factor independence ✓; 2 assembly/shared selection ✓ (F9 closed); 3 order ✓; 4 no "as another policy figures it" ✓; 5 overwrites unchanged and valid ✓; 6 verbatim quotes ✓; 7 rounding ✓; 8 docstrings (tools unchanged, closed in revision_2) ✓; 9 ties and absent-record branches stated and implemented ✓ (F6 closed); 10 every compute filter/guard stated in the rule ✓; 11 method tiers distinct in shape ✓; 12 no cross-record date pairing ✓; 13 seeded cross-category rows — task0 order lines now 5.4398 (F10 closed, 0.md); the added price lines (6 in task0, 64 in task1) do not touch 43318 / 41827 and every delivered line still equals its item's contract line on its date ✓.

### findings
F6 closed (all three members: P2 draw_buffer, P4 draw_basis, P3 reorder_point). F9 closed. F10 closed. No new charter defect. Observations O2, O3, O6, O7, O11, O13 stand.

### post-reveal closing note (revision_3)
- Both round-3 blind derivations equal GT on every write, argument, expected value, baseline_result and sensitivity figure. All round-2 REDs (F6 ×3 members, F9, F10) closed; no regression of F1–F5, F7, F8; no new defect found on the 13 XF points.

## closing_checklist (revision_3)
- Per-task files 0.md and 1.md correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; revisions 1–3 appended, older text untouched; both comparison sections PASS.
- All six extended policies covered; task scopes disjoint (task0: P1–P3 and their tools; task1: P4–P6 and their tools); tools closed, uuid8s independent.
- Each tree: 2 prerequisite problems, ≥1 value_input edge (task0 3, task1 1), one owner=user write, acyclic; difficulty-wide graph acyclic.
- Every computation: self-sufficient baseline with a definite fall-back ≠ gold (19/7/26; 10/4/3), 4–6 factors with ≥2 parameter and 1 honest method, ladders of 3 real tiers stated in their rules, every factor bearing weight on its world; each task has a multi-source factor (restock_cover; storeroom_cover, hold_lead) and cross-difficulty factors with seeded rows.
- Instantiation-stage gates on the final form: supplied green by the coordinator snapshot (r3/gates.txt, 7/7 OK); not re-run by this audit.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen
- Entry input (`snapshot.sh … 4`, r4/gates.txt): 7/7 OK; worklog tail `REWORK round 4: gates 7/7 green`. Hashes: vmi.extended.yaml 057d57f749a8056bbacb7d92069d177080222ad076e4ad5651b3c877bc41611a (changed); task_tools.py 805a54d8… (unchanged → §action_binding_and_uuids carried forward from revision_2); r4 views fba2d82d… / d488615a… (identical to r3 → the worlds are unchanged).
- Additional input: audits/render_source/d4_stocksmart_replenishment_and_program_billing/render_r1.md (renderer source scan of charter a838d492…), read in full; each of its four items treated as a RED class across all six policies.
- Charter diff r3→r4 (scratch copies) reviewed binding by binding and sentence by sentence; mechanical sweeps re-run on the whole r4 file: compute_basis quotes, baseline sentences, policy_sources and overwrite replaced_by all verbatim in their rules; no factor or plain binding reads another factor's internal binding; factor sets and labels unchanged.

### render_r1 items — closure as classes
| item | class | members now (all six policies) | status | covered by my revisions 1–3? |
|---|---|---|---|---|
| 1 | rule wording whose operator scope admits a second reading of the compute ("half of A plus B") | P2 middle demand tier now "its highest month and one third of its net vends of the last three months are added together, the sum is halved, and the result is divided by 30"; P1 projection ("first increased by half of the rise … then multiplied by 12 and divided by 52") and weighted month ("added together and the sum is divided by 6, … then multiplied by 12 and divided by 52"); P4 midpoint ("then multiplied by 12 and divided by 52"); P5 ("worked out in this order …") and safety units ("the difference … multiplied by the standard days and then divided by 30"; "half of the product of the daily draw and the standard days"); P6 allowance ("worked out in this order …"). Remaining operator phrases checked unambiguous: P3 "half the sum of the bin's reorder point and its fill-to level", P6 "half its withdrawn value" / "1 percent of their total", P2/P4 tier-1 single quotients, P5 "the visit gap, 30 days divided by …, plus the tier's replenishment lead business days". | **closed** | **No** — missed in revisions 1–3 (I recomputed by the compute and did not test the prose's operator scope). |
| 2 | selection rule without an "or there is none" branch | P1 "or the customer has none"; P2, P3 "or there is none, no … is set"; P4 "or there is none, no fill-to level is set"; P5 "or there is none" (since r2); P6 "where there is no consignment withdrawal …, where there is no service visit …". | **closed** | **No** — revision_2 checked the added same-date tie clauses but not the empty case. |
| 3 | latest-row selection with an unstated same-date tie | P5 value_class now "zero where it has none, or where two price lines share its latest effective date" (`lines_on_price_date == 1`); P1 vend price now "the highest unit price among its vends at the demand machine dated on its most recent vend date"; P3 new item price "alone on its effective date". All other latest-row selections carry a tie rule (P1/P2/P3 removals, P2/P3 new-bin entries, P4–P6 withdrawals, P5/P6 latest-date bin entries, P6 visits and price lines) or use an any/max/count form. | **closed** | **Partly** — revision_1 O8 listed the P1/P2/P4/P6 ties as observations; P5 contract_price (introduced in r2) was not checked in revisions 2–3. |
| 4 | restriction stated in the rule that the compute does not enforce | Closed members: P3 consigned-value cap (ledger value, `cap_units`, result = min(opening stock, cap units); item without a single in-effect price line → 0); P1 "on any other tier no fill-to level is set" (`consignment_available`); P6 program status active or terminating (`hold_in_scope`). **Open members (F11):** see below. | **open** | **No** — revision_1 treated the cap as a satisfied gate on task0's world; only the analogous E6 gate was noted (O3). |

### findings (revision_4)
**F11 — SOURCE-POLICY RED (render_r1 item-4 class, XF 9/10: rule restriction not enforced by compute).** Complete list of remaining members:
1. P3 `vmi_ext_opening_consignment` — "as one consigned-stocking line at the program's service visit of that day" and "its opening stock is placed at that visit": the compute has no visit binding. On a world with no service visit dated today the rule places nothing (there is no visit of that day), the compute returns the full quantity; with two visits today the rule names no visit, the compute is silent (no tie rule, unlike P6's "two or more carry the latest visit date").
2. P6 `vmi_ext_hold_converted_fill` — "the first customer-owned fill of a bin converted from consignment … is booked under this schedule": the compute does not check for a vmi_replenishment_delivered line already booked into the bin since the conversion entry; a second fill on a later visit is outside the rule but receives a quantity from the compute.
3. P4, P5, P6 — the scope "When Corbett withdraws a slow-moving consigned item from its bin at a par review" / "a bin converted from consignment at a par review": the converted item is taken from the program's most recent vmi_consignment_withdrawn of any cause, while the base charter also withdraws consigned stock "when a consigned bin is removed or the program ends". A bin-removal withdrawal is record-visible (vmi_bins change_type removal for that bin), and a program end is visible on vmi_programs.status; P4 and P5 exclude neither, P6 excludes only the program end (status gate). On a world whose latest withdrawal follows the customer's removal of that consigned bin, the rule says no conversion schedule applies, the compute sets a fill-to level (P4) and a reorder point (P5).
None of the three is reached on task0 or task1 (one visit today in each; no removal row for R-07-02; no prior customer-owned delivery into it).

No other new defect. XF_recipe points 1–13 re-checked on all six policies: 1 ✓, 2 ✓, 3 ✓ (order now explicit in P1, P2, P4, P5, P6), 4 ✓, 5 ✓ (overwrites unchanged), 6 ✓, 7 ✓, 8 ✓ (tools unchanged), 9 ✓ except F11, 10 ✓ except F11, 11 ✓, 12 ✓, 13 ✓ (worlds unchanged since r3). Observation O14: the state-form prerequisite gates E3 ("not placed until … a reorder point above zero") and E6 (consigned) are, like O3, ordering sentences for the agent and are not encoded in compute; the closures' skip-run figures (e.g. "opening stock 8") are the formula's value, not a placement the rule allows — no scored consequence.

### post-reveal closing note (revision_4)
Both round-4 blind derivations equal GT on every write, argument, expected value, baseline value and sensitivity. Tasks PASS on their worlds; the charter carries one open class, F11 (three members).

VERDICT revision_4: task0=PASS task1=PASS charter=F11

## revision_5

## charter_global_frozen
- Entry input (`snapshot.sh … 5`, r5/gates.txt): 7/7 OK; worklog tail `REWORK round 5: gates 7/7 green`. Hashes: vmi.extended.yaml 54a90d486539a12f0366e20b177f07c2605f4e7c465d973a7f9e01939943999d (changed); task_tools.py 805a54d8… (unchanged → §action_binding_and_uuids carried forward from revision_2); r5 views fba2d82d… / d488615a… (unchanged since r3).
- Diff r4→r5 confined to P3, P4, P5, P6 (new bindings visits_today, removal_entries, conversion_withdrawal, customer_owned_entries, earlier_fills; result guards; five new rule sentences). P1 and P2 byte-identical to r4. Sweeps re-run on the whole r5 file: compute_basis, baseline, policy_source and replaced_by all verbatim in their rules; no factor or plain binding reads another factor's internal binding.

### F11 closure (all members)
1. P3 visit of the day — closed: "The opening stock is placed at the program's service visit dated today; where no service visit is dated today, or two or more are, no opening stock is set under this schedule." ↔ `visits_today == 1`.
2. P6 first fill — closed: "The fill is the bin's first customer-owned fill only while no replenishment line of the converted item has been booked on the program; once one has, the bin is outside this schedule." ↔ `earlier_fills == 0`. Observation O15: the test counts lines of the item from any era of the program, so an item that was customer-owned before it was consigned would be excluded from its first post-conversion fill; rule and compute agree literally.
3. P4, P5, P6 conversion cause — closed: "A consignment withdrawal counts as a par-review conversion only where the converted item's bin carries no removal entry and the program is not closed" ↔ `conversion_withdrawal = same_day_withdrawals == 1 and removal_entries == 0 and F('status') != 'closed'` in all three.
F11 closed.

### O14 (unencoded prerequisite states) — re-checked as a class over all six edges
- E1 (P2←P1): encoded (no consigned new-bin entry → no bin → 0). E2 (P3←P1): encoded (no new-bin entry → 0). E3 (P3←P2): now encoded (`reorder_point > 0`). E6 (P6←P5): now encoded (`customer_owned_entries > 0`). O3/O14 closed for these.
- **Remaining members — F12, SOURCE-POLICY RED (render_r1 item-4 class: a restriction the rule states that the compute does not enforce):**
  1. P5 `vmi_ext_conversion_reorder_point`, E4 — rule: "Corbett's conversion entry for such a bin is recorded only after the customer's written request setting the bin's customer-owned fill-to level stands in its bin history." Compute `result: int(-(-RND(raw_reorder, 6) // 1)) if conversion_withdrawal else 0` does not test for that entry. Demonstration (task1 world, skip P4): rule — no conversion entry is recorded; compute — 7 (GT closure: "min_qty 7 instead of 8").
  2. P6 `vmi_ext_hold_converted_fill`, E5 — rule: "That fill is not booked until the bin's entries carry the customer-owned fill-to level set by the customer's written request for it." Compute tests only `critical_entries > 0` and `customer_owned_entries > 0` on the latest date. On a charter-producible world where the consigned bin was already flagged critical at the customer's earlier request (base vmi_bins_and_par allows critical flags on any bin), the conversion entry alone carries critical=true and consigned=false, so the compute fills against the allowance at the old consigned fill-to level while the rule says not until the customer's request sets a customer-owned fill-to level. (Not reached on task1: no consigned bin is critical in the seed.)
  Coverage note: revision_4 listed only E3 and E6 under O14 (as observations) and missed E4 and E5; since the reworker treated the class as a work item and its siblings E3/E6 are now encoded, E4/E5 are recorded as the class's remaining RED members.

### Renderer-class sweeps (XF 1, 2, 3, 9, 10, 12) on all six policies
- XF 1 factor independence: ✓ (mechanical; new bindings are plain).
- XF 2 assembly / shared selections: ✓ (`removal_entries`, `conversion_withdrawal`, `visits_today`, `customer_owned_entries`, `earlier_fills` are plain bindings stated once in their rules; no factor gated through another).
- XF 3 order: ✓ (P1, P2, P4, P5, P6 order sentences explicit since r4; new guards are conjunctions, order-free).
- XF 9 edges: ties ✓ (new: "two or more are" for today's visits); absent records ✓ (empty counts give the stated outcome; `reorder_point` is 0 when absent, so `> 0` is defined); month-end/negative-lag/zero-division unchanged ✓.
- XF 10 rule ↔ compute filters: every compute filter is stated in its rule ✓; rule restrictions not enforced in compute: **F12** (two members above); all other rule-stated scopes, caps, tier, status, visit, first-fill and conversion-cause restrictions are enforced.
- XF 12 cross-record date pairing: ✓ (none; the conversion-cause test counts removal entries instead of pairing dates).
- Other XF points (4, 5, 6, 7, 8, 11, 13) unchanged and ✓.

### post-reveal closing note (revision_5)
Both round-5 blind derivations equal GT (26/19/13; 19/8/8; baselines and sensitivities identical). F11 closed; F12 open (two members, no consequence on either scored path).

VERDICT revision_5: task0=PASS task1=PASS charter=F12

## revision_6

## charter_global_frozen
- Entry input (`snapshot.sh … 6`, r6/gates.txt): 7/7 OK; worklog tail `REWORK round 6: gates 7/7 green`. Hashes: vmi.extended.yaml bcd5299a5db63fe12cc95144e23d291584e0541ee52c778740f95f263db32933 (changed); task_tools.py 805a54d8… (unchanged → §action_binding_and_uuids carried forward from revision_2); r6 views fba2d82d… / d488615a… (unchanged since r3).
- Diff r5→r6: P1–P4 byte-identical (their revision_5 conclusions carried forward by reference). P5: new plain binding `request_entries`, result gated on it, E4 sentence reworded, `entry_date` moved out of hold_lead's bindings into a plain binding (now shared by `request_entries` and hold_lead — correct per XF 2). P6: new `request_entries`, result gated on it, E5 sentence reworded. Sweeps on the whole r6 file: all quotes, baseline sentences and policy_sources verbatim; no factor or plain binding reads another factor's internal binding.

### F12 closure check
1. P5 E4 — **closed.** Rule: "Corbett's conversion entry for such a bin is recorded only after the bin's entries of their latest date include the customer's written request, a par level entry still flagged consigned that names no reorder point and sets the customer-owned fill-to level." ↔ `request_entries = COUNT(vmi_bin_set, par_change, sku, consigned=True, min_qty=0, event_date=entry_date)`, `result … if conversion_withdrawal and request_entries > 0`. The request is now identified by record-visible features (also retires O2 for E4).
2. P6 E5 — **encoded but with a filter missing from the rule (new F13).** Rule: "That fill is not booked until the bin's entries of their latest date include the customer's written request for it, the par level entry naming no reorder point that sets its customer-owned fill-to level." Compute: the same `request_entries` filter including `consigned=True`, which the P6 rule does not state (P5's sentence does: "still flagged consigned"). The pre-flagged-critical bypass described in revision_5 is closed (a conversion entry carries a reorder point and is consigned=false, so it is not counted).

**F13 — SOURCE-POLICY RED, XF class 10 (compute filter not stated in the rule).** Only member: P6 `request_entries` `consigned=True`. Demonstration on a charter-producible world: day D — customer request (consigned, min 0), Corbett conversion (consigned=false); day D+1, before any fill, the customer files a revised request with submit_critical_bin_request_f65e9169 (its docstring: consigned "false when it already shows it customer-owned") → the latest-date entries are one par entry, consigned=false, min 0, carrying a customer-owned fill-to. P6 rule: the latest-date entries include a par level entry naming no reorder point that sets the customer-owned fill-to level, and they show the bin no longer consigned → the fill is booked. Compute: `request_entries` = 0 → 0. Not reached on task1 (one request, on the conversion day). Coverage: new in r6 (introduced by this rework).

### Six-edge re-check
E1 (P2←P1) encoded via the new-bin selection; E2 (P3←P1) via the new-bin selection; E3 (P3←P2) `reorder_point > 0`; E4 (P5←P4) `request_entries > 0`; E5 (P6←P4) `request_entries > 0` (F13 on its wording); E6 (P6←P5) `customer_owned_entries > 0`. Each edge's sentence verbatim in its rule; kinds/gates exist (E4 gate `request_entries`, E5 gate `vmi_bins.min_qty`); graph acyclic.

### Renderer-class sweeps (XF 1, 2, 3, 9, 10, 12), all six policies
1 ✓; 2 ✓ (`entry_date` plain and stated once; `request_entries` plain); 3 ✓; 9 ✓ (counts handle ties and absence); 10 — **F13** (one member), otherwise every compute filter is stated in its rule and every rule restriction is enforced; 12 ✓. Points 4–8, 11, 13 unchanged ✓.

### post-reveal closing note (revision_6)
Both blind derivations equal GT (26/19/13; 19/8/8). F12 closed; F13 open (one member).

VERDICT revision_6: task0=PASS task1=PASS charter=F13

## revision_7

## charter_global_frozen
- Entry input (`snapshot.sh … 7`, r7/gates.txt): 7/7 OK; worklog tail `REWORK round 7: gates 7/7 green`. Hashes: vmi.extended.yaml aa920acbff680c34f108212e9d291aabb5f5dd81db3e1bb551dc51f39a97483b (changed); task_tools.py 805a54d8… (unchanged → §action_binding_and_uuids carried forward from revision_2); r7 views fba2d82d… / d488615a… (unchanged since r3).
- Diff r6→r7: P1–P4 byte-identical (revision_6 conclusions carried forward). P5 and P6: `request_entries` no longer filters `consigned=True`; E4 and E5 sentences now "a par level entry that names no reorder point and sets the customer-owned fill-to level"; P6's E6 sentence now "That fill is booked only after the bin's entries of their latest date include one showing it no longer consigned." Sweeps on the whole r7 file: every compute_basis quote, baseline sentence and policy_source verbatim in its rule; no factor or plain binding reads another factor's internal binding.

### F13 closure check
Closed. P5 and P6 rules and compute now agree: request = latest-date par_change entry with min_qty 0 (`COUNT(vmi_bin_set, par_change, sku, min_qty=0, event_date=entry_date)`), with no consigned filter on either side. The revision_6 counter-world (a revised customer request on D+1, consigned=false, min 0) now gives: rule — request present on the latest date and that date's entries include one showing the bin no longer consigned → fill booked; compute — `request_entries` 1, `customer_owned_entries` 1 → fill booked. E6's sentence now states the latest-date scope that `customer_owned_entries` already applied (an XF 10 alignment beyond F13). No new false positive found: Corbett's own entries on a converted bin carry a computed reorder point (P5), and the only Corbett min-0 entries (P2 on new consigned bins of vended items) are dated at bin creation, not on a conversion date.

### Renderer-class sweeps (XF 1, 2, 3, 9, 10, 12), all six policies
1 ✓; 2 ✓ (`request_entries`, `entry_date`, `customer_owned_entries` plain, each stated once); 3 ✓; 9 ✓ (count tests handle ties and absence); 10 ✓ — every compute filter is stated in its rule and every rule restriction is enforced (re-checked bindings: P1 consignment tier, removal tie/none; P2 new-bin and removal tie/none; P3 cap, today's visit, reorder point > 0, single in-effect price line; P4/P5/P6 conversion cause; P5 request; P6 status, hold scope, request, latest-date not-consigned entry, first fill, price scope, visit tie); 12 ✓. Points 4–8, 11, 13 unchanged ✓.

### Observations (revision_7)
- O16: E4's `condition` says the request may be written "whether written before or after the conversion entry" — wording copied from E5; for E4 the conversion entry is the write being gated, so "after" cannot occur. The rule sentence (what is rendered) is correct; no consequence.
- O17: E6's `condition` ("carries a vmi_bin_set par_change entry with consigned = false") does not repeat the sentence's "of their latest date"; with this charter's tools no reachable world separates the two.
- O15, O6, O7, O11, O13 stand.

### post-reveal closing note (revision_7)
Both blind derivations equal GT (26/19/13; 19/8/8; baselines and sensitivities identical). F13 closed; no open charter RED; tasks PASS on all four relationships.

## closing_checklist (revision_7)
- Task files 0.md / 1.md map one-to-one to tasks 0 and 1; revisions 1–7 appended, older text untouched; both latest comparisons PASS.
- Six extended policies covered; scopes disjoint (task0 P1–P3, task1 P4–P6); tools closed, uuid8s independent (tools unchanged since revision_2).
- Each tree: 2 prerequisite problems, value_input edges ≥ 1 (task0 3, task1 1), one owner=user write, acyclic; all six edges stated in their blocked rules and enforced in compute.
- Every computation: self-sufficient baseline with a definite fall-back ≠ gold (19/7/26; 10/4/3), 4–6 factors (≥2 parameter, 1 honest method), real three-tier ladders stated in the rule, every factor bearing weight; multi-source and cross-difficulty factors with seeded rows in both tasks.
- Instantiation-stage gates on the final form: 7/7 OK per the coordinator snapshot (r7/gates.txt); not re-run by this audit.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen
- Entry input (`snapshot.sh … 8`, r8/gates.txt): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; worklog tail `REWORK round 8: gates 8/8 green`. Hashes: vmi.extended.yaml aa920acbff680c34f108212e9d291aabb5f5dd81db3e1bb551dc51f39a97483b and task_tools.py 805a54d8e4d6489c112111bfde69b108660ac9fb9e1109eb6e08425a09346e51 — both unchanged since revision_7, so every charter-global section is carried forward by reference from revision_7. r8 views 643f30bd… (task0) / d5d0dbca… (task1) changed (seed-only rework).
- Additional input read after both task freezes: audits/policy_kb/d4_stocksmart_replenishment_and_program_billing/_verdict.md revision_3 (S1–S5, N1–N4); docs/vending restock documents and blueprint products for the owning rules.

### Seed-only rework check (both tasks; details in 0.md / 1.md revision_8)
- S2, S3, S4, S5 closed; N1, N2, N3, N4 filled; S1 (1200-month bound) remains a coordinator-decided note, not routed.
- Every new or changed row checked against its owning product's rules; none lights a call-day obligation the tasks do not carry; personas unchanged; both problem trees and every factor still bear weight with unchanged tiers (re-derived from scratch on the r8 views).
- Renderer-class XF points unaffected (charter unchanged); XF 13 re-checked on the new rows ✓.
- Observations: O18 (restock rows untimed; 2026-08-27 order-dependent), O1 residual unchanged.

### post-reveal closing note (revision_8)
Both blind derivations equal GT (26/19/13; 19/8/8). No open RED.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen
- Entry input (`snapshot.sh … 9`, r9/gates.txt): all seven gate lines OK; worklog tail `REWORK round 9: gates 8/8 green`. Hashes: vmi.extended.yaml aa920acbff680c34f108212e9d291aabb5f5dd81db3e1bb551dc51f39a97483b and task_tools.py 805a54d8e4d6489c112111bfde69b108660ac9fb9e1109eb6e08425a09346e51 unchanged → charter-global sections carried forward from revision_7. r9 views 945463cb… / 52746175… (seed-only change).

### Seed-only rework check (S6)
- Changed rows (both tasks): next-day-air bookings now backorder and fill by the ship-to's standard method, with invoices and payments re-dated to the fills. Producible under order_evt_booking_and_shipping, order_evt_backorder and order_evt_freight_and_fees (free standard freight on both ship-to levels; no expedite fee on a non-expedited fill) and pricing_price_basis; credit ledgers reconcile to ar_balance.
- Factor windows re-derived on the r9 views: task0 P2/P3 backorder tiers become 3 opened / 3 filled in three months — same tier ("as many or more"); task1 P4 supply cover (backordered within six months) and P5 backorder lead (1 opened / 0 filled in three months) unchanged; next-day-air bookings unchanged; payment windows unchanged. Scored values unchanged (26/19/13; 19/8/8), every factor still bears weight, trees unchanged.
- No new obligation due on either call day.

### post-reveal closing note (revision_9)
Both blind derivations equal GT. No open RED.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
