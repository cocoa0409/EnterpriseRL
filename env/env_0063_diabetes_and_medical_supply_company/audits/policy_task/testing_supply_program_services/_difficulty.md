# Policy-task audit — testing_supply_program_services / charter-global

## charter_global_frozen

- auditor: independent policy-task auditor (erl-task-policy-audit), revision 1
- freeze time: 2026-10-15 02:21 UTC (written before any task's GT was revealed; nothing in this section is derived from a revealed GT)
- frozen inputs (sha256):
  - `tasks/testing_supply_program_services/bgm.extended.yaml` 7e45d0038de27549b0e5d206421f266dd8570f4e972a90611c35ae44f5f330ec (matches the brief)
  - `tasks/testing_supply_program_services/task_tools.py` d6a03abe39163cb91be8b22d839ca0059016a0e394a9a5cd52db4e885e0a9a52 (matches the brief)
  - `blueprint/products/bgm.yaml` df5cf4212ddae28f318faf7945ac622fae4c9075d587897eecadf7ed6235d11b
  - `blueprint/products/cgm.yaml` 0ddf69b21b95245a4ffc23b7b3edfaa63c43124da0b450f1cfbe8cd5eae44a65 (read for the cross-category rows and the CGM tier parameters the factors read)
- permitted fields read: blueprint.yaml, db_schema.json, share_tools.py, products/bgm.yaml, products/cgm.yaml (hold, quantity, patient-account rules and tier parameters only), the extended charter, task_tools.py, and the two masked views (`frozen_time`, `user_scenario`, `initial_state`).
- explicitly masked and not read: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, the instantiator's scratch and worklog, every other difficulty's `tasks/` and `audits/` directory (including `audits/policy_task/continence_supply_program_services/`, which exists and was not opened), every other scenario under `env/`.
- entry conditions (Step 0): gate snapshot supplied with the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK, only on unlock tool names lacking a KB source because the KB is not rendered yet, deferred to step 3). Masked views supplied with hashes; the four hashes were re-computed and match. Input is complete. The traceability red is the declared pre-render state and is not counted as an audit finding.
- mechanical checks run by the auditor (scratch under /tmp/audit_bgm_0063/): the base section of the extended charter (lines 1-1949) is byte-identical to `blueprint/products/bgm.yaml` (`diff` empty; every top-level key equal); every `compute_basis` entry, every `baseline.rule`, every `prerequisite[].policy_source` and every `overwrite[].replaced_by` is a whitespace-normalised substring of its own policy's `rule`; every `superseded_clause` is a substring of the named base policy's rule; every compute binding has exactly one `compute_basis` key and vice versa.

### policy_conflict_scan

Seven extended policies, each with a distinct subject and target tool:

| policy | subject | target tool | owner | computes |
| --- | --- | --- | --- | --- |
| bgm_ext_superseded_strip_takeback | bgm_return_authorization | issue_return_authorization_3dfb992f | agent | units |
| bgm_ext_above_coverage_notice | bgm_liability_notice_signed | sign_liability_notice_3f2fa265 | user | notice_units |
| bgm_ext_new_meter_strip_supply | bgm_refill_shipment | ship_strip_refill_72890190 | agent | units |
| bgm_ext_noncovered_strip_charge | bgm_patient_charge | post_noncovered_charge_41a38519 | agent | amount |
| bgm_ext_hardship_cost_share_waiver | bgm_balance_adjustment | post_hardship_waiver_f8410ea4 | agent | amount |
| bgm_ext_payment_plan_installment | bgm_patient_payment (the tool writes a `bgm_requests` payment_plan row) | accept_payment_plan_2bd91da1 | user | monthly_amount_usd |
| bgm_ext_courtesy_bridge_reship | bgm_replacement_shipment | ship_courtesy_reship_05d6f35c | agent | units |

Overlap scan (subjects, triggers, eligibility, time anchors, parameters, terminal states, cross-category reads):

- Liability notice (extended sizing) vs base `bgm_liability_notice`: compatible on signer, timing ("on or before the ship date") and notice type; the base allowance measurement is replaced only for notices this policy sizes (declared, see override_declarations). The extended policy does not exclude the Medicare Advantage tier, where base says "no notice can make the member liable" (observation O10).
- Non-covered charge vs base `bgm_liability_notice` + `bgm_evt_denials_and_appeals`: conflict on which denials become customer charges (finding C7).
- Hardship waiver vs base `bgm_evt_patient_account`: the base cap "never for more than that posting's unpaid remainder" is not implemented (finding C9).
- Payment plan vs base `bgm_evt_patient_account`: conflict on the balance the minimum-balance test is applied to (finding C8).
- Strip refill vs base `bgm_evt_refill_shipment`, `bgm_evt_quantity_limits`, `bgm_combo_cgm_backup`: supply days and units declared replaced; residual tension with the base CGM-backup sentence and with the base rounding sentence recorded as observations O1 and O2.
- Courtesy reship vs base `bgm_evt_replacement_and_delivery`: compatible (cap kept, extra past-due gate is an added necessary condition, not a contradiction; realism note O13).
- Take-back vs base `bgm_evt_returns`: compatible (window, double-return and unopened rules inherited).
- Cross-category read boundary: every cross read targets `cgm` (programs status/regimen/hold/balance, `cgm_shipments`, `cgm_billing`) through EXISTS/CFIELD/CPARAM/XCOUNT/XLATEST/XSUM; no write touches a CGM table.

Scope exclusivity (inferred from the two personas before reveal; `charter_scope` is masked): task 0 (new meter, strips) exercises takeback -> notice -> refill; task 1 (courtesy reship) exercises noncovered charge + hardship waiver -> payment plan -> courtesy reship. The two trees are disjoint and together cover all seven extended policies. To be confirmed against `charter_scope` at reveal (recorded in the task files).

### rule_compute_equivalence

Mechanical verbatim containment passed (above). Sentence-by-sentence sweep back, per policy:

- takeback: every tier and branch of the rule is in compute and vice versa (strip refill / stand-in / held shipment, use-end anchor, pace, pace shift, supersession guard, floor at 0, ceil of opened units). Edge notes: when both a delivered_not_received and a lost_in_transit replacement exist, compute prefers the former, the rule is singular (unreachable in both worlds); `recent_sensor_refills` counts sensor refills of every CGM program of the customer, the rule says "shipped on it" (observation O6).
- notice: rule and compute agree on coverage tiers, window convention, netting, covered-now units and reach, EXCEPT the per-block share of the reach beyond the window (finding C4). Rounding: floor on covered units and on the block share, as stated.
- refill: rate tiers, span tiers, CGM phase, exchange, setup, caps all present. `takeback_received` sums every `bgm_return_receipt` for A4253 in the last month, the rule says "received back under a take-back" (observation O7). Rounding: ceil of the phased strips, then caps, as stated.
- noncovered: units route, unit price, late share, hardship share present; the notice selection diverges (finding C5). Rounding "to cents only at the end": RND at the end, as stated.
- hardship: waivable basis, counted adjustments, payer/age/household shares present; payer share diverges for zero recent applications (finding C6); base cap not implemented (finding C9). Rounding at the end, as stated.
- payment plan: balance, covered balance, aged balance (oldest-first consistent with the base past-due measure), first payment, band months, prior-plan and hardship months, clamp; equivalent. Rounding: RND inside, then floor at min monthly and cap at the covered balance, as stated. When both a withdrawn and a completed plan fall in 12 months the rule gives no precedence, compute takes the withdrawn one (observation O15).
- courtesy: days to next refill, bridge mode, bridge days, daily rate, repeat/sensor shares, transit, ceil and cap: equivalent.
- RND is Python `round` on floats (half-even on exact binary ties, e.g. 44.255 -> 44.25), while the two money tool docstrings say "rounded half up" (observation O3; no gold value of this bundle depends on it as far as derivable before reveal).

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above); no base policy names a target tool.
- Docstrings: none states an action's position in a sequence or names another tool; no concrete example values; the occurrences of "until", "afterwards" and "before it is passed" describe the record's own effect or argument formatting, not a call order (observation O12).
- Tool bodies: every tool writes one row (and, for refill/charge/waiver, one running-total update) with no check of eligibility, prerequisites or amounts (`task_tools.py` lines 37-45, 76-84, 130-143, 172-181, 204-213, 240-250, 274-284).
- uuid8s: 3dfb992f, 3f2fa265, 72890190, 05d6f35c, 2bd91da1, 41a38519, f8410ea4 — seven distinct values, no shared prefix beyond one hex digit, no sequence or adjacency pattern; consistent with independent generation.
- `accept_payment_plan_2bd91da1` records months and monthly amount only; the policy's "first payment" has no field or tool (observation O5).

