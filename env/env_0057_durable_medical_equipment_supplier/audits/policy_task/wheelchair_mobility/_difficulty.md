# Policy-task audit — wheelchair_mobility / charter-global

## charter_global_frozen

- Freeze time: 2026-10-12T19:30:54Z (file mtime on write; revision 1; there is no earlier revision of this audit)
- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5). It did not write the audited artifacts.
- Frozen inputs (sha256, rechecked against the coordinator's HASHES.txt before reading):
  - `tasks/wheelchair_mobility/mobility.extended.yaml` e74257319c05b17fe69a7e6fc2bb37c87df166c837e5e311d87f07dfedde7e31
  - `tasks/wheelchair_mobility/task_tools.py` 5a2432ca6dae619559b57adb8396fe11a15f348ecbde338bb8265892313af136
  - masked views `.audit_views/policy_task/wheelchair_mobility/0.view.json` 89f91a45…, `1.view.json` 1f92fcbd… (same values as HASHES.txt)
- Read for this section: `blueprint/blueprint.yaml` (difficulty claims), `blueprint/products/mobility.yaml`, `oxygen.yaml` and `pap.yaml` (variant parameters only), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the compute primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (`DAYS`, `LATEST`, `CPARAM`, `CFIELD`, `RND`).
- Masked and not read when this section was written: everything in `tasks/wheelchair_mobility/tasks/*.json` (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure*). No earlier audits of this difficulty exist. Nothing here comes from a revealed GT.
- Entry conditions (step 0): the coordinator's brief includes the gate snapshot, with all gates rc=0 except check_traceability rc=1, which the brief explains as unlock-tool names pending the step-3 KB render. It also includes the masked views and their hashes. Inputs are complete.
- Base copy: every top-level key of `products/mobility.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) parses equal to the same key in the extended file. The only added key is `extended_policies`.

### policy_conflict_scan

There are six extended policies:

| id | subject | computes | target_tool (owner) | base refs | prerequisite |
|---|---|---|---|---|---|
| mobility_ext_battery_set_claim | mobility_repair | labor_units | record_battery_warranty_job_f5177195 (agent) | mobility_repair_responsibility | [] |
| mobility_ext_controller_claim | mobility_repair | labor_units | record_controller_warranty_job_4540982f (agent) | mobility_repair_responsibility | [] |
| mobility_ext_drive_unit_claim | mobility_repair | labor_units | record_drive_warranty_job_9fda7dd9 (agent) | mobility_repair_responsibility | [] |
| mobility_ext_cash_chair_refund | mobility_self_pay_refund | refund_amount | confirm_chair_return_refund_d347f359 (user) | mobility_self_pay | battery, controller, drive (action form, value_input → restock_pct) |
| mobility_ext_caster_claim | mobility_repair | labor_units | record_caster_warranty_job_ad31669e (agent) | mobility_repair_responsibility | [] |
| mobility_ext_kept_chair_adjustment | mobility_self_pay_refund | adjustment_amount | accept_chair_price_adjustment_610693ba (user) | mobility_self_pay | caster (action form, value_input → adj_pct) |

- **Overlapping subjects.** The four warranty-claim policies all write `mobility_repair`. Each is limited to one component (battery set / joystick-controller / drive motor-gearbox / tire-caster), and each tool stamps a different `repair_component`, so a given job falls under exactly one of them. The two self-pay policies both write `mobility_self_pay_refund`. One applies when the chair is "given back" (refund) and the other when the patient "keeps" it (adjustment), so they are disjoint on the patient's choice. No overlap gives a second answer.
- **Eligibility and time anchors.** Base warranties count from `delivery_date` (mobility_repair_responsibility). The claim policies count their own day spans to "the day the claim is posted" (NOW in compute), and the tools stamp the job with the request's `decision_date`. On both task worlds both anchors fall in the same tier (see the task files), so no divergence is demonstrated. Both self-pay policies keep the base window (`self_pay_return_window_days`, counted from the day after `delivery_date`, inclusive) and the custom/zero-window exclusion.
- **Cross-category read boundaries.** Battery, controller, drive and cash refund read the patient's oxygen holding (`status` ∈ {rental_active, payment_cap_reached}, variant `portable_hcpcs`). Kept adjustment reads the PAP holding `status`. Oxygen is difficulty home_oxygen_service and PAP is pap_therapy_rentals, so both are cross-difficulty reads. None of the reads writes anything.
- **Terminal states.** The claim tools add one `mobility_repair` row. The two user tools add one `mobility_self_pay_refund` row against the sale line. No status transition is written, so no terminal-state conflict arises.
- **Task scopes, expected from the prerequisite graph alone.** {cash_chair_refund, battery, controller, drive} forms one tree (4 policies, 4 tools) and {kept_chair_adjustment, caster} forms the other (2 policies, 2 tools). The two are disjoint and together cover all six extended policies. The task files compare this with the declared `charter_scope` after the reveal.
- Observation O-1 (scope claim): the difficulty claim in `blueprint.yaml` (`wheelchair_mobility.claim.event_types`) does not list `mobility_self_pay_refund` or `mobility_self_pay_sale`, but both root policies have `subject: [mobility_self_pay_refund]` and both user tools write `event_type="mobility_self_pay_refund"`. No difficulty claims that event. check_cross_fire passes because it checks per-task disjointness and not the blueprint claim. No consequence on the scored solution can be shown, so this is an observation.

### rule_compute_equivalence

Method: a script normalised whitespace and checked every `compute_basis` value as a substring of its policy's `rule`. It also checked every sentence of `baseline.rule` against the `rule`. Each binding was then read against its expression.

- battery_set_claim, controller_claim, drive_unit_claim, caster_claim, cash_chair_refund: every `compute_basis` quotation is verbatim in the rule. Each binding implements its quotation, including windows (`<=` for "no more than", `>=` for "or more"), "exactly" tiers (`==`), LATEST over `service_date` with the stated filters, COUNT of `repair_estimate` requests of any status, the in-home set as purchase_delivery or initial_rental_delivery with mode in_home_delivery_training, the cash refund's rounding of the fee share and use charge before the final rounding, and the final `RND`. Going the other way, every tier sentence of these rules has a compute branch. No compute branch lacks a rule sentence.
- **kept_chair_adjustment: not equivalent (finding F-1).** The `compute_basis.down_rate` quotation "`day_power` for a power chair delivered into the home with training, …" does not appear in the rule. The rule says: "A day credit is added for each such day at a rate set by the chair's class and how it was delivered: `day_power` for a power chair, `day_manual_home` for a manual chair delivered into the home with training, `day_manual_courier` for a manual chair delivered by courier, and nothing for a chair delivered any other way". The compute is `down_rate: "K('day_power') if (P('equipment_type') == 'power' and home_set2 >= 1) else (... manual tiers ...) else 0"`, and the factor ladder's first tier is "a power chair and delivered into the home with training". So the rule's power tier depends on class alone, while the compute and the ladder also require in-home delivery. Take a power chair delivered by courier: the rule gives `day_power` = 13.42 per day, and the compute gives 0, because no manual tier matches and the expression falls through to 0.
- All other kept_chair_adjustment bindings match their quotations.
- Observation O-2 (rounding primitive): every rule says "rounded to the cent half up". `RND` is `round(float(x), n)`, Python's round on a binary float, which is not half-up on exact .005 ties. No tie occurs in either task world (checked in the task files).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: six distinct pairs, each claimed by exactly one policy.
- uuid8 tails: f5177195, 4540982f, 9fda7dd9, d347f359, ad31669e, 610693ba. They share no prefix or suffix, are not sequential and are not adjacent values. Each looks independently generated.
- Tool bodies: none of the six reads any precondition. The four record tools take the request's `decision_date` as `service_date` and write one `mobility_repair` row with the fixed component and `manufacturer_warranty`. The two user tools write one refund row. None refuses, errors or hints when a prerequisite is unresolved, so the tool layer judges no prerequisite.
- Docstrings: none names another tool or states a position in a business sequence. Observation O-3: each docstring says "After the call the job/refund/adjustment appears in the chair's … history". That describes the tool's own effect, not an order against another action, but it does carry the word "after" that check 3 lists. Observation O-4: every record tool hard-codes `loaner_issued=False` and its docstring says "no loaner". Where a loaner was in fact delivered for the job (task 1's second caster repair), the written row misstates the world. No scored value reads `loaner_issued`. The policies read loaner `mobility_delivery` rows.
- Each policy subject and docstring admits a single business reading. No confirmation, review or wait is added beyond the policy. The "in person" confirmations are the rules' own owner=user statements.

### prerequisite_graph

- `prerequisite` is filled in on all six policies: four have `[]`, cash refund has three edges and kept adjustment has one.
- Edges: cash_chair_refund→battery_set_claim, cash_chair_refund→controller_claim, cash_chair_refund→drive_unit_claim, kept_chair_adjustment→caster_claim. Every `problem` is an extended policy id in this file. None points at itself or at a base policy. The graph is acyclic, with depth 1.
- `policy_source`: all four sentences are verbatim in their own policy's `rule` (machine check: True ×4).
- `form: action` on all four, each with a `fallback_reason`. No edge is state form.
- `kind: value_input` with `gate: restock_pct` (×3) and `gate: adj_pct` (×1). Both are real compute bindings of the blocked policy.
- `resolved_by` is the depended-on policy's `target_tool` in all four. Each tool writes a `mobility_repair` row with `repair_coverage=manufacturer_warranty`, which raises the `wjobs` / `adj_jobs` count read by the gate, so `effect` holds. Controller and drive rows also enter `drive_jobs`, as the effect text says.
- `condition`: "a mobility_repair row with repair_component X and repair_coverage manufacturer_warranty for every completed X repair_estimate request". This matches the sentence's "every X replacement completed … under the manufacturer's warranty has been posted". Observation O-5: `repair_estimate` requests carry no component (schema), so which completed request is "a battery-set / controller / drive / caster request" is reachable only from the customer's account of each visit. Both personas supply it on asking. The condition is no stronger or weaker than the sentence.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test on each sentence:

| edge | sentence | connective | waits on (form) | names no tool/id/snake_case | strength = condition |
|---|---|---|---|---|---|
| refund→battery | "The refund on a cash-sale chair given back is fixed only after every battery-set replacement completed on that chair under the manufacturer's warranty has been posted to its service history as a repair job." | only after | posting of the action, in business words (action) | yes | "every … completed" = condition's "for every completed" |
| refund→controller | "… is not fixed until every joystick or controller replacement completed … has been posted …" | not until | action | yes | same |
| refund→drive | "Before the refund … is fixed, every drive motor or gearbox replacement completed … must be posted …" | before | action | yes | same |
| kept→caster | "The price adjustment on a cash-sale chair the patient keeps is fixed only after every tire or caster replacement completed on that chair under the manufacturer's warranty is posted to its service history as a repair job." | only after | action | yes | same |

- Derivation (sentence + records + depended-on rule → resolving action, single reading): the refund rule waits on battery-set replacements completed under warranty being posted as repair jobs. The battery_set_claim rule ("Summit Ridge claims … the labor of every battery-set replacement done under the manufacturer's battery warranty … and posts that claim on the repair job") is the only rule that posts such a job. The records show which completed replacements already have a posted battery row. The same pattern singles out controller_claim, drive_unit_claim and caster_claim. Each sentence has one reading.
- None of the blocked rules words the dependency a second time, names a tool, or names another problem id. The depended-on rules do not restate the sentence. The docstrings say nothing about sequence (see O-3).
- **fallback_reason tested (observation O-6, ×4).** Each fallback argues that "no record-visible state singles out the battery-set (controller / drive / caster) posting". But each write leaves a `mobility_repair` row with its own `repair_component` (battery / joystick_controller / motor_gearbox / tires_casters) and `repair_coverage=manufacturer_warranty`. Only that one tool writes that component. So a state such as "the chair's service history shows a battery-set repair job under the manufacturer's warranty for every battery-set replacement completed on it" would have singled out the write. The action-form fallback is therefore unjustified. Per the skill this is an observation and not a red.
- Undeclared cross-problem order (observation O-7): the controller rule's "when a battery replacement under the manufacturer's warranty is posted on the same chair: when the latest such battery posting is no more than `harness_near_days` days before …" makes controller labor depend on the battery claim's write, and no edge declares that order. Where the only recent warranty battery replacement is still unposted, posting battery first gives the doubled controller allowance and posting controller first gives the standard one. On task 0 a warranty battery posting is already seeded, and both orders give the same controller value (shown in `0.md`), so no consequence is demonstrated there. This stays an observation.
- No base rule sentence grounds any edge.

### override_declarations

Each sentence of each `base_policy_refs` entry was checked against what the extended policy does with the quantity that is scored.

**mobility_repair_responsibility** (referenced by battery, controller, drive and caster, all with `overwrite: []`):
1. "While a chair is rental_active or suspended every repair is Summit Ridge's rental obligation …": not touched. The claims are for warranty repairs on owned chairs.
2. "On an owned chair the component's manufacturer warranty applies first, each counted from delivery_date: …": followed. Each claim is "done under the manufacturer's … warranty".
3. "Out of warranty, a repair … is billed to the coverage as labor at `repair_labor_rate_per_unit` per unit plus parts …; batteries are billed no more often than …": not touched. That is out-of-warranty coverage billing.
4. "A self-pay chair's out-of-warranty repair is patient_paid.": not touched.
5. "When labor plus parts would exceed `repair_cost_replace_threshold_pct` percent of `fee_schedule_purchase_price`, the chair is replaced instead.": not touched. The claimed units × rate stay far below the threshold on both worlds.
6. "A technician assesses … within `repair_assessment_business_days` …, and a loaner is issued where `loaner_during_owned_repair` is true.": not touched by the policies. See O-4 for the tool's loaner flag.
7. "A repair is recorded only on a chair the patient still has: … rental_active, suspended or patient_owned.": inherited.

Base fixes no value for warranty labor units (the `repair_cost` formula is for billing), so `overwrite: []` is correct. No undeclared override.

**mobility_self_pay** (referenced by cash_chair_refund and kept_chair_adjustment):
1. "Any class may be sold outright … at `self_pay_retail_price` plus `self_pay_delivery_fee`, paid in full at order.": followed. Both read the sale line.
2. "A self-pay chair is refunded only when it comes back unused and complete no later than … window …": declared by both. Cash refund replaces it with "comes back complete" (dropping "unused"). Kept adjustment replaces it with "receives a price adjustment without coming back only while …". The two replacements apply to disjoint choices (gave back / keeps), so the merged meaning is unique.
3. "The refund is the price less `self_pay_restocking_fee_pct` percent …; the delivery fee is never refunded.": declared by both, with replacements matching each rule's result sentence. Variable restocking, refunded fee, use charge, assessment and mount fees, adjustment percentage and credits are all inside the declared `replaced_by`.
4. "A sale is refunded at most once.": inherited by both. Observation O-8: the kept-chair adjustment books a `mobility_self_pay_refund` row against the sale line. Under the inherited dedup, a patient who keeps the chair, takes an adjustment, and later gives it back inside the window can never be refunded. No task exercises this.

Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped base branch was found. Neither rule calls the base output a "wrong value".

Base sentences outside `base_policy_refs` that bear on these policies (observation O-9): `mobility_return_pickup` ends "An owned chair is never picked up or charged", and `mobility_ownership` says "An owned chair is never picked up." But the cash-refund `use_anchor` ladder has a tier "when a pickup of the chair is recorded" for a chair that, being a cash sale, is `patient_owned`. Task 0's seed carries a `mobility_pickup` row and an approved `return_pickup` request on an owned chair. The base sentences govern the pickup action and the return/damage charges, not the refund amount, so no second number for the scored refund can be derived. This is recorded as an observation.

### factor_ladders

Structure per policy, from the charter only. Weight is checked in each task file.

| policy | factor | effect | decides | bindings | tiers | stated in rule | multi-source | cross-difficulty |
|---|---|---|---|---|---|---|---|---|
| battery | set_method | method | set_units | last_set, days_set, set_units | 3 (×2 / +1 / std) | yes | no (one history date) | — |
| battery | new_unit_window | parameter | new_units | days_new, new_units | 3 (2/1/0) | yes | no | — |
| battery | bay_handling | parameter | bay_units | loaners, home_set, bay_units | 3 (2/1/0) | yes | no (tier 2 "a loaner" is a single condition) | — |
| battery | o2_safety | parameter | o2_units | o2_a, o2_b, o2_port, o2_units | 3 (2/1/0) | yes | no (oxygen status ∧ portable class on the same oxygen holding row) | oxygen |
| battery | fault_review | parameter | fault_units | faults, fault_units | 3 (2/1/0) | yes | no | — |
| battery | shelf_conditioning | parameter | shelf_units | shelf_days, shelf_units | 3 (2/1/0) | yes | no | — |
| controller | harness_method | method | ctl_units | last_bat, days_bat, ctl_units | 3 (×2 / +1 / std) | yes | no | — |
| controller | first_weeks | parameter | first_units | ctl_age, first_units | 3 | yes | no | — |
| controller | ctl_handling | parameter | ctl_place | ctl_loaners, ctl_home, ctl_place | 3 | yes | no | — |
| controller | aux_port_test | parameter | aux_units | aux_a, aux_b, aux_port, aux_units | 3 | yes | no (as battery o2) | oxygen |
| drive | pair_method | method | drv_units | drv_age, drv_units | 3 (×2 / +align / std) | yes | no | — |
| drive | base_handling | parameter | drv_place | drv_loaners, drv_home, drv_place | 3 (1/2/0) | yes | no | — |
| drive | mount_removal | parameter | mount_units | mount_a, mount_b, mount_port, mount_units | 3 (1/2/0) | yes | no (as battery o2) | oxygen |
| drive | lemon_review | parameter | lemon_units | lemon_reqs, lemon_units | 3 | yes | no | — |
| refund | restock_ladder | parameter | restock_pct | wjobs, restock_pct | 4 (0/5/10/class %) | yes | no | — |
| refund | fee_share | method | fee_back | drive_jobs, req_days, fee_back | 3 (full / proportional / none) | yes | **yes**: tiers 1–2 = drive-system warranty job (service rows) ∧ return-request day span (request row) | — |
| refund | use_anchor | method | use_days | pick_day, use_days | 3 (pickup / request / booking day) | yes | no | — |
| refund | day_rate_tier | parameter | day_rate | home_set, day_rate | 4 (13.42/9.5/2.05/0) | yes | **yes**: class (holding variant) ∧ delivery mode (service rows) on every non-fall-through tier | — |
| refund | assess_withhold | parameter | assess_fee | assessed, assess_fee | 3 (125/75/0) | yes | no | — |
| refund | o2_mount_fee | parameter | mount_fee | mnt_a, mnt_b, mnt_port, mount_fee | 3 (85/35/0) | yes | no (as battery o2) | oxygen |
| caster | fork_method | method | cst_units | last_cst, days_cst, cst_units | 3 | yes | no | — |
| caster | early_wear | parameter | wear_units | cst_age, wear_units | 3 | yes | no | — |
| caster | wheel_bench | parameter | bench_units | cst_loaners, cst_home, bench_units | 3 (1/2/0) | yes | no (tier 1 "a loaner" single) | — |
| caster | recurrence_review | parameter | recur_units | cst_reqs, recur_units | 3 | yes | no | — |
| caster | tire_settling | parameter | settle_units | settle_days, settle_units | 3 | yes | no | — |
| kept | sev_tier | parameter | adj_pct | adj_jobs, adj_pct | 3 (15/10/5) | yes | no | — |
| kept | fee_return | method | fee_ret | adj_loaners, courier_set, fee_ret | 3 (full / half / none) | yes | no (tier 1 "a loaner" single) | — |
| kept | down_anchor | method | down_days | last_dec, last_loaner, down_days | 3 | yes | no (tier 1 "a loaner" single) | — |
| kept | down_rate_tier | parameter | down_rate | home_set2, down_rate | 4 (13.42/2.05/1.53/0) | **no — tier 1 differs (F-1)** | ladder/compute: yes (class ∧ delivery). **Rule: no** (rule tier 1 is "a power chair" alone) | — |
| kept | multi_service | parameter | ms_amt | pap_st, ms_amt | 3 (20/10/0) | yes | no | pap |
| kept | fail_timing | parameter | ft_amt | ft_days, ft_amt | 3 (15/7.5/0) | yes | no (one span) | — |

- Counts per policy: battery 6 (1 method, 5 parameter); controller 4 (1, 3); drive 4 (1, 3); refund 6 (2, 4); caster 5 (1, 4); kept 6 (2, 4). All are within 4–6, with at least 2 parameter and at least 1 method.
- Each factor's bindings are disjoint from every other factor's in the same policy. Every `decides` is an input, never `result`.
- No two tiers of a ladder select the same value or method on a reachable class. One unreachable exception: for K0005 and K0856, `self_pay_restocking_fee_pct` is 0, so restock_ladder's fall-through equals its jobs_high tier (0). Those classes are custom-configured and never refunded, so this is observation O-10.
- Baselines: every `baseline.rule` sentence is verbatim in its rule. Every factor's `baseline` equals its fall-through tier, and equals what `baseline.rule` states: the std units with zero added allowances, the class restocking percentage with no fee refunded, and adj_std_pct with "nothing else is added". Observation O-11: the cash refund's `baseline.rule` has no use charge at all, so it states nothing about "days of use". `use_anchor.baseline` (delivery→booking day) is the fall-through tier and the natural default, but it is not stated by the baseline paragraph.
- Method labels: each claim policy's method factor (×2 / +1 / +align on the standard allowance) is a multiplier or additive transform on an intermediate. That is one of the reference method families, and the matched-pair and alignment tiers describe different work. Observation O-12: the standard allowance is a fixed constant, so these "methods" are extensionally the value ladders {4,3,2}, {6,4,3}, {10,7,5} and {4,3,2}.
- Realism (observations, no scored consequence shown): O-13, kept `down_rate_tier` takes the per-day downtime credit from how the chair was originally delivered, and gives nothing to a manual chair collected at the branch. O-14, kept `fail_timing`'s fall-through disjunct "a longer span" can never hold for an eligible chair, because the eligibility window (≤ 30 days for every refundable class) caps delivery→request ≤ `ft_mid_days` = 30. The fall-through can be reached only through "no such request", so the ladder effectively divides customers in two. O-15, the remaining cross-difficulty ladders (oxygen-safety, aux-port test, mount removal, mount fee, PAP multi-service courtesy) are plausible as described work or courtesy and are not challenged.
- Cross-difficulty categories: oxygen (battery, controller, drive, refund) and pap (kept). Multi-source by the rule face: refund `fee_share` and `day_rate_tier`. In compute only: kept `down_rate_tier` (see F-1). The o2/aux/mount ladders combine two conditions on the same oxygen holding row, which does not meet "distinct records".

### findings

- **F-1 — SOURCE-POLICY RED (rule/compute non-equivalence), mobility_ext_kept_chair_adjustment, `down_rate`.**
  - Symptom: the `compute_basis.down_rate` quotation is not in the rule, and the ladder tier "a power chair and delivered into the home with training" is not a rule sentence.
  - Root cause: the rule's power tier reads "`day_power` for a power chair", while compute and ladder require `P('equipment_type') == 'power' and home_set2 >= 1`.
  - Evidence: `mobility.extended.yaml` kept_chair_adjustment `rule` (the "A day credit is added …" sentence), `compute.down_rate`, `compute_basis.down_rate`, `factors[down_rate_tier].ladder[0]`.
  - Demonstrated consequence: for a power chair delivered by courier, with a loaner and a 2-day downtime, the rule gives a day credit of 26.84 and the compute gives 0.00.
  - Affects: task 1, whose root is this policy. On task 1's world (a manual chair, courier) both faces agree, but the rule face removes the only multi-source factor of task 1; see `1.md` factor_weight.
- Observations O-1 … O-15 above. None is grounds for rework on its own.

## closing_checklist

Written after both reveals (2026-10-12T19:32:40Z). The pre-reveal sections above were not edited after the reveal. The only post-freeze edit to any file was the clerical freeze-timestamp correction disclosed in each file's header.

- **Status: the difficulty is NOT closed.** Task 1 fails two of the four relationships, so the step-4 close-out does not apply. The items below record where each check stands now.
- Per-task files: `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json, with `_difficulty.md` alongside them. This is revision 1; there are no older revisions.
  - Task 0: PASS on all four relationships.
  - Task 1: SOURCE-POLICY RED (F-1) and SOURCE-FACTOR RED (T1-F2).
- Coverage and scope:
  - The revealed `charter_scope` matches the pre-reveal expectation in § policy_conflict_scan:
    - task 0 = {battery_set_claim, controller_claim, drive_unit_claim, cash_chair_refund} with tools {f5177195, 4540982f, 9fda7dd9, d347f359}
    - task 1 = {caster_claim, kept_chair_adjustment} with tools {ad31669e, 610693ba}
  - The two scopes are disjoint, and together they cover all six extended policies and all six task tools.
  - `required_documents` equals `charter_scope.extended_policies` in both tasks.
  - The uuid8s are independent (§ action_binding_and_uuids).
- Trees:
  - Task 0: 3 prerequisite problems, all 3 edges `value_input`, with an owner=user root.
  - Task 1: 1 prerequisite problem, 1 `value_input` edge, with an owner=user root.
  - The difficulty-wide graph is acyclic (depth 1), and no cross-task edge exists.
- Factors:
  - Every computation declares 4–6 factors, with ≥2 parameter and ≥1 method, and every factor bears weight against an honest baseline. All-baseline fall-backs differ from gold: 2, 3, 5, 3196.00, 2, 24.95.
  - Task 0 has multi-source factors (fee_share, day_rate_tier) and cross-difficulty factors (oxygen).
  - **Task 1 has a cross-difficulty factor (pap) but no multi-source factor that survives on the rule face (T1-F2).**
- Gates: not re-run by this auditor. Step 0 forbids it, and there is no final form yet. The coordinator's snapshot in the brief is the latest gate evidence. check_compute passed, presumably because it reads multi-source status from the compute face, which differs from the rule face on down_rate_tier.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same erl-task-policy-audit subagent (Claude Opus 5.5). This section was written before any round-2 task JSON was read.
- Hashes, checked against HASHES.txt:
  - `mobility.extended.yaml`: ab63819f9d3b4030c97931e73ee30d01c593edca1673e1a5aed1cb8394ab22b5. Changed from round 1 (e7425731…).
  - `task_tools.py`: 2b630d1a03b80e312d9bc2089c5240f2aa92a78ad761e6c9f0160655a5168032. Changed from round 1 (5a2432ca…).
  - Because both inputs changed, every charter-global section was re-derived in full. Nothing below is carried forward by reference.
- The base copy still matches `products/mobility.yaml` key by key. The only added key is `extended_policies`.
- contamination_disclosure: this auditor read the round-1 GT of both tasks during round 1. The round-1 sections above were left untouched. No round-2 GT had been read when this section was written.

### Round-1 items re-checked against the artifacts

- **F-1 (kept `down_rate` rule/compute) — CLOSED.**
  - The rule now reads "`day_power` for a power chair delivered into the home with training, `day_manual_home` for a manual chair delivered into the home with training, `day_manual_courier` for a manual chair delivered by courier, and nothing for a chair delivered any other way".
  - This matches `compute.down_rate` and `factors[down_rate_tier].ladder`.
  - A machine re-check finds every `compute_basis` value of all six policies verbatim in its rule, every `baseline.rule` sentence in its rule, and every factor binding present in compute.
- **O-2 (rounding) — CLOSED.** Every money result and intermediate that is stated as rounded now uses `int(x*100 + 0.500001)/100`, which rounds half up for the positive values involved. The user tools keep `round(float(amount), 2)` on an amount that already has two decimals.
- **O-3 (the word "after" in docstrings) — CLOSED.** Grep finds no "after", "before", "first", "then" or "once" anywhere in `task_tools.py`.
- **O-4 (`loaner_issued` hard-coded) — CLOSED, but it adds a scored argument.**
  - All four record tools now take `loaner_issued: bool` and write it as given.
  - The docstring defines it: "true applies when the chair's service history shows a loaner chair delivered for the time the chair was in for this repair, false applies when no loaner chair was delivered for this repair".
  - It is decidable from the delivery rows and the request dates. No compute reads it.
- **O-6 (action-form fallbacks) — CLOSED.** All four edges are now `form: state` with no `fallback_reason`. Four-point test on each sentence:
  - "… fixed only after the chair's service history shows a battery repair job under the manufacturer's warranty for every battery-set replacement completed on it" (only after).
  - "… not fixed until … shows a joystick and controller repair job …" (not until).
  - "Before … is fixed, … must show a motor and gearbox repair job …" (before).
  - kept: "… fixed only after … shows a tires and casters repair job …" (only after).
  - Each waits on a record-visible state named in the words of the service history: "repair job", component, "under the manufacturer's warranty". None names an action, performer, tool, id or snake_case token, and the scope "for every … replacement completed on it" equals the `condition`.
  - For each state, exactly one write of this difficulty brings it about: the tool whose hard-coded `repair_component` matches. No other task tool or share tool writes a `mobility_repair` row.
  - All four `policy_source` sentences are verbatim in their own rule.
- **O-7 (undeclared battery→controller order) — CLOSED.**
  - The controller's method factor `harness_method` no longer reads warranty battery postings. It now counts repair_estimate requests: `ctl_reqs` ≥ `harness_high_count` 3 doubles the allowance, exactly 2 adds one unit, and fewer applies the standard allowance.
  - Postings do not change that count, so no claim reads another claim's write.
  - Rule, compute, compute_basis and ladder agree.
- **O-8 (adjustment uses the one refund) — CLOSED.** The kept rule now states it outright: "Accepting a price adjustment uses the sale's one refund, so a chair that has received one is not refunded if it is later given back." This agrees with the inherited base clause "A sale is refunded at most once."
- **O-9 (owned chair picked up) — CLOSED as a base contradiction, but the fix introduces F-2 below.**
  - The refund rule now says "A cash-sale chair is the patient's own and is never picked up: it comes back when the patient brings it to a branch, where its return_pickup request is approved on the day it is checked in complete."
  - This agrees with base `mobility_ownership` and `mobility_return_pickup`.
  - `use_anchor` now reads the latest return_pickup request's status and decision_date instead of a pickup row.
- **O-14 (fail_timing dead disjunct) — CLOSED.** `ft_mid_days` is now 21. The window is 30 days for every refundable manual class, so "a longer span" (22–30 days) can now occur.
- **T0-O1 (matched pair vs persona) — CLOSED.** The drive rule now says "for no more than `pair_days` days the manufacturer's early-failure teardown of the whole drive train applies and the allowance is the standard drive-unit allowance doubled". It no longer claims that both units are replaced. Rule, compute and ladder agree.
- **Kept as observations, verified unchanged:**
  - O-1: the blueprint claim still omits `mobility_self_pay_refund`.
  - O-5: the `condition` fields still name "battery-set / controller / … repair_estimate request", which the request records do not carry. The component is reachable only from the persona.
  - O-10, O-11, O-12, O-13.

### Re-scan of the charter for new defects

- **policy_conflict_scan.**
  - The six policies, their subjects, computes and target tools are unchanged from round 1. The prerequisite graph is unchanged in edges: refund→{battery, controller, drive}, kept→caster, all `value_input`. It is acyclic, with depth 1.
  - The three postings in task 0 now share no read: battery reads its own family's postings, controller reads the request count, and drive reads neither. The order among them cannot matter on any world.
  - The overwrite declarations are unchanged and remain sufficient. The new refund sentence restates base ownership rather than overriding it.
- **rule_compute_equivalence.** PASS for all six policies (machine check above, plus a re-read of the new `use_days`, `ret_dec`, `ret_st`, `ctl_reqs` and `ctl_units` bindings).
- **action_binding_and_uuids.**
  - The six `(target_tool, computes)` pairs are unique, and the uuid8 tails are unchanged and independent.
  - No tool body checks a prerequisite. The only new argument, `loaner_issued`, is written as given.
- **factor_ladders.**
  - Counts per policy are unchanged: battery 6, controller 4, drive 4, refund 6, caster 5, kept 6. Each has ≥2 parameter and ≥1 method.
  - Multi-source on the rule face:
    - refund `fee_share` and `day_rate_tier`;
    - kept `down_rate_tier`, whose three non-fall-through tiers are now each class ∧ delivery row in the rule itself.
  - Cross-difficulty: oxygen (battery, controller, drive, refund) and pap (kept).
- **F-2 — SOURCE-FACTOR RED (new in round 2): the refund's `use_anchor` ladder now restates the policy's scope, and its fall-through/baseline is never applied to any refunded customer.**
  - Symptom: `use_anchor` has three tiers:
    1. "the chair's latest return_pickup request is approved" → days to its decision_date;
    2. "the chair has a return_pickup request that is not approved" → days to its requested_date;
    3. otherwise → days to the booking day, which is also the factor's `baseline` (`DAYS(F('delivery_date'), NOW)`).
  - Root cause: two sentences of the same rule.
    - The new sentence: "A cash-sale chair … comes back when the patient brings it to a branch, where its return_pickup request is approved on the day it is checked in complete."
    - The eligibility sentence: "A cash-sale chair is refunded only when it comes back complete no later than `self_pay_return_window_days` after delivery …"
    - Together they make "the return_pickup request is approved" true of every customer who reaches the refund write.
  - Demonstrated consequence:
    - Tier 1's condition holds for every refunded chair.
    - Tier 2 (a request not yet approved means the chair has not come back) and tier 3 (no request means the chair never came back) can only describe chairs the same rule refuses to refund.
    - So the ladder has one live tier, and the factor's baseline (counting use to the booking day) is a treatment the published policy never gives a refunded customer. That is the straw-man baseline in another form.
    - The factor still moves the number on task 0 (3746.15 → 3732.73 at baseline). The defect is that the ladder is not real, not that the factor lacks weight.
  - Affects: `mobility.extended.yaml` cash_chair_refund `rule` (the branch-return sentence together with the window sentence), `compute.use_days`, `factors[use_anchor]`. It bears on task 0.
  - With `use_anchor` struck, the refund keeps 5 factors (1 method, 4 parameter), so the count bound alone is still met. The red stands under the "unreal ladder" test.

### closing_checklist (revision 2)

Written after both round-2 reveals (2026-10-12T21:02:51Z). The revision-2 pre-reveal section above was not edited after the reveal.

- **Status: the difficulty is still NOT closed.**
  - Task 1: PASS on all four relationships.
  - Task 0: SOURCE-FACTOR RED on the new F-2. It passed in round 1, so this is a regression caused by the O-9 rework.
- Round-1 REDs:
  - F-1 / T1-F1: closed.
  - T1-F2: closed.
- Reworker's "closed" claims, verified against the artifacts: F-1/T1-F1, T1-F2, O-6, O-9 (closed, but see F-2), O-7, O-2, O-4, O-3, O-8, O-14 and T0-O1 are all closed.
- Kept as observations, verified unchanged: O-1, O-5, O-10, O-11, O-12, O-13, T0-O2, T1-O1.
- Scope:
  - task 0 covers {battery, controller, drive, cash refund};
  - task 1 covers {caster, kept adjustment};
  - the two are disjoint and together complete;
  - the uuid8s are independent.
- Trees: task 0 has 3 prerequisites and task 1 has 1. All edges are `value_input` / state, each root is owner=user, and the graph is acyclic.
- Factors:
  - All six computations have 4–6 factors with ≥2 parameter and ≥1 method, and every factor bears weight.
  - Multi-source: task 0 (fee_share, day_rate_tier); task 1 (down_rate_tier).
  - Cross-difficulty: task 0 oxygen; task 1 pap.
  - F-2 fails the ladder-reality test for `use_anchor`.
- Gates were not re-run by this auditor; the coordinator's round-2 snapshot is the gate evidence.

## revision_3

### entry conditions and charter_global_frozen (revision 3)

- Gates: at the coordinator's instruction, this auditor ran `bash /tmp/erl0057_coord/gates.sh wheelchair_mobility` from the repo root. It reads only, and nothing under /tmp/erl* was edited.

  | gate | rc | result |
  |---|---|---|
  | check_extended | 0 | EXTENDED OK |
  | check_task_tools | 0 | TASK TOOL CONTRACT OK |
  | replay_tasks | 0 | REPLAY OK |
  | check_solvability | 0 | SOLVABILITY OK |
  | check_compute | 0 | COMPUTE OK |
  | check_grounding | 0 | GROUNDING OK |
  | check_cache_diff | 0 | CACHE-DIFF INFO |
  | check_cross_fire | 0 | SCOPE OK |

  All 8 lines are green, so the audit proceeds.
- Views: rebuilt with `.venv/bin/python /tmp/erl0057_coord/make_views.py wheelchair_mobility`. It printed:
  - `0.view.json` 3b3715669be954ec23d77de3f01651963c8acc77c70f996f0d4a08b005c14930 (same as round 2)
  - `1.view.json` 1f92fcbd5dc590116f99f08f9a5307c9e402669aff91fa132502d856c8f09a9c (same as rounds 1 and 2)
  - `mobility.extended.yaml` c9f2ebdf00eea565c0be3fc539050bdd725bb47f6322157c0a39033d9da2b7e4 (changed from round 2's ab63819f…)
  - `task_tools.py` 2b630d1a03b80e312d9bc2089c5240f2aa92a78ad761e6c9f0160655a5168032 (same as round 2)
- The charter changed, so every charter-global section was re-derived. The tools did not change, so the round-2 tool conclusions are carried forward by hash: O-3 and O-4 closed, no prerequisite judged by any tool, uuid8s independent.
- contamination_disclosure: this auditor has read the round-1 and round-2 GT of both tasks. No round-3 task JSON was read before the freezes below.
- The base copy still matches `products/mobility.yaml`.
- Machine re-check:
  - every `compute_basis` value of all six policies is verbatim in its rule;
  - every `baseline.rule` sentence is in its rule;
  - every factor binding exists in compute;
  - all four `policy_source` sentences are verbatim and `form: state` (the round-2 sentences are unchanged).

### what changed in round 3 (from the charter text)

- **battery / controller / drive: handling allowance.** The ladder is now:
  - no loaner and ≥2 in-home assessments → `access_units` 3 / `ctl_access_units` 3 / `drv_access_units` 2;
  - no loaner and exactly 1 assessment → `site_units` 2 / `ctl_site_units` 2 / `drv_site_units` 1;
  - nothing otherwise, "such as bench work while a loaner chair is out".
  - The bench tier is gone. Each tier now combines loaner rows with assessment rows, so all three factors are multi-source.
- **cash refund:**
  - `day_rate_tier` is now: power → `rate_power` 13.42; manual in-home → 2.05; manual courier → `rate_manual_courier` 1.53; any other manual → 0.
  - `use_anchor` is now:
    1. a loaner was delivered → days from delivery to the latest loaner delivery;
    2. no loaner, and the latest return_pickup request was made on a day before it was approved → days to its requested_date;
    3. otherwise → days to its decision_date (check-in).
  - `use_anchor`'s baseline is now days to the check-in day (`ret_dec`), or to the booking day when there is none.
- **kept adjustment:**
  - `sev_tier`: ≥3 jobs → 20%; exactly 2 → 15%; fewer → 5%, described as "the one warranty repair the adjustment presumes".
  - `down_anchor`'s fall-through is now "latest request still undecided → no days".
  - `down_rate_tier`: power → day_power, for any delivery.
  - `multi_service` now reads PAP and oxygen status: (PAP or O2 rental_active) → 20; (neither rental_active) and (PAP owned or O2 payment_cap_reached) → 10; otherwise → 0. It is multi-source and cross-difficulty (pap; oxygen is read too).
- **caster:** unchanged.

### F-2 (round 2) re-checked: CLOSED

- The refund's `use_anchor` no longer splits customers on whether the return request is approved, which every refunded chair satisfies.
- Its three tiers can each occur for a chair the policy refunds:
  - tier 1: a cash chair that had a loaner during a warranty repair and was then given back;
  - tier 2: return asked for on one day and the chair checked in on a later day;
  - tier 3: asked for and checked in on the same day.
- Its baseline (the check-in day) is the anchor a refunded chair can actually have.

### reachability sweep (every tier and every baseline, for a customer each policy serves)

- **Claim policies.**
  - Battery, controller and drive warranty months are 0 for manual classes, so these claims serve only power chairs.
  - Base `mobility_qualification` delivers a power chair only after a home assessment, so ≥1 assessment always exists. The "no assessment" corner is never needed, because the fall-through is reachable through a delivered loaner.
  - Tiers by factor:
    - set_method: posting ≤30 days / 31–180 days / no posting — reachable (a first warranty battery replacement has no prior posting).
    - new / first / pair day spans: >60 or >90 days lies inside the 6–24-month warranties — reachable.
    - fault / lemon counts, harness ≥3 / =2 / 1 — reachable.
    - o2 tiers — reachable.
    - shelf — reachable.
  - Caster: unchanged, and reachable, as in rounds 1 and 2.
- **Refund.**
  - restock: 0–1 jobs is allowed (a refund needs no repair) — reachable.
  - fee_share — reachable.
  - use_anchor — see F-3 below.
  - day_rate: power / manual in-home / manual courier / manual branch — reachable.
  - assess: power chairs have ≥1 assessment, manual chairs have 0 — reachable.
  - mount — reachable.
- **Kept adjustment.**
  - sev_tier: the fall-through (1 posted job) is now reachable for the customer the policy serves.
  - down_anchor: "undecided latest request" is reachable while another fault is open.
  - fail_timing: 22–30 days is reachable (`ft_mid_days` 21).
  - fee_return, down_rate and multi_service — reachable.

### new findings (revision 3)

- **F-3 — SOURCE-FACTOR RED (new): `use_anchor`'s tiers 2 and 3 are one tier written as two.**
  - Symptom: tier 2 ("no loaner chair delivered and the latest return_pickup request was made on a day before it was approved" → days to its requested_date) and the fall-through ("otherwise (the request was made the day the chair was checked in)" → days to its decision_date) are separated only by whether requested_date < decision_date.
  - On every chair the fall-through covers, requested_date = decision_date. An approval cannot come before its request, and a refund needs the approval: "a cash-sale chair … comes back when … its return_pickup request is approved on the day it is checked in complete" and "is refunded only when it comes back complete".
  - So for every fall-through customer, the fall-through's anchor and tier 2's anchor are the same date.
  - Root cause: cash_chair_refund `rule`, the sentence "The days of use of a cash-sale chair given back are counted by a different method according to how its return is evidenced: …", together with `compute.use_days` and `factors[use_anchor].ladder`.
  - Demonstrated consequence: the ladder rewritten as "loaner → latest loaner date; no loaner → the return request's requested_date" reproduces every value. The scratch probe replaced `use_days` with that two-tier form:
    - task-0 world: 3759.57 both ways;
    - the same world with the request made on the check-in day (tier-3 variant): 3735.51 both ways.
  - The factor therefore has two real tiers, against the required three or more. It still bears weight on task 0: the baseline gives 3746.15 against 3759.57.
  - It bears on task 0. With `use_anchor` struck, the refund keeps 5 factors (1 method `fee_share`, 4 parameter), so the count bounds alone still hold.
- **Observation O-16.** `use_anchor` tier 1 justifies the latest loaner date as "the day the patient stopped using the chair". But a loaner is delivered during a repair, after which the chair returns to the patient (task 1's world shows exactly this). So that date is not, in general, when use stopped. No task world reaches tier 1, so no consequence is demonstrated.
- **Observation O-17.** The claim policies' handling allowance now keys "work done at the patient's home" on the number of in-home accessibility assessments recorded (≥2 → the larger allowance). A home that needed a second assessment as a proxy for harder access is plausible, so no red.
- Observations kept from earlier rounds: O-1, O-5, O-10, O-11, O-12, O-13, T0-O2, T1-O1.

### closing_checklist (revision 3)

- Written after the round-3 reveals (2026-10-13T04:34:50Z). The pre-reveal revision-3 text was not edited.
- **Status: still NOT closed.**
  - Task 1: PASS.
  - Task 0: SOURCE-FACTOR RED on F-3, which is new and was introduced by the F-2 rework.
- **Round-2 RED F-2 / T0-F3: closed.**
- **Regressions:** none apart from F-3.
  - Task 1's multi-source factor moved from `down_rate_tier`, which is no longer multi-source on the rule face, to `multi_service`, which is.
  - Every earlier closure still holds: F-1, T1-F2, O-2, O-3, O-4, O-6, O-7, O-8, O-9, O-14 and T0-O1.
- Scope and trees:
  - The scopes are disjoint and together complete.
  - Task 0 has 3 state-form `value_input` edges and task 1 has 1. Both roots are owner=user, and the graph is acyclic.
- Factors:
  - All six computations have 4–6 factors with ≥2 parameter and ≥1 method, and every factor bears weight.
  - Multi-source: task 0 has fee_share and the three handling allowances; task 1 has multi_service.
  - Cross-difficulty: task 0 reads oxygen; task 1 reads pap (oxygen is read but absent).
  - Reachability holds for every tier and every baseline. The exception is that use_anchor tiers 2 and 3 collapse into one (F-3).
- Gates: the auditor's round-3 run was green on all 8 lines (see entry conditions).

## revision_4

### entry conditions and charter_global_frozen (revision 4)

- Gates: this auditor ran `bash /tmp/erl0057_coord/gates.sh wheelchair_mobility` (read-only).

  | gate | result |
  |---|---|
  | check_extended | rc=0 EXTENDED OK |
  | check_task_tools | rc=0 TASK TOOL CONTRACT OK |
  | replay_tasks | rc=0 REPLAY OK |
  | check_solvability | rc=0 SOLVABILITY OK |
  | check_compute | rc=0 COMPUTE OK |
  | check_grounding | rc=0 GROUNDING OK |
  | check_cache_diff | rc=0 CACHE-DIFF INFO |
  | check_cross_fire | rc=0 SCOPE OK |

  All 8 lines are green, so the audit proceeds.
- Views, from `make_views.py wheelchair_mobility`:
  - `0.view.json` 3b3715669be954ec23d77de3f01651963c8acc77c70f996f0d4a08b005c14930 (unchanged)
  - `1.view.json` 1f92fcbd5dc590116f99f08f9a5307c9e402669aff91fa132502d856c8f09a9c (unchanged)
  - `mobility.extended.yaml` ac8fecd5d09b86bc179e307230e99e601699f4bed9a26dd25d71c9d63326a385 (changed from round 3's c9f2ebdf…)
  - `task_tools.py` 2b630d1a03b80e312d9bc2089c5240f2aa92a78ad761e6c9f0160655a5168032 (unchanged, so the tool conclusions carry forward by hash)
- Per-policy fingerprints against round 3:
  - battery, controller, drive and cash refund changed;
  - caster (c81b8b9d2591) and kept adjustment (d6b339af3435) are byte-identical as parsed;
  - the base copy is unchanged.
- contamination_disclosure: GT from rounds 1–3 of both tasks is known to this auditor. No round-4 task JSON was read before the freezes below.
- Machine re-check, all six policies:
  - every `compute_basis` value is verbatim in its rule;
  - every baseline sentence is in its rule;
  - every factor binding exists in compute;
  - all four `policy_source` sentences are verbatim and state form.

### what changed in round 4

- **Battery / controller / drive handling allowance: wording only; compute unchanged.**
  - The sentence now reads "A … handling allowance is added by the chair's loaner and home-assessment records: … when no loaner chair has been delivered for the chair and two or more in-home accessibility assessments are recorded …, … exactly one …, and nothing in any other case".
  - The round-3 claims "work done at the patient's home" and "such as bench work while a loaner chair is out" are gone.
  - The ladder fall-through now reads "(for example a loaner chair has been delivered for the chair)".
  - **O-17: closed.** The wording now states only what the records test.
- **Cash refund `use_anchor`, rewritten.** The rule sentence: "The days of use of a cash-sale chair given back are counted by a different method according to its repair history:
  1. when a loaner chair has been delivered for the chair, from delivery_date to the requested_date of its latest return_pickup request, less the days from the requested_date to the decision_date of its latest repair_estimate request;
  2. when no loaner chair has been delivered and the chair has a repair_estimate request, from delivery_date to the requested_date of its latest repair_estimate request, the day its latest fault was reported, so that no use is charged after the chair's latest failure;
  3. otherwise from delivery_date to the decision_date of its latest return_pickup request, the day the chair was checked in at the branch."
  - Compute: `use_days`, `rep_req` and `rep_dec`. The baseline (check-in day) equals tier 3. The rule and compute are equivalent: tier 1's compute also requires a return request, which every refunded chair has.

### F-3 / T0-F4 (round 3) re-checked: CLOSED

- The tiers now split on the repair history: loaner delivered / no loaner but a repair request / no repair request. Each tier uses its own anchor.
- Distinctness probe: each tier's method was applied to a customer of each other tier (scratch script, refund value; units are dollars of refund).

  | customer | T1 method | T2 method | T3 method |
  |---|---|---|---|
  | task 0 (tier 2: no loaner, latest repair request 10-10, return requested 10-12, checked in 10-13) | 3772.99 | **3786.41** | 3746.15 |
  | task 0 + a loaner delivered 10-10 (tier 1) | **3772.99** | 3786.41 | 3746.15 |
  | task 0 with no repairs (tier 3; T2 does not apply) | 2928.64 | — | **2915.22** |

  No two tiers give the same value on a customer the policy serves.
- Each tier occurs for a realistic refunded chair:
  - tier 1: a loaner during a warranty repair, then the chair is given back;
  - tier 2: faults with no loaner;
  - tier 3: a chair returned with no repair request.
- The baseline (check-in) is the anchor a fault-free return actually gets.

### O-16 (round 3) re-checked: CLOSED

- The false justification "the latest loaner delivery, the day the patient stopped using the chair" is gone.
- Each remaining explanatory clause is literally true of the records it names:
  - "the requested_date of its latest repair_estimate request, the day its latest fault was reported" — a repair request is the fault report;
  - "so that no use is charged after the chair's latest failure" — this describes the tier's own effect;
  - "the decision_date of its latest return_pickup request, the day the chair was checked in at the branch" — per the rule's branch-return sentence, which says the return_pickup request "is approved on the day it is checked in".

### Re-scan for new defects (revision 4)

- **Conflicts / overrides / scope:** unchanged from round 3. No new cross-problem order. `use_days` reads requests and deliveries, not postings, so the three postings still commute.
- **Reachability:** every tier and baseline of every factor is reachable, as in revision 3, with the refund's `use_anchor` as tabled above.
- **Ladder reality:**
  - Tier 1 subtracts the latest repair downtime from use while a loaner covered the patient.
  - Tier 2 stops charging at the last failure for a patient left without a loaner.
  - Both are plausible goodwill treatments for a chair returned for repeated failure.
- **Near-miss on the refund:** the latest repair request (10-10) against the return request (10-12) and the check-in (10-13). This is genuine.
- **Result:** no new defect found. Observations carried: O-1, O-5, O-10, O-11, O-12, O-13, T0-O2, T1-O1. O-16 and O-17 are closed.

### closing_checklist (revision 4)

Written after the round-4 reveal (2026-10-13T05:32:55Z). The pre-reveal revision-4 text was not edited.

- **Both tasks PASS all four relationships. This difficulty passes the source-layer audit.**
- Every RED from rounds 1–3 is closed: F-1, T1-F2, F-2/T0-F3 and F-3/T0-F4. No regression and no new defect.
- Every observation is either closed or kept as an observation:
  - Closed: O-2, O-3, O-4, O-6, O-7, O-8, O-9, O-14, O-16, O-17, T0-O1.
  - Kept: O-1, O-5, O-10, O-11, O-12, O-13, T0-O2, T1-O1.
- Files: `0.md` and `1.md` map one-to-one to tasks/0.json and tasks/1.json, with `_difficulty.md` alongside. Revisions 1–4 are all kept, with older text untouched.
- Coverage: the scopes are disjoint and together complete.
  - Task 0 covers battery, controller, drive and the cash refund.
  - Task 1 covers caster and the kept-chair adjustment.
  - Each of the six task tools has an independent uuid8.
- Trees: no cycles.
  - Task 0 has 3 prerequisite edges, all `value_input` and state form.
  - Task 1 has 1 such edge.
  - Both roots are owner=user.
- Factors: every computation has 4–6 factors, including ≥2 parameter and ≥1 method.
  - Every ladder has ≥3 tiers, the tiers are distinct, and every tier and baseline is reachable by a customer the policy serves.
  - Every factor bears weight against an honest baseline.
  - The all-baseline fall-backs (2 / 3 / 5 / 3196.00; 2 / 24.95) all differ from gold.
  - Multi-source: task 0 has fee_share and the three handling allowances; task 1 has multi_service.
  - Cross-difficulty: task 0 reads oxygen; task 1 reads pap.
- Gates: the instantiation-stage gates were re-run on this final form (auditor's round-4 run above) and all 8 lines are green. check_traceability was not in the 8-line set; it is deferred to post-render by design, per the coordinator.

## revision_5

### entry conditions and charter_global_frozen (revision 5)

- Gates: `bash /tmp/erl0057_coord/gates.sh wheelchair_mobility`, run by this auditor (read-only). All 8 lines are green, so the audit proceeds.

  | gate | rc | result |
  |---|---|---|
  | check_extended | 0 | EXTENDED OK |
  | check_task_tools | 0 | TASK TOOL CONTRACT OK |
  | replay_tasks | 0 | REPLAY OK |
  | check_solvability | 0 | SOLVABILITY OK |
  | check_compute | 0 | COMPUTE OK |
  | check_grounding | 0 | GROUNDING OK |
  | check_cache_diff | 0 | CACHE-DIFF INFO |
  | check_cross_fire | 0 | SCOPE OK |

- Views, from `make_views.py`:
  - `0.view.json` 3b3715669be954ec23d77de3f01651963c8acc77c70f996f0d4a08b005c14930 (unchanged)
  - `1.view.json` 1f92fcbd5dc590116f99f08f9a5307c9e402669aff91fa132502d856c8f09a9c (unchanged)
  - `mobility.extended.yaml` 18cbd8d0a4e2002a17abde8efc37988420f0f6b300f03d8fe40b1cdc3a277ee1 (changed from round 4's ac8fecd5…)
  - `task_tools.py` 2b630d1a03b80e312d9bc2089c5240f2aa92a78ad761e6c9f0160655a5168032 (unchanged)
- Per-policy fingerprints against round 4:
  - battery, controller and drive are unchanged;
  - cash refund, caster and kept adjustment changed;
  - the base copy is unchanged.
- Additional input: the renderer's report `audits/render_source/wheelchair_mobility/render_r1_source_mismatches.md`, read as the item list. It is not evidence.
- contamination_disclosure: this auditor has seen the GT from rounds 1–4 of both tasks. No round-5 task JSON was read before the freezes below.
- Machine sweep, scratch scripts `struct5.py` and `recompute5.py`, over all six policies:
  - every `compute_basis` value is verbatim in its rule;
  - every `baseline.rule` sentence is in its rule, and every `baseline.params` key appears in `baseline.rule`;
  - every `overwrite.replaced_by` is verbatim in the rule;
  - all four `policy_source` sentences are verbatim and in state form;
  - no compute binding belongs to two factors;
  - **no factor binding reads another factor's binding**;
  - **no non-factor binding uses a `K()` constant absent from `baseline.params`**.

### render-found items re-checked against the artifacts

1. **A factor tier read another factor's binding (kept `down_rate` read `courier_set`) — CLOSED.**
   - `fee_return` now owns `fr_loaners` and `fr_courier`. `down_rate_tier` owns `dr_home` and `dr_courier`, and `down_anchor` owns `da_req`, `da_dec` and `da_loaner`.
   - In the refund, `fee_share` owns `fs_ret_req` and `use_anchor` owns `ua_ret_req`.
   - The sweep above finds no cross-factor read in any policy.
2. **Non-factor `use_charge` / `day_credit` built on constants the baseline never states — CLOSED.**
   - Cash refund `baseline.rule` now states the standard use charge: "less a use charge of `std_day_rate` for each day of use beyond the first `grace_days` days, the days of use running from delivery_date to the decision_date of the chair's latest return_pickup request (the booking day when it has none) …". Its params are `[self_pay_restocking_fee_pct, std_day_rate, grace_days]`.
   - Kept `baseline.rule` states "plus a day credit of `day_std` for each day counted, the days running from the requested_date of the chair's latest repair_estimate request to its decision_date (no days while that request is undecided or when the chair has none) …". Its params are `[adj_std_pct, day_std]`.
   - Each fall-through tier now equals its stated baseline:
     - `day_rate_tier` otherwise → `std_day_rate`;
     - `down_rate_tier` otherwise → `day_std`;
     - `use_anchor` otherwise → check-in date;
     - `down_anchor` otherwise → request→decision.
   - Observation O-18: `std_day_rate` and `day_std` are both 1.00/day. The tier rates are 13.42, 2.05 and 1.53. As a plain standard rate this is plausible, so it is not a straw man.
3. **How the chair was delivered: three different computes — CLOSED.**
   - The rules now say "its own delivery (its purchase or initial rental delivery, not a loaner delivery)" in the refund day rate, the kept fee return, the kept day rate and the caster wheel-bench.
   - Every matching compute counts `purchase_delivery` + `initial_rental_delivery` for that mode: `rate_home` / `rate_courier`, `fr_courier`, `dr_home` / `dr_courier`, `cst_home`.
   - The battery, controller and drive handling allowances do not test the delivery mode.
4. **use_anchor rule vs compute — CLOSED.**
   - Tier 1 is now gated in compute on `ref_loaner` alone. The rule states its two fallbacks: "(the booking day when it has none)" for the return request, and "(no days when that request has no decision date or the chair has none)" for the repair downtime.
   - Tier 3 states "(the booking day when it has none)".
   - Compute `use_days` implements exactly these branches.
5. **Superseded clause wider than its replacement — CLOSED as worded, but the rework introduces F-4 below.** Each `replaced_by` now limits itself: "For a cash-sale chair given back / the patient keeps, which this policy governs, and only for such a chair, …".
- **Docstrings vs bodies and rules:** the tools are unchanged (same hash as rounds 2–4). No rule change concerns a tool argument. The record tools still stamp the request's decision_date and the given `loaner_issued`. The user tools book the passed amount.

### new finding (revision 5)

- **F-4 — SOURCE-POLICY RED (new, introduced by the item-5 rework): the two self-pay policies' overwrite tails each put the sibling policy's chairs back under the base clause they both retire.**
  - Passages, each in its policy's `overwrite.replaced_by` and verbatim in its `rule`:
    - (a) cash_chair_refund: "… every other refund of a self-pay sale remains under the base refund rule." and "… every other self-pay chair remains under the base return rule."
    - (b) kept_chair_adjustment: the same two tails, word for word.
    - (c) kept_chair_adjustment rule: "Accepting a price adjustment uses the sale's one refund". So a price adjustment is a refund of the sale.
    - (d) The base clauses: "A self-pay chair is refunded only when it comes back unused and complete no later than `self_pay_return_window_days` after delivery …" and "The refund is the price less `self_pay_restocking_fee_pct` percent, rounded to the cent half up; the delivery fee is never refunded."
  - Two conclusions in the same situation:
    - **A kept chair** (task 1): by (a)+(c)+(d), the chair is an "other self-pay chair" and its adjustment is an "other refund". So it is refunded only if it comes back (it does not), and any refund would be 499.00 × 85% = 424.15 with no fee returned. By (b), the adjustment is 120.41.
    - **A returned chair** (task 0): by (b)+(d), the chair is an "other self-pay chair". It came back used after four repairs and 12 days, so it fails "unused", and any refund would be 3995.00 × 80% = 3196.00. By (a), the refund is 3786.41.
  - Root cause: each tail claims every chair outside its own scope for the base clause, including the chairs the sibling policy governs. Before the rework the pair was consistent; the renderer's item 5 itself says "the two policies together are consistent".
  - Affects: `mobility.extended.yaml`, the overwrite `replaced_by` entries and rule sentences of cash_chair_refund (×2) and kept_chair_adjustment (×2). It bears on task 0 and task 1.

### rest of the re-scan (revision 5)

- **Conflicts:** apart from F-4, none. Scope, subjects and tools are unchanged.
- **Prerequisites:** the graph and the state-form sentences are unchanged and pass.
- **Order:** postings still commute; the refund reads no posting's labor.
- **Reachability and distinctness:**
  - Refund `use_anchor`: as in round 4.
  - Refund `day_rate_tier`: 13.42 / 2.05 / 1.53 / 1.00.
  - Kept `down_anchor` tiers (loaner → loaner date / undecided → booking day / decided → decision date) on task 1's customer give 120.41 / 126.53 / 123.47, which are distinct. Each is reachable for a kept chair: a loaner was used; a repair is still open; a repair finished without a loaner.
  - Kept `down_rate_tier`: 13.42 / 2.05 / 1.53 / 1.00.
- **Multi-source:**
  - Task 0: `fee_share` and the three handling allowances.
  - Task 1: `multi_service`. `fee_return` and `down_anchor` tier 1 are compound only partly.
- **Cross-difficulty:** oxygen (task 0) and pap (task 1), both seeded.
- **Observations carried:** O-1, O-5, O-10, O-12, O-13, T0-O2, T1-O1. O-11 is now closed, because the refund baseline states the use charge and its day count.

### closing_checklist (revision 5)

Written after the round-5 reveal (2026-10-13T09:21:50Z). The pre-reveal revision-5 text was not edited.

- **Status: NOT closed.** Both tasks are SOURCE-POLICY RED on F-4. Their values, trees and factors all match gold and pass.
- **Render items:** items 1–4 are closed. Item 5 is closed in its own terms, but its rework produced F-4.
- **Regressions:** both tasks were PASS in round 4 and are now NOT PASS, because of F-4 only. No other regression:
  - every value is unchanged from round 4;
  - the only new baselines are the refund at 3187.00 and the adjustment at 28.95, both still differing from gold.
- **Unchanged checks:**
  - task scopes, prerequisite graph, state-form sentences and uuid8s;
  - factor independence, baseline-stated constants and rule/compute equivalence (machine-checked);
  - gates (green, this auditor's run).

## revision_6

### entry conditions and charter_global_frozen (revision 6)

- Gates: this auditor ran `bash /tmp/erl0057_coord/gates.sh wheelchair_mobility` read-only. All 8 lines are green: check_extended rc=0 EXTENDED OK, check_task_tools rc=0 TASK TOOL CONTRACT OK, replay_tasks rc=0 REPLAY OK, check_solvability rc=0 SOLVABILITY OK, check_compute rc=0 COMPUTE OK, check_grounding rc=0 GROUNDING OK, check_cache_diff rc=0 CACHE-DIFF INFO, check_cross_fire rc=0 SCOPE OK. The audit proceeds.
- Views (`make_views.py`):

  | file | sha256 | status |
  |---|---|---|
  | `0.view.json` | 3b3715669be954ec23d77de3f01651963c8acc77c70f996f0d4a08b005c14930 | unchanged |
  | `1.view.json` | 1f92fcbd5dc590116f99f08f9a5307c9e402669aff91fa132502d856c8f09a9c | unchanged |
  | `mobility.extended.yaml` | 1b95c64fb5f1706dcc98518d359cdbf07a91326265da0afdd94ded85577c3f31 | changed from round 5's 18cbd8d0… |
  | `task_tools.py` | 2b630d1a03b80e312d9bc2089c5240f2aa92a78ad761e6c9f0160655a5168032 | unchanged |

- Fingerprints against round 5:
  - battery, controller, drive and caster are identical.
  - cash refund and kept adjustment changed. Their `compute`, `factors`, `params`, `baseline` and `prerequisite` match the round-5 text when read back. What changed is the overwrite `replaced_by` tails and the matching rule sentences.
  - kept adjustment's `cross_category` now lists oxygen beside pap. That matches `multi_service`'s `CFIELD('oxygen','status')`.
  - The base copy is unchanged.
- contamination_disclosure: GT from rounds 1–5 is known to this auditor. No round-6 task JSON was read before the freezes below.
- Machine sweep over all six policies (`r6.py`) found 0 issues:
  - every `compute_basis` value is verbatim in its rule;
  - every baseline sentence is in its rule;
  - every `replaced_by` is verbatim in its rule;
  - all four `policy_source` sentences are in state form and verbatim;
  - no factor binding reads another factor's binding;
  - no non-factor binding uses a constant outside `baseline.params`.

### F-4 (round 5) re-checked: CLOSED

The four tails now read:

- **Refund, refund clause:** "… a refund of a self-pay sale that is neither the refund of a chair given back under this rule nor the price adjustment on a cash-sale chair the patient keeps remains under the base refund rule."
- **Refund, return clause:** "… a self-pay chair that is neither given back under this rule nor kept by the patient under the price-adjustment rule for a cash-sale chair the patient keeps remains under the base return rule."
- **Kept, refund clause:** "… a refund of a self-pay sale that is neither the price adjustment under this rule nor the refund of a cash-sale chair given back remains under the base refund rule."
- **Kept, return clause:** "… a self-pay chair that is neither kept by the patient under this rule nor given back under the refund rule for a cash-sale chair given back remains under the base return rule."

Partition of the reach of the two retired base clauses:

- Every self-pay chair is a cash-sale chair. Base `mobility_self_pay_sale` is "sold outright to a self-pay patient and paid at the time of order".
- Each self-pay case falls in exactly one place:

  | self-pay case | governed by | outcome |
  |---|---|---|
  | (a) given back, used or not | cash refund (its window, custom-class exclusion and the inherited "refunded at most once") | per the cash-refund rule; the kept tails exclude it twice ("nor given back under the refund rule …", "nor the refund of a cash-sale chair given back") |
  | (b) kept, within the adjustment rule | kept adjustment | per the adjustment rule; both refund tails exclude it |
  | (c) kept, outside the adjustment's reach (no warranty repair, past the window, or custom) | the base return rule, or under the stricter reading the kept rule | base says it is never refunded because it does not come back; the kept rule says it "receives none". Both give no money, so the readings agree. |
  | (d) a later return after an adjustment | inherited "A sale is refunded at most once" and the kept rule "a chair that has received one is not refunded if it is later given back" | the two agree |
  | (e) any other refund of a self-pay sale | base refund rule | no extended policy claims it |

- No case is claimed by two rules with different outcomes. No case is sent back to base by one policy while governed by the other.
- Task worlds: task 0 is case (a) and task 1 is case (b). Neither world is sent back to base by either tail.

### render items 1–5: stay closed

- Items 1, 2 and 4: the machine sweep above, and compute is unchanged from round 5.
- Item 3: the delivery-mode wording and compute are unchanged.
- Item 5: each replacement now says what it governs and what stays under base, and together they partition the reach, as shown above.
- Tool docstrings are unchanged (same hash), and no rule change concerns a tool argument.

### rest of the re-scan (revision 6)

- Nothing else changed:
  - prerequisite graph, state-form sentences and scope;
  - factor ladders, reachability and distinctness;
  - multi-source factors: task 0 has `fee_share` and the handling allowances; task 1 has `multi_service`;
  - cross-difficulty factors: oxygen for task 0, pap for task 1.
- No new defect found.
- Observations carried: O-1, O-5, O-10, O-12, O-13, O-18, T0-O2, T1-O1.

### closing_checklist (revision 6)

Written after the round-6 reveal (2026-10-13T09:25:46Z). The pre-reveal revision-6 text was not edited.

- **Both tasks PASS all four relationships. This difficulty passes the source-layer audit.**
- Every RED from rounds 1–5 is closed:
  - F-1 and T1-F2
  - F-2 / T0-F3
  - F-3 / T0-F4
  - F-4 / T0-F5 / T1-F3
- All five render-found items stay closed.
- Neither task regressed. Every scored value is identical to round 5, and gold agrees.
- Files: `0.md` and `1.md` map one-to-one to tasks/0.json and tasks/1.json, with `_difficulty.md` alongside. Revisions 1–6 are kept, and earlier text is untouched.
- Scopes:
  - Task 0 covers battery, controller, drive and the cash refund.
  - Task 1 covers the caster claim and the kept-chair adjustment.
  - The two are disjoint and together cover all six policies.
  - All six tool uuid8s are independent.
- Trees:
  - Task 0 has 3 state-form `value_input` edges; task 1 has 1.
  - Both roots are owner=user.
  - The graph is acyclic.
- Factors:
  - Every computation has 4–6 factors, with at least 2 of effect `parameter` and at least 1 of effect `method`.
  - Every ladder has 3 or more tiers, and the tiers are distinct and reachable.
  - Every factor bears weight against an honest baseline that the rule states.
  - The all-baseline values differ from gold: 2 / 3 / 5 / 3187.00 for task 0, and 2 / 28.95 for task 1.
  - No factor reads another factor's binding.
  - Multi-source factors: task 0 has fee_share and the handling allowances; task 1 has multi_service.
  - Cross-difficulty factors: task 0 reads oxygen; task 1 reads pap.
- Gates: re-run by this auditor on this final form. All 8 lines are green. check_traceability is deferred to post-render by design.
- Observations kept: O-1, O-5, O-10, O-12, O-13, O-18, T0-O2, T1-O1.

## revision_7

- Gates: this auditor ran `bash /tmp/erl0057_coord/gates.sh wheelchair_mobility` read-only. All 8 lines are green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- The charter and tools are unchanged: `mobility.extended.yaml` is 1b95c64fb5f1706d… and `task_tools.py` is 2b630d1a03b80e31….
- The rebuilt views are unchanged: `0.view.json` 3b3715669be954ec… and `1.view.json` 1f92fcbd5dc59011….
- Every charter-global section of revision 6 is therefore carried forward by hash.
- Round-7 scope: proof text in the task JSON only.
  - The stale "books the 3746.15 refund" is fixed (see `0.md` § revision_7).
  - A full text sweep of both task files found no other claim that contradicts the current gold. Superseded figures appear only in the "(was …)" rework log.
  - Observations T0-O3 and T1-O3 note stale binding names in plumbing notes.
- **closing_checklist (revision 7):**
  - Both tasks PASS all four relationships, so the difficulty remains passed.
  - No scored value or argument changed.
  - No new defect was found and nothing regressed.
  - The revision-6 checklist otherwise stands unchanged.
