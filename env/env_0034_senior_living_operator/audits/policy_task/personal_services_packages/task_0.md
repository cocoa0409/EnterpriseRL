# Policy-task audit — personal_services_packages / task 0

## source_derivation_frozen

- Auditor: independent policy-task auditor (round 1). Freeze time: 2026-10-05T09:10Z (wall clock), before any task GT was revealed (task 0 and task 1 both frozen before either reveal).
- Source: `env/env_0034_senior_living_operator/audits/_views/policy_task/personal_services_packages/task_0.view.json` sha256 26690d9680f05e92023f300286df82689da30336e8d450a688596f09cc392bf9 (fields frozen_time, user_scenario, initial_state only); charter and tool hashes as in `_difficulty.md` § charter_global_frozen.
- Masked and unread: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure, worklog.
- contamination_disclosure: none. The brief carried no scored value; no recursive search touched `tasks/` or `audits/`.

World (frozen_time 2026-10-05 10:20 CDT): customer Eleanor Whitfield (7fa85340…), representative Karen Whitfield-Ames, representative_authority durable_poa; assisted residency 3080556d… status on_leave, absence_reason rehab_facility, absence_start_date 2026-09-24, absence_return_date null; entrance agreement 147cb91a… LifeChoice 50% Refundable Plan, status occupied (contract_type fee_for_service per `products/entrance.yaml`); closed IL residency 91a77fcc… (moved in 2019-09-03); services plan df70605f… Personal Services Companion Package, active, residence_category assisted, effective 2024-03-01, prior suspension 2026-03-01..2026-04-30, hours_available 8.0, account_balance 521.10.

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences (Edge A), § override_declarations, § factor_ladders.
- Undeclared overrides: none found charter-wide, so no second answer to demonstrate here. The declared overrides in this tree change the scored values against base: under base services_hours_and_billing + services_disputes_and_corrections, the visit SO-2609-0389 would be re-rated at ceil(70 min to 15) = 75 min = 1.25 h, x1.25 weekend = 1.5625 h, so the correct charge would be (1.5625 - 0.5 drawn) x 44.00 = 46.75 and the dispute credit 41.25; and under base services_suspension the rolling-12 quota (2 months recorded Mar-Apr 2026, Companion max 2) leaves 0 months. Both base sentences are named in the respective `overwrite` lists, so these are declared replacements, not second readings.
- Handling time: the credit is computed on the opening world (it has no prerequisite); the suspension months are computed on opening world + the credit row. Neither reads a later write.
- Real-world waits: none. Every input is a seeded record (orders, ledger, AL residency, EFA, plan) or the effect of the credit write; the customer's choice ("as long as her package allows, starting as soon as possible") is stated in the persona. The suspension starts in a future month but nothing in the tree waits for it.
- O-2 (past_due tariff vs ledger row) checked on this world: the 2026-10 package fee row b0bd66a8 is 359.00 = tariff, so the two readings agree.
- O-1 checked: the latest delivered-visit hourly charge (0cf232c7, SO-2609-0389) is in fact over-billed, so compute's unconditional pick and the rule's selection coincide.

### problem_chain

Root problem (the customer's only ask): suspend the Companion package "for as long as her package allows, starting as soon as possible" — services_ext_suspension_months, write sign_services_suspension_89d6021d (owner user).

Walk:
1. Root rule prerequisite sentence: "The number of months a suspension may run is fixed only after every hourly charge on the plan that its visit record shows billed on more time than was delivered carries a service dispute credit referencing it."
2. Hourly charges on the plan (services_ledger):
   - 6b6ff846 SO-2607-0677, 1.0 h, 44.00, posted 2026-07-29 — already carries credit 5ff3de24 (service_dispute, 44.00, source_entry_id 6b6ff846, posted 2026-08-03). Satisfied.
   - 0cf232c7 SO-2609-0389, 2.0 h, 88.00, posted 2026-09-21. Order SO-2609-0389: booked companion_visit 2026-09-19 (Saturday), scheduled_hours 2.0; completion row actual_minutes 70. Billed on the order: draw 4bf2aa6c 0.5 h + this charge 2.0 h = 2.5 h (= 2 h x 1.25 weekend) against 70 minutes delivered. No services_credit row has source_entry_id 0cf232c7. NOT satisfied at the opening.
3. The policy whose rule writes such a credit: services_ext_short_visit_credit ("An hourly charge for a delivered visit that the visit record shows was billed on more time than the visit supports is corrected by the desk ... posted as one service dispute credit referencing that hourly charge"), write post_services_visit_credit_5ef485c2 (owner agent). Its own prerequisite list is empty and its rule carries no prerequisite sentence.

Derived tree: services_ext_short_visit_credit -> services_ext_suspension_months, one edge, kind value_input (the credit enters past_due). n = 1 prerequisite problem; value_input edges 1 >= max(0,1). Acyclic. Topological order: credit, then suspension. One owner=user write (the suspension). Isomorphic to the declared `prerequisite` of the charter.

Load-bearing run (skip the credit, replay the rest): past_due = 521.10 - 359.00 = 162.10 >= 100 -> standing_deduction 2 -> months = 2 + 2 + 1 - 2 - 1 = 2, against 3 with the credit (below). The edge bears weight.

No parallel edges. No wait: the credit is a desk write on seeded records. Tools: no body checks a prerequisite (`_difficulty.md` § action_binding_and_uuids).

The customer raises only the root problem. Persona lines touching the prerequisite are conditional on the agent: "If the agent asks about her account, you say you know a few extra charges from her September statement are still unpaid" and "If the agent tells you something on her account has to be corrected or credited before the hold can be worked out, you say that is fine, please go ahead". Neither names or steers toward the credit unprompted. The persona closes on the signed hold ("Once the agent confirms the hold is recorded, you thank them and end the call"), the last gold action.

Stray state_due obligations on this world: the only cancellation, SO-2609-0436 (companion 2026-09-26 13:00), was received 2026-09-24 08:40 — two calendar days before, band 0 under services_ext_missed_visit_hours (and >= 24 h notice under base), so no hours entry is owed; after the credit no other delivered-visit hourly charge is uncredited.

### task_independent_derivation

Identity: caller Karen gives DOB 1937-11-03 and SSN last4 8724 -> 2 matches on Eleanor's profile; representative_authority durable_poa authorises her to sign (base services_enrollment_eligibility signer sentence; tool docstring "as the resident or the resident's financial agent").

Step 1 — credit (handling time: opening world). Act now (posted 2026-09-21, 14 days into the 60-day window; desk-initiated per rule).
- visit_ref: latest delivered-visit hourly charge = 0cf232c7 (2026-09-21) over 6b6ff846 (2026-07-29). charged 88.00, month 2026-09.
- booked 2.0 h = 120 min; delivered 70 min; companion_visit; 2026-09-19.
- billed_minutes: 70 < 120 -> round down to 15: 60. base_hours = max(1.00, companion minimum 1.0) = 1.00.
- surcharge: 2026-09-19 is a Saturday, not in the holiday calendar (Labor Day 2026-09-07) -> Companion weekend_surcharge_pct 25.
- relief: AL absence rehab_facility starting 2026-09-24 = 5 days after the visit -> >3 and <=7 -> relief_long_factor 0.8.
- billable_hours = RND(1.00 x 1.25 x 0.8, 2) = 1.00.
- covering: drawn on order 0.5 (4bf2aa6c); month_end expiry in 2026-09 = 0.25 (e397f9df) > 0 -> covering = 0.75 (the 2026-09 restore 759e9bed 0.25 is passed over because the expiry tier takes precedence).
- rerated_hours = 1.00 - 0.75 = 0.25.
- overage rate: EFA 147cb91a occupied, LifeChoice 50% Refundable = fee_for_service -> 44.00 - 2.00 = 42.00. rerated_charge = 10.50.
- prior service_dispute credits in the 12 months before 2026-10-05: 5ff3de24 (2026-08-03) -> exactly one -> goodwill 10.00.
- credit = RND(min(88.00, 88.00 - 10.50 + 10.00), 2) = 87.50.
- Write: post_services_visit_credit_5ef485c2(services_plan_id=df70605f-04c3-4f42-9b1d-889d1b3aeb30, source_entry_id=0cf232c7-66ac-4b99-98ba-3eb66cdc9088, credit_reason=service_dispute, billing_period=2026-09, amount=87.50). Effect: account_balance 521.10 -> 433.60.

Step 2 — suspension (handling time: opening world + credit). Act now.
- First suspended month: first month whose first day is at least 7 days after 2026-10-05 -> 2026-11-01 (2026-10-01 already past; base notice: last day to request for November is 2026-10-25 >= 2026-10-05). Absence >= 14 days per persona ("well over that").
- max_base: Companion max_suspension_months_per_12m 2.
- absence_extra: AL residency on_leave, reason rehab_facility -> medical_extra_on_leave 2.
- tenure: effective 2024-03-01 to 2026-10-05 = 31 whole months -> >= 24, < 48 -> +1.
- past_due: charges = fees 4 x 359.00 (Jul-Oct) 1436.00 + hourly 44.00 + 88.00 + a la carte 74.10 = 1642.10; reductions = payments 3 x 359.00 = 1077.00 + credits 44.00 + 87.50 = 1208.50; balance 433.60 (= plan account_balance after the credit); less current-month fee 359.00 -> 74.60 -> above 0, below 100 -> deduct 1.
- previous suspension 2026-03-01..2026-04-30 = 2 months; ended 2026-04-30, 5 whole months before the request (>= 3, < 12); did it lie within a medical absence? AL absence began 2026-09-24, after the suspension -> no -> half, floor(2/2) = 1.
- months = max(0, 2 + 2 + 1 - 1 - 1) = 3.
- Write (handed to the customer, owner user): sign_services_suspension_89d6021d(services_plan_id=df70605f-04c3-4f42-9b1d-889d1b3aeb30, first_suspended_month=2026-11-01, suspended_months=3) -> suspension 2026-11-01..2027-01-31.

Contrast on the opening world (no credit): 2 months (2026-11-01..2026-12-31).

Terminal state: ledger gains one services_credit 87.50 against 0cf232c7 (billing_period 2026-09); plan account_balance 433.60; plan suspension_start_date 2026-11-01, suspension_end_date 2027-01-31; status unchanged active.

### factor_weight

Credit (gold candidate 87.50; factor substitutions are one at a time, others recomputed):
| factor | label honest | tier taken / rows | baseline input | value under baseline |
| --- | --- | --- | --- | --- |
| delivered_time_billing | method, yes (floor vs booked vs ceil) | short delivery: book row 702e79f8 2.0 h vs completion 2e7cfe46 70 min | 75 min (ceil) | base 1.25 -> billable 1.25 -> rerated 0.50 x 42 = 21.00 -> 77.00 |
| date_surcharge | parameter, yes | weekend (2026-09-19 Saturday) | 0 % | billable 0.80 -> rerated 0.05 -> 2.10 -> 88.00 (capped) |
| illness_relief | parameter, yes | long tier: AL 3080556d rehab_facility from 2026-09-24 (5 days) — cross-difficulty assisted | 1 | billable 1.25 -> 77.00 |
| covering_hours_rule | method, yes (adds different ledger quantities) | expired tier: e397f9df 0.25 month_end 2026-09 | drawn only 0.5 | rerated 0.50 -> 77.00 |
| entrance_overage_rate | parameter, yes | fee_for_service: EFA 147cb91a occupied — cross-difficulty entrance | 44.00 | 0.25 x 44 = 11.00 -> 87.00 |
| dispute_goodwill | parameter, yes | one prior: 5ff3de24 2026-08-03 | 0 | 77.50 |
- Every factor moves the credit. All-baseline fall-back (ceil 75 min, no surcharge, no relief, covering 0.5, rate 44.00, no goodwill): billable 1.25, rerated 0.75, charge 33.00, credit 55.00 — definite and different from 87.50. Baseline rule alone gives the same 55.00.
- Stamp: no field names an outcome (no "relief tier" / "goodwill tier" field).
- Near-miss: restore 759e9bed (0.25 h, 2026-09) — a reader adding it to covering is excluded by the expiry-first tier; the earlier charge 6b6ff846 (latest-first selection, already credited).
- Survivors: 6 factors (4 parameter, 2 method); multi-source: delivered_time_billing, illness_relief; cross-difficulty: illness_relief (assisted), entrance_overage_rate (entrance).

Suspension (gold candidate 3, on opening world + credit):
| factor | label honest | tier taken / rows | baseline | value under baseline |
| --- | --- | --- | --- | --- |
| medical_absence_extension | parameter, yes | on_leave + rehab_facility on AL 3080556d — cross-difficulty assisted | 0 | 1 |
| time_in_force_extension | parameter, yes | mid tier: effective_date 2024-03-01 (31 months) | 0 | 2 |
| account_standing_deduction | parameter, yes | some past due 74.60 (ledger rows above + credit) | 0 | 4 |
| previous_suspension_count | labelled method — NOT honest (F-1): floor(2 x 0.5) | half tier: plan suspension 2026-03-01..04-30 + AL absence start 2026-09-24 (multi-source, cross-difficulty assisted) | full: 2 | 2 |
- Every factor moves the result. All-baseline fall-back: baseline rule "max_suspension_months_per_12m less the months counted for the plan's most recent recorded suspension ... in full where that suspension ended fewer than window_months whole months before" = 2 - 2 = 0 — definite, different from 3.
- Stamps: none.
- Near-misses: IL residency move-in 2019-09-03 / EFA occupancy 2019-09-03 / profile 2019-04-22 (a reader timing tenure from residency gets >= 48 -> +2; rule says "since its effective date"); plan account_balance 521.10 read as past due (rule subtracts the current-month fee and the credit) -> 2; AL absence start 2026-09-24 vs prior suspension (not within).
- Survivors: 4 factors, 3 parameter, 0 honest method (F-1) — below the 1-method bound for this computation.
- Task-level: multi-source present (illness_relief, delivered_time_billing, previous_suspension_count); cross-difficulty present (assisted, entrance) with the rows seeded (AL 3080556d, EFA 147cb91a).

### Blind verdict before reveal
- Policy self-consistency: PASS for this task (no undeclared override; F-2 does not bear on this tree).
- Problem tree: PASS (one value_input edge, unmet at opening, bears weight, user write present).
- Factors: SOURCE-FACTOR RED via F-1 (suspension computation has no honest method factor); all six credit factors and the four suspension factors bear weight.
- Unique solution: credit 87.50 on 0cf232c7 / 2026-09, then suspension 2026-11-01 x 3 months; no second defensible reading found.

## source_gt_comparison

- Reveal time: 2026-10-05T09:07:29Z, after both task files were on disk (file mtimes: `_difficulty.md` 09:05:29Z, `task_0.md` 09:06:27Z, `task_1.md` 09:07:25Z). The freeze times written in the headers above (09:04Z / 09:10Z / 09:16Z) were estimates written ahead of the actual writes; the mtimes are the authoritative order, and every freeze precedes the reveal. No text of the frozen sections was changed after the reveal.
- GT read: `tasks/personal_services_packages/tasks/0.json` (evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents, solvability_contract, design_rationale).

| item | blind | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | hold as long as allowed, ASAP; Karen (durable_poa) signs | same (request_alignment) | same |
| read set | plan, ledger, orders, AL residency, EFA, IL residency | find_services_plans / _ledger / _orders, find_assisted_residencies, find_entrance_agreements, find_independent_residencies | same |
| now / wait / refuse | act now, both writes | both writes | same |
| step 1 object | charge 0cf232c7 (SO-2609-0389), service_dispute, 2026-09 | same | same |
| step 1 amount | 87.50 | 87.5 | same |
| step 2 | plan df70605f, 2026-11-01, 3 months | same | same |
| owners / order | credit agent, then suspension user | credit (step 9, agent), suspension (step 11, user) | same |
| terminal | credit 87.50, balance 433.60, suspension 2026-11-01..2027-01-31 | same (closure flips_to_true_by: 521.10 -> 433.60) | same |

Closest alternative candidates and their exclusion: (a) the base-rule credit 41.25 / base-quota 0 months — excluded because the extended overwrite names both base sentences; (b) 2 months — excluded because the prerequisite sentence fixes the count only after the credit; (c) restore-based covering (0.75 either way here) — excluded by the expiry-first tier; (d) tenure from 2019 residency (+2) — excluded by "since its effective date".

prerequisite_closure, value against value:
- edge suspension_months -> short_visit_credit, value_input, gate past_due, form state, resolved_by post_services_visit_credit_5ef485c2 — same as derived.
- why_false: charge amount 88.0 / hours 2.0 / actual_minutes 70 / account_balance 521.1 — same rows and values as derived.
- flips_to_true_by: balance 521.10 -> 433.60, past_due 162.10 -> 74.60, deduction 2 -> 1 — same.
- edge_load_bearing: skipped -> 2 months — same as the blind load-bearing run (2).
- resolution_order credit -> suspension — same.

factor_sensitivity vs factor_weight, figure against figure:
- credit: delivered_time_billing 77.00 / 77.00; date_surcharge 88.00 / 88.00; illness_relief 77.00 / 77.00; covering_hours_rule 77.00 / 77.00; entrance_overage_rate 87.00 / 87.00; dispute_goodwill 77.50 / 77.50; baseline_result 55.00 / 55.00. All same.
- suspension: medical_absence_extension 1 / 1; time_in_force_extension 2 / 2; account_standing_deduction 4 / 4; previous_suspension_count 2 / 2; baseline_result 0 / 0. All same.
- Labels: GT factor_trace calls medical_absence_extension and entrance_overage_rate "multi-source"; each reads one record (AL residency status + reason; EFA status + its variant's contract_type). Overstated, but the task has genuine multi-source factors (illness_relief: AL absence + visit order; previous_suspension_count: plan suspension + AL absence), so no bound fails. Observation.
- GT labels previous_suspension_count "method"; the blind audit holds it is a share parameter (F-1).

Verdicts:
- Policy self-consistency: PASS.
- Problem tree: PASS.
- Factors: SOURCE-FACTOR RED (F-1).
- Unique solution: PASS — blind derivation lands exactly on GT.

## findings

1. SOURCE-FACTOR RED — suspension computation has no honest `method` factor.
   - Symptom: services_ext_suspension_months declares one method factor, previous_suspension_count, whose tiers are a share applied to one quantity.
   - Root cause / evidence: `_difficulty.md` § findings F-1 (charter-global; not restated).
   - Demonstrated consequence on this task: the tier taken (half) gives counted_prior = floor(2 x 0.5) = 1; tier full gives floor(2 x 1) = 2; tier none gives floor(2 x 0) = 0 — one formula, three numbers. Counted honestly the step-11 computation has 4 parameter factors and 0 method factors, below the bound of at least 1 method per computation. The factor still bears weight (2 vs 3), so only the label/bound fails.
   - Affected: `services.extended.yaml` services_ext_suspension_months.factors[previous_suspension_count].effect; task 0 computations[1].
   - Relation to previous revisions: first audit round.
2. Observation — illness_relief realism (`_difficulty.md` O-6) bears on this task: the tier taken (0.8 for a rehab admission 5 days after a delivered Saturday visit) changes the credit from 77.00 to 87.50. Recorded as a realism doubt, not a red light.
3. Observation — multi-source labels in factor_trace overstated for medical_absence_extension and entrance_overage_rate (above); no bound fails.

## revision_2

### source_derivation_frozen (revision 2)

- Inputs: `task_0.view.json` 26690d98… (unchanged from round 1), `services.extended.yaml` 6102277b… (changed), `task_tools.py` 94951f4a… (unchanged). Written before reading the round-2 `tasks/0.json`.
- contamination_disclosure: the auditor read the round-1 GT of this task (credit 87.50, 3 months) after the round-1 freeze. Because the world is unchanged, the re-derivation below necessarily re-traces round-1 arithmetic; it is recomputed from the revised rule text and not copied from GT, and the reader should weigh it as a re-check rather than as a fresh blind answer.
- Per-task re-derivation is required because the charter changed (credit and suspension policies both edited).

#### policy_self_consistency (this task)
Charter-global conclusions: `_difficulty.md` § revision_2. Handling time and no-wait arguments of round 1 stand (world unchanged). O-8 not reachable here: the latest fee row b0bd66a8 is posted 2026-10-01 with billing_period 2026-10.

#### problem_chain
Unchanged tree: services_ext_short_visit_credit -> services_ext_suspension_months, value_input on past_due; unmet at opening (charge 0cf232c7 88.00 on SO-2609-0389, 70 of 120 minutes delivered, no credit referencing it; charge 6b6ff846 already credited by 5ff3de24). Persona unchanged. Load-bearing run below.

#### task_independent_derivation
Credit (opening world):
- Selection: latest delivered-visit hourly charge 0cf232c7, 88.00, 2026-09.
- billed minutes: 70 < 120 -> floor to 60 -> 1.00 h (companion minimum 1.0).
- Surcharge: 2026-09-19 Saturday -> 25 %.
- Illness relief: visit cut short (70 < 120) and AL 3080556d rehab_facility absence began 2026-09-24, 5 days after -> relief_long_factor 0.8.
- billable = RND(1.00 x 1.25 x 0.8, 2) = 1.00.
- Covering: 0.5 drawn + 0.25 month_end expiry 2026-09 = 0.75 -> re-rated 0.25 h.
- Rate: EFA 147cb91a occupied, LifeChoice 50% Refundable = fee_for_service -> 42.00 -> re-rated charge 10.50 < 88.00 (so the new "credited nothing" sentence does not apply).
- Goodwill: credit 5ff3de24 posted 2026-08-03, 2 whole months before 2026-10-05 (< 12) -> one -> 10.00.
- Credit = min(88.00, 88.00 - 10.50 + 10.00) = 87.50 -> post_services_visit_credit_5ef485c2(df70605f…, 0cf232c7…, service_dispute, 2026-09, 87.50).
Suspension (opening + credit):
- First month 2026-11-01 (first month whose 1st is >= 7 days after 2026-10-05).
- max 2 (Companion); absence +2 (on_leave, rehab_facility); tenure 2024-03-01 -> 2026-10-05 = 31 whole months -> +1.
- past_due: charges 1642.10 - reductions (1077.00 + 44.00 + 87.50) = 433.60; current-month fee on the ledger: b0bd66a8 359.00 posted 2026-10-01 for 2026-10 -> 74.60 -> deduct 1.
- Previous suspension 2026-03-01..2026-04-30 (2 months), ended 2026-04-30; whole months to 2026-10-05: 5 (a month elapses on the 30th of each later month; 2026-10-30 not reached). Not within the AL absence (began 2026-09-24). 5 >= 3 and < 12 -> tier 2, look-back 6 months: months that ended fewer than 6 whole months before the request: April (ended 2026-04-30, 5) counted; March (ended 2026-03-31, 6 whole months by 2026-09-30) not -> 1 (compute MN(2, 6 - 5) = 1).
- Months = max(0, 2 + 2 + 1 - 1 - 1) = 3 -> sign_services_suspension_89d6021d(df70605f…, 2026-11-01, 3).
- Opening-world contrast (no credit): past_due 162.10 -> deduct 2 -> 2 months. Edge bears weight.

#### factor_weight
- Credit: delivered_time_billing baseline -> 77.00; date_surcharge -> 88.00; illness_relief -> 77.00; covering_hours_rule -> 77.00; entrance_overage_rate -> 87.00; dispute_goodwill -> 77.50; all-baseline 55.00. All differ from 87.50. illness_relief now multi-source on the cut-short condition (order book vs completion) plus the AL absence.
- Suspension: medical_absence_extension -> 1; time_in_force_extension -> 2; account_standing_deduction -> 4; previous_suspension_count baseline MN(2, 12 - 5) = 2 -> 2; all-baseline 2 - 2 = 0. All differ from 3.
- previous_suspension_count bears weight (1 vs 2) but remains mislabelled (`_difficulty.md` revision_2 F-1): on this world tier 2 gives MN(2, 6 - 5) = 1 and tier 3 would give MN(2, 12 - 5) = 2 — the same counting with a 6- vs 12-month window.
- Near-misses unchanged (2019 residency/EFA dates for tenure; plan balance 521.10 read raw; restore 759e9bed; March month of the prior suspension now outside the 6-month look-back).

#### blind verdict (revision 2, before reveal)
- Policy self-consistency PASS; problem tree PASS; unique solution PASS (credit 87.50 then 3 months from 2026-11-01).
- Factors: SOURCE-FACTOR RED persists (F-1 not closed).

### source_gt_comparison (revision 2)

- Reveal: 2026-10-05T10:04:39Z, after both revision_2 derivations reached disk (mtimes 10:04:32Z). Round-2 `tasks/0.json` sha256 a552f8f2a66afb09dd3d6d182077f0a2af0418ce06dbc46d07ddc03a73886ae0.
- Writes: credit (0cf232c7…, service_dispute, 2026-09, 87.5) and suspension (2026-11-01, 3) — same as blind; owners agent then user; order credit -> suspension — same. Read set unchanged (plans, ledger, orders, assisted, entrance, independent) — same.
- prerequisite_closure value against value: why_false (88.00 / 2.00 h / 70 of 120 min / no credit) same; flips 521.10 -> 433.60, past_due 162.10 -> 74.60, deduction 2 -> 1 same; skipped -> 2 months same; resolution_order same.
- factor_sensitivity figure against figure: credit 77.00 / 88.00 / 77.00 / 77.00 / 87.00 / 77.50, baseline 55.00 — all same; suspension 1 / 2 / 4 / 2, baseline 0 — all same.
- GT factor_trace now labels illness_relief multi-source (cut-short visit + AL absence: genuine), and no longer labels medical_absence_extension or entrance_overage_rate multi-source — round-1 task-0 observation 3 closed.
- GT labels previous_suspension_count "method: look-back window"; the blind audit holds that tiers 2 and 3 are one method with a 6- vs 12-month window (F-1).

Verdicts (revision 2): policy self-consistency PASS; problem tree PASS; unique solution PASS (blind = GT); factors SOURCE-FACTOR RED (F-1 not closed).

### findings (revision 2)

1. SOURCE-FACTOR RED — F-1 not genuinely closed (relation: same defect as round-1 finding 1, renamed).
   - Symptom: previous_suspension_count is still labelled `method` while two of its three tiers select one method differing only by a number.
   - Evidence: `_difficulty.md` § revision_2 / findings F-1 (compute `MX(0, MN(prior_months, K('recent_window_months') - months_since_prior_end))` vs `MX(0, MN(prior_months, K('window_months') - months_since_prior_end))`).
   - Demonstrated on this world: tier 2 (taken) gives MN(2, 6 - 5) = 1; tier 3 gives MN(2, 12 - 5) = 2 — identical counting rule, window 6 vs 12; tier 1 gives 0 = the same rule with a window of 0. The round-1 share s in {0, 0.5, 1} has become a window W in {0, 6, 12}. Counted honestly the suspension computation has no method factor (bound: at least 1).
   - The factor bears weight (3 vs 2), so the defect is the label / method-count bound only.
   - Affected: `services.extended.yaml` services_ext_suspension_months.factors[previous_suspension_count]; task 0 computations[1].
2. Round-1 observation 2 (illness_relief realism) closed: relief now requires the visit to have ended short, and the tier taken rests on SO-2609-0389's 70 of 120 minutes plus the absence 5 days later.
3. Round-1 observation 3 closed (multi-source labels corrected).
4. No regression: every round-1 PASS item re-derived on the new charter holds with the same values.

## revision_3

### source_derivation_frozen (revision 3)

- Inputs: `task_0.view.json` 26690d98… (unchanged), `services.extended.yaml` b202a9e5… (changed: suspension policy only), `task_tools.py` 94951f4a… (unchanged). Written before reading the round-3 `tasks/0.json`.
- contamination_disclosure: round-1 and round-2 GT of this task known (credit 87.50, 3 months). Re-derived from the round-3 charter.
- Credit policy text and world unchanged since revision 2, so the credit derivation of revision 2 is carried forward on those grounds: 87.50 on 0cf232c7 (2026-09), factor results 77.00 / 88.00 / 77.00 / 77.00 / 87.00 / 77.50, all-baseline 55.00.

#### suspension (re-derived on opening world + credit)
- First month 2026-11-01; max 2 (Companion).
- absence_extra: AL 3080556d on_leave, rehab_facility -> +2.
- months_in_force (time_in_force_count): AL 3080556d admission_source larkspur_independent; IL residency 91a77fcc move_in_date 2019-09-03 on record (closed 2024-03-18, termination_reason transfer_assisted) -> tier 1 -> whole months 2019-09-03 -> 2026-10-05 = 85 (2026-09-03 is 84, 2026-10-03 is 85, 2026-11-03 not reached).
- tenure_extra: 85 >= 48 -> loyalty_long_extra +2.
- past_due: 433.60 less the fee charged on the ledger on 2026-10-01 for 2026-10 (b0bd66a8, 359.00) = 74.60 -> deduct 1.
- counted_prior: prior suspension 2026-03-01..2026-04-30 = 2 months; ended 5 whole months before the request; MN(2, 12 - 5) = 2 (both months ended fewer than 12 whole months before).
- Months = max(0, 2 + 2 + 2 - 1 - 2) = 3 -> sign_services_suspension_89d6021d(df70605f…, 2026-11-01, 3).
- Opening world (no credit): past_due 162.10 -> deduct 2 -> 2 months. Edge bears weight.

#### factor_weight (suspension)
- medical_absence_extension baseline 0 -> 1.
- time_in_force_count baseline MONTHS(2024-03-01, 2026-10-05) = 31 -> +1 -> 2.
- time_in_force_extension baseline 0 -> 1.
- account_standing_deduction baseline 0 -> 4.
- All-baseline (baseline rule: max 2 less 2 counted months): 0.
- All four differ from 3. Labels honest (`_difficulty.md` § revision_3 factor_ladders). Multi-source: time_in_force_count tier 1 (AL admission_source + IL move-in), illness_relief, delivered_time_billing. Cross-difficulty: assisted, independent (IL row 91a77fcc seeded), entrance.
- Near-misses: plan effective_date 2024-03-01 (31 months; the plain count), the prior suspension (tier 2 would give 31 - 2 = 29), plan balance 521.10 read raw, EFA occupancy and profile-opened dates (not the IL move-in the rule names). Stamp: none naming the tier; admission_source is the record the rule itself names.

#### blind verdict (revision 3, before reveal)
- Policy self-consistency PASS; problem tree PASS; factors PASS (F-1 closed); unique solution PASS: credit 87.50 then 3 months from 2026-11-01.

### source_gt_comparison (revision 3)

- Reveal 2026-10-05T10:28:55Z, after all three revision_3 sections were on disk (10:28:48Z). Round-3 `tasks/0.json` sha256 b0438680b47e1f833c189bdcaff5bd9a08c1d2f93efe0475fd2ca733af545a8e.
- Writes: credit (0cf232c7…, service_dispute, 2026-09, 87.5) and suspension (2026-11-01, 3) — same; owners and order same; scope {suspension_months, short_visit_credit} same.
- prerequisite_closure: flips 521.10 -> 433.60, past_due 162.10 -> 74.60, deduction 2 -> 1; skipped -> 2 months — same as blind.
- factor_sensitivity figure against figure: credit 77.0 / 88.0 / 77.0 / 77.0 / 87.0 / 77.5, baseline 55.0 — same; suspension medical_absence_extension 1, time_in_force_count 2, time_in_force_extension 1, account_standing_deduction 4, baseline 0 — same. GT's tier for time_in_force_count (admission_source larkspur_independent + IL move-in 2019-09-03 -> 85 months) and its counted_prior MN(2, 12 - 5) = 2 equal the blind values.
- Verdicts (revision 3): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

### findings (revision 3)
1. Round-2 finding 1 (F-1, SOURCE-FACTOR RED) — CLOSED: the mislabelled ladder is removed and the new method factor time_in_force_count is honest, bears weight (3 vs 2) and is multi-source and cross-difficulty on this world.
2. No regression: credit derivation, tree, edge weight and all other factor figures identical to revision 2.
3. Observations O-10 (stale past_due quote) and O-12 (time_in_force_extension binding list) touch this task's suspension policy but change no value here.

## revision_4

### source_derivation_frozen (revision 4)

- Inputs: `task_0.view.json` 26690d98… (unchanged), `services.extended.yaml` d73f8312… (changed), `task_tools.py` 94951f4a… (unchanged). Written before reading the round-4 `tasks/0.json` and before reading the KB-audit directories.
- contamination_disclosure: round-1..3 GT known (87.50 / 3); the brief says the scored value changed.

#### credit (opening world)
Credit compute unchanged and the world unchanged; the rule's new scope sentence and plan names do not alter any input: LifeChoice 50% Refundable is "any LifeChoice plan" -> fee_for_service -> 42.00. Credit 87.50 on 0cf232c7 (2026-09); factor results 77.00 / 88.00 / 77.00 / 77.00 / 87.00 / 77.50; all-baseline 55.00.

#### suspension (opening world + credit)
- First month 2026-11-01.
- Starting allowance: Companion max_suspension_months_per_12m 2 ("the starting allowance and not a ceiling").
- Absence: AL 3080556d on_leave, rehab_facility -> +2 to the total.
- Time in force: AL admission_source larkspur_independent, IL 91a77fcc move_in_date 2019-09-03 -> months run from 2019-09-03 -> 85 whole months -> >= 48 -> +2.
- Past due: 433.60 less the 2026-10-01 fee 359.00 = 74.60 -> deduct 1.
- Previous suspension: 2026-03-01..2026-04-30, 2 months, ended 5 whole months before; within window 12 -> window-counted MN(2, 12 - 5) = 2; did not lie within a medical absence (absence began 2026-09-24); ended >= 3 whole months before -> share 0.5 -> floor(2 x 0.5) = 1.
- Total = max(0, 2 + 2 + 2 - 1 - 1) = 4 -> sign_services_suspension_89d6021d(df70605f…, 2026-11-01, 4) -> suspension 2026-11-01..2027-02-28.
- Opening world (no credit): past due 162.10 -> deduct 2 -> 3. Edge bears weight.

#### factor_weight (suspension)
- medical_absence_extension baseline 0 -> 2.
- time_in_force_count baseline (effective date: 31 months -> +1) -> 3.
- account_standing_deduction baseline 0 -> 5.
- previous_suspension_share baseline 1 -> counted 2 -> 3.
- All-baseline (baseline rule: 2 + tenure from effective date (31 -> +1) - window-counted 2): 1. Definite, differs from 4.
- All four bear weight; labels honest; multi-source and cross-difficulty (assisted, independent) present with rows seeded.
- Near-misses: plan effective date 2024-03-01 (31 months) vs IL move-in 2019-09-03; AL absence start 2026-09-24 (after the prior suspension, so it does not contain it); plan balance 521.10 read raw; the March month of the prior suspension (still inside the 12-month window, both months counted before the share).

#### blind verdict (revision 4, before reveal)
- Policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS: credit 87.50, then suspension 2026-11-01 x 4 months.

### source_gt_comparison (revision 4)

- Reveal 2026-10-05T11:35:29Z, after all revision_4 frozen sections were on disk (11:35:03Z). Round-4 `tasks/0.json` sha256 143641a73102df7733788664ee4275998926ae3f0398b8cf5a085bd1da027335.
- Writes: credit (0cf232c7…, service_dispute, 2026-09, 87.5) and suspension (2026-11-01, 4) — same as blind; owners agent then user; order credit -> suspension — same. The scored value moved 3 -> 4 as the brief said; the blind derivation reached 4 independently from the round-4 rule.
- prerequisite_closure: flips 521.10 -> 433.60, past_due 162.10 -> 74.60, deduction 2 -> 1, suspension 3 -> 4; skipped -> 3 months — same as blind.
- factor_sensitivity figure against figure: credit 77.0 / 88.0 / 77.0 / 77.0 / 87.0 / 77.5, baseline 55.0 — same; suspension medical_absence_extension 2, time_in_force_count 3, account_standing_deduction 5, previous_suspension_share 3, baseline 1 — same.
- Verdicts (revision 4): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

### findings (revision 4)
1. No RED. Round-3 PASS items re-derived on the round-4 charter: tree, edge weight (4 vs 3), all ten factors bear weight, baselines definite (55.00 and 1) and different from gold.
2. The KB-traced items that bear on this task's source (B1/N1, B2/E1/N2, N3, N4, N5) are closed at the source — see `_difficulty.md` § revision_4 / kb_traced_items.
