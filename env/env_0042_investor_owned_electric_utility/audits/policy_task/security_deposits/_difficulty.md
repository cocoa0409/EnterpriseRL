# Policy-task audit — security_deposits / charter-global

## charter_global_frozen

- Freeze time: 2026-10-07T21:28Z (written before any task GT was revealed; nothing here comes from a revealed GT).
- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the authoring agent.
- Freeze hashes (sha256, re-checked against MANIFEST.txt at audit start, all equal):
  - `tasks/security_deposits/deposit.extended.yaml` 1d716ce96b5d38229ade737ebd14be2bf3d7c16a3a24169bfbc2fd8726c565b9
  - `tasks/security_deposits/task_tools.py` 2d4addd19f5f2ab92568746c4aab02f61c8e9dc614e7e3899e6d5973a6e399d1
- Fields read: `blueprint/blueprint.yaml`, `blueprint/products/deposit.yaml`, `blueprint/share_tools.py`, the extended charter and `task_tools.py` in full, and the masked views `task_0.view.json` / `task_1.view.json` (frozen_time, user_scenario, initial_state only).
- Fields masked and unread at this point: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*` in `tasks/*.json`. `worklog.md` and any authoring scratch were not read.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK with "suite depth: history_rows_max=11(>= 8) branches_max=89(>= 5)"; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred because the KB is not published yet), the masked views and MANIFEST.txt with hashes. Input complete. The deferred traceability gate is noted. It is not a defect of this audit.
- Base-section verbatim check: `diff` of the charter's base section (lines 1-1011) against `blueprint/products/deposit.yaml` shows no difference except the appended `extended_policies:` header. The base copy is verbatim.

### policy_conflict_scan

The charter has seven extended policies. Each one, with its target tool, trigger and the subject it writes:

| policy | target tool (owner) | trigger | writes |
| --- | --- | --- | --- |
| deposit_ext_failed_review_extension | extend_deposit_review_04d6c850 (agent) | state_due | refund_review_date |
| deposit_ext_anniversary_interest | credit_deposit_interest_e2c6de3a (agent) | state_due | deposit_interest_credit row, held_amount |
| deposit_ext_recalculated_requirement | require_additional_deposit_b541b477 (agent) | state_due | required_amount, average_monthly_bill, due date, status held->assessed |
| deposit_ext_additional_installment | pay_additional_deposit_64b1dc0d (user) | on_request | deposit_payment row (installment n+1), installment_count, held_amount |
| deposit_ext_new_agreement_requirement | assess_new_service_deposit_5e8da269 (agent) | state_due | new deposit_accounts row |
| deposit_ext_opening_installment | pay_deposit_installment_d7ce4a9b (user) | on_request | deposit_payment row (installment 1), installment_count |
| deposit_ext_review_refund | refund_deposit_by_check_703d791f (agent) | state_due | deposit_refund full_refund by check, status refunded |

Overlaps found:
- **Same day, same deposit: review, anniversary and recalculation.** A business deposit's refund review date can fall on an anniversary of its fully secured date that is also a recalculation date. For GD, reviews run every 24 months and recalculations every 12, so the 24-month review date is the second anniversary and a recalculation date. The charter puts the three in order as follows. The review outcome is decided first (base `deposit_refund_review`). Interest for that anniversary is gated on the review date lying after the anniversary, which only an extension produces. Recalculation is gated on that interest credit.
  - When the review passes, the anniversary credit can never be booked. The refund closing period carries that year instead, and the recalculation can never be fixed.
  - When the review fails, the order is extension → interest → recalculation.
  - Neither branch gives two compatible conclusions. No conflict.
- **Two refund policies.** Base `deposit_refund_review` (bill credit by default) and `deposit_ext_review_refund` (by check, on the customer's request) overlap on `deposit_refund_completion`/`deposit_refund`. The extended policy declares the overwrite of base's "A passed review refunds ..." sentence. No conflict for a check request. Bill-credit refunds have no tool in this difficulty.
- **Two installment policies.** `deposit_ext_opening_installment` (installment 1 of a deposit on a new agreement) and `deposit_ext_additional_installment` (installments numbered on from the latest, on a raised business requirement) write the same event `deposit_payment`, through different tools and on disjoint deposit states (never-paid assessed vs re-assessed after recalculation). No overlap in object.
- **Claimed event types.** `blueprint.yaml` claims, for this difficulty, `[deposit_assessment, deposit_waiver, deposit_payment, deposit_full_security, deposit_refund_completion, deposit_refund, deposit_review_update, deposit_transfer]`. `deposit_ext_anniversary_interest` writes `deposit_interest_credit` and `deposit_ext_recalculated_requirement` writes `deposit_additional_requirement`. Neither type is in this claim or in any other difficulty's claim (blueprint lines 15, 47, 78, 107, 134). This is an observation (O-G1). It changes none of the four relationships, and the cross-difficulty merge surface is out of scope here.
- **Task scopes.** These were derived blind from the masked views and are to be confirmed against `charter_scope` after the reveal. Task 0 resolves {failed_review_extension, anniversary_interest, recalculated_requirement, additional_installment}. Task 1 resolves {new_agreement_requirement, opening_installment, review_refund}. The two sets are disjoint and together cover all 7 extended policies.

### rule_compute_equivalence

Check 2 was run over each policy, sweeping `compute_basis` quotations against the rule and back.

- **deposit_ext_failed_review_extension.** Every binding has a verbatim basis, and every tier of the five ladders is a rule sentence and a branch of its `decides` binding. Two caveats:
  - The rule anchors the review window, the clean-credit months and the "disconnected on the day of the review" test to "the day the review is decided, which is the refund review date". The compute anchors all three on NOW (`within_months` windows, `MONTHS(latest_late_date, NOW)`, `EXISTS(status='disconnected')`). The two agree only when the handling date equals the recorded review date. This is an observation (O-G2): both tasks handle on the review date.
  - The rule's disconnection count is "plus one when any of the customer's agreements is disconnected". Base `deposit_msr_review_disconnections` says "plus one for each ... currently in disconnected status". The extended count is used only in `> 0` tests, so the outcome is unaffected. Observation (O-G3).
- **deposit_ext_anniversary_interest.** Compute matches the rule except at the calendar-year boundary:
  - The rule says "The Commission sets the deposit interest rate for each calendar year: rate_2024 for 2024, rate_2025 for 2025 and interest_rate_annual from 2026 on." Under that sentence 1 January of the anniversary's year earns the closing year's rate.
  - The rule also says "the days from its start to 1 January of the anniversary's year earn the earlier year's rate" together with "Days are counted from the start date to the end date, the start date not counted." Under those sentences 1 January is counted among the days earning the earlier year's rate.
  - Compute `days_prior_year: MX(0, DAYS(year_start, closing_year_start))` implements the second reading (1 January counted at the earlier rate).
  - The two sentences of one rule give different conclusions for the same day. This is finding **F-G1**.
  - The `paid_in_year` and lapse windows are `within_months=12` from NOW. They equal "the year being credited" only when the handling date is the anniversary and the year runs a full 12 months. Observation, folded into O-G2.
- **deposit_ext_recalculated_requirement.** All quantities have a verbatim basis, the phase-in tiers match, and the rounding (cent, then up to the dollar, then floor/cap) matches. One gap: the rule never states which quantity is recorded as the deposit's average monthly bill. The target tool takes `average_monthly_bill` ("the average monthly bill the new requirement rests on"). Base supplies `deposit_msr_average_bill`, the twelve-month mean of regular bills "before the assessment or recalculation date", together with the event field "Average monthly bill used in the recalculation". Where the billing basis is not the twelve-month mean, two values are defensible: the billing basis, or base's twelve-month mean. The contrast is `deposit_ext_new_agreement_requirement`, which says outright: "The estimate so adjusted is rounded to the cent and is the average monthly bill recorded on the deposit." This is finding **F-G2**. Its consequence is demonstrated per task.
- **deposit_ext_additional_installment.** Bindings match the rule. `regular_installment` floors to the cent. `result` caps at additional_due. The rule says nothing about the installments after the front-loaded first one; they are not computed and not scored. Observation (O-G4).
- **deposit_ext_new_agreement_requirement.** Bindings match, with these caveats:
  - `heating_factor` and `established_cut` use `sister_bill_count >= average_bill_minimum_months` for "drawn from a sister agreement", which is equivalent.
  - `refund_relief` uses `COUNT('deposit_transactions', ..., refund_kind='full_refund')` with no filter for "of that kind", and `F('status')`/`F('fully_secured_date')` for "that deposit". The compute is looser than the rule. Observation (O-G5). It has no effect in any world where the customer's only refunded or held deposit is of the same kind.
  - `sister_account` takes the first active agreement on the same schedule. The rule is silent when there are two. Folded into O-G5.
- **deposit_ext_opening_installment.** Two caveats:
  - The rule says "regular bills were issued on three or more of the customer's other agreements". Compute `other_sites_billed` counts bills, not agreements, and does not exclude the deposit's own agreement. Observation (O-G6). It is equivalent whenever each other agreement carries one bill in the one-month window and the own agreement has none.
  - `installments` = `MN(MX(1, ...), int(required // minimum_installment_usd))` matches "reduced until each installment reaches minimum_installment_usd".
- **deposit_ext_review_refund.** Compute matches the rule except at the same boundary as F-G1:
  - The rule says "its days before 1 January of the refund date's year earn the opening rate". Days before 1 January exclude 1 January.
  - Compute `closing_days_before_new_year: MX(0, DAYS(closing_period_start, refund_year_start))` counts through 1 January. That is one day more than the rule.
  - This is rule/compute non-equivalence, finding **F-G3**. It also shows that the charter words the same boundary two ways: "to 1 January" in the interest policy and "before 1 January" in the refund policy.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy: (extend…04d6c850, extension_months), (credit…e2c6de3a, interest_amount), (require…b541b477, required_amount), (pay_additional…64b1dc0d, amount), (assess…5e8da269, required_amount), (pay_deposit_installment…d7ce4a9b, amount), (refund…703d791f, refund_amount). No tool is shared.
- uuid8s: 04d6c850, e2c6de3a, b541b477, 64b1dc0d, 5e8da269, d7ce4a9b, 703d791f. All seven are distinct, share no common prefix or tail, and are not sequential. Nothing suggests batch derivation.
- Tool bodies were read in full. No tool checks status, gates, windows or prerequisite state:
  - `require_additional_deposit` and `assess_new_service_deposit` write unconditionally.
  - The two pay tools and the refund tool only look up the row to copy ids.
  - `extend_deposit_review` only refuses when the deposit id does not exist.
  - The tools judge no prerequisite.
- Docstrings name no other tool and no policy. Two minor items, both observations (O-G7) with no demonstrable consequence:
  - `extend_deposit_review` ("stays held after its satisfactory payment review") and `refund_deposit_by_check` ("after its satisfactory payment review") use "after" about the review event, not about another tool's write.
  - `require_additional_deposit` says it returns the deposit to assessed "so that the additional amount can be paid". That hints at the dependent's existence without naming it.

### prerequisite_graph

Check 7 found these edges:

| # | blocked policy | problem (depended on) | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | anniversary_interest | failed_review_extension | state_gate | deposit_accounts.refund_review_date | state | extend_deposit_review_04d6c850 |
| E2 | recalculated_requirement | anniversary_interest | value_input | held_amount_now | state | credit_deposit_interest_e2c6de3a |
| E3 | additional_installment | recalculated_requirement | value_input | raised_requirement | state | require_additional_deposit_b541b477 |
| E4 | new_agreement_requirement | opening_installment | state_gate | deposit_transactions.installment_number | state | pay_deposit_installment_d7ce4a9b |
| E5 | new_agreement_requirement | review_refund | value_input | refund_relief | action (fallback_reason present) | refund_deposit_by_check_703d791f |

- `prerequisite` is filled in on all 7 policies (`[]` on extension, opening_installment, review_refund).
- Every `problem` is an extended policy id of this file. None is base and none points at itself.
- The graph has two components, E1→E2→E3 and {E4, E5}. It is acyclic.
- Every `policy_source` was located verbatim in the blocked policy's own `rule`. Each was grep-checked against the rule text read above.
- `form`/`fallback_reason` pairing is correct: only E5 is action-form and only E5 carries `fallback_reason`.
- `resolved_by` equals the depended-on policy's `target_tool` in all five edges, and each tool's effect makes the gate hold:
  - The new review date is later.
  - The interest row is written.
  - Status becomes assessed with the new required amount.
  - An installment-1 payment row is written.
  - Status becomes refunded with a full_refund row.
- `kind` matches `gate`: the two state_gates point at real fields, and the three value_inputs point at existing compute bindings (`held_amount_now`, `raised_requirement`, `refund_relief`).
- Conditions:
  - E1's `condition` ends "..., which is the handling date". E2's ends "up to and including the handling date". "Handling date" is general wording, not "this task / at the opening". Observation only (O-G8).
  - No condition is strengthened or weakened against its sentence.

### prerequisite_sentences

Check 6 applies four points to each sentence: an ordering connective, the waited-on state or action, no tool/id/snake_case, and scope equal to the condition.

- **E1**: "The interest for a completed year is credited only once the refund review date recorded on the deposit falls after the anniversary that closes that year."
  - Connective "only once". The waited-on state is a record-visible field in table words ("refund review date recorded on the deposit"). No tool or id. Scope equals the condition. Passes.
  - Unique writer: only `extend_deposit_review` changes `refund_review_date` among this difficulty's writes.
  - Derivation: the review date sits on the anniversary, so the reader must find the rule that moves the review date. Only `deposit_ext_failed_review_extension` does ("its refund review date moves out ..."). Single reading.
- **E2**: "The recalculated requirement is not fixed until the deposit carries an interest credit for every anniversary of its fully secured date reached so far."
  - Connective "not ... until". State form (interest credit rows on the deposit). Passes.
  - Unique writer: `credit_deposit_interest`.
  - Derivation: the anniversary is reached and not credited, so the reader goes to `deposit_ext_anniversary_interest`. Single reading.
- **E3**: "The installment of an additional deposit is worked out only after the deposit shows its raised required amount and has returned to assessed status."
  - Connective "only after". State form. Passes.
  - Unique writer: `require_additional_deposit`. `assess_new_service_deposit` creates assessed rows but never "returned" ones.
  - Derivation leads to `deposit_ext_recalculated_requirement`. Single reading.
- **E4**: "The deposit required on a new agreement is not fixed until every other deposit of the customer that stands assessed shows its first installment received."
  - Connective "not ... until". State form. Passes.
  - Unique writer: `pay_deposit_installment` (installment 1). `pay_additional_deposit` numbers on from the latest installment, so it never writes a first installment.
  - Derivation leads to `deposit_ext_opening_installment`. That policy covers only "a deposit assessed on a new agreement". Whether the other assessed deposit is such a deposit is a per-task fact.
- **E5** (action form): "The deposit required on a new agreement is fixed only after any deposit of the customer whose satisfactory payment review has been passed on its refund review date has been refunded."
  - Connective "only after". The action "has been refunded" is in business words. No tool or id. Scope equals the condition.
  - Fallback test: the refund leaves a record-visible state that singles it out, namely status `refunded` with a `full_refund` deposit_refund row. The edge's own `condition` names that state. The `fallback_reason` argues that the records cannot tell which held deposit passed its review. That is a reason the reader must judge the review, not a reason no state marks the refund. The fallback is unjustified. Observation (O-G9), naming that state.
  - Derivation leads to `deposit_ext_review_refund` (the only policy that refunds in full). Single reading.
- The depended-on rules do not restate any sentence. Checked: extension's rule never mentions interest; interest's rule never mentions recalculation; recalculation's rule never mentions the additional installment; opening_installment and review_refund never mention new-agreement assessments.
- No extended rule states a cross-problem order beyond these five sentences.
- Base sentences that state an order:
  - `deposit_installments_and_security` "Deposit payments are accepted only while the deposit is in assessed status". Task 0's E3 rests on its own extended sentence, so this base sentence grounds no edge. Observation.
  - `deposit_assessment_rule` "a disconnected agreement is not reconnected until the first installment is received" concerns service and is unused.

### override_declarations

Check 1 swept each `base_policy_refs` entry sentence by sentence. Only deviations and findings are listed; every sentence not listed is followed or not engaged.

- **failed_review_extension**
  - `deposit_refund_review` "A failed review leaves the deposit held and moves the refund review date out by review_extension_months." Declared.
  - The extension's own "counted late payment charges" deducts waiver credits posted in the window. Base `deposit_msr_review_late_charges` excludes charges "later waived". The two can differ when a waiver in the window is for a charge outside it. Only the extension's length tier uses this, never the pass/fail test. Observation (O-G10).
- **anniversary_interest**
  - Three base sentences of `deposit_interest_rule` are declared (rate, compounding, crediting).
  - "No interest is paid when ... less than interest_min_holding_months" is inherited.
  - "Each interest period is credited once, and interest is credited only on a deposit in held status" is inherited.
  - The new review-date gate on crediting sits inside the declared supersession of base's "Interest for a full year is credited on each anniversary ...". Covered.
- **recalculated_requirement**
  - "with the same formula as at assessment" is declared.
  - `deposit_recalculation`'s threshold sentence ("exceeds the held cash by more than recalculation_increase_threshold_pct ... the difference due within additional_deposit_due_days") is inherited and not contradicted.
- **additional_installment** — finding **F-G4**, undeclared override:
  - Declared: `deposit_installments_and_security` "The regular installment is ..." and "Each installment number is recorded once."
  - The policy also cites `deposit_recalculation`, whose sentence "When the recalculated amount exceeds the held cash by more than recalculation_increase_threshold_pct of the held cash, the deposit returns to assessed with the new required amount and the difference due within additional_deposit_due_days" fixes the amount due as the recalculated amount less the held cash.
  - The extended rule defines "the held cash, which is the cash received less the cash refunded" and then makes the amount due "the required amount recorded on the deposit less the held basis". The held basis adds all or half of the credited interest on a deposit held 24 or 12 months or more.
  - That changes the amount due away from base's "difference", and no `overwrite` entry names the `deposit_recalculation` sentence.
  - The consequence is demonstrated per task.
  - A second latent conflict is inherited unmodified: "The deposit becomes held on the day deposit_msr_cash_received reaches the required amount". `deposit_msr_cash_received` sums all deposit_payment rows, including cash later refunded as excess, so a re-assessed deposit can turn held before the extended plan completes. That is not on the scored first installment. Observation (O-G11).
- **new_agreement_requirement**
  - Formula, installment count and the three trigger-window sentences are declared.
  - The new-service window, the kind selection, the first-installment due date ("first_installment_due_days after assessment"), and agg_multi_holding's one-open-deposit rule are inherited.
- **opening_installment**
  - The regular-installment, installment-number and installment-count sentences are declared.
  - `deposit_assessment_rule` "later installments under installment_schedule" is not declared. The rule's "each later installment due 30 calendar days after the previous one" conflicts with GD/LP's "single payment". Due dates are not a computed or scored quantity, so there is no consequence for the scored amount. Observation (O-G12).
- **review_refund**
  - Four supersessions are declared (passed-review payout and method, rate, base, crediting).
  - The interest_min_holding_months floor is inherited. Base's other review sentences are inherited.

### factor_ladders

Structure only. Counts are `parameter / method`. Cross-difficulty categories are read from the charter's `cross_difficulty` fields.

- **failed_review_extension**: 5 factors, 4 parameter / 1 method.
  - shortfall_length (parameter): 3 tiers, multi-source disjunction (customer-wide reconnections or secured-agreement reversals), service.
  - clean_run_credit (method, which anchor date the credited months run from): 3 tiers, service.
  - notice_months (parameter): 3 tiers, service.
  - autopay_months (parameter): 3 tiers, service.
  - service_length_months (parameter): 3 tiers, service.
  - Tier values are pairwise distinct for every kind. Shortfall gives refund_review_months / 0.5·review_extension_months / review_extension_months, for example 24/6/12 for GD and 12/3/6 for RNS. The other ladders are 3/1/0, 2/1/0 and 2/1/0.
  - Every tier is a rule sentence and a branch of its binding.
  - Fall-through equals baseline: the length is review_extension_months, the others are 0.
  - The baseline rule ("The extension is review_extension_months of the deposit's kind, counted from the recorded review date.") is a rule sentence and self-sufficient. It gives 12 for business kinds.
- **anniversary_interest**: 4 factors, 2 parameter / 2 method.
  - opening_year_rate (parameter), 3 tiers, own records.
  - calendar_year_split (method), 3 tiers.
  - interest_cash_base (method), 3 tiers.
  - satisfactory_months (parameter), 3 tiers, multi-source disjunction, service.
  - Finding **F-G5**: calendar_year_split's fall-through is "the whole year earns the closing year's rate", but its `baseline` (and baseline.rule) is interest_rate_annual. These coincide only when the anniversary falls in 2026 or later. For an anniversary in 2025 the fall-through selects rate_2025 while the baseline states interest_rate_annual. The fall-through tier is not the baseline. Whether this costs a task depends on that task's world.
- **recalculated_requirement**: 5 factors, 4 parameter / 1 method.
  - recent_load_basis (method), 3 tiers, multi-source (bill means and billing demand), service.
  - payment_record_multiple (parameter), service.
  - service_length_cut (parameter), service.
  - notice_multiple_load (parameter), service.
  - growth_phase_in (parameter), own records combined with the basis tier.
  - All tiers are distinct, stated in the rule and implemented. Fall-throughs equal baselines.
- **additional_installment**: 5 factors, 4 parameter / 1 method.
  - interest_toward_raise (method), service via reversals.
  - plan_size_count (parameter), multi-source (amount vs held cash, plus service reversals).
  - autopay_extra_installments (parameter), service.
  - service_extra_installments (parameter), service.
  - front_loaded_installment (parameter), service.
  - All tiers distinct and stated. Fall-throughs equal baselines.
- **new_agreement_requirement**: 6 factors, 4 parameter / 2 method.
  - short_history_estimate (method), service.
  - sister_load_trend (method), multi-source (means and kWh), service.
  - premise_heating_adjustment (parameter), multi-source (both premises), service.
  - customer_record_multiple (parameter), service.
  - established_sister_cut (parameter), service.
  - good_payment_refund_relief (parameter), own deposits.
  - All tiers distinct (1.3/0.8/1; −0.5/+0.5/0; 0.25/0.1/0; 0.5/0.25/0). Fall-throughs equal baselines. Baseline rule self-sufficient: multiple × default bill.
- **opening_installment**: 4 factors, 3 parameter / 1 method.
  - deposit_size_plan (parameter), multi-source (required amount and service reversals), service.
  - notice_plan_cut (parameter), service.
  - multi_site_extra (parameter), service.
  - stage_opening_method (method), service status.
  - All tiers distinct. Fall-throughs equal baselines.
- **review_refund**: 4 factors, 2 parameter / 2 method.
  - closing_opening_rate_tier (parameter).
  - closing_period_rate_method (method).
  - closing_interest_base_method (method).
  - closing_months_tier (parameter), multi-source, service.
  - Finding **F-G6**: closing_period_rate_method's fall-through is "the closing period earns the closing rate for a whole year". Its `baseline` and baseline.rule are "interest_rate_annual ... by days over days_in_year". These differ for every closing period not exactly 365 days long, and for every refund dated before 2026. A fall-through that gives a period longer than a year only one year's interest is also a treatment no utility publishes for a deposit held longer. This is an observation on realism, not demonstrable in either task.
- Every policy has 4 to 6 factors, at least 2 parameter and at least 1 method. Every ladder has 3 pairwise-disjoint tiers, and every tier is stated in the rule. Labels are honest: the method tiers change which quantity, mean, split or anchor enters the computation, and the parameter tiers change a number.
- The service-difficulty factors read `service_*` rows. These belong to the `service_billing_and_collections` difficulty.
- Realism: the ladders weigh payment record, notices, autopay, tenure, load trend and premise heating. Each is something a utility credit department plausibly weighs, and no tier condition holds of every customer who reaches the write. The months-earned lapse reduction of statutory interest is unusual but published by some commissions. No ladder is struck out on realism.

### findings

- **F-G1. SOURCE-POLICY (charter-global). The two sentences on the 1 January boundary in `deposit_ext_anniversary_interest` contradict each other.**
  - Symptom: one rule assigns 1 January of the anniversary's year to both rates.
  - Root cause: the calendar-year rate sentence ("rate_2025 for 2025 and interest_rate_annual from 2026 on") puts 1 January in the closing year. The split sentence ("the days from its start to 1 January ... earn the earlier year's rate"), read with "Days are counted from the start date to the end date, the start date not counted", counts 1 January at the earlier rate. Compute follows the latter.
  - Bears on: task 0, whose year runs 2025-10-07 → 2026-10-07. The consequence is demonstrated in `0.md`.
- **F-G2. SOURCE-TASK candidate (charter-global gap). The recorded average monthly bill on a recalculation is unstated.** `deposit_ext_recalculated_requirement` never says which quantity is the deposit's average monthly bill, and the target tool requires one. Readings are the billing basis or base `deposit_msr_average_bill` (twelve-month mean). Bears on task 0, where the two differ. Demonstrated in `0.md`.
- **F-G3. SOURCE-POLICY (rule/compute). The refund's split day count disagrees with its compute.** `deposit_ext_review_refund` says "its days before 1 January of the refund date's year", while compute counts through 1 January. Bears on task 1. Per `1.md`, the scored refund is the same under both counts there, so it is recorded as an observation-level defect for that task.
- **F-G4. SOURCE-POLICY (undeclared override). `deposit_ext_additional_installment` changes base `deposit_recalculation`'s "the difference due" without naming it in `overwrite`.** The held basis can include credited interest, while base fixes the amount due as the recalculated amount less the held cash. Bears on task 0. Demonstrated in `0.md`.
- **F-G5. SOURCE-FACTOR structure. `calendar_year_split`'s fall-through is not its baseline before 2026.** Bears on any task whose anniversary falls before 2026. Task 0's anniversary is 2026-10-07, so there the fall-through equals the baseline. Checked in `0.md`.
- **F-G6. Observation. `closing_period_rate_method`'s fall-through is not its baseline, and caps periods over a year at one year.** Task 1 takes the split tier, so the fall-through is not exercised there.
- **Observations O-G1 .. O-G12** as stated in the sections above: unclaimed event types; NOW-anchored windows; customer-wide disconnection counting; unstated later installments; looseness of `refund_relief` / `sister_account`; `other_sites_billed` counting bills; docstring "after"; "handling date" in conditions; the unjustified E5 fallback; waiver-counting variance; the base fully-secured trigger on re-assessed deposits; the undeclared installment schedule for GD/LP.

## closing_checklist

Written 2026-10-07, about 21:34Z, after both task comparisons. The charter-global section above was frozen before any reveal and is left untouched.

- **Files.** `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside them. This is the first revision; there is no older revision.
- **Not all comparison sections carry a PASS.**
  - Task 0: SOURCE-POLICY RED (F-G1, F-G4) and SOURCE-TASK RED (F-G2). Its problem tree and factors PASS.
  - Task 1: PASS on all four relationships.
- **Coverage and scopes.**
  - Coverage: `charter_scope` of task 0 = {failed_review_extension, anniversary_interest, recalculated_requirement, additional_installment}. Task 1 = {review_refund, opening_installment, new_agreement_requirement}. Together these cover all 7 extended policies.
  - The two scopes are disjoint across each whole tree. Task tools are disjoint.
  - Every uuid8 is independent (§ action_binding_and_uuids).
- **Trees.**
  - Task 0: 3 prerequisites, 2 value_input edges, user write pay_additional_deposit.
  - Task 1: 2 prerequisites, 1 value_input edge, user write pay_deposit_installment.
  - The difficulty-wide graph (E1–E5) is acyclic, and no cross-task reference exists.
- **Factors.** Every computation of both tasks has 4 to 6 factors, ≥ 2 parameter, ≥ 1 method, ≥ 1 multi-source factor and ≥ 1 service cross-difficulty factor per task. Every factor bears weight against an honest baseline on its task's world, and every all-baseline fallback differs from gold. Structural F-G5 and F-G6 are not exercised by either task.
- **Gates.** This difficulty's instantiation gates were run by the coordinator on the audited form; the snapshot is in § charter_global_frozen. This audit did not re-run them, because the artifacts are unchanged (hashes equal MANIFEST). check_traceability stays deferred until the KB is published.
- **Difficulty result:** **NOT PASSED** at the source layer. Task 0 is RED on policy self-consistency and on unique solution, and F-G1, F-G2 and F-G4 are charter-level defects. Task 1 passes.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-07, about 22:41Z (shell clock), before any round-2 GT was revealed. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5). Round-1 text above is left untouched.
- Freeze hashes, verified equal to the round-2 MANIFEST:
  - `deposit.extended.yaml` c31c9148c7b8619a1b52024d9ac53d6c47a6e0ff8f7bd48406d9f73548aba934
  - `task_tools.py` 716d3b68508e33f4bca06bea481d3956eb31f423623f0716ab5347e917363478
- Both hashes changed since round 1, so every charter-global section is re-derived in full below rather than carried forward.
- Fields read: blueprint (unchanged), the new charter and tools in full, and the rebuilt views. `diff` of the views against `round1/` shows:
  - task 0: the prior interest credit 422.55 → 422.60 and held_amount 6207.55 → 6207.60
  - task 1: the prior credit 177.11 → 177.13, held_amount 2847.11 → 2847.13, and one changed persona sentence
- Masked and unread: the same fields as in round 1. Round-2 `tasks/*.json` were not opened. No search touched `tasks/` or `/tmp`.
- Base-section `diff` against `blueprint/products/deposit.yaml`: still verbatim.

### policy_conflict_scan (r2)

- The same seven policies, targets, owners and triggers as in round 1. The same-day review / anniversary / recalculation structure still resolves the same way: the review outcome comes first; a pass leads to a refund with no anniversary credit and no recalculation; a fail leads to extension → interest → recalculation.
- The two installment policies still have disjoint objects, and the two refund paths are unchanged.
- O-G1 (claimed event types) persists. The blueprint is frozen and cannot be fixed inside this difficulty, so it remains documented.

### rule_compute_equivalence (r2)

- **failed_review_extension.**
  - The rule now anchors every window, date span and status on "the decision day, the day on which the review is decided". Compute anchors on NOW, so they are equivalent. **O-G2 closed** for this policy.
  - O-G3 (one disconnected agreement adds "one when any" rather than "one for each") persists. It is only used in a `> 0` test, so it remains an observation.
- **anniversary_interest.**
  - The split sentence now reads "its days up to and including 31 December of that earlier year earn the earlier year's rate and its days from 1 January of the anniversary's year on earn the closing year's rate". This agrees with "rate_2025 for 2025 and interest_rate_annual from 2026 on" and with "Days are counted from the start date to the end date, the start date not counted".
  - Compute `days_prior_year = MX(0, DAYS(year_start, closing_year_start) − 1)` matches: for a 2025-10-07 start it gives 85, which is 8 Oct through 31 Dec.
  - **F-G1 closed.**
  - Payments and lapses are now explicitly counted "over the interest_year_months months ending on the day the credit is booked, which is the anniversary". This matches the NOW-anchored compute (O-G2 closed here).
- **recalculated_requirement.** The new sentence "The billing basis so chosen, rounded to the cent, is the average monthly bill recorded on the deposit with the recalculated requirement." names the recorded figure. **F-G2 closed.** Compute is otherwise unchanged and matches.
- **additional_installment.**
  - New sentence: "After the installment paid first, the rest of the additional amount due is paid in equal installments over the remaining number ... each due 30 calendar days after the previous one." **O-G4 closed.** It is not computed and not scored.
  - Compute is unchanged and matches.
- **new_agreement_requirement.**
  - The sister is now "another agreement in active status on the same rate schedule that carries, or carried, the customer's deposit of the same kind". Refund relief now reads the deposit "of that kind on the sister agreement". **O-G5 closed in the rule.**
  - Compute `sister_account` is pinned to `F('service_account_id')`, the agreement of the focal same-kind deposit. That reflects the "carries, or carried" restriction.
  - `heating_factor` and `established_cut` now key on `estimate == sister_basis or estimate == sister_mean_year`. That is equivalent to "drawn from a sister agreement" except in the degenerate case where the default happens to equal a sister mean. This closes round-1 task-1 obs 3: substituting the estimate baseline now also drops the heating factor and the established cut.
- **opening_installment.** The rule now counts "three or more regular bills ... issued on the customer's agreements in the sites_window_months month". This is the same quantity the compute counts. **O-G6 closed** (rule aligned to compute).
- **review_refund.**
  - The split sentence now reads "up to and including 31 December of that earlier year". Compute `closing_days_before_new_year = MX(0, DAYS(start, refund_year_start) − 1)` matches. **F-G3 closed.**
  - A new tier gives no closing interest when the deposit is held fewer than interest_min_holding_months whole months. That is base's inherited rule, now carried in the ladder. Compute `deposit_held_months` implements it.

### action_binding_and_uuids (r2)

- The tool set, the uuid8s and the `(target_tool, computes)` claims are unchanged. Each pair is claimed by one policy, and the uuid8s are independent.
- Function bodies were re-read. No gate, status or date check was added; only the docstrings changed.
- Docstrings checked:
  - `extend_deposit_review` now says "because its satisfactory payment review was not passed"; `refund_deposit_by_check` says "on a passed satisfactory payment review"; `require_additional_deposit` now says "with the new required amount" (the "so that the additional amount can be paid" wording is gone).
  - Remaining hits for "first" and "then" are ordinal or receipt wording only.
  - **O-G7 closed.**

### prerequisite_graph (r2)

- Edges E1–E5 have the same problems, kinds, gates and resolved_by as round 1, and the graph is acyclic.
- **E5 is now `form: state`** with no `fallback_reason`, and its sentence is "... has been passed on its refund review date stands refunded". **O-G9 closed.**
- Conditions now read "which is the day the credit is booked" (E1) and "up to and including the recalculation date" (E2). **O-G8 closed.**
- Every `policy_source` is verbatim in its own rule (checked against the text above).

### prerequisite_sentences (r2)

- E1–E4 are unchanged and still pass the four points. Their unique writers and single-reading derivations are as in round 1.
- **E5:** "The deposit required on a new agreement is fixed only after any deposit of the customer whose satisfactory payment review has been passed on its refund review date stands refunded."
  - Connective "only after". The waited-on state is record-visible ("stands refunded": status refunded). No tool or id. Scope equals the condition.
  - Unique writer: `refund_deposit_by_check` is the only write in this difficulty that sets a deposit refunded.
  - Derivation: find the held deposit whose review date is reached and whose review passes, then find the rule that refunds a passed deposit (review_refund). Single reading.
- No depended-on rule restates any sentence. No new undeclared cross-problem order was found in the seven rules.

### override_declarations (r2)

- **additional_installment adds three overwrite entries.**
  - (a) `deposit_recalculation` "When the recalculated amount exceeds the held cash by more than recalculation_increase_threshold_pct of the held cash, the deposit returns to assessed with the new required amount and the difference due within additional_deposit_due_days." is replaced by "Where a recalculation has returned the deposit to assessed with a raised required amount, the difference due within additional_deposit_due_days is this additional amount due, the held basis taking the place of the held cash." **F-G4 closed**: the amount due is now declared.
    - New observation **N-1**: the superseded clause is the whole base sentence, threshold included, but the replacement keeps only the "difference due" half. Under a global reading of overwrites, `recalculation_increase_threshold_pct` survives in no sentence. Under the policy-scoped reading this charter uses elsewhere, the threshold still governs `deposit_additional_requirement`, which is the recalculation policy's subject. That is a dropped-branch hazard in a world where the recalculated amount exceeds the held cash by between 0 and 20%. Task 0 is not such a world: 13694 is far above both 5785 and the held basis.
  - (b) `deposit_installments_and_security` "The deposit becomes held on the day deposit_msr_cash_received reaches the required amount, or ... instrument ..." is replaced by a sentence scoped to "A deposit returned to assessed by a recalculation". **O-G11 closed** for re-assessed deposits.
    - Observation **N-2**: the same scope question as N-1. Read globally, the base held-trigger for every other deposit would be dropped. Read per policy (the reading consistent with the rest of the charter), it is not. No scored quantity depends on it.
- **opening_installment** adds the `deposit_assessment_rule` "The first installment is due ... and later installments under installment_schedule." with replaced_by "... each later installment of a deposit on a new agreement is due 30 calendar days after the previous one, whatever the installment_schedule of its kind." **O-G12 closed.**
- All other round-1 conclusions stand. Each was re-checked against the unchanged base-ref sentences: extension, interest, recalculation, new_agreement and refund.
- O-G10 (the extension's waiver-credit count vs base's "charges later waived") persists. It remains an observation.

### factor_ladders (r2)

- Factor ids, counts, labels and tier values are unchanged:
  - extension 5 (4 parameter / 1 method)
  - interest 4 (2 parameter / 2 method)
  - recalculation 5 (4 parameter / 1 method)
  - additional installment 5 (4 parameter / 1 method)
  - new agreement 6 (4 parameter / 2 method)
  - opening installment 4 (3 parameter / 1 method)
  - refund 4 (2 parameter / 2 method)
- **anniversary_interest.**
  - `baseline.rule` is now "The Commission sets the deposit interest rate for each calendar year ... The interest for a completed year is the cash received on the deposit times the Commission's deposit interest rate for the calendar year of the anniversary, rounded to the cent." Both sentences are in the rule and the baseline is self-sufficient.
  - calendar_year_split's baseline is now `closing_rate`, equal to its fall-through "the whole year earns the closing year's rate". **F-G5 closed.**
- **review_refund.**
  - closing_period_rate_method's ladder is now: split / held fewer than interest_min_holding_months, giving 0 / otherwise days at the closing rate over days_in_year.
  - The baseline is `refund_year_rate * closing_days / days_in_year`, equal to the new fall-through. The old one-year cap on longer periods is gone. **F-G6 closed.**
  - The three tiers are distinct: a split rate, zero, and days at the closing rate. The new tier is a base rule.
- New observation **N-3**: `opening_year_rate.baseline` and `closing_opening_rate_tier.baseline` remain `interest_rate_annual`, while each baseline rule now takes the closing (anniversary or refund) year's rate and has no opening rate. The two coincide whenever the closing year is 2026 or later. Both tasks are 2026, so there is no consequence here.
- New observation **N-4**: the sister restriction in new_agreement ("that carries, or carried, the customer's deposit of the same kind") ties the bill-estimate source to deposit history. That is an odd criterion for estimating a bill, but not demonstrably one no utility applies, so it is recorded as an observation.

### findings (r2)

- Round-1 REDs: **F-G1, F-G2, F-G3, F-G4 closed in the charter.** Per-task confirmation is in `0.md` / `1.md` revision_2. Structural **F-G5 and F-G6 closed.**
- Round-1 observations: **O-G2, O-G4, O-G5, O-G6, O-G7, O-G8, O-G9, O-G11 and O-G12 closed.** O-G1, O-G3 and O-G10 persist as observations.
- New charter-level observations: **N-1 to N-4** above. None has a consequence on either task's world.

### closing_checklist (r2)

Written 2026-10-07, about 22:43Z (shell clock), after both r2 comparisons.

- **Files.** `0.md`, `1.md` and `_difficulty.md` each carry revision_2. Round-1 text is preserved unchanged above each revision_2 heading.
- **Round-1 REDs** (task 0: F-G1, F-G2, F-G4) are **all closed**. Each was confirmed against the round-2 charter, world and GT. F-G3, F-G5 and F-G6 are closed as well.
- **New defect: task 1 SOURCE-CHAIN RED.** It was introduced by the round-2 persona rewrite, which turned round-1 observation 4 into a short-circuit of edge E4. See `1.md` revision_2 findings §1.
- **Regression check on values.** Task 0's moved values (interest, amount) are exactly the ones F-G1 requires. Task 1's refund moved only through the seeded prior credit. Nothing else regressed in values, trees or factor weights.
- **Coverage.** Coverage, disjoint scopes, tool closure and uuid8 independence are unchanged and hold. Trees: task 0 has 3 prerequisites and 2 value_input edges; task 1 has 2 prerequisites and 1 value_input edge. Each tree has a user write and no cycle.
- **Factors.** Factor bounds and weight hold on both worlds.
- **Gates.** The coordinator's round-2 gate snapshot is all green and was cited, not re-run. check_traceability is deferred.
- **Open charter observations** (not grounds for rework): O-G1, O-G3, O-G10 and N-1 to N-4.
- **Difficulty result r2: NOT PASSED.** Task 0 passes; task 1 is RED on the problem tree (SOURCE-CHAIN).

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-08, about 00:34Z (shell clock), before any round-3 GT was revealed. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5). Earlier revisions are untouched.
- Hashes, all equal to the round-3 MANIFEST:
  - `deposit.extended.yaml` 0905709dfe09f7c506aa7d758791ce4efe2862f36f0c8715f45de21d653ffcc1 (changed)
  - `task_tools.py` 716d3b68508e33f4bca06bea481d3956eb31f423623f0716ab5347e917363478 (unchanged since r2)
  - task_0 view 6c2fcdba… (unchanged)
  - task_1 view afef73f7… (changed)
- **Re-derivation basis.**
  - The charter hash changed, so the charter-global checks were redone. No copy of the r2 charter is in my read domain, so this was done by targeted re-reading against the r2 text quoted in revision_2.
  - The file still has 2385 lines and every extended policy starts on the same line (1017/1187/1363/1576/1788/2054/2209).
  - Every compute binding that carries a scored tier or a round-1/round-2 finding was re-read and is byte-identical to the r2 text quoted above: days_prior_year, period_rate, closing_days_before_new_year, closing_period_rate, extension_length, clean_credit, phase_share, held_basis, installments, other_sites_billed, sister_account, heating_factor and refund_relief.
  - Every prerequisite sentence (E1–E5) and every r2 closing sentence is still present.
  - Edits found: (a) the four `deposit_ext_additional_installment` overwrite replacements and their rule copies; (b) `opening_year_rate.baseline` and `closing_opening_rate_tier.baseline`.
  - The base section is still verbatim with the blueprint. The tool module is unchanged, so § action_binding_and_uuids (r2) carries forward on the unchanged hash.
- Masked and unread: as before. Round-3 `tasks/*.json` were not opened.

### checks (r3)

- **N-1 (closed).**
  - The `deposit_recalculation` replacement now restates the threshold: "When a recalculated amount exceeds the held cash by more than recalculation_increase_threshold_pct of the held cash, the deposit returns to assessed with the raised required amount, and the difference due within additional_deposit_due_days is this additional amount due, the held basis taking the place of the held cash."
  - The threshold survives under any scope reading of overwrites.
  - Residual observation **N-5**: the closing clause "the held basis taking the place of the held cash" can be read as also replacing the held cash in the threshold test, not only in the amount due. The two readings differ only where the recalculated amount lies between 1.2 × held cash and 1.2 × held basis.
- **N-2 (closed).** The fully-secured replacement now states the general rule ("A deposit becomes held on the day the cash received on it reaches its required amount, or on the day an accepted instrument ... is lodged") and adds the re-assessed exception. No branch is dropped.
- **N-3 (closed).**
  - `opening_year_rate.baseline` is now `closing_rate` and `closing_opening_rate_tier.baseline` is now `refund_year_rate`. Each now equals what its baseline.rule states (one rate, the closing or refund year's).
  - Both fall-throughs ("otherwise interest_rate_annual") apply only to periods beginning in 2026 or later. For those the closing year is also 2026 or later, so each fall-through equals its baseline.
- **N-4** is kept by the reworker. It remains an observation, with no consequence on task 1's world.
- **O-G1, O-G3 and O-G10** persist as observations.
- Every other r2 charter-global conclusion carries forward unchanged: conflict scan, rule/compute equivalence, prerequisite graph and sentences (E1–E5 all state form, acyclic, unique writers), override declarations (now with N-1 and N-2 closed), and factor ladders (counts, labels and tiers unchanged).

### closing_checklist (r3)

Written 2026-10-08, about 00:35Z (shell clock), after both r3 comparisons.

- **Files.** `0.md`, `1.md` and `_difficulty.md` each carry revision_3. Revisions 1 and 2 are preserved unchanged.
- **Round-2 RED** (task 1 SOURCE-CHAIN, cafe persona line): **closed**.
- **Round-2 charter observations:** N-1, N-2 and N-3 closed. N-4 kept (observation). New residual observation N-5 (scope of "the held basis taking the place of the held cash") has no consequence on either world.
- **No regression.**
  - Task 0's GT, tree and factor figures are identical to r2.
  - Task 1's GT, tree and factor figures are identical to r2. Its persona changed only in the cafe line.
- **Structure.**
  - Coverage: the 7 extended policies split 4 / 3 with disjoint scopes.
  - Tools are closed, and the uuid8s are independent and unchanged.
  - Trees: task 0 has 3 prerequisites and 2 value_input edges; task 1 has 2 prerequisites and 1 value_input edge. Each has a user write. The difficulty graph is acyclic.
- **Factors.** Every computation has 4 to 6 factors (≥ 2 parameter, ≥ 1 method), with multi-source and service cross-difficulty factors per task. Every factor bears weight against an honest baseline, and every fallback differs from gold.
- **Gates.** The coordinator's round-3 gate snapshot is all green and was cited, not re-run. check_traceability stays deferred until the KB is published.
- **Open observations** (not grounds for rework): O-G1, O-G3, O-G10, N-4 and N-5.
- **Difficulty result r3: PASSED at the source layer.** Both tasks PASS all four relationships.
