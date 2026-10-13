# Policy-task audit — assisted_living_care_levels / charter-global

## charter_global_frozen

- Round: revision_1 (round 1). Auditor: independent erl-task-policy-audit agent (not the instantiating agent). Frozen 2026-10-05T09:05Z (wall clock), before any task GT was opened.
- Freeze hashes (sha256, verified against the coordinator MANIFEST and against the copies in `tasks/assisted_living_care_levels/`, which hash identically):
  - `assisted.extended.yaml` af705dcc26f0e77ba6259b758ab06aa79af5c91e31723bd0b3fe547e1212d744
  - `task_tools.py` d6a8d689e1fbe466013c46b7442115dab937a068edb266cf2fe52fc341e32505
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/assisted.yaml` (+ `entrance.yaml` plan parameters only), `blueprint/share_tools.py`, the masked view directory `audits/_views/policy_task/assisted_living_care_levels/`.
- Masked / unread at freeze: every field of `tasks/assisted_living_care_levels/tasks/*.json` other than the three view fields; `worklog.md` of the difficulty and of the scenario; any existing audit. Not read at all: the instantiate-stage scripts (DSL semantics such as MONTHS are taken from the rule prose: "whole months" = completed calendar-month anniversaries; DAYS = calendar-day difference).
- Base copy check: lines 1-1527 of `assisted.extended.yaml` are byte-identical to `blueprint/products/assisted.yaml` (`diff` gives only the trailing blank line 1528).
- Entry conditions (Step 0): gate snapshot supplied with the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to render stage); masked views with MANIFEST hashes supplied and re-verified. Complete.

### policy_conflict_scan

Extended policies (6) and the prerequisite graph:

| policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| assisted_ext_absence_care_relief | post_absence_care_credit_bb749fc3 (agent) | amount | [] |
| assisted_ext_late_fee_assessment | assess_late_fee_246a7744 (agent) | amount | absence_care_relief (value_input, state) |
| assisted_ext_level_increase_charge | post_level_increase_care_charge_9f33663f (agent) | amount | [] |
| assisted_ext_apartment_transfer_fee | sign_apartment_change_e633e519 (user) | transfer_fee | level_increase_charge (value_input, state); late_fee_assessment (value_input, state) |
| assisted_ext_returned_payment_fee | post_returned_payment_fee_036f277a (agent) | amount | [] |
| assisted_ext_advance_payment | submit_advance_payment_8dbe3a8d (user) | amount | returned_payment_fee (value_input, state) |

- The graph has exactly two connected components: {transfer_fee <- level_increase, transfer_fee <- late_fee <- absence_relief} (root with an owner=user tool, 3 prerequisite problems, 3 value_input edges) and {advance_payment <- returned_payment_fee} (root with an owner=user tool, 1 prerequisite problem, 1 value_input edge). With M=2 the only scope partition that is pairwise disjoint and jointly complete is one component per task; the derivations in 0.md / 1.md identify task 0 with the first and task 1 with the second from the worlds alone.
- Overlapping subjects: `assisted_credit` (absence relief) vs base `assisted_level_change_effective`, `assisted_move_out`, `assisted_entrance_and_respite_credits`, `assisted_billing_corrections` — distinguished by credit_reason; `assisted_addon_charge` (returned fee and transfer fee) — distinguished by addon_code and by separate tools; `assisted_care_fee_charge` (level increase) vs base `assisted_monthly_billing` — see override_declarations, finding F1.
- The same base sentence (assisted_care_addons, "Guest meals are charged at guest_meal_fee per meal, ltc_direct_billing_fee is charged monthly ..., apartment_change_fee is charged once ..., and returned_payment_fee is charged once ...") is superseded twice, by transfer fee and by returned fee, with two different `replaced_by` texts, neither of which restates the guest-meal and ltc_direct_billing_fee clauses (observation O2).
- Cross-category reads: independent (move_in_date; independent_ledger returns), entrance (status, contract_type, occupancy_date, care_fee_discount_pct, rent_discount_pct), respite (check_in_date of a converted stay). All are reads; no write crosses the category boundary.
- Terminal states: no policy changes residency status; transfer fee changes apartment fields and rent effective from possession. No conflicting terminal state among the six.

### rule_compute_equivalence

Checked every compute binding against its `compute_basis` quotation and back against the rule, per policy:

- absence_care_relief: midnights, waiting ladder (hospital+timely post-hospital / rehab or untimely hospital / other), tenure start (IL move-in when admission_source larkspur_independent, else AL move-in), whole-month tenure, shortening ladder, floor at zero on the shortened waiting (`MX(waiting - shortening, 0)` = "never below zero"), credited-day cap, billing month = most recent full-month care fee charge, three-tier daily care fee, level-of-charge relief percentage, plan reduction, single final rounding — every binding has a verbatim basis; every rule sentence is implemented. One rule sentence ("posted at most once per absence per billing month") is an eligibility, not a compute item — correct.
- late_fee_assessment: period = most recent full-month rent charge (rule: "billing month most recently billed in full"); past-due = full-month rent + full-month care + add-ons with service_date = first of month − credits carrying the period − payments posted < 1 whole month before handling date; floor at 0 in compute is not stated in the rule but is inert because a non-positive past-due is below late_fee_min_past_due (no consequence). Rate ladder, continuing-lateness ladder, relief midnights (clipped to the month), courtesy ladder, ordering "greater-of, + continuing, x relief x courtesy, round once" — all present both ways. `relief_midnights` reads only the residency's current absence fields; the rule speaks of "a hospital or rehabilitation-facility absence during the billing month" (single-absence reading; inert on both worlds).
- level_increase_charge: days covered (routine/post-move-in from notice+30; late c-o-c/post-hospital notice from notice date; on-time from assessment date), phase-in from the most recent routine reassessment, add-on offset, plan share inside the charge, order "phase, − offset floored at 0, x plan, round once" — equivalent both ways.
- apartment_transfer_fee: five shares multiplied onto apartment_change_fee, tenure start three ways (IL / converted respite / AL move-in), windows 2 / 24 / 12 whole months — equivalent.
- returned_payment_fee: basis three ways (insurer 0 / household >= 4000 at 1.5% / flat), repeat count excludes the return being charged and adds the IL ledger returns, member share, residence share — equivalent.
- advance_payment: open balance, horizon from returns on both accounts, rent timing by lead to the first coming day (`DAYS(notice, month_last)+1` = days to the first of the next month), insurer care terms, care fee carried for the discount, add-on recurrence, vesting, assembly order — equivalent.
- Ladder face vs rule face: every tier named in each `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and vice versa. No tier lives only in compute.

Result: no SOURCE-POLICY defect from rule/compute equivalence.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one extended policy; no base policy names a task tool.
- Tool bodies (read in full): each performs one `ctx.create` on `assisted_ledger` plus a balance update (sign_apartment_change additionally updates apartment fields). None looks anything up beyond the residency row for customer_id/balance, none validates eligibility, none refuses or hints. No tool judges a prerequisite.
- Docstrings name no other tool, carry no position-in-sequence words (the "Once posted/assessed/charged ..." phrases describe the tool's own effect, not an order against another action).
- uuid8 tails: bb749fc3, 246a7744, 9f33663f, e633e519, 036f277a, 8dbe3a8d — pairwise distinct, no shared prefix, no sequence or adjacency pattern.

### prerequisite_graph

- `prerequisite` present on all six (three `[]`). Every `problem` names an extended policy of this file, none a base policy, none itself; graph acyclic.
- `policy_source` verbatim in the blocked policy's own rule: E1 (late fee <- absence relief) rule sentence 2; E2 (transfer <- level increase) rule sentence 2; E3 (transfer <- late fee) rule sentence 3; E4 (advance <- returned fee) rule sentence 2. All `form: state`, no `fallback_reason` (correct).
- `gate` names an existing compute binding of the blocked policy: period_credits, increase_billed, late_fees_in_window, open_balance. `kind: value_input` matches each (the depended-on write enters a binding of the blocked compute).
- `resolved_by` equals the depended-on policy's `target_tool` in all four; each genuinely changes the gate binding (credit carries billing_period; prorated_level_change charge counted by billing_period; late fee counted by posting_date; fee raises account_balance).
- `condition` texts match the sentences' strength and scope.
- Observation O4: E2's `effect` reads "... which together with the recent post-hospital reassessment moves the care-needs share from care_share_one to care_share_both" — it presumes one world's records (a recent post-hospital reassessment) in general text.

### prerequisite_sentences

Four-point test on each edge:

- E1 "A late fee is fixed only after the ledger carries the absence care credit owed for every absence that ended within the billing period it is assessed for." — connective "only after"; waited-on state is a ledger record (credit of the absence-care kind for the period), no actor/tool/id/snake_case; strength equals the condition. Exactly one write of this difficulty creates such a credit: post_absence_care_credit_bb749fc3 (credit_reason absence_care_credit). Derivation: sentence -> ledger shows no absence_care_credit for the period although the residency's absence ended inside it -> the policy whose rule posts "an absence-relief credit ... carries the absence start date" is absence_care_relief -> post it. Single reading.
- E2 "The transfer fee for a move is fixed only after the ledger carries the prorated care fee charge owed for the current billing month at the care level of the latest assessment." — "only after"; state; no tool or id. The only write in the difficulty that puts a prorated care fee charge on the ledger is post_level_increase_care_charge_9f33663f (charge_basis prorated_level_change). Single reading.
- E3 "The transfer fee is not fixed until the ledger carries the late fee owed for every billing period left unpaid past its grace period." — "not until"; state; single write assess_late_fee_246a7744.
- E4 "An advance payment is not taken until the ledger carries the returned payment fee owed for every payment reinstated after its return." — "not until"; state; single write post_returned_payment_fee_036f277a.
- No blocked rule restates its dependency in a second wording; no depended-on rule restates the sentence; no rule names a tool or policy id. No rule states a cross-problem order that grounds no edge (the transfer fee's care-needs and payment-standing sentences and the late fee's "every credit that carries the billing period" are the value channels of E2, E3 and E1). No base sentence is used to ground an edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- absence_care_relief vs assisted_absence: sentences 2 and 3 superseded and declared; sentences 1, 4-7 followed. The superseded sentence 3 also carried "one absence_care_credit is posted per absence per billing month" (one per month the absence spans); the extended rule posts only for the month of the most recent full-month charge — a dropped branch for absences spanning two months (observation O3, no consequence on either world: task 0's absence lies within one month). vs level_change_effective / move_out / entrance credits / billing_corrections: no sentence of these governs the absence credit amount; the plan reduction replaces nothing the base states for credits. Clean.
- late_fee_assessment vs assisted_payments_and_late_fees: sentence 5 (the late fee formula over assisted_msr_period_past_due) superseded and declared; the redefined past-due ("less every credit ... less the payments posted less than one whole month before the handling date") replaces the measure only through that declared sentence; sentences 1-4, 6-8 followed. Clean.
- level_increase_charge: four declared supersessions (level_change_effective s7 split sentence and s2 effective date; entrance_and_respite_credits s1; care_addons s5). **Not declared**: assisted_monthly_billing s1 ("the care fee at care_level_monthly_fee of the level billed") and s2 (proration of the month of a level change), and assisted_level_assignment s1 ("the level billed never differs from the band of the latest assessment once its effective date has passed"). The extended rule's phase-in sentence bills only phase_share of the difference for days carried at the new level, and its late-notice tier starts billing the new level at the notice date although the base effective date (and the seeded `level_effective_date`) is the assessment date. -> finding F1. Also dropped branches: the superseded split sentence's decrease clause (level_change_proration credit) and the superseded entrance sentence's general rule for every other rent and care fee charge are not restated (observation O3).
- apartment_transfer_fee: rent_and_apartment s5 and care_addons s7 superseded and declared; replacement adds representative signers (POA/guardian) — declared. Clean.
- returned_payment_fee: care_addons s7 and payments s2 superseded and declared. Clean.
- advance_payment: `overwrite: []`; base payments sentences 1 (oldest charge first) and 8 (posting statuses) are followed; no base sentence prices a payment. Clean.

### factor_ladders

| policy | factor | effect | tiers | multi-source | cross_difficulty | ladder real? |
| --- | --- | --- | --- | --- | --- | --- |
| absence_care_relief | absence_waiting | parameter | 3 (7/10/14) | yes (absence reason x post-hospital assessment) | — | yes |
| | larkspur_tenure_shortening | parameter | 3 (3/1/0) | no | independent | yes |
| | plan_reduction | parameter | 3 (lifecare 0 / other (100-pct)/100 / none 1) | no | entrance | **no** — F2 |
| | billed_level_daily_fee | method | 3 | no | — | yes (tier 2 "lower of" always coincides with tier 1 or tier 3 on given inputs; O5) |
| | level_relief_percentage | parameter | 3 (85/95/100) | no | — | yes |
| late_fee_assessment | repeat_lateness_rate | parameter | 3 (3.0/2.0/1.5) | no | — | yes |
| | continuing_lateness | method | 3 (per-day / flat / none) | no | — | yes |
| | hospital_absence_relief | parameter | 3 (0.5/0.75/1) | no | — | yes |
| | life_plan_courtesy | parameter | 3 (0.8/0.9/1) | no | entrance | yes |
| level_increase_charge | increase_start_day | method | 3 | yes (assessment type x notice date) | — | yes |
| | increase_phase_in | parameter | 3 (0.5/0.75/1) | no | — | yes |
| | included_addon_offset | parameter | 3 | yes | — | **no** — F2 |
| | plan_discount_inside_charge | parameter | 3 | no | entrance | **no** — F2 |
| apartment_transfer_fee | care_needs_share | parameter | 3 (0.5/0.75/1) | yes (assessments x ledger) | — | yes |
| | tenure_start_date | method | 3 | no | independent (+respite) | yes |
| | tenure_share | parameter | 3 (0.8/0.9/1) | no | — | yes |
| | repeat_move_share | parameter | 3 (1.5/1.25/1) | no | — | yes |
| | life_plan_member_share | parameter | 3 (0.5/0.75/1) | no | entrance | yes |
| | payment_standing_share | parameter | 3 (1.2/1.1/1) | no | — | yes |
| returned_payment_fee | returned_instrument_basis | method | 3 | no | — | yes |
| | repeat_return_multiplier | parameter | 3 (1.5/1.25/1) | yes (AL ledger x IL ledger) | independent | yes |
| | life_plan_member_courtesy | parameter | 3 (0.8/0.9/1) | no | entrance | yes |
| | larkspur_residence_share | parameter | 3 (0.9/0.95/1) | no | independent | yes |
| advance_payment | advance_horizon | parameter | 3 (2/1/0 months) | yes (AL x IL ledger) | independent | yes |
| | rent_increase_timing | method | 3 | no | — | yes |
| | insurer_care_terms | parameter | 3 | yes (residency flag x insurer payments) | — | yes |
| | addon_recurrence | method | 3 declared | no | — | **no** — F2 |
| | plan_discount_vesting | parameter | 3 (1/0.5/0) | no | entrance | yes |

- Every ladder is stated in full in its rule; bindings are pairwise disjoint within each policy; every `decides` is an input, never `result`; every baseline.rule sentence is a rule sentence; every factor's fall-through is the baseline except as noted in F2 for addon_recurrence.
- Declared counts: absence 5 (4P/1M), late fee 4 (3P/1M), level increase 4 (3P/1M), transfer 6 (5P/1M), returned fee 4 (3P/1M), advance 5 (3P/2M).
- Counts after striking the unreal ladders of F2: absence 4 (3P/1M) — passes; late fee 4 — passes; **level increase 2 (1P/1M) — fails 4-6 and >=2 parameter**; transfer 6 — passes; returned fee 4 — passes; advance 4 (3P/1M) — passes.
- Per component: the transfer-fee tree carries multi-source factors (absence_waiting, increase_start_day, care_needs_share) and cross-difficulty factors (tenure shortening, tenure_start_date, courtesy, member share); the advance tree carries multi-source (repeat_return_multiplier, advance_horizon, insurer_care_terms) and cross-difficulty (residence share, member courtesy, vesting).
- Realism observations (no RED): increase_phase_in (billing a share of a nurse-set level increase) and payment_standing_share (raising a move fee for past late fees) are unusual treatments but each is a coherent published policy a senior-living operator could adopt (O6).

### findings

**F1 — SOURCE-POLICY RED (undeclared override) — bears on task 0.**
- Symptom: the level-increase charge bills less than the new level's fee for days carried at that level, and starts billing it later than the effective date the base and the records give, without naming the base sentences that fix those quantities.
- Root cause: `assisted_ext_level_increase_charge.overwrite` names level_change_effective s2/s7, entrance s1 and care_addons s5, but not assisted_monthly_billing s1-s2 (in its own `base_policy_refs`) nor assisted_level_assignment s1.
- Evidence: base `assisted_monthly_billing.rule`: "Rent and the care level fee are billed ... the care fee at care_level_monthly_fee of the level billed." / "The move-in month, the month of a level or rent change and the month in which fees end are prorated: the daily amount is the monthly amount divided by the actual number of days in that calendar month, multiplied by the days billed ..."; base `assisted_level_assignment.rule`: "... the level billed never differs from the band of the latest assessment once its effective date has passed." Extended rule: "A large increase is phased in ...: a rise of phase_large_points points or more bills phase_share_large of the difference, a rise of phase_mid_points points or more but under phase_large_points bills phase_share_mid of it ..."; and "... an increase found at a change-of-condition or post-hospital reassessment whose written level notice was issued more than level_notice_issue_days calendar days after the assessment date is covered from the notice date".
- Demonstrated consequence: in 0.md (task 0 world: two readings of the scored level-increase amount).
- Affected: `assisted.extended.yaml` extended_policies[assisted_ext_level_increase_charge].overwrite / rule sentences 4-5.

**F2 — SOURCE-FACTOR RED (unreal ladders: tiers selecting the same method) — bears on task 0 (included_addon_offset, plan_discount_inside_charge, plan_reduction) and task 1 (addon_recurrence).**
- included_addon_offset: tier 1 "both monthly add-on amounts", tier 2 "that monthly add-on amount", fall-through "nothing" are one method — offset = sum of the monthly add-ons (escort, incontinence) that were billed for the month and are included at the new level — evaluated on a set of size 2, 1 and 0. The single expression `(escort_billed if escort_assistance_included else 0) + (incontinence_billed if incontinence_care_included else 0)` reproduces `offset_monthly` on every input (the compute itself falls back to it in its second branch).
- plan_reduction and plan_discount_inside_charge: tier 1 "under a lifecare plan nothing is credited/billed", tier 2 "reduced by the plan's care_fee_discount_pct percent", fall-through "in full" are one method — multiply by (100 − care_fee_discount_pct of the occupied plan, 0 when none)/100: both lifecare plans in `products/entrance.yaml` carry care_fee_discount_pct 100, so tier 2's method gives exactly tier 1's "nothing"; the rule's own justification ("so the credit returns only what was paid") is that one method.
- addon_recurrence: tier 2 "the level carried took effect on or before that day and such add-ons were billed that month -> they recur at the amounts billed" and the fall-through "otherwise no add-on recurs" are one method (recur at the amounts billed) — the fall-through is reachable only when no such add-on was billed, where the amounts billed are nothing; the declared baseline `addons_month: addons_billed_month` is tier 2's method, not the declared fall-through. The ladder has two real tiers.
- Consequence for counts: level_increase_charge keeps 2 factors that pass (fails 4-6 and >=2 parameter) — demonstrated against task 0's world in 0.md; advance_payment keeps 4 (passes counts), the unreal ladder itself is the defect for task 1 (1.md).
- Affected: `assisted.extended.yaml` factors of assisted_ext_level_increase_charge (included_addon_offset, plan_discount_inside_charge), assisted_ext_absence_care_relief (plan_reduction), assisted_ext_advance_payment (addon_recurrence), and the corresponding rule sentences.

Observations (no RED):
- O2: assisted_care_addons s7 is superseded by two policies with two different replacements; the guest_meal_fee and ltc_direct_billing_fee clauses of that sentence survive in no replacement (no scored quantity in either task reads them from base; the advance payment states ltc_direct_billing_fee in its own rule).
- O3: dropped branches in superseded sentences — the decrease clause of level_change_effective s7, the per-month absence credit of assisted_absence s3 for absences spanning months, the general entrance-discount-credit rule of entrance_and_respite_credits s1 for every rent and care fee charge other than the level-increase charge. Neither task's scored solution touches them.
- O4: E2 `effect` text presumes a world ("the recent post-hospital reassessment").
- O5: billed_level_daily_fee tier 2 ("lower of the full-month charge and the level fee") coincides on any input with tier 1 (increase during absence) or the fall-through (decrease during absence); task 0 sits on tier 1, so no consequence here.
- O6: realism notes on phase-in and payment standing (see factor_ladders).
- O7: "whole months before the handling date" windows: an entry posted on the handling date itself (the late fee posted during the transfer-fee task) is counted only under the inclusive reading; the E3 sentence makes that reading the only one under which the edge carries weight. No second answer demonstrated.

## closing_checklist

Not written: the difficulty does not pass (F1, F2 and the per-task verdicts in 0.md and 1.md). Step 4 applies only once all M tasks PASS.

## post_reveal_note

Appended after both reveals (2026-10-05T09:08Z); the sections above are unchanged from the pre-reveal freeze (sha256 34946fcb…a858 at 09:07:57Z). Both blind derivations land on GT for every scored value, object, owner and order. Per-task verdicts: task 0 — SOURCE-POLICY RED (F1) + SOURCE-FACTOR RED (F2); task 1 — SOURCE-FACTOR RED (F2). The closing checklist is not written because the difficulty does not pass.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2, same independent auditor. Frozen 2026-10-05T09:52Z, before any round-2 task JSON was opened. Round-1 text above is untouched (sha256 of this file before appending: 86768e43…0c79).
- Shared inputs: `assisted.extended.yaml` **changed** (af705dcc… -> de887ef6c33bc86d74e8bdb8659e36c2f3d24ca86d259d11ffaaf4fc821d159b; identical in the view and in `tasks/`), `task_tools.py` unchanged (d6a8d689…2505). Because the charter changed, every charter-global section is re-derived below; the tool-module conclusions (§ action_binding_and_uuids of revision_1) are carried forward on the unchanged hash.
- Base copy: lines 1-1527 still byte-identical to `blueprint/products/assisted.yaml`.
- Entry conditions: coordinator gate snapshot after rework (all OK; traceability deferred) and rebuilt view MANIFEST supplied; hashes re-verified. Complete.
- Read: the rebuilt view directory, `blueprint/`. Masked/unread at freeze: all round-2 task JSON fields beyond the views, worklogs.

### policy_conflict_scan (revision_2)

- The six policies, tools, `computes` and the prerequisite graph are unchanged; the two components (transfer-fee tree, advance-payment tree) and therefore the only disjoint, complete M=2 scope partition are unchanged.
- New content: absence relief (vested plan reduction; "mean" daily fee for straddling absences); level increase (three more declared supersessions; a decrease sentence; a reworked add-on offset; vested plan share; a new sentence on the entrance plan discount credits of every other rent and care fee charge); returned fee (guest-meal and insurer-billing clauses restated); advance payment (reworked add-on recurrence); transfer fee (E2 `effect` text).

### rule_compute_equivalence (revision_2)

- absence relief: `plan_member_months`/`plan_reduction` implement the vesting sentence (full pct at >= plan_vesting_months, plan_vesting_half x pct below, 1 without an agreement); `daily_care_fee` tier 2 is `(month_charge + fee)/2/days` = "the mean of that full-month charge and the care_level_monthly_fee ..., divided by the days in the month". Equivalent both ways.
- level increase: `included_amount`, `repriced_amount`, `offset_monthly` implement "included add-ons offset in full; when none is included, the excess of insulin / diabetic monitoring / oxygen billed over the new level's fee; otherwise nothing". `plan_discount_share` implements the vested share. The new decrease sentence and the entrance-credit sentence are not compute items of this policy (no binding needed; the target tool posts only increase charges). Equivalent.
- advance payment: tier 2 of add-on recurrence ("none billed for the most recent billed month although some were billed for the month before it ... resume at the amounts billed then") is implemented through a 2-whole-month service-date window minus the latest month; while the handling date lies in the most recent billed month (it must: charges post on the first) that window is exactly those two months. Equivalent.
- returned fee, late fee, transfer fee: unchanged except the returned fee's restated sentence (no compute item). Equivalent.

### prerequisite_graph and prerequisite_sentences (revision_2)

- Edges E1-E4, their `policy_source` sentences, forms, gates, kinds and `resolved_by` are textually unchanged; the four-point test and single-write derivations of revision_1 hold verbatim.
- E2 `effect` now reads "... moves the care-needs share one tier lower: from the full fee to care_share_one, or from care_share_one to care_share_both when a recent change-of-condition or post-hospital reassessment also stands" — general text. **O4 closed.**
- No rule gained a tool name, policy id or an unanchored cross-problem order.

### override_declarations (revision_2)

- level increase: now declares assisted_monthly_billing s1 and s2 and assisted_level_assignment s1 (and adds assisted_level_assignment to `base_policy_refs`). The merged semantics for the scored level-increase charge are unique: phase-in, difference-based proration and the first-day-covered rule now replace the base sentences that gave Reading B in revision_1. **F1 closed.**
- New O8 (observation): the three newly superseded base sentences are general charter rules — monthly billing in advance at the contracted rent and level fee, the proration of move-in / move-out / rent-change months, and "the care level ... is always the level whose ... band contains the care points of the most recent assessment" — and each `replaced_by` speaks only of the level-increase charge. Read as charter-wide supersessions they leave those general rules with no statement in the merged policy. No scored value of either task is computed from them (the late fee reads posted full-month charges; the advance payment states its own rent and fee).
- **New F3 (SOURCE-POLICY RED, introduced by the rework):** the level-increase rule now carries "Every other rent charge and care fee charge of a customer holding an Entrance Fee Agreement in occupied status keeps its separate entrance plan discount credit referencing that charge and the agreement, at the plan's rent_discount_pct or care_fee_discount_pct once the occupancy date is at least plan_vesting_months whole months old and at plan_vesting_half of those percentages before then." Base assisted_entrance_and_respite_credits s2, not superseded by any policy: "The discount percentages are care_fee_discount_pct and rent_discount_pct of the plan, set in the Entrance Fee Agreement charter, each applied to the charge amount and rounded to the cent half up." For a charge posted while the agreement is under 60 months old the two give different credits (half vs full percentage); the Entrance charter itself states that a move into assisted living "brings the care_fee_discount_pct and rent_discount_pct of the plan into effect". The same vesting premise is restated in the absence relief rule ("pays a care fee lowered by the plan's vested care discount"). Demonstration against a seeded world: 0.md revision_2.
- returned fee: the restated sentence "Guest meals remain charged at guest_meal_fee per meal, and ltc_direct_billing_fee remains charged monthly while ltc_direct_billing is true." restores the clauses dropped by the double supersession. **O2 closed.**
- O3: the decrease branch of level_change_effective s7 is restored (rule sentence 2); the general entrance-credit rule is restored but with vesting (-> F3); the absence credit still relates only to the month of the most recent full-month charge (per-month posting for absences spanning months remains dropped). **Partly closed**, as claimed.
- absence relief, late fee, transfer fee, advance payment: no new deviation from their base references.

### factor_ladders (revision_2)

| policy | factor | effect | tiers | real? |
| --- | --- | --- | --- | --- |
| absence relief | plan_reduction | parameter | full pct (>=60 m) / half pct (<60 m) / none | yes — distinct values for every plan, incl. lifecare (0 vs 0.5) |
| absence relief | billed_level_daily_fee | method | charge / mean(charge, fee) / fee | yes — tier 2 is now a distinct method (**O5 closed**) |
| level increase | included_addon_offset | method | included in full / excess over new fee / none | yes — two distinct offset methods plus no offset; label honest |
| level increase | plan_discount_inside_charge | parameter | full pct / half pct / none | yes |
| advance payment | addon_recurrence | method | re-price at level carried / resume earlier month's amounts / recur at latest amounts | yes — three distinct methods; fall-through equals the declared baseline (`addons_billed_month`) |

- Other ladders unchanged from revision_1 and real.
- Counts: absence 5 (4P/1M); late fee 4 (3P/1M); level increase 4 (2P/2M); transfer 6 (5P/1M); returned fee 4 (3P/1M); advance 5 (3P/2M). All within 4-6 with >= 2 parameter and >= 1 method. Multi-source and cross-difficulty coverage per tree as in revision_1, plus entrance occupancy dates now read by the vested plan factors. **F2 closed.**
- O6 (realism: phase-in, payment standing) unchanged — no change claimed, none needed for a verdict.
- O7 (handling-date inclusion in "whole months before the handling date" windows): charter text unchanged; remains an observation.

### findings (revision_2)

- F1 closed; F2 closed; O2, O4, O5 closed; O3 partly closed; O6, O7 unchanged observations.
- **F3 — SOURCE-POLICY RED (new, introduced by the rework) — bears on task 0** (task 0 claims assisted_ext_level_increase_charge, whose rule carries the sentence, and its seed carries credits that follow one of the two readings). Symptom: two charter sentences fix different percentages for the same entrance plan discount credit. Root cause: rule sentence 10 of assisted_ext_level_increase_charge adds vesting to the general discount credit while assisted_entrance_and_respite_credits s2 is not superseded. Evidence: quotations above. Affected: `assisted.extended.yaml` assisted_ext_level_increase_charge rule (and the vesting premise in assisted_ext_absence_care_relief's plan sentence). Demonstrated consequence: 0.md revision_2.
- O8 (new observation): see override_declarations.

### post_reveal_note (revision_2)

Appended after the round-2 reveals (about 09:52Z); the revision_2 sections above were hashed before the reveal (441f9283…7778). Both blind re-derivations equal GT on every scored value, object, owner and order. Round-1 REDs: F1 closed, F2 closed. New: F3 SOURCE-POLICY RED (vesting of the general entrance plan discount credit in the level-increase rule vs unsuperseded base entrance_and_respite_credits s2), bearing on task 0. Per-task verdicts: task 0 — SOURCE-POLICY RED (F3); task 1 — PASS. The closing checklist is not written because task 0 does not pass.

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3, same independent auditor; written before any round-3 task JSON was opened. Revision_1 and revision_2 text above untouched (sha256 of this file before appending: 2d76873c…909a).
- Shared inputs: `assisted.extended.yaml` **changed** (de887ef6… -> b94a5d79071200cd6648351cfde755a57b35b439d85777eac24007e12dd2f254, identical in view and `tasks/`); `task_tools.py` unchanged (d6a8d689…2505); base lines 1-1527 still byte-identical to `blueprint/products/assisted.yaml`.
- Scope of the change (located by structure and by verbatim spot checks): the file grew by 6 lines, all inside assisted_ext_level_increase_charge — one new `overwrite` entry (assisted_entrance_and_respite_credits s2) and one new rule sentence ("Outside the level-increase charge the general billing rules stand: ..."); the vested-credit sentence now anchors vesting "on the posting date". The prerequisite sentences E1-E4, the E2 effect text, the absence relief plan and daily-fee sentences, the returned fee's restated guest-meal sentence and the advance payment's add-on recurrence sentence are present verbatim as in revision_2; the level-increase compute bindings (`offset_monthly`, `plan_discount_share`, `result`) and the absence relief `plan_reduction` binding are unchanged. Revision_2's charter-global sections are therefore carried forward for every other policy, and re-derived below for the level-increase policy.
- Entry conditions: coordinator gate snapshot (all OK; traceability deferred) and rebuilt MANIFEST supplied; hashes re-verified.

### override_declarations (revision_3)

- **F3 closed.** assisted_ext_level_increase_charge now names base assisted_entrance_and_respite_credits s2 ("The discount percentages are care_fee_discount_pct and rent_discount_pct of the agreement's plan, ... each applied to the charge amount and rounded to the cent half up.") as superseded, replaced by the vested-credit sentence (full percentages once the agreement is at least plan_vesting_months whole months old on the posting date, plan_vesting_half of them before). The merged semantics for a discount credit are unique; the seeded half-rate credits of May and June 2026 (58 and 59 months on their posting dates) and full-rate credits from July (60 months) follow it.
- **O8 closed.** New rule sentence: "Outside the level-increase charge the general billing rules stand: rent and the care level fee are billed in advance on fee_due_day ... ; the move-in month, the month of a rent change and the month in which fees end are prorated ...; and the care level a resident carries is always the level whose care_points_min to care_points_max band contains the care points of the most recent assessment." It restates the general content of the three superseded base sentences outside the level-increase charge, consistently with the policy's own sentences on the first day covered and on decreases. No new conflict: it names no tool, no other problem, and states no cross-problem order.
- New O9 (observation): the vesting of the plan discount is measured on the posting date for the discount credits (sentence above) but at the handling date for the absence-relief credit's plan reduction and the level-increase charge's plan share. A credit relieving a charge posted before the 60-month point but handled after it would return more than was paid. Neither task's world reaches that case (task 0: October charges posted at 63 months, handled at 64; task 1: 78+ months throughout), so no consequence is demonstrable.

### rule_compute_equivalence / prerequisite_graph / prerequisite_sentences / factor_ladders (revision_3)

- Level-increase compute unchanged; the two new sentences are not compute items of this policy (its target tool posts only increase charges) — equivalence holds.
- Graph, sentences, forms, gates and `resolved_by` unchanged; revision_2 conclusions carried forward.
- Factor ladders and counts unchanged from revision_2 (all real; absence 5, late fee 4, level increase 4, transfer 6, returned fee 4, advance 5). F1, F2 remain closed.

### findings (revision_3)

- F3 closed; O8 closed; F1, F2, O2, O4, O5 remain closed; O3 partly closed (absence credit for absences spanning months still single-month); O6, O7, rounding observation unchanged; O9 new observation.
- No charter-global RED open.

### post_reveal_note (revision_3)

Appended after the round-3 reveals (10:25Z); the revision_3 sections above were hashed before the reveal (2fde8251…6d58). Both blind derivations equal GT on every scored value, object, owner, order and sensitivity figure. Per-task verdicts: task 0 — PASS; task 1 — PASS.

## closing_checklist

Written after revision_3, when both tasks pass all four relationships.

- Per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, `_difficulty.md` sits alongside; revisions 1-3 are appended in order with earlier text untouched; the latest comparison section of each task carries PASS.
- Coverage and scope: the six extended policies are covered — task 0 claims absence_care_relief, late_fee_assessment, level_increase_charge, apartment_transfer_fee; task 1 claims returned_payment_fee, advance_payment; the scopes (whole trees) are pairwise disjoint and jointly complete. Task tools and GT are closed; the six uuid8 tails (bb749fc3, 246a7744, 9f33663f, e633e519, 036f277a, 8dbe3a8d) are distinct, unpatterned and unchanged across rounds (`task_tools.py` d6a8d689…2505).
- Trees: task 0 has 3 prerequisite problems with 3 value_input edges and an owner=user root (sign_apartment_change_e633e519); task 1 has 1 prerequisite problem with 1 value_input edge and an owner=user root (submit_advance_payment_8dbe3a8d); the difficulty-wide prerequisite graph is a DAG of two components with no cross-task reference.
- Factors: every computation declares a self-sufficient baseline giving a definite number different from gold (397.26, 85.00, 338.23, 650.00; 40.00, 8894.32) and 4-6 real factors (5, 4, 4, 6; 4, 5) with >= 2 parameter and >= 1 method; each task has multi-source and cross-difficulty factors with seeded independent/entrance rows; every ladder has three distinct tiers stated in its rule; every factor bears weight against its baseline on its task's world.
- Gates on the final form: coordinator's post-round-3 snapshot — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred to the render stage (KB not published). Per Step 0 the auditor cites rather than runs them.
- Open observations (no RED): O3 residue (absence credit for absences spanning two months relates to one month only), O6 (realism of phase-in and payment-standing shares), O7 (handling-date inclusion in whole-month windows, documented), O9 (vesting anchor: posting date for discount credits vs handling date for the absence and level-increase plan factors), proof-figure rounding 365.62 / 268.12 (exact .625 / .125, half up gives .63 / .13; documented).
- The difficulty passes the source-layer audit.
