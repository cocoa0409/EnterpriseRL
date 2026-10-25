# Policy-task audit — d5_vendpoint_usage_and_machine_billing / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-16T23:45Z, before any task GT was revealed. Auditor: independent policy-task auditor (erl-task-policy-audit). I did not write these artifacts.
- `tasks/d5_vendpoint_usage_and_machine_billing/vending.extended.yaml` sha256 `f88c4ed39bbafa5579ca6382c3944df00250811c1be6ae8aefac713d68437f29` (matches brief)
- `tasks/d5_vendpoint_usage_and_machine_billing/task_tools.py` sha256 `197f4869364f5d76758c0bb19b37e0f9a415027e0a5dc53df0476de404c38092` (matches brief)
- Views: `task0.view.json` `5f5d5c03…49ef`, `task1.view.json` `602ffe88…615549` (both match brief). I kept the keys `frozen_time`, `user_scenario` and `initial_state`. These keys are masked: design_rationale, db_closure, db_closure_matches_initial_state, evaluation_criteria, charter_scope, required_documents, computations, prerequisite_closure, solvability_contract.
- Read: blueprint/{blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml}, the charter, task_tools.py, the two views, audits/render_source/XF_recipe.md, and the erlbench/ listing. Not read: tasks/*/tasks/*.json, plan.md, worklog.md, and any other env/ scenario or sibling tasks/ dir. I ran no recursive search over tasks/ or over the scenario root.
- Entry conditions (Step 0): the gate snapshot came with the brief and is saved at `.audit_views/policy/d5_vendpoint_usage_and_machine_billing/r1/gates.txt`. All 7 gates are green: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. The masked views and hashes were supplied. Input is complete.
- The base copy is verbatim. Every top-level base key of the charter (category … policies) is `==` to `blueprint/products/vending.yaml`. This was checked with a scratch yaml compare.
- Scratch sweep `/tmp/audit_d5_vendpoint_usage_and_machine_billing_0068/sweep.py` (XF-6) checked four things, and all hold for all 5 extended policies:
  - every `compute_basis` quote is verbatim in its rule;
  - every compute binding has a basis;
  - every baseline.rule sentence is in the rule;
  - every `replaced_by` is in the rule, every `superseded_clause` is in its base rule, and every prerequisite `policy_source` is in its own rule.

### policy_conflict_scan
Extended policies (5):

| id | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| P1 vending_ext_startup_par_review | vending_selection_set | par_qty | resize_selection_par_58ce1bb4 (agent) | [] |
| P2 vending_ext_emergency_restock_request | vending_fee_charged (emergency_restock_fee) | emergency_restock_fee | place_emergency_restock_request_36839656 (user) | P1 (value_input → sizing_relief) |
| P3 vending_ext_month_shortfall_fee | vending_fee_charged (usage_shortfall_fee) | shortfall_fee | charge_month_shortfall_fee_b04c8474 (agent) | [] |
| P4 vending_ext_installation_fee | vending_fee_charged (install_fee) | install_fee | charge_installation_fee_f4f2dbbd (agent) | [] |
| P5 vending_ext_early_removal_notice | vending_removal_noticed + vending_fee_charged (early_removal_fee) | early_removal_fee | give_machine_removal_notice_4669343a (user) | P3 (value_input → record_share), P4 (value_input → unbilled_install) |

- Overlapping subjects:
  - P2–P5 all write `vending_fee_charged`, but each writes a different `fee_type`.
  - P1 is the only policy that writes a Corbett `par_change`.
  - P5 is the only policy that sets `removal_pending`.
  - No two policies decide the same quantity.
- Cross-policy reads inside the difficulty:
  - P2 reads Corbett par changes, which P1 writes. This is a declared edge.
  - P5 reads shortfall lines (written by P3) and install lines (written by P4). Both are declared edges.
  - P3's stockout relief reads emergency fee lines of the *tested* (past) billing month. P2 books lines in the request month, so P3 does not depend on P2 in any world where the tested month is earlier than the request month. No rule states an order between P2 and P3.
- Eligibility and time anchors: P1 is anchored on the add entry (3 months), P2 on the request day, P3 on the latest usage bill, P4 on the installation month, and P5 on the notice day with ≥3 whole months of term remaining. No two policies conflict on a gate.
- Terminal states:
  - P5 is the only policy that changes the machine's status.
  - All other writes are append-only rows.
  - No status conflict.
- Cross-category read boundaries:
  - P1 reads vmi, credit, pricing and order.
  - P2 reads vmi.
  - P3 reads vmi, credit and pricing.
  - P4 reads pricing, order and vmi.
  - P5 reads pricing, vmi and order.
  - All are reads only. No policy writes another category.
- Conflicts between policies:
  - P2's `replaced_by`/rule says "every other fee of the machine stays under the base fee rules". P3 and P5 retire base fee clauses, so this conflicts with them. → finding F-C5 (b).
  - Otherwise none.
- Scope exclusivity (from the charter alone): the prerequisite graph has exactly two weakly connected components, {P1, P2} and {P3, P4, P5}. With M=2, the only partition in which each tree is whole is task A = {P2 root, P1} and task B = {P5 root, P3, P4}. The two sets are disjoint and together cover all 5 policies. Each task's `charter_scope` will be compared after the reveal.

### rule_compute_equivalence
Check 2 was run over all 5 policies. The sweep above covers verbatim basis. Below, each compute expression is matched to its rule sentence in both directions.

- **P1:**
  - Item selection. "highest planogram request reference" ↔ `LATEST(... date_field='change_reference', change_type='add_item')`.
  - Units in 3 months. Rule: "fewer than three whole months separate its date from today". Compute: `SUM(... within_months=3)` over issued, returned and error.
  - `days_in_machine` = `MX(DAYS(add_date,NOW),1)`, which is "counted as one when … dated today".
  - Average = units/days×7/visits per week.
  - Trigger fraction = pct/100.
  - `largest_vend` = MAX over issued with no window ("at any time").
  - Demand-pattern ladder: 3 tiers, which match the 3 branches.
  - Wear: PPE / cutting_tools or abrasives / none.
  - Backup: active program at the ship-to; new-bin count > removal count; latest entry critical.
  - Exposure: open account (closed_date ''), status on_hold/in_collections or ≥2 returned in 12 months; active and exactly 1; else 1.
  - Lead: special / latest pricing line by effective date == discontinued_substitute / none.
  - Channel: shipped units to the ship-to in 3 months, >0 and ≥ units / >0 and < units / else.
  - Assembly: (1 + allowances) × interval × factors / trigger, with ceil only at the end (`int(-(-x//1))`).
  - **Mismatch:** the rule says "the item's latest bin entry on that program is flagged critical", but compute reads `XLATEST(..., event_type='vmi_bin_set', ...)`. Compute applies a filter the rule does not state. → F-C10.
- **P2:**
  - Model fee.
  - Interval = 7/visits.
  - Latest restock with visit_type scheduled; 0 when absent.
  - Callout ladder of 3 tiers. Division only happens when days > interval, so there is no zero-division.
  - Relief: Corbett par_change dated NOW, count > 0, with the category of the highest reference.
  - Technician discount: active program at the ship-to, ≥8 / ≥4 and <8.
  - Repeat: emergency fee lines within 3 months, ≥2 / ==1 / 0.
  - Result = `RND(MX(0, callout×(1−relief−discount+surcharge)),2)`. This matches "never below zero … rounded to the cent only at the end" (XF-7 OK).
- **P3:**
  - Bill month and month end = latest usage bill. Month days = first day to bill date, inclusive.
  - Net = Σ usage bills of the period − Σ shrink of the period.
  - Shutdown: latest plant_shutdown pause line on the program with no closed date; paused days clipped to the month; ≥ month days → 0 / >0 → (D−P)/D / else 1.
  - Months in service = `MONTHS(installed_date, month_end)`, ≤6 / ≤9 / else.
  - Stockout: emergency fee lines with billing_period = bill month.
  - Spend: Σ merchandise of credit_invoice_posted, txn_date within 12 months.
  - Site credit: program with no closed date, ≥20 / ≥8.
  - Rate share by active agreement tier.
  - Assembly order: tested minimum (shares, then 1−reliefs), then credit added to usage, then shortfall ≥0, then × pct × rate share, then round half up, then cap. This matches `MN(RND(...),cap)` (XF-3 and XF-7 OK).
  - **Issues:** the rule states no counting convention for "whole months in service" → F-C9. The two XLATEST reads (start date, end date) have no tie rule → F-C9.
- **P4:**
  - Weekday counts from Monday 1970-01-05: `(d//7)*5 + min(d%7,4) + 1`, which is weekdays to the date inclusive. Lead = difference.
  - Lead ladder: >2×model → 0 / >model → fee×model/lead / fee.
  - Concession: Strategic 1.0 / Net-Price or Cost-Plus 0.5.
  - Route: ship-to `route_deliveries_per_week`, ≥3 / ≥1.
  - Crew: program with no closed date, ≥20 / ≥8.
  - Result `RND(MX(0, lead_fee×(1−Σ)),2)`.
  - Equivalent in both directions.
- **P5:**
  - Months run = `MONTHS(installed, NOW)` ("same day … reached").
  - Fee basis, three methods:
    - Strategic: fee×(term−run)/term.
    - Net-Price / Cost-Plus: fee×(term/12 − (run//12+1))/(term/12).
    - Otherwise: fee.
  - Record share: shortfall lines within 12 months, 0 / ≤3 / ≤6 / else.
  - Unbilled install = max(0, model fee − Σ install lines on the machine).
  - Recovery rate: <12 → 1, <24 → 0.5, else 0.
  - Conversion: ≥8 / ≥4.
  - Site credit: ship-to suspended / active with no shipped lines in 3 months.
  - Faults: vend error credits within 6 months, ≥3 / ≥1.
  - Result `RND(MX(0, basis×share×(1−Σcredits)) + rate×unbilled, 2)`. This matches the rule's order and rounding.
  - **Issue:** the month-end convention of "same day of the month is reached" is not stated → F-C9.
- No compute binding invents a basis. No rule sentence is left without a compute binding (sweep plus reading). The exception is the eligibility sentences (scope, ramp-up, notice ≥3 months, item empty inside review), which are gates, not computed quantities.

### action_binding_and_uuids
- (target_tool, computes) pairs are unique: 5 tools, 5 computes, one policy each.
- Every docstring was read in full:
  - None names another tool or a sequence position.
  - None uses before/after/first/until about tool order. "applies from the next restock visit" is business timing.
  - None carries a concrete example value. Formats only: "letters VPC, a hyphen and six digits", YYYY-MM.
  - No tool body checks eligibility, prerequisites or amounts. Each body is `ctx.find` → `ctx.create`/`ctx.update`.
- uuid8s: `58ce1bb4`, `36839656`, `b04c8474`, `f4f2dbbd`, `4669343a`. They share no prefix or suffix, are not sequential, and none is reused. They pass.
- Docstring-effect sweep (XF-8). Three docstrings claim effects that are absent from the tool body → F-C8.

### prerequisite_graph
- Every policy has `prerequisite`. P1, P3 and P4 have `[]`.
- Edges:
  - E1: P2 → P1, `value_input`, gate `sizing_relief`.
  - E2: P5 → P3, `value_input`, gate `record_share`.
  - E3: P5 → P4, `value_input`, gate `unbilled_install`.
- Every `problem` is an extended policy id of this file. None is base and none is self. The graph is acyclic (depth 1).
- Each `policy_source` is verbatim in its own blocked rule (sweep).
- Form is `state` for all three edges, with no `fallback_reason` (correct for the state form).
- `condition` matches the sentence's strength:
  - E1 "selection of the item most recently added … when that item ran empty inside its start-up review months, carries a par change entry from Corbett dated the request day". This matches the sentence's "Where the item found empty … is the item most recently added … and still inside Corbett's start-up par review".
  - E2 "Every billing month … that carries a usage bill and is tested … carries the usage shortfall fee line its shortfall owes". This matches "every tested month billed on the machine".
  - E3 "A machine whose model carries an installation fee carries the installation fee line its installation owes". This matches "the installation fee owed for the machine".
- `resolved_by` is the depended-on policy's `target_tool` on every edge.
- The `effect` of each edge holds against compute:
  - E1: `review_count>0` moves `sizing_relief` from 0.0 to the category relief.
  - E2: `shortfall_lines` gains one row.
  - E3: `install_billed` rises, so `unbilled_install` falls.
- `gate` names a real binding of the blocked compute on every edge, and the kind is `value_input`.
- No authoring-viewpoint phrasing.
- The graph passes.

### prerequisite_sentences
Four-point test (check 6):
- **E1.** "Where the item found empty at the request is the item most recently added to the machine and still inside Corbett's start-up par review, the emergency restock fee is fixed only after that item's selection carries a par change entry from Corbett dated the request day."
  - Ordering connective: "only after".
  - It names a state, record-visible in `vending_planogram` (change_source corbett, change_type par_change, event_date).
  - It names no tool, id or snake_case token.
  - Its scope is conditional and matches `condition`.
  - Exactly one write in d5 creates a Corbett par_change: P1's tool. Other tools write `vending_transactions` or `vending_machines`.
  - Derivation (one reading): the sentence names a Corbett par change on that selection. The only rule that produces one is P1's "Corbett re-sizes the par of its selection and records a par change entry from Corbett dated the day of the review". So P1 is resolved first, then P2.
  - P1's rule does not restate it. No second wording exists.
  - PASS.
- **E2.** "The early removal fee on a notice is not fixed until the usage shortfall fee owed for every tested month billed on the machine stands on its records."
  - "not … until" plus a state (fee lines on the machine).
  - No tool or id.
  - Exactly one d5 policy books `usage_shortfall_fee`: P3. Every fee tool takes a free `fee_type` enum, but only P3's rule books that line.
  - Derivation: tested month billed → P3's "The month tested is the billing month of the machine's latest usage bill … booked as the usage shortfall fee line of that billing month".
  - P3's rule does not restate it.
  - PASS. See observation O5 on zero-fee months.
- **E3.** "The early removal fee on a notice is fixed only after the installation fee owed for the machine stands on its records."
  - "only after" plus a state.
  - The only writer is P4 ("bills … once, as an installation fee line of the installation month, and until that line stands the fee remains owed").
  - P4's rule does not restate it.
  - PASS.
- No rule carries a cross-problem order that grounds no declared edge. I swept every rule sentence for "before/after/until/first/only once": P1 "takes effect at the next restock visit" is not cross-problem; P4 "until that line stands the fee remains owed" is self-referential. No base sentence grounds an edge: the base `vending_removal_and_relocation` sentence that tied early removal to `vending_evt_fees` is retired by P5.

### override_declarations
Check 1 was run sentence by sentence against each `base_policy_refs` entry.

- **P1** (refs planogram_management, restock_and_shrink; overwrite []).
  - planogram S1 (customer changes; effect at the next restock visit): followed. The Corbett change also takes effect at the next visit.
  - S2 (special-item and capacity bounds): not touched, since a par change adds no item.
  - S3 (Corbett slow-mover removal at review; Corbett changes never count toward included changes): followed. The start-up review is an additional Corbett change and is excluded from the included count.
  - restock S1 (fill to par at the trigger level): followed. S2–S4: not touched.
  - `[]` is correct.
- **P2** (refs fees, site_minimum, restock_and_shrink).
  - fees S4 clause "an emergency restock carries emergency_restock_fee_usd" is declared retired.
  - "a fee whose model amount is 0.00 is never charged" is followed and restated.
  - fees S1–S3 and S5: not touched by P2's quantity.
  - restock S1 "emergency restock on request … within emergency_restock_response_hours hours": followed.
  - site_minimum: not touched.
  - **Defect:** `replaced_by` adds "every other fee of the machine stays under the base fee rules". That is false in this charter, because P3 and P5 retire base fee clauses → F-C5 (b).
- **P3** (refs fees, site_minimum). fees S1 is declared retired. Its `replaced_by` restates (a) ramp-up not tested, (b) credit-hold months tested, and (c) pooled sites under the site minimum rules. Its scope is "a machine whose model does not allow site pooling or which is the only machine … at its ship-to".
  - **Defect, out-of-scope gap:** consider a machine whose model allows pooling, at a ship-to where another active machine's model does not allow pooling.
    - Base `vending_agg_site_minimum` S3 says it "test[s] on its own".
    - It is outside P3's scope (it allows pooling and is not the only machine).
    - It is not a "pooled site".
    - The retired fees S1 was its only shortfall-fee formula (pct, half-up rounding, cap), and the `replaced_by` does not restate that formula for it → F-C5 (c).
  - Also: "each calendar month after the model's ramp-up months" drops the base anchor "full months following the installation month" → F-C9 member.
  - fees S3 (one monthly fee per type per month): followed.
- **P4** (refs fees, site_minimum, placement). placement S3 is declared retired. Its `replaced_by` restates the cellular-fee half. placement S1, S2 and S4 are followed (lead read from S2). Fees "0.00 never charged" is followed ("above 0.00"). No undeclared departure.
- **P5** (refs removal_and_relocation, fees, site_minimum). removal S4 and fees S5 (early-removal clause) are both declared retired. removal S1–S3 are followed (the customer's written notice; the notice period). S5 (relocation) is not touched.
  - **Defect:** `replaced_by` #1 and the verbatim rule sentence say a later notice "leaves the early removal fee to apply at removal under the base fee rules". The base fee rule's early-removal clause is the one P5's own overwrite #2 retires. The extended rule defers to a base clause its own overwrite retires → F-C5 (a).
- Anonymous intermediates, 0/1 multipliers and dropped branches were searched for. P3's `shutdown_share` = 0 is a declared tier that zeroes the minimum. It is not hidden, because P3's overwrite covers the month test. No dropped base branch was found beyond F-C5 (c). No author note calls the base output "wrong".

### factor_ladders
Charter-global structure. Whether each factor bears weight is per task.

**P1 (6 factors):**

| factor | effect | decides | tiers | cross | multi-source |
| --- | --- | --- | --- | --- | --- |
| demand_pattern_basis | method | interval_usage | 3 | — | tier 2 = vend rows AND add entry |
| category_wear_allowance | parameter | wear_allowance | 3 | — | no |
| storeroom_bin_backup | parameter | backup_factor | 3 | vmi | yes (new-bin rows, removal rows, latest entry) |
| consigned_exposure_limit | parameter | exposure_factor | 3 | credit | yes (account status OR returned-payment rows) |
| supply_lead_allowance | parameter | lead_allowance | 3 | pricing | tier 2 = add entry AND pricing line |
| order_channel_share | parameter | channel_factor | 3 | order | yes (order lines vs vend units) |

- Counts: 1 method, 5 parameter, 4 cross-difficulty factors.
- The bindings are disjoint. No `decides` is `result`. Every tier is stated in the rule.
- Distinct outcomes:
  - demand: max(avg, largest) / max(avg, starter×(1−t)) / avg. Distinguishing inputs exist pairwise.
  - wear: 0.5 / 0.25 / 0.
  - backup: 0.7 / 0.85 / 1.
  - exposure: 0.5 / 0.8 / 1.
  - lead: 0.5 / 0.25 / 0.
  - channel: 0.75 / 0.9 / 1.
- XF-1 independence: `channel_factor` reads `item_units`, a plain baseline binding, not a factor output. The demand pattern reads `avg_interval`, `days_in_machine` and `trigger_fraction` (plain). There are no factor-on-factor reads.
- Labels are honest. The demand method changes the formula's shape.
- Realism: these are plausible MRO vending par-sizing levers (lumpy demand, new-item settling, consumable safety stock, storeroom backup, credit exposure of consigned stock, special or substitute lead time, order-channel split). All pass.

**P2 (4 factors):**

| factor | effect | decides | tiers | cross |
| --- | --- | --- | --- | --- |
| startup_sizing_relief | parameter | sizing_relief | 3 | — |
| visit_schedule_callout | method | callout | 3 | — |
| stocksmart_technician_discount | parameter | tech_discount | 3 | vmi |
| repeat_request_surcharge | parameter | repeat_surcharge | 3 | — |

- startup_sizing_relief: 1.0 / 0.5 / 0.
- visit_schedule_callout: 0 / fee×I/d / fee. Pairwise distinct on the reachable domain: at d>2I the formula gives <fee/2, not 0; at d≤I the formula gives ≥fee.
- stocksmart_technician_discount: 0.5 / 0.25 / 0.
- repeat_request_surcharge: 0.25 / 0.5 / 0 (0.5 for two or more lines, 0.25 for exactly one).
- Counts: 1 method, 3 parameter, 1 cross-difficulty factor (vmi).
- No factor in P2 is multi-source on its own. The tier conditions are single-record. Multi-source is met per task via P1.
- Independence holds. Assembly happens only in `result`.

**P3 (6 factors):** plant_shutdown_share (method, vmi), service_months_share (parameter), stockout_month_relief (parameter), account_spend_relief (parameter, credit), site_program_credit (parameter, vmi), contract_rate_share (parameter, pricing).
- Bindings are disjoint. Every tier is in the rule. The values are distinct (0.5/0.75/1, 0.2/0.1/0, 0.2/0.1/0, 1000/500/0, 0.5/0.75/1).
- Multi-source: plant_shutdown_share (program row plus pause line).
- **Defect: plant_shutdown_share is not a real method ladder.**
  - Tier 2's method, "prorated by the share of the month's calendar days not paused" = (D−P)/D, gives exactly tier 1's outcome (0) when P = D.
  - It gives exactly the fall-through's outcome (1) when P = 0.
  - So the three tiers are one method, proration by unpaused days, evaluated over its whole domain. The ladder is one tier written as three, and the label "method" names no change of algorithm.
  - P3 therefore has 0 honest method factors, below the bound of 1 → F-C11.
- Observation O7: `month_first`/`month_days` are used only by this factor but are missing from its `bindings`.

**P4 (4 factors):** installation_lead_basis (method; 0 / fee×L/lead / fee, pairwise distinct), agreement_install_concession (parameter, pricing; 1.0/0.5/0), route_crew_credit (parameter, order; 0.3/0.15/0), stocksmart_crew_credit (parameter, vmi; 0.25/0.1/0).
- Counts: 1 method, 3 parameter, 3 cross-difficulty factors. Not multi-source on its own.
- All pass structurally.

**P5 (6 factors):** agreement_fee_basis (method, pricing; three distinct formulas), minimum_usage_record (parameter; 0.6/0.75/0.9/1, 4 tiers), installation_recovery (parameter; 1/0.5/0 × unbilled), stocksmart_conversion_credit (parameter, vmi; 0.25/0.15/0), ship_to_site_credit (parameter, order; 0.5/0.2/0; multi-source = ship-to status AND order lines), machine_fault_credit (parameter; 0.3/0.1/0).
- Bindings are disjoint. `months_run` is shared by two factors, so it is plain (correct).
- Observation O7: `term_months` is used only by fee_basis but is absent from its bindings. Its text is inside the factor's ladder sentence.
- Realism notes: O2 (fee-basis ordering across agreement tiers), O8 (quiet-site condition).

### findings
Charter-global findings. Each says which task file carries the demonstration.

- **F-C11 — SOURCE-FACTOR RED (XF-11, method tiers coincide).**
  - Symptom: P3 `plant_shutdown_share` labels as `method` a ladder whose three tiers are one formula.
  - Root cause: tier 1 ("not tested, share zero") and the fall-through ("taken in full") are the end values of tier 2's proration (D−P)/D, at P=D and P=0.
  - Evidence:
    - The rule sentence "when the paused days cover every calendar day of the month the month is not tested and its minimum share is zero; when some but not all days of the month are paused the minimum is prorated by the share of the month's calendar days not paused; otherwise the minimum is taken in full".
    - compute `shutdown_share: "0.0 if paused_days >= month_days else ((month_days - paused_days) / month_days if paused_days > 0 else 1.0)"`. `paused_days` is clipped to [0, D] by `MX(0, DAYS(MX(pause_first,month_first), MN(pause_last,month_end)) + 1)`.
  - Consequence: on every input, `shutdown_share == (D−P)/D`, so a reader who only ever prorates is always right. No tier selects another algorithm, and P3's computation carries 0 honest `method` factors (the bound is ≥1).
  - Complete class list (every method ladder in the charter, pairwise table):
    - P1 demand_pattern_basis is distinct (input LV<avg, days<28, starter×0.75>avg separates T2 from T3).
    - P2 visit_schedule_callout is distinct (d=6, I=3.5: T2 = 35 ≠ T3 = 60; d=8: T2 = 26.25 ≠ T1 = 0).
    - P4 installation_lead_basis is distinct (same shape as P2).
    - P5 agreement_fee_basis is distinct (run=9, term=36: 0.75 / 0.667 / 1).
    - **Only P3 plant_shutdown_share is a member.**
  - Affected: P3 `factors[plant_shutdown_share]`, its rule sentence, compute `shutdown_share`. Bears on task 1.
- **F-C5 — SOURCE-POLICY RED (XF-5, overwrite scope and deferral). All members:**
  - (a) P5 overwrite #1 `replaced_by`, carried verbatim as rule sentence 2: "…while a notice received later leaves the early removal fee to apply at removal under the base fee rules when removal falls before the end of the minimum term". The base fee rule's early-removal clause ("A machine removed before min_term_months … carries early_removal_fee_usd once") is retired by P5's own overwrite #2. So the rule defers to a clause its own overwrite retires.
  - (b) P2 overwrite `replaced_by`, carried verbatim as rule sentence 2: "…and every other fee of the machine stays under the base fee rules". In the merged charter, two other fees are not under the base fee rules:
    - the usage shortfall fee of a machine tested on its own, retired by P3;
    - the early removal fee of a notice with ≥3 months remaining, retired by P5.
    Taken at its word, P2's sentence and P3's or P5's rule reach different conclusions for the same fee. The demonstration is in task 1.
  - (c) P3 overwrite `replaced_by`, carried verbatim as rule sentence 1. Its scope ("a machine whose model does not allow site pooling or which is the only machine of the customer at its ship-to …") plus "a pooled site stays under the site minimum rules" leave out a pooling-capable machine at a ship-to with another active machine whose model does not allow pooling. Base `vending_agg_site_minimum` S3 makes that machine "test on its own". Its only fee formula (pct, half-up, cap) was the retired fees S1. Nothing in force states its shortfall fee. Example: a Coil 40 beside a Locker 12 at one ship-to has no fee rule. Neither task's world has such a site (task 1: VP-562218 is alone at ST-52611), so no task consequence.
  - Bears on task 1 (b demonstrated); (a) and (c) are charter-only.
- **F-C9 — SOURCE-POLICY RED (XF-9, unstated month-count and tie conventions). All members:**
  - Month-count conventions:
    - P3 "the machine's whole months in service from its installation date to the date of the month's latest usage bill". No counting convention is stated, and the end date is always a month's last day. For an installation on the 29th–31st, compute `MONTHS(installed_date, month_end)` and the rule can disagree, and `service_months_share` sits at tier boundaries 6 and 9.
    - P3 `replaced_by`/rule "each calendar month after the model's ramp-up months is tested". The base anchor "full months following the installation month" is dropped.
    - P5 "a month counting once the same day of the month is reached". The rule does not say what happens when the installation day does not exist in the notice month (installed on the 31st).
    - P5 scope "while at least three whole months of the minimum term remain". The convention is not stated.
    - P1 "an item whose add entry is three or more whole months old".
  - Rolling-window sentences "fewer than N whole months separate …". The same month-end gap applies to each:
    - P1 units (3);
    - P1 returned payments (12);
    - P1 order units (the "three months ending today" of the units sentence);
    - P2 repeat lines (3);
    - P3 spend (12);
    - P5 shortfall lines (12);
    - P5 site shipments (3);
    - P5 faults (6).
  - Same-day ties (which row LATEST/XLATEST keeps):
    - P3 "the latest plant shutdown pause line recorded". Two lines can be recorded the same day, and `pause_first`/`pause_last` are two separate XLATEST reads that could come from different lines.
    - P1 "the item's latest bin entry on that program".
    - P1 "latest contract price line for the item … by effective date".
  - Not demonstrable on either task's world: installs on the 6th and 8th; frozen dates the 7th and 14th; no same-day ties. Charter-only.
- **F-C10 — SOURCE-POLICY RED (XF-10, a compute filter not in the rule).**
  - P1 `bin_critical: XLATEST('vmi','vmi_bins','critical_item', event_type='vmi_bin_set', …)` versus the rule "the item's latest bin entry on that program is flagged critical".
  - A `vmi_bin_removed` entry is a bin entry too. The rule itself distinguishes "new-bin entries" from "bin removal entries".
  - So when the latest entry is a removal and new bins still outnumber removals, the rule reads its flag while compute reads the latest set entry.
  - This is the only class member found.
  - No task consequence: in task 0, AB-53318 has one new_bin entry and no removal.
- **F-C8 — SOURCE-POLICY RED (XF-8, a docstring effect absent from the body). All members:**
  - `place_emergency_restock_request_36839656`:
    - "one emergency restock fee line is booked … for the current billing month". The body books whatever `billing_period` is passed.
    - "The fee line appears … on the month's program billing". The body posts no credit invoice.
  - `charge_month_shortfall_fee_b04c8474`: "it appears on the machine's fee history and on that month's program billing". The body posts no invoice.
  - `charge_installation_fee_f4f2dbbd`: "it appears on the machine's fee history and program billing". The body posts no invoice.
  - Why "program billing" is a real effect:
    - Base `events.vending_fee_charged.triggers: credit:credit_invoice_posted {source_type: vending_program_fee}`.
    - Both seeds carry one such invoice for every seeded fee line. Task 1: INV-5630100, INV-5630311, INV-5630522, INV-5607699, INV-5631544, INV-5607183, INV-5607398. Task 0: the 2026-09-02 45.00 and 2026-10-05 8.00 invoices.
    - So "program billing" is a real, separate record in this world, and the three bodies never create it.
  - The removal tool makes no such claim. It omits the same trigger, which is an observation.
  - Bears on both tasks (no scored-value consequence found on either world).

**Observations (not grounds for rework):**
- **O1.** P2 sets its "on-site threshold" at 8 visits a month, which is exactly the StockSmart Twice-Weekly tier. P3 and P4 use "on-site threshold" = 20 under the same words. The Twice-Weekly tier thus earns P2's "on-site technician discount".
- **O2.** P5 `agreement_fee_basis`: for every reachable input, the Net-Price/Cost-Plus basis (future whole contract years) is ≤ the Strategic basis (unrun months pro rata). In a final contract year it is 0 against a positive Strategic figure. This inverts the tier order the charter gives Strategic everywhere else (P3 rate share 0.5 < 0.75; P4 concession 1.0 > 0.5). It is a realism concern. No rule contradiction is demonstrated.
- **O3.** P1 asserts "Corbett issues these references in sequence". `resize_selection_par_58ce1bb4` issues `VPC-` + hash-derived digits, which are not sequential. P2's "the one carrying the highest planogram request reference" among same-day Corbett par changes would then not be the latest. Neither world has two such changes.
- **O4.** P2 "days since the last scheduled visit" is read from restock entries. A scheduled visit that loads nothing leaves no entry.
- **O5.** P3 and P2 do not say whether a zero fee (credited usage ≥ tested minimum; callout 0) is booked as a 0.00 line. Lines are counted later: P3 counts emergency lines, P5 counts shortfall lines. The E2 state "usage shortfall fee owed for every tested month" depends on that.
- **O6.** The baseline sentences are stated unconditionally inside rules that later replace them: P2 "The emergency restock callout is the model's emergency restock fee"; P4 "The installation fee is the model's installation fee"; P5 "The early removal fee is the model's early removal fee". The design accepts this pattern.
- **O7.** Factor `bindings` lists omit quantities that only that factor uses: P3 `month_first`, `month_days`; P5 `term_months`.
- **O8.** P5 quiet-site credit ("no order line was shipped in the three months") ignores StockSmart deliveries to the same ship-to. Task 1 has an example.
- **O9.** P4 counts weekdays with no holidays, against the base wording "install_lead_business_days business days".

## closing_checklist
Written 2026-10-17, after both reveals. The charter and tool hashes are unchanged from the freeze: `f88c4ed39bbafa55…` and `197f4869364f5d76…`.

- [x] Task files 0.md and 1.md correspond one to one with tasks 0 and 1. `_difficulty.md` sits alongside them. This is revision_1, with no older revisions.
- [ ] Every comparison carries a PASS:
  - task 0: PASS;
  - task 1: RED (SOURCE-FACTOR T1-F1, T1-F2; SOURCE-POLICY T1-F3).
- [x] Coverage and scope:
  - All 5 extended policies are covered.
  - Scopes: task 0 = {P1, P2}, task 1 = {P3, P4, P5}. They are disjoint, and each spans its whole tree.
  - Task tools and GT are closed. Each tool has its own frozen uuid8.
- [x] Trees and graph:
  - Task 0 has 1 prerequisite problem and 1 value_input edge.
  - Task 1 has 2 prerequisite problems and 2 value_input edges.
  - Each tree has one user-owned write.
  - The difficulty-wide graph is a DAG with no cross-task edges.
- [ ] Factors. Each computation declares a self-sufficient baseline and 4–6 factors with ≥2 parameter and ≥1 *honest* method. P3 fails (F-C11 / T1-F1). Every factor bears weight against an honest baseline, and each baseline alone gives a definite number ≠ gold. The ladder and seed realism checks fail at T1-F2.
- [ ] Gates on the final form: not re-run. The difficulty does not close, so a rework must change the charter and seed first. The snapshot in the brief (7/7 green) stands for this form only.
- **Difficulty does NOT pass the source-layer audit.**

### open charter REDs (each lists all of its members; full text under ### findings)
- **F-C11 (XF-11).** P3 `plant_shutdown_share` is the only member. P1 demand_pattern_basis, P2 visit_schedule_callout, P4 installation_lead_basis and P5 agreement_fee_basis were checked and pass.
- **F-C5 (XF-5).** Three members:
  - (a) P5 replaced_by #1 / rule sentence 2, "…under the base fee rules", which defers to a clause its own overwrite #2 retires;
  - (b) P2 replaced_by / rule sentence 2, "every other fee of the machine stays under the base fee rules", which contradicts P3 and P5 (demonstrated in task 1);
  - (c) P3 replaced_by / rule sentence 1, whose scope gap leaves a pooling-capable machine at a mixed site with no fee rule.
- **F-C9 (XF-9).** Members by group:
  - Month counts:
    - P3 "whole months in service";
    - P3 "after the model's ramp-up months";
    - P5 "a month counting once the same day of the month is reached";
    - P5 "at least three whole months of the minimum term remain";
    - P1 "three or more whole months old".
  - Rolling windows ("fewer than N whole months separate"):
    - P1 units (3);
    - P1 returned payments (12);
    - P1 order units (3);
    - P2 repeat lines (3);
    - P3 spend (12);
    - P5 shortfall lines (12);
    - P5 site shipments (3);
    - P5 faults (6).
  - Same-day ties:
    - P3 "latest plant shutdown pause line recorded" (two separate XLATEST reads);
    - P1 "item's latest bin entry";
    - P1 "latest contract price line … by effective date".
- **F-C10 (XF-10).** P1 `bin_critical` `event_type='vmi_bin_set'` filter, absent from the rule ("latest bin entry"). This is the only member.
- **F-C8 (XF-8).** Members:
  - `place_emergency_restock_request_36839656`: "for the current billing month", and "on the month's program billing";
  - `charge_month_shortfall_fee_b04c8474`: "on that month's program billing";
  - `charge_installation_fee_f4f2dbbd`: "program billing".
  No body posts the credit invoice that base `vending_fee_charged.triggers` declares and that both seeds carry.
- Task-level seed RED, not charter: T1-F2. The only other seeded vend-error row in either world is task 1's VE-562140 (21.80 ≤ 75.00 desk limit), which is valid. Task 0 has none.

VERDICT revision_1: task0=PASS task1=RED[SOURCE-FACTOR(T1-F1 F-C11 method-ladder; T1-F2 seed vend-error credits),SOURCE-POLICY(T1-F3 F-C5b)] charter=F-C5,F-C8,F-C9,F-C10,F-C11

## revision_2

## charter_global_frozen (revision_2)
- Frozen: 2026-10-17, before any revision_2 task GT was revealed. Same auditor as revision_1. Revision_1's text above is left untouched.
- Entry gate:
  - `tail -1 tasks/d5_vendpoint_usage_and_machine_billing/worklog.md` = `REWORK round 2: gates 7/7 green`.
  - `/tmp/erl0068_coord/snapshot.sh d5_vendpoint_usage_and_machine_billing 2` printed all 7 gates OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. The snapshot is saved at `.audit_views/policy/d5_vendpoint_usage_and_machine_billing/r2/gates.txt`.
  - Input is complete.
- Hashes (r2):

| file | sha256 |
| --- | --- |
| charter `vending.extended.yaml` | `eaf984322425ff28250df9f2fa8410a2b83e881c863d7fcd586df6570cf5962e` |
| `task_tools.py` | `e44d5475b0218e39e4e7d8879cde77f7e1adcdcd11908dc19b11e1ac7eb3d00d` |
| `r2/task0.view.json` | `77775d43692f47217f0a35febf1846dd86f287871033155e99d5ea3980e813cb` |
| `r2/task1.view.json` | `dac502e96ff03efc47665a2f7419a828e971de0f28c248790acfd545ef82ac68` |

  The charter and tool hashes both changed, so every charter-global section is re-derived in full below.
- contamination_disclosure: I know the revision_1 GT of both tasks from my revision_1 reveal. I opened no revision_2 task JSON, plan.md or worklog.md (other than its tail line) before the freezes. The `_masked_keys` are the same as r1.
- Base copy: verbatim. All top-level base keys are `==` to blueprint/products/vending.yaml.
- Scratch sweep (XF-6): all 5 policies are clean. Every compute_basis quote, baseline.rule sentence, replaced_by, superseded_clause and policy_source sits verbatim where it belongs.

### policy_conflict_scan (r2)
- Policies, tools, owners and edges are the same as r1: P1 → none; P2 ← P1; P5 ← P3, P4.
- The components are still {P1, P2} and {P3, P4, P5}, so the scopes are still forced disjoint and together complete.
- **F-C5 (b) is closed.** P2's replaced_by/rule now reads "the relocation, model swap, replacement badge card and planogram change fees named with it stay under that base sentence". That is exactly the rest of base fees S4, and it no longer conflicts with P3 or P5.
- No new conflict:
  - P2 and P3 now both state that a 0.00 fee books no line.
  - P3's stockout relief still reads only emergency lines of the tested (past) month.

### rule_compute_equivalence (r2)
Changed parts were re-checked both ways. Unchanged parts were re-read and still hold as written in revision_1.

- **P1:**
  - New general sentence: "Whole months between two dates are counted as the difference in calendar months, less one when the day of the month of the later date is before the day of the month of the earlier date; a record counts in a stated number of months ending today when fewer whole months than that number … separate its date from today". It governs `within_months`, the review age and the returned-payment window.
  - `bin_critical` now reads `XLATEST(..., date_field='change_reference', event_type='vmi_bin_set')`, matching "latest bin set entry …, new bin or par change, which is the one carrying the highest bin request reference". **F-C10 is closed.**
  - The lead allowance now counts substitute lines (>0) and removal lines (==0), matching "carries … a contract price line written as a Corbett-approved substitute … and no removal line". The pricing tie member is removed.
- **P2:**
  - The month convention is added.
  - "fee lines are counted by line date".
  - "A request whose fee comes to 0.00 books no fee line".
  - The thresholds are renamed twice-weekly/weekly (8 and 4), and compute matches.
- **P3:**
  - The scope sentence is rewritten (see override_declarations).
  - The month convention is added.
  - "all usage bills of a month carrying the month's last day as their date".
  - "a month whose shortfall fee comes to 0.00 carries no line".
  - New method `contract_usage_basis`:
    - Strategic: MX(net, bills in 2 months ending today − the month's own bills).
    - Net-Price / Cost-Plus: MX(net, bills in 3 months ending today / 3).
    - Otherwise: net.
    This matches the rule sentence both ways.
  - Shutdown tiers:
    - paused ≥ 10 days → (D−P)/D;
    - 1–9 days → 0.95;
    - otherwise → 1.
    The pause line is picked by the highest `activity_reference`, matching "the plant shutdown pause line with the highest pause reference".
  - `contract_rate_share` is removed. The result is `MN(RND(shortfall×pct/100,2),cap)`, matching "rounded half up … only then capped".
- **P4:** "Holidays falling on weekdays are counted as weekdays" is added. Compute is unchanged and still consistent.
- **P5:**
  - Months run and scope ("at most the minimum term months less three") use the general convention.
  - Fee-basis methods are swapped: Strategic now gets whole later contract years; Net-Price/Cost-Plus get unrun months pro rata.
  - The record thresholds are 2 and 5.
  - The idle-site credit is 0.35.
  - The quiet-site tier now also requires `site_program == None`.
  - Compute matches the rule on every line.
- Equivalence passes.
- Limitation: whether the DSL's `MONTHS()`/`within_months` implement the newly stated calendar convention cannot be read inside my read domain, because the DSL lives under skills/. Neither world has an input where plausible conventions diverge. → O13.

### action_binding_and_uuids (r2)
- The same 5 (target_tool, computes) pairs and uuid8s as r1. Unique, and not derived from each other.
- Docstrings:
  - The "program billing" and "current billing month" claims are gone.
  - Every remaining claim exists in its body.
  - `resize_selection_par_58ce1bb4` now claims "the next planogram request reference in sequence, one above the highest planogram request reference on record". The body computes `max(VPC numbers)+1`, so the claim holds. **F-C8 is closed. O3 is closed.**
- No ordering words, tool names or example values. No body validates anything.
- O10: the bodies still omit the credit invoice that base `vending_fee_charged.triggers` declares. The docstrings no longer claim it.

### prerequisite_graph and prerequisite_sentences (r2)
- E1, E2 and E3 are byte-identical to r1: policy_source, condition, form state, kind value_input, and gate.
- The gates exist in compute. The graph is acyclic. Each sentence is still verbatim in its blocked rule.
- The four-point test, single-writer analysis and derivation of revision_1 carry forward, because these sentences and the writing tools are unchanged.
- E2's "owed" is now definite: a month whose fee comes to 0.00 carries no line, so zero-fee months owe nothing. O5 is closed.

### override_declarations (r2)
- **P2:** retires fees S4's emergency clause. Its replaced_by keeps the four other fees of that same sentence under it. **F-C5 (b) is closed.**
- **P3:** retires fees S1. The new scope is "a machine that is not tested as part of a pooled site under the site minimum rules, and only for such a machine". That covers every non-pooled machine, including a pooling-capable machine at a site with a non-pooling one.
  - It restates the ramp-up anchor: "the model's number of full calendar months following the installation month … the installation month and the ramp-up months are not tested".
  - **F-C5 (c) is closed.**
- **P5:** replaced_by #1 now says "for a notice received later the model's early removal fee applies once at removal when removal falls before the end of the minimum term". It no longer defers to the base fee rules. **F-C5 (a) is closed.**
- **P1, P4:** as in r1. No undeclared departure.

### factor_ladders (r2)
- P1, P2 and P4 have the same factor structure as r1. Changes:
  - P2 technician tiers are renamed (values 0.5/0.25/0 kept).
  - P1 lead tier 2's condition is reworded.
- **P3** (6 factors):

| factor | label | tiers | cross | notes |
| --- | --- | --- | --- | --- |
| contract_usage_basis | method | 3 | pricing | three distinct shapes; pairwise distinct (e.g. Aug 623.20 vs 3-month average 590.98 vs net 511.65) |
| plant_shutdown_share | parameter | 3 | vmi | multi-source; **T1 is the formula (D−P)/D, T2 the fixed 0.95, T3 1** |
| service_months_share | parameter | 3 | — | |
| stockout_month_relief | parameter | 3 | — | |
| account_spend_relief | parameter | 3 | credit | |
| site_program_credit | parameter | 3 | vmi | |

  - The bindings now include `month_first`/`month_days`, so O7 is closed for P3.
  - Counts: 1 honest method, ≥4 honest parameters. **F-C11 is closed.** The P3 method ladder is real.
  - XF-1: site credit adds to "the usage tested", which baseline.rule defines ("The usage tested is the month's net usage"). No binding reads another factor's binding.
- **P5:**
  - agreement_fee_basis (method) has its tiers swapped. Strategic is now never above Net-Price/Cost-Plus, so **O2 is closed**.
  - minimum_usage_record: 0.6 / 0.75 (1–2) / 0.9 (3–5) / 1.
  - ship_to_site_credit: 0.35 / 0.2 / 0. It is multi-source (ship-to status, order lines, vmi program).
  - The bindings include `term_months`, so O7 is closed.
- Label sweep over every `parameter` factor (does any tier compute rather than select a number?):
  - P1 wear, backup, exposure, lead, channel: numbers.
  - P2 relief, technician, repeat: numbers.
  - P3 months, stockout, spend, site: numbers. **P3 plant_shutdown_share: T1 is a computation.**
  - P4 concession, route, crew: numbers.
  - P5 record, recovery (rate numbers), conversion, site, fault: numbers.
  - **The only member is P3 plant_shutdown_share** → F2-C1.
- XF-11 pairwise table for method ladders:
  - P1 demand: distinct.
  - P2 callout: distinct.
  - P3 contract_usage_basis: distinct.
  - P4 lead: distinct.
  - P5 fee basis: Strategic 2/3 vs Net-Price 27/36 vs 1 at run=9. Distinct.
  - No member.

### XF recipe re-check (r2, every point × every policy)
1. **Independence:** passes for P1–P5. No binding reads another factor's binding. Single-factor quantities are now in that factor's bindings.
2. **Assembly:** generic sentences, unchanged in kind. These are placement-only kinds, not a member.
3. **Order:** P3 order stated; P5 stated; P1, P2 and P4 commutative or single multiplier. Passes.
4. **"As another policy figures it":** none. P2 and P3 refer to base sentences only for out-of-scope fees.
5. **Overwrites:** passes, as above.
6. **Verbatim:** passes (sweep).
7. **Rounding:** passes for all 5.
8. **Docstrings:** passes. F-C8 is closed.
9. **Edges:** every r1 F-C9 member is closed:
   - P3 months in service: convention, and "counted from its installation date to the date of the month's usage bills".
   - P3 ramp-up anchor.
   - P5 months run and scope.
   - P1 review age.
   - All windows: P1 units, returns ("counted by return date"), order units; P2 lines ("by line date"); P3 spend ("by invoice date") and the 2- and 3-month bill windows; P5 lines, shipments and faults ("by line/ship/credit date").
   - P3 pause tie, by highest reference.
   - P1 bin tie, by highest reference.
   - The P1 pricing tie is gone.
   - Absent-record, zero-division, negative-lag and None branches all fall through to the fall-through tier. Passes.
10. **Filters:** passes. F-C10 is closed. The P5 `site_program` filter is stated.
11. **Method shape:** passes. See the label finding F2-C1, which is the inverse (a parameter label on a computed tier).
12. **Cross-record windows:** P3's "prior month's usage" is defined through a today-anchored window and stated so in the rule. Not a member; see O11.
13. **Seeded rows of other categories:** see task 1, T1-F4. In both seeds only `vmi_activity.vmi_pause_recorded.activity_reference` deviates from its charter format: `VPS-…` where vmi `events` says "Pause reference (VPA-...)". P3 now selects the pause line by that reference. Every other cross-category reference prefix was checked by script and conforms: credit INV/ACH/ADB/WIR/EDI/RTN/CHG; order SO/PL/NONE; pricing SPQ/PCH; vmi VBR/VV.

### findings (r2)
- **F2-C1 — SOURCE-FACTOR RED (mislabelled effect).** The only member is P3 `plant_shutdown_share`.
  - It is labelled `parameter`.
  - Rule: "when the paused days in the month are at least the long-shutdown days, the share is the month's calendar days not paused divided by the month's calendar days; when the month has at least one but fewer paused days than the long-shutdown days, the share is the short-shutdown share; otherwise the share is one".
  - Ladder tier 1 is `value: "(month_days - paused_days) / month_days"`.
  - Demonstration: under T1 the share depends on the input (10 paused days of 30 → 0.667; 15 → 0.5). Under T2 it is a fixed number (0.95 for any 1–9 days). The tiers change how the quantity is computed, not only which number is used, so the `parameter` label is dishonest.
  - Count bounds still hold whichever label is right (1 or 2 methods, ≥4 parameters).
  - Bears on task 1 (charter-level only, no numeric consequence).
- **Charter observations still open:**
  - O4: P2 "last scheduled visit" is read from restock entries.
  - O6: unconditional baseline sentences. P3 now also has "The usage tested is the month's net usage."
  - O8 (displaced): P5's quiet tier now excludes sites with an open StockSmart program, but the idle tier ("ship-to whose status is suspended") does not. A ship-to suspended for 12 months without catalog orders but served by an open StockSmart program and an active machine is "idle".
  - O10: tool bodies omit the base credit-invoice trigger.
  - O11 (new): P3 Strategic "the prior month's usage being the usage bills dated in the two months ending today less the month's own usage bills". On a month-end "today" (e.g. 10-31, before October is billed), the 2-month window drops the prior month's bill, so "prior month's usage" is 0 rather than the prior month. Rule and compute agree; the name misleads.
  - O12 (new): P3 shutdown cliff. 9 paused days give 0.95; 10 give 0.667 of a 30-day month.
  - O13 (new): DSL equivalence of the stated month convention cannot be verified within the read domain.
- **Closed:**
  - REDs: F-C5 (a), (b) and (c); F-C8; F-C9, all members; F-C10; F-C11.
  - Observations: O1, O2, O3, O5, O7, O9.

### findings (revision_2, post-reveal additions — written after both r2 freezes)
- O14 (P3/P5 E2 past-month "owed" depends on the test day) and O15 (rounding mode unstated in P2, P4 and P5; the DSL rounds floats). Both are observations; see `1.md` r2.

## closing_checklist (revision_2)
- [x] The task files correspond one to one. revision_1 text is preserved and revision_2 is appended in all three files.
- [ ] Every comparison PASSes: task 0 PASS; task 1 RED (T1-F4, T1-F5).
- [x] Scopes are disjoint and together complete. Tools and GT are closed. Each uuid8 is independent.
- [x] Trees: 1–2 prerequisite problems, ≥ max(n−1, 1) value_input edges, one user write each, and a DAG.
- [ ] Factors: the counts hold and every factor bears weight against an honest baseline, with baseline numbers ≠ gold. The checklist fails on a dishonest label (F2-C1) and an unproducible seeded vmi reference (T1-F4).
- [ ] Gates on the final form: the coordinator's r2 snapshot shows 7/7 OK. The difficulty does not close.
- **Difficulty does NOT pass the source-layer audit.**
- Round-1 REDs, all closed: F-C5 (a), (b) and (c); F-C8; F-C9 (every member); F-C10; F-C11; T1-F1; T1-F2; T1-F3.
- Open:
  - charter **F2-C1**, mislabelled effect. The only member is P3 `plant_shutdown_share`.
  - task-level **T1-F4**, XF-13. The only members are the two seeded `vmi_activity` pause rows VPS-556120 and VPS-556418.

VERDICT revision_2: task0=PASS task1=RED[SOURCE-FACTOR(T1-F4 XF-13 seed pause refs; T1-F5 F2-C1 mislabelled shutdown share)] charter=F2-C1

## revision_3

## charter_global_frozen (revision_3)
- Frozen: 2026-10-17, before any revision_3 task GT reveal. Same auditor. The revision_1 and revision_2 text above is left untouched.
- Entry gate:
  - The worklog's last line is `REWORK round 3: gates 7/7 green`.
  - `/tmp/erl0068_coord/snapshot.sh d5_vendpoint_usage_and_machine_billing 3` printed all 7 gates OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. The snapshot is saved at `.audit_views/policy/d5_vendpoint_usage_and_machine_billing/r3/gates.txt`.
  - Input is complete.
- Hashes (r3):

| file | sha256 |
| --- | --- |
| charter | `c21024a6a63e40063485fe6b6eff4d455ae3129f4253489fbb2433d62df63397` |
| tools | `30f416c50755e5d091e831b70a86ff3c0308f7a7df2e49675b371ba5bd00c44f` |
| `r3/task0.view.json` | `e8ec698b254e09b074d681c868d300069b7ea8eff04407a47b069582327d9ac4` |
| `r3/task1.view.json` | `dce5adc4e58bfda9656dea747261bee40ecfe0555d792692e12ff329a345773c` |

  Every charter-global section is re-derived in full below.
- contamination_disclosure: I know the r1 and r2 GT of the earlier designs. That design is replaced: the policies, tools and scored writes differ. No r3 task JSON, plan.md or worklog.md (beyond its tail line) was opened before the freezes.
- Base copy: verbatim (all top-level base keys `==`).
- Scratch sweep (XF-6): clean on all 5 policies.

### policy_conflict_scan (r3)
New policy set:

| id | subject | computes | tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| P1 vending_ext_startup_par_review | selection_set | par_qty | resize_selection_par_58ce1bb4 (agent) | [] |
| Q2 vending_ext_startup_item_return | item_returned | unit_credit | return_startup_item_units_bfc1c22c (user) | P1 (value_input, fill_tier) |
| Q3 vending_ext_retired_item_vend_credit | vend_error_credited | credit_amount | credit_retired_item_vends_2f4f7780 (agent) | [] |
| Q4 vending_ext_substitute_placement | selection_set (Corbett add) | par_qty | place_substitute_selection_72f4b244 (agent) | Q3 (value_input, retired_units) |
| Q5 vending_ext_substitute_par_setting | selection_set (customer par change) | par_qty | set_substitute_selection_par_5d8137ae (user) | Q4 (value_input, interval_usage) |

- **Cross-category triggers (the coordinator's check).** The tools write `vending_selection_set`, `vending_item_returned` and `vending_vend_error_credited`. All three have `triggers: []` in base `events`. They also update `vending_machines.machine_stock_value`, which is a holding field and emits no event. No tool writes `vending_fee_charged`, `vending_usage_billed` or any event that triggers another category. PASS.
- Three policies write `vending_selection_set`. Each writes a different kind of row, so no two claim the same row:
  - P1: Corbett par_change.
  - Q4: Corbett add_item.
  - Q5: customer par_change.
- Cross-policy reads:
  - Q2's selection par reads P1's entry. Declared.
  - Q4's units read Q3's credit. Declared.
  - Q5's newest item and starter par read Q4's add. Declared.
  - P1 reads add entries only. Q4's Corbett add would become "the item most recently added" for P1 and Q2 on a machine where Q4 has run. That is consistent with their rules ("the item whose add entry … carries the highest planogram request reference"). No rule orders P1 against Q4. Within one task they never meet.
- Components are {P1, Q2} and {Q3, Q4, Q5}, so the scopes are forced disjoint and together complete.

### rule_compute_equivalence (r3)
- **P1:** unchanged from r2 (equivalent).
- **Q2:**
  - Item, add date and category come from the highest add reference.
  - Current price: latest pricing line by effective date for the sku, else the latest vend price by `vended_at`.
  - Ledger: loaded − vended + returned + errors − withdrawn − shrink, over all records.
  - Selection par: latest par for the sku by change reference.
  - Fill tier: ≥ par → price − 0.75 (≥0); ≥ 0.8 × par → × 0.95; else price.
  - Trial: DAYS(add, NOW) ≥ 60 / ≥ 30.
  - Return lines within 3 months: ≥3 / ≥1.
  - Handling: PPE / cutting_tools or abrasives.
  - Result `RND(shaped × shares, 2)`.
  - Matches the rule both ways.
- **Q3:**
  - Retired sku and category come from the highest removal reference.
  - Ledger as in Q2. Shortfall = max(0, −ledger).
  - Latest vend (qty, price, date) by `vended_at`.
  - Dispense method: carousel/locker → ceil(shortfall/q) × q; smart crib → max(0, shortfall − tol% × loaded); else shortfall.
  - Shares: category, delay (days since the latest vend date), backup.
  - Result 0 if no units, else `RND(units × price × (1 + Σ), 2)`.
  - Matches the rule.
- **Q4:**
  - Retired and substitute items by highest change reference.
  - Retired units in 3 months (vends − returns − errors).
  - avg = units / 13 / visits.
  - Sized usage: T1 avg/trigger; T2 `MX(retired_par, retired_largest / trigger_fraction)`; T3 retired par.
  - Allowance, list-price step, backup, exposure, channel.
  - Ceil at the end.
  - **Mismatch:** the rule's T2 sentence admits a second reading → F3-C4.
- **Q5:**
  - Newest add (sku, date, category, starter par).
  - Selection units over the substitute and the retired item; avg.
  - Settling ladder.
  - Allowance, backup, exposure, value share (latest line by effective date), channel.
  - `/trigger`, ceil.
  - Matches the rule.

### action_binding_and_uuids (r3)
- Five (tool, computes) pairs, one per policy.
- uuid8s: `58ce1bb4`, `bfc1c22c`, `2f4f7780`, `72f4b244`, `5d8137ae`. Independent, not derived from each other, none reused.
- Docstrings: every claimed effect exists in its body:
  - next VR-/VE-/VPC- reference in sequence;
  - fields copied from the original vend or contract line;
  - credit = qty × unit credit, half-up (`cents_half_up`);
  - machine_stock_value increased.
- No example values, no tool names, no ordering words. No body validates anything. PASS.

### prerequisite_graph and prerequisite_sentences (r3)
- **E1 (Q2 → P1).** "A return of a start-up item is not credited until the item's selection carries the start-up review par change entry from Corbett that its stockout between scheduled restock visits owes."
  - "not … until"; state form; no tool or id.
  - The only writer of a Corbett par_change is P1's tool.
  - Derivation: the stockout → P1 "Corbett re-sizes the par … records a par change entry from Corbett".
  - PASS on the four-point test.
  - **But its `effect` field is false on the only world where it applies** → F3-C2.
- **E2 (Q4 → Q3).** "The substitute's par is fixed only after the retired item's stock ledger stands at zero or above."
  - "only after"; state; record-visible.
  - Single route: Q3's own rule says "While the retired item's stock ledger stands below zero, Corbett owes … one vend error credit … once that credit stands the ledger no longer stands below zero". Restocking is excluded ("once its contract price ends Corbett loads no more of it").
  - The return tool could raise the ledger, but no policy returns units of a retired item. Q2's scope is the start-up item.
  - PASS. The effect holds (it lowers retired units).
- **E3 (Q5 → Q4).** "A par change on the selection of a Corbett-placed substitute is fixed only after the substitute stands in the retired item's selection as an add entry from Corbett."
  - "only after"; state.
  - Q4 is the only writer of a Corbett add.
  - PASS. The effect holds.
- Graph: P1 ← Q2; Q3 ← Q4 ← Q5. Acyclic. Every `gate` is a real binding. No undeclared cross-problem order in any rule.

### override_declarations (r3)
- **P1:** `[]`, as before.
- **Q2:** retires the base return-credit sentence. Its replaced_by restates the vend-price credit for every other return and scopes "only such a unit". Inherited, not weakened:
  - "Coil machines … cannot take items back";
  - return_to_machine_allowed;
  - original package and the vending badge;
  - the `return_to_machine_days` window;
  - one credit per vend.
  PASS.
- **Q3:** retires the base report-window sentence. Its replaced_by restates it with the self-scoped exception. The desk-limit sentence and once-per-vend are restated or inherited.
  - **Undeclared departure.** The base `vending_vend_error_credited` event is "A logged vend that did not dispense is reversed and credited", grain "One row per vend error credited", with `quantity: "Units not dispensed."` and `original_txn_reference: "Vend transaction that failed."`. Q3 instead books one row against the latest vend, whose units credited are the retired item's whole shortfall across vends, rounded up on carousel and locker machines. That can exceed both the units that vend issued and the units not dispensed. No overwrite declares this → F3-C1.
- **Q4:** `[]`. Base planogram management is silent on Corbett adds; the capacity and special-item bounds are inherited. PASS.
- **Q5:** retires base planogram S1. Its replaced_by restates S1 with the self-scoped exception. "counts toward the included changes" is consistent with base fees. PASS.

### factor_ladders (r3)

| policy | factors | method | parameter | cross-difficulty | multi-source |
| --- | --- | --- | --- | --- | --- |
| P1 | 6 | 1 | 5 | vmi, credit, pricing, order | backup, exposure |
| Q2 | 4 | 1 (fill_level_shape) | 3 (trial, return rate, handling) | none | none (task 0 is covered by P1) |
| Q3 | 4 | 1 (dispense_unit_basis) | 3 (category share, delay, storeroom absence) | pricing, vmi | storeroom_absence (program + bins) |
| Q4 | 6 | 1 (substitute_demand_basis) | 5 | pricing ×2, vmi, credit, order | backup, exposure |
| Q5 | 6 | 1 (settling_demand_basis) | 5 | vmi, credit, pricing, order | backup, exposure |

- Bindings are disjoint. Every tier is stated in its rule.
- Label sweep: every parameter tier selects a number. **F2-C1 is closed as a class** (no parameter factor has a computed tier).
- XF-11 pairwise table:
  - Q2: T1 price−0.75, T2 price×0.95, T3 price. Distinct.
  - Q3: carousel ceil multiple, crib tolerance, plain. Distinct (shortfall 3, q 2 → 4 / 3 − tol×loaded / 3).
  - Q4: avg/trigger vs max(par, largest/trigger) vs par. Distinct.
  - Q5: T1 max(avg, starter×trigger), T2 largest, T3 avg. Distinct.
  - No member.
- XF-1: no factor reads another factor's binding. Unbound single-factor quantities (O7 kind): Q2 `units_loaded`, `units_vended`, `units_back`, `units_out`. These feed only `stock_ledger`, which is in fill_level_shape's bindings, so it is an observation.

### XF recipe re-check (r3)
1. Independence: PASS.
2. Assembly: generic. PASS.
3. Order: Q2 ("shaped by the fill level first and then multiplied by each share"), Q3, Q4 and Q5 all stated. PASS.
4. "As another policy figures it": none.
5. Overwrites: Q2, Q3 and Q5 are self-scoped and restate the out-of-scope content. P1 and Q4 are `[]`. PASS, apart from the undeclared departure F3-C1.
6. Verbatim: PASS.
7. Rounding placement: PASS. Ceil in P1, Q4 and Q5; RND at the end in Q2 and Q3.
8. Docstrings: PASS.
9. **Edges. RED (F3-C3).** The month convention is stated in every policy. Members:
   - Same-day ties, which LATEST/XLATEST row is kept, unstated:
     - Q2 "the item's contract price line with the latest effective date";
     - Q4 "the retired item's contract price line written as an added item with the latest effective date";
     - Q5 "its contract price line with the latest effective date".
     Pricing allows several lines per sku per effective date (`distinguish_by: [sku, effective_date, change_reason]`).
   - Removal-line branch: Q2's and Q5's "current contract unit price" takes the latest line even when it is a removal. A removal line carries "Contract unit price that ends", and `pricing_price_basis` gives no contract price after a removal. The rule never states that branch.
   - No other member: P1's and Q3's latest-vend reads are by timestamp to the second, and references are sequential.
10. Filters: PASS.
11. Method shape: PASS.
12. Cross-record windows: none.
13. Seeded rows of other categories conform in both worlds:
    - task 0 pricing competitive match: highest of 6.55 / 6.5075 / 5.4565 = 6.55, within the 5% maximum;
    - task 0 credit hold cured; certified funds;
    - task 1 substitute price 9.40 under the Net-Price 90-day protection;
    - vmi bin references VBR.
    No vmi_activity rows remain, so **T1-F4 is closed as a class**. An own-category seed defect is filed per task (task 1, T1-F6).

### findings (r3)
- **F3-C1 — SOURCE-POLICY RED (undeclared departure from base vend-error semantics).**
  - Q3's rule: "Corbett owes … one vend error credit against the retired item's latest vend …, recording the units credited" and "on a carousel or a locker machine … the units credited are the shortfall rounded up to whole multiples of the units of the latest vend".
  - Base: `vending_vend_error_credited` "A logged vend that did not dispense is reversed and credited", `quantity: "Units not dispensed."`, `original_txn_reference: "Vend transaction that failed."`; `one_credit_per_vend` "Each vend transaction may be returned or credited for a vend error only once."
  - Demonstrated on task 1's world:
    - The base reading gives two per-vend credits: VT-5626432 for 2 units (10-01), and VT-5626378 for 1 unit of its 2 (09-29). Both at 9.40, totalling 3 units.
    - Q3 gives one row of **4 units** against VT-5626432, which issued only 2, while 3 units were undispensed.
    - Different terminal state; the overwrite declares only the report window.
  - Only member: Q3.
- **F3-C2 — SOURCE-POLICY RED (prerequisite `effect` asserts a world fact that is false).**
  - Q2's E1 effect: "with the larger par the item's stock ledger falls below the near-full share, so the fill-level shape moves from the near-full credit share to the plain price".
  - In task 0, the only world where E1 applies, the opening ledger 24 stands at the par 24, which is tier 1 (overstock), not near-full. After P1's par of 28, 24 ≥ 0.8 × 28 = 22.4, so tier 2 (near-full), not plain.
  - The binding does move, but not as declared.
  - Other members: none. E2's and E3's effects hold on task 1.
- **F3-C3 — SOURCE-POLICY RED (XF-9).** Members as listed in point 9 (three tie sites, two removal-line branches). Neither world hits them:
  - task 0: AB-53318 lines on 08-24 and 10-05, no removal;
  - task 1: SF-55247 one line; SF-55233 one added line.
- **F3-C4 — SOURCE-POLICY RED (rule admits a second reading of compute).**
  - Q4's rule: "the sized usage is the larger of the retired item's par and its largest single vend, the largest number of its units issued in one vend on the machine at any time, divided by the low-stock trigger fraction".
  - Compute: `MX(retired_par, retired_largest / trigger_fraction)`.
  - The comma-separated "divided by …" can bind to the whole "larger of", giving (max(par, largest)) / trigger.
  - Example input: par 20, largest 4, trigger 0.2 → compute 20; second reading 100.
  - Only reachable when the retired item has no units in 3 months. Not reached in task 1, which takes T1.
- **Closed from r2:**
  - F2-C1 (no parameter factor computes; the shutdown factor is gone).
  - T1-F4 (no pause rows; all cross-category references conform).
  - T1-F5 (follows F2-C1).
- **Observations:**
  - O6 (unconditional baseline sentences): Q3 has two "The credit value is …" sentences; Q4 has "The substitute takes the retired item's par" and then "The par is sized …".
  - O7: Q2's ledger components are not in the factor's bindings.
  - O15: RND mode. Q2 and Q3 say half up, and the tool's `cents_half_up` agrees; the DSL RND is float-based.
  - O16, new realism concern: Q3's service shares (+25% PPE, +5/10% delay, +5/10% backup) credit more than was billed. The carousel rounding also credits a unit the ledger shows was dispensed. In task 1 that is 50.76 for 3 undispensed units billed at 28.20.
  - O17, new: Q2 credits a start-up return at the current contract price, here the 6.55 competitive match effective today, rather than the 6.85 paid four days earlier.
  - O18, new: the task-1 persona asks for the par "set the way Corbett sizes it rather than at a number you pick". That mirrors Q5's "rather than at a par the customer names". It is the customer's need, but phrased in the rule's words.

## closing_checklist (revision_3)
- [x] The task files correspond one to one. All revisions are preserved, with r3 appended.
- [ ] Every comparison PASSes:
  - task 0: RED (T0-F1 = F3-C2);
  - task 1: RED (T1-F7 = F3-C1; T1-F6).
- [x] Scopes {P1, Q2} and {Q3, Q4, Q5} are disjoint and together complete. Tools are closed. Each uuid8 is independent. **No task tool writes an event whose base trigger lands in another category** (selection_set, item_returned and vend_error_credited all have `triggers: []`).
- [x] Trees:
  - task 0: 1 prerequisite, value_input, 1 user write;
  - task 1: 2 prerequisites, both value_input, 1 user write.
  - A DAG.
- [x] Factors: counts within bounds, honest labels, every factor bears weight, each baseline ≠ gold. Seed realism fails at T1-F6.
- [ ] Gates on the final form: the r3 snapshot shows 7/7 OK. The difficulty does not close.
- **Difficulty does NOT pass the source-layer audit.**
- **Closed from r2:** F2-C1, T1-F4, T1-F5 (classes gone).
- **Open charter REDs, each with all members:**
  - **F3-C1.** Q3 is the only member: its single-row, cross-vend, rounded-up unit credit departs from base vend-error semantics undeclared.
  - **F3-C2.** Q2's E1 `effect` is the only member. E2 and E3 effects hold.
  - **F3-C3 (XF-9).** Unstated same-day tie for "latest effective date" in Q2, Q4 and Q5. Unstated removal-line branch for "current contract unit price" in Q2 and Q5.
  - **F3-C4.** Q4 T2's "larger of … par and … largest single vend, … divided by the low-stock trigger fraction" has a second reading. It is the only member.
- **Open task-level RED:** T1-F6 (27 mispriced SF-55233 vend rows).

VERDICT revision_3: task0=RED[SOURCE-POLICY(T0-F1 F3-C2 false edge effect)] task1=RED[SOURCE-POLICY(T1-F7 F3-C1 vend-error semantics),SOURCE-FACTOR(T1-F6 seed vend prices after removal)] charter=F3-C1,F3-C2,F3-C3,F3-C4

## revision_4

## charter_global_frozen (revision_4)
- Frozen: 2026-10-17, before any r4 task GT reveal. Same auditor. Earlier revisions are left untouched.
- Entry gate:
  - The worklog's last line is `REWORK round 4: gates 7/7 green`.
  - `/tmp/erl0068_coord/snapshot.sh d5_vendpoint_usage_and_machine_billing 4` printed all 7 gates OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. The snapshot is saved at `.audit_views/policy/d5_vendpoint_usage_and_machine_billing/r4/gates.txt`.
  - Input is complete.
- Hashes (r4):

| file | sha256 | vs r3 |
| --- | --- | --- |
| charter | `1ff07d8ec901af2686727589621a1a25f20eb89eff735071bc617f3ee48f212e` | changed |
| tools | `30f416c50755e5d091e831b70a86ff3c0308f7a7df2e49675b371ba5bd00c44f` | **unchanged** |
| `r4/task0.view.json` | `f918349dc3bf77c8a8720e15787aadf7b2dcca9a455c7822d1a8027cab8df0d4` | changed |
| `r4/task1.view.json` | `d6ca0481929643af37957fcc2ccab8bd5466b82b25817983813d3ed86d20afcb` | changed |

- contamination_disclosure: I know the r3 GT of the same design. Scored values were re-derived from the r4 views. No r4 task JSON was opened before the freezes.
- Base copy: verbatim. Sweep (XF-6): clean on all 5 policies.

### action_binding_and_uuids (r4)
- Carried forward by reference from revision_3 `### action_binding_and_uuids (r3)`, on the ground that the tools hash `30f416c5…` is unchanged.
- The (tool, computes) pairs are unchanged in the r4 charter (same 5 target_tools and computes).
- **Cross-category triggers:** unchanged. The tools still write only `vending_selection_set`, `vending_item_returned` and `vending_vend_error_credited` (all `triggers: []`). No task tool writes an event whose base trigger lands in another category. PASS.

### policy_conflict_scan, prerequisite_graph and sentences (r4, re-derived)
- Policy ids, subjects, tools and edges are unchanged: P1 ← Q2; Q3 ← Q4 ← Q5. The scopes stay forced disjoint and complete.
- The three `policy_source` sentences are unchanged and verbatim. The four-point test and single-writer analysis hold as in r3.
- `effect` fields are rewritten:
  - **E1 (Q2):** "…moves from the overstock handling charge to the near-full credit share when the ledger stays at or above the near-full share of the new par, or to the plain price when it falls below it". This covers both outcomes and holds on task 0 (24 = old par 24; new par 28; 24 ≥ 22.4 → near-full). **F3-C2 is closed.**
  - **E2 (Q4):** "…lowers its average per restock interval …; the sizing tier stays the one for retired units above zero". True on task 1 (260 → 259).
  - **E3 (Q5):** "…the starter par figure is the larger of the two". True on task 1 (55 × 0.2 = 11.0 > 9.96).

### override_declarations (r4)
- **Q2:** replaced_by now scopes "returned … against that item's latest vend". The start-up credit's price is now "the unit price of the item's latest vend, the price paid for the returned units, whatever the item's contract price line says today". Every other return stays at its original vend's price. This is consistent with base returns (credit basis = vend unit price); only the shaping and shares depart, and that is declared. PASS. **O17 is closed.**
- **Q3:**
  - replaced_by and rule now cover only "the failed vend of a retired item … whose shortfall is no more than the units of its latest vend and only for such a vend".
  - The rule states that "the latest vend is the only vend that dispensed fewer units than it logged, and it is the failed vend".
  - One credit is booked against it "recording the units it did not dispense …, credited once like any vend error".
  - A larger shortfall "stays under the base vend error rules".
  - The credit is capped: "that sum never above one, so that no credit exceeds what was billed for the units not dispensed".
  - The row now matches the base event: a failed vend reversed, `quantity` = units not dispensed, once per vend.
  - **F3-C1 is closed. O16 is closed** (the service shares no longer push the credit above the amount billed, and the carousel units equal the shortfall).
- **P1, Q4, Q5:** as in r3. PASS.

### rule_compute_equivalence (r4)
- **P1:** T2 is reworded ("the larger of two figures, the average … and the product of the starter par and one less the low-stock trigger fraction"). Same compute. PASS.
- **Q2:**
  - `latest_vend_price` = LATEST by `txn_reference`, matching "the vend carrying the highest vend transaction number (the machine log numbers vends in sequence)".
  - An item with no vend gets 0.0, matching "an item with no vend … no credit".
  - Remainder as in r3. PASS.
- **Q3:**
  - `in_scope` = 0 < shortfall ≤ last_vend_qty.
  - `units_short`: carousel/locker → shortfall; crib → max(0, shortfall − tolerance); else last_vend_qty.
  - `credit_share` = MN(1, 0.5 + shares).
  - Result `RND(units × price × share, 2)` if in scope.
  - Matches the rule both ways. PASS.
- **Q4:**
  - T2 now reads "the larger of two figures, the retired item's par and the quotient of its largest single vend … by the low-stock trigger fraction", which is `MX(retired_par, retired_largest / trigger_fraction)`. One reading only. **F3-C4 is closed.**
  - `retired_list` = XLATEST by `change_reference` with change_reason new_item, matching "the retired item's contract price line written as a new item carrying the highest quote reference (Corbett issues quote references in sequence)".
- **Q5:** `sub_price` = XLATEST by `change_reference` with change_reason discontinued_substitute, matching "the substitute's contract price line written as a Corbett-approved substitute carrying the highest change reference".
- **F3-C3 is closed.** All three tie sites now pick by sequential reference, and no rule reads a "current contract unit price" from a line that may be a removal.

### factor_ladders (r4)
- Counts unchanged: P1 6 (1m/5p), Q2 4 (1m/3p), Q3 4 (1m/3p), Q4 6 (1m/5p), Q5 6 (1m/5p). Cross-difficulty factors and multi-source factors as in r3.
- Q3's parameter factor was renamed to category_credit_share. Its values are 0.25 / 0.1 / 0. The fall-through `late_find_share` 0.5 sits in the baseline.
- Every label is honest. Pairwise methods:
  - Q3: shortfall vs shortfall − tolerance vs latest-vend units (distinct when shortfall < latest units; task 1: 1 vs 2).
  - Others unchanged.
- No member of XF-1, XF-2, XF-3 or XF-11.

### XF recipe re-check (r4)
- Points 1–8 and 10–12: PASS on all 5 policies.
- Point 9: PASS. Month convention stated; every tie broken by a sequential reference; absent-record branches stated (Q2 no vend; Q3 no shortfall or no vend; Q4/Q5 None list prices or lines → share 1).
- Point 13: PASS. Cross-category seed rows are producible in both worlds (task 0 pricing removal notice 07-27, effective 08-26 = 30 days; substitute line effective 08-26; competitive match). The own-category T1-F6 is closed in task 1's world.

### findings (r4)
- **Closed:** F3-C1, F3-C2, F3-C3, F3-C4 (each as a class; no remaining member found). O16, O17, O18 are addressed. For the persona wording, see task 1.
- **New REDs:** none charter-level.
- **Observations still open:**
  - O6: unconditional baseline sentences, e.g. Q3 "The credit value is the units of the latest vend multiplied by … the late-find share" before the full assembly sentence.
  - O7: Q2 and Q3 ledger components are not in the factor bindings.
  - O15: DSL RND float mode. No r4 figure sits on a half-cent: 6.000449, 10.4328.
  - O19, new: Q2's scope "against that item's latest vend" is the XF-12 route-around (a single candidate record). A real return policy would not single out the latest vend.

## closing_checklist (revision_4)
Written after both r4 reveals.

- [x] Task files 0.md and 1.md correspond one to one with tasks 0 and 1. revision_1 to revision_4 are preserved in all three files. Every revision_4 comparison carries a PASS (task 0 PASS, task 1 PASS).
- [x] Coverage and scope:
  - All 5 extended policies are covered: task 0 = {P1, Q2}; task 1 = {Q3, Q4, Q5}.
  - The scopes are disjoint and each spans its whole tree.
  - Task tools and GT are closed. Each uuid8 is independently generated and frozen: `58ce1bb4`, `bfc1c22c`, `2f4f7780`, `72f4b244`, `5d8137ae`.
  - No task tool writes an event whose base trigger lands in another category.
- [x] Trees:
  - task 0: 1 prerequisite problem, 1 value_input edge, 1 user write;
  - task 1: 2 prerequisite problems, 2 value_input edges, 1 user write;
  - no cycle, and the difficulty-wide graph is a DAG.
- [x] Factors:
  - Every computation declares a self-sufficient baseline and 4–6 factors with ≥2 parameter and ≥1 honest method.
  - Each task has ≥1 multi-source factor and ≥1 cross-difficulty factor.
  - Every ladder has ≥3 tiers stated in its rule, with distinct outcomes.
  - Every factor bears weight against an honest baseline.
  - Each baseline alone gives a definite number ≠ gold: 20 / 6.85 / 11.59 / 60 / 50.
- [x] Gates re-run on the final form: the coordinator's r4 snapshot (`r4/gates.txt`) shows 7/7 OK.
- **Revision_3 REDs closed:** F3-C1, F3-C2, F3-C3, F3-C4, T0-F1, T1-F6, T1-F7. No new RED. Nothing regressed.
- **Remaining observations (not grounds for rework):** O6, O7, O15, O19.
- **The difficulty passes the source-layer audit at revision_4.**

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Frozen: 2026-10-17, before any r5 task GT reveal. Same auditor. Earlier revisions are left untouched.
- Entry gate:
  - The worklog's last line is `REWORK round 5: gates 7/7 green`.
  - `/tmp/erl0068_coord/snapshot.sh d5_vendpoint_usage_and_machine_billing 5` printed all 7 gates OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. The snapshot is saved at `.audit_views/policy/d5_vendpoint_usage_and_machine_billing/r5/gates.txt`.
  - Input is complete.
- Hashes (r5):

| file | sha256 | vs r4 |
| --- | --- | --- |
| charter | `033df3037743648a4f496b2516b0dd39ff17e9076466c871a94f7256d06fd65b` | changed |
| tools | `1dee5f0cb4c3247bbcd12b880d4e112c15f30960a76145e5328c5fdb8e7db144` | changed |
| `r5/task0.view.json` | `f918349dc3bf77c8a8720e15787aadf7b2dcca9a455c7822d1a8027cab8df0d4` | **identical** |
| `r5/task1.view.json` | `d6ca0481929643af37957fcc2ccab8bd5466b82b25817983813d3ed86d20afcb` | **identical** |

- Extra input: `audits/render_source/d5_vendpoint_usage_and_machine_billing/render_r1.md`, read in full: A1–A4, B1–B5 and C. Each is treated as a RED to verify closed as a class across all five policies.
- contamination_disclosure: I know the r4 GT (28 / 6.00; 10.43 / 55 / 46). No r5 task JSON was opened before the freezes.
- Base copy: verbatim. Sweep (XF-6): clean on all 5 policies.
- Diff against my r4 scratch copy (`/tmp/audit_…/charter_r4.yaml`), by script:
  - **every `compute` expression is unchanged**;
  - the changes are rule prose (method and assembly sentences, "standard …" baseline sentences), factor `bindings`, ladder wording and `baseline` blocks;
  - prerequisites, overwrites, params and targets are unchanged.

### render_r1 items: verification and earlier coverage

| item | r5 state | covered by my earlier revisions? |
| --- | --- | --- |
| A1 Q2 ledger components unbound | `fill_level_shape.bindings` now holds `units_loaded`, `units_vended`, `units_back`, `units_out`. **Closed.** | Yes, as observation O7 (r3, r4). Under-graded: recipe point 1 makes it RED. |
| A2 Q3 `last_vend_date` | Now in `credit_delay_share.bindings`. **Closed.** | No. |
| A3 Q4 `avg_interval` / `trigger_fraction` vs `retired_par` | `substitute_demand_basis.bindings` = [avg_interval, trigger_fraction, retired_largest, sized_usage]. `retired_par` is out and is the baseline's quantity ("The standard par is the retired item's par…"). **Closed.** | No. |
| A4 Q5 `add_date` | Now in `settling_demand_basis.bindings`. **Closed.** | No. |
| B1–B5 assembly names a factor quantity, and a second result definition | Each baseline sentence now defines a named **standard** quantity: "The standard par is …" (P1, Q5), "The standard unit credit is …" (Q2), "The standard credit value is …" (Q3), "The standard par is the retired item's par …" (Q4). Each method sentence now says which baseline quantity it replaces ("can replace the average per restock interval in the standard par", "…the price in the standard unit credit", "…the units of the latest vend in the standard credit value", "…the retired item's par in the standard par"). Each assembly sentence is generic: "each method that applies first replaces the quantity of the standard par it names; the allowances that apply are then added …; … multiplied by … each share and factor that applies". It names no factor quantity and fixes the order; Q2 states the non-commuting step explicitly ("so that a charge a method subtracts comes before any share"). The result is now "the par" or "the credit", distinct from the standard quantity, so the second definition is gone. **Closed (B1–B5).** | Partly. The unconditional baseline sentences were O6 (r1–r4), an observation. The naming half I let pass in r1 as "kind names" and never flagged. Under-graded. |
| C resize docstring "applies from the next restock visit" | The sentence is removed from `resize_selection_par_58ce1bb4`. Every remaining docstring claim exists in its body. **Closed.** | No. In r1–r4 I read it as business timing, not as a claimed tool effect. |

### Class sweeps (all five policies)
- **XF-1 / A class.** A script listed every plain binding read by exactly one factor:
  - P1 `avg_interval`, Q5 `avg_interval` and Q4 `retired_par` are hit. Each is the baseline's own quantity, reached through the factor's `baseline` substitution (`interval_usage: avg_interval`, `sized_usage: retired_par`), so they are correctly plain.
  - No other single-factor plain binding remains.
  - No factor binding is read by another factor's binding.
  - Factor outputs are read only by the assembly bindings (`sized_units`, `sized_par`, `credit_share`, `result`).
  - **No member.**
- **XF-2/3 / B class.** All five assembly sentences are generic and order-fixing. No baseline sentence competes with the result's definition. **No member.**
- **XF-8 / C class.** All five docstrings checked against their bodies. **No member.**
- XF-4, 5, 6, 7, 9, 10, 11, 12 and 13 are re-checked on the new prose. The compute, overwrites and prerequisites are unchanged, so the r4 conclusions stand. Rounding wording: P1, Q4 and Q5 say "rounded up … only at the end"; P1 and Q5 also say "standard par before its rounding"; Q2 and Q3 say "rounded half up to the cent only at the end". All match compute. PASS.
- **Cross-category triggers:** the tools still write only `vending_selection_set`, `vending_item_returned` and `vending_vend_error_credited` (all `triggers: []`). The only body change is the removed docstring sentence (the bodies are re-read). No task tool writes an event whose base trigger lands in another category. PASS.

### Sections carried or re-derived (r5)
- **policy_conflict_scan, prerequisite_graph, prerequisite_sentences, override_declarations:** the inputs are unchanged (the policy_source sentences, effects, overwrites, targets and edges are byte-identical to r4). Re-checked against the new rule text; the four-point test holds. Same conclusions as revision_4. PASS.
- **rule_compute_equivalence:** compute is unchanged. Each new method or assembly sentence was mapped back to its expression:
  - P1/Q5 `interval × (1+allowances) × factors / trigger`, then ceil;
  - Q2 `shaped × shares`, then RND;
  - Q3 `units × price × MN(1, 0.5 + shares)`, then RND;
  - Q4 `sized_usage × (1 + allowance) × shares and factors`, then ceil.
  PASS.
- **factor_ladders:** counts and labels as in r4. The ladder wording now says "replaces it" and "stands". Every tier remains stated in its rule and implemented in compute. PASS.
- **action_binding_and_uuids:** the tools hash changed only by the C docstring edit. Same 5 tools and uuid8s, independent. PASS.

### findings (r5)
- Every render_r1 item (A1–A4, B1–B5, C) is closed as a class.
- No new RED. No regression found.
- Observations still open: O15 (DSL RND float mode) and O19 (Q2's latest-vend scope as the XF-12 route-around).
- O6 and O7 are closed: they were the r1–r4 under-graded forms of B and A.

## closing_checklist (revision_5)
Written after both r5 reveals.

- [x] Task files 0.md and 1.md correspond one to one with tasks 0 and 1. revision_1 to revision_5 are preserved in all three files. Every revision_5 comparison carries a PASS.
- [x] Coverage and scope:
  - All 5 extended policies are covered: task 0 = {P1, Q2}; task 1 = {Q3, Q4, Q5}.
  - The scopes are disjoint and each spans its whole tree.
  - Task tools and GT are closed. Each uuid8 is independent and frozen.
  - No task tool writes an event whose base trigger lands in another category.
- [x] Trees:
  - task 0: 1 prerequisite problem, 1 value_input edge, 1 user write;
  - task 1: 2 prerequisite problems, 2 value_input edges, 1 user write;
  - the difficulty-wide graph is a DAG.
- [x] Factors:
  - Each computation has a self-sufficient "standard …" baseline and 4–6 factors with ≥2 parameter and ≥1 honest method.
  - Each task has ≥1 multi-source factor and ≥1 cross-difficulty factor.
  - Every ladder has ≥3 distinct tiers stated in its rule.
  - Every factor bears weight.
  - Each baseline alone gives a definite number ≠ gold: 20 / 6.85 / 11.59 / 60 / 50.
- [x] Gates on the final form: the coordinator's r5 snapshot shows 7/7 OK.
- **Render_r1 items closed as classes:** A1–A4, B1–B5, C. My earlier coverage: A1 and B were observations (O7, O6), under-graded; A2–A4 and C were not caught.
- No new RED. Nothing regressed.
- **Remaining observations:** O15, O19.
- **The difficulty passes the source-layer audit at revision_5.**

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Frozen: 2026-10-17, before the r6 reveal. Same auditor. Earlier revisions are left untouched.
- Entry gate:
  - The worklog's last line is `REWORK round 6: gates 7/7 green`.
  - `/tmp/erl0068_coord/snapshot.sh d5_vendpoint_usage_and_machine_billing 6` printed all 7 gates OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. The snapshot is saved at `r6/gates.txt`.
  - Input is complete.
- Hashes (r6):

| file | sha256 | vs r5 |
| --- | --- | --- |
| charter | `8b0a7e3be1a7ee567143ad83a25c72eb56ad67ed1e971a0d4c66c25559b986bb` | changed |
| tools | `1dee5f0cb4c3247bbcd12b880d4e112c15f30960a76145e5328c5fdb8e7db144` | **unchanged** |
| task0 view | `f918349d…f0d4` | **unchanged** |
| task1 view | `d6ca0481…afcb` | **unchanged** |

- Extra input: the src items of `audits/policy_kb/d5_vendpoint_usage_and_machine_billing/_verdict.md`. Only SRC-1 and SRC-3 were read as routed (SRC-2 is not routed).
- contamination_disclosure: I know the r5 GT. The r6 task JSONs were unopened before the freezes.
- Diff against my r5 scratch copy, by script:
  - base copy identical;
  - **P1, Q2, Q3 and Q5 byte-identical to r5**;
  - Q4 changed in exactly one rule sentence (the list-price step), its compute_basis quotes for `retired_list`, `list_ratio` and `price_step`, and compute `list_ratio`.
  - Sweep (XF-6): clean.
- **Carried forward by reference** to revision_5 (inputs unchanged):
  - action_binding_and_uuids (tools hash unchanged; no cross-category trigger);
  - the P1, Q2, Q3 and Q5 parts of rule_compute_equivalence, factor_ladders and override_declarations;
  - policy_conflict_scan, prerequisite_graph and prerequisite_sentences (edges, sentences and effects unchanged).

### SRC items (verification as classes)
- **SRC-1: zero list price.**
  - Q4 rule now says "…otherwise, or when either line carries no list price or a list price of zero, the share is one".
  - Compute: `list_ratio: 1.0 if (sub_list == None or sub_list == 0 or retired_list == None or retired_list == 0) else sub_list / retired_list`.
  - The rule and compute agree for a zero or absent price on either side. **Closed.**
  - Class sweep: I checked every None, zero and absent branch in all five policies by script against its rule sentence:
    - Q5 `value_share` (`sub_price` None → 1; 0 → "below it" → 1);
    - Q2 no vend → 0;
    - Q3 `in_scope`, `delay_days` and `backup_share`;
    - P1, Q4 and Q5 channel "above zero";
    - P1 `lead_allowance`;
    - Q4 sized_usage "ever vended" → `retired_largest > 0`.
    Every branch is stated in its rule and matches compute. **No remaining member.**
  - Earlier coverage: no, I did not flag it in r1–r5.
- **SRC-3: rule names a reference field that doesn't exist.**
  - Q4 now reads "…written as a new item carrying the highest change reference (Corbett issues these references in sequence)". That is `pricing_items.change_reference` ("Quote or change reference (SPQ-...)"), matching compute `date_field='change_reference'`. **Closed.**
  - Class sweep: every "highest … reference/number" phrase in all five rules maps to a real field:
    - "planogram request reference" → `vending_planogram.change_reference`;
    - "bin request reference" → `vmi_bins.change_reference`;
    - "change reference" → `pricing_items.change_reference`;
    - "vend transaction number" → `vending_transactions.txn_reference` ("Vend transaction number from the machine log (VT-...)").
    **No remaining member.**
  - Earlier coverage: no. In r4 I accepted "quote reference" because the SPQ- references are sequential, without checking the field name.

### Renderer-class sweeps (XF 1, 2, 3, 9, 10, 12), re-run on r6
1. **Point 1:** a script lists single-factor plain bindings that are not the baseline's own quantity, and factor bindings read by another factor. Result: none in all five policies.
2. **Points 2 and 3:** assembly sentences are unchanged from r5 (generic, order-fixing); the Q4 edit touches only a factor sentence. PASS.
3. **Point 9:** ties are by sequential references, now correctly named (SRC-3). The zero and absent branches are stated (SRC-1 sweep). The month convention is unchanged. PASS.
4. **Point 10:** the Q4 filter `change_reason='new_item'` matches "written as a new item". Every other filter is unchanged from r5. PASS.
5. **Point 12:** no cross-record date windows. PASS.
- The remaining XF points (4–8, 11, 13) carry forward from r5. Nothing in their inputs changed except the Q4 sentence, which was re-checked.

### findings (r6)
- SRC-1 and SRC-3 are closed as classes. No new RED. No regression.
- Observations: O15 and O19, unchanged.

## closing_checklist (revision_6)
Written after both r6 reveals.

- [x] Task files correspond one to one. revision_1 to revision_6 are preserved. Both r6 comparisons PASS.
- [x] Scopes {P1, Q2} and {Q3, Q4, Q5} are disjoint and together complete. Tools are closed, with independent uuid8s. No task tool writes an event whose base trigger lands in another category (tools unchanged from r5).
- [x] Trees: task 0 has 1 prerequisite problem and task 1 has 2. Every edge is value_input. Each tree has one user write. The difficulty-wide graph is a DAG.
- [x] Factors: bounds hold, labels are honest, every factor bears weight, and each baseline ≠ gold (20 / 6.85 / 11.59 / 60 / 50).
- [x] Gates on the final form: the r6 snapshot shows 7/7 OK.
- **SRC-1 and SRC-3 are closed as classes.** Neither was covered by my earlier revisions. SRC-2 is not routed (a placement note).
- No new RED. Nothing regressed.
- **Remaining observations:** O15, O19.
- **The difficulty passes the source-layer audit at revision_6.**

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- Frozen: 2026-10-18, before the r7 reveal. Same auditor. Earlier revisions are left untouched.
- Entry gate:
  - The worklog's last line is `REWORK round 7: gates 7/7 green`.
  - `/tmp/erl0068_coord/snapshot.sh d5_vendpoint_usage_and_machine_billing 7` printed all 7 gates OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE.
  - Input is complete.
- Hashes (r7):

| file | sha256 | vs r6 |
| --- | --- | --- |
| charter | `8b0a7e3be1a7ee567143ad83a25c72eb56ad67ed1e971a0d4c66c25559b986bb` | **unchanged** (= 8b0a7e3be1a7ee56…, confirmed) |
| tools | `1dee5f0cb4c3247bbcd12b880d4e112c15f30960a76145e5328c5fdb8e7db144` | **unchanged** (= 1dee5f0cb4c3247b…, confirmed) |
| task0 view | `7537ca7a7add3cd266caa106696d50f3bcc95b1e8aeee1ef6fc932616117175a` | changed (seed only) |
| task1 view | `469342ff189ae7449ae5013e6727c5b70d74614736c98c962647185deb41b722` | changed (seed only) |

- **Every charter-global section carries forward by reference to revision_6**, on the ground that the charter and tools hashes are unchanged. That covers: policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids (no cross-category trigger), prerequisite_graph and sentences, override_declarations, factor_ladders, the XF sweeps, and the SRC-1/SRC-3 closures.
- Context read: the src items SRC-4 to SRC-9 in `audits/policy_kb/d5_vendpoint_usage_and_machine_billing/_verdict.md` (latest revision).
- contamination_disclosure: I know the r6 GT. The r7 task JSONs were unopened before the freezes.
- Seed producibility was judged against the owning products' charters (`blueprint/products/{vmi,pricing,order,credit}.yaml`), which are the sources of `docs/<product>/`. Per-row checks are in each task file.
- No charter-level finding. Charter: CLEAN.

## closing_checklist (revision_7)
Written after both r7 reveals.

- [x] Task files correspond one to one. revision_1 to revision_7 are preserved. Both r7 comparisons PASS.
- [x] Scopes, tools and uuid8s are unchanged and closed (charter and tools hashes are the same as r6). No task tool writes an event whose base trigger lands in another category.
- [x] Trees and factors are re-derived on the r7 worlds. Every edge and every factor still bears weight with unchanged tiers. Each baseline ≠ gold.
- [x] Seed-only rework: every new or changed row in both worlds is producible by its owning charter (vmi Self-Scan, pricing Category and Net-Price, order Standard / Route / Premier, credit Net 30 Standard).
  - The call days carry no due obligation: no VMI minimum fee, no ship-to review, no pricing renewal write, no past-due item.
  - The personas are unchanged and still match the worlds.
- [x] Gates on the final form: the r7 snapshot shows 7/7 OK.
- SRC-4 to SRC-9 are verified closed in both worlds. SRC-2 was not routed.
- **Remaining observations:** O15, O19.
- **The difficulty passes the source-layer audit at revision_7.**

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
