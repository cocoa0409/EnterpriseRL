# Policy-task audit — overpayment_waiver_and_recovery / charter-global

## charter_global_frozen

- Frozen: 2026-10-10T13:26Z, before any task view (blind or full) was opened. Auditor: independent erl-task-policy-audit agent (not the instantiator; no instantiator transcript, worklog or prior audit read).
- Inputs and hashes:
  - `tasks/overpayment_waiver_and_recovery/overpay.extended.yaml` sha256 `6ef941ea25a2e658d38fb8f65a6a55a040d029c725874d2e76b7826d2631ab77` (matches the brief)
  - `tasks/overpayment_waiver_and_recovery/task_tools.py` sha256 `1e57e51356ddb3bf1c149ef24481890215989ee0e99d27df47372e551c5a3d3a` (matches the brief)
  - `blueprint/products/overpay.yaml`, `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`; compute DSL semantics read from `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: SUM/COUNT/LATEST holding-scoped by `overpayment_id`; X* and CFIELD customer-scoped; `MONTHS` = whole months with day-of-month correction; `within_months` = `0 <= MONTHS(entry, NOW) < n`; LATEST keeps the first row on a date tie).
- Permitted: the charter, the tool module, schema, share tools. Masked/unread: every task file, every blind view, `worklog.md` (both the scenario-level and the difficulty-level one), all existing audits under `audits/`, all GT fields.
- Entry conditions (Step 0): gate snapshot supplied in the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred to render; validate_scenario pre-render document errors only). Masked views supplied with hashes; the hashes were recomputed and match (`task_0.blind.json` 455e20e5…, `task_1.blind.json` 70c256c7…, `0.json` 7eee0b01…, `1.json` af7ce174…). Input complete.
- Base copy: lines 1–1133 of the extended file are byte-identical to `blueprint/products/overpay.yaml` (diff shows only the appended comment banner); YAML-level comparison of every base key: identical.

### policy_conflict_scan

Seven extended policies, one `(target_tool, computes)` each:

| policy | target_tool (owner) | computes | base refs | overwrite |
| --- | --- | --- | --- | --- |
| overpay_ext_returned_payment_fee | book_returned_payment_fee_10cb479c (agent) | fee_amount | overpay_evt_penalty_interest | 1 sentence |
| overpay_ext_plan_arrears | pay_overpayment_arrears_d9b1e543 (user) | amount | agg_recovery_priority, evt_recovery, repayment_plan | [] |
| overpay_ext_plan_reinstatement | reinstate_repayment_plan_54c54ed5 (user) | monthly_amount | repayment_plan | 1 sentence |
| overpay_ext_new_plan_installment | set_up_repayment_plan_0b609272 (user) | monthly_amount | repayment_plan | 1 sentence |
| overpay_ext_waiver_household_income | complete_waiver_household_income_abba3816 (user) | annual_household_income | overpay_waiver | [] |
| overpay_ext_waiver_decision | record_waiver_decision_07f617be (agent) | waived_amount (+ decision enum) | overpay_waiver | 1 sentence |
| overpay_ext_plan_change | change_repayment_plan_f1933d01 (user) | monthly_amount | repayment_plan | 1 sentence |

Overlapping subjects: three policies share the base event `overpay_repayment_plan_set` (reinstatement / new plan / change); they are separated by plan state on the record (defaulted → reinstate; `none` → set up; current → change), stated in each rule's first sentence ("whose repayment plan has defaulted", "on an overpayment that has none", "carries a current repayment plan"). No two policies decide the same quantity on the same record state. Trigger/eligibility/time anchors: all inherit base `plan_on_open_debt` (status established or in_recovery) for the three plan writes and base waiver eligibility (waiver-eligible class, 30-day window, no pending appeal) for the two waiver writes; no extended policy relaxes them. Cross-category read boundaries: `claim` (history) and `withhold` (branch), read only, never written.

Prerequisite structure yields exactly two connected components, which is what M=2 scopes would partition:
- Chain A: `new_plan_installment` ← `plan_reinstatement` ← `plan_arrears` ← `returned_payment_fee` (root new plan; 3 prerequisite problems).
- Chain B: `plan_change` ← `waiver_decision` ← `waiver_household_income` (root plan change; 2 prerequisite problems).
The two components share no policy, so two tasks claiming one component each are disjoint and jointly cover all 7 policies. Which task claims which is a per-task question (charter_scope is masked; judged from each task's world/persona in its own file).

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` quotation (each `/`-separated part) is a verbatim substring of its policy's `rule` (7/7 policies, 0 misses); every sentence of every `baseline.rule` is a verbatim sentence of the `rule`; no snake_case token, tool name or policy id occurs in any extended `rule`. Every factor's ladder tiers appear as rule prose and as the branches of its `decides` binding. Manual sweep, expression by expression, found these non-equivalences (finding ids refer to `### findings`):

- returned_payment_fee `lookback_months`: rule "an overpayment carrying a repayment plan, **current or defaulted**, whose first installment due date has passed"; compute `F('repayment_plan_status') != 'none' and DAYS(...) > 0`. Schema enum `repayment_plan_status ∈ {none, current, defaulted, completed}` — compute admits `completed`, rule excludes it (G-3).
- returned_payment_fee `returned_amount` / `other_returns` and plan_arrears / plan_reinstatement `returned_installments`: rule speaks of "the returned repayment" / "other repayments … that came back unpaid" / "repayments were returned"; compute reads/counts `overpay_repayment_returned` **entries**. Base event grain: "One row per returned repayment per component". Where one returned repayment carries several component rows, LATEST amount returns one component's amount and COUNT overcounts repayments (G-4; world-dependent).
- waiver_household_income `pension_weekly`: rule "the latest weekly pension amount reported"; compute `MX(XLATEST(employer_funded), XLATEST(claimant_contributed))` — the larger of the two types' latest, not the latest (G-5; world-dependent: only when both pension types are reported).
- waiver_decision `waivable_principal`: rule "when the notice is dated before the overpaid period began"; compute tests `DAYS(overpaid_week_start, notice) < 0`, where `overpaid_week_start` is the first overpaid week's **ending Saturday** (schema). A notice dated in the six days before that Saturday is "within the overpaid period" by the rule (the period began on the Sunday) but "before" by compute (G-6; world-dependent).
- All other bindings: equivalent (windows `within_months` = "whole months … fewer than"; rounding up implemented as cent-ceiling on `RND(x*100,6)`; floors `MX(1, …)`, `MX(0, …)`, caps `MN(1, …)`, `MN(arrears, penalty_unpaid)` all quoted).

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above). The three `*_repayment_plan_*` tools each correspond to one plan state; the policy rule and the docstring agree on that state ("on one benefit overpayment that has no plan", "defaulted monthly repayment plan", "current repayment plan").
- Docstrings: no ordering word (before/after/first/then/until/prior/once/later) and no other tool's name in any of the 7 docstrings (scripted scan + reading). `set_up_repayment_plan` says "opening installment … thirty calendar days from today", consistent with `plan_first_payment_days: 30`.
- Tool bodies (read in full): none validates a prerequisite, an eligibility, a status or an amount; each `find`s the overpayment (and, for the income tool, the request) and writes the given value. `record_waiver_decision` does not check the request's income; `reinstate_repayment_plan` does not check that a repayment was booked; `set_up_repayment_plan` does not check other overpayments; `change_repayment_plan` does not check request status; `pay_overpayment_arrears` does not check fees. No tool hint or refusal tied to prerequisite state.
- uuid8 tails: 10cb479c, d9b1e543, 54c54ed5, 0b609272, abba3816, 07f617be, f1933d01 — pairwise distinct, no shared prefix/suffix, no sequential pattern; no evidence of batch derivation.
- Side effect note: `pay_overpayment_arrears` always books `component="penalty"`. This agrees with the arrears rule ("applied to the overpayment's penalty component") and with base application order only because the rule takes the payment solely when principal is fully recovered and caps it at the penalty unpaid.

### prerequisite_graph

| blocked policy | problem | kind | gate | form | verbatim in own rule | in depended-on rule | resolved_by = depended-on target_tool |
| --- | --- | --- | --- | --- | --- | --- | --- |
| plan_arrears | returned_payment_fee | value_input | fees_in_arrears (binding exists) | state | yes | no | yes |
| plan_reinstatement | plan_arrears | value_input | balance (binding exists) | state | yes | no | yes |
| new_plan_installment | plan_reinstatement | state_gate | overpayments.repayment_plan_status (real gate in the rule) | state | yes | no | yes |
| waiver_decision | waiver_household_income | value_input | household_income (binding exists) | state | yes | no | yes |
| plan_change | waiver_decision | value_input | balance (binding exists) | state | yes | no | yes |

`prerequisite: []` on returned_payment_fee and waiver_household_income. Every `problem` is an extended id of this file, none a base id or self; the graph is two disjoint chains, acyclic. No `fallback_reason` (all state form) — correct. No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

Condition-vs-sentence strength:
- waiver_decision: sentence "carries the household's annual income"; condition "annual_household_income **above zero**". A request carrying a stated income of 0.00 carries an income by the sentence but fails the condition — slight strengthening (O-4).
- plan_change: sentence "every waiver request lodged on the overpayment carries a decision"; condition adds "the overpayment is out of waiver review (status in_recovery or waived)". The added clause is a consequence of the depended-on write in the normal case, not a separate gate; the sentence does not carry it (O-4).
- Others: condition matches the sentence's strength and scope.

### prerequisite_sentences

Four-point test, every edge:

| edge | ordering connective | waits on (state, record words) | no tool/id/snake/row id | strength |
| --- | --- | --- | --- | --- |
| arrears ← fee | "is fixed only after" | "the overpayment's ledger carries a returned-payment fee for every repayment returned unpaid on it" | pass | "every" = closed set, matches condition |
| reinstatement ← arrears | "is not reinstated until" | "a repayment at least equal to the arrears payment worked out for it has been booked on the overpayment after the plan's most recent returned installment" | pass | matches |
| new plan ← reinstatement | "is set only after" | "none of the claimant's other overpayments carries a repayment plan whose status is defaulted" | pass | matches |
| decision ← income | "is not recorded until" | "the waiver request under review carries the household's annual income" | pass | see O-4 |
| change ← decision | "is changed only after" | "every waiver request lodged on the overpayment carries a decision" | pass | see O-4 |

One write per state (state-form uniqueness), derived as a reader must from the other rules:
- "returned-payment fee for every repayment returned unpaid" → only `overpay_ext_returned_payment_fee` books a fee ("a returned-payment fee is owed for that return and is booked once, as its own fee component"). Caveat: that rule charges only "the most recent repayment on the overpayment that was returned unpaid"; if a world has two or more returned repayments without a fee, no write of this difficulty can make the "every" state hold (checked per task).
- "a repayment … booked on the overpayment" → only `overpay_ext_plan_arrears` books a repayment ("the arrears payment is the claimant's own repayment, designated to that overpayment, made by card"). Single reading.
- "no other overpayment carries a defaulted plan" → only `overpay_ext_plan_reinstatement` changes a defaulted plan ("the reinstated plan returns to current standing"); new plan/change apply to `none`/current plans by their own first sentences. Single reading (per task: exactly one defaulted plan must exist on another overpayment).
- "request carries the household's annual income" → only `overpay_ext_waiver_household_income` writes the income ("the claimant completes it on the record by confirming the income worked out below"). Single reading.
- "every waiver request … carries a decision" → only `overpay_ext_waiver_decision` records a decision. Single reading.

No rule restates another rule's prerequisite sentence; no rule states a cross-problem order that grounds no edge (scan of every ordering connective in the seven rules: all others are intra-computation windows, e.g. "before the handling date"). Base sentence "When an appeal of the same determination is pending, the appeal is decided first and the waiver review waits" (overpay_waiver) states an order with an appeal, not with any problem of this difficulty; it is an inherited world gate, checked per task.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- **returned_payment_fee vs overpay_evt_penalty_interest**: penalty/interest sentences — not touched. Sentence 7 "A repayment returned unpaid … is followed by the returned-payment fee, which is booked as its own fee component" + param `returned_payment_fee` (25.00, all classes) governs the scored fee; extended computes face + surcharge + bank + late charge. Declared: the sentence is named in `overwrite`. However the declared `replaced_by` ("The returned-payment fee booked for a return is the classification's returned-payment fee, rounded to the cent") restates the base value, and the extended rule then states "The fee booked is the face charge plus the repeat-return surcharge, the pass-through bank charge and the late-return charge" (O-1).
- **plan_arrears vs overpay_agg_recovery_priority / overpay_evt_recovery / overpay_repayment_plan**, `overwrite: []`: designated repayment applied to the named overpayment — followed. Voluntary repayment accepted in any open status — followed (the arrears rule restricts only what it calls the arrears payment). Application order "fraud recoveries go to principal first, then penalty, then interest, then fees" — followed only because the payment is taken solely when principal is fully recovered and is capped at penalty unpaid (so penalty is next in order); a world with interest/fees unpaid is consistent because penalty precedes them. Card convenience fee never part of the amount — followed (docstring). Plan rule sentences (minimum, default, referral) — not touched. No undeclared override found.
- **plan_reinstatement / new_plan_installment / plan_change vs overpay_repayment_plan**: the installment sentence ("at least the classification's minimum … and at least the balance divided by … maximum plan months … the claimant may choose a larger installment") is named in each `overwrite`. Status gate ("only while … established or in_recovery") — inherited, not weakened. "The first installment is due the first-payment days after the plan is set" — new plan follows (tool sets +30 days); reinstatement and change keep the original first due date; base sentence speaks of a plan being set, not of an in-force plan being changed or reinstated — no scored quantity differs (the date is not a tool parameter) (observation O-5). Default rule, referral, "one plan may cover them all" — not touched; extended plans are per overpayment, which base permits ("may").
- **waiver_household_income vs overpay_waiver**, `overwrite: []`: base "The waiver request is the claimant's own application, giving household size and annual household income". Extended: for a one-person household the income entered is the Department-computed countable income "confirmed" by the claimant; for larger households the lodged figure stands. Where the lodged request carries no income figure, base supplies none and there is no conflict; where the claimant states a figure that differs from the computed one, base (the claimant's own figure) and extended (the computed figure) diverge on the scored quantity and no `overwrite` names the base sentence. Consequence is world/persona-dependent — demonstrated or cleared in the task file of the task that claims chain B (G-7).
- **waiver_decision vs overpay_waiver**: decision sentence named in `overwrite`; window, eligibility, "covers only the principal unpaid on the decision date", "no refund of amounts recovered", "appeal decided first" — inherited. Base lifecycle "waiver_pending → waived: The waiver is granted for the whole unpaid principal" vs extended "at or below the full-waiver percent the whole **waivable** principal is waived and the request is granted": where the notice cut-off makes the waivable principal smaller than the unpaid principal, extended "granted" (tool closes the overpayment as waived) leaves unpaid principal on a waived overpayment, contrary to the base transition meaning; the `replaced_by` declares "whole waivable principal" so the amount is declared, but the terminal status conflict with the base lifecycle is not (G-8; world-dependent).

### factor_ladders

Per policy (P = parameter, M = method as labelled; "honest" = auditor's judgement of the label; XD = cross_difficulty; MS = multi-source by the skill's definition):

**returned_payment_fee** (5 declared: 4 P, 1 M)
- face_amount_tier P: 40 / 30 / returned_payment_fee 25 — distinct; tiered NSF service charges by item amount are an established practice (honest).
- repeat_return_surcharge P: 15 / 10 / 0 — distinct, honest.
- return_lookback_window **M**: tiers select `lookback_months` 6 / 24 / 12, each substituted into the same `COUNT(… within_months=lookback_months …) - 1`; the ladder's own method texts are identical up to the number ("count other returns booked within the {plan|fraud|standard} look-back months"). This is a number in one formula → **mislabelled; honest label P**. Tier 1 conditions (plan status, start date) and tier 2 (classification) are fields of the one `overpayments` row → not MS.
- depository_bank_charge P: 15 / 12 / 6 / 0 — distinct, honest.
- late_return_handling P: 20 / 5 / 0 — distinct; conditions are return lag in days (the bank's timing). Business realism observation O-2 (charging the claimant more for a return the bank sent late is unusual; the "disputed-return" reading — long lags indicate an unauthorized-debit dispute — makes it defensible, so not a red light).
- Honest counts: **P 5, M 0** → fails "at least 1 method" (G-1). XD: none. MS: none.
- Baseline: "most recent returned repayment … fee is the classification's returned-payment fee, rounded" — self-sufficient (25.00); every factor fall-through equals it (face → 25, others → 0, lookback → standard 12 which with surcharge fall-through 0 is inert).

**plan_arrears** (4 declared: 3 P, 1 M)
- default_age_cutoff M: counts installments to the return's booking date / to the return + 1 / to the handling date — the counting endpoint changes (different date measure), accepted as method.
- breakdown_timing_price P: min_monthly_payment / midpoint / plan installment — distinct unless the plan installment equals the classification minimum (world check per task).
- support_obligation_share P: 0.5 / 0.75 / 1 — XD withhold; tier 1 = child-support order AND SNAP order (two withholding_orders rows), tier 2 = exactly one of them → **MS**.
- returned_installment_fees P: all unpaid fees / latest fee / 0 — distinct.
- Counts: P 3, M 1, XD 1 (withhold), MS 1. Bounds met.
- Baseline: self-sufficient (installments to date × plan installment − credit, floored at 0, principal gate, penalty cap), every sentence in the rule; fall-throughs equal it.

**plan_reinstatement** (4 declared: 2 P, 2 M)
- returned_installment_months P: 18 / 24 / max_plan_months. **For Fraud Overpayment — Repeat Offense, max_plan_months = 24 = single_return_months** → tiers 2 and 3 select the same value (G-2, class-dependent).
- defaulted_plan_end_anchor M: months on plan / months since return / 0 — different measures, accepted.
- intercept_relief P: 6 / 3 / 0.
- fraud_penalty_schedule M: split penalty over 12 or 6 months vs whole balance over reinstatement months — genuine algorithm change (tier 3), accepted.
- Counts: P 2, M 2, XD 0, MS 0 (tiers single-source).
- Baseline: balance / max_plan_months, cent-ceiling, floor at minimum — self-sufficient; fall-throughs equal it.

**new_plan_installment** (6 declared: 5 P, 1 M)
- principal_size_months P: 24 / 36 / max_plan_months. **First-offense fraud: max 36 = mid 36 (tiers 2/3 equal); repeat-offense fraud: max 24 = small 24 (tiers 1/3 equal)** (G-2, class-dependent).
- establishment_delay_extension P: 6 / 3 / 0. good_faith_payment P: 3 / 1 / 0. returned_payment_history P: 12 / 6 / 0. return_to_work P: 3 / 1 / 0, XD claim.
- determination_date_anchor M: all elapsed months / elapsed − 1 / 0 — anchors the plan at the determination date, the month after, or the set date; accepted as method with observation O-3 (the outcome is the same month measure offset by one).
- Counts: P 5, M 1, XD 1 (claim), MS 0.
- Baseline: balance / max_plan_months — self-sufficient; fall-throughs equal it.

**waiver_household_income** (5 declared: 4 P, 1 M)
- benefit_payment_dating M: date by week / by issue date less cancellations / by issue date — genuine; XD claim.
- earned_income_deduction P: 0.05 / 0.025 / 0; XD claim.
- support_order_exclusion P: weekly amount × 52 / window deductions × 4 / 0 — the tiers compute the quantity by different algorithms from different records (honest label M).
- other_pay_addition P: latest pension × 52 / vacation+holiday once / 0 — different algorithms (honest label M).
- withheld_tax_exclusion P: federal window × 4 / state window × 4 / 0 — same algorithm, different input; P acceptable.
- Honest counts: P 2, M 3 — bounds still met (mislabels recorded as O-6, no count consequence). XD claim + withhold. MS: benefit_dating tier 2 ("no supplemental, but a cancelled payment") is a conjunction over distinct claim_ledger rows; tier 1 is single-condition → not MS by the "every tier" definition.
- Baseline: issue-dated benefits + earnings in the 3-month window × 4, one-person rule — self-sufficient.

**waiver_decision** (6 declared: 5 P, 1 M... as labelled: period P, employment P, good_faith P, delay P, band **M**, notice cutoff M)
- overpaid_period_reliance P: 0.15 / 0.10 / 0. part_time_work_while_certifying P: 0.10 / 0.05 / 0, XD claim, tier 1 AND / tier 2 OR over claim_certifications + claims → **MS**. good_faith_repayment P: 0.05 / 0.025 / 0. slow_determination P: 0.10 / 0.05 / 0.
- partial_band_position **M**: multiplies the share by 1.2 / 0.8 / 1 — a number in one formula → honest label P (O-6; after relabel P 5, M 1 — bounds still met).
- redetermination_notice_cutoff M: pro-rata weeks / zero / whole — genuine; XD claim.
- Counts (honest): P 5, M 1, XD 2 (claim), MS 1.
- Baseline: income percent → full / partial at classification share 0.50 / denied, waivable = unpaid principal — self-sufficient.

**plan_change** (5 declared: 4 P, 1 M)
- remaining_principal_months P: 12 / 24 / max_plan_months (repeat-offense fraud max 24 = mid 24; waiver-eligible classes have 60 — class-dependent, G-2).
- hardship_band_months P: 12 / 6 / 0. review_months_given_back P: 2 / 1 / 0. waiver_size_months P: 3 / 1 / 0.
- determination_clock **M**: tier 1 (m ≥ 6) takes 6 off; tier 2 (1 ≤ m < 6) takes m off; tier 3 (m < 1, i.e. m = 0) takes nothing off = takes m off. Tier 3 is tier 2's method on its own domain, so the ladder is the single formula `min(m, 6)` — **two tiers select the same method, and the remaining distinction (a cap of 6) is a number** (G-1). Struck as a factor, plan_change has 4 factors, all P: **M 0**.
- Counts (honest): P 4, M 0 → fails. XD 0, MS 0.
- Baseline: balance / max_plan_months — self-sufficient.

Per-chain totals (honest labels): chain A (fee, arrears, reinstatement, new plan) has XD ≥ 1 (withhold, claim) and MS ≥ 1 (support_obligation_share); chain B (income, decision, change) has XD ≥ 1 (claim, withhold) and MS ≥ 1 (part_time_work_while_certifying). Per-computation method bound fails for returned_payment_fee and plan_change.

### findings

- **G-1 SOURCE-FACTOR (charter-global; consequence per task)** — symptom: two computations have no honest `method` factor. Root cause: `overpay_ext_returned_payment_fee.factors[return_lookback_window]` labelled `method` but its tiers only choose 6/24/12 for `within_months` in one COUNT; `overpay_ext_plan_change.factors[determination_clock]` labelled `method` but its tiers reduce to `min(months_since_determination, 6)` (tiers 2 and 3 identical in method). Evidence: compute lines `lookback_months: K('lookback_months_plan') if … else (K('lookback_months_fraud') if … else K('lookback_months_standard'))` and `determination_months_off: K('determination_months_cap') if m >= cap else (m if m >= 1 else 0)`. Consequence: each computation fails "at least 1 method"; demonstrated in the file of the task that claims each policy. Bears on: the task claiming chain A (fee) and the task claiming chain B (plan_change).
- **G-2 SOURCE-FACTOR (charter-global; class-dependent)** — ladders whose fall-through `P('max_plan_months')` coincides with another tier for some classifications: reinstatement `returned_installment_months` (repeat-offense 24 = single-return 24), new plan `principal_size_months` (first-offense 36 = mid 36; repeat-offense 24 = small 24), plan change `remaining_principal_months` (repeat-offense 24 = mid 24). RED only where the task's overpayment has that classification; checked per task.
- **G-3 SOURCE-POLICY (charter-global; world-dependent)** — returned_payment_fee look-back: rule "current or defaulted" vs compute `!= 'none'` (admits `completed`). RED only where the fee's overpayment carries a completed plan; checked per task.
- **G-4 SOURCE-POLICY (world-dependent)** — returned repayment counted/priced by ledger entry vs by repayment (base grain: one return row per component). Checked per task.
- **G-5 SOURCE-POLICY (world-dependent)** — pension "latest" vs `MX` of two types' latest. Checked per task.
- **G-6 SOURCE-POLICY (world-dependent)** — "before the overpaid period began" vs `DAYS(overpaid_week_start, notice) < 0` on a week-ending date. Checked per task.
- **G-7 SOURCE-POLICY candidate (persona-dependent)** — undeclared override of base "The waiver request is the claimant's own application, giving … annual household income" by the computed countable income, `overwrite: []`. Checked against the persona of the task claiming chain B.
- **G-8 SOURCE-POLICY candidate (world-dependent)** — "granted" on the whole waivable principal closes the overpayment as waived with unpaid principal left when the notice cut-off applies, against base lifecycle "waived: granted for the whole unpaid principal". Checked per task.
- **O-1 observation** — every policy writes its baseline as an unconditional sentence of the rule ("The returned-payment fee booked for a return is the classification's returned-payment fee"; "The reinstated/new/changed monthly installment is the overpayment's balance divided by the classification's maximum plan months"; "each is priced at the plan's monthly installment"; "counted by the date each payment was issued"; "The waiver share is the classification's partial-waiver share") and later sentences give the same quantity a different value ("The fee booked is the face charge plus …"). Read in full the later, composite sentences are explicit and the baseline value reappears as their fall-through tier, so a reader of the whole rule reaches one answer; this is the shape the framework requires (baseline sentences in the rule). Recorded, not a red light. The fee's `overwrite.replaced_by` restates the base value rather than the composite fee.
- **O-2 observation** — late-return charge raises the claimant's fee for the bank's lag; defensible only under the disputed-return reading.
- **O-3 observation** — new plan `determination_date_anchor` method tiers differ by a one-month offset of the same measure; accepted as method (anchor date).
- **O-4 observation** — prerequisite `condition` strength: waiver_decision "above zero" vs "carries the household's annual income"; plan_change adds an overpayment-status clause the sentence does not carry.
- **O-5 observation** — base "The first installment is due the first-payment days after the plan is set" vs reinstatement/change keeping the original first due date; not a scored parameter.
- **O-6 observation** — mislabels with no count consequence: household income `support_order_exclusion` and `other_pay_addition` (labelled P, honest M); waiver_decision `partial_band_position` (labelled M, honest P).
- **O-7 observation** — `overpay_ext_waiver_household_income.subject` is `overpay_waiver_review_opened`, but its tool writes only the income and opens no review; no tool of this difficulty performs the established/in_recovery → waiver_pending transition, so a waiver task must open with the review already open.
- **G-9 SOURCE-POLICY (charter-global; recorded 2026-10-10T13:30Z during the task-0 blind derivation, before any reveal)** — symptom: a ladder tier's scope lives only in the ladder and compute. `overpay_ext_new_plan_installment.factors[returned_payment_history].ladder` reads "two or more repayments **on the overpayment** were returned unpaid within the return-history months"; compute `COUNT('overpay_ledger', …)` is holding-scoped; the rule says only "Repayments that came back unpaid shorten the plan, counting the returns booked within the return-history months before the handling date", while its sibling sentences scope explicitly ("the most recent repayment received **on the overpayment**", "the most recent weekly benefit payment **on any of the claimant's** unemployment claims"). The rule therefore admits a claimant-wide count of returned repayments. Consequence demonstrated in `0.md` (world with returns on the claimant's other overpayment inside the window).

## closing_checklist

Written 2026-10-10T13:35Z, after both reveals. The difficulty is **not closed**: the source-layer audit does not pass.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this file sits alongside; first revision, nothing superseded. Comparison sections carry: task 0 SOURCE-FACTOR RED (F0-1) + SOURCE-POLICY RED (F0-2); task 1 SOURCE-FACTOR RED (F1-1). Neither carries PASS.
- Coverage and disjointness: task 0 claims chain A (returned_payment_fee, plan_arrears, plan_reinstatement, new_plan_installment; tools 10cb479c, d9b1e543, 54c54ed5, 0b609272), task 1 claims chain B (waiver_household_income, waiver_decision, plan_change; tools abba3816, 07f617be, f1933d01) — pairwise disjoint over whole trees, jointly all 7 policies and all 7 tools; GT write sequences close over exactly these tools; uuid8s independent (§action_binding_and_uuids). ✓
- Problem trees: task 0 — 3 prerequisite problems, 2 value_input edges, 3 owner=user writes, acyclic; task 1 — 2 prerequisite problems, 2 value_input edges, 2 owner=user writes, acyclic; the difficulty-wide graph is two disjoint chains, acyclic. ✓
- Factors: every factor bears weight on its task's world against an honest baseline and every all-baseline number is definite and differs from gold ✓; per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor ✓; **per computation ≥ 1 honest method factor fails for overpay_ext_returned_payment_fee (task 0) and overpay_ext_plan_change (task 1)** (G-1). Class-dependent ladder collapses (G-2) are not exercised by either world.
- Rule/compute: G-9 (new-plan returns sentence lacks the per-overpayment scope its ladder and compute carry) is exercised by task 0 (100.50 vs 134.00). G-3, G-4, G-5, G-6, G-7, G-8 are not exercised by either world and remain latent charter findings.
- Instantiation-stage gates: not re-run by this audit (the auditor cites the coordinator's snapshot in §charter_global_frozen; a re-run on a final form belongs after rework).

## revision_2

### charter_global_frozen (revision 2)

- Frozen 2026-10-10T18:17Z, before any round-2 task file field beyond the coordinator's masked views was read. Auditor: the same independent auditor as round 1.
- Inputs: `overpay.extended.yaml` sha256 `927d9ba44c9b1c4dd8df76bcba92a3f5bc0a31a62303e5755a03cddfc1cdccd7` (changed from 6ef941ea…), `task_tools.py` sha256 `ccfda0ae6ac1ccefc3f82e1080db496e8f0912db3c40d7c02dcc530354d3bbc4` (changed from 1e57e513…). Both hashes changed, so every charter-global section is re-derived in full below rather than carried forward. Blind views: `task_0.blind.json` 5d412894… (from `tasks/0.json` 05be2f1c…), `task_1.blind.json` 70c256c7… (unchanged from round 1; from `tasks/1.json` ab48012e…) — all recomputed and matching the brief.
- Round-1 text above is left untouched. Gate snapshot after rework: as supplied by the coordinator (all rc=0; traceability deferred). Reworker claims were taken as item ids only and verified against the artifacts.
- Base copy: lines 1–1133 still byte-identical to `blueprint/products/overpay.yaml`.
- Tool module diff (round-1 file reconstructed from the round-1 read and hash-verified as 1e57e513…): exactly one line changed — the `decision` enum text of `record_waiver_decision_07f617be` now reads "granted — the whole unpaid principal is waived …; partially_granted — less than the whole unpaid principal is waived …". No body change, no ordering word, no tool name; uuid8s unchanged.
- contamination_disclosure (charter level): this revision is written by an auditor who read both tasks' round-1 GT at 13:34Z. Nothing in this charter-global section depends on any GT field.

### policy_conflict_scan (revision 2)

Unchanged structure: the same 7 policies, tools and owners; the two disjoint chains (A: fee → arrears → reinstatement → new plan; B: income → decision → plan change); overlapping subject `overpay_repayment_plan_set` still separated by plan state. No new overlap.

### rule_compute_equivalence (revision 2)

Mechanical: every `compute_basis` part is a verbatim substring of its rule; `compute_basis` keys equal compute keys; every `baseline.rule` sentence is in its rule; no snake_case token in any rule. K-reference sweep (every `K('…')` in compute and ladders vs `params`): **`overpay_ext_plan_change.factors[remaining_principal_months].ladder` uses `K('small_remainder_months')` and `K('mid_remainder_months')`, neither of which exists in `params`** (params now carry `small_remainder_share: 0.2`, `mid_remainder_share: 0.4`; compute and rule use the shares) → R2-G-11. All other policies: no missing or unused key.

Round-1 world-dependent mismatches, re-checked:
- G-3 closed: compute `F('repayment_plan_status') == 'current' or … == 'defaulted'` now matches "current or defaulted".
- G-4 closed: rule now charges "the most recent return entry booked on the overpayment" with "each return entry counting as one returned item" and prices "the amount on the return entry being charged" — rule and compute now agree on entries.
- G-5 closed: rule "the latest weekly amount reported in the income window for each kind of pension … is added up"; compute sums the two kinds' latest, each gated on an in-window report (the unwindowed XLATEST cannot pick an out-of-window row once an in-window row of that kind exists, because no certification is dated after the handling date).
- G-6 closed: rule "the overpaid period begins on the Sunday six days before the first overpaid week's ending date"; compute treats `DAYS(week_start, notice) ≥ −6` as inside (0 weeks ending on or before a notice in that first partial week) and `< −6` as before the period.
- G-9 closed: new-plan rule now "Repayments **on the overpayment** that came back unpaid … counting the return entries booked **on the overpayment**".
- New latent mismatch R2-G-10 (fee look-back): rule "it is anchored at that first installment due date and covers the whole months elapsed from that date to the handling date plus the month in progress, **so returns from before the plan began are left out**"; compute `within_months = MONTHS(first_due, NOW) + 1` with the entry test `MONTHS(entry, NOW) < within_months`; ladder method "count return entries booked **from that date's month** to the handling date". For first due 2025-05-16 and handling 2025-10-14 the window is 5: a return booked 2025-05-15 (before the plan began) has MONTHS = 4 < 5 → counted by compute, excluded by the rule's clause; a return booked 2025-05-02 (in "that date's month") has MONTHS = 5 → excluded by compute, included by the ladder text. Three faces, two outcomes. Not exercised by task 0's world (no return between 2025-04-15 and 2025-05-31); latent.

### action_binding_and_uuids (revision 2)

Unchanged and re-confirmed: one `(target_tool, computes)` per policy; docstrings carry no ordering word or other tool name; tool bodies validate nothing; uuid8s pairwise distinct, unchanged. The `record_waiver_decision` enum text now matches the decision rule's new sentence "A request is granted only when the amount waived is the whole unpaid principal".

### prerequisite_graph (revision 2)

Same five edges, kinds, gates, forms, resolvers; acyclic; each `policy_source` verbatim in its own rule and absent from the depended-on rule. Changes: decision ← income sentence now "A waiver decision is not recorded until the waiver request under review carries a household annual income above zero." with condition "annual_household_income above zero" — strength now equal (round-1 O-4 half closed); plan_change condition drops the added overpayment-status clause and now matches the sentence (other O-4 half closed).

### prerequisite_sentences (revision 2)

Four-point test passes for all five edges (connectives: "is fixed only after", "is not reinstated until", "is set only after", "is not recorded until", "is changed only after"; record-visible states; no tool/id/snake token; strength matches). One write per state unchanged. The new household-income sentences ("An annual household income recorded as 0.00 on a request means the claimant stated no income; a request on which the claimant stated an income figure keeps the figure …") make 0.00 the record-visible form of "without the household's annual income"; the alternative reading of "stated no income" as "stated a zero income" would keep 0.00, which the decision sentence ("above zero") then never accepts — a reading with no solution, so the reader's only coherent reading is "not stated" (observation R2-O-12 on the phrase).

### override_declarations (revision 2)

- Fee: `overwrite.replaced_by` now states the composite fee ("The fee booked is the face charge plus …") — round-1 O-1 addressed for the declaration. The baseline sentence remains in the rule as the framework requires (O-1's remaining half is unchanged and stays an observation).
- Household income vs base "The waiver request is the claimant's own application, giving … annual household income": the new sentence "the income the claimant confirms on completion becomes the claimant's own statement of income on the application", with "a request on which the claimant stated an income figure keeps the figure the claimant stated", makes the computed figure the claimant's own statement and never overrides a stated one → G-7 closed (no conflict left to declare).
- Waiver decision: `replaced_by` no longer ties the full-percent tier to "granted"; new rule sentence "A request is granted only when the amount waived is the whole unpaid principal; when anything less is waived the request is partially granted and the rest of the principal stays in recovery" matches the base lifecycle meaning of `waived` → G-8 closed. Latent wording edge (observation R2-O-13): where the cut-off leaves nothing waivable and the income is at or below the full percent, nothing is waived yet the request is "partially granted" by this sentence, while above the partial percent nothing waived is "denied".
- Reinstatement / new plan / change: unchanged declarations.
- O-7 addressed: "The completion is made only on a request whose review is already open and does not itself open a review."

### factor_ladders (revision 2)

- returned_payment_fee: `return_lookback_window` (M) now selects the look-back by anchor — the first installment due date (months elapsed + 1), the determination date (months elapsed + 1), or a fixed 12 months back from the handling date. The tiers measure from different dates; accepted as an honest `method` (same standard as the anchors accepted in arrears/reinstatement/new plan). Fee counts P 4 / M 1 → **G-1 for the fee closed**. Ladder still has 3 tiers, all reachable (plan-on-record; fraud without plan; any other).
- plan_arrears: unchanged (P 3 / M 1, MS, XD withhold).
- plan_reinstatement: `returned_installment_months` now `int(max_plan_months × 0.5)` / `int(max × 0.75)` / max: 30/45/60, 24/36/48, 18/27/36, 12/18/24 for the four max values — distinct for every class → G-2 closed here.
- new_plan_installment: `principal_size_months` now shares 0.5 / 0.75 / 1 of max — distinct for every class → G-2 closed here. O-3 (anchor method by one-month offset) unchanged, still accepted.
- waiver_household_income: `support_order_exclusion`, `other_pay_addition` relabelled `method` → O-6 closed here (P 2 / M 3).
- waiver_decision: `partial_band_position` relabelled `parameter` → O-6 closed here (P 5 / M 1).
- plan_change:
  - `remaining_principal_months` compute now shares 0.2 / 0.4 / 1 of max (distinct for every class; G-2 closed in compute) — but its ladder values are `K('small_remainder_months')`, `K('mid_remainder_months')`, keys absent from the charter (R2-G-11).
  - `running_schedule_anchor` (M) replaces `determination_clock`: tier 1 "first installment due date has passed" → months from first due + 1; tier 2 "a first installment due date is recorded but has not yet passed" → min(cap, months since determination); tier 3 "no first installment due date recorded" → 0. Tiers 1 and 2 are genuinely different methods. **Tier 3 is unreachable inside the policy's own scope**: the rule opens "A claimant whose overpayment carries a current repayment plan may have its monthly installment changed", the schema defines `repayment_plan_start_date` as "Due date of the first installment of the current plan … empty when no plan", and every write that makes a plan current (`set_up_repayment_plan` sets it; `reinstate_repayment_plan` and `change_repayment_plan` keep it) leaves a date on record. The condition "a first installment due date is recorded" thus holds of every customer who reaches this write — it restates the scope, and the ladder divides those customers into two tiers, not three (R2-G-12). Struck as a factor, plan_change keeps 4 `parameter` factors and **0 method** → G-1 for plan_change **not closed**.

### findings (revision 2)

Round-1 items, status after verification:
- G-1: fee part **closed**; plan_change part **not closed** (R2-G-12).
- G-2 **closed** (all share-based ladders distinct for every classification), with R2-G-11 raised on the plan_change ladder face.
- G-3, G-4, G-5, G-6, G-7, G-8, G-9 **closed**.
- O-1 partly addressed (fee declaration), remainder unchanged (observation). O-2 addressed (the late-return charge is now explained as the depository's handling of a re-presented or disputed debit). O-3, O-5 unchanged (observations, accepted). O-4 closed. O-6 closed. O-7 closed.

New:
- **R2-G-11 SOURCE-POLICY RED (charter-global; consequence in `1.md`)** — symptom: a factor ladder names parameters the charter does not have. Root cause: the rework moved `remainder_months` to shares in `params`, `compute`, `compute_basis` and the rule but left the ladder of `remaining_principal_months` on the removed keys. Evidence: ladder tiers `value: K('small_remainder_months')`, `value: K('mid_remainder_months')`; `params` has only `small_remainder_share: 0.2`, `mid_remainder_share: 0.4`; compute `int(P('max_plan_months') * K('small_remainder_share')) if …`. Consequence: the ladder tier is not a branch of its `decides` binding and its value is not drawn from the charter (evaluates to no value); demonstrated on task 1's world in `1.md`. Regression introduced by the rework.
- **R2-G-12 SOURCE-FACTOR RED (charter-global; consequence in `1.md`)** — `running_schedule_anchor` has an unreachable fall-through tier (above); plan_change has no honest method factor.
- **R2-G-10 SOURCE-POLICY (latent, not exercised by either world)** — fee plan-anchored look-back: rule clause "so returns from before the plan began are left out" and ladder text "from that date's month" disagree with compute's whole-months test for returns booked within a month before the first due date.
- R2-O-12 observation — "stated no income" for 0.00 is readable as "stated a zero income"; only the coherence argument above excludes it.
- R2-O-13 observation — waiver decision naming when nothing is waivable at or below the full percent (latent).

### closing_checklist (revision 2)

Written 2026-10-10T18:18Z, after both revision-2 reveals. The difficulty is **still not closed**.

- Files: `0.md`, `1.md`, `_difficulty.md`, each with round-1 text untouched and a `## revision_2` appended (frozen derivation before reveal, then comparison).
- Verdicts: task 0 **PASS** (all four relationships); task 1 **SOURCE-FACTOR RED (F1-1 / R2-G-12) + SOURCE-POLICY RED (F1-4 / R2-G-11)**.
- Round-1 REDs: F0-1 closed; F0-2 closed; F1-1 not closed (a new ladder replaced the old one, but its fall-through tier cannot be reached under the policy's own scope).
- Regression check: one new defect introduced by the rework (R2-G-11, plan_change ladder naming removed parameters); no figure regressed in either task; task 0's changed seed fee (46.00 → 36.00) now matches the round-2 fee policy at its booking date, and the derived figures moved consistently (arrears 148.00 → 138.00, reinstatement 59.89 → 60.22).
- Coverage, disjointness, uuid8s, trees (n = 3 / n = 2, value_input 2 / 2, customer writes 3 / 2, acyclic): unchanged ✓.
- Factor bounds: every computation now has an honest method factor except overpay_ext_plan_change; every factor bears weight with a definite, differing all-baseline number ✓; per task MS ≥ 1 and XD ≥ 1 ✓.
- Latent (not exercised by either world): R2-G-10 (fee plan-anchored look-back: rule clause / ladder text / compute disagree for returns within a month before the first due date); R2-O-12, R2-O-13 observations.
- Instantiation-stage gates: not re-run by the auditor; the coordinator's post-rework snapshot is cited above.

## revision_3

### charter_global_frozen (revision 3)

- Frozen 2026-10-10T19:06Z, before any round-3 GT field was read. Same auditor.
- Inputs: `overpay.extended.yaml` sha256 `b41f769e6f6137481618437df5e6a1f6def01fb6b0cdc0c488d166c7a7f60eba` (changed from 927d9ba4…), `task_tools.py` sha256 `0ef251c89bbadaa135c7f1a953142fcfb769e75fc916c7be764b0b88bff0218c` (changed from ccfda0ae…). Both changed → every charter-global section re-derived. Blind views unchanged since revision 2 (5d412894…, 70c256c7…); task files now `0.json` d02d7137…, `1.json` 17a486db… — all hashes recomputed and matching the brief.
- Method of comparison: the round-2 charter's rules, compute, ladders and baselines were printed in full during revision 2 and kept; the round-3 charter was printed in the same format and diffed structure-by-structure and sentence-by-sentence. Tool module diffed against the hash-verified round-1 reconstruction.
- Base copy still byte-identical. Mechanical sweep: every compute_basis part verbatim in its rule; compute_basis keys = compute keys; every baseline sentence in its rule; every prerequisite sentence verbatim; no snake_case token in any rule; every `K('…')` in compute and ladders exists in `params` and no param is unused (all 7 policies).
- contamination_disclosure: the auditor has read both tasks' round-1 and round-2 GT. Nothing in this section depends on a GT field.

### what changed (round 2 → round 3)

- returned_payment_fee: the rule clause "so returns from before the plan began are left out" is removed; the look-back ladder methods now read "the whole months elapsed from that date [first due / determination] to the handling date plus the month in progress" and "run the look-back back from the handling date over the fixed standard look-back months". Compute unchanged.
- waiver_household_income: "An annual household income recorded as 0.00 on a request is the record of a request lodged without any income figure; a request on which the claimant wrote an income figure keeps the figure the claimant wrote, …" (was "means the claimant stated no income … stated an income figure …"). Compute unchanged.
- waiver_decision: "when an amount above zero but less than the whole unpaid principal is waived the request is partially granted …; when nothing is waived the request is denied." Compute unchanged. Tool docstring enum: "partially_granted — an amount above zero but less than the whole unpaid principal is waived".
- plan_change: ladder of `remaining_principal_months` now `int(P('max_plan_months') * K('small_remainder_share'))` / `… K('mid_remainder_share')` / max — equal to compute; `running_schedule_anchor` rebuilt: new binding `review_opened_on = LATEST(request_date)`; compute `(MONTHS(first_due, review_opened_on) + 1 if review_opened_on != None and DAYS(first_due, review_opened_on) > 0 else MONTHS(first_due, NOW) + 1) if DAYS(first_due, NOW) > 0 else MN(cap, months_since_determination)`; rule tiers: (1) first due passed, no waiver request lodged after it → whole months first due → handling date + 1; (2) first due passed, a request lodged after it → "billing stopped for the review, so only the installments fallen due before the review are taken off", whole months first due → latest request date + 1; (3) first due not yet passed → months since determination, capped at 6.
- All other policies: byte-for-byte unchanged in rule, compute, ladders, params, prerequisites.

### verification of round-2 items

- **R2-G-11 closed**: the ladder values are now the compute branches, with keys present in `params`.
- **R2-G-12 closed**: all three `running_schedule_anchor` tiers are reachable inside the policy's scope (a current plan whose first due date has passed with or without a later waiver request; a current plan set within its first-payment days whose first due date has not passed), pairwise disjoint, and select different measures (to the handling date / to the latest request date / from the determination date, capped) — accepted as `method` on the same standard as `default_age_cutoff`. Plan change counts: P 4 / M 1 ✓. "latest waiver request date" vs "a waiver request was lodged … after that date": the latest request date is after the first due date exactly when some request is, so compute and rule agree.
- **R2-G-10 closed**: rule, ladder and compute now state the same window (whole months + month in progress, entry test "fewer than that number"); the contradicting clause is gone.
- **R2-O-12 closed**: 0.00 is now unambiguously "lodged without any income figure".
- **R2-O-13 closed**: zero waived → denied in every income band; the enum docstring agrees.
- O-1 remainder, O-3, O-5: unchanged, still observations.
- Re-run of every revision-2 structural conclusion (conflict scan, uuids, prerequisite graph and sentences, override declarations, factor ladders of the five unchanged policies): unchanged and still holding.

### new findings (revision 3)

- **R3-O-14 observation (not exercised by either world)** — overlap between `running_schedule_anchor` tier 2 and `review_months_given_back`. Both credit the same billing stop. Tier 2 says "billing stopped for the review, so only the installments fallen due before the review are taken off", and `review_months_given_back` says "Months spent under waiver review, when billing stopped, are given back". Worked example: first due 2025-06-26, request lodged 2025-08-20, handling 2025-10-21. Tier 2 takes off 2 instead of the 4 tier 1 would take, and the review factor adds +2 on top, so the 2-month review lengthens the plan by 4. For a customer whose request came before the first due date (tier 1), the review months are taken off and given back once, a net of 0. The same billing stop is credited differently depending on whether the request came before or after the first installment. Each tier on its own is a treatment an agency could publish (stop counting at the billing stop), so this is recorded as an observation about how the two factors interact, not as an unreal tier. Task 1's customer takes tier 1, so its score is not affected.

### closing_checklist (revision 3)

Written 2026-10-10T19:07Z, after both revision-3 reveals. All M = 2 tasks PASS all four relationships; the difficulty passes the source-layer audit.

- Files: `0.md`, `1.md`, `_difficulty.md`. Each keeps its round-1 and revision-2 text unchanged and has a `## revision_3` appended (frozen recomputation first, then the comparison). Every revision-3 comparison carries PASS.
- Coverage and disjointness: task 0 covers chain A (4 policies, tools 10cb479c / d9b1e543 / 54c54ed5 / 0b609272). Task 1 covers chain B (3 policies, tools abba3816 / 07f617be / f1933d01). The two scopes are pairwise disjoint over whole trees and together cover all 7 extended policies and all 7 tools. The GT write sequences use exactly these tools. The uuid8s are independent and unchanged.
- Problem trees: task 0 has n = 3, 2 value_input edges and 3 customer writes; task 1 has n = 2, 2 value_input edges and 2 customer writes. Both are acyclic, and the difficulty-wide graph is two disjoint chains with no cycle.
- Factors: every computation has 4–6 factors with at least 2 `parameter` and at least 1 honest `method`:
  - fee 4/1, arrears 3/1, reinstatement 2/2, new plan 5/1, income 2/3, decision 5/1, plan change 4/1.
  - Every ladder has ≥ 3 reachable tiers with distinct outcomes, and every condition and outcome is stated in its rule and implemented in compute.
  - Every factor bears weight on its task's world against an honest baseline. The all-baseline numbers (25.00, 180.00, 50.00, 50.25; 36,024.00, 1,150.00, 25.00) are definite and differ from gold.
  - Each task has MS ≥ 1 and XD ≥ 1 with seeded rows.
- Round-2 REDs: R2-G-11/F1-4 closed and R2-G-12/F1-1 closed. R2-G-10, R2-O-12 and R2-O-13 are closed. Task 0 did not regress; all of its figures are identical to revision 2. No new red.
- Open observations (no red): O-1 remainder (baseline sentence kept in each rule as the framework requires), O-3, O-5, and R3-O-14 (latent overlap between running_schedule_anchor tier 2 and review_months_given_back; not exercised by either world).
- Instantiation-stage gates: the auditor did not re-run them and cites the coordinator's post-round-3 snapshot (all rc=0; check_traceability deferred to render).
