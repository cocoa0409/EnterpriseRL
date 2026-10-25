# Policy-task audit — vehicle_purchase_deals / charter-global

## revision_1

## charter_global_frozen
- auditor: erl-task-policy-audit (independent auditor, coordinator dispatch), freeze time 2026-10-22 (before any GT reveal).
- freeze hashes (sha256 12-char): `purchase.extended.yaml` 1a68702ec9bd, `task_tools.py` 908f3efa4823 (match the coordinator gate snapshot). Views: r1/0.view.json 836583dbe498bb59, r1/1.view.json 0fa3ef1e75133f2f.
- entry conditions (Step 0): gate snapshot supplied (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred), masked views supplied with hashes. Complete.
- read: blueprint (blueprint.yaml outline, db_schema.json, share_tools.py signatures, products/purchase.yaml, products/service.yaml), `purchase.extended.yaml`, `task_tools.py`, `audits/render_source/XF_recipe.md`, the two masked views, the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/CFIELD/X* semantics). Not read: tasks/*.json, plan.md, worklog.md, any other scenario. No recursive grep over tasks/ or the scenario tree.
- base copy: `head -1088 purchase.extended.yaml` is byte-identical to `blueprint/products/purchase.yaml` (diff empty).
- Nothing in this section is derived from a revealed GT.

### policy_conflict_scan
Six extended policies:

| policy | scope (deal type) | subject / computes | target_tool (owner) | prerequisite |
|---|---|---|---|---|
| purchase_ext_fleet_delivery_fee | Fleet, home-delivered | purchase_charge_reversed / reversal_amount | reverse_fleet_delivery_fee_7a0a59bd (agent) | [] |
| purchase_ext_fleet_unit_incentive | qualifying Fleet deal | purchase_payment_posted / incentive_amount | credit_fleet_incentive_b735a70c (agent) | [] |
| purchase_ext_fleet_late_balance_fee | Fleet | purchase_charge_posted / fee_amount | post_fleet_late_fee_7ed43dd7 (agent) | delivery_fee (value_input), unit_incentive (value_input) |
| purchase_ext_fleet_order_deposit | reserved Fleet | purchase_deposit_received / deposit_amount | pay_fleet_order_deposit_c9caca35 (user) | late_balance_fee (state_gate) |
| purchase_ext_extension_deposit | reserved non-Fleet | purchase_deposit_received / deposit_amount | pay_extension_deposit_9124466d (user) | [] |
| purchase_ext_hold_extension_days | reserved non-Fleet | purchase_hold_extended / extension_days | extend_vehicle_hold_21e7c68f (agent) | extension_deposit (value_input) |

- Overlapping subjects are split by deal type: the two deposit policies (Fleet vs non-Fleet), late fee (Fleet vs base for others), hold extension (non-Fleet vs base kept for Fleet), delivery fee (Fleet vs base). No two policies price the same quantity for the same deal type.
- Cross-category reads: every policy reads only the customer's service account/ledger (service category), consistent with each `cross_category` block.
- Conflict found with an in-force base clause not in any `overwrite`: base purchase_evt_hold_extension "Extensions carry no fee and leave the deposit unchanged." vs the extension-deposit/hold-extension pair (finding C1).
- Conflict with base late-balance withdrawn-terms timing (finding C4).
- Claimed scopes (from the masked views' user_scenario + the prerequisite graph, to be compared against charter_scope after reveal): task 0 tree {order_deposit ← late_balance_fee ← {delivery_fee, unit_incentive}}, task 1 tree {hold_extension_days ← extension_deposit}. Pairwise disjoint and jointly complete over the six policies.

### rule_compute_equivalence
Mechanical sweep (`/tmp/audit_vehicle_purchase_deals_0075/mech.py`): every `compute_basis` quote is verbatim in its rule (XF B10 clean); every `baseline.rule` sentence is in the rule; every factor binding exists in compute; every prerequisite `policy_source` is verbatim in its own rule.
Manual two-way sweep per policy:
- delivery_fee: distance, free-radius ladder (`XCOUNT within_months=12` == "fewer than 12 whole calendar months ... same day reached", MONTHS() implements exactly that, month-end case consistent), late-window counting (DAYS(contract,delivery) − delivery_window_days; "more than 15" / "1..15" / within), mile-rate ladder, weekend (DAYS from Monday 2000-01-03 %7: 5=Sat, 6=Sun), tenure share, assembly order "addition first, share, rounding last", `posted − already reversed − fleet fee`, floor at 0 ("left as posted"). Equivalent.
- unit_incentive: class ladder, upfit XSUM keyed on vehicle_id (customer-pay labor+parts, no window — rule states none), reporting lag (−1 sentinel for no filing == "no filing yet earns none"), fleet-size, closeout (MONTHS('2000-01-01',d)%12 → 7/8 = Aug/Sep, 5/6 = Jun/Jul), rounding last. Equivalent.
- late_balance_fee: standing ladder (24m returned payments, any method — rule says "returned payment"), credit-use (None/0 limit → no add-on), fee-basis ladder, buyer payments (excl. deposit_transfer/lender_funding/manufacturer_incentive, less returned), early-pay 12m, down-payment, assembly order, min fee last. Equivalent except the negative-lag branch (C4).
- order_deposit: standing ladder (MONTHS ≥ 60), late-history 24m, held-unit (DAYS(reserved, expiry) − vehicle_hold_days), check count, credit-hold / exposure / plain base, `MX(0, required − held)`, rounding. Equivalent.
- extension_deposit: tier rate, check+ACH returned 24m, days left (DAYS(NOW, expiry)), service spend 12m, reservation deposits, card / recent-check / whole credit ladder. Equivalent.
- hold_extension_days: cover ladder (held ≥ ratio × price AND collected-funds deposit), visits (customer-pay labor line A, 12m), tenure, start offset (Sunday → +1; recent check → MX(0, DAYS(expiry, check)+10); else 0), result = offset + length. Equivalent.
- Rounding: `RND` is Python `round` (banker's) while every rule says "half up"; no value in either task world sits on a .xx5 boundary (checked), so no consequence here (observation O1).

### action_binding_and_uuids
- Each (target_tool, computes) is claimed once. uuid8s 7a0a59bd, b735a70c, 7ed43dd7, c9caca35, 9124466d, 21e7c68f: no shared prefix/suffix, no sequence — independent.
- No factor id is a substring of any tool name (mechanical, XF A7 clean).
- Docstrings: format-only arg descriptions, no example values, no ordering words, no other tool named; every claimed effect is in the body (XF E17 clean). No tool body checks a policy precondition or computes an amount.
- Trigger rule (XF E18): events written are purchase_payment_posted, purchase_charge_reversed, purchase_charge_posted, purchase_deposit_received, purchase_hold_extended — all with base `triggers: []`; nothing lands in another category.

### prerequisite_graph
- `prerequisite` filled on all six (`[]` on four). Edges: order_deposit→late_fee (state_gate), late_fee→delivery_fee (value_input, gate deal_balance), late_fee→unit_incentive (value_input, gate deal_balance), hold_extension→extension_deposit (value_input, gate deposit_cover_days). All targets are extended ids in this file; acyclic; all `form: state`, no `fallback_reason` (correct for state form).
- `resolved_by` = the depended-on policy's target_tool on every edge; effects hold (reversal/credit lower balance_due; extension deposit raises deposit_held_balance).
- order_deposit edge: `gate: purchase_transactions.billing_month` is a field, not an eligibility gate of the policy (the policy has no eligibility list) — observation O2.
- condition vs sentence: see C3.

### prerequisite_sentences
1. order_deposit: "A fleet order deposit is not taken on a reserved unit until every delivered Fleet Vehicle Purchase Agreement of the buyer that is past its late balance assessment day carries a late balance fee for the current billing month." — connective "not ... until"; record test (deal status, delivery_date + 40, a late_balance_fee row with billing_month = handling month); no tool/id. One write brings it about: post_fleet_late_fee_7ed43dd7. Derivation: sentence + records → find the policy whose rule posts a late balance fee on a fleet deal → late_balance_fee. Single reading. Strength mismatch with `condition` → C3.
2. late_fee ← delivery_fee: "The fleet late balance fee is fixed only after any home delivery fee posted on the deal above the fleet home delivery fee stands reversed down to that fee." — connective ok; one write (reverse_fleet_delivery_fee). The waited-on state is defined by another policy's computed amount ("the fleet home delivery fee") → C2.
3. late_fee ← unit_incentive: "The fleet late balance fee is not worked out until the manufacturer fleet incentive owed on a qualifying unit stands credited on the deal." — record test (qualifying = unit count in the year; credited = a manufacturer_incentive payment row). One write (credit_fleet_incentive). Passes.
4. hold_extension ← extension_deposit: "The extension days are not worked out until the deposits held on the deal include the extension deposit owed for holding the vehicle longer." — one write (pay_extension_deposit; pay_fleet_order_deposit is fleet-only by its own policy). Waited-on state defined by another policy's computed amount → C2.
- No rule carries a second wording, a tool name or another policy id; depended-on rules do not restate the sentences; no undeclared cross-problem order found in any rule.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (and against base clauses outside the refs that govern the same quantity):
- delivery_fee: purchase_evt_home_delivery — two overwrites (free-radius clause; fee/posting clause), both scope-named and restating the out-of-scope treatment; remaining sentences (availability/max miles, distance as recorded, no second fee for store redelivery) inherited, not contradicted. doc_fee, exchange, spot_delivery: no conflicting sentence. Outside refs: purchase_evt_delivery_gate "the buyer's remedy when it does not is the late-delivery waiver" — the late-delivery mileage credit is a fee term, not a cancellation remedy (observation O3).
- unit_incentive: purchase_evt_fleet_incentive amount clause overwritten, scope-named; once-per-deal, payment_method, zero-threshold types, unwound/cancelled exclusion inherited. returned_payment: no conflict.
- late_balance_fee: purchase_evt_late_balance fee clause overwritten, scope-named, restates rounding/min/billing_month for others. The extended "assessment day (the delivery date plus late_balance_assess_after_days calendar days)" contradicts the in-force withdrawn-terms clause → C4. Others (contract_signing, doc_fee, home_delivery, returned_payment, exchange, trade, fleet_terms, title): no conflicting sentence.
- order_deposit: purchase_evt_deposit, `overwrite: []` — restates status/max/method limits; card limits and certified-funds period inherited; the added late-fee gate restricts, does not contradict. Over-max case: base "refused as a whole; the store does not substitute a smaller amount" — extended says deposits are kept within deposit_max_usd; no task world reaches it (observation O4).
- extension_deposit: purchase_evt_deposit, `overwrite: []` — consistent. But purchase_evt_hold_extension (not in refs) "Extensions carry no fee and leave the deposit unchanged." governs the same transaction → C1.
- hold_extension_days: one overwrite (length/counting clause), scope-named, restates count+1 and "never from the request date". Not overwritten: "Extensions carry no fee and leave the deposit unchanged." → C1.

### factor_ladders
All-pairs method table (XF A5) and T2 (XF A6):

| policy | factor | label | tiers (distinguishing input per pair) | T2 world exists |
|---|---|---|---|---|
| delivery_fee | free_radius_standing | param | 200 / 175 / 150 | yes |
| | price_class_mile_rate | param | 1.60 / 1.45 / 1.25 | yes |
| | weekend_delivery | param | 45 / 85 / 0 | yes |
| | late_delivery_miles | method | 0 vs beyond (beyond); 0 vs MX(0,beyond−4d) (beyond,d); MX(..) vs beyond (d) | yes |
| | account_tenure_share | param | 0.85 / 0.95 / 1 | yes |
| unit_incentive | unit_price_class | param | 2150 / 1650 / 1150 | yes |
| | upfit_work | param | 1000 / 400 / 0 | yes (realism C10) |
| | registration_reporting | param | 200 / 100 / 0 | yes |
| | model_year_closeout | method | +pct×price (price) vs max(·,1500) (floor) vs identity | yes (realism C10) |
| | registered_fleet_size | param | 350 / 150 / 0 | yes |
| late_balance_fee | payment_standing_rate | param | 0.01 / 0.0175 / 0.0125 | yes |
| | open_credit_use | param | 0.0025 / 0.001 / 0 | yes |
| | late_fee_history_basis | method | bal×min(1,d/30) (d) vs bal−fees (fees) vs bal | yes |
| | paid_down_share | param | 0.8 / 0.9 / 1 | yes |
| | service_early_payer | param | 0.85 / 0.95 / 1 | yes |
| | down_payment_record | param | 0.85 / 0.95 / 1 | yes |
| order_deposit | commercial_standing_rate | param | 0.05 / 0.075 / 0.10 | yes |
| | service_late_history | param | 0.05 / 0.025 / 0 | yes |
| | extended_hold_rate | param | 0.035 / 0.02 / 0 | yes |
| | check_funds_rate | param | 0.02 / 0.01 / 0 | yes (realism O5) |
| | account_exposure_base | method | deposit_max (no rate/price) vs rate×(price+open) (open) vs rate×price | yes (gating C6) |
| extension_deposit | rewards_tier_rate, returned_bank_payment_rate, hold_time_left_rate, service_spend_record, reservation_money_share | param | distinct values each | yes |
| | deposit_funds_credit | method | held−card (card) vs 0 vs held | yes |
| hold_extension_days | deposit_cover, service_visit_record, service_tenure_days | param | 2/1/0 each | yes |
| | extension_start_day | method | Sunday: offset 1; check: MX(0,DAYS(exp,chk)+10); else: offset 0. Pair (Sunday, else) = constant 1 vs constant 0, NO distinguishing input → C5 | yes |

- Counts: delivery_fee 5 (4p/1m), unit_incentive 5 (4p/1m), late_balance_fee 6 (5p/1m), order_deposit 5 (4p/1m), extension_deposit 6 (5p/1m), hold_extension_days 4 (3p/1m). All 4–6, ≥2 parameter, ≥1 method. Every ladder ≥3 tiers, stated in the rule and implemented in compute; no two tiers of one ladder share a value.
- Multi-source factors: free_radius_standing, payment_standing_rate, commercial_standing_rate (Net15 OR Net30-young), account_exposure_base (tier 2), deposit_cover (held ratio AND collected-funds row). Cross-difficulty (service) factors in every policy except hold_extension's deposit_cover/start_day; task-level: task 0 and task 1 each carry several.
- `decides` is an input (never `result`) on every factor; binding sets disjoint within each policy.
- Independence / assembly / shared selections: C6, C7, C8. Realism: C10, observations O5–O8.

### findings
Every finding below is RED unless marked observation; "bears on" names the task files that demonstrate the consequence.

**C1 — SOURCE-POLICY RED (undeclared override, XF C14).** Symptom: base purchase_evt_hold_extension (in force, never overwritten) says "Extensions carry no fee and leave the deposit unchanged."; purchase_ext_extension_deposit says "this policy sets the extension deposit a buyer adds to hold the vehicle longer" and purchase_ext_hold_extension_days says "The extension days are not worked out until the deposits held on the deal include the extension deposit owed for holding the vehicle longer." Root cause: the extended pair makes added deposit money a condition of the extension, contradicting the base clause, while extension_deposit lists only purchase_evt_deposit in base_policy_refs and hold_extension_days overwrites only the length/counting clause. Consequence: a reader of the base clause extends with no deposit (different terminal state and a different extension length). Bears on task 1.

**C2 — SOURCE-POLICY RED (XF D15: prerequisite state defined by another policy's computation).** Members (all found): (a) late_balance_fee ← delivery_fee: "...any home delivery fee posted on the deal above the fleet home delivery fee stands reversed down to that fee" — "the fleet home delivery fee" exists only as the delivery-fee policy's computed amount; no record test decides whether the 157.50 posted fee "stands reversed down" without running that computation. (b) hold_extension_days ← extension_deposit: "...until the deposits held on the deal include the extension deposit owed for holding the vehicle longer" — "the extension deposit owed" is the extension-deposit policy's computed amount; whether held deposits "include" it is not a record test. Bears on task 0 (a) and task 1 (b).

**C3 — SOURCE-POLICY RED (check 6: sentence broader than condition).** Sentence 1 (order_deposit) requires a current-month late fee on every delivered fleet deal past its assessment day; the `condition` adds "and whose balance_due is above 0.00". Base late-balance: "No late balance fee is assessed when balance_due is 0.00 or less", and purchase_evt_deal_close keeps a delivered deal with a credit balance open until it is refunded. Second reading: in a world with a delivered fleet deal past day 40 carrying a credit balance, the sentence can never be satisfied (no order deposit can ever be taken); the condition says it is satisfied. Neither task world has such a deal — no task consequence.

**C4 — SOURCE-POLICY RED (XF C14 / B9 negative lag).** late_balance_fee defines "the assessment day (the delivery date plus late_balance_assess_after_days calendar days)" for every fleet deal; in-force base purchase_evt_late_balance says a fleet deal whose net terms were withdrawn under purchase_combo_fleet_terms is assessed "after late_balance_assess_after_days minus balance_due_days_after_delivery calendar days instead" (10 days). For such a deal assessed on day 25: base timing prorates 15/30 of the balance; the extended compute gives `days_after_assessment_day = −15`, fee basis = −0.5 × balance, so the fee falls to the 50.00 minimum — a branch with no stated rule tier. Neither task world has a withdrawn-terms deal — no task consequence.

**C5 — SOURCE-FACTOR RED (XF A5 all-pairs, mislabelled tier pair).** hold_extension_days.extension_start_day (method): Sunday tier `start_offset = 1` and fall-through `start_offset = 0` are the same expression with a different constant — no input distinguishes them; that pair is a parameter swap inside a `method` factor. Bears on task 1 (its world takes the Sunday tier).

**C6 — SOURCE-FACTOR RED (XF A1: factor gated through / reading another factor).** Members: (a) delivery_fee: `fleet_delivery_fee: RND(...) if beyond_radius_miles > 0 else 0` with `beyond_radius_miles = MX(0, distance − free_radius)` — free_radius is free_radius_standing's output, so price_class_mile_rate, weekend_delivery, late_delivery_miles and account_tenure_share act only when free_radius_standing's tier leaves the distance beyond the radius (distance 180, Net 30 clean buyer: fee 0.00 whatever the other four tiers; same world at the 150-mile baseline radius: they move it); late_delivery_miles's operand is likewise the factor-modified beyond_radius_miles (its floor at 0 binds differently by radius tier). (b) order_deposit: account_exposure_base's credit-hold tier "the deal type's deposit_max_usd whatever the rate" gates commercial_standing_rate, service_late_history, extended_hold_rate and check_funds_rate (all four inert for a credit-hold buyer). Not counted: model_year_closeout's floor/addition on the summed incentive — a cap/finishing stage on the assembled amount that XF A3/A6 admit with T1/T2 (observation O6). Bears on task 0.

**C7 — SOURCE-POLICY RED (XF A3: assembly sentence names a factor).** unit_incentive: "Every allowance and bonus is added to the per-unit amount first, giving the summed incentive; the closeout program then finishes the summed incentive, and rounding to the cent comes last." — names "the closeout program" (model_year_closeout) in the generic combination sentence that the computation document carries. Bears on task 0.

**C8 — SOURCE-FACTOR RED (XF A2: shared record selection bound inside two factors).** unit_incentive: "the vehicle price charged on the deal (the amount posted under charge_code vehicle_price)" is read twice — `class_price_charged` (bound to unit_price_class) and `closeout_price_charged` (bound to model_year_closeout) — and defined only inside unit_price_class's sentence; the closeout sentence uses the term without its definition. Bears on task 0.

**C9 — SOURCE-POLICY RED (XF B11: framing clause asserts a fact no record holds / narrower than the measure).** Members: (a) extension_deposit "A buyer who has kept the vehicle they drive now in the group's service bays" — no record says which vehicle the buyer drives now; the measure sums every customer-pay line on the account. (b) extension_deposit "The money the buyer put down when reserving" — measure is every deposit received on the deal, whatever its date. (c) unit_incentive "A unit upfitted by the group's service department" — records hold labor/parts lines, not upfit work; measure is every customer-pay labor/parts line on the vehicle. (d) hold_extension_days "falls on a Sunday, when the store is closed" — stores carry no hours. (e) order_deposit "paid by personal check (payment_method check)" — records carry `check`, not personal vs business (the buyer is a fleet business). Bears on task 0 (c, e) and task 1 (a, b, d).

**C10 — SOURCE-FACTOR RED (XF F22 realism / unreal ladder condition).** Members: (a) unit_incentive.upfit_work: tier 2 pays a 400.00 "upfit allowance" for any customer-pay labor or parts on the unit's vehicle, with no window and no link to body/equipment installation — a 90.00 oil change on a delivered fleet unit earns it; no OEM or dealer upfit program pays an upfit allowance on repair or maintenance work. (b) unit_incentive.model_year_closeout: tiers keyed on delivery month only — a next-model-year unit (e.g. a MY2027 unit delivered September 2026) earns "model-year closeout" cash of 1% of price; closeout programs apply to the outgoing model year (vehicles.model_year is on record and not read). Bears on task 0.

Observations (no demonstrable consequence; not grounds for rework):
- O1 RND is banker's rounding vs "half up" in every rule; no boundary value in either world.
- O2 order_deposit edge `gate` names a field, not an eligibility gate.
- O3 delivery_gate's "the buyer's remedy ... is the late-delivery waiver" vs the late-delivery mileage credit — different quantity.
- O4 order_deposit over-max case (base: refuse whole) unreachable in task worlds.
- O5 check_funds_rate (extra order-deposit rate per check-paid deposit, even long-cleared, on a deal type whose own deposit_methods_allowed lists check) — plausible as the company's own schedule, weakly motivated.
- O6 model_year_closeout floor/addition reads the summed incentive (assembled amount) — admitted shape under XF A3/A6.
- O7 delivery_fee free-radius and tenure tiers are evaluated at the handling date, not the delivery date the fee belongs to; stated explicitly, consistent.
- O8 registration_reporting keys an OEM reporting bonus on title_application_date — plausible as the company's schedule.

## closing_checklist (post-reveal, revision_1)
Not closed — the difficulty does not pass the source-layer audit.
- Task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; both comparison sections end RED.
- charter_scope revealed: task 0 {fleet_delivery_fee, fleet_unit_incentive, fleet_late_balance_fee, fleet_order_deposit}, task 1 {extension_deposit, hold_extension_days} — pairwise disjoint, jointly complete, matches the pre-reveal scan; uuid8s independent.
- Problem trees: task 0 n=3 with 2 value_input edges, task 1 n=1 with 1; each has an owner=user write; whole-difficulty graph acyclic. PASS on both worlds.
- Factors: counts and T1 hold on both worlds (every factor moves gold; all-baseline ≠ gold), but C5, C6, C8, C10 and task-0 T0-1 stand.
- Gates were not re-run by this auditor (verdict RED; nothing to close).

Per-task verdicts: task 0 RED (SOURCE-FACTOR T0-1/C6/C8/C10, SOURCE-POLICY C2a/C7/C9c,e, SOURCE-TASK T0-3); task 1 RED (SOURCE-TASK T1-1/T1-2, SOURCE-POLICY C1/C2b/C9a,b,d, SOURCE-FACTOR C5). Charter RED ids: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10

---

## revision_2

## charter_global_frozen (revision_2)
- Gate check: last line of tasks/vehicle_purchase_deals/worklog.md = `REWORK round 2: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 2` (run by this auditor, 2026-10-22T05:22:11): views r2/0.view.json sha256 fb2422f088207165, r2/1.view.json ffd6eed2f41edbcb (masked: charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; hashes purchase.extended.yaml 8ac4125fd70c, task_tools.py 28698d49db86, tasks/0.json 370ccaa22300, tasks/1.json 13f3733f7571.
- Both shared inputs changed (r1: 1a68702ec9bd / 908f3efa4823) → every charter-global section is re-derived in full below; nothing carried forward by reference. Blueprint unchanged (products/*.yaml mtimes 2026-10-21; base copy head -1088 still byte-identical to blueprint/products/purchase.yaml).
- Read before freeze: extended charter, task_tools.py, XF_recipe.md, r2 views (diffed against r1 views), DSL evaluator. Not read before freeze: tasks/*.json, plan.md, worklog.md body. No recursive grep over tasks/ or the scenario tree.

### policy_conflict_scan (r2)
Same six policies, same targets/owners. Scope splits now: delivery_fee = Fleet delivered beyond the deal type's free radius; late_balance_fee = Fleet whose buyer's service account is not on credit hold (credit-hold fleet deals and other types keep the base fee and timing); order_deposit = reserved Fleet; extension_deposit = reserved non-Fleet (now overwrites the base "Extensions carry no fee and leave the deposit unchanged." with a scoped replacement); hold_extension_days = reserved non-Fleet. No two policies price one quantity for one deal type. Scopes from the views: task 0 tree {order_deposit ← late_fee ← {delivery_fee, unit_incentive}}, task 1 {hold_extension_days ← extension_deposit}: disjoint, complete.

### rule_compute_equivalence (r2)
Mechanical (mech.py): every compute_basis quote verbatim in its rule; every baseline.rule sentence in the rule; every replaced_by verbatim in its rule; bindings exist and are disjoint per policy. Manual two-way per changed binding:
- delivery_fee: radius = deal type's (plain `beyond_radius_miles`); standing share (Net 30/Net 15 active, 0 late fees in 12m) 0.8/0.9/1; tenure share; late ladder: >15 days `MN(beyond, 50)`, 1..15 `MX(0.5·beyond, beyond − 4·d)`, within `beyond`; shares multiply "in turn"; zero fee within the radius. Equivalent.
- unit_incentive: class; quarterly program cash (month index 6–8 Jul–Sep 500, 3–5 Apr–Jun 250, else 0); order-bank (DAYS(contract, delivery) >30 / 15..30 / <15); fleet size; report timing (lag >10 → −25/day beyond 10, no filing → −25/day from delivery to handling beyond 10, floor 0.5 × summed, else unchanged); rounding last. Equivalent.
- late_balance_fee: credit-hold → base fee `MX(min, RND(pct × balance))`; `days_after_assessment_day = MX(0, …)` ("none elapsed counts as zero"); earlier fees net of reversals for the basis, count by posting; "on a later date" = strict. Equivalent.
- order_deposit: credit-hold tier = rate × cash_price + hold account's open_balance. Equivalent.
- extension_deposit: card deposits net of card refunds; credited `MX(0, held − card)`; min 250 compared after the credit subtraction, rounding last. Equivalent.
- hold_extension_days: collected funds net of refunds; start offset `7 − weekday` for Sat/Sun (→ Monday), weekday-check tier unchanged; "each request handled as one extension". Equivalent.
- O1 carried (compute RND is banker's; tools now round half up; no boundary value in either world).

### action_binding_and_uuids (r2)
Unchanged ids and (target_tool, computes) pairs, each claimed once; uuid8s independent; no factor id ⊂ tool name (new ids commercial_standing_share, quarterly_program, order_bank_lead, registration_report_timing, deposit_received_record checked). Docstrings: format-only, no example values, no ordering words, no other tool named. Tool bodies now enforce every published format: `_Money.cents` half-up on Decimal(str(x)) for all four money args, amount > 0 else "Error:", billing_month `YYYY-MM` with month 01–12, extension_days whole and > 0 (bool rejected), reversal source must be a home_delivery_fee purchase_charge_posted row of the same deal. These are argument contracts, not policy prerequisites; no body checks a prerequisite or computes an amount. Trigger rule unchanged (all written events have `triggers: []`).

### prerequisite_graph (r2)
Edges unchanged in shape; acyclic; resolved_by = target_tool on each. late_fee → delivery_fee is now `form: action` with `fallback_reason`; others `state` without. `condition` fields agree with their sentences (order_deposit now carries "with a balance still due above 0.00" in both). O2 carried (order_deposit gate names a field).

### prerequisite_sentences (r2)
1. order_deposit: "...past its late balance assessment day with a balance still due above 0.00 carries a late balance fee for the current billing month." Record test, matches condition, one write (post_fleet_late_fee). PASS (closes C3).
2. late_fee ← delivery_fee (action form): "The fleet late balance fee is fixed only after the home delivery fee posted on the deal has been checked against the fleet home delivery fee and any excess reversed." Fallback tested: the reversal leaves a row only when an excess exists, so no record state singles out "checked"; the fallback is justified. Derivation: action in business words → the delivery-fee rule ("corrected by one purchase_charge_reversed entry ... for the excess") → reverse_fleet_delivery_fee. Single reading. PASS (closes C2a).
3. late_fee ← unit_incentive: unchanged, PASS.
4. hold_extension ← extension_deposit: "The extension days are not worked out until a deposit received on the handling date stands on the deal." Record test (closes C2b's computed-amount form); one write of this difficulty brings it about for a non-Fleet deal (pay_extension_deposit). But see N3.

### override_declarations (r2)
- delivery_fee: one overwrite (the "Beyond it ..." clause); "Within home_delivery_free_radius_miles the delivery is free and no fee is posted" stays in force and agrees with the rule. replaced_by → N1.
- unit_incentive: unchanged overwrite, scope-named. PASS.
- late_balance_fee: replaced_by now scopes out credit-hold buyers and keeps "the base assessment timing" for them. Withdrawn-terms deals (credit_hold before delivery) are on credit hold at assessment unless later reinstated; a reinstated withdrawn-terms deal is not identifiable from any record (no field marks withdrawn terms) — residual corner, observation R2-O4. Negative lag now stated (zero). C4 closed.
- order_deposit: unchanged `overwrite: []`, no conflicting base sentence. PASS.
- extension_deposit: overwrites "Extensions carry no fee and leave the deposit unchanged." with a scope-named replacement that restates the Fleet case; base_policy_refs now include purchase_evt_hold_extension. C1 closed.
- hold_extension_days: unchanged overwrite; "Each request ... one extension; a further extension needs a further request" adds no conflict with "at most max_hold_extensions". PASS.

### factor_ladders (r2)
All-pairs (XF A5) and T2 (A6) for changed factors:

| policy | factor | label | tiers / distinguishing input per pair | T2 |
|---|---|---|---|---|
| delivery_fee | commercial_standing_share | param | 0.8 / 0.9 / 1 | yes |
| | late_delivery_miles | method | MN(b,50) vs MX(0.5b, b−4d) (d); MN(b,50) vs b (cap, b>50); MX(..) vs b (d) | yes (realism N2) |
| unit_incentive | quarterly_program | param | 500 / 250 / 0 | yes |
| | order_bank_lead | param | 300 / 150 / 0 | yes |
| | registration_report_timing | method | lag-penalty (lag) vs elapsed-penalty (handling date) vs identity; floor 0.5×summed | yes |
| order_deposit | account_exposure_base | method | rate×price + hold open_balance vs rate×(price+open) vs rate×price — rate factors act in every tier | yes |
| extension_deposit | deposit_received_record | param | 0.85 / 0.95 / 1 | yes |
| | deposit_funds_credit | method | MX(0, held − card net of refunds) (card) vs 0 vs held | yes |
| hold_extension_days | extension_start_day | method | Sat/Sun: offset 7 − weekday (input: expiry weekday, 2 or 1) vs check-clear MX(0, DAYS(exp,chk)+10) vs 0 — every pair has a distinguishing input | yes |

- Counts: 5 (4p/1m), 5 (4p/1m), 6 (5p/1m), 5 (4p/1m), 6 (5p/1m), 4 (3p/1m). Ladders ≥3 tiers, stated in rule, implemented in compute, no two tiers share a value.
- Independence (A1): delivery fee no longer gates on a factor output (the radius is the deal type's); order deposit's credit-hold tier keeps the rate; incentive's report adjustment acts on the summed incentive as the stated "adjustment ... next" stage (admitted shape, T2 holds) — C6 closed.
- Assembly (A3): incentive "Every bonus and program cash amount is added to the per-unit amount first, giving the summed incentive; any adjustment to the summed incentive comes next, and rounding to the cent comes last." — kind words (bonus, program cash, adjustment), no factor named; "program cash" is produced by one factor only (observation R2-O1). C7 closed.
- Shared selections (A2): vehicle price charged read once per policy; C8 closed.
- Framing (B11): "the vehicle they drive now", "put down when reserving", "upfitted", "when the store is closed", "personal check" all gone; no new framing asserting an unrecorded fact found. C9 closed.
- Realism (F22): upfit and closeout factors removed (C10 closed); new members → N2; observations R2-O2/O3/O5.

### findings (revision_2)
Round-1 items: C1 closed, C2 closed (a: justified action form; b: record test — but N3), C3 closed, C4 closed (residual R2-O4), C5 closed, C6 closed, C7 closed, C8 closed, C9 closed, C10 closed.

**N1 — SOURCE-POLICY RED (XF C13: replaced_by drops still-in-force content).** purchase_ext_fleet_delivery_fee retires the base clause "Beyond it the home delivery fee is ... never less than home_delivery_min_fee_usd; it is posted once per deal under charge_code home_delivery_fee on the delivery date." Its replaced_by restates the fee formula for other deal types but not "it is posted once per deal under charge_code home_delivery_fee on the delivery date"; that content survives only as a separate sentence of the fleet policy's rule. Consequence: the base home-delivery text, once the clause is replaced, no longer says how or when any deal type's home delivery fee is posted. (Regression: the r1 replaced_by carried it.) Bears on task 0.

**N2 — SOURCE-FACTOR RED (XF F22 / unreal ladder).** delivery_fee.late_delivery_miles: the latest tier (">15 days after the window") charges `MN(beyond, 50)` while the 1–15-day tier charges `MX(0.5·beyond, beyond − 4·days)`. For any beyond-radius distance under 100 miles the concession shrinks as lateness grows, and under 50 miles it vanishes: beyond 40 miles — 1 day late 36 miles, 15 days late 20 miles, 16 days late 40 miles (the on-time charge); beyond 60 — 15 days late 30 miles, 16 days late 50 miles. No dealer publishes a late-delivery concession that is withdrawn from its latest deliveries. Bears on task 0 (its computation declares this ladder; task 0 takes the 1–15-day tier).

**N3 — SOURCE-POLICY RED (check 6: state sentence broader than the dependency).** hold_extension_days: "The extension days are not worked out until a deposit received on the handling date stands on the deal." Any deposit received that day satisfies it, including the reservation deposit of a deal reserved and extended on the same day (hold_requires_deposit puts a deposit on the reservation date). In that world the state holds at the opening, so reading A extends at once (no collected funds → deposit_cover 0) and takes the extension deposit afterwards, reading B takes the extension deposit first (cover tier may rise) — two extension_days values, two terminal states. Task 1's deal was reserved the day before handling — no consequence on its world.

Observations (r2): R2-O1 incentive assembly "program cash" is one factor's kind word; R2-O2 registration_report_timing reduces the buyer's incentive for title-filing lag that base purchase_evt_title assigns to the store (plausible only where the fleet buyer supplies the registration papers); R2-O3 "The manufacturer's quarterly fleet program" states OEM program amounts as fact (consistent with the base charter's manufacturer-incentive framing); R2-O4 reinstated withdrawn-terms corner (C4 residual, not record-identifiable); R2-O5 weekend expiry → Monday start although dealerships trade on Saturdays (plausible as a lender-business-day schedule); O1, O2, O5, O7 carried.

## closing_checklist (revision_2, post-reveal)
Not closed — the difficulty still fails the source-layer audit.
- Task files carry revision_2 sections (old revisions untouched); comparison sections: task 0 RED, task 1 PASS.
- charter_scope r2: task 0 {fleet_delivery_fee, fleet_unit_incentive, fleet_late_balance_fee, fleet_order_deposit}, task 1 {extension_deposit, hold_extension_days} — disjoint, complete; uuid8s unchanged and independent.
- Trees: task 0 n=3 / 2 value_input, task 1 n=1 / 1; customer write in each; graph acyclic. PASS.
- Factors: counts within bounds; every factor moves gold on its world; all-baseline ≠ gold (0.00, 1150.00, 360.41, 3634.00; 1063.00, 3). N2 (unreal late-delivery ladder) stands.
- Tool bodies enforce their docstrings (half-up cents, amount > 0, YYYY-MM, whole days > 0, reversal source row); they judge no prerequisite.
- Gates: coordinator snapshot 2026-10-22T05:22:11 all green (cited above); not re-run here (verdict RED).
- Reworker claim audit (worklog "Rework round 2", by item id): C1–C10, T0-1, T0-3, T1-1, T1-2 verified closed against the artifacts. Regressions introduced by the rework: N1 (delivery-fee replaced_by dropped the posting content the r1 replaced_by carried) and N2 (the new late-delivery cap tier). New: N3, T0-4.
- Note: the worklog reports that another writer overwrote purchase.extended.yaml / task_tools.py / plan.md between rounds (hashes 2a6939935f0c / 3148936cfdc4); the r2 artifacts audited here match the coordinator's r2 snapshot hashes (8ac4125fd70c / 28698d49db86).

Per-task verdicts (revision_2): task 0 RED (SOURCE-POLICY N1, SOURCE-FACTOR N2, SOURCE-TASK T0-4); task 1 PASS. Charter RED ids: N1, N2, N3.

VERDICT revision_2: task0=RED task1=PASS charter=N1,N2,N3

---

## revision_3

## charter_global_frozen (revision_3)
- Gate: last non-blank worklog line = `REWORK round 3: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 3` (run by this auditor, 2026-10-22T05:56:51): r3/0.view.json sha256 fb2422f088207165, r3/1.view.json ffd6eed2f41edbcb (identical to r2 → task worlds and user_scenarios unchanged); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; hashes purchase.extended.yaml 3d8a1e6677e4 (changed from 8ac4125fd70c), task_tools.py 28698d49db86 (unchanged), tasks/0.json d83b935da127, tasks/1.json 95969dd640b1.
- Re-derivation scope: task_tools.py unchanged → action_binding_and_uuids (r2) carried forward on hash 28698d49db86 (tool bodies enforce half-up cents, amount > 0, YYYY-MM, whole days > 0, reversal source row; no prerequisite judged). The extended charter changed → every other charter-global section re-derived. Base copy still byte-identical to blueprint/products/purchase.yaml; blueprint unchanged.
- Change set (r2 → r3, from diffing my r2 dumps against r3): delivery_fee replaced_by/rule restate posting; late tier >15 days = `MN(late_floor_share × beyond, late_long_cap_miles)`; `+ 0.000001` added inside every money `RND` (delivery fee ×2, incentive, late fee ×2, order deposit, extension deposit); extension_deposit and hold_extension_days scoped to extensions "asked for on a day after its reserved_date" (`requested_on_reserved_date = F('reserved_date') == NOW` → deposit 0 / base hold_extension_days), a new sentence "On such a deal, a deposit the buyer adds on a day after the reserved_date is the extension deposit, taken at the amount this policy sets", and the hold-extension prerequisite condition narrowed to a deposit dated after the reserved_date. Nothing else changed (compute, factors, ladders, prerequisite sentences, params of the other policies byte-equal).

### rule_compute_equivalence / prerequisite / overrides / factor_ladders (r3, changed parts only; unchanged parts re-checked equal to r2 text)
- Mechanical: compute_basis quotes verbatim, baseline sentences in rule, replaced_by verbatim in rule, bindings exist/disjoint, no factor id ⊂ tool name — clean.
- **N1 closed:** delivery_fee replaced_by now ends "...and every home delivery fee, this one included, is posted once per deal under charge_code home_delivery_fee on the delivery date"; the retired base clause's posting content is restated for every deal type.
- **N2 closed:** >15-day tier `MN(0.5b, 50)` ≤ 0.5b ≤ the 1–15-day tier `MX(0.5b, b − 4d)` ≤ b (within window) for every b ≥ 0, so chargeable miles never rise with lateness (beyond 40: 1 day 36, 15 days 20, 16 days 20; beyond 60: 15 days 30, 16 days 30). All-pairs: >15 vs within differ by the 50-mile cap (b > 100); >15 vs 1–15 by days d; 1–15 vs within by d. Rule ↔ compute equal ("late_floor_share of the miles beyond the free radius, never more than late_long_cap_miles").
- **N3 closed:** both policies now scope the extension deposit / factor-priced extension to requests made after the reserved_date, so the reservation-date deposit can never satisfy "a deposit received on the handling date"; the new sentence fixes any post-reservation deposit on such a deal as the extension deposit, so one write of this difficulty brings the state about. Same-day requests: base extension (hold_extension_days, no deposit) — the base clause is restated in both replaced_by texts (XF C13 ok) and computed exactly (XF B12 ok). Scope test is a plain record test (reserved_date vs handling date).
- Rounding at exact ties: for a value whose exact decimal is k + 0.005, `round(x + 0.000001, 2)` returns k + 0.01, matching "half up" (also for binary-inexact ties such as 1.005). See R1 for values just below a tie.
- Realism of the new scope: an extension asked for on the reservation day gets the base 3 days with no deposit while next-day requests pay the factor-priced deposit — plausible as "an extension taken with the reservation is part of the reservation" (observation R3-O1).

### findings (revision_3)
Round-2 items: N1 closed, N2 closed, N3 closed (T0-4 per-task, see 0.md).

**R1 — SOURCE-POLICY RED (rule ↔ compute rounding: compute rounds values just below a half-cent up; rule says half up).** Root cause: `RND(x + 0.000001, 2)` moves every value in [k + 0.005 − 0.000001, k + 0.005) across the tie. Members where such a value is producible (all found; checked by exact-fraction search, `/tmp/audit_vehicle_purchase_deals_0075`):
  (a) purchase_ext_fleet_late_balance_fee `result` (fleet scope): the d/30 proration makes fee values non-terminating. World: balance_due 28930.58, 20 days after the assessment day, rate 0.011, shares 0.9 × 0.95 × 0.95 (task 0's tiers) → exact 172.32499977; the rule's half-up gives 172.32, the compute gives 172.33.
  (b) purchase_ext_extension_deposit `result`: rate × cash_price × shares. World: task 1's tiers (0.055, 0.9, 0.95, card deposit not credited) with cash_price 41184.37 → exact 1936.69499925; rule 1936.69, compute 1936.70.
  Not reachable (value grid coarser than 0.000001 near the tie, so only exact ties occur, where the compute agrees): delivery_fee (`fleet_delivery_fee`, `result`; exhaustive half-mile × rate × surcharge × share search found no value in the window), unit_incentive (multiples of 0.50), order_deposit (multiples of 0.00005), late fee `base_scope_fee` (multiples of 0.000125).
  Neither task world sits in the window (171.74388 and 1940.2515) — no task consequence.

Observations (r3): R3-O1 same-day extension carve-out realism; R2-O1…O5 and O1, O2, O5, O7 carried.

## closing_checklist (revision_3, post-reveal)
Not closed.
- Reveal 2026-10-22T05:59:26Z. Both tasks' gold writes, values, trees, load-bearing figures and factor sensitivities equal the blind re-derivation on the r3 charter.
- Round-2 REDs verified against the artifacts: N1 closed, N2 closed, N3 closed, T0-4 closed. No item that passed in revision_2 regressed (task 1 values, tree and factors unchanged; tools unchanged by hash; unchanged policies byte-equal in rule/compute/factors).
- Reworker claims (worklog "Rework round 3") checked: N1/N2/N3/T0-4, rounding note and "values unchanged" all true; its exact-tie probe holds, but the near-tie window it does not mention is R1.
- New: R1 (charter, rounding just below a half-cent, members late fee result and extension deposit result) and T1-3 (task 1 proof field "TBD").
- Scopes, trees (n=3/2 value_input; n=1/1), customer writes, acyclicity, factor counts and T1/T2: PASS. Tool bodies enforce their docstrings (unchanged, hash 28698d49db86). Gates: snapshot 2026-10-22T05:56:51 all green (cited above).

Per-task verdicts (revision_3): task 0 PASS; task 1 RED (T1-3). Charter RED ids: R1.

VERDICT revision_3: task0=PASS task1=RED charter=R1

---

## revision_4

## charter_global_frozen (revision_4)
- Gate: last non-blank worklog line = `REWORK round 4: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 4` (run by this auditor, 2026-10-22T07:08:42): r4/0.view.json sha256 fb2422f088207165 (= r3), r4/1.view.json b3cbe43bded2de30 (changed); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; hashes purchase.extended.yaml b0268ec31415 (changed), task_tools.py 28698d49db86 (unchanged → r2 tool-body conclusion carried forward on that hash), tasks/0.json bfc994931a83, tasks/1.json 9773908734be.
- Coordinator ruling applied: money rounding written RND(x + 0.000000001, 2) under a "half up" rule is accepted; a value within 1e-9 below a half cent is DSL-KNOWN residue, not RED; any mismatch beyond 1e-9 is RED; a floor that creates an amount where the rule owes nothing is RED.
- Change set r3 → r4 (diff of my r3 dumps against r4): every money `RND(x + 0.000001, 2)` → `RND(x + 0.000000001, 2)`; late fee `result = 0 if deal_balance <= 0 else ...` with the rule/baseline sentence "while the balance_due is 0.00 or less no late balance fee is assessed and the minimum does not apply"; extension deposit new param max_credit_share 0.6, binding `credit_applied = MN(credited_deposits, max_credit_share × required after shares)` used in `result`, rule sentence "The deposits credited never exceed max_credit_share of the extension deposit required after its shares, so part of every extension deposit is new money." (placed directly after the deposit_funds_credit ladder). Task 1 world: cash_price 41260.00 → 41265.00 (nothing else; user_scenario unchanged). All other rule/compute/factor text byte-equal to r3. Base copy byte-identical; blueprint unchanged.

### changed-policy checks (XF recipe on late_balance_fee, extension_deposit, and the rounding edit on all six)
- Mechanical: compute_basis verbatim, baseline sentences in rule, replaced_by verbatim, bindings, factor-id/tool-name: clean.
- **R1 closed under the ruling:** with `+ 1e-9` the r3 counterexamples now round as the rule says (exact 172.32499977 → 172.32; 1936.69499925 → 1936.69); float error on these magnitudes (< 1e5, a few products) is ~1e-11, so exact decimal ties still round up and no mismatch beyond 1e-9 remains in any of the seven RND sites.
- Late fee zero-balance: rule, baseline.rule and compute agree (no fee, no minimum at balance ≤ 0.00), matching base purchase_evt_late_balance "No late balance fee is assessed when balance_due is 0.00 or less". Remaining floors: late-fee minimum only with a positive balance (the rule owes it); delivery fee / order deposit floors at 0; incentive floor is a share of an owed amount; extension deposit minimum 250 is owed by the rule's own sentence for every in-scope request, and same-day requests are out of scope (0). No floor creates an amount the rule does not owe.
- Extension-deposit credit cap → R4-1.

### findings (revision_4)
Round-3 items: R1 closed (ruling applied); T1-3 per task file.

**R4-1 — SOURCE-FACTOR RED (incoherent baseline: a plain cap that acts with every factor at baseline is absent from baseline.rule and contradicts a baseline sentence).** purchase_ext_extension_deposit. Members (all found):
  (a) baseline.rule keeps "Every deposit received on the deal and still held (deposit_held_balance) is credited toward the extension deposit required." and omits the new cap, so a reader of the computation document alone credits the whole deposit held, while compute's all-baseline caps it. World: standard tier (Service Guest Account, no service lines), cash_price 41265.00, one 2000.00 cash deposit held, more than 4 days left on the hold, request after the reserved date → baseline.rule: 0.05 × 41265 − 2000 = 63.25 → minimum → 250.00; compute with every factor at baseline: 2063.25 − MN(2000, 0.6 × 2063.25 = 1237.95) = 825.30.
  (b) Inside the rule, the same baseline sentence ("Every deposit ... is credited toward the extension deposit required") and the cap sentence ("The deposits credited never exceed max_credit_share ...") give 250.00 vs 825.30 in that world; the cap also reads the share factors' outputs ("after its shares") and sits after the deposit_funds_credit ladder, so it renders with that factor although it acts at baseline.
  Swept the other five policies for plain sentences that change the baseline number but are missing from baseline.rule: none (delivery-fee zero-within-radius and floor are neutral at baseline; late-fee zero-balance sentence is in baseline.rule; order-deposit "already covers" is in baseline.rule; hold-extension same-day scope gives the baseline days).
  Task 1's world: cap 0.6 × 1940.49 = 1164.29 > credited 0 (and > 1000 under the factor's baseline) → no consequence on gold or on any factor sensitivity.

Observations (r4): R4-O1 max_credit_share realism ("part of every extension deposit is new money": a buyer whose held deposits exceed the requirement still adds ≥ 40% of it) — plausible as the store's own schedule; earlier observations carried.

## closing_checklist (revision_4, post-reveal)
Not closed (one charter RED).
- Reveal 2026-10-22T07:10:44Z: both tasks' gold, trees, load-bearing figures, factor sensitivities (figures and tier strings) and baselines equal the blind re-derivation on the r4 charter.
- Round-3 REDs verified against the artifacts: R1 closed under the coordinator's 1e-9 ruling (no rounding mismatch beyond 1e-9 at any of the seven sites); T1-3 closed. Nothing that passed regressed (task 0 values unchanged; task 1 tiers and 7-day result unchanged; tools unchanged by hash; unchanged policies byte-equal).
- Reworker claims (worklog "Rework round 4") verified true; the credit cap it added to answer the zero-amount ruling introduced R4-1.
- Scopes, trees, customer writes, acyclicity, factor counts, T1/T2, tool-body contracts: PASS. Gates: snapshot 2026-10-22T07:08:42 all green (cited above).

Per-task verdicts (revision_4): task 0 PASS; task 1 PASS. Charter RED ids: R4-1.

VERDICT revision_4: task0=PASS task1=PASS charter=R4-1

---

## revision_5

## charter_global_frozen (revision_5)
- Gate: last non-blank worklog line = `REWORK round 5: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 5` (run by this auditor, 2026-10-22T07:21:42): r5/0.view.json sha256 fb2422f088207165, r5/1.view.json b3cbe43bded2de30 (both = r4 → worlds and user_scenarios unchanged); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; hashes purchase.extended.yaml 875a1ffe9065 (changed from b0268ec31415), task_tools.py 28698d49db86 (unchanged — tool-body conclusion carried forward on that hash), tasks/0.json e78c228357f5, tasks/1.json ea400d243509. Base copy byte-identical; blueprint unchanged.
- Coordinator rulings applied: RND(x + 1e-9, 2) accepted under "half up" (residue within 1e-9 not RED); a floor that creates an amount the rule does not owe is RED; an action-form prerequisite with a valid fallback_reason is acceptable.
- Change set r4 → r5 (diff of my saved r4 dumps `/tmp/audit_vehicle_purchase_deals_0075/r4_*.txt` against r5): purchase_ext_extension_deposit only —
  - rule: the baseline sentence becomes "Every deposit received on the deal and still held (deposit_held_balance) is credited toward the extension deposit required, but the deposits credited never exceed max_credit_share of the extension deposit required, so part of every extension deposit is new money."; the separate r4 cap sentence ("... of the extension deposit required after its shares ...", placed after the deposit_funds_credit ladder) is removed;
  - baseline.rule carries the same sentence; baseline.params adds max_credit_share;
  - compute: `credit_applied = MN(credited_deposits, max_credit_share × extension_required)` (no share factors read).
  Every other policy's rule, compute, factors, prerequisite and overwrite text is byte-equal to r4.

### changed-sentence checks (XF recipe)
- Mechanical: compute_basis verbatim (credit_applied now quotes the merged baseline sentence), baseline sentences in rule, replaced_by verbatim, bindings, factor-id/tool-name — clean.
- A1/A3/A4: the cap is a plain baseline sentence reading `extension_required` (rate × cash_price, the quantity the baseline defines) — it no longer reads a factor output and no longer sits in a factor's text.
- B8 two-way: "never exceed max_credit_share of the extension deposit required" = `MN(credited, 0.6 × extension_required)`; order unchanged (add-ons, required, shares, credit subtracted, minimum, rounding).
- Zero-amount ruling: owed before the minimum = required × spend share × deposit-received share − credit applied ≥ required × (0.85 × 0.85 − 0.6) > 0 for every tier combination, so an amount is always owed and the 250.00 minimum only raises an owed amount; same-day requests stay out of scope (0). Other policies' floors unchanged from revision_4 (none creates an amount).
- T2 for deposit_funds_credit: a world where the cap does not bind (credited < 0.6 × required) lets the factor move the result alone — holds.

### findings (revision_5)
- **R4-1 closed.** (a) baseline.rule now contains the cap; the r4 demonstration world (standard tier, cash_price 41265, 2000.00 cash held) gives 825.30 from baseline.rule (2063.25 − MN(2000, 1237.95)) and 825.30 from compute with every factor at baseline. (b) The contradicting pair of sentences is now one sentence with the cap as its stated limit; no other sentence credits the whole held deposit.
- No new RED. Observation R5-O1: the assembly sentence says "each share then multiplies the extension deposit required in turn" while the cap is "max_credit_share of the extension deposit required"; the rule's definition ("The extension deposit required is the extension deposit rate times the deal's cash_price") fixes the cap's base before the shares, which compute implements (world with task 1's tiers and 2000.00 cash held: 578.74; a reader who took the post-share amount would get 776.19). The defined term gives one referent, so this is recorded as a wording risk for renderers, not a second defensible reading. Earlier observations carried.

## closing_checklist (revision_5, post-reveal)
- Reveal 2026-10-22T07:22:46Z: both tasks' gold, trees, load-bearing figures, factor sensitivities (figures and tier strings) and baselines equal the blind re-derivation on the r5 charter.
- R4-1 verified closed against the artifacts (diff against my saved r4 dumps; demonstration world now 825.30 from both baseline.rule and compute). Worklog round-5 claims checked: true. (Its share-product floor 0.765 = 0.9 × 0.85 is the exact minimum; the 0.7225 bound written above is looser but leads to the same conclusion.)
- Nothing that passed in revision_4 regressed: only the extension-deposit policy changed; task values unchanged; tools unchanged by hash; other policies byte-equal.
- Scopes disjoint and complete; every task tree has 1–3 prerequisite problems with ≥ max(n−1,1) value_input edges, an owner=user write and no cycle; graph acyclic; every computation has a self-sufficient baseline (baseline.rule = compute all-baseline), 4–6 factors (≥2 parameter, 1 method), each task has multi-source and cross-difficulty factors, every factor moves its task's gold, and all-baseline ≠ gold; ladders real by the checks of revisions 2–5; tool bodies enforce their docstrings and judge no prerequisite; uuid8s independent.
- Gates: coordinator snapshot 2026-10-22T07:21:42, all seven green (cited above); not re-run by this auditor.
- Open observations only (no RED): R5-O1 (cap base wording), R4-O1, R3-O1, R2-O1…O5, O1, O2, O5, O7.

Per-task verdicts (revision_5): task 0 PASS; task 1 PASS. Charter CLEAN.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

---

## revision_6

## charter_global_frozen (revision_6)
- Input: renderer scan `audits/render_source/vehicle_purchase_deals/render_r1.md` (read in full): one STOP finding F1 (incentive assembly sentence names factor quantities, XF A3) and one low note (order_deposit's shared plain binding `order_account` quoted the commercial-standing ladder sentence as its basis).
- Gate: last non-blank worklog line = `REWORK round 6: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 6` (run by this auditor, 2026-10-22T07:49:14): r6/0.view.json sha256 fb2422f088207165, r6/1.view.json b3cbe43bded2de30 (both = r5); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; hashes purchase.extended.yaml c9d5d4252466 (changed), task_tools.py 28698d49db86 (unchanged), tasks/0.json 233d1414491e, tasks/1.json 3ae5d6f76369. Base copy byte-identical.
- Rulings applied: RND(x + 1e-9) accepted; floor creating an amount where nothing is owed is RED; action-form prerequisite with valid fallback_reason acceptable.
- Change set r5 → r6 (diff against my saved r5 dumps): compute, factors, ladders, baselines, prerequisites, overwrites byte-equal; rule text changes only —
  - unit_incentive: "Every bonus and program cash amount is added to the per-unit amount first, ..." → "Every amount added to the per-unit amount is added first, giving the summed incentive; any adjustment to the summed incentive comes next, and rounding to the cent comes last." (compute_basis summed_incentive / result updated verbatim);
  - order_deposit: new sentence "The buyer's active service account is the buyer's service account in active status, identified by its tier (variant_name)." now the compute_basis of `order_account`.

### grading of the renderer's items
- **F1 — genuinely closed.** The sentence now names no factor quantity ("amount added", "adjustment" are generic stage words); order of the non-commuting stages kept; quotes verbatim (mechanical sweep clean). Audit-side disclosure: this was my observation R2-O1 in revisions 2–5, graded as acceptable "kind words"; it is an XF A3 member ("program cash" was exactly one factor's quantity, "bonus" two factors' quantities) and should have been RED from revision_2. Revision_5's CLEAN therefore missed one A3 member.
- **Low note — closed.** `order_account` now has its own plain sentence (record test: status active, tier from variant_name); it is a non-factor binding shared by commercial_standing_rate and account_exposure_base, stated once (XF A2). The sentence acts on no baseline number (the baseline tier reads no account), so baseline.rule needs no change.

### class sweep (all members, one pass)
XF A3 — assembly / combination sentences of all six policies:
- delivery_fee "Where an amount is added to the delivery mileage charge and shares apply to the fee, the addition is made first, each share then multiplies that sum in turn, and rounding to the cent comes last." — generic stage words.
- unit_incentive (above) — generic.
- late_balance_fee "Any add-on to the monthly rate is added to it first; the resulting rate multiplies the fee basis; each share then multiplies that product in turn; the product is rounded to the cent, and the minimum fee is compared last." — generic ("any add-on", "each share"; conditional, names no factor's own noun).
- order_deposit "Every add-on to the order deposit rate is added to it first; ..." — generic.
- extension_deposit "Every add-on ... each share ... the deposits credited are subtracted next, the minimum ..." — generic (deposits credited is the baseline's own quantity).
- hold_extension_days "Every added day is added ... counted from the extension's starting day ..." — generic (the starting day is the baseline's own quantity: the current hold_expires_date).
No further member. Other classes re-checked on the changed sentences: A2 (order_account shared selection stated once — now satisfied), B8/B10 (bases verbatim, two-way unchanged), B11 (the new sentence asserts only recorded fields). Nothing else in the charter changed, so revision_5's sections stand for the unchanged text (hash-diffed).

### findings (revision_6)
- F1 closed; low note closed. No RED remains.
- Correction to earlier revisions: R2-O1 (revisions 2–5) is withdrawn as an observation and recorded as the A3 member the renderer found (now closed).

## closing_checklist (revision_6, post-reveal)
- Resumed after an account cut: the frozen sections above were already on disk; the reveal (2026-10-22T07:50:21Z) had already run before the cut and showed both tasks' gold, baselines and factor sensitivities equal to the frozen derivation. This section, the task comparisons and the verdict line are the only pieces appended on resume; nothing above was redone.
- Worklog round-6 claims (F1 generic sentence in rule + both bases; order_account plain sentence; compute unchanged; mechanical sweep) checked against the artifacts: true.
- Nothing that passed in revision_5 regressed: compute, factors, baselines, prerequisites, overwrites byte-equal to r5; tools unchanged (28698d49db86); worlds unchanged (view hashes = r5).
- Gates: coordinator snapshot 2026-10-22T07:49:14, all seven green (cited above).
- Open observations only: R5-O1, R4-O1, R3-O1, R2-O2…O5, O1, O2, O5, O7 (R2-O1 withdrawn, see findings).

Per-task verdicts (revision_6): task 0 PASS; task 1 PASS. Charter CLEAN.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

---

## revision_7

## charter_global_frozen (revision_7)
- Input: KB audit `audits/policy_kb/vehicle_purchase_deals/_difficulty.md` (read in full) and its S1 detail in `policy_kb/vehicle_purchase_deals/0.md`: source-side item S1 — task 0's seeded service early-payment discount credits 9.31 (RO 160342, 2026-03-11) and 26.60 (RO 160497, 2026-06-16) and their ACH payments 474.47 / 1333.67 follow the retired 2% service clause; the published service rules give 5.82 / 16.63. KB notes N1–N3 there are policy-side placement/wording notes (N3 = my R5-O1).
- Gate: last non-blank worklog line = `REWORK round 7: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 7` (run by this auditor, 2026-10-22T10:36:40): r7/0.view.json sha256 85606764eeb7308a (changed), r7/1.view.json b3cbe43bded2de30 (= r6); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; tasks/0.json 0acd2133fa91, tasks/1.json 1b573f9e91d8.
- Seed-only confirmed: purchase.extended.yaml c9d5d4252466 and task_tools.py 28698d49db86 (sha256sum run here) are byte-identical to revision_6, so every charter-global section of revision_6 stands unchanged.
- Owning published rules used to check the re-priced rows: the rendered service KB under `docs/service/` (early_payment_discount_computation, fleet_early_payment_discount_terms, the five factor documents of service_ext_early_payment_discount, payment_late_fees_and_credit_hold). No sibling difficulty's tasks directory was read.

### S1 — seed diff and re-pricing check
View diff r6 → r7 (task 0 only; user_scenario and frozen_time unchanged): four service_ro_lines rows changed, nothing else —
- credit eec27bc2 (RO 160342, 2026-03-11, early_payment_discount, source labor line a8434162): 9.31 → 5.82, line_letter → `A`;
- payment b805ea1d (RO 160342, 2026-03-11, ACH): 474.47 → 477.96;
- credit 4c0024a4 (RO 160497, 2026-06-16, early_payment_discount, source labor line 4d8318ff): 26.60 → 16.63, line_letter → `A`;
- payment 74d00e99 (RO 160497, 2026-06-16, ACH): 1333.67 → 1343.64.

Re-priced under the published service early-payment discount, evaluated on each invoice's payment date:
- rate: the tier share for Commercial Fleet Account - Net 30 is 2%. The fleet-deal rate does not apply, because the units (2022 F-250s 33f13aa2 / 874f8bc6) have no closed Fleet Vehicle Purchase Agreement deal. Tenure addition +0.5%: the account was opened 2019-04-08, which is ≥ 60 whole months before 2026-03-11 and 2026-06-16. Prompt-payer addition: none, because there are fewer than 8 payments in 12 months (2025-08-20, 2026-03-11, 2026-06-16). Rate 2.5%.
- discountable total: the invoices were paid by ACH and the unit has no Kessler Care plan (no maintenance records are seeded), so the total is labor plus parts less comeback, overage and goodwill credits: 268.60 + 196.80 = 465.40, and 604.35 + 725.70 = 1330.05.
- window: the ACH window for Net 30 is 15 days; both invoices were paid 7 days after their line date, so both are inside. The labor exceeds the credits by ≥ 10.00. No comeback is owed, so the hub's prerequisite holds.
- standing share: the service late fee on 2025-08-05 falls within 12 whole months of each payment date (7 and 10 months), and no payment was returned, so the share is ×0.5.
- discount: 465.40 × 0.025 × 0.5 = 5.8175 → 5.82; 1330.05 × 0.025 × 0.5 = 16.625625 → 16.63 (half up). Booked against each invoice's latest customer-pay labor charge (line A) ✓.
- payments: 483.78 − 5.82 = 477.96 and 1360.27 − 16.63 = 1343.64, so each invoice nets to 0.00 ✓.
- account: the open_balance stays 10724.70, equal to the ledger, because the two ROs net to zero either way.
S1 is genuinely closed.

### findings (revision_7)
- S1 closed (seed only; the re-priced rows are what the owning published rules produce). No charter change, so no new charter defect is possible this round; all revision_6 charter conclusions carried forward by hash.

## closing_checklist (revision_7, post-reveal)
- Reveal 2026-10-22T10:38:16Z. Both tasks' gold, baselines and factor sensitivities are unchanged and equal to the blind re-derivation on the r7 worlds.
- S1 is verified closed against the artifacts (view diff plus re-pricing by the published service rules). The class is exhausted: task 0 holds the only two early-payment credits, and task 1's world has none.
- Nothing that passed regressed. The charter and tools are byte-identical (c9d5d4252466 / 28698d49db86), task 1's world is unchanged, and task 0's only change is the four service rows.
- Gates: coordinator snapshot 2026-10-22T10:36:40, all seven green (cited above).
- Only observations remain open. KB notes N1–N3 are policy-side placement/wording notes; N3 is the same item as R5-O1.

Per-task verdicts (revision_7): task 0 PASS; task 1 PASS. Charter CLEAN.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

---

## revision_8

## charter_global_frozen (revision_8)
- Input: KB audit `audits/policy_kb/vehicle_purchase_deals/_difficulty.md` revision_3 and `policy_kb/vehicle_purchase_deals/1.md` revision_3 (read): source-side item S2 — task 1's four service_points_earned rows (376 / 1034 / 272 / 756) and rewards_points_balance 2438 follow the retired 2-per-dollar earning clause; the published rule gives 470 / 1292 / 590 / 1195 and 3547.
- Gate: last non-blank worklog line = `REWORK round 8: gates 7/7 green` (only that line read before the freeze).
- `/tmp/erl0075_coord/snapshot.sh vehicle_purchase_deals 8` (run by this auditor, 2026-10-22T12:36:13): r8/0.view.json sha256 85606764eeb7308a (= r7), r8/1.view.json e569f56e1955f730 (changed); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; tasks/0.json 4ffaacbd2b90, tasks/1.json a7216ed75984.
- Seed-only confirmed: purchase.extended.yaml c9d5d4252466 and task_tools.py 28698d49db86 (my own sha256sum) byte-identical to revisions 6–7; charter-global conclusions carried forward on those hashes.
- Owning published rules used: docs/service — points_earned_on_paid_repair_order (baseline), owner_rewards_points_crediting_note (hub), its factor documents (earning_dollars_redemptions_and_late_payment, rewards_tenure_points_multiplier, frequent_visit_points_bonus, owner_earning_rate_for_group_bought_vehicles, kessler_care_member_points_bonus, kessler_shield_labor_points_bonus), owner_rewards_points_terms_by_tier, owner_rewards_points_program_rules. No sibling difficulty's tasks directory read.

### S2 — seed diff and re-pricing check
View diff r7 → r8 (task 1 only; user_scenario and frozen_time unchanged): service_accounts SA-148730 rewards_points_balance 2438 → 3547; service_points_earned rows 01c2eb2d 376 → 470, cd89a3aa 1034 → 1292, 380f27ec 272 → 590, c749ada0 756 → 1195. Nothing else changed.
Re-priced under the published crediting policy (assembly: rate × earning dollars [+ per-dollar labor bonus] → × multipliers, fraction dropped → + fixed bonuses → cap):
- earning rate: Gold 2 per dollar. There is no group-bought addition, because the 2017 Camry has no closed purchase deal.
- per-dollar labor bonus: none, because there is no Kessler Shield contract in the seed.
- earning dollars: each payment was received within 30 days of labor close, so the earning dollars are labor plus parts with cents dropped: 188 (128.88 + 59.28), 517 (241.65 + 275.41), 136 (80.55 + 55.77) and 378 (144.99 + 233.04).
- tenure ×1.25: Gold, account opened 2018-05-14, more than 60 whole months before every crediting date.
- visit bonus +250 when at least 3 payments fall in the last 12 whole months (Gold). The counts are:
  - 2025-09-14: 1 payment;
  - 2025-12-09: 2 payments (09-14 and 12-09);
  - 2026-04-16: 4 payments (09-14, 12-09, 12-22, 04-16);
  - 2026-08-11: 5 payments.
- Kessler Care member bonus: none, because no maintenance plan is seeded. Cap 10000 per repair order, not binding.
- Points:
  - RO 512248: 376 × 1.25 = 470;
  - RO 517903: 1034 × 1.25 = 1292.5 → 1292;
  - RO 521577: 272 × 1.25 = 340, + 250 = 590;
  - RO 525014: 756 × 1.25 = 945, + 250 = 1195.
- Balance: 470 + 1292 + 590 + 1195 = 3547, with no redemptions or expiries.
- All five members match. Crediting dates are unchanged (each row's line_date). For RO 517903 the points stay dated 2025-12-09, the day the later-returned check first paid it in full. If they were credited on the 2025-12-22 re-payment, the visit bonus would apply (3 payments) — recorded as observation R8-O1, because the published rule credits on payment in full and the seed keeps the first such date.
S2 is genuinely closed.

### findings (revision_8)
- S2 closed (seed only). No charter text read rewards points (the purchase charter has no points read; task 1's factors read tier, status, opened date, returned payments, customer-pay spend and line-A ROs). No new RED.
- Observation R8-O1: as above.

## closing_checklist (revision_8, post-reveal)
- Reveal 2026-10-22T12:37:14Z: both tasks' gold, baselines and factor sensitivities are unchanged and equal to the blind re-derivation on the r8 worlds. Every factor still bears weight.
- S2 is verified closed against the artifacts and the published service documents. The class is exhausted: task 0's Net 30 account has no points rows. The persona is unchanged and consistent with the seed.
- Nothing regressed. The charter and tools are byte-identical, task 0's world is unchanged, and task 1's only change is the five points members.
- Gates: coordinator snapshot 2026-10-22T12:36:13, all seven green (cited above).
- Open observations only (R8-O1 new; earlier ones carried).

Per-task verdicts (revision_8): task 0 PASS; task 1 PASS. Charter CLEAN.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
