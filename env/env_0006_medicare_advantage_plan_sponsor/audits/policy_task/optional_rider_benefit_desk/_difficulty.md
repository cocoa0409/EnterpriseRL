# Policy-task audit — optional_rider_benefit_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-21 (session clock), written **before any task's `evaluation_criteria` / `computations` were read**.
- Auditor: independent source-layer auditor (not the instantiating agent).
- Freeze hashes (sha256[:16], verified on disk at freeze time):
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/optional_rider_benefit_desk/osb.extended.yaml` = `c9b6d66de893b951`
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/optional_rider_benefit_desk/task_tools.py` = `77ec40148512d29a`
  - masked view `_masked_views/0.masked.json` = `355570060acfc704`
  - masked view `_masked_views/1.masked.json` = `eb975e755e24a52b`
- Fields permitted at freeze: the base section and `extended_policies` of `osb.extended.yaml`; `task_tools.py`; `blueprint/products/*.yaml`; `blueprint/blueprint.yaml`; `blueprint/db_schema.json`; `blueprint/share_tools.py`; `erlbench/`; the gate-layer compute evaluator `skills/erl-task-instantiate/scripts/check_compute.py`; and per task only `frozen_time`, `user_scenario`, `initial_state`.
- Fields explicitly masked at freeze: `evaluation_criteria`, `computations` (including `expected`, `factor_trace`, `factor_sensitivity`, `baseline_result`, every `step`/`arg`), `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- Verified that the masked views carry exactly the three permitted keys and nothing else.
- No contamination: `tasks/0.json` and `tasks/1.json` were not opened, and no recursive search was run whose match domain included them.

### entry_conditions

The brief supplied the instantiation-stage gate snapshot with actual output lines: `check_extended` (EXTENDED OK), `check_task_tools` (TASK TOOL CONTRACT OK), `replay_tasks` (REPLAY OK, both tasks deterministic, non-vacuous, 0 errors, closure matches initial_state), `check_solvability` (SOLVABILITY OK), `check_compute` (COMPUTE OK), `check_grounding` (GROUNDING OK), `check_cross_fire` (SCOPE OK). `check_traceability` cannot run before the render step; `check_cache_diff` is informational. Entry conditions are met. **These are the qualification to enter a manual audit, not evidence of correctness**, and several findings below sit in exactly the space the scripts cannot see.

### policy_conflict_scan

The structured policy in force for `osb` is the 12 base policies plus the 7 extended policies of `osb.extended.yaml`. The base section is a verbatim copy of `blueprint/products/osb.yaml` (compared field by field; no divergence).

Scope claims, derived from each task's root problem and its prerequisite closure:

| Task | Policies claimed (root first) |
| --- | --- |
| 0 | `osb_ext_rider_benefit_line_settlement`, `osb_ext_rider_arrears_settlement`, `osb_ext_precover_premium_credit`, `osb_ext_adjusted_line_restatement` |
| 1 | `osb_ext_rider_closure_settlement`, `osb_ext_unpaid_premium_suspension_arrears`, `osb_ext_unbilled_cycle_premium_charge` |

4 + 3 = 7, pairwise disjoint and jointly complete over the extended set. **PASS.**

Overlapping-subject scan across the merged policy:

- `osb_rider_premium_charge` / `_payment` / `_credit` are each written by exactly one extended policy. No two extended policies compute the same quantity on the same subject.
- Time anchors: every extended policy anchors on `rider_effective_date`, `benefits_available_from`, `rider_end_date` or a ledger `posted_date`. No two anchor the same quantity differently.
- Cross-category read boundaries: `advantage` is declared by four policies, `allowance` by one. Every declared category is a real sibling difficulty (`blueprint.yaml` difficulties 0 and 2). No policy reads a category it does not declare.
- **One genuine conflict found — see finding F1** (`osb_premium_suspension_and_recovery` sentence 4 against `osb_ext_rider_benefit_line_settlement`).

### rule_compute_equivalence

Check 2 was run binding by binding over all seven extended policies against the gate-layer evaluator's actual semantics (`skills/erl-task-instantiate/scripts/check_compute.py`: `within_months=N` means `0 <= MONTHS(row_date, NOW) < N`, lower bound inclusive / upper exclusive; `MONTHS` is whole calendar months floored by day-of-month; **no benefit-year or period scoping is ever applied automatically**; `RND` is Python `round`, i.e. banker's rounding).

Most bindings quote a verbatim rule sentence and implement it. The following do not, and are carried as findings F3, F4, F5, F6, F8, F9 below.

Factor-ladder leg of the equivalence: for every declared factor, each `ladder` tier was matched against a sentence of the `rule` and a branch of the `decides` binding. Every tier has both — with the one exception recorded in F3 (the "no days of grace at all" tier of `governing_days_of_grace`, whose stated value 0 is not the value the compute produces).

### action_binding_and_uuids

Seven task tools, seven `(target_tool, computes)` pairs, each claimed by exactly one policy:

| Tool | owner | Policy | computes |
| --- | --- | --- | --- |
| `settle_rider_benefit_line_e49937be` | agent | `osb_ext_rider_benefit_line_settlement` | `rider_paid_amount` |
| `reverse_rider_benefit_line_9daedfb7` | agent | `osb_ext_adjusted_line_restatement` | `restated_member_share` |
| `pay_rider_premium_by_telephone_9597e982` | **user** | `osb_ext_rider_arrears_settlement` | `settlement_amount` |
| `post_rider_premium_credit_050a58f6` | agent | `osb_ext_precover_premium_credit` | `credit_amount` |
| `post_rider_premium_charge_4237e97e` | agent | `osb_ext_unbilled_cycle_premium_charge` | `charge_amount` |
| `suspend_rider_for_unpaid_premium_a0d6b513` | agent | `osb_ext_unpaid_premium_suspension_arrears` | `arrears_at_suspension` |
| `end_rider_at_member_request_09efad65` | **user** | `osb_ext_rider_closure_settlement` | `closing_premium_balance` |

No docstring names another tool and none states a route. **PASS on tool naming.**

uuid8s sorted: `050a58f6`, `09efad65`, `4237e97e`, `9597e982`, `9daedfb7`, `a0d6b513`, `e49937be`. No shared prefix (leading nibbles `0,0,4,9,9,a,e`), no sequence, numeric gaps between sorted values are wildly uneven (8.2e7 / 9.4e8 / 1.4e9 / 1.4e8 / 5.3e7 / 1.1e9), and the longest substring shared by any pair is 3 nibbles (`97e`, one coincidence). Consistent with seven independent draws. **PASS.**

Two observations on the tool module are recorded as F12 and F14.

### prerequisite_graph

Check 7 over the whole graph. Every one of the seven policies has `prerequisite` filled in (`[]` where there is none). Five edges declared:

| # | Blocked policy | Depends on | kind | gate | form |
| --- | --- | --- | --- | --- | --- |
| E1 | `osb_ext_rider_benefit_line_settlement` | `osb_ext_rider_arrears_settlement` | state_gate | `osb_benefit_payment.rider_in_force_on_service_date` | state |
| E2 | `osb_ext_rider_benefit_line_settlement` | `osb_ext_adjusted_line_restatement` | value_input | `benefit_used` | state |
| E3 | `osb_ext_rider_arrears_settlement` | `osb_ext_precover_premium_credit` | value_input | `credits_counted` | state |
| E4 | `osb_ext_rider_closure_settlement` | `osb_ext_unpaid_premium_suspension_arrears` | value_input | `standing_basis` | state |
| E5 | `osb_ext_unpaid_premium_suspension_arrears` | `osb_ext_unbilled_cycle_premium_charge` | value_input | `charges_counted` | state |

- Every `problem` points at another extended policy id in this file; none points at a base policy or at itself.
- The graph is a forest of two trees (root `..._benefit_line_settlement`; root `..._closure_settlement`) and is **acyclic**. No edge crosses between the two task scopes.
- Every `form` is `state`; **no edge is action-form, so no `fallback_reason` is required and none is present**. The state form's priority is honoured throughout.
- Every `gate` names a real object: E1 names a base eligibility that genuinely exists (`osb_benefit_payment` rule sentence 2, "The rider stands at active on the date of service of the line"); E2/E3/E4/E5 each name a binding that genuinely appears in the blocked policy's own `compute` (`benefit_used`, `credits_counted`, `standing_basis`, `charges_counted` — all present).
- Every `resolved_by` is the depended-on policy's own `target_tool`, and each genuinely moves the gate: `pay_rider_premium_by_telephone_9597e982` is the **only** tool in the module that writes `status="active"`; `suspend_rider_for_unpaid_premium_a0d6b513` is the only one that writes `status="premium_suspended"`; `reverse_rider_benefit_line_9daedfb7` is the only one that creates a `claim_status="reversed"` row; `post_rider_premium_credit_050a58f6` and `post_rider_premium_charge_4237e97e` are the only writers of their ledger event types.
- No `condition` is strengthened or weakened relative to the sentence it rests on (checked one by one against the quoted sentence).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in the `prerequisite` blocks.

**PASS.**

### prerequisite_sentences

Check 6, four-point test on each of the five edges. Each `policy_source` was located verbatim in the blocked policy's **own** `rule` (confirmed by exact string match against the rule text).

- **E1** — "A benefit is not settled on a submitted line until the rider it is claimed under stands in force with no rider premium outstanding against it on the day the service was given."
  Ordering connective *until* ✓. State form: "stands in force with no rider premium outstanding against it" — a record-visible state (`osb_riders.status`, `osb_riders.rider_premium_balance_due`) with no action, performer or tool ✓. No tool name, policy id, snake_case token or row id ✓. Strength matches the `condition` ✓.
  *Derivation to the single resolving action:* the sentence demands the rider be in force with nothing outstanding. Reading the other policies' own rules, `osb_ext_rider_arrears_settlement` is the only one whose result is money that clears rider premium owed ("The money a member is asked for to clear the rider premium they owe…"), and base `osb_premium_suspension_and_recovery` sentence 5 states "Paying the arrears in full restores the rider from the day the money is posted". Exactly one write brings the state about. **One reading.**
- **E2** — "What is left of the benefit year's maximum is not worked out before a reversal stands on the member's benefit history against every settled line the plan has marked as adjusted."
  Ordering *before* ✓; state "a reversal stands … against every settled line … marked as adjusted" ✓ (`osb_benefit_claims.claim_status`, `.source_claim_id`); no tool/id ✓. Only `osb_ext_adjusted_line_restatement` describes backing a line out; exactly one write. **One reading.**
- **E3** — "The money a member is asked for is fixed only after every rider premium charge raised for a coverage month beginning before the day the rider took effect carries a credit against it."
  Ordering *only after* ✓; state "carries a credit against it" ✓; no tool/id ✓. Only `osb_ext_precover_premium_credit` posts such a credit. **One reading.**
- **E4** — "The rider premium left owed when a rider is closed is fixed only once the rider stands suspended for unpaid premium on its own record."
  Ordering *only once* ✓; state "stands suspended for unpaid premium on its own record" ✓; no tool/id ✓. Only `osb_ext_unpaid_premium_suspension_arrears` puts a rider into premium suspension. **One reading.**
- **E5** — "The rider premium standing owed is not struck until every billing cycle the rider has been in force through carries a rider premium charge on the rider premium account."
  Ordering *until* ✓; state "carries a rider premium charge on the rider premium account" ✓; no tool/id ✓. Only `osb_ext_unbilled_cycle_premium_charge` raises one. **One reading.**

- No blocked rule carries a second wording of its dependency, another problem's tool name, or an aggregated chain.
- No depended-on rule restates the sentence (checked in both directions across all seven rules).
- No docstring states an action's position relative to another tool. Docstrings do carry generic ordering words ("read … before the call", "Afterwards the member's record shows …") — recorded as observation F14, not a red light, because none names another tool or a route.
- No cross-problem order is stated in any rule that grounds no declared edge; and no task's tree rests on a **base** rule sentence for its ordering.

**PASS.**

### override_declarations

Check 1's finding half, run sentence by sentence over each extended policy against every entry of its `base_policy_refs`.

Declared overrides (4 in total), each naming its base sentence and each merging to a unique semantics:

- `osb_ext_rider_benefit_line_settlement` × 2 against `osb_benefit_payment`: the out-of-network sentence (base denies the line where the share is zero; extended carries nothing into the calculation — same outcome, restated as a calculation) and the annual-maximum sentence (base states the cap narratively; extended defines "what is left" arithmetically). Both named, both merge uniquely. ✓
- `osb_ext_adjusted_line_restatement` × 1 against `osb_benefit_payment`: the same out-of-network sentence, for the reversal's benefit basis. Named, merges uniquely. ✓
- `osb_ext_unbilled_cycle_premium_charge` × 1 against `osb_rider_premium_billing_and_posting`: base charges "for each coverage month from the rider effective date to the rider end date"; extended fixes the coverage months one charge carries. Named, merges uniquely. ✓

Base provisions **not** hit by any `overwrite` and therefore inherited in full were each checked for whether an extended policy handles the governed quantity differently:

- `osb_rider_enrollment`, `osb_waiting_period`, `osb_termination_and_cancellation`, `osb_frequency_limitations`, `osb_coordination_with_medical_plan`, `osb_predetermination_and_appeal`, `osb_claim_reversal_and_correction`, `osb_agg_multi_holding` — no extended policy contradicts any sentence of these on a scored quantity.
- `osb_premium_suspension_and_recovery` — **one undeclared conflict, finding F1.**
- `osb_agg_combined_rider_maximum` — **one dropped branch, finding F13** (observation; no consequence on either seeded world).

The three disguised forms were looked for specifically. No anonymous intermediate factor and no 0/1 multiplier was found. One dropped branch (F13). No author's note calls a base output a "wrong value".

### factor_ladders

Charter-global structure of the factors. Counts per policy:

| Policy | factors | parameter | method | ladder tiers (as stated) | declared cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `..._rider_benefit_line_settlement` | 5 | 3 | 2 | 3,3,5,3,3 | — |
| `..._rider_arrears_settlement` | 6 | 2 | 4 | 3 each | advantage ×3 |
| `..._precover_premium_credit` | 4 | 2 | 2 | 3 each | advantage ×2 |
| `..._adjusted_line_restatement` | 5 | 3 | 2 | 3,5,3,3,3 | allowance ×1 |
| `..._unbilled_cycle_premium_charge` | 4 | 2 | 2 | 3 each | advantage ×2 |
| `..._unpaid_premium_suspension_arrears` | 5 | 2 | 3 | 3 each | advantage ×1 |
| `..._rider_closure_settlement` | 5 | 3 | 2 | 3 each | advantage ×2 |

Every policy is inside the 4–6 bound and clears the 2-`parameter` / 1-`method` floor **as declared**. Every ladder has at least three tiers as written, the fall-through counted, and within each ladder the tiers are pairwise disjoint as stated. Every factor's `decides` names an input binding, never `result`. Binding sets are disjoint within each policy (checked pairwise).

Label honesty was checked one factor at a time: each `method` factor's tiers genuinely select a different algorithm (a different window, a different aggregate, a different formula shape), and each `parameter` factor's tiers genuinely select a different number. No mislabelling found, and every `method` tier names a computation rule the charter states.

Two structural defects were found and are carried as findings:

- **F2** — the conjunct "the rider is billed on the medical plan bill" is vacuous charter-wide, which strips seven ladders of a reachable tier.
- **F7** — `refund_ceiling_basis` declares a `cross_difficulty` it does not exercise.

Whether each factor **bears weight** is a fact about one world and lives in each task's `factor_weight`.

### findings

#### F1 — `SOURCE-POLICY RED`: undeclared override of `osb_premium_suspension_and_recovery` sentence 4 (bears on **task 0**)

- **Symptom.** Two clauses of the merged policy give a different benefit on the same line in the same situation: nothing, or the full computed benefit.
- **Root cause.** `osb_ext_rider_benefit_line_settlement` replaces base `osb_benefit_payment`'s treatment of the suspended-rider case *by way of its prerequisite sentence*, but `osb_premium_suspension_and_recovery` — which carries its own, contrary sentence about the very same lines — is neither in that policy's `base_policy_refs` nor named in any `overwrite`. It is therefore inherited in full.
- **Evidence.**
  - Base, `osb.extended.yaml` → `policies` → `osb_premium_suspension_and_recovery` → `rule`, sentence 5: *"Paying the arrears in full restores the rider from the day the money is posted, **and services given while it was suspended stay the member's own cost**."*
  - Extended, `osb_ext_rider_benefit_line_settlement` → `rule`, penultimate sentence: *"A benefit is not settled on a submitted line until the rider it is claimed under stands in force with no rider premium outstanding against it on the day the service was given."*
  - `osb_ext_rider_benefit_line_settlement` → `overwrite` names only two sentences, both from `osb_benefit_payment`; neither is the sentence above.
  - `base_policy_refs` for that policy = `[osb_benefit_payment, osb_frequency_limitations, osb_agg_combined_rider_maximum, osb_coordination_with_medical_plan, osb_predetermination_and_appeal]` — `osb_premium_suspension_and_recovery` is absent.
- **Demonstrated consequence.** Demonstrated against task 0's world in `0.md` → `policy_self_consistency`: the base clause yields **0.00** on the pended hearing-aid line and the extended clause yields **1312.50**. The task has two defensible answers on its root scored parameter.
- **Affected artifact and location.** `env/env_0006_medicare_advantage_plan_sponsor/tasks/optional_rider_benefit_desk/osb.extended.yaml`: `policies[osb_premium_suspension_and_recovery].rule` sentence 5, against `extended_policies[osb_ext_rider_benefit_line_settlement].rule` and its `overwrite` list.

#### F2 — `SOURCE-FACTOR RED`: `rider_premium_billed_with_plan` is constant, so seven ladders lose a reachable tier (bears on **tasks 0 and 1**)

- **Symptom.** Tier conditions of the form "the rider is billed on the medical plan bill" divide no customers, and the complementary tiers ("the rider is billed on its own", "otherwise") can never be selected by any customer of this category.
- **Root cause.** `P('rider_premium_billed_with_plan')` is `True` on **every one of the six variants**, and `osb_riders.variant_name` is a closed enum over exactly those six (`db_schema.json`). `billed_with_plan` is therefore a constant of the charter, not a fact about a customer.
- **Evidence.** `osb.extended.yaml` → `variants[*].parameters.rider_premium_billed_with_plan`: Preventive Dental `True`, Vision Plus `True`, Hearing Advantage `True`, Comprehensive Dental `True`, Premier Dental `True`, Dental Vision Hearing Bundle `True`.
  Ladders affected (tier that can never fire, quoted from `factors[].ladder`):
  1. `..._rider_arrears_settlement.combined_bill_span` — fall-through *"otherwise: the money left over is taken over the bills raised within the days of grace the rider held allows"*.
  2. `..._rider_arrears_settlement.surplus_carried_to_rider` — fall-through *"otherwise → nothing, the rider being billed on its own"*.
  3. `..._rider_arrears_settlement.money_reaching_rider_basis` — fall-through reachable only through an empty plan ledger, never through "billed on its own".
  4. `..._precover_premium_credit.plan_bill_cycle_months` — fall-through *"otherwise: the charge carries the whole calendar months from the day the plan received the rider request to the handling date"*.
  5. `..._precover_premium_credit.months_outside_cover` — tier 2 *"the rider is billed on its own"*.
  6. `..._unbilled_cycle_premium_charge.plan_bill_cycle_length` — fall-through *"otherwise: one charge carries the whole calendar months from the day the rider took effect to the handling date"*.
  7. `..._unbilled_cycle_premium_charge.months_met_from_combined_bill` — fall-through *"otherwise: the number of payments posted to the rider premium account"*.
  8. `..._rider_closure_settlement.bill_money_set_against_closing` — fall-through *"otherwise → nothing"*.
- **Demonstrated consequence.** Each listed ladder has **two** reachable tiers, not three. Worse, four of them take that unreachable fall-through as the factor's `baseline` — a default the business applies to no customer it has, which is the straw-man baseline in another form. Demonstrated per task in `0.md` → `factor_weight` (`plan_bill_cycle_months`: the baseline books a single quarterly charge as carrying **8** coverage months) and `1.md` → `factor_weight` (`plan_bill_cycle_length`: the baseline books one charge as carrying **6** coverage months for a quarterly-billed plan).
- **Affected artifact and location.** `osb.extended.yaml`: `variants[*].parameters.rider_premium_billed_with_plan`, and the eight `factors[].ladder` / `factors[].baseline` blocks listed above.

#### F3 — `SOURCE-POLICY RED`: the days-of-grace window is promised in days and implemented in whole months (bears on **task 1**)

- **Symptom.** The rule fixes the span by a number of days of grace; the compute selects rows by a whole-calendar-month window, so the set of ledger rows counted is not the set the rule describes. A tier whose stated value is "no days of grace at all" produces a one-month window.
- **Root cause.** `grace_window_months: MX(1, int(governing_grace_days / 30))` (and `MX(1, int(P('rider_premium_grace_period_days') / 30))` in the arrears policy) converts a day count into a month count by integer division, then floors it at 1; `within_months=N` then selects rows by `0 <= MONTHS(posted_date, NOW) < N`, a calendar-month test, not a day test.
- **Evidence.**
  - `..._unpaid_premium_suspension_arrears.rule`: *"The days of grace that govern the span the figure is struck over are the days of grace the rider held allows"* … *"where the rider stands ended, **no days of grace govern it at all**."*
  - `..._unpaid_premium_suspension_arrears.compute`: `grace_window_months: MX(1, int(governing_grace_days / 30))`. With `governing_grace_days = 0` this is `MX(1, 0) = 1` — a one-month window, not none.
  - `..._rider_arrears_settlement.compute`: `grace_window_months: MX(1, int(P('rider_premium_grace_period_days') / 30))`.
  - Base `osb_premium_suspension_and_recovery.rule` sentence 3 forbids exactly this substitution: *"Calendar days are counted from the day after that posting date, every day of the week counts, the last day of the grace period is itself inside it, and **full 24-hour periods are never used in place of calendar days**."*
  - Evaluator semantics: `check_compute.py` `_within` → `m = MONTHS(str(d)[:10], NOW); return 0 <= m < within_months`.
- **Demonstrated consequence.** Demonstrated on task 1 in `1.md` → `factor_weight`: with the governing 90 days the window is 3 months and the credit posted 2026-07-05 is counted, giving arrears **73.40**; a reader applying 90 *calendar days* from the handling date 2026-09-18 reaches back to 2026-06-20 and counts the same credit, but the *60-day* rider figure gives a 2-month window that silently drops a credit which 60 calendar days (back to 2026-07-20) would also drop — the two counting conventions agree here only by accident of the seed, while the rule's own "no days of grace at all" tier is unimplementable as written.
- **Affected artifact and location.** `osb.extended.yaml`: `extended_policies[osb_ext_unpaid_premium_suspension_arrears].compute.grace_window_months` and `.factors[governing_days_of_grace].ladder[1]`; `extended_policies[osb_ext_rider_arrears_settlement].compute.grace_window_months`.

#### F7 — `SOURCE-FACTOR RED`: `refund_ceiling_basis` declares a cross-difficulty read it does not make (bears on **task 1**)

- **Symptom.** A factor is declared to decide its tier from another difficulty's records, and lists that difficulty's bindings, while the quantity it decides is computed without reference to any of them.
- **Root cause.** The factor's `bindings` list carries `plan_cycle` and `cycle_months`, which do read `advantage`; but `refund_ceiling` is bound only from `billed_with_plan` (a tier parameter of this product), `F('rider_end_date')` and `F('status')` — all own-holding fields. `plan_cycle` flows to `refund_rate`, which is a *different* factor's quantity.
- **Evidence.** `..._rider_closure_settlement.compute`: `refund_ceiling: last_charge_amount if (billed_with_plan==True and F('rider_end_date')=='') else (0.0 if F('status')=='terminated' else P('monthly_rider_premium'))` — no `CFIELD`, `CPARAM` or `X*` call appears. Against `factors[refund_ceiling_basis]`: `decides: refund_ceiling`, `bindings: [billed_with_plan, plan_cycle, cycle_months, refund_ceiling]`, `evidence: [cross_category, tier_param]`, `cross_difficulty: advantage`.
- **Demonstrated consequence.** The ladder does not bear on the quantity it decides by way of the other product at all: changing `advantage_enrollments.premium_billing_frequency` moves `refund_rate`, never `refund_ceiling`. Demonstrated on task 1 in `1.md` → `factor_weight`. The task's cross-difficulty floor is met only by `bill_money_set_against_closing`, which does genuinely read `advantage_premium_ledger`.
- **Affected artifact and location.** `osb.extended.yaml`: `extended_policies[osb_ext_rider_closure_settlement].factors[refund_ceiling_basis]`.

#### F8 — `SOURCE-POLICY RED`: `cycle_months` in the closure policy rests on no sentence of its own rule (bears on **task 1**)

- **Symptom.** A compute binding that materially moves the scored figure has no basis in the rule; `compute_basis` covers it with a quotation about a different quantity.
- **Root cause.** The closure policy needs to know how many coverage months a billing cycle carries, but no sentence of `..._rider_closure_settlement.rule` says. That definition lives only in two *other* policies' rules.
- **Evidence.**
  - `..._rider_closure_settlement.compute`: `cycle_months: 3 if (billed_with_plan==True and plan_cycle=='quarterly') else (1 if (billed_with_plan==True and plan_cycle=='monthly') else 1)`.
  - `..._rider_closure_settlement.compute_basis.cycle_months` quotes: *"The rate each coverage month is refunded at is the amount of the rider premium charge carrying the most money of any standing on the account. Where that charge carries more than one coverage month, the rate is instead that amount divided by the coverage months it carries…"* — that sentence fixes the *rate*, and says nothing about how many months a cycle carries.
  - A full-text search of `..._rider_closure_settlement.rule` finds no sentence containing "quarterly" or "monthly".
  - Separately, the second and third branches of the expression both yield `1`, so two of the three branches are indistinguishable in outcome.
- **Demonstrated consequence.** Demonstrated on task 1 in `1.md`: `cycle_months = 3` drives `refund_rate = 85.80/3 = 28.60` and `months_after_end = 3 − 1 − 0 = 2`, hence `refund_due = 57.20` — over half the closing figure — from a number the policy's own rule never states. A reader with only this policy cannot reach it.
- **Affected artifact and location.** `osb.extended.yaml`: `extended_policies[osb_ext_rider_closure_settlement].compute.cycle_months` and `.compute_basis.cycle_months`.

#### F10 — `SOURCE-FACTOR RED`: an unreal tier in `credit_ceiling_basis` (bears on **task 0**)

- **Symptom.** A ladder tier makes whether the member gets their money back turn on how many charges happen to be sitting on the account, which is not a condition that line of business weighs for that quantity, and which contradicts the policy's own opening sentence.
- **Root cause.** The tier was written to give the ladder a third outcome rather than to state a rule the business applies.
- **Evidence.** `..._precover_premium_credit.rule`, sentence 1: *"Rider premium charged for a coverage month beginning before the day the rider took effect **is owed back to the member**, and is relieved by a credit against the single rider premium charge that carried it."* Against `.factors[credit_ceiling_basis].ladder[1]`: *"when: no more than one rider premium charge stands on the rider premium account — value: **nothing, no credit being due at all**"*, implemented as `credit_ceiling: … (0.0 if charges_raised<2 else …)`.
- **Demonstrated consequence.** A member billed a month before their cover began, whose account happens to carry one charge rather than two, is owed the money by sentence 1 and refused it by the ladder. No insurer decides a billing refund on the count of entries on the account. Task 0's customer sits on tier 1 so the scored number is untouched; the tier is nonetheless a tier the business does not have, so the ladder has two real outcomes, not three. Recorded against task 0's `factor_weight`.
- **Affected artifact and location.** `osb.extended.yaml`: `extended_policies[osb_ext_precover_premium_credit].factors[credit_ceiling_basis].ladder[1]` and `.compute.credit_ceiling`.

#### F11 — Observation: the precover-credit baseline promises a refund and always computes nothing

- `..._precover_premium_credit.baseline.rule` contains both *"Rider premium charged for a coverage month beginning before the day the rider took effect is owed back to the member"* and *"No coverage month counts as charged before cover began."* Since `credit_before_cap = rate × months_before_cover`, the second sentence forces the baseline to **0.00 for every member in every world**. The baseline is self-sufficient in the narrow sense (a reader does reach a definite number) and differs from gold, so this is not a red light on the letter of the test; but the computation document it will render into states a refund entitlement and then computes nothing, on every world. Bears on task 0.

#### F13 — Observation: the combined rider maximum is a dropped branch

- Base `osb_agg_combined_rider_maximum.rule` sentence 2: *"Each rider's own annual maximum is applied first on its own claims; the combined cap then applies across the riders, and a line that would pass it is paid only up to what is left."* `osb_ext_rider_benefit_line_settlement` lists this policy in `base_policy_refs`, declares no `overwrite` against it, and its `compute` applies only `P('annual_benefit_maximum')` — `combined_rider_annual_maximum` (4500.0 on every tier) appears in no binding. Base `osb_agg_multi_holding.params.max_per_customer` is 2, so a member may hold two riders and reach the branch. Neither seeded world holds a second rider, so no consequence is demonstrable and this is not a red light.

#### F4 — Observation: "in the benefit year" is an empty promise in the settlement compute

- `..._rider_benefit_line_settlement.rule` says "in the benefit year" five times (of `benefit_settled_lines`, `benefit_after_reversals`, `deductible_lines_settled`, `benefit_used`). The corresponding aggregates carry no `benefit_year` filter and no `within_months`, and the evaluator applies **no** automatic period scoping (`check_compute.py` `_within` returns `True` when `within_months is None`). The aggregates therefore span every claim row for that rider for all time. Both seeded worlds carry a single benefit year, so no consequence is demonstrable.

#### F5 — Observation: "settled" is implemented two ways inside one policy

- In `..._rider_benefit_line_settlement.compute`, `benefit_settled_lines` counts `claim_status='paid'` **plus** `claim_status='adjusted'`, while `deductible_lines_settled` counts `claim_status='paid'` only — although the rule uses one word for both: *"only while the rider has settled no line in such a category in the benefit year"*. An adjusted line in a deductible category would be "settled" for the maximum and unsettled for the deductible. Neither world places an adjusted line in a deductible category, so no consequence is demonstrable.

#### F6 — Observation: a dead cross-category binding in the arrears policy

- `..._rider_arrears_settlement.compute` binds `plan_grace_days: CPARAM('advantage','premium_grace_period_days')`, and no later binding in that policy refers to it. Its `compute_basis` entry quotes the sentence about *the rider's own* days of grace, which is implemented by `grace_window_months` from `P('rider_premium_grace_period_days')`. The policy's `cross_category[0].reads` accordingly lists `premium_grace_period_days` as a read the computation never exercises. No scored consequence.

#### F9 — Observation: `months_after_end` names a charge the compute never reads

- `..._rider_closure_settlement.rule`: *"the coverage months beyond the day it ends are instead the coverage months of **the billing cycle last charged** that begin after the month in which that intake reached the plan"*. The compute is `months_after_end: MX(0, cycle_months - 1 - MX(0, MONTHS(cancellation_received, NOW))) …` — it reads no charge row and no billing period, so "the billing cycle last charged" enters the figure through nothing. On task 1 the two readings coincide at 2; they separate whenever the cancellation is older than the current cycle.

#### F12 — Observation: two documented parameters are inert, and both are the tie to the prerequisite record

- `suspend_rider_for_unpaid_premium_a0d6b513(osb_rider_premium_entry_id)` and `end_rider_at_member_request_09efad65(osb_rider_request_id)` are described in `Args:` but never read, stored or echoed by their function bodies. In both cases it is the parameter that would have bound the write to the record its prerequisite turns on (the first unpaid charge; the cancellation intake). This is an observation, not a red light: it weakens nothing about whether the policy entails the answer, and the tools correctly judge no prerequisite (see below).

#### F14 — Observation: docstring ordering words, and banker's rounding

- Every docstring carries generic ordering words ("read … **before** the call", "**Afterwards** the member's record shows …", "still left owing **once** this money is posted"). None names another tool, states a route, or places the action relative to another problem's write, so check 3's substance holds; the letter of "no ordering word" does not.
- `RND` is Python `round` on a binary float — banker's rounding — while every rule says "rounded to the nearest cent". Neither task's figures fall on a `.xx5` boundary, so no consequence is demonstrable here.

#### Tool layer: no prerequisite is judged by a tool — **PASS**

Every one of the seven function bodies was read. There is no `raise`, no `assert`, no error return, no status check, no balance check, no existence check and no hint in any of them; the only two `if` statements are value selections (`cleared` in `pay_rider_premium_by_telephone_9597e982`, `effect` in `post_rider_premium_credit_050a58f6`), neither of which can reject a call. `suspend_rider_for_unpaid_premium_a0d6b513` and `end_rider_at_member_request_09efad65` make no `ctx.find` call at all. The prerequisite decision therefore stays entirely with the agent, which is what the relationship requires.

## closing_checklist

Written after both tasks' reveals. This section is post-reveal by construction and sits below the charter-global section, which remains pre-reveal.

**The difficulty does NOT close.** Four of the eight items below pass; the two relationship items do not.

| Item | Status |
| --- | --- |
| Per-task audit files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them; old revisions traceable | ✅ `0.md`, `1.md`, `_difficulty.md` in `audits/policy_task/optional_rider_benefit_desk/`. First revision, so nothing to preserve. |
| Every comparison section carries a PASS | ❌ `0.md` → `source_gt_comparison` carries SOURCE-POLICY RED + SOURCE-FACTOR RED; `1.md` carries SOURCE-POLICY RED + SOURCE-FACTOR RED. |
| Extended policies fully covered; the two tasks' scopes pairwise disjoint and jointly complete over the whole tree | ✅ 4 + 3 = 7, disjoint, complete (verified against both `charter_scope` blocks). |
| Task tools and GT closed; each tool uses an independently generated, frozen uuid8 | ✅ 7 tools, 7 policies, 7 uuid8s, no reuse and no sign of batch derivation (see `### action_binding_and_uuids`). |
| Every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 problem resolved by an `owner=user` tool, no cycle | ✅ Task 0: n = 3, 2 value_input (floor 2), user write `pay_rider_premium_by_telephone_9597e982`. Task 1: n = 2, 2 value_input (floor 1), user write `end_rider_at_member_request_09efad65`. |
| The `prerequisite` edges of the whole difficulty remain a DAG, with no cycle created by cross-task references | ✅ Two disjoint trees, five edges, no cross-task edge. |
| Every computation declares a self-sufficient baseline and 4–6 factors (≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty); every ladder ≥3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business actually holds; every factor bears weight against an honest baseline, with the baseline alone giving a definite number different from gold | ⚠️ **Partly.** All 34 declared factors across the seven computations **do** bear weight on their own worlds, every baseline is honest in the sense that it matches its policy's `baseline.rule`, every `tier_taken` and every one of the 34 `factor_sensitivity` figures and 7 `baseline_result` figures was reproduced independently, and each whole-baseline figure is definite and differs from gold. **But** F2 leaves eight ladders with two reachable tiers rather than three; F7 declares a cross-difficulty read that is never made; F10 states a tier the business does not have; and F11 leaves one baseline that computes 0.00 on every possible world. |
| This difficulty's instantiation-stage gates re-run on the final form | ✅ All seven re-run at close: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 17 acts / 1.json 13 acts, deterministic, non-vacuous, 0 errors, closure matches initial_state), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Identical to the entry snapshot — nothing was touched by this audit. |

### Verdict across the four relationships

| Relationship | Task 0 | Task 1 |
| --- | --- | --- |
| Policy self-consistency | **SOURCE-POLICY RED** (F1) | **SOURCE-POLICY RED** (F3, F8) |
| The problem tree holds | PASS | PASS |
| Factors bear weight | **SOURCE-FACTOR RED** (F2, F10) | **SOURCE-FACTOR RED** (F2, F7) |
| Policy ↔ task unique solution | Not determinable while F1 stands; the blind derivation matched GT on every item | PASS on the derivation, qualified by F8 |

**This difficulty does not pass the source-layer audit.**

### What the blind derivation establishes, and what it does not

Both tasks were derived independently from the structured policy, `frozen_time`, `user_scenario` and the raw DB, frozen to disk, and only then compared. The blind result reproduced GT **exactly and without exception**: all 7 scored figures (66.50, 45.60, 38.30, 1312.50; 85.80, 73.40, 11.40), every tool argument including the four record ids chosen by rule rather than by convenience (`8e2c41b7-…` as the charge that carried the pre-cover month, `a2f95c60-…` as the oldest unpaid, `f540db99-…` as the first unpaid, `9a1c4e7b-…` as the predetermination), both enum values, the verbatim remittance reference, the end date 2026-09-30, both write orders, both terminal states, both `prerequisite_closure` graphs including the flip-to-true figures, all 34 `tier_taken` strings, all 34 `factor_sensitivity` figures and all 7 `baseline_result` figures.

That the computations are arithmetically sound is therefore established as firmly as this method can establish it. **The four red lights are not arithmetic disagreements** — they are defects in what the policy *entails*: a base sentence that is still in force and says the opposite (F1); two quantities the compute produces that no sentence of the governing rule states (F3, F8); and ladders whose tiers or cross-difficulty claims do not correspond to anything in the seeded world (F2, F7, F10). Every one of them survives a green gate run precisely because the scripts check structure, references and parsability, and none of these is a structural fault.

### Note on scope

The cross-difficulty merge surface and the scenario-level check do not belong to this skill and were not run. `check_traceability` cannot run until the render step publishes the KB. No artifact under `blueprint/`, `tasks/` or `erlbench/` was modified by this audit; the only writes were the three files in this directory.

---

# revision_2 — charter-global re-audit

## charter_global_frozen (revision_2)

- Re-audit time: 2026-09-21. **This is not a blind audit.** Round 1's GT was revealed to this auditor, so revision_2 is a verification pass against the reworked artifacts, not an independent derivation, and is not presented as one. Revision 1 above is untouched.
- Re-derivation rule applied: both charter files moved, so the whole charter-global section is **re-derived in full** rather than carried forward.

| Artifact | revision_1 | revision_2 | |
| --- | --- | --- | --- |
| `osb.extended.yaml` | `c9b6d66de893b951` | `e285d0681d06abb9` | CHANGED |
| `task_tools.py` | `77ec40148512d29a` | `e395ff8ef9847b9b` | CHANGED |
| `_masked_views/0.masked.json` | `355570060acfc704` | `50875defa48de659` | CHANGED |
| `_masked_views/1.masked.json` | `eb975e755e24a52b` | `eb975e755e24a52b` | unchanged |

- Base-copy integrity re-checked first, because a rework is the moment a base copy gets quietly edited: `policies`, `variants`, `events`, `measures`, `parameter_schema`, `lifecycle`, `binding` and `accounts` in `osb.extended.yaml` are each **byte-identical** to `blueprint/products/osb.yaml`. No base sentence was rewritten to make a conflict go away. ✅

### verdict_on_round_1_items

| Item | Reworker's claim | My verdict | Basis |
| --- | --- | --- | --- |
| **F1** | closed | **Closed as a RED; residual observation R2-O1** | The conflict no longer bites any seeded world, but the charter-level hole is not sealed |
| **F2** | closed | **CLOSED — substantively** | `rider_premium_billed_with_plan` now appears in **zero** compute bindings charter-wide |
| **F3** | closed | **CLOSED — substantively** | Rule gained a conversion sentence; compute dropped the `MX(1, …)` floor |
| **F7** | closed | **CLOSED** | `refund_ceiling_basis` deleted; the quantity is unconditional in rule and compute alike |
| **F8** | closed | **CLOSED** | The closure rule now states the whole billing-cycle ladder; its three tiers now differ in outcome |
| **F10** | closed | **CLOSED** | The charge-count tier is gone, binding and all |
| **F4** | fixed | **FIXED (by rule)** | A new sentence licenses the unfiltered aggregate, and the licence is true |
| **F5** | fixed | **FIXED** | "settled" → "paid" in rule and binding name alike |
| **F6** | fixed | **NOT FIXED — REGRESSED** | The dead binding survives, lost its `compute_basis`, and its read is now undeclared |
| **F9** | fixed | **FIXED** | Rule rewritten to what the compute actually does |
| **F11** | fixed | **FIXED** | The baseline no longer computes nothing for every member |
| **F12** | fixed | **COSMETIC ONLY** | Both parameters are referenced solely inside a returned f-string |
| **F14** (ordering words) | fixed | **NOT FIXED** | Ordering words still in all seven docstrings |
| **O2** | fixed | **FIXED** | The unseeded prior-year claim is gone from `design_rationale` |
| **O3** | fixed | **NOT FIXED** | Both treatments of out-of-network liability persist |
| **F13**, **F14** (rounding), **O1**, **O4**, **O5** | declined | **Declines accepted** | Each was an observation with no demonstrable consequence in these worlds; see below |

### policy_conflict_scan (re-derived)

Scope claims are unchanged and still pairwise disjoint and jointly complete: task 0 takes `{benefit_line_settlement, adjusted_line_restatement, rider_arrears_settlement, precover_premium_credit}`, task 1 takes `{closure_settlement, unpaid_premium_suspension_arrears, unbilled_cycle_premium_charge}`; 4 + 3 = 7. ✅

The round-1 conflict (F1) is re-examined in full below. One **new** conflict was found in the prerequisite declarations (R2-F1) and one in the cross-category boundary (R2-F2).

### override_declarations (re-derived)

Four declared overrides, unchanged in number and each still naming its base sentence and merging uniquely: two on `osb_benefit_payment` in the settlement policy, one on `osb_benefit_payment` in the restatement, one on `osb_rider_premium_billing_and_posting` in the unbilled-charge policy. Every base provision not hit by an `overwrite` was re-checked sentence by sentence against the reworked extended text. `osb_agg_combined_rider_maximum`'s combined cap is still a dropped branch (F13, declined — accepted). `osb_premium_suspension_and_recovery` sentence 5 is discussed at R2-O1.

### rule_compute_equivalence (re-derived)

Re-run binding by binding over all seven reworked policies against the evaluator's semantics. The rework added four new `plan_status` branches, and **every one of them is grounded in a real sentence of its own policy's `rule`** — I checked each explicitly rather than trusting the pattern:

- `osb_ext_rider_arrears_settlement`: *"Where that enrollment does not stand in force, it is taken over the bills raised up to the day its coverage ended; where that enrollment stands in force and the rider took effect after it did, …"*
- `osb_ext_precover_premium_credit`: *"Where the medical plan enrollment the rider hangs on stands in force and is billed quarterly, the charge carries three coverage months instead; where that enrollment does not stand in force and a rider premium charge stands …"*
- `osb_ext_unbilled_cycle_premium_charge`: *"Where the medical plan enrollment the rider hangs on stands in force and is billed quarterly, one charge carries three coverage months instead; …"*
- `osb_ext_rider_closure_settlement`: *"Where the medical plan enrollment the rider hangs on stands in force and is billed quarterly, a billing cycle carries three coverage months instead; where that enrollment does not stand in force, it carries the whole calendar months from the day the rider took effect to the handling date, and never fewer than one."*

`compute_basis` coverage is complete for every binding of every policy **with one exception**: `osb_ext_rider_arrears_settlement.plan_grace_days` now has no `compute_basis` entry at all (it had one, quoting an unrelated sentence, in round 1). That is part of F6's regression.

### factor_ladders (re-derived)

| Policy | factors | parameter | method | cross_difficulty |
| --- | --- | --- | --- | --- |
| `..._rider_benefit_line_settlement` | 5 | 3 | 2 | — |
| `..._rider_arrears_settlement` | 6 | 2 | 4 | advantage ×3 |
| `..._precover_premium_credit` | 4 | 2 | 2 | advantage ×2 |
| `..._adjusted_line_restatement` | 5 | 3 | 2 | allowance ×1 |
| `..._unbilled_cycle_premium_charge` | 4 | 2 | 2 | advantage ×2 |
| `..._unpaid_premium_suspension_arrears` | 5 | 2 | 3 | advantage ×1 |
| `..._rider_closure_settlement` | 5 | 2 | 3 | advantage ×2 |

All seven inside the 4–6 bound, all clearing 2-`parameter` / 1-`method`, every ladder at least three tiers, every `decides` an input rather than `result`, binding sets disjoint within each policy. **Every factor's `baseline` now equals its own fall-through tier, and every fall-through is reachable** — the heart of the F2 fix, checked factor by factor rather than in aggregate.

One ladder is not pairwise disjoint as stated: `osb_ext_precover_premium_credit.months_outside_cover` tier 1 (*"the rider took effect after the medical plan enrollment it hangs on took effect"*) and tier 2 (*"the medical plan enrollment the rider hangs on does not stand in force"*) both hold of a rider that took effect after an enrollment that has since terminated. The compute resolves it by order, so no world is ambiguous; recorded as R2-O3.

### closure_evidence_for_each_round_1_red

**F1 — closed as a RED, residual observation R2-O1.** The fix is in the world, not the charter. `osb_benefit_claims["3f607bf2-…"].date_of_service` moved from `2026-09-21` (the morning of the call, while the rider stood suspended) to **`2026-06-12`**. Recomputing when the suspension fell due: the first unpaid charge is `a2f95c60-…` posted `2026-04-01`; the Bundle tier allows 90 days of grace; counted from the day after, grace ran to `2026-06-30`, so the rider stood **active** on 2026-06-12. Base `osb_premium_suspension_and_recovery` sentence 5 — *"services given while it was suspended stay the member's own cost"* — therefore no longer reaches this line, and the second defensible answer of 0.00 is gone. The settlement's prerequisite sentence was also rewritten from *"…on the day the service was given"* to plain *"…stands in force with no rider premium outstanding against it"*, which now restates base sentence 1 (*"it stops paying for services while the arrears stand"*) instead of contradicting sentence 5. Both halves check out.

What is **not** fixed: `osb_ext_rider_benefit_line_settlement.base_policy_refs` still omits `osb_premium_suspension_and_recovery`, and no `overwrite` names sentence 5. The charter would produce the same two answers again for any pended line whose service date fell inside a suspension. No seeded world exercises it, so per the evidence standard it is **not** a red light — recorded as R2-O1.