### prerequisite_graph

Edges (all `form: state`, no `fallback_reason`, as required for state form):

| id | blocked policy | problem | kind | gate | resolved_by |
| --- | --- | --- | --- | --- | --- |
| E1 | bgm_ext_above_coverage_notice | bgm_ext_superseded_strip_takeback | value_input | window_netting | issue_return_authorization_3dfb992f |
| E2 | bgm_ext_new_meter_strip_supply | bgm_ext_above_coverage_notice | state_gate | bgm_orders.notice_units | sign_liability_notice_3f2fa265 |
| E3 | bgm_ext_new_meter_strip_supply | bgm_ext_superseded_strip_takeback | value_input | exchange_units | issue_return_authorization_3dfb992f |
| E4 | bgm_ext_courtesy_bridge_reship | bgm_ext_payment_plan_installment | state_gate | bgm_requests.request_status | accept_payment_plan_2bd91da1 |
| E5 | bgm_ext_payment_plan_installment | bgm_ext_noncovered_strip_charge | value_input | program_balance | post_noncovered_charge_41a38519 |
| E6 | bgm_ext_payment_plan_installment | bgm_ext_hardship_cost_share_waiver | value_input | program_balance | post_hardship_waiver_f8410ea4 |

- `prerequisite` is filled on all seven policies (`[]` on takeback, noncovered, hardship); every `problem` is another extended policy of this file, never a base policy, never itself; the graph is two disjoint DAGs (takeback -> notice -> refill with takeback -> refill; {noncovered, hardship} -> plan -> courtesy); acyclic.
- Every `policy_source` is verbatim in its own blocked policy's `rule` (mechanical check).
- `value_input` gates name real compute bindings (`window_netting`, `exchange_units`, `program_balance`). The two `state_gate` edges name a DB field rather than an eligibility id (the extended policies declare no eligibility blocks) — observation O9; the gate they name is real (a notice row / an approved payment-plan row).
- `resolved_by` is in each case the depended-on policy's `target_tool`, and that write does produce the stated `effect`: E1/E3 add a `bgm_return_authorization` row that enters `takeback_units` / `takeback_open`; E2 adds a `bgm_liability_notice_signed` row; E4 adds an approved `payment_plan` request; E5/E6 add a `bgm_patient_charge` / `bgm_balance_adjustment` row that enters `program_balance`.
- `condition` vs sentence: E3's condition adds "issued within the last calendar month", which the sentence does not carry (the exchange tier reads one calendar month). Inside the 30-day return window the two coincide except on the boundary day (an authorization issued exactly one calendar month ago, window still open) — observation O8. E5's condition carries the same breadth as its sentence ("every bgm_claim_denial on a strip claim ... has a ... non_covered_item" charge), which is the breadth finding C7 rests on. No authoring-viewpoint phrasing in any prerequisite field.

### prerequisite_sentences

Four-point test per edge:

- E1 "The units a liability notice for test strips covers are fixed only after the strips the customer holds from the program's latest strip refill, when the meter they were shipped for has since been replaced on the program and their return window is still open, carry a take-back authorization for every unit counted as still sealed." Connective "only after"; waited-on state: a take-back (return) authorization row covering the units counted as sealed — record-visible, no performer, no tool; no snake_case, no id; strength matches the condition. Single writer: only `issue_return_authorization_3dfb992f` (takeback policy) creates `bgm_return_authorization` rows. Derivation: sentence -> look for the policy whose rule issues take-back authorizations for superseded strips -> takeback rule gives the count. One reading.
- E2 "A strip refill that ships more units than the plan's coverage leaves for its supply days is not shipped until a liability notice for test strips, signed by the customer on or after the date of the newest written order for test strips, stands on the program's file." Connective "not ... until"; state: a signed strip notice dated on/after the newest strip order; single writer `sign_liability_notice_3f2fa265` (notice policy). The size of that notice is the notice policy's own rule. One reading. (The antecedent "more units than the plan's coverage leaves for its supply days" is loose, but in the only world that exercises it (task 0) every reading of it is exceeded — see 0.md.)
- E3 "The units of the first strip refill after a newly supplied meter are fixed only after the shipment of strips the customer holds from the latest strip refill, while its return window is open, carries a take-back authorization for any of its units counted as still sealed." "only after"; same state and writer as E1. One reading.
- E4 "A courtesy reship for a program that carries a past-due amount is not shipped until an approved payment plan request covering the program's balance stands on the program." "not ... until"; state: approved payment-plan request; single writer `accept_payment_plan_2bd91da1`. One reading.
- E5 "The monthly installment of a payment plan is fixed only after every strip claim line the payer denied under a signed liability notice carries its non-covered item patient charge on the program." "only after"; state: non_covered_item charge rows; single writer `post_noncovered_charge_41a38519`. The sentence is broader than what the base denial route lets the depended-on policy charge (finding C7).
- E6 "Before the monthly installment of a payment plan is fixed, every posting named on an approved hardship application of the program must carry its hardship waiver balance adjustment." "Before"; state: hardship_waiver adjustment against the named posting; single writer `post_hardship_waiver_f8410ea4`. One reading.
- No rule carries a second wording of any edge, a tool name or another extended policy's id (scan: no target-tool stem and no extended-policy id occurs in any rule); the depended-on rules do not restate the sentences. No undeclared cross-problem order found in the extended rules (the notice rule's "on or before the ship date" is the inherited base sentence and is covered by the declared E2 edge; the refill rule's "the customer confirms it personally first" is a caller confirmation, not a problem).
- Base sentences stating a cross-problem order (`bgm_liability_notice`: "only after the customer signs ... before the ship date") are not relied on: E2 has its own extended sentence.

### override_declarations

Sentence-by-sentence against `base_policy_refs`:

- bgm_ext_superseded_strip_takeback (`overwrite: []`; refs bgm_evt_returns, bgm_preferred_meter, bgm_evt_replacement_and_delivery): unopened-only, return window, "never exceed the units of that shipment, less any units already authorized", restoring to the authorization on receipt — all followed or untouched; "strips for the old meter are not shipped after the change" — followed; replacement rules untouched. No undeclared override.
- bgm_ext_above_coverage_notice (overwrite of the quantity-limits measurement clause; refs bgm_liability_notice, bgm_evt_quantity_limits, bgm_combo_cgm_backup): measurement window/count declared; "further limited by the quantity on the written order" followed (order units); rounding down followed; CGM reduction only for an active CGM followed. MA/self-pay notice inapplicability not excluded (observation O10). No undeclared override found.
- bgm_ext_new_meter_strip_supply (overwrite of bgm_evt_refill_shipment's supply-days/units clause): the superseded clause includes "the units and pieces follow from the supply days under bgm_evt_quantity_limits", and the replaced_by states that this refill's units follow from "those days, the rates, the take-back exchange and the setup units stated here"; read with that delegation removed, the base sentence "quantities are rounded down to whole units within the allowance" no longer governs this refill's units, so the rule's "rounded up" is judged declared (observation O1). Base `bgm_combo_cgm_backup` "a CGM program in ... on_hold ... does not reduce the allowance" vs the extended CGM-phase (backup rate after an on-hold CGM program's hold limit): the extended governs shipped units, not the allowance; tension recorded as observation O2. Other base refill sentences (one grant, valid-through, confirmation, earliest ship date, reverification, free standard shipping, payer claim) followed. The base cap "units shipped may not exceed the program's authorized units remaining" is not in compute (compute caps at the drawn grant's unshipped units only) — not reached in task 0 (106 remaining).
- bgm_ext_noncovered_strip_charge (overwrite of "that the payer denied, charged at the Larkfield cash price of the units concerned"): price and reductions declared. NOT declared: the base denial route. Base `bgm_evt_denials_and_appeals`: "A denial is worked by its denial code, and the code alone decides the route ... CO-50 (not medically necessary), CO-151 (frequency or quantity not supported) and CO-197 (authorization absent) are appealable ... a CO-151 denial [is appealed] only when a medical record supporting the quantity, dated on or before the date of service, is on file; otherwise the denial is not appealed and is handled as a non-covered amount under bgm_liability_notice." The extended concerned-units tier 1 prices "CO-151 or CO-50" denials as customer charges with no exclusion of CO-50 (always on the appeal route) or of CO-151 with a supporting record (on the appeal route) -> finding C7.
- bgm_ext_hardship_cost_share_waiver (`overwrite: []`): tier, approval and counselling gates inherited and respected; base "each against the one posting it adjusts and never for more than that posting's unpaid remainder" — not implemented (finding C9). Partial waivers (shares below 1) do not contradict any base sentence.
- bgm_ext_payment_plan_installment (`overwrite: []`): base "A payment plan is offered only on tiers where payment_plan_max_months is greater than 0, for a balance of at least payment_plan_min_balance_usd" — in base the balance is "The customer's balance on the program"; the extended tests "a covered balance of at least payment_plan_min_balance_usd" where the covered balance adds the active CGM program's balance -> undeclared override (finding C8). Max months, min monthly, oldest-first application and the past-due exclusion are respected.
- bgm_ext_courtesy_bridge_reship (`overwrite: []`): cap "never exceeds the units of that original shipment" kept; courtesy count kept; partial quantity is within the cap; the added past-due gate is an extra necessary condition. No undeclared override.

### factor_ladders

Structure only (weight is per task). P = parameter, M = method, MS = every non-fall-through tier a conjunction/disjunction over distinct records, XD = cross_difficulty.

| policy | factor | label | tiers | distinct outcomes | MS | XD | structural verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| takeback | held_shipment_choice | M | 3 | yes | no | - | pass |
| takeback | use_end_anchor | M | 3 | yes | no | - | pass |
| takeback | testing_pace | P | 3 | yes (5.0/4.0/1.5) | yes (treatment class on the bgm program AND regimen on the open CGM program) | cgm | pass |
| takeback | sensor_status_shift | P | 3 | yes (+2.0/-2.5/0) | no | cgm | pass |
| notice | coverage_allowance_tier | P | 4 | yes (tier 2 differs from the fall-through only on PPO: min(200,150)=150 vs 200; reachable) | yes (treatment class AND CGM status) | cgm | pass |
| notice | window_netting | P | 4 | NO — every tier equals take-back units + notice units on its own domain | (yes) | - | FAIL C1 |
| notice | notice_reach | M | 4 | yes | yes for tiers 1-2 (order dates/quantities AND tier notice type AND CGM hold), tier 3 single | cgm | pass |
| notice | window_convention | M | 3 | yes | no | - | pass |
| refill | order_rate_choice | P | 3 | yes | yes (order row vs refill/grant rows AND order date) | - | pass |
| refill | supply_span | M | 3 | yes | no | - | pass |
| refill | sensor_phase | M | 3 | yes | no | cgm | pass (realism O2) |
| refill | takeback_exchange | P | 3 | yes (received vs authorized; distinguishing input received 1 / authorized 2) | no | - | pass |
| refill | setup_allowance | P | 3 | yes (1/2/0) | no | - | pass |
| noncovered | concerned_units_route | M | 3 | yes (tier 2 vs fall-through coincide only while notice units <= shipment units; distinguishing input notice > shipment, see O11) | no | - | pass |
| noncovered | unit_price_basis | P | 3 | yes | no | - | pass (label O4) |
| noncovered | posting_delay_share | P | 3 | yes | no | - | pass |
| noncovered | hardship_relief_share | P | 3 | yes | no | - | pass |
| hardship | waivable_basis | M | 3 | yes | yes (posting type/amount on the billing row AND the program tier's deductible/copay) | - | pass |
| hardship | counted_adjustment_kinds | P | 4 | NO — every tier equals billing_correction total + secondary_payer_payment total on its own domain | (yes) | - | FAIL C1 |
| hardship | payer_class_share | P | 4 | yes on the reachable domain, but the fall-through is unreachable and its outcome contradicts base | no | - | FAIL C3 |
| hardship | posting_age_share | P | 3 | yes | no | - | pass |
| hardship | household_relief_share | P | 3 | yes | no | cgm | pass (seed check per task) |
| payment plan | household_coverage_scope | M | 3 | yes | no | cgm | pass |
| payment plan | aged_first_payment | P | 3 | yes (aged balance vs fixed 25.00) | no | - | pass |
| payment plan | balance_band_months | P | 3 | yes | no | - | pass |
| payment plan | prior_plan_record | P | 3 | yes | no | - | pass |
| payment plan | hardship_months_extension | P | 3 | yes | no | - | pass |
| courtesy | bridge_shape | M | 3 | yes | no | - | pass |
| courtesy | bridge_day_convention | M | 3 | NO — tier 2 equals the fall-through on its whole reachable domain | no | - | FAIL C2 |
| courtesy | bridge_daily_rate | P | 3 | yes | tier 1 is one record condition (plus a tier parameter) -> no | - | pass |
| courtesy | repeat_courtesy_share | P | 3 | yes | no | - | pass |
| courtesy | sensor_wear_share | P | 3 | yes | no | cgm | pass |
| courtesy | transit_allowance | P | 3 | yes | no | - | FAIL C3 (fall-through outcome) |

Counts after striking the failed factors (bounds 4-6, >=2 P, >=1 M per computation):

- takeback 4 (2P, 2M) — within bounds.
- notice 3 surviving (1P, 2M) — BELOW bounds (C1).
- refill 5 (3P, 2M) — within bounds.
- noncovered 4 (3P, 1M) — within bounds.
- hardship 3 surviving (2P, 1M) — BELOW bounds (C1 + C3).
- payment plan 5 (4P, 1M) — within bounds.
- courtesy 4 surviving (3P, 1M) — within bounds.
- Per task (scope inferred from personas): task 0 has MS factors testing_pace, coverage_allowance_tier, order_rate_choice and XD factors on cgm; task 1 has MS factor waivable_basis and XD factors household_relief_share, household_coverage_scope, sensor_wear_share.
- Every surviving tier's value or method is drawn from the charter's own params/tier parameters; every tier is stated in its rule and implemented in compute (mechanical and manual sweep); `decides` is never `result`; binding sets are disjoint. Factor independence: no factor binding reads another factor's binding (traced: takeback `use_days`, notice `window_allowance`/`covered_reach_units`, refill `phased_strips`/`result`, plan `plan_months`/`result`, courtesy `bridge_strips` are non-factor assembly bindings); refill `supply_span` tier 1 and `setup_allowance` tier 1 key on the same fact (first refill after a new meter) — correlated but not reading each other (observation O16).

### findings

C1 — SOURCE-FACTOR RED (class: ladder whose tiers are one formula written as cases). Members (complete list after scanning all 33 factors):
1. `bgm_ext_above_coverage_notice.window_netting`: tiers "take-back units plus notice units" (both on file), "the take-back units" (no notices), "the notice units" (no take-backs), "0" (neither). On each tier's own domain its value equals take-back + notice, so all four tiers select one value; no input distinguishes any pair. The factor is one non-tiered rule (net both) against a baseline (net nothing).
2. `bgm_ext_hardship_cost_share_waiver.counted_adjustment_kinds`: tiers "their total" (only billing_correction), "their total" (only secondary_payer_payment), "the two totals together" (both), "0" (none) — identically correction + secondary on every tier's domain.
Consequence: struck as factors, the notice computation keeps 3 factors with 1 parameter and the hardship computation keeps 3 with C3 — both below the 4-factor / 2-parameter floor. Bears on task 0 (notice) and task 1 (hardship); demonstrated in 0.md and 1.md.

C2 — SOURCE-FACTOR RED (class: method tiers that coincide on their reachable domain). Member: `bgm_ext_courtesy_bridge_reship.bridge_day_convention` tier 2 ("on the self-pay tier they run to the end of the supply less refill_contact_lead_days") vs fall-through ("the days until the next refill may ship", i.e. supply left less refill_ship_lead_days). Tier 2 is reachable only on the Self-Pay tier, where refill_contact_lead_days = 7 = refill_ship_lead_days (bgm.yaml lines 230-231); every self-pay input gives the same bridge days under both. No other pair in the charter coincides on its reachable domain (checked: window_convention tier 1 vs fall-through differ whenever months 2-3 carry refills; coverage_allowance_tier tier 2 differs on PPO; bridge_daily_rate tier 2 vs fall-through differ off self-pay; takeback_exchange, order_rate_choice, concerned_units_route each have a distinguishing input listed in the table). The ladder keeps two real tiers (< 3). Bears on task 1 (courtesy); the courtesy count stays within bounds.

C3 — SOURCE-FACTOR RED (class: tier outcome no such business publishes for that situation). Members:
1. `bgm_ext_hardship_cost_share_waiver.payer_class_share` fall-through "1 on every other tier": the only tiers it can name are Self-Pay and Medicaid, where `hardship_waiver_allowed` is false and base says "A hardship waiver is granted only on tiers where hardship_waiver_allowed is true" (bgm.yaml lines 220, 541, 1576-1577). The fall-through therefore publishes a full (share 1) waiver for exactly the customers base never waives, and no customer who reaches this write is on it; the effective ladder has no reachable fall-through.
2. `bgm_ext_courtesy_bridge_reship.transit_allowance` fall-through "0 otherwise": the shipping methods are standard, expedited, expedited_no_charge (bgm.yaml line 747), so "otherwise" is exactly a refill Larkfield shipped two-day at its own cost; it gets 0 transit days while a customer-paid two-day refill gets expedited_transit_days 2. The condition also reads the original package's method, whereas the transit the bridge must cover is the reship's own (the tool takes the reship's `shipping_method`).
Bears on task 1; demonstrated in 1.md (the tiers taken there are not the fall-throughs, so the consequence is structural).

C4 — SOURCE-POLICY RED (rule vs compute; the reach-block share). Rule: "The coverage is ... strips_per_90_days_insulin for an insulin-treated customer who holds no active CGM program ..." and "every 30-day block of the reach beyond the blocks the window spans adds one block's share of the coverage, that share being the coverage divided by the window's 30-day blocks and by strips_per_billing_unit", while the 30-day tier sentence keeps "the coverage" distinct from what is measured: "the coverage measured against it is one third of the coverage", and the PA tier: "what is measured against it is not the coverage but the units approved". Compute: `block_units = int((window_allowance / window_blocks) // P('strips_per_billing_unit'))` with `window_allowance` = one third of the coverage (30-day non-PA tiers) or the PA monthly strips (PA tier). Members: (a) 30-day non-PA tiers (Self-Pay, Commercial HMO): rule share = coverage/1/50, compute = (coverage/3)/1/50 — a factor of 3; (b) PA tier (Medicaid): rule share = coverage/1/50, compute = PA units per block. Demonstrated on task 0 (HMO) in 0.md: second reading 1 unit vs 7.

C5 — SOURCE-POLICY RED (first-match read with a decoy). Rule: "the notice that counts is the latest liability notice for test strips signed on or before that shipment's ship date, a notice signed later counting as none." Compute: `notice_date = LATEST(... notice_date ...)` over all strip notices, then `notice_units = notice_units_signed if (notice_date and notice_date <= ship_date) else 0`. Same situation, different conclusions: notices of 2026-06-01 (5 units) and 2026-08-01, shipment 2026-07-06 — rule counts the 06-01 notice (5 units), compute counts none (charge 0). Not reached in task 1 (one notice on file).

C6 — SOURCE-POLICY RED (rule vs compute; zero recent applications). Rule: "medicare_hardship_share on the Original Medicare and Medicare Advantage tiers when the program has only one approved hardship application received within the last 12 calendar months, medicare_repeat_share on those tiers when it has more than one, commercial_hardship_share on the Commercial HMO and Commercial PPO tiers, and 1 on every other tier." Compute: `K('medicare_hardship_share') if (medicare_tier and approved_recent <= 1)`. A Medicare-tier program whose only approved application was received 13 months ago: compute 0.75; the rule's Medicare tiers both fail and "every other tier" names other tiers — the rule gives no 0.75. Not reached in task 1 (one recent application).

C7 — SOURCE-POLICY RED (undeclared override of the base denial route). Passages: base `bgm_evt_denials_and_appeals` (quoted in override_declarations: the code alone decides the route; CO-50 and CO-151 appealable; CO-151 appealed when a supporting record dated on or before the date of service is on file, "otherwise ... handled as a non-covered amount under bgm_liability_notice") vs extended `bgm_ext_noncovered_strip_charge`: "The units concerned are, when the denied claim also carries a remittance and the denial code is CO-151 or CO-50, the shipment's units above the units the treatment-class allowance gives ..." and the E5 sentence "every strip claim line the payer denied under a signed liability notice carries its non-covered item patient charge". The overwrite names only the price clause. For a CO-50 denial, and for a CO-151 denial with an over_limit_justification record dated on or before the date of service, base routes to appeal and extended to a customer charge. Bears on task 1 (CO-151 with the 2026-01-08 record on file); demonstrated in 1.md.

C8 — SOURCE-POLICY RED (undeclared override of the payment-plan minimum balance). Base `bgm_evt_patient_account`: "The customer's balance on the program is the running total of its patient-balance postings ... A payment plan is offered only on tiers where payment_plan_max_months is greater than 0, for a balance of at least payment_plan_min_balance_usd". Extended: "offered under bgm_evt_patient_account only on tiers where payment_plan_max_months is greater than 0 and for a covered balance of at least payment_plan_min_balance_usd" with "The plan covers the program's balance together with the balance of the customer's active CGM program when that CGM balance is above 0". `overwrite: []`. A program balance below the minimum with a CGM balance that lifts the covered balance over it: base offers no plan, extended offers one. Bears on task 1; demonstrated in 1.md.

C9 — SOURCE-POLICY RED (inherited cap dropped). Base: "A balance adjustment is posted only for one of these reasons, each against the one posting it adjusts and never for more than that posting's unpaid remainder"; base also applies payments "to the oldest unpaid posting first". Extended hardship rule and compute subtract only billing_correction/secondary_payer_payment adjustments and never cap at the unpaid remainder; the baseline subtracts nothing. A named posting of 46.16 that oldest-first payments have reduced to 5.00: base caps the waiver at 5.00, compute returns the full formula. `overwrite: []`. Task 1's gold-candidate value is under the cap (1.md), so no task consequence; the baseline value there exceeds it (recorded in 1.md as an observation).

Observations (no demonstrated consequence on a task's scored solution):
- O1 refill rounding: ceil of the phased strips vs base "quantities are rounded down to whole units within the allowance"; judged declared through the superseded delegation clause (see override_declarations). In task 0 the floor reading would give 7 instead of 8 (0.md).
- O2 refill CGM phase: after an on-hold CGM program's hold limit the refill drops to the CGM backup rate, although at that limit the CGM program is closed under `cgm_holds_and_closure` unless resumed, and base `bgm_combo_cgm_backup` says an on-hold CGM program "does not reduce the allowance". Realism tension; not demonstrated as a second defensible reading because the replaced_by places the units under this policy.
- O3 RND vs "rounded half up" in the money tool docstrings (Python float `round`).
- O4 `unit_price_basis` labelled parameter although tier 1 changes the price's basis (allowed amount over allowance units); counts unaffected either way.
- O5 payment plan: the policy's first payment has no field in `accept_payment_plan_2bd91da1` and no payment tool exists; the subject is listed as bgm_patient_payment while the write is a bgm_requests row.
- O6 `recent_sensor_refills` (takeback, courtesy) counts sensor refills of every CGM program of the customer; the rules say "shipped on it".
- O7 `takeback_received` counts every strip return receipt of the last month, not only receipts under a take-back.
- O8 E3 condition's "within the last calendar month" vs the sentence's open window (boundary day only).
- O9 state_gate `gate` names a DB field, not an eligibility id.
- O10 the notice policy does not exclude Medicare Advantage / Self-Pay, where base says no notice applies or can make the member liable.
- O11 `concerned_units_route` fall-through can charge more units than the shipment carried when a notice covers more units than shipped.
- O12 docstring words "until", "afterwards", "before it is passed" describe effects/formatting, not call order.
- O13 courtesy past-due gate fires at any past-due amount above 0, while base holds shipments only at past_due_hold_min_usd and above.
- O14 a bgm payment plan covering the CGM balance is recorded only on `bgm_requests`; the CGM program's own past-due test (`cgm_evt_patient_account`) cannot see it.
- O15 payment plan: no precedence stated when both a withdrawn and a completed plan fall in the last 12 months.
- O16 `supply_span` and `setup_allowance` both key on "first strip refill after a newly supplied meter".

## closing_checklist

Written after both reveals (2026-10-15 02:27 UTC); the sections above were frozen before it and are unchanged.

- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision 1 (no older revision exists).
- Scope: charter_scope of task 0 = {new_meter_strip_supply, above_coverage_notice, superseded_strip_takeback}, task 1 = {courtesy_bridge_reship, payment_plan_installment, noncovered_strip_charge, hardship_cost_share_waiver} — pairwise disjoint, jointly all seven extended policies, as inferred before reveal.
- Problem trees: task 0 two prerequisite problems / 2 value_input edges; task 1 three / 2 value_input edges; each has an owner=user write; difficulty-wide graph acyclic.
- uuid8s independent (action_binding_and_uuids).
- NOT CLOSED: the difficulty does not pass the source-layer audit. Comparison verdicts: task 0 SOURCE-POLICY RED (C4) + SOURCE-FACTOR RED (C1); task 1 SOURCE-POLICY RED (C7, C8) + SOURCE-FACTOR RED (C1, C3, seeded CGM rows, C2 structural, proof-field multi-source claim). Charter-global RED items C1-C9 (C5, C6, C9 carry no consequence on either task's scored value but are demonstrated on the charter domain).
- Gate re-run on the final form: not performed by this audit (the audit edits nothing and runs no instantiation gate; the brief's snapshot stands).

## revision_2

### charter_global_frozen (revision 2)

- re-audit round 2; freeze time 2026-10-15 08:45 UTC, written before either task's round-2 GT was revealed; nothing below is derived from a round-2 GT. The revision-1 text above is left untouched.
- inputs (sha256, all match the brief): `bgm.extended.yaml` f1d47f736f0824280a2465e4a7576b35073ba6f2da1d236e0d2fc432fddf5a2d (changed since round 1 -> every charter-global section re-derived in full); `task_tools.py` da2f86957357d3211b62510a5a29094f73f4d273f9cfdbb555972e92e2ab40a1 (changed -> re-derived); views 0.view.json 14dd84f4... (unchanged) and 1.view.json 8b2c0fc1... (changed); `blueprint/products/bgm.yaml` and `cgm.yaml` unchanged (df5cf421..., 0ddf69b2...).
- entry conditions: gate snapshot supplied (all green except TRACEABILITY on unlock tool names, pre-render); views supplied with hashes; input complete.
- mechanical checks re-run: base section still byte-identical to `products/bgm.yaml`; every compute_basis, baseline.rule, policy_source and replaced_by is verbatim in its own rule; every superseded_clause is verbatim in its base policy; compute and compute_basis keys correspond one to one; no prerequisite sentence carries a snake_case token, a tool stem or a policy id; no rule names a task tool or another extended policy; no authoring-viewpoint phrase in any prerequisite field.
- read isolation and masking as in revision 1; the round-1 compact dump in /tmp/audit_bgm_0063/ was used only to locate what changed.

### what changed in the charter (located by diff, then re-read in full)

- takeback: rule wording of the wearing-shift tier now says "shipped to the customer on any of the customer's CGM programs" (matches the cross-customer XCOUNT); compute unchanged.
- notice: `window_netting` is now a plain binding (take-back units + notice units), stated in the baseline sentence; new factor `regimen_testing_uplift` (parameter; +pump_regimen_extra_strips 270 / +mdi_regimen_extra_strips 150 / 0, read from a CGM program that is on hold or not yet active); the block share now reads "what is measured against the window divided by the window's 30-day blocks"; new exclusion "No notice is sized on a tier whose liability_notice_type is organization_determination_required or not_applicable".
- refill: rule/ladder wording of the exchange tier ("recorded as received back on the program"); E3 condition now "while the return window ... is open"; compute unchanged.
- noncovered: prices only a strip refill whose denial is CO-151 with no over_limit_justification record on file, or PR-204, with the latest strip notice signed on or before the ship date and a notice tier; CO-50, CO-197, CO-151-with-record and a later latest notice are left to the base route with no charge from this policy; units capped by the shipment's units.
- hardship: `counted_adjustment_kinds` removed (all adjustments against the posting are subtracted, plain binding); `payer_class_share` re-laddered (Medicare repeat 0.6 / Medicare one-or-none 0.75 / otherwise 1 = Commercial HMO/PPO); new factor `payment_effort_share` (no payment in 6 months 0.8 / none in 3 months 0.9 / else 1); explicit cap at the posting less its adjustments and at an oldest-first remainder; no waiver on tiers where hardship_waiver_allowed is false.
- payment plan: offered only for a program's balance of at least payment_plan_min_balance_usd; first payment removed; `household_coverage_scope` and `aged_first_payment` replaced by `plan_balance_scope` (method: balance less charges of the last month / aged balance alone when it coexists with postings of the last 4 months / balance) and `household_months_extension` (CGM balance >= 100 -> +2, > 0 -> +1, else 0); withdrawn-vs-completed precedence stated; short_plan_months now 2; E5 sentence now "every strip claim denial that is not appealed but handled as a non-covered amount under a signed liability notice"; E6 sentence now names "the posting named on the program's latest approved hardship application".
- courtesy: `bridge_day_convention` re-cut as a parameter on the lead days (0 when the stood-in refill shipped on a recorded confirmation on a 90-day tier / refill_contact_lead_days when on a recorded confirmation on a 30-day tier / refill_ship_lead_days otherwise); `transit_allowance` removed — the reship's own method is now fixed by the rule (standard for a standard original, expedited_no_charge otherwise) and its transit days follow it; new factor `fingerstick_reserve` (pump 40 / MDI 30 / 0 strips from the open CGM program's regimen); cgm_wearing_share 0.6; E4 sentence drops "covering the program's balance".
- tools: the money docstrings now say "already rounded to the cent before it is passed" (no half-up claim); the reship's `shipping_method` docstring adds "as for a reship standing in for a two-day package"; bodies still check nothing; uuid8s unchanged.

### round-1 RED items, closure check

- C1 closed: no ladder of the charter is one formula written as cases (all 33 factors re-scanned; window_netting and counted_adjustment_kinds are no longer factors).
- C2 closed: `bridge_day_convention` tier 2 (30-day tier, recorded confirmation: HMO 10, Medicaid 14) and its fall-through (no recorded confirmation, i.e. Self-Pay: 7) differ on tier 2's whole reachable domain; tier 1 (0) differs from both.
- C3 closed: `payer_class_share`'s fall-through is now the Commercial HMO/PPO tiers, reachable and published at full waiver; the original-method transit tier is gone and transit follows the reship's own method.
- C4 closed: the share is defined on "what is measured against the window", which is exactly `window_allowance / window_blocks` on all three window tiers.
- C5 closed: rule and compute now both take the program's latest strip notice and price nothing when it post-dates the ship date.
- C6 closed: the rule's Medicare tier now covers "one such application or none" = compute `approved_recent <= 1` side.
- C7 closed: CO-50 and CO-197 are not priced; CO-151 is priced only with no over_limit_justification record on file (stricter than base's "dated on or before the date of service", the difference being left to the base route by the rule's own deferral sentence).
- C8 closed: the minimum is tested on the program's balance (`plan_offered`), matching base.
- C9 closed: the cap is in rule and compute; on any world where oldest-first payments stop at or before the named posting it equals the posting's oldest-first remainder (it can only be lower when other postings fall inside the N-month window, which is stricter than base, never looser).

### new or residual charter-global items (revision 2)

R2-1 — SOURCE-FACTOR RED (unreal tier, new in round 2): `bgm_ext_above_coverage_notice.regimen_testing_uplift`. Rule: "To the coverage are added pump_regimen_extra_strips strips when the customer's CGM program that is on hold or not yet active records the insulin regimen insulin_pump, mdi_regimen_extra_strips strips when such a CGM program records multiple_daily_injections ... because a customer whose sensor is paused or not yet started tests by fingerstick at the pace of that regimen." The tier treats the customer's testing need as plan coverage. No payer of this charter covers strips on that ground: the coverage parameters are strips_per_90_days_insulin / _non_insulin / _with_cgm only, base `bgm_combo_cgm_backup` says an on-hold or not-yet-active CGM program "does not reduce the allowance" (and nothing raises it), and base `bgm_evt_quantity_limits` keeps (not superseded) "A quantity above the allowance is covered only when a medical record with purpose over_limit_justification ... is dated no more than high_utilization_record_months calendar months before the ship date ... and without such a record an above-allowance quantity ships only under bgm_liability_notice". A notice sized against the uplifted coverage leaves the uplift's units outside the notice although the payer will deny them, so they become Larkfield's write-off — a sizing no supplier would publish. The condition (regimen on a paused CGM program) is one no payer in the charter weighs for strip coverage. Bears on task 0 (on-hold MDI CGM; demonstrated in 0.md revision_2).

R2-2 — SOURCE-POLICY RED (prerequisite condition narrower than its sentence; residual of round-1 C7's E5 breadth): E5 sentence "The monthly installment of a payment plan is fixed only after every strip claim denial that is not appealed but handled as a non-covered amount under a signed liability notice carries its non-covered item patient charge on the program." Field `condition`: "the strip claim denial named by the program's latest bgm_claim_denial, when it is a CO-151 denial with no medical record of purpose over_limit_justification on file or a PR-204 denial and the program's latest bgm_liability_notice_signed for A4253 is dated on or before the shipment's ship date, has a ... non_covered_item for that shipment". The sentence covers every such denial and every base-routed non-covered denial (e.g. CO-151 whose only over_limit record is dated after the date of service, which base handles as non-covered); the condition covers only the latest denial and only the two codes this policy prices. Same situation, different conclusions: two uncharged non-covered strip denials on file — the sentence leaves the installment unfixable until both carry charges, the condition is met after one. Not reached in task 1 (one denial on file).

Observations (revision 2):
- O1, O2, O4, O9, O12, O13, O16 stand as in revision 1 (claimed open by the reworker; re-checked, unchanged).
- O17 `payment_effort_share` lowers a hardship waiver for a customer who has made no payment in 3-6 months; a hardship programme that weighs the customer's own payments is publishable, but it is the opposite of the hardship rationale; not demonstrated as unreal.
- O18 the reship rule grants expedited_no_charge to stand in for a customer-paid expedited refill ("whether the customer paid for it or not"), whereas base `bgm_evt_refill_shipment` records expedited_no_charge only "when the expedite only makes up for a delay Larkfield caused" (a refill sentence; base says nothing about a courtesy reship's method).
- O19 the reship tool's `shipping_method` docstring now carries a policy cue ("as for a reship standing in for a two-day package").
- O20 `plan_balance_scope` tier 1 subtracts the charges of the last month — including the non-covered charge E5 makes the plan wait on — from the covered balance, while `plan_offered` and the band still count it; coherent, but the E5 `effect` text ("raising the covered balance") holds only through the tier switch it causes.

### factor_ladders (revision 2)

| policy | factors (label) | count P/M | MS | XD | structural verdict |
| --- | --- | --- | --- | --- | --- |
| takeback | held_shipment_choice (M), use_end_anchor (M), testing_pace (P), sensor_status_shift (P) | 2/2 | testing_pace | cgm x2 | pass |
| notice | coverage_allowance_tier (P), regimen_testing_uplift (P), notice_reach (M), window_convention (M) | 2/2 | coverage_allowance_tier | cgm x3 | regimen_testing_uplift FAIL R2-1 -> 3 surviving (1P) |
| refill | order_rate_choice (P), supply_span (M), sensor_phase (M), takeback_exchange (P), setup_allowance (P) | 3/2 | order_rate_choice | cgm | pass |
| noncovered | concerned_units_route (M), unit_price_basis (P), posting_delay_share (P), hardship_relief_share (P) | 3/1 | none | - | pass |
| hardship | waivable_basis (M), payer_class_share (P), payment_effort_share (P), posting_age_share (P), household_relief_share (P) | 4/1 | waivable_basis, payer_class_share | cgm | pass |
| payment plan | plan_balance_scope (M), balance_band_months (P), prior_plan_record (P), hardship_months_extension (P), household_months_extension (P) | 4/1 | none | cgm | pass |
| courtesy | bridge_shape (M), bridge_day_convention (P), bridge_daily_rate (P), repeat_courtesy_share (P), sensor_wear_share (P), fingerstick_reserve (P) | 5/1 | none | cgm x2 | pass |

All tiers distinct in outcome on their reachable domains (re-scanned pairwise: plan_balance_scope tiers 1/2/3 differ whenever charges of the last month or the aged/recent split are non-zero; household_months_extension 2/1/0; fingerstick_reserve 40/30/0; payment_effort_share 0.8/0.9/1); every tier stated in its rule and implemented in compute; `decides` never `result`; binding sets disjoint; no factor binding reads another factor's binding (new plain bindings `coverage_total`, `window_netting`, `counted_adjustments`, `waiver_cap`, `reship_method`, `transit_days`, `plan_offered` sit outside every factor). Labels honest (bridge_day_convention now selects a number of lead days -> parameter).

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-15 08:50 UTC).
- Files 0.md / 1.md / _difficulty.md each carry an appended `revision_2`; revision-1 text untouched.
- Round-1 charter REDs C1-C9: all closed (see "round-1 RED items, closure check" above). Reworker-claimed observation closures O3, O5, O6, O7, O8, O10, O11, O14, O15 verified; O1, O2, O4, O9, O12, O13, O16 remain open as claimed.
- Scopes disjoint and complete (charter_scope: task 0 three policies, task 1 four); trees: task 0 2 prerequisite problems / 2 value_input, task 1 3 / 2; owner=user write in each; graph acyclic; uuid8s unchanged and independent.
- Gold values moved only where the charter or world moved: task 0 notice 7 -> 5 (regimen uplift); task 1 waiver 11.11 -> 8.89 (payment share), plan 4 x 22.13 -> 4 x 24.98 (new plan rules and world balance); charge 19.12 and reship 4 unchanged.
- NOT CLOSED: R2-1 (SOURCE-FACTOR, new: regimen_testing_uplift realism; task 0's notice computation keeps 3 real factors) and R2-2 (SOURCE-POLICY, residual: E5 condition narrower than its sentence; no task consequence). Gate re-run on the final form not performed by this audit (brief's snapshot stands).
- Correction to the revision-2 factor_ladders table (noted after reveal, table left as frozen): payer_class_share is not multi-source (its second tier, "one of those Medicare tiers with one such application or none", rests on the tier alone); the hardship computation's MS factor is waivable_basis; courtesy's bridge_day_convention (refill confirmation record AND the tier's supply days) is multi-source. No verdict changes.

## revision_3

### charter_global_frozen (revision 3)

- re-audit round 3; freeze time 2026-10-15 09:38 UTC, before either task's round-3 GT was revealed; revision 1 and 2 text untouched.
- inputs (sha256, all match the brief): `bgm.extended.yaml` 28b5edc3738c3058b5d074063c5cdb2c646faac3c522d81415caa0e6ed22847b and `task_tools.py` ff767d510d91cf7fcf8d8315b81f8f2c7f7c28c2df7f70adabffab78104f617c (both changed -> charter-global sections re-derived; unchanged policies re-checked by diff against the round-2 dump); 0.view.json 6b3e95f6... (changed), 1.view.json 8b2c0fc1... (unchanged); products/bgm.yaml and cgm.yaml unchanged; base copy still byte-identical.
- mechanical checks re-run: compute/compute_basis one-to-one and verbatim; baseline.rule, policy_source, replaced_by verbatim in their rules; superseded_clause verbatim in base; no snake_case/tool/policy-id token in any prerequisite sentence; no rule names a task tool or another extended policy.

### what changed (round 2 -> round 3)

- notice: `regimen_testing_uplift` removed (rule, params, compute, replaced_by "with the CGM adjustment stated here" only); new factor `notice_order_rate` (parameter): newest strip order when it is not the order behind the latest strip refill and was signed within 30 days / the lower of the two when signed more than 30 days ago / otherwise the order behind the latest strip refill — the same ladder as the refill's `order_rate_choice`, "because the notice covers the rate the next refill ships at"; baseline sentence now "the units per 30 days of the written order behind the program's latest strip refill"; E1 condition now carries the sentence's antecedent (meter replaced, window open).
- refill: E2 condition carries "when the strip refill ships more units than the coverage leaves for its supply days ... signed by the customer"; E3 condition carries "for the first strip refill after a newly supplied meter". Rule and compute unchanged.
- payment plan: E5 sentence "The monthly installment of a payment plan is fixed only after the program's latest claim denial, when it denies a strip claim line and is not appealed but handled as a non-covered amount under a signed liability notice, carries its non-covered item patient charge on the program."; condition "when the program's latest bgm_claim_denial denies a claim billing an A4253 shipment, is not routed to appeal under bgm_evt_denials_and_appeals and is covered by a bgm_liability_notice_signed record for A4253 dated on or before that shipment's ship date, that shipment has a ... non_covered_item"; effect text now states the minimum-balance test, the band and the last-month exclusion.
- courtesy: the reship ships expedited_no_charge only when the stood-in refill shipped expedited_no_charge, "and by standard shipping otherwise, a customer-paid expedite included"; compute `reship_method` follows.
- tools: reship `shipping_method` docstring cue removed ("expedited_no_charge when the reship goes by two-day shipping that Larkfield pays for"); bodies unchanged in substance; uuid8s unchanged.
- takeback, noncovered, hardship: unchanged.

### round-2 RED items, closure check

- R2-1 closed: no tier of the charter adds strips to a payer's coverage on a ground the charter's payers do not weigh; the replacement `notice_order_rate` selects the prescribed rate, a quantity the base itself limits ("further limited by the quantity on the written order") and the refill policy already ships at. Its three tiers differ (newest vs min(newest, earlier) vs earlier; distinguishing inputs newest > earlier and newest < earlier). Notice: 4 factors, 2P (coverage_allowance_tier, notice_order_rate) / 2M (notice_reach, window_convention); MS coverage_allowance_tier; XD cgm. No factor binding reads another's (`notice_order_rate` and `notice_reach` both read the plain bindings newest_order_qty/date and prior_order_id/qty; neither reads the other).
- R2-2 closed: E5's sentence and condition now name the same object (the latest denial), the same route test (not appealed, handled as non-covered under base) and the same notice test (a notice signed on or before the ship date); a base-routed charge at the cash price for a denial whose latest notice post-dates the ship date is also covered by both, written through the same tool. Sweep over the other edges: E1, E2, E3 conditions now carry their sentences' antecedents; E4 and E6 unchanged and matching.
- O18 closed: a customer-paid expedite is no longer turned into a free expedite (matches base "recorded as expedited_no_charge when the expedite only makes up for a delay Larkfield caused"). O19 closed (cue removed). O20 closed (effect text accurate).
- O17 stands (claimed open); O1, O2, O4, O9, O12, O13, O16 stand as before.

### new defects (revision 3)

None found. Re-checked for regressions: factor counts per computation 4/4/5/4/5/5/6 with >= 2P and >= 1M; no collapsed or coinciding ladder; no unreachable fall-through; rule/compute equivalence holds on every changed binding (`notice_rate`, `reship_method`); prerequisite graph unchanged in shape and acyclic.

### closing_checklist (revision 3)

Written after the round-3 reveals (2026-10-15 09:41 UTC).
- Files carry appended `revision_3` sections; earlier revisions untouched.
- Round-2 REDs R2-1 and R2-2 closed; O18, O19, O20 closed; O17 open as claimed; O1, O2, O4, O9, O12, O13, O16 remain open observations (no demonstrated consequence).
- Per-task verdicts: task 0 PASS on all four relationships (gold 2 / 8 / 8, equal to the blind derivation); task 1 PASS on all four (gold 19.12 / 8.89 / 4 x 24.98 / 4, equal to the blind derivation, unchanged from round 2).
- Scopes pairwise disjoint and jointly covering all seven extended policies; trees: task 0 two prerequisite problems / 2 value_input edges, task 1 three / 2; each with an owner=user write; difficulty graph acyclic; uuid8s independent and unchanged.
- Every computation declares a self-sufficient baseline and 4-6 factors (>= 2P, >= 1M); each task has an MS factor (task 0 testing_pace / coverage_allowance_tier / order_rate_choice; task 1 waivable_basis / bridge_day_convention) and XD factors on seeded CGM rows consistent with the CGM charter; every factor bears weight with the all-baseline figure definite and different from gold.
- The difficulty passes the source-layer audit at revision 3. Instantiation-stage gates: the coordinator's round-3 snapshot (all green except the pre-render TRACEABILITY on unlock tool names) is cited; this audit did not re-run them.

## revision_4

### charter_global_frozen (revision 4)

- re-audit round 4 (after KB render); freeze time 2026-10-15 12:15 UTC, before either task's round-4 GT was revealed; earlier revisions untouched.
- inputs (sha256, match the brief): `bgm.extended.yaml` 98c8f6f7d92efe2cb78ae27c0eff1fd367f67c25ab3357085015819a1192bdfd (changed -> charter-global sections re-derived; all seven policies differ textually from round 3 and were re-read); `task_tools.py` ff767d51... (unchanged -> tool-contract conclusions of revision 3 carried forward on that hash); views 0 (6b3e95f6...) and 1 (8b2c0fc1...) unchanged; products/bgm.yaml, cgm.yaml unchanged; base copy byte-identical.
- additional permitted inputs read: `audits/render_source/testing_supply_program_services/findings.md` (F1-F9, base note) and the source-side sections of `audits/policy_kb/testing_supply_program_services/0.md`, `1.md` (render_source_findings_judgement, S9, B1). The KB documents themselves were not needed and not read.
- gate snapshot now fully green (TRACEABILITY OK after render).
- mechanical checks re-run: compute/compute_basis one-to-one and verbatim; baseline.rule, policy_source, replaced_by verbatim in their rules; superseded_clause verbatim in base (F3's narrowed clause "charged at the Larkfield cash price of the units concerned" is a substring of `bgm_liability_notice`); no forbidden token in any prerequisite sentence; no rule names a task tool or another extended policy.

### KB-surfaced items, closure check

- F1 closed: the hardship baseline sentence is now "the waiver is the waivable cost share less every balance adjustment already posted against that posting, never below 0"; each share is stated in its own sentence with its acting base ("Before the ceilings and the rounding apply, the waiver is multiplied by ..."); compute unchanged (`waiver_raw` then `MN(waiver_raw, waiver_cap)`), so rule and compute agree on the order.
- F2 closed: the courtesy baseline is now a self-sufficient method — "it ships one 30-day block of strips plus the transit days at strips_per_90_days_non_insulin divided by 90 strips a day, divided by strips_per_billing_unit and rounded up to a whole unit, never more than the refill's units" — and `bridge_shape` now only chooses the days covered (bridge days > 30 / every unit when 0 or fewer / one block otherwise; baseline mode 2 = its fall-through). The assembly sits in plain bindings (`cover_days`, `reship_strips`, `result`); rate, shares and reserve act on the baseline formula, so each bears weight without `bridge_shape` leaving its baseline. `bridge_day_convention` acts only through the bridge-days tier (an interaction through a plain binding, not a read of another factor's binding). Ladder distinct, rule = compute (`bridge_mode = 1 if >30 else (3 if <=0 else 2)`).
- F3 closed: superseded clause narrowed to the pricing phrase; the denial requirement stays in force from base and the extended rule.
- F4 closed: rule "when the program already has a strip refill and the meter ship date ... is later than the ship date of the program's latest strip refill; a program with no strip refill yet has no refill after a newly supplied meter" = compute `meter_newly_supplied = True if (latest_refill_ship and ...)`; the new-program setup tier is reachable again.
- F5 closed: rule now dates by "received within the last 12 calendar months that now stands withdrawn/completed" = compute (`received_at`).
- F6 closed: rule now states "never fewer than one block" and "nothing being measured against the window when the program holds no payer prior authorization for test strips" = compute (`MX(1, ...)`, `pa_grant_units or 0`).
- F7 closed: rule now states the precedence ("the latest replacement for non-receipt when one is on file, and otherwise the latest replacement for loss in transit") and the no-POD case ("or today while that replacement has no proof of delivery, so that its days of use then count as none") = compute.
- F8 closed: rule now "remittances whose allowed amounts total more than 0 and the treatment-class allowance gives at least one unit", else billed charge per unit, "0 when the shipment records no units" = compute (`SUM` of allowed, guards).
- S9 closed: E2 sentence now names the measure — "A strip refill that takes the program's test strips shipped over the 90 days ending on its ship date, that refill counted, above the tier's strip allowance is not shipped until ..." — and the condition names `bgm_msr_strips_shipped_90d` against the tier's allowance under `bgm_evt_quantity_limits`; one reading; single writer unchanged.
- F9 (KB auditor rejected; no change): agreed — the docstring's recorded effect is the return authorization row; the "prepaid return label" is a described real-world artefact with no schema entity; no scored effect disagrees. Observation only.
- B1 (base, BLUEPRINT-KNOWN): `bgm_combo_cgm_backup.formula` vs its rule for a non-insulin customer; no extended compute or tool reads `allowance_with_cgm`; task 0's CGM is on hold and task 1 is insulin-treated (min(300,300) on both readings). Not load-bearing; outside this audit's write domain.

### new defects (revision 4)

None found. Re-scan: factor counts 4/4/5/4/5/5/6, each >= 2P and >= 1M; ladders distinct on reachable domains (courtesy `bridge_shape` tiers: bridge days vs every unit vs one block); no factor binding reads another factor's binding; baselines self-sufficient and stated in their rules; prerequisite graph unchanged and acyclic; observations O1, O2, O4, O9, O12, O13, O16, O17 unchanged.

### closing_checklist (revision 4)

Written after the round-4 reveals (2026-10-15 12:15 UTC).
- KB-surfaced items F1-F8 and S9 verified closed in the charter; F9 agreed as a non-defect (observation); B1 base, not load-bearing for either task.
- Scored values unchanged in both tasks (task 0: 2 / 8 / 8; task 1: 19.12 / 8.89 / 4 x 24.98 / 4); only the courtesy fall-backs moved (bridge_shape 6 -> 2, all-baseline 6 -> 1), both still definite and different from gold.
- Scopes disjoint and complete; trees, value_input counts, owner=user writes and acyclicity as in revision 3; uuid8s unchanged; every computation 4-6 factors with >= 2P / >= 1M, MS and XD per task, every factor load-bearing against a self-sufficient baseline.
- Gates: coordinator's round-4 snapshot fully green (including TRACEABILITY); not re-run by this audit.
- The difficulty passes the source-layer audit at revision 4.

## revision_5

### charter_global_frozen (revision 5)

- re-audit round 5 (XF class sweep); freeze time 2026-10-15 16:15 UTC, before either task's round-5 GT was revealed; earlier revisions untouched.
- inputs (sha256, match the brief): `bgm.extended.yaml` 832415a5dce2f10291ab07afeeb3f9b964262eba9bfff5b6d09ddf43f458bd69 (changed -> re-derived); `task_tools.py` ff767d51... unchanged (tool-contract conclusions carried forward on that hash); views unchanged (6b3e95f6..., 8b2c0fc1...); products unchanged; base copy byte-identical. Read in addition: `audits/render_source/XF_recipe.md`.
- what changed: every rule reworded per the recipe (standard method first, shared quantities defined once in record terms, one generic combination sentence per policy, each factor sentence stating how it changes the standard quantity); ladder when/method texts brought in line with the rules (held_shipment_choice, window_convention, supply_span, unit_price_basis, bridge_shape); the courtesy baseline now includes the shipping-method / transit sentence; compute changed only in the courtesy reship: `bridge_day_convention` now decides `lead_adjust_days` (+refill_ship_lead_days on a confirmed 90-day refill / +(ship lead - contact lead) on a confirmed 30-day refill / 0), added to the covered days after `bridge_shape` picks them (`cover_days = (days_to_next if bridge_mode == 1 else 30) + lead_adjust_days`), replacing the old `bridge_days` that `bridge_shape`'s tier consumed. Every other compute line is identical to round 4.

### XF checks (recipe items 1-6, re-done independently)

- compute_basis: one key per binding (courtesy's removed `supply_left` / `bridge_lead_days` / `bridge_days` keys removed with them); every quote verbatim in its rule; baseline.rule verbatim in its rule; policy_source verbatim; superseded/replaced_by verbatim.
- No factor binding reads another factor's binding, in any policy (scripted transitive scan over all 33 factors: empty). The combination lives in plain bindings (`strips_used`, `window_allowance`/`covered_reach_units`, `phased_strips`/`result`, `charged_units`, `waiver_raw`, `plan_months`, `cover_days`/`reship_strips`).
- No baseline sentence and no combination sentence names a factor id or a factor's own quantity beyond the standard quantity it replaces (the notice baseline's "the notice reaches one 30-day block", the courtesy baseline's "one 30-day block" and the takeback's "daily_pace_default strips" are the standard figures the factors replace, as the recipe allows); each policy carries exactly one generic combination sentence ("Each rule set out below changes ... only ..."), with order stated generically where it matters (courtesy: replace days, then add days, then rate, then multiply, then add, then round/cap; refill: replacements before additions, limits last; notice: replacements then sizing; hardship: multiplications before ceilings and rounding; plan: replacements before months added/taken off, limits last).
- Rule = compute on every reworded sentence (sentence-by-sentence check of the seven policies; the courtesy's added-days sentence "Days are added to the days the reship covers: refill_ship_lead_days when ... 90 ...; refill_ship_lead_days less refill_contact_lead_days ... when ... 30 ...; and none otherwise" = `lead_adjust_days`; "when they are 0 or fewer, the reship instead replaces every unit of the refill, one for one, and no other rule below changes it" = `result = lost_units if bridge_mode == 3`).
- Ladders: tiers distinct on reachable domains — bridge_shape (days to next refill / every unit / 30-day block), bridge_day_convention (+10 on PPO/MA/OM, -3 on HMO, -7 on Medicaid, 0 on Self-Pay); all others as revision 4. Counts 4/4/5/4/5/5/6, each >= 2P and >= 1M; baselines self-sufficient, reachable (each fall-through is a tier real customers occupy) and stated in their rules.
- Realism of the changed courtesy method: lead-day adjustment now also applies to the one-block case (a confirmed 90-day-tier refill gets 40 days instead of 30) — the same rationale the rule gives for the bridge case; publishable.

### round-4 items

- None open at revision 4 (task0=PASS, task1=PASS, charter=CLEAN); the KB re-audit's stale-ladder items (R2-1/R2-A of that audit) are addressed by the ladder sweep above and found consistent.

### new defects (revision 5)

None found. Observations O1, O2, O4, O9, O12, O13, O16, O17 unchanged.

### closing_checklist (revision 5)

Written after the round-5 reveals (2026-10-15 16:15 UTC).
- XF recipe items 1-6 re-verified independently on all seven policies; rule = compute; compute_basis verbatim; no factor reads another; every factor bears weight against a self-sufficient, reachable baseline; method tiers distinct.
- Scored values unchanged in both tasks (task 0: 2 / 8 / 8; task 1: 19.12 / 8.89 / 4 x 24.98 / 4); one unscored courtesy fall-back moved (bridge_shape 2 -> 3), definite and not gold.
- Scopes, trees, owner=user writes, acyclicity, uuid8s as in revision 4. Gates: coordinator's round-5 snapshot all OK; not re-run by this audit.
- The difficulty passes the source-layer audit at revision 5.
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN
