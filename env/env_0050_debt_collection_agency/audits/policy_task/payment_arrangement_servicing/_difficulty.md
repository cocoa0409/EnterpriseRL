# Policy-task audit — payment_arrangement_servicing / charter-global

## charter_global_frozen

- Revision: revision_1 (first audit of this difficulty; no earlier revision exists).
- Freeze time: 2026-10-10T13:17Z. Auditor: erl-task-policy-audit auditor (Claude Opus 5.5 subagent). The auditor did not write these artifacts.
- Hashes the section was built from:
  - `tasks/payment_arrangement_servicing/plan.extended.yaml` sha256 `6d7cd862b56a12b3efe186c3c61f93cf9fa5e51c348dcc1a518bed2fc84c9423` (matches the brief)
  - `tasks/payment_arrangement_servicing/task_tools.py` sha256 `2c3196ee453f9a8aee4baf699dbe077efb19ee870a337ad612af799deea9b59a` (matches the brief)
  - `blueprint/products/plan.yaml` sha256 `6eecbe4e…db78e`; `blueprint/share_tools.py` sha256 `607e95d4…eeba`; `blueprint/products/hardship.yaml` sha256 `2cb89196…7037`
- Fields read: blueprint.yaml, db_schema.json, share_tools.py, products/plan.yaml, products/hardship.yaml (tier parameters and its plan-related rules), the extended charter, task_tools.py, `erlbench/` and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (build_env: `within_months` means `0 <= MONTHS(d, NOW) < N`; CFIELD/CPARAM return the first matching holding of the customer; X-history is scoped to the customer).
- Masked and not read when this section was written: every `tasks/*.json`, both worklogs (`tasks/payment_arrangement_servicing/worklog.md` and the scenario-level `worklog.md`), every other audit, and every other scenario or difficulty directory. This section contains nothing taken from a revealed GT.
- Entry conditions (Step 0): the brief came with a gate snapshot showing check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all green (check_traceability deferred because the KB is not published yet). It also listed the masked view files and their sha256 values, and these match the files on disk. The entry conditions are met. The auditor cites these gates and did not re-run them.

### policy_conflict_scan

- **Base copy.** Lines 1–1159 of the extended charter are byte-identical to `blueprint/products/plan.yaml` (checked with `diff`; the only difference is a trailing blank line).
- **Extended policies and claimed scope.** The charter's own comments assign the six extended policies as follows. Task 0: `plan_ext_returned_installment_redating` (prerequisite problem, agent) and `plan_ext_new_method_handover` (root, owner=user). Task 1: `plan_ext_presuspension_missed_entry`, `plan_ext_post_hold_resumption`, `plan_ext_post_hold_reaging` (prerequisites, agent) and `plan_ext_post_hold_restructure` (root, owner=user). Each policy belongs to exactly one task, so the two scopes do not overlap, and together they cover all six policies. Both sides are checked against `charter_scope` at the reveal.
- **Overlapping subjects.** Four extended policies have `plan_schedule_change_recorded` as their subject: redating (`due_date_change`), handover (`funding_method_change`), reaging (`deferral`) and restructure (`restructure`). Each writes a different `change_type` through its own tool, so no `(tool, computes)` pair is shared. All four inherit the base `plan_evt_schedule_changes` gates: active status, the per-12-month limits per kind, the restructure and deferral minimum paid installments, and the affordability test for restructures.
- **Triggers.** redating, handover, resumption and restructure are `on_request`. presuspension and reaging are `state_due`. None of them introduces a trigger that conflicts with another.
- **Time anchors.** redating uses NOW, the return-received date or the scheduled due date. handover uses NOW and the schedule anchor date. presuspension uses `suspended_date`, the hold's `request_date` or `start_date`, the return date or the last-presented date. resumption uses NOW, `ended_date + contact_resume_delay_days` or the day after `ended_date`. reaging uses `created_date`, `authorization_date` or the due date of installment 1. restructure uses NOW and the anchor date. Where these collide with base anchors, the collisions are listed under override_declarations.
- **Terminal states.** The resumption tool sets status active. No extended policy cancels, breaks or completes a plan, so no extended policy collides with a base terminal transition.
- **Cross-category read boundaries.** Declared `cross_category.reads` match the compute calls (account: event_type, payment_channel, return_reason, adjustment_reason, amount, txn_date, placed_balance; hardship: hold_start_basis, documentation_required, outbound_calls_paused, contact_resume_delay_days, request_date, start_date, ended_date, hardship_hold_events.assistance_outcome). No undeclared read was found.
- **Cross-product rule touching this difficulty.** `hardship.yaml` `hardship_combo_dispute_and_arrangements` says: "When a hold starts on an account with an active payment plan, the plan is suspended the same day; when the hold ends, the plan resumes only if the consumer agrees, under the payment arrangement suspension rule, and the account returns to arranged, otherwise to active." This agrees with base `plan_evt_suspension`. The resumption tool does not move `placed_accounts.status` back to arranged. Recorded as observation O-7.

### rule_compute_equivalence

Each compute binding was swept against its `compute_basis` quotation and back against the rule, sentence by sentence.

- **redating.** Every binding has a verbatim basis, and every tier, window, channel rule and cap in the rule is implemented. `account_latest_return_reason` is an all-time XLATEST, but it is only consulted when `account_returns_6m >= 1`, and in that case the latest return is inside the window. It is therefore equivalent to the rule's "whose most recent return". No empty promise was found.
- **handover.** Equivalent. One phrase has no compute counterpart. The rule says "after a return for account_closed or stop_payment, when no earlier debit remains to be stopped, the days … are counted in calendar days". If "when no earlier debit remains to be stopped" is read as a condition rather than an explanation, compute has nothing for it. Recorded as O-3. The `inputs` metadata lists only the debit_card counts and omits credit_card; compute covers both (metadata only).
- **presuspension.** Two mismatches were found, both recorded as O-4:
  - (a) `hold_request_lag` adds `hold_request_lag >= 0`. The rule's "requested no more than thirty days after the examined installment's scheduled due date" does not exclude a request made before the due date.
  - (b) `hold_start_basis_tier`, `hold_request_date` and `hold_start_date` read CPARAM/CFIELD on `account_id`. That returns the first hardship holding on the account, not "the hardship hold that suspended the plan".
  - Task 1's world has one hold and a request lag of 15, so neither mismatch has a consequence there.
- **resumption.** Equivalent. The monthly alignment uses the anchor's day number with no clamp for short months. The rule is silent on short months.
- **reaging.** Three mismatches, none with a consequence in task 1, recorded as O-5:
  - (a) `reaged_installment` = LATEST missed `installment_number` ignores "uncured".
  - (b) The `term_window_start` factor ladder's first tier adds "AND installment 1 carries a scheduled due date on its payment entries". The rule only says "a plan that took a down payment counts its term from the scheduled due date of installment 1". Compute falls through to `authorization_date` or `created_date` when installment 1 has no payment row, but the rule does not.
  - (c) CFIELD/CPARAM select the first hold on the account (same mechanism as presuspension (b)).
- **restructure.** Equivalent, with one reservation recorded as O-6. `debit_within_notice` = `DAYS(NOW, anchor) <= 3` also treats a past anchor as "a debit falls due within three days of the handling date".

### action_binding_and_uuids

- **Tool bindings.** Each `(target_tool, computes)` pair is claimed by exactly one policy:
  - `redate_returned_installment_ce690b15` / shift_days
  - `authorize_payment_method_50f022be` / installment_number
  - `record_missed_installment_d21cca89` / installment_number
  - `resume_suspended_plan_416c1e83` / days_to_first_installment
  - `reage_missed_installment_128922de` / installment_amount
  - `authorize_restructured_installments_370d01b0` / installment_amount
- **uuid8s.** ce690b15, 50f022be, d21cca89, 416c1e83, 128922de and 370d01b0 are pairwise distinct. They share no common prefix or tail, are not sequential, and do not look batch-derived.
- **Docstrings.** No docstring names another tool or states a sequence position. "afterwards" appears only as "the consumer can afterwards see …", which describes what becomes visible, not an order of actions. None of the tool bodies validates a prerequisite: each one reads the plan and writes exactly what the caller passes in.
- **Tool effect versus rule.**
  - The reaging tool always moves the named installment one period past the current final installment, extends `final_due_date` and sets the regular amount. The reaging rule's second branch says "the re-aged remainder is added to the final installment and the regular installment is unchanged". The tool cannot produce that terminal state, because it appends the installment and has no parameter for raising the final installment.
  - Under the third branch ("spread"), the rule spreads the remainder over the following installments while the tool still appends the installment behind the final. The remainder is then scheduled twice.
  - Recorded as finding F-5. Task 1 takes the first branch, so the finding has no consequence there.

### prerequisite_graph

- **Every policy filled in.** `prerequisite: []` appears for redating and presuspension. Edges are declared for handover (1), resumption (1), reaging (2) and restructure (2).
- **Graph.**
  - task 0: handover → redating (value_input, gate `result`)
  - task 1: resumption → presuspension (state_gate, gate `plan_installments.event_type`)
  - task 1: reaging → resumption (state_gate, gate `plan_evt_schedule_changes.change_on_active_plan`)
  - task 1: reaging → presuspension (value_input, gate `reaged_installment`)
  - task 1: restructure → reaging (value_input, gate `restructure_balance`)
  - task 1: restructure → presuspension (value_input, gate `missed_entry_penalty`)
  - Every `problem` points to an extended policy id in this file, never to a base policy or to itself. The graph is acyclic, and no cross-task edge exists.
- **policy_source quotability.** Each `policy_source` is found verbatim in the blocked policy's own `rule`. All six edges are `form: state`, so no `fallback_reason` is required and none is present.
- **resolved_by.** Each `resolved_by` is the depended-on policy's `target_tool`.
- **kind and gate.**
  - The value_input gates `result`, `reaged_installment`, `restructure_balance` and `missed_entry_penalty` are bindings that exist in the blocked policy's compute.
  - The resumption edge is `state_gate` with `gate: plan_installments.event_type`. That is a field, not an eligibility gate, and the resumption policy declares no eligibility gate. Recorded as O-8: structure only, no demonstrable consequence.
- **Condition versus sentence.**
  - handover: the condition adds "and payment_plans.schedule_anchor_installment and schedule_anchor_date point at that installment and its new due date". This is stronger than the sentence, which asks only for the history entry. The redate tool writes both, so this is O-9 with no consequence.
  - restructure → presuspension: the condition says "whose grace ran out before missed-installment counting stopped", but the sentence says "ahead of the plan's suspension". This is finding **F-3**, below under prerequisite_sentences.
- **World-specific effect text.** Two `effect` texts make claims specific to one world: "taking two installments off the restructured count" and "moves from the installment after the returned one to the returned one itself". Recorded as O-10.

### prerequisite_sentences

Four-point test per edge: ordering connective / waited-on state in record words / no tool, policy id, snake_case token or row id / same strength and scope as the condition.

1. **handover → redating.** Sentence: "The first installment a newly authorized payment method collects is fixed only after the plan's installment history carries a due-date change for the installment of its most recent returned installment payment."
   - Connective "only after". State: a due-date change on the installment history. No tool name.
   - Only one write in this difficulty records a `due_date_change`: `redate_returned_installment_ce690b15`. The redating policy's rule ("the installment that payment was for is re-dated by one due-date change") identifies that write.
   - One reading. PASS.
2. **resumption → presuspension.** Sentence: "A suspended plan is not resumed until its installment history carries a missed entry for the installment whose grace period ran out before missed-installment counting stopped."
   - Connective "not … until". The state is visible in the records. Only one writer of `plan_installment_missed` exists: `record_missed_installment_d21cca89`.
   - The sentence uses the phrase "grace period". Base `plan_evt_installments` defines that term (grace_period_days_autopay from the due date). The presuspension policy defines a different "pre-suspension grace". This is the source of the second reading recorded under F-1.
   - The structural form passes. The defect in which installment the sentence points to is carried by F-1.
3. **reaging → resumption.** Sentence: "The re-aging deferral is recorded only after the plan's status is active again after its suspension."
   - Connective "only after". The state is the record's status. Only `resume_suspended_plan_416c1e83` sets active. PASS.
   - The same rule's first sentence, "After a plan returns from a hardship suspension, the installment … is re-aged", is a second wording of the same dependency. It leads to the same conclusion. Recorded as O-11.
4. **reaging → presuspension.** Sentence: "The re-aging method is not settled until the installment history carries the missed entry of the installment being re-aged." Connective "not … until". Only one writer. PASS.
5. **restructure → reaging.** Sentence: "The restructured installment is fixed only after the installment history carries a re-aging deferral for the installment with the most recent uncured missed entry." Connective "only after". Only one writer of `deferral`: `reage_missed_installment_128922de`. PASS.
6. **restructure → presuspension — FAIL (F-3).** Sentence: "The restructured installment is not worked out before the installment history records as missed the last installment whose grace ran out ahead of the plan's suspension."
   - The condition and the resolving policy define the target as the installment whose grace ran out before *missed-installment counting stopped*. In the presuspension policy, that cutoff can fall before the plan's `suspended_date` (the hold's `request_date` or `start_date`).
   - The sentence instead ties it to "the plan's suspension". Its scope differs from the condition's. The task 1 file demonstrates what this costs.

Further checks:
- The depended-on policies' rules do not restate any of these sentences.
- No extended rule names a tool, a policy id or a row id.
- No extended rule states a cross-problem order that is not backed by a declared edge.
- Base sentences that state cross-problem orders ("must first have that plan cancelled or completed"; "a consumer whose hold is still active must first have the hold ended") do not support any edge of these tasks.

### override_declarations

Swept sentence by sentence against each policy's `base_policy_refs`.

- **redating** (`overwrite: []`; refs `plan_agg_combined_affordability`, `plan_evt_schedule_changes`, `plan_evt_installments`).
  - The due-date change limits, the max shift (the rule's cap), the monthly_due_day_max limit (inherited), and "returns for account_closed, stop_payment … are never presented again" are all followed.
  - Base leaves the size of the shift to the consumer and does not fix a number. No conflict.
- **handover** (`overwrite: []`). Base `plan_evt_installments`: "An installment counts as paid when the payments applied to it reach the installment amount less the type's partial_payment_tolerance_usd." That sentence applies to every plan of a type. The handover rule treats the same quantity (how many installments the plan's payments already cover) differently:
  - its baseline and fall-through use "zero dollars" (fewer than six installments paid);
  - a manual-pay tier uses "two dollars".
  - The type tolerance appears only on its autopay tier. The deviation is not named in `overwrite`. Recorded as **F-4**: the undeclared override, together with the straw-man baseline it creates for the factor.
  - Base `plan_evt_schedule_changes`, "takes effect on the consumer's new authorization, given the same way as at set-up", is followed. The base revocation sentence (stop_payment_notice_business_days) governs which old debit is stopped. No conflict was found that can be demonstrated in task 0's world.
- **presuspension** (`overwrite: []`; refs `plan_evt_installments`, `plan_evt_suspension`). The base grace and counting rules are restated under F-1 below. The extended rule handles the same quantity — whether and when an installment's grace ran out before counting stopped — differently on three counts:
  - the counting cutoff can be the hold's `request_date` or `start_date`, earlier than `suspended_date`;
  - the grace can start on the return-received date or the last-presented date instead of the due date;
  - the grace length can be 9 or 5 days instead of the type's grace, plus hold-timing and weekend extensions.
  - None of these is declared. Recorded as **F-1** (undeclared override). The task 1 file demonstrates the second answer.
- **resumption** (`overwrite: []`; ref `plan_evt_suspension`). Base: "it falls due no sooner than resume_min_days_to_next_installment calendar days after the resumption date". The restart-clock tier "the clock starts on the day after the hold's ended_date and the offset is … which may be negative" can, when combined with a lead equal to resume_min, give fewer days than base allows. Recorded as F-6, an undeclared override that is only possible in other worlds; it does not occur in task 1, where the offset is +2.
- **reaging.** The override is declared, with the superseded clause "it moves the next unpaid installment to one period after the current final installment, extending final_due_date by one period". However, its `replaced_by` quotes only the branch that is identical to the superseded base clause ("appended there and the regular installment is unchanged"). The branches that actually deviate (add the remainder to the final installment; spread it) are not quoted. Recorded as O-12.
- **restructure** (`overwrite: []`; refs `plan_agg_combined_affordability`, `plan_evt_schedule_changes`, `plan_eligibility_and_terms`).
  - Base: "it re-spreads the current arrangement_balance over a new count of installments".
  - The extended rule's first two tiers re-spread "the arrangement_balance less the re-aged remainder" (and "less one regular installment"), and leave the remainder on a separate installment behind the final one.
  - This is an intermediate quantity, the base the installment is computed from, and the change is not declared. Recorded as **F-2** (undeclared override, anonymous intermediate). The task 1 file demonstrates it.
  - Base's count freedom ("a new count … stays within the type's maximums") is narrowed, not contradicted. The minimums and the affordability test are inherited.
- **"Installments paid".** Several extended rules define "installments paid" as "the installment payments received under the plan less those returned", a count of rows. Base measure `plan_msr_installments_paid` counts distinct installments paid within tolerance, excluding returned payments. The two counts differ in task 1 (6 vs 5), but no threshold of either task falls between them. Recorded as O-2.

### factor_ladders

Per policy: declared factors (effect label, decides). Tiers and outcomes were checked against the rule.

| Policy | Factors | param / method | Cross-difficulty | Multi-source |
| --- | --- | --- | --- | --- |
| redating | lead (param, 3/5/7), clock_start (method: received / due / NOW), day_count (method: business / calendar+weekend roll / calendar), buffer (param, 2/4/0) | 2 / 2 | buffer → account | lead (paid rows AND return rows), buffer (count AND reason) |
| handover | setup_notice (param, 3/4/5), day_count (method: calendar / business-after-next-business-day / business), tolerance (param, type / 2.00 / 0.00), extension (param, 0/3/2) | 3 / 1 | extension → account | notice, tolerance, extension |
| presuspension | cutoff (method: request_date / start_date / suspended_date), grace_length (param, 9/5/type), grace_start (method: return date / last presented / due date), hold_timing (param, 2/1/0), weekend (param, 2/1/0) | 3 / 2 | cutoff, hold_timing → hardship | cutoff, grace_length, hold_timing |
| resumption | restart_lead (param, 21/17/type), clock (method), cooldown (param, 7/3/0), statement (param, 5/2/0), alignment (method) | 3 / 2 | lead, clock → hardship; statement → account | lead, clock, alignment |
| reaging | method (method: append / add to final / spread), tolling (param, 30/15/0), goodfaith (param, 31/14/0), term_start (method) | 2 / 2 | tolling → hardship | method, tolling, goodfaith |
| restructure | balance (method), relief (param, 2/1/0), missed_penalty (param, 4/2/0), return_penalty (param, 2/1/0), tenure (param, 2/1/0), credit_bonus (param, 2/1/0) | 5 / 1 | relief → hardship; bonus → account | balance, relief, tenure, bonus |

- **Structure.** Each ladder has three tiers that do not overlap as stated, and each tier appears in the rule's prose and as a branch of the `decides` binding (exception: reaging term_start's extra condition, O-5). Every fall-through equals the factor's `baseline`, and every `baseline.rule` sentence appears in the rule. Counts are 4–6 factors per policy, at least 2 parameter and 1 method per policy. Per task: task 0 has a multi-source factor and an account-reading factor; task 1 has multi-source factors and hardship- and account-reading factors.
- **Tiers whose outcome depends on the plan type and collide for some types.** Recorded as F-7, charter-global. No consequence in tasks 0 or 1:
  - handover tolerance: tier 1 is the type's partial_payment_tolerance_usd. Promise-to-Pay (0.00) equals the fall-through; Short-Term (2.00) equals the manual tier.
  - presuspension grace_length: the fall-through is the type's grace. For Standard (5/5) and for Short-Term manual (5) it equals the 5-day tier.
  - resumption restart_lead: the fall-through is the type's resume_min. For Hardship Reduced-Payment (21) it equals the 21-day tier.
- **Label honesty.** Parameter tiers change a number; method tiers change the start date, the counting rule, the base or the placement. No mislabel was found.
- **Business realism** (outcomes checked against what a collector would publish):
  - handover tolerance: the "zero dollars" fall-through and baseline contradict Ridgeline's own published treatment (base: an installment counts as paid within the type's tolerance, with no condition on how many installments are paid). This is F-4's factor face.
  - redating buffer: its "no return in six months → 0" fall-through is practically unreachable at this write. The policy only fires on a returned installment payment, and the charter's own trigger books that same return onto the account ledger (`plan_installment_returned` → `account:account_payment_returned`, same date and reason). The tier is therefore normally read from the mirror of the same return that the clock-start factor reads. Edge cases exist (a return older than six months on a still-active plan), so this is recorded as observation O-1, not RED.
  - The other conditions (hold timing, weekend due dates, financial-assistance outcome, client relief credits, returned-debit history, tenure) are ones a collector plausibly weighs for the quantity concerned.
- Whether each factor bears weight is decided in each task file's `factor_weight`.

### findings

| id | class | finding | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED (undeclared override) | Several sentences decide the same quantity: whether an installment's grace ran out before counting stopped. Base `plan_evt_installments`: "An installment is recorded as missed only when the handling date is later than the grace period counted from the installment's scheduled due date and the installment is not paid. The grace period is grace_period_days_manual calendar days for a plan paid manually and grace_period_days_autopay calendar days for a plan collected by automatic debit, the day after the due date being day one." Base `plan_evt_suspension`: "Missed-installment counting stops while the plan is suspended". `plan_ext_presuspension_missed_entry` replaces the cutoff, the grace start and the grace length for that quantity, with `overwrite: []`. | task 1 (demonstrated there) |
| F-2 | SOURCE-POLICY RED (undeclared override, anonymous intermediate) | Base `plan_evt_schedule_changes`: "it re-spreads the current arrangement_balance over a new count of installments". `plan_ext_post_hold_restructure` re-spreads "the arrangement_balance less the re-aged remainder" (and "less one regular installment"), with `overwrite: []`. | task 1 |
| F-3 | SOURCE-POLICY RED (prerequisite sentence scope ≠ condition) | The restructure → presuspension sentence says "ahead of the plan's suspension". The condition and the resolving rule say "before missed-installment counting stopped", and that cutoff can be earlier than `suspended_date`. | task 1 |
| F-4 | SOURCE-FACTOR (straw-man baseline) + SOURCE-POLICY (undeclared override) | The handover tolerance baseline and fall-through are $0, and a manual tier is $2. Base counts an installment as paid within the type's partial_payment_tolerance_usd for every plan. | task 0 (factor weight demonstrated there) |
| F-5 | observation (tool vs rule) | The reaging tool cannot produce branch 2's terminal state, and in branch 3 it schedules the remainder twice. | none (task 1 takes branch 1) |
| F-6 | observation (potential undeclared override) | A negative restart-clock offset can fall below base's resume_min floor. | none (task 1 offset +2) |
| F-7 | observation (tiers that collide for some types) | handover tolerance, presuspension grace_length and resumption restart_lead have tiers that coincide for some plan types. | none (Standard and Extended values are distinct) |
| O-1 … O-12 | observations | Listed in the sections above. | — |

