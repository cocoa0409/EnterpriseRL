# Policy-task audit — window_contract_deposits_and_cancellations / charter-global

## charter_global_frozen
- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), revision 1.
- Freeze time: 2026-10-13 (written before any task's GT was revealed; nothing here derives from a revealed GT).
- Frozen artifact hashes (re-verified with sha256sum at audit start, equal to the coordinator's):
  - `8bfbf3d20cf7108b18507e11b7dea25cd114a0b8db4565e7bdc15b4514aed990  window.extended.yaml`
  - `67f9431450158a8c6610b2a68a2da82318372ad931b52d0a08bc3ae5ebaf5f1e  task_tools.py`
  - masked views `0.view.json` 33fb1d1a…002a and `1.view.json` 85d971de…8b74 (equal to the brief).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures), `blueprint/products/window.yaml` (diffed against the base copy), enum lines of `door.yaml`/`finance.yaml`/`install.yaml`/`warranty.yaml`/`order.yaml`, `window.extended.yaml`, `task_tools.py`, and the DSL semantics (`build_env` in `skills/erl-task-instantiate/scripts/check_compute.py`: CFIELD/CPARAM return the first matching holding of the customer; XSUM/XCOUNT are customer-scoped; MONTHS counts whole months; RND is Python `round(float(x), 2)`).
- Masked and unread at the time of writing: every `tasks/*.json` field other than the coordinator's views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure); the instantiator's worklog and /tmp scratch; the sibling difficulty audit directory.
- Entry conditions (Step 0): gate snapshot supplied (EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; TRACEABILITY deferred for unlock tool-name provenance pending KB render; validate_scenario only missing-document errors); masked views supplied with hashes; frozen hashes match. Inputs complete.

### policy_conflict_scan
- Base copy: lines 1–1522 of `window.extended.yaml` are byte-identical to `blueprint/products/window.yaml` (diff shows only the trailing blank line; a key-by-key YAML comparison gives all ten base keys equal). No base rewrite.
- Six extended policies, two disjoint prerequisite components:
  - A = {`window_ext_final_balance_payoff` (root, `pay_final_balance_39e93918`, owner=user) ← `window_ext_late_balance_charge`, `window_ext_change_order_fee`, `window_ext_remeasure_fee` (all agent)}.
  - B = {`window_ext_deposit_balance` (root, `pay_deposit_balance_19bfa79b`, owner=user) ← `window_ext_door_bundle_credit` (agent)}.
- Overlapping subjects: the three fee policies all write `window_fee_assessed` but on distinct `fee_kind`s (remeasure_fee / change_order_fee / late_balance_charge) through distinct tools; the two payment roots write `window_payment_received` with distinct `payment_kind` (final_balance vs booking_deposit) and disjoint status domains (installed vs not yet released). No two policies decide the same quantity in the same situation.
- Triggers/time anchors: remeasure fee dated the remeasure date, change-order fee dated the change-order date, late charge and both payments dated today, door credit dated today — consistent with base dating except where declared (see override_declarations).
- Cross-category read boundaries: reads only (finance, door, install, order, warranty); no extended policy writes another category.
- Interaction between component-A policies: the late-charge balance excludes fees ("fees, earlier late balance charges included, ... bear no late charge"), so the late charge does not read the remeasure/change-order fee writes; the change-order fee and remeasure fee read no fee rows; the three prerequisites of the payoff are mutually independent (no shared balance/cap/dedup key). The payoff reads all three through `fees_on_contract`.
- Interaction in component B: the door credit reads no window ledger row; the deposit reads it through `price_credits`.
- Scope exclusivity/completeness of the M=2 claims cannot be checked against `charter_scope` before the reveal; pre-reveal expectation from the graph: one task per component, jointly covering all six policies. Settled in `closing_checklist`.

### rule_compute_equivalence
Mechanical sweep (`/tmp/audit_d1_0060/mech.py`): every `compute_basis` quotation is a verbatim substring of its policy's `rule`; every `replaced_by` is verbatim in the rule; every `superseded_clause` is verbatim in the cited base rule; every `baseline.rule` sentence is in the rule; every factor's `decides` is a compute binding. Manual back-sweep per policy:
- `window_ext_remeasure_fee`: coverage ladder (≤2 → min(remeasure fee, missed fee); >2 and 2·n < contract openings → prorated; else flat), timing share (>10 d → 1.25; ≤3 d → 0.75; else 1), repeat share (≥3 → 1.5; =2 → 1.25; else 1), oversize share (≥3 → 1.25; ≥1 → 1.1; else 1), single end rounding — each implemented and each compute branch stated. Compute's `F('measure_date')` is the contract's final-measure date ("the final measure date") — equivalent. PASS.
- `window_ext_change_order_fee`: all six ladders stated and implemented. **Gap (finding G4)**: the rule's object is "the most recent customer change order on the contract, that is every change-order line written on the latest date that carries change-order lines"; base `window_oversize_pricing` says the oversize line "is not a customer change order", and base measure `window_msr_change_orders` excludes `oversize_surcharge`. Compute's `last_change_date`, `change_lines`, `openings_priced` filter only `event_type='window_change_order'` and so include `oversize_surcharge` lines. The two clauses of the rule sentence ("customer change order" vs "every change-order line") disagree whenever an oversize line sits on or after the latest customer change-order date. Consequence is world-dependent; demonstrated (or not) in the task file. `lender_paperwork_share`: rule tier 3 is "a contract paid by cash, check or card"; compute also returns 1.0 for a financing contract with no finance account on it — a case the rule does not state (observation G6).
- `window_ext_late_balance_charge`: clock anchor, grace, goodwill, late rate, standing, catch-up, period rounding then minimum then × periods — all stated and implemented. `factory_ship_slip_days` uses `DAYS(committed_ship_date, ship_date)`, which raises if the order has no ship date (world-dependent; checked per task). PASS structurally.
- `window_ext_final_balance_payoff`: balance due, job net charges, four holds, cap at job net charges, single end rounding — stated and implemented. The warranty hold reads all of the customer's warranty visits (rule: "on the household's registrations") — consistent. PASS.
- `window_ext_door_bundle_credit`: starting rate by signing order, door-price step, owner step, timing, promo, commitment shares, sum-then-shares-then-price, end rounding — implemented. Rule "warranty registration in force from an earlier Ridgeline installation": compute `CFIELD('warranty','coverage_start_date', status='active')` takes the first active registration and does not test "from an earlier installation" (observation G9; bites only if the household holds several active registrations or one not from an earlier install — checked per task). "the door contract": compute takes the customer's first door holding (checked per task).
- `window_ext_deposit_balance`: measured value, size step, three-tier method, upfront shares, payments net of refunds, floor at zero, rounding — implemented; `F('payment_method') == 'cash_check_card'` matches the schema enum. PASS.

### action_binding_and_uuids
- `(target_tool, computes)`: six distinct tools, each claimed by exactly one policy (`amount` each). No base policy targets them.
- uuid8 tails: 39e93918, 0f8afea0, bcbd2cec, bdabfe19, 19bfa79b, ed16c33c — pairwise unrelated, no shared prefix, no sequence, no reuse of a share-tool tail. PASS.
- Docstrings: no concrete example value; no other tool named; no sequence position stated. Descriptive state clauses ("once the windows are installed", "that has not yet been released to the factory", "whose remaining balance is overdue") describe the object, not an order among actions — observation only. No docstring claims an effect the body lacks (each body creates exactly the one `window_transactions` row described, with the stated kind/date).
- Tool bodies judge nothing: none reads status, balances, prior fees or any prerequisite state; none refuses, errors or hints (only `ctx.find` to copy `customer_id`). PASS.
- Factor ids vs tool names: no factor id is a substring of any task tool or share tool name (mechanical check). PASS.
- Rounding wording: tool docstrings say amounts are "rounded half up to the cent"; the rules say "rounded to the cent"; compute RND is Python `round` (binary float, ties-to-even on exact representations). Divergence can bite only at an exact half-cent pre-round value (observation G7; checked per task).

### prerequisite_graph
- `prerequisite` filled on all six (`[]` on the four leaves). Edges: payoff → late charge / change-order fee / remeasure fee; deposit → door credit. All `problem`s are extended ids of this file, none base, none self; graph acyclic (depth 1).
- Every `policy_source` verbatim in the blocked policy's own rule (mechanical). `form: state` on all four; no `fallback_reason` (none needed).
- `resolved_by` = the depended-on policy's `target_tool` on all four. `kind: value_input` with `gate` `fees_on_contract` (payoff) / `measured_value` (deposit) — both real compute bindings, and the resolving write genuinely moves them (a new fee row raises `fees_on_contract`; a new credit row raises `price_credits` and lowers `measured_value`).
- `condition` vs sentence: payoff edges — same strength and scope. Deposit edge — the `condition` adds "and not cancelled, when the contract's discount program is none", which the sentence does not carry (finding G2).
- No authoring-viewpoint phrasing in any `prerequisite` field.

### prerequisite_sentences
- Payoff ← late charge: "The payoff amount is fixed only after the contract's ledger carries a late balance charge for every full late period that has ended under the late-charge terms." Connective "only after"; state "ledger carries a late balance charge for every full late period that has ended" (record-visible: `window_transactions` fee_kind late_balance_charge vs periods by the late-charge rule); no tool/id/snake_case. Exactly one write brings it about: `window_ext_late_balance_charge` (the only policy booking a late balance charge). Derivation: sentence → count ended periods under the late-charge terms → compare with booked late charges → the late-charge rule books "every full period that has ended without a late balance charge ... in one entry". Single reading. PASS.
- Payoff ← change-order fee: "The payoff amount is not quoted until the ledger carries a change-order fee for every customer change order written beyond the series free count." "not … until"; state form; one write (`window_ext_change_order_fee`). The depended-on rule figures a fee only "for the most recent customer change order"; if more than one change order beyond the free count lacked a fee, the charter states no amount for the earlier ones (finding G5, world-dependent).
- Payoff ← remeasure fee: "Before the payoff amount is worked out, the ledger must carry a remeasure fee for every customer-requested remeasure beyond the series free remeasure count." "Before"; state form; one write. Same "most recent only" caveat (G5).
- Deposit ← door credit: "The deposit balance is not worked out until the ledger carries a door bundle discount credit for every Ridgeline door contract signed within the bundle window of this contract." "not … until"; state form; one write (`window_ext_door_bundle_credit`). Broader than its condition (G2).
- No rule restates another's sentence; no second wording; no other problem's id or tool in any rule; depended-on rules are silent about the payoff/deposit. No base rule sentence is used to ground an edge (base "In the natural course" ordering lives in blueprint prose only, not in a charter rule). No undeclared cross-problem order found in any extended rule.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry; criterion: the scored quantity.
- remeasure fee vs `window_measure_visits`: "carries the series remeasure fee after that" — declared (replaced_by keeps free count, company remeasure free/uncounted). Missed-appointment sentences untouched (quick-check tier reads the missed fee as a value only). vs `window_change_orders`, `window_series_change`, `window_standard_cancellation`, `window_final_balance`, `window_oversize_pricing`: followed; no sentence governs the remeasure fee amount. PASS.
- change-order fee vs `window_change_orders`: "each later change order carries the series change-order fee once, on the date it is written" — declared, keeps once/dated/free count. Other sentences (status, max count, pricing of lines) followed. Others refs: no conflict. PASS (subject to G4's object definition, which is a rule/compute matter).
- late charge vs `window_final_balance`: the late-charge sentence (rate × unpaid balance per full 30-day period after the due date, minimum, assessed at period end) — declared: new balance base excluding fees, start date shifted by grace/goodwill, catch-up in one entry dated today; keeps the due date and "no charge before it". "A late balance charge applies only while the contract status is installed" — inherited. PASS.
- payoff vs `window_final_balance`: "The net charges of the contract's installation job are collected with it…" — declared (holds subtracted, held charges stay owed). Balance-due sentence restated equivalently (contract price + change orders + fees − credits − net payments = price + net charges − paid). vs `window_agg_payment_application`, `window_booking_deposit`: followed. PASS.
- door credit vs `window_price_credits`: "A door_bundle_discount credit equals the series bundle percentage of the signed contract price" — declared; window/once-per-pair/program-none kept. vs `window_discount_programs`: followed. PASS.
- deposit vs `window_booking_deposit`: cash sentence and financed sentence — both declared (two overwrites). The second `replaced_by` is a bare fragment that names no scope of its own ("a contract paid by Ridgeline financing requires …"); the first `replaced_by` scope ("For the required booking deposit of a contract not yet released … and only for it") already covers both, and the two agree on the financed case — no second answer arises (observation G8). Rounding, window, measure booking, card limit, booking/progress recording inherited. vs other refs: followed. PASS.
- No anonymous intermediate, 0/1 multiplier, or dropped branch found. No author note calls base output wrong.

### factor_ladders
Counts (declared): remeasure 4 (1 method, 3 parameter); change-order 6 (1 m, 5 p); late charge 6 (1 m, 5 p); payoff 4 (1 m, 3 p); door credit 6 (1 m, 5 p); deposit 4 (1 m, 3 p). All ladders three tiers, pairwise disjoint as stated, every tier in the rule and in compute, `decides` an input not `result`, binding sets disjoint within each policy, fall-through = factor baseline everywhere.

Tier outcomes distinct in every ladder (values listed: remeasure timing 1.25/0.75/1; repeat 1.5/1.25/1; oversize 1.25/1.1/1; change timing 0.5/1.5/1; special-order 1.5/1.25/1; size 1.25/0.75/1; lender 1.5/1.25/1; returning 0.5/0.75/1; grace 10/5/0; goodwill 14/7/0; late rate 0.02/0.0125/0.015; standing 0.6/0.8/1; catch-up 0.5/0.75/1; inspection 200/100/0; warranty 400/200/0; lead-safe 200/100/0; door step 0.02/0.01/0; owner step 0.01/0.005/0; bundle timing 0.75/0.9/1; promo 0.5/0.75/1; commitment 0.5/0.75/1; deposit step 0.10/0.05/0; special upfront 1.0/0.5/0; oversize upfront 1.0/0.5/0). `bundle_rate_source` tiers give the same number whenever the door series' window-bundle rate equals the window series bundle percentage (world-dependent).

Method labels — honest?
- `remeasure_opening_coverage`: min of two fees / prorated by opening ratio / flat — prorating changes arithmetic form. Honest.
- `change_scope_method`: per-opening × count with a floor / fee + per-extra-line / flat. Honest.
- `punch_retainage`: hold all job net charges / count × per-item / nothing. Honest.
- `deposit_method`: financed % with no floor / % plus upfront shares of uncovered special lines capped / max(% , minimum) capped. Honest.
- `late_clock_anchor` (**finding G1a**): tiers "runs from the lender funding date" / "from the date the installation job closed" / "from the installation completion date". Each tier substitutes a different date into the identical expression `DAYS(late_clock_start, NOW) − due − grace − goodwill`, then `// 30`; the late-charge algorithm is unchanged. This is a value (a date) chosen by tier — a `parameter` effect under a `method` label.
- `bundle_rate_source` (**finding G1b**): tiers "door series rate" / "higher of window and door rates" / "window series rate". Each tier yields a rate substituted into the identical expression `(start + steps) × shares × price`; it is "a different number into the same formula (a rate)". The max() of tier 2 still yields a rate fed into the unchanged formula.
- With those two relabelled, `window_ext_late_balance_charge` and `window_ext_door_bundle_credit` each carry 0 `method` factors (floor 1).

Multi-source factors (every non-fall-through tier a conjunction/disjunction over distinct records): `company_delay_goodwill` (install reschedule rows ∧/∨ factory order dates), `account_standing_share` (finance txns of several accounts ∧ account on contract), `lead_safe_verification_hold` (job status ∧ lead-safe fee rows), `lender_paperwork_share` (window payment_method ∧ finance plan), `promo_financing_share` (window plan ∨ door plan), `change_timing_share` tier 1 (change row date vs contract measure date ∨ no measure). Component A and component B each contain at least one.

Cross-difficulty factors and categories: change-order fee — finance, door; late charge — finance (clock, grace, standing), install (goodwill; also reads order); payoff — install (punch, inspection, lead-safe), warranty; door credit — door (rate source, door step, commitment), warranty, finance; remeasure fee and deposit — none. Each component has several.

Realism of conditions and outcomes (window-replacement practice):
- Remeasure: quick-check pricing, proration by openings, surcharges for late/repeat remeasures and oversize review — plausible company schedules. `repeat_remeasure_share` (**observation G3**): the fee applies only beyond the series free remeasure count; for series with free count 2 (5500, 6600) every remeasure reaching this write is the third or later, so tier 1 holds of every customer who reaches the write and the ladder does not divide them; for free count 1 (2200–4400) the fall-through ("a single one") is unreachable. RED only for a task on a 5500/6600 contract.
- Change-order fee: pre-measure discount, late-change surcharge, factory-paint/specialty-glass surcharges, size bands, lender amendment paperwork, loyalty reductions — all real in the trade.
- Late charge: clock from funding/closeout, grace for financed accounts, goodwill for company delays, repeat/partial-payer rates, clean-history reduction, catch-up reduction — published-schedule plausible.
- Payoff: punch retainage, inspection and lead-safe clearance holds — standard contractor practice; warranty-repair hold reads warranty visits on any of the household's registrations, which is a real practice when the pending repair is on the same project and weaker when it is on an unrelated older registration (checked per task).
- Door credit: rate published by the door series when the door led, project-size step, returning-owner step, add-on timing, promo-financing dealer-fee reduction, commitment by door stage — plausible.
- Deposit: deposit true-up on measured value, lower % for large projects, special-order and oversize upfront — standard.

### findings
- **G1 — SOURCE-FACTOR RED (mislabelled effect), bears on the task claiming `window_ext_late_balance_charge` (component A) and the task claiming `window_ext_door_bundle_credit` (component B).** Symptom: `late_clock_anchor` and `bundle_rate_source` are labelled `method` but every tier only selects a value (a date / a rate) substituted into an unchanged formula. Root cause: factor declarations `window.extended.yaml` lines 1950–1964 and 2336–2350. Evidence: compute lines 1896/1902–1903 (`late_clock_start` feeds `DAYS(late_clock_start, NOW) - …`, same expression for all tiers) and 2306/2318 (`starting_bundle_rate` feeds `(starting_bundle_rate + door_project_step + returning_owner_step) * … * F('contract_price')`, same expression for all tiers). Demonstrated consequence: each of the two computations has zero honest `method` factors against the floor of 1 per computation. Affected: factors blocks of both policies.
- **G2 — SOURCE-POLICY RED (prerequisite sentence broader than its condition), bears on the component-B task.** Sentence (rule line 2463): "The deposit balance is not worked out until the ledger carries a door bundle discount credit for every Ridgeline door contract signed within the bundle window of this contract." Condition (line 2478) restricts to door contracts "not cancelled, when the contract's discount program is none". Base `window_price_credits`: "The door bundle discount is granted only when the contract's discount program is none." and "…neither contract is cancelled". Same situation, two conclusions: a window contract with discount_program `military` and a door contract signed 10 days later — the deposit rule says the deposit balance waits for a credit; the credit rule forbids it; the deposit has no solution under the sentence as written, while under the condition the edge simply does not apply. Whether the task's world exercises it is shown in the task file.
- **G3 — observation (ladder condition series-dependent)**: see factor_ladders; RED only on a 5500/6600 remeasure task.
- **G4 — rule/compute object of the change-order fee includes oversize lines**: see rule_compute_equivalence; consequence world-dependent, demonstrated or cleared in the component-A task file.
- **G5 — "most recent only" vs "every … beyond the free count"**: the change-order and remeasure fee rules figure one item; the payoff sentences require every item. World-dependent (cleared or demonstrated per task).
- **G6 — observation**: lender paperwork share for a financing contract with no finance account is stated by no tier.
- **G7 — observation**: tool docstrings say "rounded half up"; RND is Python round; checked per task for exact half-cent values.
- **G8 — observation**: second deposit `replaced_by` names no scope of its own; no second answer results.
- **G9 — observation**: returning-owner step's "from an earlier Ridgeline installation" and "the door contract" are not narrowed in compute (first active registration / first door holding); checked per task.

## closing_checklist
Written after both reveals (below the pre-reveal section, which was not edited). The difficulty is **not closed**: not every task passes all four relationships.
- Audit files: `0.md`, `1.md` one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; revision 1 (no prior revision in this directory).
- Coverage and scope exclusivity: task 0 `charter_scope` = {late balance charge, change-order fee, remeasure fee, final balance payoff} (+ their four tools); task 1 = {door bundle credit, deposit balance} (+ two tools). Pairwise disjoint over whole trees; union = all six extended policies and all six task tools. PASS.
- uuid8s independent and frozen (see action_binding_and_uuids). PASS.
- Trees: task 0 — 3 prerequisites, 3 value_input, user-owned root, acyclic; task 1 — 1 prerequisite, 1 value_input, user-owned root, acyclic; difficulty graph acyclic with no cross-task edge. PASS structurally; task 0 carries a proof-text RED (`0.md` T0-2).
- Factors: every factor bears weight on its task's world and every all-baseline fall-back is definite and differs from gold (105.62/85.00/135.00/4811.52; 451.36/1148.95). **Open: G1** — the late-charge (task 0) and door-credit (task 1) computations have no honest `method` factor (`0.md` T0-1, `1.md` T1-1).
- Policy self-consistency: **Open: G2** (deposit prerequisite sentence broader than its condition; `1.md` T1-2). G4/G5 world-dependent and not exercised by either task.
- Unique solution: both tasks PASS (blind derivation equals GT on every write, argument, owner and terminal row).
- Instantiation-stage gates: not re-run by this auditor (the brief supplies the snapshot and assigns gate runs to the coordinator); the snapshot's deferred TRACEABILITY gate remains for step 3.

Per-task verdicts:
- task 0: SOURCE-FACTOR RED (T0-1 / G1a), SOURCE-CHAIN RED (T0-2, proof text only).
- task 1: SOURCE-FACTOR RED (T1-1 / G1b), SOURCE-POLICY RED at charter level (T1-2 / G2, no consequence on this world).

## revision_2

### charter_global_frozen (revision 2)
- Re-audit requested by the coordinator (round 2). Written 2026-10-13 before any round-2 GT field was read; nothing here derives from a revealed GT.
- Hashes (re-verified, equal to the brief): `window.extended.yaml` b28dc9c0f8b692729c353206fd6b27eef73da07353ebc3423d53361ab817eab6 (changed from 8bfbf3d2…); `task_tools.py` 74f9784dca30fdf767f1069ee7bebb1534bc232ed6488173dd8ee17d06a7573d (changed from 67f94314…); views `0.view.json` 5d278eaf… (changed), `1.view.json` 85d971de… (unchanged world). Both shared inputs moved, so every charter-global section is re-derived in full below (round-1 text above is left untouched).
- Masked/unread until the per-task freezes: same field list as round 1. contamination_disclosure: none (no search over `tasks/`, `.audit_views/` or the scenario root; the reworker's claims arrived as item ids only).
- Entry conditions: gate snapshot supplied (all OK except TRACEABILITY, deferred: 6 unlock tool-name misses pending render); views and hashes supplied. Inputs complete.

### policy_conflict_scan (revision 2)
- Base copy lines 1–1522 still byte-identical to `blueprint/products/window.yaml`.
- Same six policies, same two components (A: payoff ← late charge, change-order fee, remeasure fee; B: deposit ← door credit), same tools and fee kinds; no two policies decide one quantity in one situation. The late-charge balance still excludes fees, so the three A-prerequisites still commute; the new late-charge minimum terms read install punch rows and warranty visits, not window fee rows.

### rule_compute_equivalence (revision 2)
Mechanical sweep re-run (`/tmp/audit_d1_0060/mech.py`): all `compute_basis` quotations verbatim in their rules, all `replaced_by` in rules, all `superseded_clause`s in base, all baseline sentences in rules, every `decides` a binding. Manual back-sweep of what changed:
- Remeasure fee: `repeat_remeasure_share` replaced by `company_check_share` (days from "the latest completed company remeasure ordered by Ridgeline on or before the remeasure date"). Compute `last_company_check` = LATEST over all completed company remeasures, not only those on or before the remeasure date; when the latest company remeasure falls after the remeasure, compute returns 1.0 instead of looking back to an earlier qualifying one (**observation G12**, world-dependent).
- Change-order fee: object now "every customer change-order line written on the latest date that carries customer change-order lines; an oversize surcharge line is never a customer change-order line"; compute `last_change_date` takes the max over the nine customer change kinds, `change_lines` and `openings_priced` subtract oversize lines. Rule and compute agree — **G4 closed**. `lender_paperwork_share` tier 3 now "any other contract, whether paid by cash, check or card or carrying no financing plan on record" — matches compute — **G6 closed**.
- Late charge: `late_rate_tier` removed (rate is the series monthly rate); new `minimum_charge_method` (work owed → late-rate amount alone; else balance < 250 → minimum alone; else max(late-rate amount, minimum)) — stated in the rule and implemented. `warranty_parts_awaiting` sums the household's warranty visits, while the sentence frames the condition as work owed "on the contract's installation"; the "meaning …" clause does not itself restrict the warranty part to this contract (**observation G11**, world-dependent).
- Payoff: three prerequisite sentences now name the latest item (see prerequisite_sentences). Holds unchanged.
- Door credit: starting rate is always the window series bundle percentage; new `bundle_credit_basis` (door first → series base price × openings the completed final measure confirmed, options excluded; same day → signed price + customer change-order lines; window first → signed price) — stated and implemented (`final_measure_on`, `measured_openings`). Returning-owner step now restricted to coverage that began before this contract's signing — rule and compute agree (`owner_coverage_start < F('signed_date')`); compute still reads only the first active registration (residual of G9; world-dependent).
- Deposit: unchanged formulas; second overwrite `replaced_by` now carries its own scope ("For a contract paid by Ridgeline financing and not yet released … and only for such a contract … a financed contract already released stays under the base rule") — **G8 closed**.
- Dead metadata: `window_ext_change_order_fee.inputs.history[0]` still lists an unfiltered latest-txn_date read over all change-order rows; it is not part of the compute (observation only).

### action_binding_and_uuids (revision 2)
- Same six tools, same uuid8 tails, one policy each. Bodies unchanged in logic (copy `customer_id`, create one row; no check, refusal or hint). Docstrings now say "rounded to the cent" (no "half up") — **G7 closed**; no example value, no sequence word, no other tool named. No factor id is a substring of any tool name (mechanical).

### prerequisite_graph (revision 2)
- Edges unchanged in shape (3 + 1, all value_input, state form, `resolved_by` = target tools, gates `fees_on_contract` / `measured_value` real bindings), acyclic. Every `condition` is now worded identically to its `policy_source`. PASS.

### prerequisite_sentences (revision 2)
- Payoff ← late charge: unchanged sentence; PASS.
- Payoff ← change-order fee: "The payoff amount is not quoted until the ledger carries a change-order fee for the latest customer change order whenever that change order falls beyond the series free count." Payoff ← remeasure fee: "Before the payoff amount is worked out, the ledger must carry a remeasure fee for the latest completed customer-requested remeasure whenever that remeasure falls beyond the series free remeasure count." Both now ask for exactly the item the depended-on rule figures ("the most recent …") — **G5 closed**; connectives "not … until" / "Before"; state form; one write each; no tool or id.
- Deposit ← door credit: "The deposit balance is not worked out until the ledger carries a door bundle discount credit for every Ridgeline door contract that was signed within the bundle window of this contract and is not cancelled, whenever this contract's discount program is none." The sentence now carries both restrictions of the base grant rule (not cancelled; program none), and `condition` is the same sentence. The round-1 situation (discount program `military`, door signed 10 days later) now leaves the edge inapplicable rather than unsatisfiable — **G2 closed**.

### override_declarations (revision 2)
- Late charge: replaced_by now describes the minimum-charge terms ("combined with the series minimum charge as the minimum-charge terms below set out"), so the base "never less than the minimum charge" is declared as replaced for these charges. Door credit: replaced_by now names the credit basis replacing "the signed contract price". Deposit: both overwrites scoped. Remeasure and change-order fee: unchanged declarations. Payoff: unchanged. No undeclared override found. PASS.

### factor_ladders (revision 2)
- Counts: remeasure 4 (1 m / 3 p); change-order 6 (1/5); late charge 6 (1/5: `late_clock_anchor` now `parameter`, `minimum_charge_method` the method); payoff 4 (1/3); door credit 6 (1/5: `bundle_credit_basis` the method); deposit 4 (1/3).
- Method labels: `late_clock_anchor` relabelled parameter (honest). `bundle_credit_basis`: tiers compute the basis by different arithmetic over different inputs (per-opening base price × measured openings; price + sum of customer lines; price field) — honest; the business does vary bundle discounts between "base product only" and "whole project". **G1b closed.** `minimum_charge_method`: three stated methods (no floor / flat minimum / max of the two).
- **New finding G10 — `minimum_charge_method` tier 2 always returns the fall-through's number.** Tier 2 applies when no work is owed and "the late-charge balance is below the small-balance amount" (250) and gives "the series minimum charge alone"; the fall-through gives "the larger of the late-rate amount and the series minimum charge". The late-rate amount is the series monthly rate × account-standing share × catch-up share × balance; every series has `late_balance_monthly_rate` 0.015 and `late_balance_min_charge` 15.0, and every share is ≤ 1 (0.5/0.8/1; 0.5/0.75/1). For any balance < 250 the late-rate amount is < 0.015 × 250 = 3.75 < 15, so the fall-through also gives exactly 15.00. On every input its condition admits, tier 2 selects the same number as the fall-through: one tier written as two. The ladder has two live outcomes, not three; the factor fails the ≥3-distinct-tier test, and with it struck out the late-charge computation has 5 factors and **0 method factors**. G1a's class therefore re-opens through this replacement. Bears on task 0.
- `company_check_share` (replaces `repeat_remeasure_share`; **G3 closed**): same-trip/recent/none tiers, values 0.75/0.9/1, each reachable in every series; real practice (a customer remeasure riding on a company visit costs less).
- Other ladders unchanged except values chosen to avoid ties (bundle late add-on 0.7, measured door 0.8, clean-paying 0.5); all tiers distinct.
- Multi-source: `minimum_charge_method` tier 1 (install punch rows ∨ warranty visits), `company_delay_goodwill`, `account_standing_share`, `lead_safe_verification_hold`, `lender_paperwork_share`, `promo_financing_share`. Cross-difficulty categories unchanged (late charge adds warranty).

### findings (revision 2)
- G1a — the relabel is honest, but the replacement method factor fails the ladder test (G10). **Not closed in effect.** Task 0.
- G1b — closed. G2 — closed. G3 — closed (factor replaced). G4 — closed. G5 — closed. G6 — closed. G7 — closed in docstrings; per-task tie check in task files. G8 — closed. G9 — "earlier installation" now in compute; first-row read remains (observation, world-dependent).
- **G10 — SOURCE-FACTOR RED (new, structural)**: see factor_ladders. Evidence: `window.extended.yaml` lines 1878, 1924, 1927, 2004–2018; variant parameters lines 217–218, 274–275, 331–332, 388–389, 445–446, 502–503 (rate 0.015, minimum 15.0 in all six series).
- G11, G12 — observations (world-dependent).

### closing_checklist (revision 2)
Written after the round-2 reveals. Difficulty **not closed**.
- Files one-to-one with tasks; revision_2 appended to `_difficulty.md`, `0.md`, `1.md`; round-1 text untouched.
- Scopes: task 0 {late charge, change-order fee, remeasure fee, payoff}; task 1 {door credit, deposit} — disjoint, jointly complete. uuid8s unchanged and independent.
- Trees: task 0 (3 prerequisites, 3 value_input, user root), task 1 (1, 1, user root); acyclic; every edge load-bearing; GT equals blind on every write in both tasks.
- Factors: every factor bears weight on its world; fall-backs definite and ≠ gold (75.62/85.00/135.00/3776.90; 451.36/1162.82). **Open: G10** — `minimum_charge_method` tier 2 ≡ fall-through, so step 11 of task 0 has no honest method factor.
- Round-1 items: G1a re-opened as G10 (T0-3); G1b, G2, G3, G4, G5, G6, G7, G8, T0-2 closed; G9 residual and G11/G12 observations, world-dependent, not exercised.
- Gates: not re-run by the auditor (snapshot supplied; TRACEABILITY deferred to render).

Per-task verdicts (revision 2):
- task 0: SOURCE-FACTOR RED (T0-3 / G10).
- task 1: PASS.

## revision_3

### charter_global_frozen (revision 3)
- Round-3 re-audit. Written 2026-10-13 before any round-3 GT field was read. Hashes re-verified and equal to the brief: `window.extended.yaml` 7e86ff7e938565f347a27a478952851aef1a0b31d07592eb0b8158c394e83aa6 (changed from b28dc9c0…); `task_tools.py` 74f9784d… (unchanged); views 5d278eaf… / 85d971de… (unchanged). The charter moved, so the charter-global sections are re-derived below; `action_binding_and_uuids` carries forward from revision 2 on the unchanged tool hash (bodies and docstrings re-grepped: unchanged). Base copy still identical to `blueprint/products/window.yaml`. contamination_disclosure: none for round 3.
- Mechanical sweep re-run (`/tmp/audit_d1_0060/mech.py`): all compute_basis/replaced_by/superseded/baseline/prerequisite quotations verbatim; gates exist; no factor id inside a tool name.

### changes verified (revision 3)
- **G10 / T0-3 — closed.** `minimum_charge_method` tier 2 is now "no such work is owed and the contract already carries a late balance charge for an earlier period → the series minimum charge plus the late-rate amount" (rule line in the minimum-terms sentence; compute `P('late_balance_min_charge') + late_rate_amount if periods_charged > 0`). Against the fall-through max(late-rate amount, minimum): if the late-rate amount ≥ 15 the two differ by 15.00; if it is below 15 they differ by the late-rate amount, which is positive for any late-charge balance above about 1.33 (0.015 × 0.5 × 0.75 × b ≥ 0.005), in every series (rate 0.015, minimum 15.0 in all six). Tier 1 (late-rate amount alone) differs from the fall-through whenever the late-rate amount is below 15. Three distinct outcomes; three distinct arithmetic forms (no floor / sum / max) — an honest `method`. `small_balance_amount` removed from params. Realism: a flat late fee plus the rate for a repeat late period, and no minimum while the company still owes work, are both published practice.
- **G11 — closed.** The rule now says "a warranty part left on order at a service visit under this contract's warranty registration"; compute filters `warranty_registration_id=CFIELD('warranty','warranty_registration_id', window_contract_id=HID)`.
- **G12 — closed.** Rule, basis and ladder now read "the latest completed company remeasure ordered by Ridgeline on the contract", with a latest one after the remeasure date taking a share of one; compute (`LATEST` over company remeasures, negative day difference → 1.0) matches.
- **Dead `inputs.history` metadata — closed.** The change-order entry now filters the nine customer kinds and lists the oversize subtractions; the late-charge entries list punch and warranty reads.
- **G9 residual — wording closed, new defect opened (G13).** The door-credit rule now says "The door contract read for the credit is the household's door contract on record, and where the household holds several door contracts, the one recorded first; the warranty registration read for the returning-owner step is the household's registration in force, and where it holds several, the one recorded first." Rule and compute (first matching row) now agree. See G13 for what that rule does.

### findings (revision 3)
- **G13 — SOURCE-POLICY RED (new in revision 3, charter level; no task world exercises it).** Two passages:
  - deposit rule: "The deposit balance is not worked out until the ledger carries a door bundle discount credit for every Ridgeline door contract that was signed within the bundle window of this contract and is not cancelled, whenever this contract's discount program is none."
  - base `window_price_credits` (kept by the door-credit overwrite: "when and how often the credit is granted … stay as the base rule states them"): the credit "is granted on the window contract when the customer signs a Ridgeline door contract within the bundle window … and once per pair of contracts".
  - door-credit rule: "The door contract read for the credit is … where the household holds several door contracts, the one recorded first."

  Situation: a household holds door contract D1 (recorded first, signed 20 days before window contract W) and door contract D2 (signed 10 days after W). Both are inside the 60-day window, neither is cancelled, and the discount program is none. The deposit sentence and the base rule call for two credits, one per pair. The door-credit rule figures both from D1's signing date, price, stage and financing, so the two amounts are identical. Also, `post_door_bundle_credit_ed16c33c` builds its row id from (window contract, amount, "door_bundle_discount") and `ctx.create` is idempotent (`erlbench/tools.py` line 111–119). The second call therefore writes nothing: the ledger can never carry two credits, and no credit row names its door anyway. Either the deposit waits forever (no solution), or an agent counts one credit as covering both doors (a second reading).

  The same "recorded first" choice applies when only an out-of-window door is recorded first (an old closed door contract plus a new in-window one): the credit for the in-window pair is then figured from the out-of-window door's dates and price. That is not a treatment the business would publish for that pair.

  Neither task exercises this: task 1 has one door contract and one registration; task 0 has no door credit.
- Observation: "the one recorded first" for the warranty registration can pick a registration whose coverage began after this contract's signing and so drop the step, although an older qualifying registration exists (compute requires `owner_coverage_start < F('signed_date')` on the first row only). This is world-dependent and not exercised.
- All other revision-2 conclusions carry forward unchanged: policy_conflict_scan, override_declarations (the late-charge overwrite already referred the minimum to "the minimum-charge terms below"), prerequisite_graph, prerequisite_sentences. The factor counts per computation are unchanged (1 honest method each).

### closing_checklist (revision 3)
Written after the round-3 reveals.
- Both tasks: GT equals the blind derivation on every write, argument, owner, order and terminal row. Every factor bears weight. Each computation has one honest method factor, at least two parameters and 4–6 factors. Each task has at least one multi-source and one cross-difficulty factor. Both trees are well formed, acyclic, load-bearing, with a user-owned root. Scopes are disjoint and complete. uuid8s are unchanged. Gates were not re-run by the auditor (snapshot cited; TRACEABILITY deferred to render).
- Round-2 items closed: G10/T0-3, G11, G12, dead inputs.history entries, G9 wording.
- **Open: G13** (charter-level SOURCE-POLICY RED, new in round 3). The door-credit rule's "the one recorded first" selection, read with the deposit's "for every … door contract" sentence, the base per-pair grant and the idempotent credit row id, has no solution in a two-door household. No task world exercises it. The difficulty is therefore not closed at charter level, although both tasks' scored solutions are unique and correct.

Per-task verdicts (revision 3):
- task 0: PASS.
- task 1: PASS on its world; carries charter-level SOURCE-POLICY RED G13 (T1-3), with no consequence on this world.

## revision_4

### charter_global_frozen (revision 4)
- Round-4 re-audit, written 2026-10-13 before any round-4 GT field was read. Hashes re-verified and equal to the brief:
  - `window.extended.yaml` ca32d47eb7b8da0b22cb0ecae1a925c4b5b597562374ab54e186c7341a931c11 (changed).
  - `task_tools.py` 74f9784d… (unchanged; `action_binding_and_uuids` carries forward from revision 2).
  - views 9f68a088… / 13b41fd7… (both changed).
- Base copy is still identical to the blueprint. The mechanical sweep re-run is clean (quotations verbatim, gates exist, no factor id inside a tool name). contamination_disclosure: earlier rounds' GT known from earlier reveals; none for round 4.

### changes verified (revision 4)
- **G13 / T1-3 — closed.**
  - A new overwrite supersedes base "and once per pair of contracts". On the window side the credit is now once per window contract, paired with one door.
  - The deposit sentence asks for "this contract's door bundle discount credit" (one row), and its condition is identical to it.
  - With one credit per window contract, the idempotent-row-id collision and the "every door" demand are gone.
  - The compute reads the paired door by id (`paired_door` → `CFIELD(..., door_contract_id=paired_door)`).
- **Registration observation — closed.** `returning_owner_step` was replaced by `window_project_step`: openings confirmed at the completed final measure; ≥20 → +0.01, ≥10 → +0.005, else 0. Rule, basis, ladder and compute agree. Realism: a larger window project earning a richer bundle rate is ordinary practice.
- **Change-order `returning_household_share` — first-row class closed.**
  - It is now keyed on "the household's most recent final-balance payment on a Ridgeline door contract" (`XLATEST` over door_transactions; a payment must fall before the change-order date). Rule, ladder and compute agree.
  - Observation G16: a door paid entirely by lender funding leaves no customer final-balance row, so that household counts as not returning. This is world-dependent; on task 0's world the 2017 door was paid off by check.

### findings (revision 4)
- **G14 — SOURCE-POLICY RED (new in revision 4, charter level; no task world exercises it).** The pairing rule contradicts the base grant condition that the same policy keeps.
  - **Passage 1** (second overwrite `replaced_by` and the rule's first sentence): "when the credit is granted, and the rule that it needs a discount program of none, stay as the base rule states them".
  - **The kept base clause** (`window_price_credits`): the credit "is granted on the window contract when the customer signs a Ridgeline door contract within the bundle window of calendar days before or after this contract's signed date and neither contract is cancelled".
  - **Passage 2** (new pairing sentence): "the door contract it pairs with is the household's door contract whose booking deposit was received most recently, and the credit arises only when that door contract was signed within the bundle window of this contract and is not cancelled".
  - **Situation A.** The household holds a 2017 closed door contract D0 with its 2017 booking deposit. It also holds a new Portal 310 or Portal 520 door D1 on Ridgeline financing, signed 10 days after window contract W. Those two door series have `financed_deposit_pct: 0.0` (`door.yaml` lines 170, 232), so D1 never takes a booking deposit.
    - Passage 2 pairs W with D0, which is outside the window, so no credit.
    - The kept base clause grants the credit, because the customer signed D1 within the window and neither contract is cancelled.
    - The door charter still grants D1 its door-side bundle discount.
  - **Situation B.** In-window door D1 (deposit on its signing day) plus a later door D2 signed 70 days after W, whose deposit arrives later. Passage 2 pairs with D2, which is outside the window, so no window credit. The base clause grants one for D1.
  - **Situation C.** The most recent deposit sits on a cancelled door. Passage 2 gives no credit; the base clause grants one for the other, in-window door.
  - In each situation the two passages reach opposite conclusions about whether the credit is owed. The deposit's prerequisite sentence inherits Passage 2, so whether the deposit waits on a credit also flips.
  - Realism: a replacement contractor pairs a bundle by the contracts signed together inside the bundle window, not by which booking deposit cleared last. Withholding an earned window bundle credit because of a later or cancelled door purchase, or because a financed door took no deposit, is not a treatment the business would publish.
  - Neither task exercises it: task 1 holds one door contract, in-window, with a booking deposit; task 0 has no door credit.
- Observations: G15 — the rule names no tie-break when two door booking deposits share the latest date (`XLATEST` keeps the first row met). G17 — `project_openings` sums all completed final measures where the rule reads "the completed final measure" (one per contract under the base lifecycle, so this is moot in practice). G16 as above.
- Carried forward unchanged: policy_conflict_scan, prerequisite_graph (shape unchanged; deposit condition = sentence), the other prerequisite sentences, and the factor structure (each computation has 4–6 factors with 1 honest method). The door credit's cross-difficulty factors are now door and finance only (`window_project_step` reads this contract).

### closing_checklist (revision 4)
Written after the round-4 reveals.
- In both tasks GT equals the blind derivation on every write, argument, owner, order, terminal row, fall-back and factor substitution.
- Every computation has 4–6 factors with one honest method, at least two parameters, and every factor bearing weight. Each task has a multi-source factor (task 0: goodwill, standing, minimum terms, lead-safe, lender; task 1: promo financing) and a cross-difficulty factor.
- Both trees hold. Scopes are disjoint and complete. The tools are unchanged. Gates were not re-run by the auditor (snapshot cited; TRACEABILITY deferred to render).
- Round-3 items closed: G13/T1-3, the registration observation, and the first-row class in the change-order fee.
- **Open: G14** — a new charter-level SOURCE-POLICY RED in the door-credit pairing rule, which contradicts the kept base grant clause and is unrealistic for the trade. No task world exercises it. Observations G15, G16, G17 are world-dependent and not exercised.

Per-task verdicts (revision 4):
- task 0: PASS.
- task 1: PASS on its world; carries charter-level SOURCE-POLICY RED G14 (T1-4), with no consequence on this world.

## revision_5

### charter_global_frozen (revision 5)
- Round-5 re-audit, written 2026-10-14 before any round-5 GT field was read. No revision_5 text existed before this round; the cut delivery had not run.
- Hashes re-verified and equal to the brief:
  - `window.extended.yaml` 65fb1d0301756ee74a823b1f5307698a941278a167e6b79a5e6c53dc4f33fcc0 (changed);
  - `task_tools.py` 74f9784d… (unchanged, so `action_binding_and_uuids` carries forward);
  - `0.view.json` 5d278eaf…, the same hash as revisions 2–3, so the 2017 door ledger is gone again;
  - `1.view.json` 13b41fd7…, the same as revision 4.
- Base copy is still identical to the blueprint. The mechanical sweep is clean. contamination_disclosure: earlier rounds' GT known; none for round 5.

### changes verified (revision 5)
- **G14 contradiction — closed.** The first door-credit overwrite now supersedes the whole base grant clause, verbatim: "it is granted on the window contract when the customer signs a Ridgeline door contract within the bundle window of calendar days before or after this contract's signed date and neither contract is cancelled, and once per pair of contracts". The second overwrite no longer keeps "when the credit is granted", so no kept base clause disagrees with the new pairing rule.
- **`replaced_by` completeness.** Kept from the base clause: in-window, door not cancelled, discount program none, granted on the window contract, and how often (now once per window contract). Dropped: "neither contract is cancelled" as it applied to the window contract itself. The sibling base clause in `window_standard_cancellation` ("Once a contract is cancelled, no further change order, measure visit, or price credit other than an on_time_guarantee_credit already earned is booked to it") still bars a credit on a cancelled window contract, so the drop has no consequence. Observation only.
- **Rule = compute for the pairing.** Five per-stage `CFIELD(..., status=<stage>)` reads, an in-window test against `P('door_bundle_window_days')`, the first in-window stage pairs, and `result = 0` when none pairs ("no window-side credit arises").
  - The rule's parenthesis "contracts are entered when signed, so this is the earliest signed at that stage" asserts that record order equals signing order. Compute takes dict order, so the two agree only on seeds entered in signing order. Both task worlds hold one door contract, so this is not exercised.
- **Deposit sentence.** It now reads "…whenever a door contract of the household pairs with this contract under the window-side bundle pairing terms and this contract's discount program is none". The `condition` is the same sentence without its lead clause; state form; one write brings it about.
- **G15 — moot** (deposit pairing withdrawn). **G16 —** the returning-household share reads "first closed Ridgeline door contract (the closed door contract entered first in the records, that is the earliest signed)". Rule and compute agree; "customer since the first door" is a realistic loyalty anchor. **G17 — closed** (`project_openings` uses MAX, and the rule says so).

### findings (revision 5)
- **G18 — SOURCE-POLICY RED (charter level; residual of G14's class; no task world exercises it).** The window-side pairing looks at only one door contract per stage, so an in-window door is ignored whenever an out-of-window door at the same stage was entered first.
  - **The conflicting passages:**
    - Window side (`window_ext_door_bundle_credit` rule and overwrite 1): "at each stage only the one entered first in the records is looked at … the first door contract so looked at that was signed within the bundle window … pairs with it … and when none pairs no window-side credit arises".
    - Door side (`door.yaml`, `door_price_credits`, base charter, rendered in the same KB): "A window_bundle_discount credit … is granted on the door contract when the customer signs a Ridgeline window contract within the bundle window of calendar days before or after this contract's signed date and neither contract is cancelled, once per pair of contracts."
  - **Situation:** a household holds an entry door contract D-entry, signed 75 days before window contract W, and a patio door contract D-patio, signed 20 days before W. Both are `measured`, D-entry was entered first, neither is cancelled, and W's discount program is none.
  - **What each side concludes:**
    - The window side looks only at D-entry at the measured stage. It is out of the window, no other stage holds a door, so W and D-patio are not a bundle and no window credit arises.
    - The door side grants D-patio its window-bundle discount for the pair (W, D-patio), which is a bundle.
  - **Consequence:** the KB tells the agent the same pair both is and is not bundled. The deposit's prerequisite sentence turns on the window answer, so whether the deposit waits on a credit flips with it.
  - **Realism:** a window-and-door company pairs a bundle by the contracts signed together within the window. Denying the window side of an earned bundle because an older door contract at the same stage is on file — a stalled or earlier-season purchase — is not a treatment it would publish. The blueprint itself describes households holding "a door contract signed the same season", so two door contracts per household is an ordinary world.
  - **Not exercised by any task:** task 1 has one door contract (measured, in the window); task 0 has no door credit.
- **Class sweep (as requested): every first-match read in the charter, with its decoy and absent-record cases.** Every read below takes the first matching row in record order (`CFIELD`/`CPARAM`/`EXISTS` return or test the first holding). None of them is exercised by either task world, where each read has exactly one candidate row.
  1. Door credit, per-stage door reads (`door_s/m/o/i/c_*`): **decoy** — two door contracts at one stage, the first entered out of the window and the second in it (G18). **Absent** — no door in the window → result 0, no credit, as stated.
  2. Door credit `door_signed`/`door_price`/`door_stage`/`door_plan_promo` (keyed by `paired_door` id — exact). **Absent** — the paired door has no finance account → promo `None` → share of one (stated by the rule's "otherwise").
  3. Door credit `window_plan_promo` = `CPARAM('finance','promo_type', window_contract_id=HID)`: **decoy** — a cancelled or declined financing approval on this window contract entered before the live account; the cancelled plan's promotion decides the share.
  4. Change-order `plan_promo_months` = `CPARAM('finance','promo_months', window_contract_id=HID)`: same decoy as 3. **Absent** — a financing contract with no account on record → share of one (stated since revision 2).
  5. Change-order `first_door_closed` = `CFIELD('door','closed_date', status='closed')`: **decoy** — two closed door contracts entered out of signing order; the rule's "entered first …, that is the earliest signed" then names two different contracts.
  6. Late charge `funded_on`, `autopay_on` = `CFIELD('finance', …, window_contract_id=HID)` and `EXISTS('finance', window_contract_id=HID)` (grace, standing tier 2): **decoy** — a cancelled or declined approval entered first. It gives no funded date, so the clock falls to completion. `autopay_enrolled` is false, so manual grace applies. `EXISTS` is true even when the only account on the contract is cancelled.
  7. Late charge `job_closed_on`, and the job id used for company reschedules and open punch items = `CFIELD('install', …, window_contract_id=HID)`: **decoy** — a cancelled installation job (install charter `install_cancellation`) entered before the job that did the work; its punch items, reschedules and closing date are read instead.
  8. Late charge `factory_ship_slip_days` = `DAYS(CFIELD('order','committed_ship_date', …), CFIELD('order','ship_date', …))`: **decoy** — a cancelled factory order (order charter `order_cancellation`) entered before the order that shipped. **Absent** — no order on the contract, or an empty `ship_date`: `DAYS` raises, so no definite number.
  9. Late charge `warranty_parts_awaiting` (registration via `CFIELD('warranty','warranty_registration_id', window_contract_id=HID)`): **decoy** — a voided or closed registration on the contract entered before the live one. **Absent** — no registration yet → id `None` → 0 parts awaiting (a sensible reading).
  10. Payoff `install_job`, `job_status`, `job_permitted`, `job_units` = `CFIELD('install', …, window_contract_id=HID)`: same decoy as 7; the holds would read the cancelled job. **Absent** — no job → all holds 0 and job net charges 0.
  11. Remeasure `last_company_check`, change-order `last_change_date`, `final_measure_on`/`measured_openings` are `LATEST`/`MAX` over this contract's own ledger, keyed by stated filters — no first-match issue. **Absent** — a contract with no customer change-order line yields `''` and `DAYS` would raise, but the change-order policy applies only to a change order beyond the free count, so the input always exists.
- Carried forward unchanged: policy_conflict_scan, prerequisite_graph (shape unchanged), the payoff prerequisite sentences, factor structure (4–6 factors each, one honest method, distinct tiers), and override declarations other than the door credit's.

### closing_checklist (revision 5)
Written after the round-5 reveals.
- In both tasks GT equals the blind derivation on every write, argument, owner, order, terminal row, fall-back and factor substitution.
- Factor structure holds: 4–6 factors with one honest method per computation, distinct tiers, every factor bearing weight. Trees hold. Scopes are disjoint and complete. The tools are unchanged. Gates were not re-run by the auditor (snapshot cited; TRACEABILITY deferred to render).
- Round-4 items: the G14 contradiction is closed; G15 is moot; G16 and G17 are closed.
- **Open: G18** (charter-level SOURCE-POLICY RED: same-stage first-entered pairing contradicts the door charter's per-pair bundle and is unrealistic).
- The first-match class sweep lists eleven read sites with their decoy and absent-record cases. Items 3–10 carry the same class of risk and are not exercised by any task.

revision_5 verdict: task0=PASS task1=PASS
charter=G18

## revision_6

### entry (revision 6)
- 2026-10-14. On the coordinator's instruction I built the views and ran the gates myself, from the repo root.
- **Views** (`/tmp/erl0060_coord/views.py`, executed only):
  - `0.view.json` 5d278eafc553ebf582555460536046290b9add642ac077f3b45173a464d5327e
  - `1.view.json` 13b41fd743e41ebd79d43f556ef265346fdf4f32cc60ea8ac08250d2ca0ecb93
  - Both are identical to revision 5, so neither world changed.
- **Charter and tools:** `window.extended.yaml` 1d5a7513e7fb6de3a59f59a407334cfef6d031949558cba89ae5ff1a0b698210 (changed); `task_tools.py` 74f9784d… (unchanged).
- **Gates** (summary lines only; full outputs in `/tmp/audit_d1_0060/gate_*.txt`, read with numbers masked):
  - EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - TRACEABILITY NOT OK, with six misses, all `unlock_*_discoverable_tool:tool_name`: four in 0.json (the late charge, change-order fee, remeasure fee and payoff tools) and two in 1.json (the door credit and deposit tools). No other miss.
  - The entry condition holds; not STOPPED.
- Base copy is identical to the blueprint. The mechanical sweep is clean. contamination_disclosure: none for round 6. The gate outputs were read only for their summary and miss lines, with every decimal figure masked.

### changes verified (revision 6)
- **Class sites 2–10 of revision 5 — closed.** Each read now carries an explicit status filter and an absent-record branch that the rule states.
  - **The filters:**
    - Financing account: the one "in force (approved, active, delinquent or paid off); a cancelled or charged-off account is never read". This covers the change-order plan, the late-charge funding date, autopay, grace and standing, and both door-credit plan reads.
    - Installation job: "the one not cancelled". This covers the late-charge clock, reschedules and punch items, and every payoff hold.
    - Factory order: "the one not cancelled". When there is no order or no ship date, the slip is 0.
    - Warranty registration: "in force (active or transfer pending)".
    - Returning household: now reads the latest closing date over closed door contracts (`XLATEST`), independent of record order. "Any other household, including one with no closed door contract, takes a share of one".
  - **Probes** (my own, on scratch copies of the views, `/tmp/audit_d1_0060/r6probe.py`). I put a decoy row first in record order for each site and checked the absent-record branches:
    - Task 0 with a cancelled finance account, a cancelled install job, a cancelled factory order and a voided registration all entered first: the live reads stay on 27196484 / ac86ec8f / 30b248b8 / 9f9d5bef. Late charge 14.18, change-order fee 153.81 and the opening-world payoff 2665.40 are all unchanged.
    - Task 0 with the factory order removed: slip 0, goodwill 7, late charge 14.18. That is a definite number; it used to raise.
    - Task 1 with a cancelled financing account (equal-pay plan) entered first on the door: the door promo is still deferred_interest; credit 161.27.
- **Round-5 G18 decoy — closed.** An older out-of-window door at the same stage, entered first, no longer masks the in-window door. Probe: pairs eed57bf9; credit 161.27. Record-entry order no longer matters.
- **Pairing rule = compute.**
  - For each stage, the latest-signed door contract at that stage is taken (`XLATEST` signed_date per status; cancelled excluded).
  - Of those, the ones in the window are candidates, and the latest-signed candidate pairs.
  - A signing-date tie goes to the further stage. Within one stage and day, the highest price pairs.
  - With no candidate, the result is 0 ("no window-side credit arises").
- **Overwrite scope:** unchanged from revision 5 (whole base grant clause superseded; the cancelled-window case is covered by `window_standard_cancellation`).

### findings (revision 6)
- **G18 (residual) — SOURCE-POLICY RED, narrowed but not closed (charter level; no task world exercises it).**
  - **Why it remains:** each stage still contributes only one door, now its latest-signed. A door that is in the bundle window and not cancelled is never a candidate when a later-signed out-of-window door sits at the same stage. The window side then denies a pair that the door side grants.
  - **Probe** on a scratch copy of task 1's world:
    - window contract W signed on 2026-06-01;
    - patio door D1 signed on 2026-06-20 (19 days after W, so in the window), status measured;
    - entry door D2 signed on 2026-08-15 (75 days after W, so out of the window), status measured.
  - **Result:** the window side computes `pair_stage` none, `paired_door` None and result 0, whichever row is entered first.
  - **Door side:** the door charter (`door_price_credits`: "granted on the door contract when the customer signs a Ridgeline window contract within the bundle window … once per pair of contracts") grants D1 its window-bundle discount for the pair (W, D1).
  - **Consequence:** the KB again says the same pair both is and is not a bundle. The deposit's prerequisite sentence ("whenever a door contract of the household pairs with this contract under the window-side bundle pairing terms") flips with it.
  - **Realism:** a later door purchase made outside the bundle window cannot un-bundle an earlier in-window pair in this trade.
  - **The criterion the coordinator set:** "the window side pairs exactly the pairs the door side grants". With a once-per-window credit, that means "a window credit arises whenever the door side grants at least one pair with this window". The probe fails it.
  - **Remaining members of this class:** only the per-stage selection (five `XLATEST(..., status=<stage>)` reads in `window_ext_door_bundle_credit`). Its decoy is a later-signed, out-of-window door at the same stage as an in-window one. Its absent case — no in-window door at all → 0 — is correct. A tie on stage, signing date and price still falls to record order (`CFIELD` with equal keys); this is an observation only.
- **Observation G19 (realism):** the returning-household share now runs from the most recently closed door. A household whose last door closed five years ago gets the larger reduction (0.5), and one whose last door closed last year gets 0.75. Rule and compute agree. As a win-back schedule this is defensible, so it is not raised.
- **Re-derivation:** both worlds are unchanged, and the DSL evaluation on the views gives the same figures as revision 5: 14.18 / 153.81 / 43.51 / 2876.90 and 161.27 / 1719.48, with every substitution and fall-back unchanged.

### closing_checklist (revision 6)
- Both tasks: GT equals the blind derivation on every write, argument, owner, order, terminal row, fall-back and substitution. Factor structure, trees, scopes and tools hold. I re-ran the gates myself this round: all green except TRACEABILITY, whose six misses are all `unlock_*:tool_name` pending the KB render.
- Revision-5 class sites 2–10: closed, verified by decoy and absent-record probes. Round-5 G18 decoy (older same-stage door entered first): closed.
- **Open: G18 residual** — a later-signed out-of-window door at the same stage masks an in-window door, so the window side denies a pair the door side grants. The one remaining member of the class is the per-stage latest-signed selection.

revision_6 verdict: task0=PASS task1=PASS
charter=G18

## revision_7

### entry (revision 7)
- 2026-10-14. On the coordinator's instruction I built the views and ran the gates myself.
- **Views** (`/tmp/erl0060_coord/views.py`, executed only): `0.view.json` 5d278eafc553ebf582555460536046290b9add642ac077f3b45173a464d5327e and `1.view.json` 13b41fd743e41ebd79d43f556ef265346fdf4f32cc60ea8ac08250d2ca0ecb93. Both are unchanged, so neither world changed. The door-side credit row this route relies on (door_transactions e593c0b0, window_bundle_discount 214.00 dated 2026-08-31) was already in task 1's seed.
- **Charter and tools:** `window.extended.yaml` e8f306a522afde93cb25a3ee7b48fc97f4f44a04893b253b6d462c385a46d7ca (changed); `task_tools.py` 74f9784d… (unchanged).
- **Gates** (summary lines only, in `/tmp/audit_d1_0060/gate7_*.txt`):
  - EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - TRACEABILITY NOT OK, with six misses, all `unlock_*_discoverable_tool:tool_name`.
  - Not STOPPED.
- Base copy identical to the blueprint; mechanical sweep clean.
- contamination_disclosure: neither world changed, so the blind figures are revision 6's frozen figures. This round I re-ran the DSL evaluation and read the gold in the same tool call. The evaluation output (identical to revision 6) printed before the gold lines, but this freeze note was written after the reveal. Disclosed; it has no effect on any figure.

### changes verified (revision 7)
- **New pairing anchor.** The window side pairs with "the door contract whose own window bundle discount, granted under the door terms, is the household's most recent one by date, and among such door credits granted on the same date the one with the highest amount". That door pairs only when it is not cancelled, its program is none, and it was signed within the bundle window of this contract.
  - Compute matches: `door_credit_date` = XLATEST credit date, `door_credit_amount` = XMAX amount on that date, `credited_door` = the door on that row, followed by the status, program and `ABS(DAYS(...)) <= window` test.
  - The deposit sentence equals its condition.
- **Seeded row realism (task 1).** The door charter's `door_price_credits` grants "a window_bundle_discount credit [that] equals the series bundle percentage of the signed door contract price … granted on the door contract when the customer signs a Ridgeline window contract within the bundle window … and neither contract is cancelled, once per pair". Against that:
  - Glide 840 `window_bundle_discount_pct` 0.05 × 4280 = 214.00 ✓.
  - Dated 2026-08-31, the window's signing day, which is the event that triggers the door-side grant ✓.
  - Door program none ✓; door measured, not cancelled ✓; 41 days, inside the 60-day door window ✓.
  - Realistic.
- **Probes** (my own, on scratch copies of task 1's world, `/tmp/audit_d1_0060/r7probe.py`):
  - **Base:** pairs eed57bf9; credit 161.27.
  - **(a) An old out-of-window bundle credit** (2017 door, 2017 credit) alongside the current one: still pairs eed57bf9; 161.27 ✓.
  - **(b2) Two in-window doors credited the same day:** the higher credit (300.00, door D3) pairs; 460.77. Deterministic ✓.
  - **(d) No credit row at all:** result 0, no credit (stated).
  - **(a2) Current door's credit not on the door ledger, only the 2017 one:** result 0. This is an absent-record case. The door charter always books its credit when the window is signed, so a correctly seeded world never shows it. Observation only.
  - **(c) A cancelled credited door — see G18 below.**
  - **(b) Two credited doors, one bundled with another window — see G18 below.**
  - **Tie — see the class list below.**

### findings (revision 7)
- **G18 (residual) — SOURCE-POLICY RED, still not closed (charter level; neither task exercises it).**
  - **Why it remains:** the anchor is the household's single most recent door-side bundle credit, and that row does not say which window contract it pairs with. Any later credit on a door that cannot pair with this window therefore hides an earlier credit that does.
  - **Probe (c), cancelled credited door.** Window contract W was signed 2026-08-31. Door eed57bf9 holds its door credit dated 2026-08-31 (pair W–eed57bf9 granted by the door side). The customer then signs a second door CXL on 2026-09-05; it is credited 150.00 that day for the same window, then cancelled.
    - Window side: `credited_door` CXL is cancelled, so it does not pair; result 0.
    - The door side granted, and still holds, the bundle discount for the pair W–eed57bf9. Signing a second door and cancelling it is an ordinary event in this trade.
  - **Probe (b), two windows (the base cap allows two open window contracts per customer).** W was signed 2026-08-31 and paired with eed57bf9 (credit 2026-08-31). A second window contract W2 is signed 2026-10-30, and door D2, signed 2026-11-05, takes its door credit 2026-11-05 for the pair W2–D2. Handling W on 2026-11-10:
    - `credited_door` = D2, which is 66 days after W and so outside its window; result 0.
    - W loses the bundle the door side granted for the pair W–eed57bf9.
  - **Consequence:** in both probes the window side denies a pair the door charter grants. The deposit's prerequisite sentence flips with it. This fails the coordinator's criterion that the window side pairs exactly the doors the door charter grants.
- **Remaining members of the class (complete list):**
  1. The most-recent-credit anchor with a credited door that no longer pairs, because it is cancelled, has a discount program, or is out of this window (probes b and c) — RED as above.
  2. The tie on credit date and amount: `XLATEST(..., txn_date=…, amount=…)` returns the first row met. Probe: a second door D4 with the same 214.00 credit on 2026-08-31 pairs or not depending on which row is entered first (eed57bf9 vs D4). The paired door's own signed date, price, stage and financing then feed the credit, so this is record-order dependent. The rule is silent on this tie. It is a second instance of the same defect; I record it as an observation because equal same-day credits on two doors are rare.
  3. Absent-record case (a2) — observation only, as above.
- All other sites from revisions 5 and 6 stay closed (filters and absent tiers unchanged; mechanical sweep clean). No regression in factor structure, trees or override declarations.

### closing_checklist (revision 7)
- Both tasks: GT equals the blind derivation on every write, fall-back and substitution. The gates I ran are green except TRACEABILITY, whose six misses are all `unlock_*:tool_name` pending render.
- The round-6 G18 decoy (a later out-of-window door at the same stage) is closed, because a door outside every window never carries a credit.
- **Open: G18 residual** — the most-recent-door-credit anchor is masked by a later credit on a door that cannot pair with this window (cancelled, or bundled with a second window). A tie on credit date and amount is still record-order dependent.

revision_7 verdict: task0=PASS task1=PASS
charter=G18

## revision_8

### entry (revision 8)
- 2026-10-14. On the coordinator's instruction I built the views and ran the gates myself.
- **Views:** `0.view.json` 5d278eafc553ebf582555460536046290b9add642ac077f3b45173a464d5327e and `1.view.json` 13b41fd743e41ebd79d43f556ef265346fdf4f32cc60ea8ac08250d2ca0ecb93. Both unchanged; no world changed.
- **Charter:** `window.extended.yaml` c05622d9ae0adf02612a4bd804d86dbb2f6b2eef34f3d080e0caa0c6433ba44c (changed).
- **Tools:** `task_tools.py` c0b715a74318b440a3f5951c0e257ed21ce760d5c2ecf1a25fd14f2b4c769bb8 — **also changed, which the brief did not mention**. `post_door_bundle_credit_ed16c33c` now takes `door_contract_id` and builds its row id from (window, door, amount, kind), so credits for different doors on one day stay separate rows.
- **Gates** (summary lines, `/tmp/audit_d1_0060/gate8_*.txt`): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK. TRACEABILITY NOT OK with six misses, all `unlock_*_discoverable_tool:tool_name`. Not STOPPED.
- Base copy identical to the blueprint; mechanical sweep clean.
- contamination_disclosure: none. The DSL evaluation and the frozen task notes below were done before this round's gold was read.

### changes verified (revision 8)
- **Scope as written.** The door-credit overwrite now names its own scope: "For a household holding exactly one Ridgeline door contract that is not cancelled, and only for such a household…". The brief also mentions "one not-cancelled window contract", but the charter imposes no window-count condition. That is harmless, as the probe below shows.
- **Inside the scope.** The credit arises when the door was signed within the bundle window, the door's program is none and this contract's program is none; "otherwise such a household's window contract earns no door bundle discount".
  - The door charter grants the door side of the pair when the window was signed within the window, neither contract is cancelled, and the door's program is none.
  - So the window side pairs the door-side pair whenever this contract's own program is none. That last condition is the base window rule (`bundle_vs_program`), which both sides apply to their own contract.
  - The extra "door's program is none" condition is declared in `replaced_by`, and it matches the door side, which grants nothing to a door with a program.
- **Outside the scope** (no live door, or two or more): "every other household remains under the base rule for when and how often the credit is granted and for its amount, and this policy figures no credit for it".
  - The base rule gives a definite answer: one credit per in-window, non-cancelled door, each equal to the series bundle percentage × signed price. That is the door side's per-pair rule mirrored.
  - The revised tool can now book one row per door.
- **`replaced_by` completeness.** Both overwrites name their scope.
  - Overwrite 1 keeps: in-window, door not cancelled (through the household count), once (in scope), and program none. Out of scope it hands everything back to the base rule. A cancelled window contract is still barred by `window_standard_cancellation`.
  - Overwrite 2 keeps program none and returns out-of-scope amounts to the base rule.
- **Deposit sentence = condition, with the same scope.** "For a household holding exactly one Ridgeline door contract that is not cancelled, the deposit balance is not worked out until the ledger carries this contract's door bundle discount credit whenever that door contract was signed within the bundle window of this contract and the discount programs of both contracts are none; for every other household the deposit balance is worked out on the credits already on the ledger."
- **Compute = rule.**
  - `live_door_count` counts the household's door contracts at the five non-cancelled stages.
  - `single_door` is used only when that count is 1, so it is unique and independent of record order.
  - `paired_door` applies the window and both programs; `result` is 0 when there is no pair.
- **Probes** (scratch copies of task 1's world, `/tmp/audit_d1_0060/r8probe.py`):
  - **Base:** 1 live door → pairs eed57bf9; 161.27.
  - **Credited-then-cancelled later door** (CXL, cancelled, with a 150.00 door credit): live count 1 → still pairs eed57bf9; 161.27. Round-7 probe (c) closed.
  - **Second window contract W2** signed 2026-09-10 (51 days after the door): W gets 161.27 and W2 gets 146.61. The door side grants each pair.
  - **W2 signed 2026-09-20** (61 days after the door): W2 gets 0. Correct, because it is outside the 60-day window. Round-7 probe (b) closed.
  - **Ties:** impossible inside the scope, since there is exactly one door. Round-7 tie case closed.
  - **Scope boundary** (old closed 2017 door plus the current door, i.e. 2 live doors): this policy figures 0. The base rule governs and gives one credit, for the in-window current door, at 4% × 11284 = 451.36. The deposit then works on the ledger as it stands (1759.80 here).
  - **Boundary with two in-window live doors:** this policy figures 0. The base rule gives two credits, one per door, each 451.36, and the tool keeps them as two rows.
  - **In scope, door program military:** 0. Consistent with the door side, which grants no door-side credit either.
  - **Only door cancelled:** 0 live doors → out of scope → the base rule gives no credit, since its door is cancelled.

### findings (revision 8)
- **G18 — closed.** Inside the scope the window side pairs exactly the door-side pair (subject only to each side's own program rule). Outside it the base clause gives a definite per-pair answer that mirrors the door side. No record-order dependence remains in the pairing.
- Observation G20: out of scope, the deposit is worked out on the credits already on the ledger. An owed base-rule credit not yet booked therefore does not hold up the deposit. The sentence says so explicitly, so there is one reading.
- Observation G21 (realism of the boundary): a household that also holds an old closed door contract (for example a 2017 door) falls outside the scope. Its new in-window pair is then credited at the base percentage rather than under the extended terms. Both answers are definite and consistent with the door side, so this is a modelling choice, not a contradiction.
- Tool change: the docstring states what the body does ("The door contract the credit is granted for is part of the credit's reference, so credits for different door contracts granted on the same day stay separate entries"). The door id is part of the row id but not stored as a field, and the docstring does not claim it is stored. No example value, no ordering word. uuid8 unchanged. Fine.
- No regression: factor structure, trees, the other class sites and the overrides are unchanged; the mechanical sweep is clean.

### closing_checklist (revision 8)
- Both tasks: GT equals the blind derivation on every write and argument (including the new door_contract_id), fall-back and substitution. The gates I ran are green except TRACEABILITY, whose six misses are all `unlock_*:tool_name` pending render. Factor structure, trees, scopes and the first-match class sites are all closed and unchanged.
- G18: closed under the single-door scope, with the base clause definite and consistent outside it. Open observations only: G20, G21, and G9/G11/G12-class residues already closed.
- Gold changed only by the added door_contract_id argument in task 1's step 8; no scored value changed.

revision_8 verdict: task0=PASS task1=PASS
charter=CLEAN

## revision_9

### entry (revision 9)
- 2026-10-14. This round follows the window KB renderer's source findings (`audits/render_source/window_contract_deposits_and_cancellations/window_round1.md`, read in full: F1–F4).
- **Views** (executed `/tmp/erl0060_coord/views.py`): `0.view.json` 5d278eafc553ebf582555460536046290b9add642ac077f3b45173a464d5327e and `1.view.json` 13b41fd743e41ebd79d43f556ef265346fdf4f32cc60ea8ac08250d2ca0ecb93. Both unchanged.
- **Charter:** `window.extended.yaml` 837d7727357871be1eca7f783626575ab6a10f94bd89dcba06251364ff978d88 (changed). **Tools:** `task_tools.py` c0b715a7… (unchanged from revision 8).
- **Gates** (summary lines, `/tmp/audit_d1_0060/gate9_*.txt`): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, **TRACEABILITY OK** (no misses; the docs are now rendered), SCOPE OK. Not STOPPED.
- Base copy identical to the blueprint; mechanical sweep clean.
- contamination_disclosure: none. The probes and the evaluation were run, and the per-task notes written, before this round's gold was read.

### auditor's own miss (disclosure)
- I did not raise F1 or F2 in rounds 1–8.
  - **F1:** the late charge counted its entries (`COUNT(... fee_kind='late_balance_charge')`) as the periods already charged, while the rule lets one entry carry every ended period. My round-1 rule/compute sweep accepted the "periods_charged" quotation without testing a multi-period entry.
  - **F2:** "Throughout these terms … never read" (added in round 6) was in conflict with the household-wide account-standing counts. I checked the in-force filter on the account reads but not on the transaction counts.
- Both were real rule/compute mismatches with no consequence on either task world: no late entry exists in task 0, and the household has a single financing account.

### changes verified (revision 9)
- **F1 — closed.**
  - The overwrite and rule now say "so a full period counts as already charged when it ended on or before the date of the contract's latest late balance charge entry".
  - Compute: `periods_charged = MX(0, (DAYS(late_clock_start, last_late_entry) - due - grace - goodwill) // 30)`, with `last_late_entry` the latest late-charge entry date. That is exactly the number of periods ending on or before that date, counted from the late-charge start date.
  - `periods_due` and the catch-up anchor (`period_days * (periods_charged + 1)`) follow from it.
  - Probes on scratch copies of task 0's world (`/tmp/audit_d1_0060/r9probe.py`; start 2026-08-19, period ends 09-18, 10-18, 11-17, 12-17, 2027-01-16):

    | Ledger | Figured on | Charged / due | Days since first uncharged period end, share | Late charge |
    |---|---|---|---|---|
    | One entry dated 2026-11-20 (covering 3 periods) | 2027-01-20 | 3 / 2 | 34, stale 0.5 | 2 × 9.45 = 18.90 |
    | One entry dated 2026-09-25 (covering 1 period) | 2026-11-20 | 1 / 2 | 33 | 18.90 |
    | No entry | 2026-11-20 | 0 / 3 | — | 28.35 |

    All consistent with the rule. The old entry-count compute would have charged 4 periods in the first probe, re-charging two.
  - The minimum-charge tier "already carries a late balance charge for an earlier period" now keys on `periods_charged > 0`, which is consistent with that definition.
- **F2 — closed.**
  - The rule now says "The account-standing share comes from the contract's financing account in force: … otherwise, including a contract with no financing account in force, it is one."
  - Compute: the three counts are filtered `finance_account_id=live_finance_account`.
  - Probes:
    - A charged-off household account with a late fee in the last 12 months, plus a cancelled account on this contract with a returned payment entered first: standing stays 0.5, late charge 14.18. Both decoys are excluded.
    - A late fee on the live account itself: standing 1.0, late charge 28.35. The filter reads the live account.
  - Realism: the standing now rests on the paying account behind this contract, which is the account whose record the business weighs.
- **F3 — closed.** The change-order `returning_household_share` ladder tier 3 now reads "otherwise: any other household, including one with no closed door contract and one whose most recently closed door contract closed on or after the change order date", which equals the rule and the compute.
- **F4 — closed.** The credit-basis sentence now carries "(the largest count should more than one completed final measure be recorded, …)", which equals compute `MAX(...)`.
- **No regression.**
  - Every revision-8 conclusion is unchanged: the G18 scope, the overwrites, the deposit sentence, the class-site filters, tool docstrings, factor structure and trees.
  - Re-derivation: neither world changed, and every scored, fall-back and substitution figure is unchanged (14.18 / 153.81 / 43.51 / 2876.90; 161.27 / 1719.48).

### closing_checklist (revision 9)
- All four renderer source items (F1–F4) are closed, and the two late-charge reads were probed with decoys.
- The full gate block, run by me, is green, including TRACEABILITY.
- Both tasks: GT equals the blind derivation on every write, argument, fall-back and substitution. No regression from revision 8.
- Only observations remain (G16 superseded, G19, G20, G21).

revision_9 verdict: task0=PASS task1=PASS
charter=CLEAN
