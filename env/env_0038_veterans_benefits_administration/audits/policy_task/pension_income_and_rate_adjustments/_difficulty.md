# Policy-task audit — pension_income_and_rate_adjustments / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), revision 1.
- Freeze time: 2026-10-06T03:31Z (wall clock). Written before any task's GT was revealed. Nothing in this section is derived from a revealed GT.
- Freeze hashes (re-computed in place, equal to the orchestrator MANIFEST):
  - `tasks/pension_income_and_rate_adjustments/pension.extended.yaml` sha256 `7992427baa266aa7484548b5938f47d451bfdca395455465ed4b1f5ca1593b22`
  - `tasks/pension_income_and_rate_adjustments/task_tools.py` sha256 `78bedbc3ea04911fdc6e3aaf070336c03230326364c06ad04dd0b18dba093202`
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (table shapes only), `blueprint/share_tools.py`, `blueprint/products/pension.yaml` (base), `blueprint/products/loan.yaml` (funding-fee refund rule only), the extended charter and `task_tools.py`. The masked views were used only to know which policies each task's world touches; no task JSON was opened.
- Masked and not read: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`; no earlier audit exists.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/erl0038/views/policy_task/pension_income_and_rate_adjustments/GATES.txt`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred to the KB step. Masked views and MANIFEST hashes supplied and verified. Entry conditions are met.
- Base copy: lines 1-1002 of the extended file are byte-identical to `blueprint/products/pension.yaml` (diff shows only one trailing blank line).

Policy inventory (7 extended policies; each target tool claimed once):

| id | target_tool (owner) | computes | prerequisite edges | world it is instantiated on |
| --- | --- | --- | --- | --- |
| pension_ext_benefit_income_statement | certify_benefit_income_d2f4edcf (user) | annual_amount | [] | task 0 |
| pension_ext_care_cost_rate_adjustment | record_rate_adjustment_fee79930 (agent) | adjusted_annual_rate | <- statement (value_input, state) | task 0 |
| pension_ext_increase_retro_release | release_retro_payment_a1af7a43 (agent) | gross_amount | <- care_cost (value_input, state) | task 0 (root) |
| pension_ext_one_time_payment_declaration | declare_lump_sum_cb649dee (user) | annual_amount | [] | task 1 |
| pension_ext_recurring_income_redetermination | update_countable_income_81bdd26c (agent) | annual_countable_income | [] | task 1 |
| pension_ext_net_worth_redetermination | update_net_worth_02de4f94 (agent) | net_worth | <- declaration (value_input, state); <- recurring (value_input, state) | task 1 |
| pension_ext_annual_rate_redetermination | record_annual_rate_redetermination_a1a40d3e (agent) | adjusted_annual_rate | <- recurring (value_input, state); <- net_worth (state_gate, state) | task 1 (root) |

### policy_conflict_scan

Overlapping subjects across the merged charter:

1. `pension_rate_adjusted` / `adjusted_annual_rate` is claimed by two extended policies with overlapping triggers. `pension_ext_care_cost_rate_adjustment` (trigger `state_due`): "A care-cost rate adjustment recomputes the annual pension when the veteran reports recurring care costs, such as an in-home aide, that he pays himself. ... an adjustment that raises the rate, or one that rests on a report the veteran sent, is recorded as soon as it is computed." `pension_ext_annual_rate_redetermination` (trigger `on_request`): "When a veteran asks VA to settle what his pension will be after one-time payments and new care costs, VA redetermines the annual pension going forward and records it as a rate adjustment." When a veteran has sent care-cost reports and also asks for the settlement, both rules apply to the same reports and reach incompatible conclusions. The effective date is "the first day of the month after the month in which the earliest reported care month began" in one and "the first day of the month after the month in which the most recent change it reflects began" in the other. The source is "the report of the most recent care month" in one and "the veteran's one-time payment declaration" in the other. The channel is that report's channel in one and the declaration's channel in the other. The value methods also differ: own income from the statement versus countable income on the award plus one-time payments, and premiums by rate-adjustment recency versus premiums by report age. No sentence says which governs. Recorded as finding G4; it applies to task 1's world, which has four veteran-sent care reports received 2026-10-02 and an explicit settlement request.
2. `pension_income_change_reported` / `annual_amount` is written by two user tools, statement and declaration. They write identical rows (`event_type=pension_income_change_reported`, `income_source=other`, `report_channel=phone`), and the readers (`care_cost.statement_amount`, `net_worth.declared_amount`, `annual_rate.declared_amount`) take `LATEST(... income_source='other')` without telling them apart. Neither task world contains both kinds, so nothing is demonstrable. Recorded as observation G9.
3. `pension_financials_updated`: recurring income writes `annual_countable_income` and net worth writes `net_worth`. The fields are disjoint and the order is fixed by net worth's own prerequisite sentence. No conflict.
4. Compensation as income. Base `pension_excl_compensation` says "Compensation paid to the veteran counts as income for pension". The statement policy says monthly compensation in election months "is settled against the pension instead of being counted as income", and the release-share tiers also cut how much of the retroactive compensation counts. This is an undeclared override (G1). Recurring-income "no compensation recurs" after election is forward-looking and is consistent with base, because compensation is no longer paid.
5. Effective date of a rate decrease. Base `pension_evt_income_change`: "An income increase lowers the rate effective the last day of the month in which the change began". The annual-rate redetermination always uses "the first day of the month after ...". This is an undeclared override (G2).
6. Medical threshold base. Base `pension_rate_computation`: "medical_expense_threshold_pct percent of the category's medical_deduction_base_mapr". Three extended ladders (care_cost, net_worth, annual_rate) substitute a household-dependent base whose fall-through is "the basic rate for a veteran alone" even for spouse-counting categories. This is an undeclared override (G3).
7. Income-match due process: the care-cost policy's declared overwrite narrows the base 60-day clause to rate-lowering matches. It is declared, and its merged meaning is unique. No task world has an income match.
8. Cross-category read boundaries: every cross read (comp, loan, debt) is declared under `cross_category` and reads only the customer's own rows. The read and write boundaries are clean.

Scope partition: task 0 spans {statement, care_cost, retro_release} and task 1 spans {declaration, recurring, net_worth, annual_rate}. The two are pairwise disjoint and jointly cover all 7 extended policies. Observation G16: four claimed event types (`pension_medical_expenses_reported`, `pension_asset_transfer_reported`, `pension_rate_category_changed`, `pension_payment_profile_updated`) are written by no extended policy or task tool.

### rule_compute_equivalence

A mechanical sweep confirms that every `compute_basis` quotation is a verbatim substring of its policy's `rule` and that every sentence of every `baseline.rule` is in its `rule`. Sentence-by-sentence findings:

- **statement**: every compute binding traces to a rule sentence. The retro-share tiers, months-before-pension (`MONTHS(comp_eff, pension_eff) + payment_start_lag_months`) and rounding after the share all match. No invented basis.
- **care_cost**: own-income recency, spouse COLA, threshold-base, premium-recency, care monthly and care-months tiers all match. Gap (observation G13): `care_latest` and `care_latest_end`/`care_received` take `LATEST` over every `pension_medical_expenses_reported` row with no window. The rule speaks of "the most recent month" of "the care months reported" in the three-month window, so a premium report with a later `expense_period_start` would be read as the most recent care month. Neither world triggers it: task 0's 2026-05-01 premium period precedes the July care month, and task 1's reports are all in the window.
- **retro_release**: months owed, amount already paid, returned payments, compensation subtraction and release share all match. The period sentence ("runs from the month of that adjustment's effective date through the entitlement month of the most recent monthly payment") fixes the months owed, so no tier stands only in compute.
- **declaration**: period, fee cap, withheld-part add-back, refunds left out and release counted all match. The "fee cap share, rounded to the cent" comparison is as stated.
- **recurring**: the SS/spouse COLA, interest scaling and compensation recurrence all match. The baseline's "all compensation issued" includes the retroactive release, and the compute does the same.
- **net_worth**: assets last determined, release cash, refunds, loan subtraction, declared one-time income, threshold base and income after deduction all match.
- **annual_rate**:
  - (a) The **care-months tiers do not match** (G6). The rule's first tier reads "the most recent care month ended no more than the ongoing-care gap *after* the report reached VA". The compute is `care_gap_days = DAYS(care_latest_end, care_received)`, i.e. days the month ended *before* the report. The rule's second tier reads "it ended longer *before*". For a care month that ended 100 days before its report, rule tier 1 holds (the month did not end more than 92 days after the report) and so does rule tier 2 (it ended longer before). The rule therefore says both "ongoing, x12" and "ended, x count" for the same situation, while compute says "ended".
  - (b) The **premium tiers overlap as stated** (G5). "premium reports received between three and twelve whole months before the redetermination count at their total; when the only premium reports are twelve to twenty-four whole months old, ... Part B ...". A report exactly twelve whole months old satisfies both, while compute (`within_months` half-open) puts it only in the second.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique across the seven policies; no tool is claimed twice.
- Docstrings carry no ordering word (before/after/first) and name no other tool. Two docstrings refer to another write's output: `release_retro_payment.adjustment_id` "... or returned when that adjustment was recorded" and `record_annual_rate_redetermination.source_report_id` "... or returned when it was filed". Each describes where an id comes from, not a sequence. Observation G10b.
- Near-duplicate tools (observation G10). `record_rate_adjustment_fee79930` and `record_annual_rate_redetermination_a1a40d3e` have identical signatures and write identical rows (`event_type=pension_rate_adjusted`, `penalty_months=0`, `overpayment_created=False`); they differ only in id prefix (`pra_`/`prd_`). The first docstring ("a rate adjustment that sets a new annual pension from a given effective date, made from a report already on the award") also fits the annual redetermination, whose rule says it "records it as a rate adjustment". The two user tools are likewise near-duplicates (G9). Business words ("redetermination ... going forward" against "rate adjustment") separate them, so no second reading is demonstrated. Recorded as an observation.
- None of the tool bodies checks a precondition: each one only calls `ctx.find` (for customer_id), `ctx.create` or `ctx.update`. The tool layer judges no prerequisite.
- uuid8s: d2f4edcf, fee79930, a1af7a43, cb649dee, 81bdd26c, 02de4f94, a1a40d3e. All seven are distinct. `a1af7a43` and `a1a40d3e` share the prefix `a1a`, which has about a 0.5% chance of happening by accident over 21 pairs. Batch derivation cannot be demonstrated, so this is observation G14.

### prerequisite_graph

- `prerequisite` is filled in on all 7 policies, with `[]` on statement, declaration and recurring.
- Edges: care_cost<-statement, retro<-care_cost, net_worth<-declaration, net_worth<-recurring, annual<-recurring, annual<-net_worth. Every edge points at an extended policy id other than itself. The graph is acyclic, with topological orders statement -> care_cost -> retro and {declaration, recurring} -> net_worth -> annual.
- `policy_source` is verbatim in the blocked policy's own rule for all 6 edges, and none appears in the depended-on rule (mechanical check).
- `form: state` on all 6 edges. No `fallback_reason` is present or needed.
- `resolved_by` equals the depended-on policy's `target_tool` on all 6 edges.
- `kind`/`gate`: the value_input gates `statement_amount`, `new_annual`, `declared_amount` and `income_on_award` (both net_worth and annual) are real compute bindings. The state_gate `pension_awards.net_worth` is the real `payable` gate (`F('net_worth') <= P('net_worth_limit')`).
- Condition strength:
  - annual<-net_worth: the condition requires net worth to include "the compensation release and refunds deposited since opened_date, the declared one-time income and the redetermined countable income". The sentence says only "counts every one-time VA payment deposited since the award was granted", so the condition is stronger than the sentence. The depended-on policy's own rule writes all of these at once, so the resolving action is the same. Observation G12.
  - retro<-care_cost: the condition adds "recorded after the most recent monthly payment", which the sentence implies by "months already paid". This is accepted.
- No authoring-viewpoint phrasing in `prerequisite`.
- Whether each edge bears weight is decided per task (see the task files).

### prerequisite_sentences

| edge | sentence (verbatim) | connective | state named | single resolving write | reading |
| --- | --- | --- | --- | --- | --- |
| care_cost <- statement | "The new annual rate is fixed only after the award carries a benefit income statement from the veteran dated on the day his VA disability compensation stopped." | only after | an income change report from the veteran dated on the compensation award's closing date | statement rule ("that statement is the income change report ... dated as a change that began on the date the compensation award closed") -> certify_benefit_income. The declaration also writes `income_source=other`, but its rule dates it "on the date of the most recent compensation release", and business words ("benefit income statement" against "declaration of one-time payments") separate the two | single |
| retro <- care_cost | "A retroactive release for months already paid is not issued until the award carries a rate adjustment that raises the annual pension for those months." | not ... until | a rate adjustment raising the annual pension for paid months | care_cost rule ("recomputes the annual pension when the veteran reports recurring care costs ... takes effect on the first day of the month after the month in which the earliest reported care month began"), a retroactive effective date. The annual redetermination is a second candidate writer of a `pension_rate_adjusted` row, but its rule is "going forward" and is on request (observation G11) | single |
| net_worth <- declaration | "Net worth is not redetermined until the award carries the veteran's own declaration of the one-time VA payments deposited to him, dated on the date of the most recent compensation release." | not ... until | a veteran's declaration report dated on the latest compensation release date | declaration rule -> declare_lump_sum | single |
| net_worth <- recurring | "Net worth is redetermined only after the countable income on the award reflects the recurring income on file as of the redetermination." | only after | award countable income equals redetermined recurring income | recurring rule -> update_countable_income (the only writer of `annual_countable_income`) | single |
| annual <- recurring | "The redetermined annual rate is fixed only after the countable income on the award has been brought up to the recurring income on file." | only after | same as above ("brought up to" is directional; observation G18) | update_countable_income | single |
| annual <- net_worth | "A redetermined annual rate is not recorded until the net worth on the award counts every one-time VA payment deposited since the award was granted." | not ... until | award net worth counts deposits since grant | net_worth rule -> update_net_worth (the only writer of `net_worth`) | single |

No rule restates a dependency in a second wording, and none names a tool, a policy id or a snake_case token. The base rule `pension_payment_schedule` states orders within base, and none of those grounds an edge here. The annual rule's "it names as its source the veteran's one-time payment declaration" makes the root read the declaration directly, but it is not an ordering sentence. The order is entailed transitively through the net-worth sentence (observation G19).

### override_declarations

Sentence by sentence against each `base_policy_refs` entry. "Follows" means the scored quantity is the same under base:

- **statement** (refs `pension_evt_income_change`, overwrite []):
  - "Every change in a household income source must be reported ... telephone, online or by mail": followed (phone).
  - The effective-date sentences do not govern `annual_amount`.
  - **Outside the refs, conflict**: `pension_excl_compensation` "Compensation paid to the veteran counts as income for pension." The statement says "no monthly compensation is stated, because the months it paid were also months of pension and are settled against the pension instead of being counted as income". The share rule "when the compensation effective date falls on or after the pension effective date, none of it counts" also counts only part of the retroactive release. Neither is declared. The author's own phrase "instead of being counted as income" acknowledges the deviation. This is **G1**.
- **care_cost** (refs rate_computation, income_change, medical_expenses, net_worth_and_transfers, income_match; overwrite = income_match clause, declared):
  - rate_computation, "the annual pension equals the maximum annual pension rate ... minus countable income after the medical deduction, and is never below zero": followed.
  - "Unreimbursed medical expenses reduce countable income only by the amount that exceeds medical_expense_threshold_pct percent of the category's medical_deduction_base_mapr": **not followed** on the threshold-household fall-through and first tier (**G3**). Not declared.
  - medical_expenses, "The annual total for the evaluated period (pension_msr_annual_medical_expenses) replaces the prior figure": extended adds the award's figure (premiums) to the care cost rather than replacing it. The base "evaluated period" is not pinned for a prospective care adjustment, so no definite second number follows. Observation G20.
  - income_change, "An income decrease raises the rate from the first day of the month after the month the change began": followed.
  - The reporting-window sentence is followed.
  - net_worth: no sentence governs `adjusted_annual_rate` beyond payability, which the rule does not drop.
- **retro_release** (refs income_change, medical_expenses, care_and_dependents; overwrite []):
  - "the higher amount for months already paid is released as a retroactive payment": extended also subtracts compensation paid for pension months. That rests on base `pension_excl_compensation` "never paid to the same veteran for the same month", which supports an offset. Not a conflict.
- **declaration** (refs income_change; overwrite []):
  - Reporting sentences are followed.
  - "VA refunds of the veteran's own money are not income" sits against base `pension_rate_computation` "every source except the excluded sources". A refund of one's own money is arguably not an income source, so this is observation G21, not a conflict.
- **recurring** (refs rate_computation, medicaid; overwrite []):
  - "Countable income is the annualized income of the veteran from every source except the excluded sources, plus the spouse's income ...": followed. Recurring sources are annualized; one-time payments are kept apart by the policy's own sentence, which base does not contradict because base speaks of annualized income.
- **net_worth** (refs rate_computation, medicaid, net_worth_and_transfers; overwrite []):
  - "net worth - assets other than the primary residence ... plus annual countable income": followed.
  - Threshold fall-through: **G3** again.
- **annual_rate** (refs rate_computation, income_change, medical_expenses, net_worth_and_transfers, income_match; overwrite []):
  - income_change, "An income increase lowers the rate effective the last day of the month in which the change began, and the lower rate is paid from the following month": **not followed**. The rule says "The redetermined rate takes effect on the first day of the month after the month in which the most recent change it reflects began", whether the redetermination lowers or raises the rate. Not declared (**G2**).
  - Threshold fall-through: **G3**.
  - "No pension is payable while net worth ... exceeds net_worth_limit": followed (`payable`).

### factor_ladders

A tier is struck when (i) two tiers of the ladder are one rule written twice, meaning the tier's value equals the other tier's formula evaluated in that tier's own situation, or (ii) a condition or outcome is one VA does not weigh or would not publish. A factor whose ladder falls below three distinct real tiers is struck. Counts are after striking.

| policy | factor (label, cross) | tiers distinct and real? | survives |
| --- | --- | --- | --- |
| statement | social_security_adjustment_years (param) | x1.0537 / x1.028 / x1. Real: the 2026 COLA is 2.8% and the 2025 COLA is 2.5%, so 1.028 x 1.025 = 1.0537 | yes |
| statement | monthly_compensation_treatment (method, comp; multi-source: comp award termination_reason + comp ledger) | 0 (election) / latest x12 (running) / as issued | yes |
| statement | retroactive_release_fee (param, comp) | "release less the withheld fee" vs "the gross release" when no fee was withheld: the second is the first with fee = 0, so one rule (gross - fee) is written as two. Real ladder = {gross - fee, 0} | **no** (2 tiers) |
| statement | retroactive_release_pension_months (param, comp) | ratio / 0 / 1 | yes |
| care_cost | own_income_statement_recency (method) | statement / max(statement, award) / award | yes |
| care_cost | spouse_social_security_adjustment_years (param) | COLA tiers | yes |
| care_cost | medical_threshold_household (param) | Tier-2 conjunct "a spouse income figure is on file" is not something VA weighs: the 5% threshold follows the MAPR for the household with its dependents (38 CFR 3.278), whether or not the spouse has income. The fall-through "basic rate for a veteran alone" for a spouse-counting category is not a treatment VA publishes, and it also contradicts base (G3) | **no** |
| care_cost | premium_confirmation_recency (param) | Fall-through "when the award has no rate adjustment, premiums add nothing" discards medical expenses already accepted on the award at grant. No VA practice ignores accepted expenses because no adjustment has yet been recorded, so this is a straw-man fall-through | **no** |
| care_cost | care_monthly_figure (method) | latest / average / total | yes |
| care_cost | care_months_counted (param) | 12 / count / 1 | yes |
| retro | months_owed_from_payments (method) | count paid / whole months / through current month | yes |
| retro | amount_already_paid (method) | Tier 1 "monthly payments issued plus the earlier release" vs tier 2 "the monthly payments issued" when no earlier release: tier 2 = tier 1 with release = 0. Real ladder = {issued + release, latest x months} | **no** (2 tiers) |
| retro | returned_payment_owed (param) | "gross when nothing withheld" vs "net that came back when part withheld": on tier 1's situation, net that came back = gross. One rule (what came back) is written as two. Real ladder = {what came back, 0} | **no** |
| retro | monthly_compensation_subtracted (param, comp) | all since pension effective / in months owed / 0 | yes |
| retro | retroactive_compensation_considered (param, comp) | same pattern as retroactive_release_fee | **no** |
| retro | retroactive_compensation_pension_share (param, comp) | ratio / 1 / 0 | yes |
| declaration | declaration_period (method) | since pension effective / since prior declaration / 12 months | yes |
| declaration | representative_fee_taken_out (param, comp; multi-source: comp award `attorney_fee_agreement_on_file` + comp payment fee) | fee / 20% cap / 0. The cap is real (38 CFR 14.636) | yes |
| declaration | debt_withholding_added_back (param, debt) | "whole withheld part" vs "withheld part less the refund" when a refund exists: tier 1 = tier 2 with refund = 0 | **no** |
| declaration | own_money_refunds_left_out (param, loan) | Tier-1 condition "comp effective date on or before the loan's closing date" holds for every refund on the retroactive-award ground (`loan.yaml` refund rule), and VA does not weigh it when deciding whether a refund of the veteran's own money is income: a refund on the Purple Heart or fee-in-error ground is equally his own money. Tier-2 conjunct "AND no funding fee refund was" makes an overcollection refund count as income merely because a funding-fee refund also arrived. No business weighs that | **no** |
| recurring | veteran_social_security_adjustment_years (param) | COLA tiers | yes |
| recurring | spouse_social_security_level_age (param) | COLA tiers | yes |
| recurring | interest_follows_savings (param, comp) | All three tiers are one formula `interest x (assets + deposits - transfers)/assets`: tier 2 has deposits = 0, and tier 3 ("as reported") has deposits = transfers = 0 | **no** |
| recurring | compensation_recurrence (method, comp) | 0 / rate x12 / issued | yes |
| net_worth | compensation_release_cash (param, comp) | "net amount deposited when part withheld" vs "gross when nothing withheld": on tier 2's situation, net = gross. One rule | **no** |
| net_worth | refunds_cash (param, loan) | All three tiers equal `fee_refund + debt_refund` (tier 2 has fee = 0, tier 3 has both = 0). The ladder is one sum | **no** |
| net_worth | home_loan_subtraction (param, loan) | 0 / partial-claim balance / unpaid principal. Distinct; the residence exclusion is real | yes |
| net_worth | declared_one_time_income (method) | full / prorated / none | yes |
| net_worth | net_worth_threshold_household (param) | same defect as medical_threshold_household | **no** |
| net_worth | income_after_medical_deduction (method) | income - d / 0 / income: a floor clamp, max(0, income - max(0, d)). Accepted as distinct values, but the `method` label is doubtful (observation G17) | yes |
| annual | one_time_payments_counted (method) | full / prorated / none | yes |
| annual | rate_threshold_household (param) | same defect as medical_threshold_household | **no** |
| annual | premium_report_age (param) | tiers overlap as stated at exactly twelve whole months (G5) | **no** |
| annual | redetermined_care_monthly (method) | latest / average / total | yes |
| annual | redetermined_care_months (param) | tiers overlap as stated for months ending more than 92 days before the report (G6) | **no** |

Surviving counts against the bounds (4-6 in all, at least 2 parameter, at least 1 method):

| policy | declared | surviving | parameter / method | verdict |
| --- | --- | --- | --- | --- |
| statement | 4 | 3 | 2 / 1 | **below 4** |
| care_cost | 6 | 4 | 2 (spouse COLA, care months) / 2 | meets |
| retro | 6 | 3 | 2 / 1 | **below 4** |
| declaration | 4 | 2 | 1 / 1 | **below 4, below 2 parameter** |
| recurring | 4 | 3 | 2 / 1 | **below 4** |
| net_worth | 6 | 3 | 1 (home loan) / 2 | **below 4, below 2 parameter** |
| annual | 5 | 3 | 0 / 2 | **below 4, below 2 parameter** |

