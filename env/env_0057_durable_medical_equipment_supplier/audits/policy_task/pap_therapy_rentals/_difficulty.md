# Policy-task audit — pap_therapy_rentals / charter-global

## charter_global_frozen

- Frozen: 2026-10-12 19:11 UTC, before any task GT was revealed. Auditor: erl-task-policy-audit subagent (independent of the instantiating agent).
- Inputs and hashes (recomputed by the auditor, they match the coordinator's HASHES.txt):
  - `tasks/pap_therapy_rentals/pap.extended.yaml` sha256=ccc18b4c3256f59f12dd3907b3381f1733568cf7054528811b04cefb948deb79
  - `tasks/pap_therapy_rentals/task_tools.py` sha256=66ce95e647b6c3fbdc6ffb27f319cb6955936e65a68d68184f7f13b6c594da0d
  - `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{pap,coverage,resupply}.yaml`
  - the compute primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `eval_compute`, `substitute`), used only as the executable meaning of the restricted expressions
- Permitted: the charter, schema, shared tools and task tools; per task only `frozen_time`, `user_scenario`, `initial_state` through `.audit_views/policy_task/pap_therapy_rentals/{0,1}.view.json`.
- Masked and not read for this section: every task's `evaluation_criteria`, `computations`, `design_rationale`, `db_closure*`, `solvability_contract`, `prerequisite_closure`, `charter_scope`, `required_documents`. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): gate snapshot supplied with the brief — check_extended, check_task_tools, replay_tasks (--check), check_solvability, check_compute, check_grounding, check_cache_diff (info), check_cross_fire all rc=0; check_traceability rc=1 with the only misses being the four task-tool names, deferred to post-render by design. Masked views with hashes supplied. Input complete.
- Base copy: lines 1-1296 of `pap.extended.yaml` are byte-identical to `blueprint/products/pap.yaml` (`diff` shows only the appended `extended_policies` banner). The base is not rewritten.

### policy_conflict_scan

Extended policies (7) and their write bindings:

| policy | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| pap_ext_return_labor | pap_repair | labor_units | record_return_inspection_bc7317cd (agent) | [] |
| pap_ext_return_parts | pap_repair | parts_amount | record_return_inspection_bc7317cd (agent) | [] |
| pap_ext_used_accessories | pap_repair | repair_patient_share | record_return_inspection_bc7317cd (agent) | [] |
| pap_ext_self_pay_refund | pap_purchase_refund | refund_amount | return_device_for_refund_b6f98fe9 (user) | used_accessories, return_parts, return_labor (all value_input, state form) |
| pap_ext_usage_nights | pap_compliance_download | nights_4h_plus | record_usage_download_48c54aed (agent) | [] |
| pap_ext_usage_hours | pap_compliance_download | avg_daily_use_hours | record_usage_download_48c54aed (agent) | [] |
| pap_ext_home_unit_purchase | pap_purchase_sale | sale_amount | purchase_home_device_8c1f8216 (user) | usage_nights, usage_hours (both value_input, state form) |

- Overlapping subjects: three policies share `pap_repair` and one write (one inspection row carries the three computed fields); two share `pap_compliance_download` and one write. Their `computes` are distinct, their inputs never read each other's outputs, and they are evaluated on the same pre-write world, so no ordering conflict arises inside a shared write.
- Triggers / eligibility / time anchors: all four refund-side policies anchor "days kept" on `pap_holdings.setup_date` (the delivery date of a self-pay device) to the decision_date of the completed `return_pickup` request; the parts policy alone re-anchors its air-path clock (warranty repair date / sale date). The purchase anchors its hour-wear and trial clock on setup_date and NOW. No two policies give different anchors for the same quantity.
- Terminal states: none of the four tools changes `pap_holdings.status`; the refund leaves the self-pay record `patient_owned`, the purchase leaves the coverage record in whatever status it had (observation O9).
- Cross-category read boundaries: reads are confined to `resupply_holdings` (mask_style, humidifier_in_use, heated_tubing_in_use, status, enrollment_date) and `coverage_holdings` (variant parameters payer_type, allowed_pct_of_fee_schedule; status). Read-only; no cross-category write.
- Inferred task scopes from the views (to be confirmed against `charter_scope` after reveal): task 0 = {return_labor, return_parts, used_accessories, self_pay_refund}; task 1 = {usage_nights, usage_hours, home_unit_purchase}. Pairwise disjoint and jointly complete over the seven extended policies.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back over the rule. All `compute_basis` quotations are verbatim in their rules; every `baseline.rule` sentence is verbatim in its rule (scripted check, no miss). Per policy:

- return_labor: base 2 / keep ladder (>14 -> 2, >7..14 -> 1, else 0) / humidifier ladder (furnished & enrollment in use -> 2, furnished -> 1, else 0) / route ladder (virtual_setup -> 1, in_home_setup -> 2, else 0) / warranty method (>=2 -> max(sum,10), ==1 -> sum + that job's labor_units, else sum). Two faces agree; `int()` final.
- return_parts: filter 7.50 / chamber 24.00-9.50-0 / outlet 12.00 (heated) - 6.00 (standard & humidifier in use) - 0 / air-path kit 18.00-9.00-0 on >14, >7 / air-path anchor latest warranty repair date -> sale line date (`adjudication_date`, the schema's "transaction date" of a sale) when virtual_setup -> delivery date. Agree. Minor: the outlet binding filters `status='active'`; the rule's outlet sentence says "the tubing the patient's supply enrollment records" without "active" (observation O6).
- used_accessories: mask 129/108/89 by mask_style; tubing 63/39/15 by heated&humid / not-heated&humid / other; borne: enrolled & kept>14 -> min(kit, 12*days); kept<=14 -> mask; else kit; packaging 6.50/3.25/0; RND 2. Agree.
- self_pay_refund: worn value (>21 straight line over RUL*30, >14 0.4%/day beyond 14, else price) RND 2; restock pct by recorded parts (>=40 -> 20, >=10 -> 17.5, else class pct); fee RND 2; cap 140/170/uncapped by active enrollment tenure; withholding recorded share / 0 / 104; handling 35/20/0 by labor 10+/5-9/else; delivery-fee credit whole / half / 0; result RND 2. Agree. Minor: `enroll_months` reads `CFIELD('resupply','enrollment_date')` with no status filter while the rule speaks of the active enrollment (observation O5).
- usage_nights / usage_hours: serial-scope method, swap credit, acclimation / first-unit add-back, pressure credit. Agree. Minor: `all_nights` / `all_hours` / `all_windows` aggregate every `pap_compliance_download` row, including any earlier usage summary (`compliance_result none`), whereas the rule sums "the 30-night compliance windows" (observation O4).
- home_unit_purchase: list price by payer_type (medicare_ffs -> FSP; other active -> FSP*pct RND 2; else retail); wear (summary -> hours*days/20000; scored windows only -> 2%/window; else none) RND 2; failed-trial 15/5/0; repair 10/5/0; one combined discount RND 2; humidifier 79/39.50/0. Agree.
- Rounding primitive: `RND` is Python `round(float(x), n)` (ties-to-even on binary floats) while every rule says "half up" (observation O3). No exact half-cent tie occurs in either task world.

No compute binding invents a basis; no rule sentence is left unimplemented. **PASS** (observations O3-O6).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique: (record_return_inspection, labor_units / parts_amount / repair_patient_share), (return_device_for_refund, refund_amount), (record_usage_download, nights_4h_plus / avg_daily_use_hours), (purchase_home_device, sale_amount).
- Docstrings: no sequence position, no other tool name, no before/after/first. `record_return_inspection` hard-codes `repair_coverage='none'`, `repair_fault='none'`; `record_usage_download` hard-codes `compliance_result='none'`; `purchase_home_device` hard-codes `fee_amount=0.0`, `adjudication_date=today`. No tool reads or checks a prerequisite (function bodies only `ctx.find` the holding/sale for customer_id/hcpcs and `ctx.create`).
- uuid8s `bc7317cd`, `b6f98fe9`, `48c54aed`, `8c1f8216`: no shared prefix, no sequence, no adjacent values. **PASS**.
- Observation O11: the refund tool records the refunded amount in `sale_amount` but leaves `fee_amount` (base: "restocking fee withheld on a refund") unset.

### prerequisite_graph

- Every extended policy carries `prerequisite` (`[]` on five). Edges: self_pay_refund -> {used_accessories, return_parts, return_labor}; home_unit_purchase -> {usage_nights, usage_hours}. Every `problem` is an extended policy id of this file, none a base id, none self. Acyclic (depth 1).
- Every `policy_source` is verbatim in its own rule (scripted check: all five True).
- All `form: state`, no `fallback_reason` (correct for state form).
- `gate` bindings exist in compute: withheld_value, restock_pct, handling_charge, failed_pct, worn_price; all `kind: value_input`.
- `resolved_by` equals the depended-on policy's `target_tool` for all five; that write creates exactly the row the `condition` describes (`pap_repair` with `repair_coverage none`; `pap_compliance_download` with `compliance_result none`).
- No authoring-viewpoint phrasing in the prerequisite fields. **PASS** — except that the usage_hours edge's `effect` ("the worn price moves from the per-window wear to the therapy-hours wear") is accurate to the compute but not to its own sentence; see finding G1.

### prerequisite_sentences

| edge | sentence (verbatim) | four-point test |
| --- | --- | --- |
| refund <- used_accessories | "The refund is fixed only after the device's service history carries a return inspection recording the value of used accessories the patient bears." | "only after"; record-visible state; no tool/id/snake_case; scope = condition. PASS |
| refund <- return_parts | "No restocking percentage is set on the refund until the return inspection on the device record shows the reconditioning parts amount." | "until"; state; clean; reads as timing of the decision. PASS |
| refund <- return_labor | "Before the refund's handling charge is applied, the return inspection on the device record must show the reconditioning labor units booked for the unit." | "Before"; state; clean. PASS |
| purchase <- usage_nights | "The price of a unit bought where it already stands in the patient's home is fixed only after the device record carries a usage summary crediting the qualifying nights." | "only after"; state; clean. PASS |
| purchase <- usage_hours | "No wear is taken off the in-home unit's price until a usage summary on the device record states the average daily use." | "until"; state; clean; **broader than the condition / contradicts tier 2 of the same rule** — finding G1 |

- Single resolving write per state: the only writes in this difficulty that create a `pap_repair` with no cost assignment or a `pap_compliance_download` with no result are `record_return_inspection_bc7317cd` and `record_usage_download_48c54aed`; the shared tools write only identity verifications and hand-offs. Each state-form edge has exactly one resolving write.
- Derivation, refund side: sentence ("return inspection ... recording the value of used accessories / parts amount / labor units") + records (no inspection row on the record) + the depended-on rules ("the patient bears ... on its return inspection", "booked on its return inspection", "the branch books reconditioning labor ... on its return inspection") -> the inspection write carrying the three amounts. Unique reading.
- Derivation, purchase side: sentence ("a usage summary crediting the qualifying nights / stating the average daily use") + records (only scored windows) + depended-on rules ("Summit Ridge files a usage summary download on the device record ... it states the qualifying nights ...", "The average daily use on a usage summary download ...") -> the usage-summary write. Unique reading.
- No rule carries a second wording, a tool name or another problem's id; no depended-on rule restates the blocked sentence. The usage_nights rule's opening "When a patient asks to buy or settle a coverage-rented unit ... Summit Ridge files a usage summary download" is a trigger, not a cross-problem order; it grounds no undeclared edge.
- No base rule sentence is used to ground an edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusion per sentence of the base policy):

- **pap_repair_responsibility** (refs of return_labor, return_parts, used_accessories):
  - "Who pays for a repair follows the record's status." — followed; the inspection assigns no payer (tool hard-codes `none`).
  - "While ... trial_active, rental_active or suspended, any repair or swap is Summit Ridge's rental obligation ..." — not applicable (record is patient_owned).
  - "A patient-owned device within `manufacturer_warranty_months` of setup_date is repaired under the manufacturer warranty at no charge ..." — on a returned self-pay unit within 24 months this sentence would assign `manufacturer_warranty`; the extended side assigns no coverage. Not named in any `overwrite`. The governed field (`repair_coverage`) is hard-coded by the tool and not a computed argument; no scored quantity moves. Observation O8.
  - "Otherwise an owned device bought under coverage is repaired with labor at `repair_labor_rate_per_unit` ... billed to the coverage" — not applicable (self-pay).
  - "an owned self-pay device is repaired at the patient's cost (repair_coverage patient_paid)." — handled differently; declared in used_accessories' `overwrite` (superseded verbatim). return_labor and return_parts carry `overwrite: []` but do not touch the payer or the patient amount; their quantities (labor_units, parts_amount) are not governed by this sentence. OK.
  - "When labor plus parts would exceed `repair_cost_replace_threshold_pct` ... replaced" — followed (inspection amounts are far below 862.40 in every reachable world).
  - Loaner sentence — not applicable (tool writes `loaner_issued=False`, base: loaner only "while an owned device is out for repair").
  - "A repair is recorded only on a device the patient still has: the device record is trial_active, rental_active, suspended or patient_owned." — the operative test after the colon is the status list; a returned self-pay record stays `patient_owned`, so followed. The lead-in wording ("a device the patient still has") is at odds with a unit already received back; observation O8.
- **pap_self_pay** (refs of self_pay_refund, home_unit_purchase):
  - "Any class may be bought outright ... at `self_pay_retail_price` plus `self_pay_delivery_fee`, paid in full when the order is placed" — superseded by home_unit_purchase's `overwrite`; refund side follows it for the original sale.
  - "the Travel CPAP System (E0601) is sold only this way." — followed.
  - "A self-pay device is returned for a refund only when it comes back complete in its original packaging no later than `self_pay_return_window_days` ..." — inherited, not weakened (refund rule repeats "within the class's return window").
  - "The refund is the device price less `self_pay_restocking_fee_pct` percent, rounded ...; the delivery fee and any mask or tubing that has been used are never refunded." — superseded verbatim by self_pay_refund's `overwrite`.
  - "A sale is refunded at most once." / "A self-pay device is never billed to coverage afterward." — inherited.
- **pap_trial_compliance** (refs of usage_nights, usage_hours): "A compliance download scores one window of `compliance_window_days` consecutive nights" superseded by both (declared). Remaining sentences (conversion needs a `met` window, modem data only, failed trial) are untouched by a summary that carries `compliance_result none`. Followed.
- Disguised forms: no anonymous intermediate factor, no 0/1 multiplier, no dropped base branch found. The `replaced_by` texts of self_pay_refund and home_unit_purchase are the policies' baselines, and the rules then refine them by factor ladders; the two places where the baseline wording is categorical are listed as observation O1 with per-task numbers in the task files.

Result: no undeclared override with a scored consequence. **PASS** (observations O1, O8).

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tier | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| return_labor | keep_time_units | parameter | keep_units | 3 | no | — |
| | humidifier_care_units | parameter | humid_units | 3 | yes (holding humidifier_included AND resupply humidifier_in_use) | resupply |
| | setup_route_units | parameter | route_units | 3 | no | — |
| | warranty_rework_protocol | method | booked_units | 3 | no | — |
| return_parts | chamber_part_price | parameter | chamber_part | 3 | yes (holding + resupply) | resupply |
| | outlet_part_price | parameter | outlet_part | 3 | tier 2 two fields of one row | resupply |
| | airpath_kit_price | parameter | airpath_part | 3 | no | — |
| | airpath_clock_anchor | method | airpath_days | 3 | yes (repair row; delivery row + sale line) | — |
| used_accessories | mask_style_value | parameter | mask_value | 3 | no | resupply |
| | air_path_set_value | parameter | tubing_value | 3 | two fields of one row | resupply |
| | hygiene_charge_basis | method | borne_value | 3 | yes (resupply status AND request/holding dates) | resupply |
| | travel_packaging_value | parameter | packaging | 3 | no | — |
| self_pay_refund | wear_proration | method | worn_value | 3 | no | — |
| | restock_rate_tier | parameter | restock_pct | 3 | no | — |
| | restock_loyalty_cap | parameter | restock_cap | 3 | resupply status AND enrollment_date (one row) | resupply |
| | accessory_withholding | parameter | withheld_value | 3 | no | — |
| | handling_charge_tier | parameter | handling_charge | 3 | no | — |
| | delivery_fee_credit | parameter | fee_credit | 3 | yes (repair row AND delivery row) | — |
| usage_nights | serial_window_scope | method | counted_nights | 3 | yes (loaner row AND no swap row) | — |
| | swap_night_credit | parameter | swap_credit | 3 | swap row only | — |
| | acclimation_night_credit | parameter | acclim_credit | 3 | delivery row + download rows | — |
| | pressure_night_credit | parameter | pressure_credit | 3 | no | — |
| usage_hours | serial_hours_scope | method | averaged_hours | 3 | yes | — |
| | swap_time_addback | parameter | swap_hours | 3 | swap row only | — |
| | pressure_time_addback | parameter | pressure_hours | 3 | no | — |
| | first_unit_time_addback | parameter | first_hours | 3 | delivery row + download rows | — |
| home_unit_purchase | list_price_basis | parameter | list_price | 3 declared, **2 effective** (G2) | no | coverage |
| | hours_wear_basis | method | worn_price | 3 | no | — |
| | failed_trial_discount | parameter | failed_pct | 3 | yes (summary row AND holding setup_date vs class trial) | — |
| | repair_history_discount | parameter | repair_pct | 3 | no | — |
| | humidifier_bundle_value | parameter | humid_value | 3 | yes (holding + resupply) | resupply |

- Counts: return_labor 4 (3p/1m), return_parts 4 (3p/1m), used_accessories 4 (3p/1m), self_pay_refund 6 (5p/1m), usage_nights 4 (3p/1m), usage_hours 4 (3p/1m), home_unit_purchase 5 (4p/1m). All within 4-6 with >=2 parameter and >=1 method as declared.
- Per task (inferred scopes): task 0 has multi-source (humidifier_care_units, chamber_part_price, delivery_fee_credit, ...) and cross_difficulty resupply factors; task 1 has multi-source (humidifier_bundle_value, failed_trial_discount) and cross_difficulty factors (coverage, resupply) — only in home_unit_purchase; usage_nights and usage_hours read no other difficulty.
- Bindings disjoint within each policy; every `decides` is an input, never `result`.
- Every tier of every ladder is stated in the rule with its condition and value/method and implemented in `compute`; every fall-through equals the factor's `baseline`, and every `baseline` equals what `baseline.rule` gives for that input (checked per factor: 0 for the additive units/parts/credits; `sale_price`, class percentage, uncapped, 104.00, `kit_value`, `all_nights`, `all_hours/all_windows`, `list_price`, self-pay retail price, `subtotal`, `DAYS(setup_date, recv_date)`).
- Labels: method factors change the algorithm (window scope, floor-at-10 / add-a-job, anchor date, proration rule, wear basis, capped daily charge); parameter factors substitute numbers. Honest.
- Ladder reality — defects: G2 (list_price_basis tier 1 ≡ tier 2), G3 (wear_proration non-monotonic). Near-degenerate: O2 (hygiene_charge_basis tier 1 = tier 3 everywhere but one cell).

### findings

**G1 — SOURCE-POLICY RED (check 6: prerequisite sentence broader than its condition, contradicting the same rule).** Bears on task 1.
- Symptom: the usage_hours edge's sentence states that no wear at all is taken before a usage summary exists, while the same rule takes per-window wear without one.
- Evidence: home_unit_purchase rule, sentence A (edge `policy_source`): "No wear is taken off the in-home unit's price until a usage summary on the device record states the average daily use." Sentence B (same rule): "with only scored compliance windows on the record, the list price is reduced by 2 percent for each window". The edge's own `effect`: "the worn price moves from the per-window wear to the therapy-hours wear computed from the summary's average daily use" — i.e. the `condition`/`effect` describe a change of wear basis, the sentence describes the absence of wear.
- Demonstrated consequence: on a device record carrying scored windows and no summary (task 1's opening world: three `not_met` windows), sentence A gives worn price = list price, sentence B gives list price x (1 - 0.02 x 3). The task file gives the figures. The gold write is evaluated after the summary exists, where both readings select the hours tier, so the scored sale amount does not move. The defect is in the stated dependency and in the opening-world contrast.
- Root cause / location: `pap.extended.yaml` pap_ext_home_unit_purchase `rule` and `prerequisite[1].policy_source`.

**G2 — SOURCE-FACTOR RED (unreal ladder: two tiers select the same value).** Bears on task 1.
- Evidence: list_price_basis tier 1 "the device record's coverage is an active Original Medicare Part B record -> the class's fee-schedule purchase amount"; tier 2 "another active coverage record -> the fee-schedule purchase amount times the payer class's contracted percentage". `blueprint/products/coverage.yaml` lines 89-103: "Original Medicare Part B" `payer_type: "medicare_ffs"`, `allowed_pct_of_fee_schedule: 100`. So for every record that meets tier 1's condition, tier 2's method gives FSP x 100 / 100 = FSP — the same value. The Original-Medicare tier never changes a number relative to the general active-coverage tier; the ladder has two effective tiers (active coverage -> FSP x pct; otherwise -> retail), below the floor of three.
- Demonstrated consequence: on task 1's world (Original Medicare Part B, FSP 862.40) tier 1 = 862.40 and tier 2's formula = 862.40; an agent that misclassifies the payer as "another active coverage" scores the same. Count consequence in the task file.
- Location: pap_ext_home_unit_purchase `factors[list_price_basis]`, `rule` ("when that coverage is an active Original Medicare Part B record the list price is the class's fee-schedule purchase amount; when it is another active coverage record ...").

**G3 — SOURCE-FACTOR RED (unreal ladder: a tier's outcome no business would publish).** Bears on task 0.
- Evidence: wear_proration: ">21 days -> price x (1 - days / (RUL months x 30))"; ">14 and <=21 days -> price less 0.4 % per day beyond 14". With RUL 60 months (every class), day 21 refunds 97.2 % of the price and day 22 refunds 1 - 22/1800 = 98.78 %. On the Auto-Adjusting CPAP price 899.00: 21 days -> 873.83, 22 days -> 888.01. Keeping the unit one day longer raises the refundable value by 14.18 USD, and every day from 22 to 30 refunds more than day 21 (day 30: 884.02). No retailer publishes a wear schedule in which the refund rises with time kept.
- Demonstrated consequence: the ladder's top tier is not a real treatment; struck, wear_proration is not a real three-tier factor, and it is self_pay_refund's only `method` factor. Count consequence in the task 0 file.
- Location: pap_ext_self_pay_refund `rule` (the "refundable value of the unit depends on those days" sentence) and `factors[wear_proration]`.

**Observations (no demonstrated consequence on a scored value; not grounds for rework on their own):**
- O1 Categorical baseline wording versus a factor tier: self_pay_refund says "the delivery fee is not refunded" (also in its `replaced_by`) and then adds "plus the delivery fee credit" into the refund; home_unit_purchase says an in-home unit "carries no delivery fee and no humidifier charge" (also in its `replaced_by`) and then adds 79.00 / 39.50 USD for the humidifier. Read as baseline plus a more specific tier, each has one reading. The per-task figures for the literal reading are in the task files.
- O2 hygiene_charge_basis: min(kit, 12 x days) with days >= 15 equals the kit value (the fall-through) for every mask/tubing combination except full face + heated set (kit 192.00) kept exactly 15 days (180.00). The tier differs from the fall-through only in that one cell.
- O3 `RND` is ties-to-even on binary floats; rules say half up. No tie in either world.
- O4 usage_nights / usage_hours aggregate all `pap_compliance_download` rows, including earlier summaries; rule says "30-night compliance windows". No earlier summary is seeded.
- O5 refund `enroll_months` reads the first resupply row of any status. One resupply row in task 0.
- O6 return_parts outlet binding requires an active enrollment; the rule's outlet sentence does not say "active" (the neighbouring chamber sentence does).
- O7 Tree depth versus actions: the refund tree's three prerequisite problems are resolved by one agent call, and the purchase tree's two by one agent call.
- O8 Base pap_repair_responsibility's warranty sentence and its "a device the patient still has" lead-in are not superseded for the return inspection. No computed argument depends on them (the tool hard-codes `repair_coverage none`).
- O9 After the in-home purchase the coverage-billed record keeps its status and coverage_id. The charter does not say what happens to rental billing or title. No tool or gold-relevant write is implied.
- O10 usage_nights `baseline.params: [window_nights]` names a key the baseline expression does not use. usage_hours `baseline.params: []`.
- O11 The refund tool leaves `fee_amount` (restocking fee withheld) unset on the refund line.

## closing_checklist

(Written after all tasks were revealed and compared; see below.)

### closing status (written after both reveals; nothing above this line was changed)

The difficulty is **not closed**: not all four relationships PASS for every task.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **SOURCE-FACTOR RED** (G3: refund has no real method factor) | PASS |
| 1 | **SOURCE-POLICY RED** (G1) | PASS | **SOURCE-FACTOR RED** (G2 + failed_trial_discount stamp; sale computation 3 surviving factors) | PASS |

Checklist state:
- Per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and this file sits alongside them. First revision.
- Coverage and scopes: `charter_scope` task 0 = {return_labor, return_parts, used_accessories, self_pay_refund} with {record_return_inspection, return_device_for_refund}; task 1 = {usage_nights, usage_hours, home_unit_purchase} with {record_usage_download, purchase_home_device}. These are pairwise disjoint and cover all seven extended policies and four tools, and match the pre-reveal inference.
- Trees: task 0 has n=3 with 3 value_input edges; task 1 has n=2 with 2. Each has one owner=user root write. Acyclic, and the whole-difficulty graph is acyclic.
- Factors: all 31 declared factors bear weight on their task world against honest baselines, and every all-baseline fall-back is definite and differs from gold (task 0: 2 / 7.50 / 104.00 / 660.15; task 1: 51 / 4.0 / 899.00). The ladder-reality and stamp findings above stand.
- Gate re-run on the final form: not performed by this audit. Step 0 assigns gates to the coordinator, and the final form is pending rework of G1/G2/G3 and the task 1 stamp.

## revision_2

### charter_global_frozen (revision 2)
- Frozen 2026-10-12 20:31 UTC (auditor clock), before any revision-2 task GT was read. Same auditor and same masking division as round 1.
- Hashes:
  - `pap.extended.yaml` sha256=9709c9dbe0117fe749caa64e6adde475c53d52b828ba13e4639467b95bb17b4b (changed from ccc18b4c…, so every charter-global section below is re-derived in full).
  - `task_tools.py` sha256=66ce95e6…da0d (unchanged; `action_binding_and_uuids` carried forward by reference on that hash).
  - Views: 0.view.json 9481bf5d… (persona changed; initial_state row counts unchanged), 1.view.json 16a9e4fd… (unchanged).
- Base copy: lines 1-1296 still byte-identical to `blueprint/products/pap.yaml`.
- Scripted checks on the new charter: every `policy_source` is verbatim in its rule; every `baseline.rule` sentence is in its rule; every `compute_basis` quotation is in its rule. No miss.
- Entry gates: supplied by the coordinator (all green; traceability misses only the four unlock tool names). Input complete.

### policy_conflict_scan (r2)
The table of round 1 still holds: same seven policies, same subjects, computes, target tools and edges. Scopes are unchanged in shape. New cross-policy content:
- home_unit_purchase adds "The sale ends the coverage rental: no rental month is billed on the device record once it carries the patient's self-pay sale." This narrows base pap_evt_rental_billing ("A rental month is billed only while the device record is trial_active or rental_active") for a sold unit. No overwrite names that policy. No write of this difficulty bills a rental month, so no scored quantity moves. Recorded as observation N2.
- home_unit_purchase now prices an active-coverage unit at the class's `unreturned_equipment_charge`, a parameter base pap_return_pickup uses as a charge for an unrecovered device. This reuses the value, not a conflict, because the base sentence governs a different event.

### rule_compute_equivalence (r2)
Re-swept all seven policies. Changes since round 1, each checked in both directions:
- return_labor warranty method: ">=2 jobs → sum + labor of all those jobs + 2 protocol units; exactly one → sum + max(1, that job's units); none → sum". Matches compute (`warranty_total_units`, `MX(K('min_job_units'), …)`). Python precedence puts the whole `subtotal + … + K('protocol_units')` in the true branch, as the rule says. PASS.
- return_parts outlet: "a patient whose active enrollment records heated tubing" now matches `status='active'`. **O6 closed.**
- used_accessories borne value: enrolled and kept >14 → mask + tubing × days / 90. Matches compute. PASS.
- self_pay_refund wear: >21 → 0.4 % × 7 + 0.8 % × (days − 21); 15-21 → 0.4 % × (days − 14). Matches. PASS.
- self_pay_refund restock: standard + 5 / + 2.5 / + 0 points. Matches. PASS.
- self_pay_refund enrollment tenure reads the active enrollment only. **O5 closed.**
- self_pay_refund withholding — **new defect N1, see findings.** The rule's three tiers are each conditioned on what "the return inspection on the device record shows" (above 104.00 → recorded; "no used-accessory amount at all … sealed" → 0; above zero up to 104.00 → 104.00). The baseline sentence is "less the standard accessory kit of 104.00 USD". The compute is `withheld_value: share_recorded if share_recorded > 104 else (0 if share_recorded == 0 else 104)`, with `share_recorded = MAX(... repair_coverage='none')`, which returns 0.0 when no inspection exists. A record with no inspection therefore takes the "sealed" branch (0), a case no rule tier states. The rule (fall-through and baseline) gives 104.00.
- usage_nights / usage_hours aggregate only `met` / `not_met` windows, so an earlier summary is excluded, as "the 30-night compliance windows" says. **O4 closed.**
- home_unit_purchase:
  - List price: active coverage → `unreturned_equipment_charge`; terminated → RND((charge + retail) / 2); else retail.
  - Wear: ≥4.5 h → hours × days / 20000; 2.0–4.5 h → credited nights × 4 / 20000; <2.0 h or no summary → none.
  - Trial discount: 15 / 8 / 4 / 0 at <40, 40–49, 50–62 nights once the trial period has passed.
  - Repair discount: every job on the record, including those on a swapped-out unit.
  - All match the compute. PASS.
- O3 (`RND` ties-to-even versus "half up") is unchanged and left open by the reworker. No tie arises in either revision-2 world (checked: 895.40×0.20, 725.88×0.87 = 631.5156, 750×0.96784 = 725.88).

### action_binding_and_uuids (r2)
Carried forward by reference: `task_tools.py` hash unchanged (66ce95e6…), and the `(target_tool, computes)` pairs are unchanged in the charter. PASS. O11 (refund line leaves `fee_amount` unset) remains open, as declared by the reworker.

### prerequisite_graph (r2)
Same five edges, kinds, gates, forms and resolving tools. All gate bindings still exist. Acyclic.
- The purchase←usage_hours `effect` now reads "the worn price moves from the unworn list price to the wear the summary's average daily use selects", which agrees with its sentence and with the compute (no summary → `summary_hours` 0 → no wear).
- The refund←used_accessories `effect` reads "a sealed return withholds nothing, and any other amount withholds the standard kit". This is accurate after the inspection. Before it, the compute does not follow the "any other amount withholds the standard kit" wording (N1).
- PASS for the graph itself.

### prerequisite_sentences (r2)
- The five sentences are verbatim unchanged.
- The usage_hours sentence "No wear is taken off the in-home unit's price until a usage summary on the device record states the average daily use." no longer contradicts the rule: the per-window wear tier is gone, and with no summary the ladder takes no wear. **G1 closed.**
- Unique resolving writes are unchanged. No second wording, no tool name and no base-grounded edge.
- PASS.

### override_declarations (r2)
- used_accessories now also supersedes the base warranty sentence ("A patient-owned device within `manufacturer_warranty_months` … repaired under the manufacturer warranty at no charge …") with the stock-reconditioning `replaced_by`. The base lead-in "A repair is recorded only on a device the patient still has" is still unsuperseded, but its operative status list is met (patient_owned) and nothing computed depends on it. **O8: warranty half closed; the lead-in half remains an observation with no consequence.**
- self_pay_refund `replaced_by` and rule now say "the standard refund does not include the delivery fee". With that wording the delivery-fee credit tier reads as an exception to the standard refund rather than against a categorical "not refunded". **O1 (refund half) closed.**
- home_unit_purchase `replaced_by` and baseline drop "no humidifier charge". **O1 (purchase half) closed.**
- New narrowing of base rental billing (N2), undeclared, with no scored consequence (observation).
- PASS with observation N2.

### factor_ladders (r2)
Counts unchanged:
- return_labor 4 (3p/1m), return_parts 4 (3p/1m), used_accessories 4 (3p/1m), self_pay_refund 6 (5p/1m), usage_nights 4 (3p/1m), usage_hours 4 (3p/1m), home_unit_purchase 5 (4p/1m).
- Bindings disjoint; fall-throughs equal baselines.

Ladder reality, re-judged:
- **G3 closed.** wear_proration is now monotone: day 21 → 97.2 %, day 22 → 96.4 %, day 30 → 90.0 % of price. This is a published-style two-rate schedule.
- **restock_rate_tier (same class).** Tiers are now standard + 5, standard + 2.5 and standard. They are distinct for every class, including E0471, whose standard 20 % previously coincided with the old flat 20 % tier.
- **warranty_rework_protocol (same class).** The old "max(sum, 10)" tier could book fewer units for two warranty jobs than for one. It is now "sum + all jobs + 2", which is monotone and distinct from the one-job tier.
- **G2 closed.** list_price_basis tiers are now unreturned-equipment charge / midpoint of that charge and retail / retail. For every class these are three distinct values (e.g. Auto CPAP 750.00 / 824.50 / 899.00). Each tier reads the coverage record's status, a cross-category value. The terminated-coverage midpoint is a constructed price but a plausible published buy-out figure, so it is not raised.
- **O2 closed.** hygiene_charge_basis "mask + tubing × days / 90" for 15-30 days is always strictly between the mask-only tier and the full kit, never equal to either.
- failed_trial_discount now has four tiers, all conditioned on the trial having passed and banded by credited nights (<40 / 40–49 / 50–62 / else). Distinct values. The stamp question is per-task (task 1 file).
- hours_wear_basis: three distinct methods keyed on summary hours.
- PASS for structure.

### findings (r2)

**N1 — SOURCE-POLICY RED (check 2: compute branch the rule does not state).**
- Location: `pap.extended.yaml` pap_ext_self_pay_refund `compute.withheld_value` against its `rule` / `baseline.rule` / `factors[accessory_withholding]`.
- Symptom: with no return inspection on the record, the compute withholds 0.00 ("sealed") while the rule withholds the standard kit.
- Evidence:
  - Rule: "when the return inspection on the device record shows a used-accessory amount above the standard accessory kit of 104.00 USD that amount is withheld, when it shows no used-accessory amount at all the accessories came back sealed and nothing is withheld, and when it shows an amount above zero up to the standard kit the standard kit is withheld".
  - Baseline: "less the standard accessory kit of 104.00 USD for the used mask and tubing".
  - Compute: `share_recorded = MAX('pap_service','repair_patient_share', …, repair_coverage='none')`, which is 0.0 with no row, then `0 if share_recorded == 0`.
  - The round-1 tier "when no inspection is on the record the standard accessory kit is withheld" was removed from both faces, but the compute's zero test still captures the no-inspection world.
- Demonstrated consequence: on task 0's opening world the compute gives a refund of 810.09 and the rule gives 706.09 (the task file has the arithmetic). The scored refund is evaluated after the inspection (share 146.00 > 104.00), where both give 638.40, so the scored value does not move. The defect sits in the opening-world contrast and in any proof text that cites the skip figure.
- Bears on task 0.

**Observations (r2):**
- N2: the undeclared narrowing of base rental billing by the sale.
- O3, O7 and O11: open, as the reworker declared.
- O8: the lead-in half remains.
- The terminated-coverage midpoint price is constructed (not raised).

Round-1 items verified closed against the artifacts: G1, G2, G3 (plus the restocking and labor ladders of the same class), O1, O2, O4, O5, O6, O10 (`baseline.params` of usage_nights/hours now `[]`, matching their constant-free baselines), and O9 in its billing half (status after the buy-out is still unstated, with no consequence).

### closing status (r2, written after the r2 reveals; nothing above in revision_2 was changed after them)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (N1; scored 638.40 unaffected) | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Round-1 REDs: G1, G2, G3 (plus the restocking and labor ladders of the same class), task-0 finding 1 and task-1 findings 1–3 are all verified closed.
- Round-1 observations: O1, O2, O4, O5, O6 and O10 closed; O8 warranty half closed (lead-in half remains, no consequence); O9 billing half addressed; the repair-count and persona observations closed. O3, O7 and O11 open, as declared.
- New in r2: N1 (SOURCE-POLICY RED, task 0) and N2 (observation).
- Regression check: every round-1 PASS item was re-derived on the r2 artifacts (scopes, trees, edges, verbatim sentences, single resolving writes, uuid8s, tool bodies) and still holds.
- The difficulty is **not closed** while N1 stands. The gate re-run on the final form remains with the coordinator.

## revision_3

### entry (r3)
- Gates (auditor ran `bash /tmp/erl0057_coord/gates.sh pap_therapy_rentals` read-only, 2026-10-12):
  - check_extended rc=0 :: EXTENDED OK
  - check_task_tools rc=0 :: TASK TOOL CONTRACT OK
  - replay_tasks rc=0 :: REPLAY OK
  - check_solvability rc=0 :: SOLVABILITY OK
  - check_compute rc=0 :: COMPUTE OK
  - check_grounding rc=0 :: GROUNDING OK
  - check_cache_diff rc=0 :: CACHE-DIFF INFO (optional; no correctness gate)
  - check_cross_fire rc=0 :: SCOPE OK
  - All 8 lines are OK/INFO, so the audit proceeds.
- Views rebuilt mechanically with `/tmp/erl0057_coord/make_views.py pap_therapy_rentals`:
  - 0.view.json sha256=9481bf5d088caa949c867730c7da8261b85c503d719ee2a8228c62b996977ec0 (same as r2)
  - 1.view.json sha256=16a9e4fd270f0a8def621a8aa3fd1eaaddd0dc603eeb2a422bc1070b2469842d (same as r2)
  - pap.extended.yaml sha256=de631907ba552db11b646a22bc1a89ee5eb8ff05abc70cd88990d7a5c8cfef5a (changed from 9709c9db…)
  - task_tools.py sha256=66ce95e647b6c3fbdc6ffb27f319cb6955936e65a68d68184f7f13b6c594da0d (unchanged)
- Charter-global sections re-derived because the charter hash moved. `action_binding_and_uuids` is carried forward on the unchanged tool hash.
- Frozen 2026-10-12 21:08 UTC (auditor clock), before any r3 task GT was read.

### charter-global re-derivation (r3)
Scripted over the r3 charter:
- base lines 1-1296 byte-identical to `blueprint/products/pap.yaml`;
- every `policy_source` verbatim in its rule;
- every `baseline.rule` sentence and every `compute_basis` quotation in its rule;
- every `overwrite.superseded_clause` verbatim in the named base policy's rule, and every `replaced_by` present in the extended rule.

Factor structure unchanged: 4/4/4/6/4/4/5 factors, ≥2 parameter and 1 method each, ladders ≥3 tiers. Prerequisite graph unchanged (five value_input state-form edges, acyclic).

What changed, each checked in both directions:
- **N1 (refund withholding).**
  - Rule now: "… when it shows no used-accessory amount at all the accessories came back sealed and nothing is withheld, and in any other case, an amount above zero up to the standard kit or no used-accessory amount recorded on the device record, the standard kit is withheld as the minimum charge for opened accessories."
  - Compute now: `withheld_value: share_recorded if share_recorded > 104 else (0 if (inspections >= 1 and share_recorded == 0) else 104)`, with `inspections = COUNT(pap_repair, repair_coverage none)`.
  - The ladder's fall-through now names "no used-accessory amount recorded on the device record", and the edge `effect` says "a sealed return (an inspection recording no amount) withholds nothing, and any other amount, or no amount recorded, withholds the standard kit".
  - The no-inspection world now takes 104.00 in both faces. **N1 closed.**
  - Wording note (observation only): "no used-accessory amount at all" (sealed tier, conditioned on "it", the inspection, showing it) and "no used-accessory amount recorded on the device record" (fall-through) are close in wording but separated by their subjects and by the ladder's parentheticals.
- **N2 / O9 (rental billing and status after the buy-out).**
  - home_unit_purchase now lists `pap_evt_rental_billing` in `base_policy_refs` and declares an overwrite superseding "A rental month is billed only while the device record is trial_active or rental_active." with "… and carries no self-pay sale of the unit."
  - The rule adds "the self-pay sale line is the patient's record of owning the unit, the device record keeps its status and coverage as they stand".
  - The narrowing is declared and the post-sale status is stated. **N2 closed; O9 closed.**
  - No write of this difficulty bills a rental month, and `purchase_home_device_8c1f8216` changes no status, consistent with "keeps its status and coverage".
- **O8 remainder.**
  - used_accessories adds a third overwrite superseding "A repair is recorded only on a device the patient still has: the device record is trial_active, rental_active, suspended or patient_owned." (verbatim). The replacement is "A return inspection is recorded on the device record of a self-pay unit that has come back to Summit Ridge while that record is patient_owned; it is not a repair of a device the patient still has." That replacement is carried into the rule.
  - The base `device_with_patient` state contract (allowed statuses include patient_owned) is not contradicted.
  - **O8 closed.**
- New content scanned for new defects:
  - The new used_accessories sentence adds a record-state condition (patient_owned) on the inspection. It states no cross-problem order and grounds no undeclared edge.
  - The new billing sentence states no order between problems of this difficulty.
  - Neither introduces a compute branch or a tier.
  - No new defect found.
- Still open (unchanged, declared open): O3 (`RND` ties-to-even; no tie in either world), O7 (one call per prerequisite set), O11 (refund line `fee_amount` unset).

### closing status (r3, written after the r3 reveals; nothing above in revision_3 was changed after them)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Closing checklist:
- Files: `0.md` and `1.md` correspond one-to-one with the tasks, alongside this file. Revisions 1-3 are appended and the older text is untouched. Every r3 comparison section carries PASS.
- Coverage and scopes: `charter_scope` task 0 = {return_labor, return_parts, used_accessories, self_pay_refund}; task 1 = {usage_nights, usage_hours, home_unit_purchase}. Pairwise disjoint, covering all seven extended policies and the four task tools. GT is closed over the tools. uuid8s bc7317cd / b6f98fe9 / 48c54aed / 8c1f8216 are independent.
- Trees: task 0 has 3 prerequisite problems with 3 value_input edges; task 1 has 2 with 2. Each has one owner=user root write. Both are acyclic, and the difficulty-wide graph is acyclic.
- Factors:
  - 31 factors, 4-6 per computation, ≥2 parameter and ≥1 method each; ladders ≥3 distinct tiers, all stated in the rules.
  - Every factor bears weight on its task world against an honest baseline.
  - Baseline-only fall-backs are definite and differ from gold (task 0: 2 / 7.50 / 104.00 / 660.15; task 1: 51 / 4.0 / 899.00).
  - Each task has a multi-source factor and a cross-difficulty factor (task 0: resupply; task 1: coverage and resupply).
- Gates on the final form: re-run by this auditor at the start of r3 (8/8 OK/INFO, lines above). The charter and task files read in r3 are the ones gated.
- Open observations (no red): O3 (`RND` ties-to-even vs "half up"; no tie arises in either gold world), O7 (one call resolves each prerequisite set), O11 (refund line leaves `fee_amount` unset).
- **The difficulty passes the source-layer audit as of revision 3.**

## revision_4

### entry (r4)
- Gates (auditor ran `bash /tmp/erl0057_coord/gates.sh pap_therapy_rentals` read-only, 2026-10-13 05:50 UTC):
  - check_extended rc=0 :: EXTENDED OK
  - check_task_tools rc=0 :: TASK TOOL CONTRACT OK
  - replay_tasks rc=0 :: REPLAY OK
  - check_solvability rc=0 :: SOLVABILITY OK
  - check_compute rc=0 :: COMPUTE OK
  - check_grounding rc=0 :: GROUNDING OK
  - check_cache_diff rc=0 :: CACHE-DIFF INFO (optional; no correctness gate)
  - check_cross_fire rc=0 :: SCOPE OK
  - All 8 lines are OK/INFO.
- Views rebuilt with `make_views.py`:
  - 0.view.json 9481bf5d…7ec0 (unchanged)
  - 1.view.json 16a9e4fd…842d (unchanged)
  - pap.extended.yaml sha256=b0befc006c3c88b50e6e444a112047989a709b01aacde3a3419b0207250293f3 (changed)
  - task_tools.py sha256=42f1d8b0a7499761d4d8607e6dcdba27d99c023df50f63b94c479d5a327e9d8d (changed)
- Both shared inputs moved, so every charter-global section is re-derived.
- Input also read: the renderer's `audits/render_source/pap_therapy_rentals/render_r1_source_mismatches.md`, supplied by the coordinator. It contains charter quotations only, no task GT.
- Frozen 2026-10-13 05:53 UTC (auditor clock), before any r4 task GT was read.

### Relation to previous revisions (disclosure)
Render items 1 and 2(a)–(e) existed in the charter during r1–r3. This audit's `override_declarations` in r1–r3 checked each overwrite against the task's quantity but did not test whether a superseded clause's reach exceeded its replacement. Its `factor_ladders` did not test whether a factor's tier rested on another factor's output. Those were misses of this audit, not defects introduced later. Item 4 (card wording) and the docstring point N3 below were also present and missed.

### render-found items — verification (r4)
- **Item 1 (return_parts airpath kit tiered on a value decided by another factor).**
  - `airpath_kit_price` is gone. `airpath_clock_anchor` (method) now `decides: airpath_part` and owns `airpath_days` and `airpath_part`.
  - Its fall-through baseline is the kit chosen on the delivery-date count, which the new baseline sentence states: "Reconditioning parts start from the filter set …, and the internal air-path kit, chosen by the days from the delivery date … more than 14 days takes the full air-path kit at 18.00 USD, more than 7 and up to 14 days takes the half kit at 9.00 USD, and 7 days or less takes none."
  - A new parameter factor, `case_seal_part` (7.00 / 3.50 / 0 by count of warranty repairs, "A unit whose case was opened for warranty work takes new tamper seals and case screws"), keeps the count at 4 (3p/1m). Its ladder has distinct values, is stated in the rule, and is a plausible reconditioning charge.
  - Scripted scan: no factor binding of return_parts reads another factor's binding. **Closed.**
- **Item 2(a)–(c) (used_accessories overwrites).** Each superseded clause is verbatim in base pap_repair_responsibility, and each replacement is now scoped "for a self-pay device sent back for a refund, and only for such a device", re-affirming the base clause for every other device:
  - (a) warranty: "every other patient-owned device within the manufacturer warranty period remains repaired under the manufacturer warranty at no charge, except water and drop damage".
  - (b) patient_paid: "every other owned self-pay device that is outside the manufacturer warranty, or has water or drop damage, remains repaired at the patient's cost".
  - (c) "A repair is recorded only on a device the patient still has" (the superseded clause now stops before the status list): "every other repair remains recorded only on a device the patient still has". The status list and the `device_with_patient` eligibility (allowed statuses including patient_owned) stay in force and are not contradicted. The return inspection is recorded "while that record is patient_owned".
  - Each overwrite now reaches exactly what its replacement governs, and none contradicts an in-force base sentence. **Closed.**
- **Item 2(d) (usage_nights / usage_hours).**
  - Both replacements are scoped to "a usage summary download … and only for such a download" and add "every other compliance download remains a scored window of the class's compliance window nights, as the base trial-compliance rule states".
  - Base conversion ("converted only when a pap_compliance_download … shows compliance_result met") is untouched and still served by scored windows. **Closed.**
- **Item 2(e) (home_unit_purchase vs base retail + delivery fee).**
  - The replacement is scoped to "a unit bought outright where it already stands in the patient's home on a coverage-billed device record … and only for such a unit".
  - It adds "every other outright purchase remains at the class's self-pay retail price plus its self-pay delivery fee, paid in full when the order is placed, as the base self-pay rule states".
  - `self_pay_delivery_fee` is charged again in an in-force rule, and the base "the Travel CPAP System (E0601) is sold only this way" again points at an in-force clause.
  - The refund overwrite's reach (all self-pay refunds) equals the refund policy's subject (pap_purchase_refund), so it is not over-wide.
  - **Closed.**
- **Item 3 (usage swap credits read the scope factor's `swaps`).** `swap_night_credit` / `swap_time_addback` now read their own binding `swap_jobs`. **Closed.**
- **Item 4 (card wording in user-tool docstrings).** "card" no longer appears in task_tools.py. Signatures, owners, uuid8 names and function bodies are unchanged: no checks, same `ctx.create` fields, purchase `fee_amount=0.0`. **Closed.**

### charter-global re-derivation (r4)
Scripted over the r4 charter:
- base lines 1-1296 byte-identical;
- every `policy_source` verbatim in its own rule;
- every `baseline.rule` sentence and `compute_basis` quotation in its rule;
- every `superseded_clause` verbatim in its base policy;
- every `replaced_by` carried in its extended rule. The three apparent misses were artefacts of YAML line-folding inside `replaced_by` ("trial- compliance", "coverage- billed", "self- pay"); the rules carry the hyphenated words intact. Cosmetic observation O12.

Structure:
- Factor counts 4/4/4/6/4/4/5, each with ≥2 parameter and 1 method; every ladder has ≥3 distinct tiers stated in the rule.
- Prerequisite graph unchanged (five value_input state-form edges, acyclic).
- uuid8s unchanged and independent.

Factor dependency scan:
- Three method factors combine other factors' values in their formula:
  - used_accessories `hygiene_charge_basis` ("the mask value plus the tubing value prorated …");
  - home_unit_purchase `hours_wear_basis` (wear on the list price);
  - the parts sum.
- In each, the tier conditions rest on records (enrolment and days kept; summary hours), not on another factor's output. Each formula's inputs have stated baseline defaults (nasal mask 89.00, standard tubing 15.00, retail list price), so each document is computable alone.
- This is composition, not the render-item-1 shape. Recorded as observation O13.

### findings (r4)
**N3 — SOURCE-POLICY RED (check 3: tool docstring admits a second reading that contradicts the rule).** Pre-existing since r1; missed by r1–r3.
- `return_device_for_refund_b6f98fe9` docstring: "One call books one refund line against the sale being refunded: the amount refunded to the patient and the date the returned unit was received. The device price is the only amount refunded through this line."
- self_pay_refund rule: "A unit that failed early is credited the delivery fee charged on its sale line … The refund is the refundable value, less the restocking fee after any cap, less the used-accessory withholding, less the handling charge, plus the delivery fee credit".
- For a record on the credit tier, the rule puts the delivery-fee credit into the one refund amount. The docstring says only the device price is refunded through this line, so the credit would be left out of `refund_amount`.
- Demonstrated in task 0 (credit tier taken): 638.40 (rule) vs 589.40 (docstring reading).
- Location: `task_tools.py` return_device_for_refund_b6f98fe9 docstring, against pap_ext_self_pay_refund `rule`.

**Observations (r4):**
- O12: folded-line hyphen artefacts in three `replaced_by` fields.
- O13: method factors compose other factors' values; tier conditions are record-based.
- O3, O7: open as before.
- O11: the refund line still leaves `fee_amount` unset.

### closing status (r4, written after the r4 reveals; nothing above in revision_4 was changed after them)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED (N3)** | PASS | PASS | **SOURCE-TASK RED (via N3)** |
| 1 | PASS | PASS | PASS | PASS |

- Render-found items 1, 2(a)–(e), 3 and 4: verified closed against the charter and tools.
  - Every overwrite now reaches exactly its replacement's scope and re-affirms the base clause elsewhere.
  - No factor's tier rests on another factor's output.
- No regression: task 1 is identical to r3. Task 0's only moved figure is parts_amount 52.50 → 56.00, from the new tamper-seal factor; gold matches it and the refund is unchanged.
- New: N3 (pre-existing docstring contradiction, missed by r1–r3). Observations O12 and O13.
- Open: O3, O7, O11.
- The difficulty is **not closed** while N3 stands.

## revision_5

### entry (r5)
- Gates (auditor ran `bash /tmp/erl0057_coord/gates.sh pap_therapy_rentals` read-only, 2026-10-13 06:13 UTC):
  - check_extended rc=0 :: EXTENDED OK
  - check_task_tools rc=0 :: TASK TOOL CONTRACT OK
  - replay_tasks rc=0 :: REPLAY OK
  - check_solvability rc=0 :: SOLVABILITY OK
  - check_compute rc=0 :: COMPUTE OK
  - check_grounding rc=0 :: GROUNDING OK
  - check_cache_diff rc=0 :: CACHE-DIFF INFO (optional; no correctness gate)
  - check_cross_fire rc=0 :: SCOPE OK
  - All 8 lines are OK/INFO.
- Views rebuilt:
  - 0.view.json 9481bf5d088caa949c867730c7da8261b85c503d719ee2a8228c62b996977ec0 (unchanged)
  - 1.view.json 16a9e4fd270f0a8def621a8aa3fd1eaaddd0dc603eeb2a422bc1070b2469842d (unchanged)
  - pap.extended.yaml da9508805997734448655b6398f485ea2434ce5d2cc8812d765914833b41c765 (changed)
  - task_tools.py 2438a3e5f75df2902098731aa06de98e825d1549b0e53a121af47fc477c20b42 (changed)
- Every charter-global section re-derived.
- Frozen 2026-10-13 06:15 UTC (auditor clock), before any r5 task GT was read.

### N3 and the docstring sweep (r5)
Each of the four docstrings was read in full together with its function body. Every business statement in them was checked against the charter:
- **return_device_for_refund_b6f98fe9.** "The device price is the only amount refunded through this line" is gone. What remains is "books one refund line against the sale being refunded: the amount refunded to the patient and the date the returned unit was received". This states nothing the rule does not, and the refund amount carries the rule's full result, credit included. **N3 closed.**
- **record_return_inspection_bc7317cd.** "assessed and reconditioned for stock, not repaired for the patient, so the job carries no repair cost assignment" matches used_accessories' scoped replacement ("the return inspection assigns no repair cost"). The earlier extra claims ("no fault", "no loaner", "nothing is billed to any insurance", "0.00 when the patient bears none") are gone. The body still hard-codes `repair_fault/repair_coverage='none'` and `loaner_issued=False`; these are storage defaults, not stated business rules.
- **record_usage_download_48c54aed.** "a usage statement for the device, not a scored compliance window, so it carries no met or not-met result" matches the scoped usage overwrites. The serial and window arguments are format and lookup instructions only.
- **purchase_home_device_8c1f8216.** "paying the price in full" and "No delivery fee is charged because the unit is already in the home" match the scoped purchase replacement ("paid in full …, with no delivery fee"). The hcpcs mapping matches the charter's variant `hcpcs_code`s.
- No docstring states a sequence, names another tool, or carries an ordering word. No body checks a prerequisite. The uuid8 names are unchanged and independent.

### O12 (r5)
The `replaced_by` fields no longer carry folded-line hyphen artefacts (regex scan for "word- word": none). Every `replaced_by` is present verbatim in its extended rule (scripted). **O12 closed.**

### override sweep — corrected method, whole charter (r5)
For each overwrite, I compared the full reach of the superseded base clause (every record and event it governs, not only this difficulty's tasks) with the replacement's reach, and checked that whatever the clause governed outside the replacement is re-affirmed and that no in-force base sentence is contradicted.

| # | policy → base clause | base clause reach | replacement reach + re-affirmation | in-force base contradicted? |
| --- | --- | --- | --- | --- |
| 1 | used_accessories → "an owned self-pay device is repaired at the patient's cost (repair_coverage patient_paid)." | every owned self-pay device out of warranty or with water/drop damage | refund-return inspection only; "every other owned self-pay device that is outside the manufacturer warranty, or has water or drop damage, remains repaired at the patient's cost" | no — equal reach |
| 2 | used_accessories → warranty sentence ("A patient-owned device within `manufacturer_warranty_months` … except water_damage and drop_damage …") | every patient-owned device (self-pay or coverage-bought) within warranty | refund-return inspection only; "every other patient-owned device within the manufacturer warranty period remains repaired under the manufacturer warranty at no charge, except water and drop damage" | no — equal reach |
| 3 | used_accessories → "A repair is recorded only on a device the patient still has" (the clause stops before the status list) | every repair | refund-return inspection only, "while that record is patient_owned"; "every other repair remains recorded only on a device the patient still has" | no. The status list and the `device_with_patient` state contract (allowed statuses including patient_owned) stay in force and are met. |
| 4 | self_pay_refund → "The refund is the device price less …; the delivery fee and any mask or tubing that has been used are never refunded." | every self-pay refund | every self-pay refund (subject pap_purchase_refund; rule "A self-pay device returned complete in its original packaging within the class's return window is refunded …") | no — equal reach. Return window, refund-once and never-billed-to-coverage stay inherited. |
| 5 | usage_nights → "A compliance download scores one window of `compliance_window_days` consecutive nights" | every compliance download | usage summary only; "every other compliance download remains a scored window …" | no. The rest of the base sentence (met tests) and conversion ("converted only when … compliance_result met") still govern scored windows. |
| 6 | usage_hours → same clause | same | same scoping and re-affirmation | no |
| 7 | home_unit_purchase → "A rental month is billed only while the device record is trial_active or rental_active." | every rental month of every coverage-billed record | every rental month, with the added condition "and carries no self-pay sale of the unit". The added condition can only bind a coverage-billed record carrying an in-home sale, the case this policy creates, so the effective reach equals the policy's scope. | no. It is consistent with `billable_status` (still trial_active/rental_active) and with base pap_self_pay "A self-pay device is never billed to coverage afterward". |
| 8 | home_unit_purchase → "Any class may be bought outright … at `self_pay_retail_price` plus `self_pay_delivery_fee`, paid in full when the order is placed;" | every outright purchase | in-home unit on a coverage-billed record only; "every other outright purchase remains at the class's self-pay retail price plus its self-pay delivery fee …" | no. "the Travel CPAP System (E0601) is sold only this way" points at the re-affirmed clause. |

Policies with `overwrite: []` (return_labor, return_parts) re-checked sentence by sentence against pap_repair_responsibility's full reach:
- They compute labor and parts for the same inspection whose payer, recording and warranty treatment rows 1–3 already scope.
- Base "Otherwise an owned device bought under coverage is repaired with labor at `repair_labor_rate_per_unit` …" does not reach a self-pay return.
- The replace-instead-of-repair threshold and the loaner sentence govern repairs, which by row 3's replacement the inspection is not.
- No undeclared override.

The same full-reach reading surfaced one thing outside the overwrites:
- **O14 (observation).** The extended rules read "the date the completed return pickup request records the unit as received back" for a patient_owned self-pay unit.
- Base pap_return_pickup frames `return_pickup` requests for rented devices and says "A patient-owned device is never picked up or charged on return".
- No write of this difficulty creates a request or a pickup; the request is seeded history read only for its date, and task 0's unit was shipped back, not picked up. So no in-force sentence is contradicted by any write, and no scored value moves.

Result: every overwrite reaches exactly what its replacement governs, and none contradicts an in-force base sentence. **PASS.**

### other charter-global re-checks (r5)
- Scripted over the r5 charter:
  - base lines 1-1296 byte-identical;
  - every `policy_source` verbatim in its own rule;
  - every `baseline.rule` sentence and `compute_basis` quotation in its rule;
  - every `superseded_clause` verbatim in its base rule;
  - every factor's `decides` among its own bindings.
- Factor structure unchanged since r4 (counts 4/4/4/6/4/4/5; each ≥2 parameter and 1 method; ≥3 distinct tiers).
- Only the r4 composition reads remain: hygiene_charge_basis ← mask_value / tubing_value, and hours_wear_basis ← list_price. Their tier conditions are record-based (O13); no tier rests on another factor's output.
- Prerequisite graph unchanged (five value_input state-form edges, acyclic).

### findings (r5)
- N3 closed. O12 closed.
- No new red.
- Observations: O14 (new, no consequence); O13 (unchanged); O3, O7, O11 open as declared.

### closing status (r5, written after the r5 reveals; nothing above in revision_5 was changed after them)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Closing checklist:
- Files: `0.md` and `1.md` correspond one-to-one with the tasks; revisions 1–5 are appended with older text untouched, and every r5 comparison carries PASS.
- Scopes: task 0 = {return_labor, return_parts, used_accessories, self_pay_refund}; task 1 = {usage_nights, usage_hours, home_unit_purchase}. Disjoint and covering all seven extended policies and four tools. uuid8s are independent and unchanged.
- Trees: 3 and 2 prerequisite problems, all value_input, each with one owner=user root write. Acyclic, including the difficulty-wide graph.
- Factors:
  - 4–6 per computation, ≥2 parameter and ≥1 method; ladders of ≥3 distinct, real tiers stated in the rules.
  - Every factor bears weight; all-baseline fall-backs are definite and differ from gold.
  - Each task has a multi-source and a cross-difficulty factor.
- Overrides: the whole-charter full-reach sweep passes (8 overwrites, equal reach, no in-force base sentence contradicted).
- Docstrings: state nothing beyond the rules.
- Gates on the final form: 8/8 OK/INFO, re-run at the start of r5.
- Open observations (no red): O3, O7, O11, O13, O14.
- **The difficulty passes the source-layer audit as of revision 5.**

## revision_6

### entry (r6)
- Gates (auditor ran `gates.sh pap_therapy_rentals` read-only, 2026-10-13 09:31 UTC):
  - check_extended rc=0 :: EXTENDED OK
  - check_task_tools rc=0 :: TASK TOOL CONTRACT OK
  - replay_tasks rc=0 :: REPLAY OK
  - check_solvability rc=0 :: SOLVABILITY OK
  - check_compute rc=0 :: COMPUTE OK
  - check_grounding rc=0 :: GROUNDING OK
  - check_cache_diff rc=0 :: CACHE-DIFF INFO (optional; no correctness gate)
  - check_cross_fire rc=0 :: SCOPE OK
  - All 8 lines are OK/INFO.
- Views rebuilt:
  - 0.view.json 9481bf5d088caa949c867730c7da8261b85c503d719ee2a8228c62b996977ec0 (unchanged)
  - 1.view.json 16a9e4fd270f0a8def621a8aa3fd1eaaddd0dc603eeb2a422bc1070b2469842d (unchanged)
  - pap.extended.yaml 48376a3f40ebcfcff3b719c636ff27b7d5ca6137f32cc6dd1f9afe70dd85b798 (changed)
  - task_tools.py 282afe262ddea313a4d5e9b9c7cefc989e1729b8da81f87462e993e010aa6d35 (changed)
- Also read as input: `audits/render_source/pap_therapy_rentals/kb_r1_source_notes.md` (S1–S3; charter quotations and two seed dates, no GT).
- Frozen 2026-10-13 09:33 UTC (auditor clock), before any r6 task GT was read.

### S1–S3 verification (r6)
- **S1 (air-path "sale date": rule vs compute vs tool contract).**
  - Rule now: "on a unit shipped for a virtual setup they are counted from the transaction date on its sale line, the date the sale was paid and the unit left the warehouse".
  - Compute: `sale_date = LATEST('pap_billing','adjudication_date', …, event_type='pap_purchase_sale')`.
  - Schema `pap_billing.adjudication_date`: "… for a sale or refund, the transaction date".
  - `purchase_home_device_8c1f8216` Returns now call `service_from_date` "the delivery date booked on the sale line, which for a unit already in the home is the day of the sale". It no longer calls it "the sale date". The refund tool calls its own `service_from_date` "the received date".
  - Rule, compute and contract therefore all name `adjudication_date` as the transaction date and `service_from_date` as the delivery date. In task 0's world, 2026-09-17 is the transaction date and 2026-09-24 the delivery date; only one reading remains. The branch is not taken in either task (task 0 takes the warranty anchor). **Closed.**
  - Relation: in r1 I resolved this mapping from the schema and did not notice the purchase tool's contrary "sale date" label. That was a miss of this audit.
- **S2 (base parameter descriptions vs the refund's restocking base and delivery-fee credit).**
  - The descriptions in the verbatim base copy remain unchanged, as they must: `self_pay_delivery_fee` "Non-refundable delivery and setup fee on a self-pay sale", `self_pay_restocking_fee_pct` "Restocking fee withheld from the device price on a self-pay return".
  - The refund rule now states the departure explicitly and scoped: "For a self-pay refund this policy governs, and only for such a refund, the class's restocking percentage is taken of the refundable value worked out below rather than of the full device price, and the delivery fee, otherwise non-refundable, comes back to the patient only through the delivery fee credit below."
  - This names both base wordings it departs from ("rather than of the full device price", "otherwise non-refundable") and confines the departure to this policy's refunds. It agrees with the compute (`raw_restock` on `worn_value`; `fee_credit` added).
  - With wear at its fall-through (≤14 days → full price) the refundable value equals the price, so the baseline sentence "… of that price" is not contradicted.
  - `overwrite` entries bind base *policies*, not `parameter_schema` descriptions, so an in-rule scoped declaration is the available form. Observation O15 records this as the charter's mechanism limit, not a defect.
  - **Closed.**
- **S3 (depended-on rules announcing the policy that waits on them).** Scripted scan of the five depended-on rules (return_labor, return_parts, used_accessories, usage_nights, usage_hours) for refund / buy / bought / purchase / settle / sale-amount / withholding wording:
  - usage_nights now opens "A usage summary download is a statement Summit Ridge files on a device record to summarise the therapy use the modem has reported for the unit standing in the home." The purchase trigger is gone.
  - return_labor now opens "When a self-pay device bought outright comes back to Summit Ridge on a completed return pickup request, …". "bought outright" describes the device, and the refund is no longer named.
  - used_accessories' three `replaced_by` texts and its rule now scope to "a self-pay device sent back to Summit Ridge on a completed return pickup request" instead of "sent back for a refund".
  - No other hit. No depended-on rule names or restates the blocked policy or its prerequisite sentence. **Closed.**

### charter-global re-checks (r6)
- Scripted over the r6 charter:
  - base lines 1-1296 byte-identical;
  - every `policy_source` verbatim in its own rule;
  - every `baseline.rule` sentence and `compute_basis` quotation in its rule;
  - every `superseded_clause` verbatim in its base rule;
  - every `replaced_by` in its extended rule.
- Factor structure unchanged since r4/r5 (counts 4/4/4/6/4/4/5; each ≥2 parameter and 1 method; ≥3 distinct tiers). The only cross-binding reads are the r4 composition reads (O13). Prerequisite graph unchanged.
- Full-reach override sweep, re-run with the r5 method:
  - The re-scoped used_accessories replacements ("sent back to Summit Ridge on a completed return pickup request … and only for such a device"; every other device re-affirmed) reach exactly the returned self-pay units the base clauses would otherwise govern. The other five rows are unchanged from r5.
  - No in-force base sentence is contradicted. **PASS.**
- Tool contracts: purchase Returns wording changed as above. Bodies, owners, uuid8 names and argument formats are unchanged; no prerequisite checks; no ordering words or tool names.
- Residual, recorded as observation **O16**: the depended-on inspection tool's docstring still opens "Record the branch return inspection of a self-pay PAP device that has come back to Summit Ridge for a refund". The tool layer still names the refund the inspection serves, the same hop S3 removed from the rules. Its rule counterpart now says "on a completed return pickup request". It names no tool and no order, and the hop is already stated by the refund rule's own prerequisite sentences, so no score or path changes.

### findings (r6)
- S1, S2, S3 closed. No new red.
- Observations: O15 (parameter descriptions are declared departures in-rule because `overwrite` cannot target them); O16 (refund purpose word in the inspection docstring); O13, O14, O3, O7, O11 as before.

### closing status (r6, written after the r6 reveals; nothing above in revision_6 was changed after them)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- S1–S3: closed.
- Closing checklist: unchanged from r5. Scopes are disjoint and complete; trees hold; factors bear weight; the full-reach override sweep passes; docstrings state nothing beyond the rules except observation O16.
- Gates on the final form: 8/8 OK/INFO at the start of r6.
- Open observations (no red): O3, O7, O11, O13, O14, O15, O16.
- **The difficulty passes the source-layer audit as of revision 6.**
