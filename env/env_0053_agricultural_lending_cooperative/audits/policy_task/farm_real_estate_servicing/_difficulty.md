# Policy-task audit — farm_real_estate_servicing / charter-global

## charter_global_frozen

- Frozen: written 2026-10-11 from 10:08Z, before any task's GT was revealed (reveal of tasks/0.json at 10:12Z). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Inputs and hashes (recomputed by the auditor; they match the coordinator's HASHES.txt):
  - `tasks/farm_real_estate_servicing/farmland.extended.yaml` sha256 `2983e79f7a219d645de72b271e920f44b8d8067aebbe5866ba91c8cff7d7ae7a`
  - `tasks/farm_real_estate_servicing/task_tools.py` sha256 `f3d8f4a1d0688634fe906f227a8a636cd23f8b262f730405a204832bd03eaa2f`
  - `.audit_views/policy_task/farm_real_estate_servicing/0.view.json` sha256 `22a405f0…763dfa`, `1.view.json` sha256 `c4a98078…53d01` (kept keys: `frozen_time`, `user_scenario`, `initial_state` only — checked)
  - `blueprint/products/farmland.yaml` (base copy), `blueprint/products/{operating,cropins,homeloan}.yaml` (cross-category parameters only), `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/blueprint.yaml`; the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `LATEST`, `_within`, `int`).
- What I could read: the charter (base + extended), the tool contracts and bodies, the schema, the shared tools.
- What was masked: every task key except the three above (`evaluation_criteria`, `computations`, `prerequisite_closure`, `solvability_contract`, `charter_scope`, `required_documents`, `design_rationale`, `db_closure*`); no other audit file; no other scenario directory. I did not grep `tasks/`.
- Entry conditions (Step 0): the coordinator sent the gate snapshot: extended / task_tools / solvability / compute / grounding / cross_fire green, cache_diff informational, traceability deferred. `replay_tasks` rc=1 and its only FAIL lines are `farmland_parcels.loan_id → homeloan_loans` dangling-FK lines. **I checked that ruling and agree with it**: `db_schema.json` declares `farmland_parcels.loan_id` as "foreign key -> farmland_loans", and in both views every `farmland_parcels.loan_id` equals the one `farmland_loans` row. So the gate's field-name FK resolution to `homeloan_loans` is a gate artefact. The masked views and their hashes were supplied. Input is complete.

### policy_conflict_scan

The charter has five extended policies, each bound to one write tool:

| policy | target_tool (owner) | computes | trigger | prerequisite |
|---|---|---|---|---|
| farmland_ext_default_interest_entry | book_default_interest_ef623284 (agent) | amount | state_due | [] |
| farmland_ext_autopay_enrolment_rate | authorize_installment_autodebit_3b801ea5 (user) | interest_rate | on_request | ← default_interest_entry (value_input, state) |
| farmland_ext_missed_late_charge | assess_late_charge_e3cbcc6c (agent) | amount | state_due | [] |
| farmland_ext_split_paydown | authorize_principal_paydown_4d1911cd (user) | amount | on_request | [] |
| farmland_ext_farmstead_release_price | release_farmstead_parcel_0569f2e2 (agent) | release_price | on_request | ← split_paydown (state_gate, state); ← missed_late_charge (value_input, state) |

Overlap scan:
- **Subjects / tables.** Two policies write `farmland_transactions` rows that later policies count. A default-rate accrual is read by autopay `default_24` and by default-interest `prior_default`. A `late_charge` fee is read by autopay `late_24`, late-charge `prior_late` and release `late_24`. Scheduled principal payments are read by the default-interest and late-charge clocks. The paydown tool writes `payment_purpose=prepayment`, which none of the `payment_purpose='scheduled'` aggregates match. The release tool writes `partial_release` fees and `release_proceeds` payments, which none of the `late_charge` or `scheduled` aggregates match. So no write of one policy silently moves another policy's input except along a declared edge, apart from the two state_due policies, which can fire wherever their state holds. Cross-fire therefore has to be judged on each task's world (done in each task file).
- **Triggers / time anchors.** The default-interest and late-charge policies both take "the most recent installment bill" and "the most recent scheduled principal payment" as their object. Their clocks are disjoint quantities: past the trigger days vs past the grace days.
- **Eligibility / terminal states.** Inherited base gates: payments only in active or nonaccrual status; autopay only in active or nonaccrual; release only in active (paid_off for payoff); one late charge per installment; one release per mortgage record; no partial release while an installment is past due; survey below 40 acres; combined LTV under `farmland_agg_combined_ltv`. No extended policy weakens them, and no tool enforces them (see action_binding_and_uuids).
- **Cross-category read boundaries.** Read-only reads: `operating_lines` (status, autodraft_enrolled, variant_name, outstanding_principal, commitment_amount, plus CPARAM `relationship_rate_discount_pct`), `cropins_policies` (status, indemnity_assigned), `cropins_transactions` (indemnity paid, payee), and `homeloan_loans` (status applied, property_parcel_number, original_principal, original_value, applied_date). No write goes outside farmland.
- **Scope partition.** The prerequisite graph has two connected components: {default_interest_entry → autopay_enrolment_rate} and {missed_late_charge, split_paydown → farmstead_release_price}. With M=2, the two components are the only partition into whole trees. They are pairwise disjoint and together cover all five extended policies. Whether each task's declared `charter_scope` matches is checked at reveal.

### rule_compute_equivalence

I swept each binding's `compute_basis` quotation against the `rule`, then swept the `rule` back against `compute`.

- **default_interest_entry.** Every binding has its quotation in the rule. bill_due/cure_on/cure_principal: "the most recent installment bill, together with the most recent scheduled principal payment". Trigger, add-on, clock start, last day and relief ladders are each stated in full. `default_days = MX(0, days_to_cure + end_offset - anchor_offset - trigger_days)` matches "days counted … less the days the later clock start takes off, less the trigger days, never below zero". `result` uses a single RND after the relief, matching "relief is applied to the unrounded figure before the single rounding". One window anchor the rule leaves open: "had no default-rate interest entry in the last 60 months" is implemented as a 60-month window ending on NOW, measured on `period_end`. It decides nothing in either world (observation O-6).
- **autopay_enrolment_rate.** All bindings are quoted. The ladders for spread, mix, autopay discount, relationship discount, young-farmer discount and stacking are each in the rule. Rounding (3 dp), floor and base rate (K 6.75) are stated. `default_24` counts default-rate entries by `period_end`, while the rule says "a default-rate interest entry in that time" and the default-interest rule dates the entry "the day it is booked" (O-6, no consequence in task 0).
- **missed_late_charge.** All bindings are quoted. `grace_credit` counts only interest payments on the bill (`paid_in_grace` comes from `interest_paid_amt`), while the ladder speaks of "the payment received within the grace period". A scheduled principal payment inside the grace period would be read as a credit by the rule but not by compute. In task 1 no principal payment falls inside grace (O-7).
- **split_paydown — RED, rounding mode.** The rule says: "The paydown is the principal balance less that most, never below zero, **rounded up to the next cent**." `result` is `0 - int(0 - (shortfall + curtailment) * 100) / 100`. In the sandbox `int` is Python `int` (check_compute.py `env["int"] = int`), which truncates toward zero. For a positive x, `-int(-100x)/100` is **floor(100x)/100, i.e. rounded down**. So compute implements a rounding mode the rule nowhere states, and it contradicts the one the rule does state. The rule also says "rounded up" of the shortfall and then "A split curtailment is added to the paydown" without saying whether the round-up applies before or after the curtailment is added. Compute rounds the sum. This is finding F-1, demonstrated on task 1.
- **farmstead_release_price.** All bindings are quoted. `share` uses RND(…,2) and `result` uses RND(…,2), matching "rounded to cents … and rounded to cents". The homesite-value method's "the value still mortgaged is adjusted by the same difference" is implemented as `net_value - home_value + home_used`. The ladders for the four additions are in the rule.
- **Factor ladders in both faces.** For every factor of all five policies, each `ladder` tier is a rule sentence and a branch of its `decides` binding, and each branch of the binding is a stated tier (checked one by one; the ladder_shape fork count matches the tiers − 1 in every factor). There is no rule-only tier and no compute-only tier.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: five policies, five distinct tools. Each pair is claimed once.
- uuid8 tails: `ef623284`, `3b801ea5`, `e3cbcc6c`, `4d1911cd`, `0569f2e2`. All distinct, with no shared prefix, no sequential pattern and no copied tail.
- Tool bodies: each body only creates rows and updates balances. None reads a gate, refuses, errors or hints on an unmet prerequisite: `book_default_interest` creates an accrual row and raises accrued_interest; `authorize_installment_autodebit` updates three fields; `assess_late_charge` creates a fee and raises fees_due; `authorize_principal_paydown` creates a prepayment and lowers principal; `release_farmstead_parcel` creates the release, the proceeds and the fee, and updates principal, collateral and fees. **The tool layer judges no prerequisite.**
- Docstrings: none names another tool or states a position in a sequence. The only "before" wording ("read from the farm real estate loan lookup before the call") is about reading the loan id, not about another problem. Every docstring describes one business reading.
- Docstring examples (observation O-1): `book_default_interest_ef623284.rate_applied` gives "e.g. 2.000", and `authorize_installment_autodebit_3b801ea5.interest_rate` gives "e.g. 6.150". Whether these coincide with a task's scored value is a world fact, judged in 0.md.

### prerequisite_graph

- Every policy fills in `prerequisite` (three with `[]`).
- Each `problem` points at an extended policy in this file, never at a base policy and never at itself.
- The graph is acyclic: two edges into release, one into autopay, no back edges.
- `policy_source` is verbatim in the blocked policy's own rule for all three edges (whitespace-normalised check), and in none of the depended-on rules.
- `form: state` on all three edges, with no `fallback_reason`, which is consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all three edges.
- `kind` / `gate`:
  - autopay ← default_interest: value_input, gate `autopay_disc`, a compute binding fed through `default_24`.
  - release ← missed_late_charge: value_input, gate `record_add`, a compute binding fed through `late_24`.
  - release ← split_paydown: state_gate, gate `farmland_loans.principal_balance`. The release policy has no `eligibility` block; the gate is carried by the rule sentence alone and the field is real (observation O-3).
- `condition` matches the sentence's strength and scope on all three edges:
  - "for every installment bill whose completing scheduled payment came more than its default-interest trigger days after the due date" restates "every installment that was paid in full more than its default-interest trigger days after it fell due";
  - "for every installment bill completed after its grace period" restates "every installment that was paid in full after its grace period";
  - the principal gate restates the release gate sentence.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` text.

### prerequisite_sentences

All three edges pass the four-point test: an ordering connective, a record-visible state, no tool/id/snake_case token, and the strength of the `condition`.

1. **Autopay ← default interest.** Sentence: "The re-set rate is fixed only after the records carry a default-rate interest entry for every installment that was paid in full more than its default-interest trigger days after it fell due." "only after" is the connective. "records carry a default-rate interest entry" is a state named in the finder's words: `find_farmland_transactions` shows "whether at the contract or default rate". Only `book_default_interest_ef623284` writes `rate_basis=default_rate`, so exactly one write brings the state about.
   Derivation: the reader takes the most recent bill and its completing payment from the history. They test whether it completed more than its trigger days late, where "its default-interest trigger days" is resolved from the default-interest rule's trigger ladder. They then find the policy whose rule books "its own interest entry marked as default-rate interest" (default_interest_entry). Only one reading.
2. **Release ← split paydown.** Sentence: "A homesite release is not recorded until the principal standing on the loan, less the release price at the product's standard release premium, already sits within the post-split loan-to-value limit of the parcels that stay mortgaged." "not … until" is the connective. "principal standing on the loan" is a state: `principal_balance` is shown by `find_farmland_loans`. The only write that lowers principal before the release is `authorize_principal_paydown_4d1911cd`; the release tool's own principal reduction is the blocked write.
   Derivation: "post-split limit" leads to the paydown rule, which defines the limit and its three adjustments and states the paydown that "leaves the loan within the post-split limit once the release price is applied".
   One wording risk, recorded as observation O-2 because its consequence on the scored solution cannot be demonstrated (see 1.md): "the release price at the product's standard release premium" swaps only the premium percentage. The release rule's own homesite-value method (application value 322,000 vs appraisal 268,000) would still apply under a literal reading, while the paydown rule figures the release price on "the appraised values at mortgage".
3. **Release ← missed late charge.** Sentence: "The release price is set only once the records carry the late charge owed on every installment that was paid in full after its grace period." "only once" is the connective. The late-charge entry is a record-visible state, and only `assess_late_charge_e3cbcc6c` writes `fee_code=late_charge`, so exactly one write. Derivation: the reader takes the most recent bill, sees completion after the grace days, and finds the policy that assesses "a late charge that should have arisen … and was never assessed". Only one reading.

Second wording / depended-on restatement: the split-paydown rule (the depended-on side) states the same order again: "the paydown the member makes from their own funds **before the release**". It is not the blocked rule's sentence and it states no conflicting order: it is the same direction as the declared edge, so neither order nor terminal state can differ. It is a second wording of the dependency on the depended-on side, and it also self-triggers the paydown on the member's split request ("When a member asks to split the farmstead…"). Recorded as observation O-4.

No other extended rule states a cross-problem order. No base sentence grounds any of the three edges: every edge rests on an extended sentence.

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry.

- **default_interest_entry vs farmland_installment_billing.**
  - Changed and declared: the default sentence ("While an installment is past due more than default_interest_trigger_days … until the day every past-due installment is paid") is superseded whole. That covers the trigger (60 → ladder), the add-on (contract + 3.0 → add-on-only ladder), the period start (day after threshold → clock-start method) and the period end (payment day → channel method). The relief multiplier is new matter on the same quantity, inside the replaced sentence's scope.
  - Followed: daily accrual on principal actual_365, the rounding once to cents, and the installment rows.
  - Undeclared conflict: none.
- **autopay_enrolment_rate vs farmland_rate_setting and farmland_autopay_enrolment.**
  - Superseded and declared: "Enrolling in or cancelling autopay adds or removes the autopay discount from that day without restarting any fixed period." and "The autopay discount of farmland_rate_setting is added or removed from the change date; moving the debit…".
  - Followed: own instruction and last four as given; active/nonaccrual gate; debit on due dates.
  - Base sentences scoped "At closing and at a rate conversion" (starting rate, spread, autopay + ybs capped) do not govern an autopay change, so no conflict.
  - Partial, undeclared tension: "The young-farmer discount, once given, stays for the fixed period … and is re-tested only at a conversion." The extended rule re-tests the young-farmer discount at an autopay change (loan-age tiers 0.5 / 0.25 / 0). Recorded as observation O-5; in task 0 both readings give 0.5.
  - Also O-5: the base `parameter_schema` defines `rate_discount_cap_pct` as "Most the autopay and young-farmer discounts may take off together". The extended stacking tier 1 adds the young-farmer discount outside the cap. parameter_schema is not a policy and cannot appear in `overwrite`.
  - Later conflict with no scored consequence (O-5): `farmland_rate_adjustment_rule` moves a variable rate at the next base-rate date with `variable_rate_spread_pct`, not with the collateral spread tier.
- **missed_late_charge vs farmland_evt_late_charge** (+ seven fee-bearing refs). The amount sentence is superseded and declared. Followed: the grace arising (day 0, after the 15th day), one per installment, none in nonaccrual or on fees or protective advances, and the waivers. The other seven refs govern other fee codes (returned payment, prepayment, conversion, release, protective advance, flood, assumption), so no conflict.
- **split_paydown vs farmland_payment_application, farmland_prepayment, farmland_partial_release.**
  - Superseded and declared: the partial_release sentence "The release price is applied to principal as release proceeds … any excess being paid down at the same time."
  - Inherited:
    - payment_application's "prepayment only when no installment is past due";
    - prepayment's fee on prepayments and release proceeds beyond the free allowance. The variable product has an empty schedule and 100 % free; other products would carry a fee no task tool can book. That is a latent gap with no consequence in task 1 (observation O-8).
  - Observation O-8: the superseded clause also carried "The release price is applied to principal as release proceeds on the release date". The replacement does not restate it, though the base event trigger and the release tool both still do it.
- **farmstead_release_price vs farmland_agg_combined_ltv, farmland_partial_release, farmland_payoff.**
  - Superseded and declared: the release-price sentence ("greater of … ; for a farmstead split the release price is the premium amount alone").
  - Inherited: status, once per parcel, the partial_release request, another parcel still mortgaged, the survey below 40 acres, the fee, no past-due installment, and the combined LTV test ("may not exceed the lowest max_ltv_after_release_pct"). The combined test is not superseded by any extended policy. A per-task check that it holds after the scored release is in 1.md.
- Disguised forms: no anonymous intermediate factor outside a declared superseded clause; no 0/1 existence multiplier on an amount base already fixed; no dropped base branch inside the scope of the claimed writes. No rule or basis calls a base output a "wrong value".

### factor_ladders

I judge labels against the framework's own method definition (check_compute.py docstring: "a multiplier on an intermediate or on the result, the day-count or window convention, the anchor the clock starts from … any way the calculation genuinely varies"). Multipliers and period-boundary conventions are therefore honest `method` labels.

| policy | factor | effect | tiers | distinct outcomes | multi-source (semantic) | cross_difficulty |
|---|---|---|---|---|---|---|
| default_interest | trigger_by_seasoning_and_record | parameter | 3 (75/45/product 60) | yes | yes (loan age × default history) | — |
| | addon_by_cure_speed | parameter | 3 (2.0/4.0/product 3.0) | yes | no | — |
| | clock_start_after_interest_paid | method (anchor) | 3 (grace end / payment day / due date) | yes | partly | — |
| | last_day_by_payment_channel | method (period-end convention) | 3 (day before / +2 / that day) | yes | no | — |
| | disaster_relief_from_assigned_indemnity | method (multiplier) | 3 (½ / ¾ / full) | yes | yes (cropins indemnity × installment share) | cropins |
| autopay | spread_by_collateral_coverage | parameter | 3 (0.10/0.50/product) | yes | no | — |
| | collateral_mix_adjustment | parameter | 3 (−0.05/+0.10/0) | yes | no | — |
| | autopay_discount_by_record | parameter | 3 (0.15/0.05/product) | yes | yes (fee rows × accrual rows) | — |
| | relationship_discount_from_operating_credit | parameter | 3 (CPARAM/0.05/0) | yes* | single-record conjunction | operating |
| | young_farmer_land_discount | parameter | 3 (product/0.25/0) | yes | yes (StartRight line × farm loan date) | operating |
| | discount_combination_by_program | method (stacking) | 3 | yes | no | operating |
| missed_late_charge | late_charge_percentage_by_record | parameter | 3 (3.0/5.0/product 4.0) | yes | no (tier 2 single) | — |
| | good_faith_payment_credit | parameter | 3 (1.0/0.5/0) | yes | yes (payment date/amount × bill due × installment) | — |
| | operating_relationship_credit | parameter | 3 (0.25/0.10/0) | yes | single-record conjunction | operating |
| | crop_season_credit | parameter | 3 (0.5/0.25/0) | yes | no | — |
| | lateness_multiplier | method (multiplier) | 3 (½ / 1½ / 1) | yes | no | — |
| split_paydown | limit_by_operating_leverage | parameter | 3 (−5/−10/0) | yes | yes (drawn active line ∧ no stressed line / suspended ∨ matured line) | operating |
| | limit_by_collateral_mix | parameter | 3 (−5/+5/0) | yes | no (tier 1 single) | — |
| | limit_by_crop_insurance | parameter | 3 (+2.5/+1.0/0) | yes | single-record conjunction (tier 1) | cropins |
| | split_curtailment_by_home_financing | method (adds a curtailment component on the pre-paydown release price, or none) | 3 (10 %/5 %/none) | yes | no | homeloan |
| release | premium_by_late_record | parameter | 3 (+15/+10/0) | yes | no | — |
| | premium_by_homesite_size | parameter | 3 (+10/+5/0) | yes | no | — |
| | premium_by_release_history | parameter | 3 (+10/+5/0) | yes | no | — |
| | premium_by_loan_seasoning | parameter | 3 (+5/+2.5/0) | yes | no | — |
| | homesite_value_by_newest_appraisal | method (valuation source) | 3 | yes | yes (homesite parcel × homeloan application, date) | homeloan |

Counts per computation, all within bounds:

| computation | factors | parameter | method |
|---|---|---|---|
| default_interest | 5 | 2 | 3 |
| autopay | 6 | 5 | 1 |
| missed_late_charge | 5 | 4 | 1 |
| split_paydown | 4 | 3 | 1 |
| release | 5 | 4 | 1 |

Per task component:

| component | multi-source factors | cross-difficulty factors | categories read |
|---|---|---|---|
| {default_interest, autopay} | trigger, relief, autopay record, young-farmer | relief, relationship, young-farmer, combination | cropins, operating |
| {missed_late_charge, split_paydown, release} | good-faith credit, operating leverage, homesite value | relationship credit, leverage, crop insurance, curtailment, homesite value | operating, cropins, homeloan |

- Every ladder is stated in prose in its rule (condition and value or method), and every ladder is implemented in compute. Every fall-through equals the policy's `baseline.rule` statement for that input. Every sentence of each `baseline.rule` is a sentence of the rule (verbatim check).
- Every condition is one an ag lender plausibly weighs for that quantity: seasoning and record, cure speed, payment channel, assigned crop indemnity, LTV, collateral mix, payment history, operating relationship, harvest/planting season, homesite size, release history, loan seasoning, newest appraisal, operating leverage and crop insurance cover. None restates the policy's own scope.
- Observation O-9:
  - `relationship_discount_from_operating_credit`'s tier 1 value is CPARAM `relationship_rate_discount_pct`, which is 0.0 for an Agribusiness Revolving Line. For that product, tier 1 equals the fall-through and sits below tier 2 (0.05).
  - On the 15/25-year fixed products (`autopay_rate_discount_pct` = `rate_discount_cap_pct` = 0), the autopay ladder collapses to 0 through `MN(autopay_disc, cap)`.
  - Neither arises in either task world.
- Observation O-10: the machine multi-source test (`ladder_shape`) credits `operating_relationship_credit` and `limit_by_crop_insurance`, whose tier-1 conditions are two fields of one record. The semantic multi-source floor is still met in both components by the factors marked "yes" above.

### findings

- **F-1 — SOURCE-POLICY RED (rule/compute equivalence), farmland_ext_split_paydown.**
  - Symptom: the rule says "rounded up to the next cent", but compute `result: "0 - int(0 - (shortfall + curtailment) * 100) / 100"` rounds down. With Python `int` truncation, −int(−100x)/100 = floor(100x)/100. The round-up point is also unstated relative to the curtailment ("…rounded up to the next cent. … A split curtailment is added to the paydown").
  - Root cause: a rounding idiom that is a ceiling only under floor-division semantics, written with `int`.
  - Evidence: farmland.extended.yaml lines 2061 (rule) and 2116 (compute); check_compute.py `build_env` maps `"int": int`.
  - Consequence: any world where the shortfall + curtailment has a sub-cent remainder gets a scored paydown 0.01 below the rule's figure.
  - Bears on task 1 (consequence demonstrated in 1.md).
- **O-1 — tool docstring examples.** `rate_applied` "e.g. 2.000" and `interest_rate` "e.g. 6.150". Bears on task 0 (see 0.md).
- **O-2 — homesite value in the release gate is left open.** The release state-gate sentence leaves open which homesite value "the release price at the product's standard release premium" uses. Bears on task 1.
- **O-3 — gate on a field, no eligibility block.** The release state_gate edge names `farmland_loans.principal_balance` as its gate, and the release policy declares no `eligibility` entry. The gate lives only in the rule sentence. No consequence.
- **O-4 — paydown rule restates the order.** The depended-on split_paydown rule restates the order ("before the release") and self-triggers on the split request. Same order as the declared edge, so no demonstrable consequence. Bears on task 1.
- **O-5 — rate-setting tensions.** Undeclared tension with base rate_setting ("re-tested only at a conversion"), with the parameter_schema definition of `rate_discount_cap_pct`, and with the future base-rate move in `farmland_rate_adjustment_rule`. Bears on task 0, where no scored consequence is demonstrable (see 0.md).
- **O-6 — dating of default-rate entries.** Default-rate entries are dated by `period_end` in the `default_24`/`prior_default` windows, while the rule dates the entry by booking day. No consequence in task 0.
- **O-7 — principal payment in grace.** `grace_credit` ignores a scheduled principal payment inside the grace period, while the rule's wording ("the payment received within the grace period") would include it. No consequence in task 1.
- **O-8 — latent prepayment-fee gap.** On products with a non-empty prepayment schedule, the paydown and release proceeds would carry an inherited prepayment fee that no task tool books. The superseded clause also drops the explicit release-proceeds sentence. No consequence on the variable product in task 1.
- **O-9 — collapsing tiers.** The CPARAM tier collapses for an Agribusiness line, and the autopay ladder collapses on the 15/25-year fixed products. Not in either world.
- **O-10 — machine multi-source credit** for single-record conjunctions. The semantic floor is met.

## closing_checklist

Written 2026-10-11 after both reveals. Everything above this heading was frozen before any reveal (sha256 `30d8a5f1…d326` at reveal time).

- **Audit files.** `0.md` and `1.md` correspond one-to-one with tasks 0 and 1. Each carries a frozen section and a comparison. This is the first revision, so there are no older revisions.
  - task 0: PASS on all four relationships.
  - task 1: **SOURCE-POLICY RED** and **SOURCE-TASK RED** (F-1).
- **Coverage and scope.** All five extended policies are covered: task 0 has {default_interest_entry, autopay_enrolment_rate}; task 1 has {missed_late_charge, split_paydown, farmstead_release_price}. The `charter_scope` fields of both tasks match the graph components derived pre-reveal. The two scopes are pairwise disjoint, each spans its whole tree, and the task tools are closed (two and three tools respectively). The uuid8s are independent and frozen (§ action_binding_and_uuids).
- **Trees.**

  | task | prerequisite problems | value_input edges | user-owned problem | cycles |
  |---|---|---|---|---|
  | 0 | 1 | 1 | the root | none |
  | 1 | 2 | 1 | the paydown | none |

  The whole graph is a DAG with no cross-task edges.
- **Factors.** Every computation has a self-sufficient baseline and 4–6 factors with at least 2 parameter and 1 method. Every ladder has at least 3 tiers stated in the rule, and every factor bears weight on its task's world (figures in each task's `factor_weight`, matched against GT). Each task has at least 1 multi-source factor and at least 1 cross-difficulty factor. The baseline alone gives a definite non-gold number in all five computations.
- **Not satisfied:** policy self-consistency for split_paydown (F-1: compute floors where the rule says "rounded up"), with a second defensible scored paydown in task 1.
- **Gates.** The instantiation-stage gates on a final form were not re-run, because the difficulty does not close: F-1 is open. The only gate snapshot is the coordinator's (Step 0), which did not catch F-1 because check_compute validates `expected` against the same flooring compute.
- **Difficulty verdict:** **does not pass the source-layer audit.** Task 0 PASS; task 1 SOURCE-POLICY RED + SOURCE-TASK RED.

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-11 11:53Z, before tasks/0.json and tasks/1.json of round 2 were opened. Auditor: the same independent auditor as round 1.
- **Both shared inputs changed, so every charter-global section is re-derived in full; none is carried forward.**
  - `farmland.extended.yaml`: round-1 `2983e79f…d7ae7a` → now `784b53034b041626ed2339fd7dd311afa0dc35413bd509718e74f85916c9e8af`.
  - `task_tools.py`: round-1 `f3d8f4a1…eaa2f` → now `bed40b8cfed2ecbcd0b3b2b70d644bab58e5ccba4398799a3f75cfa5f79ad645`.
  - The base copy is still verbatim equal to `blueprint/products/farmland.yaml` (re-checked).
  - Views unchanged: `0.view.json` `22a405f0…763dfa` and `1.view.json` `c4a98078…53d01` (recomputed).
- Masked as in round 1. The round-2 task JSONs were not opened before this freeze.
- contamination_disclosure: I read the round-1 GT of both tasks in round 1. Everything below is re-derived from the round-2 charter, the round-2 tools and the unchanged worlds; nothing is copied from round-1 GT.
- Gate snapshot (coordinator, after rework): EXTENDED / TASK TOOL CONTRACT / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, CACHE-DIFF INFO, REPLAY NOT OK with only the loan_id FK lines (the same artefact I verified in round 1). Input is complete.

### What changed in the charter (located by reading the round-2 file against the round-1 text quoted in this report)

| item | round-2 artifact | status |
|---|---|---|
| F-1 | split_paydown rule adds: "The curtailment is added to the shortfall before any rounding, and the sum of the two is rounded up to the next cent once; neither part is rounded on its own." Compute now `cents_due = (shortfall + curtailment) * 100` and `result = RND((int(cents_due) + (1 if cents_due - int(cents_due) > 0.000001 else 0)) / 100, 2)`, a true ceiling to the cent with a 10⁻⁶-cent float tolerance. | rule and compute now agree in mode and point |
| O-1 | the "e.g. 2.000" (`rate_applied`) and "e.g. 6.150" (`interest_rate`) examples are removed; no docstring carries an example value | closed |
| O-2 | release gate sentence now reads "…less the release price at the product's standard release premium **on the homesite's appraised value at mortgage**…"; `condition` updated the same way; `policy_source` is verbatim in the rule | closed |
| O-4 | the paydown rule and its `replaced_by` no longer say "before the release" | closed |
| O-5a | new `overwrite` on farmland_rate_setting declares "The young-farmer discount, once given, stays for the fixed period … re-tested only at a conversion." → "The young-farmer land discount follows the member's StartRight Operating Line" (the superseded clause is verbatim in base; the replacement is a rule fragment) | closed |
| O-5b | `parameter_schema.rate_discount_cap_pct` ("Most the autopay and young-farmer discounts may take off together") vs stacking tier 1 | unchanged; base dictionary, cannot take an `overwrite`; observation stands |
| O-5c | `farmland_rate_adjustment_rule` future base-rate move uses `variable_rate_spread_pct` | unchanged; no scored consequence; observation stands |
| O-6 | `prior_default` (default interest) and `default_24` (autopay) now use `date_field='effective_date'`, matching "dated the day it is booked" | closed |
| O-7 | late-charge rule now "A good-faith **interest** payment … the amount counted being the interest paid on the installment when the most recent interest payment was received within the grace period"; the ladder `when` texts say the same | closed (rule matches compute) |
| O-8a | split_paydown's superseded clause is narrowed to "after which principal may not exceed … at the same time", so "The release price is applied to principal as release proceeds on the release date" stays in force | closed |
| O-8b | latent prepayment fee on non-variable products (no task tool books it) | unchanged; observation stands (no task world reaches it) |
| O-9a | relationship discount now "never less than 0.10" (`MX(K('relationship_autodraft_floor_pct'), CPARAM … or 0)`), so the Agribusiness tier no longer equals the fall-through or falls below tier 2 | closed |
| O-9b | on the 15/25-year fixed products, `other_rate` = `MN(autopay_disc, cap 0)` still collapses the autopay ladder to 0 | unchanged; observation stands (latent) |
| O-3, O-10, O-11 | unchanged, as the reworker claims | observations stand |

The reworker's "O-5, O-8, O-9 closed" holds only for the parts marked closed above. O-5b/c, O-8b and O-9b remain latent observations with no consequence in either world.

### policy_conflict_scan (revision 2)

Re-run on the round-2 charter.
- Policies, tools, owners and triggers are unchanged from round 1. The graph has the same two components, {default_interest → autopay} and {missed_late_charge, split_paydown → release}.
- The scope partition is unchanged, disjoint and complete.
- No write of one policy moves another's input except along a declared edge. The `effective_date` re-dating moves nothing across policies.

### rule_compute_equivalence (revision 2)

I re-swept every binding of all five policies against its `compute_basis` quotation and the rule, and swept back.
- **split_paydown.**
  - `cents_due` and `result` implement exactly "added … before any rounding … the sum rounded up to the next cent once; neither part is rounded on its own".
  - The baseline sentence "The paydown is the principal balance less that most, never below zero, rounded up to the next cent" (no curtailment) is consistent: the shortfall alone rounded up.
  - The 10⁻⁶-cent tolerance is a float guard below any money amount. Observation O-13, no consequence.
  - **F-1's rule/compute mismatch is closed.**
- **Default interest and autopay.** The windows are now dated by booking date (`effective_date`), consistent with "dated the day it is booked". The relationship-discount floor is stated in the rule and implemented in compute.
- **Missed late charge.** The good-faith credit is now worded on interest, matching compute.
- **Release.** No change except the gate sentence, which compute does not implement: it is a gate, not a binding.
- All ladders are in both faces, fork counts ≥ tiers − 1, and every `baseline.rule` sentence is in its rule (machine re-check).

### action_binding_and_uuids (revision 2)

- The five `(target_tool, computes)` pairs are unchanged and unique. The uuid8s are unchanged, independent and frozen.
- Tool bodies are unchanged in effect: no gate, error or hint in any body (grep of every `if`).
- Docstrings: no example values, no other tool named, no sequence position. The only "before the call" wording refers to reading the loan id.

### prerequisite_graph and prerequisite_sentences (revision 2)

- The three edges are unchanged in `problem`, `kind`, `gate`, `form` and `resolved_by`.
- `policy_source` is verbatim in the blocked rule and absent from the depended-on rules.
- The graph is acyclic. No `fallback_reason` (all state form).
- **Edge 2's sentence** now names the measure fully: standard premium on the homesite's appraised value at mortgage. That is the same measure the paydown rule's formula uses, so the reading is single. The second wording in the paydown rule (O-4) is gone.
- The `condition` matches the sentence.
- Edges 1 and 3 are unchanged and pass the four-point test.

### override_declarations (revision 2)

Same sweep as round 1, plus the new declaration.
- The rate_setting "re-tested only at a conversion" sentence is now declared superseded for the autopay change. The young-farmer re-test at an autopay change is therefore declared.
- split_paydown's narrowed superseded clause keeps the release-proceeds sentence in force.
- No undeclared conflict with a scored consequence remains: O-5b/c are dictionary or future-event tensions with no scored effect.

### factor_ladders (revision 2)

- Factor sets, labels, tier counts and per-task counts are as in round 1.
- relationship_discount's tier 1 value is now max(CPARAM, 0.10): distinct from tier 2 (0.05) and from the fall-through (0) for every operating product.
- Every ladder is in the rule and in compute; tiers are distinct in outcome; the conditions are realistic.

### findings (revision 2, charter-global)

- **F-1: closed** at the charter level (rule/compute rounding mode and point now agree; demonstrated per task in 1.md revision_2).
- **No new charter-global RED.**
- Observations O-3, O-5b, O-5c, O-8b, O-9b and O-10 stand (latent, no consequence). New observation **O-13**: the `> 0.000001` cent tolerance in the ceiling, a float guard with no consequence.

### closing_checklist (revision 2)

Written after the round-2 reveals.
- **Files.** One-to-one task files exist, each with a `revision_2` frozen section and comparison appended. The round-1 text is untouched. Each round-2 comparison carries PASS on all four relationships for task 0 and task 1.
- **Coverage.** All five extended policies are covered. The scopes ({default_interest, autopay}, {missed_late_charge, split_paydown, release}) are pairwise disjoint and complete. Task tools are closed. The uuid8s are unchanged, independent and frozen.
- **Trees.**
  - task 0: 1 prerequisite problem, 1 value_input edge, user root.
  - task 1: 2 prerequisite problems, 1 value_input edge, user paydown.
  - No cycle; the whole graph is a DAG.
- **Factors.** Every computation has a self-sufficient baseline giving a definite non-gold number (1,707.52, 6.900, 549.77, 0.00, 200,294.08) and 4–6 factors with ≥ 2 parameter and ≥ 1 method. Every factor moves its task's scored value. Each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor, with seeded rows.
- **Gates on the final form:** the coordinator's post-rework snapshot is cited. EXTENDED, TASK TOOL CONTRACT, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK; CACHE-DIFF is INFO; REPLAY is det/nonvac/err-free with closure 48/48 and 41/41, its only FAIL lines being the loan_id FK artefact verified in round 1.
- **Round-1 RED status:** F-1 closed. No new RED. No regression.
- **Reworker claims checked against the artifacts:**
  - O-1, O-2, O-4, O-6, O-7 and O-12 are closed in full.
  - O-5, O-8 and O-9 are closed only in part (O-5a, O-8a, O-9a). O-5b, O-5c, O-8b and O-9b stand as latent observations: they live in base text or on products no task reaches, so they have no consequence.
  - O-3, O-10 and O-11 are unchanged, as the reworker claimed.
- **Difficulty verdict (round 2): passes the source-layer audit.** Task 0 PASS; task 1 PASS.