Per task, after striking:
- Task 0 keeps a multi-source, cross-difficulty factor (monthly_compensation_treatment: comp award + comp ledger).
- Task 1 keeps one too (representative_fee_taken_out: comp award flag + comp payment). Task 1 also keeps home_loan_subtraction (loan, single record).
- Every ladder is stated in full in its rule, and every rule tier has a compute branch. The two annual-rate exceptions are G5 and G6 (stated so that tiers overlap).

### findings

- **G1 — SOURCE-POLICY RED (undeclared override).**
  - Symptom: the statement policy drops monthly compensation and part of the retroactive compensation from "income", although base says compensation counts.
  - Root cause: `pension_excl_compensation` is not in `base_policy_refs`, and `overwrite: []`.
  - Evidence: base "Compensation paid to the veteran counts as income for pension." Extended "no monthly compensation is stated, because the months it paid were also months of pension and are settled against the pension instead of being counted as income".
  - Consequence: two values for `certify_benefit_income.annual_amount` whenever an election-ended compensation award paid monthly compensation in the window.
  - Bears on task 0, demonstrated there.
  - Realism note: the extended treatment matches real VA offset practice (38 CFR 3.700). The defect is that it is not declared.
- **G2 — SOURCE-POLICY RED (undeclared override).**
  - Evidence: base `pension_evt_income_change` "An income increase lowers the rate effective the last day of the month in which the change began". Annual-rate rule "The redetermined rate takes effect on the first day of the month after the month in which the most recent change it reflects began". `pension_evt_income_change` is in `base_policy_refs`, and `overwrite: []`.
  - Real VA practice (38 CFR 3.660(a)(2)) is the base sentence.
  - Bears on task 1 (`change_effective_date`), demonstrated there.
- **G3 — SOURCE-POLICY RED (undeclared override), with no consequence on either world.**
  - Evidence: base `pension_rate_computation` "...percent of the category's medical_deduction_base_mapr". Extended threshold ladders (care_cost, net_worth, annual) use "otherwise it is the basic rate for a veteran alone".
  - Same situation, one-dependent category with no spouse income report and no children: base gives 22838 x 5% = 1141.90, extended gives 17440 x 5% = 872.00.
  - Both task worlds sit on the "spouse figure on file" tier (22838), so neither task's scored value is moved.
- **G4 — SOURCE-POLICY RED (policy conflict on `adjusted_annual_rate`).**
  - The care-cost (state_due) and annual-rate (on_request) policies both fire when a veteran who sent care-cost reports asks for a settlement.
  - They give incompatible effective date, source, channel and value (see policy_conflict_scan 1).
  - Bears on task 1, demonstrated there.
- **G5 — SOURCE-FACTOR RED (ladder overlaps as stated).**
  - `premium_report_age`: "between three and twelve whole months" vs "twelve to twenty-four whole months".
  - Bears on task 1, whose only premium-type report, received 2025-09-18, is exactly twelve whole months old on 2026-10-07. Demonstrated there.
- **G6 — SOURCE-POLICY/SOURCE-FACTOR RED (rule direction contradicts compute; tiers overlap as stated).**
  - `redetermined_care_months`: "ended no more than the ongoing-care gap after the report reached VA" vs "it ended longer before"; compute measures days before.
  - Task 1's latest care month ends after its report (-29 days), so every reading gives "ongoing". No consequence on task 1's scored value.
- **G7 — SOURCE-FACTOR RED (one rule written as two or three tiers).** Affected factors:
  - retroactive_release_fee
  - amount_already_paid
  - returned_payment_owed
  - retroactive_compensation_considered
  - debt_withholding_added_back
  - interest_follows_savings
  - compensation_release_cash
  - refunds_cash

  Bears on task 0 (statement and retro fall below 4 factors) and task 1 (declaration, recurring, net_worth fall below the bounds).
- **G8 — SOURCE-FACTOR RED (unreal conditions or outcomes).** Affected factors:
  - medical_threshold_household, net_worth_threshold_household and rate_threshold_household ("a spouse income figure is on file"; the veteran-alone fall-through for spouse-counting categories)
  - premium_confirmation_recency (the no-adjustment fall-through discards accepted expenses)
  - own_money_refunds_left_out (the comp-effective-vs-closing condition and the "no funding fee refund" conjunct)

  Bears on task 0 (care_cost still meets 4 after striking) and task 1 (annual drops to 3 with 0 parameter).
- Observations (not grounds for rework):
  - G9: indistinguishable user-tool rows (`income_source=other`).
  - G10: near-duplicate rate-adjustment tools. G10b: docstrings point at another write's returned id.
  - G11: the retro-release state could in principle be produced by the annual redetermination tool.
  - G12: the annual<-net_worth condition is stronger than its sentence.
  - G13: `care_latest` is not windowed.
  - G14: the `a1a` uuid prefix collision.
  - G15: "the fresh period", "the ongoing-care gap" and "the response period" are named in rule prose without their day counts, which sit only in `params`.
  - G16: four claimed event types are uncovered.
  - G17: income_after_medical_deduction labelled `method` is a clamp.
  - G18: "brought up to" is directional while the condition is equality.
  - G19: the annual rule reads the declaration without its own prerequisite sentence (reached transitively).
  - G20: the base "replaces the prior figure" sentence against the extended additive medical figure.
  - G21: refunds-not-income against base "every source".

## closing_checklist

Written after both reveals (2026-10-06T03:36Z or later). This section is not part of the pre-reveal charter-global freeze above.

**Erratum to the pre-reveal § factor_ladders count table.** This is an arithmetic slip, not a GT-driven change, and the text above is left as written. The annual-rate row should read surviving **2** (0 parameter / 2 method), not 3: one_time_payments_counted and redetermined_care_monthly survive, while threshold, premium_report_age and redetermined_care_months are struck. G8's parenthetical "annual drops to 3 with 0 parameter" should read 2. The verdict is unchanged.

The difficulty does **not** pass the source-layer audit. Checklist status:

| item | status |
| --- | --- |
| per-task files 1:1 with tasks (`0.md`, `1.md`) + `_difficulty.md`; old revisions traceable (revision 1, none earlier) | done |
| every comparison section carries PASS | **no**. Task 0: SOURCE-POLICY / SOURCE-CHAIN / SOURCE-FACTOR RED. Task 1: SOURCE-POLICY / SOURCE-CHAIN / SOURCE-FACTOR / SOURCE-TASK RED |
| extended policies fully covered; scopes pairwise disjoint (task 0: 3 problems, task 1: 4 problems) | yes |
| task tools and GT closed; uuid8s independent | tools closed. uuid prefix collision a1af7a43 / a1a40d3e recorded as observation G14 |
| each tree has 1-3 prerequisite problems, at least max(n-1,1) value_input edges, a customer write, no cycle; the difficulty's graph is a DAG | yes structurally (task 0: 2 prerequisites / 2 value_input / user statement; task 1: 3 / 3 / user declaration). But task 0's persona hints at the first hop, and task 1's state_gate edge does not bear weight |
| each computation has a self-sufficient baseline giving a definite non-gold number | yes for all 7 computations (whole-baseline values: 17281.68, 4098, 9163.0, 13863.64, 42371.64, 62726.05, 11218; each differs from gold) |
| 4-6 real factors per computation (2 parameter, 1 method), every ladder 3 or more distinct and real tiers | **no**. Statement 3, retro 3, declaration 2, recurring 3, net worth 3, annual 2 surviving (G5-G8) |
| per task, at least 1 multi-source and 1 cross-difficulty factor with seeded rows | yes (task 0: monthly_compensation_treatment; task 1: representative_fee_taken_out) |
| instantiation gates re-run on the final form | not re-run by the auditor (out of its role). The artifacts are unchanged since the gate snapshot: `pension.extended.yaml` and `task_tools.py` hashes are identical to the MANIFEST at close; `tasks/0.json` sha256 `adf19ef8...61ed04`, `tasks/1.json` sha256 `a5cf255f...958af7` |

Charter-global findings and the tasks that demonstrate them:
- G1: task 0
- G2: task 1
- G3: none
- G4: task 1
- G5: task 1
- G6: none
- G7: tasks 0 and 1
- G8: tasks 0 and 1

Additional stale proof text found at reveal (observation): task 0's `design_rationale` claims that record_rate_adjustment_fee79930 is the only write that can bring a raising adjustment about, because task 1's "penalty adjustment ... records an annual pension of 0". The final charter has no such policy, and its annual redetermination tool can record any rate.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent auditor as revision 1, re-audit round 2. Written 2026-10-06 ~06:2xZ, before any round-2 task JSON was opened. Nothing in this section is derived from a revealed GT.
- Re-derive rule applied:
  - `pension.extended.yaml` changed: round 1 `7992427b...ca1593b22`, round 2 `72f10d2b7c930f9af018f354ce6f8af35edfe5482d0051fd924cb4dd3a5f4a0b`. Every charter-global section below is re-derived in full from the round-2 file.
  - `task_tools.py` is unchanged (`78bedbc3...a093202`), so § action_binding_and_uuids is carried forward by reference to revision 1, apart from the G10/G11 notes below.
  - Base copy (lines 1-1002) is still byte-identical to `blueprint/products/pension.yaml`.
- Entry conditions: the fresh gate snapshot `/tmp/erl0038/views/policy_task/pension_income_and_rate_adjustments/GATES.txt` lists all 8 lines green, with traceability deferred. The rebuilt masked views match MANIFEST (`task_0.view.json` `dfac64e7...0ba9`, `task_1.view.json` `f94df35d...89d8`).
- Masked fields: the same nine as revision 1. The reworker's closure claims were taken as item ids only, not as evidence.

### policy_conflict_scan (revision 2)

1. `adjusted_annual_rate` is claimed by care_cost and annual_rate, as before.
   - New care-cost sentence: "A care-cost rate adjustment is not recorded for a veteran who has asked VA to redetermine his pension going forward; the care costs he reported are then taken into that redetermination."
   - New annual-rate sentence: "Recurring care costs the veteran has reported that no rate adjustment has yet taken in are taken into the redetermination, and no separate care-cost rate adjustment is recorded for them."
   - The two triggers are now exclusive: an on-request settlement excludes the care-cost adjustment. **G4 closed.**
2. `pension_excl_compensation` "Compensation paid to the veteran counts as income for pension."
   - Statement: the sentence is now declared in `overwrite` and replaced by "counts as income for pension only for months before pension was first paid; compensation paid for a month that pension also paid is settled against the pension for that month and is not counted as income". The merged meaning is unique on the election-ended world. **G1 closed for the statement.**
   - **Declaration (new, R2-N1)**: `pension_ext_one_time_payment_declaration` now lists `pension_excl_compensation` in `base_policy_refs` but keeps `overwrite: []`. Its rule says the releases "count by the months the most recent release was paid for, because compensation is never paid for a month the pension is also paid: ... only the share for the months before the pension effective date counts ... otherwise it is settled against the pension, and nothing counts".
   - For a release straddling the pension effective date, base counts all of it and the declaration counts a share. That is an undeclared override of the same base sentence. The statement's declaration does not cover another policy: each policy must declare in its own `overwrite`.
   - Two further mismatches:
     - Statement and declaration measure "before pension" differently. The statement uses "before pension was first paid" (effective date plus payment lag); the declaration uses "before the pension effective date". The effective month itself falls before the first paid month but is not before the effective date, so the two rules count it differently.
     - Statement tiers 2 and 3 count compensation issued or projected in months that pension also paid. A running award projected for 12 months, or "as issued", contradicts the policy's own declared replacement sentence. No consistent world has a running compensation award together with a running pension, which base forbids, so this is an observation (R2-O1).
3. Income-decrease and increase effective dates. The annual rate now says "When the redetermined rate is lower than the rate being paid, it takes effect on the last day of the month in which the most recent change it reflects began and the lower rate is paid from the following month; when it is higher, it takes effect on the first day of the month after that month". This matches base `pension_evt_income_change` on both sides. **G2 closed.**
4. Medical threshold. Care_cost, net_worth and annual_rate all use "the category's basic rate for the medical deduction", i.e. `P('medical_deduction_base_mapr')`, which is base. The household-threshold factors are removed. **G3 closed.**
5. Net worth posting (new sentence, R2-O2): "When a compensation release is paid to a pensioner, its gross amount is posted to the net worth on the award at once and stays there until net worth is redetermined."
   - No write of this difficulty or of base performs the posting. It is asserted as a ledger convention, and the seed must carry it.
   - Realism: VA's net worth on a pension award is a determination (assets + annual income, 38 CFR 3.274), not a running ledger. Posting the *gross* release also counts the representative's fee and any debt offset, which never reached the veteran.
   - Base `pension_evt_net_worth_and_transfers` says "an award whose net worth rises above the limit is terminated for excess net worth". A posted figure above the limit therefore invites a termination reading before redetermination. The extended text's "stays there until net worth is redetermined" makes the figure provisional, and no termination tool is in this difficulty.
   - Recorded as a realism observation. Its consequence for task 1's state gate is assessed in `1.md`.
6. Cross-category read boundaries: debt is no longer read; reads are confined to comp and loan. The read boundaries are clean.

Scope partition: unchanged and disjoint. Task 0 covers statement, care_cost and retro; task 1 covers declaration, recurring, net_worth and annual. G16 (four uncovered event types) still stands as an observation.

### rule_compute_equivalence (revision 2)

Mechanical sweep: every `baseline.rule` sentence is in its rule, and every `compute_basis` quotation is verbatim in its rule, **except one**. `recurring.compute_basis.ss_figure` quotes "In the standard redetermination each Social Security figure and the interest figure are taken as reported on the most recent report of that source". The rule now reads "each Social Security figure, the annuity figure and the interest figure are taken as reported ...". This is a stale quotation. The binding's substance is supported by the new sentence, so no consequence follows. Observation **R2-O3**, a regression introduced by the rework.

Policy by policy:
- **statement**: the fee tiers, the share applied to "the release less the fee taken out", and rounding all match compute.
- **care_cost**: annuity FERS tiers (1.02 / 1.0404), premium confirmation (one year: in full; up to two years: Part B; otherwise 0, with "by the grant of the award" when the award has no adjustment), care tiers ("before the report reached VA" / "more than that gap before"). All match.
- **retro**: the fee-taken-out tiers and lump share match.
- **declaration**: the period, fee, share by the months of the most recent release (`MONTHS(start, end) + 1`; months before the effective date, capped), and deposit recency (90 days / one year / none) match.
- **recurring**: the annuity tiers and compensation recurrence (election / ended otherwise / running) match.
- **net_worth**:
  - "less every compensation release posted to it since the award was granted" = `releases_posted` (gross, since `opened_date`).
  - The premium tiers "three to eleven" / "twelve to twenty-three" are half-open and disjoint.
  - The care-months tier "no more than the ongoing-care gap before the report reached VA, or ended after it" matches `care_gap_days <= 92`.
- **annual_rate**: the same premium and care tiers. **G5 and G6 closed.**
- G13 (`care_latest` not windowed) persists. Observation, no change.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged, so revision 1 is carried forward. Notes:
- G10 (near-duplicate rate tools) is no longer a live conflict: the care-cost rule now excludes itself whenever a settlement is requested.
- G11: the second candidate writer of a raising adjustment remains in principle. The task-0 rationale's claim is checked at the reveal.
- G9, G10b and G14 are unchanged observations.

### prerequisite_graph and prerequisite_sentences (revision 2)

Mechanical check:
- 6 edges.
- Every `policy_source` is verbatim in its own rule, absent from the depended-on rule, and `resolved_by` equals the depended-on target tool.
- All edges are state form. The graph is acyclic.

