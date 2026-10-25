# Policy-task audit — fleet_business_servicing / charter-global

## charter_global_frozen
- auditor: erl-task-policy-audit (independent auditor; did not author any audited artifact)
- freeze time: 2026-10-15T20:20Z (written before any task's GT was revealed; contains nothing derived from a revealed GT)
- freeze hashes (sha256):
  - `tasks/fleet_business_servicing/fleet.extended.yaml` 0b851e523527d35d57f8454b456e1b5d4bdb51aaf68025af141016456d18d521
  - `tasks/fleet_business_servicing/task_tools.py` c669ce6eb67684096efaaab37cf4fae13c5978fa160b8153874278cb2abb08d3
  - masked views `.audit_views/policy/fleet_business_servicing/0.json` c01382ded42a4a45…, `1.json` 025b585a5cd5f16a… (match the coordinator brief)
- fields permitted: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml of this scenario), the extended charter, task_tools.py, masked views (frozen_time, user_scenario, initial_state), erlbench/, skill scripts (DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py`).
- fields masked until reveal: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*, worklog.md (difficulty and scenario root). None opened before freeze.
- entry conditions (Step 0): gate snapshot supplied in the brief (`.audit_views/policy/fleet_business_servicing/snapshot_r1.txt`): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability misses are only the unlock tool-name provenance (pre-render), validate_scenario INVALID only for `documents: 0` (pre-render). Masked views supplied with hashes. Inputs complete.
- base copy: lines 1–1716 of the extended charter are byte-identical to `blueprint/products/fleet.yaml` (`diff` empty).

### policy_conflict_scan
Six extended policies, each `computes: amount`, each on a distinct subject/target tool:

| policy | subject | target tool (owner) | scope sentence |
|---|---|---|---|
| fleet_ext_closed_end_termination_charge (ET) | fleet_unit_charge | bill_early_termination_18cdd752 (agent) | closed-end unit turned in before scheduled end |
| fleet_ext_closed_end_mileage_charge (EM) | fleet_unit_charge | bill_excess_mileage_e7ed45ad (agent) | excess-mileage charge on a turned-in closed-end unit |
| fleet_ext_latest_month_late_charge (LC) | fleet_late_charge | assess_late_charge_6db1a799 (agent) | late charge on the unit's most recent invoice month |
| fleet_ext_turned_in_unit_refund (RF) | fleet_credit_refund | request_credit_refund_a747b6b6 (user) | credit balance on a turned-in unit, before close |
| fleet_ext_trac_shortfall_charge (D) | fleet_trac_deficiency_charge | bill_trac_deficiency_eb6903d6 (agent) | TRAC sale-settlement deficiency |
| fleet_ext_deficiency_arrangement_payment (PA) | fleet_payment | remit_arrangement_payment_506aa8ae (user) | first payment of a TRAC-deficiency arrangement |

- ET and EM share subject `fleet_unit_charge` but bill different `fee_type`s (early_termination_fee / excess_mileage_charge); the base sentence each replaces is a different clause of `fleet_termination`; no overlap of quantity.
- LC vs base late charge: split by invoice month (most recent vs earlier); base grace (`late_grace`) and dedup (`one_late`) inherited.
- RF vs base refund: split by unit state (turned-in, not closed vs closed). D vs base TRAC: deficiency only; surplus/even/closed-end stay base. PA vs base deficiency due date: arrangement at the business's request only.
- Cross-category read boundaries: all reads are `status`/`days_past_due`/`contract_date`/`past_due_amount`/`fees_due_balance` on retail/balloon and `status`/`variant_name`/`vin` on care; consistent with each policy's `cross_category` declaration.
- Scope partition derived from the prerequisite graph (to be compared with `charter_scope` at reveal): tree A = {RF ← ET, EM, LC}; tree B = {PA ← D}. Pairwise disjoint, jointly cover all six policies.
- No two policies reach incompatible conclusions on a shared subject/trigger/time anchor. One base↔extended conflict on an intermediate quantity is recorded as finding P-1 below.

### rule_compute_equivalence
Every binding's `compute_basis` quotation was located verbatim in its policy's `rule`; sweep back done sentence by sentence.
- ET: months-left (MONTHS turn_in→scheduled_end), fee ladder (≤6 half / 7–11 ×m/12 / ≥12 full), upfit multiplier (medium-duty & <36 mo → 1.25; other class with upfit×100 > 10×chassis & <36 mo → 1.10; else 1 — the else-branch reaching tier 2 for a ≥36-month medium-duty unit is unreachable, so equivalent), notice credit (≥50 / 40–49 / <40 days), relationship credit (both / one / neither, EXISTS active), usage addition (>82 / >66 mi per day), care credit (Platinum family / other plan / none), result order (×multiplier, −credits floored at 0, +addition, one rounding). Equivalent.
- EM: driven, class rate (K constants equal to `closed_end_excess_mileage_rate_by_class` in every tier), allowance ladder (days-based when turned in early after ≥ minimum_term_months; term-based on/after scheduled end; months_in_service otherwise), relationship miles, rate reduction (None-safe: no retail contract ⇒ `None != 0` ⇒ $0.03 tier, matching "no active retail installment contract with no days past due"), utilization, maintenance, result order (miles over → rate → priced amount, one rounding). Equivalent.
- LC: latest invoice fields via LATEST by txn_date; base-part ladder; rate ladder (balloon dpd 0 ∧ 12-month late-charge COUNT); floor by tenure to today; lateness by DAYS(due, NOW); wind-down; delinquency addition; result order (minimum first, multipliers, addition, one rounding). Equivalent **except** `lc_paid` — see P-1.
- RF: credit = −charges_due_balance; setoff ladder; toll ladder (13-state list matches the compute list exactly); reserve ladder (10 % × wear-cap % × cap cost / flat $300 / none); clearing holdback (`within_months=1` ⇔ "less than one whole month before today" under the DSL's `0 <= MONTHS < 1`). Equivalent.
- D: book retired = LATEST settlement `amount`; gross; actual expenses; remarketing ladder; expense allowance ladder (DAYS turn_in→sale_date); term relief (MONTHS in_service→turn_in vs term_months / 24); notice credit ('' guarded); payment-history credit; balloon-tenure credit; result order (shortfall floored, ×(1−relief), −credits floored, one rounding). Equivalent.
- PA: arranged balance; months ladder (MN 12 / MX 1 of MONTHS(NOW, scheduled_end)); share ladder; minimum ladder (SUM of deficiency charges on the unit); up-front count ladder; result `MN(balance, down + upfront × (balance − down)/months)`. Equivalent.
- Every factor ladder tier appears both in the rule prose and as a branch of its `decides` binding; no tier lives in one face only.

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). The shared tools are reads plus `verify_customer_identity` and `transfer_to_human_agent`; no shared write posts a unit charge, late charge, deficiency, payment or refund, so every state-form edge has exactly one resolving write in this difficulty.
- uuid8s: 18cdd752, e7ed45ad, 6db1a799, a747b6b6, eb6903d6, 506aa8ae — no shared prefix/suffix, no sequence, no reuse. PASS.
- Tool bodies: each performs one `create` + one `update` of `charges_due_balance`; none checks status, prerequisite, amount or eligibility (no refusal, no hint). PASS.
- Docstrings: no gold-like example values. Ordering words: the four agent tools say the unit id is "read from the fleet unit lookup for the business before the call", and the remit tool says it "remits the first payment of a payment arrangement" — neither names another write tool nor states a cross-problem order (observation O-2).

### prerequisite_graph
- `prerequisite` present on all six policies (`[]` on ET, EM, LC, D).
- Edges: RF→ET, RF→EM, RF→LC (all `value_input`, gate `rf_credit`, form `state`); PA→D (`value_input`, gate `pa_balance`, form `state`). All `problem`s are extended ids in this file; graph acyclic (two stars).
- `policy_source` of each edge is a verbatim sentence of the blocked policy's own rule (RF rule sentences 2, 3, 4; PA rule sentence 2). No `fallback_reason` (none needed: all state form).
- `resolved_by` = the depended-on policy's `target_tool` in all four; each tool raises `charges_due_balance` by the amount, which moves `rf_credit` (down) / `pa_balance` (up) — `effect` holds. `gate` names exist in the blocked compute.
- `condition` texts match the sentences' strength (ET "turned in before its scheduled end date"; EM "driven beyond its allowance"; LC "went unpaid past its grace period"; D "sale settlement shows trac_result deficiency").
- The PA edge's `effect` asserts the charge raises the balance "from zero" — a world assertion in charter text (observation O-3).

### prerequisite_sentences
Four-point test, per edge:
1. RF→ET: "The refund is not made until the unit's ledger carries the early termination charge owed for a closed-end unit turned in before its scheduled end date." Connective "not … until"; record-visible state (a ledger unit charge); no tool/id/snake_case; scope = closed-end early turn-in. Reader derivation: "ledger carries the early termination charge" → the only rule describing that charge is ET's ("the early termination charge billed is figured as this policy states") → bill_early_termination. Single reading. PASS.
2. RF→EM: "Nor is the refund made until the unit's ledger carries the excess mileage charge owed for the miles a turned-in closed-end unit was driven beyond its allowance." → EM rule ("For the excess mileage charge billed on a closed-end commercial unit that has been turned in") → bill_excess_mileage. PASS.
3. RF→LC: "The refund is figured only after the unit's ledger carries the late charge owed on the unit's most recent rental invoice month once that month's grace period has fully run out." → LC rule ("For the late charge assessed on a unit's most recent rental invoice month") → assess_late_charge. PASS.
4. PA→D: "The first arrangement payment is fixed only after the unit's ledger carries the deficiency charge billed for its sale settlement." → D rule ("For the deficiency billed when a TRAC unit's sale settlement falls short of its book value") → bill_trac_deficiency. PASS.
- Depended-on rules (ET, EM, LC, D) do not restate the sentences; no rule carries a second wording, a tool name or another policy id. No rule states a cross-problem order that grounds no declared edge. Base sentences with order ("The unit schedule closes once its charges due are zero") ground no edge.

### override_declarations
Sentence-by-sentence against `base_policy_refs`:
- ET (fleet_termination, fleet_unit_pricing, fleet_default_and_recovery): replaces "A closed-end commercial unit ended before scheduled_end_date is billed closed_end_early_termination_fee;" — declared. Notice, lapse, withdrawal, minimum-term, wear-cap, rentals-through-turn-in, pricing and default sentences followed. PASS.
- EM (same refs): replaces "at any end it is billed excess mileage … months_in_service divided by 12" — declared; purchase-ended units and wear stay base. Uses `minimum_term_months` (defined in base as a TRAC parameter) as a closed-end proration threshold, named explicitly in the rule (observation O-5). PASS.
- LC (fleet_billing_and_payments): replaces "The late charge is late_charge_pct_of_past_due percent of fleet_msr_past_due_invoice_amount, but never less than late_charge_min." — declared (also covers the base formula's rounding point). Grace, dedup, status, channel sentences inherited. The base posting sentence "…is applied to the oldest unpaid invoice month first unless the remittance names the months it pays" governs the intermediate "payments applied to that invoice month" and is not followed by `lc_paid` — finding P-1.
- RF (fleet_billing_and_payments): replaces "A credit balance left on a unit after it closes is refunded within refund_days calendar days." — declared. PASS.
- D (fleet_trac_settlement): replaces "Net proceeds are gross_sale_proceeds less sale_expenses less remarketing_fee for the tier" and "when they fall short the shortfall is billed as a deficiency" — declared. Whether a settlement "falls short" (the scope gate) is still the base net-proceeds test recorded as `trac_result`; extended net proceeds can then floor the charge at 0 (observation O-4). PASS.
- PA (fleet_billing_and_payments, fleet_trac_settlement): replaces "due trac_deficiency_payment_days calendar days after the settlement invoice" — declared; payment status (`sold` allowed) and channel sentences followed. PASS.
- No 0/1 multiplier and no dropped base branch found.

### factor_ladders
| policy | factor | label | decides | tiers | multi-source tier | cross_difficulty | ladder realism |
|---|---|---|---|---|---|---|---|
| ET | et_remaining_term_basis | method | et_fee | 3 | no | – | ok |
| ET | et_upfit_load_schedule | parameter | et_upfit_load | 3 | yes (class/upfit ∧ months) one record | – | ok |
| ET | et_notice_lead_credit | parameter | et_notice_credit | 3 | no | – | ok |
| ET | et_relationship_holdings_credit | parameter | et_relationship_credit | 3 | yes (retail ∧ balloon) | retail (+balloon) | ok |
| ET | et_usage_intensity_addition | parameter | et_usage_addition | 3 | no | – | ok |
| ET | et_care_coverage_credit | parameter | et_care_credit | 3 | no | care (no difficulty) | **F-1** |
| EM | em_allowance_proration | method | em_allowance | 3 | yes (before end ∧ ≥ min term) | – | ok |
| EM | em_relationship_free_miles | parameter | em_relationship_miles | 3 | no | retail | ok |
| EM | em_rate_relief | parameter | em_rate_reduction | 3 | yes (balloon ∧ retail) | balloon (+retail) | ok |
| EM | em_utilization_scale | parameter | em_utilization | 3 | no | – | **F-2** |
| EM | em_maintained_unit_scale | parameter | em_maintenance | 3 | no | care | **F-1** |
| LC | lc_invoice_part_basis | method | lc_base | 3 | yes (date ∧ turn-in) | – | ok |
| LC | lc_relationship_rate | parameter | lc_rate | 3 | yes (balloon ∧ unit ledger) | balloon | ok |
| LC | lc_tenure_minimum | parameter | lc_floor | 3 | no | – | ok |
| LC | lc_lateness_scale | parameter | lc_lateness | 3 | no | – | ok |
| LC | lc_wind_down_scale | parameter | lc_wind_down | 3 | yes (notice ∧ turn-in) | – | ok |
| LC | lc_cross_account_addition | parameter | lc_delinquency | 3 | no | retail | observation O-6 |
| RF | rf_retail_setoff | parameter | rf_setoff | 3 | no | retail | ok |
| RF | rf_toll_reserve | parameter | rf_toll | 3 | yes (date ∧ title state) | – | ok |
| RF | rf_condition_reserve | method | rf_reserve | 3 | yes (lease type ∧ date) | – | ok |
| RF | rf_clearing_holdback | parameter | rf_hold | 3 | yes (checks ∧ ACH) | – | **F-3** |
| D | d_relationship_remarketing | parameter | d_remarketing_fee | 3 | yes (retail ∧ balloon) | balloon (+retail) | ok |
| D | d_sale_expense_allowance | method | d_expenses_allowed | 3 | no | – | ok |
| D | d_term_completion_relief | parameter | d_term_relief | 3 | no | – | ok |
| D | d_notice_lead_credit | parameter | d_notice_credit | 3 | no | – | ok |
| D | d_payment_history_credit | parameter | d_history_credit | 3 | no | – | ok |
| D | d_balloon_tenure_credit | parameter | d_tenure_credit | 3 | no | balloon | ok |
| PA | pa_term_months_rule | method | pa_months | 3 | yes (before end ∧ balloon) | balloon | ok |
| PA | pa_down_share_schedule | parameter | pa_share | 3 | no | – | ok |
| PA | pa_minimum_down_schedule | parameter | pa_minimum | 3 | no | – | ok |
| PA | pa_upfront_count_schedule | parameter | pa_upfront | 3 | no | retail | ok |

- Counts: ET 6 (1 method/5 parameter), EM 5 (1/4), LC 6 (1/5), RF 4 (1/3), D 6 (1/5), PA 4 (1/3). All within 4–6, ≥2 parameter, ≥1 method. Each factor's bindings are disjoint and `decides` an input, never `result`.
- Distinct outcomes: checked against every tier's parameter values — e.g. LC rate 1.00/1.25 vs `late_charge_pct_of_past_due` 1.5 in all six tiers; LC floor 15/20 vs `late_charge_min` 25 in all tiers; D remarketing 150/250 vs `remarketing_fee` 395/395/350/325/295/275; EM class rates equal the variant map in all tiers. No two tiers of any ladder share a value or method.
- Labels honest: every `method` factor changes the formula in at least one tier (half/prorate/full; components vs net-of-tax vs gross; days- vs term- vs months-proration; percent-of-cap vs flat vs none; capped vs actual expenses; computed months vs fixed 3 vs 1).
- Fall-through tier = factor baseline = what `baseline.rule` states, for all 31 factors. Every `baseline.rule` sentence is in its rule and yields a definite number (ET fee; EM months-based allowance × class rate; LC gross-less-payments × tier % floored at tier minimum; RF whole credit balance; D tier-fee net proceeds; PA whole balance).
- Ladder realism: three charter-wide REDs, F-1, F-2, F-3 below.

### findings

**P-1 — SOURCE-POLICY RED (rule/compute + undeclared base handling of an intermediate) — bears on task 0**
- Symptom: `lc_paid` counts only payments whose `billing_period` equals the invoice month.
- Root cause: the LC rule defines the late-charge base by "the business payments applied to that invoice month"; the inherited base posting sentence says a payment "is applied to the oldest unpaid invoice month first unless the remittance names the months it pays". The compute `lc_paid: "SUM('fleet_transactions', 'amount', event_type='fleet_payment', billing_period=lc_inv_period)"` treats a remittance that names no month as applied to no month. The overwrite does not name the posting sentence. Class members: `lc_paid` only (no other binding reads payment application; base measure `fleet_msr_past_due_invoice_amount` carries the same phrase).
- Consequence: on any world holding an unnamed remittance received while the latest month is unpaid, the rule + base give one base and the compute another. Demonstrated against task 0's world in `0.md` (22.87 vs 22.38, refund 1509.98 vs 1510.47).
- Affected: `fleet.extended.yaml` → fleet_ext_latest_month_late_charge `compute.lc_paid` / `compute_basis.lc_paid`; base `fleet_billing_and_payments` rule sentence 3.

**F-1 — SOURCE-FACTOR RED (unreal ladder: tier no fleet unit can be on) — bears on task 0**
- Symptom: `et_care_coverage_credit` tier 2 ("covered by an active Kestrel Care contract on any other plan" → $60) and `em_maintained_unit_scale` tier 2 (same condition → 0.95).
- Root cause: `blueprint/products/care.yaml` rule care_eligibility_and_pricing: "commercial use is covered only where commercial_use_allowed is true"; variants: Powertrain/Gold/Gold Plus `commercial_use_allowed: false`, Platinum/Platinum Plus/Platinum Elite `true`. Every Kestrel Commercial Fleet Lease unit is a business-use work vehicle (blueprint: "Businesses lease work trucks, vans and cars under the Kestrel Commercial Fleet Lease"). So the "other plan" tier names a coverage the care charter forbids on any fleet unit; tier 1 ("Platinum, Platinum Plus or Platinum Elite") is exactly the set of plans that may cover one. Each ladder therefore has two reachable tiers, not three.
- Class members (complete): et_care_coverage_credit (tier 2), em_maintained_unit_scale (tier 2). No other factor reads care.
- Consequence: demonstrated in `0.md` — task 0 puts its customer on exactly that tier through a seeded Kestrel Care Gold contract on fleet unit 512's VIN, a row the care charter cannot produce.

**F-2 — SOURCE-FACTOR RED (unreal tier values) — bears on task 0**
- Symptom: `em_utilization_scale` multiplies the excess-mileage charge by 0.80 where miles driven exceed 82 a day and 0.90 where they exceed 66, i.e. the harder a unit was driven past its allowance, the less each excess mile costs.
- Root cause: the excess-mileage charge compensates the lessor for residual value lost per extra mile; no lessor reduces that charge because the lessee used the vehicle more intensively. The charter itself prices the same fact the other way: `et_usage_intensity_addition` adds $150 / $75 to the early termination charge on the identical >82 / >66 miles-a-day conditions, for the same turn-in. Tier values 0.80 and 0.90 are treatments no captive fleet lessor would publish.
- Consequence: demonstrated in `0.md` (customer on the 0.90 tier; 1197.76 with it, 1330.84 without).
- Affected: fleet_ext_closed_end_mileage_charge rule sentence "The priced amount is multiplied by the mileage utilization multiplier…", `params.utilization_multiplier_high/mid`, factor `em_utilization_scale`.

**F-3 — SOURCE-FACTOR RED (unreal compound condition part) — charter-wide, no task number moves**
- Symptom: `rf_clearing_holdback` holds recent ACH debits only "where none were [business checks posted]".
- Root cause: a funds-availability hold exists because an item can still be returned; an ACH debit drawn less than a month ago is returnable whether or not the business also mailed a check. The condition part "no business check posted to the unit less than one whole month before today" is not something a lender weighs when deciding to hold ACH-debit funds; a business that paid both ways would have its ACH debits released untested. That ladder exists only to keep tiers mutually exclusive.
- Consequence: the condition is named (demonstration form "name a condition … that no business in that line weighs"). Neither task holds an ACH-debit payment, so no scored number moves; the defect is in the published ladder.
- Affected: fleet_ext_turned_in_unit_refund rule sentence "The refund clearing holdback is …", `compute.rf_hold`, factor `rf_clearing_holdback`.

**Observations (not grounds for rework)**
- O-1 first-match reads of "the business's active … contract" (singular rule wording, `CFIELD` returns the first match): em_relationship_miles (retail contract_date), em_rate_reduction (balloon & retail dpd), lc_rate (balloon dpd), lc_delinquency (retail dpd), rf_setoff (retail dpd/past_due/fees), d_tenure_credit (balloon contract_date), pa_months (balloon dpd), pa_upfront (retail dpd). Both tasks seed exactly one active retail and one active balloon, so no number depends on which row is first.
- O-2 docstring ordering words: "before the call" (four agent tools, about reading the unit id); "the first payment of a payment arrangement" (remit tool). Neither states a cross-problem order.
- O-3 PA edge `effect`: "raises the unit's charges due balance from zero to the charge" asserts a world fact in charter text.
- O-4 D scope: whether a settlement "falls short" is decided by the base net-proceeds test (`trac_result`); the extended net proceeds can then floor the charge at zero.
- O-5 EM allowance tier 1 uses `minimum_term_months`, a parameter the base schema describes for TRAC units, as a closed-end proration threshold; named explicitly, so unambiguous.
- O-6 realism, not demonstrated: `lc_cross_account_addition` adds $10/$15 to a fleet late charge because a separate retail contract is past due; `lc_wind_down_scale` discounts a late charge because the unit is being terminated; the ET/EM care credits tie a vehicle service contract to lease-end charges. These are relationship concessions of a kind captives use, and are kept as observations.
- O-7 RF setoff: the setoff holdback is withheld from the refund, but no policy posts it to the retail contract.

## closing_checklist
Status: **NOT CLOSED, round 1.** Written after the reveals (GT first opened 2026-10-15T20:21:26Z; the charter-global section above was frozen at 20:19:35Z, sha256 1659c9f3…, and is unchanged).
- Per-task files: `0.md` and `1.md`, one per task, alongside this file. Each has a frozen derivation and an appended `source_gt_comparison`. First revision, no older revisions.
- Scope: GT `charter_scope` task 0 = {ET, EM, LC, RF} + their four tools; task 1 = {D, PA} + their two tools. This equals the partition derived pre-reveal in §policy_conflict_scan: pairwise disjoint, jointly covering all six extended policies and all six task tools. Each task tool has an independent uuid8.
- Problem trees: task 0 has 3 prerequisite problems with 3 `value_input` edges, user write = refund. Task 1 has 1 prerequisite problem with 1 `value_input` edge, user write = arrangement payment. Both are acyclic, and the difficulty-wide graph is two disjoint stars. PASS.
- Computations: all 6 declare a self-sufficient baseline giving a definite number ≠ gold; every factor bears weight against an honest baseline on its task's world (figures match GT sensitivities one for one). Open:
  - F-1 strikes the two care ladders;
  - F-2 strikes em_utilization_scale (EM then has 3 surviving factors, < 4);
  - F-3 is an unreal compound condition in the rf_clearing_holdback ladder;
  - T1-1: task 1's deficiency computation has no near-miss.
- Unique solution: task 1 PASS. Task 0 has two defensible late-charge / refund values (T0-1 from P-1).
- Gates: not re-run by this auditor (Step 0: the coordinator's snapshot r1 is cited). A re-run on the final form belongs to the round that closes these findings.

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | SOURCE-POLICY RED (P-1) | PASS | SOURCE-FACTOR RED (F-1/T0-2, F-2/T0-3) | SOURCE-TASK RED (T0-1) |
| 1 | PASS | PASS | SOURCE-FACTOR RED (T1-1) | PASS |

Charter-wide REDs: P-1 (lc_paid vs base payment-application sentence), F-1 (care "other plan" tiers unreachable for commercial fleet units: et_care_coverage_credit, em_maintained_unit_scale), F-2 (em_utilization_scale discounts heavier use), F-3 (rf_clearing_holdback holds ACH debits only when no check was posted).

task0=SOURCE-POLICY RED task1=SOURCE-FACTOR RED
charter=P-1,F-1,F-2,F-3

## revision_2

### charter_global_frozen (revision_2)
- Re-audit round 2, the same independent auditor. Gating line checked: `tail -1 tasks/fleet_business_servicing/worklog.md` = "REWORK round 2: gates 8/8 green". Gate snapshot: `.audit_views/policy/fleet_business_servicing/snapshot_r2.txt` (2026-10-15T23:27:48Z). EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE are all OK. The traceability miss is the unlock tool-name provenance only, and validate is INVALID only on `documents: 0`; both are expected pre-render.
- Hashes: charter `fleet.extended.yaml` 4a36ed18efaadbc5… and `task_tools.py` db4c63aa39a18208… both **changed** from round 1, so every charter-global section is re-derived in full below. Masked views: 0.json 9880b78de6f27b18…, 1.json 0a339f094eb31958…. Blueprint products, db_schema and share_tools match `/tmp/erl0066_coord/blueprint_freeze.sha256`. Base copy is still byte-identical to `blueprint/products/fleet.yaml`.
- Written before reading the worklog's "REWORK round 2 closure" and before opening any round-2 task JSON. contamination_disclosure: the round-1 GT of both tasks was seen in revision 1 (inherent to a re-audit). Every round-2 figure below was recomputed from the round-2 charter and masked views.
- XF recipe (`audits/render_source/XF_recipe.md`, 12 points) checked on all six policies. Members are REDs.

### re-derived charter checks (revision_2)
- Conflict scan / scope: the same six policies, subjects and target tools. Trees are unchanged: {RF ← ET, EM, LC}, {PA ← D}. A new base↔extended interaction is the PA overwrite of the posting clause (see R2-C2).
- Rule/compute equivalence:
  - A script sweep finds every `compute_basis` quote, `policy_source`, `replaced_by` and `baseline.rule` sentence verbatim in its own rule (XF-5 clean), and every superseded clause verbatim in its base rule.
  - All cross-category `CFIELD` first-match reads are gone; they are replaced by `EXISTS(…, days_past_due=0)` and `XCOUNT` over retail/balloon ledgers (closes O-1).
  - New compute branches checked both ways:
    - EM: relationship miles by retail_funding age; unit-age addition.
    - LC: delinquency addition by retail late-charge count.
    - RF: delinquency reserve; clearing holdback over checks + ACH debits by unit late-charge count.
    - D: tenure by balloon_funding age; the "recorded deficiency stays in scope" sentence.
    - PA: up-front count by retail late-charge count; negative months → 1.
  - **Exception: `lc_paid`, R2-C1.**
- Action binding / uuids: unchanged ids (18cdd752, e7ed45ad, 6db1a799, a747b6b6, eb6903d6, 506aa8ae), one policy each. Bodies are still unconditional create + update. "before the call" and "first payment" are removed (closes O-2). **Exception: remit docstring effect claim, R2-C3.**
- Prerequisite graph / sentences: the same four state-form edges with identical `policy_source` sentences. Each is still verbatim in the blocked rule, with one resolving write each. The PA `effect` no longer asserts "from zero" (closes O-3). The RF→LC `effect` now also names the 12-month late-charge history that the clearing holdback reads. That is accurate: the LC write moves both the credit and the holdback tier.
- Factor ladders (structure):
  - Counts: ET 6 (1 m), EM 5 (1 m), LC 6 (1 m), RF 4 (1 m), D 6 (1 m), PA 4 (1 m). Every tier is distinct; fall-through = baseline = `baseline.rule` input. No factor reads another factor's binding (script check; XF-3 clean). The shared record selections `lc_inv_date` and `lc_inv_period` are plain bindings stated once ("The most recent rental invoice is …").
  - F-1 closed: the care ladders are now Platinum Plus/Elite / Platinum / none, and every tier is a plan the care charter lets cover a commercial vehicle.
  - F-2 closed: `em_utilization_scale` is removed and replaced by `em_unit_age_addition` (+$0.05 / +$0.02 a mile for units turned in under 24 / 24–35 months). A surcharge for early-returned young units is a treatment a lessor would publish.
  - F-3 closed: the holdback now covers both returnable channels, and its tier is the unit's 12-month late-charge history (a risk-based hold).
  - New ladders `rf_retail_delinquency_reserve` and `pa_upfront_count_schedule` (retail late charges in 6 months) are realistic credit-risk terms. `lc_cross_account_addition` now reads retail late charges and remains observation O-6.
- XF points 1, 2, 4, 6, 7, 10 and 12-in-charter: no member found.
  - Assembly/order sentences are generic and fix the order (ET, LC, D "schedule … first; multiplier/relief …; credit …; addition last"; EM "miles over, then per-mile rate, then priced amount"; RF "every holdback"; PA "in the order the standard method sets out").
  - Ties are stated for both LATEST reads (LC invoice, D settlement).
  - Counting conventions are stated in every policy and match `MONTHS`/`DAYS`/`_within`.
  - Rounding is once, at the end, everywhere.

### findings (revision_2, charter-wide)
**R2-C1 — SOURCE-POLICY RED (XF-8: a rule branch absent from compute; residual of P-1)**
- The LC rule now states: "The business payments applied to an invoice month are the payments the unit's ledger records against that month: a remittance is applied to the months it names, and a remittance naming no month to the oldest unpaid invoice month first."
- The compute is unchanged: `lc_paid: "SUM('fleet_transactions', 'amount', event_type='fleet_payment', billing_period=lc_inv_period)"`. It has no branch for a remittance naming no month (`billing_period` empty).
- The rule branch "a remittance naming no month to the oldest unpaid invoice month first" is therefore not in the compute. On any world where such a remittance is posted while the latest month is unpaid, rule and compute give different late-charge bases (the round-1 task-0 world was exactly that case: 22.38 vs 22.87).
- The round-2 task-0 seed no longer contains such a row (both remittances name months), so no scored number moves. The charter defect remains.

**R2-C2 — SOURCE-POLICY RED (XF-9: base-clause restatement / deferral). All members:**
1. EM retires the whole base clause "at any end it is billed excess mileage at … divided by 12". Its `replaced_by`/rule restates only the purchase ending ("a closed-end commercial unit ended by purchase is billed excess mileage … as before"). The other still-in-force ending, a closed-end unit **recovered after an uncured default** (lifecycle defaulted → off_road, "The unit is recovered after an uncured default"; no turn-in), is not restated. Excess mileage for that unit now has no rule. ET's own replaced_by ("ended before its scheduled end date in any other way … as before") shows the restatement that EM lacks.
2. D retires "Net proceeds are gross_sale_proceeds less sale_expenses less remarketing_fee for the tier". It restates that clause only "for a sale surplus or an even result" and then says "every closed-end unit remains under the base rule". For closed-end settlements (trac_result not_applicable) the rule defers to the base clause its own overwrite retired.
3. PA retires the base posting clause "is applied to the oldest unpaid invoice month first unless the remittance names the months it pays" for arrangement payments ("never to a rental invoice month"). The LC rule restates that same clause as in force without naming the sibling's case: "a remittance naming no month to the oldest unpaid invoice month first". An arrangement payment is booked naming no month (`billing_period=""` in `remit_arrangement_payment_506aa8ae`). For a unit holding an arrangement payment and an unpaid latest invoice month, LC's sentence applies the payment to that month while PA's says never. Two rules give two conclusions.

**R2-C3 — SOURCE-POLICY RED (XF-11: a docstring/rule claims an effect the tool cannot have)**
- `remit_arrangement_payment_506aa8ae` docstring: "One business payment is booked … naming the arranged deficiency and no rental month". The body writes `remittance_reference=rid` (the payment's own id) and `billing_period=""`, and nothing that names or links the deficiency charge. `fleet_transactions` has no field that could (db_schema).
- The PA rule sentence "An arrangement payment names the arranged deficiency it pays and is applied to that deficiency on the unit" states the same unrecordable effect.

**Observations (revision_2)**
- O2-1: ET/EM care ladders. Rule tier 3 reads "nothing/1 where no active Kestrel Care contract covers it", while the compute fall-through also catches an active Powertrain/Gold/Gold Plus contract on the VIN. That state cannot be produced: the care charter forbids those plans on a commercially used vehicle, and every fleet unit is one. So this is not an XF-8 member.
- O-6 (carried): `lc_cross_account_addition` surcharges a fleet late charge for retail late charges.

### round-1 RED closure check (revision_2, after reveal)
| round-1 item | claim (worklog "REWORK round 2 closure") | verified on disk | status |
|---|---|---|---|
| P-1 | rule restates posting sentence; task-0 seed remittances name months | task-0 world consistent; compute `lc_paid` still lacks the unnamed-remittance branch the rule now states | **open at charter level as R2-C1** (task consequence closed) |
| F-1 / T0-2 | care ladders Platinum-family only; Platinum seed row | yes; care row within Platinum options and caps | closed |
| F-2 / T0-3 | utilization replaced by unit-age addition | yes | closed |
| F-3 | hold covers checks + ACH debits, tier by late-charge history | yes | closed |
| T0-1 | single defensible value | yes (no unnamed remittance; dpd 18 reconciles) | closed |
| T1-1 | near-misses seeded | yes (posting vs sale date → 4,077.00; 13-month late charge → 3,957.90) | closed, but the retail rows added for it are illegal → R2-T1 |
| O-1 … O-7, T0-O*, T1-O* | as listed | O-1, O-2, O-3, O-4, O-7, T0-O1, T0-O2, T1-O2 closed; O-5 and O-6 kept by design | — |
Worklog XF table rows "9 base clauses OK" and "11 tools OK (names the deficiency)" are contradicted by R2-C2 and R2-C3.

## closing_checklist (revision_2)
NOT CLOSED.
- Per-task: task 0 PASS on all four relationships; task 1 SOURCE-FACTOR RED (R2-T1).
- Charter-wide REDs: R2-C1 (XF-8, `lc_paid`), R2-C2 (XF-9: EM recovery restatement; D closed-end defers to a retired clause; LC posting restatement omits the PA sibling case), R2-C3 (XF-11, remit docstring and PA rule claim the payment names the deficiency).
- Scope and trees: unchanged and disjoint. GT values equal blind values in both tasks. Gates cited from snapshot_r2 (not re-run by this auditor).

task0=PASS task1=SOURCE-FACTOR RED
charter=R2-C1,R2-C2,R2-C3
VERDICT revision_2: task0=PASS task1=SOURCE-FACTOR RED charter=R2-C1,R2-C2,R2-C3

## revision_3

### charter_global_frozen (revision_3)
- Re-audit round 3, the same independent auditor.
- Gating: `tail -1 worklog.md` = "REWORK round 3: gates 8/8 green".
- Gate snapshot: `.audit_views/policy/fleet_business_servicing/snapshot_r3.txt` (2026-10-16T00:06:46Z). All gates OK. The only traceability miss is unlock tool-name provenance, and validate is INVALID only on `documents: 0`; both are expected pre-render.
- Hashes: charter 3beadc43ada06dba… and tools 22a04337c82e0a92… both changed again, so every charter-global section is re-derived. Masked views: 0.json 9880b78de6f27b18… (unchanged from round 2), 1.json d19b5cfab49d6780… (changed).
- Base copy is byte-identical to the blueprint, and the blueprint matches `/tmp/erl0066_coord/blueprint_freeze.sha256`.
- Frozen before reading the worklog's "REWORK round 3 closure" or any round-3 task JSON. contamination_disclosure: GT of rounds 1–2 was seen in earlier revisions. Figures below were recomputed from the round-3 artifacts.

### re-derived charter checks (revision_3)
- Script sweep, all six policies, no member found:
  - every compute_basis quote, policy_source, replaced_by and baseline sentence is verbatim in its own rule (XF-5);
  - every superseded clause is verbatim in its base rule;
  - no factor reads another factor's binding, and no plain binding reads a factor binding (XF-3);
  - factor counts: ET 6 / EM 5 / LC 6 / RF 4 / D 6 / PA 4, each with ≥1 method and ≥2 parameter;
  - every fall-through = baseline.
- Tool bodies: still unconditional create + update; the uuid8s are unchanged and distinct. The remit docstring now says "recorded against no rental invoice month", matching `billing_period=""` (XF-11 clean). No ordering words in any docstring.
- Prerequisite graph and sentences: unchanged (four state-form `value_input` edges, verbatim sentences, one resolving write each).
- XF points 1, 2, 4, 6, 7 and 10: the assembly/order sentences, tie sentences, counting conventions and once-at-end rounding are the same as revision_2. No member found.
- XF-8: the ET/EM care fall-through now reads "no active Kestrel Care Platinum, Platinum Plus or Platinum Elite contract covers it", which matches the compute else-branch (closes O2-1). The LC payment branch now matches the compute (R2-C1 below).
- XF-9: every retired base clause is now restated for each out-of-scope case or brought inside the policy (R2-C2 below). No rule defers to a clause its own overwrite retired, and no overwrite retires a clause that never conflicted. PA's posting-clause overwrite is real: an arrangement payment names no month, and the base clause would apply it to the oldest unpaid month.

### round-2 RED closure (verified on disk, pre-reveal)
- **R2-C1 closed.** The LC rule now reads "The business payments applied to an invoice month are the payments the unit's ledger records against that month, each payment being recorded against the month it was applied to when it posted; a payment recorded against no invoice month is not counted." That is exactly `lc_paid` (SUM where `billing_period` = the latest invoice's month). Every branch now matches both ways.
- **R2-C2 closed, all three members:**
  1. ET and EM scopes now cover a closed-end unit "whose lease ended … by a turn-in or by a recovery after an uncured default". Each restates the purchase ending ("as before, and this policy's figure does not apply to it"). EM keeps wear under base. Every ending of the retired clauses is covered.
  2. D's replaced_by now restates net proceeds "for a sale surplus, an even result or the sale of a closed-end commercial unit … as before". It no longer defers to the retired clause.
  3. LC no longer restates the posting clause; it reads only the recorded month. PA's overwrite states how arrangement payments are booked ("against its charges due without being recorded against any rental invoice month"). The two rules now agree: an arrangement payment counts toward no month's late-charge base.
- **R2-C3 closed.** The "names the arranged deficiency" claim is removed from both the PA rule and the remit docstring.
- No regression of the round-1 closures (F-1, F-2, F-3, O-1…O-4, O-7).

### findings (revision_3, charter-wide)
- No RED.
- O3-1 (observation): ET and EM now fix "The turn-in date read below is the date the unit was turned in or recovered, as the unit records it" (EM also names the odometer). db_schema describes `turn_in_date` only as "date the unit was turned in", with no separate recovery-date field. The binding is stated in the rule and no task exercises a recovered unit, so no consequence can be demonstrated. ET's usage addition names the "turn-in odometer" without EM's recovery wording.
- O-5 and O-6 carried.

### worklog claims vs disk (revision_3, after reveal)
| round-2 item | claim | verified | status |
|---|---|---|---|
| R2-C1 | LC payment sentence = `lc_paid` | rule text and compute agree both ways | closed |
| R2-C2.1 | EM (and ET) cover turn-in + recovery; purchase restated | yes | closed (O3-1 observation on the recovery-date binding) |
| R2-C2.2 | D restates net proceeds for surplus / even / closed-end | yes | closed |
| R2-C2.3 | LC no longer restates the posting clause | yes; PA alone retires and restates it | closed |
| R2-C3 | PA rule and docstring say "recorded against no rental invoice month" | yes; body `billing_period=""` | closed |
| R2-T1 | retail late charges at due + 11 | yes (04-08, 10-09, 11-08) | closed |
| O2-1 | care tier-3 wording | yes | closed |
- The worklog's XF table matches what I found on disk for all 12 points × 6 policies.
- GT values are unchanged in both tasks and equal the blind values.

## closing_checklist (revision_3)
- Per-task files `0.md` and `1.md` sit beside this file, with revisions 1–3 appended in order and every comparison PASS in revision_3.
- Coverage and scope:
  - all six extended policies covered;
  - scopes disjoint (task 0: ET, EM, LC, RF; task 1: D, PA);
  - task tools and GT closed;
  - uuid8s independent.
- Trees:
  - task 0 has 3 prerequisites, all `value_input`;
  - task 1 has 1 prerequisite, `value_input`;
  - each tree includes a user write;
  - the difficulty-wide graph is acyclic.
- Factors:
  - every computation has a self-sufficient baseline giving a definite number different from gold;
  - 4–6 factors with ≥2 parameter and 1 method;
  - each task has multi-source and cross-difficulty factors;
  - every ladder has ≥3 distinct, realistic tiers stated in its rule;
  - every factor bears weight;
  - near-misses are present in every computation.
- Gates: snapshot_r3 (coordinator run, cited).
- Charter-wide: no RED. Observations O3-1, O-5 and O-6 remain.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

### charter_global_frozen (revision_4)
- Re-audit round 4, the same independent auditor.
- Gating: `tail -1 worklog.md` = "REWORK round 4: gates 9/9 green".
- Gate snapshot: `.audit_views/policy/fleet_business_servicing/snapshot_r4.txt` (2026-10-16T09:22:57Z). All gates OK, and TRACEABILITY is now OK (KB rendered). validate_scenario reports INVALID with `documents: 303`; the snapshot does not print the cause, and the gate is scenario-wide, so it is cited and not judged here.
- Hashes: charter df4ccd3161ce174c… and tools 51595cadbb1a2591… both changed, so every charter-global section is re-derived. Masked views: 0.json 8f497e3355386cfb…, 1.json e3715da72f9e7b0b…, both changed.
- Base copy is byte-identical to the blueprint, and the blueprint matches the freeze file.
- Input of this round: KB-audit source items SRC-1…SRC-5 (`audits/policy_kb/fleet_business_servicing/_difficulty.md`).
- Frozen before reading the worklog "REWORK round 4 closure" or the round-4 task JSON. contamination_disclosure: GT of rounds 1–3 was seen earlier.
- **Auditor self-correction:** none of SRC-1…SRC-5 was raised in my revisions 1–3. All five are genuine misses of this audit:
  - SRC-1/2: XF-8 branch and naming gaps;
  - SRC-3/4: XF-11 docstring claims;
  - SRC-5: task 1 never seeded the completed termination-notice request that base `fleet_termination` makes the evidence of an effective notice. That was missed in revisions 1–3 although `fleet_requests` was absent from task 1 in every round.
  The revision_3 CLEAN/PASS verdict was therefore wrong on those points.

### SRC closure (verified on disk)
- **SRC-1 closed.** Every rule, compute_basis, ladder and cross-category note that names the retail holding now says "Kestrel New Vehicle Retail Installment Sale Contract(s)" (swept: et_relationship_holdings_credit, em_relationship_free_miles, em_rate_relief, lc_cross_account_addition, rf_retail_delinquency_reserve, d_relationship_remarketing, pa_upfront_count_schedule). The name pins the retail category the compute reads. "Kestrel Advantage Balloon contract" was already unambiguous.
- **SRC-2 closed.** The ET and EM care middle tier now reads "covered by an active Kestrel Care Platinum contract but by no active Kestrel Care Platinum Plus or Kestrel Care Platinum Elite contract". That is the compute's precedence (upper tier tested first), and the three tiers are now disjoint in the rule.
- **SRC-3 closed.** The D rule reads "the deficiency charge is then booked at zero, which settles the terminal rental adjustment". The `bill_trac_deficiency_eb6903d6` amount is now "a number of zero or more", so the zero branch is bookable and PA's waited-on state ("ledger carries the deficiency charge") is reachable there.
- **SRC-4 closed.** The refund and remit docstrings now claim only "the … channel chosen recorded on it", the posting and the balance change, which is exactly what the bodies do. No fund-movement claim remains.
- **SRC-5 closed (seed).** Task 1 now holds `fleet_requests/529d9cae…`: termination_notice, completed by named signer Megan Zielinski, created and completed 2026-07-02 (= `termination_notice_date`), requested_date 2026-08-24 (= turn-in). Turn-in falls in the notice window (≥ 07-02 + 30 = 08-01; ≤ 07-02 + 60 = 08-31). The notice is effective under base Clause T1, so the deficiency notice credit has a single reading ($200; the "no effective notice" reading, 4,107.90 / 1,301.76, is excluded by the record).

### re-derived charter checks (revision_4)
- Script sweep, no member found: every compute_basis quote, policy_source, replaced_by and baseline sentence is verbatim in its own rule; every superseded clause is verbatim in base; no factor or plain binding reads another factor's binding; factor counts 6/5/6/4/6/4 (each ≥1 method, ≥2 parameter); every fall-through = baseline; prerequisite edges unchanged (four state-form `value_input`).
- Tool bodies: still unconditional create + update; uuid8s unchanged; no ordering words; no example values. Docstring effects match the bodies.
- XF 1–12 on all six policies: no member found.
  - Point 8: SRC-2 and SRC-3 are now closed. The LC payment branch still matches the compute. The ET/EM recovery binding is unchanged (O3-1 carried).
  - Point 9: the restatements from revision_3 are intact.
  - Point 11: SRC-3 and SRC-4 are closed.
- New seed rows checked for charter producibility:
  - Task 0 `fleet_requests/f9f346c8…`, delivery_acceptance completed 2024-07-01 by signer Renee Vandermolen. Delivered 2024-06-26, `delivery_acceptance_days` 5, counted from the day after delivery, so signing on day 5 is timely. Completion = `in_service_date` ✓.
  - Task 1 `fleet_requests/9289b5d2…`, delivery_acceptance completed 2024-03-01. Delivered 2024-02-26; leap year, so 4 days ✓. Completion = `in_service_date` ✓.
  - Task 1 history of the closed 2019 balloon (`a99f96e3…`):
    - `balloon_maturity_election` pay_balloon on 2022-03-10, while the contract was active and before its 2022-04-10 maturity ✓;
    - `balloon_payment` payoff 16,058.02 by wire on 2022-04-08 = final installment 428.03 + balloon 15,630.00 (interest 96.30 = 15,961.72 × 7.24 % / 12; principal 15,961.72 = 331.73 + 15,630.00) ✓;
    - `balloon_lien_release` electronic on 2022-04-11: wire carries no hold, release is within elt_release_business_days 3, recipient is the customer for a customer payoff ✓;
    - contract closed 2022-04-12 with title released_electronic ✓.
  All new rows are states their owning charters can produce.
- Observations carried: O3-1, O-5, O-6.

### worklog claims vs disk (revision_4, after reveal)
| item | claim | verified | status |
|---|---|---|---|
| SRC-1 | full product name everywhere | yes (rule / quote / ladder / note sweep) | closed |
| SRC-2 | Platinum tier excludes Platinum Plus/Elite | yes; matches the compute precedence | closed |
| SRC-3 | zero deficiency booked; tool "zero or more" | yes | closed |
| SRC-4 | docstrings describe only the recorded posting | yes; matches the bodies | closed |
| SRC-5 | completed 2026-07-02 notice request seeded and read | yes; single reading | closed |
| new rows | delivery acceptances; 2019 balloon history | all charter-producible (closed_date 2022-04-11 = release date) | OK |
- GT values in both tasks are unchanged and equal the blind values. No regression of any round-1…3 closure.

## closing_checklist (revision_4)
- Per-task files carry revisions 1–4. Every revision_4 comparison is PASS.
- Scope: disjoint and complete (task 0: ET, EM, LC, RF; task 1: D, PA). Tools: closed, with independent uuid8s.
- Trees:
  - task 0 has 3 prerequisites, all `value_input`;
  - task 1 has 1 prerequisite, `value_input`;
  - each tree includes a user write;
  - acyclic.
- Factors:
  - 4–6 per computation, each with ≥1 method and ≥2 parameter;
  - multi-source and cross-difficulty factors in each task;
  - realistic, distinct ladders;
  - every factor bears weight;
  - baselines definite and different from gold;
  - near-misses present.
- XF 1–12: no member.
- Gates: snapshot_r4, cited. The scenario-wide validate result is INVALID with the cause not printed (the KB is rendered). It is not adjudicated by this policy-task audit.
- Observations: O3-1, O-5, O-6.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (revision_5)
- Re-audit round 5 (seed-only rework for the KB auditor's SRC-6).
- Gating: `tail -1 worklog.md` = "REWORK round 5: gates 9/9 green".
- Gate snapshot: `.audit_views/policy/fleet_business_servicing/snapshot_r5.txt` (2026-10-16T11:04:27Z). All gates OK, TRACEABILITY OK, and validate_scenario is now **VALID** (373 documents).
- Hashes: charter df4ccd3161ce174c… and tools 51595cadbb1a2591… are **identical to snapshot_r4**, so the revision_4 charter-global sections carry forward by reference on these two hashes. Masked views changed (0.json f266323413b45b1e…, 1.json d80067131d15e11a…).
- contamination/order disclosure: I re-priced the retail charges independently from the published retail documents before opening the worklog's "REWORK round 5 closure". I read that section before writing this revision to disk. The GT task JSON was read only after the per-task freezes below.
- Read scope: this round's check ("what the published docs/retail rules produce") is against the agent-visible published KB `docs/retail/` (unpaid-installment late-charge hub, calculation sheet, rate schedule, graduated factor, clean-schedule / Care-plan / lessee / partial-effort point cards). The sibling difficulty's `tasks/retail_payment_servicing/` was not read.

### SRC-6 verification (seeded retail late charges vs the published retail rules)
Rule as published: starting rate 3.5 % (≥30 installments satisfied and no returned payment in 24 months), less points (clean schedule 0.5; Care plan 0.5 if financed in this contract, 0.25 if financed otherwise; lessee 0.5/0.25; partial effort 0.5/0.25), applied once to the unpaid installment portion and rounded to the cent. The graduated factor then applies, keyed to days from the next due date to the assessment date minus 10 days of grace: 1–7 days → half, rounded down to the whole dollar; 8–14 → three quarters, rounded down; otherwise kept to the cent. The cap is min(company 30.00, state 35.00).

**Task 0, contract 5307716482** (monthly 949.72): 3.5 − 0.5 (no extension or due-date change ever) − 0.25 (Care Platinum financed cash and Care Platinum Elite financed in the balloon account, both "financed some other way") − 0 (no lease) − 0 (no payment entry in the prior calendar month) = 2.75 %.

| charge date | installment | unpaid portion | figure at rate | days beyond grace | graduated | seeded |
|---|---|---|---|---|---|---|
| 2026-03-15 | 03-04 | 949.72 | 26.12 | 1 | half → 13.06 → 13.00 | 13.00 ✓ |
| 2026-06-15 | 06-04 | 949.72 | 26.12 | 1 | 13.00 | 13.00 ✓ |
| 2026-10-15 | 10-04 | 949.72 | 26.12 | 1 | 13.00 | 13.00 ✓ |

- Fee payments of 13.00 on 03-27 and 06-26 ✓; fees due 13.00 = the unpaid October charge ✓.

**Task 1, contract 5124409863** (monthly 815.70): 3.5 − 0.5 (clean schedule) − 0 (no Care) − 0 (no lease) − 0 (no recent payment entry) = 3.0 %.

| charge date | installment | unpaid portion | figure at rate | days beyond grace | graduated | seeded |
|---|---|---|---|---|---|---|
| 2026-04-08 | 03-28 | 815.70 | 24.47 | 1 | half → 12.235 → 12.00 | 12.00 ✓ |
| 2026-10-09 | 09-28 | 815.70 | 24.47 | 1 | 12.00 | 12.00 ✓ |
| 2026-11-08 | 10-28 | 1,631.40 − 815.70 = 815.70 | 24.47 | 41 − 10 = 31 (next due date 09-28) | kept | 24.47 ✓ |

- Fee payment 12.00 on 04-20 ✓; fees due 12.00 + 24.47 = 36.47 ✓.
- All charges sit on due + 11; all are below both caps. Past-due amounts (2 × monthly) are unchanged.

**SRC-6 closed.** Every re-priced row is what the published retail rule produces, and the balances agree. Fleet factors read only the count and dates of these charges (lc_cross_account_addition, rf_retail_delinquency_reserve, pa_upfront_count_schedule), and those are unchanged.

### re-derived checks (revision_5)
- Charter / tools: unchanged (hashes above). The revision_4 conclusions on XF 1–12, sweeps, ladders and the prerequisite graph carry forward; no member.
- No other cross-category row moved in a way that affects any computation: all 31 single-factor swap results and all 6 scored values recompute identically to revision_4.

### worklog claims vs disk (revision_5, after reveal)
| item | claim | verified | status |
|---|---|---|---|
| SRC-6 | retail charges re-priced by the published rule (task 0: 13.00 × 3; task 1: 12.00, 12.00, 24.47); fee payments and fees due adjusted | yes, recomputed independently from docs/retail (table above) | closed |
| charter/tools unchanged | df4ccd31… / 51595cad… | yes (snapshot_r4 = snapshot_r5) | OK |
| scored values unchanged | 290.00 / 1451.83 / 27.87 / 1965.25; 3907.90 / 1257.31 | yes (blind = GT) | OK |
| proof text current | business-object cards | yes; no stale amount | OK |

## closing_checklist (revision_5)
- Revisions 1–5 are present in all three files, and every revision_5 comparison is PASS.
- Scope, trees, factors and XF 1–12 are as closed in revision_4. The charter and tools are byte-identical.
- Seed: all cross-category rows are producible by their owning charters, including the re-priced retail late charges.
- Gates: snapshot_r5, all green, validate VALID.
- Observations carried: O3-1, O-5, O-6.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN
