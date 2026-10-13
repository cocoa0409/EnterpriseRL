# Policy-task audit — meter_testing_and_metering / charter-global

## charter_global_frozen

- Freeze time: 2026-10-07T21:26Z (written before any task's GT was opened; contains nothing derived from a revealed GT).
- Auditor: independent policy-task auditor (Claude agent, not the author of these artifacts).
- Frozen inputs (sha256, re-verified against MANIFEST.txt):
  - `tasks/meter_testing_and_metering/meter.extended.yaml` = `09087215f4df335748b25793bc8ce4a9f3e431384f92b005b9cc28b2812486a9`
  - `tasks/meter_testing_and_metering/task_tools.py` = `051515011c5d1e8368eddf6e27e8284f32564a2dd7ad1aee3cae77267f8fe556`
- Fields permitted: the blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/meter.yaml`, `products/service.yaml` for schedule parameters), the extended charter in full, `task_tools.py` in full, the masked views (`frozen_time`, `user_scenario`, `initial_state`), and the erlbench DSL semantics (`within_months` / `MONTHS` / `LATEST` scoping as implemented by the instantiate-stage evaluator).
- Fields masked and unread at this point: every task file `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure).
- Entry conditions (Step 0): gate snapshot supplied by the coordinator — check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute "suite depth: history_rows_max=35(>= 8) branches_max=113(>= 5)" / COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff INFO (optional); check_cross_fire SCOPE OK; check_traceability deferred (KB not yet published). Masked views and hashes supplied. Inputs complete; check_traceability being deferred is noted, not a defect of this audit's inputs.
- Base copy: `diff <(head -954 meter.extended.yaml) blueprint/products/meter.yaml` differs only by one trailing blank line — the base section is verbatim.

### policy_conflict_scan