Changes since round 1:
- annual <- recurring: "The redetermined annual rate is fixed only after the countable income on the award matches the recurring income on file." "Matches" equals the equality condition. **G18 closed.**
- annual <- net_worth: the condition now reads "counts every one-time VA payment deposited since pension_awards.opened_date at the cash it brought, with no compensation release left posted at its gross amount". That is the sentence plus the net-worth rule's own posting convention, so it is no longer strengthened beyond the depended-on rule. **G12 closed.**
- The other four sentences are unchanged and pass the four-point test as in revision 1.
- G19 (the root reads the declaration without its own sentence) persists. Observation.

### override_declarations (revision 2)

- statement: `pension_excl_compensation` declared (closed). `pension_evt_income_change` followed.
- care_cost: income-match clause declared. The threshold now follows base. Base `pension_evt_medical_expenses` "replaces the prior figure" against an additive medical figure: G20 persists as an observation.
- retro: `pension_excl_compensation` added to refs, `overwrite: []`. Subtracting compensation paid for pension months rests on "never paid ... for the same month". No conflict.
- **declaration: undeclared override of `pension_excl_compensation` (R2-N1)**, see the conflict scan, item 2.
- recurring: follows base.
- net_worth: follows base apart from the posting convention (R2-O2).
- annual: income-change effective dates now follow base (closed). Threshold follows base.

### factor_ladders (revision 2)

