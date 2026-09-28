# Policy-task audit — shopper_ratings_and_deactivations / charter-global

## charter_global_frozen

- Scenario: `env/env_0027_grocery_delivery_platform`, difficulty `shopper_ratings_and_deactivations`, category `shopper`, M=2 (tasks 0 and 1).
- Freeze hashes (re-computed by the auditor at start, identical to the brief):
  - `tasks/shopper_ratings_and_deactivations/shopper.extended.yaml` sha256 `933b8965ab846bc2414707b9b30e46f667cfa7849feb17cc9d55e71278a8b8df`
  - `tasks/shopper_ratings_and_deactivations/task_tools.py` sha256 `a04109ea940db2e824d6f0114b1b6422679ebfd0f18f03661c8b1c877dc9b361`
- Freeze time: 2026-09-24T23:58Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: erl-task-policy-audit auditor (Claude Opus 5.5), independent of the instantiating agent.
- Fields permitted: blueprint (`blueprint.yaml` difficulty entry, `db_schema.json`, `share_tools.py`, `products/shopper.yaml`, and for cross-category reads `products/batch.yaml`, `products/payout.yaml`), the extended charter, `task_tools.py`, and per task only `frozen_time`, `user_scenario`, `initial_state` from the orchestrator's masked views.
- Fields masked (not read before all freezes): `tasks/0.json`, `tasks/1.json` in full (evaluation_criteria, computations, solvability_contract, prerequisite_closure, charter_scope, required_documents, design_rationale, db_closure*), the instantiator's `worklog.md`, the scenario `worklog.md`, any earlier audit.
- Entry conditions (Step 0): the gate snapshot came with the brief — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred (KB not published). Masked views supplied with hashes, verified: task_0 view `5a3928d6…6a77`, task_1 view `3aa4ae54…bb50`. Input complete.
- Out-of-domain read disclosure: to fix the semantics of the compute DSL primitives (`within_months` = MONTHS(date, NOW) in [0, n); `CFIELD` = first matching holding of the customer; `LATEST`/`XLATEST` = max by date string), the auditor read the docstring and the `build_env` section of `skills/erl-task-instantiate/scripts/check_compute.py`. It carries no task GT. All recomputation in this audit uses the auditor's own evaluator (temporary script, deleted), not that gate.

### policy_conflict_scan

Complete structured policy = base section of `shopper.extended.yaml` (verified: all ten top-level base keys are equal as parsed YAML to `blueprint/products/shopper.yaml`, and lines 1–1025 are byte-identical) + 8 extended policies:

| id | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| shopper_ext_dropped_batch_severity | state_due | record_dropped_batch_violation_61b8c422 (agent) | points | [] |
| shopper_ext_wrong_address_severity | state_due | record_wrong_address_violation_db63d782 (agent) | points | ← dropped_batch_severity |
| shopper_ext_missing_items_excusal | state_due | decide_missing_items_dispute_36c35ef8 (agent) | points | [] |
| shopper_ext_conduct_complaint_excusal | on_request | dispute_conduct_complaint_violation_2203c191 (user) | points | ← missing_items_excusal, ← wrong_address_severity |
| shopper_ext_wrong_address_excusal | state_due | decide_wrong_address_dispute_4037a75e (agent) | points | [] |
| shopper_ext_alcohol_procedure_excusal | state_due | decide_alcohol_procedure_dispute_63dedfc1 (agent) | points | [] |
| shopper_ext_late_delivery_excusal | state_due | decide_late_delivery_dispute_3251c6fd (agent) | points | [] |
| shopper_ext_dropped_batch_excusal | on_request | dispute_dropped_batch_violation_598e80dc (user) | points | ← wrong_address_excusal, ← alcohol_procedure_excusal, ← late_delivery_excusal |