## closing_checklist

(Written only after every task's derivation is frozen and its GT revealed; see below.)

### revision_1 closing status (written after both reveals, 2026-10-10T13:30Z)

The difficulty is **not closed**. Step 4 requires every task to pass all four relationships, and neither task does:

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | F-4 carried as factor consequence | PASS | **SOURCE-FACTOR RED** (F-4) | PASS | SOURCE-FACTOR RED |
| 1 | **SOURCE-POLICY RED** (F-1, F-2, F-3) | PASS | PASS | **SOURCE-TASK RED** (final_due_date 2028-05-12 vs GT 2028-06-12) | SOURCE-POLICY RED + SOURCE-TASK RED |

Checklist items that hold as of revision_1:
- One task file per task (`0.md`, `1.md`) sits alongside this file.
- Scopes are disjoint and together cover all six extended policies (GT `charter_scope`: task 0 = {redating, handover}; task 1 = {presuspension, resumption, reaging, restructure}).
- The six task tools have distinct, independently generated uuid8s.
- Problem trees: task 0 has n = 1 with 1 value_input edge; task 1 has n = 3 with 3 value_input edges. Both roots are owner=user. The graph is acyclic across the difficulty.

Checklist items that do not hold:
- Every comparison carries a PASS.
- Every factor bears weight against an honest baseline (task 0 computation B, F-4).
- Every policy is self-consistent (F-1, F-2, F-3).

The instantiation gates were not re-run on a final form, because nothing was reworked; the gate snapshot cited is the one supplied with the brief.

---

## revision_2

### charter_global_frozen (revision_2)

- Freeze time: 2026-10-10T19:20Z (system clock). Auditor: the same erl-task-policy-audit auditor (Claude Opus 5.5 subagent). The auditor did not write or rework these artifacts.
- Shared inputs:
  - `plan.extended.yaml` sha256 `c94e5a69708092e9e3ce28c520219181c0635d14e571c13c5133c1bc83bcabac`. It **changed** since revision_1 (`6d7cd862…`), so every charter-global section below is re-derived in full.
  - `task_tools.py` `2c3196ee…9a59a`, unchanged. The tool-module conclusions of revision_1 §action_binding_and_uuids (uuid8s, docstrings, tools do not gate) carry forward on that hash. Only the parts that depend on the charter (F-5) are re-checked.
  - The base copy (lines 1–1159) is still byte-identical to `blueprint/products/plan.yaml` (`6eecbe4e…`).
- Masked before this section was written: `tasks/{0,1}.json` (revision_2 content) and the rework record in `tasks/payment_arrangement_servicing/worklog.md`. Neither was opened before this section and both task derivations were frozen.
- contamination_disclosure: the auditor read the revision_1 GT of both tasks during the round-1 reveal. Revision_2 is therefore a verification re-derivation, not a blind first derivation. Nothing in this section comes from the revision_2 GT or the worklog. The coordinator's brief names the closed item ids but no values.
- Gate snapshot supplied (coordinator re-run): EXTENDED / TASK TOOL CONTRACT / REPLAY (0.json clos 26/26, 1.json 39/39) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK. Cited, not re-run.

### policy_conflict_scan (revision_2)

- **Scope.** Same six extended policies, same assignment (task 0: redating and handover; task 1: presuspension, resumption, reaging and restructure). The scopes do not overlap and together cover all six.
- **Subjects, triggers and terminal states.** Unchanged from revision_1, except that the resumption result now has a floor at the type's `resume_min_days_to_next_installment`, which agrees with base `plan_evt_suspension`.
- **Hold identification.** "The hardship hold that suspended the plan" is now defined in every hardship-reading policy as "the hold on the plan's account whose decision_date is the plan's suspended_date". The compute uses CFIELD/CPARAM filtered on `decision_date=F('suspended_date')`.
- **Cross-product touch with the account charter (new in this round).** `account.yaml` `account_evt_payment_channels` says: "When account_msr_returns_in_lookback reaches the stage's returned_payment_block_threshold, electronic channels (ach_bank_debit, debit_card, credit_card) are blocked on the account … While a returned-payment block is in force, an electronic payment is accepted only when the handling date is later than the block period counted from the txn_date of the most recent returned payment."
  - Plan installments post to the account: base event `plan_installment_paid` triggers `account:account_payment_posted`. So this account rule gates every card or ACH installment a plan collects.
  - The plan charter says nothing about it. "A payment-method change must be a method the type allows" checks only the plan type.
  - Whether it bites depends on the world. That is decided per task: task 0 finding R2-N1, and in task 1 the block ends on 10-13, before any debit falls due.
- **Hardship touch (pre-existing, observation O-13).** `hardship.yaml` says "When a hold starts on an account with an active payment plan, the plan is suspended the same day", and a request-date tier's start_date is its request_date. The plan charter's base rule ("An active plan is suspended on the day its account enters … hardship_hold") and the new identification text both take the decision date as the suspension day. The plan's own base rule supports the reading the charter now encodes, so this is not RED.

### rule_compute_equivalence (revision_2)

- **redating.** The buffer now reads only returns of payments "not made under a payment plan" (`plan_id=None` on both XCOUNT and XLATEST), and the rule says the same. Equivalent.
- **handover.** The tolerance is now fixed to "the type's partial_payment_tolerance_usd" in both the rule and the compute. The new return allowance (0/4/2) is stated in the rule and implemented. The "when no earlier debit remains" clause is gone. Equivalent (O-3 closed).
- **presuspension.** The hold-timing rule now states "requested on or after the examined installment's scheduled due date and no more than thirty days after it", which matches `hold_request_lag >= 0` (O-4a closed). The hold is selected by decision_date in both faces (O-4b closed). Equivalent.
- **resumption.** "never fewer than the type's resume_min_days_to_next_installment" is implemented as `MX(P('resume_min_days_to_next_installment'), restart_alignment)`. The assistance outcome is read for the suspending hold's id. Equivalent.
- **reaging.**
  - The rule now drops "uncured" ("the installment carrying a plan's most recent missed entry from before a hardship suspension"), matching the compute (O-5a closed).
  - The term-start fallback is in the rule ("when installment 1 carries no payment entry it is treated as a plan without a down payment") and in the compute (O-5b closed).
  - Branch 2 is now "spread evenly over those installments and the re-aged installment's own new place together", implemented as `installment_amount + ⌈r/(n+1)⌉`.
  - Equivalent.
- **restructure.**
  - `debit_within_notice` is now `0 <= DAYS(NOW, anchor) <= 3`, matching "on or after the handling date and no more than three days after it" (O-6 closed).
  - The new final-due-date and count sentence governs tool arguments the compute does not produce. It is quoted under task 1 and is not a compute binding.
  - Equivalent.
- **"kept installment payments".** This term now replaces "installments paid" throughout, so the extension no longer re-defines base measure `plan_msr_installments_paid` under the same name (O-2 closed).

### action_binding_and_uuids (revision_2)

- The `(target_tool, computes)` pairs and uuid8s are unchanged from revision_1 (tool hash unchanged). PASS, carried forward.
- **F-5 re-check (tool versus rule).** The reaging rule now reads "Under every method the deferral places the re-aged installment one period after the plan's current final installment; where the re-aged remainder is spread, that installment carries only what the arrangement_balance still leaves …". Branch 2 now spreads over the following installments plus the re-aged installment's own new place. Both match what `reage_missed_installment_128922de` does: it always appends the installment and sets the regular amount. **F-5 closed.**

### prerequisite_graph (revision_2)

- The edges, kinds, gates, `resolved_by` and acyclicity are the same as revision_1. Every `policy_source` is still found verbatim in the blocked policy's own rule.
- handover's condition no longer adds the anchor clause (O-9 closed).
- The `effect` texts no longer make claims specific to one world (O-10 closed).
- O-8 (the resumption edge's `gate: plan_installments.event_type` is a field, not an eligibility gate) is kept by the reworker. It is still an observation with no consequence.

### prerequisite_sentences (revision_2)

- **resumption → presuspension.** "A suspended plan is not resumed until its installment history carries a missed entry for the last installment whose pre-suspension grace had run out by the date missed-installment counting stopped." It now uses the extension's own term "pre-suspension grace" and its own cutoff, so the base-"grace period" second reading is gone. PASS.
- **restructure → presuspension.** "…records as missed the last installment whose pre-suspension grace had run out by the time missed-installment counting stopped." Its scope now equals the condition ("by the date missed-installment counting stopped") and the resolving rule. **F-3 closed.** PASS.
- **restructure → reaging.** "…a re-aging deferral for the installment with the most recent missed entry." PASS. The only deferral writer is `reage_missed_installment_128922de`.
- **handover → redating, reaging → resumption, reaging → presuspension.** Unchanged wording. PASS.
- **Second wording of a dependency.** The reaging rule no longer opens with "After a plan returns from a hardship suspension" (O-11 closed).
- No extended rule names a tool, a policy id or a row id, and no extended rule states a cross-problem order without a declared edge behind it.

### override_declarations (revision_2)

- **presuspension.** Two `overwrite` entries are now declared:
  - (i) base `plan_evt_installments` "The grace period is grace_period_days_manual calendar days … the day after the due date being day one.", replaced by the pre-suspension grace;
  - (ii) base `plan_evt_suspension` "Missed-installment counting stops while the plan is suspended and restarts from the new schedule.", replaced by the counting-cutoff ladder.
  - The rule confines the replacement: "for that determination the counting cutoff, the grace start and the grace length set out below apply". **F-1 closed** for the quantity it governs.
  - Residual observation O-14: both superseded clauses are wider than their replacements. (i) is the general grace sentence for every missed entry. (ii) also carries "restarts from the new schedule". Read literally, the declaration leaves ordinary, non-suspension misses and post-resumption counting without the superseded wording. Neither task uses either case, so there is no consequence.
- **handover.** Its tolerance is now base's type tolerance, so no deviation remains and `overwrite: []` is correct. **F-4's override face closed.**
- **resumption.** The floor removes the possible conflict with the base minimum. **F-6 closed.**
- **reaging.** `replaced_by` now quotes the standard spread method that actually deviates (O-12 closed). The merged semantics are unique.
- **restructure.** `overwrite` now declares "it re-spreads the current arrangement_balance over a new count of installments", replaced by "…re-spreads the restructure balance evenly over the restructured count". **F-2 closed.** Base's count maximums, minimums and the affordability test are still inherited.
- **redating.** No change in its relation to base. PASS.

### factor_ladders (revision_2)

| Policy | Factors (label: tiers) | param / method | Cross-difficulty |
| --- | --- | --- | --- |
| redating | lead (param 3/5/7), clock_start (method), day_count (method), buffer (param 2/4/0; non-plan returns only) | 2 / 2 | buffer → account |
| handover | setup_notice (param 3/4/5), day_count (method), extension (param 0/3/2), **return_allowance (param 0/4/2, new)** | 3 / 1 | extension → account |
| presuspension | cutoff (method), grace_length (param 9/**4**/type), grace_start (method), hold_timing (param 2/1/0), weekend (param 2/1/0) | 3 / 2 | cutoff, hold_timing → hardship |
| resumption | restart_lead (param **22**/17/type), clock (method), cooldown (param **6**/3/0), statement (param 5/2/0), alignment (method) | 3 / 2 | lead, clock → hardship; statement → account |
| reaging | method (method: append / spread incl. own place / spread), tolling (param), goodfaith (param), term_start (method) | 2 / 2 | tolling → hardship |
| restructure | balance (method), relief, missed penalty, return penalty, tenure, credit bonus (param) | 5 / 1 | relief → hardship; bonus → account |

- **F-7 re-check (tiers that coincide with the type's value).**
  - The handover tolerance ladder is gone.
  - grace_length 9/4 never equals a type grace (0, 3, 5, 7, 10).
  - restart_lead 22/17 never equals a type `resume_min` (7, 10, 14, 21).
  - **F-7 closed.**
- **O-1 re-check.** The buffer now reads only returns of payments outside any plan. Its fall-through is reachable, and the tier no longer rests on the mirror of the plan's own return. **O-1 closed.**
- **New factor, `setup_notice_return_allowance`.** It is multi-source (kept installment payments AND other returned installment payments in 12 months). Its tiers 0/4/2 are distinct and stated in the rule, and its fall-through equals `baseline.rule` ("the set-up notice return allowance is two days"). It is a plausible lever for a collector: more notice when the plan has repeated returns. Its conditions are the same as those of the redating lead factor in the same task, which is a design observation (O-15), not a defect.
- **Totals.** Every policy has 4–6 factors with ≥ 2 parameter and ≥ 1 method. Each task keeps multi-source factors and at least one cross-difficulty factor.

### findings (revision_2)

| id | revision_1 class | revision_2 status |
| --- | --- | --- |
| F-1 | SOURCE-POLICY RED | **closed** (declared overwrites; residual observation O-14) |
| F-2 | SOURCE-POLICY RED | **closed** |
| F-3 | SOURCE-POLICY RED | **closed** |
| F-4 | SOURCE-FACTOR RED | **closed** (tolerance is the type tolerance, no longer a factor; replaced by return_allowance) |
| F-5 | observation | closed |
| F-6 | observation | closed |
| F-7 | observation | closed |
| O-1 … O-6, O-9 … O-12 | observations | closed |
| O-7, O-8 | observations | kept (no consequence) |
| **R2-N1** | — | **new: account returned-payment block versus card autopay.** The world-dependent half is in `0.md` revision_2. The charter-global half: the plan charter lets a payment-method change go to card or ACH autopay checking only the plan type's flags, while the account charter's returned-payment block can forbid every electronic installment on the same account. No plan rule mentions the block. |
| O-13, O-14, O-15 | — | new observations (above) |

### closing_status (revision_2, written after both revision_2 reveals, 2026-10-10T19:23Z)

The difficulty is **not closed**: task 0 fails one relationship.

| task | policy self-consistency | problem tree | factors bear weight | unique solution | revision_2 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS (plan charter); cross-product silence carried under R2-N1 | PASS | PASS (F-4 closed) | **SOURCE-TASK RED (R2-N1, new: the account returned-payment block makes GT's debit-card autopay from 2026-10-14 contrary to `account_evt_payment_channels`)** | SOURCE-TASK RED |
| 1 | PASS (F-1, F-2, F-3 closed) | PASS | PASS | PASS (`final_due_date` fixed by rule) | PASS |

**Closure of the round-1 items.**
- Every round-1 RED is genuinely closed: F-1, F-2, F-3, F-4 and the task 1 `final_due_date` ambiguity.
- The round-1 observations the reworker claimed are closed: F-5, F-6, F-7, O-1 … O-6 and O-9 … O-12.
- O-7 and O-8 are kept with acceptable reasons.

**Regression.** R2-N1 (task 0) was introduced by the O-1 seed fix.

**New observations.** O-13, O-14 and O-15.

**Checklist items that hold:**
- one file per task, with revision_1 preserved verbatim and revision_2 appended;
- scopes disjoint and covering all six extended policies (GT `charter_scope` unchanged);
- uuid8s distinct and frozen;
- trees: task 0 has n = 1 with 1 value_input edge, task 1 has n = 3 with 3 value_input edges; both roots are user-owned; acyclic;
- every computation has a self-sufficient baseline, 4–6 factors (≥ 2 parameter, ≥ 1 method), every factor bearing weight, and fall-backs different from gold (task 0: 10 and 8; task 1: 6, 14, 253 and 253).

**Not satisfied:** every comparison carrying a PASS (task 0).

The gates were cited from the coordinator's revision_2 snapshot, not re-run.

### erratum on revision_1 timestamps (revision_1 text left untouched)

The "Freeze time" labels in revision_1 (13:25Z in `0.md`, 13:40Z in `1.md`) were hand-estimated and are later than the revision_1 reveal (13:22Z). The actual order was freeze first, then reveal. The evidence is the command that performed the round-1 reveal: it first printed the sha256 of the three frozen files (`0.md` `10e38fab…`, `1.md` `da8ae8cf…`, `_difficulty.md` `a27779d0…`) and the system time 2026-10-10T13:21:45Z, and only then opened the task JSONs. The revision_2 timestamps above are taken from the system clock.

---

## revision_3

### charter_global_frozen (revision_3)

- Freeze time: see the system time printed with this append. Auditor: the same erl-task-policy-audit auditor (Claude Opus 5.5 subagent), independent of the instantiator and the reworker.
- Shared inputs:
  - `plan.extended.yaml` sha256 `b1187c19840640b6dbbd8fc238d8e84a1f6738083c1f6f0e8be194a2b7e42c6e`. It **changed** since revision_2 (`c94e5a69…`).
  - `task_tools.py` `2c3196ee…9a59a`, unchanged.
  - The base copy (lines 1–1159) is still byte-identical to `blueprint/products/plan.yaml`.
- What was re-derived. The changed passages (redating buffer, handover rule and return allowance, presuspension overwrite) were re-derived. The remaining policies were re-read through their compute: a replay of every policy's compute and factor substitution on both revision_3 worlds gives values identical to revision_2, figure for figure.
- **contamination_disclosure.**
  - The revision_1 and revision_2 GT of both tasks were read in earlier rounds.
  - In this round, the auditor's first inspection command also printed the tail of `tasks/payment_arrangement_servicing/worklog.md` before this freeze. That tail includes the round-3 record, which restates scored values: "shift 8 unchanged", "buffer 2", "Gold (card_autopay, recorded_call, 7) unchanged".
  - These values equal the revision_2 GT already known, so no new scored value entered the derivation. Revision_3 is a verification re-derivation, not a blind one.
  - `tasks/{0,1}.json` (revision_3) were not opened before this freeze.
- Gate snapshot supplied: 7/7 green. Cited, not re-run.

### changes verified (revision_3)

- **redating buffer window.** It is now "the payments on the placed account that were not made under a payment plan and were returned in the last twelve months". The rule, compute (`within_months=12` on both XCOUNT and XLATEST), ladder and inputs agree.
  - The compute binding is still named `account_returns_6m`. That is cosmetic and recorded as O-16: the name does not affect the evaluation.
  - Rule and compute are equivalent.
- **handover.**
  - The return allowance now reads "the plan's returned installment payments in the last six months". The rule, compute (`within_months=6`), ladder and inputs (`within_months: 6`) agree. The binding is still named `handover_other_returns_12m` (cosmetic, O-16).
  - Its condition window (6 months) now differs from the redating lead's (12 months). **O-15 closed.**
- **handover, new sentence (charter-global half of R2-N1).** "A payment-method change does not lift a returned-payment block that the account rules have placed on the placed account: an automatic method is authorized under this policy only while the placed account accepts electronic payments, that is while no such block is in force on the handling date."
  - This reconciles the plan charter with `account.yaml` `account_evt_payment_channels`.
  - It is a cross-category state condition on acting now, not a compute input, so no binding is needed.
  - It names no tool, policy id or other problem, and states no cross-problem order. It is not a prerequisite sentence: no write in this difficulty lifts a block.
  - **R2-N1 charter-global half closed.**
- **presuspension overwrite (O-14).**
  - The `plan_evt_suspension` superseded clause is narrowed to "Missed-installment counting stops while the plan is suspended". "…and restarts from the new schedule" stays inherited.
  - The grace-sentence overwrite is scoped by the rule's "for that determination the counting cutoff, the grace start and the grace length set out below apply". For ordinary misses, the inherited `grace_elapsed` gate keeps the base grace.
  - The merged semantics are unique. **O-14 closed.**
- **Unchanged (confirmed by replay and by re-reading the revision_2 conclusions).** policy_conflict_scan, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences and factor_ladders keep their revision_2 conclusions. The factor counts and labels are unchanged. The new handover sentence adds no edge, so the edge set and acyclicity are unchanged.

### findings (revision_3)

| id | revision_2 status | revision_3 status |
| --- | --- | --- |
| R2-N1 | SOURCE-TASK RED (task 0) | charter half **closed** (above); world half verified in `0.md` revision_3 |
| O-14 | observation | closed |
| O-15 | observation | closed |
| O-13 | observation | kept, with the reworker's reason (the plan base suspends on entry to hardship_hold at approval). Accepted. |
| O-7, O-8 | kept | kept |
| O-16 | — | new observation: compute binding names `account_returns_6m` and `handover_other_returns_12m` no longer match their windows (12 and 6 months). Cosmetic; no effect on evaluation. |

### closing_checklist (revision_3, written after both revision_3 reveals)

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

- **Task files.** One file per task (`0.md`, `1.md`), with `_difficulty.md` alongside. revision_1 and revision_2 are preserved verbatim and revision_3 is appended. Every revision_3 comparison carries a PASS.
- **Scope and tools.** All six extended policies are covered. The task scopes are disjoint (GT `charter_scope`: task 0 {redating, handover}; task 1 {presuspension, resumption, reaging, restructure}). Task tools and GT are closed. The six uuid8s were independently generated and frozen.
- **Problem trees.** Task 0 has 1 prerequisite problem with 1 value_input edge. Task 1 has 3 prerequisite problems with 3 value_input edges. Both roots are owner=user tools. The difficulty-wide graph has 6 edges, no cross-task reference and no cycle.
- **Factors.** Every computation states a self-sufficient baseline and 4–6 factors (≥ 2 parameter, ≥ 1 method). Each task has multi-source and cross-difficulty factors (task 0: account; task 1: hardship and account). Every ladder has three tiers stated in its rule, distinct in outcome and plausible for the business. Every factor bears weight against an honest baseline. Fall-backs differ from gold: task 0 gives 10 against 8 and 8 against 7; task 1 gives 6 against 5, 14 against 64, 253 against 243 and 253 against 215.
- **Gates.** The instantiation-stage gates on the final form are cited from the coordinator's revision_3 snapshot (7/7 green, `/tmp/env0050_views/gates/env0050_payment_arrangement_servicing_r3_gates.txt`). The auditor did not re-run them.
- **Remaining observations (not grounds for rework):**
  - O-7: the resume tool does not move the account status.
  - O-8: the resumption state-gate field form.
  - O-13: hardship "same day" wording against suspension on the decision date.
  - O-16: stale binding names.
  - O-17: an off-by-one window label in task 0's tracing.
  - Task 1's `arrangement_balance` exceeds its `balance_due` after the client credit.

**The difficulty passes the source-layer audit at revision_3.**