| policy | factors (label) | distinct and real? | surviving |
| --- | --- | --- | --- |
| statement | SS COLA (param), monthly comp (method, comp, multi-source), representative_fee_on_release (param, comp, multi-source: agreement + fee; fee / 20% cap / 0, which is real per 38 CFR 14.636), release share (param, comp) | all distinct and real | **4** (3 parameter / 1 method). Meets |
| care_cost | own income (method), spouse COLA (param), FERS annuity COLA (param; 2.0% FERS COLA for both the 2026 and 2025 CPI, so 1.02 / 1.0404, real), premium confirmation (param; the fall-through "more than two years: nothing until reported again" is real), care monthly (method), care months (param) | all real; the G8 fall-through is gone | **6**. Meets |
| retro | months owed (method), amount_already_paid (method), returned_payment_owed (param), monthly comp (param), retroactive_compensation_fee_taken_out (param, new), lump share (param) | **amount_already_paid and returned_payment_owed are unchanged from round 1. Each is one rule written as two tiers** (issued + earlier release, where tier 2 is tier 1 with release = 0; and what came back, where tier 1 "gross when nothing withheld" = tier 2's "net that came back" on that row) | 4 (3 parameter / 1 method). The count meets the floor, but two declared factors are still unreal ladders. **G7 open for retro** |
| declaration | period (method), fee (param, comp, multi-source), **release_months_before_pension (param, comp)**, deposit recency (method; labelled `cross_difficulty: null` although it reads the comp ledger, observation R2-O4) | **release_months_before_pension is one formula written as three tiers** (new, R2-N2). Tier 1 "every month before the effective date: 1" = (months before / all months) when every month is before; tier 3 "paid only for pension months: 0" = the same ratio with 0 months before. The compute confirms it: `pension_share` equals `months_before_pension / months_paid_for` in all three branches | **3** (1 parameter / 2 method). **Below 4 and below 2 parameter** |
| recurring | SS COLA, spouse COLA, FERS annuity COLA (param), compensation recurrence (method, comp: election 0 / ended otherwise: actually issued / running: rate x12) | real. The interest one-formula ladder (G7) is removed. Counting compensation actually received in the 12-month annualisation period for an award that ended for another reason matches VA's actual-receipt practice | **4**. Meets |
| net_worth | home loan (param, loan), declared one-time (method), income after deduction (param; a clamp, accepted as in revision 1 and now labelled parameter, G17 closed), premium age (param), care monthly (method), care months (param) | real. The release-cash and refunds one-rule ladders and the threshold-household ladder are removed | **6**. Meets |
| annual | one-time (method), income after deduction (param, clamp), premium age (param), care monthly (method), care months (param) | real. G5 and G6 are removed | **5** (3 parameter / 2 method). Meets |

Per task:
- Task 0 keeps a multi-source, cross-difficulty factor (statement and retro fee, monthly comp).
- Task 1 keeps one too (declaration fee: comp award agreement + comp payment fee), plus home loan (loan).
- G8 closed: the threshold-household ladders, the premium no-adjustment straw man and the refund conditions/stamp factor are all gone.

### findings (revision 2)

| id | round-1 item | revision-2 status | evidence |
| --- | --- | --- | --- |
| G1 | undeclared override in the statement | **closed** for the statement; the same base sentence is **newly** overridden undeclared in the declaration (R2-N1) | statement `overwrite[0]`; declaration `overwrite: []` with refs incl. `pension_excl_compensation` |
| G2 | decrease effective date | **closed** | annual rule "When the redetermined rate is lower ... last day of the month" |
| G3 | threshold base | **closed** | `threshold: RND(P('medical_deduction_base_mapr') * ...)` in all three |
| G4 | care-cost vs annual conflict | **closed** | the exclusion sentences in both rules |
| G5 | premium tier overlap | **closed** | "three to eleven" / "twelve to twenty-three" |
| G6 | care-months direction | **closed** | "or ended after it"; "more than that gap before" |
| G7 | one rule written as several tiers | **partly open**: closed for statement, recurring and net_worth (factors replaced or removed); **open** for retro (`amount_already_paid`, `returned_payment_owed` unchanged); **new instance** in the declaration (`release_months_before_pension`, R2-N2) | see the factor table |
| G8 | unreal conditions or outcomes | **closed** | the ladders were removed or rewritten |
| G11 | second writer of a raising adjustment | observation, unchanged; the stale rationale is checked at the reveal | tools unchanged |
| G12 | condition stronger than sentence | **closed** | new condition text |
| G17 | clamp labelled method | **closed** (now `parameter`) | |
| G18 | "brought up to" | **closed** ("matches") | |
| G9, G10, G10b, G13, G14, G15, G16, G19, G20, G21 | observations | unchanged. G21 is moot: refunds are no longer declared. G10 is no longer live. | |
| **R2-N1** | new | **SOURCE-POLICY RED (charter)**: undeclared override of `pension_excl_compensation` in the declaration. Same situation (a release straddling the pension effective date): base counts it all, the declaration counts a share | demonstrated on task 1 only if its release straddles; see `1.md` |
| **R2-N2** | new | **SOURCE-FACTOR RED**: the declaration share ladder is one formula, so the declaration has 3 surviving factors and 1 parameter | bears on task 1 |
| R2-O1 | new obs | statement monthly-comp tiers 2/3 vs its declared replacement; "before pension first paid" vs "before the effective date" | |
| R2-O2 | new obs | the gross-posting convention for net worth is not VA practice and overstates assets by the fee and offset | |
| R2-O3 | new obs (regression) | stale `compute_basis` quotation in recurring | |
| R2-O4 | new obs | `release_deposit_recency` reads comp but is labelled `cross_difficulty: null` | |

### closing_checklist (revision 2)

Written after both round-2 reveals (06:17:26Z). The per-task scored solutions equal my blind derivations exactly, in both tasks. The difficulty **still does not pass**.

| item | status |
| --- | --- |
| every comparison section carries PASS | **no**. Task 0: SOURCE-FACTOR RED (retro unreal ladders, G7). Task 1: SOURCE-FACTOR RED (declaration share ladder, R2-N2). Charter: SOURCE-POLICY RED R2-N1 (undeclared declaration override; no task consequence) |
| scopes disjoint and complete; tools closed | yes (tools unchanged) |
| trees: 1-3 prerequisites, value_input floor met, a customer write, acyclic, every edge bears weight | yes (task 0: 2/2; task 1: 3 prerequisites, 3 value_input edges, state gate now bearing weight) |
| baselines definite and different from gold | yes, all 7 computations (15169.05, 3828, 9156.0, 0.00, 33749.64, 76356.46, 6339) |
| 4-6 real factors (2 parameter, 1 method) per computation; ladders real and distinct | **no** for the declaration (3 / 1 parameter). Retro meets the count but declares 2 unreal ladders |
| multi-source and cross-difficulty per task | yes |
| gates on the final form | per the coordinator's fresh snapshot, all 8 green. Artifacts at close: `pension.extended.yaml` `72f10d2b...a4a0b`, `task_tools.py` `78bedbc3...093202`, `tasks/0.json` `0689bbd3...a409`, `tasks/1.json` `a82ef911...e1d3` |

Open items after round 2:
- G7 (retro `amount_already_paid` and `returned_payment_owed`; task 0)
- R2-N2 (declaration share ladder; task 1)
- R2-N1 (charter override, no task consequence)

Observations: R2-O1 through R2-O5 and the carried-over G9/G10b/G13/G14/G15/G16/G19/G20.

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-06 ~07:1xZ by the same auditor, before any round-3 task JSON was opened. Nothing here is derived from a revealed GT.
- Re-derive rule:
  - `pension.extended.yaml` changed again: round 2 `72f10d2b...a4a0b`, round 3 `bedcf2f7ee61b9f31141fe1dd3f2aaa4a8ee74b57898451feb4db73d5a2746e6`. Every charter-global section is re-derived in full.
  - `task_tools.py` is unchanged (`78bedbc3...093202`), so the tool-module conclusions carry forward from revisions 1 and 2.
  - Base copy lines 1-1002 are still identical to `blueprint/products/pension.yaml`.
- Entry: the fresh `GATES.txt` lists all 8 green, with traceability deferred. The views match MANIFEST (`task_0.view.json` `36bda754...b845`, `task_1.view.json` `ffe228bc...c0fa`).
- The reworker's claims were used as item ids only.

### re-derivation (revision 3)

- **Mechanical sweep.** Every `compute_basis` quotation is verbatim in its rule, every baseline sentence is in its rule, and every compute binding has a basis.
  - All 6 `policy_source` sentences are verbatim in their own rule, absent from the depended-on rule, and `resolved_by` equals the target tool.
  - The graph is acyclic and every edge is state form.
  - **R2-O3 closed**: the recurring `ss_figure` basis now quotes "each Social Security figure, the annuity figure and the interest figure are taken as reported ...", which is in the rule.
- **Override declarations.** `pension_ext_one_time_payment_declaration.overwrite` now names `pension_excl_compensation` with the same replacement the statement declares, and its rule carries that replacement sentence verbatim. **R2-N1 closed.** The other policies are unchanged against base (revision 2 § override_declarations).
- **Policy conflict scan.** No new overlap.
  - The care-cost / annual-rate exclusion sentences remain (G4 stays closed).
  - The annual-rate effective-date branches remain (G2 stays closed).
  - The threshold is the category base everywhere (G3 stays closed).
  - The statement now includes "his federal civil service annuity" in the benefit income, and the care-cost "benefit income on the award" is the countable income less the spouse figure, so it includes the annuity. The two policies define the same quantity, and the annuity is counted once.
- **R2-O1 (claimed no change needed).** The statement's monthly-compensation tiers 2/3 still sit beside the declared "not counted for months pension also paid" replacement. Both share computations (statement and declaration) now measure "months before pension was first paid" as months before the effective date plus the payment lag. Observation retained; no consistent world exhibits it.
- **R2-O2 (claimed no change needed).** The gross-posting convention for net worth is unchanged. Observation retained (realism: VA's net worth is a determination, not a ledger that posts the gross release).

### factor_ladders (revision 3)

| policy | factors (label) | ladder check | surviving |
| --- | --- | --- | --- |
| statement | SS COLA (param), monthly comp (method, comp, multi-source), representative fee (param, comp, multi-source), release share (param, comp), **FERS annuity COLA (param, new here)**, **release deposit recency (method, comp, new)**: fresh / remaining months of its twelve-month year / none after one year | all distinct and real. Treating lump-sum income as counting for the 12 months after receipt is real VA practice | 6 (4 parameter / 2 method). Meets |
| care_cost | own income (method), spouse COLA (param), **income after deduction (param, clamp; moved here from the statement-annuity slot)**, premium confirmation (param), care monthly (method), care months (param) | the clamp is accepted as in the net worth and annual policies | 6 (4 / 2). Meets |
| retro | months owed (method), monthly comp (param, comp), fee taken out (param, comp), lump share (param, comp) | **`amount_already_paid` and `returned_payment_owed` are removed**. Their rule sentences are now single fixed statements: "What was already paid is the monthly payments issued in the months owed plus any earlier retroactive release issued in those months"; "the amount that came back from it is added". **G7 closed** | 4 (3 / 1). Meets |
| declaration | period (method), fee (param, comp), **release share (param, comp, rewritten)**, deposit recency (method, now `cross_difficulty: comp`, **R2-O4 closed**) | Share tiers: 1 when every month precedes the effective date; (months before the effective date + payment lag) / all months when the release straddles; 0 otherwise. The middle formula gives a value above 1 on tier 1's situation and a non-zero value when the first month is the effective month, so the three tiers are no longer one formula. **R2-N2 closed** | 4 (2 / 2). Meets |
| recurring | SS, spouse, FERS annuity (param), comp recurrence (method) | unchanged since revision 2 | 4. Meets |
| net_worth | unchanged since revision 2 | | 6. Meets |
| annual | unchanged since revision 2 | | 5. Meets |

Per task, a multi-source, cross-difficulty factor exists in each: task 0 has fee and monthly comp; task 1 has the declaration fee.

### findings (revision 3)

| id | claim | verified status |
| --- | --- | --- |
| G7 (retro ladders) | closed | **closed**: the factors are removed and the rule sentences are fixed |
| R2-N2 | closed | **closed**: the share tiers are distinct |
| R2-N1 | closed | **closed**: declared in the declaration's own `overwrite` |
| R2-O3 | closed | **closed** |
| R2-O4 | closed | **closed** |
| R2-O5 | closed | **closed** in the worlds: the personas now say Delmar started at the post office in 1986 and Wendell in 1987, after FERS took effect for new hires in 1984, so the FERS reduced COLA is correct |
| R2-O1 | no change needed | observation retained |
| R2-O2 | no change needed | observation retained |
| new defects | — | none found at charter level |

### closing_checklist (revision 3)

Written after the round-3 reveals (07:07:23Z).
- Every round-2 RED that was claimed closed is verified closed: G7 (retro), R2-N2, R2-N1, R2-O3, R2-O4 and R2-O5.
- R2-O1 and R2-O2 remain observations.
- No new charter-level defect was found.
- Every scored value and date in both tasks equals my blind derivation.

The difficulty **still does not pass**, because of a per-task GT defect the gates do not detect:
- **R3-T0 (task 0, regression in round 3).** The retro release's `adjustment_id` in GT is the round-2 adjustment id (`pra_8bba5a21fa44`, made for rate 21259). The round-3 gold adjustment returns `pra_4d5d048804d7`.
- **R3-T1 (task 1, present since round 2 and missed in my revision-2 comparison).** The root's `source_report_id` in GT is the round-1 declaration id (`pod_8bce7d26e70f`, made for 12201.32). The gold declaration of 8216.60 returns `pod_70884785f32d`.
- In both tasks the GT DB hash differs from the hash of the correct trajectory: task 0 `8d787b34` vs `fc5d03e6`; task 1 `abb6ddb0` vs `d0a8fd50`. Each is **SOURCE-TASK RED**.

| checklist item | status |
| --- | --- |
| every comparison PASS | **no** (SOURCE-TASK RED in both tasks) |
| policy self-consistency, trees, factor floors, baselines, multi-source and cross-difficulty | pass in both tasks |
| tools and scopes | unchanged, closed |
| gates on the final form | all green per the coordinator's snapshot, but they do not check that a reference id copied into a later step equals the id the earlier gold write returns. Artifacts at close: `pension.extended.yaml` `bedcf2f7...46e6`, `task_tools.py` `78bedbc3...093202`, `tasks/0.json` `1cadf698...e757`, `tasks/1.json` `37f59808...cae5` |

Open items:
- R3-T0
- R3-T1

Observations: R2-O1, R2-O2, and the carried-over G9/G10b/G13/G14/G15/G16/G19/G20.

## revision_4

### charter_global_frozen (revision 4) — carried forward

- Written 2026-10-06 ~07:25Z, before any round-4 task JSON was opened.
- Re-derive rule: `pension.extended.yaml` (`bedcf2f7...46e6`) and `task_tools.py` (`78bedbc3...093202`) are byte-identical to round 3, re-hashed in place. Every charter-global section of revision 3 is therefore carried forward by reference. These two hashes are the grounds for not re-deriving.
- The fresh `GATES.txt` lists all 8 green, with traceability deferred.
- The masked views are also unchanged since round 3 (`task_0.view.json` `36bda754...b845`, `task_1.view.json` `ffe228bc...c0fa`). The reworker's claims were taken as item ids only.

### closing_checklist (revision 4)

Written after the round-4 reveals (07:24:49Z).

| checklist item | status |
| --- | --- |
| per-task files 1:1 with tasks, plus `_difficulty.md`; revisions 1-4 appended, older text untouched | done |
| every comparison PASS | **yes** (task 0 and task 1, revision 4) |
| extended policies fully covered; scopes disjoint (task 0: statement / care_cost / retro; task 1: declaration / recurring / net_worth / annual); tools closed; uuid8s independent (G14 prefix collision is an observation only) | yes |
| trees: 1-3 prerequisites, value_input floor met, a customer write, every edge bearing weight, acyclic, and the difficulty's graph a DAG | yes (task 0: 2 prerequisites / 2 value_input / user statement; task 1: 3 / 3 / user declaration; the state gate bears weight) |
| baselines self-sufficient, definite and different from gold | yes, in all 7 computations |
| 4-6 real factors (at least 2 parameter, 1 method), real and distinct ladders, multi-source and cross-difficulty per task | yes (statement 6, care cost 6, retro 4, declaration 4, recurring 4, net worth 6, annual 5) |
| GT reproducible by a correct trajectory | yes: GT replay hashes equal the hashes of an independently run correct trajectory (task 0 `fc5d03e6`, task 1 `d0a8fd50`) |
| gates on the final form | all 8 green per the coordinator's round-4 snapshot. Artifacts at close: `pension.extended.yaml` `bedcf2f7...46e6`, `task_tools.py` `78bedbc3...093202`, `tasks/0.json` `f6ccdc9c...c857`, `tasks/1.json` `0cf62bc0...0696` |

**The difficulty passes the source-layer audit** (policy self-consistency, problem tree, factor weight and unique solution all PASS for both tasks). Remaining items are observations only, not grounds for rework:
- R2-O1: the statement's monthly-compensation tiers 2/3 sit beside the declared replacement.
- R2-O2: the gross-posting convention for net worth, which is not VA practice. Task 1's state-gate weight rests on it.
- Carried-over observations: G9, G10b, G13, G14, G15, G16, G19, G20.

`check_traceability` is still deferred to the KB step.

## revision_5

### charter_global_frozen (revision 5)

- Written 2026-10-06 ~10:1xZ, before any round-5 task JSON was opened, and **before reading the render-layer audits** under `audits/policy_kb/` and `audits/runtime_context/`. Those audits were read only after this freeze; see the comparison sections.
- Re-derive rule:
  - `pension.extended.yaml` changed: round 4 `bedcf2f7...46e6`, round 5 `196e4c8b6bddb3d57f435b7e1d76e31f7821c1d056d2a7dbd61df9c459e6f033`. All charter-global checks are re-derived.
  - `task_tools.py` is unchanged (`78bedbc3...093202`).
  - The masked views are unchanged (`36bda754...b845`, `ffe228bc...c0fa`).
  - Base lines 1-1002 are still identical to `blueprint/products/pension.yaml`.
- `GATES.txt` lists 9/9 green, including TRACEABILITY OK.

**Self-correction (an omission in revisions 1-4).** In every earlier round the statement rule dated the statement "on the date the compensation award closed" while its ages read "before the statement", yet the compute aged everything to NOW (the filing day). This is a rule/compute equivalence failure that my check 2 should have caught and did not. On task 0's world it moved the release-recency weight (the release-age tiers) and therefore all three scored values. I record the miss here; the older revision texts are left as written.

### re-derivation (revision 5)

- **Mechanical sweep.** Every `compute_basis` quotation is verbatim in its rule, every baseline sentence is in its rule, and every binding has a basis.
  - All 6 `policy_source` sentences are verbatim in their own rule and absent from the depended-on rule, and `resolved_by` equals the target tool.
  - The graph is acyclic and every edge is state form.
- **Statement time anchor (N1).**
  - New rule sentence: "Every age the statement measures is measured to the date it carries, the day the change began, and not to the day the veteran files it."
  - The compute now has `statement_date = CFIELD('comp','closed_date') or XLATEST(comp payment_date)`, with `ss_level_age`, `annuity_level_age`, `release_age` and `release_weight` all measured to `statement_date`.
  - Rule and compute are now equivalent on every age. **N1 closed.**
  - Residual observation (R5-O1): the monthly-compensation window "issued since the pension effective date" is a period, not an age, and the compute closes it at NOW (`within_months=MONTHS(effective_date, NOW)`). The rule's new sentence speaks only of ages, so the window's end is not fixed by any sentence. The scored value is unaffected (the election tier gives 0 regardless of count). Only the monthly-compensation factor's baseline value depends on the window's end.
- **Declaration anchor (M2).** "Every age and period the declaration measures is measured to the day the veteran files it, not to the date it carries." The compute measures to NOW. Equivalent. **M2 closed.**
- **Premium wording (M1).** The net-worth and annual rules now say "medical expense reports received three to eleven whole months before the redetermination count as premiums at their total; when none was received in that span and some were received twelve to twenty-three whole months before, ... Part B ...". That equals the compute (`recent_count > 0`; otherwise `lapsed_count > 0`). This also retires my earlier concern that a "premium report" was not identifiable from the records. **M1 closed.**
- **Triggers (N3/M3).**
  - Statement: "When monthly VA disability compensation paid to a pensioner for months his pension was also paid stops or changes". Task 1's only monthly compensation (October 2025) precedes the pension's first paid month, so it does not fire there.
  - Declaration, recurring and net worth fire on "a retroactive compensation release ... after his compensation award has ended". Task 0's release (2026-02-17) preceded the award's closing (2026-05-31), so they do not fire there.
  - Care cost excludes itself under a redetermination request. The annual rate is on request only. The retro release needs a raising adjustment.
  - Each world now triggers only its own tree. **N3/M3 closed.**
- Override declarations, conflict scan, factor ladders and counts are unchanged from revision 3/4 apart from the anchors above: statement 6, care cost 6, retro 4, declaration 4, recurring 4, net worth 6, annual 5, all real and distinct. No new defect.

### closing_checklist (revision 5)

Written after the reveals (10:05:45Z) and after reading the render-layer audits.

| item | status |
| --- | --- |
| every comparison PASS | yes (tasks 0 and 1, revision 5) |
| claimed closed: N1, M1, M2, N3/M3 | verified **closed** (see above and the task files) |
| claimed no change: N2 | confirmed. Observation only (= G9); no world contains both user-tool rows |
| no regression | none. Task 1's scored solution and hash are unchanged from round 4. Task 0's values moved exactly as the new anchor entails, and its reference id was refreshed (GT hash equals the hash of the correct trajectory) |
| trees, factor floors, baselines, multi-source and cross-difficulty, scopes, tools | as in revision 4. All hold on the round-5 charter |
| gates on the final form | 9/9 green per the coordinator's snapshot (including TRACEABILITY OK). Artifacts at close: `pension.extended.yaml` `196e4c8b...f033`, `task_tools.py` `78bedbc3...093202`, `tasks/0.json` `34060cc2...cea4`, `tasks/1.json` `3d806b04...870c` |

**The difficulty passes the source-layer audit.** Open items: none.

Observations:
- R2-O1: the statement's monthly-compensation tiers 2/3 against its declared replacement.
- R2-O2: the gross-posting convention for net worth.
- R5-O1: the monthly-compensation window in the statement closes at the filing day.
- N2 = G9: both user tools write `income_source='other'`.
- G10b, G13, G14, G15, G16, G19, G20.