**F2 — closed substantively.** `P('rider_premium_billed_with_plan')` now appears in **zero** compute bindings across all seven policies (searched exhaustively, not sampled). The vacuous conjunct was replaced by tests on `CFIELD('advantage','status')`, and `advantage_enrollments.status` is a seven-value enum (`enrollment_submitted`, `cms_transaction_pending`, `active`, `premium_grace_period`, `terminated_for_nonpayment`, `disenrolled`, `cancelled_before_effective`) that genuinely varies between customers. Every ladder that carried the dead conjunct now has three reachable tiers, and — the part that matters most — every affected factor's `baseline` moved onto a tier a real customer can occupy:

| Factor | round-1 baseline (unreachable tier) | round-2 baseline (reachable tier) |
| --- | --- | --- |
| `combined_bill_span` | grace-window `XSUM` | every bill raised on that enrollment |
| `plan_bill_cycle_months` | months since the request was received | the single coverage month it is booked to |
| `plan_bill_cycle_length` | months since the rider took effect | the single coverage month it is booked to |
| `months_outside_cover` | `0` | months from the rider taking effect to benefits becoming payable |
| `surplus_carried_to_rider`, `months_met_from_combined_bill`, `bill_money_set_against_closing` | fall-through gated on "billed on its own" | fall-through gated on whether the bill carries money received |

This is a real fix, not a rewording: the round-1 baselines produced treatments no insurer applies (one quarterly charge carrying 8 or 6 coverage months); the round-2 baselines produce the ordinary monthly treatment. Cost: R2-F2 below.

**F3 — closed substantively, on both halves.** (a) The rule gained a sentence that states exactly what the compute does, including the half-open boundary and the zero case: *"The days of grace that govern are reckoned into whole months at thirty days to the month, any part month being dropped, and the span runs back over that many whole calendar months from the handling date, an entry posted in an earlier calendar month falling outside it; where no days of grace govern, the span is empty and no entry falls inside it."* (b) The compute changed behaviour: `grace_window_months: int(governing_grace_days / 30)` — the `MX(1, …)` floor is gone, so the "no days of grace at all" tier now yields `within_months=0`, i.e. `0 ≤ m < 0`, an empty span, exactly as the rule says. Round 1's complaint was that the tier's stated value was unproducible; it is now produced. The sentence is also carried in `baseline.rule`, as required.

**F7 — closed.** `refund_ceiling_basis` is deleted. `refund_ceiling: last_charge_amount` is now unconditional in the compute and matched by an unconditional rule sentence (*"The most that may be refunded is the amount of the rider premium charge carrying the most money of any standing on the account, a credit never exceeding the charge it relieves"*), also present in `baseline.rule`. The replacement factor `billing_cycle_length` decides `cycle_months`, a quantity that genuinely reads `CFIELD('advantage','status')` and `CFIELD('advantage','premium_billing_frequency')` — so its `cross_difficulty: advantage` is now an honest declaration rather than a false one.

**F8 — closed.** The closure rule now carries the whole ladder: *"A billing cycle carries a single coverage month"* (fall-through) and *"Where the medical plan enrollment the rider hangs on stands in force and is billed quarterly, a billing cycle carries three coverage months instead; where that enrollment does not stand in force, it carries the whole calendar months from the day the rider took effect to the handling date, and never fewer than one."* Round 1's second complaint — that two of the three branches both yielded 1 — is also fixed: the branches now yield `3`, `MX(1, MONTHS(rider_effective_date, NOW))` and `1`, three distinct outcomes.

**F10 — closed.** The tier *"no more than one rider premium charge stands on the rider premium account → no credit is due at all"* is gone, and so is the `charges_raised` binding it rested on. The ladder now turns on the rider's own standing (`premium_suspended` → the whole charge; an end date on record → nothing further, what was owed having been settled at closure; otherwise → the charge less credits already posted) — conditions an insurer does weigh when deciding how much of a charge may be relieved.

### findings (revision_2)

#### R2-F1 — `SOURCE-POLICY RED`: the state_gate's `gate` and `effect` now contradict its own `condition` and the world

- **Symptom.** The one `state_gate` edge in the difficulty declares as its gate a base eligibility that is **already satisfied at `frozen_time`**, and asserts an effect the resolving write cannot produce.
- **Root cause.** The F1 rework dropped *"on the day the service was given"* from the prerequisite sentence and from `condition`, and moved the line's service date back three months — but left `gate` and `effect` at their round-1 wording, which are still anchored on the service date.
- **Evidence.** `extended_policies[osb_ext_rider_benefit_line_settlement].prerequisite[0]`:
  - `gate: osb_benefit_payment.rider_in_force_on_service_date`
  - `condition: "The rider carries status active and a rider premium balance due of nothing."` (no service-date anchor)
  - `effect: "The eligibility that the rider stands active on the date of service of the line becomes satisfied, the rider premium balance due having fallen to nothing and the rider having returned to active."`
  - The named gate's own condition, `policies[osb_benefit_payment].eligibility[rider_in_force_on_service_date].condition`, is *"The rider stands at active on the date of service of the line."*
  - `initial_state.osb_benefit_claims["3f607bf2-…"].date_of_service = "2026-06-12"`; the rider's suspension fell due 2026-07-01 (first unpaid charge 2026-04-01 + 90 days of grace counted from the day after = 2026-06-30). **The rider stood active on 2026-06-12.**
- **Demonstrated consequence.** At `frozen_time` the gate named by the edge evaluates **true** while the edge's `condition` evaluates **false** — they are no longer the same test. Worse, `effect` asserts that the eligibility "becomes satisfied" as a result of the payment; it was never unsatisfied, and no write available in this difficulty can alter what the rider's standing was on a past date, so the assertion is false on its own world. Under the rule that a sentence asserting what the world is like is part of the proof, this is a defect of the artifact. A reader who checks the declared gate at the opening finds it holds and concludes there is no prerequisite here at all.
- **Affected artifact and location.** `osb.extended.yaml` → `extended_policies[osb_ext_rider_benefit_line_settlement].prerequisite[0].gate` and `.effect`. Consequence demonstrated against task 0's world in `0.md` → revision_2.
- **Relation to previous revisions.** New in revision_2; introduced by the F1 rework. Round 1's wording was internally consistent because both the sentence and the world were anchored on the same day.

#### R2-F2 — `SOURCE-POLICY RED`: four undeclared cross-category reads

- **Symptom.** Four policies read a field of another category that their own `cross_category.reads` does not declare.
- **Root cause.** The F2 rework introduced `CFIELD('advantage','status')` into four policies and updated the declared reads of only one of them; and the F6 rework narrowed the arrears policy's declared reads without removing the read itself.
- **Evidence.** Actual reads extracted from each `compute` and compared against each `cross_category[].reads`:

| Policy | Undeclared read | Declared reads |
| --- | --- | --- |
| `osb_ext_precover_premium_credit` | `advantage.status` | `coverage_effective_date`, `premium_billing_frequency` |
| `osb_ext_unbilled_cycle_premium_charge` | `advantage.status` | `premium_billing_frequency`, `advantage_premium_ledger.amount`, `.event_type` |
| `osb_ext_rider_closure_settlement` | `advantage.status` | `premium_billing_frequency`, `advantage_premium_ledger.amount`, `.event_type` |
| `osb_ext_rider_arrears_settlement` | `advantage.premium_grace_period_days` | `status`, `coverage_effective_date`, `coverage_end_date`, `advantage_premium_ledger.*` |

  (`osb_ext_rider_arrears_settlement` *does* declare `status` — it is the one policy that was updated, which is what makes the other three an omission rather than a convention.)
- **Demonstrated consequence.** `cross_category.reads` is the policy's declaration of what it may consult in another product, and it is what the render step licenses a reader to look at. `billing_cycle_length`'s tier 1 and tier 2 both turn on whether the medical plan enrollment stands in force, and `advantage.status` appears in no declared read of `osb_ext_rider_closure_settlement` — so the ladder that decides `cycle_months`, and through it `refund_rate` and `months_after_end`, rests on a field the policy never admits to reading. On task 1 that ladder carries 57.20 of a 73.40 basis. The `EXTENDED` gate's `[PASS] cross-category reads declared exactly` is false at field level; it evidently checks the category, not the field.
- **Affected artifact and location.** `osb.extended.yaml` → the `cross_category` blocks of the four policies named above.
- **Relation to previous revisions.** New in revision_2 as to the three `status` reads; the fourth is F6's regression (round 1 had `premium_grace_period_days` declared and unused — it is now undeclared and unused).

#### R2-F3 — F6 not fixed, and regressed on two counts

- **Verdict.** Observation (as in round 1 — no scored consequence), but recorded because it was claimed fixed and is now worse.
- **Evidence.** `osb_ext_rider_arrears_settlement.compute` still opens with `plan_grace_days: CPARAM('advantage','premium_grace_period_days')`. No later binding in that policy refers to it — `grace_window_months` is computed from `int(P('rider_premium_grace_period_days') / 30)`, the rider's own parameter. Beyond surviving, the binding has (a) **lost its `compute_basis` entry** entirely, so it is now the only binding in the charter with no basis at all, and (b) **lost its declaration**, `premium_grace_period_days` having been dropped from that policy's `cross_category[0].reads`. The note on that block still reads *"…and its published days of grace"*, describing a read that decides nothing.

#### R2-F4 — F12 closed cosmetically

- **Verdict.** Observation (unchanged in force from round 1).
- **Evidence.** `suspend_rider_for_unpaid_premium_a0d6b513` body in full: `arrears = round(float(arrears_at_suspension), 2)` then `ctx.update("osb_riders", osb_rider_id, status="premium_suspended", rider_premium_balance_due=arrears)` then a return string that now interpolates `{osb_rider_premium_entry_id}`. Likewise `end_rider_at_member_request_09efad65` now interpolates `{osb_rider_request_id}` into its return. Neither parameter is read from the DB, written to any row, or validated; the **DB effect of both tools is byte-identical to round 1**. The substance of F12 — that the parameter which would bind the write to its prerequisite record binds nothing — is untouched. Naming a value in a confirmation sentence is not using it.

#### R2-F5 — F14 (ordering words) and O3 not fixed

- **F14 ordering words.** All seven docstrings still carry ordering words (`before`, `after`, `afterwards`, `once`, `first`, `then`, `while`, `next`). No docstring names another tool and none states a route — verified: the only occurrences of any tool's uuid8 in the module are the seven `def` lines. So the substance of check 3 still holds and this remains the same observation it was in round 1, but the claim of a fix is not borne out.
- **O3.** `settle_rider_benefit_line_e49937be` still computes `member = round(allowed - paid, 2)`, while `osb_ext_adjusted_line_restatement.compute` still sets `liability_basis: rev_submitted if rev_network=='out_of_network' else …`. On task 0 both apply to out-of-network lines of the same rider on the same call: the settled hearing aid leaves the member 2150.00 − 1312.50 = 837.50 (allowed-based), while the restated frame line leaves her 395.00 − 217.00 − 132.40 (submitted-charge-based). Two treatments of what an out-of-network provider may bill, unchanged. Observation, as in round 1.

#### Accepted declines

