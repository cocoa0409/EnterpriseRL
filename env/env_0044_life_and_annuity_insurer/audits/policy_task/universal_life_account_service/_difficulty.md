# Policy-task audit — universal_life_account_service / charter-global

## charter_global_frozen

- Freeze time: 2026-10-08T07:40Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: claude-opus-5-5, running erl-task-policy-audit as an independent auditor. It did not write the artifacts under audit.
- Inputs, with their hashes as handed over and re-checked with `sha256sum`:
  - `env/env_0044_life_and_annuity_insurer/tasks/universal_life_account_service/ul.extended.yaml`: 326133b095aeea96807845cad8a8dfa1e2587f4c9c685184457cf53aae8391fa
  - `.../task_tools.py`: bfc05761a9ec75c5d2c5cefd8dde8e7df058a823ba598870260e1e5a2ed9709a
  - Masked views: `/tmp/erl0044_views/universal_life_account_service/task_0.masked.json` 831cf66d…762e and `task_1.masked.json` ae371619…ab4e02. Each holds only frozen_time, user_scenario and initial_state.
  - `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml) and `erlbench/`. The DSL semantics were taken from `skills/erl-task-instantiate/scripts/check_compute.py`, which defines build_env, MONTHS, DAYS, SUM, LATEST, CFIELD, XCOUNT and RND (= Python `round`).
- Fields allowed: everything listed above.
- Fields masked and unread at freeze time: `tasks/0.json` and `tasks/1.json` in full (evaluation_criteria, computations, db_closure, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), plus the difficulty worklog.
- Entry conditions (Step 0): the brief supplies the gate snapshot. EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK. CACHE-DIFF is INFO only. check_traceability is deferred to the render stage. Both masked views came with hashes, and both matched on re-check. No input was missing.
- Base copy: lines 1–1386 of `ul.extended.yaml` are byte-identical to `blueprint/products/ul.yaml`. `diff` shows only the appended blank line and the `# ---- extended policies …` comment.

### policy_conflict_scan

There are six extended policies. All target tools are in `task_tools.py`.

| id | target_tool (owner) | computes | base refs | prerequisite |
| --- | --- | --- | --- | --- |
| ul_ext_loan_interest_settlement | settle_loan_interest_b95e2dd6 (agent) | interest_amount | ul_evt_policy_loan | [] |
| ul_ext_overloan_charge | assess_overloan_charge_72382565 (agent) | overloan_charge | ul_overloan_protection | ← settlement (state_gate, state form) |
| ul_ext_overloan_protected_face | exercise_overloan_protection_1091dc6b (user) | protected_face_amount | ul_overloan_protection | ← overloan_charge (value_input, state form) |
| ul_ext_surrender_charge_assessment | assess_surrender_charge_840d0421 (agent) | surrender_charge | ul_surrender, ul_face_and_option_changes | [] |
| ul_ext_guideline_excess_refund | refund_guideline_excess_434d2811 (agent) | refund_amount | ul_evt_premium_acceptance | [] |
| ul_ext_surrender_payout | surrender_policy_65d610d4 (user) | net_paid_amount | ul_surrender | ← surrender charge (value_input), ← guideline refund (value_input) |

Overlapping subjects:

- **ul_ext_overloan_charge and ul_ext_overloan_protected_face** both refine `ul_overloan_protection`. They replace different base clauses: the charge clause, and the face clause. The face policy subtracts the *booked* charge (`opr_charge_booked`) and never re-derives it, so the two policies cannot disagree.
- **ul_ext_surrender_charge_assessment and ul_ext_surrender_payout** both refine `ul_surrender`. The payout reads the *booked* full-surrender charge (`po_charge_booked`) and does not recompute it.
- **ul_ext_loan_interest_settlement and ul_ext_surrender_payout** both price loan interest. The settlement rule uses an interim charged rate of 0.045 from policy year 6; the payout uses `surrender_interim_loan_rate` 0.045 from `surrender_interim_loan_year` 6. The values agree, so there is no conflict. The undeclared-override aspect is covered under override_declarations, observation O-3.

Other checks:

- **Triggers and time anchors** are consistent: NOW for the settlement and the overloan pair; the surrender request's received_date for the effective date in the charge, the refund end-date and the payout.
- **Terminal states** are consistent with base. Exercise sets overloan_protected and option A, as base `ul_overloan_protection` says. Surrender sets status surrendered with termination_date = the effective date, as base `ul_policy_surrendered` says.
- **Cross-category reads** are all of other categories' holdings and ledgers: fixed in the charge; ltc in the face, the surrender charge and the payout; term in the surrender charge and the payout; whole in the payout. All read-only.
- **Claim scope:** every event the tools write (ul_loan_repaid, ul_overloan_protection_charged, ul_overloan_protection_exercised, ul_surrender_charge_assessed, ul_premium_refunded, ul_policy_surrendered/ul_surrender_value_paid) is in this difficulty's `claim.event_types` in blueprint.yaml.
- **Scope of the M=2 tasks**, inferred pre-reveal from the prerequisite graph: two disjoint trees, {settlement → charge → face} and {surrender charge, guideline refund → payout}. Together they cover all six extended policies, so they are jointly complete. This is compared with charter_scope after the reveal, in the task files.

### rule_compute_equivalence

Method: a script confirmed that every `compute_basis` quotation is a verbatim substring of its policy's `rule`. All are. Then every binding was swept against its rule sentence.

- **ul_ext_loan_interest_settlement.** The balance, gain, balance_rate, advance_rate, three-way accrual, discount ladder and single final rounding are all faithful, with one exception: `months_to_anniversary: "12 - MONTHS(F('issue_date'), NOW) % 12"`. The rule says *"the whole months left until the next policy anniversary"*. Away from a monthly anniversary day, the compute returns whole months **elapsed** subtracted from 12, which is one more than the whole months left: it counts the running partial month as a whole month left. **Finding F-1.**
- **ul_ext_overloan_charge.** Faithful. Rate band, attained age, carry tiers (fixed interest on AV above the loan, plus collateral at the loan-type credited rate), payment count, ledger loan ratio, active fixed contract value, single rounding.
- **ul_ext_overloan_protected_face.** Faithful except `deduction_reserve`, tier 2: `F('current_monthly_deduction') * (12 - MONTHS(F('issue_date'), NOW) % 12)`. The rule says *"a reserve of the current monthly deduction for each whole month left until the next policy anniversary"*. This is the same idiom as F-1, and here it enters the scored amount. **Finding F-1** (the consequence is demonstrated in task 0).
- **ul_ext_surrender_charge_assessment.** Faithful. The tier ladders transcribed into `sc_rate_*` match `surrender_charge_ladder` for all six tiers, checked value by value. Monthly and quarterly grading toward the next year's rate (0 after the schedule), issue age from date of birth, funding test, term years via `CFIELD('term','issue_date', status='converted')`, care waiver.
- **ul_ext_guideline_excess_refund.** Faithful except `excess_earnings`. The rule says *"the rate is compounded monthly over the whole months in that period and the remaining days earn simple interest over 365 on the compounded amount"*. The compute uses `earnings_days // 30` and `earnings_days % 30`, which are 30-day months. "Thirty-day months" appears only in `factors[earnings_compounding].ladder[0].method`. It is not in the rule. A calendar-month reading of "whole months in that period" gives a different remainder whenever the period spans a 31-day month or February. **Finding F-2** (the consequence is demonstrated in task 1). Every other binding, including the end-date ladder and the start offsets, is faithful.
- **ul_ext_surrender_payout.** Faithful. Released value, unearned deduction (whole deduction for 1–15 days, COI part only for 16–29), fee, booked charge, refund booked on or after the latest monthly anniversary, loan interest, cost-basis source, taxable amount, withholding election, delay interest.
- **Ladders against the rule.** Every tier named in `factors[].ladder` of all six policies is a sentence of the rule and a branch of its `decides` binding, and vice versa. The single exception is the "thirty-day" wording of F-2.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy, as the table above shows.
- **Owners:** two writes are owner=user (exercise and surrender) and four are owner=agent.
- **Tool bodies** (`task_tools.py`, lines 11–210) contain no `if`, `raise` or validation. Each performs one create or update and returns a receipt. No tool judges eligibility, prerequisites or amounts.
- **Docstrings:** none names another tool or uses before, after or first to place itself in a sequence. "Afterwards" appears at lines 17 and 81, but it describes the call's own effect. Observation O-6: `assess_overloan_charge_72382565` says *"the entry is what the policy's account value is reduced by when the rider is carried out"*. This mentions the exercise action as the moment of reduction. It is not an ordering connective, and it is consistent with the declared edge.
- **uuid8s:** b95e2dd6, 72382565, 1091dc6b, 840d0421, 434d2811 and 65d610d4. All six are distinct, share no prefix or suffix, and show no sequential pattern. There is no sign of batch derivation.

### prerequisite_graph

- `prerequisite` is filled on all six policies: `[]` on settlement, surrender-charge and guideline-refund.
- Edges: charge → settlement, face → charge, payout → surrender charge, payout → guideline refund. Every `problem` is an extended policy id in this file, never a base id and never the policy itself. The graph is acyclic: two trees of depth 2 and depth 1.
- `policy_source` is verbatim in the blocked policy's own rule for all four edges (script check).
- `form: state` on all four edges, and there is no `fallback_reason`, which is correct for state form.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- `kind`:
  - The face edge has gate `opr_charge_booked`, the payout's charge edge has `po_charge_booked`, and the payout's refund edge has `po_refund_since`. All three are value_input, and each gate is a real compute binding of the blocked policy.
  - The charge edge has `gate: ul_holdings.loan_interest_paid_to_date`. It is a state_gate whose gate is the record field the sentence names. The extended policy has no `eligibility` list, so the gate is a field rather than an eligibility id. Observation O-5.
- **Conditions:** each matches its sentence's strength. The face and payout conditions name the booked ledger entry; the refund condition restates the limit test.
- **Finding F-3:** the charge edge's `condition` reads *"ul_holdings.loan_interest_paid_to_date equals the charge date (the frozen date), so no loan interest accrues …"*. "(the frozen date)" is authoring-viewpoint wording, written into the general text of the policy.

### prerequisite_sentences

The four-point test, edge by edge:

1. **charge ← settlement.** *"The overloan protection charge is figured only after the policy's loan interest paid-to date stands at the date the charge is figured, so that no loan interest is left accruing from an earlier date."*
   - Connective: "only after".
   - Waited-on state: "the loan interest paid-to date stands at the date the charge is figured". This is `ul_holdings.loan_interest_paid_to_date`, a record-visible state with no action, performer or tool.
   - No tool name, policy id or snake_case token.
   - Strength equals the condition.
   - Only one write in this difficulty changes that field: `settle_loan_interest_b95e2dd6`, line 38. The shared module has no writes besides identity verification and handoff.
   - Derivation: the settlement rule says *"a cash settlement moves the loan interest paid-to date to the settlement date without reducing loan principal"*. That points to a single resolving action.
2. **face ← charge.** *"The protected face is not fixed until the overloan protection charge stands deducted in the policy's activity history."*
   - Connective: "not until".
   - State: an overloan protection charge entry in ul_transactions.
   - Only one write creates that event: `assess_overloan_charge_72382565`.
   - The charge rule describes booking that entry. Single reading.
3. **payout ← surrender charge.** *"The surrender value is paid only after the full-surrender charge for the surrender request stands booked in the policy's activity history."*
   - Connective: "only after".
   - State: a ul_surrender_charge_assessed entry with charge_reason full_surrender.
   - One write: `assess_surrender_charge_840d0421`. Single reading.
4. **payout ← guideline refund.** *"The surrender value is not settled until the gross premiums received, less the premiums refunded and the partial withdrawals, stand at or below the guideline premium limit in the policy's activity history."*
   - Connective: "not until".
   - State: a ledger quantity compared with the limit.
   - The only write in this difficulty that lowers that quantity is `refund_guideline_excess_434d2811`, which adds a ul_premium_refunded entry. No withdrawal tool exists here. The guideline-refund rule names that quantity and the limit, so the resolution is unique.

Further checks:

- No blocked rule carries a second wording, a tool name or another problem's id for its dependency.
- No depended-on rule restates the blocked sentence.
- No base rule sentence grounds any edge.
- Observation O-4, on the depended-on side: two rules use "when …" to describe the occasion of their own write:
  - The charge rule: *"When an approved overloan protection election is carried out, a one-time overloan protection charge is deducted …"*.
  - The surrender-charge rule: *"When a signed full surrender is processed, the surrender charge is booked …"*.

  These name the dependent action as the occasion but carry no before/after. In each pair the blocked rule's sentence ("not fixed until …", "paid only after …") fixes one order, so no second order arises. If a reader inverted the overloan pair (exercise first), the face would be figured with nothing booked. That world is shown in task 0.

### override_declarations

Checked base sentence by base sentence for every `base_policy_refs` entry.

**ul_ext_loan_interest_settlement → ul_evt_policy_loan**
- "Loans are standard loans … preferred_loan_charged_rate …": replaced, and declared in overwrite[0].
- "Interest accrues simple … capitalized.": replaced (discount), and declared in overwrite[1].
- "Repayments are applied first to accrued interest … at least min_loan_repayment": followed. The interest-only settlement is far above $50.
- Status and signed-request sentences (loan advance only): not touched.
- The base formula `accrued_loan_interest` (holding loan_balance × standard rate × days) is the quantity the overwrites replace.
- Observation O-1: overwrite[0].replaced_by restates only the balance-rate sentence. The advance-rate sentence (blended rate) is not in replaced_by. The superseded clause is still named, so the override is declared.

**ul_ext_overloan_charge → ul_overloan_protection**
- "On exercise overloan_charge_pct of the account value is deducted": replaced and declared.
- Eligibility (attained age ≥ overloan_min_attained_age, policy year ≥ overloan_min_policy_year, indebtedness ≥ threshold, not a MEC) and signed approved election: inherited.

**ul_ext_overloan_protected_face → ul_overloan_protection**
- The face sentence: replaced and declared.
- "death benefit option becomes Option A" and "monthly deductions stop": inherited (the tool sets A).
- Corridor factors `corridor_factor_*` equal the tier `corridor_factor_ladder` from age 75 up.

**ul_ext_surrender_charge_assessment → ul_surrender, ul_face_and_option_changes**
- The full-surrender charge sentence: replaced and declared.
- Effective-date sentence: followed.
- `ul_face_and_option_changes` (face-decrease charge): not touched. The policy prices only full surrender, so `overwrite` correctly carries no entry for it.

**ul_ext_guideline_excess_refund → ul_evt_premium_acceptance**
- The guideline-excess sentence: replaced and declared. replaced_by drops "within 60 days of receipt" and "unless it is needed to keep the policy in force"; the extended rule deliberately covers refunds made more than 60 days after receipt (compliance-day end date).
- Excess definition = `ul_msr_cumulative_premiums` against the greater of the GSP and the GLP times policy years begun. Equivalent to base.
- The conversion credit counts as premium, as base says.

**ul_ext_surrender_payout → ul_surrender**
- CSV and taxable sentences: replaced and declared.
- Signature sentence (owner + irrevocable beneficiaries + assignee) and effective-date sentence: inherited and followed.
- Observation O-3: the payout's loan-interest sentence uses a surrender interim loan rate (0.045 from year 6). That departs from base `ul_evt_policy_loan`'s rate sentence, which is not in this policy's `base_policy_refs`/`overwrite`. The same base sentence is declared replaced by ul_ext_loan_interest_settlement with the same figures, so the two extended statements agree. Both tasks seed a world where no conflict arises: task 1's loan balance is 0.

**Disguised forms**
- Anonymous intermediate: none found outside declared clauses.
- 0/1 multiplier: none.
- Dropped base branch: none. Base "zero after surrender_charge_years" is kept as the trailing 0 of each ladder.

**Result:** no undeclared override that changes a scored quantity.

### factor_ladders

Structure only. Whether each factor bears weight is decided per task.

| policy | factor | label | ladder (tiers) | multi-source? | cross_difficulty | structural notes |
| --- | --- | --- | --- | --- | --- | --- |
| settlement | settlement_balance_rate | parameter | 3: py≥preferred → preferred rate; interim≤py<preferred → 0.045; else standard | no | — | ok |
| settlement | settlement_advance_rate | parameter | 3: py≥preferred ∧ advance≤gain → preferred; py≥preferred ∧ advance>gain → blended 0.04; else standard | yes (policy year × ledger advance × AV−cost basis) | — | ok structurally. Stamp issue is per task. |
| settlement | settlement_accrual_days | method | 3: advance after paid-to (split accrual) / repayment after paid-to / whole balance | yes | — | ok |
| settlement | early_settlement_discount | parameter | 3: ≥6 months → 0.02; ≥3 → 0.01; else 0 | no | — | the months count is F-1 |
| overloan charge | overloan_charge_rate_band | parameter | 3: py≥25 ∧ age≥85 → 0.025; py≥20 ∧ age≥min age (75) ∧ ¬long → 0.03; else tier pct | yes as written | — | **F-4**: the mid tier's condition "age ≥ the rider's minimum attained age" holds for every customer who reaches this write (base eligibility). |
| overloan charge | charge_value_carry | method | 3: ≥15 days full carry / 1–14 days fixed only / 0 days as shown | no | — | ok |
| overloan charge | charge_persistency_share | parameter | 3: ≥15 payments 0.90; ≥10 → 0.95; else 1 | no | — | ok |
| overloan charge | charge_indebtedness_surcharge | parameter | 3: ≥0.99 → 0.10; ≥0.97 → 0.05; else 0 | no | — | ok. The fall-through band 0.94–0.97 is reachable. |
| overloan charge | charge_household_share | parameter | 3: active fixed ≥ 50,000 → 0.90; active fixed < 50,000 → 0.95; none → 1 | yes (status ∧ value) | fixed | observation O-7 (cross-product discount on a rider charge) |
| protected face | protected_deduction_reserve | method | 3: age≥85 → 6×deduction; age<85 ∧ py<25 → deduction × whole months left; else 0 | no (tier 1 single) | — | the months count is F-1. Label borderline (O-8). |
| protected face | protected_duration_enhancement | parameter | 3: py≥30 → 1.03; py≥20 → 1.015; else 1 | no | — | ok |
| protected face | protected_loan_margin | parameter | 3: ledger loan/AV ≥0.98 → 1.02; ≥ overloan threshold (0.94) → 1.01; else 1 | no | — | **F-5**: "≥ the threshold" holds for every customer who reaches this write, and the fall-through/baseline (1) can never be reached. |
| protected face | protected_care_margin | parameter | 3: LTC claim_active ∧ ≥3 benefit payments in 6m → 1.02; claim_active ∧ 1–2 → 1.01; else 1 | yes (ltc status ∧ ltc ledger) | ltc | **F-6**: the tier outcomes raise the guaranteed paid-up death benefit *because* the insured is on an active long-term-care claim. That is a treatment no life insurer publishes. |
| surrender charge | schedule_rate_grading | method | 3: py≥6 monthly grading; 2–5 quarterly; py1 unchanged | no | — | ok |
| surrender charge | issue_age_share_band | parameter | 3: ≥65 → 0.80; 55–64 → 0.90; else 1 | no | — | ok |
| surrender charge | surrender_funding_credit | parameter | 3: ≥1.5×target×py → 0.10; ≥target×py → 0.05; else 0 | no | — | ok |
| surrender charge | term_conversion_credit | parameter | 3: converted ∧ ≥5y → 0.50; converted ∧ 1–4y → 0.25; else 0 | yes | term | ok |
| surrender charge | surrender_care_waiver | parameter | 3: claim_active ∧ ≥3 payments → 0.60; claim_active ∧ 1–2 → 0.30; else 0 | yes | ltc | ok. Waivers for chronic illness or confinement are real industry practice. |
| guideline refund | excess_earnings_rate | parameter | 3: allocation 0 ∧ ≥30 days → current fixed; allocation>0 ∧ ≥30 days → guaranteed min; else 0 | yes | — | ok |
| guideline refund | late_refund_addition | parameter | 3: ≥60 days → 0.02; 45–59 → 0.01; else 0 | no | — | ok |
| guideline refund | earnings_start_date | method | 3: check +5 days; card/online +1; else receipt | no | — | label borderline: the tiers substitute an offset (O-8) |
| guideline refund | earnings_end_date | method | 3: approved surrender on file → its received date; none ∧ >60 days → compliance day; else refund date | no | — | ok |
| guideline refund | earnings_compounding | method | 3: ≥45 days monthly compounding + simple remainder; 1–44 simple; day 0 nothing | no | — | **F-7**: the declared `baseline` (simple interest) is ladder tier 2. It is neither the fall-through ("no earnings") nor what `baseline.rule` states ("with no earnings added"). Also F-2 (30-day months only in the ladder). |
| payout | persistency_interest_bonus | parameter | 3: py≥10 → 0.005; 5–9 → 0.0025; else 0 | no | — | ok |
| payout | released_value_carry | method | 3: ≥15 days current+bonus and collateral; 1–14 guaranteed min; 0 as shown | no | — | ok |
| payout | unearned_deduction_refund | method | 3: 1–15 days whole deduction; 16–29 COI part only; else 0 | no | — | ok |
| payout | surrender_processing_fee | parameter | 3: py≤5 → 75; ≤SC years → 50; else 0 | no | — | ok |
| payout | surrender_cost_basis_source | method | 3: converted term ∧ conversion credit → less credits; no term ∧ exchange ∧ surrendered whole → swap basis; else gross | yes | term (also reads whole) | ok |
| payout | delayed_payment_interest | parameter | 3: ≥30 days → 0.06; 7–29 → 0.03; else 0 | no | — | ok |

Counts as declared:

| policy | factors | parameter | method |
| --- | --- | --- | --- |
| settlement | 4 | 3 | 1 |
| charge | 5 | 4 | 1 |
| face | 4 | 3 | 1 |
| surrender charge | 5 | 4 | 1 |
| refund | 5 | 2 | 3 |
| payout | 6 | 3 | 3 |

- Cross-difficulty factors: fixed (charge), ltc (face, surrender charge), term (surrender charge, payout).
- Structural checks:
  - Every ladder has three pairwise-disjoint tiers, and every ladder is stated in full in its rule.
  - No two tiers of any ladder select the same value or method.
  - Every `baseline` block's sentence is in the rule.
  - Each fall-through equals the factor `baseline`, except F-7.
  - `decides` is never `result`.
- Counts after striking the defective factors, which bears on task 0:
  - Protected face: F-5 and F-6 leave 2 surviving factors. Even if F-6 is set aside, F-5 alone leaves 3. Either way the count is below the floor of 4.
  - Overloan charge: striking F-4 leaves 4 (3 parameter, 1 method), which still meets the floor.
  - The settlement count also depends on task 0's world (stamp issue). See the task 0 file.

### findings

- **F-1, SOURCE-POLICY RED (rule ≠ compute).**
  - Symptom: `months_to_anniversary` (settlement) and tier 2 of `deduction_reserve` (protected face) both compute `12 - MONTHS(issue_date, NOW) % 12`.
  - Root cause: the rules say "whole months left until the next policy anniversary". On any day that is not a monthly anniversary, the compute returns whole months left + 1.
  - Evidence: rule sentences at `ul.extended.yaml` lines 1421 and 1741; compute at lines 1435 and 1767.
  - Demonstrated consequence (charter): on a date 5 months and some days before the anniversary, the rule gives 5 months (partial discount 0.01) and the compute gives 6 (full discount 0.02).
  - Bears on task 0: the discount tier there is unaffected, but the reserve and the scored protected face are affected. Demonstrated in `0.md`.
- **F-2, SOURCE-POLICY RED (rule ≠ compute).**
  - Symptom: `excess_earnings` splits the earnings period into 30-day months.
  - Root cause: the rule says "compounded monthly over the whole months in that period and the remaining days earn simple interest". The 30-day convention lives only in the factor ladder text (line 2225), not in the rule (line 2122).
  - Bears on task 1: the period spans the 31-day Aug–Sep month. Demonstrated in `1.md`.
- **F-3, SOURCE-POLICY RED (authoring viewpoint in `prerequisite`).**
  - Evidence: line 1574, `condition: … equals the charge date (the frozen date) …`.
  - Bears on task 0.
- **F-4, SOURCE-FACTOR RED (unreal ladder: a vacuous condition part).**
  - The mid tier of `overloan_charge_rate_band` requires "the insured's attained age is at least the rider's minimum attained age".
  - Base `ul_overloan_protection` already requires *"the insured's attained age is at least overloan_min_attained_age"* for any exercise, so that conjunct divides no customer who reaches this write.
  - Bears on task 0. The computation's count survives at 4.
- **F-5, SOURCE-FACTOR RED (unreal ladder: vacuous condition and an unreachable fall-through/baseline).**
  - The tier 2 condition of `protected_loan_margin` is "at or above the tier's overloan loan-to-value threshold", and its fall-through is "below the threshold no margin applies".
  - Base eligibility requires indebtedness ≥ overloan_loan_to_av_threshold of the account value. The charge's prerequisite forces the accrued interest to be settled first, so at this write indebtedness equals the ledger loan.
  - So every customer who reaches this write is at or above the threshold. The baseline value 1 is a treatment no eligible customer ever receives.
  - Bears on task 0, where it drives the computation's factor count below 4.
- **F-6, SOURCE-FACTOR RED (unreal tier outcome).**
  - The tiers of `protected_care_margin` raise the guaranteed paid-up face by 1–2% because the insured is on an active CareAssure claim, that is, chronically ill.
  - Raising guaranteed death benefit at no charge for a documented impaired life is anti-selective. No life insurer publishes such an enhancement.
  - The conditions themselves (an active LTC claim and recent benefit payments) are real things insurers weigh, for waivers. It is the outcome that is unreal.
  - Bears on task 0.
- **F-7, SOURCE-FACTOR RED (dishonest factor baseline).**
  - `earnings_compounding.baseline.excess_earnings = guideline_excess * (earnings_rate + late_addition) * earnings_days / 365`. That is ladder tier 2 (simple interest).
  - The fall-through tier is "no earnings". `baseline.rule` says "with no earnings added".
  - Bears on task 1, where it is demonstrated.
- **Observations (no RED):**
  - O-1: overwrite[0].replaced_by of the settlement omits the advance-rate sentence.
  - O-2: the payout's surrender cost basis takes off "the premiums refunded", meaning the refund entry amount, which includes earnings. This matches the base measure's "amount of ul_premium_refunded rows".
  - O-3: the payout's interim loan rate is undeclared on its own side but agrees with the declared settlement override.
  - O-4: "When … carried out/processed" occasion wording on the depended-on side.
  - O-5: the state_gate's `gate` is a holding field, not an eligibility id.
  - O-6: the overloan charge docstring mentions "when the rider is carried out".
  - O-7: the household share is a cross-product discount on a contractual rider charge. Unusual, but not demonstrably unpublishable.
  - O-8: two method labels are borderline: `protected_deduction_reserve` (a count × deduction) and `earnings_start_date` (offset substitution). Neither changes a policy's parameter/method minimums.
  - O-9: `conversion_credit` and `premiums_counted` read the customer's first converted term policy via CFIELD/EXISTS, not the one recorded in `converted_from_term_policy_id`. This is harmless where the customer has one term policy.

## closing_checklist

Written 2026-10-08T07:45Z, after both reveals. This is the only post-reveal section of this file; the charter-global section above is unchanged since its freeze hash 125f1654…05dc.

**The difficulty is NOT closed.** Neither task passes all four relationships.

| item | status |
| --- | --- |
| Audit files | `0.md`, `1.md` and this file correspond one-to-one with the tasks. First revision; no older revision exists. Each comparison section carries a verdict, and neither carries PASS on every relationship. |
| Coverage, scopes, tools | All six extended policies are covered. Scopes are pairwise disjoint: `charter_scope` of task 0 = {settlement, charge, face}; task 1 = {guideline refund, surrender charge, payout}. Each task tool has an independently generated, frozen uuid8. |
| Problem trees | Each tree has 2 prerequisite problems, at least 1 value_input edge (task 0: 1; task 1: 2) and an owner=user root. The difficulty-wide graph is acyclic. |
| Factors | **Not met.** Task 0: settlement and protected-face computations fall below 4 surviving factors (stamp; F-5/F-6), and no multi-source factor survives (stamp, F-4, F-6). Task 1: F-7 dishonest baseline. |
| Rule/compute equivalence | **Not met.** F-1 changes task 0's scored face. F-2 changes task 1's refund and net payout. |
| Gates | The instantiation-stage gate snapshot is the brief's (all OK; traceability deferred). Per Step 0 the auditor does not re-run them. The difficulty is not at a final form that could be closed. |

Per-task verdicts:

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED | PASS | SOURCE-FACTOR RED | SOURCE-TASK RED |
| 1 | SOURCE-POLICY RED | PASS | SOURCE-FACTOR RED | SOURCE-TASK RED |

## revision_2

### revision_2 / charter_global_frozen

Written 2026-10-08, before any round-2 task file was opened. The round-1 text above is left untouched.

**Inputs re-checked**

- `ul.extended.yaml` is now 9f3551fcc6cb6cbdeaea00258ccb888cffd5677b2b4eb8e38a1eb34c6af8b2ce. It changed from round 1's 326133b0…91fa, so every charter-global section is re-derived in full below.
- `task_tools.py` is bfc05761…709a, unchanged. The tool-module half of § action_binding_and_uuids is carried forward on that hash: same six tools, same uuid8s, bodies still free of checks.
- Masked views: task_0 482fa0b9…a52b, task_1 846c0b50…795f. Both match the brief.
- Base copy: lines 1–1386 are still byte-identical to `blueprint/products/ul.yaml`.
- Gate snapshot (from the brief): all OK, with traceability deferred.

**contamination_disclosure.** This auditor saw the round-1 GT during the round-1 reveal: the figures 2,466.39, 5,791.21, 221,373.34, 516.38, 13,438.43 and 71,708.53. That exposure is inherent to a re-audit. The round-2 derivation below is a fresh recomputation from the round-2 charter, seeds and tools; the protected face changed value under round 2, which shows it was not copied. No round-2 task JSON was opened before this freeze.

**What changed, per policy (round 1 → round 2)**

- **settlement**
  - The discount-count sentence, overwrite[1].replaced_by and the discount ladder text now read "the number of monthly anniversaries still to fall due after the settlement date up to and including the next policy anniversary".
  - The compute is unchanged.
- **overloan charge**
  - New param `mid_duration_attained_age: 78`. The mid tier's age condition now reads "the mid-duration attained age" in the rule, compute and ladder.
  - `prerequisite.condition` now reads "equals the date the charge is figured".
- **protected face**
  - The care margin and its ltc cross read are removed.
  - New method factor `protected_value_carry`: the account value brought forward from the latest monthly anniversary by the same two-tier carry the charge uses (param face_full_carry_days 15).
  - Reserve tier 2 now counts "each monthly anniversary still to fall due after the exercise date up to and including the next policy anniversary".
  - The loan margin's tier-2 lower bound is now a separate `standard_loan_margin_ratio` 0.96 (not the 0.94 overloan threshold), measured against "the account value shown".
  - The overwrite replaced_by is updated to match.
- **guideline refund**
  - The rule now says "whole thirty-day months".
  - The `earnings_compounding` baseline is now "0".
- **payout**
  - `base_policy_refs` adds `ul_evt_policy_loan`.
  - A new overwrite entry declares that the loan-rate sentence is replaced by the payout's loan-interest sentence.
- **surrender charge:** unchanged.
- The surrender-charge rate tables still match all six tier ladders (script check).

### revision_2 / policy_conflict_scan

- The same six policies, targets, owners and edges as round 1.
- No new overlapping subject.
- Scopes, inferred pre-reveal from the graph, are unchanged: {settlement → charge → face} and {surrender charge, guideline refund → payout}. Disjoint and jointly complete.
- The payout and the settlement now both declare replacements of the same base loan-rate sentence. Each replacement scopes itself to its own quantity:
  - the settlement: "the rate charged on the balance carried from the paid-to date … in which the interest is settled";
  - the payout: "loan interest accrued to the effective date … of the surrender".

  The common interim figure is 0.045 from year 6. They differ only where the settlement prices a recent advance larger than the gain at the blended rate, or splits accrual by advance date, while the payout uses the whole balance at the year's rate. These are distinct occasions (cash settlement before the due date, versus surrender), so there is no single situation in which both claim the same quantity. Observation O-10. It was present in round 1 and has not regressed.

### revision_2 / rule_compute_equivalence

- **Script checks:** all `compute_basis` quotations are verbatim in their rules, and all overwrite `replaced_by` texts are verbatim in their own rules. All `baseline.rule` sentences are in the rules. Every factor's `decides` and `baseline` keys are compute bindings.
- **Settlement `months_to_anniversary`** (`12 - MONTHS(issue, NOW) % 12`) against the new rule ("monthly anniversaries still to fall due after the settlement date up to and including the next policy anniversary"):
  - Off a monthly anniversary day the two are equal. Example: at 2026-10-08 with issue day 14, the rule counts Oct 14 … May 14 = 8 and the compute gives 8.
  - On a monthly anniversary day they are also equal: the rule excludes that day, and MONTHS has already counted it.
  - **F-1 is closed** for every issue day of 28 or below.
- **Protected-face reserve tier 2:** the same idiom and the same wording. **F-1 is closed** here too.
- **Observation O-11 (latent; no task affected).** On issue days 29–31, where base `ul_monthly_deduction_and_crediting` puts the monthly anniversary on "the last day of a shorter month", `MONTHS` compares day-of-month. On such a short-month anniversary it counts one month fewer than elapsed, so the compute returns the rule's count + 1.
  - Constructed example: issue 2020-08-31, settlement 2026-06-30 (a monthly anniversary). The rule counts Jul 31 and Aug 31 = 2, so no discount. The compute gives 12 − 9 = 3, so the 1% partial discount.
  - Neither task's world has such a date (both issue days are 9 or 14), so no consequence can be demonstrated on a task. Recorded as an observation. It would be a SOURCE-POLICY RED for any task seeded on those dates.
- **Refund `excess_earnings`:** the 30-day split now matches the rule's "whole thirty-day months". **F-2 is closed.**
- **New face bindings** (`face_latest_monthiversary`, `face_carry_days`, `face_collateral_rate`, `carried_value`): each matches its rule sentence.
- **Loan margin:** `opr_ledger_loan / F('account_value') >= 0.98 / >= 0.96`, and the rule now says "of the account value shown". The round-1 "account value after the booked charge" candidate reading is gone.
- **Charge rate band:** the compute uses `K('mid_duration_attained_age')`, matching the rule.
- Everything else is unchanged from round 1 and still equivalent.

### revision_2 / action_binding_and_uuids

Carried forward on the unchanged `task_tools.py` hash, as stated above. Each `(target_tool, computes)` pair is still claimed once.

### revision_2 / prerequisite_graph and prerequisite_sentences

- The same four edges, all state form, with sources verbatim (script check) and value_input gates that are compute bindings. Acyclic.
- **F-3 is closed:** the condition now reads "ul_holdings.loan_interest_paid_to_date equals the date the charge is figured …". No authoring-viewpoint wording remains in any `prerequisite` field.
- The four-point test results and single-write resolution are unchanged from round 1. The face → charge sentence is unchanged. The new face `effect` text ("lowering the value the protected face is figured on") is consistent with the compute.
- O-4 and O-6 are unchanged.

### revision_2 / override_declarations

- **Settlement:** both overwrites are still named, and replaced_by[1] is updated verbatim. O-1 is unchanged.
- **Overloan charge:** unchanged. Base eligibility is still inherited.
- **Protected face:** the face sentence is still declared, with replaced_by now naming the carried value and no care margin.
- **Surrender charge:** unchanged.
- **Guideline refund:** unchanged declaration.
- **Payout:**
  - CSV and taxable sentences declared, as in round 1.
  - New: the `ul_evt_policy_loan` rate sentence is declared replaced, and it is now in `base_policy_refs`. **O-3 is closed.**
  - Residual observation O-12: the superseded base sentence also defined loan *type* (standard/preferred) and its collateral credited rates. Neither the settlement nor the payout replacement restates the loan type. The charge, face and payout still credit collateral "at the credited rate of the policy's loan type", which their computes take as preferred from preferred_loan_first_policy_year. Every tier sets standard_loan_credited_rate = preferred_loan_credited_rate = 0.03, so no reading changes any number. This situation existed in round 1 and is not a regression.
- **Result:** no undeclared override that changes a scored quantity.

### revision_2 / factor_ladders

Changes against round 1's table; every other row is unchanged and still structurally sound.

| policy | factor | label | ladder | multi-source? | cross | round-2 status |
| --- | --- | --- | --- | --- | --- | --- |
| overloan charge | overloan_charge_rate_band | parameter | py≥25 ∧ age≥85 → 0.025; py≥20 ∧ age≥78 ∧ ¬long → 0.03; else tier pct | yes | — | **F-4 closed.** 78 > the 75 eligibility floor, so the age conjunct now divides eligible customers (75–77 fall through). |
| protected face | protected_value_carry | method (new) | ≥15 days fixed + collateral carry / 1–14 days fixed only / as shown | no | — | sound. The fall-through equals the baseline, and both equal `baseline.rule`'s "account value shown". |
| protected face | protected_deduction_reserve | method | age≥85 → 6×; age<85 ∧ py<25 → per remaining monthly anniversary; else 0 | no | — | the count wording is fixed (F-1 closed). Label still borderline (O-8). |
| protected face | protected_loan_margin | parameter | ≥0.98 → 1.02; ≥0.96 → 1.01; else 1 | no | — | **F-5 closed.** Eligible customers at 0.94–0.96 reach the fall-through, so the lower bound divides and the baseline 1 is a real treatment. |
| protected face | protected_care_margin | — | removed | — | — | **F-6 closed** by removal. |
| guideline refund | earnings_compounding | method | unchanged ladder | no | — | **F-7 closed.** Baseline "0" equals the fall-through ("no earnings") and `baseline.rule`. |

Counts as declared:

| policy | factors | parameter | method |
| --- | --- | --- | --- |
| settlement | 4 | 3 | 1 |
| charge | 5 | 4 | 1 |
| face | 4 | 2 | 2 |
| surrender charge | 5 | 4 | 1 |
| refund | 5 | 2 | 3 |
| payout | 6 | 3 | 3 |

- Every policy meets 4–6 factors with at least 2 parameter and at least 1 method.
- Cross-difficulty factors: fixed (charge), term and ltc (surrender charge), term (payout). The face now has none.

### revision_2 / findings (charter-global)

| round-1 finding | round-2 status |
| --- | --- |
| F-1 | closed |
| F-2 | closed |
| F-3 | closed |
| F-4 | closed |
| F-5 | closed |
| F-6 | closed (removed) |
| F-7 | closed |
| O-3 | closed |

- **No new charter-global RED.**
- New observations:
  - O-10: settlement and payout price loan interest differently on distinct occasions.
  - O-11: latent off-by-one on issue days 29–31; affects no task world.
  - O-12: loan type is no longer restated after the override; no numeric effect.
- Unchanged observations: O-1, O-2, O-4, O-5, O-6, O-7, O-8, O-9.

### revision_2 / closing_checklist

Written after both round-2 reveals. The round-1 closing_checklist above is left as it was.

| item | status |
| --- | --- |
| Audit files | `0.md`, `1.md` and this file match the two tasks one-to-one. Revision 1 is kept intact; revision 2 is appended. Both round-2 comparison sections carry PASS on all four relationships. |
| Coverage | All six extended policies are covered. charter_scope task 0 = {settlement, charge, face} and task 1 = {refund, surrender charge, payout}, pairwise disjoint and jointly complete. Tools and GT are closed. The uuid8s are independent and frozen (tool module unchanged). |
| Problem trees | Each tree has 2 prerequisite problems, at least 1 value_input edge (task 0: 1; task 1: 2) and an owner=user root. The difficulty-wide graph is acyclic. |
| Factors | Every computation has a baseline that stands on its own and 4–6 factors with at least 2 parameter and at least 1 method. Per task, at least 1 multi-source factor and at least 1 cross-difficulty factor survive (task 0: advance rate and rate band / fixed; task 1: care waiver and conversion credit / term, ltc). Every ladder has 3 tiers stated in its rule, with distinct outcomes. Every factor bears weight against an honest baseline, and each baseline alone differs from gold. |
| Rule/compute equivalence | Holds on both task worlds. O-11 is latent (issue days 29–31) and affects neither task. |
| Gates | Brief snapshot after rework: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; CACHE-DIFF INFO; traceability deferred to the render stage. The auditor did not re-run them (Step 0). |

**The difficulty passes the source-layer audit in revision 2.**

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Carried observations, none of them a RED: O-1, O-2, O-4–O-12, and the residual LTC seed fields in task 1.