Overlaps scanned:
- **Subjects**: the two severity policies write `shopper_violation_recorded` for disjoint violation types (batch_dropped / wrong_address); the six excusal policies write `shopper_violation_cleared` for six disjoint violation types. No two extended policies decide the same quantity for the same object.
- **Triggers / object selection**: missing-items selects the disputed violation through the submitted dispute (`source_event_id`); wrong-address, alcohol and late-delivery excusal select "the account's most recent … violation" of their type; conduct and dropped-batch excusal select the most recent violation of their type offered by the app. See observation O4 (selection by recency rather than by the dispute's source) — no conflict in either task world.
- **Eligibility / time anchors**: base `shopper_evt_violations` dispute window (violation_dispute_days, event_date as day 0, inclusive) is not overwritten by any extended policy and therefore governs every excusal; no extended sentence contradicts it.
- **Terminal states**: see observations O2/O3 (partial clearing vs the base measure; zero-point `dispute_upheld` clearing on a denied late-delivery dispute).
- **Cross-category read boundaries**: `shopper_ext_dropped_batch_severity` contradicts the batch charter on which drops carry a violation at all — **finding F1 (SOURCE-POLICY RED)**. No other cross-category contradiction found (payout freeze_reason / available_balance_usd, batch pay components, reversal reasons, wait_free_minutes all read consistently with their charters).
- **Scope exclusivity and completeness**: the prerequisite graph has exactly two connected components — {conduct_complaint_excusal, missing_items_excusal, wrong_address_severity, dropped_batch_severity} and {dropped_batch_excusal, wrong_address_excusal, alcohol_procedure_excusal, late_delivery_excusal}. They are disjoint and together cover all 8 extended policies. All 8 target events (`shopper_violation_recorded`, `shopper_violation_cleared`) are within the difficulty's claimed event_types.

### rule_compute_equivalence

Each binding of each policy was matched to its `compute_basis` quotation, and every quotation was found verbatim in the policy's `rule`. Then the auditor swept back through every rule sentence. Results:

- **dropped_batch_severity**: fault (0 / half rounded down `//2` / full), stage (started ∧ ≥2 orders / started ∧ 1 order / not started), batch-type adjustment (×2 Express 30 / +ceil(half) Stock-Up `s+(s+1)//2` / as is), track (>3 / 1..3 / none, over `within_months=1`), holding (`DAYS(accepted_at, dropped_date)` ≥2 / =1 / 0), volume relief (≥10 / 5..9 / fewer, base-pay rows `within_months=1`), and the final sum `MX(0, …)`: every one is stated in the rule and implemented. Observation O5: `CFIELD('batch', …, status='dropped')` reads the first dropped batch of the customer, while the rule reads "the batch it concerns". This is equivalent only when one dropped batch is owed.
- **wrong_address_severity**: batch-size (≥3 half down / 2 less one / 1 full), clawback size (≥5.00 / 2.50–<5.00 / less), 3-month track (≥5 / 3–4 / fewer), harm (any 1★ / no 1★ ∧ some 2–3★ / none), tenure (`DAYS(activated_date, NOW)` ≥1095 / 365–1094 / less), clawback relief (frozen ∧ negative_balance / balance<0 ∧ not frozen / otherwise), `MX(0, …)`: all equivalent. Observation O6: the rule's fall-through "a payout account at zero or above earns no relief" does not name the case "frozen for another reason with a balance below zero". Compute's `else 0` covers it. No task world is on that case.
- **missing_items_excusal**: all tiers equivalent, including the cap `MN(recorded, credit)` and the subtraction of the disputed violation from the repeat count (`… - 1`). Observation O7: `disputed_entry` = latest submitted `violation_dispute` of any violation type, while the rule reads "a missing-items dispute that stands submitted". The compute is broader than the rule. In task 0 only one dispute is submitted, so there is no consequence.
- **conduct_complaint_excusal, wrong_address_excusal, alcohol_procedure_excusal, late_delivery_excusal, dropped_batch_excusal**: every quantity, window (1 / 3 / 12 whole months), `- 1` exclusion of the disputed violation, tier boundary ("up to one minute short of", "up to but not including", "exactly one"), multiplier (×2, +ceil(half)), `MX(0,…)` floor and cap `MN` is quoted and implemented. The late-delivery `result` compares the lateness credit with `late_excusal_mark` once, after the store-delay credit is added, as the rule states.
- No compute binding invents a basis, and no rule sentence about the computed quantity is left unimplemented. Every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and the reverse holds too.

### action_binding_and_uuids

- Each `(target_tool, computes=points)` is claimed by exactly one policy (8 distinct tools for 8 policies).
- Docstrings: each describes one atomic write and its post-state. None names another tool or states a position in a sequence relative to another action. The words "Afterwards …" / "then sees" describe the call's own post-state (observation only). No docstring adds a confirmation, review or wait. Function bodies: none reads a prerequisite state, refuses, or computes a value. Each only `find`s the account, `create`s the row(s) and `update`s the balance/appeal status.
- uuid8s: `61b8c422`, `db63d782`, `36c35ef8`, `2203c191`, `4037a75e`, `63dedfc1`, `3251c6fd`, `598e80dc`. All are distinct, share no prefix or suffix, and show no sequence or adjacent-value pattern. PASS.

### prerequisite_graph

Check 7 over the 6 edges:

| edge (blocked ← problem) | kind / gate | gate binding exists | policy_source verbatim in own rule | form / fallback | resolved_by = problem's target_tool |
| --- | --- | --- | --- | --- | --- |
| E1 wrong_address_severity ← dropped_batch_severity | value_input / `recent_three_month_violations` | yes | yes | state / none | yes |
| E2 conduct_complaint_excusal ← missing_items_excusal | value_input / `other_standing_points` | yes | yes | state / none | yes |
| E3 conduct_complaint_excusal ← wrong_address_severity | value_input / `other_standing_points` | yes | yes | state / none | yes |
| E4 dropped_batch_excusal ← wrong_address_excusal | value_input / `drop_other_standing_points` | yes | yes | state / none | yes |
| E5 dropped_batch_excusal ← alcohol_procedure_excusal | value_input / `drop_other_standing_points` | yes | yes | state / none | yes |
| E6 dropped_batch_excusal ← late_delivery_excusal | value_input / `drop_other_standing_points` | yes | yes | state / none | yes |

- Every policy fills `prerequisite` (`[]` for five). Every `problem` names another extended policy of this file, never a base policy and never itself. The graph is acyclic: two trees of depth ≤ 2, and no edge crosses between them.
- `condition` vs sentence: E1 "every batch the account dropped carries its dropped-batch violation entry" ↔ "Every batch of the shopper whose status is dropped has a violation entry of type batch_dropped naming that batch" (same scope). E2/E4 "no … dispute … stands submitted and undecided" ↔ "No violation dispute of a … violation … has appeal status submitted" (same). E3 "every batch pay taken back for an order verified as not delivered is matched by its wrong-address violation entry" ↔ reversal-with-order_not_delivered_verified matched by a wrong_address entry naming the batch (same). E5 "every alcohol-procedure dispute … has been decided" ↔ none submitted (same, since `appeal_status` ∈ {submitted, upheld, denied}). E6 "every late-delivery dispute … must carry a decision" ↔ none submitted (same). None is strengthened or weakened.
- `effect` claims hold as mechanisms: E1 adds a violation dated today, so it counts in the 3-month window. E2/E4/E5/E6 add a cleared entry, which lowers "other standing points". E3 adds recorded points, which raises it. The `effect` texts contain no authoring-viewpoint phrasing.

### prerequisite_sentences

Four-point test per edge (ordering connective / record-visible state in table words / no tool, id or snake_case token / strength equals condition):

- E1 "The points a wrong-address violation is booked with are fixed only after every batch the account dropped carries its dropped-batch violation entry." Connective "only after". State: batches with status dropped, and shopper_events violation entries naming them. No tool or id. Scope equals the condition. Single write of this difficulty that brings it about: `record_dropped_batch_violation_61b8c422` (reader path: dropped-batch severity rule "Every batch a shopper drops after accepting it owes one dropped-batch violation, booked on the account with the batch it concerns"). One reading inside this charter. **But the waited-on state conflicts with the batch charter for excused drops. See F1.**
- E2 "The points a conduct-complaint dispute removes are not fixed until no missing-items dispute on the account stands submitted and undecided." Connective "not until". State: shopper_appeals status. Single write: `decide_missing_items_dispute_36c35ef8` (reader path: missing-items rule "A missing-items dispute that stands submitted is decided by the agent … and marks … upheld"). One reading.
- E3 "The points a conduct-complaint dispute removes are fixed only after every batch pay taken back for an order verified as not delivered is matched by its wrong-address violation entry." Connective "only after". State: batch ledger reversal rows and shopper violation entries. Single write: `record_wrong_address_violation_db63d782` (wrong-address severity rule "Every batch pay reversal booked because an order was verified as not delivered owes one wrong-address violation"). One reading.
- E4 "The points a dropped-batch dispute removes are not fixed until no wrong-address dispute on the account stands submitted and undecided." Single write: `decide_wrong_address_dispute_4037a75e`. One reading.
- E5 "The points a dropped-batch dispute removes are worked out only after every alcohol-procedure dispute on the account has been decided." Connective "only after". Single write: `decide_alcohol_procedure_dispute_63dedfc1`. One reading.
- E6 "Before the points a dropped-batch dispute removes are fixed, every late-delivery dispute on the account must carry a decision." Connective "Before". Single write: `decide_late_delivery_dispute_3251c6fd`. It also carries the decision when the figure is 0 ("denied"). One reading.
- No state-form edge has two candidate writes in this difficulty. No action-form edge exists, so there is no `fallback_reason` to test.
- No rule carries a second wording of any dependency, a tool name or another policy id. No depended-on rule restates the blocked sentence. No extended rule states a cross-problem order that grounds no declared edge. Base: `shopper_evt_documents` says "reactivation follows shopper_evt_reactivation", a base cross-problem mention that grounds no edge in either task (observation O8).

### override_declarations

Sentence-by-sentence against `shopper_evt_violations` (the sole `base_policy_refs` entry of all 8):

| base sentence | handled by extended | declared |
| --- | --- | --- |
| S1 "A substantiated violation adds the points set for its type (…)" | replaced for batch_dropped and wrong_address by severity points | yes (dropped_batch_severity, wrong_address_severity) |
| S2 zero-tolerance handling | untouched | n/a |
| S3 "Only one violation of a type is recorded per order." | replaced by one per dropped batch / one per pay reversal | yes (both severity policies) |
| S4 expiry after violation_window_days | inherited | n/a |
| S5/S6 dispute accepted only within the dispute window, event_date day 0, inclusive | inherited by all six excusals (none contradicts) | n/a |
| S7 "A dispute is decided on the records" | followed | n/a |
| S8 late_delivery cleared when the order record shows it was not late | replaced by the lateness-credit test | yes (late_delivery_excusal) |
| S9 missing_items cleared when no order_item_refunded row with refund_reason missing | replaced by the excusal-credit amount | yes (missing_items_excusal) |
| S10 "any other dispute goes to the appeals team." | replaced for conduct, wrong_address, alcohol, dropped disputes | yes (4 declarations) |

- No undeclared override of a scored quantity was found inside the shopper charter. Disguised forms checked: no anonymous intermediate factor overrides a base quantity. No 0/1 multiplier zeroes a base-fixed amount. The late-delivery "removes none" branch is the declared replacement of S8. No dropped branch.
- Found half only (per-task consequences live in the task files): the partial clearing that the excusals introduce interacts with the unmodified base measure `shopper_msr_active_points` (O2). This is not a scored quantity.
- **Outside this category's base, the dropped-batch severity rule contradicts the batch charter (F1).** An `overwrite` in this file can only name shopper base sentences, so this conflict cannot be declared away here.

### factor_ladders

Per computation (P = parameter, M = method; tiers counted with fall-through; all ladders are ≥3 pairwise-disjoint tiers, stated in the rule with their conditions and values or methods, implemented in compute, fall-through = the factor's `baseline` = what `baseline.rule` states):

| policy | factors (label) | P / M | multi-source factors | cross_difficulty |
| --- | --- | --- | --- | --- |
| dropped_batch_severity | fault_by_drop_reason (M), stage_surcharge (P), stage_by_batch_type (M), track_record_surcharge (P), holding_surcharge (P), volume_relief (P) | 4 / 2 | stage_surcharge (shopping started ∧ order count) | batch ×5 |
| wrong_address_severity | batch_size_points (M), clawback_size_surcharge (P), wrong_address_track_surcharge (P), customer_harm_surcharge (P), tenure_relief (P), clawback_relief (P) | 5 / 1 | clawback_relief (status ∧ freeze_reason / balance ∧ status), customer_harm (no 1★ ∧ some 2–3★) | batch ×2, payout ×1 |
| missing_items_excusal | batch_size_credit (P), batch_type_adjustment (M), feedback_credit (P), repeat_reduction (P) | 3 / 1 | — | batch ×2 |
| conduct_complaint_excusal | counter_wait_credit (P), praise_credit (P), tenure_adjustment (M), prior_complaint_reduction (P), standing_points_reduction (P) | 4 / 1 | counter_wait (batch wait_minutes vs batch-type wait_free_minutes) | batch ×1 |
| wrong_address_excusal | route_credit (P), unreachable_credit (P), multi_order_adjustment (M), prior_reduction (P), low_rating_reduction (P) | 4 / 1 | — | batch ×2 |
| alcohol_procedure_excusal | outage_credit (P), handoff_praise_credit (P), tenure_adjustment (M), prior_reduction (P) | 3 / 1 | — | none |
| late_delivery_excusal | store_wait_credit (P), detour_credit (P), multi_order_adjustment (M), store_delay_credit (P) | 3 / 1 | store_wait (wait vs free minutes), detour (driven vs estimated miles) | batch ×3 |
| dropped_batch_excusal | forfeited_offer_credit (P), reliability_credit (P), drop_praise_credit (P), release_adjustment (M), prior_reduction (P), standing_reduction (P) | 5 / 1 | forfeited_offer (shown pay ∧ zero earnings) | batch ×3 |

- Counts: every computation has 4–6 declared factors, ≥2 P and ≥1 M, before the realism tests below. Per tree: tree A (conduct) has multi-source (stage_surcharge, clawback_relief, counter_wait) and cross-difficulty (batch, payout). Tree B (dropped excusal) has multi-source (forfeited_offer, store_wait, detour) and cross-difficulty (batch).
- Bindings: no binding belongs to two factors. Every `decides` is an input, never `result`.
- Distinct outcomes: every ladder's tiers select distinct values (2/1/0; 3/2/0 for outage and prior-alcohol; 1/2/3 for wrong-address batch size at points_wrong_address = 3) or distinct methods (×2 / +ceil(half) / as is; half-down / full / zero). The method ladders ×2 and +ceil(half) coincide on an input of 1 (both 2), but they are distinct methods, not one tier written twice.
- Labels: every `method` factor changes the algorithm (a multiplier on an intermediate, or a fraction of the charter's type points). Every `parameter` factor substitutes a number. Honest.
- Baselines: each `baseline.rule` is a sentence of its `rule`, names the standard method and default values, and gives a definite number with no factor applied. For the six excusals that number is 0 points removed (late-delivery: none removed). For the severities it is points_batch_dropped / points_wrong_address.
- **Realism of conditions (tested per tier condition):**
  - **F2 (SOURCE-FACTOR RED):** `shopper_ext_alcohol_procedure_excusal.alcohol_handoff_praise_credit`. An alcohol-procedure violation is "handing over alcohol without completing the ID scan" (`parameter_schema.points_alcohol_procedure`). Its excusal credit is raised by "the 5-star ratings the shopper received less than one whole month before the decision" — ratings from any customers on any batches. Whether other customers rated the shopper 5 stars has no bearing on whether an age check was carried out on this hand-off, and alcohol delivery businesses do not weigh it when excusing a missed ID scan. The ID check is a legal compliance step, and satisfaction elsewhere does not mitigate it. That is a condition no business in that line weighs for that quantity. Struck out, the alcohol computation keeps 3 factors (outage, tenure, prior), below the floor of 4.
  - **F3 (SOURCE-FACTOR RED):** `shopper_ext_wrong_address_severity.clawback_relief`. Violation severity is relieved by 1 or 2 points according to the shopper's payout account "after the pay was taken back": frozen for a negative balance, or merely below zero. A payout balance goes below zero or not depending on whether the shopper had already cashed out or had other earnings pending, not on anything about the wrong-address hand-off. No delivery platform grades a disciplinary violation by the worker's wallet balance. The condition is not one that line of business weighs for violation points.
  - Other conditions read as weighed by that line of business (drop reason, stage, batch type, acceptance-to-drop days, recent violations, base-pay volume; batch size, clawback size, customer harm, tenure; item units, batch type, customer feedback on the batch, repeats; counter wait, praise for conduct, tenure, prior complaints, standing points; unreachable-customer exclusions, prior wrong-address, 1-star ratings on the batch; outage exclusions, prior alcohol; store wait, detour, store-delay exclusions; forfeited offer, reliability, release timing, prior drops, standing). Weaker but not struck: route miles as a wrong-address excusal credit, and 5-star praise as a dropped-batch excusal credit (observation O9).
  - No tier condition holds for every customer who reaches its write.

### findings

**F1 — SOURCE-POLICY RED (cross-category conflict on which drops carry a violation and how many points). Bears on task 0 (its tree contains `shopper_ext_dropped_batch_severity` on a vehicle_breakdown drop).**
- Symptom: for a batch dropped for vehicle_breakdown or personal_safety (or store_closed / app_outage), the shopper extended charter says a dropped-batch violation is owed and booked with points, while the batch charter says no violation is recorded and the drop carries no violation points.
- Root cause: `shopper_ext_dropped_batch_severity.rule` widens the obligation to "Every batch a shopper drops after accepting it owes one dropped-batch violation" and assigns fault points by drop reason, including half points for vehicle_breakdown / personal_safety. The batch charter, a published policy of the same scenario that this policy reads through `cross_category`, excludes those reasons from violations altogether. An `overwrite` in the shopper file can only supersede shopper base sentences, so the conflict is undeclared and cannot be declared here.
- Evidence (verbatim):
  - `tasks/shopper_ratings_and_deactivations/shopper.extended.yaml` `extended_policies[shopper_ext_dropped_batch_severity].rule`: "Every batch a shopper drops after accepting it owes one dropped-batch violation, booked on the account with the batch it concerns." … "a batch dropped because the store closed or the app failed carries no fault points; a batch dropped for a vehicle breakdown or for personal safety carries half of points_batch_dropped, rounded down to a whole point".
  - `blueprint/products/batch.yaml` `policies[batch_evt_cancel_and_drop].rule`: "A drop with drop_reason shopper_choice records a batch_dropped violation on the shopper account; a drop whose reason is in excused_drop_reasons records none."
  - `blueprint/products/batch.yaml` `parameter_schema.excused_drop_reasons`: "List — drop reasons that carry no violation points." Every batch variant, Stock-Up Batch included, lists `[store_closed, app_outage, vehicle_breakdown, personal_safety]`.
  - `blueprint/products/batch.yaml` event `batch_dropped` triggers `shopper:shopper_violation_recorded` only `when: {drop_reason: shopper_choice}`.
  - Edge E1's waited-on state ("every batch the account dropped carries its dropped-batch violation entry") therefore requires, for an excused drop, a violation entry that the batch charter says must not exist.
- Demonstrated consequence: in task 0, see `0.md` findings (two defensible write sets and three scored values change).
- Affected: `shopper.extended.yaml` → `shopper_ext_dropped_batch_severity` (rule, fault ladder, `factors[fault_by_drop_reason]`), and E1 of `shopper_ext_wrong_address_severity.prerequisite`.

**F2 — SOURCE-FACTOR RED (unreal ladder condition): `alcohol_handoff_praise_credit`.** See factor_ladders above. Bears on task 1 (its tree contains `shopper_ext_alcohol_procedure_excusal`). The demonstration is in `1.md`.

**F3 — SOURCE-FACTOR RED (unreal ladder condition): `clawback_relief` of `shopper_ext_wrong_address_severity`.** See factor_ladders above. Bears on task 0. The demonstration is in `0.md`.

Observations (not grounds for rework):
- O1 Docstring wording "Afterwards …" / "then sees" describes the post-state of the call itself, not an order among tools. No consequence.
- O2 Partial clearing vs base measure: `shopper_msr_active_points` counts only recorded rows "that have no shopper_violation_cleared row". After a partial excusal (e.g. 1 of 2 points), the base measure drops the whole violation while the tools lower `violation_points_balance` only by the partial figure. The measure feeds holds and deactivation, which are not scored here. The per-task hold-threshold effect is recorded in `0.md`.
- O3 `late_delivery_excusal` books a `dispute_upheld` cleared entry even when it removes 0 points and the tool marks the dispute `denied`. Under O2 that zero-point row also removes the violation from the base active-points measure. Neither task world is on the 0 branch.
- O4 wrong_address / alcohol / late-delivery excusals select "the account's most recent … violation", not the dispute's `source_event_id`. They diverge only if a submitted dispute names an older violation. In neither world.
- O5 dropped_batch_severity `CFIELD(..., status='dropped')` reads the first dropped batch, not necessarily the owed one. In task 0 exactly one dropped batch exists.
- O6 clawback_relief rule fall-through does not name "frozen for another reason and negative". Compute `else 0` covers it. In neither world.
- O7 missing_items `disputed_entry` is not filtered by violation type, unlike the rule. Task 0 has exactly one submitted dispute.
- O8 Base `shopper_evt_documents` names another policy id ("reactivation follows shopper_evt_reactivation"). It is base text and grounds no edge in either task.
- O9 Route miles (wrong-address excusal) and 5-star praise (dropped-batch excusal) are weak mitigators. They are not struck.

## closing_checklist

Written after both tasks' `source_gt_comparison` (reveal 2026-09-25T00:01:34Z). This section is the only difficulty-level text written after the reveal. Nothing above it was changed after the reveal.

**Status: NOT CLOSABLE.** The four relationships do not PASS on both tasks.

| item | status |
| --- | --- |
| per-task files one-to-one with tasks, `_difficulty.md` alongside, every comparison carrying a PASS | `0.md`, `1.md` present; comparisons carry RED verdicts (task 0: SOURCE-POLICY, SOURCE-FACTOR, SOURCE-TASK; task 1: SOURCE-FACTOR) |
| extended policies fully covered, scopes pairwise disjoint, tools/GT closed, uuid8 independent | met: `charter_scope` of task 0 = {missing_items, dropped_severity, wrong_address_severity, conduct}, task 1 = {wrong_address_excusal, alcohol, late, dropped_excusal}; disjoint, union = all 8; uuid8s independent |
| every tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, one owner=user write, acyclic; whole-difficulty graph acyclic | met: both trees n = 3, 3 value_input edges, user root, acyclic, no cross-task edge |
| every computation has a self-sufficient baseline and 4–6 honest, real, load-bearing factors; per task ≥1 multi-source and ≥1 cross-difficulty | **not met**: F2 strikes `alcohol_handoff_praise_credit`, leaving the alcohol computation at 3 factors (task 1). F3 strikes `clawback_relief` of the wrong-address severity (task 0), whose scored value rests on it. Every other factor bears weight against an honest baseline, and each baseline alone gives a definite number different from gold |
| policy self-consistent | **not met**: F1 (shopper dropped-batch severity vs batch charter `excused_drop_reasons`) |
| instantiation gates re-run on the final form | not re-run by the auditor (Step 0: gates are supplied, not run). Artifact hashes at close are identical to the gate snapshot's inputs (`shopper.extended.yaml` 933b8965…, `task_tools.py` a04109ea…), so the brief's snapshot (all rc=0; check_traceability deferred) stands for the audited form |

Per-task verdicts:
- task 0: SOURCE-POLICY RED (T0-F1), SOURCE-FACTOR RED (T0-F3), SOURCE-TASK RED (T0-F4); problem tree PASS.
- task 1: SOURCE-FACTOR RED (T1-F2); policy self-consistency, problem tree and unique solution PASS.

## revision_2

### charter_global_frozen (revision_2)

- Inputs:
  - `shopper.extended.yaml` sha256 `840aa169595c49e28a602b8327fd2c63fe632ff685adb623fbca9776b1485aad` (changed from round 1's `933b8965…`, so every charter-global section below is **re-derived in full**, not carried forward).
  - `task_tools.py` sha256 `a04109ea940db2e824d6f0114b1b6422679ebfd0f18f03661c8b1c877dc9b361` (unchanged).
  - Blueprint files unchanged: mtimes 2026-09-24T20:2x, before round 1. `products/batch.yaml` is re-used as read in round 1.
- Freeze time: 2026-09-25T00:2xZ. Written before any round-2 task GT was opened.
- Auditor: the same erl-task-policy-audit auditor as round 1 (Claude Opus 5.5), independent of the reworker.
- Masking: as in round 1. The views are `views_r2/…/task_0.view.json` `815b19de…d749` and `task_1.view.json` `bf96d0dd…1887` (hashes verified), holding only frozen_time, user_scenario and initial_state.
- **contamination_disclosure (round 2):**
  - The auditor read the full round-1 `tasks/0.json` and `tasks/1.json` (GT of the round-1 worlds) during round 1. It therefore knows the round-1 gold conventions: step layout, read sets, the round-1 figures.
  - The round-2 worlds and charter differ, and every round-2 figure below was recomputed from the round-2 charter and views with the auditor's own evaluator. The round-2 task JSON was not opened before this freeze.
  - The round-2 derivation is blind to round-2 GT but not naive to the round-1 design. Where a round-2 figure coincides with round 1 (e.g. missing-items 1, conduct 3), the recomputation, not memory, is the evidence.
  - The round-1 out-of-domain read of `check_compute.py` (DSL semantics) is again the basis for primitive semantics. No new read was made.
- Entry conditions: the gate snapshot after rework came with the brief (all rc=0; check_traceability deferred). The views were supplied with hashes. Input complete.

### policy_conflict_scan (revision_2)

- Base section still byte-identical to `blueprint/products/shopper.yaml` (lines 1–1025 `diff` empty; all ten keys equal as parsed).
- The 8 extended policies have the same ids, triggers, target tools, owners and `prerequisite` edge set as round 1. Two components: {conduct, missing_items, wrong_address_severity, dropped_batch_severity} and {dropped_batch_excusal, wrong_address_excusal, alcohol, late}. They are disjoint and together complete.
- **Cross-category (the F1 surface), re-checked:** `shopper_ext_dropped_batch_severity.rule` now reads "Every batch a shopper drops after accepting it with the drop reason shopper_choice, the shopper's own choice, owes one dropped-batch violation …; a batch dropped for a reason the batch charter excuses (store_closed, app_outage, vehicle_breakdown, personal_safety) or for any reason other than shopper_choice owes no dropped-batch violation."
  - This matches `batch.yaml` `batch_evt_cancel_and_drop` ("A drop with drop_reason shopper_choice records a batch_dropped violation …; a drop whose reason is in excused_drop_reasons records none") and the `batch_dropped` event trigger (`when: {drop_reason: shopper_choice}`).
  - The fault-by-drop-reason ladder is gone, so no excused drop can carry points.
  - For `not_started` drops, both charters now agree on no violation.
  - No contradiction remains.
- Payout: `shopper_ext_wrong_address_severity` no longer reads the payout category (cross_category = batch only). No other cross-category read changed.
- Subjects, triggers, time anchors and terminal states are otherwise as in round 1. No new overlap.

### rule_compute_equivalence (revision_2)

Machine sweep plus manual reading:
- Every `compute_basis` quotation is found verbatim in its policy's `rule`, and every compute binding has one.
- Every `baseline.rule` sentence is in the `rule`.
- Each prerequisite `policy_source` is in its own `rule`.
- Changed policies, read tier by tier:
  - **dropped_batch_severity**: type points `P('points_batch_dropped')` (no fault ladder). The owed batch is selected with `drop_reason='shopper_choice'` in every `CFIELD`, which implements the scope sentence. Stage, batch type, track, holding, **stranded items** (item_count ≥ 60 → 2; 30–59 → 1; fewer → 0), volume relief (≥ 10 → **3**; 5–9 → 1), and `MX(0, …)` are all stated and implemented.
  - **wrong_address_severity**: clawback relief removed from rule, compute, factors, overwrite and baseline (consistent in all five places). **Repeat-address surcharge** added: "other wrong-address violations recorded … less than twelve whole months before the day the wrong-address violation is booked", ≥ 2 → 2, exactly one → 1, none → 0. Compute `COUNT(within_months=12, violation_type='wrong_address')` is taken before the new entry exists, so "other" needs no `- 1`. Equivalent.
  - **alcohol_procedure_excusal**: hand-off praise removed. Outage credit is now 4/3/0 and tenure-adjusted alone. **Recent-record reduction** added: "violations of any other type recorded … less than one whole month before the decision", ≥ 4 → 2, 1–3 → 1, none → 0. Compute is all recorded within 1 month minus alcohol_procedure within 1 month. Equivalent.
  - **wrong_address_excusal**: the low-rating reduction now counts "ratings of 2 stars or fewer" on the batch. Compute counts rating 1 plus rating 2, and the ladder text says the same. Equivalent. The parameter names `one_star_many` / `one_star_*_reduction` keep the old wording (naming only, observation).
  - **conduct_complaint_excusal**: standing thresholds 11/6. **dropped_batch_excusal**: drop standing thresholds 6/3. Ladder texts reference the parameters. Equivalent.
  - missing_items and late_delivery are unchanged.
- Carried observations re-checked: O5 now reads "first dropped shopper_choice batch". O7 (missing-items `disputed_entry` not filtered by violation type) is unchanged. O6 is gone with clawback relief.

### action_binding_and_uuids (revision_2)

`task_tools.py` is unchanged (same hash). Round-1 conclusion stands on the same object: 8 distinct `(target_tool, points)` claims, no prerequisite judged by any tool body, uuid8s independent. The `target_tool` of each of the 8 policies is unchanged.

### prerequisite_graph (revision_2)

Same 6 edges, kinds, gates and `resolved_by`. Acyclic.
- **E1 changed**:
  - `policy_source` "The points a wrong-address violation is booked with are fixed only after every batch the account dropped by its own choice carries its dropped-batch violation entry." It is verbatim in the wrong-address severity rule.
  - `condition` "Every batch of the shopper whose status is dropped with drop_reason shopper_choice has a violation entry of type batch_dropped naming that batch". Same scope as the sentence: "by its own choice" is tied to shopper_choice by the dropped-batch rule's own gloss "the drop reason shopper_choice, the shopper's own choice".
  - `resolved_by` `record_dropped_batch_violation_61b8c422`.
  - The gate binding `recent_three_month_violations` exists.
- E2–E6 are verbatim identical to round 1, and their conditions are unchanged.

### prerequisite_sentences (revision_2)

- E1 four-point test: connective "only after"; record-visible state (batches.status dropped ∧ drop_reason shopper_choice; a batch_dropped violation entry naming the batch); no tool, id or snake_case token; strength equals condition. One write of this difficulty brings it about (`record_dropped_batch_violation_61b8c422`, via the dropped-batch rule "Every batch a shopper drops … with the drop reason shopper_choice … owes one dropped-batch violation"). The state is now reachable consistently with the batch charter, which closes the E1 half of F1.
- E2–E6: round-1 derivations re-read against the unchanged sentences. Still one reading each.
- No new cross-problem order sentence appears in any changed rule. The new clauses (stranded items, repeat address, recent record) state no dependency.

### override_declarations (revision_2)

- dropped_batch_severity `overwrite[0].replaced_by` updated to the new formula ("the level's points_batch_dropped plus the adjusted stage surcharge plus … plus the stranded-items surcharge, less the volume relief").
- wrong_address_severity `overwrite[0].replaced_by` updated ("… plus the repeat-address surcharge, less the tenure relief").
- The alcohol overwrite is unchanged, and its replaced text does not name the removed praise credit.
- Base sentences S1–S10: same conclusions as round 1. No undeclared override of a scored quantity.

### factor_ladders (revision_2)

| policy | factors (label) | P / M | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| dropped_batch_severity | stage_surcharge P, stage_by_batch_type M, track_record_surcharge P, holding_surcharge P, **stranded_items_surcharge P**, volume_relief P | 5 / 1 | stage_surcharge | batch ×5 |
| wrong_address_severity | batch_size_points M, clawback_size_surcharge P, wrong_address_track_surcharge P, customer_harm_surcharge P, tenure_relief P, **repeat_address_surcharge P** | 5 / 1 | customer_harm (no 1★ ∧ some 2–3★) | batch ×2 |
| missing_items_excusal | unchanged | 3 / 1 | — | batch ×2 |
| conduct_complaint_excusal | unchanged (thresholds 11/6) | 4 / 1 | counter_wait | batch ×1 |
| wrong_address_excusal | unchanged ids; low-rating now "2 stars or fewer" | 4 / 1 | — | batch ×2 |
| alcohol_procedure_excusal | outage_credit P, tenure_adjustment M, prior_reduction P, **recent_record_reduction P** | 3 / 1 | — | none |
| late_delivery_excusal | unchanged | 3 / 1 | store_wait, detour | batch ×3 |
| dropped_batch_excusal | unchanged (thresholds 6/3) | 5 / 1 | forfeited_offer | batch ×3 |

- Every computation has 4–6 factors, ≥2 P, ≥1 M. Each ladder has ≥3 disjoint tiers stated in the rule, distinct values (2/1/0; 3/1/0 volume; 4/3/0 outage; 3/2/0 prior-alcohol) or distinct methods. The fall-through tier equals the baseline stated in `baseline.rule`. Labels are honest.
- **Realism of the new or changed conditions:**
  - Stranded items: the groceries a drop leaves to be re-offered are something a delivery platform weighs in a drop's severity.
  - Repeat address: prior wrong-address hand-offs in 12 months are a standard repeat-offence escalation.
  - Recent record: fresh violations of other kinds reduce the benefit of the doubt on a compliance breach. Disciplinary practice weighs this, and the charter states it as a reduction.
  - Wrong-address excusal counting ≤2★ ratings on the batch: customer harm evidence, as before.
  - No new condition holds for every customer at its write.
- The round-1 struck factors are gone: `alcohol_handoff_praise_credit` (F2) and `clawback_relief` (F3) appear nowhere in the charter.
- Tree A: multi-source (stage_surcharge, counter_wait) and cross-difficulty (batch). Tree B: multi-source (forfeited_offer, store_wait, detour) and cross-difficulty (batch).

### findings (revision_2, charter-global)

Round-1 items at the charter level:
- **F1 — closed at the charter level.** The dropped-batch obligation is now bounded to shopper_choice drops, and the excused reasons are named as owing none, in agreement with `batch.yaml`. E1 is narrowed to the same scope. The per-task check of the world is in `0.md` revision_2.
- **F3 — closed.** `clawback_relief` was removed from rule, compute, factors, overwrite and baseline. The replacement factor `repeat_address_surcharge` passes the realism test.
- **F2 — closed at the charter level.** `alcohol_handoff_praise_credit` was removed. The alcohol computation still has 4 declared factors (3 P, 1 M), all with real conditions. Load-bearing on the task world is checked in `1.md` revision_2.

New charter-global observations (no RED):
- O10 The batch charter's `batch_dropped` event *triggers* the batch_dropped violation for a shopper_choice drop at drop time. A world where a shopper_choice drop sits unbooked (task 0) is therefore a world where that system trigger did not fire. The shopper extended rule treats it as an owed booking, which agrees in substance with the batch charter (a violation is recorded). This is not a contradiction and has no second scored reading.
- O11 Parameter names `one_star_many`, `one_star_many_reduction`, `one_star_one_reduction` now govern "ratings of 2 stars or fewer". This is naming only, and rule, compute and ladder agree.
- Carried: O2, O3, O4, O5 (now over shopper_choice drops), O7, O8, O9. O1 is unchanged with the tool module.

### closing_checklist (revision_2)

Written after both revision_2 comparisons (reveal 2026-09-25T00:19:24Z). Nothing in the revision_2 charter-global sections above was changed after the reveal.

| item | status |
| --- | --- |
| per-task files one-to-one with tasks, `_difficulty.md` alongside, revisions traceable, every comparison carrying a PASS | met: `0.md` and `1.md` each carry revision_2 with PASS, and round-1 text is preserved above each revision |
| extended policies fully covered, scopes pairwise disjoint, tools and GT closed, uuid8 independent | met: `charter_scope` task 0 = {missing_items, dropped_severity, wrong_address_severity, conduct}, task 1 = {wrong_address_excusal, alcohol, late, dropped_excusal}; disjoint, union = 8; tool module unchanged |
| every tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, a user write, acyclic; whole graph acyclic | met: both n = 3 with 3 value_input edges, user roots, no cross-task edge |
| every computation has a self-sufficient baseline and 4–6 honest, real, load-bearing factors; per task multi-source and cross-difficulty | met: all 8 computations re-verified on the round-2 worlds, and every factor moves its scored value; fall-backs 0/2/3/0 (task 0) and 0/0/0/0 (task 1) all differ from gold |
| policy self-consistent | met: F1 closed (shopper_choice scope agrees with `batch.yaml`) |
| instantiation gates on the final form | not re-run by the auditor (Step 0). The brief's post-rework snapshot is all rc=0 (check_traceability deferred), and the artifact hashes at close (`840aa169…`, `a04109ea…`) equal the ones it was run on |

Round-1 item status: **F1/T0-F1 closed; F3/T0-F3 closed; F2/T1-F2 closed; T0-F4 closed;** dispute-window-anchor observation closed.

No new RED, no regression.

Persisting observations: the task-0 hold-threshold crossing (unscored), O10, O11, O2–O5, O7–O9.

**Difficulty verdict (revision_2): PASS on all four relationships for both tasks. The source-layer audit is closed.**

## revision_3

### charter_global_frozen (revision_3)

- Inputs:
  - `shopper.extended.yaml` sha256 `840aa169595c49e28a602b8327fd2c63fe632ff685adb623fbca9776b1485aad` and `task_tools.py` sha256 `a04109ea940db2e824d6f0114b1b6422679ebfd0f18f03661c8b1c877dc9b361`, both re-hashed by the auditor and identical to revision_2. **By the re-audit rule, every charter-global section of revision_2 is carried forward by reference, not re-derived**: policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders, findings.
  - Blueprint unchanged (mtimes before round 1).
- Freeze time: 2026-09-25T04:5xZ. Written before round-3 `tasks/*.json` was opened.
- Auditor: same as rounds 1–2.
- Views: `views_r3/…/task_0.view.json` `cb64c2c7…f13d` and `task_1.view.json` `facec810…2530` (hashes verified).
- contamination_disclosure: as in revision_2. The auditor has seen round-1 and round-2 GT. Round-3 GT was not opened before this freeze.
- Read for this round: `audits/merge_acceptance/validate_scenario.round1.txt` (at the coordinator's instruction) and `erlbench/validate.py` / `erlbench/determinism.py` / `erlbench/loader.py` (runtime clock), all within the read domain.

### validator item (charter-global half)

- The validator lines are "ERROR: shopper_ratings_and_deactivations/0: frozen_time '2026-09-22T15:10:00' must start with YYYY-MM-DD" and the same for task 1 with '2026-09-23T11:25:00'.
- The check is `erlbench/validate.py:227` `re.match(r"^\d{4}-\d{2}-\d{2}\b", str(ft))`. `T` is a word character, so `\b` fails after the date. The runtime clock (`erlbench/determinism.py` `Clock`) documents the intended form "2025-11-14 03:40:00 EST".
- Runtime use of the stamp in this difficulty:
  - Every task tool derives its date as `ctx.now()[:10]`, which gives the same date whatever follows it.
  - Only two fields take the full stamp: `shopper_appeals.created_at` in the two user tools (task_tools.py lines 155 and 320), and `verification_log.verified_at` (share_tools.py 427/430). No policy compute reads either field for a scored value. The only `created_at` read is missing-items `disputed_entry`, filtered to `appeal_status='submitted'`, which a user-filed dispute (status upheld) never matches.
  - `make_id` seeds take no time component.
  - The compute DSL's clock is `str(frozen_time)[:10]` (NOW, DAYS, MONTHS all use the date prefix).
- So a stamp change that keeps the date prefix moves no anchor, window, count or scored value, provided the date is unchanged. This is checked per task.

### closing_checklist (revision_3)

Written after the revision_3 comparisons (reveal 2026-09-25T04:57:24Z). The revision_2 checklist is carried forward with these results:

| item | status |
| --- | --- |
| validator item `frozen_time … must start with YYYY-MM-DD` (both tasks) | closed: '2026-09-22 15:10:00 CDT' and '2026-09-23 11:25:00 CDT' match `^\d{4}-\d{2}-\d{2}\b`, and no old-form literal remains in either task file |
| instant, time anchors, window boundaries, scored values | unchanged: same date and wall clock; views differ from revision_2 only in `/frozen_time`; all gold writes and all `computations` figures identical to revision_2 |
| charter and tools | unchanged (`840aa169…`, `a04109ea…`); charter-global sections carried forward |
| full-stamp fields (`shopper_appeals.created_at` from the user tools, `verification_log.verified_at`) | now take the space-form stamp; no scored computation reads them |
| gates | brief's post-rework snapshot: all 7 rc=0; validate_scenario has no ERROR for this difficulty other than the expected pre-render "required document … not found"; check_traceability deferred. Not re-run by the auditor |

**Difficulty verdict (revision_3): PASS for both tasks on all four relationships.** No open RED, no new defect, no regression.
