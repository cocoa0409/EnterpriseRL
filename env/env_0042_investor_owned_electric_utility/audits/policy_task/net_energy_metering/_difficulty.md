# Policy-task audit — net_energy_metering / charter-global

## charter_global_frozen

- Freeze time: 2026-10-07T21:30Z (written before any task's GT was revealed; nothing here derives from a revealed GT).
- Auditor: independent erl-task-policy-audit run (not the authoring agent).
- Frozen inputs (sha256, re-computed and matching `audits/views/policy_task/net_energy_metering/MANIFEST.txt`):
  - `tasks/net_energy_metering/nem.extended.yaml` ce20ee69d78acd2c008b50fa747335386ef0774e69093521791664a182420f68
  - `tasks/net_energy_metering/task_tools.py` fa5f599dfecd5da690ef7e44c853c7eea4991322e98c7ebc47621bf1ba8f0313
  - also read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{nem,service,meter,dr}.yaml` (parameters and rule sentences only).
- Permitted: the charter (base + extended), the tool module, the schema, the shared tools, the masked task views (frozen_time / user_scenario / initial_state).
- Masked and unread at freeze: every field of `tasks/*.json` other than the three above (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*).
- Entry conditions (Step 0): gate snapshot supplied by the coordinator — check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK ("suite depth: history_rows_max=72(>= 8) branches_max=70(>= 5)"); check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred (KB not yet published). Masked views and MANIFEST present; hashes match. Entry conditions satisfied; gates were not re-run by this auditor.
- Read-domain note: a scoped `grep` for the DSL function names, run over `erlbench/` and `skills/erl-task-instantiate/scripts/`, printed a few lines of `check_compute.py` (the docstring and the `_within` helper: a row is "within_months=N" when the whole months from its date to NOW satisfy 0 <= m < N). That script contains no task GT. The DSL is otherwise read from the prose of each rule, which defines "whole calendar months" and "dated in the 12 months before".

### policy_conflict_scan

The charter has 6 extended policies on top of the 10 base policies. The base copy (lines 1-961 of the extended file) is byte-identical to `blueprint/products/nem.yaml` (checked with `diff`).

| Subject (event) | Policies that decide it | Result |
| --- | --- | --- |
| nem_export_credit (rates and amount of a banked credit) | base nem_export_credit_calculation; ext nem_ext_export_credit_revaluation (revalues "the most recent export credit"); ext nem_ext_estimated_export_credit (books a credit for an estimated-read period at "the rate recorded on the preceding export credit") | **CONFLICT F1**: once an estimated credit is booked, it becomes "the most recent export credit". The revaluation rule then fixes rates for it that differ from the rates the estimated rule gave it. See findings. |
| nem_true_up_forfeiture (anniversary) | base nem_true_up_rule; ext nem_ext_carried_credit_expiry | Declared override. The base forfeit branch for NEM-A is dropped (observation O3). |
| nem_true_up_payout (anniversary) | base nem_true_up_rule; ext nem_ext_anniversary_cash_out | Declared override. Compatible with the expiry rule: the order between them is fixed by a prerequisite sentence. |
| nem_termination + settlement | base nem_true_up_rule, nem_modification_transfer_termination; ext nem_ext_move_out_termination (stopping service, no transfer, cash-out rider); ext nem_ext_requested_termination (keeping service, cash-out rider) | The two extended scopes are disjoint ("stopping electric service at the address" vs "keeping electric service at the address"). There is an undeclared conflict with the base check-minimum sentence (O1). The base forfeit-rider termination branch is dropped (O3). |
| Cross-rule state_due interplay | expiry and anniversary (state_due) vs move-out (on_request) | Move-out carries no sentence waiting on an owed anniversary cash-out, while requested termination does. If a move-out world had an owed anniversary cash-out, the order would not be fixed (O4). Task 0's world owes none: the bank was 0.00 at the 2026-03 true-up (see 0.md). |
| Time anchors | All windows anchor on NOW (the booking or termination) with "12 months before" and on whole calendar months from the PTO date. Revaluation anchors on the credit's billing_period_end. | Consistent. |
| Cross-category read boundaries | service (schedule params, bills, SA status, space_heating), meter (interval length or type of the in-service meter), dr (EXISTS active) | Reads only. No extended rule writes another category. |

Claimed scopes (derived from the prerequisite graph, before reveal): task 0 = {nem_ext_move_out_termination <- nem_ext_estimated_export_credit <- nem_ext_export_credit_revaluation}; task 1 = {nem_ext_requested_termination <- nem_ext_anniversary_cash_out <- nem_ext_carried_credit_expiry}. The two scopes are pairwise disjoint and together cover all 6 extended policies (to be confirmed against `charter_scope` after reveal, in the task files).

### rule_compute_equivalence

Check 2 was run binding by binding against each `compute_basis`. Every binding quotes a rule sentence verbatim, and every ladder tier is stated in the rule's prose and implemented in the `decides` binding. Every `baseline.rule` sentence occurs verbatim in its `rule`. Every `overwrite.replaced_by` occurs verbatim in its `rule`, and every `superseded_clause` occurs verbatim in the cited base rule (all checked by script).

Points examined:
- Revaluation: `xr_summer` and `xr_read` select the bill by `billing_period_end=xr_end` ("the service bill whose billing period ends on the export credit's billing period end"). `xr_pscr` = RND(PSCR*0.60,5) for the less-NBC basis. `xr_months_operating` = MONTHS(PTO, xr_end). Rates RND 5 and the amount RND 2 once. Equivalent.
- Estimated: `ye_scale` tier 1 = (DAYS+1)/(DAYS+1) ("both days included") and tier 2 = DAYS/DAYS ("first day excluded"), RND 4. Factors multiply in the stated order, then RND 0 once. `ye_on` = RND(total*share,0). Equivalent.
- Move-out: `u_avg_offset` tier 1 sums regular bills only and tier 2 all bills, both "dated in the 12 months before the termination". `u_months_op` = MONTHS(PTO, NOW). Equivalent, except for **O5**: `u_other_active = EXISTS('service', status='active')` does not exclude the hosting agreement, while the rule says "another service agreement". The two diverge whenever the hosting agreement is itself active (offsettable tier 2). No task has that world, so this is an observation.
- Expiry, anniversary, requested termination: each binding matches its quoted sentence. The prose states no rounding point that compute does not implement, and compute implements no rounding point the prose omits.
- The rule makes no empty promise; compute invents no basis.

Result: PASS, with observation O5.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: revalue_export_credit_a4b62fb5/revalued_credit_usd; book_estimated_export_credit_93ce1e35/estimated_credit_usd; end_net_metering_at_move_out_0a8cee83/payout_usd; expire_carried_credit_d622768b/expired_credit_usd; settle_anniversary_cash_out_0ae9f9d5/payout_usd; end_net_metering_on_request_0babfbf5/payout_usd. Each tool is claimed by exactly one policy.
- Owners: the two terminations are `owner="user"` and the other four are `owner="agent"`. These match the blueprint summary ("terminating the agreement is the customer's own decision").
- Function bodies: no tool reads a policy precondition, a status, or another row's existence. Each writes what it is passed. The revalue tool reads only the entry's prior amount to move the bank. The book tool creates the row and adds the amount. The end tools always pay "check" and zero the bank. No tool refuses or hints when a prerequisite is unresolved.
- Docstrings name no other task tool and state no write sequence. Ordering words occur only as read-lookup provenance ("read from the ... lookup before the call") and as effect description ("Afterwards the history shows ..."), so this is an observation only.
- **uuid8 independence (finding U1)**: three of the six tails — `0a8cee83`, `0ae9f9d5` and `0babfbf5` (the two terminations and the anniversary cash-out) — fall inside one 0.44% slice of the 32-bit space (0x0a8cee83..0x0babfbf5). The gaps are 0x5d0b52 and 0xc20220. Read as 100-ns UUIDv1 time_low ticks, that is about 0.6 s and 1.3 s apart. Six independent uniform draws put three of them that close with probability around 1e-3. They look like adjacent values from one sequential generator rather than independently generated tails. The other three (`a4b62fb5`, `93ce1e35`, `d622768b`) show no pattern. This changes no scored value, so it is recorded as a check-3 defect without a scored consequence: the Step-4 checklist item "each task tool uses an independently generated, frozen uuid8" cannot be ticked.

### prerequisite_graph

| Policy | prerequisite | kind / gate | form | resolved_by = depended-on target_tool | gate exists in compute |
| --- | --- | --- | --- | --- | --- |
| nem_ext_export_credit_revaluation | [] | — | — | — | — |
| nem_ext_estimated_export_credit | nem_ext_export_credit_revaluation | value_input / ye_rate_on | state | revalue_export_credit_a4b62fb5 ✓ | ye_rate_on ✓ |
| nem_ext_move_out_termination | nem_ext_estimated_export_credit | value_input / u_bank | state | book_estimated_export_credit_93ce1e35 ✓ | u_bank ✓ |
| nem_ext_carried_credit_expiry | [] | — | — | — | — |
| nem_ext_anniversary_cash_out | nem_ext_carried_credit_expiry | value_input / an_bank | state | expire_carried_credit_d622768b ✓ | an_bank ✓ |
| nem_ext_requested_termination | nem_ext_anniversary_cash_out | value_input / v_bank | state | settle_anniversary_cash_out_0ae9f9d5 ✓ | v_bank ✓ |

- Every policy fills `prerequisite`. Every `problem` names an extended policy in this file (never a base policy, never itself). The graph is two chains, so it is acyclic.
- Each `policy_source` occurs verbatim in its own `rule` (checked by script). No edge is action-form, so no `fallback_reason` is needed.
- Each `condition` matches the sentence's scope. "Every billing period billed ... since permission to operate" is matched by "every service_bills row ... after the PTO date". "The expiry entry owed" is matched by "whenever the carried credit left unused is above zero". "The anniversary cash-out owed for every true-up bill" is matched by "for every service bill dated in the true_up_month ... whose bank called for a cash-out". None is strengthened or weakened.
- `effect` statements are true of the binding: resolving the edge changes the gate binding's value.
- No authoring-viewpoint phrasing (e.g. "in this task") appears. "The current true-up month" in one `condition` is a general phrase.
- Result: PASS.

### prerequisite_sentences

Four-point test, one edge at a time:

1. estimated <- revaluation: "The estimated export credit is fixed only after the most recent export credit in the net metering history carries the per-kWh rates that the revaluation of export credits fixes for it."
   - Connective "only after" ✓. State form: the rates recorded on a ledger row ✓. No tool name, id or snake_case ✓. Scope matches the condition ✓.
   - Exactly one write brings the state about: the revalue tool. The only other export-credit write, the estimated booking, creates a new row and cannot set the waited-on row's rates.
   - Derivation: the reader sees that the latest export credit's recorded rates differ from those the revaluation rule computes for it. The revaluation rule ("When the per-kWh rates recorded on that export credit are not the rates this rule fixes, the credit is revalued") is the one rule that rewrites them. Single reading.
2. move-out <- estimated: "The move-out settlement is not fixed until every billing period billed on the hosting service agreement since permission to operate has an export credit in the net metering history."
   - "not ... until" ✓. State ✓. Clean wording ✓.
   - One write banks an export credit for a period that has none: the estimated rule ("the export credit of a billing period whose service bill was issued on an estimated closing read and which has no export credit"). Single reading, provided the missing period's bill is an estimated read.
   - Observation O6: no rule books a missing credit for an actual-read period, so in such a world the edge would be unresolvable. Not the case in task 0.
3. anniversary <- expiry: "The anniversary cash-out is fixed only after the bank carries the expiry entry owed for credit carried into the closing true-up year and left unused by its bills."
   - "only after" ✓. State ✓. Clean wording ✓.
   - The anniversary forfeiture is written only by the expiry tool; the end tools write termination-kind forfeitures. Single reading.
4. requested termination <- anniversary: "The requested-termination settlement is not fixed until the bank carries the anniversary cash-out owed for every true-up bill issued since permission to operate."
   - ✓ on all four points. The anniversary-kind payout is written only by the settle tool. Single reading.

Other checks on the sentences:
- No depended-on rule restates the sentence that waits on it.
- No extended rule states a cross-problem order that grounds no edge. ("It is trued up at the next actual read" in the estimated rule is a future event, not an order between problems.)
- Two base sentences carry cross-problem orders: "the seller's bank is settled under bank_disposition_on_sale before the move" and "a customer who wants net metering must first return to a communicating meter". No tree rests on either, so both are observations (O7).

Result: PASS.

### override_declarations

Sentence-by-sentence sweep of each `base_policy_refs` entry:

- nem_export_credit_calculation (refs of revaluation and estimated):
  - S1 "Each billing period ... banks one export credit" — followed.
  - S2 "Exported kWh are split into on-peak and off-peak exports under the rider's export_on_peak_window." — **handled differently, undeclared, in two places**:
    - (a) Revaluation tier "the closing read is a customer read": on-peak = total x 0.22. This replaces the measured window split.
    - (b) Estimated on-peak share keys on "the schedule has on-peak hours". Under NBT riders the export window is "15:00-20:00 ... whatever the service agreement's rate schedule", so an NBT agreement on a flat schedule would get on-peak share 0 where the base window gives on-peak exports.
    - Neither appears in an `overwrite`. Neither task world reaches (a) or (b) (no customer_read bill; task 0's rider is NEM-R on RT), so both are recorded as observation O2.
  - S3 "Under credit_basis retail_energy_rate ...; under retail_energy_rate_less_nbc that rate less nonbypassable_charge_usd_kwh;" — declared by **both** extended policies with **different** `replaced_by` texts. That is the root of F1.
  - S4 "under avoided_cost_export_rate at the rider's export rates" — outside revaluation's scope; the estimated rule copies the preceding credit's rates, which is consistent.
  - S5 (rates recorded, rounded to the cent) and S6 (operating only; grid-charged battery export) — followed.
- nem_program_interactions — no sentence touched.
- nem_true_up_rule (refs of move-out, expiry, anniversary, requested termination):
  - S1 settle the residual at the true-up bill and at termination — followed.
  - S2 "At an anniversary true-up, cash_out pays the residual, carry_forward leaves it in the bank, and forfeit zeroes it." — declared by expiry and by anniversary. The replacements cover cash_out and carry_forward only; the forfeit (NEM-A) branch has no replacement (dropped branch, O3).
  - S3 "At termination the residual is settled under termination_disposition." — declared by move-out and requested termination. Both replacements are scoped to cash-out riders; the forfeit-rider termination is dropped (O3).
  - S4 "A payout of at least payout_minimum_check_usd is paid by check; a smaller payout is credited to the service agreement." — **not declared** by move-out ("the move-out payout is paid by check") or by requested termination ("the requested-termination payout is paid by check"). Both say check with no minimum. The tools hard-code `payout_method="check"`. This is an undeclared override (O1); it matters only for a payout below $25 (residential) or $100 (business). The anniversary rule restates the minimum consistently.
  - S5 "A residual of zero settles nothing." and S6 "settled once ... operating or terminated" — followed.
- nem_modification_transfer_termination: the modification and transfer sentences are untouched, and both extended scopes exclude transfer. "the bank is then settled under termination_disposition." is declared by both terminations.

Findings only. Each task file demonstrates or rules out a consequence on its own world.

### factor_ladders

Per policy: declared factors, effect label, tier count, and whether the ladder is real within the policy's own scope. Charter facts used by the reachability tests:
- (i) meter.yaml: every `bidirectional: true` meter has `interval_length_minutes: 15`, and both non-bidirectional meters have 0 or 60.
- (ii) meter_installation_lifecycle: "a net energy metering agreement needs a bidirectional meter".
- (iii) nem_review_and_permission: "Permission to operate requires a bidirectional meter in service at the address", plus nem_program_interactions on opt-out meters.
- (iv) service_bill_calculation and service_stop_and_final_bill: "a final bill is issued when the agreement closes"; "Every closure issues a final bill".

Together (i)-(iii) mean the meter in service for every **operating** agreement records 15-minute interval data. By (iv), a final bill exists only on a closed agreement.

| Policy | Factor (label) | Tiers | Reachable within the rule's scope? | Verdict |
| --- | --- | --- | --- | --- |
| revaluation | seasonal_energy_rates (parameter) | 3 | yes | ok |
| revaluation | time_of_use_split (method) | 3 | yes | ok |
| revaluation | supply_cost_component (parameter) | 3 | **no**: the scope is "an agreement whose rider values exports at a retail rate (the legacy rider and the residential successor rider and the aggregated rider)", whose credit_basis values are retail_energy_rate (NEM-L) and retail_energy_rate_less_nbc (NEM-R, NEM-A). The fall-through "otherwise nothing is added" (= the baseline) is the avoided-cost basis, which never reaches this write. | **F2 unreal ladder**: two real tiers; the baseline is a treatment the rule gives no in-scope agreement |
| revaluation | non_bypassable_charge_phase_in (parameter) | 3 | yes (fall-through = legacy rider) | ok |
| estimated | billing_day_scaling (method) | 3 | **no**: both non-fall-through tiers carry "its closing read is estimated", which holds of every agreement reaching this write (scope: "a billing period whose service bill was issued on an estimated closing read"). The fall-through "scaling ratio is 1" is unreachable. The two reachable tiers differ only by the +1 day-count convention, i.e. a number in one formula, not a method. | **F3 unreal ladder + mislabelled** |
| estimated | daylight_shift (parameter) | 3 | yes | ok |
| estimated | vacancy_uplift (parameter) | 3 | **no**: tier 2 "a final bill and the hosting service agreement is not closed" contradicts (iv) | **F4 unreal ladder** (two real tiers) |
| estimated | provisional_estimate_factor (parameter) | 3 | **no**: "the meter in service ... records 15-minute interval data" holds of every operating agreement by (i)-(iii); the fall-through is unreachable | **F5 unreal ladder** |
| estimated | estimated_on_peak_share (parameter) | 3 | yes | ok |
| move-out | offsettable_charge_average (method) | 3 | yes | ok |
| move-out | full_value_months (parameter) | 3 | yes (business cash-out riders reach "otherwise") | ok |
| move-out | tenure_months (parameter) | 3 | yes | ok |
| move-out | surplus_share (parameter) | 3 | yes | ok |
| move-out | staying_uplift (parameter) | 3 | yes | ok |
| move-out | estimated_read_holdback (parameter) | 3 | **no**: tier 2 "... and the meter does not record 15-minute interval data" is unreachable for an operating agreement by (i)-(iii); the "15-minute" part of tier 1 holds of everyone | **F6 unreal ladder** |
| expiry | carried_credit_drawing_order (method) | 3 | yes (NBT-R/NBT-C on flat schedules; NEM-L/R on "otherwise") | ok |
| expiry | estimated_read_reserve (parameter) | 3 | yes | ok |
| expiry | tenure_expiry_share (parameter) | 3 | yes (edge case: second true-up bill dated before the PTO day-of-month) | ok |
| expiry | grid_access_exempt_amount (parameter) | 3 | weakly: base charges every billing period of an avoided-cost agreement, so "fewer than 12" arises only with irregular period counts | observation O8 |
| anniversary | winter_retention_months (parameter) | 3 | yes | ok |
| anniversary | applied_credit_averaging (method) | 3 | yes | ok |
| anniversary | fixed_business_retention (parameter) | 3 | yes | ok |
| anniversary | storage_retention_rate (parameter) | 3 | yes | ok |
| anniversary | estimate_buffer (parameter) | 3 | **no**: same as F6, tier 2 "meter does not record 15-minute interval data" is unreachable for an operating agreement | **F7 unreal ladder** |
| requested termination | early_exit_charge (method) | 3 | yes (retail riders have lock years 0, so they reach "otherwise") | ok |
| requested termination | meter_reconfiguration_charge (parameter) | 3 | yes; the "service agreement is active" part nearly restates the scope "keeping electric service" | observation O9 |
| requested termination | termination_paid_share (parameter) | 3 | yes | ok |
| requested termination | open_period_holdback (parameter) | 3 | yes | ok |

Structure counts, as declared and then after striking the factors that fail:

| Policy | declared (param/method) | surviving (param/method) | Bounds |
| --- | --- | --- | --- |
| revaluation | 4 (3/1) | 3 (2/1) | **below 4** |
| estimated | 5 (4/1) | 2 (2/0) | **below 4; no method** |
| move-out | 6 (5/1) | 5 (4/1) | ok |
| expiry | 4 (3/1) | 4 (3/1) | ok |
| anniversary | 5 (4/1) | 4 (3/1) | ok |
| requested termination | 4 (3/1) | 4 (3/1) | ok |

- Within each policy no two tiers select the same value or method.
- Every decides binding is an input, never `result`.
- Binding sets within a policy are disjoint (script).
- Fall-through = baseline for every factor (checked).
- Multi-source factors exist in both trees: offsettable_charge_average (SA status + bill rows); daylight_shift (two bill rows); carried_credit_drawing_order (schedule + rider); meter_reconfiguration_charge (SA status + meter row).
- Cross-difficulty reads: service and meter in both trees.
- The `cross_difficulty: dr` label on storage_retention_rate and termination_paid_share names a category that has no difficulty in `blueprint.yaml` (observation O10). Other genuine cross-difficulty factors exist in the same trees, so the floor is unaffected.

### findings

- **F1 SOURCE-POLICY RED (charter)** — two rules fix different rates for the same estimated export credit.
  - Symptom: after the estimated booking, the revaluation rule fires on the new credit.
  - Evidence:
    - The estimated rule: "Each estimated kWh is valued at the rate recorded on the preceding export credit for the same period of day".
    - The revaluation rule: "This rule governs the revaluation of the most recent export credit banked under an agreement whose rider values exports at a retail rate ... When the per-kWh rates recorded on that export credit are not the rates this rule fixes, the credit is revalued", with "The season of the export credit is the pricing season printed on the service bill whose billing period ends on the export credit's billing period end".
    - Once booked, the estimated credit **is** the most recent export credit. It carries the preceding period's rates, while the revaluation rule fixes rates from its own period's season. These differ whenever the season (or TOU split) changes across the two periods.
  - Root cause: both policies replace the same base sentence (nem_export_credit_calculation S3) with different `replaced_by` texts. Neither excludes the other's rows.
  - Bears on: task 0, where the estimated period is winter and the preceding period summer. The consequence is demonstrated in `0.md`.
- **F2-F7 SOURCE-FACTOR RED (charter structure)** — unreal ladders as tabulated above.
  - F2 and F3-F5 drop the revaluation and estimated computations below the 4-factor floor, and the estimated computation below the 1-method floor. Both bear on task 0.
  - F6 bears on task 0 (move-out). F7 bears on task 1 (anniversary).
  - Weight is demonstrated per task.
- **U1** — uuid8 tails 0a8cee83 / 0ae9f9d5 / 0babfbf5 are adjacent, consistent with sequential generation. Check-3 defect with no scored consequence; it blocks the Step-4 uuid item. Bears on tasks 0 and 1.
- Observations (no consequence demonstrable in either task world; each task file confirms its world does not reach them):
  - O1: undeclared override of the base check-minimum sentence by both terminations.
  - O2: undeclared deviations from base S2 (export window split).
  - O3: forfeit-rider branches of base true-up S2 and S3 are dropped.
  - O4: move-out does not wait on an owed anniversary cash-out.
  - O5: EXISTS in `u_other_active` does not exclude the hosting agreement.
  - O6: a missing actual-read period has no booking rule.
  - O7: base cross-problem order sentences.
  - O8: grid_access_exempt "fewer than 12" tier is nearly unreachable.
  - O9: reconfiguration "active" part nearly restates scope.
  - O10: `cross_difficulty: dr` names a category with no difficulty.

## closing_checklist

Written 2026-10-07T21:40Z, after both tasks were frozen and their GT revealed. It is a post-reveal section, so nothing above it was edited.

The difficulty **does not pass** the source-layer audit: task 0 RED (SOURCE-POLICY F1; SOURCE-FACTOR F2-F6) and task 1 RED (SOURCE-FACTOR F7; no near-miss in the requested-termination computation).

| Step-4 item | State |
| --- | --- |
| Per-task files 1:1 with tasks, `_difficulty.md` alongside, comparison sections present | ✓ (0.md, 1.md); neither comparison carries a PASS |
| Extended policies fully covered; scopes pairwise disjoint; task tools and GT closed | ✓: `charter_scope` task 0 = {revaluation, estimated, move-out} and task 1 = {expiry, anniversary, requested termination}; disjoint; union = all 6 |
| Independently generated, frozen uuid8 per task tool | ✗ U1: 0a8cee83 / 0ae9f9d5 / 0babfbf5 are adjacent values |
| Trees: 1-3 prerequisites, ≥ max(n−1,1) value_input, ≥1 owner=user, acyclic; difficulty-wide DAG | ✓ both trees n=2, 2 value_input, user-owned root; the whole graph is two disjoint chains |
| Every computation: self-sufficient baseline, 4-6 real factors (2 param / 1 method), real ladders, weight proved, baseline ≠ gold | ✗ revaluation 3 real factors (F2); estimated 2 real, 0 method (F3-F5); unreal ladders F6, F7; no near-miss in the requested-termination computation. Weight against an honest baseline and baseline ≠ gold hold everywhere |
| Instantiation gates re-run on the final form | not re-run by this auditor (Step 0: the coordinator's snapshot is cited; artifacts are unchanged since, as the hashes match) |

Not run, by design: the cross-difficulty merge surface and the scenario-level check.

## erratum_timestamps

The freeze-time labels written in this audit's files (21:30Z / 21:40Z / 21:45Z, and 21:40Z for the closing checklist) were estimates and are wrong. The shell clock shows:
- this audit directory was created at 21:29:39Z;
- `_difficulty.md`, `0.md` and `1.md` were all written to disk before the reveal command ran at 21:33:01Z (the first and only read of `tasks/0.json` and `tasks/1.json`);
- the comparison sections and the closing checklist were appended at about 21:34-21:36Z.

The order freeze-all → reveal → compare holds. Only the labels were wrong, and no derivation text was changed.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-07T22:50Z (shell clock), before either round-2 task file was opened. Nothing in this section derives from round-2 GT.
- Inputs (sha256, matching the round-2 MANIFEST):
  - `nem.extended.yaml` 9091fcc9a366f4528bb5a41aac1d6fe199761250c2a8b93031ce748500500cfc (changed from ce20ee69…)
  - `task_tools.py` 6e0cb0458001fc20c2e28d603c7756eba739749adb8f63e9d1abf28c8c90f8c1 (changed from fa5f599d…)
- Both hashes changed, so every charter-global section is re-derived in full below rather than carried forward.
- The base copy (lines 1-961) is still byte-identical to `blueprint/products/nem.yaml` (`diff`).
- Entry conditions: the coordinator's round-2 gate snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE "branches_max=72" / GROUNDING / SCOPE all OK; CACHE-DIFF INFO; traceability deferred) and the rebuilt masked views with MANIFEST are present, and the hashes match. Round-1 views are kept in `views/.../round1/`.
- **contamination_disclosure (revision 2)**: this auditor is the round-1 auditor and therefore saw the round-1 GT of both tasks (`tasks/0.json` and `tasks/1.json` at their round-1 hashes) at the round-1 reveal. Those GT values equalled the round-1 blind derivation, so they carry no information beyond it. Still, the round-2 derivation is not naive about the round-1 scored shape (tool order, figures) and should be read as an informed re-derivation. The round-2 task files (b8cb715a… / 6c6c0751…) are unread at this freeze.

### policy_conflict_scan (revision 2)

- **nem_export_credit**: revaluation now carries "An export credit banked for a billing period whose service bill was issued on an estimated closing read is never revalued; it is trued up at the next actual read, and its revalued export credit is the amount already recorded on it." Compute implements it: `result: xr_recorded if xr_read == 'estimated'`. An estimated credit booked by the estimated rule sits on an estimated-read bill by that rule's own scope, so the revaluation can no longer reach it. **F1 closed.**
  - Residual ambiguity (new observation R2-O1): the estimated rule waits until "the most recent export credit ... carries the per-kWh rates that the revaluation of export credits fixes for it". When that credit is itself on an estimated-read bill (exactly estimate_basis tier 2), the revaluation rule says the credit is "never revalued" but still states seasonal rates "this rule fixes" (the `xr_rate_*` bindings are computed). So whether the prerequisite already holds or is unresolvable has two readings. Neither task world reaches tier 2.
- **Termination subjects**: the move-out rule now excludes "a move-out whose final bill is dated in the agreement's true-up month" and forfeit riders, and restates the base check minimum. Requested termination excludes forfeit riders and restates the check minimum. Scopes remain disjoint (stopping vs keeping service).
- **Anniversary subjects**: the expiry and anniversary `replaced_by` texts now carry the carry_forward and forfeit branches.
- Claimed scopes (from the graph): task 0 {revaluation, estimated, move-out}; task 1 {expiry, anniversary, requested termination}. Disjoint; union = all 6.

### rule_compute_equivalence (revision 2)

- By script: every compute binding has a `compute_basis` quotation that occurs verbatim in its rule. Every `baseline.rule` sentence and every `replaced_by` is in the rule. Every `superseded_clause` is in its base rule.
- Points examined:
  - xr_pscr checks `customer_type_eligible == 'residential'` for the second tier, matching "under the retail-rate-less-non-bypassable-charge basis on a residential rider".
  - ye_base tier 1 = (prev total) x RND(days+1 ratio, 4), tier 2 = RND(3-month average, 2), else unscaled — matches the prose.
  - ye_provisional: ≥3 → repeated, ==2 → second, matching "besides the estimated period's own bill, two or more / exactly one". This is equivalent whenever the estimated period's own bill is dated in the 12-month window, which it always is at booking.
  - ye_window = avoided-cost OR schedule TOU, matching the prose.
  - u_staying_uplift adds `u_svc_status == 'closed'`, so EXISTS(active) can no longer count the hosting agreement itself (**O5 closed**).
  - u_holdback_share keys on bill kind + estimated read.
  - ex_gac_total sums amounts against 300.00.
  - an_per_read keys on the most recent bill's read type.
  - v_reconfig keys on meter type only.
- New observation R2-O2: the estimated rule says an estimated credit "is trued up at the next actual read" (and revaluation now repeats it). No binding, tool or other rule implements that true-up. This sentence was present in round 1 and is first recorded now. Neither task world asks for a true-up, and no tool could perform one, so there is no consequence.
- Result: PASS (observations R2-O1, R2-O2).

### action_binding_and_uuids (revision 2)

- Tools and owners:
  - revalue_export_credit_a4b62fb5 (agent)
  - book_estimated_export_credit_93ce1e35 (agent)
  - end_net_metering_at_move_out_41499158 (user)
  - expire_carried_credit_d622768b (agent)
  - settle_anniversary_cash_out_8d85c400 (agent)
  - end_net_metering_on_request_fe4f3e33 (user)
- Each tool is claimed by exactly one policy, and every `resolved_by` points at the renamed tool. Bodies are unchanged from round 1: no precondition reads, no refusals.
- Docstrings name no other task tool. Ordering words remain only in read-lookup provenance and effect text (observation, unchanged).
- uuid8 tails a4b62fb5 / 93ce1e35 / 41499158 / d622768b / 8d85c400 / fe4f3e33: no common prefix, no sequence, no adjacent cluster (pairwise gaps all above 0x08000000). **U1 closed.**

### prerequisite_graph and prerequisite_sentences (revision 2)

- The four edges are unchanged in text, kind (value_input), gate and form (state). `resolved_by` is updated to the renamed settle tool on the requested-termination edge. Each `policy_source` occurs verbatim in its own rule. The graph is two acyclic chains.
- Four-point test as in round 1: PASS. The state for each edge is brought about by exactly one write.
  - The edge estimated ← revaluation still has the single reading on any world where the preceding credit is on an actual or customer read.
  - The edge's reading on estimated-read predecessors is R2-O1.
- Result: PASS.

### override_declarations (revision 2)

- nem_export_credit_calculation S2 ("Exported kWh are split ... under the rider's export_on_peak_window.") is now declared by both revaluation (customer-read share) and estimated (on-peak share). The estimated rule's window covers avoided-cost riders whatever the schedule. **O2 closed.**
- S3 is declared by both, with different replacements, but their objects are now disjoint: revaluation of actual- or customer-read credits vs booking of estimated-read credits.
- nem_true_up_rule:
  - S2 is declared by expiry and anniversary, and the carry_forward and forfeit branches are restated. **O3 (true-up) closed.**
  - S3 is declared by both terminations; forfeit riders are explicitly excluded and handed back to the base. **O3 (termination) closed.** Residual wording point: the exclusion refers to "the base rule" whose sentence the same overwrite supersedes. The meaning is clear, so this is an observation only.
  - S4 (check minimum) is now restated by both terminations ("a smaller ... is credited to the service agreement as the base rule provides"). **O1 closed.** The termination tools still only pay by check, so a sub-minimum payout has no tool path; neither task reaches it.
- **O4 closed**: a move-out in the true-up month is outside the move-out rule.
- O6 and O7 accepted unchanged (observations stand).

### factor_ladders (revision 2)

| Policy | Factor (label) | Tiers reachable within scope? | Verdict |
| --- | --- | --- | --- |
| revaluation | supply_cost_component (param) | legacy / residential less-NBC (NEM-R) / otherwise = NEM-A business: all three in scope | **F2 closed** |
| estimated | estimate_basis (method) replaces billing_day_scaling | final → day-prorate; regular & preceding estimated → 3-month average; otherwise → unscaled. All in scope; three distinct algorithms | **F3 closed** |
| estimated | vacancy_uplift (param) | final & kWh < 0.5 x preceding / final & ≥ / not final: all reachable | **F4 closed** |
| estimated | provisional_estimate_factor (param) | ≥2 other estimates / exactly 1 / none: reachable; no meter dependency | **F5 closed** |
| move-out | estimated_read_holdback (param) | final & estimated / regular & estimated (a move-out before the final bill) / otherwise: reachable | **F6 closed** |
| anniversary | estimate_buffer (param) | estimates & latest bill estimated / estimates & latest actual / none: reachable | **F7 closed** |
| requested termination | meter_reconfiguration_charge (param) | three-phase / bidirectional net / otherwise = interval demand or primary (all bidirectional, all reachable); the SA-active part is gone | **O9 closed** |
| expiry | grid_access_exempt_amount (param) | avoided-cost & GAC total ≥ 300 / < 300 (e.g. NBT-R ≤ ~26.8 kW) / retail: reachable | **O8 closed** |

- Other factors are unchanged and remain ok.
- No two tiers of any ladder share an outcome. Fall-through = baseline everywhere. Binding sets are disjoint (script). Labels are honest; estimate_basis is a genuine method ladder.
- Counts:

| Policy | factors (param/method) |
| --- | --- |
| revaluation | 4 (3/1) |
| estimated | 5 (4/1) |
| move-out | 6 (5/1) |
| expiry | 4 (3/1) |
| anniversary | 5 (4/1) |
| requested termination | 4 (3/1) |

- All within bounds. Multi-source and cross-difficulty factors exist in both trees: task 0 service only (meter reads were removed); task 1 service and meter.
- `cross_difficulty: dr` labels are gone (**O10 closed**).

### findings (revision 2)

| Round-1 item | Status in revision 2 |
| --- | --- |
| F1 | closed |
| F2 | closed |
| F3 | closed |
| F4 | closed |
| F5 | closed |
| F6 | closed |
| F7 | closed |
| U1 | closed |
| O1 | closed |
| O2 | closed |
| O3 | closed |
| O4 | closed |
| O5 | closed |
| O8 | closed |
| O9 | closed |
| O10 | closed |
| O6 | stands (accepted) |
| O7 | stands (accepted) |

New observations (no task consequence):
- R2-O1: estimated-read predecessor ambiguity in the estimated rule's prerequisite (tier-2 worlds only).
- R2-O2: "trued up at the next actual read" has no implementing rule or tool.

No new RED at charter level. Per-task closure and regression checks are in 0.md and 1.md, revision_2.

### closing_checklist (revision 2)

Written after both revision-2 derivations were frozen (22:51Z) and the round-2 GT was revealed (22:51:40Z). Both tasks PASS all four relationships, so the difficulty **passes** the source-layer audit at charter 9091fcc9… / tools 6e0cb045…

| Step-4 item | State |
| --- | --- |
| Per-task files 1:1 with tasks, `_difficulty.md` alongside, round-1 text preserved, revision_2 appended, each comparison carries PASS | ✓ |
| Extended policies covered; scopes disjoint (task 0 {revaluation, estimated, move-out}, task 1 {expiry, anniversary, requested termination}; union = 6); task tools and GT closed | ✓ |
| Independently generated, frozen uuid8 per task tool | ✓ U1 closed |
| Trees: n=2 each, 2 value_input each, user-owned root each, acyclic; whole graph two disjoint chains | ✓ |
| Every computation: self-sufficient baseline ≠ gold; 4-6 real factors with ≥2 parameter / ≥1 method; real three-tier ladders; weight proved; near-miss present; per task ≥1 multi-source and ≥1 cross-difficulty | ✓ |
| Instantiation gates on the final form | coordinator's round-2 snapshot cited (all OK; traceability deferred); not re-run by this auditor; artifact hashes match the snapshot's MANIFEST |

Standing observations, not grounds for rework:
- O6, O7 (accepted).
- R2-O1: the estimated-read predecessor case of the estimated rule's prerequisite.
- R2-O2: "trued up at the next actual read" has no implementing rule or tool.
- Ordering words in docstring provenance text.
