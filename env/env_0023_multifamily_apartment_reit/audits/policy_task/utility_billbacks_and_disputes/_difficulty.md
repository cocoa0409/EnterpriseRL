# Policy-task audit — utility_billbacks_and_disputes / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), round 1. Did not author any artifact of this difficulty.
- Freeze time: 2026-09-24T18:08Z. Written before any task's GT was revealed. Nothing in this section is derived from a revealed GT.
- Frozen inputs:
  - `tasks/utility_billbacks_and_disputes/utility.extended.yaml`: sha256 `695833e4c8ed4f23aeb2898f95d1cd4414f67fe6b1a08b9df0e5b43768c2a26a`. Matches the brief.
  - `tasks/utility_billbacks_and_disputes/task_tools.py`: sha256 `d4280f88afca0b8fd505cf9bda76fa39ea816fbd27679bee8c0c0292b8c55e7a`. Matches the brief.
  - `blueprint/products/utility.yaml`, `blueprint/blueprint.yaml` (difficulty entry), `blueprint/db_schema.json`, `blueprint/share_tools.py`, and `erlbench/` plus `skills/erl-task-instantiate/scripts/check_compute.py` for the DSL semantics.
- Permitted fields: the whole charter, the tool module, the blueprint, and the masked task views (`frozen_time`, `user_scenario`, `initial_state` only). The world facts cited here are used only to name charter-level shapes.
- Masked fields: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, the closure fields, and every other audit directory.
- Entry conditions (Step 0): the brief supplies the gate snapshot. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all show rc=0 and OK lines. check_traceability is deferred to the render stage, as stated. Masked views are supplied with hashes, and I re-hashed both views and they match. Input is complete.
- Base copy: every key of `blueprint/products/utility.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) compares equal to the same key in `utility.extended.yaml` (yaml load plus `==`). The base section is verbatim.

### policy_conflict_scan

The charter has eight extended policies, one target tool each.

| policy | subject | trigger | target_tool (owner) | computes | base refs |
|---|---|---|---|---|---|
| utility_ext_gas_trueup_line | utility_usage_billback | state_due | post_gas_trueup_line_465c860d (agent) | amount | submetered_usage |
| utility_ext_electric_estimate_line | utility_usage_billback | state_due | bill_estimated_electric_line_1c085b40 (agent) | amount | submetered_usage |
| utility_ext_undisputed_balance_payment | utility_payment | on_request | pay_undisputed_utility_balance_990e05bb (user) | amount | agg_household_balance, evt_payments |
| utility_ext_leak_adjustment_credit | utility_bill_adjustment | on_request | credit_leak_adjustment_a9c6c674 (agent) | credit_amount | adjustments_and_disputes |
| utility_ext_final_package_fee | utility_flat_charge | state_due | post_final_package_fee_c766a545 (agent) | amount | flat_and_package, final_bill_and_close |
| utility_ext_final_water_overage | utility_package_overage | state_due | post_final_water_overage_2681eca1 (agent) | amount | flat_and_package |
| utility_ext_final_electric_overage | utility_package_overage | state_due | post_final_electric_overage_b496acda (agent) | amount | flat_and_package |
| utility_ext_moveout_utility_payment | utility_payment | on_request | pay_moveout_utility_share_762d5a93 (user) | amount | agg_household_balance, evt_payments |

- **Overlapping subjects.**
  - The two usage-line policies are separated by service and read basis. The gas policy covers a gas period closed by an actual read after estimates. The electric policy covers an electric period that closed with no read. The two conditions are disjoint.
  - The two payment policies are separated by account state and ground. The undisputed payment covers an account with a line under a submitted dispute ("while a bill line on it stands under a dispute still in submitted status"). The move-out payment covers "an account in final billing". The two could only meet on a final_billing account that also carries a submitted dispute. Neither task world has that combination, so this is an observation only (O-1).
  - The two overage policies are separated by service.
- **Triggers and time anchors.** Every state_due policy uses the same anchor: "issued at the first bill issue after ..." and "owed from that bill issue day until it stands on the account". The windows are all "fewer than N whole months before the billing/decision/payment date". The DSL implements this as `0 <= MONTHS(date, NOW) < N`, where MONTHS is whole months with a day-of-month correction. Rule and compute agree.
- **Eligibility inherited from base.** No extended policy weakens a base eligibility:
  - active or final_billing state gates;
  - the 60-day dispute window;
  - once per reason;
  - dispute-only correction;
  - certified-funds instrument restriction.
- **Cross-category read boundaries.** Each policy's `cross_category` declares exactly the lease, term and deposit fields its compute reads through CFIELD/XCOUNT/XSUM. check_extended confirms this, and I verified it by reading. No read goes outside the declarations.
- **Terminal states.**
  - Each agent write adds one bill line and moves `balance_due`.
  - The leak credit also marks the suspected-leak dispute `credited`.
  - No policy closes an account or changes a lifecycle state.
  - The base close sentence ("each account is closed once its final bill has been issued and its balance paid or carried there") does not fire inside either task. The move-out residue is carried at final accounting under the deposit charter, not now.
- **Scope exclusivity and coverage** (inferred from the charter graph and the personas; `charter_scope` is masked until reveal):
  - Tree A: leak ← undisputed payment ← {gas true-up, electric estimate}.
  - Tree B: move-out payment ← {final package fee, final water overage, final electric overage}, with the water and electric overages each ← final package fee.
  - The two trees are disjoint and together cover all eight policies. I confirm this against `charter_scope` in each task's comparison.

### rule_compute_equivalence

Check 2, run over all eight policies. Every compute binding has a `compute_basis` quotation that I located in the rule. Every tier of every `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and every branch of each binding is a stated tier. I found no tier that exists in only one of the two. Residual rule/compute gaps follow. None of them changes a value in either task world (see each task file), so all are observations.

- **O-2: SUM rounds usage aggregates to 2 decimals.** The DSL's `SUM` returns `round(s, 2)` (`check_compute.py` build_env). The rule rounds aggregated usage "to 3 decimals" (gas true-up usage, usual water usage, electric averages). Where a read carries 3 decimals, compute truncates before the rule's rounding point. In both worlds every read has at most 2 decimals (water 2, gas 1, electric 0), so there is no consequence here.
- **O-3: RND is Python `round`, not half-up.** The rules say "rounded half up to the cent". The two differ only on an exact binary tie. I checked every rounding point in both worlds and none sits on a tie that resolves differently. Task 1's priced water overage 1 + 1.147×1.25 = 2.43375 gives 2.434 under half-up and 2.434 in the DSL.
- **O-4: "other than the read of the disputed period" is computed by subtraction.** `ub_payable` and `lk_usual` compute this as `(S − disputed_line_usage)/(N − 1)`. That equals the rule's mean only if the disputed period's read lies inside the window and its usage equals the disputed line's usage. Both hold in task 0: read 2026-01-31, 11.06, equal to line 71950a27's 11.06.
- **O-5: `ub_deposit` adds a filter the rule does not state.** The compute uses `CFIELD('deposit','deposit_held', status='held') or 0`, but the rule says only "the cash deposit held on the lease's security deposit account". A deposit in `move_out_review` still holds cash, yet the compute would read 0. In task 0 the deposit status is `held`, so there is no consequence.
- **O-6: `gt_cum` sums every gas read in the 3-month window.** The rule asserts these reads "are the actual read and the estimated reads it follows". Compute and rule diverge only if the window also held an earlier actual read. In task 0 the window holds Nov (est), Dec (est) and Jan (actual) only.

### action_binding_and_uuids

- **Claims.** Each `(target_tool, computes)` pair is claimed by exactly one policy (8 distinct tools, 8 policies).
- **Docstrings.** No docstring states a sequence position, names another tool, or checks a condition. The only ordering words are:
  - "after the line/payment/credit" in the Returns sections, which describe the tool's own balance effect;
  - the move-out payment's summary line "... after you have moved out", which describes a real-world status of the resident, not another tool (O-7).
- **Tool bodies.** No function body refuses, errors or hints on any policy condition. Each body is `find` → `create` → `update(balance_due)`, and the leak tool additionally marks disputes `credited`. The module docstring states this explicitly.
- **uuid8s.** 465c860d, 1c085b40, 990e05bb, a9c6c674, c766a545, 2681eca1, b496acda, 762d5a93. There are no shared prefixes, sequences, or adjacent values, and none is reused. They appear independently generated.

### prerequisite_graph

Check 7, run over the whole graph.

- **`prerequisite` is filled in everywhere.** Gas, electric and final package fee are `[]`. The other five carry edges.
- **Edges** (all `problem` targets are extended policy ids in this file; none points at a base policy or at itself):

| # | blocked policy | problem | kind | gate | form | policy_source verbatim in own rule |
|---|---|---|---|---|---|---|
| E1 | undisputed_balance_payment | gas_trueup_line | value_input | ub_open (binding exists) | state | yes |
| E2 | undisputed_balance_payment | electric_estimate_line | value_input | ub_open (exists) | state | yes |
| E3 | leak_adjustment_credit | undisputed_balance_payment | state_gate | `utility_bills.event_type` | action (fallback_reason present) | yes |
| E4 | final_water_overage | final_package_fee | value_input | wo_days (exists) | state | yes |
| E5 | final_electric_overage | final_package_fee | value_input | eo_days (exists) | state | yes |
| E6 | moveout_utility_payment | final_package_fee | value_input | mo_balance (exists) | state | yes |
| E7 | moveout_utility_payment | final_water_overage | value_input | mo_balance (exists) | state | yes |
| E8 | moveout_utility_payment | final_electric_overage | value_input | mo_balance (exists) | state | yes |

- **Verbatim check.** Each policy_source was checked for whitespace-normalised containment in its own rule. All 8 are contained.
- **Form and fallback.** `fallback_reason` is present exactly on the action-form edge E3.
- **Acyclicity.** The graph is acyclic. Topological orders are gas, electric → undisputed → leak, and package fee → water/electric overage → move-out.
- **resolved_by.** Each `resolved_by` is the depended-on policy's `target_tool`. The written line genuinely enters the gate binding:
  - E1/E2/E6/E7/E8: the line enters the SUM of charges behind ub_open or mo_balance.
  - E4/E5: the package fee line becomes the LATEST `utility_package` flat line, whose proration_days and days_in_period feed wo_days/eo_days.
  - E3: the payment line is the waited-on event.
- **O-8: E3's gate is a field, not an eligibility id.** E3 is `kind: state_gate`, but its `gate` names a column (`utility_bills.event_type`) rather than an eligibility id, and the leak policy declares no eligibility list of its own. The gate is real (the payment line's presence), but it is not a named eligibility gate. Observation.
- **Conditions.** Each `condition` restates its sentence at the same strength. E7 and E8 carry "whenever the service end ... read exceeds the final ... allowance", which matches the overage policies' own "whenever the final ... overage is above zero". No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Check 6, the four-point test on each edge. For each: the ordering connective, what is waited on, the absence of tool/id/snake_case/row-id, and whether it matches the condition's strength.

- **E1**: "The undisputed balance is fixed only after the account carries a gas usage line for the billing period closed by each actual gas read that follows estimated gas reads."
  - Test: "only after"; record-visible state (a gas usage line for that period); no tool or id; universal "each", matching the condition. Pass.
  - Single writer: only `post_gas_trueup_line_465c860d` creates a gas `utility_usage_billback` line. The electric tool writes service_type electric.
  - Derivation: the records show an actual gas read that follows estimated reads, with no gas line for its period. The gas true-up policy's rule opens with "The gas true-up line is the gas usage line of the billing period closed by an actual gas read that follows one or more estimated gas reads". So exactly one reading leads to that policy.
- **E2**: "Before the undisputed balance is worked out, every billing period that closed without an electricity read must carry its estimated electricity line on the account."
  - Test: "Before"; state (an estimated electricity line per read-less period); no tool; universal. Pass.
  - Single writer: only `bill_estimated_electric_line_1c085b40` writes an estimated electric usage line.
  - Derivation: the electric policy's rule opens with "The estimated electricity line is the electricity usage line of a billing period that closed without any electricity read". One reading.
- **E3**: "A leak adjustment is not granted until the resident has paid the undisputed balance of the account."
  - Test: "not ... until"; action form, in business words; no tool or id. Pass.
  - Testing the fallback_reason: the depended-on write leaves only a `utility_payment` line. A state such as "a payment posted after the dispute was submitted" would not single out this write, because a second writer of this difficulty (`pay_moveout_utility_share_762d5a93`) writes an identical `utility_payment` row. Nothing on the row marks it as the undisputed balance. The fallback is justified.
  - Derivation: the sentence names "the undisputed balance of the account". The undisputed payment policy's rule defines that term and says "the resident pays it in person". One reading.
- **E4**: "The final water allowance is prorated only after the final period's package fee line stands on the account with its proration days."
- **E5**: "The final electricity allowance is not prorated until the final period's package fee line stands on the account with its proration days."
  - E4 and E5 test: "only after" / "not ... until"; state; no tool. Pass.
  - Single writer: only `post_final_package_fee_c766a545` writes a `utility_package` flat line. Its rule names "the package fee line of the final billing period".
- **E6**: "The part of the final utility balance paid in person is fixed only after the account in final billing carries its package fee line for the final period."
- **E7**: "Before the part paid in person is worked out, the final period's water usage above its final water allowance must stand on the account as a water overage line."
- **E8**: "The part paid in person is not worked out until the final period's electricity usage above its final electricity allowance stands on the account as an electricity overage line."
  - E6–E8 test: ordering connectives present; states; no tools. Pass.
  - Single writers: E6 package fee tool; E7 water overage tool (service water); E8 electric overage tool (service electric).
- **No extra wording.**
  - No blocked rule carries a second wording of its dependency, a tool name, or another policy id.
  - No depended-on rule restates the sentence: the gas, electric and package-fee rules are silent about their dependents.
  - No rule states an undeclared cross-problem order.
  - No base rule sentence states a cross-problem order that a tree rests on.

### override_declarations

Check 1's finding half, run sentence by sentence against each `base_policy_refs` entry.

- **gas_trueup_line vs utility_evt_submetered_usage.** Two supersessions are declared: the true-up usage clause and the usage-line amount clause.
  - Inherited unchanged: the state gate; read cadence; sewer as a separate line; the estimate clause (it governs the prior estimated lines, not this one); "no more than estimated_read_max_consecutive consecutive estimates"; "Lines of the previous month are issued on bill_issue_day" (compatible with "issued at the first bill issue after that read").
  - O-9: the base sentence "when that difference is negative the over-billed amount is credited by an estimated_read_true_up adjustment" is not superseded. The extended amount is `MX(0, ...)` with "when [the catch-up] is zero the line bills the gas true-up usage". For a negative true-up, extended would post a zero line where base posts a credit adjustment. Neither task world has a negative true-up.
- **electric_estimate_line vs utility_evt_submetered_usage.** The estimate clause (including "prorated by days") and the amount clause are superseded and declared. The consecutive-estimate ceiling is inherited. No undeclared deviation.
- **undisputed_balance_payment vs agg_household_balance and evt_payments.** `overwrite: []`. Checked sentence by sentence: payment on its own account and oldest line first; state gate; lease-accepted instruments; no late fees; no disconnection. Extended adds a new quantity (the undisputed balance) and never reprices a base quantity. No conflict.
- **leak_adjustment_credit vs utility_evt_adjustments_and_disputes.** Two supersessions are declared: the credit formula, and the threshold's measure (usual usage in place of utility_msr_average_usage).
  - Inherited: dispute-only correction; 60-day window; once per reason; "inside the apartment home"; "Allocation programs have no leak adjustment".
  - O-10 (undeclared override, no demonstrable consequence): base counts prior leak adjustments over `utility_msr_leak_adjustments_12m` ("Trailing 365 calendar days ending on and including the evaluation date"). Extended states "fewer than twelve whole months before the decision date" and never names the base window. The two windows differ only on boundary days. In task 0 the account carries no leak_adjustment row at all, so both give 0.
  - O-11: extended adds a gate, "not granted until the resident has paid the undisputed balance", on top of base's "A leak_adjustment is granted when ...". This is a prerequisite sentence by construction (E3), not a repricing of a base quantity. Recorded as an observation only.
- **final_package_fee vs flat_and_package and final_bill_and_close.** Both supersessions are declared.
  - O-12: the first superseded clause covers "Flat amounts, the package fee and the package allowances ... prorated ... over the actual days of the period", but the replacement speaks only of *final package fees*. The declaration therefore removes the base proration rule for every non-final flat amount and for all allowances without replacing them.
  - O-13: the second superseded clause includes the issuance deadline "is issued within final_bill_days_after_move_out calendar days", which the replacement (a days-charged sentence) does not carry. Neither dropped branch is written in either task: task 1 is at day 18 of 30 after move-out.
- **final_water_overage and final_electric_overage vs utility_evt_flat_and_package: F-1 below.** Each declares only the overage pricing clause. Each prorates its allowance by "the proration days over the days in period recorded on the account's latest package fee line". For the final period that is days charged over convention_days = 30. Base prorates allowances "by days of responsibility over the actual days of the period ... (allowances to 3 decimals)". Neither overage policy's `overwrite` names that sentence. The only declaration naming it is the sibling final_package_fee's, and that replacement says nothing about allowances.
- **moveout_utility_payment vs agg_household_balance and evt_payments.** `overwrite: []`. Checked: the final_billing state gate is inherited; "remaining utility balance ... carried into the final account statement" is compatible ("whatever is not paid is carried"); instruments are inherited. No conflict.

### factor_ladders

Each factor below is listed with its label, what it decides, its tier outcomes (fall-through last), and whether its tiers are multi-source (MS).

**gas_trueup_line**: 5 factors.

| factor | label | decides | tiers | MS | cross_difficulty |
|---|---|---|---|---|---|
| backbill_state_cap | parameter | gt_catchup_cap | 1.0×own / 1.5×own / no cap | no | lease |
| catchup_relief | method | gt_catchup_counted | ×0.5 floor to therm / ×0.75 ceil to therm / as measured | yes (estimate count + tenure) | lease |
| catchup_price_share | parameter | gt_price_share | 0.80 / 0.90 / 1.0 | yes (autopay + payments) | lease |
| trueup_service_charge | parameter | gt_service_share | 0 / 0.5 / 1.0 | yes (estimate count + renewals) | term |
| estimate_charge_return | parameter | gt_return_share | 1.0 / 0.5 / 0 | no | lease |

- Counts: 4 parameter, 1 method, 3 multi-source, 5 cross-difficulty (lease, term).
- O-14: catchup_relief's method difference between its two non-fall-through tiers rests on the multiplier *and* the rounding function (floor vs ceiling to a whole therm), and the fall-through has no whole-unit rounding. A change of rounding function is a change of procedure, so I accept the `method` label. Noted as the thinnest method label in the charter.

**electric_estimate_line**: 6 factors.

| factor | label | decides | tiers | MS | cross_difficulty |
|---|---|---|---|---|---|
| estimate_window | method | el_recent | 7-month mean / default_kwh_per_occupant × billed occupants / 4-month mean | yes | lease |
| seasonal_adjustment | method | el_seasonal | mean(recent, last-year read) / last-year read / recent | yes | none |
| estimate_share | parameter | el_share | 0.90 / 0.80 / 1.0 | yes | lease |
| renewal_loyalty_reduction | parameter | el_loyalty | 0.05 / 0.02 / 0 | no | term |
| state_estimate_share | parameter | el_state_share | 0.95 / 0.97 / 1.0 | no | lease |
| estimate_service_share | parameter | el_service_share | 0.5 / 0.75 / 1.0 | yes | lease |

- Counts: 4 parameter, 2 method (estimate_window has a genuinely different algorithm in its tier 2), 4 multi-source.

**undisputed_balance_payment**: 4 factors.

| factor | label | decides | tiers | MS | cross_difficulty |
|---|---|---|---|---|---|
| dispute_hold_scope | method | ub_held | line+sewer / all water lines in 2 months / line alone | yes (reason + sewer line) | none |
| payable_held_part | method | ub_payable | proportional / service charges / 0 | yes (repair date + read count) | none |
| deposit_security_share | parameter | ub_security_share | 0.50 / 0.75 / 1.0 | yes (deposit + rent) | deposit |
| payment_standing_share | parameter | ub_standing_share | 0.80 / 0.90 / 1.0 | yes | lease |

- Counts: 2 parameter, 2 method.

**leak_adjustment_credit**: 6 declared factors.

| factor | label | decides | tiers | cross_difficulty |
|---|---|---|---|---|
| usual_usage_window | **method** | lk_usual | mean of other actual water reads over 7 / 5 / 4 whole months | lease |
| household_tolerance | parameter | lk_tolerance | 0.20 / 0.10 / 0 | lease |
| repeat_reporter_cap | parameter | lk_excess_cap | 2.0× / 3.0× / none | none |
| repair_speed_share | parameter | lk_share | 0.75 / 0.60 / leak_adjustment_credit_pct | none |
| renewal_loyalty_increment | parameter | lk_loyalty | 0.10 / 0.05 / 0 | term |
| prompt_report_courtesy | parameter | lk_courtesy | 10 / 5 / 0 | none |

- **F-2 below: mislabelled method.** Every tier of usual_usage_window computes the same thing, "the mean of the actual water reads other than the disputed read" dated fewer than N whole months before the decision date. Only N ∈ {7, 5, 4} changes: `RND((lk_s7−lk_usage)/(lk_n7−1),3)` vs `RND((lk_s5−lk_usage)/(lk_n5−1),3)` vs `RND((lk_s4−lk_usage)/(lk_n4−1),3)`. That substitutes a number (the window length) into one formula, which is a parameter. With it re-labelled, the leak computation has 0 `method` factors against the required ≥1. Parameter factors: 6. Multi-source: usual_usage_window (tenure + read count), repair_speed_share (repair days + prior adjustments).

**final_package_fee**: 5 factors.

| factor | label | decides | tiers |
|---|---|---|---|
| notice_days_charged | method | pf_days_charged | days − 1 / flat 30 / days of responsibility |
| state_final_fee_share | parameter | pf_state_share | 0.95 / 0.97 / 1.0 |
| final_month_tenure_courtesy | parameter | pf_courtesy | 0.10 / 0.05 / 0 |
| final_month_standing_credit | parameter | pf_standing_credit | 2.50 / 1.25 / 0 |
| final_month_renewal_credit | parameter | pf_renewal_credit | 5.00 / 2.50 / 0 |

- notice_days_charged is a genuine change in counting convention, from pro-rata days to a full month, and is multi-source (notice date + named move-out vs lease move-out). The standing credit is also multi-source.
- Counts: 4 parameter, 1 method.

**final_water_overage**: 6 factors.

| factor | label | decides | tiers |
|---|---|---|---|
| moveout_cleaning_allowance | parameter | wo_cleaning | 0.75 / 0.50 / 0 |
| water_overage_blocks | method | wo_priced | block schedule / uniform ×1.10 / measured |
| sewer_carriage_share | parameter | wo_sewer_share | 0.50 / 0.75 / 1.0 |
| drought_surcharge | parameter | wo_drought | 1.10 / 1.05 / 1.0 |
| final_overage_tenure_share | parameter | wo_tenure_share | 0.80 / 0.90 / 1.0 |
| final_overage_renewal_share | parameter | wo_renewal_share | 0.90 / 0.95 / 1.0 |

- Counts: 5 parameter, 1 method. No tier is multi-source (see task 1 for the per-task requirement).

**final_electric_overage**: 6 factors.

| factor | label | decides | tiers |
|---|---|---|---|
| climate_allowance_uplift | parameter | eo_climate | 150 / 75 / 0 |
| household_allowance_uplift | parameter | eo_household | 100 / 50 / 0 |
| electricity_overage_blocks | method | eo_priced | block schedule / uniform ×1.10 / measured |
| final_electricity_tenure_share | parameter | eo_tenure_share | 0.85 / 0.92 / 1.0 |
| final_electricity_standing_share | parameter | eo_standing_share | 0.95 / 0.97 / 1.0 |
| final_electricity_renewal_share | parameter | eo_renewal_share | 0.94 / 0.97 / 1.0 |

- The standing share is multi-source. Counts: 5 parameter, 1 method.

**moveout_utility_payment**: 4 factors.

| factor | label | decides | tiers |
|---|---|---|---|
| itemization_anticipation | method | mo_anticipated | itemized + reserve×rest / reserve×held / held |
| itemization_reserve_share | parameter | mo_reserve_share | 0.60 / 0.80 / 1.0 |
| forwarding_reliance_share | parameter | mo_forwarding_share | 1.0 / 0.5 / 0 |
| lease_standing_reliance_share | parameter | mo_standing_share | 1.0 / 0.5 / 0 |

- itemization_anticipation is multi-source (deposit status + itemized-charge count). forwarding_reliance_share is multi-source (forwarding address + refund method), as is lease_standing_reliance_share (autopay + certified funds).
- Counts: 3 parameter, 1 method, 3 multi-source (deposit, lease).

**Structural checks across all policies.**
- Bindings are disjoint within each policy. No factor `decides: result`. Every ladder has 3 pairwise-disjoint tiers as stated, and no two tiers of one ladder select the same value or method.
- Every tier's condition and outcome is stated in the rule prose, including the fall-through.
- Every fall-through equals the factor's `baseline` binding.
- Every `baseline.rule` sentence was checked for whitespace-normalised containment in the rule, and all are contained. Each `baseline.rule` is self-sufficient: it yields a definite number from the records with no factor applied.
- **Realism of ladders.** Several ladders are commercially unusual for a utility billback program: renewal-loyalty increments on a leak credit or estimate line; a sewer carriage share on the overage that falls as the floor plan grows; an estimate discount keyed to rent autopay. None has a tier whose condition holds of every customer who reaches its write, or a fall-through that is a straw man (every fall-through is the plain standard method). I cannot show that a named condition is one no business weighs, so this is observation O-15, not a red light.

### findings

- **F-1: SOURCE-POLICY RED (undeclared override of allowance proration; bears on task 1).**
  - Symptom: final_water_overage and final_electric_overage prorate the final allowance by the latest package fee line's proration days over days in period (for the final period, days charged/30). Base utility_evt_flat_and_package prorates "the package allowances ... by days of responsibility over the actual days of the period (proration_method), rounded half up to the cent (allowances to 3 decimals)".
  - Root cause: neither overage policy's `overwrite` names that base sentence; each names only the overage-pricing clause. The only overwrite naming the sentence is final_package_fee's, and its `replaced_by` ("Final package fees are prorated over a 30-day month ...") governs fees only. No declaration anywhere replaces the allowance half.
  - Evidence: `utility.extended.yaml` lines 2155–2162 (water overwrite), 2394–2401 (electric overwrite), 1942–1952 (package fee overwrite); base `utility.yaml` line 763–765.
  - Consequence: demonstrated in `1.md` against task 1's world (base reading 30.18 / 76.74 / 63.59 vs the extended reading 30.32 / 76.98 / 63.97).
  - Affected: both overage policies' `overwrite` and the package fee's `overwrite`.
- **F-2: SOURCE-FACTOR RED (mislabelled method; bears on task 0).**
  - Symptom and root cause: leak_adjustment_credit's only `method` factor, usual_usage_window, changes only the averaging window length (7/5/4 whole months) inside one formula.
  - Consequence: the leak computation has no honest method factor (needs ≥1). Demonstrated in `0.md`.
  - Affected: `utility.extended.yaml` lines 1830–1844, and the rule sentence at lines 1702–1709.
- **Observations O-1 … O-15**, as written above. None is grounds for rework on its own.

## closing_checklist

Written after both reveals (2026-09-24T18:12Z). **The difficulty does not close.** Not every task passes all four relationships:

- **task 0: SOURCE-FACTOR RED** (F-2, mislabelled method on the leak computation);
- **task 1: SOURCE-POLICY RED** (F-1, undeclared allowance-proration override).

Status of each Step 4 item:

- **Audit files.** `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and this file sits alongside them. This is round 1, with no older revisions. Each comparison section carries a verdict, not a PASS.
- **Scope and closure.**
  - Coverage and disjointness: confirmed against `charter_scope`. Task 0 claims {gas_trueup_line, electric_estimate_line, undisputed_balance_payment, leak_adjustment_credit}; task 1 claims {final_package_fee, final_water_overage, final_electric_overage, moveout_utility_payment}. The sets are disjoint and cover all 8. The task tools match one-to-one.
  - uuid8s are independent (§action_binding_and_uuids).
- **Problem trees.** Each has 3 prerequisite problems. value_input edges are 2 (task 0) and 5 (task 1). Each has one owner=user problem, and each is acyclic. The difficulty-wide graph (E1–E8) is acyclic, with no cross-task edge.
- **Factors.**
  - Every computation declares a self-sufficient baseline and 4–6 factors, every ladder has 3 tiers stated in the rule, and every factor bears weight against an honest baseline. The all-baseline number differs from gold in all 8 computations.
  - **Exception:** the leak computation has 0 honest method factors (F-2).
- **Gates.** Not re-run on a final form, because the difficulty does not close. The rc=0 snapshot in the brief remains the entry evidence.

## revision_2

### charter_global_frozen (round 2)

- Auditor: the same independent auditor, round 2. Freeze time: 2026-09-24, before either task's round-2 GT was read.
- Frozen inputs:
  - `utility.extended.yaml`: sha256 `1610bd4d8e64f495eec38f00d34acca283d7701e225267f7e6936cd2537875fa` (was `695833e4…`, **changed**);
  - `task_tools.py`: sha256 `9366601a4beb256bebf2acbc32ceeb5b049dfed99d20872fbdb05dfdd190872a` (was `d4280f88…`, **changed**);
  - views `r2/0.json` `b8eed7c3…` and `r2/1.json` `976055b1…`, byte-identical to round 1 (re-hashed).
- Because both shared inputs moved, every charter-global section below is re-derived in full, not carried forward. The round-1 text above is preserved untouched.
- Entry conditions: the brief's round-2 gate snapshot shows every instantiation gate at rc=0 (traceability deferred to render). Input is complete.
- Base copy: all 10 keys still compare equal to `blueprint/products/utility.yaml`. Verbatim.

### policy_conflict_scan (round 2)

- **Subjects, tools and computes are unchanged.** Still 8 policies, 8 distinct `(target_tool, computes)` pairs, and 8 prerequisite edges.
- **O-1 is closed.** The undisputed payment rule now reads "…on an active utility services account … (an account in final billing is settled by the move-out utility payment instead)". The move-out rule adds "It applies to every account in final billing, whether or not a line on it stands under a dispute". The two payment policies are now disjoint by account status.
  - Note: the undisputed rule now names another problem's concept ("the move-out utility payment") as a scope boundary. It states no order and grounds no edge, so it is not an undeclared dependency.
- **Other checks re-run.** Triggers and anchors, inherited eligibility, cross-category declarations and terminal states were all re-checked on the new text. No conflict.
- **Scopes.** The inferred scopes are unchanged: tree A {gas, electric, undisputed, leak} and tree B {package fee, water overage, electric overage, move-out}. They are disjoint and together cover all 8.

### rule_compute_equivalence (round 2)

- **Mechanical sweep, re-run.**
  - Every `compute_basis` quotation is found verbatim in its policy's rule after whitespace normalisation (0 misses across all 8 policies).
  - Every `baseline.rule` sentence is found in its rule (0 misses).
  - Every ladder tier is a rule sentence and a branch of its `decides` binding.
- **O-2 closed.** The gas, electric, undisputed and leak rules now each state that "each sum of recorded … usage is taken to 2 decimals", which is what the DSL's `SUM` does.
- **O-3 unchanged.** RND is Python `round`. No new tie arises: the new leak figure (3.502 + 3.460)/2 = 3.481 is exact. Still an observation.
- **O-4 closed.** The undisputed and leak rules now define the seven-month and four-month figures explicitly as "usage of the actual water reads … less the usage billed on the disputed line (the read of the disputed period), divided by the number of those reads less one". That is exactly `ub_payable` / `lk_usual`.
- **O-5 closed.** `ub_deposit` is now `CFIELD('deposit', 'deposit_held') or 0`, with no status filter.
- **O-6 closed.** `gt_cum` is now `LATEST(gas read usage) + SUM(estimated gas reads < 3 months)`. The rule now says "the usage recorded on the account's latest gas read, which is the actual read, plus the usage recorded on the estimated gas reads …".
- **O-9 closed.** The gas rule and its overwrite now read "…when the gas true-up usage is below zero the line bills no usage, the over-billed usage being credited by the estimated-read true-up adjustment the base rule provides". `gt_billed_usage` uses `MX(0, gt_trueup_usage)`. The base credit route is preserved.
- **New leak ladder (seasonal_usual_usage) in compute.** `lk_usual` implements the rule's three tiers exactly:
  - tier 1 (tenure ≥ 36, last year's same-month read exists, ≥ 6 other reads in 7 months): `RND((RND((lk_s7-lk_usage)/(lk_n7-1),3)+lk_ly)/2,3)`;
  - tier 2 (12 ≤ tenure < 36 and last year's read exists): `RND(lk_ly,3)`;
  - fall-through: the four-month figure.
  - `lk_ly` and `lk_ly_n` read the actual water read 12 ≤ months < 13 back, as the rule says ("Last year's water read of the same service month is the actual water read dated at least twelve and fewer than thirteen whole months before the decision date").

### action_binding_and_uuids (round 2)

- **Tool bodies unchanged in substance.** Every body is still `find` → `create` → `update(balance_due)`, and the leak tool still marks disputes credited. No body checks a condition.
- **O-7 closed.** The move-out docstring's summary line is now "Make your move-out utility payment on the utility services account of the apartment home you have left." The only remaining ordering words are "after the line/payment/credit" in the Returns sections, describing each tool's own effect.
- **uuid8s unchanged and independent.** 465c860d, 1c085b40, 990e05bb, a9c6c674, c766a545, 2681eca1, b496acda, 762d5a93.

### prerequisite_graph (round 2)

- Edges E1–E8 are unchanged in problem, kind, gate, form and resolver.
- Every `policy_source` is still contained verbatim in its own rule (mechanical check: 8/8).
- E2's sentence and condition now carry the same added scope ("since / after the account's first recorded electricity read"), at the same strength as each other.
- The graph is still acyclic.
- O-8 is unchanged: E3's `gate` is a column. Observation.

### prerequisite_sentences (round 2)

- E1 and E3–E8 are textually unchanged. The round-1 four-point results stand, re-read against the new rules.
- E2 now reads "Before the undisputed balance is worked out, every billing period since the account's first recorded electricity read that closed without an electricity read must carry its estimated electricity line on the account."
  - Four-point test: "Before"; a record state; no tool or id; universal over a bounded set. Pass.
  - The electric rule's scope now matches: "a billing period that closed without any electricity read after the account's first recorded electricity read".
  - **T0-O1 is closed at the charter level.** Periods before the first seeded read can no longer be read into E2.
- The single-writer argument for each state-form edge is unchanged. The E3 fallback is still justified (the move-out payment tool writes an identical `utility_payment` row).

### override_declarations (round 2)

- **gas_trueup_line.** Two supersessions are declared. The first `replaced_by` now also routes a negative true-up to the base estimated_read_true_up credit, which closes O-9. No undeclared deviation.
- **electric_estimate_line.** Unchanged. No undeclared deviation.
- **undisputed_balance_payment and moveout_utility_payment.** `overwrite: []`. The added scope sentences reprice no base quantity.
- **leak_adjustment_credit.** A third supersession is now declared: "and utility_msr_leak_adjustments_12m is below leak_adjustments_per_12_months;" is replaced by the twelve-whole-months count. **O-10 is closed.** The base measure itself stays in the base section, unreferenced by the merged leak clause. O-11 is unchanged (a prerequisite gate by construction).
- **F-1 closed. Allowance proration is now declared by the policies that deviate.**
  - final_water_overage and final_electric_overage each now name, in their own `overwrite`, the base sentence "Flat amounts, the package fee and the package allowances are prorated … (allowances to 3 decimals)."
  - Each replaces it for its own service: the final allowance = allowance × proration days / days in period of the latest package fee line; and "[Water|Electricity] allowances of every period other than the final period of an account in final billing remain prorated … by days of responsibility over the actual days of the period, to 3 decimals".
  - final_package_fee's replacement now also restates the base proration for "Package fees and flat amounts of every period other than the final period of an account in final billing, and the package gas allowance of every period including the final one".
  - The three replacements govern disjoint quantities, so the merged semantics are unique. The base 29/31 reading of the final water and electricity allowance is now explicitly superseded in the very policies that compute them.
- **O-13 closed.** final_package_fee's second supersession now covers only the fragment "the last period's usage, allocation or overage lines and flat or package lines prorated through the service end date", so the issuance deadline ("is issued within final_bill_days_after_move_out calendar days") stays in force.
- **O-12 narrowed, not fully closed; now O-12r plus the new O-16.** Both are observations; neither task writes such a line.
  - O-12r: the union of the three replacements of the flat/package proration sentence restores the base rule for every non-final period and for gas allowances. It does not cover **final-period flat amounts of a non-package account in final billing** (trash, pest, stormwater, billing administration on an allocation or submetered program). They are excluded from "every period other than the final period of an account in final billing" and are not "Final package fees". No replacement gives their proration.
  - O-16 (new): the final_bill_and_close fragment "the last period's usage, allocation or overage lines and flat or package lines prorated through the service end date" is superseded three times: by the package fee's notice sentence and by the water and electric allowance sentences. None of the three replaces it for the **usage and allocation lines of a non-package account's final bill**. The base "No line may be billed for any day after the service end date" still bounds them, but "prorated through the service end date" is no longer stated for them.

### factor_ladders (round 2)

- Gas (4p/1m), electric (4p/2m), undisputed (2p/2m), package fee (4p/1m), water overage (5p/1m), electric overage (5p/1m) and move-out (3p/1m) are structurally unchanged. The round-1 per-policy tables above stand. O-14 is unchanged.
- **leak_adjustment_credit: F-2 closed.** usual_usage_window is replaced by **seasonal_usual_usage** (`method`, decides `lk_usual`, bindings [lk_n7, lk_s7, lk_tenure, lk_ly_n, lk_ly, lk_usual]). Tiers:
  1. "seasonal blend: the mean of the seven-month usual usage and last year's water read of the same service month";
  2. "same-month comparison: last year's water read of the same service month alone";
  3. fall-through "recent mean: the four-month figure".
  - The three tiers use three different procedures (a blend of two estimators; a single prior-year observation; a recent-window mean), not one formula with a swapped number. The `method` label is honest.
  - The tiers are pairwise disjoint: tier 1 needs tenure ≥ 36 and tier 2 needs 12 ≤ tenure < 36.
  - The factor is multi-source (tenure, last-year read, read count) and cross_difficulty lease. Its baseline is the four-month figure, which is baseline.rule's value.
  - Seasonal comparison against the same month last year is a standard practice for utility leak adjustments. Realistic.
  - Leak counts now: 5 parameter, 1 method.
- **O-15 addressed by adding rationale sentences.** The added sentences justify the estimate share (autopay tempering), the renewal loyalty ("the Larkspur renewal loyalty program's allowance…"), and the sewer carriage share ("larger floor plans carry private patio hose bibs whose water never reaches the sewer"). They change no tier and no value. The ladders' realism remains an observation, not a red light.

### findings (round 2)

- **F-1: closed** (evidence under override_declarations above; the task-1 demonstration is in `1.md` revision_2).
- **F-2: closed** (evidence under factor_ladders above; the task-0 demonstration is in `0.md` revision_2).
- Observations: O-1, O-2, O-4, O-5, O-6, O-7, O-9, O-10, O-13 and T0-O1 are closed. O-3, O-8, O-11 and O-14 are unchanged, and I agree with "no change needed". O-15 is addressed by rationale only and remains an observation. O-12 is narrowed to O-12r. **O-16 is new** (observation).
- New red lights: none at charter level. There is no regression in any section.

### closing_checklist (round 2)

Written after both round-2 reveals (2026-09-24T18:26Z). **The difficulty closes.**

- **Per-task verdicts, round 2:** task 0 PASS and task 1 PASS, on all four relationships. `0.md` and `1.md` each carry the round-1 text untouched plus `## revision_2`, with the frozen section written before the comparison.
- **Coverage and exclusivity.** Confirmed against both `charter_scope`: the 8 extended policies are covered once each, the scopes are pairwise disjoint, and the task tools are closed one-to-one. The uuid8s are independent and unchanged.
- **Problem trees.**
  - task 0: n = 3, 2 value_input edges, user write = the undisputed payment.
  - task 1: n = 3, 5 value_input edges, user write = the move-out payment.
  - Both are acyclic, and the difficulty-wide graph E1–E8 is acyclic with no cross-task edge.
- **Factors.** Every one of the 8 computations has a self-sufficient baseline and 4–6 factors with ≥ 2 parameter and ≥ 1 honest method:
  - leak now 5p/1m (F-2 closed);
  - all tasks have ≥ 1 multi-source and ≥ 1 cross-difficulty factor;
  - every ladder has 3 distinct tiers stated in its rule;
  - every factor bears weight;
  - every all-baseline number differs from gold (155.25, 91.12, 295.52, 30.18; 159.50, 45.66, 112.37, 233.97).
- **Gates.** The coordinator's round-2 re-run on the final form is at rc=0 (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). Traceability is deferred to the render stage.
- **Open observations** (not grounds for rework): O-3, O-8, O-11, O-12r, O-14, O-15 and the new O-16.