- **F13** (combined rider maximum, a dropped branch): still undeclared, still unexercised — neither seeded world holds a second rider, so no consequence is demonstrable. Decline accepted.
- **F14** (banker's rounding): re-checked against all 7 scored figures and all 34 factor baselines; none falls on a `.xx5` boundary. Decline accepted.
- **O1** (`balance_effect` decided by prose, not arithmetic): unchanged, and the policy does entail `settles_balance` via *"The money a member is asked for **to clear** the rider premium they owe…"*. Decline accepted.
- **O4** (suspension recorded as a step on a voluntary cancellation) and **O5** (the 4.80 treated two ways): unchanged; both were recorded as passing every formal test. Declines accepted.

#### R2-O1 — residual: the F1 hole is avoided, not sealed

See the F1 paragraph above. The settlement policy still does not list `osb_premium_suspension_and_recovery` among its `base_policy_refs` and no `overwrite` names its sentence 5, so the charter still admits the round-1 contradiction for any pended line serviced during a suspension. Unexercised by both seeded worlds, therefore an observation rather than a red light.

#### R2-O2 — two stale `cross_category` notes

`osb_ext_rider_closure_settlement.cross_category[0].note` still reads *"Decides the **refund-ceiling factor** from the medical plan enrollment's billing frequency…"* — but `refund_ceiling_basis` was deleted in this rework and `refund_ceiling` is no longer a factored quantity at all. `osb_ext_rider_arrears_settlement.cross_category[0].note` still reads *"…and its published days of grace"*, describing the dead `plan_grace_days` binding. Both notes now describe the charter as it was, not as it is.

#### R2-O3 — one ladder not pairwise disjoint as stated

`osb_ext_precover_premium_credit.months_outside_cover`: tier 1 *"the rider took effect after the medical plan enrollment it hangs on took effect"* and tier 2 *"the medical plan enrollment the rider hangs on does not stand in force"* both hold of a rider that took effect after an enrollment which has since terminated. The compute resolves by evaluation order, so no world is ambiguous and no figure is at risk; but the tiers are not disjoint as written.

#### R2-O4 — a latent crash on the new `coverage_end_date` read

`osb_ext_rider_arrears_settlement.compute.plan_paid` and `.plan_charged` evaluate `MX(1, MONTHS(CFIELD('advantage','coverage_end_date'), NOW))` on the `plan_status != 'active'` branch. `MONTHS` parses with `int()` and raises `ValueError` on `''`. An enrollment in `premium_grace_period`, `cms_transaction_pending` or `enrollment_submitted` is not `active` and would ordinarily carry an empty `coverage_end_date`, so that branch raises rather than computing. Python's conditional is lazy and both seeded enrollments are `active`, so neither world reaches it. Unexercised, hence an observation.

#### R2-O5 — the new in-force tiers are unexercised in this difficulty

`advantage_enrollments.status` is `active` in **both** seeded worlds, so every tier the F2 fix introduced on the "does not stand in force" side is reachable in principle but taken by no customer in this difficulty. That is not a defect — a fall-through must be reachable, not exercised — but it means the fix's new discriminating condition is not itself tested by either task.

## closing_checklist (revision_2)

Written after both tasks' revision_2 sections. **The difficulty still does not close**, on narrower grounds than round 1.

| Item | Status |
| --- | --- |
| Per-task files one-to-one with tasks; old revisions traceable | ✅ `0.md`, `1.md`, `_difficulty.md`; revision_1 preserved verbatim, revision_2 appended below it in each |
| Every comparison section carries a PASS | ❌ Both tasks carry SOURCE-POLICY RED (task 0: R2-F1, R2-F2; task 1: R2-F2) |
| Extended policies fully covered; scopes pairwise disjoint and jointly complete | ✅ 4 + 3 = 7, unchanged |
| Task tools and GT closed; independently generated, frozen uuid8s | ✅ Same 7 uuid8s, unchanged and unreused |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle | ✅ Task 0: n=3, 2 value_input, user payment. Task 1: n=2, 2 value_input, user ending |
| Difficulty-wide `prerequisite` graph still a DAG | ✅ Two disjoint trees, five edges, no cross-task edge |
| Baselines self-sufficient; 4–6 factors; ladders ≥3 distinct, reachable tiers; every factor bears weight | ✅ **Now passing.** All 34 factors bear weight; every baseline sits on a reachable fall-through; every whole-baseline figure is definite and differs from gold |
| Instantiation gates re-run on the final form | ✅ Coordinator's re-run: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK |

### Verdict across the four relationships

| Relationship | Task 0 | Task 1 |
| --- | --- | --- |
| Policy self-consistency | **SOURCE-POLICY RED** (R2-F1, R2-F2) | **SOURCE-POLICY RED** (R2-F2) |
| The problem tree holds | PASS | PASS |
| Factors bear weight | **PASS** (was RED) | **PASS** (was RED) |
| Policy ↔ task unique solution | **PASS** (was not determinable) | **PASS, unqualified** (was qualified) |

### What the rework achieved, and what it cost

All six round-1 red lights are **genuinely closed**, and in five of the six the fix is substantive rather than verbal — a rule gained a sentence that states what the compute does (F3, F8), a factor was deleted along with the quantity it falsely claimed (F7), a tier and its binding were removed (F10), a dead tier parameter was replaced throughout by a field that genuinely varies (F2). F1 alone is closed by moving the world rather than by sealing the charter, which is why R2-O1 records the hole as still open in principle.

Arithmetic held throughout: all 7 scored figures, all 34 `factor_sensitivity` figures and all 7 `baseline_result` figures were recomputed and reproduce exactly. Seven baselines moved, every one of them because its factor's fall-through moved onto a reachable tier, and each was recomputed from the new ladder rather than accepted. The two seed edits in task 0 are both load-bearing and both correct: the service date moves the line out of the suspension window (F1), and the 280.00 plan payment keeps `combined_bill_span` bearing weight once its baseline became the unwindowed sum.

The cost is two new defects, both of the same kind — **declarations left behind by a fix**. R2-F1: the F1 rework dropped the service-date anchor from a prerequisite's sentence and condition but left `gate` and `effect` anchored on it, so the edge now names an eligibility that is already true at the opening and asserts a change that never occurs. R2-F2: the F2 rework introduced `CFIELD('advantage','status')` into four policies and updated the declared cross-category reads of only one. Three claimed fixes are also not fixes: F6 survives and regressed on two counts, F12 is cosmetic (a parameter echoed in a return string is not a parameter used), and F14's ordering words and O3's two liability treatments are untouched. The five declines are all accepted.

**This difficulty does not pass the source-layer audit.** The factor relationship and the unique-solution relationship are repaired; policy self-consistency fails on new grounds.

---

# revision_3 — charter-global re-audit

## charter_global_frozen (revision_3)

- Re-audit time: 2026-09-21. **Not blind.** This GT has been revealed to this auditor since round 1; revision_3 is a verification pass and is not presented as an independent derivation. Revisions 1 and 2 are untouched.
- Re-derivation rule: both charter files moved, so the charter-global section is re-derived in full.

| Artifact | round 2 | round 3 | |
| --- | --- | --- | --- |
| `osb.extended.yaml` | `e285d0681d06abb9` | `7bf7236e46010815` | CHANGED |
| `task_tools.py` | `e395ff8ef9847b9b` | `98fbab8766bafd1a` | CHANGED |
| `_masked_views/0.masked.json` | `50875defa48de659` | `50875defa48de659` | unchanged |
| `_masked_views/1.masked.json` | `eb975e755e24a52b` | `eb975e755e24a52b` | unchanged |

Both worlds are byte-identical to round 2, so every figure I recomputed in revision_2 carries forward unchanged; what moved is the charter, the tools and the task files' non-world sections. `replay_tasks.py` was **not** run during this audit, per the coordinator's note that it rebuilds `db_closure` from a set iteration and is byte-unstable; the hashes above stayed pinned throughout.

## THE RULING ASKED FOR — F12's remainder

**Question.** Does the inert `osb_rider_premium_entry_id` parameter on `suspend_rider_for_unpaid_premium_a0d6b513` move any scored value, any GT, or the unique solution of either task?

**Ruling: NO. It moves nothing. Recorded as a known base issue; it is an accepted cost, not a blocker.**

I verified the reworker's framing before accepting it, rather than taking it as established.

**Premise 1 — base really does mandate the parameter. TRUE.** `policies[osb_premium_suspension_and_recovery].eligibility[rider_grace_period_exhausted]` (kind `time`) carries:

```
correlation_keys: [["osb_riders.osb_rider_id", "osb_rider_premium_ledger.osb_rider_premium_entry_id"]]
action_bindings : {"osb_riders.osb_rider_id": "osb_rider_id",
                   "osb_rider_premium_ledger.osb_rider_premium_entry_id": "osb_rider_premium_entry_id"}
```

The correlation pairs the rider with a ledger entry and the action must bind both, so the tool is obliged to take the parameter. The obligation is genuine.

**Premise 2 — no field can hold it. TRUE, on both halves.**
- `osb_riders` has 15 columns and none can carry a ledger reference: `linked_plan_reference` means the medical plan enrollment, `network_provider_reference` is a 10-digit NPI, and the rest are dates, amounts, enums and names.
- `osb_rider_premium_ledger.event_type` is a **closed enum of exactly three values** — `osb_rider_premium_charge`, `osb_rider_premium_payment`, `osb_rider_premium_credit`. There is no suspension member, so no ledger row can record a suspension at all; and `source_premium_entry_id` is defined in the schema as *"the rider premium charge a credit relieves; empty on charges and payments"*, i.e. it exists only for credits.

So a non-cosmetic consumption would need either a new `osb_riders` column or a new `event_type` enum member. Both are base edits. **The remedy really would require a base edit, so it is a base defect.** The framing is verified, not merely accepted.

**Now the correctness question, which is decided on three independent grounds.**

1. **Scoring cannot see it.** `erlbench/scoring.py` scores by database hash — *"seeded DB and compare the resulting database hashes"*, `score()` returning `target_hash` / `predicted_hash` from `engine.db.hash()`. A tool argument reaches the score **only** through the DB writes it produces. The whole body of `suspend_rider_for_unpaid_premium_a0d6b513` is `ctx.update("osb_riders", osb_rider_id, status="premium_suspended", rider_premium_balance_due=arrears)`; the parameter is referenced nowhere but the returned confirmation sentence. No reachable DB state depends on it, so it **cannot** move the score.
2. **No computation consumes it.** `arrears_at_suspension` is produced by `osb_ext_unpaid_premium_suspension_arrears`, whose every binding reads either a `SUM`/`MX` aggregate over the whole ledger or an `F(...)` field of the rider — never a caller-supplied entry id. Substituting any other entry id leaves task 1's three figures (85.80, 73.40, 11.40), all 14 of its factor sensitivities and both of its terminal states untouched.
3. **It does not threaten the unique solution, because its correct value is uniquely entailed anyway.** The docstring fixes it as *"the reference number of the first rider premium charge that went unpaid on that rider"*, and base `rider_grace_period_exhausted` independently anchors the grace period on *"the day the plan posted the first unpaid rider premium charge"*. On task 1's world exactly one entry answers that: `f540db99-…`, the 2026-06-01 charge of 85.80 against which only 18.40 + 12.40 = 30.80 of credits stand, the 2026-03-01 charge having been settled in full by the 2026-03-08 payment of 85.80. It is reachable at runtime through `find_osb_rider_premium_ledger`. There is therefore neither ambiguity nor an unreachable requirement.

Task 0 never calls this tool, so it is untouched there.

**Consequence of the ruling.** This difficulty's scope does **not** sit on a bad clause in any way that bites. No routing-around is required, and I am not designing one. The honest characterisation of the residual cost is narrow: the parameter is not useless to the task — it still obliges the agent to identify the first unpaid charge from the ledger, which is a real derivation, and the tool reports it back in its confirmation — it is simply **an argument the harness cannot verify**. That is a defect of frozen base, not of this difficulty, and it stands.

## verdict_on_round_2_items

| Item | Claim | My verdict | Basis |
| --- | --- | --- | --- |
| **R2-F1** | closed | **PARTLY — new finding R3-F1** | The edge is correctly re-anchored, but the same false claim survives in two further declarations |
| **R2-F2** | closed | **CLOSED** | My own field-level sweep: 0 undeclared reads, 0 declared-but-unread, all 7 policies |
| **F6 / R2-F3** | closed | **CLOSED** | `plan_grace_days` gone from the arrears policy; 0 never-used bindings charter-wide; every binding has a `compute_basis` |
| **F14 / O3 / R2-F5** | closed | **F14 CLOSED; O3 not** | Zero ordering words in all seven docstrings; O3's two liability treatments are mechanically unchanged |
| **R2-O1** | closed | **CLOSED** | `osb_premium_suspension_and_recovery` added to `base_policy_refs` with a declared `overwrite` |
| **R2-O2** | closed | **CLOSED** | Both stale notes rewritten to name the factors that actually exist |
| **R2-O3** | closed | **CLOSED** | `months_outside_cover` tier 2 gained a "no later than" conjunct, making the ladder disjoint |
| **R2-O4** | closed | **CLOSED** | The guard now excludes an empty `coverage_end_date` |
| **F12 / R2-F4** | partly, remainder declined | **Half closed; remainder ruled harmless** | See the ruling above |
| **R2-O5** | declined | **Decline accepted** | Both enrollments still `active`; a fall-through must be reachable, not exercised |

### closure_evidence

**R2-F2 — closed, verified by my own sweep rather than theirs.** I extracted every `CFIELD`/`CPARAM`/`XSUM`/`XCOUNT`/`XMAX`/`XLATEST` call from all seven `compute` blocks and compared the field set against each policy's `cross_category[].reads`. Result: **0 undeclared reads and 0 declared-but-unread fields**, across 17 cross-category reads in six policies. The round-2 problems are gone one by one: `advantage.status` is now declared in `osb_ext_precover_premium_credit`, `osb_ext_unbilled_cycle_premium_charge` and `osb_ext_rider_closure_settlement`; and the fourth case was indeed closed by **removing the read** — `plan_grace_days` no longer appears in `osb_ext_rider_arrears_settlement` at all, which is why `premium_grace_period_days` is correctly absent from that policy's declaration. `CPARAM('advantage','premium_grace_period_days')` survives only in `osb_ext_unpaid_premium_suspension_arrears`, where `governing_grace_days` genuinely consumes it and where it is declared.

**F6 / R2-F3 — closed.** The dead binding is gone, and the stronger property now holds charter-wide: every binding of every policy is consumed by a later binding, and every binding has a `compute_basis` entry. Round 2's "only binding in the charter with no basis at all" no longer exists.

**R2-O1 — closed properly, in the charter rather than the world.** `osb_ext_rider_benefit_line_settlement.base_policy_refs` now includes `osb_premium_suspension_and_recovery`, and a third `overwrite` names the offending clause:

```
base_policy: osb_premium_suspension_and_recovery
superseded_clause: services given while it was suspended stay the member's own cost
replaced_by: A benefit is not settled on a submitted line until the rider it is claimed under
             stands in force with no rider premium outstanding against it.
```

This is the seal round 2 found missing. The round-1 contradiction can no longer arise for any world, not merely for the two seeded ones — a clause-level override, properly declared, with unique merged semantics.

**R2-O2 — closed.** `osb_ext_rider_closure_settlement`'s note now reads *"Decides the billing-cycle-length factor from whether the medical plan enrollment the rider hangs on stands in force and how often it is billed…"*, naming the factor that exists instead of the deleted `refund_ceiling_basis`; `osb_ext_rider_arrears_settlement`'s now reads *"…from whether the medical plan enrollment the rider hangs on stands in force and when its coverage began and ended"*, with the dead "published days of grace" gone.

**R2-O3 — closed.** `months_outside_cover` tier 2 is now *"the rider took effect **no later than** the medical plan enrollment it hangs on did and that enrollment does not stand in force"*. The added conjunct makes it disjoint from tier 1 as stated, so the ladder no longer relies on evaluation order.

**R2-O4 — closed.** The guard is now `if (plan_status!='active' and CFIELD('advantage','coverage_end_date')!='')`, so `MONTHS('', NOW)` — which would raise `ValueError` in the evaluator — is unreachable by construction rather than by lazy evaluation.

**F14 — closed.** All seven docstrings now carry **zero** ordering words (`before`, `after`, `afterwards`, `once`, `first`, `then`, `until`, `next`, `subsequently`). Re-confirmed alongside it that the tool layer still judges no prerequisite: no `raise`, no `assert`, no error return anywhere in the module.

**F12, the half that was closed.** `end_rider_at_member_request_09efad65` now genuinely consumes `osb_rider_request_id`: it writes `ctx.update("osb_rider_requests", osb_rider_request_id, intake_status="completed", …)`. That is a real DB effect, not an echo, and it is business-correct — base `osb_termination_and_cancellation` requires the intake to stand at `recorded`, `awaiting_member_signature` or `under_review` *before* the write, and closing it to `completed` afterwards is the natural terminal state. It does not disturb task 1's figures: the closure compute selects the intake by `request_action='rider_cancellation'`, not by `intake_status`.

**O3 — not closed.** `settle_rider_benefit_line_e49937be` still computes `member = round(allowed - paid, 2)` while `osb_ext_adjusted_line_restatement.liability_basis` still resolves to `rev_submitted` on an out-of-network line. The two treatments of what an out-of-network provider may bill are mechanically unchanged. This has been an observation since round 1 with no demonstrable consequence, and it remains exactly that — but the claim of closure is not borne out.

### findings (revision_3)

#### R3-F1 — `SOURCE-POLICY RED`: R2-F1's false claim survives in two further declarations

- **Verdict.** R2-F1 is **partly** closed. The declaration it was raised against was fixed; two others making the identical false assertion were not.
- **Symptom.** Two base eligibilities anchored on the **date of service** are declared to be false at the opening and established by the member's telephone payment. Both are in fact true at the opening, and the payment cannot affect either.
- **Root cause.** The same pattern that produced R2-F1 and R2-F2: a fix changed one declaration and left the others that pointed at it. The reworker's sweep found the problem-tree card and stopped there.
- **What *was* fixed, and correctly.** `extended_policies[osb_ext_rider_benefit_line_settlement].prerequisite[0]` now reads `gate: osb_riders.status`, with `effect: "The rider's own record moves from premium_suspended to active and the rider premium balance due standing on it falls to nothing…"`. That gate is genuinely false at the opening (`status = "premium_suspended"`, `rider_premium_balance_due = 219.0`) and genuinely true after the payment. `prerequisite_closure` in `tasks/0.json` matches it exactly — same `gate`, same `condition`, same `policy_source` — and its `why_false` and `flips_to_true_by` are both re-anchored on the record state. The pre-fix sentence appears nowhere as a live quotation: 0 occurrences in the charter, in `task_tools.py` and in `tasks/1.json`, and the single occurrence in `tasks/0.json` is narrative *about* the rework, not an assertion of the current form.
- **Evidence for what was missed.** Two places still assert the round-2 claim:
  1. `tasks/0.json` → `design_rationale`, base-invariant card for the settlement write: *"Gate **rider_in_force_on_service_date**, kind state: **false at the opening and true at handling time, established by the member's payment at action 12**. Gate **rider_in_force_for_coordination**, kind state, allowed set active or waiting_period: **likewise established at action 12**."*
  2. `tasks/0.json` → `solvability_contract.gold_actions[3].base_preconditions`: both `rider_in_force_on_service_date` and `rider_in_force_for_coordination` carry `"prior_step:12"` in their `evidence` lists — the same causal claim in structured form.
- **Why the claim is false.** Both eligibilities are anchored on the date of service, verbatim from base: `rider_in_force_on_service_date` is *"The rider stands at active on the date of service of the line"*, and `rider_in_force_for_coordination` is *"The rider held is in force on the date of service of the line the medical plan is paying"*. On task 0's world `osb_benefit_claims["3f607bf2-…"].date_of_service = "2026-06-12"`, and the rider stood **active** from 2026-02-01 until the grace period on the 2026-04-01 charge expired on 2026-06-30. Both eligibilities therefore held at the opening, and no write available in this difficulty can alter the rider's standing on a past date.
- **The contradiction is internal to one field.** The same `design_rationale` states elsewhere: *"the grace period on the rider ran out on 2026-06-30, which is why the standing is premium_suspended and not active"*. Taken with `date_of_service = 2026-06-12`, that sentence entails the rider was active on the date of service — which is the opposite of what the base-invariant card asserts four paragraphs away. No external recomputation is needed to see it.
- **Demonstrated consequence.** Under the rule that a sentence asserting what the world is like is part of the proof, both declarations are false on their own world. Their practical effect is the one R2-F1 named: a reader who checks the eligibilities the artifact says the payment establishes finds them already satisfied, and concludes the settlement has no premium prerequisite. The prerequisite's real force now rests solely on the re-anchored `prerequisite[0]` and on the rule sentence; `design_rationale` and `solvability_contract` both misdescribe it.
- **Affected artifact and location.** `env/env_0006_medicare_advantage_plan_sponsor/tasks/optional_rider_benefit_desk/tasks/0.json` → `design_rationale` (base-invariant card for the settlement write) and `solvability_contract.gold_actions[3].base_preconditions[0].evidence` / `[2].evidence`. Demonstrated against task 0's world in `0.md` → revision_3.
- **Relation to previous revisions.** Direct continuation of R2-F1 (revision_2), itself a continuation of F1 (revision_1). Third consecutive round in which a fix has left a declaration behind — the first two rounds in the charter, this one in the task file's proof fields.

#### R3-O1 — Observation: the re-anchored gate names one field of a two-field condition

`prerequisite[0].gate` is now `osb_riders.status`, while its `condition` tests two fields — *"The rider carries status active **and a rider premium balance due of nothing**"*. The balance lives on `osb_riders.rider_premium_balance_due`, which the gate does not name. Both are on the same row and the `effect` describes both, so nothing is ambiguous and no figure is at risk; the designation is simply partial. Noted also because `gate` has changed category between rounds — round 2 named a base eligibility id, round 3 names a record field — and only the latter is checkable against a row.

#### Carried forward unchanged

- **F13** (combined rider maximum, a dropped branch), **F14 rounding** (banker's rounding; no figure on a `.xx5` boundary), **O1** (`balance_effect` decided by prose), **O4** (suspension recorded as a step on a voluntary cancellation), **O5** (the 4.80 treated two ways), **R2-O5** (both enrollments `active`, so the new in-force tiers are unexercised): all re-checked, all unchanged, all still observations with no demonstrable consequence. Declines accepted.
- **O3**: unchanged in mechanism; see above.

## closing_checklist (revision_3)

| Item | Status |
| --- | --- |
| Per-task files one-to-one; old revisions traceable | ✅ revisions 1, 2 and 3 appended in order, none rewritten |
| Every comparison section carries a PASS | ❌ Task 0 carries SOURCE-POLICY RED (R3-F1); task 1 is clean |
| Extended policies covered; scopes disjoint and complete | ✅ 4 + 3 = 7, confirmed against both `charter_scope` blocks |
| Task tools and GT closed; independent, frozen uuid8s | ✅ same 7 uuid8s, unchanged and unreused |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle | ✅ unchanged from revision_2 |
| Difficulty-wide `prerequisite` graph a DAG | ✅ two disjoint trees, five edges |
| Baselines self-sufficient; 4–6 factors; ladders ≥3 distinct reachable tiers; every factor bears weight | ✅ all 34 factors; figures identical to revision_2, where each was recomputed |
| Instantiation gates re-run | ✅ coordinator's run: all seven OK (`replay_tasks.py` deliberately not re-run here) |

### Verdict across the four relationships

| Relationship | Task 0 | Task 1 |
| --- | --- | --- |
| Policy self-consistency | **SOURCE-POLICY RED** (R3-F1) | **PASS** |
| The problem tree holds | PASS | PASS |
| Factors bear weight | PASS | PASS |
| Policy ↔ task unique solution | PASS | PASS |

**Task 1 passes all four relationships outright.** Task 0 fails one, on two proof-field declarations.

### Trajectory across the three rounds

| | round 1 | round 2 | round 3 |
| --- | --- | --- | --- |
| REDs open | 4 (F1, F2, F3, F7, F8, F10 across two tasks) | 2 (R2-F1, R2-F2) | 1 (R3-F1) |
| Tasks failing ≥1 relationship | 2 of 2 | 2 of 2 | 1 of 2 |
| Relationships failing | policy self-consistency, factors, uniqueness | policy self-consistency | policy self-consistency |

Every round-2 red light is closed on the merits, and all six round-1 red lights remain closed — I re-checked each rather than assuming it. The rework is converging: the charter itself is now clean on every test I can apply to it, the seal R2-O1 asked for was made properly in the charter rather than by arranging the world, and seven observations were closed along the way. What remains is a single instance of the one failure mode that has recurred in all three rounds — **a fix that moved a declaration without moving everything that pointed at it** — and it now sits in `tasks/0.json`'s proof fields rather than in the charter.

The F12 question the coordinator posed is answered separately above: the inert parameter moves nothing, the remedy genuinely would require a base edit, and it is an accepted cost rather than a blocker.

**This difficulty does not pass the source-layer audit**, on R3-F1 alone.

---

# revision_4 — charter-global carry-forward and closing

## charter_global_frozen (revision_4)

- Re-audit time: 2026-09-21. **Not blind** — this GT has been revealed since round 1. Verification pass. Revisions 1–3 untouched.

**The charter-global section is carried forward by reference, not re-derived.** My carry-forward rule is that a charter-global section is re-derived only when its shared inputs can have moved it. Both shared inputs are byte-identical to round 3:

| Artifact | round 3 | round 4 | |
| --- | --- | --- | --- |
| `osb.extended.yaml` | `7bf7236e46010815` | `7bf7236e46010815` | **unchanged** |
| `task_tools.py` | `98fbab8766bafd1a` | `98fbab8766bafd1a` | **unchanged** |
| `_masked_views/0.masked.json` | `50875defa48de659` | `50875defa48de659` | **unchanged** |
| `_masked_views/1.masked.json` | `eb975e755e24a52b` | `eb975e755e24a52b` | **unchanged** |

I verified these on disk myself rather than taking them from the brief. On those two charter hashes, every conclusion of `# revision_3` → `## charter_global_frozen` through `### closure_evidence` stands unchanged and is **cited, not re-derived**: the policy conflict scan, `rule_compute_equivalence`, `action_binding_and_uuids`, `prerequisite_graph`, `prerequisite_sentences`, `override_declarations` and `factor_ladders`. The base copy is still byte-identical to `blueprint/products/osb.yaml` (independently confirmed by the coordinator; the charter hash not having moved is itself sufficient). `replay_tasks.py` was again not run, keeping the hashes pinned.

Only the proof fields inside `tasks/0.json` and `tasks/1.json` moved. The per-task sections are judged against their own task files in `0.md` and `1.md` → `# revision_4`.

## verdict_on_round_3_items

| Item | Claim | My verdict |
| --- | --- | --- |
| **R3-F1** | closed | **CLOSED** — all three sites verified, and my own independent sweep finds no fourth |
| **O3** | explicitly not claimed | Correct; remains the observation it has been since round 1 |
| **F12** | untouched, settled on my ruling | Correct; the charter and tool hashes confirm nothing moved |

### R3-F1 — closed, verified site by site

The two sites I named in revision_3 are fixed, and fixed on the merits rather than by deletion:

1. **`design_rationale`, base-invariant card.** Now reads: *"Gate rider_in_force_on_service_date, kind state: its condition is anchored on the date of service of the line, and the aid was fitted on 2026-06-12, when the rider still stood in force — the ninety days of grace on the unpaid April charge ran to 2026-06-30, so no suspension had arisen by then — and the gate therefore holds at the opening, on the record as it stands. **No gold action establishes it.** Gate rider_in_force_for_coordination … anchored on the same date of service and holding at the opening for the same reason. **Neither of these is what the member's payment answers.** What the payment answers is this settlement policy's own prerequisite sentence, whose gate is `osb_riders.status` — the rider's standing now, not its standing on the date of service."* That is the correct account, and it is the account I reached independently in revision_3.
2. **`solvability_contract.gold_actions[3].base_preconditions`.** `prior_step:12` is gone from both eligibilities, from the evidence list and from the correlation binding alike. `evidence_bindings` now resolves `osb_riders.osb_rider_id` from `initial_state`, and the evidence lists name `osb_riders.status`, `osb_benefit_claims.…date_of_service` and `osb_rider_premium_ledger.a2f95c60-….posted_date` — precisely the three facts a reader needs to check whether the rider stood active on the date of service. Both carry `satisfied: true`, which is the true value.

### The third site, and whether the edge is still load-bearing

The reworker's own sweep found a site I had not named — `prerequisite_closure.edge_load_bearing[0].skipped_effect` — and flagged that it had made the edge *look* load-bearing for the wrong reason. That is a real and material catch, and the fix is sound:

> *"Skipping the member's payment leaves `osb_riders.status` at premium_suspended and `osb_riders.rider_premium_balance_due` at 152.50 in the terminal state instead of active and 0.0, so the terminal hash differs on two fields of the rider record and the `osb_rider_premium_ledger` row for the telephone payment is absent altogether. The benefit on the line is then settled while the rider still stands premium_suspended with rider premium outstanding against it, which this settlement policy's own prerequisite sentence does not permit. **The base gate anchored on the date of service is untouched by the skip: the aid was fitted on 2026-06-12, when the rider stood in force, so that gate holds either way.**"*

**Verified: the edge genuinely remains load-bearing, and on the ground now stated.**

- The arithmetic checks: the opening `rider_premium_balance_due` is 219.00; `post_rider_premium_credit_050a58f6` decrements it by the 66.50 credit at step 10, leaving **152.50**; skipping the payment leaves it there, against 0.00 and `status="active"` when the payment runs.
- Scoring compares database hashes (`erlbench/scoring.py`), so a terminal state differing on two `osb_riders` fields **plus** an entirely absent `osb_rider_premium_ledger` row necessarily produces a different hash. The edge bears weight on the terminal state — which is what a `state_gate` is for, and what I recorded in revision_1 before any of this was contested.
- The ground is true rather than merely different: the old claim (the service-date gate failing) was false because that gate holds either way, and the new text says so explicitly instead of quietly dropping it.

The terminal-hash half was already correct in round 3 and is unchanged, so nothing regressed in closing this.

### The sweep gap, and whether it is covered

The reworker recorded that its round-3 sweep swept the **charter** for declarations naming what it had just edited, which structurally cannot find a restatement of the same fact in a **different artifact**. That diagnosis is fair, and it explains all three rounds of this failure mode.

**I verified the replacement sweep independently rather than trusting it.** I ran my own: a regex over *every string value at every path* in both task JSONs, matching on assertion type — `prior_step`, `establish*`, `becomes satisfied`, `flips to true`, `false at the opening`, `true at handling`, `at action N`, `unmet at`, `made true by`, `answered by` — and read every hit against the dates on the record. That sweeps by *what is being asserted* across *all* artifacts, which is exactly the gap the old sweep left. Result:

- The three sites above are fixed.
- **No fourth site exists.** Every remaining hit is either narrative about the rework, an `argument_uniqueness_tracing` entry citing which read-action returned a value (honest and unrelated), or one of the three `prior_step` provenances below.
- **All three surviving `prior_step` references are honest**, checked one by one against the world:
  - task 0, `gold_actions[1]` (the payment) cites `prior_step:10` — the payment's 38.30 does depend on the 66.50 credit posted at step 10. True.
  - task 0, `gold_actions[3]` (the settlement) cites `prior_step:12` with the fact *"The rider stands in force with no rider premium outstanding against it, which is what the member's own telephone payment brought about earlier in this call."* True — and note it is now framed on `osb_riders.status`, the standing **now**, not on either service-date gate. This is the one place a `prior_step:12` claim is correct, and it is correctly confined to it.
  - task 1, `gold_actions[1]` (the suspension) cites `prior_step:8` — the charge raised at step 8 is what makes every billing cycle carry a charge. True.

### Regression check

- **All seven scored figures unchanged**, re-read off disk: 66.5 / 38.3 / 45.6 / 1312.5 (task 0) and 85.8 / 73.4 / 11.4 (task 1). All seven whole-baseline figures unchanged: 0.0 / 118.0 / 310.0 / 0.0 and 0.0 / 132.2 / 140.8. All 34 factor counts unchanged (4+6+5+5 and 4+5+5). Every tool argument unchanged.
- **Frozen times and worlds unchanged**: `2026-09-21 10:40:00 EDT` and `2026-09-18 14:20:00 EDT`; both `initial_state` and both `user_scenario` blocks hash identically to round 3, as the unchanged masked-view hashes already imply.
- **Scopes unchanged** and still disjoint and complete: 4 + 3 = 7.
- **Task 1 still passes all four relationships**, as it did in round 3 — nothing in its file moved except proof text, and its one `prior_step` provenance verifies honest.

## closing_checklist (revision_4)

| Item | Status |
| --- | --- |
| Per-task files one-to-one; old revisions traceable | ✅ revisions 1–4 appended in order, none rewritten |
| Every comparison section carries a PASS | ✅ **both tasks now PASS** |
| Extended policies covered; scopes disjoint and complete | ✅ 4 + 3 = 7 |
| Task tools and GT closed; independent, frozen uuid8s | ✅ unchanged (tool hash unmoved) |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle | ✅ unchanged; all five edges verified load-bearing, edge 0 now on a true ground |
| Difficulty-wide `prerequisite` graph a DAG | ✅ two disjoint trees, five edges |
| Baselines self-sufficient; 4–6 factors; ladders ≥3 distinct reachable tiers; every factor bears weight | ✅ all 34; figures identical to revision_2, where each was recomputed |
| Instantiation gates re-run | ✅ coordinator's run: all seven OK (`replay_tasks.py` deliberately skipped here) |

### Final verdict across the four relationships

| Relationship | Task 0 | Task 1 |
| --- | --- | --- |
| Policy self-consistency | **PASS** | **PASS** |
| The problem tree holds | **PASS** | **PASS** |
| Factors bear weight | **PASS** | **PASS** |
| Policy ↔ task unique solution | **PASS** | **PASS** |

# THIS DIFFICULTY PASSES THE SOURCE-LAYER AUDIT.

One known issue stands, on the record and by ruling rather than by oversight: **F12's remainder**, the inert `osb_rider_premium_entry_id` on `suspend_rider_for_unpaid_premium_a0d6b513`. It is a defect of frozen base — base `rider_grace_period_exhausted` mandates the parameter while no `osb_riders` column can hold a ledger reference and `osb_rider_premium_ledger.event_type` is a closed three-value enum with no suspension member — and I ruled in revision_3 that it moves no scored value, no GT figure and no unique solution. It is an accepted cost, not a blocker.

### Trajectory across the four rounds

| | round 1 | round 2 | round 3 | round 4 |
| --- | --- | --- | --- | --- |
| REDs open | 4 | 2 | 1 | **0** |
| Tasks failing ≥1 relationship | 2 of 2 | 2 of 2 | 1 of 2 | **0 of 2** |
| Relationships failing | self-consistency, factors, uniqueness | self-consistency | self-consistency | **none** |

Every red light raised in four rounds is closed on the merits, and I re-checked each rather than assuming it stayed closed. The recurring failure mode — a fix right at its site with the same false claim left standing elsewhere — was finally closed by attacking the sweep itself: the reworker replaced a sweep keyed on *what it had edited* with one keyed on *what is being asserted*, across all artifacts rather than one. That is the correct generalisation, and my own independent sweep of the same shape reproduces its clean result.
