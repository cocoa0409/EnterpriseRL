# Policy-task audit — protection_plan_claims_and_refunds / charter-global

## charter_global_frozen
- Written 2026-10-23T20:56Z (revision_1), before any task's GT was revealed. Auditor: independent erl-task-policy-audit agent (not the instantiator).
- Freeze hashes (match the coordinator snapshot `/tmp/erl0080_coord/snaps/protection_plan_claims_and_refunds.r1.txt`):
  - `plan.extended.yaml` de7fe722e9fa045cdcf70350d420eff4d6f01220f7ab2cf7e74d479e8ea0623e
  - `task_tools.py` b33a757d4e12688890b21f09798b878d528c41346b59bc7aa41b4d52be113e85
  - `blueprint/products/plan.yaml` d5daff28690b0d28d9f6003acfafff586e47570736dc3c084ba59067ea0d3cd2
  - views task0 034cfab1…9eb2, task1 5d2b52e4…fce (sha256 re-checked, equal to the snapshot)
- Entry conditions (Step 0): the snapshot carries the 7 instantiation gates with their output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK) and the masked-view hashes. Input complete.
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/plan.yaml, products/order.yaml (cross-category realism), the extended charter, task_tools.py, the two masked views, `audits/render_source/XF_recipe.md`, `audits/render_source/owner_ruling.md`, the DSL helpers in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/LATEST/within_months semantics).
- Not read before the freeze: `tasks/*.json`, `worklog.md`, `plan.md`, other difficulties' tasks/audits. Nothing in this section derives from a revealed GT.
- Mechanical sweeps (scratch in /tmp/erl0080_audit_plan/mech.py): base section verbatim equal to products/plan.yaml (no key differs); every `compute_basis` quote verbatim in its rule; every `policy_source` verbatim in its rule; every `baseline.rule` sentence in its rule; every `superseded_clause` verbatim in its base rule; no factor id is a substring of a tool name; no forbidden substring in task_tools.py; one cross-factor read found (C2).

### policy_conflict_scan
Six extended policies; claimed tool/compute pairs:

| policy | subject | target_tool / computes | prerequisite |
| --- | --- | --- | --- |
| plan_ext_limit_of_liability_registration | plan_register_item | register_item_limit_ba116528 / amount_usd | [] |
| plan_ext_accident_claim_service_fee | plan_decide_claim | record_claim_decision_cf68f06d / service_fee_usd | [] |
| plan_ext_repair_authorization_value | plan_settle_claim (repair) | authorize_claim_repair_5d8df043 / amount_usd | ← service fee (state_gate), ← registration (value_input) |
| plan_ext_accident_cancellation_refund | plan_cancel, plan_refund (Accident) | cancel_accident_plan_cec4ac7d / refund_amount_usd | ← service fee (value_input), ← repair (value_input) |
| plan_ext_food_loss_payment | plan_settle_claim (food_loss_payment) | pay_food_loss_claim_b4f587dd / amount_usd | [] |
| plan_ext_standard_cancellation_refund | plan_cancel, plan_refund (Standard) | cancel_standard_plan_ca7b280f / refund_amount_usd | ← food loss (value_input) |

- Overlapping subjects are split by record tests: the two settlement policies by settlement kind (repair vs food-loss payment); the two cancellation policies by tier (Accident vs Standard), and each names the sibling in its replaced_by (XF C.16 satisfied). The service-fee overwrite is scoped to approved Accident-tier claims; the food-loss overwrite to Standard-tier food loss; the registration overwrite to single-item plans.
- Both cancellation policies retire the same base clause and each restates the base formula for "any other one-time plan" — no conflict between them.
- Scope: the two task trees (task0 = Accident root with service fee, repair, registration; task1 = Standard root with food loss) together cover all six policies and share no policy — jointly complete and pairwise disjoint by construction of the edge graph (verified per task after reveal).
- Base conflicts found beyond the declared overwrites: see `override_declarations` (observation class O1) and findings C7.

### rule_compute_equivalence
Check 2 per policy (quotes verified verbatim by script). Rule ⇄ compute agree on the stated domain except for the findings below:
- registration: every binding quoted; tiers of all four factors appear in rule and compute. Equivalent.
- service fee: equivalent on the approved-claim domain; "a decision denying it carries no claim service fee" is a scope statement with no compute branch (O10). Same-day tie for "the latest claim filed" unstated (C4).
- repair: equivalent; T1 condition "outside the tier's in-home service categories" exists only in compute and ladder text, but no tier lists computers/tablets/phones as in-home, so equal on every input. Tie rule unstated (C4).
- accident cancellation: rule "The used share is one less the unused coverage days divided by the coverage days, each counted from that start" vs compute `time_used_share: 1 - unused_days / coverage_days` with `unused_days` counted from today irrespective of the shifted start — diverge when the cancellation precedes the shifted start (C6).
- food loss: equivalent; "the failure claim" in the rule vs `claim_type='mechanical_failure'` in compute (O8).
- standard cancellation: equivalent except the T1 share has no rule or compute outcome when warranty months ≥ term months (C5), and the term-month denominator month-end convention (C4).

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- uuid8s: ba116528, cf68f06d, 5d8df043, cec4ac7d, b4f587dd, ca7b280f — six distinct values, no shared prefix/suffix, no sequence; consistent with independent generation.
- Docstrings name no other tool and state no cross-problem order. They do carry the words "before the call" / "After the call" about argument provenance and the call's own effect, and describe their object as "approved claim" (repair, food loss) (O2).
- Tool bodies: no prerequisite is checked (no tool reads another problem's state) — PASS for "tool layer judges no prerequisite". Contract defects: C9.
- owner=user: cancel_accident_plan_cec4ac7d and cancel_standard_plan_ca7b280f record the holder's confirmed cancellation — ruling (a) in owner_ruling.md. Legitimate.

### prerequisite_graph
- `prerequisite` present on all six policies ([] on registration, service fee, food loss). Every `problem` is an extended policy id of this file, never base, never self. Graph: registration → repair; service fee → repair; service fee → accident cancel; repair → accident cancel; food loss → standard cancel. Acyclic.
- Every `policy_source` is verbatim in the blocked policy's own rule (script). All five edges are `form: state`; no `fallback_reason` (none needed).
- `resolved_by` equals the depended-on policy's target_tool on all five edges.
- `kind`/`gate`: value_input gates `registered_limit`, `fees_owed`, `payout_share`, `claims_deduction` are bindings of the blocked compute; the single state_gate names the field `plan_events.claim_decision` (no eligibility entry exists in extended policies; the gate is the rule sentence) — O14.
- Conditions: neither strengthened nor weakened relative to the sentences, with one structural point that matters per task: the accident-root edge "every claim approved on the plan carries its repair settlement" is a universal over approved claims, so it is vacuously true on any world without an approved claim (see task0 file).

### prerequisite_sentences
Four-point test, all five edges:

| edge | sentence | connective | waited-on state (record words) | single resolving write |
| --- | --- | --- | --- | --- |
| repair ← service fee | "A repair is not authorized until the claim it settles carries the administrator's approval." | until | a plan_decide_claim row with claim_decision approved on the claim | record_claim_decision (only writer of decision rows) |
| repair ← registration | "The authorized repair value is fixed only after the covered item carries its limit-of-liability registration on the plan." | only after | a plan_register_item row | register_item_limit (only writer) |
| accident ← service fee | "The Accident plan cancellation refund is not worked out until every claim filed on the plan carries the administrator's decision." | not … until | decision row on every plan_file_claim row | record_claim_decision |
| accident ← repair | "The Accident plan cancellation refund is fixed only after every claim approved on the plan carries its repair settlement." | only after | plan_settle_claim row, settlement_method repair, on every approved claim | authorize_claim_repair (pay_food_loss writes food_loss_payment, not repair) |
| standard ← food loss | "The Standard plan cancellation refund is not fixed until every food-loss claim approved on the plan carries its food-loss payment." | not … until | plan_settle_claim row, settlement_method food_loss_payment, on every approved food claim | pay_food_loss_claim |

- No tool names, policy ids, snake_case tokens or row ids in any sentence; scope words ("every claim filed", "every claim approved", "every food-loss claim approved") match the conditions. No second wording of any edge in its rule; no depended-on rule restates the sentence.
- Derivation (sentence + records + depended-on rule → write): a reader holding the Accident rule finds an undecided claim → the only rule that books a decision with a service fee is the service-fee policy → decide; once a claim is approved, the repair sentence engages → the repair policy books repair settlements, and its own sentences send the reader to the approval (already done) and to the registration policy. Single reading on each edge.
- Cross-problem order stated without an edge: the service-fee rule (restating base) "every service fee is collected before the repair or replacement is released" — fee collection has no write in this difficulty and the decision→repair order it implies is carried by the declared state_gate edge (O12, observation).
- D.20 (resolver settles every engaged case): **C8** below.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (findings only):
- registration vs plan_coverage_term: S3 "On activation the covered item is registered and its net price becomes the limit of liability." — declared overwrite. All other sentences followed. vs plan_agg_complete_overlap: Complete-only per-item net-price limit followed (ext keeps Complete at net). vs plan_claim_settlement: last sentence declared; "repair estimate … percent of the item's net price", "reimbursement … item's net price minus earlier settlements", "a settlement never exceeds the item's remaining share of the limit of liability", fulfilment on zero liability — followed.
- service fee vs plan_claim_settlement: band sentence declared; collection-before-release sentence restated. vs plan_claim_eligibility: perils, filing, status, MW deferral, claim limit, decision deadline, "the decision states the service fee owed under plan_claim_settlement" — followed.
- repair (overwrite []) vs plan_claim_settlement: does not change the repair/replace choice, the remaining-share cap or the fee; it fixes the settlement value only. The base choice "repair where … the repair estimate is no more than replacement_threshold_pct percent of the item's net price" rests on a "repair estimate" no record holds (O11). vs plan_agg_complete_overlap: single-item scope; no conflict.
- accident cancellation vs plan_cancellation_refund: prorated clause declared; holder-decision, refund-once, method-that-paid, item-returned, full-refund window, no refund after replacement/reimbursement, Complete, billing error — followed. vs plan_coverage_term: coverage dates followed; the waiting-period shift is a new counting rule inside the declared replacement.
- food loss vs plan_claim_eligibility: peril sentence declared. vs plan_claim_settlement: remaining-share cap followed.
- standard cancellation vs plan_cancellation_refund / plan_coverage_term: as for accident.
- **O1 (observation class, exhaustive):** extended amounts contradict base *definitional* text that the overwrite mechanism (policy sentences only) cannot retire: `parameter_schema.food_spoilage_max_usd` "Most paid for food lost … per claim" (food loss pays up to 400 + allowances on Standard tiers); `parameter_schema.liability_limit_basis` "Limit of liability per covered item: the net price paid", `events.plan_register_item.amount_usd` "Limit of liability added, the item's net price", `accounts.liability_remaining` "registering a covered item books its purchase price in", `db_schema.plan_holdings.covered_item_price_usd` "… sets the limit of liability" (registration); `parameter_schema.service_fee_ladder` "Service fee per approved claim by covered item price band" (Accident service fee); `parameter_schema.cancellation_fee_pct` "applied to prorated refunds (the lesser of this and the cap)" and `prorated_refund_basis` "unused_days refunds price x (coverage days remaining / total coverage days)", `measures.plan_msr_unused_coverage_days` total-days definition (both cancellation policies). Each extended rule is explicit and scoped, so I record this as an observation (a KB-render hazard), not as a second defensible answer.

### factor_ladders
Counts per computation (declared): registration 4 (method: price_paid_basis, delivery_charge_inclusion; parameter: adjustment_pass_through, accessory_allowance_rule); service fee 6 (method: starting_fee_method; 5 parameter); repair 6 (method: repair_charge_method; 5 parameter); accident cancellation 5 (method: coverage_count_start; 4 parameter); food loss 5 (method: spoilage_cause_allowance; 4 parameter); standard cancellation 6 (method: warranty_month_share; 5 parameter). Every ladder has 3 stated tiers, each stated in the rule and implemented in compute; `decides` is never `result`; bindings disjoint. Cross-difficulty (order) factors: price_paid_basis, adjustment_pass_through, accessory_allowance_rule, delivery_charge_inclusion, starting_fee_method, repair_charge_method, service_call_charge, return_label_charge, household_haul_away_allowance, warranty_month_share, warranty_period_fee, price_drop_rebate_rule. The category-keyed ones (starting_fee_method, repair_charge_method, service_call_charge, return_label_charge) read `order_events.item_category`, which the plan holding repeats in `covered_item_category` (O3); the others read order-only facts.

Method-factor pairwise table (XF A.7: aggregates of one field count as one input whatever the filter; constants are not inputs):

| factor | T1 | T2 | T3 | T1–T2 | T1–T3 | T2–T3 |
| --- | --- | --- | --- | --- | --- | --- |
| price_paid_basis | line amount / units (promo line) | (amount + card discount)/units | recorded covered_item_price_usd | card discount ✓ | **coincide on every charter-produced world**: db_schema defines covered_item_price_usd as "net price paid for the covered item before tax" and order_post_line.amount_usd as "Net amount paid for the line before tax", so amount/units = recorded price | ✓ |
| delivery_charge_inclusion | Σ fee rows {large_item_delivery, haul_away} | Σ fee rows {same_day_delivery, shipping, express_delivery} | 0 | **same input** (order_events.amount_usd fee sum, filter only) | **coincide**: order.yaml fee types are program-specific (In-Store/Pickup/Drive Up: standard_fee_type not_applicable, no express, no haul-away), so the T1/T2 sum is 0 on T3's domain | **coincide** (same) |
| starting_fee_method | portable rate × recorded price | band + K visit charge | band | ✓ | ✓ | **additive constant only** |
| repair_charge_method | portable rate × registered limit | flat + K in-home labor | flat | ✓ | ✓ | **additive constant only** |
| coverage_count_start | offset P(waiting_period_days) | offset days(start→purchase) | offset 0 | ✓ | ✓ (tariff param) | ✓ — but **T2 is unreachable**: the policy is scoped to Accident tiers and every Accident tier has waiting_period_days 30 (plan.yaml lines 263/331/399), so "a tier with no waiting period" never occurs; 2 reachable tiers |
| spoilage_cause_allowance | disposal rate × food claimed | K flat 15 | 0 | ✓ | ✓ | **constant vs nothing only** |
| warranty_month_share | whole months beyond W / (term − W) | days from purchase date | days from start | ✓ | ✓ | ✓ |

Only warranty_month_share passes all pairs. Under A.7, five of six computations (registration, service fee, repair, accident cancellation, food loss) carry no method factor that survives (C3).

Defining-sentence table (A.3), compact: shared record selections are stated once and used by baseline + factors ("The covered order line is the order line named on the plan…"; "The claim decided/settled is the latest claim filed on the plan"; "The item's remaining share is …"; "The plan price kept is …"; coverage/unused-day definitions). Factor-only sentences (payout share; failure-claim lookup; months held) sit in their own factor sentences, not in baseline.rule. No baseline-only sentence is used by a single factor. One structural miss: `incident_date` is a shared selection but is listed as a binding of prompt_report_credit and read by late_purchase_surcharge (C2). The repair baseline.rule omits the remaining-share definition it caps at (O9; computable from `liability_remaining_usd`).

Realism notes per ladder are in the findings (C10, C11) and observations (O4, O13).

### findings
Charter-global, revision_1. Each lists the tasks it bears on; the per-task files demonstrate the consequence.

**C1 — SOURCE-POLICY RED (XF A.2, assembly sentences name factor quantities) — all six policies.**
Symptom: each rule states the combination by naming the factors' quantities instead of once, generically. Evidence (verbatim): registration "The registered limit of liability is the starting price, less the price-adjustment reduction, plus the accessory allowance, plus the delivery charges added, rounded half up …"; service fee "The claim service fee is the starting claim service fee, plus the repeat-claim step and the late-purchase surcharge, less the prompt-report credit, the term credit and the plan-price credit …"; repair "The authorized repair value is the repair charge plus the parts allowance, the age allowance, the service-call charge, the inspection charge and the return-shipping label charge …"; accident "first the plan price kept times one less the used share, then less the cancellation fee and the claim service fees still owed …; that result is raised by the late-handling addition rate; then the denial credit is added …" (also "A payout weighting is added to the used share"); food loss "The food-loss payment is the food loss claimed held to the per-claim food-loss limit, times the repeat share, plus the spoilage allowance, the reporting allowance and the household allowance …"; standard "The Standard plan cancellation refund is the price kept times the unused share, plus the delivery-gap credit and the price-drop rebate, less the cancellation fee, the claim-handling charge and the claims deduction …". Consequence: the computation document (baseline, silent about variation) cannot carry these sentences without naming every factor, and factor documents must name each other — the KB-EXPLICIT class renderers stop on. Bears on task0 (registration, service fee, repair, accident) and task1 (food loss, standard).

**C2 — SOURCE-FACTOR RED (XF A.1/A.4, factor reads another factor's binding) — plan_ext_accident_claim_service_fee.**
`late_purchase_surcharge.bindings = [incident_offset_days, late_surcharge]`; `incident_offset_days: "DAYS(F('coverage_start_date'), incident_date)"`; `incident_date` is listed in `prompt_report_credit.bindings`. The shared record selection (the decided claim's incident date) is owned by a factor rather than stated as a plain binding. Numerically inert on substitution (prompt_report_credit's baseline replaces only `prompt_credit`), but the late-purchase factor's document must depend on the prompt-report factor's selection. Bears on task0.

**C3 — SOURCE-FACTOR RED (XF A.7, method tiers that coincide or differ only by a constant; unreachable tier) — five computations.**
Members (pairwise table above): price_paid_basis T1≡T3 on every charter-produced world; delivery_charge_inclusion all three tiers equal "sum of the order's delivery-type fee rows" on every charter-produced world; starting_fee_method T2/T3, repair_charge_method T2/T3, spoilage_cause_allowance T2/T3 differ by a constant only; coverage_count_start T2 unreachable inside its Accident-only scope. Demonstration for price_paid_basis on task0's own order with the recorded price the schema prescribes (2149.99): registration 2289.97 with the factor, 2289.97 with its baseline — no weight. Consequence: registration, service fee, repair, accident cancellation and food loss have no method factor that passes; only standard cancellation does. Bears on task0 (all four computations) and task1 (food loss).

**C4 — SOURCE-POLICY RED (XF B.10, unstated tie / month-end / window-boundary conventions).**
(a) "The claim decided is the latest claim filed on the plan" (service fee) and "The claim settled is the latest claim filed on the plan" (repair) state no same-day tie rule; LATEST keeps the first stored row. Producible world: an Accident 3-Year plan with an accidental_damage and a battery_failure claim filed the same day — the fee is the computed fee or 0.00 (battery_failure is not in Accident service_fee_claim_types) depending on row order. Also "the latest food-loss claim filed" (food loss) when two food claims share a filing date. (b) Term spans counted with MONTHS(): service fee "A term credit comes off by the whole months from coverage_start_date to coverage_end_date" and standard T1 "divided by the whole months from coverage_start_date to coverage_end_date less the warranty months". For a coverage start of 2024-02-29 on a 3-year plan, coverage_end_date falls back to 2027-02-28 (base plan_coverage_term) and MONTHS gives 35, so a 3-year plan gets "nothing for any other term" while the base defines the span as term_months = 36. (c) "in the 12 months up to today" (service fee repeat step; food repeat share) does not state whether a row dated exactly 12 months before today counts; compute (`within_months=12`) excludes it. Not engaged by either task's world (checked in the task files).

**C5 — SOURCE-POLICY RED (XF B.10, zero division / no outcome) — plan_ext_standard_cancellation_refund.**
T1 "divided by the whole months from coverage_start_date to coverage_end_date less the warranty months": order_post_line.manufacturer_warranty_months is "integer >= 0" with no bound, so a Standard 3-Year plan on an item with a 36-month manufacturer warranty gives 0/0 (ZeroDivisionError in compute; no number from the rule), and W > term gives a negative denominator. Not engaged by task1 (W=12, term 36).

**C6 — SOURCE-POLICY RED (rule ≠ compute; second reading) — plan_ext_accident_cancellation_refund.**
Rule: "both the coverage days and the used days start on … coverage_start_date plus waiting_period_days … The used share is one less the unused coverage days divided by the coverage days, each counted from that start." Compute: `unused_days: MX(0, DAYS(NOW, F('coverage_end_date')) - 1)` with no cap at the shifted coverage days. Probe (scratch probe_c6.py): Accident 2-Year, coverage start 2026-10-01, bought 2026-10-20 after fulfilment, claim filed 10-21 and denied for the waiting period, cancelled 2026-10-23 (claim filed → prorated): unused 708 > coverage 701, used share −0.00999, result 45.48; reading the unused days as counted from that start (capped at 701) gives used share 0 and 45.10. Two readings, two numbers. Not engaged by task0 (cancellation is past the shifted start).

**C7 — SOURCE-POLICY RED (extended refund exceeds the charge; base says a refund is all or part of a charge) — both cancellation policies.**
Base `events.plan_refund.meaning`: "All or part of a plan charge is refunded." and plan_cancellation_refund "Each plan charge is refunded at most once". Standard: with the warranty-month method the unused share is 1.0 inside the warranty, and the delivery-gap credit and price-drop rebate are then added on top. Probe: task1's own plan with its claims removed gives 278.82 on a 269.00 charge (scratch task1.py). Accident: the denial credit and the negative used share in C6 give 45.48 on a 39.00 charge. Bears on task1 (the gap credit is paid on top of a full unused share — see task1 file); task0 not over the charge.

**C8 — SOURCE-CHAIN RED (XF D.20, resolver cannot settle every engaged case) — accident ← repair edge.**
The accident root waits until "every claim approved on the plan carries its repair settlement", and the only resolver books a repair. Base plan_claim_settlement (in force, not overwritten): "An approved claim is settled by repair where repair_first is true and the repair estimate is no more than replacement_threshold_pct percent of the item's net price; otherwise by replacement …". Producible world: an Accident plan on a 120.00 tablet (accidental damage, item age ≥ 270 days, bought after fulfilment): the repair value is 0.18×120 + 30 + 40 + 20 + 24.50 = 136.10, held to the 120.00 share, i.e. 100% > 80% of net price, so the base settles by replacement. The root then waits on a repair settlement the base forbids, and this difficulty has no replacement write. Not engaged by task0 (676.69 ≤ 80% of 2149.99).

**C9 — SOURCE-POLICY RED (XF E.24, tool bodies vs docstrings) — four tools.**
(a) register_item_limit_ba116528, authorize_claim_repair_5d8df043 and pay_food_loss_claim_b4f587dd declare "a positive decimal number", but the bodies only round (`_Money.cents`) and accept 0.00 or negative values (e.g. a repair authorized before registration computes 0.00 and the tool books it). (b) cancel_accident_plan_cec4ac7d and cancel_standard_plan_ca7b280f hard-code `payment_method_type="external_card"`, `card_account_id=None` and claim "credited to the external card that paid the plan". Base: "the refund goes to the method that paid it", and plan_refund triggers card:card_post_credit for northgate_card. On a plan paid by Northgate Card the tool books the refund to the wrong method and the card credit never posts. Both tasks' plans were paid by external_card, so neither task is engaged.

**C10 — SOURCE-FACTOR RED (realism: an outcome no administrator publishes) — denial_credit_rule (accident cancellation).**
"A denial credit is added where a claim on the plan was denied: the waiting-period credit where a claim was denied as denied_waiting_period, the not-covered credit …". It pays the holder more on cancellation because the administrator denied a claim. No plan administrator or state cancellation schedule pays such a credit (statutory late-refund penalties, by contrast, have a real counterpart in late_handling_addition). Bears on task0 (a waiting-period denial is seeded and adds 10.00).

**C11 — SOURCE-FACTOR RED (realism: the condition admits records the business would never weigh; second-record probe) — accessory_allowance_rule and delivery_charge_inclusion (registration).**
"Accessories bought with the item are other merchandise lines of the covered order in the covered item's category" and "Delivery charges paid on the covered order are added". Probe: one order with two laptops (computers_tablets), each with its own Accident plan (one plan per item is allowed). Each plan's registered limit adds the other laptop's full price as an "accessory" and the full order delivery fee, so the delivery fee is counted twice and each limit roughly doubles. No administrator sets one device's limit of liability to include a second, separately covered device. Task0's world has a real accessory (a docking station), so this is not engaged in task0's number; the defect is in the ladder's condition.

Observations (charter-global, not grounds for rework): O1 (base definitional text, above); O2 (docstrings "before the call"/"After the call"; "approved claim" in repair/food docstrings names the gated state); O3 (category-keyed "cross-difficulty" factors repeat the plan's own covered_item_category); O4 (household_haul_away_allowance: +20.00 food-loss payment because an old appliance was hauled away, +10.00 for a large-item order without haul-away, 0 otherwise — weak business rationale, and the middle tier contradicts the "no backup appliance" rationale); O8 ("the failure claim" vs compute's mechanical_failure only; a same-day power_surge claim is ambiguous); O9; O10; O11 ("repair estimate" held by no record); O12 (fee "collected before the repair … is released" vs deducted as "still owed" from a later refund); O13 (competitor price match passes only one half into the limit; delivery charges raise a limit of liability — both unusual industry practice); O14; O15 (service fee "the tier's portable-device rate" is one policy constant, not a tier parameter); the cancel tools write a new confirmed request and leave an earlier `submitted` app request untouched.

## closing_checklist
Written after both reveals (from 2026-10-23T20:59:38Z on). The section above was not edited after the reveal.
- Per-task files: `0.md` and `1.md`, one per task, next to this file. Revision_1; no earlier revision.
- Scope: charter_scope task0 = {registration, service fee, repair, accident cancellation} with tools {register, record decision, authorize repair, cancel accident}; task1 = {food loss, standard cancellation} with tools {pay food loss, cancel standard}. Pairwise disjoint and jointly cover all six extended policies and six task tools. The edge graph is a DAG with no cross-task edge.
- Trees: task0 declares 3 prerequisite problems with 3 value_input edges, but one edge is satisfied at the opening (0.md T0-1). Task1 has 1 problem with 1 value_input edge. Both roots are owner=user (ruling (a)).
- Factors: every declared factor bears weight on its task's world against an honest baseline. Every whole-baseline number differs from gold (2349.99 / 49.00 / 289.00 / 222.08 / 250.00 / 176.99). But C3 leaves 5 of 6 computations without a method factor that survives the pairwise test. Task0's registration weight rests on a non-producible seed (T0-2). Neither cancellation computation has a near-miss (T0-3, T1-2). C10 and C11 are realism failures.
- GT agreement: both tasks' GT equals my independent derivation in every value, tool, owner and order. The unique-solution relationship holds on the seeded worlds.
- Not closable: SOURCE-CHAIN / SOURCE-FACTOR / SOURCE-POLICY REDs stand (task files and C1–C11). The gates were not re-run by this auditor (coordinator snapshot r1 is the gate record).

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11

## revision_2

### charter_global_frozen (revision_2)
- Written 2026-10-24T13:15Z, before any round-2 GT field was read. Revision_1 text above is left untouched (its VERDICT line is the revision_1 record).
- Snapshot executed: `/tmp/erl0080_coord/snapshot.sh protection_plan_claims_and_refunds 2` at 2026-10-24T13:09:22Z. Output cited:
  - views: task0 9082c3c9b59fdf6315b8878912c4fe41fa56df5e8e4562c8833ace79f382ecf9, task1 15f8571ae85a0884b6ea32adee9c003ae681d963db85be2c7cb1d1f130b4cf78 (sha256 re-checked, equal)
  - plan.extended.yaml b25bcc460b67d1ebd1318ff06603d6fafacbf65e7f4bdd499993b60c523f1a8b; task_tools.py 5c54fa3a54a23049cc9518be57e20427d999393cd782f80005c4954448710753; products/*.yaml unchanged from r1 (plan.yaml d5daff28…)
  - gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK
- Both charter hashes changed, so every charter-global section is re-derived in full below. Inputs read: rework_claims_r2.md (item ids only), the extended charter, task_tools.py, both views, order.yaml/card.yaml/db_schema for realism. worklog.md read with `tail -1` only ("REWORK round 2: gates 7/7 green"). plan.md was not read.
- Mechanical sweep (mech.py, re-run): the base section is still verbatim; every compute_basis / policy_source / baseline sentence / superseded clause is verbatim; no cross-factor binding reads; no factor id inside a tool name; no forbidden substrings; uuid8s unchanged and distinct.

### policy_conflict_scan (r2)
- Edge graph: registration → repair (value_input registered_limit); repair → service fee (state_gate, "A claim decision is not recorded until every claim approved earlier on the plan carries its repair or replacement settlement."); service fee → accident (value_input fees_owed); repair → accident (value_input payout_share, "…every claim approved on the plan before today carries its repair or replacement settlement."); food loss → standard (value_input claims_deduction). The repair←service-fee edge of r1 is gone. The graph is acyclic.
- Subjects: the repair policy now also owns plan_fulfil (replacement branch). Every (tool, computes) pair is unique. The cancellation policies still split by tier and name each other.
- Scope: unchanged split (task0 four policies, task1 two). Verified against charter_scope after the reveal.

### rule_compute_equivalence (r2)
Every changed sentence was swept against compute. The ties, the 12-month window ("less than 12 whole months before today" = `within_months=12`), the term span by days, the unused-days cap, the price-kept cap, the term_months denominator, the failure-claim types and the repair/replacement branch all agree. Two edges have no stated rule: the food-loss "failure claim" when two qualify (N1), and the repair branch versus the base no-lemon sentence (N3).

### action_binding_and_uuids (r2)
- authorize_claim_repair_5d8df043 now takes `settlement_method` (repair | replacement; the other enum values return an error) and fulfils the plan on replacement. The register, repair and food-loss tools guard `amount <= 0`. The cancel tools refuse a charge whose payment_method_type is not external_card and confirm the newest waiting `submitted` request. Docstrings now match the bodies. No tool tests a prerequisite.
- Docstrings no longer say "approved claim". They still say "before the call"/"After the call" about argument provenance (observation, unchanged).

### prerequisite_sentences (r2)
- All five sentences pass the four-point test (until / not … until / only after; record words "decision", "repair or replacement settlement", "limit-of-liability registration", "food-loss payment"; no tool or id). Each state has exactly one writer of this difficulty: record_claim_decision for decisions, authorize_claim_repair for repair/replacement, register_item_limit for registrations, pay_food_loss_claim for food-loss payments.
- **N2 (D.20) defect in the new service-fee sentence:** "A claim decision is not recorded until every claim approved earlier on the plan carries its repair or replacement settlement." The policy's rule speaks for decisions on every tier (it restates the out-of-tier band fee). An approved claim whose settlement is a food-loss payment or an eGift-card reimbursement never carries a "repair or replacement settlement", so no later decision on that plan can ever be recorded, and no write of this difficulty can satisfy the gate. See findings.

### override_declarations (r2)
- Same declared overwrites as r1, sentence sweep repeated. **New (N3):** the repair rule's new sentence "…otherwise it is settled by repair at the authorized repair value" (repair policy, `overwrite: []`) contradicts the still-in-force base plan_claim_settlement sentence "Once plan_msr_item_repairs has reached no_lemon_repairs, the next approved claim for the same failure on that item is settled by replacement whatever the estimate."
- O1 (base definitional text) is unchanged; the reworker marks it disputed. I keep it as an observation, as in r1.

### factor_ladders (r2) — method pairwise table
| factor | T1 | T2 | T3 | verdict |
| --- | --- | --- | --- | --- |
| replacement_price_basis (registration) | unit_price_usd (promo line) | (amount + card discount)/units | recorded covered_item_price_usd | **FAIL**: on every charter-produced line, amount_usd = unit×qty − promo − card discount (order post_line meanings; card.yaml discount taken at checkout) and the recorded price is the net price paid (db_schema). So T2 = unit_price_usd when there is no promo, and T3 = amount/qty = unit_price_usd when there is no discount. All three tiers return unit_price_usd on their own domains: the ladder is one rule ("the pre-discount unit price") written as three. |
| delivery_charge_share | relabelled `parameter` (1.0 / 0.75 / 0 shares) | | | ok as a parameter |
| starting_fee_method (service fee) | rate × recorded price | MX(band, 59.00) | band | passes (T2 has no band input on the reachable domain; observation: every Accident band ≤ 49 < 59, so "the greater of" never picks the band) |
| repair_charge_method | flat × registered limit / 1500 | MX(flat, 249) | flat | passes |
| coverage_count_start (accident) | offset P(waiting_period_days) | offset −days(purchase → start) | offset 0 | **FAIL T2/T3**: T3's domain is "not bought after fulfilment and coverage did not start after purchase", i.e. purchase date = coverage start. There T2's formula gives −0 = 0 = T3, so the 'nothing' tier coincides with T2 across its whole domain (XF A.7). Two real tiers. |
| spoilage_cause_allowance (food) | rate × claimed | MX(25, rate × claimed) | 0 | passes |
| warranty_month_share (standard) | whole months beyond W / (term_months − W), or 1 | unused / days(purchase → end) | unused / coverage days | passes |

Surviving method factors per computation: registration **none**; service fee starting_fee_method; repair repair_charge_method; accident **none**; food loss spoilage_cause_allowance; standard warranty_month_share. The parameter / multi-source / cross-difficulty counts still pass per task. New parameter factors (claim_administration_charge, request_waiting_addition, northgate_install_allowance, delivery_charge_share) have three distinct values each.

### findings (revision_2, charter-global)
Round-1 item status (my re-check, not the reworker's claim):

| r1 id | r2 status | evidence |
| --- | --- | --- |
| C1 | closed | Each rule now has one generic order sentence ("Where several of these apply, … settled first; every amount … applied next …"). Observation O16: the order sentences still name the replaced slot ("the starting price", "the starting claim service fee", "the repair charge", "the counting start, the used share and the cancellation fee"). The accident "used share" is defined only inside the payout-weighting sentence. This is placement only and fixes a non-commuting order. |
| C2 | closed | incident/filing dates are plain bindings; the sweep finds no cross reads |
| C3 | **open** (R2-C3) | replacement_price_basis collapses to one value; coverage_count_start T2/T3 coincide. Registration and accident have no surviving method factor (table above). starting_fee_method, repair_charge_method and spoilage_cause_allowance are fixed. |
| C4 | closed | tie sentences (service fee, repair, food loss); term credit by days (2024-02-29 → 2027-02-28 = 1095 days → three-year tier); "less than 12 whole months before today" |
| C5 | closed | W ≥ term_months → 1; denominator term_months − W > 0 |
| C6 | closed | `unused_days: MN(coverage_days, days_to_end)`; the r1 probe now gives used share 0 |
| C7 | closed | both results `MN(price_kept, …)`; baselines say "never more than the plan price kept" |
| C8 | closed for its member | replacement branch plus tool support; root edge reads "repair or replacement". A new D.20 member arises elsewhere (N2) |
| C9 | closed | positivity guards; cancel tools refuse non-external charges (observation: a Northgate-Card-paid plan has no cancellation path in this difficulty) |
| C10 | closed | denial credit removed; claim_administration_charge (count of approved claims) is a real deduction |
| C11 | **open** (R2-C11) | see below |

**R2-C3 — SOURCE-FACTOR RED (XF A.7) — replacement_price_basis, coverage_count_start.** Pairwise table above. Probe for replacement_price_basis: a Standard 2-Year plan on a 499.99 TV line paid with a Northgate Card, 5% discount 25.00, amount 474.99, no promo. T2 = (474.99 + 25.00)/1 = 499.99 = unit_price_usd, the same as T1's formula. With no discount at all, T3 = recorded 499.99 = unit_price_usd. Probe for coverage_count_start: an Accident plan bought at the register on the fulfilment day (purchase = start = 2026-03-01), T3 offset 0. T2's formula gives −DAYS(2026-03-01, 2026-03-01) = 0, the same refund.

**R2-C11 — SOURCE-FACTOR RED (realism; second-record probe) — accessory_allowance_rule, delivery_charge_share.** Two members remain. (a) The accessory definition now keys on return class general_merchandise, which no longer catches a second laptop, but order.yaml does not tie category to class. Two small appliances on one order (a 129.99 stand mixer and a 79.99 blender, both small_appliances / general_merchandise, each with its own Standard 2-Year plan) still count each other as the accessory: +39.995 on the mixer's limit and +64.995 on the blender's. (b) "Delivery charges paid on the covered order are added to the registered limit": two covered items on one Scheduled Large-Item order (a refrigerator and a range, each with its own plan) each add the whole 49.00 + 25.00, so the single delivery fee enters two limits of liability.

**N1 — SOURCE-POLICY RED (XF B.10, second record without a rule) — plan_ext_food_loss_payment.** "according to the failure claim, a mechanical-failure or power-surge claim, filed on the plan with the same incident date as the food-loss claim". The dedup key (line, incident date, claim type) admits one claim of each type for the same incident, but the rule names no pick, and compute takes the mechanical claim first (`… or …`). Probe: a Standard 3-Year plan with a 120.00 food claim on incident D, a mechanical claim for D denied_manufacturer_warranty, and a power-surge claim for D approved (power surge is never deferred). Compute gives 12.00 (disposal 10%). The other reading gives max(25.00, 12.00) = 25.00. Not engaged by task1 (no power-surge claim).

**N2 — SOURCE-CHAIN RED (XF D.20, gate no write can satisfy) — plan_ext_accident_claim_service_fee prerequisite.** Sentence and reasoning in prerequisite_sentences. Demonstration on task1's own seed: plan fa63a9a5… has food claim b37051c2… approved 2026-06-17 and settled by food-loss payment c6da717b…, which is not a repair or replacement settlement. Under the sentence, the decisions 9bb2cd9d… and 08de8015… dated 2026-10-02 could not have been recorded, and no further decision on that plan ever can. The seed holds decisions the in-force rule forbids. Same for any plan with a reimbursement settlement.

**N3 — SOURCE-POLICY RED (XF C.17, undeclared contradiction of an in-force base clause) — plan_ext_repair_authorization_value.** Quoted under override_declarations. Probe: an Accident 2-Year plan on a laptop with three repair settlements booked for battery_failure; a fourth battery_failure claim is approved with an authorized repair value of 300.00 against a 1,000.00 recorded price (30% < 80%). Base: replacement whatever the estimate. Extended: "otherwise it is settled by repair at the authorized repair value". Two settlements, two values (300.00 repair vs the remaining-share replacement), two terminal states (plan active vs fulfilled). Not engaged by task0 (no prior repair).

Observations r2 (beyond r1 carry-overs O1, O3, O10, O11, O13, O14): O16 (above). O17: northgate_install_allowance still raises a food-loss payment for a Northgate-installed unit (+20.00 with haul-away, +10.00 without) on a weak business rationale (r1 O4 reworded, not changed in kind). O18: registration starts from the pre-promotion unit price and then takes the full price drop measured against the promoted price — explicit, but it mixes two price bases. O19: starting_fee_method T2 "the greater of the band amount and the in-home visit charge" never selects the band on any Accident tier. O20: the persona's "with a sleeve" (task0) volunteers accessory evidence when asked about the order.

### closing_checklist (revision_2)
Written after the r2 reveals (13:16:29Z). The r2 charter-global section above was written before the reveal and is not edited.
- Per-task files carry revision_2 sections. Scope is unchanged and disjoint (charter_scope task0 = 4 policies / 4 tools, task1 = 2 / 2). The DAG has no cross-task edges.
- r1 closures verified: C1, C2, C4, C5, C6, C7, C8, C9, C10, T0-1, T0-2, T0-3, T1-2, T1-3. Still open: C3 (as R2-C3: replacement_price_basis, coverage_count_start) and C11 (as R2-C11: small-appliance accessory, delivery fee across two plans). New: N1 (food-loss failure claim, second record), N2 (decision gate that food-loss/reimbursement settlements can never satisfy; contradicted by task1's own seed), N3 (repair branch vs the base no-lemon clause), and task0 T0-R2-1 (SOURCE-TASK).
- GT equals my independent derivation in every value of both tasks. Gates per snapshot r2 are 7/7 green; I did not re-run them.

VERDICT revision_2: task0=RED task1=PASS charter=R2-C3,R2-C11,N1,N2,N3

## revision_3

### charter_global_frozen (revision_3)
- Written 2026-10-24T13:50Z, before any round-3 GT field was read. Revisions 1–2 are untouched.
- Snapshot executed: `/tmp/erl0080_coord/snapshot.sh protection_plan_claims_and_refunds 3` (2026-10-24T13:46:52Z):
  - views: task0 8de5ec61d176a8b668f43aad5419f7948fcbe53d196638667322cd1e2d77423b, task1 97437fc97c225fa91095a6be62d98c4e11cb6b1625484d46700c846033179257
  - plan.extended.yaml 290543fc498191b35668e24bec4d7c3e67132cedafe2775fe64d93a706ea2997; task_tools.py 6ebf08c4235450650747f5a9ab4bd5506bd7f5b4bc797e0c0d55a925925ccfdf; products unchanged
  - gates 7/7 OK (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE)
- Both charter hashes changed, so every charter-global section is re-derived below. worklog.md read with `tail -1` only ("REWORK round 3: gates 7/7 green"). plan.md was not read. The mechanical sweep is clean: base verbatim; quotes, sources and baselines verbatim; no cross-factor read; no factor id inside a tool name; uuid8s unchanged.

### changed policies, XF re-check (r3)
- Registration: replacement_price_basis now has T1 = pre-promotion unit price, T2 = the price-drop adjusted unit price, T3 = recorded price. New competitor_match_reduction: local ad whole, online half (local_competitor_ad is reachable only on In-Store orders, per order.yaml). Covered device lines (same category and return class) share the accessory and delivery amounts. Accessories count only for a non-general-merchandise covered line. Pairwise: T1–T2 differ by input (unit price vs adjusted price), T1–T3 by input (they coincide only on discount-free lines), T2–T3 by input. **Passes.**
- Service fee: the gate now reads "carries a settlement"; tv_visit_charge 39, so MX(band, 39) picks the band at 49 and the visit charge at 29/0 — a genuine max.
- Repair: no-lemon branch (repair settlements now carry their claim type; the tool writes `claim_type=claim["claim_type"]`); same-day bar ("A claim is not authorized on the day of its approval").
- Accident: coverage_count_start T2 needs a gap above 7 days, so on T3's domain (gap 1–7) T2's formula differs; **passes**. New sentence: a claim approved on the cancellation date keeps its fee in the refund and is repaired after cancellation.
- Food loss: approved failure claim first, then MW denial, reading both mechanical and power-surge. Probe (r3_probe.py): mechanical denied for MW + power surge approved on the same incident, 120.00 claimed → spoilage 25.00 (approved branch); single reading. **N1 closed.**
- Standard cancellation: unchanged since r2.
- Probes on changed reads: `drop_price` absent → T3; a competitor-match row is not taken as a drop (adjustment_type filter); one adjustment per line (order rule), so no second match; `same_failure_repairs` excludes replacements and other claim types; `device_lines` counts a returned second device line (rule and compute agree; observation O22); approval same-day ties are stated.

### method table (r3)
replacement_price_basis passes; starting_fee_method passes; repair_charge_method passes; coverage_count_start passes; spoilage_cause_allowance passes; warranty_month_share passes. Every computation now has a surviving method factor. Counts per computation pass (registration 4: 1 method, 3 parameter).

### findings (revision_3, charter-global)
| r2 id | r3 status |
| --- | --- |
| R2-C3 | **closed** (table above) |
| R2-C11 | **partly open** → R3-C11 |
| N1 | closed (probe above) |
| N2 | closed — the gate and the accident edge read "carries a settlement"; task1's 2026-10-02 decisions now follow the rule (earlier approved food claim b37051c2… carries food-loss payment c6da717b…) |
| N3 | closed — `same_failure_repairs >= no_lemon_repairs` → replacement at the remaining share |

**R3-C11 — SOURCE-FACTOR RED (realism; second-record probe) — plan_ext_limit_of_liability_registration.** Two members remain:
- (a) A general-merchandise line in the covered category can carry its own Standard plan (Standard covers computers_tablets items from 20.00). Example: a 79.99 keyboard, return class general_merchandise, on the laptop's order, with its own Standard 2-Year plan. It is still counted in the laptop's accessory amount (whole share), so one item's price sits in two limits of liability. The keyboard plan's own device lines are the general-merchandise lines (keyboard + sleeve = 2).
- (b) Delivery fees are shared only within one category and return class. A refrigerator (major_appliances / large_items) and a sofa (furniture / large_items), each with its own Standard plan on one Scheduled Large-Item order, each add the full 49.00 + 25.00. The laptop + keyboard case above adds 7.49 to the laptop and 3.75 to the keyboard (1.5 × the fee).

**N5 — SOURCE-CHAIN RED (XF D.20 / real-world wait; second-record probe) — service-fee gate together with the same-day bar.** Probe: an Accident plan with two undecided, approvable claims C1 (filed 2026-10-01) and C2 (filed 2026-10-07), and the holder cancelling today.
- The root needs every claim filed to carry a decision.
- "The claim decided is the latest claim filed on the plan", so the fee computation reads C2's data even when C1 is the claim being decided.
- Once one claim is approved today, "A claim decision is not recorded until every claim approved earlier on the plan carries a settlement" blocks the other decision.
- "A claim is not authorized on the day of its approval" blocks that settlement until tomorrow.
- So the root cannot be resolved without waiting a day. Not engaged by task0, which has one undecided claim.

Observations r3: O21 — the service-fee gate's sentence covers every tier, while `resolved_by` names only the repair tool. On a Standard plan an approved unpaid food claim would be resolved by the food-loss payment instead. The claim's type tells the reader which write applies, and no task tree engages it. O22 — `device_lines` counts returned device lines. O23 — "not authorized on the day of its approval" is a company processing rule with no stated business reason. O16, O17, O1 carry over.

### closing_checklist (revision_3)
- After the r3 reveals (13:50:50Z): GT equals my independent derivation in both tasks. Both trees hold (all edges unmet at the opening and load-bearing). Every computation has 4–6 factors, a surviving method factor, a near-miss and honest baselines. Scope is disjoint and complete. The DAG holds. Gates per snapshot r3 are 7/7 green (not re-run by me).
- Closed this round: R2-C3, N1, N2, N3, T0-R2-1, and R2-C11 member (two same-category devices / small appliances counting each other).
- Open (charter-only; neither task's world engages them): R3-C11 (a covered general-merchandise item counted as a device's accessory; delivery fees across categories), N5 (two undecided claims: fee computation tied to the latest claim, plus gate × same-day bar forcing a one-day wait).

VERDICT revision_3: task0=PASS task1=PASS charter=R3-C11,N5

## revision_4

### charter_global_frozen (revision_4)
- Written 2026-10-24T18:15Z, before any round-4 GT field was read. Revisions 1–3 are untouched.
- Snapshot executed: `/tmp/erl0080_coord/snapshot.sh protection_plan_claims_and_refunds 4` (run at 18:1x and re-run at 2026-10-24T18:12:46Z to capture the header; views are rebuilt identically):
  - views: task0 e5d9244f1f9d23b63258a32344f9ede3f6cc3c9aa0898dedc077f080afc2fbec, task1 260a40ecf11755aba0f754a0676343a2f729bcdd67fdf6bbcc36926cd4a439f4
  - plan.extended.yaml b2061a5dcd976b991cae9297fae8def8a01b365ea5ddf7e3ee1b4f7836f1a402; task_tools.py c0870e92e862ee8ed73989c61552c8cf3d93b3cec890f40cfa3e980a19cf1b3d; products unchanged
  - gates 7/7 OK
- Both charter hashes changed. The change set was taken by diff against my r3 copies (/tmp/erl0080_audit_plan/ext_r3.yaml, tools_r3.py). Only the registration and service-fee policies and record_claim_decision changed, so the other four policies' r3 sections carry forward on that diff. worklog.md was read with `tail -1` only ("REWORK round 4: gates 7/7 green"). The mechanical sweep is clean.

### changed policies, XF re-check (r4)
- **Registration.** One line-composition sentence now defines three line sets:
  - merchandise lines: all lines of the covered order;
  - device lines: same category and return class as the covered line;
  - accessory lines: general-merchandise lines in the category, counted only when the covered line is not general merchandise and every one of them is "priced below the lowest min_item_price_usd of the single-item tiers".
  The delivery share is divided across all merchandise lines and the accessory allowance across device lines. Bindings: device_lines and line_class are now owned by accessory_allowance_rule (its only reader), merchandise_lines by delivery_charge_share; no cross reads. Rule and compute agree except for N6. The method table is unchanged (replacement_price_basis passes).
- **Service fee.**
  - Gate: "…every claim approved on the plan before today carries a settlement."
  - Claim decided: "the latest claim filed on the plan that does not yet carry a decision, a claim being marked with its decision when the decision is recorded". Compute is `LATEST(… plan_file_claim, claim_decision='not_applicable')`; the tool now marks the filed claim row, and the seeds mark their decided claims.
  - Other readers of claim_decision filter on plan_decide_claim rows (accident approvals, repair settled claim, food failure decisions), so marking the filed row double-counts nothing.
  - Tie rule stated.
- Probes on changed reads:
  - Two undecided claims C1/C2: C2 is decided first, then C1 becomes the latest undecided. C2's approval today does not gate C1, so the root resolves today and **N5 is closed**.
  - Laptop + 79.99 keyboard (GM): XMAX unit price ≥ 20 → no accessory amount, so **R3-C11(a) is closed**.
  - Refrigerator + sofa on one large-item order: each plan takes 74/2, so **R3-C11(b) is closed**.
  - Absent accessory: XMAX 0 → amount 0.
  - Decoy below (N6).

### findings (revision_4, charter-global)
| r3 id | r4 status |
| --- | --- |
| R3-C11 | closed (probes above) |
| N5 | closed (probe above) |

**N6 — SOURCE-POLICY RED (XF B.10/B.12: decoy record, rule purpose vs compute) — accessory price test.** The rule says accessory lines count only where "every one of them is priced below the lowest min_item_price_usd of the single-item tiers, so that no line that could carry a plan of its own is ever an accessory of another item." Plan eligibility (plan_purchase_eligibility_and_price) tests "net price paid before tax", but compute tests `XMAX(… 'unit_price_usd' …) < K('lowest_plan_price_usd')`, i.e. the selling price before promotions. Probe (r4_probe.py) on task0's order: the cable line re-seeded as unit 24.99, promo 5.00, amount 19.99. This line cannot carry a plan of its own (net 19.99 < 20.00), so the stated purpose makes it an accessory (+19.99, whole share for a computer). Compute gives accessory amount 0. Two readings, registered limit differing by 19.99. Not engaged by task0 (cable unit = net = 19.99).

Observations r4: O24 — one GM line at or above 20.00 removes every accessory, even a 9.99 cable (stated outright; realism weak). O25 — the delivery share divides by every merchandise line, paper towels included (no double count; arbitrary apportionment). O21–O23 carry over.

### closing_checklist (revision_4)
- After the r4 reveals: GT equals my derivation in both tasks. Trees, factors, near-misses, scope and DAG hold. Gates 7/7 per snapshot r4.
- Closed: R3-C11, N5. New and open: N6 (accessory price test: unit price in compute vs the net-price eligibility the rule's purpose clause invokes). It is charter-only, not engaged by either task.

VERDICT revision_4: task0=PASS task1=PASS charter=N6

## revision_5

### charter_global_frozen (revision_5)
- Written 2026-10-24T18:47Z, before any round-5 GT field was read. Revisions 1–4 are untouched.
- Snapshot executed: `/tmp/erl0080_coord/snapshot.sh protection_plan_claims_and_refunds 5` (2026-10-24T18:46:39Z):
  - views: task0 e5d9244f1f9d23b63258a32344f9ede3f6cc3c9aa0898dedc077f080afc2fbec, task1 260a40ecf11755aba0f754a0676343a2f729bcdd67fdf6bbcc36926cd4a439f4 — identical to r4
  - plan.extended.yaml 0cb9cbce7143a138e616b3b06d135dc3912dea9b6d42ee65c72be1c2fcb25ba5 (changed); task_tools.py c0870e92e862ee8ed73989c61552c8cf3d93b3cec890f40cfa3e980a19cf1b3d (unchanged since r4)
  - gates 7/7 OK
- Carry-forward grounds: tools hash and both view hashes are unchanged since r4, so the tool and per-task world sections carry forward by reference. In the charter, the diff against r3 shows the r4 change set plus one r5 change: the registration line-composition sentence (net line-amount test, with the stated reason for the all-or-none rule) and `accessory_price_top` reading `amount_usd`. That sentence and its reads are re-derived below; every other section carries forward from r4. worklog.md read with `tail -1` only ("REWORK round 5: gates 7/7 green"). The mechanical sweep is clean (quotes verbatim, no cross reads).

### changed read, XF re-check (r5)
- Rule: accessory lines count only where "every one of them has a line amount, the net price paid for the line before tax, below the lowest min_item_price_usd of the single-item tiers". Compute: `XMAX(… 'amount_usd' … return_class='general_merchandise') < K('lowest_plan_price_usd')` (20.00 = min over the five single-item tiers). Rule = compute.
- Probes (r5_probe.py, task0 order):
  - r4 decoy (unit 24.99, promo 5.00, net 19.99) → counted, accessory 19.99. **N6 closed.**
  - Absent accessory → 0, and the delivery split becomes 9.99 × 0.75 / 2 → 2303.74.
  - Card-discounted line → amount is net after the discount, consistent with "net price paid".
  - Two-unit line, 2 × 12.99 = 25.98 → not counted, and it disables the other accessories (O26 below).

### findings (revision_5, charter-global)
| r4 id | r5 status |
| --- | --- |
| N6 | closed |

No new RED. Observations: O26 — the test is per line, not per unit, so a 2 × 12.99 cable line (neither unit could carry a plan) is treated as a possible stand-alone purchase. The rule states this explicitly as a line amount; it is not a second reading. O24 now has its reason stated. O21–O23 and O25 carry over.

### closing_checklist (revision_5)
- Per-task files are one-to-one with the tasks, and revisions 1–5 are preserved. Both comparison sections are PASS.
- Coverage and scope: six extended policies, task0 = 4 and task1 = 2, disjoint and complete. Tools are closed; uuid8s are independent and frozen.
- Trees: task0 has 3 prerequisite problems with 3 value_input edges, task1 has 1 with 1. All edges are unmet at the opening and load-bearing. Both roots are owner=user. The difficulty graph is a DAG.
- Factors: every computation has 4–6 factors with a surviving method factor, a near-miss and honest baselines. Every factor bears weight, and every whole-baseline number differs from gold. Each task has multi-source and cross-difficulty factors.
- Gates: 7/7 green on the final form per snapshot r5 (coordinator-run; not re-run by me).
- All round-1 to round-4 REDs are closed; no new defect in round 5. Observations O1, O3, O10, O11, O13, O14, O16, O17 and O21–O26 stand as non-blocking notes.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (revision_6) — seed-only round
- Written 2026-10-25T05:10Z, before any round-6 GT field was read. Revisions 1–5 are untouched.
- Snapshot executed: `/tmp/erl0080_coord/snapshot.sh protection_plan_claims_and_refunds 6` (2026-10-25T05:09:30Z):
  - views: task0 e5d9244f1f9d23b63258a32344f9ede3f6cc3c9aa0898dedc077f080afc2fbec (unchanged since r4), task1 8760613884a7d3d372c59f946c98000420066ddc36ae08db1f3301fd1ba4cfbb (changed)
  - plan.extended.yaml 0cb9cbce…25ba5 and task_tools.py c0870e92…1b3d — byte-identical to my r5 copies (sha256 of /tmp/erl0080_audit_plan/ext_r5.yaml, tools_r5.py) and to /tmp/erl0080_coord/seed_freeze.txt
  - gates 7/7 OK
- Carry-forward grounds: both charter hashes and task0's view hash are unchanged, so every charter-global section (r5) and all of task0 (r5) carry forward by reference. Only task1's world is re-derived. Reworker claims: src2, src3 (task1 seed); src1 no action; order rows unchanged in both tasks. worklog.md read with `tail -1` only ("REWORK round 6: gates 7/7 green").
- Other-product rows: task1's order rows (Large-Item 49.00, haul-away 25.00, promo 300.00, price drop 100.00 on day 10 of 14 after fulfilment) are unchanged and agree with the published `docs/order/fulfilment_fee_schedule_aa930408.json` (Large-Item 49.00, haul-away 25.00) and `price_drop_and_price_match_policy_09964abd.json` (window from the order date). Task0's order rows are unchanged since r4.

No charter finding is open.

### closing_checklist (revision_6)
- After the r6 reveal: task1 GT equals my blind re-derivation (food loss 295.54, refund 54.78). Both re-priced seed rows are producible under the in-force charter at their own dates. Task0 is unchanged. The charter and tools are byte-identical to r5 (seed freeze confirmed). Gates 7/7 per snapshot r6.
- KB seed items: src2 and src3 are closed; src1 is my standing observation O1 (base definitional text), with no verdict effect.
- Nothing regressed; no new defect.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