Extended policies (6), their claims and the tasks they belong to (from the charter's own section comments):

| policy | target_tool (owner) | computes | subject | prerequisite |
| --- | --- | --- | --- | --- |
| meter_ext_slow_meter_backbill | post_slow_meter_backbill_dc57beb1 (agent) | backbill_amount | meter_accuracy_adjustment | [] |
| meter_ext_referee_backbill_settlement | accept_referee_backbill_settlement_27524241 (user) | settlement_amount | meter_accuracy_adjustment | slow_meter_backbill (value_input) |
| meter_ext_repeat_test_fee | charge_repeat_test_fee_cae4c873 (agent) | fee_amount | meter_test_fee | [] |
| meter_ext_fast_meter_refund | post_fast_meter_refund_06e0a347 (agent) | refund_amount | meter_accuracy_adjustment | repeat_test_fee (value_input) |
| meter_ext_referee_refund_settlement | accept_referee_refund_settlement_2157b6a7 (user) | settlement_amount | meter_accuracy_adjustment | fast_meter_refund (value_input), non_registering_backbill (state_gate) |
| meter_ext_non_registering_backbill | post_non_registering_backbill_96d206ff (agent) | backbill_amount | meter_accuracy_adjustment | [] |

- Overlapping subject `meter_accuracy_adjustment` (five policies): the objects are disjoint by the classifying result each rule names — slow-meter backbill "when that result classifies the meter slow" (company result, by the type's test method); fast-meter refund "classifies the meter fast"; non-registering backbill "the meter's test result that classifies it non_registering"; the two referee settlements are recorded "against the referee test result" (the meter's latest result) whose company result is slow / fast respectively. Base dedup `adjust_each_result_once` ("Each test result is adjusted once.") is respected: each policy writes against a different meter_test_id. No two policies reach different conclusions on one object.
- Triggers / time anchors: the three agent writes are dated "on the date it is calculated" (tool stamps `ctx.now()`); the two settlements "on the date the customer accepts it" (tool stamps `ctx.now()`); the repeat fee is "posted on the test date of the result it is charged for" (tool stamps the result's `test_date`). Consistent with the tools.
- Cross-category read boundaries: all reads of `service` (schedule parameters via CPARAM, `rate_effective_date`, `service_voltage`, `variant_name` via CFIELD, bills / late payment charges via XSUM/XCOUNT filtered by `service_account_id=F('service_account_id')`). No write crosses into another category.
- Scope: the charter's own section comments assign slow-meter backbill + referee backbill settlement to task 0, and repeat test fee + fast-meter refund + referee refund settlement + non-registering backbill to task 1. The two scopes are disjoint (no shared policy or target tool) and jointly cover all six extended policies (re-confirmed against the masked worlds in each task file; confirmed against `charter_scope` only after reveal).
- Base-only event types of the blueprint claim (meter_test_request, meter_installation_order, meter_order_cancellation, opt-out fees) carry no extended policy; this is not required by the four relationships — observation only.

### rule_compute_equivalence

Check 2, over every extended policy. For every binding the `compute_basis` quotation was located verbatim in the policy's own `rule` (all located). Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding, and vice versa (no tier lives in one face only). Points examined beyond the one-to-one quotation match:

1. Bill-window implementation (all five bill-based computations). The rule says "counting back from the company test date, the most recent regular bills whose billing period ended on or before that date, as many as N"; compute implements it as the bills with `0 <= MONTHS(billing_period_end, NOW)` in `[MONTHS(test_date, NOW), MONTHS(test_date, NOW)+N)`. The two coincide only when no bill ends after the test date inside the same NOW-relative month bucket as the test date (day-of-month dependent). Likewise the non-registering prior-year window (`+12`) and "ended before the month of the latest test request" (`MONTHS(request_date, NOW)` rather than the calendar month). In both task worlds the two readings select identical bill sets (verified bill by bill in each task file), so no consequence is demonstrable here — **observation**.
2. Interest tier wording in `meter_ext_fast_meter_refund`. Rule: "Where the fast-meter refund **covers** at least the full-interest number of bills ... Where it **covers** at least the half-interest number"; the same rule says the refund "also covers the regular bills whose billing period ended after the company test date". Compute (`fr_bills_counted`) and the ladder face ("the refund **counts back** at least ...") count only the bills counted back. A world where the forward bills push the covered count across 6 or 12 would give two readings. In task 1 the counts are 18 back / 19 covered, both >= 12 — no consequence demonstrable — **observation** (the referee refund settlement's rule says "counts back", consistent with its compute).
3. `fr_complaints` / `rr_complaints` count customer requests with `MONTHS(request_date, NOW) < free_test_period_months + MONTHS(company_test_date, NOW)`; this also admits customer requests made after the company test date, which the rule ("within ... months before the company test date") excludes. In task 1 no customer request on the meter falls after the company test (the post-test request is `commission_referee`) — **observation**.
4. `tf_earlier_tests` counts customer requests within `lookback + MONTHS(request, NOW)` months of NOW, minus one for the charged request — equivalent to "within the escalation look-back before the charged test's request, in whole calendar months back from that request" whenever the charged request is the latest customer request (it is, by the rule's object sentence). Verified on task 1's rows.
5. `rs_already_backbilled` / `rr_already_refunded` sum every backbill / refund on the holding — matches "every backbill/refund already standing on the meter's adjustment record". `fr_fees_returned` / `rr_fees_returned` sum every `meter_test_fee` on the holding — matches "every repeat test fee standing on the meter's metering charges".
6. No compute binding invents a basis absent from the rule; no rule sentence is left without a binding (the descriptive clauses "because the meter kept registering slow/fast until it was taken out", "Large and medium demand customers receive their interval data every day" are justifications, not quantities).

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above); no base policy names a target tool.
- Tool bodies (task_tools.py lines 14-243): every tool creates exactly one row (`meter_adjustments` or `meter_charges`) from the passed values, with no eligibility, prerequisite, amount or state check, no error path and no hint; the module docstring states "No tool checks eligibility, prerequisites or amounts". Owners: slow backbill / repeat fee / fast refund / non-registering backbill = agent; both referee settlements = user.
- Docstrings name no other tool and carry no before/after/first wording. Two docstrings describe the semantics of the amount relative to other rows: `accept_referee_backbill_settlement_27524241` "the settlement amount ... that the customer agrees to owe on top of whatever backbill already stands for the meter" and `accept_referee_refund_settlement_2157b6a7` "owed back to the customer on top of whatever refund already stands for the meter". This restates the subtraction the rule already states ("minus every backbill/refund already standing on the meter's adjustment record"); it does not state a position in a sequence — **observation**.
- uuid8s: dc57beb1, 27524241, cae4c873, 06e0a347, 96d206ff, 2157b6a7 — six distinct values, no shared prefix beyond a single leading digit, no sequence, no copy-with-new-tail pattern. Accepted as independently generated.
- The tools do not post the service-side triggers the base event declares for `meter_accuracy_adjustment` / `meter_test_fee` ("Nothing else on the meter or the service account is changed by this call"); there is no share write tool for service postings, so no second scored write is reachable — **observation**.

### prerequisite_graph

Check 7. `prerequisite` is filled on all six policies (`[]` on slow-meter backbill, repeat test fee, non-registering backbill). Edges:

| id | blocked -> problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| E1 | referee_backbill_settlement -> slow_meter_backbill | value_input | rs_already_backbilled (exists in compute) | state | post_slow_meter_backbill_dc57beb1 (= target_tool) |
| E2 | referee_refund_settlement -> fast_meter_refund | value_input | rr_already_refunded (exists) | state | post_fast_meter_refund_06e0a347 (= target_tool) |
| E3 | referee_refund_settlement -> non_registering_backbill | state_gate | `meter_adjustments.meter_test_id` | state | post_non_registering_backbill_96d206ff (= target_tool) |
| E4 | fast_meter_refund -> repeat_test_fee | value_input | fr_fees_returned (exists) | state | charge_repeat_test_fee_cae4c873 (= target_tool) |

- Every `problem` is an extended policy id of this file; none points at a base policy or itself. Graph: {RS->SB}, {RR->FR->TF, RR->NR}: acyclic.
- Every `policy_source` is verbatim in its own policy's `rule` (located by string match: E1 at rule sentence 3 of referee_backbill_settlement; E2 and E3 at sentences 3 and 4 of referee_refund_settlement; E4 at sentence 2 of fast_meter_refund).
- `form: state` everywhere, no `fallback_reason` anywhere — consistent.
- `condition` matches the sentence's strength: E1 "carries a backbill recorded against the company's own slow test result" = "the company test result it reviews carries its slow-meter backbill"; E2 likewise; E3 "Every non_registering test result on the customer's other meter installations has a backbill row" = "every test result on the customer's other meters that found a meter not registering carries its non-registering backbill" (open set stated open); E4 "Every chargeable within-tolerance customer-requested test of the meter carries its repeat test fee" = "every repeat test fee owed for the meter's earlier within-tolerance customer tests stands on the meter's metering charges". Not strengthened or weakened.
- `effect` holds by the tool effects: E1/E2 the tools create the backbill/refund row the gate sums; E4 the tool creates the meter_test_fee row `fr_fees_returned` sums; E3 creates the backbill row carrying the non-registering result's meter_test_id.
- E3's `gate` is a table field, not the id of a declared eligibility entry (the referee refund settlement declares no `eligibility` block); the gate is carried by the rule sentence itself. No consequence demonstrable (the sentence is in the rule and is discoverable) — **observation**.
- No authoring-viewpoint wording inside any `prerequisite` field. The YAML section comments ("# Task 0 — ... (prerequisite problem)", "(root problem)", "(state-gate prerequisite)") are authoring-viewpoint text inside the charter file; they are comments, not policy fields, and are dropped by any YAML load — **observation**.

### prerequisite_sentences

Check 6, four-point test per edge:

- E1 "The referee backbill settlement is fixed only after the company test result it reviews carries its slow-meter backbill on the meter's adjustment record." — ordering connective "only after"; waited-on state is record-visible (a `meter_adjustments` row, direction backbill, `meter_test_id` = the company result); no tool, id or snake_case; strength = condition. One write brings it about: the slow-meter backbill policy's own rule says "The slow-meter backbill is recorded on the meter's adjustment record against that test result, as a backbill" — the only other backbill write on such a meter (the referee settlement itself) is recorded "against the referee test result", not the company result. Derivation: sentence -> records (no adjustment row on the company result) -> the slow-meter backbill rule describes exactly that row -> resolving action = post the slow-meter backbill. Single reading.
- E2 "The referee refund settlement is not credited until the company test result it reviews carries its fast-meter refund on the meter's adjustment record." — "not ... until"; state record-visible; exactly one write (fast-meter refund rule: "recorded on the meter's adjustment record against that result, as a refund"). Single reading.
- E3 "The referee refund settlement is not credited until every test result on the customer's other meters that found a meter not registering carries its non-registering backbill on that meter's adjustment record." — "not ... until"; state record-visible (backbill row whose `meter_test_id` is the non_registering result); exactly one write (non-registering backbill rule: "recorded on the meter's adjustment record against that result, as a backbill"; the slow-meter backbill applies only to a slow result). Single reading.
- E4 "The fast-meter refund is fixed only after every repeat test fee owed for the meter's earlier within-tolerance customer tests stands on the meter's metering charges." — "only after"; state record-visible (`meter_charges` row, event meter_test_fee, per chargeable result); exactly one write (repeat test fee rule). Note the depended-on rule resolves only "the meter's latest within-tolerance result answering the meter's latest customer-requested test", so a world with two or more owed-and-uncharged fees would leave the sentence unsatisfiable by the declared writes; the task-1 world has exactly one such result (shown in `1.md`) — **observation**.
- No blocked rule carries a second wording of its dependency, a tool name or another policy id; no depended-on rule restates the sentence (slow-meter, fast-meter, non-registering and repeat-fee rules say nothing about referee settlements or refunds).
- Undeclared cross-problem orders: none. The fast-meter refund's "plus every repeat test fee standing on the meter's metering charges" and the settlements' "minus every backbill/refund already standing" are value reads grounded by E4, E1, E2. No base sentence is used to ground an edge.

### override_declarations

Check 1 (finding half), sentence by sentence against each `base_policy_refs` entry.

`meter_accuracy_adjustment_rule` (referenced by slow backbill, referee backbill, fast refund, referee refund, non-registering backbill):

| base sentence | slow BB | ref BB settl. | fast refund | ref refund settl. | non-reg BB |
| --- | --- | --- | --- | --- | --- |
| S1 "A meter found fast is corrected by a refund and ... slow or non_registering by a backbill." | follows | follows | follows | follows | follows |
| S2 "The adjustment period ends on the test date and starts on meter_msr_error_start_date ..." | overwritten (declared) | overwritten (declared) | overwritten (declared) | overwritten (declared) | overwritten (declared) |
| S3 "The corrected charges are the energy, demand and PSCR charges of the regular bills ... (meter_msr_affected_charges)." | overwritten (declared) | overwritten (declared) | overwritten (declared) | overwritten (declared) | not named; governs the quantity only through S5, which is overwritten (declared); the extended recovered charges still comprise energy, PSCR and demand — no divergent quantity |
| S4 "For a fast or slow meter the amount is those charges times abs(1 - 100/registration_pct) ..." | overwritten (declared) | overwritten (declared) | overwritten (declared) | overwritten (declared) | n/a (non-registering) |
| S5 "For a non_registering meter the backbill is computed under non_registering_basis." | n/a | n/a | n/a | n/a | overwritten (declared) |
| S6 "An adjustment smaller than adjustment_threshold_usd is recorded with amount 0.00 and posts nothing." | follows | follows | follows | follows | follows |
| S7 "Each test result is adjusted once." | follows | follows (against referee result) | follows | follows (against referee result) | follows |
| S8 "The refund is credited, and the backbill billed, on the service agreement on the adjustment date." | follows | overwritten (declared: on acceptance date) | follows | overwritten (declared) | follows |
| S9 "Backbills never attract a late payment charge ... payment arrangement ..." | follows | follows | n/a | n/a | follows |

Disguised forms: the anonymous intermediate (target registration 99 / 99.5 in place of 100 in the slow/referee backbill error factor) is inside the declared S4 replacement ("so that the slow-meter error factor is ..." and the rule's tier sentences); the 0/1 multiplier (late-share 0, interest 0) is inside the declared S4 replacement of the refunds; no dropped branch (S1's three classifications are each served). The extended rules contain no "wrong value" / "algorithm to avoid" language about base.

`meter_test_fee_rule` (referenced by repeat test fee): T1 "charged only for a customer-requested test whose result is within_tolerance and only when meter_msr_customer_tests_in_period ... reaches free_tests_per_period" — follows (rule: "when the free-test allowance counted under the agreement-wide allowance rule is already used"); T2 "No fee is charged when the meter is found fast, slow or non_registering, ... periodic or utility-initiated tests, or ... the first test in the period" — follows; T3 "Each test result is charged at most once" — follows ("charged once for that result"); T4 "The fee is the repeat_test_fee_usd of the meter type tested and is posted on the test date" — overwritten (declared).

`meter_agg_agreement_test_allowance` (referenced by repeat test fee): all sentences followed; the escalation counts "earlier customer-requested tests of the same meter", a different quantity from the agreement-wide allowance (not a conflict).

No undeclared override found.

### factor_ladders

Structure only (weight lives in each task's `factor_weight`).

| policy | factor | label | decides | tiers (fall-through last) | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| slow BB | slow_backbill_months_reached | method | sb_months_reached | all months since install / months since schedule effective / half months since anchor | yes (install reason + test history; test history + service account) | null |
| slow BB | slow_backbill_limit | parameter | sb_backbill_limit | 6 / 3 / backbill_max | tier 2 yes (install date + test history + type interval); tier 1 single (install date) | null |
| slow BB | slow_backbill_demand_basis | method | sb_demand_corrected | demand above minimum / all demand / none | yes (schedule demand charge + bills) | service |
| slow BB | slow_backbill_target_registration | parameter | sb_target_registration | 100-tol / 100-tol/2 / 100 | tier 2 conj. of two request kinds (same table) | null |
| ref BB | settlement_months_reached, settlement_limit, settlement_demand_basis, settlement_target_registration | as slow BB | rs_* | as slow BB | as slow BB | demand_basis: service |
| ref BB | settlement_last_bill | method | rs_end_offset | add bills to removal / add all later bills / none | single (installation status/date) | null |
| repeat fee | repeat_fee_base_fee | parameter | tf_base_fee | +IT check / +demand-register check / base | tier 2 conj. (voltage + schedule) | service |
| repeat fee | repeat_fee_lookback | **method** | tf_lookback_months | 24 / 6 / free_test_period_months | single (schedule) | service |
| repeat fee | repeat_fee_escalation | parameter | tf_multiplier | 2.0 / 1.5 / 1 | single (test history) | null |
| repeat fee | repeat_fee_witness_surcharge | parameter | tf_witness_surcharge | 60 / 25 / 0 | yes (request witness flag + result method) | null |
| repeat fee | repeat_fee_band_credit | parameter | tf_band_credit | 100 / 50 / 0 | single | null |
| fast refund | fast_refund_months_reached | method | fr_months_reached | all months since install / months since schedule effective / half months since anchor | tier 2 yes | null |
| fast refund | fast_refund_limit | parameter | fr_refund_limit | 18 (LP) / 15 (GD) / refund_max | single | service |
| fast refund | fast_refund_demand_basis | method | fr_demand_corrected | as slow BB | yes | service |
| fast refund | fast_refund_late_charges | parameter | fr_late_share | error factor / 1 / 0 | yes (schedule + late charges) | service |
| fast refund | fast_refund_interest | parameter | fr_interest_rate | rate / rate/2 / 0 | single | null |
| fast refund | fast_refund_last_bill | method | fr_end_offset | as ref BB | single | null |
| ref refund | the same six factors, rr_* | same labels | rr_* | same tiers (settlement_* params) | same | limit, demand, late: service |
| non-reg BB | nonreg_bills_covered | method | nr_bills_covered | zero-kWh count / months since install capped / half months capped | tier 2 yes | service |
| non-reg BB | nonreg_demand_recovered | method | nr_demand_recovered | prior minus billed / none / prior in full | yes (schedule + bills) | service |
| non-reg BB | nonreg_overdue_share | parameter | nr_overdue_share | 0.5 / 0.75 / 1 | yes (type interval + test history/install date) | null |
| non-reg BB | nonreg_reporting_share | parameter | nr_reporting_share | 0.8 / 0.9 / 1 | yes (test request + bills) | service |

Counts per policy: slow BB 4 (2 parameter, 2 method); ref BB 5 (2 parameter, 3 method); repeat fee 5 (4 parameter, 1 method as labelled); fast refund 6 (3 parameter, 3 method); ref refund 6 (3 parameter, 3 method); non-reg BB 4 (2 parameter, 2 method). Every ladder has three pairwise-disjoint tiers, each stated in the rule with its value or method and implemented in compute; `decides` is never `result`; binding sets are disjoint within each policy; each fall-through tier equals the factor's `baseline`, and each `baseline` matches `baseline.rule`.

Charter-global ladder findings (consequence demonstrated, where demonstrable, in the task files):

- **F-LADDER-1 (mislabelled effect), repeat_fee_lookback.** Labelled `method`, but its three tiers only substitute a different number of months (demand-schedule look-back 24, residential look-back 6, free_test_period_months 12) into the same count ("The repeat escalation multiplier counts the earlier customer-requested tests of the same meter requested within the escalation look-back ..."). That is a `parameter` by the definition (a tier that substitutes a different number into the same formula). With it relabelled, `meter_ext_repeat_test_fee` has zero `method` factors (< 1). Bears on task 1.
- **F-LADDER-2 (unreal tier), fast_refund_months_reached / settlement_refund_months_reached, tier 1.** Rule: "Where the customer requested tests of the meter within the meter type's free_test_period_months ... before the company test date, the customer's complaints show the error may predate every test (a customer test that had found the meter outside tolerance would have taken it out of service, so each of those tests found it within tolerance), and the billing months the fast-meter refund reaches back are all the whole calendar months between the installation date and the company test date." The condition is that recent accuracy tests found the meter accurate, and the method dates the over-registration back past those very tests to installation. A utility's recorded within-tolerance test is its evidence that the meter was accurate on that date — the base charter itself anchors the error start at "the later of the installed date and the last previous test date" (`error_start_basis`). No utility publishes a refund rule that, because its tests certified the meter accurate, refunds over-registration for the months those tests certified. Bears on task 1 (both refund computations take this tier).
- Observation, fast_refund_limit / settlement_refund_limit tier 2: the rule justifies the tier with "Large and medium demand customers receive their interval data every day, so their refunds reach back less far", yet the Schedule GD value (15 months) exceeds the refund_max_months of the AMI Interval Demand Meter (12), the meter type a GD customer at secondary voltage holds. No task world in this difficulty takes the GD tier of a refund limit (task 1's refund agreement is LP on a Primary Metering Installation, 18 < 24), so no consequence is demonstrable.
- Observation, nonreg_demand_recovered fall-through: the fall-through (schedule without a demand charge) recovers "the prior-year bills' demand charges in full", which on such a schedule are 0.00 unless the schedule changed within the year, so in effect it selects the same zero as tier 2; and the baseline rule applied to a demand schedule recovers the prior-year demand in full without netting the demand already billed. Task 1's world takes tier 1 (shown in `1.md`), where neither point moves the scored value.
- Observation, slow_backbill_target_registration / settlement_target_registration: correcting only to the tolerance edge when the company itself initiated the test, and to the half-band for a periodic test, is an unusual but internally coherent mitigation; not demonstrable as a treatment no utility could publish.
- Observation: the repeat-test-fee prerequisite (E4) charges a fee that the fast-meter refund returns in the same transaction; the fee is a net-zero movement for the customer and cancels out of the referee refund settlement (settlement adds every repeat fee and subtracts the fast-meter refund that already includes it). The edge bears weight on the fast-meter refund itself (shown in `1.md`).

### findings

1. F-LADDER-1 — SOURCE-FACTOR RED candidate (mislabelled `method`; repeat-fee computation left with no `method` factor). Bears on task 1; demonstrated in `1.md`.
2. F-LADDER-2 — SOURCE-FACTOR RED candidate (unreal tier in the two refund months-reached ladders). Bears on task 1; demonstrated in `1.md`.
3. Observations (no demonstrable consequence in either world): bill-window approximation in compute; "covers" vs "counts back" in the fast-meter interest tier; complaints window admits post-test requests; E3 gate is a field rather than an eligibility id; E4 resolvable only for a single owed fee; settlement docstrings restate "on top of whatever ... already stands"; tools post no service-side trigger rows; YAML authoring comments; GD refund-limit rationale contradicts its value; non-registering demand fall-through vacuous; target-registration tiers unusual; repeat fee charged and returned in one transaction.
4. Task 0 (slow-meter backbill + referee backbill settlement) is touched by no charter-global RED candidate; its file still checks every per-task relationship on its own world.

## closing_checklist

Written after both reveals (2026-10-07T21:30:30Z); everything above this heading was frozen before any reveal.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; first revision (no older revisions).
- Comparison verdicts: task 0 PASS on all four relationships; task 1 **SOURCE-FACTOR RED** (F1 = F-LADDER-1 mislabelled method, repeat-fee computation has no method factor; F2 = F-LADDER-2 unreal months-reached tier in the fast-meter refund and referee refund settlement). Policy self-consistency, problem tree and unique solution PASS for task 1.
- Coverage and scope: GT `charter_scope` task 0 = {slow_meter_backbill, referee_backbill_settlement}, task 1 = {repeat_test_fee, fast_meter_refund, non_registering_backbill, referee_refund_settlement} — pairwise disjoint over whole trees, jointly cover all six extended policies; tools closed; uuid8s independent (see action_binding_and_uuids).
- Trees: task 0 n=1 (1 value_input), task 1 n=3 (2 value_input, 1 state_gate); each has an owner=user write (the referee settlement); difficulty-wide prerequisite graph acyclic (two disjoint components).
- Factors: every computation declares a self-sufficient baseline and 4-6 factors with honest baselines that bear weight on its world; the repeat-fee computation fails the 1-`method` floor once its look-back factor is labelled honestly, and the two refund computations take a months-reached tier that fails the business-reality test.
- Difficulty does **not** close: Step 4 requires all tasks PASS. The instantiation-stage gate re-run on the final form is not performed by this audit (gate snapshot from the coordinator is cited in charter_global_frozen; check_traceability deferred).

## revision_2

Re-audit round 2. The text above (round 1) is left untouched. This section is written before either round-2 task file was opened, and contains nothing derived from a round-2 GT.

### charter_global_frozen (revision_2)

- Freeze time: 2026-10-07T22:46:18Z. Auditor: same independent policy-task auditor.
- Inputs (sha256 re-verified against the round-2 MANIFEST): `meter.extended.yaml` = `9c70d6ba66cd98a3a7496fa2cb25434bfa55e5d7ac93af44c0749e0ebc5afc9f` (**changed** from round 1 `09087215...`); `task_tools.py` = `051515011c5d1e8368eddf6e27e8284f32564a2dd7ad1aee3cae77267f8fe556` (unchanged); views: task_0 `2bd3cc4e...` (unchanged, byte-identical to `round1/task_0.view.json`), task_1 `a1ebca18...` (changed: seed only; frozen_time and user_scenario identical to round 1).
- Because the charter hash changed, every charter-global section is re-derived in full below. Sections that rest only on `task_tools.py` (tool bodies, owners, docstrings, uuid8s) are carried forward by reference to round-1 `action_binding_and_uuids` on the ground that the tool hash is unchanged; the `(target_tool, computes)` claim check is re-run because it lives in the charter.
- Gate snapshot (coordinator, after rework): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK ("suite depth: history_rows_max=32(>= 8) branches_max=111(>= 5)"); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; check_traceability deferred. Inputs complete.
- Base copy: `head -954` still equals `blueprint/products/meter.yaml` except one trailing blank line — verbatim.
- Masked and unread at freeze: `tasks/0.json` (now `b5d63d6e...`), `tasks/1.json` (now `0aad4892...`).

### what changed in the charter (located by re-reading every extended policy against the round-1 text quoted in this file)

- `meter_ext_slow_meter_backbill`, `meter_ext_referee_backbill_settlement`, `meter_ext_non_registering_backbill`: rule, overwrite, params, prerequisite, compute, factors and baseline are content-identical to round 1 (YAML re-flowed only).
- YAML authoring comments ("# Task 0 — ...") removed (round-1 observation closed).
- `meter_ext_repeat_test_fee`: the look-back factor and its params (`demand_schedule_window_months`, `residential_window_months`) are gone; the rule now says "The repeat escalation multiplier rests on the earlier customer-requested tests of the same meter counted before the charged test's request. Under the standard method the earlier customer-requested tests counted are those requested within the meter type's free_test_period_months ... How they are counted follows the meter's own test record, because on demand schedules a periodic company test of the installation is the accuracy check of record. Where the rate schedule carries a demand charge and the meter carries a periodic test request, that periodic test starts the count afresh, and the earlier customer-requested tests counted are those requested after the meter's latest periodic test request, whenever they fall. Where the rate schedule carries a demand charge and the meter carries no periodic test request, every earlier customer-requested test of the meter since its installation is counted. In every other case the earlier customer-requested tests are counted as the standard method counts them." New factor `repeat_fee_count_basis` (method, decides `tf_earlier_tests`, bindings `tf_latest_periodic`, `tf_earlier_tests`); `baseline.rule` gains the standard counting sentence.
- `meter_ext_fast_meter_refund` and `meter_ext_referee_refund_settlement`: the months-reached tier 1 is now "Where the meter's latest within-tolerance result already lay in the outer drift share of the tolerance band, on the same side of 100 as the company test's registration_pct, ... the billing months ... are all the whole calendar months between the test date of that within-tolerance result and the company test date", with the governing sentence "they never reach back past the meter's latest within-tolerance result, which is the company's evidence that the meter registered within tolerance on that date"; new param `drift_share` / `settlement_drift_share` 0.75; new bindings `fr_last_registration`, `fr_drift` (rr_ likewise); the complaints binding is gone. The "Large and medium demand customers receive their interval data every day ..." sentence is removed. Params changed: large-power limit 18 -> 3, medium-demand limit 15 -> 6, half-interest bills 6 -> 3.
- Fast-meter refund interest sentence now reads "Where the fast-meter refund counts back at least the full-interest number of bills ... Where it covers at least the half-interest number of bills but fewer than the full-interest number ..."; the referee refund settlement says "counts back" in both tiers.

### policy_conflict_scan (revision_2)

Re-run in full: the six policies, their `(target_tool, computes)` pairs, owners, subjects and prerequisite edges are as in the round-1 table; objects remain disjoint by classifying result; time anchors unchanged; cross-category reads now: repeat fee reads `service_voltage`, `demand_charge_usd_kw` (no longer `variant_name`). No conflict. Scope partition per the policies' content: {slow BB, referee BB} and {repeat fee, fast refund, non-reg BB, referee refund} — disjoint, jointly complete (confirmed against `charter_scope` only after reveal).

### rule_compute_equivalence (revision_2)

All `compute_basis` quotations re-located verbatim in their rules (including the new `tf_latest_periodic`, `tf_request_offset`, `fr_last_registration`, `fr_drift`, `rr_*` counterparts). Every ladder tier appears in rule and compute both ways.

- `tf_earlier_tests` tier 1 is implemented as customer requests with `MONTHS(request_date, NOW) < MONTHS(latest periodic request, NOW)`, minus one. Equivalent to "requested after the meter's latest periodic test request" except when a customer request falls in the same NOW-relative month bucket as the periodic request — the same day-of-month approximation as round-1 item 1. Verified on task 1's rows (in `1.md` revision_2): identical sets.
- `fr_drift` = `|last within registration - 100| >= drift_share x tolerance` AND same sign as the company result's deviation — matches "lay in the outer drift share of the tolerance band, on the same side of 100 as the company test's registration_pct". Tier 1 months = `MONTHS(latest within date, company date)` — matches. Tier 2 requires a within-tolerance result ("after its test date") — matches `fr_last_within_tolerance != None`.
- Round-1 item 1 (bill windows by NOW-relative months): unchanged — **observation**, re-checked on task 1's new rows in `1.md`.
- Round-1 item 2 (interest "covers" vs "counts back"): **partly closed**. The referee refund settlement now says "counts back" in both tiers. The fast-meter refund now says "counts back" in tier 1 but still "Where it **covers** at least the half-interest number of bills but fewer than the full-interest number" in tier 2, while compute uses the counted-back count for both. A world where counted-back < 3 <= covered would give two readings; consequence checked on task 1's world in `1.md` — **observation** unless demonstrated there.
- Round-1 item 3 (complaints window): **closed** — the binding no longer exists.
- The fast-meter refund's interest sentence ends "simple interest for half the counted-back period"; the referee refund settlement's ends "half the repriced period" while multiplying by the bills counted back — descriptive gloss, no quantity changes (observation, carried).

### action_binding_and_uuids (revision_2)

Carried forward from round 1 (tool hash unchanged). Claims re-checked: each `(target_tool, computes)` still claimed by exactly one policy.

### prerequisite_graph (revision_2)

Re-run: same four edges E1-E4, same `policy_source` strings (verbatim in their rules), same kinds, gates (`rs_already_backbilled`, `rr_already_refunded`, `fr_fees_returned` still exist in compute; E3 gate `meter_adjustments.meter_test_id`), forms, resolved_by. Acyclic. E3's field-not-eligibility-id gate remains an observation. No authoring-viewpoint wording anywhere (comments removed).

### prerequisite_sentences (revision_2)

The four sentences are unchanged and re-pass the four-point test; each waited-on state is still brought about by exactly one write; the depended-on rules (slow BB, fast refund, non-reg BB, repeat fee) carry no restatement. The repeat-fee rule's object sentence is unchanged (single latest owed fee), so the E4 "every owed fee" scope observation stands, to be checked against task 1's new seed. No undeclared cross-problem order introduced: the new count-basis sentences read the meter's own periodic test request (a record, not another problem's write).

### override_declarations (revision_2)

Re-run sentence by sentence. `meter_accuracy_adjustment_rule` S1-S9: conclusions identical to the round-1 table for all five adjustment policies (the drift tier lives inside the declared S2 replacement). `meter_test_fee_rule` T1-T3 followed, T4 overwritten (declared, unchanged). `meter_agg_agreement_test_allowance`: the new count basis concerns the escalation count "of the same meter", not the agreement-wide allowance — no conflict. No undeclared override.

### factor_ladders (revision_2)

| policy | factors (label) | parameter / method |
| --- | --- | --- |
| slow BB | unchanged (4) | 2 / 2 |
| ref BB | unchanged (5) | 2 / 3 |
| repeat fee | base_fee (P), **count_basis (M)**, escalation (P), witness (P), band_credit (P) | 4 / 1 |
| fast refund | months_reached (M, drift tier), limit (P), demand_basis (M), late_charges (P), interest (P), last_bill (M) | 3 / 3 |
| ref refund | the same six, rr_* | 3 / 3 |
| non-reg BB | unchanged (4) | 2 / 2 |

- **F-LADDER-1 re-check (repeat fee): closed.** `repeat_fee_count_basis` tiers select different counting rules — a count reset at the meter's latest periodic test request, a count of every customer test since installation, or a rolling free_test_period_months window. Each tier draws the boundary of the counted set from a different record (periodic request date, installation date, or a fixed span before the charged request); that is a change in how the quantity is computed, not one number swapped into the same formula. Label honest; the repeat-fee computation has 1 `method`. Tier 1 is multi-source (schedule demand charge + the meter's periodic request). Business reality: resetting a repeat-test escalation at the company's own periodic accuracy check of record is a recognisable practice; no straw tier. Fall-through = baseline = baseline.rule's added sentence.
- `repeat_fee_escalation` now lists `tf_charged_request_date`, `tf_request_offset` as bindings; binding sets remain disjoint across the five factors.
- **F-LADDER-2 re-check (refund months): closed at the charter level.** The complaints tier is gone. The new tier 1 dates the error from the latest within-tolerance test when that test already sat in the outer 75% drift share on the same side as the failing result — the error is still bounded by the company's last accurate evidence (the rule now says so outright), and the choice between "from that test" and "from the midpoint" is a real dating question utilities weigh. Tier 1 is multi-source (two test results). Tier 2 and fall-through unchanged.
- Refund limit (both refunds): LP 3, GD 6, otherwise refund_max_months. The round-1 GD observation is closed (6 < 12, and the contradicting rationale sentence is removed). The rule now gives no reason for shorter limits on LP/GD; a 3-month cap on a large-power refund against the Primary Metering Installation's 24 is a sharp but not unpublishable treatment — observation.
- Interest half tier now 3 bills (both refunds).
- Non-registering demand fall-through vacuity and target-registration tiers: unchanged observations.

### findings (revision_2, charter-global)

1. F-LADDER-1: closed at the charter level (count_basis is an honest method).
2. F-LADDER-2: closed at the charter level (complaints tier removed; drift tier bounded by the latest accurate test).
3. New / remaining observations: fast-meter refund interest tier 2 still says "covers" (partial closure of round-1 item 2); 3-month LP refund limit has no stated reason; count-basis tier 1 implemented by the NOW-relative month approximation; the rest as round 1 item 3 minus the closed ones (complaints window, GD limit, YAML comments).
4. Task 0's two policies are content-identical to round 1 and its view is byte-identical; regression check in `0.md` revision_2.

### closing_checklist (revision_2)

Written after the round-2 reveals (2026-10-07T22:47:11Z).

- Files: `_difficulty.md`, `0.md`, `1.md`, each with round 1 untouched and `## revision_2` appended; every revision_2 comparison carries PASS.
- Round-1 REDs: F1 / F-LADDER-1 closed; F2 / F-LADDER-2 closed. No new RED; no regression in task 0 (its policies and view unchanged; GT values identical to round 1).
- Coverage and scope: GT charter_scope task 0 = {slow BB, referee BB}, task 1 = {repeat fee, fast refund, non-reg BB, referee refund}; pairwise disjoint over whole trees, jointly cover all six extended policies; tools closed; uuid8s independent (tool module unchanged).
- Trees: task 0 n=1 (1 value_input), task 1 n=3 (2 value_input + 1 state_gate); each has the owner=user referee settlement; difficulty graph acyclic.
- Factors: every computation has a self-sufficient baseline and 4-6 factors with >= 2 parameter and >= 1 method (repeat fee now 4/1); each task has multi-source and cross-difficulty (service) factors; every factor bears weight against an honest baseline; each all-baseline differs from gold.
- Remaining observations (not grounds for rework): fast-meter interest tier 2 "covers" wording; unexplained 3-month LP refund limit; NOW-relative month windows; E3 gate is a field; E4 resolvable for a single owed fee; settlement docstrings' "on top of whatever ... already stands"; no service-side trigger rows; non-registering demand fall-through vacuity; target-registration tiers unusual; repeat fee net-zero inside the refund.
- Gate re-run on the final form: the coordinator's round-2 snapshot (all OK, check_traceability deferred) is the re-run of record; this audit does not run gates.
- The difficulty passes the source-layer audit.
